"""Conservative, deterministic EU27 coverage audit (no network or source activation).

Usage: python -m scripts.audit_eu27_coverage [--output path.json]

A verified vacancy in one city does not prove complete national mapping.
The full queue remains scripts/build_eu27_expansion_queue.py; this audit only
tracks observed results and makes missing national evidence explicit.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

from collector.public_sources import PUBLIC_API_ADAPTERS
from scripts.build_eu27_expansion_queue import EU27, ROOT


def parse_time(value):
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return stamp.replace(tzinfo=timezone.utc) if stamp.tzinfo is None else stamp
    except ValueError:
        return None


def active_evidence(job, catalog_time):
    """Require current, policy-v2 evidence at the catalog snapshot."""
    proof = job.get("verification") or {}
    if not isinstance(proof, dict):
        return False
    if job.get("status") != "open" or proof.get("state") != "verified" or proof.get("policy_version") != 2:
        return False
    checked = parse_time(job.get("last_verified_at") or proof.get("checked_at"))
    reference = parse_time(catalog_time)
    return bool(checked and reference and 0 <= (reference - checked).total_seconds() <= 48 * 3600)


def eligible(job, catalog_time):
    """No legacy/stale/open-by-label-only promotion."""
    return job.get("link_status") == "verified" and active_evidence(job, catalog_time)


def posting_country(job):
    """Count a posting only where its own location evidence is unambiguous."""
    declared = job.get("country")
    if declared in EU27:
        return declared
    candidates = set(job.get("countries") or [])
    return next(iter(candidates)) if len(candidates) == 1 and next(iter(candidates)) in EU27 else None


def audit(catalog, companies, sources):
    jobs = catalog.get("jobs", [])
    if not isinstance(jobs, list):
        raise ValueError("Catalog jobs must be a list")
    enabled = {s["id"] for s in sources if s.get("enabled") and isinstance(s.get("id"), str)}
    public_sources = {s["id"] for s in sources if s.get("id") in enabled
                      and s.get("active_listing_api") is True
                      and s.get("adapter") in PUBLIC_API_ADAPTERS}
    catalog_time = catalog.get("updated_at")
    rows = {country: dict(country=country, research_targets=0, enabled_research_target_sources=0,
                          seen_job_records=0, unverified_job_records=0, closed_job_records=0,
                          verified_hr_internships=0, verified_hr_working_students=0,
                          verified_hr_traineeships=0, verified_source_ids=set(),
                          direct_hr_internships=0, public_only_hr_internships=0,
                          national_mapping_complete=False,
                          completion_evidence="not-established")
            for country in EU27}
    sources_by_country = {country: set() for country in EU27}
    for company in companies:
        countries = set(company.get("target_countries") or []).intersection(rows)
        for country in countries:
            rows[country]["research_targets"] += 1
            # Being attached to an enabled source still does not establish
            # geographical job coverage, or feed completeness, in that country.
            sources_by_country[country].update(
                set(company.get("source_ids") or []).intersection(enabled))
    for country in EU27:
        rows[country]["enabled_research_target_sources"] = len(sources_by_country[country])

    seen_ids = set()
    ambiguous = 0
    for job in jobs:
        jid = job.get("id")
        if not isinstance(jid, str) or not jid or jid in seen_ids:
            raise ValueError("Catalog job IDs must be present and unique")
        seen_ids.add(jid)
        country = posting_country(job)
        if country is None:
            ambiguous += 1
            continue
        row = rows[country]
        row["seen_job_records"] += 1
        if job.get("status") == "closed":
            row["closed_job_records"] += 1
        if job.get("internship_type") == "internship":
            application = job.get("application_verification")
            if eligible(job, catalog_time) and isinstance(application, dict) and application.get("url"):
                row["direct_hr_internships"] += 1
            elif (job.get("source_id") in public_sources
                  and job.get("link_status") == "public-api-active-listing"
                  and active_evidence(job, catalog_time)
                  and job["verification"].get("policy") == "public-api-active-listing"):
                row["public_only_hr_internships"] += 1
        if not eligible(job, catalog_time):
            row["unverified_job_records"] += int(job.get("status") != "closed")
            continue
        kind = job.get("internship_type")
        field = {"internship": "verified_hr_internships",
                 "working-student": "verified_hr_working_students",
                 "traineeship": "verified_hr_traineeships"}.get(kind)
        if field:
            row[field] += 1
            if isinstance(job.get("source_id"), str):
                row["verified_source_ids"].add(job["source_id"])

    countries = []
    for country in EU27:
        row = rows[country]
        row["verified_source_ids"] = sorted(row["verified_source_ids"])
        row["has_verified_hr_internship"] = row["verified_hr_internships"] > 0
        countries.append(row)
    return dict(schema_version=1, generated_from="current-checked-in-catalog-and-registries",
                catalog_updated_at=catalog.get("updated_at"), catalog_records=len(jobs),
                unlocated_or_ambiguous_job_records=ambiguous,
                eu_country_count=len(EU27),
                countries_with_verified_hr_internships=sum(x["has_verified_hr_internship"] for x in countries),
                verified_hr_internships=sum(x["verified_hr_internships"] for x in countries),
                verified_hr_working_students=sum(x["verified_hr_working_students"] for x in countries),
                direct_hr_internships=sum(x["direct_hr_internships"] for x in countries),
                public_only_hr_internships=sum(x["public_only_hr_internships"] for x in countries),
                countries_without_direct_hr_internships=sum(not x["direct_hr_internships"] for x in countries),
                countries_without_observed_open_hr_internships=sum(
                    not (x["direct_hr_internships"] or x["public_only_hr_internships"]) for x in countries),
                nationally_complete_countries=0, countries=countries,
                limits=["Research targets are not confirmed workplaces or national mapping",
                        "An enabled source does not prove an exhaustive inventory",
                        "No source is created or activated; no network requests",
                        "Only fresh policy-v2 evidence counts toward the direct and public-only internship totals",
                        "The legacy unverified_job_records field includes active public-only listings",
                        "National completion needs an externally documented acceptance review"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    read = lambda p: json.loads((ROOT / p).read_text(encoding="utf-8"))
    result = audit(read("data/catalog.json"), read("data/companies.json"), read("data/sources.json"))
    body = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(body, encoding="utf-8")
    else:
        print(body, end="")


if __name__ == "__main__":
    main()
