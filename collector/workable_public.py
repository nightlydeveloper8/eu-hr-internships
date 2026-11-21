"""Uncredentialed published Workable board inventory; never submits applications."""
import json, re
from urllib.parse import urlsplit
from .classify import plain
from .employer_pages import approved

def workable_public_records(source, client):
    board=source.get('board','')
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,99}',board):
        raise ValueError('Invalid reviewed Workable board')
    expected='https://www.workable.com/api/accounts/'+board+'?details=true'
    redirect='https://apply.workable.com/api/v1/widget/accounts/'+board+'?details=true'
    if source.get('feed_url')!=expected:
        raise ValueError('Only reviewed public Workable inventory is supported')
    approved(expected,source)
    previous=getattr(client,'redirect_scope_allowed',None)
    redirects=set()
    def allowed_redirect(url):
        if url!=redirect or url in redirects or (previous is not None and not previous(url)):
            return False
        if hasattr(client,'check') and hasattr(client,'requests'):
            client.check()
            client.requests+=1
        redirects.add(url)
        return True
    client.redirect_scope_allowed=allowed_redirect
    try:
        body,_,final=client.request(expected,accept='application/json')
    finally:
        if previous is None: del client.redirect_scope_allowed
        else: client.redirect_scope_allowed=previous
    if final not in (expected,redirect): raise ValueError('Workable inventory redirected')
    payload=json.loads(body)
    if not isinstance(payload,dict) or not isinstance(payload.get('jobs'),list):
        raise ValueError('Invalid Workable public inventory')
    if len(payload['jobs'])>1000 or payload.get('next') or payload.get('next_page') or payload.get('paging'):
        raise ValueError('Workable inventory requires pagination review')
    rows=[]; seen=set()
    for job in payload['jobs']:
        ident=job.get('shortcode') if isinstance(job,dict) else None
        if not isinstance(ident,str) or not re.fullmatch(r'[A-Z0-9]{10}',ident) or ident in seen:
            raise ValueError('Invalid or duplicate Workable shortcode')
        seen.add(ident)
        title=plain(job.get('title') or '')
        if not title: raise ValueError('Workable position has no title')
        for key in ('url','application_url'):
            raw=urlsplit(job.get(key) or '')
            if raw.query or raw.fragment: raise ValueError('Workable posting URL contains query or fragment')
            address=approved(job.get(key) or '',source);parsed=urlsplit(address)
            if (parsed.hostname!='apply.workable.com' or parsed.query or parsed.fragment or
                not re.fullmatch(r'/(?:'+re.escape(board)+r'/)?j/'+ident+(r'/apply' if key=='application_url' else '')+r'/?',parsed.path)):
                raise ValueError('Workable URL does not match board and shortcode')
        vacancy=job['url']
        city=plain(job.get('city') or '');country=plain(job.get('country') or '')
        rows.append(dict(source_id=source['id'],external_id=ident,posting_identifier=ident,
                         employer=source['employer'],title=title,location=', '.join(x for x in (city,country) if x),
                         text=plain(job.get('description') or ''),url=vacancy,apply_url=vacancy,
                         observed_application_url=job['application_url'],inventory_evidence='current-employer-feed',
                         employment=job.get('employment_type') or '',city=city,country=None,
                         published_at=job.get('published_on'),language=None,work_mode=None))
    from .universal import Inventory
    return Inventory(rows,dict(status='ok',complete=False,closure_complete=False,pages_read=1,
                     feed_records=len(rows),published_records=len(rows),
                     discovery_scope='workable-public-feed-no-absence-closure'))
