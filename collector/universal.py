"""Autonomous public career discovery, structured/visible extraction and rendering.
Every employer is attempted; unknown coverage and access restrictions are outcomes,
never silently converted into an empty successful job list.
"""
from collections import deque
from datetime import datetime,timezone
from html.parser import HTMLParser
import json,re,time
import xml.etree.ElementTree as ET
from io import BytesIO
import gzip
from urllib.parse import urlsplit,urljoin,parse_qs
from .classify import canonical_url,plain,fold,classify_role,country_codes
from .employer_pages import PageParser,walk_json
from .runtime import CollectionBudgetExceeded,PageCache
from .ownership import employer_matches,owned_record

CAREER=re.compile(r'career|karriere|werken.?bij|working.?at|work.?with.?us|join.?us|recrut|rejoignez|emploi|jobs|vacatur|lavora.?con|lavora.?in|lavoro|trabaja|trabajar|carriere|stellen|opportunit|oferty.?pracy|kariera|vacantes|candidatur',re.I)
JOBPATH=re.compile(r'/(?:jobs?|vacatures?|vacancy|positions?|postings?|offres?|stellenangebote|stellen|annunci|o)/[^/?#]+|[?&](?:jobid|job_id|vacancyid|positionid)=',re.I)
NEXT=re.compile(r'^(?:next|next page|successiv[ao]|volgende|weiter|suivant|siguiente|próxim[ao]|następna|nästa|[›»→])$',re.I)
EMPTY=re.compile(r'no (?:open |current |matching |available )?(?:jobs|positions|vacancies)|geen (?:openstaande )?vacatures|nessuna (?:posizione|offerta)|keine (?:offenen )?(?:stellen|jobs)|aucun(?:e)? (?:offre|poste)|no hay (?:ofertas|vacantes)',re.I)
CHALLENGE=re.compile(r'captcha|verify (?:you are|that you are) human|access denied|just a moment|security verification',re.I)
PROVIDERS=('greenhouse.io','lever.co','recruitee.com','personio.de','personio.com','teamtailor.com','softgarden.de','ashbyhq.com','smartrecruiters.com','myworkdayjobs.com','myworkdaysite.com','successfactors.com','successfactors.eu','taleo.net','icims.com','intervieweb.it','inrecruiting.com','altamiraweb.com','workable.com','bamboohr.com','jobvite.com','applytojob.com','flatchr.io','welcomekit.co','oraclecloud.com','avature.net')
LEGAL={'gmbh','co','kg','ag','spa','srl','bv','nv','sa','sas','ltd','inc','group','groep','the','and','netherlands','deutschland','italia','france'}
VENDOR_HOSTS=set(PROVIDERS)|{'www.'+p for p in PROVIDERS}|{'app.recruitee.com','blog.recruitee.com','landing.recruitee.com','support.recruitee.com','tagging-server.recruitee.com'}
def provider_host(host):return host not in VENDOR_HOSTS and any(host.endswith('.'+p) for p in PROVIDERS)
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
        location=not footer and bool(re.search(r'(?:^|\s)(?:location|job[-_]?location|vacancy[-_]location|standort|locatie|job[-_]city|job[-_]address|workplace|joblocal|addressLocality)(?:\s|$)',a.get('class','')+' '+a.get('itemprop',''),re.I))
        if not footer and re.search(r'map-marker|location-dot|icon-location|icon-pin',a.get('class','')+' '+a.get('data-icon',''),re.I):
            for ancestor in reversed(self.stack):
                if ancestor['tag'] in ('li','dd') or re.search(r'icon-box-wrapper|icon-list-item',ancestor.get('class','')):
                    ancestor['location']=True;break
        node=dict(tag=tag,**{'class':a.get('class','')},ignored=ignored,main=main,footer=footer,location=location or (parent.get('location',False) and not footer))
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
        from .verification import expired
        try:
            if expired(expiry,datetime.now(timezone.utc).isoformat()):return None
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
    if name and not employer_matches(plain(name),source,job_url):return None
    if not name and (source.get('require_employer_identity') or urlsplit(job_url).hostname not in source['allowed_hosts']):return None
    employment=data.get('employmentType','');employment=' '.join(str(x) for x in employment) if isinstance(employment,list) else str(employment or '')
    record=dict(source_id=source['id'],external_id=job_url,employer=plain(name) or source['employer'],title=title,text=text,location='; '.join(cities+sorted(set(countries))),city='; '.join(cities) or None,country=countries[0] if len(set(countries))==1 else None,url=job_url,apply_url=job_url,language=None,published_at=data.get('datePosted') if isinstance(data.get('datePosted'),str) else None,employment=employment,work_mode='remote' if data.get('jobLocationType')=='TELECOMMUTE' else None,needs_page=False,extraction_method='jobposting',valid_through=data.get('validThrough'))
    identifier=data.get('identifier')
    if isinstance(identifier,dict):identifier=identifier.get('value')
    if isinstance(identifier,(str,int)) and str(identifier).strip():record['posting_identifier']=str(identifier).strip()
    if name:record['employer_identity_evidence']='jobposting-hiring-organization'
    if declared:record['countries']=sorted(set(countries))
    return record

