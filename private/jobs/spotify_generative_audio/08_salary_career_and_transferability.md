# Spotify：薪资、合同、职业成长与迁移

核查2026-10-21。[官方JD](https://www.lifeatspotify.com/jobs/research-scientist-generative-audio-2)；[官方招聘FAQ](https://www.lifeatspotify.com/start-your-journey/faq)；[London办公室](https://www.lifeatspotify.com/find-your-team/locations/london)。公开条款仅按页面所述；未收到offer。

## 已知与未知

| 项目 | 已知 | 仍要核实 |
|---|---|---|
| 合同 | Permanent，多个资历层级 | 具体级别、试用、notice、IP/发表审批、工时、是否有固定项目资金限制 |
| 工作地 | JD标题London or Stockholm；实际EMEA须公司有work location | 具体英国雇佣实体；London是否本岗位可选；每周出勤/差旅；在家工作协议；不假定澳洲跨境remote |
| 协作 | 欧洲/GMT，JD列CET15–18核心时段 | 夏令时和地区时区表达、必须重叠时段与出差，不能把JD时差写成全年不变UTC |
| 薪资 | 未披露 | GBP base、bonus、股权类型/归属、级别、调薪、UK pension、签证/搬迁费用；用户最低可接受薪资未给 |
| 福利 | JD/FAQ列学习、股权相关激励、家长假和wellbeing等全球项目 | UK具体eligibility、兑现方式、法定/额外假、medical、养老金等须合同/HR，不把全球marketing写成个人确定权利 |
| 移民 | 该JD未承诺岗位CoS或GT文件 | UK sponsor实体、具体岗位是否愿签CoS、SOC/工资/折扣/英语、GT研究或数字科技材料；详见11号分析 |

不提供缺来源的市场薪资估计或税后计算。当前salary_development=null；“工业大厂一定高薪”不是证据。收到实际范围后，按base/股权风险/搬迁及签证自付成本/生活约束分别比较，不能把未归属股权视作现金。

## 成长及伦敦机会：明确属于推断

若实际进入团队并承担可证实的工作，该岗位有望把现有音乐表达研究延伸为通用偏好对齐、reward evaluation、生成模型评价与跨职能产品协作。这些经历可能支持以后London audio/creative AI、生成模型或research engineer岗位；不是保就业/跳槽结果。英国工作许可与雇佣实体是现实前提：SW换雇主通常要新CoS和更新签证；GT较灵活但不能预设已获背书。Permanent在合同上较长期，不代表裁员或研究方向变化风险消失。

## 方向过窄的防范

现有履历容易被读成“只做MIDI力度”或“只会音乐领域微调”。新稿要展示方法层：标签稀缺下监督设计、多任务/跨域泛化、奖励与人类偏好关系、对照与主观评价。保留音乐优势，避免硬换成未做过的通用LLM/语音/生产工程经历。

| 迁移方向 | 可迁移真实基础 | 需补的具体能力/证据 |
|---|---|---|
| 更广AI研究 | 多任务、Transformer/U-Net、后训练、评价；D P028–P050 | 数据/计算规模、严谨消融、通用基准、复现、理论深度和个人ownership |
| 音频/语音 | 音频/DSP、感知评价、生成模型；不是已做TTS | TTS/vocoder/codec、语音数据与对齐、声学评价、扩散/flow目标和采样实现；先做可公开许可数据项目 |
| 一般ML/软件工程 | Python/PyTorch研究实现、公开项目入口 | 测试、版本/依赖、typed API、性能profiling、服务接口、日志、CI、部署/monitoring；没有完成前不写已有 |
| 创意技术/音乐工具 | Ableton/Max/MSP、表达控制、HMM原型、听测 | 交互设计、延迟与鲁棒性、用户任务评估、可维护分发；原型不等于商业产品 |
| 机器人/音乐机器人 | 时间/节拍/表现参数建模；Arduino MIDI theremin只证明物理音乐交互原型（D P060） | 机器人运动学/动力学、反馈/阻抗控制、ROS2、坐标与传感融合、模拟器、执行器/安全约束、实时控制与真实平台集成；HRI另需人机实验、交互与伦理设计 |

短期优先补一个能证明实验可信度与编码质量的音频评估小作品，比同时宣称跨到机器人和规模LLM更有用。机器人是中期转向，需要实物/仿真项目与控制证据；兴趣和Arduino课程不能代替机器人研究。
