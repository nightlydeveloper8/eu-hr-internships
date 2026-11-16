"""Bounded follow-up: public-feed candidate -> exact named application page.

This verifier only reads application URLs already observed in a licensed feed,
and only on explicitly approved hosts. It deliberately does not promote
records into the policy-v2 catalog or claim employer ownership from a feed
referral. It reuses the existing conservative HTML vacancy/applicant verifier.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from urllib.parse import urlsplit
import time

from .official_feed_discovery import https_url
from .runtime import BudgetClient
from .verification import _verify_vacancy, applicant_form, blocked_error
from .ownership import employer_matches
from .universal import Document
from .classify import fold, plain, canonical_url


class CapturedClient:
    """Capture only in-memory bytes needed for strict form/identity checks."""
    def __init__(self, client):
        self.client = client
        self.pages = {}

    def request(self, url, *args, **kwargs):
        body, status, final = self.client.request(url, *args, **kwargs)
        self.pages[canonical_url(final)] = body
        return body, status, final

    def __getattr__(self, key):
        return getattr(self.client, key)


def _identity_matches(body, url, employer, title):
    doc = Document(body, url)
    matching_posts = [post for post in doc.jobposts()
                      if fold(plain(post.get("title"))) == fold(title)]
    if not matching_posts:
        return False
    source = {"employer": employer, "employer_aliases": []}
    for post in matching_posts:
        org = post.get("hiringOrganization")
        name = org.get("name") if isinstance(org, dict) else org
        if name and employer_matches(plain(name), source, url):
            return True
    return False


def verify_candidate(candidate, approved_hosts, client_factory=BudgetClient):
    """Validate same vacancy/form and employer evidence, never publish it.

    Never follow an unapproved host, fetch a job-search listing or submit forms.
    A feed-supplied application URL can be checked only after its host is
    independently approved for this bounded preflight.
    """
    started = time.monotonic()
    row = dict(provider=candidate.get("provider"), provider_id=candidate.get("provider_id"),
               employer=candidate.get("employer"), title=candidate.get("title"),
               country=candidate.get("country"), application_url=candidate.get("apply_url"),
               state="not-checked", vacancy_match=False, enabled_form=False,
               employer_identity_evidence="not-established",
               production_enabled=False, added_verified_internship=False,
               requests=0, bytes_read=0, renderings=0)
    client = None
    try:
        if candidate.get("provider") != "jobtech-se" or candidate.get("country") != "SE":
            raise ValueError("Only Swedish JobTech pilot candidates are eligible")
        if candidate.get("verification_state") != "unverified":
            raise ValueError("Candidate must remain unverified before live review")
        url = https_url(candidate.get("apply_url"))
        if not url:
            raise ValueError("No approved, job-specific HTTPS application URL in feed")
        host = urlsplit(url).hostname
        if host not in approved_hosts:
            row["state"] = "host-review-required"
            row["reason"] = "Feed-referenced ATS host not on independently approved preflight list"
            return row
        client = client_factory(seconds=20, max_requests=4, delay=1.0)
        # A redirect to a different host (or a downgrade) is not a grant.
        client.redirect_scope_allowed = lambda target: bool(
            https_url(target, {host}) and urlsplit(target).hostname == host
        )
        captured = CapturedClient(client)
        record = dict(url=url, apply_url=url, title=candidate["title"],
                      external_id=candidate["provider_id"],
                      employer=candidate["employer"], inventory_evidence="public-jobtech-referral")
        source = dict(id="preflight-jobtech-"+str(candidate["provider_id"]),
                      adapter="employer-index", employer=candidate["employer"],
                      employer_aliases=[], allowed_hosts=[host])
        stamp = datetime.now(timezone.utc).isoformat()
        # Reuse the no-browser branch of the existing policy-v2 verifier.
        proof = _verify_vacancy(record, source, captured, stamp)
        target = canonical_url(proof["url"])
        body = captured.pages.get(target)
        if body is None:
            raise ValueError("Application form was not fetched from same approved host")
        if not applicant_form(body, strict=True):
            raise ValueError("Strict visible enabled applicant form not established")
        row["vacancy_match"] = True
        row["enabled_form"] = True
        row["proof_method"] = proof["method"]
        identity = any(_identity_matches(content, page_url, candidate["employer"],
                                          candidate["title"])
                       for page_url, content in captured.pages.items())
        if identity:
            row["employer_identity_evidence"] = "same-vacancy-jobposting-hiring-organization"
            row["state"] = "same-vacancy-form-and-owner-evidence"
        else:
            row["state"] = "form-observed-employer-identity-unverified"
        # This report alone does not establish a fully verified production
        # opportunity; unique ID, origin, location and review are still needed.
        row["reason"] = "Live public HTML inspected; production policy-v2 review still required"
    except Exception as exc:
        if row["state"] != "host-review-required":
            row["state"] = "blocked" if blocked_error(exc) else "unverified"
            row["reason"] = str(exc)[:220]
    finally:
        row["requests"] = client.requests if client else 0
        row["bytes_read"] = client.bytes if client else 0
        row["elapsed_seconds"] = round(time.monotonic()-started, 3)
    return row


def verify_candidates(report, approved_hosts, max_candidates=2, client_factory=BudgetClient):
    """No hidden network access. Each exact candidate gets at most 4 requests."""
    if report.get("provider") != "jobtech-se" or report.get("mode") != "discovery-only":
        raise ValueError("Expected a JobTech discovery-only JSON report")
    if not isinstance(approved_hosts, (list, tuple, set)) or not approved_hosts:
        raise ValueError("Explicit, nonempty exact host allowlist required")
    if len(approved_hosts) > 5 or any(
        not isinstance(h, str) or not h or h.lower() != h or
        not https_url("https://" + h, {h}) for h in approved_hosts
    ):
        raise ValueError("Invalid preflight host allowlist")
    if not 1 <= max_candidates <= 5:
        raise ValueError("Invalid verification candidate limit")
    candidates=report.get("candidates")
    if not isinstance(candidates, list):
        raise ValueError("Candidate list required")
    # Stable deterministic order, bounded before any live reads.
    rows = [verify_candidate(x, set(approved_hosts), client_factory)
            for x in sorted(candidates, key=lambda x:str(x.get("provider_id","")))[:max_candidates]]
    return dict(schema_version=1, mode="application-readonly-preflight",
        provider="jobtech-se", checked_at=datetime.now(timezone.utc).isoformat(),
        candidates_seen=len(candidates), candidates_attempted=len(rows),
        requests=sum(x["requests"] for x in rows),
        bytes_read=sum(x["bytes_read"] for x in rows),
        renderings=0, states=dict(Counter(x["state"] for x in rows)), rows=rows,
        verified_vacancies_added=0, collector_registry_modified=False,
        applications_submitted=0, production_enabled=False)
