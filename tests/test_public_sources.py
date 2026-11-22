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
            dict(countries=['SE'], status='open', internship_type='internship', advertisement_language={'code': 'sv'}),
            dict(countries=['SE'], status='open', internship_type='working-student', advertisement_language={'code': 'en'}),
            dict(countries=['SE', 'DK'], status='unverified'),
            dict(countries=['NL'], status='closed')])
        coverage = dict(sources=[dict(id='s1', status='ok'), dict(id='s2', status='partial', records_inspected=0)])
        sources = [dict(id='s1', enabled=True, target_countries=['SE']), dict(id='s2', enabled=True, target_countries=['SE'])]
        result = country_metric.metric(catalog, coverage, sources)
        self.assertEqual(len(result['rows']), 29)
        se = next(r for r in result['rows'] if r['code'] == 'SE')
        self.assertEqual((se['verified_open'], se['to_verify'], se['sources_functioning'], se['sources_enabled']), (2, 1, 1, 2))
        self.assertEqual((se['verified_internships'], se['verified_english'], se['verified_local']), (1, 1, 1))
        self.assertEqual(result['summary']['countries_with_verified'], 1)
        before = country_metric.metric(dict(jobs=[]), {}, sources)
        text = country_metric.markdown(result, before)
        self.assertIn('| SE Sweden | 0 → 2 | 1 | 1 | 1 | 0 → 1 |', text)
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp)
            for name, value in (('catalog.json', catalog), ('coverage.json', coverage), ('sources.json', sources)):
                (data / name).write_text(json.dumps(value))
            with contextlib.redirect_stdout(io.StringIO()):
                country_metric.main(['--data', tmp, '--json', str(data / 'out.json')])
            self.assertEqual(json.loads((data / 'out.json').read_text())['summary']['verified_open'], 2)


if __name__ == '__main__':
    unittest.main()


EURES_PAGE = json.loads((Path(__file__).parent / 'fixtures' / 'eures' / 'search-page.json').read_text())


class FakeEuresClient:
    """One fixture page for every search; per-vacancy lookups from a dict or 404."""
    def __init__(self, details=None):
        self.posts, self.gets, self.details = [], [], details or {}

    def post_json(self, url, payload):
        self.posts.append(payload)
        return EURES_PAGE if payload['page'] == 1 else dict(EURES_PAGE, jvs=[])

    def json(self, url):
        self.gets.append(url)
        identifier = urlsplit(url).path.rsplit('/', 1)[-1]
        if identifier in self.details:
            return self.details[identifier]
        raise HTTPError(url, 404, 'RESOURCE_UNAVAILABLE', None, None)


def eures_source(**extra):
    value = dict(id='public-eu-eures', employer='EURES – European Job Mobility Portal (ELA)', adapter='eures-search',
                 enabled=True, source_kind='public-employment-service', allowed_hosts=['europa.eu'],
                 target_countries=['BE', 'GR'], queries=['HR intern'], combined_queries=[])
    value.update(extra)
    return value


