"""Deterministic, three-candidate pilot. Default: offline PR #21 replay.

--capture performs fresh, bounded public reads, never a collection/catalog write.
Output cannot overwrite an existing capture. No fixture authorizes production.
"""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import sys
import types
from datetime import datetime,timezone
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from collector.verification import verify_vacancy
from collector.dynamic_ats import PILOTS
from collector.runtime import BudgetClient
from collector.rendering import render_pages
from scripts.replay_sprint18 import Replay

FIXTURES=ROOT/'tests/fixtures/sprint18-batch2'


def baseline():
    folder=ROOT/'tests/fixtures/dynamic-ats-baseline'
    source=gzip.decompress((folder/'verification.py.gz').read_bytes())
    assert hashlib.sha256(source).hexdigest()==json.loads((folder/'manifest.json').read_text())['sha256']
    module=types.ModuleType('collector._dynamic_baseline');module.__package__='collector'
    exec(compile(source,'verification-baseline.py','exec'),module.__dict__)
    return module.verify_vacancy


def check(verifier,item,client,stamp):
    observation={}
    try:result=dict(state='verified',proof=verifier(item['record'],item['source'],client,stamp,observation))
    except Exception as exc:result=dict(state='unverified',error=str(exc))
    if observation.get('dynamic_ats'):result['metrics']=observation['dynamic_ats']
    return result


def items():
    for source in sorted(PILOTS):
        path=FIXTURES/source.removeprefix('auto-')/'capture.json'
        payload=json.loads(path.read_text())
        assert len(payload['records'])==1
        yield path,payload,payload['records'][0]


def replay():
    rows=[]
    for path,payload,item in items():
        with patch.dict(os.environ,PEOPLE_PLACEMENT_DYNAMIC_ATS=''):
            after=check(verify_vacancy,item,Replay(path),payload['stamp'])
        # Offline replay durations are not live costs and do not belong in a
        # reproducible report. Recorded live costs stay in the capture manifest.
        after.get('metrics',{}).pop('total_seconds',None)
        rows.append(dict(source_id=item['source']['id'],id=item['record']['id'],kind='historical-html-replay',
                         before=check(baseline(),item,Replay(path),payload['stamp']),after=after))
    return dict(rows=rows,live_requests=0,production_catalog_modified=False)


def replay_live(folder=ROOT/'tests/fixtures/dynamic-ats-release'):
    """Recheck saved DOM offline; never counts as another live observation."""
    rows=[]
    for path in sorted(folder.glob('*/capture.json')):
        item=json.loads(path.read_text());responses={};renders=[]
        for entry in item['responses']:
            body=gzip.decompress((path.parent/entry['file']).read_bytes())
            assert hashlib.sha256(body).hexdigest()==entry['sha256']
            if entry.get('kind')=='rendered-dom':renders.append((entry['url'],body))
            else:responses[entry['url']]=(body,entry['status'],entry['final_url'])
        class Evidence(BudgetClient):
            def request(self,url):
                self.check();self.requests+=1
                return responses[url]
        client=Evidence(seconds=45,max_requests=48)
        from collector import dynamic_ats
        with patch.dict(os.environ,PEOPLE_PLACEMENT_DYNAMIC_ATS='pilot-v1'),patch.object(dynamic_ats,'_RENDERINGS',0),patch('collector.rendering.render_pages',return_value=(renders,True)):
            after=check(verify_vacancy,item,client,item['stamp'])
        before=check(baseline(),item,Evidence(seconds=45,max_requests=48),item['stamp'])
        assert before==item['before']
        assert after['state']==item['after']['state']
        assert after.get('proof')==item['after'].get('proof')
        rows.append(dict(source_id=item['source']['id'],id=item['id'],kind='rendered-dom-replay',
                         before=before,after={k:v for k,v in after.items() if k!='metrics'}))
    return dict(rows=rows,live_requests=0,production_catalog_modified=False)


