"""Offline regressions for the second, employer-internal SmartWays tenant."""
import unittest
from scripts.preview_internal_recruitee import (
    BASE, HOST, REVIEWED_CAREERS_HOST, SOURCE, allowed, employer_board, employer_legal_identity,
    LEGAL_URL, reviewed_source, ReadOnlyClient
)
from collector.classify import classify_role
from collector.recruitee_alias import reconcile, same_path_redirect


class AliasResolutionTests(unittest.TestCase):
    def test_only_live_same_path_aliases_with_published_application_survive(self):
        class Client:
            def __init__(self, adversarial=None):
                self.calls = []
                self.adversarial = adversarial
            def request(self, url):
                self.calls.append(url)
                if self.adversarial and url.endswith(self.adversarial[0]):
                    return b"", 200, self.adversarial[1]
                return b"<html>SmartWays</html>", 200, url.replace(
                    "careers.smartways.io", "smartways.recruitee.com")
        source = dict(SOURCE)
        row = dict(title="Recruitment Internship Programme (paid)",
                   text="Our recruitment team", employment="",
                   countries=["PL"], url="https://careers.smartways.io/o/recruitment-internship-programme-paid",
                   apply_url="https://careers.smartways.io/o/recruitment-internship-programme-paid",
                   observed_application_url="https://careers.smartways.io/o/recruitment-internship-programme-paid/c/new")
        fake = Client()
        resolved = reconcile(source, fake, [row])
        self.assertEqual(len(fake.calls), 2)
        self.assertEqual(resolved[0]["url"], "https://smartways.recruitee.com/o/recruitment-internship-programme-paid")
        self.assertEqual(resolved[0]["observed_application_url"],
                         resolved[0]["url"] + "/c/new")
        for bad in ("https://jobs.smartways.io/o/recruitment-internship-programme-paid",
                    "https://careers.smartways.io/o/another-job",
                    "https://malicious.example/o/recruitment-internship-programme-paid"):
            # A different host or vacancy cannot be accepted as the redirect result.
            client = Client(("/o/recruitment-internship-programme-paid",
                             bad))
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                same_path_redirect(client, row["url"])
        no_app = dict(row, observed_application_url=None)
        with self.assertRaises(ValueError):
            reconcile(source, Client(), [no_app])
        skip = dict(row,title="Marketing & Sales Internship Programme (paid)")
        no_get = Client()
        self.assertEqual(reconcile(source, no_get, [skip])[0]["url"], skip["url"])
        self.assertEqual(no_get.calls, [])

class InternalRecruiteeTests(unittest.TestCase):
    def test_new_internal_board_is_not_the_previous_client_vacancy_board(self):
        self.assertEqual(SOURCE["allowed_hosts"], ["smartways.recruitee.com", "careers.smartways.io"])
        self.assertNotIn("jobs.smartways.io", SOURCE["allowed_hosts"])
        self.assertFalse(SOURCE["enabled"])
        self.assertTrue(reviewed_source(dict(SOURCE)))
        for change in (
            {"enabled": True}, {"allowed_hosts": [HOST, "jobs.smartways.io"]},
            {"feed_url": "https://jobs.smartways.io/api/offers/"},
            {"max_requests": 200}, {"collection_seconds": 1000},
            {"reviewed_recruitee_alias": "unreviewed-tenant"},
            {"target_countries": ["NL"]}, {"application_check": None}
        ):
            with self.subTest(change=change):
                with self.assertRaises(ValueError):
                    reviewed_source(dict(SOURCE, **change))

    def test_read_only_scope_rejects_external_redirects_and_application_posts(self):
        self.assertTrue(allowed(BASE + "/api/offers/"))
        self.assertTrue(allowed(BASE + "/o/recruitment-internship-programme-paid"))
        self.assertTrue(allowed(BASE + "/o/recruitment-internship-programme-paid/c/new"))
        self.assertTrue(allowed(BASE + "/robots.txt"))
        self.assertTrue(allowed("https://" + REVIEWED_CAREERS_HOST
                                + "/o/recruitment-internship-programme-paid"))
        self.assertTrue(allowed("https://" + REVIEWED_CAREERS_HOST
                                + "/o/recruitment-internship-programme-paid/c/new"))
        self.assertFalse(allowed("https://" + REVIEWED_CAREERS_HOST + "/api/offers/"))
        self.assertTrue(allowed(LEGAL_URL))
        for target in (
            "https://jobs.smartways.io/api/offers/",
            BASE + "/api/offers/?next=https://other.example",
            BASE + "/admin/jobs",
            "http://smartways.recruitee.com/api/offers/",
            "https://other.example/o/recruitment-internship-programme-paid"
        ):
            self.assertFalse(allowed(target), target)
        client = ReadOnlyClient(dict(SOURCE))
        before = client.requests
        with self.assertRaises(ValueError):
            client.request(BASE + "/o/test/c/new", method="POST")
        self.assertEqual(client.requests, before)

    def test_tenant_and_independent_legal_ownership_must_match(self):
        html = b'<h1>SmartWays</h1>'
        self.assertTrue(employer_board(html, BASE + "/"))
        with self.assertRaises(ValueError):
            employer_board(b'<h1>Other company</h1>', BASE + "/")
        with self.assertRaises(ValueError):
            employer_board(html, "https://jobs.smartways.io/")
        legal = ("SmartWays spółka z ograniczoną odpowiedzialnością "
                 "NIP 6793137813").encode()
        self.assertTrue(employer_legal_identity(legal, LEGAL_URL))
        for body, url in (
            (b"Other company NIP 6793137813", LEGAL_URL),
            (b"SmartWays sp. z o.o. NIP 1234567890", LEGAL_URL),
            (legal, "https://jobs.smartways.io/privacy-policy"),
        ):
            with self.subTest(body=body, url=url):
                with self.assertRaises(ValueError):
                    employer_legal_identity(body, url)

    def test_recruiting_programme_qualifies_but_sales_programme_does_not(self):
        role = classify_role("Recruitment Internship Programme (paid)")
        self.assertIsNotNone(role)
        self.assertEqual(role["internship_type"], "internship")
        self.assertIn("talent-acquisition", role["categories"])
        self.assertIsNone(classify_role("Marketing & Sales Internship Programme (paid)"))
        self.assertIsNone(classify_role("Senior IT Recruitment Consultant"))


if __name__ == "__main__":
    unittest.main()
