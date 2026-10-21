# 独立QA复核（集成前快照）

核查2026-10-21；本QA仅只读本地产物、脚本与源CV，并修改Spotify自己负责的来源/签证/summary。没有浏览器抢占、运行申请、联网提交、生成DOCX/PDF或改其他代理正文。此为生成过程中的快照，不能替代总控最终重建、逐页文档/浏览器及完整链接复验。

## 结论

**隐私隔离设计与现有public-safe扫描通过；四岗评分公式一致。最终交付尚有可修的集成/命名/manifest状态、一处时长措辞风险及一项公开来源缓存差异。** 不以此快照宣称所有验收已通过。

- public-safe现有5个HTML、39个相对链接：缺文件0、越界路径0、缺anchor0、symlink0。public-safe及scripts共10个文本文件扫描候选姓名/邮箱/个人主页handle/本地绝对路径/特定私有模型与合作者词，无命中。此为明确范围的字符串检查，不声称能证明任意敏感语义不存在。
- build.py的public-safe分支只读取public-safe/example_data.json；示例机构/分数均虚构，无真实Resume、联系、移民、伴侣或邮箱史。CSS/HTML无外部字体、脚本、追踪或资源载入。真实Markdown转HTML留在private旁边，未靠隐藏UI隔离。
- serve.py绑定127.0.0.1，服务根只选private或public-safe，禁止目录索引，默认禁脚本/表单并no-store；没有服务整个项目根。当前两产物没有symlink。若未来添加symlink，SimpleHTTPRequestHandler本身可能跟随它，发布/预览前应继续检查。
- .gitignore排除private、screenshots、logs、原CV/Resume、文档与凭据。它不能撤销已在Git历史里的文件；README须明确，当前未发现Git初始化/remote配置产物，未执行Git写操作。
- 原DOCX/PDF本次重算SHA256分别匹配用户给定值，186929/416858字节，源文件保持原样。详情见independent_qa_source_integrity.json。

## 必须在最终验收前处理/确认

| 优先 | 发现 | 具体修复建议 |
|---|---|---|
| P1集成 | private当前30个HTML的60个缺链，全部为shared/all_questions.html和shared/cross_role_comparison.html | 完成同名MD并重新build private，或统一导航到实际de_duplicated_questions；最终再扫描全部HTML。此快照不判断尚在写的文件为永久缺失 |
| P1交付 | Cambridge快照未有11_visa_route_analysis.md和manifest；其他三岗有 | 齐稿后逐岗确认11号签证与manifest，补format状态、实际生成文件、hash/bytes、来源、外联未执行字段；root统一manifest应覆盖网页/截图/源码 |
| P1文件名 | Apple现有编号稿03_tailored_resume.txt不带姓名/职位/日期；另有命名TXT却不以03开头，renderer只选03*.txt | 将可渲染源统一为03_...Zhanhong_He_Apple_..._20261021_v1.txt，保持下载/manifest同步；不要导出后仍留无日期DOCX/PDF为主文件 |
| P1事实措辞 | ElevenLabs Resume写“during a three-month visit”，Great Bay准确结束/实际完成时长未确认 | 改为appointment/visit began March2026、计划时长仅作为appointment信息，或不写实际三月历时；用户确认后再精确化 |
| P2来源新旧差异 | 本QA早期web搜索缓存（标Crawled 2 months ago）描述SFProxy仅README；总控当日open同URL已见3 commits与模型/scripts/tests目录 | **优先总控当前直接读取；撤回当前代码未公开的确定断言。** 可保守标Project repository；代码存在与已复现/质量审计仍区分。具体审计方法与缓存差异见source_conflict_sfproxy.json |
| P2隐私日志 | render_resumes.py打印folder.name与dest.name，文件名含候选姓名 | 改只打印role id和成功计数，避免姓名进入构建日志；私人文件本身可含姓名 |
| P2可重建隐私 | public-safe构建未清理旧目录或限制已有文件白名单 | 构建前清洁仅generated输出或做严格白名单/敏感文件阻断，防未来删除UI但旧敏感文件残留；当前目录扫描无残留 |
| P2完整性 | 部分manifest在生成DOCX/HTML前写入，hash/状态可能过期；summary downloads也可能仍显示pending | 最后统一按真实文件重算、填文档页数/渲染状态/截图路径/来源完整性，并再检查下载实际内容 |

