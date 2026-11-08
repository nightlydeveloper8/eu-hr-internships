"""Compare main and the fix on identical official responses, strictly offline.

Only known-candidate verification is replayed, not a complete source inventory.
Frozen pages must never be used to renew production verification.
"""
from collections import Counter
import copy
import gzip
import hashlib
import json
import sys
import tempfile
import types
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.coverage_sprint18_batch2 import FIXTURES, REPORT, write
from scripts.replay_sprint18 import Replay
from collector.pipeline import finalize
from collector.verification import verify_vacancy, blocked_error


def baseline_verifier():
    manifest=json.loads((FIXTURES/'baseline.json').read_text())
    body=gzip.decompress((FIXTURES/'verification-before.py.gz').read_bytes())
    assert hashlib.sha256(body).hexdigest()==manifest['verification_sha256']
    module=types.ModuleType('collector._sprint18_baseline')
    module.__package__='collector'
    exec(compile(body,'verification-before.py','exec'),module.__dict__)
    return module.verify_vacancy


def check(verifier,item,client,stamp):
    try:return dict(proof=verifier(item['record'],item['source'],client,stamp))
    except ValueError as exc:return dict(error=str(exc))


def replay(output=None):
    if sys.version_info < (3,12):raise RuntimeError('Use Python 3.12+, as in CI (ISO dates and HTTP 308)')
    selection=json.loads((REPORT/'ranking.json').read_text())
    manifest=json.loads((FIXTURES/'baseline.json').read_text())
    body=gzip.decompress((FIXTURES/'catalog-before.json.gz').read_bytes())
    assert hashlib.sha256(body).hexdigest()==manifest['catalog_sha256']
    prior=json.loads(body)
    before_verifier=baseline_verifier()
    rows=[]
    captures=sorted(FIXTURES.glob('*/capture.json'))
    assert {p.parent.name for p in captures}=={r['company_id'] for r in selection['shortlist'] if r['selected']}
    for path in captures:
        payload=json.loads(path.read_text())
        for item in payload['records']:
            before_client,after_client=Replay(path),Replay(path)
            before=check(before_verifier,item,before_client,payload['stamp'])
            after=check(verify_vacancy,item,after_client,payload['stamp'])
            assert before==item['before'],(payload['company_id'],before,item['before'])
            assert after==check(verify_vacancy,item,Replay(path),payload['stamp'])
            rows.append(dict(company_id=payload['company_id'],id=item['record']['id'],
                             vacancy_url=item['record']['url'],source_id=item['source']['id'],
                             observed_at=payload['stamp'],before=before,after=after,
                             before_requests=before_client.calls,after_requests=after_client.calls))
    stamp=max(r['observed_at'] for r in rows)
    selected_ids={r['source_id'] for r in rows}
    registry=json.loads((ROOT/'data/sources.json').read_text())
    selected=[s for s in registry if s['id'] in selected_ids]
    old={j['id']:j for j in prior['jobs']}

    def parts(which):
        result=[]
        for source in selected:
            jobs=[]
            for row in rows:
                if row['source_id']!=source['id']:continue
                job=copy.deepcopy(old[row['id']])
                proof=row[which].get('proof')
                state='verified' if proof else 'blocked' if blocked_error(ValueError(row[which]['error'])) else 'incomplete'
                job.update(status='open' if proof else 'unverified',last_seen_at=stamp,
                           last_verified_at=stamp if proof else None,link_status=state,
                           verification=dict(state=state,policy_version=2,
                                             checked_at=stamp,reason=proof['method'] if proof else row[which]['error']))
                if proof:job.update(apply_url=proof['url'],application_verification=dict(proof,checked_at=stamp))
                jobs.append(job)
            result.append(dict(jobs=jobs,report=dict(id=source['id'],status='partial',records_inspected=len(jobs),
                                                   complete=False,closure_complete=False),closure_eligible=[]))
        return result

    with tempfile.TemporaryDirectory() as folder:
        before,_=finalize(registry,selected,copy.deepcopy(prior),{'sources':[]},parts('before'),stamp,Path(folder)/'before')
        after,_=finalize(registry,selected,copy.deepcopy(prior),{'sources':[]},parts('after'),stamp,Path(folder)/'after')
        second,_=finalize(registry,selected,copy.deepcopy(after),{'sources':[]},parts('after'),stamp,Path(folder)/'second')
    assert after['jobs']==second['jobs']
    assert set(old)=={j['id'] for j in after['jobs']}
    baseline_jobs={j['id']:j for j in before['jobs']}
    candidate_ids={r['id'] for r in rows}
    for job in after['jobs']:
        previous=old[job['id']]
        for key in ('id','source_id','employer','first_discovered_at','identity_aliases','ownership_review'):
            assert job.get(key)==previous.get(key),(job['id'],key)
        if previous['status']=='open':assert job['status']=='open'
        if previous['status']=='closed':assert job['status']=='closed'
        if job['id'] not in candidate_ids:assert job==baseline_jobs[job['id']]
    report=dict(base_commit=manifest['commit'],scope='Known-candidate verification only; no complete inventory or discovery claim',
                production_catalog_modified=False,shortlist_count=17,analyzed_companies=len(captures),candidate_count=len(rows),
                baseline_company_states=dict(Counter(r['state'] for r in selection['shortlist'] if r['selected'])),
                live_requests=sum(json.loads(p.read_text())['requests'] for p in captures),
                source_costs=[dict(company_id=p.parent.name,requests=(d:=json.loads(p.read_text()))['requests'],
                                   bytes_read=d['bytes_read'],seconds=round(sum(e['seconds'] for e in d['events'] if not e['url'].endswith('/robots.txt')),3)) for p in captures],
                verified_before=sum('proof' in r['before'] for r in rows),verified_after=sum('proof' in r['after'] for r in rows),
                new_hr_discovered=0,rows=rows,
                global_before=dict(Counter(j['status'] for j in before['jobs'])),
                global_after=dict(Counter(j['status'] for j in after['jobs'])),
                two_finalizations_idempotent=True,ids_ownership_aliases_and_existing_open_preserved=True)
    report.update(unverified_before=len(rows)-report['verified_before'],unverified_after=len(rows)-report['verified_after'],
                  conversion_before=report['verified_before']/len(rows),conversion_after=report['verified_after']/len(rows))
    if output:write(output,report)
    return report


if __name__=='__main__':
    report=replay(REPORT/'comparison.json')
    print(json.dumps({k:report[k] for k in ('analyzed_companies','candidate_count','verified_before','verified_after','global_before','global_after','live_requests')}))
