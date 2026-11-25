import json
import unittest

from collector.pipeline import process_source
from collector.sitemap_jobposting import reference_cta
from test_sitemap_jobposting import FixtureClient, HOST, POSTING, STAMP, sitemap, source


def structured_script(value, attributes='type="application/ld+json"'):
    return f'<script {attributes}>{json.dumps(value)}</script>'


class SitemapPlatformTest(unittest.TestCase):
    def replay(self, url, body, **overrides):
        host = url.split('/')[2]
        base = 'https://' + host
        client = FixtureClient({
            base + '/robots.txt': b'User-agent: *\n',
            base + '/sitemap.xml': sitemap('urlset', 'url', [url]),
            url: body.encode(),
        })
        part = process_source(source(career_url=base, allowed_hosts=[host], **overrides),
                              client, STAMP, staging=True)
        self.assertEqual(len(client.requests), 3)
        return part['jobs']

    def test_bosch_reconciles_two_identifiers_using_only_the_official_page(self):
        identifier = 'b96ffbae-cfbf-45d7-a478-55c0abc15bbe'
        url = 'https://jobs.bosch.de/job/HR-Internship?id=' + identifier
        target = 'https://jobs.smartrecruiters.com/BoschGroup/744000163665309-hr-internship'
        post = dict(
            self.posting('DE'), identifier={'value': identifier},
            hiringOrganization={'name': 'Bosch Rexroth AG'})
        job = dict(online=True, source='bosch_smartrecruiters', idClient=identifier,
                   idFS='744000163665309', title='HR Internship',
                   company='Bosch Rexroth AG', applicationUrl=target)
        for different_id in (False, True):
            with self.subTest(different_id=different_id):
                if different_id:
                    job['idFS'] = '744000163665310'
                state = {'props': {'pageProps': {'job': {'data': job}}}}
                html = f'<a href="{target}">Jetzt bewerben</a>' + structured_script(post)
                html += structured_script(state, 'id="__NEXT_DATA__" type="application/json"')
                result, = self.replay(url, html, employer='Bosch',
                                      employer_aliases=['Bosch Rexroth AG'],
                                      reviewed_listing_layout='bosch')
                self.assertEqual(result['status'], 'unverified' if different_id else 'open')
                self.assertEqual(result['employer'], 'Bosch')
                self.assertEqual(result['employer_subsidiary'], 'Bosch Rexroth AG')
                self.assertNotIn('application_verification', result)
                self.assertEqual(result['apply_url'], url)

    def test_next_workday_requires_an_open_matching_requisition(self):
        url = HOST + '/job/hr-internship-j00355161'
        host = 'example.wd3.myworkdayjobs.com'
        target = 'https://' + host + '/External/job/Veldhoven/HR-Internship_J-00355161/apply'
        job = dict(status='Open', displayJobTitle='HR Internship', id='J-00355161',
                   detailPageUrl=url, applyUrl=target, datePosted='2026-11-18',
                   descriptionExternal='Internship in human resources.',
                   city='Veldhoven', country='Netherlands')
        for status in ('Open', 'Closed'):
            with self.subTest(status=status):
                job['status'] = status
                html = f'<h1>HR Internship</h1><a href="{target}">Apply now</a>'
                html += structured_script({'props': {'pageProps': {'jobData': job}}},
                                          'id="__NEXT_DATA__"')
                jobs = self.replay(url, html, reviewed_listing_layout='next-workday',
                                   reviewed_application_reference_hosts=[host])
                self.assertEqual([job['status'] for job in jobs], ['open'] if status == 'Open' else [])

    def test_workflow_requires_same_vacancy_before_using_explicit_locality_suffix(self):
        post = self.posting()
        post['jobLocation'] = [{'address': {'addressLocality': 'Paris, France'}}]
        for identifier in ('12345', '98765'):
            with self.subTest(identifier=identifier):
                html = f'<link rel="canonical" href="{POSTING}">'
                html += f'<a href="/en/Workflow?vacancyId={identifier}">Apply now</a>'
                jobs = self.replay(POSTING, html + structured_script(post),
                                   reviewed_listing_layout='vacancy-workflow')
                self.assertEqual([job['countries'] for job in jobs],
                                 [['FR']] if identifier == '12345' else [])

    def test_rmk_microdata_uses_agreeing_metadata_and_same_id_apply_link(self):
        body = f'<link rel="canonical" href="{POSTING}">'
        body += (
            '<meta property="og:title" content="HR Internship">'
            '<meta name="twitter:title" content="HR Internship">'
            '<main itemscope itemtype="https://schema.org/JobPosting">'
            '<meta itemprop="datePosted" content="Thu Nov 12 00:00:00 UTC 2026">'
            '<meta itemprop="streetAddress" content="Munich, DE, 80809">'
            '<div itemprop="description">Internship in Human Resources.</div>'
            '<a href="/talentcommunity/apply/12345/">Apply now</a></main>'
        )
        job, = self.replay(POSTING, body, reviewed_rmk_dates=True)
        self.assertEqual(job['status'], 'open')
        self.assertEqual(job['countries'], ['DE'])
        self.assertEqual(self.replay(POSTING, body.replace('name="twitter:title" content="HR Internship"',
                                                        'name="twitter:title" content="Other posting"'),
                                     reviewed_rmk_dates=True), [])

    def test_radancy_references_require_a_reviewed_host_and_an_exact_vacancy(self):
        cases = (
            ('loreal.example', '/job/Applicationmethods?jobId=256372', '256372'),
            ('ing.wd3.myworkdayjobs.com', '/ICSGBLCOR/job/Luxembourg/HR_REQ-10115027/apply', 'REQ-10115027'),
        )
        for host, path, identifier in cases:
            with self.subTest(host=host):
                url = 'https://' + host + path
                self.assertTrue(reference_cta(url, identifier, [host]))
                self.assertFalse(reference_cta(url, 'someone-else', [host]))
                self.assertFalse(reference_cta(url, identifier, ['other.example']))

    @staticmethod
    def posting(country='NL'):
        return {'@type': 'JobPosting', 'title': 'HR Internship',
                'description': 'Internship in human resources.', 'datePosted': '2026-11-18',
                'jobLocation': {'address': {'addressCountry': country}}}
