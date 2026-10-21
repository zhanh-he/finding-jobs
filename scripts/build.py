"""Build two physically separate static sites. Public mode never reads private/."""
from pathlib import Path
import json,html,re,argparse,os
ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--view',choices=['private','public-safe'],required=True);args=ap.parse_args()
view=args.view;out=ROOT/view;out.mkdir(exist_ok=True)
if view=='public-safe':
 examples=json.loads((out/'example_data.json').read_text())
 allowed={'index.html','example_data.json','assets/style.css'}|{f'jobs/{j["id"]}/index.html' for j in examples}
 unexpected=[str(f.relative_to(out)) for f in out.rglob('*') if f.is_symlink() or (f.is_file() and f.relative_to(out).as_posix() not in allowed)]
 if unexpected:raise SystemExit('Public build stopped: unexpected files require review')
(out/'assets').mkdir(exist_ok=True)
CSS='''*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;overflow-wrap:anywhere;background:#f5f5f1;color:#182b36;font:16px/1.7 -apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC",sans-serif}a{color:#006d71;text-decoration-thickness:1px;text-underline-offset:4px;overflow-wrap:anywhere}a:hover{color:#003f43}button,a{touch-action:manipulation}header{border-bottom:1px solid #d6dedb;background:#fff}nav{max-width:1180px;margin:auto;padding:17px 30px;display:flex;gap:25px;align-items:center;flex-wrap:wrap}nav a{font-size:14px;text-decoration:none}nav .brand{margin-right:auto;font-size:17px;font-weight:750;color:#182b36}main{max-width:1180px;margin:auto;padding:42px 30px 65px}h1{font-size:clamp(30px,4.2vw,52px);line-height:1.2;letter-spacing:-1px;margin:14px 0 24px;font-weight:720}h2{font-size:25px;line-height:1.35;margin:36px 0 16px}h3{font-size:18px;line-height:1.4;margin:12px 0}p{margin:10px 0 18px}.eyebrow{font-size:12px;letter-spacing:2px;color:#006d71;font-weight:700;text-transform:uppercase}.intro{max-width:800px;color:#52616b;font-size:18px}.badge{display:inline-block;font-size:12px;font-weight:700;padding:4px 11px;border-radius:30px;background:#e0efeb;color:#205c50}.badge.warn{background:#f6e6cc;color:#805317}.hero{display:grid;grid-template-columns:1fr 260px;gap:45px;align-items:center;margin-bottom:34px}.hero aside{border-left:3px solid #d59644;padding-left:24px;font-size:14px}.hero aside strong{font-size:22px;display:block}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:20px}.card{background:#fff;border:1px solid #d6dedb;border-radius:12px;padding:25px;min-width:0}.card-top{display:flex;gap:12px;justify-content:space-between;align-items:center}.num{font-size:12px;font-weight:700;color:#73858b;letter-spacing:1.5px}.card h2{font-size:29px;margin:16px 0 5px}.role{font-size:14px;color:#65747a;min-height:44px}.card p{font-size:15px}.stats{display:flex;gap:25px;margin:20px 0 15px;padding-top:17px;border-top:1px solid #e4e9e7}.stat strong{display:block;font-size:23px;line-height:1.2}.stat small{color:#65747a;font-size:12px}.card-link{font-size:14px;font-weight:700}.muted{color:#65747a}.note{font-size:14px;color:#65747a}.table-wrap{overscroll-behavior-x:contain;overflow:auto;max-width:100%;background:#fff;border:1px solid #d6dedb;border-radius:8px}#evidence table{min-width:860px}table{border-collapse:collapse;width:100%;font-size:14px}th,td{padding:13px 15px;border-bottom:1px solid #e0e6e3;text-align:left;vertical-align:top;overflow-wrap:anywhere}th{background:#edf2ef;color:#35515b;font-size:12px}td:first-child{font-weight:600}.two{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:30px}.two>div{min-width:0}.facts{background:#eaf0ec;border-radius:10px;padding:24px}.facts p{font-size:15px;margin:7px 0}.actions{display:flex;flex-wrap:wrap;gap:10px;margin:20px 0}.btn{display:inline-block;background:#006d71;color:#fff;padding:10px 17px;border-radius:6px;text-decoration:none;font-size:14px;font-weight:650}.btn:hover{background:#004e52;color:white}.btn.secondary{background:#fff;color:#006d71;border:1px solid #bacbc6}.tabs{display:flex;gap:22px;padding:15px 0;border-top:1px solid #d6dedb;border-bottom:1px solid #d6dedb;flex-wrap:wrap;font-size:14px}.section{scroll-margin-top:20px;margin-top:34px}ul,ol{padding-left:23px}li{margin:8px 0}details{border-top:1px solid #d6dedb;padding:14px 0}summary{cursor:pointer;font-weight:650}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:14px/1.75 ui-monospace,SFMono-Regular,monospace;background:#fff;border:1px solid #e0e6e3;padding:24px;border-radius:8px}code{background:#e6eeea;padding:2px 4px;font-size:13px}.document{max-width:960px}.document h1{font-size:36px}.document .table-wrap{margin:22px 0}.document table{min-width:650px}.file-list{display:grid;grid-template-columns:1fr 1fr;gap:7px 24px;font-size:14px}.file-list a{display:block;padding:8px 0}footer{max-width:1180px;margin:0 auto;padding:22px 30px;border-top:1px solid #d6dedb;font-size:12px;color:#65747a}.rank{white-space:nowrap}.skip{position:absolute;left:-9999px}.skip:focus{left:15px;top:10px;background:white;padding:10px;z-index:100}a:focus-visible,summary:focus-visible{outline:3px solid #d59644;outline-offset:4px}@media(max-width:720px){nav{padding:14px 20px;gap:15px}main{padding:28px 20px 45px}.hero{grid-template-columns:1fr;gap:17px}.hero aside{margin:0 0 12px}.grid,.two{grid-template-columns:1fr}.card{padding:21px}.card h2{font-size:26px}.role{min-height:0}.file-list{grid-template-columns:1fr}h1{letter-spacing:-.5px}.document h1{font-size:29px}th,td{padding:10px}.stats{gap:22px}pre{padding:17px;font-size:13px}footer{padding:20px}.tabs{gap:17px}.hero .intro{font-size:16px}}@media print{nav,.tabs,.actions,footer{display:none}main{padding:0}body{background:white}.card{break-inside:avoid}a{color:black}.grid,.two{display:block}}'''
(out/'assets/style.css').write_text(CSS)
E=lambda x:html.escape(str(x),quote=True)
def inline(t):
 t=E(t)
 def link(m):
  title,href=m.group(1),html.unescape(m.group(2))
  if href.startswith(('javascript:','data:','file:')):return title
  if href.endswith('.md'):href=href[:-3]+'.html'
  return f'<a href="{E(href)}">{title}</a>'
 t=re.sub(r'\[([^\]]+)\]\(([^\)]+)\)',link,t)
 t=re.sub(r'\*\*(.+?)\*\*',r'<strong>\1</strong>',t)
 t=re.sub(r'`([^`]+)`',r'<code>\1</code>',t)
 return t
