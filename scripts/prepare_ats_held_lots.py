"""Create disabled ATS lots from completed, European feed observations."""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import sys
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from collector.classify import COUNTRIES
from collector.company_registry import company_key, validate_registry
from collector.daily import provision, shard_for
from scripts.ats_held_census import PROVIDERS
from scripts.ats_tenant_discovery import identity, registry_keys
from scripts.ats_tenant_yield import feed_source, reviewed_url

LOT_SIZE = 500
PREFIX = "ats-2026-11"
TERMS = {
    "greenhouse": "https://www.greenhouse.com/master-subscription-agreement",
    "lever": "https://www.lever.co/legal/terms-of-service",
    "personio-xml": "https://www.personio.com/terms/",
    "recruitee": "https://recruitee.com/terms",
}


def stable_board_id(provider, tenant):
    digest = hashlib.sha256(f"{provider}:{tenant}".encode()).hexdigest()[:20]
    return f"ats-board-{digest}"


def prior_keys(companies, sources):
    keys = set()
    for row in [*companies, *sources]:
        for field in ("career_url", "website_url", "evidence_url", "feed_url"):
            key = identity(row.get(field))
            if key:
                keys.add(key)
        ats = row.get("adapter")
        board = row.get("board")
        if ats in {"greenhouse", "lever"} and board:
            region = row.get("region") == "eu" or "eu." in row.get("api_host", "")
            keys.add((ats, ("eu/" if region else "") + board.lower()))
    return keys


def eligible(row):
    return (row.get("ats") in PROVIDERS and row.get("state") == "feed-read"
            and row.get("european_postings", 0) > 0 and row.get("countries")
            and set(row["countries"]) <= COUNTRIES.keys())


def prepare(companies, sources, observations, known=()):
    companies, sources = deepcopy(companies), deepcopy(sources)
    active_before = {entry["id"] for entry in sources if entry.get("enabled")}
    used_keys = prior_keys(companies, sources) | set(known)
    used_names = {company_key(row["name"]) for row in companies}
    used_names.update(company_key(alias) for row in companies for alias in row.get("aliases", []))
    company_ids = {c["id"] for c in companies}
    source_ids = {s["id"] for s in sources}
    counts = Counter(s["rollout_batch_id"] for s in sources if s.get("rollout_batch_id", "").startswith(PREFIX))
    stats = Counter()
    selected = sorted((r for r in observations if eligible(r)),
                      key=lambda r: (not bool(r["signals"]), r["ats"], r["tenant"]))
    for row in selected:
        provider, tenant = row["ats"], row["tenant"]
        key = provider, tenant
        if key in used_keys:
            stats[(provider, "registered")] += 1
            continue
        career = reviewed_url(provider, tenant)
        if identity(career) != key:
            raise ValueError(f"Unexpected board identity: {key}")
        names = set(row.get("names") or [])
        # Use the exact public board handle when the feed does not publish a
        # single name. The hold records that attribution is still pending.
        verified_name = next(iter(names)) if len(names) == 1 else None
        handle = tenant.split("/")[-1].split(".")[0]
        name_keys = {company_key(handle)}
        if verified_name:
            name_keys.add(company_key(verified_name))
        if used_names & name_keys:
            stats[(provider, "identity-collision")] += 1
            continue
        label = verified_name or tenant
        signal_date = datetime.fromisoformat(row["observed_at"])
        source = feed_source(provider, tenant)
        host = urlsplit(career).hostname
        hosts = set(source["allowed_hosts"]) | {host}
        if provider == "greenhouse":
            hosts.update({"boards.eu.greenhouse.io"} if tenant.startswith("eu/") else {"boards.greenhouse.io"})
        board_id = stable_board_id(provider, tenant)
        sid = f"{board_id}-source"
        if board_id in company_ids or sid in source_ids:
            raise ValueError(f"Registry ID collision: {board_id}")
        lot = 1
        while counts[f"{PREFIX}-{lot:02}"] >= LOT_SIZE:
            lot += 1
        batch = f"{PREFIX}-{lot:02}"
        evidence = source.get("feed_url") or career
        source.update(id=sid, company_id=board_id, employer=label, enabled=False,
                      career_url=career, allowed_hosts=sorted(hosts),
                      target_countries=sorted(set(row["countries"])), rollout_batch_id=batch,
                      status="pending-ats-rollout-approval", reviewed_on=signal_date.date().isoformat(),
                      permission_basis="Observed public board feed with HTTP 200 robots and allowed feed path; GET only",
                      documentation_url=TERMS[provider],
                      review_notes="Staging feed shows European postings; board identity and vacancy proof must be reconciled before rollout.",
                      employer_name_evidence="feed-company-name" if verified_name else "board-handle-only",
                      last_hr_signal_at=row["observed_at"] if row["signals"] else None,
                      observed_hr_signals=len(row["signals"]), max_requests=12, collection_seconds=45)
        # Board host without a slug is not a distinct employer identity on shared ATSs.
        if provider in {"personio-xml", "recruitee"}:
            source.pop("board", None)
        if provider != "lever":
            source.pop("region", None)
        sources.append(source)
        companies.append(dict(id=board_id, name=label, career_url=career, evidence_url=evidence,
                              source_ids=[sid], target_countries=source["target_countries"], workplaces=[],
                              rollout_batch_id=batch, collection_activation_hold=True,
                              employer_name_evidence=source["employer_name_evidence"]))
        counts[batch] += 1
        used_keys.add(key)
        used_names.update(name_keys)
        company_ids.add(board_id)
        source_ids.add(sid)
        stats[(provider, "prepared")] += 1
    if provision(companies, sources) != (companies, sources):
        raise ValueError("Provisioning would change the prepared registry")
    if {entry["id"] for entry in sources if entry.get("enabled")} != active_before:
        raise ValueError("Active source IDs changed")
    return companies, sources, {f"{ats}/{state}": count for (ats, state), count in stats.items()}


