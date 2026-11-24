"""Italian eligibility and current-listing proof are independent."""
import json
import unittest
from unittest.mock import Mock, patch

from collector.pipeline import process_source


class ItalianAgencyEvidenceTests(unittest.TestCase):
    host = "agency.example"
    url = "https://agency.example/jobs/123"
    stamp = "2026-11-23T18:00:00Z"
    source = dict(id="agency", employer="Agency", adapter="employer-sitemap",
                  allowed_hosts=[host], italian_agency_slug_triage=True)

    def replay(self, description, deadline="2026-12-01", listed=True, message="", posted=None, source=None):
        posting = dict(title="Stage HR", description=description, validThrough=deadline,
                       hiringOrganization={"name": "Agency"},
                       jobLocation={"address": {"addressCountry": "IT"}},
                       identifier={"value": "123"})
        posting["@type"] = "JobPosting"
        if posted:posting["datePosted"] = posted
        body = (f'<h1>Stage HR</h1><p>{message}</p><script type="application/ld+json">'
                + json.dumps(posting) + "</script>").encode()
        record = dict(source_id="agency", external_id=self.url, employer="Agency",
                      url=self.url, apply_url=self.url, needs_page=True,
                      agency_sitemap_current=listed)
        client = Mock()
        client.request.return_value = (body, 200, self.url)
        with patch("collector.pipeline.collect", return_value=[record]):
            return process_source(source or self.source, client, self.stamp)["jobs"]

    def test_sitemap_and_live_structured_deadline_support_current_listing_only(self):
        job, = self.replay("Supporto al recruitment.")
        self.assertEqual(job["student_eligibility"], "not_stated")
        self.assertEqual(job["status"], "open")
        self.assertEqual(job["verification"]["reason"], "official-sitemap-live-jobposting")
        self.assertNotIn("application_verification", job)

    def test_confirmed_student_without_current_listing_evidence_stays_a_lead(self):
        job, = self.replay("Tirocinio curriculare.", listed=False)
        self.assertEqual(job["student_eligibility"], "confirmed")
        self.assertEqual(job["status"], "unverified")

    def test_explicit_exclusion_or_closed_vacancy_cannot_become_current(self):
        self.assertEqual(self.replay("Tirocinio extracurriculare."), [])
        job, = self.replay("Tirocinio curriculare.", message="L'annuncio non è più disponibile.")
        self.assertEqual(job["status"], "closed")

    def test_italian_dates_are_unambiguous_and_contradictory_deadlines_are_not_closure(self):
        source=dict(self.source,jobposting_date_format="%d/%m/%Y")
        job,=self.replay("Stage HR per laureandi.", posted="12/11/2026", source=source)
        self.assertEqual(job["published_at"], "2026-11-12")
        self.assertEqual(job["status"], "open")
        job,=self.replay("Stage HR per laureandi.", posted="12/11/2026",
                         deadline="1970-04-01", source=source)
        self.assertIsNone(job["valid_through"])
        self.assertEqual(job["status"], "unverified")
