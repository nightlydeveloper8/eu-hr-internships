"""One-time EU27 batch08 GET-only preflight; never run on daily schedule.

Uses the existing BudgetClient, robots, and exact reviewed host scopes.
No POST, credentials, browser, CAPTCHA or applicant data. The workflow that
invokes it must be removed from the pilot branch after the run.
"""
import hashlib
import json
import time
from urllib.parse import urlsplit
from collector.runtime import BudgetClient
from collector.universal import Document
from collector.verification import applicant_form
from collector.applications import ensure_open_document, ApplicantForms, ApplicationClosed

# A path below is deliberately not an endpoint candidate invented from the
# page: all except the provider-documented Personio XML were seen on official
# employer/ATS pages or the employer's published application link.
SOURCES = [
    dict(country="AT", employer="Peek & Cloppenburg Austria",
         key="praktikum-hr-retail-at-cee",
         hosts=["karriere.peek-cloppenburg.at", "puc.csod.com"],
         pages=[
             ["corporate_careers", "https://karriere.peek-cloppenburg.at/"],
             ["official_ats_inventory", "https://puc.csod.com/ux/ats/careersite/1/home?c=puc&country=at&lang=de-at&sq="],
         ]),
    dict(country="DE", employer="Audi Business Innovation GmbH",
         key="2540621",
         hosts=["www.audibusinessinnovation.de", "audi-business-innovation-gmbh.jobs.personio.de"],
         pages=[
             ["corporate_careers", "https://www.audibusinessinnovation.de/career/"],
             ["inventory", "https://audi-business-innovation-gmbh.jobs.personio.de/"],
             ["provider_xml", "https://audi-business-innovation-gmbh.jobs.personio.de/xml"],
             ["vacancy", "https://audi-business-innovation-gmbh.jobs.personio.de/job/2540621?language=de"],
             ["application", "https://audi-business-innovation-gmbh.jobs.personio.de/job/2540621/apply?language=de"],
         ]),
    dict(country="DE", employer="Studyflix GmbH",
         key="1119149", hosts=["studyflix-gmbh.jobs.personio.de"],
         pages=[
             ["inventory", "https://studyflix-gmbh.jobs.personio.de/"],
             ["vacancy", "https://studyflix-gmbh.jobs.personio.de/job/1119149"],
             ["application", "https://studyflix-gmbh.jobs.personio.de/job/1119149/apply"],
         ]),
    dict(country="DK", employer="A.P. Moller - Maersk",
         key="R199126", hosts=["maersk.wd3.myworkdayjobs.com"],
         pages=[
             ["inventory", "https://maersk.wd3.myworkdayjobs.com/en-US/Maersk_Careers"],
             ["vacancy", "https://maersk.wd3.myworkdayjobs.com/en-US/Maersk_Careers/job/Talent-Acquisition-Intern---Early-Careers-_R199126"],
         ]),
    dict(country="FI", employer="StaffPoint Oy",
         key="3Bkmpb", hosts=["www.staffpoint.fi", "staffpoint.talentadore.com"],
         pages=[
             ["inventory", "https://www.staffpoint.fi/tyopaikat?field=4&field=5"],
             ["vacancy", "https://www.staffpoint.fi/tyopaikat/hr-harjoittelija-horeca-tiimiin-staffpointille-3Bkmpb"],
             ["application", "https://staffpoint.talentadore.com/apply/hr-harjoittelija-horeca-tiimiin-staffpointille/3Bkmpb?display=form_only"],
         ]),
    dict(country="PL", employer="Michael Page Poland",
         key="JN-112026-7142697", hosts=["www.michaelpage.pl"],
         pages=[
             ["vacancy", "https://www.michaelpage.pl/job-detail/sta%C5%BCysta-hr/ref/jn-112026-7142697?lang=pl&ng-jn=job-detail&ng-src=other-users-applied"],
         ]),
    dict(country="SE", employer="SnabbPass AB",
         key="talent-acquisition-digital-growth-internship-ai-recruitment",
         hosts=["www.snabbpass.com"],
         pages=[
             ["inventory", "https://www.snabbpass.com/en/career"],
             ["vacancy", "https://www.snabbpass.com/en/career/talent-acquisition-digital-growth-internship-ai-recruitment"],
         ])
]

