# AlphaAgent：以正则化探索对抗 alpha 衰减的 LLM 驱动 Alpha 挖掘（AlphaAgent: LLM-Driven Alpha Mining with Regularized Exploration to Counteract Alpha Decay）

> 来源：https://arxiv.org/abs/2502.16789 （KDD 2025，DOI 10.1145/3711896.3736838）
> 原文：未下载（仅摘要级引用）
> 翻译日期：2026-11-03 ｜ 范围：摘要级 ｜ 方式：机器翻译初稿，未经人工校对
> 引用于：docs/brief-plan.md

## 摘要

Alpha 挖掘是量化投资的关键环节，目标是在日益复杂的金融市场中发现对未来资产收益具有预测力的信号。然而 alpha decay（因子预测力随时间衰减）这一普遍问题给 alpha 挖掘带来了重大挑战：传统方法如遗传编程（genetic programming）会因过拟合与复杂度而快速衰减；LLM 驱动的方法虽然前景可观，却往往过度依赖既有知识，产出同质化的因子，反而加剧信号拥挤并加速衰减。

为应对这一挑战，我们提出 AlphaAgent：一个把 LLM 智能体与针对性正则化（ad hoc regularization）结合起来的自主框架，用于挖掘抗衰减的 alpha 因子。它采用三个关键机制：（i）通过基于抽象语法树（AST）与既有 alpha 的相似度度量来强制原创性；（ii）由 LLM 评估市场假设与所生成因子之间的语义一致性，实现假设与因子的对齐；（iii）通过基于 AST 的结构约束控制复杂度，防止容易过拟合的过度工程化构造。三者共同引导 alpha 生成过程在原创性、金融逻辑与对市场变化的适应性之间取得平衡，从而降低 alpha 衰减的风险。

大量评估表明，在牛熊市中 AlphaAgent 抑制 alpha 衰减的效果都优于传统方法与 LLM 方法：过去四年里，它在中国 CSI 500 与美国 S&P 500 市场上持续提供显著的 alpha。值得注意的是，AlphaAgent 展现出对 alpha 衰减的显著抵抗力，提升了产出强力因子的潜力。代码见 https://github.com/RndmVariableQ/AlphaAgent

## 题录

- **分类**：cs.CE（计算工程、金融与科学）；cs.AI（人工智能）
- **Comments**：9 pages；Code is available at https://github.com/RndmVariableQ/AlphaAgent
- **作者**：Ziyi Tang, Zechuan Chen, Jiarui Yang, Jiayao Mai, Yongsen Zheng, Keze Wang, Jinrui Chen, Liang Lin
- **提交**：2025-02-24（v1），最后修订 2025-06-09（v2）
- **会议**：KDD '25（多伦多，2025-08-03 至 08-07），页 2813–2822
