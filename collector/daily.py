"""Provision every employer, collect in bounded parallel shards, merge once.

    python -m collector.daily provision
    python -m collector.daily collect --shard 0 --shards 8 --run-id manual-2026-11-06
    python -m collector.daily merge --inputs .staging/results --shards 8 --run-id manual-2026-11-06
"""
import argparse,copy,hashlib,json,logging,os,re,time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor,as_completed
from datetime import datetime,timedelta,timezone
from pathlib import Path
from urllib.parse import urlsplit
from .pipeline import ROOT,read,write,now,process_source,finalize,deduplicate
from .classify import COUNTRIES,canonical_url
from .runtime import BudgetClient,PageCache
LOG=logging.getLogger(__name__)
MAX_SHARD_AGE=timedelta(hours=24)
CLOCK_SKEW=timedelta(minutes=5)

def collection_run_id(shards,run_id=None):
    value=run_id if run_id is not None else os.environ.get('COLLECTOR_RUN_ID')
    if value is None:
        if shards>1:raise ValueError('Multi-shard collection requires --run-id or COLLECTOR_RUN_ID')
        return None
    if not isinstance(value,str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._:/-]{0,199}',value):
        raise ValueError('Invalid collector run ID')
    return value

def collection_time(value):
    try:
        result=datetime.fromisoformat(value.replace('Z','+00:00'))
        if result.tzinfo is None:raise ValueError('Timezone required')
        return result.astimezone(timezone.utc)
    except (AttributeError,TypeError,ValueError) as exc:
        raise ValueError('Invalid timezone-aware collection timestamp') from exc

def validate_shard_times(payload,clock):
    started=collection_time(payload.get('started_at'));finished=collection_time(payload.get('finished_at'))
    if started>finished or started<clock-MAX_SHARD_AGE or finished>clock+CLOCK_SKEW:
        raise ValueError('Expired, future or reversed shard timestamps; previous catalog retained')
    for part in payload.get('parts',[]):
        checked=collection_time(part.get('report',{}).get('checked_at'))
        if not started-CLOCK_SKEW<=checked<=finished+CLOCK_SKEW:
            raise ValueError('Source timestamp outside shard collection interval; previous catalog retained')
    return finished

def provision(companies,sources):
    """Idempotently attach an actual crawler to every unserved employer."""
    companies=copy.deepcopy(companies);sources=copy.deepcopy(sources)
    by_id={s['id']:s for s in sources}
    for company in companies:
        active=[by_id[s] for s in company.get('source_ids',[]) if s in by_id and by_id[s].get('enabled')]
        if active:continue
        starts=list(dict.fromkeys(canonical_url(u) for u in [company.get('career_url'),company.get('website_url')] if u))
        if not starts:raise ValueError('Employer has no public starting URL: '+company['id'])
        sid='auto-'+company['id']
        if sid in by_id:raise ValueError('Automatic source ID collision: '+sid)
        source=dict(id=sid,company_id=company['id'],employer=company['name'],adapter='universal-employer',enabled=True,start_urls=starts,career_url=company.get('career_url') or starts[0],allowed_hosts=sorted({urlsplit(u).hostname for u in starts}),target_countries=company.get('target_countries',[]),max_pages=70,max_requests=110,collection_seconds=120,max_navigation_depth=3,max_render_pages=4,permission_basis='Declared official website/career page and observed public recruiting links; robots checked at runtime; no authentication or challenge bypass',status='automatic-collection-pending')
        sources.append(source);by_id[sid]=source;company.setdefault('source_ids',[]).append(sid)
    return companies,sources

def provision_files():
    companies,sources=provision(read(ROOT/'data/companies.json',[]),read(ROOT/'data/sources.json',[]))
    write(ROOT/'data/companies.json',companies);write(ROOT/'data/sources.json',sources)
    return companies,sources

def shard_for(source_id,shards):return int(hashlib.sha256(source_id.encode()).hexdigest()[:12],16)%shards

def fingerprint(sources):return hashlib.sha256(json.dumps(sources,sort_keys=True,ensure_ascii=False).encode()).hexdigest()

