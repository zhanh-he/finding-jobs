from pathlib import Path
import json,csv,re
from registry_ui import build_ui
ROOT=Path(__file__).resolve().parents[1]
def write_csv(p,rows):
 fields=list(dict.fromkeys(k for row in rows for k in row))
 def value(v):
  if v is None:return ''
  if isinstance(v,(dict,list)):v=json.dumps(v,ensure_ascii=False)
  if isinstance(v,str) and re.match(r'^\s*[=+@-]',v):return "'"+v
  return v
 with p.open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,lineterminator="\n");w.writeheader();w.writerows({k:value(v) for k,v in r.items()} for r in rows)
for view,safe in [('private',False),('public-safe',True)]:
 data=json.loads((ROOT/view/'data/jobs.json').read_text())
 build_ui(ROOT/view,data['jobs'],{k:v for k,v in data.items() if k!='jobs'},public_safe=safe)
 write_csv(ROOT/view/'data/jobs.csv',data['jobs'])
 print(json.dumps({'view':view,'records':len(data['jobs']),'mode':'published'}))
