"""Read-only JobTech → policy-v2 employer inventory / ATS proof, staging only."""
import argparse
import json
from pathlib import Path
from collector.official_feed_policy_dossier import review

ROOT=Path(__file__).resolve().parents[1]


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input",type=Path,required=True)
    p.add_argument("--provider-id",required=True)
    p.add_argument("--approved-host",required=True)
    p.add_argument("--reviewed-inventory",required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args(argv)
    if a.output.resolve().is_relative_to((ROOT/"data").resolve()) or a.output.resolve()==a.input.resolve():
        p.error("Cannot overwrite production files or input")
    payload=json.loads(a.input.read_text())
    if payload.get("provider")!="jobtech-se" or payload.get("mode")!="discovery-only":
        p.error("Expected JobTech discovery-only input")
    candidates=[c for c in payload["candidates"] if c.get("provider_id")==a.provider_id]
    if len(candidates)!=1:
        p.error("Exactly one observed matching JobTech posting required")
    result=review(candidates[0],approved_host=a.approved_host,
                  approved_inventory_url=a.reviewed_inventory)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
    print("POLICY_V2_DOSSIER "+json.dumps(result,ensure_ascii=False,sort_keys=True))
    return result


if __name__=="__main__":
    main()
