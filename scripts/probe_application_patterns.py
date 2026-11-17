"""Two-source read-only application diagnosis from official employer pages.

Only exact existing catalog URLs on the already-reviewed source host may be
requested. This tool is an opt-in bounded preflight, never a catalog writer or
application submitter. No guessed endpoint, browser, account or CAPTCHA bypass.
"""
import json
import argparse
import re
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urljoin, urlsplit

from collector.pipeline import ROOT, read
from collector.classify import canonical_url, fold, plain
from collector.runtime import BudgetClient
from collector.applications import checked_document
from collector.verification import same_requisition, shares_identifier, same_title, applicant_form, disabled_submit_applicant_form

SELECTED = {
    "employer-danone": "https://careers.danone.com/en-global/jobs/internship-hr-business-partner-intern-28754-en-us.html",
    "employer-tyche-bank": "https://careers.tychebank.it/jobs/8592225-hr-intern",
}
MAX_PER_SOURCE = 5


def diagnose(source, record, factory=BudgetClient):
    approved=source["allowed_hosts"]
    if len(approved)!=1 or approved[0]!=urlsplit(record["url"]).hostname:
        raise ValueError("One exact already-approved host and catalog URL required")
    if record["url"]!=SELECTED[source["id"]]:
        raise ValueError("Only two pre-reviewed catalog records may be inspected")
    client=factory(seconds=35,max_requests=MAX_PER_SOURCE,delay=0.8)
    client.redirect_scope_allowed=lambda url: urlsplit(url).scheme=="https" and \
        urlsplit(url).hostname in approved and not urlsplit(url).username and \
        urlsplit(url).port is None
    output=dict(source_id=source["id"], country=record["country"],
                posting_url=record["url"], parent_page="not-read",
                application_entries_observed=0, possible_same_identity_entries=0,
                form="not-tested", verified_vacancies_added=0,
                applications_submitted=0,renderings=0)
    try:
        body,doc=checked_document(record["url"],source,client)
        output["parent_page"]="same-title" if same_title(doc,record["title"]) else "title-mismatch"
        if output["parent_page"]!="same-title":
            raise ValueError("Employer page title no longer matches catalog lead")
        output["same_page_visible_applicant_form"]=applicant_form(body,strict=True)
        output["same_page_disabled_form"]=disabled_submit_applicant_form(body)
        targets=[]
        for href,label,_ in doc.links:
            if not re.search(r"apply|solliciteer|solliciteren|bewerben|postuler|candidati|candidarsi|candidatar",fold(plain(label))):
                continue
            target=canonical_url(urljoin(doc.url,href))
            parts=urlsplit(target)
            if parts.hostname not in approved or parts.scheme!="https":
                continue
            if target==canonical_url(doc.url):continue
            targets.append(target)
        targets=list(dict.fromkeys(targets))
        output["application_entries_observed"]=len(targets)
        candidates=[url for url in targets
                    if same_requisition(record["url"],url) or shares_identifier(record,url)]
        output["possible_same_identity_entries"]=len(candidates)
        # One exact user-observed CTA may be read. No page transitions to an
        # unreviewed host, and no inferred /applications/new endpoints.
        if len(candidates)==1:
            try:
                abody,app=checked_document(candidates[0],source,client)
                output["form"]=("enabled-vacancy-matched" if
                    (same_title(app,record["title"]) or same_requisition(record["url"],app.url))
                    and applicant_form(abody,strict=True) else
                    "visible-disabled" if disabled_submit_applicant_form(abody) else
                    "not-established")
                output["application_on_same_host"]=True
                output["application_id_match"]=same_requisition(record["url"],app.url) or shares_identifier(record,app.url)
            except Exception as exc:
                output["form"]="application-target-not-readable"
                output["error_type"]=type(exc).__name__
        elif candidates:
            output["form"]="ambiguous-application-entries"
        else:
            output["form"]="no-identified-onhost-application-anchor"
    except Exception as exc:
        output["error_type"]=type(exc).__name__
        output["status"]="incomplete"
    finally:
        output["requests"]=client.requests
        output["bytes_read"]=client.bytes
        output["rate_limited_skips"]=client.rate_limited_skips
    return output


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",required=True,type=Path)
    args=parser.parse_args()
    out=args.output.resolve()
    if out.is_relative_to((ROOT/"data").resolve()) or out.is_relative_to((ROOT/"dist").resolve()):
        parser.error("Read-only diagnostic output cannot modify production/public files")
    sources={s["id"]:s for s in read(ROOT/"data/sources.json",[])}
    catalog=read(ROOT/"data/catalog.json",{})["jobs"]
    rows=[]
    for sid,url in SELECTED.items():
        matches=[j for j in catalog if j["url"]==url and j["source_id"]==sid]
        if len(matches)!=1 or sid not in sources or not sources[sid].get("enabled"):
            raise ValueError("Required exact active official source / catalog lead is missing")
        rows.append(diagnose(sources[sid],matches[0]))
    report=dict(mode="single-bounded-read-only-official-application-diagnostic",
                checked_at=datetime.now(timezone.utc).isoformat(),
                requests=sum(r["requests"] for r in rows),
                bytes_read=sum(r["bytes_read"] for r in rows),
                source_count=len(rows),source_results=rows,
                new_verified_vacancies=0,production_files_modified=False,
                conclusion="Diagnosis only; no policy-v2 applicant form claimed without complete same-vacancy proof")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
    print("APPLICATION_GAP_DIAGNOSTIC "+json.dumps(report,ensure_ascii=False,sort_keys=True))
    return report


if __name__=="__main__": main()
