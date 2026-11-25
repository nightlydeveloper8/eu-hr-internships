import gzip
import json
import unittest

from collector.adapters import ScopedRedirect, Client
from collector.runtime import BudgetClient, CollectionBudgetExceeded, _RATE_LIMITED_HOSTS
from unittest.mock import patch
from urllib.error import HTTPError
from collector.pipeline import process_source
from collector.sitemap_jobposting import collect_records, phenom_listing, danone_posting, candidate, parse_sitemap, locations

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

    def test_mercedes_current_listing_uses_published_button_without_fetching_it(self):
        host = 'https://jobs.mercedes-benz.com'
        url = host + '/de/praktikant-personalmanagement-123456-mer0004a24'
        localized = url.replace('/de/', '/en/')
        post = {'@type': 'JobPosting', 'title': 'Praktikant Personalmanagement (Pflichtpraktikum)',
                'description': 'Sie sind immatrikuliert. Human Resources und Personalmanagement.',
                'datePosted': '2026-11-01', 'identifier': {'value': 'mer0004a24'},
                'jobLocation': {'address': {'addressCountry': 'DE', 'addressLocality': 'Stuttgart'}}}
        target = 'https://tas-daimler.taleo.net/careersection/ex/jobapply.ftl?job=MER0004A24'
        html = ('<script type="application/ld+json">' + json.dumps(post) + '</script>'
                '<wb-button aria-label="Bewerben" class="mjp-job-ad__content-tags-join-button" href="'
                + target + '">Bewerben</wb-button>')
        cfg = source(career_url=host, allowed_hosts=['jobs.mercedes-benz.com'],
                     reviewed_listing_layout='mercedes-benz')
        for markup, expected in ((html, 'open'), (html.replace('MER0004A24', 'MER0004A25'), 'unverified'),
                                 (html.replace('<wb-button', '<wb-button disabled'), 'unverified')):
            with self.subTest(expected=expected):
                client = FixtureClient({host + '/robots.txt': b'User-agent: *',
                                        host + '/sitemap.xml': sitemap('urlset', 'url', [url, localized]),
                                        url: markup.encode()})
                job, = process_source(cfg, client, STAMP, staging=True)['jobs']
                self.assertEqual(job['status'], expected)
                self.assertNotIn('application_verification', job)
                self.assertEqual(client.requests, [host + '/robots.txt', host + '/sitemap.xml', url])

    def test_workday_backoff_honors_retry_after_and_counts_both_gets(self):
        host = 'workday-backoff.test'
        root = 'https://' + host
        robots = root + '/robots.txt'
        jobs = root + '/jobs.xml'
        cfg = source(career_url=root, allowed_hosts=[host], adapter='workday', workday_site='Example')
        requests = []

        def response(_client, url, **_kwargs):
            requests.append(url)
            if len(requests) == 1:
                raise HTTPError(url, 429, 'Too Many Requests', {'Retry-After': '75'}, None)
            if url == robots:
                return f'Sitemap: {jobs}'.encode(), 200, url
            return sitemap('urlset', 'url', []), 200, url

        self.addCleanup(_RATE_LIMITED_HOSTS.discard, host)
        with patch.object(Client, 'request', response):
            client = BudgetClient(seconds=90, max_requests=3, delay=0)
            with patch.object(client, 'pause') as pause:
                self.assertEqual(collect_records(cfg, client), [])
            pause.assert_called_once_with(75)
            self.assertEqual(requests, [robots, robots, jobs])
            self.assertEqual(client.requests, 3)
            self.assertEqual(client.retry_outcomes['http-429'], 1)
            self.assertNotIn(host, _RATE_LIMITED_HOSTS)

        requests.clear()
        with patch.object(Client, 'request', response):
            client = BudgetClient(seconds=20, max_requests=3, delay=0)
            with self.assertRaises(CollectionBudgetExceeded):
                collect_records(cfg, client)
            self.assertEqual(requests, [robots])
            self.assertIn(host, _RATE_LIMITED_HOSTS)

    def test_radancy_city_slug_and_numeric_suffix_are_triaged(self):
        url = HOST + '/en/job/paris/stage-charge-de-recrutement/1234/12345678901'
        client = FixtureClient({HOST+'/robots.txt': b'User-agent: *',
                                HOST+'/sitemap.xml': sitemap('urlset', 'url', [url])})
        self.assertEqual([record['url'] for record in collect_records(source(), client)], [url])
        self.assertFalse(candidate('STAGE - Compensation d’une rotation par traitement IA'))
        self.assertTrue(candidate('Intern Compensation & Benefits'))

    def test_phenom_publication_needs_matching_external_job_and_route(self):
        route = 'https://example.wd3.myworkdayjobs.com/Careers/job/Paris/Stage-HR_R0344574-1/apply'
        job = dict(jobId='R0344574', reqId='R0344574', title='Stage HR',
                   jobVisibility=['external'], applyUrl=route)
        result = dict(posting_identifier='R0344574', title='Stage HR')
        def document():
            return ('<script>phApp.ddo = '+json.dumps({'jobDetail':{'data':{'job':job}}})+'</script>').encode()
        hosts = ['example.wd3.myworkdayjobs.com']
        self.assertTrue(phenom_listing(document(), result, hosts))
        self.assertFalse(phenom_listing(document(), result, []))
        job['jobVisibility'] = ['internal']
        self.assertFalse(phenom_listing(document(), result, hosts))
        job['jobVisibility'] = ['external']
        job['applyUrl'] = route.replace('R0344574', 'R0344575')
        self.assertFalse(phenom_listing(document(), result, hosts))

    def test_danone_requires_fragment_for_the_exact_listing(self):
        body = (b'<article data-cmp-contentfragment-model="/danone-job-model" title="Stage RH" key="stage-rh-29216-fr-fr" '
                b'jobid="29216" country="France" posted="1795198980000" description="Stage RH"></article>')
        url = HOST+'/jobs/stage-rh-29216-fr-fr.html'
        self.assertIsNone(danone_posting(body, url.replace('29216','29217')))
        self.assertEqual(danone_posting(body, url)['identifier'], '29216')

    def test_tolerant_sitemap_preserves_locations_and_rejects_truncation(self):
        valid = ('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
                 'xmlns:xhtml="http://www.w3.org/1999/xhtml"><url><loc>'+POSTING+'</loc>\n'
                 '<xhtml:link rel="alternate" href="https://careers.example.org/"quoted"/" />\n'
                 '</url></urlset>').encode('utf-8-sig')
        self.assertEqual(list(locations(parse_sitemap(gzip.compress(valid),
                          discard_broken_alternates=True), 'url')), [POSTING])
        with self.assertRaisesRegex(ValueError,'DOCTYPE'):
            parse_sitemap(b'<!DOCTYPE sitemap>'+valid, discard_broken_alternates=True)
        with self.assertRaisesRegex(ValueError,'20 MB transport limit'):
            parse_sitemap(b'<urlset>'+b' '*20_000_000, discard_broken_alternates=True)

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
