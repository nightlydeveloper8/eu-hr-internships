"""Official public employment-service APIs (national job banks).

Only sources whose terms, licence and robots.txt were reviewed in
docs/fonti-pubbliche.md are implemented here. Each adapter returns the same
record shape as the employer adapters, with three differences:

* ``inventory_evidence`` is ``official-public-api-active-listing``: the API
  lists published advertisements only.
* ``url`` and ``apply_url`` both point to the official public advertisement
  page; the employer's own application link (if published) is kept only in
  ``external_application_url`` for cross-source deduplication.
* Contact details (e-mail addresses, phone numbers, named contacts) are never
  copied: free text is scrubbed before classification.
"""
import re
from urllib.parse import urlencode, urlsplit
from .classify import canonical_url, fold, plain

PUBLIC_API_ADAPTERS = ('jobtech-search', 'eures-search')
# Pan-European copies yield to the employer's own listing and to a national
# public service listing of the same vacancy.
SECONDARY_PUBLIC_ADAPTERS = ('eures-search',)
PUBLIC_SOURCE_KIND = 'public-employment-service'
INVENTORY_EVIDENCE = 'official-public-api-active-listing'

# Queries are recall aids only. Every result still has to pass the normal
# internship + HR title classification and an explicit country.
def vocabulary_search_terms(language):
    """(placement terms, HR terms) for one language from data/hr-vocabulary.json."""
    from .classify import VOCABULARY
    search = VOCABULARY.get('search', {})
    return search.get('placement_terms', {}).get(language, []), search.get('hr_terms', {}).get(language, [])


def jobtech_queries():
    placements, hr_terms = vocabulary_search_terms('sv')
    generated = ['+' + p + ' +' + h for p in placements for h in hr_terms]
    # Swedish compounds and English-language ads in Platsbanken.
    return tuple(generated + ['+praktikant', '+HR-praktik', '+HR-praktikant', '+internship', '+intern +HR', '+trainee +HR'])


JOBTECH_QUERIES = jobtech_queries()
JOBTECH_PAGE = 100
JOBTECH_MAX_OFFSET = 300  # results are relevance-ranked; deeper pages are off-topic
JOBTECH_SWEDEN = {'199', 'sverige', 'sweden'}
JOBTECH_WORK_MODE = {'hybridarbete': 'hybrid', 'distansarbete': 'remote', 'pa plats': 'on-site', 'på plats': 'on-site'}

EMAIL = re.compile(r'[\w.+-]+@[\w-]+(?:\.[\w-]+)+')
PHONE = re.compile(r'(?<![\w/])\+?\d[\d\s().-]{6,}\d(?![\w/])')
ISO_DATE = re.compile(r'\d{4}-\d{2}-\d{2}')


def _phone(match):
    value = match.group(0)
    # Dates and short amounts are not phone numbers; keep intake/duration text.
    if ISO_DATE.fullmatch(value.strip()) or sum(c.isdigit() for c in value) < 8:
        return value
    return ' '


def scrub(text):
    """Remove e-mail addresses and phone numbers; keep the rest unchanged."""
    return re.sub(r'\s+', ' ', PHONE.sub(_phone, EMAIL.sub(' ', plain(text or '')))).strip()


def https_or_none(url):
    try:
        return canonical_url(url) if url else None
    except ValueError:
        return None


def _fatal(exc):
    """Errors that must fail the whole source instead of skipping one query."""
    return (type(exc).__name__ == 'CollectionBudgetExceeded' or getattr(exc, 'code', None) in (401, 403, 404, 429, 451)
            or 'robots' in str(exc))


def _retry_once(call):
    """Retry a dropped connection, 5xx or truncated JSON body once."""
    for attempt in (1, 2):
        try:
            return call()
        except Exception as exc:
            if attempt == 2 or _fatal(exc):
                raise


# Public-API verification rule (Phase 5). Applies only to sources whose
# registry entry declares ``active_listing_api: true`` after review: their
# search returns currently published advertisements only.
MAX_LISTING_AGE_DAYS = 180
LISTED_ONLY = 'public-api-listed'
ACTIVE_LISTING = 'public-api-active-listing'


