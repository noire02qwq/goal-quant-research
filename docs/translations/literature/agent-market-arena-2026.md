# 当智能体开始交易：面向 LLM 智能体的实时多市场交易基准（When Agents Trade: Live Multi-Market Trading Benchmark for LLM Agents）

> 来源：https://arxiv.org/abs/2510.11695 （Agent Market Arena / AMA，WWW 2026）
> 原文：未下载（仅摘要级引用）
> 翻译日期：2026-11-03 ｜ 范围：摘要级 ｜ 方式：机器翻译初稿，未经人工校对
> 引用于：docs/brief-plan.md

## 摘要

尽管基于大语言模型的智能体正被越来越多地用于金融交易，它们能否在实盘市场中推理并作出适应仍然不清楚——多数研究测的是模型而不是智能体，覆盖的时间与资产有限，而且依赖未经核实的数据。为填补这些空白，我们提出 Agent Market Arena（AMA）：首个用于跨多个市场评估 LLM 交易智能体的终身（lifelong）、实时基准。AMA 在统一的交易框架中整合经过核实的交易数据、专家审校的新闻与多样的智能体架构，从而在真实条件下进行公平且持续的比较。

它实现了四个智能体：InvestorAgent 作为单智能体基线，TradeAgent 与 HedgeFundAgent 具有不同的风险风格，DeepFundAgent 则基于记忆进行推理；并在这四个智能体上评估了 GPT-4o、GPT-4.1、Claude-3.5-haiku、Claude-sonnet-4 与 Gemini-2.0-flash。加密货币与股票市场上的实盘实验表明，智能体框架呈现出显著不同的行为模式——从激进的风险承担到保守的决策——而底座模型对结果差异的贡献相对较小。AMA 由此为 LLM 智能体的金融推理与交易智能，建立了一个严谨、可复现且持续演化的评估基础。

## 题录

- **分类**：cs.CL（计算与语言）
- **Comments**：无（原文未填）；已被 WWW 2026（The ACM Web Conference 2026）接收
- **作者**：Lingfei Qian, Xueqing Peng, Yan Wang, Vincent Jim Zhang, Huan He, Hanley Smith, Yi Han, Yueru He, Haohang Li, Yupeng Cao, Yangyang Yu, Alejandro Lopez-Lira, Peng Lu, Jian-Yun Nie, Guojun Xiong, Jimin Huang, Sophia Ananiadou
- **提交**：2025-10-13（v1），最后修订 2025-10-30（v2）
- **配套**：代码 https://github.com/The-FinAI/Agent_Market_Arena
