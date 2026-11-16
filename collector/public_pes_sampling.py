"""Bounded, privacy-minimal exploratory preflights for public EU vacancy datasets.

Exactly one recent Czech daily *delta prefix* or one Latvian NVA datastore page.
Not a market-completeness claim, not an employer source and not a vacancy
verifier. HTTP GET only; robots, HTTPS and same-host redirect enforcement.
"""
from collections import Counter
from datetime import date, datetime, timedelta, timezone
import json
import re
import time
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, build_opener
from .adapters import AGENT, CheckedRedirect
from .runtime import BudgetClient, host_lock
from .official_feed_discovery import https_url, mpsv_cz_candidate
from .classify import classify_role, fold, plain

MPSV_HOST = "data.mpsv.cz"
MPSV_DAILY_PREFIX = "https://data.mpsv.cz/od/soubory/volna-mista-prirustek/volna-mista-prirustek-"
LV_HOST = "data.gov.lv"
LV_RESOURCE = "7f68f6fc-a0f9-4c31-b43c-770e97a06fda"
LV_SEARCH = "https://data.gov.lv/dati/api/3/action/datastore_search"
MAX_BYTES = 1_000_000
MAX_ROWS = 250
TITLE_HR = re.compile(r"\bhr\b|personal|lidsk.{0,12}zdroj|nabor|rekruta|cilvekresurs|personala|darbiniek|atlases\s+special")
TITLE_INTERNSHIP = re.compile(r"\bstaz|praktik|prakse|praktikants|internship|trainee")


def checked_bounded_get(client, url, max_bytes=MAX_BYTES):
    """A one-request byte cap, even if Range is ignored by the origin."""
    if not isinstance(client, BudgetClient) or not 1024 <= max_bytes <= MAX_BYTES:
        raise ValueError("Invalid bounded source HTTP budget")
    if not https_url(url):
        raise ValueError("Unsafe source URL")
    host = urlsplit(url).hostname
    if host not in {MPSV_HOST, LV_HOST}:
        raise ValueError("Source not approved")
    if not client.permitted(url):
        raise ValueError("robots.txt disallows public dataset GET")
    client.redirect_scope_allowed = lambda target: bool(
        https_url(target, {host}) and urlsplit(target).hostname == host
    )
    with host_lock(host):
        client.check()
        client.pause(max(0,client.host_delays.get(host,client.delay)-
                             (time.monotonic()-client.last.get(host,0))))
        client.check()
        client.requests += 1
        client.last[host] = time.monotonic()
        headers = {
            "User-Agent": AGENT, "Accept": "application/json",
            "Accept-Encoding": "identity",
            "Range": "bytes=0-"+str(max_bytes-1),
        }
        with build_opener(CheckedRedirect(client)).open(
                Request(url, headers=headers, method="GET"),
                timeout=min(15,max(0.1,client.remaining()))) as response:
            final = response.url
            if not https_url(final,{host}) or final != url:
                raise ValueError("Dataset redirected to an unreviewed URL")
            if response.status not in (200,206):
                raise ValueError("Unexpected source response status")
            body = response.read(max_bytes+1)
            truncated = len(body)>max_bytes
            body = body[:max_bytes]
            client.bytes += len(body)
            return body, dict(http_status=response.status,
                              truncated=truncated or response.status==206,
                              bytes_read=len(body))


def _cz_items_from_prefix(data, max_rows):
    """Read complete JSON objects from the start of a larger {polozky:[...]}."""
    text = data.decode("utf-8", "ignore")
    match = re.search(r'"polozky"\s*:\s*\[',text)
    if not match:
        raise ValueError("Official MPSV polozky root missing")
    decoder = json.JSONDecoder()
    i=match.end()
    rows=[]
    complete=False
    while len(rows)<max_rows:
        while i<len(text) and text[i] in " \t\r\n,":
            i+=1
        if i>=len(text):
            break
        if text[i]=="]":
            complete=True
            break
        try:
            item,end=decoder.raw_decode(text,i)
        except json.JSONDecodeError:
            break
        if not isinstance(item,dict):
            raise ValueError("Invalid MPSV vacancy row")
        rows.append(item)
        i=end
    return rows,complete


