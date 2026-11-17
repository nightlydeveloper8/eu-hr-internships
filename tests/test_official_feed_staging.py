"""Offline regular-finalize replay of a *current* JobTech → ATS v2 dossier."""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from collector.official_feed_staging import staging_part, stage_live_candidate
from collector.official_feed_policy_dossier import review
from collector.pipeline import finalize
from collector.verification import verified_job

HOST = "jobb.jobandtalent.com"
TITLE = "Praktik inom HR och rekrytering i Malmö - våren 2027"
PARENT = "https://" + HOST + "/jobs/8503489-praktik-inom-hr-och-rekrytering-i-malmo-varen-2027"
APP = PARENT + "/applications/new?promotion=2231065-arbetsformedlingen"
SITEMAP = "https://" + HOST + "/sitemap"
LEGAL = "https://" + HOST + "/privacy-policy"
SOURCE = dict(id="staging-jobandtalent-se", employer="Jobandtalent Sweden AB",
              adapter="jobtech-policy-v2-staging", enabled=False, staging_only=True,
              ownership_scope="reviewed-hosts", require_employer_identity=True,
              allowed_hosts=[HOST], reviewed_inventory_url=SITEMAP)


def candidate(**updates):
    row = dict(provider="jobtech-se", provider_id="31558200",
               employer="Jobandtalent Sweden AB", title=TITLE,
               country="SE", city="Malmö",
               workplace_country_evidence=True, verification_state="unverified",
               url="https://arbetsformedlingen.se/platsbanken/annonser/31558200",
               apply_url=APP)
    row.update(updates)
    return row


def pages():
    app = (f"<main><h1>{TITLE}</h1><a href='{LEGAL}'>Privacy Policy</a>"
           "<form><input name='name'><input name='email' type='email'>"
           "<input name='cv' type='file'><button type='submit'>Apply</button></form></main>").encode()
    parent = (f"<main><h1>{TITLE}</h1><p>Plats: Malmö, Hyllie</p>"
              f"<a href='{APP}'>Ansök</a></main>").encode()
    index = (f"<html><a href='/jobs/8503489-praktik-inom-hr-och-rekrytering-i-malmo-varen-2027'>"
             f"{TITLE}</a></html>").encode()
    return {PARENT: parent, APP: app, SITEMAP: index,
            LEGAL: b"<main>Personuppgiftsansvarig Jobandtalent Sweden AB</main>"}


class Budget:
    pages_by_url = pages()
    total_requests = 0

    def __init__(self, seconds, max_requests, delay):
        self.requests = 0
        self.bytes = 0
        self.redirect_scope_allowed = None

    def request(self, url, **kwargs):
        self.requests += 1
        type(self).total_requests += 1
        if url not in self.pages_by_url:
            raise ValueError("Unknown reviewed URL")
        if self.redirect_scope_allowed and not self.redirect_scope_allowed(url):
            raise ValueError("Unapproved redirect")
        body = self.pages_by_url[url]
        self.bytes += len(body)
        return body, 200, url


