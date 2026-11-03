# hermes-agent 走读笔记（2026）

> **状态**：已完成（文档级 + 关键源码走读；纯静态走读，未在运行时实测）
> **走读日期**：2026-11-03
> **对象**：`NousResearch/hermes-agent`（本 agent 运行时），本地克隆 `oss-repos/hermes-agent`，HEAD `ad2b705b`（**depth=1，未读 git 历史**）
> **对照文档**：本项目 `docs/brief-plan.md` §3 主表两条 hermes 映射、§5.1/§5.2/§5.4/§5.5
>
> ⚠️ **自身项目利益相关**：hermes-agent 即当前运行本任务的 agent 运行时，本文所有结论既是外部参考，也是"自家地基"的现状描述——回填 §3 时应注明这一双重身份。
> ⚠️ 仓库内无顶层 `docs/`，文档站源码在 `website/docs/`（对应 https://hermes-agent.nousresearch.com/docs ）；下文文档路径均以仓库根为基准。

---

## 1. 精读范围

**已精读（文档）**：

| 文档 | 内容 |
|---|---|
| `website/docs/user-guide/features/memory.md` | MEMORY.md/USER.md 双存储、字符上限、frozen snapshot、nudge/background review、write_approval |
| `website/docs/user-guide/features/skills.md` | 渐进披露三级加载、`skill_manage`、写入门控、project-local skills、外部目录 |
| `website/docs/user-guide/features/curator.md` | 技能生命周期 `active→stale→archived`、pin/lock、审计 ledger、快照回滚 |
| `website/docs/developer-guide/cron-internals.md` | 任务存储、tick 循环、**missed-occurrence contract（重启缺口）**、fire-claim 租约、投递队列、provider fallback |
| `website/docs/developer-guide/state-db-recovery.md` | state.db/FTS 损坏的在线隔离与修复 |
| `website/docs/user-guide/features/kanban.md`（第 1340–1474 行：Runs / Event reference） | 每次尝试一行 run、崩溃/过期/孤儿卡回收、unknown admission 不重执行 |

**已精读（源码）**：

| 文件 | 读了什么 |
|---|---|
| `hermes_startup_watchdog.py`（全文 513 行） | 启动存活看门狗：lease/CPU 扩展、fire 取证、`os._exit(75)` |
| `cron/jobs.py`（关键函数定位）、`cron/occurrences.py`、`cron/unreachable_retry.py`、`cron/monitor.py`（头部） | 持久化、跨进程 flock、occurrence 去重、受限重跑 |
| `agent/turn_context.py`（nudge 计数与 turn 装配）、`agent/turn_finalizer.py`（840–895 行） | memory/skill nudge 触发点 |
| `run_agent.py`（740–850 行） | 后台 review fork 的生成/延迟/重排队 |
| `agent/background_review.py`（380–560 行提示词） | 蒸馏提示词：记忆路由 + 技能 lesson 层规范 |
| `agent/agent_init.py`（nudge 配置）、`hermes_cli/config_defaults.py`（1300–1315 行） | 默认参数 |
| `agent/memory_manager.py` / `agent/memory_provider.py`（620–670 / 183–195 行） | 外部记忆 provider 的 `on_session_end` 钩子 |

**明确没读**：`gateway/` 主循环与会话生命周期源码、`cron/scheduler.py` 主循环全文（只按文档+函数签名核对）、`tools/memory_tool*.py` 与 `tools/skill_*.py` 实现细节、第三方记忆 provider（Honcho/Mem0 等）实现、`evals/`、i18n 文档、skill 加载器（`skills_tool.py`）实现。以上均为"文档层面已述、源码未逐行核"，凡引用只标文档结论。

---

## 2. §3 映射①判定：记忆自管 + 周期蒸馏（nudge）+ 经验→技能沉淀

**原文（brief-plan §3 hermes 行）**：`agent 自管记忆 + 周期蒸馏（nudge）；经验→技能沉淀` → 落 `Run 收尾记忆蒸馏` + `经验隐式沉淀为目标私有技能`。

### 判定：**证实（主体机制成立；但"蒸馏时机"与"技能作用域"两处有出入，需本项目自建）**

### 2.1 已证实：agent 自管记忆

- 两个文件存储：`MEMORY.md`（2,200 字符）/ `USER.md`（1,375 字符），按 profile 隔离，会话开始时**冻结快照**注入系统提示；agent 用 `memory` 工具 `add/patch/remove` 自管，无 `read` 动作（内容本来就在上下文里）。
  路径 `website/docs/user-guide/features/memory.md`
  <https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/memory.md>