def job_from_visible(doc,source,is_job=False):
    if source.get('require_employer_identity') or urlsplit(doc.url).hostname not in source['allowed_hosts']:return None
    if re.search(r'/(?:blogs?|news|stories|events|insights|articles?)(?:/|$)',urlsplit(doc.url).path,re.I):return None
    title=next((h for h in doc.h1 if classify_role(h)),None)
    if not title and is_job and len(doc.h1)==1 and len(doc.text)>200:title=doc.h1[0]
    if not title:return None
    text=doc.text
    if CHALLENGE.search(text[:3000]):return None
    # Geography comes only from labelled or semantically marked job locations.
    marked=plain(' '.join(doc.locations))
    if len(marked)>160:marked=''
    labelled=re.search(r'\b(?:location|standort|locatie|luogo di lavoro|sede di lavoro|localisation|ubicaci[oó]n|miejsce pracy|plaats|勤務地)\b\s*[:：\-]?\s*([^\n.;]{2,150})',' '.join(doc.main),re.I)
    location=marked or (labelled.group(1) if labelled else '')
    location=re.split(r'\blocation\s*:\s*',location,flags=re.I)[-1].strip()
    if len(location)>160:location=''
    url=safe_url(doc.url)
    if not url:return None
    return dict(source_id=source['id'],external_id=url,employer=source['employer'],title=title,text=text,location=location,city=location or None,country=None,url=url,apply_url=url,language=None,published_at=None,employment='',work_mode=None,needs_page=False,extraction_method='visible-html',geography_unresolved=not bool(country_codes(location)))

class Inventory(list):
    def __init__(self,records=(),stats=None):super().__init__(records);self.stats=stats or {}

