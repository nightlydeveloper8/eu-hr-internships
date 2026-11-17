"""Offline policy-v2 reuse and host-scope regressions for feed -> application."""
from unittest import TestCase
from urllib.parse import urlsplit
from collector.official_feed_verification import verify_candidate, verify_candidates, academic_term_title_variant


TITLE = "HR Internship in Talent Acquisition and Recruitment"
APP = "https://jobs.example.test/jobs/hr-internship-recruitment"
OWNER = "Example Sweden AB"

def candidate(**overrides):
    row = dict(provider="jobtech-se", provider_id="31558200", country="SE",
               employer=OWNER, title=TITLE,
               url="https://arbetsformedlingen.se/platsbanken/annonser/31558200",
               apply_url=APP, verification_state="unverified")
    row.update(overrides)
    return row


def html(title=TITLE, employer=OWNER, disabled=False):
    import json
    job = {"@context":"https://schema.org","@type":"JobPosting",
           "title":title,"hiringOrganization":{"@type":"Organization","name":employer}}
    return (('<html><body><main><h1>'+title+'</h1>'
       + '<script type="application/ld+json">'+json.dumps(job)+'</script>'
       + '<form action="/apply" id="application">'
       + '<input type="text" name="first_name">'
       + '<input type="email" name="email">'
       + '<input type="file" name="cv">'
       + '<button type="submit"'+(' disabled' if disabled else '')+'>Apply</button>'
       + '</form></main></body></html>').encode())


class FakeClient:
    bodies = {}
    def __init__(self, seconds, max_requests, delay):
        self.requests = 0
        self.bytes = 0
        self.redirect_scope_allowed = None

    def request(self,url,**kwargs):
        self.requests += 1
        body, final = self.bodies.get(url, (b"",url))
        if self.redirect_scope_allowed and not self.redirect_scope_allowed(final):
            raise ValueError("Redirect outside approved source scope")
        self.bytes += len(body)
        return body,200,final


