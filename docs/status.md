# Delivery status

This records tested deliverables and remaining gates; a numbered phase is not claimed complete merely because code exists.

| Phase | Observed deliverable | Status / remaining gate |
|---|---|---|
| 0 Architecture | `architecture.md`, explicit acceptance criteria, static/Python boundary | Implemented and checked against the brief |
| 1 Source research | Registry includes all 27 countries; documented ATS research; live HTTP discovery audit | Official EU27 NUTS geography, 842-employer inventory and initial Dutch province coverage added; comprehensive employer research and integrations remain |
| 2 Adapters | Four adapters and pagination fixtures; live Greenhouse/Lever collection | Greenhouse/Lever plus Danone/Unilever official page/sitemap collection demonstrated; Ashby/SmartRecruiters access gates remain blocked |
| 3 Normalisation | Country/city handling, stable IDs, canonical URL deduplication, conservative reconciliation | Unit tests pass; cross-ATS duplicate URLs can remain |
| 4 Classification | Ten HR areas, multilingual signals, explicit language evidence, 50 manually labelled examples | Regression set passes; small sample is not population accuracy |
| 5 Interface | Search, all specified filters, ordering, local bookmarks, coverage dialog, responsive styling | Browser checks recorded in QA report |
| 6 Automation/deployment | Public GitHub repository; passing validation and first manual daily collection; bot data commit and retained artifact; separate public Sites deployment | Cloudflare production site and automatic deployment from a second bot collection commit verified; first actual scheduled execution remains to be observed. See `publication.md` for evidence |
| 7 QA | Python/JS regression tests, real catalog validation, direct-link HEAD checks, browser QA | Observed results recorded in QA report |
| 8 Expansion | 27-country employer backlog, blocked-source statuses and discovery audit | Employer-first registry and regional queue implemented; 40 monitored employers and 22 catalog opportunities (20 internships, 2 working-student roles); a revised per-country research plan targets 100 employers with recent verified collection per country initially and 500–1,500 on expansion, prioritising medium businesses; comprehensive coverage remains ongoing |

No costs were authorised for paid APIs, AI inference, domains or subscriptions. No external credentials are stored in the source. Public JSON contains discovery metadata and brief evidence only.
