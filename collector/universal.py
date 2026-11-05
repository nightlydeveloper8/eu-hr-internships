"""Autonomous public career discovery, structured/visible extraction and rendering.
Every employer is attempted; unknown coverage and access restrictions are outcomes,
never silently converted into an empty successful job list.
"""
from collections import deque
from datetime import datetime,timezone
from html.parser import HTMLParser
import json,re,time
from urllib.parse import urlsplit,urljoin,parse_qs
from .classify import canonical_url,plain,fold,classify_role,country_codes
from .employer_pages import PageParser,walk_json
from .runtime import CollectionBudgetExceeded,PageCache

CAREER=re.compile(r'career|karriere|werken.?bij|working.?at|work.?with.?us|join.?us|recrut|rejoignez|emploi|jobs|vacatur|lavora.?con|lavora.?in|lavoro|trabaja|trabajar|carriere|stellen|opportunit|oferty.?pracy|kariera|vacantes|candidatur',re.I)
JOBPATH=re.compile(r'/(?:jobs?|vacatures?|vacancy|positions?|postings?|offres?|stellenangebote|stellen|annunci|o)/[^/?#]+|[?&](?:jobid|job_id|vacancyid|positionid)=',re.I)
NEXT=re.compile(r'^(?:next|next page|successiv[ao]|volgende|weiter|suivant|siguiente|próxim[ao]|następna|nästa|[›»→])$',re.I)
EMPTY=re.compile(r'no (?:open |current |matching |available )?(?:jobs|positions|vacancies)|geen (?:openstaande )?vacatures|nessuna (?:posizione|offerta)|keine (?:offenen )?(?:stellen|jobs)|aucun(?:e)? (?:offre|poste)|no hay (?:ofertas|vacantes)',re.I)
CHALLENGE=re.compile(r'captcha|verify (?:you are|that you are) human|access denied|just a moment|security verification',re.I)
PROVIDERS=('greenhouse.io','lever.co','recruitee.com','personio.de','personio.com','teamtailor.com','softgarden.de','ashbyhq.com','smartrecruiters.com','myworkdayjobs.com','myworkdaysite.com','successfactors.com','successfactors.eu','taleo.net','icims.com','intervieweb.it','inrecruiting.com','altamiraweb.com','workable.com','bamboohr.com','jobvite.com','applytojob.com','flatchr.io','welcomekit.co','oraclecloud.com','avature.net')
LEGAL={'gmbh','co','kg','ag','spa','srl','bv','nv','sa','sas','ltd','inc','group','groep','the','and','netherlands','deutschland','italia','france'}
def provider_host(host):return any(host==p or host.endswith('.'+p) for p in PROVIDERS)
def safe_url(url):
    try:
        value=canonical_url(url);host=urlsplit(value).hostname
        if host.endswith(('.local','.internal')):return None
        return value
    except (ValueError,TypeError,AttributeError):return None

class Document(HTMLParser):
    def __init__(self,body,url):
        super().__init__(convert_charrefs=True);self.url=url;self.links=[];self.frames=[];self.buttons=[];self.h1=[];self.main=[];self.body=[];self.locations=[];self.stack=[];self.anchor=None;self.heading=None;self.button=None;self.meta={}
        self.structured=PageParser();self.structured.feed(body.decode('utf-8','replace'));self.feed(body.decode('utf-8','replace'))
    def handle_starttag(self,tag,attrs):
        a=dict(attrs);parent=self.stack[-1] if self.stack else {};ignored=parent.get('ignored',False) or tag in ('script','style','noscript','svg')
        main=parent.get('main',False) or tag in ('main','article') or a.get('role')=='main' or bool(re.search(r'entry-content|job-description|job-detail|vacancy-detail',a.get('class','')))
        footer=parent.get('footer',False) or tag in ('footer','nav','header')
        location=not footer and bool(re.search(r'location|standort|locatie|job-city|job-address|workplace|joblocal',a.get('class','')+' '+a.get('itemprop',''),re.I))
        node=dict(tag=tag,ignored=ignored,main=main,footer=footer,location=location or (parent.get('location',False) and not footer))
        if tag not in ('meta','link','input','br','hr','img','source','wbr','area','base','embed','param'):self.stack.append(node)
        if tag=='a' and a.get('href'):self.anchor=[a['href'],'',a.get('rel','')]
        if tag=='h1':self.heading=[]
        if tag=='button':self.button=[]
        if tag=='iframe' and a.get('src'):self.frames.append(a['src'])
        if tag=='meta' and a.get('content'):self.meta[a.get('property') or a.get('name','')]=a['content']
        if tag=='link' and a.get('rel')=='next' and a.get('href'):self.links.append([a['href'],'next','next'])
    def handle_data(self,data):
        node=self.stack[-1] if self.stack else {}
        if node.get('ignored'):return
        self.body.append(data)
        if node.get('main') and not node.get('footer'):self.main.append(data)
        if node.get('location') and (node.get('main') or not node.get('footer')):self.locations.append(data)
        if self.anchor is not None:self.anchor[1]+=' '+data
        if self.heading is not None:self.heading.append(data)
        if self.button is not None:self.button.append(data)
    def handle_endtag(self,tag):
        if tag=='a' and self.anchor is not None:self.links.append(self.anchor);self.anchor=None
        if tag=='h1' and self.heading is not None:self.h1.append(plain(' '.join(self.heading)));self.heading=None
        if tag=='button' and self.button is not None:self.buttons.append(plain(' '.join(self.button)));self.button=None
        for i in range(len(self.stack)-1,-1,-1):
            if self.stack[i]['tag']==tag:self.stack=self.stack[:i];break
    @property
    def text(self):return plain(' '.join(self.main or self.body))
    def jobposts(self):return [p for script in self.structured.scripts for p in walk_json(script)]

