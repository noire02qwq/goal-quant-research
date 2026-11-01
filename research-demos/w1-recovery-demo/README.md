# W1 Recovery Demo：持久化调度、崩溃恢复与群组会话恢复

> 状态：已跑通（2026-11-01，macOS / Python 3.14.6 / sqlite 3.53.2）

## 验证目标

对应 brief-plan §12.0 W1 研究项「模拟双 worker 抢占 + 进程崩溃后 recovery 扫描恢复」与 §12.2 W1 群组子题「群组状态的持久化基座」，逐条验证 §5.2 执行规则：

| # | 规则（brief-plan §5.2） | 验证方式 |
|---|---|---|
| 1 | 原子认领 + lease + fencing（§5.3 调度层） | 场景 A：双 worker 进程抢 12 个任务 |
| 2 | 回执先查再执行、幂等去重 | 场景 B：崩溃后续跑，已完成步骤零重跑 |
| 4 | 结果不确定不隐藏重试（`outcome_unknown`） | 场景 B：崩溃留下 running + 过期 lease，恢复扫描显式标记再重排 |
| 5 | 恢复扫描：lease 过期孤儿 Run 重入队 | 场景 B：`recovery_scan()` 统计与状态断言 |
| W1§12.2 | 群组消息独立持久化 + `goal_event.actor_agent_id` 归因 | 场景 C：双 agent 会话中断后从持久化消息恢复 |

## 运行方式

零第三方依赖（Python 标准库 + sqlite3）：

```bash
cd research-demos/w1-recovery-demo
python3 demo.py                 # 三组场景端到端（含真实子进程崩溃，退出码 137）
python3 -m unittest test_recovery -v   # 9 个定点测试
```

## 文件

| 文件 | 职责 |
|---|---|
| `goalstore.py` | 最小持久化基座：goal_run（认领/租约/fencing）、goal_receipt（幂等回执）、step_exec_log（步骤级执行证据）、goal_event（带 actor 归因的事件流）、group_message（群组消息） |
| `worker.py` | worker 子进程：认领→回执先查→分步执行→回执/终态；`--crash-at N` 在第 N 步硬退出（不写回执、不释放租约）注入真实进程崩溃 |
| `demo.py` | 场景编排与断言：A 双 worker 抢占、B 崩溃恢复、C 群组会话恢复 |
| `test_recovery.py` | 定点测试：fencing 拒绝过期写入、回执幂等、恢复扫描语义、actor 归因 |

本 demo 为独立原创最小实现（非平台代码移植），只承载恢复语义验证；平台侧真实实现位于公司仓库，不入库（CONVENTIONS §6）。

## 实测结论（2026-11-01，两次连跑结果一致）

- **场景 A**：12 任务 × 双 worker，两进程各认领 6 个；36 条步骤证据无一重复、无一丢失 → 原子认领在并发下安全。
- **场景 B**：worker 在第 2 步 `os._exit(137)`；崩溃后 Run 留在 `running`、lease 剩余 ~1.45s（**不伪装成功、不立即重试**）；租约过期后 `recovery_scan` 记 `outcome_unknown` → 重排；恢复 worker 幂等续跑：步骤 1（已完成）零重跑，步骤 2（中断）标 `interrupted` 后重跑一次，最终 `succeeded`。
- **场景 C**：researcher/coder 双 agent 会话在第 4 步崩溃，4 条消息已持久化；恢复 worker 从持久化消息重建上下文续传，最终消息 seq 1–6 完整无重复，步骤级回执防重放。
- **fencing**（测试覆盖）：租约易主后旧 token 的回执写入被拒绝，新 token 写入成功 → 重启后的旧 worker 无法污染新执行。

## 结论指向的决策记录

[docs/decisions/0002-w1-recovery-semantics.md](../../docs/decisions/0002-w1-recovery-semantics.md)（状态：提议；W1 文献精读结论回来后由 @research 合入并转「已采纳」）。
