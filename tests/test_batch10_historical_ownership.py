"""Legacy external referral quarantine: preserve IDs, avoid fake HR vacancies.

All tests are offline; no requests, source activation, or job applications.
"""
import copy
import tempfile
import unittest
from pathlib import Path

from collector.ownership import quarantine_historical_external_jobs
from collector.pipeline import ROOT, finalize, read

SOURCE_ID='auto-tilburg-university'
AGG='https://www.nationalevacaturebank.nl/vacature/example-hr-stage'
OFFICIAL='https://www.tilburguniversity.edu/over-ons/werken-bij/stage-hr'

def record(url=AGG,status='unverified',id='legacy-one',verification_state='incomplete'):
    return {'id':id,'source_id':SOURCE_ID,
            'source_name':'Tilburg University',
            'employer':'An actual third-party employer',
            'url':url,'apply_url':url,
            'status':status,'link_status':'incomplete',
            'last_verified_at':None,
            'verification':{'policy_version':2,'state':verification_state,'checked_at':'2026-11-07T07:04:32+00:00',
                            'reason':'Previous verify failed'},
            'first_discovered_at':'2026-11-07T07:04:32+00:00',
            'last_seen_at':'2026-11-07T07:04:32+00:00'}

SOURCES=[
 {'id':SOURCE_ID,'employer':'Tilburg University',
  'ownership_scope':'reviewed-hosts','require_employer_identity':True,
  'allowed_hosts':['www.tilburguniversity.edu']},
 {'id':'reviewed-recruitee','employer':'Actual Employer',
  'ownership_scope':'reviewed-hosts',
  'allowed_hosts':['tenant.recruitee.com']}
]

class HistoricalOwnershipQuarantineTests(unittest.TestCase):
    def test_external_historical_record_flagged_with_origins_and_ids_preserved(self):
        old=record()
        new=quarantine_historical_external_jobs([old],SOURCES)[0]
        self.assertEqual(old['status'],'unverified')
        for key in ('id','source_id','source_name','employer','url','apply_url','first_discovered_at','last_seen_at'):
            self.assertEqual(old[key],new[key])
        self.assertEqual(new['status'],'unverified')
        self.assertEqual(new['link_status'],'review-required')
        self.assertEqual(new['verification']['state'],'incomplete')
        self.assertEqual(new['ownership_risk']['observed_host'],'www.nationalevacaturebank.nl')
        self.assertIsNone(new['last_verified_at'])
        self.assertIn('individual evidence',new['review_note'])

    def test_closed_not_resurrected(self):
        old=record(status='closed')
        old['closure_reason']='Published application deadline has passed'
        new=quarantine_historical_external_jobs([old],SOURCES)[0]
        self.assertEqual(new['status'],'closed')
        self.assertEqual(new['closure_reason'],old['closure_reason'])
        self.assertEqual(new['verification'],old['verification'])
        self.assertEqual(new['ownership_risk']['original_source_id'],SOURCE_ID)

    def test_wrongly_open_legacy_record_is_not_published_as_verified(self):
        old=record(status='open',verification_state='verified')
        old['last_verified_at']='2026-11-16T18:00:00+00:00'
        new=quarantine_historical_external_jobs([old],SOURCES)[0]
        self.assertEqual(new['status'],'unverified')
        self.assertEqual(new['verification']['state'],'incomplete')
        self.assertIsNone(new['last_verified_at'])

    def test_official_reviewed_host_and_positive_transfer_are_untouched(self):
        official=record(url=OFFICIAL,id='official')
        positive=record(id='positive')
        positive['ownership_review']={'evidence_url':'https://tenant.recruitee.com/o/hr','reviewed_on':'2026-11-16'}
        transferred=record(id='transferred')
        transferred['source_id']='reviewed-recruitee'
        transferred['url']='https://tenant.recruitee.com/o/hr'
        transferred['apply_url']=transferred['url']
        for example in (official,positive,transferred):
            self.assertEqual(quarantine_historical_external_jobs([example],SOURCES),[example])

    def test_idempotent_repeat_and_no_unreviewed_host_changes(self):
        original=record()
        once=quarantine_historical_external_jobs([original],SOURCES)
        twice=quarantine_historical_external_jobs(once,SOURCES)
        self.assertEqual(once,twice)
        unrelated=record(id='source-other')
        unrelated['source_id']='unreviewed-other'
        self.assertEqual(quarantine_historical_external_jobs([unrelated],SOURCES),[unrelated])

    def test_real_registry_and_cumulative_finalize_preserve_existing_catalog(self):
        # Use current catalog records but no current live source. No network.
        registry=read(ROOT/'data/sources.json',[])
        prior=read(ROOT/'data/catalog.json',{})
        old_unverified=next(j for j in prior['jobs'] if j['source_id']==SOURCE_ID and j['status']=='unverified')
        old_closed=next(j for j in prior['jobs'] if j['source_id']==SOURCE_ID and j['status']=='closed')
        true_verified=next(j for j in prior['jobs'] if j['status']=='open' and j['source_id']!=SOURCE_ID
                          and j['verification']['state']=='verified')
        before=[copy.deepcopy(j) for j in [old_unverified,old_closed,true_verified]]
        with tempfile.TemporaryDirectory() as tmp:
            catalog,coverage=finalize(registry,[],dict(prior,jobs=before),{},[],
                                     '2026-11-16T18:55:00+00:00',Path(tmp))
        self.assertEqual({j['id'] for j in catalog['jobs']},{j['id'] for j in before})
        affected={j['id']:j for j in catalog['jobs']}
        self.assertEqual(affected[old_unverified['id']]['link_status'],'review-required')
        self.assertEqual(affected[old_closed['id']]['status'],'closed')
        self.assertEqual(affected[true_verified['id']]['verification']['state'],'verified')
        self.assertEqual(coverage['quality']['historical_unreviewed_external_records'],2)

if __name__=='__main__':
    unittest.main()
