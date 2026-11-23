import unittest

from collector.classify import also_open_to_recent_graduates
from collector.pipeline import process_source, reconcile
from collector.verification import PERSONIO_STATIC_FORM, verify_vacancy
from test_disabled_submit_diagnostic import APPLY, Pages, STAMP, URL, form

FEED = 'https://example.jobs.personio.de/xml'
SOURCE = {
    'id': 'personio-example',
    'adapter': 'personio-xml',
    'employer': 'Example',
    'feed_url': FEED,
    'allowed_hosts': ['example.jobs.personio.de'],
    'application_check': PERSONIO_STATIC_FORM,
    'require_enrolled_students': True,
}
POSITION = '''<position><id>2540621</id><name>HR Intern</name><office>Berlin</office>
<jobDescriptions><jobDescription><value>Currently pursuing or recently completed a degree in HR.</value>
</jobDescription></jobDescriptions></position>'''
VACANCY = '<h1>HR Intern</h1><a href="/job/2540621/apply">Apply</a>'


def pages(position=POSITION, vacancy=VACANCY, application=None):
    if application is None:
        application = '<h1>HR Intern</h1>' + form()
    return Pages({FEED: '<workzag-jobs>' + position + '</workzag-jobs>',
                  URL: vacancy, APPLY: application})


