"""Read-only comparison of two committed daily snapshots; never contacts employers."""
import argparse
from collections import Counter
import json
from pathlib import Path
import subprocess
import sys
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from collector.verification import verified_job

ROOT = Path(__file__).resolve().parents[1]
FOCUS = ['auto-daf-trucks', 'auto-becton-dickinson', 'auto-belsimpel-gomibo-group',
         'auto-tilburg-university', 'auto-randstad-italia-spa', 'auto-bmw-group']


def read_ref(ref, path):
    return json.loads(subprocess.check_output(['git', 'show', ref+':'+path], cwd=ROOT))


def snapshot(ref):
    catalog = read_ref(ref, 'data/catalog.json')
    reports = {s['id']:s for s in read_ref(ref, 'data/coverage.json')['sources']}
    sources = {s['id']:s for s in read_ref(ref, 'data/sources.json')}
    rows = []
    for sid in FOCUS:
        source = sources[sid]
        report = reports[sid]
        jobs = [j for j in catalog['jobs'] if j['source_id']==sid]
        checked = report['checked_at']
        # A retained reason is historical if this run did not produce that observation.
        prior = [j for j in jobs if (j.get('verification',{}).get('checked_at') or '') < checked]
        outside = [j for j in jobs if urlsplit(j['url']).hostname not in source['allowed_hosts']]
        rows.append(dict(source_id=sid, catalog_records=len(jobs),
                         verification_observations_before_latest_source_run=len(prior),
                         retained_reason_counts=dict(Counter(j.get('verification',{}).get('reason') for j in prior)),
                         retained_observation_dates=dict(Counter((j.get('verification',{}).get('checked_at') or '')[:10] for j in prior)),
                         outside_declared_host_count=len(outside),
                         outside_declared_hosts=dict(Counter(urlsplit(j['url']).hostname for j in outside)),
                         latest_source_report={k:report.get(k) for k in (
                             'checked_at','status','matching','collected','pages_read','pending_urls',
                             'requests','bytes_read','duration_seconds','allowed_hosts','page_failures')},
                         latest_page_errors=report.get('page_errors',[])[:3]))
    verified = [j for j in catalog['jobs'] if j.get('internship_type')=='internship'
                and verified_job(j, catalog['updated_at'])]
    return dict(ref=ref, updated_at=catalog['updated_at'], total=len(catalog['jobs']),
                states=dict(Counter(j['status'] for j in catalog['jobs'])),
                fresh_verified_internships=len(verified),
                verified_by_country=dict(Counter(j['country'] for j in verified)), sources=rows), catalog


def audit(before, after):
    previous, old = snapshot(before)
    current, new = snapshot(after)
    old_ids = {j['id'] for j in old['jobs']}
    new_ids = {j['id'] for j in new['jobs']}
    return dict(before=previous, after=current,
                delta_verified=current['fresh_verified_internships']-previous['fresh_verified_internships'],
                new_catalog_ids=sorted(new_ids-old_ids), removed_catalog_ids=sorted(old_ids-new_ids),
                limitations=['Snapshots are historical collection evidence, not new live checks.',
                             'Outside declared hosts requires ownership review, not automatic reassignment.',
                             'Retained reasons do not describe the latest source run.',
                             'Zero newly collected records does not establish absence or closure.'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--before', required=True)
    parser.add_argument('--after', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.before, args.after)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('delta_verified','new_catalog_ids','removed_catalog_ids')}))
