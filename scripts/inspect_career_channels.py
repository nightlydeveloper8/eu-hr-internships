"""Review official career links and public ATS references; never auto-enable sources."""
import sys,json,re
from pathlib import Path
import argparse
from html import unescape
from concurrent.futures import ThreadPoolExecutor,as_completed
from urllib.parse import urljoin,urlsplit
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from collector.adapters import Client
from collector.employer_pages import PageParser
from collector.classify import classify_role
root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description='Inspect declared employer career pages without enabling sources.')
parser.add_argument('--cache',type=Path,default=Path('/tmp/channel-scans'))
parser.add_argument('--workers',type=int,default=6)
parser.add_argument('--country')
parser.add_argument('--method')
parser.add_argument('--registry',type=Path,default=root/'data/companies.json')
args=parser.parse_args();args.cache.mkdir(parents=True,exist_ok=True)
companies=json.loads(args.registry.read_text())
selected=[c for c in companies if c.get('career_url') and not c.get('source_ids') and (not args.country or args.country in c.get('target_countries',[])) and (not args.method or c.get('discovery_method')==args.method)]
def scan(c):
 row={'company_id':c['id'],'url':c['career_url']}
 try:
  body,status,final=Client().request(c['career_url']);(args.cache/(c['id']+'.html')).write_bytes(body)
  parser=PageParser();parser.feed(body.decode('utf-8','replace'));links=list(dict.fromkeys(urljoin(final,x.strip()) for x in parser.links if urlsplit(urljoin(final,x.strip())).scheme=='https'))
  html=unescape(body.decode('utf-8','replace').replace('\\/','/'))
  embedded=re.findall(r'https?://[a-zA-Z0-9.-]+\.(?:jobs\.personio\.(?:de|com)|recruitee\.com|greenhouse\.io|lever\.co)[^\s"<>\\]*',html)
  row['embedded_ats_links']=sorted({x.rstrip("`;'") for x in embedded if not any(t in x for t in ['analytics','captcha'])})
  row.update(status='reviewed',final_url=final,ats_links=[x for x in [final]+links if re.search(r'greenhouse.io|lever.co|recruitee.com|personio.de|personio.com|teamtailor.com|softgarden.de|ashbyhq.com|smartrecruiters.com',urlsplit(x).hostname or '')],candidate_job_links=[x for x in links if classify_role(urlsplit(x).path.replace('-',' ').replace('_',' '))],jobposting=body.count(b'JobPosting'))
 except Exception as e:row.update(status='review-required',reason=str(e)[:200])
 return row
results=[]
suffix='-'.join(x for x in [args.country.lower() if args.country else '',args.method or ''] if x)
output=root/'docs'/('career-channel-scan-'+suffix+'.json' if suffix else 'career-channel-scan.json')
print('Scanning',len(selected),flush=True)
with ThreadPoolExecutor(max_workers=args.workers) as pool:
 for f in as_completed([pool.submit(scan,c) for c in selected]):
  results.append(f.result());output.write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
  if len(results)%25==0:print('Reviewed',len(results),'ATS',sum(bool(r.get('ats_links')) for r in results),'HR candidate links',sum(bool(r.get('candidate_job_links')) for r in results),flush=True)
print('Complete',len(results),flush=True)
