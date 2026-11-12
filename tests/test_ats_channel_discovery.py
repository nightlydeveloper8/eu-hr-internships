"""Offline regressions for employer-linked ATS candidate review."""
import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from collector.ats_channel_discovery import (
    identify_channel, same_official_page, safe_url, pilot
)


class ChannelPatternTests(unittest.TestCase):
    def test_providers_and_endpoint_hints_are_only_proposals(self):
        examples = [
            ("https://job-boards.greenhouse.io/test/jobs/123", "greenhouse:test"),
            ("https://jobs.eu.lever.co/test/123?utm_source=ad", "lever:test"),
            ("https://demo.jobs.personio.de/job/123", "personio-xml:demo.jobs.personio.de"),
            ("https://demo.recruitee.com/#jobs", "recruitee:demo.recruitee.com"),
        ]
        for url, key in examples:
            with self.subTest(url=url):
                self.assertEqual(identify_channel(url)["channel_key"], key)
                self.assertEqual(identify_channel(url)["gate"], "review-required")

    def test_blocked_and_unsupported_are_not_onboarding_grants(self):
        for url in ("https://jobs.ashbyhq.com/example", "https://jobs.smartrecruiters.com/company",
                    "https://example.teamtailor.com/jobs", "https://company.career.softgarden.de/"):
            with self.subTest(url=url):
                self.assertNotEqual(identify_channel(url)["gate"], "review-required")
        self.assertIsNone(identify_channel("https://app.recruitee.com/"))
        self.assertIsNone(identify_channel("https://www.teamtailor.com/?utm_source=careers"))
        self.assertIsNone(identify_channel("https://jobs.lever.co/"))

    def test_url_safety(self):
        for url in ("http://jobs.lever.co/company", "https://user:pass@jobs.lever.co/company",
                    "https://jobs.lever.co:443/company", "https://evil.example/greenhouse.io/company",
                    "https://jobs.lever.co/company\nX", "https://jobs.lever.co\\@evil.test/company"):
            with self.subTest(url=url):
                self.assertIsNone(identify_channel(url))
        self.assertTrue(same_official_page("https://a.test/jobs/#x", "https://a.test/jobs/"))
        self.assertFalse(same_official_page("https://other.test/jobs", "https://a.test/jobs"))