class VerifyLicensedFeedTests(TestCase):
    def run_candidate(self, record=None, body=None, final=None, hosts=None):
        if record is None: record=candidate()
        url=record.get("apply_url",APP)
        FakeClient.bodies={url:(body if body is not None else html(),final or url)}
        return verify_candidate(record,hosts if hosts is not None else {urlsplit(url).hostname},
                                client_factory=FakeClient)

    def test_current_same_title_owner_and_enabled_form_only_review_not_catalog(self):
        report=self.run_candidate()
        self.assertEqual(report["state"],"same-vacancy-form-and-owner-evidence")
        self.assertTrue(report["vacancy_match"])
        self.assertTrue(report["enabled_form"])
        self.assertEqual(report["employer_identity_evidence"],
                         "same-vacancy-jobposting-hiring-organization")
        self.assertFalse(report["added_verified_internship"])
        self.assertEqual(report["requests"],1)
        self.assertEqual(report["renderings"],0)

    def test_no_title_match_or_wrong_employer_never_auto_verifies(self):
        wrong_title=self.run_candidate(body=html(title="Sales manager"))
        self.assertEqual(wrong_title["state"],"unverified")
        self.assertFalse(wrong_title["enabled_form"])
        wrong_owner=self.run_candidate(body=html(employer="Wrong Company Ltd"))
        self.assertEqual(wrong_owner["state"],"form-observed-employer-identity-unverified")
        self.assertTrue(wrong_owner["enabled_form"])
        self.assertFalse(wrong_owner["added_verified_internship"])

    def test_disabled_submit_not_a_verified_form(self):
        row=self.run_candidate(body=html(disabled=True))
        self.assertNotEqual(row["state"],"same-vacancy-form-and-owner-evidence")
        self.assertFalse(row["enabled_form"])

    def test_host_not_explicitly_approved_costs_zero_requests(self):
        FakeClient.bodies={APP:(html(),APP)}
        row=verify_candidate(candidate(),{"different.example"},client_factory=FakeClient)
        self.assertEqual(row["state"],"host-review-required")
        self.assertEqual(row["requests"],0)

    def test_cross_host_redirect_and_bad_input_fail_closed(self):
        row=self.run_candidate(final="https://another.example/path")
        self.assertEqual(row["state"],"unverified")
        no_url=self.run_candidate(record=candidate(apply_url=None))
        self.assertEqual(no_url["requests"],0)
        self.assertFalse(no_url["added_verified_internship"])
        self.assertEqual(self.run_candidate(record=candidate(country="NL"))["requests"],0)

    def test_no_unapproved_batch_or_more_than_five_hosts(self):
        doc=dict(provider="jobtech-se",mode="discovery-only",
                 candidates=[candidate(),candidate(provider_id="123")])
        with self.assertRaises(ValueError):
            verify_candidates(doc,[],client_factory=FakeClient)
        with self.assertRaises(ValueError):
            verify_candidates(doc,["one.example"]*6,client_factory=FakeClient)
        with self.assertRaises(ValueError):
            verify_candidates(doc,["jobs.example.test"],max_candidates=6,
                              client_factory=FakeClient)
        FakeClient.bodies={APP:(html(),APP)}
        out=verify_candidates(doc,["jobs.example.test"],max_candidates=2,
                              client_factory=FakeClient)
        self.assertEqual(out["candidates_attempted"],2)
        self.assertEqual(out["verified_vacancies_added"],0)
        self.assertEqual(out["applications_submitted"],0)
        self.assertFalse(out["production_enabled"])
        self.assertEqual(out["renderings"],0)


    def test_sweden_term_marker_drifts_are_diagnostic_not_verified(self):
        self.assertTrue(academic_term_title_variant(
            "HR Internship VT27 in Talent Acquisition and Recruitment", "HR Internship in Talent Acquisition and Recruitment"))
        self.assertFalse(academic_term_title_variant(
            "HR Internship VT27 in Talent Acquisition and Recruitment", "HR Internship Payroll"))
        self.assertFalse(academic_term_title_variant(
            "HR Internship VT27 HT26 in Talent Acquisition and Recruitment", "HR Internship in Talent Acquisition and Recruitment"))
        self.assertFalse(academic_term_title_variant(
            "Sales VT27", "Sales"))
        row=self.run_candidate(record=candidate(title="HR Internship VT27 in Talent Acquisition and Recruitment"),
                               body=html(title="HR Internship in Talent Acquisition and Recruitment"))
        self.assertEqual(row["state"],"seasonal-title-variant-form-observed-review-required")
        self.assertTrue(row["seasonal_title_variant"])
        self.assertFalse(row["vacancy_match"])
        self.assertTrue(row["enabled_form"])
        self.assertFalse(row["added_verified_internship"])

    def test_same_host_explicit_legal_page_can_add_separate_owner_evidence(self):
        raw=html(employer="Other Recruiting Provider")
        raw=raw.replace(b"</main>",b'<a href="/privacy-policy">Privacy Policy</a></main>')
        FakeClient.bodies={
            APP:(raw,APP),
            "https://jobs.example.test/privacy-policy":(
                b"<html><body>Registered employer: Example Sweden AB</body></html>",
                "https://jobs.example.test/privacy-policy")}
        row=verify_candidate(candidate(),{"jobs.example.test"},client_factory=FakeClient)
        self.assertEqual(row["state"],"same-vacancy-form-and-owner-evidence")
        self.assertEqual(row["employer_identity_evidence"],
                         "same-host-legal-page-names-employer")
        self.assertEqual(row["requests"],2)
        self.assertFalse(row["added_verified_internship"])

    def test_cross_host_legal_link_does_not_grant_owner_status(self):
        raw=html(employer="Other Recruiting Provider")
        raw=raw.replace(b"</main>",b'<a href="https://other.example/privacy">Privacy Policy</a></main>')
        FakeClient.bodies={APP:(raw,APP)}
        row=verify_candidate(candidate(),{"jobs.example.test"},client_factory=FakeClient)
        self.assertEqual(row["state"],"form-observed-employer-identity-unverified")
        self.assertEqual(row["requests"],1)


    def test_reject_non_jobtech_candidate_and_no_independent_identity_assumption(self):
        a=self.run_candidate(record=candidate(provider="eures-authorized-input"))
        self.assertEqual(a["state"],"unverified")
        self.assertEqual(a["requests"],0)
        b=self.run_candidate(body=html(employer=""))
        self.assertEqual(b["state"],"form-observed-employer-identity-unverified")
