from pathlib import Path
import json,csv,re
from registry_ui import build_ui
from public_projection import public_projection
from build_canva_report import build_canva_report
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
canonical=json.loads((ROOT/'private/data/jobs.json').read_text())
build_canva_report(ROOT/'private',canonical)
for view,safe in [('private',False),('public-safe',True)]:
 data=public_projection(canonical) if safe else canonical
 # Only remove stale generated registry pages; retained application packs are untouched.
 ids={j['id'] for j in data['jobs']}
 for page in (ROOT/view/'registry').glob('*.html'):
  if page.stem not in ids:page.unlink()
 build_ui(ROOT/view,data['jobs'],{k:v for k,v in data.items() if k!='jobs'},public_safe=safe)
 write_csv(ROOT/view/'data/jobs.csv',data['jobs'])
 print(json.dumps({'view':view,'records':len(data['jobs']),'mode':'published'}))
