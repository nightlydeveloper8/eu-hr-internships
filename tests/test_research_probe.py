import unittest
from scripts.probe_research_urls import probe
from collector.runtime import CollectionBudgetExceeded


class ResearchProbeTests(unittest.TestCase):
    def test_exhausted_shared_budget_stops_all_hosts(self):
        class Client:
            calls = []
            def request(self, url):
                self.calls.append(url)
                raise CollectionBudgetExceeded('Time budget exhausted')
        c = Client()
        rows = probe(['https://first.example/a', 'https://other.example/a',
                      'https://first.example/b'], c)
        self.assertEqual(c.calls, ['https://first.example/a'])
        self.assertEqual([r['status'] for r in rows],
                         ['unread', 'skipped-budget', 'skipped-budget'])
        self.assertTrue(all(r['reason'] == 'Time budget exhausted' for r in rows))

    def test_non_budget_error_does_not_close_other_hosts(self):
        class Client:
            def request(self, url):
                if 'first.example' in url:
                    raise ValueError('Malformed public response')
                return b'public', 200, url
        rows = probe(['https://first.example/a', 'https://other.example/a'], Client())
        self.assertEqual([r['status'] for r in rows], ['unread', 200])

    def test_blocked_host_is_not_retried_and_other_host_can_continue(self):
        class Client:
            calls = []
            def request(self, url):
                self.calls.append(url)
                if 'blocked.example' in url:
                    raise ValueError('robots.txt unavailable: 403')
                return b'public', 200, url
        c = Client()
        rows = probe(['https://blocked.example/a', 'https://blocked.example/b',
                      'https://other.example/a', 'https://other.example/a'], c)
        self.assertEqual(c.calls, ['https://blocked.example/a', 'https://other.example/a'])
        self.assertEqual([r['status'] for r in rows], ['unread', 'skipped-host', 200])
        self.assertIn('sha256', rows[-1])

    def test_invalid_protocol_never_reaches_client(self):
        class Client:
            def request(self, url):
                raise AssertionError('Must not request invalid URL')
        with self.assertRaisesRegex(ValueError, 'HTTPS'):
            probe(['http://example.org/a'], Client())
