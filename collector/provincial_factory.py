"""Offline workflow snapshots; no collection, network access or candidate promotion."""
import hashlib
import json
import math
import os
import tempfile
import re
import subprocess
from collections import Counter
from datetime import datetime, timedelta, timezone
from urllib.parse import urlsplit
from .company_registry import company_key
from .verification import blocked_error, expired, verified_job

SCHEMA_VERSION = 1
FRESHNESS = timedelta(hours=48)
STATES = ('complete', 'partial', 'incomplete', 'blocked', 'failed', 'not-attempted')


def encode(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode()


def digest(value):
    return hashlib.sha256(value).hexdigest()


def read(path):
    return json.loads(path.read_text())


def atomic_write(path, payload):
    """Readers see either the old complete snapshot or the new one."""
    if path.exists() and path.read_bytes() == payload:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix='.factory-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def clock(value):
    try:
        result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except (ValueError, TypeError, AttributeError):
        raise ValueError('Invalid timestamp; expected ISO 8601 with timezone') from None
    if result.tzinfo is None:
        raise ValueError('Timestamp must include timezone')
    return result.astimezone(timezone.utc)


def recent(value, at):
    try:
        return timedelta(0) <= clock(at) - clock(value) <= FRESHNESS
    except (ValueError, TypeError, AttributeError):
        return False


def deadline_open(job, at):
    """Honor application deadlines independently of the verification's 48h age."""
    try:
        # expired() treats a date-only deadline as inclusive. Normalize the
        # evaluation date to UTC even when --at supplies another timezone.
        return not expired(job.get('valid_through'), clock(at).isoformat())
    except (ValueError, TypeError, AttributeError):
        return False


def workspace(root, slug):
    if not re.fullmatch(r'[a-z][a-z0-9-]*', slug) or not (root / f'data/{slug}-geography.json').is_file():
        raise ValueError('Unknown provincial geography')
    return root / '.staging' / 'factory' / slug


def source_state(report):
    if not report:
        return 'not-attempted'
    if report.get('status') == 'ok' and report.get('complete') is True and report.get('inventory_complete') is not False:
        return 'complete'
    if report.get('status') in ('blocked', 'failed'):
        errors = str(report.get('error', '')) + str(report.get('page_errors', []))
        return 'blocked' if report.get('status') == 'blocked' or blocked_error(Exception(errors)) else 'failed'
    return 'partial' if report.get('records_inspected', 0) else 'incomplete'


def snapshot(root, slug, at):
    workspace(root, slug)
    clock(at)
    companies = [c for c in read(root / 'data/companies.json') if c.get(slug + '_research')]
    sources = {s['id']: s for s in read(root / 'data/sources.json')}
    reports = {r['id']: r for r in read(root / 'data/coverage.json')['sources']}
    geography = read(root / f'data/{slug}-geography.json')
    region = geography['province']['nuts2_code']
    ids = sorted({sid for c in companies for sid in c.get('source_ids', [])})
    rows = []
    for sid in ids:
        r = reports.get(sid, {})
        rows.append(dict(id=sid, enabled=bool(sources.get(sid, {}).get('enabled')), state=source_state(r),
                         fresh=recent(r.get('checked_at'), at), checked_at=r.get('checked_at'), report_present=bool(r)))
    by_id = {r['id']: r for r in rows}
    employers = []
    for c in sorted(companies, key=lambda c: c['id']):
        configured = [by_id[s] for s in c.get('source_ids', []) if by_id[s]['enabled']]
        employers.append(dict(id=c['id'], configured=bool(configured), complete_recent=bool(configured) and all(
            r['state'] == 'complete' and r['fresh'] for r in configured), municipality_codes=sorted({
                p['municipality_code'] for p in c.get('workplaces', []) if p.get('region_code') == region
                and p.get('location_confidence') == 'confirmed' and p.get('municipality_code')})))
    names = {company_key(n) for c in companies for n in [c['name']] + c.get('aliases', [])}
    jobs = [j for j in read(root / 'data/catalog.json')['jobs'] if region in j.get('region_codes', [])
            and (j.get('source_id') in ids or company_key(j.get('employer', '')) in names)
            and j.get('internship_type') == 'internship' and verified_job(j, at) and deadline_open(j, at)]
    municipalities = [dict(name=m['name'], identified=sum(m['cbs_code'] in e['municipality_codes'] for e in employers),
        configured=sum(e['configured'] and m['cbs_code'] in e['municipality_codes'] for e in employers),
        complete_recent=sum(e['complete_recent'] and m['cbs_code'] in e['municipality_codes'] for e in employers))
        for m in sorted(geography['municipalities'], key=lambda m: m['name'])]
    queue = workspace(root, slug) / 'handoff.json'
    candidates = read(queue)['candidates'] if queue.exists() else []
    anomalies = [dict(source_id=r['id'], reason='missing-source-config' if r['id'] not in sources else
        'disabled' if not r['enabled'] else 'stale-or-invalid-time' if not r['fresh'] else r['state'])
        for r in rows if not r['enabled'] or not r['fresh'] or r['state'] != 'complete']
    priority = {'missing-source-config': 0, 'blocked': 1, 'failed': 2, 'stale-or-invalid-time': 3}
    anomalies.sort(key=lambda r: (priority.get(r['reason'], 4), r['source_id']))
    return dict(schema_version=1, province=slug, as_of=at, sources=rows, identified_employers=len(employers),
        configured_employers=sum(e['configured'] for e in employers),
        unconfigured_employer_ids=sorted(e['id'] for e in employers if not e['configured']), complete_recent_employers=sum(e['complete_recent'] for e in employers),
        configured_sources=sum(r['enabled'] for r in rows), complete_recent_sources=sum(r['enabled'] and r['fresh'] and r['state'] == 'complete' for r in rows),
        source_states=dict(Counter(r['state'] for r in rows)), stale_sources=sum(not r['fresh'] for r in rows), municipalities=municipalities,
        verified_hr_internship_ids=sorted({j['id'] for j in jobs}), review_candidates=len(candidates), anomalies=anomalies)


def compact(report, source=None):
    lines = [f"Province: {report['province']} | as of {report['as_of']} | freshness: 48h",
        f"Employers: identified {report['identified_employers']}; configured {report['configured_employers']}; complete/recent {report['complete_recent_employers']}",
        f"Sources: configured {report['configured_sources']}; complete/recent {report['complete_recent_sources']}; stale/invalid/missing timestamp {report['stale_sources']}",
        'Collection states (independent of freshness): ' + '; '.join(f'{s}={report["source_states"].get(s, 0)}' for s in STATES),
        f"Verified HR internships (policy v2, <=48h): {len(report['verified_hr_internship_ids'])}; untrusted review candidates: {report['review_candidates']}",
        'Municipality | identified / configured / complete-recent employers (overlapping totals)']
    lines.extend(f"{m['name']} | {m['identified']} / {m['configured']} / {m['complete_recent']}" for m in report['municipalities'][:60])
    if len(report['municipalities']) > 60:
        lines.append('Other municipalities omitted; use saved geography and registry files.')
    lines.append(f"Priority anomalies: {len(report['anomalies'])} (first 10)")
    lines.extend(f"{r['source_id']}: {r['reason']}" for r in report['anomalies'][:10])
    if source:
        row = next((r for r in report['sources'] if r['id'] == source), None)
        if row is None:
            raise ValueError('Source is not attached to this province')
        lines.append(f"Source {source}: state={row['state']}; fresh={row['fresh']}; checked_at={row['checked_at']}")
        lines.append(f"Full evidence: data/coverage.json, sources[id={source}] (not printed)")
    lines.append('Evidence: data/coverage.json; data/catalog.json; data/companies.json; provincial geography. No network requests.')
    return '\n'.join(lines) + '\n'


def versions(root, slug):
    base = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
    paths = sorted({*root.glob('collector/**/*.py'), *root.glob('scripts/**/*.py'), *root.glob('requirements*.txt')})
    code = {str(p.relative_to(root)): digest(p.read_bytes()) for p in paths}
    paths = [root / 'data' / name for name in ('companies.json', 'sources.json', 'coverage.json', 'catalog.json', f'{slug}-geography.json')]
    paths.append(workspace(root, slug) / 'handoff.json')
    inputs = {str(p.relative_to(root)): digest(p.read_bytes()) if p.exists() else None for p in paths}
    return dict(git_commit=base, code_sha256=digest(encode(code)), input_sha256=digest(encode(inputs)), input_files=inputs)


def checkpoint(root, slug, at, resume=False):
    folder = workspace(root, slug)
    path = folder / 'checkpoint.json'
    version = versions(root, slug)
    report = snapshot(root, slug, at)
    if versions(root, slug) != version:
        raise ValueError('Code or inputs changed during snapshot; retry')
    state_hash = digest(encode({k: v for k, v in report.items() if k != 'as_of'}))
    old = read(path) if path.exists() else None
    reusable = bool(old and old.get('schema_version') == SCHEMA_VERSION and old.get('province') == slug
        and old.get('versions') == version and old.get('state_sha256') == state_hash
        and (folder / 'checkpoints' / (digest(encode(old)) + '.json')).is_file()
        and (folder / 'checkpoints' / (digest(encode(old)) + '.json')).read_bytes() == encode(old)
        and timedelta(0) <= clock(at) - clock(old['created_at']) < FRESHNESS)
    if reusable:
        return old, 'reused'
    if resume:
        raise ValueError('Checkpoint missing or obsolete: rerun checkpoint to recompute; no command executed')
    pending = [dict(source_id=r['source_id'], action=r['reason']) for r in report['anomalies']]
    pending.extend(dict(employer_id=cid, action='review-and-configure-official-source') for cid in report['unconfigured_employer_ids'])
    if report['review_candidates']:
        pending.append(dict(action='manually-review-untrusted-candidates', count=report['review_candidates']))
    result = dict(schema_version=1, province=slug, phase='offline-review', created_at=at, versions=version,
        state_sha256=state_hash, processed_sources=[dict(id=r['id'], checked_at=r['checked_at'], state=r['state'], fresh=r['fresh'])
        for r in report['sources'] if r['report_present']], pending_tasks=pending,
        verified_hr_internship_ids=report['verified_hr_internship_ids'], next_command=f'python3 scripts/provincial_factory.py summary {slug}',
        capabilities=dict(provincial_workflow_checkpoint=True, mid_crawler_resume=False))
    folder.mkdir(parents=True, exist_ok=True)
    history = folder / 'checkpoints'
    history.mkdir(exist_ok=True)
    payload = encode(result)
    atomic_write(history / (digest(payload) + '.json'), payload)
    atomic_write(path, payload)
    return result, 'created'


def import_handoff(root, slug, path, at):
    """All fields are inert claims, including a claimed verified review status."""
    folder = workspace(root, slug)
    clock(at)
    municipalities = {m['name'] for m in read(root / f'data/{slug}-geography.json')['municipalities']}
    payload = read(path)
    if not isinstance(payload, dict) or set(payload) != {'schema_version', 'candidates'} or type(payload['schema_version']) is not int or payload['schema_version'] != 1 or not isinstance(payload['candidates'], list):
        raise ValueError('Expected schema_version=1 and candidates array')
    fields = {'employer', 'official_career_url', 'municipality', 'evidence_url', 'observed_at', 'confidence', 'review_status'}
    queue_path = folder / 'handoff.json'
    queue = read(queue_path) if queue_path.exists() else dict(schema_version=1, province=slug, candidates=[])
    existing = {c['id']: c for c in queue['candidates']}
    for candidate in payload['candidates']:
        if not isinstance(candidate, dict) or set(candidate) != fields:
            raise ValueError('Candidate fields must match the documented handoff schema')
        for key in fields - {'confidence'}:
            value = candidate[key]
            if not isinstance(value, str) or not value.strip() or len(value) > 1000 or any(ord(c) < 32 or ord(c) == 127 for c in value):
                raise ValueError('Invalid text field: ' + key)
        if candidate['municipality'] not in municipalities:
            raise ValueError('Municipality is not in selected province')
        for key in ('official_career_url', 'evidence_url'):
            try:
                url = urlsplit(candidate[key])
            except ValueError:
                raise ValueError('Malformed candidate URL') from None
            if url.scheme != 'https' or not url.hostname or url.username or url.password or any(c.isspace() for c in candidate[key]):
                raise ValueError('Expected HTTPS URL without credentials')
        confidence = candidate['confidence']
        if isinstance(confidence, bool) or not isinstance(confidence, (int, float)) or not math.isfinite(confidence) or not 0 <= confidence <= 1:
            raise ValueError('confidence must be numeric in [0,1]')
        if clock(candidate['observed_at']) > clock(at):
            raise ValueError('observed_at cannot be in the future')
        cid = digest(encode(candidate))
        if cid not in existing:
            existing[cid] = dict(candidate, id=cid, claimed_review_status=candidate['review_status'], review_status='pending',
                                 trust='unverified-external-data', imported_at=at)
    queue['candidates'] = [existing[k] for k in sorted(existing)]
    folder.mkdir(parents=True, exist_ok=True)
    atomic_write(queue_path, encode(queue))
    return len(queue['candidates'])
