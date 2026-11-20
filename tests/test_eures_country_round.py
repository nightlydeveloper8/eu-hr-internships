"""Offline budget replay for the isolated EURES prototype."""
import unittest

from collector.runtime import CollectionBudgetExceeded
from scripts.pilot_eures_country_round import preview_inventory


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
