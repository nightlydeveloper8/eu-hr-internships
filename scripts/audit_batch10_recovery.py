"""Lotto 10 — offline recoverability audit for NL, BE, FR, ES, PT.

Do not mistake historical third-party referrals, expired vacancies, research
targets or blocked sites for recoverable official applications. No HTTP calls.
Usage: python -m scripts.audit_batch10_recovery [--output PATH]
"""
import argparse
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit
import json

from scripts.build_eu27_expansion_queue import ROOT

COUNTRIES=("NL","BE","FR","ES","PT")


def ownership_risk(job, source):
    """Historical off-host vacancy without a reviewed ownership transfer."""
    if not source or job.get('ownership_review'):
        return False
    if source.get('ownership_scope')!='reviewed-hosts' and not source.get('require_employer_identity'):
        return False
    host=urlsplit(job.get('url') or '').hostname
    return bool(host and host not in source.get('allowed_hosts',[]))


def cause(job):
    reason=(job.get('verification') or {}).get('reason') or ''
    note=(job.get('review_note') or '')
    value=reason+' '+note
    if 'Historical external' in value or 'outside source reviewed employer hosts' in value:
        return 'historical-unreviewed-source'
    if 'Time budget exhausted' in value or 'Request budget exhausted' in value:
        return 'source-budget-exhausted'
    if 'Application link lacks a matching vacancy identifier' in value:
        return 'application-requisition-identity'
    if 'No available vacancy-specific application entry' in value:
        return 'no-observed-application-entry'
    if 'Current page does not identify the same vacancy' in value or 'Application page does not identify the same vacancy' in value:
        return 'title-mismatch'
    if 'robots.txt' in value or '403' in value or '429' in value or 'timed out' in value or 'Remote end closed' in value:
        return 'access-or-network'
    if 'Applicant form not established' in value:
        return 'application-fields-unknown'
    return 'other-review-required'


def audit(catalog, registry):
    allowed=set(COUNTRIES)
    sources={s['id']:s for s in registry}
    totals=Counter()
    rows={c:Counter() for c in COUNTRIES}
    causes=Counter()
    by_source=Counter()
    by_source_cause=Counter()
    rejected_sources=Counter()
    seen_ids=set()
    for job in catalog.get('jobs',[]):
        if job.get('id') in seen_ids:raise ValueError('Duplicate catalog job ID')
        seen_ids.add(job.get('id'))
        country=job.get('country')
        if country not in allowed:continue
        row=rows[country]
        row['total']+=1;totals['total']+=1
        status=job.get('status')
        if status=='open' and job.get('verification',{}).get('state')=='verified' and job.get('link_status')=='verified':
            row['verified_record']+=1
            totals['verified_record']+=1
            if job.get('internship_type')=='internship':
                row['verified_internship']+=1;totals['verified_internship']+=1
        if status=='closed':
            row['closed']+=1;totals['closed']+=1
        if status=='unverified':
            row['unverified']+=1;totals['unverified']+=1
        if ownership_risk(job,sources.get(job.get('source_id'))):
            row['unreviewed_external_source_total']+=1
            totals['unreviewed_external_source_total']+=1
            rejected_sources[job.get('source_id')]+=1
            if status=='unverified':
                row['unreviewed_external_unverified']+=1;totals['unreviewed_external_unverified']+=1
            continue
        if status!='unverified':continue
        row['eligible_for_evidence_review']+=1;totals['eligible_for_evidence_review']+=1
        label=cause(job)
        causes[label]+=1
        by_source[job.get('source_id')]+=1
        by_source_cause[(job.get('source_id'),label)]+=1
    return dict(schema_version=1,mode='offline-no-network',catalog_updated_at=catalog.get('updated_at'),
                countries=[dict(country=country,**rows[country]) for country in COUNTRIES],
                totals=dict(totals),priority_causes=[dict(cause=k,count=v) for k,v in causes.most_common()],
                priority_sources=[dict(source_id=k,count=v) for k,v in by_source.most_common(25)],
                priority_source_causes=[dict(source_id=k[0],cause=k[1],count=v) for k,v in by_source_cause.most_common(25)],
                historical_unreviewed_sources=dict(rejected_sources),
                constraints=['Not all remaining unverified records are recoverable, currently open or unique vacancies',
                             'Historical third-party records are preserved but excluded from official recovery queue',
                             'Never infer availability from HTTP200, the company website alone, or stored past evidence',
                             'The national EU27 mapping remains incomplete; this is a five-country snapshot',
                             'No source changes, requests, rendering, applications or production rollout'])


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path)
    args=p.parse_args()
    read=lambda path:json.loads((ROOT/path).read_text(encoding='utf-8'))
    result=audit(read('data/catalog.json'),read('data/sources.json'))
    text=json.dumps(result,indent=2,ensure_ascii=False)+'\n'
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(text,encoding='utf-8')
    else:
        print(text,end='')


if __name__=='__main__':
    main()
