"""Synthetic behavior, historical replay and browser request safety are separate."""
import copy
import gzip
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from collector import dynamic_ats
from collector.applications import ApplicationClosed
from collector.runtime import BudgetClient,CollectionBudgetExceeded
from collector.verification import verify_vacancy
from collector.pipeline import finalize
from scripts.dynamic_ats_pilot import replay,replay_live

ROOT=Path(__file__).resolve().parents[1]
MARKER=b'''<div id="application-form-hident3"></div><div class="btn" onclick="toggleForm('hident2')">Solliciteer direct</div>'''
FORM=b'<form id="application"><input name="name"><input type="email"><input type="file" name="resume"><button>Apply</button></form>'


class DynamicTests(unittest.TestCase):
    def setUp(self):
        self.env=patch.dict(os.environ,PEOPLE_PLACEMENT_DYNAMIC_ATS='pilot-v1');self.env.start();self.addCleanup(self.env.stop)
        self.budget=patch.object(dynamic_ats,'_RENDERINGS',0);self.budget.start();self.addCleanup(self.budget.stop)
        self.url='https://www.werkenbijbentacera.nl/vacatures/stage-hr-123'
        self.record=dict(url=self.url,title='Stage HR',external_id=self.url,posting_identifier='123')
        self.source=dict(id='auto-bentacera',allowed_hosts=['www.werkenbijbentacera.nl'])
        self.stamp='2026-11-08T12:00:00+00:00';self.observation={}
        self.html=self.page(MARKER)
        self.client=BudgetClient(seconds=90,max_requests=100,delay=0)
        self.client.request=lambda url:(self.html,200,url)

    def page(self,body,title='Stage HR',identifier='123',deadline=None):
        return ('<h1>'+title+'</h1><script type="application/ld+json">'+json.dumps(dict(
            **{'@type':'JobPosting'},title=title,identifier=identifier,validThrough=deadline))+'</script>').encode()+body

    def verify(self,body=None,error=None,final=None):
        render=patch('collector.rendering.render_pages',side_effect=error,return_value=([(final or self.url,self.page(FORM) if body is None else body)],True))
        with render as mocked:
            try:return verify_vacancy(self.record,self.source,self.client,self.stamp,self.observation)
            finally:self.render_calls=mocked.call_count

    def test_valid_specific_dynamic_form_and_no_mutation(self):
        original=copy.deepcopy(self.record)
        proof=self.verify()
        self.assertEqual(proof['method'],'rendered-same-vacancy-applicant-form')
        self.assertEqual(self.record,original)
        self.assertEqual(self.observation['dynamic_ats']['outcome'],'verified')
        self.assertEqual(self.render_calls,1)

    def test_missing_disabled_newsletter_cookie_forms_never_verify(self):
        for form in (b'',FORM.replace(b'<button>',b'<button disabled>'),
                     FORM.replace(b'<form id="application">',b'<form id="application"><fieldset disabled>').replace(b'</form>',b'</fieldset></form>'),
                     FORM.replace(b'<form ',b'<form hidden '),
                     FORM.replace(b'<form ',b'<form aria-disabled="true" '),
                     b'<form id="newsletter"><input name="name"><input type="email"><button>Subscribe</button></form>',
                     b'<form id="cookie"><input name="consent"><button>OK</button></form>'):
            with self.subTest(form=form),patch.object(self.client,'dynamic_ats_attempted',False,create=True),patch.object(dynamic_ats,'_RENDERINGS',0):
                with self.assertRaises(ValueError):self.verify(self.page(form))
                self.assertEqual(self.observation['dynamic_ats']['outcome'],'unverified')

    def test_rendered_title_id_redirect_and_deadline_rejected(self):
        invalid=[self.page(FORM,title='Software Intern'),self.page(FORM,identifier='999'),
                 self.page(FORM,deadline='2020-01-01'),self.page(FORM.replace(b'<form ',b'<form action="https://evil.org/apply" ')),self.page(FORM.replace(b'<input name="name">',b'<input name="name"><input name="jobId" value="999">'))]
        for body in invalid:
            with self.subTest(body=body),patch.object(self.client,'dynamic_ats_attempted',False,create=True),patch.object(dynamic_ats,'_RENDERINGS',0):
                with self.assertRaises(ValueError):self.verify(body)
        with patch.object(self.client,'dynamic_ats_attempted',False,create=True),patch.object(dynamic_ats,'_RENDERINGS',0):
            with self.assertRaisesRegex(ValueError,'redirected'):self.verify(final='https://evil.org/jobs')

    def test_preconditions_never_launch_browser(self):
        for html in (self.page(MARKER,title='Other job'),self.page(MARKER,identifier='999'),
                     self.page(MARKER,deadline='2020-01-01'),self.page(MARKER+b'Verify you are human'),
                     self.page(b'<a href="https://evil.org/123">Apply</a>')):
            self.html=html
            with self.subTest(html=html),self.assertRaises(ValueError):self.verify()
            self.assertEqual(self.render_calls,0)

    def test_disabled_nonpilot_missing_marker_and_captcha_excluded(self):
        cases=[('pilot-disabled',{'PEOPLE_PLACEMENT_DYNAMIC_ATS':''},self.source,self.html),
               ('source-not-pilot',{},dict(self.source,id='other'),self.html),
               ('no-reviewed-javascript-marker',{},self.source,self.page(b'')),
               ('captcha',{},self.source,self.html+b'<div class="g-recaptcha"></div>'),
               ('html-applicant-form-unavailable',{},self.source,self.html+FORM.replace(b'<button>',b'<button disabled>'))]
        for reason,env,source,body in cases:
            with self.subTest(reason=reason),patch.dict(os.environ,env),patch.object(self,'source',source),patch.object(self,'html',body):
                with self.assertRaises(ValueError):self.verify()
                self.assertEqual(self.render_calls,0)
                self.assertEqual(self.observation['dynamic_ats']['reason'],reason)

    def test_timeout_robots_and_budget_are_unverified(self):
        for error in (TimeoutError('timeout'),ValueError('robots.txt disallows browser navigation'),CollectionBudgetExceeded('budget')):
            with self.subTest(error=error),patch.object(self.client,'dynamic_ats_attempted',False,create=True),patch.object(dynamic_ats,'_RENDERINGS',0):
                with self.assertRaises(type(error)):self.verify(error=error)
                self.assertEqual(self.observation['dynamic_ats']['outcome'],'unverified')
        with patch.object(dynamic_ats,'_RENDERINGS',3):
            with self.assertRaises(ValueError):self.verify()
            self.assertEqual(self.render_calls,0)
            self.assertEqual(self.observation['dynamic_ats']['reason'],'process-render-budget-exhausted')
        self.client.max_requests=0
        with self.assertRaises(ValueError):self.verify()
        self.assertEqual(self.render_calls,0)

    def test_unapproved_cta_cannot_be_bypassed_using_inline_marker(self):
        self.html=self.page(MARKER+b'<a href="https://evil.org/apply/123">Apply</a>')
        with self.assertRaises(ValueError):self.verify()
        self.assertEqual(self.render_calls,0)
        self.assertEqual(self.observation['dynamic_ats']['reason'],'unapproved-application-host')

    def test_collected_expired_deadline_never_launches(self):
        self.record['valid_through']='2020-01-01'
        with self.assertRaisesRegex(ValueError,'deadline'):self.verify()
        self.assertEqual(self.render_calls,0)

    def test_ordinary_html_avoids_browser(self):
        self.html=self.page(FORM)
        self.verify()
        self.assertEqual(self.render_calls,0)
        self.assertEqual(self.observation['dynamic_ats']['reason'],'ordinary-html-sufficient')

    def test_linked_application_reapplies_policy(self):
        child=self.url+'/solliciteer'
        vacancy=self.page(('<a href="'+child+'">Solliciteer</a>').encode())
        self.client.request=lambda url:(vacancy if url==self.url else self.html,200,url)
        proof=self.verify(final=child)
        self.assertEqual(proof['method'],'rendered-linked-same-vacancy-applicant-form')
        self.assertEqual(proof['url'],child)

    def test_render_budget_shares_counts_and_bounds_robots(self):
        bounded=dynamic_ats.RenderBudget(self.client)
        bounded.requests+=2
        self.assertEqual(self.client.requests,2)
        self.client.requests=bounded.start+dynamic_ats.MAX_REQUESTS
        with self.assertRaises(CollectionBudgetExceeded):bounded.check()


