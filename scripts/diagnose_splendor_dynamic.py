"""One opt-in, non-submitting, read-only dynamic ATS diagnostic for a JobTech lead.

Uses the existing strict browser layer: only GET/HEAD on the exact allowed
host, no auth, CAPTCHA bypass, analytics, form clicks or POST. If any resource
or navigation is denied, availability remains UNKNOWN, never 'closed'.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

from collector.classify import fold, plain
from collector.official_feed_discovery import https_url
from collector.official_feed_verification import academic_term_title_variant
from collector.runtime import BudgetClient
from collector.universal import Document
from collector.verification import applicant_form, same_title

ROOT=Path(__file__).resolve().parents[1]


def inspect(candidate,*,approved_host,client_factory=BudgetClient,render=None):
    result=dict(provider=candidate.get("provider"),provider_id=candidate.get("provider_id"),
                state="review-required",verified_vacancies_added=0,
                production_activated=False,applications_submitted=0,
                browser_attempted=False,renderings=0,requests=0,bytes_read=0)
    url=https_url(candidate.get("apply_url"),{approved_host})
    if (candidate.get("provider")!="jobtech-se" or
        candidate.get("verification_state")!="unverified" or
        candidate.get("country")!="SE" or not url):
        result["reason"]="Source metadata or exact pre-approved ATS host invalid"
        return result
    client=client_factory(seconds=55,max_requests=17,delay=0.8)
    client.redirect_scope_allowed=lambda target:bool(
        https_url(target,{approved_host}) and urlsplit(target).hostname==approved_host)
    measures={}
    try:
        if render is None:
            from collector.rendering import render_pages
            render=render_pages
        result["browser_attempted"]=True
        snapshots,_=render(url,client,lambda target:bool(
            https_url(target,{approved_host}) and
            urlsplit(target).hostname==approved_host),
            limit=1,application_read=True,application_toggle=False,metrics=measures)
        if not snapshots:
            raise ValueError("No complete rendered applicant document")
        final,body=snapshots[-1]
        if https_url(final,{approved_host})!=url:
            raise ValueError("Rendered vacancy URL differs from approved target")
        doc=Document(body,final)
        exact=same_title(doc,candidate["title"])
        drift=any(academic_term_title_variant(candidate["title"],t) for t in doc.h1)
        form=applicant_form(body,strict=True)
        result.update(observed_heading=doc.h1[:2],exact_title=exact,
                      academic_term_variant=drift,enabled_applicant_form=form,
                      applicant_cta_visible=bool(re.search(r"\b(?:ansok|ansokan|skicka\s+ansokan)\b",
                                                        fold(doc.text))))
        if not exact and not drift:
            result["state"]="rendered-but-identity-unmatched"
        elif form:
            result["state"]="rendered-enabled-form-preflight-only"
        elif result["applicant_cta_visible"]:
            result["state"]="rendered-CTA-only-form-not-established"
        else:
            result["state"]="rendered-no-applicant-form-evidence"
    except Exception as exc:
        result["state"]="incomplete-access-or-render"
        result["reason"]=type(exc).__name__+": "+str(exc)[:220]
    finally:
        result.update(requests=client.requests,bytes_read=client.bytes,
                      renderings=1 if result["browser_attempted"] else 0,
                      browser_requests=measures.get("browser_requests",0),
                      blocked_requests=measures.get("blocked_requests",0),
                      suppressed_resources=measures.get("suppressed_resources",0),
                      browser_bytes=measures.get("browser_bytes",0))
    return result


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source-report",type=Path,required=True)
    p.add_argument("--provider-id",required=True)
    p.add_argument("--approved-host",required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args(argv)
    if a.output.resolve().is_relative_to((ROOT/"data").resolve()) or a.output.resolve()==a.source_report.resolve():
        p.error("Cannot write into production data or overwrite input")
    source=json.loads(a.source_report.read_text())
    if source.get("mode")!="discovery-only" or source.get("provider")!="jobtech-se":
        p.error("Expected public JobTech discovery report")
    leads=[x for x in source["candidates"] if x["provider_id"]==a.provider_id]
    if len(leads)!=1:
        p.error("Expected exact public posting ID")
    result=inspect(leads[0],approved_host=a.approved_host)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
    print("DYNAMIC_FORM_DIAGNOSTIC "+json.dumps(result,ensure_ascii=False,sort_keys=True))
    return result


if __name__=="__main__":
    main()
