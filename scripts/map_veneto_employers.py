"""Map only public Confindustria Veneto Est sector cards and declared websites.
No premium pages, authentication, personal contacts or invented size data.
"""
import argparse,json,re,sys
from concurrent.futures import ThreadPoolExecutor,as_completed
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urljoin,urlsplit
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from collector.adapters import Client
from collector.employer_pages import JobLinksParser
from collector.company_registry import company_key
from scripts.map_employers import inspect,domain,clean
ROOT=Path(__file__).resolve().parents[1];BASE='https://bcomcve.confindustriavenest.it'

def sector_rows(body,url):
 for block in body.split('<h2')[1:]:
  title=re.search(r'^[^>]*>(.*?)</h2>',block,re.S)
  if not title:continue
  parser=JobLinksParser();parser.feed(block)
  websites=[u.strip() for u,label in parser.links if u.strip().startswith(('http://','https://')) and domain(u) not in ('www.iubenda.com','iubenda.com')]
  profiles=[urljoin(BASE,u) for u,label in parser.links if u.startswith('/aziende/')]
  if websites and profiles:yield clean(title[1]),websites[0],profiles[0]

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--cache',type=Path,required=True);parser.add_argument('--limit',type=int,default=200);args=parser.parse_args();args.cache.mkdir(parents=True,exist_ok=True)
 existing=json.loads((ROOT/'data/companies.json').read_text());names={company_key(n) for c in existing for n in [c['name']]+c.get('aliases',[])};domains={domain(c.get('website_url') or c.get('career_url')) for c in existing}
 client=Client(delay=.6);p=JobLinksParser();p.feed(client.request(BASE+'/gruppi-merceologici')[0].decode())
 sectors=list(dict.fromkeys(urljoin(BASE,u) for u,label in p.links if u.startswith('/gruppi-merceologici/')));groups=[];audit=[]
 for url in sectors:
  try:
   b,_,_=client.request(url);rows=list(sector_rows(b.decode('utf-8','replace'),url));groups.append((url,rows));audit.append(dict(url=url,status='read',declared_websites=len(rows)))
  except Exception as e:audit.append(dict(url=url,status='review-required',reason=str(e)[:180]))
 selected=[];offset=0
 while len(selected)<args.limit and any(offset<len(rows) for url,rows in groups):
  for url,rows in groups:
   if offset>=len(rows):continue
   name,website,evidence=rows[offset];key=company_key(name)
   if key in names or domain(website) in domains:continue
   names.add(key);domains.add(domain(website))
   selected.append(dict(id=key,name=name,website_url=website,career_url=None,evidence_url=evidence,target_countries=['IT'],workplaces=[],source_ids=[],priority='normal',hr_internship_evidence='not-yet-confirmed',review_status='research-required',qualification_status='hr-capacity-and-size-review-required',discovery_method='regional-industry-association',discovery_directory=url,sector_evidence={'label':url.rsplit('/',1)[-1],'url':url}))
   if len(selected)>=args.limit:break
  offset+=1
 print('Public sectors',len(sectors),'candidates after deduplication',len(selected),flush=True);results=[]
 with ThreadPoolExecutor(max_workers=6) as pool:
  for f in as_completed([pool.submit(inspect,c) for c in selected]):
   row=f.result();row['checked_at']=datetime.now(timezone.utc).isoformat();results.append(row);(args.cache/'results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
   if len(results)%25==0:print('Reviewed',len(results),'career pages',sum(bool(c.get('career_url')) for c in results),flush=True)
 current=json.loads((ROOT/'data/companies.json').read_text());ids={c['id'] for c in current};eligible=[r for r in results if r['website_url'].startswith('https://') and r['id'] not in ids];current.extend(eligible)
 (ROOT/'docs/veneto-mapping-audit.json').write_text(json.dumps(dict(sectors=audit,companies=results),ensure_ascii=False,indent=2)+'\n');(ROOT/'data/companies.json').write_text(json.dumps(sorted(current,key=lambda c:c['id']),ensure_ascii=False,indent=2)+'\n')
 print('Complete',len(current),'employers;',len(eligible),'added;',sum(bool(c.get('career_url')) for c in eligible),'career pages',flush=True)
if __name__=='__main__':main()
