"""Documented public recruiting feeds; only job metadata leaves this module."""
import xml.etree.ElementTree as ET
from urllib.parse import urlsplit
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

def recruitee_public_xml_records(source,client):
    """Opt-in read-only Recruitee public XML feed, not authenticated Careers Site API.

    Only employer-published exact apply_url is accepted: never infer /c/new.
    Inventory evidence is bounded and deliberately never permits closure by
    absence. The caller still verifies the actual vacancy and form via v2.
    """
    if source.get('feed_format') != 'recruitee-public-xml' or source.get('application_check') != 'recruitee-linked':
        raise ValueError('Reviewed Recruitee XML and application gate required')
    url=approved(source['feed_url'],source)
    parsed_feed = urlsplit(url)
    if parsed_feed.path != '/api/feeds/offers.xml' or parsed_feed.query or parsed_feed.fragment:
        raise ValueError('Only reviewed public Recruitee XML path is supported')
    body,_,final=client.request(url)
    if final != url:
        raise ValueError('Public offers XML redirected')
    payload = body.decode('utf-8-sig')
    if '\0' in payload or '<!DOCTYPE' in payload.upper() or '<!ENTITY' in payload.upper():
        raise ValueError('Public offers XML must be UTF-8 without a DTD')
    root = ET.fromstring(payload)
    if root.tag!='offers' or len(root)>1000 or any(o.tag!='offer' for o in root):
        raise ValueError('Unexpected Recruitee XML inventory')
    records=[];seen=set()
    for item in root:
        values={child.tag:(child.text or '').strip() for child in item if len(child)==0}
        identifier=values.get('id','')
        title=plain(values.get('title',''))
        city=plain(values.get('city',''))
        country=values.get('country_code','')
        if not identifier.isdigit() or identifier in seen or not title or not country:
            raise ValueError('Malformed or duplicate Recruitee public offer')
        seen.add(identifier)
        vacancy=approved(values.get('careers_url',''),source)
        apply=approved(values.get('apply_url',''),source)
        vp=urlsplit(vacancy);ap=urlsplit(apply)
        if (vp.hostname!=ap.hostname or ap.query or ap.fragment
            or ap.path.rstrip('/')!=vp.path.rstrip('/')+'/c/new'):
            raise ValueError('Public XML did not publish matching vacancy application entry')
        records.append(dict(
            inventory_evidence='current-employer-feed',source_id=source['id'],
            external_id=identifier,posting_identifier=identifier,
            employer=source['employer'],title=title,location=city+', '+country,
            text=plain(values.get('description','')+' '+values.get('requirements','')),
            url=vacancy,apply_url=vacancy,observed_application_url=apply,
            countries=[country],city=city,country=country,
            language=None,published_at=values.get('published_at') or None,
            employment=values.get('employment_type_code',''),
            work_mode='remote' if values.get('remote')=='true'
                      else 'hybrid' if values.get('hybrid')=='true' else None))
    from .universal import Inventory
    return Inventory(records,dict(
        status='ok',complete=False,closure_complete=False,pages_read=1,
        feed_records=len(root),published_records=len(records),
        discovery_scope='reviewed-public-xml-no-absence-closure'))


def recruitee_records(source,client):
    if source.get('feed_format') == 'recruitee-public-xml':
        return recruitee_public_xml_records(source,client)
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
        if source.get('application_check')=='recruitee-linked':
            # Preserve an actually published entry, never invent /c/new from a
            # slug. Other registered Recruitee sources retain their behavior.
            out[-1]['posting_identifier']=str(j['id'])
            if j.get('careers_apply_url'):
                out[-1]['observed_application_url']=approved(j['careers_apply_url'],source)
    if len({x['external_id'] for x in out})!=len(out):raise ValueError('Duplicate offers')
    if source.get('report_feed_scope'):
        from .universal import Inventory
        return Inventory(out,dict(status='ok',complete=True,closure_complete=False,pages_read=1,
            feed_records=len(data['offers']),published_records=len(out),
            discovery_scope=source.get('discovery_scope')))
    return out
