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
        seen.add(c['id'])
        if not c.get('career_url') and not c.get('website_url'):raise ValueError('Company requires an official website or career URL')
        if c.get('career_url'):canonical_url(c['career_url'])
        if c.get('website_url'):canonical_url(c['website_url'])
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
    if not company.get('career_url'):return []
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
        if employer not in {company_key(n) for n in [company['name']]+company.get('aliases',[])}:continue
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
    return dict(generated_at=stamp,exhaustive=False,company_count=len(companies),career_pages_recorded=sum(bool(c.get('career_url')) for c in companies),career_pages_verified_this_mapping=sum(c.get('career_check',{}).get('status')=='reachable' for c in companies),monitored_companies=sum(bool(enabled.intersection(c.get('source_ids',[]))) for c in companies),regions=rows,countries=[dict(code=c,name=n,companies_identified=sum(c in x.get('target_countries',[]) or any(p['country']==c for p in x.get('workplaces',[])) for x in companies),regions_with_employers=sum(r['country']==c and r['level']==2 and r['companies_located']>0 for r in rows)) for c,n in COUNTRIES.items()],limitations=['Candidate operating countries are not confirmed workplaces.','Corporate presence is not evidence of an HR internship opening.','Unknown regional placement remains unknown; zero monitoring is not zero openings.'])

def country_research_progress(companies,sources,plan,source_reports=None,stamp=None):
    """Operational quotas require recent complete collection in the actual country."""
    from datetime import datetime,timezone,timedelta
    moment=datetime.fromisoformat(stamp) if stamp else datetime.now(timezone.utc)
    cutoff=moment-timedelta(hours=plan.get('collection_freshness_hours',48))
    successful={}
    for report in source_reports or []:
        try:checked=datetime.fromisoformat(report['checked_at'])
        except (KeyError,TypeError,ValueError):continue
        if report.get('status')=='ok' and checked.tzinfo and checked>=cutoff:successful[report['id']]=report
    enabled={s['id'] for s in sources if s.get('enabled')};result=[]
    for country in plan['countries']:
        code=country['code']
        candidates=[c for c in companies if code in c.get('target_countries',[]) or any(p['country']==code for p in c.get('workplaces',[])) or any(code in successful.get(sid,{}).get('observed_countries',[]) for sid in c.get('source_ids',[]))]
        located=[c for c in candidates if any(p['country']==code and p.get('location_confidence')=='confirmed' for p in c.get('workplaces',[]))]
        reachable=[c for c in located if c.get('career_check',{}).get('status')=='reachable' or enabled.intersection(c.get('source_ids',[]))]
        # Configured sources may cover a different country; success in this country
        # requires a later source/country audit and is not implied here.
        monitored=[c for c in located if enabled.intersection(c.get('source_ids',[]))]
        active=[c for c in candidates if any(sid in enabled and sid in successful and code in successful[sid].get('observed_countries',[]) for sid in c.get('source_ids',[]))]
        result.append(dict(code=code,name=country['name'],baseline_target=country['baseline_target'],expansion_target=country['expansion_target'],companies_identified=len(candidates),companies_located=len(located),companies_with_located_career_channel=len(reachable),located_employers_with_monitoring_configured=len(monitored),companies_monitored_in_country=len(active),baseline_gap=max(0,country['baseline_target']-len(active)),expansion_gap=max(0,country['expansion_target']-len(active)),size_unknown=sum(not c.get('employee_size_evidence') for c in candidates),status='baseline-reached' if len(active)>=country['baseline_target'] else 'integration-required'))
    return result

def discovery_queue(geography,report,plan=None):
    counts={r['code']:r['companies_located'] for r in report['regions']};queue=[]
    progress={c['code']:c for c in report['countries']}
    policies={c['code']:c for c in (plan or {}).get('countries',[])}
    regions={code:sorted(u['code'] for u in geography['units'] if u['country']==code and u['level']==2 and not u.get('extra_region')) for code in progress}
    for unit in geography['units']:
        if unit['level'] not in (2,3) or unit.get('extra_region'):continue
        country=progress[unit['country']];policy=policies.get(unit['country'],{})
        baseline=country.get('baseline_target',100);confirmed=country.get('companies_located',0)
        active=country.get('companies_monitored_in_country',0)
        # Deficit ratio first, then unresearched regions; no fixed country bonus.
        expansion=country.get('expansion_target',policy.get('expansion_target',500))
        active_target=baseline if active<baseline else expansion
        gap_ratio=max(0,active_target-active)/active_target
        score=(10000 if active<baseline else 0)+round(gap_ratio*10000)+(100 if unit['level']==2 else 0)-min(counts.get(unit['code'],0)*3,90)
        allocation=None
        if unit['level']==2:
            codes=regions[unit['country']];base,remainder=divmod(baseline,len(codes))
            allocation=base+(codes.index(unit['code'])<remainder)
        terms=policy.get('research_terms',['medium sized companies','human resources internship'])
        queue.append(dict(territory=unit['code'],country=unit['country'],name=unit['name'],level=unit['level'],priority=score,companies_identified=counts.get(unit['code'],0),country_confirmed_employers=confirmed,country_baseline_target=baseline,country_expansion_target=expansion,country_active_target=active_target,country_monitored_employers=active,country_baseline_gap=max(0,baseline-active),target_companies=allocation,status='research-required',research_queries=[f'"{unit["name"]}" {terms[0]} chamber directory',f'"{unit["name"]}" industrial park cluster employers',f'"{unit["name"]}" {terms[1]}'],note='Provisional regional allocation of the national monitored-employer milestone, not a market estimate. Rebalance with documented employment data; regional company counts can overlap. NUTS3 tasks have no additive quota. At least 60% of new research targets 50–999 employee businesses; size and workplace require evidence.'))
    return sorted(queue,key=lambda x:(-x['priority'],x['country'],x['territory']))


def integration_queue(companies,sources,source_reports):
    registry={s['id']:s for s in sources};runs={r['id']:r for r in source_reports};rows=[]
    for company in companies:
        enabled=[registry[sid] for sid in company.get('source_ids',[]) if sid in registry and registry[sid].get('enabled')]
        state='collecting' if enabled else 'integration-required' if company.get('career_url') else 'career-discovery-required'
        if enabled and any(runs.get(s['id'],{}).get('status')!='ok' for s in enabled):state='collection-review-required'
        blocked=[registry[sid].get('review_notes') for sid in company.get('source_ids',[]) if sid in registry and not registry[sid].get('enabled') and registry[sid].get('review_notes')]
        rows.append(dict(company_id=company['id'],name=company['name'],candidate_countries=company.get('target_countries',[]),state=state,career_url=company.get('career_url'),source_ids=company.get('source_ids',[]),access_blocks=blocked,next_action='Check source completeness, country coverage and freshness' if enabled else 'Review public recruiting system, HTML pagination and permitted rendered pages; implement and run extractor' if company.get('career_url') else 'Locate official recruiting channel, including externally hosted ATS'))
    return sorted(rows,key=lambda r:(r['state']=='collecting',r['name']))
