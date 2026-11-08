"""Offline real-response replay and conservative identity/timeout regressions."""
import copy
import gzip
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from collector.applications import ApplicationClosed
from collector.pipeline import process_source, finalize
from collector.universal import Inventory
from collector.verification import verify_vacancy, same_requisition, verified_job
from scripts.coverage_sprint18_batch2 import FIXTURES, REPORT, rank
from scripts.replay_sprint18_batch2 import replay


class IdentityTests(unittest.TestCase):
    def setUp(self):
        self.stamp='2026-11-08T12:00:00+00:00'
        self.url='https://example.org/vacatures/stage-hr'
        self.record=dict(url=self.url,title='Stage HR',external_id=self.url)
        self.source=dict(allowed_hosts=['example.org','ats.example.org'])
        self.form=b'<form id="application"><input name="name"><input type="email"><button>Apply</button></form>'

    def verify(self, target, identifier='123', app_title='Stage HR', app_id=None, body=None, final=None):
        post={'@type':'JobPosting','title':'Stage HR','identifier':identifier}
        vacancy=('<h1>Stage HR</h1><script type="application/ld+json">'+json.dumps(post)+'</script>'
                 '<a href="'+target+'">Solliciteer direct</a>').encode()
        app=('<h1>'+app_title+'</h1>').encode()+(self.form if body is None else body)
        if app_id:app+=('<script type="application/ld+json">'+json.dumps(dict(post,identifier=app_id))+'</script>').encode()
        client=unittest.mock.Mock()
        client.request.side_effect=lambda url: (vacancy,200,self.url) if url==self.url else (app,200,final or target)
        return verify_vacancy(self.record,self.source,client,self.stamp)

    def test_structured_id_bridges_observed_ats_cta_without_mutation(self):
        target='https://ats.example.org/ApplicationForm?job=123'
        proof=self.verify(target)
        self.assertEqual(proof['url'],target)
        self.assertEqual(proof['method'],'linked-same-vacancy-applicant-form')
        self.assertNotIn('posting_identifier',self.record)

    def test_dutch_child_retains_complete_path(self):
        proof=self.verify(self.url+'/solliciteer',identifier=None)
        self.assertEqual(proof['vacancy_match'],'title')
        for target in ('https://example.org/solliciteer',self.url+'-other/solliciteer',
                       self.url+'/solliciteer/other','https://other.org/vacatures/stage-hr/solliciteer'):
            self.assertFalse(same_requisition(self.url,target))

    def test_cta_cannot_supply_its_own_identity(self):
        for identifier in (None,'1234',{'value':'456'}):
            with self.subTest(identifier=identifier),self.assertRaisesRegex(ValueError,'matching vacancy identifier'):
                self.verify('https://ats.example.org/ApplicationForm?job=123',identifier=identifier)

    def test_collected_structured_conflict_rejected(self):
        self.record['posting_identifier']='456'
        with self.assertRaisesRegex(ValueError,'differs from collected'):
            self.verify('https://ats.example.org/ApplicationForm?job=123')
        self.record.pop('posting_identifier')
        with self.assertRaisesRegex(ValueError,'matching vacancy identifier'):
            self.verify('https://ats.example.org/ApplicationForm?job=999')

    def test_title_form_host_redirect_deadline_and_requisition_still_required(self):
        target='https://ats.example.org/ApplicationForm?job=123'
        invalid=[dict(app_title='Software Intern'),dict(body=b''),dict(app_id='456'),
                 dict(final=target+'&other=1'),dict(body=self.form.replace(b'<button>',b'<button disabled>')),
                 dict(body=b'Verify you are human'+self.form)]
        for kwargs in invalid:
            with self.subTest(kwargs=kwargs),self.assertRaises(ValueError):self.verify(target,**kwargs)
        with self.assertRaises(ValueError):self.verify('https://unapproved.org/ApplicationForm?job=123')
        expired=b'<script type="application/ld+json">{"@type":"JobPosting","title":"Stage HR","validThrough":"2020-01-01"}</script>'
        with self.assertRaises(ApplicationClosed):self.verify(target,body=self.form+expired)


