# 0002：W1 恢复语义定稿——原子认领 + fencing token + 步骤级幂等回执 + 显式 outcome_unknown

> 状态：已采纳 ｜ 日期：2026-11-01 ｜ 作者：@dev ｜ 文献合入：@research 2026-11-01 ｜ 关联：[w1-recovery-demo](../../research-demos/w1-recovery-demo/README.md)、[literature/W1 文献笔记](../literature/W1-durable-scheduling-recovery.md)、brief-plan §5.2/§5.3/§12.2 W1

## 背景

W1 研究项要求用独立 demo 建立「持久化调度与恢复」的设计依据（brief-plan §12.0）。平台既有调度层已提供原子认领/lease/fencing/occurrence 幂等四项能力声明，但 goal-agent 领域侧（`goal_run` 生命周期、回执粒度、崩溃后的可见性语义）尚无经实证的定稿。同时 §12.2 W1 群组子题要回答「多 agent 会话是否需要独立于 goal_run 的持久化」。

## 决策

1. **`goal_run` 采纳四元组状态语义**：`queued → running → (succeeded | failed | outcome_unknown)`。崩溃/断连的 Run **必须显式落 `outcome_unknown`**，由恢复扫描决定重排或人工确认——不允许静默重试，也不允许伪装终态（demo 场景 B 实证该路径）。
2. **调度原语照搬平台能力、不重造**：原子认领（单语句 UPDATE + RETURNING）、lease 心跳续期、fencing token 递增、恢复扫描四件套。demo 以最小实现复刻该语义并全部验证通过（demo 代码为独立原创实现，不含平台代码）。
3. **回执两级粒度**：期次级 `occurrence_key` 回执（跨期去重，防整期重跑）+ 步骤级 `step_key` 回执（期内防重跑）。实测：崩溃恢复后已完成步骤零重跑、中断步骤重跑恰好一次——**步骤级回执是"已完成期次不重跑"（§4.3）在期次内部的自然延伸，必须纳入 schema**。
4. **fencing 写保护**：回执/终态写入必须携带当前 fencing token，租约易主后旧持有者的写入被拒绝（测试 `test_stale_token_write_rejected`）。这是"重启后的旧 worker 不污染新执行"的构造性保证。
5. **群组消息独立于 goal_run 持久化**（回答 §12.2 W1 问题）：双 agent 会话消息用独立表（`group_message`，session+seq 主键、幂等追加），恢复时从持久化消息重建上下文续传；事件流 `goal_event` 增加 `actor_agent_id` 归因。**理由**：会话消息生命周期跨多个 goal_run（一个会话可能横跨多次期次执行），挂靠 goal_run 会在恢复时丢失跨 Run 的对话连续性；demo 场景 C 实证独立持久化下中断恢复无重复、无丢失。**文献支撑**（[W1 文献笔记](../literature/W1-durable-scheduling-recovery.md)，2026-11-01 精读合入）：[Resume Means Resume](https://arxiv.org/abs/2608.03836) 实测跨进程 resume 同一 parked interrupt 时 consume-once 大面积失效（36/40 实验格饱和、两后端 10/10），证明"独立锚点+统一语义"缺一不可——锚点独立解决跨 Run 连续性，而 consume-once/幂等追加/fencing 统一语义防止多恢复者并发重放；[DeepSeek Super-agent](../essay-study/deepseek-super-agent-2026.md) 的 Source/Thread 抽象同构（Source 持读取位置、Thread 横跨 Worker 生命周期、重启不重放）。

## 实测数据

环境：macOS 26 / Python 3.14.6 / sqlite 3.53.2（WAL），两次连跑结果一致；demo README 有完整输出。

| 场景 | 测量 | 结果 |
|---|---|---|
| A 双 worker 抢占 | 12 任务并发认领 | 两进程各 6 个，36 条步骤证据 0 重复 0 丢失 |
| B 崩溃恢复 | 第 2 步硬退出（exit 137） | 崩溃后 `running`+lease 剩余 ~1.45s；过期后扫描 `requeued=1`；续跑后步骤 1 零重跑、步骤 2 interrupted+completed 各 1 |
| C 群组恢复 | 双 agent 会话第 4 步崩溃 | 崩溃前 4 条消息持久化；恢复后 seq 1–6 完整无重复 |
| fencing | 旧 token 写回执 | 拒绝；新 token 接受 |

## 理由

- 「结果不确定不隐藏重试」是 mission 对任务失败恢复的硬要求；demo 证明 `outcome_unknown` + 显式扫描能在不隐藏崩溃的前提下自动收敛（无需人工介入即可重排，同时事件流完整留痕供人工追溯）。
- 步骤级回执直接决定恢复成本：日频量化期次内含拉数/回测/报告多步，整期重跑浪费算力且可能重复写产物；实测幂等续跑把重跑范围收敛到"中断那一步"。
- 群组独立持久化与 MetaGPT/AutoGen 的「结构化消息 + 独立会话编排」方向一致（仅摘要级）；W1 精读后补充：与 Resume Means Resume 的 consume-once 实测证据及 DeepSeek Source/Thread 抽象互证（见决策 5 文献支撑）。

## 备选方案（不采纳的）

| 备选 | 不采纳理由 |
|---|---|
| 崩溃后立即重试（无 lease） | 无法区分"慢"与"死"，双执行风险；fencing 无从谈起 |
| 只有期次级回执（无步骤级） | 期内多步全量重跑，长回测期次恢复成本不可接受（实测中断步骤重跑范围会扩大到整个期次） |
| 群组消息挂在 goal_run 上 | 跨 Run 会话连续性丢失，恢复后对话上下文断裂（场景 C 的恢复语义将不成立） |
| 恢复扫描静默重排（不标 outcome_unknown） | 违反"结果不确定不隐藏"，审计视角无法区分"从未执行"与"执行结果未知" |

## 对设计文档的修订

- brief-plan §5.2 规则 2：回执粒度明确为「期次级 + 步骤级」两级（是否已更新：**否，待本记录转"已采纳"后由 @dev 走 PR 修订**）
- brief-plan §4.4 `goal_run`：补充 `fencing_token`、`lease_expires_at`、`claim_owner` 字段；`goal_receipt` 从 `receipt_json` 字段升格为独立幂等回执表（是否已更新：否，同上）
- brief-plan §12.2 W1 落点：确认 `goal_event.actor_agent_id` 采纳，且群组消息需独立持久化表（是否已更新：否，同上）

## 文献复核结论（@research，2026-11-01）

对五条决策逐条对照 [literature/W1](../literature/W1-durable-scheduling-recovery.md) 精读结果：

1. `outcome_unknown` 显式化 —— **文献强化**。Same Winners（[2609.34215](https://arxiv.org/abs/2609.34215)）证明不显式区分"从未执行/结果未知"会使恢复评估指标失真；对应其诊断四量（agreement / all-zero fraction / held-out success / pooled success），W5 演练口径采纳。
2. 调度四件套不重造 —— **无冲突**。Resume Means Resume（[2608.03836](https://arxiv.org/abs/2608.03836)）对 DBOS 基线的测量同样显示：成熟持久层的 gate-answer 延迟 2.9–5.0×，佐证"不重造、薄封装"方向。
3. 两级回执 —— **文献强化**。同文 CO-c 子句实测：无计数式 consume-once 时跨进程恢复 gated effect 打 k 次；步骤级 `step_key` 回执即 CO-c 的实现。
4. fencing 写保护 —— **文献强化**。同文 REMIT 修复只能绑在 durable-state read path（write path 无效），fencing 拒旧 token 写入正是把守卫放在写路径的做法。
5. 群组消息独立持久化 —— **文献确认，措辞校准为"语义统一、锚点独立"**（见决策 5 文献支撑段）。

补充采纳项（不在本记录五条内，随 brief-plan 修订进入设计）：①自建外部 effect ledger 作恢复正确性第二 oracle（框架内部状态不可信——5 框架实测全部部分违约）；②恢复正确性验收清单＝六性质+FI+liveness（翻译为状态×事件转换表的可失败测试）；③CUA-Recovery（[2610.27645](https://arxiv.org/abs/2610.27645)）takeover-depth 梯度注入用于 W5 故障演练设计，且检测(EAR)与修复(Pass@3)弱相关——韧性循环须拆"检测""修复"两个指标。

## 后续动作

- [x] W1 文献精读（durable execution 方向 4 篇 + DeepSeek super-agent）结论合入本记录，转「已采纳」（@research，2026-11-01）
- [ ] 转已采纳后走 PR 修订 brief-plan §4.4/§5.2/§12.2 并留痕（@dev）
- [ ] 平台仓库落地时按本记录定义 goal_* schema 与恢复扫描实现（harness-hub 开发，待 @user 回公司内网后启动）