class EuresAdapterTests(unittest.TestCase):
    def test_summary_maps_to_official_portal_page_and_nuts_place(self):
        from collector.public_sources import eures_record
        record = eures_record(eures_source(), EURES_PAGE['jvs'][0])
        self.assertEqual(record['url'], 'https://europa.eu/eures/portal/jv-se/jv-details/QkUtSFItMQ?lang=en')
        self.assertEqual(record['countries'], ['BE'])
        self.assertEqual(record['city'], 'Arr. Kortrijk')
        self.assertEqual(record['language'], 'nl')
        self.assertNotIn('jobs@example.be', record['text'])
        self.assertNotIn('470 12 34 56', record['text'])
        self.assertEqual(eures_record(eures_source(), EURES_PAGE['jvs'][2])['countries'], ['GR'])

    def test_search_reads_internship_facet_then_titles_and_closes_only_on_404(self):
        known = ['https://europa.eu/eures/portal/jv-se/jv-details/R09ORQ?lang=en']
        client = FakeEuresClient()
        rows = collect(eures_source(known_job_urls=known), client)
        self.assertEqual(client.posts[0]['positionOfferingCodes'], ['internship'])
        self.assertEqual(client.posts[1]['keywords'], [{'keyword': 'HR intern', 'specificSearchCode': 'TITLE'}])
        self.assertTrue(all(p['resultsPerPage'] == 50 for p in client.posts))
        self.assertEqual(len(rows), 4)
        self.assertEqual(rows.stats['verified_closed_urls'], known)
        self.assertFalse(rows.stats['closure_complete'])

    def test_pipeline_keeps_hr_internships_in_scope_and_drops_non_hr(self):
        part = process_source(eures_source(), FakeEuresClient(), '2026-11-17T08:00:00+00:00')
        titles = sorted((j['title'], tuple(j['countries'])) for j in part['jobs'])
        self.assertEqual(titles, [('HR Intern', ('GR',)), ('HR Praktikum', ('CH',)), ('Internship HR', ('BE',))])
        self.assertEqual(next(j for j in part['jobs'] if j['countries'] == ['CH'])['city'], 'Zürich')
        self.assertTrue(all(j['link_status'] == 'public-api-listed' and j['status'] == 'unverified' for j in part['jobs']))

    def test_eures_copy_yields_to_employer_and_national_listings(self):
        own = dict(id='a', source_id='greenhouse-x', employer='Splendor Plant AB', title='HR Intern', countries=['SE'],
                   status='open', url='https://x.example/1', apply_url='https://x.example/1')
        national = dict(id='b', source_id='public-se-jobtech', employer='Exempel AB', title='HR-praktik', countries=['SE'],
                        status='unverified', url='https://arbetsformedlingen.se/platsbanken/annonser/9', apply_url='https://arbetsformedlingen.se/platsbanken/annonser/9')
        copy_own = dict(own, id='c', source_id='public-eu-eures', employer='Splendor Plant Aktiebolag', url='https://europa.eu/eures/portal/jv-se/jv-details/A')
        copy_national = dict(national, id='d', source_id='public-eu-eures', url='https://europa.eu/eures/portal/jv-se/jv-details/B')
        jobs, merged = merge_public_duplicates([own, national, copy_own, copy_national],
                                               ['public-se-jobtech', 'public-eu-eures'], ['public-eu-eures'])
        self.assertEqual((sorted(j['id'] for j in jobs), merged), (['a', 'b'], 2))
        self.assertEqual(national['duplicate_source_ids'], ['public-eu-eures'])


class EuresDetailTests(unittest.TestCase):
    def test_detail_reduces_to_summary_without_contacts_and_undisclosed_employer(self):
        from collector.public_sources import eures_detail_summary, eures_record
        detail = {'id': 'X1', 'preferredLanguage': 'de', 'creationDate': 1794698333140, 'jvProfiles': {'de': {
            'title': 'Werkstudent im Recruiting (m/w/d)', 'description': 'Recruiting. Mail n.m@example.de',
            'positionOfferingCode': 'internship', 'locations': [{'countryCode': 'de', 'region': 'ded44', 'cityName': 'Plauen'}],
            'employer': {'name': 'siehe Beschreibung'},
            'personContacts': [{'givenName': 'Nicole', 'familyName': 'Muster', 'communications': {'emails': [{'uri': 'n.m@example.de'}]}}]}}}
        summary = eures_detail_summary(detail, 'X1')
        self.assertNotIn('personContacts', json.dumps(summary))
        record = eures_record(eures_source(), summary)
        self.assertEqual(record['countries'], ['DE'])
        self.assertEqual(record['employer'], 'Employer not disclosed (see EURES advertisement)')
        self.assertNotIn('Nicole', json.dumps(record))
        self.assertNotIn('n.m@example.de', record['text'])
        self.assertIsNone(eures_record(eures_source(), eures_detail_summary({'jvProfiles': {}}, 'X2')))


