"""Run the reviewed, unregistered JKS source against a temporary catalog."""
from copy import deepcopy
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from collector.jks import SOURCE
from collector.pipeline import ROOT, finalize, now, process_source, read
from collector.runtime import BudgetClient
from collector.verification import verified_job


def preview():
    registry = read(ROOT / "data/sources.json", [])
    if any(s["id"] == SOURCE["id"] for s in registry) or SOURCE["enabled"]:
        raise ValueError("Expected unregistered staging source")
    catalog = read(ROOT / "data/catalog.json", {})
    source = deepcopy(SOURCE)
    client = BudgetClient(seconds=source["collection_seconds"], max_requests=source["max_requests"], delay=1)
    stamp = now()
    part = process_source(source, client, stamp)
    if part["closure_eligible"]:
        raise ValueError("Partial inventory cannot close postings")
    before = {j["id"] for j in catalog["jobs"]}
    with TemporaryDirectory() as directory:
        staged, _ = finalize([*registry, source], [source], catalog, {}, [part], stamp, Path(directory))
        again, _ = finalize([*registry, source], [source], deepcopy(staged), {}, [part], stamp, Path(directory))
    after = {j["id"] for j in staged["jobs"]}
    if not before <= after or len(after) != len(staged["jobs"]) or sorted(after) != sorted(j["id"] for j in again["jobs"]):
        raise ValueError("Catalog identity regression")
    proofs = [dict(id=j["id"], project=j["source_posting_id"], title=j["title"], city=j["city"],
                   url=j["url"], application=j["application_verification"]["url"]) for j in staged["jobs"]
              if j["source_id"] == source["id"] and j.get("country") == "DK" and j["internship_type"] == "internship"
              and verified_job(j, stamp) and (j.get("application_verification") or {}).get("method") == "jks-talentech-same-project-form"]
    return dict(proofs=proofs, ids_before=len(before), ids_after=len(after), report=part["report"],
                requests=client.requests, bytes=client.bytes, stamp=stamp)


if __name__ == "__main__":
    print(json.dumps(preview(), ensure_ascii=False))
