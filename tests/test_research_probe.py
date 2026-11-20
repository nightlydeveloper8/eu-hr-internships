import unittest
from scripts.probe_research_urls import probe


class ResearchProbeTests(unittest.TestCase):
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
