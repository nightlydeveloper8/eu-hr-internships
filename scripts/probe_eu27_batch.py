"""Explicit, bounded GET-only preflight of new EU27 adapter candidates.

Default is an offline selection preview. --live reads ONE already-observed
vacancy/board per new employer, robots enforced, exact-host redirect scope,
4 logical requests/20 seconds per employer, 4 workers maximum, no browser,
no API inventory, no follow-up application navigation and no registry writes.
"""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import sys
import time
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from collector.ats_channel_discovery import safe_url
from collector.runtime import BudgetClient
from collector.universal import Document
from collector.applications import ensure_open_document
from collector.verification import same_title, applicant_form


def select(batch):
    rows=[];seen=set()
    for row in batch['rows']:
        if row['action']!='new-employer-channel' or not row['adapter_reusable']:continue
        if row['channel_key'] in seen:continue
        seen.add(row['channel_key']);rows.append(row)
    return rows


def probe(row,client_factory=BudgetClient):
    start=time.monotonic()
    evidence=next((e for e in row['hr_evidence'] if e['kind'] in ('indexed-search','page-open')),None)
    result=dict(company_key=row['company_key'],name=row['name'],channel_key=row['channel_key'],
        adapter=row['adapter'],checked_at=datetime.now(timezone.utc).isoformat(),
        expected_title=evidence['title'] if evidence else None,
        url=evidence['url'] if evidence else None,state='not-read',availability='unverified',
        identity_review='required',integration_ready=False,production_enabled=False,
        requests=0,bytes_read=0,renderings=0)
    client=None
    try:
        url=result['url'];p=safe_url(url)
        if not p:raise ValueError('No safe observed URL')
        if p.path.rstrip('/').endswith(('/c/new','/apply')):
            raise ValueError('Application URL only; first establish the observed vacancy page')
        client=client_factory(seconds=20,max_requests=4)
        client.redirect_scope_allowed=lambda target:bool(safe_url(target) and urlsplit(target).hostname==p.hostname)
        body,status,final=client.request(url)
        if urlsplit(final).hostname!=p.hostname:raise ValueError('Cross-host redirect requires review')
        doc=Document(body,final)
        result.update(http_status=status,final_url=final,body_sha256=hashlib.sha256(body).hexdigest(),
            title_match=same_title(doc,result['expected_title']),headings=doc.h1[:3],
            structured_titles=[post.get('title') for post in doc.jobposts()][:3])
        ensure_open_document(doc)
        result['applicant_form_present']=applicant_form(body,strict=True)
        result['state']='same-title-page-observed' if result['title_match'] else 'page-read-title-not-established'
    except Exception as exc:
        result.update(state='not-established',error=type(exc).__name__+': '+str(exc)[:240])
    if client:result.update(requests=client.requests,bytes_read=client.bytes)
    result['duration_seconds']=round(time.monotonic()-start,3)
    return result


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live',action='store_true')
    parser.add_argument('--limit',type=int,default=28)
    parser.add_argument('--names',nargs='+',help='Explicit subset of new candidate names; no repeat of other probes')
    parser.add_argument('--output',type=Path,default=ROOT/'docs/eu27-expansion/probe-2026-11-16.json')
    args=parser.parse_args(argv)
    if not 1<=args.limit<=28:parser.error('Limit must be between 1 and 28')
    batch=json.loads((ROOT/'docs/eu27-expansion/batch-01.json').read_text())
    rows=select(batch)
    if args.names:
        rows=[r for r in rows if r['name'] in args.names]
        if set(args.names)!={r['name'] for r in rows}:parser.error('Names must be present in the current new-adapter candidate batch')
    rows=rows[:args.limit]
    if not args.live:
        print(json.dumps(dict(mode='offline-preview',selected=len(rows),names=[r['name'] for r in rows])));return
    if args.output.exists():raise ValueError('Evidence already exists; do not silently refresh')
    start=time.monotonic()
    with ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(probe,rows))
    report=dict(schema_version=1,mode='bounded-one-page-preflight-not-vacancy-verification',
        base_commit=batch['base_commit'],catalog_updated_at=batch['catalog_updated_at'],
        checked_at=datetime.now(timezone.utc).isoformat(),
        scope='Only observed new-employer URLs on reusable adapters, one page each',
        limits=dict(per_employer_requests=4,per_employer_seconds=20,workers=4,browser_renderings=0),
        summary=dict(employers=len(results),states=dict(Counter(r['state'] for r in results)),
            requests=sum(r['requests'] for r in results),bytes_read=sum(r['bytes_read'] for r in results),
            source_seconds=round(sum(r['duration_seconds'] for r in results),3),
            wall_seconds=round(time.monotonic()-start,3),
            same_title_pages=sum(bool(r.get('title_match')) and r['state']=='same-title-page-observed' for r in results),
            forms_on_same_title_pages=sum(bool(r.get('applicant_form_present')) and r['state']=='same-title-page-observed' for r in results),
            new_verified=0,new_enabled_sources=0),
        counting_note='Logical request counters include robots lookups; redirects are not separately counted. No page is promoted to verified by this report.',
        rows=results)
    args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report['summary']))


if __name__=='__main__':main()