## 评分独立重算

| 岗位 | 已知加权和 | 已知权重 | 计算暂定分 | summary展示 | 结论 |
|---|---:|---:|---:|---:|---|
| Cambridge |57.5|70%|82.142857|82.1|一致；非A，覆盖不足且核心条件未解 |
| Spotify |46.8|60%|78|78.0|一致；C核心条件待核，有B潜力 |
| ElevenLabs |47.8|60%|79.666667|79.67|一致；B有重大未知 |
| Apple |45.2|60%|75.333333|75.33|一致；B有重大未知 |

地点生活/薪资未知未填0或中点；面试竞争力按定性、数值null。Cambridge给已公布条款支持薪资发展分，另外三岗不因工业品牌补分。暂定分仅用于已知维度，不能横向机械排名；行动顺序遵用户Cambridge→Spotify→ElevenLabs→Apple。

## 用户15项覆盖抽查

| 用户任务 | 对应文件/检查结果 |
|---|---|
|1 独立评分与首轮差异|各岗01与summary；四岗计算通过 |
|2 逐条必需/优先/职责|各岗02 CSV+易读MD；行数Cam39、Spotify23、Eleven11、Apple27。行数不是质量分；OR/理想要求均需保持语义 |
|3 原CV页段证据及未知|矩阵有PDF页/DOCX段号和限制；CV重复未当独立事实验证 |
|4 四类缺口|各岗01/04/09区分能力、资料、表达和可补；没有用新demo冒充旧工程成果 |
|5 定性面试竞争力/风险|各岗01及07；无精确成功率 |
|6 申请判断和否决|各岗01/09；PhD/CoS等条件不被高分抵消 |
|7 保留/删减/前移/改写/量化|各岗04均存在，重点为去已获PhD暗示、题录冲突、实习期限和工程夸大 |
|8 英文定制Resume|四岗可读TXT已存在；未见姓名后PhD、旧Dec2026、London-based或TTS/部署/分布式熟练虚构；上述Eleven措辞须复核 |
|9 新命名DOCX/PDF/渲染|统一生成仍进行中；Apple编号命名须修；未对未生成/未视觉页宣称通过 |
|10 Cover Letter|四岗05存在；英文，最新博士状态，未写伴侣信息 |
|11 短联系稿|四岗06存在；本地DO_NOT_SEND，未猜邮箱或以公告作者作内推 |
|12 10面试问答|四岗07存在；结构、真实证据和不能声称部分均有 |
|13 薪资福利合同成长|四岗08存在；未公开薪资保持未知，未编税后；Cambridge有官方条款 |
|14 方向过窄与机器人迁移|各岗08/01明确ROS2/控制/仿真/平台等补足，Arduino原型不等于机器人研究 |
|15 最终优先级/行动/问题|各岗09/10及共享问题表；到实际提交前停止；总控跨岗比较/统一问题导航待集成 |

Cambridge已取得完整官方Further Information并额外准备proposal/工作样本清单，旧包“缺完整JD”应被更新；其他来源的403/登录限制记录与正常公开浏览器读取不混为绕过。公开页面仍有Apply/Submit入口只证明观察状态，不保证名额。

## 本QA已完成的Spotify修正

读取共研sponsor_register_verified_extract.json：官方2026-10-20 register，2026-10-21读取，Spotify Limited / London / Worker(A rating) / Skilled Worker。已同步Spotify10、11、summary和manifest，具名法人license不再记全面未知；**实际雇佣法人匹配和本岗位CoS意愿仍未知**，未加技能分。共研原CSV来源及hash保留，未谎称本子任务另做一次在线下载。

机器可读快照：independent_qa_snapshot.json；source哈希核对：independent_qa_source_integrity.json。总控修复/最终重建后应重跑本地链接和公开静态扫描，再执行桌面/手机及文档逐页视觉QA。

补充校正：SFProxy旧缓存与当前目录之差不能作为代码不存在的依据；本QA未运行代码，不评价个人代码ownership或质量。总控已收到上述时长/命名/导航问题，正在修复；本报告保留最初快照以供追踪。
