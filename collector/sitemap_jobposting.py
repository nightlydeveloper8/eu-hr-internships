"""Bounded GET-only discovery from reviewed corporate and Workday sitemaps."""
from datetime import datetime
import re
from urllib.error import HTTPError
from urllib.parse import unquote, urljoin, urlsplit, parse_qs
import xml.etree.ElementTree as ET

from .adapters import AGENT
from .applications import ensure_open_document
from .classify import canonical_url, fold
from .employer_pages import decompress_sitemap, slug_title
from .runtime import CollectionBudgetExceeded
from .sf_rmk import HR, NON_STAGE, STAGE, PostingMarkup
from .universal import Document, Inventory, job_from_json
from .verification import same_requisition, shares_identifier

ADAPTERS = ('sitemap-jobposting', 'workday')
MAX_SITEMAPS = 6
MAX_DETAILS = 10
MAX_REQUESTS = 1 + MAX_SITEMAPS + MAX_DETAILS
WORKDAY = re.compile(r'/(?:[a-z]{2}(?:-[a-z]{2})?/)?(?P<site>[^/]+)/job/(?:[^/]+/)*[^/]+_(?P<id>[^/]+)', re.I)
EXCLUDED = re.compile(r'\b(?:graduate|apprentice|apprenticeship)\b')
JOB_MAP = re.compile(r'job|vacanc|career|stellen|emploi|offres|empleo|lavoro', re.I)


def robots_policy(text):
    groups, maps = [], []
    agents, rules = [], []
    for line in text.splitlines():
        kind, _, value = line.partition('#')[0].partition(':')
        kind, value = kind.strip().lower(), value.strip()
        if kind == 'user-agent' and value:
            if rules:
                groups.append((agents, rules))
                agents, rules = [], []
            agents.append(value.lower())
        elif kind == 'sitemap' and value:
            maps.append(value)
        elif agents and kind in ('allow', 'disallow', 'crawl-delay'):
            rules.append((kind, value))
    groups.append((agents, rules))
    bot = AGENT.split('/')[0].lower()
    specific = [rule for names, rules in groups if bot in names for rule in rules]
    selected = specific if any(bot in names for names, _ in groups) else [
        rule for names, rules in groups if '*' in names for rule in rules]
    delays = [float(value) for kind, value in selected
              if kind == 'crawl-delay' and re.fullmatch(r'\d+(?:\.\d+)?', value)]
    return selected, maps, max([2., *delays])


def robots_allows(rules, url):
    parsed = urlsplit(url)
    path = parsed.path or '/'
    if parsed.query:
        path += '?' + parsed.query
    for target in {path, unquote(path)}:
        matches = []
        for kind, value in rules:
            if kind not in ('allow', 'disallow') or not value:
                continue
            for pattern in {value, unquote(value)}:
                prefix = pattern.removesuffix('$')
                regex = re.escape(prefix).replace(r'\*', '.*')
                if re.match(regex + ('$' if pattern.endswith('$') else ''), target):
                    matches.append((len(prefix.replace('*', '')), kind == 'allow'))
        if not max(matches, default=(0, True))[1]:
            return False
    return True


def candidate(title):
    title = fold(title).replace('ł', 'l')
    return bool(STAGE.search(title) and HR.search(title)
                and not NON_STAGE.search(title) and not EXCLUDED.search(title))


