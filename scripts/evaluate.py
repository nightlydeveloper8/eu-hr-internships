"""Emit inspectable rule-evaluation results; never claim population accuracy."""
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from collector.classify import classify_role
root=Path(__file__).resolve().parents[1]
rows=json.loads((root/'data/evaluation.json').read_text())
errors=[];tp=tn=fp=fn=0
for row in rows:
    result=classify_role(row['title'],row.get('text',''),row.get('employment',''))
    predicted=bool(result);expected=row['include']
    if predicted and expected:tp+=1
    elif not predicted and not expected:tn+=1
    elif predicted:fp+=1
    else:fn+=1
    if predicted!=expected or row.get('category') and (not result or row['category'] not in result['categories']):errors.append(row['title'])
report={'examples':len(rows),'true_positives':tp,'true_negatives':tn,'false_positives':fp,'false_negatives':fn,'errors':errors,'limitation':'Small manually labelled regression set; these scores are not estimates of accuracy on all European jobs.'}
(root/'docs/evaluation-report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
if errors:raise SystemExit(1)