- 源码实现：`tools/memory_tool.py`（`memory_tool()` 入口，222 行起）、`tools/memory_tool_store.py`。
  <https://github.com/NousResearch/hermes-agent/blob/main/tools/memory_tool.py>
- **容量策略与本项目不同**：超限不是自动压缩，而是**报错并要求 agent 自己在同一批操作里腾位**（"limit is checked only on the batch result"）；另有精确重复拒绝与注入/外泄模式安全扫描。见 memory.md "What Happens When Memory is Full" / "Security Scanning"。
- 跨会话召回的另一半是 `session_search`（`~/.hermes/state.db` FTS5，无 LLM 摘要），与记忆文件分工："关键事实进记忆、往事按需搜"。见 memory.md "Session Search"。

### 2.2 已证实：周期蒸馏（nudge）

- 两个 nudge 计数器，**默认间隔都是 10**：
  - `memory.nudge_interval: 10` → `hermes_cli/config_defaults.py:1309`
    <https://github.com/NousResearch/hermes-agent/blob/main/hermes_cli/config_defaults.py>
  - `skills.creation_nudge_interval: 10` → `agent/agent_init.py:1288`
    <https://github.com/NousResearch/hermes-agent/blob/main/agent/agent_init.py>
- 触发点：`_tick_memory_nudge()` 每个**用户轮次** +1，到间隔即置位 `should_review_memory`（`agent/turn_context.py:765-776`）；技能侧按**工具迭代次数**累加（`agent/turn_finalizer.py:861-869`、`agent/provider_projection.py:45`）。计数器跨轮不清零、可从历史 hydrate（`turn_context.py:759-762`）。
  <https://github.com/NousResearch/hermes-agent/blob/main/agent/turn_context.py>
- 置位后由 `run_agent._spawn_background_review()` 起一个 **后台 fork**（结构克隆对话快照、独立 prompt cache、不碰活跃会话；本地 GPU 场景可 `defer` 到空闲、被抢占可重排队 ≤3 次）。`run_agent.py:752-830`
  <https://github.com/NousResearch/hermes-agent/blob/main/run_agent.py>
- 蒸馏提示词三份：`_MEMORY_REVIEW_PROMPT`（391）、`_SKILL_REVIEW_PROMPT`（456）、`_COMBINED_REVIEW_PROMPT`（529），在 `agent/background_review.py`。记忆侧强调"只存能指出出处的落地事实、不推断用户特质"；技能侧强调"class-level 伞技能、教训不是日志、read-before-write 强制、未验证的失败不许写成可靠流程"。
  <https://github.com/NousResearch/hermes-agent/blob/main/agent/background_review.py>

### 2.3 出入一：蒸馏**不是"Run/会话收尾"**，而是"每 N 轮后的后台 review"

- 上述触发点在 **turn 结束**（`agent/turn_finalizer.py` 的 `_mirror_turn_to_memory` → `_spawn_background_review`），与"会话结束"无关；文档也明说 `Memory Needs Session Boundaries`——内置记忆系统是围绕"会话结束"设计的**消费**侧，但**写入侧的蒸馏钩子不在会话结束处**。
- 内置记忆唯一带 `on_session_end` 语义的是**外部记忆 provider**（`agent/memory_provider.py:183`："End-of-session extraction; fires only at real session boundaries, never per-turn"，由 `agent/memory_manager.py:629/commit_session_boundary_async` 串行调度，end→switch 严格先后）。
- 另一条硬约束：**frozen snapshot**——本会话写入的记忆磁盘上立即生效，但要**下一个会话**才进系统提示（memory.md "Frozen snapshot pattern"）。
- ⇒ **对本项目（自身项目利益相关）**：§5.4 的"每期 Run 收尾蒸馏"在 hermes 里**没有直接对应物**，需要自己在受管 Run 终态处挂蒸馏子步骤；可借鉴的是 review fork 的形态（结构克隆快照、独立 cache、可延迟、可被 `memory.write_approval` 门控暂存）。

### 2.4 出入二：经验→技能沉淀证实，但**作用域是 profile 级全局，不是"目标私有"**

- 证实部分：后台 review 会创建/修补 class-level 伞技能，且**只有 `write origin = background_review` 的创建**才被标 `created_by: agent` 进入 curator 管辖；前台 `skill_manage(create)`（含 `/learn`）标 `created_by: learn`，视为用户主导、curator 不动。见 `website/docs/user-guide/features/curator.md` §"What agent-created means"。
  <https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/curator.md>
