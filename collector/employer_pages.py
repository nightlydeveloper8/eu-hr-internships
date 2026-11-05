"""Audited employer sitemaps and structured public job pages (no browser execution).

All in-scope job URLs are inventoried first. Descriptive slugs are a discovery hint,
never the final role/geography decision. Opaque URLs remain an explicit coverage gap.
"""
from datetime import datetime, timezone
from html.parser import HTMLParser
import json
import re
from urllib.parse import urlsplit, unquote
import xml.etree.ElementTree as ET
from .classify import canonical_url, plain

class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.scripts=[];self.fragments=[];self.links=[];self._json=False;self._body=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='script' and a.get('type','').lower()=='application/ld+json':self._json=True;self._body=[]
        if tag=='article' and a.get('data-cmp-contentfragment-model','').endswith('danone-job-model'):
            self.fragments.append({k:v for k,v in a.items() if k in ('title','country','city','locale','posted','jobid','key','description','descriptionheader','positiontype','workfromhome')})
        if tag=='a' and a.get('href'):self.links.append(a['href'])
    def handle_data(self,data):
        if self._json:self._body.append(data)
    def handle_endtag(self,tag):
        if tag=='script' and self._json:
            try:self.scripts.append(json.loads(''.join(self._body)))
            except (ValueError,TypeError):pass
            self._json=False

def approved(url,source):
    value=canonical_url(url)
    if urlsplit(value).hostname not in source['allowed_hosts']:raise ValueError('Unapproved employer-page host')
    return value

def sitemap_records(source,client):
    pending=list(source['sitemaps']);seen=set();job_urls=set();pattern=re.compile(source['job_url_pattern'])
    while pending:
        url=approved(pending.pop(0),source)
        if url in seen:continue
        if len(seen)>=source.get('max_sitemaps',20):raise ValueError('Sitemap safety limit; snapshot incomplete')
        seen.add(url);body,_,final=client.request(url);approved(final,source)
        if b'<!DOCTYPE' in body.upper():raise ValueError('DOCTYPE not permitted in sitemap')
        root=ET.fromstring(body)
        tag=root.tag.rsplit('}',1)[-1]
        if tag not in ('urlset','sitemapindex'):raise ValueError('Not a sitemap')
        urls=[x.text.strip() for x in root.iter() if x.tag.rsplit('}',1)[-1]=='loc' and x.text]
        for target in urls:
            if tag=='sitemapindex':pending.append(approved(target,source))
            elif pattern.search(target):job_urls.add(approved(target,source))
        if len(job_urls)>source.get('max_job_urls',20000):raise ValueError('Job URL safety limit; snapshot incomplete')
    if not job_urls:raise ValueError('No matching job URLs; source layout needs review')
    # Missing old links on a sitemap alone must never close a posting.
    return [dict(source_id=source['id'],external_id=u,employer=source['employer'],title=re.sub(r'[-_]+',' ',unquote(urlsplit(u).path)),location='',text='',url=u,apply_url=u,language=None,published_at=None,employment='',city=None,country=None,work_mode=None,needs_page=True) for u in sorted(job_urls)]

def walk_json(value):
    if isinstance(value,list):
        for item in value:yield from walk_json(item)
    elif isinstance(value,dict):
        types=value.get('@type',[]);types=[types] if isinstance(types,str) else types
        if 'JobPosting' in types:yield value
        for k in ('@graph','mainEntity','itemListElement','item'):
            if k in value:yield from walk_json(value[k])

def page_record(record,source,client,clock=None):
    body,_,final=client.request(approved(record['url'],source));approved(final,source)
    parser=PageParser();parser.feed(body.decode('utf-8','replace'))
    data=next((j for script in parser.scripts for j in walk_json(script)),None)
    result=dict(record);stamp=clock or datetime.now(timezone.utc)
    if source.get('page_format')=='danone':
        slug=urlsplit(record['url']).path.rsplit('/',1)[-1].removesuffix('.html')
        fragment=next((f for f in parser.fragments if f.get('key')==slug),None)
        if not fragment:raise ValueError('Matching Danone job fragment not found; page may be closed')
        title=plain(fragment['title'])
        result.update(title=title,location=plain(fragment.get('city',''))+', '+plain(fragment.get('country','')),city=fragment.get('city'),country=fragment.get('country'),text=plain(fragment.get('descriptionheader','')+' '+fragment.get('description','')),language=fragment.get('locale'),published_at=datetime.fromtimestamp(int(fragment['posted'])/1000,timezone.utc).isoformat() if fragment.get('posted','').isdigit() else None,employment=fragment.get('positiontype',''),work_mode={'Hybrid':'hybrid','On-site':'on-site','Remote':'remote'}.get(fragment.get('workfromhome')))
    elif data:
        expires=data.get('validThrough')
        if expires:
            try:
                expiry=datetime.fromisoformat(expires.replace('Z','+00:00'))
                if expiry.tzinfo is None:expiry=expiry.replace(tzinfo=timezone.utc)
                if expiry<stamp:raise ValueError('Posting has expired')
            except (TypeError,AttributeError):raise ValueError('Malformed expiry')
        loc=data.get('jobLocation',[]);loc=loc if isinstance(loc,list) else [loc]
        addresses=[l.get('address',{}) for l in loc if isinstance(l,dict)]
        countries=[];cities=[]
        for a in addresses:
            if not isinstance(a,dict):continue
            c=a.get('addressCountry');c=c.get('name') if isinstance(c,dict) else c
            if c:countries.append(c)
            if a.get('addressLocality'):cities.append(a['addressLocality'])
        employer=data.get('hiringOrganization',{}).get('name')
        if employer and not any(token in employer.lower() for token in source.get('employer_tokens',[source['employer'].lower()])):raise ValueError('Unexpected hiring organisation')
        result.update(title=plain(data.get('title')),text=plain(data.get('description')),location='; '.join(cities+countries),city='; '.join(cities) or None,country=countries[0] if len(set(countries))==1 else None,published_at=data.get('datePosted'),employment=' '.join(data.get('employmentType',[])) if isinstance(data.get('employmentType'),list) else data.get('employmentType',''),work_mode='remote' if data.get('jobLocationType')=='TELECOMMUTE' else None)
    else:raise ValueError('No supported JobPosting structured data; no page-text guessing')
    if not result['title'] or not result['text']:raise ValueError('Missing structured title/description')
    # Job page is the official application entry point. Never invent an apply URL.
    result['url']=approved(final,source);result['apply_url']=result['url'];result['needs_page']=False
    return result
