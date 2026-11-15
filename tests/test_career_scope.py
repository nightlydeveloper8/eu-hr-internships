"""Offline regressions for malformed attributes and persisted career referrals."""
import json
import tempfile
import unittest
from unittest.mock import patch

from collector.runtime import PageCache
from collector.universal import Crawler, Document
from tests.test_all_employers import FakeClient, posting, source


class CareerScopeTests(unittest.TestCase):
    def test_valueless_presentation_attributes_do_not_destroy_job_content(self):
        body = b'''<main class><h1>HR Intern</h1><p data-icon>Apply</p>
          <div itemprop>Internship in Amsterdam</div><a href="/jobs/1" rel>Vacancy</a></main>'''
        doc = Document(body, 'https://example.org')
        self.assertEqual(doc.h1, ['HR Intern'])
        self.assertIn('Internship in Amsterdam', doc.text)
        self.assertEqual(doc.links, [['/jobs/1', ' Vacancy', '']])

    def test_current_checkpoint_cannot_authorize_external_seed_or_pending(self):
        scoped = dict(source(), ownership_scope='reviewed-hosts')
        external = 'https://third.recruitee.com'
        job = 'https://example.org/jobs/1'
        state = dict(ownership_policy_version=1, allowed_hosts=['third.recruitee.com'],
                     preferred_career_url=external,
                     pending=[dict(url=external+'/o/hr', job=True, depth=0)])
        # Exercise a second cycle using the checkpoint actually saved by the first.
        with tempfile.TemporaryDirectory() as folder, patch.dict('os.environ', {'COLLECTOR_CACHE_DIR': folder}):
            PageCache(scoped['id']).save_state(state)
            for cycle in range(2):
                client = FakeClient({'https://example.org': '<a href="/jobs/1">HR Intern</a>',
                                     job: '<script type="application/ld+json">'+json.dumps(posting())+'</script>',
                                     external: '<h1>External referral</h1>'})
                rows = Crawler(scoped, client).run()
                self.assertEqual(set(client.calls), {'https://example.org', job} if cycle==0 else {'https://example.org'})
                self.assertEqual(len(rows), 1)
                self.assertEqual(rows.stats['allowed_hosts'], ['example.org'])
                self.assertFalse(rows.stats['closure_complete'])
            saved = PageCache(scoped['id']).state()
            self.assertNotIn('third.recruitee.com', saved['allowed_hosts'])

    def test_redirect_does_not_grant_new_host_or_extract_external_jobs(self):
        scoped = dict(source(), ownership_scope='reviewed-hosts')
        class Redirect(FakeClient):
            def request(self, url, **kwargs):
                self.calls.append(url)
                return ('<script type="application/ld+json">'+json.dumps(
                    posting(hiringOrganization={'name': 'Example'}))+'</script>').encode(), 200, 'https://third.example/jobs/1'
        with tempfile.TemporaryDirectory() as folder, patch.dict('os.environ', {'COLLECTOR_CACHE_DIR': folder}):
            client = Redirect({})
            rows = Crawler(scoped, client).run()
            self.assertEqual(list(rows), [])
            self.assertNotIn('third.example', rows.stats['allowed_hosts'])
            self.assertFalse(rows.stats['complete'])

    def test_explicitly_reviewed_other_host_remains_usable(self):
        scoped = dict(source(), ownership_scope='reviewed-hosts',
                      allowed_hosts=['example.org', 'careers.example.net'],
                      start_urls=['https://careers.example.net/jobs/1'])
        body = '<script type="application/ld+json">'+json.dumps(posting(hiringOrganization={'name': 'Example'}))+'</script>'
        with tempfile.TemporaryDirectory() as folder, patch.dict('os.environ', {'COLLECTOR_CACHE_DIR': folder}):
            rows = Crawler(scoped, FakeClient({scoped['start_urls'][0]: body})).run()
            self.assertEqual(len(rows), 1)
            self.assertFalse(rows.stats['closure_complete'])


if __name__ == '__main__':
    unittest.main()
