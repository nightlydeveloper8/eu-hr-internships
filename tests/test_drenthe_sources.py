import unittest
from unittest.mock import patch
from collector.applications import verify_application, ApplicationClosed
from collector.verification import verify_vacancy
from collector.employer_pages import page_record,index_records
from collector.classify import extract_metadata

class Client:
    def __init__(self,pages):self.pages=pages;self.calls=[]
    def request(self,url,**kwargs):self.calls.append(url);return self.pages[url].encode(),200,url
    def check(self):pass
    def remaining(self):return 100

class DrentheSourceTests(unittest.TestCase):
    def test_email_requires_reviewed_address_and_current_application_instruction(self):
        url='https://example.org/jobs/hr';source=dict(application_check='official-email',application_email='hr@example.org',allowed_hosts=['example.org'])
        page='<main><h1>HR stage</h1><p>Stuur je motivatie en CV naar <a href="mailto:hr@example.org">hr@example.org</a></p></main>'
        record=dict(url=url,title='HR stage');c=Client({url:page})
        proof=verify_vacancy(record,source,c,'2026-11-06T12:00:00+00:00')
        self.assertEqual(proof['method'],'official-vacancy-email-instructions');self.assertFalse(proof['delivery_verified'])
        for invalid in [page.replace('Stuur je motivatie en CV naar','Contact:'),page.replace('mailto:hr@','mailto:service@'),page.replace('<h1>HR stage','<h1>Other stage')]:
            with self.assertRaises(ValueError):verify_vacancy(record,source,Client({url:invalid}),'2026-11-06T12:00:00+00:00')
        with self.assertRaises(ApplicationClosed):verify_vacancy(record,source,Client({url:page.replace('</main>','This job is closed</main>')}),'2026-11-06T12:00:00+00:00')

    def test_formie_requisition_title_fields_and_enabled_submit_must_agree(self):
        url='https://example.org/jobs/hr';app='https://example.org/solliciteren?vacature=4260'
        source=dict(application_check='formie-linked',allowed_hosts=['example.org'])
        record=dict(url=url,title='HR stage',posting_identifier='4260')
        page='<h1>HR stage</h1><a href="/solliciteren?vacature=4260">Solliciteren</a>'
        form='<main>Solliciteren voor: HR stage<form data-form-handle="applicationFormOne"><input name="fields[vacancyId]" value="4260"><input name="fields[firstName]"><input name="fields[email]"><button type="submit">Apply</button></form></main>'
        self.assertEqual(verify_application(record,source,Client({url:page,app:form}))['url'],app)
        for invalid in [form.replace('value="4260"','value="99"'),form.replace('voor: HR stage','voor: Other stage'),form.replace('type="submit"','type="submit" disabled')]:
            with self.assertRaises(ValueError):verify_application(record,source,Client({url:page,app:invalid}))

    def test_reviewed_visible_workplace_comes_from_current_text(self):
        url='https://example.org/jobs/hr';source=dict(allowed_hosts=['example.org'],page_format='reviewed-visible',reviewed_workplaces=[dict(pattern=r'Locatie: Assen\b',city='Assen',country='NL')])
        page='<main><h1>HR stage</h1>Locatie: Assen '+('Relevant HR internship text. '*15)+'</main>'
        result=page_record(dict(url=url),source,Client({url:page}));self.assertEqual(result['city'],'Assen')
        with self.assertRaises(ValueError):page_record(dict(url=url),source,Client({url:page.replace('Locatie: Assen','Locatie: Amsterdam')}))

    def test_rendered_inventory_requires_matching_live_count(self):
        url='https://example.org/jobs';source=dict(id='one',employer='One',allowed_hosts=['example.org'],index_urls=[url],index_rendered=True,job_url_pattern=r'/job/',index_job_count_pattern=r'(\d+) results')
        body=b'1 results <a href="/job/1">HR stage</a>'
        with patch('collector.rendering.render_pages',return_value=([(url,body)],True)):
            self.assertEqual(len(index_records(source,Client({}))),1)
        with patch('collector.rendering.render_pages',return_value=([(url,body.replace(b'1 results',b'2 results'))],True)):
            with self.assertRaisesRegex(ValueError,'inventory count'):index_records(source,Client({}))
        with patch('collector.rendering.render_pages',return_value=([(url,body)],False)):
            with self.assertRaisesRegex(ValueError,'incomplete'):index_records(source,Client({}))

    def test_dutch_education_requirement_is_preserved(self):
        self.assertEqual(extract_metadata('Je volgt een HBO-opleiding Human Resource Management en zit in het tweede jaar.')['enrollment'],'Je volgt een HBO-opleiding Human Resource Management en zit in het tweede jaar.')
        self.assertIsNone(extract_metadata('We offer training and workshops.')['enrollment'])

    def test_captcha_meta_refresh_is_blocked_before_browser_navigation(self):
        from collector.universal import Crawler
        url='https://example.org/jobs'
        source=dict(id='captcha-test',employer='Example',allowed_hosts=['example.org'])
        body='<html><head><meta http-equiv="refresh" content="0;/.well-known/sgcaptcha/?r=jobs"></head></html>'
        with patch('collector.rendering.render_pages') as render:
            with self.assertRaisesRegex(ValueError,'Access challenge'):
                Crawler(source,Client({url:body})).visit(url)
        render.assert_not_called()

    def test_empty_inventory_needs_reviewed_live_message_and_heading(self):
        url='https://example.org/jobs'
        source=dict(id='airport',employer='Airport',allowed_hosts=['example.org'],index_urls=[url],
            job_url_pattern=r'/jobs/\d+',report_index_scope=True,inventory_scope_complete=True,
            reviewed_empty_index=dict(heading='Vacatures',pattern=r'Er zijn geen vacatures gevonden\.'))
        page='<main><h1>Vacatures</h1>Er zijn geen vacatures gevonden.</main>'
        result=index_records(source,Client({url:page}))
        self.assertEqual(len(result),0)
        self.assertTrue(result.stats['complete'])
        self.assertFalse(result.stats['closure_complete'])
        self.assertEqual(result.stats['declared_job_count'],0)
        for invalid in [page.replace('Vacatures','Page unavailable'),page.replace('Er zijn geen vacatures gevonden.','Loading...'),
                        page+'<a href="/jobs/123">HR stage</a>']:
            with self.assertRaises(ValueError):index_records(source,Client({url:invalid}))
        # A generic empty list still fails; the marker is an individually reviewed opt-in.
        with self.assertRaises(ValueError):index_records(dict(source,reviewed_empty_index=None),Client({url:page}))
        with self.assertRaises(ValueError):index_records(dict(source,index_job_count_pattern=r'(\d+) results'),Client({url:page+' 1 results'}))

    def test_cegid_post_allowance_is_only_for_observed_public_inventory(self):
        import json
        from collector.rendering import cegid_inventory_search
        page='https://jobs.workatcenterparcs.com/nl/annonces?customFieldMcqChoice=57781'
        url='https://api.digitalrecruiters.com/public/v1/careers-site/job-ads?domainName=jobs.workatcenterparcs.com&limit=20&page=1&locale=nl_BE'
        data={'filters':{'customFieldMcqChoice':['57781']},'coordinates':{'lat':0,'lng':0}}
        self.assertTrue(cegid_inventory_search(url,json.dumps(data),page))
        for target in [url.replace('job-ads?','map-pins?'),url.replace('job-ads?','applications?'),
                       url.replace('api.digitalrecruiters.com/','evil.example/'),url.replace('limit=20','limit=10000'),
                       url.replace('page=1','page=0'),url+'&page=2',url.replace('domainName=jobs.workatcenterparcs.com','domainName=other.example')]:
            self.assertFalse(cegid_inventory_search(target,json.dumps(data),page))
        for payload in ['invalid','null','[]',json.dumps(dict(data,email='candidate@example.org')),
                        json.dumps(dict(data,filters={'candidate':['57781']})),
                        json.dumps(dict(data,filters={'customFieldMcqChoice':['apply']})),
                        json.dumps(dict(data,filters={'customFieldMcqChoice':['57783']})),
                        json.dumps(dict(data,coordinates={'lat':1000,'lng':0}))]:
            self.assertFalse(cegid_inventory_search(url,payload,page))

    def test_cegid_inventory_counts_scopes_and_rejects_external_or_duplicate_jobs(self):
        from collector.cegid import inventory_records,index_records as cegid_records
        url='https://jobs.workatcenterparcs.com/nl/annonces?customFieldMcqChoice=57781'
        source=dict(id='center',employer='Center Parcs',allowed_hosts=['jobs.workatcenterparcs.com'],
                    index_urls=[url],discovery_scope='Reviewed park query')
        item=dict(job_ad_id=123,title='Stage HR',location='Dalen',contract='Stage',url='123-stage-hr-dalen',
                  career_domain='jobs.workatcenterparcs.com',is_external=False,is_aggregated=False)
        data=dict(count=1,items=[item])
        rows,scope=inventory_records(data,source,url)
        self.assertTrue(scope['complete']);self.assertEqual(rows[0]['city'],'Dalen')
        self.assertEqual(rows[0]['url'],'https://jobs.workatcenterparcs.com/nl/annonce/123-stage-hr-dalen')
        self.assertFalse(inventory_records(dict(data,count=2),source,url)[1]['complete'])
        self.assertTrue(inventory_records(dict(count=0,items=[]),source,url)[1]['complete'])
        for invalid in [dict(data,count=0),dict(data,count='1'),dict(data,items=[item,item]),
                        dict(data,items=[dict(item,is_external=True)]),dict(data,items=[dict(item,url='999-other-job')]),
                        dict(data,items=[dict(item,career_domain='evil.example')])]:
            with self.assertRaises(ValueError):inventory_records(invalid,source,url)
        with self.assertRaises(ValueError):inventory_records(data,source,url.replace('57781','57765'))
        def capture(*args,**kwargs):kwargs['cegid_responses'].append(dict(data,count=2));return [],True
        with patch('collector.rendering.render_pages',side_effect=capture):
            result=cegid_records(source,Client({}))
        self.assertFalse(result.stats['complete']);self.assertFalse(result.stats['closure_complete'])
        self.assertEqual(result.stats['status'],'partial')
