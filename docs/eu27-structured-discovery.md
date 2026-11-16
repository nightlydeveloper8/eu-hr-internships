# People Placement — EU27 structured discovery: JobTech and EURES input

**Date:** 2026-11-16. This is a proposed, opt-in integration in a separate PR,
not an activated daily collection source.

## Design

Build a small common normalizer for public vacancy feeds: stable IDs, employer,
title, country, official posting URL and, when present, application URL. Use the
project's existing multilingual HR placement classifier. Output a **discovery
review queue**, never directly publish records as confirmed internships.

Only the existing policy-v2 pipeline can verify a vacancy: source ownership,
current employer page and same-vacancy application proof, workplace and
freshness. The input feed is NOT that proof.

## Swedish JobTech: usable public open data

Arbetsförmedlingen provides a documented CC0, public JobSearch API without
account or API key. Official documentation:

- https://data.arbetsformedlingen.se/dataservice/jobsearch/
- https://data.arbetsformedlingen.se/dataset/job-ads/
- https://gitlab.com/arbetsformedlingen/job-ads/jobsearch-apis/-/blob/main/docs/GettingStartedJobSearchEN.md

Run a bounded, explicit pilot on a network-enabled runner:

    python -m scripts.official_feed_discovery --provider jobtech-se --live --per-query 12 --output /tmp/se-review.json

The program makes three Swedish-language searches, first page only, with
at most 40 hits/query, 120 observed records, 12 requests including robots
checks, and a 65-second logical budget. It checks robots at runtime, uses
a host-bound redirect scope, and never renders pages, signs in or submits
applications. Output contains only small metadata and no full description.

## EURES: same parser contract, no unapproved scraping

EURES's job-search service places specific conditions on extracting vacancy
data for further processing and reserves API extraction for recognised partners:

https://europa.eu/eures/portal/jv-se/home?lang=en

A link back to EURES does not negate the separate extraction restriction.
Legal exceptions for research require an independent assessment; an operator's
assertion does not itself establish an authorization.

A recognised, authorised upstream may supply a normalized JSON array:

    [
      {
        "id": "EURES-123",
        "title": "HR Internship",
        "employer": "Example Employer",
        "country": "NL",
        "city": "Utrecht",
        "url": "https://europa.eu/eures/portal/jv-se/jv-details/EURES-123",
        "description": "HR placement work",
        "published_at": "2026-11-16"
      }
    ]

Import requires an explicit JSON evidence file with source=eures, a grant
reference, granting authority, approved use, valid HTTPS document URL, future
valid_until and permits_vacancy_extraction_and_indexing=true. These checks
validate evidence metadata, NOT its legal authenticity or sufficiency.

    python -m scripts.official_feed_discovery --provider eures-authorized-input --input /tmp/eures-authorised.json --authorization /tmp/eures-permission.json --output /tmp/eures-review.json

The EURES importer does not request EURES pages or API endpoints, and never
stores the full input description. No valid grant has been asserted here.

## Measured, not assumed

- Requests actually executed for this implementation: 0 external feed GETs.
- New production sources enabled: 0. New verified internships: 0.
- The Swedish pilot has **not** been run live in the current environment.
  Its number of matches, bytes and wall time remain unknown.
- The EU baseline at 2026-11-16 19:26 UTC: 362 catalog records, 27 verified
  HR internship entries plus one verified working student; 13/27 countries
  have catalog records, 5/27 have verified HR internships.
- No change to active schedules, company/source registry, catalog or policy v2.

## Remaining to make the new feed part of verified production inventory

1. Execute the JobTech pilot, record requests, bytes, candidates and dedup,
   plus official employer ownership and per-country work locations.
2. Reconcile only accepted candidates against employer-declared official ATS
   sources, then feed them through the existing vacancy/application verifier.
3. Measure actual unique and candidable new internships and costs over two
   ordinary cycles before proposing activation.
4. For EURES, obtain and verify applicable extraction authorization or use a
   source that independently licenses vacancy metadata; do not run extraction
   through an API that restricts it to approved partners.
5. Extend this identical normalization interface to other countries'
   independently licensed employment-service feeds, rather than adding more
   low-yield generic crawlers.
