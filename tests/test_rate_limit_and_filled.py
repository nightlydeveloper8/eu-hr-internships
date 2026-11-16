"""Offline regression tests: 429 host circuit and visible filled-vacancy evidence."""
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

from collector.adapters import Client
from collector.applications import ApplicationClosed
from collector.runtime import BudgetClient, _RATE_LIMITED_HOSTS
from collector.verification import verify_vacancy


class RateLimitedHostTests(unittest.TestCase):
    hosts = ("stop-429.test", "redirect-429.test", "other-429.test", "robots-429.test")

    def setUp(self):
        _RATE_LIMITED_HOSTS.difference_update(self.hosts)

    def tearDown(self):
        _RATE_LIMITED_HOSTS.difference_update(self.hosts)

    def test_first_429_stops_subsequent_urls_and_other_clients_without_new_requests(self):
        first = "https://stop-429.test/jobs/1"
        later = "https://stop-429.test/jobs/2"
        other = "https://other-429.test/jobs/1"
        calls = []

        def response(_client, url, **kwargs):
            calls.append(url)
            if url == first:
                raise HTTPError(url, 429, "Too Many Requests", None, None)
            return b"ok", 200, url

        with patch.object(Client, "request", response):
            client = BudgetClient(seconds=10, max_requests=6, delay=0)
            with self.assertRaises(HTTPError) as first_error:
                client.request(first, robots=False)
            self.assertEqual(first_error.exception.code, 429)
            with self.assertRaises(HTTPError) as skipped:
                client.request(later, robots=False)
            self.assertEqual(skipped.exception.code, 429)
            self.assertEqual(client.rate_limited_skips, 1)
            self.assertEqual(client.requests, 1)
            self.assertEqual(calls, [first])

            # A new employer client in the same collection process should not
            # retry this host, while an unrelated host continues normally.
            second_client = BudgetClient(seconds=10, max_requests=3, delay=0)
            with self.assertRaises(HTTPError):
                second_client.request(later, robots=False)
            self.assertEqual(second_client.requests, 0)
            self.assertEqual(second_client.rate_limited_skips, 1)
            self.assertEqual(second_client.request(other, robots=False), (b"ok", 200, other))
            self.assertEqual(calls, [first, other])

    def test_redirect_429_quarantines_only_the_host_that_answered(self):
        origin = "https://other-429.test/jobs/3"
        blocked = "https://redirect-429.test/jobs/9"
        calls = []

        def response(_client, url, **kwargs):
            calls.append(url)
            if len(calls) == 1:
                raise HTTPError(blocked, 429, "Too Many Requests", None, None)
            return b"ok", 200, url

        with patch.object(Client, "request", response):
            client = BudgetClient(seconds=10, max_requests=5, delay=0)
            with self.assertRaises(HTTPError):
                client.request(origin, robots=False)
            with self.assertRaises(HTTPError):
                client.request(blocked, robots=False)
            self.assertEqual(client.request(origin, robots=False), (b"ok", 200, origin))
            self.assertEqual(calls, [origin, origin])

    def test_non_429_failure_does_not_quarantine_host(self):
        url = "https://other-429.test/jobs/10"
        calls = []

        def response(_client, u, **kwargs):
            calls.append(u)
            if len(calls) == 1:
                raise HTTPError(u, 503, "Unavailable", None, None)
            return b"ok", 200, u

        with patch.object(Client, "request", response):
            client = BudgetClient(seconds=10, max_requests=3, delay=0)
            with self.assertRaises(HTTPError) as error:
                client.request(url, robots=False)
            self.assertEqual(error.exception.code, 503)
            self.assertEqual(client.request(url, robots=False), (b"ok", 200, url))
            self.assertEqual(calls, [url, url])

    def test_robots_429_also_stops_following_urls(self):
        class Server:
            calls = []

            def open(self, request, timeout):
                self.calls.append(request.full_url)
                raise HTTPError(request.full_url, 429, "Too Many Requests", None, None)

        server = Server()
        with patch("collector.adapters.build_opener", return_value=server):
            client = BudgetClient(seconds=10, max_requests=4, delay=0)
            with self.assertRaisesRegex(ValueError, "robots.txt unavailable: 429"):
                client.request("https://robots-429.test/jobs/1")
            attempted = list(server.calls)
            self.assertEqual(attempted, ["https://robots-429.test/robots.txt"])
            with self.assertRaises(HTTPError) as error:
                client.request("https://robots-429.test/jobs/2")
            self.assertEqual(error.exception.code, 429)
            self.assertEqual(server.calls, attempted)
            self.assertEqual(client.rate_limited_skips, 1)


class FilledVacancyTests(unittest.TestCase):
    def test_visible_electrolux_filled_message_overrides_stale_json_ld(self):
        import json
        url = "https://example.org/jobs/JR81378"
        title = "HR Project Management Intern"
        record = dict(source_id="electrolux-probe", external_id="JR81378",
                      posting_identifier="JR81378", employer="Electrolux Group",
                      title=title, text="HR project management internship",
                      url=url, apply_url=url, inventory_evidence="current-employer-feed")
        source = dict(id="electrolux-probe", employer="Electrolux Group",
                      adapter="universal-employer", allowed_hosts=["example.org"])
        posting = {"@context": "https://schema.org", "@type": "JobPosting",
                   "title": title, "identifier": {"value": "JR81378"},
                   "validThrough": "2026-12-16T00:00:00Z"}
        html = ('<h1>' + title + '</h1><p>We\'re sorry… The job you are trying '
                'to apply for has been filled. Explore other jobs here</p>'
                '<script type="application/ld+json">' + json.dumps(posting) + '</script>')

        class Pages:
            calls = 0

            def request(self, requested, **kwargs):
                self.calls += 1
                return html.encode(), 200, requested

        client = Pages()
        with self.assertRaises(ApplicationClosed):
            verify_vacancy(record, source, client, "2026-11-16T12:00:00+00:00")
        self.assertEqual(client.calls, 1)

    def test_regular_open_ad_does_not_trigger_filled_phrase(self):
        from collector.universal import Document
        from collector.applications import ensure_open_document
        doc = Document(b"<h1>HR Intern</h1><p>We have filled many positions in the past.</p>",
                       "https://example.org/jobs/hr")
        ensure_open_document(doc)


if __name__ == "__main__":
    unittest.main()