- 作用域事实：技能全部落在 `~/.hermes/skills/`（profile 唯一真源），**进 `skills_list` 索引、进系统提示目录、可被任何会话加载**——hermes 里**不存在"目标私有、不进技能选择目录"的技能**。
- 最接近"私有作用域"的三个现成机制（可作为 §5.4 目标私有技能的参照）：
  1. **project-local skills**：`<repo>/.hermes/skills/`，仅在该仓库会话生效、**必须 `hermes skills trust` 才加载**、扫描危险即隔离、curator 永不修改、优先级最高（`skills.md` §Project-Local Skills / §Scan-time quarantine）。
     <https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/skills.md>
  2. **`skills.create_dir`**：把 agent 新建技能重定向到指定目录，agent 提示词随配置渲染。
  3. **cron 任务的 `skills:` 字段**：被任何 cron 任务引用的技能（含 paused/disabled）**被 curator 跳过自动流转**，防止慢周期任务的技能被归档（curator.md §How it runs 第 1 阶段、§Pinning）。
- 门控与回滚（对本项目审批门有直接参考）：`memory.write_approval` / `skills.write_approval` 开启后写入一律**暂存**（`~/.hermes/pending/skills/`，重启存活），用 `/memory pending`、`/skills approve|reject` 审（memory.md §Controlling memory writes、skills.md §Gating agent skill writes）。
  <https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/memory.md>

---

## 3. §3 映射②判定：cron + 持久化状态模块 + startup watchdog 组合

**原文（brief-plan §3 hermes 行）**：`cron + 持久化状态模块 + startup watchdog 组合` → 落 `无人值守调度的工程样板` + `恢复扫描（孤儿 Run 清理）`。

### 判定：**有出入——前半（无人值守调度工程样板）证实且证据很硬；后半（startup watchdog = 恢复扫描/孤儿 Run 清理）与源码语义不符，该子项应改写**

### 3.1 已证实：cron 持久化 + 重启恢复语义（工程样板成立）

- **持久化**：任务存 `~/.hermes/cron/jobs.json`，临时文件+rename 原子写；跨进程 **fcntl/msvcrt flock**（`cron/jobs.py:260 (_acquire_flock)`、`:296` 说明 gateway 与 CLI 并写场景）。
  <https://github.com/NousResearch/hermes-agent/blob/main/cron/jobs.py>
- **重启缺口契约（missed-occurrence contract）**——文档级核心证据：**每 occurrence 至多执行一次，且每个 occurrence 都必须有交代**（要么带 `scheduled_instant` 执行，要么带原因记 skip，绝不静默丢弃）。机制顺序：
  1. 派发**前**就把 `next_run_at` 推过当期（防崩溃后反复重发），同时盖 `pending_slot` 戳；
  2. `pending_slot` 属主可证已死 → **恢复一次**（把 `scheduled_at` 还原为 `next_run_at`，最多还原一次，绝不回放 N 个槽）；
  3. 已执行的 occurrence 查 executions 台账 `completed` 行 → 永不二次执行（`failed/unknown` 不算完成）；
  4. 宽限期内迟到照发（`kind=late`）、过宽限合并补发一次（`catch_up`）或按 `cron.catch_up_missed: false` 记原因跳过。
   见 `website/docs/developer-guide/cron-internals.md` §Missed-occurrence contract；实现 `cron/occurrences.py`（`completed_occurrence` / `pending_slot_stamp` / `unclaimed_pending_slot`）、`cron/jobs.py:3177 (_evaluate_due_job)` / `:2723 (claim_job_for_fire)` / `:2484 (mark_job_run)`。
  <https://github.com/NousResearch/hermes-agent/blob/main/website/docs/developer-guide/cron-internals.md>
  <https://github.com/NousResearch/hermes-agent/blob/main/cron/occurrences.py>
