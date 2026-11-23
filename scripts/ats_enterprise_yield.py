"""Sample enterprise sitemaps with strict per-host robots and GET only."""
from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import gzip
from email.utils import parsedate_to_datetime
from io import BytesIO
import json
from pathlib import Path
import random
import re
import sys
import time
from urllib.error import HTTPError
from urllib.request import HTTPRedirectHandler, Request, build_opener
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from collector.adapters import AGENT
from collector.ats_channel_discovery import safe_url
from collector.classify import classify_role, plain
from collector.pipeline import record_countries
from collector.universal import Document
from scripts.ats_enterprise_discovery import DOMAINS, identity

LIMIT = 2_000_000
BUDGET = 7
REVIEWED = {"workday", "avature", "icims", "cornerstone"}


class StopRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def robots_policy(text):
    groups = []
    sitemaps = []
    agents, directives = [], []
    for raw in text.splitlines():
        name, sep, value = raw.partition("#")[0].partition(":")
        if not sep:
            continue
        name, value = name.strip().lower(), value.strip()
        if name == "sitemap":
            sitemaps.append(value)
        elif name == "user-agent":
            if directives:
                groups.append((agents, directives))
                agents, directives = [], []
            agents.append(value.lower())
        elif name in {"allow", "disallow", "crawl-delay"} and agents and value:
            directives.append((name, value))
    groups.append((agents, directives))
    product = AGENT.split("/", 1)[0].lower()
    matches = [(len(a) if a != "*" else 0, rules)
               for uas, rules in groups for a in uas if a == "*" or a == product]
    best = max((score for score, _ in matches), default=-1)
    rules = [rule for score, rs in matches if score == best for rule in rs]
    delays = [float(v) for n, v in rules if n == "crawl-delay" and re.fullmatch(r"\d+(?:\.\d+)?", v)]
    return rules, sitemaps, max([2.0, *delays])


def robots_allows(rules, path):
    matches = []
    for directive, pattern in rules:
        if directive == "crawl-delay":
            continue
        rule = pattern.rstrip("$")
        regex = re.escape(rule).replace(r"\*", ".*") + ("$" if pattern.endswith("$") else "")
        if re.match(regex, path):
            matches.append((len(rule.replace("*", "")), directive == "allow"))
    return max(matches, default=(0, True))[1]


class PublicClient:
    def __init__(self, host):
        self.host = host
        self.requests = self.bytes = 0
        self.last = 0.0
        self.rules = None
        self.delay = 2
        self.deadline = time.monotonic() + 55
        self.opener = build_opener(StopRedirect())

    def get(self, raw, robots=False):
        url = safe_url(raw)
        if not url or url.hostname != self.host or url.query or url.fragment:
            raise ValueError("outside exact public scope")
        if robots:
            if url.path != "/robots.txt" or self.requests:
                raise ValueError("invalid robots preflight")
        elif self.rules is None or not robots_allows(self.rules, url.path or "/"):
            raise ValueError("robots disallow or unavailable")
        wait = max(0, self.last + self.delay - time.monotonic())
        if self.requests >= BUDGET or time.monotonic() + wait >= self.deadline:
            raise ValueError("budget exhausted")
        time.sleep(wait)
        self.last = time.monotonic()
        self.requests += 1
        request = Request(raw, headers={"User-Agent": AGENT, "Accept-Encoding": "identity"})
        with self.opener.open(request, timeout=min(8, self.deadline - self.last)) as response:
            if response.status != 200:
                raise ValueError("HTTP 200 required")
            body = response.read(LIMIT + 1)
            self.bytes += len(body)
            if len(body) > LIMIT:
                raise ValueError("response too large")
            return body

    def read_robots(self):
        body = self.get(f"https://{self.host}/robots.txt", robots=True)
        text = body.decode("utf-8-sig")
        if re.search(r"<(?:html|!doctype)\b", text, re.I):
            raise ValueError("robots returned HTML")
        self.rules, sitemaps, self.delay = robots_policy(text)
        return sitemaps


def sitemap_entries(data):
    if data.startswith(b"\x1f\x8b"):
        with gzip.GzipFile(fileobj=BytesIO(data)) as stream:
            data = stream.read(LIMIT + 1)
        if len(data) > LIMIT:
            raise ValueError("sitemap inflated past byte limit")
    root = ET.fromstring(data)
    tag = root.tag.rsplit("}", 1)[-1]
    if tag not in {"urlset", "sitemapindex"}:
        raise ValueError("unknown sitemap type")
    return tag, [node.text.strip() for node in root.findall("./*/{*}loc") if node.text]


