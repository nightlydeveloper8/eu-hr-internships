"""Employer-first discovery inventory and honest geographic coverage reports."""
from collections import Counter
import hashlib
import re
from urllib.parse import urlsplit, urljoin
from .classify import COUNTRIES, canonical_url, fold
from .employer_pages import PageParser

def company_key(name):
    return re.sub(r'[^a-z0-9]+','-',fold(name)).strip('-')

def validate_registry(companies,geography,sources):
    units={u['code']:u for u in geography['units']};source_ids={s['id'] for s in sources};seen=set()
    for c in companies:
        if c['id'] in seen:raise ValueError('Duplicate company ID')
        seen.add(c['id']);canonical_url(c['career_url'])
        if not c.get('evidence_url'):raise ValueError('Company requires a provenance URL')
        for source_id in c.get('source_ids',[]):
            if source_id not in source_ids:raise ValueError('Unknown source reference')
        for place in c.get('workplaces',[]):
            if place['country'] not in COUNTRIES:raise ValueError('Not an EU workplace')
            for field,level in [('region_code',2),('subregion_code',3)]:
                code=place.get(field)
                if code and (code not in units or units[code]['level']!=level or units[code]['country']!=place['country']):raise ValueError('Invalid workplace geography')
            if place.get('location_confidence')=='confirmed' and not place.get('evidence_url'):raise ValueError('Confirmed workplace requires evidence')
    return True

def discover_channels(company,client):
    """Inspect only the declared career page; propose channels, never auto-enable."""
    url=canonical_url(company['career_url']);host=urlsplit(url).hostname
    body,_,final=client.request(url)
    if urlsplit(final).hostname not in company.get('approved_career_hosts',[host]):raise ValueError('Career page redirected to an unreviewed host')
    parser=PageParser();parser.feed(body.decode('utf-8','replace'));channels=[]
    providers={'job-boards.greenhouse.io':'greenhouse','boards.greenhouse.io':'greenhouse','jobs.lever.co':'lever','jobs.eu.lever.co':'lever','jobs.ashbyhq.com':'ashby','careers.smartrecruiters.com':'smartrecruiters','jobs.smartrecruiters.com':'smartrecruiters'}
    for href in [final]+parser.links:
        target=urljoin(final,href);parts=urlsplit(target)
        if parts.scheme!='https' or parts.hostname not in providers:continue
        path=[p for p in parts.path.split('/') if p]
        if not path:continue
        entry={'adapter':providers[parts.hostname],'board':path[0],'career_url':canonical_url(target),'status':'requires-access-review'}
        if not any((x['adapter'],x['board'])==(entry['adapter'],entry['board']) for x in channels):channels.append(entry)
    return channels

def region_codes_for_job(job,companies):
    # Assign only a matching observed workplace city; never infer all offices from an employer name.
    city=fold(job.get('city') or '');employer=company_key(job['employer']);codes=set()
    for company in companies:
        if company_key(company['name'])!=employer:continue
        for place in company.get('workplaces',[]):
            if place.get('location_confidence')!='confirmed' or place['country'] not in job['countries']:continue
            if re.search(r'\b'+re.escape(fold(place['city']))+r'\b',city) and place.get('region_code'):codes.add(place['region_code'])
    return sorted(codes)

def coverage_report(companies,geography,sources,jobs,stamp):
    enabled={s['id'] for s in sources if s.get('enabled')};validate_registry(companies,geography,sources)
    rows=[]
    for unit in geography['units']:
        if unit['level'] not in (2,3) or unit.get('extra_region'):continue
        field='region_code' if unit['level']==2 else 'subregion_code'
        located=[c for c in companies if any(p.get(field)==unit['code'] and p.get('location_confidence')=='confirmed' for p in c.get('workplaces',[]))]
        monitored=[c for c in located if enabled.intersection(c.get('source_ids',[]))]
        open_jobs=[j for j in jobs if j['status']=='open' and unit['level']==2 and unit['code'] in j.get('region_codes',[])]
        rows.append(dict(code=unit['code'],name=unit['name'],country=unit['country'],level=unit['level'],companies_located=len(located),companies_monitored=len(monitored),open_listings=len(open_jobs) if unit['level']==2 else None,listing_mapping='region only; subregion not inferred' if unit['level']==3 else 'confirmed employer/city match',company_ids=[c['id'] for c in located],status='not-researched' if not located else 'monitoring' if monitored else 'employers-identified'))
    return dict(generated_at=stamp,exhaustive=False,company_count=len(companies),monitored_companies=sum(bool(enabled.intersection(c.get('source_ids',[]))) for c in companies),regions=rows,countries=[dict(code=c,name=n,companies_identified=sum(c in x.get('target_countries',[]) or any(p['country']==c for p in x.get('workplaces',[])) for x in companies),regions_with_employers=sum(r['country']==c and r['level']==2 and r['companies_located']>0 for r in rows)) for c,n in COUNTRIES.items()],limitations=['Candidate operating countries are not confirmed workplaces.','Corporate presence is not evidence of an HR internship opening.','Unknown regional placement remains unknown; zero monitoring is not zero openings.'])

def discovery_queue(geography,report):
    counts={r['code']:r['companies_located'] for r in report['regions']};queue=[]
    for unit in geography['units']:
        if unit['level'] not in (2,3) or unit.get('extra_region'):continue
        score=(1000 if unit['country']=='NL' else 100)+(30 if unit['level']==2 else 0)-min(counts.get(unit['code'],0)*3,30)
        queue.append(dict(territory=unit['code'],country=unit['country'],name=unit['name'],level=unit['level'],priority=score,companies_identified=counts.get(unit['code'],0),target_companies=20 if unit['country']=='NL' and unit['level']==2 else 10,status='research-required',research_queries=[f'"{unit["name"]}" employers investment agency business directory',f'"{unit["name"]}" human resources internship employer careers'],note='Planning target, not a promise of openings; use official regional agencies, chambers, university employer lists and employer sites.'))
    return sorted(queue,key=lambda x:(-x['priority'],x['country'],x['territory']))
