# Verified and unverified opportunity views

7 November 2026. The homepage now exposes two visible verification views: Verified opportunities and Include unverified opportunities. The inclusive view retains all non-closed catalog records, including listings whose application or current availability could not be confirmed. Closed listings remain excluded. Existing checkbox and `?unverified=true` links remain compatible.

Each view shows counts with the active filters applied. Archived records, verified/unverified listings, internships, working-student roles and traineeships are counted separately. The page states how many matching cards are loaded; Show all loads every match. Filtering still composes with country, region, language, category and saved listings.

The previous generic partial-refresh banner is replaced by a collapsible source-status explanation with completed/partial/failed source-check counts. Actual total failures, stale data and browser-storage problems retain notices. Access restrictions and incomplete checks are not represented as successfully verified sources. Each unverified card gives plain-language availability guidance; no verification policy or source restriction is weakened.

Validation: 175 Python tests, 17 frontend tests, 64 classification cases with zero errors, catalog validation and static build. Browser fixtures exercise button/checkbox/URL/reset synchronization, keyboard use, type/status counts, filters, exclusions and Show all. A real-catalog browser check rendered all 308 non-closed records (18 verified, 290 unverified, 1 closed excluded from 309 archived) on desktop/mobile without page errors or document overflow. Counts are a snapshot, not a guarantee of availability or a count of verified internships.

This change contains UI, tests and documentation only. It preserves the collected dataset and the separate unfinished Flevoland work.
