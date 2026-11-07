"""Offline Issue #10 snapshot audit. No network, collection or dataset mutation."""
import argparse,json,subprocess,sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from collector.verification import verified_job
from collector.company_registry import country_research_progress
ROOT=Path(__file__).resolve().parents[1]
BASE='3ec0afd'

def diagnose(ref=BASE):
    def load(name):
        return json.loads(subprocess.check_output(['git','show',ref+':'+name],cwd=ROOT))
    catalog=load('data/catalog.json');coverage=load('data/coverage.json')
    sources=load('data/sources.json');companies=load('data/companies.json');stamp=catalog['updated_at']
    jobs=catalog['jobs'];verified=[j for j in jobs if verified_job(j,stamp)]
    report={ 'baseline_ref':ref,'baseline_catalog_updated_at':stamp,
        'catalog':dict(historical=len(jobs),verified=len(verified),
            verified_types=dict(Counter(j['internship_type'] for j in verified)),
            unverified=sum(j['status']!='closed' and not verified_job(j,stamp) for j in jobs),
            closed=sum(j['status']=='closed' for j in jobs),
            english_documented=sum(j.get('language_requirements',{}).get('english_support')=='documented' for j in verified),
            english_alone_documented=sum(j.get('language_requirements',{}).get('english_sufficiency')=='documented' for j in verified)),
        'sources':[]}
    for sid in ['auto-tilburg-university','auto-randstad-italia-spa']:
        rows=[j for j in jobs if j['source_id']==sid]
        run=next(r for r in coverage['sources'] if r['id']==sid)
        config=next(s for s in sources if s['id']==sid)
        fields=['status','checked_at','duration_seconds','requests','pages_read','rendered_pages',
            'records_inspected','job_urls_discovered','pending_urls','cache_hits','complete',
            'closure_complete','inventory_complete','page_failures','page_errors_truncated','methods']
        report['sources'].append(dict(id=sid,budget_seconds=config['collection_seconds'],
            max_requests=config['max_requests'],max_pages=config['max_pages'],
            catalog_records=len(rows),reasons=dict(Counter(j['verification']['reason'] for j in rows)),
            catalog_hosts=dict(Counter(urlsplit(j['url']).hostname for j in rows)),
            run={k:run[k] for k in fields if k in run}))
    plan=load('data/employer-research-plan.json')
    progress=country_research_progress(companies,sources,plan,coverage['sources'],stamp)
    enabled={s['id'] for s in sources if s.get('enabled')}
    report['employers']=dict(configured=sum(bool(enabled.intersection(c['source_ids'])) for c in companies),
        complete_recent_employer_country_relationships=sum(c['companies_monitored_in_country'] for c in progress),
        baseline_target=sum(c['baseline_target'] for c in progress),
        definition='Configured employers and complete/recent employer-country inventories have different units and denominators.')
    registry={s['id']:s for s in sources};shortlist=[]
    for job in jobs:
        if job.get('verification',{}).get('reason')!='No available vacancy-specific application entry established':continue
        source=registry[job['source_id']]
        if source['id'] in ['auto-tilburg-university','auto-randstad-italia-spa']:continue
        if urlsplit(job['url']).hostname not in source['allowed_hosts']:continue
        # Configured hosts are only a screening hint, not fresh ownership/application proof.
        score=(source['adapter']!='universal-employer',bool(job.get('published_at')),job.get('published_at') or job['first_discovered_at'])
        shortlist.append((score,dict(id=job['id'],employer=job['employer'],url=job['url'],source_id=source['id'],
            adapter=source['adapter'],published_at=job.get('published_at'),
            first_discovered_at=job['first_discovered_at'],
            reason='Configured host, HR role already classified; individually review current employer, deadline and actual application entry. No promotion without policy-v2 evidence.')))
    report['application_review_shortlist']=[r for _,r in sorted(shortlist,key=lambda x:x[0],reverse=True)[:5]]
    report['shortlist_limitations']='Offline triage only; no claim that these old observations remain open, official ownership is current, or a conversion will succeed.'
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--ref',default=BASE);p.add_argument('--output',type=Path);a=p.parse_args()
    result=diagnose(a.ref)
    if a.output:a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print('Baseline:',result['catalog'])
    print('Time-budget records:',{s['id']:s['reasons'].get('Time budget exhausted; checkpoint retained',0) for s in result['sources']})
