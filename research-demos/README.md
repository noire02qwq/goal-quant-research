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
| [w4-approval-gate-demo](w4-approval-gate-demo/README.md) | 审批门 requested_by 归因 + use-time digest 绑定原子消费（Loopjacking 负例）、角色×工具矩阵不可变与运行时撤销、消息不得改授权边界、goal 级预算、确定性 monitor 优先（§12.1 W4 + §12.2 W4 + W4 采纳①–④） | **可运行（11-10 实测 16/16 测试 + 5 步剧本全过）**；[0005](../docs/decisions/0005-w4-approval-binding-and-authorization-governance.md)（**提议待核验**），依据 [W4 笔记](../docs/literature/W4-hitl-approval-authorization.md) |
| [w5-fault-drill-demo](w5-fault-drill-demo/README.md) | 五类故障注入（改坏代码/重启/改目标/interface 诚实+熔断真触发/数据面注入正交性）、固定窗口+seed 夹具、T3/T4 策略模板（§12.0 W5 研究项 + W5 笔记采纳⑥） | **可运行（11-11 实测 19/19 测试 + 7 步剧本全过，含 τ_b 实测行 +1.0000）**；0006 预留待 @research 立（τ_b 第四维实测已就位 + 汇报分档），依据 [W5 笔记](../docs/literature/W5-real-eval-fault-style.md) |
