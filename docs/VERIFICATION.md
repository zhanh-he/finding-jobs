# Canva 发布前验收 · 2026-10-22

- 114条canonical，原103条ID均保留；仅既有Cambridge和Tencent两条作本轮明确状态／一致性修正，其他旧记录仅增加公开事实投影开关。
- 原四岗包、此前三套材料及Submitted原件无内容diff；161个材料引用的文件与SHA匹配；提交归档2个SHA匹配。
- 数据/schema/source FK/别名去重/unknown加权/必需与加分项/投递状态证据验证：0错误、0警告。
- Python 37项测试、Registry JS 61断言、Progress JS26断言通过。
- 构建重复执行字节一致；214个HTML、1265个相对链接／锚点、403个静态文件通过。公开安全投影49条，已无孤立旧历史详情页。
- 本地浏览器：Canva11行，open1/closed5/unknown5；未知及关闭无投递按钮；Stockholm搜出3条含Spotify；Cambridge默认已投递，后续本机阶段仍优先。Shortlist刷新持久化；旧备份／进度key兼容由回归测试覆盖；真实筛选CSV下载11行。
- 默认桌面与390×844检查通过；手机页面不整体横向溢出，表格在独立区域滚动。浮动筛选默认收起。
- 新Canva材料未入repo/Pages/download indexes；公开新增要求不含候选逐项私有证据；本地两页DOCX/PDF全部渲染检查，三格式正文一致。
- 只读维护脚本实跑完整102条分页、无duplicate，不修改canonical；403/404限制没有绕过。

本文件记录发布前检查。精确推送commit、Actions运行及线上验收以GitHub部署记录和本轮本地交付的DEPLOYMENT_VERIFICATION.json为准；提交文件存在不代表已上线。
