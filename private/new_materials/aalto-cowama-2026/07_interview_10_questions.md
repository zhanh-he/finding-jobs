# 10个最可能面试问题与回答结构
问题是研究准备，不是虚构回答。每项必须由本人补充个人贡献与可披露结果。

## 1 Why move from musical dynamics to watermarking?
回答结构：共享生成音频/感知质量/内容保持问题→说明domainlearning计划→一项可测试假设。
可用真实证据：D28–38,48–50
不能声称：不能称现成watermark成果。

## 2 What is a content based watermark and how would you test it?
回答结构：先明确嵌入/检测/内容语义的定义和threatmodel→baseline→heldoutgenerator和quality。
可用真实证据：JD；新discussionnote
不能声称：不声称已经实现COWAMA方法。

## 3 How do you trade robustness against perceptual quality?
回答结构：固定可比变换强度→同时reportfalsepositive、detectability、quality→听测设计。
可用真实证据：D35,38,50
不能声称：不编AUC/MOS结果或现有watermark经验。

## 4 Which attacks belong in a realistic evaluation?
回答结构：压缩/采样率/EQ/时间编辑等是拟议候选；按threatmodel挑选→强度范围→contentretention。
可用真实证据：proposal；differentiableproxy D28–30
不能声称：不能称过去已写攻击库。

## 5 What does loudness supervision teach you about evaluation?
回答结构：解释proxy与rendererdependence→为什么声学指标不等同感知→失败例。
可用真实证据：D28–30,35
不能声称：不把loudness等同所有感知维度。

## 6 How would you avoid false positives and dataset leakage?
回答结构：独立calibrationsplit→固定threshold→未水印真实和生成对照→按内容/模型划分。
可用真实证据：拟议研究设计
不能声称：不能声称已证明泛化或给保证。

## 7 What is your experience with diffusion, neural codecs and HPC?
回答结构：分开已做U-Net/VAE/maskedTransformer vs待学diffusion/codec/HPC；提出baseline复现和环境记录。
可用真实证据：D49；公开repo目录仅说明存在脚本
不能声称：不把U-Net自动算扩散实现，不能编GPU规模。

## 8 How would you organise an open source release?
回答结构：复现环境/版本/许可证/测试/数据清单→不能释放保密材料→最小可运行example。
可用真实证据：公开sfproxyrepo；D28–38
不能声称：repo存在不证明全部质量检查已通过。

## 9 How would you work with the doctoral researcher?
回答结构：共同定义interfaces/evaluation→明确分工→review与实验记录→honours共同指导例。
可用真实证据：D47；工业研究合作D40–50
不能声称：不能称曾独立指导博士。

## 10 What would you deliver in your first ninety days?
回答结构：baseline与threatmodel、数据许可、heldout拆分和评估suite；一项内容aware假设，先与PI校准。
可用真实证据：新discussionnote
不能声称：不承诺已授予博士、已具芬兰许可或未协商到岗。
