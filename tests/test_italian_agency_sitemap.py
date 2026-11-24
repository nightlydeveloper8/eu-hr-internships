import unittest
from unittest.mock import Mock

from collector.employer_pages import italian_agency_slug_candidate, sitemap_records
from collector.pipeline import agency_sitemap_due
from collector.classify import italian_student_eligibility


class ItalianAgencySitemapTests(unittest.TestCase):
    base = "https://agency.example"
    candidate = base + "/jobs/tirocinio-selezione-del-personale-12345"
    excluded = base + "/jobs/tirocinio-sviluppo-software-12346"

    def test_slug_requires_both_signals_and_never_uses_query(self):
        self.assertTrue(italian_agency_slug_candidate(self.candidate))
        self.assertFalse(italian_agency_slug_candidate(self.excluded + "?query=hr"))
        self.assertFalse(italian_agency_slug_candidate(self.base + "/jobs/payroll-manager"))
        self.assertFalse(italian_agency_slug_candidate(self.base + "/jobs/internal-hr-lead"))
        self.assertFalse(italian_agency_slug_candidate(self.base + "/jobs/hr/stage-sviluppo/12345"))

    def test_sitemap_keeps_lastmod_and_known_postings_for_recheck(self):
        sitemap = self.base + "/sitemap.xml"
        client = Mock()
        client.request.return_value = (
            f"<urlset><url><loc>{self.candidate}</loc><lastmod>2026-11-23</lastmod></url>"
            f"<url><loc>{self.excluded}</loc></url></urlset>".encode(), 200, sitemap
        )
        source = dict(id="agency", employer="Agency", sitemaps=[sitemap],
                      allowed_hosts=["agency.example"], job_url_pattern="/jobs/",
                      url_slug_prefilter=True, italian_agency_slug_triage=True,
                      known_job_urls=[self.base + "/jobs/archived-slug"])
        records = {r["url"]: r.get("sitemap_lastmod") for r in sitemap_records(source, client)}
        self.assertEqual(records, {self.candidate: "2026-11-23",
                                   self.base + "/jobs/archived-slug": None})

        strict = sitemap_records(dict(source, slow_collection_lane=True), client)
        self.assertEqual([record["url"] for record in strict], [self.candidate])

    def test_lastmod_update_and_rotation_are_due(self):
        first_check = "2026-11-22T18:00:00Z"
        state = {self.candidate: dict(lastmod="2026-11-22", checked_at=first_check)}
        same = dict(url=self.candidate, sitemap_lastmod="2026-11-22")
        changed = dict(same, sitemap_lastmod="2026-11-23")
        self.assertEqual(agency_sitemap_due([same], state, set(), "2026-11-23T18:00:00Z"), [])
        self.assertEqual(agency_sitemap_due([changed], state, set(), "2026-11-23T01:00:00Z"), [changed])
        self.assertEqual(agency_sitemap_due([same], state, {self.candidate}, "2026-11-23T18:00:00Z"), [same])

    def test_italian_student_evidence_is_independent_of_generic_stage_label(self):
        self.assertEqual(italian_student_eligibility("Tirocinio curricolare HR"), "confirmed")
        self.assertEqual(italian_student_eligibility("Stage HR", "Posizione per laureandi."), "confirmed")
        self.assertEqual(italian_student_eligibility("Stage HR", "Supporto nelle selezioni."), "not_stated")
        self.assertEqual(italian_student_eligibility("Stage extracurriculare HR"), "excluded")
