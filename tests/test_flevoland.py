"""Flevoland import, primary HLB evidence and real finalize regression boundaries."""
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from collector.pipeline import ROOT, read, finalize
from collector.flevoland import hlb_records
from collector.verification import verify_vacancy
from scripts.integrate_flevoland import integrate

AT = '2026-11-07T17:00:00+00:00'


class Client:
    def __init__(self, pages): self.pages = pages
    def request(self, url, **kwargs): return self.pages[url].encode(), 200, url


class FlevolandTests(unittest.TestCase):
    def test_official_geography_and_idempotent_existing_registry(self):
        geo = read(ROOT/'data/flevoland-geography.json', {})
        self.assertEqual({m['name'] for m in geo['municipalities']},
            {'Almere', 'Lelystad', 'Dronten', 'Noordoostpolder', 'Urk', 'Zeewolde'})
        codes = [p['code'] for m in geo['municipalities'] for p in m['settlements']]
        self.assertEqual(len(codes), 19)
        self.assertEqual(len(set(codes)), 19)
        rows = read(ROOT/'docs/flevoland-research-employers.json', {})['employers']
        companies = read(ROOT/'data/companies.json', [])
        sources = read(ROOT/'data/sources.json', [])
        first = integrate(companies, sources, geo, rows)
        self.assertEqual(first[:2], integrate(*first[:2], geo, rows)[:2])
        self.assertEqual(len(first[2]), 19)
        self.assertEqual(next(c for c in first[0] if c['id']=='alfen')['source_ids'],
            next(c for c in companies if c['id']=='alfen')['source_ids'])
        with self.assertRaisesRegex(ValueError, 'Unresolved CBS locality'):
            integrate(companies, sources, geo, [dict(rows[0], locality='Emmeloord')])

    def hlb(self):
        index = 'https://www.hlbbv.nl/nl/over-hlb/werken-bij/'
        vacancy = 'https://www.hlbbv.nl/nl/vacature/example'
        source = dict(id='hlb', employer='HLB Group', adapter='hlb-index', career_url=index,
            allowed_hosts=['www.hlbbv.nl'], reviewed_city_countries={'Dronten':'NL'},
            application_check='hlb-email', application_email='personeel@hlbbv.nl')
        pages = {index: '<div class="vacancies-overview-item"><div class="card"><h3>Stagiair HR</h3><span class="location-label"><i></i>Dronten</span><a href="/nl/vacature/example/">View vacancy</a></div></div>',
            vacancy: '<h1>Stagiair HR</h1><p>Je cv en motivatiebrief mogen gestuurd worden naar <a href="mailto:personeel@hlbbv.nl">personeel@hlbbv.nl</a></p><footer>Wijster</footer>'}
        return source, pages, index, vacancy

    def test_hlb_primary_card_location_and_vacancy_specific_email(self):
        source, pages, _, _ = self.hlb()
        records = hlb_records(source, Client(pages))
        self.assertEqual(records[0]['city'], 'Dronten')
        self.assertFalse(records.stats['complete'])
        proof = verify_vacancy(records[0], source, Client(pages), AT)
        self.assertEqual(proof['application_email'], 'personeel@hlbbv.nl')
        self.assertFalse(proof['delivery_verified'])

    def test_hlb_rejects_wrong_city_title_and_email_instructions(self):
        source, pages, index, vacancy = self.hlb()
        for mutated in (dict(pages, **{index: pages[index].replace('Dronten', 'Unknown')}),
                        dict(pages, **{vacancy: pages[vacancy].replace('<h1>Stagiair HR', '<h1>Other role')})):
            with self.assertRaises(ValueError): hlb_records(source, Client(mutated))
        record = hlb_records(source, Client(pages))[0]
        for old, new in [('mailto:personeel@hlbbv.nl', 'mailto:other@hlbbv.nl'),
                         ('Je cv en motivatiebrief mogen gestuurd worden naar', 'For questions contact')]:
            changed = dict(pages, **{vacancy: pages[vacancy].replace(old, new)})
            with self.assertRaises(ValueError): verify_vacancy(record, source, Client(changed), AT)

    def test_finalize_new_unverified_then_verified_then_partial_and_reappearance(self):
        template = copy.deepcopy(read(ROOT/'data/catalog.json', {})['jobs'][0])
        new = dict(template, id='new-flevoland', source_id='flv-test', employer='Example',
            source_posting_id='flv-1', url='https://example.org/job/1', apply_url='https://example.org/job/1/apply',
            status='unverified', link_status='incomplete', last_seen_at=AT, last_verified_at=None,
            first_discovered_at=AT, valid_through=None,
            verification=dict(state='incomplete', policy_version=2, checked_at=AT, reason='Application unverified'))
        source = dict(id='flv-test', enabled=True)
        def part(jobs, complete=False):
            return [dict(report=dict(id='flv-test', status='ok' if complete else 'partial',
                records_inspected=len(jobs), checked_at=AT), jobs=jobs,
                closure_eligible=['flv-test'] if complete else [])]
        with tempfile.TemporaryDirectory() as d, patch('collector.company_registry.region_codes_for_job', return_value=['NL23']):
            out = Path(d)
            r, cov = finalize([source], [source], {'jobs':[]}, {}, part([new]), AT, out)
            self.assertEqual(r['jobs'][0]['status'], 'unverified')
            self.assertEqual(r['jobs'][0]['first_discovered_at'], AT)
            # A partial successful source with no new match cannot promote or close it.
            r, cov = finalize([source], [source], r, cov, part([]), AT, out)
            self.assertEqual(r['jobs'][0]['status'], 'unverified')
            verified = dict(new, status='open', link_status='verified', last_verified_at=AT,
                verification=dict(state='verified', policy_version=2, checked_at=AT))
            r, cov = finalize([source], [source], r, cov, part([verified], True), AT, out)
            self.assertEqual(r['jobs'][0]['status'], 'open')
            self.assertEqual(r['jobs'][0]['id'], 'new-flevoland')
            # A fresh alias observation must keep the published catalog ID.
            alias = dict(verified, id='new-alias', first_discovered_at='2026-11-07T17:01:00+00:00')
            r, _ = finalize([source], [source], r, cov, part([alias]), AT, out)
            self.assertEqual([j['id'] for j in r['jobs']], ['new-flevoland'])
            self.assertEqual(r['jobs'][0]['first_discovered_at'], AT)


if __name__ == '__main__': unittest.main()