def _instant(value):
    from datetime import datetime, timezone
    parsed = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def public_api_verification(source, record, stamp):
    """Return (verified_at or None, link_status, reason) for a public-API record."""
    from .verification import expired
    if not source.get('active_listing_api'):
        return None, LISTED_ONLY, 'Listed by an official public employment-service API on this run; this source is not reviewed as an active-listings-only API'
    if record.get('inventory_evidence') != INVENTORY_EVIDENCE:
        return None, LISTED_ONLY, 'Record did not come from the active-listing search on this run'
    deadline = record.get('valid_through')
    try:
        if deadline and expired(deadline, stamp):
            return None, LISTED_ONLY, 'Published application deadline has passed'
        published = record.get('published_at')
        age = (_instant(stamp) - _instant(published)).days if published else None
    except (ValueError, TypeError):
        return None, LISTED_ONLY, 'Invalid publication date or deadline in the public API record'
    if not deadline and (age is None or age > MAX_LISTING_AGE_DAYS):
        return None, LISTED_ONLY, f'Listed by the public API but published more than {MAX_LISTING_AGE_DAYS} days ago (or undated) without an application deadline'
    if age is not None and age < -1:
        return None, LISTED_ONLY, 'Publication date lies in the future'
    return stamp, ACTIVE_LISTING, ('Returned on this run by an official public employment-service search that lists only currently '
                                  'published advertisements; the employer application page was not checked')

class PublicInventory(list):
    """Records plus collection statistics (same contract as universal.Inventory)."""
    def __init__(self, records=(), stats=None):
        super().__init__(records)
        self.stats = stats or {}


def jobtech_record(source, hit):
    if hit.get('removed'):
        return None
    address = hit.get('workplace_address') or {}
    country_value = fold(str(address.get('country_code') or address.get('country') or ''))
    if country_value not in JOBTECH_SWEDEN:
        return None  # ads abroad: country names are Swedish labels; do not guess
    page = canonical_url(hit['webpage_url'])
    if urlsplit(page).hostname not in source['allowed_hosts']:
        raise ValueError('Unexpected JobTech advertisement host')
    description = hit.get('description') or {}
    text = ' '.join(scrub(description.get(key)) for key in ('text', 'needs', 'requirements', 'conditions') if description.get(key))
    employer = hit.get('employer') or {}
    city = address.get('city') or address.get('municipality') or ''
    location = ', '.join(x for x in (city.title() if city.isupper() else city, address.get('region'), 'Sweden') if x)
    model = fold((hit.get('workplace_model') or {}).get('label') or '')
    application = hit.get('application_details') or {}
    deadline = hit.get('application_deadline')
    return dict(
        inventory_evidence=INVENTORY_EVIDENCE, source_id=source['id'], external_id=str(hit['id']),
        posting_identifier=str(hit['id']), employer=plain(employer.get('name') or employer.get('workplace') or ''),
        title=plain(hit['headline']), location=location, text=text, url=page, apply_url=page,
        countries=['SE'], language=None, published_at=hit.get('publication_date'),
        valid_through=deadline[:10] if deadline else None,
        employment=plain((hit.get('employment_type') or {}).get('label') or ''),
        city=city.title() if city.isupper() else city, country='SE',
        work_mode=JOBTECH_WORK_MODE.get(model), external_application_url=https_or_none(application.get('url')))


def jobtech_records(source, client):
    base = 'https://jobsearch.api.jobtechdev.se'
    records, queries, partial, errors = {}, 0, [], []
    for query in source.get('queries', JOBTECH_QUERIES):
        offset = 0
        while offset <= JOBTECH_MAX_OFFSET:
            url = base + '/search?' + urlencode({'q': query, 'limit': JOBTECH_PAGE, 'offset': offset})
            try:
                data = _retry_once(lambda: client.json(url))
            except Exception as exc:
                if _fatal(exc):
                    raise
                errors.append(dict(query=query, offset=offset, error=str(exc)[:160]))
                break
            queries += 1
            hits = data.get('hits')
            if not isinstance(hits, list):
                raise ValueError('Malformed JobTech search page')
            for hit in hits:
                record = jobtech_record(source, hit)
                if record:
                    records[record['external_id']] = record
            total = (data.get('total') or {}).get('value', 0)
            offset += JOBTECH_PAGE
            if not hits or offset >= total:
                break
        else:
            partial.append(query)
    # Previously published ads that dropped out of the relevance window are
    # checked individually; only an explicit removal/404 closes them.
    closed = []
    for url in source.get('known_job_urls', []):
        identifier = urlsplit(url).path.rstrip('/').split('/')[-1]
        if not identifier.isdigit() or identifier in records:
            continue
        try:
            hit = client.json(base + '/ad/' + identifier)
        except Exception as exc:  # HTTPError 404 = removed
            if getattr(exc, 'code', None) == 404:
                closed.append(url)
                continue
            raise
        if hit.get('removed'):
            closed.append(url)
            continue
        record = jobtech_record(source, hit)
        if record:
            records[record['external_id']] = record
    if errors and not records:
        raise ValueError('JobTech search unavailable: ' + errors[0]['error'])
    return PublicInventory(records.values(), dict(
        status='partial' if errors else 'ok', search_errors=errors[:20], complete=False, closure_complete=False, queries=queries,
        truncated_queries=partial, published_records=len(records), verified_closed_urls=closed,
        snapshot_kind='public-api-query-inventory',
        discovery_scope=source.get('discovery_scope')))


