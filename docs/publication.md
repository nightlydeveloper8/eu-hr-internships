# Verified publication — 5 November 2026

Automated production website: https://people-placement-eu.pages.dev/

Original Sites snapshot: https://people-placement-eu.mysticbramble.chatgpt.site

Sites deployment succeeded; access was set to public. The deployed page was then opened in the browser and showed the actual catalog, all 27 country options and seven listings, with Netherlands priority and no sign-in screen. Static site version 1 corresponds to source commit `7d96b554d3bf5cf2b5a8d567ba04277afc8dcca8`. Later local commits add delivery/setup documentation without changing deployed application code.

The current data contains seven verified links from six employers in four EU countries; six listings have explicit English evidence. Last collection: 5 November 2026 at 12:34 UTC / 13:34 Europe/Zurich. Ten enabled boards completed successfully. This is limited source coverage, not coverage of every employer in the EU.

The source is now published at https://github.com/nightlydeveloper8/eu-hr-internships (public, production branch `main`). The connected GitHub account was verified with a read-only profile request. All 34 tracked project files were uploaded in commit `7bca32c0063c3197cebf7397452124789398923b`. The original local history is preserved on branch `pre-github-publication`; local `main` tracks `origin/main`.

GitHub validation passed, including 28 Python tests, 11 JavaScript tests, the 50-example evaluation and static build: https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/42031289895.

The first manual **Daily employer collection** succeeded on 5 November 2026: https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/42031413698. All ten enabled sources succeeded, producing seven catalog records. The successful collection timestamp is `2026-11-05T12:56:55.273287+00:00` (13:56 Europe/Zurich). The workflow uploaded `catalog-and-coverage` (artifact `13416292493`, retained for 14 days) and pushed bot commit `f883825` with updated catalog and coverage data. All workflow steps completed successfully. GitHub emitted non-blocking notices about action Node runtime deprecation and the Ubuntu runner transition; action-version maintenance remains future work.

The daily schedule is configured for 06:17 UTC. The first actual scheduled execution remains unverified; the next expected date is 6 November 2026 (07:17 Europe/Zurich), subject to GitHub delays. Cloudflare Pages Git integration is now active and its automatic data deployment was verified (details below). The initial Sites deployment will not independently run the Python collector or refresh its static snapshot. A portable ZIP in the parent Internship directory predates GitHub activation.

The owner requested a step-by-step setup guide. See [guida-attivazione.md](guida-attivazione.md) for the Italian instructions, including verification of the first actual scheduled run. No passwords or API tokens need to be shared in chat.

## Verified Cloudflare activation — 5 November 2026

The owner completed Cloudflare login and email verification, then explicitly approved installing Cloudflare Workers and Pages for **only** `nightlydeveloper8/eu-hr-internships`. The project `people-placement-eu` uses `main`, framework `None`, build command `python3 scripts/build.py`, output `dist`, repository root, and no environment secrets. No paid plan, domain purchase or subscription was selected.

The initial deployment `93cb7c85-50f3-42ff-a5c5-8b4060bd5ae6` succeeded for commit `bee0f47` at 13:04 UTC / 14:04 Europe/Zurich. The browser opened the production site and displayed seven opportunities, all 27 country options and employer links; selecting France returned four results, and Reset restored seven.

A second manual collection succeeded: https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/42032685457. All steps passed, artifact `catalog-and-coverage` (`13416643332`) was retained, and the bot pushed commit `6dea8b08a07e30cb10cdd206c1c93b8f356a6c7d`. Cloudflare automatically built and published that exact commit in deployment `daa2794e-01a8-47af-b9e8-eadb54e886b5`, with status **success** at 13:06 UTC / 14:06 Europe/Zurich. The production dataset, reloaded in the browser, showed `updated_at: 2026-11-05T13:05:42.815449+00:00` and `update_status: ok`, matching the bot commit. The data cache permits up to five minutes of browser caching; reload revalidated the new data.

The GitHub → catalog commit → Cloudflare production deployment chain is verified. The first actual scheduled run remains to be observed on 6 November 2026 after 06:17 UTC / 07:17 Europe/Zurich. No future monitoring task was created. Browser access to the production site required no site login; an additional cookie-free Python HTTP probe returned 403, and a separate private-browser check could not be completed, so independent anonymous-client verification is not claimed.
