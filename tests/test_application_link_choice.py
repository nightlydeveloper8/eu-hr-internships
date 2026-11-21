"""Among several observed calls to action, follow the one carrying the vacancy identity."""
import unittest
from collector.verification import verify_vacancy

VACANCY = 'https://careers.example.com/en/job/dusseldorf/werkstudent-hr/256058'
GENERIC = 'https://careers.example.com/en/get-ready-to-apply'
SPECIFIC = 'https://careers-apply.example.com/job/Applicationmethods?jobId=256058'
FORM = b'<h1>Werkstudent HR</h1><form id="application"><input name="name"><input type="email"><input name="cv" type="file"><button>Apply</button></form>'


def verify(links, allowed=('careers.example.com', 'careers-apply.example.com'), form=FORM):
    page = ('<h1>Werkstudent HR</h1>' + ''.join(f'<a href="{u}">Apply now</a>' for u in links)).encode()
    calls = []

    class Client:
        def request(self, url):
            calls.append(url)
            if url == VACANCY:
                return page, 200, url
            return (form if url == SPECIFIC else b'<h1>How to apply</h1><p>General advice</p>'), 200, url
    proof = verify_vacancy(dict(url=VACANCY, title='Werkstudent HR', posting_identifier='256058'),
                           dict(id='not-a-pilot', allowed_hosts=list(allowed)), Client(), '2026-11-18T10:00:00+00:00')
    return proof, calls


class ApplicationLinkChoiceTests(unittest.TestCase):
    def test_generic_first_link_no_longer_hides_the_matching_application(self):
        proof, calls = verify([GENERIC, SPECIFIC])
        self.assertEqual(proof['url'], SPECIFIC)
        self.assertEqual(proof['method'], 'linked-same-vacancy-applicant-form')
        self.assertNotIn(GENERIC, calls)

    def test_identity_rule_is_unchanged(self):
        with self.assertRaisesRegex(ValueError, 'lacks a matching vacancy identifier'):
            verify([GENERIC, SPECIFIC.replace('256058', '256059')])
        with self.assertRaisesRegex(ValueError, 'lacks a matching vacancy identifier'):
            verify([GENERIC])
        with self.assertRaises(ValueError):  # unapproved host is never followed
            verify([GENERIC, SPECIFIC], allowed=('careers.example.com',))

    def test_form_gate_still_applies_to_the_chosen_link(self):
        with self.assertRaises(ValueError):
            verify([GENERIC, SPECIFIC], form=FORM.replace(b'<button>', b'<button disabled>'))


if __name__ == '__main__':
    unittest.main()
