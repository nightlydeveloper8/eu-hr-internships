"""Read-only discovery of employers from reviewed public institutional directories.

No registry writes, no unknown-host requests, no job verification or applicant actions.
A candidate's directory country is a discovery scope, not a job workplace.
"""
from __future__ import annotations

from collections import Counter
from html.parser import HTMLParser
from urllib.parse import urlsplit, urljoin
import re
import time

from .company_registry import company_key
from .runtime import BudgetClient


class DiscoveryAccessError(ValueError):
    pass


def safe_https_url(raw):
    if not isinstance(raw, str) or not raw or raw.strip() != raw:
        return None
    if any(ord(ch) < 32 or ch == "\\" for ch in raw):
        return None
    try:
        parsed = urlsplit(raw)
        host = parsed.hostname
        if (parsed.scheme != "https" or not host or parsed.username or parsed.password
                or parsed.port is not None or not re.fullmatch(r"[a-z0-9.-]+", host.lower())):
            return None
        if host.lower() in ("localhost", "localhost.localdomain") or not "." in host:
            return None
        if re.fullmatch(r"\d+(?:\.\d+){3}", host):
            return None
    except ValueError:
        return None
    return parsed


def canonical_host(url):
    parsed = safe_https_url(url)
    if not parsed:
        return None
    return parsed.hostname.lower().removeprefix("www.")


class _LinkCards(HTMLParser):
    """Only explicitly marked employer cards, never arbitrary directory links."""
    def __init__(self, marker):
        super().__init__(convert_charrefs=True)
        self.marker = marker
        self.current = None
        self.rows = []

    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        values = dict(attrs)
        if self.marker not in values.get("class", "").split():
            return
        href = values.get("href")
        if href:
            self.current = [href, "", 1]

    def handle_data(self, data):
        if self.current:
            self.current[1] += data[:200]

    def handle_endtag(self, tag):
        if self.current and tag == "a":
            self.rows.append(tuple(self.current[:2]))
            self.current = None



