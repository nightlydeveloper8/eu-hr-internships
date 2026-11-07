import argparse
from collections import Counter
from datetime import datetime, timezone
import json
import logging
import os
import re
from pathlib import Path
from urllib.parse import urlsplit,parse_qs
from .adapters import Client, collect, enrich
from .classify import COUNTRIES, LANGUAGES, CATEGORIES, canonical_url, classify_role, country_codes, stable_id, workplace_languages, language_summary, advertisement_language, extract_metadata

ROOT=Path(__file__).resolve().parents[1]
LOG=logging.getLogger(__name__)

def now(): return datetime.now(timezone.utc).isoformat()
def read(path,default): return json.loads(path.read_text()) if path.exists() else default
def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix('.tmp')
    temp.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    os.replace(temp,path)

def allowed_url(url,source):
    cleaned=canonical_url(url)
    host=urlsplit(cleaned).hostname
    if host not in source['allowed_hosts']: raise ValueError('Unapproved job host: '+host)
    return cleaned

def reconcile(previous,current,successful,stamp):
    merged={j['id']:dict(j) for j in previous}
    for job in current:
        old=merged.get(job['id'],{})
        job['first_discovered_at']=old.get('first_discovered_at',job.get('first_discovered_at',stamp))
        job['missing_count']=0
        job.pop('missing_since',None)
        merged[job['id']]=job
    seen={j['id'] for j in current}
    for key,job in merged.items():
        if key in seen or job['source_id'] not in successful or job.get('status')=='closed': continue
        if job.get('last_missing_run')==stamp[:10]: continue
        job['missing_count']=job.get('missing_count',0)+1
        job['missing_since']=job.get('missing_since',stamp)
        job['last_missing_run']=stamp[:10]
        elapsed=(datetime.fromisoformat(stamp)-datetime.fromisoformat(job['missing_since'])).total_seconds()
        job['status']='closed' if job['missing_count']>=3 and elapsed>=48*3600 else 'unverified'
        if job.get('verification'):
            job['verification']=dict(job['verification'],state='closed' if job['status']=='closed' else 'incomplete',checked_at=stamp,reason='Missing from complete employer inventory; '+str(job['missing_count'])+' daily observations')
    return list(merged.values())

def posting_identity(job):
    if job.get('source_posting_id'):return 'posting:'+job['source_id']+':'+str(job['source_posting_id'])
    return posting_url_identity(job)

def posting_url_identity(job):
    p=urlsplit(job['url']);host=p.hostname or '';identifier=None
    # Public platform URLs expose stable IDs shared by their language mirrors.
    if host=='jobs.smartrecruiters.com':
        match=re.match(r'^/([^/]+)/(\d+)(?:-|/|$)',p.path)
        if match:return 'posting:'+job['source_id']+':smartrecruiters:'+match.group(1).lower()+':'+match.group(2)
    elif host=='careers-nl.jdepeets.com':
        identifier=(parse_qs(p.query).get('id') or [''])[0]
        if re.fullmatch(r'\d+',identifier):return 'posting:'+job['source_id']+':smartrecruiters:jacobsdouweegberts:'+identifier
        identifier=None
    if host=='careers.loreal.com':
        match=re.search(r'/\d+/(\d+)$',p.path);identifier=match.group(1) if match else None
    elif host.endswith('.intervieweb.it'):
        match=re.search(r'/jobs/[^/]*-(\d+)(?:/[a-z]{2})?/?$',p.path);identifier=match.group(1) if match else None
        if not identifier and p.path.endswith('/app.php'):
            query=parse_qs(p.query)
            if query.get('module')==['annunci']:
                match=re.search(r'-(\d+)$',(query.get('l') or [''])[0]);identifier=match.group(1) if match else None
    if identifier:return 'posting:'+job['source_id']+':'+host+':'+identifier
    return None

def apply_listing_reviews(jobs,reviews):
    excluded={canonical_url(r['url']) for r in reviews if r.get('decision')=='excluded'}
    pending={canonical_url(r['url']):r for r in reviews if r.get('decision')=='needs-verification'}
    result=[]
    for job in jobs:
        url=canonical_url(job['url'])
        if url in excluded:continue
        if url in pending:
            job=dict(job,status='unverified',link_status='review-required',review_note=pending[url]['reason'])
        result.append(job)
    return result

