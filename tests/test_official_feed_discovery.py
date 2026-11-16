"""Offline evidence and safety tests for EU structured public vacancy discovery."""
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest

from collector.official_feed_discovery import (
    JOBTECH_QUERIES, eures_candidate, https_url, jobtech_candidate,
    jobtech_search, normalize, discovery_report
)
from scripts.official_feed_discovery import authorisation_evidence, main


def jobtech_record(id_="123456", title="Praktik inom HR och rekrytering"):
    return {
        "id":id_, "headline":title,
        "description":{"text":"Som praktikant får du erfarenhet av rekrytering och HR."},
        "employer":{"name":"Example Sweden AB"},
        "workplace_address":{"country":"Sverige","municipality":"Stockholm"},
        "webpage_url":"https://arbetsformedlingen.se/platsbanken/annonser/"+id_,
        "application_details":{"url":"https://careers.example/jobs/"+id_},
        "publication_date":"2026-11-16T10:00:00+00:00"
    }


def eures_record(id_="EURES-123",title="HR internship",country="NL"):
    return dict(id=id_,title=title,country=country,employer="Example BV",
        city="Utrecht",description="HR and payroll internship",
        url="https://europa.eu/eures/portal/jv-se/jv-details/"+id_)


class OfficialDiscoveryTests(unittest.TestCase):
    def test_swedish_official_data_becomes_review_candidate_only(self):
        row=jobtech_candidate(jobtech_record())
        self.assertIsNotNone(row)
        self.assertEqual((row["provider"],row["country"],row["provider_id"]),
                         ("jobtech-se","SE","123456"))
        self.assertEqual(row["verification_state"],"unverified")
        self.assertEqual(row["verified_vacancies_added"],0)
        self.assertEqual(row["apply_url"],"https://careers.example/jobs/123456")
        self.assertTrue(row["workplace_country_evidence"])
        self.assertNotIn("description",row)
        self.assertNotIn("text",row)

    def test_no_non_hr_or_permanent_or_unlocated_borrowed_country(self):
        self.assertIsNone(jobtech_candidate(jobtech_record(title="Marketing praktik")))
        self.assertIsNone(jobtech_candidate(jobtech_record(title="HR manager permanent")))
        wrong=jobtech_record();wrong["workplace_address"]["country"]="Norge"
        self.assertIsNone(jobtech_candidate(wrong))
        missing=jobtech_record();missing["webpage_url"]=""
        self.assertIsNone(jobtech_candidate(missing))
        missing=jobtech_record();missing["employer"]={}
        self.assertIsNone(jobtech_candidate(missing))
        row=jobtech_record();row["workplace_address"]["country"]=""
        self.assertFalse(jobtech_candidate(row)["workplace_country_evidence"])

    def test_exact_url_host_and_unsafe_url_fail_closed(self):
        for url in ("http://europa.eu/eures/portal/jv-se/jv-details/123",
                    "https://evil.example/eures/portal/jv-se/jv-details/123",
                    "https://europa.eu:443/eures/portal/jv-se/jv-details/123",
                    "https://user:pass@europa.eu/eures/portal/jv-se/jv-details/123",
                    "https://europa.eu\\@evil.example/eures/portal/jv-se/jv-details/123"):
            with self.subTest(url=url):
                self.assertIsNone(https_url(url,{"europa.eu"}))
        row=eures_record();row["url"]="https://europa.eu/eures/portal/jv-se/home?lang=en"
        self.assertIsNone(eures_candidate(row))

    def test_eures_authorised_metadata_is_not_verified_by_import(self):
        row=eures_candidate(eures_record())
        self.assertEqual(row["provider"],"eures-authorized-input")
        self.assertIsNone(row["apply_url"])
        self.assertEqual(row["country"],"NL")
        self.assertFalse(row["workplace_country_evidence"])
        self.assertEqual(row["verification_state"],"unverified")
        self.assertEqual(row["verified_vacancies_added"],0)
        self.assertNotIn("description",row)
        bad=eures_record(country="CH")
        self.assertIsNone(eures_candidate(bad))
        bad=eures_record(title="HR Operations Specialist")
        self.assertIsNone(eures_candidate(bad))

    def test_deduplicate_existing_url_and_repeated_ids(self):
        records=[jobtech_record(),jobtech_record(),jobtech_record("98765"),
                 jobtech_record("24680",title="Sales manager")]
        a=normalize(records,"jobtech-se")
        self.assertEqual(a["candidate_count"],2)
        self.assertEqual(a["rejected"]["duplicate-in-input"],1)
        self.assertEqual(a["rejected"]["not-eligible-or-incomplete"],1)
        b=normalize(records,"jobtech-se",existing_urls=[a["candidates"][0]["url"]])
        self.assertEqual(b["candidate_count"],1)
        self.assertEqual(b["rejected"]["already-in-catalog"],1)
        self.assertEqual(b["catalogue_modified"] if "catalogue_modified" in b else None,None)
        self.assertEqual(b["verified_vacancies_added"],0)

    def test_budget_limits_and_bad_response(self):
        class Client:
            def __init__(self,reply):
                self.reply=reply;self.calls=[];self.requests=0;self.bytes=0
            def json(self,url):
                self.calls.append(url);self.requests+=1
                return self.reply
        client=Client({"hits":[jobtech_record()]})
        with self.assertRaises(ValueError):
            jobtech_search(client,("hr",)*4)
        with self.assertRaises(ValueError):
            jobtech_search(client,("hr",),per_query=41)
        self.assertEqual(client.calls,[])
        result=discovery_report(client,queries=("hr praktik",),per_query=4)
        self.assertEqual(result["requests"],1)
        self.assertEqual(result["candidate_count"],1)
        self.assertEqual(len(client.calls),1)
        self.assertIn("limit=4",client.calls[0])
        self.assertIn("q=hr+praktik",client.calls[0])
        with self.assertRaises(ValueError):
            jobtech_search(Client({"hits":"bad"}),("hr praktik",))
        with self.assertRaises(ValueError):
            normalize([jobtech_record()]*121,"jobtech-se")

    def test_no_eures_api_fetch_and_no_write_without_grant(self):
        with TemporaryDirectory() as tmp:
            path=Path(tmp)
            source=path/"input.json";source.write_text(json.dumps([eures_record()]))
            report=path/"report.json"
            with patch("collector.runtime.BudgetClient.request", side_effect=AssertionError("no network")):
                with self.assertRaises(SystemExit):
                    main(["--provider","eures-authorized-input","--input",str(source),
                          "--output",str(report)])
            self.assertFalse(report.exists())
            with self.assertRaises(SystemExit):
                main(["--provider","eures-authorized-input","--live",
                      "--output",str(report)])

    def test_eures_grant_metadata_expiry_and_explicit_scope(self):
        with TemporaryDirectory() as tmp:
            path=Path(tmp)/"permission.json"
            data=dict(source="eures",grant_reference="test-contract",
                granting_authority="Test national coordinating office",
                approved_use="public vacancy metadata index",
                document_url="https://example.org/grant",
                permits_vacancy_extraction_and_indexing=True,
                valid_until=(datetime.now(timezone.utc)+timedelta(days=10)).isoformat())
            path.write_text(json.dumps(data))
            self.assertEqual(authorisation_evidence(path)["status"],
                             "operator-attested-not-independently-authenticated")
            data["permits_vacancy_extraction_and_indexing"]=False
            path.write_text(json.dumps(data))
            with self.assertRaises(ValueError):authorisation_evidence(path)
            data["permits_vacancy_extraction_and_indexing"]=True
            data["valid_until"]=(datetime.now(timezone.utc)-timedelta(days=1)).isoformat()
            path.write_text(json.dumps(data))
            with self.assertRaises(ValueError):authorisation_evidence(path)

    def test_production_catalog_and_registry_are_never_modified_by_offline_import(self):
        with TemporaryDirectory() as tmp:
            path=Path(tmp)
            permission=path/"permission.json"
            permission.write_text(json.dumps(dict(
                source="eures",grant_reference="test-contract",
                granting_authority="Test NCO",approved_use="public index",
                document_url="https://example.org/grant",
                permits_vacancy_extraction_and_indexing=True,
                valid_until=(datetime.now(timezone.utc)+timedelta(days=10)).isoformat())))
            source=path/"input.json";source.write_text(json.dumps([eures_record()]))
            output=path/"output.json"
            import hashlib
            root=Path(__file__).resolve().parents[1]
            files=[root/"data/catalog.json",root/"data/sources.json"]
            before=[hashlib.sha256(p.read_bytes()).hexdigest() for p in files]
            with patch("collector.runtime.BudgetClient.request",side_effect=AssertionError("network")):
                report=main(["--provider","eures-authorized-input",
                    "--input",str(source),"--authorization",str(permission),
                    "--output",str(output)])
            after=[hashlib.sha256(p.read_bytes()).hexdigest() for p in files]
            self.assertEqual(before,after)
            self.assertFalse(report["catalog_modified"])
            self.assertEqual(report["candidate_count"],1)
            self.assertEqual(report["requests"],0)


if __name__=="__main__":
    unittest.main()