class ReplayTests(unittest.TestCase):
    def test_nonpilot_reports_remain_deterministic_with_variable_timings(self):
        import itertools
        from types import SimpleNamespace
        from scripts.replay_sprint18 import run
        ticks=itertools.count()
        # Deliberately different durations on every call. Production metrics
        # for this experiment must not perturb unrelated source reports.
        with patch.object(dynamic_ats,'time',SimpleNamespace(monotonic=lambda:next(ticks)**2)):
            report=run()
        self.assertTrue(report['inventory_replay']['two_collections_idempotent'])

    def test_fresh_capture_replays_with_stricter_final_checks(self):
        report=replay_live()
        self.assertEqual(sum(row['after']['state']=='verified' for row in report['rows']),2)
        self.assertEqual(report['live_requests'],0)

    def test_same_pr21_evidence_no_live_verification_claim(self):
        with patch.dict(os.environ,PEOPLE_PLACEMENT_DYNAMIC_ATS=''):
            report=replay()
        self.assertEqual(report['live_requests'],0)
        self.assertEqual(len(report['rows']),3)
        self.assertTrue(all(row['before']['state']==row['after']['state']=='unverified' for row in report['rows']))

    def test_324_historical_ids_and_two_idempotent_finalizations(self):
        prior=json.loads(gzip.decompress((ROOT/'tests/fixtures/dynamic-ats-baseline/catalog.json.gz').read_bytes()))
        registry=json.loads((ROOT/'data/sources.json').read_text())
        source=next(s for s in registry if s['id']=='auto-bentacera')
        job=copy.deepcopy(next(j for j in prior['jobs'] if j['source_id']==source['id']))
        # Synthetic success on one existing ID; no change to the real catalog.
        job.update(status='open',link_status='verified',last_verified_at='2026-11-08T12:00:00+00:00',
                   verification=dict(state='verified',policy_version=2,checked_at='2026-11-08T12:00:00+00:00',reason='synthetic dynamic'))
        part=dict(jobs=[job],report=dict(id=source['id'],status='partial',complete=False,closure_complete=False),closure_eligible=[])
        with tempfile.TemporaryDirectory() as folder:
            baseline_part=copy.deepcopy(part);baseline_part['jobs']=[copy.deepcopy(next(j for j in prior['jobs'] if j['id']==job['id']))]
            baseline,_=finalize(registry,[source],copy.deepcopy(prior),{'sources':[]},[baseline_part],'2026-11-08T12:00:00+00:00',Path(folder)/'baseline')
            a,_=finalize(registry,[source],copy.deepcopy(prior),{'sources':[]},[part],'2026-11-08T12:00:00+00:00',Path(folder)/'a')
            b,_=finalize(registry,[source],copy.deepcopy(a),{'sources':[]},[part],'2026-11-08T12:00:00+00:00',Path(folder)/'b')
        self.assertEqual(a['jobs'],b['jobs'])
        old={j['id']:j for j in prior['jobs']}
        comparison={j['id']:j for j in baseline['jobs']}
        self.assertEqual(len(old),324)
        self.assertEqual(set(old),{j['id'] for j in b['jobs']})
        for row in b['jobs']:
            for key in ('source_id','first_discovered_at','identity_aliases','ownership_review'):
                self.assertEqual(row.get(key),old[row['id']].get(key))
            if old[row['id']]['status']=='closed':self.assertEqual(row['status'],'closed')
            if old[row['id']]['status']=='open':self.assertEqual(row['status'],'open')
            if row['id']!=job['id']:self.assertEqual(row,comparison[row['id']])


