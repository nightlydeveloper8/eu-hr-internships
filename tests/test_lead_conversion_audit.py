"""Regression tests for the offline lead conversion audit; no network requests."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.lead_conversion_audit import analyze, family, reason_category  # noqa: E402


def job(id_, reason, *, status="unverified", kind="internship", source="employer-adecco-group"):
    return {
        "id": id_, "source_id": source, "source_type": "employer-sitemap",
        "country": "FR", "url": "https://careers.adeccogroup.com/en/job/a/1/2",
        "internship_type": kind, "status": status, "link_status": "incomplete",
        "verification": {"state": "incomplete", "reason": reason, "policy_version": 2},
    }


class AuditTest(unittest.TestCase):
    def setUp(self):
        self.sources = [{"id": "employer-adecco-group", "permission_basis": "Official Radancy careers site"}]
        self.coverage = {"sources": [{
            "id": "employer-adecco-group", "requests": 20,
            "bytes_read": 1200, "duration_seconds": 4.2, "status": "partial",
        }]}
        self.snapshot = "2026-11-21T07:35:04+00:00"

    def test_excludes_unowned_legacy_without_losing_its_id(self):
        from scripts.lead_conversion_audit import OWNERSHIP_HOLD
        records = [job("a", "No available vacancy-specific application entry established"),
                   job("b", OWNERSHIP_HOLD), job("c", "robots.txt unavailable: 403", kind="working-student")]
        result = analyze({"jobs": records, "updated_at": self.snapshot},
                         self.sources, self.coverage)
        self.assertEqual(result["totals"]["catalog_jobs"], 3)
        self.assertEqual(result["totals"]["actionable_leads"], 1)
        self.assertEqual(result["totals"]["legacy_ownership_holds"], 1)
        self.assertEqual(sum(row["count"] for row in result["reason_country_family"]), 1)
        self.assertEqual(result["source_run_costs"][0]["source_run_get_requests"], 20)

    def test_does_not_treat_expired_or_unproven_as_direct(self):
        recent = job("recent", "linked-same-vacancy-applicant-form", status="open")
        recent.update(link_status="verified", last_verified_at="2026-11-21T07:00:00+00:00",
                      verification={"state": "verified", "policy_version": 2},
                      application_verification={"method": "linked-same-vacancy-applicant-form"})
        stale = dict(recent, id="old", last_verified_at="2026-11-17T07:00:00+00:00")
        no_app = dict(recent, id="missing", application_verification=None)
        output = analyze({"jobs": [recent, stale, no_app], "updated_at": self.snapshot},
                         self.sources, self.coverage)
        self.assertEqual(output["totals"]["current_verified_internships"], 2)
        self.assertEqual(output["totals"]["direct_applications_verified"], 1)

    def test_platform_name_requires_reviewed_signal(self):
        source = self.sources[0]
        self.assertEqual(family(job("a", "x"), source), "Radancy (source reviewed)")
        self.assertEqual(family(job("a", "x"), {}), "employer-sitemap (ATS unconfirmed)")
        eures = job("e", "x", source="public-eu-eures")
        eures["source_type"] = "eures-search"
        self.assertEqual(family(eures), "EURES")
        self.assertEqual(reason_category(job("x", "robots.txt disallows https://blocked.example/x")),
                         "robots-disallowed")

    def test_current_catalog_has_exhaustive_nonpromoting_matrix(self):
        data = ROOT / "data"
        catalog = json.loads((data / "catalog.json").read_text(encoding="utf-8"))
        sources = json.loads((data / "sources.json").read_text(encoding="utf-8"))
        coverage = json.loads((data / "coverage.json").read_text(encoding="utf-8"))
        result = analyze(catalog, sources, coverage)
        self.assertEqual(result["totals"]["catalog_jobs"], len(catalog["jobs"]))
        self.assertEqual(result["totals"]["distinct_ids"], len({j["id"] for j in catalog["jobs"]}))
        self.assertEqual(sum(result["by_country"].values()), result["totals"]["actionable_leads"])
        self.assertEqual(sum(result["by_reason"].values()), result["totals"]["actionable_leads"])
        self.assertEqual(sum(cell["count"] for cell in result["reason_country_family"]),
                         result["totals"]["actionable_leads"])
        print("LEAD_AUDIT_CI", json.dumps({
            "baseline": result["totals"],
            "by_country": result["by_country"],
            "by_reason": result["by_reason"],
            "matrix_rows": len(result["reason_country_family"]),
        }, sort_keys=True))


if __name__ == "__main__":
    unittest.main()
