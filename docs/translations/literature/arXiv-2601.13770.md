# Look-Ahead-Bench：金融场景下 Point-in-Time LLM 前视偏差的标准化基准（Look-Ahead-Bench: a Standardized Benchmark of Look-ahead Bias in Point-in-Time LLMs for Finance）

> 来源：https://arxiv.org/abs/2601.13770
> 原文：未下载（仅摘要级引用）
> 翻译日期：2026-11-03 ｜ 范围：摘要级 ｜ 方式：机器翻译初稿，未经人工校对
> 引用于：docs/brief-plan.md

## 摘要

我们提出 Look-Ahead-Bench，一个标准化基准，用于在贴近实际的金融工作流中测量 Point-in-Time（PiT）大语言模型的前视偏差（look-ahead bias）。与多数主要通过问答来测试内部前视知识的现有方法不同，本基准在实际场景中评估模型行为。为了把真正的预测能力与基于记忆的表现区分开，我们分析了模型在时间上分属不同市场状态时的性能衰减，并引入若干量化基线来划定性能门槛。

我们用主流开源 LLM——Llama 3.1（8B 与 70B）以及 DeepSeek 3.2——对照 PiT-Inference 的一组 Point-in-Time 模型（Pitinf-Small、Pitinf-Medium，以及前沿级的 Pitinf-Large）进行评估。结果显示，标准 LLM 存在显著的前视偏差（以 alpha 衰减衡量），而 Pitinf 系列没有这一问题，并且随着规模扩大表现出更好的泛化与推理能力。

本工作为金融 LLM 时间偏差的标准化评估奠定了基础，也为识别适合实际部署的模型提供了实用框架。代码见 https://github.com/benstaf/lookaheadbench

## 题录

- **分类**：cs.AI（人工智能）；cs.CL（计算与语言）；cs.LG（机器学习）；q-fin.CP（计算金融）；q-fin.GN（一般金融）
- **Comments**：无（原文未填）
- **作者**：Mostapha Benhenda
- **提交**：2026-01-20（v1）
