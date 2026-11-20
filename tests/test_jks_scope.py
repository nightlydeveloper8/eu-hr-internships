import unittest
from types import SimpleNamespace

from collector.jks import SOURCE, inventory, project_url, scope, source_gate
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

    def test_broader_current_index_recovers_other_cities_without_dropping_originals(self):
        # The large country board is read once, but matching projects are
        # capped. The first three previously reviewed indexes retain priority.
        original = [
            ("157063", "praktikant-til-hr-og-rekruttering-hos-jks-vejle", "Vejle"),
            ("156880", "praktikant-til-hr-og-rekruttering-hos-jks-slagelse", "Slagelse"),
            ("160886", "praktikant-til-hr-og-rekruttering-hos-jks-esbjerg", "Esbjerg"),
            ("160782", "praktikant-til-hr-og-rekruttering-hos-jks-odense", "Odense"),
        ]
        new = [
            ("160605", "praktikant-til-hr-og-rekruttering-hos-jks-randers", "Randers"),
            ("160539", "praktikant-til-hr-og-rekruttering-hos-jks-frederikshavn", "Frederikshavn"),
            ("160534", "praktikant-til-hr-og-rekruttering-hos-jks-hobro", "Hobro"),
        ]
        pages = {}
        def link(item):
            project, slug, _ = item
            url = f"https://www.jks.dk/jobs/{slug}-{project}"
            pages[url] = (f"<main><h1>Praktikant til HR og rekruttering hos JKS {item[2]}</h1>"
                          f"<p>HR rekruttering - {item[2]}</p></main>").encode()
            return f"<a href='{url}'>Se jobopslag</a>"
        from collector.jks import INDEXES, MAX_PROJECTS
        nationwide = '<a href="/jobs/praktikanter-til-hr-og-rekrutteringsopgaver-jks-i-hele-danmark-159170">National</a>'
        for index, rows in zip(INDEXES, [original[:2], original[2:3], original[3:4], new]):
            pages[index] = ("<html>" + "".join(link(row) for row in rows)
                            + (nationwide if index == INDEXES[0] else "") + "</html>").encode()
        class FakeClient:
            def __init__(self):
                self.requests = 0
                self.redirect_scope_allowed = None
            def request(self, url, **kwargs):
                if self.redirect_scope_allowed and not self.redirect_scope_allowed(url):
                    raise AssertionError("A page outside the reviewed scope was requested")
                self.requests += 1
                if url not in pages:
                    raise AssertionError("Unexpected GET " + url)
                return pages[url], 200, url
        client = FakeClient()
        entries = inventory(dict(SOURCE), client)
        ids = [row["external_id"] for row in entries]
        self.assertEqual(ids, [p[0] for p in (original + new[:2])])
        self.assertEqual(len(ids), MAX_PROJECTS)
        self.assertIn("160534", entries.stats["deferred_projects"])
        self.assertIn("159170", entries.stats["unresolved_projects"])
        self.assertFalse(entries.stats["closure_complete"])
        self.assertEqual(client.requests, len(INDEXES) + MAX_PROJECTS)
        self.assertLessEqual(client.requests + 2 * MAX_PROJECTS + 2, SOURCE["max_requests"])

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
