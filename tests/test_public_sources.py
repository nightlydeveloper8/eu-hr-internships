import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit

from collector.adapters import collect
from collector.pipeline import process_source, validate_catalog
from collector.public_sources import (jobtech_record, jobtech_records, merge_public_duplicates, scrub,
                                      employer_key, title_key)
from collector.classify import COUNTRIES, LANGUAGES, CATEGORIES
from scripts import country_metric

FIXTURES = Path(__file__).parent / 'fixtures' / 'jobtech'
PAGE = json.loads((FIXTURES / 'search-page.json').read_text())
AD = json.loads((FIXTURES / 'ad-active.json').read_text())


def source(**extra):
    value = dict(id='public-se-jobtech', employer='Arbetsförmedlingen – Platsbanken (JobTech JobSearch)',
                 adapter='jobtech-search', enabled=True, source_kind='public-employment-service',
                 allowed_hosts=['arbetsformedlingen.se', 'jobsearch.api.jobtechdev.se'], target_countries=['SE'],
                 queries=['+praktik +HR'])
    value.update(extra)
    return value


class FakeClient:
    """Serves the fixture page for searches and per-ad lookups; records calls."""
    def __init__(self, ads=None):
        self.calls = []
        self.ads = ads or {}

    def json(self, url):
        self.calls.append(url)
        parts = urlsplit(url)
        if parts.path == '/search':
            offset = int(parse_qs(parts.query)['offset'][0])
            return PAGE if offset == 0 else dict(PAGE, hits=[])
        identifier = parts.path.rsplit('/', 1)[-1]
        if identifier in self.ads:
            return self.ads[identifier]
        raise HTTPError(url, 404, 'Ad not found', None, None)


class JobTechAdapterTests(unittest.TestCase):
    def test_swedish_ad_maps_to_official_page_without_contact_details(self):
        record = jobtech_record(source(), PAGE['hits'][0])
        self.assertEqual(record['url'], 'https://arbetsformedlingen.se/platsbanken/annonser/40000001')
        self.assertEqual(record['apply_url'], record['url'])
        self.assertEqual(record['countries'], ['SE'])
        self.assertEqual(record['city'], 'Malmö')
        self.assertEqual(record['valid_through'], '2026-12-14')
        self.assertEqual(record['work_mode'], 'hybrid')
        self.assertEqual(record['inventory_evidence'], 'official-public-api-active-listing')
        self.assertEqual(record['external_application_url'], 'https://careers.example.se/jobs/123-hr-praktik')
        self.assertNotIn('anna@example.se', record['text'])
        self.assertNotIn('070-123 45 67', record['text'])
        self.assertNotIn('Anna Andersson', json.dumps(record, ensure_ascii=False))
        self.assertIn('2027-01-18', record['text'])  # dates survive the phone filter

    def test_ads_abroad_and_removed_ads_are_skipped(self):
        self.assertIsNone(jobtech_record(source(), PAGE['hits'][2]))
        self.assertIsNone(jobtech_record(source(), dict(PAGE['hits'][0], removed=True)))

    def test_unapproved_advertisement_host_fails_the_source(self):
        with self.assertRaises(ValueError):
            jobtech_record(source(), dict(PAGE['hits'][0], webpage_url='https://example.org/ad/1'))

    def test_inventory_never_closes_by_absence_but_honours_explicit_removal(self):
        known = ['https://arbetsformedlingen.se/platsbanken/annonser/40000009',
                 'https://arbetsformedlingen.se/platsbanken/annonser/40000010']
        client = FakeClient(ads={'40000009': AD})
        rows = collect(source(known_job_urls=known), client)
        self.assertEqual({r['external_id'] for r in rows}, {'40000001', '40000002', '40000009'})
        self.assertFalse(rows.stats['closure_complete'])
        self.assertEqual(rows.stats['verified_closed_urls'], [known[1]])
        self.assertTrue(all('jobsearch.api.jobtechdev.se' in call for call in client.calls))

    def test_process_source_keeps_public_listing_unverified_and_exports_no_text(self):
        part = process_source(source(), FakeClient(), '2026-11-17T08:00:00+00:00')
        self.assertEqual(part['report']['status'], 'ok')
        self.assertEqual(len(part['jobs']), 1)
        job = part['jobs'][0]
        self.assertEqual(job['title'], 'Praktik inom HR och rekrytering i Malmö - våren 2027')
        self.assertEqual(job['status'], 'unverified')
        self.assertEqual(job['link_status'], 'public-api-listed')
        self.assertEqual(job['verification']['state'], 'incomplete')
        self.assertEqual(job['public_api_listed_at'], '2026-11-17T08:00:00+00:00')
        self.assertNotIn('text', job)
        self.assertEqual(part['closure_eligible'], [])
        catalog = dict(schema_version=1, countries=COUNTRIES, languages=LANGUAGES,
                       categories={k: v[0] for k, v in CATEGORIES.items()}, jobs=part['jobs'])
        self.assertTrue(validate_catalog(catalog))

    def test_scrub_keeps_amounts_and_dates(self):
        self.assertEqual(scrub('Lön 25 000 kr, start 2027-01-18, ring 08-123 456 78'), 'Lön 25 000 kr, start 2027-01-18, ring')


