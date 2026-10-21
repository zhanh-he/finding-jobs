# 项目贡献填写模板

更新：2026-10-21。每个项目用下面六项，短句即可；不知道的写“暂无”或“尚未评估”。Huawei不作为必填作品，不需要披露内部技术、数据、指标或制作内部demo。毕业/答辩不再反复追问，沿用“已答辩、预计2026年11月获证”，不补写正式已授予。

## 项目候选 A 歌词条件音乐生成的后训练与评估

作品名称：Lyrics2song GRPO / Music Post-Training Lab。

作品入口：[用户提供的成果页](https://zhanh-he.github.io/RL-paper-reading/demos/#lyrics)。

背景已预填：页面展示歌词条件音乐生成的GRPO实验，包含baseline/checkpoint对照、验证与测试协议、A/B音频展示。它是用户自报成果的公开入口；这次没有审计训练代码、重新运行实验、下载音频或检查点，也不据此确定每个组件均由本人完成或任何雇主已批准再次传播。

本轮可见的证据边界：固定验证有分数记录；默认展示的WildSongBench测试仍有局部覆盖，页面将完整目标与当前完成量分开。不能将训练reward、固定验证、独立测试与听感结论混为一谈，不能把计划或队列称为完成。现阶段无需把网页上的数字全部抄进简历。

填写：

```text
1. 问题：这项工作要解决什么？为什么困难？
   [一句话]

2. 我的贡献：我亲自设计、实现、训练或评估了什么？
   [两三项具体动作；并说明已有系统或合作者负责哪部分]

3. 方法：我实际使用且可以对外说明的方法/工具是什么？
   [只填本人做过的；不要根据网页模型列表认领全部实现]

4. 结果：最有说服力的一项结果是什么？
   [有数字：指标 + baseline + 验证/测试集 + 样本覆盖 + 数值]
   [无数字：实际完成的功能、已记录的发现或失败案例]
   [若没有系统评估，写“目前只有演示/局部评估”即可]

5. 证据：哪一个链接最直接支持上述贡献或结果？
   [具体demo章节 / 论文 / 本人代码或实验记录；没有公开代码写“暂无”]

6. 边界：一项局限，以及哪些内容可以写入申请材料？
   局限：[一句话]
   可用于申请：[内容或仅该链接]
   不能写出：[如雇主内部数据、模型细节、指标；无需提供这些内容]
```

## 项目候选 B 表现性音乐动态与结构建模

可选名称：Joint Estimation of Piano Dynamics and Metrical Structure with a Multi-Task Multi-Scale Network。

背景已预填：根据原CV，使用multitask CRNN建模动态、节拍及结构，并在PyTorch重实现Bark-scale specific-loudness特征。ICASSP2026发表记录已在上一轮由学校和会议来源核验；个人贡献和可归属的结果仍用自己的话补齐。

项目代码入口：[piano-dynamic-estimation](https://github.com/zhanh-he/piano-dynamic-estimation)。

也可以换成自己更熟悉的跨乐器SoundFont代理、score-informed Transformer或MIDI velocity U-Net项目；不要求选Huawei经历。

复制并填写上面同样六项：问题、我的贡献、方法、结果、证据、边界。团队论文的参数量或性能不能直接改写为自己个人的优化成果；如尚未确认归属，先用定性描述。

## 英文 Resume 句式

以下方括号是待填写模板，不是可以直接发送的事实。只保留有证据的一两句即可。

个人实现：

```text
Implemented [specific component] for [problem], using [confirmed methods/tools] to [observable capability].
```

有可靠量化结果：

```text
Evaluated [system] against [baseline] on [held-out evaluation and coverage], achieving [verified result] measured by [metric].
```

暂时没有可靠数字：

```text
Developed [prototype/pipeline] for [specific task] and documented [actual comparisons or failure cases], with examples available at [demo link].
```

如果本人只做了其中一部分：

```text
Contributed [specific component] to [team project], with responsibility for [own scope]; [other component] used an existing implementation.
```

仅有演示、尚无系统评估：

```text
Built a prototype demonstrating [specific behavior], with public examples available at [demo link].
```

## 60秒英文面试叙述

```text
The project addressed [problem]. My responsibility was [personal contribution], while [existing-system or collaborator contribution] came from [source]. I implemented [specific work] and evaluated it using [actual procedure]. The evidence currently supports [bounded conclusion]. One limitation is [limitation]; my next experiment would test [future work].
```

## Huawei对外表述原则

不要求用Huawei内部项目填满这份模板。现有四岗v1文件仍是本地待核草稿；其中Huawei技术条目不应被视为已经获得披露许可，也不应直接对外发送。以后整理对外定稿时，默认保留准确任职信息和音乐/音频AI研究的概括方向；技术、数据、模型、奖励、训练规模、指标或demo仅在明确可披露时使用。不能将相关工作重新标为“独立个人项目”以绕开保密边界。

面试可用：

```text
I can discuss my role and the general research approach while keeping proprietary data, model details and internal results confidential. I can use my public research projects to explain my implementation and evaluation work.
```

## 已收到的最新偏好

不再追问答辩/毕业的细枝末节，也不把这些问题放在作品模板的填写前置条件。正式授予未确认时不称已获博士；若雇主日后确实要求学位证明，再处理相应材料。本轮不重算四岗分数、不改英文CV、不新增未经本人确认的量化成果、不更改任何线上页面或公开目录。
