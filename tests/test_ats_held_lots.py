"""Offline non-activation and batch planning regression coverage."""
from collections import Counter
from datetime import datetime, timezone
import json
import unittest

from collector.daily import provision
from scripts.ats_held_census import BoardClient, RequestBudget, summarize_records
from scripts.prepare_ats_held_lots import PREFIX, ROOT, prepare, simulate_selection


STAMP = "2026-11-23T18:00:00+00:00"


def sample(tenant, **fields):
    return dict({"ats": "personio-xml", "tenant": f"{tenant}.jobs.personio.de",
                 "state": "feed-read", "european_postings": 2, "countries": ["DE"],
                 "signals": [], "observed_at": STAMP}, **fields)


class HeldLotsTest(unittest.TestCase):
    def test_country_and_signal_classification(self):
        records = [
            {"external_id": "a", "title": "HR Intern", "text": "HR internship for students",
             "location": "Amsterdam, Netherlands"},
            {"external_id": "b", "title": "HR Intern", "location": "London, Ontario", "country": "CA"},
            {"external_id": "c", "title": "HR Werkstudent", "location": "Berlin, Germany"},
        ]
        row = summarize_records(records)
        self.assertEqual(row["european_postings"], 2)
        self.assertEqual(row["countries"], ["DE", "NL"])
        self.assertEqual(row["signals"], [{"id": "a", "countries": ["NL"]}])

    def test_held_lots_are_stable_and_never_provision_a_fallback(self):
        observations = [sample(f"board-{i}") for i in range(501)]
        observations.append(sample("blocked", state="incomplete"))
        companies, sources, _ = prepare([], [], observations)
        self.assertEqual(len(companies), 501)
        self.assertEqual({s["rollout_batch_id"] for s in sources}, {"ats-2026-11-01", "ats-2026-11-02"})
        self.assertEqual(sum(x["rollout_batch_id"] == "ats-2026-11-01" for x in sources), 500)
        self.assertTrue(all(c["collection_activation_hold"] is True for c in companies))
        self.assertTrue(all(s["enabled"] is False for s in sources))
        self.assertEqual(provision(companies, sources), (companies, sources))
        self.assertEqual(prepare(companies, sources, observations)[:2], (companies, sources))

    def test_activation_simulation_keeps_actual_records_held(self):
        observations = [sample("first", signals=[{"id": "1", "countries": ["DE"]}]), sample("second")]
        companies, sources, _ = prepare([], [], observations)
        row = simulate_selection(companies, sources, "ats-2026-11-01",
                                 datetime(2026, 11, 23, 19, tzinfo=timezone.utc))
        self.assertEqual((row["selected"], row["daily"], row["weekly"]), (2, 1, 1))
        self.assertTrue(all(c["collection_activation_hold"] for c in companies))
        self.assertTrue(all(not s["enabled"] for s in sources))
        # Turning on the source alone cannot bypass the existing hold gate.
        with self.assertRaisesRegex(ValueError, "Held employer"):
            provision(companies, [dict(sources[0], enabled=True), sources[1]])

    def test_checked_in_lot_cannot_activate_via_provisioning(self):
        companies = json.loads((ROOT / "data/companies.json").read_text())
        sources = json.loads((ROOT / "data/sources.json").read_text())
        registered = {row["id"]: row for row in companies}
        lots = [row for row in sources if row.get("rollout_batch_id", "").startswith(PREFIX)]
        self.assertTrue(lots, "Expected checked-in ATS lots")
        self.assertTrue(all(count <= 500 for count in Counter(row["rollout_batch_id"] for row in lots).values()))
        for row in lots:
            company = registered[row["company_id"]]
            self.assertIs(row["enabled"], False)
            self.assertIs(company["collection_activation_hold"], True)
            self.assertIn(row["id"], company["source_ids"])
            self.assertEqual(row["rollout_batch_id"], company["rollout_batch_id"])
        self.assertEqual(provision(companies, sources), (companies, sources))

    def test_robot_rules_and_daily_limit_block_before_http(self):
        board = BoardClient("example.jobs.personio.de", RequestBudget(0))
        board.rules = [("disallow", "/xml")]
        with self.assertRaisesRegex(ValueError, "robots"):
            board.request("https://example.jobs.personio.de/xml")
        board.rules = []
        with self.assertRaisesRegex(ValueError, "daily budget reached"):
            board.request("https://example.jobs.personio.de/xml")
        self.assertEqual(board.gets, 0)
