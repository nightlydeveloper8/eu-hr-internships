"""Offline regressions for the second, employer-internal SmartWays tenant."""
import unittest
from scripts.preview_internal_recruitee import (
    BASE, HOST, SOURCE, allowed, employer_board, reviewed_source, ReadOnlyClient
)
from collector.classify import classify_role


class InternalRecruiteeTests(unittest.TestCase):
    def test_new_internal_board_is_not_the_previous_client_vacancy_board(self):
        self.assertEqual(SOURCE["allowed_hosts"], ["smartways.recruitee.com"])
        self.assertNotIn("jobs.smartways.io", SOURCE["allowed_hosts"])
        self.assertFalse(SOURCE["enabled"])
        self.assertTrue(reviewed_source(dict(SOURCE)))
        for change in (
            {"enabled": True}, {"allowed_hosts": [HOST, "jobs.smartways.io"]},
            {"feed_url": "https://jobs.smartways.io/api/offers/"},
            {"max_requests": 200}, {"collection_seconds": 1000},
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

    def test_live_tenant_must_name_company_and_link_corporate_site(self):
        html = b'<h1>SmartWays</h1><a href="https://www.smartways.io/">Company website</a>'
        self.assertTrue(employer_board(html, BASE + "/"))
        with self.assertRaises(ValueError):
            employer_board(b'<h1>SmartWays</h1>', BASE + "/")
        with self.assertRaises(ValueError):
            employer_board(html, "https://jobs.smartways.io/")

    def test_recruiting_programme_qualifies_but_sales_programme_does_not(self):
        role = classify_role("Recruitment Internship Programme (paid)")
        self.assertIsNotNone(role)
        self.assertEqual(role["internship_type"], "internship")
        self.assertIn("talent-acquisition", role["categories"])
        self.assertIsNone(classify_role("Marketing & Sales Internship Programme (paid)"))
        self.assertIsNone(classify_role("Senior IT Recruitment Consultant"))


if __name__ == "__main__":
    unittest.main()
