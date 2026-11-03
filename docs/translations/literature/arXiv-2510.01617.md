# AMAS：面向基于 LLM 的多智能体系统的通信拓扑自适应确定（AMAS: Adaptively Determining Communication Topology for LLM-based Multi-Agent System）

> 来源：https://arxiv.org/abs/2510.01617
> 原文：未下载（仅摘要级引用）
> 翻译日期：2026-11-03 ｜ 范围：摘要级 ｜ 方式：机器翻译初稿，未经人工校对
> 引用于：docs/brief-plan.md；docs/decisions/0001-multi-agent-group-research-increment.md

## 摘要

尽管大语言模型彻底改变了自然语言处理的能力，但要把它们作为自主多智能体系统（MAS）投入工业级问题求解，仍存在持续的障碍。传统 MAS 架构从根本上受限于不灵活、手工设计的图拓扑——这些拓扑对上下文没有响应能力，导致在各类学术与商业工作负载上的效果都打了折扣。为克服这些限制，我们提出 AMAS，一个具范式转换意义的框架：它通过新颖的动态图设计者重新定义基于 LLM 的 MAS。

这个组件借助轻量级的 LLM 适配，自主识别特定任务下的最优图配置，从而摆脱对单一、通用结构模板的依赖。AMAS 转而利用每个输入本身的特性，智能地把查询引导到为该任务优化的智能体路径上。在问答、数学演绎与代码生成基准上的严格验证表明，AMAS 在多种 LLM 架构上都系统性地优于最先进的单智能体与多智能体方法。我们的研究确立了一个结论：对上下文敏感的结构可适应性，是高性能 LLM MAS 部署的基础要求。

## 题录

- **分类**：cs.CL（计算与语言）
- **Comments**：Accepted by EMNLP-2025
- **作者**：Hui Yi Leong, Yuheng Li, Yuqing Wu, Wenwen Ouyang, Wei Zhu, Jiechao Gao, Wei Han
- **提交**：2025-10-02（v1），最后修订 2025-10-29（v3）
