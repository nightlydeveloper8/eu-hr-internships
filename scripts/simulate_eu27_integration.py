"""Offline two-cycle simulation of the reviewed bundle; never updates production. Requires the original scratch GET captures."""
import sys,json,gzip,tempfile,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from collector.pipeline import process_source,finalize
from collector.classify import canonical_url

def main():
    P=ROOT/'docs/eu27-expansion';raw=Path('/tmp/pp-eu27-feed-review-20261116')
    b=json.loads((P/'reviewed-integration-bundle.json').read_text());f=json.loads((P/'feed-review-2026-11-16.json').read_text());feeds={r['name']:r for r in f['rows']};apps={}
    for name in ['strict-application-review-2026-11-16.json','strict-application-review-2026-11-16-addendum.json']:
     for r in json.loads((P/name).read_text())['rows']:apps[r['name']]=r
    parts=[]
    for source in b['sources']:
     row=feeds[source['employer']];phase='strict-application-addendum' if source['employer']=='Ibexa' else 'strict-application-phase'
     responses={}
     for folder,events in [(raw/row['action_id'],row['events']),(raw/phase/row['action_id'],apps[source['employer']]['events'])]:
      for e in events:
       if e.get('scratch_file'):responses[canonical_url(e['url'])]=(folder/e['scratch_file'],e)
     class Replay:
      def request(self,url,method='GET',**kwargs):
       if method!='GET':raise AssertionError('Unexpected non-GET')
       path,e=responses[canonical_url(url)];return gzip.decompress(path.read_bytes()),e['status'],e['final_url']
     parts.append(process_source(source,Replay(),row['checked_at']))
    prior=json.loads((ROOT/'data/catalog.json').read_text());oldids={j['id'] for j in prior['jobs']};stamp=max(r['checked_at'] for r in feeds.values());registry=json.loads((ROOT/'data/sources.json').read_text())+b['sources']
    with tempfile.TemporaryDirectory() as tmp:
     after,_=finalize(registry,b['sources'],prior,{},parts,stamp,Path(tmp))
     again,_=finalize(registry,b['sources'],after,{},parts,stamp,Path(tmp)/'again')
    newids={j['id'] for j in after['jobs']};counts=lambda c:sum(j['status']=='open' and j.get('verification',{}).get('state')=='verified' for j in c['jobs'])
    r=dict(mode='offline-two-cycle-simulation-not-production-or-live-verification',baseline_catalog_updated_at=prior['updated_at'],before_records=len(oldids),after_records=len(newids),before_open_verified=counts(prior),after_open_verified=counts(after),old_ids_preserved=oldids.issubset(newids),two_cycles_idempotent=after['jobs']==again['jobs'],new_jobs=[dict(id=j['id'],title=j['title'],employer=j['employer'],countries=j['countries'],status=j['status']) for j in after['jobs'] if j['id'] not in oldids],network_requests=0)
    (P/'integration-simulation-2026-11-16.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps(r,ensure_ascii=False))

if __name__=='__main__':main()