class JobTechStagingTests(unittest.TestCase):
    def setUp(self):
        Budget.pages_by_url = pages()
        Budget.total_requests = 0

    def proof(self, lead=None):
        return review(lead or candidate(), approved_host=HOST,
                      approved_inventory_url=SITEMAP, client_factory=Budget)

    def stage(self, lead=None, dossier=None, previous=()):
        lead = lead or candidate()
        dossier = dossier or self.proof(lead)
        part = staging_part(lead, dossier, SOURCE, dossier["checked_at"], previous)
        return part, dossier

    def test_real_policy_review_stages_one_record_through_finalize_twice(self):
        part, dossier = self.stage()
        self.assertEqual(dossier["status"], "policy-v2-evidence-passed-staging-only")
        self.assertEqual(part["report"]["status"], "partial")  # one job != full inventory
        self.assertEqual(len(part["jobs"]), 1, part["report"].get("reason"))
        self.assertEqual(part["closure_eligible"], [])
        self.assertEqual(part["jobs"][0]["official_feed_provenance"],
                         {"provider": "jobtech-se", "public_id": "31558200",
                          "ats_id": "8503489"})
        with TemporaryDirectory() as tmp:
            first, coverage = finalize([SOURCE], [SOURCE], {"jobs": []}, {},
                                       [part], dossier["checked_at"], Path(tmp))
        self.assertEqual(len(first["jobs"]), 1)
        job = first["jobs"][0]
        self.assertTrue(verified_job(job, dossier["checked_at"]))
        self.assertEqual(job["source_posting_id"], "8503489")
        self.assertEqual(job["country"], "SE")
        self.assertEqual(job["verification"]["policy_version"], 2)
        self.assertEqual(coverage["quality"]["verified_internships"], 1)
        self.assertEqual(first["update_status"], "partial")
        second_part, second_dossier = self.stage(previous=first["jobs"])
        with TemporaryDirectory() as tmp:
            second, second_coverage = finalize([SOURCE], [SOURCE], first, {},
                                                [second_part], second_dossier["checked_at"], Path(tmp))
        self.assertEqual([j["id"] for j in second["jobs"]], [job["id"]])
        self.assertEqual(second_coverage["quality"]["verified_internships"], 1)
        self.assertEqual(second["jobs"][0]["first_discovered_at"], job["first_discovered_at"])
        self.assertGreaterEqual(Budget.total_requests, 10)

    def test_live_helper_reads_new_proof_before_in_memory_staging(self):
        part, dossier = stage_live_candidate(candidate(), SOURCE, client_factory=Budget)
        self.assertEqual(dossier["status"], "policy-v2-evidence-passed-staging-only")
        self.assertEqual(len(part["jobs"]), 1, part["report"].get("reason"))
        self.assertEqual(part["report"]["matching"], 1)
        self.assertEqual(Budget.total_requests, dossier["requests"])

    def test_offline_replay_uses_normal_finalize_without_production_writes(self):
        from scripts.stage_jobtech_policy import replay
        discovery = dict(provider="jobtech-se", mode="discovery-only",
                         candidates=[candidate()])
        dossier = self.proof()
        result = replay(discovery, dossier, {"jobs": []},
                        provider_id="31558200", source_id=SOURCE["id"],
                        approved_host=HOST, reviewed_inventory=SITEMAP)
        self.assertEqual(result["stage_result"], "eligible-staging-only")
        self.assertEqual(result["new_staged_distinct_verified_internships"], 1)
        self.assertEqual(result["baseline_ids_lost"], 0)
        self.assertEqual(result["production_verified_vacancies_added"], 0)
        self.assertFalse(result["production_catalog_modified"])
        self.assertFalse(result["source_registry_modified"])
        self.assertEqual(result["closure_eligible"], [])
        result_bad = replay(discovery, dict(dossier, official_inventory_confirmed=False),
                            {"jobs": []}, provider_id="31558200",
                            source_id=SOURCE["id"], approved_host=HOST,
                            reviewed_inventory=SITEMAP)
        self.assertEqual(result_bad["stage_result"], "review-required")
        self.assertEqual(result_bad["new_staged_distinct_verified_internships"], 0)

    def test_wrong_feed_ats_employer_city_and_unapproved_source_fail_closed(self):
        dossier = self.proof()
        checks = [
            (candidate(provider_id="other"), dossier, SOURCE),
            (candidate(apply_url=APP.replace("8503489", "9999999")), dossier, SOURCE),
            (candidate(employer="Another staffing agency"), dossier, SOURCE),
            (candidate(city="Stockholm"), dossier, SOURCE),
            (candidate(), dict(dossier, official_inventory_confirmed=False), SOURCE),
            (candidate(), dict(dossier, job_identity_match=False), SOURCE),
            (candidate(), dict(dossier, owner_evidence="not-established"), SOURCE),
            (candidate(), dict(dossier, application_preflight="review-required"), SOURCE),
            (candidate(), dict(dossier, status="review-required"), SOURCE),
            (candidate(), dossier, dict(SOURCE, enabled=True)),
            (candidate(), dossier, dict(SOURCE, allowed_hosts=["other.example"])),
        ]
        for lead, proof, source in checks:
            with self.subTest(lead=lead, source=source, status=proof["status"]):
                part = staging_part(lead, proof, source, dossier["checked_at"])
                self.assertFalse(part["jobs"])
                self.assertFalse(part["closure_eligible"])
                self.assertEqual(part["report"]["status"], "partial")
                self.assertTrue(part["report"]["reason"])

    def test_missing_or_stale_proof_does_not_close_historical_vacancy(self):
        good, dossier = self.stage()
        with TemporaryDirectory() as tmp:
            prior, _ = finalize([SOURCE], [SOURCE], {"jobs": []}, {},
                                [good], dossier["checked_at"], Path(tmp))
        old_id = prior["jobs"][0]["id"]
        stale = dict(dossier, checked_at=(
            datetime.fromisoformat(dossier["checked_at"]) - timedelta(hours=1)).isoformat())
        missing = staging_part(candidate(), stale, SOURCE, dossier["checked_at"], prior["jobs"])
        self.assertFalse(missing["jobs"])
        self.assertEqual(missing["closure_eligible"], [])
        with TemporaryDirectory() as tmp:
            current, _ = finalize([SOURCE], [SOURCE], prior, {},
                                  [missing], dossier["checked_at"], Path(tmp))
        self.assertEqual(len(current["jobs"]), 1)
        self.assertEqual(current["jobs"][0]["id"], old_id)
        self.assertNotEqual(current["jobs"][0]["status"], "closed")

    def test_possible_existing_mirror_requires_review_not_a_second_vacancy(self):
        dossier = self.proof()
        existing = dict(id="other-id", url="https://another.example/other-ats/job",
                        apply_url="https://another.example/other-ats/job",
                        employer=candidate()["employer"], title=TITLE, country="SE")
        part = staging_part(candidate(), dossier, SOURCE, dossier["checked_at"], [existing])
        self.assertEqual(part["jobs"], [])
        self.assertIn("mirror", part["report"]["reason"])


if __name__ == "__main__":
    unittest.main()
