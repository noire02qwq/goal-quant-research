# 学习谁与谁通信：面向高效 LLM 多智能体协作的角色感知通信拓扑调度（Learning Who Talks to Whom: Role-Aware Communication Topology Scheduling for Efficient LLM Multi-Agent Collaboration）

> 来源：https://arxiv.org/abs/2610.25851
> 原文：未下载（仅摘要级引用）
> 翻译日期：2026-11-03 ｜ 范围：摘要级 ｜ 方式：机器翻译初稿，未经人工校对
> 引用于：docs/brief-plan.md；docs/decisions/0001-multi-agent-group-research-increment.md

## 摘要

由大语言模型驱动的多智能体系统依赖结构化的通信拓扑来完成信息交换与协同推理。然而，如何有效调度这些拓扑——动态决定谁与谁说话、何时通信——仍然是一个根本性挑战：它要求在集体推理性能与指数级 token 开销之间取得平衡。

现有的拓扑调度方法要么强加静态通信图、无法适应动态的问题求解状态，要么忽视智能体角色之间的互补性，同时也没能把合成出的图结构显式纳入团队层面的决策评估。为应对这些局限，我们提出 ACTS：一个角色感知的自适应通信拓扑调度框架，用于高效的 LLM 多智能体协作。ACTS 在"集中训练、分散执行"（CTDE）范式下编排，引入了一种新颖的双重注意力机制。

具体而言，Role-conditioned Relational Attention 模块依据智能体角色与不断演化的执行状态，动态选出数量可变的交互伙伴；Topological Attention Mixer 则把有向通信拓扑显式嵌入团队价值分解，以实现精确的功劳分配（credit assignment）。在覆盖代码生成、多步推理、通用知识与竞赛数学的 9 项有挑战性的基准上，全面评估表明 ACTS 一致优于最先进的基线：平均准确率最多提升 6.19 个百分点，同时 token 消耗降低超过 15%。项目网站见 https://acts-mas.github.io/ACTS/

## 题录

- **分类**：cs.MA（多智能体系统）
- **Comments**：Project website: https://acts-mas.github.io/ACTS/
- **作者**：Haibin Li, Wenya Yu, Xuefeng Jiang, Jia Li, Xiao Han, Shuai Su, Wei Wei
- **提交**：2026-10-19（v1）
