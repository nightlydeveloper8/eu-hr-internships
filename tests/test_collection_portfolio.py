from copy import deepcopy
import unittest
from unittest.mock import patch

from collector.pipeline import process_source
from collector.dynamic_ats import MissingDynamicForm
from collector.verification import _verify_vacancy

from scripts.collection_portfolio import portfolio


STAMP = "2026-11-20T06:00:00+00:00"
HOST = "work.recruitee.com"
SOURCE = dict(id="employer", employer="Employer", enabled=True, adapter="universal-employer",
              allowed_hosts=[HOST])
OBSERVATION = dict(id="employer", adapter="recruitee", checked_at=STAMP, requests=4,
                   matching=0, status="partial", complete=False)


def job(id_, **updates):
    return dict(id=id_, source_id="employer", source_type="recruitee", country="NL",
                internship_type="internship", url=f"https://{HOST}/o/job-{id_}",
                status="unverified", last_seen_at=STAMP,
                verification=dict(state="incomplete", reason="No available vacancy-specific application entry",
                                  checked_at=STAMP, policy_version=2)) | updates


def report(jobs=(), observation=OBSERVATION, source=SOURCE):
    return portfolio({"jobs": list(jobs)}, {"sources": [observation], "generated_at": STAMP}, [source])


class CollectionPortfolioTests(unittest.TestCase):
    def test_maps_configured_routes_separately_from_measured_capability(self):
        out = report()
        self.assertEqual(out["adapters"]["universal-employer"]["enabled"], 1)
        self.assertEqual(out["adapters"]["recruitee"]["recent_attempts"], 1)
        self.assertEqual(out["adapters"]["recruitee"]["requests_with_explicit_zero_matches"], 4)
        self.assertEqual(out["adapters"]["recruitee"]["complete_inventories"], 0)
        self.assertEqual(out["provider_signals"]["recruitee.com"]["registered_typed_sources"], 0)

    def test_counts_distinct_fresh_confirmation_and_public_leads_separately(self):
        positive = dict(status="open", last_verified_at=STAMP, link_status="verified",
                        verification=dict(state="verified", policy_version=2))
        records = [
            job("direct", **positive, application_verification={"method": "form"}),
            job("public", employer="Company AB", **(positive | {"link_status": "public-api-active-listing",
                "verification": positive["verification"] | {
                "policy": "public-api-active-listing"}}), external_application_url="https://employer.eu/apply"),
            job("stale", **(positive | {"last_verified_at": "2026-11-01T08:00:00Z"}),
                application_verification={"method": "form"}),
        ]
        out = report(records + [deepcopy(records[0])])
        self.assertEqual(out["countries"]["NL"], {"direct": 1, "public_listings": 1,
                                                   "public_leads_with_external_url": 1})
        self.assertEqual(out["adapters"]["recruitee"]["direct_catalog_internships"], 1)
        self.assertEqual(out["public_employer_clusters"], [
            {"country": "NL", "employer": "Company AB", "listings": 1,
             "with_external_url": 1, "listing_sources": ["employer"]}])

    def test_groups_only_recent_reviewable_employer_pages_by_real_gap(self):
        records = [job("1"), job("2", country="FR"),
                   job("old", last_seen_at="2026-11-01T08:00:00Z"),
                   job("unapproved", url="https://third-party.eu/1"),
                   job("historical-ownership", ownership_risk=True),
                   job("blocked", verification=dict(state="blocked", checked_at=STAMP))]
        outcomes = report(records)["application_review"]
        self.assertEqual([(row["gap"], row["candidates"]) for row in outcomes],
                         [("application-form", 2), ("access-blocked", 1)])
        self.assertEqual(outcomes[0]["countries"], {"FR": 1, "NL": 1})
        self.assertEqual(outcomes[0]["sample_ids"], ["1", "2"])

    def test_partial_zero_and_missing_data_are_not_complete_empty_inventories(self):
        unknown = {k: v for k, v in OBSERVATION.items() if k not in ("matching", "requests")}
        out = report(observation=unknown)
        self.assertEqual(out["highest_request_zero_match_sources"], [])
        self.assertEqual(out["adapters"]["recruitee"]["requests_unknown_sources"], 1)
        self.assertEqual(out["adapters"]["recruitee"]["complete_inventories"], 0)
        self.assertEqual(report(source=SOURCE | {"enabled": False})["recent_coverage"], 0)

    def test_out_of_scope_application_cta_is_reported_without_requesting_it(self):
        from collector.universal import Document

        url = f"https://{HOST}/o/internship-456"
        applicant_url = "https://apply.example.org/jobs/456?private_token=must-not-be-emitted"
        html = f"<h1>HR internship</h1><a href='{applicant_url}'>Apply</a>".encode()
        observation = {}
        record = dict(url=url, apply_url=url, title="HR internship", posting_identifier="456")
        with patch("collector.verification.checked_document",
                   return_value=(html, Document(html, url))) as read_document:
            with self.assertRaises(MissingDynamicForm):
                _verify_vacancy(record, SOURCE, object(), STAMP, observation)
        read_document.assert_called_once()
        self.assertEqual(observation["application_route_hints"], [("apply.example.org", True, False)])

    def test_pipeline_aggregates_routes_without_promoting_candidate(self):
        url = f"https://{HOST}/o/internship-456"
        record = dict(url=url, apply_url=url, title="HR internship", external_id="456",
                      posting_identifier="456", employer="Employer", location="Netherlands",
                      country="NL", text="Human resources internship")
        source = SOURCE | {"adapter": "recruitee"}

        def failed(record, source, client, stamp, observation):
            observation["application_route_hints"] = [("apply.example.org", True, False)]
            raise ValueError("Application requires a reviewed host")

        with (patch("collector.pipeline.collect", return_value=[record]),
              patch("collector.pipeline.enrich", return_value=record),
              patch("collector.verification.verify_vacancy", side_effect=failed)):
            part = process_source(source, object(), STAMP)
        self.assertEqual(part["jobs"][0]["status"], "unverified")
        self.assertEqual(part["closure_eligible"], [])
        self.assertEqual(part["report"]["application_route_hints"], [
            {"host": "apply.example.org", "matching_identifier": True,
             "in_source_scope": False, "observations": 1}])
