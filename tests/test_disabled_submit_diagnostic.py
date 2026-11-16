"""Disabled Personio-style submit is diagnostic-only, never verified policy v2."""
import unittest

from collector.applications import ApplicantForms
from collector.dynamic_ats import MissingDynamicForm
from collector.verification import applicant_form, disabled_submit_applicant_form, verify_vacancy

URL = "https://example.jobs.personio.de/job/2540621"
APPLY = URL + "/apply"
STAMP = "2026-11-16T17:00:00+00:00"
SOURCE = {"id":"test", "employer":"Employer", "adapter":"lever",
          "allowed_hosts":["example.jobs.personio.de"]}
RECORD = {"source_id":"test", "external_id":"2540621", "posting_identifier":"2540621",
          "employer":"Employer", "title":"HR Intern", "text":"HR tasks",
          "url":URL, "apply_url":APPLY, "inventory_evidence":"current-employer-feed"}

def form(submit='disabled', attributes='class="DynamicForm_formContainer__PHnT_"'):
    button = '<button type="submit" '+submit+'>Apply</button>'
    return ('<form '+attributes+'>'
        '<input type="text" name="first_name">'
        '<input type="text" name="last_name">'
        '<input type="email" name="email">'
        '<input type="file" name="documents.cv">'
        +button+'</form>')

class Pages:
    def __init__(self, pages):
        self.pages=pages
        self.calls=[]
    def request(self,url,**kwargs):
        self.calls.append(url)
        return self.pages[url].encode(),200,url

class DisabledSubmitTests(unittest.TestCase):
    def test_personio_like_disabled_form_detected_but_not_verified(self):
        body=form().encode()
        self.assertFalse(applicant_form(body,strict=True))
        self.assertTrue(disabled_submit_applicant_form(body))
        forms=ApplicantForms(body,strict=True).forms
        self.assertEqual(forms[0]["disabled_submits"],1)
        self.assertFalse(forms[0]["submit"])

    def test_disabled_aria_and_class_supported(self):
        for disabled in ('aria-disabled="true"', 'class="disabled"'):
            with self.subTest(disabled=disabled):
                self.assertTrue(disabled_submit_applicant_form(form(disabled).encode()))

    def test_enabled_submit_still_only_normal_verification(self):
        body=form("").encode()
        self.assertFalse(disabled_submit_applicant_form(body))
        self.assertTrue(applicant_form(body,strict=True))

    def test_newsletter_contact_missing_submit_and_hidden_are_not_applicant(self):
        cases=[
            form(attributes='id="newsletter"'),
            '<form id="application"><input name="email"><button disabled type="submit">Subscribe</button></form>',
            '<form id="application"><input name="first_name"><input name="email"><button disabled type="submit">Apply</button></form>',
            '<div hidden>'+form()+'</div>',
            form().replace('<button type="submit" disabled>Apply</button>', ''),
        ]
        for candidate in cases:
            with self.subTest(body=candidate[:65]):
                self.assertFalse(disabled_submit_applicant_form(candidate.encode()))

    def test_same_vacancy_form_with_disabled_submit_is_incomplete_without_fallback(self):
        pages=Pages({URL:'<h1>HR Intern</h1>'+form()})
        with self.assertRaisesRegex(ValueError, "submit disabled in initial HTML") as exc:
            verify_vacancy(RECORD,SOURCE,pages,STAMP)
        self.assertNotIsInstance(exc.exception,MissingDynamicForm)
        self.assertEqual(pages.calls,[URL])

    def test_application_child_with_disabled_submit_is_also_incomplete(self):
        pages=Pages({URL:'<h1>HR Intern</h1><a href="/job/2540621/apply">Apply</a>',
                     APPLY:'<h1>HR Intern</h1>'+form()})
        with self.assertRaisesRegex(ValueError, "submit disabled in initial HTML"):
            verify_vacancy(RECORD,SOURCE,pages,STAMP)
        self.assertEqual(pages.calls,[URL,APPLY])

    def test_other_ats_keep_dynamic_fallback_and_existing_exclusion_logic(self):
        url = "https://example.org/jobs/2540621"
        other = dict(RECORD,url=url,apply_url=url+"/apply")
        source = dict(SOURCE,allowed_hosts=["example.org"])
        pages=Pages({url:'<h1>HR Intern</h1>'+form()})
        with self.assertRaises(MissingDynamicForm):
            verify_vacancy(other,source,pages,STAMP)
        self.assertEqual(pages.calls,[url])

    def test_an_enabled_form_remains_eligible_without_policy_relaxation(self):
        pages=Pages({URL:'<h1>HR Intern</h1>'+form(submit="")})
        result=verify_vacancy(RECORD,SOURCE,pages,STAMP)
        self.assertEqual(result["method"],"same-vacancy-applicant-form")

if __name__=="__main__":
    unittest.main()
