"""Read-only daily policy-v2 opportunity gaps; never count leads as open jobs.

Uses the currently published catalog and latest source outcomes. One report
per ordinary collection, no new HTTP, browser, credentials or inference.
Ranks *causes to investigate* rather than claiming probabilities of openings.
"""
from collections import Counter, defaultdict
from datetime import datetime, timezone, timedelta
import json
from pathlib import Path
from urllib.parse import urlsplit

from collector.pipeline import ROOT, read, write
from collector.verification import verified_job

BLOCKED = ("robots", "http error 401", "http error 403", "http error 429",
           "captcha", "access challenge", "access denied", "rate-limited")
APPLICATION = ("no available vacancy-specific application entry established",
               "application link lacks a matching vacancy identifier",
               "applicant form not established", "applicant fields visible but submit disabled",
               "application page does not identify the same vacancy",
               "application requisition differs from vacancy")
MISMATCH = ("current page does not identify the same vacancy",
            "vacancy redirected to a different url")
QUARANTINE = "historical-unreviewed-external-host"


def _utc(value):
    if not value:
        return None
    try:
        stamp = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return stamp.astimezone(timezone.utc) if stamp.tzinfo else None
    except (ValueError, TypeError):
        return None


def reason_kind(job):
    reason = str((job.get("verification") or {}).get("reason") or "").lower()
    if (job.get("ownership_risk") or {}).get("state") == QUARANTINE or "historical external url" in reason:
        return "quarantined-ownership"
    if any(term in reason for term in BLOCKED):
        return "blocked-access"
    if any(term in reason for term in MISMATCH):
        return "vacancy-identity-mismatch"
    if any(term in reason for term in APPLICATION):
        return "application-proof-gap"
    return "other-unverified"


