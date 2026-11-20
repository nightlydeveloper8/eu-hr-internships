"""Group current public HR internship records without treating an employer/city match as an identity."""
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit


def groups(catalog, registry):
    enabled = {s["id"] for s in registry if s.get("enabled") and s.get("active_listing_api")
               and s.get("adapter") in {"eures-search", "jobtech-search"}}
    stamp = datetime.fromisoformat(catalog["updated_at"])
    grouped = defaultdict(set)
    for j in catalog["jobs"]:
        proof = j.get("verification") or {}
        if (j.get("country") not in {"IT", "CH", "SE"} or j.get("source_id") not in enabled
                or j.get("status") != "open" or j.get("internship_type") != "internship"
                or j.get("link_status") != "public-api-active-listing" or proof.get("state") != "verified"
                or proof.get("policy_version") != 2 or proof.get("policy") != "public-api-active-listing"):
            continue
        checked = j.get("last_verified_at") or proof.get("checked_at")
        if not checked or not 0 <= (stamp - datetime.fromisoformat(checked)).total_seconds() <= 48 * 3600:
            continue
        channel = urlsplit(j.get("external_application_url") or j["url"]).hostname
        grouped[(j["country"], j["employer"], j["city"], channel)].add(j["id"])
    return [dict(country=k[0], employer=k[1], city=k[2], platform=k[3], ids=sorted(ids))
            for k, ids in sorted(grouped.items())]


if __name__ == "__main__":
    data = Path(__file__).resolve().parents[1] / "data"
    print(json.dumps(groups(json.loads((data / "catalog.json").read_text()),
                            json.loads((data / "sources.json").read_text())), ensure_ascii=False, indent=2))
