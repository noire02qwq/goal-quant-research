# MultiAgentBench：评估 LLM 智能体的协作与竞争（MultiAgentBench: Evaluating the Collaboration and Competition of LLM agents）

> 来源：https://arxiv.org/abs/2503.01935
> 原文：未下载（仅摘要级引用）
> 翻译日期：2026-11-03 ｜ 范围：摘要级 ｜ 方式：机器翻译初稿，未经人工校对
> 引用于：docs/brief-plan.md、docs/decisions/0001-multi-agent-group-research-increment.md

## 题录

- **英文原题**：MultiAgentBench: Evaluating the Collaboration and Competition of LLM agents
- **作者**：Kunlun Zhu, Hongyi Du, Zhaochen Hong, Xiaocheng Yang, Shuyi Guo, Zhe Wang, Zhenhailong Wang, Cheng Qian, Xiangru Tang, Heng Ji, Jiaxuan You
- **arXiv**：arXiv:2503.01935 ［Submitted on 3 Mar 2025］

## 摘要（中文译文）

大语言模型（LLM）作为自主智能体已展现出出色能力，但现有基准或聚焦单智能体任务，或局限于狭窄领域，无法刻画多智能体协调与竞争的动态。本文提出 MultiAgentBench，一个面向多样交互场景、评估基于 LLM 的多智能体系统的综合基准。

该框架不仅度量任务完成情况，还用基于里程碑的新型关键绩效指标（KPI）衡量协作与竞争的质量。我们还评估了多种协调协议（包括星型、链式、树状与图状拓扑），以及群体讨论、认知规划等创新策略。值得注意的是，gpt-4o-mini 取得平均最高任务分；在研究场景中，图状结构在各类协调协议里表现最好；认知规划使里程碑达成率提升 3%。代码与数据集见 https://github.com/MultiagentBench/MARBLE 。

以上为摘要级译文；原文正文未下载、未翻译。

## 原文分类与 comments

- **分类（arXiv subjects）**：Multiagent Systems (cs.MA); Artificial Intelligence (cs.AI); Computation and Language (cs.CL); Computers and Society (cs.CY)
- **comments**：https://github.com/MultiagentBench/MARBLE
