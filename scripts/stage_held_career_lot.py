"""Replay held recruiting sources into an isolated staging catalog."""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import csv
import json
from pathlib import Path
import tempfile
import time

from collector.classify import COUNTRIES, canonical_url
from collector.daily import shard_for, split_collection_sources
from collector.pipeline import ROOT, finalize, now, process_source
from collector.runtime import BudgetClient
from collector.sitemap_jobposting import MAX_REQUESTS
from collector.verification import verified_job

MANIFEST = ROOT / 'docs/staging/held-career-lots-20261124.json'
GOLD = ROOT / 'docs/recall-gold-set-2026-11.csv'


def collect(source, stamp, *, active=False):
    client = BudgetClient(seconds=source['collection_seconds'], max_requests=source['max_requests'],
                          delay=source['collection_delay'])
    start = time.monotonic()
    part = process_source(source, client, stamp, staging=not active)
    part['report'].update(requests=client.requests, bytes_read=client.bytes,
                          duration_seconds=round(time.monotonic() - start, 2),
                          http_observations=getattr(client, 'sitemap_jobposting_observations', []),
                          retry_outcomes=dict(client.retry_outcomes))
    return part


def openings(jobs, stamp):
    return [job for job in jobs if job['internship_type'] == 'internship'
            and job.get('student_eligibility') != 'excluded'
            and job.get('ownership_risk', {}).get('state') != 'historical-unreviewed-external-host'
            and verified_job(dict(job, link_status='verified'), stamp)]


def summarise(registry, sources, parts, baseline, stamp, output):
    base, _ = finalize(registry, [], baseline, {}, [], stamp, output / 'control')
    candidate, _ = finalize(registry + sources, sources, baseline, {}, parts, stamp, output / 'candidate')
    before, after = openings(base['jobs'], stamp), openings(candidate['jobs'], stamp)
    lost = sorted({job['id'] for job in baseline['jobs']} - {job['id'] for job in candidate['jobs']})
    baseline_ids = {job['id'] for job in baseline['jobs']}
    before_ids = {job['id'] for job in before}
    new_ids = sorted({job['id'] for job in candidate['jobs']} - baseline_ids)
    upgrades = [job for job in after if job['id'] in baseline_ids - before_ids
                and job.get('verification', {}).get('reason') == 'official-sitemap-live-jobposting']
    before_count = Counter(code for job in before for code in job['countries'])
    after_count = Counter(code for job in after for code in job['countries'])
    with GOLD.open() as handle:
        gold = list(csv.DictReader(handle))
    def hits(jobs):
        keys = {(code, canonical_url(job['url'])) for job in jobs for code in job['countries']}
        return Counter(row['paese'] for row in gold if (row['paese'], canonical_url(row['url'])) in keys)
    denominators = Counter(row['paese'] for row in gold)
    old_hits, new_hits = hits(before), hits(after)
    return dict(ids_lost=lost, new_ids=new_ids, upgraded_ids=[job['id'] for job in upgrades],
                opened=[dict(id=job['id'], title=job['title'], countries=job['countries'],
                             internship_type=job['internship_type'], student_eligibility=job.get('student_eligibility'))
                        for job in after if job['id'] not in before_ids],
                totals=[len(before),len(after)], compared_at=stamp,
                benchmark_url_recall={code: [old_hits[code], new_hits[code], n]
                                      for code, n in denominators.items()},
                by_country={code: [before_count[code], after_count[code]] for code in COUNTRIES},
                requests=sum(part['report']['requests'] for part in parts),
                reports=[part['report'] for part in parts])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('lot', choices=['CORPORATE-SITEMAP', 'WORKDAY'])
    parser.add_argument('--manifest', type=Path, default=MANIFEST)
    parser.add_argument('--simulate-active', action='store_true')
    parser.add_argument('--baseline-dir', type=Path, default=ROOT / 'data')
    parser.add_argument('--source', nargs='+', default=[])
    parser.add_argument('--workday-public-sitemap', action='store_true',
                        help='Staging only: apply the Nov 23 Workday review to robots-advertised sitemap routes')
    args = parser.parse_args()
    data = args.baseline_dir
    registry = json.loads((data / 'sources.json').read_text())
    baseline = json.loads((data / 'catalog.json').read_text())
    lot = json.loads(args.manifest.read_text())[args.lot]
    sources = [row['source'] for row in lot['sources'] if 'source' in row and
               (row['source']['id'] in args.source or (args.simulate_active and not args.source))]
    blocked = []
    if args.source and set(args.source) != {source['id'] for source in sources}:
        parser.error('Unknown staging source ID')
    for source in sources:
        if source['enabled'] or not source['collection_activation_hold']:
            parser.error('Staging accepts held sources only')
        if args.workday_public_sitemap and source['adapter'] == 'workday':
            source.update(access_review='allowed', permission_basis='Workday review, 23 Nov 2026; robots-declared sitemap and public detail')
        if not args.simulate_active:
            source.update(max_requests=MAX_REQUESTS, collection_seconds=source.get('staging_collection_seconds', 720))
        if source.get('access_review') != 'allowed':
            if not args.simulate_active:
                parser.error('Missing route-level access evidence')
            blocked.append(source['id'])
        if args.simulate_active:
            source.update(enabled=True, collection_activation_hold=False)
    sources = [source for source in sources if source['id'] not in blocked]
    stamp = now() if sources else baseline['last_attempt_at']
    regular, slow = split_collection_sources(sources) if args.simulate_active else (sources, [])
    with ThreadPoolExecutor(max_workers=6) as pool:
        slow_run = pool.submit(lambda: [collect(source, stamp, active=True) for source in slow])
        parts = list(pool.map(lambda source: collect(source, stamp, active=args.simulate_active), regular))
        parts.extend(slow_run.result())
    output = Path(tempfile.mkdtemp(prefix='held-career-staging-'))
    result = summarise(registry, sources, parts, baseline, stamp, output)
    regular_ids = {source['id'] for source in regular}
    per_shard = Counter()
    for part in parts:
        report = part['report']
        if report['id'] in regular_ids:
            per_shard[shard_for(report['id'], 16)] += report['duration_seconds']
    result['active_simulation'] = args.simulate_active
    result['sources_without_access_review'] = blocked
    result['regular_serial_seconds_by_shard'] = dict(per_shard)
    result['slow_lane_seconds'] = sum(part['report']['duration_seconds'] for part in parts
                                      if part['report']['id'] not in regular_ids)
    result['snapshot_clock'] = baseline['last_attempt_at']
    result['snapshot_by_country'] = dict(Counter(code for job in openings(baseline['jobs'], result['snapshot_clock'])
                                                  for code in job['countries']))
    (output / 'parts.json').write_text(json.dumps(parts, ensure_ascii=False))
    (output / 'report.json').write_text(json.dumps(result, indent=2, ensure_ascii=False))
    print(output / 'report.json')
    if result['ids_lost']:
        raise SystemExit('Catalog ID regression')


if __name__ == '__main__':
    main()
