"""Bounded review of the 29 proposed feeds; explicit --live only.

GET-only, 12 logical requests/45 seconds per employer, four workers, exact
observed ATS/feed hosts. No registry/catalog writes, no browser, no submit.
Raw metadata responses stay in a user-specified scratch directory.
"""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import gzip, hashlib, json, re, sys, time
from pathlib import Path
from urllib.parse import urlsplit, urljoin

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from collector.adapters import collect
from collector.runtime import BudgetClient
from collector.universal import Document
from collector.classify import classify_role, canonical_url
from collector.pipeline import record_countries
from collector.verification import verify_vacancy


def config(proposal):
    host=urlsplit(proposal['observed_url']).hostname
    s=dict(id='eu27-'+proposal['action_id'],employer=proposal['name'],adapter=proposal['adapter'],
        enabled=False,career_url=proposal['observed_url'],allowed_hosts=[host],
        max_requests=12,collection_seconds=45)
    if proposal.get('candidate_feed_url'):s['feed_url']=proposal['candidate_feed_url']
    elif proposal['adapter']=='greenhouse':
        s.update(board=proposal['candidate_board']);s['allowed_hosts'].append('boards-api.greenhouse.io')
    elif proposal['adapter']=='lever':
        s.update(board=proposal['candidate_board']);s['allowed_hosts'].append('api.lever.co')
    return s


class Recorder(BudgetClient):
    def __init__(self,folder,hosts,seconds=45,max_requests=12):
        super().__init__(seconds=seconds,max_requests=max_requests);self.folder=folder;folder.mkdir(parents=True,exist_ok=True)
        self.events=[];self.hosts=set(hosts)
        self.redirect_scope_allowed=lambda u:urlsplit(u).hostname in self.hosts
    def request(self,url,method='GET',**kwargs):
        if method!='GET':raise ValueError('Review allows GET only')
        if urlsplit(url).hostname not in self.hosts:raise ValueError('Review URL outside exact host scope')
        t=time.monotonic();event=dict(url=url,method=method)
        try:
            result=super().request(url,method=method,**kwargs);body,status,final=result
            key=hashlib.sha256(url.encode()).hexdigest()[:24]+'.gz'
            (self.folder/key).write_bytes(gzip.compress(body,mtime=0))
            event.update(status=status,final_url=final,sha256=hashlib.sha256(body).hexdigest(),scratch_file=key,bytes=len(body))
            return result
        except Exception as e:event['error']=type(e).__name__+': '+str(e)[:200];raise
        finally:event['seconds']=round(time.monotonic()-t,3);self.events.append(event)


def review(proposal,folder):
    s=config(proposal);client=Recorder(folder/proposal['action_id'],s['allowed_hosts']);t=time.monotonic()
    row=dict(action_id=proposal['action_id'],name=proposal['name'],adapter=s['adapter'],
        checked_at=datetime.now(timezone.utc).isoformat(),source_proposal=s,
        inventory_state='not-established',ownership_state='not-established',admissible=False,
        jobs=[],corporate_link_candidates=[],new_verified=0,production_enabled=False)
    try:
        records=collect(s,client)
        row.update(inventory_state='complete-feed-read',records=len(records),
            feed_scope='All records returned by existing adapter; national coverage still requires posting geography',
            observed_job_hosts=sorted({urlsplit(r['url']).hostname for r in records}))
        for r in records:
            role=classify_role(r['title'],r.get('text',''),r.get('employment',''))
            if role:
                row['jobs'].append(dict(external_id=r['external_id'],title=r['title'],url=r['url'],
                    countries=record_countries(r),internship_type=role['internship_type']))
        body,_,final=client.request(proposal['observed_url']);doc=Document(body,final)
        row['observed_page']=dict(url=final,headings=doc.h1,structured_employers=[p.get('hiringOrganization') for p in doc.jobposts()])
        for href,label,_ in doc.links:
            target=urljoin(final,href);host=urlsplit(target).hostname
            if urlsplit(target).scheme=='https' and host not in s['allowed_hosts'] and not re.search(r'linkedin|facebook|instagram|twitter|youtube|recruitee|personio|greenhouse|lever|google|cookie|privacy|whatsapp|tiktok',host or '',re.I):
                row['corporate_link_candidates'].append(dict(url=target,label=label.strip()[:100]))
        # Application verification is a technical observation until ownership
        # has a separate official employer->ATS proof. It never updates catalog.
        candidates=[r for r in records if (classify_role(r['title'],r.get('text',''),r.get('employment','')) or {}).get('internship_type')=='internship']
        for r in candidates[:3]:
            attempt=dict(title=r['title'],url=r['url'],external_id=r['external_id'])
            try:attempt['application_proof']=verify_vacancy(r,s,client,row['checked_at'])
            except Exception as e:attempt['error']=type(e).__name__+': '+str(e)[:220]
            row.setdefault('application_attempts',[]).append(attempt)
            if client.remaining()<1 or client.requests>=client.max_requests:break
    except Exception as e:row['error']=type(e).__name__+': '+str(e)[:240]
    row.update(requests=client.requests,bytes_read=client.bytes,duration_seconds=round(time.monotonic()-t,3),events=client.events)
    return row


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--live',action='store_true')
    p.add_argument('--scratch',type=Path,default=Path('/tmp/pp-eu27-feed-review-20261116'))
    p.add_argument('--output',type=Path,default=ROOT/'docs/eu27-expansion/feed-review-2026-11-16.json')
    a=p.parse_args(argv);b=json.loads((ROOT/'docs/eu27-expansion/batch-01.json').read_text());proposals=b['adapter_proposals']
    if not a.live:print(json.dumps(dict(mode='offline-preview',proposals=len(proposals))));return
    if a.output.exists():raise ValueError('Evidence already exists; no silent refresh')
    t=time.monotonic()
    with ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(lambda x:review(x,a.scratch),proposals))
    report=dict(schema_version=1,mode='bounded-feed-and-application-review-no-production-writes',base_commit=b['base_commit'],
        checked_at=datetime.now(timezone.utc).isoformat(),limits=dict(per_employer_requests=12,per_employer_seconds=45,workers=4,renderings=0),
        summary=dict(employers=len(rows),inventories=dict(Counter(r['inventory_state'] for r in rows)),
            records=sum(r.get('records',0) for r in rows),hr_student_roles=sum(len(r['jobs']) for r in rows),
            technical_application_proofs=sum('application_proof' in a for r in rows for a in r.get('application_attempts',[])),
            requests=sum(r['requests'] for r in rows),bytes_read=sum(r['bytes_read'] for r in rows),
            source_seconds=round(sum(r['duration_seconds'] for r in rows),3),wall_seconds=round(time.monotonic()-t,3),
            new_verified=0,new_enabled_sources=0),
        counting_note='Logical requests include robots, not every redirect; technical application proof alone does not establish employer ownership.',rows=rows)
    a.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report['summary']))

if __name__=='__main__':main()
