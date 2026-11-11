"""Issue #23: do not lose a known vacancy's explicit closure or silently filter HR candidates."""
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from collector.daily import collect_shard
from collector.pipeline import ROOT, finalize, process_source, read
from collector.universal import Crawler, Inventory, job_from_json
from tests.test_all_employers import FakeClient, posting, source


class KnownVacancyEvidenceTests(unittest.TestCase):
    def known(self, title='Traineeship Salarisprofessional'):
        s=source()
        url='https://example.org/vacatures/traineeship-salarisprofessional-leeuwarden-284'
        s.update(known_job_urls=[url],known_job_titles={url:title})
        return s,url

    def test_fresh_same_url_exact_named_closure_survives_partial_inventory(self):
        s,url=self.known()
        pages={url:'<main><h3>De vacature "Traineeship Salarisprofessional" is niet meer beschikbaar.</h3><h1>Related: HR Intern</h1></main>',
               s['start_urls'][0]:'<main>Other positions available</main>'}
        with tempfile.TemporaryDirectory() as d,patch.dict(os.environ,{'COLLECTOR_CACHE_DIR':d}):
            rows=Crawler(s,FakeClient(pages)).run()
        self.assertEqual(list(rows),[])
        self.assertIn(url,rows.stats['verified_closed_urls'])
        self.assertEqual(rows.stats['explicit_known_closures'],1)
        self.assertFalse(rows.stats['closure_complete'])  # not a complete inventory
        self.assertEqual(rows.stats['matching'] if 'matching' in rows.stats else 0,0)

    def test_other_job_closure_and_redirect_never_close_known_vacancy(self):
        s,url=self.known()
        for document in ('De vacature "Different HR Intern" is niet meer beschikbaar.',
                         'De vacature "Traineeship Salarisprofessional" is nog beschikbaar.',
                         '<h1>Traineeship Salarisprofessional</h1> Read more vacancies'):
            with self.subTest(document=document),tempfile.TemporaryDirectory() as d,patch.dict(os.environ,{'COLLECTOR_CACHE_DIR':d}):
                crawler=Crawler(s,FakeClient({url:'<main>'+document+'</main>'}))
                crawler.visit(url,is_job=True)
                self.assertFalse(crawler.closed_urls)
        class RedirectClient(FakeClient):
            def request(self,url,**kwargs):
                return b'<main>De vacature "Traineeship Salarisprofessional" is niet meer beschikbaar.</main>',200,'https://example.org/vacatures/other'
        with tempfile.TemporaryDirectory() as d,patch.dict(os.environ,{'COLLECTOR_CACHE_DIR':d}):
            crawler=Crawler(s,RedirectClient({}))
            crawler.visit(url,is_job=True)
            self.assertFalse(crawler.closed_urls)

    def test_unreviewed_title_and_stale_cache_cannot_certify_closure(self):
        s,url=self.known()
        s['known_job_titles']={}
        page='<main>De vacature "Traineeship Salarisprofessional" is niet meer beschikbaar.</main>'
        with tempfile.TemporaryDirectory() as d,patch.dict(os.environ,{'COLLECTOR_CACHE_DIR':d}):
            crawler=Crawler(s,FakeClient({url:page}))
            crawler.visit(url,is_job=True)
            self.assertFalse(crawler.closed_urls)
        s['known_job_titles']={url:'Traineeship Salarisprofessional'}
        with tempfile.TemporaryDirectory() as d,patch.dict(os.environ,{'COLLECTOR_CACHE_DIR':d}):
            crawler=Crawler(s,FakeClient({url:page}))
            crawler.cache.put(url,dict(records=[],links=[],empty=False))
            crawler.visit(url,is_job=True)
            self.assertFalse(crawler.closed_urls)

    def test_explicit_closure_keeps_all_catalog_ids_and_is_idempotent(self):
        prior=read(ROOT/'data/catalog.json',{})
        registry=read(ROOT/'data/sources.json',[])
        target=next(j for j in prior['jobs'] if j['source_id']=='auto-bentacera' and j['title']=='Traineeship Salarisprofessional')
        s=next(s for s in registry if s['id']==target['source_id'])
        stamp=prior['last_attempt_at']
        part=dict(report=dict(id=s['id'],status='partial',complete=False,closure_complete=False,
                    verified_closed_urls=[target['url']],checked_at=stamp,records_inspected=1),
                  jobs=[],closure_eligible=[])
        with tempfile.TemporaryDirectory() as folder:
            first,_=finalize(registry,[s],prior,{'sources':[]},[part],stamp,Path(folder))
            second,_=finalize(registry,[s],first,{'sources':[]},[part],stamp,Path(folder))
        self.assertEqual(first['jobs'],second['jobs'])
        self.assertEqual({x['id'] for x in prior['jobs']},{x['id'] for x in second['jobs']})
        updated=next(j for j in second['jobs'] if j['id']==target['id'])
        self.assertEqual(updated['status'],'closed')
        self.assertEqual(updated['verification']['policy_version'],2)
        self.assertEqual(updated['first_discovered_at'],target['first_discovered_at'])

    def test_daily_forwards_title_only_for_known_nonclosed_urls(self):
        s=source()
        company=dict(id='example',name='Example',source_ids=[s['id']])
        jobs=[dict(source_id=s['id'],url='https://example.org/jobs/hr',title='HR Intern',status='unverified'),
              dict(source_id=s['id'],url='https://example.org/jobs/closed',title='Closed HR Intern',status='closed')]
        observed=[]
        def fake_read(path,default):
            if path.name=='catalog.json':return {'jobs':jobs}
            return default
        def fake_process(src,client,stamp,prev_count,cache):
            observed.append(src)
            return dict(report=dict(id=src['id'],status='partial',checked_at=stamp),jobs=[],closure_eligible=[])
        with tempfile.TemporaryDirectory() as d,patch('collector.daily.provision_files',return_value=([company],[s])), \
             patch('collector.daily.read',side_effect=fake_read),patch('collector.daily.process_source',side_effect=fake_process):
            collect_shard(shard=0,shards=1,output=Path(d)/'shard-0.json')
        self.assertEqual(observed[0]['known_job_titles'],{'https://example.org/jobs/hr':'HR Intern'})
        self.assertEqual(observed[0]['known_job_urls'],['https://example.org/jobs/hr'])