EURES_API = 'https://europa.eu/eures/api/jv-searchengine/public'
EURES_PAGE = 50  # the portal accepts 10, 25 or 50
EURES_MAX_PAGES = 8
EURES_OFFERING_MAX_PAGES = 30
# Title queries are generated from data/hr-vocabulary.json: per language, one
# relevance-ranked query combining the placement terms and the HR terms (the
# portal ranks vacancies matching more terms first). A query is paged while it
# keeps producing new HR internships. Recall aids only: classification and an
# explicit country still decide inclusion.
EURES_LANGUAGES = ('en', 'de', 'fr', 'it', 'es', 'nl', 'pt', 'pl', 'sv', 'da', 'fi', 'cs', 'sk', 'sl', 'hr',
                   'hu', 'ro', 'bg', 'el', 'et', 'lv', 'lt')
EURES_EMPTY_PAGES = 2  # stop after this many consecutive pages without new HR internships


def eures_pair_queries():
    """One placement term + one HR term per query (measured 18/11/2026: ~18% more
    HR internships than one combined query per language)."""
    from .classify import fold
    pairs = []
    for language in EURES_LANGUAGES:
        placements, hr_terms = vocabulary_search_terms(language)
        pairs += [p + ' ' + h for p in placements for h in hr_terms]
    unique = {}
    for query in pairs:
        unique.setdefault(fold(query), query)
    return tuple(unique.values())


def eures_queries():
    queries = []
    for language in EURES_LANGUAGES:
        placements, hr_terms = vocabulary_search_terms(language)
        if placements and hr_terms:
            queries.append(' '.join(dict.fromkeys(placements + hr_terms)))
    return tuple(queries)


EURES_PAIR_QUERIES = eures_pair_queries()
EURES_PAIR_PAGES = 3
EURES_QUERIES = eures_queries()
EURES_COUNTRY_ALIASES = {'EL': 'GR', 'UK': 'GB'}
# Some services (e.g. the Dutch UWV) do not transmit the employer's name.
EURES_UNDISCLOSED_EMPLOYER = 'Employer not disclosed (see EURES advertisement)'


def eures_criteria(keywords=(), offering=(), page=1):
    return {
        'resultsPerPage': EURES_PAGE, 'page': page, 'sortSearch': 'BEST_MATCH',
        'keywords': [{'keyword': k, 'specificSearchCode': 'TITLE'} for k in keywords],
        'publicationPeriod': None, 'occupationUris': [], 'skillUris': [], 'requiredExperienceCodes': [],
        'positionScheduleCodes': [], 'sectorCodes': [], 'educationAndQualificationLevelCodes': [],
        'educationGroupCodes': [], 'positionOfferingCodes': list(offering), 'locationCodes': [],
        'euresFlagCodes': [], 'otherBenefitsCodes': [], 'requiredLanguages': [], 'advSearchRequiredLanguages': [],
        'minNumberPost': None, 'sessionId': 'people-placement'}


_NUTS = None


def nuts_name(code):
    global _NUTS
    if _NUTS is None:
        import json
        from pathlib import Path
        path = Path(__file__).resolve().parents[1] / 'data' / 'geography.json'
        units = json.loads(path.read_text()).get('units', []) if path.exists() else []
        _NUTS = {u['code']: u.get('latin_name') or u.get('name') for u in units}
    return _NUTS.get(code)


