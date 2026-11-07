import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from collector.applications import verify_application,odoo_application,ApplicationClosed
from collector.universal import Document
from collector.employer_pages import index_records
from collector.provinces import coverage
from scripts.import_province_geography import build
from scripts.integrate_groningen import integrate
from collector.pipeline import ROOT,read


class PublicClient:
    def __init__(self,pages):self.pages=pages;self.calls=[]
    def request(self,url,**kwargs):
        self.calls.append(url)
        return self.pages[url].encode(),200,url


class ProvincialTests(unittest.TestCase):
    def test_province_separation_recent_verification_and_municipal_jobs(self):
        company=dict(id='one',name='One',source_ids=['one'],groningen_research={'size':{'qualification':'verified_50_plus'}},workplaces=[dict(region_code='NL11',city='Veendam',municipality_code='A',location_confidence='confirmed'),dict(region_code='NL11',city='Winschoten',municipality_code='B',location_confidence='confirmed')])
        geography=dict(municipalities=[dict(cbs_code=c,name=c,settlement_count=1) for c in ['A','B']])
        base=dict(status='open',verification={'state':'verified','policy_version':2},link_status='verified',internship_type='internship',source_id='one',employer='One',region_codes=['NL11'],city='Veendam',last_verified_at='2026-11-06T05:00:00+00:00')
        jobs=[dict(base,id='current'),dict(base,id='legacy',verification={}),dict(base,id='stale',last_verified_at='2026-11-01T00:00:00+00:00'),dict(base,id='unverified',link_status='unverified'),dict(base,id='elsewhere',region_codes=['NL12']),dict(base,id='student',internship_type='working-student')]
        result=coverage([company],[dict(id='one',enabled=True)],[dict(id='one',checked_at='2026-11-06T05:00:00+00:00',status='partial',records_inspected=2)],jobs,geography,'2026-11-06T06:00:00+00:00',research_key='groningen_research',region_code='NL11',province='Groningen')
        self.assertEqual(result['verified_hr_internship_ids'],['current'])
        self.assertEqual([m['verified_hr_internships'] for m in result['municipalities']],[1,0])
        self.assertEqual(result['summary']['employers'],1)
        self.assertEqual(result['province'],'Groningen')
        self.assertEqual(coverage([company],[],[],[],geography,'2026-11-06T06:00:00+00:00')['summary']['employers'],0)

    def test_reviewed_import_is_idempotent_and_group_feed_is_shared(self):
        companies=read(ROOT/'data/companies.json',[]);sources=read(ROOT/'data/sources.json',[])
        rows=read(ROOT/'data/groningen-employers.json',[]);geography=read(ROOT/'data/groningen-geography.json',{})
        c,s,_=integrate(companies,sources,geography,rows)
        c2,s2,_=integrate(c,s,geography,rows)
        self.assertEqual(c,c2);self.assertEqual(s,s2)
        self.assertEqual(len({x['id'] for x in c}),len(c))
        shipyard=next(x for x in c if x['id']=='royal-niestern-sander')
        parent=next(x for x in c if x['id']=='royal-wagenborg')
        self.assertEqual(shipyard['source_ids'],parent['source_ids'])
        self.assertEqual(len([x for x in c if x['id']=='rijksuniversiteit-groningen-campus-fryslan']),1)

    def test_cbs_frame_has_unique_codes_and_municipal_totals(self):
        g=read(ROOT/'data/groningen-geography.json',{})
        self.assertEqual(g['municipality_count'],10);self.assertEqual(g['settlement_count'],199)
        places=[p['code'] for m in g['municipalities'] for p in m['settlements']]
        self.assertEqual(len(set(places)),199)
        self.assertEqual(sum(m['settlement_count'] for m in g['municipalities']),199)
        names={x['name'] for x in g['ambiguous_settlement_names']}
        self.assertTrue({'Winsum','Borgercompagnie','Niekerk','Oostwold'}.issubset(names))

    def test_nested_job_cards_and_all_observed_pages_are_read(self):
        client=PublicClient({'https://example.org/jobs':'<a href="/jobs/detail/one-1">One <a href="/jobs/apply/1">Apply</a></a><a href="/jobs/page/2">2</a>',
            'https://example.org/jobs/page/2':'<a href="/jobs/detail/two-2">Two</a><a href="/jobs/page/2">2</a>'})
        source=dict(id='test',employer='Test',allowed_hosts=['example.org'],index_urls=['https://example.org/jobs'],job_url_pattern=r'/jobs/detail/',index_page_pattern=r'/jobs/page/\d+$',report_index_scope=True,inventory_scope_complete=True)
        jobs=index_records(source,client)
        self.assertEqual(len(jobs),2);self.assertEqual(len(client.calls),2)
        self.assertEqual(jobs.stats['pages_read'],2)
        self.assertTrue(jobs.stats['complete']);self.assertFalse(jobs.stats['closure_complete'])

    def test_count_mismatch_cannot_claim_complete_inventory(self):
        source=dict(id='test',employer='Test',allowed_hosts=['example.org'],index_urls=['https://example.org/jobs'],job_url_pattern=r'/job/',index_job_count_pattern=r'(\d+) jobs')
        with self.assertRaisesRegex(ValueError,'published inventory count'):
            index_records(source,PublicClient({'https://example.org/jobs':'2 jobs <a href="/job/1">One</a>'}))

    def test_odoo_requires_same_vacancy_and_applicant_fields(self):
        source=dict(allowed_hosts=['example.org'],application_check='odoo')
        page='<main><h1>HR stage</h1><a href="/jobs/apply/306">Apply</a><a href="/jobs/apply/old-241">Old link</a></main>'
        form='<main><h1>Sollicitatieformulier</h1><form id="hr_recruitment_form" data-model_name="hr.applicant"><input name="partner_name"><input name="email_from"><button type="submit">Solliciteren</button></form>Vacature HR stage Locatie Fotofabriek Afdeling Stages</main>'
        client=PublicClient({'https://example.org/jobs/306':page,'https://example.org/jobs/apply/306':form})
        result=verify_application(dict(url='https://example.org/jobs/306',title='HR stage'),source,client)
        self.assertEqual(result['url'],'https://example.org/jobs/apply/306')
        self.assertNotIn('https://example.org/jobs/apply/old-241',client.calls)
        client.pages['https://example.org/jobs/apply/306']=form.replace('<button type="submit">Solliciteren</button>','<a class="s_website_form_send" role="button" href="#">Solliciteren</a>')
        self.assertEqual(verify_application(dict(url='https://example.org/jobs/306',title='HR stage'),source,client)['url'],'https://example.org/jobs/apply/306')
        client.pages['https://example.org/jobs/apply/306']=form.replace('type="submit"','type="submit" disabled')
        with self.assertRaisesRegex(ValueError,'enabled submit'):
            verify_application(dict(url='https://example.org/jobs/306',title='HR stage'),source,client)
        client.pages['https://example.org/jobs/apply/306']=form.replace('Vacature HR stage','Vacature Other job')
        with self.assertRaisesRegex(ValueError,'same vacancy'):
            verify_application(dict(url='https://example.org/jobs/306',title='HR stage'),source,client)

    def test_avature_checks_job_id_and_same_job_application_entry(self):
        source=dict(allowed_hosts=['example.org'],application_check='avature-linked')
        pages={'https://example.org/job/1':'<a href="/External/JobDetail?jobId=7">Apply</a>',
            'https://example.org/External/JobDetail?jobId=7':'<main><h1>HR stage</h1><a href="/External/Login?jobId=7">Solliciteren</a></main>'}
        record=dict(url='https://example.org/job/1',title='HR stage',posting_identifier='7')
        self.assertTrue(verify_application(record,source,PublicClient(pages))['account_required'])
        with self.assertRaisesRegex(ValueError,'requisition differs'):
            verify_application(dict(record,posting_identifier='8'),source,PublicClient(pages))
        pages['https://example.org/External/JobDetail?jobId=7']='<main>This job is closed</main>'
        with self.assertRaises(ApplicationClosed):verify_application(record,source,PublicClient(pages))

    def test_hanos_placeholder_alone_is_not_an_active_application(self):
        source=dict(allowed_hosts=['example.org'],application_check='hanos-rendered')
        client=PublicClient({'https://example.org/job/1':'<h1>HR stage</h1><div id="application-form"></div>'})
        with patch('collector.rendering.render_pages',return_value=([('https://example.org/job/1',b'<div id="application-form"></div>')],True)):
            with self.assertRaisesRegex(ValueError,'form unavailable'):
                verify_application(dict(url='https://example.org/job/1',title='HR stage'),source,client)



