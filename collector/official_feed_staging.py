"""Fail-closed bridge from a *fresh* JobTech policy-v2 dossier to staging finalize.

This is NOT a daily adapter. It does not register, enable or publish sources.
Only a newly read employer/ATS dossier may yield an in-memory observation;
any doubt yields no job and can never count absence as proof of closure.
"""
from datetime import datetime, timezone
from urllib.parse import urlsplit

from .classify import (
    advertisement_language, classify_role, extract_metadata, fold,
    language_summary, plain, stable_id, workplace_languages,
)
from .official_feed_discovery import https_url
from .official_feed_policy_dossier import ats_parent, catalog_overlap, review


def _utc(value):
    if not isinstance(value, str):
        raise ValueError("Dossier timestamp missing")
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError("Dossier timestamp lacks timezone")
    return dt.astimezone(timezone.utc)


def staging_part(candidate, dossier, source, stamp, prior_jobs=()):
    """Create a normal finalize-compatible part; no file I/O and no network.

    A partial single-candidate inventory must NEVER authorize closure by absence.
    """
    sid = source.get("id", "")
    report = dict(id=sid, employer=source.get("employer", ""),
                  adapter="jobtech-policy-v2-staging", checked_at=stamp,
                  status="partial", complete=False, closure_complete=False,
                  records_inspected=0, matching=0, source_enabled=False,
                  policy_v2_staging=True, page_failures=0)
    result = dict(report=report, jobs=[], closure_eligible=[])
    try:
        if not sid or source.get("enabled") is not False or source.get("staging_only") is not True:
            raise ValueError("Only an explicitly disabled staging source is allowed")
        if source.get("ownership_scope") != "reviewed-hosts" or source.get("require_employer_identity") is not True:
            raise ValueError("Strict employer ownership scope is required")
        hosts = source.get("allowed_hosts")
        if not isinstance(hosts, list) or len(hosts) != 1 or not isinstance(hosts[0], str):
            raise ValueError("One exact approved ATS host is required")
        host = hosts[0]
        inventory = https_url(source.get("reviewed_inventory_url"), {host})
        if not inventory:
            raise ValueError("Reviewed inventory URL must be on the approved ATS host")
        if not isinstance(candidate, dict) or not isinstance(dossier, dict):
            raise ValueError("Candidate and live dossier required")
        if candidate.get("provider") != "jobtech-se" or candidate.get("country") != "SE":
            raise ValueError("Only reviewed Swedish JobTech candidates supported")
        if candidate.get("verification_state") != "unverified" or not candidate.get("workplace_country_evidence"):
            raise ValueError("JobTech candidate lacks required country or staging status")
        employer = plain(candidate.get("employer"))
        title = plain(candidate.get("title"))
        city = plain(candidate.get("city"))
        if not employer or not city or not title or fold(employer) != fold(plain(source.get("employer"))):
            raise ValueError("Exact candidate employer, title and city are required")
        role = classify_role(title)
        if not role or role["internship_type"] != "internship":
            raise ValueError("Title does not establish an HR internship")
        parent = ats_parent(candidate.get("apply_url"), host)
        if not parent:
            raise ValueError("Observed ATS application identifier missing")
        expected = dict(
            provider="jobtech-se", public_id=candidate.get("provider_id"),
            employer=employer, country="SE", city=city, title=title,
            source_job_url=candidate.get("url"), ats_job_url=parent["job_page"],
            application_url=parent["application_url"],
            ats_posting_id=parent["ats_id"], reviewed_inventory_url=inventory,
        )
        if any(fold(plain(dossier.get(key))) != fold(plain(value))
               for key, value in expected.items()):
            raise ValueError("Live dossier identity, workplace, or provenance disagrees with feed")
        if dossier.get("status") != "policy-v2-evidence-passed-staging-only":
            raise ValueError("Current employer policy-v2 dossier is not positive")
        for key in ("official_inventory_confirmed", "employer_city_match",
                    "internship_role_match", "job_identity_match"):
            if dossier.get(key) is not True:
                raise ValueError("Required employer, inventory or form proof absent: " + key)
        if dossier.get("application_preflight") != "same-vacancy-form-and-owner-evidence":
            raise ValueError("Independent employer identity and applicant form not proven")
        if dossier.get("owner_evidence") != "same-host-legal-page-names-employer":
            raise ValueError("Exact legal-employer provenance not proven")
        if dossier.get("application_proof_method") not in (
            "linked-same-vacancy-applicant-form",
            "public-feed-same-ATS-id-current-employer-CTA-and-enabled-form",
        ):
            raise ValueError("No supported observed same-vacancy applicant form")
        if dossier.get("catalogue_entry_created") is not False or dossier.get("production_activated") is not False:
            raise ValueError("Dossier is not isolated from production")
        age = (_utc(stamp) - _utc(dossier.get("checked_at"))).total_seconds()
        if age < 0 or age > 1800:
            raise ValueError("Dossier must be fresh and from this bounded staging cycle")
        job_id = stable_id(sid, parent["ats_id"])
        overlap = catalog_overlap(candidate, dossier, list(prior_jobs))
        if overlap["possible_mirror_count"] or any(
            match.get("id") != job_id for match in overlap["exact_matches"]
        ):
            raise ValueError("Unresolved catalog mirror or different official identity")
        langs = workplace_languages(title)
        method = dossier["application_proof_method"]
        job = dict(
            id=job_id, external_id=parent["ats_id"], source_id=sid,
            source_name=employer, source_type="jobtech-policy-v2-staging",
            source_posting_id=parent["ats_id"], employer=employer, title=title,
            country="SE", countries=["SE"], city=city,
            url=parent["job_page"], apply_url=parent["application_url"],
            **role, advertisement_language=advertisement_language(title),
            workplace_languages=langs, language_requirements=language_summary(title, langs),
            language_confidence="confirmed" if langs else "unspecified",
            **extract_metadata(title), published_at=candidate.get("published_at"),
            valid_through=None, first_discovered_at=stamp, last_seen_at=stamp,
            last_verified_at=stamp, link_status="verified",
            verification=dict(state="verified", checked_at=stamp,
                              policy_version=2, reason=method),
            application_verification=dict(
                url=parent["application_url"], method=method,
                vacancy_match="title", inventory="reviewed-employer-public-job-page",
                checked_at=stamp),
            official_feed_provenance=dict(provider="jobtech-se",
                                          public_id=candidate["provider_id"],
                                          ats_id=parent["ats_id"]),
            status="open",
        )
        report.update(records_inspected=1, matching=1, verification_states={"verified": 1},
                      candidate_filter_reasons={}, page_failures=0,
                      reviewed_ats_id=parent["ats_id"],
                      preexisting_exact_matches=overlap["exact_url_or_path_count"])
        result["jobs"] = [job]
    except (ValueError, TypeError, KeyError, AttributeError) as exc:
        report.update(status="partial", verification_states={"incomplete": 1},
                      reason=str(exc)[:200], page_failures=1)
    return result


def stage_live_candidate(candidate, source, prior_jobs=(), client_factory=None):
    """Run a *new* bounded ATS review first; then stage only that live proof."""
    kwargs = dict(approved_host=source["allowed_hosts"][0],
                  approved_inventory_url=source["reviewed_inventory_url"])
    if client_factory is not None:
        kwargs["client_factory"] = client_factory
    dossier = review(candidate, **kwargs)
    # The collection timestamp must not precede the final live ATS proof.
    stamp = datetime.now(timezone.utc).isoformat()
    return staging_part(candidate, dossier, source, stamp, prior_jobs), dossier
