"""Measure the staged sample through existing public-feed adapters."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import sys
import time
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.ats_tenant_discovery import identity
from collector.adapters import collect
from collector.classify import classify_role
from collector.pipeline import record_countries
from collector.runtime import BudgetClient


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
        super().__init__(seconds=45, max_requests=12, delay=2)
        self.hosts = set(hosts)
        self.redirect_scope_allowed = self.in_scope

    def in_scope(self, url):
        parsed = urlsplit(url)
        return parsed.scheme == "https" and parsed.netloc in self.hosts

    def request(self, url, method="GET", **kwargs):
        if method != "GET" or not self.in_scope(url):
            raise ValueError("Staging request outside reviewed GET scope")
        return super().request(url, method=method, **kwargs)


def measure(provider, tenant, source):
    client = FeedClient(source["allowed_hosts"])
    start = time.monotonic()
    row = {"ats": provider, "tenant": tenant, "state": "incomplete"}
    try:
        records = collect(source, client)
        internships = []
        for record in records:
            role = classify_role(record["title"], record["text"], record.get("employment", ""))
            if role and role["internship_type"] == "internship":
                internships.append({"external_id": record["external_id"],
                                    "countries": record_countries(record) or ["sconosciuto"],
                                    "proof": "current-employer-feed"})
        row.update(state="feed-read", postings=len(records), internships=internships)
    except Exception as error:
        row["error"] = type(error).__name__
    return dict(row, logical_get=client.requests, body_bytes=client.bytes,
                seconds=round(time.monotonic() - start, 3))


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
            "hr_stage_feed_signals": len(jobs),
            "stage_signals_by_country": dict(Counter(code for job in jobs for code in job["countries"])),
            "logical_get": requests, "body_bytes": body_bytes, "source_seconds": round(seconds, 3),
            "cost_per_stage_feed_signal": ({"logical_get": requests / len(jobs),
                                           "body_bytes": body_bytes / len(jobs),
                                           "source_seconds": round(seconds / len(jobs), 3)}
                                          if jobs else "non dimostrato"),
        }
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    staging = Path(__file__).resolve().parents[1] / ".staging" / "ats-tenant-discovery"
    if staging.resolve() != staging:
        parser.error("Staging directory must not be a symlink")
    inventory = json.loads((staging / "inventory.json").read_text())
    # A review specifies an exact tenant/host scope and the public access basis.
    # Robots is still handled live by the existing client, including redirects.
    reviews_path = staging / "access-review.json"
    reviews = json.loads(reviews_path.read_text()) if reviews_path.exists() else []
    approved = {(row["ats"], row["tenant"]): row for row in reviews}
    rows = []
    counts = Counter()
    for provider, tenants in inventory["sample"].items():
        for tenant in tenants:
            key = (provider, tenant)
            review = approved.get(key, {})
            source = feed_source(*key)
            row = {"ats": provider, "tenant": tenant, "state": "access-not-demonstrated"}
            if (source and identity(review.get("observed_url")) == key
                    and set(review.get("hosts", [])) == set(source["allowed_hosts"])
                    and review.get("terms_basis") and review.get("terms_url", "").startswith("https://")
                    and review.get("approved_for_staging") is True):
                row["state"] = "ready"
                if args.live:
                    row = measure(*key, source)
            counts[row["state"]] += 1
            rows.append(row)
    result = {"states": counts, "summary": summarize(rows), "rows": rows}
    if args.live:
        temporary = staging / "yield.tmp"
        with temporary.open("x") as stream:
            json.dump(result, stream, indent=2)
            stream.write("\n")
        temporary.replace(staging / "yield.json")
    print(json.dumps(counts, sort_keys=True))


if __name__ == "__main__":
    main()
