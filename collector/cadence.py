"""Opt-in source scheduling from completed, published observations."""

from datetime import datetime, timedelta
import os

from .public_sources import PUBLIC_API_ADAPTERS

DAILY_ADAPTERS = frozenset((*PUBLIC_API_ADAPTERS, 'greenhouse', 'lever',
    'recruitee', 'personio-xml', 'smartrecruiters', 'ashby', 'workable-public',
    'amazon-search', 'workday', 'teamtailor', 'talentech'))
HR_WINDOW = timedelta(days=60)


def enabled():
    return os.environ.get('COLLECTOR_SOURCE_CADENCE') == '1'


def timestamp(value):
    try:
        result = datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return None
    return result if result.utcoffset() is not None else None


def outcome(report):
    status = report.get('status')
    if status == 'failed':
        error = str(report.get('error', '')).lower()
        if report.get('access_state') == 'blocked' or any(marker in error for marker in ('robots.txt disallows', 'public source access blocked')):
            return 'blocked'
    return status


def observe(previous, report, hr_count):
    """Advance after an execution. Unknown counts cannot establish an empty run."""
    observed = report['checked_at']
    at = timestamp(observed)
    before = timestamp(previous.get('last_attempt'))
    if at is None or (before is not None and at <= before):
        return dict(previous)
    state = {'last_attempt': observed, 'failure_streak': 0}
    if previous.get('last_hr'):
        state['last_hr'] = previous['last_hr']
    if hr_count:
        state['last_hr'] = observed
    result = outcome(report)
    if (result == 'ok' and hr_count == 0 and report.get('inventory_complete', True)
            and (report.get('records_inspected', 0) or report.get('explicit_empty')
                 or report.get('complete') is True)):
        state['empty_since'] = previous.get('empty_since', observed)
    if result in ('failed', 'blocked'):
        reason = report.get('error') or report.get('access_state')
        if reason:
            state.update(failure_streak=previous.get('failure_streak', 0) + 1,
                         failure_reason=reason)
    return state


def interval(source, state, at, open_sources):
    if source['id'] in open_sources or source['adapter'] in DAILY_ADAPTERS:
        return 1
    last_hr = timestamp(state.get('last_hr'))
    if last_hr is not None and at - last_hr <= HR_WINDOW:
        return 1
    if state.get('failure_streak', 0) > 14 and state.get('failure_reason'):
        return 30
    empty_since = timestamp(state.get('empty_since'))
    if empty_since is not None and at - empty_since >= HR_WINDOW:
        return 7
    return 1


def due(source, state, at, open_sources):
    days = interval(source, state, at, open_sources)
    last = timestamp(state.get('last_attempt'))
    return days == 1 or last is None or at - last >= timedelta(days=days)


def select(sources, catalog, coverage, at):
    open_sources = {job['source_id'] for job in catalog.get('jobs', [])
                    if job.get('status') == 'open'}
    states = {report['id']: report.get('cadence', {}) for report in coverage.get('sources', [])}
    return [source for source in sources
            if due(source, states.get(source['id'], {}), at, open_sources)]
