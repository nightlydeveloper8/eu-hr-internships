"""Discover recruiting sitemaps and activate sources backed by a live replay."""

import argparse
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
from datetime import datetime
from hashlib import sha256
import json
import time
from pathlib import Path
import re
from tempfile import TemporaryDirectory
from urllib.error import HTTPError
from urllib.parse import unquote, urlsplit
from xml.etree.ElementTree import ParseError
from zoneinfo import ZoneInfo

from .classify import COUNTRIES, canonical_url, excluded_german_title, excluded_placement_title
from .employer_pages import slug_title
from .pipeline import ROOT, finalize, now, process_source, read, write
from .runtime import BudgetClient, CollectionBudgetExceeded
from .sitemap_jobposting import (APPLICATION_ROUTE, JOB_MAP, Scan, candidate, locations,
                                 parse_sitemap, robots_allows, robots_policy)
from .verification import verified_job

STATE = ROOT / 'data/discovery-activations.json'
SOURCES = ROOT / 'data/sources.json'
STAGING = ROOT / 'docs/staging'
WEEKLY_LIMIT = 20
SHARDS = 16
EXCLUDED = {
    'linkedin.com', 'indeed.com', 'infojobs.net', 'infojobs.it', 'glassdoor.com',
    'kering.com', 'richemont.com', 'ryanair.com', 'hubspot.com', 'sebgroup.com',
    'werkenbijabnamro.nl', 'freseniusmedicalcare.com', 'novartis.com', 'jobs.fuchs.com',
    'michaelpage.pt', 'grafton.cz', 'grafton.sk', 'grafton.com', 'smartrecruiters.com',
    'ashbyhq.com', 'welcometothejungle.com', 'randstad.es', 'manpower.it',
    'careers.essilorluxottica.com',
}
AGENCY_HOSTS = '''
www.randstad.dk www.randstad.lu www.randstad.at manpower.lu www.manpower.hr
www.manpower.si www.manpower.hu www.adecco.com www.michaelpage.pt www.grafton.cz
www.grafton.sk pl.grafton.com www.staffpoint.fi karriar.uniflex.se
'''.split()
GROUPS = ('randstad', 'manpower', 'adecco', 'michaelpage', 'grafton', 'staffpoint',
          'uniflex', 'gigroup', 'synergie', 'hays', 'robertwalters')


def week_for(stamp):
    year, week, _ = datetime.fromisoformat(stamp).astimezone(ZoneInfo('Europe/Amsterdam')).isocalendar()
    return f'{year}-W{week:02}'


def host_of(source):
    return urlsplit(source.get('career_url', '')).hostname


def platform(source):
    if source.get('discovery_platform'):
        return source['discovery_platform']
    adapter = source['adapter']
    if adapter == 'sf-rmk':
        return adapter
    if adapter == 'sitemap-jobposting':
        if source.get('reviewed_listing_layout') == 'bosch':
            return 'bosch'
        return 'radancy' if 'radancy' in source.get('permission_basis', '').lower() else adapter
    if adapter == 'employer-sitemap':
        basis = source.get('permission_basis', '').lower()
        for known in ('radancy', 'phenom'):
            if f'({known})' in basis:
                return known
        if source.get('published_listing_platform') == 'teamtailor':
            return 'teamtailor'
        if source['id'] == 'paesi-piccoli-jks-dk' or source.get('published_listing_platform') == 'talentech':
            return 'talentech'
        if source.get('staffing_agency') or source.get('agency_slug_country'):
            employer = re.sub('[^a-z]', '', source['employer'].lower())
            return next((group for group in GROUPS if employer.startswith(group)), None)
    return None


def inventory(sources):
    hosts = defaultdict(lambda: {'maps': set(), 'migration': set(), 'templates': {}})
    exclusions = set(EXCLUDED)
    small = read(STAGING / 'paesi-piccoli-discovery.json', {})
    for host in (*small['part_a'], *small['universities'], *AGENCY_HOSTS):
        hosts[host]['platform_hint'] = small['part_a'].get(host)
    for source in small.get('reviewed_sources', []):
        entry = hosts[host_of(source)]
        entry['maps'].update(source.get('sitemaps', []))
        if source.get('access_review') == 'allowed' and source.get('reviewed_on') and source.get('permission_basis'):
            entry['templates'][source['id']] = source
    for company in read(ROOT / 'data/companies.json', []):
        host = urlsplit(company.get('career_url') or company.get('website_url') or '').hostname
        if host:
            hosts[host]
    for document in (ROOT / 'docs').glob('agenzie-*-2026-11.md'):
        for host in re.findall(r'https://([\w.-]+)', document.read_text()):
            if host.removeprefix('www.').split('.')[0] in GROUPS:
                hosts[host]
    for document in ('docs/corporate-da-rivedere.csv', 'docs/migrazione-sitemap-candidati.csv',
                     'docs/staging/migrazione-sitemap-riesame-203.csv'):
        with (ROOT / document).open(newline='') as handle:
            for row in csv.DictReader(handle):
                entry = hosts[row['host']]
                if row.get('source_id'):
                    entry['migration'].add(row['source_id'])
                if sitemap := row.get('sitemap', row.get('url_sitemap')):
                    entry['maps'].add(sitemap)
    for lot in read(STAGING / 'held-career-lots-20261124.json', {}).values():
        for row in lot['sources']:
            host = row.get('host')
            if not host:
                continue
            hosts[host]
            if row.get('disposition') == 'excluded':
                exclusions.add(host)
            if source := row.get('source'):
                hosts[host]['maps'].update(source.get('sitemaps', []))
                if (platform(source) and source.get('access_review') == 'allowed'
                        and source.get('reviewed_on') and source.get('permission_basis')):
                    hosts[host]['templates'][source['id']] = source
    for source in sources:
        if host := host_of(source):
            hosts[host]['maps'].update(source.get('sitemaps', []))
            if not hosts[host].get('platform_hint') and platform(source):
                hosts[host]['platform_hint'] = platform(source)
            if source.get('access_review') in ('denied', 'excluded') or source.get('status') in ('blocked', 'excluded'):
                exclusions.add(host)
            if (platform(source) and source.get('permission_basis') and source.get('reviewed_on')
                    and (source.get('access_review') == 'allowed' or source.get('status') == 'reviewed-active')):
                hosts[host]['templates'][source['id']] = source
    return hosts, exclusions


