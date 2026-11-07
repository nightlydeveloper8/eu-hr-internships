"""Deterministic shortlist and bounded, read-only evidence for issue #18.

Default: rank existing NL sources; --capture: at most one known HR page per
batch employer, 8 requests/45 seconds per employer, robots enforced, no browser.
Never writes the production registry or catalog.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import sys
import time
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from collector.runtime import BudgetClient
from collector.verification import verify_vacancy

FIXTURES = ROOT / 'tests/fixtures/sprint18'
REPORT = ROOT / 'docs/coverage-sprint18'


def read(path):
    return json.loads((ROOT / path).read_text())


def shortlist():
    companies = read('data/companies.json')
    sources = {s['id']: s for s in read('data/sources.json')}
    employers = {e['company_id']: e for e in read('data/employer-collection.json')['employers']}
    jobs = read('data/catalog.json')['jobs']
    queue = {e['company_id']: e for e in read('docs/company-integration-queue.json')}
    rows = []
    excluded = []
    for company in companies:
        outcome = employers[company['id']]
        active = [sources[s] for s in company['source_ids'] if sources[s].get('enabled')]
        candidates = [j for j in jobs if j['source_id'] in {s['id'] for s in active}]
        if 'NL' not in company['target_countries'] or not candidates:
            continue
        reasons = sorted({j.get('verification', {}).get('reason', '') for j in candidates})
        blocked = any(any(token in reason.lower() for token in ('robots', '403', '406', '429', 'captcha', 'access challenge')) for reason in reasons)
        hosts = {urlsplit(j['url']).hostname for j in candidates}
        unowned = not all(urlsplit(j['url']).hostname in sources[j['source_id']]['allowed_hosts'] for j in candidates)
        disallowed = hosts & {'noorderlink.nl', 'www.nationalevacaturebank.nl', 'www.werkenvoornederland.nl', 'jobs.smartrecruiters.com'}
        manual = any(s.get('application_check') in ('official-email', 'hlb-email') for s in active)
        if blocked or unowned or disallowed or manual or outcome['state'] == 'blocked-or-failed':
            excluded.append(dict(company_id=company['id'], reasons=reasons, cause='access/ownership/aggregator/manual channel', hosts=sorted(hosts)))
            continue
        if outcome['state'] not in ('partial', 'discovery-incomplete'):
            continue
        nullable = any('NoneType' in reason for reason in reasons)
        form = any('No available vacancy-specific application' in reason for reason in reasons)
        score = (100 if nullable else 0) + (40 if form else 0) + (20 if any(j['status'] == 'unverified' for j in candidates) else 0) + (10 if len(active) == 1 else 0) + (10 if outcome['pending_urls'] == 0 else 0) + (10 if outcome['pages_read'] <= 10 else 0)
        rows.append(dict(company_id=company['id'], name=company['name'], score=score,
                         reasons=reasons, state=outcome['state'], source_ids=[s['id'] for s in active],
                         adapters=sorted({s['adapter'] for s in active}),
                         career_url=company.get('career_url'), workplaces=company.get('workplaces', []),
                         candidate_countries=company['target_countries'],
                         previous_pages_read=outcome['pages_read'], pending_urls=outcome['pending_urls'],
                         hr_candidates=len(candidates), unverified=sum(j['status']=='unverified' for j in candidates),
                         explicit_languages=[dict(id=j['id'], requirements=j.get('workplace_languages', [])) for j in candidates],
                         queue_state=queue.get(company['id'], {}).get('state'),
                         request_budget=8, duration_budget_seconds=45,
                         score_components=dict(nullable_form_attributes=100 if nullable else 0,
                             missing_form_evidence=40 if form else 0, unverified=20 if any(j['status']=='unverified' for j in candidates) else 0,
                             single_adapter=10 if len(active)==1 else 0, no_pending=10 if outcome['pending_urls']==0 else 0,
                             low_observed_page_cost=10 if outcome['pages_read']<=10 else 0)))
    rows.sort(key=lambda r: (-r['score'], r['previous_pages_read'], r['company_id']))
    rows = rows[:25]
    for i, row in enumerate(rows):
        row.update(rank=i+1, batch=i<8)
    return dict(baseline_commit='6d97637', score_is='heuristic priority, not an estimated success probability',
                inputs=['data/company-coverage.json', 'data/employer-collection.json', 'data/sources.json', 'data/companies.json', 'data/catalog.json', 'docs/company-integration-queue.json', 'docs/company-discovery-queue.json', 'docs/company-channel-review.json'],
                coverage_regions=len(read('data/company-coverage.json')['regions']),
                discovery_queue_entries=len(read('docs/company-discovery-queue.json')),
                channel_reviews=len(read('docs/company-channel-review.json')), shortlist=rows, excluded=excluded)


class Recorder(BudgetClient):
    def __init__(self, folder):
        super().__init__(seconds=45, max_requests=8)
        self.folder = folder
        self.events = []
        self.responses = []
        self.denied = set()

    def request(self, url, method='GET', **kwargs):
        # No retry on a denied origin, including subsequent robots lookups.
        origin = urlsplit(url).netloc
        if origin in self.denied:
            raise ValueError('Source excluded after access failure')
        start = time.monotonic()
        try:
            result = super().request(url, method=method, **kwargs)
            name = hashlib.sha256(url.encode()).hexdigest()[:20] + '.html.gz'
            with gzip.GzipFile(filename=str(self.folder / name), mode='wb', mtime=0) as f:
                f.write(result[0])
            self.responses.append(dict(url=url, final_url=result[2], status=result[1], file=name,
                                       sha256=hashlib.sha256(result[0]).hexdigest()))
            self.events.append(dict(url=url, status=result[1], seconds=round(time.monotonic()-start, 3)))
            return result
        except Exception as exc:
            self.events.append(dict(url=url, error=str(exc), seconds=round(time.monotonic()-start, 3)))
            self.denied.add(origin)
            raise


def capture(selection):
    sources = {s['id']:s for s in read('data/sources.json')}
    jobs = read('data/catalog.json')['jobs']
    for row in selection['shortlist'][:8]:
        folder = FIXTURES / row['company_id']
        folder.mkdir(parents=True, exist_ok=True)
        if (folder/'capture.json').exists():
            raise ValueError('Capture exists; do not silently refresh real evidence')
        job = next(j for j in jobs if j['source_id'] in row['source_ids'] and j['status']=='unverified')
        source = sources[job['source_id']]
        record = dict(job, text='', location=job.get('city') or '', posting_identifier=job.get('source_posting_id'))
        client = Recorder(folder)
        stamp = datetime.now(timezone.utc).isoformat()
        try:
            proof = verify_vacancy(record, source, client, stamp)
            result = dict(proof=proof)
        except Exception as exc:
            result = dict(error=str(exc))
        payload = dict(company_id=row['company_id'], stamp=stamp, source=source, record=record,
                       events=client.events, responses=client.responses, requests=client.requests, bytes_read=client.bytes, baseline=result)
        (folder/'capture.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2)+'\n')
        print(row['company_id'], result.get('error', 'verified'), client.requests, flush=True)


def capture_linked():
    """Read one observed same-ID application CTA; no guessed routes or rendering."""
    from collector.universal import Document
    from collector.verification import shares_identifier, same_requisition
    from urllib.parse import urljoin
    import re
    for path in sorted(FIXTURES.glob('*/capture.json')):
        payload = json.loads(path.read_text())
        source, record = payload['source'], payload['record']
        targets = []
        for response in payload['responses']:
            if response['url'] != record['url']:
                continue
            doc = Document(gzip.decompress((path.parent/response['file']).read_bytes()), response['final_url'])
            if doc.url != record['url']:
                continue
            for href, label, _ in doc.links:
                target = urljoin(doc.url, href)
                if (re.search(r'apply|solliciteer|solliciteren|bewerben|postuler', label, re.I)
                    and urlsplit(target).hostname in source['allowed_hosts']
                    and target.split('#')[0] != doc.url.split('#')[0]
                    and (same_requisition(doc.url,target) or shares_identifier(record,target))):
                    targets.append(target)
        if not targets or any(r['url'] == targets[0] for r in payload['responses']):
            continue
        client = Recorder(path.parent)
        client.max_requests = 8-payload['requests']
        try:
            client.request(targets[0])
        except Exception:
            pass
        payload['events'].extend(client.events)
        payload['responses'].extend(client.responses)
        payload['requests'] += client.requests
        payload['bytes_read'] += client.bytes
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2)+'\n')
        print(payload['company_id'], 'observed CTA', client.requests, flush=True)


def capture_inventory():
    """Only the configured public Greenhouse adapter in this batch."""
    from collector.adapters import collect
    selection = shortlist()
    selected = {sid for r in selection['shortlist'][:8] for sid in r['source_ids']}
    for source in read('data/sources.json'):
        if source['id'] not in selected or source['adapter'] != 'greenhouse':
            continue
        folder = next(p.parent for p in FIXTURES.glob('*/capture.json') if json.loads(p.read_text())['source']['id']==source['id'])
        path = folder/'capture.json'
        payload = json.loads(path.read_text())
        if payload.get('inventory_attempted'):
            raise ValueError('Inventory already captured')
        client = Recorder(folder)
        client.max_requests = 8-payload['requests']
        try:
            records = collect(source, client)
            payload['inventory_records'] = len(records)
        except Exception as exc:
            payload['inventory_error'] = str(exc)
        payload['inventory_attempted'] = True
        payload['events'].extend(client.events)
        payload['responses'].extend(client.responses)
        payload['requests'] += client.requests
        payload['bytes_read'] += client.bytes
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2)+'\n')
        print(source['id'], payload.get('inventory_records',payload.get('inventory_error')), client.requests)


def confirm_live():
    """Fresh before-publication check only for the successful Greenhouse batch source."""
    from collector.adapters import collect
    from collector.classify import classify_role
    for path in sorted(FIXTURES.glob('*/capture.json')):
        payload = json.loads(path.read_text())
        if payload['source']['adapter'] != 'greenhouse' or not payload.get('inventory_attempted'):
            continue
        folder = path.parent/'confirmation'
        folder.mkdir(exist_ok=True)
        target = folder/'result.json'
        if target.exists():
            raise ValueError('Live confirmation already recorded')
        client = Recorder(folder)
        client.max_requests = 8-payload['requests']
        source = payload['source']
        stamp = datetime.now(timezone.utc).isoformat()
        result = dict(stamp=stamp, source_id=source['id'])
        try:
            records = collect(source,client)
            candidates = [r for r in records if classify_role(r['title'],r['text'],r.get('employment',''))]
            result['inventory_records'] = len(records)
            result['hr_candidates'] = len(candidates)
            result['proofs'] = [dict(external_id=r['external_id'],title=r['title'],
                **verify_vacancy(r,source,client,stamp)) for r in candidates]
        except Exception as exc:
            result['error'] = str(exc)
        result.update(requests=client.requests, events=client.events, responses=client.responses)
        target.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
        print(json.dumps({k:result[k] for k in result if k not in ('events','responses')},ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--capture', action='store_true')
    parser.add_argument('--capture-linked', action='store_true')
    parser.add_argument('--capture-inventory', action='store_true')
    parser.add_argument('--confirm-live', action='store_true')
    args = parser.parse_args()
    REPORT.mkdir(parents=True, exist_ok=True)
    selection = shortlist()
    (REPORT/'shortlist.json').write_text(json.dumps(selection, ensure_ascii=False, indent=2)+'\n')
    if args.capture:
        capture(selection)
    elif args.capture_linked:
        capture_linked()
    elif args.capture_inventory:
        capture_inventory()
    elif args.confirm_live:
        confirm_live()
    else:
        print([(r['company_id'], r['score']) for r in selection['shortlist']])
