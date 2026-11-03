# BacktestBench：面向自动化量化策略回测的 LLM 基准（BacktestBench: Benchmarking Large Language Models for Automated Quantitative Strategy Backtesting）

> 来源：https://arxiv.org/abs/2605.17937 （KDD 2026，DOI 10.1145/3770855.3817460）
> 原文：未下载（仅摘要级引用）
> 翻译日期：2026-11-03 ｜ 范围：摘要级 ｜ 方式：机器翻译初稿，未经人工校对
> 引用于：docs/brief-plan.md

## 摘要

量化回测是评估交易策略的关键环节，却一直受制于较高的技术门槛与有限的可扩展性。大语言模型（LLM）通过代码生成、工具使用与智能体规划，为自动化这条复杂的跨学科工作流提供了变革性的路径；但目前缺少专门面向自动化量化回测的大规模基准，使这一设想在实践中面临显著挑战，也拖住了该领域的进展。为填补这一关键空白，我们提出 BacktestBench——首个面向自动化量化回测的大规模基准。

BacktestBench 基于 600 多万条真实市场记录构建，包含 18,246 个精心标注的问答对，覆盖四类任务：指标计算、股票代码选择、策略选择与参数确认。我们同时提出 AutoBacktest，一个稳健的多智能体基线：它协调 Summarizer（负责语义因子抽取）、Retriever（负责生成经过验证的 SQL）与 Coder（负责 Python 回测实现），把自然语言描述的策略转化为可复现的回测。

我们对 23 个主流 LLM 做了评估，并辅以针对性的消融实验，识别出影响端到端表现的关键因素，凸显了 grounded verification（有依据的验证）与标准化指标表示的重要性。

## 题录

- **分类**：cs.CL（计算与语言）；cs.AI（人工智能）
- **Comments**：This paper has been accepted by KDD 2026 (Datasets and Benchmarks Track)
- **作者**：Zhensheng Wang, Wenmian Yang, Qingtai Wu, Lequan Ma, Yiquan Zhang, Weijia Jia
- **提交**：2026-05-18（v1），最后修订 2026-05-25（v2）