def application_identity_url(job):
    """Only reviewed vacancy-shaped application URLs can identify mirrors."""
    url=canonical_url(job.get('apply_url') or job['url']);p=urlsplit(url)
    if p.hostname in ('jobs.lever.co','jobs.eu.lever.co') and re.fullmatch(r'/[^/]+/[^/]+/apply',p.path):return url
    if re.fullmatch(r'/jobs/apply/(?:[^/]+-)?\d+',p.path):return url
    if '/External/' in p.path and (parse_qs(p.query).get('jobId') or [''])[0]:return url
    return None

def observation_time(job):
    values=[job.get('last_seen_at'),job.get('verification',{}).get('checked_at'),job.get('last_verified_at')]
    parsed=[]
    for value in values:
        try:
            date=datetime.fromisoformat(value.replace('Z','+00:00'))
            if date.tzinfo:parsed.append(date.timestamp())
        except (ValueError,TypeError,AttributeError):pass
    return max(parsed,default=0)

def deduplicate(jobs):
    by_key={};groups=[]
    for job in sorted(jobs,key=lambda j:j.get('first_discovered_at','')):
        keys={canonical_url(job['url'])}
        for identity in (posting_identity(job),posting_url_identity(job),application_identity_url(job)):
            if identity:keys.add(identity)
        # Exact vacancy URLs / official IDs / vacancy-specific application paths
        # identify mirrors. A general applicant portal never does.
        matches={by_key[k] for k in keys if k in by_key}
        if matches:
            index=min(matches);existing=groups[index]
            for other in sorted(matches-{index}):
                existing['members'].extend(groups[other]['members']);existing['keys'].update(groups[other]['keys']);groups[other]=None
            existing['members'].append(job);existing['keys'].update(keys)
        else:
            index=len(groups);existing=dict(members=[job],keys=keys);groups.append(existing)
        for key in existing['keys']:by_key[key]=index
    result=[]
    for group in groups:
        if group is None:continue
        members=group['members'];first=members[0]
        newest=max(members,key=lambda j:(observation_time(j),j.get('status')=='closed'))
        merged=dict(newest,id=first['id'],first_discovered_at=first.get('first_discovered_at'))
        verified=[m.get('last_verified_at') for m in members if m.get('last_verified_at')]
        if not merged.get('last_verified_at') and verified:merged['last_verified_at']=max(verified,key=lambda stamp:observation_time({'last_verified_at':stamp}))
        countries=sorted({c for m in members for c in m.get('countries',[])})
        if countries:merged.update(countries=countries,country=countries[0])
        if len(members)>1:merged['duplicate_source_ids']=sorted({sid for m in members for sid in [m['source_id']]+m.get('duplicate_source_ids',[])})
        result.append(merged)
    return result

def validate_catalog(data):
    assert data['schema_version']==1
    assert len(data['countries'])==27
    ids=set()
    for j in data['jobs']:
        assert j['id'] not in ids; ids.add(j['id'])
        assert j['country'] in COUNTRIES and all(c in COUNTRIES for c in j['countries'])
        assert j['categories'] and all(c in CATEGORIES for c in j['categories'])
        assert j['status'] in ('open','unverified','closed')
        assert j['internship_confidence']=='confirmed'
        canonical_url(j['url']); canonical_url(j['apply_url'])
        assert 'text' not in j and 'description' not in j
        if 'verification' in j:
            assert j['verification']['state'] in ('verified','incomplete','blocked','closed')
            assert j['verification']['policy_version']==2
            if j['status']=='open':assert j['verification']['state']=='verified' and j.get('last_verified_at')
        for lang in j['workplace_languages']:
            assert lang['code'] in LANGUAGES and lang['confidence']=='confirmed' and lang['evidence']
            assert lang['requirement'] in ('required','required-or-working','working','alternative','preferred')
    return True

def record_countries(record):
    if 'countries' in record:
        return sorted({code for c in record['countries'] for code in country_codes('',c)})
    return country_codes(record['location'],record.get('country'))

