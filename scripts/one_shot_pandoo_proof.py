"""One-shot offline-no-applicant proof of official PANDOO email entry.

GET two officially observed public pages with robots. The exact HTML is
checked by the existing policy v2 verifier; no mail, login, browser, POST or
candidate data. Country workplace mapping is explicitly NOT established.
"""
import hashlib,json,re,time
from urllib.parse import urljoin,urlsplit
from collector.runtime import BudgetClient
from collector.universal import Document
from collector.verification import verify_vacancy
from collector.classify import canonical_url
URL="https://pandoo.lu/hr-intern-f/m/d"
INDEX="https://pandoo.lu/jobs"
STAMP="2026-11-16T18:30:00+00:00"
SOURCE={"id":"eu-pandoo-lu-probe","employer":"PANDOO Administration",
 "adapter":"employer-index","application_check":"official-email",
 "application_email":"hr@pandoo.lu","allowed_hosts":["pandoo.lu"]}
RECORD={"source_id":"eu-pandoo-lu-probe","external_id":"pandoo-hr-2026",
 "employer":"PANDOO Administration","title":"HR Intern (F/M/D)",
 "text":"HR internship","url":URL,"apply_url":URL,
 "inventory_evidence":"reviewed-current-employer-careers-page"}

def run():
 started=time.monotonic()
 client=BudgetClient(seconds=30,max_requests=6,delay=.5)
 client.redirect_scope_allowed=lambda url: urlsplit(url).scheme=="https" and urlsplit(url).hostname=="pandoo.lu"
 out={"mode":"one-time-readonly-review","date":"2026-11-16","verified_catalog_jobs":0,
 "new_enabled_sources":0,"email_sent":False,"delivery_verified":False}
 try:
  ib,istat,ifinal=client.request(INDEX,robots=True,timeout=10,attempts=1)
  body,status,final=client.request(URL,robots=True,timeout=10,attempts=1)
  idx=Document(ib,ifinal);doc=Document(body,final)
  exact=[urljoin(ifinal,href) for href,label,_ in idx.links if canonical_url(urljoin(ifinal,href))==canonical_url(URL)]
  out["inventory"]={"http":istat,"final_url":ifinal,"body_sha256":hashlib.sha256(ib).hexdigest(),
    "bytes":len(ib),"exact_role_link_count":len(exact),"text_mentions_hr_intern":"HR Intern" in idx.text}
  out["vacancy"]={"http":status,"final_url":final,"body_sha256":hashlib.sha256(body).hexdigest(),
    "bytes":len(body),"h1":doc.h1,"observed_mailto_labels":[label for href,label,_ in doc.links
      if href.lower().split("?")[0]=="mailto:hr@pandoo.lu"],
    "explicit_apply_instruction":bool(re.search(r"please send us your application",doc.text,re.I))}
  class Snapshot:
   requests=0
   def request(self,url,**kwargs):
    self.requests+=1
    if canonical_url(url)!=canonical_url(final):raise ValueError("outside snapshot")
    return body,200,final
  snapshot=Snapshot()
  if len(exact)!=1:raise ValueError("Employer inventory missing single exact job link")
  proof=verify_vacancy(RECORD,SOURCE,snapshot,STAMP)
  out["direct_application_proof"]={"method":proof.get("method"),
     "application_email":proof.get("application_email"),
     "delivery_verified":proof.get("delivery_verified"),
     "reused_snapshot_requests":snapshot.requests}
  out["application_channel_matched"]=(
     proof.get("method")=="official-vacancy-email-instructions"
     and proof.get("delivery_verified") is False)
  out["workplace_confirmed_from_job_page"]=False
  out["reason_not_catalog_verified"]="Company office location appears in page footer, but the specific internship workplace is not explicitly established by the vacancy; no source registered."
 except Exception as exc:
  out["error_type"]=type(exc).__name__;out["error"]=str(exc)[:300]
  out["application_channel_matched"]=False
 out["requests"]=client.requests
 out["bytes_read"]=client.bytes
 out["source_seconds"]=round(time.monotonic()-started,3)
 out["renderings"]=0
 print("PANDOO_ONE_SHOT_BEGIN")
 print(json.dumps(out,ensure_ascii=False))
 print("PANDOO_ONE_SHOT_END")

if __name__=="__main__":run()
