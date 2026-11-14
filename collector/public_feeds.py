"""Documented public recruiting feeds; only job metadata leaves this module."""
import xml.etree.ElementTree as ET
from .classify import plain
from .employer_pages import approved

def personio_records(source,client):
    url=approved(source['feed_url'],source);body,_,final=client.request(url);approved(final,source)
    if b'<!DOCTYPE' in body.upper():raise ValueError('DOCTYPE not permitted')
    root=ET.fromstring(body)
    if root.tag!='workzag-jobs':raise ValueError('Not a Personio jobs feed')
    base=final.split('/xml',1)[0];out=[]
    for j in root.findall('position'):
        identifier=j.findtext('id','')
        if not identifier.isdigit():raise ValueError('Malformed position ID')
        offices=[j.findtext('office','')]+[x.text or '' for x in j.findall('additionalOffices/office')]
        text=' '.join(plain(x.findtext('name','')+' '+x.findtext('value','')) for x in j.findall('jobDescriptions/jobDescription'))
        job_url=approved(base+'/job/'+identifier,source)
        out.append(dict(inventory_evidence='current-employer-feed',source_id=source['id'],external_id=identifier,employer=source['employer'],title=plain(j.findtext('name')),location='; '.join(offices),text=text,url=job_url,apply_url=job_url,language=None,published_at=None,employment=j.findtext('employmentType',''),city='; '.join(offices),country=None,work_mode=None))
    if len({x['external_id'] for x in out})!=len(out):raise ValueError('Duplicate positions')
    return out

def recruitee_records(source,client):
    body,_,final=client.request(approved(source['feed_url'],source));approved(final,source)
    import json
    data=json.loads(body)
    if not isinstance(data.get('offers'),list):raise ValueError('Not a Recruitee offers feed')
    if data.get('next') or data.get('next_page'):raise ValueError('Unreviewed pagination')
    out=[]
    for j in data['offers']:
        if j.get('status')!='published':continue
        url=approved(j['careers_url'],source)
        locations=j.get('locations') or [j]
        countries=sorted({x.get('country_code') for x in locations if x.get('country_code')})
        if not countries and j.get('country_code'):countries=[j['country_code']]
        cities=sorted({x.get('city') for x in locations if x.get('city')})
        # Keep a multi-country posting intact; downstream URL deduplication must
        # not erase any locations by collapsing country-specific copies.
        location='; '.join(cities+countries) or j.get('location','')
        out.append(dict(inventory_evidence='current-employer-feed',source_id=source['id'],external_id=str(j['id']),employer=source['employer'],title=plain(j['title']),location=location,text=plain((j.get('description') or '')+' '+(j.get('requirements') or '')),url=url,apply_url=url,countries=countries,language=None,published_at=None,employment=j.get('employment_type_code',''),city='; '.join(cities) or j.get('city'),country=countries[0] if len(countries)==1 else None,work_mode='remote' if j.get('remote') else 'hybrid' if j.get('hybrid') else None))
    if len({x['external_id'] for x in out})!=len(out):raise ValueError('Duplicate offers')
    if source.get('report_feed_scope'):
        from .universal import Inventory
        return Inventory(out,dict(status='ok',complete=True,closure_complete=False,pages_read=1,
            feed_records=len(data['offers']),published_records=len(out),
            discovery_scope=source.get('discovery_scope')))
    return out