def slug_candidate(url):
    path = unquote(urlsplit(url).path)
    segments = path.rstrip('/').split('/')
    while len(segments) > 2 and re.fullmatch(r'[a-zA-Z]{0,8}\d+', segments[-1]):
        segments.pop()
    slug = re.sub(r'\.(?:html?|aspx?)$', '', segments[-1], flags=re.I)
    return not APPLICATION_ROUTE.search(path) and candidate(slug_title('/' + slug.replace('_', '-')))


def fingerprint(value):
    return sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def membership(host):
    return int(sha256(host.encode()).hexdigest()[:8], 16) % SHARDS


PROBE_LIMIT = 12
PLATFORM_MAPS = {
    'sf-rmk': ('/sitemap.xml',),
    'radancy': ('/sitemap', '/sitemap/jobs.xml'),
    'phenom': ('/global/en/sitemap_index.xml', '/eu/en/sitemap_index.xml', '/sitemap-index.xml'),
    'teamtailor': ('/sitemap.xml',),
    'talentech': ('/Sitemap.xml',),
}


def platform_signal(host, rules, urls, hint):
    """Return a provider signal and whether the route layout confirms it."""
    paths = [urlsplit(url).path for url in urls]
    if ({'/applybutton/', '/talentcommunity/'} <=
            {value.lower() for kind, value in rules if kind == 'disallow'}):
        return 'sf-rmk', True
    if host.endswith('.teamtailor.com'):
        return 'teamtailor', True
    if any(re.fullmatch(r'/(?:[a-z-]+/)?job/[^/]+/[^/]+/\d+/\d+/?', path, re.I)
           for path in paths):
        return 'radancy', True
    normalized = (hint or '').lower()
    if normalized == 'phenom' and any(re.fullmatch(r'/[a-z-]+/[a-z-]+/job/[^/]+/[^/]+/?', path)
                                      for path in paths):
        return normalized, True
    if normalized == 'talentech' and any(re.fullmatch(r'/jobs/[^/]+-\d+/?', path) for path in paths):
        return normalized, True
    return (normalized if normalized not in ('', 'non_verificato', 'proprio/altro') else None), False


def map_candidates(host, advertised, hints, known_platform, cached):
    base = f'https://{host}'
    known_routes = PLATFORM_MAPS.get(known_platform, ())
    return list(dict.fromkeys([
        cached.get('sitemap'), *sorted(hints['maps']), *advertised,
        *(base + route for route in known_routes), base + '/sitemap.xml', base + '/sitemap_index.xml',
    ]))


def robots_failure(cached, week, error):
    attempts = cached.get('robots_attempts', 0)
    attempts += cached.get('robots_week') != week
    status = getattr(error, 'code', type(error).__name__)
    return dict(robots_attempts=attempts, robots_week=week, robots_error=status,
                reason=('Robots non letto · hold dopo 3 tentativi' if attempts >= 3
                        else 'Robots non letto · riprovare la prossima settimana'))


