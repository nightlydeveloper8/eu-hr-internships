"""Isolated and bounded Recruitee employer-internal ATS verification pilot.

SmartWays runs two distinct Recruitee boards. The earlier jobs.smartways.io
board contains predominantly client vacancies; the company's own recruiting
internship is advertised on smartways.recruitee.com. Never combine tenants.
This preview uses the ordinary collector and policy-v2 verifier, never writes
to the repository's production catalog, and never submits an application.
"""
from copy import deepcopy
import json
import re
from pathlib import Path
from tempfile import TemporaryDirectory
from time import monotonic
from urllib.parse import urljoin, urlsplit

from collector.classify import canonical_url
from collector.pipeline import ROOT, finalize, now, process_source, read
from collector.runtime import BudgetClient
from collector.universal import Document
from collector.verification import verified_job

HOST = "smartways.recruitee.com"
REVIEWED_CAREERS_HOST = "careers.smartways.io"
BASE = "https://" + HOST
LEGAL_URL = BASE + "/privacy-policy"
LEGAL_TAX_ID = "6793137813"
SOURCE = dict(
    id="pilot-smartways-internal-pl",
    employer="SmartWays", adapter="recruitee", enabled=False,
    staging_only=True, rollout_approved=False,
    application_check="recruitee-linked",
    reviewed_recruitee_alias="smartways-internal",
    feed_url=BASE + "/api/offers/", career_url=BASE + "/",
    allowed_hosts=[HOST, REVIEWED_CAREERS_HOST], target_countries=["PL"],
    ownership_scope="reviewed-hosts", require_employer_identity=True,
    report_feed_scope=True,
    max_requests=14, collection_seconds=75,
    discovery_scope="One employer-internal Recruitee board; never infer closures from absent offers",
    permission_basis="Official SmartWays internal Careers Site and exact Recruitee tenant; current same-ID form required",
)


def reviewed_source(source):
    required = ("id", "employer", "adapter", "application_check", "feed_url",
                "career_url", "target_countries", "ownership_scope",
                "require_employer_identity", "report_feed_scope",
                "reviewed_recruitee_alias", "staging_only", "rollout_approved")
    if (not isinstance(source, dict) or
            any(source.get(k) != SOURCE[k] for k in required) or
            source.get("enabled") is not False or
            source.get("allowed_hosts") != [HOST, REVIEWED_CAREERS_HOST] or
            type(source.get("max_requests")) is not int or
            not 8 <= source["max_requests"] <= SOURCE["max_requests"] or
            type(source.get("collection_seconds")) is not int or
            not 30 <= source["collection_seconds"] <= SOURCE["collection_seconds"]):
        raise ValueError("Unreviewed tenant, identity, activation or request budget")
    return True


def allowed(url):
    try:
        parsed = urlsplit(canonical_url(url))
    except (ValueError, TypeError):
        return False
    if parsed.query:
        return False
    if parsed.hostname == HOST:
        return (parsed.path in ("", "/", "/robots.txt", "/privacy-policy", "/api/offers")
                or bool(re.fullmatch(r"/o/[a-zA-Z0-9%_-]+(?:/c/new)?", parsed.path)))
    if parsed.hostname == REVIEWED_CAREERS_HOST:
        # Distinct published alias on the *same* employer-internal feed.
        # Never accept jobs.smartways.io (third-party client vacancies).
        return parsed.path == "/robots.txt" or bool(
            re.fullmatch(r"/o/[a-zA-Z0-9%_-]+(?:/c/new)?", parsed.path))
    return False


class ReadOnlyClient(BudgetClient):
    def __init__(self, source):
        reviewed_source(source)
        super().__init__(seconds=source["collection_seconds"],
                         max_requests=source["max_requests"], delay=0.7)
        self.redirect_scope_allowed = allowed

    def request(self, url, method="GET", **kwargs):
        if method != "GET" or not allowed(url):
            raise ValueError("Internal Recruitee pilot is read-only and tenant-scoped")
        return super().request(url, method=method, **kwargs)


