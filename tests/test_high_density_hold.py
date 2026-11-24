"""Provisioning guards and shared pacing for reviewed Italian agencies."""
import json
import unittest
from unittest.mock import Mock, patch

from collector.adapters import collect
from collector.daily import provision, shard_for, shared_collection_hosts, source_shard
from collector.pipeline import ROOT
from collector.runtime import BudgetClient


class HighDensityHoldTests(unittest.TestCase):
    def test_held_channel_cannot_be_collected(self):
        companies = json.loads((ROOT / "data/companies.json").read_text())
        sources = json.loads((ROOT / "data/sources.json").read_text())
        source = next(s for s in sources if s["id"] == "held-randstad-it-jobposting")
        company = next(c for c in companies if c["id"] == source["company_id"])

        self.assertIn(source["id"], company["source_ids"])
        _, result = provision(companies, sources)
        self.assertEqual(result, sources)
        self.assertTrue(next(s for s in result if s["id"] == "auto-randstad-italia-spa")["enabled"])

        client = Mock()
        with self.assertRaisesRegex(ValueError, "collection activation hold"):
            collect(dict(source, enabled=True, collection_activation_hold=True), client)
        self.assertEqual(client.mock_calls, [])

    def test_it_lot_provisioning_is_idempotent_after_activation_and_rollback(self):
        companies = json.loads((ROOT / "data/companies.json").read_text())
        sources = json.loads((ROOT / "data/sources.json").read_text())
        lot = [s for s in sources if s.get("collection_lot") == "IT-agenzie"]
        self.assertEqual({s["id"] for s in lot},
                         {"held-randstad-it-jobposting", "held-synergie-it-jobposting",
                          "held-gi-group-it-jobposting", "held-adecco-it-jobposting"})
        self.assertEqual(provision(companies, sources), (companies, sources))
        for source in lot:
            source.update(enabled=False, collection_activation_hold=True)
        self.assertEqual(provision(companies, sources), (companies, sources))

    def test_gi_group_channels_share_shard_and_minimum_delay(self):
        sources = json.loads((ROOT / "data/sources.json").read_text())
        existing = next(s for s in sources if s["id"] == "auto-gi-group")
        reviewed = next(s for s in sources if s["id"] == "held-gi-group-it-jobposting")
        self.assertEqual(reviewed["agency_details_per_cycle"], 15)
        hosts = shared_collection_hosts([existing, reviewed])
        self.assertEqual(source_shard(reviewed, 16, hosts), shard_for(existing["id"], 16))
        self.assertEqual(source_shard(existing, 16, hosts), shard_for(existing["id"], 16))

        self.assertEqual(source_shard(reviewed,16,hosts,{"www.gigroup.it"}),16)
        self.assertEqual(source_shard(existing,16,hosts,{"www.gigroup.it"}),16)

        host = "www.gigroup.it"
        url = "https://" + host
        with patch.dict("collector.runtime._DELAYS", {}, clear=True), patch.dict(
            "collector.runtime._ROBOTS", {}, clear=True
        ):
            BudgetClient.set_host_delays({host: hosts[host][1]})
            client = BudgetClient()
            with patch.object(client, "request", return_value=(b"User-agent: *\nCrawl-delay: 5", 200, url)):
                self.assertTrue(client.permitted(url))
            self.assertEqual(client.host_delays[host], 120)
