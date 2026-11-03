# Strat-LLM：结合实时多源信号的分层策略对齐股票交易框架（Strat-LLM: Stratified Strategy Alignment for LLM-based Stock Trading with Real-time Multi-Source Signals）

> 来源：https://arxiv.org/abs/2605.06024
> 原文：未下载（仅摘要级引用）
> 翻译日期：2026-11-03 ｜ 范围：摘要级 ｜ 方式：机器翻译初稿，未经人工校对
> 引用于：docs/brief-plan.md

## 摘要

大语言模型正演化为自主交易智能体，但现有基准往往忽视了架构推理与策略一致性之间的相互作用。我们提出 Strat-LLM，一个以分层策略对齐（Stratified Strategy Alignment）为基础的框架。它在整个 2025 年运行于实盘前向（live-forward）环境，整合序列价格、实时新闻与年报等异构数据，以消除前视偏差。

在 A 股与美股上的大量压力测试揭示了以下几点：（1）重推理的模型在 Free Mode 下靠内部逻辑达到效用峰值，而标准模型需要 Strict Mode 作为关键的风险锚；（2）对齐效用依市场状态而异——Free 与 Guided 模式在上行市场中捕捉动量，Strict Mode 则在下行趋势中缓解回撤；（3）中等规模模型（35B）在严格约束下保真度最佳，而超大模型（122B）在僵硬规则下要付出"对齐税"，却能在 Guided Mode 中获得性能溢价；（4）标准 LLM 常陷入高胜率陷阱——为小收益优化而牺牲总收益，只有通过深度推理或严格的外部护栏才能缓解。

项目详情见 https://Strat-LLM.github.io

## 题录

- **分类**：cs.AI（人工智能）
- **Comments**：Accepted by the 2026 International Joint Conference on Neural Networks (IJCNN)
- **作者**：Wenliang Huang, Zengyi Yu
- **提交**：2026-05-07（v1）
