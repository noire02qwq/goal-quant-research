# AlphaEvolve：用于科学与算法发现的编码智能体（AlphaEvolve: A coding agent for scientific and algorithmic discovery）

> 来源：https://arxiv.org/abs/2506.13131
> 原文：未下载（仅摘要级引用）
> 翻译日期：2026-11-03 ｜ 范围：摘要级 ｜ 方式：机器翻译初稿，未经人工校对
> 引用于：docs/brief-plan.md

## 摘要

本白皮书介绍 AlphaEvolve，一个进化式编码智能体，能在攻克开放科学问题、优化关键计算基础设施组件等高难任务上，大幅增强最先进 LLM 的能力。AlphaEvolve 编排了一条由 LLM 组成的自主流水线，其任务是通过直接修改代码来改进算法。它采用进化方法，持续从一个或多个评估器接收反馈，迭代地改进算法，进而可能带来新的科学与实践发现。我们把它应用于若干重要的计算问题，以展示这一方法的广泛适用性。

当用于优化 Google 大规模计算栈的关键组件时，AlphaEvolve 为数据中心开发出更高效的调度算法，在硬件加速器的电路设计中找到一个功能等价的简化方案，并加快了支撑 AlphaEvolve 自身的 LLM 的训练。此外，AlphaEvolve 发现了一批新颖且可证明正确的算法，在数学与计算机科学的一系列问题上超越已有最优解，显著扩展了此前自动化发现方法（Romera-Paredes et al., 2023）的适用范围。

值得注意的是，AlphaEvolve 开发的搜索算法找到了一个用 48 次标量乘法完成两个 4×4 复矩阵相乘的方法——这是 56 年来首次在该场景下改进 Strassen 算法。我们相信，AlphaEvolve 及同类编码智能体，能在改进众多科学与计算领域的问题解法上产生重要影响。

## 题录

- **分类**：cs.AI（人工智能）；cs.LG（机器学习）；cs.NE（神经与进化计算）
- **Comments**：无（原文未填）
- **作者**：Alexander Novikov, Ngân Vũ, Marvin Eisenberger, Emilien Dupont, Po-Sen Huang, Adam Zsolt Wagner, Sergey Shirobokov, Borislav Kozlovskii, Francisco J. R. Ruiz, Abbas Mehrabian, M. Pawan Kumar, Abigail See, Swarat Chaudhuri, George Holland, Alex Davies, Sebastian Nowozin, Pushmeet Kohli, Matej Balog
- **提交**：2025-06-16（v1）
