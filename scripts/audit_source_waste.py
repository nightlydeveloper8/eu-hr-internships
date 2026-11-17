"""Offline audit of expensive source-days with no HR matches.

Works on existing data/coverage.json only: no employer requests, browser, POST,
registry changes, or publication.  A matching=0 observation is not evidence that
the employer has no HR internships.  Patterns are mutually exclusive triage
buckets, not proven causal savings.
"""
import argparse
from collections import Counter, defaultdict
from datetime import date
import json
import math
from pathlib import Path
import re


PATTERNS = {
    'access_or_collection_error': 'Observed access restriction, error or failed source',
    'universal_frontier_backlog': 'Universal crawl with URLs still pending',
    'browser_render_without_hr': 'Rendered pages but no HR match',
    'universal_incomplete_other': 'Other incomplete universal crawl',
    'nonuniversal_incomplete': 'Incomplete specific-adapter source',
}
CONTROL = 'complete_no_hr_match'
ACCESS = re.compile(r'robots\.txt|disallow|\b40[1369]\b|\b429\b|captcha|challenge|access denied|rate.limit|timeout|timed out|ssl error|connection error|dns error', re.I)
INCOMPLETE = {'partial', 'discovery-incomplete', 'blocked', 'blocked-or-failed', 'failed', 'incomplete'}


def nonnegative_int(value):
    return value if type(value) is int and value >= 0 else 0


def nonnegative_float(value):
    return float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and value >= 0 else 0.0


def error_excerpt(report):
    parts = []
    for key in ('error', 'primary_error', 'page_errors'):
        value = report.get(key)
        if isinstance(value, str):
            parts.append(value[:500])
        elif isinstance(value, list):
            for item in value[:8]:
                parts.append(str(item)[:250])
    return ' | '.join(parts)


def incomplete(report):
    status = report.get('status')
    return status in INCOMPLETE or report.get('complete') is False or report.get('closure_complete') is False


def pattern(report):
    """One disjoint, descriptive class per no-HR source-day."""
    if report.get('status') in {'failed', 'blocked', 'blocked-or-failed'} or ACCESS.search(error_excerpt(report)):
        return 'access_or_collection_error'
    if report.get('adapter') == 'universal-employer' and nonnegative_int(report.get('pending_urls')) > 0 and incomplete(report):
        return 'universal_frontier_backlog'
    if nonnegative_int(report.get('rendered_pages')) > 0:
        return 'browser_render_without_hr'
    if report.get('adapter') == 'universal-employer' and incomplete(report):
        return 'universal_incomplete_other'
    if incomplete(report):
        return 'nonuniversal_incomplete'
    return CONTROL


def metrics(report):
    return {
        'requests': nonnegative_int(report.get('requests')),
        'bytes': nonnegative_int(report.get('bytes_read')),
        'renderings': nonnegative_int(report.get('rendered_pages')),
        'source_seconds': nonnegative_float(report.get('duration_seconds')),
    }


def combine(target, row):
    for key in ('requests', 'bytes', 'renderings', 'source_seconds'):
        target[key] += row[key]


def audit(coverage, target_date=None, topn=12):
    sources = coverage.get('sources', [])
    if not isinstance(sources, list):
        raise ValueError('coverage.sources must be a list')
    days = sorted({str(r.get('checked_at', ''))[:10] for r in sources
                   if isinstance(r, dict) and re.fullmatch(r'\d{4}-\d{2}-\d{2}', str(r.get('checked_at', ''))[:10])})
    selected_date = target_date or (days[-1] if days else '')
    if not selected_date:
        raise ValueError('No dated source observations')
    date.fromisoformat(selected_date)
    empty_cost = {k: 0 if k != 'source_seconds' else 0.0 for k in ('requests', 'bytes', 'renderings', 'source_seconds')}
    totals = dict(empty_cost)
    zero = dict(empty_cost, source_days=0)
    # Never seed a new bucket from running totals: doing so double counts HTTP.
    classified = defaultdict(lambda: dict(empty_cost, source_days=0, pending_urls=0, sources_with_rendering=0))
    statuses = Counter()
    top = []
    active_rows = 0
    unknown_matches = 0
    positive_matches = 0
    for report in sources:
        if not isinstance(report, dict) or str(report.get('checked_at', ''))[:10] != selected_date:
            continue
        if not report.get('id') or type(report.get('requests')) is not int:
            continue
        active_rows += 1
        m = metrics(report)
        combine(totals, m)
        match = report.get('matching')
        if type(match) is not int or match < 0:
            unknown_matches += 1
            continue
        if match > 0:
            positive_matches += 1
            continue
        zero['source_days'] += 1
        combine(zero, m)
        label = pattern(report)
        bucket = classified[label]
        bucket['source_days'] += 1
        bucket['pending_urls'] += nonnegative_int(report.get('pending_urls'))
        bucket['sources_with_rendering'] += int(m['renderings'] > 0)
        combine(bucket, m)
        statuses[str(report.get('status', 'unknown'))] += 1
        top.append(dict(source_id=report['id'], status=report.get('status'),
                        adapter=report.get('adapter'), pattern=label,
                        pending_urls=nonnegative_int(report.get('pending_urls')),
                        page_failures=nonnegative_int(report.get('page_failures')),
                        **m))
    ranked = [
        dict(pattern=key, interpretation=PATTERNS[key], **classified[key])
        for key in sorted(PATTERNS, key=lambda k: (-classified[k]['requests'], k))
    ]
    complete = dict(pattern=CONTROL, interpretation='Successful/complete observation with no HR match; not assumed a technical fault',
                    **classified[CONTROL])
    no_hr_request_pct = round(100 * zero['requests'] / totals['requests'], 2) if totals['requests'] else None
    return {
        'observation_date_utc': selected_date, 'fresh_source_reports': active_rows,
        'known_zero_hr_source_days': zero['source_days'],
        'positive_hr_source_days': positive_matches, 'matching_unknown_source_days': unknown_matches,
        'all_fresh_cost': totals, 'no_hr_cost': zero,
        'no_hr_requests_pct': no_hr_request_pct,
        'technical_pattern_rank_by_requests': ranked,
        'nontechnical_complete_no_hr': complete,
        'zero_hr_status_counts': dict(sorted(statuses.items())),
        'top_costly_zero_hr_sources': sorted(top, key=lambda row: (-row['requests'], row['source_id']))[:topn],
        'interpretation': 'Triage, not proof of wasted HTTP or causal savings. Matching means HR leads observed, not policy-v2 application verification. A failed/partial source cannot be marked empty or closed.',
        'cost_units': 'HTTP requests, transferred bytes, rendered pages, cumulative source-seconds; no monetary or wall-clock claim.',
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--coverage', type=Path, default=Path('data/coverage.json'))
    p.add_argument('--date', help='UTC day YYYY-MM-DD (default: last checked_at day)')
    p.add_argument('--output', type=Path, help='Optional path to the full JSON output')
    p.add_argument('--topn', type=int, default=12)
    a = p.parse_args()
    report = audit(json.loads(a.coverage.read_text()), a.date, max(0, min(a.topn, 50)))
    data = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)
    if a.output:
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_text(data + '\n')
    print(data)


if __name__ == '__main__':
    main()
