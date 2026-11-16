"""A one-time structural-only diagnostic of known Personio/Talentadore forms.

Only inspected HTML tags, form relationships and provider XML tag names.
No applicant data, script evaluation, browser, POST, authentication, or bypass.
"""
from html.parser import HTMLParser
from urllib.parse import urlsplit
from xml.etree import ElementTree
import json,time,hashlib
from collector.runtime import BudgetClient

TARGETS=[
 ("DE","Audi Business Innovation","https://audi-business-innovation-gmbh.jobs.personio.de/job/2540621/apply?language=de"),
 ("DE","Studyflix GmbH","https://studyflix-gmbh.jobs.personio.de/job/1119149/apply"),
 ("FI","StaffPoint Oy","https://staffpoint.talentadore.com/apply/hr-harjoittelija-horeca-tiimiin-staffpointille/3Bkmpb?display=form_only")
]
FEEDS=[
 ("DE","Audi Business Innovation","https://audi-business-innovation-gmbh.jobs.personio.de/xml"),
 ("DE","Studyflix GmbH","https://studyflix-gmbh.jobs.personio.de/xml")
]
VOID={"input","meta","link","img","br","hr","source","area","base","embed","param","wbr"}

class Shape(HTMLParser):
 def __init__(self):
  super().__init__();self.forms=[];self.current=None;self.buttons=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=="form":
   item={"id":a.get("id"),"method":a.get("method"),
         "action_path":urlsplit(a.get("action") or "").path[:100],
         "name":a.get("name"),"nfields":0,"fields":[],
         "inside_submit":0,"outside_associated_submit":0,
         "formclass":(a.get("class") or "")[:100]}
   self.forms.append(item);self.current=item
  if tag in ("input","select","textarea"):
   if self.current is not None:
    self.current["nfields"]+=1
    if len(self.current["fields"])<22:self.current["fields"].append({"type":a.get("type"),
      "name":(a.get("name") or "")[:90], "id":(a.get("id") or "")[:90],
      "disabled":("disabled" in a),"hidden":(a.get("type")=="hidden")})
  if tag=="button" or (tag=="input" and a.get("type","").lower()=="submit"):
   btn={"tag":tag,"type":a.get("type","submit"),"form":a.get("form"),
        "id":a.get("id"),"name":a.get("name"),"disabled":"disabled" in a,
        "class":(a.get("class") or "")[:90], "inside_form":self.current is not None}
   self.buttons.append(btn)
   if self.current is not None and btn["type"]=="submit":self.current["inside_submit"]+=1
 def handle_endtag(self,tag):
  if tag=="form":self.current=None

def run():
 out={"schema_version":1,"mode":"one-time-structure-only","form_pages":[],"feeds":[]}
 for country,employer,url in TARGETS:
  start=time.monotonic();client=BudgetClient(seconds=25,max_requests=4,delay=0.5)
  host=urlsplit(url).hostname
  client.redirect_scope_allowed=lambda dest,host=host: urlsplit(dest).scheme=="https" and urlsplit(dest).hostname==host
  record={"country":country,"employer":employer,"url":url}
  try:
   body,status,final=client.request(url,robots=True,timeout=10,attempts=1)
   shape=Shape();shape.feed(body.decode("utf-8","replace"))
   for form in shape.forms:
    form["outside_associated_submit"]=sum(int(not b["inside_form"] and b.get("form")==form["id"] and b["type"]=="submit" and not b["disabled"]) for b in shape.buttons) if form.get("id") else 0
   record.update(http=status,sha256=hashlib.sha256(body).hexdigest(),
    bytes_read=len(body),forms=shape.forms,buttons=shape.buttons[:20],total_buttons=len(shape.buttons),
    any_form_submit=any(bool(f["inside_submit"] or f["outside_associated_submit"]) for f in shape.forms))
  except Exception as exc:record.update(error_type=type(exc).__name__,error=str(exc)[:180])
  record.update(requests=client.requests,seconds=round(time.monotonic()-start,3))
  out["form_pages"].append(record)
 for country,employer,url in FEEDS:
  start=time.monotonic();client=BudgetClient(seconds=25,max_requests=4,delay=0.5)
  host=urlsplit(url).hostname
  client.redirect_scope_allowed=lambda dest,host=host: urlsplit(dest).scheme=="https" and urlsplit(dest).hostname==host
  row={"country":country,"employer":employer,"url":url}
  try:
   body,status,final=client.request(url,robots=True,timeout=10,attempts=1,accept="application/xml,text/xml;q=0.9,*/*;q=0.8")
   root=ElementTree.fromstring(body)
   tags={}
   for elem in root.iter():
    key=elem.tag.split("}")[-1];tags[key]=tags.get(key,0)+1
   row.update(http=status,bytes_read=len(body),sha256=hashlib.sha256(body).hexdigest(),root=root.tag,
      tag_counts={key:tags[key] for key in ("job","position","id","name","title","description","jobDetails","job_type") if key in tags},
      top_tags=list(tags.keys())[:20])
  except Exception as exc:row.update(error_type=type(exc).__name__,error=str(exc)[:180])
  row.update(requests=client.requests,seconds=round(time.monotonic()-start,3))
  out["feeds"].append(row)
 out["totals"]={"requests":sum(x["requests"] for x in out["form_pages"]+out["feeds"]),
 "bytes_read":sum(x.get("bytes_read",0) for x in out["form_pages"]+out["feeds"]),
 "source_seconds":round(sum(x["seconds"] for x in out["form_pages"]+out["feeds"]),3)}
 print("BATCH08_FORM_DIAGNOSTIC_BEGIN")
 print(json.dumps(out,ensure_ascii=False))
 print("BATCH08_FORM_DIAGNOSTIC_END")

if __name__=="__main__":run()