class PublicDuplicateTests(unittest.TestCase):
    def job(self, source_id, **extra):
        value = dict(id=source_id + extra.get('title', 'x'), source_id=source_id, employer='Exempel Bemanning AB',
                     title='Praktik inom HR och rekrytering', countries=['SE'], status='unverified',
                     url='https://careers.example.se/jobs/123', apply_url='https://careers.example.se/jobs/123/apply')
        value.update(extra)
        return value

    def test_public_copy_merges_into_employer_record_by_application_url(self):
        own = self.job('greenhouse-example')
        public = self.job('public-se-jobtech', url='https://arbetsformedlingen.se/platsbanken/annonser/1',
                          external_application_url='https://careers.example.se/jobs/123/apply', title='HR praktik')
        jobs, merged = merge_public_duplicates([own, public], ['public-se-jobtech'])
        self.assertEqual((len(jobs), merged), (1, 1))
        self.assertEqual(jobs[0]['duplicate_source_ids'], ['public-se-jobtech'])
        self.assertEqual(jobs[0]['public_listing_urls'], ['https://arbetsformedlingen.se/platsbanken/annonser/1'])

    def test_public_copy_merges_by_normalised_employer_title_country(self):
        own = self.job('greenhouse-example', employer='Exempel Bemanning', title='Praktik inom HR och rekrytering (m/f/d)')
        public = self.job('public-se-jobtech', employer='Exempel Bemanning Aktiebolag', url='https://arbetsformedlingen.se/platsbanken/annonser/2')
        jobs, merged = merge_public_duplicates([own, public], ['public-se-jobtech'])
        self.assertEqual(merged, 1)
        self.assertEqual(employer_key('Exempel Bemanning Aktiebolag'), employer_key('Exempel Bemanning'))
        self.assertEqual(title_key('HR Intern (m/w/d)'), title_key('HR Intern'))

    def test_ambiguous_or_foreign_matches_are_kept_separate(self):
        first = self.job('a', url='https://a.example/1')
        second = self.job('b', url='https://b.example/2')
        public = self.job('public-se-jobtech', url='https://arbetsformedlingen.se/platsbanken/annonser/3')
        jobs, merged = merge_public_duplicates([first, second, public], ['public-se-jobtech'])
        self.assertEqual((len(jobs), merged), (3, 0))
        other_country = self.job('public-se-jobtech', countries=['DK'], url='https://arbetsformedlingen.se/platsbanken/annonser/4')
        jobs, merged = merge_public_duplicates([first, other_country], ['public-se-jobtech'])
        self.assertEqual(merged, 0)


class CountryMetricTests(unittest.TestCase):
    def test_metric_has_29_rows_and_compares_before_after(self):
        catalog = dict(updated_at='2026-11-17', jobs=[
            dict(countries=['SE'], status='open'), dict(countries=['SE', 'DK'], status='unverified'),
            dict(countries=['NL'], status='closed')])
        coverage = dict(sources=[dict(id='s1', status='ok'), dict(id='s2', status='partial', records_inspected=0)])
        sources = [dict(id='s1', enabled=True, target_countries=['SE']), dict(id='s2', enabled=True, target_countries=['SE'])]
        result = country_metric.metric(catalog, coverage, sources)
        self.assertEqual(len(result['rows']), 29)
        se = next(r for r in result['rows'] if r['code'] == 'SE')
        self.assertEqual((se['verified_open'], se['to_verify'], se['sources_functioning'], se['sources_enabled']), (1, 1, 1, 2))
        self.assertEqual(result['summary']['countries_with_verified'], 1)
        before = country_metric.metric(dict(jobs=[]), {}, sources)
        text = country_metric.markdown(result, before)
        self.assertIn('| SE Sweden | 0 → 1 | 0 → 1 |', text)
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp)
            for name, value in (('catalog.json', catalog), ('coverage.json', coverage), ('sources.json', sources)):
                (data / name).write_text(json.dumps(value))
            with contextlib.redirect_stdout(io.StringIO()):
                country_metric.main(['--data', tmp, '--json', str(data / 'out.json')])
            self.assertEqual(json.loads((data / 'out.json').read_text())['summary']['verified_open'], 1)


if __name__ == '__main__':
    unittest.main()