class EuresResilienceTests(unittest.TestCase):
    def test_dropped_connection_is_retried_then_query_skipped_as_partial(self):
        from http.client import RemoteDisconnected

        class Flaky(FakeEuresClient):
            def post_json(self, url, payload):
                self.posts.append(payload)
                if payload['keywords']:
                    raise RemoteDisconnected('Remote end closed connection without response')
                return EURES_PAGE if payload['page'] == 1 else dict(EURES_PAGE, jvs=[])
        client = Flaky()
        rows = collect(eures_source(), client)
        self.assertEqual(rows.stats['status'], 'partial')
        self.assertEqual(rows.stats['search_errors'][0]['query'], 'HR intern')
        self.assertEqual(sum(1 for p in client.posts if p['keywords']), 2)  # one retry
        self.assertEqual(len(rows), 4)

    def test_access_refusal_fails_the_source(self):
        class Refused(FakeEuresClient):
            def post_json(self, url, payload):
                raise HTTPError(url, 403, 'Forbidden', None, None)
        with self.assertRaises(HTTPError):
            collect(eures_source(), Refused())


class JobTechResilienceTests(unittest.TestCase):
    def test_truncated_page_is_retried_once_then_skipped(self):
        class Truncated(FakeClient):
            def json(self, url):
                if '/search' in url and 'intern' in url:
                    self.calls.append(url)
                    raise json.JSONDecodeError('Unterminated string', '', 0)
                return super().json(url)
        client = Truncated()
        rows = collect(source(queries=['+internship', '+praktik +HR']), client)
        self.assertEqual(rows.stats['status'], 'partial')
        self.assertEqual(rows.stats['search_errors'][0]['query'], '+internship')
        self.assertEqual(sum('internship' in c for c in client.calls), 2)
        self.assertEqual(len(rows), 2)


class PublicApiVerificationRuleTests(unittest.TestCase):
    STAMP = '2026-11-17T08:00:00+00:00'

    def rule(self, flagged=True, **record):
        from collector.public_sources import public_api_verification, INVENTORY_EVIDENCE
        value = dict(inventory_evidence=INVENTORY_EVIDENCE, published_at='2026-11-02T09:00:00', valid_through=None)
        value.update(record)
        return public_api_verification(source(active_listing_api=flagged), value, self.STAMP)

    def test_reviewed_active_listing_api_verifies_current_ads(self):
        verified, status, reason = self.rule()
        self.assertEqual((verified, status), (self.STAMP, 'public-api-active-listing'))
        self.assertIn('employer application page was not checked', reason)
        self.assertEqual(self.rule(published_at='2025-01-01', valid_through='2026-12-31')[0], self.STAMP)

    def test_rule_does_not_apply_without_review_flag_or_with_weak_evidence(self):
        self.assertEqual(self.rule(flagged=False)[:2], (None, 'public-api-listed'))
        self.assertIsNone(self.rule(valid_through='2026-11-16')[0])               # deadline passed
        self.assertIsNone(self.rule(published_at='2026-03-01T00:00:00')[0])       # >180 days, no deadline
        self.assertIsNone(self.rule(published_at=None)[0])                        # undated, no deadline
        self.assertIsNone(self.rule(published_at='2027-03-01')[0])                # future publication
        self.assertIsNone(self.rule(published_at='not a date')[0])
        self.assertIsNone(self.rule(inventory_evidence='employer-board')[0])

    def test_pipeline_opens_verified_public_listing_and_catalog_validates(self):
        part = process_source(source(active_listing_api=True), FakeClient(), self.STAMP)
        job = part['jobs'][0]
        self.assertEqual((job['status'], job['link_status'], job['last_verified_at']), ('open', 'public-api-active-listing', self.STAMP))
        self.assertEqual(job['verification']['state'], 'verified')
        self.assertEqual(job['verification']['policy'], 'public-api-active-listing')
        catalog = dict(schema_version=1, countries=COUNTRIES, languages=LANGUAGES,
                       categories={k: v[0] for k, v in CATEGORIES.items()}, jobs=part['jobs'])
        self.assertTrue(validate_catalog(catalog))

    def test_verified_public_copy_replaces_unverified_employer_duplicate(self):
        own = dict(id='a', source_id='greenhouse-x', employer='Exempel AB', title='HR praktik', countries=['SE'],
                   status='unverified', url='https://x.example/1', apply_url='https://x.example/1')
        public = dict(own, id='b', source_id='public-se-jobtech', status='open', employer='Exempel Aktiebolag',
                      url='https://arbetsformedlingen.se/platsbanken/annonser/5', apply_url='https://arbetsformedlingen.se/platsbanken/annonser/5')
        eures = dict(public, id='c', source_id='public-eu-eures', url='https://europa.eu/eures/portal/jv-se/jv-details/Z')
        jobs, merged = merge_public_duplicates([own, public, eures], ['public-se-jobtech', 'public-eu-eures'], ['public-eu-eures'])
        self.assertEqual(([j['id'] for j in jobs], merged), (['b'], 2))
        self.assertEqual(jobs[0]['duplicate_source_ids'], ['greenhouse-x', 'public-eu-eures'])
        self.assertEqual(jobs[0]['related_listing_urls'], ['https://x.example/1'])
        # An open employer listing is never replaced.
        jobs, _ = merge_public_duplicates([dict(own, status='open'), dict(public)], ['public-se-jobtech'])
        self.assertEqual([j['id'] for j in jobs], ['a'])


