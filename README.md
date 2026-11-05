# People Placement — EU HR Internship Finder

A static, registration-free directory of HR internships from official employer job boards. All 27 EU countries are selectable. Netherlands-first ranking is enabled by default. The initial collection is deliberately small and is **not exhaustive**.


## Employer-first expansion (5 November 2026)

The first ten-board sample was too small to represent EU opportunities. The project now includes a 842-employer research registry, official NUTS 2024 names/codes for all 27 countries, an auditable seed workplace in each of the twelve Dutch provinces, regional coverage/gap reports and a public `employers.html` explorer. Forty employers currently have collection configured; the rest are research/integration candidates. The revised strategy targets an initial 100 employers with recent successful collection in each country, followed by country-specific targets of 500–1,500, with at least 60% of new research directed at businesses with 50–999 employees. These are planned targets, not achieved coverage. Country deficits use recent successful source inventories with observed country coverage, and discovery no longer gives the Netherlands a fixed priority. `data/employer-research-plan.json` stores targets for all 27 countries; `docs/country-research-progress.json` tracks actual progress. Regional job filters use confirmed company/city mappings only. The Dutch province seed is a starting point, not a completed employer census.

Danone and Unilever now contribute directly through their public sitemaps and structured employer pages. The expansion validation collected 16 HR internships, including four in the Netherlands, across five countries. Counts change with collection. Sitemap URL slugs are triage hints; final structured titles and countries must pass classification. Opaque or unlisted URLs can be missed, and sitemap absence cannot close a posting. Explicit source scopes are stored in the registry.

See [the Italian coverage strategy](docs/strategia-copertura.md). Run `python3 scripts/company_coverage.py` to regenerate reports and the regional discovery queue. `python3 scripts/company_coverage.py --inspect-country NL --limit 10` can propose ATS channels from declared official career pages, without auto-enabling them. Geography is versioned and imported separately using `python3 scripts/import_geography.py`; it is not re-downloaded every day. There are no new runtime dependencies or recurring AI calls.

## What is implemented

- Python collectors for Greenhouse, Lever (global and EU), Ashby and SmartRecruiters; pagination and fixture tests for all four.
- Live Greenhouse and Lever collection. Ashby and SmartRecruiters remain disabled after access checks (see below).
- Ten HR specialisations, multilingual internship/title rules, separate advertisement-language and workplace-language evidence, metadata-only public export.
- Country, specialisation, workplace/ad-language, internship type, work arrangement, keyword and saved-job filters; recency and relevance sorting; Netherlands priority.
- Local bookmarks, responsive desktop/mobile layout, update timestamps, stale warnings, source health and 27-country coverage report.
- Daily GitHub Actions collection, manual execution, tests before publication, issue-based alerts, an independent stale-data monitor and a static Cloudflare Pages build.

## Run locally

Python 3.9+ and Node 22+ for JavaScript tests. No Python packages or npm installation are needed.

```sh
python3 -m unittest discover -s tests -v
node --test tests/frontend.test.js
python3 scripts/evaluate.py
python3 scripts/build.py
python3 -m http.server 5173 --directory dist
```

Open `http://localhost:5173`. The checked-in public dataset makes the app usable without running the collector. The browser fetches only local JSON and uses no external fonts, analytics, accounts or paid services.

## Collect and inspect data

```sh
python3 -m collector.pipeline
python3 -m collector.pipeline --sources greenhouse-talentprograms lever-veepee
python3 -m collector.pipeline --validate
python3 scripts/audit_registry.py
python3 scripts/build.py
```

`--sources` performs a targeted update; other sources are retained. `--no-verify` is a diagnostic option: new listings remain unverified and are hidden by default. Do not use it for a normal production update.

`data/catalog.json` is the public catalog; `data/coverage.json` contains source runs, observed country coverage and quality counters. `data/sources.json` is the expandable registry. The inspectable regression set is `data/evaluation.json`; its score is in `docs/evaluation-report.json`. Homepage checks for discovery candidates are in `docs/source-discovery-audit.json`. A reachable homepage does not imply permission, integration or current HR internships.