def probe():
    output = {"schema_version": 1, "mode": "batch08-one-time-GET-only",
              "date": "2026-11-16", "limits": {"requests_each": 12, "source_seconds_each": 45,
              "renderings": 0}, "rows": []}
    for source in SOURCES:
        start = time.monotonic()
        client = BudgetClient(seconds=45, max_requests=12, delay=0.5)
        allowed = set(source["hosts"])
        client.redirect_scope_allowed = lambda target, allowed=allowed: (
            urlsplit(target).scheme == "https" and
            urlsplit(target).hostname in allowed
        )
        row = dict(country=source["country"], employer=source["employer"],
                   expected_identifier=source["key"], reviewed_hosts=source["hosts"],
                   policy_v2_verified=False, new_source_enabled=False, pages=[])
        for kind,url in source["pages"]:
            item = {"kind":kind,"requested_url":url}
            try:
                body,status,final=client.request(url,robots=True,timeout=9,attempts=1,
                   accept="application/xml,text/xml;q=0.9,*/*;q=0.8" if kind=="provider_xml" else None)
                if urlsplit(final).hostname not in allowed:
                    raise ValueError("Unexpected final host")
                doc=Document(body,final) if kind!="provider_xml" else None
                item.update(status=status,final_url=final,bytes=len(body),
                            sha256=hashlib.sha256(body).hexdigest(),
                            expected_identifier_in_final_url=source["key"].lower() in final.lower(),
                            expected_identifier_in_html=source["key"].lower().encode() in body.lower(),
                            robots_guard_passed=True)
                if doc:
                    item["headings"]=doc.h1[:3]
                    item["job_postings"]=len(doc.jobposts())
                    try:
                        ensure_open_document(doc)
                        item["explicit_closed"]=False
                    except ApplicationClosed:
                        item["explicit_closed"]=True
                    item["applicant_form_detected"]=bool(applicant_form(body,strict=True))
                    forms=ApplicantForms(body,strict=True).forms
                    item["html_forms_total"]=len(forms)
                    item["candidate_forms_with_email"]=sum(
                        any("email" in str(field.get(k) or "").lower()
                            for field in form["fields"] for k in ("type","name","id"))
                        for form in forms)
                    item["candidate_forms_with_enabled_submit"]=sum(
                        bool(form["submit"]) for form in forms)
                    item["apply_cta_links"]=[
                        {"href":href[:220],"label":label.strip()[:60]} for href,label,_ in doc.links
                        if any(token in label.lower() for token in ("apply","bewerb","ansøg","hae työpaikkaa","sök","aplikuj"))
                    ][:4]
                else:
                    item["xml_job_count_marker"]=body.count(b"<job>")
                # Pass of robots guard is scoped to this URL, not blanket host approval.
            except Exception as exc:
                item.update(error_type=type(exc).__name__,error=str(exc)[:200],
                            robots_guard_passed=False)
            row["pages"].append(item)
            if client.remaining()<3 or client.requests>=12:break
        row.update(requests=client.requests,bytes_read=client.bytes,
                   source_seconds=round(time.monotonic()-start,3),
                   host_rate_limited_skips=client.rate_limited_skips)
        output["rows"].append(row)
    output["totals"] = dict(
        sources=len(output["rows"]),countries=len(set(x["country"] for x in output["rows"])),
        requests=sum(x["requests"] for x in output["rows"]),
        body_bytes=sum(x["bytes_read"] for x in output["rows"]),
        source_seconds=round(sum(x["source_seconds"] for x in output["rows"]),3),
        forms_visible=sum(bool(p.get("applicant_form_detected"))
                          for x in output["rows"] for p in x["pages"]),
        sources_enabled=0,policy_v2_verified=0,renderings=0)
    print("BATCH08_GET_PILOT_BEGIN")
    print(json.dumps(output,ensure_ascii=False))
    print("BATCH08_GET_PILOT_END")

if __name__=="__main__":
    probe()
