# ChatDev：面向软件开发的交流型智能体（ChatDev: Communicative Agents for Software Development）

> 来源：https://arxiv.org/abs/2307.07924
> 原文：未下载（仅摘要级引用）
> 翻译日期：2026-11-03 ｜ 范围：摘要级 ｜ 方式：机器翻译初稿，未经人工校对
> 引用于：docs/brief-plan.md、docs/decisions/0001-multi-agent-group-research-increment.md

## 题录

- **英文原题**：ChatDev: Communicative Agents for Software Development
- **作者**：Chen Qian, Wei Liu, Hongzhang Liu, Nuo Chen, Yufan Dang, Jiahao Li, Cheng Yang, Weize Chen, Yusheng Su, Xin Cong, Juyuan Xu, Dahai Li, Zhiyuan Liu, Maosong Sun
- **arXiv**：arXiv:2307.07924 ［Submitted on 16 Jul 2023 (v1), last revised 5 Jun 2024 (this version, v5)］

## 摘要（中文译文）

软件开发是一项复杂的任务，需要多名技能各异的成员通力合作。已有大量研究用深度学习改进瀑布模型中的特定阶段，例如设计、编码与测试。然而，每个阶段的深度学习模型都需要各自独立的设计，导致各阶段之间出现技术上的割裂，最终使开发过程零散而低效。

本文提出 ChatDev，一个由对话驱动的软件开发框架：由大语言模型（LLM）驱动的专职智能体，在「说什么」（通过 chat chain，即对话链）与「怎么说」（通过 communicative dehallucination，即交流去幻觉）两个层面接受引导。这些智能体通过统一的、基于语言的交流共同参与设计、编码与测试阶段，解决方案来自它们之间的多轮对话。我们发现，用自然语言交流有利于系统设计，而用编程语言交流则有助于调试。

这一范式展示了语言交流如何促进多智能体协作，把语言确立为 LLM 智能体之间自主完成任务的统一桥梁。代码与数据见 https://github.com/OpenBMB/ChatDev 。

以上为摘要级译文；原文正文未下载、未翻译。

## 原文分类与 comments

- **分类（arXiv subjects）**：Software Engineering (cs.SE); Computation and Language (cs.CL); Multiagent Systems (cs.MA)
- **comments**：Accepted to ACL 2024; https://github.com/OpenBMB/ChatDev
