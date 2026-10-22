#!/usr/bin/env python3
"""Build a local registry from the supplied canonical rows, without reading private sources.

Call build_ui(output_root, jobs, metadata, public_safe=False) after copying retained
first-round files into output_root. All paths in artifacts are relative to that root.
The caller owns the public-safe field/file allowlist: this module never copies files.
"""
from pathlib import Path
import html
import json
import re
import shutil
from urllib.parse import quote, urlparse

ASSETS = Path(__file__).resolve().parent.parent / 'site-assets'


def esc(value):
    return html.escape(str(value), quote=True)


def external_url(value):
    if not isinstance(value, str):
        return None
    parsed = urlparse(value)
    return value if parsed.scheme in ('https', 'http') and parsed.netloc else None


def local_file(root, value):
    if not isinstance(value, str) or not value or '\\' in value:
        return None
    p = Path(value)
    if p.is_absolute() or '..' in p.parts or urlparse(value).scheme:
        return None
    target = root / p
    if not target.resolve().is_relative_to(root.resolve()):
        return None
    return value if target.is_file() and target.stat().st_size else None


def display(value):
    if value is None or value == '' or value == [] or value == {}:
        return '未知／尚未核实'
    if isinstance(value, bool):
        return '是' if value else '否'
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, indent=2)
    return str(value)


def data_section(title, values):
    rows = ''.join(f'<tr><th scope="row">{esc(label)}</th><td><pre class="value">{esc(display(value))}</pre></td></tr>' for label, value in values)
    return f'<section class="detail-section"><h2>{esc(title)}</h2><table class="detail-table"><caption>{esc(title)}</caption><tbody>{rows}</tbody></table></section>'


def requirement_matrix_section(job, public_safe):
    # Candidate evidence is private; the public builder also uses its own field allowlist.
    matrix = job.get('requirement_evidence_matrix')
    if public_safe or not isinstance(matrix, list) or not matrix:
        return ''
    fields = [('id', '编号'), ('kind', '类别'), ('requirement', '岗位条件'), ('cv_ref', 'CV／项目证据'), ('status', '证据状态'), ('interpretation', '解释与边界'), ('source_ids', '岗位来源 ID')]
    headers = ''.join(f'<th scope="col">{esc(label)}</th>' for _, label in fields)
    rows = []
    for item in matrix:
        if not isinstance(item, dict):
            continue
        cells = ''
        for key, _ in fields:
            opening = '<th scope="row">' if key == 'id' else '<td>'
            closing = '</th>' if key == 'id' else '</td>'
            cells += opening + '<pre class="value">' + esc(display(item.get(key))) + '</pre>' + closing
        rows.append(f'<tr>{cells}</tr>')
    return '<section class="detail-section"><h2>逐项要求 → 候选人证据</h2><p class="muted">岗位要求、候选人证据和解释分开保留；未证明不代表明确不具备。</p><div class="table-scroll"><table class="detail-table requirement-matrix"><caption>要求与候选人证据映射</caption><thead><tr>' + headers + '</tr></thead><tbody>' + ''.join(rows) + '</tbody></table></div></section>'


