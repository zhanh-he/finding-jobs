# 音乐与音频 AI 求职研究与申请材料

静态网站包含四岗比较、逐项证据、定制Resume和Cover Letter下载、研究计划与签证/职业分析。所有申请材料均为草稿；岗位状态、签证与薪资资料核查日为2026-10-21，之后可能变化。本站不代表雇主或移民机构，也不代投递。

## 网站入口

[打开网站](https://zhanh-he.github.io/finding-jobs/) · [仓库内首页](private/index.html) · [运行与发布说明](#本地预览)

根首页以相对路径转到 `private/index.html`。所有岗位页、报告和下载采用相对链接，支持 `/finding-jobs/` 子路径。`private` 是本地项目沿用的目录名，**在公开仓库和公开Pages中不提供隐私保护**。`public-safe/` 是单独的匿名示例，并非真实材料的隐藏机制。

## 内容

- `private/jobs/`：Cambridge、Spotify、ElevenLabs、Apple的报告、CSV/易读证据矩阵、英文Resume TXT/DOCX/PDF、Cover Letter、未发送的联系草稿和面试准备。
- `private/shared/`：跨岗结论、官方签证证据、问题清单、项目贡献模板、来源与验收记录。
- `private/screenshots/`：本地桌面和手机验收截图。
- `public-safe/`：虚构匿名示例。
- `scripts/`：无框架构建、链接验证、预览和Pages打包脚本。
- `.github/workflows/pages.yml`：GitHub Pages部署流程。

## 本地预览

```sh
python3 scripts/serve.py --view private --port 8765
```

打开 `http://127.0.0.1:8765/`。服务仅绑定本机，按Ctrl+C结束。无Node或前端依赖。

修改Markdown/summary后：

```sh
python3 scripts/build.py --view private
python3 scripts/prepare_pages.py
```

后者验证链接并生成仅供部署的 `_site/`。新增真实简历文件必须存在才加入下载链接；不要放占位死链接。DOCX/PDF改稿后须重新渲染并检查，不能只修改TXT。

## 发布边界

用户在本聊天已明确确认完整公开，包括姓名、个人邮箱、完整CV/信件、签证需求、共同生活偏好、申请史、未发表稿件状态及推荐人姓名与邮箱。原报告中“仅本地/禁止上传”是制作时的历史边界；本次发布按上述新的明确授权执行。不得把公开仓库或 `noindex` 当成隐私保护。未发送联系稿不是发信记录；已公开页面也不等于Huawei或其他雇主批准披露。不得上传原始CV文件、凭据、工作目录、私有音频/模型或本机日志。`.gitignore`不能删除已经进入Git历史的内容。

正式博士授予未确认，不称已获博士；用户已答辩、预计2026年11月证书。Huawei展示边界按用户最新指示保守处理。成绩或作品属于团队时，不自动归为个人成果。
