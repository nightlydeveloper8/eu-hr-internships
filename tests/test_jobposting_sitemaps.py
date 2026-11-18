"""Phase 3: large multi-country employer sitemaps read only through JobPosting pages."""
import json
import unittest

from collector.employer_pages import page_record, sitemap_records, slug_prefilter, slug_title

SITEMAP = b'''<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
<url><loc>https://careers.example.com/en/job/warsaw/hr-intern-talent-acquisition/123/456</loc></url>
<url><loc>https://careers.example.com/en/job/lyon/charge-de-recrutement-en-stage-h-f/26094/789</loc></url>
<url><loc>https://careers.example.com/en/job/madrid/key-account-manager/123/999</loc></url>
<url><loc>https://careers.example.com/en/about-us</loc></url></urlset>'''


def page(title, country=''):
    data = {'@context': 'http://schema.org', '@type': 'JobPosting', 'title': title,
            'description': 'Support the HR team with recruitment as an intern during your studies.',
            'hiringOrganization': {'@type': 'Organization', 'name': 'Example Group'},
            'jobLocation': [{'@type': 'Place', 'address': {'addressLocality': 'Lyon', 'addressCountry': country}}]}
    return ('<html><script type="application/ld+json">' + json.dumps(data) + '</script></html>').encode()


class Client:
    def __init__(self, pages):
        self.pages, self.read = pages, []

    def request(self, url):
        self.read.append(url)
        return self.pages[url], 200, url


def source(**extra):
    value = dict(id='employer-example', employer='Example Group', adapter='employer-sitemap', enabled=True,
                 sitemaps=['https://careers.example.com/sitemap.xml'], allowed_hosts=['careers.example.com'],
                 job_url_pattern=r'^https://careers\.example\.com/[a-z]+/job/', employer_tokens=['example'])
    value.update(extra)
    return value


class SlugPrefilterTests(unittest.TestCase):
    def test_slug_title_drops_ids_and_separators(self):
        self.assertEqual(slug_title('https://www.pgcareers.com/eu/en/job/R000157398/Human-Resources-Manager-Internship'),
                         'eu en job Human Resources Manager Internship')

    def test_only_hr_internship_slugs_are_read(self):
        client = Client({'https://careers.example.com/sitemap.xml': SITEMAP})
        rows = sitemap_records(source(url_slug_prefilter=True), client)
        self.assertEqual(sorted(r['url'] for r in rows), [
            'https://careers.example.com/en/job/lyon/charge-de-recrutement-en-stage-h-f/26094/789',
            'https://careers.example.com/en/job/warsaw/hr-intern-talent-acquisition/123/456'])
        self.assertFalse(slug_prefilter('https://careers.example.com/en/job/madrid/key-account-manager/123/999'))

    def test_without_prefilter_every_job_url_is_inventoried(self):
        client = Client({'https://careers.example.com/sitemap.xml': SITEMAP})
        self.assertEqual(len(sitemap_records(source(), client)), 3)

    def test_prefilter_with_no_current_match_is_an_empty_inventory_not_an_error(self):
        empty = SITEMAP.replace(b'hr-intern-talent-acquisition', b'sales').replace(b'charge-de-recrutement-en-stage-h-f', b'buyer')
        self.assertEqual(sitemap_records(source(url_slug_prefilter=True), Client({'https://careers.example.com/sitemap.xml': empty})), [])


class ReviewedCountryTests(unittest.TestCase):
    URL = 'https://careers.example.com/en/job/lyon/charge-de-recrutement-en-stage-h-f/26094/789'

    def record(self):
        return dict(source_id='employer-example', external_id=self.URL, employer='Example Group', title='', text='',
                    url=self.URL, apply_url=self.URL, needs_page=True)

    def test_empty_address_country_uses_reviewed_url_section(self):
        src = source(url_country_patterns={'/26094/': 'FR'})
        result = page_record(self.record(), src, Client({self.URL: page('Chargé de recrutement en stage H/F')}))
        self.assertEqual((result['countries'], result['country']), (['FR'], 'FR'))

    def test_published_address_country_wins(self):
        src = source(url_country_patterns={'/26094/': 'FR'})
        result = page_record(self.record(), src, Client({self.URL: page('Chargé de recrutement en stage H/F', 'Belgium')}))
        self.assertEqual(result['countries'], ['BE'])


if __name__ == '__main__':
    unittest.main()
