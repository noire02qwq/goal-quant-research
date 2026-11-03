# TradingAgents：基于多智能体 LLM 的金融交易框架（TradingAgents: Multi-Agents LLM Financial Trading Framework）

> 来源：https://arxiv.org/abs/2412.20138
> 原文：未下载（仅摘要级引用）
> 翻译日期：2026-11-03 ｜ 范围：摘要级 ｜ 方式：机器翻译初稿，未经人工校对
> 引用于：docs/brief-plan.md

## 题录

- **英文原题**：TradingAgents: Multi-Agents LLM Financial Trading Framework
- **作者**：Yijia Xiao, Edward Sun, Di Luo, Wei Wang
- **arXiv**：arXiv:2412.20138 ［Submitted on 28 Dec 2024 (v1), last revised 3 Jun 2025 (this version, v7)］

## 摘要（中文译文）

由大语言模型（LLM）驱动的智能体社会在自动问题求解上已取得显著进展。在金融领域，研究大多聚焦于处理特定任务的单智能体系统，或各自独立收集数据的多智能体框架；而多智能体系统复现真实交易公司协作动态的潜力，仍鲜有探索。

TradingAgents 提出一个受交易公司启发的股票交易新框架：由 LLM 驱动的智能体分别担任基本面分析师、情绪分析师、技术分析师，以及风险偏好各异的交易员。框架中还有评估市场状况的多头（Bull）与空头（Bear）研究员智能体、监控敞口的风险管理团队，以及综合辩论与历史数据中的见解、据此做出决策的交易员。通过模拟一个动态、协作的交易环境，该框架旨在提升交易表现。

详细的架构与大量实验显示，它优于基线模型，在累计收益、Sharpe 比率与最大回撤上均有明显改善，凸显了多智能体 LLM 框架在金融交易中的潜力。代码见 https://github.com/TauricResearch/TradingAgents 。

以上为摘要级译文；原文正文未下载、未翻译。

## 原文分类与 comments

- **分类（arXiv subjects）**：Trading and Market Microstructure (q-fin.TR); Artificial Intelligence (cs.AI); Computational Engineering, Finance, and Science (cs.CE); Machine Learning (cs.LG)
- **comments**：Tauric Research @ https://github.com/TauricResearch ｜ Oral @ Multi-Agent AI in the Real World
