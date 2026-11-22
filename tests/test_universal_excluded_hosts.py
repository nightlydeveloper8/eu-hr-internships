import json
import tempfile
import unittest
from urllib.request import Request
from unittest.mock import patch

from collector.adapters import CheckedRedirect, Client
from collector.daily import provision
from collector.pipeline import reconcile
from collector.runtime import PageCache
from collector.universal import collect_universal
from collector.universal_hosts import excluded_url, universal_host_scope
from test_all_employers import FakeClient, posting, source

SMART = 'https://jobs.smartrecruiters.com/company/123'
ASHBY = 'https://jobs.ashbyhq.com/company/123'
CAREERS = 'https://example.org'
JOB = CAREERS + '/jobs/123'
STAMP = '2026-11-22T08:00:00+00:00'


class UniversalExcludedHostsTests(unittest.TestCase):
    def test_crawl_excludes_stale_checkpoint_seeds_and_observed_ats_links(self):
        employer = source()
        employer['start_urls'] += [SMART, ASHBY]
        employer['allowed_hosts'] += ['jobs.smartrecruiters.com', 'jobs.ashbyhq.com']
        employer['known_job_urls'] = [SMART]
        pages = {
            CAREERS: f'<a href="{SMART}">Careers</a><iframe src="{ASHBY}"></iframe><a href="{JOB}">HR Intern</a>',
            JOB: '<script type="application/ld+json">' + json.dumps(
                posting(hiringOrganization={'name': 'Example'})) + '</script>',
        }
        client = FakeClient(pages)
        with tempfile.TemporaryDirectory() as temp, patch.dict('os.environ', {'COLLECTOR_CACHE_DIR': temp}):
            cache = PageCache(employer['id'])
            cache.save_state({'preferred_career_url': ASHBY,
                              'allowed_hosts': ['jobs.smartrecruiters.com', 'jobs.ashbyhq.com'],
                              'pending': [{'url': ASHBY}]})
            jobs = collect_universal(employer, client)
            self.assertEqual(cache.state()['allowed_hosts'], ['example.org'])
            self.assertNotIn('preferred_career_url', cache.state())
        self.assertEqual(client.calls, [CAREERS, JOB])
        self.assertEqual([j['url'] for j in jobs], [JOB])

    def test_transport_denies_direct_requests_and_redirects_before_robots(self):
        client = Client()
        with patch.object(client, 'permitted') as robots, universal_host_scope(client):
            for url in (SMART, ASHBY, 'https://api.smartrecruiters.com/v1/companies/example/postings',
                        'https://jobs.ashbyhq.com./example'):
                with self.subTest(url=url):
                    with self.assertRaisesRegex(ValueError, 'Excluded universal ATS host'):
                        client.request(url)
                    with self.assertRaisesRegex(ValueError, 'Redirect to excluded'):
                        CheckedRedirect(client).redirect_request(Request(CAREERS), None, 302, '', {}, url)
            robots.assert_not_called()
        self.assertFalse(hasattr(client, 'universal_host_scope'))
        self.assertFalse(excluded_url('https://ashbyhq.com.example.org/careers'))

    def test_provision_uses_own_site_and_never_creates_an_ats_only_crawler(self):
        companies = [
            dict(id='mixed', name='Mixed', source_ids=[], career_url=SMART, website_url=CAREERS),
            dict(id='ats-only', name='ATS only', source_ids=[], career_url=ASHBY),
        ]
        c, s = provision(companies, [])
        crawler, = s
        self.assertEqual(crawler['id'], 'auto-mixed')
        self.assertEqual(crawler['start_urls'], [CAREERS])
        self.assertEqual(crawler['allowed_hosts'], ['example.org'])
        self.assertEqual(crawler['career_url'], CAREERS)
        self.assertEqual(c[1]['source_ids'], [])
        self.assertEqual(provision(c, s), (c, s))

    def test_excluded_url_is_never_absence_evidence_for_historical_record(self):
        def job(catalog_id, url):
            return dict(id=catalog_id, source_id='auto-example', source_type='universal-employer',
                        url=url, status='unverified', missing_count=2,
                        missing_since='2026-11-19T08:00:00+00:00')
        previous = [job('ats-id', SMART), job('independent-id', JOB)]
        result = {j['id']: j for j in reconcile(previous, [], {'auto-example'}, STAMP)}
        self.assertEqual(result['ats-id']['status'], 'unverified')
        self.assertEqual(result['ats-id']['missing_count'], 2)
        self.assertEqual(result['independent-id']['status'], 'closed')
