"""Enumerate ATS board identities from Common Crawl CDX, entirely in staging."""
from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
import random
import re
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from collector.ats_channel_discovery import TOKEN, _registered_keys, identify_channel, safe_url

INDEX = "https://index.commoncrawl.org"
USER_AGENT = "PeoplePlacement-ATS-Research/1.0"
HOST_RULES = {
    "teamtailor": ("teamtailor.com",),
    "inrecruiting": ("intervieweb.it",),
    "softgarden": ("softgarden.io", "softgarden.de"),
    "factorial": ("factorialhr.com", "factorial.com"),
    "altamira": ("altamiraweb.com",),
    "bizneo": ("bizneo.com",),
    "talentclue": ("talentclue.com",),
}
PATH_RULES = {
    "apply.workable.com": "workable",
    "www.welcometothejungle.com": "welcome-to-the-jungle",
    "app.welcometothejungle.com": "welcome-to-the-jungle",
}
QUERIES = {
    "recruitee": ("recruitee.com",),
    "personio-xml": ("jobs.personio.de", "jobs.personio.com"),
    "lever": ("jobs.lever.co", "jobs.eu.lever.co"),
    "greenhouse": ("boards.greenhouse.io", "job-boards.greenhouse.io", "boards.eu.greenhouse.io"),
    "talentech": ("candidate.hr-manager.net",),
    **HOST_RULES,
}
for host, provider in PATH_RULES.items():
    QUERIES[provider] = (*QUERIES.get(provider, ()), host)

RESERVED = set("www app api help support blog careers jobs admin login embed static cdn assets"
               " demo test status apply search signin auth docs resources privacy legal welcome j".split())


def identity(raw):
    url = safe_url(raw)
    if url is None:
        return None
    host = url.hostname
    parts = url.path.strip("/").split("/")
    existing = identify_channel(raw)
    if existing and existing["adapter"] in {"recruitee", "personio-xml", "greenhouse", "lever"}:
        provider = existing["adapter"]
        tenant = existing["tenant"]
        if tenant.split(".")[0] in RESERVED:
            return None
        # Regional boards may be independently administered.
        if host in {"boards.eu.greenhouse.io", "jobs.eu.lever.co"}:
            tenant = "eu/" + tenant
        return provider, tenant
    if host == "candidate.hr-manager.net" and url.path.lower() == "/applicationinit.aspx":
        params = parse_qs(url.query, max_num_fields=30) if url.query.count("&") < 30 else {}
        cid = params.get("cid", [])
        if len(cid) == 1 and re.fullmatch(r"[0-9]{1,12}", cid[0]):
            return "talentech", str(int(cid[0]))
    if host in PATH_RULES:
        provider = PATH_RULES[host]
        if provider == "welcome-to-the-jungle":
            if len(parts) >= 2 and parts[0] == "companies":
                parts = parts[1:]
            elif len(parts) >= 3 and parts[1] == "companies":
                parts = parts[2:]
            else:
                return None
        if TOKEN.fullmatch(parts[0]) and parts[0].lower() not in RESERVED:
            return provider, parts[0].lower()
    for provider, domains in HOST_RULES.items():
        for domain in domains:
            label, separator, suffix = host.partition(".")
            if not separator or suffix != domain or label in RESERVED or not TOKEN.fullmatch(label):
                continue
            # Require a recognizable public career route for broad corporate domains.
            if provider in {"factorial", "altamira", "bizneo"}:
                if parts[0].lower() not in {"careers", "jobs", "career", "vacancies", "trabaja-con-nosotros"}:
                    continue
            if provider == "inrecruiting" and "career" not in parts and parts[0] != "jobs":
                continue
            return provider, host
    return None


def registry_keys(root):
    keys = set()
    for table, fields in {
        "companies": ("career_url", "website_url", "evidence_url"),
        "sources": ("career_url", "feed_url", "url"),
    }.items():
        document = json.loads((root / "data" / f"{table}.json").read_text())
        for entry in document[table] if isinstance(document, dict) else document:
            explicit = set()
            for field in fields:
                key = identity(entry.get(field))
                if key:
                    explicit.add(key)
            keys.update(explicit)
            for raw in _registered_keys(entry):
                provider, tenant = raw.split(":", 1)
                if not any(provider == item[0] for item in explicit):
                    keys.add((provider, tenant))
    return keys


def sample(rows, seed):
    groups = defaultdict(list)
    for row in rows:
        if not row["registered"]:
            groups[row["ats"]].append(row["tenant"])
    return {
        provider: random.Random(f"{seed}:{provider}").sample(sorted(tenants), min(300, len(tenants)))
        for provider, tenants in sorted(groups.items())
    }


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


