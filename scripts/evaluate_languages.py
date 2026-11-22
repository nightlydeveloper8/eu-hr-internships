"""Replay the labelled ad languages against the published reference catalog."""
from collections import Counter, defaultdict
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from collector.classify import advertisement_language
from collector.public_sources import eures_language


def metrics(rows, predictions):
    scores = Counter()
    for row, result in zip(rows, predictions, strict=True):
        code = result.get('code')
        predicted = result.get('codes') or ([code] if code else [])
        scores['classified'] += bool(predicted)
        scores['matching'] += predicted == row['advertisement_languages']
        scores['confirmed'] += result.get('confidence') == 'confirmed'
    return dict(scores)


def per_country(rows, predictions, countries_for):
    result = defaultdict(Counter)
    for row, ad in zip(rows, predictions, strict=True):
        for country in countries_for(row):
            result[country][ad.get('code') or 'unknown'] += 1
    return dict(sorted(result.items()))


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'data/catalog.json'
    jobs = [job for job in json.loads(path.read_text())['jobs'] if job['status'] == 'open']
    by_id = {job['id']: job for job in jobs}
    rows = json.loads((ROOT / 'data/language-evaluation.json').read_text())['open_listings']
    before = [by_id[row['id']]['advertisement_language'] for row in rows]
    after = []
    for row in rows:
        body = row['body_tokens']
        metadata = eures_language(row['source_metadata'], row['title'], body)
        after.append(advertisement_language(body, metadata))
    snapshot_ads = [job['advertisement_language'] for job in jobs]
    summary = {
        'open': len(jobs),
        'codes': Counter(ad.get('code') or 'unknown' for ad in snapshot_ads),
        'confidence': Counter(ad['confidence'] for ad in snapshot_ads),
        'method': Counter(ad['method'] for ad in snapshot_ads),
        'confidence_method': Counter(ad['confidence'] + ' / ' + ad['method'] for ad in snapshot_ads),
        'named_requirement_evidence': sum(any(l.get('evidence') for l in job.get('workplace_languages', [])) for job in jobs),
        'explicit_status_with_named_excerpt': sum(
            job.get('language_requirements', {}).get('requirements_status') == 'explicit'
            and any(l.get('evidence') for l in job.get('workplace_languages', []))
            for job in jobs
        ),
        'english_support': sum(job.get('language_requirements', {}).get('english_support') == 'documented' for job in jobs),
        'english_sufficiency': sum(job.get('language_requirements', {}).get('english_sufficiency') == 'documented' for job in jobs),
        'snapshot_per_country': per_country(jobs, snapshot_ads, lambda job: job['countries']),
        'sample_size': len(rows),
        'sample_before': metrics(rows, before),
        'sample_after': metrics(rows, after),
        'sample_per_country_before': per_country(rows, before, lambda row: by_id[row['id']]['countries']),
        'sample_per_country_after': per_country(rows, after, lambda row: by_id[row['id']]['countries']),
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
