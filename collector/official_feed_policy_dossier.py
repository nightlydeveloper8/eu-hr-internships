"""Final read-only policy-v2 dossier for a public-feed employer ATS vacancy.

The employer's own named job page, its observed same-position application,
workplace and employer identity are mandatory. JobTech and ATS IDs are kept
separate. No source registration or catalog publication occurs here.
"""
from datetime import datetime, timezone
from urllib.parse import urlsplit, urlunsplit, urljoin
import re
import time
from .classify import canonical_url, fold, plain, classify_role
from .official_feed_discovery import https_url
from .official_feed_verification import CapturedClient, verify_candidate
from .runtime import BudgetClient
from .verification import _verify_vacancy, blocked_error, same_title, same_requisition, applicant_form, structured_identifiers, expired
from .universal import Document
from .applications import ensure_open_document, checked_document, ApplicantForms
from .dynamic_ats import MissingDynamicForm


def ats_parent(application_url, host):
    checked=https_url(application_url,{host})
    if not checked:
        return None
    p=urlsplit(checked)
    m=re.fullmatch(r"(?P<parent>/jobs/(?P<id>\d{5,12})-[a-z0-9-]+)/applications/new/?",p.path)
    if not m:
        return None
    return dict(job_page=urlunsplit(("https",host,m["parent"],"","")),
                ats_id=m["id"],application_url=checked)



def _published_source_child_fallback(candidate, vacancy, source, captured):
    """Specific known Teamtailor path when employer CTA is a non-link button.

    The caller has already read an identified employer parent. The external
    public feed supplied the child URL, not the parser. No CTA target is
    invented from a button. Separate ID/path, identical title, published
    employer CTA and strict same-vacancy form all remain mandatory.
    """
    parent_url=vacancy["url"]
    app_url=vacancy["apply_url"]
    body=captured.pages.get(canonical_url(parent_url))
    if not body:
        raise ValueError("Current employer vacancy HTML unavailable")
    doc=Document(body,parent_url)
    ensure_open_document(doc)
    if not same_title(doc,vacancy["title"]):
        raise ValueError("Current employer page does not name the same role")
    if not same_requisition(parent_url,app_url):
        raise ValueError("Observed application URL does not belong to employer ATS job")
    if not re.search(r"\b(?:skicka\s+ansokan|ansok|ansokan)\b",fold(doc.text)):
        raise ValueError("Employer vacancy has no visible applicant CTA")
    # An existing Teamtailor parent→child path with one fixed ATS ID is
    # required. Do not accept generic /apply, locale pages, or wrong IDs.
    parent=ats_parent(app_url,urlsplit(parent_url).hostname)
    if not parent or canonical_url(parent["job_page"])!=canonical_url(parent_url):
        raise ValueError("Source application ATS ID differs from current employer vacancy")
    if str(vacancy["posting_identifier"])!=parent["ats_id"]:
        raise ValueError("Unexpected ATS identifier")
    ids=structured_identifiers(doc,vacancy["title"])
    if ids and ids!={parent["ats_id"]}:
        raise ValueError("Employer parent structured identifier conflict")
    app_body,app=checked_document(app_url,source,captured)
    if canonical_url(app.url)!=canonical_url(app_url) or not same_title(app,vacancy["title"]):
        raise ValueError("Application redirected or does not identify same current vacancy")
    form_ids=structured_identifiers(app,vacancy["title"])
    if form_ids and form_ids!={parent["ats_id"]}:
        raise ValueError("Application structured identifier differs")
    for post in app.jobposts():
        if fold(plain(post.get("title")))==fold(vacancy["title"]) and expired(post.get("validThrough"),datetime.now(timezone.utc).isoformat()):
            raise ValueError("Application deadline expired")
    for form in ApplicantForms(app_body,strict=True).forms:
        action=form["attrs"].get("action")
        if action and not https_url(urljoin(app.url,action),{urlsplit(parent_url).hostname}):
            raise ValueError("Applicant form action host is unreviewed")
    if not applicant_form(app_body,strict=True):
        raise ValueError("Same-vacancy application form is not visible and enabled")
    return dict(url=canonical_url(app.url),method="public-feed-same-ATS-id-current-employer-CTA-and-enabled-form",
                vacancy_match="title",inventory=vacancy["inventory_evidence"])

