"""Offline budget replay for the isolated EURES prototype."""
import unittest

from collector.runtime import CollectionBudgetExceeded
from scripts.pilot_eures_country_round import TERMS, preview_inventory


class LimitedClient:
    def __init__(self, limit):
        self.max_requests = limit
        self.pages = []

    def post_json(self, url, payload):
        if len(self.pages) >= self.max_requests:
            raise CollectionBudgetExceeded("test budget")
        self.pages.append(payload)
        return {"jvs": []}


class CountryRoundTests(unittest.TestCase):
    def test_first_pages_and_global_tail_compete_for_one_budget(self):
        source = dict(id="public-eu-eures", target_countries=["PL", "NL"],
                      max_requests=330, queries=[], combined_queries=[])
        for cap, expected in [(1, [["nl"]]), (2, [["nl"], ["pl"]]), (3, [["nl"], ["pl"], []])]:
            with self.subTest(cap=cap):
                client = LimitedClient(cap)
                preview_inventory(source, client)
                self.assertEqual([p["locationCodes"] for p in client.pages], expected)

    def test_complete_market_round_keeps_global_tail_within_ordinary_budget(self):
        # Empty replay pages test allocation only. They do not estimate vacancy yield.
        source = dict(id="public-eu-eures", target_countries=list(TERMS), max_requests=330,
                      queries=[f"term {i}" for i in range(330)], combined_queries=[])
        client = LimitedClient(330)
        client.pages.append({"locationCodes": None})  # robots GET charged before the first search
        inventory = preview_inventory(source, client)
        self.assertEqual(len(client.pages), 330)
        locations = [p["locationCodes"] for p in client.pages[1:]]
        self.assertEqual(len({tuple(loc) for loc in locations if loc}), 28)
        self.assertTrue(all(locations[:28]))
        self.assertEqual(locations[28:], [[]] * 301)
        self.assertFalse(inventory.stats["closure_complete"])
