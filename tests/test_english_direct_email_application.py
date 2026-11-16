"""English direct email application requires same-vacancy affirmative instructions.

No emails are sent; these are all synthetic offline fixtures.
"""
import unittest
from collector.verification import verify_vacancy

URL="https://pandoo.lu/hr-intern-f/m/d"
SOURCE=dict(id="eu-pandoo-review",employer="PANDOO Administration",
            application_check="official-email",application_email="hr@pandoo.lu",
            allowed_hosts=["pandoo.lu"])
RECORD=dict(source_id="eu-pandoo-review",external_id="pandoo-hr-2026",
            employer="PANDOO Administration",title="HR Intern (F/M/D)",url=URL,
            apply_url=URL,inventory_evidence="current-employer-careers-index",
            text="Six month internship in HR administration, recruiting and HRIS")
STAMP="2026-11-16T18:00:00+00:00"

class Pages:
    def __init__(self, html):self.html=html;self.requests=0
    def request(self,url,**kwargs):
        self.requests+=1
        return self.html.encode(),200,url

def html(body, address="hr@pandoo.lu", label="Apply now"):
    return ('<main><h1>HR Intern (F/M/D)</h1><p>'+body+'</p>'
            '<a href="mailto:'+address+'">'+label+'</a></main>')

class EnglishDirectEmailTests(unittest.TestCase):
    def test_explicit_official_email_on_exact_job_is_confirmed_without_delivery_claim(self):
        page=Pages(html("If you are interested, please send us your application."))
        proof=verify_vacancy(RECORD,SOURCE,page,STAMP)
        self.assertEqual(proof["method"],"official-vacancy-email-instructions")
        self.assertEqual(proof["application_email"],"hr@pandoo.lu")
        self.assertFalse(proof["delivery_verified"])
        self.assertEqual(proof["inventory"],"current-employer-careers-index")
        self.assertEqual(page.requests,1)

    def test_generic_contact_and_email_without_invitation_never_qualifies(self):
        bodies=["If you have questions, contact us.",
                "Please send us your questions about this opportunity.",
                "You can ask us about the role or subscribe to future alerts."]
        for body in bodies:
            with self.subTest(body=body),self.assertRaisesRegex(ValueError,"email application instructions"):
                verify_vacancy(RECORD,SOURCE,Pages(html(body)),STAMP)

    def test_wrong_address_generic_label_negation_and_wrong_role_rejected(self):
        variants=[
            html("If interested, please send us your application.","hello@pandoo.lu"),
            html("If interested, please send us your application.",label="Contact us"),
            html("Please do not send us your application."),
            html("Please send us your application.").replace("<h1>HR Intern (F/M/D)</h1>","<h1>Fund Accountant</h1>"),
            html("Please send us your application.").replace('mailto:hr@pandoo.lu','href="https://example.com"'),
        ]
        for case in variants:
            with self.subTest(case=case[-85:]),self.assertRaises(ValueError):
                verify_vacancy(RECORD,SOURCE,Pages(case),STAMP)

    def test_english_mailto_does_not_override_explicit_closed_notice(self):
        page=Pages(html("HR Intern has been filled. If interested, please send us your application."))
        with self.assertRaises(ValueError):
            verify_vacancy(RECORD,SOURCE,page,STAMP)

    def test_no_registration_of_email_from_unreviewed_source(self):
        source=dict(SOURCE,application_email="info@pandoo.lu")
        with self.assertRaises(ValueError):
            verify_vacancy(RECORD,source,Pages(html("Please send us your application.")),STAMP)

if __name__=="__main__":unittest.main()
