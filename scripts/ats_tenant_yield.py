"""Measure the staged sample through existing public-feed adapters."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
import math
import statistics
import threading
from pathlib import Path
import sys
import time
from urllib.error import HTTPError
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.ats_tenant_discovery import identity
from collector.adapters import collect
from collector.classify import COUNTRIES, classify_role
from collector.pipeline import record_countries
from collector.runtime import BudgetClient


PUBLIC_FEEDS = {
    "greenhouse": "https://developers.greenhouse.io/job-board.html",
    "lever": "https://github.com/lever/postings-api",
    "personio-xml": "https://support.personio.de/hc/en-us/articles/207576365-Integrate-jobs-from-Personio-into-your-website-via-XML",
    "recruitee": "https://docs.recruitee.com/reference/offers",
    "workable": "https://workable.readme.io/reference/jobs-1",
}


def feed_source(provider, tenant):
    region, _, board = tenant.rpartition("/")
    source = {"id": f"staging:{provider}:{tenant}", "employer": tenant,
              "adapter": provider, "board": board, "enabled": False}
    if provider == "greenhouse":
        source["api_host"] = "boards-api.eu.greenhouse.io" if region == "eu" else "boards-api.greenhouse.io"
        hosts = [source["api_host"]]
    elif provider == "lever":
        source["region"] = region
        hosts = ["api.eu.lever.co" if region == "eu" else "api.lever.co"]
    elif provider in {"personio-xml", "recruitee"}:
        path = "/xml" if provider == "personio-xml" else "/api/offers/"
        source["feed_url"] = "https://" + tenant + path
        hosts = [tenant]
    elif provider == "workable":
        source["adapter"] = "workable-public"
        source["feed_url"] = f"https://www.workable.com/api/accounts/{board}?details=true"
        hosts = ["www.workable.com", "apply.workable.com"]
    else:
        return None
    return dict(source, allowed_hosts=hosts)


class FeedClient(BudgetClient):
    def __init__(self, hosts):
        super().__init__(seconds=45, max_requests=12, delay=1)
        self.hosts = set(hosts)
        self.redirect_scope_allowed = self.in_scope

    def in_scope(self, url):
        parsed = urlsplit(url)
        return parsed.scheme == "https" and parsed.netloc in self.hosts

    def request(self, url, method="GET", **kwargs):
        if method != "GET" or not self.in_scope(url):
            raise ValueError("Staging request outside reviewed GET scope")
        return super().request(url, method=method, **kwargs)


HTTP_COUNT = threading.local()


def audit_request(event, args):
    if event == "urllib.Request" and args[3] == "GET" and hasattr(HTTP_COUNT, "get"):
        HTTP_COUNT.get += 1


def measure(provider, tenant, source):
    client = FeedClient(source["allowed_hosts"])
    start = time.monotonic()
    row = {"ats": provider, "tenant": tenant, "state": "incomplete",
           "observed_at": datetime.now(timezone.utc).isoformat()}
    HTTP_COUNT.get = 0
    try:
        records = collect(source, client)
        internships = {}
        europe = set()
        unknown = set()
        for record in records:
            external_id = record["external_id"]
            countries = sorted(set(record_countries(record)) & COUNTRIES.keys())
            if not countries:
                if not record.get("countries") and not record.get("country"):
                    unknown.add(external_id)
                continue
            europe.add(external_id)
            role = classify_role(record["title"], record["text"], record.get("employment", ""))
            if role and role["internship_type"] == "internship":
                internships[external_id] = {"external_id": external_id, "countries": countries,
                                            "proof": "feed-signal-only"}
        row.update(state="feed-read", postings=len(records), european_postings=len(europe),
                   unknown_location=len(unknown - europe), internships=list(internships.values()))
    except (ValueError, OSError, HTTPError, RuntimeError, KeyError, TypeError) as error:
        row["error"] = type(error).__name__
        if isinstance(error, HTTPError):
            row["http_status"] = error.code
        elif "robots" in str(error):
            row["error"] = "robots-unavailable-or-disallowed"
    finally:
        measured_get = HTTP_COUNT.get
        del HTTP_COUNT.get
    return dict(row, logical_get=client.requests, urllib_get=measured_get, body_bytes=client.bytes,
                seconds=round(time.monotonic() - start, 3))


def estimate(cohort):
    strata = defaultdict(list)
    if not cohort or any(row["state"] != "feed-read" for row in cohort):
        return "non dimostrato"
    for row in cohort:
        strata[row["stratum"]].append(row)
    total = variance = 0
    fully_observed = True
    for stratum in strata.values():
        population = stratum[0]["population"]
        counts = [len(row["internships"]) for row in stratum]
        n = len(counts)
        total += population * statistics.mean(counts)
        if n < population:
            fully_observed = False
            if n < 30 or sum(value > 0 for value in counts) < 10:
                return "non dimostrato"  # A rare or sparse yield cannot support this interval.
            variance += population ** 2 * (1 - n / population) * statistics.variance(counts) / n
    margin = 1.96 * math.sqrt(variance)
    return {"total_feed_signals": round(total, 1), "interval95": [
        round(max(0, total - margin), 1), round(total + margin, 1)],
            "method": "census" if fully_observed else "stratified-normal-with-finite-population-correction"}


def estimate_detectable_tenants(cohort):
    """Estimate operational detections with simultaneous Wilson bounds by stratum."""
    strata = defaultdict(list)
    for row in cohort:
        strata[row["stratum"]].append(row)
    if not strata or any(row["state"] not in {"feed-read", "incomplete"} for row in cohort):
        return "non dimostrato"
    z = statistics.NormalDist().inv_cdf(1 - .05 / (2 * len(strata)))
    lower = upper = total = 0
    for rows in strata.values():
        n, population = len(rows), rows[0]["population"]
        rate = sum(bool(row.get("internships")) for row in rows) / n
        total += population * rate
        if n == population:
            lower += population * rate
            upper += population * rate
            continue
        denominator = 1 + z * z / n
        center = (rate + z * z / (2 * n)) / denominator
        margin = z * math.sqrt(rate * (1 - rate) / n + z * z / (4 * n * n)) / denominator
        lower += population * max(0, center - margin)
        upper += population * min(1, center + margin)
    return {"tenant_detections": round(total, 1), "interval95": [math.floor(lower), math.ceil(upper)],
            "method": "stratified-operational-detections-bonferroni-wilson"}


def summarize(rows):
    groups = defaultdict(list)
    for row in rows:
        groups[row["ats"]].append(row)
    result = {}
    for provider, cohort in sorted(groups.items()):
        jobs = [job for row in cohort for job in row.get("internships", [])]
        requests = sum(row.get("logical_get", 0) for row in cohort)
        body_bytes = sum(row.get("body_bytes", 0) for row in cohort)
        seconds = sum(row.get("seconds", 0) for row in cohort)
        result[provider] = {
            "sampled": len(cohort), "feed_reads": sum(row["state"] == "feed-read" for row in cohort),
            "postings": sum(row.get("postings", 0) for row in cohort),
            "tenants_with_european_postings": sum(row.get("european_postings", 0) > 0 for row in cohort),
            "european_postings": sum(row.get("european_postings", 0) for row in cohort),
            "urllib_get": sum(row.get("urllib_get", 0) for row in cohort),
            "estimate": estimate(cohort),
            "estimate_detectable_tenants": estimate_detectable_tenants(cohort),
            "hr_stage_feed_signals": len(jobs),
            "stage_signals_by_country": dict(Counter(code for job in jobs for code in job["countries"])),
            "logical_get": requests, "body_bytes": body_bytes, "source_seconds": round(seconds, 3),
            "cost_per_stage_feed_signal": ({"logical_get": requests / len(jobs),
                                           "body_bytes": body_bytes / len(jobs),
                                           "source_seconds": round(seconds / len(jobs), 3)}
                                          if jobs else "non dimostrato"),
        }
    return result


def reviewed_url(provider, tenant):
    region, _, board = tenant.rpartition("/")
    hosts = {
        "greenhouse": "job-boards.eu.greenhouse.io" if region == "eu" else "job-boards.greenhouse.io",
        "lever": "jobs.eu.lever.co" if region == "eu" else "jobs.lever.co",
        "workable": "apply.workable.com",
    }
    return f"https://{hosts[provider]}/{board}" if provider in hosts else f"https://{tenant}/"


def scan_provider(provider, members, staging, live, resume=False, retry_transport=False):
    rows = []
    path = staging / f"yield-{provider}.jsonl"
    if path.is_symlink():
        raise ValueError("Staging output must not be a symlink")
    previous = {}
    if resume and path.exists():
        previous = {row["tenant"]: row for row in
                    (json.loads(line) for line in path.read_text().splitlines())}
    missing = []
    for member in members:
        tenant = member["tenant"]
        old = previous.get(tenant)
        if (old and old["state"] in {"feed-read", "incomplete"}
                and not (retry_transport and old.get("error") == "URLError")):
            rows.append(dict(old, stratum=member["stratum"], population=member["population"]))
        else:
            missing.append(member)
    # Preserving existing attempts makes staged refreshes safe to resume.
    snapshot = path.with_suffix(".tmp")
    with snapshot.open("x") as stream:
        stream.writelines(json.dumps(row) + "\n" for row in rows)
    snapshot.replace(path)
    with path.open("a", buffering=1) as stream:
        for member in missing:
            tenant = member["tenant"]
            row = {"ats": provider, "tenant": tenant, "state": "access-not-demonstrated"}
            if provider in PUBLIC_FEEDS and identity(reviewed_url(provider, tenant)) == (provider, tenant):
                row["state"] = "ready"
                if live:
                    row = measure(provider, tenant, feed_source(provider, tenant))
            row.update(stratum=member["stratum"], population=member["population"])
            stream.write(json.dumps(row) + "\n")
            rows.append(row)
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--native-trust", action="store_true", help="Use optional truststore from staging")
    parser.add_argument("--provider", choices=sorted(PUBLIC_FEEDS), action="append")
    parser.add_argument("--resume", action="store_true", help="Reuse attempts in the same staging session")
    parser.add_argument("--retry-transport", action="store_true", help="Retry only prior URL transport errors")
    args = parser.parse_args()
    if args.retry_transport and not (args.resume and args.live):
        parser.error("--retry-transport requires --resume and --live")
    staging = Path(__file__).resolve().parents[1] / ".staging" / "ats-tenant-discovery"
    if staging.resolve() != staging:
        parser.error("Staging directory must not be a symlink")
    inventory = json.loads((staging / "inventory.json").read_text())
    selected = {provider: members for provider, members in inventory["sample"].items()
                if not args.provider or provider in args.provider}
    if args.native_trust:
        import truststore

        truststore.inject_into_ssl()
    sys.addaudithook(audit_request)
    started = time.monotonic()
    with ThreadPoolExecutor(max_workers=5) as pool:
        jobs = [pool.submit(scan_provider, provider, members, staging, args.live, args.resume, args.retry_transport)
                for provider, members in selected.items()]
        rows = [row for job in jobs for row in job.result()]
    counts = Counter(row["state"] for row in rows)
    result = {"states": counts, "summary": summarize(rows),
              "wall_seconds": round(time.monotonic() - started, 3), "rows": rows}
    if args.live:
        output = staging / ("yield-" + "-".join(sorted(args.provider)) + ".json"
                            if args.provider else "yield.json")
        temporary = output.with_suffix(".tmp")
        with temporary.open("x") as stream:
            json.dump(result, stream, indent=2)
            stream.write("\n")
        temporary.replace(output)
    print(json.dumps(counts, sort_keys=True))


if __name__ == "__main__":
    main()
