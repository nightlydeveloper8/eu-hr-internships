"""Prepare Ampelmann's reviewed Recruitee XML source DISABLED, never activate.

Must be used only on the branch that includes the reviewed public XML adapter.
An opt-in company hold prevents daily.provision() silently creating an enabled
universal crawler while the specific Recruitee adapter awaits cross-day proof.
--apply alters local registry files only; no HTTP, site, merge or activation.
"""
import argparse
from copy import deepcopy
import json
from pathlib import Path
from urllib.parse import urlsplit

from collector.company_registry import company_key, validate_registry
from collector.daily import provision
from collector.pipeline import ROOT

CAREER = 'https://careers.ampelmann.nl/'
FEED = 'https://careers.ampelmann.nl/api/feeds/offers.xml'
VACANCY = 'https://careers.ampelmann.nl/o/internship-people-organisation-1'
EMPLOYER = 'Ampelmann Operations B.V.'
COMPANY_ID = 'ampelmann-operations-b-v'
SOURCE_ID = 'recruitee-ampelmann-nl'
HOLD = 'collection_activation_hold'

SOURCE_TEMPLATE = dict(
    id=SOURCE_ID, company_id=COMPANY_ID, employer=EMPLOYER,
    adapter='recruitee', enabled=False,
    feed_format='recruitee-public-xml', application_check='recruitee-linked',
    feed_url=FEED, career_url=CAREER,
    allowed_hosts=['careers.ampelmann.nl'], target_countries=['NL'],
    ownership_scope='reviewed-hosts', require_employer_identity=True,
    permission_basis='Reviewed employer-published XML and same-ID application; runtime robots gate',
    max_requests=16, collection_seconds=70,
    status='pending-cross-day-and-rollout-approval',
)

COMPANY_TEMPLATE = dict(
    id=COMPANY_ID, name=EMPLOYER, career_url=CAREER,
    evidence_url=VACANCY, target_countries=['NL'],
    workplaces=[{'city': 'Delft', 'country': 'NL',
                 'location_confidence': 'confirmed', 'evidence_url': VACANCY}],
    source_ids=[SOURCE_ID],
    collection_activation_hold=True,
)


def prepare(companies, sources):
    companies, sources = deepcopy(companies), deepcopy(sources)
    eligible = [
        c for c in companies
        if company_key(c.get('name', '')) in ('ampelmann', company_key(EMPLOYER))
        or urlsplit(c.get('career_url') or '').hostname == 'careers.ampelmann.nl'
        or c.get('id') == COMPANY_ID
    ]
    if len(eligible) > 1:
        raise ValueError('Ambiguous existing Ampelmann company records: review required')
    matching = eligible[0] if eligible else None
    source_by_id = {s['id']: s for s in sources}
    if len(source_by_id) != len(sources):
        raise ValueError('Registry already contains duplicate source IDs')
    for source in sources:
        if source.get('id') == SOURCE_ID and (source.get('enabled')
                or source.get('company_id') not in (COMPANY_ID, matching['id'] if matching else COMPANY_ID)):
            raise ValueError('Proposed source ID already active or associated elsewhere')
    if matching:
        company = matching
        cid = company['id']
        if any(source_by_id.get(sid, {}).get('enabled') for sid in company.get('source_ids', [])):
            raise ValueError('Existing Ampelmann source already active; manual review before hold')
        company[HOLD] = True
        company.setdefault('source_ids', [])
        if SOURCE_ID not in company['source_ids']:
            company['source_ids'].append(SOURCE_ID)
        if 'NL' not in company.get('target_countries', []):
            company.setdefault('target_countries', []).append('NL')
        company.setdefault('career_url', CAREER)
        company.setdefault('evidence_url', VACANCY)
    else:
        company = deepcopy(COMPANY_TEMPLATE)
        companies.append(company)
        cid = COMPANY_ID
    if SOURCE_ID not in source_by_id:
        row = deepcopy(SOURCE_TEMPLATE)
        row['company_id'] = cid
        sources.append(row)
    else:
        row = source_by_id[SOURCE_ID]
        if (row.get('company_id') != cid or row.get('adapter') != 'recruitee'
                or row.get('feed_format') != 'recruitee-public-xml'
                or row.get('allowed_hosts') != ['careers.ampelmann.nl']):
            raise ValueError('Existing Ampelmann source differs from reviewed profile')
        if row.get('enabled') is not False:
            raise ValueError('Disabled flag changed unexpectedly')
    # A regular daily provision must NEVER auto-create an enabled universal
    # source for this held company; reject any accidental enabled source.
    provisioned_companies, provisioned_sources = provision(companies, sources)
    assert len(provisioned_companies) == len(companies)
    assert {x['id'] for x in provisioned_sources} == {x['id'] for x in sources}
    assert not [s for s in provisioned_sources
                if s.get('company_id') == cid and s.get('enabled')]
    return companies, sources, dict(company_id=cid, source_id=SOURCE_ID,
                                    enabled=False, hold=True,
                                    active_sources=0, auto_provisioned=0)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--companies', type=Path, default=ROOT / 'data/companies.json')
    p.add_argument('--sources', type=Path, default=ROOT / 'data/sources.json')
    p.add_argument('--apply', action='store_true',
                   help='Write reviewed DISABLED registry records to local branch')
    args = p.parse_args()
    originals = [json.loads(args.companies.read_text()), json.loads(args.sources.read_text())]
    companies, sources, summary = prepare(*originals)
    # No writes on a safety or identity failure.
    summary['would_add_companies'] = len(companies) - len(originals[0])
    summary['would_add_sources'] = len(sources) - len(originals[1])
    if args.apply:
        args.companies.write_text(json.dumps(companies, ensure_ascii=False, indent=2) + '\n')
        args.sources.write_text(json.dumps(sources, ensure_ascii=False, indent=2) + '\n')
    summary['registry_files_written'] = args.apply
    print(json.dumps(summary, sort_keys=True))


if __name__ == '__main__':
    main()
