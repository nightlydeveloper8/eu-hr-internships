"""Small synthetic, no-network checks for SmartRecruiters policy-safe preflight."""
import unittest

from scripts.pilot_smartrecruiters_public import candidates, official_same_id_links, inspect_one, run
from collector.universal import Document


ID = '744000161490861'
URL = 'https://jobs.smartrecruiters.com/Salomon/' + ID + '-hr-intern'
TITLE = 'HR Internship'
SCRIPT = ('<script type="application/ld+json">{"@context":"https://schema.org",'
          '"@type":"JobPosting","title":"HR Internship","identifier":'
          '{"value":"' + ID + '"}}</script>')
FORM = ('<form id="job-apply"><input name="first_name"><input name="last_name">'
        '<input type="email" name="email"><input type="file" name="cv">'
        '<button type="submit">Apply</button></form>')
VACANCY = ('<html><h1>HR Internship</h1>' + SCRIPT +
           '<a href="' + URL + '/apply">Apply</a></html>').encode()
APPLICATION = ('<html><h1>HR Internship</h1>' + SCRIPT + FORM + '</html>').encode()


def record():
    return dict(id='abc', source_id='auto-salomon', title=TITLE,
                status='unverified', internship_type='internship',
                country='FR', url=URL, _target_id=ID, _tenant='Salomon')


class FakeClient:
    def __init__(self, mapping):
        self.mapping = mapping
        self.requests = 0
        self.bytes = 0
        self.redirect_scope_allowed = None
    def request(self, url, **kwargs):
        self.requests += 1
        if self.redirect_scope_allowed and not self.redirect_scope_allowed(url):
            raise ValueError('out-of-scope')
        body = self.mapping[url]
        self.bytes += len(body)
        return body, 200, url


class SmartRecruitersPreflightTests(unittest.TestCase):
    def test_only_reviewed_country_unverified_internships_selected(self):
        row = record()
        catalog = dict(jobs=[row, dict(row, id='b', country='NL'),
                             dict(row, id='c', status='closed'),
                             dict(row, id='d', internship_type='working-student')])
        selected = candidates(catalog)
        self.assertEqual([r['id'] for r in selected], ['abc'])

    def test_published_same_posting_cta_and_visible_form_is_candidate_only(self):
        client = FakeClient({URL: VACANCY, URL + '/apply': APPLICATION})
        result = inspect_one(record(), client)
        self.assertEqual(result['outcome'], 'same-id-visible-enabled-form-candidate')
        self.assertEqual(client.requests, 2)
        self.assertEqual(result['posting_id'], ID)

    def test_wrong_id_and_other_host_are_not_allowed(self):
        doc = Document(('<html><h1>HR Internship</h1>' + SCRIPT +
                        '<a href="/Salomon/744000161490862-other/apply">Apply</a>'
                        '<a href="https://evil.example.com/apply">Apply</a>'
                        '<a href="/Salomon/apply">Apply</a></html>').encode(), URL)
        self.assertEqual(official_same_id_links(doc, record()), [])

    def test_static_shell_is_not_verified(self):
        client = FakeClient({URL: b'<h1>HR Internship</h1><button>Apply</button>'})
        result = inspect_one(record(), client)
        self.assertEqual(result['outcome'], 'not-verified')
        self.assertEqual(result['reason'], 'no-unique-published-same-id-CTA')

    def test_bounded_batch_does_not_mark_catalog_verified(self):
        catalog = {'updated_at': '2026-11-17T08:00:00Z', 'jobs': [record()]}
        client = FakeClient({URL: VACANCY, URL + '/apply': APPLICATION})
        result = run(catalog, client)
        self.assertEqual(result['candidate_form_results'], 1)
        self.assertEqual(result['posts'], 0)
        self.assertEqual(catalog['jobs'][0]['status'], 'unverified')
        self.assertEqual(result['http_requests'], 2)
        with self.assertRaises(ValueError):
            run(catalog, FakeClient({}), max_positions=0)


if __name__ == '__main__':
    unittest.main()
