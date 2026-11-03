# Agent Workflow Memory：智能体工作流记忆（Agent Workflow Memory）

> 来源：https://arxiv.org/abs/2409.07429
> 原文：未下载（仅摘要级引用）
> 翻译日期：2026-11-03 ｜ 范围：摘要级 ｜ 方式：机器翻译初稿，未经人工校对
> 引用于：docs/brief-plan.md

## 题录

- **英文原题**：Agent Workflow Memory
- **作者**：Zora Zhiruo Wang, Jiayuan Mao, Daniel Fried, Graham Neubig
- **arXiv**：arXiv:2409.07429 ［Submitted on 11 Sep 2024］

## 摘要（中文译文）

尽管基于语言模型的智能体已有解决网页导航等现实任务的潜力，现有方法在动作轨迹复杂、时间跨度长的任务上仍力不从心。相比之下，人类能灵活应对复杂任务：从过往经验中学习可复用的任务工作流，再用它指导后续行动。为了让智能体也能受益于这一过程，我们提出 Agent Workflow Memory（AWM，智能体工作流记忆）：一种归纳常用例程（即工作流）的方法，并有选择地把工作流提供给智能体，引导其后续生成。

AWM 灵活适用于离线与在线两种场景：离线时，智能体事先从训练样本中归纳工作流；在线时，则从测试查询中即时归纳。我们在两个主流网页导航基准——Mind2Web 与 WebArena——上开展实验，二者合计覆盖 200 多个领域、1000 多个任务，涉及旅行、购物、社交媒体等。AWM 使基线结果大幅提升：在 Mind2Web 与 WebArena 上相对成功率分别提高 24.6% 与 51.1%，同时减少了成功完成 WebArena 任务所需的步数。此外，在线 AWM 在跨任务、跨网站、跨领域的评估中都能稳健泛化；随着训练与测试任务分布的差距扩大，它仍以 8.9 至 14.0 个百分点的绝对优势超过基线。

以上为摘要级译文；原文正文未下载、未翻译。

## 原文分类与 comments

- **分类（arXiv subjects）**：Computation and Language (cs.CL)
- **comments**：无（arXiv abs 页未给出）
