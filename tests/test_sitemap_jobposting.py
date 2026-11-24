import json
import unittest

from collector.adapters import ScopedRedirect
from collector.pipeline import process_source
from collector.sitemap_jobposting import collect_records

HOST = 'https://careers.example.org'
POSTING = HOST + '/en/jobs/hr-intern-12345'
TRANSLATION = HOST + '/fr/jobs/stage-rh-12345'
STAMP = '2026-11-24T12:00:00+00:00'


def sitemap(kind, entry, urls):
    return (f'<{kind}>' + ''.join(f'<{entry}><loc>{url}</loc></{entry}>' for url in urls)
            + f'</{kind}>').encode()


class FixtureClient:
    def __init__(self, pages):
        self.pages = pages
        self.requests = []
        self.host_delays = {}

    def request(self, url, **kwargs):
        self.requests.append(url)
        assert not kwargs['robots']
        assert not self.redirect_scope_allowed(url)
        value = self.pages[url]
        if isinstance(value, Exception):
            raise value
        return value, 200, url


def source(**overrides):
    return dict(dict(id='held-example', employer='Example', career_url=HOST,
                     allowed_hosts=['careers.example.org'], adapter='sitemap-jobposting',
                     enabled=False, collection_activation_hold=True, access_review='allowed'), **overrides)


class SitemapJobPostingTest(unittest.TestCase):
    def test_live_shape_replay_prioritizes_jobs_and_deduplicates_before_details(self):
        index, jobs, general = [HOST + path for path in ('/sitemap.xml', '/jobs.xml', '/pages.xml')]
        post = {'@type': 'JobPosting', 'title': 'HR Internship', 'description': 'Internship in human resources.',
                'datePosted': '2026-11-01', 'validThrough': '2026-12-31',
                'jobLocation': {'address': {'addressCountry': 'NL', 'addressLocality': 'Utrecht'}},
                'identifier': {'value': '12345'}}
        html = '<a href="/en/jobs/hr-intern-12345/apply">Apply now</a>'                '<script type="application/ld+json">' + json.dumps(post) + '</script>'
        client = FixtureClient({
            HOST + '/robots.txt': b'User-agent: *\nCrawl-delay: 3.5\nDisallow: /*/private/*\n',
            index: sitemap('sitemapindex', 'sitemap', [general, jobs]),
            jobs: sitemap('urlset', 'url', [POSTING, TRANSLATION, HOST + '/en/private/hr-intern-88888',
                                           HOST + '/jobs/hr-intern-alternance-23456',
                                           HOST + '/jobs/finance-intern-34567']),
            general: sitemap('urlset', 'url', []),
            POSTING: html.encode(),
        })
        part = process_source(source(), client, STAMP, staging=True)
        self.assertEqual(client.requests, [HOST + '/robots.txt', index, jobs, general, POSTING])
        self.assertEqual(client.host_delays['careers.example.org'], 3.5)
        self.assertEqual(part['report']['sitemap_candidates'], 1)
        job, = part['jobs']
        self.assertEqual(job['countries'], ['NL'])
        self.assertEqual(job['external_id'], '12345')
        self.assertEqual(job['status'], 'open')
        self.assertNotIn('application_verification', job)
        self.assertEqual(part['closure_eligible'], [])

    def test_nested_job_maps_beyond_six_reads_exclude_application_routes(self):
        maps = [f'{HOST}/jobs-{index}.xml' for index in range(10)]
        distractions = [f'{HOST}/articles-{index}.xml' for index in range(4)]
        pages = {
            HOST + '/robots.txt': f'Sitemap: {maps[0]}'.encode(),
            **{url: sitemap('sitemapindex', 'sitemap', [next_map, *distractions])
               for url, next_map in zip(maps, maps[1:])},
            maps[-1]: sitemap('urlset', 'url', [POSTING, HOST + '/apply/hr-intern-45678']),
            **{url: sitemap('urlset', 'url', []) for url in distractions},
        }
        result = collect_records(source(), FixtureClient(pages))
        self.assertEqual([record['url'] for record in result], [POSTING])
        self.assertEqual(result.stats['sitemaps_read'], 11)
        self.assertEqual(result.stats['sitemaps_pending'], 3)
        self.assertEqual(result.stats['status'], 'partial')

    def test_same_host_sitemap_redirect_is_counted_inside_discovery(self):
        initial = HOST + '/sitemap.xml'
        target = HOST + '/sitemap_index.xml'
        client = FixtureClient({
            HOST + '/robots.txt': b'User-agent: *',
            initial: ScopedRedirect(307, target),
            target: sitemap('urlset', 'url', [POSTING]),
        })
        self.assertEqual(len(collect_records(source(), client)), 1)
        self.assertEqual(client.requests, [HOST + '/robots.txt', initial, target])
        self.assertEqual([read['http'] for read in client.sitemap_jobposting_observations],
                         [200, 307, 200])

    def test_workday_selects_its_site_and_deduplicates_locale_variants(self):
        jobs = HOST + '/jobs.xml'
        english = HOST + '/en-US/Example/job/Rome/HR-Intern_JR000123'
        italian = HOST + '/it-IT/Example/job/Roma/Tirocinio-HR_JR000123'
        other = english.replace('/Example/', '/Other/')
        client = FixtureClient({
            HOST + '/robots.txt': f'User-agent: *\nSitemap: {jobs}'.encode(),
            jobs: sitemap('urlset', 'url', [other, english, italian]),
        })
        result = collect_records(source(adapter='workday', workday_site='Example'), client)
        self.assertEqual([row['external_id'] for row in result], ['JR000123'])
        self.assertEqual(client.requests, [HOST + '/robots.txt', jobs])

    def test_uncertain_access_makes_no_requests(self):
        client = FixtureClient({})
        with self.assertRaisesRegex(ValueError, 'documented access review'):
            collect_records(source(access_review='uncertain'), client)
        self.assertEqual(client.requests, [])

    def test_disallowed_sitemap_makes_no_detail_requests(self):
        robots = HOST + '/robots.txt'
        client = FixtureClient({robots: b'User-agent: *\nDisallow: /sitemap.xml$'})
        with self.assertRaisesRegex(ValueError, 'No permitted same-host sitemap'):
            collect_records(source(), client)
        self.assertEqual(client.requests, [robots])
