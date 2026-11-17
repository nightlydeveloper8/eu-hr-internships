"""Offline safety and idempotence regression for a single live Jobandtalent pilot."""
import json
import unittest

from scripts.pilot_jobandtalent_two_cycles import run, HOST, INVENTORY, ATS_ID, JOBTECH_ID

TITLE = "Praktik inom HR och rekrytering i Malmö - våren 2027"
PARENT = "https://" + HOST + "/jobs/8503489-praktik-inom-hr-och-rekrytering-i-malmo-varen-2027"
APP = PARENT + "/applications/new?promotion=2231065-arbetsformedlingen"
LEGAL = "https://" + HOST + "/privacy-policy"


def feed_record():
    return dict(id=int(JOBTECH_ID), headline=TITLE,
                description={"text": "Praktik inom HR och rekrytering."},
                employer={"name": "Jobandtalent Sweden AB"},
                workplace_address={"country": "Sverige", "municipality": "Malmö"},
                webpage_url="https://arbetsformedlingen.se/platsbanken/annonser/"+JOBTECH_ID,
                application_details={"url": APP}, publication_date="2026-11-16")


class Discovery:
    def __init__(self, hits=None):
        self.requests = 0
        self.bytes = 0
        self.hits = [feed_record()] if hits is None else hits
    def json(self, url):
        self.requests += 1
        out = dict(hits=self.hits)
        self.bytes += len(json.dumps(out).encode())
        return out


class ATS:
    calls = 0
    legal_text = b"<main>Personuppgiftsansvarig Jobandtalent Sweden AB</main>"
    def __init__(self, seconds, max_requests, delay):
        self.requests = self.bytes = 0
        self.redirect_scope_allowed = None
    def request(self, url, **kwargs):
        self.requests += 1
        type(self).calls += 1
        pages = {
            PARENT: (f"<main><h1>{TITLE}</h1><p>Plats: Malmö, Hyllie</p>"
                     f"<a href='{APP}'>Ansök</a></main>").encode(),
            APP: (f"<main><h1>{TITLE}</h1><a href='{LEGAL}'>Privacy Policy</a>"
                  "<form><input name='full_name'>"
                  "<input name='email' type='email'><input name='cv' type='file'>"
                  "<button type='submit'>Apply</button></form></main>").encode(),
            LEGAL: self.legal_text,
            INVENTORY: (f"<html><a href='/jobs/8503489-praktik-inom-hr-och-rekrytering-i-malmo-varen-2027'>"
                        f"{TITLE}</a></html>").encode(),
        }
        if url not in pages or (self.redirect_scope_allowed and not self.redirect_scope_allowed(url)):
            raise ValueError("Unauthorized ATS request")
        body = pages[url]
        self.bytes += len(body)
        return body, 200, url


class TwoCyclePilotTests(unittest.TestCase):
    def setUp(self):
        ATS.legal_text = b"<main>Personuppgiftsansvarig Jobandtalent Sweden AB</main>"
        ATS.calls = 0

    def test_bounded_discovery_and_two_distinct_live_proofs_remain_one_vacancy(self):
        d = Discovery()
        report = run({"jobs": []}, discovery_client=d, dossier_factory=ATS)
        self.assertEqual(report["state"], "two-live-cycles-staging-policy-v2-passed", report)
        self.assertEqual(report["discovery"]["requests"], 3)
        self.assertEqual(len(report["cycles"]), 2)
        self.assertEqual(report["cycles"][0]["new_record_ids_vs_previous"], 1)
        self.assertEqual(report["cycles"][1]["new_record_ids_vs_previous"], 0)
        self.assertEqual(report["distinct_staging_new_vs_baseline"], 1)
        self.assertTrue(report["idempotent_second_cycle"])
        self.assertEqual(report["cycles"][1]["duplicate_id_count"], 0)
        self.assertEqual(report["cycles"][1]["catalog_ids_lost_vs_previous"], 0)
        self.assertEqual(report["net_new_distinct_verified_in_production"], 0)
        self.assertFalse(report["catalog_modified"])
        self.assertFalse(report["source_enabled"])
        self.assertEqual(report["applications_submitted"], 0)
        self.assertEqual(report["total_requests"], d.requests + ATS.calls)
        self.assertGreater(ATS.calls, 0)

    def test_not_in_bounded_feed_no_ats_requests(self):
        report = run({"jobs": []}, discovery_client=Discovery(hits=[]), dossier_factory=ATS)
        self.assertEqual(report["state"], "jobtech-posting-not-found-in-bounded-sample")
        self.assertEqual(ATS.calls, 0)
        self.assertEqual(report["total_requests"], 3)

    def test_no_legal_employer_identity_does_not_retry_second_cycle(self):
        ATS.legal_text = b"<main>Other company AB</main>"
        report = run({"jobs": []}, discovery_client=Discovery(), dossier_factory=ATS)
        self.assertEqual(report["state"], "policy-v2-review-required-no-promotion", report)
        self.assertEqual(len(report["cycles"]), 1)
        self.assertEqual(report["cycles"][0]["stage_status"], "review-required")
        self.assertEqual(report["net_new_distinct_verified_in_production"], 0)


if __name__ == "__main__":
    unittest.main()
