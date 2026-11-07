"""Employer ownership is separate from link/application availability."""
from urllib.parse import urlsplit
from .classify import fold,canonical_url

def employer_matches(name,source):
    def key(value):return ' '.join(fold(value).split())
    return key(name) in {key(n) for n in [source['employer']]+source.get('employer_aliases',[])}

def owned_record(record,source):
    if not employer_matches(record.get('employer',''),source):return False
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