def eures_page_url(identifier):
    return canonical_url('https://europa.eu/eures/portal/jv-se/jv-details/' + identifier + '?lang=en')


# Job-board names that appear as a logo in crawled advertisements, not employers.
EURES_BOARD_LOGOS = re.compile(r'(?i)^(?:indeed|linkedin|glassdoor|monster(?:board)?|nationale vacaturebank|werkzoeken(?:\.nl)?|'
                               r'jobbird|stagemarkt|werk\.nl|uwv|eures|homepage|logo|company|bedrijf|werkgever)$')


def eures_employer_from_text(text):
    """Employer of a crawled advertisement whose page starts with "<Employer> logo".

    Several national services (UWV for the Netherlands) republish ads found on
    employer sites without the employer field; the page header is kept in the
    description. The name is used only when the header repeats it later."""
    match = re.match(r'\s*([^.:;|<>]{2,60}?)\s+logo\b', text or '', re.I)
    if not match:
        return None
    name = match.group(1).strip(' -\u2013')
    if not name or EURES_BOARD_LOGOS.match(name) or len(re.findall(re.escape(name), text, re.I)) < 2:
        return None
    return name


def eures_language(hint, title, text):
    """EURES' language label is the national service's default (UWV labels English
    ads as Dutch). A clear stopword reading of the text wins over the label."""
    from .classify import advertisement_language
    reading = advertisement_language(title + '. ' + (text or ''))
    if reading['code'] and hint and reading['code'] != hint.lower().split('-')[0]:
        return None
    return hint


def eures_fingerprint(record):
    """Same vacancy republished under a new EURES id: same title, place and text."""
    title = re.sub(r'[^a-z0-9]', '', fold(record['title']))
    body = re.sub(r'[^a-z0-9]', '', fold(plain(record.get('text') or '')))
    start = body.find(title) if title else -1
    body = body[start + len(title):] if start >= 0 else body
    return (title, fold(record.get('employer') or ''), record.get('city') or '', body[:300])


def eures_record(source, jv):
    identifier = str(jv.get('id') or '')
    if not identifier:
        raise ValueError('Malformed EURES vacancy summary')
    if not jv.get('title'):
        return None
    location_map = jv.get('locationMap') or {}
    countries, places = set(), []
    for code, regions in location_map.items():
        country = EURES_COUNTRY_ALIASES.get(code.upper(), code.upper())
        if re.fullmatch(r'[A-Z]{2}', country):
            countries.add(country)
        for region in regions or []:
            name = nuts_name(region)
            if name and name not in places:
                places.append(name)
    if not countries:
        return None
    from datetime import datetime, timezone
    created = jv.get('creationDate')
    published = datetime.fromtimestamp(created / 1000, timezone.utc).isoformat() if isinstance(created, (int, float)) else None
    languages = jv.get('availableLanguages') or []
    employer = plain((jv.get('employer') or {}).get('name') or '')
    text = scrub(jv.get('description'))
    if not employer or re.fullmatch(r'(?i)non renseign\w*|siehe beschreibung|not specified|n/?a|-+', employer):
        employer = eures_employer_from_text(plain(jv.get('description') or '')) or EURES_UNDISCLOSED_EMPLOYER
    page = eures_page_url(identifier)
    return dict(
        inventory_evidence=INVENTORY_EVIDENCE, source_id=source['id'], external_id=identifier,
        posting_identifier=identifier, employer=employer, title=plain(jv['title']),
        location='; '.join(places + sorted(countries)), text=text, url=page, apply_url=page,
        countries=sorted(countries), published_at=published,
        language=eures_language(languages[0], plain(jv['title']), plain(jv.get('description') or '')) if len(languages) == 1 else None,
        valid_through=None, employment=plain(jv.get('positionOfferingCode') or ''),
        city='; '.join(places), country=sorted(countries)[0] if len(countries) == 1 else None, work_mode=None)


def eures_detail_summary(detail, identifier):
    """Reduce a vacancy detail to the search-summary shape; contacts are dropped."""
    profiles = detail.get('jvProfiles') or {}
    profile = profiles.get(detail.get('preferredLanguage')) or next(iter(profiles.values()), {})
    if not profile.get('title'):
        return {'id': identifier}
    location_map = {}
    for place in profile.get('locations') or []:
        if place.get('countryCode'):
            regions = location_map.setdefault(place['countryCode'].upper(), [])
            if place.get('region'):
                regions.append(place['region'].upper())
    return dict(id=detail.get('id') or identifier, title=profile['title'], description=profile.get('description'),
                locationMap=location_map, employer={'name': (profile.get('employer') or {}).get('name')},
                positionOfferingCode=profile.get('positionOfferingCode'), creationDate=detail.get('creationDate'),
                availableLanguages=[detail['preferredLanguage']] if detail.get('preferredLanguage') else [])


