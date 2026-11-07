"""Offline feed -> policy-v2 verification -> final catalog regression (Issue #10)."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from collector.pipeline import ROOT, finalize, process_source, read, reconcile
from collector.verification import verified_job


class FixtureClient:
    def __init__(self, source, target, body, offers=True):
        offer=dict(id=971718,status='published',title=target['title'],careers_url=target['url'],
            country_code='NL',city='Eindhoven',description='HR internship at Ennatuurlijk')
        self.pages={source['feed_url'].rstrip('/'):json.dumps({'offers':[offer] if offers else []}).encode(),
                    target['url']:body.encode()}

    def request(self, url):
        # Unplanned requests fail; there is no network transport in this fixture.
        return self.pages[url],200,url


class EnnatuurlijkReconciliationTests(unittest.TestCase):
    def setUp(self):
        self.registry=read(ROOT/'data/sources.json',[])
        self.source=next(s for s in self.registry if s['id']=='auto-ennatuurlijk')
        self.target=next(j for j in read(ROOT/'data/catalog.json',{})['jobs'] if j['id']=='70d297b765fc2696c836')
        self.body='<h1>'+self.target['title']+'</h1><form id="apply"><input name="name"><input type="email" name="email"><button type="submit">Apply</button></form>'

    def cycle(self, prior, day=7, body=None, offers=True, failed=False, verify=True):
        observed=f'2026-11-{day:02d}T12:00:00+00:00';stamp=f'2026-11-{day:02d}T13:30:00+00:00'
        client=FixtureClient(self.source,self.target,self.body if body is None else body,offers)
        if failed:client.request=lambda url: (_ for _ in ()).throw(ValueError('Incomplete inventory'))
        part=process_source(self.source,client,observed,verify=verify)
        with tempfile.TemporaryDirectory() as directory:
            result,coverage=finalize(self.registry,[self.source],dict(jobs=copy.deepcopy(prior)),{},[part],stamp,Path(directory))
            self.assertEqual(read(Path(directory)/'catalog.json',{}),result)
        return result['jobs'],part,coverage

    def assert_identity(self, job):
        for field in ('id','first_discovered_at','url','apply_url'):
            self.assertEqual(job[field],self.target[field],field)
        self.assertEqual(job['employer'],'Ennatuurlijk');self.assertEqual(job['source_id'],'auto-ennatuurlijk')
        self.assertNotIn('auto-tilburg-university',job.get('duplicate_source_ids',[]))

    def test_full_pipeline_current_verification_survives_historical_missing(self):
        # Use the actual post-run regression as history. Only the fixture form
        # establishes a fresh verification; never promote the input by hand.
        prior=[copy.deepcopy(self.target)]
        for day in (7,7,8,9):
            rows,part,coverage=self.cycle(prior,day)
            self.assertEqual(part['report']['verification_states'],{'verified':1})
            self.assertEqual(part['closure_eligible'],[self.source['id']])
            self.assertNotEqual(part['jobs'][0]['id'],self.target['id'])
            self.assertEqual(len(rows),1);job=rows[0];self.assert_identity(job)
            self.assertTrue(verified_job(job,f'2026-11-{day:02d}T13:30:00+00:00'))
            self.assertEqual(job['application_verification'],part['jobs'][0]['application_verification'])
            self.assertEqual(job['last_seen_at'],part['jobs'][0]['last_seen_at'])
            self.assertEqual(job['missing_count'],0)
            self.assertNotIn('missing_since',job);self.assertNotIn('last_missing_run',job)
            self.assertEqual(coverage['quality']['verified_internships'],1)
            if day==7 and prior[0].get('status')=='open':self.assertEqual(rows,prior)
            prior=rows

    def test_ownership_review_precedes_identity_and_absence(self):
        old=dict(self.target,source_id='auto-tilburg-university',employer='Tilburg University')
        rows,_,_=self.cycle([old]);self.assert_identity(rows[0]);self.assertEqual(rows[0]['status'],'open')

    def test_consecutive_absences_close_only_after_three_complete_days(self):
        rows,_,_=self.cycle([self.target])
        for day,count in ((8,1),(8,1),(9,2),(10,3)):
            rows,part,_=self.cycle(rows,day,offers=False)
            self.assertEqual(part['closure_eligible'],[self.source['id']])
            self.assertEqual(rows[0]['missing_count'],count)
            self.assertEqual(rows[0]['status'],'closed' if count==3 else 'unverified');self.assert_identity(rows[0])

    def test_failed_inventory_does_not_count_as_absence(self):
        rows,_,_=self.cycle([self.target]);previous=copy.deepcopy(rows)
        for day in (8,9):
            rows,part,_=self.cycle(rows,day,failed=True)
            self.assertEqual(part['closure_eligible'],[])
            self.assertEqual(rows[0]['missing_count'],0);self.assertNotIn('missing_since',rows[0])
            self.assertEqual(rows[0]['last_seen_at'],previous[0]['last_seen_at'])
            self.assertEqual(rows[0]['status'],'open' if day==8 else 'unverified')
            if day==9:self.assertEqual(rows[0]['link_status'],'stale')

    def test_current_application_failure_or_explicit_closure_beats_old_proof(self):
        for body,state,status in (('<h1>'+self.target['title']+'</h1>','incomplete','unverified'),
                ('<h1>'+self.target['title']+'</h1><p>This job is closed</p>','closed','closed')):
            with self.subTest(state=state):
                prior,_,_=self.cycle([self.target]);rows,part,_=self.cycle(prior,8,body=body)
                self.assertEqual(part['jobs'][0]['verification']['state'],state)
                self.assertEqual(rows[0]['verification']['state'],state);self.assertEqual(rows[0]['status'],status)
                self.assertEqual(rows[0]['missing_count'],0)
                self.assert_identity(rows[0]);self.assertFalse(verified_job(rows[0],'2026-11-08T13:30:00+00:00'))
                if state=='closed':
                    rows,_,_=self.cycle(rows,9,offers=False);self.assertEqual(rows[0]['status'],'closed')

    def test_disabled_verification_cannot_reuse_historical_application_proof(self):
        prior,_,_=self.cycle([self.target]);rows,_,_=self.cycle(prior,8,verify=False)
        self.assertEqual(rows[0]['status'],'unverified');self.assertEqual(rows[0]['verification']['policy_version'],2)
        self.assertFalse(verified_job(rows[0],'2026-11-08T13:30:00+00:00'))

    def test_unreviewed_source_alias_reconciles_before_synthetic_missing_timestamp(self):
        # Generic identity path, independent of the Ennatuurlijk ownership review.
        old=copy.deepcopy(self.target)
        old.update(id='historical-id',source_id='old-source')
        fresh=copy.deepcopy(old)
        fresh.update(id='new-id',source_id='new-source',last_seen_at='2026-11-08T12:00:00+00:00')
        rows=reconcile([old],[fresh],{'old-source','new-source'},'2026-11-08T13:30:00+00:00')
        self.assertEqual(len(rows),1);self.assertEqual(rows[0]['id'],'historical-id')
        self.assertEqual(rows[0]['source_id'],'new-source');self.assertEqual(rows[0]['missing_count'],0)
        self.assertEqual(rows[0]['last_seen_at'],fresh['last_seen_at'])
        self.assertEqual(rows[0]['first_discovered_at'],old['first_discovered_at'])

    def test_partial_inventory_without_target_preserves_absence_counter(self):
        prior,_,_=self.cycle([self.target])
        part=dict(report=dict(id=self.source['id'],status='partial',records_inspected=1),
                  jobs=[],closure_eligible=[])
        with tempfile.TemporaryDirectory() as directory:
            result,_=finalize(self.registry,[self.source],dict(jobs=prior),{},[part],
                '2026-11-08T13:30:00+00:00',Path(directory))
        self.assertEqual(result['jobs'],prior)
