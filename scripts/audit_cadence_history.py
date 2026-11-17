"""Read-only counterfactual on versioned daily source coverage (never schedules crawls).

Use: python -m scripts.audit_cadence_history --start 2026-11-04 --end 2026-11-17
Needs repository git history. A selected snapshot is the latest commit *within each UTC day*.
Only source reports whose checked_at falls on that day count as fresh observations.
Missing days are unknown, not empty / failed runs. Counterfactuals cannot establish
no missed openings or monetary savings.
"""
import argparse
from collections import defaultdict
from datetime import date
import json
import subprocess


def git(*args):
    return subprocess.check_output(('git',) + args, text=True)


def snapshots(start, end):
    # log ordered newest first. Final versioned coverage per date is sufficient
    # for a conservative daily recheck comparison; intermediate runs excluded.
    lines = git('log', f'--since={start}T00:00:00Z',
                f'--until={end}T23:59:59Z', '--format=%H|%ad',
                '--date=short', '--', 'data/coverage.json').splitlines()
    days = {}
    for line in lines:
        sha, day = line.split('|', 1)
        if start <= day <= end:
            days.setdefault(day, sha)
    return days


def covered_observations(day, coverage):
    for r in coverage.get('sources', []):
        if (r.get('checked_at') or '')[:10] != day:
            continue
        if not r.get('id') or type(r.get('requests')) is not int:
            continue
        yield r


def no_hr_complete(r):
    # Missing/partial/blocked and malformed inventories are NEVER interpreted
    # as "not productive". This is a safety rule, not an objective ranking.
    return (r.get('status') == 'ok'
            and r.get('complete', True) is not False
            and r.get('closure_complete', True) is not False
            and r.get('matching', 0) == 0
            and r.get('records_inspected', 0) >= 0)


def run_backtest(day_rows):
    source_streak = defaultdict(int)
    previous_observed = {}
    totals = dict(requests=0, bytes=0, renderings=0, seconds=0.0, fresh_reports=0)
    saved = dict(requests=0, bytes=0, renderings=0, seconds=0.0,
                 source_day_skips=0, future_matching_leads_on_skipped_days=0,
                 delayed_source_days=0)
    by_day = []
    for day in sorted(day_rows):
        day_tot = dict(requests=0, bytes=0, renderings=0, seconds=0.0,
                       fresh_reports=0, shadow_skips=0)
        d = date.fromisoformat(day)
        for r in day_rows[day]:
            sid = r['id']
            calls = r.get('requests', 0)
            size = r.get('bytes_read', 0)
            render = r.get('rendered_pages', 0)
            secs = r.get('duration_seconds', 0.0)
            vals = (calls if type(calls) is int else 0,
                    size if type(size) is int else 0,
                    render if type(render) is int else 0,
                    secs if isinstance(secs, (int, float)) else 0)
            for dst in (totals, day_tot):
                dst['requests'] += vals[0]
                dst['bytes'] += vals[1]
                dst['renderings'] += vals[2]
                dst['seconds'] += vals[3]
                dst['fresh_reports'] += 1
            prev = previous_observed.get(sid)
            if prev is not None and (d - prev).days > 2:
                source_streak[sid] = 0
            # A *shadow* alternate-day policy. This would only withhold
            # sources which had at least 3 actual consecutive successful zero-
            # HR observations before this day. It does not change production.
            would_skip = source_streak[sid] >= 3 and d.day % 2 == 0
            if would_skip:
                saved['source_day_skips'] += 1
                day_tot['shadow_skips'] += 1
                saved['requests'] += vals[0]
                saved['bytes'] += vals[1]
                saved['renderings'] += vals[2]
                saved['seconds'] += vals[3]
                count = r.get('matching', 0) if type(r.get('matching')) is int else 0
                if count > 0:
                    saved['delayed_source_days'] += 1
                    saved['future_matching_leads_on_skipped_days'] += count
                    source_streak[sid] = 0
                # In a shadow skip, the next real check follows a gap; we
                # intentionally do not use the skipped observation to qualify.
                previous_observed[sid] = d
                continue
            if no_hr_complete(r):
                source_streak[sid] += 1
            else:
                source_streak[sid] = 0
            previous_observed[sid] = d
        by_day.append(dict(day=day, **day_tot))
    result = dict(snapshot_days=len(day_rows), days=sorted(day_rows),
                  totals=totals, counterfactual=saved,
                  potential_request_reduction_pct=round(100*saved['requests']/totals['requests'],2) if totals['requests'] else None,
                  safety="Shadow replay only; cannot guarantee zero missed internships")
    return result, by_day


def analyze(start, end):
    days = snapshots(start, end)
    day_rows = {}
    for day, sha in days.items():
        coverage = json.loads(git('show', sha+':data/coverage.json'))
        day_rows[day] = list(covered_observations(day, coverage))
    result, by_day = run_backtest(day_rows)
    start_d, end_d = date.fromisoformat(start), date.fromisoformat(end)
    result['window_days'] = (end_d-start_d).days+1
    result['missing_days'] = [str(start_d.fromordinal(i))
                              for i in range(start_d.toordinal(),end_d.toordinal()+1)
                              if str(start_d.fromordinal(i)) not in day_rows]
    result['by_day'] = by_day
    result['source_commit_by_day'] = {k:v[:12] for k,v in days.items()}
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--start', required=True)
    parser.add_argument('--end', required=True)
    args=parser.parse_args()
    print(json.dumps(analyze(args.start,args.end),sort_keys=True))


if __name__=='__main__': main()
