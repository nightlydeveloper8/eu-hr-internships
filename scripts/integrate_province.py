"""Integrate reviewed provincial employers without duplicating shared registries."""
import copy
from urllib.parse import urlsplit
from collector.company_registry import company_key
from collector.classify import fold,canonical_url
from collector.daily import provision


def integrate_employers(companies,sources,geography,rows,*,slug):
    companies=copy.deepcopy(companies);sources=copy.deepcopy(sources)
    by_id={c['id']:c for c in companies};used=set();regional=[]
    municipalities={m['name']:m for m in geography['municipalities']}
    region_code=geography['province']['nuts2_code']
    for row in rows:
        cid=row.get('existing_company_id') or company_key(row['name'])
        if cid in used:raise ValueError('Duplicate reviewed employer: '+cid)
        used.add(cid)
        company=by_id.get(cid)
        if row.get('existing_company_id') and company is None:
            raise ValueError('Unknown existing company ID: '+cid)
        if not company:
            keys={company_key(n) for n in [row['name']]+row.get('aliases',[])}
            matches=[c for c in companies if keys.intersection(company_key(n) for n in [c['name']]+c.get('aliases',[]))]
            if matches:raise ValueError('Explicit reuse required: '+str([c['id'] for c in matches]))
            company=dict(id=cid,name=row['name'],website_url=row['website_url'],career_url=row.get('career_url'),evidence_url=row['presence_source_url'],target_countries=['NL'],workplaces=[],source_ids=[],priority='high',hr_internship_evidence='not-yet-confirmed',review_status='research-required')
            companies.append(company);by_id[cid]=company
        old_name=company['name'];company['name']=row['name']
        company['aliases']=sorted(set(company.get('aliases',[])+row.get('aliases',[])+([old_name] if old_name!=row['name'] else [])))
        company['target_countries']=sorted(set(company.get('target_countries',[])+['NL']))
        if row.get('website_url'):company['website_url']=row['website_url']
        if row.get('career_url'):company['career_url']=row['career_url']
        for location in [row]+row.get('additional_locations',[]):
            municipality=municipalities[location['municipality']]
            name=location.get('locality');lookup=name
            places=[p for p in municipality['settlements'] if fold(p['name'])==fold(lookup or '')]
            if name and not places:
                places=[p for p in municipality['settlements'] if fold(name) in [fold(v) for v in p.get('search_name_variants',[])]]
            if name and len(places)!=1:raise ValueError('Unresolved CBS locality: '+str((name,municipality['name'])))
            place=dict(country='NL',region_code=region_code,city=name,municipality=municipality['name'],municipality_code=municipality['cbs_code'],settlement_code=places[0]['code'] if places else None,location_confidence='confirmed',evidence_url=location['presence_source_url'],checked_on=row['checked_on'])
            company['workplaces']=[p for p in company.get('workplaces',[]) if not (p.get('region_code')==region_code and fold(p.get('city') or '')==fold(name or '') and (not p.get('municipality_code') or p.get('municipality_code')==municipality['cbs_code']))]+[place]
        company[slug+'_research']=dict(checked_on=row['checked_on'],size=row['size'],employer_type=row['employer_type'],group_name=row.get('group_name'),notes=row.get('notes',[]))
        if row['size']['qualification']=='verified_50_plus':company['employee_size_evidence']=row['size']
        regional.append(dict(row,company_id=cid))
    companies,sources=provision(companies,sources)
    by_id={c['id']:c for c in companies}
    source_by_id={s['id']:s for s in sources}
    # Extend existing employers' discovery starts, preserving stable source IDs.
    for row in regional:
        company=by_id[row['company_id']]
        for sid in company['source_ids']:
            source=source_by_id.get(sid)
            if not source or source.get('adapter')!='universal-employer':continue
            source['start_urls']=list(dict.fromkeys(canonical_url(u) for u in [company.get('career_url') or company['website_url']]+source.get('start_urls',[])))
            source['allowed_hosts']=sorted(set(source['allowed_hosts'])|{urlsplit(company.get('career_url') or company['website_url']).hostname})
            source['employer']=company['name'];source['career_url']=company.get('career_url') or company['website_url']
    return companies,sources,regional
