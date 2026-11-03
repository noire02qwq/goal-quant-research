# ExpeL：大语言模型智能体是经验学习者（ExpeL: LLM Agents Are Experiential Learners）

> 来源：https://arxiv.org/abs/2308.10144
> 原文：未下载（仅摘要级引用）
> 翻译日期：2026-11-03 ｜ 范围：摘要级 ｜ 方式：机器翻译初稿，未经人工校对
> 引用于：docs/brief-plan.md

## 题录

- **英文原题**：ExpeL: LLM Agents Are Experiential Learners
- **作者**：Andrew Zhao, Daniel Huang, Quentin Xu, Matthieu Lin, Yong-Jin Liu, Gao Huang
- **arXiv**：arXiv:2308.10144 ［Submitted on 20 Aug 2023 (v1), last revised 20 Dec 2024 (this version, v3)］

## 摘要（中文译文）

近来，把大语言模型（LLM）用于决策任务的研究热度迅速上升，主要依靠的是 LLM 内蕴的广泛世界知识。虽然为特定决策任务定制 LLM 的需求日益增长，但针对任务做微调既耗费资源，也可能削弱模型的泛化能力。况且 GPT-4、Claude 等先进语言模型主要通过 API 调用提供服务，其参数权重属专有信息、不对外公开。这使得「不更新参数、仅从智能体经验中学习」的新方法愈发必要。

为应对这些问题，我们提出经验学习智能体 ExpeL（Experiential Learning）。该智能体从一批训练任务中自主积累经验，并用自然语言提炼知识；在推理阶段，它回忆已提炼的见解与过去的经验，据此做出有依据的判断。实验结果凸显了 ExpeL 稳健的学习效能：随着经验不断积累，其表现持续提升。我们还通过定性观察与补充实验，进一步考察了 ExpeL 涌现的能力与迁移学习潜力。

以上为摘要级译文；原文正文未下载、未翻译。

## 原文分类与 comments

- **分类（arXiv subjects）**：Machine Learning (cs.LG); Artificial Intelligence (cs.AI); Computation and Language (cs.CL)
- **comments**：Accepted by the 38th Annual AAAI Conference on Artificial Intelligence (AAAI-24)