def process_source(source,client,stamp,prev_count=0,verify=True,cache=None):
    current=[];successful=set();closure_eligible=set();partial_sources=set()
    LOG.info('Collecting %s (%s)',source['employer'],source['adapter'])
    report={'id':source['id'],'employer':source['employer'],'adapter':source['adapter'],'checked_at':stamp}
    try:
        ownership_source=source
        records=collect(source,client)
        inventory_stats=getattr(records,'stats',{})
        source=dict(source,allowed_hosts=sorted(set(source['allowed_hosts'])|set(inventory_stats.get('allowed_hosts',[]))))
        bulk_disappearance=prev_count>=20 and len(records)<prev_count*0.4 and inventory_stats.get('complete',True)
        if bulk_disappearance:
            partial_sources.add(source['id']);report['bulk_disappearance_quarantined']=True
            report['error']='Large inventory reduction; new valid matches accepted, absence-based closure disabled pending review'
        report['collected']=len(records)
        staged=[];page_errors=[];inspected=[];verified_closed_urls=set(inventory_stats.get('verified_closed_urls',[]))
        if cache:
            known=set(source.get('known_job_urls',[]))
            records=sorted(records,key=lambda r:(0 if r['url'] in known else 1 if classify_role(r.get('title','')) else 3 if r.get('needs_page') and cache.exists(r['url']) else 2,cache.timestamp(r['url'])))
        for record in records:
            if source['adapter']=='universal-employer':
                from .ownership import owned_record
                if not owned_record(record,ownership_source):continue
            # Inventory hints and URL slugs are not job titles. Read structured
            # pages before filtering, including opaque IDs and untranslated URLs.
            if record.get('needs_page'):
                try:
                    cached=cache.get(record['url'],max_age_hours=12 if record['url'] in source.get('known_job_urls',[]) else 48) if cache else None
                    record=cached or enrich(record,source,client)
                    if cache and not cached:cache.put(record['url'],record)
                except Exception as exc:
                    from .applications import ApplicationClosed
                    if isinstance(exc,ApplicationClosed):verified_closed_urls.add(record['url']);continue
                    page_errors.append(dict(url=record['url'],error=str(exc)[:180]))
                    from .runtime import CollectionBudgetExceeded
                    if isinstance(exc,CollectionBudgetExceeded):break
                    continue
            else:
                role=classify_role(record['title'],record['text'],record.get('employment',''))
                if role:
                    try:record=enrich(record,source,client)
                    except Exception as exc:
                        from .applications import ApplicationClosed
                        if isinstance(exc,ApplicationClosed):verified_closed_urls.add(record['url']);continue
                        page_errors.append(dict(url=record['url'],error=str(exc)[:180]));continue
            inspected.append(record)
            role=classify_role(record['title'],record['text'],record.get('employment',''))
            countries=record_countries(record)
            if not role or not countries:continue
            url=allowed_url(record['url'],source); apply=allowed_url(record['apply_url'],source)
            verified=None; link_status='not-checked'; application=None; closed=False
            verification={'state':'incomplete','checked_at':stamp,'policy_version':2,'reason':'Verification disabled'}
            if verify:
                from .verification import verify_vacancy, blocked_error
                from .applications import ApplicationClosed
                try:
                    application=verify_vacancy(record,source,client,stamp)
                    apply=allowed_url(application['url'],source)
                    verified=stamp; link_status='verified'
                    verification.update(state='verified',reason=application['method'])
                except Exception as exc:
                    closed=isinstance(exc,ApplicationClosed)
                    state='closed' if closed else 'blocked' if blocked_error(exc) else 'incomplete'
                    verification.update(state=state,reason=str(exc)[:200])
                    link_status=state
                    if not closed:page_errors.append(dict(url=apply,error='Vacancy verification: '+str(exc)[:150]))
                    LOG.warning('Vacancy %s %s: %s',url,state,str(exc)[:150])
            langs=workplace_languages(record['text'])
            staged.append(dict(id=stable_id(source['id'],record['external_id']),external_id=record['external_id'],source_id=source['id'],source_name=source['employer'],source_type=source['adapter'],source_posting_id=record.get('posting_identifier'),employer=record['employer'],title=record['title'],country=countries[0],countries=countries,city=record.get('city') or record['location'],url=url,apply_url=apply,**role,advertisement_language=advertisement_language(record['text'],record.get('language')),workplace_languages=langs,language_requirements=language_summary(record['text'],langs),language_confidence='confirmed' if langs else 'unspecified',**extract_metadata(record['text'],record.get('work_mode')),published_at=record.get('published_at'),valid_through=application.get('valid_through') if application else record.get('valid_through'),first_discovered_at=stamp,last_seen_at=stamp,last_verified_at=verified,link_status=link_status,verification=verification,status='open' if verified else 'unverified'))
            if application:staged[-1]['application_verification']=dict(application,checked_at=stamp)
            if closed:staged[-1].update(status='closed',closure_reason='Official recruiting page explicitly disables applications')
        current.extend(staged); successful.add(source['id'])
        if page_errors or inventory_stats.get('status','ok')!='ok':partial_sources.add(source['id'])
        if not bulk_disappearance and not page_errors and inventory_stats.get('closure_complete',inventory_stats.get('complete',True)) and source['adapter'] not in ('employer-sitemap','employer-index'):closure_eligible.add(source['id'])
        report.update(status='partial' if source['id'] in partial_sources else 'ok',matching=len(staged),verification_states=dict(Counter(j['verification']['state'] for j in staged)),observed_countries=sorted({c for r in inspected for c in record_countries(r)}),records_inspected=len(inspected),page_failures=len(page_errors),page_errors=page_errors[:30],page_errors_truncated=len(page_errors)>30)
        report.update(inventory_stats)
        report['verified_closed_urls']=sorted(verified_closed_urls)
        if bulk_disappearance:report['status']='partial'
        if page_errors:report.update(status='partial',page_failures=len(page_errors),page_errors=page_errors[:30])
        # Inventory discovery can succeed while a detail/application read fails.
        # Keep the evidence for that narrower scope without calling the source complete.
        if 'complete' in inventory_stats:report['inventory_complete']=inventory_stats['complete']
        if report['status']!='ok':report.update(complete=False,closure_complete=False)
        if any(j['verification']['state']=='blocked' for j in staged):report['access_state']='blocked'
        if cache:report['cache_hits']=max(cache.hits,inventory_stats.get('cache_hits',0))
        if source['adapter'] in ('employer-sitemap','employer-index'):
            report.update(snapshot_kind='public-job-page-inventory',discovery_scope=source.get('discovery_scope'),page_discovery_mode='read-all-inventoried-job-pages')
        if source.get('cegid_inventory_search'):
            report.update(snapshot_kind='public-job-search-inventory',page_discovery_mode='published-titles-and-locations-with-HR-detail-enrichment')
        LOG.info('%s: %s public records; %s HR internships',source['id'],len(records),len(staged))
    except Exception as exc:
        from .verification import blocked_error
        report.update(status='failed',access_state='blocked' if blocked_error(exc) else 'error',error=str(exc)[:400])
        LOG.error('%s failed; previous data retained: %s',source['id'],exc)
    return dict(report=report,jobs=current,closure_eligible=sorted(closure_eligible))

