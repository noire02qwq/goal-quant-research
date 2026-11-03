---
sidebar_position: 3
title: "Curator"
description: "agent 创建的 skill 的后台维护 —— 使用追踪、过期、归档与 LLM 驱动的审查"
---

# Curator（策展器 / 后台 skill 维护）

> 来源：https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/curator.md
> 原文：oss-repos/hermes-agent/website/docs/user-guide/features/curator.md
> 翻译日期：2026-11-03 ｜ 范围：全文 ｜ 方式：机器翻译初稿，未经人工校对
> 引用于：docs/essay-study/hermes-2026.md、docs/brief-plan.md §3

## 目录

- [它怎么运行](#它怎么运行)
- [配置](#配置)
  - [用更便宜的 aux 模型跑审查](#用更便宜的-aux-模型跑审查)
- [CLI](#cli)
- [备份与回滚](#备份与回滚)
- [审计账本与单条回滚](#审计账本与单条回滚)
- [归档 TTL 清理](#归档-ttl-清理)
- [「agent 创建」是什么意思](#agent-创建是什么意思)
  - [收编未纳管的 skill](#收编未纳管的-skill)
- [Pin 一个 skill](#pin-一个-skill)
- [Lock 一个 skill](#lock-一个-skill)
- [使用遥测](#使用遥测)
- [每次运行的报告](#每次运行的报告)
  - [摘要中的改名映射](#摘要中的改名映射)
- [恢复一个已归档的 skill](#恢复一个已归档的-skill)
- [按环境关闭](#按环境关闭)
- [另见](#另见)

curator 是一道针对 **agent 创建的 skill** 的后台维护流程。它追踪每个 skill 被查看、使用与修补的频率，把长期未用的 skill 沿 `active → stale → archived` 状态推进，并周期性地产生一个短小的辅助模型审查，提出合并建议或修补漂移。

它存在的意义是：经由[自我改进闭环](./skills.md#agent-管理的-skillskill_manage-工具)创建的 skill 不会永远堆下去。每当 agent 解决一个新问题并存下一个 skill，它就落进 `~/.hermes/skills/`。没有维护的话，最终你会得到几十个狭窄、近乎重复的 skill，既污染目录又浪费 token。

默认情况下 curator 只管理 agent 创建的 skill。设 `curator.prune_builtins: true` 后，它也可以在 `archive_after_days` 天未使用之后归档**未使用的随附内置 skill**（随仓库发布）；这是选择性开启的，因为随发 skill 从 `skills_list` 里悄然消失很容易被误当成安装损坏。从 [agentskills.io](https://agentskills.io) 的 hub 安装的 skill 则始终是禁区。curator 也**从不自动删除** —— 最坏的结果是归档进 `~/.hermes/skills/.archive/`，而那是可恢复的。

跟踪 [issue #7816](https://github.com/NousResearch/hermes-agent/issues/7816)。

## 它怎么运行

curator 由空闲检查触发，而不是 cron 任务。在 CLI 会话开始时、gateway 的日常维护中（本地 Desktop 也涵盖在内，因为它挂到 gateway 上），以及 `hermes serve` 的维护定时器上，Hermes 会检查是否同时满足：

1. 距离上一次 curator 运行已过去足够时间（`interval_hours`，默认 **7 天**），且
2. agent 已经空闲了足够久（`min_idle_hours`，默认 **2 小时**）。

`hermes serve` / `hermes dashboard` 后端（例如远程 Desktop 连接）共用既有的每小时维护定时器（首次轮询在 90 秒之后），与 cron 任务无关。它们从进程启动、以及同一 profile 中最近一次聊天活动来度量空闲时长；会话关闭或被回收后仍保留该活动时间戳，并且当该 profile 正有轮次在跑时跳过 curator。一个已连接但空闲的窗口不会阻塞维护。同一 profile 若有正在运行的消息 gateway，则由它接管这些杂务。

定时器服务于其后端所属的 profile。进行中的维护跑在工作线程里；关闭后端不会协作式地中断那一轮。为同一 profile 启动多个独立的 serve 进程，仍可能与 curator 的间隔检查发生竞争。

如果两条都满足，它会产生一个 `AIAgent` 的后台 fork —— 与记忆/skill 自我改进提醒所用的是同一套模式。fork 跑在自己的 prompt cache 里，绝不触碰活跃对话。

:::info 首次运行的行为
在全新安装上（或者一个早于 curator 的旧安装在 `hermes update` 后第一次走到定时点），curator **不会立即运行**。第一次观察会把 `last_run_at` 播种为「现在」，并把首次真正的检查推迟整整一个 `interval_hours`。这样你有一个完整周期去审视自己的 skill 库、把重要的钉住（pin），或者干脆退出，然后 curator 才会碰它。

如果你想在它真正运行之前看看 curator *会*做什么，运行 `hermes curator run --dry-run` —— 它会产出同样的审查报告，但不改动 skill 库。
:::

一次运行分两个阶段：

1. **自动状态转移**（确定性的，不涉及 LLM）。`stale_after_days`（14）天未使用的 skill 变成 `stale`；`archive_after_days`（30）天未使用的 skill 被移入 `~/.hermes/skills/.archive/`。这是始终开启的修剪行为 —— 只要 curator 启用就会运行，没有辅助模型开销。
   - **已 pin 的 skill** 以及**任何 cron 任务引用的 skill**（包括已暂停/已禁用的任务）会被整体跳过 —— 在自动转移上等同于 pin，这样一个缓慢或暂停的排程无法把某个任务正用着的 skill 归档掉。合并（consolidation）在重组伞状 skill 时也会改写 cron 的 skill 引用。
   - **从未用过的 skill**（`use_count == 0`）有宽限下限：它们至少要活到 `stale_after_days` 天才会被归档。零使用是「没有证据」，不是「这个 skill 可有可无」的证明。
2. **LLM 合并**（单次辅助模型流程，迭代上限很高 —— 一轮完整的策展扫描通常要 50–100 次 API 调用）—— **默认关闭**。当 `curator.consolidate: true` 时，fork 出来的 agent 会巡视 agent 创建的 skill，可以用 `skill_view` 读取其中任何一个，并逐个决定：保留、修补（经由 `skill_manage`）、把重叠的 skill 合并成类级伞状 skill，或归档（经由 `skill_manage action=delete` 并给出 `absorbed_into` 目标 —— 这一流程没有终端界面）。给它的候选清单只包含它真正读得了、写得了的 skill：随附内置 skill（即使开了 `prune_builtins: true`，那只影响确定性的归档流程）与 `skills.disabled` 里的 skill（`skill_view` 会拒绝）永远不会出现在清单里，所以这一流程不会把工具预算浪费在被拒绝的读写上。合并把一个 skill 视为完整包：如果某 skill 带有 `references/`、`templates/`、`scripts/`、`assets/`，或有指向这些路径的相对链接，curator 必须要么让它保持独立，要么把需要的支撑文件重新安家并改写路径，要么原样归档整个包 —— 而不是只把 `SKILL.md` 拍平塞进另一个 skill 的 `references/` 文件里。

:::info 合并是选择性开启的
默认情况下 curator 只做**修剪** —— 确定性的空闲流程会把 skill 标为 stale，并归档长期未用的。那套带主张的 LLM **合并**流程（建伞、合并重叠 skill）默认关闭，因为它每次运行都要花辅助模型的 token，并且会对你的 skill 库做大规模结构性改动。用 `curator.consolidate: true` 打开它，或用 `hermes curator run --consolidate` 按需跑一次。
:::

已 pin 的 skill 会被 curator 的自动转移跳过，而 agent 的 `skill_manage` 工具也拒绝**删除**它们；编辑与修补仍然放行。要让 agent 完全无法改动某个 skill，请改用 lock（锁定）。见下文的 [Pin 一个 skill](#pin-一个-skill) 与 [Lock 一个 skill](#lock-一个-skill)。

## 配置

所有设置都位于 `config.yaml` 的 `curator:` 下（不是 `.env` —— 这不是秘密）。默认值：

```yaml
curator:
  enabled: true
  interval_hours: 168          # 7 days
  min_idle_hours: 2
  stale_after_days: 14
  archive_after_days: 30
  consolidate: false           # LLM umbrella-building pass — opt-in (prune-only by default)
  prune_builtins: false        # opt in to archiving unused bundled built-in skills too (hub skills always exempt)
```

要彻底关闭，设 `curator.enabled: false`。要保留始终开启的修剪、同时选择启用 LLM 合并，设 `curator.consolidate: true`。

### 用更便宜的 aux 模型跑审查

curator 的 LLM 审查流程是一个常规的辅助任务槽位 —— `auxiliary.curator` —— 与 Vision、Compression、Session Search 等并列。「Auto」意为「用我的主聊天模型」；覆盖该槽位即可为审查流程钉住特定的 provider + 模型。

**最省事 —— `hermes model`：**

```bash
hermes model                   # → "Auxiliary models — side-task routing"
                               # → pick "Curator" → pick provider → pick model
```

同一个选择器在 Web dashboard 的 **Models** 标签下也有。

**直接改 config.yaml（等价写法）：**

```yaml
auxiliary:
  curator:
    provider: openrouter
    model: google/gemini-3-flash-preview
    timeout: 600               # generous — reviews can take several minutes
```

保持 `provider: auto`（默认）会让审查流程走你的主聊天模型，与其他每个辅助任务的行为一致。

:::note 旧配置
早期版本用的是一次性的 `curator.auxiliary.{provider,model}` 块。那条路径仍能工作，但会打一行弃用日志 —— 请迁移到上面的 `auxiliary.curator`，这样 curator 就与其他每个 aux 任务共用同一套管道（`hermes model`、dashboard 的 Models 标签、`base_url`、`api_key`、`timeout`、`extra_body`）。
:::

## CLI

```bash
hermes curator status         # last run, counts, pinned list, LRU top 5
hermes curator run            # trigger a run now (blocks until done). Prune-only unless curator.consolidate: true
hermes curator run --consolidate # force the LLM consolidation pass on for this run, overriding the config default
hermes curator run --background  # fire-and-forget: start the run in a background thread
hermes curator run --dry-run  # preview only — report without any mutations
hermes curator backup         # take a manual snapshot of ~/.hermes/skills/
hermes curator rollback       # restore from the newest snapshot
hermes curator rollback --list     # list available snapshots
hermes curator rollback --id <ts>  # restore a specific snapshot
hermes curator rollback -y         # skip the confirmation prompt
hermes curator pause          # stop runs until resumed
hermes curator resume
hermes curator pin <skill>    # never auto-transition this skill
hermes curator unpin <skill>
hermes curator lock <skill>   # the agent may not change it
hermes curator unlock <skill>
hermes curator adopt <skill>    # hand an unmanaged skill to the curator
hermes curator adopt --all-unmanaged   # hand over every unmanaged skill
hermes curator list-unmanaged   # itemize skills with no provenance marker
hermes curator restore <skill>  # move an archived skill back to active
hermes curator list-archived    # list skills currently in ~/.hermes/skills/.archive/
hermes curator archive <skill>  # manually archive a single skill now
hermes curator prune [--days N] # bulk-archive agent-created skills idle >= N days (default: `archive_after_days`, 30)
hermes curator ledger           # list the per-mutation audit ledger (all actors)
hermes curator ledger --skill <name> --limit 50  # filter/paginate ledger entries
hermes curator rollback <entry-id>  # undo a single mutation from the ledger
hermes curator purge [--days N] [--dry-run]  # delete archived skills older than the TTL (explicit only)
```

## 备份与回滚

在合并流程（`consolidate: true`，也是唯一会就地改写 skill 内容的流程）之前，Hermes 会在 `~/.hermes/skills/.curator_backups/<utc-iso>/skills.tar.gz` 对 `~/.hermes/skills/` 打一个 tar.gz 快照。快照只覆盖活跃 skill 树：`.archive/`、审计账本、`.hub/` 与备份本身从不纳入，回滚也从不倒带它们（用更旧的副本会丢掉已归档的 skill 或账本条目）。如果某轮流程归档或合并了你不想动的东西，一条命令即可撤销整次运行：

```bash
hermes curator rollback        # restore newest snapshot (with confirmation)
hermes curator rollback -y     # skip the prompt
hermes curator rollback --list # see all snapshots with reason + size
```

回滚本身也是可逆的：在替换 skill 树之前，Hermes 会再打一个标记为 `pre-rollback to <target-id>` 的快照，所以误回滚可以用 `--id` 滚回那一个来撤销。

你也可以随时用 `hermes curator backup --reason "before-refactor"` 手工打快照。`--reason` 字符串会写进快照的 `manifest.json`，并在 `--list` 中显示。

默认的只修剪流程不打快照：它只是把整个目录搬进 `.archive/`，而这件事本身就有对应的撤销命令（`hermes curator restore`），并且每次改动都记在下面的账本里。每次运行都会把快照修剪到 `curator.backup.keep`（默认 2），以限制磁盘占用：

```yaml
curator:
  backup:
    enabled: true
    keep: 2
```

设 `curator.backup.enabled: false` 可关闭自动快照。只有先设 `enabled: true`，手工的 `hermes curator backup` 命令在备份关闭时才可用 —— 这个开关对两条路径是对称把关的，从而没有哪种方式能意外跳过有改动运行的运行前快照。

`hermes curator status` 还会列出最久未用的五个 skill —— 一眼看出接下来哪些最可能变成 stale。

同一套子命令在运行中的会话里（CLI 或 gateway 平台）也可作为 `/curator` 斜杠命令使用。

## 审计账本与单条回滚

整次运行的快照回答的是「撤销上一轮 curator 做的所有事」—— 但有时你想知道*谁改了什么*，并精确撤销某一次改动。每一次 skill 改动 —— curator 的自动转移、agent 的 `skill_manage` 调用，以及你自己的 CLI 归档/恢复/清理 —— 都会向 `~/.hermes/skills/.curator_ledger.jsonl` 这个只追加的 JSONL 账本追加一条记录：

- **actor** —— `curator`（后台审查 fork / 自动转移）、`agent`（前台 agent 工具调用）或 `user`（CLI 命令）
- **action** —— `create`、`edit`、`patch`、`delete`、`write_file`、`remove_file`、`archive`、`restore`、`purge`、`rollback`
- **evidence** —— 删除意图（合并时的 `absorbed_into`，修剪时为空，以及是否由可恢复归档路径处理），以及可用时触发它的会话 id
- **before/after** —— 逐文件的 `{path, sha256}` 清单。文件内容按内容寻址存储（按哈希去重）在 `~/.hermes/.curator_backups/blobs/` 下，所以一百条触及同一未变文件的记录只花一个 blob。

```bash
hermes curator ledger                  # newest 20 entries
hermes curator ledger --skill my-skill --limit 50
hermes curator rollback <entry-id>     # restore that one mutation's before-state
```

单条回滚会从 blob 存储里精确恢复那一次改动触及的文件（并删除它创建的文件）—— skill 树里的其他东西一动不动。与整树回滚一样，它会先为当前状态记一条安全账本记录，并且**失败即关闭（fail closed）**：安全捕获写不出来时，什么都不改。由于前台删除同样入账，`hermes curator rollback <entry-id>` 可以让一个被硬删的 skill 复活。

账本是遥测，不是闸门 —— 如果写记录失败，改动照样生效。用下面的配置关掉它：

```yaml
skills:
  ledger: false
```

这个文件还有大小上限：一旦超过 `skills.ledger_max_bytes`（默认 5 MB），下一次改动会先经由未变文件去重重写它（正是 `hermes curator ledger --compact` 所做的），如果真正有分歧的记录仍超限，就丢弃最旧的那些、无论形状如何 —— 最新那条总是存活，保留尾部里的行从不被重写或解析（那里的一行坏数据原样保留），这次清扫还会释放没有任何引用、且已超过一小时的 blob（一个新出现的无引用 blob 可能属于另一个进程尚未记录的捕获）。设为 `0` 可让账本永远保持只追加。

```yaml
skills:
  ledger_max_bytes: 5242880   # 0 = never auto-maintain
```

## 归档 TTL 清理

归档的 skill 默认永久保留。如果你希望 `~/.hermes/skills/.archive/` 有界，设一个 TTL 然后显式清理 —— 清理从不自动运行，并且每个被清理的 skill 都会先被捕获进账本（连同 blob），所以即便是一次清理也留下可审计、可恢复的痕迹：

```yaml
curator:
  archive_ttl_days: 180   # 0 (default) = never purge
```

```bash
hermes curator purge --dry-run   # preview what would be deleted
hermes curator purge             # delete archives older than the TTL (with confirmation)
hermes curator purge --days 90   # one-off TTL override
```

## 「agent 创建」是什么意思

curator 只管理在 `~/.hermes/skills/.usage.json` 中被明确标记为 **agent 创建**的 skill。一个 skill 需要同时满足以下所有条件才算数：

1. 它的名字**不在** `~/.hermes/skills/.bundled_manifest` 里（随仓库发布的内置 skill）。
2. 它的名字**不在** `~/.hermes/skills/.hub/lock.json` 里（hub 安装的 skill）。
3. 它的 `.usage.json` 条目带有 `"created_by": "agent"` 或 `"agent_created": true`。

目前，只有**后台自我改进审查 fork** 会设置这个标记 —— 即它在周期性审查流程（约每 10 个 agent 轮次一次）中创建新伞状 skill 的时候。后台 fork 以 `background_review` 作为写入来源运行（经由 `tools/skill_provenance.py`），这是唯一会触发 `skill_manage` 中 `mark_agent_created()` 调用的路径。

前台 agent 在对话中经由 `skill_manage(action="create")` 创建的 skill（包括 `/learn`）**不会**被标为 agent 创建 —— 它们被记为 `created_by: learn`，这会让它们立刻出现在[学习历程](./memory.md#学习历程journey)里，但不算 curator 的纳管对象。它们被视为用户主导的，curator 有意不碰。

:::warning 你手写的 skill 不受策展
如果你手工创建了 `SKILL.md`，或把 Hermes 指向了一个外部 skill 目录，该 skill 的 `.usage.json` 条目会是 `created_by: null`（或缺这个字段）。curator 不会碰它。前台 agent 应你要求创建的 skill（`created_by: learn`）同理。

**要看 curator 实际管理哪些 skill**，运行 `hermes curator status`。如果 agent 创建的数量为 0，说明当前没有任何 skill 在 curator 的管辖之内 —— LLM 审查流程会被跳过，报告会显示 `Model: (not resolved) via (not resolved)`、`Duration: 0s`。
:::

### 收编未纳管的 skill

`hermes curator status` 会在纳管数量之外报告一个**未纳管（unmanaged）**数量：

```
curator-managed skills: 43 total  (agent-created=43  bundled=0)
  active     41
  stale       2
  archived    0

unmanaged (no provenance marker): 112 total
  pre-dates marker    34
  foreground-created  78
  never auto-staled or archived — `hermes curator adopt <name>` hands one over
```

这 112 个是策展*有资格*纳入、却对生命周期永久不可见的，原因只有两种之一：

- **pre-dates marker** —— 记录写于 `created_by` 存在之前，所以它根本不携带任何来源信号。作者身份从记录上确实无从得知。
- **foreground-created** —— 前台的 `skill_manage(create)` 按设计记下 `created_by: learn`（更老的记录则是未设置），因为你要求创建的 skill 属于你。

于是一个庞大的 skill 库可能看起来被完整策展，而其中大部分其实碰不得。`adopt` 通过**声明**来弥合这个缺口：

```bash
hermes curator list-unmanaged                    # itemize them, with reasons
hermes curator adopt <name> [<name> ...]         # hand specific skills over
hermes curator adopt --all-unmanaged --dry-run   # preview the full list
hermes curator adopt --all-unmanaged             # hand over everything (prompts)
hermes curator adopt --all-unmanaged --yes       # skip the prompt
```

收编写入的正是后台审查 fork 写入的同一个 `created_by: agent` 标记。它**不会**重置空闲时钟 —— 被收编的 skill 保留既有的 `last_activity_at`，所以把一个你早已不用的 skill 库交出去，并不会给它换来一个新的 90 天窗口。预期被收编、长期空闲的 skill 会在下一轮变为 `stale`（或 `archived`）；这正是目的所在。

收编只管辖*归档*。后台自我改进审查可以对任何它从中学习的 skill 打补丁、重写、添加支撑文件（手写的、URL 安装的、随附的、hub 安装的、外部的或已 pin 的），好让经验落到掌管该任务的 skill 里，无论作者是谁。每一次这样的写入都记录在 skill 账本中。它只可能归档（删除）curator 管理的 skill，绝不会动已 pin 的。要在这些写入落地前审核它们，请打开 `skills.write_approval`（见 [Gating agent skill writes](./skills.md#门控-agent-的技能写入skillswrite_approval)）。一个被审查编辑过的随附或 hub 安装 skill 会被算作本地已修改，于是 `hermes update` / `hermes skills update` 不再覆盖它。

:::note `created_by` 是策略标记，不是来源声明
存储的字段名叫 `created_by`，但它被消费为「自主策展可以碰这个吗？」—— 而不是「这个文件是谁写的」。这是两个不同的问题，对于早于该标记的记录，作者身份的答案根本无从恢复。保留这个名字是因为每个 `.usage.json` 里都已经有它了；把它读作策略。`hermes curator adopt` 改变的是策略，对文件是谁写的只字不提。
:::

:::note 来源是声明出来的，从不推断
收编刻意做成手动的。遥测无法确立作者：一个有数千次修补的 skill 证明的是 agent *维护*它，而不是 agent *写了*它 —— Hermes 经常代表你编辑用户撰写的 skill。一个自动的「看着像 agent 做的，收了它」启发式，迟早会把你手写的东西归档掉。`adopt` 会拒绝随附的、hub 安装的、外部的与受保护的内置 skill，它们的所有者不是你。
:::

真正属于 agent 创建的 skill 遵循完整生命周期：

- `active` →（30 天未用）`stale` →（90 天未用）`archived`
- 已 pin 的 skill 跳过所有自动转移
- 归档可经 `hermes curator restore <name>` 恢复

如果你想保护某个 agent 创建的 skill 不被归档，用 `hermes curator pin <name>`。如果你想让 agent 完全无法改动某个 skill —— 比如你依赖的手写 skill —— 用 `hermes curator lock <name>`。两者都在下文说明。

## Pin 一个 skill

pin 保护 skill 不被删除 —— 既挡 curator 的自动归档流程，也挡 agent 的 `skill_manage(action="delete")` 工具调用。一旦 skill 被 pin：

- **curator** 在自动转移（`active → stale → archived`）中跳过它，其 LLM 审查流程也被告知不要碰它。
- **agent 的 `skill_manage` 工具**拒绝对其执行 `delete`，并把用户引向 `hermes curator unpin <name>`。补丁与编辑仍然放行，这样 agent 在踩到坑时可以改进已 pin skill 的内容，而不必来一套 pin/unpin/re-pin 的折腾。

pin 与 unpin：

```bash
hermes curator pin <skill>
hermes curator unpin <skill>
```

该标记以 `"pinned": true` 存在 skill 于 `~/.hermes/skills/.usage.json` 的条目上，因此能跨会话存续。

出现在任何 cron 任务 `skills:` 列表里的 skill，在**自动转移**上受同样保护（只要引用还在，curator 就不会把它变 stale 或归档），即使任务处于暂停或禁用状态也一样。如果你还想挡住 `skill_manage delete`，请优先使用显式的 pin。

只有 **agent 创建**的 skill 才能被 pin —— `hermes curator pin` 会拒绝随附与 hub 安装的 skill，并给出解释性消息。hub 安装的 skill 永远不受 curator 改动。随附内置 skill 只有在你用 `curator.prune_builtins: true` 选择启用后才会被碰到，而且即便如此也只在 `archive_after_days` 天未使用后被归档 —— 绝不会被打补丁、被合并或被删除。

一小批**受保护的内置 skill** 可以被硬编码为永不可归档、永不可合并，无论 `curator.prune_builtins`、pin 状态或 LLM 判断如何。它们支撑着关键的用户体验，悄悄归档其中一个会把它的斜杠命令变成一个「Unknown command」错误，而你收不到任何信号。（这批目前是空的 —— `plan` 这个原成员已经毕业为内置的 `/plan` 命令，磁盘上不再有对应 skill。）受保护的内置 skill 会从 curator 的候选清单中整体滤掉，因此合并流程根本看不到它们。

如果你想要比「不被删除」更强的保证 —— 在 agent 仍能读取和使用的同时冻结 skill 内容 —— 就 lock（下文一节）。pin 和 lock 都不拦你自己：你的编辑器与 Desktop 的 skill 编辑器永远可用。

## Lock 一个 skill

pin 挡住归档。lock 则**挡住 agent 对 skill 的任何改动**，同时 skill 照旧可读、列在 skill 索引里、可自动加载、可使用。

```bash
hermes curator lock <skill>
hermes curator unlock <skill>
hermes curator status          # lists locked skills
```

在 Desktop 中，打开 **Capabilities → Skills**，选中该 skill 后使用它的 lock 开关。

skill 一旦被锁，agent 能写入的每一条途径都会拒绝它 —— 普通轮次、cron 任务、subagent、后台自我改进审查与 curator 流程一视同仁，甚至在 `--yolo` 下也一样：

- **`skill_manage`** 拒绝 `patch`、`edit`、`write_file`、`remove_file` 与 `delete`，单操作与批量两种形式都是。
- **`write_file` 与 `patch`** 拒绝 skill 目录内的任何路径（`SKILL.md`、`references/`、`scripts/` …）。
- **`terminal`** 拒绝向那里写入的命令：重定向与 `tee`、`cp`/`mv`/`rm`/`touch`/`mkdir`/`chmod`、`sed -i`/`perl -i`、skill 树内的 `git` 变更、向其解压归档，以及点名该 skill 的内联 `python -c`/`bash -c` 代码，`cd` 进该 skill 之后同样适用。读取该 skill、运行它的脚本仍然正常。
- curator 从不归档被锁的 skill。
- agent 无法解锁：`terminal` 拒绝 `hermes curator unlock`，而且只要还有任一 skill 被锁，锁定记录（`skills/.usage.json`）也以同样方式受保护。拒绝消息会让 agent 描述它想做的改动，由你来决定。

你自己的编辑不受闸门限制：在编辑器里或 Desktop 的 skill 编辑器里改这些文件永远有效。要让 agent 再次可以改动它，运行 `hermes curator unlock <skill>` 或拨动开关。

该标记以 `"locked": true` 存在 skill 于 `~/.hermes/skills/.usage.json` 的条目上，与 `pinned` 同在一个 sidecar 里，因此它是**按 profile 的**：`hermes -p work curator lock deploy-runbook` 只锁该 profile 的那一份。任何在该 profile 中能解析出来的 skill 都可以被锁（手写的、agent 创建的、随附的或 hub 安装的）；`lock` 会拒绝它无法解析的名字。

锁不能做什么：

- 它是**策略检查，不是沙箱。** terminal 检查读的是命令的写入目标；一个通过自身逻辑往 skill 里写的脚本，或 `execute_code`，不会被检查。需要硬边界的话，请配合文件系统权限。
- 如果 `.usage.json` 损坏，后台流程会被拒绝（fail closed），而普通轮次照常进行，所以一个坏文件不会冻结所有 skill 编辑。修复它，或运行 `hermes curator unlock <skill>` 让它重写。
- 它**不会**阻止 `hermes update` / `hermes skills update` 刷新你没有改动过的随附或 hub skill；那些是你的命令，不是 agent 写入。

## 使用遥测

curator 维护一个 `~/.hermes/skills/.usage.json` 的 sidecar，每个 skill 一条记录：

```json
{
  "my-skill": {
    "use_count": 12,
    "view_count": 34,
    "last_used_at": "2026-04-24T18:12:03Z",
    "last_viewed_at": "2026-04-23T09:44:17Z",
    "patch_count": 3,
    "last_patched_at": "2026-04-20T22:01:55Z",
    "created_at": "2026-03-01T14:20:00Z",
    "state": "active",
    "pinned": false,
    "archived_at": null
  }
}
```

计数器在这些情况下递增：

- `view_count`：agent 对该 skill 调用 `skill_view`。
- `use_count`：该 skill 被加载进某次对话的 prompt。
- `patch_count`：对该 skill 执行了 `skill_manage patch/edit/write_file/remove_file`。

随附与 hub 安装的 skill 被明确排除在遥测写入之外。

## 每次运行的报告

每次 curator 运行都会在 `~/.hermes/logs/curator/` 下写一个带时间戳的目录：

```
~/.hermes/logs/curator/
└── 20260429-111512/
    ├── run.json      # machine-readable: full fidelity, stats, LLM output
    └── REPORT.md     # human-readable summary
```

`REPORT.md` 是快速了解某次运行做了什么的途径 —— 哪些 skill 发生了状态转移、LLM 审查者说了什么、它修补了哪些 skill。适合审计，不必去 grep `agent.log`。

:::note 没有候选？报告显示 `(not resolved)`
当 curator **没有 agent 创建的 skill** 可审时，LLM 审查流程会被整体跳过。报告头部会显示 `Model: (not resolved) via (not resolved)`、`Duration: 0s` —— 这**不**表示配置错误或模型解析失败。它只是说明没有候选，因此从未调用过任何模型。自动转移阶段照常运行并正常报告计数。
:::

### 摘要中的改名映射

如果某次运行把多个 skill 合并到一个伞状 skill 之下（或合并了近似重复项），运行结束时打印给用户看的摘要会包含一份显式的改名映射，列出 curator 应用的每一对 `old-name → new-name`。这在逐 skill 的状态转移行之外额外给出，所以当一波改名落地时，你一眼就能看到，不必去 diff JSON 报告。这个提示也会在 `hermes curator pin` 下冒出来，如果你想锁定新标签，可以立刻 pin 伞状名字。

## 恢复一个已归档的 skill

如果 curator 归档了你仍然想要的东西：

```bash
hermes curator restore <skill-name>
```

这会把 skill 从 `~/.hermes/skills/.archive/` 搬回活跃树，并把状态重置为 `active`。如果期间已有同名的随附或 hub 安装 skill 被装上（会遮蔽上游），恢复会被拒绝。

## 按环境关闭

curator 默认开启。要关掉它：

- **只关一个 profile：** 编辑 `~/.hermes/config.yaml`（或当前激活 profile 的配置），设 `curator.enabled: false`。
- **只关一次运行：** `hermes curator pause` —— 暂停会跨会话保持；用 `resume` 重新启用。

如果 `min_idle_hours` 还没走完，curator 也会拒绝运行，所以在一台活跃的开发机上，它自然只在安静的时段运行。

## 另见

- [Skills System](./skills.md) —— skill 总体如何工作，以及创建它们的自我改进闭环
- [Memory](./memory.md) —— 与之平行的、维护长期记忆的后台审查
- [Bundled Skills Catalog](../../reference/skills-catalog.md)
- [Issue #7816](https://github.com/NousResearch/hermes-agent/issues/7816) —— 最初的提议与设计讨论
