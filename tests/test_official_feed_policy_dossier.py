"""Offline end-to-end policy-v2 dossier: public JobTech → employer ATS."""
from unittest import TestCase
from collector.official_feed_policy_dossier import review,ats_parent

HOST="jobb.jobandtalent.com"
TITLE="Praktik inom HR och rekrytering i Malmö - våren 2027"
PARENT="https://"+HOST+"/jobs/8503489-praktik-inom-hr-och-rekrytering-i-malmo-varen-2027"
APP=PARENT+"/applications/new?promotion=2231065-arbetsformedlingen"
SITEMAP="https://"+HOST+"/sitemap"
LEGAL="https://"+HOST+"/privacy-policy"


def candidate(**updates):
    row=dict(provider="jobtech-se",provider_id="31558200",employer="Jobandtalent Sweden AB",
             title=TITLE,country="SE",city="Malmö",
             workplace_country_evidence=True,verification_state="unverified",
             url="https://arbetsformedlingen.se/platsbanken/annonser/31558200",
             apply_url=APP)
    row.update(updates)
    return row


def html_pages():
    app=(f"<html><main><h1>{TITLE}</h1>"
         f"<a href='{LEGAL}'>Privacy Policy</a>"
         "<form id='apply'><input name='full_name'>"
         "<input name='email' type='email'><input name='cv' type='file'>"
         "<button type='submit'>Apply</button></form>"
         "</main></html>").encode()
    parent=(f"<html><main><h1>{TITLE}</h1>"
            f"<p>Plats: Malmö, Hyllie</p><a href='{APP}'>Ansök</a>"
            "</main></html>").encode()
    index=(f"<html><body><a href='/jobs/8503489-praktik-inom-hr-och-rekrytering-i-malmo-varen-2027'>"
           f"{TITLE}</a></body></html>").encode()
    return {APP:app,PARENT:parent,SITEMAP:index,
            LEGAL:b"<html><main>Personuppgiftsansvarig Jobandtalent Sweden AB</main></html>"}


class FakeBudget:
    pages=html_pages()
    def __init__(self,seconds,max_requests,delay):
        self.requests=0;self.bytes=0;self.redirect_scope_allowed=None
    def request(self,url,**kwargs):
        self.requests+=1
        if url not in self.pages:
            raise ValueError("Missing reviewed page")
        if self.redirect_scope_allowed and not self.redirect_scope_allowed(url):
            raise ValueError("Redirect outside preflight scope")
        body=self.pages[url];self.bytes+=len(body)
        return body,200,url


class PolicyReviewTests(TestCase):
    def setUp(self):
        FakeBudget.pages=html_pages()

    def test_ats_identifier_does_not_conflate_with_jobtech_id(self):
        result=ats_parent(APP,HOST)
        self.assertEqual(result["ats_id"],"8503489")
        self.assertEqual(result["job_page"],PARENT)
        self.assertIsNone(ats_parent(APP,"attacker.example"))
        self.assertIsNone(ats_parent(PARENT+"/other/job","jobb.jobandtalent.com"))

    def test_exact_employer_source_and_application_full_staging_pass(self):
        out=review(candidate(),approved_host=HOST,approved_inventory_url=SITEMAP,
                   client_factory=FakeBudget)
        self.assertEqual(out["status"],"policy-v2-evidence-passed-staging-only",out.get("reason"))
        self.assertEqual(out["ats_posting_id"],"8503489")
        self.assertEqual(out["public_id"],"31558200")
        self.assertEqual(out["application_proof_method"],"linked-same-vacancy-applicant-form")
        self.assertTrue(out["official_inventory_confirmed"])
        self.assertTrue(out["employer_city_match"])
        self.assertEqual(out["owner_evidence"],"same-host-legal-page-names-employer")
        self.assertEqual(out["requests"],5)
        self.assertEqual(out["verified_vacancies_added"],0)
        self.assertFalse(out["catalogue_entry_created"])
        self.assertFalse(out["production_activated"])

    def test_no_proof_when_feed_country_or_city_is_unestablished(self):
        a=review(candidate(workplace_country_evidence=False),approved_host=HOST,
                 approved_inventory_url=SITEMAP,client_factory=FakeBudget)
        self.assertEqual(a["status"],"review-required")
        self.assertEqual(a["requests"],0)
        b=review(candidate(city=""),approved_host=HOST,
                 approved_inventory_url=SITEMAP,client_factory=FakeBudget)
        self.assertEqual(b["status"],"review-required")
        self.assertEqual(b["verified_vacancies_added"],0)

    def test_wrong_employer_or_no_official_inventory_cannot_pass(self):
        FakeBudget.pages[LEGAL]=b"<html><main>Other Company AB</main></html>"
        a=review(candidate(),approved_host=HOST,
                 approved_inventory_url=SITEMAP,client_factory=FakeBudget)
        self.assertEqual(a["status"],"review-required")
        self.assertIn("ownership",a["reason"])
        FakeBudget.pages=html_pages()
        FakeBudget.pages[SITEMAP]=b"<html>No job listing</html>"
        b=review(candidate(),approved_host=HOST,
                 approved_inventory_url=SITEMAP,client_factory=FakeBudget)
        self.assertEqual(b["status"],"review-required")
        self.assertFalse(b["official_inventory_confirmed"])

    def test_employer_page_without_source_city_or_same_position(self):
        FakeBudget.pages[PARENT]=(f"<html><main><h1>{TITLE}</h1>"
                                  f"<a href='{APP}'>Ansök</a></main></html>").encode()
        a=review(candidate(),approved_host=HOST,
                 approved_inventory_url=SITEMAP,client_factory=FakeBudget)
        self.assertEqual(a["status"],"review-required")
        self.assertIn("city",a["reason"])
        FakeBudget.pages=html_pages()
        FakeBudget.pages[PARENT]=b"<html><main><h1>Different internship</h1></main></html>"
        b=review(candidate(),approved_host=HOST,
                 approved_inventory_url=SITEMAP,client_factory=FakeBudget)
        self.assertEqual(b["status"],"review-required")