class CandidatePilotTests(unittest.TestCase):
    def setUp(self):
        self.companies = [
            dict(id="de", name="Employer DE", career_url="https://de.example/careers",
                 source_ids=["auto-de"], target_countries=["DE"]),
            dict(id="fr", name="Employer FR", career_url="https://fr.example/jobs",
                 source_ids=["auto-fr", "recruitee-fr"], target_countries=["FR"]),
            dict(id="be", name="Employer BE", career_url="https://be.example/work",
                 source_ids=["auto-be"], target_countries=["BE"]),
            dict(id="ie", name="Employer IE", career_url="https://ie.example/careers",
                 source_ids=["auto-ie"], target_countries=["IE"]),
        ]
        self.sources = [dict(id="recruitee-fr", adapter="recruitee",
            feed_url="https://france.recruitee.com/api/offers/", enabled=True)]
        self.scans = [
            dict(company_id="de", url="https://de.example/careers",
                 final_url="https://de.example/careers", status="reviewed",
                 ats_links=["https://deco.jobs.personio.de/job/123",
                            "https://deco.jobs.personio.de/job/456?language=de"]),
            dict(company_id="fr", url="https://fr.example/jobs",
                 final_url="https://fr.example/jobs", status="reviewed",
                 ats_links=["https://france.recruitee.com/", "https://france.recruitee.com/#jobs"]),
            dict(company_id="be", url="https://be.example/work",
                 final_url="https://be.example/work", status="reviewed",
                 ats_links=["https://jobs.lever.co/belgian/0001"]),
            dict(company_id="ie", url="https://ie.example/careers",
                 final_url="https://ie.example/careers", status="reviewed",
                 ats_links=["https://job-boards.greenhouse.io/irish/jobs/987"]),
        ]

    def test_four_country_sample_deduplicates_and_keeps_gates(self):
        result = pilot(self.companies, self.sources, self.scans, per_country=6)
        self.assertEqual(len(result["proposals"]), 4)
        self.assertEqual(len(result["countries"]), 4)
        status = {r["company_id"]: r["status"] for r in result["proposals"]}
        self.assertEqual(status["fr"], "already-registered")
        self.assertEqual(status["de"], "requires-access-and-identity-review")
        self.assertEqual(status["be"], "requires-access-and-identity-review")
        self.assertEqual(status["ie"], "requires-access-and-identity-review")
        de = next(p for p in result["proposals"] if p["company_id"] == "de")
        self.assertEqual(len(de["observed_links"]), 2)
        for record in result["proposals"]:
            self.assertFalse(record["enabled"])
            self.assertEqual(record["robots"], "not-rechecked-offline")
            self.assertEqual(record["hosts"], "not-authorized-by-discovery")
            self.assertEqual(record["verified_vacancies_added"], 0)
        self.assertEqual(result["new_verified_internships"], 0)
        self.assertEqual(result["additional_http_requests"], 0)
        self.assertEqual(result["additional_browser_renders"], 0)

    def test_unofficial_page_redirect_and_unreviewed_evidence_fail_closed(self):
        self.scans.extend([
            dict(company_id="de", url="https://attacker.example/careers",
                 final_url="https://attacker.example/careers", status="reviewed",
                 ats_links=["https://jobs.lever.co/bad"]),
            dict(company_id="de", url="https://de.example/careers",
                 final_url="https://attacker.example/other", status="reviewed",
                 ats_links=["https://jobs.lever.co/bad"]),
            dict(company_id="de", url="https://de.example/careers",
                 final_url="https://de.example/careers", status="blocked",
                 ats_links=["https://jobs.lever.co/bad"]),
        ])
        result = pilot(self.companies, self.sources, self.scans)
        self.assertFalse(any(r["tenant"] == "bad" for r in result["proposals"]))

    def test_shared_tenant_is_not_assigned_to_another_employer(self):
        self.scans[0]["ats_links"] = ["https://france.recruitee.com/jobs/abc"]
        result = pilot(self.companies, self.sources, self.scans)
        de = next(r for r in result["proposals"] if r["company_id"] == "de")
        self.assertEqual(de["status"], "ownership-review")
        self.assertEqual(de["registry_source_ids"], ["recruitee-fr"])

    def test_two_repeat_discovery_cycles_do_not_modify_registry_or_catalog(self):
        original_companies = copy.deepcopy(self.companies)
        original_sources = copy.deepcopy(self.sources)
        original_scans = copy.deepcopy(self.scans)
        historical_catalog = {"jobs": [{"id": "unchanged", "status": "open",
            "verification": {"policy_version": 2, "state": "verified"}}]}
        initial_catalog = copy.deepcopy(historical_catalog)
        with patch("urllib.request.urlopen", side_effect=AssertionError("unexpected network")):
            first = pilot(self.companies, self.sources, self.scans)
            second = pilot(self.companies, self.sources, self.scans)
        self.assertEqual(first, second)
        self.assertEqual(self.companies, original_companies)
        self.assertEqual(self.sources, original_sources)
        self.assertEqual(self.scans, original_scans)
        self.assertEqual(historical_catalog, initial_catalog)

    def test_real_historical_scan_is_read_only(self):
        root = Path(__file__).resolve().parents[1]
        companies = json.loads((root / "data/companies.json").read_text())
        sources = json.loads((root / "data/sources.json").read_text())
        scans = json.loads((root / "docs/career-channel-scan.json").read_text())
        result = pilot(companies, sources, scans, per_country=6)
        self.assertEqual([c["country"] for c in result["countries"]], ["DE", "FR", "BE", "IE"])
        self.assertEqual(result["newly_enabled_sources"], 0)
        self.assertTrue(all(not row["enabled"] for row in result["proposals"]))


if __name__ == "__main__":
    unittest.main()