def md(txt):
 lines=txt.splitlines();parts=[];i=0
 while i<len(lines):
  line=lines[i].strip()
  if not line:i+=1;continue
  if line.startswith('```'):
   i+=1;block=[]
   while i<len(lines) and not lines[i].strip().startswith('```'):block.append(lines[i]);i+=1
   parts.append('<pre>'+E('\n'.join(block))+'</pre>');i+=1;continue
  if line.startswith('|') and i+1<len(lines) and re.match(r'^\s*\|?\s*:?-{2,}',lines[i+1]):
   table=[]
   while i<len(lines) and lines[i].strip().startswith('|'):
    cells=lines[i].strip().strip('|').split('|')
    if not all(re.fullmatch(r'\s*:?-+:?\s*',c) for c in cells):table.append(cells)
    i+=1
   parts.append('<div class="table-wrap"><table><thead><tr>'+''.join('<th>'+inline(c.strip())+'</th>' for c in table[0])+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+inline(c.strip())+'</td>' for c in row)+'</tr>' for row in table[1:])+'</tbody></table></div>');continue
  h=re.match(r'^(#{1,6})\s+(.+)',line)
  if h:parts.append(f'<h{len(h[1])}>'+inline(h[2])+f'</h{len(h[1])}>');i+=1;continue
  li=re.match(r'^(?:[-*]|\d+[.、])\s+(.+)',line)
  if li:
   typ='ol' if line[0].isdigit() else 'ul';items=[]
   while i<len(lines):
    m=re.match(r'^(?:[-*]|\d+[.、])\s+(.+)',lines[i].strip())
    if not m:break
    items.append('<li>'+inline(m[1])+'</li>');i+=1
   parts.append('<'+typ+'>'+''.join(items)+'</'+typ+'>');continue
  if line in ['---','***']:i+=1;continue
  para=[line];i+=1
  while i<len(lines) and lines[i].strip() and not re.match(r'^(#|\||[-*] |\d+\. |```)',lines[i].strip()):para.append(lines[i].strip());i+=1
  parts.append('<p>'+inline(' '.join(para))+'</p>')
 return '\n'.join(parts)
