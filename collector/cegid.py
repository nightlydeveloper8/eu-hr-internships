"""Reviewed Cegid public search response; no candidate or account operations.

The official Nuxt client publishes /nl/annonce/:jobSlug and getJobAds uses
POST /public/v1/careers-site/job-ads. Only that exact search template is
allowed by rendering.py. Scope/count mismatch remains partial; no closures.
"""
import re
from urllib.parse import urlsplit,parse_qs
from .classify import plain
from .employer_pages import approved
from .universal import Inventory

NL_PARKS={'57783','57789','57775','57787','57777','57785','57781','57779','57773'}

def inventory_records(data,source,index_url):
    parsed=urlsplit(index_url)
    choices=set(parse_qs(parsed.query).get('customFieldMcqChoice',[''])[0].split(','))
    if parsed.hostname!='jobs.workatcenterparcs.com' or parsed.path!='/nl/annonces' or not choices or not choices<=NL_PARKS:
        raise ValueError('Unreviewed Cegid inventory scope or country')
    if not isinstance(data,dict) or type(data.get('count')) is not int or data['count']<0 or not isinstance(data.get('items'),list):
        raise ValueError('Cegid inventory count/items unavailable')
    records={}
    for item in data['items']:
        if (not isinstance(item,dict) or item.get('is_external') is not False or item.get('is_aggregated') is not False
            or item.get('career_domain')!=parsed.hostname or type(item.get('job_ad_id')) is not int):
            raise ValueError('Unreviewed Cegid external/aggregated posting')
        slug=item.get('url','');identifier=str(item['job_ad_id'])
        if not re.fullmatch(re.escape(identifier)+r'-[a-z0-9-]+',slug) or not item.get('title') or not item.get('location'):
            raise ValueError('Cegid posting identity/title/location unavailable')
        url=approved('https://'+parsed.hostname+'/nl/annonce/'+slug,source)
        if identifier in records:raise ValueError('Duplicate Cegid requisition in inventory page')
        records[identifier]=dict(source_id=source['id'],external_id=identifier,posting_identifier=identifier,
            employer=source['employer'],title=plain(item['title']),location=plain(item['location']),city=plain(item['location']),
            country='NL',countries=['NL'],url=url,apply_url=url,text='',language=None,published_at=None,
            employment=plain(item.get('contract','')),work_mode=None,needs_page=False,
            inventory_evidence='current-employer-feed')
    if len(records)>data['count']:raise ValueError('Cegid inventory count contradicts records')
    return list(records.values()),dict(url=index_url,declared_job_count=data['count'],observed_jobs=len(records),complete=len(records)==data['count'])

def index_records(source,client):
    from .rendering import render_pages
    records={};scopes=[]
    for url in source['index_urls']:
        url=approved(url,source);responses=[]
        render_pages(url,client,lambda target:urlsplit(target).hostname in source['allowed_hosts'],
            limit=1,cegid_search=True,cegid_responses=responses)
        if len(responses)!=1:raise ValueError('Cegid public search response unavailable')
        rows,scope=inventory_records(responses[0],source,url);scopes.append(scope)
        for row in rows:
            if row['external_id'] in records and row!=records[row['external_id']]:raise ValueError('Cegid posting changed between scopes')
            records[row['external_id']]=row
    complete=bool(scopes) and all(scope['complete'] for scope in scopes)
    return Inventory(records.values(),dict(status='ok' if complete else 'partial',complete=complete,
        closure_complete=False,pages_read=len(scopes),job_urls_discovered=len(records),observed_scopes=scopes,
        discovery_scope=source['discovery_scope'],explicit_empty=complete and not records))
