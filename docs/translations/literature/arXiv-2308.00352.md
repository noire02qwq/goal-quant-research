# MetaGPT：面向多智能体协作框架的元编程（MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework）

> 来源：https://arxiv.org/abs/2308.00352
> 原文：未下载（仅摘要级引用）
> 翻译日期：2026-11-03 ｜ 范围：摘要级 ｜ 方式：机器翻译初稿，未经人工校对
> 引用于：docs/brief-plan.md、docs/decisions/0001-multi-agent-group-research-increment.md

## 题录

- **英文原题**：MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework
- **作者**：Sirui Hong, Mingchen Zhuge, Jiaqi Chen, Xiawu Zheng, Yuheng Cheng, Ceyao Zhang, Jinlin Wang, Zili Wang, Steven Ka Shing Yau, Zijuan Lin, Liyang Zhou, Chenyu Ran, Lingfeng Xiao, Chenglin Wu, Jürgen Schmidhuber
- **arXiv**：arXiv:2308.00352 ［Submitted on 1 Aug 2023 (v1), last revised 1 Nov 2024 (this version, v7)］

## 摘要（中文译文）

基于大语言模型（LLM）的智能体社会在自动问题求解上已取得显著进展。现有的 LLM 多智能体系统已经能够完成简单的对话型任务；但面对更复杂的任务，朴素地串联 LLM 会引发级联幻觉、造成逻辑不一致，使求解变得困难。

本文提出 MetaGPT，一个创新的元编程框架，把高效的人类工作流程融入 LLM 多智能体协作。MetaGPT 把标准操作规程（SOP）编码为提示序列，让工作流更加顺畅，使具备类人领域专长的智能体能够校验中间结果、减少错误。MetaGPT 采用流水线范式，为不同智能体分配不同角色，把复杂任务高效拆解为由多个智能体协作完成的子任务。在协作式软件工程基准上，MetaGPT 生成的方案比以往基于对话的多智能体系统更加连贯。

项目地址：https://github.com/geekan/MetaGPT

以上为摘要级译文；原文正文未下载、未翻译。

## 原文分类与 comments

- **分类（arXiv subjects）**：Artificial Intelligence (cs.AI); Multiagent Systems (cs.MA)
- **comments**：无（arXiv abs 页未给出）
