"""Regression tests for measured two-run official Greenhouse audit."""
import copy
import json
from pathlib import Path
import unittest

from scripts.audit_greenhouse_cycles import analyze


EVIDENCE = (Path(__file__).resolve().parents[1] /
            "docs/greenhouse-dim-two-cycles.json")


class DIMCycleAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))

    def test_measured_complete_cycles_preserve_verified_job(self):
        result = analyze(self.evidence)
        self.assertEqual([x["collected"] for x in result["cycles"]], [33, 33])
        self.assertEqual([x["requests"] for x in result["cycles"]], [4, 4])
        self.assertEqual(result["same_verified_hr_internships"], 1)
        self.assertEqual(result["added_verified_hr_internships_in_second_cycle"], 0)
        self.assertEqual(result["no_longer_verified_hr_internships"], 0)
        self.assertEqual(result["unique_verified_hr_internships_across_cycles"], 1)
        self.assertEqual(result["total_requests"], 8)
        self.assertEqual(result["total_bytes_read"], 609894)
        self.assertEqual(result["total_duration_seconds"], 2.8)
        self.assertIsNone(result["estimated_monetary_cost"])

    def test_two_runs_must_be_independent_complete_and_identity_stable(self):
        for mutate in (
            lambda d: d["cycles"][1].update(workflow_run_id=d["cycles"][0]["workflow_run_id"]),
            lambda d: d["cycles"][1]["source_report"].update(status="partial"),
            lambda d: d["cycles"][1]["source_report"].update(page_failures=1),
            lambda d: d["cycles"][1]["source_report"].update(records_inspected=32),
            lambda d: d["cycles"][1]["source_report"].update(checked_at="2026-11-09T00:00:00+00:00"),
            lambda d: d["cycles"][1]["source_report"].update(requests=0),
            lambda d: d["cycles"][1]["verified_hr_jobs"][0].update(policy_version=1),
            lambda d: d["cycles"][1]["verified_hr_jobs"][0].update(
                apply_url="https://job-boards.greenhouse.io/unrelated/jobs/8331346"),
        ):
            with self.subTest(mutate=mutate.__code__.co_firstlineno):
                data = copy.deepcopy(self.evidence)
                mutate(data)
                with self.assertRaises(ValueError):
                    analyze(data)

    def test_new_verified_vacancy_is_counted_without_double_counting(self):
        data = copy.deepcopy(self.evidence)
        extra = copy.deepcopy(data["cycles"][1]["verified_hr_jobs"][0])
        extra["catalog_id"] = "distinct-synthetic-vacancy"
        extra["posting_id"] = "synthetic-only"
        extra["url"] = "https://job-boards.greenhouse.io/dim/jobs/synthetic-only"
        extra["apply_url"] = extra["url"]
        data["cycles"][1]["verified_hr_jobs"].append(extra)
        data["cycles"][1]["source_report"]["matching"] = 2
        data["cycles"][1]["source_report"]["verification_states"]["verified"] = 2
        result = analyze(data)
        self.assertEqual(result["same_verified_hr_internships"], 1)
        self.assertEqual(result["added_verified_hr_internships_in_second_cycle"], 1)
        self.assertEqual(result["unique_verified_hr_internships_across_cycles"], 2)

    def test_no_network_or_input_mutation(self):
        data = copy.deepcopy(self.evidence)
        old = copy.deepcopy(data)
        a = analyze(data)
        b = analyze(data)
        self.assertEqual(a, b)
        self.assertEqual(data, old)


if __name__ == "__main__":
    unittest.main()
