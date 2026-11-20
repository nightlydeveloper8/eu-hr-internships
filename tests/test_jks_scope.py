import unittest
from types import SimpleNamespace

from collector.jks import SOURCE, inventory, project_url, scope, source_gate, advertised_deadline
from collector.universal import Document
from collector.verification import expired
from collector.daily import provision
from collector.pipeline import ROOT, read


class JksScopeTests(unittest.TestCase):
    def test_registered_jks_is_disabled_and_daily_provision_does_not_enable_it(self):
        sources = read(ROOT / "data/sources.json", [])
        selected = [row for row in sources if row.get("id") == SOURCE["id"]]
        self.assertEqual(len(selected), 1)
        actual = selected[0]
        self.assertEqual(source_gate(actual), "staging")
        self.assertFalse(actual["enabled"])
        self.assertFalse(actual["rollout_approved"])
        self.assertTrue(actual["staging_only"])
        _, provisioned = provision(read(ROOT / "data/companies.json", []), sources)
        self.assertFalse(next(row for row in provisioned if row["id"] == SOURCE["id"])["enabled"])
        self.assertEqual(sum(bool(row.get("enabled")) for row in sources),
                         sum(bool(row.get("enabled")) for row in provisioned))

    def test_rollout_flag_alone_never_allows_collection_or_network(self):
        for change in ({"enabled": True},
                       {"enabled": True, "staging_only": False},
                       {"enabled": True, "staging_only": False, "rollout_approved": True},
                       {"allowed_hosts": ["www.jks.dk", "unapproved.example"]},
                       {"max_requests": 1000},
                       {"target_countries": ["SE"]}):
            with self.subTest(change=change):
                source = dict(SOURCE, **change)
                calls = []
                class NoNetwork:
                    def request(self, url):
                        calls.append(url)
                        raise AssertionError("Unapproved source attempted a GET")
                with self.assertRaises(ValueError):
                    inventory(source, NoNetwork())
                self.assertEqual(calls, [])
        approved = dict(SOURCE, enabled=True, staging_only=False, rollout_approved=True,
                        rollout_authorization="synthetic-only-test-approval")
        self.assertEqual(source_gate(approved), "production")

    def test_current_jks_expiry_is_inclusive_and_not_confused_with_slug_year(self):
        url = "https://www.jks.dk/jobs/praktikant-efteraar-2025-slagelse-156880"
        body = (b"<div>Udl\xc3\xb8ber:</div><div>25.11.26</div>"
                b"<main><h1>HR Praktikant</h1></main>"
                b"<aside>Udl\xc3\xb8ber: 25.11.26</aside>")
        deadline = advertised_deadline(Document(body, url))
        self.assertEqual(deadline, "2026-11-25")
        self.assertFalse(expired(deadline, "2026-11-25T18:00:00+00:00"))
        self.assertTrue(expired(deadline, "2026-11-26T00:00:00+00:00"))
        for html in (
            b"<main><h1>HR Praktikant</h1></main>",
            b"<p>Udlober: 25.11.26</p>",
            b"<p>Udl\xc3\xb8ber: 25.11.26</p><p>Udl\xc3\xb8ber: 26.11.26</p>",
            b"<p>Udl\xc3\xb8ber: 31.02.27</p>",
        ):
            with self.subTest(html=html):
                with self.assertRaises(ValueError):
                    advertised_deadline(Document(html, url))

    def test_talentech_requires_the_employer_and_exact_project(self):
        url = "https://candidate.hr-manager.net/ApplicationInit.aspx?cid=1601&ProjectId=160886"
        self.assertTrue(project_url(url, "160886"))
        for changed in [url.replace("1601&", "1602&"), url.replace("160886", "160885"),
                        url.replace("Init.aspx", "Other.aspx"), url + "&projectid=160885",
                        url + "&next=https://example.org", url.replace("hr-manager.net", "example.org")]:
            with self.subTest(changed=changed):
                self.assertFalse(project_url(changed, "160886"))

    def test_scopes_intersect_and_restore_on_failure(self):
        permitted = lambda url: url.startswith("https://www.jks.dk/")
        client = SimpleNamespace(redirect_scope_allowed=permitted)
        inside = "https://www.jks.dk/jobs/example-160886"
        with self.assertRaises(ValueError):
            with scope(client, lambda url: url == inside):
                self.assertTrue(client.redirect_scope_allowed(inside))
                self.assertFalse(client.redirect_scope_allowed("https://www.jks.dk/other"))
                self.assertFalse(client.redirect_scope_allowed("https://candidate.hr-manager.net/robots.txt"))
                raise ValueError("stopped")
        self.assertIs(client.redirect_scope_allowed, permitted)
