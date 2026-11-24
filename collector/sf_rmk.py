"""Read-only SAP SuccessFactors Recruiting Marketing sitemaps and job pages."""
from collections import defaultdict
from datetime import datetime
from html.parser import HTMLParser
import re
from urllib.error import HTTPError
from urllib.parse import unquote, urljoin, urlsplit
from urllib.robotparser import RobotFileParser
import xml.etree.ElementTree as ET

from .adapters import AGENT
from .classify import COUNTRIES, CATEGORIES, INTERNSHIP, classify_role, POLISH_PLACEMENT, canonical_url, fold, plain
from .employer_pages import decompress_sitemap, slug_title

JOB_PATH = re.compile(r'/(?:[\w-]+/)?job/(?P<slug>[^/]+)/(?P<id>\d+)(?:-[a-z]{2}_[a-z]{2})?/?', re.I)
FORBIDDEN_PREFIX = {'applybutton','talentcommunity','mobile','services','preapply',
                    'emailsubscribe','email','error','unsubscribe','reset'}
VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
STAGE = re.compile(INTERNSHIP + '|' + POLISH_PLACEMENT + r'|\b(?:pflichtpraktikum|becari|stagiaire)\b')
NON_STAGE = re.compile(r'\b(?:werkstudent\w*|working student|trainee\w*|alternance|apprentissage|alternant\w*)\b')
HR = re.compile('|'.join(regex for _, regex in CATEGORIES.values()) +
                r'|\b(?:personal(?:betreuung|entwicklung|management|marketing|bereich|auswahl\w*|abteilung)'
                r'|entgeltabrechnung|employer branding|kadr\w*|seleccio\w*|recursos humans|hrpersonal)\b')


def path_match(url):
    parsed = urlsplit(url)
    path = unquote(parsed.path)
    segments=path.strip('/').split('/')
    if (parsed.query or any(part in ('.','..') for part in segments) or '\\' in path
            or segments[0].casefold() in FORBIDDEN_PREFIX):
        return None
    return JOB_PATH.fullmatch(path)


def candidate(url):
    match = path_match(url)
    if not match:
        return False
    title = fold(slug_title('/' + match['slug'])).replace('ł','l')
    return bool(STAGE.search(title) and HR.search(title) and not NON_STAGE.search(title))


def role_for_posting(title, text, employment):
    normalized=fold(title)
    normalized=re.sub(r'\brecruiting\w+\b','recruiting',normalized)
    normalized=re.sub(r'\b(?:personalbetreuung|personalmanagement|personalbereich|personalmarketing|hrpersonal)\b',
                      'human resources',normalized)
    normalized=re.sub(r'\bpersonalauswahl\w*\b','recruiting',normalized)
    normalized=normalized.replace('organisationsentwicklung','organizational development')
    normalized=normalized.replace('entgeltabrechnung','payroll')
    return classify_role(normalized,text,employment)


def student_scope(countries, record, role):
    from .classify import student_eligibility_for_country
    results={}
    for country in countries:
        title=record['title']
        if country=='DE' and role['internship_type']=='internship':
            # Recruiting apprentices is a specialization within the internship.
            title=re.sub(r'\b(?:Schwerpunkt Ausbildung|Recruiting Auszubildende)\b','Recruiting',title,flags=re.I)
        level=student_eligibility_for_country(country,title,record['text'],record['employment'])
        if level!='excluded':
            results[country]=level
    return list(results),'confirmed' if results and set(results.values())=={'confirmed'} else 'not_stated'


def request(source, client, url, *, robots=False):
    """Limit even redirect targets to the same source and the same kind of path."""
    if getattr(client, 'sf_rmk_blocked', False) is True:
        raise ValueError('SF-RMK host stopped after an access restriction')
    original = path_match(url)
    path = urlsplit(url).path
    previous = getattr(client,'redirect_scope_allowed',None)
    def allowed(target):
        try:
            target=target.encode('latin1').decode('utf8')
        except UnicodeError:
            pass
        parsed=urlsplit(target)
        if (parsed.scheme!='https' or parsed.hostname not in source['allowed_hosts']
                or parsed.hostname!=urlsplit(url).hostname or parsed.query
                or (callable(previous) and not previous(target))
                or (not robots and not client.sf_rmk_robots.can_fetch(AGENT,target))):
            return False
        match=path_match(target)
        if original:
            return bool(match and (match['id']==original['id'] or
                                  fold(slug_title('/'+match['slug']))==fold(slug_title('/'+original['slug']))))
        return parsed.path.rstrip('/')==path.rstrip('/')
    if not allowed(url):
        raise ValueError('SF-RMK path outside reviewed scope')
    client.redirect_scope_allowed=allowed
    try:
        if not robots and not client.sf_rmk_robots.can_fetch(AGENT,url):
            raise ValueError('robots.txt disallows SF-RMK route')
        body,status,final=client.request(url,robots=False)
        if status != 200 or not allowed(final) or (not robots and not client.sf_rmk_robots.can_fetch(AGENT,final)):
            raise ValueError('SF-RMK response outside reviewed scope')
        return body,final
    except HTTPError as exc:
        if exc.code in (403,429):
            client.sf_rmk_blocked=True
        raise
    finally:
        client.redirect_scope_allowed=previous


