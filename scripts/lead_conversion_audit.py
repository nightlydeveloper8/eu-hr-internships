"""Read-only conversion audit for HR internship leads, with no HTTP requests.

The script never upgrades evidence, calls employers, or edits published data.
Output files are explicitly requested and should be placed under .staging/.
"""
import argparse
import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
OWNERSHIP_HOLD = (
    "Historical external URL outside source reviewed employer hosts; "
    "official vacancy ownership not established"
)

REASONS = {
    "No available vacancy-specific application entry established": "missing-application-entry",
    "Application link lacks a matching vacancy identifier": "application-id-not-matched",
    "Current page does not identify the same vacancy": "vacancy-identity-mismatch",
    "Application page does not identify the same vacancy": "application-identity-mismatch",
    "Verification timestamp is future, invalid or older than 48 hours": "expired-verification",
    "robots.txt unavailable: 403": "robots-unavailable",
    "HTTP Error 429: Host rate-limited earlier in this collection process": "rate-limited",
    "Time budget exhausted; checkpoint retained": "time-budget-exhausted",
    "Request budget exhausted; checkpoint retained": "request-budget-exhausted",
    "Listed by the public API but published more than 180 days ago (or undated) without an application deadline":
        "public-listing-too-old-or-undated",
    "Applicant fields visible but submit disabled in initial HTML; availability unverified":
        "disabled-applicant-submit",
    "Applicant form not established; application may require JavaScript or an account":
        "dynamic-form-or-login-unconfirmed",
    "sequence item 4: expected str instance, NoneType found": "parsing-error",
    "Requires vacancy/application evidence under policy v2": "legacy-proof-ineligible",
    "Application redirected to a different URL; identity requires review": "redirect-identity-unconfirmed",
    "The read operation timed out": "read-timeout",
    "same-vacancy-applicant-form": "ownership-review-required",
    "official-vacancy-email-instructions": "ownership-review-required",
}


def hostname(url):
    try:
        return (urlsplit(url or "").hostname or "unknown").lower()
    except ValueError:
        return "unknown"


def family(job, source=None):
    """ATS is named only when a reviewed source or exact provider host supports it."""
    host = hostname(job.get("url"))
    adapter = job.get("source_type") or "unknown"
    if adapter == "eures-search":
        return "EURES"
    if adapter == "amazon-search":
        return "Amazon.jobs"
    if adapter == "recruitee" or host.endswith(".recruitee.com"):
        return "Recruitee"
    if adapter == "personio-xml" or host.endswith(".jobs.personio.de"):
        return "Personio"
    if host == "jobs.smartrecruiters.com":
        return "SmartRecruiters"
    if host.endswith(".myworkdayjobs.com"):
        return "Workday"
    basis = (source or {}).get("permission_basis") or ""
    if "radancy" in basis.lower():
        return "Radancy (source reviewed)"
    return adapter + " (ATS unconfirmed)"


def reason_category(job):
    reason = (job.get("verification") or {}).get("reason") or ""
    if reason in REASONS:
        return REASONS[reason]
    if reason.startswith("robots.txt disallows "):
        return "robots-disallowed"
    if job.get("link_status") == "review-required":
        return "ownership-review-required"
    return "other-unclassified"


def _recent(job, clock):
    try:
        at = datetime.fromisoformat(job["last_verified_at"].replace("Z", "+00:00"))
        if at.tzinfo is None:
            at = at.replace(tzinfo=timezone.utc)
        age = (clock - at).total_seconds()
        proof = job.get("verification") or {}
        return (0 <= age <= 48 * 3600 and proof.get("state") == "verified"
                and proof.get("policy_version") == 2)
    except (KeyError, TypeError, ValueError, AttributeError):
        return False