class PartialAvailabilityTests(unittest.TestCase):
    def fixture(self):
        from collector.universal import job_from_json
        source=dict(id='review-example',employer='Example',adapter='employer-index',allowed_hosts=['example.org'])
        record=job_from_json(dict(title='HR Intern',description='HR internship for a student. Fluent in English.',jobLocation={'address':{'addressLocality':'Groningen','addressCountry':'NL'}}),'https://example.org/jobs/1',source)
        return source,record

    def test_failed_detail_keeps_previous_postings_and_never_marks_source_complete(self):
        from collector.pipeline import process_source,finalize,now
        from collector.universal import Inventory
        import copy
        source,record=self.fixture();failed=dict(record,url='https://example.org/jobs/2',external_id='2',needs_page=True)
        inventory=Inventory([record,failed],dict(status='ok',complete=True,closure_complete=False))
        def enrich(row,*args,**kwargs):
            if row['url']==failed['url']:raise ValueError('Detail page inaccessible')
            return row
        class Client:
            def request(self,url,**kwargs):return b'',200,url
        stamp=now()
        with patch('collector.pipeline.collect',return_value=inventory),patch('collector.pipeline.enrich',side_effect=enrich):
            part=process_source(source,Client(),stamp)
        self.assertEqual(part['report']['status'],'partial')
        self.assertTrue(part['report']['inventory_complete'])
        self.assertFalse(part['report']['complete']);self.assertFalse(part['report']['closure_complete'])
        self.assertEqual(part['closure_eligible'],[])
        prior=copy.deepcopy(read(ROOT/'data/catalog.json',{}))
        retained=copy.deepcopy(prior['jobs'][0]);retained.update(id='old-same-source',source_id=source['id'],employer='Example',url='https://example.org/jobs/old',apply_url='https://example.org/jobs/old',status='open',last_verified_at=stamp,last_seen_at=stamp,valid_through=None,verification={},link_status='verified')
        proven=copy.deepcopy(retained);proven.update(id='old-proven-same-source',url='https://example.org/jobs/proven',apply_url='https://example.org/jobs/proven',verification=dict(state='verified',policy_version=2,checked_at=stamp))
        prior['jobs'].extend([retained,proven])
        before={j['id'] for j in prior['jobs']}
        with tempfile.TemporaryDirectory() as directory:
            result,report=finalize([source],[source],prior,{},[part],stamp,Path(directory))
        self.assertTrue(before.issubset({j['id'] for j in result['jobs']}))
        old=next(j for j in result['jobs'] if j['id']==retained['id'])
        self.assertEqual(old['status'],'unverified');self.assertEqual(old['link_status'],'legacy-verification');self.assertEqual(old.get('missing_count'),retained.get('missing_count'))
        kept_proven=next(j for j in result['jobs'] if j['id']==proven['id'])
        self.assertEqual(kept_proven['status'],'open');self.assertEqual(kept_proven['verification'],proven['verification'])
        self.assertEqual(kept_proven.get('missing_count'),proven.get('missing_count'))
        self.assertEqual(result['update_status'],'partial')

    def test_cached_job_still_checks_application_and_blocked_access_is_partial(self):
        from collector.pipeline import process_source,now
        from collector.runtime import PageCache
        from collector.universal import Inventory
        source,record=self.fixture();source['application_check']='avature-linked'
        inventory=Inventory([dict(record,needs_page=True)],dict(status='ok',complete=True,closure_complete=False))
        with tempfile.TemporaryDirectory() as directory:
            cache=PageCache('review-example',directory);cache.put(record['url'],record)
            with patch('collector.pipeline.collect',return_value=inventory),patch('collector.pipeline.enrich') as enrich,patch('collector.verification.verify_vacancy',side_effect=ValueError('robots.txt disallows application')) as check:
                part=process_source(source,object(),now(),cache=cache)
        enrich.assert_not_called();check.assert_called_once()
        self.assertEqual(part['jobs'][0]['status'],'unverified')
        self.assertEqual(part['report']['status'],'partial')
        self.assertFalse(part['report']['complete']);self.assertEqual(part['closure_eligible'],[])


if __name__=='__main__':unittest.main()