def probe(host, hints, exclusions, cached=None):
    if (not re.fullmatch(r'[a-z0-9-]+(?:\.[a-z0-9-]+)+', host)
            or any(host == domain or host.endswith('.' + domain) for domain in exclusions)
            or re.search(r'(?:^|\.)(?:linkedin|indeed|infojobs|glassdoor)\.[a-z.]+$', host)):
        return {'reason': 'Host escluso o non valido', 'requests': 0}
    cached = cached or {}
    routes_key = fingerprint([sorted(hints['maps']), hints.get('platform_hint')])
    if cached.get('routes_key') != routes_key:
        cached = {}
    stamp = now()
    week = week_for(stamp)
    if (cached.get('robots_denied') or cached.get('robots_attempts', 0) >= 3
            or cached.get('robots_week') == week):
        return dict(cached, requests=0, bytes=0, seconds=0, cache_hit=True)

    client = BudgetClient(seconds=85, max_requests=PROBE_LIMIT, delay=2)
    scan = Scan(dict(career_url=f'https://{host}/', allowed_hosts=[host],
                     adapter='sitemap-jobposting', access_review='allowed'), client)
    started = time.monotonic()
    result = {'platform': hints.get('platform_hint'), 'routes_key': routes_key}

    def completed(row):
        return dict(row, requests=client.requests, bytes=client.bytes,
                    seconds=round(time.monotonic() - started, 3))

    try:
        advertised = scan.preflight()
    except (OSError, ValueError, CollectionBudgetExceeded) as error:
        return completed({**result, **robots_failure(cached, week, error)})

    provider, confirmed = platform_signal(host, scan.rules, [], result['platform'])
    robots_key = fingerprint(scan.rules)
    result.update(robots=True, robots_key=robots_key, robots_checked_at=stamp,
                  platform=provider, platform_confirmed=confirmed)
    roots = [url for url in map_candidates(host, advertised, hints, provider, cached)
             if url and scan.permitted(url)]
    if not roots:
        return completed(dict(result, robots_denied=True, reason='Robots vieta i percorsi sitemap'))

    pending = roots[:]
    seen, candidates, job_paths = set(), set(), []
    count = denied_details = 0
    children_seen = False
    errors = []
    while pending and client.requests < PROBE_LIMIT and client.remaining():
        raw = pending.pop(0)
        if raw in seen:
            continue
        seen.add(raw)
        known = cached.get('sitemap') == raw and cached.get('robots_key') == robots_key
        client.conditional_get_headers = {
            header: cached['validators'][key] for key, header in
            (('ETag', 'If-None-Match'), ('Last-Modified', 'If-Modified-Since'))
            if known and cached.get('validators', {}).get(key)
        }
        try:
            content = scan.get(raw, follow_redirects=False)
            signature = fingerprint([robots_key, raw, sha256(content).hexdigest()])
            validators = getattr(client, 'response_validators', {})
            if known and signature == cached.get('signature'):
                return completed(dict(cached, validators=validators, cache_hit=True, robots_checked_at=stamp))
            doc = parse_sitemap(content)
            kind = doc.tag.rsplit('}', 1)[-1]
            if kind not in ('urlset', 'sitemapindex'):
                raise ValueError('Unknown sitemap format')
        except (OSError, ValueError, ParseError, CollectionBudgetExceeded) as error:
            status = getattr(error, 'code', None)
            if status == 304 and known and client.conditional_get_headers and cached.get('signature'):
                return completed(dict(cached, cache_hit=True, robots_checked_at=stamp))
            errors.append(f'{status or type(error).__name__}')
            if status in (401, 403, 429, 451):
                result['access_stop'] = status
                break
            continue
        if kind == 'urlset' and not list(locations(doc, 'url')) and 'sitemap' not in result:
            errors.append('Sitemap vuota')
            continue
        if 'sitemap' not in result:
            result.update(sitemap=raw, signature=signature, validators=validators,
                          lastmod=max((item.text.strip() for item in doc.iter()
                                       if item.tag.rsplit('}', 1)[-1] == 'lastmod' and item.text), default=None))
            # Fallback roots are for discovery of a sitemap, not for crawling every sitemap.
            # Once a root is found, only its children enter the remaining budget.
            pending.clear()
        if kind == 'sitemapindex':
            children_seen = True
            children = {url for url in locations(doc, 'sitemap') if url not in seen and scan.permitted(url)}
            pending = sorted(set(pending) | children, key=lambda url: (not JOB_MAP.search(urlsplit(url).path), url))
        else:
            urls = list(locations(doc, 'url'))
            count += len(urls)
            public = [url for url in urls if scan.scoped(url)]
            job_paths.extend(url for url in public if JOB_MAP.search(urlsplit(url).path))
            for url in public:
                if slug_candidate(url):
                    if scan.permitted(url):
                        candidates.add(url)
                    else:
                        denied_details += 1

    provider, confirmed = platform_signal(host, scan.rules, job_paths, result.get('platform'))
    if denied_details and not candidates and not pending and not errors:
        return completed(dict(result, robots_denied=True, reason='Robots vieta i dettagli candidati'))
    reason = ('Accesso interrotto · HTTP ' + str(result['access_stop']) if result.get('access_stop') else
              'Slug stage HR trovati' if candidates else
              'Slug ambigui · inventario sitemap parziale' if children_seen and (pending or errors) else
              'Nessuno slug stage HR nella sitemap letta' if count else
              'Sitemap assente, vuota o non leggibile')
    return completed(dict(result, platform=provider, platform_confirmed=confirmed,
                          children=len(pending) if children_seen else 0, candidates=len(candidates),
                          urls=count, sitemap_errors=errors, reason=reason))


def scan_hosts(hosts, exclusions, cached=None, checkpoint=None):
    cached = cached or {}
    results = {}
    with ThreadPoolExecutor(max_workers=16) as pool:
        futures = {pool.submit(probe, host, hints, exclusions, cached[host])
                   if host in cached else pool.submit(probe, host, hints, exclusions): host
                   for host, hints in hosts.items()}
        for future in as_completed(futures):
            results[futures[future]] = future.result()
            if checkpoint and len(results) % 8 == 0:
                write(checkpoint, results)
    return results


