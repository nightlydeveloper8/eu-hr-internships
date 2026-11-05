"""Only unauthenticated, documented, public/listed job-board GET endpoints."""
import json
import logging
import re
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit, quote
from urllib.request import Request, urlopen
from urllib.robotparser import RobotFileParser
from .classify import plain

LOG = logging.getLogger(__name__)
AGENT = 'PeoplePlacementBot/1.0 (public HR internship discovery; source: README.md)'

class Client:
    def __init__(self, delay=0.35):
        self.delay, self.last, self.robots = delay, {}, {}
        self.host_delays = {}

    def pause(self,seconds):time.sleep(seconds)

    def request(self, url, method='GET', robots=True, timeout=35, attempts=3):
        host = urlsplit(url).netloc
        if robots and not self.permitted(url): raise ValueError('robots.txt disallows '+url)
        for attempt in range(attempts):
            self.pause(max(0,self.host_delays.get(host,self.delay)-(time.monotonic()-self.last.get(host,0))))
            self.last[host]=time.monotonic()
            try:
                with urlopen(Request(url,headers={'User-Agent':AGENT,'Accept':'application/json,text/html;q=0.8'},method=method),timeout=timeout) as response:
                    if urlsplit(response.url).scheme != 'https': raise ValueError('Unsafe redirect')
                    return response.read(20_000_000), response.status, response.url
            except HTTPError as exc:
                if exc.code not in (429,500,502,503,504) or attempt==attempts-1: raise
                retry = exc.headers.get('Retry-After','')
                pause = min(60,int(retry)) if retry.isdigit() else 2**(attempt+1)
                LOG.warning('Retry HTTP %s: %s',exc.code,host)
                self.pause(pause)
            except (URLError,TimeoutError):
                if attempt==attempts-1: raise
                self.pause(2**(attempt+1))

    def permitted(self,url):
        p=urlsplit(url); origin=p.scheme+'://'+p.netloc
        if origin not in self.robots:
            parser=RobotFileParser()
            try:
                body,_,_=self.request(origin+'/robots.txt',robots=False)
                robots_text=body.decode('utf-8','replace')
                if re.search(r'<(?:!doctype|html)\b',robots_text,re.I):raise ValueError('robots.txt returned HTML; access review required')
                parser.parse(robots_text.splitlines())
            except HTTPError as exc:
                if exc.code in (404,410): parser.parse([])
                else: raise ValueError('robots.txt unavailable: '+str(exc.code))
            self.robots[origin]=parser
        parser=self.robots[origin]
        delay=parser.crawl_delay(AGENT) or parser.crawl_delay('*')
        if delay: self.host_delays[p.netloc]=max(self.delay,delay)
        return parser.can_fetch(AGENT,url)

    def json(self,url):
        body,_,_=self.request(url)
        return json.loads(body)

def _record(source, job_id,title,location,text,url,apply=None,**extra):
    if not job_id or not title or not url: raise ValueError('Malformed source record')
    return dict(source_id=source['id'],external_id=str(job_id),employer=source['employer'],title=plain(title),location=plain(location),text=plain(text),url=url,apply_url=apply or url,**extra)

