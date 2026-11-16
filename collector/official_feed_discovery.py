"""Bounded discovery of HR placements from public, reusable structured vacancy feeds.

Discovery output is a review queue, NOT a public catalog and NOT a verified
application. JobTech SE offers a documented CC0 public API. EURES input can
only be supplied from a separately authorised channel; this module NEVER
contacts the EURES portal or its restricted API.

No browser, API credentials, application submissions, or employer-host fetches.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from urllib.parse import urlsplit
import re

from .classify import COUNTRIES, canonical_url, classify_role, fold

JOBTECH_SEARCH = "https://jobsearch.api.jobtechdev.se/search"
JOBTECH_HOST = "jobsearch.api.jobtechdev.se"
JOBTECH_QUERIES = ("hr praktik", "personal praktik", "rekrytering praktik")
MAX_RESULTS = 120
MAX_QUERIES = 3
MAX_PER_QUERY = 40
EURES_PREFIX = "https://europa.eu/eures/portal/jv-se/jv-details/"


def https_url(value, allowed_hosts=None):
    """Reject credentials, non-HTTPS, nonstandard ports and ambiguous URLs."""
    if not isinstance(value, str) or not value or value.strip() != value:
        return None
    if any(ord(c) < 32 or c == "\\" for c in value):
        return None
    try:
        parsed = urlsplit(value)
        host = parsed.hostname
        if (parsed.scheme != "https" or not host or parsed.username or parsed.password
                or parsed.port is not None or not re.fullmatch(r"[a-z0-9.-]+", host.lower())):
            return None
        if allowed_hosts is not None and host.lower() not in allowed_hosts:
            return None
        return canonical_url(value)
    except (ValueError, TypeError):
        return None


def _title_and_kind(title, description):
    # HR must be present in the title according to the project's conservative
    # classifier. Employment-like role keywords in the description alone are
    # never sufficient to publish an HR internship.
    result = classify_role(title, description)
    if result is None or result["internship_type"] != "internship":
        return None
    return result


def _text(value):
    if isinstance(value, str):
        return " ".join(value.split())[:4000]
    return ""


def jobtech_candidate(record):
    """Normalize one JobSearch hit; never invent an employer or apply link."""
    if not isinstance(record, dict):
        return None
    id_ = str(record.get("id", ""))
    if not re.fullmatch(r"[0-9]{1,24}", id_):
        return None
    title = _text(record.get("headline"))
    description = record.get("description") or {}
    description = _text(description.get("text", "")) if isinstance(description, dict) else ""
    role = _title_and_kind(title, description)
    if role is None:
        return None
    employer = record.get("employer") or {}
    employer_name = _text(employer.get("name", "")) if isinstance(employer, dict) else ""
    if not employer_name:
        return None
    address = record.get("workplace_address") or {}
    address = address if isinstance(address, dict) else {}
    country = _text(address.get("country", ""))
    if country and fold(country) not in ("sverige", "sweden", "se"):
        return None
    # JobTech itself supplies the vacancy's public URL; no guessed link.
    url = https_url(record.get("webpage_url"))
    if not url:
        return None
    application = record.get("application_details") or {}
    application = application if isinstance(application, dict) else {}
    apply_url = https_url(application.get("url"))
    # Application URLs from public job boards are leads only; they are NOT
    # evidence that the exact employer's form can currently be submitted.
    return dict(provider="jobtech-se", provider_id=id_, employer=employer_name,
        title=title, country="SE", workplace_country_evidence=bool(country),
        city=_text(address.get("municipality", "")) or _text(address.get("city", "")),
        url=url, apply_url=apply_url, categories=role["categories"],
        internship_type="internship", published_at=record.get("publication_date"),
        review_status="employer-identity-and-application-unverified",
        verification_state="unverified", verified_vacancies_added=0)


def eures_candidate(record):
    """Normalize explicitly supplied, legitimately acquired EURES metadata.

    This is an input contract for an authorised upstream, *not* an EURES API
    client or a licence determination. No network and no full-text storage.
    """
    if not isinstance(record, dict):
        return None
    id_ = str(record.get("id", "")).strip()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{2,99}", id_):
        return None
    url = https_url(record.get("url"), {"europa.eu"})
    if not url or not url.startswith(EURES_PREFIX):
        return None
    title = _text(record.get("title"))
    role = _title_and_kind(title, _text(record.get("description", "")))
    if not role:
        return None
    employer = _text(record.get("employer"))
    country = str(record.get("country", "")).upper()
    if not employer or country not in COUNTRIES:
        return None
    # EURES job-search IDs and links are discovery evidence, not a
    # demonstration of employer provenance or an accessible application.
    return dict(provider="eures-authorized-input", provider_id=id_,
        employer=employer, title=title, country=country,
        workplace_country_evidence=False, city=_text(record.get("city")),
        url=url, apply_url=None, categories=role["categories"],
        internship_type="internship", published_at=record.get("published_at"),
        review_status="employer-identity-and-application-unverified",
        verification_state="unverified", verified_vacancies_added=0)


def normalize(records, provider, limit=MAX_RESULTS, existing_urls=()):
    if not 1 <= limit <= MAX_RESULTS:
        raise ValueError("Candidate limit must be in 1..120")
    if provider not in ("jobtech-se", "eures-authorized-input"):
        raise ValueError("Unknown structured source")
    if not isinstance(records, list):
        raise ValueError("Feed records must be an array")
    if len(records) > limit:
        raise ValueError("Input exceeds explicitly bounded record count")
    parser = jobtech_candidate if provider == "jobtech-se" else eures_candidate
    previously = {canonical_url(u) for u in existing_urls if https_url(u)}
    seen_ids, seen_urls = set(), set()
    candidates = []
    rejected = Counter()
    for item in records:
        row = parser(item)
        if row is None:
            rejected["not-eligible-or-incomplete"] += 1
            continue
        key = (row["provider"], row["provider_id"])
        if key in seen_ids or row["url"] in seen_urls:
            rejected["duplicate-in-input"] += 1
            continue
        seen_ids.add(key)
        seen_urls.add(row["url"])
        if row["url"] in previously:
            rejected["already-in-catalog"] += 1
            continue
        candidates.append(row)
    return dict(schema_version=1, mode="discovery-only",
        provider=provider, input_records=len(records), candidate_count=len(candidates),
        rejected=dict(rejected), candidates=candidates, verified_vacancies_added=0,
        employer_hosts_probed=0, applications_submitted=0,
        limits=["No claim of an open, verified HR internship",
                "Original employer ownership and application form require separate live policy-v2 review",
                "EURES data cannot be acquired by this module; use authorised upstream only"])


def jobtech_search(client, queries=JOBTECH_QUERIES, per_query=20):
    """Small, explicit live pilot via robots-aware BudgetClient; no pagination."""
    from urllib.parse import urlencode
    if (not isinstance(queries, (tuple, list)) or not queries
            or len(queries) > MAX_QUERIES
            or not 1 <= per_query <= MAX_PER_QUERY
            or any(not isinstance(q, str) or not 2 <= len(q) <= 60 for q in queries)):
        raise ValueError("Live JobTech pilot query budget invalid")
    all_rows = []
    for query in queries:
        params = urlencode({"q": query, "limit": per_query, "offset": 0})
        url = JOBTECH_SEARCH + "?" + params
        data = client.json(url)  # BudgetClient enforces robots, throttling and timeout.
        if not isinstance(data, dict) or not isinstance(data.get("hits"), list):
            raise ValueError("Malformed JobTech JSON search results")
        hits = data["hits"]
        if len(hits) > per_query:
            raise ValueError("JobTech feed returned more than the requested cap")
        all_rows.extend(hits)
    if len(all_rows) > MAX_RESULTS:
        raise ValueError("Source search exceeded hard cap")
    return all_rows


def discovery_report(client, catalog_urls=(), queries=JOBTECH_QUERIES, per_query=20):
    rows = jobtech_search(client, queries, per_query)
    report = normalize(rows, "jobtech-se", limit=MAX_RESULTS, existing_urls=catalog_urls)
    report.update(requests=client.requests, bytes_read=client.bytes,
        requested_queries=list(queries), checked_at=datetime.now(timezone.utc).isoformat(),
        rendering_count=0, collector_registry_modified=False)
    return report
