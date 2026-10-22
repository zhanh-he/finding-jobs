'use strict';
(() => {
  const $ = id => document.getElementById(id);
  const state = {payload: null, jobs: [], view: 'vacancies', filters: {}, search: '', sort: {key: 'deadline_then_relevance', direction: 'asc'}, hidden: new Set(), available: {}, overrides: Object.create(null)};
  const STATUS = {open:'开放', upcoming:'即将开放', closed:'已关闭', unknown:'状态未知'};
  const TYPE = {academic:'学术／研究',industry:'工业岗位',vacancy:'职位',watch:'团队观察',history:'历史记录'};
  const STAGE = {not_applied_unconfirmed:'未投递·待确认',not_applied:'未投递（本人确认）',preparing:'准备中',applied:'已投递',acknowledged:'已收到回执',screening:'筛选中',assessment:'测评中',interview:'面试中',technical_interview:'技术面试',final_interview:'最终面试',offer:'Offer',rejected:'拒绝',withdrawn:'已撤回',on_hold:'暂缓',contacted:'已联系',unknown:'未知'};
  const CONF = {high:'高',medium:'中',low:'低'};
  const VISA = {confirmed:'已证实具体岗位支持',pending:'具体岗位待证',not_applicable:'不适用',unknown:'未知'};
  const columns = [
    {key:'progress',label:'投递进度',default:true}, {key:'deadline',label:'截止',default:true},
    {key:'career',label:'相关度',default:true}, {key:'title',label:'职位／机构／团队',default:true},
    {key:'place',label:'地点',default:true}, {key:'terms',label:'薪资／合同',default:true},
    {key:'gates',label:'门槛／签证',default:true}, {key:'channels',label:'官方信息／投递',default:true},
    {key:'artifacts',label:'材料',default:true}, {key:'action',label:'行动／备注',default:true},
    {key:'priority',label:'当前等级'}, {key:'overall',label:'综合分＋覆盖'}, {key:'org',label:'机构'},
    {key:'team',label:'团队'}, {key:'london',label:'伦敦'}, {key:'salary',label:'薪资原文'},
    {key:'contract',label:'合同原文'}, {key:'direction',label:'方向'}, {key:'channel',label:'渠道'},
    {key:'status',label:'招聘状态'}, {key:'stage',label:'投递阶段（本地）'}, {key:'londonlife',label:'伦敦生活'},
    {key:'source',label:'官方信息源'}, {key:'verified',label:'核实日期'}, {key:'confidence',label:'证据可信度'}
  ];
  state.hidden = new Set(columns.filter(c=>!c.default).map(c=>c.key));
  const filters = [
    ['country','country',null],['city','city',null],['type','job_type',TYPE],['status','vacancy_status',STATUS],
    ['grade','grade',null],['stage','application_stage',STAGE],['visa','visa_filter_status',VISA],['depth','deep_review_status',null],['expiry','expiry_status',{expired:'已过期',not_expired:'未截止',unknown:'截止未知'}]
  ];
  function text(v) {
    if (v === null || v === undefined || v === '') return '未知';
    if (Array.isArray(v)) return v.map(text).join('；');
    if (typeof v === 'object') return v.label || v.name || v.title || v.reason || v.status || JSON.stringify(v);
    return String(v);
  }
  function scalar(v) { return v === undefined || v === null || v === '' ? null : (typeof v === 'object' ? text(v) : v); }
  function number(v) { return typeof v === 'number' && Number.isFinite(v) ? v : null; }
  function score(j, k) { return number(j.scores?.[k] ?? j[k]); }
  function grade(j) { return j.active_recommendation?.grade ?? j.recommendation ?? null; }
  function confidence(j) { return typeof j.source_confidence === 'object' ? j.source_confidence?.level : j.source_confidence; }
  function verifiedOpen(j) { return j.record_type === 'vacancy' && j.vacancy_status === 'open' && j.verified_open === true; }
  function effectiveStage(j) {
    let stage=state.overrides[j.id]?.stage ?? j.application_stage ?? 'unknown';
    if(stage==='draft')stage='preparing';
    if(stage==='not_found_in_audit')stage='not_applied_unconfirmed';
    return stage;
  }
  function filterValue(j, key) {
    if (key === 'expiry_status') return expiryStatus(j).status;
    if (key === 'application_stage') return effectiveStage(j);
    if (key === 'grade') return scalar(grade(j));
    if (key === 'job_type') return scalar(j.job_type || (j.record_type !== 'vacancy' ? j.record_type : null));
    if (key === 'visa_filter_status') return scalar(j.visa_filter_status) || 'unknown';
    return scalar(j[key]);
  }
  function listStrings(v) { return Array.isArray(v) ? v.map(text) : (v ? [text(v)] : []); }
  function datePart(v) { return typeof v === 'object' && v ? v.date || v.deadline_date || null : scalar(v); }
  function deadlineKey(j) {
    const value = datePart(j.planning_deadline) || j.deadline_iso || j.deadline_date;
    if (!value || !/^\d{4}-\d{2}-\d{2}/.test(String(value))) return null;
    return String(value).substring(0, 10);
  }
  function sortValue(j,key) {
    const mapping = {
      priority: () => grade(j), overall: () => score(j,'provisional_overall'), career: () => score(j,'career_fit_score'),
      title: () => j.title, org: () => j.organization, team: () => j.team || j.lab || j.project,
      place: () => [j.country,j.city].filter(Boolean).join(' / ') || null, london: () => j.is_london === null || j.is_london === undefined ? null : Number(j.is_london),
      salary: () => number(j.salary_min)===null ? null : `${j.salary_currency || 'unknown'}/${j.salary_period || 'unknown'}/${j.salary_min}`, contract: () => j.contract_type, direction: () => listStrings(j.direction).join(';') || null,
      channel: () => j.recruitment_channel, status: () => j.vacancy_status, stage: () => effectiveStage(j),
      deadline: () => deadlineKey(j), londonlife: () => score(j,'london_cohabitation_score'), action: () => scalar(j.next_action),
      source: () => j.official_url, verified: () => j.status_checked_at || j.verified_at,
      confidence: () => ({high:3,medium:2,low:1})[confidence(j)] ?? null,
      artifacts: () => (state.available[j.id] || []).length, progress: () => effectiveStage(j), terms: () => number(j.salary_min), gates: () => scalar(j.hard_gate_status), channels: () => j.application_url || j.information_url || j.official_url
    };
    return scalar(mapping[key]?.());
  }
  function compareValues(a,b,direction='asc') {
    const an = a === null || a === undefined || a === '', bn = b === null || b === undefined || b === '';
    if (an && bn) return 0;
    if (an) return 1;
    if (bn) return -1;
    const cmp = typeof a === 'number' && typeof b === 'number' ? a-b : String(a).localeCompare(String(b),['zh-CN','en'],{numeric:true,sensitivity:'base'});
    return direction === 'desc' ? -cmp : cmp;
  }
  function hardGateRank(j) {
    const v = text(j.hard_gate_status).toLowerCase();
    if (/blocked|ineligible|not_met|不满足|明确障碍/.test(v)) return 3;
    if (/met|satisfied|pass|满足|无已知硬障碍/.test(v) && !/not|unknown|待|未/.test(v)) return 0;
    return 1;
  }
  function recommendedCompare(a,b) {
    const ga = grade(a) === null ? null : ({A:0,B:1,C:2,D:3})[grade(a)] ?? null;
    const gb = grade(b) === null ? null : ({A:0,B:1,C:2,D:3})[grade(b)] ?? null;
    return compareValues(ga,gb) || compareValues(hardGateRank(a),hardGateRank(b)) ||
      compareValues(sortValue(a,'confidence'),sortValue(b,'confidence'),'desc') ||
      compareValues(score(a,'coverage_pct'),score(b,'coverage_pct'),'desc') ||
      compareValues(sortValue(a,'overall'),sortValue(b,'overall'),'desc') || compareValues(a.organization,b.organization);
  }
  function viewMatch(j,view) {
    if (view === 'all') return true;
    if (view === 'vacancies') return j.record_type === 'vacancy';
    if (view === 'open') return verifiedOpen(j);
    if (['watch','history'].includes(view)) return j.record_type === view;
    return j.record_type === 'vacancy' && j.vacancy_status === view;
  }
  function selectRows(jobs,query=state) {
    const q = query.search.trim().toLocaleLowerCase();
    return jobs.filter(j => viewMatch(j,query.view)).filter(j => {
      if (q) {
        const haystack = [j.title,j.organization,j.team,j.lab,j.project,j.country,j.city,...listStrings(j.direction)].filter(Boolean).join(' ').toLocaleLowerCase();
        if (!haystack.includes(q)) return false;
      }
      return filters.every(([name,key]) => {
        const chosen = query.filters[name] || '';
        if (!chosen) return true;
        const value = filterValue(j,key);
        return chosen === '__unknown__' ? value === null : String(value) === chosen;
      });
    }).sort((a,b) => query.sort.key === 'deadline_then_relevance' ? (compareValues(deadlineKey(a),deadlineKey(b)) || compareValues(sortValue(a,'career'),sortValue(b,'career'),'desc') || recommendedCompare(a,b)) : query.sort.key === 'recommended' ? recommendedCompare(a,b) : compareValues(sortValue(a,query.sort.key),sortValue(b,query.sort.key),query.sort.direction) || compareValues(a.id,b.id));
  }
  function node(tag,content,className) {
    const n = document.createElement(tag);
    if (content !== undefined && content !== null) n.textContent = content;
    if (className) n.className = className;
    return n;
  }
  function link(label,url,external=false) {
    const a = node('a',label); a.href=url;a.title=label;
    if (external) {a.target='_blank';a.rel='noopener noreferrer';}
    return a;
  }
  function safeHTTP(url) { try {const u=new URL(url);return ['https:','http:'].includes(u.protocol)?u.href:null;} catch {return null;} }
  function safeMailto(value) {
    if(typeof value!=='string'||!/^mailto:/i.test(value))return null;
    try{const u=new URL(value),addresses=decodeURIComponent(u.pathname);if(/[\r\n<>]/.test(addresses)||addresses.length>500)return null;return addresses.split(/[;,]/).every(v=>/^[^\s<>@,;]+@[^\s<>@,;]+\.[^\s<>@,;]+$/.test(v.trim()))?addresses:null;}catch{return null;}
  }
  function mailChannel(parent,address,label='邮件投递') {
    parent.append(node('span',label,'application-email-label'));
    const addr=node('span',address,'application-email');addr.tabIndex=0;addr.title='可选中地址复制；不会自动打开邮件客户端';parent.append(addr);
    const button=node('button','复制地址','copy-email');button.type='button';button.title='仅复制邮件地址，不创建草稿或发信';
    button.addEventListener('click',async()=>{try{if(!navigator.clipboard)throw new Error('no clipboard');await navigator.clipboard.writeText(address);button.textContent='已复制';}catch{button.textContent='请选中地址复制';addr.focus();}});parent.append(button);
  }
  function sub(parent,label) {const n=node('small',label,'cell-sub');n.title=label;parent.append(n);}
  function scoreCell(td,value,coverage) {
    if (value === null) td.append(node('span','未评分','unknown'));
    else td.append(node('span',Number(value.toFixed(2)).toString(),'score-number'));
    sub(td,coverage === null ? '覆盖率未知' : `覆盖 ${Number(coverage.toFixed(2))}%`);
  }
  function expiryStatus(j,now=new Date()) {
    if(j.vacancy_status==='closed')return {status:'expired',label:'已过期／官方关闭',reason:'来源核实状态为closed；不覆盖个人投递阶段',uncertain_time:false};
    if(j.deadline_iso&&!Number.isNaN(Date.parse(j.deadline_iso))){const expired=+now>=Date.parse(j.deadline_iso);return {status:expired?'expired':'not_expired',label:expired?'已过期':'未截止',reason:'按已证实精确截止时刻比较',uncertain_time:false};}
    const date=j.deadline_date;
    if(typeof date!=='string'||!/^\d{4}-\d{2}-\d{2}$/.test(date)||Number.isNaN(Date.parse(date+'T12:00:00Z'))||new Date(date+'T12:00:00Z').toISOString().slice(0,10)!==date)return {status:'unknown',label:'截止未知',reason:'没有有效官方截止；planning_deadline不当作已证实截止',uncertain_time:true};
    const calendar=zone=>new Intl.DateTimeFormat('sv-SE',{timeZone:zone,year:'numeric',month:'2-digit',day:'2-digit'}).format(now);
    if(j.deadline_timezone){try{const expired=calendar(j.deadline_timezone)>date;return {status:expired?'expired':'not_expired',label:expired?'已过期·时刻未明':'未超过截止日期·时刻未明',reason:'按岗位原地日期比较，当天不判过期；未补造午夜',uncertain_time:true};}catch{/* Unknown IANA zone: use conservative whole-world date bounds below. */}}
    const earliestLocalDate=calendar('Etc/GMT+12'),latestLocalDate=calendar('Pacific/Kiritimati');
    if(earliestLocalDate>date)return {status:'expired',label:'已过期·时刻未明',reason:'各时区日期均已超过截止日；原时区和时刻未核实',uncertain_time:true};
    if(latestLocalDate<=date)return {status:'not_expired',label:'未超过截止日期·时刻未明',reason:'各时区尚未超过截止日；原时区和时刻未核实',uncertain_time:true};
    return {status:'unknown',label:'截止未知·时区未明',reason:'日期位于跨时区边界；不使用电脑时区代替岗位当地日期',uncertain_time:true};
  }
  function deadlineInfo(j,now=new Date()) {
    const date=deadlineKey(j), out={primary:'未公布／未知',secondary:null,alert:null};
    if (j.deadline_iso && !Number.isNaN(Date.parse(j.deadline_iso))) {
      const d=new Date(j.deadline_iso);
      out.primary=[j.deadline_date || date,j.deadline_time,j.deadline_timezone].filter(Boolean).join(' ');
      if (!j.deadline_time) out.primary=j.deadline_iso;
      out.secondary='伦敦 '+new Intl.DateTimeFormat('sv-SE',{dateStyle:'short',timeStyle:'short',timeZone:'Europe/London'}).format(d);
      const delta=d-now;
      if(delta<0)out.alert='截止时刻已过（招聘状态仍以来源核验为准）';
      else if(delta<48*3600000)out.alert='距离已知截止时刻不足 48 小时';
    } else if (date) {
      out.primary=String(j.deadline_date || date)+' · 仅日期';
      const zone=j.deadline_timezone || 'Europe/London';
      let today;
      try {today=new Intl.DateTimeFormat('sv-SE',{year:'numeric',month:'2-digit',day:'2-digit',timeZone:zone}).format(now);}catch{today=null;}
      if(today && date<today)out.alert='规划日期已过；未据此自动改招聘状态';
      else if(today && date===today)out.alert='已到该日期；截止时刻未知';
      out.secondary=j.deadline_timezone ? `原地时区 ${j.deadline_timezone}，时刻未知` : '时区／时刻未证实，不换算伦敦时刻';
    }
    if(j.deadline_conflict){out.secondary=(out.secondary?out.secondary+'；':'')+`来源冲突，保守规划 ${text(datePart(j.planning_deadline))}`;}
    else if(datePart(j.planning_deadline) && datePart(j.planning_deadline)!==j.deadline_date){out.secondary=(out.secondary?out.secondary+'；':'')+'规划 '+text(datePart(j.planning_deadline));}
    return out;
  }
  function renderCell(td,j,key) {
    switch(key) {
      case 'progress': {const hook=node('div',undefined,'progress-cell');hook.dataset.progressId=j.id;if(document.body.dataset.mode==='public-safe'){hook.textContent='公开版本不含私人进度';}else{hook.textContent=STAGE[effectiveStage(j)] || text(effectiveStage(j));hook.dataset.progressEditable='true';}td.append(hook);break;}
      case 'terms': {td.append(node('span',text(j.salary_original || (j.salary_min!==null&&j.salary_min!==undefined?`${text(j.salary_currency)} ${j.salary_min}${j.salary_max!==null&&j.salary_max!==undefined?'–'+j.salary_max:''}/${text(j.salary_period)}`:null))));sub(td,[j.contract_type,j.contract_duration].filter(Boolean).map(text).join(' · ') || '合同未知');break;}
      case 'gates': {const gates={pending:'待核',provisionally_satisfied_near_completion:'接近完成可申请',pending_doctoral_timing:'博士时点待核',blocked_standard_SW_at_advertised_salary:'薪资不满足通常SW',major_domain_gap:'核心方向缺口',satisfied:'已满足',met:'已满足',not_applicable:'不适用',blocked:'存在硬障碍'};const gate=node('span',gates[j.hard_gate_status] || '待核');gate.title=text(j.hard_gate_status);td.append(gate);sub(td,VISA[j.visa_filter_status] || '具体岗位签证待核');if(j.ai_application_policy==='research_only_human_authored_application')sub(td,'申请须本人撰写，禁AI文本');if(j.ai_application_policy==='disclosure_required')sub(td,'AI辅助须申报');break;}
      case 'channels': {const info=safeHTTP(j.information_url || j.official_url),apply=safeHTTP(j.application_url),mail=safeMailto(j.application_url),context=[j.application_channel,j.application_instructions,'渠道核实 '+text(j.channel_verified_at)].filter(Boolean).map(text).join('\n');td.title=context;if(info){const a=link('官方信息 ↗',info,true);a.title=context;td.append(a);}else td.append(node('span','信息待核','unknown'));if(apply){td.append(node('br'));const a=link('投递入口 ↗',apply,true);a.title=context;td.append(a);}else if(mail){mailChannel(td,mail,String(j.application_channel||'').toLowerCase().includes('host')?'Host意向':'邮件投递');}else{sub(td,j.vacancy_status==='closed'?'已关闭／无入口':j.application_url?'渠道原文见详情':'入口待核');}const checked=typeof j.channel_verified_at==='string'&&/^\d{4}-\d{2}-\d{2}/.test(j.channel_verified_at)?j.channel_verified_at.slice(5,10):null;sub(td,checked?'核'+checked:'未核');break;}
      case 'priority': {const g=grade(j);td.append(node('span',g || '未评级',`badge ${g?'grade-'+g:''}`));sub(td,j.active_recommendation?.reason || '当前建议尚未形成');break;}
      case 'overall': scoreCell(td,score(j,'provisional_overall'),score(j,'coverage_pct'));break;
      case 'career': {scoreCell(td,score(j,'career_fit_score'),score(j,'career_fit_coverage_pct'));const g=grade(j);sub(td,`${g?'当前 '+g:'未评级'} · ${STATUS[j.vacancy_status]||'状态未知'}`);break;}
      case 'title': td.append(link(text(j.title),`registry/${encodeURIComponent(j.id)}.html`));sub(td,[j.organization,j.team||j.lab||j.project].filter(Boolean).map(text).join(' · '));break;
      case 'org': td.append(node('span',text(j.organization)));break;
      case 'team': td.append(node('span',text(j.team || j.lab || j.project)));break;
      case 'place': td.append(node('span',[j.country,j.city].filter(Boolean).join(' / ') || '未知'));sub(td,text(j.remote_policy));break;
      case 'london': td.append(node('span',j.is_london===true?'是':j.is_london===false?'否':'未知'));sub(td,text(j.remote_policy));break;
      case 'salary': {const raw=j.salary_original;if(raw)td.append(node('span',text(raw)));else if(j.salary_min!==null&&j.salary_min!==undefined){td.append(node('span',`${text(j.salary_currency)} ${j.salary_min}${j.salary_max!==null&&j.salary_max!==undefined?'–'+j.salary_max:''} / ${text(j.salary_period)}`));}else td.append(node('span','未公布／未知','unknown'));if(j.salary_estimate)sub(td,'另有市场估计，见详情；不视为 offer');break;}
      case 'contract': td.append(node('span',text(j.contract_type)));sub(td,text(j.contract_duration));break;
      case 'direction': td.append(node('span',text(j.direction)));break;
      case 'channel': td.append(node('span',text(j.recruitment_channel)));break;
      case 'status': td.append(node('span',j.record_type==='watch'?'团队观察':j.record_type==='history'?'历史记录':STATUS[j.vacancy_status] || '未知',`badge status-${j.record_type==='vacancy'?j.vacancy_status:j.record_type}`));sub(td,j.status_reason || '未提供状态依据');if(j.vacancy_status==='open'&&!verifiedOpen(j)&&j.record_type==='vacancy')sub(td,'未达到已证实开放条件');break;
      case 'stage': td.append(node('span',STAGE[effectiveStage(j)] || text(effectiveStage(j))));break;
      case 'deadline': {const d=deadlineInfo(j);const primary=node('span',d.primary);primary.title=d.primary;td.append(primary);if(d.secondary)sub(td,d.secondary);const expiry=expiryStatus(j);if(expiry.status==='expired'&&expiry.uncertain_time){const alert=node('small',expiry.label,'deadline-alert');alert.title=expiry.reason;td.append(alert);}else if(d.alert)td.append(node('small',d.alert,'deadline-alert'));break;}
      case 'londonlife': {const n=score(j,'london_cohabitation_score');td.append(node('span',n===null?'未评分':Number(n.toFixed(2)).toString(),n===null?'unknown':'score-number'));sub(td,'独立偏好维度；非硬否决');break;}
      case 'action': {const action=node('span',text(j.next_action));action.title=text(j.next_action);td.append(action);if(document.body.dataset.mode!=='public-safe'){const note=node('div',undefined,'progress-note');note.dataset.progressNoteId=j.id;td.append(note);}break;}
      case 'source': {const u=safeHTTP(j.official_url);if(u)td.append(link('官方来源 ↗',u,true));else td.append(node('span','未取得官方职位页','unknown'));sub(td,`${text(j.jd_completeness)} JD`);break;}
      case 'verified': td.append(node('span',text(j.status_checked_at || j.verified_at)));break;
      case 'confidence': td.append(node('span',CONF[confidence(j)] || '未知',`badge conf-${confidence(j)||'unknown'}`));sub(td,j.source_confidence?.reason || '未提供理由');break;
      case 'artifacts': {if(document.body.dataset.mode==='public-safe'){td.append(node('span','不含私人材料'));break;}const a=state.available[j.id] || [];td.append(link(a.length?`${a.length}文件`:'未生成',`registry/${encodeURIComponent(j.id)}.html`));const stage=j.deep_review_status==='preserved_round1'?'首轮':j.deep_review_status==='completed_round2_draft'?'新稿':j.deep_review_status==='research_only_no_generated_application'?'仅研究':null;if(stage)sub(td,stage);td.title=text(j.deep_review_status);break;}
      default: td.append(node('span','未知'));
    }
  }
  function renderHeaders() {
    const tr=$('column-headers');tr.replaceChildren();
    for(const c of columns){const th=node('th');th.scope='col';th.dataset.key=c.key;th.className='col-'+c.key;if(state.hidden.has(c.key))th.classList.add('hidden-column');th.setAttribute('aria-sort',state.sort.key===c.key?(state.sort.direction==='asc'?'ascending':'descending'):'none');const b=node('button',c.label);b.type='button';b.setAttribute('aria-label',`按${c.label}排序`);if(c.key==='salary')b.title='先按原币与周期分组，再按金额排序；不是购买力比较';b.addEventListener('click',()=>{state.sort={key:c.key,direction:state.sort.key===c.key&&state.sort.direction==='asc'?'desc':'asc'};$('sort-view').value='';render();});th.append(b);tr.append(th);}
  }
  function render() {
    const rows=selectRows(state.jobs);renderHeaders();const body=$('jobs-body');body.replaceChildren();
    const fragment=document.createDocumentFragment();
    for(const j of rows){const tr=node('tr');tr.dataset.id=j.id;for(const c of columns){const td=node('td');td.className='col-'+c.key;if(state.hidden.has(c.key))td.classList.add('hidden-column');renderCell(td,j,c.key);tr.append(td);}fragment.append(tr);}body.append(fragment);
    const viewSize=state.jobs.filter(j=>viewMatch(j,state.view)).length;
    $('results-count').textContent=`当前筛选 ${rows.length} 条 / 当前视图 ${viewSize} 条 / 完整候选池 ${state.jobs.length} 条`;
    $('empty').hidden=rows.length!==0;
    document.dispatchEvent(new CustomEvent('registry:rendered',{detail:{ids:rows.map(j=>j.id)}}));
    for(const b of $('view-tabs').querySelectorAll('button'))b.setAttribute('aria-pressed',String(b.dataset.view===state.view));
    $('export-filtered').textContent=`导出筛选 CSV（${rows.length}）`;
    $('build-note').textContent=`当前模式：${document.body.dataset.mode==='public-safe'?'公开安全版本':'本人授权公开研究版本'}。当前排序：${state.sort.key==='deadline_then_relevance'?'截止 → 相关度':state.sort.key==='recommended'?'建议优先':(columns.find(c=>c.key===state.sort.key)?.label || state.sort.key)}；未知始终排后。`;
  }
  function urgentDeadlines(jobs,now=new Date()) {
    const windowMs=48*3600000;
    const format=(d,zone)=>new Intl.DateTimeFormat('zh-CN',{timeZone:zone,year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',hour12:false,timeZoneName:'short'}).format(d);
    return jobs.filter(j=>j.record_type==='vacancy'&&j.deadline_iso&&!Number.isNaN(Date.parse(j.deadline_iso))).map(j=>{
      const date=new Date(j.deadline_iso),delta=date-now;
      let original;
      try{original=j.deadline_timezone?format(date,j.deadline_timezone):j.deadline_iso;}catch{original=j.deadline_iso;}
      return {job:j,delta,expired:delta<0,original,london:format(date,'Europe/London'),perth:format(date,'Australia/Perth')};
    }).filter(item=>item.delta>=-windowMs&&item.delta<windowMs).sort((a,b)=>a.delta-b.delta);
  }
  function renderUrgentDeadlines() {
    const target=$('urgent-deadlines'),items=urgentDeadlines(state.jobs);
    target.replaceChildren();target.hidden=items.length===0;
    if(!items.length)return;
    target.append(node('h2','紧急截止 · 按当前时间计算'));
    target.append(node('p','以下为未来48小时内或刚过去48小时内的已知精确截止；日期未证实到时刻的记录不强行推算。招聘状态保留来源核验结果。','urgent-intro'));
    const list=node('ul');
    for(const item of items){
      const j=item.job,li=node('li',undefined,item.expired?'urgent-expired':'urgent-upcoming');
      const heading=node('div',undefined,'urgent-heading');
      heading.append(node('strong',item.expired?'截止时刻已过':'不足48小时截止'),link(`${text(j.organization)} · ${text(j.title)}`,`registry/${encodeURIComponent(j.id)}.html`));
      li.append(heading);
      li.append(node('p',`原地 ${item.original} · 伦敦 ${item.london} · Perth ${item.perth}`));
      if(j.deadline_original)li.append(node('small',`来源原文：${text(j.deadline_original)}`));
      li.append(node('small',`来源核实招聘状态：${STATUS[j.vacancy_status]||'未知'}；提示只反映时间经过，不自动改成开放或关闭。`));
      list.append(li);
    }
    target.append(list);
  }
  function populateFilters() {
    for(const [name,key,labels] of filters){const select=$('filter-'+name);const values=[...new Set((key==='application_stage'?[...Object.keys(STAGE),...state.jobs.map(j=>filterValue(j,key))]:key==='expiry_status'?['expired','not_expired','unknown']:state.jobs.map(j=>filterValue(j,key))).filter(v=>v!==null))].sort((a,b)=>compareValues(a,b));for(const v of values){const o=node('option',labels?.[v] || text(v));o.value=String(v);select.append(o);}if(state.jobs.some(j=>filterValue(j,key)===null)){const o=node('option','未知／未提供');o.value='__unknown__';select.append(o);}select.addEventListener('change',()=>{state.filters[name]=select.value;render();});}
  }
  function buildCounts() {
    const counts=[['职位',state.jobs.filter(j=>j.record_type==='vacancy').length],['完整记录',state.jobs.length],['已证实开放',state.jobs.filter(verifiedOpen).length],['即将开放',state.jobs.filter(j=>viewMatch(j,'upcoming')).length],['状态未知',state.jobs.filter(j=>viewMatch(j,'unknown')).length],['已关闭',state.jobs.filter(j=>viewMatch(j,'closed')).length],['团队观察',state.jobs.filter(j=>j.record_type==='watch').length],['历史记录',state.jobs.filter(j=>j.record_type==='history').length]];
    for(const [label,count] of counts){const p=node('span',undefined,'count-pill');p.append(node('span',label),node('strong',String(count)));$('pool-counts').append(p);}
  }
  function buildColumns() {
    for(const c of columns){const label=node('label');const input=node('input');input.type='checkbox';input.checked=!state.hidden.has(c.key);input.value=c.key;input.disabled=c.key==='title';input.addEventListener('change',()=>{input.checked?state.hidden.delete(c.key):state.hidden.add(c.key);render();});label.append(input,node('span',c.label));$('column-controls').append(label);}
  }
  function csvCell(v) {
    if(v===null||v===undefined)return '""';
    let s=typeof v==='object'?JSON.stringify(v):String(v);
    if(typeof v!=='number'&&(/^[\s\uFEFF]*[=+\-@]/.test(s)||/^[\t\r\n]/.test(s)))s="'"+s;
    return '"'+s.replaceAll('"','""')+'"';
  }
  function csvForRows(rows) {
    const fields=['id','record_type','organization','title','team','country','city','is_london','job_type','direction','vacancy_status','verified_open','status_reason','status_checked_at','recommendation','recommendation_reason','provisional_overall','coverage_pct','career_fit_score','career_fit_coverage_pct','london_cohabitation_score','location_preference_score','salary_min','salary_max','salary_currency','salary_period','salary_original','contract_type','contract_duration','recruitment_channel','application_stage','deadline_original','deadline_date','deadline_time','deadline_timezone','deadline_iso','deadline_precision','deadline_conflict','planning_deadline','official_url','information_url','application_url','application_channel','channel_verified_at','application_instructions','verified_at','source_confidence','deep_review_status','next_action','source_ids','scores','essential_requirements','preferred_requirements','ai_application_policy'];
    if(document.body.dataset.mode!=='public-safe')fields.push('visa','candidate_evidence_refs','missing_evidence','application_history_refs','artifacts','local_progress_stage','local_progress_updated_at','local_progress_applied_at','local_progress_follow_up_date','local_progress_note');
    return '\uFEFF'+[fields,...rows.map(j=>fields.map(k=>k==='local_progress_stage'?effectiveStage(j):k.startsWith('local_progress_')?(state.overrides[j.id]?.[k.replace('local_progress_','')]??null):k==='recommendation'?grade(j):k==='recommendation_reason'?j.active_recommendation?.reason:k in (j.scores||{})?j.scores[k]:j[k]??null))].map(row=>row.map(csvCell).join(',')).join('\r\n')+'\r\n';
  }
  function download(content,type,name) {const url=URL.createObjectURL(new Blob([content],{type}));const a=link('',url);a.download=name;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);}
  function clear() {state.view='vacancies';state.search='';state.filters={};state.sort={key:'deadline_then_relevance',direction:'asc'};$('search').value='';for(const [name] of filters)$('filter-'+name).value='';$('sort-view').value='deadline_then_relevance';render();}
  async function init() {
    try {
      const [r,a]=await Promise.all([fetch('data/jobs.json'),fetch('assets/available-artifacts.json')]);
      if(!r.ok)throw new Error(`读取 data/jobs.json 失败：HTTP ${r.status}`);
      const payload=await r.json();
      if(!payload || !Array.isArray(payload.jobs))throw new Error('canonical JSON 缺少 jobs 数组');
      const ids=new Set();for(const j of payload.jobs){if(!j||typeof j.id!=='string'||ids.has(j.id))throw new Error('canonical 数据含重复或无效 ID');ids.add(j.id);}
      state.payload=payload;state.jobs=payload.jobs;state.available=a.ok?await a.json():{};
      populateFilters();buildCounts();buildColumns();renderUrgentDeadlines();
      document.addEventListener('click',e=>{for(const panel of document.querySelectorAll('.filter-float[open],.columns[open]'))if(!panel.contains(e.target))panel.open=false;});
      document.addEventListener('keydown',e=>{if(e.key==='Escape')for(const panel of document.querySelectorAll('.filter-float[open],.columns[open]'))panel.open=false;});
      setInterval(renderUrgentDeadlines,60000);
      $('search').addEventListener('input',()=>{state.search=$('search').value;render();});$('clear').addEventListener('click',clear);
      for(const b of $('view-tabs').querySelectorAll('button'))b.addEventListener('click',()=>{state.view=b.dataset.view;render();});
      $('sort-view').addEventListener('change',()=>{const val=$('sort-view').value;if(!val)return;const [key,direction]=val.split(':');state.sort={key,direction:direction||'asc'};render();});
      const suffix=String(payload.as_of||'current').substring(0,10).replaceAll('-','');
      $('export-filtered').addEventListener('click',()=>download(csvForRows(selectRows(state.jobs)),'text/csv;charset=utf-8',`jobs_filtered_${suffix}.csv`));
      $('export-all').addEventListener('click',()=>download(csvForRows(state.jobs),'text/csv;charset=utf-8',`jobs_all_${suffix}.csv`));
      $('export-json').addEventListener('click',()=>download(JSON.stringify(state.payload,null,2)+'\n','application/json;charset=utf-8',`jobs_${suffix}.json`));
      document.dispatchEvent(new CustomEvent('registry:ready',{detail:{jobs:state.jobs,publicSafe:document.body.dataset.mode==='public-safe'}}));
      render();
    } catch(e) {$('error').hidden=false;$('error').textContent=`无法显示职位表：${e.message}。请刷新页面，或下载源数据 JSON／CSV。`;$('results-count').textContent='数据读取失败';}
  }
  window.registryProgressAPI={
    get publicSafe(){return document.body.dataset.mode==='public-safe';},
    getJobs:()=>JSON.parse(JSON.stringify(state.jobs)),
    getStage:j=>effectiveStage(j),
    setOverrides:entries=>{
      if(document.body.dataset.mode==='public-safe')return false;
      const overrides=Object.create(null),known=new Set(state.jobs.map(j=>j.id));
      const source=entries?.entries&&!Array.isArray(entries)?entries.entries:entries;
      const pairs=Array.isArray(source)?source.map(e=>[e.job_id||e.id,e]):Object.entries(source||{});
      for(const [id,entry] of pairs){
        if(!known.has(id)||!entry||typeof entry!=='object')continue;
        const value={};
        for(const key of ['stage','updated_at','applied_at','follow_up_date','note'])if(entry[key]!==undefined)value[key]=entry[key];
        if(value.stage==='draft')value.stage='preparing';
        if(value.stage==='not_found_in_audit')value.stage='not_applied_unconfirmed';
        if(value.stage&&!Object.hasOwn(STAGE,value.stage))value.stage='unknown';
        overrides[id]=value;
      }
      state.overrides=overrides;
      if(state.payload)render();
      return true;
    }
  };
  window.registryTesting={csvCell,compareValues,deadlineInfo,urgentDeadlines,selectRows,verifiedOpen,csvForRows,state,render,effectiveStage,safeMailto,expiryStatus};
  init();
})();