def simulate_selection(companies, sources, lot, stamp):
    """Exercise the existing provisioning selection on copies only."""
    companies, sources = deepcopy(companies), deepcopy(sources)
    original = {source["id"] for source in sources if source.get("enabled")}
    members = {source["company_id"] for source in sources if source.get("rollout_batch_id") == lot}
    for row in companies:
        if row["id"] in members:
            if row.get("collection_activation_hold") is not True:
                raise ValueError("Expected held employer")
            row["collection_activation_hold"] = False
    for row in sources:
        if row.get("rollout_batch_id") == lot:
            if row.get("enabled") is not False:
                raise ValueError("Expected disabled source")
            row["enabled"] = True
    if provision(companies, sources) != (companies, sources):
        raise ValueError("Simulation auto-provisioned a source")
    selected = [row for row in sources if row.get("enabled") and row["id"] not in original]
    fresh = stamp - timedelta(days=60)
    daily = [r for r in selected if r.get("last_hr_signal_at") and fresh <= datetime.fromisoformat(r["last_hr_signal_at"]) <= stamp]
    daily_ids = {r["id"] for r in daily}
    weekly = [r for r in selected if r["id"] not in daily_ids]
    # A stable hash spreads weekly work across cycles and preserves existing shards.
    cycles = [daily + [r for r in weekly if shard_for(r["id"], 7) == day] for day in range(7)]
    max_cycle = max(map(len, cycles))
    max_shard = max((max(Counter(shard_for(r["id"], 16) for r in cycle).values(), default=0)
                     for cycle in cycles), default=0)
    return {"selected": len(selected), "daily": len(daily), "weekly": len(weekly),
            "max_sources_per_cycle": max_cycle,
            "max_logical_get_per_cycle": 12 * max_cycle,
            "largest_shard_per_cycle": max_shard,
            "largest_shard_if_all_selected": max(Counter(shard_for(r["id"], 16) for r in selected).values(), default=0),
            "observed_signals": sum(r["observed_hr_signals"] for r in selected)}


def replay_without_new_proof(catalog, sources, coverage, output):
    from collector.pipeline import finalize

    registry = deepcopy(sources)
    selected = [row for row in registry if row.get("rollout_batch_id") == f"{PREFIX}-01"]
    for row in selected:
        row["enabled"] = True
    output.mkdir(parents=True, exist_ok=True)
    if output.resolve() != output:
        raise ValueError("Replay output must not be a symlink")
    result, _ = finalize(registry, selected, deepcopy(catalog), coverage, [],
                         catalog["last_attempt_at"], output)
    before = {row["id"] for row in catalog["jobs"]}
    after = {row["id"] for row in result["jobs"]}
    if before != after or len(after) != len(result["jobs"]):
        raise ValueError("Replay changed the canonical ID set or introduced a duplicate")
    return {"ids_before": len(before), "ids_after": len(after), "ids_lost": len(before - after)}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--apply", action="store_true", help="Write held registries on the current branch")
    p.add_argument("--replay", action="store_true", help="Run the catalog replay in staging")
    args = p.parse_args()
    staging = ROOT / ".staging" / "ats-held-census"
    if staging.resolve() != staging:
        p.error("Staging must not be a symlink")
    if args.apply and (staging / "census.lock").exists():
        p.error("Wait until the census writer has stopped before applying registry changes")
    with (staging / "census.jsonl").open() as stream:
        latest = {}
        for line in stream:
            if line.endswith("\n"):
                row = json.loads(line)
                latest[row["ats"], row["tenant"]] = row
    registry_paths = [ROOT / "data" / f"{table}.json" for table in ("companies", "sources")]
    originals = [json.loads(path.read_text()) for path in registry_paths]
    companies, sources, stats = prepare(*originals, latest.values(), known=registry_keys(ROOT))
    validate_registry(companies, json.loads((ROOT / "data/geography.json").read_text()), sources)
    result = {"changes": stats, "batches": {}, "simulated_lot_1": simulate_selection(
        companies, sources, f"{PREFIX}-01", datetime.now(timezone.utc))}
    result["batches"] = dict(Counter(s["rollout_batch_id"] for s in sources if s.get("rollout_batch_id")))
    if args.replay:
        result["catalog_replay"] = replay_without_new_proof(
            json.loads((ROOT / "data/catalog.json").read_text()), sources,
            json.loads((ROOT / "data/coverage.json").read_text()), staging / "simulation")
    if args.apply:
        payloads = [json.dumps(rows, ensure_ascii=False, indent=2) + "\n" for rows in (companies, sources)]
        temporary_paths = []
        try:
            for path, payload in zip(registry_paths, payloads):
                temporary = path.with_suffix(".tmp")
                with temporary.open("x") as stream:
                    temporary_paths.append(temporary)
                    stream.write(payload)
            for temporary, path in zip(temporary_paths, registry_paths):
                temporary.replace(path)
        finally:
            for temporary in temporary_paths:
                temporary.unlink(missing_ok=True)
    (staging / "lot-summary.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
