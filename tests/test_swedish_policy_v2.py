"""Strict, standalone policy-v2 regression for Swedish employer ATS vacancy."""
from datetime import datetime,timezone
from unittest import TestCase
from urllib.parse import urlsplit
from collector.verification import _verify_vacancy, same_requisition

TITLE="Praktik inom HR och rekrytering i Malmö - våren 2027"
PARENT="https://jobb.jobandtalent.com/jobs/8503489-praktik-inom-hr-och-rekrytering-i-malmo-varen-2027"
CHILD=PARENT+"/applications/new?promotion=2231065-arbetsformedlingen"


class FakeClient:
    def __init__(self,body,child_body):
        self.pages={PARENT:body,CHILD:child_body}
        self.requests=0
    def request(self,url,**kwargs):
        self.requests+=1
        return self.pages[url],200,url


def parent_html(label="Ansök",target=CHILD):
    return (f"<html><body><main><h1>{TITLE}</h1>"
            f"<p>Plats: Malmö, Hyllie</p>"
            f"<a href='{target}'>{label}</a>"
            f"</main></body></html>").encode()


def applicant_html(title=TITLE,enabled=True):
    disabled="" if enabled else " disabled"
    return (f"<html><body><main><h1>{title}</h1>"
            f"<form id='application' action='/jobs/8503489/applications'>"
            "<input name='first_name' type='text'>"
            "<input name='email' type='email'>"
            "<input name='cv' type='file'>"
            f"<button type='submit'{disabled}>Ansök</button>"
            "</form></main></body></html>").encode()


def case(body=None,child=None):
    client=FakeClient(body or parent_html(),child or applicant_html())
    record=dict(title=TITLE,url=PARENT,apply_url=CHILD,
                external_id="8503489",posting_identifier="8503489",
                employer="Jobandtalent Sweden AB",inventory_evidence="official-employer-job-page")
    source=dict(id="pilot-se-8503489",adapter="employer-index",
                employer="Jobandtalent Sweden AB",
                allowed_hosts=["jobb.jobandtalent.com"])
    return _verify_vacancy(record,source,client,datetime.now(timezone.utc).isoformat()),client


class SwedishATSIdentityTests(TestCase):
    def test_parent_child_requisition_relationship(self):
        self.assertTrue(same_requisition(PARENT,CHILD))
        self.assertFalse(same_requisition(PARENT,PARENT+"/applications/new-unknown"))
        self.assertFalse(same_requisition(PARENT,"https://other.example/jobs/8503489/applications/new"))
        self.assertFalse(same_requisition(PARENT,"https://jobb.jobandtalent.com/jobs/9999-other/applications/new"))

    def test_swedish_apply_link_plus_same_title_enabled_form_passes_existing_verifier(self):
        proof,client=case()
        self.assertEqual(proof["url"],CHILD)
        self.assertEqual(proof["method"],"linked-same-vacancy-applicant-form")
        self.assertEqual(proof["vacancy_match"],"title")
        self.assertEqual(proof["inventory"],"official-employer-job-page")
        self.assertEqual(client.requests,2)

    def test_other_position_child_or_disabled_form_fails(self):
        with self.assertRaisesRegex(ValueError,"different vacancy|same vacancy|matching vacancy identifier"):
            case(body=parent_html(target="https://jobb.jobandtalent.com/jobs/9999-something/applications/new"))
        with self.assertRaises(ValueError):
            case(child=applicant_html(enabled=False))
        with self.assertRaises(ValueError):
            case(child=applicant_html(title="Sales representative"))

    def test_no_invented_link_from_source(self):
        with self.assertRaises(ValueError):
            case(body=parent_html(target=PARENT))
