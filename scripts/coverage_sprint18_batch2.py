"""Rank only the remaining shortlist; bounded reads, immutable offline evidence.

No production writes or inventory crawl. Capture uses the normal robots-aware
client and only known vacancy URLs (max 8 logical requests/45s per company).
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import gzip
import hashlib
import json
import re
from pathlib import Path
import subprocess
import sys
from urllib.parse import urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.coverage_sprint18 import Recorder, read
from collector.universal import Document
from collector.classify import fold, canonical_url

REPORT = ROOT / 'docs/coverage-sprint18/batch2'
FIXTURES = ROOT / 'tests/fixtures/sprint18-batch2'


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def rank():
    remaining = [r for r in read('docs/coverage-sprint18/shortlist.json')['shortlist'] if not r['batch']]
    assert len(remaining) == 17
    outcomes = {e['company_id']: e for e in read('data/employer-collection.json')['employers']}
    jobs = read('data/catalog.json')['jobs']
    rows = []
    for previous in remaining:
        outcome = outcomes[previous['company_id']]
        candidates = [j for j in jobs if j['source_id'] in previous['source_ids']]
        reasons = sorted({j.get('verification', {}).get('reason', '') for j in candidates})
        blocked = any(any(t in reason.lower() for t in ('robots', '403', '406', '429', 'captcha', 'access challenge')) for reason in reasons)
        pending = outcome['pending_urls']
        components = dict(unverified=20 if any(j['status']=='unverified' for j in candidates) else 0,
                          form_or_identity=40 if any('No available vacancy-specific application' in r or 'Application link lacks' in r for r in reasons) else 0,
                          no_pending=30 if not pending else 0,
                          nl_candidate=20 if any('NL' in j['countries'] for j in candidates) else 0,
                          low_cost=10 if outcome['pages_read']<=10 else 0)
        excluded = 'access restriction' if blocked or outcome['state']=='blocked-or-failed' else 'already verified' if not any(j['status']=='unverified' for j in candidates) else None
        rows.append(dict(company_id=previous['company_id'], name=previous['name'],
                         source_ids=previous['source_ids'], state=outcome['state'], reasons=reasons,
                         pages_read=outcome['pages_read'], pending_urls=pending,
                         candidate_ids=[j['id'] for j in candidates], countries=sorted({c for j in candidates for c in j['countries']}),
                         explicit_languages=[dict(id=j['id'], requirements=j['workplace_languages']) for j in candidates],
                         score_components=components, score=sum(components.values()), excluded=excluded))
    rows.sort(key=lambda r: (bool(r['excluded']), -r['score'], r['pages_read'], r['company_id']))
    for i, row in enumerate(rows):
        row.update(rank=i+1, selected=i<7 and not row['excluded'])
    return dict(catalog_updated_at=read('data/catalog.json')['updated_at'],
                global_statuses=dict(Counter(j['status'] for j in jobs)),
                scope='Only the 17 remaining companies from the original shortlist',
                heuristic='20 unverified + 40 missing form/identity + 30 no pending URLs + 20 known NL vacancy + 10 <=10 pages; exclusions first',
                request_budget_per_company=8, seconds_per_company=45, shortlist=rows)


def capture():
    if sys.version_info < (3,12):raise RuntimeError('Use Python 3.12+, as in CI')
    selection = rank()
    if (REPORT/'ranking.json').exists() or FIXTURES.exists():
        raise ValueError('Evidence already exists; no silent refresh')
    # Git provenance belongs to a new capture, not the pure ranking calculation.
    # Actions' shallow PR checkout need not contain origin/main to run tests.
    selection['base_commit']=subprocess.check_output(['git','rev-parse','origin/main'],cwd=ROOT,text=True).strip()
    write(REPORT/'ranking.json', selection)
    FIXTURES.mkdir(parents=True)
    catalog=(ROOT/'data/catalog.json').read_bytes()
    baseline=subprocess.check_output(['git','show',selection['base_commit']+':collector/verification.py'],cwd=ROOT)
    (FIXTURES/'catalog-before.json.gz').write_bytes(gzip.compress(catalog,mtime=0))
    (FIXTURES/'verification-before.py.gz').write_bytes(gzip.compress(baseline,mtime=0))
    write(FIXTURES/'baseline.json',dict(commit=selection['base_commit'],
                                      verification_sha256=hashlib.sha256(baseline).hexdigest(),
                                      catalog_sha256=hashlib.sha256(catalog).hexdigest()))
    from scripts.replay_sprint18_batch2 import baseline_verifier
    verify_before=baseline_verifier()
    sources = {s['id']:s for s in read('data/sources.json')}
    jobs = read('data/catalog.json')['jobs']
    for row in selection['shortlist']:
        if not row['selected']:continue
        folder = FIXTURES/row['company_id']
        folder.mkdir()
        client = Recorder(folder)
        records = []
        stamp = datetime.now(timezone.utc).isoformat()
        for job in jobs:
            if job['id'] not in row['candidate_ids'] or job['status']!='unverified':continue
            source = sources[job['source_id']]
            record = dict(job, text='', location=job.get('city') or '', posting_identifier=job.get('source_posting_id'))
            try:result = dict(proof=verify_before(record, source, client, stamp))
            except Exception as exc:result = dict(error=str(exc))
            records.append(dict(source=source, record=record, before=result))
        payload = dict(company_id=row['company_id'],stamp=stamp,records=records,
                       responses=client.responses,events=client.events,requests=client.requests,bytes_read=client.bytes,python=sys.version)
        write(folder/'capture.json', payload)
        print(row['company_id'],client.requests,[r['before'] for r in records],flush=True)


def remaining_recorder(path,payload):
    client=Recorder(path.parent)
    client.max_requests=8-payload['requests']
    client.deadline-=sum(e['seconds'] for e in payload['events'] if not e['url'].endswith('/robots.txt'))
    return client


def capture_linked():
    """Diagnose one published application CTA, even when identity is unproven.

    Reading a CTA is not verification. No guessed endpoints, generic application
    links, denied sources or unapproved hosts are followed.
    """
    for path in sorted(FIXTURES.glob('*/capture.json')):
        payload = json.loads(path.read_text())
        if payload.get('linked_attempted'):continue
        targets = []
        for item in payload['records']:
            for response in payload['responses']:
                if response['url']!=item['record']['url']:continue
                body=gzip.decompress((path.parent/response['file']).read_bytes())
                doc=Document(body,response['final_url'])
                if canonical_url(doc.url)!=canonical_url(item['record']['url']):continue
                for href,label,_ in doc.links:
                    if not re.fullmatch(r'solliciteer(?: direct)?|apply(?: now)?',fold(label).strip()):continue
                    try:target=canonical_url(urljoin(doc.url,href))
                    except ValueError:continue
                    if (urlsplit(target).hostname in item['source']['allowed_hosts']
                        and target!=canonical_url(doc.url)):
                        targets.append(target)
        if not targets:continue
        client=remaining_recorder(path,payload)
        try:client.request(targets[0])
        except Exception:pass
        payload['linked_attempted']=True
        payload['responses'].extend(client.responses)
        payload['events'].extend(client.events)
        payload['requests']+=client.requests
        payload['bytes_read']+=client.bytes
        write(path,payload)
        print(payload['company_id'],client.requests,flush=True)


def confirm_runtime():
    """Recheck only HTTP 308 captured with the older system Python.

    CI uses 3.12, whose urllib supports 308. Preserve the earlier attempt and
    charge both attempts to the original request budget.
    """
    if sys.version_info < (3,12):raise RuntimeError('Use Python 3.12+, as in CI')
    for path in sorted(FIXTURES.glob('*/capture.json')):
        payload=json.loads(path.read_text())
        if not any('HTTP Error 308' in e.get('error','') for e in payload['events']):continue
        if payload.get('runtime_confirmation'):raise ValueError('Runtime confirmation already recorded')
        client=remaining_recorder(path,payload)
        original=json.loads(json.dumps(payload['records']))
        stamp=datetime.now(timezone.utc).isoformat()
        from scripts.replay_sprint18_batch2 import baseline_verifier
        verify_before=baseline_verifier()
        for item in payload['records']:
            try:item['before']=dict(proof=verify_before(item['record'],item['source'],client,stamp))
            except Exception as exc:item['before']=dict(error=str(exc))
        payload['runtime_confirmation']=dict(original_records=original,original_stamp=payload['stamp'],python=sys.version)
        payload['stamp']=stamp
        payload['responses'].extend(client.responses)
        payload['events'].extend(client.events)
        payload['requests']+=client.requests
        payload['bytes_read']+=client.bytes
        write(path,payload)
        print(payload['company_id'],client.requests,[r['before'] for r in payload['records']],flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capture',action='store_true')
    parser.add_argument('--capture-linked',action='store_true')
    parser.add_argument('--confirm-runtime',action='store_true')
    args = parser.parse_args()
    if args.capture:capture()
    elif args.capture_linked:capture_linked()
    elif args.confirm_runtime:confirm_runtime()
    else:print(json.dumps(rank(),ensure_ascii=False,indent=2))
