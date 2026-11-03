# R&D-Agent-Quant：面向数据的因子与模型联合优化多智能体框架（R&D-Agent-Quant: A Multi-Agent Framework for Data-Centric Factors and Model Joint Optimization）

> 来源：https://arxiv.org/abs/2505.15155
> 原文：未下载（仅摘要级引用）
> 翻译日期：2026-11-03 ｜ 范围：摘要级 ｜ 方式：机器翻译初稿，未经人工校对
> 引用于：docs/brief-plan.md

## 摘要

金融市场高维、非平稳且持续波动，给资产收益预测带来了根本性挑战。尽管大语言模型与多智能体系统不断进步，当前的量化研究流程仍存在自动化程度有限、可解释性弱，以及因子挖掘与模型创新等关键环节彼此割裂的问题。本文提出面向量化金融的 R&D-Agent，简称 RD-Agent(Q)：这是首个以数据为中心的多智能体框架，通过协同的因子—模型联合优化，把量化策略的全栈研发自动化。

RD-Agent(Q) 将量化过程拆成两个迭代阶段。Research 阶段动态生成与目标对齐的 prompt，依据领域先验提出假设，并把假设落实为具体任务；Development 阶段由代码生成智能体 Co-STEER 编写任务代码，随后在真实市场回测中执行。两个阶段之间由 feedback 阶段衔接：该阶段全面评估实验结果，为下一轮迭代提供依据，而方向选择交给多臂老虎机调度器自适应完成。

实证结果显示，RD-Agent(Q) 只用少七成的因子，就能取得较经典因子库最高两倍的年化收益，并在真实市场上优于当前最好的深度时序模型。其因子与模型的联合优化，在预测精度与策略稳健性之间实现了良好平衡。代码见 https://github.com/microsoft/RD-Agent

## 题录

- **分类**：q-fin.CP（计算金融）；cs.AI（人工智能）；cs.CE（计算工程、金融与科学）；cs.LG（机器学习）
- **Comments**：42 pages, 11 figures, NeurIPS 2025
- **作者**：Yuante Li, Xu Yang, Xiao Yang, Minrui Xu, Xisen Wang, Weiqing Liu, Jiang Bian
- **提交**：2025-05-21（v1），最后修订 2025-09-25（v2）