class PersonioStaticApplicationTests(unittest.TestCase):
    def test_live_feed_and_visible_same_id_form_accept_disabled_submit(self):
        client = pages()
        result = process_source(SOURCE, client, STAMP)
        job, = result['jobs']
        self.assertEqual(client.calls, [FEED, URL, APPLY])
        self.assertEqual(job['status'], 'open')
        self.assertEqual(job['application_verification']['method'], PERSONIO_STATIC_FORM)
        self.assertEqual(job['application_verification']['vacancy_match'], 'personio-posting-id')
        self.assertTrue(job['also_open_to_recent_graduates'])
        self.assertFalse(result['closure_eligible'])

    def test_absent_from_feed_does_not_probe_vacancy(self):
        client = pages(position='')
        self.assertEqual(process_source(SOURCE, client, STAMP)['jobs'], [])
        self.assertEqual(client.calls, [FEED])

    def test_ordinary_feed_marker_without_personio_read_is_incomplete(self):
        record = dict(source_id=SOURCE['id'], external_id='2540621', posting_identifier='2540621',
                      inventory_evidence='current-employer-feed', name='Example', title='HR Intern', url=URL)
        client = pages()
        with self.assertRaisesRegex(ValueError, 'Current same-tenant Personio XML'):
            verify_vacancy(record, SOURCE, client, STAMP)
        self.assertEqual(client.calls, [URL])

    def test_different_posting_id_never_follows_the_link(self):
        client = pages(vacancy=VACANCY.replace('2540621', '1540621'))
        job, = process_source(SOURCE, client, STAMP)['jobs']
        self.assertEqual(job['status'], 'unverified')
        self.assertEqual(client.calls, [FEED, URL])

    def test_application_json_ld_cannot_identify_a_different_id(self):
        posting = ('<script type="application/ld+json">'
                   '{"@type":"JobPosting","title":"HR Intern","identifier":{"value":"123-456"}}'
                   '</script>')
        job, = process_source(SOURCE, pages(application='<h1>HR Intern</h1>' + posting + form()), STAMP)['jobs']
        self.assertEqual(job['status'], 'unverified')
        self.assertIn('identifier differs', job['verification']['reason'])

    def test_wrong_canonical_id_rejects_the_application(self):
        page = '<link rel="canonical" href="/job/123"><h1>HR Intern</h1>' + form()
        job, = process_source(SOURCE, pages(application=page), STAMP)['jobs']
        self.assertEqual(job['status'], 'unverified')
        self.assertIn('identifier differs', job['verification']['reason'])

    def test_graduate_only_internship_does_not_reach_the_application_check(self):
        graduate_only = POSITION.replace('Currently pursuing or recently completed', 'Recently completed')
        client = pages(position=graduate_only)
        self.assertEqual(process_source(SOURCE, client, STAMP)['jobs'], [])
        self.assertEqual(client.calls, [FEED])

    def test_missing_hidden_and_template_fields_do_not_verify(self):
        for candidate in ('<form><button disabled>Apply</button></form>',
                          '<div hidden>' + form() + '</div>',
                          '<template>' + form() + '</template>'):
            with self.subTest(candidate=candidate[:30]):
                client = pages(application='<h1>HR Intern</h1>' + candidate)
                job, = process_source(SOURCE, client, STAMP)['jobs']
                self.assertEqual(job['status'], 'unverified')
                self.assertNotIn('application_verification', job)

    def test_duplicate_posting_hold_never_counts_as_complete_inventory(self):
        duplicate = POSITION.replace('2540621', '2540622')
        client = pages(position=POSITION + duplicate)
        source = dict(SOURCE, duplicate_posting_ids=['2540622'])
        result = process_source(source, client, STAMP)
        self.assertEqual([job['external_id'] for job in result['jobs']], ['2540621'])
        self.assertFalse(result['closure_eligible'])

    def test_reviewed_mirror_retains_catalog_id_and_listing_provenance(self):
        public_url = 'https://europa.eu/eures/portal/jv-se/jv-details/example?lang=en'
        source = dict(SOURCE, reviewed_public_mirrors={'2540621': public_url})
        direct, = process_source(source, pages(), STAMP)['jobs']
        public = dict(id='existing-id', source_id='public-eu-eures', url=public_url,
                      first_discovered_at='2026-11-01T00:00:00+00:00', countries=['DE'],
                      status='open', verification={'policy': 'public-api-active-listing'})
        refreshed_public = dict(public, last_seen_at='2026-11-16T17:07:00+00:00')
        merged, = reconcile([public], [direct, refreshed_public], set(), STAMP)
        self.assertEqual(merged['id'], 'existing-id')
        self.assertEqual(merged['source_id'], SOURCE['id'])
        self.assertIn(public_url, merged['identity_aliases'])
        self.assertEqual(merged['application_verification']['method'], PERSONIO_STATIC_FORM)

    def test_reviewed_recruitee_mirror_precedes_same_cycle_public_copy(self):
        public_url = 'https://europa.eu/eures/portal/jv-se/jv-details/example?lang=en'
        public = dict(id='existing-id', source_id='public-eu-eures', url=public_url,
                      first_discovered_at='2026-11-01T00:00:00+00:00', countries=['NL'],
                      status='open', verification={'policy': 'public-api-active-listing'})
        direct = dict(id='direct-id', source_id='recruitee-example',
                      url='https://example.org/o/hr-intern', countries=['NL'],
                      status='open', last_seen_at=STAMP, identity_aliases=[public_url],
                      application_verification={'method': 'official-recruitee-same-posting-visible-form'})
        refreshed = dict(public, last_seen_at='2026-11-16T17:07:00+00:00')
        merged, = reconcile([public], [direct, refreshed], set(), STAMP)
        self.assertEqual(merged['id'], public['id'])
        self.assertEqual(merged['source_id'], direct['source_id'])
        self.assertIn(public_url, merged['identity_aliases'])
        self.assertIn('catalog:direct-id', merged['identity_aliases'])

    def test_recent_graduate_badge_requires_an_explicit_student_alternative(self):
        for evidence in ('Enrolled in or recently completed a degree.',
                         'Du studierst Psychologie oder hast dein Studium bereits erfolgreich abgeschlossen.'):
            self.assertTrue(also_open_to_recent_graduates(evidence))
        for evidence in ('You are currently pursuing a degree. Recent graduate programmes are also available.',
                         'Recent graduates should apply.', 'You must be enrolled throughout the placement.'):
            self.assertFalse(also_open_to_recent_graduates(evidence))

    def test_reviewed_sources_remain_enabled_through_provisioning(self):
        from pathlib import Path

        from collector.daily import provision
        from collector.pipeline import read

        root = Path(__file__).resolve().parents[1]
        companies = read(root / 'data/companies.json', [])
        sources = read(root / 'data/sources.json', [])
        expected = {
            'recruitee-mercedes-benz-io-pt',
            'personio-ten23-health-ch', 'personio-watson-farley-williams-de',
            'personio-studyflix-de', 'personio-bloomwell-group-de', 'personio-vamo-de',
            'personio-reformer-club-de', 'personio-wilken-software-group-de', 'personio-avantgarde-de',
        }
        provisioned_companies, provisioned_sources = provision(companies, sources)
        self.assertEqual((provisioned_companies, provisioned_sources), (companies, sources))
        by_id = {source['id']: source for source in provisioned_sources}
        employers = {company['id']: company for company in provisioned_companies}
        for source_id in expected:
            with self.subTest(source=source_id):
                source = by_id[source_id]
                company = employers[source['company_id']]
                self.assertIs(source['enabled'], True)
                self.assertNotIn('collection_activation_hold', source)
                self.assertNotIn('collection_activation_hold', company)
                self.assertEqual(company['source_ids'], [source_id])
                self.assertNotIn('auto-' + company['id'], by_id)
                self.assertEqual(
                    [candidate['id'] for candidate in provisioned_sources
                     if candidate.get('company_id') == company['id'] and candidate['enabled']],
                    [source_id],
                )
