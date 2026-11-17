"""Opt-in, small, metadata-only public national employment-data pilots.

Does not fetch EURES, employer ATS, or applications. Output in /tmp or staging
only; never modify production catalog/source registry.
"""
import argparse
from datetime import date
import json
from pathlib import Path
from collector.public_pes_sampling import run

ROOT=Path(__file__).resolve().parents[1]


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--provider",choices=("mpsv-cz","nva-lv"),required=True)
    p.add_argument("--date",type=date.fromisoformat)
    p.add_argument("--max-bytes",type=int,default=700000)
    p.add_argument("--max-rows",type=int,default=200)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args(argv)
    if a.provider=="mpsv-cz" and a.date is None:
        p.error("MPSV daily delta requires a concrete date")
    if a.provider=="nva-lv" and a.date is not None:
        p.error("Latvian CKAN datastore does not use --date")
    if not 4096<=a.max_bytes<=1000000 or not 1<=a.max_rows<=250:
        p.error("Preflight bytes/rows budget invalid")
    target=a.output.resolve()
    if target.is_relative_to((ROOT/"data").resolve()):
        p.error("Never put preflight snapshots inside production data")
    result=run(a.provider,day=a.date,max_bytes=a.max_bytes,max_rows=a.max_rows)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True,ensure_ascii=False)+"\n")
    # No personal fields or long texts in this report.
    print(json.dumps({k:result.get(k) for k in
        ("country","source","state","records_scanned","counts",
         "strict_distinct_candidates","input_complete","requests",
         "bytes_read","elapsed_seconds","error")},ensure_ascii=False,sort_keys=True))
    return result


if __name__=="__main__":
    main()