def current(job, stamp):
    return (job.get('internship_type') == 'internship' and job.get('student_eligibility') != 'excluded'
            and not job.get('ownership_risk')
            and any(code in COUNTRIES for code in job.get('countries', []))
            and verified_job(job, stamp))


def job_ids(catalog):
    return {job['id'] for job in catalog['jobs']}


def gate(observation, approved_elsewhere, terms_cleared, used, estimate, replay=None, *, migration=False):
    if not migration and not terms_cleared:
        return 'Termini da rivedere con il maintainer'
    if (not observation.get('robots') or observation.get('robots_denied') or observation.get('access_stop')
            or (not migration and not observation.get('sitemap'))):
        return 'Robots o sitemap non verificati'
    if not approved_elsewhere:
        return 'Manca un esito positivo su un altro sito della piattaforma'
    if used >= WEEKLY_LIMIT:
        return 'Raggiunto il tetto settimanale di 20'
    if estimate >= 35 * 60:
        return 'Stima della raccolta pari o superiore a 35 minuti'
    if replay and (replay['lost'] or replay['excluded'] or not replay['budget']):
        return 'Replay fallito per ID, titoli o budget'
    if replay and not migration and not replay['current']:
        return 'Nessuno stage europeo con prova current listing'
    return ''


class ReplayClient(BudgetClient):
    """Enforce exact-host robots for every adapter request during the replay."""

    def __init__(self, source):
        super().__init__(seconds=source['collection_seconds'], max_requests=min(source['max_requests'], PROBE_LIMIT),
                         delay=source['collection_delay'])
        self.host = host_of(source)
        self.scan = Scan(dict(source, access_review='allowed'), self)
        self.rules = None

    def request(self, url, method='GET', robots=True, timeout=12, attempts=1,
                accept=None, body=None, content_type=None):
        if method != 'GET' or body is not None or not self.scan.scoped(url):
            raise ValueError('Replay requires a same-host public GET')
        is_robots = url == f'https://{self.host}/robots.txt'
        if self.rules is None and not is_robots:
            self.request(f'https://{self.host}/robots.txt', robots=False)
        if not is_robots and not robots_allows(self.rules, url):
            raise ValueError('Replay route blocked by robots.txt')
        scope = getattr(self, 'redirect_scope_allowed', None)
        self.redirect_scope_allowed = lambda _: False
        try:
            response = super().request(url, method=method, robots=False, timeout=timeout,
                                       attempts=1, accept=accept)
        finally:
            self.redirect_scope_allowed = scope
        if is_robots:
            text = response[0].decode('utf-8-sig')
            if response[1] != 200 or re.search(r'<(?:html|!doctype|title|body)|captcha', text, re.I):
                raise ValueError('Unreadable robots.txt in replay')
            self.rules, _, delay = robots_policy(text)
            self.host_delays[self.host] = max(delay, self.host_delays.get(self.host, 0))
        return response

    def permitted(self, url):
        return self.rules is not None and self.scan.scoped(url) and robots_allows(self.rules, url)


def collect_replay(source, stamp):
    client = ReplayClient(source)
    started = time.monotonic()
    part = process_source(source, client, stamp)
    return part, client.remaining(), client.requests, client.bytes, round(time.monotonic() - started, 3)


def simulate(source, registry, catalog, stamp, parts, collected=None):
    part, remaining, requests, size, seconds = collected or collect_replay(source, stamp)
    report = part['report']
    registry = [item for item in registry if item['id'] != source['id']] + [source]
    with TemporaryDirectory() as output:
        result, _ = finalize(registry, [source], catalog, {}, [*parts, part], stamp, Path(output))
    staged_urls = {canonical_url(job['url']) for job in part['jobs'] if current(job, stamp)}
    excluded_reasons = ('student-eligibility-excluded', 'italian-student-eligibility-excluded',
                        'explicitly-enrolled-student-internship-required')
    gaps = Counter()
    reasons = report.get('candidate_filter_reasons', {})
    if reasons.get('not-hr-student-role'):
        gaps['Titolo non HR o stage non ammissibile'] += reasons['not-hr-student-role']
    if reasons.get('hr-candidate-without-country'):
        gaps['Paese europeo non dimostrato'] += reasons['hr-candidate-without-country']
    if report.get('page_errors') or report.get('sitemap_errors') or report.get('error'):
        gaps['Annuncio o inventario non leggibile nella verifica live'] += (
            len(report.get('page_errors', [])) + len(report.get('sitemap_errors', []))
            + bool(report.get('error')))
    for job in part['jobs']:
        if current(job, stamp):
            continue
        if not (job.get('published_at') or job.get('valid_through')):
            gaps['Data di pubblicazione o scadenza assente'] += 1
        else:
            reason = job.get('verification', {}).get('reason', 'Prova current listing incompleta')
            gaps[reason] += 1
    if not gaps and not staged_urls:
        gaps['Nessuna scheda HR europea da verificare nel budget'] += 1
    return part, dict(
        lost=sorted(job_ids(catalog) - job_ids(result)),
        excluded=any(report.get('candidate_filter_reasons', {}).get(reason) for reason in excluded_reasons)
        or any(excluded_placement_title(job['title']) or job.get('student_eligibility') == 'excluded'
                     or ('DE' in job['countries'] and excluded_german_title(job['title'])) for job in part['jobs']),
        budget=bool(remaining and report['status'] in ('ok', 'partial')
                    and not report.get('page_errors') and not report.get('sitemap_errors')),
        current=any(current(job, stamp) and job.get('last_verified_at') == stamp
                    and canonical_url(job['url']) in staged_urls for job in result['jobs']),
        requests=requests, bytes=size, seconds=seconds, gaps=dict(gaps),
    )


