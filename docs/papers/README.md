# 论文 PDF 归档

研究涉及的论文下载 PDF 后归档于此（docs/CONVENTIONS.md §3.4）。

## 命名

- arXiv 论文：`arXiv-<ID>.pdf`，如 `arXiv-2404.12345.pdf`（ID 不含版本号，取最新版）。
- 非 arXiv 来源：`<短名>-<年份>.pdf`，短名小写连字符。

## 引用方式

- 文献笔记/决策记录中引用时同时给出：相对路径 `docs/papers/<文件名>.pdf` + 在线链接（arXiv abs 页或官方文档 URL）。
- 无在线链接的引用视为未溯源，不得作为设计依据（CONVENTIONS §3.3）。

## 索引

| 文件 | 论文 | 在线链接 | 引用于 |
|---|---|---|---|
| arXiv-2608.03836.pdf | Resume Means Resume: A Machine-Checked Conformance Contract for Checkpoint, Interrupt, and Resume Semantics in Workflow Persistence Layers | https://arxiv.org/abs/2608.03836 | docs/literature/W1-durable-scheduling-recovery.md |
| arXiv-2608.14380.pdf | AgentRewind: Recoverable Execution for Long-Horizon LLM Agents | https://arxiv.org/abs/2608.14380 | docs/literature/W1-durable-scheduling-recovery.md |
| arXiv-2609.34215.pdf | Same Winners, Different Success Rates: Evaluating How LLM Agents Recover from Failures | https://arxiv.org/abs/2609.34215 | docs/literature/W1-durable-scheduling-recovery.md |
| arXiv-2610.27645.pdf | CUA-Recovery: Benchmarking Error Recovery in Long-Horizon Computer-Use Agents | https://arxiv.org/abs/2610.27645 | docs/literature/W1-durable-scheduling-recovery.md |
| arXiv-2610.14515.pdf | SEPM: Self-Evolving Procedural Memory Grounded in Task Graphs for Multi-Agent Collaboration | https://arxiv.org/abs/2610.14515 | docs/literature/W2-context-memory-distillation.md |
| arXiv-2610.34724.pdf | Harness-Model Collaboration for Long-Horizon Continual Learning | https://arxiv.org/abs/2610.34724 | docs/literature/W2-context-memory-distillation.md |
| arXiv-2610.38573.pdf | CALM: Conflict-Aware Lifecycle Memory Governance for Long-Horizon Language Agents | https://arxiv.org/abs/2610.38573 | docs/literature/W2-context-memory-distillation.md |
| arXiv-2610.26995.pdf | SPEM: Structure-Aware Procedural Memory for Efficient Skill Use in LLM Agents | https://arxiv.org/abs/2610.26995 | docs/literature/W2-context-memory-distillation.md |
| arXiv-2605.17937.pdf | BacktestBench: Benchmarking Large Language Models for Automated Quantitative Strategy Backtesting | https://arxiv.org/abs/2605.17937 | docs/literature/W3-backtest-reliability.md |
| arXiv-2601.13770.pdf | Look-Ahead-Bench: a Standardized Benchmark of Look-ahead Bias in Point-in-Time LLMs for Finance | https://arxiv.org/abs/2601.13770 | docs/literature/W3-backtest-reliability.md |
| arXiv-2608.27734.pdf | What survives honest evaluation? Leakage-safe, search-aware assessment of LLM-driven trading strategy discovery | https://arxiv.org/abs/2608.27734 | docs/literature/W3-backtest-reliability.md |
| arXiv-2610.03080.pdf | MintEval: Do LLMs Implement the Trading Strategy You Asked For? A Behavioural-Equivalence Benchmark | https://arxiv.org/abs/2610.03080 | docs/literature/W3-backtest-reliability.md |
| arXiv-2611.11588.pdf | FinCutBench: A Continually Updated Benchmark for Measuring the Temporal Boundaries of LLM Financial Knowledge | https://arxiv.org/abs/2611.11588 | docs/literature/W3-backtest-reliability.md |
| arXiv-2611.06607.pdf | Hard to Fool: A Bounded LLM Research Loop for Quantitative Finance, and What Two Dozen Campaigns Found | https://arxiv.org/abs/2611.06607 | docs/literature/W3-backtest-reliability.md |
| arXiv-2610.26101.pdf | QuantHarness: Reliable Before Profitable — Governing Financial Strategy Development with LLM Agents | https://arxiv.org/abs/2610.26101 | docs/literature/W3-backtest-reliability.md |
| arXiv-2610.35835.pdf | I-HITL: Inalienable Human-in-the-Loop | https://arxiv.org/abs/2610.35835 | docs/literature/W4-hitl-approval-authorization.md |
| arXiv-2609.21081.pdf | Loopjacking: Hijacking Human-in-the-Loop Approval | https://arxiv.org/abs/2609.21081 | docs/literature/W4-hitl-approval-authorization.md |
| arXiv-2610.22987.pdf | From Approval to Abuse: Privilege Escalation Attacks on Harness-Protected Coding Agents | https://arxiv.org/abs/2610.22987 | docs/literature/W4-hitl-approval-authorization.md |
| arXiv-2611.04086.pdf | Permitted but Unauthorized: Affordance-Induced Delegated-Scope Violations in Multi-Agent LLM Systems | https://arxiv.org/abs/2611.04086 | docs/literature/W4-hitl-approval-authorization.md |
