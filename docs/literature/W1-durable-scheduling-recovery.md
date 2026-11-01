# W1：长程任务的持久化调度与恢复

> 状态：定稿 ｜ 检索日期：2026-11-01 ｜ 对应 brief-plan.md §12.1 第 W1 行、§12.2 W1 群组子题（多 agent 会话是否需要独立于 goal_run 的持久化）

## 1. 检索式与日期

- 检索日期：2026-11-01（arXiv API，按 submittedDate 降序，覆盖 2026-06 至 2026-10）
- 检索式：
  - `all:"durable execution" AND all:agent`
  - `all:agent AND all:checkpoint AND all:recovery AND all:LLM`
  - `all:"long-horizon" AND all:agent AND all:persistence`
  - `all:agent AND all:"fault tolerance" AND all:LLM`
- 检索工具与局限：本轮命中充分，补上了 §12.1 标注的"durable execution 待补"缺口；四篇入选论文均已下载 PDF（[docs/papers/](../papers/README.md)）并全文精读。

## 2. 入选论文（4 篇，全部 2026 下半年）

| 论文 | 一句话贡献 | 与本项目的关系 | 精读状态 |
|---|---|---|---|
| [Resume Means Resume](https://arxiv.org/abs/2608.03836)（arXiv 2608.03836，2026-08） | 用机器可查契约（6 性质+fork-intent+liveness）形式化 checkpoint/interrupt/resume 语义，并用确定性 conformance harness 证明 LangGraph/CrewAI/LlamaIndex 等 5 个框架全都部分违约 | 直接给出"目标状态机+恢复扫描"的**恢复语义验收清单**；证明"框架有 checkpoint≠效果只发生一次" | 已精读（全文+附录） |
| [AgentRewind](https://arxiv.org/abs/2608.14380)（arXiv 2608.14380，2026-08） | 在每个决策边界记录 (context, env) 对齐 checkpoint，前缀从执行日志回放不重跑，成对恢复评估显示恢复率 8.0%→30.0% | "失败即修复韧性循环"的机制+评估双参考；rewind memory ≈ 跨 Run 注入的失败经验 | 已精读 |
| [Same Winners, Different Success Rates](https://arxiv.org/abs/2609.34215)（arXiv 2609.34215，2026-09） | 证明 set-agreement 类稳定性指标在数学上无法区分 85.4% 一致/1.4% 成功与 20% 一致/90% 成功，提出 4 量诊断口径（agreement、all-zero fraction、held-out success、pooled success） | W5 故障演练与恢复评估的**指标口径规范**：只报"两次演练选了同一修复策略"会重演假象 | 已精读 |
| [CUA-Recovery](https://arxiv.org/abs/2610.27645)（arXiv 2610.27645，2026-10） | ReRail 流水线构造 2,250 个人工核验错误状态（takeover-depth d∈{0..25} 梯度注入），实测最强模型 Pass@3≤25.5%、检测(EAR)与修复(Pass@3)弱相关、78% 错误至少 3 步后才显现 | W5 故障注入演练的现成设计（root cause 后按步数接管）；"检测≠修复"要求韧性循环拆两个指标 | 已精读 |

**§12.2 群组维度补充**：Resume Means Resume 的 consume-once 子句（跨进程 resume 同一 parked interrupt 时 gated effect 打 k 次，36/40 实验格饱和）正是"多 agent 会话持久化"要防的事故。结论（与 [decisions/0002](../decisions/0002-w1-recovery-semantics.md) 第 5 条一致，demo 场景 C 实证）：**语义必须统一、锚点应当独立**——群组消息不挂 goal_run（会话横跨多次期次 Run，挂靠会丢跨 Run 连续性），但必须复用与 goal_run 完全相同的 consume-once/幂等追加/恢复扫描语义（session+seq 唯一键、幂等追加、fencing 写保护），不允许出现第二套恢复语义。DeepSeek Super-agent 的 Source/Thread 抽象是同构佐证：Source 持读取位置、Thread 横跨多个 Worker 生命周期、重启不重放（[essay-study 笔记](../essay-study/deepseek-super-agent-2026.md) §2/§6）。

## 3. 方向结论

- **采纳（恢复语义清单）**：2608.03836 的六性质+FI+liveness 作为状态机恢复语义规范——RD（恢复决策必须是 DB durable state 的纯函数，扫描不得依赖进程内存/时序）、EO/CO-c（工具幂等回执；**审批门必须 CAS 式消费一次**，否则双实例调度器必然产生 lost-update）、CV（checkpoint 写入时 schema 校验 loud reject，不静默持久化非法状态）、FI（resume 请求带 retry/fork 判别位）、liveness（"永不恢复"也算违约，恢复扫描要有最终完成保证）。依据：论文 39-run fault matrix 实测 5 框架全违约，含 LangGraph crash 路径重复执行已记录任务。
- **采纳（外部 effect ledger 第二 oracle）**：恢复正确性不能只信框架/自研 checkpointer 的内部状态，要自建独立于执行路径的外部 effect 台账对账（论文用进程内计数器+磁盘 SQLite ledger 双 oracle 的方法）。依据：同上，CrewAI framework state 显示正确=11 而外部 ledger 显示实际 effect=2。
- **采纳（W5 评估口径）**：恢复评估固定报 4 量（agreement、all-zero fraction、held-out success、pooled success），结果记录持久绑定 (goal_run, step, action) provenance。依据：2609.34215 实测 checkpoint 置换改变 8–13% cell 级结论；agreement 与 success Spearman −0.796~−0.443（负相关）。
- **改造采纳（故障注入设计）**：CUA-Recovery 的 takeover-depth 梯度注入（root cause 后 0/5/10/15/20/25 步接管）搬进 W5 演练清单；错误分类（planning+perception 57.3% / termination 23.5% / execution 19.1%）用作故障类型配比参照。改造点：GUI 桌面场景换成"改坏代码/数据源不可达/调度超时/审批挂起"等金融后端故障。依据：2,250 个核验状态的错误时程统计——78.1% 错误至少 3 步后才显现，恢复扫描不能只看最近 K 步。
- **改造采纳（失败经验注入）**：AgentRewind 的 rewind memory（失败教训以 system message 注入后续 Run）对应我们的 goal_memory_digest 失败经验条目；paired-recovery 评估法（同失败状态复制两份只差恢复能力）用于 W5 演练。依据：消融显示去 rewind memory 成功率 87.8→51.2。改造点：**不采纳文件系统回滚**——我们以 DB 状态机为权威，workspace 外的金融副作用（下单/通知）只能靠 ledger+补偿，不能靠回滚。
- **不采纳**：REMIT 修复实现本身（论文的修复件只绑 checkpointer read path，我们是自研状态机，抄其原则不搬代码）。

## 4. 对设计文档的修订

- [x] brief-plan.md §12.1 W1 行：候选论文由"待补"更新为上述 4 篇（已同步更新）。
- [ ] W1 recovery demo（@dev 执行）决策记录：恢复语义清单落成可失败测试用例（状态×事件转换表逐条对拍六性质），结论落 docs/decisions/0002 起续编。
- [ ] §12.2 W1 群组持久化结论待 demo 实测后定稿（当前倾向：不建独立持久化，复用同一 effect ledger + actor_agent_id）。

## 5. 风险与待验证项

- 2608.03836 的契约针对 framework checkpointer API；我们自研 DB 状态机需把六性质翻译成表结构+转换表约束，翻译过程可能暴露新的歧义（正是 demo 要干的事）。
- 论文崩溃模型仅 fail-stop，无网络分区/脑裂；双 worker 抢占 demo 需自己加"调度器双实例"注入场景。
- CUA-Recovery 依赖可确定性重放环境；金融数据源（行情拉取）不可重放，演练需固定数据缓存快照。
- AgentRewind 的 stall 判定依赖外部 verifier，我们的 stalled 终态判据（brief-plan §13）仍需 T3 调参定标。
