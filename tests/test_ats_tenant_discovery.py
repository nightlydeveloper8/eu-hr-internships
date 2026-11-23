import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import Mock
from urllib.error import HTTPError

from scripts.ats_tenant_discovery import collect, identity, registry_keys, sample


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
            "https://acme.intervieweb.it/acme/it/career": ("inrecruiting", "acme.intervieweb.it"),
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

    def test_pages_and_failure_remain_distinct(self):
        client = Mock()
        capture = {"url": "https://acme.recruitee.com/o/test", "status": "200",
                   "timestamp": "20261101000000"}
        client.read.side_effect = [
            b'{"pages": 2}', json.dumps(capture).encode(),
            HTTPError("https://index.commoncrawl.org/", 504, "timeout", {}, None),
        ]
        seen, queries = collect(client, ["CC-MAIN-2026-43", "CC-MAIN-2026-39"], ["recruitee"], 1)
        self.assertEqual(len(seen), 1)
        self.assertEqual([query["status"] for query in queries], ["capped", "incomplete"])

    def test_sample_excludes_registered_and_is_order_independent(self):
        rows = [{"ats": "lever", "tenant": str(i), "registered": i == 300} for i in range(302)]
        result = sample(rows, "example")
        self.assertEqual(result, sample(reversed(rows), "example"))
        self.assertEqual(len(set(result["lever"])), 300)
        self.assertNotIn("300", result["lever"])


class YieldTest(unittest.TestCase):
    def test_costs_include_incomplete_reads_and_keep_geography_unknown(self):
        from scripts.ats_tenant_yield import summarize

        result = summarize([
            {"ats": "lever", "state": "incomplete", "logical_get": 2, "seconds": 10},
            {"ats": "lever", "state": "feed-read", "logical_get": 1,
             "body_bytes": 900, "seconds": 2, "postings": 3,
             "internships": [{"countries": ["sconosciuto"]}]},
        ])["lever"]
        self.assertEqual(result["feed_reads"], 1)
        self.assertEqual(result["stage_signals_by_country"], {"sconosciuto": 1})
        self.assertEqual(result["cost_per_stage_feed_signal"], {
            "logical_get": 3, "body_bytes": 900, "source_seconds": 12,
        })
