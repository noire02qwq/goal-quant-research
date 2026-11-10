# 研究 Demo 区（入库）

这里放 **brief-plan 定稿之后**的研究 demo 本体，随本仓库版本管理（docs/CONVENTIONS.md §4）。

## 约定

- 每个 demo 目录自带 README，必须包含：①验证目标（对应 brief-plan 哪节的设计问题）②运行方式 ③结论指向的决策记录编号（`docs/decisions/NNNN-*.md`）。
- demo 结论走"先决策记录、后设计修订"流程：跑通后先写 `docs/decisions/`，再定点回写 `brief-plan.md`。
- 单文件/数据集超 20MB 不入库；数据放本地或外部存储，README 记录获取方式。
- 唯一不放这里的例外：写于 brief-plan 之前的 vnpy demo（`../independent-demo-apps/vn-demo/`，独立仓库）。

## 索引

| Demo | 验证目标 | 决策记录 |
|---|---|---|
| [w1-recovery-demo](w1-recovery-demo/README.md) | 双 worker 抢占、进程崩溃恢复扫描、群组会话中断恢复（brief-plan §5.2 规则 1/2/4/5 + §12.2 W1） | [0002](../docs/decisions/0002-w1-recovery-semantics.md)（已采纳） |
| [w2-memory-distillation-demo](w2-memory-distillation-demo/README.md) | 晋升 gate 可计算判据、记忆生命周期 supersede/TTL 不删除、16KB 组装 gate 先于 packing（brief-plan §5.4 + §12.2 W2） | [0003](../docs/decisions/0003-w2-memory-distillation.md)（已采纳） |
| [w3-lookahead-proof-demo](w3-lookahead-proof-demo/README.md) | 前视偏差构造性不可能（窗口数据 API 拒未来）+ 前视 lint 第二道防线 + 指标库统一计算 + assigned_role opt-in（§12.1 W3 + §12.2 W3） | **可运行（11-10 实测 12/12 + 4 步剧本全过）**；[0004](../docs/decisions/0004-w3-backtest-reliability-and-lookahead-guard.md)（**已采纳**），brief-plan 五处已按其修订 |
| [w4-approval-gate-demo](w4-approval-gate-demo/README.md) | 审批门 requested_by 归因、成员互批绕过被拒、角色×工具授权矩阵、消息不得改授权边界、预算按 goal 计（§12.1 W4 + §12.2 W4） | 脚手架就绪、实现中；决策记录待写 0005，依据 [W4 笔记](../docs/literature/W4-hitl-approval-authorization.md) |