def job_from_json(data,url,source):
    title=plain(data.get('title'));text=plain(data.get('description'))
    if not title or not text:return None
    expiry=data.get('validThrough')
    if expiry:
        try:
            t=datetime.fromisoformat(str(expiry).replace('Z','+00:00'));t=t.replace(tzinfo=timezone.utc) if t.tzinfo is None else t
            if t<datetime.now(timezone.utc):return None
        except ValueError:pass
    loc=data.get('jobLocation',[]);loc=loc if isinstance(loc,list) else [loc];cities=[];countries=[];declared=False
    for place in loc:
        address=place.get('address',{}) if isinstance(place,dict) else {}
        if not isinstance(address,dict):continue
        if address.get('addressLocality'):cities.append(str(address['addressLocality']))
        c=address.get('addressCountry');c=c.get('name') if isinstance(c,dict) else c
        if isinstance(c,str):declared=True;countries.extend(country_codes('',c))
    hiring=data.get('hiringOrganization',{});name=hiring.get('name') if isinstance(hiring,dict) else None
    job_url=safe_url(urljoin(url,data.get('url') or url))
    if not job_url:return None
    employment=data.get('employmentType','');employment=' '.join(str(x) for x in employment) if isinstance(employment,list) else str(employment or '')
    record=dict(source_id=source['id'],external_id=job_url,employer=plain(name) or source['employer'],title=title,text=text,location='; '.join(cities+sorted(set(countries))),city='; '.join(cities) or None,country=countries[0] if len(set(countries))==1 else None,url=job_url,apply_url=job_url,language=None,published_at=data.get('datePosted') if isinstance(data.get('datePosted'),str) else None,employment=employment,work_mode='remote' if data.get('jobLocationType')=='TELECOMMUTE' else None,needs_page=False,extraction_method='jobposting')
    if declared:record['countries']=sorted(set(countries))
    return record

def job_from_visible(doc,source,is_job=False):
    title=next((h for h in doc.h1 if classify_role(h)),None)
    if not title and is_job and len(doc.h1)==1 and len(doc.text)>200:title=doc.h1[0]
    if not title:return None
    text=doc.text
    if CHALLENGE.search(text[:3000]):return None
    # Geography comes only from labelled or semantically marked job locations.
    marked=plain(' '.join(doc.locations))[:600]
    labelled=re.search(r'(?:location|standort|locatie|luogo di lavoro|sede di lavoro|localisation|ubicaci[oó]n|miejsce pracy|plaats|勤務地)\s*[:：\-]?\s*([^\n.;]{2,150})',' '.join(doc.main),re.I)
    location=marked or (labelled.group(1) if labelled else '')
    url=safe_url(doc.url)
    if not url:return None
    return dict(source_id=source['id'],external_id=url,employer=source['employer'],title=title,text=text,location=location,city=location or None,country=None,url=url,apply_url=url,language=None,published_at=None,employment='',work_mode=None,needs_page=False,extraction_method='visible-html',geography_unresolved=not bool(country_codes(location)))

class Inventory(list):
    def __init__(self,records=(),stats=None):super().__init__(records);self.stats=stats or {}

