"""Offline checks for the enterprise staging access gate and JSON-LD evidence."""
import unittest
from unittest.mock import patch

from scripts.ats_enterprise_yield import (PublicClient, in_board, measure, retry_delay,
                                          robots_allows, robots_policy, sitemap_entries, staging_fields)


class AccessGateTests(unittest.TestCase):
    def test_robots_rejects_without_a_successful_read(self):
        client = PublicClient("example.avature.net")
        with self.assertRaisesRegex(ValueError, "robots"):
            client.get("https://example.avature.net/careers/sitemap.xml")
        self.assertEqual(client.requests, 0)

    def test_robots_keeps_specific_allow_and_applies_wildcard_disallow(self):
        rules, maps, delay = robots_policy("""User-agent: *
Disallow: /
Allow: /careers/
Disallow: /careers/*/private$
Crawl-delay: 10
Sitemap: https://example.avature.net/careers/sitemap.xml
""")
        self.assertEqual(delay, 10)
        self.assertEqual(len(maps), 1)
        self.assertTrue(robots_allows(rules, "/careers/jobdetail/2"))
        self.assertFalse(robots_allows(rules, "/careers/hr/private"))
        self.assertFalse(robots_allows(rules, "/internalcareers/"))

    def test_robots_failures_never_enable_content(self):
        client = PublicClient("example.avature.net")
        with patch.object(client, "get", return_value=b"<html>Just a moment</html>"):
            with self.assertRaisesRegex(ValueError, "returned HTML"):
                client.read_robots()
        self.assertIsNone(client.rules)

    def test_same_host_and_board_for_nested_sitemaps(self):
        host = "example.avature.net"
        self.assertTrue(in_board("avature", host, f"https://{host}/en_GB/careers/sitemap.xml", True))
        self.assertFalse(in_board("avature", host, f"https://{host}/internalcareers/sitemap.xml", True))
        self.assertFalse(in_board("avature", host, "https://other.avature.net/en_GB/careers/sitemap.xml", True))
        board = "x.wd3.myworkdayjobs.com/external"
        self.assertTrue(in_board("workday", board, "https://x.wd3.myworkdayjobs.com/External/siteMap.xml", True))
        self.assertFalse(in_board("workday", board, "https://x.wd3.myworkdayjobs.com/Internal/siteMap.xml", True))

    def test_retry_wait_never_shortens_retry_after(self):
        self.assertEqual(retry_delay("10"), 60)
        self.assertEqual(retry_delay("120"), 120)

    def test_cornerstone_checks_current_detail_after_robots(self):
        body = b'<script type="application/ld+json">{"@context":"https://schema.org","@type":"JobPosting","title":"HR intern"}</script>'
        url = "https://example.csod.com/ux/ats/careersite/4/home/requisition/15"
        with patch("scripts.ats_enterprise_yield.PublicClient") as client:
            agent = client.return_value
            agent.requests = 2
            agent.bytes = len(body)
            agent.get.return_value = body
            result = measure("cornerstone", "example.csod.com/4", "seed", [url])
        agent.read_robots.assert_called_once_with()
        agent.get.assert_called_once_with(url)
        self.assertEqual((result["state"], result["pages"]), ("ammesso", 1))

    def test_sitemap_entries_and_jobposting_fields(self):
        tag, links = sitemap_entries(b'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                                     b'<url><loc>https://example.test/job/1</loc></url></urlset>')
        self.assertEqual((tag, links), ("urlset", ["https://example.test/job/1"]))
        post = {"title": "HR Intern", "description": "HR internship for university students",
                "datePosted": "2026-11-22", "url": links[0], "directApply": True,
                "jobLocation": {"address": {"addressCountry": "IT"}}}
        result = staging_fields(post, "example.test")
        self.assertEqual(result["countries"], ["IT"])
        self.assertTrue(result["hr_stage"])
        self.assertFalse(result["application_link"])
        post["potentialAction"] = {"@type": "ApplyAction", "target": "https://example.test/job/1/apply"}
        self.assertTrue(staging_fields(post, "example.test")["application_link"])

    def test_summary_keeps_retry_costs_and_uses_latest_observations(self):
        import json
        from pathlib import Path
        from tempfile import TemporaryDirectory

        from scripts.ats_enterprise_yield import summarize_staging

        post = {"title": True, "date": True, "location": True, "application_link": False,
                "hr_stage": True, "countries": ["ES"]}
        first = {"tenant": "example", "state": "incerto", "pages": 0, "jobposting": [],
                 "get": 1, "bytes": 0, "seconds": 2}
        retry = dict(first, state="ammesso", pages=1, jobposting=[post], get=3, bytes=5)
        with TemporaryDirectory() as folder:
            stage = Path(folder)
            (stage / "workday-sample.json").write_text(json.dumps({"rows": [first], "population": 1}))
            (stage / "workday-sample-robots-rate-limit.json").write_text(json.dumps({"rows": [retry]}))
            result = summarize_staging(stage)
        workday = result["platforms"]["workday"]
        self.assertEqual((workday["sample"], workday["get"], workday["countries"]), (1, 4, {"ES": 1}))
        self.assertEqual(result["jsonld"]["fields"]["application_link"], 0)
