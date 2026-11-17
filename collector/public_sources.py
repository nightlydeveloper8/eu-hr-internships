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

PUBLIC_API_ADAPTERS = ('jobtech-search',)
PUBLIC_SOURCE_KIND = 'public-employment-service'
INVENTORY_EVIDENCE = 'official-public-api-active-listing'

# Queries are recall aids only. Every result still has to pass the normal
# internship + HR title classification and an explicit country.
JOBTECH_QUERIES = (
    '+praktik +HR', '+praktik +rekrytering', '+praktik +personal', '+praktikant',
    '+HR-praktik', '+HR-praktikant', '+internship', '+intern +HR', '+trainee +HR',
    '+trainee +rekrytering',
)
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
    records, queries, partial = {}, 0, []
    for query in source.get('queries', JOBTECH_QUERIES):
        offset = 0
        while offset <= JOBTECH_MAX_OFFSET:
            data = client.json(base + '/search?' + urlencode({'q': query, 'limit': JOBTECH_PAGE, 'offset': offset}))
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
    return PublicInventory(records.values(), dict(
        status='ok', complete=False, closure_complete=False, queries=queries,
        truncated_queries=partial, published_records=len(records), verified_closed_urls=closed,
        snapshot_kind='public-api-query-inventory',
        discovery_scope=source.get('discovery_scope')))


def collect_public(source, client):
    if source['adapter'] == 'jobtech-search':
        return jobtech_records(source, client)
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


def merge_public_duplicates(jobs, public_source_ids):
    """Fold a public-service copy into the employer's own listing.

    A public record is merged only when exactly one non-public, non-closed
    catalog record matches by (a) the employer application URL published by
    the public service, or (b) the same employer, title and country. Ambiguous
    matches are left as separate records rather than guessed.
    """
    public_source_ids = set(public_source_ids)
    own = [j for j in jobs if j['source_id'] not in public_source_ids and j.get('status') != 'closed']
    by_url, by_identity = {}, {}
    for job in own:
        for url in {job.get('url'), job.get('apply_url')}:
            if url:
                by_url.setdefault(canonical_url(url), []).append(job)
        for country in job.get('countries', []):
            by_identity.setdefault((employer_key(job['employer']), title_key(job['title']), country), []).append(job)
    result, merged = [], 0
    for job in jobs:
        if job['source_id'] not in public_source_ids or job.get('status') == 'closed':
            result.append(job)
            continue
        matches = []
        if job.get('external_application_url'):
            matches = by_url.get(job['external_application_url'], [])
        if not matches:
            keys = {(employer_key(job['employer']), title_key(job['title']), c) for c in job.get('countries', [])}
            matches = list({id(m): m for k in keys for m in by_identity.get(k, [])}.values())
        if len(matches) != 1:
            result.append(job)
            continue
        target = matches[0]
        target['duplicate_source_ids'] = sorted(set(target.get('duplicate_source_ids', [])) | {job['source_id']})
        target['public_listing_urls'] = sorted(set(target.get('public_listing_urls', [])) | {job['url']})
        merged += 1
    return result, merged
