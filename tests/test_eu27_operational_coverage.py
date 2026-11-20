"""EU27 readiness is about verified placements, never index or company counts."""
import copy
import json
from pathlib import Path
import unittest

from scripts.audit_eu27_coverage import EU27, audit, eligible, posting_country


def job(jid, country="LT", role="internship", *, status="open", link_status="verified",
        version=2, checked_at="2026-11-16T12:00:00+00:00"):
    return dict(id=jid, title="HR Intern", source_id="source-1",
                country=country, internship_type=role, status=status,
                link_status=link_status, last_verified_at=checked_at,
                verification=dict(state="verified", policy_version=version, checked_at=checked_at))


def catalog(jobs):
    return dict(updated_at="2026-11-16T13:00:00+00:00", jobs=jobs)


class EU27AuditTests(unittest.TestCase):
    def test_every_country_reported_even_with_zero_sources(self):
        result = audit(catalog([]), [], [])
        self.assertEqual(result["eu_country_count"], 27)
        self.assertEqual({c["country"] for c in result["countries"]}, set(EU27))
        self.assertEqual(result["countries_with_verified_hr_internships"], 0)
        self.assertEqual(result["nationally_complete_countries"], 0)
        self.assertFalse(any(c["national_mapping_complete"] for c in result["countries"]))

    def test_one_v2_stage_does_not_imply_national_mapping_complete(self):
        companies = [dict(id="c", target_countries=["LT", "LV"], source_ids=["source-1"])]
        sources = [dict(id="source-1", enabled=True)]
        result = audit(catalog([job("1")]), companies, sources)
        rows = {c["country"]: c for c in result["countries"]}
        self.assertEqual(result["verified_hr_internships"], 1)
        self.assertEqual(rows["LT"]["verified_hr_internships"], 1)
        self.assertEqual(rows["LT"]["verified_source_ids"], ["source-1"])
        self.assertEqual(rows["LV"]["verified_hr_internships"], 0)
        self.assertEqual(rows["LV"]["enabled_research_target_sources"], 1)
        self.assertFalse(rows["LT"]["national_mapping_complete"])

    def test_unverified_closed_legacy_and_stale_not_promoted(self):
        jobs = [job("1", status="unverified"),
                job("2", status="closed"),
                job("3", version=1),
                job("4", link_status="unverified"),
                job("5", checked_at="2026-11-12T12:00:00+00:00"),
                job("6", checked_at="2026-11-17T12:00:00+00:00")]
        result = audit(catalog(jobs), [], [])
        row = next(c for c in result["countries"] if c["country"] == "LT")
        self.assertEqual(row["seen_job_records"], 6)
        self.assertEqual(row["verified_hr_internships"], 0)
        self.assertEqual(row["closed_job_records"], 1)
        self.assertEqual(row["unverified_job_records"], 5)

    def test_only_distinct_internship_types_count_as_stages(self):
        result = audit(catalog([job("i"), job("w", role="working-student"),
                                job("t", role="traineeship")]), [], [])
        self.assertEqual(result["verified_hr_internships"], 1)
        self.assertEqual(result["verified_hr_working_students"], 1)
        self.assertEqual(result["countries_with_verified_hr_internships"], 1)

    def test_ambiguous_geography_and_duplicate_id_handling(self):
        ambiguous = job("a", country=None)
        ambiguous["countries"] = ["LT", "LV"]
        single = job("b", country=None)
        single["countries"] = ["LV"]
        result = audit(catalog([ambiguous, single]), [], [])
        self.assertEqual(result["unlocated_or_ambiguous_job_records"], 1)
        self.assertEqual(next(c for c in result["countries"] if c["country"] == "LV")["verified_hr_internships"], 1)
        with self.assertRaisesRegex(ValueError, "unique"):
            audit(catalog([job("same"), job("same")]), [], [])

    def test_mapped_batch_schedule_has_all_eu27_once(self):
        path = Path(__file__).resolve().parents[1] / "docs/eu27-expansion/batch-06-review-2026-11-16.json"
        report = json.loads(path.read_text(encoding="utf-8"))
        countries = list(report["scope_countries"])
        for next_batch in report["follow_up_batches"]:
            countries.extend(next_batch["countries"])
        self.assertEqual(len(countries), len(EU27))
        self.assertEqual(set(countries), set(EU27))
        self.assertEqual(report["summary"]["verified_new"], 0)
        self.assertTrue(all(not r["verified"] and not r["enabled"] for r in report["rows"]))

    def test_country_outcomes_distinguish_application_evidence_from_public_listing(self):
        direct = dict(job("direct", country="PL"), application_verification={"url": "https://example.org/apply"})
        listing = dict(job("active", country="LT", link_status="public-api-active-listing"), source_id="public")
        listing["verification"]["policy"] = "public-api-active-listing"
        stale = dict(listing, id="stale", country="LV", last_verified_at="2026-11-01T12:00:00+00:00")
        spoof = dict(listing, id="spoof", country="EE", source_id="unreviewed")
        unlabeled = job("legacy", country="IE")
        sources = [dict(id="public", adapter="eures-search", enabled=True, active_listing_api=True)]
        result = audit(catalog([direct, listing, stale, spoof, unlabeled]), [], sources)
        rows = {r["country"]: r for r in result["countries"]}
        self.assertEqual(rows["LT"]["public_only_hr_internships"], 1)
        self.assertEqual(rows["LT"]["direct_hr_internships"], 0)
        self.assertEqual(rows["PL"]["direct_hr_internships"], 1)
        self.assertEqual(result["direct_hr_internships"], 1)
        self.assertEqual(result["public_only_hr_internships"], 1)
        self.assertEqual(result["countries_without_direct_hr_internships"], 26)
        self.assertEqual(result["countries_without_observed_open_hr_internships"], 25)

    def test_original_inputs_not_mutated(self):
        inputs = (catalog([job("1")]), [dict(id="c", target_countries=["LT"], source_ids=["source-1"])],
                  [dict(id="source-1", enabled=True)])
        before = copy.deepcopy(inputs)
        audit(*inputs)
        self.assertEqual(inputs, before)


if __name__ == "__main__":
    unittest.main()
