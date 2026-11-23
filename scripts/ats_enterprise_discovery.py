"""Enumerate enterprise career board identities from Common Crawl in staging."""
from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
import re
import sys
import time
from urllib.parse import parse_qs

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from collector.ats_channel_discovery import safe_url
from scripts.ats_columnar_index import ColumnarIndex, DATA, overlaps
from scripts.ats_tenant_discovery import inspect_partitions, surt

DOMAINS = {
    "workday": ("myworkdayjobs.com", "myworkdaysite.com"),
    "successfactors": ("successfactors.eu", "successfactors.com", "jobs2web.com"),
    "oracle": ("oraclecloud.com",),
    "taleo": ("taleo.net",),
    "avature": ("avature.net",),
    "cornerstone": ("csod.com",),
    "icims": ("icims.com",),
    "phenom": ("phenompeople.com", "phenom.com"),
}
TOKEN = re.compile(r"^[a-z0-9][a-z0-9_.-]{0,99}$")
LOCALE = re.compile(r"[a-z]{2}[-_][a-z]{2}")
RESERVED = {"api", "www", "home", "health", "search", "static", "assets", "login",
            "job", "robots.txt", "sitemap.xml", "favicon.ico", "apply", "cxs"}
ROUTE_SQL = """
    SELECT DISTINCT {projection}
    FROM read_parquet(?)
    WHERE url_surtkey >= ? AND url_surtkey < ? AND fetch_status = 200
      AND regexp_matches(lower(split_part(url, '?', 1)), ?)
"""
PATH_FILTER = {
    "oracle": r"/hcmui/candidateexperience/(?:[^/]+/)?sites/[^/]+",
    "taleo": r"/careersection/[^/]+(?:/?$|/(?:jobsearch|jobdetail|moresearch|joblist)\.ftl(?:/|$))",
    "avature": r"/(?:careers|career|jobs|externalcareers)(?:/|$)",
    "cornerstone": r"/ux/ats/careersite/[0-9]+|/ats/careersite/",
    "icims": r"/jobs(?:/|$)|/careerportal(?:/|$)",
    "phenom": r"/(?:global/|[a-z]{2}/)?(?:[a-z]{2}/)?(?:job|search-results|career)(?:/|$)",
    "successfactors": r"/(?:career|careers|job|talentcommunity)(?:/|$)",
    "workday": r"^https?://[^/]+/[^/]+",
}


def identity(provider, raw):
    url = safe_url(raw)
    if not url or not any(url.hostname.endswith("." + domain) for domain in DOMAINS[provider]):
        return None
    host = url.hostname
    path = [part.lower() for part in url.path.split("/") if part]
    route = "/".join(path)
    if host.split(".")[0] in {"api", "support", "community", "static", "cdn", "www"}:
        return None
    if provider == "workday":
        if host.endswith(".myworkdaysite.com"):
            if len(path) >= 3 and path[0] == "recruiting" and all(TOKEN.fullmatch(p) for p in path[1:3]):
                return host + "/" + "/".join(path[:3])
            return None
        if not path or not re.search(r"\.wd\d+\.myworkdayjobs\.com$", host):
            return None
        if LOCALE.fullmatch(path[0]):
            path = path[1:]
        if path and TOKEN.fullmatch(path[0]) and path[0] not in RESERVED:
            if len(path) == 1 or path[1] in {"job", "jobs"}:
                return host + "/" + path[0]
        return None
    if provider == "successfactors":
        if host.endswith(".jobs2web.com") and path and path[0] in {"job", "career", "careers", "talentcommunity"}:
            return host
        if path and path[0] in {"career", "careers"} and len(url.query) < 4096:
            company = parse_qs(url.query.lower()).get("company", [])
            if len(company) == 1 and TOKEN.fullmatch(company[0]):
                return f"{host}/{path[0]}/{company[0]}"
        return None
    match = re.match({
        "oracle": r"hcmui/candidateexperience/(?:[^/]+/)?sites/([^/]+)(?:/|$)",
        "taleo": r"careersection/([a-z0-9_-]+)(?:/?$|/(?:jobsearch|jobdetail|moresearch|joblist)\.ftl(?:/|$))",
        "avature": r"(?:[a-z]{2}(?:[-_][a-z]{2})?/)?(?:careers|career|jobs|externalcareers)(?:/|$)",
        "cornerstone": r"ux/ats/careersite/([0-9]+)(?:/|$)|ats/careersite/",
        "icims": r"(?:jobs|careerportal)(?:/|$)",
        "phenom": r"(?:global/|[a-z]{2}/)?(?:[a-z]{2}/)?(?:job|search-results|career)(?:/|$)",
    }[provider], route)
    if not match:
        return None
    site = match[1] if match.lastindex else None
    if site and (not TOKEN.fullmatch(site) or site in RESERVED):
        return None
    return host + ("/" + site if site else "")


