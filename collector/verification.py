"""Conservative, read-only evidence of a vacancy and its application entry."""
import re
from datetime import datetime, timezone
from urllib.error import HTTPError
from urllib.parse import urljoin, urlsplit
from .classify import canonical_url, fold, plain, classify_role
from .applications import checked_document, verify_application, ApplicationClosed, ApplicantForms

POLICY_VERSION = 2


def verified_job(job, stamp):
    try:
        clock=datetime.fromisoformat(stamp.replace('Z','+00:00'))
        verified=datetime.fromisoformat(job['last_verified_at'].replace('Z','+00:00'))
        proof=job.get('verification',{})
        return job.get('status')=='open' and job.get('link_status')=='verified' and proof.get('state')=='verified' and proof.get('policy_version')==POLICY_VERSION and 0<=(clock-verified).total_seconds()<=48*3600
    except (ValueError,TypeError,AttributeError,KeyError):return False


def blocked_error(exc):
    return (isinstance(exc, HTTPError) and exc.code in (401, 403, 429, 451)) or bool(
        re.search(r'robots|access (?:challenge|restricted|denied)|captcha|security verification', str(exc), re.I))


def expired(value, stamp):
    if not value: return False
    date = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    if date.tzinfo is None: date = date.replace(tzinfo=timezone.utc)
    # Date-only deadlines are inclusive through that UTC day.
    if len(str(value)) == 10: return date.date() < datetime.fromisoformat(stamp).date()
    return date < datetime.fromisoformat(stamp)


def same_title(doc, title):
    expected = fold(plain(title))
    titles = doc.h1 + [plain(p.get('title')) for p in doc.jobposts()]
    return expected in [fold(t) for t in titles]


def same_requisition(vacancy, application):
    """An observed /apply child retains the complete vacancy path (e.g. Lever UUID).

    General /apply pages and unrelated IDs cannot pass this check.
    """
    a,b=urlsplit(vacancy),urlsplit(application)
    path=a.path.rstrip('/')
    return a.hostname==b.hostname and len(path.split('/'))>=3 and bool(
        re.fullmatch(re.escape(path)+r'/(?:apply|application)',b.path.rstrip('/')))


def shares_identifier(record, application):
    candidates=[record.get('posting_identifier'),record.get('external_id')]
    final_segment=urlsplit(record['url']).path.rstrip('/').split('/')[-1]
    if re.fullmatch(r'\d+|[0-9a-fA-F-]{32,36}',final_segment):candidates.append(final_segment)
    parts=[p for p in re.split(r'[/=?&]',urlsplit(application).path+'?'+urlsplit(application).query) if p]
    return any(isinstance(value,(str,int)) and str(value) in parts for value in candidates)


def structured_identifiers(doc, title):
    identifiers=set()
    for post in doc.jobposts():
        if fold(plain(post.get('title')))!=fold(title):continue
        value=post.get('identifier')
        if isinstance(value,dict):value=value.get('value')
        if isinstance(value,(str,int)) and str(value).strip():identifiers.add(str(value).strip())
    return identifiers


def applicant_form(body):
    for form in ApplicantForms(body).forms:
        names=' '.join(i.get('name','')+' '+i.get('type','') for i in form['fields']).lower()
        attributes=' '.join(form['attrs'].values()).lower()
        application=bool(re.search(r'apply|applica|recruit|candidate',attributes) or re.search(r'resume|\bcv\b',names))
        if application and form['submit'] and 'email' in names and re.search(r'name|resume|\bcv\b',names):return True
    return False


def verify_vacancy(record, source, client, stamp, observation=None):
    """No successful HEAD, cached page or JSON-LD alone establishes an opening."""
    body, doc = checked_document(record['url'], source, client)
    if canonical_url(doc.url)!=canonical_url(record['url']):raise ValueError('Vacancy redirected to a different URL; identity requires review')
    if not same_title(doc, record['title']):
        from .reviewed_html import reviewed_titles
        if doc.h1 or [fold(t) for t in reviewed_titles(body,source)] != [fold(record['title'])]:
            raise ValueError('Current page does not identify the same vacancy')
    fresh_deadline=next((post.get('validThrough') for post in doc.jobposts() if fold(plain(post.get('title')))==fold(record['title'])),None)
    for post in doc.jobposts():
        if fold(plain(post.get('title'))) == fold(record['title']) and expired(post.get('validThrough'), stamp):
            raise ApplicationClosed('Published application deadline has passed')
    identifiers=structured_identifiers(doc,record['title'])
    if len(identifiers)>1 or (record.get('posting_identifier') and identifiers and str(record['posting_identifier']) not in identifiers):raise ValueError('Vacancy identifier differs from collected position')
    # Capture the identified vacancy independently of application success. A
    # current page with no start supersedes an older feed/cache start as well.
    if observation is not None:
        from .intake import extract_intake
        observation['intake'] = extract_intake(doc.text, stamp)
    reviewed = verify_application(record, source, client)
    if reviewed:
        return dict(reviewed,valid_through=fresh_deadline, vacancy_match='title', inventory=record.get('inventory_evidence', 'not-established'))
    # An actual form on this same, identified vacancy is direct application evidence.
    if applicant_form(body):
        return dict(url=canonical_url(doc.url), method='same-vacancy-applicant-form',valid_through=fresh_deadline, vacancy_match='title',
                    inventory=record.get('inventory_evidence', 'not-established'))
    # Follow only observed calls to action on approved employer/provider hosts.
    targets = []
    for href, label, _ in doc.links:
        if not re.search(r'\bapply\b|solliciteer|solliciteren|bewerben|postuler|candidati|candidarsi|candidatar', fold(label)): continue
        target = canonical_url(urljoin(doc.url, href))
        if urlsplit(target).hostname in source['allowed_hosts'] and target != canonical_url(doc.url): targets.append(target)
    if not targets: raise ValueError('No available vacancy-specific application entry established')
    # Do not treat a redirect to a careers/search page or another requisition as success.
    if not same_requisition(doc.url,targets[0]) and not shares_identifier(record,targets[0]):raise ValueError('Application link lacks a matching vacancy identifier')
    app_body, application = checked_document(targets[0], source, client)
    if canonical_url(application.url)!=targets[0]:raise ValueError('Application redirected to a different URL; identity requires review')
    for post in application.jobposts():
        if fold(plain(post.get('title')))==fold(record['title']) and expired(post.get('validThrough'),stamp):raise ApplicationClosed('Application deadline has passed')
    application_ids=structured_identifiers(application,record['title'])
    expected_ids=identifiers or ({str(record['posting_identifier'])} if record.get('posting_identifier') else set())
    if expected_ids and application_ids and expected_ids!=application_ids:raise ValueError('Application requisition differs from vacancy')
    if not same_title(application, record['title']) and (application.jobposts() or any(classify_role(h) for h in application.h1)):raise ValueError('Application identifies a different vacancy')
    if not same_title(application, record['title']) and not same_requisition(doc.url,application.url): raise ValueError('Application page does not identify the same vacancy')
    if not applicant_form(app_body): raise ValueError('Applicant form not established; application may require JavaScript or an account')
    return dict(url=canonical_url(application.url), method='linked-same-vacancy-applicant-form',valid_through=fresh_deadline, vacancy_match='title' if same_title(application,record['title']) else 'vacancy-path-application-child',
                inventory=record.get('inventory_evidence', 'not-established'))
