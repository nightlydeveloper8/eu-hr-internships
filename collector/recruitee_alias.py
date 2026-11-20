"""Conservative, opt-in reconciliation of an employer Recruitee host alias.

The feed itself publishes careers.smartways.io, whose current GET redirects to
the same employer's Recruitee tenant. Never fabricate an application URL: both
links MUST have been published by the feed and independently read live.
Other Recruitee employers and external-client portals remain unchanged.
"""
import re
from contextlib import contextmanager
from urllib.parse import urlsplit

from .classify import canonical_url, classify_role

TENANT = "smartways.recruitee.com"
ALIAS = "careers.smartways.io"
PILOT_ID = "pilot-smartways-internal-pl"


def source_gate(source):
    """Only the reviewed disabled source or separately authorised rollout."""
    if (not isinstance(source, dict)
            or source.get("id") != PILOT_ID
            or source.get("employer") != "SmartWays"
            or source.get("adapter") != "recruitee"
            or source.get("reviewed_recruitee_alias") != "smartways-internal"
            or not isinstance(source.get("allowed_hosts"), list)
            or len(source["allowed_hosts"]) != 2
            or set(source["allowed_hosts"]) != {TENANT, ALIAS}
            or source.get("application_check") != "recruitee-linked"
            or source.get("feed_url") != f"https://{TENANT}/api/offers/"
            or source.get("target_countries") != ["PL"]
            or source.get("ownership_scope") != "reviewed-hosts"
            or source.get("require_employer_identity") is not True
            or type(source.get("max_requests")) is not int
            or not 8 <= source["max_requests"] <= 14
            or type(source.get("collection_seconds")) is not int
            or not 30 <= source["collection_seconds"] <= 75):
        raise ValueError("Recruitee alias scope, source or budget not reviewed")
    if source.get("enabled") is False and source.get("staging_only") is True and source.get("rollout_approved") is False:
        return "staging"
    if (source.get("enabled") is True and source.get("staging_only") is False
            and source.get("rollout_approved") is True
            and isinstance(source.get("rollout_authorization"), str)
            and len(source["rollout_authorization"].strip()) >= 10):
        return "production"
    raise ValueError("SmartWays alias requires separate explicit rollout approval")


def allowed(url):
    try:
        parsed = urlsplit(canonical_url(url))
    except (TypeError, ValueError):
        return False
    if parsed.query:
        return False
    detail = bool(re.fullmatch(r"/o/[a-zA-Z0-9%_-]+(?:/c/new)?", parsed.path))
    if parsed.hostname == TENANT:
        return detail or parsed.path in ("", "/", "/robots.txt", "/privacy-policy", "/api/offers")
    if parsed.hostname == ALIAS:
        return detail or parsed.path == "/robots.txt"
    return False


@contextmanager
def scope(client):
    previous = getattr(client, "redirect_scope_allowed", None)
    def permitted(url):
        return allowed(url) and (previous is None or previous(url))
    client.redirect_scope_allowed = permitted
    try:
        yield
    finally:
        if previous is None:
            del client.redirect_scope_allowed
        else:
            client.redirect_scope_allowed = previous


def reviewed(source):
    return source_gate(source)


def same_path_redirect(client, url, expected_suffix=""):
    original = urlsplit(canonical_url(url))
    if (original.hostname != ALIAS or original.query or
            not original.path.startswith("/o/")):
        raise ValueError("Unreviewed Recruitee alias URL")
    body, status, final = client.request(url)
    resolved = urlsplit(canonical_url(final))
    if (status != 200 or resolved.hostname != TENANT or
            resolved.path != original.path or resolved.query or
            not resolved.path.endswith(expected_suffix)):
        raise ValueError("Recruitee alias did not resolve to same vacancy path")
    return canonical_url(final)


def reconcile(source, client, records):
    """Read redirected pages only for currently classified HR internships."""
    reviewed(source)
    output = []
    for record in records:
        row = dict(record)
        if (not classify_role(row.get("title",""), row.get("text",""),
                              row.get("employment",""))
                or row.get("countries") != ["PL"]):
            output.append(row)
            continue
        observed = row.get("observed_application_url")
        if not observed:
            raise ValueError("Current Recruitee feed did not publish application URL")
        detail = same_path_redirect(client, row["url"])
        app = same_path_redirect(client, observed, "/c/new")
        if urlsplit(app).path != urlsplit(detail).path.rstrip("/") + "/c/new":
            raise ValueError("Recruitee application alias does not share vacancy path")
        row.update(url=detail, apply_url=detail, observed_application_url=app,
                   inventory_evidence="current-employer-feed")
        output.append(row)
    return output