def migration_adapter(previous, observed):
    """Prepare a same-host adapter from an already established route layout."""
    name = observed.get('platform')
    sitemap = observed.get('sitemap')
    host = host_of(previous)
    if not observed.get('platform_confirmed') or not sitemap or host not in previous.get('allowed_hosts', []):
        return None
    fields = dict(
        id=previous['id'], employer=previous['employer'], career_url=previous['career_url'],
        allowed_hosts=[host], sitemaps=[sitemap], target_countries=previous.get('target_countries', []),
        max_requests=min(previous.get('max_requests', 12), 12),
        collection_seconds=previous.get('collection_seconds', 90), collection_delay=2,
        permission_basis=previous.get('permission_basis', 'Existing official route; robots checked live.'),
        discovery_platform=name, access_review='allowed',
        reviewed_on=(observed.get('robots_checked_at') or now())[:10],
        review_notes='Existing registered host migrated to its observed platform. Public exact-host routes and live robots only.',
    )
    if name == 'sf-rmk' and urlsplit(sitemap).path == '/sitemap.xml':
        return dict(fields, adapter='sf-rmk')
    patterns = {
        'radancy': r'/(?:[a-z-]+/)?job/[^/]+/[^/]+/\d+/\d+/?$',
        'phenom': r'/[a-z-]+/[a-z-]+/job/[^/]+/[^/]+/?$',
        'talentech': r'/jobs/[^/]+-\d+/?$',
    }
    if name in patterns:
        return dict(fields, adapter='employer-sitemap', job_url_pattern=patterns[name],
                    url_slug_prefilter=True)
    if name == 'teamtailor':
        return dict(fields, adapter='employer-sitemap', published_listing_platform='teamtailor',
                    job_url_pattern=rf'^https://{re.escape(host)}/jobs/\d+-[^/?]+/?$',
                    url_slug_prefilter=True)
    return None


def legacy_migration_source(source):
    return (source['adapter'] in ('universal-employer', 'employer-sitemap', 'employer-index')
            and not platform(source))


