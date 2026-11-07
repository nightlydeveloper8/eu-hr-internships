"""Offline replay of captured official responses; never contacts the network.

Frozen bodies only measure regressions, never refresh production verification.
"""
from collections import Counter
import copy
import gzip
import hashlib
import json
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from collector.pipeline import process_source, finalize
from collector.verification import verify_vacancy
from scripts.coverage_sprint18 import FIXTURES, REPORT, read


class Replay:
    def __init__(self, path):
        self.path = path
        self.payload = json.loads(path.read_text())
        self.calls = []

    def request(self, url, **kwargs):
        if kwargs.get('method', 'GET') != 'GET':
            raise AssertionError('Replay permits read-only GET')
        self.calls.append(url)
        for response in self.payload['responses']:
            if response['url'] == url:
                body = gzip.decompress((self.path.parent/response['file']).read_bytes())
                assert hashlib.sha256(body).hexdigest() == response['sha256']
                return body, response['status'], response['final_url']
        event = next((e for e in self.payload['events'] if e['url']==url and 'error' in e), None)
        if event:
            raise ValueError(event['error'])
        raise AssertionError('Uncaptured request: '+url)

    def json(self, url):
        return json.loads(self.request(url)[0])


def legacy_applicant_form(body):
    """Exact pre-fix predicate at 6d97637; frozen for differential replay."""
    import re
    from collector.applications import ApplicantForms
    for form in ApplicantForms(body).forms:
        names=' '.join(i.get('name','')+' '+i.get('type','') for i in form['fields']).lower()
        attributes=' '.join(form['attrs'].values()).lower()
        application=bool(re.search(r'apply|applica|recruit|candidate',attributes) or re.search(r'resume|\bcv\b',names))
        if application and form['submit'] and 'email' in names and re.search(r'name|resume|\bcv\b',names):return True
    return False


def run(output=None):
    rows = []
    inventory_delta = None
    # Freeze historical catalog as well: nightly changes cannot alter this experiment.
    prior = json.loads(gzip.decompress((FIXTURES/'catalog-before.json.gz').read_bytes()))
    coverage = {'sources': []}
    selection = read('docs/coverage-sprint18/shortlist.json')
    expected = {r['company_id'] for r in selection['shortlist'] if r['batch']}
    captures = list(sorted(FIXTURES.glob('*/capture.json')))
    assert {p.parent.name for p in captures} == expected and len(captures) == 8
    for path in captures:
        client = Replay(path)
        payload = client.payload
        row = dict(company_id=payload['company_id'], vacancy_url=payload['record']['url'],
                   observed_at=payload['stamp'], baseline=payload['baseline'],
                   live_requests=payload['requests'], live_bytes=payload['bytes_read'],
                   live_duration_seconds=round(sum(e['seconds'] for e in payload['events'] if not e['url'].endswith('/robots.txt')),3))
        try:
            proof = verify_vacancy(payload['record'], payload['source'], client, payload['stamp'])
            row['after'] = dict(proof=proof)
        except ValueError as exc:
            row['after'] = dict(error=str(exc))
        confirmation = path.parent/'confirmation/result.json'
        if confirmation.exists():
            live = json.loads(confirmation.read_text())
            row['fresh_live_confirmation'] = live
            row['live_requests'] += live['requests']
            row['live_duration_seconds'] = round(row['live_duration_seconds']+sum(e['seconds'] for e in live['events'] if not e['url'].endswith('/robots.txt')),3)
            assert row['live_requests'] <= 8
        row['newly_discovered_hr'] = 0
        if payload['source']['adapter'] == 'greenhouse' and not payload.get('inventory_error'):
            source = payload['source']
            sources = [source]
            with patch('collector.verification.applicant_form', legacy_applicant_form):
                before = process_source(source, Replay(path), payload['stamp'])
            after = process_source(source, Replay(path), payload['stamp'])
            second = process_source(source, Replay(path), payload['stamp'])
            assert after == second
            with tempfile.TemporaryDirectory() as folder:
                original, _ = finalize(sources, [source], copy.deepcopy(prior), coverage, [before], payload['stamp'], Path(folder)/'before')
                changed, _ = finalize(sources, [source], copy.deepcopy(prior), coverage, [after], payload['stamp'], Path(folder)/'after')
                repeated, _ = finalize(sources, [source], copy.deepcopy(changed), coverage, [second], payload['stamp'], Path(folder)/'second')
            assert changed['jobs'] == repeated['jobs']
            assert {j['id'] for j in prior['jobs']} == {j['id'] for j in changed['jobs']}
            old = {j['id']:j for j in prior['jobs']}
            baseline_jobs = {j['id']:j for j in original['jobs']}
            for job in changed['jobs']:
                previous = old[job['id']]
                for key in ('id','source_id','employer','first_discovered_at'):
                    assert job.get(key) == previous.get(key), (key,job['id'])
                if previous['status']=='open':
                    assert job['status']=='open', job['id']
                if job['source_id'] != source['id']:
                    assert job == baseline_jobs[job['id']], job['id']
            inventory_delta = dict(company_id=payload['company_id'],
                raw_published_count=len(Replay(path).json(next(r['url'] for r in payload['responses'] if '/jobs?content=true' in r['url']))['jobs']), records_inspected=after['report']['records_inspected'],
                before_report=before['report'], after_report=after['report'],
                after_hr_jobs=after['jobs'],
                global_before=dict(Counter(j['status'] for j in original['jobs'])),
                global_after=dict(Counter(j['status'] for j in changed['jobs'])),
                two_collections_idempotent=True, identities_and_existing_open_preserved=True)
        rows.append(row)
    assert inventory_delta is not None
    verified_before = sum('proof' in r['baseline'] for r in rows)
    verified_after = sum('proof' in r['after'] for r in rows)
    report = dict(scope='8 known HR candidates; full official inventory replay only for configured Greenhouse source; no full crawl of other 7',
                  production_catalog_modified=False, shortlist_count=len(selection['shortlist']), analyzed_companies=len(rows),
                  baseline_company_states=dict(Counter(r['state'] for r in selection['shortlist'] if r['batch'])),
                  company_coverage_delta=dict(partial_to_collected=['hunter-douglas-talent-programs'], other_seven='inventory not recollected; no complete-coverage claim'),
                  candidate_count=len(rows), newly_discovered_hr=0,
                  verified_before=verified_before, verified_after=verified_after,
                  unverified_before=len(rows)-verified_before, unverified_after=len(rows)-verified_after,
                  conversion_before=verified_before/len(rows), conversion_after=verified_after/len(rows),
                  live_requests=sum(r['live_requests'] for r in rows), rows=rows, inventory_replay=inventory_delta)
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ('analyzed_companies','verified_before','verified_after','newly_discovered_hr','live_requests')}))
    return report


if __name__ == '__main__':
    run(REPORT/'comparison.json')