class Crawler:
    def __init__(self,source,client):
        self.source=source;self.client=client;self.scan_deadline=time.monotonic()+client.remaining()*.82 if hasattr(client,'remaining') else float('inf');self.cache=PageCache(source['id']);self.state=self.cache.state();self.allowed=set(source['allowed_hosts'])|set(self.state.get('allowed_hosts',[]));self.records={};self.errors=[];self.pages=0;self.rendered=0;self.inventory=False;self.empty=False;self.incomplete=False;self.feeds=set();self.completed_feeds=set();self.urls_seen=set();self.job_candidates=set();self.used_methods=set()
    def allow(self,url,observed=False):
        value=safe_url(url)
        if not value:return False
        host=urlsplit(value).hostname
        if host in self.allowed:return True
        if observed and provider_host(host):self.allowed.add(host);return True
        return False
    def add_record(self,r):
        if not r:return
        # URL was explicitly published in a trusted employer's structured data/feed.
        url=safe_url(r['url'])
        if not url:return
        self.allowed.add(urlsplit(url).hostname);r['source_id']=self.source['id'];self.records[url]=r
    def feed(self,url):
        """Only documented endpoints with identifiers observed in employer links."""
        from .adapters import collect
        p=urlsplit(url);host=p.hostname or '';path=[x for x in p.path.split('/') if x];adapter=None;board=None;feed=None
        if host in ('job-boards.greenhouse.io','boards.greenhouse.io','boards.eu.greenhouse.io') and path and path[0]!='embed':adapter='greenhouse';board=path[0]
        elif host in ('jobs.lever.co','jobs.eu.lever.co') and path:adapter='lever';board=path[0]
        elif re.fullmatch(r'[a-z0-9-]+\.jobs\.personio\.(?:de|com)',host):adapter='personio-xml';feed='https://'+host+'/xml'
        elif host=='jobs.ashbyhq.com' and path:adapter='ashby';board=path[0]
        elif host in ('careers.smartrecruiters.com','jobs.smartrecruiters.com') and path:adapter='smartrecruiters';board=path[0]
        elif host.endswith('.recruitee.com') and host not in ('www.recruitee.com','careers-analytics.recruitee.com'):adapter='recruitee';feed='https://'+host+'/api/offers/'
        if not adapter:return False
        key=(adapter,board or feed)
        if key in self.feeds:return False
        self.feeds.add(key);s=dict(self.source,adapter=adapter,board=board or '',allowed_hosts=list(self.allowed))
        if host=='jobs.eu.lever.co':s['region']='eu'
        if host=='boards.eu.greenhouse.io':s['api_host']='boards-api.eu.greenhouse.io'
        if feed:s['feed_url']=feed
        try:
            rows=collect(s,self.client)
            for r in rows:self.add_record(r)
            self.inventory=True;self.empty=not rows;self.completed_feeds.add(key);self.used_methods.add(adapter);return True
        except CollectionBudgetExceeded:raise
        except Exception as exc:self.errors.append(dict(url=feed or url,error='Feed: '+str(exc)[:160]));return False
    def visit(self,url,is_job=False,render=False):
        self.client.check();cached=self.cache.get(url,max_age_hours=48) if is_job else None
        if cached:
            self.used_methods.add('cached-job-page');return cached
        body,_,final=self.client.request(url)
        if not safe_url(final):raise ValueError('Unsafe final URL')
        # A declared employer redirect is public provenance for its final host.
        self.allowed.add(urlsplit(final).hostname);self.pages+=1;doc=Document(body,final)
        if CHALLENGE.search(doc.text[:3000]):raise ValueError('Access challenge; no bypass attempted')
        for embedded in re.findall(r'https://[^\s<>\"\']+',body.decode('utf-8','replace').replace('\\/','/')):
            target=safe_url(embedded.rstrip(');,'))
            if target and provider_host(urlsplit(target).hostname) and self.allow(target,observed=True):doc.frames.append(target)
        docs=[doc]
        js_shell=not doc.jobposts() and not job_from_visible(doc,self.source,is_job) and (len(doc.text)<350 or not any(JOBPATH.search(u) or CAREER.search(label+' '+u) for u,label,_ in doc.links))
        has_more=any(re.search(r'load more|show more|carica|mostra|mehr|volgende|voir plus',b,re.I) for b in doc.buttons)
        if render or (not self.source.get('no_browser') and (js_shell or has_more)):
            from .rendering import render_pages
            try:
                rendered,complete=render_pages(final,self.client,lambda u:self.allow(u),limit=self.source.get('max_render_pages',4))
                docs.extend(Document(b,u) for u,b in rendered);self.rendered+=len(rendered);self.incomplete|=not complete;self.used_methods.add('browser')
            except Exception as exc:
                self.incomplete=True;self.errors.append(dict(url=final,error='Rendered read: '+str(exc)[:160]))
        result=dict(records=[],links=[],empty=False)
        for d in docs:
            posts=d.jobposts()
            for post in posts:
                r=job_from_json(post,d.url,self.source)
                if r:result['records'].append(r)
            visible=job_from_visible(d,self.source,is_job) if not posts else None
            if visible:result['records'].append(visible)
            if posts or visible:self.inventory=True;self.used_methods.add('jobposting' if posts else 'visible-html')
            for href,label,rel in d.links:
                target=safe_url(urljoin(d.url,href.strip()))
                if not target:continue
                if CAREER.search(label) and not re.search(r'facebook|linkedin|instagram|youtube|twitter|tiktok',urlsplit(target).hostname):self.allowed.add(urlsplit(target).hostname)
                if not self.allow(target,observed=True):continue
                label=plain(label)
                path=urlsplit(target).path
                if re.search(r'privacy|datenschutz|cookies?|impressum|contact|kontakt|login|register|/apply(?:[/?]|$)|/application|job-alert|talent-community',path,re.I):continue
                job=bool(JOBPATH.search(target) or classify_role(label))
                if job or CAREER.search(label+' '+path) or (path in ('','/') and CAREER.search(urlsplit(target).hostname)) or 'next' in rel or NEXT.fullmatch(label.strip()):result['links'].append(dict(url=target,job=job,priority=0 if classify_role(label+' '+path.replace('-',' ')) else 1 if ('next' in rel or NEXT.fullmatch(label.strip()) or not job) else 2))
            for href in d.frames:
                target=safe_url(urljoin(d.url,href.strip()))
                if target and self.allow(target,observed=True) and (provider_host(urlsplit(target).hostname) or CAREER.search(target)):result['links'].append(dict(url=target,job=False))
            result['empty']|=bool(EMPTY.search(d.text))
        if is_job:self.cache.put(url,result)
        return result
    def run(self):
        seeds=[u for u in [self.state.get('preferred_career_url')]+self.source['start_urls'] if u and safe_url(u)]
        queue=deque((u,False,0) for u in dict.fromkeys(seeds));pending=self.state.get('pending',[])
        for entry in pending:
            if self.allow(entry.get('url','')):queue.append((entry['url'],entry.get('job',True),entry.get('depth',1)))
        max_pages=self.source.get('max_pages',60)
        try:
            while queue:
                self.client.check()
                if time.monotonic()>=self.scan_deadline:self.incomplete=True;break
                if self.pages>=max_pages:self.incomplete=True;break
                url,is_job,depth=queue.popleft()
                if url in self.urls_seen:continue
                self.urls_seen.add(url)
                try:
                    if self.feed(url):continue
                    result=self.visit(url,is_job)
                    self.empty|=result['empty']
                    for r in result['records']:self.add_record(r)
                    for link in result['links']:
                        if link['job']:self.job_candidates.add(link['url'])
                        if link['url'] not in self.urls_seen and (link['job'] or depth<self.source.get('max_navigation_depth',3)):
                            queue.append((link['url'],link['job'],depth+1))
                            if not link['job'] and CAREER.search(link['url']):self.state['preferred_career_url']=link['url']
                    # New pages precede cached details so a large employer resumes fairly.
                    if len(queue)>2:queue=deque(dict.fromkeys(sorted(queue,key=lambda x:(self.cache.exists(x[0]),0 if classify_role(urlsplit(x[0]).path.replace('-',' ')) else 1 if not x[1] else 2,x[2]))))
                except CollectionBudgetExceeded:self.urls_seen.discard(url);queue.appendleft((url,is_job,depth));raise
                except Exception as exc:self.errors.append(dict(url=url,error=str(exc)[:180]))
        except CollectionBudgetExceeded as exc:self.incomplete=True;self.errors.append(dict(url='collection-budget',error=str(exc)))
        remaining=[dict(url=u,job=j,depth=d) for u,j,d in queue if u not in self.urls_seen]
        self.state['allowed_hosts']=sorted(self.allowed);self.state['pending']=remaining[:2000];self.cache.save_state(self.state)
        unresolved=sum(bool(r.get('geography_unresolved')) for r in self.records.values())
        complete=(bool(self.completed_feeds) and self.inventory or self.empty) and not self.incomplete and not self.errors and not remaining and not unresolved
        stats=dict(status='ok' if complete else 'partial' if self.records or self.pages else 'failed',inventory_kind='bounded-public-career-crawl',complete=complete,pages_read=self.pages,rendered_pages=self.rendered,job_urls_discovered=len(self.job_candidates),pending_urls=len(remaining),records_inspected=len(self.records),unresolved_geography=unresolved,explicit_empty=self.empty,methods=sorted(self.used_methods),cache_hits=self.cache.hits,page_failures=len(self.errors),page_errors=self.errors[:30],allowed_hosts=sorted(self.allowed))
        if not self.inventory and not self.empty:stats['error']='No verified job inventory or explicit empty vacancy list found; discovery continues automatically'
        return Inventory(self.records.values(),stats)

def collect_universal(source,client):return Crawler(source,client).run()
