# QA report — 5 November 2026

## Automated checks observed

- 28 Python unit tests passed, including all four adapter fixtures, complete pagination, malformed/incomplete responses, EU Lever region, unlisted Ashby exclusion, robots denial, safe URLs, failed-source preservation, daily closure idempotency, reappearance, canonical/application-link deduplication and multilingual extraction.
- 11 JavaScript logic tests passed: composed filters, English workplace/ad separation, closed/unverified states, bookmarks, Netherlands ordering, relevance, accent-insensitive matching, multiple countries, recency, stale timestamps and unsafe links.
- The 50 manually labelled classification examples passed: 29 positive, 21 negative. This is a deliberately small regression set, not a representative accuracy estimate.
- Catalog schema, categories, EU country codes, HTTPS links, evidence fields, stable IDs and absence of full descriptions passed validation before building.
- Portable static build passed and local HTTP root returned 200.

## Live collection observed

The final complete collection succeeded for 10 of 10 enabled sources. It collected over 1,200 public job records before filtering and exported seven HR internships in four countries: Netherlands (1), France (4), Belgium (1), Portugal (1). Six have explicit English workplace/proficiency evidence. Seven original/application links passed direct HEAD checks; the public job-board presence was also confirmed in that collection. Reachability does not guarantee continued availability after verification.

Employers with matching records: Hunter Douglas – Talent Programs, Emma – The Sleep Company, Veepee, DIM, Pigment and Malt. Advertisement languages include English and French. Veepee's French HR internship has unspecified workplace language, demonstrating that the collector does not infer a language requirement from advertisement text.

SmartRecruiters and Ashby sources are disabled after access checks. Invalid board tokens remain visible in the registry with endpoint-review status. None is counted as a successfully integrated source. The source-discovery audit separately records reachable and unverified employer homepages for all 27 countries.

## Browser checks observed

Checked through the actual browser at desktop 1360 × 900 and mobile 390 × 844:

- Default Netherlands-first results place the Rotterdam HRBP internship first.
- Keyword search for Rotterdam returns one match.
- Saving the Rotterdam internship changes the shortlist count; the saved-only filter and bookmark survive a page reload.
- Country Netherlands combined with confirmed English returns the Rotterdam match and its explicit proficiency excerpt.
- Country Malta remains selectable and displays an honest zero-result state.
- Advertisement-language French returns two postings; workplace-language uncertainty remains separate.
- The coverage dialog contains exactly 27 country rows and reports seven verified open links, six English-evidence records and 10/10 refreshed sources.
- Mobile filters open, change country to Belgium, return one result and close using Show results.
- Mobile document width fits within the viewport with no horizontal overflow.
- Original and application links use the employer-managed ATS hosts and open in a new tab.

Two metadata issues discovered during inspection were fixed and covered by regression tests: paid holiday duration must not become internship duration, and “additional languages are a plus” must not make required English optional.

## Not yet verified

GitHub-hosted scheduled execution, issue notification delivery, bot commit permissions and a Cloudflare Pages production rebuild require account connection. Their workflow/configuration is supplied, but no live run is claimed. Browser UI checks were interactive; they are not represented as an unattended end-to-end CI suite. Statistical multilingual precision/recall and full 27-country live listing coverage remain expansion work.
