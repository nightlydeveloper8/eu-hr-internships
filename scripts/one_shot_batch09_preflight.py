"""EU27 batch09 one-shot official GET-only study, no scheduled sources.

Runs on isolated branch only; no credentials, browser, POST, applicants or
unreviewed hosts. Uses BudgetClient robots and exact host redirect scope.
"""
import hashlib
import json
import re
import time
from urllib.parse import urlsplit
from collector.runtime import BudgetClient
from collector.universal import Document
from collector.applications import ApplicantForms, ensure_open_document, ApplicationClosed
from collector.verification import applicant_form

SOURCES = [
 dict(country="CZ", employer="SAP", id="REF3475V",
      hosts=["jobs.sap.com"],
      urls=[
       ("inventory", "https://jobs.sap.com/en/jobs/?location=Prague"),
       ("vacancy","https://jobs.sap.com/en/jobs/744000161307409/sap-ixp-intern-recruiting-associate-tech-td-limited-full-time/"),
      ]),
 dict(country="CZ", employer="Amazon", id="10561439", hosts=["www.amazon.jobs"],
      urls=[
       ("inventory","https://www.amazon.jobs/en/search?base_query=human+resources+intern"),
       ("vacancy","https://www.amazon.jobs/en/jobs/10561439/operations-human-resources-partner-intern-6-months-2027"),
      ]),
 dict(country="RO", employer="BAT", id="81347", hosts=["careers.bat.com"],
      urls=[
       ("inventory","https://careers.bat.com/en/search_jobs/bucharest/1045/1/1"),
       ("vacancy","https://careers.bat.com/en/job/bucharest/hr-intern/1045/46198641856"),
       ("apply","https://careers.bat.com/en/apply?locale=en_GB&req=81347"),
      ]),
 dict(country="RO", employer="Marquardt", id="sUQZQQ",
      hosts=["www.marquardt.com", "marquardt-ro.mingle.ro"],
      urls=[
       ("vacancy","https://www.marquardt.com/careers/job-search/detail/hr-internship-french-english-speakers-f-m"),
       ("apply","https://marquardt-ro.mingle.ro/en/apply/sUQZQQ"),
      ]),
 dict(country="IE", employer="TikTok", id="7694622895491205429",
      hosts=["lifeattiktok.com", "careers.tiktok.com"],
      urls=[
       ("vacancy","https://lifeattiktok.com/search/7694622895491205429"),
       ("apply","https://careers.tiktok.com/resume/7694622895491205429/apply"),
      ]),
 dict(country="LU", employer="PANDOO", id="hr-intern-f/m/d", hosts=["pandoo.lu"],
      urls=[
       ("inventory","https://pandoo.lu/jobs"),
       ("vacancy","https://pandoo.lu/hr-intern-f/m/d"),
      ]),
 dict(country="LU", employer="EY", id="1749932", hosts=["careers.ey.com"],
      urls=[
       ("vacancy","https://careers.ey.com/ey/job/Luxembourg-HR-Mobility-Intern-L-1855/1444849033/"),
      ]),
 dict(country="LU", employer="Deloitte Luxembourg", id="13618", hosts=["jobs.deloitte.lu"],
      urls=[
       ("vacancy","https://jobs.deloitte.lu/job/Learning-%26-Development-Intern/13618-en_GB"),
      ])
]

def measure():
    result={"schema_version":1,"date":"2026-11-16","mode":"one-shot-robots-guarded-readonly",
            "max_requests_each":10,"max_source_seconds_each":35,"renderings":0,
            "policy_v2_verified":0,"sources_enabled":0,"rows":[]}
    for target in SOURCES:
        t0=time.monotonic()
        client=BudgetClient(seconds=35,max_requests=10,delay=.5)
        allowed=set(target["hosts"])
        client.redirect_scope_allowed=lambda url,allowed=allowed: (
             urlsplit(url).scheme=="https" and urlsplit(url).hostname in allowed)
        row={"country":target["country"],"employer":target["employer"],"expected_id":target["id"],
             "hosts":target["hosts"],"pages":[],"verified":False,"enabled":False}
        for kind,url in target["urls"]:
            page={"kind":kind,"requested_url":url}
            try:
                body,status,final=client.request(url,robots=True,timeout=9,attempts=1)
                if urlsplit(final).hostname not in allowed:
                    raise ValueError("out-of-review host")
                doc=Document(body,final)
                try: ensure_open_document(doc); closed=False
                except ApplicationClosed: closed=True
                forms=ApplicantForms(body,strict=True).forms
                mailtos=[{"href":href,"label":label.strip()[:70]} for href,label,_ in doc.links if href.startswith("mailto:")]
                applies=[{"href":href[:240],"label":label.strip()[:60]} for href,label,_ in doc.links
                         if re.search(r"apply|aplic|bewerb|job",label,re.I)]
                page.update(status=status,final=final,bytes=len(body),
                            sha256=hashlib.sha256(body).hexdigest(),h1=doc.h1[:4],
                            title_present=bool(re.search(r"hr|human resources|recruiting|mobility|talent",doc.text,re.I)),
                            expected_id_in_url=target["id"].lower() in final.lower(),
                            expected_id_in_body=target["id"].lower().encode() in body.lower(),
                            form_count=len(forms),applicant_form_visible_enabled=applicant_form(body,strict=True),
                            forms_with_submit=sum(bool(f["submit"]) for f in forms),
                            mailto_links=mailtos[:5],apply_links=applies[:6],
                            closed_text_detected=closed,robots_guard_passed=True)
            except Exception as exc:
                page.update(error_type=type(exc).__name__,error=str(exc)[:180],robots_guard_passed=False)
            row["pages"].append(page)
            if client.requests>=10 or client.remaining()<3:break
        row.update(requests=client.requests,bytes_read=client.bytes,
                   source_seconds=round(time.monotonic()-t0,3),
                   rate_limited_skips=client.rate_limited_skips)
        result["rows"].append(row)
    result["totals"]={
        "sources":len(result["rows"]), "countries":len(set(r["country"] for r in result["rows"])),
        "requests":sum(r["requests"] for r in result["rows"]),
        "bytes_read":sum(r["bytes_read"] for r in result["rows"]),
        "source_seconds":round(sum(r["source_seconds"] for r in result["rows"]),3),
        "verified":0,"enabled":0,"renderings":0}
    print("BATCH09_ONE_SHOT_BEGIN")
    print(json.dumps(result,ensure_ascii=False))
    print("BATCH09_ONE_SHOT_END")

if __name__=="__main__":
    measure()
