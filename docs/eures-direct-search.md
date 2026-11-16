# EURES in People Placement — outbound search, not vacancy ingestion

Date: 2026-11-16

## What the user can do

The public homepage provides a separate link labelled **Open EURES job search**.
It opens the official European job mobility portal's *Find a job* search in a new tab:

https://europa.eu/eures/portal/jv-se/home?lang=en

The user selects country, occupation, terms, and other available filters
**on EURES**. People Placement filters are **not** carried across because no
documented stable filter/deep-link parameter scheme has been established.

The EURES panel is distinct from verified/unverified People Placement cards.
It does not show or count EURES listings, suggest they meet policy v2, or
submit applications.

## Why this does not automatically index EURES vacancies

EURES publishes *specific additional terms* on its Find a Job service:

- "You are not permitted to use 'screen scraping' or any other automated or manual
  system to extract job vacancy data in order to further process or re-publish
  the information."
- "Only EURES partner organisations, recognised by a EURES National Coordination
  Office, are allowed to extract data using our API or similar technologies."

Official terms (the job-search page):
https://europa.eu/eures/portal/jv-se/home?lang=en

Further documentation:
https://eures.europa.eu/eures-services/help-and-support_en
https://eures.europa.eu/eures-legal-notice_it

**Linking out without importing job data is not republication.**
But storing even vacancy titles, employers, countries, or source URLs obtained
by automated extraction for an index **is further processing**. Thus merely
linking each extracted vacancy back to EURES would not remove the access
restriction. The general copyright reuse notice is not a grant overriding
the vacancy-specific Find a Job service terms.

No permission to extract through EURES API is currently documented in this
repository. Do not create scraping scripts, API polling, bulk download,
or EURES job-card imports until independently reviewed authorisation exists.

## Cost, coverage, acceptance criteria

- Extra EURES collection requests: **0**.
- Extra EURES browser rendering in collection: **0**.
- Extra indexed vacancies or enabled EURES sources: **0**.
- No change to `data/catalog.json`, `data/sources.json`, or to policy-v2 verification.
- EURES opens as an external search. Any opportunities seen there are external,
  not People Placement-verified results.
- The main service remains functional even if EURES is unavailable.

The homepage feature may be deployed after PR review, CI success and explicitly
authorised merge. For **automated** EU27 growth, prioritise independently
licensed national public employment-service feeds or employer-declared ATS
endpoints, with official access review, stable vacancy IDs, job-specific
application checks, provenance, per-host throttling and cost measurement.

## Remaining work (separate from the safe external link)

1. Identify public employment-service feeds per EU country, documenting their
   own access terms, filtering, update schedule, original employer identifiers,
   rate limits and permissible reuse. EURES membership does not automatically
   license those feeds for our use.
2. If EURES partner access is obtained, obtain written scope, retention,
   processing and attribution conditions before designing a bounded import.
3. Benchmark new independent sources by incremental, distinct verified HR
   internships per permitted request and per full daily collection cycle.