def staging_fields(post, host):
    locations = post.get("jobLocation") or []
    if isinstance(locations, dict):
        locations = [locations]
    countries = set()
    for location in locations if isinstance(locations, list) else []:
        address = location.get("address", {}) if isinstance(location, dict) else {}
        if not isinstance(address, dict):
            continue
        country = address.get("addressCountry")
        if isinstance(country, dict):
            country = country.get("name")
        city = address.get("addressLocality")
        countries.update(record_countries({"location": city if isinstance(city, str) else "",
                                           "country": country if isinstance(country, str) else None}))
    title = post.get("title")
    description = post.get("description")
    employment = post.get("employmentType")
    role = classify_role(plain(title), plain(description if isinstance(description, str) else ""),
                         employment if isinstance(employment, str) else "") if isinstance(title, str) else None
    # schema.org url identifies the listing. potentialAction may identify an application.
    actions = post.get("potentialAction") or []
    if isinstance(actions, dict):
        actions = [actions]
    has_apply = False
    for action in actions if isinstance(actions, list) else []:
        if not isinstance(action, dict) or action.get("@type") != "ApplyAction":
            continue
        target = action.get("target")
        if isinstance(target, dict):
            target = target.get("urlTemplate")
        parsed = safe_url(target)
        has_apply |= bool(parsed and parsed.hostname == host)
    date = post.get("datePosted")
    return {"title": isinstance(title, str) and bool(title.strip()), "location": bool(countries),
            "date": isinstance(date, str) and bool(re.match(r"^\d{4}-\d{2}-\d{2}", date)),
            "application_link": has_apply, "countries": sorted(countries),
            "hr_stage": bool(countries and role and role["internship_type"] == "internship")}


def in_board(provider, tenant, url, sitemap=False):
    if provider == "workday":
        return (identity(provider, url.rsplit("/", 1)[0]) == tenant if sitemap
                else identity(provider, url) == tenant and "/job/" in url.lower())
    parsed = safe_url(url)
    if not parsed or parsed.hostname != tenant or parsed.query or parsed.fragment:
        return False
    path = parsed.path.lower()
    if provider == "icims":
        return "sitemap" in path if sitemap else bool(re.fullmatch(r"/jobs/[0-9]+/[^/]+/job/?", path))
    if not re.match(r"/(?:[a-z]{2}[-_][a-z]{2}/)?careers/", path):
        return False
    return "sitemap" in path if sitemap else "/jobdetail/" in path


def cornerstone_urls(stage, cohort, crawls):
    """Choose detail URLs from index metadata for boards without a public feed."""
    from scripts.ats_columnar_index import ColumnarIndex, DATA, overlaps
    from scripts.ats_tenant_discovery import surt

    index = ColumnarIndex(stage)
    cache = ROOT / ".staging" / "ats-tenant-discovery" / "bounds.jsonl"
    hosts = sorted({tenant.split("/")[0] for tenant in cohort})
    keys = set(cohort)
    candidates = {}
    prefix = surt("csod.com", subdomains=True)
    for line in cache.read_text().splitlines():
        item = json.loads(line)
        if (not any(f"/crawl={crawl}/" in item["path"] for crawl in crawls)
                or "bounds" not in item or not overlaps(item["bounds"], prefix)):
            continue
        records = index.parquet("""
            SELECT DISTINCT split_part(url, '?', 1)
            FROM read_parquet(?)
            WHERE url_surtkey >= ? AND url_surtkey < ? AND fetch_status = 200
              AND url_host_name IN (SELECT unnest(?))
              AND regexp_matches(lower(split_part(url, '?', 1)),
                                 '/ux/ats/careersite/[0-9]+/home/requisition/[0-9]+/?$')
        """, [DATA + item["path"], prefix, prefix + "\uffff", hosts], "cornerstone-detail")
        for (url,) in records:
            key = identity("cornerstone", url)
            if key in keys:
                candidates.setdefault(key, set()).add(url.rstrip("/"))
    with (stage / "cornerstone-metadata-requests.json").open("x") as stream:
        json.dump(index.events, stream)
    return candidates


def retry_delay(value):
    if not value:
        return 60
    if value.isdecimal():
        return max(60, int(value))
    try:
        date = parsedate_to_datetime(value)
        return max(60, (date - datetime.now(timezone.utc)).total_seconds())
    except (TypeError, ValueError, OverflowError):
        return 60