def posting_id(url, source):
    parsed = urlsplit(url)
    path = unquote(parsed.path).rstrip('/')
    if source['adapter'] == 'workday':
        match = WORKDAY.fullmatch(path)
        return match['id'] if match and match['site'] == source['workday_site'] else None
    ids = parse_qs(parsed.query)
    for key in ('jobId', 'jobid', 'requisitionId', 'id'):
        values = ids.get(key, [])
        if len(values) == 1 and re.fullmatch(r'[\w-]+', values[0]):
            return values[0].casefold()
    segment = path.rsplit('/', 1)[-1]
    segment = re.sub(r'\.(?:s?html?|aspx?)$', '', segment, flags=re.I)
    segment = re.sub(r'[-_][a-z]{2}[-_][a-z]{2}$', '', segment, flags=re.I)
    match = re.search(r'(?:^|[/_-])([A-Za-z]{1,8}\d{4,}|\d{5,}|[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12})$', segment, re.I)
    if not match:
        match = re.search(r'/((?:JR|REQ|REF)\d{4,})/[^/]+$', path, re.I)
    return match[1].casefold() if match else None


class Scan:
    def __init__(self, source, client):
        self.client = client
        self.source = source
        self.host = urlsplit(source['career_url']).hostname
        if self.host not in source['allowed_hosts'] or source.get('access_review') != 'allowed':
            raise ValueError('Exact career host requires a documented access review')
        self.rules = []
        self.requests = 0
        self.blocked = False

    def scoped(self, url):
        try:
            parsed = urlsplit(url)
            path = unquote(parsed.path)
            return (parsed.netloc == self.host and not parsed.fragment
                    and not re.search(r'[\x00-\x20\x7f]', url) and '\\' not in path
                    and not any(part in ('.', '..') for part in path.split('/'))
                    and bool(canonical_url(url)))
        except ValueError:
            return False

    def permitted(self, url):
        return self.scoped(url) and robots_allows(self.rules, url) and robots_allows(self.rules, canonical_url(url))

    def get(self, url, *, robots=False):
        if self.blocked or self.requests >= MAX_REQUESTS:
            raise CollectionBudgetExceeded('Sitemap host stopped or request budget exhausted')
        if not self.scoped(url) or (not robots and not self.permitted(url)):
            raise ValueError('URL outside approved robots scope')
        previous = getattr(self.client, 'redirect_scope_allowed', None)
        self.client.redirect_scope_allowed = lambda target: False
        self.requests += 1
        try:
            body, status, final = self.client.request(url, robots=False, attempts=1)
            if status != 200 or canonical_url(url) != canonical_url(final):
                raise ValueError('Exact public HTTP 200 response required')
            return body
        except HTTPError as exc:
            if exc.code in (401, 403, 429, 451):
                self.blocked = True
            raise
        finally:
            self.client.redirect_scope_allowed = previous

    def preflight(self):
        text = self.get(f'https://{self.host}/robots.txt', robots=True).decode('utf-8-sig')
        if re.search(r'<(?:html|!doctype|title|body)|captcha', text, re.I):
            raise ValueError('robots.txt returned HTML or an access challenge')
        self.rules, maps, delay = robots_policy(text)
        self.client.host_delays[self.host] = max(delay, self.client.host_delays.get(self.host, 0))
        if self.source['adapter'] == 'workday' and not maps:
            raise ValueError('Workday requires a robots-advertised sitemap')
        return maps or [f'https://{self.host}/sitemap.xml']


def locations(root, child):
    for entry in root:
        if entry.tag.rsplit('}', 1)[-1] == child:
            for loc in entry:
                if loc.tag.rsplit('}', 1)[-1] == 'loc' and loc.text:
                    yield loc.text.strip()


