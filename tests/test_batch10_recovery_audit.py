"""Offline EU27 batch10 audit: risk segmentation not fake vacancy recovery."""
import unittest
from scripts.audit_batch10_recovery import audit, cause, ownership_risk

STAMP="2026-11-16T18:00:00+00:00"
SOURCES=[
 {'id':'til','ownership_scope':'reviewed-hosts','require_employer_identity':True,
  'allowed_hosts':['www.tilburguniversity.edu']},
 {'id':'employer','ownership_scope':'reviewed-hosts','allowed_hosts':['jobs.employer.nl']}
]
def job(jid,source='employer',country='NL',status='unverified',
        url='https://jobs.employer.nl/job/hr-intern',reason='No available vacancy-specific application entry established',
        kind='internship',verified=False,ownership_review=None):
    v=dict(id=jid,source_id=source,country=country,url=url,status=status,
        link_status='verified' if verified else 'incomplete',internship_type=kind,
        verification={'policy_version':2,'state':'verified' if verified else 'incomplete','checked_at':STAMP,'reason':reason},
        last_verified_at=STAMP if verified else None)
    if ownership_review:v['ownership_review']=ownership_review
    return v

class RecoveryAuditTests(unittest.TestCase):
    def test_recovery_queue_separates_unsupported_referrals_from_official_jobs(self):
        unowned='https://www.nationalevacaturebank.nl/vacature/hr-stage'
        jobs=[
            job('1',source='til',url=unowned),
            job('2',source='til',status='closed',url=unowned),
            job('3',reason='Application link lacks a matching vacancy identifier'),
            job('4',status='open',verified=True),
            job('5',country='FR',reason='No available vacancy-specific application entry established'),
            job('6',country='BE',source='til',url=unowned,
                ownership_review={'evidence_url':'https://employer.example/hr'}),
            job('7',country='PT',status='open',verified=True),
            job('8',country='ES',reason='robots.txt unavailable: 403')
        ]
        catalog={'updated_at':STAMP,'jobs':jobs}
        result=audit(catalog,SOURCES)
        self.assertEqual(result['totals']['total'],8)
        self.assertEqual(result['totals']['unverified'],5)
        self.assertEqual(result['totals']['unreviewed_external_source_total'],2)
        self.assertEqual(result['totals']['unreviewed_external_unverified'],1)
        self.assertEqual(result['totals']['eligible_for_evidence_review'],4)
        self.assertEqual(result['totals']['verified_internship'],2)
        self.assertEqual(result['historical_unreviewed_sources'],{'til':2})
        self.assertEqual({x['cause']:x['count'] for x in result['priority_causes']},
                         {'no-observed-application-entry':2,
                          'application-requisition-identity':1,'access-or-network':1})
        self.assertEqual(result['countries'][0]['country'],'NL')

    def test_reviewed_host_is_not_blanket_approval_of_external_provider(self):
        j=job('no',source='til',url='https://jobs.other.com/job/12')
        self.assertTrue(ownership_risk(j,SOURCES[0]))
        j['ownership_review']={'reviewed_on':'2026-11-16'}
        self.assertFalse(ownership_risk(j,SOURCES[0]))
        official=job('ok',source='til',url='https://www.tilburguniversity.edu/jobs/12')
        self.assertFalse(ownership_risk(official,SOURCES[0]))
        self.assertFalse(ownership_risk(j,None))

    def test_stale_or_legacy_verification_is_never_fresh_verified(self):
        old=job('old',status='open',verified=True)
        old['last_verified_at']='2026-11-01T08:00:00+00:00'
        legacy=job('legacy',status='open',verified=True)
        legacy['verification']['policy_version']=1
        result=audit({'updated_at':STAMP,'jobs':[old,legacy]},SOURCES)
        self.assertNotIn('verified_internship',result['totals'])

    def test_duplicate_ids_fail_closed(self):
        one=job('duplicate')
        with self.assertRaisesRegex(ValueError,"Duplicate catalog job ID"):
            audit({'updated_at':STAMP,'jobs':[one,dict(one)]},SOURCES)

    def test_audit_is_pure_and_does_not_fabricate_new_status(self):
        records=[job('1',source='til',url='https://www.nationalevacaturebank.nl/stage')]
        snapshot=repr(records)
        _=audit({'updated_at':STAMP,'jobs':records},SOURCES)
        self.assertEqual(repr(records),snapshot)
        self.assertEqual(records[0]['status'],'unverified')

if __name__=="__main__":
    unittest.main()
