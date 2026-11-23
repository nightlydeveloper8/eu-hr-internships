"""Enumerate ATS board identities from the Common Crawl columnar index, entirely in staging."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import random
import re
import sys
import time
from urllib.parse import parse_qs

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from collector.ats_channel_discovery import TOKEN, _registered_keys, identify_channel, safe_url

HOST_RULES = {
    "teamtailor": ("teamtailor.com",),
    "inrecruiting": ("intervieweb.it",),
    "softgarden": ("softgarden.io", "softgarden.de"),
    "factorial": ("factorialhr.com",),
    "altamira": ("altamiraweb.com",),
    "bizneo": ("bizneo.com",),
    "talentclue": ("talentclue.com",),
    "varbi": ("varbi.com",),
    "erecruiter": ("erecruiter.net", "bewerberportal.at", "kandidatenportal.eu"),
}
PATH_RULES = {
    "apply.workable.com": "workable",
    "emp.jobylon.com": "jobylon",
    "careers.talentclue.com": "talentclue",
    "www.welcometothejungle.com": "welcome-to-the-jungle",
    "app.welcometothejungle.com": "welcome-to-the-jungle",
}
QUERIES = {
    "recruitee": ("recruitee.com",),
    "personio-xml": ("jobs.personio.de", "jobs.personio.com"),
    "lever": ("jobs.lever.co", "jobs.eu.lever.co"),
    "greenhouse": ("boards.greenhouse.io", "job-boards.greenhouse.io", "boards.eu.greenhouse.io", "job-boards.eu.greenhouse.io"),
    "talentech": ("candidate.hr-manager.net",),
    **HOST_RULES,
}
for host, provider in PATH_RULES.items():
    QUERIES[provider] = (*QUERIES.get(provider, ()), host)

RESERVED = set("www app api help support blog careers jobs admin login embed static cdn assets"
               " demo test status apply search signin auth docs resources privacy legal welcome j preproduction example preview media internal apidoc".split())


def identity(raw):
    url = safe_url(raw)
    if url is None:
        return None
    host = url.hostname
    parts = url.path.strip("/").split("/")
    existing = identify_channel(raw)
    if host == "job-boards.eu.greenhouse.io":
        existing = identify_channel(raw.replace(host, "boards.eu.greenhouse.io", 1))
    if existing and existing["adapter"] in {"recruitee", "personio-xml", "greenhouse", "lever"}:
        provider = existing["adapter"]
        tenant = existing["tenant"]
        if tenant.split(".")[0] in RESERVED:
            return None
        # Regional boards may be independently administered.
        if host in {"boards.eu.greenhouse.io", "job-boards.eu.greenhouse.io", "jobs.eu.lever.co"}:
            tenant = "eu/" + tenant
        return provider, tenant
    if host == "candidate.hr-manager.net" and url.path.lower() == "/applicationinit.aspx":
        params = parse_qs(url.query, max_num_fields=30) if url.query.count("&") < 30 else {}
        cid = params.get("cid", [])
        if len(cid) == 1 and re.fullmatch(r"[0-9]{1,12}", cid[0]):
            return "talentech", str(int(cid[0]))
    if host in PATH_RULES:
        provider = PATH_RULES[host]
        if provider == "talentclue":
            if len(parts) >= 4 and parts[1] == "group" and parts[2].isdigit() and parts[3] == "offers":
                return provider, "group/" + str(int(parts[2]))
            return None
        if provider == "jobylon":
            if len(parts) >= 2 and parts[0] == "companies" and re.fullmatch(r"[0-9]{1,12}", parts[1]):
                return provider, str(int(parts[1]))
            return None
        if provider == "welcome-to-the-jungle":
            if len(parts) >= 2 and parts[0] == "companies":
                parts = parts[1:]
            elif len(parts) >= 3 and parts[1] == "companies":
                parts = parts[2:]
            else:
                return None
        if TOKEN.fullmatch(parts[0]) and parts[0].lower() not in RESERVED:
            return provider, parts[0].lower()
    for provider, domains in HOST_RULES.items():
        for domain in domains:
            label, separator, suffix = host.partition(".")
            if (not separator or suffix != domain or not TOKEN.fullmatch(label)
                    or (label in RESERVED and not (provider == "erecruiter" and label == "jobs"))
                    or re.search(r"(^|[-_])(test|demo|sandbox|preview)([-_0-9]|$)", label)):
                continue
            # Require a recognizable public career route for broad corporate domains.
            if provider in {"altamira", "bizneo"}:
                if parts[0].lower() not in {"careers", "jobs", "career", "vacancies", "trabaja-con-nosotros"}:
                    continue
            if provider == "erecruiter" and not set(map(str.lower, parts[:2])) & {"job", "jobs"}:
                continue
            if provider == "inrecruiting":
                if len(parts) >= 3 and parts[2].lower() == "career" and TOKEN.fullmatch(parts[0]):
                    return provider, host + "/" + parts[0].lower()
                if (len(parts) >= 2 and len(parts[0]) == 2 and parts[1].lower() == "career"):
                    return provider, host
                if parts[0].lower() not in {"job", "jobs"}:
                    continue
            return provider, host
    return None


def registry_keys(root):
    keys = set()
    for table, fields in {
        "companies": ("career_url", "website_url", "evidence_url"),
        "sources": ("career_url", "feed_url", "url"),
    }.items():
        document = json.loads((root / "data" / f"{table}.json").read_text())
        for entry in document[table] if isinstance(document, dict) else document:
            explicit = set()
            for field in fields:
                key = identity(entry.get(field))
                if key:
                    explicit.add(key)
            keys.update(explicit)
            if entry.get("adapter") == "workable-public" and TOKEN.fullmatch(entry.get("board", "")):
                keys.add(("workable", entry["board"].lower()))
            for raw in _registered_keys(entry):
                provider, tenant = raw.split(":", 1)
                if not any(provider == item[0] for item in explicit):
                    keys.add((provider, tenant))
    return keys


def surt(host, subdomains=False):
    key = ",".join(reversed(host.split(".")))
    return key + ("," if subdomains else ")/")


def prefixes(provider, host):
    if provider == "jobylon":
        return [surt(host) + "companies/"]
    if provider == "talentclue" and host in PATH_RULES:
        return [surt(host) + locale + "/group/" for locale in ("es", "en", "ca")]
    if provider == "talentech":
        return [surt(host) + "applicationinit.aspx"]
    if provider == "welcome-to-the-jungle":
        return [surt(host) + route for route in (
            "companies/", "en/companies/", "fr/companies/", "cs/companies/", "sk/companies/",
            "es/companies/", "de/companies/",
        )]
    return [surt(host, host not in PATH_RULES and (provider in HOST_RULES
                                                  or provider in {"recruitee", "personio-xml"}))]


def sample(rows, seed):
    groups = defaultdict(lambda: defaultdict(list))
    for row in rows:
        if not row["registered"]:
            stratum = "multiple-crawls" if len(row.get("crawls", [])) > 1 else "one-crawl"
            groups[row["ats"]][stratum].append(row["tenant"])
    result = {}
    for provider, strata in sorted(groups.items()):
        total = sum(map(len, strata.values()))
        limit = min(300, total)
        result[provider] = []
        remaining = limit
        remaining_population = total
        ordered = sorted(strata.items())
        for index, (stratum, members) in enumerate(ordered):
            population = len(members)
            count = remaining if index == len(ordered) - 1 else min(
                population, remaining - 1, max(1, round(limit * population / total))
            )
            count = max(count, remaining - (remaining_population - population))
            picked = random.Random(f"{seed}:{provider}:{stratum}").sample(sorted(members), count)
            result[provider].extend({"tenant": tenant, "stratum": stratum, "population": population}
                                    for tenant in picked)
            remaining -= count
            remaining_population -= population
    return result


def inspect_partitions(index, crawls, staging):
    cache = staging / "bounds.jsonl"
    rows = {}
    if cache.is_symlink():
        raise ValueError("Metadata cache must not be a symlink")
    if cache.exists():
        for line in cache.read_text().splitlines():
            item = json.loads(line)
            if "bounds" in item:
                rows[item["path"]] = item
    by_crawl = {}
    with cache.open("a", buffering=1) as stream:
        for crawl in crawls:
            by_crawl[crawl] = []
            for path in index.partitions(crawl):
                if path not in rows:
                    try:
                        rows[path] = {"path": path, "bounds": index.bounds(path), "event": index.events[-1]}
                    except Exception as error:
                        rows[path] = {"path": path, "error": str(error), "event": index.events[-1]}
                    stream.write(json.dumps(rows[path]) + "\n")
                by_crawl[crawl].append(rows[path])
    return by_crawl


def enumerate_partitions(index, partitions, providers):
    from scripts.ats_columnar_index import overlaps

    seen = defaultdict(set)
    queries = []
    for crawl, files in partitions.items():
        for provider in providers:
            matches = set()
            failures = sum("error" in row for row in files)
            for host in QUERIES[provider]:
                for prefix in prefixes(provider, host):
                    for row in files:
                        if "bounds" not in row or not overlaps(row["bounds"], prefix):
                            continue
                        selection = (row["path"], prefix)
                        matches.add(selection)
            for path, prefix in sorted(matches):
                try:
                    for url, _ in index.urls(path, prefix, provider):
                        key = identity(url)
                        if key and key[0] == provider:
                            seen[key].add(crawl)
                except Exception as error:
                    failures += 1
                    print(f"{crawl} {provider}: {error}", file=sys.stderr, flush=True)
            queries.append({"crawl": crawl, "ats": provider, "selected_ranges": len(matches),
                            "failures": failures, "complete": not failures})
    return seen, queries


def main():
    from scripts.ats_columnar_index import ColumnarIndex

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", choices=sorted(QUERIES), action="append")
    parser.add_argument("--crawl", action="append", help="Default: latest three in collinfo.json")
    parser.add_argument("--seed", default="2026-11-23")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    registered = registry_keys(root)
    output = root / ".staging" / "ats-tenant-discovery"
    output.mkdir(parents=True, exist_ok=True)
    if output.resolve() != output:
        parser.error("Staging directory must not be a symlink")
    index = ColumnarIndex(output)
    crawls = args.crawl or index.recent()
    if not 1 <= len(set(crawls)) == len(crawls) <= 3 or any(
        not re.fullmatch(r"CC-MAIN-\d{4}-\d{2}", crawl) for crawl in crawls
    ):
        parser.error("Select up to three distinct Common Crawl IDs")
    providers = sorted(set(args.provider or QUERIES))
    started = time.monotonic()
    partitions = inspect_partitions(index, crawls, output)
    seen, queries = enumerate_partitions(index, partitions, providers)
    rows = [{"ats": provider, "tenant": tenant, "registered": (provider, tenant) in registered,
             "country": "sconosciuto", "crawls": sorted(sightings)}
            for (provider, tenant), sightings in sorted(seen.items())]
    totals = Counter(row["ats"] for row in rows)
    known = Counter(row["ats"] for row in rows if row["registered"])
    reference = Counter(provider for provider, _ in registered)
    summary = {provider: {"observed": totals[provider], "registered": known[provider],
                          "new": totals[provider] - known[provider], "registry_reference": reference[provider],
                          "complete": all(q["complete"] for q in queries if q["ats"] == provider)}
               for provider in providers}
    metadata = [row["event"] for files in partitions.values() for row in files]
    result = {"summary": summary, "crawls": crawls, "queries": queries,
              "requests": [event for event in index.events if event["type"] != "metadata"],
              "metadata": metadata, "wall_seconds": round(time.monotonic() - started, 3),
              "tenants": rows, "sample_seed": args.seed, "sample": sample(rows, args.seed)}
    path = output / "inventory.json"
    temporary = path.with_suffix(".tmp")
    with temporary.open("x") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    temporary.replace(path)
    print(json.dumps(summary), flush=True)


if __name__ == "__main__":
    main()
