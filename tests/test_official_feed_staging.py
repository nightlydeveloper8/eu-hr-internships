"""Offline regular-finalize replay of a *current* JobTech → ATS v2 dossier."""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from collector.official_feed_staging import staging_part
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

    def existing_jobtech_copy(self):
        lead = candidate()
        return dict(
            id="public-copy-id", external_id=lead["provider_id"], source_posting_id=lead["provider_id"],
            source_id="public-se-jobtech", source_type="jobtech-search", employer=lead["employer"],
            title=lead["title"], country=lead["country"], countries=["SE"], city=lead["city"],
            status="open", url=lead["url"], external_application_url=APP,
            first_discovered_at="2026-11-18T07:26:38+00:00",
            public_listing_urls=["https://europa.eu/eures/portal/jv-se/jv-details/alias"],
            duplicate_source_ids=["public-eu-eures"],
            verification=dict(state="verified",policy_version=2,policy="public-api-active-listing"),
        )

    def test_exact_public_copy_keeps_its_id_and_links_on_two_previews(self):
        prior = self.existing_jobtech_copy()
        part, dossier = self.stage(previous=[prior])
        self.assertEqual(len(part["jobs"]), 1, part["report"].get("reason"))
        job = part["jobs"][0]
        self.assertEqual(job["id"], prior["id"])
        self.assertEqual(job["first_discovered_at"], prior["first_discovered_at"])
        self.assertEqual(set(job["public_listing_urls"]), {prior["url"], *prior["public_listing_urls"]})
        self.assertIn("public-eu-eures", job["duplicate_source_ids"])
        self.assertIn("public-se-jobtech", job["duplicate_source_ids"])
        repeat, _ = self.stage(dossier=dossier, previous=[job])
        self.assertEqual(repeat["jobs"], [job])
        self.assertFalse(repeat["closure_eligible"])

    def test_unknown_conflicting_and_ambiguous_public_copies_remain_unresolved(self):
        prior = self.existing_jobtech_copy()
        alternatives = [
            [dict(prior, external_application_url=APP.replace("8503489", "8503490"))],
            [dict(prior, source_posting_id="31558201")],
            [dict(prior, city="Stockholm")],
            [dict(prior, status="closed")],
            [dict(prior, ownership_risk="historical")],
            [prior, dict(prior, id="another-public-row")],
        ]
        dossier = self.proof()
        for rows in alternatives:
            with self.subTest(rows=rows):
                part, _ = self.stage(dossier=dossier, previous=rows)
                self.assertEqual(part["jobs"], [])
                self.assertEqual(part["closure_eligible"], [])

    def test_public_copy_adoption_does_not_apply_to_production(self):
        dossier = self.proof()
        production_source = dict(SOURCE, enabled=True, staging_only=False, rollout_approved=True,
                                 rollout_authorization="synthetic permission for regression test")
        part = staging_part(candidate(), dossier, production_source, dossier["checked_at"],
                            [self.existing_jobtech_copy()], production=True)
        self.assertFalse(part["jobs"])
        self.assertFalse(part["closure_eligible"])

    def test_public_refresh_keeps_exact_fresh_proof_then_falls_back_after_expiry(self):
        from collector.pipeline import reconcile
        prior = self.existing_jobtech_copy()
        part, dossier = self.stage(previous=[prior])
        job = part["jobs"][0]
        stamp = dossier["checked_at"]
        pub_time = (datetime.fromisoformat(stamp)+timedelta(hours=1)).isoformat()
        raw = dict(prior, apply_url=prior["url"], last_seen_at=pub_time, last_verified_at=pub_time,
                   verification=dict(prior["verification"], checked_at=pub_time))
        both = reconcile([prior], [job, raw], set(), pub_time)
        self.assertEqual(len(both), 1)
        self.assertEqual(both[0]["application_verification"], job["application_verification"])
        refreshed = reconcile(both, [raw], set(), pub_time)
        self.assertEqual(refreshed[0]["last_verified_at"], stamp)
        self.assertEqual(refreshed[0]["application_verification"], job["application_verification"])
        after = (datetime.fromisoformat(stamp)+timedelta(hours=49)).isoformat()
        fallback = reconcile(refreshed, [raw], set(), after)
        self.assertEqual(fallback[0]["id"], prior["id"])
        self.assertNotIn("application_verification", fallback[0])
        self.assertEqual(fallback[0]["verification"]["policy"], "public-api-active-listing")
        conflict = reconcile(both,[dict(raw,external_application_url=APP.replace("8503489","8503490"))],
                             set(),pub_time)
        self.assertNotIn("application_verification", conflict[0])

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
