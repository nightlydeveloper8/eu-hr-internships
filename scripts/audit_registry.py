"""Read-only HTTP validation of discovery candidates. Never enables a scraper."""
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from collector.adapters import Client
from collector.pipeline import now
root=Path(__file__).resolve().parents[1]
client=Client();cache={};rows=[]
for source in json.loads((root/'data/sources.json').read_text()):
    if source.get('status')!='discovery-only':continue
    url=source['career_url']
    if url not in cache:
        try:
            _,status,final=client.request(url,method='HEAD')
            cache[url]={'http_status':status,'final_url':final,'status':'reachable','checked_at':now()}
        except Exception as exc:cache[url]={'status':'unverified','reason':str(exc)[:200],'checked_at':now()}
    row=dict(id=source['id'],employer=source['employer'],countries=source['target_countries'],url=url,**cache[url]);rows.append(row)
    print(source['id'],row['status'],row.get('reason',''))
(root/'docs/source-discovery-audit.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
