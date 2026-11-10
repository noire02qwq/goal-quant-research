# 决策记录（ADR）

研究 demo 跑通、文献方向落定、设计取舍发生时，先在此写决策记录，再改 brief-plan.md。**结论推翻设计假设而不写决策记录 = 未完成研究。**

## 编号与命名

- 四位递增编号：`0001`、`0002`……（下一个编号看本目录现有文件最大值 +1）
- 格式：`NNNN-<主题短名>.md`，例：`0001-vnpy-as-backtest-engine.md`
- 模板：[../templates/decision-record.md](../templates/decision-record.md)

## 生命周期

`提议` → `已采纳`（设计文档已同步更新）→ 必要时 `已被取代`（写明被哪条取代，不删除原文）。

## 已归档

| 编号 | 主题 | 状态 |
|---|---|---|
| [0001](0001-multi-agent-group-research-increment.md) | 多智能体群组配合交互以增量研究线并入 W1–W5 | 已采纳 |
| [0002](0002-w1-recovery-semantics.md) | W1 恢复语义定稿：原子认领 + fencing + 步骤级幂等回执 + 显式 outcome_unknown + 群组消息独立持久化 | 已采纳 |
| [0003](0003-w2-memory-distillation.md) | W2 记忆蒸馏语义：可计算晋升 gate + 生命周期 supersede 不删除 + gate 先于 packing | 已采纳 |
| [0004](0004-w3-backtest-reliability-and-lookahead-guard.md) | W3 回测可靠性：前视构造性防护三层定稿 + 验收口径拆分（因果合规✓/语义等价留W6）+ 账本三仪器留测评线，逐条标注验证状态 | 已采纳 |
| [0005](0005-w4-approval-binding-and-authorization-governance.md) | W4 审批/授权边界：use-time digest 绑定+原子消费（Loopjacking 证伪弱绑定）、审批通道隔离最小验证、矩阵 immutable ceiling ✓/提议来源约束未验证、monitor 唯一防线（采纳④四子项覆盖 1.5） | 提议 |
