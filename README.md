# 音乐／音频 AI · 职位与投递进度表

[打开线上职位表](https://zhanh-he.github.io/finding-jobs/private/index.html) · [新版使用说明](https://zhanh-he.github.io/finding-jobs/private/shared/round2_online_guide.html)

2026-10-22更新第二轮桌面版。默认37条具体职位，完整候选池103条（另含14观察、52历史），按截止→相关度排序；核查基准2026-10-21，当前时间的已过期标记与广告核查快照分开。未知不会当作0或自动判定关闭。十列10px桌面表格、浮动收起筛选器、官方信息/实际投递入口、CSV/JSON导出均可用。

原Cambridge、Spotify、ElevenLabs、Apple四套成果保留；新增SCRIME、Aalto、Tencent三套申请材料。所有自动生成文本仍为草稿。本次网站更新没有联系雇主或提交申请。Cambridge后来上传的定稿CV另有下载副本，仅移除本机失效超链接；原`formal_doc/`用户上传内容保留，未据文件名推断已提交。CHRIS6表单未新增到Pages。

## 进度保存

阶段、备注、实际投递日及下次检查日只保存到当前浏览器localStorage，不写入GitHub源数据，不向雇主发送。换浏览器/设备、localhost切换到线上时不会自动同步。先在旧页面“备份进度”，再到新页面“导入进度”；同岗位ID合并覆盖，其余进度保留。源JSON按钮不含本机进度，CSV有独立`local_progress_*`列，进度JSON须单独备份。

已过期独立于已投递/面试/拒绝等阶段；日期只有天时不补午夜。“未投递·待确认”表示审计缺口，不证明从未申请。

## 内容与构建

- `private/data/jobs.json`：授权公开的103条结构化职位/历史结论，已去原始邮件摘要、Gmail深链和本机路径。
- `private/registry/`：每条记录的证据、缺口、薪资合同、签证与真实材料链接。
- `private/jobs/`：原四套报告和申请草稿，内容保留。
- `private/new_materials/`：新三套可编辑DOCX、PDF、TXT及报告/信件/矩阵/面试准备。
- `private/jd_sources/`：单独白名单选取的官方JD核验快照，不含原邮箱备份或原CV文件。
- `public-safe/`：单独的41条公开职位事实投影，不含个人评估、签证、申请史或CV/信件。
- `site-assets/`、`scripts/registry_ui.py`、`scripts/build_registry.py`：无框架、stdlib即可重建。

```sh
python3 scripts/build_registry.py
python3 scripts/prepare_pages.py
node scripts/test_registry_logic.js
node scripts/test_progress_logic.js
python3 scripts/serve.py --view private --port 8765
```

最后一条仅本机预览，端口占用时换一个，不结束他人的服务。GitHub Actions在main更新后构建并验证`_site/`再部署。无需读取本机私有输入包；不要运行旧`scripts/build.py`覆盖新版首页。所有相对链接兼容`/finding-jobs/`子路径。

## 公开范围

用户先前明确批准真实姓名、邮箱、完整CV/信件、私人分析、签证、共同生活偏好、申请史、论文状态和推荐人联系方式公开，并于2026-10-22明确要求更新线上。`private/`为历史目录名，不是访问控制。公开站点可由任何人读取。

本次不连带上传原始邮箱备份、原CV源文件、本机绝对路径、凭据、私有录音/模型、运行日志或本地打包文件。用户自行上传到`formal_doc/`的既有内容不由本次删除或覆盖。`.gitignore`不撤销已经存在的Git历史。Helsinki申请正文须本人写，未生成该岗定制文本；Turku AI使用须申报。Huawei按用户给出的保密边界只保留概括项目描述。
