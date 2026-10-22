"""Canva decision page derived entirely from canonical job/campaign fields."""
from html import escape as e


def build_canva_report(root, data):
    campaign = data.get('campaigns', {}).get('canva')
    if not campaign:
        return
    rows = []
    for j in data['jobs']:
        if j.get('organization') != 'Canva':
            continue
        def val(key, child=None):
            value = j.get(key)
            if child:
                value = (value or {}).get(child)
            return e(str(value or '未知'))
        locations = '；'.join(x.get('city', '') for x in j.get('locations', []))
        rows.append(f'<tr><th><a href="../registry/{e(j["id"])}.html">{val("title")}</a></th><td>{e(locations)}</td><td>{val("vacancy_status")}</td><td>{val("research_direction_fit","label")}</td><td>{val("level_fit","label")}</td><td>{val("application_action","label")}<br>{val("application_action","reason")}</td></tr>')
    points = ''.join('<li>' + e(p) + '</li>' for p in campaign.get('decision_points', []))
    sources = {s['id']: s for s in data['sources']}
    refs = ''.join(f'<li><a href="{e(sources[sid]["url"])}" target="_blank" rel="noopener noreferrer">{e(sources[sid]["title"])}</a> · {e(str(sources[sid].get("verified_at", "")))}</li>' for sid in campaign.get('source_ids', []) if sid in sources and sources[sid].get('url'))
    page = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Canva 申请决策 · {e(campaign['checked_at'])}</title><link rel="stylesheet" href="../assets/registry.css"></head><body><main class="detail-shell"><nav><a href="../index.html?view=canva">← Canva 职位表</a></nav><h1>Canva：先确认合适岗位，Principal 仅作冲刺</h1><p>{e(campaign['summary_zh'])}</p><p>核查：{e(campaign['checked_at'])} · {e(campaign['scope'])}</p><ul>{points}</ul><div class="table-scroll"><table class="detail-table"><caption>正式职位与团队线索分别计数；来自同一 canonical JSON</caption><thead><tr><th>岗位／详情</th><th>地点</th><th>状态</th><th>研究方向</th><th>职级</th><th>动作及理由</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div><h2>材料与签证</h2><p>{e(campaign['draft_note'])}</p><p>{e(campaign['visa_note'])}</p><h2>核验来源</h2><ul>{refs}</ul><p>关闭岗位不投递；NI 团队线索需先核实是否有适合当前资历且可在目标城市工作的真实 opening。未联系任何机构、未提交申请。</p></main></body></html>'''
    target = root / 'shared/canva_decision_20261022.html'
    target.parent.mkdir(exist_ok=True)
    target.write_text(page, encoding='utf-8')
