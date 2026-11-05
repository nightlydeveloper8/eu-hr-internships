# Phase 0: architecture and acceptance contract

People Placement is a static, registration-free EU HR internship directory. Python 3.9+ standard-library collectors use documented public employer ATS APIs. Browser-native JavaScript renders a static JSON export; there are no runtime dependencies, paid APIs, AI calls, cookies or accounts. This deliberately uses buildless JavaScript instead of Vite to keep maintenance and deployment small.

## Acceptance gates

1. Exactly 27 EU countries can be selected, including those with zero listings; Netherlands-first ranking is default.
2. Only records with explicit internship/student/traineeship signals and HR title signals enter the catalog. Ordinary employment, marketing and software roles must fail the evaluation set.
3. Advertisement language and workplace language are independent fields. English filters require an explicit role-specific proficiency or working-language statement. Additional languages remain visible; confirmed English never means English-only eligibility.
4. All four initial adapters have fixture tests; live sources are reported separately from adapter support. Entire public boards are paginated before classification; detail calls enrich candidate records only.
5. URLs must use HTTPS and approved public hosts. Successful API presence and successful direct-link checks have separate timestamps.
6. A failed/incomplete source cannot count as an absence or close records. Closing requires three complete missing snapshots spanning 48 hours. Bulk disappearance is quarantined.
7. Collection, classification evaluation, catalog validation and frontend logic tests pass before the public export is published. Export uses staged atomic file replacements.
8. A daily GitHub Actions workflow and independent stale monitor are supplied. Scheduled execution is only claimed active after a real GitHub repository run is verified.
9. Desktop/mobile browser QA verifies filtering, search, saved jobs, unknown fields and employer links.
10. Public hosting must permit anonymous visitors. Cloudflare Pages is the portable target; any alternative published preview is documented separately.

## Data boundaries

Full descriptions are held in memory for deterministic classification and discarded. Public metadata includes at most brief language, duration and enrollment evidence. Raw descriptions and personal recruiter details are not exported. No aggregator supplies catalog records. Coverage is measured by integrated sources and observed job countries, never assumed from employer size or headquarters.

## Research sources

- Greenhouse public GET API: https://docs.greenhouse.io/job-board
- Lever public postings, global/EU regions: https://github.com/lever/postings-api
- Ashby public job-board API: https://developers.ashbyhq.com/docs/public-job-posting-api
- SmartRecruiters public company postings: https://developers.smartrecruiters.com/docs/endpoints

Only public listed postings are used. No internal/authenticated feeds, application submission endpoints or browser protection workarounds. Future page/feed/sitemap adapters require an explicit permission/terms review and robots checks before enabling. Public API documentation permits retrieval for career boards; it is not a blanket license for redistribution. Store discovery metadata only and honor source removal requests.
