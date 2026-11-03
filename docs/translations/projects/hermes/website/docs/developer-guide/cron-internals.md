---
sidebar_position: 11
title: "Cron 内部机制"
description: "Hermes 如何存储、排程、编辑、暂停、加载 skill 并投递 cron 任务"
---

# Cron 内部机制（Cron Internals）

> 来源：https://github.com/NousResearch/hermes-agent/blob/main/website/docs/developer-guide/cron-internals.md
> 原文：oss-repos/hermes-agent/website/docs/developer-guide/cron-internals.md
> 翻译日期：2026-11-03 ｜ 范围：全文 ｜ 方式：机器翻译初稿，未经人工校对
> 引用于：docs/essay-study/hermes-2026.md、docs/brief-plan.md §3

cron 子系统提供定时任务执行能力——从简单的一次性延迟，到带 skill 注入、跨平台投递的周期性 cron 表达式任务。

## 目录

- [关键文件](#关键文件)
- [调度模型](#调度模型)
- [每任务时区](#每任务时区)
- [任务存储](#任务存储)
- [调度器运行时](#调度器运行时)
- [Skill 加持的任务](#skill-加持的任务)
- [投递模型](#投递模型)
- [递归防护](#递归防护)
- [加锁](#加锁)
- [CLI 接口](#cli-接口)
- [相关文档](#相关文档)

## 关键文件

| 文件 | 用途 |
|------|---------|
| `cron/jobs.py` | 任务模型、存储、对 `jobs.json` 的原子读写 |
| `cron/jobs_time.py` | 每任务的 `timezone` / `grace_minutes` 旋钮：校验、容错读取、到期扫描时区 |
| `cron/scheduler.py` | 调度器循环——到期任务检测、执行、重复次数追踪 |
| `tools/cronjob_tools.py` | 面向模型的 `cronjob_manage` 工具注册与处理器 |
| `gateway/run.py` | gateway 集成——长驻循环中的 cron tick |
| `hermes_cli/cron.py` | CLI 的 `hermes cron` 子命令 |

## 调度模型

支持四种调度格式：

| 格式 | 示例 | 行为 |
|--------|--------|----------|
| **相对延迟** | `30m`、`2h`、`1d` | 一次性，指定时长后触发 |
| **固定间隔** | `every 2h`、`every 30m` | 周期性，按固定间隔触发 |
| **Cron 表达式** | `0 9 * * *` | 标准 5 字段 cron 语法（分、时、日、月、周几） |
| **ISO 时间戳** | `2025-01-15T09:00:00` | 一次性，在精确时刻触发 |

面向模型的接口只有一个 `cronjob_manage` 工具，操作采用 action 风格：`create`、`list`、`update`、`pause`、`resume`、`run`、`remove`。

## 每任务时区

`compute_next_run(schedule, last_run_at, *, timezone=...)` 按 *任务 pin → profile `timezone` → 基准偏移* 的顺序解析时区，并且**每一个**推进 `next_run_at` 的调用方都要传入该任务的 pin（推进点、认领路径、resume/re-arm、恢复路径、以及配额/不可达规划器）。漏掉一处的表现就是一次爆发式重跑或一个被跳过的时槽，因为存储的时刻与表达式会被放在不同时区里解释。

分发路径和计算路径一样需要这个 pin。`_evaluate_due_job` 用 `_ensure_aware(raw, zone_for_job(job))` 构造它的 `_DueJob`，从而让所有下游判定都拿到该任务的时钟；带 pin 时区的任务会**完全跳过 `_repair_timezone_shifted_cron`**。那个修复是给「跟随 profile 时区、跨时区变更而移动」的任务准备的：对 pin 任务来说，它存储的偏移本来就合法地不同于 profile，于是修复里的挂钟比较（`_stored_wall_clock_is_future`）会把一个本该到期的 occurrence 读成「仍在未来」，进而重新锚定到下一个——任务就悄悄地永远不触发了。这就是为什么只修 `compute_next_run` 不够。

`timezone` 与 `grace_minutes` 是记录的顶层字段（不在 `schedule` 里面），在创建和更新两个入口都由 `jobs_time.normalize_*` 校验。持久化值损坏时会降级为 profile 时区，每个值只告警一次——60 秒一次的扫描不能因为一条坏记录就挂掉。不需要迁移：这些键在旧存储里根本不存在，所有读取方都用 `.get()`。

## 任务存储

任务存放在 `~/.hermes/cron/jobs.json`，写入采用原子语义（先写临时文件，再 rename）。每条任务记录包含：

```json
{
  "id": "a1b2c3d4e5f6",
  "name": "Daily briefing",
  "prompt": "Summarize today's AI news and funding rounds",
  "schedule": {
    "kind": "cron",
    "expr": "0 9 * * *",
    "display": "0 9 * * *"
  },
  "skills": ["ai-funding-daily-report"],
  "deliver": "telegram:-1001234567890",
  "repeat": {
    "times": null,
    "completed": 42
  },
  "state": "scheduled",
  "enabled": true,
  "next_run_at": "2025-01-16T09:00:00Z",
  "last_run_at": "2025-01-15T09:00:00Z",
  "last_status": "ok",
  "created_at": "2025-01-01T00:00:00Z",
  "model": null,
  "provider": null,
  "script": null
}
```

### `last_status` 字面量

`last_status` 由 `cron.jobs.mark_job_run` 在一次运行结束时写入；对于走队列投递的运行，还会被下面的投递回写改写一次。每个渲染端（`hermes cron list` / `doctor`、`cronjob_manage` 工具、web dashboard 徽标、Desktop routine 检查器）都显式映射每一个字面量——消费方绝不能用 `== "ok"` 来判断「用户拿到结果了」：

| 字面量 | 含义 | 详情字段 |
|---------|---------|--------------|
| `ok` | Agent 运行成功，且（如果有目标）投递已确认 | — |
| `delivery_queued` | Agent 运行成功；其发送已交给持久化投递队列，尚未落定（过渡态） | `last_delivery_queued` |
| `error` | Agent 运行失败 | `last_error` |
| `delivery_failed` | Agent 运行成功，但输出从未到达目标 | `last_delivery_error`（此时 `last_error` 为 `null`） |
| `blocked_config` | 派发前校验拒绝，没有消耗这次运行 | `last_error` |

### 队列投递生命周期与回写

带投递目标且带 `execution_id` 的 agent 运行不会内联发送：它把内容交给 `cron/delivery_queue.py`（profile 的 `cron/deliveries.db`，以 `execution_id` 为键），并记账 `last_status = "delivery_queued"`、台账 `delivery_outcome = "queued"`。gateway 的一次家务实务 tick 会通过它活着的 adapter 把队列排空（`scheduler.drain_delivery_queue`）；每一行至多被认领一次（`pending → delivering → delivered | failed | suppressed`）。认领方 gateway 如果死在发送中途，该行会被 fence 成 `unknown`，且永不重试。

随后 `cron/delivery_outcome.py::settle_queued_delivery` 把终局结果回写到当初入队的那次运行上：

| 队列行 | 台账 `delivery_outcome` | 任务 `last_status` / `last_delivery_error` |
|---|---|---|
| `delivered` | `delivered` | `ok` / `null` |
| `suppressed` | `suppressed` | `ok` / `null` |
| `failed` | `failed` | `delivery_failed` / 发送错误 |
| `unknown` | `failed` | `delivery_failed` / 「发送结果未知且未重试」 |

两侧都会调用它：排空方在把一行终局化之后调用，运行方在自己记账之后也调用，因为排空可能先于运行的 `mark_job_run` 落盘完成。每次写入都以 `execution_id` 做 fence（该次运行必须仍是此任务最新的台账尝试、最新的已记录完成），因此这个调用是幂等的，绝不会改写更晚一次运行的状态；台账只会把 `queued` 推向某个终局。在 gateway 排空该行之前，`last_status` 一直是 `delivery_queued`，`hermes cron list` 显示「已结束；投递仍在进行中」。

### 任务生命周期状态

| 状态 | 含义 |
|-------|---------|
| `scheduled` | 生效中，将在下一次排定时间触发 |
| `paused` | 已挂起——恢复前不会触发 |
| `completed` | 重复次数用尽，或一次性任务已触发 |
| `running` | 正在执行（瞬时状态） |

### 向后兼容

旧任务可能只有一个 `skill` 字段而不是 `skills` 数组。调度器在加载时做归一化——单个 `skill` 会被提升为 `skills: [skill]`。

## 调度器运行时

### Tick 循环

调度器按周期 tick 运行（默认每 60 秒一次）：

```text
tick()
  1. Acquire scheduler lock (prevents overlapping ticks)
  2. Load all jobs from jobs.json
  3. Filter to due jobs (next_run <= now AND state == "scheduled")
  4. For each due job:
     a. Set state to "running"
     b. Create fresh AIAgent session (no conversation history)
     c. Load attached skills in order (injected as user messages)
     d. Run the job prompt through the agent
     e. Deliver the response to the configured target
     f. Update run_count, compute next_run
     g. If repeat count exhausted → state = "completed"
     h. Otherwise → state = "scheduled"
  5. Write updated jobs back to jobs.json
  6. Release scheduler lock
```

### Missed-occurrence 契约（重启缺口）

周期性任务遵循 **每个 occurrence 至多执行一次，且每个 occurrence 都有交代**：它要么跑了（带一条携带其 `scheduled_instant` 的执行记录），要么它的跳过被记下原因。occurrence 绝不会被悄悄丢掉。机制如下，顺序即到期扫描应用它们的顺序（`cron/jobs.py::_evaluate_due_job`）：

1. **派发前的推进是暂定的。** `tick()` 在派发*之前*就把 `next_run_at` 推过了到期的 occurrence，这样运行中途崩溃不会导致每次重启都重新触发一次。
   - 但这样会留下一个窗口——已推进、却还没有 fire claim（解释器收尾、执行器拒绝接活、`SIGKILL`）。于是到期扫描在同一次保存里给记录盖上 `pending_slot = {scheduled_at, at, by}`。
   - 清除时机：`claim_job_for_fire`（此后才可能存在副作用的时点）和 `mark_job_run` 会清掉它；显式改写 `schedule` / `next_run_at` / `enabled` / `state`（编辑、暂停、恢复、立即运行）也会丢弃它。

2. **只恢复一次。** 后续扫描若发现某个 `pending_slot` 的属主已可证明消失（不是本进程、且该任务不在本进程的 running 集合里；或者是另一个进程，且已越过 300 秒 fire-claim 租约，或其 pid 已死），就把 `scheduled_at` 作为 `next_run_at` 放回去、丢掉戳记，并记一条 WARNING（`cron/occurrences.py::unclaimed_pending_slot`）。每个丢失的 occurrence 至多发生一次——恢复回来的时刻随后会像任何其他逾期时槽一样走下面的普通规则，因此绝不会出现 N 个时槽的重放。

3. **已触发过 → 绝不再触发。** 在任何东西到期之前，`completed_occurrence()` 都会先查执行台账，看有没有 `scheduled_instant` 完全相同的 `completed` 行；重启前跑过的时槽会直接推进、不再触发。`failed` / `unknown` 行不算完成；一行 `completed` 若其 `finished_at`（否则 `claimed_at`）早于它被盖戳的那个时刻，同样不算——一次运行无法证明一个当时还没发生的 occurrence。没有可比时间戳的行继续计数。
   occurrence 身份只有在到期后才可被认领：`claim_job_for_fire` 会丢弃仍在未来的 `scheduled_instant`，因此一次脱离 tick 的触发（dashboard 手动触发、webhook、租约回收、失火兜底）会以「零 occurrence」方式运行，而不是消耗下一个时槽。

4. **宽限期内迟到 → 迟到触发。** 宽限期 = 周期的一半，夹在 `[120 s, 2 h]`（`_compute_grace_seconds`）；这次派发会被盖上 `last_dispatch.kind = late`。

5. **超出宽限期 → 折叠积压、只触发一次**（`kind = catch_up`）；若运维设置了 `cron.catch_up_missed: false`（计划内停机），则带原因记录地跳过。一次性任务超过 120 秒宽限期后会带诊断信息退役，绝不复活。

6. **暂停 / 禁用 / 终局任务永不触发**；到期扫描会在上述任何规则之前丢弃它们，暂停/恢复也会清掉任何 pending 时槽。不过，*在暂停期间*到期的周期性 occurrence 并没有丢：`resume_job` 会把已过期的存储 `next_run_at` 保留为到期时刻，而不是从当下重新锚定（并记录它这么做了），于是恢复后的第一个 tick 会对它应用规则 3–5——一次迟到/补跑，或一条有记录的跳过。一次性任务和未来的时刻则在恢复时从当下重新计算。

同一套存储字段驱动所有拓扑：独立的 `hermes -p X gateway run` 和由宿主 gateway 服务的 profile（`_start_multiplex` 在 `_profile_cron_scope` 下逐个 tick 各个 home）评估的是完全相同的记录。每台主机一个 gateway 进程会 tick *每一个* profile 的存储——`gateway.multiplex_profiles` 管的是 adapter，不是 cron——而每次运行的记账（在途认领、并行 worker 池、陈旧代码让位决策）以 profile home 为键，所以两个 profile 可以携带同名任务而不冲突。自己跑 gateway 的 profile 会在每次 tick 时被跳过，因此两个进程绝不会争抢它的存储，它的投递也始终从它自己的活 adapter 出去。

**运行期间的 fire-claim 租约。** 触发中的运行持有 `fire_claim = {at, by}`，一个心跳线程每 60 秒刷新一次 `at`（租约 300 秒）。心跳采样若读到该 claim 属于别人，会先重新采样一次才计数：只有确认丢失才会取消在途运行。即便如此，运行结果也是在完成时对照存储裁定的，而不是对照那个闩锁——存储仍认可的 claim 会记录该次运行的真实结果（`ok`，或真实错误），而真正被重新接管的 claim 会丢弃过期结果、绝不覆盖新属主。因此，`Interrupted by shutdown before terminal completion.` 只在真实的传输层取消（gateway drain）停掉一个仍持有其 claim 的运行时才会被记录。

### Gateway 集成

在 gateway 模式下，cron 的**触发器**（决定到期任务*何时*触发的那一部分，即「Axis B」）通过可插拔的 `CronScheduler` provider 选取。gateway 调用 `resolve_cron_scheduler()`（`cron/scheduler_provider.py`），在一条专门的后台线程里运行解析出来的 provider 的 `start()`，与另一条 gateway 家务线程并行。

当前 provider 由 `cron.provider` 配置项选择：

- **留空（默认）** → 内置的 `InProcessCronScheduler`，它跑历史上的进程内循环，每 60 秒调用一次 `scheduler.tick()`。这与 provider 出现之前的行为逐字节一致。
- **指定 provider 名**（例如 `chronos`，一个面向 scale-to-zero 部署的托管 cron provider）→ 从 `plugins/cron_providers/<name>/` 或 `$HERMES_HOME/plugins/<name>/` 发现。

如果指定的 provider 缺失、加载失败，或报告 `is_available() == False`，解析器会带一条警告回落到内置实现——**cron 永远不会没有触发器。** 内置 provider 位于 core（`cron/scheduler_provider.py`），不在 `plugins/` 里，所以这个回落不可能被误删。

「触发」（firing）*意味着什么*（任务执行 + 投递）没有变化，且由所有 provider 共享——它留在 `scheduler.run_job()` / `scheduler._deliver_result()` 里。provider 只控制触发器，从不控制执行。

一个 ticker 如果在其运行期间代码被更新（启动时的 revision ≠ 磁盘上的 revision），它只会在另一个进程持有 gateway 运行时锁时，把这次 tick 让给一个真正接得住它的 gateway：持锁者必须是一个活着的 gateway，其 `gateway_state.json` 心跳是新鲜的，且它盖戳的 `code_sha` 等于磁盘上的 revision。如果持锁的进程自己还在跑更新前的代码——`hermes update` 之后单 gateway 的常见情况——那它永远不算「新鲜 gateway」，于是 ticker 继续派发，而不是把每次 tick 都让给一个不存在的对象。

在 CLI 模式下，cron 任务只在运行 `hermes cron` 命令或处于活跃 CLI 会话期间才会触发。

gateway 接管运行时的升级说明（已废弃的 `cron.bot_chat_delivery_timeout_seconds` 键、遗留的 `cron/bot_chat_pending/` 记录、以及被切换重启打断的运行）见 [Updating](../getting-started/updating.md#upgrading-to-the-gateway-owned-session-runtime)。

### 面向 scale-to-zero 的托管 cron（Chronos）

托管 gateway 可以跑 **Chronos** provider（`cron.provider: chronos`）来替代内置 ticker。Chronos 让空闲的 gateway 可以**缩容到零**、同时仍然触发 cron 任务：它不再跑 60 秒的进程内循环（那会一直占着进程不放），而是请 Nous 基础设施在每个任务真实的下一次触发时刻，恰好武装**一个托管的一次性触发**。到点时 Nous 通过带鉴权的 webhook（`POST /api/cron/fire`）回调 gateway；gateway 用与内置实现相同的 `run_one_job` 路径跑该任务，然后为下一个一次性触发重新武装。两次触发之间进程可以完全停掉——它只在真正的 fire 时醒来，绝不会被周期性定时器唤醒。

流程（托管调度器由 Nous 提供；agent 不持有任何调度器凭据）：

```
create/update a cron job
  → Chronos asks Nous to arm a one-shot at the job's next_run_at
      (authenticated with the agent's existing Nous token)
  → at fire time Nous calls the gateway: POST {callback_url}/api/cron/fire
      (authenticated with a short-lived, purpose-scoped Nous-minted JWT)
  → the gateway verifies the token, claims the job (store compare-and-set so
    multi-replica deployments fire at-most-once), runs it, and re-arms the next
    one-shot
```

配置（全部非机密；托管 agent 上由 Nous 在开通时设置）：

| 键 | 含义 |
|---|---|
| `cron.provider` | 设为 `chronos` 以启用（留空 = 内置 ticker） |
| `cron.chronos.portal_url` | Nous 基础 URL（武装 + fire token 签发方） |
| `cron.chronos.callback_url` | gateway 自己接收 fire 回调的公网基础 URL |
| `cron.chronos.expected_audience` | 本 agent 的 fire token audience |
| `cron.chronos.nas_jwks_url` | 校验入站 fire token 的密钥集 |

如果 Chronos 配置错误，或 agent 没有登录 Nous，`resolve_cron_scheduler()` 会回落到内置 ticker（记一条警告）——cron 不会失去触发器。周期性任务每次触发后重新武装；`repeat`-N 任务在次数用尽时干净地停止（不留孤儿一次性触发）。完整的 agent ↔ Nous 线协议见 [Chronos 托管 cron 契约](chronos-managed-cron-contract.md)。

### 新会话隔离

每个 cron 任务都跑在一个全新的 agent 会话里：

- 没有上一次运行的对话历史
- 没有上一次 cron 执行的记忆（持久记忆——MEMORY.md / USER.md——会照常加载，和其他 agent 运行一样，因此长期偏好与事实会延续下来；但单次运行的对话上下文不会）
- prompt 必须自包含——cron 任务无法反问澄清
- `cronjob` 工具集被禁用（递归防护）

## Skill 加持的任务

cron 任务可以通过 `skills` 字段挂一个或多个 skill。执行时：

1. 按指定顺序加载 skill
2. 每个 skill 的 SKILL.md 内容作为上下文注入
3. 任务的 prompt 追加为任务指令
4. agent 处理合并后的 skill 上下文 + prompt

这样就能复用经过测试的工作流，而不必把整套指令粘进 cron prompt。例如：

```
Create a daily funding report → attach "ai-funding-daily-report" skill
```

### 脚本加持的任务

任务也可以通过 `script` 字段挂一个 Python 脚本。脚本在每一轮 agent 回合*之前*运行，其 stdout 作为上下文注入 prompt。这支持数据采集与变更检测类模式：

```python
# ~/.hermes/scripts/check_competitors.py
import requests, json
# Fetch competitor release notes, diff against last run
# Print summary to stdout — agent analyzes and reports
```

脚本超时默认 3600 秒（1 小时）。`_get_script_timeout()` 通过三层链解析上限：

1. **模块级覆盖** —— `_SCRIPT_TIMEOUT`（供测试 / monkeypatch 用）。只有当它与默认值不同时才会生效。
2. **环境变量** —— `HERMES_CRON_SCRIPT_TIMEOUT`
3. **配置** —— `config.yaml` 中的 `cron.script_timeout_seconds`（经 `load_config()` 读取）
4. **默认值** —— 3600 秒（1 小时）

这个超时只约束**运行前的脚本**，不约束 agent。基于 skill / LLM 驱动的任务跑在另一套基于*不活跃时长*的预算上（`HERMES_CRON_TIMEOUT`，默认 600 秒空闲，`0` = 不限）——只要它们持续调用工具或流式输出 token，就可以跑上几个小时，只有在配置的空闲期内毫无活动之后才会被杀掉。在 Python 单调时钟不计入挂起的平台（macOS 与 Linux）上，宿主睡眠的时间不计入该空闲期；Windows 行为不变。脚本被派发到一个常驻线程池（不占着 tick 锁），所以一个长跑脚本不会阻塞其他到期任务的触发。

超时或属主取消时，`cron.scheduler_script` 走共享的 `agent.deadline.kill_process_tree` 硬杀路径。在 POSIX 上，它会先短暂暂停并重新扫描存活的进程树，再向后代及其父进程发信号，包括那些处在独立会话、没有继承输出管道的子进程。这闭合了「快照之后 fork」的竞态。暂停等待是有界的；发现或权限失败时仍只做尽力而为的组清理，而不是沙箱级保证。任何被清理停掉的目标，若终止失败会被恢复运行；已停掉的目标保持原样。显式的优雅信号不会挂起接收方。Windows 继续使用 `taskkill /F /T`。

### Provider 恢复

`run_job()` 把用户配置的 fallback provider 与凭据池传进 `AIAgent` 实例：

- **Fallback provider** —— 从 `config.yaml` 读取 `fallback_providers`（列表）或 `fallback_model`（遗留字典），与 gateway 的 `_load_fallback_model()` 模式一致。作为 `fallback_model=` 传给 `AIAgent.__init__`，由它把两种格式归一化成一条 fallback 链。**仅限未 pin 的任务：** `_job_fallback_chain()` 对自带 `provider`、`model` 或 `base_url` 的任务不返回任何链，同一个答案也喂给 `_resolve_job_runtime()` 里的凭据解析遍历、派发前的键检查，以及运行中的阶梯，因此 pin 过的任务绝不会落到全局链的条目上（#100437）。它与 pin 过的委派子任务共享 `hermes_cli.fallback_config.scoped_fallback_chain()`。
- **凭据池** —— 用解析出的运行时 provider 名，通过 `load_pool(provider)` 从 `agent.credential_pool` 加载。只有当池里有凭据时才传（`pool.has_credentials()`）。在 429 / 限流错误时支持同 provider 的密钥轮转。

这与 gateway 的行为一致——没有它，cron agent 一旦碰上限流就会直接失败，而不会尝试恢复。

## 投递模型

cron 任务的结果可以投递到任何受支持的平台。

只写平台名（`slack`、`telegram`……）会投递到该平台配置的**主频道**。要指定**具体**目标，就在冒号后面追加目标：`platform:<target>`。目标在触发时才解析（而不是创建任务时），所以任务可以先指定一个尚未连接的平台上的目的地，等它上线后再开始投递。

多数平台还接受把可选的 thread/topic 作为第三段：`platform:<chat_id>:<thread_id>`。

| 目标 | 语法 | 示例 |
|--------|--------|---------|
| 来源聊天 | `origin` | 投递到创建该任务的那个聊天 |
| 本地文件 | `local` | 保存到 `~/.hermes/cron/output/` |
| Telegram | `telegram`、`telegram:<chat_id>`、`telegram:<chat_id>:<thread_id>`、`telegram:@username` | `telegram:-1001234567890:17585` |
| Discord | `discord`、`discord:#channel`、`discord:<channel_id>`、`discord:<channel_id>:<thread_id>` | `discord:#engineering` |
| Slack | `slack`、`slack:#channel`、`slack:<channel_id>`、`slack:<channel_id>:<thread_ts>` | `slack:#engineering` |
| Matrix | `matrix`、`matrix:<!room_id:server>`、`matrix:<@user:server>` | `matrix:!abc123:example.org` |
| 飞书 | `feishu`、`feishu:<chat_id>`、`feishu:<chat_id>:<thread_id>` | `feishu:oc_abc123def` |
| WhatsApp | `whatsapp`、`whatsapp:<jid>`、`whatsapp:+<E.164>` | `whatsapp:123456@g.us` |
| Signal | `signal`、`signal:group:<id>`、`signal:+<E.164>` | `signal:group:aBcD==` |
| SMS | `sms`、`sms:+<E.164>` | `sms:+<E.164 number>` |
| Email | `email`、`email:<address>` | `email:alerts@example.com` |
| 微信 | `weixin`、`weixin:<wxid>` | `weixin:wxid_abc123` |
| Mattermost | `mattermost` 或 `mattermost:<channel_id>` | 裸名投递到 Mattermost 主频道 |
| Home Assistant（插件） | `homeassistant` 或 `homeassistant:<notify target>` | 裸名投递到 `HASS_HOME_CHANNEL`；需要 `homeassistant` 目录插件 |
| 钉钉 | `dingtalk` 或 `dingtalk:<chat_id>` | 裸名投递到钉钉 |
| 企业微信 | `wecom` 或 `wecom:<chat_id>` | 裸名投递到企业微信 |
| BlueBubbles | `bluebubbles` 或 `bluebubbles:<chat_guid>` | 裸名经 BlueBubbles 投递到 iMessage |
| QQ 机器人 | `qqbot` 或 `qqbot:<chat_id>` | 裸名经官方 API v2 投递到 QQ（腾讯） |
| Bot Chat | `bot-chat` 或 `bot-chat:<profile>` | 注入本地某个 profile 的权威 Bot Chat（由 bot 回应） |

第一组平台有显式且校验过的目标语法——具名频道（`#channel`）、topic/thread、房间/用户 ID、群 ID 或电话号码。其余平台接受通用的 `platform:<chat_id>` 形式（冒号后的值原样用作目标 ID）；裸平台名始终投递到主频道。

**具名频道**（`slack:#engineering`、`discord:#engineering`，或友好名 `slack:engineering`）会对照 gateway 从已连接 adapter 构建的频道目录解析，所以 gateway 必须先发现该频道，名字解析才能成功；原始 ID（`slack:C0123ABCD45`）始终可用。

**Telegram topic** 用 `telegram:<chat_id>:<thread_id>`（例如 `telegram:-1001234567890:17585`）。**Slack thread** 的第三段是父消息的 `thread_ts`（例如 `slack:C0123ABCD45:1700000000.000100`），因此只在回复既有消息之下的内容时适用。

**Bot Chat**（`bot-chat`、`bot-chat:<profile>`）是机器本地的伪平台，不是 gateway adapter。具备收件箱能力的权威活属主会立即获得持久准入（无论空闲还是忙碌）；只有该属主会执行进来的这一轮。`scheduler_delivery._deliver_to_bot_chat` 用 `get_profile_dir` 或任务当前的 `get_hermes_home` 解析目标，由来源 home、任务 ID、持久 `execution_id` 与目标 home 推导回执 ID，并在发现属主之前先查回执。尚无 Bot Chat 的 profile 会在首次投递时由权威方创建一个（已废弃的 CLI 通道那套 `--create-if-missing` 语义）。

这里没有本地 CLI 兜底：如果没有在跑的权威方，该次运行会被记为 `delivery_failed`，原因写进 `last_delivery_error`，输出保留在 `hermes cron runs` 之下；它不会自动重投，调度器也永远不会变成该 profile 存储的第二个写入方。投递是一次真实的入站回合，不是会话记录的镜像。入队/已认领的回执会把回执 ID 填进 `last_delivery_queued`。投递聚合器把准入通知排除在真实错误之外，并记执行 `delivery_outcome=queued`；成功的任务用 `last_status=delivery_queued`。混合目标上的真实错误优先判为 failed，同时保留入队回执元数据。目标 profile 的持久回执是终局完成的权威依据。「已入队」是历史上的准入结果，不是投递成功的证明。

当 Bot Chat 的发送走的是 gateway 投递队列（一次 agent 运行）时，上面那套回写会在排空方的发送返回后落定该 cron 运行：`ok` / `delivered` 此时意味着目标的权威方**接受**了这一轮，而 `last_delivery_queued` 保留着那些 Bot Chat 回合可能仍在运行的回执 ID。内联完成的 Bot Chat 投递（`no_agent` 任务，或只发 Bot Chat 的外部 worker）不在队列上，因此它的运行保持 `last_status=delivery_queued` / `delivery_outcome=queued`，不会有任何东西把后续的回执完成写回 cron 历史。bot-chat 目标被排除在 `all` 和凭据预检之外。只发 bot-chat 的外部 worker 绕过 gateway 投递队列；混合的外部 worker 目标仍走 gateway 交接。

### 响应包裹

默认（`cron.wrap_response: true`）下，cron 投递会被包裹为：

- 一个标明 cron 任务名与任务的头部
- 一个注明 agent 在对话里看不到这条已投递消息的尾部

cron 响应中的 `[SILENT]` 前缀会完全抑制投递——适用于只需写文件或产生副作用的任务。

### 会话隔离

Cron 投递**不会**镜像进 gateway 的会话对话历史。它们只存在于该 cron 任务自己的会话里。这避免了目标聊天对话中消息交替次序被破坏的问题。

## 递归防护

Cron 运行的会话禁用了 `cronjob` 工具集。这防止了：

- 定时任务创建新的 cron 任务
- 可能爆炸式消耗 token 的递归调度
- 在任务内部意外改动任务的调度

## 加锁

调度器使用跨进程的文件锁（Unix 上 `fcntl.flock`，Windows 上 `msvcrt.locking`），防止重叠的 tick 把同一批到期任务执行两次——即使一方是 gateway 的进程内 ticker、另一方是独立的 `hermes cron` 或手动 `tick()` 调用。如果拿不到锁，`tick()` 立即返回 0。

### 陈旧代码让位

在拿到 tick 锁之前，一个代码在它运行期间被更新过的 gateway（启动 revision ≠ 磁盘 revision），会在另一个进程持有 gateway 运行时锁时让出这次 tick——更新鲜的 gateway 的 ticker 会接管派发，而陈旧的那个不能带着混杂的 `sys.modules` 与之赛跑。让位会以 `CronTickYielded` 抛出，并作为 ticker 的最后一次错误持久化，于是 `hermes cron status` 会报告 **「Gateway is running STALE code — its cron ticker yields every tick and fires NOTHING」**，附上两个 revision 和重启命令——尽管存活心跳仍在持续刷新。`hermes update` 把这个环闭上：一个被更新后舰队版本矩阵证明已陈旧的 gateway，会被交给先 drain 的 `request_restart` 路径（SIGUSR1），而不是留在原地继续跑；受监管的 gateway 会在新代码上重新拉起，裸的 `gateway run` 则被停掉并列在「Restart manually」之下。

## CLI 接口

`hermes cron` CLI 提供直接的任务管理：

```bash
hermes cron list                    # Show all jobs
hermes cron create                  # Interactive job creation (alias: add)
hermes cron edit <job_id>           # Edit job configuration
hermes cron pause <job_id>          # Pause a running job
hermes cron resume <job_id>         # Resume a paused job
hermes cron run <job_id>            # Trigger immediate execution
hermes cron remove <job_id>         # Delete a job
```

## 相关文档

- [Cron 功能指南](../user-guide/features/cron.md)
- [Gateway 内部机制](./gateway-internals.md)
- [Agent 循环内部机制](./agent-loop.md)

参考文献从略，见原文。
