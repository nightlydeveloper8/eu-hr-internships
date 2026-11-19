"""Bounded follow-up: public-feed candidate -> exact named application page.

This verifier only reads application URLs already observed in a licensed feed,
and only on explicitly approved hosts. It deliberately does not promote
records into the policy-v2 catalog or claim employer ownership from a feed
referral. It reuses the existing conservative HTML vacancy/applicant verifier.
"""
from __future__ import annotations

from datetime import datetime, timezone
from urllib.parse import urlsplit, urljoin
import re
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



def academic_term_title_variant(feed_title, official_title):
    """Limited diagnostic: only VT/HT year markers may be absent at source.

    No fuzzy distance, synonym expansion, employer-name substitution or
    promotion to verified. The observed ATS title must otherwise be identical.
    """
    def tokens(value):
        return re.findall(r"[a-z0-9]+", fold(plain(value)))
    expected, actual = tokens(feed_title), tokens(official_title)
    if not expected or not actual or len(actual) < 6 or expected == actual:
        return False
    term_positions = [i for i, x in enumerate(expected)
                      if re.fullmatch(r"(?:vt|ht)(?:\d{2}|\d{4})", x)]
    return len(term_positions) == 1 and [
        x for i, x in enumerate(expected) if i not in term_positions
    ] == actual


def _legal_page_owner_evidence(captured, first_url, employer):
    """One observed *same-host* public legal/privacy link; no guessed pages.

    Named legal entity on the actual recruiting host strengthens ownership.
    This does not establish full policy-v2 verification independently.
    """
    page = captured.pages.get(canonical_url(first_url))
    if not page:
        return None
    doc = Document(page, first_url)
    host = urlsplit(first_url).hostname
    for href, label, _ in doc.links:
        if not re.search(r"privacy|integritet|datenschutz|impressum|legal",fold(label)):
            continue
        target = https_url(urljoin(first_url, href), {host})
        if not target or canonical_url(target) == canonical_url(first_url):
            continue
        try:
            body, status, final = captured.request(target)
            if status != 200 or canonical_url(final) != canonical_url(target):
                continue
            legal = fold(Document(body, final).text)
            name = fold(plain(employer))
            if name and re.search(r"(?<!\w)"+re.escape(name)+r"(?!\w)",legal):
                return target
        except Exception:
            # No legal-page evidence is not a failed vacancy form read.
            continue
        break  # At most one legal page per employer/candidate.
    return None

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
            evidence_url = _legal_page_owner_evidence(captured, url, candidate["employer"])
            if evidence_url:
                row["employer_identity_evidence"] = "same-host-legal-page-names-employer"
                row["employer_identity_evidence_url"] = evidence_url
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
            # Some public feeds add a Swedish academic term (VT27/HT26) to
            # an otherwise identical official title. Report that separately;
            # it can never bypass policy v2's exact same-title requirement.
            if ("Current page does not identify the same vacancy" in str(exc)
                    and "captured" in locals() and "url" in locals()):
                body = captured.pages.get(canonical_url(url))
                if body:
                    page = Document(body, url)
                    matches = [title for title in page.h1
                               if academic_term_title_variant(candidate["title"], title)]
                    if len(set(matches)) == 1:
                        row["seasonal_title_variant"] = True
                        row["official_title_observed"] = matches[0]
                        row["enabled_form"] = applicant_form(body, strict=True)
                        row["state"] = ("seasonal-title-variant-form-observed-review-required"
                                        if row["enabled_form"] else
                                        "seasonal-title-variant-no-enabled-form")
                        row["reason"] = ("Academic term differs but remaining title matches; "
                                         "exact policy-v2 title proof NOT bypassed")
    finally:
        # Useful, bounded diagnostics even on an exact-title failure; neither
        # complete HTML nor personal applicant fields are stored in the report.
        if "captured" in locals():
            headings, jobs, owners = [], [], []
            for page_url, content in list(captured.pages.items())[:2]:
                doc = Document(content, page_url)
                headings.extend(doc.h1[:3])
                for post in doc.jobposts()[:3]:
                    jobs.append(plain(post.get("title"))[:160])
                    org = post.get("hiringOrganization")
                    if isinstance(org, dict):
                        owners.append(plain(org.get("name"))[:130])
            row["observed_headings"] = headings[:4]
            row["structured_job_titles"] = jobs[:4]
            row["structured_hiring_organizations"] = owners[:4]
        row["requests"] = client.requests if client else 0
        row["bytes_read"] = client.bytes if client else 0
        row["elapsed_seconds"] = round(time.monotonic()-started, 3)
    return row
