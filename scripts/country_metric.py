"""Per-country success metric for the coverage plan (29 rows: EU-27 + CH + GB).

    python scripts/country_metric.py                       # markdown table to stdout
    python scripts/country_metric.py --json out.json       # also write JSON
    python scripts/country_metric.py --compare before.json # add before/after deltas

Columns: verified open HR internships, records awaiting verification, and
enabled sources targeting the country whose last run inspected records or
completed successfully. Output is diagnostic: in GitHub Actions it goes to the
job summary and the run artifacts, never into the repository.
"""
import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from collector.classify import COUNTRIES  # noqa: E402

EXTRA = {'CH': 'Switzerland', 'GB': 'United Kingdom'}


def read(path, default):
    return json.loads(path.read_text()) if path.exists() else default


def functioning(report):
    return report.get('status') == 'ok' or (report.get('status') == 'partial' and report.get('records_inspected', 0) > 0)


def metric(catalog, coverage, sources):
    countries = dict(COUNTRIES)
    countries.update({k: v for k, v in EXTRA.items() if k not in countries})
    reports = {r['id']: r for r in coverage.get('sources', [])}
    rows = []
    for code, name in countries.items():
        jobs = [j for j in catalog.get('jobs', []) if code in j.get('countries', [])]
        targeting = [s for s in sources if s.get('enabled') and code in s.get('target_countries', [])]
        rows.append(dict(
            code=code, name=name,
            verified_open=sum(j.get('status') == 'open' for j in jobs),
            to_verify=sum(j.get('status') == 'unverified' for j in jobs),
            sources_enabled=len(targeting),
            sources_functioning=sum(functioning(reports.get(s['id'], {})) for s in targeting),
        ))
    summary = dict(
        countries=len(rows),
        countries_with_verified=sum(r['verified_open'] > 0 for r in rows),
        countries_with_any_listing=sum(r['verified_open'] + r['to_verify'] > 0 for r in rows),
        verified_open=sum(r['verified_open'] for r in rows),
        to_verify=sum(r['to_verify'] for r in rows),
    )
    return dict(generated_from=catalog.get('updated_at'), summary=summary, rows=rows)


def markdown(result, before=None):
    old = {r['code']: r for r in (before or {}).get('rows', [])}
    cols = ('verified_open', 'to_verify', 'sources_functioning')
    head = '| Paese | Stage HR verificati e aperti | Da verificare | Fonti funzionanti / attive |'
    lines = [head, '|---|---:|---:|---:|']

    def cell(row, key):
        value = row[key]
        if row['code'] in old and old[row['code']][key] != value:
            return f'{old[row["code"]][key]} → {value}'
        return str(value)
    for row in result['rows']:
        functioning_cell = cell(row, 'sources_functioning') + f' / {row["sources_enabled"]}'
        lines.append(f'| {row["code"]} {row["name"]} | {cell(row, cols[0])} | {cell(row, cols[1])} | {functioning_cell} |')
    s = result['summary']
    b = (before or {}).get('summary')
    lines.append('')
    lines.append(f'Paesi con almeno uno stage HR verificato: **{s["countries_with_verified"]}/{s["countries"]}**'
                 + (f' (prima: {b["countries_with_verified"]})' if b else ''))
    lines.append(f'Paesi con almeno un annuncio (verificato o da verificare): {s["countries_with_any_listing"]}/{s["countries"]}'
                 + (f' (prima: {b["countries_with_any_listing"]})' if b else ''))
    return '\n'.join(lines) + '\n'


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=Path, default=ROOT / 'data')
    parser.add_argument('--json', type=Path)
    parser.add_argument('--compare', type=Path)
    parser.add_argument('--summary', action='store_true', help='append to $GITHUB_STEP_SUMMARY when set')
    args = parser.parse_args(argv)
    result = metric(read(args.data / 'catalog.json', {}), read(args.data / 'coverage.json', {}), read(args.data / 'sources.json', []))
    before = read(args.compare, None) if args.compare else None
    text = markdown(result, before)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    if args.summary and os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a', encoding='utf-8') as handle:
            handle.write('## Copertura per paese\n\n' + text)
    print(text)
    return result


if __name__ == '__main__':
    main()