def analyze(catalog, sources, coverage, *, limit=25):
    """Deterministic snapshot, no wall-clock inference or internet access."""
    if (not isinstance(catalog, dict) or
            not isinstance(catalog.get("jobs"), list) or not _utc(catalog.get("updated_at"))):
        raise ValueError("Current timestamped catalog required")
    stamp = _utc(catalog["updated_at"])
    selected = {s["id"]: s for s in sources if s.get("enabled")}
    reports = {r["id"]:r for r in coverage.get("sources",[]) if r.get("id")}
    summary = Counter()
    countries_verified = Counter()
    country_leads = Counter()
    buckets = defaultdict(lambda: dict(counts=Counter(), active_ids=set(), countries=set(),
                                        examples=[], host_counts=Counter(), stale_reasons=0))
    current_job_count = 0

    for job in catalog["jobs"]:
        typ = job.get("internship_type")
        if typ not in ("internship", "working-student", "traineeship"):
            continue
        if job.get("status") == "closed":
            summary["closed_records"] += 1
            continue
        if verified_job(job, catalog["updated_at"]):
            summary["policy_v2_verified_"+typ] += 1
            for country in job.get("countries", [job.get("country")]):
                if country and typ == "internship":
                    countries_verified[country] += 1
            continue

        if job.get("status") != "unverified":
            summary["unexpected_nonverified_status"] += 1
            continue
        current_job_count += 1
        country = job.get("country")
        if country:
            country_leads[country] += 1
        sid = job.get("source_id")
        kind = reason_kind(job)
        summary[kind] += 1
        if sid not in selected or kind in ("quarantined-ownership", "blocked-access"):
            summary["not_auto_actionable"] += 1
            continue

        source = selected[sid]
        host = urlsplit(job.get("url", "")).hostname
        if host not in source.get("allowed_hosts", ()):
            summary["unapproved_source_host"] += 1
            continue
        bucket = buckets[sid]
        bucket["counts"][kind] += 1
        bucket["active_ids"].add(job["id"])
        if country:
            bucket["countries"].add(country)
        bucket["host_counts"][host] += 1
        evidence = _utc((job.get("verification") or {}).get("checked_at"))
        source_checked = _utc((reports.get(sid) or {}).get("checked_at"))
        # A stored reason from an earlier crawl is not a newly demonstrated
        # failure. Preserve it in the queue but don't call it live-confirmed.
        if evidence is None or evidence < stamp - timedelta(hours=48) or (
            source_checked and evidence < source_checked - timedelta(minutes=10)):
            bucket["stale_reasons"] += 1
        if len(bucket["examples"]) < 4:
            bucket["examples"].append(dict(id=job["id"], country=country, kind=kind,
                                           fresh_evidence=bool(evidence and
                                               evidence >= stamp-timedelta(hours=48) and
                                               (not source_checked or
                                                evidence >= source_checked-timedelta(minutes=10)))))

    rows = []
    for sid, bucket in buckets.items():
        counts = bucket["counts"]
        report = reports.get(sid, {})
        cost = report.get("requests")
        cost = cost if isinstance(cost, (int,float)) and cost >= 0 else None
        actionable = counts.get("application-proof-gap",0)
        # Relative triage score only, never probability or expected new jobs.
        score = 10*actionable + 3*counts.get("vacancy-identity-mismatch",0)
        score += counts.get("other-unverified",0)
        if cost is not None:
            score = round(score/(1+cost/20), 3)
        rows.append(dict(source_id=sid, employer=selected[sid].get("employer"),
                         current_unverified_distinct_ids=len(bucket["active_ids"]),
                         reasons=dict(counts),countries=sorted(bucket["countries"]),
                         observed_hosts=sorted(bucket["host_counts"]),
                         stored_reasons_not_fresh=bucket["stale_reasons"],
                         last_source_state=report.get("status"),
                         last_source_requests=cost,
                         last_source_bytes=report.get("bytes_read"),
                         last_source_checked_at=report.get("checked_at"),
                         score_heuristic_not_success_probability=score,
                         representative_ids=bucket["examples"],
                         recommended_next_step=(
                            "Review shared vacancy-to-application mapping on approved employer ATS; fresh same-ID/form proof required"
                            if actionable else
                            "Recheck exact vacancy identity/ownership before any promotion")))
    rows.sort(key=lambda r:(-r["score_heuristic_not_success_probability"],
                             -r["current_unverified_distinct_ids"],r["source_id"]))
    verified_countries = sorted(countries_verified)
    return dict(schema_version=1,
        mode="offline-bounded-policy-v2-blocker-priority",
        catalog_updated_at=catalog["updated_at"],
        sources_enabled=len(selected),
        total_catalog_records=len(catalog["jobs"]),
        unverified_records=current_job_count,
        status_counts=dict(summary),
        fresh_verified_hr_internships=summary.get("policy_v2_verified_internship",0),
        countries_with_verified_hr_internships=verified_countries,
        countries_without_verified_hr_internships=sorted(set(catalog.get("countries",{}))-set(verified_countries)),
        countries_with_unverified_leads=dict(sorted(country_leads.items())),
        ranked_source_count=len(rows),
        ranked_sources=rows[:limit],
        excluded_quarantined_or_blocked=summary["not_auto_actionable"],
        caveats=["Unverified IDs are not available internships; potential impact is NOT a forecast",
                 "Old errors may be retained without a new HTTP observation; fresh_evidence separates them",
                 "Robots/429/403 and unreviewed ownership are not retry recommendations",
                 "Ranking is offline only and does not change sources, budgets or applicant policy v2",
                 "No full EU27 geographic coverage is inferred from a configured employer count"])


def generate(output=ROOT/"docs/opportunity-quality-backlog.json"):
    report=analyze(
        read(ROOT/"data/catalog.json",{}),
        read(ROOT/"data/sources.json",[]),
        read(ROOT/"data/coverage.json",{}))
    write(Path(output),report)
    print("Opportunity bottlenecks:",report["fresh_verified_hr_internships"],
          "HR internships verified;",report["unverified_records"],
          "unverified records;",report["ranked_source_count"],"candidate source groups")
    return report


if __name__ == "__main__":
    generate()
