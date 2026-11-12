"""Offline-by-default EU university directory discovery.

Examples:
python3 scripts/eu_directory_discovery.py --snapshot-dir /tmp/approved-seeds
python3 scripts/eu_directory_discovery.py --live --output /tmp/discovery.json

The second form fetches ONLY seeds with explicit access_reviewed=true.
No registry writes, employer website visits, or verification of jobs.
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from collector.eu_directory_discovery import build_discovery_queue, fetch_reviewed_seed


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seeds", type=Path, default=ROOT/"data/eu-discovery-seeds.json")
    parser.add_argument("--snapshot-dir", type=Path)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--previous", type=Path, help="Persisted prior discovery-only queue")
    parser.add_argument("--output", type=Path, help="Output JSON; stdout when omitted")
    parser.add_argument("--per-seed", type=int, default=40)
    args = parser.parse_args(argv)
    if args.live and args.snapshot_dir:
        parser.error("--live and --snapshot-dir are mutually exclusive")
    if args.live and not args.output:
        parser.error("Live discovery requires an explicit output audit path")
    if not args.live and not args.snapshot_dir:
        parser.error("Offline discovery requires --snapshot-dir")
    seeds = json.loads(args.seeds.read_text(encoding="utf-8"))["seeds"]
    companies = json.loads((ROOT/"data/companies.json").read_text(encoding="utf-8"))
    previous = json.loads(args.previous.read_text(encoding="utf-8")) if args.previous else None
    snapshots = {}
    for seed in seeds:
        if args.live:
            if not seed["access_reviewed"]:
                continue
            record = fetch_reviewed_seed(seed, seconds=20, max_requests=6)
            snapshots[seed["id"]] = dict(html=record.pop("body"),
                observed_at=datetime.now(timezone.utc).isoformat(), **record)
        else:
            path = args.snapshot_dir/(seed["id"]+".html")
            meta = args.snapshot_dir/(seed["id"]+".meta.json")
            if not path.is_file():
                continue
            if not meta.is_file():
                parser.error("Missing observation provenance: "+str(meta))
            record = json.loads(meta.read_text(encoding="utf-8"))
            snapshots[seed["id"]] = dict(html=path.read_text(encoding="utf-8"), **record)
    report = build_discovery_queue(seeds, snapshots, companies, previous=previous,
                                   per_seed=args.per_seed)
    raw = json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False)+"\n"
    if args.output:
        args.output.write_text(raw, encoding="utf-8")
    else:
        print(raw, end="")
    return report


if __name__ == "__main__":
    main()
