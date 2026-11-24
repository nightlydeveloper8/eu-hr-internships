"""Dutch agency sitemap routing and rollout hold."""
import json
import unittest
from unittest.mock import Mock

from collector.adapters import collect
from collector.daily import provision
from collector.employer_pages import dutch_agency_slug_candidate
from collector.pipeline import ROOT


class DutchAgencyTests(unittest.TestCase):
    def test_uses_only_the_vacancy_slug(self):
        self.assertTrue(dutch_agency_slug_candidate(
            "https://www.tempo-team.nl/vacatures/758734/stagiair%28e%29-hr-administratie"))
        self.assertTrue(dutch_agency_slug_candidate(
            "https://www.youngcapital.nl/vacatures/5437684-recruitment-stage-bij-youngcapital"))
        self.assertFalse(dutch_agency_slug_candidate(
            "https://www.randstad.nl/vacatures/123456/werkstudent-hr?filter=stage"))

    def test_disabled_sources_cannot_collect_and_provisioning_is_idempotent(self):
        companies, sources = [
            json.loads((ROOT / "data" / name).read_text())
            for name in ("companies.json", "sources.json")
        ]
        lot = [source for source in sources if source.get("collection_lot") == "AGENZIE-NL"]
        self.assertEqual(len(lot), 3)
        for source in lot:
            self.assertIs(source["enabled"], False)
            self.assertIs(source["collection_activation_hold"], True)
            client = Mock()
            with self.assertRaisesRegex(ValueError, "collection activation hold"):
                collect(dict(source, enabled=True), client)
            self.assertEqual(client.mock_calls, [])
        self.assertEqual(provision(companies, sources), (companies, sources))
