"""Bounded JobTech -> reviewed employer ATS adapter for the ordinary collection pipeline.

Never infer ATS ownership from JobTech metadata. This adapter is intentionally
disabled in the source registry. In staging, an explicit opt-in is required.
Future production use additionally requires a *separate* explicit rollout gate,
fresh same-vacancy employer/ATS verification and the ordinary pipeline finalize.
No form submission, rendering, API tokens, EURES reads or absence-based closure.
"""
from __future__ import annotations

from datetime import datetime, timezone
from urllib.parse import urlsplit
import time

from .classify import fold, plain
from .official_feed_discovery import JOBTECH_HOST, JOBTECH_QUERIES, discovery_report, https_url
from .official_feed_policy_dossier import ats_parent, review
from .official_feed_staging import staging_part
from .runtime import BudgetClient

ADAPTER = "jobtech-policy-v2"
MAX_SOURCE_REQUESTS = 18
MAX_SOURCE_SECONDS = 100
MAX_RESULTS_PER_QUERY = 10
MAX_QUERIES = 3


def source_gate(source, *, preview=False):
    """Validate the entire reviewed host/provenance/budget and activation scope."""
    if not isinstance(source, dict) or source.get("adapter") != ADAPTER:
        raise ValueError("Unknown employer feed adapter")
    if source.get("feed_provider") != "jobtech-se" or source.get("target_countries") != ["SE"]:
        raise ValueError("Unsupported national feed or workplace country")
    if source.get("ownership_scope") != "reviewed-hosts" or source.get("require_employer_identity") is not True:
        raise ValueError("Independent employer ownership review is mandatory")
    if source.get("allowed_hosts") != ["jobb.jobandtalent.com"]:
        raise ValueError("This first pilot grants precisely one previously reviewed recruiting host")
    if source.get("reviewed_inventory_url") != "https://jobb.jobandtalent.com/sitemap":
        raise ValueError("An exact reviewed employer inventory URL is mandatory")
    if source.get("provider_id") != "31558200" or source.get("expected_ats_id") != "8503489":
        raise ValueError("Expected public ID and distinct employer ATS posting ID required")
    if source.get("employer") != "Jobandtalent Sweden AB" or source.get("expected_city") != "Malmö":
        raise ValueError("Independently reviewed legal entity and workplace required")
    if source.get("id") != "staging-jobandtalent-se":
        raise ValueError("Canonical source ID protects stable catalog identity")
    if (source.get("jobtech_queries") != list(JOBTECH_QUERIES)
            or source.get("results_per_query") != MAX_RESULTS_PER_QUERY):
        raise ValueError("Only audited bounded feed query set is permitted")
    if (type(source.get("max_requests")) is not int or
            not 13 <= source["max_requests"] <= MAX_SOURCE_REQUESTS or
            type(source.get("collection_seconds")) is not int or
            not 40 <= source["collection_seconds"] <= MAX_SOURCE_SECONDS):
        raise ValueError("Source exceeds audited request/time limits")
    if (source.get("enabled") is False and source.get("staging_only") is True
            and source.get("rollout_approved") is False):
        if not preview:
            raise ValueError("Disabled JobTech source requires an explicit read-only preview")
        return "staging"
    if (source.get("enabled") is True and source.get("staging_only") is False
            and source.get("rollout_approved") is True and not preview
            and isinstance(source.get("rollout_authorization"), str)
            and len(source["rollout_authorization"].strip()) >= 10):
        return "production"
    raise ValueError("Source activation is not approved; no network calls permitted")


class AtsBudgetFactory:
    """Share a hard remaining request/time budget across both internal ATS clients."""
    def __init__(self, first_client, total_requests, seconds, factory=BudgetClient):
        self.first = first_client
        self.total_requests = total_requests
        self.deadline = time.monotonic() + seconds
        self.factory = factory
        self.clients = []
    def __call__(self, *, seconds, max_requests, delay):
        elapsed_count = getattr(self.first, "requests", 0) + sum(c.requests for c in self.clients)
        left = self.total_requests - elapsed_count
        remaining = min(seconds, self.deadline - time.monotonic())
        if left <= 0 or remaining <= .5:
            raise ValueError("Shared source budget exhausted before ATS review")
        client = self.factory(seconds=remaining, max_requests=min(max_requests, left), delay=delay)
        self.clients.append(client)
        return client
    @property
    def requests(self):
        return sum(c.requests for c in self.clients)
    @property
    def bytes(self):
        return sum(c.bytes for c in self.clients)
    @property
    def rate_limited_skips(self):
        return sum(getattr(c, "rate_limited_skips", 0) for c in self.clients)


