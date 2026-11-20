import unittest
from types import SimpleNamespace

from collector.jks import project_url, scope


class JksScopeTests(unittest.TestCase):
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
