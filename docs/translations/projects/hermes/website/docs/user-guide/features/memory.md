---
sidebar_position: 3
title: "持久记忆"
description: "Hermes Agent 如何跨会话记忆 —— MEMORY.md、USER.md 与 session search"
---

# 持久记忆（Persistent Memory）

> 来源：https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/memory.md
> 原文：oss-repos/hermes-agent/website/docs/user-guide/features/memory.md
> 翻译日期：2026-11-03 ｜ 范围：全文 ｜ 方式：机器翻译初稿，未经人工校对
> 引用于：docs/essay-study/hermes-2026.md、docs/brief-plan.md §3

## 目录

- [工作原理](#工作原理)
- [记忆在系统提示中的呈现方式](#记忆在系统提示中的呈现方式)
- [记忆需要会话边界](#记忆需要会话边界)
- [排障：「我让它记住，下一个会话它忘了」](#排障我让它记住下一个会话它忘了)
- [memory 工具的动作](#memory-工具的动作)
  - [子串匹配](#子串匹配)
- [两个 target 详解](#两个-target-详解)
  - [`memory` —— agent 的个人笔记](#memory-target)
  - [`user` —— 用户画像](#user-target)
- [该存什么、该跳过什么](#该存什么该跳过什么)
  - [主动保存这些](#主动保存这些)
  - [跳过这些](#跳过这些)
- [容量管理](#容量管理)
  - [记忆写满时会发生什么](#记忆写满时会发生什么)
  - [好的记忆条目示例](#好的记忆条目示例)
- [去重](#去重)
- [安全扫描](#安全扫描)
- [会话搜索](#会话搜索)
  - [session_search 与 memory 对比](#session_search-与-memory-对比)
- [学习历程（`/journey`）](#学习历程journey)
- [配置](#配置)
  - [外部召回的尺寸](#外部召回的尺寸)
- [控制记忆写入（`write_approval`）](#控制记忆写入write_approval)
- [后台审查通知（`display.memory_notifications`）](#后台审查通知displaymemory_notifications)
- [用更便宜的模型跑审查（`auxiliary.background_review`）](#用更便宜的模型跑审查auxiliarybackground_review)
  - [同模型审查的推理设置](#同模型审查的推理设置)
  - [关闭自动审查（`enabled`）](#关闭自动审查enabled)
  - [限制审查开销（`max_input_tokens`）](#限制审查开销max_input_tokens)
  - [放行一个窄范围的额外审查工具（`extra_tools`）](#放行一个窄范围的额外审查工具extra_tools)
  - [本地模型：审查等待 GPU 空闲（`defer`）](#本地模型审查等待-gpu-空闲defer)
- [控制 skill 写入（`skills.write_approval`）](#控制-skill-写入skillswrite_approval)
- [外部记忆提供方](#外部记忆提供方)

## 工作原理

agent 的记忆由两个文件构成：

| 文件 | 用途 | 字符上限 |
|------|------|----------|
| **MEMORY.md** | agent 的个人笔记 —— 环境事实、惯例、学到的东西 | 2,200 字符（约 800 token） |
| **USER.md** | 用户画像 —— 你的偏好、沟通风格、期望 | 1,375 字符（约 500 token） |

两个文件都存放在 `~/.hermes/memories/`，并在会话开始时以**冻结快照**的形式注入系统提示。agent 通过 `memory` 工具管理自己的记忆 —— 可以增补、修补或删除条目。

:::caution 一个 Hermes home 只放一个 agent
不要让两个 agent 进程指向同一个 Hermes home 目录。记忆写入是自动的，并会在会话开始时加载回系统提示；两个写入者共享一个 home，会把各自的条目互相搅在一起，最终变成谁（包括你）都没有写过的状态。记忆按 [profile](../profiles.md) 隔离，这是设计使然 —— 给第二个 agent 它自己的 profile；如果它们确实需要共享记忆，请改用[外部记忆提供方](./memory-providers.md)。
:::

:::info
字符上限是为了让记忆保持聚焦。记忆**不会**自动压缩：当一次写入会超出上限时，`memory` 工具会返回错误，而不是悄悄丢掉条目。随后 agent 自己腾地方 —— 在同一轮里先合并或删除条目再重试（见[记忆写满时会发生什么](#记忆写满时会发生什么)）。注意 `patch` 同样受上限约束：一次让条目变长的修补仍可能溢出，所以新文本必须缩短（或删掉别的条目）才能放得下。
:::

## 记忆在系统提示中的呈现方式

每个会话开始时，记忆条目会从磁盘加载，并渲染成系统提示里一个冻结的块：

```
══════════════════════════════════════════════
MEMORY (your personal notes) [67% — 1,474/2,200 chars]
══════════════════════════════════════════════
User's project is a Rust web service at ~/code/myapi using Axum + SQLx
§
This machine runs Ubuntu 22.04, has Docker and Podman installed
§
User prefers concise responses, dislikes verbose explanations
```

格式包含：

- 一个标明存储归属的头部（MEMORY 或 USER PROFILE）
- 使用百分比与字符数，让 agent 知道还剩多少容量
- 各条目之间用 `§`（section sign）分隔
- 条目可以有多行

**冻结快照模式：** 系统提示的注入只在会话开始时捕获一次，会话中途永不改变。这是有意为之 —— 可以保住 LLM 的 prefix cache，换来性能。当 agent 在会话中增删记忆条目时，改动会立即持久化到磁盘，但要到下一个会话开始才会出现在系统提示里。工具响应则始终反映实时状态。

## 记忆需要会话边界

整套记忆机制都围绕会话**结束**那一刻构建：`MEMORY.md` 与 `USER.md` 把要点带进下一个会话，而 `session_search` 在旧上下文消失之后补齐缺口。在单个会话内部，这套机器没有理由运转 —— 所有要紧的东西都还在活跃上下文里，所以 agent 很少查询 `session_search`，多半是压缩记忆条目而不是梳理它们。

这一点在消息平台（Telegram、Discord 等）上尤其要紧：那里的聊天被刻意设计成[一个连续的会话](../sessions.md#session-continuity)，能扛过重启、gateway 崩溃与机器重开。夜里关机**不会**结束会话 —— 下一条消息会从原处接着走。如果你从不重置，一个聊天可以以单个会话连续跑上数周：方便，但越来越贵（压缩会在越来越长的历史上反复运行），而且 *遗忘 → 从记忆中唤回 → 搜索过往会话* 这个学习闭环几乎从不被触发。由于上面说的冻结快照，新写入的记忆条目对正在运行的会话也不可见。

**实践：** 在自然边界处运行 `/new` —— 一个任务结束、话题转换、一天开始。每个边界正是记忆回本的时候：agent 重新读取更新后的 `MEMORY.md`/`USER.md` 快照，从一段便宜的短上下文起步，并在真正需要历史时才去用 `session_search`。在 CLI 上这基本不用操心（每次调用就是新会话）；在 gateway 上，边界需要你自己创造。

## 排障：「我让它记住，下一个会话它忘了」

最常见的反馈是这样的：你告诉 agent 某样东西放在哪里（一个 Obsidian vault、一个项目目录、一台服务器），它回答「好的，我记下了」，然后一个全新会话完全不知道你在说什么。按下面的顺序逐条排查 —— 第一条解释了绝大多数情况。

1. **先确认写入是否真的发生了。** 记忆只有在模型*调用 `memory` 工具*时才会持久化；「我已经把那条记进记忆了」这类句子只是文本。打开文件找那条记录：

   ```bash
   cat ~/.hermes/memories/MEMORY.md
   cat ~/.hermes/memories/USER.md
   ```

   如果事实不在里面，就是模型声称保存了却根本没保存。小的本地模型（大约 30B 参数以下）和工具调用能力弱的模型经常这样 —— 它们给出了确认，却没发出工具调用。可以明确要求（「用 `memory` 工具把 vault 路径 `/srv/vault` 存下来」），并确认条目确实落到了文件里。如果反复出现，解法是用更强的模型来做配置，而不是堆更多指令；一旦条目存在，较小的模型读起来没问题，因为它们是随系统提示一起送达的。

2. **确认写入没有被挂起待审。** 开启 `write_approval: true` 后，交互式 CLI 之外的写入会先挂起等待审核，在批准之前永远到不了文件 —— 运行 `/memory pending` 与 `/memory approve all`。见[控制记忆写入](#控制记忆写入write_approval)。

3. **确认你读的和你写的是同一份记忆。** 记忆按 [profile](../profiles.md) 隔离：`hermes -p work`（或 `work chat` / `work gateway start`）读的是 `~/.hermes/profiles/work/memories/`，不是 `~/.hermes/memories/`。默认 profile 下的 CLI 会话和另一个 profile 上的 Telegram bot 不共享笔记。`hermes profile list` 可以看到有哪些。

4. **确认记忆功能是开着的。** `memory.memory_enabled: false`（或在 `agent.disabled_toolsets` 下列出 `memory`）会直接移除这个工具 —— 模型无论说什么都存不进任何东西。见[配置](#配置)。

5. **记住快照在会话开始时就冻结了。** 当前会话里保存的事实，对*下一个*会话可见，而不是对已经在跑的其他会话可见。写入之后请开一个新会话（`/new`，或重新起一次 CLI 调用）。

有两样东西**不会**让 agent 记住事：`.env` 里的变量（那是凭据和设置，不是记忆），以及随口提到、没有要求保存的事实。对于一个周期性任务每次运行都需要的地址，[skill](./skills.md) 往往比记忆条目更合适 —— 它只在相关时加载，也不占用那 2,200 字符的预算。

## memory 工具的动作

agent 使用 `memory` 工具的这些动作：

- **add** —— 新增一条记忆
- **patch** —— 替换已有条目中的一段文本、保留其余部分（`old_text` 是那段文本，`content` 是替换内容）
- **remove** —— 删除一条不再相关的条目（通过 `old_text` 做子串匹配）

没有 `read` 动作 —— 记忆内容会在会话开始时自动注入系统提示。agent 把自己的记忆当作对话上下文的一部分来看待。

每次工具调用都需要一个顶层 `target`：agent 笔记用 `"memory"`，用户画像用 `"user"`。一个批次里的所有操作都共用这一个 target：

```json
{"target": "user", "operations": [{"action": "add", "content": "User prefers metric units"}]}
```

target 缺失或为 null，或者某个操作内部的 target 与顶层不一致，都会在写入或挂起待审之前返回错误。修正负载后重试；要同时更新两个存储，请分两次调用。

### 子串匹配

`patch` 与 `remove` 动作用短的唯一子串做匹配 —— 你不需要给出条目的全文。`old_text` 参数只要是一个能唯一标识某一条目的子串即可：

```python
# If memory contains "User prefers dark mode in all editors"
memory(action="patch", target="memory",
       old_text="dark mode in all editors",
       content="light mode in VS Code, dark mode in terminal")
# -> "User prefers light mode in VS Code, dark mode in terminal"
```

如果子串匹配到多条记录，会返回错误，要求给出更精确的匹配。

`patch` 只替换命中条目中 `old_text` 那一段，其余全部保留。该段在条目中必须只出现一次；如果出现多次，调用会被拒绝，agent 会带上更多上下文重试。要从条目里删掉一段文字，就 patch 一个包含它的更长片段。要重写整条记录，就把整条作为 `old_text` 传入（整条精确匹配优先于子串匹配）。

没有 `replace` 动作。它会整条覆盖命中的记录，而模型把它当查找替换用，结果把多事实条目里的其他事实一并抹掉了。现在 `replace` 调用会返回一个指向 `patch` 的错误；在此改动之前已挂起待审的写入仍按原样生效。

## 两个 target 详解

### `memory` —— agent 的个人笔记 {#memory-target}

存放 agent 需要记住的环境、工作流与经验教训：

- 环境事实（操作系统、工具、项目结构）
- 项目惯例与配置
- 发现的工具怪癖与变通办法
- 已完成任务的日记条目
- 验证有效的 skill 与技巧

### `user` —— 用户画像 {#user-target}

存放关于用户身份、偏好与沟通风格的信息：

- 姓名、角色、时区
- 沟通偏好（简洁还是详细、格式偏好）
- 讨厌的事、需要回避的事
- 工作习惯
- 技术水平

## 该存什么、该跳过什么

### 主动保存这些

agent 会自动保存 —— 你不必开口。它在学到这些东西时保存：

- **用户偏好：**「我更喜欢 TypeScript 而不是 JavaScript」→ 存入 `user`
- **环境事实：**「这台服务器跑 Debian 12，带 PostgreSQL 16」→ 存入 `memory`
- **纠正：**「Docker 命令别用 `sudo`，用户在 docker 组里」→ 存入 `memory`
- **惯例：**「项目用 tab、行宽 120 字符、docstring 用 Google 风格」→ 存入 `memory`
- **完成的工作：**「2026-01-15 把数据库从 MySQL 迁移到 PostgreSQL」→ 存入 `memory`
- **明确要求：**「记住我的 API key 每月轮换一次」→ 存入 `memory`

### 跳过这些

- **琐碎/显而易见的信息：**「用户问了 Python」—— 太笼统，没有用处
- **容易重新查到的事实：**「Python 3.12 支持 f-string 嵌套」—— 网上一搜就有
- **原始数据倾倒：** 大段代码、日志文件、数据表 —— 对记忆来说太大了
- **只属于本次会话的临时物：** 临时文件路径、一次性的调试上下文
- **已在 context 文件里的信息：** SOUL.md 与 AGENTS.md 的内容

## 容量管理

记忆有严格的字符上限，以保证系统提示的规模有界：

| 存储 | 上限 | 典型条目数 |
|------|------|------------|
| memory | 2,200 字符 | 8–15 条 |
| user | 1,375 字符 | 5–10 条 |

### 记忆写满时会发生什么

当你试图加入一条会超限的条目时，工具会返回错误：

```json
{
  "success": false,
  "error": "Memory at 2,100/2,200 chars; adding this entry (250 chars) would exceed the limit by 153 chars. Retry as ONE 'operations' batch that removes or shortens (patch) stale entries from current_entries below to free at least 153 chars AND adds this entry — the limit is checked only on the batch result.",
  "current_entries": ["..."],
  "usage": "2,100/2,200"
}
```

接着 agent 会重新发出**一个** `operations` 批次：先腾出至少指定数量的字符（删除，或用 `patch` 缩短），再加入新条目；上限只针对批次的最终结果检查。`patch`/`remove` 的 `old_text` 匹配不到任何条目时会以同样的方式失败，并在 `closest_entries` 里列出它最接近的那些条目。

**最佳实践：** 当记忆超过 80% 容量（系统提示头部可以看到）时，先合并条目再加入新条目。比如，把三条各自独立的「项目使用 X」条目合并成一条完整的项目描述。

### 好的记忆条目示例

**紧凑、信息密度高的条目效果最好：**

```
# Good: Packs multiple related facts
User runs macOS 14 Sonoma, uses Homebrew, has Docker Desktop and Podman. Shell: zsh with oh-my-zsh. Editor: VS Code with Vim keybindings.

# Good: Specific, actionable convention
Project ~/code/api uses Go 1.22, sqlc for DB queries, chi router. Run tests with 'make test'. CI via GitHub Actions.

# Good: Lesson learned with context
The staging server (10.0.1.50) needs SSH port 2222, not 22. Key is at ~/.ssh/staging_ed25519.

# Bad: Too vague
User has a project.

# Bad: Too verbose
On January 5th, 2026, the user asked me to look at their project which is
located at ~/code/api. I discovered it uses Go version 1.22 and...
```

## 去重

记忆系统会自动拒绝完全重复的条目。如果你试图加入已经存在的内容，它会返回成功，并附一条「未添加重复条目」的提示。

## 安全扫描

记忆条目在被接受之前会接受注入与外泄模式扫描，因为它们会被注入系统提示。命中威胁模式（prompt 注入、凭据外泄、SSH 后门）或含有不可见 Unicode 字符的内容会被拦截。

## 会话搜索

除了 MEMORY.md 与 USER.md，agent 还可以用 `session_search` 工具搜索自己过去的对话：

- 所有 CLI 与消息平台会话都存在 SQLite（`~/.hermes/state.db`）里，带 FTS5 全文检索
- 搜索查询返回数据库里的真实消息 —— 没有 LLM 摘要，也没有截断
- agent 能找到几周前讨论过的东西，即使它们不在活跃记忆里
- agent 还可以在找到的会话内部前后滚动浏览

```bash
hermes sessions list    # Browse past sessions
```

三种调用形态（发现 / 滚动 / 浏览）与响应格式见[会话搜索工具](../sessions.md#session-search-tool)。

### session_search 与 memory 对比

| 特性 | 持久记忆 | 会话搜索 |
|------|----------|----------|
| **容量** | 合计约 1,300 token | 无限（所有会话） |
| **速度** | 即时（就在系统提示里） | FTS5 查询约 20ms，滚动约 1ms |
| **开销** | 每个提示都花 token | 免费 —— 无 LLM 调用 |
| **用例** | 关键事实随时在手 | 找出特定的过往对话 |
| **管理** | 由 agent 手工梳理 | 自动 —— 所有会话都会存 |
| **token 开销** | 每会话固定（约 1,300 token） | 按需（需要时才搜） |

**记忆**用于那些应该始终在上下文里的关键事实。**会话搜索**用于「上周我们讨论过 X 吗？」这类需要 agent 从过往对话中唤回细节的查询。

## 学习历程（`/journey`）

学习历程（learning journey）是 Hermes 所学一切的时间线视图 —— 已保存的 skill 与记忆条目按时间作图（最老的在上、最新的在下），并配一个可播放的「星座」拖动条来回放这个积累过程。同一份图数据驱动三个界面：

- **经典 CLI / 独立运行** —— `hermes journey`（别名：`hermes learning`、`hermes memory-graph`）在终端渲染时间线。标志：`--play` 动画回放积累过程（`--fps` 调节帧率），`--width`/`--height` 覆盖渲染尺寸，`--no-color` 关闭颜色，`--json` 导出原始图数据。
- **TUI** —— `/journey`（别名：`/learning`、`/memory-graph`）以覆盖层形式打开时间线。
- **桌面应用** —— `/journey` 打开星图 / memory-graph 面板，是同一批节点的交互式可视化。

一个 skill 只要有了学习信号就会出现在时间线上：它在本 profile 中被创建（`/learn` 的结果，或前台的 `skill_manage` create）、由后台审查创建，或至少被使用过一次。随附的（bundled）skill 与从未被用过的手写 skill 不会进入时间线。

除了查看，历程也是你**修剪与纠正** Hermes 所学内容的地方：

| 命令 | 作用 |
|------|------|
| `hermes journey list` | 列出节点 id —— skill 名，以及记忆块的 `memory:<source>:<index>:<fingerprint>` id（原样回传其中一个即可）。 |
| `hermes journey delete <node> [-y]` | 删除节点。skill 是**归档**（可恢复），记忆块则被移除。`-y` 跳过确认。 |
| `hermes journey edit <node>` | 在 `$EDITOR` 中打开节点内容（skill 的 `SKILL.md` 或该记忆块）。 |

同一套 `list` / `delete <id>` / `edit <id>` 子命令在 CLI 的聊天内 `/journey` 命令中同样可用，桌面面板则直接在节点上提供编辑 / 删除。

## 配置

```yaml
# In ~/.hermes/config.yaml
memory:
  memory_enabled: true
  user_profile_enabled: true
  memory_char_limit: 2200   # ~800 tokens
  user_char_limit: 1375     # ~500 tokens
  write_approval: false     # false = write freely (default) | true = require approval
  prefetch_spill_enabled: false  # external recall stays intact unless explicitly enabled
```

把 **`memory_enabled` 与 `user_profile_enabled` 同时**设为 `false`，会把内置存储彻底关掉：`memory` 工具从 schema 中移除，它在系统提示中的指引块也随之移除，模型因此永远不会被告知有一个它用不了的工具。通过 `memory.provider` 设置的外部提供方（Hindsight、Mem0、Honcho 等）不受影响，仍保留自己的工具 —— 当你想用第三方记忆后端*替代*内置文件时就用这个。在 `agent.disabled_toolsets` 下列出 `memory` 是更重的开关：它连外部提供方的工具也会一起隐藏。

如果只设 `memory_enabled: false`（用户画像仍开启），工具会保留 —— 它支撑着画像存储 —— 但系统提示会把完整的记忆指引换成更窄的、只讲画像的块。此时工具 schema 只声明 `user` target，对已禁用的 `MEMORY.md` 的直接写入或挂起写入都会被拒绝。反过来的配置则只声明 `memory`，并拒绝 `USER.md` 的写入。

### 外部召回的尺寸

外部记忆提供方默认返回其完整的预取上下文，上限为 `hooks.output_spill.max_chars` 的 10 倍（至少 100,000 字符）；超过该值的召回仍会溢出（spill），这样一个失控的提供方无法撑爆上下文窗口。`memory.prefetch_spill_enabled: true` 让当前 profile 选择把超大召回替换成头尾预览加一个文件路径。这能减少重放的上下文，但按相关性排序的中段就不再对模型直接可见了。提供方自带召回预算时，优先用它。

这个选择性开关复用共享的 `hooks.output_spill` 阈值、预览长度与目录；`hooks.output_spill.enabled: false` 依然会关掉它。普通插件 hooks 默认继续独立于记忆开关而溢出。相关设置在提供方注册时被捕获：改完要重启 Hermes。配置细节见[超大预取结果](../../developer-guide/memory-provider-plugin.md#oversized-prefetch-results)。

## 控制记忆写入（`write_approval`）

默认情况下 agent 可以自由保存记忆 —— 包括每轮之后运行的后台自我改进审查。如果你希望先审批再保存，设 `memory.write_approval: true`。它是一个简单的开关闸门，同时作用于**前台轮次**与**后台审查**：

| `write_approval` | 行为 |
|------------------|------|
| `false`（默认） | 自由写入 —— 闸门关闭（改动前的行为）。 |
| `true` | 任何保存都需要先批准。在交互式 CLI 中，前台写入会就地向你提示（条目都很小，可以完整读完）。其他所有地方 —— 消息平台、脚本、后台自我改进审查 —— 写入都会**挂起**等待审核，用 `/memory pending` 查看。 |

> 要彻底关掉记忆（不只是加闸门），把 `memory_enabled: false` 与 `user_profile_enabled: false` 都设上。两个内置存储都禁用时，内置的 `memory` 工具会自动隐藏。

从 CLI 或任意消息平台审核挂起的写入：

```
/memory pending             # list staged memory writes (auto ones tagged [auto])
/memory approve <id>        # apply one (or 'all')
/memory reject <id>         # drop one (or 'all')
/memory approval on         # turn the gate on (or 'off') and persist it
```

这就是「agent 保存了关于我的错误假设」的答案：设 `write_approval: true`，每一次保存 —— 尤其是那些未经提示的后台保存 —— 都要等你点头或摇头，才会进入你的画像。

挂起的 `patch` 或 `remove`（即使闸门关闭，后台审查也会把这两者挂起）会记录它所针对的完整条目，`/memory pending` 会显示出来。批准只作用于那一条：如果在挂起之后它已经变了，写入会被拒绝并继续挂着等你驳回。在这套「钉住目标」机制存在之前挂起的 `replace`/`patch`/`remove` 没有可校验的目标，同样会被拒绝：驳回它，然后重新做这次修改。`/memory approve` 会列出每一条被它覆盖或删除的条目全文。

## 后台审查通知（`display.memory_notifications`）

一轮结束之后，后台自我改进审查可能会悄悄保存一条记忆或更新一个 skill。这就是 Hermes 带同意机制的学习闭环：反复出现的纠正与持久的工作流经验会变成紧凑的记忆条目或程序性 skill，而 `write_approval` 可以让这些写入在影响未来会话之前先挂起待审。默认情况下它会在聊天里冒一行简短的 `💾 Memory updated`，让你知道发生了什么。控制它有多啰嗦：

```yaml
display:
  memory_notifications: on    # off | on (default) | verbose
```

| 取值 | 行为 |
|------|------|
| `off` | 不发聊天通知。审查照跑、照写 —— 只是你看不到那一行。 |
| `on`（默认） | 普通一行，如 `💾 Memory updated`、`💾 Skill 'foo' patched`。 |
| `verbose` | 附带改动的紧凑预览，如 `💾 Memory ➕ User prefers terse replies`，或一段 skill 的 `"old" → "new"` diff 片段。 |

> 这只管 **gateway** 的聊天通知。审查本身、以及对你的记忆/skill 存储的写入，都不受此设置影响。可按平台设置：`display.platforms.<platform>.memory_notifications`。

成功的 skill 批次在 `on` 与 `verbose` 模式下都会点名每个已应用的操作，包括辅助文件的写入/移除与 skill 删除。挂起待审的写入与已回滚的批次不会被报告为已完成的变更。批次摘要使用**实际应用**的结果，而不是假定请求的写入都执行了。

## 用更便宜的模型跑审查（`auxiliary.background_review`）

审查默认跑在你的**主聊天模型**上，方式是重放对话 —— 对话在 prompt cache 里已经是热的，所以只是便宜的缓存读取。如果主模型很贵，你可以改用更便宜的模型跑审查：

```yaml
auxiliary:
  background_review:
    provider: openrouter
    model: google/gemini-3-flash-preview   # auto (default) = main chat model
```

当你把它指向一个与主模型**不同**的模型时，审查就在那边运行，成本大幅降低（基准测试中约 3–5 倍）。由于另一个模型反正无法复用你主模型的 prompt cache，这个 fork 会自动重放一份紧凑的对话**摘要**（最近几轮逐字 + 更早轮次的概括），而不是完整记录 —— 最小化它写入新 cache 的内容。采集效果如何：测试中，记忆采集与主模型审查完全一致，skill 采集则近乎一致。

保持 `auto`（或设成你的主模型），一切照旧 —— 审查继续在主模型上用完整的热缓存重放运行。

### 同模型审查的推理设置

与父调用使用同一模型的审查**总是继承父调用的 reasoning effort**。设置 `auxiliary.background_review.reasoning_effort` 不会覆盖它，无论路由是 `auto` 还是显式选择了父 provider/模型。

推理设置、系统提示、完整对话快照与工具定义在 fork 诞生时与父调用逐字节一致，这样审查才能复用它的 prompt-cache 前缀。只改审查的思考级别会破坏这种一致性。同模型审查没有独立的 effort 开关。

要在不改变主对话 effort 的前提下减少审查工作量，可以调整 `memory.nudge_interval` / `skills.creation_nudge_interval`、按下面说的关闭自动审查，或把审查路由到别的模型。异模型路由使用摘要，不共享父调用的热前缀；在那条路由上 `auxiliary.background_review.reasoning_effort` **是**被遵守的（未设置 = 所路由 provider 的默认值）。当该键已设置但审查仍留在主模型上时，会打印一次性警告。这些频率与路由控制都无法解除同模型推理的绑定。

### 关闭自动审查（`enabled`）

在繁忙的机器上，审查 fork 可能烧掉相当大比例的总 token。运维可以在不把 nudge 间隔清零的情况下关掉它：

```yaml
auxiliary:
  background_review:
    enabled: true              # false = skip automatic post-turn forks
```

设 `enabled: false` 后，自动的轮后 fork 不再产生；手动 `/refine` 仍然可用，带不带聚焦文本都行。

### 限制审查开销（`max_input_tokens`）

审查循环在它发出的每次 provider 请求上都重放对话，所以单次审查的输入 token 会在其工具迭代中成倍累积。`max_input_tokens` 限制单次审查重放输入 token 的**总和**；循环会在越界之前停下。`<= 0` 表示不限制。

```yaml
auxiliary:
  background_review:
    max_input_tokens: 48000  # <= 0 = unlimited
```

未设置该键时，预算由审查模型解析出的上下文窗口推导：窗口的 75%，上限 600,000 token —— 因此在小的本地模型上同样生效（65,536 token 的模型拿到 49,152），而固定的云端规模默认值在那里永远不会起作用。如果窗口无法解析，则采用保守的 120,000 token 回退值。注意该键位于 `auxiliary:` 之下；顶层的 `background_review:` 块不会被读取。

fork 的用量以 `task='background_review'` 持久化到 `session_model_usage`，并会向 `agent.log` 写一行完成日志（`Background review complete: thread=bg-review calls=… in=… out=… result=…`）。

### 放行一个窄范围的额外审查工具（`extra_tools`）

后台审查默认可以使用记忆、skill 管理与只读文件工具。如果某个 profile 还提供了别的对无人值守审查安全的工具，可以按名字选择性放行：

```yaml
auxiliary:
  background_review:
    extra_tools:
      - propose_shared_memory
```

该工具必须已经对父 agent 可用；这个设置只是把它加进审查 fork 的运行时白名单。它不会启用任意工具，未列出的工具仍然被拒绝。请保持列表精简，并优先选择那些把提案挂起给人审核、而不是直接施加外部或破坏性改动的工具。默认是空列表。

### 本地模型：审查等待 GPU 空闲（`defer`）

在云 provider 上，审查几秒就跑完，与你接下来做什么并行。当审查的运行时是**托管的本地 llama-server**（Settings → Local models）时，同一个 fork 会占住你下一条提示所需的 GPU —— 大模型上要占几分钟 —— 而发送新提示会取消它，学习成果随之丢弃。因此在托管本地运行时上，审查**默认被推迟**：在轮次结束时排队，等机器安静过一个短暂的稳定窗口后再执行。审查本身没有任何变化 —— 同样的模型、同样的完整记录重放、同样的写入 —— 只是执行时刻挪了位置。

```yaml
auxiliary:
  background_review:
    defer: auto            # auto (default) | never
    defer_max_age_s: 1800  # run a queued review anyway after this long
```

| 取值 | 行为 |
|------|------|
| `auto`（默认） | 运行时解析为托管本地服务器的审查会被排队、在空闲时运行；其他所有运行时（云端、外部服务器）照旧立即产生。 |
| `never` | 处处保持旧行为：轮次结束立即产生，即使跑在托管本地 GPU 上。 |

排队的审查按会话合并（较新一轮的快照替换较旧的那个 —— 审查会重放整个对话，所以什么都不会丢），被新提示抢占的审查会重新排队而不是被丢弃，等待超过 `defer_max_age_s` 的审查即使机器始终不空闲也会运行。显式的 `/refine` 总是立即运行。队列在内存中：应用退出时仍在等待的审查会被丢弃，与一个进行中的 fork 被丢弃一样。

## 控制 skill 写入（`skills.write_approval`）

skill 用的是同一套开关闸门，但审核体验不同，因为 `SKILL.md` 远远大到没法在聊天气泡里读：

```yaml
skills:
  write_approval: false     # false = write freely (default) | true = require approval
```

`write_approval: true` 时，skill 写入（create / edit / patch / write_file / delete）无论来源一律**挂起**。你会就地看到一行要点，完整 diff 则留在带外：

```
/skills pending             # list staged skill writes + a one-line gist each
/skills diff <id>           # full unified diff (best viewed in CLI or dashboard)
/skills approve <id>        # apply it (or 'all')
/skills reject <id>         # drop it (or 'all')
/skills approval on         # turn the gate on (or 'off') and persist it
```

在消息平台上，凭要点加元数据即可批准一个 skill；想读完整改动，可以在 CLI / dashboard 上打开 `/skills diff`，或查看 `~/.hermes/pending/skills/<id>.json` 下的挂起文件。完整细节见 [Gating agent skill writes](./skills.md#门控-agent-的技能写入skillswrite_approval)。

## 外部记忆提供方

要获得超出 MEMORY.md 与 USER.md 的更深、更持久的记忆，Hermes 自带 2 个外部记忆提供方插件 —— RetainDB 与 ByteRover —— 还有更多，如 Honcho、Hindsight、Supermemory、Mem0、OpenViking 与 Holographic，可从[插件目录](plugins.md)用 `hermes plugins install <name>` 安装。

外部提供方与内置记忆**并行**运行（从不取代它），并增加知识图谱、语义搜索、自动事实抽取、跨会话用户建模等能力。

```bash
hermes memory setup      # pick a provider and configure it
hermes memory status     # check what's active
```

每个提供方的细节、安装步骤与对比见 [Memory Providers](./memory-providers.md) 指南。