def stage(sources, catalog, state, stamp, baseline, observations=None, replay_cache=None):
    week = week_for(stamp)
    entries = state.get(week, {})
    rolled_back = {sid for records in state.values() for sid, item in records.items() if item.get('rollback')}
    held_companies = {company['id'] for company in read(ROOT / 'data/companies.json', [])
                      if company.get('collection_activation_hold')}
    registry = {source['id']: source for source in sources}
    hosts, exclusions = inventory(sources)
    # Production proof may have aged since publication. Evaluate it at the
    # catalog's observation time, while requiring fresh evidence in the replay.
    positive = {job['source_id'] for job in catalog['jobs']
                if current(job, catalog.get('last_attempt_at', stamp))}
    proof, production, active = defaultdict(set), set(), defaultdict(set)
    for source in sources:
        if source.get('enabled'):
            if platform(source):
                production.add((platform(source), source['adapter']))
            for host in {*source.get('allowed_hosts', []), host_of(source)}:
                active[host].add(source['id'])
            if source['id'] in positive:
                proof[platform(source)].add(host_of(source))
    estimate = baseline + sum(entry['after']['collection_seconds'] for entry in entries.values()
                              if not entry.get('rollback'))
    parallel_replays = observations is not None
    observations = scan_hosts(hosts, exclusions) if observations is None else observations
    replay_cache = {} if replay_cache is None else replay_cache
    reports, parts, pending = {}, [], []
    changed = False
    for host in sorted(hosts):
        observed = reports[host] = dict(observations.get(host, {'reason': 'Shard mancante'}))
        hints = hosts[host]
        prior = [registry[sid] for sid in sorted(hints['migration'])
                 if sid in registry and legacy_migration_source(registry[sid])]
        migration = bool(prior)
        if hints['migration'] and not migration and all(sid in registry for sid in hints['migration']):
            observed['reason'] = 'Migrazione già su adattatore dedicato'
            continue
        observed['migration_ids'] = sorted(hints['migration'])
        if not observed.get('robots') or observed.get('robots_denied') or observed.get('access_stop'):
            continue
        if not migration and not observed.get('candidates'):
            continue
        templates = [source for sid, source in hints['templates'].items()
                     if not registry.get(sid, {}).get('enabled')]
        if migration and len(prior) == 1 and not templates:
            generated = migration_adapter(prior[0], observed)
            if generated:
                templates = [generated]
        if len(templates) != 1 or len(prior) > 1:
            hint = observed.get('platform')
            if len(templates) > 1 or len(prior) > 1:
                observed['reason'] = 'Configurazione da rivedere · più fonti sullo stesso host'
            elif hint and hint not in {item[0] for item in production}:
                observed['reason'] = 'Piattaforma non in produzione · ' + hint
                observed['unsupported_platform'] = hint
            elif active[host] and not migration:
                observed['reason'] = 'Fonte già attiva'
            elif not migration:
                observed['reason'] = ('Termini da verificare' if hint else
                                      'Slug ambigui · piattaforma non identificata')
            else:
                observed['reason'] = 'Configurazione da rivedere · formato dell’adattatore non attestato'
            continue
        template = templates[0]
        sid = prior[0]['id'] if migration else template['id']
        previous = registry.get(sid)
        if active[host] - {sid} or sid in entries or sid in rolled_back or (
                previous and previous.get('status') == 'discovery-rollback-hold'):
            observed['reason'] = 'Host già coperto o rientrato in hold'
            continue
        if (set(template['allowed_hosts']) != {host} or template.get('slow_collection_lane')
                or not all(isinstance(template.get(key), (int, float)) and template[key] > 0
                           for key in ('collection_delay', 'collection_seconds', 'max_requests'))):
            observed['reason'] = 'Configurazione da rivedere · budget o perimetro dell’adattatore'
            continue
        source = dict(template, id=sid, enabled=True, collection_activation_hold=False,
                      status='reviewed-active')
        if migration:
            if prior[0].get('company_id'):
                source['company_id'] = prior[0]['company_id']
            source['source_id_aliases'] = sorted({sid, template['id'], *prior[0].get('source_id_aliases', [])})
            # A disabled generic source stays disabled after changing its adapter.
            if not previous.get('enabled'):
                source.update(enabled=False, collection_activation_hold=True, status='reviewed-disabled')
        elif source.get('company_id') in held_companies:
            observed['reason'] = 'Datore in hold nel registro aziende'
            continue
        adapter_platform = platform(template)
        observed['platform'] = adapter_platform
        replay_key = (fingerprint([observed['signature'], {key: value for key, value in source.items()
                                                        if key != 'reviewed_on'}])
                      if observed.get('signature') and not observed.get('children') else None)
        has_proof = (adapter_platform, source['adapter']) in production
        if not migration:
            has_proof = bool(adapter_platform and proof[adapter_platform] - {host, None})
        reason = gate(observed, has_proof, True, len(entries), estimate + source['collection_seconds'],
                      migration=migration)
        if not has_proof and adapter_platform:
            observed['reason'] = 'Piattaforma senza prova richiesta · ' + adapter_platform
            if (adapter_platform, source['adapter']) not in production:
                observed['unsupported_platform'] = adapter_platform
            continue
        if reason:
            observed['reason'] = reason
        elif replay_key and replay_cache.get(host, {}).get('key') == replay_key:
            observed.update(reason=replay_cache[host]['reason'], replay_cache_hit=True,
                            replay=replay_cache[host]['replay'])
        else:
            pending.append((host, observed, source, previous, bool(prior), replay_key))

    # Fetch independent hosts concurrently. The finalizer and weekly limits
    # still run in a single deterministic order over all accepted parts.
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {host: pool.submit(collect_replay, dict(source, enabled=True, collection_activation_hold=False), stamp)
                   for host, _, source, _, _, _ in pending} if parallel_replays else {}
        for host, observed, source, previous, migration, replay_key in pending:
            next_estimate = estimate + source['collection_seconds']
            params = (observed, True, True, len(entries), next_estimate)
            reason = gate(*params, migration=migration)
            if not reason:
                try:
                    replay_args = (futures[host].result(),) if host in futures else ()
                    part, replay = simulate(source, list(registry.values()), catalog, stamp, parts, *replay_args)
                except (OSError, ValueError, CollectionBudgetExceeded):
                    observed['reason'] = 'Replay del catalogo fallito'
                    continue
                observed['replay'] = replay
                reason = gate(*params, replay, migration=migration)
                if replay_key and reason and replay['budget'] and not replay['lost']:
                    replay_cache[host] = dict(key=replay_key, reason=reason, replay=replay)
            if reason:
                observed['reason'] = reason
                continue
            sid = source['id']
            entries[sid] = dict(before=previous, after=source, host=host, at=stamp, migration=migration)
            registry[sid] = source
            parts.append(part)
            estimate = next_estimate
            replay_cache.pop(host, None)
            observed.update(reason='Migrata' if migration else 'Attivata', source_id=sid, migration=migration)
            changed = True
    if changed:
        state[week] = entries
    return list(registry.values()), reports, changed


