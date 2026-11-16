"""Safe, repeatable structured EU vacancy discovery pilot.

Examples:
  python -m scripts.official_feed_discovery --provider jobtech-se --live --output /tmp/se-pilot.json
  python -m scripts.official_feed_discovery --provider eures-authorized-input \
      --input /path/authorised-eures.json --authorization /path/grant-evidence.json \
      --output /tmp/eures-review.json

Never writes to the main catalog or registers an ATS source. EURES has NO
live-fetch mode here; a separate authorised upstream must supply metadata.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import time
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from collector.official_feed_discovery import (
    JOBTECH_HOST, JOBTECH_QUERIES, discovery_report, normalize, https_url
)
from collector.runtime import BudgetClient


def authorisation_evidence(path):
    """Require an explicit, auditable operator grant for EURES input."""
    if not path or not path.is_file():
        raise ValueError("EURES input needs an authorization evidence JSON file")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("source") != "eures":
        raise ValueError("Invalid EURES authorization evidence")
    fields = ("grant_reference", "granting_authority", "approved_use", "document_url", "valid_until")
    if any(not isinstance(data.get(k), str) or not data[k].strip() for k in fields):
        raise ValueError("EURES authorization metadata is incomplete")
    if data.get("permits_vacancy_extraction_and_indexing") is not True:
        raise ValueError("No permission for both extraction and downstream indexing")
    if not https_url(data["document_url"]):
        raise ValueError("Authorization document URL must be valid HTTPS")
    try:
        expiry = datetime.fromisoformat(data["valid_until"].replace("Z", "+00:00"))
        if expiry.tzinfo is None:
            raise ValueError("Timezone required")
    except (TypeError, ValueError) as exc:
        raise ValueError("Invalid EURES authorization expiry") from exc
    if expiry <= datetime.now(timezone.utc):
        raise ValueError("EURES authorization evidence has expired")
    return {"grant_reference":data["grant_reference"],
            "granting_authority":data["granting_authority"],
            "document_url":data["document_url"],
            "valid_until":data["valid_until"],
            "status":"operator-attested-not-independently-authenticated"}


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--provider",required=True,choices=["jobtech-se","eures-authorized-input"])
    p.add_argument("--live",action="store_true",help="JobTech SE only, explicit bounded GET")
    p.add_argument("--input",type=Path,help="Licensed normalized JSON input; must be an array")
    p.add_argument("--authorization",type=Path,help="Auditable EURES partner permission; not an automatic legal review")
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--per-query",type=int,default=12)
    args=p.parse_args(argv)
    if args.output.resolve() in {(ROOT/"data/catalog.json").resolve(),(ROOT/"data/sources.json").resolve()}:
        p.error("Cannot overwrite production data")
    if args.live == bool(args.input):
        p.error("Choose exactly one of --live or --input")
    if args.provider=="eures-authorized-input" and args.live:
        p.error("EURES automated fetching is not available in this program")
    if args.provider=="jobtech-se" and args.authorization:
        p.error("JobTech SE does not need an EURES grant")
    if args.provider=="eures-authorized-input":
        try:
            grant=authorisation_evidence(args.authorization)
        except (OSError,ValueError,TypeError) as exc:
            p.error(str(exc))
    else:
        grant=None
    catalog=json.loads((ROOT/"data/catalog.json").read_text(encoding="utf-8"))
    existing=[j["url"] for j in catalog["jobs"] if j.get("url")]
    started=time.monotonic()
    if args.live:
        client=BudgetClient(seconds=65,max_requests=12,delay=1.0)
        client.redirect_scope_allowed=lambda target:bool(
            https_url(target,{JOBTECH_HOST})
            and urlsplit(target).hostname==JOBTECH_HOST
        )
        report=discovery_report(client, existing, JOBTECH_QUERIES, args.per_query)
    else:
        data=json.loads(args.input.read_text(encoding="utf-8"))
        report=normalize(data,args.provider,existing_urls=existing)
        report.update(requests=0,bytes_read=0,rendering_count=0,
                      checked_at=datetime.now(timezone.utc).isoformat(),
                      collector_registry_modified=False)
    report["authorisation"]=grant if grant else {"kind":"public-cc0" if args.provider=="jobtech-se" else "missing"}
    report["elapsed_seconds"]=round(time.monotonic()-started,3)
    report["baseline_catalog_jobs"]=len(catalog["jobs"])
    report["catalog_modified"]=False
    if args.output.resolve().is_relative_to((ROOT/"data").resolve()):
        p.error("Discovery report must not be saved into production data/")
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2,ensure_ascii=False,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:report[k] for k in ("provider","input_records","candidate_count",
        "verified_vacancies_added","requests","bytes_read","catalog_modified")},sort_keys=True))
    return report


if __name__=="__main__":
    main()
