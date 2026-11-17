"""Opt-in exact-application preflight from a licensed JobTech discovery report.

Runs only with explicit approved employer recruiting hosts. No form submission,
login, CAPTCHA bypass, new catalog entries or automatic source activation.
"""
import argparse
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from collector.official_feed_verification import verify_candidates


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--approved-host",action="append",required=True)
    p.add_argument("--max-candidates",type=int,default=2)
    args=p.parse_args(argv)
    if args.input.resolve()==args.output.resolve():
        p.error("Input and output must be different")
    if args.output.resolve().is_relative_to((ROOT/"data").resolve()):
        p.error("A preflight report may not overwrite production data")
    report=json.loads(args.input.read_text(encoding="utf-8"))
    result=verify_candidates(report,args.approved_host,args.max_candidates)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({k:result[k] for k in
        ("candidates_seen","candidates_attempted","requests","bytes_read",
         "renderings","states","verified_vacancies_added","production_enabled")},
        sort_keys=True))
    for row in result["rows"]:
        print("APPLICATION_PROBE "+json.dumps(
            {k:row.get(k) for k in
             ("provider_id","employer","state","vacancy_match","enabled_form",
              "employer_identity_evidence","observed_headings",
              "structured_job_titles","structured_hiring_organizations",
              "requests","reason")},
            ensure_ascii=False,sort_keys=True))
    return result


if __name__=="__main__":main()