def collect(source,client):
    kind,board=source['adapter'],quote(source.get('board',''),safe='')
    out=[]
    if kind=='universal-employer':
        from .universal import collect_universal
        return collect_universal(source,client)
    if kind in ('personio-xml','recruitee'):
        from .public_feeds import personio_records,recruitee_records
        return (personio_records if kind=='personio-xml' else recruitee_records)(source,client)
    if kind=='employer-index':
        from .employer_pages import index_records
        return index_records(source,client)
    if kind=='employer-sitemap':
        from .employer_pages import sitemap_records
        return sitemap_records(source,client)
    elif kind=='greenhouse':
        api_host=source.get('api_host','boards-api.greenhouse.io')
        if api_host not in ('boards-api.greenhouse.io','boards-api.eu.greenhouse.io'):raise ValueError('Unknown Greenhouse region')
        data=client.json(f'https://{api_host}/v1/boards/{board}/jobs?content=true')
        jobs=data['jobs']
        if not isinstance(jobs,list) or data.get('meta',{}).get('total',len(jobs))!=len(jobs): raise ValueError('Incomplete Greenhouse board')
        for j in jobs:
            # Prospect/talent-community entries are not vacancies.
            if j.get('internal_job_id','present') is None: continue
            out.append(_record(source,j['id'],j['title'],j.get('location',{}).get('name',''),j.get('content',''),j['absolute_url'],language=j.get('language'),published_at=j.get('first_published'),employment='',city=None,country=None,work_mode=None))
    elif kind=='lever':
        domain='api.eu.lever.co' if source.get('region')=='eu' else 'api.lever.co'
        offset=0
        while True:
            jobs=client.json(f'https://{domain}/v0/postings/{board}?mode=json&limit=100&skip={offset}')
            if not isinstance(jobs,list): raise ValueError('Malformed Lever page')
            for j in jobs:
                cats=j.get('categories',{})
                content=j.get('descriptionPlain','')+' '+j.get('additionalPlain','')+' '+' '.join(x.get('text','')+' '+x.get('content','') for x in j.get('lists',[]))
                out.append(_record(source,j['id'],j['text'],cats.get('location',''),content,j['hostedUrl'],j.get('applyUrl'),language=None,published_at=None,employment=cats.get('commitment',''),city=None,country=None,work_mode={'onsite':'on-site','hybrid':'hybrid','remote':'remote'}.get(j.get('workplaceType'))))
            offset+=len(jobs)
            if len(jobs)<100: break
            if offset>25000: raise ValueError('Lever pagination safety limit')
    elif kind=='ashby':
        data=client.json(f'https://api.ashbyhq.com/posting-api/job-board/{board}')
        for j in data['jobs']:
            if not j.get('isListed',True): continue
            address=j.get('address',{}).get('postalAddress',{}) or j.get('address',{})
            out.append(_record(source,j.get('id') or j['jobUrl'].rstrip('/').split('/')[-1],j['title'],j.get('location',''),j.get('descriptionPlain') or j.get('descriptionHtml',''),j['jobUrl'],j.get('applyUrl'),language=None,published_at=j.get('publishedAt'),employment=j.get('employmentType',''),city=address.get('addressLocality'),country=address.get('addressCountry'),work_mode={'OnSite':'on-site','Hybrid':'hybrid','Remote':'remote'}.get(j.get('workplaceType')) or ('remote' if j.get('isRemote') else None)))
    elif kind=='smartrecruiters':
        offset=0
        while True:
            data=client.json(f'https://api.smartrecruiters.com/v1/companies/{board}/postings?limit=100&offset={offset}')
            jobs=data['content']; total=data['totalFound']
            if not isinstance(jobs,list) or (not jobs and offset<total): raise ValueError('Incomplete SmartRecruiters page')
            for j in jobs:
                if j.get('visibility','PUBLIC')!='PUBLIC': continue
                loc=j.get('location',{})
                out.append(_record(source,j['id'],j['name'],loc.get('fullLocation') or loc.get('city',''),'',f'https://jobs.smartrecruiters.com/{board}/{j["id"]}',language=j.get('language',{}).get('code'),published_at=j.get('releasedDate'),employment=j.get('experienceLevel',{}).get('label','')+' '+j.get('typeOfEmployment',{}).get('label',''),city=loc.get('city'),country=loc.get('country'),work_mode='hybrid' if loc.get('hybrid') else 'remote' if loc.get('remote') else None))
            offset+=len(jobs)
            if offset>=total: break
            if offset>25000: raise ValueError('SmartRecruiters pagination safety limit')
    else: raise ValueError('Unsupported adapter: '+kind)
    ids=[j['external_id'] for j in out]
    if len(ids)!=len(set(ids)): raise ValueError('Repeated IDs: board may have changed during pagination')
    return out

def enrich(record,source,client):
    if source['adapter'] in ('employer-sitemap','employer-index'):
        from .employer_pages import page_record
        return page_record(record,source,client)
    if source['adapter']!='smartrecruiters': return record
    j=client.json(f'https://api.smartrecruiters.com/v1/companies/{quote(source["board"],safe="")}/postings/{record["external_id"]}')
    if j.get('active') is False or j.get('visibility','PUBLIC')!='PUBLIC': raise ValueError('Inactive or private posting')
    record=dict(record)
    record['text']=' '.join(plain(s.get('text','')) for key,s in j.get('jobAd',{}).get('sections',{}).items() if key!='companyDescription')
    record['url']=j.get('postingUrl') or record['url']
    record['apply_url']=j.get('applyUrl') or record['url']
    return record
