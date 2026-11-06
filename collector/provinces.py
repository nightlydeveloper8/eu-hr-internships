"""Shared municipal coverage for researched Dutch provinces."""
from collections import Counter
from datetime import datetime, timedelta
from .company_registry import company_key
from .classify import fold
from .pipeline import ROOT, read, write, now


def coverage(companies,sources,runs,jobs,geography,stamp,opportunities=None,*,research_key="friesland_research",region_code="NL12",province="Fryslân"):
    cutoff=datetime.fromisoformat(stamp)-timedelta(hours=48)
    def verified(job):
        try:return job.get('link_status')=='verified' and cutoff <= datetime.fromisoformat(job['last_verified_at']) <= datetime.fromisoformat(stamp)
        except (KeyError,TypeError,ValueError):return False
    enabled={s['id'] for s in sources if s.get('enabled')}
    reports={r['id']:r for r in runs};rows=[]
    for company in companies:
        research=company.get(research_key)
        if not research:continue
        ids=sorted(enabled.intersection(company.get('source_ids',[])))
        attempts=[reports[sid] for sid in ids if sid in reports]
        def fresh(r):
            try:return datetime.fromisoformat(r['checked_at'])>=cutoff
            except (KeyError,TypeError,ValueError):return False
        recent=[r for r in attempts if fresh(r)]
        if not ids:state='unconfigured'
        elif len(recent)!=len(ids):state='not-recently-checked'
        elif all(r.get('status')=='ok' for r in recent):state='collected'
        elif any(r.get('records_inspected',0) for r in recent):state='partial'
        elif any(r.get('status')=='partial' for r in recent):state='discovery-incomplete'
        else:state='blocked-or-failed'
        names={company_key(n) for n in [company['name']]+company.get('aliases',[])}
        local_jobs=[j for j in jobs if j.get('status')=='open' and j.get('internship_type')=='internship' and region_code in j.get('region_codes',[]) and verified(j) and (j['source_id'] in ids or company_key(j['employer']) in names)]
        places=[p for p in company.get('workplaces',[]) if p.get('region_code')==region_code and p.get('location_confidence')=='confirmed']
        rows.append(dict(company_id=company['id'],name=company['name'],group_name=research.get('group_name'),career_url=company.get('career_url') or company.get('website_url'),size=research.get('size',{}),employer_type=research.get('employer_type','private'),workplaces=places,source_ids=ids,state=state,attempted_recently=len(recent)==len(ids) and bool(ids),last_attempt_at=max((r.get('checked_at','') for r in attempts),default=None),public_job_records=sum(r.get('records_inspected',0) for r in recent),verified_hr_internship_ids=sorted(j['id'] for j in local_jobs),errors=[dict(source_id=r['id'],message=r.get('error') or str(r.get('page_errors',[])[:3])) for r in recent if r.get('error') or r.get('page_errors')]))
    municipalities=[]
    for m in geography.get('municipalities',[]):
        employers=[r for r in rows if any(p.get('municipality_code')==m['cbs_code'] for p in r['workplaces'])]
        local_ids={jid for r in employers for jid in r['verified_hr_internship_ids'] for j in jobs if j['id']==jid and any(p.get('municipality_code')==m['cbs_code'] and p.get('city') and fold(j.get('city') or '')==fold(p['city']) for p in r['workplaces'])}
        municipalities.append(dict(verified_hr_internship_ids=sorted(local_ids),verified_hr_internships=len(local_ids),code=m['cbs_code'],name=m['name'],settlements=m['settlement_count'],employers=len(employers),qualified_employers=sum(r['size'].get('qualification')=='verified_50_plus' for r in employers),size_unknown=sum(r['size'].get('qualification','unknown')=='unknown' for r in employers),below_threshold=sum(r['size'].get('qualification')=='below_50' for r in employers),collection_states=dict(Counter(r['state'] for r in employers)),company_ids=sorted(r['company_id'] for r in employers)))
    job_ids={jid for r in rows for jid in r['verified_hr_internship_ids']}
    qualified={r['company_id'] for r in rows if r['size'].get('qualification')=='verified_50_plus'}
    qualified_jobs={jid for r in rows if r['company_id'] in qualified for jid in r['verified_hr_internship_ids']}
    return dict(schema_version=1,generated_at=stamp,province=province,region_code=region_code,exhaustive=False,geography_reference_date=geography.get('administrative_reference_date'),employee_threshold=50,size_counting='Documented employer/group qualification; group headcount is never assigned to a local establishment. Unknown size stays separate.',municipal_counting='A distinct employer counts once provincially and once in each documented municipality; municipality totals overlap.',summary=dict(employers=len(rows),qualified_employers=len(qualified),distinct_groups=len({company_key(r.get('group_name') or r['name']) for r in rows}),qualified_groups=len({company_key(r.get('group_name') or r['name']) for r in rows if r['company_id'] in qualified}),size_unknown=sum(r['size'].get('qualification','unknown')=='unknown' for r in rows),below_threshold=sum(r['size'].get('qualification')=='below_50' for r in rows),municipalities=len(municipalities),municipalities_with_qualified_employers=sum(m['qualified_employers']>0 for m in municipalities),configured=sum(bool(r['source_ids']) for r in rows),attempted_recently=sum(r['attempted_recently'] for r in rows),collection_states=dict(Counter(r['state'] for r in rows)),qualified_collection_states=dict(Counter(r['state'] for r in rows if r['company_id'] in qualified)),verified_hr_internships=len(job_ids),verified_hr_internships_qualified_employers=len(qualified_jobs)),municipalities=municipalities,employers=rows,verified_hr_internship_ids=sorted(job_ids),research_opportunities=opportunities or [],schedule=dict(workflow='collect.yml',cron_utc='17 6 * * *',note='Daily hosted runner; Europe/Amsterdam 07:17 winter / 08:17 summer. Scheduled start may be delayed by GitHub.'),limitations=['Employer mapping is still expanding; no complete business-register denominator is available.','Configured, attempted, fully read observed inventory, partial and blocked sources are distinct.','No current vacancy is inferred from company presence or a general internship programme.'])


def generate_province(slug):
    path=ROOT/'data'/(slug+'-geography.json')
    if not path.exists():return
    geography=read(path,{})
    report=coverage(read(ROOT/'data/companies.json',[]),read(ROOT/'data/sources.json',[]),
        read(ROOT/'data/coverage.json',{}).get('sources',[]),read(ROOT/'data/catalog.json',{}).get('jobs',[]),
        geography,now(),read(ROOT/'data'/(slug+'-opportunities.json'),[]),research_key=slug+'_research',
        region_code=geography['province']['nuts2_code'],province=geography['province']['official_name'])
    write(ROOT/'data'/(slug+'-coverage.json'),report)
    return report


def generate_all():
    return {slug:generate_province(slug) for slug in ('friesland','groningen')
        if (ROOT/'data'/(slug+'-geography.json')).exists()}


if __name__=='__main__':
    for slug,report in generate_all().items():print(slug,report['summary'])
