"""One-time read-only EU27 batch07 preflight. Do not schedule or enable sources.

Exact observed corporate/ATS URLs only. Respect robots and host scopes.
Never send applicant details, POST, browser automation, or credentials.
"""
import hashlib
import json
import time
from urllib.error import HTTPError
from urllib.parse import urlsplit

from collector.runtime import BudgetClient
from collector.universal import Document
from collector.verification import applicant_form
from collector.applications import ensure_open_document, ApplicationClosed

SOURCES = [
    {
        "country": "CY", "employer": "Brainstorm Hospitality", "job_id": "7649525",
        "title": "HR Intern", "hosts": {"careers.fridays.com.cy"},
        "pages": [
            ("inventory", "https://careers.fridays.com.cy/"),
            ("vacancy", "https://careers.fridays.com.cy/jobs/7649525-hr-intern"),
        ],
    },
    {
        "country": "GR", "employer": "iKnowHow S.A.", "job_id": "3F368EAC02",
        "title": "HR Intern (Talent Acquisition)", "hosts": {"apply.workable.com"},
        "pages": [
            ("inventory", "https://apply.workable.com/ikh/"),
            ("vacancy", "https://apply.workable.com/ikh/j/3F368EAC02"),
        ],
    },
    {
        "country": "MT", "employer": "Marriott / Westin Dragonara", "job_id": "26132701",
        "title": "Human Resources Intern (The Westin Dragonara Resort)",
        "hosts": {"careers.marriott.com", "ejwl.fa.us2.oraclecloud.com"},
        "pages": [
            ("inventory", "https://careers.marriott.com/brands/westin/jobs/page/52"),
            ("vacancy", "https://careers.marriott.com/human-resources-intern-the-westin-dragonara-resort/job/P1-7345932-0"),
            ("application", "https://ejwl.fa.us2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX/job/26132701/apply/email?posting_type=1"),
        ],
    },
]

def run():
    output = {"schema_version": 1, "mode": "one-time-bounded-readonly-preflight",
              "policy_version": 2, "requests_max_per_source": 12,
              "seconds_max_per_source": 45, "renderings": 0, "rows": []}
    for source in SOURCES:
        started = time.monotonic()
        client = BudgetClient(seconds=45, max_requests=12, delay=0.5)
        # Never allow an arbitrary redirect to expand the scope.
        client.redirect_scope_allowed = (
            lambda destination, allowed=source["hosts"]:
                urlsplit(destination).scheme == "https"
                and urlsplit(destination).hostname in allowed
        )
        row = {"country": source["country"], "employer": source["employer"],
               "job_id": source["job_id"], "pages": [],
               "verified": False, "enabled": False,
               "notes": "Page/forms alone are not policy-v2 proof; no sources activated"}
        for page_type, url in source["pages"]:
            page = {"kind": page_type, "url": url}
            try:
                body, status, final = client.request(url, robots=True, timeout=9, attempts=1)
                if urlsplit(final).hostname not in source["hosts"]:
                    raise ValueError("Redirect host outside reviewed scope")
                doc = Document(body, final)
                try:
                    ensure_open_document(doc)
                    page["page_closure"] = "none-detected"
                except ApplicationClosed:
                    page["page_closure"] = "explicitly-closed"
                page.update(http_status=status, final_url=final,
                            bytes=len(body), sha256=hashlib.sha256(body).hexdigest(),
                            headings=doc.h1[:3],
                            title_in_text=source["title"].lower() in doc.text.lower(),
                            job_id_in_url=source["job_id"] in final,
                            applicant_form_visible_enabled=bool(applicant_form(body, strict=True)),
                            observed_link_labels=[
                                label[:80] for _, label, _ in doc.links
                                if "apply" in label.lower()][:4])
                # All successful requests passed the built-in robots guard.
                page["robots_guard_passed"] = True
            except Exception as exc:
                page["error_type"] = type(exc).__name__
                page["error"] = str(exc)[:180]
                page["robots_guard_passed"] = False
            row["pages"].append(page)
            if client.remaining() < 2 or client.requests >= 12:
                break
        row.update(requests=client.requests, bytes_read=client.bytes,
                   seconds=round(time.monotonic()-started, 3),
                   rate_limited_skips=client.rate_limited_skips)
        output["rows"].append(row)
    output["totals"] = {
        "requests": sum(r["requests"] for r in output["rows"]),
        "bytes_read": sum(r["bytes_read"] for r in output["rows"]),
        "source_seconds": round(sum(r["seconds"] for r in output["rows"]),3),
        "verified": 0, "enabled": 0,
    }
    print("BATCH07_PREFLIGHT_JSON_START")
    print(json.dumps(output, ensure_ascii=False))
    print("BATCH07_PREFLIGHT_JSON_END")

if __name__ == "__main__":
    run()
