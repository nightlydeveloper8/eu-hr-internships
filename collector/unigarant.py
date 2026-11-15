"""Official public Unigarant search; discovery is separate from job verification."""
import re
from urllib.parse import urlsplit
from .classify import plain
from .employer_pages import approved
from .universal import Inventory


def inventory_records(data,source):
    if (not isinstance(data,dict) or data.get('success') is not True
        or type(data.get('total')) is not int or data['total']<0
        or not isinstance(data.get('vacancies'),list)):
        raise ValueError('Unigarant public inventory success/count/records unavailable')
    records={};urls=set()
    for item in data['vacancies']:
        if (not isinstance(item,dict) or type(item.get('id')) is not int or item['id']<=0
            or not isinstance(item.get('title'),str) or not item['title'].strip()
            or not isinstance(item.get('shortDescription'),str)
            or item.get('type') not in ('vacancy','student','event')):
            raise ValueError('Unigarant public record identity/title/type unavailable')
        url=approved(item.get('url',''),source);parsed=urlsplit(url)
        if parsed.hostname!='werkenbijunigarant.nl' or not re.fullmatch(r'/vacature/[a-z0-9-]+/?',parsed.path) or parsed.query:
            raise ValueError('Unreviewed Unigarant vacancy URL')
        identifier=str(item['id'])
        if identifier in records or url in urls:raise ValueError('Duplicate Unigarant inventory record')
        urls.add(url)
        records[identifier]=dict(source_id=source['id'],external_id=identifier,employer=source['employer'],
            title=plain(item['title']),text=plain(item['shortDescription']),url=url,apply_url=url,
            language=None,published_at=None,employment=item['type'],country=None,countries=[],city=None,
            location='',work_mode=None,needs_page=False,inventory_evidence='current-employer-feed')
    if len(records)>data['total']:raise ValueError('Unigarant count contradicts records')
    return list(records.values()),dict(declared_job_count=data['total'],observed_jobs=len(records),complete=len(records)==data['total'])


def index_records(source,client):
    from .rendering import render_pages
    records={};scopes=[]
    for url in source['index_urls']:
        url=approved(url,source)
        if urlsplit(url).netloc!='werkenbijunigarant.nl' or urlsplit(url).path.rstrip('/')!='/vacatures' or urlsplit(url).query:
            raise ValueError('Unreviewed Unigarant discovery scope')
        responses=[]
        render_pages(url,client,lambda target:urlsplit(target).hostname in source['allowed_hosts'],limit=1,
            unigarant_search=True,unigarant_responses=responses,index_error_pattern=source['index_error_pattern'])
        if len(responses)!=1:raise ValueError('Unigarant public search response unavailable')
        rows,scope=inventory_records(responses[0],source);scopes.append(dict(scope,url=url))
        for row in rows:
            if row['external_id'] in records and row!=records[row['external_id']]:raise ValueError('Unigarant inventory changed between scopes')
            records[row['external_id']]=row
    # Published short descriptions do not establish all duties, workplace or a
    # current application. Preserve narrower discovery evidence, never closures.
    return Inventory(records.values(),dict(status='partial',complete=False,closure_complete=False,
        pages_read=len(scopes),job_urls_discovered=len(records),observed_scopes=scopes,
        discovery_scope=source['discovery_scope'],explicit_empty=False))