class EuresBudgetTests(unittest.TestCase):
    def test_budget_exhaustion_keeps_collected_records_as_partial(self):
        from collector.runtime import CollectionBudgetExceeded

        class Budgeted(FakeEuresClient):
            def post_json(self, url, payload):
                if payload['keywords'] and payload['keywords'][0]['keyword'] == 'second':
                    raise CollectionBudgetExceeded('Collection time budget exhausted')
                return super().post_json(url, payload)
        client = Budgeted()
        rows = collect(eures_source(queries=['HR intern', 'second', 'third'], known_job_urls=['https://europa.eu/eures/portal/jv-se/jv-details/X?lang=en']), client)
        self.assertEqual(rows.stats['status'], 'partial')
        self.assertEqual(rows.stats['budget_stopped_at'], 'second')
        self.assertIn('third', rows.stats['truncated_queries'])
        self.assertEqual(len(rows), 4)
        self.assertEqual(client.gets, [])  # no per-vacancy checks after the budget ran out

    def test_priority_details_survive_search_budget_and_keep_exact_id(self):
        from collector.runtime import CollectionBudgetExceeded

        class Budgeted(FakeEuresClient):
            def post_json(self, url, payload):
                self.posts.append(payload)
                raise CollectionBudgetExceeded('Request budget exhausted')

        detail = {'id': 'SAME', 'preferredLanguage': 'nl', 'creationDate': 1794698333140,
                  'jvProfiles': {'nl': {'title': 'Stage HR', 'locations': [{'countryCode': 'BE'}]}}}
        client = Budgeted({'SAME': detail, 'WRONG': detail})
        known = ['https://europa.eu/eures/portal/jv-se/jv-details/' + key + '?lang=en'
                 for key in ('SAME', 'WRONG', 'MISSING', 'OTHER')]
        source = eures_source(known_job_urls=known, priority_recheck_urls=known,
                              max_known_checks=3, active_listing_api=True)
        part = process_source(source, client, '2026-11-21T09:00:00+00:00')
        self.assertEqual(len(client.gets), 3)
        self.assertEqual(len(client.posts), 1)
        self.assertEqual(part['report']['status'], 'partial')
        self.assertEqual(part['report']['budget_stopped_at'], 'positionOffering=internship')
        self.assertEqual(part['report']['verified_closed_urls'], [known[2]])
        self.assertEqual([job['external_id'] for job in part['jobs']], ['SAME'])
        job = part['jobs'][0]
        self.assertEqual(job['verification']['policy'], 'public-api-active-listing')
        self.assertIsNone(job.get('application_verification'))

    def test_normal_rechecks_skip_mismatched_id_and_continue(self):
        def details(identifier):
            return {'id': identifier, 'preferredLanguage': 'nl', 'creationDate': 1794698333140,
                    'jvProfiles': {'nl': {'title': 'Stage HR', 'locations': [{'countryCode': 'BE'}]}}}

        known = ['https://europa.eu/eures/portal/jv-se/jv-details/' + key + '?lang=en'
                 for key in ('MISMATCH', 'VALID')]
        client = FakeEuresClient({'MISMATCH': details('OTHER'), 'VALID': details('VALID')})
        source = eures_source(known_job_urls=known, active_listing_api=True)
        part = process_source(source, client, '2026-11-21T09:00:00+00:00')
        report = part['report']
        self.assertEqual(len(client.gets), 2)
        self.assertEqual(report['status'], 'partial')
        self.assertEqual(report['detail_errors'], [
            {'url': known[0], 'error': 'EURES detail returned a different vacancy identifier'}])
        self.assertEqual(report['verified_closed_urls'], [])
        jobs = {job['external_id']: job for job in part['jobs']}
        self.assertIn('QkUtSFItMQ', jobs)  # Keep previously collected search results.
        self.assertEqual(jobs['VALID']['verification']['policy'], 'public-api-active-listing')
        self.assertNotIn('MISMATCH', jobs)
        self.assertNotIn('OTHER', jobs)

    def test_same_cycle_search_result_overrides_priority_detail_404(self):
        client = FakeEuresClient()
        url = 'https://europa.eu/eures/portal/jv-se/jv-details/QkUtSFItMQ?lang=en'
        rows = collect(eures_source(priority_recheck_urls=[url], known_job_urls=[url]), client)
        self.assertEqual(len(client.gets), 1)
        self.assertNotIn(url, rows.stats['verified_closed_urls'])
        self.assertIn(url, [row['url'] for row in rows])

    def test_pair_queries_are_generated_and_deduplicated(self):
        from collector.public_sources import EURES_PAIR_QUERIES
        from collector.classify import fold
        self.assertIn('tirocinio paghe', EURES_PAIR_QUERIES)
        self.assertIn('praktikum personalentwicklung', EURES_PAIR_QUERIES)
        self.assertEqual(len({fold(q) for q in EURES_PAIR_QUERIES}), len(EURES_PAIR_QUERIES))


