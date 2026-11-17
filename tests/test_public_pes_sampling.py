"""Offline safety and representative-format tests for EU public data sampling."""
import json
from datetime import date, timedelta
from unittest import TestCase
from unittest.mock import patch

from collector.public_pes_sampling import (
    MAX_BYTES, _cz_items_from_prefix, sample_czech, sample_latvia,
    checked_bounded_get, run,
)
from collector.runtime import BudgetClient


class FakeBudget(BudgetClient):
    def __init__(self,**kwargs):
        self.requests=1
        self.bytes=90
        self.remaining=lambda:20
        self.redirect_scope_allowed=None
    def permitted(self,url):
        return True
    def check(self):
        return None


def row(portal_id=111,title="Stáž HR"):
    return dict(portalId=portal_id,pozadovanaProfese={"cs":title},
                zamestnavatel={"nazev":"Example Czech s.r.o."},
                urlAdresa="https://example.org/jobs/cz-hr-"+str(portal_id),
                expirace="2027-12-31",datumVlozeni="2026-11-16T00:00:00Z",
                kontaktniPracoviste={"telefon":"secret private number",
                                     "email":"private@example.invalid"})


class SamplingTests(TestCase):
    def test_czech_incremental_parser_never_uses_incomplete_object(self):
        data=('{"polozky":['+json.dumps(row(1),ensure_ascii=False)+","+
              json.dumps(row(2),ensure_ascii=False)[:33]).encode()
        items,complete=_cz_items_from_prefix(data,200)
        self.assertEqual(len(items),1)
        self.assertFalse(complete)
        with self.assertRaises(ValueError):
            _cz_items_from_prefix(b'{"other":[]}',5)

    def test_czech_sample_counts_complete_rows_only_and_no_personal_contacts(self):
        records={"polozky":[row(1),row(2),row(3,"Obchodní manažer")]}
        raw=json.dumps(records,ensure_ascii=False).encode()
        with patch("collector.public_pes_sampling.checked_bounded_get",
                   return_value=(raw,dict(http_status=200,truncated=False,bytes_read=len(raw)))):
            report=sample_czech(FakeBudget(),date.today()-timedelta(days=1),
                                max_bytes=800000,max_rows=200)
        self.assertEqual(report["records_scanned"],3)
        self.assertEqual(report["strict_distinct_candidates"],2)
        self.assertEqual(report["counts"]["combined_title_cues"],2)
        self.assertTrue(report["input_complete"])
        self.assertEqual(len(report["candidates"]),2)
        self.assertNotIn("secret",json.dumps(report))
        self.assertNotIn("private@example.invalid",json.dumps(report))

    def test_czech_sample_not_marked_exhaustive_when_prefix_or_row_cap(self):
        records={"polozky":[row(1),row(2)]}
        raw=json.dumps(records,ensure_ascii=False).encode()
        with patch("collector.public_pes_sampling.checked_bounded_get",
                   return_value=(raw,dict(http_status=206,truncated=True,bytes_read=len(raw)))):
            report=sample_czech(FakeBudget(),date.today()-timedelta(days=1),max_rows=1)
        self.assertFalse(report["input_complete"])
        self.assertEqual(report["records_scanned"],1)
        self.assertEqual(report["strict_distinct_candidates"],1)

    def test_latvian_summarizes_without_publishing_or_contact_data(self):
        records=[
            {"Vakances_Nr":"123","Vakances_nosaukums":"HR praktikants",
             "Vakances_paplasinats_apraksts":"Iestāde","Attels":"private@sample.lv"},
            {"Vakances_Nr":"124","Vakances_nosaukums":"Bus driver",
             "Vakances_paplasinats_apraksts":""}]
        data=json.dumps({"success":True,"result":{"records":records}}).encode()
        with patch("collector.public_pes_sampling.checked_bounded_get",
                   return_value=(data,dict(http_status=200,truncated=False,bytes_read=len(data)))):
            report=sample_latvia(FakeBudget(),max_rows=10)
        self.assertEqual(report["records_scanned"],2)
        self.assertEqual(report["counts"]["combined_title_cues"],1)
        self.assertEqual(report["strict_distinct_candidates"],0)
        self.assertEqual(report["candidates"],[])
        self.assertNotIn("private@sample.lv",json.dumps(report))

    def test_non_public_unsupported_host_fail_closed_before_http(self):
        with self.assertRaises(ValueError):
            checked_bounded_get(FakeBudget(),"https://private.example/secret")
        with self.assertRaises(ValueError):
            checked_bounded_get(FakeBudget(),"http://data.mpsv.cz/foo")
        with self.assertRaises(ValueError):
            checked_bounded_get(FakeBudget(),"https://data.mpsv.cz/foo",max_bytes=2_000_000)

    def test_error_retains_metric_zero_and_no_verified_claim(self):
        with patch("collector.public_pes_sampling.checked_bounded_get",
                   side_effect=ValueError("robots.txt disallows")):
            report=run("nva-lv",client_factory=FakeBudget)
        self.assertEqual(report["state"],"blocked-or-incomplete")
        self.assertEqual(report["verified_vacancies_added"],0)
        self.assertFalse(report["production_enabled"])
        self.assertEqual(report["records_scanned"],0)

    def test_reject_date_beyond_window_and_unsupported_provider(self):
        for d in (date.today()+timedelta(days=1),
                  date.today()-timedelta(days=11)):
            with self.assertRaises(ValueError):
                sample_czech(FakeBudget(),d)
        self.assertEqual(run("unknown",client_factory=FakeBudget)["state"],
                         "blocked-or-incomplete")