class IndexClient:
    def __init__(self):
        self.opener = build_opener(NoRedirect())
        self.events = []

    def read(self, endpoint, params=None):
        if params:
            endpoint += "?" + urlencode(params)
        for attempt in range(2):
            started = time.monotonic()
            body = b""
            backoff = 0
            status = "network-error"
            try:
                request = Request(INDEX + endpoint, headers={"User-Agent": USER_AGENT})
                with self.opener.open(request, timeout=20) as response:
                    status = response.status
                    body = response.read(8 * 1024 * 1024 + 1)
                if len(body) > 8 * 1024 * 1024:
                    raise ValueError("Response exceeds byte limit")
                return body
            except HTTPError as error:
                status = error.code
                retry_after = error.headers.get("Retry-After", "")
                error.close()
                if status not in {429, 500, 502, 503, 504} or attempt:
                    raise
                if retry_after and not retry_after.isdecimal():
                    raise  # Do not retry sooner than a server date.
                wait = max(10, int(retry_after or 0))
                if wait > 60:
                    raise
                backoff = wait
            except (URLError, TimeoutError):
                if attempt:
                    raise
                backoff = 10
            finally:
                self.events.append({"endpoint": endpoint, "status": status, "bytes": len(body),
                                    "seconds": round(time.monotonic() - started, 3)})
                time.sleep(max(2, backoff))
        raise RuntimeError("Unreachable retry state")


def collect(client, crawls, providers, page_cap):
    seen = defaultdict(set)
    queries = []
    for crawl in crawls:
        for provider in providers:
            for host in QUERIES[provider]:
                query = {"crawl": crawl, "ats": provider, "host": host, "read": 0}
                queries.append(query)
                params = {"url": host, "matchType": "domain", "output": "json",
                          "pageSize": 1, "filter": "status:200"}
                endpoint = f"/{crawl}-index"
                try:
                    pages = json.loads(client.read(endpoint, {**params, "showNumPages": "true"}))["pages"]
                    query["pages"] = pages
                    for page in range(min(pages, page_cap)):
                        for line in client.read(endpoint, {**params, "page": page}).splitlines():
                            record = json.loads(line)
                            key = identity(record.get("url"))
                            if key and key[0] == provider and record.get("status") == "200":
                                seen[key].add((crawl, host, record["timestamp"]))
                        query["read"] += 1
                    query["status"] = "complete" if query["read"] == pages else "capped"
                except HTTPError as error:
                    query.update(status="incomplete", error=f"HTTP {error.code}")
                except (URLError, TimeoutError, ValueError, KeyError) as error:
                    query.update(status="incomplete", error=type(error).__name__)
    return seen, queries


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", choices=sorted(QUERIES), action="append")
    parser.add_argument("--crawl", action="append", help="Default: latest two in collinfo.json")
    parser.add_argument("--page-cap", type=int, default=2, choices=range(1, 21))
    parser.add_argument("--seed", default="2026-11-23")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    registered = registry_keys(root)
    output = root / ".staging" / "ats-tenant-discovery"
    output.mkdir(parents=True, exist_ok=True)
    if output.resolve() != output:
        parser.error("Staging directory must not be a symlink")
    client = IndexClient()
    crawls = args.crawl or [entry["id"] for entry in json.loads(client.read("/collinfo.json"))[:2]]
    if not 2 <= len(set(crawls)) == len(crawls) <= 3 or any(
        not re.fullmatch(r"CC-MAIN-\d{4}-\d{2}", crawl) for crawl in crawls
    ):
        parser.error("Select two or three distinct Common Crawl IDs")
    seen, queries = collect(client, crawls, args.provider or sorted(QUERIES), args.page_cap)
    rows = []
    for (provider, tenant), sightings in sorted(seen.items()):
        # Keep just the latest indexed capture per crawl and query host.
        latest = {(crawl, host): stamp for crawl, host, stamp in sorted(sightings)}
        rows.append({"ats": provider, "tenant": tenant, "registered": (provider, tenant) in registered,
                     "country": "sconosciuto",
                     "observations": [{"crawl": crawl, "query_host": host, "timestamp": stamp}
                                      for (crawl, host), stamp in sorted(latest.items())]})
    summary = {}
    for provider in args.provider or sorted(QUERIES):
        matches = [row for row in rows if row["ats"] == provider]
        known = sum(row["registered"] for row in matches)
        summary[provider] = {"observed": len(matches), "registered": known,
                             "new": len(matches) - known,
                             "registry_reference": sum(key[0] == provider for key in registered),
                             "all_queries_complete": all(q["status"] == "complete"
                                                         for q in queries if q["ats"] == provider)}
    result = {"summary": summary, "crawls": crawls, "queries": queries, "requests": client.events, "tenants": rows,
              "sample_seed": args.seed, "sample": sample(rows, args.seed)}
    path = output / "inventory.json"
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    temporary.replace(path)


if __name__ == "__main__":
    main()