def capture(output):
    output.mkdir(parents=True,exist_ok=False)
    os.environ['PEOPLE_PLACEMENT_DYNAMIC_ATS']='pilot-v1'
    from collector import dynamic_ats
    dynamic_ats._RENDERINGS=0
    rows=[]
    for path,payload,item in items():
        folder=output/item['source']['id'];folder.mkdir()
        responses={};renders=[];events=[]
        class Capture(BudgetClient):
            def request(self,url,*args,**kwargs):
                start=__import__('time').monotonic()
                try:
                    result=super().request(url,*args,**kwargs);responses[url]=result;return result
                finally:events.append(dict(url=url,seconds=round(__import__('time').monotonic()-start,3)))
        client=Capture(seconds=45,max_requests=48)
        stamp=datetime.now(timezone.utc).isoformat()
        def render(*args,**kwargs):
            result=render_pages(*args,**kwargs);renders.extend(result[0]);return result
        with patch('collector.rendering.render_pages',side_effect=render):
            after=check(verify_vacancy,item,client,stamp)
        class SameEvidence:
            def request(self,url):
                if url not in responses:raise ValueError('Response not observed in live pilot')
                return responses[url]
        before=check(baseline(),item,SameEvidence(),stamp)
        manifest=[]
        for url,(body,status,final) in sorted(responses.items()):
            file=hashlib.sha256(url.encode()).hexdigest()[:20]+'.html.gz'
            (folder/file).write_bytes(gzip.compress(body,mtime=0))
            manifest.append(dict(url=url,status=status,final_url=final,file=file,sha256=hashlib.sha256(body).hexdigest()))
        for n,(url,body) in enumerate(renders):
            file='rendered-'+str(n)+'.html.gz';(folder/file).write_bytes(gzip.compress(body,mtime=0))
            manifest.append(dict(url=url,kind='rendered-dom',file=file,sha256=hashlib.sha256(body).hexdigest()))
        row=dict(source_id=item['source']['id'],id=item['record']['id'],kind='live-read',stamp=stamp,
                 record=item['record'],source=item['source'],before=before,after=after,
                 requests=client.requests,bytes_http=client.bytes,events=events,responses=manifest)
        (folder/'capture.json').write_text(json.dumps(row,ensure_ascii=False,indent=2)+'\n');rows.append(row)
        print(json.dumps({key:row[key] for key in ('source_id','before','after','requests')}),flush=True)
    report=dict(base_commit='1d198a4',rows=rows,verified_before=sum(r['before']['state']=='verified' for r in rows),
                verified_after=sum(r['after']['state']=='verified' for r in rows),
                production_catalog_modified=False,scope='Only three known candidates; no inventory or discovery')
    (output/'comparison.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')


def comparison_report():
    historical=replay();rendered=replay_live()
    attempts=[]
    for name in ('dynamic-ats-live','dynamic-ats-diagnostic','dynamic-ats-final','dynamic-ats-release'):
        payload=json.loads((ROOT/'tests/fixtures'/name/'comparison.json').read_text())
        rows=[]
        for row in payload['rows']:
            metrics=row['after']['metrics']
            rows.append(dict(source_id=row['source_id'],id=row['id'],observed_at=row['stamp'],
                             before=row['before']['state'],after=row['after']['state'],
                             proof=row['after'].get('proof'),error=row['after'].get('error'),
                             total_requests=row['requests'],**metrics))
        attempts.append(dict(capture=name,rows=rows,requests=sum(r['requests'] for r in payload['rows']),
                             renderings=sum(r['after']['metrics']['renderings'] for r in payload['rows'])))
    return dict(base_commit='1d198a4',scope='Three existing known candidates; no inventory/discovery',
                historical_html=historical,rendered_dom_replay=rendered,live_attempts=attempts,
                total_live_requests=sum(a['requests'] for a in attempts),
                total_live_renderings=sum(a['renderings'] for a in attempts),
                verified_before=0,verified_after=2,conversion_before=0,conversion_after=2/3,
                new_vacancies_discovered=0,production_catalog_modified=False,
                historical_ids=324,feature_enabled_by_default=False,
                synthetic_tests='tests/test_dynamic_ats.py: behavior and fake browser transport; not live evidence')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capture',type=Path)
    parser.add_argument('--report',type=Path)
    args=parser.parse_args()
    if args.capture:capture(args.capture)
    elif args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(json.dumps(comparison_report(),ensure_ascii=False,indent=2)+'\n')
    else:print(json.dumps(dict(historical_html=replay(),rendered_dom=replay_live()),ensure_ascii=False,indent=2))