def process_jobtech_source(source, client, stamp, *, prior_jobs=(),
                           verify=True, preview=False, ats_client_factory=BudgetClient):
    """Return the exact (report, jobs, closure_eligible) shape of process_source.

    When called from an ordinary enabled daily shard, preview=False always.
    Disabled preview callers must explicitly opt in, and finalize only in tmp.
    """
    started = time.monotonic()
    report = dict(id=source.get("id"), employer=source.get("employer"),
                  adapter=ADAPTER, checked_at=stamp, status="partial",
                  complete=False, closure_complete=False,
                  snapshot_kind="bounded-public-feed-and-reviewed-employer-ATS",
                  discovery_scope="one-reviewed-public-ID-with-fresh-ATS-proof",
                  page_failures=0, records_inspected=0,
                  matching=0, collected=0, verification_states={},
                  requests=0, bytes_read=0, ats_requests=0,
                  ats_bytes_read=0, browser_renderings=0,
                  source_enabled=source.get("enabled") is True,
                  closure_not_inferred=True)
    part = dict(report=report, jobs=[], closure_eligible=[])
    ats = None
    try:
        if not verify:
            raise ValueError("Policy-v2 verification cannot be disabled for reviewed feed sources")
        mode = source_gate(source, preview=preview)
        if mode == "production" and not isinstance(client, BudgetClient):
            raise ValueError("Production requires the robots-aware BudgetClient")
        if not callable(getattr(client, "json", None)):
            raise ValueError("A bounded structured-feed reader is required")
        # Redirects outside the single public API are refused before fetching.
        client.redirect_scope_allowed = lambda target: bool(
            https_url(target, {JOBTECH_HOST})
            and urlsplit(target).hostname == JOBTECH_HOST
        )
        discovered = discovery_report(
            client, catalog_urls=(j.get("url") for j in prior_jobs if isinstance(j, dict)),
            queries=tuple(source["jobtech_queries"]),
            per_query=source["results_per_query"],
        )
        report.update(feed_rows_scanned=discovered["input_records"],
                      feed_hr_candidates=discovered["candidate_count"],
                      feed_requests=discovered["requests"],
                      feed_bytes_read=discovered["bytes_read"],
                      collected=discovered["input_records"])
        candidates = [row for row in discovered["candidates"]
                      if row.get("provider_id") == source["provider_id"]]
        if len(candidates) != 1:
            raise ValueError("Exact public JobTech posting absent or duplicated in limited search")
        candidate = candidates[0]
        if (fold(plain(candidate.get("employer"))) != fold(source["employer"])
                or fold(plain(candidate.get("city"))) != fold(source["expected_city"])
                or candidate.get("country") != "SE"):
            raise ValueError("JobTech employer or locality differs from reviewed source")
        parsed = ats_parent(candidate.get("apply_url"), source["allowed_hosts"][0])
        if not parsed or parsed["ats_id"] != source["expected_ats_id"]:
            raise ValueError("Unexpected ATS tenant or posting ID")
        elapsed = time.monotonic() - started
        remaining = source["collection_seconds"] - elapsed
        if remaining <= 1:
            raise ValueError("No source time budget for independent ATS verification")
        ats = AtsBudgetFactory(client, source["max_requests"],
                               remaining, factory=ats_client_factory)
        dossier = review(
            candidate,
            approved_host=source["allowed_hosts"][0],
            approved_inventory_url=source["reviewed_inventory_url"],
            client_factory=ats,
        )
        report.update(dossier_state=dossier["status"],
                      dossier_ats_id=dossier.get("ats_posting_id"),
                      dossier_inventory_confirmed=dossier.get("official_inventory_confirmed",False))
        # Never pass the pre-verification collection timestamp as new evidence.
        evidence_stamp = datetime.now(timezone.utc).isoformat()
        observation = staging_part(
            candidate, dossier, source, evidence_stamp, prior_jobs,
            production=(mode == "production"),
        )
        if not observation["jobs"]:
            raise ValueError(observation["report"].get("reason")
                             or dossier.get("reason") or "Policy-v2 review incomplete")
        part["jobs"] = observation["jobs"]
        report.update(records_inspected=1, matching=1,
                      verification_states={"verified": 1},
                      reviewed_ats_id=parsed["ats_id"],
                      preexisting_exact_matches=observation["report"].get("preexisting_exact_matches", 0))
        # This is a partial sample of one known opening, never the exhaustive
        # employer inventory; no automatic closed records can result.
    except (ValueError, TypeError, KeyError, AttributeError, RuntimeError, OSError) as exc:
        report.update(status="partial", page_failures=1,
                      verification_states={"incomplete": 1},
                      reason=str(exc)[:210])
    finally:
        report.update(checked_at=datetime.now(timezone.utc).isoformat(),
                      requests=getattr(client,"requests",0) + (ats.requests if ats else 0),
                      bytes_read=getattr(client,"bytes",0) + (ats.bytes if ats else 0),
                      ats_requests=ats.requests if ats else 0,
                      ats_bytes_read=ats.bytes if ats else 0,
                      rate_limited_skips=getattr(client,"rate_limited_skips",0) +
                          (ats.rate_limited_skips if ats else 0),
                      duration_seconds=round(time.monotonic() - started, 3))
    return part
