"""Offline checks for enterprise career-board identity and scan coverage."""
import unittest
from unittest.mock import Mock

from scripts.ats_enterprise_discovery import enumerate_enterprise, identity


class EnterpriseDiscoveryTests(unittest.TestCase):
    def test_workday_paths_distinguish_sites_but_not_locales(self):
        host = "example.wd3.myworkdayjobs.com"
        self.assertEqual(identity("workday", f"https://{host}/it-IT/Example_Careers/job/Rome/R1"),
                         f"{host}/example_careers")
        self.assertEqual(identity("workday", f"https://{host}/example_careers"), f"{host}/example_careers")
        self.assertEqual(identity("workday", f"https://{host}/external"), f"{host}/external")
        self.assertIsNone(identity("workday", f"https://{host}/wday/cxs/example/external/jobs"))
        self.assertEqual(identity("workday", "https://wd3.myworkdaysite.com/recruiting/example/External"),
                         "wd3.myworkdaysite.com/recruiting/example/external")

    def test_successfactors_shared_host_requires_company(self):
        host = "career5.successfactors.eu"
        self.assertEqual(identity("successfactors", f"https://{host}/career?company=BMWAG&lang=en_DE"),
                         f"{host}/career/bmwag")
        self.assertIsNone(identity("successfactors", f"https://{host}/career?lang=en_DE"))
        self.assertIsNone(identity("successfactors", f"https://{host}/career?company=a&company=b"))

    def test_platform_routes(self):
        examples = [
            ("oracle", "https://x.fa.us2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX/job/7",
             "x.fa.us2.oraclecloud.com/cx"),
            ("taleo", "https://x.taleo.net/careersection/2/jobdetail.ftl?job=123", "x.taleo.net/2"),
            ("avature", "https://x.avature.net/careers/JobDetail/1", "x.avature.net"),
            ("cornerstone", "https://x.csod.com/ux/ats/careersite/4/home?c=x", "x.csod.com/4"),
            ("icims", "https://jobs-x.icims.com/jobs/123/title/job", "jobs-x.icims.com"),
            ("phenom", "https://careers.phenom.com/global/en/job/12/Example", "careers.phenom.com"),
        ]
        for provider, url, key in examples:
            with self.subTest(provider=provider):
                self.assertEqual(identity(provider, url), key)
        self.assertIsNone(identity("oracle", "https://oraclecloud.com.example.org/hcmUI/CandidateExperience/sites/CX"))
        self.assertIsNone(identity("cornerstone", "https://x.csod.com/ui/lms-learning-details/"))
        self.assertIsNone(identity("taleo", "https://x.taleo.net/careersection/2026PRD.1.2/help/"))
        self.assertIsNone(identity("taleo", "https://x.taleo.net/careersection/application.jss"))

    def test_partition_scan_tracks_missing_metadata_and_distinct_sites(self):
        index = Mock()
        index.parquet.return_value = [("https://x.wd3.myworkdayjobs.com/en-US/External/job/1",),
                                      ("https://x.wd3.myworkdayjobs.com/External",)]
        files = [{"path": "inside", "bounds": ["com,myworkdayjobs,x", "com,myworkdayjobs,z"]},
                 {"path": "outside", "bounds": ["a", "b"]},
                 {"path": "unknown", "error": "missing"}]
        seen, reports = enumerate_enterprise(index, {"crawl": files}, ["workday"])
        self.assertEqual(dict(seen), {("workday", "x.wd3.myworkdayjobs.com/external"): {"crawl"}})
        self.assertEqual([(row["ranges"], row["failures"]) for row in reports], [(1, 1)])
