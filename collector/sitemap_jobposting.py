"""Bounded GET-only discovery from reviewed corporate and Workday sitemaps."""
from datetime import datetime, timezone
import json
from html.parser import HTMLParser
import re
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urljoin, urlsplit, urlunsplit, parse_qs, quote
import xml.etree.ElementTree as ET

from .adapters import AGENT, ScopedRedirect
from .applications import ensure_open_document
from .classify import canonical_url, fold, plain
from .employer_pages import PageParser, decompress_sitemap, slug_title
from .runtime import CollectionBudgetExceeded
from .ownership import employer_matches
from .sf_rmk import HR, NON_STAGE, STAGE, PostingMarkup, path_match, rmk_date
from .universal import Document, Inventory, job_from_json
from .verification import same_requisition, shares_identifier

ADAPTERS = ('sitemap-jobposting', 'workday')
MAX_DISCOVERY_REQUESTS = 12
MAX_REQUESTS = 262
WORKDAY = re.compile(r'/(?:[a-z]{2}(?:-[a-z]{2})?/)?(?P<site>[^/]+)/job/(?:[^/]+/)*[^/]+_(?P<id>[^/]+)', re.I)
EXCLUDED = re.compile(r'\b(?:graduate|apprentice|apprenticeship)\b')
APPLICATION_ROUTE = re.compile(r'(?:^|/)(?:apply|applybutton|application|preapply|talentcommunity|solliciteren|bewerben|postuler)(?:/|$)', re.I)
JOB_MAP = re.compile(r'job|vacanc|career|offer|offre|stelle|emploi|empleo|lavoro|position', re.I)


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
    # Bare "compensation" can describe an engineering operation.
    hr_title = re.sub(r'\bcompensation\b(?!\s+(?:and|&)\s+benefits)', '', title)
    return bool(STAGE.search(title) and HR.search(hr_title)
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
    if source.get('reviewed_listing_layout') == 'mercedes-benz':
        match = re.search(r'-(mer[0-9a-z]{7}|j\d{9})$', path, re.I)
        return match[1].casefold() if match else None
    if source.get('job_id_pattern'):
        match = re.search(source['job_id_pattern'], path)
        return match['id'].casefold() if match else None
    if source.get('reviewed_rmk_dates'):
        match = path_match(url)
        if match:
            return match['id']
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
        self.observations = []
        self.discovering = True
        self.retried_rate_limit = False

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
        try:
            return self._get_once(url, robots=robots)
        except HTTPError as exc:
            retry = getattr(self.client, 'retry_rate_limited_get', None)
            if (exc.code != 429 or self.source['adapter'] != 'workday'
                    or self.retried_rate_limit or not callable(retry)
                    or (self.discovering and self.requests >= MAX_DISCOVERY_REQUESTS)
                    or self.observations[-1].get('rate_limited_skip')):
                raise
            self.retried_rate_limit = True
            self.blocked = False
            return self._get_once(url, robots=robots, rate_limit=exc)
        except ScopedRedirect as exc:
            original_id = posting_id(url, self.source)
            target = exc.target
            old_rmk = path_match(url) if (self.source.get('reviewed_rmk_layout') or self.source.get('reviewed_rmk_redirects')) else None
            new_rmk = path_match(target) if old_rmk else None
            reviewed_rmk_redirect = bool(new_rmk and fold(old_rmk['slug']) == fold(new_rmk['slug']))
            sitemap_redirect = (self.discovering and self.requests < MAX_DISCOVERY_REQUESTS
                                and re.search(r'(?:sitemap[^/]*|[^/]+)\.xml(?:\.gz)?$',
                                              urlsplit(target).path, re.I))
            if not robots and sitemap_redirect and self.permitted(target):
                return self._get_once(target, robots=False)
            if (not robots and not self.discovering
                    and original_id and self.permitted(target)
                    and not APPLICATION_ROUTE.search(unquote(urlsplit(target).path))
                    and (posting_id(target, self.source) == original_id or reviewed_rmk_redirect)):
                return self._get_once(target, robots=False)
            raise

    def _get_once(self, url, *, robots, rate_limit=None):
        if self.blocked or self.requests >= MAX_REQUESTS:
            raise CollectionBudgetExceeded('Sitemap host stopped or request budget exhausted')
        if not self.scoped(url) or (not robots and not self.permitted(url)):
            raise ValueError('URL outside approved robots scope')
        previous = getattr(self.client, 'redirect_scope_allowed', None)
        self.client.redirect_scope_allowed = lambda target: False
        preserve = getattr(self.client, 'preserve_request_url', False)
        self.client.preserve_request_url = True
        parsed = urlsplit(url)
        wire_url = urlunsplit((parsed.scheme, parsed.netloc,
                               quote(parsed.path, safe="/%:@!$&'()*+,;=-._~"),
                               quote(parsed.query, safe="%/?+:@!$&'()*+,;=-._~"), ''))
        self.requests += 1
        observation = dict(url=url, phase="robots" if robots else "sitemap" if self.discovering else "detail")
        self.observations.append(observation)
        before = getattr(self.client, 'requests', None)
        try:
            if rate_limit:
                body, status, final = self.client.retry_rate_limited_get(wire_url, rate_limit)
            else:
                body, status, final = self.client.request(wire_url, robots=False, attempts=1)
            observation['http'] = status
            if status != 200 or canonical_url(url) != canonical_url(final):
                raise ValueError('Exact public HTTP 200 response required')
            return body
        except ScopedRedirect as exc:
            observation.update(http=exc.status, redirect=exc.target)
            raise
        except HTTPError as exc:
            observation['http'] = exc.code
            if exc.code == 429 and before is not None and self.client.requests == before:
                observation['rate_limited_skip'] = True
            if exc.code in (401, 403, 429, 451):
                self.blocked = True
            raise
        except (URLError, OSError, ValueError, CollectionBudgetExceeded) as exc:
            observation['error'] = str(exc)[:180]
            raise
        finally:
            self.client.redirect_scope_allowed = previous
            self.client.preserve_request_url = preserve

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
    client.sitemap_jobposting_observations = scan.observations
    pending = set(scan.preflight())
    seen, records = set(), {}
    url_filter = re.compile(source.get('job_url_pattern', ''))
    preferred = tuple(source.get('preferred_sitemap_paths', ()))
    pending = {url for url in pending if scan.permitted(url)}
    if not pending:
        raise ValueError('No permitted same-host sitemap')
    errors = []
    maps_parsed = 0
    def priority(url):
        path = urlsplit(url).path
        rank = next((i for i, prefix in enumerate(preferred) if path.startswith(prefix)), len(preferred))
        return (not bool(JOB_MAP.search(path)), rank, url)

    while pending and scan.requests < MAX_DISCOVERY_REQUESTS and not scan.blocked:
        sitemap = min(pending, key=priority)
        pending.remove(sitemap)
        if sitemap in seen or not scan.permitted(sitemap):
            continue
        seen.add(sitemap)
        try:
            body = decompress_sitemap(scan.get(sitemap))
            if b'<!DOCTYPE' in body.replace(b'\0', b'').upper():
                raise ValueError('DOCTYPE not permitted in sitemap')
            root = ET.fromstring(body)
        except (CollectionBudgetExceeded, OSError, ValueError, ET.ParseError) as exc:
            errors.append(dict(url=sitemap, error=str(exc)[:180]))
            if isinstance(exc, CollectionBudgetExceeded):
                break
            continue
        maps_parsed += 1
        kind = root.tag.rsplit('}', 1)[-1]
        if kind == 'sitemapindex':
            pending.update(set(locations(root, 'sitemap')) - seen)
            continue
        if kind != 'urlset':
            errors.append(dict(url=sitemap, error='Unsupported sitemap root'))
            continue
        for url in locations(root, 'url'):
            if not scan.permitted(url):
                continue
            path = urlsplit(url).path.rstrip('/')
            if APPLICATION_ROUTE.search(unquote(path)) or not url_filter.search(path):
                continue
            parts = path.strip('/').split('/')
            while len(parts)>1 and re.fullmatch(r'[A-Za-z]{0,8}\d+(?:[-_][a-z]{2}[-_][a-z]{2})?', parts[-1], re.I):
                parts.pop()
            slug = re.sub(r'\.(?:s?html?|aspx?)$', '', parts[-1], flags=re.I)
            title = slug_title('/' + slug.replace('_', '-'))
            identifier = posting_id(url, source)
            if not candidate(title) or (source['adapter'] == 'workday' and not identifier):
                continue
            key = identifier or canonical_url(url)
            records.setdefault(key, dict(source_id=source['id'], external_id=key, title=title,
                                         employer=source['employer'], url=url, apply_url=url, needs_page=True))
    if not maps_parsed and errors:
        raise ValueError(errors[-1]['error'])
    scan.discovering = False
    client.sitemap_jobposting_scan = scan
    return Inventory(records.values(), dict(sitemap_candidates=len(records),
                                    sitemaps_read=len(seen), sitemap_errors=errors,
                                    sitemaps_pending=sum(scan.permitted(url) for url in pending),
                                    status='partial' if errors or pending else 'ok',
                                    closure_complete=False))


class MercedesListingControl(HTMLParser):
    """Read the reviewed job-detail component without following its target."""
    def __init__(self, body):
        super().__init__()
        self.targets = set()
        self.feed(body.decode('utf-8', 'replace'))

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if (tag == 'wb-button' and 'mjp-job-ad__content-tags-join-button' in (attrs.get('class') or '').split()
                and (attrs.get('aria-label') or '').casefold() in ('bewerben', 'apply', 'apply now')
                and 'disabled' not in attrs and attrs.get('aria-disabled') != 'true' and attrs.get('href')):
            self.targets.add(attrs['href'])


def mercedes_listing_control(body, url, source, identifier):
    if urlsplit(url).hostname != 'jobs.mercedes-benz.com' or not identifier:
        return False
    if identifier.casefold() != posting_id(url, source):
        return False
    targets = MercedesListingControl(body).targets
    if len(targets) != 1:
        return False
    try:
        target = urlsplit(canonical_url(next(iter(targets))))
    except ValueError:
        return False
    if target.hostname == 'jobs.mercedes-amg.com':
        return bool(re.fullmatch(r'/job-invite/\d+', target.path))
    if target.hostname == 'tas-daimler.taleo.net':
        return (target.path.endswith('/jobapply.ftl') and
                [value.casefold() for value in parse_qs(target.query).get('job', [])] == [identifier.casefold()])
    return False


def danone_posting(body, url):
    """Read the reviewed Danone job fragment for this exact URL."""
    parser = PageParser()
    parser.feed(body.decode('utf-8', 'replace'))
    key = urlsplit(url).path.rsplit('/', 1)[-1].removesuffix('.html')
    matches = [item for item in parser.fragments if item.get('key') == key]
    if not matches or any(item != matches[0] for item in matches[1:]):
        return None
    item = matches[0]
    job_id = item.get('jobid') or ''
    posted = item.get('posted') or ''
    if not job_id.isdecimal() or not posted.isdecimal():
        return None
    return dict(title=item.get('title'), description=(item.get('descriptionheader') or '')+' '+(item.get('description') or ''),
                employmentType=item.get('positiontype'), identifier=job_id, inLanguage=item.get('locale'),
                datePosted=datetime.fromtimestamp(int(posted)/1000, timezone.utc).isoformat(),
                jobLocation={'address': {'addressCountry': item.get('country'), 'addressLocality': item.get('city')}})


def phenom_listing(body, result, hosts):
    """The embedded external job and the official CTA must identify this JobPosting."""
    expected = str(result.get('posting_identifier') or '').casefold()
    script = re.search(r'phApp\.ddo\s*=\s*(?=\{)', body.decode('utf-8','replace'))
    if not expected or script is None:
        return False
    try:
        payload, _ = json.JSONDecoder().raw_decode(script.string, script.end())
        job = payload['jobDetail']['data']['job']
        if (str(job.get('jobId','')).casefold() != expected or str(job.get('reqId','')).casefold() != expected
                or fold(plain(job.get('title'))) != fold(result['title'])
                or not isinstance(job.get('jobVisibility'), list) or 'external' not in job['jobVisibility']):
            return False
        target = urlsplit(canonical_url(job['applyUrl']))
        if target.hostname not in hosts:
            return False
        if target.hostname.endswith('.myworkdayjobs.com'):
            match = WORKDAY.fullmatch(target.path.removesuffix('/apply'))
            return bool(target.path.endswith('/apply') and match and
                        match['id'].casefold() in (expected, expected+'-1'))
        return parse_qs(target.query).get('career_job_req_id') == [expected] and target.path == '/careers'
    except (KeyError, TypeError, ValueError, AttributeError):
        return False


def job_record(record, source, client):
    scan = client.sitemap_jobposting_scan
    url = record['url']
    body = scan.get(url)
    url = scan.observations[-1]['url']
    doc = Document(body, url)
    try:
        ensure_open_document(doc)
    except ValueError as exc:
        from .verification import blocked_error
        if blocked_error(exc):
            scan.blocked = True
        raise
    posts = doc.jobposts()
    layout = url if source.get('reviewed_rmk_layout') == 'bmw-de' and path_match(url) else None
    microdata = PostingMarkup(body).posting(layout, doc.h1) if not posts else None
    scan.observations[-1]['markup'] = ('json-ld' if posts else 'microdata' if microdata else 'none')
    post = posts[0] if len(posts) == 1 else microdata
    danone = not post and not posts and source.get('reviewed_listing_layout') == 'danone'
    if danone:
        post = danone_posting(body, url)
        if post:
            scan.observations[-1]['markup'] = 'danone-structured-fragment'
    if not post:
        raise ValueError('No unique JobPosting')
    stable = posting_id(url, source)
    links = list(doc.canonical_links) + ([post['url']] if post.get('url') else [])
    for link in links:
        target = urljoin(url, link)
        if not scan.scoped(target) or (canonical_url(url) != canonical_url(target)
                                      and not (stable and posting_id(target, source) == stable)):
            raise ValueError('JobPosting URL does not identify the sitemap vacancy')
    if source.get('reviewed_rmk_dates'):
        post = dict(post, datePosted=rmk_date(post.get('datePosted')),
                    validThrough=rmk_date(post.get('validThrough')))
    result = job_from_json(dict(post, url=url, validThrough=None), url, source)
    if not result or not result.get('countries'):
        organization = post.get('hiringOrganization')
        name = plain(organization.get('name')) if isinstance(organization, dict) else ''
        if name and not employer_matches(name, source, url):
            raise ValueError(f'Unreviewed hiring organization: {name[:100]}')
        if not result:
            raise ValueError('JobPosting missing a usable title or description')
        raise ValueError('Explicit workplace country outside scope or missing')
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
    reference_hosts = source.get('reviewed_application_reference_hosts', [])
    if stable and reference_hosts:
        result['sitemap_jobposting_cta'] |= any(
            urlsplit(href).scheme == 'https' and urlsplit(href).hostname in reference_hosts
            and shares_identifier(dict(result, external_id=stable), href)
            for href,label,_ in doc.links if re.search(r'\b(?:apply|bewerben|postuler)\b', fold(label)))
    sources_for_alias = source.get('replaces_source_ids', [])
    if identifier:
        result['identity_aliases'] = [f'posting:{previous}:{identifier}' for previous in sources_for_alias]
    if source.get('reviewed_phenom_application_hosts'):
        result['sitemap_jobposting_cta'] |= phenom_listing(body, result, source['reviewed_phenom_application_hosts'])
    if danone:
        result['sitemap_jobposting_cta'] |= any(
            re.fullmatch(r'(?:de|fr|nl|uk|es|it|pl|global)apply-danone\.icims\.com', urlsplit(href).hostname or '')
            and urlsplit(href).scheme == 'https'
            and urlsplit(href).path.rstrip('/') == f'/jobs/{identifier}/login'
            and 'apply' in fold(label)
            for href,label,_ in doc.links)
    if source.get('reviewed_listing_layout') == 'mercedes-benz':
        result['sitemap_jobposting_cta'] |= mercedes_listing_control(
            body, url, source, result.get('posting_identifier'))
    return result
