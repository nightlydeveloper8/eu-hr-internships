"""Offline regression for nullable Schema.org JobPosting employmentType."""
from datetime import datetime, timezone
import json
import unittest

from collector.employer_pages import page_record


class Pages:
    def __init__(self, url, body):
        self.url, self.body = url, body
        self.calls = []

    def request(self, url, **kwargs):
        self.calls.append(url)
        return self.body.encode(), 200, url


class NullableEmploymentTypeTests(unittest.TestCase):
    def test_null_entries_preserve_valid_jobposting_metadata(self):
        url = 'https://careers.example.com/jobs/hr-intern'
        source = dict(id='employer-example', employer='Example',
                      allowed_hosts=['careers.example.com'])
        basic = dict(
            **{'@type': 'JobPosting'},
            title='HR Internship',
            description='Join the people and recruitment team.',
            hiringOrganization={'name': 'Example'},
            jobLocation={'address': {'addressLocality': 'Amsterdam',
                                     'addressCountry': 'NL'}},
        )
        for raw, expected in [
            (['Internship', None, 'Part-time', '', None, 'Student'], 'Internship Part-time Student'),
            ([None, None], ''),
            (None, ''),
            ('Internship', 'Internship'),
        ]:
            with self.subTest(employmentType=raw):
                body = '<script type="application/ld+json">' + json.dumps(
                    dict(basic, employmentType=raw)) + '</script>'
                client = Pages(url, body)
                result = page_record({'url': url}, source, client,
                                     datetime(2026, 11, 16, tzinfo=timezone.utc))
                self.assertEqual(result['title'], 'HR Internship')
                self.assertEqual(result['country'], 'NL')
                self.assertEqual(result['city'], 'Amsterdam')
                self.assertEqual(result['employment'], expected)
                self.assertEqual(result['apply_url'], url)
                self.assertEqual(client.calls, [url])

    def test_unapproved_host_still_rejected_without_request(self):
        url = 'https://third-party.example/jobs/hr-intern'
        client = Pages(url, '')
        with self.assertRaisesRegex(ValueError, 'Unapproved employer-page host'):
            page_record({'url': url},
                        {'allowed_hosts': ['careers.example.com']}, client)
        self.assertEqual(client.calls, [])


if __name__ == '__main__':
    unittest.main()
