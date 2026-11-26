"""Discover recruiting sitemaps and activate sources backed by a live replay."""

import argparse
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
import csv
from datetime import datetime
from pathlib import Path
import re
from tempfile import TemporaryDirectory
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
EXCLUDED = {
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
    adapter = source['adapter']
    if adapter == 'sf-rmk':
        return adapter
    if adapter == 'sitemap-jobposting':
        if source.get('reviewed_listing_layout') == 'bosch':
            return 'bosch'
        return 'radancy' if 'radancy' in source.get('permission_basis', '').lower() else adapter
    if adapter == 'employer-sitemap':
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


def probe(host, hints, exclusions):
    if not re.fullmatch(r'[a-z0-9-]+(?:\.[a-z0-9-]+)+', host) or any(
            host == domain or host.endswith('.' + domain) for domain in exclusions):
        return {'reason': 'Host escluso o non valido', 'requests': 0}
    client = BudgetClient(seconds=30, max_requests=2, delay=2)
    scan = Scan(dict(career_url=f'https://{host}/', allowed_hosts=[host],
                     adapter='sitemap-jobposting', access_review='allowed'), client)
    result = {'platform': hints.get('platform_hint')}
    try:
        ready = [url for url in scan.preflight() if scan.permitted(url)]
        result['robots'] = True
        if not ready:
            result['reason'] = 'Sitemap non consentita'
        else:
            url = min(ready, key=lambda item: (item not in hints['maps'], not JOB_MAP.search(item), item))
            doc = parse_sitemap(scan.get(url))
            kind = doc.tag.rsplit('}', 1)[-1]
            if kind not in ('urlset', 'sitemapindex'):
                raise ValueError('Unknown sitemap format')
            children = {item for item in locations(doc, 'sitemap') if scan.permitted(item)}
            slugs = {item for item in locations(doc, 'url') if scan.permitted(item) and slug_candidate(item)}
            result.update(sitemap=url, children=len(children), candidates=len(slugs))
            result['reason'] = ('Indice con sitemap figlie' if children else
                                'Slug stage HR trovati' if slugs else 'Nessuno slug stage HR nella sitemap letta')
    except (OSError, ValueError, ParseError, CollectionBudgetExceeded) as error:
        result['reason'] = f'Preflight incompleto ({type(error).__name__})'
    return dict(result, requests=client.requests)


def current(job, stamp):
    return (job.get('internship_type') == 'internship' and job.get('student_eligibility') != 'excluded'
            and not job.get('ownership_risk')
            and any(code in COUNTRIES for code in job.get('countries', []))
            and verified_job(job, stamp))


def job_ids(catalog):
    return {job['id'] for job in catalog['jobs']}


def gate(observation, approved_elsewhere, terms_cleared, used, estimate, replay=None):
    if not terms_cleared:
        return 'Termini da rivedere con il maintainer'
    if not observation.get('robots') or not observation.get('sitemap'):
        return 'Robots o sitemap non verificati'
    if not approved_elsewhere:
        return 'Manca un esito positivo su un altro sito della piattaforma'
    if used >= WEEKLY_LIMIT:
        return 'Raggiunto il tetto settimanale di 20'
    if estimate >= 35 * 60:
        return 'Stima della raccolta pari o superiore a 35 minuti'
    if replay and (replay['lost'] or replay['excluded'] or not replay['budget']):
        return 'Replay fallito per ID, titoli o budget'
    if replay and not replay['current']:
        return 'Nessuno stage europeo con prova current listing'
    return ''


class ReplayClient(BudgetClient):
    """Enforce exact-host robots for every adapter request during the replay."""

    def __init__(self, source):
        super().__init__(seconds=source['collection_seconds'], max_requests=source['max_requests'],
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


def simulate(source, registry, catalog, stamp, parts):
    client = ReplayClient(source)
    part = process_source(source, client, stamp)
    report = part['report']
    registry = [item for item in registry if item['id'] != source['id']] + [source]
    with TemporaryDirectory() as output:
        result, _ = finalize(registry, [source], catalog, {}, [*parts, part], stamp, Path(output))
    staged_urls = {canonical_url(job['url']) for job in part['jobs'] if current(job, stamp)}
    excluded_reasons = ('student-eligibility-excluded', 'italian-student-eligibility-excluded',
                        'explicitly-enrolled-student-internship-required')
    return part, dict(
        lost=sorted(job_ids(catalog) - job_ids(result)),
        excluded=any(report.get('candidate_filter_reasons', {}).get(reason) for reason in excluded_reasons)
        or any(excluded_placement_title(job['title']) or job.get('student_eligibility') == 'excluded'
                     or ('DE' in job['countries'] and excluded_german_title(job['title'])) for job in part['jobs']),
        budget=bool(client.remaining() and report['status'] in ('ok', 'partial')
                    and not report.get('page_errors') and not report.get('sitemap_errors')),
        current=any(current(job, stamp) and job.get('last_verified_at') == stamp
                    and canonical_url(job['url']) in staged_urls for job in result['jobs']),
        requests=client.requests, bytes=client.bytes,
    )


def stage(sources, catalog, state, stamp, baseline):
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
    proof, active = defaultdict(set), defaultdict(set)
    for source in sources:
        if source.get('enabled'):
            for host in {*source.get('allowed_hosts', []), host_of(source)}:
                active[host].add(source['id'])
            if source['id'] in positive:
                proof[platform(source)].add(host_of(source))
    estimate = baseline + sum(entry['after']['collection_seconds'] for entry in entries.values()
                              if not entry.get('rollback'))
    reports, parts = {}, []
    changed = False
    with ThreadPoolExecutor(max_workers=24) as pool:
        futures = {host: pool.submit(probe, host, hints, exclusions) for host, hints in hosts.items()}
        for host in sorted(hosts):
            observed = reports[host] = futures[host].result()
            if not (observed.get('candidates') or observed.get('children')):
                continue
            hints = hosts[host]
            prior = [registry[sid] for sid in hints['migration']
                     if sid in registry and registry[sid]['adapter'] == 'universal-employer']
            templates = [source for sid, source in hints['templates'].items()
                         if not registry.get(sid, {}).get('enabled')]
            if len(templates) != 1 or len(prior) > 1:
                observed['reason'] = ('Fonte già attiva' if active[host] and not prior
                                      else 'Termini, piattaforma o configurazione da rivedere')
                continue
            template = templates[0]
            sid = prior[0]['id'] if prior else template['id']
            previous = registry.get(sid)
            if active[host] - {sid} or sid in entries or sid in rolled_back or (
                    previous and previous.get('status') == 'discovery-rollback-hold'):
                observed['reason'] = 'Host già coperto o rientrato in hold'
                continue
            if (set(template['allowed_hosts']) != {host} or template.get('slow_collection_lane')
                    or not all(isinstance(template.get(key), (int, float)) and template[key] > 0
                               for key in ('collection_delay', 'collection_seconds', 'max_requests'))):
                observed['reason'] = 'Budget o perimetro dell’adattatore da rivedere'
                continue
            source = dict(template, id=sid, enabled=True, collection_activation_hold=False,
                          status='reviewed-active')
            if prior:
                source['company_id'] = prior[0]['company_id']
                source['source_id_aliases'] = sorted({sid, template['id']})
            # Keep the previous source ID and every company reference in place.
            if source.get('company_id') in held_companies:
                observed['reason'] = 'Datore in hold nel registro aziende'
                continue
            adapter_platform = platform(template)
            observed['platform'] = adapter_platform
            next_estimate = estimate + source['collection_seconds']
            params = (observed, bool(adapter_platform and proof[adapter_platform] - {host, None}),
                      True, len(entries), next_estimate)
            reason = gate(*params)
            if not reason:
                try:
                    part, replay = simulate(source, list(registry.values()), catalog, stamp, parts)
                except (OSError, ValueError, CollectionBudgetExceeded):
                    observed['reason'] = 'Replay del catalogo fallito'
                    continue
                observed['replay'] = replay
                reason = gate(*params, replay)
            if reason:
                observed['reason'] = reason
                continue
            entries[sid] = dict(before=previous, after=source, host=host, at=stamp)
            registry[sid] = source
            parts.append(part)
            estimate = next_estimate
            observed['reason'] = 'Attivata'
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
        if previous and previous['enabled']:
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
        ran = {sid for sid, entry in entries.items() if not entry.get('rollback')
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
        by_country = Counter(code for job in (published or {}).get('jobs', [])
                             if successful and job['id'] not in before_ids
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
              + (f" — {entry['rollback']['reason']}" if entry.get('rollback') else '')
              for sid, entry in sorted(entries.items())] or ['Nessuna.']
    if observations is not None:
        lines += ['', '### Fonti in attesa di decisione']
        groups = defaultdict(list)
        for host, row in sorted(observations.items()):
            if row['reason'] not in ('Attivata', 'Fonte già attiva', 'Nessuno slug stage HR nella sitemap letta'):
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline-seconds', type=int)
    parser.add_argument('--audit-event', type=Path)
    parser.add_argument('--run-sources', type=Path)
    parser.add_argument('--before', type=Path)
    parser.add_argument('--after', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    sources, state = read(SOURCES, []), read(STATE, {})
    stamp = now()
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
        sources, observations, changed = stage(sources, read(ROOT / 'data/catalog.json', {}),
                                               state, stamp, args.baseline_seconds)
        week = week_for(stamp)
        reports = {week: dict(activation=report_text(state.get(week, {}), None, None),
                              hold=report_text({}, observations, None).split('### Fonti in attesa di decisione', 1)[1])}
        write(args.output.parent / 'observations.json', observations)
    if changed:
        write(SOURCES, sources)
        write(STATE, state)
    write(args.output, reports)


if __name__ == '__main__':
    main()