class Inventory(list):
    def __init__(self, records, total):
        super().__init__(records)
        self.stats={'sitemap_jobs':total,'sitemap_candidates':len(records),'closure_complete':False}


def collect_records(source, client):
    sitemap=source['sitemaps'][0]
    if urlsplit(sitemap).path!='/sitemap.xml':
        raise ValueError('Expected reviewed SF-RMK sitemap.xml path')
    body,_=request(source,client,urljoin(sitemap,'/robots.txt'),robots=True)
    robots=body.decode('utf-8','replace')
    if not re.search(r'^Disallow:\s*/applybutton/',robots,re.M|re.I) or not re.search(r'^Disallow:\s*/talentcommunity/',robots,re.M|re.I):
        raise ValueError('SF-RMK robots signature missing')
    client.sf_rmk_robots=RobotFileParser()
    client.sf_rmk_robots.parse(robots.splitlines())
    delay=client.sf_rmk_robots.crawl_delay(AGENT)
    if delay and hasattr(client,'host_delays'):
        host=urlsplit(sitemap).netloc
        client.host_delays[host]=max(client.host_delays.get(host,0),delay)
    body,_=request(source,client,sitemap)
    body=decompress_sitemap(body)
    if b'<!DOCTYPE' in body.upper():
        raise ValueError('DOCTYPE not permitted in sitemap')
    root=ET.fromstring(body)
    if root.tag.rsplit('}',1)[-1]!='urlset':
        raise ValueError('Expected SF-RMK job sitemap URL set')
    postings={}
    for loc in root.iter():
        if loc.tag.rsplit('}',1)[-1]!='loc' or not loc.text:
            continue
        url=canonical_url(loc.text.strip())
        match=path_match(url)
        if match and urlsplit(url).hostname==urlsplit(sitemap).hostname:
            key=(match['id'],candidate(url))
            postings.setdefault(key,url)
    if not postings:
        raise ValueError('SF-RMK sitemap contains no vacancy URLs')
    return Inventory([dict(source_id=source['id'],external_id=id,employer=source['employer'],
                           title=slug_title('/'+path_match(url)['slug']),url=url,apply_url=url,
                           needs_page=True,sitemap_url=url)
                      for (id,matched),url in sorted(postings.items()) if matched],
                     len({id for id,_ in postings}))


class PostingMarkup(HTMLParser):
    """Read schema.org properties inside the single RMK JobPosting scope."""
    def __init__(self, body):
        super().__init__()
        self.stack=[]
        self.fields=defaultdict(list)
        self.layout=defaultdict(list)
        self.scopes=0
        self.feed(body.decode('utf-8','replace'))

    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        scope=(attrs.get('itemtype') or '').rstrip('/').endswith('schema.org/JobPosting')
        self.scopes+=scope
        parent=self.stack[-1] if self.stack else ('',False,None,False,None)
        active=scope or parent[1]
        ignored=parent[3] or tag in ('script','style','template','noscript')
        prop=attrs.get('itemprop') if active and not ignored else None
        if prop:
            value=attrs.get('content') or attrs.get('datetime')
            if value:
                self.fields[prop].append(value)
                prop=None
        layout=parent[4]
        if active and 'joblayouttoken' in (attrs.get('class') or '').split():
            layout=[]
            self.layout['tokens'].append(layout)
        if tag not in VOID:
            self.stack.append((tag,active,prop,ignored,layout))

    def handle_endtag(self, tag):
        for index in range(len(self.stack)-1,-1,-1):
            if self.stack[index][0]==tag:
                del self.stack[index:]
                break

    def handle_data(self, data):
        if self.stack and not self.stack[-1][3] and data.strip():
            layout=self.stack[-1][4]
            if layout is not None:
                layout.append(data)
            for _,_,prop,_,_ in reversed(self.stack):
                if prop:
                    self.fields[prop].append(data)
                    break

    def posting(self, layout_url=None, headings=()):
        if self.scopes!=1:
            return None
        post={key:plain(' '.join(self.fields[key])) for key in
              ('title','description','datePosted','validThrough','employmentType')}
        addresses=[]
        for line in self.fields['streetAddress']:
            pieces=[piece.strip() for piece in line.split(',')]
            if len(pieces)>=2 and pieces[1] in COUNTRIES:
                addresses.append({'addressLocality':pieces[0],'addressCountry':pieces[1]})
        if not addresses and self.fields['addressCountry']:
            addresses=[{'addressCountry':self.fields['addressCountry'][0],
                        'addressLocality':plain(' '.join(self.fields['addressLocality']))}]
        if layout_url and not post['title']:
            labels={}
            for token in self.layout['tokens']:
                label,separator,value=plain(' '.join(token)).partition(':')
                if separator:
                    labels[label]=value.strip()
            post.update(title=labels.get('Stellenbezeichnung'),description=labels.get('Stellenbeschreibung'),
                        datePosted=labels.get('Startdatum der Ausschreibung'))
            # The audited BMW layout omits the location value. Its German sitemap
            # supplies the city, federal state and five-digit postal code explicitly.
            slug=path_match(layout_url)['slug']
            match=re.fullmatch(r'([^-]+)-.+-(?:BE|BY|SN|BB|BW|HB|HH|HE|MV|NI|NW|RP|SH|SL|ST|TH)-\d{5}',slug)
            if match:
                addresses=[{'addressLocality':match[1],'addressCountry':'DE'}]
        post['jobLocation']=[{'address':address} for address in addresses]
        if not post['title'] and len(headings)==1:
            post['title']=headings[0]
        return post if post['title'] and post['description'] else None


