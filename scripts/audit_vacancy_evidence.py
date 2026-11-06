"""Bounded comparison on existing sources; never publishes catalog or full job text.

python3 scripts/audit_vacancy_evidence.py --sources lever-emma-sleep auto-fotofabriek --output /tmp/evidence.json
"""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from collector.adapters import collect,enrich
from collector.classify import classify_role,workplace_languages,language_summary
from collector.pipeline import ROOT,read,write,process_source,now
from collector.runtime import BudgetClient
from unittest.mock import patch


def baseline_classifier(revision):
    code=subprocess.check_output(['git','show',revision+':collector/classify.py'],cwd=ROOT,text=True)
    module=type(sys)('baseline_classifier');exec(compile(code,'baseline/classify.py','exec'),module.__dict__)
    return module


def audit_source(source,baseline,limit,seconds):
    client=BudgetClient(seconds=seconds,max_requests=60,delay=.5);stamp=now()
    report=dict(source_id=source['id'],checked_at=stamp,scope='Existing source; bounded sample, not coverage or population accuracy')
    try:
        rows=collect(source,client)
        known={j['url'] for j in read(ROOT/'data/catalog.json',{}).get('jobs',[]) if j['source_id']==source['id']}
        candidates=[r for r in rows if r['url'] in known or classify_role(r.get('title',''),r.get('text',''),r.get('employment','')) or baseline.classify_role(r.get('title',''),r.get('text',''),r.get('employment',''))]
        # Read all candidate titles until a small sample of pertinent roles is reached.
        sample=[];errors=[]
        for r in candidates:
            try:
                r=enrich(r,source,client)
                if classify_role(r['title'],r.get('text',''),r.get('employment','')) or baseline.classify_role(r['title'],r.get('text',''),r.get('employment','')):sample.append(r)
            except Exception as exc:errors.append(dict(url=r['url'],error=str(exc)[:180]))
            if len(sample)>=limit:break
        comparisons=[]
        # Reuse the current inventory, without issuing a second discovery run.
        with patch('collector.pipeline.collect',return_value=sample),patch('collector.pipeline.enrich',side_effect=lambda r,*a:r):
            part=process_source(source,client,stamp)
        checked={j['external_id']:j for j in part['jobs']}
        for r in sample:
            old=baseline.classify_role(r['title'],r.get('text',''),r.get('employment',''));new=classify_role(r['title'],r.get('text',''),r.get('employment',''))
            j=checked.get(r['external_id'],{})
            try:
                _,_,final=client.request(r['url'],method='HEAD');head_ok=final==r['url']
            except Exception:head_ok=False
            comparisons.append(dict(title=r['title'],url=r['url'],before_role=old,after_role=new,before_head_available=head_ok,
                after_verification=j.get('verification'),before_languages=baseline.workplace_languages(r.get('text','')),
                after_languages=workplace_languages(r.get('text','')),language_requirements=language_summary(r.get('text',''))))
        part['report']['scope']='Bounded sample, not a complete source health report'
        if errors:part['report'].update(status='partial',complete=False,closure_complete=False)
        report.update(inventory_records=len(rows),sample=comparisons,errors=errors,source_report=part['report'])
    except Exception as exc:report.update(error=str(exc)[:300])
    report.update(requests=client.requests,finished_at=now());return report


def offline_comparison(baseline):
    from collector import classify as current
    roles=read(ROOT/'data/evaluation.json',[]);languages=read(ROOT/'data/language-evaluation.json',[])
    result={}
    for label,module in [('before',baseline),('after',current)]:
        role_errors=[];language_errors=[]
        for row in roles:
            prediction=module.classify_role(row['title'],row.get('text',''),row.get('employment',''))
            if bool(prediction)!=row['include'] or (prediction and row.get('category') and row['category'] not in prediction['categories']):role_errors.append(row['title'])
        for row in languages:
            evidence=module.workplace_languages(row['text'])
            if label=='before':
                required=sorted({l['code'] for l in evidence if l['requirement']!='preferred'})
                english=any(l['code']=='en' for l in evidence);alone=False
            else:
                summary=module.language_summary(row['text'],evidence)
                required=summary['required_languages'];english=summary['english_support']=='documented';alone=summary['english_sufficiency']=='documented'
            if required!=row['required'] or english!=row['english_supported'] or alone!=row['english_alone']:language_errors.append(row['text'])
        result[label]=dict(role_cases=len(roles),role_errors=role_errors,language_cases=len(languages),language_errors=language_errors)
    result['limitation']='Small labelled regression sets; not population accuracy. Before-language measurement reflects the old English filter and conflated required/working field.'
    return result


def main():
    p=argparse.ArgumentParser();p.add_argument('--sources',nargs='+',default=[]);p.add_argument('--baseline',default='1579e4f');p.add_argument('--limit',type=int,default=2);p.add_argument('--seconds',type=int,default=90);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    sources={s['id']:s for s in read(ROOT/'data/sources.json',[])};baseline=baseline_classifier(a.baseline)
    reports=[]
    with ThreadPoolExecutor(max_workers=3) as pool:
        reports=list(pool.map(lambda sid:audit_source(sources[sid],baseline,a.limit,a.seconds),a.sources))
    rows=[r for s in reports for r in s.get('sample',[])]
    result=dict(baseline=a.baseline,generated_at=now(),scope='Existing employers only; no catalog publication; observations at stated timestamps',
        offline=offline_comparison(baseline),summary=dict(sources=len(reports),sample=len(rows),before_head_available=sum(r['before_head_available'] for r in rows),after_states=dict(Counter((r.get('after_verification') or {}).get('state','not-classified') for r in rows)),errors=sum(bool(s.get('error'))+len(s.get('errors',[])) for s in reports)),sources=reports)
    write(a.output,result);print(json.dumps(result['summary'],ensure_ascii=False))
if __name__=='__main__':main()
