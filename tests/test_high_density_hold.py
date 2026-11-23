"""The reviewed Randstad channel cannot trigger collection while on hold."""
import json
import unittest
from unittest.mock import Mock

from collector.adapters import collect
from collector.daily import provision
from collector.pipeline import ROOT


class HighDensityHoldTests(unittest.TestCase):
    def test_prepared_channel_cannot_activate_during_provisioning(self):
        companies = json.loads((ROOT / "data/companies.json").read_text())
        sources = json.loads((ROOT / "data/sources.json").read_text())
        source = next(s for s in sources if s["id"] == "held-randstad-it-jobposting")
        company = next(c for c in companies if c["id"] == source["company_id"])

        self.assertIn(source["id"], company["source_ids"])
        self.assertIs(source["enabled"], False)
        self.assertIs(source["collection_activation_hold"], True)
        _, result = provision(companies, sources)
        self.assertEqual(result, sources)
        self.assertTrue(next(s for s in result if s["id"] == "auto-randstad-italia-spa")["enabled"])

        client = Mock()
        with self.assertRaisesRegex(ValueError, "collection activation hold"):
            collect(dict(source, enabled=True), client)
        self.assertEqual(client.mock_calls, [])

    def test_entire_it_lot_is_held_and_provisioning_is_idempotent(self):
        companies = json.loads((ROOT / "data/companies.json").read_text())
        sources = json.loads((ROOT / "data/sources.json").read_text())
        lot = [s for s in sources if s.get("collection_lot") == "IT-agenzie"]
        self.assertEqual({s["id"] for s in lot},
                         {"held-randstad-it-jobposting", "held-synergie-it-jobposting",
                          "held-gi-group-it-jobposting", "held-adecco-it-jobposting"})
        self.assertTrue(all(s["enabled"] is False and s["collection_activation_hold"] is True for s in lot))
        self.assertEqual(provision(companies, sources), (companies, sources))