The pipeline first collects **all public records** from each enabled board, then filters on internship signals, HR title and EU geography. SmartRecruiters would enrich candidate records through the documented detail endpoint after the full board is collected. Full descriptions are processed in memory; extracted public job text may be retained in an ignored, compressed technical cache for up to 48 hours between reads. It is never included in the public export. Brief evidence excerpts support language and enrolment metadata.

## Data and confidence

- Stable IDs hash source ID and source posting ID. Canonical original and application URLs remove tracking parameters for deduplication; shared application links merge mirrors. Records with distinct URLs are retained conservatively. Cross-ATS duplicates with different URLs/requisition IDs can remain.
- Advertisement language uses source metadata where available, otherwise an explicitly uncertain deterministic word heuristic. Ambiguous/unsupported text is unknown.
- Workplace languages require explicit proficiency or working-language statements. English ad text is never sufficient. English confirmation **does not** establish that English alone is sufficient; other stated languages remain visible.
- Internship/student/traineeship confidence is confirmed only by explicit title or source employment-type signals. Generic permanent roles are excluded even if descriptions mention interns.
- Location uses source country metadata first, followed by country names and a curated city dictionary. Unknown and ambiguous locations are excluded instead of assigning an employer’s headquarters. Remote “Europe” alone is not treated as permission to work from all EU states. Multi-country records support independent country filters when countries are explicit.
- Durations and enrolment are only extracted from relevant explicit text. Unknown fields are labelled. No visa, citizenship, work-permit, compensation or eligibility inference is performed.
- Link HEAD checks honor robots and approved hosts. An HTTP success verifies reachability, not a guaranteed open vacancy: API membership provides the other availability signal. If a link cannot be checked, the record is unverified and hidden unless requested.

## Failure and closure policy

Each source is isolated. Exceptions, incomplete pagination, duplicate IDs and a drop below 40% of a previously substantial board snapshot quarantine that source; its previous catalog records survive unchanged. A missing record only increments on a successful complete source snapshot, at most once per UTC day. Closing requires at least three missing snapshots spanning 48 hours. Reappearing IDs retain their first discovery date and reopen.

Successful sources can still update during a partial run; the UI shows a partial-refresh notice and the workflow creates a health issue. A complete collection failure does not advance the successful-update timestamp and makes the workflow fail. The static build validates data before export; GitHub commits data only after validation succeeds. The UI warns after 36 hours. The two JSON files are individually replaced atomically, and deployed together by the static hosting build; the local development folder is not a transactional database.

## Source access decisions

As checked on 5 November 2026:

- **Greenhouse:** documented public GET board endpoints, no credentials. Runtime robots checks apply. Invalid tokens are disabled instead of repeatedly queried.
- **Lever:** documented public board GET endpoints, all pages collected with a per-host delay. The implementation honors the advertised crawl delay.
- **SmartRecruiters:** its public API documentation exists, but `api.smartrecruiters.com/robots.txt` disallows general bots. Three employers are registered but collection is disabled. Do not impersonate the specially permitted crawler.
- **Ashby:** the documented public posting API exists, but the robots endpoint returned HTTP 401. Six sources are conservatively disabled pending permission/access clarification. No authentication workaround is attempted.
- Other employer career pages are discovery-only candidates across all 27 countries. Additional reviewed employer sitemaps, a scoped BAS job-page connector and public Personio/Recruitee feeds are now enabled. See `docs/integrazione-canali-novembre-2026.md` for the executed checks, source scopes and the announced Recruitee authentication change.

