"""Compare two completed, independent, provenance-linked ATS collection cycles.

Reads checked-in historic source reports; it does not call an ATS, write to a
catalog, execute a workflow or refresh a vacancy's verification timestamp.

Usage: python3 scripts/audit_greenhouse_cycles.py
       python3 scripts/audit_greenhouse_cycles.py --input docs/greenhouse-dim-two-cycles.json
"""
from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EVIDENCE = ROOT / "docs/greenhouse-dim-two-cycles.json"


def _date(raw):
    value = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    if value.tzinfo is None:
        raise ValueError("Evidence timestamps must contain an explicit timezone")
    return value


def _ids(cycle, target):
    checked_at = cycle["source_report"]["checked_at"]
    verified = {}
    for job in cycle.get("verified_hr_jobs", []):
        key = job["catalog_id"]
        if key in verified:
            raise ValueError("Repeated verified job ID within source cycle")
        if job.get("policy_version") != 2 or job.get("verification_state") != "verified":
            raise ValueError("Only policy v2 verified positions may count")
        if job.get("verification_reason") != "same-vacancy-applicant-form":
            raise ValueError("Vacancy-specific applicant form is not proven")
        if job.get("status") != "open" or job.get("country") != target["country"]:
            raise ValueError("Job must be open at a confirmed target workplace")
        if job.get("checked_at") != checked_at:
            raise ValueError("Verification time must be the observed collection time")
        if not job.get("apply_url", "").startswith(target["official_board_url"] + "/jobs/"):
            raise ValueError("An official, source-owned vacancy URL is required")
        if job["url"] != job["apply_url"]:
            raise ValueError("Application URL does not match the observed vacancy")
        verified[key] = job
    return verified


def analyze(evidence):
    if evidence.get("schema_version") != 1:
        raise ValueError("Unsupported evidence schema")
    target = evidence["target"]
    if target["source_id"] != "greenhouse-dim" or target["board"] != "dim":
        raise ValueError("This audit is scoped to the reviewed DIM Greenhouse tenant")
    cycles = evidence["cycles"]
    if len(cycles) != 2:
        raise ValueError("Exactly two independent collection cycles required")
    seen = set()
    per_cycle = []
    job_sets = []
    previous_time = None
    for cycle in cycles:
        run_id = cycle["workflow_run_id"]
        if run_id in seen:
            raise ValueError("Cannot replay the same workflow run as a second cycle")
        seen.add(run_id)
        src = cycle["source_report"]
        stamp = _date(src["checked_at"])
        if previous_time is not None and stamp <= previous_time:
            raise ValueError("Two cycles must be chronologically distinct")
        previous_time = stamp
        if src["id"] != target["source_id"] or src["adapter"] != "greenhouse":
            raise ValueError("Source identity or adapter changed")
        if src["status"] != "ok" or src["page_failures"] != 0:
            raise ValueError("Partial or failed inventories cannot demonstrate full collection")
        if src["collected"] != src["records_inspected"] or src["collected"] < 0:
            raise ValueError("Inventory completeness invariant failed")
        if src["requests"] <= 0 or src["bytes_read"] <= 0 or src["duration_seconds"] <= 0:
            raise ValueError("A live collection must have measurable request, byte and time costs")
        if target["country"] not in src["observed_countries"]:
            raise ValueError("Target workplace country not observed in source")
        jobs = _ids(cycle, target)
        if (src["matching"] != len(jobs) or
                src["verification_states"].get("verified") != len(jobs)):
            raise ValueError("Verified jobs differ from source report counts")
        job_sets.append(set(jobs))
        per_cycle.append(dict(workflow_run_id=run_id, collected=src["collected"],
                              complete=True, verified_hr_internships=len(jobs),
                              requests=src["requests"],
                              duration_seconds=src["duration_seconds"],
                              bytes_read=src["bytes_read"],
                              verified_per_100_requests=round(len(jobs) * 100 / src["requests"], 2)))

    first, second = job_sets
    total_requests = sum(r["requests"] for r in per_cycle)
    total_seconds = sum(r["duration_seconds"] for r in per_cycle)
    total_bytes = sum(r["bytes_read"] for r in per_cycle)
    return dict(source_id=target["source_id"], cycles=per_cycle,
                same_verified_hr_internships=len(first & second),
                added_verified_hr_internships_in_second_cycle=len(second - first),
                no_longer_verified_hr_internships=len(first - second),
                unique_verified_hr_internships_across_cycles=len(first | second),
                total_requests=total_requests,
                total_duration_seconds=round(total_seconds, 3),
                total_bytes_read=total_bytes,
                requests_per_cycle=round(total_requests / 2, 2),
                bytes_per_cycle=round(total_bytes / 2),
                estimated_monetary_cost=None,
                run_type="two historical completed live collection runs; no new live run executed",
                conclusion="retention-confirmed; expansion-not-measured-by-new-job-IDs")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_EVIDENCE)
    args = parser.parse_args(argv)
    report = analyze(json.loads(args.input.read_text(encoding="utf-8")))
    print(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True))
    return report


if __name__ == "__main__":
    main()