class _EmployerTable(HTMLParser):
    """Read only employer-name / external-website pairs from two-column tables."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.row = None
        self.cell = None
        self.rows = []

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self.row = []
        elif tag in ("td", "th") and self.row is not None:
            self.cell = dict(tag=tag, text=[], links=[])
        elif tag == "a" and self.cell is not None:
            href = dict(attrs).get("href")
            if href:
                self.cell["links"].append(href)

    def handle_data(self, value):
        if self.cell is not None:
            self.cell["text"].append(value)

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self.cell is not None and self.row is not None:
            self.row.append(self.cell)
            self.cell = None
        elif tag == "tr":
            if self.row and len(self.row) >= 2 and all(x["tag"] == "td" for x in self.row[:2]):
                name = " ".join(" ".join(self.row[0]["text"]).split())
                for link in self.row[1]["links"]:
                    if name and safe_https_url(link):
                        self.rows.append((name, link))
                        break
            self.row = None
            self.cell = None


def extract_directory_rows(seed, html):
    """Use existing reviewed parsers, or a source-specific card marker."""
    if seed["parser"] in ("ikom", "phdtalent", "fontys"):
        # Reuse the mapping parsers without executing the old bulk importer.
        from scripts.map_employers import directory_rows
        return list(directory_rows(seed["parser"], html))
    if seed["parser"] == "employer-table":
        marker = seed.get("page_marker")
        if (not isinstance(marker, str) or len(marker) < 5
                or marker.casefold() not in html.casefold()):
            raise ValueError("Employer-table page marker missing or changed")
        parser = _EmployerTable()
        parser.feed(html)
        return [(name, website, seed["url"]) for name, website in parser.rows]
    if seed["parser"] == "employer-card":
        marker = seed.get("card_class")
        if not marker or not re.fullmatch(r"[A-Za-z0-9_-]{2,60}", marker):
            raise ValueError("Employer-card parser requires a reviewed CSS class")
        parser = _LinkCards(marker)
        parser.feed(html)
        return [(name.strip(), urljoin(seed["url"], href), seed["url"])
                for href, name in parser.rows]
    raise ValueError("Unreviewed directory parser")


class SeedClient(BudgetClient):
    """Reject cross-host redirects BEFORE following them, including robots redirects."""
    def __init__(self, seed, seconds=20, max_requests=6):
        super().__init__(seconds=seconds, max_requests=max_requests, delay=.5)
        self.seed_host = urlsplit(seed["url"]).hostname.lower()

    def _approved(self, url):
        parsed = safe_https_url(url)
        return bool(parsed and parsed.hostname.lower() == self.seed_host)

    def permitted(self, url):
        if not self._approved(url):
            return False
        return super().permitted(url)

    def request(self, url, method="GET", robots=True, timeout=12, attempts=1):
        if not self._approved(url) or method != "GET" or not robots:
            # robots=False is permitted only for the existing Client's internal
            # robots.txt fetch, and only on the exact approved source host.
            if not (method == "GET" and not robots and self._approved(url)
                    and urlsplit(url).path == "/robots.txt"):
                raise DiscoveryAccessError("Request outside reviewed seed scope")
        return super().request(url, method=method, robots=robots, timeout=timeout,
                               attempts=1)


def validate_seed(seed):
    required = ("id", "country", "url", "parser", "access_reviewed")
    if any(key not in seed for key in required):
        raise ValueError("Incomplete seed")
    if not re.fullmatch(r"[a-z0-9-]{3,60}", seed["id"]):
        raise ValueError("Invalid seed ID")
    if not re.fullmatch(r"[A-Z]{2}", seed["country"]):
        raise ValueError("Invalid seed country")
    if not safe_https_url(seed["url"]):
        raise ValueError("Invalid official seed URL")
    if seed["parser"] not in ("ikom", "phdtalent", "fontys", "employer-card", "employer-table"):
        raise ValueError("Unsupported seed parser")
    if not isinstance(seed["access_reviewed"], bool):
        raise ValueError("Missing explicit access review flag")
    if seed["parser"] == "employer-card" and not seed.get("card_class"):
        raise ValueError("Missing reviewed employer-card marker")
    if seed["parser"] == "employer-table" and (
            not isinstance(seed.get("page_marker"), str)
            or len(seed["page_marker"]) < 5):
        raise ValueError("Missing reviewed employer-table marker")


def fetch_reviewed_seed(seed, seconds=20, max_requests=6):
    """Opt-in network stage: one reviewed seed URL, robots-aware and bounded."""
    validate_seed(seed)
    if not seed["access_reviewed"]:
        raise DiscoveryAccessError("Source is pending access/robots review")
    client = SeedClient(seed, seconds=seconds, max_requests=max_requests)
    started = time.monotonic()
    body, status, final = client.request(seed["url"])
    if not safe_https_url(final) or canonical_host(final) != canonical_host(seed["url"]):
        raise DiscoveryAccessError("Cross-host seed redirect denied")
    if len(body) > 1_000_000:
        raise DiscoveryAccessError("Directory snapshot exceeds byte budget")
    if status != 200:
        raise DiscoveryAccessError("Directory returned non-200 status")
    return dict(body=body.decode("utf-8", "replace"), final_url=final,
                requests=client.requests, bytes=client.bytes,
                duration_seconds=round(time.monotonic() - started, 3))


def build_discovery_queue(seeds, snapshots, companies, previous=None, per_seed=40):
    """Turn snapshots into unverified company leads; retain candidates across cycles.

    Input snapshots are explicit acquisition events. This never refreshes
    last_verified_at and never changes jobs, company registry or source registry.
    """
    if not 1 <= per_seed <= 100:
        raise ValueError("Per-seed candidate limit out of range")
    existing_names = {company_key(name) for c in companies
                      for name in [c["name"]] + c.get("aliases", []) if name}
    existing_hosts = {canonical_host(url) for c in companies
                      for url in (c.get("website_url"), c.get("career_url"))}
    existing_hosts.discard(None)
    records = {}
    if previous:
        for row in previous.get("candidates", []):
            if (company_key(row.get("name", "")) in existing_names
                    or canonical_host(row.get("declared_website_url")) in existing_hosts):
                # The candidate was integrated since the previous cycle.
                # Do not keep it queued as a new employer.
                continue
            records[row["key"]] = dict(row)
    stats = []
    seen_ids = set()
    for seed in seeds:
        validate_seed(seed)
        if seed["id"] in seen_ids:
            raise ValueError("Duplicate discovery seed")
        seen_ids.add(seed["id"])
        snapshot = snapshots.get(seed["id"])
        if snapshot is None:
            stats.append(dict(seed_id=seed["id"], country=seed["country"],
                              status="no-new-observation", candidates=0,
                              requests=0, bytes=0, duration_seconds=0))
            continue
        if not isinstance(snapshot, dict) or not isinstance(snapshot.get("html"), str):
            raise ValueError("Invalid captured directory snapshot")
        if len(snapshot["html"].encode("utf-8")) > 1_000_000:
            raise ValueError("Snapshot byte budget exceeded")
        # A capture is not permission to collect unknown outbound domains.
        final = snapshot.get("final_url", seed["url"])
        if not safe_https_url(final) or urlsplit(final).hostname != urlsplit(seed["url"]).hostname:
            raise DiscoveryAccessError("Unreviewed directory redirect")
        observed_at = snapshot.get("observed_at")
        if not isinstance(observed_at, str) or not observed_at:
            raise ValueError("Missing observation timestamp")
        count = 0
        observed = set()
        for name, website, evidence in extract_directory_rows(seed, snapshot["html"]):
            clean_name = " ".join(name.split())[:120]
            key_name = company_key(clean_name)
            host = canonical_host(website)
            if not key_name or not host or len(key_name) < 2:
                continue
            # Ignore directory self-links, search portals, URL shorteners and social media.
            if host == canonical_host(seed["url"]) or host in {
                "linkedin.com", "facebook.com", "instagram.com", "google.com",
                "bit.ly", "tinyurl.com", "indeed.com", "glassdoor.com"}:
                continue
            canonical_key = host + "|" + key_name
            if canonical_key in observed:
                continue
            observed.add(canonical_key)
            if key_name in existing_names or host in existing_hosts:
                continue
            key = canonical_key
            proof = evidence if canonical_host(evidence) == canonical_host(seed["url"]) else seed["url"]
            if key in records:
                records[key]["last_observed_at"] = max(records[key]["last_observed_at"], observed_at)
                records[key]["evidence_urls"] = sorted(set(records[key]["evidence_urls"]) | {proof})
                records[key]["candidate_country_scopes"] = sorted(set(records[key]["candidate_country_scopes"]) | {seed["country"]})
            else:
                records[key] = dict(key=key, name=clean_name, declared_website_url=website,
                    candidate_country_scopes=[seed["country"]], evidence_urls=[proof],
                    first_observed_at=observed_at, last_observed_at=observed_at,
                    status="identity-and-host-review-required",
                    ats_source_enabled=False, verified_hr_internships=0)
            count += 1
            if count >= per_seed:
                break
        stats.append(dict(seed_id=seed["id"], country=seed["country"],
            status="observed", candidates=count,
            requests=snapshot.get("requests", 0), bytes=snapshot.get("bytes", 0),
            duration_seconds=snapshot.get("duration_seconds", 0)))
    candidates = sorted(records.values(), key=lambda r:r["key"])
    return dict(schema_version=1, state="discovery-only", source_metrics=stats,
                candidates=candidates, pending_candidate_count=len(candidates),
                enabled_ats_sources=0, added_verified_hr_internships=0,
                requests=sum(x["requests"] for x in stats),
                total_seconds=round(sum(x["duration_seconds"] for x in stats), 3),
                warnings=["Directory participation is not a job, workplace or ATS ownership proof.",
                          "No host or ATS is authorized by a directory link.",
                          "Stale or missing observations cannot close a vacancy.",
                          "Candidate count is not an opportunity count."])