def rollback(sources, entries, reason, run_id):
    """Restore the generic crawler or put the reviewed source back on hold."""
    registry = {source['id']: source for source in sources}
    changed = False
    for sid, entry in entries.items():
        if entry.get('rollback') or registry.get(sid) != entry['after']:
            continue
        previous = entry['before']
        if previous is not None:
            registry[sid] = previous
        else:
            registry[sid] = dict(previous or entry['after'], enabled=False,
                                 collection_activation_hold=True, status='discovery-rollback-hold')
        entry['rollback'] = {'reason': reason, 'run_id': run_id}
        changed = True
    return list(registry.values()), changed


def collection_result(duration, timeout, before, after):
    lost = sorted(job_ids(before) - job_ids(after)) if after else []
    if timeout or duration > 45 * 60 or lost:
        return f'Rientro: {duration} s, timeout={timeout}, ID persi={len(lost)}'
    return ''


def audit(sources, state, event, baseline, run_sources, published, stamp):
    run_id = event['id']
    duration = round((datetime.fromisoformat(event['updated_at'])
                      - datetime.fromisoformat(event['run_started_at'])).total_seconds())
    jobs = event['jobs']
    timeout = event['conclusion'] == 'timed_out' or any(
        job['conclusion'] == 'timed_out' or (
            job['conclusion'] == 'cancelled' and job.get('started_at') and job.get('completed_at')
            and (datetime.fromisoformat(job['completed_at'])
                 - datetime.fromisoformat(job['started_at'])).total_seconds() >= 45 * 60)
        for job in jobs)
    snapshot = {source['id']: source for source in run_sources}
    reason = collection_result(duration, timeout, baseline, published)
    reports, changed = {}, False
    collection_week = week_for(event['run_started_at'])
    review_weeks = {**state, collection_week: state.get(collection_week, {})}
    for week, entries in review_weeks.items():
        ran = {sid for sid, entry in entries.items() if not entry.get('rollback') and entry['after'].get('enabled')
               and snapshot.get(sid) == entry['after']
               and (not entry.get('verified_run') or (reason and week == collection_week))}
        if not ran and (week != collection_week or entries):
            continue
        if reason and ran:
            sources, reverted = rollback(sources, entries, reason, run_id)
            changed |= reverted
        successful = event['conclusion'] == 'success' and bool(published)
        if successful and not reason:
            for sid in ran:
                entries[sid]['verified_run'] = run_id
                changed = True
        before_ids = job_ids(baseline)
        previous_stamp = baseline.get('last_attempt_at', stamp)
        previous_current = {job['id'] for job in baseline['jobs'] if current(job, previous_stamp)}
        by_country = Counter(code for job in (published or {}).get('jobs', [])
                             if successful and job['id'] not in previous_current
                             and job['source_id'] in ran and current(job, stamp)
                             for code in job['countries'])
        reports[week] = dict(run_id=run_id, duration=duration, timeout=timeout,
                             lost=len(before_ids - job_ids(published)) if published else None,
                             added=dict(by_country), successful=successful, reason=reason,
                             reviewed=sorted(ran))
    return sources, reports, changed


def report_text(entries, observations, audit_report):
    lines = ['### Fonti attivate automaticamente']
    lines += [f"- `{sid}` ({entry['host']})"
              + (' · migrata' if entry.get('migration') else '')
              + (f" — {entry['rollback']['reason']}" if entry.get('rollback') else '')
              for sid, entry in sorted(entries.items())] or ['Nessuna.']
    if observations is not None:
        lines += ['', '### Fonti in attesa di decisione']
        groups = defaultdict(list)
        for host, row in sorted(observations.items()):
            if row['reason'] not in ('Attivata', 'Migrata', 'Migrazione già su adattatore dedicato', 'Fonte già attiva', 'Nessuno slug stage HR nella sitemap letta'):
                count = f" ({row['candidates']})" if row.get('candidates') else ''
                groups[row['reason']].append(host + count)
        for reason, hosts in sorted(groups.items()):
            lines.append(f'- **{reason}** ({len(hosts)}): ' + ', '.join(hosts))
        if not groups:
            lines.append('Nessuna.')
    if audit_report is not None:
        row = audit_report
        lines += ['', '### Stage aggiunti per paese',
                  ', '.join(f'{code} {count}' for code, count in sorted(row['added'].items()))
                  or ('Nessuna aggiunta' if row['successful'] else 'Pubblicazione da confermare'),
                  f"Raccolta: {row['duration']} s; ID persi: "
                  + ('non verificabili' if row['lost'] is None else str(row['lost'])),
                  f"Run: https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/{row['run_id']}"]
        if row['reason']:
            lines.append(row['reason'])
    return '\n'.join(lines)


def funnel_bucket(row):
    reason = row['reason']
    replay = row.get('replay')
    if reason in ('Attivata', 'Migrata', 'Migrazione già su adattatore dedicato'):
        return reason
    if row.get('robots_denied'):
        return 'Robots vieta i percorsi'
    if row.get('robots_attempts'):
        return reason
    if reason == 'Host escluso o non valido':
        return 'Esclusione registrata o host non valido'
    if reason == 'Shard mancante':
        return reason
    if not row.get('robots') or reason == 'Sitemap non consentita':
        return 'Robots non letto o percorso negato'
    if not row.get('sitemap') or row.get('urls') == row.get('children') == 0:
        return 'Sitemap assente, vuota o non leggibile'
    if reason == 'Nessuno slug stage HR nella sitemap letta':
        return 'Zero slug candidati'
    if replay:
        failed = [label for label, failed in (('ID persi', replay['lost']),
                  ('titoli esclusi', replay['excluded']), ('budget o lettura incompleta', not replay['budget']),
                  ('livello di prova', not replay['current'])) if failed]
        if failed:
            return 'Replay fallito · ' + ', '.join(failed)
    return reason


