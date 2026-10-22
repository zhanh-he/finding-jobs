# Tencent R107821 十道面试题与回答结构

没有生成虚构个人故事；以下结构由用户填入真实决定和结果。

## 1. Why this speech role with a music background?

回答结构：用JD含music生成开头→DPO/奖励/听测共同问题→明确speech-specific gap→举一个可迁移决定。

真实证据：D P041–042/P049–050；ICASSP音频研究

不能声称：不能称做过TTS、full-duplex或生产语音服务。

## 2. Explain DPO versus GRPO in your actual work.

回答结构：定义目标/数据→本人模块→为何用偏好或组内奖励→失败/验证→可披露边界；无数值不补。

真实证据：D P041–042，用户允许概括经验

不能声称：不透露内部模型规模、专有任务/数据或把计划说完成。

## 3. How would you extend an LLM to audio?

回答结构：区分已做music post-training与假设设计→公开codec/tokenizer选择→序列长度/对齐→adapter或joint training→验证协议。

真实证据：D P006/P041与公开知识；设计是提案

不能声称：不把设计说成过去已部署；未证speech tokenizer实现。

## 4. How would you evaluate expressive synthesis?

回答结构：质量/可懂度/可控性/说话人一致性/延迟分开→客观指标限制→盲听设计和统计→reward hacking检查。

真实证据：D P038/P050专业听测与P042偏好数据

不能声称：不编MOS人数、置信区间或已获得的改善率。

## 5. Compare diffusion, flow, autoregressive and codec approaches.

回答结构：清晰区分建模/表示/采样；quality-latency-conditioning取舍→只以VAE/Transformer实际经验举例→未实作项说明。

真实证据：D P049/P041

不能声称：不写全部四范式hands-on或把codec与生成目标混为同一层。

## 6. How would you build streaming/full-duplex interaction?

回答结构：先确认时延预算/因果性→分块状态、turn-taking/打断→同步/回声→测试/回退；明确学习设计而非履历。

真实证据：D P033序列任务仅相邻；无直接speech系统

不能声称：不把音乐长序列等同实时口语交互。

## 7. Describe a PyTorch implementation you owned.

回答结构：从Bark-specific loudness输入输出/梯度/shape→验证对照→多任务loss→错误诊断；只讲本人熟悉模块。

真实证据：D P033–035与公开研究repo

不能声称：不给未知代码行/GPU/速度数据。

## 8. How would you move a research model online?

回答结构：离线baseline→profiling→延迟吞吐预算→数据/版本/回归→监测回滚；与已经完成研究实现分开。

真实证据：D P049；生产部署未证明

不能声称：不能宣称上线规模、CI/MLOps或分布式运维经验。

## 9. What was your individual contribution to your publications?

回答结构：选ICASSP和Beyond Piano两项→problem/本人模块/合作者边界→结果证据来源→局限和下一实验。

真实证据：D P028–035；当日UWA/arXiv原始记录

不能声称：不把共著同伴工作、in-review论文或完整abstract指标都当本人独立成果。

## 10. How do you handle ambiguous work and cross-team disagreements?

回答结构：选Dolby听测或UWA合作实例→分歧→可检验假设→沟通/责任→真实结果；最后说明希望在team职责范围成长。

真实证据：D P038/P045–050

不能声称：不虚构带团队人数/管理职责；回答资格/签证准确不预设有工作权。
