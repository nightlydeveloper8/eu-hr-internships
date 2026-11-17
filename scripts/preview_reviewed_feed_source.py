"""Manual-only, read-only preview of one disabled reviewed national-feed source.

Use only after explicit preflight authorisation. Does not run from cron or
workflow PR triggers. It never writes production data, enables sources, or
submits applications. Fresh ATS and source identity proof is mandatory.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import time

from collector.pipeline import ROOT, process_source, finalize, read
from collector.runtime import BudgetClient
from collector.official_feed_adapter import ADAPTER, source_gate


def preview(source, baseline, registry, *, discovery_client=None,
            ats_client_factory=None):
    start = time.monotonic()
    source_gate(source, preview=True)  # No HTTP until all guards pass.
    if not isinstance(baseline, dict) or not isinstance(baseline.get("jobs"),list):
        raise ValueError("Valid current catalog snapshot required")
    client = discovery_client or BudgetClient(
        seconds=source["collection_seconds"],max_requests=source["max_requests"],delay=1.0
    )
    stamp = datetime.now(timezone.utc).isoformat()
    kwargs=dict(verify=True, official_feed_preview=True,
                official_feed_prior_jobs=baseline["jobs"])
    if ats_client_factory is not None:
        kwargs["official_feed_ats_client_factory"] = ats_client_factory
    part=process_source(source,client,stamp,**kwargs)
    with TemporaryDirectory(prefix="people-placement-feed-preview-") as directory:
        staged,coverage=finalize(registry,[source],baseline,{},[part],
                                 datetime.now(timezone.utc).isoformat(),Path(directory))
    baseline_ids={r["id"] for r in baseline["jobs"]}
    staged_ids={r["id"] for r in staged["jobs"]}
    added=[r for r in staged["jobs"] if r["id"] not in baseline_ids]
    verified=[r for r in added if r["status"]=="open"
              and r["internship_type"]=="internship"
              and r["verification"]["state"]=="verified"]
    r=part["report"]
    return dict(
        mode="manual-disabled-source-preflight-only",
        source_id=source["id"],provider_id=source["provider_id"],
        expected_ats_id=source["expected_ats_id"],country="SE",
        state="staging-policy-v2-verified" if part["jobs"] else "review-required",
        reason=r.get("reason"),feed_rows_scanned=r.get("feed_rows_scanned",0),
        feed_hr_candidates=r.get("feed_hr_candidates",0),
        feed_requests=r.get("feed_requests",0),
        feed_bytes_read=r.get("feed_bytes_read",0),
        ats_requests=r.get("ats_requests",0),
        ats_bytes_read=r.get("ats_bytes_read",0),
        requests=r.get("requests",0),bytes_read=r.get("bytes_read",0),
        elapsed_seconds=round(time.monotonic()-start,3),
        verified_staging_new_distinct=len(verified),
        baseline_catalog_ids=len(baseline_ids),staged_catalog_ids=len(staged_ids),
        baseline_catalog_ids_lost=len(baseline_ids-staged_ids),
        duplicate_catalog_ids=len(staged["jobs"])-len(staged_ids),
        staging_verified_internships=coverage["quality"]["verified_internships"],
        closure_eligible=part["closure_eligible"],
        source_enabled=False,production_enabled=False,
        production_verified_vacancies_added=0,production_catalog_modified=False,
        applications_submitted=0,browser_renderings=0,
    )


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source-id",required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args(argv)
    if not args.source_id.startswith("staging-"):
        p.error("Only a reviewed, explicitly disabled staging source ID is allowed")
    out=args.output.resolve()
    if (out.is_relative_to((ROOT/"data").resolve()) or out.is_relative_to((ROOT/"dist").resolve())):
        p.error("Preflight reports must never overwrite public catalog files")
    sources=read(ROOT/"data/sources.json",[])
    candidates=[x for x in sources if x.get("id")==args.source_id]
    if len(candidates)!=1:
        p.error("Exactly one registered reviewed source required")
    source=candidates[0]
    source_gate(source,preview=True)
    report=preview(source,read(ROOT/"data/catalog.json",{}),sources)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+"\n",
                   encoding="utf-8")
    print("REVIEWED_FEED_PREVIEW "+json.dumps(report,ensure_ascii=False,sort_keys=True))
    return report


if __name__=="__main__":
    main()
