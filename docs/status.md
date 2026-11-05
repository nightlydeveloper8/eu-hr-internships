# Delivery status

This records tested deliverables and remaining gates; a numbered phase is not claimed complete merely because code exists.

| Phase | Observed deliverable | Status / remaining gate |
|---|---|---|
| 0 Architecture | `architecture.md`, explicit acceptance criteria, static/Python boundary | Implemented and checked against the brief |
| 1 Source research | Registry includes all 27 countries; documented ATS research; live HTTP discovery audit | Initial registry tested; exhaustive or full-country collection not claimed; unverified pages and permission reviews remain |
| 2 Adapters | Four adapters and pagination fixtures; live Greenhouse/Lever collection | Greenhouse/Lever demonstrated; Ashby/SmartRecruiters live gate blocked by access checks |
| 3 Normalisation | Country/city handling, stable IDs, canonical URL deduplication, conservative reconciliation | Unit tests pass; cross-ATS duplicate URLs can remain |
| 4 Classification | Ten HR areas, multilingual signals, explicit language evidence, 50 manually labelled examples | Regression set passes; small sample is not population accuracy |
| 5 Interface | Search, all specified filters, ordering, local bookmarks, coverage dialog, responsive styling | Browser checks recorded in QA report |
| 6 Automation/deployment | Three GitHub workflows; Cloudflare static export; separate public Sites deployment | GitHub activation and Cloudflare account linkage require account access; no verified unattended run yet |
| 7 QA | Python/JS regression tests, real catalog validation, direct-link HEAD checks, browser QA | Observed results recorded in QA report |
| 8 Expansion | 27-country employer backlog, blocked-source statuses and discovery audit | Started; source expansion remains ongoing |

No costs were authorised for paid APIs, AI inference, domains or subscriptions. No external credentials are stored in the source. Public JSON contains discovery metadata and brief evidence only.