def collect_records(source, client):
    scan = Scan(source, client)
    pending = set(scan.preflight())
    seen, records = set(), {}
    url_filter = re.compile(source.get('job_url_pattern', ''))
    pending = {url for url in pending if scan.permitted(url)}
    if not pending:
        raise ValueError('No permitted same-host sitemap')
    while pending and len(seen) < MAX_SITEMAPS:
        sitemap = min(pending, key=lambda url: (not bool(JOB_MAP.search(url)), url))
        pending.remove(sitemap)
        if sitemap in seen or not scan.permitted(sitemap):
            continue
        seen.add(sitemap)
        body = decompress_sitemap(scan.get(sitemap))
        # Reject DTDs even when the input declares UTF-16/32.
        if b'<!DOCTYPE' in body.replace(b'\0', b'').upper():
            raise ValueError('DOCTYPE not permitted in sitemap')
        root = ET.fromstring(body)
        kind = root.tag.rsplit('}', 1)[-1]
        if kind == 'sitemapindex':
            pending.update(set(locations(root, 'sitemap')) - seen)
            continue
        if kind != 'urlset':
            raise ValueError('Unsupported sitemap root')
        for url in locations(root, 'url'):
            if not scan.permitted(url):
                continue
            path = urlsplit(url).path.rstrip('/')
            if not url_filter.search(path):
                continue
            parts = path.split('/')
            slug = parts[-1]
            if len(parts) > 2 and re.fullmatch(r'[A-Za-z]{0,8}\d+', slug):
                slug = parts[-2]
            title = slug_title('/' + slug.replace('_', '-'))
            identifier = posting_id(url, source)
            if not candidate(title) or (source['adapter'] == 'workday' and not identifier):
                continue
            key = identifier or canonical_url(url)
            records.setdefault(key, dict(source_id=source['id'], external_id=key, title=title,
                                         employer=source['employer'], url=url, apply_url=url, needs_page=True))
    client.sitemap_jobposting_scan = scan
    selected = list(records.values())[:MAX_DETAILS]
    return Inventory(selected, dict(sitemap_candidates=len(records), selected_candidates=len(selected),
                                    sitemaps_read=len(seen), closure_complete=False))


def job_record(record, source, client):
    scan = client.sitemap_jobposting_scan
    url = record['url']
    body = scan.get(url)
    doc = Document(body, url)
    try:
        ensure_open_document(doc)
    except ValueError as exc:
        from .verification import blocked_error
        if blocked_error(exc):
            scan.blocked = True
        raise
    posts = doc.jobposts()
    post = posts[0] if len(posts) == 1 else PostingMarkup(body).posting() if not posts else None
    if not post:
        raise ValueError('No unique JobPosting')
    stable = posting_id(url, source)
    links = list(doc.canonical_links) + ([post['url']] if post.get('url') else [])
    for link in links:
        target = urljoin(url, link)
        if not scan.scoped(target) or (canonical_url(url) != canonical_url(target)
                                      and not (stable and posting_id(target, source) == stable)):
            raise ValueError('JobPosting URL does not identify the sitemap vacancy')
    result = job_from_json(dict(post, url=url, validThrough=None), url, source)
    if not result or not result.get('countries'):
        raise ValueError('Usable JobPosting and explicit workplace country required')
    if not candidate(result['title']):
        raise ValueError('Structured title is outside HR internship scope')
    # Reject malformed or contradictory dates at detail scope, not host scope.
    dates = {}
    for key in ('datePosted', 'validThrough'):
        value = post.get(key)
        if value:
            if not isinstance(value, str):
                raise ValueError('JobPosting date is not an ISO date string')
            dates[key] = datetime.fromisoformat(value.strip().replace('Z', '+00:00')).date()
    if dates.get('datePosted') and dates.get('validThrough') and dates['validThrough'] < dates['datePosted']:
        raise ValueError('JobPosting deadline precedes publication')
    identifier = result.get('posting_identifier') or stable
    result.update(external_id=identifier or canonical_url(url), posting_identifier=identifier,
                  valid_through=(post.get('validThrough') or '').strip() or None,
                  published_at=dates['datePosted'].isoformat() if 'datePosted' in dates else None)
    result['sitemap_jobposting_cta'] = any(
        scan.scoped(target) and (same_requisition(url, target) or shares_identifier(result, target))
        for href, label, _ in doc.links
        if re.search(r'\b(?:apply|bewerben|postuler|candidati|candidatar|solliciteer|inscribirse)\b', fold(label))
        for target in (urljoin(url, href),)
    )
    return result
