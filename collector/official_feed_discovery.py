"""Normalize one licensed JobTech posting for employer application review."""
from __future__ import annotations

from urllib.parse import urlsplit
import re

from .classify import canonical_url, classify_role, fold

JOBTECH_HOST = "jobsearch.api.jobtechdev.se"
JOBTECH_QUERIES = ("hr praktik", "personal praktik", "rekrytering praktik")


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