def collect_shard(shard=0,shards=8,workers=6,output=None,source_ids=None,seconds=None,run_id=None):
    if shards<1 or not 0<=shard<shards:raise ValueError('Invalid shard')
    run_id=collection_run_id(shards,run_id)
    companies,sources=provision_files();enabled=[s for s in sources if s.get('enabled')]
    if source_ids and set(source_ids)-{s['id'] for s in enabled}:raise ValueError('Unknown or disabled source IDs: '+str(sorted(set(source_ids)-{s['id'] for s in enabled})))
    selected=[s for s in enabled if shard_for(s['id'],shards)==shard and (not source_ids or s['id'] in source_ids)]
    counts={r['id']:r.get('collected',0) for r in read(ROOT/'data/coverage.json',{}).get('sources',[])}
    known={}
    for job in read(ROOT/'data/catalog.json',{}).get('jobs',[]):
        if job.get('status')!='closed':known.setdefault(job['source_id'],[]).append(job['url'])
    regional={}
    for company in companies:
        research=[company[key] for key in ('friesland_research','groningen_research') if company.get(key)]
        if research:
            priority=0 if any(r.get('size',{}).get('qualification')=='verified_50_plus' for r in research) else 1
            for sid in company.get('source_ids',[]):regional[sid]=min(regional.get(sid,2),priority)
    selected.sort(key=lambda s:(regional.get(s['id'],2),s['id'] not in known,s['adapter']=='universal-employer',-counts.get(s['id'],0),s['id']))
    stamp=now();parts=[]
    company_for={sid:c for c in companies for sid in c.get('source_ids',[])}
    def work(source):
        source=dict(source,known_job_urls=known.get(source['id'],[]))
        started=time.monotonic();client=BudgetClient(seconds=seconds or source.get('collection_seconds',180 if source['adapter'] in ('employer-sitemap','employer-index') else 120),max_requests=source.get('max_requests',180))
        part=process_source(source,client,stamp,counts.get(source['id'],0),cache=PageCache(source['id']))
        if part['report']['status']=='failed' and source['adapter']!='universal-employer' and client.remaining()>15:
            c=company_for.get(source['id'],{});starts=list(dict.fromkeys(u for u in [source.get('career_url'),c.get('website_url')] if u))
            if starts:
                fallback=dict(source,adapter='universal-employer',start_urls=starts,max_pages=60,max_navigation_depth=3,max_render_pages=4,allowed_hosts=sorted(set(source['allowed_hosts'])|{urlsplit(u).hostname for u in starts}))
                primary_error=part['report'].get('error');part=process_source(fallback,client,stamp,verify=True,cache=PageCache(source['id']))
                part['report'].update(primary_adapter=source['adapter'],primary_error=primary_error)
        report=part['report'];report.update(duration_seconds=round(time.monotonic()-started,2),requests=client.requests,bytes_read=client.bytes,shard=shard)
        return part
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures={pool.submit(work,s):s for s in selected}
        for future in as_completed(futures):
            source=futures[future]
            try:part=future.result()
            except Exception as exc:part=dict(report=dict(id=source['id'],employer=source['employer'],adapter=source['adapter'],checked_at=stamp,status='failed',error=str(exc)[:400]),jobs=[],closure_eligible=[])
            parts.append(part)
            LOG.info('Shard %s: %s/%s employers; %s %s; %s HR matches',shard,len(parts),len(selected),source['employer'],part['report']['status'],len(part['jobs']))
            # A killed runner leaves a usable diagnostic checkpoint, never a partial catalog.
            payload=dict(schema_version=1,run_id=run_id,shard=shard,shards=shards,registry_fingerprint=fingerprint(enabled),started_at=stamp,finished_at=now(),expected_source_ids=sorted(s['id'] for s in selected),parts=parts,complete=len(parts)==len(selected))
            write(output or ROOT/'.staging/results'/('shard-'+str(shard)+'.json'),payload)
    if not selected:
        payload=dict(schema_version=1,run_id=run_id,shard=shard,shards=shards,registry_fingerprint=fingerprint(enabled),started_at=stamp,finished_at=now(),expected_source_ids=[],parts=[],complete=True)
        write(output or ROOT/'.staging/results'/('shard-'+str(shard)+'.json'),payload)
    return payload

