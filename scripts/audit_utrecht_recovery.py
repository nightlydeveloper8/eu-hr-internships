"""Deterministic, offline preservation audit for the PR #7 recovery."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from collector.company_registry import validate_registry
from collector.pipeline import ROOT, read, validate_catalog, write

PUBLISHED_MAIN = 'ff618eb'
ORIGINAL_UTRECHT = '299d330'


def historical(ref, path):
    return json.loads(subprocess.check_output(['git', 'show', f'{ref}:{path}'], cwd=ROOT))


def audit():
    catalog = read(ROOT / 'data/catalog.json', {})
    validate_catalog(catalog)
    jobs = {j['id']: j for j in catalog['jobs']}
    main = historical(PUBLISHED_MAIN, 'data/catalog.json')['jobs']
    original = historical(ORIGINAL_UTRECHT, 'data/catalog.json')['jobs']
    assert {j['id'] for j in main} <= jobs.keys(), 'Published catalog IDs lost'
    assert {j['id'] for j in original} <= jobs.keys(), 'Original Utrecht catalog IDs lost'
    assert all(j == jobs[j['id']] for j in main), 'Published observations changed'
    runs = {r['id']: r for r in read(ROOT / 'data/coverage.json', {})['sources']}
    main_runs = historical(PUBLISHED_MAIN, 'data/coverage.json')['sources']
    assert all(r == runs[r['id']] for r in main_runs), 'Published source observations changed'
    assert read(ROOT / 'data/employer-collection.json', {}) == historical(PUBLISHED_MAIN, 'data/employer-collection.json')
    assert read(ROOT / 'data/ownership-reviews.json', []) == historical(PUBLISHED_MAIN, 'data/ownership-reviews.json')
    companies = read(ROOT / 'data/companies.json', [])
    sources = read(ROOT / 'data/sources.json', [])
    assert validate_registry(companies, read(ROOT / 'data/geography.json', {}), sources)
    assert {c['id'] for c in historical(PUBLISHED_MAIN, 'data/companies.json')} <= {c['id'] for c in companies}
    assert {s['id'] for s in historical(PUBLISHED_MAIN, 'data/sources.json')} <= {s['id'] for s in sources}
    # Existing workplaces outside Utrecht must survive Utrecht enrichment.
    by_id = {c['id']: c for c in companies}
    for c in historical(PUBLISHED_MAIN, 'data/companies.json'):
        for place in c.get('workplaces', []):
            if place.get('region_code') != 'NL35':
                assert place in by_id[c['id']]['workplaces'], (c['id'], 'Non-Utrecht workplace lost')
    geography = read(ROOT / 'data/utrecht-geography.json', {})
    assert geography == historical(ORIGINAL_UTRECHT, 'data/utrecht-geography.json')
    places = [p['code'] for m in geography['municipalities'] for p in m['settlements']]
    assert len(geography['municipalities']) == 26 and len(places) == len(set(places)) == 104
    researched = {c['id'] for c in companies if c.get('utrecht_research')}
    expected = {c['id'] for c in historical(ORIGINAL_UTRECHT, 'data/companies.json') if c.get('utrecht_research')}
    assert researched == expected and len(researched) == 51
    pending = {r['url'] for r in read(ROOT / 'data/listing-reviews.json', []) if r['decision'] == 'needs-verification'}
    for job in jobs.values():
        if job['source_id'] in ('auto-trunkrs', 'auto-domino-s-pizza-netherlands'):
            assert job['status'] == 'unverified' and job['url'] in pending
    coverage = read(ROOT / 'data/coverage.json', {})
    assert coverage['quality']['total'] == len(jobs)
    assert coverage['quality']['open'] == sum(j['status'] == 'open' for j in jobs.values())
    for slug in ('friesland', 'groningen', 'drenthe'):
        before = historical(PUBLISHED_MAIN, f'data/{slug}-coverage.json')
        after = read(ROOT / f'data/{slug}-coverage.json', {})
        assert before['verified_hr_internship_ids'] == after['verified_hr_internship_ids'], slug
    return dict(published_main=subprocess.check_output(['git','rev-parse',PUBLISHED_MAIN],cwd=ROOT,text=True).strip(),original_utrecht=ORIGINAL_UTRECHT,published_records=len(main),original_records=len(original),merged_records=len(jobs),published_records_lost=0,published_records_modified=0,published_source_reports_preserved=len(main_runs),municipalities=26,settlements=104,researched_employers=51,other_province_verified_ids_preserved=True,ownership_reviews_preserved=True,daily_employer_collection_preserved=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = audit()
    if args.output:
        write(args.output, result)
    print(json.dumps(result, ensure_ascii=False, separators=(',', ':')))
