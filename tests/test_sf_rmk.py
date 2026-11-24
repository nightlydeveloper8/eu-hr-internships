import unittest
from urllib.error import HTTPError

from collector.adapters import collect
from collector.pipeline import process_source
from collector.sf_rmk import candidate, request


HOST = 'https://careers.example.org'
SITEMAP = HOST + '/sitemap.xml'
JOB = HOST + '/job/Berlin-Pflichtpraktikum-HR/123/'
OTHER = HOST + '/job/Berlin-Software-Engineer/456/'
ROBOTS = b'User-agent: *\nDisallow: /applybutton/\nDisallow: /talentcommunity/\n'
SOURCE = {
    'id': 'rmk-test', 'adapter': 'sf-rmk', 'employer': 'Example',
    'allowed_hosts': ['careers.example.org'], 'sitemaps': [SITEMAP],
}
STAMP = '2026-11-24T10:00:00+00:00'


class Replay:
    def __init__(self, body, robots=ROBOTS):
        self.calls = []
        self.responses = {
            HOST+'/robots.txt': robots,
            SITEMAP: f'<urlset><url><loc>{JOB}</loc></url><url><loc>{OTHER}</loc></url></urlset>'.encode(),
            JOB.rstrip('/'): body,
        }

    def request(self, url, **kwargs):
        self.calls.append(url)
        if isinstance(self.responses[url], HTTPError):
            raise self.responses[url]
        return self.responses[url], 200, url


class RmkTests(unittest.TestCase):
    def test_microdata_current_listing_reads_only_the_requested_paths(self):
        body = f'''<html lang="de"><link rel="canonical" href="{JOB}">
          <div itemscope itemtype="https://schema.org/JobPosting">
            <h1 itemprop="title">Pflichtpraktikum HR</h1>
            <div itemprop="description"><p>Pflichtpraktikum für immatrikulierte Studierende.</p></div>
            <meta itemprop="datePosted" content="Mon Nov 23 00:00:00 UTC 2026">
            <meta itemprop="streetAddress" content="Berlin, DE, 12345">
            <a href="/talentcommunity/apply/123/">Jetzt bewerben</a>
          </div></html>'''.encode()
        client = Replay(body)
        report = process_source(SOURCE, client, STAMP)
        self.assertEqual(client.calls, [HOST+'/robots.txt', SITEMAP, JOB.rstrip('/')])
        job, = report['jobs']
        self.assertEqual(job['status'], 'open')
        self.assertEqual(job['student_eligibility'], 'confirmed')
        self.assertEqual(job['verification']['reason'], 'sf-rmk-sitemap-live-jobposting')
        self.assertNotIn('application_verification', job)
        self.assertEqual(report['report']['sitemap_jobs'], 2)

    def test_hold_and_robots_guard(self):
        client = Replay(b'')
        with self.assertRaisesRegex(ValueError, 'collection activation hold'):
            collect(dict(SOURCE, collection_activation_hold=True, enabled=True), client)
        self.assertEqual(client.calls, [])
        client = Replay(b'', ROBOTS+b'Disallow: /job/\n')
        result = process_source(SOURCE, client, STAMP)
        self.assertEqual(client.calls, [HOST+'/robots.txt', SITEMAP])
        self.assertFalse(result['jobs'])

    def test_detail_redirect_cannot_leave_public_vacancy_routes(self):
        class Redirect(Replay):
            def request(self, url, **kwargs):
                if url==JOB:
                    for forbidden in ('/applybutton/123/', '/services/job/Example/123/',
                                      '/talentcommunity/apply/123/', '/job/Other/987/'):
                        self_test.assertFalse(self.redirect_scope_allowed(HOST+forbidden))
                    self_test.assertFalse(self.redirect_scope_allowed('https://other.example.org/job/Example/123/'))
                    return b'', 200, url
                return super().request(url, **kwargs)
        self_test=self
        client=Redirect(b'')
        collect(SOURCE,client)
        request(SOURCE,client,JOB)

    def test_ignores_apprenticeships_and_matches_employer_branding(self):
        self.assertFalse(candidate(HOST+'/job/Paris-Alternance-RH/42/'))
        self.assertFalse(candidate(HOST+'/talentcommunity/apply/42/'))
        self.assertTrue(candidate(HOST+'/job/M%C3%BCnchen-Praktikant-Employer-Branding/42/'))
        self.assertTrue(candidate(HOST+'/Provinzial/job/D%C3%BCsseldorf-Praktikum-HRPersonal/42/'))