def eures_records(source, client):
    from .classify import classify_role
    records, requests, truncated, errors = {}, 0, [], []

    def read(criteria):
        nonlocal requests
        data = _retry_once(lambda: client.post_json(EURES_API + '/jv-search/search', criteria))
        requests += 1
        jvs = data.get('jvs')
        if not isinstance(jvs, list):
            raise ValueError('Malformed EURES search page')
        matches = 0
        for jv in jvs:
            record = eures_record(source, jv)
            if not record:
                continue
            if record['external_id'] not in records and classify_role(record['title'], record['text'], record['employment']):
                matches += 1
            records.setdefault(record['external_id'], record)
        return jvs, matches

    # 1. Everything the national services coded as an internship.
    def scan(label, criteria_for, max_pages, stop_without_matches):
        empty = 0
        for page in range(1, max_pages + 1):
            try:
                jvs, matches = read(criteria_for(page))
            except Exception as exc:
                if _fatal(exc):
                    raise
                errors.append(dict(query=label, page=page, error=str(exc)[:160]))
                return
            empty = 0 if matches else empty + 1
            if len(jvs) < EURES_PAGE or (stop_without_matches and empty >= EURES_EMPTY_PAGES):
                return
        truncated.append(label)

    budget_stop = []

    def guarded(label, criteria_for, max_pages, stop_without_matches):
        # The daily time/request budget ends the run gracefully: what was read
        # is kept (status partial) instead of failing the whole source.
        if budget_stop:
            truncated.append(label)
            return
        try:
            scan(label, criteria_for, max_pages, stop_without_matches)
        except Exception as exc:
            if type(exc).__name__ != 'CollectionBudgetExceeded':
                raise
            budget_stop.append(label)
            truncated.append(label)

    guarded('positionOffering=internship', lambda page: eures_criteria(offering=['internship'], page=page),
            EURES_OFFERING_MAX_PAGES, False)
    # 2. Pair queries (placement term + HR term), highest-volume languages first.
    for query in source.get('queries', EURES_PAIR_QUERIES):
        guarded(query, lambda page, q=query: eures_criteria(keywords=[q], page=page), EURES_PAIR_PAGES, True)
    # 3. Combined per-language queries add a few extra matches when time remains.
    for query in source.get('combined_queries', EURES_QUERIES):
        guarded(query, lambda page, q=query: eures_criteria(keywords=[q], page=page), EURES_MAX_PAGES, True)
    # 3. Known vacancies outside today's result windows: explicit status only.
    closed = []
    for url in ([] if budget_stop else source.get('known_job_urls', [])[:source.get('max_known_checks', 40)]):
        identifier = urlsplit(url).path.rstrip('/').split('/')[-1]
        if identifier in records:
            continue
        try:
            jv = client.json(EURES_API + '/jv/id/' + identifier + '?requestLang=en&preferredLang=en')
        except Exception as exc:
            if getattr(exc, 'code', None) == 404:
                closed.append(url)
                continue
            raise
        requests += 1
        record = eures_record(source, eures_detail_summary(jv, identifier))
        if record:
            records[record['external_id']] = record
    if errors and not records:
        raise ValueError('EURES search unavailable: ' + errors[0]['error'])
    # The same vacancy is sometimes republished under a new id (a repost, or a
    # second language version). Keep the most recent copy only.
    newest = {}
    for record in sorted(records.values(), key=lambda r: (r.get('published_at') or '', r['external_id']), reverse=True):
        newest.setdefault(eures_fingerprint(record), record)
    folded = len(records) - len(newest)
    records = {r['external_id']: r for r in newest.values()}
    return PublicInventory(records.values(), dict(
        republished_duplicates_folded=folded,
        status='partial' if errors or budget_stop else 'ok', search_errors=errors[:20],
        budget_stopped_at=budget_stop[0] if budget_stop else None,
        complete=False, closure_complete=False, queries=requests, truncated_queries=truncated,
        published_records=len(records), verified_closed_urls=closed, snapshot_kind='public-api-query-inventory',
        discovery_scope=source.get('discovery_scope')))