class EuresCrawledAdTests(unittest.TestCase):
    """UWV republishes crawled employer ads: no employer field, a Dutch label on
    English text, and the same ad under a new id."""
    HEADER = ('Northwind Events logo  Northwind Events Homepage  English en Northwind Events logo  '
              'Stage HR & Recruitment - Op locatie - Amsterdam - People & Culture ')
    BODY_EN = ('Would you like to help us find the right people? You will join our team and support '
               'the recruitment of our crew. We are looking for a student with an interest in HR.')

    def jv(self, identifier, header, created, title='Stage HR & Recruitment', body=None):
        return dict(id=identifier, title=title, description=header + (body or self.BODY_EN),
                    locationMap={'NL': ['NL329']}, employer={}, positionOfferingCode='temporary',
                    creationDate=created, availableLanguages=['nl'])

    def test_employer_read_from_repeated_logo_header_only(self):
        from collector.public_sources import eures_employer_from_text, eures_record
        self.assertEqual(eures_record(eures_source(), self.jv('A', self.HEADER, 1))['employer'], 'Northwind Events')
        self.assertIsNone(eures_employer_from_text('Indeed logo Indeed logo HR stage'))
        self.assertIsNone(eures_employer_from_text('Acme logo. HR stage at a company'))
        self.assertIsNone(eures_employer_from_text('Functiegebied HRM Regio Noord-Holland'))

    def test_clear_text_language_overrides_the_service_default_label(self):
        from collector.public_sources import eures_record
        self.assertIsNone(eures_record(eures_source(), self.jv('A', self.HEADER, 1))['language'])
        dutch = 'Wil jij ons team helpen? Je gaat aan de slag bij een van de leukste werkgevers en wij zijn op zoek naar jou voor een stage.'
        self.assertEqual(eures_record(eures_source(), self.jv('B', self.HEADER, 1, body=dutch))['language'], 'nl')

    def test_republished_vacancy_is_kept_once_with_the_newest_id(self):
        other_header = self.HEADER.replace('English en', 'Nederlands nl')
        page = dict(numberRecords=3, jvs=[self.jv('OLD', self.HEADER, 1000), self.jv('NEW', other_header, 2000),
                                          self.jv('ELSE', self.HEADER, 3000, title='HR Intern')])

        class Client(FakeEuresClient):
            def post_json(self, url, payload):
                self.posts.append(payload)
                return page if payload['page'] == 1 else dict(page, jvs=[])
        rows = collect(eures_source(), Client())
        self.assertEqual(sorted(r['external_id'] for r in rows), ['ELSE', 'NEW'])
        self.assertEqual(rows.stats['republished_duplicates_folded'], 1)