class Crawler:
    def __init__(self,source,client):
        self.source=source;self.known_urls=set(source.get('known_job_urls',[]));self.client=client;self.scan_deadline=time.monotonic()+client.remaining()*.82 if hasattr(client,'remaining') else float('inf');self.cache=PageCache(source['id'],revision=4 if source.get('ownership_scope')=='reviewed-hosts' else 3);self.state=self.cache.state();
        if source.get('ownership_scope')=='reviewed-hosts' and self.state.get('ownership_policy_version')!=1:self.state={}
        self.state['ownership_policy_version']=1
        self.allowed=set(source['allowed_hosts'])|set(self.state.get('allowed_hosts',[]));self.records={};self.errors=[];self.pages=0;self.rendered=0;self.inventory=False;self.empty=False;self.incomplete=False;self.feeds=set();self.completed_feeds=set();self.urls_seen=set();self.job_candidates=set();self.used_methods=set();self.sitemap_origins=set();self.sitemaps_read=0;self.closed_urls=set();self.custom_recruitee=set()
    def allow(self,url,observed=False):
        value=safe_url(url)
        if not value:return False
        host=urlsplit(value).hostname
        if host in VENDOR_HOSTS:return False
        if self.source.get('ownership_scope')=='reviewed-hosts' and host not in self.source['allowed_hosts']:return False
        if host in self.allowed:return True
        if observed and provider_host(host):self.allowed.add(host);return True
        return False
    def add_record(self,r):
        if not r or not owned_record(r,self.source):return
        # URL was explicitly published in a trusted employer's structured data/feed.
        url=safe_url(r['url'])
        if not url:return
        self.allowed.add(urlsplit(url).hostname);r['source_id']=self.source['id'];self.records[url]=r
    def feed(self,url):
        """Only documented endpoints with identifiers observed in employer links."""
        from .adapters import collect,enrich
        p=urlsplit(url);host=p.hostname or '';path=[x for x in p.path.split('/') if x];adapter=None;board=None;feed=None
        if host in ('job-boards.greenhouse.io','boards.greenhouse.io','boards.eu.greenhouse.io') and path and path[0]!='embed':adapter='greenhouse';board=path[0]
        elif host in ('jobs.lever.co','jobs.eu.lever.co') and path:adapter='lever';board=path[0]
        elif re.fullmatch(r'[a-z0-9-]+\.jobs\.personio\.(?:de|com)',host):adapter='personio-xml';feed='https://'+host+'/xml'
        elif host=='jobs.ashbyhq.com' and path:adapter='ashby';board=path[0]
        elif host in ('careers.smartrecruiters.com','jobs.smartrecruiters.com') and path:adapter='smartrecruiters';board=path[0]
        elif host.endswith('.recruitee.com') and host not in ('www.recruitee.com','careers-analytics.recruitee.com'):adapter='recruitee';feed='https://'+host+'/api/offers/'
        elif host in self.custom_recruitee:adapter='recruitee';feed='https://'+host+'/api/offers/'
        if not adapter:return False
        # A posting/referral link does not establish ownership of an ATS tenant.
        if host not in self.source['allowed_hosts']:return False
        key=(adapter,board or feed)
        if key in self.completed_feeds:return True
        if key in self.feeds:return False
        self.feeds.add(key);s=dict(self.source,adapter=adapter,board=board or '',allowed_hosts=list(self.allowed))
        if host=='jobs.eu.lever.co':s['region']='eu'
        if host=='boards.eu.greenhouse.io':s['api_host']='boards-api.eu.greenhouse.io'
        if feed:s['feed_url']=feed
        try:
            rows=collect(s,self.client)
            for r in rows:
                if adapter=='smartrecruiters' and classify_role(r['title'],'',r.get('employment','')):r=enrich(r,s,self.client)
                self.add_record(r)
            self.inventory=True;self.empty=not rows;self.completed_feeds.add(key);self.used_methods.add(adapter);return True
        except CollectionBudgetExceeded:raise
        except Exception as exc:self.errors.append(dict(url=feed or url,error='Feed: '+str(exc)[:160]));return False
    def visit(self,url,is_job=False,render=False):
        self.client.check();cached=self.cache.get(url,max_age_hours=12 if url in self.known_urls else 48) if is_job else None
        if cached:
            for record in cached.get('records',[]):record.pop('inventory_evidence',None)
            self.used_methods.add('cached-job-page');return cached
        body,_,final=self.client.request(url)
        if not safe_url(final):raise ValueError('Unsafe final URL')
        # A declared employer redirect is public provenance for its final host.
        self.allowed.add(urlsplit(final).hostname);self.pages+=1
        if body.lstrip().startswith(b'{'):
            try:payload=json.loads(body)
            except ValueError:payload=None
            if payload is not None:
                from .public_json import smartrecruiters_job
                result=smartrecruiters_job(payload,final,self.source)
                if result is not None:
                    self.used_methods.add('public-smartrecruiters-json');self.closed_urls.update(result.get('closed_urls',[]))
                    self.inventory|=bool(result['records']);return result
        if body.startswith(b'\x1f\x8b'):
            with gzip.GzipFile(fileobj=BytesIO(body)) as zipped:body=zipped.read(20_000_001)
            if len(body)>20_000_000:raise ValueError('Sitemap decompression limit')
        if re.search(br'<(?:[a-z]+:)?(?:urlset|sitemapindex)\b',body[:1000],re.I):
            if b'<!DOCTYPE' in body.upper():raise ValueError('Sitemap DOCTYPE not allowed')
            root=ET.fromstring(body);index=root.tag.rsplit('}',1)[-1]=='sitemapindex';links=[];self.sitemaps_read+=1;self.used_methods.add('robots-declared-sitemap')
            for node in root.iter():
                if node.tag.rsplit('}',1)[-1]!='loc' or not node.text:continue
                target=safe_url(urljoin(final,node.text.strip()))
                if not target or not self.allow(target):continue
                path=urlsplit(target).path
                if re.search(r'/(?:blogs?|news|stories|events|insights|articles?)(?:/|$)',path,re.I):continue
                if index:
                    if self.sitemaps_read<5 and (CAREER.search(path) or re.search(r'(?:page|job|vacan|career|stellen|posizion)',path,re.I)):links.append(dict(url=target,job=False))
                    else:self.incomplete=True
                elif CAREER.search(path) or JOBPATH.search(target):links.append(dict(url=target,job=True))
            if len(links)>2000:self.incomplete=True
            return dict(records=[],links=links[:2000],empty=False)
        doc=Document(body,final)
        if CHALLENGE.search(doc.text[:3000]) or (re.search(br'http-equiv=["\']refresh["\']',body,re.I) and b'/.well-known/sgcaptcha/' in body):
            raise ValueError('Access challenge; no bypass attempted')
        # Employer-hosted Recruitee sites retain the platform credit/assets and
        # the documented /o/ posting paths. No board identifier is invented.
        platform_credit=any(re.search(r'https://[^/]*(?:recruitee\.com|recruiteecdn\.com)(?:/|$)',urljoin(final,href),re.I) for href,_,_ in doc.links) or bool(re.search(br'(?:src|href)=["\'][^"\']*recruitee(?:cdn)?\.com/',body,re.I))
        if platform_credit and any(urlsplit(urljoin(final,href)).hostname==urlsplit(final).hostname and urlsplit(urljoin(final,href)).path.startswith('/o/') for href,_,_ in doc.links):
            self.custom_recruitee.add(urlsplit(final).hostname)
            if self.feed(final):return dict(records=[],links=[],empty=self.empty)
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
        origin=urlsplit(final).scheme+'://'+urlsplit(final).netloc
        if origin not in self.sitemap_origins:
            self.sitemap_origins.add(origin);robots=getattr(self.client,'robots',{}).get(origin)
            for sitemap in (robots.site_maps() or []) if robots else []:
                target=safe_url(sitemap)
                if target and self.allow(target):result['links'].append(dict(url=target,job=False))
        for d in docs:
            posts=d.jobposts()
            for post in posts:
                from .verification import expired
                try:
                    if expired(post.get('validThrough'),datetime.now(timezone.utc).isoformat()):
                        self.closed_urls.add(d.url);continue
                except (ValueError,TypeError):pass
                r=job_from_json(post,d.url,self.source)
                if not r and self.source.get('visible_description_for_structured_jobs') and plain(post.get('title')) in d.h1 and len(d.text)>200:
                    # Reviewed AFAS template: title/address are structured, while
                    # its description is published only in the same visible page.
                    r=job_from_json(dict(post,description=d.text),d.url,self.source)
                if r:result['records'].append(r)
            visible=job_from_visible(d,self.source,is_job) if not posts else None
            if visible:result['records'].append(visible)
            if posts or visible:self.inventory=True;self.used_methods.add('jobposting' if posts else 'visible-html')
            for href,label,rel in d.links:
                target=safe_url(urljoin(d.url,href.strip()))
                if not target:continue
                if CAREER.search(label) and self.source.get('ownership_scope')!='reviewed-hosts' and not re.search(r'facebook|linkedin|instagram|youtube|twitter|tiktok',urlsplit(target).hostname):self.allowed.add(urlsplit(target).hostname)
                if not self.allow(target,observed=True):continue
                label=plain(label)
                path=urlsplit(target).path
                if re.search(r'/(?:blogs?|news|stories|events|insights|articles?)(?:/|$)|privacy|datenschutz|cookies?|impressum|contact|kontakt|login|register|/apply(?:[/?]|$)|/application|job-alert|talent-community',path,re.I):continue
                job=bool(JOBPATH.search(target) or classify_role(label))
                if job or CAREER.search(label+' '+path) or (path in ('','/') and CAREER.search(urlsplit(target).hostname)) or 'next' in rel or NEXT.fullmatch(label.strip()):result['links'].append(dict(url=target,job=job,priority=0 if classify_role(label+' '+path.replace('-',' ')) else 1 if ('next' in rel or NEXT.fullmatch(label.strip()) or not job) else 2))
            for href in d.frames:
                target=safe_url(urljoin(d.url,href.strip()))
                if target and self.allow(target,observed=True) and (provider_host(urlsplit(target).hostname) or CAREER.search(target)):result['links'].append(dict(url=target,job=False))
            result['empty']|=bool(EMPTY.search(d.text))
        for record in result['records']:
            record['_text_observation']=dict(kind='live',checked_at=datetime.now(timezone.utc).isoformat())
        if is_job:self.cache.put(url,result)
        return result
    def priority(self,entry):
        url,is_job,depth=entry;path=urlsplit(url).path
        if url in self.known_urls:priority=0
        elif classify_role(path.replace('-',' ')):priority=1
        elif not is_job and (depth==0 or re.search(r'/(?:jobs|careers|vacatures|karriere|stellenangebote|lavoraconnoi)/?$',path,re.I)):priority=2
        elif is_job:priority=4 if self.cache.exists(url) else 3
        else:priority=5
        return (priority,self.cache.timestamp(url),depth)

    def run(self):
        seeds=[u for u in [self.state.get('preferred_career_url')]+self.source['start_urls'] if u and safe_url(u)]
        queue=deque((u,True,0) for u in self.source.get('known_job_urls',[]) if self.allow(u));queue.extend((u,False,0) for u in dict.fromkeys(seeds));pending=self.state.get('pending',[])
        for entry in pending:
            if self.allow(entry.get('url','')):queue.append((entry['url'],entry.get('job',True),entry.get('depth',1)))
        max_pages=self.source.get('max_pages',60)
        try:
            while queue:
                self.client.check()
                if time.monotonic()>=self.scan_deadline or (hasattr(self.client,'max_requests') and self.client.requests>=self.client.max_requests*.8):self.incomplete=True;break
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
                    if len(queue)>2:queue=deque(dict.fromkeys(sorted(queue,key=self.priority)))
                except CollectionBudgetExceeded:self.urls_seen.discard(url);queue.appendleft((url,is_job,depth));raise
                except Exception as exc:self.errors.append(dict(url=url,error=str(exc)[:180]))
        except CollectionBudgetExceeded as exc:self.incomplete=True;self.errors.append(dict(url='collection-budget',error=str(exc)))
        remaining=[dict(url=u,job=j,depth=d) for u,j,d in queue if u not in self.urls_seen]
        self.state['allowed_hosts']=sorted(self.allowed);self.state['pending']=remaining[:2000];self.cache.save_state(self.state)
        unresolved=sum(bool(r.get('geography_unresolved')) for r in self.records.values())
        complete=(bool(self.completed_feeds) and self.inventory or self.empty) and not self.incomplete and not self.errors and not remaining and not unresolved
        stats=dict(status='ok' if complete else 'partial' if self.records or self.pages else 'failed',inventory_kind='bounded-public-career-crawl',complete=complete,closure_complete=complete and bool(self.completed_feeds),verified_closed_urls=sorted(self.closed_urls),pages_read=self.pages,sitemaps_read=self.sitemaps_read,rendered_pages=self.rendered,job_urls_discovered=len(self.job_candidates),pending_urls=len(remaining),records_inspected=len(self.records),unresolved_geography=unresolved,explicit_empty=self.empty,methods=sorted(self.used_methods),cache_hits=self.cache.hits,page_failures=len(self.errors),page_errors=self.errors[:30],allowed_hosts=sorted(self.allowed))
        if not self.inventory and not self.empty:stats['error']='No verified job inventory or explicit empty vacancy list found; discovery continues automatically'
        if not self.inventory and not self.empty and self.errors and all(
            re.search(r'Access challenge|robots\.txt disallows|HTTP Error: (?:401|403|429|451)',e['error'],re.I)
            for e in self.errors):
            stats.update(status='failed',error='Public source access blocked; no inventory established; no bypass attempted')
        return Inventory(self.records.values(),stats)

def collect_universal(source,client):return Crawler(source,client).run()
