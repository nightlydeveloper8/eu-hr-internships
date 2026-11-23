"""Read the #134 ATS inventory in staging with a resumable daily GET budget."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
import signal
from pathlib import Path
import sys
import threading
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, build_opener

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from collector.adapters import AGENT, collect
from collector.ats_channel_discovery import safe_url
from collector.classify import COUNTRIES, classify_role
from collector.pipeline import record_countries
from scripts.ats_enterprise_yield import StopRedirect, retry_delay, robots_allows, robots_policy
from scripts.ats_tenant_yield import feed_source, reviewed_url
from scripts.ats_tenant_discovery import identity

PROVIDERS = ("personio-xml", "recruitee", "greenhouse", "lever")
PER_TENANT = 12
DAILY = 15000
BODY_LIMIT = 20_000_000


class RequestBudget:
    def __init__(self, remaining):
        self.remaining = remaining
        self.lock = threading.Lock()

    def charge(self):
        with self.lock:
            if self.remaining <= 0:
                raise ValueError("daily budget reached")
            self.remaining -= 1


class BoardClient:
    def __init__(self, host, budget, minimum_delay=1.0):
        self.host = host
        self.budget = budget
        self.minimum_delay = minimum_delay
        self.delay = minimum_delay
        self.last = 0.0
        self.rules = None
        self.blocked = None
        self.opener = build_opener(StopRedirect())
        self.reset()

    def reset(self):
        self.gets = self.bytes = 0
        self.started = time.monotonic()
        self.employer_names = set()

    def request(self, url, *, accept=None, robots=True):
        parsed = safe_url(url)
        if not parsed or parsed.hostname != self.host or parsed.fragment:
            raise ValueError("outside exact host scope")
        if self.blocked:
            raise ValueError(self.blocked)
        if robots:
            if self.rules is None:
                self.read_robots()
            path = parsed.path or "/"
            if parsed.query:
                path += "?" + parsed.query
            if not robots_allows(self.rules, path):
                raise ValueError("robots disallows feed")
        wait = max(0, self.delay + self.last - time.monotonic())
        if self.gets >= PER_TENANT or time.monotonic() - self.started + wait >= 45:
            raise ValueError("tenant budget reached")
        time.sleep(wait)
        self.budget.charge()
        self.last = time.monotonic()
        self.gets += 1
        headers = {"User-Agent": AGENT, "Accept": accept or "*/*", "Accept-Encoding": "identity"}
        with self.opener.open(Request(url, headers=headers), timeout=12) as response:
            if response.status != 200:
                raise ValueError("HTTP 200 required")
            body = response.read(BODY_LIMIT + 1)
            self.bytes += len(body)
            if len(body) > BODY_LIMIT:
                raise ValueError("feed byte limit")
            if not robots and b"<html" in body[:2048].lower():
                raise ValueError("robots is HTML")
            if self.host.endswith((".recruitee.com", ".personio.de", ".personio.com")) and robots:
                self.capture_name(body)
            return body, response.status, response.url

    def capture_name(self, body):
        if not self.host.endswith(".recruitee.com"):
            return
        try:
            feed = json.loads(body)
        except (UnicodeError, ValueError):
            return
        company = feed.get("company") if isinstance(feed, dict) else None
        name = company.get("name") if isinstance(company, dict) else None
        if isinstance(name, str) and 0 < len(name.strip()) <= 120:
            self.employer_names.add(name.strip())

    def read_robots(self):
        url = f"https://{self.host}/robots.txt"
        try:
            body, _, _ = self.request(url, robots=False)
        except HTTPError as error:
            if error.code != 429:
                self.blocked = f"robots HTTP {error.code}"
                error.close()
                raise ValueError(self.blocked) from error
            wait = retry_delay(error.headers.get("Retry-After"))
            error.close()
            if wait > 60:
                self.blocked = "robots HTTP 429 with Retry-After above staging budget"
                raise ValueError(self.blocked) from error
            time.sleep(wait)
            self.started = time.monotonic()
            try:
                body, _, _ = self.request(url, robots=False)
            except (OSError, ValueError) as repeated:
                self.blocked = f"robots repeated HTTP {getattr(repeated, 'code', 429)}"
                raise ValueError(self.blocked) from repeated
        rules, _, _ = robots_policy(body.decode("utf-8-sig"))
        # A published crawl delay takes precedence over the local floor.
        delays = [float(value) for key, value in rules if key == "crawl-delay" and value.replace(".", "", 1).isdigit()]
        self.delay = max([self.minimum_delay, *delays])
        self.rules = rules

    def json(self, url):
        body, _, _ = self.request(url, accept="application/json")
        return json.loads(body)


def summarize_records(records):
    europe = {}
    signals = {}
    for record in records:
        countries = sorted(set(record_countries(record)) & COUNTRIES.keys())
        if not countries:
            continue
        identifier = record["external_id"]
        europe[identifier] = countries
        role = classify_role(record["title"], record.get("text", ""), record.get("employment", ""))
        if role and role["internship_type"] == "internship":
            signals[identifier] = {"id": identifier, "countries": countries}
    return {"postings": len(records), "european_postings": len(europe),
            "countries": sorted({code for countries in europe.values() for code in countries}),
            "signals": list(signals.values())}


def measure(ats, tenant, source, client):
    client.reset()
    begin = time.monotonic()
    result = {"ats": ats, "tenant": tenant, "state": "incomplete",
              "observed_at": datetime.now(timezone.utc).isoformat()}
    try:
        result.update(summarize_records(collect(source, client)), state="feed-read",
                      names=sorted(client.employer_names))
    except HTTPError as error:
        if error.code in {403, 429}:
            client.blocked = f"feed HTTP {error.code}; host stopped"
        result["error"] = f"HTTP {error.code}"
        error.close()
    except URLError as error:
        reason = error.reason
        result["error"] = "URLError"
        result["transport"] = type(reason).__name__
    except (OSError, ValueError, TypeError, KeyError, AttributeError, SyntaxError) as error:
        result["error"] = str(error) if type(error) is ValueError else type(error).__name__
    return dict(result, get=client.gets, bytes=client.bytes,
                seconds=round(time.monotonic() - begin, 3))


def run(staging, inventory, providers, selected_host=None, stopped=None, minimum_delay=1.0):
    stopped = stopped or threading.Event()
    today = datetime.now(timezone.utc).date().isoformat()
    path = staging / "census.jsonl"
    if path.is_symlink():
        raise ValueError("staging checkpoint must not be a symlink")
    previous = [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []
    seen = {
        (row["ats"], row["tenant"]) for row in previous if row.get("error") != "daily budget reached"
    }
    budget = RequestBudget(DAILY - sum(row["get"] for row in previous
                                       if row["observed_at"].startswith(today)))
    groups = defaultdict(list)
    for row in inventory["tenants"]:
        ats, tenant = row["ats"], row["tenant"]
        if ats not in providers or (ats, tenant) in seen:
            continue
        if identity(reviewed_url(ats, tenant)) != (ats, tenant):
            raise ValueError(f"Invalid inventory identity: {ats}/{tenant}")
        source = feed_source(ats, tenant)
        host = source["allowed_hosts"][0]
        if selected_host is None or selected_host == host:
            groups[host].append((ats, tenant, source))
    write = threading.Lock()
    totals = Counter()
    blocked_providers = set()
    restrictions = defaultdict(set)
    with path.open("a", buffering=1) as out:
        def worker(item):
            host, rows = item
            client = BoardClient(host, budget, minimum_delay)
            transport_failures = 0
            for ats, tenant, source in rows:
                with write:
                    if stopped.is_set() or ats in blocked_providers or budget.remaining <= 0:
                        return
                result = measure(ats, tenant, source, client)
                with write:
                    out.write(json.dumps(result, ensure_ascii=False) + "\n")
                    totals[(ats, result["state"])] += 1
                    error = result.get("error", "")
                    if "429" in error or "403" in error:
                        restrictions[ats].add(host)
                        if len(restrictions[ats]) >= 3:
                            blocked_providers.add(ats)
                            print(f"{ats}: pausing after repeated restrictions across hosts", flush=True)
                if client.blocked:
                    return
                if result.get("error") in {"URLError", "TimeoutError"}:
                    transport_failures += 1
                    if transport_failures >= 3:
                        print(f"{host}: stopping after three transport failures", flush=True)
                        return
                else:
                    transport_failures = 0

        with ThreadPoolExecutor(max_workers=8) as pool:
            list(pool.map(worker, sorted(groups.items(), key=lambda item: -len(item[1]))))
    return {f"{ats}/{state}": count for (ats,state), count in totals.items()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", choices=PROVIDERS, action="append")
    parser.add_argument("--native-trust", action="store_true")
    parser.add_argument("--host", help="Resume only this exact feed host")
    parser.add_argument("--delay", type=float, choices=(0.5, 1.0, 2.0), default=1.0)
    args = parser.parse_args()
    if args.native_trust:
        import truststore
        truststore.inject_into_ssl()
    root = ROOT / ".staging"
    staging = root / "ats-held-census"
    if staging.resolve() != staging:
        parser.error("Staging paths must not be symlinks")
    staging.mkdir(parents=True, exist_ok=True)
    inventory = json.loads((root / "ats-tenant-discovery" / "inventory.json").read_text())
    stopped = threading.Event()
    signal.signal(signal.SIGTERM, lambda *_: stopped.set())
    signal.signal(signal.SIGINT, lambda *_: stopped.set())
    with (staging / "census.lock").open("x"):
        try:
            print(json.dumps(run(staging, inventory, args.provider or PROVIDERS, args.host, stopped, args.delay)), flush=True)
        finally:
            (staging / "census.lock").unlink()


if __name__ == "__main__":
    main()