class BrowserSafetyTests(unittest.TestCase):
    """Exercise the real renderer's routing/click code with a fake transport."""
    def render(self,requests,disallow=None,toggle=False,handler="toggleForm('hident2')",response_status=200,headers=None):
        import sys
        from types import SimpleNamespace
        from unittest.mock import Mock,MagicMock
        from collector.rendering import render_pages
        url='https://approved.org/vacatures/123'
        client=BudgetClient(seconds=90,max_requests=100,delay=0)
        client.permitted=Mock(side_effect=lambda target:target!=disallow)
        page=MagicMock();page.url=url;page.content.return_value='<h1>Stage HR</h1>'
        locator=MagicMock();locator.inner_text.return_value='Stage HR';page.locator.return_value=locator
        control=MagicMock();control.inner_text.return_value='Solliciteer direct'
        control.get_attribute.return_value=handler
        control.is_visible.return_value=True;control.locator.return_value.count.return_value=0
        locator.count.return_value=1 if toggle else 0;locator.nth.return_value=control
        context=MagicMock();context.new_page.return_value=page
        browser=MagicMock();browser.new_context.return_value=context
        pw=MagicMock();pw.chromium.launch.return_value=browser
        manager=MagicMock();manager.__enter__.return_value=pw
        routes=[]
        def goto(*args,**kwargs):
            route_handler=context.route.call_args.args[1]
            for method,kind,target,nav in requests:
                req=SimpleNamespace(method=method,resource_type=kind,url=target,is_navigation_request=lambda nav=nav:nav,headers=headers or {})
                route=Mock(request=req)
                route.fetch.return_value=Mock(status=response_status,body=lambda:b'public resource')
                route_handler(route);routes.append(route)
            return SimpleNamespace(status=200)
        page.goto.side_effect=goto
        metrics={}
        modules={'playwright':SimpleNamespace(),'playwright.sync_api':SimpleNamespace(sync_playwright=lambda:manager)}
        with patch.dict(sys.modules,modules):
            try:
                result=render_pages(url,client,lambda target:target.startswith('https://approved.org/'),
                                    application_read=True,application_toggle=toggle,metrics=metrics)
                return result,client,routes,context,page,control,metrics
            except Exception:
                self.routes=routes;self.metrics=metrics;self.control=control;raise

    def test_approved_scripts_and_css_are_robots_checked_and_counted(self):
        requests=[('GET','document','https://approved.org/vacatures/123',True),
                  ('GET','script','https://approved.org/app.js',False),
                  ('GET','stylesheet','https://approved.org/site.css',False)]
        _,client,routes,context,page,control,metrics=self.render(requests,toggle=True)
        self.assertEqual(client.requests,3)
        self.assertEqual(metrics['browser_requests'],3)
        self.assertTrue(all(route.fulfill.called for route in routes))
        self.assertTrue(all(any(call.args[0]==target for call in client.permitted.call_args_list) for _,_,target,_ in requests))
        for route in routes:self.assertEqual(route.fetch.call_args.kwargs['max_redirects'],0)
        control.click.assert_called_once();page.get_by_role.assert_not_called()
        context.route_web_socket.assert_called_once();context.close.assert_called_once()

    def test_post_including_search_and_application_never_sent(self):
        for path in ('/jobs/search','/application/submit'):
            with self.subTest(path=path),self.assertRaisesRegex(ValueError,'non-read-method'):
                self.render([('POST','xhr','https://approved.org'+path,False)])
            self.routes[0].abort.assert_called_once();self.routes[0].continue_.assert_not_called()

    def test_redirect_unapproved_script_robots_and_budget_abort(self):
        cases=[('GET','document','https://approved.org/login',True),
               ('GET','script','https://unapproved.org/app.js',False),
               ('GET','script','https://approved.org/forbidden.js',False)]
        for req in cases:
            with self.subTest(req=req),self.assertRaises(ValueError):
                self.render([req],disallow='https://approved.org/forbidden.js')
            self.routes[0].continue_.assert_not_called()
        with self.assertRaisesRegex(ValueError,'budget'):
            self.render([('GET','script','https://approved.org/app.js',False)]*101)
        self.assertEqual(sum(route.fulfill.called for route in self.routes),99)

    def test_tracker_blocked_without_robots_or_host_approval(self):
        _,client,routes,_,_,_,_=self.render([('GET','script','https://analytics.floydhamilton.tech/matomo.js',False)])
        self.assertEqual(client.requests,0)
        routes[0].abort.assert_called_once()
        self.assertEqual(client.permitted.call_count,1) # initial navigation only

    def test_arbitrary_inline_handler_not_clicked(self):
        _,_,_,_,_,control,_=self.render([],toggle=True,handler="toggleForm('hident2');document.forms[0].submit()")
        control.click.assert_not_called()

    def test_http_redirects_and_access_blocks_never_followed(self):
        for status in (301,302,307,308,401,403,429,451):
            with self.subTest(status=status),self.assertRaisesRegex(ValueError,'HTTP '+str(status)):
                self.render([('GET','script','https://approved.org/script',False)],response_status=status)
            route=self.routes[0]
            self.assertEqual(route.fetch.call_args.kwargs['max_redirects'],0)
            route.fulfill.assert_not_called();route.continue_.assert_not_called()
            route.fetch.return_value.dispose.assert_called_once()

    def test_authentication_headers_not_transmitted(self):
        with self.assertRaisesRegex(ValueError,'authentication-excluded'):
            self.render([('GET','xhr','https://approved.org/read',False)],headers={'authorization':'synthetic'})
        self.routes[0].fetch.assert_not_called()
