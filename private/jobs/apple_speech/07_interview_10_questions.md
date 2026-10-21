# 最可能的10个面试问题与回答框架

问题是针对JD推测，不是内部题库；分析中文，英文问题便于练习。所有回答先说自己实际做过什么，再提出迁移或计划。

## 1. How would you translate your music-expression research into controllable speech generation?

回答结构：先说明音乐任务的输入/输出和条件机制，再比较prosody、emotion、speaker与pacing；提出可控性/可懂度/身份保持/感知质量四类验证，讲一个条件冲突失败情景。

可用真实证据：D P028–P038，PDF pp1–2，尤其score-informed Transformer和动态CRNN。

不能声称：不能称MIDI velocity就是prosody，不能称做过TTS或speaker控制。

## 2. Explain a Transformer or VAE you actually implemented, including its objective and failure modes.

回答结构：选真正本人写过的一个模型；画数据流、mask/condition、loss与训练推理差异；讲失败样本与ablation。对VAE解释ELBO/KL及posterior collapse时只用已知范围。

可用真实证据：D P032/P049，PDF p2。

不能声称：不把所有架构当独立完整ownership；不声称Flow Matching/Diffusion实作。

## 3. How do conditioning, alignment and guided inference differ?

回答结构：区分训练条件、时序/模态对齐、推理期控制；以音乐score信息为真实起点，再提出语音时长/文本与audio token对齐验证。说明采样引导与后训练不是同一机制。

可用真实证据：D P031–P032、P041–P042，PDF p2。

不能声称：不能把DPO/GRPO说成做过classifier-free guidance；新方案标proposal。

## 4. Walk us through your PyTorch code and how you verified it.

回答结构：先讲Bark-scale特征输入输出、tensor形状、边界与数值；给实际参考/检查；如果可展示代码再指出模块边界与可重复步骤。

可用真实证据：D P035及P009，PDF p2/p1。

不能声称：未实际做过的unit tests、gradcheck、CI、分布式或部署不说已完成；可以说明下一步会怎样补。

## 5. How would you evaluate expressive speech without sacrificing intelligibility or speaker identity?

回答结构：从真实听测设计讲目标、对照、随机化、尺度和分析；再把speech评价设计作研究计划：控制准确性、内容可懂度、speaker similarity及多口音/人群。

可用真实证据：D P038/P050和P042，PDF p2。

不能声称：未确认人数、统计显著性、伦理流程不能编；专业听者不等于accessibility样本。

## 6. Compare DPO and GRPO, and explain how you would detect reward hacking.

回答结构：用可披露范围说明目标、偏好对或group rollout、reference/优势估计与数据质量；讲reward和人类偏好分歧检查，区分实际完成与拟做ablation。

可用真实证据：D P041–P042，PDF p2。

不能声称：不泄露模型名规模/内部数据，不补训练GPU和效果数值；不把音乐结果说成已适用于语音。

## 7. A model is too slow or too large for a device. What would you measure and change first?

回答结构：先测端到端latency、first audio、RTF、peak memory、KV/cache与数据搬运，再考虑streaming/chunk、算子/precision或quantization，并评质量/控制退化。把这是思路讲清。

可用真实证据：目前无edge部署直接证据；D P060只能支持C音乐界面背景；Apple官方July2026文章可作背景阅读。

不能声称：不可称部署过AMX、量化、实时TTS或使用Apple内部工具；不把官方paper指标当自己成果。

## 8. Derive the learning objective and explain how you would test a modelling assumption.

回答结构：从本人熟悉项目选loss；讲梯度、概率假设、normalization、train/val/test和控制变量；选择一个失败假设设置ablation及不确定性。

可用真实证据：D P032/P034/P035、教育P014–P018，PDF p2/p1。

不能声称：不编课程成绩、统计检验或“严格推导已证明”；不把CV教育当逐科能力证书。

## 9. Tell us about a research result that changed your plan or a collaboration under shifting priorities.

回答结构：STAR结构：真实目标/变更、自己负责、与合作者/听者沟通、取舍与结果；清楚区分个人与团队，不夸管理范围。

可用真实证据：Dolby听测D P048–P050、UWA教学/共同指导P045–P047、跨机构P040–P044，PDF p2。

不能声称：目前没有具体事件细节；只能备选证据，不能编故事/人数/冲突。

## 10. How would you turn a research prototype into a maintainable training and inference library?

回答结构：给最小API与模块边界；configuration/data provenance/checkpoint/repro、正确性与回归、benchmark、错误处理；再列自己确实做过的部分与需补部分。

可用真实证据：D P041/P049可支持原型；clean scalable库尚未证明。

不能声称：不能称有production shipped、CI/MLOps、服务SLA或大规模训练；新增练习必须标时间和范围。