def measure(provider, tenant, seed, candidate_urls=()):
    host = tenant.split("/")[0]
    client = PublicClient(host)
    start = time.monotonic()
    row = {"tenant": tenant, "state": "incerto", "pages": 0, "jobposting": [], "listed_urls": 0}
    try:
        if not any(host.endswith("." + domain) for domain in DOMAINS[provider]):
            raise ValueError("tenant outside reviewed ATS domains")
        ads = client.read_robots()
        if provider == "cornerstone":
            jobs = sorted(url for url in candidate_urls if identity(provider, url) == tenant)
            if not jobs:
                raise ValueError("no indexed detail candidate for board")
        else:
            selected = [url for url in ads if in_board(provider, tenant, url, sitemap=True)]
            if not selected:
                raise ValueError("no robots-advertised sitemap for site")
            tag, urls = sitemap_entries(client.get(sorted(selected)[0]))
            row["state"] = "ammesso"
            if tag == "sitemapindex":
                # A nested sitemap is bounded to this exact host and reviewed board path.
                children = [url for url in urls if in_board(provider, tenant, url, sitemap=True)]
                if not children:
                    raise ValueError("no in-scope nested sitemap")
                tag, urls = sitemap_entries(client.get(sorted(children)[0]))
            if tag != "urlset":
                raise ValueError("unexpected nested sitemap")
            jobs = sorted({url for url in urls if in_board(provider, tenant, url)})
        row["listed_urls"] = len(jobs)
        for url in random.Random(f"{seed}:{tenant}").sample(jobs, min(3, len(jobs))):
            body = client.get(url)
            if re.search(rb"<title[^>]*>[^<]*(?:captcha|access denied|just a moment)", body, re.I):
                raise ValueError("access challenge")
            row["pages"] += 1
            posts = Document(body, url).jobposts()
            if provider == "cornerstone" and len(posts) == 1:
                row["state"] = "ammesso"
            if len(posts) == 1:
                row["jobposting"].append(staging_fields(posts[0], host))
    except HTTPError as error:
        row["stop"] = f"HTTP {error.code}"
        if error.code == 429:
            row["retry_not_before"] = time.time() + retry_delay(error.headers.get("Retry-After"))
        error.close()
    except (OSError, ValueError, ET.ParseError) as error:
        row["stop"] = str(error) if type(error) is ValueError else type(error).__name__
    return dict(row, get=client.requests, bytes=client.bytes, seconds=round(time.monotonic() - start, 3))


