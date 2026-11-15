"""Observed Workday requisition IDs bridge URLs but never replace application proof."""
import unittest
from collector.verification import shares_identifier, verify_vacancy


class WorkdayIdentifierTests(unittest.TestCase):
    vacancy = 'https://example.org/vacatures/stage-hr/JR123/'
    application = 'https://tenant.myworkdayjobs.com/Board/job/Resort/Stage-HR_JR123/apply'

    def test_exact_known_id_in_workday_apply_path_only(self):
        record = dict(url=self.vacancy, posting_identifier='JR123')
        self.assertTrue(shares_identifier(record, self.application))
        for target in [self.application.replace('JR123', 'JR1234'),
                       self.application.replace('JR123', 'JR0123'),
                       self.application.replace('/apply', '/search'),
                       self.application.replace('tenant.myworkdayjobs.com', 'tenant.myworkdayjobs.com.evil.org')]:
            with self.subTest(target=target):
                self.assertFalse(shares_identifier(record, target))
        self.assertFalse(shares_identifier(dict(url=self.vacancy), self.application))

    def verify(self, body, allowed=True):
        vacancy = self.vacancy
        app = self.application
        page = ('<main><h1>Stage HR</h1><script type="application/ld+json">'
                '{"@type":"JobPosting","title":"Stage HR","identifier":{"value":"JR123"}}'
                '</script><a href="' + app + '">Solliciteer nu</a></main>').encode()

        class Client:
            def request(self, url, **kwargs):
                return (page if url.rstrip('/') == vacancy.rstrip('/') else body), 200, url

        hosts = ['example.org'] + (['tenant.myworkdayjobs.com'] if allowed else [])
        return verify_vacancy(dict(url=vacancy, title='Stage HR'),
                              dict(id='not-a-pilot', allowed_hosts=hosts), Client(),
                              '2026-11-13T01:00:00+00:00')

    def test_spa_response_never_establishes_application(self):
        with self.assertRaises(ValueError):
            self.verify(b'{"widget":"redirect","externalSpa":true}')

    def test_host_title_and_enabled_form_are_still_required(self):
        body = b'<main><h1>Stage HR</h1><form><input name="first_name"><input name="email"><input type="file" name="cv"><button type="submit">Apply</button></form></main>'
        with self.assertRaises(ValueError):
            self.verify(body, allowed=False)
        with self.assertRaises(ValueError):
            self.verify(body.replace(b'<h1>Stage HR', b'<h1>Stage Finance'))
        with self.assertRaises(ValueError):
            self.verify(body.replace(b'type="submit"', b'type="submit" disabled'))
        self.assertEqual(self.verify(body)['url'], self.application)


if __name__ == '__main__':
    unittest.main()
