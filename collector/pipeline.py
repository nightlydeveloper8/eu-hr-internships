import argparse
from collections import Counter
from datetime import datetime, timezone
import json
import logging
import os
from pathlib import Path
from urllib.parse import urlsplit
from .adapters import Client, collect, enrich
from .classify import COUNTRIES, LANGUAGES, CATEGORIES, canonical_url, classify_role, country_codes, stable_id, workplace_languages, advertisement_language, extract_metadata

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
        job['first_discovered_at']=old.get('first_discovered_at',stamp)
        job['missing_count']=0
        job.pop('missing_since',None)
        merged[job['id']]=job
    seen={j['id'] for j in current}
    for key,job in merged.items():
        if key in seen or job['source_id'] not in successful: continue
        if job.get('last_missing_run')==stamp[:10]: continue
        job['missing_count']=job.get('missing_count',0)+1
        job['missing_since']=job.get('missing_since',stamp)
        job['last_missing_run']=stamp[:10]
        elapsed=(datetime.fromisoformat(stamp)-datetime.fromisoformat(job['missing_since'])).total_seconds()
        job['status']='closed' if job['missing_count']>=3 and elapsed>=48*3600 else 'unverified'
    return list(merged.values())

def deduplicate(jobs):
    by_url={}
    for job in sorted(jobs,key=lambda j:j.get('first_discovered_at','')):
        keys={canonical_url(job['url']),canonical_url(job.get('apply_url') or job['url'])}
        existing=next((by_url[k] for k in keys if k in by_url),None)
        if existing is not None:
            existing['duplicate_source_ids']=sorted(set(existing.get('duplicate_source_ids',[])+[job['source_id']]))
            # Keep stable ID/first discovery, use freshest verified metadata.
            if job.get('last_verified_at','')>existing.get('last_verified_at',''):
                stable,first=existing['id'],existing['first_discovered_at']
                existing.update(job); existing['id'],existing['first_discovered_at']=stable,first
        else: existing=dict(job)
        for key in keys: by_url[key]=existing
    return list({id(value):value for value in by_url.values()}.values())

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
        for lang in j['workplace_languages']:
            assert lang['code'] in LANGUAGES and lang['confidence']=='confirmed' and lang['evidence']
    return True

def run(source_ids=None,verify=True,output=ROOT/'data'):
    registry=read(ROOT/'data/sources.json',[])
    selected=[s for s in registry if s.get('enabled') and (not source_ids or s['id'] in source_ids)]
    prior=read(output/'catalog.json',{'jobs':[],'updated_at':None})
    prior_report=read(output/'coverage.json',{'sources':[]})
    report_by_id={r['id']:r for r in prior_report.get('sources',[])}
    stamp=now(); client=Client(); current=[]; successful=set(); reports=[]
    for source in selected:
        LOG.info('Collecting %s (%s)',source['employer'],source['adapter'])
        report={'id':source['id'],'employer':source['employer'],'adapter':source['adapter'],'checked_at':stamp}
        try:
            records=collect(source,client)
            prev_count=report_by_id.get(source['id'],{}).get('collected',0)
            if prev_count>=20 and len(records)<prev_count*0.4: raise ValueError('Bulk disappearance quarantined; review source before next run')
            report['collected']=len(records)
            staged=[]
            for record in records:
                role=classify_role(record['title'],record['text'],record.get('employment',''))
                countries=country_codes(record['location'],record.get('country'))
                if not role or not countries: continue
                record=enrich(record,source,client)
                url=allowed_url(record['url'],source); apply=allowed_url(record['apply_url'],source)
                verified=None; link_status='not-checked'
                if verify:
                    try:
                        # HEAD avoids downloading/reproducing descriptions. No fallback on access restrictions.
                        for target in set((url,apply)):
                            _,_,final=client.request(target,method='HEAD')
                            allowed_url(final,source)
                        verified=stamp; link_status='verified'
                    except Exception as exc:
                        LOG.warning('Link unverified %s: %s',url,str(exc)[:150]); link_status='unverified'
                langs=workplace_languages(record['text'])
                staged.append(dict(id=stable_id(source['id'],record['external_id']),external_id=record['external_id'],source_id=source['id'],source_name=source['employer'],source_type=source['adapter'],employer=record['employer'],title=record['title'],country=countries[0],countries=countries,city=record.get('city') or record['location'],url=url,apply_url=apply,**role,advertisement_language=advertisement_language(record['text'],record.get('language')),workplace_languages=langs,language_confidence='confirmed' if langs else 'unspecified',**extract_metadata(record['text'],record.get('work_mode')),published_at=record.get('published_at'),first_discovered_at=stamp,last_seen_at=stamp,last_verified_at=verified,link_status=link_status,status='open' if verified else 'unverified'))
            current.extend(staged); successful.add(source['id'])
            report.update(status='ok',matching=len(staged),observed_countries=sorted({c for r in records for c in country_codes(r['location'],r.get('country'))}))
            LOG.info('%s: %s public records; %s HR internships',source['id'],len(records),len(staged))
        except Exception as exc:
            report.update(status='failed',error=str(exc)[:400])
            LOG.error('%s failed; previous data retained: %s',source['id'],exc)
        reports.append(report)
    jobs=deduplicate(reconcile(prior['jobs'],current,successful,stamp))
    # Preserve historical verification when API is present but this run's HEAD is temporarily blocked.
    old={j['id']:j for j in prior['jobs']}
    for j in jobs:
        if not j.get('last_verified_at') and j['id'] in old: j['last_verified_at']=old[j['id']].get('last_verified_at')
    result={'schema_version':1,'updated_at':stamp if successful else prior.get('updated_at'),'last_attempt_at':stamp,'update_status':'ok' if len(successful)==len(selected) and selected else 'partial' if successful else 'failed','countries':COUNTRIES,'languages':LANGUAGES,'categories':{k:v[0] for k,v in CATEGORIES.items()},'jobs':jobs}
    validate_catalog(result)
    report_by_id.update({r['id']:r for r in reports})
    counts=Counter(c for j in jobs if j['status']!='closed' for c in j['countries'])
    all_reports=list(report_by_id.values())
    coverage={'generated_at':stamp,'exhaustive':False,'sources':all_reports,'countries':[{'code':c,'name':n,'listings':counts[c],'sources_with_observed_jobs':sum(c in r.get('observed_countries',[]) for r in all_reports if r['status']=='ok'),'discovery_candidates':sum(c in s.get('target_countries',[]) for s in registry if not s.get('enabled'))} for c,n in COUNTRIES.items()],'quality':{'total':len(jobs),'open':sum(j['status']=='open' for j in jobs),'unverified':sum(j['status']=='unverified' for j in jobs),'confirmed_english':sum(any(l['code']=='en' for l in j['workplace_languages']) for j in jobs if j['status']!='closed'),'sources_succeeded':len(successful),'sources_attempted':len(selected)}}
    # Validate both documents before either is exported; the build copies only a successful run.
    write(output/'coverage.json',coverage); write(output/'catalog.json',result)
    LOG.info('Catalog: %s records, %s/%s sources succeeded',len(jobs),len(successful),len(selected))
    return result,coverage

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--sources',nargs='*'); parser.add_argument('--no-verify',action='store_true'); parser.add_argument('--validate',action='store_true'); args=parser.parse_args()
    logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(message)s')
    if args.validate: validate_catalog(read(ROOT/'data/catalog.json',{})); return
    _,report=run(args.sources,not args.no_verify)
    if report['quality']['sources_succeeded']==0: raise SystemExit(1)

if __name__=='__main__': main()
