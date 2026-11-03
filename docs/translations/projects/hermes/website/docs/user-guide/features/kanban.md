---
sidebar_position: 12
title: "Kanban（多 Agent 看板）"
description: "面向多 Hermes profile 协作的持久化 SQLite 任务看板"
---

# Kanban——多 Agent Profile 协作（Kanban — Multi-Agent Profile Collaboration）

> 来源：https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/kanban.md
> 原文：oss-repos/hermes-agent/website/docs/user-guide/features/kanban.md
> 翻译日期：2026-11-03 ｜ 范围：全文 ｜ 方式：机器翻译初稿，未经人工校对
> 引用于：docs/essay-study/hermes-2026.md、docs/brief-plan.md §3

## 目录

- [迭代上限前的完成检查点](#completion-checkpoints)
- [两个界面：模型通过工具说话，你通过 CLI 说话](#two-surfaces)
- [PR 完成契约](#pr-completion-contracts)
- [Kanban 与 delegate_task 的对比](#kanban-vs-delegate)
- [核心概念](#core-concepts)
- [看板（多项目）](#boards)
  - [从 CLI 管理看板](#boards-cli)
  - [从 dashboard 管理看板](#boards-dashboard)
  - [在 Desktop 应用中切换看板](#boards-desktop)
- [文件附件](#file-attachments)
- [快速开始](#quick-start)
  - [内嵌于 gateway 的 dispatcher（默认）](#gateway-dispatcher)
    - [worker 与 systemd cgroup](#systemd-cgroups)
  - [跨 home 共享看板](#shared-boards)
  - [幂等创建（用于自动化 / webhook）](#idempotent-create)
  - [CLI 批量动词](#bulk-cli-verbs)
- [为聊天 profile 启用工具](#enable-tools)
- [worker 如何与看板交互](#worker-interaction)
  - [为什么用工具而不是 shell 调用 hermes kanban](#why-tools)
  - [建议的交接证据](#handoff-evidence)
  - [worker 生命周期](#worker-lifecycle)
  - [把额外 skill 固定到特定任务](#pin-extra-skills)
  - [按任务覆盖模型](#per-task-model)
  - [成本策略：前沿模型做编排，廉价模型做 worker](#cost-strategy)
  - [生命周期插件钩子](#lifecycle-hooks)
  - [goal 模式卡片（--goal）](#goal-cards)
  - [编排者如何表现](#orchestrator-behavior)
- [Dashboard（GUI）](#dashboard)
  - [这个插件给你什么](#plugin-capabilities)
  - [自动编排 vs 手动编排](#auto-vs-manual)
  - [架构](#architecture)
  - [REST 接口](#rest-surface)
  - [Dashboard 配置](#dashboard-config)
  - [安全模型](#security-model)
  - [实时更新](#live-updates)
  - [扩展它](#extending)
  - [范围边界](#scope-boundary)
- [CLI 命令参考](#cli-reference)
  - [并发、调度与子任务晋级配置](#concurrency-config)
  - [定时启动任务（scheduled_at）](#scheduled-at)
  - [重生防护](#respawn-guard)
  - [拖拽删除与批量删除（dashboard）](#drag-delete)
  - [worker 可见性端点](#worker-visibility)
  - [Kanban Swarm 拓扑助手](#swarm-helper)
- [/kanban 斜杠命令](#kanban-slash-command)
  - [运行中使用：/kanban 绕过「agent 正在运行」的守卫](#slash-mid-run)
  - [create 时自动订阅（仅 gateway）](#slash-auto-subscribe)
  - [消息平台中的输出截断](#output-truncation)
  - [自动补全](#autocomplete)
- [协作模式](#collaboration-patterns)
- [把上下文交给后续卡片（parent 链接）](#parent-link)
  - [调和冲突的 worker 分支](#branch-collision)
  - [并行战役中的冲突热点](#collision-hotspots)
- [多租户用法](#multi-tenant)
- [桌面通知](#desktop-notifications)
- [Gateway 通知](#gateway-notifications)
  - [投递模式](#delivery-modes)
  - [多 profile 环境：投递归 profile 所有](#multi-profile-delivery)
- [Run——每次尝试一行](#runs)
  - [向前兼容](#forward-compat)
- [事件参考](#event-reference)
- [范围之外](#out-of-scope)

---

> **想要一篇导览？** 读 [Kanban 教程](./kanban-tutorial)——四个用户故事（单人开发、机队式铺量、带重试的角色流水线、熔断器），每个都配 dashboard 截图。本页是参考手册，教程是叙事。

Hermes Kanban 是一块持久任务看板，由你所有的 Hermes profile 共享，让多个具名 agent 协作干活，而不必依赖脆弱的进程内 subagent 群。每个任务是 `~/.hermes/kanban.db` 里的一行；每次交接是任何人都能读、能写的一行；每个 worker 是一个有自己身份的完整 OS 进程。

### 迭代上限前的完成检查点 {#completion-checkpoints}

由 dispatcher 持有的 worker，在其有限迭代预算走到约 90% 时会收到一次检查点提示，该提示附着在一个新的工具结果上，且此时还剩至少一次可调用工具的机会。想更早提醒，可用 `agent.budget_warning_ratio` 调整阈值。极小的预算最晚在倒数第二次迭代时提醒；只跑一次迭代的运行没有上限前的检查窗口。提示会在下一次请求之前写入会话记录。worker 应当在核验过任务契约之后才调用 `kanban_complete`，否则就先落一条进度评论再继续。仅有一次 commit 或 diff 从不会自动完成任务。

硬上限、无工具的最终摘要，以及连续失败熔断器都保持不变：预算耗尽的 worker 仍要受有界重试的约束。这是一个「有机会提醒」的机制，并不保证模型一定听。普通对话与被委派的子任务不会继承这套自动 Kanban 检查点；它们的迭代提醒仍是可选开启的。

### 两个界面：模型通过工具说话，你通过 CLI 说话 {#two-surfaces}

看板有两扇正门，背后都是同一个 `~/.hermes/kanban.db`：

- **Agent 通过专用的 `kanban_*` toolset 驱动看板** —— `kanban_show`、`kanban_list`、`kanban_complete`、`kanban_request_review`、`kanban_request_changes`、`kanban_block`、`kanban_heartbeat`、`kanban_comment`、`kanban_attach`、`kanban_attach_url`、`kanban_attachments`、`kanban_create`、`kanban_link`、`kanban_unblock`。dispatcher 生成每个 worker 时，这些工具已经写进它的 schema；编排者 profile 也可以显式启用 `kanban` toolset。模型靠直接调用工具来读取与路由任务，*而不是* shell 出去执行 `hermes kanban`。参见下文的 [worker 如何与看板交互](#worker-interaction)。
- **你（以及脚本、cron）通过 `hermes kanban …` 驱动看板** —— 在 CLI 上、在会话里用 `/kanban …` 斜杠命令，或在 dashboard 上。这些入口是给人和自动化用的——也就是背后没有 tool-calling 模型的场合。

两个界面都经由同一层 `kanban_db` 路由，所以读操作看到的是一致视图，写操作也不会漂移。本页其余示例都用 CLI，因为方便复制粘贴，但每个 CLI 动词都有模型使用的工具调用等价物。

这套形态覆盖的是 `delegate_task` 扛不动的工作负载：

- **研究分诊** —— 并行研究员 + 分析师 + 写作者，人留在环路里。
- **定时运维** —— 每天重复的简报，几周下来攒成一份日志。
- **数字分身** —— 常驻的具名助手（`inbox-triage`、`ops-review`），随时间积累记忆。
- **工程流水线** —— 拆解 → 在并行 worktree 中实现 → 评审 → 迭代 → PR。
- **机队式作业** —— 一个专家管理 N 个对象（50 个社交账号、12 个被监控的服务）。

八种典型的协作模式收录在下文的[协作模式](#collaboration-patterns)。

## PR 完成契约 {#pr-completion-contracts}

创建任务时用 `--completion-contract OWNER/REPO` 声明 PR 类工作（针对已有工作也可以给精确的 `https://github.com/OWNER/REPO/pull/123` 链接）。`kanban_create` 接受同样的 `completion_contract` 字段。故意只在本地做的工作用 `local-only`；已有的、未声明的卡片保持该默认值。正文里贴的 URL 不构成策略。

发布之后，把 `metadata.published_pr` 传给完成操作。第一个匹配上的 URL 会永久绑定这张卡片；重试不能拿一个变绿的兄弟 PR 顶替。CLI 的 `show --json` 与 `kanban_show` 都会暴露已保存的契约。

共享的 `complete_task` 边界覆盖 worker 工具、CLI、评审批准与 dashboard 完成。它会读取经典的分支保护与生效 ruleset 要求的 contexts，分页拉取 exact-head 的 check run 与旧式 status，然后重新读取 PR 的 head/base。可选的 failed/skipped 遥测不会否决已接受的必需检查。必需证据缺失、pending、failed、cancelled、timed-out、stale、skipped 或 neutral，都无法完成卡片。零 run 的接受、读不懂的策略、GitHub API 失败同样无法完成。没有必需检查的仓库需要 `local-only` 契约。`gh` 必须已认证，且对仓库的 checks 与 rules 有读权限；这个闸门不做任何远端写入。

接受性读取以**被指派 profile 的** `gh` 登录身份运行——取该 profile 自己 `.env` 里的 `GH_TOKEN` / `GH_CONFIG_DIR`，而不是完成卡片的那个进程的环境登录。在多 profile 主机上（每个组织一个 GitHub 身份），请在每个 profile 内分别登录 `gh`（在该 profile 的 `.env` 里设 `GH_CONFIG_DIR`）。token 必须放在 profile 的 `.env`（或配置好的密钥来源）里：仅在 shell 或 systemd 单元中 export 的 `GH_TOKEN` 会被从 `gh` 子进程里抹掉，绝不会重新加上。被指派的 profile 如果没有自己的 `gh` 登录、或该登录已不存在，会被拒绝并报 `not logged in`，而不是回落到 `~/.config/gh`；未指派的卡片仍使用环境登录。看不到该仓库的登录会被判为 `classification=auth` 并点名 profile 与仓库，而不是一个可重试的基础设施失败。

拒绝时保留活跃卡片与工作区。持久化的 `pr_acceptance` 事件会存下 PR URL、SHA、必需 contexts、check 的 ID/URL、分类与恢复指引；`last_failure_error` 会给出下一步。修掉失败、重跑基础设施检查或等待，然后再重试完成。需要人工介入时用 `kanban_block`。GitHub 泛化的 `failure` 无法判断到底是测试失败还是制品上传失败，需要查看它保留的 URL。显式的基础设施结论与 API 失败会被单独分类。此过程不会派生额外 worker。

回执持久化与终态写入的复查会在同一把 SQLite 锁下核对 run/契约的归属：一个被回收的 worker 无法完成，也无法把接受结果挂到新的 run 上。最后一次 GitHub 读取只是完成时刻的快照，不是分布式事务，也不是完成后的持续监控。这是单用户生命周期守卫，不是针对任意直接数据库写入的 OS 隔离。GitHub Enterprise 不在覆盖范围内。相关的发布/生命周期工作：#91230、#84254、#52311；仅本地校验与发布并不等于远端接受。

## Kanban 与 `delegate_task` 的对比 {#kanban-vs-delegate}

它们看起来相似，但不是同一种原语。

| | `delegate_task` | Kanban |
|---|---|---|
| 形态 | RPC 调用（fork → join） | 持久消息队列 + 状态机 |
| 父任务 | 阻塞直到子任务返回 | `create` 之后即发即忘 |
| 子任务身份 | 匿名 subagent | 具名 profile，带持久记忆 |
| 可恢复性 | 无——失败即失败 | block → unblock → 重跑；崩溃 → 回收 |
| 人在环路 | 不支持 | 任何时点都可以评论 / 解除阻塞 |
| 每任务的 agent 数 | 一次调用 = 一个 subagent | 任务存续期内 N 个 agent（重试、评审、跟进） |
| 审计轨迹 | 上下文压缩后丢失 | SQLite 中永久的持久行 |
| 协作方式 | 层级式（调用方 → 被调方） | 对等——任何 profile 可读写任何任务 |

**一句话区分：** `delegate_task` 是一次函数调用；Kanban 是一条工作队列，其中每次交接都是任何 profile（或人）都能看到、能改的一行。

:::caution 别把支援卡片链接到它本来要解除阻塞的那张卡
一个被 `t_parent` 阻塞、为缺失部分创建支援卡片的 worker，**绝不能**执行 `kanban_link(t_parent, t_support)`：这个链接会让支援卡片变成被阻塞父卡的*子卡*，于是它被挡在「它存在就是为了给它解除阻塞」的父卡后面，两张卡都永远不会运行。请改为在支援卡片正文里引用父卡 id。当 `link`/`kanban_link` 把一个 `ready` 子卡降级时（`kanban_create` 带 `parents` 停放新卡时同理），会报告 `gated: true` 并记录一条 `dependency_wait` 事件，因此这个死锁在看板上是可见的；`hermes kanban unlink <parent> <child>` 可以解开它。
:::

**该用 `delegate_task` 的场合：** 父 agent 需要一个简短的推理答案才能继续，不涉及人，结果回到父 agent 的上下文里。

**该用 Kanban 的场合：** 工作跨 agent 边界、需要在重启后存活、可能需要人输入、可能被另一个角色接手，或事后需要可被查到。

两者也可以在一次运行里共存。kanban 任务在该 profile 的 gateway 之下、于一个隔离的受管 worker 中执行，它经由 `delegate_task` 派生的子任务也由该 gateway 在 worker 执行期间保留：每个子任务有自己的会话（列为该卡片会话的 subagent）、计入 `delegation.max_concurrent_children` 与 `delegation.max_spawn_depth`、在其卡片的轮次内返回结果，并随 worker 一起结束。如果 gateway 在某个子任务进行中挂掉，该子任务会被终止，绝不会恢复。必须活得比 gateway 更久、或需要自己评审者的工作，仍然应该放进子卡片（`kanban_create` 带 `parents`）。

## 核心概念 {#core-concepts}

- **Board（看板）** —— 一条独立的任务队列，自带 SQLite DB、workspace 目录与 dispatcher 循环。一次安装可以有多个看板（例如每个项目、仓库或领域一个）；见下文的[看板（多项目）](#boards)。单项目用户只待在 `default` 看板上，在本文档之外根本看不到「看板」这个词。
- **Task（任务）** —— 一行记录，含标题、可选正文、一个负责人（profile 名）、状态（`triage | todo | ready | running | blocked | review | done | archived`）、可选租户命名空间、可选幂等键（为重试的自动化去重）。
- **Link（链接）** —— 记录父 → 子依赖的 `task_links` 行。当所有父任务都是 `done` 时，dispatcher 把 `todo → ready` 晋级。给一个运行中的子任务加链接会被拒绝，因为它无法约束已被认领的工作；唯一的例外是活跃 worker 在依赖阻塞交接前一刻、带着 dispatcher 提供的 run 归属，给自己的卡片加链接。
- **Comment（评论）** —— agent 之间的协议。Agent 与人都追加评论；worker 被（重新）生成时，会把完整评论串作为上下文的一部分读入。
- **Workspace（工作区）** —— worker 干活所在的目录。有三种：
  - `scratch`（默认）—— `~/.hermes/kanban/workspaces/<id>/` 下的新鲜临时目录（非默认看板则是 `~/.hermes/kanban/boards/<slug>/workspaces/<id>/`）。**任务完成时删除** —— scratch 按设计就是一次性的。通过 `kanban_complete(artifacts=[...])` 或 `kanban_request_review(artifacts=[...])` 显式声明的文件，会在清理前被复制进持久的按任务附件存储（评审交接在交接时刻就 stage 它们，因为真正删除 scratch 工作区的是评审者稍后的完成动作）；旧式完成摘要里已有的交付物路径同样处理。其余 scratch 文件会被删除。声明了却缺失的 scratch 产物会让任务保持进行中，好让 worker 修正路径后重试。当整个工作区都需要保留时，用 `worktree:` 或 `dir:<path>`。安装后第一次创建 scratch 工作区时，dispatcher 会记一条警告，并在任务上发出 `tip_scratch_workspace` 事件（可用 `hermes kanban show <id>` 查看）。
  - `dir:<path>` —— 已存在的共享目录（Obsidian 库、邮件运维目录、按账号划分的文件夹）。**必须是绝对路径。** 像 `dir:../tenants/foo/` 这样的相对路径会在派发时被拒绝，因为它会相对于 dispatcher 恰好所在的 CWD 解析，既含糊又是混淆代理的逃逸向量。除此之外该路径是被信任的——这是你的机器、你的文件系统，worker 用你的 uid 运行。这就是可信本地用户的威胁模型；kanban 按设计是单主机的。**完成时保留。**
  - `worktree` —— 用于编码任务的 `.worktrees/<id>/` 下的 git worktree。用 `worktree:<path>` 固定确切目标路径。由 worker 侧的 `git worktree add` 创建，提供了参数时使用 `--branch`。**完成时保留。**
- **Dispatcher** —— 一个长驻循环，每 N 秒（默认 60）做一轮：回收过期的认领、回收崩溃的 worker（PID 已消失但 TTL 未到）、回收比自己的 run 活得更久的 worker（自己的 `kanban_complete`/`kanban_block` 之后仍存活的 worker，在其 run 关闭两分钟后会被终止，好让它有时间收尾最后一轮——按 PID *与* 启动时间指纹双重匹配，所以被回收复用的 PID 绝不会被误发信号；记为 `terminal_worker_reaped` 事件）、晋级就绪任务、原子认领、生成被指派的 profile。默认**在 gateway 内部**运行（`kanban.dispatch_in_gateway: true`）。一次 tick 中一个 dispatcher 扫全部看板；worker 生成时会钉住 `HERMES_KANBAN_BOARD`，因此看不到其他看板。同一任务连续 `kanban.failure_limit` 次生成失败后（默认 2），dispatcher 会以最后一次错误为由自动把它置为阻塞——防止在 profile 不存在、工作区挂载不了之类任务上空转。
- **Tenant（租户）** —— 看板*内部*的可选字符串命名空间。一支专家机队可以服务多家企业（`--tenant business-a`），靠 workspace 路径与记忆键前缀做数据隔离。租户是软过滤；看板才是硬隔离边界。

## 看板（多项目） {#boards}

看板让你把互不相关的工作流——每个项目、仓库或领域一条——拆进彼此隔离的队列。全新安装恰好有一个名为 `default` 的看板（数据库仍在 `~/.hermes/kanban.db`，以保持兼容）。只想有一条工作流的用户永远不需要知道看板的存在；该功能是可选开启的。

按看板的隔离是绝对的：

- 每个看板一个独立的 SQLite DB（`~/.hermes/kanban/boards/<slug>/kanban.db`）。
- 独立的 `workspaces/` 与 `logs/` 目录。
- 为任务生成的 worker **只**能看到自己看板的任务——dispatcher 在子进程环境里设置 `HERMES_KANBAN_BOARD`，worker 能访问的每个 `kanban_*` 工具都会读它。
- 不允许跨看板链接任务（保持 schema 简单；如果确实需要跨项目引用，用自由文本提及并手动按 id 查找）。

### 从 CLI 管理看板 {#boards-cli}

```bash
# See what's on disk. Fresh installs show only "default".
hermes kanban boards list

# Create a new board.
hermes kanban boards create atm10-server \
    --name "ATM10 Server" \
    --description "Minecraft modded server ops" \
    --icon 🎮 \
    --switch                   # optional: make it the active board

# Operate on a specific board without switching.
hermes kanban --board atm10-server list
hermes kanban --board atm10-server create "Restart ATM server" --assignee ops

# Change which board is "current" for subsequent calls.
hermes kanban boards switch atm10-server
hermes kanban boards show             # who's active right now?

# Rename the display name (the slug is immutable — it's the directory name).
hermes kanban boards rename atm10-server "ATM10 (Prod)"

# Archive (default) — moves the board's dir to boards/_archived/<slug>-<ts>/.
# Recoverable by moving the dir back.
hermes kanban boards rm atm10-server

# Hard delete — `rm -rf` the board dir. No recovery.
hermes kanban boards rm atm10-server --delete
```

看板解析顺序（优先级从高到低）：

1. CLI 调用上显式的 `--board <slug>`。
2. `HERMES_KANBAN_BOARD` 环境变量（由 dispatcher 在生成 worker 时设置，因此 worker 看不到其他看板）。
3. `~/.hermes/kanban/current` —— `hermes kanban boards switch` 持久化的 slug。
4. `default`。

slug 有校验：小写字母数字 + 连字符 + 下划线，1–64 个字符，必须以字母数字开头。大写输入会自动转小写。其他任何写法（斜杠、空格、点、`..`）都会在 CLI 层被拒绝，这样路径穿越花样无法给看板命名。

### 从 dashboard 管理看板 {#boards-dashboard}

`hermes dashboard` → Kanban 标签页在看板多于一个（或任意看板有任务）时，顶部会显示看板切换器。只有一个看板的用户只会看到一个小的 `+ New board` 按钮；切换器在用得上之前保持隐藏。

- **看板下拉框** —— 选择活跃看板。你的选择存进浏览器的 `localStorage`，因此刷新后仍保持，同时不会把你留着开着的终端里 CLI 的 `current` 指针挪走。
- **+ New board** —— 打开一个弹窗，要你填 slug、显示名、描述、图标、项目目录，以及（当存在任何 Project 时）一个 **Project** 选择器。可选自动切换到新看板。
- **Settings** —— 打开弹窗，编辑当前看板的显示名、描述与**项目目录**（`default_workdir`）。项目目录是看板级的工作区默认值，每个新任务都会继承（git 仓库 → 保留 worktree，普通目录 → 保留目录）；每个任务仍可在创建时覆盖它。清空该字段会让新任务回到一次性 scratch 工作区——除非绑定了 Project，那种情况用 Project 的主文件夹；要回到 scratch，先解绑项目。
- **Project**（两个弹窗里都有）—— 把看板绑定到一个 Hermes Project（即看板的 `project_id`）。在已绑定看板上创建的任务继承该 Project；在目录字段为空时选择 Project，也会用 Project 的主文件夹填充项目目录。绑定的 Project 以 `Project: <name>` 徽章显示在看板下拉框旁；它的 `×` 会解绑看板（发送 `project_id: ""`）而不碰项目目录，Settings 里的 `No binding` 在保存时效果相同。选择器只在至少存在一个 Project 时出现。
- **Archive** —— 只在非 `default` 看板上显示。确认后把看板目录移入 `boards/_archived/`。

所有 dashboard API 端点都接受 `?board=<slug>` 来限定看板范围；events WebSocket 在连接时即钉在某个看板上，在 UI 里切换看板会针对新看板打开一条新的 WS。

### 在 Desktop 应用中切换看板 {#boards-desktop}

在 Desktop 应用里，看板切换器位于 Kanban 页面顶部的标题行、页面标题旁边：一个 **Board** 控件，显示当前看板的名称与任务数，带一个箭头——悬停会提示「Switch board」。点它可以选另一个看板，也可以重命名、配置、导出、导入、创建或归档看板。当 Kanban 以分屏小格打开时，同一个 **Board** 控件出现在该看板自己的标题行里、任务数之后。与 dashboard 一样，桌面端保留自己的选择（本地持久化），不会移动 CLI 的 `current` 指针。

## 文件附件 {#file-attachments}

任务可以带文件附件——PDF、图片、源文档——这样 worker 不必靠你把路径贴进正文、再指望它自己找到。

- **上传** —— 在 dashboard 抽屉里打开任务，用 **Attachments** 区域的 *Upload file* 按钮（可一次多个文件）。每次上传上限 25 MB。
- **存储** —— 文件落在默认看板的 `<hermes-home>/kanban/attachments/<task_id>/`，具名看板则是 `<hermes-home>/kanban/boards/<slug>/attachments/<task_id>/`。设 `HERMES_KANBAN_ATTACHMENTS_ROOT` 可固定自定义位置。
- **worker 看到什么** —— dispatcher 把任务交给 worker 时，worker 的上下文里会有一个 **Attachments** 区域，列出每个文件的名称与**绝对路径**。worker 有完整的 file/terminal 工具权限，因此可直接读附件（`read_file`，或 `pdftotext` 之类的 shell 工具）。
- **下载 / 移除** —— 抽屉里每个附件都带下载链接与移除（×）控件。移除附件会删掉它的元数据行；磁盘文件只有在没有其他附件行还引用它时才删除（被多个任务共享的文件会一直留到最后一个引用被移除）。在 CLI 上，`hermes kanban attach-rm ATTACHMENT_ID` 以同样方式移除附件。

:::note 远程终端后端
附件路径在**本地**终端后端上直接解析，而这是 Kanban worker 的默认后端。如果你把 worker 跑在远程后端（Docker、Modal），请把看板的 `attachments/` 目录挂载进沙箱，worker 上下文里的绝对路径才可达。
:::

## 快速开始 {#quick-start}

下面的命令是**你**（人类）在搭看板、建任务。任务一旦被指派，dispatcher 就把被指派的 profile 生成为 worker，从那以后**模型通过 `kanban_*` 工具调用驱动任务，而不是 CLI 命令**——见下文的 [worker 如何与看板交互](#worker-interaction)。

```bash
# 1. Create the board (you)
hermes kanban init

# 2. Start the gateway (hosts the embedded dispatcher)
hermes gateway start

# 3. Create a task (you — or an orchestrator agent via kanban_create)
hermes kanban create "research AI funding landscape" --assignee researcher

# 4. Watch activity live (you)
hermes kanban watch

# 5. See the board (you)
hermes kanban list
hermes kanban stats
```

dispatcher 捡起 `t_abcd` 并生成 `researcher` profile 时，该 worker 的模型做的第一件事就是调用 `kanban_show()` 读自己的任务。它不会去跑 `hermes kanban show t_abcd`。

### 内嵌于 gateway 的 dispatcher（默认） {#gateway-dispatcher}

dispatcher 跑在 gateway 进程内部。无需安装任何东西，也没有独立服务要管理——只要 gateway 活着，就绪任务会在下一个 tick（默认 60 秒）被捡起。

```yaml
# config.yaml
kanban:
  dispatch_in_gateway: true        # default
  dispatch_interval_seconds: 60    # default
  review_dispatch: true            # default: spawn the assigned profile with
                                   # the bundled sdlc-review skill. Set false
                                   # for human-only review boards.
  # dispatch_profiles: [sage]       # unset (key omitted): this home may claim
                                   # cards for any existing profile. Set to a
                                   # list (or comma-separated string) of profile
                                   # names to restrict which assignees this home
                                   # claims. Fail-closed: an empty list, `null`
                                   # or a bare `dispatch_profiles:` claims
                                   # nothing, and so does an unreadable config.
```

调试时可用 `HERMES_KANBAN_DISPATCH_IN_GATEWAY=0` 在运行时覆盖该配置旗标。标准的 gateway 托管方式照旧适用：直接跑 `hermes gateway start`，或把 gateway 接成 systemd user 单元（见 gateway 文档）。没有运行中的 gateway 时，`ready` 任务会一直待在原地直到它起来——`hermes kanban create` 在创建时就会就此告警。

#### worker 与 systemd cgroup {#systemd-cgroups}

worker 是即发即忘的进程，活得比 dispatcher 的 tick 长，因此只要 dispatcher 跑在某个 systemd 单元内部，worker 就会在自己的 transient scope 中启动（`systemd-run --user --scope --unit hermes-worker-kanban-<task>-run-<run>`），并在该单元退出或重启后继续存活。创建这个 scope 需要派发用户的 session bus（`/run/user/<uid>/bus`）；系统级安装的用户可以用 `sudo loginctl enable-linger <user>` 补一个。

- **Gateway dispatcher**（`dispatch_in_gateway: true`，gateway 由 systemd 托管）：scope 是强制的。如果 bus 不可达，生成会被拒绝，并在卡片上记为一次*基础设施*失败——`spawn_failed` 且 `metadata.infrastructure: true`，`last_failure_error` 里给出 linger 的补救办法，gateway 日志里有一条警告——卡片保持 `ready`。它**不会**推进 `consecutive_failures`，所以主机的一次抖动绝不会把卡片直接停成 `blocked`；重生防护会给重试拉开间隔（`infrastructure_cooldown`，与限流冷却同一窗口），直到 bus 恢复。
- **在你自己的单元里跑 `hermes kanban dispatch`**（`Type=oneshot` 定时器、编排序列服务）：bus 可达时 worker 同样拿到 scope。没有 scope 时 worker 仍会被生成——在*你的*单元的 cgroup 内——dispatcher 会大声记一次日志，说明该单元退出会把它杀掉。默认 `KillMode=control-group` 的 `Type=oneshot` 会在流程结束后一秒内丢掉所有 worker；要么启用 linger 让 scope 能被创建，要么在该单元上设 `KillMode=process`，这样它退出时只杀 dispatcher 自己。

以独立进程运行 `hermes kanban daemon` 已**弃用**；请改用 gateway。如果确实跑不了 gateway（无头主机策略禁止长驻服务等），`--force` 后门会让旧的独立 daemon 多活一个发布周期，但同时对同一个 `kanban.db` 跑 gateway 内嵌 dispatcher 和独立 daemon 会造成认领竞争，不受支持。

### 跨 home 共享看板 {#shared-boards}

在多个 Hermes home（容器、机队主机）里挂载同一个 `kanban.db` 可以共享看板，但 profile 名是 home 本地的，且每个 home 都有一个名为 `default` 的根 profile——因此 `default` 天生就会撞名。dispatcher 的生成闸门会针对*认领方* home 检查 `profile_exists(assignee)`，不做进一步配置时，每个 home 的 dispatcher 都认为指派给 `default` 的卡片可认领，于是错误的 home 可能认领并运行它。要么给每个 home 起唯一的 profile 名、且在共享看板上绝不把卡片指派给 `default`；要么为每个 home 设置 `kanban.dispatch_profiles`，声明该 home 究竟可以认领哪些负责人——任何其他情况都会落进 dispatcher 的 `skipped_nonspawnable` 桶而不被生成，也不再算作 gateway 唤醒探测的可生成工作。

### 幂等创建（用于自动化 / webhook） {#idempotent-create}

```bash
# First call creates the task. Any subsequent call with the same key
# returns the existing task id instead of duplicating.
hermes kanban create "nightly ops review" \
    --assignee ops \
    --idempotency-key "nightly-ops-$(date -u +%Y-%m-%d)" \
    --json
```

### CLI 批量动词 {#bulk-cli-verbs}

所有生命周期动词都接受多个 id，一条命令即可清理一批：

```bash
hermes kanban complete t_abc t_def t_hij --result "batch wrap"
hermes kanban archive  t_abc t_def t_hij
hermes kanban unblock  t_abc t_def
hermes kanban block    t_abc "need input" --ids t_def t_hij
```

:::note 被解除阻塞的任务落到哪里
`unblock` 会把任务恢复到安全的来源阶段：父任务已完成的评审方工作回到 **`review`**，父任务已完成的实现工作回到 **`ready`**，只要还有任一父任务未完成则回到 **`todo`**。`todo` 任务保留其来源阶段的出处，依赖闸门清除后自动回到 `review` 或 `ready`。`unblock` 绝不会直接路由到 `triage`。

如果你解除阻塞一个任务，而它后来出现在 **`triage`**，那不是 unblock 造成的，而是随后*因同一原因再次被阻塞*导致的：任务在阻塞 → 解除阻塞 → 因同一原因再次阻塞累计 `BLOCK_RECURRENCE_LIMIT` 次（默认 `2`）之后，解除阻塞的断路器不再把它送回 `blocked`——在那里 cron 只会不停给它解除阻塞——而是路由到 `triage`，交由编排者处理。这是一个确定性的 DB 守卫，不是 LLM 的判断，任务正文也无法豁免它：复发计数器刻意在每次 unblock 后仍然保留（只有成功的 `complete` 才会清零）。要让一个已解除阻塞的任务留在工作池里，请在解除阻塞前查明*它为何反复再阻塞*（父任务未完成、缺输入、能力不满足），或者在预期就是循环时调高 `BLOCK_RECURRENCE_LIMIT`。
:::

## 为聊天 profile 启用工具 {#enable-tools}

Desktop 的 Kanban 插件只负责显示看板；它不会给聊天 agent 管理任务的权限。为应该编排工作的那个 profile 与平台启用 `kanban` toolset：

```bash
hermes -p planner tools enable kanban                      # CLI / TUI / Desktop chats
hermes -p planner tools enable kanban --platform telegram  # a gateway platform
```

每个平台在 `config.yaml` 的 `platform_toolsets.<platform>` 下有各自的选择；该 toolset 也是 `hermes tools` 与 dashboard 里的一个复选框。拥有它的 gateway agent 可以在聊天中 `kanban_create`，并自动订阅同一话题里该任务的完成/阻塞通知。改完这个设置后请新开一个聊天；既有会话保留它们的工具 schema 与 prompt cache。`agent.disabled_toolsets` 仍然优先。旧式的顶层 `toolsets: [kanban]` 只在没有保存过任何平台选择时作为兜底生效；单独的 `all` 不构成 Kanban 的开启。

dispatcher 持有的 worker 会自动收到它们的任务生命周期工具。`delegate_task` 的子任务不会获得改动看板的权限。

## worker 如何与看板交互 {#worker-interaction}

**Worker 不会 shell 出去执行 `hermes kanban`。** dispatcher 生成 worker 时，会在子进程环境里设 `HERMES_KANBAN_TASK=t_abcd`，这个环境变量会在模型的 schema 里打开一套专用的 **kanban toolset**。同一套 toolset 也提供给在自己的 toolset 配置中启用 `kanban` 的编排者 profile。这些工具经由 Python 的 `kanban_db` 层直接读写看板，与 CLI 一样。运行中的 worker 像调用其他工具一样调用它们；它从来看不到、也不需要 `hermes kanban` CLI。

| 工具 | 用途 | 必需参数 |
|---|---|---|
| `kanban_show` | 读取当前任务（标题、正文、历次尝试、父任务交接、评论、完整预格式化的 `worker_context`）。默认取环境变量里的任务 id。 | — |
| `kanban_list` | 按 `assignee`、`status`、`tenant`、归档可见性与 limit 过滤，列出任务摘要。供编排者发现看板上的工作。 | — |
| `kanban_complete` | 以 `summary` + `metadata` 结构化交接收尾。 | `summary` / `result` 至少一个 |
| `kanban_request_review` | 发起同一张卡的评审，带持久化的 `summary`、可选 `metadata` 与可选评审者 profile。任务进入 `review`；这不是阻塞。 | `summary` |
| `kanban_request_changes` | 评审者在活跃评审 run 中给出的裁定。关闭该 run，重新施加父任务门控，把任务路由回原实现者，且不计入阻塞循环。 | `reason` |
| `kanban_block` | 停止工作并按原因路由：`kind=dependency`（停在 `todo` 等待，父任务完成时自动恢复；若没有未完成的父任务则改记为 `needs_input`，因为这个等待永远无法被满足）、`needs_input`/`capability`/`transient`（上报给人）。同 kind 反复再阻塞会自动升级到 `triage`。 | `reason` |
| `kanban_heartbeat` | 在长操作中报活。纯副作用。 | — |
| `kanban_comment` | 向任务串追加一条持久备注。 | `task_id`、`body` |
| `kanban_attach` | 以内联字节（base64）方式把文件附到任务上；存在该任务的附件目录下（上限 25 MB）。 | 文件字节 + 名称 |
| `kanban_attach_url` | 按 URL 把文件附到任务上。 | `url` |
| `kanban_attachments` | 列出任务的附件。 | — |
| `kanban_create` | （编排者）带 `assignee`、可选 `parents`、`skills` 等扇出为子任务。当有未完成父任务把新卡停在 `todo` 时，返回 `gated: true` + `gated_by`。 | `title`、`assignee` |
| `kanban_link` | （编排者）事后补一条 `parent_id → child_id` 依赖边。当子卡原为 `ready`、因父任务未完成而被降回 `todo` 时，返回 `gated: true`——子卡只会在父任务完成后运行。子卡已被认领时拒绝并报 `child is already running`——认领之后加的边无法串行化这次运行（worker 仍可在 `kind=dependency` 阻塞之前链接*自己*运行中的卡片）。 | `parent_id`、`child_id` |
| `kanban_unblock` | （编排者）把被阻塞的任务恢复到其来源阶段（`review` 或 `ready`），有父任务未完成时则为 `todo`。 | `task_id` |

一个典型的 worker 轮次看起来像：

```
# Model's tool calls, in order:
kanban_show()                                     # no args — uses HERMES_KANBAN_TASK
# (model reads the returned worker_context, does the work via terminal/file tools)
kanban_heartbeat(note="halfway through — 4 of 8 files transformed")
# (more work)
kanban_complete(
    summary="migrated limiter.py to token-bucket; added 14 tests, all pass",
    metadata={"changed_files": ["limiter.py", "tests/test_limiter.py"], "tests_run": 14},
)
```

**编排者**型 worker 则改为扇出：

```
kanban_show()
kanban_create(
    title="research ICP funding 2024-2026",
    assignee="researcher-a",
    body="focus on seed + series A, North America, AI-adjacent",
)
# → returns {"task_id": "t_r1", ...}
kanban_create(title="research ICP funding — EU angle", assignee="researcher-b", body="…")
# → returns {"task_id": "t_r2", ...}
kanban_create(
    title="synthesize findings into launch brief",
    assignee="writer",
    parents=["t_r1", "t_r2"],                     # promotes to ready when both complete
    body="one-pager, 300 words, neutral tone",
)
kanban_complete(summary="decomposed into 2 research tasks + 1 writer; linked dependencies")
```

标注了「（编排者）」的工具——`kanban_list`、`kanban_create`、`kanban_link`、`kanban_unblock`，以及对他人任务的 `kanban_comment`——都在同一套 toolset 里可用；约定（编码在自动注入的 kanban 指引中）是：worker profile 不扇出、不路由无关工作，编排者 profile 不执行实现类工作。dispatcher 生成的 worker 在破坏性生命周期操作上仍受任务范围限制，无法改动无关任务。

### 为什么用工具而不是 shell 调用 `hermes kanban` {#why-tools}

三个理由：

1. **后端可移植性。** 终端工具指向远程后端（Docker / Modal / SSH / 插件沙箱）的 worker，会在容器*内部*执行 `hermes kanban complete`，而那里既没装 `hermes`，也没挂载 `~/.hermes/kanban.db`。kanban 工具跑在 agent 自己的 Python 进程里，无论终端后端是什么都能访问 `~/.hermes/kanban.db`。
2. **没有 shell 引号的脆弱性。** 把 `--metadata '{"files": [...]}'` 穿过 shlex + argparse 是一个潜伏的坑。结构化的工具参数完全绕开它。
3. **更好的错误信息。** 工具结果是模型可以推理的结构化 JSON，而不是它还得去解析的 stderr 字符串。

**普通会话的 schema 零占用。** 常规 `hermes chat` 会话的 schema 里没有任何 `kanban_*` 工具，除非当前 profile 为编排工作显式启用 `kanban` toolset。dispatcher 生成的任务 worker 因为设置了 `HERMES_KANBAN_TASK` 而拿到任务范围的工具；编排者 profile 通过配置拿到更宽的路由接口。从不碰 kanban 的用户不会有工具膨胀。

自动注入的 kanban 指引教模型何时调用哪个工具、按什么顺序。它只注入给拥有该任务的、由 dispatcher 生成的 worker：仅仅启用了 `kanban` toolset 的交互式会话虽然保留这些工具，但不会被告知「你已被分配了**一个**任务」；`delegate_task` 的子任务或在 worker 内部发起的 cron 运行——它们继承了 worker 的 `HERMES_KANBAN_TASK`——既不会收到 worker 协议，也不会在自己的轮次预算耗尽时对 worker 的卡片记终态。

### 建议的交接证据 {#handoff-evidence}

`kanban_complete(summary=..., metadata={...})` 刻意保持灵活：summary 是给人看的结项说明，`metadata` 是给下游 agent、评审者或 dashboard 复用的机器可读交接，不必去刮正文。

对工程与评审类任务，推荐这个可选的 metadata 形状：

```json
{
  "changed_files": ["path/to/file.py"],
  "verification": ["pytest tests/hermes_cli/test_kanban_db.py -q"],
  "dependencies": ["parent task id or external issue, if any"],
  "blocked_reason": null,
  "retry_notes": "what failed before, if this was a retry",
  "residual_risk": ["what was not tested or still needs human review"]
}
```

这些键是约定，不是 schema 要求。它的好处是：每个 worker 都留下足够证据，让下一位读者快速回答四个问题：

1. 改了什么？
2. 怎么验证的？
3. 如果失败，什么能解除阻塞或重试它？
4. 还有哪些风险是刻意留着没关的？

不要把密钥、原始日志、token、OAuth 材料和无关的会话记录放进 `metadata`，改为存指针与摘要。如果任务没有文件或测试，就在 `summary` 里明确说明，并把确实存在的证据放进 `metadata`，例如源码 URL、issue id 或人工评审步骤。

### worker 生命周期 {#worker-lifecycle}

每个处理 kanban 任务的 profile 都会自动获得 worker 生命周期——它在生成时注入 worker 的系统提示（`KANBAN_GUIDANCE` 块），因此**无需安装或配置任何东西**。它用**工具调用**（而不是 CLI 命令）教给 worker 完整的生命周期：

1. 生成后调用 `kanban_show()`，读取标题 + 正文 + 父任务交接 + 历次尝试 + 完整评论串。
2. 用 terminal 工具 `cd $HERMES_KANBAN_WORKSPACE`，在那里干活。
3. 长操作期间每隔几分钟调用一次 `kanban_heartbeat(note="...")`。**如果你的工作可能跑超过 1 小时，至少每小时调用一次 `kanban_heartbeat`** —— 对于已运行超过 `kanban.dispatch_stale_timeout_seconds`（默认 4 小时）、且最近一小时没有心跳的任务，dispatcher 会回收它，前提假设是 worker 崩了没清理。回收是良性的（任务回到 `ready` 重新派发，不给失败计数器加一），但你会丢掉当前 run 的进度。
4. 用 `kanban_complete(summary="...", metadata={...})` 完成；把代码改动交给同卡评审则用 `kanban_request_review(summary="...")`；卡住时用 `kanban_block(reason="...")`。

正常的工具活动也会自动延长认领（worker 大约每分钟把自己的进程内活跃状态镜像到看板上）。这座桥只对 dispatcher 自己生成的进程有效：同时携带 `HERMES_DELEGATED_CHILD_CONTEXT` 与 `HERMES_KANBAN_TASK` 的进程（`delegate_task` 后代，或手工启动的 worker 环境副本）会被挡在看板之外——它的自动心跳会记一条 `kanban auto-heartbeat for task … refused` 警告，`kanban_complete` / `kanban_request_review` 会拒绝。请修的是启动方式（让 dispatcher 来生成 worker），而不是把该标记 export 掉。

最后那次终态看板调用（`kanban_complete` / `kanban_request_review` / `kanban_block`；评审者以 `kanban_complete` 或 `kanban_request_changes` 收尾）是 worker 协议的一部分。如果 worker 进程以状态 0 退出而任务仍是 `running`，dispatcher 会把它当作协议违规并发出 `protocol_violation` 事件。因此 dispatcher 生成的 worker 在轮次失败时以非零码退出：普通失败为 `1`；provider 被限流、过载、返回 5xx 或超时，或账号撞上计费/配额墙时为 `75`（`EX_TEMPFAIL`）——dispatcher 把该 run 记为 `rate_limited` 并重新排队任务、不计一次失败，所以配额窗口绝不会被记成协议违规；provider 拒绝了重试解决不了的东西时为 `78`（`EX_CONFIG`）：profile 的凭据（401/403，被吊销或无效的 key）、模型（404 / model not found）或 TLS 链。

这种**终态 provider 错误**第一次出现就触发熔断器：dispatcher 把该 run 记为 `crashed` 且 `exit_kind: terminal_provider`，发出带 `terminal_provider: true` 的 `gave_up`，并把卡片停成 `blocked`（粘性——`recompute_ready` 不会自动恢复它），`last_failure_error` 里放 provider 自己的原话，而不是反复撞同一堵墙直到 `kanban.failure_limit` / `max_retries` 耗尽。两条通道的记账方式相同：一个死于被吊销 key 的评审者 worker，停卡方式与实现者一模一样。`hermes kanban show` 会把它显示为 *Provider rejected this profile's credential or model — blocked after one attempt*；请修被指派 profile 的 provider（`hermes -p <profile> auth` / `setup`），然后 `hermes kanban unblock <id>`。worker 还会把自己的退出码写成自身日志的最后一行（`[kanban-worker-exit] rc=<code>`），因此每个 tick 跑一次的 `hermes kanban dispatch` 进程——它从未收割 worker、也读不到其退出状态——会以与 gateway 内嵌 dispatcher 相同的方式记下同样的死法；在到达那一行之前被杀掉的 worker 只是一次普通的 `crashed`（`pid <n> not alive`）。

**agent 侧的预防：** worker 退出前，如果检测到模型在没有任何终态看板调用的情况下就要停，Hermes 会注入至多两次合成提醒。这能接住常见情形：模型叙述了下一步（「让我写报告吧」）然后以 `finish_reason=stop` 停下。提醒会要求模型立刻调用 `kanban_complete`、`kanban_request_review` 或 `kanban_block`。已经把卡片交出去的 worker（`kanban_request_review`，或评审者的 `kanban_request_changes`）绝不会被提醒——交接就是它的终态调用，提醒也从不会让它去 `kanban_complete` 一张正在评审中的卡片。该守卫只对 dispatcher 生成的 worker 本身生效（`HERMES_KANBAN_TASK` 已设置且该 run 拥有该任务）——在 worker 内部运行的 `delegate_task` 子任务与 cron 任务会继承这个变量但绝不会被提醒，因为它们没有看板工具——可用 `HERMES_KANBAN_STOP_NUDGE=0` 关闭。

**dispatcher 侧的恢复：** 如果提醒次数用尽，或 worker 在到达提醒之前就崩了，dispatcher 会给这次违规一次**有界重试**（最多 `_PROTOCOL_VIOLATION_FAILURE_LIMIT` 次连续违规，默认 3），之后自动把任务置为阻塞，而不是再生成进同一个循环。这个预算只统计*连续的*干净退出协议违规——穿插其间的限流重排队是中性的，任何其他失败类型都会清零连击——每个任务的 `max_retries` 可以覆盖该上限。被这个预算阻塞的卡片会一直保持阻塞（它不像低于 `failure_limit` 的熔断阻塞那样自动晋级），直到执行 `hermes kanban unblock <id>`，同时获得全新的重试预算。这通常意味着模型写了一段纯文本答案就退出了，根本没用 Kanban 的工具界面。

生命周期细节，加上那些承重的参考细节（workspace 种类、交付物 `artifacts`、认领新建的卡片），都随那个系统提示块一起发布，因此无论 worker 跑在哪个 profile 下都具备这些知识——不需要按 profile 配置 skill。

**Worker 的会话名。** worker 的会话在生成时以它的卡片命名（`Fix the swap modal`；看板行读不到时为 `Kanban task <id>`），所以 `hermes sessions` 与会话搜索显示的是卡片本身，而不是模型的猜测。worker 从不发起给交互式会话命名的辅助 `title_generation` 模型调用；worker 会话里手工执行 `/title` 仍然有效。

### 把额外 skill 固定到特定任务 {#pin-extra-skills}

有时单个任务需要被指派 profile 默认不带的专家上下文——翻译任务需要 `translation` skill，评审任务需要 `github-code-review`，安全审计需要 `security-pr-audit`。与其每次都去改被指派者的 profile，不如把 skill 直接挂到任务上。

**来自编排者 agent**（常见情形——一个 agent 把工作路由给另一个），用 `kanban_create` 工具的 `skills` 数组：

```
kanban_create(
    title="translate README to Japanese",
    assignee="linguist",
    skills=["translation"],
)

kanban_create(
    title="audit auth flow",
    assignee="reviewer",
    skills=["security-pr-audit", "github-code-review"],
)
```

**来自人（CLI / 斜杠命令）**，每个 skill 重复一次 `--skill`：

```bash
hermes kanban create "translate README to Japanese" \
    --assignee linguist \
    --skill translation

hermes kanban create "audit auth flow" \
    --assignee reviewer \
    --skill security-pr-audit \
    --skill github-code-review
```

**来自 dashboard**，在创建任务对话框的 **skills** 字段里用逗号分隔填写。

dispatcher 会为列出的每个 skill 发出一个 `--skills <name>` 旗标，于是 worker 生成时，除了自动注入的 kanban 指引，还会加载全部这些 skill。skill 名必须与被指派 profile 上实际安装的 skill 匹配（跑 `hermes skills list` 可看有哪些）；没有运行时安装。

### 按任务覆盖模型 {#per-task-model}

把任务的 worker 钉到特定模型（也可指定 provider），独立于被指派 profile 的默认值：

```bash
# At creation
hermes kanban create "hard refactor" --assignee coder \
    --model claude-opus-4.6 --provider anthropic

# Or later — takes effect on the next dispatch
hermes kanban set-model t_abcd claude-opus-4.6 --provider anthropic
hermes kanban set-model t_abcd none    # clear the override
```

dispatcher 用钉住的模型生成 worker（设置了 `--provider <name>` 时会传入；`--provider` 需要同时给 model）。dashboard 的按任务模型下拉框驱动同一个 `model_override` 字段。没有覆盖时，worker 使用其 profile 配置的模型。

### 成本策略：前沿模型做编排，廉价模型做 worker {#cost-strategy}

Kanban 的按 profile 配置让规划者/worker 的成本切分很自然。把一个项目拆成边界清晰的卡片需要前沿级的判断力；执行一张已经带着明确目标、上下文与交接证据的卡片通常不需要——而绝大多数 token 都花在 worker 身上，所以成本就在 worker 模型上。用前沿模型跑你的编排者/dispatcher profile，把 worker profile 指向廉价模型。每个 profile 在 `~/.hermes/profiles/<name>/` 下有自己的 `config.yaml`，dispatcher 生成 `hermes -p <assignee>` 时会注入按 profile 划分的 `HERMES_HOME`，因此每个 worker 读到的都是自己 profile 的模型设置：

```yaml
# ~/.hermes/config.yaml (orchestrator / dispatcher profile)
model:
  default: "your-frontier-model"

# ~/.hermes/profiles/coder/config.yaml (worker profile)
model:
  default: "your-inexpensive-model"

# ~/.hermes/profiles/researcher/config.yaml (another worker profile)
model:
  default: "your-inexpensive-model"
```

对偶尔那些质量敏感的卡片，用[按任务覆盖模型](#per-task-model)把那一个任务钉回更强的模型（创建时 `--model`/`--provider`、之后 `hermes kanban set-model`，或 dashboard 的模型下拉框）——无需改任何 profile。

### 生命周期插件钩子 {#lifecycle-hooks}

看板状态转移会触发[插件钩子](./hooks.md#plugin-hooks)：`kanban_task_claimed`、`kanban_task_completed`、`kanban_task_blocked`，每个都带 `task_id` 与 `profile_name`。钩子在看板 DB 变更**提交之后**触发，因此回调看到的永远是持久状态。注意进程的划分：`kanban_task_claimed` 在 **dispatcher** 进程里触发，而 `kanban_task_completed`/`kanban_task_blocked` 在 **worker** 进程里触发——把钩子注册在 dispatcher profile 上，才能集中观测所有转移。

```python
def register(ctx):
    def on_blocked(task_id=None, profile_name=None, **kw):
        ctx.dispatch_tool("terminal", {"command": f"notify-send 'kanban blocked: {task_id}'"})
    ctx.register_hook("kanban_task_blocked", on_blocked)
```

### goal 模式卡片（`--goal`） {#goal-cards}

默认情况下每个 worker 对它的卡片只有**一次机会**——干活、调用 `kanban_complete`/`kanban_block`、退出。传 `--goal`（CLI）或 `goal_mode=True`（`kanban_create` 工具 / dashboard），则改为让该 worker 跑在**goal 循环**里，也就是 `/goal` 斜杠命令背后那套同款 Ralph 风格引擎：每一轮之后，一个辅助裁判会拿卡片的标题 + 正文（视为验收标准）核对 worker 的产出；如果活没干完——且轮次预算还有——worker 就**在同一会话里**继续干，直到裁判认可、worker 自己终止任务，或预算耗尽（此时会把卡片**置为阻塞**交人工评审，而不是静默退出）。如果裁判裁定按当前写法 goal **不可达成**，卡片会立即带着裁判给出的理由被阻塞——不可能完成的卡片绝不会被标为 done，对这种卡片执行 `kanban complete` / `kanban request-review` 会被拒绝，并提示改用 `kanban block` 或重新界定范围。

```bash
hermes kanban create "Translate the docs site to French" \
    --body "Acceptance: every page translated, no English left, links intact." \
    --assignee linguist \
    --goal \
    --goal-max-turns 15      # optional; default 20
```

开放式、多步骤或「一直干到 X 成立」的卡片适合用它。一次性的廉价活就别用——每轮裁判的开销不划算，而且 dispatcher 现有的重试/熔断已经能处理 worker 的临时故障。裁判的效果取决于你的 goal 文本，所以请把正文写成**明确的验收标准**。

`kanban complete` / `kanban request-review` 上的裁判闸门（以及对应的 `kanban_complete` / `kanban_request_review` 工具）只在拿到**真实裁定**时才拒绝。如果裁判调用本身失败——中继错误、鉴权、超时——交接会被放行，日志里落一条 `goal judge unreachable … allowing lifecycle handoff` 警告，因此裁判不可达绝不会挡住人工批准。无头 CLI 闸门会发送与 `specify`/`decompose` 相同的按任务中继亲和键（`kanban:<task-id>`），于是要求会话键的中继会接受裁判请求。

goal 模式 worker 的 **Worker log**（dashboard 抽屉、`hermes kanban log <id>`）与其他 worker 一样带实时工具流，另外每个被裁判的轮次多一行 `kanban goal loop: turn N/M verdict=…`，卡片运行时你就能跟进循环在做什么。

:::note goal 模式卡片借用 `/goal` 引擎，但不接入它
`--goal` 是在*那张卡片自己的 worker 会话内部*跑续写循环。它与 [`/goal` 斜杠命令](./goals)共享引擎，但不共享状态：在聊天会话里设置 `/goal` 绝不会创建、认领或移动 kanban 卡片，goal 模式卡片的循环对任何聊天会话的 `/goal status` 都不可见。想让这段对话继续迭代，用 [`/goal`](./goals)；想让看板上有活干，就建一张卡。
:::

### 编排者如何表现 {#orchestrator-behavior}

**守规矩的编排者不亲自干活。** 它把用户的目标拆成任务、建立链接、把每条分给你配好的某个 profile，然后退到一边。编排者指引——反诱惑规则、Step-0 的 profile 发现提示（dispatcher 对未知的被指派者名字会静默失败，所以编排者必须把每张卡都落在你机器上真实存在的 profile 上）、以及以 `kanban_create` / `kanban_link` / `kanban_comment` 为核心的拆解手册——会自动注入 worker 的系统提示；无需安装任何东西。

一个典型的编排者轮次（两个并行研究者交接给一位写作者）：

```
# Goal from user: "draft a launch post on the ICP funding landscape"
kanban_create(title="research ICP funding, NA angle",  assignee="researcher-a", body="…")  # → t_r1
kanban_create(title="research ICP funding, EU angle",  assignee="researcher-b", body="…")  # → t_r2
kanban_create(
    title="synthesize ICP funding research into launch post draft",
    assignee="writer",
    parents=["t_r1", "t_r2"],        # promoted to 'ready' when both researchers complete
    body="one-pager, neutral tone, cite sources inline",
)                                     # → t_w1
# Optional: add cross-cutting deps discovered later without re-creating tasks
kanban_link(parent_id="t_r1", child_id="t_followup")
kanban_complete(
    summary="decomposed into 2 parallel research tasks → 1 synthesis task; writer starts when both researchers finish",
)
```

编排者指引会自动随 worker 的系统提示一起发布——无需按 profile 安装或同步任何东西。

**扇出之前先做决定。** 设计决策属于编排者，不属于 worker。如果两张并行卡片各自都得选同一件事——命名方案、schema、文件格式、API 形状——就由编排者定一次，并把这个决定同时盖进**两张**卡片的正文。worker 看不到兄弟卡片，所以每张子卡的正文必须带上它依赖的全部决定。例子：并行的「做 exporter」和「做 importer」两张卡，别让两个 worker 各发明一套文件格式——先定一种（比如换行分隔、带 `version` 字段的 JSON），写进两份正文，否则两半永远对不上。

效果最好的搭配，是给它一个 toolset 被限制为看板操作（`kanban`、`gateway`、`memory`）的 profile，这样编排者即使想执行实现类任务也做不到。

## Dashboard（GUI） {#dashboard}

`/kanban` CLI 与斜杠命令足以无头运行看板，但对留在环路里的人来说，可视化看板往往才是对的界面：分诊、跨 profile 监督、读评论串、在列之间拖卡片。Hermes 把它作为**随附的 dashboard 插件**发布在 `plugins/kanban/` —— 不是核心功能，也不是独立服务——遵循 [Extending the Dashboard](./extending-the-dashboard) 中给出的模式。

这样打开它：

```bash
hermes kanban init      # one-time: create kanban.db if not already present
hermes dashboard        # "Kanban" tab appears in the nav, after "Skills"
```

### 这个插件给你什么 {#plugin-capabilities}

- 一个 **Kanban** 标签页，每个状态一列：`triage`、`todo`、`ready`、`running`、`blocked`、`done`（开关打开时还有 `archived`）。
  - 队列列按派发顺序列出卡片（优先级，然后最早的在前——最上面的卡片下一个被生成）。`done` 列是历史，最新完成的在前；CLI 上 `hermes kanban list --status done --sort completed-desc` 给出同样顺序。
  - `triage` 是粗略想法的停放列。默认（`kanban.auto_decompose: true`）下，dispatcher 会自动对落到这里的任务跑**decomposer**。内置 decomposer 走 `auxiliary.kanban_decomposer` 模型路径，读你的 profile 名册（含描述），把任务扇出成一张小的子任务图，按描述路由给最合适的专家。原任务作为所有子任务的父任务保持存活，于是等全部完成后，它的负责人（`kanban.orchestrator_profile`，否则任务原本的负责人，否则当前激活的 default profile）会被唤醒来判定是否完成。可以在页面顶部的 **Orchestration: Auto/Manual** 药丸开关切换（祖母绿 = Auto，灰 = Manual），或直接编辑 `config.yaml`。两种模式都与 `hermes kanban specify` 共存——当你不想要扇出时，它仍可用作单任务的 spec 重写。
- 卡片显示任务 id、标题、优先级徽章、租户标签、被指派 profile、评论/链接数量、一个**进度药丸**（任务有依赖时显示 `N/M` 个子任务已完成），以及「创建于 N 之前」。每张卡的复选框支持多选。
- **Running 内的按 profile 泳道** —— 工具栏复选框把 Running 列按被指派者分子组。
- **经 WebSocket 的实时更新** —— 插件以短轮询间隔 tail 只追加的 `task_events` 表；任何 profile（CLI、gateway 或另一个 dashboard 标签页）一有动作，看板立刻反映变化。重载做了去抖，一串事件只触发一次重新拉取。
- **拖放** 卡片跨列以改状态。放下时发送 `PATCH /api/plugins/kanban/tasks/:id`，经由 CLI 使用的同一套 `kanban_db` 代码路由——三个界面绝不会漂移。移入破坏性状态（`done`、`archived`、`blocked`）会要求确认。触摸设备使用基于指针的回退方案，平板上也能用。
- **创建任务对话框** —— 点任意列头的 `+` 打开带标签字段的弹窗：标题、负责人、优先级、skill、workspace 种类/路径（从看板的项目目录播种；按任务可覆盖）、goal 模式，以及（可选）从所有既有任务下拉选择的父任务。回车创建任务，Shift+Enter 在标题字段换行，Escape 取消。从 Triage 列创建会自动把新任务停进 triage。
- **多选 + 批量操作** —— shift/ctrl 点击卡片或勾选其复选框加入选择。顶部出现批量操作条，含批量状态转移、归档与改派（按 profile 下拉，或「(unassign)」）。破坏性批量先确认。按 id 的部分失败会被报告，不中断其余操作。
- **点开一张卡**（不带 shift/ctrl）会打开侧边抽屉（Escape 或点外面关闭），内含：
  - **可编辑标题** —— 点标题即可改名。
  - **可编辑负责人 / 优先级** —— 点元信息行即可改写。
  - **可编辑描述** —— 默认按 markdown 渲染（标题、粗体、斜体、行内代码、围栏代码、`http(s)` / `mailto:` 链接、项目符号列表），带一个「edit」按钮切换成 textarea。markdown 渲染用的是一个极小、XSS 安全的渲染器：所有替换都作用在 HTML 转义后的输入上，只有 `http(s)` / `mailto:` 链接会放行，并且总是设置 `target="_blank"` + `rel="noopener noreferrer"`。
  - **依赖编辑器** —— 父/子的 chip 列表，每个带 `×` 可解除链接，另有覆盖所有其他任务的下拉框用于新增父或子。成环尝试会在服务端被拒绝并给出清晰提示。
  - **状态操作行**（→ triage / → ready / → running / block / unblock / complete / archive），破坏性转移带确认提示。对 **Triage** 列的卡片，该行还暴露两个 LLM 驱动的动作：**⚗ Decompose** 把任务按描述路由到专家 profile、扇出成子任务图；**✨ Specify** 做单任务 spec 重写。当 LLM 认为任务不值得扇出时，Decompose 会回退为 specify 式的晋级，因此它是严格的超集。两者都能从 CLI（`hermes kanban decompose <id>` / `specify <id>` / `--all`）、任一 gateway 平台（`/kanban decompose <id>`）以及 `POST /api/plugins/kanban/tasks/:id/decompose` 与 `…/specify` 程序化调用。相关模型在 `config.yaml` 的 `auxiliary.kanban_decomposer` 与 `auxiliary.triage_specifier` 下配置。
  - 结果区域（同样按 markdown 渲染）、回车即发的评论串、最近 20 条事件。
- **工具栏过滤** —— 自由文本搜索、租户下拉（默认取 `config.yaml` 的 `dashboard.kanban.default_tenant`）、负责人下拉、「显示归档」开关、「按 profile 分泳道」开关，以及一个 **Nudge dispatcher** 按钮，让你不必等下一个 60 秒 tick。

视觉上目标是大家熟悉的 Linear / Fusion 布局：深色主题、带计数的列头、彩色状态点、优先级与租户的 pill chip。插件只读主题 CSS 变量（`--color-*`、`--radius`、`--font-mono` …），因此会随当前 dashboard 主题自动换肤。

### 自动编排 vs 手动编排 {#auto-vs-manual}

kanban 看板有两种方式处理你丢进 Triage 列的任务：

**Auto（默认）** —— `kanban.auto_decompose: true`。gateway 内嵌的 dispatcher 每个 tick 都跑一次 **decomposer**，上限由 `kanban.auto_decompose_per_tick` 控制（默认每 tick 3 个任务），这样批量涌入的 triage 任务不会突发烧掉辅助 LLM。decomposer 用内置拆解提示加 `auxiliary.kanban_decomposer` 模型路径，读你已安装的 profile 及其描述，让 LLM 产出一张 JSON 任务图：要生成哪些任务、交给谁、谁依赖谁。原 triage 任务成为图中每个叶子的父任务，因此它活到整张图完成为止——随后再晋级回 `ready`，让它的负责人（`kanban.orchestrator_profile`，否则任务原本的负责人，否则当前激活的 default profile）判定完成情况，若活没干完就继续加任务。这就是「丢一行话，走开」的流程。

一次完成的内置扇出会与它的子任务图一起原子记录。把该根任务移回 Triage 不会再建一张图；普通的前置链接不会阻碍任务的首次拆解。完成标记会一直保留（扛住事件保留策略），直到任务被删除。这不是对独立手工建图的语义去重，也不是对早先被裁剪历史的修复。

新任务未指定租户时，创建会按给定顺序继承其父任务中第一个非空租户。显式租户（包括工具传入的 worker 活跃租户）优先。看板仍然是硬隔离边界。

**Manual** —— `kanban.auto_decompose: false`。triage 任务留在 triage，直到你动手。点卡片上的 **⚗ Decompose** 按钮、跑 `hermes kanban decompose <id>`（或 `--all`），或在聊天里用 `/kanban decompose <id>`。这与 decomposer 出现之前的看板行为一致，适合你想完全控制何时跑什么的场合。

**重要边界：** Manual 模式只关掉内置的 Triage decomposer。它不阻止某个 profile 调用 `kanban_create`，也不关闭创建者会话的唤醒。开启 `kanban.auto_subscribe_on_create: true` 时，任务的终态事件会用一个合成状态轮次唤醒发起它的 agent，让它查看交接、判断是否真有新的后续工作要做。如果任务完成应当保持被动，设 `auto_subscribe_on_create: false`。为保持出处，内置 decomposer 的子任务用 `created_by=auto-decomposer`；由被唤醒 profile 创建的任务则带该 profile 名。

在 kanban 页面顶部的 **Orchestration: Auto/Manual** 药丸（祖母绿 = Auto，灰 = Manual）之间切换，或直接编辑 `config.yaml`。两种模式都与 `hermes kanban specify` 共存——当你不想要扇出时，它仍可用作单任务的 spec 重写。

decomposer 的路由决定依赖 profile 描述，这是按 profile 的标注原语，可用 `hermes profile create --description "..."`、`hermes profile describe <name> --text "..."`、`hermes profile describe <name> --auto`（由该 profile 已安装的 skill + 模型生成），或在展开的 **Orchestration settings** 面板里用 dashboard 的按 profile 编辑器来设置。没有描述的 profile 仍会出现在名册中——可按名路由，只是不那么精确。decomposer **绝不会**把子任务落到 `assignee=None`：当 LLM 选了未知 profile，子任务会被路由到 `kanban.default_assignee`，否则根任务的负责人（如果它指向存在的 profile），否则当前激活的 default profile。

`kanban.orchestrator_profile` 并不会把该 profile 的 prompt、skill 或自定义逻辑加载进拆解调用，它控制的是扇出之后谁拥有根/编排任务。要改 decomposer 的模型/provider，配置 `auxiliary.kanban_decomposer`。要用某个 profile 的自定义任务拆分逻辑替代内置 decomposer，切到 Manual 模式，让该 profile 显式创建或拆解任务。

配置开关（都在 `~/.hermes/config.yaml` 的 `kanban:` 下）：

| 键 | 默认 | 用途 |
|---|---|---|
| `auto_decompose` | `true` | dispatcher 每个 tick 自动对 Triage 任务跑内置 decomposer。它不约束 profile 发起的 `kanban_create` 调用，也不约束创建者唤醒轮次。 |
| `auto_decompose_per_tick` | `3` | 每个 dispatcher tick 的拆解上限，超出的推迟到下一 tick。 |
| `orchestrator_profile` | `""` | 拆解后指派给根/编排任务的 profile。空 = 根任务保留自己的负责人，否则用当前激活的 default profile。 |
| `default_assignee` | `""` | LLM 选了未知 profile 时子任务落到哪里。空 = 回退到根任务的负责人，否则当前激活的 default。 |
| `auto_subscribe_on_create` | `true` | 当 `kanban_create` 在持久 gateway/TUI 会话内运行时，终态事件会用合成状态轮次唤醒发起它的 agent。要被动完成、或要求显式 `kanban_notify-subscribe` 调用，设为 `false`。与 `auto_decompose` 互相独立。 |
| `notify_in_gateway` | `true` | 由该 gateway 轮询并投递 Kanban 订阅。不拥有任何通知订阅的 profile 上设为 `false`，可停掉空闲的每五秒通知轮询。与 `dispatch_in_gateway` 互相独立；非派发 gateway 仍可能拥有按 profile 的投递适配器。 |
| `done_sub_retention_days` | `30` | 通知订阅在 `done` 后仍存活（可安全重开），到 `archived` 时移除。通知器 GC 会清理其任务已 `done` 或 `blocked` 且这么多天没有新事件的订阅，从而限制从不归档的看板上订阅表的增长。`0` 关闭该清扫。 |

以及两个辅助 LLM 槽位：

| 键 | 用途 |
|---|---|
| `auxiliary.kanban_decomposer` | 产出任务图的模型（由 Decompose 调用）。设 `provider`/`model` 可覆盖主聊天模型。 |
| `auxiliary.profile_describer` | 自动生成 profile 描述的模型（由 `hermes profile describe --auto` 调用）。 |

### 架构 {#architecture}

GUI 严格是一个**读穿 DB、写穿 kanban_db** 的层，自身没有任何领域逻辑：

<!-- ascii-guard-ignore -->
```
┌────────────────────────┐      WebSocket (tails task_events)
│   React SPA (plugin)   │ ◀──────────────────────────────────┐
│   HTML5 drag-and-drop  │                                    │
└──────────┬─────────────┘                                    │
           │ REST over fetchJSON                              │
           ▼                                                  │
┌────────────────────────┐     writes call kanban_db.*        │
│  FastAPI router        │     directly — same code path      │
│  plugins/kanban/       │     the CLI /kanban verbs use      │
│  dashboard/plugin_api.py                                    │
└──────────┬─────────────┘                                    │
           │                                                  │
           ▼                                                  │
┌────────────────────────┐                                    │
│  ~/.hermes/kanban.db   │ ───── append task_events ──────────┘
│  (WAL, shared)         │
└────────────────────────┘
```
<!-- ascii-guard-ignore-end -->

### REST 接口 {#rest-surface}

所有路由挂在 `/api/plugins/kanban/` 下，由 dashboard 的临时会话 token 保护：

| 方法 | 路径 | 用途 |
|---|---|---|
| `GET` | `/board?tenant=<name>&include_archived=…` | 按状态列分组的完整看板，外加过滤下拉所需的租户 + 负责人 |
| `GET` | `/tasks/:id` | 任务 + 评论 + 事件 + 链接 |
| `POST` | `/tasks` | 创建（封装 `kanban_db.create_task`，接受 `triage: bool` 与 `parents: [id, …]`） |
| `PATCH` | `/tasks/:id` | 状态 / 负责人 / 优先级 / 标题 / 正文 / 结果 |
| `POST` | `/tasks/bulk` | 对 `ids` 中每个 id 应用同样的 patch（状态 / 归档 / 负责人 / 优先级）。按 id 报告失败，不中断其余 |
| `POST` | `/tasks/:id/comments` | 追加一条评论 |
| `POST` | `/tasks/:id/specify` | 跑 triage specifier——辅助 LLM 充实任务正文并把它从 `triage` 晋级到 `todo`。返回 `{ok, task_id, reason, new_title}`；`ok=false` 加人可读原因的「不在 triage」/无 aux client / LLM 错误是 200，不是 4xx |
| `POST` | `/tasks/:id/decompose` | 跑 kanban decomposer——辅助 LLM 产出任务图，helper 原子地创建子任务 + 链接根任务 + 翻转 `triage → todo`。返回 `{ok, task_id, reason, fanout, child_ids, new_title}`。LLM 错误同样按 200 返回，约定同 `/specify`。 |
| `GET` | `/profiles` | 列出已安装 profile 及其描述（供 dashboard 的 profile 描述编辑器与编排者选择器消费）。 |
| `PATCH` | `/profiles/:name` | 设置或清除某 profile 的描述（用户撰写——`description_auto: false`）。返回 `{ok, profile, description}`。 |
| `POST` | `/profiles/:name/describe-auto` | 经 `auxiliary.profile_describer` 为 profile 生成描述。以 `description_auto: true` 持久化，dashboard 可据此显示「review」徽章。 |
| `GET` | `/orchestration` | 读取 kanban 编排设置（`orchestrator_profile`、`default_assignee`、`auto_decompose`）以及回退后*实际生效*的值。 |
| `PUT` | `/orchestration` | 更新 `config.yaml` 中这三个编排键的一个或多个。会校验非空 profile 名确实存在。 |
| `POST` | `/links` | 添加依赖（`parent_id` → `child_id`） |
| `DELETE` | `/links?parent_id=…&child_id=…` | 移除依赖 |
| `POST` | `/dispatch?max=…&dry_run=…` | 推一下 dispatcher——跳过 60 秒等待 |
| `GET` | `/config` | 从 `config.yaml` 读取 `dashboard.kanban` 偏好——`default_tenant`、`lane_by_profile`、`include_archived_by_default`、`render_markdown` |
| `WS` | `/events?since=<event_id>` | `task_events` 行的实时流。不带 `since` 时流从看板当前尾部开始（`/board` 快照已含历史）；传 `since=<latest_event_id>` 可从那里追平，传 `since=0` 则回放全部历史 |

每个 handler 都是薄封装——插件约 700 行 Python（router + WebSocket tail + 批量批处理器 + 配置读取器），不新增任何业务逻辑。一个小小的 `_conn()` 辅助函数在每次读写时自动初始化 `kanban.db`，所以无论用户先打开 dashboard、直接打 REST API，还是先跑 `hermes kanban init`，全新安装都能工作。

### Dashboard 配置 {#dashboard-config}

`~/.hermes/config.yaml` 里 `dashboard.kanban` 下的这些键可以改标签页的默认值——插件在加载时经 `GET /config` 读取：

```yaml
dashboard:
  kanban:
    default_tenant: acme              # preselects the tenant filter
    lane_by_profile: true             # default for the "lanes by profile" toggle
    include_archived_by_default: false
    render_markdown: true             # set false for plain <pre> rendering
```

每个键都可选，缺省时回落到上面显示的默认值。

### 安全模型 {#security-model}

dashboard 的 HTTP 鉴权中间件[显式跳过 `/api/plugins/`](./extending-the-dashboard#backend-api-routes)——插件路由按设计是不鉴权的，因为 dashboard 默认只绑定 localhost。这意味着 kanban 的 REST 接口从主机上的任何进程都能访问。

WebSocket 多走一步：它要求把 dashboard 的临时会话 token 作为 `?token=…` 查询参数（浏览器无法在升级请求上设置 `Authorization`），与浏览器内 PTY 桥所用的模式一致。

如果你跑 `hermes dashboard --host 0.0.0.0`，每个插件路由——包括 kanban——都变得可从网络访问。**别在共享主机上这么做。** 看板里有任务正文、评论与工作区路径；能摸到这些路由的攻击者不仅获得对整个协作界面的读权限，还能创建 / 改派 / 归档任务。

`~/.hermes/kanban.db` 里的任务刻意与 profile 无关（这正是协作原语）。如果你用 `hermes -p <profile> dashboard` 打开 dashboard，看板仍会显示主机上任何其他 profile 创建的任务。所有 profile 归同一用户所有，但如果有多个角色并存，这一点值得知道。

### 实时更新 {#live-updates}

`task_events` 是一张带单调 `id` 的只追加 SQLite 表。WebSocket 端点记住每个客户端最后见到的事件 id，新行落库即推送。当一串事件到达时，前端重新拉取（极便宜的）看板端点——比针对每种事件类型去 patch 本地状态更简单也更正确。WAL 模式意味着读循环永远不会阻塞 dispatcher 的 `BEGIN IMMEDIATE` 认领事务。

### 扩展它 {#extending}

插件使用标准的 Hermes dashboard 插件契约——完整的 manifest 参考、shell 槽位、页面作用域槽位与 Plugin SDK 见 [Extending the Dashboard](./extending-the-dashboard)。额外的列、按租户过滤的布局，或整块 `tab.override` 替换，都可以表达而无需 fork 本插件。dashboard 没有按卡片的槽位；在桌面看板上，插件通过 `KANBAN_CARD_AREAS.badges` 贡献区添加按卡片的标签（见 [Desktop Plugin SDK](../../developer-guide/desktop-plugin-sdk.md#kanban-card-badges)）。

不删除只想禁用：往 `config.yaml` 加 `dashboard.plugins.kanban.enabled: false`（或删掉 `plugins/kanban/dashboard/manifest.json`）。

### 范围边界 {#scope-boundary}

GUI 刻意做薄。插件做的每件事都能从 CLI 触达；插件只是让它对人更舒服。自动指派、预算、治理闸门与组织架构视图仍留在用户空间——一个 router profile、另一个插件，或复用 `tools/approval.py` —— 正如设计规格的范围之外一节所列。

## CLI 命令参考 {#cli-reference}

这是**你**（或脚本、cron、dashboard）用来驱动看板的接口。跑在 dispatcher 内部的 worker 对同样的操作使用 `kanban_*` [工具接口](#worker-interaction)——这里的 CLI 与那里的工具都经由 `kanban_db` 路由，因此两个界面在构造上就是一致的。

```
hermes kanban init                                     # create kanban.db + print daemon hint
hermes kanban create "<title>" [--body ...] [--assignee <profile>]
                                [--parent <id>]... [--tenant <name>]
                                [--workspace scratch|worktree|worktree:<path>|dir:<path>]
                                [--branch <name>]
                                [--priority N] [--triage] [--idempotency-key KEY]
                                [--max-runtime 30m|2h|1d|<seconds>]
                                [--max-retries N]
                                [--goal] [--goal-max-turns N]
                                [--skill <name>]...
                                [--json]
hermes kanban list [--mine] [--assignee P] [--status S] [--tenant T] [--archived]
        [--workflow-template-id <id>] [--current-step-key <key>]
        [--sort completed-desc|created|created-desc|priority|priority-desc|status|assignee|title|updated]
        [--json]
hermes kanban show <id> [--json]
hermes kanban assign <id> <profile>                    # or 'none' to unassign
hermes kanban reassign <id>... <profile>               # bulk re-assign tasks to a profile
hermes kanban edit <id> [--title ...] [--body ...]     # edit task title / body / priority in place
        [--priority N]
hermes kanban promote <id>...                          # move todo/blocked tasks to ready (recovery)
hermes kanban schedule <id> --at <ISO8601>             # set/clear a task's scheduled_at start time
hermes kanban diagnostics [--json]                     # board health snapshot (alias: diag)
hermes kanban link <parent_id> <child_id>
hermes kanban unlink <parent_id> <child_id>
hermes kanban claim <id> [--ttl SECONDS]
hermes kanban comment <id> "<text>" [--author NAME]

# Bulk verbs — accept multiple ids:
hermes kanban complete <id>... [--result "..."] [--force]
hermes kanban block <id> "<reason>" [--ids <id>...]
hermes kanban unblock <id>...
hermes kanban archive <id>...

hermes kanban request-review <id> [--summary "..."] [--metadata JSON] [--reviewer PROFILE]
hermes kanban request-changes <id> "<required changes>"               # active reviewer -> implementer
hermes kanban reopen-review  <id>... [--reason "..."]                 # changes requested: 'review' -> ready/todo

hermes kanban tail <id>                                # follow a single task's event stream
hermes kanban watch [--assignee P] [--tenant T]        # live stream ALL events to the terminal
        [--kinds completed,blocked,…] [--interval SECS]
hermes kanban heartbeat <id> [--note "..."]            # worker liveness signal for long ops
hermes kanban runs <id> [--json]                       # attempt history (one row per run)
hermes kanban assignees [--json]                       # profiles on disk + per-assignee task counts
hermes kanban dispatch [--dry-run] [--max N]           # one-shot pass
        [--failure-limit N] [--json]
hermes kanban daemon --force                           # DEPRECATED — standalone dispatcher (use `hermes gateway start` instead)
        [--failure-limit N] [--pidfile PATH] [-v]
hermes kanban stats [--json]                           # per-status + per-assignee counts
hermes kanban log <id> [--tail BYTES]                  # worker log from ~/.hermes/kanban/logs/
hermes kanban notify-subscribe <id>                    # gateway bridge hook (used by /kanban in the gateway)
        --platform <name> --chat-id <id> [--thread-id <id>] [--user-id <id>]
        [--chat-type dm|group|channel|thread] [--delivery-mode notify|notify+wake|wake]
hermes kanban notify-list [<id>] [--json]
hermes kanban notify-unsubscribe <id>
        --platform <name> --chat-id <id> [--thread-id <id>]
hermes kanban context <id>                             # what a worker sees
hermes kanban specify [<id> | --all] [--tenant T]      # flesh out a triage-column idea
        [--author NAME] [--json]                       #   into a full spec and promote to todo
hermes kanban gc [--event-retention-days N]            # workspaces + old events + old logs
        [--log-retention-days N]                       #   (negative N is rejected; 0 disables that sweep)
```

所有命令在交互式 CLI 与消息网关中也都能作为斜杠命令使用（见下文的 [`/kanban` 斜杠命令](#kanban-slash-command)）。

`--max-retries` 是 dispatcher 的按任务熔断覆盖。`--max-retries 1` 会在第一次非成功尝试后阻塞任务，而 `--max-retries 3` 允许两次重试、第三次失败时阻塞。省略它则使用 `config.yaml` 里的 `kanban.failure_limit`，再往后才是内置默认值。

### 并发、调度与子任务晋级配置 {#concurrency-config}

| 配置键 | 默认 | 作用 |
|------------|---------|--------------|
| `kanban.max_in_progress` | 未设置（不限） | 限制同时运行的任务数。看板上已有 N 个在跑时，dispatcher 跳过更多生成——对慢 worker（本地 LLM、资源受限主机）有用，让它们先干完手头的活，免得更多堆积后超时。非法或小于 1 的值会记一条警告并按不限处理。 |
| `kanban.max_in_progress_per_profile` | 未设置（不限） | `max_in_progress` 的按 profile 变体——限制单个被指派 profile 同时能跑多少任务。当某个 profile 慢或被限流、而其他 profile 应当继续流动时有用。与看板级的 `max_in_progress` 并行生效；两者都放行才能生成。 |
| `kanban.dispatch_profiles` | 未设置（任何已存在的 profile） | 面向跨 Hermes home 共享看板的按 home 认领白名单。该键存在时，本 home 的 dispatcher 只认领被指派者在列表中的卡片——失败即关闭：空列表、`null` 或光秃秃的 `dispatch_profiles:` 什么都不认领，配置读取失败也会记警告且什么都不认领；其他被指派者落进 `skipped_nonspawnable`。只有完全省略该键才意味着「任何已存在的 profile」。`hermes kanban diagnostics` 会打印本 home 解析后的值（`any`、列出的名字，或 `none (fail-closed: …)`）。见[跨 home 共享看板](#shared-boards)。 |
| `kanban.auto_promote_children` | `true` | `decompose_triage_task()` 产出的子任务若没有父级阻塞依赖，会自动晋级为 `ready`，让 dispatcher 能捡起它们。设为 `false` 则要求人工评审——子任务留在 `todo`，直到你晋级它们。 |
| `kanban.default_workdir` | 未设置 | 看板级默认工作目录，当 `--workspace` 与任务本身都没有覆盖时应用到新任务。按任务的 `workspace:` 仍然优先。 |

```yaml
kanban:
  max_in_progress: 2
  auto_promote_children: false
  default_workdir: ~/work/active-project
```

### 定时启动任务（`scheduled_at`） {#scheduled-at}

给任务设 `scheduled_at` 可以把派发推迟到指定时刻。dispatcher 会跳过 `scheduled_at` 还在未来的就绪任务，在该时间戳之后的第一个 tick 捡起它们。

```bash
hermes kanban create "nightly backup audit" \
  --assignee ops --scheduled-at "2026-06-01T03:00:00Z"
```

### 重生防护 {#respawn-guard}

满足以下任一条件时，dispatcher 拒绝重新生成一个就绪任务：上一次 run 撞到配额/鉴权/429 错误（`blocker_auth`）、在防护窗口内成功完成过一次 run（`recent_success`）、或近期任务评论里出现了 GitHub PR 链接（`active_pr`）。有两种冷却会把卡片按住却从不计入它：撞配额墙重新排队后的 `rate_limit_cooldown`，以及主机拒绝放置 worker 之后的 `infrastructure_cooldown`（没有重启安全的 systemd scope——见 [worker 与 systemd cgroup](#systemd-cgroups)）；两者共用 `HERMES_KANBAN_RATE_LIMIT_COOLDOWN_SECONDS` 窗口（默认 300 秒）。这防止在人还没来得及跟进时，同一个 bug 或任务上反复爆发 worker。见[事件参考](#event-reference)中的 `respawn_guarded` 行。

想看一张就绪卡为什么没被生成，跑 `hermes kanban dispatch --dry-run` —— 输出会为每张被按住的卡片列出 `Guarded (<reason>): <task id>`（带 `--json` 时还有 `respawn_guarded`、`rate_limited`、`skipped_locked`、`memory_pressure`）。gateway 与独立 daemon 的「dispatcher stuck」警告也会点名上一个 tick 按住了什么，例如 `Last tick held back: active_pr=1`。

`recent_success` 与 `active_pr` 只按住 **ready** 通道——它们是评审交接的输入，不是反对交接的信号。要让评审者、收尾者或其他恢复型 profile 接手一张 PR 已经开着的卡片，要么用 `hermes kanban request-review <id>` 把它移进评审通道（`ready` 与 `running` 都接受；评审通道的生成不受这两条防护约束），要么用 `hermes kanban assign <id> <profile>` 把就绪卡交给该 profile：在 PR 评论*之后*记录的交接——运营者改派、评审者的 changes-requested 裁定、或评审重开——会为卡片上现在点名的那个 profile 解除 `active_pr`，因为那个 PR 正是它要干的活。只有改成*不同* profile 才算数：改派同一个 profile、取消指派、或 dispatcher 自己的 `kanban.default_assignee` 填充都不会解除防护，所以开了 PR 的那个被指派者在崩溃、回收或无变化的改派之后仍不会针对它重新生成；交接之后又发的更新 PR 评论会再次启动防护。成功之后刻意的重新排队（拖 `done→ready`、`unblock`、再次晋级）也会解除 `recent_success`，因此手工重跑绝不会被整个窗口静默按住。

### 拖拽删除与批量删除（dashboard） {#drag-delete}

dashboard 在 kanban 页面上提供一个**回收站投放区**——把任意卡片拖进去即删除该任务（级联删除 `task_events`、子链接与订阅）。有确认提示防手滑。批量删除也可经 `DELETE /api/plugins/kanban/tasks` 触达，请求体为 JSON `{"ids": ["t_abc", "t_def", ...]}`。

### worker 可见性端点 {#worker-visibility}

dashboard 插件 API 现在为外部监控暴露这些只读端点（外加一个运行控制动词）：

| 端点 | 返回 |
|----------|---------|
| `GET /api/plugins/kanban/workers/active` | 当前已生成的 worker，含 PID、profile、任务 id、启动时间、最近心跳 |
| `GET /api/plugins/kanban/runs/{id}` | 单次 run 详情——任务 id、状态、起止时间、退出码、日志路径 |
| `POST /api/plugins/kanban/runs/{run_id}/terminate` | 终止一次可回收的 run——停止 worker 并把任务释放出来重新派发 |
| `GET /api/plugins/kanban/inspect` | 合并的 dispatcher 快照——积压、进行中数量对 `max_in_progress`、近期事件 |

以上全部受与 kanban 插件 API 其余部分相同的 dashboard 插件鉴权保护。

### Kanban Swarm 拓扑助手 {#swarm-helper}

`hermes kanban swarm` 一次性创建一张持久的 **Kanban Swarm v1** 图：一张完成即收尾的根/黑板卡、N 张并行 worker 卡、一张门控于全部 worker 的验证者卡，以及一张门控于验证者的综合者卡。共享的 swarm 上下文（那块「黑板」）以结构化 JSON 评论的形式存在根卡上，任何 worker 都能读到。

```bash
hermes kanban swarm "Design a multi-region failover plan" \
  --workers researcher,architect,sre \
  --verifier reviewer --synthesizer writer
```

产出的图是原子提交的：dispatcher 与 dashboard 读者要么看不到新的 swarm，要么看到完整拓扑，绝不会看到只链了一半的根/worker/验证者图。之后按正常方式派发——worker 并行运行，它们全部完成后验证者被唤醒，验证者判定工作干净后综合者被唤醒。

## `/kanban` 斜杠命令 {#kanban-slash-command}

每个 `hermes kanban <action>` 动词也都能以 `/kanban <action>` 触达——既可以从交互式 `hermes chat` 会话内部，**也可以**从任一 gateway 平台（Telegram、Discord、Slack、WhatsApp、Signal、Matrix、Mattermost、email、SMS）。两个界面调用的都是同一个 `hermes_cli.kanban.run_slash()` 入口，它复用 `hermes kanban` 的 argparse 树，因此参数接口、旗标与输出格式在 CLI、`/kanban` 与 `hermes kanban` 之间完全一致。你不必离开聊天就能驱动看板。

```
/kanban list
/kanban show t_abcd
/kanban create "write launch post" --assignee writer --parent t_research
/kanban comment t_abcd "looks good, ship it"
/kanban unblock t_abcd
/kanban dispatch --max 3
/kanban specify t_abcd                  # flesh out a triage one-liner into a real spec
/kanban specify --all --tenant engineering  # sweep every triage task in one tenant
```

多词参数的引号写法与 shell 里一样——`run_slash` 用 `shlex.split` 解析行的其余部分，所以 `"..."` 与 `'...'` 都可以。

### 运行中使用：`/kanban` 绕过「agent 正在运行」的守卫 {#slash-mid-run}

gateway 通常会在 agent 还在思考时把斜杠命令与用户消息排队——正是这层保护防止你在第一轮还在进行时不小心开启第二轮。**`/kanban` 被显式豁免于该守卫。** 看板活在 `~/.hermes/kanban.db` 里，不在运行中 agent 的状态里，所以读操作（`list`、`show`、`context`、`tail`、`watch`、`stats`、`runs`）与写操作（`comment`、`unblock`、`block`、`assign`、`archive`、`create`、`link` …）都会立刻执行，哪怕正在轮次中间。

这正是这种分离的全部意义：

- worker 阻塞着等同伴 → 你在手机上发 `/kanban unblock t_abcd`，dispatcher 在下一个 tick 捡起那个同伴。被阻塞的 worker 不会被打断——它只是不再被阻塞而已。
- 你发现某张卡需要人的上下文 → `/kanban comment t_xyz "use the 2026 schema, not 2025"` 落到任务串上，该任务*下一次* run 会在 `kanban_show()` 里读到它。
- 你想知道机队在干什么、又不想打断编排者 → `/kanban list --mine` 或 `/kanban stats` 检查看板，完全不碰你的主对话。

### `/kanban create` 时自动订阅（仅 gateway） {#slash-auto-subscribe}

当你在 gateway 上用 `/kanban create "…"` 创建任务时，发起它的那个聊天（平台 + 聊天 id + 话题 id）会自动订阅该任务的终态事件（`completed`、`blocked`、`gave_up`、`crashed`、`timed_out`）。每个终态事件你会收到一条消息——`completed` 时还包括 worker 结果摘要的第一行——无需轮询，也无需记住任务 id。

```
you> /kanban create "transcribe today's podcast" --assignee transcriber
bot> Created t_9fc1a3  (ready, assignee=transcriber)
     (subscribed — you'll be notified when t_9fc1a3 completes or blocks)

… ~8 minutes later …

bot> ✓ t_9fc1a3 completed by transcriber
     transcribed 42 minutes, saved to podcast/2026-05-04.md
```

订阅在任务到达 `done` 之后仍然存活——完成是可逆的（评审者或控制者可以重开一个已完成的任务），因此发起会话在重开周期中会持续收到通知。到 `archived`（不可逆的终态）时自动移除。在从不归档的看板上，GC 清扫会清理那些已 `done` 或 `blocked`、且 `kanban.done_sub_retention_days` 天（默认 30；设 0 关闭）没有新活动的任务的订阅，于是陈旧行不会无限累积。如果你用 `--json`（机器输出）脚本化创建，自动订阅会被跳过——假设是脚本调用方想通过 `/kanban notify-subscribe` 显式管理订阅。

经由 `kanban_create` 或 `hermes kanban create` 创建任务的 dispatcher worker，即使没有 `parents` 依赖链接，也会复制其所属任务的持久通知订阅。目的地、路由锚点与投递模式都会保留；被动订阅不会因为自动订阅被升级成唤醒。是否把当前对话作为新目的地由 `auto_subscribe_on_create` 控制，复制既有订阅与它无关。对于裸 CLI 会话，或所属任务没有任何订阅的 worker，不会凭空发明目的地。

对 `kanban_create` 而言，会话血缘按此顺序解析：显式的 `session_id`、所属 worker 任务的持久会话、请求作用域的 API 来源、然后是当前会话。只有当某个候选 id 在激活 profile 的 `state.db` `sessions` 表里有对应行时才会被盖上；在任何地方都解析不到的 id（行从未写入的会话，或从别的进程继承来的 id）会让 `session_id` 保持 NULL，而不是指向一个任何数据库都解析不出来的会话。内置拆解同样继承其根任务的持久会话。会话血缘本身不是通知目的地：改 `session_id` 不会替换既有订阅；要改事件投递到哪里，请用 `notify-subscribe` 与 `notify-unsubscribe`。

聊天发起的自动订阅以 `notify+wake` 模式创建：遇到终态事件时，目的地 agent 既会收到被动消息，**也会**真正跑一轮，于是它能读到看板上下文并用自己的口吻回复。见下文的[投递模式](#delivery-modes)。

### 消息平台中的输出截断 {#output-truncation}

gateway 平台对消息长度有实际限制。如果 `/kanban list`、`/kanban show` 或 `/kanban tail` 的输出超过约 3800 字符，响应会被截断并加上 `… (truncated; use \`hermes kanban …\` in your terminal for full output)` 页脚。CLI 界面没有这种上限。

### 自动补全 {#autocomplete}

在交互式 CLI 中，输入 `/kanban ` 后按 Tab 会在内置子命令列表中循环（`list`、`ls`、`show`、`create`、`assign`、`link`、`unlink`、`claim`、`comment`、`complete`、`block`、`unblock`、`archive`、`tail`、`dispatch`、`context`、`init`、`gc`）。上面 CLI 参考中列出的其余动词（`watch`、`stats`、`runs`、`log`、`assignees`、`heartbeat`、`notify-subscribe`、`notify-list`、`notify-unsubscribe`、`daemon`）同样可用——只是还没进自动补全的提示列表。

## 协作模式 {#collaboration-patterns}

看板支持以下八种模式，无需任何新原语：

| 模式 | 形态 | 例子 |
|---|---|---|
| **P1 扇出** | N 个同级，同一角色 | 「并行研究 5 个角度」 |
| **P2 流水线** | 角色链：侦察 → 编辑 → 写作 | 每日简报组装 |
| **P3 投票 / 法定人数** | N 个同级 + 1 个汇总者 | 3 名研究者 → 1 名评审者挑 |
| **P4 长期日志** | 同一 profile + 共享目录 + cron | Obsidian 库 |
| **P5 人在环路** | worker 阻塞 → 用户评论 → 解除阻塞 | 模糊的决策 |
| **P6 `@mention`** | 正文中的内联路由 | `@reviewer look at this` |
| **P7 话题作用域工作区** | 在话题里 `/kanban here` | 按项目的 gateway 话题 |
| **P8 机队式铺量** | 一个 profile，N 个对象 | 50 个社交账号 |
| **P9 Triage specifier** | 粗略想法 → `triage` → `hermes kanban specify` 充实正文 → `todo` | 「把这行话变成一个有 spec 的任务」 |

## 把上下文交给后续卡片（parent 链接） {#parent-link}

parent 链接不只是调度闸门——它是从**已完成**卡片把上下文交接给新卡片的通道。当你用 `--parent <done-card-id>` 创建一张卡时，会发生两件事：

1. **它立刻就有资格运行。** `create_task` 按父任务状态设状态：父任务全部为 `done` 的子任务直接以 `ready` 创建——不用等，也不用手工晋级。（父任务仍未完成的子任务停在 `todo`，直到最后一个父任务完成时 `recompute_ready` 晋级它们。）
2. **父任务的交接随行。** 为该子任务组装的 worker 上下文（`build_worker_context`，即 `kanban_show()` 的返回）里有一个 `## Parent task results` 区域，逐字包含每个父任务的完成 `summary` 与 `metadata`：

```
## Parent task results
### t_77c26979 (completed just now)
Added exponential backoff with jitter to the retry helper.
_metadata_: `{"changed_files": ["hermes_cli/retry.py", "tests/test_retry.py"], "decisions": ["capped backoff at 60s", "jitter = full"]}`
```

这就是为什么对已完成卡片的后续工作，正确形态是**一张新的子卡，而不是重开那张 done 卡**。已完成的卡片是不可变的历史——它们的上下文经由 parent 链接向前流动。同一张卡上的返工（失败卡上的重试循环）是另一种机制：*同一*张卡上的历次尝试会以「历次尝试」的形式出现在该卡自己的上下文里。

只有 worktree 或分支是不够的：仓库状态告诉后续 worker 代码*长什么样*，但没说*为什么*——那些决策、跑过的测试、动过的文件都在父任务的结构化交接里，不在 git 里。父任务完成时还不存在的证据（比如两小时后才失败的 CI 日志）应当放进新卡的**正文**。

```bash
# Implementation card t_impl is done. CI fails two hours later.
hermes kanban create "Fix CI failure from t_impl: test_retry flakes on 3.11" \
    --assignee coder \
    --parent t_impl \
    --body "$(cat <<'EOF'
CI run #4812 failed after t_impl merged.
Log excerpt: FAILED tests/test_retry.py::test_backoff_jitter - TimeoutError
Acceptance: tests/test_retry.py green on 3.11 and 3.12 in CI.
Use a fresh worktree/branch; do not force-push the original branch.
EOF
)"
```

修复用的 worker 生成时，原卡片的 summary 与 metadata（改了哪些文件、做了哪些决定）已经在上下文里，再加上你写进正文的新证据。

### 调和冲突的 worker 分支 {#branch-collision}

在工程流水线（带 worktree 的 P1/P2）里，两个 worker 的分支在合并时可能冲突。别让任何一方自己裁决——发生冲突的 agent 缺少对方的上下文，不是可靠地覆盖另一边，就是丢掉自己这边。正确做法是创建一张调和卡，指派给**第三个中立的 profile**，并把**两张**冲突卡都链为 parent：parent 链接会把双方的完成摘要带进调和者的上下文，于是它同时拿到两份 diff *与* 两个意图。随附的 [`agent-merge-conflict-arbiter` 可选 skill](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/autonomous-ai-agents/agent-merge-conflict-arbiter/SKILL.md) 会给该 worker 完整流程：给每个冲突块分类、公正地解决、验证，然后交回一份点名每项决定的摘要。

### 并行战役中的冲突热点 {#collision-hotspots}

在大规模战役里，有些文件会变成冲突磁铁：许多 worker 各往同一个文件里加一点，没人负责把它保持精简，它就成了持续合并冲突的现场。缓解手段是一条评论约定，而不是新原语。当某个 worker 发现自己的 diff 在某个文件上反复与同伴冲突——或它动过的文件反复出现在其他卡片的近期评论里——它不该默默往上堆。相反，它在自己卡片上留一条带可识别前缀的评论：

```
hotspot: hermes_cli/kanban_db.py — third conflicting edit to the dispatch loop this wave
```

并在完成 `metadata` 里重复该标记。编排者（或检查看板的人）看到**两条以上点名同一路径的 `hotspot:` 评论**时，应当为该文件创建一张专门的重构/拆解卡，*然后再*排队更多要动它的工作——拆开磁铁文件，比调和它日后造成的每一场冲突都便宜。对于*已经*发生的冲突，用上面的调和卡模式并配合 `agent-merge-conflict-arbiter` 可选 skill；热点标记是上游修复，能让调和者不至于变成一条常设通道。

## 多租户用法 {#multi-tenant}

当一支专家机队服务多家企业时，给每个任务打上租户标签：

```bash
hermes kanban create "monthly report" \
    --assignee researcher \
    --tenant business-a \
    --workspace dir:~/tenants/business-a/data/
```

worker 收到 `$HERMES_TENANT`，并按前缀给自己的记忆写入加命名空间。看板、dispatcher 与 profile 定义全部共享；只有数据是分域的。

## 桌面通知 {#desktop-notifications}

Desktop 应用的 Kanban 插件原生呈现同样的终态事件——不需要 gateway 平台。Kanban 看板的实时事件 socket 连接期间，每个 `completed`、`blocked`、`gave_up`、`crashed`、`timed_out`，或路由到 triage（`block_loop_detected`）的事件都会弹出应用内 toast，带上 worker 的交接内容（摘要、阻塞原因或错误）以及一个「Open Kanban」动作。当你不在 Hermes 窗口时，同一事件还会触发操作系统原生通知（由 **Settings ▸ Notifications ▸ Plugin notifications** 把关），所以你在别的应用里时任务撞上阻塞也能通知到你。

覆盖窗口：桌面通知跟随实时事件流，因此只在应用运行且 Kanban 插件启用时才会触发。应用关闭期间落下的事件不会在下次启动时作为通知重放——要让投递在应用关闭后仍生效，请用下面的 gateway 订阅。

## Gateway 通知 {#gateway-notifications}

当你在 gateway（Telegram、Discord、Slack 等）上执行 `/kanban create …` 时，发起它的聊天会自动订阅新任务。gateway 的后台通知器每隔几秒轮询一次 `task_events`，每个终态事件（`completed`、`blocked`、`gave_up`、`crashed`、`timed_out`）向该聊天投递一条消息。已完成的任务还会发送 worker `--result` 的第一行，这样你不用 `/kanban show` 就能看到结果。

你可以在 CLI 上显式管理订阅——当脚本 / cron 想通知一个并非由它发起的聊天时很有用：

```bash
hermes kanban notify-subscribe t_abcd \
    --platform telegram --chat-id 12345678 --thread-id 7 \
    --chat-type group --delivery-mode notify+wake
hermes kanban notify-list
hermes kanban notify-unsubscribe t_abcd \
    --platform telegram --chat-id 12345678 --thread-id 7
```

任务到达 `done` 或 `archived` 时订阅会自动移除；无需清理。

**`profile_routes` 下的 Discord 话题：** 当 gateway 复用多个 profile、把某个*频道*路由给某个 profile 时，从 CLI 为该频道里某个*话题*创建的订阅需要该话题的路由锚点，否则通知器无法把它匹配到任何路由、直接跳过（记一次 WARNING）。请显式传入——`--parent-chat-id <频道 id>`，Discord 还要 `--guild-id <guild id>`：

```bash
hermes kanban notify-subscribe t_abcd \
    --platform discord --chat-id <thread id> --thread-id <thread id> --chat-type thread \
    --parent-chat-id <channel id> --guild-id <guild id> --delivery-mode notify+wake
```

从聊天内部创建的订阅（`/kanban create`、`kanban_create`）会自动记录这些锚点。

### 投递模式 {#delivery-modes}

`--delivery-mode` 控制通知器**如何**响应终态事件。每个订阅属于三种模式之一（`notify` 是默认，也是最初的行为）：

| 模式 | 被动消息 | 唤醒 agent | 适用场景 |
|------|-----------------|-----------------|-------------|
| `notify` | 是 | 否 | 你只想要聊天里一条提醒消息（默认）。 |
| `notify+wake` | 是 | 是 | 你还想让目的地 agent 真正跑一轮——读看板上下文、用自己的口吻回复。聊天发起的自动订阅用的就是这个。 |
| `wake` | 否 | 是 | 你只希望 agent 对事件采取行动，不要单独的 ping。 |

对 `notify+wake` 而言，只有当唤醒也被接纳进适配器的轮次队列、且被动 ping 已发出时，投递才算完成。缺失的 handler、被拒的路由与满的队列会在后续通知器 tick 上重试，且订阅不会过期。已发出的 ping 在 SQLite 中单独做检查点，因此被拒绝的唤醒不会重复一个已做检查点的 ping。`notify` 保持被动，从不开启轮次。被接纳不等于模型一定执行或回复成功；常规轮次闸门照旧适用。这不是精确一次投递：发送与检查点之间进程崩溃会重复 ping，而且现有的「投递前认领」游标不是可从崩溃恢复的队列。

「wake」会伪造一条发往目的地 gateway agent 的入站消息，让它跑一个正常轮次（读评论 + 结果、推理、回复），而不是只收到一行被动通知。它只在通知器跑在活的 gateway 进程内时才触发；否则 `notify+wake` 订阅仍会投递被动消息，而只带 `wake` 的订阅在该进程里什么都不做。

**哪些事件会唤醒。** 返回任务结果、或需要编排者注意的那些：`completed`、`blocked`、`gave_up`、`crashed`、`timed_out`、`review_requested`（worker 完成实现并经 `kanban_request_review` 交接）以及 `block_loop_detected`（任务在反复阻塞后被路由到 `triage`）。`status`、`archived` 与 `unblocked` 会投递但绝不唤醒——它们是记账式转移，不是注意信号。当 `completed` 或 `review_requested` 事件带摘要时，该交接随唤醒轮次一起送达，于是被唤醒的 agent 能看到 worker 实际做了什么。

`--chat-type`（`dm` | `group` | `channel` | `thread`）记录发起聊天的类型，好让被唤醒的轮次解析出操作者的**真实**会话：`build_session_key` 对群组、频道、话题的键法与私聊不同，不准确的 `chat_type` 会把唤醒路由进另一个没有上下文的独立会话。`/kanban` 的自动订阅与斜杠命令路径会自动捕获这一点——只有从脚本或 cron 订阅聊天时才需要手填。省略它则不改动既有订阅（新订阅默认 `dm`）。

### 多 profile 环境：投递归 profile 所有 {#multi-profile-delivery}

在每个 profile 一个 gateway 的部署里（一个 dispatcher，`writer`、`admin` 等各有独立 gateway 进程——见[多 gateway 指南](./kanban-multi-gateway.md)），派发与投递各有其主：

- **派发保持单一所有者。** 恰好一个 gateway 保持 `kanban.dispatch_in_gateway: true` 并运行 dispatcher；其他所有 gateway 都设为 `false`。
- **通知投递归 profile 所有。** 每个 gateway——包括非派发的——都会运行通知器，只轮询那些标注了「其平台适配器由本 gateway 承载」的 profile 的订阅。从 `writer` profile 的 Telegram 创建的任务，其 `completed`/`blocked` 消息由 `writer` gateway 投递，尽管派发是 `default` gateway 做的。
- **被 `gateway.profile_routes` 钉住的复用 profile** 可以使用主适配器，条件是订阅持久化的平台、聊天、话题、作用域与父频道锚点经 `gateway.profile_routes` 精确解析到该被服务的 profile，且该 profile 自己不持有该平台的适配器。该平台已连接的次级适配器仍然优先；该 profile 在*其他*平台上运行的适配器不会阻塞投递（共享 bot 是服务被钉住聊天的唯一凭据，入站轮次与通知都走它）。未匹配、被改派、已禁用或含糊的路由保持未投递、可重试。缺少必需路由锚点的旧记录不会被猜着塞给某个 profile。唤醒轮次保持目的地 profile 的运行时作用域与授权传输。
- **无状态（`api_server`）订阅**携带裸 session id，任何 `profile_routes` 条目都无法为其锚定（session 上没有 chat/thread/guild 判别符）。当订阅的 session 活在该 profile 自己的 `state.db` 里时，才恰好授权给被服务的 profile——共享监听器镜像 `/p/<profile>/`，因此 session 存储就是所有权证明，绝不是平台。随后唤醒在该 profile 的运行时作用域内运行、并在进程内恢复那个确切会话，所以不涉及第二个监听器或次级 `API_SERVER_KEY`。未知的、标注给另一个 profile 的、或属于未被服务 profile 的 session 保持未投递、可重试，而 default profile 自己的 `api_server` 订阅不受影响。
- **遗留订阅**（创建于 profile 标注之前，行上没有 `notifier_profile`）只由持有真正 dispatcher 单例锁的那个 gateway 投递，因此两个 gateway 绝不会争抢它们。

跨 gateway 的重复投递由看板 DB 中按事件的原子认领防止。不需要任何中继、凭据共享或额外 dispatcher——每个 profile gateway 只是通过自己的适配器投递。

## Run——每次尝试一行 {#runs}

规范 worker 经由被指派 profile 的 gateway 所有者执行。本地传输会带上 dispatcher 那个确切的看板数据库路径，包括自定义路径与指派给另一个 profile 的共享看板；它不会创建独立的记录写入器。该所有者校验 task/run/claim 并冻结其策略。

如果所有者或受管 worker 在带一个**未知**准入的情况下消失，而所有者为该次尝试绑定的解释器（它的 `worker_bound` 事件）可能还在运行，卡片会保留它的 run 与 claim：过期的 claim、陈旧的心跳与运行时上限都不会重新执行那次有歧义的尝试，所有者账本不可用同样会暂停回收。一旦那个被绑定的解释器本身也死了，就不可能还有东西在跑这次尝试，于是崩溃清扫会像对待任何死 worker 一样回收它：run 以 crashed 关闭，卡片在常规崩溃预算下回到 `ready`（或 `review`），而该预算可能重新执行丢失尝试已经产生过的副作用。从未绑定解释器的 run，在其所有者敲定准入后也以同样方式释放（丢失的卡片尝试其准入会敲定为 `interrupted`）：当为该 run 记录的所有 worker pid 都已死亡，或在一条都没记录的情况下其 claim 已过期时，run 以 crashed 关闭（若其 claim 已失效则算作已回收），卡片在同一崩溃预算下回到 `ready`。显式解决未知准入（用 `prompt.resolve_unknown` 传入其准入 id 与执行代次）也会以同样方式敲定，因此它可能导致又一次尝试。为避免那样，请先检查副作用并完成或阻塞卡片；只有确实想要新尝试时才解除阻塞一张被阻塞的卡片。已确认的超时与 provider 限流结果保持其常规的重试/失败记账行为。

任务是逻辑工作单元；**run** 是执行它的一次尝试。dispatcher 认领一个就绪任务时，会在 `task_runs` 里建一行，并把 `tasks.current_run_id` 指向它。当那次尝试结束——完成、阻塞、崩溃、超时、生成失败、被回收——run 行以一个 `outcome` 关闭，任务的指针清空。一个尝试过三次的任务有三行 `task_runs`。

为什么要两张表而不是直接改任务：真实的事后复盘需要**完整的尝试历史**（「第二次评审尝试到了批准，第三次合并了」），而且你需要一个干净的地方挂按次尝试的元数据——改了哪些文件、跑了哪些测试、评审者记了哪些发现。那些是 run 的事实，不是任务的事实。

**结构化交接**也住在 run 上。worker 完成任务时（经 `kanban_complete(...)`）可以传：

- `summary`（工具参数）/ `--summary`（CLI）—— 人可读交接；落在 run 上；下游子任务在自己的 `build_worker_context` 里看到它。
- `metadata`（工具参数）/ `--metadata`（CLI）—— run 上的自由格式 JSON 字典；子任务会看到它与摘要一起被序列化的形式。
- `result`（工具参数）/ `--result`（CLI）—— 落在任务行上的短日志行（遗留字段，为兼容保留）。

下游子任务为每个父任务读取最近一次已完成 run 的 summary + metadata。重试中的 worker 读取自己任务上的历次尝试（outcome、summary、error），免得重复一条已经失败过的路径。

```
# What a worker actually does — a tool call, from inside the agent loop:
kanban_complete(
    summary="implemented token bucket, keys on user_id with IP fallback, all tests pass",
    metadata={"changed_files": ["limiter.py", "tests/test_limiter.py"], "tests_run": 14},
    result="rate limiter shipped",
)
```

当你（人类）需要收尾一个 worker 收不了的任务时——例如被放弃的任务，或你在 dashboard 上手工标为完成的任务——同一套交接也可经 CLI 触达：

```bash
hermes kanban complete t_abcd \
    --result "rate limiter shipped" \
    --summary "implemented token bucket, keys on user_id with IP fallback, all tests pass" \
    --metadata '{"changed_files": ["limiter.py", "tests/test_limiter.py"], "tests_run": 14}'

# Review the attempt history on a retried task:
hermes kanban runs t_abcd
#   #  OUTCOME       PROFILE           ELAPSED  STARTED
#   1  blocked       worker               12s  2026-04-27 14:02
#        → BLOCKED: need decision on rate-limit key
#   2  completed     worker                8m   2026-04-27 15:18
#        → implemented token bucket, keys on user_id with IP fallback
```

Run 在 dashboard（抽屉里的 Run History 区域，每次尝试一行彩色行）与 REST API（`GET /api/plugins/kanban/tasks/:id` 返回 `runs[]` 数组）上都可见。带 `{status: "done", summary, metadata}` 的 `PATCH /api/plugins/kanban/tasks/:id` 会把两者都转给内核，因此 dashboard 的「mark done」按钮与 CLI 等价。`task_events` 行带着所属的 `run_id`，UI 据此按尝试分组；`completed` 事件在其负载里嵌入首行摘要（上限 400 字符），这样 gateway 通知器无需再来一次 SQL 往返就能渲染结构化交接。

**批量收尾的注意点。** `hermes kanban complete a b c --summary X` 会被拒绝——结构化交接是按 run 的，把同一个 summary 复制粘贴给 N 个任务几乎总是错的。*不带* `--summary` / `--metadata` 的批量收尾对「我干完了一堆行政任务」这类常见情形仍然可用。

**完成时的依赖拒绝会点名父任务。** 当某张卡的直接父任务不是 `done`/`archived`（父任务在 run 中途被重开，或一条早于「运行中子任务拒绝」的边）时，`kanban_complete` / `hermes kanban complete` / dashboard 的「mark done」与「request review」动作（单个与批量）会报告 `unsatisfied parent dependencies: t_… (todo)`，而不是泛化的「unknown id, stale run, or already terminal」文案；卡片保持进行中。`kanban_show` 会在 `unsatisfied_parents` 下列出同样的父任务，`hermes kanban show` / `hermes kanban diagnostics` / dashboard 会在处于该状态的运行中卡片上抛出 `running_with_open_parents` 警告。请完成父任务，或 `hermes kanban unlink <parent> <child>`；依赖闸门没有强制通过的路径。

**完成时的活跃认领守卫。** 一个 `running` 任务，其 worker 持有活跃认领时，只有该 worker（run 内部的 `kanban_complete`）或显式的运营者覆盖才能完成它：`hermes kanban complete <id> --force` 与 dashboard 的「mark done」动作。没有认领的 `hermes kanban complete <id>`，或编排者会话的 `kanban_complete`，会被拒绝并提示 `--force` / `hermes kanban reclaim`，这样第二个会话再也不能在活跃 worker 底下悄悄关掉它的 run。对 `ready`、`blocked` 或 `review` 卡片的无认领完成不受影响。

**状态变更带来的回收 run。** 如果你在 dashboard 上把一个运行中任务拖离 `running`（拖回 `ready`，或直接到 `todo`），或归档一个仍在运行的任务，进行中的 run 会以 `outcome='reclaimed'` 关闭，而不是变成孤儿。当 `tasks.current_run_id` 为 `NULL` 时 `task_runs` 行必然处于终态，反之亦然——这条不变式在 CLI、dashboard、dispatcher 与通知器之间都成立。

**从未认领的完成的合成 run。** 完成或阻塞一个从未被认领的任务（例如人从 dashboard 带 summary 关闭一个 `ready` 任务，或 CLI 用户跑 `hermes kanban complete <ready-task> --summary X`）否则会丢掉交接。内核改为插入一行零时长 run（`started_at == ended_at`）承载 summary / metadata / reason，使尝试历史保持完整。`completed` / `blocked` 事件的 `run_id` 指向该行。

**抽屉实时刷新。** 当 dashboard 的 WebSocket 事件流为用户正在查看的任务报告新事件时，抽屉会自行重新加载（靠一个按任务的事件计数器串进 `useEffect` 依赖列表）。要看 run 的新行或更新后的结果，不再需要关掉再打开。

### 向前兼容 {#forward-compat}

`tasks` 上两个可空列是为 v2 工作流路由预留的：`workflow_template_id`（该任务属于哪个模板）与 `current_step_key`（该模板中哪一步处于激活）。v1 内核在路由时忽略它们，但允许客户端写入，于是 v2 版本可以在不再做一次 schema 迁移的前提下加入路由机制。

## 事件参考 {#event-reference}

每次转移都向 `task_events` 追加一行。每行带一个可选 `run_id`，UI 据此按尝试分组。kind 分成三簇，便于过滤（`hermes kanban watch --kinds completed,gave_up,timed_out`）：

**生命周期**（作为逻辑单元的任务发生了什么变化）：

| Kind | 负载 | 时机 |
|---|---|---|
| `created` | `{assignee, status, parents, tenant}` | 任务插入。`run_id` 为 `NULL`。 |
| `promoted` | — | 所有父任务都到 `done`，`todo → ready`。`run_id` 为 `NULL`。 |
| `claimed` | `{lock, expires, run_id}` | dispatcher 原子认领了一个 `ready` 任务用于生成。 |
| `completed` | `{result_len, summary?}` | worker 写了 `--result` / `--summary` 且任务到达 `done`。`summary` 是首行交接（400 字符上限）；完整版在 run 行上。若对从未认领的任务带交接字段调用 `complete_task`，会合成一行零时长 run，使 `run_id` 仍有指向。 |
| `blocked` | `{reason, kind, recurrences}` | worker 或人把任务翻成 `blocked`。`kind` 是带类型的阻塞原因（`needs_input`、`capability`、`transient`，泛化阻塞为 `null`）；`recurrences` 是解除阻塞循环计数器。没有未完成父任务的 `kind=dependency` 阻塞会落到这里并记为 `needs_input`（负载补上 `requested_kind: dependency`、`rekind_reason: no_open_parent`），因为 `todo` 只会让它在下一个派发 tick 被重新晋级和重新生成。对从未认领的任务带 `--reason` 调用时合成一行零时长 run。 |
| `dependency_wait` | `{reason, kind}` 或 `{reason: parent_not_done, demoted: true, parent}` | 至少一个父任务仍未完成时 worker 以 `kind=dependency` 阻塞——任务只是在等另一个任务，因此它路由到 `todo`（受父任务门控、自动晋级）而不是 `blocked`，也不计复发次数。不需要人。当 `link`/`kanban_link` 把一个 `ready` 子卡挂到一个非 `done` 的父任务下时也会发出：子卡掉回 `todo`，该事件记录原因（`ready → running` 认领会重新检查父任务，因此在父任务完成或用 `hermes kanban unlink` 删掉链接之前，没人能运行它）。 |
| `block_loop_detected` | `{reason, kind, recurrences, limit}` | 任务因同一原因被解除阻塞又再次阻塞，累计 `BLOCK_RECURRENCE_LIMIT` 次（默认 2）。它不再落进 `blocked`（在那里 cron 会不停解除阻塞），而是路由到 `triage` 交编排者处理，打断解除阻塞↔再阻塞的循环。 |
| `unblocked` | — | `blocked → ready`（父任务仍未完成则为 `todo`），手工或经 `/unblock`。重置 dispatcher 的 `consecutive_failures`，但刻意保留 `block_recurrences`，让断路器仍有记忆。`run_id` 为 `NULL`。 |
| `archived` | — | 从默认看板隐藏。若任务仍在运行，则带着作为副作用被回收的那次 run 的 `run_id`。 |

**编辑**（人驱动的、非转移的变更）：

| Kind | 负载 | 时机 |
|---|---|---|
| `assigned` | `{assignee}` | 负责人变更（含取消指派）。 |
| `edited` | `{fields}` | 标题或正文更新。 |
| `reprioritized` | `{priority}` | 优先级变更。 |
| `status` | `{status}` | dashboard 拖放直接写入了状态（例如 `todo → ready`）。从 `running` 拖走时带着被回收 run 的 `run_id`；否则 `run_id` 为 NULL。 |

**Worker 遥测**（关于执行进程，而非逻辑任务）：

| Kind | 负载 | 时机 |
|---|---|---|
| `spawned` | `{pid}` | dispatcher 成功启动了 worker 进程。 |
| `worker_registered` | `{pid, started_at}` | dispatcher 启动 worker 之后、记录其 pid 之前挂掉了，于是 worker 在首次模型调用前自己记下 pid。随后活性检查看得到它，过期的 claim 会被延长而不是再生成第二个 worker。其 run 在走到这一步之前就被回收的 worker，会在不动卡片的情况下退出。 |
| `heartbeat` | `{note?}` | worker 在长操作中调用 `hermes kanban heartbeat $TASK` 报活。 |
| `reclaimed` | `{stale_lock}` | claim TTL 到期且未完成；任务回到 `ready`。自动回收算作朝 `gave_up` 断路器的一次非成功尝试（一个从未生成 worker 的 claim 否则会永远循环 认领 → 回收 → 认领）；运营者的 `reclaim` 则重置该计数器。 |
| `crashed` | `{pid, claimer, exit_kind?, exit_code?, worker_output?}` | worker PID 已不存活但 TTL 尚未到期。`worker_output` 是 worker 自身日志的尾部（其最终响应或渲染出的 provider 错误，去掉外框，≤ 400 字符），也会追加到任务的 `last_failure_error`，于是看板显示的是*原因*而不只是退出码。 |
| `timed_out` | `{pid, elapsed_seconds, limit_seconds, sigkill}` | 超过 `max_runtime_seconds`；dispatcher 发 SIGTERM（5 秒宽限后 SIGKILL）并重新排队。 |
| `stale` | `{elapsed_seconds, last_heartbeat_at, heartbeat_age_seconds, timeout_seconds, pid, terminated}` | 任务运行超过 `kanban.dispatch_stale_timeout_seconds`（默认 4 小时）**且**最近一小时没有收到 `kanban_heartbeat`。dispatcher 对本机 worker（若有）发 SIGTERM，把任务重置为 `ready` 重新派发。**不**给失败计数器加一（stale 是 dispatcher 侧的缺席检测，不是 worker 故障）。跑长操作的 worker 应至少每小时调用一次 `kanban_heartbeat` 以避免它。 |
| `reconciled` | `{reason, claim_lock, claim_expires, worker_pid}` | 孤儿卡对账：卡片为 `running` 但认领记账损坏（`claim_lock` 或 `claim_expires` 为 NULL——认领中途崩溃、手工 SQL、DB 恢复）且没有活跃 worker，于是 TTL/崩溃/陈旧三条路径都无法恢复它。dispatcher 把它重新排队回 `ready` 并附一条解释性评论。由 config.yaml 的 `kanban.reconcile_orphans` 把关（默认 `true`）。 |
| `respawn_guarded` | `{reason}` | dispatcher 本 tick 拒绝重新生成该就绪任务。原因：`infrastructure_cooldown`（主机拒绝了上次生成——没有重启安全的 systemd scope——且冷却未过；从不计入卡片）、`rate_limit_cooldown`（上次 run 撞上配额墙；同一冷却，从不计入）、`blocker_auth`（上次失败是配额/鉴权/429 错误——等限流窗口重置）、`recent_success`（最近一小时有过完成的 run——等评审后再重跑）、`active_pr`（近期评论里出现了 GitHub PR URL——先前的 worker 已经开过 PR）。任务保持 `ready`；下一个 tick 会再有一次生成机会。如果底层条件持续，常规的 `consecutive_failures` 熔断器会在 `failure_limit` 次失败后经 `gave_up` 自动阻塞。 |
| `spawn_failed` | `{error, failures}` | 一次生成尝试失败（PATH 缺失、工作区挂载不上……）。计数器加一；任务回到 `ready` 重试。 |
| `skipped_nonspawnable` | `{assignee}` | dispatcher 拒绝生成，因为被指派 profile 在本 home 中不存在（或不在 `kanban.dispatch_profiles` 里）。每张卡只写一次——只有中间落了其他事件才重复——因此 `show`/`tail` 能点名缺失的 profile，而不会每个 tick 都来一行。卡片保持 `ready`；改派它或安装该 profile。 |
| `protocol_violation` | `{pid, claimer, exit_code, protocol_violation, worker_output?}` | worker 在任务仍为 `running` 时成功退出，通常因为它给出了答案却没有终态看板调用（`kanban_complete`、`kanban_request_review` 或 `kanban_block`）。每次违规都发出（负载中的 `protocol_violation: true` 标记会被复制进 run 元数据，并喂给仅针对违规的重试预算）。在预算之内——最多 `_PROTOCOL_VIOLATION_FAILURE_LIMIT`（默认 3）次*连续*违规，按任务的 `max_retries` 优先——任务 simply 回到 `ready` 再试一次；当连击达到上限时 dispatcher 还会发出 `gave_up` 并自动阻塞。`worker_output` 带着 worker 自己最后打印的文本（通常是它解释为何停下），同样并入 `last_failure_error`，并作为上次尝试的错误展示给重试 worker。 |
| `gave_up` | `{failures, effective_limit, limit_source, error, terminal_provider?}` | 连续 N 次非成功尝试后熔断器触发。任务以最后一次错误自动阻塞。生效上限的解析顺序：任务的 `max_retries`，然后 dispatcher 的 `failure_limit` / `kanban.failure_limit`，再然后内置默认。`terminal_provider: true` 表示 worker 因一个重试解决不了的 provider 错误以 `78` 退出（凭据被吊销、模型消失）——包括明确需要重新登录的启动期凭据失败（`hermes auth` / `setup`），它在第一轮之前就以 `78` 退出；其他启动失败以 `1` 退出——而熔断器在那第一次尝试上就触发，粘性，与上限无关。 |

`hermes kanban tail <id>` 对单个任务显示这些。`hermes kanban watch` 按看板范围流式输出它们。

## 范围之外 {#out-of-scope}

Kanban 刻意做成单主机。`~/.hermes/kanban.db` 是本地 SQLite 文件，dispatcher 在同一台机器上生成 worker。不支持在两台主机之间跑共享看板——没有支撑「主机 A 上的 worker X、主机 B 上的 worker Y」的协作原语，崩溃检测路径也假设 PID 是主机本地的。如果你需要多主机，请每台主机跑一个独立看板，用 `delegate_task` / 消息队列把它们桥接起来。