def sample_czech(client, day, max_bytes=MAX_BYTES, max_rows=MAX_ROWS):
    if not isinstance(day, date) or not date.today()-timedelta(days=10)<=day<=date.today():
        raise ValueError("Czech sample date must be within ten days")
    if not 1<=max_rows<=MAX_ROWS:
        raise ValueError("Czech sample row cap invalid")
    url=MPSV_DAILY_PREFIX+day.isoformat()+".json"
    data, meta=checked_bounded_get(client,url,max_bytes)
    items, fully_parsed=_cz_items_from_prefix(data,max_rows)
    inspected=Counter()
    candidates=[]
    ids=set()
    for record in items:
        position=record.get("pozadovanaProfese")
        title=position.get("cs","") if isinstance(position,dict) else ""
        norm=fold(plain(title))
        if TITLE_HR.search(norm):
            inspected["hr_title_cues"]+=1
        if TITLE_INTERNSHIP.search(norm):
            inspected["internship_title_cues"]+=1
        if TITLE_HR.search(norm) and TITLE_INTERNSHIP.search(norm):
            inspected["combined_title_cues"]+=1
        normalized=mpsv_cz_candidate(record)
        if normalized:
            if normalized["provider_id"] not in ids:
                ids.add(normalized["provider_id"])
                candidates.append(normalized)
    return dict(country="CZ",source="mpsv-daily-delta",source_date=day.isoformat(),
        source_url=url,records_scanned=len(items),input_complete=fully_parsed,
        sampling="first-complete-JSON-objects-in-byte-capped-one-day-delta",
        counts=dict(inspected),strict_distinct_candidates=len(candidates),
        candidates=candidates[:12],candidate_list_truncated=len(candidates)>12,
        caveat="Partial daily changes, not Czech current vacancy inventory; no closure proof",
        **meta)


def sample_latvia(client, max_rows=200):
    if not 1<=max_rows<=MAX_ROWS:
        raise ValueError("Latvian row cap invalid")
    url=LV_SEARCH+"?"+urlencode({"resource_id":LV_RESOURCE,"limit":max_rows})
    data,meta=checked_bounded_get(client,url,MAX_BYTES)
    if meta["truncated"]:
        raise ValueError("Latvian bounded JSON response truncated: no valid sample")
    obj=json.loads(data)
    if obj.get("success") is not True or not isinstance(obj.get("result",{}).get("records"),list):
        raise ValueError("Latvian NVA datastore result unavailable or malformed")
    rows=obj["result"]["records"]
    if len(rows)>max_rows:
        raise ValueError("Unbounded Latvian datastore response")
    counts=Counter()
    for item in rows:
        if not isinstance(item,dict):
            continue
        title=fold(plain(item.get("Vakances_nosaukums")))
        if TITLE_HR.search(title):
            counts["hr_title_cues"]+=1
        if TITLE_INTERNSHIP.search(title):
            counts["internship_title_cues"]+=1
        if TITLE_HR.search(title) and TITLE_INTERNSHIP.search(title):
            counts["combined_title_cues"]+=1
        # No company name or job-specific application URL in this published
        # schema: cannot promote *any* records from this API alone.
        if classify_role(item.get("Vakances_nosaukums",""),
                         item.get("Vakances_paplasinats_apraksts","")):
            counts["project_role_classifier_hits"]+=1
    return dict(country="LV",source="nva-vakances-cc0",
        source_url=url,records_scanned=len(rows),input_complete=len(rows)<max_rows,
        sampling="first-datastore-page-no-pagination",
        counts=dict(counts),strict_distinct_candidates=0,candidates=[],
        caveat="Public-sector-only NVA dataset; employer name and application link unavailable in schema",
        **meta)


def run(provider, *, day=None, max_bytes=MAX_BYTES, max_rows=200, client_factory=BudgetClient):
    client=client_factory(seconds=40,max_requests=5,delay=0.8)
    started=time.monotonic()
    try:
        if provider=="mpsv-cz":
            result=sample_czech(client,day,max_bytes,max_rows)
        elif provider=="nva-lv":
            result=sample_latvia(client,max_rows)
        else:
            raise ValueError("Unknown public open-data source")
        result["state"]="partial-sample" if not result["input_complete"] else "sample-complete"
    except Exception as exc:
        result=dict(state="blocked-or-incomplete",source=provider,
                    error=type(exc).__name__+": "+str(exc)[:180],
                    country="CZ" if provider=="mpsv-cz" else "LV",
                    records_scanned=0,strict_distinct_candidates=0,candidates=[],
                    input_complete=False)
    result.update(requests=client.requests,bytes_read=client.bytes,
                  elapsed_seconds=round(time.monotonic()-started,3),
                  renderings=0,verified_vacancies_added=0,
                  employer_hosts_probed=0,applications_submitted=0,
                  source_registry_changed=False,production_enabled=False)
    return result