- **运行期租约与 fencing**：fire 期间持有 `fire_claim={at,by}`，心跳线程每 60s 刷新、租约 300s；心跳读到"别人的 claim"须复采样确认才取消在途 run；完成时的写入**以 store 判定并按 `execution_id` fence**（idempotent，不覆盖后来者）——同 `hermes cron` 文档 "Every write is fenced on the execution_id"。
- **不确定结果不重试（与 §5.2 规则 4 强同构）**：
  - 投递队列 `cron/delivery_queue.py`：行 `pending→delivering→delivered|failed|suppressed` 每行至多认领一次，**认领方 gateway 死在发送中 → 该行 fence 成 `unknown` 且永不重试**（`cron-internals.md` §Queued delivery lifecycle；回写 `cron/delivery_outcome.py::settle_queued_delivery`）。
  - `cron/unreachable_retry.py` 头部明文：只有"**瞬时网络错 + agent 零次 API 调用**"才自动重跑——"Nothing was executed and nothing was spent, so re-running cannot double a side effect"，普通失败一律不做通用重试。
    <https://github.com/NousResearch/hermes-agent/blob/main/cron/unreachable_retry.py>
- **无人值守韧性**：provider fallback 链 + 凭据池轮转注入 cron run（`cron-internals.md` §Provider Recovery）；调度触发器可插拔且**缺 provider 必回落内置 ticker（"cron is never left without a trigger"）**；cron run 是全新会话、禁用 `cronjob` 工具集防递归；每个 cron job 可挂 `skills`。

### 3.2 有出入：startup watchdog **不是**恢复扫描

- `hermes_startup_watchdog.py` 的职责（docstring 原文）：**进程在事件循环活起来之前死锁**（OOF-298：30 小时全在 `futex_wait_queue`、零日志、s6 却看到活 PID）时，由入口处武装的守护线程 `faulthandler` dump 全线程栈、写 lifecycle ledger、`os._exit(75)` 让 s6/systemd **重启进程**。权限顺序：阶段 lease（`report_startup_progress`，单次钳 900s）> 进程 CPU 进展（至多 3 次延长）> 开火；`kick` 用于故意零 CPU 的等待（重启风暴退避）；**仅 env 配置**（`HERMES_STARTUP_WATCHDOG=0/…_TIMEOUT_S`），因为 config.yaml 解析本身就在被保护范围内；fire 路径禁自带 import、另有 10s 兜底护送线程。
  <https://github.com/NousResearch/hermes-agent/blob/main/hermes_startup_watchdog.py>
- ⇒ 它是"**启动存活 → 拉起重启**"的看门狗，**不扫描任何孤儿 Run、不回收任何持久化任务状态**。§3 把它写成"恢复扫描（孤儿 Run 清理）"是**语义错配**。

### 3.3 hermes 里真正对应"恢复扫描 / 孤儿 Run 清理"的东西（建议据此回填）

1. **cron 的 `pending_slot` 恢复 + occurrence 台账**（§3.1）：启动后每次 due 扫描自带"孤儿槽恢复、至多一次"。
2. **Kanban dispatcher 恢复扫描**（与本项目 `goal_run` 最同构的原型）：每 60s 循环——回收过期 claim（TTL）、回收**已死 worker**（PID 不在但 TTL 未到）、回收跑完还活着的 worker、超时（`timed_out`）、无心跳陈旧（`stale`，默认 4h+1h 心跳窗）、以及**孤儿卡对账**：`running` 但 `claim_lock/claim_expires` 为 NULL（claim 中途崩溃/手工 SQL/库恢复）且无活 worker → 重排回 `ready` 并落 `reconciled` 事件，开关 `kanban.reconcile_orphans`（默认 true）。见 `website/docs/user-guide/features/kanban.md` L138、L1459–1463。
   <https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/kanban.md>
   - 同文档 L1349–1367：**unknown admission 不重执行**——owner/worker 带"未知准入"消失时，只要绑定期解释器可能还活着，**过期 claim、陈旧心跳、运行时上限都不重跑该模糊尝试**；等解释器确认死亡后才按 crash 回收；并提供 `prompt.resolve_unknown` 显式落定。这几乎是 §5.2 规则 4（"不伪装终态、不静默重试、审计能区分从未执行与结果未知"）的现成实现。
3. **启动期清理类扫描**：Docker 孤儿容器回收器（`docker_orphan_reaper`，启动时扫 `Exited` 且超过 `2×lifetime_seconds` 的 hermes 标签容器，`website/docs/user-guide/configuration.md` L433–475）。
4. **state.db 损坏的在线隔离**：`website/docs/developer-guide/state-db-recovery.md`——写失败即 quarantine 句柄、跳过 WAL checkpoint、派生索引降级 LIKE 回退（"stopping the writes is the protection"）。

### 3.4 对照结论（供 §5.2 / §5.4 回填）