def collect_public(source, client):
    if source['adapter'] == 'jobtech-search':
        return jobtech_records(source, client)
    if source['adapter'] == 'eures-search':
        return eures_records(source, client)
    raise ValueError('Unsupported public adapter: ' + source['adapter'])


LEGAL_SUFFIX = re.compile(
    r'\b(?:aktiebolag|ab|publ|gmbh|ag|kg|se|sa|sas|sarl|srl|spa|s\.?p\.?a|bv|b\.v|nv|n\.v|ltd|limited|plc|llc|inc|'
    r'oy|oyj|as|a/s|aps|sp\.? z o\.?o|s\.r\.o|kft|zrt|group|groep|sverige|sweden|deutschland|france|nederland)\b\.?')


def employer_key(name):
    value = fold(plain(name or '')).replace('&', ' and ')
    value = LEGAL_SUFFIX.sub(' ', value)
    return re.sub(r'[^a-z0-9]+', ' ', value).strip()


def title_key(title):
    value = fold(plain(title or ''))
    value = re.sub(r'\((?:[mwfdhx]\s*/\s*)+[mwfdhx]\)|\b(?:[mwfdhx]\s*/\s*){1,3}[mwfdhx]\b', ' ', value)
    return re.sub(r'[^a-z0-9]+', ' ', value).strip()


def _fold_into(jobs, copies_from, targets_from):
    """Merge each record of ``copies_from`` into its unique match in ``targets_from``."""
    targets = [j for j in jobs if j['source_id'] in targets_from and j.get('status') != 'closed']
    by_url, by_identity = {}, {}
    for job in targets:
        for url in {job.get('url'), job.get('apply_url'), job.get('external_application_url')}:
            if url:
                by_url.setdefault(canonical_url(url), []).append(job)
        for country in job.get('countries', []):
            by_identity.setdefault((employer_key(job['employer']), title_key(job['title']), country), []).append(job)
    result, merged, replaced = [], 0, {}
    for job in jobs:
        if job['source_id'] not in copies_from or job.get('status') == 'closed':
            result.append(job)
            continue
        matches = []
        if job.get('external_application_url'):
            matches = list({id(m): m for m in by_url.get(job['external_application_url'], [])}.values())
        if not matches:
            keys = {(employer_key(job['employer']), title_key(job['title']), c) for c in job.get('countries', [])}
            matches = list({id(m): m for k in keys for m in by_identity.get(k, [])}.values())
        if len(matches) != 1:
            result.append(job)
            continue
        target = replaced.get(id(matches[0]), matches[0])
        if job.get('status') == 'open' and target.get('status') != 'open':
            # Keep the listing that carries current evidence. The unverified
            # record is folded into the verified public copy, never the reverse.
            job['duplicate_source_ids'] = sorted(set(target.get('duplicate_source_ids', [])) | {target['source_id']})
            job['related_listing_urls'] = sorted(set(target.get('related_listing_urls', [])) | {target['url']})
            job['public_listing_urls'] = sorted(set(target.get('public_listing_urls', [])))
            replaced[id(matches[0])] = job
            merged += 1
            continue
        target['duplicate_source_ids'] = sorted(set(target.get('duplicate_source_ids', [])) | {job['source_id']})
        target['public_listing_urls'] = sorted(set(target.get('public_listing_urls', [])) | {job['url']})
        merged += 1
    return [replaced.get(id(j), j) for j in result], merged


def merge_public_duplicates(jobs, public_source_ids, secondary_source_ids=()):
    """Fold public-service copies into the most direct listing of a vacancy.

    Order of preference: the employer's own listing, then a national public
    service, then a pan-European copy (EURES). A copy is merged only when
    exactly one non-closed record matches by (a) the employer application URL
    published by the public service, or (b) the same normalised employer,
    title and country. Ambiguous matches stay separate rather than guessed.
    """
    public = set(public_source_ids)
    secondary = set(secondary_source_ids) & public
    every = {j['source_id'] for j in jobs}
    own = every - public
    jobs, first = _fold_into(jobs, public - secondary, own)
    jobs, second = _fold_into(jobs, secondary, every - secondary)
    return jobs, first + second
