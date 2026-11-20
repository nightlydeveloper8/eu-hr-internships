"""Safety tests for the future daily JobTech source: disabled by default.

Mocks are fully offline. No network, source activation or applicant submission.
"""
from copy import deepcopy
from datetime import datetime, timezone, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from collector.daily import provision
from collector.official_feed_adapter import source_gate, ADAPTER, AtsBudgetFactory
from collector.official_feed_discovery import JOBTECH_HOST, JOBTECH_QUERIES
from collector.pipeline import ROOT, finalize, process_source, read
from collector.runtime import BudgetClient

HOST = "jobb.jobandtalent.com"
TITLE = "Praktik inom HR och rekrytering i Malmö - våren 2027"
PARENT = "https://" + HOST + "/jobs/8503489-praktik-inom-hr-och-rekrytering-i-malmo-varen-2027"
APP = PARENT + "/applications/new?promotion=2231065-arbetsformedlingen"
LEGAL = "https://" + HOST + "/privacy-policy"
INVENTORY = "https://" + HOST + "/sitemap"
SOURCE_ID = "staging-jobandtalent-se"


def source():
    return dict(id=SOURCE_ID, adapter=ADAPTER,
                employer="Jobandtalent Sweden AB", feed_provider="jobtech-se",
                provider_id="31558200", expected_ats_id="8503489",
                expected_city="Malmö",
                enabled=False, staging_only=True, rollout_approved=False,
                ownership_scope="reviewed-hosts", require_employer_identity=True,
                allowed_hosts=[HOST], reviewed_inventory_url=INVENTORY,
                target_countries=["SE"], jobtech_queries=list(JOBTECH_QUERIES),
                results_per_query=10, max_requests=18, collection_seconds=95)


def feed_record(**updates):
    record=dict(id=31558200, headline=TITLE,
                description={"text":"HR praktik med rekrytering"},
                employer={"name":"Jobandtalent Sweden AB"},
                workplace_address={"country":"Sverige","municipality":"Malmö"},
                webpage_url="https://arbetsformedlingen.se/platsbanken/annonser/31558200",
                application_details={"url":APP},publication_date="2026-11-16")
    record.update(updates)
    return record


class Discovery:
    def __init__(self, rows=None):
        self.requests=0;self.bytes=0
        self.rows=[feed_record()] if rows is None else rows
        self.redirect_scope_allowed=None
    def json(self,url):
        if self.redirect_scope_allowed and not self.redirect_scope_allowed(url):
            raise ValueError("Unexpected national feed endpoint")
        self.requests+=1
        if url != f"https://{JOBTECH_HOST}/ad/31558200":
            raise ValueError("Expected the documented exact-ID endpoint")
        data=self.rows[0] if len(self.rows)==1 else {}
        self.bytes+=len(json.dumps(data).encode())
        return data


class ProductionDiscovery(BudgetClient):
    def __init__(self,rows=None):
        super().__init__(seconds=95,max_requests=18,delay=0.0)
        self.rows=[feed_record()] if rows is None else rows
    def json(self,url):
        if self.redirect_scope_allowed and not self.redirect_scope_allowed(url):
            raise ValueError("Unexpected national feed host")
        self.requests+=1
        if url != f"https://{JOBTECH_HOST}/ad/31558200":
            raise ValueError("Expected the documented exact-ID endpoint")
        data=self.rows[0] if len(self.rows)==1 else {}
        self.bytes+=len(json.dumps(data).encode())
        return data


class ATS:
    calls=0
    owner=b"<main>Personuppgiftsansvarig Jobandtalent Sweden AB</main>"
    rate_limit=False
    def __init__(self, seconds, max_requests, delay):
        self.requests=0;self.bytes=0
        self.max_requests=max_requests
        self.redirect_scope_allowed=None
    def request(self,url,**kwargs):
        if self.rate_limit:
            from urllib.error import HTTPError
            raise HTTPError(url,429,"rate limited",{},None)
        if self.requests>=self.max_requests:
            raise ValueError("Test shared budget exhausted")
        if self.redirect_scope_allowed and not self.redirect_scope_allowed(url):
            raise ValueError("Unexpected ATS URL")
        pages={
            PARENT:(f"<main><h1>{TITLE}</h1><p>Plats: Malmö, Hyllie</p>"
                    f"<a href='{APP}'>Ansök</a></main>").encode(),
            APP:(f"<main><h1>{TITLE}</h1><a href='{LEGAL}'>Privacy Policy</a>"
                 "<form><input name='full_name'><input name='email' type='email'>"
                 "<input name='cv' type='file'><button type='submit'>Apply</button>"
                 "</form></main>").encode(),
            LEGAL:self.owner,
            INVENTORY:(f"<html><a href='/jobs/8503489-praktik-inom-hr-och-rekrytering-i-malmo-varen-2027'>"
                       f"{TITLE}</a></html>").encode()
        }
        if url not in pages:raise ValueError("Unknown ATS URL")
        body=pages[url]
        self.requests+=1;type(self).calls+=1;self.bytes+=len(body)
        return body,200,url


