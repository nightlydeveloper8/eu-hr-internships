# People Placement — EU27 structured discovery: JobTech and EURES input

## November 16 live outcome: application verification and second-country schema

Read-only ATS verification is now implemented in
\`collector/official_feed_verification.py\` and exposed through
\`scripts/verify_official_feed_candidates.py\`. The shared JobTech parser
produces candidates; the second pass reads *only* exact feed-published
application URLs on explicit preflight host allowlists. It reuses the
project's no-browser \`_verify_vacancy()\` (policy v2), adds strict enabled
applicant-form checks, and requires an independently observed company-name
signal before recording employer ownership evidence. One observed same-host
privacy/legal link is allowed per candidate, with no guessed policy URLs.

The latest [CI preflight #43964714978](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/43964714978)
performed 5 ATS GETs (including robots), 0 renderings, and reported:

- Jobandtalent Sweden AB — JobTech 31558200: exact current job title,
  enabled same-vacancy application form and company legal name on a privacy
  page linked from the same recruiting host. State:
  \`same-vacancy-form-and-owner-evidence\`. **Not in public catalog**.
- Splendor Plant — JobTech 31613684: public feed adds academic semester
  \`VT27\` to the employer's current title; a strict, single-token
  seasonal variant diagnostic identifies this *without* changing policy
  v2's exact-title gate. Initial employer page did not expose an enabled
  applicant form. State: \`seasonal-title-variant-no-enabled-form\`.
  **Not verified.**

Neither stage has been promoted, and no applicant data were submitted.
This is a PR-only preflight, not a successful daily catalog integration.

**Czech extension:** The public MPSV/Úřad práce nationwide vacancies
dataset is published daily and its catalog identifies no copyright/database
right restriction, but notes the presence of personal data. The official
daily JSON schema is
https://data.mpsv.cz/od/soubory/volna-mista-prirustek/volna-mista-prirustek.schema.json .
The common normalizer now supports a **bounded offline \`mpsv-cz\` input**:
stable \`portalId\`, occupation, organization, candidate employer vacancy URL,
country and publication date. Applicant contacts, telephone numbers, email
addresses, workplace addresses and full text are **not** retained; generic
company homepages and expired records are rejected. No MPSV live read or
Czech vacancy verification has occurred.

Run a bounded, operator-provided permitted JSON sample only:

    python -m scripts.official_feed_discovery \
      --provider mpsv-cz --input /tmp/selected-mpsv-rows.json \
      --output /tmp/cz-review.json

The EU27 access/readiness evidence matrix is saved in
\`docs/eu27-public-feed-readiness.json\`, with 27 countries and explicit
unknowns. It is not a claim that 27 public feeds are available.


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

- Requests actually executed in two PR preflights: 8 HTTP requests; zero EURES GETs.
- New production sources enabled: 0. New verified internships: 0.
- The official public feed pilot **has now run twice** in PR-specific GitHub Actions:
  https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/43960047644
  and https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/43960318146
  Each inspected 30 hits via 4 HTTP requests with zero renders and returned
  2 distinct candidate internships from 2 employers. Run 1: 324,016 bytes
  and 5.977 seconds; run 2: 324,021 bytes and 6.837 seconds.
  Candidate IDs were 31558200 (Jobandtalent Sweden AB, HR & recruiting
  internship Malmö) and 31613684 (Splendor Plant Aktiebolag, HR praktik).
  Both carry source-published job-specific application URLs, which are
  unverified until employer ownership, same-vacancy application and freshness
  satisfy policy v2. No new verified opportunities. These metrics reflect
  only the fixed three-query pilot, NOT an exhaustive Sweden inventory.
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