class RealBatchTests(unittest.TestCase):
    def test_exact_before_after_and_two_finalizations(self):
        report=replay()
        self.assertEqual((report['candidate_count'],report['verified_before'],report['verified_after']),(8,0,0))
        self.assertEqual(report['global_before'],dict(open=24,unverified=296,closed=4))
        self.assertEqual(report['global_before'],report['global_after'])
        self.assertTrue(report['two_finalizations_idempotent'])
        achmea=next(r for r in report['rows'] if r['company_id']=='centraal-beheer-achmea')
        self.assertIn('matching vacancy identifier',achmea['before']['error'])
        self.assertIn('Applicant form not established',achmea['after']['error'])
        blocked=next(r for r in report['rows'] if r['company_id']=='defabrique-holding')
        self.assertIn('robots.txt unavailable: 406',blocked['after']['error'])

    def test_fixed_scope_budget_and_body_integrity(self):
        saved=json.loads((REPORT/'ranking.json').read_text())
        self.assertEqual({r['company_id'] for r in saved['shortlist']},{r['company_id'] for r in rank()['shortlist']})
        self.assertEqual(len(saved['shortlist']),17)
        for path in FIXTURES.glob('*/capture.json'):
            payload=json.loads(path.read_text())
            self.assertLessEqual(payload['requests'],8)
            for response in payload['responses']:
                body=gzip.decompress((path.parent/response['file']).read_bytes())
                self.assertEqual(hashlib.sha256(body).hexdigest(),response['sha256'])


class VeepeeTimeoutTests(unittest.TestCase):
    def setUp(self):
        root=FIXTURES.parents[2]
        self.prior=json.loads(gzip.decompress((FIXTURES/'catalog-before.json.gz').read_bytes()))
        self.job=next(j for j in self.prior['jobs'] if j['id']=='638f5719bdad59dfc7be')
        self.source=next(s for s in json.loads((root/'data/sources.json').read_text()) if s['id']==self.job['source_id'])
        self.record=dict(source_id=self.source['id'],external_id=self.job['external_id'],employer=self.job['employer'],
                         title=self.job['title'],text='HR recruitment internship',employment='internship',
                         location=self.job['city'],countries=self.job['countries'],url=self.job['url'],apply_url=self.job['url'])

    def process(self,client,stamp,records=None):
        with patch('collector.pipeline.collect',return_value=records if records is not None else [self.record]),patch('collector.pipeline.enrich',side_effect=lambda r,*args,**kwargs:r):
            return process_source(self.source,client,stamp)

    def test_repeated_timeout_never_closes_or_renews_verification_then_recovers(self):
        # Simulate the last verified observation before the recorded timeout.
        self.job['status']='open'
        self.job['verification']=dict(self.job['verification'],state='verified')
        original_date=self.job['last_verified_at']
        prior=self.prior
        client=unittest.mock.Mock()
        client.request.side_effect=TimeoutError('The read operation timed out')
        for stamp in ('2026-11-08T12:00:00+00:00','2026-11-09T12:00:00+00:00','2026-11-10T12:00:00+00:00'):
            part=self.process(client,stamp)
            self.assertEqual(part['report']['status'],'partial')
            self.assertEqual(part['closure_eligible'],[])
            with tempfile.TemporaryDirectory() as folder:
                prior,_=finalize([self.source],[self.source],prior,{'sources':[]},[part],stamp,Path(folder))
            job=next(j for j in prior['jobs'] if j['id']==self.job['id'])
            self.assertEqual(job['status'],'unverified')
            self.assertEqual(job['verification']['state'],'incomplete')
            self.assertEqual(job['last_verified_at'],original_date)
            self.assertEqual(job['missing_count'],0)
            self.assertFalse(verified_job(job,stamp))
        client.request.side_effect=None
        body=('<h1>'+self.job['title']+'</h1><form id="application"><input name="name"><input type="email"><button>Apply</button></form>').encode()
        client.request.return_value=(body,200,self.job['url'])
        stamp='2026-11-11T12:00:00+00:00'
        part=self.process(client,stamp)
        with tempfile.TemporaryDirectory() as folder:
            recovered,_=finalize([self.source],[self.source],prior,{'sources':[]},[part],stamp,Path(folder))
        job=next(j for j in recovered['jobs'] if j['id']==self.job['id'])
        self.assertTrue(verified_job(job,stamp))
        self.assertEqual(job['first_discovered_at'],self.job['first_discovered_at'])

    def test_inventory_timeout_and_partial_absence_preserve_history(self):
        stamp='2026-11-08T12:00:00+00:00'
        with patch('collector.pipeline.collect',side_effect=TimeoutError('The read operation timed out')):
            failed=process_source(self.source,unittest.mock.Mock(),stamp)
        self.assertEqual(failed['report']['status'],'failed')
        partial=self.process(unittest.mock.Mock(),stamp,Inventory([],dict(status='partial',complete=False)))
        for part in (failed,partial):
            self.assertEqual(part['closure_eligible'],[])
            with tempfile.TemporaryDirectory() as folder:
                result,_=finalize([self.source],[self.source],copy.deepcopy(self.prior),{'sources':[]},[part],stamp,Path(folder))
            job=next(j for j in result['jobs'] if j['id']==self.job['id'])
            self.assertEqual(job['status'],self.job['status'])
            self.assertEqual(job['missing_count'],self.job['missing_count'])
            self.assertEqual(job['last_verified_at'],self.job['last_verified_at'])
