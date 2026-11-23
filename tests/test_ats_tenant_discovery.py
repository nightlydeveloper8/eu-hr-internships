import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import Mock

from scripts.ats_columnar_index import overlaps
from scripts.ats_tenant_discovery import enumerate_partitions, identity, prefixes, registry_keys, sample


class DiscoveryTest(unittest.TestCase):
    def test_provider_identity(self):
        examples = {
            "https://boards.greenhouse.io/Acme/jobs/42": ("greenhouse", "acme"),
            "https://job-boards.greenhouse.io/acme": ("greenhouse", "acme"),
            "https://boards.eu.greenhouse.io/acme": ("greenhouse", "eu/acme"),
            "https://jobs.eu.lever.co/acme/42": ("lever", "eu/acme"),
            "https://testco.jobs.personio.de/job/42": ("personio-xml", "testco.jobs.personio.de"),
            "https://testco.recruitee.com/o/role": ("recruitee", "testco.recruitee.com"),
            "https://testco.teamtailor.com/jobs/42": ("teamtailor", "testco.teamtailor.com"),
            "https://apply.workable.com/acme/j/42": ("workable", "acme"),
            "https://candidate.hr-manager.net/ApplicationInit.aspx?ProjectId=157629&cid=1601": ("talentech", "1601"),
            "https://acme.intervieweb.it/acme/it/career": ("inrecruiting", "acme.intervieweb.it/acme"),
            "https://www.welcometothejungle.com/fr/companies/acme/jobs/x": ("welcome-to-the-jungle", "acme"),
        }
        for url, result in examples.items():
            with self.subTest(url=url):
                self.assertEqual(identity(url), result)

    def test_non_tenants(self):
        for url in (
            "https://jobs.ashbyhq.com/acme", "https://jobs.smartrecruiters.com/acme",
            "https://portal.teamtailor.com.example.org/jobs/42",
            "https://www.recruitee.com/features", "https://jobs.lever.co/apply",
            "https://jobs.talentclue.com/42", "https://jobs.lever.co@bad.example/acme",
            "https://candidate.hr-manager.net/ApplicationInit.aspx?cid=1&cid=2",
        ):
            with self.subTest(url=url):
                self.assertIsNone(identity(url))

    def test_registry_checks_disabled_sources_and_company_urls(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "data").mkdir()
            (root / "data/companies.json").write_text(json.dumps([
                {"career_url": "https://jobs.lever.co/known"},
            ]))
            (root / "data/sources.json").write_text(json.dumps([
                {"adapter": "greenhouse", "board": "hidden", "enabled": False},
                {"adapter": "lever", "board": "known", "career_url": "https://jobs.eu.lever.co/known"},
            ]))
            self.assertEqual(registry_keys(root), {
                ("lever", "known"), ("lever", "eu/known"), ("greenhouse", "hidden"),
            })

    def test_surt_overlap_has_correct_boundaries(self):
        self.assertEqual(prefixes("greenhouse", "job-boards.greenhouse.io"),
                         ["io,greenhouse,job-boards)/"])
        self.assertEqual(prefixes("personio-xml", "jobs.personio.de"), ["de,personio,jobs,"])
        self.assertTrue(overlaps(("a", "de,personio,jobs,"), "de,personio,jobs,"))
        self.assertFalse(overlaps(("de,personio,jobs,\uffff", "z"), "de,personio,jobs,"))

    def test_scans_all_intersecting_files_and_reports_missing_metadata(self):
        client = Mock()
        client.urls.return_value = [("https://acme.recruitee.com/o/test", "acme.recruitee.com")]
        seen, queries = enumerate_partitions(client, {
            "first": [{"path": "left", "bounds": ["a", "com,recruitee,acme"]},
                      {"path": "right", "bounds": ["com,recruitee,acme", "z"]},
                      {"path": "missing", "error": "missing statistics"}],
            "second": [{"path": "all", "bounds": ["a", "z"]}],
        }, ["recruitee"])
        self.assertEqual(seen[("recruitee", "acme.recruitee.com")], {"first", "second"})
        self.assertEqual([(q["selected_ranges"], q["complete"]) for q in queries],
                         [(2, False), (1, True)])
        self.assertEqual(client.urls.call_count, 3)

    def test_sample_excludes_registered_and_is_order_independent(self):
        rows = [{"ats": "lever", "tenant": str(i), "registered": i == 300,
                 "crawls": ["a", "b"] if i < 6 else ["a"]} for i in range(302)]
        result = sample(rows, "example")
        self.assertEqual(result, sample(reversed(rows), "example"))
        tenants = {row["tenant"] for row in result["lever"]}
        self.assertEqual(len(tenants), 300)
        self.assertNotIn("300", tenants)
        self.assertEqual({row["stratum"] for row in result["lever"]}, {"one-crawl", "multiple-crawls"})


class YieldTest(unittest.TestCase):
    def test_costs_include_incomplete_reads_and_keep_geography_unknown(self):
        from scripts.ats_tenant_yield import summarize

        result = summarize([
            {"ats": "lever", "state": "incomplete", "stratum": "one-crawl", "population": 4,
             "logical_get": 2, "seconds": 10},
            {"ats": "lever", "state": "feed-read", "stratum": "one-crawl", "population": 4,
             "logical_get": 1,
             "body_bytes": 900, "seconds": 2, "postings": 3,
             "internships": [{"countries": ["sconosciuto"]}]},
        ])["lever"]
        self.assertEqual(result["feed_reads"], 1)
        self.assertEqual(result["stage_signals_by_country"], {"sconosciuto": 1})
        self.assertEqual(result["cost_per_stage_feed_signal"], {
            "logical_get": 3, "body_bytes": 900, "source_seconds": 12,
        })


    def test_uncertain_yield_and_operational_detection_are_distinct(self):
        from scripts.ats_tenant_yield import estimate, estimate_detectable_tenants

        rows = [{"stratum": "one-crawl", "population": 40, "state": "feed-read",
                 "internships": []} for _ in range(30)]
        self.assertEqual(estimate(rows), "non dimostrato")
        result = estimate_detectable_tenants(rows)
        self.assertEqual(result["tenant_detections"], 0)
        self.assertGreater(result["interval95"][1], 0)

    def test_measure_uses_posting_geography_and_feed_level_only(self):
        from scripts.ats_tenant_yield import measure

        known = {"external_id": "1", "title": "HR Intern", "text": "HR internship",
                 "location": "London, United Kingdom", "country": None}
        unknown = dict(known, external_id="2", location="Remote")
        outside = dict(known, external_id="3", location="London, Ontario", country="CA")
        with unittest.mock.patch("scripts.ats_tenant_yield.collect", return_value=[known, unknown, outside]):
            result = measure("lever", "sample", {"allowed_hosts": ["api.lever.co"]})
        self.assertEqual(result["european_postings"], 1)
        self.assertEqual(result["unknown_location"], 1)
        self.assertEqual(result["internships"], [
            {"external_id": "1", "countries": ["GB"], "proof": "feed-signal-only"},
        ])
