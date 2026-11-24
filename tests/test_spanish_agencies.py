"""Reviewed Spanish agency formats, eligibility and staging safety."""
import json
import unittest
from unittest.mock import Mock

from collector.adapters import collect
from collector.classify import classify_spanish_agency_role, student_eligibility_for_country
from collector.daily import provision
from collector.employer_pages import spanish_agency_slug_candidate
from collector.pipeline import ROOT
from collector.verification import teamtailor_published_listing


class SpanishAgencyTests(unittest.TestCase):
    def test_slug_extracts_adecco_hash_and_catalan_teamtailor_route(self):
        self.assertTrue(spanish_agency_slug_candidate(
            "https://www.adecco.com/es-es/ofertas-trabajo/beca-rrhh-alicante/13fd849e977a82f7100bd1df2807d265"))
        self.assertTrue(spanish_agency_slug_candidate(
            "https://empleo.gruporas.es/jobs/8766398-becari-a-de-seleccio-de-personal"))
        self.assertFalse(spanish_agency_slug_candidate(
            "https://www.example.com/rrhh/tecnico-administrativo-321277?query=beca"))

    def test_reviewed_catalan_and_spanish_hr_titles(self):
        self.assertIsNotNone(classify_spanish_agency_role("BECARI/A DE RRHH"))
        self.assertIsNotNone(classify_spanish_agency_role("Beca Selección", "Procesos de selección de personal."))
        self.assertIsNone(classify_spanish_agency_role("Beca Selección", "Selección musical para radio."))
        self.assertEqual(student_eligibility_for_country("ES", "Beca RRHH",
            "Si eres estudiante y buscas compaginar tus estudios.", ""), "confirmed")

    def test_same_job_frame_does_not_infer_an_application(self):
        url="https://empleo.gruporas.es/jobs/123456-beca-rrhh"
        stamp="2026-11-24T09:00:00Z"
        posted="2026-11-13T09:00:00+01:00"
        frame=f'<turbo-frame id="application_form" src="{url}/applications/new"></turbo-frame>'.encode()
        self.assertTrue(teamtailor_published_listing(frame,url,posted,stamp))
        self.assertFalse(teamtailor_published_listing(frame,url.replace("123456","123457"),posted,stamp))
        self.assertFalse(teamtailor_published_listing(frame,url,"2026-12-25T09:00:00Z",stamp))

    def test_lot_stays_disabled_and_provisioning_is_idempotent(self):
        companies,sources=[json.loads((ROOT/"data"/name).read_text()) for name in ("companies.json","sources.json")]
        lot=[source for source in sources if source.get("collection_lot")=="AGENZIE-ES"]
        self.assertEqual({s["id"] for s in lot},{"held-adecco-es-jobposting","held-grupo-ras-es-jobposting"})
        for source in lot:
            self.assertIs(source["enabled"],False)
            self.assertIs(source["collection_activation_hold"],True)
            client=Mock()
            with self.assertRaisesRegex(ValueError,"collection activation hold"):
                collect(dict(source,enabled=True),client)
            self.assertEqual(client.mock_calls,[])
        self.assertEqual(provision(companies,sources),(companies,sources))
