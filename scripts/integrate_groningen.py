"""Idempotently integrate reviewed Groningen research into the shared registries.

Run after updating docs/groningen-research-{city,municipalities}.json. Unknown
localities and ambiguous matches fail instead of assigning a guessed municipality.
"""
import copy,json,sys
from pathlib import Path
from urllib.parse import urlsplit
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from collector.pipeline import ROOT,read,write
from collector.company_registry import company_key
from collector.classify import fold,canonical_url
from collector.daily import provision


def integrate(companies,sources,geography,rows):
    companies=copy.deepcopy(companies);sources=copy.deepcopy(sources)
    by_id={c['id']:c for c in companies};used=set();regional=[]
    municipalities={m['name']:m for m in geography['municipalities']}
    for row in rows:
        cid=row.get('existing_company_id') or company_key(row['name'])
        if cid in used:raise ValueError('Duplicate reviewed employer: '+cid)
        used.add(cid)
        company=by_id.get(cid)
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
            name=location.get('locality');lookup='Haren Gn' if name=='Haren' and municipality['name']=='Groningen' else name
            places=[p for p in municipality['settlements'] if fold(p['name'])==fold(lookup or '')]
            if name and len(places)!=1:raise ValueError('Unresolved CBS locality: '+str((name,municipality['name'])))
            place=dict(country='NL',region_code='NL11',city=name,municipality=municipality['name'],municipality_code=municipality['cbs_code'],settlement_code=places[0]['code'] if places else None,location_confidence='confirmed',evidence_url=location['presence_source_url'],checked_on=row['checked_on'])
            company['workplaces']=[p for p in company.get('workplaces',[]) if not (p.get('region_code')=='NL11' and fold(p.get('city') or '')==fold(name or '') and (not p.get('municipality_code') or p.get('municipality_code')==municipality['cbs_code']))]+[place]
        company['groningen_research']=dict(checked_on=row['checked_on'],size=row['size'],employer_type=row['employer_type'],group_name=row.get('group_name'),notes=row.get('notes',[]))
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
            source['start_urls']=list(dict.fromkeys(canonical_url(u) for u in [company['career_url']]+source.get('start_urls',[])))
            source['allowed_hosts']=sorted(set(source['allowed_hosts'])|{urlsplit(company['career_url']).hostname})
            source['employer']=company['name'];source['career_url']=company['career_url']
    def configure(cid,**fields):
        company=next(c for c in companies if c['id']==cid)
        source=source_by_id[company['source_ids'][0]];source.update(fields)
        source.update(access_reviewed_on='2026-11-06',permission_basis='Official employer-published public listings and linked application pages; robots and approved hosts checked on every read; no forms submitted')
    configure('hanos',adapter='employer-index',index_urls=['https://www.werkenbijhanos.nl/werkgebieden/HR'],job_url_pattern=r'^https://www\.werkenbijhanos\.nl/vacatures/[^/?]+-\d+$',application_check='hanos-rendered',report_index_scope=True,inventory_scope_complete=True,discovery_scope='All four observed job links in the official HR department list; excludes other departments and group brands.',max_requests=100,collection_seconds=160)
    configure('ikea-ingka-group',adapter='employer-index',allowed_hosts=['jobs.ikea.com','ikea.avature.net'],index_urls=['https://jobs.ikea.com/en/location/jobs/22908/2750405-2755249-2755251/4/1'],job_url_pattern=r'^https://jobs\.ikea\.com/en/job/groningen/[^/]+/\d+/\d+$',index_job_count_pattern=r'(\d+) jobs in Groningen',employer_tokens=['ingka'],application_check='avature-linked',report_index_scope=True,inventory_scope_complete=True,discovery_scope='Official Groningen city list, all observed postings; link count must equal the live published total. Province sites outside the city require separate discovery.',max_requests=100,collection_seconds=180)
    configure('fotofabriek',adapter='employer-index',index_urls=['https://www.werkenbijfotofabriek.nl/jobs'],job_url_pattern=r'^https://www\.werkenbijfotofabriek\.nl/jobs/detail/[^/?]+-\d+$',job_id_pattern=r'-(\d+)$',index_page_pattern=r'^https://www\.werkenbijfotofabriek\.nl/jobs/page/\d+\?',page_format='odoo-visible',reviewed_workplace_labels={'Fotofabriek':dict(city='Groningen',country='NL',address_evidence='Osloweg 75, 9723 BJ Groningen')},application_check='odoo',report_index_scope=True,inventory_scope_complete=True,discovery_scope='Official HTML vacancy list and all observed numbered pages; each form identifies vacancy and workplace label, resolved to the published Groningen campus address.',max_requests=140,collection_seconds=240)
    # Shared group feed already exists. Reuse it for the parent and shipyard;
    # do not download or count a second group feed.
    shared='auto-wagenborg-passagiersdiensten'
    if shared in source_by_id:
        source_by_id[shared]['employer']='Royal Wagenborg'
        wpd=next(c for c in companies if c['id']=='wagenborg-passagiersdiensten')
        wpd['aliases']=sorted(set(wpd.get('aliases',[])+['Royal Wagenborg']))
        removed=set()
        for cid in ('royal-wagenborg','royal-niestern-sander'):
            company=next(c for c in companies if c['id']==cid)
            removed.update(sid for sid in company['source_ids'] if sid!=shared);company['source_ids']=[shared]
        sources=[s for s in sources if s['id'] not in removed]
    return companies,sources,regional


def main():
    rows=[]
    for filename in ('groningen-research-city.json','groningen-research-municipalities.json'):
        rows.extend(read(ROOT/'docs'/filename,{})['employers'])
    companies,sources,regional=integrate(read(ROOT/'data/companies.json',[]),read(ROOT/'data/sources.json',[]),read(ROOT/'data/groningen-geography.json',{}),rows)
    write(ROOT/'data/companies.json',companies);write(ROOT/'data/sources.json',sources)
    write(ROOT/'data/groningen-employers.json',regional)
    print(len(regional),'provincial employers;',sum(r['size']['qualification']=='verified_50_plus' for r in regional),'qualified')

if __name__=='__main__':main()
