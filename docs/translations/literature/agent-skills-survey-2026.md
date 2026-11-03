# 从程序性记忆看 Agent Skills：一篇综述（Agent Skills from the Perspective of Procedural Memory: A Survey）

> 来源：https://yashonwu.github.io/agent-skills-survey/ （项目页标题即 "Agent Skills Survey"；论文预印本为 Authorea Preprints 2026）
> 原文：未下载（仅摘要级引用）
> 翻译日期：2026-11-03 ｜ 范围：摘要级 ｜ 方式：机器翻译初稿，未经人工校对
> 引用于：docs/brief-plan.md

## 摘要

随着由大语言模型驱动的自主智能体在复杂真实任务上展现出强劲能力，近期研究把重点放在利用 skill（技能）为它们赋予领域专长与适应性能力上。本综述首次从程序性记忆（procedural memory）的视角，系统梳理 LLM 驱动的 Agent Skills：把技能概念化为程序性知识的核心形式，使智能体能够通过交互与经验把求解过程内化、保存并复用。我们全面考察 Agent Skills 究竟指什么、为什么对 agentic intelligence 至关重要，以及如何在 LLM 系统中有效地获取、表示、调用与精化。此外，我们综述了跨多个领域的代表性应用，并讨论发展与泛化 Agent Skills 的关键挑战与未来机会。

- **关键词**：Agent Skills、Agentic AI、LLM Agents、Procedural Memory

## 项目页要点（摘要之外的概括）

- **Skill Acquisition（技能获取）**：智能体通过反复的任务交互，把重复出现的行为模式转化为可复用的技能，编码成经验驱动的程序性知识。
- **Skill Representation（技能表示）**：技能以带轻量元数据的模块化、可发现的程序性记忆单元存储，只在需要时才展开细节。
- **Skill Invocation（技能调用）**：当任务落在某技能的适用范围内时，智能体检索并执行该技能（及相关工具），从而可靠地跑通复杂工作流。
- **Skill Refinement（技能精化）**：技能依据结果与反馈持续更新，以修复错误、提高效率并适应新的上下文。

## 题录

- **作者**：Yaxiong Wu, Yongyue Zhang
- **出处**：Authorea Preprints，2026（项目页另列 GitHub 仓库 `yashonwu/agent-skills-survey`）
- **消歧说明**：仓库参考文献中的条目只写作「Agent Skills Survey」。本译文对应其项目页标题恰为 "Agent Skills Survey" 的这篇（检索式 `procedural memory agent skills survey` 也与之吻合）。同期还有多篇名称高度相近的综述，例如 arXiv 2605.07358《A Comprehensive Survey on Agent Skills》、arXiv 2602.12430《Agent Skills for Large Language Models》、Google Research《A Survey on Agent Skills: Externalized Procedural Knowledge in Language Models》，仓库指的是哪一篇无法从现有引用唯一确定。
