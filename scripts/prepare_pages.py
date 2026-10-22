"""Prepare only website files for Pages and verify all internal links."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import shutil,json,re,hashlib
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'_site'
if OUT.exists():shutil.rmtree(OUT)
OUT.mkdir()
for name in ['private','public-safe']:
 source=ROOT/name
 if any(p.is_symlink() for p in source.rglob('*')):raise SystemExit('Symlink in site content; review required')
 shutil.copytree(source,OUT/name)
for name in ['index.html','.nojekyll']:shutil.copy2(ROOT/name,OUT/name)
class Parser(HTMLParser):
 def __init__(self):super().__init__();self.urls=[];self.ids=set()
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id' in a:self.ids.add(a['id'])
  if tag in ['a','link','script','img']:
   self.urls.extend(a[k] for k in ['href','src'] if k in a)
if (OUT/'private/source_library').exists():raise SystemExit('Raw local source library must not be published')
failures=[];links=0
for file in OUT.rglob('*.html'):
 p=Parser();p.feed(file.read_text())
 for url in p.urls:
  u=urlsplit(url)
  if u.scheme or u.netloc:continue
  if not u.path and not u.fragment:continue
  links+=1
  target=(file.parent/unquote(u.path)).resolve() if u.path else file.resolve()
  if u.path.startswith('/') or not target.is_relative_to(OUT.resolve()) or not target.is_file():failures.append((str(file.relative_to(OUT)),url));continue
  if u.fragment and target.suffix=='.html':
   tp=Parser();tp.feed(target.read_text())
   if unquote(u.fragment) not in tp.ids:failures.append((str(file.relative_to(OUT)),url))
secrets=[]
for f in OUT.rglob('*'):
 if not f.is_file():continue
 if f.suffix in ['.html','.md','.txt','.json','.css','.js']:
  t=f.read_text(errors='replace')
  if re.search(r'(?:gh[pousr]_[A-Za-z0-9]{25,}|sk-[A-Za-z0-9]{25,}|BEGIN (?:RSA |OPENSSH )?PRIVATE KEY)',t):secrets.append(str(f.relative_to(OUT)))
  if re.search(r'[/]Users/|file:///|/workspace/shared/|mail\.google\.com/mail/',t):secrets.append(str(f.relative_to(OUT)))
  if f.name in ['email_audit.json','email_audit.md'] or 'announcement_PRIVATE' in f.name:secrets.append(str(f.relative_to(OUT)))
if failures or secrets:
 print(json.dumps({'missing_or_unsafe_links':failures,'secret_or_local_path_files':secrets},ensure_ascii=False));raise SystemExit(1)
print(json.dumps({'pages':len(list(OUT.rglob('*.html'))),'relative_links_verified':links,'files':len([f for f in OUT.rglob('*') if f.is_file()]),'status':'passed'}))
