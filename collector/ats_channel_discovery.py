"""Offline, fail-closed discovery of employer-linked ATS channels.

This module never fetches URLs, modifies source registries, or verifies vacancies.
It only turns already-reviewed, employer-declared page observations into an
auditable queue for human access/identity review.
"""
from __future__ import annotations

from collections import defaultdict
from urllib.parse import urlsplit
import re

PILOT_COUNTRIES = ("DE", "FR", "BE", "IE")
TOKEN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,99}$")
PERSONIO = re.compile(r"^([a-z0-9-]+)\.jobs\.personio\.(?:de|com)$")
RECRUITEE = re.compile(r"^([a-z0-9-]+)\.recruitee\.com$")
RECRUITEE_RESERVED = {"www", "app", "blog", "support", "landing", "careers-analytics", "tagging-server"}


def safe_url(raw):
    """Reject non-HTTPS, credentials, custom ports, controls and deceptive URLs."""
    if not isinstance(raw, str) or not raw or any(ord(ch) < 32 or ch == "\\" for ch in raw):
        return None
    try:
        p = urlsplit(raw.strip())
        if p.scheme != "https" or not p.hostname or p.username or p.password or p.port is not None:
            return None
        if not re.fullmatch(r"[a-z0-9.-]+", p.hostname.lower()):
            return None
        return p
    except ValueError:
        return None


def same_official_page(a, b):
    x, y = safe_url(a), safe_url(b)
    return bool(x and y and x.hostname.lower() == y.hostname.lower()
                and x.path.rstrip("/") == y.path.rstrip("/") and x.query == y.query)


def identify_channel(url):
    """Parse only recognized tenant patterns; no provider URL is fetched."""
    p = safe_url(url)
    if not p:
        return None
    host = p.hostname.lower()
    segments = [s for s in p.path.split("/") if s]
    adapter, tenant, hint, gate = None, None, None, "review-required"
    if host in {"job-boards.greenhouse.io", "boards.greenhouse.io", "boards.eu.greenhouse.io"}:
        if segments and TOKEN.fullmatch(segments[0]) and segments[0] not in {"embed", "jobs"}:
            adapter, tenant = "greenhouse", segments[0].lower()
            hint = "boards-api.eu.greenhouse.io" if host == "boards.eu.greenhouse.io" else "boards-api.greenhouse.io"
    elif host in {"jobs.lever.co", "jobs.eu.lever.co"}:
        if segments and TOKEN.fullmatch(segments[0]):
            adapter, tenant = "lever", segments[0].lower()
            hint = "api.eu.lever.co" if host == "jobs.eu.lever.co" else "api.lever.co"
    elif PERSONIO.fullmatch(host):
        adapter, tenant = "personio-xml", host
        hint = "https://" + host + "/xml"
    elif RECRUITEE.fullmatch(host):
        tenant_match = RECRUITEE.fullmatch(host).group(1)
        if tenant_match not in RECRUITEE_RESERVED:
            adapter, tenant = "recruitee", host
            hint = "https://" + host + "/api/offers/"
    elif host == "jobs.ashbyhq.com" or host.endswith(".smartrecruiters.com"):
        adapter, tenant, gate = "access-review", host, "blocked-or-not-approved"
    elif (host.endswith(".teamtailor.com") and host.split(".")[0] not in {"www", "app"}) or host.endswith(".softgarden.de"):
        adapter, tenant, gate = "unsupported-provider", host, "no-reviewed-adapter"
    if not adapter:
        return None
    return dict(adapter=adapter, tenant=tenant, channel_key=adapter + ":" + tenant,
                observed_host=host, endpoint_hint=hint, gate=gate)


def _registered_keys(source):
    adapter = source.get("adapter")
    if adapter not in {"greenhouse", "lever", "personio-xml", "recruitee"}:
        return set()
    keys = set()
    for value in (source.get("career_url"), source.get("feed_url")):
        item = identify_channel(value)
        if item and item["adapter"] == adapter:
            keys.add(item["channel_key"])
    if adapter in {"greenhouse", "lever"} and source.get("board"):
        keys.add(adapter + ":" + str(source["board"]).lower())
    return keys