| 本项目条目 | hermes 对应物 | 备注 |
|---|---|---|
| §5.2 规则 4 结果不确定不隐藏重试 | kanban unknown admission 不重执行；delivery queue `unknown` fence 永不重试；unreachable_retry 只在零副作用证明下重跑 | **强同构，多处独立印证** |
| §5.2 规则 5 恢复扫描（先标 unknown 再决策） | cron `pending_slot` 恢复；kanban `reconcile_orphans` / crash sweep | 扫描同样幂等、带原因落事件 |
| §5.2 规则 6 fencing 写保护 | cron 按 `execution_id` fence 的写回 + 300s fire-claim 租约心跳；kanban claim TTL + live-claim guard | 同构 |
| §5.4 CALM 生命周期（确定性状态机、不物理删） | **内置记忆侧：未找到任何生命周期状态机**（只有字符上限+add/patch/remove）；**技能侧有**：`active→stale→archived` 确定性相位（14d stale / 30d archive）、归档可 `restore`、`archive_ttl_days` 显式 TTL、consolidation 用 `absorbed_into` 归档而非删除、每次变更有审计 ledger 可单条回滚 | CALM 的"supersede 不删 + TTL 第二通道"最接近的落地在**技能库**而非记忆；`curator.md` |
| §5.1 有界摘要（打分+贪心装入） | hermes 是**硬字符上限 + 超限报错 + frozen snapshot**，无打分无准入 gate | 实现路线不同，不构成佐证，构成对照 |

---

## 4. 新映射候选（建议进 §3 主表或 §5 对应小节）

1. **kanban dispatcher 恢复扫描 + `task_runs`（一次尝试一行）+ unknown admission 不重执行** → §4.4 `goal_run`/`goal_receipt` 双表与 §5.2 规则 4/5/6 的**同仓同构原型**（比 startup watchdog 贴合得多）。证据：`website/docs/user-guide/features/kanban.md` L1342–1371、L1459–1463。
2. **cron 投递队列的 fenced-unknown + `execution_id` 幂等写回** → §4.4 `goal_receipt` 的 fencing 与"投递结果终局化"参照（`cron-internals.md` §Queued delivery lifecycle、`cron/delivery_outcome.py`）。
3. **curator 技能生命周期 + 审计 ledger + 快照/单条回滚** → §5.4 目标私有技能的**淘汰与回退治理**（`curator.md`：`.usage.json` sidecar、`.curator_ledger.jsonl` 内容寻址 blob、`hermes curator rollback <entry-id>`）。
4. **`write_approval` 暂存审批（memory/skills 双门）** → §5.5 审批门在"蒸馏产物写入"上的现成交互形态（pending/diff/approve，重启存活）。
5. **project-local skills + `skills trust` + 扫描隔离 + `skills.create_dir`** → §5.4 "目标私有技能存储与装载"的最接近参照（作用域隔离、需显式信任、curator 不动）；叠加 **cron `skills:` 引用保护** = "被调度任务引用的技能不得被自动清理"。
6. **`on_session_end`（外部 provider 的真会话边界抽取）** → §5.4 "Run 收尾蒸馏"的钩子形态参照（`agent/memory_provider.py:183`、`agent/memory_manager.py:629`）。

## 5. 不确定处 / 未读清单

- **本克隆 depth=1**，仅 `ad2b705b` 一个可见提交，未 `--unshallow`，未核对上述机制的历史演进（例如 curator/watchdog 的引入时间）。
- **未在运行时验证**：所有结论来自文档与静态源码走读，没有实跑 cron 崩溃恢复 / watchdog 开火 / curator 演练。
- 未读源码：`gateway/`、`cron/scheduler.py` 主循环全文、`tools/memory_tool*.py`、`tools/skill_*.py`、`agent/curator.py` 实现细节、第三方记忆 provider。
- 文档说后台 review "约每 10 个 agent 轮次创建一次 agent-created 技能"（curator.md §What agent-created means）——该数字与两个默认 nudge_interval=10 一致，但**触发计数器一个是用户轮次、一个是工具迭代**，"每 10 轮"的精确口径以代码为准，文档未逐字对应。
- 系统提示中的技能目录在会话中**冻结到下次 compaction**（skills.md §Skills added during a conversation），本项目"每期 Run 装载"需自行决定是否沿用该缓存友好策略。
- hermes 侧**没有**"记忆 facts 分类型（goal/work_summary）、检索打分、生命周期白名单迁移"这类结构（§5.4 SEPM/CALM 主线在 hermes 中**未找到对应**），不得据 hermes 现状宣称该设计已有先例。
