"""Verify local outputs without printing personal contents or filenames."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import json,re,hashlib
ROOT=Path(__file__).resolve().parents[1]
class Parser(HTMLParser):
 def __init__(self):super().__init__();self.links=[];self.ids=set()
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id' in a:self.ids.add(a['id'])
  if tag in ['a','link','img','script']:
   for k in ['href','src']:
    if k in a:self.links.append((tag,a[k]))
def links_for(view):
 root=ROOT/view;bad=[];count=0
 for page in root.rglob('*.html'):
  p=Parser();p.feed(page.read_text())
  for tag,ref in p.links:
   u=urlsplit(ref)
   if u.scheme or u.netloc:continue
   if not u.path and not u.fragment:continue
   count+=1
   if u.path.startswith('/'):bad.append({'page':str(page.relative_to(ROOT)),'kind':'absolute local URL'});continue
   dest=(page.parent/unquote(u.path)).resolve() if u.path else page.resolve()
   if not dest.is_relative_to(root.resolve()) or not dest.is_file():bad.append({'page':str(page.relative_to(ROOT)),'target':ref,'kind':'missing or outside view'});continue
   if u.fragment and dest.suffix=='.html':
    dp=Parser();dp.feed(dest.read_text())
    if unquote(u.fragment) not in dp.ids:bad.append({'page':str(page.relative_to(ROOT)),'target':ref,'kind':'missing anchor'})
 return {'html_pages':len(list(root.rglob('*.html'))),'relative_links':count,'failures':bad}
result={'private_links':links_for('private'),'public_links':links_for('public-safe')}
public=ROOT/'public-safe';examples=json.loads((public/'example_data.json').read_text());allowed={'index.html','example_data.json','assets/style.css'}|{f'jobs/{j["id"]}/index.html' for j in examples}
result['public_unexpected_files']=[str(f.relative_to(public)) for f in public.rglob('*') if f.is_symlink() or (f.is_file() and f.relative_to(public).as_posix() not in allowed)]
identities=set();contacts=set();repo_urls=set()
for txt in (ROOT/'private/jobs').glob('*/03*.txt'):
 t=txt.read_text();identities.add(re.sub(r'\W','',t.splitlines()[0].lower()))
 contacts.update(re.findall(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}',t))
 repo_urls.update(re.findall(r'(?:github\.com|linkedin\.com/in)/[A-Za-z0-9_-]+',t))
findings=[]
for f in list(public.rglob('*'))+list((ROOT/'scripts').rglob('*'))+[ROOT/'README.md']:
 if not f.is_file():continue
 t=f.read_text(errors='replace');normalized=re.sub(r'\W','',t.lower())
 checks=[]
 if any(x and x in normalized for x in identities):checks.append('candidate identity')
 if any(x.lower() in t.lower() for x in contacts|repo_urls):checks.append('candidate contact/profile')
 if re.search(r'[/]Users/|(?:sk|ghp|gho)_[A-Za-z0-9]{15,}|BEGIN (?:RSA |OPENSSH )?PRIVATE KEY',t):checks.append('local path or credential marker')
 if re.search(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}',t):checks.append('email address')
 if checks:findings.append({'file':str(f.relative_to(ROOT)),'kinds':checks})
result['public_source_privacy_findings']=findings
w={'research':20,'technical':20,'academic':10,'engineering':10,'location':25,'location_lifestyle':25,'salary_development':10,'interview':5,'interview_competitiveness':5}
result['score_checks']=[]
for f in (ROOT/'private/jobs').glob('*/summary.json'):
 j=json.loads(f.read_text());den=0;num=0
 for k,v in j['score_dimensions'].items():
  v=v.get('score') if isinstance(v,dict) else v
  if v is not None:den+=w[k];num+=v*w[k]
 result['score_checks'].append({'role':j['id'],'computed_score':num/den,'reported_score':j['score'],'coverage':den,'pass':abs(num/den-j['score'])<.06 and den==j['coverage_percent']})
passed=not(result['private_links']['failures'] or result['public_links']['failures'] or result['public_unexpected_files'] or findings) and all(x['pass'] for x in result['score_checks'])
result['pass']=passed
report=ROOT/'private/shared/local_verification.json';report.write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps({'pass':passed,'private_pages':result['private_links']['html_pages'],'public_pages':result['public_links']['html_pages'],'link_failures':len(result['private_links']['failures'])+len(result['public_links']['failures']),'privacy_findings':len(findings)},ensure_ascii=False))
raise SystemExit(0 if passed else 1)
