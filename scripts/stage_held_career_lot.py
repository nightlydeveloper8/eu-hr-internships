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
from collector.pipeline import ROOT, finalize, now, process_source
from collector.runtime import BudgetClient
from collector.verification import verified_job

MANIFEST = ROOT / 'docs/staging/held-career-lots-20261124.json'
GOLD = ROOT / 'docs/recall-gold-set-2026-11.csv'


def collect(source, stamp):
    client = BudgetClient(seconds=source['collection_seconds'], max_requests=source['max_requests'],
                          delay=source['collection_delay'])
    start = time.monotonic()
    part = process_source(source, client, stamp, staging=True)
    part['report'].update(requests=client.requests, bytes_read=client.bytes,
                          duration_seconds=round(time.monotonic() - start, 2))
    return part


def openings(jobs, stamp):
    return [job for job in jobs if job['internship_type'] == 'internship'
            and job.get('student_eligibility') != 'excluded' and verified_job(job, stamp)]


def summarise(registry, sources, parts, baseline, stamp, output):
    base, _ = finalize(registry, [], baseline, {}, [], stamp, output / 'control')
    candidate, _ = finalize(registry + sources, sources, baseline, {}, parts, stamp, output / 'candidate')
    before, after = openings(base['jobs'], stamp), openings(candidate['jobs'], stamp)
    lost = sorted({job['id'] for job in baseline['jobs']} - {job['id'] for job in candidate['jobs']})
    before_count = Counter(code for job in before for code in job['countries'])
    after_count = Counter(code for job in after for code in job['countries'])
    with GOLD.open() as handle:
        gold = list(csv.DictReader(handle))
    def hits(jobs):
        keys = {(code, canonical_url(job['url'])) for job in jobs for code in job['countries']}
        return Counter(row['paese'] for row in gold if (row['paese'], canonical_url(row['url'])) in keys)
    denominators = Counter(row['paese'] for row in gold)
    old_hits, new_hits = hits(before), hits(after)
    return dict(ids_lost=lost, compared_at=stamp,
                benchmark_url_recall={code: [old_hits[code], new_hits[code], n]
                                      for code, n in denominators.items()},
                by_country={code: [before_count[code], after_count[code]] for code in COUNTRIES},
                requests=sum(part['report']['requests'] for part in parts),
                reports=[part['report'] for part in parts])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('lot', choices=['CORPORATE-SITEMAP', 'WORKDAY'])
    parser.add_argument('--source', nargs='+', default=[])
    parser.add_argument('--workday-public-sitemap', action='store_true',
                        help='Staging only: apply the Nov 23 Workday review to robots-advertised sitemap routes')
    args = parser.parse_args()
    data = ROOT / 'data'
    registry = json.loads((data / 'sources.json').read_text())
    baseline = json.loads((data / 'catalog.json').read_text())
    lot = json.loads(MANIFEST.read_text())[args.lot]
    sources = [row['source'] for row in lot['sources'] if 'source' in row and row['source']['id'] in args.source]
    if set(args.source) != {source['id'] for source in sources}:
        parser.error('Unknown staging source ID')
    for source in sources:
        if source['enabled'] or not source['collection_activation_hold']:
            parser.error('Staging accepts held sources only')
        if args.workday_public_sitemap and source['adapter'] == 'workday':
            source.update(access_review='allowed', permission_basis='Workday review, 23 Nov 2026; robots-declared sitemap and public detail')
        if source.get('access_review') != 'allowed':
            parser.error('Missing route-level access evidence')
    stamp = now() if sources else baseline['last_attempt_at']
    with ThreadPoolExecutor(max_workers=4) as pool:
        parts = list(pool.map(lambda source: collect(source, stamp), sources))
    output = Path(tempfile.mkdtemp(prefix='held-career-staging-'))
    result = summarise(registry, sources, parts, baseline, stamp, output)
    (output / 'report.json').write_text(json.dumps(result, indent=2, ensure_ascii=False))
    print(output / 'report.json')
    if result['ids_lost']:
        raise SystemExit('Catalog ID regression')


if __name__ == '__main__':
    main()
