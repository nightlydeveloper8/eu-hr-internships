"""Render the source audit from versioned publications without running collectors.

Pass the pinned publication HEAD and the fourteen selected Actions run IDs
(newest first). Git history provides pre-window state for the warm replay.
"""

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import timedelta
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import urlsplit
from zipfile import ZipFile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from collector import cadence  # noqa: E402
from collector.classify import canonical_url  # noqa: E402

UNKNOWN = 'non dimostrato'
METRICS = ('records_inspected', 'matching', 'internships', 'requests', 'get', 'bytes_read', 'duration_seconds')
OUTCOMES = ('ok', 'partial', 'failed', 'blocked')
RUN_URL = 'https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/'


def git(*args):
    return subprocess.check_output(['git', *args], text=True)


def snapshot(sha, name):
    return json.loads(git('show', f'{sha}:data/{name}.json'))


@dataclass
class Metrics:
    counts: Counter = field(default_factory=Counter)
    totals: Counter = field(default_factory=Counter)
    measured: Counter = field(default_factory=Counter)
    opened: set = field(default_factory=set)
    classified: set = field(default_factory=set)

    def add(self, report, internships=None):
        self.counts[cadence.outcome(report)] += 1
        for key in METRICS:
            value = report.get(key)
            if key == 'internships':
                value = internships if internships is not None else 0 if report.get('matching') == 0 else None
            if key == 'get' and report['adapter'] != 'eures-search':
                value = report.get('requests')
            if type(value) in (int, float):
                self.totals[key] += value
                self.measured[key] += 1

    @property
    def attempts(self):
        return sum(self.counts.values())

    def value(self, key, average=False):
        measured = self.measured[key]
        if not measured:
            return UNKNOWN
        total = self.totals[key]
        label = f'{total / measured:.2f}' if average else f'{total:.2f}' if key == 'duration_seconds' else str(total)
        if measured != self.attempts:
            return f'{label} ({measured}/{self.attempts} misurati)'
        return label


@dataclass
class Cycle:
    sha: str
    stamp: str
    registry: dict
    reports: dict
    employers: dict
    catalog: dict
    open_by_source: dict
    observed: dict
    classified: dict
    strict_matches: dict


def load_cycle(sha, artifact_dir=None, run_id=None):
    coverage = snapshot(sha, 'coverage')
    catalog = snapshot(sha, 'catalog')
    employers = snapshot(sha, 'employer-collection')
    stamp = coverage['generated_at']
    if employers['generated_at'] != stamp or catalog['last_attempt_at'] != stamp:
        raise ValueError(f'Snapshot misaligned: {sha}')
    registry = {s['id']: s for s in snapshot(sha, 'sources') if s.get('enabled')}
    finished = cadence.timestamp(stamp)
    # Never reuse a stale report from coverage's cumulative source map.
    reports = {r['id']: r for r in coverage['sources'] if r['id'] in registry
               and (checked := cadence.timestamp(r.get('checked_at'))) is not None
               and finished - timedelta(hours=24) <= checked <= finished}
    if len(reports) != len(registry) or len(reports) != coverage['quality']['sources_attempted']:
        raise ValueError(f'Missing current observations: {sha}')
    open_sources = defaultdict(set)
    observed = defaultdict(set)
    classified = defaultdict(set)
    for j in catalog['jobs']:
        sid = j['source_id']
        if j['status'] == 'open':
            open_sources[sid].add(j['id'])
        if j.get('internship_type') != 'internship' or sid not in reports:
            continue
        checked = cadence.timestamp(reports[sid]['checked_at'])
        if cadence.timestamp(j.get('last_seen_at')) == checked:
            classified[sid].add(j['id'])
        if j['status'] == 'open' and cadence.timestamp(j.get('last_verified_at')) == checked:
            observed[sid].add(j['id'])
    strict_matches = {}
    if artifact_dir is not None:
        for path in (artifact_dir / str(run_id)).glob('employer-shard-*.zip'):
            shard = int(path.stem.rsplit('-', 1)[-1])
            with ZipFile(path) as archive:
                payload = json.loads(archive.read(f'shard-{shard}.json'))
            if (str(payload['run_id']).split('/')[0] != str(run_id)
                    or payload['shard'] != shard or not payload['complete']):
                raise ValueError(f'Artifact does not match run {run_id}, shard {shard}')
            for part in payload['parts']:
                report = part['report']
                sid = report['id']
                if reports.get(sid) != report:
                    raise ValueError(f'Artifact does not match coverage: {sha} / {sid}')
                if 'matching' in report and report['matching'] != len(part['jobs']):
                    raise ValueError(f'Match count does not match artifact: {sha} / {sid}')
                strict_matches[sid] = sum(j.get('internship_type') == 'internship'
                                          for j in part['jobs'])
    return Cycle(sha, stamp, registry, reports, employers['summary'], catalog,
                 open_sources, observed, classified, strict_matches)


