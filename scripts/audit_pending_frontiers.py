"""Audit restored universal-crawler frontiers WITHOUT network or source changes.

The daily collector stores <= 2000 URLs per source. The coverage report counts
remaining URLs before truncation; these numbers must never be treated as the
same denominator. Candidate removals here are SHADOW only: duplicate URL
entries and already-rejected vendor static assets. No vacancies are classified
as absent and no real frontier is rewritten.
"""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

from collector.daily import shard_for
from collector.universal import provider_resource

NONJOB_NAVIGATION = re.compile(
    r'/(?:privacy(?:-policy)?|cookie(?:s|-policy)?|datenschutz|'
    r'impressum|terms(?:-and-conditions)?|login|register|'
    r'newsletter|job-alert)(?:/|$)', re.I
)


def source_cache_path(cache_root, source_id):
    return cache_root / hashlib.sha256(source_id.encode()).hexdigest()[:24] / 'frontier.json'


def analyze_pending(pending):
    """Count only *certain* duplicate URLs/resources; other paths need review."""
    if not isinstance(pending, list):
        raise ValueError('Malformed frontier pending list')
    seen = set()
    exact_duplicate_entries = 0
    invalid_url_entries = 0
    vendor_resource_entries = 0
    review_navigation_entries = 0
    job_flagged = 0
    unique_clean = set()
    for row in pending:
        if not isinstance(row, dict):
            invalid_url_entries += 1
            continue
        url = row.get('url')
        parsed = urlsplit(url) if isinstance(url, str) else None
        if not parsed or parsed.scheme not in ('https', 'http') or not parsed.hostname:
            invalid_url_entries += 1
            continue
        if url in seen:
            exact_duplicate_entries += 1
            continue
        seen.add(url)
        if provider_resource(url):
            vendor_resource_entries += 1
            continue
        unique_clean.add(url)
        if row.get('job') is True:
            job_flagged += 1
        if NONJOB_NAVIGATION.search(parsed.path) and row.get('job') is not True:
            # Review only: do not remove until the employer-specific landing
            # page and any HR examples prove these can never be job entries.
            review_navigation_entries += 1
    return {
        'stored_entries': len(pending),
        'exact_duplicate_entries': exact_duplicate_entries,
        'invalid_url_entries': invalid_url_entries,
        'vendor_resource_entries': vendor_resource_entries,
        'review_navigation_entries': review_navigation_entries,
        'preserved_distinct_urls': len(unique_clean),
        'preserved_job_flagged': job_flagged,
        'certain_shadow_removals': exact_duplicate_entries + invalid_url_entries + vendor_resource_entries,
    }


def scan(coverage, sources, cache_root, *, shard, shards=16, day='2026-11-17'):
    source_by_id = {s['id']: s for s in sources if isinstance(s, dict) and s.get('id')}
    source_rows = [
        row for row in coverage.get('sources', [])
        if isinstance(row, dict) and str(row.get('checked_at', ''))[:10] == day
        and row.get('adapter') == 'universal-employer'
        and row.get('matching') == 0
        and (row.get('pending_urls') or 0) > 0
        and isinstance(row.get('id'), str)
        and shard_for(row['id'], shards) == shard
    ]
    records = []
    for row in source_rows:
        sid = row['id']
        if sid not in source_by_id:
            records.append({'source_id': sid, 'problem': 'not-in-source-registry',
                            'coverage_pending': row.get('pending_urls')})
            continue
        path = source_cache_path(cache_root, sid)
        if not path.exists():
            records.append({'source_id': sid, 'problem': 'frontier-cache-not-restored',
                            'coverage_pending': row.get('pending_urls')})
            continue
        try:
            data = json.loads(path.read_text())
            metrics = analyze_pending(data.get('pending'))
            records.append({'source_id': sid, 'coverage_pending': row.get('pending_urls'),
                            'status': row.get('status'), 'requests': row.get('requests'),
                            **metrics})
        except (OSError, ValueError, TypeError) as exc:
            records.append({'source_id': sid, 'coverage_pending': row.get('pending_urls'),
                            'problem': 'invalid-frontier-cache: ' + type(exc).__name__})
    return {
        'shard': shard, 'shards': shards, 'coverage_day': day,
        'kind': 'shadow-audit-only', 'candidate_sources': len(source_rows),
        'records': records,
    }


def combine(shard_reports):
    expected_shards = {r['shard'] for r in shard_reports}
    if len(expected_shards) != len(shard_reports):
        raise ValueError('Duplicate shard results')
    if len({r['shards'] for r in shard_reports}) != 1:
        raise ValueError('Inconsistent shard count')
    if expected_shards != set(range(shard_reports[0]['shards'])):
        raise ValueError('Missing shard reports')
    if len({r['coverage_day'] for r in shard_reports}) != 1:
        raise ValueError('Inconsistent observation day')
    all_records = [row for r in shard_reports for row in r['records']]
    if len({row['source_id'] for row in all_records}) != len(all_records):
        raise ValueError('Duplicate source across shards')
    observed = [r for r in all_records if 'problem' not in r]
    totals = defaultdict(int)
    for row in observed:
        for key in ('coverage_pending', 'stored_entries', 'exact_duplicate_entries',
                    'invalid_url_entries', 'vendor_resource_entries',
                    'review_navigation_entries', 'preserved_distinct_urls',
                    'preserved_job_flagged', 'certain_shadow_removals'):
            totals[key] += row[key]
    return {
        'observation_day_utc': shard_reports[0]['coverage_day'],
        'shards': len(shard_reports),
        'target_source_reports': len(all_records),
        'cache_matched_sources': len(observed),
        'unmatched_sources': len(all_records) - len(observed),
        'total_coverage_pending_in_target_sources': sum(int(r.get('coverage_pending') or 0) for r in all_records),
        'matched_source_totals': dict(sorted(totals.items())),
        'unmatched_source_ids': [r['source_id'] for r in all_records if 'problem' in r],
        'top_certain_shadow_removals': sorted(
            ({k: r[k] for k in ('source_id', 'coverage_pending', 'stored_entries',
                               'exact_duplicate_entries', 'vendor_resource_entries',
                               'certain_shadow_removals')} for r in observed),
            key=lambda r: (-r['certain_shadow_removals'], r['source_id'])
        )[:20],
        'limits': ('Frontier cache is a restore snapshot and may be older than '
                   'the coverage report; compare source and retained counts. '
                   'Only exact duplicate URL entries, invalid URLs and provider '
                   'static assets are candidate removals, not HTTP savings. '
                   'Employer pages are never requested or closed.'),
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--coverage', type=Path, default=Path('data/coverage.json'))
    p.add_argument('--sources', type=Path, default=Path('data/sources.json'))
    p.add_argument('--cache-root', type=Path, default=Path('.cache/collector'))
    p.add_argument('--day', default='2026-11-17')
    p.add_argument('--shard', type=int)
    p.add_argument('--shards', type=int, default=16)
    p.add_argument('--input-dir', type=Path)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    if args.input_dir:
        reports = [json.loads(f.read_text()) for f in sorted(args.input_dir.rglob('frontier-shard-*.json'))]
        result = combine(reports)
    else:
        if args.shard is None:
            p.error('Select --shard or --input-dir')
        result = scan(json.loads(args.coverage.read_text()),
                      json.loads(args.sources.read_text()), args.cache_root,
                      shard=args.shard, shards=args.shards, day=args.day)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'records'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
