"""Offline identity-risk audit, not a claim that unmatched historical jobs are live."""
import json
from pathlib import Path

from collector.employer_resolution import is_reviewed_publisher, name_key, reviewed_source, validate_reviews

ROOT = Path(__file__).resolve().parents[1]


def audit(companies, sources, catalog, reviews):
    validate_reviews(reviews, sources)
    by_id = {s['id']: reviewed_source(s, reviews) for s in sources}
    mismatched = []
    scoped = []
    for job in catalog['jobs']:
        source = by_id.get(job.get('source_id'))
        if not source:
            continue
        if name_key(job.get('employer')) in {name_key(n) for n in
                                              [source['employer']]+source.get('employer_aliases',[])}:
            continue
        mismatched.append(job)
        if is_reviewed_publisher(job.get('employer'), source, job.get('url')):
            scoped.append(job)
    source_ids = sorted({j['source_id'] for j in mismatched})
    return dict(
        company_count=len(companies),
        configured_sources=len(sources),
        historical_catalog_ids=len(catalog['jobs']),
        historical_name_discrepancies=len(mismatched),
        affected_sources=len(source_ids),
        reviewed_publisher_matches=len(scoped),
        reviewed_publisher_ids=sorted(j['id'] for j in scoped),
        unreviewed_name_discrepancies=len(mismatched)-len(scoped),
        tilburg_unreviewed=sum(j['source_id']=='auto-tilburg-university' for j in mismatched),
        group_relationships_not_matching=sum(r['relation']!='official-recruiting-publisher' for r in reviews),
        live_requests=0,
        browser_renderings=0,
        candidacies_verified_by_audit=0,
        interpretation='Discrepancies are historical candidates for review, NOT confirmed ownership errors or current internships.'
    )


def main():
    def load(name):
        return json.loads((ROOT/'data'/name).read_text())
    report=audit(load('companies.json'),load('sources.json'),load('catalog.json'),
                 load('employer-identity-reviews.json'))
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()