def durable_failure(source, report):
    """Only evidence on configured seeds, never on arbitrary vacancy paths."""
    if cadence.outcome(report) not in ('failed', 'blocked') or report.get('pages_read'):
        return None
    seeds = {canonical_url(u) for u in source.get('start_urls', [])}
    if not seeds or report.get('page_errors_truncated'):
        return None
    errors = {canonical_url(e['url']): e['error'] for e in report.get('page_errors', [])
              if e.get('url', '').startswith(('https://', 'http://'))}
    reasons = []
    for seed in sorted(seeds):
        error = errors.get(seed, '')
        if re.search(r'Name or service not known|nodename nor servname|NXDOMAIN', error, re.I):
            reasons.append((seed, 'DNS'))
        elif urlsplit(seed).path in ('', '/') and re.search(r'HTTP Error:? 404\b', error):
            reasons.append((seed, '404 sulla radice'))
        elif error.startswith('robots.txt disallows ') and not error.startswith('robots.txt disallows redirect '):
            reasons.append((seed, 'robots.txt'))
        else:
            return None
    return tuple(reasons)


def replay(cycles, history, *, prior=None):
    state = {}
    previous_open = set()
    already_open = set()
    persistence = {}
    for cycle in history:
        previous_open = set(cycle.open_by_source)
        already_open.update(set().union(*cycle.open_by_source.values()))
        state = {sid: cadence.observe(state.get(sid, {}), report, report.get('matching'))
                 for sid, report in cycle.reports.items()}
        persistence = record_failures(cycle, persistence)
    if prior is not None:
        previous_open = set(prior.open_by_source)
        already_open.update(set().union(*prior.open_by_source.values()))
    baseline_seen = set(already_open)
    simulated_seen = set(already_open)
    baseline_first = {}
    replay_first = {}
    skipped = []
    replay_rows = []
    for cycle in cycles:
        next_open = set(previous_open)
        saved = Metrics()
        for sid, report in cycle.reports.items():
            source = cycle.registry[sid]
            at = cadence.timestamp(report['checked_at'])
            for job_id in cycle.observed[sid] - baseline_seen:
                baseline_first[job_id] = (at, sid)
            baseline_seen.update(cycle.observed[sid])
            if not cadence.due(source, state.get(sid, {}), at, previous_open):
                saved.add(report)
                skipped.append((cycle.sha, sid, cadence.interval(source, state[sid], at, previous_open)))
                continue
            state[sid] = cadence.observe(state.get(sid, {}), report,
                                         cycle.strict_matches.get(sid, report.get('matching')))
            for job_id in cycle.observed[sid] - simulated_seen:
                replay_first[job_id] = at
            simulated_seen.update(cycle.observed[sid])
            next_open.discard(sid)
            if cycle.open_by_source.get(sid):
                next_open.add(sid)
        state = {sid: value for sid, value in state.items() if sid in cycle.registry}
        previous_open = next_open
        persistence = record_failures(cycle, persistence)
        replay_rows.append(saved)
    delayed = {j: (at, sid, replay_first.get(j)) for j, (at, sid) in baseline_first.items()
               if replay_first.get(j) != at}
    return replay_rows, skipped, delayed, persistence


