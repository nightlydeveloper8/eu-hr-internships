"""An explicitly undisclosed client is attributed to the reviewed agency."""
import json
import unittest
from unittest.mock import Mock, patch

from collector.pipeline import process_source


class AgencyClientTests(unittest.TestCase):
    url = "https://agency.example/jobs/123"
    stamp = "2026-11-23T17:45:40+00:00"
    source = dict(id="agency", employer="Example Agency", adapter="employer-index",
                  allowed_hosts=["agency.example"], staffing_agency=True)

    def collect_posting(self, description, source=None):
        data = {
            "@type": "JobPosting",
            "title": "Stage curriculare risorse umane",
            "description": description,
            "hiringOrganization": {"name": "Example Agency"},
            "jobLocation": {"address": {"addressCountry": "IT"}},
        }
        body = '<script type="application/ld+json">' + json.dumps(data) + '</script>'
        record = dict(source_id="agency", external_id="123", employer="Example Agency",
                      url=self.url, apply_url=self.url, needs_page=True)
        client = Mock()
        client.request.return_value = (body.encode(), 200, self.url)
        with patch("collector.pipeline.collect", return_value=[record]):
            result = process_source(source or self.source, client, self.stamp, verify=False)
        self.assertEqual(len(result["jobs"]), 1)
        return result["jobs"][0]

    def test_explicit_undisclosed_client_is_exported_without_a_name(self):
        job = self.collect_posting(
            "Stage curriculare per studenti in selezione e risorse umane. Azienda cliente non indicata."
        )
        self.assertEqual(job["employer"], "Example Agency")
        self.assertEqual(job["agency_client"], "non indicato")
        self.assertNotIn("description", job)

    def test_generic_client_reference_and_named_client_are_not_assertions(self):
        for sentence in ("Presso azienda cliente.", "Azienda cliente: ACME."):
            with self.subTest(sentence=sentence):
                job = self.collect_posting("Stage curriculare per studenti in risorse umane. " + sentence)
                self.assertNotIn("agency_client", job)

    def test_only_reviewed_agency_sources_emit_client_status(self):
        job = self.collect_posting(
            "Stage curriculare per studenti in risorse umane. Cliente non indicato.",
            dict(self.source, staffing_agency=False),
        )
        self.assertNotIn("agency_client", job)
