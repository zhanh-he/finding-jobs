# 音乐／音频 AI · 职位与投递进度表

[完整职位表](https://zhanh-he.github.io/finding-jobs/private/index.html) · [Canva 视图](https://zhanh-he.github.io/finding-jobs/private/index.html?view=canva) · [Canva 决策报告](https://zhanh-he.github.io/finding-jobs/private/shared/canva_decision_20261022.html)

2026-10-22 Canva 更新：完整池114条＝43条具体职位、19条团队观察、52条历史记录。具体职位状态18开放、7关闭、18未知；这是各记录核查日的状态，不是114个可投岗位。本轮Canva覆盖官方列表102条（100＋2分页），新增1个开放冲刺岗、5个关闭旧岗、5类状态未知的官方NeurIPS团队线索。没有已核实开放的正常主攻Canva岗位。其他公司的原核查日期保持，不冒称本轮全部重新核验。

默认表格按截止→相关度；浮动收起筛选器，搜索、排序、列设置、CSV／JSON导出可用。Canva视图分别展示方向匹配与职级匹配。多地点参与搜索／筛选；薪资先按币种、周期、税前后分组，仅组内比较金额，不进行隐含汇率换算。桌面紧凑显示；手机表格横向滚动。

Cambridge用户本轮明确确认已提交，实际提交日未猜测。原定向提交稿和原四岗成果保持；不重复催投。旧报告属于带日期的归档，不代表当前招聘状态。未使用的信件仍是未使用草稿。申请表未加入Pages下载。新Canva evaluation/post-training底稿及询问模板仅本地待审，没有进入本仓库或Pages。

## 数据与目录

- **唯一 canonical：`private/data/jobs.json`**。所有列表、详情、Canva报告、CSV及公开安全投影从它生成；不要手动维护第二份事实表。
- `private/data/jobs.schema.json`：结构规范；`sources`注册表记录官方来源及核查日期。新Canva条目未知分数全部null，不以主观数字包装职级跨度。
- `public-safe/data/jobs.json`：`scripts/public_projection.py`字段白名单派生产物，包含49条公开职位／团队事实；不含个人匹配、移民分析、投递史、CV和信件。
- `site-assets/`、`scripts/registry_ui.py`：UI源码；`scripts/build_registry.py`统一构建。
- `private/registry/`：生成详情；`private/shared/canva_decision_20261022.html`：从同一数据生成的中文决策。
- `private/jobs/`保留原四岗包，`private/new_materials/`保留此前三套材料；`formal_doc/Submitted_CVResume/`为不可覆盖提交归档。
- `docs/HANDOFF.md`：本轮状态与后续入口；`docs/RESEARCH_SOURCES.md`：公开研究来源。
- `.local/canva_20261022/`：被Git排除的详细候选证据／冲突登记；新草稿保存在本地交付目录，不参与网站构建。无需这些私有输入即可重建站点。

## 进度与短名单

阶段、备注、投递日、跟进日及短名单只保存到当前浏览器localStorage，使用原有storage key；刷新／部署不清空记录。源数据中用户确认的提交状态作为默认值；用户本机后续阶段优先。换浏览器、localhost换线上时，先“备份进度”再“导入进度”。旧备份没有shortlisted仍可导入。CSV附带本地进度列；源JSON不含本机进度。截止过期与已提交／面试／拒绝是两个不同维度。

## 构建与验收

Python3及Node即可，无第三方运行依赖：

```sh
python3 scripts/validate_registry.py
python3 -m unittest discover -s scripts -p 'test_*.py'
node scripts/test_registry_logic.js
node scripts/test_progress_logic.js
python3 scripts/build_registry.py
python3 scripts/prepare_pages.py
python3 scripts/update_manifest.py
python3 scripts/serve.py --view private --port 8765
```

端口占用请换端口，不结束其他人的服务。`prepare_pages.py`校验所有HTML相对链接／锚点、禁止绝对本机路径／凭据／原邮件备份，生成`_site/`。相对链接兼容`/finding-jobs/`子路径。不要运行旧`scripts/build.py`覆盖新版首页。发布前检查diff、提交原件hash及所有真实下载；测试后需浏览器检查桌面与手机，以及实际线上部署。

维护Canva状态时可运行 `python3 scripts/check_canva.py`，只读官方API分页／既有ID并把报告写入被忽略的`.local/`，**不自动修改canonical、不投递、不部署**。404／403保留访问限制，不等同关闭。审阅证据后再更新JSON及来源时间，运行上述检查。岗位城市镜像按职位族合并；旧ID别名不重复计数。

GitHub Actions在main更新后运行数据／UI／链接检查并部署。正常`git push`前先fetch检查并行改动；不得force push。提交成功与Pages部署成功分别确认，再检查真实URL。新CV／信件必须经本轮用户审阅和明确批准后才能加入公开下载。

## 公开范围

`private/`是历史目录名，不提供访问控制；现有网站和仓库为公开。历史广泛公开授权不覆盖本轮新草稿的“本地待审”限制。见[PUBLICATION_SCOPE.md](PUBLICATION_SCOPE.md)。本轮只发布官方岗位资料、必要状态判断和代码／通用维护说明，不增加联系方式、原邮件、申请表或新CV披露。`.gitignore`不会撤销已进入Git历史的信息。Huawei保密细节、指标和内部实现不加入demo。