def pilot(companies, sources, scans, countries=PILOT_COUNTRIES, per_country=6):
    """Build a deterministic review queue using historical official-page scans.

    A company's target country is research scope, NOT a verified workplace.
    New candidates cannot be enabled by this function.
    """
    if per_country < 1 or per_country > 25:
        raise ValueError("Per-country sample must be between 1 and 25")
    countries = tuple(dict.fromkeys(countries))
    if not countries or any(not re.fullmatch(r"[A-Z]{2}", c) for c in countries):
        raise ValueError("Invalid country list")
    companies_by_id = {c["id"]: c for c in companies}
    scans_by_company = defaultdict(list)
    for observation in scans:
        c = companies_by_id.get(observation.get("company_id"))
        if not c or observation.get("status") != "reviewed":
            continue
        # The scan must begin at an exact page declared by the employer.
        if not any(same_official_page(observation.get("url"), u)
                   for u in (c.get("career_url"), c.get("website_url"))):
            continue
        # A redirect to a different hostname needs a separate review.
        first, final = safe_url(observation.get("url")), safe_url(observation.get("final_url"))
        if not first or not final or first.hostname.lower() != final.hostname.lower():
            continue
        scans_by_company[c["id"]].append(observation)

    existing = defaultdict(set)
    for source in sources:
        for key in _registered_keys(source):
            existing[key].add(source["id"])

    samples = {}
    selected_ids = set()
    for country in countries:
        candidates = [c for c in companies if country in c.get("target_countries", [])]
        def can_reuse_adapter(company):
            return any((identify_channel(url) or {}).get("gate") == "review-required"
                       for item in scans_by_company[company["id"]]
                       for url in item.get("ats_links", []))
        candidates.sort(key=lambda c: (
            -int(can_reuse_adapter(c)),
            -int(any(item.get("ats_links") for item in scans_by_company[c["id"]])),
            c["id"]))
        chosen = candidates[:per_country]
        samples[country] = [c["id"] for c in chosen]
        selected_ids.update(samples[country])

    queued = {}
    for company_id in sorted(selected_ids):
        company = companies_by_id[company_id]
        for scan in scans_by_company[company_id]:
            for raw in scan.get("ats_links", []):
                found = identify_channel(raw)
                if not found:
                    continue
                index = (company_id, found["channel_key"])
                if index not in queued:
                    known = sorted(existing.get(found["channel_key"], set()))
                    owned = sorted(set(known).intersection(company.get("source_ids", [])))
                    if owned:
                        status = "already-registered"
                    elif known:
                        status = "ownership-review"
                    elif found["gate"] == "review-required":
                        status = "requires-access-and-identity-review"
                    elif found["gate"] == "blocked-or-not-approved":
                        status = "access-review"
                    else:
                        status = "unsupported-provider"
                    queued[index] = dict(company_id=company_id, company_name=company["name"],
                        candidate_countries=sorted(set(company.get("target_countries", [])).intersection(countries)),
                        adapter=found["adapter"], tenant=found["tenant"],
                        channel_key=found["channel_key"], observed_host=found["observed_host"],
                        endpoint_hint=found["endpoint_hint"], status=status,
                        registry_source_ids=known, evidence_pages=set(), observed_links=set(),
                        robots="not-rechecked-offline", hosts="not-authorized-by-discovery",
                        enabled=False, verified_vacancies_added=0)
                queued[index]["evidence_pages"].add(scan["url"])
                queued[index]["observed_links"].add(raw.strip())
    proposals = []
    for key in sorted(queued):
        item = queued[key]
        item["evidence_pages"] = sorted(item["evidence_pages"])
        item["observed_links"] = sorted(item["observed_links"])
        proposals.append(item)
    country_stats = []
    for country in countries:
        found = [x for x in proposals if x["company_id"] in samples[country]]
        country_stats.append(dict(country=country, companies_sampled=len(samples[country]),
            sample_company_ids=samples[country], detected_channels=len(found),
            review_candidates=sum(x["status"] == "requires-access-and-identity-review" for x in found),
            already_registered=sum(x["status"] == "already-registered" for x in found),
            ownership_review=sum(x["status"] == "ownership-review" for x in found),
            blocked_or_unsupported=sum(x["status"] in ("access-review", "unsupported-provider") for x in found)))
    return dict(schema_version=1, mode="offline-historical-review-only", countries=country_stats,
        proposals=proposals, observed_channel_count=len(proposals),
        newly_enabled_sources=0, new_verified_internships=0,
        additional_http_requests=0, additional_browser_renders=0,
        notes=["Historical scans do not prove current vacancy or current robots permission.",
               "Target countries are research scope, not confirmed work locations.",
               "No persistent source or catalog modifications; explicit review needed before onboarding."])