def finalize(registry,selected,prior,prior_report,parts,stamp,output):
    reports=[p['report'] for p in parts];current=[j for p in parts for j in p['jobs']]
    successful={r['id'] for r in reports if r['status'] in ('ok','partial') and (r.get('records_inspected',0) or r.get('explicit_empty') or r['status']=='ok')}
    partial_sources={r['id'] for r in reports if r['status']=='partial'}
    closure_eligible={sid for p in parts for sid in p['closure_eligible']}
    report_by_id={r['id']:r for r in prior_report.get('sources',[])}
    from .ownership import apply_ownership_reviews
    reviewed=apply_ownership_reviews(reconcile(prior['jobs'],current,closure_eligible,stamp),read(ROOT/'data/ownership-reviews.json',[]))
    jobs=deduplicate(apply_listing_reviews(reviewed,read(ROOT/'data/listing-reviews.json',[])))
    explicitly_closed={canonical_url(url) for p in parts for url in p['report'].get('verified_closed_urls',[])}
    for job in jobs:
        if canonical_url(job['url']) in explicitly_closed:
            job['status']='closed';job['closure_reason']='Official recruiting page explicitly disables applications';job['verification']=dict(state='closed',checked_at=stamp,policy_version=2,reason=job['closure_reason'])
    from .company_registry import region_codes_for_job
    companies=read(ROOT/'data/companies.json',[])
    for job in jobs:job['region_codes']=region_codes_for_job(job,companies)
    # Preserve historical verification when API is present but this run's vacancy/application read is temporarily blocked.
    old={j['id']:j for j in prior['jobs']}
    for j in jobs:
        if not j.get('last_verified_at') and j['id'] in old: j['last_verified_at']=old[j['id']].get('last_verified_at')
    result={'schema_version':1,'updated_at':stamp if successful else prior.get('updated_at'),'last_attempt_at':stamp,'update_status':'ok' if len(successful)==len(selected) and selected and not partial_sources else 'partial' if successful else 'failed','countries':COUNTRIES,'languages':LANGUAGES,'categories':{k:v[0] for k,v in CATEGORIES.items()},'jobs':jobs}
    for job in jobs:
        from .verification import expired
        try:
            if expired(job.get('valid_through'),stamp):
                job.update(status='closed',closure_reason='Published application deadline has passed',verification=dict(state='closed',checked_at=stamp,policy_version=2,reason='Published application deadline has passed'))
        except (ValueError,TypeError):
            job.update(status='unverified',link_status='invalid-deadline',verification=dict(state='incomplete',checked_at=stamp,policy_version=2,reason='Invalid application deadline'))
        # Historical HEAD checks cannot satisfy the stronger evidence policy.
        if job['status']=='open' and job.get('verification',{}).get('policy_version')!=2:
            job.update(status='unverified',link_status='legacy-verification',verification=dict(state='incomplete',reason='Requires vacancy/application evidence under policy v2',policy_version=2,checked_at=None))
        try:age=(datetime.fromisoformat(stamp)-datetime.fromisoformat(job.get('last_verified_at') or job['last_seen_at'])).total_seconds()
        except (ValueError,TypeError,KeyError):age=float('inf')
        if job['status']=='open' and (age<0 or age>48*3600):
            job['status']='unverified';job['link_status']='stale';job['verification']=dict(job.get('verification',{}),state='incomplete',reason='Verification timestamp is future, invalid or older than 48 hours')
    validate_catalog(result)
    report_by_id.update({r['id']:r for r in reports})
    counts=Counter(c for j in jobs if j['status']!='closed' for c in j['countries'])
    all_reports=list(report_by_id.values())
    coverage={'generated_at':stamp,'exhaustive':False,'sources':all_reports,'countries':[{'code':c,'name':n,'listings':counts[c],'sources_with_observed_jobs':sum(c in r.get('observed_countries',[]) for r in all_reports if r['status']=='ok'),'discovery_candidates':sum(c in s.get('target_countries',[]) for s in registry if not s.get('enabled'))} for c,n in COUNTRIES.items()],'quality':{'total':len(jobs),'open':sum(j['status']=='open' for j in jobs),'unverified':sum(j['status']=='unverified' for j in jobs),'confirmed_english':sum(any(l['code']=='en' and l['requirement']!='preferred' for l in j['workplace_languages']) for j in jobs if j['status']!='closed'),'sources_succeeded':len(successful),'sources_attempted':len(selected),'sources_partial':len(partial_sources)}}
    coverage['quality'].update(verified_internships=sum(j['status']=='open' and j['internship_type']=='internship' for j in jobs),verified_working_students=sum(j['status']=='open' and j['internship_type']=='working-student' for j in jobs),verified_traineeships=sum(j['status']=='open' and j['internship_type']=='traineeship' for j in jobs))
    # Validate both documents before either is exported; the build copies only a successful run.
    write(output/'coverage.json',coverage); write(output/'catalog.json',result)
    LOG.info('Catalog: %s records, %s/%s sources succeeded',len(jobs),len(successful),len(selected))
    return result,coverage

def run(source_ids=None,verify=True,output=ROOT/'data'):
    registry=read(ROOT/'data/sources.json',[])
    selected=[s for s in registry if s.get('enabled') and (not source_ids or s['id'] in source_ids)]
    prior=read(output/'catalog.json',{'jobs':[],'updated_at':None})
    prior_report=read(output/'coverage.json',{'sources':[]})
    counts={r['id']:r.get('collected',0) for r in prior_report.get('sources',[])}
    stamp=now();client=Client()
    parts=[process_source(source,client,stamp,counts.get(source['id'],0),verify) for source in selected]
    return finalize(registry,selected,prior,prior_report,parts,stamp,output)

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--sources',nargs='*'); parser.add_argument('--no-verify',action='store_true'); parser.add_argument('--validate',action='store_true'); args=parser.parse_args()
    logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(message)s')
    if args.validate: validate_catalog(read(ROOT/'data/catalog.json',{})); return
    _,report=run(args.sources,not args.no_verify)
    if report['quality']['sources_succeeded']==0: raise SystemExit(1)

if __name__=='__main__': main()
