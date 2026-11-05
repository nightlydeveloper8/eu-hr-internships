"""Apply reviewed group aliases without discarding recruiting-channel provenance."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def consolidate(companies,rules):
 companies=list(companies)
 for rule in rules:
  members=[c for c in companies if c['id'] in rule['members']]
  if not members:continue
  base=dict(next((c for c in members if c['id']==rule['id']),members[0]))
  base.update(id=rule['id'],name=rule['name'],identity_evidence_url=rule['evidence_url'])
  base['aliases']=sorted(set(n for c in members for n in [c['name']]+c.get('aliases',[]) if n!=rule['name']))
  base['target_countries']=sorted({v for c in members for v in c['target_countries']})
  base['source_ids']=sorted({v for c in members for v in c['source_ids']})
  base['workplaces']=[p for c in members for p in c['workplaces']]
  links=base.get('additional_channels',[])
  for c in members:
   if c['id']!=base['id'] or c['name']!=base['name']:
    item={k:c.get(k) for k in ['name','website_url','career_url','evidence_url','career_check'] if c.get(k)}
    if item not in links:links.append(item)
  base['additional_channels']=links
  if not base.get('career_url'):
   verified=next((c for c in members if c.get('career_url')),None)
   if verified:
    base['career_url']=verified['career_url']
    if verified.get('career_check'):base['career_check']=verified['career_check']
  if base['source_ids'] and any(c['review_status']=='monitoring' for c in members):base['review_status']='monitoring'
  companies=[c for c in companies if c['id'] not in rule['members']]
  companies.append(base)
 return sorted(companies,key=lambda c:c['id'])
if __name__=='__main__':
 p=ROOT/'data/companies.json';rows=json.loads(p.read_text());rules=json.loads((ROOT/'data/company-identity-rules.json').read_text());result=consolidate(rows,rules);p.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(len(rows),'records consolidated into',len(result))
