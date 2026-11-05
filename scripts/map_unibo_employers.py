"""Map public Bologna career-fair employer profiles to their declared official sites.
Profiles are discovery provenance; neither attendance nor an accessible site confirms
an Italian workplace or a currently available HR internship.
"""
import argparse,json,re,sys,threading
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
from urllib.parse import urlsplit
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from collector.adapters import Client
from collector.employer_pages import JobLinksParser
from collector.company_registry import company_key
from scripts.map_employers import inspect,domain,clean
ROOT=Path(__file__).resolve().parents[1]
DIRECTORY='https://eventi.unibo.it/careerday/aziende-partecipanti-2026'

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--cache',type=Path,required=True);args=parser.parse_args();args.cache.mkdir(parents=True,exist_ok=True)
 client=Client(delay=.6);lock=threading.Lock()
 body=client.request(DIRECTORY)[0].decode('utf-8','replace');links=JobLinksParser();links.feed(body)
 profiles=sorted({u for u,_ in links.links if re.fullmatch(re.escape(DIRECTORY)+r'/view/\d+',u)})
 existing=json.loads((ROOT/'data/companies.json').read_text());known_names={company_key(n) for c in existing for n in [c['name']]+c.get('aliases',[])};known_domains={domain(c.get('website_url') or c.get('career_url')) for c in existing}
 results=[];accepted=[];state_lock=threading.Lock()
 def profile(url):
  row={'profile_url':url}
  try:
   with lock:b,_,_=client.request(url)
   html=b.decode('utf-8','replace');title=re.search(r'<h1[^>]*>(.*?)</h1>',html,re.S)
   if not title:raise ValueError('Missing employer name')
   name=clean(title[1]);p=JobLinksParser();p.feed(html)
   websites=[u.strip() for u,label in p.links if u.strip().startswith(('https://','http://')) and clean(label).rstrip('/')==u.strip().rstrip('/') and domain(u) not in ('eventi.unibo.it','www.unibo.it')]
   if not websites:raise ValueError('No explicitly declared official website')
   website=websites[0];key=company_key(name)
   with state_lock:
    if key in known_names or domain(website) in known_domains:return dict(profile_url=url,name=name,status='already-known')
    known_names.add(key);known_domains.add(domain(website))
   company=dict(id=key,name=name,website_url=website,career_url=None,evidence_url=url,target_countries=['IT'],workplaces=[],source_ids=[],priority='normal',hr_internship_evidence='not-yet-confirmed',review_status='research-required',discovery_method='university-career-fair',discovery_directory=DIRECTORY)
   company=inspect(company)
   final=company.get('website_check',{}).get('final_url','')
   if final.startswith('https://'):company['website_url']=final
   if not company['website_url'].startswith('https://'):return dict(profile_url=url,name=name,status='https-review-required')
   with state_lock:accepted.append(company)
   return dict(profile_url=url,name=name,status='mapped',website_check=company.get('website_check'),career_check=company.get('career_check'))
  except Exception as e:row.update(status='review-required',reason=str(e)[:180]);return row
 print('Profiles to review',len(profiles),flush=True)
 with ThreadPoolExecutor(max_workers=4) as pool:
  for f in as_completed([pool.submit(profile,u) for u in profiles]):
   results.append(f.result());(ROOT/'docs/unibo-mapping-audit.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n');(args.cache/'accepted.json').write_text(json.dumps(accepted,ensure_ascii=False,indent=2)+'\n')
   if len(results)%20==0:print('Reviewed',len(results),'new employers',len(accepted),flush=True)
 # Re-read after network work so any simultaneous source integrations survive.
 current=json.loads((ROOT/'data/companies.json').read_text());ids={c['id'] for c in current};new=[c for c in accepted if c['id'] not in ids];current.extend(new)
 (ROOT/'data/companies.json').write_text(json.dumps(sorted(current,key=lambda c:c['id']),ensure_ascii=False,indent=2)+'\n')
 print('Complete',len(current),'employers;',len(new),'added;',sum(bool(c.get('career_url')) for c in new),'career pages',flush=True)
if __name__=='__main__':main()
