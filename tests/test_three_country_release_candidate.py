"""Cross-feature contract: three countries, no accidental release or ID loss.

This suite is deliberately offline. Separate employer/ATS preflight runs supply
live policy-v2 evidence; source registration and CI are not such evidence.
"""
import unittest

from collector.classify import stable_id
from collector.daily import provision
from collector.jks import source_gate as jks_gate
from collector.official_feed_adapter import source_gate as jobtech_gate
from collector.pipeline import ROOT, read
from collector.recruitee_alias import source_gate as smartways_gate
from collector.verification import verify_vacancy


IDS = ("staging-jobandtalent-se", "jks-dk-internships", "pilot-smartways-internal-pl")


class ThreeCountryReleaseCandidate(unittest.TestCase):
    def setUp(self):
        sources = read(ROOT / "data/sources.json", [])
        self.registry = sources
        self.by_id = {s["id"]: s for s in sources}

    def test_three_exact_disabled_sources_no_duplicates(self):
        self.assertEqual(len(self.registry), len(self.by_id))
        for name in IDS:
            self.assertIn(name, self.by_id)
            source = self.by_id[name]
            self.assertIs(source.get("enabled"), False)
            self.assertIs(source.get("staging_only"), True)
            self.assertIs(source.get("rollout_approved"), False)
            self.assertIsNone(source.get("rollout_authorization"))
        self.assertEqual(jks_gate(self.by_id[IDS[1]]), "staging")
        self.assertEqual(smartways_gate(self.by_id[IDS[2]]), "staging")
        self.assertEqual(jobtech_gate(self.by_id[IDS[0]], preview=True), "staging")
        with self.assertRaises(ValueError):
            jobtech_gate(self.by_id[IDS[0]], preview=False)

    def test_daily_provision_preserves_all_disabled_and_other_enabled(self):
        _, after = provision(read(ROOT / "data/companies.json", []), self.registry)
        self.assertEqual(sum(s.get("enabled") is True for s in self.registry),
                         sum(s.get("enabled") is True for s in after))
        for name in IDS:
            s = [row for row in after if row["id"] == name]
            self.assertEqual(len(s), 1)
            self.assertFalse(s[0]["enabled"])
        # No new auto collector may be inferred from disabled staging evidence.
        self.assertEqual(set(s["id"] for s in after), set(self.by_id))

    def test_each_activation_gate_is_separate_and_fail_closed(self):
        for name, gate in (
            (IDS[1], jks_gate), (IDS[2], smartways_gate),
        ):
            row = self.by_id[name]
            for changes in (dict(enabled=True), dict(staging_only=False),
                            dict(rollout_approved=True),
                            dict(enabled=True, staging_only=False, rollout_approved=True)):
                with self.subTest(name=name, changes=changes):
                    with self.assertRaises(ValueError):
                        gate(dict(row, **changes))
        se = self.by_id[IDS[0]]
        for changes in (dict(enabled=True), dict(staging_only=False),
                        dict(rollout_approved=True),
                        dict(enabled=True, staging_only=False, rollout_approved=True)):
            with self.subTest(changes=changes):
                with self.assertRaises(ValueError):
                    jobtech_gate(dict(se, **changes))

    def test_verification_dispatch_requires_review_before_any_get(self):
        class NoNetwork:
            def request(self, *args, **kwargs):
                raise AssertionError("Unapproved pipeline attempted a GET")
        jks = dict(self.by_id[IDS[1]], enabled=True)
        with self.assertRaises(ValueError):
            verify_vacancy(
                dict(url="https://www.jks.dk/jobs/role-160886",
                     title="HR Praktikant", posting_identifier="160886"),
                jks, NoNetwork(), "2026-11-20T18:00:00+00:00")
        smart = dict(self.by_id[IDS[2]], enabled=True)
        with self.assertRaises(ValueError):
            verify_vacancy(
                dict(url="https://smartways.recruitee.com/o/recruitment-internship-programme-paid",
                     title="Recruitment Internship Programme (paid)"),
                smart, NoNetwork(), "2026-11-20T18:00:00+00:00")

    def test_existing_public_id_and_new_candidate_ids_are_distinct(self):
        catalog = read(ROOT / "data/catalog.json", {})
        ids = {row["id"] for row in catalog["jobs"]}
        self.assertEqual(len(ids), len(catalog["jobs"]))
        public = [row for row in catalog["jobs"]
                  if row.get("source_id") == "public-se-jobtech"
                  and row.get("external_id") == "31558200"]
        self.assertEqual(len(public), 1)
        proposed = {
            stable_id(IDS[1], project)
            for project in ("157063", "156880", "160886", "160782")
        }
        proposed.add(stable_id(IDS[2], "31252"))
        self.assertEqual(len(proposed), 5)
        self.assertFalse(proposed & ids, "A staging-only new catalog ID already exists")
        # The JobTech conversion MUST adopt the one existing public ID,
        # not invent a sixth ID for the corresponding official ATS posting.
        self.assertNotIn(public[0]["id"], proposed)


if __name__ == "__main__":
    unittest.main()
