"""Conservative, opt-in reconciliation of an employer Recruitee host alias.

The feed itself publishes careers.smartways.io, whose current GET redirects to
the same employer's Recruitee tenant. Never fabricate an application URL: both
links MUST have been published by the feed and independently read live.
Other Recruitee employers and external-client portals remain unchanged.
"""
from urllib.parse import urlsplit

from .classify import canonical_url, classify_role

TENANT = "smartways.recruitee.com"
ALIAS = "careers.smartways.io"
PILOT_ID = "pilot-smartways-internal-pl"


def reviewed(source):
    if (source.get("id") != PILOT_ID
            or source.get("adapter") != "recruitee"
            or source.get("reviewed_recruitee_alias") != "smartways-internal"
            or source.get("enabled") is not False
            or source.get("allowed_hosts") != [TENANT, ALIAS]
            or source.get("application_check") != "recruitee-linked"
            or source.get("feed_url") != f"https://{TENANT}/api/offers/"
            or source.get("target_countries") != ["PL"]):
        raise ValueError("Recruitee alias scope and ownership not reviewed")


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