Official references: [Greenhouse](https://docs.greenhouse.io/job-board), [Lever](https://github.com/lever/postings-api), [Ashby](https://developers.ashbyhq.com/docs/public-job-posting-api), [SmartRecruiters](https://developers.smartrecruiters.com/docs/endpoints).

## Activate GitHub automation

The workflows are supplied; **they do not run until this source is pushed to a GitHub repository and Actions is enabled**. A Sites-hosted Git repository does not execute GitHub workflows.

1. Create a GitHub repository owned by the intended account/organisation and push this checkout. Keep `main` as the production branch.
2. Enable Actions. Allow the daily workflow to write repository contents and issues; if organisation policy or branch protection prevents bot pushes, use an approved update PR flow instead of weakening those protections.
3. Run **Daily employer collection → Run workflow** once. Inspect logs, the `catalog-and-coverage` artifact and the bot’s catalog commit.
4. Enable GitHub Actions/issue email notifications or watch the repository. Health alerts create one open issue per monitor and close it on recovery.
5. Confirm the Cloudflare build for the bot’s commit succeeds and the live dataset timestamp changes.

The main schedule is 06:17 UTC daily (07:17 in Zurich winter, 08:17 summer). The stale monitor runs at 12:47 UTC. GitHub schedules can be delayed; public-repository schedules may be disabled after 60 days without repository activity. GitHub sends normal workflow-failure notifications, and the browser stale warning works even when Actions itself stops running. Two GitHub schedules cannot detect a complete GitHub outage from outside GitHub; a separate free uptime monitor is an optional future addition.

## Deploy to Cloudflare Pages Free

The website runs independently of Codex, Work and ChatGPT. It is entirely static.

1. In Cloudflare, choose **Workers & Pages → Create → Pages → Connect to Git** and connect the GitHub repository.
2. Set the production branch to `main`, framework preset to **None**, build command to `python3 scripts/build.py`, and output directory to `dist`.
3. Use a build image with Python 3.9+; there are no pip/npm installation steps or environment secrets.
4. Deploy, open the returned `pages.dev` URL in an anonymous browser and verify filtering and original employer links.
5. Confirm every subsequent bot data commit triggers a Pages build. Configure production build notifications in Cloudflare.

Alternatively build locally and upload the `dist` directory in the Pages dashboard. Direct upload alone does not configure daily deployment: use the Git integration for the unattended path. No D1, Workers runtime, AI credits, login provider or custom domain is needed. `.openai/hosting.json` only records the separate Sites publication and is ignored by Cloudflare Pages.

## Maintenance

- Add a verified employer board to `data/sources.json` with a unique ID, supported adapter, exact board token, approved link hosts and access-review evidence. Never set every EU country as actual coverage based on corporate presence.
- Validate robots and the provider’s published terms; run a targeted collection, inspect the complete board count, manually review every new match and run the tests before enabling daily collection.
- Keep disabled sources disabled until access is explicitly resolved; a registry status of discovery-only is intentional.
- Extend multilingual rules with labelled positive **and negative** examples. Add region/city aliases only when unambiguous. Preserve uncertainty rather than guessing language or country.
- Review `docs/source-discovery-audit.json` and the live coverage dialog for geographic gaps. Headline totals are observed matches, never exhaustive-market counts.
- Update action versions periodically using official action releases. Do not add paid dependencies or unattended AI inference.
- To remove a posting/source, disable its registry entry and deliberately remove affected records from the catalog in a reviewed source commit. Disabled sources are retained by default for failure safety.

## Costs and current limits

The portable application has no paid dependencies or recurring AI inference. The intended setup uses a public GitHub repository with standard Linux runners and Cloudflare Pages Free; review the providers’ current free-tier limits during account setup. No paid plan, domain or API key is required by the code. The separate Sites publication uses the account’s available hosting; it is not the configured unattended Cloudflare Pages target.

Coverage is a small sample and initially concentrated in the Netherlands, France, Belgium and Portugal. Rule evaluation is a small regression check, not a statistical quality guarantee. Dutch workplace opportunities may currently be absent even though Dutch filters work. No full-market crawler, PDF parsing, advanced NLP, general-purpose feed connector or live browser automation is used by the daily collector. These are expansion work, not features claimed complete.

GitHub repository creation, live scheduled-run verification and Cloudflare Pages account linkage require the owner’s external account access. See `docs/status.md` for observed implementation and deployment status.