def analyze(catalog, sources, coverage):
    jobs = catalog.get("jobs") or []
    now = datetime.fromisoformat(catalog["updated_at"].replace("Z", "+00:00"))
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    sources_by_id = {s["id"]: s for s in sources}
    reports_by_id = {s["id"]: s for s in coverage.get("sources", [])}
    archived_ids = [j.get("id") for j in jobs]
    ownership_holds = [
        j for j in jobs
        if j.get("internship_type") == "internship" and j.get("status") == "unverified"
        and (j.get("verification") or {}).get("reason") == OWNERSHIP_HOLD
    ]
    leads = [
        j for j in jobs
        if j.get("internship_type") == "internship" and j.get("status") == "unverified"
        and (j.get("verification") or {}).get("reason") != OWNERSHIP_HOLD
    ]
    opened = [j for j in jobs if j.get("internship_type") == "internship"
              and j.get("status") == "open" and _recent(j, now)]
    direct = [j for j in opened if j.get("link_status") == "verified"
              and bool(j.get("application_verification"))]
    public = [j for j in opened if j.get("link_status") == "public-api-active-listing"]
    by_cell, by_country, by_family, by_reason, by_host, by_source = (
        Counter(), Counter(), Counter(), Counter(), Counter(), Counter()
    )
    raw_reasons = Counter()
    for job in leads:
        country = job.get("country") or "unknown"
        ats = family(job, sources_by_id.get(job.get("source_id")))
        reason = reason_category(job)
        by_cell[country, ats, reason] += 1
        by_country[country] += 1
        by_family[ats] += 1
        by_reason[reason] += 1
        by_host[hostname(job.get("url"))] += 1
        by_source[job.get("source_id") or "unknown"] += 1
        raw_reasons[(job.get("verification") or {}).get("reason") or "missing"] += 1

    matrix = [
        dict(country=country, ats_family=ats, reason=reason, count=count)
        for (country, ats, reason), count in sorted(by_cell.items())
    ]
    costs = []
    for sid, count in by_source.most_common():
        run = reports_by_id.get(sid, {})
        req = run.get("requests")
        bytes_read = run.get("bytes_read")
        seconds = run.get("duration_seconds")
        costs.append(dict(
            source_id=sid, leads=count, adapter=run.get("adapter"),
            checked_at=run.get("checked_at"), last_run_status=run.get("status"),
            source_run_get_requests=req, source_run_bytes=bytes_read,
            source_run_seconds=seconds,
            source_run_requests_per_lead=round(req / count, 2) if isinstance(req, (int, float)) else None,
        ))
    return dict(
        snapshot_at=catalog["updated_at"], snapshot_status=catalog.get("update_status"),
        totals=dict(
            catalog_jobs=len(jobs), distinct_ids=len(set(archived_ids)),
            duplicate_ids=len(jobs) - len(set(archived_ids)),
            current_verified_internships=len(opened),
            direct_applications_verified=len(direct),
            public_service_current=len(public),
            actionable_leads=len(leads), legacy_ownership_holds=len(ownership_holds),
            remaining_archived=len(jobs)-len(opened)-len(leads)-len(ownership_holds),
        ),
        by_country=dict(sorted(by_country.items())),
        by_family=dict(by_family.most_common()),
        by_reason=dict(by_reason.most_common()),
        by_host=dict(by_host.most_common()),
        raw_reasons=dict(raw_reasons.most_common()),
        reason_country_family=matrix,
        source_run_costs=costs,
        methodology=dict(
            offline_get_requests=0, offline_employer_bytes=0,
            caveat="A source-run cost includes all jobs, not only these leads. "
                   "It is not the marginal HTTP cost of converting one lead.",
            verified_rule="Snapshot at catalog updated_at: open internship, policy v2 verified <=48h; "
                          "direct additionally requires same-vacancy application_verification.",
            exclusion="93 historical external URLs with ownership unestablished are separately held; "
                      "do not upgrade or silently discard them.",
        ),
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=ROOT / "data/catalog.json")
    parser.add_argument("--sources", type=Path, default=ROOT / "data/sources.json")
    parser.add_argument("--coverage", type=Path, default=ROOT / "data/coverage.json")
    parser.add_argument("--json", type=Path, help="write complete JSON to an ignored .staging/ file")
    parser.add_argument("--csv", type=Path, help="write reason x country x ATS matrix to CSV")
    args = parser.parse_args(argv)
    report = analyze(
        json.loads(args.catalog.read_text(encoding="utf-8")),
        json.loads(args.sources.read_text(encoding="utf-8")),
        json.loads(args.coverage.read_text(encoding="utf-8")),
    )
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.csv:
        args.csv.parent.mkdir(parents=True, exist_ok=True)
        with args.csv.open("w", newline="", encoding="utf-8") as out:
            writer = csv.DictWriter(out, fieldnames=["country", "ats_family", "reason", "count"])
            writer.writeheader()
            writer.writerows(report["reason_country_family"])
    print(json.dumps({
        "snapshot_at": report["snapshot_at"],
        "totals": report["totals"],
        "by_country": report["by_country"],
        "by_family": report["by_family"],
        "by_reason": report["by_reason"],
        "top_source_costs": report["source_run_costs"][:10],
        "matrix_rows": len(report["reason_country_family"]),
    }, indent=2, ensure_ascii=False))
    return report


if __name__ == "__main__":
    main()
