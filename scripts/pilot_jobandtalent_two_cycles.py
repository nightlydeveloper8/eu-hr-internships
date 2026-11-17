"""Explicit single-vacancy JobTech / employer ATS / cumulative two-cycle read-only pilot.

One fresh JobTech snapshot + at most two separately fresh employer-ATS dossier reads;
no applications, no manual promotion, no source activation or production writes.
Only non-personal, bounded aggregate metrics are retained.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import time
from urllib.parse import urlsplit

from collector.official_feed_discovery import JOBTECH_QUERIES, discovery_report, https_url
from collector.official_feed_policy_dossier import review
from collector.official_feed_staging import staging_part
from collector.pipeline import ROOT, finalize
from collector.runtime import BudgetClient
from tempfile import TemporaryDirectory

JOBTECH_ID = "31558200"
ATS_ID = "8503489"
HOST = "jobb.jobandtalent.com"
INVENTORY = "https://jobb.jobandtalent.com/sitemap"
SOURCE_ID = "staging-jobandtalent-se"


def baseline_from_file(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("jobs"), list):
        raise ValueError("Missing baseline catalog")
    return data


def run(baseline, discovery_client=None, dossier_factory=None, *,
        candidate_id=JOBTECH_ID, max_per_query=10):
    """A single opt-in run with two fresh reads of the *same* posting.

    Distinguishes a second real ATS review from offline two-cycle fixture tests.
    A blocked first cycle stops; no speculative second retry.
    """
    started = time.monotonic()
    result = dict(mode="bounded-live-two-cycle-staging-only",
                  jobtech_id=candidate_id, ats_id_expected=ATS_ID,
                  baseline_jobs=len(baseline.get("jobs", [])),
                  discovery={}, cycles=[], state="not-started",
                  net_new_distinct_verified_in_production=0,
                  source_enabled=False, catalog_modified=False,
                  applications_submitted=0, browser_renderings=0,
                  limits="Only one exact existing JobTech id, reviewed host and company inventory; two ATS dossiers maximum")
    if not isinstance(baseline, dict) or not isinstance(baseline.get("jobs"), list):
        raise ValueError("A valid catalog snapshot is mandatory")
    if candidate_id != JOBTECH_ID:
        raise ValueError("Only the reviewed Jobandtalent JobTech ID is permitted")
    network = discovery_client or BudgetClient(seconds=65, max_requests=9, delay=1.0)
    network.redirect_scope_allowed = lambda url: bool(
        https_url(url, {"jobsearch.api.jobtechdev.se"})
        and urlsplit(url).hostname == "jobsearch.api.jobtechdev.se"
    )
    current = baseline
    try:
        source = dict(id=SOURCE_ID, employer="Jobandtalent Sweden AB",
                      adapter="jobtech-policy-v2-staging",
                      enabled=False, staging_only=True,
                      ownership_scope="reviewed-hosts",
                      require_employer_identity=True,
                      allowed_hosts=[HOST], reviewed_inventory_url=INVENTORY)
        fetched = discovery_report(network, catalog_urls=(
            row["url"] for row in baseline["jobs"] if row.get("url")
        ), queries=JOBTECH_QUERIES, per_query=max_per_query)
        result["discovery"] = dict(
            requests=fetched["requests"], bytes_read=fetched["bytes_read"],
            candidates=fetched["candidate_count"], scanned=fetched["input_records"],
            queries=len(JOBTECH_QUERIES),
        )
        matches = [c for c in fetched["candidates"]
                   if c.get("provider_id") == candidate_id]
        if len(matches) != 1:
            result["state"] = "jobtech-posting-not-found-in-bounded-sample"
            return result
        candidate = matches[0]
        baseline_ids = {x["id"] for x in baseline["jobs"]}
        prior_id = None
        first_discovery = None
        for number in (1, 2):
            cycle_start = time.monotonic()
            # Dossier reads an exact approved ATS + legal page + inventory with BudgetClient.
            kwargs = dict(approved_host=HOST, approved_inventory_url=INVENTORY)
            if dossier_factory is not None:
                kwargs["client_factory"] = dossier_factory
            dossier = review(candidate, **kwargs)
            stamp = datetime.now(timezone.utc).isoformat()
            part = staging_part(candidate, dossier, source, stamp, current["jobs"])
            summary = dict(cycle=number,
                           dossier_status=dossier["status"],
                           ats_id_observed=dossier.get("ats_posting_id"),
                           requests=dossier["requests"], bytes_read=dossier["bytes_read"],
                           elapsed_seconds=round(time.monotonic()-cycle_start, 3),
                           reviewed_inventory=bool(dossier.get("official_inventory_confirmed")),
                           same_vacancy_form=bool(dossier.get("job_identity_match")),
                           stage_status="eligible" if part["jobs"] else "review-required",
                           reason=part["report"].get("reason") or dossier.get("reason"),
                           closure_eligible=len(part["closure_eligible"]))
            if not part["jobs"]:
                result["cycles"].append(summary)
                result["state"] = "policy-v2-review-required-no-promotion"
                return result
            with TemporaryDirectory(prefix="pp-jobandtalent-pilot-") as directory:
                staged, coverage = finalize(
                    [source], [source], current, {}, [part], stamp, Path(directory)
                )
            prior_ids = {x["id"] for x in current["jobs"]}
            staged_ids = [x["id"] for x in staged["jobs"]]
            job_id = part["jobs"][0]["id"]
            observed = [x for x in staged["jobs"] if x["id"] == job_id]
            valid = len(observed) == 1 and observed[0]["status"] == "open"
            summary.update(
                stage_verified=valid,
                new_record_ids_vs_previous=len(set(staged_ids)-prior_ids),
                catalog_ids_lost_vs_previous=len(prior_ids-set(staged_ids)),
                id_stable=prior_id is None or prior_id == job_id,
                first_discovered_preserved=first_discovery is None or
                    observed[0]["first_discovered_at"] == first_discovery if observed else False,
                duplicate_id_count=len(staged_ids)-len(set(staged_ids)),
                staging_verified_internships=coverage["quality"]["verified_internships"],
                catalog_output_written_only_in_temporary_directory=True,
            )
            result["cycles"].append(summary)
            if not valid or summary["catalog_ids_lost_vs_previous"] or summary["duplicate_id_count"] or not summary["id_stable"] or not summary["first_discovered_preserved"]:
                result["state"] = "staging-invariant-failed"
                return result
            prior_id = job_id
            first_discovery = observed[0]["first_discovered_at"]
            current = staged
        last_id = result["cycles"][-1]
        result["distinct_staging_new_vs_baseline"] = sum(
            j["id"] not in baseline_ids and j["status"] == "open"
            and j["internship_type"] == "internship"
            for j in current["jobs"]
        )
        result["idempotent_second_cycle"] = (
            last_id["id_stable"] and last_id["first_discovered_preserved"]
            and last_id["new_record_ids_vs_previous"] == 0
        )
        result["state"] = "two-live-cycles-staging-policy-v2-passed" if result["idempotent_second_cycle"] else "staging-invariant-failed"
    except Exception as exc:
        result["state"] = "access-blocked-or-execution-incomplete"
        result["reason"] = type(exc).__name__ + ": " + str(exc)[:180]
    finally:
        result["total_requests"] = getattr(network, "requests", 0) + sum(
            x["requests"] for x in result["cycles"]
        )
        result["total_bytes_read"] = getattr(network, "bytes", 0) + sum(
            x["bytes_read"] for x in result["cycles"]
        )
        result["elapsed_seconds"] = round(time.monotonic()-started, 3)
    return result


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--catalog", type=Path, default=ROOT/"data/catalog.json")
    args = p.parse_args(argv)
    target = args.output.resolve()
    if target.is_relative_to((ROOT/"data").resolve()) or target == args.catalog.resolve():
        p.error("A preflight cannot overwrite production data or its baseline")
    report = run(baseline_from_file(args.catalog))
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)+"\n",
                      encoding="utf-8")
    print("JOBANDTALENT_TWO_CYCLE_RESULT "+json.dumps(report, ensure_ascii=False, sort_keys=True))
    return report


if __name__ == "__main__":
    main()
