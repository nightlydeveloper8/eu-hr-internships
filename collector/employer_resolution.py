"""Reviewed, source-scoped recruiting identities; corporate ties are NOT job ownership.

Only a reviewed official publisher name on the *same approved recruiting host*
can match a structured JobPosting hiringOrganization. Company aliases and group
memberships alone are intentionally not sufficient for collection or verification.
"""
from datetime import date
from urllib.parse import urlsplit

from .classify import canonical_url, fold

RELATIONS = frozenset({'official-recruiting-publisher', 'group-parent', 'subsidiary', 'brand', 'shared-ats'})


def name_key(value):
    return ' '.join(fold(str(value or '')).split())


def validate_reviews(reviews, sources):
    """Reject malformed or overbroad grants before the collector starts."""
    by_id = {s['id']: s for s in sources}
    seen = set()
    for review in reviews:
        source = by_id.get(review.get('source_id'))
        if not source:
            raise ValueError('Identity review references unknown source')
        if review.get('relation') not in RELATIONS:
            raise ValueError('Unknown employer identity relation')
        if review.get('company_id') != source.get('company_id') or review.get('source_employer') != source.get('employer'):
            raise ValueError('Identity review source/company mismatch')
        name = review.get('published_name')
        if not isinstance(name, str) or not name.strip():
            raise ValueError('Identity review requires exact published name')
        try:
            date.fromisoformat(review['reviewed_on'])
            evidence = canonical_url(review['evidence_url'])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError('Identity review requires dated HTTPS evidence') from exc
        host = review.get('host')
        if (not isinstance(host, str) or not host or host != host.lower() or
                urlsplit(evidence).hostname != host or host not in source['allowed_hosts']):
            raise ValueError('Identity review must use exact already-approved official host')
        key = (source['id'], name_key(name), host)
        if key in seen:
            raise ValueError('Duplicate source-scoped identity review')
        seen.add(key)
        if review['relation'] == 'official-recruiting-publisher':
            if source.get('adapter') != 'universal-employer':
                raise ValueError('Publisher review is limited to the universal employer crawler')
            if name_key(name) == name_key(source['employer']):
                raise ValueError('Redundant employer identity review')
    return True


def reviewed_source(source, reviews):
    """Attach only official-publisher evidence to a runtime copy; never persist it."""
    scoped = {}
    for review in reviews:
        if (review.get('source_id') == source.get('id') and
                review.get('company_id') == source.get('company_id') and
                review.get('source_employer') == source.get('employer') and
                review.get('relation') == 'official-recruiting-publisher' and
                review.get('host') in source.get('allowed_hosts', [])):
            key = name_key(review['published_name'])
            scoped.setdefault(key, set()).add(review['host'])
    # Group, brand, subsidiary and shared-ATS relations are never grants.
    return dict(source, _reviewed_identity_hosts={key: sorted(hosts) for key, hosts in scoped.items()})


def is_reviewed_publisher(name, source, url):
    """Exact name and exact reviewed host; no inferred domains or group-wide alias."""
    if not url:
        return False
    try:
        host = urlsplit(canonical_url(url)).hostname
    except (TypeError, ValueError):
        return False
    return host in source.get('_reviewed_identity_hosts', {}).get(name_key(name), ())
