"""Check preservation and summarize a bounded provincial follow-up against a Git ref.

Example: python3 scripts/audit_province_followup.py drenthe --baseline 699d1a4
  --attempts .staging/drenthe/collection.json work/cegid-part.json work/scania-part.json
  --output docs/drenthe-followup-audit.json
"""
import argparse,json,subprocess,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from collector.pipeline import ROOT,read,write,now
from collector.classify import canonical_url


def audit(province,baseline,attempt_files):
    def previous(name):return json.loads(subprocess.check_output(['git','show',baseline+':data/'+name+'.json'],cwd=ROOT))
    old_companies=previous('companies');old_sources=previous('sources');old_jobs=previous('catalog')['jobs']
    companies=read(ROOT/'data/companies.json',[]);sources=read(ROOT/'data/sources.json',[]);jobs=read(ROOT/'data/catalog.json',{})['jobs']
    removed=dict(companies=sorted({x['id'] for x in old_companies}-{x['id'] for x in companies}),
        sources=sorted({x['id'] for x in old_sources}-{x['id'] for x in sources}),
        catalog_urls=sorted({canonical_url(x['url']) for x in old_jobs}-{canonical_url(x['url']) for x in jobs}))
    if any(removed.values()):raise ValueError('Pre-existing records removed: '+str(removed))
    for name,rows in [('companies',companies),('sources',sources),('catalog',jobs)]:
        if len({r['id'] for r in rows})!=len(rows):raise ValueError('Duplicate IDs in '+name)
    if len({canonical_url(j['url']) for j in jobs})!=len(jobs):raise ValueError('Duplicate canonical catalog URLs')
    before={c['id']:c for c in old_companies};preserved_workplaces=0
    for company in companies:
        old=before.get(company['id'],{})
        if not set(old.get('source_ids',[]))<=set(company.get('source_ids',[])):raise ValueError('Existing source attachment removed')
        for key,value in old.items():
            if key.endswith('_research') and key!=province+'_research' and company.get(key)!=value:
                raise ValueError('Other provincial research changed')
        for place in old.get('workplaces',[]):
            if place.get('region_code')!=read(ROOT/'data'/(province+'-geography.json'),{})['province']['nuts2_code']:
                if place not in company.get('workplaces',[]):raise ValueError('Other-region workplace changed')
                preserved_workplaces+=1
    attempts=[]
    for path in attempt_files:
        payload=read(path,{})
        attempts.extend(part['report'] for part in payload.get('parts',[payload]))
    invalid=[r['id'] for r in read(ROOT/'data/coverage.json',{})['sources'] if r.get('status')!='ok' and (r.get('complete') or r.get('closure_complete'))]
    if invalid:raise ValueError('Incomplete source reports marked complete: '+str(invalid))
    report=read(ROOT/'data'/(province+'-coverage.json'),{})
    source_ids={s for e in report['employers'] for s in e['source_ids']}
    return dict(schema_version=1,generated_at=now(),province=province,baseline_commit=subprocess.check_output(['git','rev-parse',baseline],cwd=ROOT,text=True).strip(),
        exhaustive=False,removed=removed,preservation_checks_passed=True,preserved_other_region_workplaces=preserved_workplaces,
        baseline_counts=dict(companies=len(old_companies),sources=len(old_sources),catalog=len(old_jobs)),
        current_counts=dict(companies=len(companies),sources=len(sources),catalog=len(jobs)),
        summary=report['summary'],municipalities=report['municipalities'],
        source_attempts=attempts,attempt_count=len(attempts),distinct_attempted_sources=len({r['id'] for r in attempts}),
        invalid_complete_reports=invalid,language_decisions=[dict(id=j['id'],title=j['title'],city=j['city'],status=j['status'],url=j['url'],
            language_requirements=j['language_requirements'],workplace_languages=j['workplace_languages'],verification=j['verification']) for j in jobs if j['source_id'] in source_ids],
        note='Per-source checked_at retained. A full inventory in one query does not establish complete employer/market coverage. No merge or deployment performed.')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('province');p.add_argument('--baseline',required=True)
    p.add_argument('--attempts',type=Path,nargs='+',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    result=audit(a.province,a.baseline,a.attempts);write(a.output,result)
    print(json.dumps({k:result[k] for k in ('preservation_checks_passed','attempt_count','distinct_attempted_sources','current_counts','summary')},indent=2))
if __name__=='__main__':main()
