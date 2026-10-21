# Apple定制Resume改动说明

新稿为私有本地英文草稿；源DOCX/PDF保留。TXT完整可读；DOCX/PDF由主代理生成并单独验收，未生成前不得把TXT说成已做版式验收。

| 动作 | 项目与证据 | 原因/边界 |
|---|---|---|
| 改写 | 姓名后删PhD与Dec2026；D P001/P014，用户最新确认 | 用Audio and Music ML Researcher；教育写doctoral studies、答辩完成、证书预计Nov2026，不称正式授予。 |
| 前移/保留 | Huawei后训练D P040–P042；Dolby生成与听测P048–P050 | 直接呼应generative research、偏好与perceptual control；Huawei写appointment beganJun2026，不算完成六个月。 |
| 降敏 | Huawei模型名、规模和内部任务细节 | 只留DPO/GRPO、奖励、rollout与偏好数据概要；所有细节仍须本人核保密边界。 |
| 保留/改写 | UWA动态、Transformer、Bark PyTorch、跨乐器D P028–P038 | 从项目任务写出输入/建模/评价，不声称已做TTS/prosody/speaker控制。 |
| 独立核实 | ICASSP2026 P033–P035与UWA机构库 | 仅这条本子任务明确核实Published2026及DOI；用He,Z.避免擅改机构库作者显示名。公开摘要模型规模不直接归个人结果。 |
| 保守重排 | SMC2026与CMMR2025项目 | SMC提交/发表状态存在其他源冲突，列research project；CMMR也只列项目标题与活动，不在本短稿写未独立核验的会议信息。最终提交前确认citation。 |
| 删除 | 四条ICASSP2027 under review P022–P025 | 两页行业稿聚焦最相关已能解释的工作；不得转成accepted。Speech extraction贡献/姓名待确认，避免借合著冒充TTS。 |
| 删除 | CASM/PawChorale LBD P026–P027 | 同副标题冲突待核，不静默修正、不计两项确定成果。 |
| 删减 | GDUT BEng P019–P020、Top3 P017、referee邮箱P062/P064 | 独立学位/排名语境未确认；不在短稿写可能两个已获本科；申请时如需完整教育历史再如实补。 |
| 删减 | Java/HTML/基本C++、硬件、音乐课程、2019英语教学 | 非此岗核心，避免噪声及暗示系统/edge水平；内部档案保留。 |
| 待补 | 用户可检查代码、training/inference库、环境、测试、规模 | 只有真实有据才添加；不补NumPy、DDP、CI/MLOps、生产部署、TTS/vocoder或quantization关键词。 |

## 待补量化表（不在Resume里放占位数值）

| 工作 | 可以补充的真实量化 | 所需验证 |
|---|---|---|
| PyTorch研究项目 | 数据集/切分、objective metric、baseline/ablation、推理时间/内存 | 本人实际测量、代码与配置；区分论文整体与个人贡献 |
| 专业听测 | 人数、样本数、随机化、评价尺度、统计方法/置信区间 | 实际protocol和本人职责；不捏显著性 |
| 后训练 | 非保密数据规模、偏好一致性、reward检查、对比结果 | 公司允许披露且有证据；未获许可维持概要 |
| 研究软件 | 可复现步骤、测试范围、API/调用者、本人ownership | 实际repo/commit与能公开的片段 |

投递前用户核准所有日期、职称、可披露范围、英文动机和教育状态。不能把本次新增demo当作已有训练/推理研究软件成果。