def review(candidate, *, approved_host, approved_inventory_url=None,
           client_factory=BudgetClient):
    start=time.monotonic()
    result=dict(provider=candidate.get("provider"),public_id=candidate.get("provider_id"),
                employer=candidate.get("employer"),country=candidate.get("country"),
                city=candidate.get("city"),title=candidate.get("title"),
                status="review-required",policy_version=2,
                catalogue_entry_created=False,production_activated=False,
                verified_vacancies_added=0,requests=0,bytes_read=0,renderings=0)
    client=None
    try:
        if candidate.get("provider")!="jobtech-se" or candidate.get("country")!="SE":
            raise ValueError("Only approved Swedish JobTech evidence supported")
        if candidate.get("verification_state")!="unverified":
            raise ValueError("Official-feed candidate must remain unverified during assessment")
        if not candidate.get("workplace_country_evidence"):
            raise ValueError("Source did not supply explicit Sweden location evidence")
        city=fold(plain(candidate.get("city")))
        if not city or len(city)<3:
            raise ValueError("Source city is unavailable")
        parent=ats_parent(candidate.get("apply_url"),approved_host)
        if parent is None:
            raise ValueError("Observed application URL lacks known same-vacancy ATS ID")
        result.update(source_job_url=candidate["url"],ats_job_url=parent["job_page"],
                      ats_posting_id=parent["ats_id"],application_url=parent["application_url"])
        # The existing strict preflight requires form and independent company
        # ownership evidence before any policy-v2 candidate assessment.
        preliminary=verify_candidate(candidate,{approved_host},client_factory=client_factory)
        result["application_preflight"]=preliminary["state"]
        result["owner_evidence"]=preliminary["employer_identity_evidence"]
        result["requests"]+=preliminary["requests"]
        result["bytes_read"]+=preliminary["bytes_read"]
        if preliminary["state"]!="same-vacancy-form-and-owner-evidence":
            raise ValueError("Applicant form or employer ownership evidence missing")
        client=client_factory(seconds=35,max_requests=5,delay=0.8)
        client.redirect_scope_allowed=lambda url:bool(
            https_url(url,{approved_host}) and urlsplit(url).hostname==approved_host
        )
        captured=CapturedClient(client)
        source=dict(id="preflight-"+str(candidate["provider_id"]),adapter="employer-index",
                    employer=candidate["employer"],allowed_hosts=[approved_host])
        vacancy=dict(url=parent["job_page"],apply_url=parent["application_url"],
                     posting_identifier=parent["ats_id"],external_id=parent["ats_id"],
                     employer=candidate["employer"],title=candidate["title"],
                     inventory_evidence="reviewed-employer-public-job-page")
        try:
            proof=_verify_vacancy(vacancy,source,captured,datetime.now(timezone.utc).isoformat())
        except MissingDynamicForm:
            proof=_published_source_child_fallback(candidate,vacancy,source,captured)
        page=captured.pages.get(canonical_url(parent["job_page"]))
        if not page:
            raise ValueError("Employer vacancy parent page not read")
        document=Document(page,parent["job_page"])
        ensure_open_document(document)
        # City is checked against a specific employer-published location
        # label, not merely because it is repeated in the job title.
        if not re.search(r"\b(?:plats|location|ort)\s*:?\s*"+re.escape(city)+r"\b",
                         fold(document.text)):
            raise ValueError("Official employer job page did not establish source city")
        result["employer_city_match"]=True
        if not classify_role(candidate["title"]):
            raise ValueError("Official posting no longer classifies as HR placement")
        result["internship_role_match"]=True
        result["application_proof_method"]=proof["method"]
        result["job_identity_match"]=(proof["vacancy_match"]=="title")
        result["official_inventory_confirmed"]=False
        if approved_inventory_url:
            sitemap=https_url(approved_inventory_url,{approved_host})
            if not sitemap:
                raise ValueError("Unapproved employer inventory host")
            body,status,final=captured.request(sitemap)
            if final!=sitemap or status!=200:
                raise ValueError("Employer inventory not read at reviewed URL")
            listings=Document(body,final)
            found=any(canonical_url(thing)==canonical_url(parent["job_page"])
                      for href,_,_ in listings.links
                      for thing in (https_url(urljoin(final,href),{approved_host}),)
                      if thing)
            result["official_inventory_confirmed"]=found
            if not found:
                raise ValueError("Employer's current inventory does not link to vacancy")
        else:
            raise ValueError("Employer inventory URL requires separate review")
        result["status"]="policy-v2-evidence-passed-staging-only"
        result["review_note"]="Proof supports an on-host opening; source registry and catalog publish still gated"
    except Exception as exc:
        if result["status"]!="policy-v2-evidence-passed-staging-only":
            result["status"]="access-blocked" if blocked_error(exc) else "review-required"
            result["reason"]=str(exc)[:210]
    finally:
        if client:
            result["requests"]+=client.requests
            result["bytes_read"]+=client.bytes
        result["elapsed_seconds"]=round(time.monotonic()-start,3)
    return result
