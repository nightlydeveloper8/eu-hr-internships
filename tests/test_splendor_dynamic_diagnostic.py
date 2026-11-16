"""No-network regressions for safe one-off dynamic application inspection."""
from unittest import TestCase
from scripts.diagnose_splendor_dynamic import inspect

HOST="splendorplant.careers.haileyhr.app"
URL="https://"+HOST+"/sv-SE/job/safe-job-id"
TITLE="HR-praktik VT27 bygg vår HR Hub hos Splendor Plant"
OFFICIAL="HR-praktik – bygg vår HR Hub hos Splendor Plant"


def candidate(**extra):
    a=dict(provider="jobtech-se",provider_id="31613684",
           verification_state="unverified",country="SE",title=TITLE,
           apply_url=URL,employer="Splendor Plant Aktiebolag")
    a.update(extra)
    return a


def body(form=False):
    fields=("<form id='application'><input name='name'>"
            "<input type='email' name='email'><input type='file' name='cv'>"
            "<button type='submit'>Ansök</button></form>") if form else "<button type='button'>Ansök</button>"
    return (f"<html><main><h1>{OFFICIAL}</h1>{fields}</main></html>").encode()


class FakeClient:
    def __init__(self,seconds,max_requests,delay):
        self.requests=0;self.bytes=0;self.redirect_scope_allowed=None


class DynamicDiagnosticTests(TestCase):
    def test_rendered_current_job_with_enabled_form_is_only_a_preflight(self):
        def render(url,client,allowed,**opts):
            self.assertTrue(allowed(url))
            self.assertFalse(allowed("https://other.example/js"))
            self.assertTrue(opts["application_read"])
            self.assertFalse(opts["application_toggle"])
            self.assertEqual(opts["limit"],1)
            client.requests+=1;client.bytes+=len(body(True))
            opts["metrics"].update(browser_requests=1,blocked_requests=0,browser_bytes=len(body(True)))
            return [(url,body(True))],True
        result=inspect(candidate(),approved_host=HOST,
                       client_factory=FakeClient,render=render)
        self.assertEqual(result["state"],"rendered-enabled-form-preflight-only")
        self.assertTrue(result["academic_term_variant"])
        self.assertFalse(result["exact_title"])
        self.assertTrue(result["enabled_applicant_form"])
        self.assertEqual(result["renderings"],1)
        self.assertEqual(result["verified_vacancies_added"],0)
        self.assertFalse(result["production_activated"])

    def test_cta_only_is_not_a_verified_form(self):
        result=inspect(candidate(),approved_host=HOST,client_factory=FakeClient,
                       render=lambda u,c,a,**kw: ([(u,body(False))],True))
        self.assertEqual(result["state"],"rendered-CTA-only-form-not-established")
        self.assertFalse(result["enabled_applicant_form"])

    def test_browser_restriction_remains_unknown_not_closed(self):
        def blocked(*args,**kwargs):
            raise ValueError("Dynamic browser request denied: unapproved JS host")
        out=inspect(candidate(),approved_host=HOST,client_factory=FakeClient,render=blocked)
        self.assertEqual(out["state"],"incomplete-access-or-render")
        self.assertNotIn("closed",out["state"])
        self.assertEqual(out["verified_vacancies_added"],0)

    def test_never_browse_unapproved_or_non_jobtech_urls(self):
        def network(*args,**kwargs):
            raise AssertionError("Network must not be called")
        out=inspect(candidate(apply_url="https://attacker.example/job"),
                    approved_host=HOST,client_factory=network,render=network)
        self.assertEqual(out["state"],"review-required")
        self.assertEqual(out["requests"],0)
        out=inspect(candidate(provider="eures-authorized-input"),
                    approved_host=HOST,client_factory=network,render=network)
        self.assertEqual(out["state"],"review-required")