def employer_report(companies,sources,parts,stamp,catalog_jobs=None):
    unique_matches=Counter(j['source_id'] for j in (catalog_jobs if catalog_jobs is not None else deduplicate([j for p in parts for j in p.get('jobs',[])])) if j.get('status')!='closed')
    reports={p['report']['id']:p['report'] for p in parts};enabled={s['id'] for s in sources if s.get('enabled')};rows=[]
    for c in companies:
        ids=sorted(enabled.intersection(c['source_ids']));runs=[reports[i] for i in ids if i in reports]
        if len(runs)!=len(ids) or not ids:state='not-attempted'
        elif all(r['status']=='ok' for r in runs):state='collected' if any(r.get('collected',0) for r in runs) else 'verified-empty'
        elif any(r.get('records_inspected',0) for r in runs):state='partial'
        elif any(r['status']=='partial' for r in runs):state='discovery-incomplete'
        else:state='blocked-or-failed'
        rows.append(dict(company_id=c['id'],name=c['name'],candidate_countries=c.get('target_countries',[]),state=state,source_ids=ids,attempted=len(runs)==len(ids) and bool(ids),checked_at=max((r['checked_at'] for r in runs),default=None),public_job_records=sum(r.get('records_inspected',0) for r in runs),matching_hr_positions=sum(unique_matches[sid] for sid in ids),pages_read=sum(r.get('pages_read',0) for r in runs),pending_urls=sum(r.get('pending_urls',0) for r in runs),errors=[dict(source_id=r['id'],error=r.get('error') or str(r.get('page_errors',[])[:3])) for r in runs if r.get('error') or r.get('page_errors')],next_attempt='next daily run'))
    summary=dict(Counter(r['state'] for r in rows));summary.update(companies=len(companies),configured=sum(bool(enabled.intersection(c['source_ids'])) for c in companies),attempted=sum(r['attempted'] for r in rows))
    countries=[dict(code=code,name=name,companies_identified=sum(code in r['candidate_countries'] for r in rows),states=dict(Counter(r['state'] for r in rows if code in r['candidate_countries']))) for code,name in COUNTRIES.items()]
    return dict(generated_at=stamp,exhaustive=False,summary=summary,country_counting='Candidate country membership; multi-country employers counted once per country. Actual job locations require published evidence.',countries=countries,employers=rows)

def merge(inputs,shards=8,output=ROOT/'data',run_id=None):
    if shards<1:raise ValueError('Invalid shard count')
    run_id=collection_run_id(shards,run_id);clock=collection_time(now());finished_times=[]
    companies,sources=provision_files();enabled=[s for s in sources if s.get('enabled')];expected={s['id'] for s in enabled};seen=set();parts=[];payloads=[]
    for i in range(shards):
        files=list(Path(inputs).rglob('shard-'+str(i)+'.json'))
        if len(files)!=1:raise ValueError('Expected exactly one result for shard '+str(i))
        p=read(files[0],{});payloads.append(p)
        if p.get('run_id')!=run_id:raise ValueError('Shard belongs to another collection run; previous catalog retained')
        finished_times.append(validate_shard_times(p,clock))
        if p.get('shard')!=i or p.get('shards')!=shards or not p.get('complete') or p.get('registry_fingerprint')!=fingerprint(enabled):raise ValueError('Incomplete/stale shard '+str(i)+'; previous catalog retained')
        assigned={s for s in expected if shard_for(s,shards)==i}
        ids=[part['report']['id'] for part in p['parts']]
        if set(ids)!=assigned or len(ids)!=len(set(ids)) or set(ids)&seen:raise ValueError('Missing, duplicate or unexpected employer results in shard '+str(i))
        seen.update(ids);parts.extend(p['parts'])
    if seen!=expected:raise ValueError('Every enabled employer must be attempted before publishing')
    stamp=max(finished_times).isoformat()
    result,coverage=finalize(sources,enabled,read(output/'catalog.json',{'jobs':[]}),read(output/'coverage.json',{}),parts,stamp,output)
    employers=employer_report(companies,sources,parts,stamp,result['jobs'])
    write(output/'employer-collection.json',employers)
    LOG.info('All-employer collection: %s',employers['summary']);return result,coverage,employers

def main():
    p=argparse.ArgumentParser();p.add_argument('command',choices=['provision','collect','merge']);p.add_argument('--shard',type=int,default=0);p.add_argument('--shards',type=int,default=8);p.add_argument('--workers',type=int,default=6);p.add_argument('--output',type=Path);p.add_argument('--inputs',type=Path,default=ROOT/'.staging/results');p.add_argument('--sources',nargs='+');p.add_argument('--seconds',type=int);p.add_argument('--run-id',help='Shared ID for this collection run; defaults to COLLECTOR_RUN_ID');a=p.parse_args()
    logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(message)s')
    if a.command=='provision':
        c,s=provision_files();print(len(c),'employers;',sum(x.get('enabled',False) for x in s),'active collectors')
    elif a.command=='collect':collect_shard(a.shard,a.shards,a.workers,a.output,a.sources,a.seconds,a.run_id)
    else:merge(a.inputs,a.shards,a.output or ROOT/'data',a.run_id)
if __name__=='__main__':main()
