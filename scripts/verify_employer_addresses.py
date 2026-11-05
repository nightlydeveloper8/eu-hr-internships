"""Verify explicit corporate address metadata for one discovery family."""
import argparse,json,sys
from concurrent.futures import ThreadPoolExecutor,as_completed
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from collector.adapters import Client
from collector.employer_identity import organisation_evidence
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--method',required=True);args=p.parse_args();rows=json.loads((ROOT/'data/companies.json').read_text());selected=[c for c in rows if c.get('discovery_method')==args.method and c.get('website_check',{}).get('status')=='reachable' and c.get('website_url') and not c.get('workplaces')];results=[]
 def check(c):
  row={'company_id':c['id']}
  try:
   b,_,final=Client().request(c['website_url']);row.update(status='checked',workplaces=organisation_evidence(b,final,datetime.now(timezone.utc).date().isoformat()))
  except Exception as e:row.update(status='review-required',reason=str(e)[:180])
  return row
 print('Official websites',len(selected),flush=True)
 with ThreadPoolExecutor(max_workers=6) as pool:
  for f in as_completed([pool.submit(check,c) for c in selected]):
   results.append(f.result())
   if len(results)%25==0:print('Checked',len(results),'with explicit addresses',sum(bool(r.get('workplaces')) for r in results),flush=True)
 current=json.loads((ROOT/'data/companies.json').read_text());by={c['id']:c for c in current}
 for r in results:
  for place in r.get('workplaces',[]):
   if place not in by[r['company_id']]['workplaces']:by[r['company_id']]['workplaces'].append(place)
 (ROOT/'data/companies.json').write_text(json.dumps(current,ensure_ascii=False,indent=2)+'\n');(ROOT/'docs/employer-address-audit.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n');print('Complete',len(results),sum(bool(r.get('workplaces')) for r in results),flush=True)
if __name__=='__main__':main()
