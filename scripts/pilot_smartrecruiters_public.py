"""GET-only, bounded SmartRecruiters public-HTML same-posting diagnostic.

No SmartRecruiters API, browser, POST, application submission, account, guessing
apply URLs, or catalog modifications. Re-uses current official job URLs from
the versioned catalog solely for a small preflight. A visible form candidate
does NOT automatically satisfy policy-v2 source ownership or location gates.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from urllib.parse import urljoin, urlsplit
from urllib.error import HTTPError

from collector.classify import canonical_url, fold, plain
from collector.pipeline import ROOT
from collector.runtime import BudgetClient
from collector.universal import Document
from collector.verification import applicant_form, same_title, same_requisition, shares_identifier, structured_identifiers

JOB = re.compile(r'^/([^/]+)/(\d{15})(?:[-/]|$)')
APPLY_LABEL = re.compile(r'\bapply\b|\bpostuler\b|\bcandidater\b', re.I)
HOST = 'jobs.smartrecruiters.com'


def candidates(catalog):
    rows = []
    for record in catalog.get('jobs', []):
        if (record.get('status') != 'unverified'
                or record.get('internship_type') != 'internship'
                or record.get('country') not in ('FR', 'BE')):
            continue
        url = urlsplit(record.get('url', ''))
        match = JOB.match(url.path) if url.hostname == HOST else None
        if match:
            rows.append(dict(record, _target_id=match.group(2), _tenant=match.group(1)))
    return sorted(rows, key=lambda r: (r['country'], r['source_id'], r['_target_id']))


def official_same_id_links(document, record):
    match = JOB.match(urlsplit(record['url']).path)
    if not match:
        return []
    augmented = dict(record, posting_identifier=match.group(2))
    targets = []
    for href, label, _ in document.links:
        if not APPLY_LABEL.search(fold(label)):
            continue
        target = canonical_url(urljoin(document.url, href))
        p = urlsplit(target)
        if p.hostname != HOST or target == canonical_url(document.url):
            continue
        # Only CTA actually published on the vacancy, never a guessed route.
        if same_requisition(document.url, target) or shares_identifier(augmented, target):
            targets.append(target)
    return sorted(set(targets))


def inspect_one(record, client):
    result = dict(source_id=record['source_id'], posting_id=record['_target_id'],
                  tenant=record['_tenant'], country=record['country'],
                  catalog_id=record['id'], page_url=record['url'],
                  outcome='not-verified', application_candidates=0)
    try:
        body, status, final = client.request(record['url'], timeout=9, attempts=1)
        if status != 200 or canonical_url(final) != canonical_url(record['url']):
            result['reason'] = 'non-200-or-redirected-vacancy'
            return result
        doc = Document(body, final)
        result['title_matches'] = same_title(doc, record['title'])
        identifiers = structured_identifiers(doc, record['title'])
        result['structured_ids'] = sorted(identifiers)[:4]
        # An exact public URL and matching title alone cannot prove the
        # application identity if the form is not specific to the posting.
        if not result['title_matches'] or (identifiers and identifiers != {record['_target_id']}):
            result['reason'] = 'current-title-or-posting-identity-not-established'
            return result
        if applicant_form(body, strict=True) and identifiers == {record['_target_id']}:
            result.update(outcome='same-id-visible-enabled-form-candidate',
                          reason='title-and-structured-id-and-strict-form')
            return result
        targets = official_same_id_links(doc, record)
        result['application_candidates'] = len(targets)
        if len(targets) != 1:
            result['reason'] = 'no-unique-published-same-id-CTA'
            return result
        target = targets[0]
        app_body, app_status, app_final = client.request(target, timeout=9, attempts=1)
        if app_status != 200 or canonical_url(app_final) != target:
            result['reason'] = 'CTA-target-not-current'
            return result
        app = Document(app_body, app_final)
        app_ids = structured_identifiers(app, record['title'])
        result['application_structured_ids'] = sorted(app_ids)[:4]
        if (app_ids != {record['_target_id']} or not same_title(app, record['title'])
                or not applicant_form(app_body, strict=True)):
            result['reason'] = 'CTA-form-title-id-or-enabled-submit-missing'
            return result
        result.update(outcome='same-id-visible-enabled-form-candidate',
                      reason='official-observed-CTA-and-strict-form')
        return result
    except Exception as exc:
        result['reason'] = 'read-failed:' + str(exc)[:140]
        if isinstance(exc, HTTPError) and exc.code == 429:
            result['rate_limited'] = True
        return result


def run(catalog, client, *, max_positions=12):
    rows = candidates(catalog)
    if len(rows) > max_positions:
        raise ValueError('Sample exceeds reviewed bounded job count')
    client.redirect_scope_allowed = lambda url: urlsplit(url).hostname == HOST
    start_reqs = client.requests
    started = datetime.now(timezone.utc).isoformat()
    out = []
    for index, record in enumerate(rows):
        result = inspect_one(record, client)
        out.append(result)
        if result.get('rate_limited'):
            out.extend(dict(catalog_id=r['id'], source_id=r['source_id'],
                            posting_id=r['_target_id'], outcome='not-tested',
                            reason='same-host-HTTP-429-quarantine')
                       for r in rows[index + 1:])
            break
    return {
        'started_at_utc': started, 'ended_at_utc': datetime.now(timezone.utc).isoformat(),
        'catalog_updated_at': catalog.get('updated_at'),
        'selected_catalog_records': len(rows),
        'visited_records': len([o for o in out if o['outcome'] != 'not-tested']),
        'http_requests': client.requests - start_reqs,
        'bytes_read': client.bytes,
        'browser_renderings': 0, 'posts': 0,
        'candidate_form_results': sum(x.get('outcome') == 'same-id-visible-enabled-form-candidate' for x in out),
        'by_outcome': dict(Counter(x['outcome'] for x in out)),
        'results': out,
        'limits': ('Only catalog FR/BE unverified official SmartRecruiters links, '
                   'GET robots-aware and same-host redirects; no API. '
                   'These diagnostics are not policy-v2 verification, and zero '
                   'or missing form is not evidence that an application is closed.'),
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--catalog', type=Path, default=ROOT / 'data/catalog.json')
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    client = BudgetClient(seconds=90, max_requests=30, delay=.6)
    report = run(json.loads(args.catalog.read_text()), client)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(report, ensure_ascii=False))


if __name__ == '__main__':
    main()
