"""Import public university career-fair directories, then inspect official website links.

No guessed URLs, personal contacts or job descriptions are persisted. A fair country
is a research target, never evidence of an office. Website access is not monitoring.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.parse import urljoin, urlsplit
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from collector.adapters import Client
from collector.company_registry import company_key

ROOT=Path(__file__).resolve().parents[1]
DIRECTORIES={
 'fontys':('NL','https://fontyscareerevent.nl/eindhoven/deelnemende-bedrijven.php?lang=en'),
 'ikom':('DE','https://ikom-tum.de/de/messen/ikom/2026'),
 'phdtalent':('FR','https://careerfair.phdtalent.fr/en/exhibitors/'),
}
class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[];self.current=None
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='a' and a.get('href'):self.current=[a['href'],'']
 def handle_data(self,data):
  if self.current:self.current[1]+=data
 def handle_endtag(self,tag):
  if tag=='a' and self.current:self.links.append(self.current);self.current=None

def clean(s):return unescape(re.sub('<[^>]*>','',s)).strip()
def directory_rows(kind,body):
 if kind=='ikom':
  # Read only public company name, website and exhibitor ID; ignore all other metadata.
  string=r'"((?:\\.|[^"\\])*)"'
  pattern=r'\{id:'+string+r',fair_id:'+string+r',name:'+string+r',booth_number:.*?website_url:'+string
  for m in re.finditer(pattern,body):
   identifier,_,name,url=[json.loads('"'+x+'"') for x in m.groups()]
   yield name,url,DIRECTORIES[kind][1]+'/aussteller/'+identifier
 elif kind=='fontys':
  for block in body.split('<div class="fancy-inner-content">')[1:]:
   name=re.search(r'<h2>(.*?)</h2>',block,re.S);url=re.search(r'<a class="btn" href="([^"]+)"',block)
   if name and url:yield clean(name[1]),unescape(url[1]),DIRECTORIES[kind][1]
 elif kind=='phdtalent':
  for m in re.finditer(r'<a href="([^"]+)" data-caption-title="([^"]+)"',body):
   yield unescape(m[2]),unescape(m[1]),DIRECTORIES[kind][1]

def website_url(url):
 url=url.strip()
 if url.startswith('www.'):url='https://'+url
 p=urlsplit(url)
 if p.scheme not in ('https','http') or not p.hostname or p.username:return None
 # Preserve the declared link; HTTPS is checked explicitly during inspection.
 return url

def domain(url):
 host=(urlsplit(url or '').hostname or '').lower().removeprefix('www.')
 return host

CAREER=re.compile(r'career|karriere|werken.?bij|working.?at|work.?with.?us|join.?us|recrutement|rejoignez|emploi|jobs|vacatures|lavora.?con|trabaja.?con|carriere',re.I)
def inspect(row):
 row=dict(row);client=Client(delay=.5)
 try:
  declared=row['website_url'];requested=declared
  if urlsplit(declared).scheme=='http':requested=urlsplit(declared)._replace(scheme='https').geturl()
  body,status,final=client.request(requested)
  row['website_check']={'status':'reachable','http_status':status,'declared_url':declared,'requested_url':requested,'final_url':final}
  from collector.employer_identity import organisation_evidence
  row['workplaces']=organisation_evidence(body,final,datetime.now(timezone.utc).date().isoformat())
  if final.startswith('https://'):row['website_url']=final
  parser=Links();parser.feed(body.decode('utf-8','replace'))
  candidates=[]
  if CAREER.search(urlsplit(final).path):candidates.append(final)
  for href,label in parser.links:
   target=urljoin(final,href)
   if urlsplit(target).scheme=='https' and CAREER.search(label+' '+urlsplit(target).path) and not re.search(r'linkedin|facebook|instagram|youtube',domain(target)):
    if target not in candidates:candidates.append(target)
  row['career_candidates']=candidates[:8]
  row['career_url']=None
  # Verify the first actual link, rather than guessing an ATS slug or path.
  if candidates:
   try:
    _,status,career_final=client.request(candidates[0]);row['career_url']=career_final
    row['career_check']={'status':'reachable','http_status':status,'linked_from':final}
   except Exception as e:row['career_check']={'status':'review-required','reason':str(e)[:180]}
 except Exception as e:row['website_check']={'status':'review-required','reason':str(e)[:180]}
 return row

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--cache',type=Path,required=True);parser.add_argument('--workers',type=int,default=6);args=parser.parse_args()
 existing=json.loads((ROOT/'data/companies.json').read_text());known_names={company_key(n) for c in existing for n in [c['name']]+c.get('aliases',[])};known_domains={domain(c.get('website_url') or c.get('career_url')) for c in existing}
 for c in existing:
  known_domains.update(domain(link.get('website_url') or link.get('career_url')) for link in c.get('additional_channels',[]))
 rows=[]
 for kind,(country,url) in DIRECTORIES.items():
  path=args.cache/(kind+'.html')
  if not path.exists():path.write_bytes(Client().request(url)[0])
  for name,website,evidence in directory_rows(kind,path.read_text()):
   website=website_url(website)
   if not website or not name or company_key(name) in known_names or domain(website) in known_domains:continue
   known_names.add(company_key(name));known_domains.add(domain(website))
   rows.append(dict(id=company_key(name),name=name,website_url=website,career_url=None,evidence_url=evidence,target_countries=[country],workplaces=[],source_ids=[],priority='normal',hr_internship_evidence='not-yet-confirmed',review_status='research-required',discovery_method='university-career-fair',discovery_directory=url))
 print('Candidates after name/domain deduplication:',len(rows),flush=True)
 results=[];out=args.cache/'verified.json'
 with ThreadPoolExecutor(max_workers=args.workers) as pool:
  futures=[pool.submit(inspect,row) for row in rows]
  for f in as_completed(futures):
   results.append(f.result())
   out.write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
   if len(results)%25==0:print('Checked',len(results),'career pages',sum(bool(r.get('career_url')) for r in results),flush=True)
 stamp=datetime.now(timezone.utc).isoformat()
 for r in results:r['checked_at']=stamp
 (ROOT/'docs/employer-mapping-audit.json').write_text(json.dumps(sorted(results,key=lambda x:x['id']),ensure_ascii=False,indent=2)+'\n')
 # Commit only after the full run; accessible and blocked candidates remain distinct.
 eligible=[r for r in results if r['website_url'].startswith('https://')]
 existing.extend(sorted(eligible,key=lambda x:x['id']))
 from scripts.consolidate_employers import consolidate
 existing=consolidate(existing,json.loads((ROOT/'data/company-identity-rules.json').read_text()))
 (ROOT/'data/companies.json').write_text(json.dumps(existing,ensure_ascii=False,indent=2)+'\n')
 print('Total',len(existing),'new',len(eligible),'verified career pages',sum(bool(r.get('career_url')) for r in results),flush=True)
if __name__=='__main__':main()
