"""EU discovery from official directory snapshots: offline safety and replay."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from collector.eu_directory_discovery import (
    safe_https_url, SeedClient, DiscoveryAccessError, build_discovery_queue,
    extract_directory_rows, fetch_reviewed_seed
)


class DiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.seeds = [
            dict(id="official-be", country="BE", url="https://career.uni.example/be",
                 parser="employer-card", card_class="employer", access_reviewed=False),
            dict(id="official-ie", country="IE", url="https://career.other.example/ie",
                 parser="employer-card", card_class="employer", access_reviewed=False)]
        self.companies = [dict(id="known", name="Known employer",
            website_url="https://known.example/", career_url=None, aliases=[])]
        self.be = '<a class="employer" href="https://newco.example/careers">New Co</a>' \
                  '<a class="employer" href="https://known.example/">Known employer</a>' \
                  '<a class="nav" href="https://unrelated.example/">Unrelated</a>' \
                  '<a class="employer" href="https://newco.example/jobs">New Co</a>'
        self.ie = '<a class="employer" href="https://newco.example/about">New Co</a>' \
                  '<a class="employer" href="https://irish.example/">Irish Group</a>'
        self.snapshots = {
            "official-be": dict(html=self.be, final_url=self.seeds[0]["url"],
                                observed_at="2026-11-12T10:00:00Z", requests=0),
            "official-ie": dict(html=self.ie, final_url=self.seeds[1]["url"],
                                observed_at="2026-11-12T11:00:00Z", requests=0)}

    def test_two_country_new_employers_dedupe_and_provenance(self):
        result = build_discovery_queue(self.seeds, self.snapshots, self.companies)
        self.assertEqual(result["pending_candidate_count"], 2)
        self.assertEqual({r["name"] for r in result["candidates"]},
                         {"New Co", "Irish Group"})
        new = next(r for r in result["candidates"] if r["name"] == "New Co")
        self.assertEqual(new["candidate_country_scopes"], ["BE", "IE"])
        self.assertEqual(new["first_observed_at"], "2026-11-12T10:00:00Z")
        self.assertEqual(new["last_observed_at"], "2026-11-12T11:00:00Z")
        self.assertEqual(len(new["evidence_urls"]), 2)
        self.assertEqual(new["status"], "identity-and-host-review-required")
        self.assertEqual(result["enabled_ats_sources"], 0)
        self.assertEqual(result["added_verified_hr_internships"], 0)

    def test_repeat_cycles_and_missing_source_preserve_history_and_catalog(self):
        originals = (copy.deepcopy(self.seeds), copy.deepcopy(self.snapshots),
                     copy.deepcopy(self.companies))
        catalog = dict(jobs=[dict(id="original", status="open",
                                 verification=dict(state="verified", policy_version=2))])
        old = copy.deepcopy(catalog)
        first = build_discovery_queue(self.seeds, self.snapshots, self.companies)
        second = build_discovery_queue(self.seeds, self.snapshots, self.companies, previous=first)
        third = build_discovery_queue(self.seeds, {}, self.companies, previous=second)
        self.assertEqual(first["candidates"], second["candidates"])
        self.assertEqual(second["candidates"], third["candidates"])
        self.assertEqual((self.seeds, self.snapshots, self.companies), originals)
        self.assertEqual(catalog, old)

    def test_cross_host_redirect_and_bad_candidate_links_fail_closed(self):
        self.snapshots["official-be"]["final_url"] = "https://untrusted.example"
        with self.assertRaises(DiscoveryAccessError):
            build_discovery_queue(self.seeds, self.snapshots, self.companies)
        self.snapshots["official-be"]["final_url"] = self.seeds[0]["url"]
        self.snapshots["official-be"]["html"] += (
            '<a class="employer" href="http://bad.example">Bad</a>'
            '<a class="employer" href="https://name:password@bad.example/">Bad</a>'
            '<a class="employer" href="https://127.0.0.1/">Bad</a>')
        result = build_discovery_queue(self.seeds, self.snapshots, self.companies)
        self.assertEqual(result["pending_candidate_count"], 2)

    def test_no_unreviewed_live_requests(self):
        with patch.object(SeedClient, "request", side_effect=AssertionError("network")):
            with self.assertRaises(DiscoveryAccessError):
                fetch_reviewed_seed(self.seeds[0])
        live_seed = dict(self.seeds[0], access_reviewed=True)
        client = SeedClient(live_seed)
        for url in ("https://untrusted.example/", "http://career.uni.example/be",
                    "https://127.0.0.1/", "https://career.uni.example:443/be"):
            with self.subTest(url=url):
                with self.assertRaises(DiscoveryAccessError):
                    client.request(url)
        with self.assertRaises(DiscoveryAccessError):
            client.request(self.seeds[0]["url"], method="POST")
        with self.assertRaises(DiscoveryAccessError):
            client.request(self.seeds[0]["url"], robots=False)

    def test_offline_budget_and_empty_non_authorized_seed(self):
        with self.assertRaises(ValueError):
            build_discovery_queue(self.seeds, self.snapshots, self.companies, per_seed=0)
        with self.assertRaises(ValueError):
            build_discovery_queue(self.seeds, {**self.snapshots,
                "official-be": dict(self.snapshots["official-be"], html="x"*1_000_001)},
                self.companies)
        report = build_discovery_queue(self.seeds, {}, self.companies)
        self.assertEqual(report["pending_candidate_count"], 0)
        self.assertEqual(report["requests"], 0)
        self.assertEqual(report["source_metrics"][0]["status"], "no-new-observation")

    def test_existing_university_parsers_remain_reused(self):
        seed = dict(id="ikom-test", country="DE",
            url="https://ikom-tum.de/de/messen/ikom/2026",
            parser="ikom", access_reviewed=False)
        # Empty fixture must not invent employer identities.
        self.assertEqual(extract_directory_rows(seed, "<html><body>No exhibitors</body></html>"), [])

    def test_live_seeds_default_disabled_in_repository(self):
        path = Path(__file__).resolve().parents[1]/"data/eu-discovery-seeds.json"
        data = json.loads(path.read_text())
        self.assertEqual([x["country"] for x in data["seeds"]], ["DE", "FR"])
        self.assertTrue(all(not x["access_reviewed"] for x in data["seeds"]))
        self.assertEqual([x["country"] for x in data["pilot_research_candidates"]],
                         ["BE", "IE"])


if __name__ == "__main__":
    unittest.main()