def page(title,content,depth=0,doc=False):
 rel='../'*depth
 links=f'<a href="{rel}index.html" class="brand">音频 AI · 求职复核</a>'
 if view=='private':links+=f'<a href="{rel}shared/cross_role_comparison.html">跨岗结论</a><a href="{rel}shared/visa_routes_official_evidence.html">签证证据</a><a href="{rel}shared/all_questions.html">待确认问题</a>'
 else:links+='<span class="badge">匿名示例</span>'
 label='公开发布材料 · 申请草稿未提交 · 核查截至2026-10-21 · private目录不提供访问保护' if view=='private' else '虚构示例数据 · 不代表任何候选人'
 return f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><meta name="referrer" content="no-referrer"><title>{E(title)} · 音频 AI 求职复核</title><link rel="stylesheet" href="{rel}assets/style.css"></head><body><a class="skip" href="#main">跳到正文</a><header><nav aria-label="主导航">{links}</nav></header><main id="main" class="{ "document" if doc else "" }">{content}</main><footer>{label} · 相对路径静态站点 · 无追踪脚本或外部字体</footer></body></html>'
def dimval(v):return v.get('score') if isinstance(v,dict) else v
def lis(items):return '<ul>'+''.join('<li>'+E(x)+'</li>' for x in items)+'</ul>'
if view=='private':
 order=['cambridge_GT51091','spotify_generative_audio','elevenlabs_research_engineer','apple_speech']
 jobs=[]
 for role_id in order:
  f=out/'jobs'/role_id/'summary.json'
  if f.exists():jobs.append(json.loads(f.read_text()))
 for src in list((out/'jobs').rglob('*.md'))+list((out/'shared').glob('*.md')):
  # Every rendered report stays alongside its private source.
  rel=src.relative_to(out);depth=len(rel.parts)-1
  src.with_suffix('.html').write_text(page(src.stem,md(src.read_text()),depth,True))
else:
 jobs=json.loads((out/'example_data.json').read_text())
weights={'research':20,'technical':20,'academic':10,'engineering':10,'location':25,'salary_development':10,'interview':5}
names={'research':'研究','technical':'技术','academic':'学术','engineering':'工程','location':'地点生活','location_lifestyle':'地点生活','salary_development':'薪资发展','interview':'面试竞争力','interview_competitiveness':'面试竞争力'}
for n,j in enumerate(jobs,1):
 folder=out/'jobs'/j['id'];folder.mkdir(parents=True,exist_ok=True)
 score=j['score'];cov=j['coverage_percent'];sc='待批准' if score is None else f'{score:.1f}'
 grade=j['grade'];badge=f'<span class="badge {"warn" if str(grade).startswith("C") else ""}">{E(grade)}</span>'
 downloads=[]
 if view=='private':
  for pat,label in [('03*.pdf','Resume PDF'),('03*.docx','Resume DOCX'),('03*.txt','Resume TXT'),('05*.txt','Cover Letter TXT'),('02*.csv','证据矩阵 CSV')]:
   files=sorted(folder.glob(pat))
   if files:downloads.append(f'<a class="btn {"secondary" if not label.endswith("PDF") else ""}" href="{E(files[0].name)}" download>{E(label)}</a>')
   else:downloads.append(f'<span class="note">{E(label)} 待生成</span>')
  allfiles=[f for f in sorted(folder.iterdir()) if f.is_file() and f.suffix in ['.md','.txt','.pdf','.docx','.csv']]
  filelist='<div class="file-list">'+''.join(f'<a href="{E(f.with_suffix(".html").name if f.suffix==".md" else f.name)}">{E(f.stem)}</a>' for f in allfiles)+'</div>'
  res=next(iter(folder.glob('03*.txt')),None);cl=folder/'05_cover_letter_draft.txt'
  preview=(f'<details><summary>完整英文 Resume 预览</summary><pre>{E(res.read_text())}</pre></details>' if res else '')+(f'<details><summary>英文 Cover Letter 预览</summary><pre>{E(cl.read_text())}</pre></details>' if cl.exists() else '')
  matrix=folder/'02_requirement_evidence_matrix.md'
  evidence=md(matrix.read_text()) if matrix.exists() else '<p>待生成</p>'
  visa_file=folder/'11_visa_route_analysis.md';visa=md(visa_file.read_text()) if visa_file.exists() else '<p>'+E(j.get('visa','待核实'))+'</p>'
 else:
  filelist='<p>示例不包含真实申请材料。此区域不提供真实申请材料下载。</p>';preview='';evidence='<p>以下仅演示证据分级结构：直接证据、可迁移证据、资料缺口。没有真实候选人信息。</p>';visa='<p>示例未包含个人身份资料。</p>'
 rows=''.join('<tr><td>'+E(names.get(k,k))+'</td><td>'+('未知' if dimval(v) is None else E(dimval(v)))+'</td></tr>' for k,v in j.get('score_dimensions',{}).items())
 body=f'<div class="eyebrow">岗位 {n:02d} / 04 · {"核查 2026.10.21" if view=="private" else "匿名示例"}</div><h1>{E(j["institution"])}</h1><p class="intro">{E(j["title"])}</p>{badge}<p class="intro">{E(j["summary_zh"])}</p><div class="actions">'+''.join(downloads)+'</div><nav class="tabs" aria-label="本页章节"><a href="#decision">结论</a><a href="#evidence">证据</a><a href="#terms">合同与条件</a><a href="#visa">签证</a><a href="#files">材料</a></nav>'
 body+=f'<section id="decision" class="section"><h2>判断与行动</h2><div class="two"><div><div class="stats"><div class="stat"><strong>{sc}</strong><small>已知维度暂定分</small></div><div class="stat"><strong>{cov if cov is not None else "—"}%</strong><small>评分覆盖</small></div></div><p>{E(j["decision"])}</p><p class="note">未知不计作 0，也不填中点。分数不是面试概率，硬资格与用工条件另行判断。</p><div class="table-wrap"><table><thead><tr><th>维度</th><th>适配分</th></tr></thead><tbody>{rows}</tbody></table></div></div><div><h3>主要证据</h3>{lis(j["strengths"])}<h3>尚待解决</h3>{lis(j["gaps"])}</div></div><h3>下一步</h3>{lis(j["actions"])}</section>'
 body+=f'<section id="evidence" class="section"><h2>要求与证据</h2><p class="note">手机可在表格内部横向滚动，查看完整证据与缺口。</p><details><summary>展开完整逐项证据矩阵</summary>{evidence}</details></section><section id="terms" class="section"><h2>合同与工作条件</h2><div class="facts"><p><strong>薪资</strong> {E(j["salary"])}</p><p><strong>合同 / 地点</strong> {E(j["contract"])}</p><p><strong>来源状态</strong> {E(j["source_status"])}</p></div></section><section id="visa" class="section"><h2>英国工作路线</h2><p>{E(j.get("visa","匿名示例没有个人路线判断。"))}</p><details><summary>查看逐岗资格、证据、费用与 ILR 核验</summary>{visa}</details></section><section id="files" class="section"><h2>已生成材料</h2>{preview}{filelist}</section>'
 if j.get('url'):body+='<p class="note"><a href="'+E(j['url'])+'">官方招聘来源</a> · 只读核验，不从本地页提交申请。</p>'
 (folder/'index.html').write_text(page(j['institution'],body,2))
