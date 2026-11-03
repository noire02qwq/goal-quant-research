# 通过假设树精化走向通用自主研究（Toward Generalist Autonomous Research via Hypothesis-Tree Refinement）

> 来源：https://arxiv.org/abs/2606.11926
> 原文：未下载（仅摘要级引用）
> 翻译日期：2026-11-03 ｜ 范围：摘要级 ｜ 方式：机器翻译初稿，未经人工校对
> 引用于：docs/brief-plan.md

## 摘要

科学进步依赖探索、实验与抽象的反复循环。研究者检验候选方向、解读证据，并把从中得到的经验带入后续尝试。我们研究 AI 智能体如何在长时程上自主跑完这个循环。为此我们提出 Arbor，一个通用的自主研究框架：它结合了一个长寿命的协调者（coordinator）、若干短寿命的执行者（executor），以及 Hypothesis Tree Refinement（HTR）——一棵持久的树，把假设、产物、证据与提炼出的洞见跨时间连接起来。协调者在树上管理全局研究策略，执行者则在隔离的 worktree 中实现并检验单个假设。

随着结果返回，Arbor 更新这棵树、传播可复用的教训、精化搜索前沿，并接纳经过验证的改进。这一设计把自主研究从一连串局部尝试转变为一个累积过程：策略、执行与证据都得以跨时间延续。

我们在 Autonomous Optimization（AO）这一运行设定下评估 Arbor：智能体在没有逐步人工监督的情况下，通过迭代实验改进一个初始研究产物。在覆盖模型训练、harness 工程与数据合成的六项真实研究任务中，Arbor 在全部六项上都取得最好的留出（held-out）结果，其平均相对留出增益超过 Codex 与 Claude Code 在相同任务接口与资源预算下的 2.5 倍。在 MLE-Bench Lite 上，Arbor 配合 GPT-5.5 达到 86.36% Any Medal，是我们对比中的最强结果。

## 题录

- **分类**：cs.CL（计算与语言）；cs.AI（人工智能）
- **Comments**：无（原文未填）
- **作者**：Jiajie Jin, Yuyang Hu, Kai Qiu, Qi Dai, Chong Luo, Guanting Dong, Xiaoxi Li, Tong Zhao, Xiaolong Ma, Gongrui Zhang, Zhirong Wu, Bei Liu, Zhengyuan Yang, Linjie Li, Lijuan Wang, Hongjin Qian, Yutao Zhu, Zhicheng Dou
- **提交**：2026-06-10（v1）