def enumerate_enterprise(index, partitions, providers):
    sightings = defaultdict(set)
    reports = []
    for crawl, files in partitions.items():
        for provider in providers:
            failures = sum("error" in row for row in files)
            count = 0
            for domain in DOMAINS[provider]:
                prefix = surt(domain, subdomains=True)
                for item in files:
                    if "bounds" not in item or not overlaps(item["bounds"], prefix):
                        continue
                    count += 1
                    # Preserve query selectors only for the shared SAP career host.
                    projection = ("split_part(url, '?', 1), "
                                  "regexp_extract_all(lower(split_part(url, '?', 2)), '(?:^|&)company=([^&#]*)', 1)"
                                  if provider == "successfactors"
                                  else "regexp_extract(url, '^https://[^/?#]+(?:/[^/?#]+){0,7}', 0)")
                    sql = ROUTE_SQL.format(projection=projection)
                    try:
                        rows = index.parquet(sql, [DATA + item["path"], prefix, prefix + "\uffff",
                                                   PATH_FILTER[provider]], "enterprise-scan")
                    except Exception as error:
                        failures += 1
                        print(f"{crawl} {provider}: {error}", file=sys.stderr, flush=True)
                        continue
                    for url, *extra in rows:
                        if extra and extra[0]:
                            if len(extra[0]) != 1 or not TOKEN.fullmatch(extra[0][0]):
                                continue
                            url += "?company=" + extra[0][0]
                        key = identity(provider, url)
                        if key:
                            sightings[provider, key].add(crawl)
            reports.append({"crawl": crawl, "ats": provider, "ranges": count, "failures": failures})
    return sightings, reports


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", choices=sorted(DOMAINS), action="append")
    args = parser.parse_args()
    staging = ROOT / ".staging" / "ats-enterprise"
    shared = ROOT / ".staging" / "ats-tenant-discovery"
    if staging.resolve() != staging or shared.resolve() != shared:
        parser.error("Staging directories must not be symlinks")
    staging.mkdir(parents=True, exist_ok=True)
    shared.mkdir(parents=True, exist_ok=True)
    index = ColumnarIndex(staging)
    started = time.monotonic()
    crawls = index.recent()
    files = inspect_partitions(index, crawls, shared)
    providers = sorted(set(args.provider or DOMAINS))
    sightings, reports = enumerate_enterprise(index, files, providers)
    counts = {provider: sum(key[0] == provider for key in sightings) for provider in providers}
    tenants = [{"ats": provider, "tenant": key, "crawls": sorted(seen)}
               for (provider, key), seen in sorted(sightings.items())]
    result = {"crawls": crawls, "counts": counts, "queries": reports,
              "wall_seconds": round(time.monotonic() - started, 3),
              "requests": index.events, "tenants": tenants}
    output = staging / "inventory.json"
    temporary = output.with_suffix(".tmp")
    with temporary.open("x") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    temporary.replace(output)
    print(json.dumps({"counts": counts, "failed_ranges": sum(r["failures"] for r in reports)}))


if __name__ == "__main__":
    main()
