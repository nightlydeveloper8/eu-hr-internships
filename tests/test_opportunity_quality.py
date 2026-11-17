"""No-network tests for daily policy-v2 proof-gap triage."""
import unittest

from scripts.opportunity_quality import analyze, reason_kind
from collector.pipeline import read, ROOT

STAMP = "2026-11-17T08:07:40+00:00"


def job(id, reason, **kw):
    o=dict(id=id,source_id="reviewed-one",employer="Reviewed Employer",
           title="HR Internship",url="https://careers.example/jobs/"+id,
           country="SE",countries=["SE"],internship_type="internship",
           status="unverified",link_status="incomplete",
           verification=dict(state="incomplete",policy_version=2,
                             reason=reason,checked_at=STAMP),
           last_verified_at=STAMP,last_seen_at=STAMP)
    o.update(kw)
    return o


class OpportunityBacklogTests(unittest.TestCase):
    def test_no_proof_is_not_a_verified_vacancy(self):
        rows=[
            job("one","No available vacancy-specific application entry established"),
            job("two","Application link lacks a matching vacancy identifier"),
            job("three","robots.txt unavailable: 403"),
            job("four","Historical external URL outside source reviewed employer hosts"),
            job("five","Application page does not identify the same vacancy"),
            job("six","linked-same-vacancy-applicant-form",
                status="open",link_status="verified",
                verification=dict(state="verified",policy_version=2,reason="linked",checked_at=STAMP)),
            job("seven","Official application closed",status="closed"),
        ]
        sources=[dict(id="reviewed-one",employer="Reviewed Employer",
                      enabled=True,allowed_hosts=["careers.example"])]
        coverage=dict(sources=[dict(id="reviewed-one",status="partial",
                                    checked_at=STAMP,requests=10,bytes_read=1200)])
        r=analyze(dict(updated_at=STAMP,jobs=rows,countries={"SE":"Sweden","IT":"Italy"}),
                  sources,coverage)
        self.assertEqual(r["fresh_verified_hr_internships"],1)
        self.assertEqual(r["unverified_records"],5)
        self.assertEqual(r["status_counts"]["application-proof-gap"],3)
        self.assertEqual(r["excluded_quarantined_or_blocked"],2)
        self.assertEqual(r["ranked_source_count"],1)
        self.assertEqual(r["ranked_sources"][0]["current_unverified_distinct_ids"],3)
        self.assertEqual(r["countries_without_verified_hr_internships"],["IT"])
        self.assertEqual(r["ranked_sources"][0]["last_source_requests"],10)
        self.assertEqual(r["ranked_sources"][0]["stored_reasons_not_fresh"],0)

    def test_stale_old_error_is_not_new_live_evidence(self):
        source=dict(id="reviewed-one",enabled=True,allowed_hosts=["careers.example"])
        row=job("x","No available vacancy-specific application entry established")
        row["verification"]["checked_at"]="2026-11-14T00:00:00+00:00"
        r=analyze(dict(updated_at=STAMP,jobs=[row],countries={"SE":"Sweden"}),
                  [source],dict(sources=[dict(id="reviewed-one",checked_at=STAMP,requests=2)]))
        self.assertEqual(r["ranked_sources"][0]["stored_reasons_not_fresh"],1)
        self.assertFalse(r["ranked_sources"][0]["representative_ids"][0]["fresh_evidence"])

    def test_unapproved_hosts_and_disabled_source_cannot_be_auto_prioritized(self):
        row=job("x","No available vacancy-specific application entry established")
        initial=dict(updated_at=STAMP,jobs=[row],countries={"SE":"Sweden"})
        self.assertEqual(analyze(initial,[],{} )["ranked_source_count"],0)
        source=dict(id="reviewed-one",enabled=True,allowed_hosts=["different.example"])
        r=analyze(initial,[source],{})
        self.assertEqual(r["ranked_source_count"],0)
        self.assertEqual(r["status_counts"]["unapproved_source_host"],1)

    def test_many_working_students_cannot_outrank_single_hr_internship(self):
        reason="No available vacancy-specific application entry established"
        students=[job("ws-"+str(i),reason,source_id="working-only",
                      internship_type="working-student") for i in range(12)]
        internship=job("hr-intern",reason,source_id="internship-one")
        sources=[dict(id=sid,enabled=True,allowed_hosts=["careers.example"])
                 for sid in ("working-only","internship-one")]
        report=analyze(dict(updated_at=STAMP,jobs=students+[internship],
                            countries={"SE":"Sweden"}),sources,{},limit=5)
        self.assertEqual(report["unverified_records"],13)
        self.assertEqual(report["unverified_hr_internship_records"],1)
        self.assertEqual(report["unverified_working_student_records"],12)
        self.assertEqual(report["ranked_internship_source_count"],1)
        self.assertEqual(report["ranked_sources"][0]["source_id"],"internship-one")
        self.assertEqual(report["ranked_sources"][0]["current_unverified_hr_internships"],1)
        self.assertEqual(report["ranked_sources"][1]["current_unverified_hr_internships"],0)
        self.assertEqual(report["ranked_sources"][1]["current_unverified_working_students"],12)
        self.assertEqual(report["ranked_sources"][1]["score_heuristic_not_success_probability"],0)
        self.assertEqual(report["ranked_sources"][0]["representative_ids"][0]["opportunity_type"],"internship")

    def test_invalid_catalog_timestamp_never_claims_success(self):
        with self.assertRaises(ValueError):
            analyze(dict(jobs=[]),[],{})

    def test_real_catalog_analyzes_without_mutation_or_http(self):
        catalog=read(ROOT/"data/catalog.json",{})
        sources=read(ROOT/"data/sources.json",[])
        coverage=read(ROOT/"data/coverage.json",{})
        before=len(catalog["jobs"])
        report=analyze(catalog,sources,coverage)
        self.assertEqual(len(catalog["jobs"]),before)
        self.assertEqual(report["total_catalog_records"],before)
        self.assertGreaterEqual(report["fresh_verified_hr_internships"],0)
        self.assertLessEqual(report["fresh_verified_hr_internships"],before)
        self.assertLessEqual(report["ranked_source_count"],before)
        self.assertLessEqual(len(report["ranked_sources"]),25)


if __name__=="__main__":
    unittest.main()