class AdapterIntegrationTests(unittest.TestCase):
    def setUp(self):
        ATS.calls=0
        ATS.rate_limit=False
        ATS.owner=b"<main>Personuppgiftsansvarig Jobandtalent Sweden AB</main>"
        self.stamp=datetime.now(timezone.utc).isoformat()

    def run_source(self,src=None, client=None, prior=(), preview=False, verify=True):
        return process_source(src or source(), client or Discovery(), self.stamp,
                              verify=verify, official_feed_preview=preview,
                              official_feed_prior_jobs=list(prior),
                              official_feed_ats_client_factory=ATS)

    def test_registered_source_is_disabled_and_not_provisioned_by_accident(self):
        sources=read(ROOT/"data/sources.json",[])
        configured=[x for x in sources if x.get("id")==SOURCE_ID]
        self.assertEqual(len(configured),1)
        self.assertEqual(configured[0]["adapter"],ADAPTER)
        self.assertFalse(configured[0]["enabled"])
        self.assertFalse(configured[0]["rollout_approved"])
        self.assertTrue(configured[0]["staging_only"])
        companies=read(ROOT/"data/companies.json",[])
        self.assertFalse(any("jobandtalent" in c.get("id","").lower() for c in companies))
        # Already-provisioned company registry must not synthesize an enabled
        # universal crawler for this unlinked reviewed disabled source.
        _,after=provision(companies,sources)
        self.assertFalse(next(x for x in after if x["id"]==SOURCE_ID)["enabled"])
        self.assertEqual(sum(x.get("enabled",False) for x in sources),
                         sum(x.get("enabled",False) for x in after))

    def test_disabled_source_zero_requests_without_explicit_preview(self):
        discovery=Discovery()
        p=self.run_source(client=discovery)
        self.assertFalse(p["jobs"])
        self.assertEqual(p["closure_eligible"],[])
        self.assertEqual(p["report"]["requests"],0)
        self.assertEqual(discovery.requests,0)
        self.assertEqual(ATS.calls,0)
        self.assertIn("requires an explicit",p["report"]["reason"])

    def test_enabled_flag_alone_never_activates_and_no_verify_never_publishes(self):
        for change in ({"enabled":True},
                       {"enabled":True,"staging_only":False},
                       {"enabled":True,"staging_only":False,"rollout_approved":True},
                       {"allowed_hosts":["evil.example"]},
                       {"max_requests":1000}):
            with self.subTest(change=change):
                candidate=dict(source(),**change)
                discovery=Discovery()
                p=self.run_source(candidate,discovery,preview=False)
                self.assertFalse(p["jobs"])
                self.assertEqual(discovery.requests,0)
        p=self.run_source(preview=True,verify=False)
        self.assertFalse(p["jobs"])
        self.assertEqual(ATS.calls,0)

    def test_one_reviewed_candidate_flows_through_process_source_and_finalize_twice(self):
        source_config=source()
        p=self.run_source(preview=True)
        self.assertEqual(p["report"]["matching"],1,p["report"])
        self.assertEqual(p["report"]["status"],"partial")
        self.assertEqual(p["report"]["feed_rows_scanned"],1)
        self.assertEqual(p["report"]["feed_requests"],1)
        self.assertEqual(p["report"]["feed_hr_candidates"],1)
        self.assertLessEqual(p["report"]["requests"],source_config["max_requests"])
        self.assertEqual(p["report"]["requests"],
                         p["report"]["feed_requests"]+p["report"]["ats_requests"])
        self.assertGreater(p["report"]["ats_bytes_read"],0)
        self.assertEqual(p["closure_eligible"],[])
        self.assertEqual(len(p["jobs"]),1)
        self.assertEqual(p["jobs"][0]["source_posting_id"],"8503489")
        with TemporaryDirectory(prefix="adapter-test-") as tmp:
            first,c=finalize([source_config],[source_config],{"jobs":[]},{},[p],
                             datetime.now(timezone.utc).isoformat(),Path(tmp))
            self.assertEqual(len(first["jobs"]),1)
            self.assertEqual(c["quality"]["verified_internships"],1)
            second=self.run_source(prior=first["jobs"],preview=True)
            follow,quality=finalize([source_config],[source_config],first,{},[second],
                                    datetime.now(timezone.utc).isoformat(),Path(tmp))
        self.assertEqual(len(follow["jobs"]),1)
        self.assertEqual(quality["quality"]["verified_internships"],1)
        self.assertEqual(follow["jobs"][0]["id"],first["jobs"][0]["id"])
        self.assertEqual(follow["jobs"][0]["first_discovered_at"],
                         first["jobs"][0]["first_discovered_at"])
        self.assertEqual(ATS.calls,p["report"]["ats_requests"]+second["report"]["ats_requests"])

    def test_missing_candidate_or_identity_failure_never_closes_existing_record(self):
        initial=self.run_source(preview=True)
        self.assertEqual(len(initial["jobs"]),1,initial["report"].get("reason"))
        prior=initial["jobs"]
        for discovery in (Discovery(rows=[]),
                          Discovery(rows=[feed_record(id=999999)]),
                          Discovery(rows=[feed_record(employer={"name":"Other employer"})])):
            with self.subTest(rows=discovery.rows):
                part=self.run_source(client=discovery,prior=prior,preview=True)
                self.assertFalse(part["jobs"])
                self.assertFalse(part["closure_eligible"])
                with TemporaryDirectory(prefix="adapter-missing-") as tmp:
                    current,_=finalize([source()],[source()],{"jobs":prior},{},[part],
                                       datetime.now(timezone.utc).isoformat(),Path(tmp))
                self.assertEqual(len(current["jobs"]),1)
                self.assertNotEqual(current["jobs"][0]["status"],"closed")

    def test_wrong_ats_id_and_unreviewed_mirror_are_quarantined(self):
        wrong=Discovery([feed_record(application_details={
            "url":APP.replace("8503489","9999999")})])
        before=ATS.calls
        part=self.run_source(client=wrong,preview=True)
        self.assertFalse(part["jobs"])
        self.assertEqual(ATS.calls,before)
        mirror=dict(id="other",url="https://elsewhere.example/jobs/1",
                    apply_url="https://elsewhere.example/jobs/1",
                    employer="Jobandtalent Sweden AB",title=TITLE,country="SE")
        blocked=self.run_source(prior=[mirror],preview=True)
        self.assertFalse(blocked["jobs"])
        self.assertIn("mirror",blocked["report"]["reason"])

    def test_no_employer_owner_or_rate_limit_is_fail_closed(self):
        ATS.owner=b"<main>Unrelated company</main>"
        blocked=self.run_source(preview=True)
        self.assertFalse(blocked["jobs"])
        self.assertEqual(blocked["closure_eligible"],[])
        ATS.owner=b"<main>Personuppgiftsansvarig Jobandtalent Sweden AB</main>"
        ATS.rate_limit=True
        limited=self.run_source(preview=True)
        self.assertFalse(limited["jobs"])
        self.assertEqual(limited["closure_eligible"],[])
        self.assertLessEqual(limited["report"]["requests"],source()["max_requests"])

    def test_manual_cli_preview_reuses_regular_pipeline_only_in_temporary_directory(self):
        from scripts.preview_reviewed_feed_source import preview
        input_source=source()
        result=preview(input_source,{"jobs":[]},[input_source],
                       discovery_client=Discovery(),ats_client_factory=ATS)
        self.assertEqual(result["state"],"staging-policy-v2-verified",result)
        self.assertEqual(result["verified_staging_new_distinct"],1)
        self.assertEqual(result["staging_direct_internships_gained"],1)
        self.assertEqual(result["converted_existing_ids"],[])
        self.assertEqual(result["staging_verified_internships"],1)
        self.assertEqual(result["closure_eligible"],[])
        self.assertEqual(result["requests"],result["feed_requests"]+result["ats_requests"])
        self.assertEqual(result["baseline_catalog_ids_lost"],0)
        self.assertFalse(result["production_catalog_modified"])
        self.assertFalse(result["source_enabled"])
        self.assertEqual(result["production_verified_vacancies_added"],0)
        self.assertEqual(result["applications_submitted"],0)

    def test_production_requires_separate_rollout_authority_and_budgetclient(self):
        enabled=dict(source(), enabled=True, staging_only=False,
                     rollout_approved=True,rollout_authorization="approved-v2-reviewed-2026-11-17")
        self.assertEqual(source_gate(enabled),"production")
        no_budget=self.run_source(enabled,Discovery(),preview=False)
        self.assertFalse(no_budget["jobs"])
        self.assertEqual(no_budget["report"]["requests"],0)
        realshape=self.run_source(enabled,ProductionDiscovery(),preview=False)
        self.assertEqual(len(realshape["jobs"]),1,realshape["report"].get("reason"))
        self.assertEqual(realshape["jobs"][0]["source_type"],ADAPTER)
        self.assertEqual(realshape["report"]["requests"],
                         realshape["report"]["feed_requests"]+
                         realshape["report"]["ats_requests"])
        self.assertEqual(realshape["closure_eligible"],[])


if __name__=="__main__":unittest.main()