def employer_board(homepage, final):
    """Current internal tenant must identify the employer before further reads."""
    if canonical_url(final) != canonical_url(BASE):
        raise ValueError("Internal Recruitee homepage redirected")
    document = Document(homepage, final)
    if "smartways" not in document.text.casefold():
        raise ValueError("Current tenant does not name SmartWays")
    return True


def employer_legal_identity(html, final):
    """Independent same-host legal page, with NIP from the corporate site.

    The previous employer-website link test failed on the live careers HTML.
    A verified legal name plus the company's publicly stated tax identifier
    is stronger ownership evidence; do not infer it from a job title.
    """
    if canonical_url(final) != canonical_url(LEGAL_URL):
        raise ValueError("SmartWays legal notice redirected")
    value = Document(html, final).text.casefold()
    if not ("smartways" in value and LEGAL_TAX_ID in value and
            ("spółka" in value or "spolka" in value or "sp. z o.o" in value)):
        raise ValueError("Legal notice does not establish the reviewed SmartWays identity")
    return True


def direct(rows, stamp):
    return sum(
        verified_job(job, stamp) and job.get("internship_type") == "internship"
        and bool((job.get("application_verification") or {}).get("url"))
        for job in rows
    )


def preview():
    registry = read(ROOT / "data/sources.json", [])
    candidates = [entry for entry in registry if entry.get("id") == SOURCE["id"]]
    if len(candidates) != 1:
        raise ValueError("Expected exactly one disabled, reviewed SmartWays source")
    source = deepcopy(candidates[0])
    reviewed_source(source)
    if source.get("enabled") is not False:
        raise ValueError("SmartWays preview may only read a disabled source")
    catalog = read(ROOT / "data/catalog.json", {})
    stamp = now()
    client = ReadOnlyClient(source)
    started = monotonic()
    result = dict(source_id=source["id"], checked_at=stamp,
                  source_enabled=False, catalog_modified=False,
                  applications_submitted=0, verified_new_in_production=0)
    part = None
    try:
        homepage, _, final = client.request(BASE + "/")
        employer_board(homepage, final)
        legal, _, legal_final = client.request(LEGAL_URL)
        employer_legal_identity(legal, legal_final)
        part = process_source(source, client, stamp)
        if part["closure_eligible"]:
            raise ValueError("Partial Recruitee sample cannot close records")
        before = {job["id"] for job in catalog["jobs"]}
        with TemporaryDirectory(prefix="people-placement-smartways-") as temp:
            staged, _ = finalize([*registry, source], [source],
                                 catalog, {}, [part], stamp, Path(temp))
            repeated, _ = finalize([*registry, source], [source],
                                   deepcopy(staged), {}, [part], stamp, Path(temp))
        after = {job["id"] for job in staged["jobs"]}
        if (not before <= after or len(after) != len(staged["jobs"])
                or after != {job["id"] for job in repeated["jobs"]}):
            raise ValueError("Unstable catalog identity or removed prior job")
        verified = [
            dict(id=job["id"], posting_id=job["external_id"],
                 employer=job["employer"], title=job["title"],
                 city=job["city"], country=job["country"],
                 vacancy=job["url"],
                 application=job["application_verification"]["url"])
            for job in staged["jobs"]
            if job.get("source_id") == source["id"]
            and job.get("country") == "PL"
            and job.get("internship_type") == "internship"
            and verified_job(job, stamp)
            and (job.get("application_verification") or {}).get("method")
            == "official-recruitee-same-posting-visible-form"
        ]
        result.update(
            state="staging" if verified else "no-verified-internship",
            verified=verified,
            ids_before=len(before), ids_after=len(after),
            direct_before=direct(catalog["jobs"], stamp),
            direct_after=direct(staged["jobs"], stamp),
            report=part["report"],
            idempotent=True,
        )
    except Exception as exc:
        result.update(state="incomplete", reason=str(exc)[:240],
                      report=part["report"] if part else None)
    finally:
        result.update(requests=client.requests, bytes_read=client.bytes,
                      browser_renderings=0,
                      duration_seconds=round(monotonic()-started, 3))
    return result


if __name__ == "__main__":
    print(json.dumps(preview(), ensure_ascii=False))