def record_failures(cycle, previous):
    result = {}
    for sid, report in cycle.reports.items():
        reason = durable_failure(cycle.registry[sid], report)
        if reason:
            old_reason, count = previous.get(sid, (None, 0))
            result[sid] = reason, count + 1 if reason == old_reason else 1
    return result


def table(headers, rows):
    print('| ' + ' | '.join(headers) + ' |')
    print('| ' + ' | '.join('---' for _ in headers) + ' |')
    for row in rows:
        print('| ' + ' | '.join(str(value).replace('|', r'\|') for value in row) + ' |')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('head')
    parser.add_argument('runs', nargs=14, type=int)
    parser.add_argument('--artifact-dir', type=Path)
    args = parser.parse_args()
    commits = git('log', '--first-parent', '--format=%H', '--grep=^Refresh all-employer HR internship collection$', args.head).splitlines()
    run_for = dict(zip(commits[:14], args.runs))
    history = [load_cycle(sha) for sha in reversed(commits[14:])]
    cycles = [load_cycle(sha, args.artifact_dir, run_for[sha]) for sha in reversed(commits[:14])]
    keys = ('requests', 'get', 'bytes_read', 'duration_seconds')
    sources = defaultdict(Metrics)
    groups = defaultdict(Metrics)
    types = {}
    all_cost = Metrics()
    all_groups = defaultdict(Metrics)
    for cycle in cycles:
        for sid, report in cycle.reports.items():
            kind = cycle.registry[sid]['adapter']
            types[sid] = kind
            for metrics in (sources[sid], groups[kind], all_cost):
                metrics.add(report, cycle.strict_matches.get(sid))
                metrics.opened.update(cycle.observed[sid])
                metrics.classified.update(cycle.classified[sid])
            all_groups[report['adapter']].add(report)
    print('## Cicli pubblicati e riscontri')
    print()
    table(('Commit', 'Run', 'Fine UTC', 'Fonti', 'Datori tentati', 'ID', 'Stage aperti a fine ciclo'),
          ((c.sha[:7], f'[{run_for[c.sha]}]({RUN_URL}{run_for[c.sha]})', c.stamp,
            len(c.reports), c.employers['attempted'], len(c.catalog['jobs']),
            sum(j['status'] == 'open' and j.get('internship_type') == 'internship' for j in c.catalog['jobs']))
           for c in cycles))
    print()
    print('## Rendimento per source_type')
    print()
    def group_row(kind, metrics):
        unit_costs = (f'{metrics.totals[key] / len(metrics.opened):.2f}'
                      if metrics.opened and metrics.measured[key] == metrics.attempts else UNKNOWN
                      for key in ('requests', 'bytes_read', 'duration_seconds'))
        label = f'**{kind}**' if kind == 'universal-employer' else kind
        return (label, metrics.attempts, *(metrics.value(k) for k in keys),
                len(metrics.opened), *unit_costs)
    table(('Tipo configurato', 'Tentativi', 'Richieste', 'GET BudgetClient', 'Byte', 'Secondi-fonte',
           'Stage aperti osservati (ID)', 'Richieste / stage', 'Byte / stage', 'Secondi / stage'),
          [group_row(kind, metrics) for kind, metrics in sorted(groups.items())]
          + [group_row('Totale', all_cost)])
    print()
    print(f"Adapter universale effettivo, fallback inclusi: {all_groups['universal-employer'].value('requests')} "
          f"richieste. La riga per tipo configurato mantiene il costo del fallback assegnato alla fonte originaria.")
    print()
    print('## Replay in ordine temporale')
    print()
    warm, skipped, delayed, persistence = replay(cycles, history)
    cold, cold_skips, cold_delayed, _ = replay(cycles, [], prior=history[-1] if history else None)
    baseline = {(c.sha, sid): report for c in cycles for sid, report in c.reports.items()}
    savings = Metrics()
    for sha, sid, _ in skipped:
        savings.add(baseline[sha, sid])
    print(f'Avvio a freddo: {len(cold_skips)} tentativi evitati, '
          f"{sum(row.totals['requests'] for row in cold)} richieste evitate, "
          f"{sum(row.totals['duration_seconds'] for row in cold) / 60:.2f} minuti-fonte evitati, "
          f'{len(cold_delayed)} ID con prima osservazione aperta spostata nel campione.')
    print()
    print(f'Replay con {len(history)} pubblicazioni anteriori: {len(skipped)} tentativi evitati '
          f'({sum(days == 7 for _, _, days in skipped)} settimanali, '
          f'{sum(days == 30 for _, _, days in skipped)} mensili).')
    print(f"Risparmio osservabile: {savings.value('requests')} richieste BudgetClient "
          f"({savings.value('get')} GET BudgetClient), "
          f"{savings.value('bytes_read')} byte e {savings.totals['duration_seconds'] / 60:.2f} minuti-fonte "
          f"({savings.measured['duration_seconds']}/{len(skipped)} durate misurate).")
    print(f"Richieste prima → dopo: {all_cost.totals['requests']} → "
          f"{all_cost.totals['requests'] - savings.totals['requests']}. "
          f"Match HR studenti nei tentativi saltati: {savings.value('matching')}.")
    print()
    table(('Commit', 'Tentativi evitati', 'Richieste evitate', 'Minuti-fonte osservati'),
          ((c.sha[:7], m.attempts, m.value('requests') if m.attempts else 0,
            f"{m.totals['duration_seconds'] / 60:.2f}") for c, m in zip(cycles, warm)))
    print()
    missed = sum(later is None for _, _, later in delayed.values())
    print(f'Ritardi osservati nel campione: {len(delayed) - missed}. '
          f'Stage aperti che il replay **avrebbe perso entro la finestra**: **{missed}**. '
          f'Esito definitivo dopo la finestra: {UNKNOWN}.')
    if delayed:
        print()
        table(('ID', 'Fonte iniziale', 'Prima prova UTC', 'Replay UTC', 'Giorni di ritardo'),
              ((job_id, sid, at.isoformat(), later.isoformat() if later else UNKNOWN,
                f'{(later - at).total_seconds() / 86400:.2f}' if later else UNKNOWN)
               for job_id, (at, sid, later) in sorted(delayed.items())))
    print()
    print('## Proposte di disattivazione per guasto persistente')
    print()
    candidates = [(sid, count, ', '.join(f'{reason} su {url}' for url, reason in reasons))
                  for sid, (reasons, count) in sorted(persistence.items()) if count > 14]
    if candidates:
        print(f'{len(candidates)} proposte basate su errori ripetuti a ogni partenza configurata. '
              f'Carattere permanente del guasto: {UNKNOWN}.')
        print()
        table(('Fonte', 'Ultimi cicli consecutivi', 'Evidenza sulle partenze configurate'), candidates)
    else:
        print(f'Nessuna fonte soddisfa il criterio documentale. Guasto permanente: {UNKNOWN}.')
    print()
    print('## Dettaglio per fonte')
    print()
    table(('Fonte', 'Tipo', 'R/P/F/B', 'Posting letti (tot.)', 'Ruoli HR studenti (tot.)',
           'Stage HR classificati (somma)', 'Stage aperti (ID)', 'Richieste medie',
           'GET medi BudgetClient', 'Byte medi', 'Secondi medi'),
          ((sid, types[sid], '/'.join(str(m.counts[k]) for k in OUTCOMES),
            m.value('records_inspected'), m.value('matching'),
            m.value('internships') if m.measured['internships'] == m.attempts
            else f"≥{max(len(m.classified), m.totals['internships'])} · esatto {UNKNOWN}", len(m.opened),
            *(m.value(key, average=True) for key in keys))
           for sid, m in sorted(sources.items())))


if __name__ == '__main__':
    main()
