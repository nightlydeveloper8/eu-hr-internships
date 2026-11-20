"""Rank collection work from saved coverage, catalog and source snapshots."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timedelta
import json
from pathlib import Path

from collector.ats_channel_discovery import safe_url
from collector.classify import COUNTRIES, NON_EU, fold, plain
from collector.public_sources import PUBLIC_API_ADAPTERS
from collector.universal import PROVIDERS
from collector.verification import verified_job


def recent(value, clock):
    if not value:
        return False
    try:
        age = clock - datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return False
    return timedelta(0) <= age <= timedelta(hours=48)


def application_gap(reason):
    if "historical external url" in reason or "ownership" in reason:
        return "ownership"
    if "matching vacancy identifier" in reason or "identify the same vacancy" in reason:
        return "vacancy-identity"
    if "budget exhausted" in reason or "time budget" in reason:
        return "budget"
    if "application entry" in reason or "applicant form" in reason or "submit disabled" in reason:
        return "application-form"
    return "needs-review"


def provider_signals(source, observation):
    hosts = set(source.get("allowed_hosts", [])) | set(observation.get("allowed_hosts", []))
    for key in ("career_url", "feed_url", "sitemap_url"):
        url = safe_url(source.get(key))
        if url:
            hosts.add(url.hostname)
    return {provider for provider in PROVIDERS
            if any(host == provider or host.endswith("." + provider) for host in hosts)}


def portfolio(catalog, coverage, registry):
    """Return a decision report. All candidate IDs remain unverified leads."""
    stamp = coverage["generated_at"]
    clock = datetime.fromisoformat(stamp)
    enabled = {s["id"]: s for s in registry if s.get("enabled")}
    attempts = {r["id"]: r for r in coverage["sources"]
                if r["id"] in enabled and recent(r.get("checked_at"), clock)}
    countries = {country: dict(direct=0, public_listings=0, public_leads_with_external_url=0)
                 for country in COUNTRIES | NON_EU}
    adapters = defaultdict(Counter)
    providers = defaultdict(Counter)
    for source in registry:
        adapters[source["adapter"]]["configured"] += 1
        adapters[source["adapter"]]["enabled"] += int(bool(source.get("enabled")))

    for source_id, row in attempts.items():
        source = enabled[source_id]
        group = adapters[row["adapter"]]
        requests = row.get("requests")
        known_cost = isinstance(requests, int) and requests >= 0
        matching = row.get("matching")
        group["recent_attempts"] += 1
        group["reported_request_attempts"] += requests if known_cost else 0
        group["requests_unknown_sources"] += int(not known_cost)
        group["requests_with_explicit_zero_matches"] += requests if known_cost and matching == 0 else 0
        group["complete_inventories"] += int(row.get("status") == "ok" and row.get("complete") is True)
        group["reported_matches"] += matching or 0
        for provider in provider_signals(source, row):
            providers[provider]["sources_with_recent_measurements"] += 1
            providers[provider]["complete_inventories"] += int(row.get("status") == "ok" and row.get("complete") is True)
            providers[provider]["sources_with_matches"] += int(bool(matching))
            providers[provider]["registered_typed_sources"] += int(
                source["adapter"] not in ("universal-employer", "employer-sitemap", "employer-index"))

    groups = defaultdict(list)
    public_by_employer = defaultdict(list)
    seen_ids = set()
    for job in catalog["jobs"]:
        if job["id"] in seen_ids or job.get("internship_type") != "internship":
            continue
        seen_ids.add(job["id"])
        country = job.get("country")
        if country not in countries:
            continue
        country_counts = countries[country]
        proof = job.get("verification", {})
        source_id = job.get("source_id")
        is_public = proof.get("policy") == "public-api-active-listing"
        if verified_job(job, stamp):
            if job.get("application_verification") and not is_public:
                country_counts["direct"] += 1
                adapters[job["source_type"]]["direct_catalog_internships"] += 1
            elif is_public:
                country_counts["public_listings"] += 1
                country_counts["public_leads_with_external_url"] += int(
                    bool(safe_url(job.get("external_application_url"))))
                employer = fold(plain(job.get("employer")))
                if employer:
                    public_by_employer[country, employer].append(job)
        if (proof.get("state") not in ("incomplete", "blocked") or job.get("status") != "unverified"
                or not recent(job.get("last_seen_at"), clock) or source_id not in attempts
                or is_public or not recent(proof.get("checked_at"), clock)):
            continue
        source = enabled[source_id]
        if source["adapter"] in PUBLIC_API_ADAPTERS or job.get("ownership_risk"):
            continue
        url = safe_url(job.get("url"))
        if not url or url.hostname not in source.get("allowed_hosts", []):
            continue
        gap = "access-blocked" if proof["state"] == "blocked" else application_gap(str(proof.get("reason", "")).lower())
        groups[source_id, gap].append(job)

    queue = []
    for (source_id, gap), jobs in groups.items():
        row = attempts[source_id]
        country_counts = Counter(job["country"] for job in jobs)
        queue.append(dict(source_id=source_id, employer=enabled[source_id].get("employer"),
                          observed_adapter=row["adapter"], gap=gap,
                          candidates=len(jobs), countries=dict(sorted(country_counts.items())),
                          previous_snapshot_requests=row.get("requests"),
                          observed_application_routes=row.get("application_route_hints", []),
                          sample_ids=sorted(job["id"] for job in jobs)[:3]))
    queue.sort(key=lambda r: (-r["candidates"], r["source_id"], r["gap"]))

    public_clusters = [
        dict(country=country, employer=jobs[0]["employer"], listings=len(jobs),
             with_external_url=sum(bool(safe_url(job.get("external_application_url"))) for job in jobs),
             listing_sources=sorted({job["source_id"] for job in jobs}))
        for (country, _), jobs in public_by_employer.items()
    ]
    public_clusters.sort(key=lambda row: (row["country"], -row["listings"], row["employer"]))

    zero = sorted((row for row in attempts.values() if row.get("matching") == 0
                   and isinstance(row.get("requests"), int) and row["requests"] > 0),
                  key=lambda row: (-row["requests"], row["id"]))
    return dict(snapshot_at=stamp, enabled_sources=len(enabled), recent_coverage=len(attempts),
                countries=countries, adapters=dict(sorted(adapters.items())),
                provider_signals=dict(sorted(providers.items())),
                application_review=queue, public_employer_clusters=public_clusters,
                highest_request_zero_match_sources=[
                    {key: row.get(key) for key in ("id", "employer", "adapter", "status",
                                                   "requests", "bytes_read", "pending_urls", "complete")}
                    for row in zero[:20]])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path(__file__).resolve().parents[1] / "data")
    args = parser.parse_args()

    def load_snapshot(name):
        return json.loads((args.data_dir / (name + ".json")).read_text(encoding="utf-8"))

    print(json.dumps(portfolio(load_snapshot("catalog"), load_snapshot("coverage"),
                               load_snapshot("sources")), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