def detail_page(root, job, metadata, public_safe):
    jid = str(job['id'])
    title = job.get('title') or jid
    org = job.get('organization') or '机构未知'
    official = external_url(job.get('official_url'))
    official_link = f'<a href="{esc(official)}" rel="noopener noreferrer" target="_blank">官方招聘来源 ↗</a>' if official else '<span>官方来源未取得</span>'
    retained = local_file(root, f'jobs/{jid}/index.html') if not public_safe else None
    retained_link = f'<a href="../jobs/{quote(jid)}/index.html">首轮完整报告与申请材料（保留原版）</a>' if retained else ''
    jd = local_file(root, job.get('jd_href')) if not public_safe else None
    jd_label = '完整 JD（核验快照）' if 'full' in str(job.get('jd_completeness') or '').lower() else 'JD／公告原文（核验快照）'
    jd_link = f'<a href="../{esc(quote(jd, safe="/"))}">{esc(jd_label)}</a>' if jd else ''
    source_lookup = {str(s.get('id') or s.get('source_id')): s for s in metadata.get('sources', []) if isinstance(s, dict)}
    source_rows = []
    for sid in job.get('source_ids') or []:
        src = source_lookup.get(str(sid), {})
        url = external_url(src.get('url') or src.get('official_url'))
        anchor = f'<a href="{esc(url)}" rel="noopener noreferrer" target="_blank">{esc(src.get("title") or sid)} ↗</a>' if url else esc(src.get('title') or sid)
        evidence = src.get('excerpt') or src.get('evidence') or src.get('description')
        source_rows.append(f'<tr><th scope="row">{esc(sid)}</th><td>{anchor}</td><td>{esc(display(src.get("verified_at") or src.get("retrieved_at")))}</td><td><pre class="value">{esc(display(evidence))}</pre></td></tr>')
    sources = '<section class="detail-section"><h2>来源与可追溯性</h2><div class="table-scroll"><table class="detail-table"><caption>本记录引用来源；核实日期与文本日期分开保留</caption><thead><tr><th scope="col">来源 ID</th><th scope="col">来源</th><th scope="col">抓取／核实</th><th scope="col">证据短摘／说明</th></tr></thead><tbody>' + ''.join(source_rows) + '</tbody></table></div></section>'
    artifact_items = []
    if not public_safe:
        for a in job.get('artifacts') or []:
            if not isinstance(a, dict):
                continue
            p = local_file(root, a.get('path'))
            ready = a.get('status') not in ('missing', 'not_generated', 'blocked', 'planned', 'pending')
            label = f'{a.get("type") or "文件"} · {a.get("version") or "版本未注明"}'
            if p and ready:
                artifact_items.append(f'<li><a href="../{esc(quote(p, safe="/"))}" download>{esc(label)}</a><small>{esc(a.get("sha256") or "哈希未提供")}</small></li>')
            else:
                artifact_items.append(f'<li>{esc(label)} — 未生成／当前不可下载（{esc(a.get("status") or "unknown")}）</li>')
    artifacts = '' if public_safe else '<section class="detail-section"><h2>申请材料（草稿／用户上传定稿）</h2><p>申请文本均为草稿，未发送或提交。下载仅在文件真实存在时显示。</p><ul class="artifacts">' + (''.join(artifact_items) or '<li>本岗位尚未生成申请材料。</li>') + '</ul></section>'
    sections = [
        data_section('当前判断与评分', [('记录类型', job.get('record_type')), ('招聘状态及原因', {'status': job.get('vacancy_status'), 'reason': job.get('status_reason'), 'checked_at': job.get('status_checked_at'), 'verified_open': job.get('verified_open')}), ('当前建议', job.get('active_recommendation')), ('统一评分', job.get('scores')), ('证据可信度', job.get('source_confidence')), ('核心资格', job.get('hard_gate_status')), ('资历判断', job.get('seniority_assessment')), ('AI 申请政策', job.get('ai_application_policy'))]),
        data_section('职位、合同与截止', [('机构／团队', {'organization': org, 'team': job.get('team'), 'lab': job.get('lab'), 'project': job.get('project')}), ('国家／城市／安排', {'country': job.get('country'), 'city': job.get('city'), 'is_london': job.get('is_london'), 'remote_policy': job.get('remote_policy'), 'attendance_frequency': job.get('attendance_frequency')}), ('薪资', {k: job.get(k) for k in ('salary_original', 'salary_min', 'salary_max', 'salary_currency', 'salary_period', 'salary_gross_or_net', 'salary_estimate')}), ('合同／开始', {k: job.get(k) for k in ('contract_type', 'contract_duration', 'start_date', 'hours')}), ('截止原文与精度', {k: job.get(k) for k in ('deadline_original', 'deadline_date', 'deadline_time', 'deadline_timezone', 'deadline_iso', 'deadline_precision', 'deadline_conflict', 'planning_deadline', 'deadline_evidence')}), ('JD 完整性', job.get('jd_completeness'))]),
        data_section('官方信息与投递渠道', [('信息页面', job.get('information_url') or job.get('official_url')), ('官方投递入口', job.get('application_url')), ('渠道类型', job.get('application_channel')), ('投递说明', job.get('application_instructions')), ('渠道核实日期', job.get('channel_verified_at')), ('渠道检查与限制', {'checked_at':job.get('channel_checked_at'),'status':job.get('channel_verification_status'),'evidence':job.get('channel_evidence')}), ('各申请事件',job.get('application_events')), ('来源冲突',job.get('source_conflicts'))]),
        data_section('AI 申请政策与官方依据', [('当前政策', job.get('ai_application_policy')), ('官方依据／短摘与核实记录', job.get('ai_policy_evidence'))]),
        data_section('职责与要求', [('职责', job.get('responsibilities')), ('必需条件', job.get('essential_requirements')), ('优先条件', job.get('preferred_requirements')), ('后续动作', job.get('next_action'))]),
    ]
    matrix = requirement_matrix_section(job, public_safe)
    if matrix:
        sections.append(matrix)
    if not public_safe:
        sections += [data_section('候选人证据与待问事项（本人授权公开）', [('CV／项目证据', job.get('candidate_evidence_refs')), ('资料或能力缺口', job.get('missing_evidence')), ('伦敦生活场景', job.get('london_life_scenarios')), ('需用户／HR 回答', job.get('questions')), ('具体岗位签证核验', job.get('visa')), ('申请历史引用', job.get('application_history_refs')), ('联系方式（仅草稿研究）', job.get('contacts'))]), data_section('评分版本与迁移', [('首轮筛选证据', job.get('screening_score')), ('已有深度复核', job.get('deep_review_score')), ('旧 ID', job.get('prior_round_ids')), ('去重键', job.get('dedup_key')), ('更新时间', job.get('last_updated'))])]
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>{esc(org)} · {esc(title)} · 职位档案</title><link rel="stylesheet" href="../assets/registry.css"></head><body><a class="skip-link" href="#main">跳到正文</a><main id="main" class="detail-shell"><nav class="detail-nav"><a href="../index.html">← 返回完整职位表</a>{official_link}{jd_link}{retained_link}</nav><p class="eyebrow">{'公开安全示例 · 按允许字段构建' if public_safe else '第二轮公开研究 · 申请材料为草稿'}</p><h1>{esc(title)}</h1><p class="lead">{esc(org)} · {esc(display(job.get('city')))} / {esc(display(job.get('country')))}</p><p class="muted">记录 ID：{esc(jid)} · 核实：{esc(display(job.get('verified_at')))}。未知保留为未知；表格排序与职位资格相互独立。</p>{''.join(sections)}{artifacts}{sources}<footer><a href="../data/jobs.json">当前模式 canonical JSON</a> · 构建基准 {esc(metadata.get('as_of') or '未注明')}。进度只存当前浏览器；网页本身公开。</footer></main></body></html>'''


def build_ui(output_root: Path, jobs: list, metadata: dict, public_safe=False):
    """Write registry UI and exact supplied canonical rows; do not mutate them or copy downloads."""
    output_root = Path(output_root)
    for directory in ('assets', 'data', 'registry'):
        (output_root / directory).mkdir(parents=True, exist_ok=True)
    for job in jobs:
        if not isinstance(job, dict) or not isinstance(job.get('id'), str) or not re.fullmatch(r'[A-Za-z0-9_.-]+', job.get('id', '')):
            raise ValueError('Registry IDs must be nonempty safe filename components')
    if len({j['id'] for j in jobs}) != len(jobs):
        raise ValueError('Duplicate registry IDs')
    payload = {k: v for k, v in metadata.items() if k != 'jobs'}
    payload['jobs'] = jobs
    (output_root / 'data' / 'jobs.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    for name in ('registry.js', 'registry.css'):
        shutil.copyfile(ASSETS / name, output_root / 'assets' / name)
    available = {}
    for job in jobs:
        available[job['id']] = [] if public_safe else [a['path'] for a in (job.get('artifacts') or []) if isinstance(a, dict) and local_file(output_root, a.get('path')) and a.get('status') not in ('missing', 'not_generated', 'blocked', 'planned', 'pending')]
        (output_root / 'registry' / f'{job["id"]}.html').write_text(detail_page(output_root, job, metadata, public_safe), encoding='utf-8')
    (output_root / 'assets' / 'available-artifacts.json').write_text(json.dumps(available, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    progress_script = ''
    if not public_safe and (ASSETS / 'progress.js').is_file():
        shutil.copyfile(ASSETS / 'progress.js', output_root / 'assets' / 'progress.js')
        progress_script = '<script defer src="assets/progress.js"></script>'
    mode = 'public-safe' if public_safe else 'personal-published'
    local_links = '' if public_safe else '<a href="shared/cross_role_comparison.html">首轮跨岗报告（保留）</a>' if (output_root / 'shared/cross_role_comparison.html').is_file() else ''
    if not public_safe: local_links += '<a href="https://github.com/zhanh-he/finding-jobs" target="_blank" rel="noopener noreferrer">GitHub ↗</a><a href="shared/round2_online_guide.html">新版说明</a>'
    page = INDEX.replace('__PROGRESS_SCRIPT__', progress_script).replace('__MODE__', mode).replace('__AS_OF__', esc(metadata.get('as_of') or '未注明')).replace('__LOCAL_LINKS__', local_links).replace('__PRIVACY__', '公开安全构建 · 仅允许字段／文件' if public_safe else '本人授权公开 · 进度仅存此浏览器')
    (output_root / 'index.html').write_text(page, encoding='utf-8')
    return {'rows': len(jobs), 'detail_pages': len(jobs), 'mode': mode, 'output_root': str(output_root)}


INDEX = '''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>音乐与音频 AI · 完整职位总表</title><link rel="stylesheet" href="assets/registry.css"><script defer src="assets/registry.js"></script>__PROGRESS_SCRIPT__</head>
<body data-mode="__MODE__" class="desktop-registry"><a class="skip-link" href="#registry">跳到职位表</a>
<header class="compact-head"><div class="compact-title"><h1>音乐／音频 AI · 职位总表</h1><span class="privacy-chip">__PRIVACY__</span><span class="as-of">资料基准 __AS_OF__</span>__LOCAL_LINKS__</div>
<div class="compact-tools"><label class="search-label" for="search"><span class="sr-only">搜索职位、机构、团队、方向、城市</span><input id="search" type="search" placeholder="搜索职位 / 机构 / 团队 / 城市" autocomplete="off"></label>
<details class="filter-float" id="filter-popover"><summary>筛选／视图 <span aria-hidden="true">⌄</span></summary><section class="filter-panel" aria-label="组合筛选面板"><div id="view-tabs" class="view-tabs" role="group" aria-label="候选池视图"><button data-view="vacancies" aria-pressed="true" type="button">全部职位</button><button data-view="open" aria-pressed="false" type="button">已证实开放</button><button data-view="all" aria-pressed="false" type="button">全部记录</button><button data-view="upcoming" aria-pressed="false" type="button">即将开放</button><button data-view="unknown" aria-pressed="false" type="button">状态未知</button><button data-view="closed" aria-pressed="false" type="button">已关闭</button><button data-view="watch" aria-pressed="false" type="button">团队观察</button><button data-view="history" aria-pressed="false" type="button">历史记录</button></div>
<div class="filters" id="filters"><label>国家<select id="filter-country" aria-label="国家"><option value="">全部国家</option></select></label><label>城市<select id="filter-city" aria-label="城市"><option value="">全部城市</option></select></label><label>岗位类型<select id="filter-type" aria-label="岗位类型"><option value="">全部类型</option></select></label><label>开放状态<select id="filter-status" aria-label="开放状态"><option value="">全部状态</option></select></label><label>当前推荐<select id="filter-grade" aria-label="当前推荐"><option value="">全部推荐</option></select></label><label>申请阶段<select id="filter-stage" aria-label="申请阶段"><option value="">全部阶段</option></select></label><label>具体岗位签证证据<select id="filter-visa" aria-label="具体岗位签证证据"><option value="">全部证据状态</option></select></label><label>深度材料状态<select id="filter-depth" aria-label="深度材料状态"><option value="">全部材料状态</option></select></label><label>截止情况<select id="filter-expiry" aria-label="截止情况"><option value="">全部截止情况</option></select></label></div><button id="clear" class="secondary" type="button">清空筛选，恢复全部职位</button><p class="muted">全部职位排除团队观察与历史公告；已证实开放严格按来源核实。未知值不当作0，牌照不等于本岗担保。</p></section></details>
<label class="sort-label"><span class="sr-only">排序视角</span><select id="sort-view"><option value="" hidden>列排序（见箭头）</option><option value="deadline_then_relevance" selected>截止 → 相关度</option><option value="recommended">建议：等级／资格／证据</option><option value="career:desc">相关度：高到低</option><option value="londonlife:desc">伦敦生活：高到低</option><option value="deadline:asc">截止：近到远</option><option value="org:asc">机构：A–Z</option></select></label>
<details class="columns"><summary>显示列</summary><fieldset id="column-controls"><legend>默认10列；其他原始字段可展开，职位列保留</legend></fieldset></details><div class="export-buttons"><button id="export-filtered" type="button">筛选 CSV</button><button id="export-all" class="secondary" type="button">全部 CSV</button><button id="export-json" class="secondary" type="button">JSON</button></div><div id="local-progress-tools"></div></div>
<div id="pool-counts" class="pool-counts" aria-label="完整候选池分类计数"></div><section id="urgent-deadlines" class="urgent-deadlines" aria-live="polite" aria-label="48小时内紧急截止" hidden></section></header>
<main><section id="registry" class="registry-section" aria-label="完整职位表"><div class="results-line"><p id="results-count" role="status" aria-live="polite">正在读取数据…</p><span class="compact-help" id="scroll-hint">点击列名排序 · 未知排后 · 点击职位看完整证据、原文与材料</span></div><div id="error" class="error" role="alert" hidden></div><div class="table-scroll registry-scroll" tabindex="0" role="region" aria-label="可横向滚动的完整职位表" aria-describedby="scroll-hint"><table id="jobs-table"><caption>每行一条候选职位；相关度为研究／技术／学术／工程已知权重归一化，覆盖率以60为分母。完整字段可显示或打开详情。</caption><thead><tr id="column-headers"></tr></thead><tbody id="jobs-body"></tbody></table></div><div id="empty" class="empty" hidden><h3>没有符合当前条件的记录</h3><p>打开筛选面板切换视图，或清空筛选。</p></div><noscript><p class="error">交互表需要 JavaScript；仍可直接打开 <a href="data/jobs.json">JSON</a> 或交付包中的 CSV。</p></noscript></section><footer><a href="data/jobs.json">canonical JSON</a><span id="clock-note">精确截止按当前时间显示；日期未知时刻不补造午夜。</span><span id="build-note"></span></footer></main></body></html>'''