hero='<div class="hero"><div><div class="eyebrow">Research review / 2026.10.21</div><h1>音乐与音频 AI<br>求职第二阶段复核</h1><p class="intro">四份独立判断、逐项证据和定制材料。先看申请关卡，再看分数；所有未知均保留。</p></div><aside><span class="badge">'+('公开材料' if view=='private' else '匿名示例')+'</span><strong>'+('Cambridge 今日截止' if view=='private' else '展示结构与阅读体验')+'</strong><p>'+('21 Oct 2026 午夜 BST<br>22 Oct 07:00 Perth<br>建议留足提交余量，当前未提交。' if view=='private' else '所有机构、评分与经历均为虚构。此区域仅作界面示例。')+'</p></aside></div>'
if view=='private':hero+='<p class="note">行动顺序：Cambridge → Spotify → ElevenLabs → Apple。此顺序考虑截止与岗位任务，不按不完整分数机械排序。当前无确定 A。</p>'
cards=[]
for n,j in enumerate(jobs,1):
 sc='待批准' if j['score'] is None else f'{j["score"]:.1f}';cov='—' if j['coverage_percent'] is None else str(j['coverage_percent'])
 cards.append(f'<article class="card"><div class="card-top"><span class="num">{n:02d} / REVIEW</span><span class="badge {"warn" if str(j["grade"]).startswith("C") else ""}">{E(j["grade"])}</span></div><h2>{E(j["institution"])}</h2><div class="role">{E(j["title"])}</div><p>{E(j["summary_zh"])}</p><div class="stats"><div class="stat"><strong>{sc}</strong><small>暂定适配分</small></div><div class="stat"><strong>{cov}%</strong><small>权重覆盖</small></div></div><a class="card-link" href="jobs/{E(j["id"])}/index.html">查看判断与材料 →</a></article>')
body=hero+'<div class="grid">'+''.join(cards)+'</div><section class="section"><h2>如何阅读这份复核</h2><div class="two"><div><h3>证据决定表述</h3><p>直接项目证据、可迁移能力和资料缺口分别标注。未证明不等于不会；计划不写成完成成果。</p></div><div><h3>材料就绪与申请就绪分别判断</h3><p>页面提供真实生成文件。最终事实、雇主条件与用户核稿完成后，才决定下一步。</p></div></div></section>'
(out/'index.html').write_text(page('四岗对比',body))
print(json.dumps({'view':view,'job_pages':len(jobs),'html_files':len(list(out.rglob('*.html')))},ensure_ascii=False))