class CandidateDropEvidenceTests(unittest.TestCase):
    def test_wrong_hiring_organization_is_not_silently_attributed_to_subsidiary(self):
        s=source()
        body='<script type="application/ld+json">'+json.dumps(posting(hiringOrganization={'name':'Different Group'}))+'</script>'
        with tempfile.TemporaryDirectory() as d,patch.dict(os.environ,{'COLLECTOR_CACHE_DIR':d}):
            rows=Crawler(s,FakeClient({s['start_urls'][0]:body})).run()
        self.assertFalse(rows)
        self.assertEqual(rows.stats['structured_identity_mismatches'],1)

    def test_filter_reports_unresolved_geography_and_ownership_without_promoting(self):
        s=source()
        good=job_from_json(posting(),'https://example.org/jobs/1',s)
        no_country=dict(good,countries=[],country=None,location='Unrecognised',url='https://example.org/jobs/2')
        no_hr=dict(good,title='Full-time Accountant',text='Permanent job',url='https://example.org/jobs/3')
        foreign=dict(good,employer='Different Group',url='https://example.org/jobs/4')
        rows=Inventory([good,no_country,no_hr,foreign],dict(status='partial',complete=False))
        with patch('collector.pipeline.collect',return_value=rows), \
             patch('collector.pipeline.enrich',side_effect=lambda r,*args,**kw:r), \
             patch('collector.verification.verify_vacancy',side_effect=ValueError('Applicant form not available')):
            part=process_source(s,FakeClient({}),'2026-11-11T11:00:00+00:00')
        self.assertEqual(part['report']['candidate_filter_reasons'],{
            'hr-candidate-without-country':1,'not-hr-student-role':1,'ownership-rejected':1})
        self.assertEqual(len(part['jobs']),1)
        self.assertEqual(part['jobs'][0]['status'],'unverified')


if __name__=='__main__':unittest.main()