def summarize_staging(stage):
    from scripts.ats_tenant_yield import estimate_detectable_tenants

    all_admitted = []
    reports = {}
    for provider in sorted(REVIEWED):
        path = stage / f"{provider}-sample.json"
        if not path.exists():
            continue
        initial = json.loads(path.read_text())
        attempts = list(initial["rows"])
        latest = {row["tenant"]: row for row in attempts}
        for retry in ("robots-rate-limit", "nested-sitemap"):
            evidence = stage / f"{provider}-sample-{retry}.json"
            if evidence.exists():
                rows = json.loads(evidence.read_text())["rows"]
                attempts.extend(rows)
                latest.update((row["tenant"], row) for row in rows)
        cohort = list(latest.values())
        admitted = [row for row in cohort if row["state"] == "ammesso"]
        all_admitted.extend((provider, row["tenant"], row) for row in admitted)
        signals = [post for row in cohort for post in row["jobposting"] if post["hr_stage"]]
        euro_tenants = sum(any(post["location"] for post in row["jobposting"]) for row in cohort)
        intervals = []
        for row in cohort:
            intervals.append({
                "stratum": "all", "population": initial["population"],
                "state": "feed-read" if row["state"] == "ammesso" else "incomplete",
                "internships": [post for post in row["jobposting"] if post["hr_stage"]],
            })
        reports[provider] = {
            "sample": len(cohort), "admitted": len(admitted),
            "pages": sum(row["pages"] for row in cohort), "eu_tenants": euro_tenants,
            "signals": len(signals), "countries": dict(Counter(code for post in signals for code in post["countries"])),
            "get": sum(row["get"] for row in attempts), "bytes": sum(row["bytes"] for row in attempts),
            "seconds": round(sum(row["seconds"] for row in attempts), 3),
            "operational_estimate": estimate_detectable_tenants(intervals),
        }
    sample = random.Random("2026-11-23-jsonld").sample(sorted(all_admitted), min(100, len(all_admitted)))
    posts = [post for _, _, row in sample for post in row["jobposting"]]
    fields = ("title", "location", "date", "application_link")
    schema = {
        "tenant_sample": len(sample), "tenants_with_pages": sum(row["pages"] > 0 for _, _, row in sample),
        "pages": sum(row["pages"] for _, _, row in sample), "jobposting": len(posts),
        "fields": {field: sum(post[field] for post in posts) for field in fields},
        "all_four": sum(all(post[field] for field in fields) for post in posts),
    }
    return {"platforms": reports, "jsonld": schema}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", choices=sorted(REVIEWED))
    parser.add_argument("--summary", action="store_true", help="Report completed staging samples without network")
    parser.add_argument("--native-trust", action="store_true")
    parser.add_argument("--retry", choices=("robots-rate-limit", "nested-sitemap"),
                        help="Repeat only the selected incomplete attempts after the initial run")
    args = parser.parse_args()
    stage = ROOT / ".staging" / "ats-enterprise"
    if stage.resolve() != stage:
        parser.error("Staging must not be a symlink")
    if args.summary:
        if args.provider or args.retry:
            parser.error("--summary reports all completed platforms")
        print(json.dumps(summarize_staging(stage), indent=2))
        return
    if not args.provider:
        parser.error("--provider is required for live staging")
    if args.native_trust:
        import truststore
        truststore.inject_into_ssl()
    inventory = json.loads((stage / "inventory.json").read_text())
    population = sorted(row["tenant"] for row in inventory["tenants"] if row["ats"] == args.provider)
    seed = "2026-11-23-access-v2"
    cohort = random.Random(seed).sample(population, min(100, len(population)))
    started = time.monotonic()
    rows = []
    suffix = f"-{args.retry}" if args.retry else ""
    if args.retry:
        initial = json.loads((stage / f"{args.provider}-sample.json").read_text())
        previous = initial["rows"]
        def eligible(row):
            if args.retry == "nested-sitemap":
                return row.get("stop") == "no in-scope nested sitemap"
            return row.get("stop") == "host blocked" or (row.get("get") == 1 and row.get("stop") == "HTTP 429")
        eligible_rows = [row for row in previous if eligible(row)]
        cohort = [row["tenant"] for row in eligible_rows]
        if args.retry == "robots-rate-limit" and cohort:
            # Conservatively wait for every host from the previous run before
            # retrying a blocked cohort. A repeated block stops the host.
            earliest = datetime.fromisoformat(initial["observed_at"]).timestamp() + 60
            latest = max([earliest, *(row.get("retry_not_before", 0) for row in eligible_rows)])
            if latest - time.time() > 60:
                parser.error("Retry-After is still active; resume after the recorded time")
            time.sleep(max(0, latest - time.time()))
    candidates = (cornerstone_urls(stage, cohort, inventory["crawls"])
                  if args.provider == "cornerstone" else {})
    # Grouping by host prevents two workers from interleaving tenants on one host.
    groups = {}
    for tenant in cohort:
        groups.setdefault(tenant.split("/")[0], []).append(tenant)

    def run_group(tenants):
        results = []
        for tenant in tenants:
            result = measure(args.provider, tenant, seed, candidates.get(tenant, ()))
            results.append(result)
            if result.get("stop") in {"HTTP 403", "HTTP 429"}:
                results.extend({"tenant": other, "state": "incerto", "stop": "host blocked",
                                "pages": 0, "jobposting": [], "get": 0, "bytes": 0, "seconds": 0}
                               for other in tenants[len(results):])
                break
            if len(results) < len(tenants):
                time.sleep(60)
        return results

    with (stage / f"{args.provider}-sample{suffix}.jsonl").open("x", buffering=1) as checkpoint:
        with ThreadPoolExecutor(max_workers=4) as pool:
            jobs = [pool.submit(run_group, group) for group in groups.values()]
            for job in as_completed(jobs):
                for row in job.result():
                    checkpoint.write(json.dumps(row) + "\n")
                    rows.append(row)
    total = {"observed_at": datetime.now(timezone.utc).isoformat(), "population": len(population),
             "sample": len(rows), "states": Counter(row["state"] for row in rows),
             "wall_seconds": round(time.monotonic() - started, 3), "rows": rows}
    with (stage / f"{args.provider}-sample{suffix}.json").open("x") as stream:
        json.dump(total, stream, indent=2)
        stream.write("\n")
    print(json.dumps({k: v for k, v in total.items() if k != "rows"}))


if __name__ == "__main__":
    main()
