"""Employer ownership is separate from link/application availability."""
from urllib.parse import urlsplit
from .classify import fold,canonical_url
from .employer_resolution import is_reviewed_publisher, name_key

def employer_matches(name,source,url=None):
    key=name_key(name)
    if key in {name_key(n) for n in [source['employer']]+source.get('employer_aliases',[])}:
        return True
    return is_reviewed_publisher(name,source,url)

def owned_record(record,source):
    name=record.get('employer','')
    url=record.get('url')
    if not employer_matches(name,source,url):return False
    # Approved recruiting publishers are not equivalent to subsidiaries. A
    # structured same-vacancy hiringOrganization is required on the reviewed host.
    if is_reviewed_publisher(name,source,url) and record.get('employer_identity_evidence')!='jobposting-hiring-organization':
        return False
    if source.get('require_employer_identity') and record.get('employer_identity_evidence')!='jobposting-hiring-organization':return False
    return (urlsplit(record['url']).hostname in source['allowed_hosts'] or
            record.get('employer_identity_evidence')=='jobposting-hiring-organization')

def apply_ownership_reviews(jobs,reviews):
    by_url={canonical_url(r['url']):r for r in reviews}
    result=[]
    for job in jobs:
        review=by_url.get(canonical_url(job['url']))
        if review:
            job=dict(job)
            job.update(id=review['catalog_id'],source_id=review['source_id'],
                source_name=review['employer'],employer=review['employer'],source_type='recruitee',
                external_id=review['external_id'])
            job['ownership_review']=dict(evidence_url=review['evidence_url'],
                reviewed_on=review['reviewed_on'],original_source_id=review['original_source_id'])
            job['duplicate_source_ids']=[s for s in job.get('duplicate_source_ids',[])
                if s!=review['original_source_id']]
            if not job['duplicate_source_ids']:job.pop('duplicate_source_ids')
        result.append(job)
    return result

def quarantine_historical_external_jobs(jobs, registry):
    """Preserve but flag old third-party jobs attributed to a restricted employer.

    A previous crawler may have followed a student/referral portal and stored
    postings under the referring university. The new reviewed-hosts policy
    rejects these during discovery; that alone cannot repair *historical*
    catalog rows, which remain in the cumulative archive. Only an individual
    positive ownership review may transfer those records to an actual employer.
    No network, mass deletion, closing, or ownership guess happens here.
    """
    sources={source['id']:source for source in registry if source.get('id')}
    flagged=[]
    for original in jobs:
        source=sources.get(original.get('source_id'))
        host=urlsplit(original.get('url') or '').hostname
        if (not source or not host or
            not (source.get('ownership_scope')=='reviewed-hosts' or source.get('require_employer_identity')) or
            host in source.get('allowed_hosts',[]) or original.get('ownership_review')):
            flagged.append(original)
            continue
        job=dict(original)
        job['ownership_risk']=dict(state='historical-unreviewed-external-host',
                                   original_source_id=source['id'], observed_host=host)
        job['review_note']='Historical external job-board link; original employer ownership and direct application require individual evidence'
        if job.get('status')!='closed':
            job['status']='unverified'
            job['link_status']='review-required'
            job['last_verified_at']=None
            job['verification']=dict(job.get('verification') or {},
                policy_version=2,state='incomplete',
                reason='Historical external URL outside source reviewed employer hosts; official vacancy ownership not established')
        flagged.append(job)
    return flagged