def rmk_date(value):
    if not value:
        return None
    for format in (None, '%a %b %d %H:%M:%S UTC %Y','%d.%m.%y'):
        try:
            if format is None:
                return datetime.fromisoformat(value.replace('Z','+00:00')).date().isoformat()
            return datetime.strptime(value,format).date().isoformat()
        except ValueError:
            continue
    raise ValueError('Unrecognized SF-RMK posting date')


def job_record(record, source, client):
    from .applications import ensure_open_document
    from .universal import Document, job_from_json
    body,final=request(source,client,record['url'])
    final_id=path_match(final)['id']
    doc=Document(body,final)
    canonicals=[urljoin(final,url) for url in doc.canonical_links]
    if canonicals and not any(path_match(url) and path_match(url)['id']==final_id
                              and urlsplit(url).hostname==urlsplit(final).hostname for url in canonicals):
        raise ValueError('SF-RMK canonical vacancy identifier disagrees')
    ensure_open_document(doc)
    posts=doc.jobposts()
    layout_url=record['url'] if source.get('reviewed_rmk_layout')=='bmw-de' else None
    headings=doc.h1
    if not headings and canonicals and doc.meta.get('og:title')==doc.meta.get('twitter:title'):
        headings=[doc.meta['og:title']] if doc.meta.get('og:title') else []
    post=posts[0] if len(posts)==1 else PostingMarkup(body).posting(layout_url,headings) if not posts else None
    if not post:
        raise ValueError('No unique supported SF-RMK JobPosting')
    post=dict(post,datePosted=rmk_date(post.get('datePosted')),validThrough=rmk_date(post.get('validThrough')))
    if post.get('url'):
        advertised=urljoin(final,post['url'])
        if not path_match(advertised) or path_match(advertised)['id']!=final_id or urlsplit(advertised).hostname!=urlsplit(final).hostname:
            raise ValueError('Structured SF-RMK vacancy identifier disagrees')
    addresses=post.get('jobLocation') or []
    addresses=addresses if isinstance(addresses,list) else [addresses]
    if not any(isinstance(loc,dict) and isinstance(loc.get('address'),dict)
               and loc['address'].get('addressCountry') for loc in addresses):
        raise ValueError('SF-RMK workplace country lacks structured evidence')
    result=job_from_json(dict(post,validThrough=None),final,source)
    if not result or not result.get('countries'):
        raise ValueError('Missing SF-RMK job title or description')
    cta=any(urlsplit(urljoin(final,href)).hostname==urlsplit(final).hostname and
            re.fullmatch(r'/(?:talentcommunity/apply|applybutton)/'+final_id+r'/?',
                         urlsplit(urljoin(final,href)).path) for href,_,_ in doc.links)
    return dict(record,**{key:result[key] for key in ('title','text','city','countries','location','employment')},
                external_id=final_id,posting_identifier=final_id,url=canonical_url(final),apply_url=canonical_url(final),
                published_at=post['datePosted'],valid_through=post['validThrough'],needs_page=False,
                sf_rmk_listing=bool(cta and canonicals))
