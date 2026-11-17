"""Replay a just-read JobTech policy-v2 dossier through normal finalize IN MEMORY.

This command never updates data/, an employer registry, or the public catalog.
It is designed for the opt-in, bounded JobTech preflight workflow only.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from collector.official_feed_staging import staging_part
from collector.pipeline import ROOT, finalize


def replay(discovery, dossier, catalog, *, provider_id, source_id, approved_host,
           reviewed_inventory, stamp=None):
    if not isinstance(discovery, dict) or discovery.get("provider") != "jobtech-se" or discovery.get("mode") != "discovery-only":
        raise ValueError("A bounded JobTech discovery report is required")
    candidates = [x for x in discovery.get("candidates", [])
                  if isinstance(x, dict) and x.get("provider_id") == provider_id]
    if len(candidates) != 1:
        raise ValueError("Exactly one observed source posting required")
    if not isinstance(catalog, dict) or not isinstance(catalog.get("jobs"), list):
        raise ValueError("A valid baseline catalog is required")
    if not isinstance(source_id, str) or not source_id.startswith("staging-"):
        raise ValueError("Staging-specific source ID required")
    candidate = candidates[0]
    source = dict(id=source_id, employer=candidate.get("employer"),
                  adapter="jobtech-policy-v2-staging", enabled=False, staging_only=True,
                  ownership_scope="reviewed-hosts", require_employer_identity=True,
                  allowed_hosts=[approved_host],
                  reviewed_inventory_url=reviewed_inventory)
    clock = stamp or datetime.now(timezone.utc).isoformat()
    part = staging_part(candidate, dossier, source, clock, catalog["jobs"])
    with TemporaryDirectory(prefix="pp-jobtech-replay-") as temporary:
        staged, coverage = finalize([source], [source], catalog, {},
                                    [part], clock, Path(temporary))
    old_ids = {x["id"] for x in catalog["jobs"]}
    staged_ids = {x["id"] for x in staged["jobs"]}
    new_rows = [x for x in staged["jobs"] if x["id"] not in old_ids]
    return dict(
        mode="offline-finalize-replay-not-published",
        provider="jobtech-se", provider_id=provider_id,
        stage_result="eligible-staging-only" if part["jobs"] else "review-required",
        reason=part["report"].get("reason"),
        reviewed_ats_id=part["report"].get("reviewed_ats_id"),
        baseline_catalog_count=len(old_ids), staged_catalog_count=len(staged_ids),
        baseline_ids_lost=len(old_ids-staged_ids),
        new_staged_distinct_verified_internships=sum(
            x["status"] == "open" and x["internship_type"] == "internship" for x in new_rows),
        existing_staged_records_reverified=sum(
            x["id"] in old_ids and x["status"] == "open" for x in part["jobs"]),
        candidate_job_ids=[x["id"] for x in part["jobs"]],
        snapshot_status=staged["update_status"],
        closure_eligible=part["closure_eligible"],
        production_catalog_modified=False, source_registry_modified=False,
        production_verified_vacancies_added=0, applications_submitted=0,
        incremental_http_requests=0, renderings=0,
        note="Staging-only replay from current live dossier; no registered daily source",
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--discovery", type=Path, required=True)
    parser.add_argument("--dossier", type=Path, required=True)
    parser.add_argument("--provider-id", required=True)
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--approved-host", required=True)
    parser.add_argument("--reviewed-inventory", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.output.resolve().is_relative_to((ROOT/"data").resolve()) or args.output.resolve() in (
        args.discovery.resolve(), args.dossier.resolve()
    ):
        parser.error("Refusing to overwrite a source input or production file")
    report = replay(
        json.loads(args.discovery.read_text(encoding="utf-8")),
        json.loads(args.dossier.read_text(encoding="utf-8")),
        json.loads((ROOT/"data/catalog.json").read_text(encoding="utf-8")),
        provider_id=args.provider_id, source_id=args.source_id,
        approved_host=args.approved_host, reviewed_inventory=args.reviewed_inventory,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2)+"\n",
                           encoding="utf-8")
    print("STAGING_FINALIZE_REPLAY "+json.dumps(report, ensure_ascii=False, sort_keys=True))
    return report


if __name__ == "__main__":
    main()
