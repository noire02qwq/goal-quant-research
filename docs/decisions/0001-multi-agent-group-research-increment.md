# 0001：多智能体群组配合交互以增量研究线并入 W1–W5

> 状态：已采纳 ｜ 日期：2026-11-01 ｜ 作者：@dev ｜ 关联：brief-plan.md §12.2、§12.0/§12.1

## 背景

任务范围新增"多智能体群组配合交互"研究（用户 2026-11-01 指令），要求**仅做增量与适配、不缩水既有内容**，并安排进前 5 周。既定执行形态是"调度触发的受管 Run"（brief-plan §4.2），群组能力不能推翻该形态。检索日期 2026-10-31/11-01，候选论文均仅摘要级：

- [Multi-Agent Collaboration Mechanisms: A Survey of LLMs](https://arxiv.org/abs/2501.06322)：协作机制可扩展框架综述
- [Beyond Self-Talk: A Communication-Centric Survey of LLM-MAS](https://arxiv.org/abs/2502.14321)：通信视角分层（架构/协议/消息对象），含通信攻击面（§5.5）
- [AutoGen](https://arxiv.org/abs/2308.08155)：GroupChatManager 选 speaker + 广播；对话即编排
- [MetaGPT](https://arxiv.org/abs/2308.00352)（ICLR 2024）：SOP 流水线 + **结构化消息**（publish-subscribe、schema 化产出），降低信息丢失与幻觉级联
- [ChatDev](https://arxiv.org/abs/2307.07924)：phase-based 群组流水线
- [MultiAgentBench](https://arxiv.org/abs/2503.01935)：协调/竞争评测含 Coordination 指标

## 决策

在 §12.1 之后新增 §12.2「多智能体群组配合交互」增量研究线：W1–W5 每周挂靠一个群组子主题（W1 持久化基座 / W2 群组记忆模型 / W3 角色分工×DAG / W4 群组治理 / W5 群组故障注入），共用当周既有 demo 基建；W6–W10 不新增子主题，W8 反方评审（A3）复用 W4 产出的"角色×工具"授权矩阵与 W2 的结构化消息 schema。字段级增量：`goal_event.actor_agent_id`、`goal_memory_digest.scope/author_agent_id`、`goal_plan_task.assigned_role`（可选，缺省=单角色现行为）。

## 理由

- **挂靠而非新增周次**：满足"不缩水既有内容"，且群组子主题与当周主线天然同题（如 W2 的记忆蒸馏 ↔ 群组共享/私有记忆）。
- **静态角色 + SOP 编排**：MetaGPT/AutoGen 的 group chat 模式可审计、可归因，符合金融治理要求。
- **opt-in 字段**：`assigned_role` 缺省即现行为，群组能力不破坏既有单受管 Run 路径。

## 备选方案（不采纳的）

| 备选 | 不采纳理由 |
|---|---|
| 独立 W' 周或扩到 W1–W5 之外 | 违反"安排进前 5 周"要求；压缩既有周负载 |
| MARL/动态通信拓扑学习（[ACTS](https://arxiv.org/abs/2610.25851)、[AMAS](https://arxiv.org/abs/2510.01617)） | 与"审批可归因、行为可审计"冲突，引入不可预测性 |
| 大规模 agent 社会仿真 | 超出"单目标执行协作"范围；规模假设 ≤5 成员 |

## 对设计文档的修订

- brief-plan.md §12.2：新增整节；§12.0 Phase 1 周表下加注指向（是否已更新：是，同 PR）

## 后续动作

- [ ] W1 demo 时验证 `goal_event.actor_agent_id` 必要性（@dev，W1）
- [ ] W2 精读 AutoGen/MetaGPT 后定稿群组记忆 schema（@research，W2）
- [ ] W4 定稿"角色×工具"授权矩阵并预留 reviewer 角色位（@dev，W4）