def funnel(sources, observations):
    hosts, _ = inventory(sources)
    totals = Counter(funnel_bucket(row) for row in observations.values())
    by_id = {source['id']: source for source in sources}
    migrations = Counter()
    for host, hints in hosts.items():
        for sid in hints['migration']:
            if sid in by_id and not legacy_migration_source(by_id[sid]):
                migrations['Migrazione già su adattatore dedicato'] += 1
            else:
                migrations[funnel_bucket(observations[host])] += 1
    lines = ['### Imbuto', '| Passaggio | Host | Fonti di migrazione |', '| --- | ---: | ---: |']
    for key in sorted(totals.keys() | migrations.keys()):
        lines.append(f'| {key} | {totals[key]} | {migrations[key]} |')
    lines.append(f'| Totale | {sum(totals.values())} | {sum(migrations.values())} |')
    unsupported = Counter(row['unsupported_platform'] for row in observations.values()
                          if row.get('unsupported_platform') and row.get('candidates'))
    lines += ['', '### Piattaforme non supportate con candidati']
    lines += [f'- {name} · {count} host' for name, count in unsupported.most_common(10)] or ['Nessuna osservata.']
    failures = [(host, row['replay'].get('gaps', {})) for host, row in sorted(observations.items())
                if row.get('replay') and row['reason'] not in ('Attivata', 'Migrata')]
    if failures:
        lines += ['', '### Passaggi mancanti nel replay']
        for host, gaps in failures:
            lines.append(f"- {host} · " + (', '.join(f'{gap} ({count})' for gap, count in gaps.items())
                                           or 'Controllo del replay incompleto'))
    lines.append(f"Cache sitemap: {sum(bool(row.get('cache_hit')) for row in observations.values())} host. "
                 f"Cache replay: {sum(bool(row.get('replay_cache_hit')) for row in observations.values())} host.")
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline-seconds', type=int)
    parser.add_argument('--scan-shard', type=int, choices=range(SHARDS))
    parser.add_argument('--scans', type=Path)
    parser.add_argument('--cache', type=Path)
    parser.add_argument('--audit-event', type=Path)
    parser.add_argument('--run-sources', type=Path)
    parser.add_argument('--before', type=Path)
    parser.add_argument('--after', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    sources, state = read(SOURCES, []), read(STATE, {})
    stamp = now()
    cache = read(args.cache, {}) if args.cache else {}
    if args.scan_shard is not None:
        hosts, exclusions = inventory(sources)
        shard = {host: hints for host, hints in hosts.items() if membership(host) == args.scan_shard}
        observations = scan_hosts(shard, exclusions, cache, args.output)
        write(args.output, observations)
        if args.cache:
            cache.update({host: row for host, row in observations.items()
                          if row.get('robots') or row.get('robots_attempts')})
            write(args.cache, cache)
        return
    if args.audit_event:
        event = read(args.audit_event, {})
        sources, audits, changed = audit(sources, state, event, read(args.before, {}),
                                         read(args.run_sources, []), read(args.after, None),
                                         event['updated_at'])
        reports = {week: dict(activation=report_text(state.get(week, {}), None, None),
                              collection=report_text({}, None, row).split('### Stage aggiunti per paese', 1)[1],
                              ran=bool(row['reviewed']))
                   for week, row in audits.items()}
    else:
        if args.baseline_seconds is None or args.baseline_seconds < 0:
            parser.error('A recent collection duration is required')
        scans = None
        if args.scans:
            scans = {}
            for file in sorted(args.scans.glob('scan-*.json')):
                scans.update(read(file, {}))
        original = sources
        if scans is not None:
            expected, _ = inventory(sources)
            scans = {host: scans.get(host, {'reason': 'Shard mancante'}) for host in expected}
            write(args.output, {week_for(stamp): dict(funnel=funnel(sources, scans),
                  hold='\nReplay in corso o interrotto. Consultare gli artefatti per shard.')})
        sources, observations, changed = stage(sources, read(ROOT / 'data/catalog.json', {}),
                                               state, stamp, args.baseline_seconds, scans, cache)
        if args.cache:
            write(args.cache, cache)
        week = week_for(stamp)
        reports = {week: dict(activation=report_text(state.get(week, {}), None, None),
                              funnel=funnel(original, observations),
                              hold=report_text({}, observations, None).split('### Fonti in attesa di decisione', 1)[1])}
        write(args.output.parent / 'observations.json', observations)
    if changed:
        write(SOURCES, sources)
        write(STATE, state)
    write(args.output, reports)


if __name__ == '__main__':
    main()
