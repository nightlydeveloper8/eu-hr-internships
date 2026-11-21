"""Deterministic, offline shortlist of official-ATS conversion candidates.

Consumes the existing catalog only. No GET, API, rendering or status promotion.
The shape of a destination URL is a research hint, not ownership/form evidence.
"""
from collections import Counter
import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

from collector.pipeline import ROOT
from collector.verification import verified_job

DEFAULT_COUNTRIES = ("PL", "IE", "CZ", "SE")


def safe_https(value):
    if not isinstance(value, str):
        return None
    try:
        p = urlsplit(value)
        if p.scheme != "https" or not p.hostname or p.username or p.password:
            return None
        if p.port and p.port != 443:
            return None
        return value
    except ValueError:
        return None


def ats_hint(url):
    """Identify only IDs *already present* in a public URL. No inferred links."""
    url = safe_https(url)
    if not url:
        return ("invalid-or-unknown", None)
    p = urlsplit(url)
    host = p.hostname.lower()
    path = p.path
    if host == "jobs.smartrecruiters.com":
        m = re.match(r"^/[^/]+/(\d{15})(?:$|[-/])", path)
        if m:
            return ("smartrecruiters", m.group(1))
    if host.endswith(".varbi.com"):
        m = re.search(r"/jobID:(\d+)(?:/|$)", path, re.I)
        if m:
            return ("varbi", m.group(1))
    if host == "jobs.ashbyhq.com":
        m = re.fullmatch(r"/[^/]+/([0-9a-fA-F-]{36})/?", path)
        if m:
            return ("ashby", m.group(1))
    if re.search(r"\.myworkdayjobs\.com$", host):
        m = re.search(r"_((?:JR|REQ)[-_]?[A-Za-z0-9]+)(?:/|$)", path, re.I)
        if m:
            return ("workday", m.group(1))
    m = re.fullmatch(r"/jobs/(\d+)(?:-[^/]+)?/applications/new/?", path)
    if m:
        return ("ats-same-id-path-review-required", m.group(1))
    if host in ("amazon.jobs", "www.amazon.jobs"):
        m = re.match(r"^/(?:[a-z]{2}/)?jobs/(\d+)(?:/|$)", path)
        if m:
            return ("amazon-jobs", m.group(1))
    if host.endswith(".careers-page.com"):
        m = re.fullmatch(r"/jobs/([0-9a-fA-F-]{36})/?", path)
        if m:
            return ("careers-page", m.group(1))
    return ("unclassified", None)


def build_report(catalog, countries=DEFAULT_COUNTRIES, per_country=20):
    """Never label catalog leads as fresh policy-v2 employer applications."""
    if not isinstance(catalog, dict) or not isinstance(catalog.get("jobs"), list):
        raise ValueError("A catalog with jobs[] is required")
    if not isinstance(per_country, int) or not 1 <= per_country <= 100:
        raise ValueError("Per-country limit outside offline shortlist bounds")
    stamp = catalog.get("updated_at") or catalog.get("last_attempt_at") or ""
    selected = []
    for country in countries:
        if not re.fullmatch(r"[A-Z]{2}", str(country)):
            raise ValueError("Country must be an ISO-like two-letter code")
        rows = [row for row in catalog["jobs"]
                if isinstance(row, dict) and row.get("status") != "closed"
                and not row.get("ownership_risk")
                and country in (row.get("countries") or [row.get("country")])]
        verified = sum(bool(row.get("application_verification", {}).get("url"))
                       and row.get("internship_type") == "internship"
                       and verified_job(row, stamp) for row in rows)
        leads = {}
        for job in rows:
            if bool(job.get("application_verification", {}).get("url")) and verified_job(job, stamp):
                continue
            url = safe_https(job.get("external_application_url")) or safe_https(job.get("url"))
            if not url:
                continue
            provider, ats_id = ats_hint(url)
            # An explicit external application URL is a prioritisation signal,
            # never a claim of current employer ownership or an enabled form.
            public = job.get("source_type") in ("jobtech-search", "eures-search")
            score = int(ats_id is not None) * 2 + int(bool(safe_https(job.get("external_application_url"))))
            score += int(not public)
            record = dict(country=country, employer=job.get("employer"), title=job.get("title"),
                          url=url, catalog_id=job.get("id"), source_id=job.get("source_id"),
                          public_source=bool(public), ats_family_hint=provider,
                          observed_posting_id=ats_id, score=score,
                          state="research-only-not-a-verified-application")
            if url not in leads or (score, str(record["catalog_id"])) > (
                    leads[url]["score"], str(leads[url]["catalog_id"])):
                leads[url] = record
        ranked = sorted(leads.values(), key=lambda r: (-r["score"], str(r["employer"]), str(r["catalog_id"])))
        selected.append(dict(country=country, known_open_or_unverified=len(rows),
                             policy_v2_direct_verified=verified,
                             research_candidates=len(ranked),
                             candidates_shown=ranked[:per_country],
                             ats_hints=dict(Counter(r["ats_family_hint"] for r in ranked))))
    return dict(catalog_updated_at=stamp, scope="offline-replay-existing-catalog-only",
                policy="No candidate is promoted without current official employer inventory, same-vacancy application form, ownership and 48h freshness",
                requests=0, bytes_read=0, renderings=0,
                countries=selected)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", type=Path, default=ROOT / "data/catalog.json")
    parser.add_argument("--countries", nargs="+", default=list(DEFAULT_COUNTRIES))
    parser.add_argument("--per-country", type=int, default=20)
    args = parser.parse_args()
    data = json.loads(args.catalog.read_text(encoding="utf-8"))
    print(json.dumps(build_report(data, args.countries, args.per_country),
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
