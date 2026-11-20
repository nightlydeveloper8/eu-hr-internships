"""Offline coverage, no website requests or source/config mutations."""
import unittest
from scripts.official_ats_country_queue import ats_hint, build_report, safe_https


def job(id, country, status="unverified", **more):
    return dict(id=id, country=country, countries=[country], status=status,
                internship_type="internship", title="HR Intern",
                employer="Employer", source_id="employer-one",
                source_type="employer-index",
                url="https://careers.example.com/jobs/" + id, **more)


class CountryQueueTests(unittest.TestCase):
    def test_exact_url_shapes_are_hints_not_verified_evidence(self):
        examples = [
            ("https://jobs.smartrecruiters.com/Averna1/744000152889189", ("smartrecruiters", "744000152889189")),
            ("https://suzuki.varbi.com/se/what:job/jobID:989715/type:job", ("varbi", "989715")),
            ("https://jobs.ashbyhq.com/rohlik/5de1a048-53ed-4b3a-9877-62d463b57ba0", ("ashby", "5de1a048-53ed-4b3a-9877-62d463b57ba0")),
            ("https://jobb.jobandtalent.com/jobs/8503489-role/applications/new", ("ats-same-id-path-review-required", "8503489")),
            ("https://amazon.jobs/en/jobs/10561439/role", ("amazon-jobs", "10561439")),
            ("https://manifesto.careers-page.com/jobs/1e8e178e-3cb5-40d7-993b-517ec3ae1c54", ("careers-page", "1e8e178e-3cb5-40d7-993b-517ec3ae1c54")),
        ]
        for uri, expected in examples:
            with self.subTest(uri=uri):
                self.assertEqual(ats_hint(uri), expected)
        for uri in ("http://jobs.smartrecruiters.com/Company/744000152889189",
                    "https://evil.example/Company/744000152889189",
                    "https://user:password@jobs.smartrecruiters.com/Company/744000152889189",
                    "https://jobs.smartrecruiters.com:444/Company/744000152889189"):
            self.assertNotEqual(ats_hint(uri)[0], "smartrecruiters")

    def test_zero_markets_and_duplicate_urls_never_invent_applications(self):
        direct = job("verified", "PL", status="open", last_verified_at="2026-11-20T10:00:00+00:00",
                     link_status="verified", verification=dict(state="verified", policy_version=2),
                     application_verification=dict(url="https://apply.example.com/job/verified"))
        unverified = job("other", "PL", external_application_url="https://jobs.smartrecruiters.com/Averna1/744000152889189")
        mirror = job("same", "PL", external_application_url="https://jobs.smartrecruiters.com/Averna1/744000152889189")
        closed = job("closed", "CZ", status="closed")
        risky = job("risky", "CZ", ownership_risk={"state": "unreviewed"})
        data = dict(updated_at="2026-11-20T11:00:00+00:00",
                    jobs=[direct, unverified, mirror, closed, risky])
        result = build_report(data, ["PL", "IE", "CZ"])
        self.assertEqual([x["country"] for x in result["countries"]], ["PL", "IE", "CZ"])
        pl, ie, cz = result["countries"]
        self.assertEqual(pl["policy_v2_direct_verified"], 1)
        self.assertEqual(pl["research_candidates"], 1)
        self.assertEqual(pl["candidates_shown"][0]["state"],
                         "research-only-not-a-verified-application")
        self.assertEqual(ie["research_candidates"], 0)
        self.assertEqual(cz["research_candidates"], 0)
        self.assertEqual(result["requests"], 0)
        self.assertEqual(result["renderings"], 0)

    def test_public_candidate_with_exact_ats_id_still_requires_ownership(self):
        lead = job("sw", "SE", status="open", source_id="public-se-jobtech",
                   source_type="jobtech-search",
                   external_application_url="https://jobb.jobandtalent.com/jobs/8503489-role/applications/new")
        report = build_report(dict(updated_at="2026-11-20T10:00:00+00:00", jobs=[lead]), ["SE"])
        row = report["countries"][0]["candidates_shown"][0]
        self.assertTrue(row["public_source"])
        self.assertEqual(row["observed_posting_id"], "8503489")
        self.assertEqual(report["countries"][0]["policy_v2_direct_verified"], 0)
        self.assertIn("not-a-verified", row["state"])

    def test_rejects_malformed_inputs(self):
        for bad in (None, [], {"jobs": "not-an-array"}, {}):
            with self.assertRaises(ValueError):
                build_report(bad)
        with self.assertRaises(ValueError):
            build_report({"jobs": []}, countries=["ZZZ"])
        with self.assertRaises(ValueError):
            build_report({"jobs": []}, per_country=0)


if __name__ == "__main__":
    unittest.main()
