"""EU27 access evidence must never be confused with operational source coverage."""
import json
from pathlib import Path
import unittest
from collector.classify import COUNTRIES

ROOT=Path(__file__).resolve().parents[1]


class PublicPESReadinessTests(unittest.TestCase):
    def test_all_eu27_in_readiness_not_claimed_indexed(self):
        doc=json.loads((ROOT/"docs/eu27-public-feed-readiness.json").read_text())
        countries=doc["countries"]
        self.assertEqual(len(countries),27)
        self.assertEqual(set(COUNTRIES),{x["country"] for x in countries})
        self.assertEqual(doc["mode"],"read-only-research-queue-not-production")
        self.assertEqual(sum(x["readiness"]=="public-feed-pilot-confirmed"
                             for x in countries),1)
        self.assertEqual(next(x for x in countries if x["country"]=="SE")["service"],
                         "Arbetsförmedlingen JobSearch")
        self.assertEqual(next(x for x in countries if x["country"]=="CZ")["readiness"],
                         "official-open-data-needs-technical-and-privacy-review")
        self.assertEqual(next(x for x in countries if x["country"]=="AT")["readiness"],
                         "portal-automation-prohibited")
        self.assertEqual(next(x for x in countries if x["country"]=="FI")["readiness"],
                         "explicit-activation-required")
        for item in countries:
            self.assertNotIn("operational",item["readiness"])
            self.assertIn("next_action",item)
        self.assertEqual(doc["pan_european"]["readiness"],"partner-conditional")


if __name__=="__main__":
    unittest.main()
