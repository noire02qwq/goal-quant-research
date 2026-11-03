---
sidebar_position: 2
title: "Hermes Agent Configuration"
description: "Configure Hermes Agent — config.yaml, providers, models, API keys, and more"
---

# Hermes Agent 配置（Hermes Agent Configuration）

> 来源：https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/configuration.md
> 原文：oss-repos/hermes-agent/website/docs/user-guide/configuration.md
> 翻译日期：2026-11-03 ｜ 范围：全文 ｜ 方式：机器翻译初稿，未经人工校对
> 引用于：docs/essay-study/hermes-2026.md、docs/brief-plan.md §3

本页的 Python 依赖命令使用 [PM 准备好的源码检出](../reference/package-management.md#developer-workflow)。依赖变更之后，请重新激活该检出并重启 Hermes。

所有设置都存放在 `~/.hermes/` 目录里，便于访问。

:::tip 拿到能用的 `config.yaml` 的最省事路径
运行 `hermes setup --portal`——一次 OAuth 就能拿到模型 provider 和全部四个 Tool Gateway 工具，不必手改 YAML。Portal 订阅者在按 token 计费的 provider 上还能打九折。见 [Nous Portal](../integrations/nous-portal.md)。
:::

## 目录



- [目录结构](#目录结构)

- [管理配置](#管理配置)

- [配置优先级](#配置优先级)

- [运行时限制](#运行时限制)

- [数据库设置](#数据库设置)

- [环境变量替换](#环境变量替换)

- [更新行为](#更新行为)

- [Terminal Backend 配置](#terminal-backend-配置)

- [Skill 设置](#skill-设置)

- [记忆配置](#记忆配置)

- [上下文文件截断](#上下文文件截断)

- [文件读取安全](#文件读取安全)

- [工具输出截断上限](#工具输出截断上限)

- [全局工具集禁用](#全局工具集禁用)

- [Git worktree 隔离](#git-worktree-隔离)

- [上下文压缩](#上下文压缩)

- [Gateway 回合租约超时](#gateway-回合租约超时)

- [Gateway 重启 drain](#gateway-重启-drain)

- [会话停滞看门狗](#会话停滞看门狗)

- [重连注意力升级](#重连注意力升级)

- [Gateway agent 缓存](#gateway-agent-缓存)

- [Context Engine](#context-engine)

- [迭代预算](#迭代预算)

- [墙钟运行预算](#墙钟运行预算)

- [停止时校验（编码验证）](#停止时校验编码验证)

- [常驻目标（`/goal`）](#常驻目标goal)

- [上下文压力告警](#上下文压力告警)

- [凭据池策略](#凭据池策略)

- [Prompt 缓存](#prompt-缓存)

- [辅助模型](#辅助模型)

- [推理力度](#推理力度)

- [Fast Mode](#fast-mode)

- [工具使用强制](#工具使用强制)

- [执行纪律指引](#执行纪律指引)

- [工具循环护栏](#工具循环护栏)

- [TTS 配置](#tts-配置)

- [显示设置](#显示设置)

- [隐私](#隐私)

- [语音转文字（STT）](#语音转文字stt)

- [语音模式（CLI）](#语音模式cli)

- [流式输出](#流式输出)

- [群聊会话隔离](#群聊会话隔离)

- [原生托管房间讨论限制](#原生托管房间讨论限制)

- [未授权私聊行为](#未授权私聊行为)

- [快捷命令](#快捷命令)

- [人工延迟](#人工延迟)

- [代码执行](#代码执行)

- [Web 搜索后端](#web-搜索后端)

- [浏览器](#浏览器)

- [时区](#时区)

- [Discord](#discord)

- [安全](#安全)

- [网站黑名单](#网站黑名单)

- [智能审批](#智能审批)

- [检查点](#检查点)

- [委派](#委派)

- [澄清](#澄清)

- [上下文文件（SOUL.md、AGENTS.md）](#上下文文件soulmdagentsmd)

- [工作目录](#工作目录)

- [网络](#网络)

- [引导](#引导)

- [Webapp](#webapp)

- [Dashboard](#dashboard)

## 目录结构

```text
~/.hermes/
├── config.yaml     # Settings (model, terminal, TTS, compression, etc.)
├── .env            # API keys and secrets
├── auth.json       # OAuth provider credentials (Nous Portal, etc.)
├── SOUL.md         # Primary agent identity (slot #1 in system prompt)
├── memories/       # Persistent memory (MEMORY.md, USER.md)
├── skills/         # Agent-created skills (managed via skill_manage tool)
├── cron/           # Scheduled jobs
├── sessions/       # Gateway sessions
└── logs/           # Logs (errors.log, gateway.log — secrets auto-redacted)
```

## 管理配置

```bash
hermes config              # View current configuration
hermes config edit         # Open config.yaml in your editor
hermes config get KEY      # Print a resolved value
hermes config set KEY VAL  # Set a specific value
hermes config unset KEY    # Remove a user-set value
hermes config check        # Check for missing options and stale saved selections
hermes config migrate      # Interactively add missing options

# Examples:
hermes config get model
hermes config set model anthropic/claude-opus-4
hermes config set terminal.backend docker
hermes config unset terminal.backend
hermes config set OPENROUTER_API_KEY sk-or-...  # Saves to .env
```

:::tip
`hermes config set` 会自动把值路由到正确的文件——每个 `UPPER_SNAKE` 形式的名字（`OPENROUTER_API_KEY`、`DISCORD_HOME_CHANNEL`、`TELEGRAM_GROUP_ALLOWED_USERS`、`HERMES_TIMEZONE`……）都是环境变量，存进 `.env`，绝不进 `config.yaml`；带点的设置进 `config.yaml`。其他任何 `UPPER_SNAKE` 名字原样存进 `.env`（它会被导出到进程环境供插件与 skill 使用）；落在 env 写入方黑名单上的名字（`HERMES_YOLO_MODE`、`PATH`……）会被拒绝。已知键若写在错误的前缀下（例如 `gateway.discord.foo`，其中 `discord.foo` 本身就是已知键），会在写入任何东西之前被拒绝，并附带「你是不是想写……」的提示；要强行写入请传 `--force`。已知段下的其他未知路径（比如拼错的 `agent.max_turnz`，或没有播种默认值的运行时读取键）会连同「你是不是想写……」提示一起写入，因为仅凭 schema 无法区分这两种情况。对这类路径执行 `hermes config get` 会打印你文件里的值，同时在 stderr 提示 Hermes 可能并不读它，这样一个遗留键就不可能悄悄冒充生效设置。
:::

## 配置优先级

设置按以下顺序解析（优先级从高到低）：

1. **CLI 参数** —— 例如 `hermes chat --model anthropic/claude-sonnet-4`（每次调用的覆盖）
2. **`~/.hermes/config.yaml`** —— 所有非机密设置的主配置文件
3. **`~/.hermes/.env`** —— 环境变量的兜底；机密（API key、token、密码）**必须**放这里
4. **内置默认值** —— 什么都没设置时使用的硬编码安全默认值

:::info 经验法则
机密（API key、bot token、密码）放 `.env`。其他一切（模型、terminal backend、压缩设置、记忆上限、工具集）放 `config.yaml`。两者都设置时，非机密设置以 `config.yaml` 为准。
:::

:::tip 组织部署
管理员可以通过系统级的受管目录，钉住标准用户无法覆盖的特定配置与机密值。见[受管范围](./managed-scope.md)。
:::

## 运行时限制

长驻的 Hermes server 界面（包括 gateway 与 `hermes serve --isolated`）在操作系统支持时，会在启动期间施加配置的 `RLIMIT_NOFILE` 软限制：

```yaml
runtime:
  nofile_soft_limit: 4096
```

默认值是 `4096`。Hermes 会把目标夹到操作系统的硬限制，且绝不会降低一个已经拥有更高软限制的进程。把值设为 `0`、`false` 或 `null` 可关闭这项调整。在 Windows 以及无法更改该限制的沙箱里，启动照常继续，不改限制。

在带 glibc 的 Linux 上，gateway、`hermes serve` 与 `hermes dashboard` 还会限制进程可创建的 malloc arena 数量：

```yaml
runtime:
  malloc_arena_max: 4
```

否则 glibc 会给每个新线程分配自己的 arena，每个 CPU 核最多八个，并保留每个 arena 已释放的页；一个跑着大量短命 worker 线程的长驻 gateway 最终会占着几百 MB 已释放却未归还的内存。该上限在启动时、服务器创建任何线程之前设定，且只作用于 Hermes server 进程本身——它运行的命令（terminal 工具、MCP server、构建）保持 glibc 默认。显式的 `MALLOC_ARENA_MAX`（或 `GLIBC_TUNABLES=glibc.malloc.arena_max=…`）优先，无论是在启动前导出还是写在 profile 的 `.env` 里。把值设为 `0`、`false` 或 `null` 则保持 glibc 默认。其他平台忽略此项。

## 数据库设置

`database:` 段控制 Hermes 如何打开它的 SQLite 状态数据库（`state.db`），该库存放会话、消息与 gateway 路由：

```yaml
database:
  # Journal mode for state.db: wal (default) or delete.
  # Use delete on filesystems where WAL is unsafe (network mounts). On
  # virtiofs/9p bind mounts (Docker Desktop, Podman on macOS, OrbStack)
  # Hermes detects the mount and creates fresh databases in delete mode
  # automatically. Note: an existing on-disk WAL database is never
  # live-downgraded — Hermes keeps WAL and logs an error telling you the
  # configured delete did not apply (or that the WAL database sits on a
  # cross-VM mount). To convert an existing database, stop
  # every process using it and run
  # `hermes sessions set-journal-mode delete` (see Sessions).
  journal_mode: wal

  # Durability level for every state.db connection: OFF, NORMAL, FULL,
  # EXTRA (or 0-3). Unset leaves SQLite's compile-time default, which
  # differs between interpreter builds. On macOS this is a floor, not a
  # pin: values below FULL are refused to protect against Darwin fsync
  # reordering; EXTRA is honored.
  # synchronous: FULL

  # Optional WAL sizing pragmas (integers). Unset = SQLite defaults.
  # wal_autocheckpoint: 1000     # pages between automatic checkpoints
  # journal_size_limit: 67108864 # cap the WAL/journal size in bytes
```

当一个既有数据库的磁盘 journal 模式在打开时被静默翻转成 WAL——例如运维曾手工把它转成 `delete`——Hermes 也会告警（每个数据库每个进程一次），并点名 `database.journal_mode` 这个让该选择持久生效的设置。反向绝不会自动发生：已经处于 WAL 模式的数据库在你设置 `journal_mode: delete` 时不会被在线降级（在连接打开的情况下降级可能损坏它）。`hermes doctor` 会一直警告 `<db> is in WAL mode despite database.journal_mode=delete`，直到你停掉该 profile 的所有 Hermes 进程并运行 `hermes sessions set-journal-mode delete`（只要还有东西持有该文件它就拒绝执行，并校验转换后的文件头）。该警告还会点名当前持有数据库的进程（`<db> is held by PID <n> (<command>)`），让你知道该停谁；当持有者扫描不完整或不可用时，它会说 `cannot prove the database is quiet`，而不是报一切正常。

## 环境变量替换

可以在 `config.yaml` 里用 `${VAR_NAME}` 语法引用环境变量：

```yaml
auxiliary:
  vision:
    api_key: ${GOOGLE_API_KEY}
    base_url: ${CUSTOM_VISION_URL}

delegation:
  api_key: ${DELEGATION_KEY}
```

单个值里可以引用多个变量：`url: "${HOST}:${PORT}"`。被引用的变量未设置时，占位符原样保留（`${UNDEFINED_VAR}` 保持不变）并记一条警告。裸的 `$VAR` 不会展开。

在[多路复用的多 profile gateway](./multi-profile-gateways.md) 下，profile 的 `config.yaml` 里的引用是对照**该 profile 自己的** `.env`（它的机密作用域）解析的，而不是共享的进程环境——profile B 里的 `${MATRIX_ACCESS_TOKEN}` 除非 B 自己定义了该变量，否则保持未解析（原样保留并记警告）。这适用于多路复用器内部加载 B 配置的所有位置：路由的 gateway 回合、B 的 adapter 启动、以及 B 的 cron 任务。单 profile 运行不受影响。完整清单见[每个 profile 隔离了什么](./multi-profile-gateways.md#what-is-isolated-per-profile)。

gateway 服务的本地 `hermes chat` / TUI 会话，会在创建会话时从其 profile 当前的 `config.yaml` 与 `.env` 解析这些引用、`provider_routing` 与 `prefill_messages_file`。对它们的修改会在下一个新会话生效，无需重启 gateway；已开会话保留其创建时的值。重启 gateway 也不会重新读取它们：重启后恢复的会话保留随它存储的路由与 prefill 路径，并在第一次需要时从该存储路径重新读取 prefill 文件的内容。在 gateway 启动时所用的那个 profile 上，你从 `.env` 删除的变量仍会解析到 gateway 启动时加载的值，因为查不到时会回退到进程环境；要让它失效需重启 gateway。

也接受 Cursor 风格的 SecretRef 语法：`${env:VAR_NAME}` 的解析与 `${VAR_NAME}` 完全相同（`env:` 前缀被剥掉），所以从 Cursor / Claude 配置复制来的 MCP 或 provider 片段在 `config.yaml` 与 `mcp_servers` 块里都能原样工作。其他 SecretRef 来源（`${file:...}`、`${vault:...}`、`${bitwarden:...}`）**不会**内联解析——外部机密后端会在启动时通过 `secrets:` 块把值注入环境，请改用 `${env:NAME}` 引用；未知前缀会告警一次并保持原样。

关于 AI provider 的设置（OpenRouter、Anthropic、自定义端点、自托管 LLM、fallback 模型等），见 [AI Providers](../integrations/providers.md)。

### Provider 超时

可以设置 `providers.<id>.request_timeout_seconds` 作为 provider 级的请求超时，再用 `providers.<id>.models.<model>.timeout_seconds` 做模型级覆盖。它作用于每种传输上的主回合客户端（OpenAI 线协议、原生 Anthropic、Anthropic 兼容）、fallback 链、凭据轮转后的重建，以及（对 OpenAI 线协议）每个请求的 timeout kwarg——因此配置值优先于遗留的 `HERMES_API_TIMEOUT` 环境变量。

也可以设置 `providers.<id>.stale_timeout_seconds` 作为非流式陈旧调用检测器的超时，再用 `providers.<id>.models.<model>.stale_timeout_seconds` 做模型级覆盖。它优先于遗留的 `HERMES_API_CALL_STALE_TIMEOUT` 环境变量。同一个键也是流式陈旧流的期限：显式值原样使用——隐式的按上下文规模分档（超过 5 万 token 为 240 秒，超过 10 万为 300 秒）与推理模型下限只适用于 180 秒这个默认值，所以显式值可以缩短卡死流的容忍时长。

这些都不设置时保持遗留默认（`HERMES_API_TIMEOUT=1800` 秒、`HERMES_API_CALL_STALE_TIMEOUT=90` 秒、原生 Anthropic 900 秒）。对本地端点，非流式陈旧检测器在隐式设置时会自动关闭，并可针对超大上下文向上伸缩。在 AWS Bedrock（`providers.bedrock`）上，解析出的请求超时是 boto3 Converse 客户端（`bedrock_converse`）与 AnthropicBedrock SDK 客户端的 socket 读超时，按活动模型逐请求选取，因此 `/model` 切换或 fallback 会使用该模型的值。连接超时保持固定（Converse 上 botocore 的 60 秒，AnthropicBedrock 上 10 秒），读超时约束的是每次 socket 读，而不是整个调用。不设置时 Converse 保持 botocore 的 60 秒读超时，AnthropicBedrock 为 900 秒。见 [`cli-config.yaml.example`](https://github.com/NousResearch/hermes-agent/blob/main/cli-config.yaml.example) 中的带注释示例。

## 更新行为

### 后台检查

被动更新检查（CLI 横幅、TUI 徽标、dashboard、桌面应用）会向 GitHub REST API 询问 `main` 的最新提交，当它与你的检出不同时，再问 compare 端点拿到确切的差异数量与变更日志。它们从不运行 `git fetch`——在部分克隆（`--filter=blob:none`）里也从不从 promisor 远端下载缺失对象（Git 2.44 及以上）——且每次安装至多**每 24 小时**问一次（失败的检查一小时后重试）。应用更新（`hermes update`，或桌面应用的 Update 按钮）总是重新抓取并使缓存答案失效。显式检查——`hermes update --check`、桌面应用的「Check for Updates…」菜单项、Settings → About →「Check now」——绕过缓存。

### SSH 认证

启动时的更新检查用与其网络调用同一套隔离 Git 配置读取 origin URL。因此全局的 `url.*.insteadOf` 改写无法把一个官方 SSH 远端藏起来不走公开 HTTPS 路径。

Hermes 的隔离内部 Git 命令默认用 `ssh -o BatchMode=yes`：未知主机密钥、密码、需要口令的加密密钥会直接失败，而不是打开终端询问。拥有可用密钥或 SSH agent 的受信主机继续正常认证。这不会改动磁盘上的 Git 或 SSH 配置，也不会改动你在 terminal 工具里运行的命令。

内部默认值会覆盖仓库的 `core.sshCommand` 设置。显式的 `GIT_SSH_COMMAND` 环境变量仍然优先，所以自定义的身份或传输命令可以保留在那里。若该覆盖必须保持非交互，请在其中包含 `-o BatchMode=yes`；允许询问的覆盖仍可能打断后台检查。

`hermes update` 相关设置在 `config.yaml` 的 `updates` 下：

```yaml
updates:
  pre_update_backup: quick       # quick (state snapshot, default) | full (snapshot + HERMES_HOME zip) | off
  backup_keep: 5                 # Keep this many full pre-update backup zips
  non_interactive_local_changes: stash  # stash | discard
  auto_switch_parked_branch: true       # auto-switch a clean, fully merged parked branch back to main
```

`pre_update_backup` 是更新前唯一的安全旋钮：`quick`（默认）把关键状态文件（配对数据、cron 任务、配置、认证；超过 1 GiB 的文件跳过）快照进 `state-snapshots/`；`full` 额外把整个 `HERMES_HOME` 打成 zip 放进 `backups/`，在大的 home 上可能多花几分钟；`off` 两者都关闭。遗留布尔值仍然生效（`true` → `full`，`false` → `off`）。

`config.yaml` 本身的定点副本（在 `hermes setup` 重写它之前、在 `hermes migrate` 编辑它之前、每次解析成功时、以及解析失败时）会写到 `backups/config/config.yaml.<reason>.<timestamp>`。完全相同的重复会被跳过，每种原因只保留最近五份，所以它们不会在 `config.yaml` 旁边堆积。如果 `config.yaml` 坏了，Hermes 会用最近的 `good` 副本代替内置默认值来服务，并在每次启动时告警，直到 YAML 修好为止；那个坏文件本身绝不被修改。

对 git 安装，Hermes 会在检出更新分支或拉取之前，自动 stash 脏的已跟踪文件，以及更新新增路径下的任何未跟踪文件。更新从不写入的未跟踪文件保持原位。交互式终端更新会在 stash 任何东西之前询问是否保留改动；回答「否」会直接删除它们，而不是留下一条 stash 条目。非交互式更新（桌面/聊天应用、gateway 或 `--yes`）使用 `updates.non_interactive_local_changes`：`stash` 在成功拉取后恢复本地源码编辑，`discard` 在成功拉取后丢弃更新创建的 stash。`discard` 只应用在本地源码编辑本就不应保留的受管安装上。

在那步 stash 之前，Hermes 还会还原 npm install/build 反复折腾留下的已跟踪 `package-lock.json` 差异。更新前请提交或手工 stash 掉有意为之的 lockfile 改动。

## Terminal Backend 配置

Hermes 自带六种 terminal backend。每一种决定 agent 的 shell 命令实际在哪里执行——你的本地机器、一个 Docker 容器、经 SSH 的远程服务器、Modal 云沙箱（直连或经 Nous 托管的 gateway）、Daytona workspace，或 Vercel Sandbox。插件还能再加，例如官方的 [Singularity/Apptainer](#singularityapptainer-backend) backend。

```yaml
terminal:
  backend: local    # local | docker | ssh | modal | daytona | vercel_sandbox | <plugin backend>
  cwd: "."          # Gateway/cron working directory (CLI always uses launch dir)
  temp_dir: ""      # Session temp root; empty = TMPDIR, else ~/.hermes/cache/terminal
  font_family: ""   # Desktop terminal font; e.g. "MesloLGS NF"
  timeout: 180      # Per-command timeout in seconds
  home_mode: auto   # auto | real | profile — subprocess HOME policy
  env_passthrough: []  # Env var names to forward to sandboxed execution (terminal + execute_code)
  client_env_passthrough: []  # Extra non-secret toolchain names (e.g. GEM_HOME) a local CLI/TUI session's tools take from its launching shell
  sync_back_max_bytes: 2147483648  # Remote backends: refuse to extract a state archive larger than this (bytes)
  modal_image: "nousresearch/hermes-sandbox:desktop"                 # Container image for Modal backend
  daytona_image: "nousresearch/hermes-sandbox:desktop"               # Container image for Daytona backend
```

`terminal.temp_dir` 控制 Hermes 在 local backend 上把会话临时产物放在哪里——后台进程的日志/pid/退出文件、代码执行沙箱、以及溢出的工具结果。它为空（默认）时，Hermes 会尊重环境中显式的 `TMPDIR`/`TMP`/`TEMP`，否则改用真实存储上的受管目录 `~/.hermes/cache/terminal`，而不是 `/tmp`——在许多发行版上（尤其是 Arch 系配置），`/tmp` 是一个由内存支撑的小 tmpfs，负载高时 Hermes 的会话产物会把它撑爆。该受管目录会被自动清理：空闲 24 小时（其内部任何位置一天没有写入）的条目，gateway 家务进程每小时扫一次，纯 CLI 安装则每个进程扫一次。把 `temp_dir` 设成一个已存在的绝对路径，可以把会话临时文件挪到别处；用户设置的路径绝不自动清理。

与 `terminal.temp_dir` 无关，每个 Hermes 进程（CLI、TUI、gateway、Desktop backend、cron）以及它启动的每个子进程，在启动时都会把 `TMPDIR`、`TMP`、`TEMP` 指向 **`~/.hermes/cache/scratch`**（按 profile 区分），于是 `tempfile.mkdtemp()`、`mktemp`、浏览器 profile 和探测脚本全都落在真实存储上，而不是内存支撑的系统临时目录。System prompt 会点名这个 scratch 目录。Hermes 只在这些变量尚未设置时才设置——你或操作系统导出的 `TMPDIR`（macOS 的 `/var/folders`、Windows 的 `%TEMP%`）保持不变。

条目在**空闲满 24 小时**后由启动后立刻拉起的后台进程清理（每小时至多一次；启动从不等它，即使命令立即退出该轮也会跑完）：只要条目内部任何地方在过去一天里有过写入就保留，最后一次写入之后满一天就删除。硬链接文件不算写入（`git clone --local` 与其源仓库共享 pack 文件，源仓库的活动否则会让克隆永生）。

删除一个空闲条目之前，Hermes 还会停掉任何工作目录仍在该条目内运行的进程（或在一个已不存在的 scratch 路径内，例如测试遗留的无头浏览器），并丢弃任何指向其中的 `git worktree` 注册。Hermes 自己启动且仍在追踪的进程（后台 `terminal` 进程、gateway、CLI 会话，或它们启动且仍是其子进程的任何东西）从不停止；启动 Hermes 命令的那个 shell（或它的父进程）也不停，即使该命令已退出——它们中有人正在其中工作的空闲条目会被保留。无法检查进程的那一轮不停任何进程，也不删除任何进程可能正在其中工作的条目。每个条目在删除前都会再检查一次，因此在清理轮停进程期间被写入的条目会被保留。每一次删除、被停进程与被保留条目都记录在 `~/.hermes/logs/scratch-prune.log` 里。含有你的用户可能读不了或删不掉的文件的条目（典型是 Docker 容器写进 bind mount 的 root 属主产物）绝不会在半盲状态下被部分删除：它会连同删除它的命令记一次日志（`sudo rm -rf '<path>'`，装了 Docker 时也可用 `docker run … rm -rf` 替代），然后跳过，不再每小时重扫，直到它消失、其顶层目录变化、或当初拒绝访问的目录对你变得可访问（例如执行过 `sudo chown -R` 之后）；无论如何每周仍会再检查一次。Hermes 从不自己运行那条命令。`hermes doctor` 会报告该目录、其大小以及这类被跳过的条目，并对 `cache/` 下其他没有清理器覆盖、超过 1 GB 的目录告警。

`desktop.font_family` 设置聊天以及 Hermes Desktop 其余界面的字体（终端面板有自己的键，见上文）。给它一个已安装的字体族名（例如 `OpenDyslexic` 或 `Atkinson Hyperlegible`）或一个 CSS 字体栈；Hermes 会在其后保留当前主题自己的字体栈，这样中日韩与 emoji 字形仍能解析，留空则使用主题字体。在 **Settings → Appearance → Chat Font** 里编辑。

`terminal.font_family` 控制 Hermes Desktop 里的内嵌终端。它接受一个本地安装的字体族名（例如 `MesloLGS NF`）或一个 CSS 字体栈。Hermes 会在后面追加自带的 JetBrains Mono 字体栈作为兜底，留空则保持默认。同一个按 profile 区分的设置也可以在 **Settings → Appearance → Terminal Font** 里编辑；不需要下载 Google Fonts，也不需要系统字体权限。

对 Modal、Daytona、Vercel Sandbox 这类云沙箱，`container_persistent: true` 表示 Hermes 会尽量在沙箱重建之间保留文件系统状态。它不承诺同一个活沙箱、PID 空间或后台进程之后仍在运行。

### Backend 总览

| Backend | 命令在哪跑 | 隔离 | 适合 |
|---------|-------------------|-----------|----------|
| **local** | 直接在你的机器上 | 无 | 开发、个人使用 |
| **docker** | 单个持久 Docker 容器（跨会话、`/new`、subagent 共享） | 完整（namespace、cap-drop） | 安全沙箱、CI/CD |
| **ssh** | 经 SSH 的远程服务器 | 网络边界 | 远程开发、强劲硬件 |
| **modal** | Modal 云沙箱 | 完整（云 VM） | 临时云算力、评测 |
| **daytona** | Daytona workspace | 完整（云容器） | 托管云开发环境 |
| **vercel_sandbox** | Vercel Sandbox | 完整（云 microVM） | 云端执行，文件系统持久化由快照支撑 |
| **singularity**（插件） | Singularity/Apptainer 容器 | Namespace（--containall） | HPC 集群、共享机器 |

### Local Backend

默认值。命令直接在你的机器上执行，没有隔离。无需特殊设置。

```yaml
terminal:
  backend: local
```

默认情况下，本地工具子进程保留你真实的 OS 用户 `HOME`。这让 `git`、`ssh`、`gh`、`az`、`npm`、Claude Code、Codex 之类的外部 CLI 能找到它们在你正常 shell 里已经在用的凭据与配置。Hermes 的状态仍通过 `HERMES_HOME` 按 profile 划分；profile 选择配置、记忆、会话或 skill 用的不是 `HOME`。

Hermes **不会**改动你系统级的 `HOME`、你的 shell 启动文件，或操作系统账户的 home。这个设置只控制传给 Hermes 经 `terminal` 等工具启动的子进程、后台 terminal 进程、`execute_code` 与 ACP 辅助进程的环境。

#### `terminal.home_mode`

| 模式 | 宿主安装 | 容器 | 取舍 |
|---|---|---|---|
| `auto` | 保留真实 OS 用户 `HOME` | 使用 `{HERMES_HOME}/home` | 推荐默认。宿主 CLI 继续可用；容器状态持久。 |
| `real` | 强制真实 OS 用户 `HOME` | 可见时强制真实 OS 用户 `HOME` | 当父进程误以 `HOME` 指向 profile home 启动时有用。 |
| `profile` | 存在时使用 `{HERMES_HOME}/home` | 存在时使用 `{HERMES_HOME}/home` | 严格的按 profile CLI 配置隔离，但正常的 `~/.ssh`、`~/.gitconfig`、`~/.azure`、`~/.config/gh`、Claude/Codex 认证、npm 状态等都看不到，除非你在 profile home 里初始化或链接它们。 |

默认模式的缺点是宿主上的各个 profile 共享 `~` 下同一套普通用户级 CLI 凭据/配置。如果你需要一个带独立 git 身份、SSH 密钥、GitHub CLI 登录、npm 配置或云 CLI 登录的 profile，用 `home_mode: profile`，并有意识地在该 profile home 内初始化这些工具。

如果你确实想要严格的按 profile 工具配置隔离，设置：

```yaml
terminal:
  home_mode: profile
```

该模式下工具子进程用 `{HERMES_HOME}/home` 作为 `HOME`。Hermes 还会设置 `HERMES_REAL_HOME`，让脚本在需要时仍能定位到真实用户 home。容器 backend 在 `auto` 模式下继续用 `{HERMES_HOME}/home`，因为该目录位于持久的 Hermes 数据卷上。

需要区分 profile 状态与真实用户 home 的脚本，应以 `HERMES_HOME` 取 Hermes 数据、以 `HERMES_REAL_HOME` 取账户 home：

```python
from pathlib import Path
import os

hermes_home = Path(os.environ["HERMES_HOME"])
real_home = Path(os.environ.get("HERMES_REAL_HOME", os.environ["HOME"]))
```

:::warning
Agent 拥有与你的用户账户相同的文件系统访问权。用 `hermes tools` 禁用你不想给的工具，或改用 Docker 做沙箱。
:::

### Docker Backend

在 Docker 容器内执行命令，带安全加固（丢弃全部 capability、禁止提权、PID 限制）。

**持久容器，跨 Hermes 进程共享。** 在 `container_persistent: true` 与 `docker_mount_cwd_to_workspace: false`（均为默认）下，同一 profile 的会话共享它最初的那个沙箱。此模式下在 Desktop 里选工作目录不会另建一个 workspace 沙箱，因此 CLI 与 Desktop 仍访问同一批文件。启用宿主 workspace 挂载后，持久容器改为按 profile 与所选 workspace 为键：同一 workspace 的会话共享一个容器，不同 workspace 各自分开。`delegate_task` subagent 用其父进程的容器。

更早的构建即使在挂载关闭时也给每个 Desktop 目录一个独立沙箱。那些目录（`TERMINAL_SANDBOX_DIR/docker` 下的 `*_ws_*`，默认在 profile 的 Hermes home 里的 `sandboxes/docker`）仍保留，但 terminal 与文件面板不再使用：把你还需要的东西拷进 profile 沙箱的 `workspace` 或 `home`。

在具名 profile 里，它的 gateway 聊天、Desktop 会话、cron 任务与 Kanban worker 全都使用该 profile 唯一的沙箱（`TERMINAL_SANDBOX_DIR/docker` 下的 `profile_<name>-*`）。更早的构建会把以该 profile 启动的 gateway（`hermes -p <name> gateway`）及其 cron、Kanban 工作放在 profile home 下另一个独立的 `default` 沙箱里。那个目录仍保留，但不再使用：同样方式把需要的东西拷出来。

Terminal、文件与 `execute_code` 调用在所选容器里用 `docker exec`。已安装的包、`/workspace` 里的文件与**后台进程**会在调用之间、以及使用该容器的 Hermes 进程之间延续。关闭 TUI 会话、运行 `/quit` 或启动新的 `hermes` 调用本身不会移除它；下一个进程可以通过它的标签复用它。确切的拆除规则见下文**容器生命周期**。

**按会话隔离模式（`container_persistent: false`）。** 给 Docker backend 设置 `container_persistent: false` 会切换成**每个会话一个**容器：每次聊天（桌面应用会话、gateway 对话、TUI 会话）都拿到自己的全新沙箱，在首次 terminal/文件调用时创建，会话关闭或空闲超过 `lifetime_seconds` 时移除。会话之间什么都不延续——没有文件系统状态、没有挂载、没有后台进程。`docker_mount_cwd_to_workspace: true` 时，只有**该会话挂接的** workspace 才挂到 `/workspace`；没有挂接目录的新会话拿到空 workspace，而不是继承上一个会话的挂载。`delegate_task` subagent 仍与其父会话共享容器。当沙箱是对话之间的安全边界时用这个模式；想要上文描述的长寿命共享容器就保持默认的 `true`。

```yaml
terminal:
  backend: docker
  # Default: nikolaik/python-nodejs (Python 3.13 / Node 26) plus a display stack, so Bot Screen,
  # computer_use and the browser run INSIDE this sandbox (Bot Screen → "Where the screen runs").
  # Any other image works for shell work; the screen then needs bot_desktop.placement: gateway.
  # Writing this key is a decision: a persisted container on another image is recreated on the next
  # terminal call. Left unset, an existing container is kept and the CLI / Screen pane ask first.
  docker_image: "nousresearch/hermes-sandbox:desktop"
  docker_mount_cwd_to_workspace: false  # Mount launch dir into /workspace
  docker_run_as_host_user: false   # See "Running container as host user" below
  docker_snap_compat: false        # See "Snap-packaged Docker (AppArmor)" below
  docker_forward_env:              # Host env vars to forward into container
    - "GITHUB_TOKEN"
  docker_env:                      # Literal env vars to inject (KEY=value)
    DEBUG: "1"
    PYTHONUNBUFFERED: "1"
  docker_volumes:                  # Host directory mounts
    - "/home/user/projects:/workspace/projects"
    - "/home/user/data:/data:ro"   # :ro for read-only
  docker_extra_args:               # Extra flags appended verbatim to `docker run`
    - "--gpus=all"
    - "--network=host"
  docker_network: true             # false = air-gap the container (--network=none)

  # Resource limits
  container_cpu: 1                 # CPU cores (0 = unlimited)
  container_memory: 5120           # MB (0 = unlimited)
  container_disk: 51200            # MB (requires overlay2 on XFS+pquota)
  container_persistent: true       # true = persist /workspace + /root, shared container; false = fresh container per session (see below)

  # Cross-process container reuse (defaults match the "one long-lived
  # container shared across sessions" contract — see Container lifecycle).
  docker_persist_across_processes: true   # Reuse container across Hermes restarts
  docker_shared_container_key: ""         # Opt in trusted profiles to one identity
  docker_orphan_reaper: true              # Sweep abandoned Exited containers at startup

  # Cross-backend lifecycle settings (apply to docker as well)
  timeout: 180                     # Per-command timeout in seconds
  lifetime_seconds: 300            # Idle-reaper window; also feeds 2× orphan-reaper threshold
```

**`docker_env`** 对比 **`docker_forward_env`**：前者注入你在配置里指定的字面 `KEY=value` 对（值存在 `config.yaml` 里，或经 `TERMINAL_DOCKER_ENV='{"DEBUG":"1"}'` 以 JSON 字典传入）；后者从你的 shell 或 `~/.hermes/.env` 转发值，因此真正的机密绝不出现在配置文件里。token 用 `docker_forward_env`，容器需要的静态旋钮用 `docker_env`。

**`terminal.docker_extra_args`**（也可用 `TERMINAL_DOCKER_EXTRA_ARGS='["--gpus=all"]'` 覆盖）让你传入 Hermes 没有做成一等键的任意 `docker run` 标志——`--gpus`、`--network`、`--add-host`、替代的 `--security-opt` 覆盖等。每项必须是字符串；该列表追加到组装好的 `docker run` 调用末尾，因此必要时可以覆盖 Hermes 的默认值。请慎用——与沙箱加固冲突的标志（capability 丢弃、`--user`、workspace bind 挂载）会悄悄削弱隔离。

**`terminal.docker_network`**（默认 `true`；环境变量 `TERMINAL_DOCKER_NETWORK`）——设为 `false` 时沙箱容器用 `--network=none` 运行，切断 agent 命令的一切网络出口。这作用于 `terminal`、`execute_code` 与文件工具使用的执行容器。由于容器跨 Hermes 进程持久，在存在较旧联网容器时把它翻成 `false` 会移除那个容器并启动一个新的气隙容器（会记一条警告）；其中运行的后台进程会丢失。优先用这个键，而不是通过 `docker_extra_args` 传 `--network=none`。

**前置条件：**已安装并运行 Docker Desktop 或 Docker Engine。Hermes 会探测 `$PATH` 加上常见的 macOS 安装位置（`/usr/local/bin/docker`、`/opt/homebrew/bin/docker`、Docker Desktop 应用包）。Podman 开箱即用：两者都装了时设 `HERMES_DOCKER_BINARY=podman`（或完整路径）来强制使用它。

#### 容器生命周期

Hermes 管理的容器带有标签，后续进程（以及孤儿回收器）据此识别它们：

- `hermes-agent=1` —— 标明它由 Hermes 管理
- `hermes-task-id=<sanitized task_id>` —— 按任务复用探测的键
- `hermes-profile=<sanitized profile name>` —— 默认把复用与回收限定在当前 Hermes profile；设置 `docker_shared_container_key` 时改用其清洗后的值
- `hermes-environment=<digest>` —— 对没有显式共享键的容器，把复用限定到所请求的镜像、挂载参数与活动的 `HERMES_HOME`；宿主路径与卷来源做哈希而不暴露在该标签里。来自进程临时目录的挂载（那份防符号链接问题的 skill 拷贝）按其稳定的容器路径哈希，而不是按随机的宿主临时目录，因此不会破坏复用

启动时，Hermes 运行 `docker ps --filter label=hermes-task-id=<id> --filter label=hermes-profile=<identity>`，找到匹配就**附着到既有容器**。该身份就是当前 profile，除非 `docker_shared_container_key` 显式让受信 profile 共用一个值。如果容器处于 `exited`（例如 Docker 守护进程重启之后），会被 `docker start` 并复用——文件系统状态与已安装的包都还在，但容器内的后台进程不在了。

没有显式共享键时，复用探测还要求 `hermes-environment` 标签匹配。改动镜像、挂载参数或 `HERMES_HOME` 会启动全新容器，而不是悄悄沿用另一套配置。在该标签引入之前创建的容器匹配不上，所以升级后的第一个会话会起一个全新容器；既有运行中的容器不会被移除。

Hermes 进程退出时——`/quit`、关闭 TUI 会话、gateway 关停、甚至 SIGKILL——默认模式下清理路径对容器是**空操作**。容器继续运行。下一个 Hermes 进程在几毫秒内经标签探测附着上去。这正是「跨会话共享一个长寿命容器」契约所要求的行为：只有这样，后台进程（npm watcher、dev server、长跑的 pytest）才能跨会话存活。

**只有在这些情况下容器才会被拆除（停止并 `docker rm -f`）：**

| 触发条件 | 何时生效 |
|---|---|
| `docker_persist_across_processes: false` | 显式的按进程隔离。每次 `cleanup()` 都做 `stop` + `rm -f`。与 issue #20561 之前的行为一致。 |
| 空闲回收器（`lifetime_seconds`，默认 300 秒） | 仅当环境是 `persist_across_processes=false`。持久模式的环境是空操作；容器挺过空闲清扫。 |
| 下次启动时的孤儿回收器 | 扫描**已 Exited**、年龄超过 `2 × lifetime_seconds`（默认 600 秒 = 10 分钟）的 hermes 标签容器，范围限定当前 profile。**运行中的容器绝不动**——保证兄弟进程安全。设 `docker_orphan_reaper: false` 可关闭。 |
| 用户直接操作 | `docker rm -f`、`docker system prune`、重启 Docker Desktop。我们不设 `--restart=always`，所以宿主重启后容器停在 `Exited`（其 CoW 层还在，下次启动会被复用，但后台进程没了）。 |

值得知道的边界情况：

- **容器内 PID 1 被 OOM 杀掉**会让容器转为 `Exited`。下次复用会 `docker start` 它；文件系统状态还在，后台进程没了。
- **切换 profile** 会把容器相互隔离——标着 `hermes-profile=work` 的容器对跑在 `hermes-profile=research` 下的 Hermes 进程不可见。孤儿回收器同样按 profile 划分，所以跨 profile 的容器不会被误回收，但在你用它们原来的 profile 再次启动 Hermes 之前也不会被自动清理。
- **显式跨 profile 共享**——为有意在同一个受信 workspace 里协作的 profile，在 `terminal:` 下设置相同的非空 `docker_shared_container_key`。这只替换它们的容器身份标签；任务、出口与网络兼容性检查仍然生效。没有该键的 profile 保持隔离。身份标签由该键加一个短摘要后缀推导，所以看起来相似的键（`team/workspace` 与 `team_workspace`）绝不会撞进同一个容器。**重要：共享容器只创建一次，由最先启动它的那个 profile 创建**——该 profile 的 `docker_image`、卷、shm 大小与其他不可变 Docker 设置胜出，后续 profile 原样附着；它们配置里不同的设置会被忽略，直到容器被移除重建。共享同一个键的 profile 应当在镜像与挂载上达成一致。

经 `delegate_task(tasks=[...])` 派生的并行 subagent 共享这一个容器——并发的 `cd`、环境变量改动与同路径写入会互相冲突。如果某个 subagent 需要隔离沙箱，它必须经 `register_task_env_overrides()` 注册按任务的镜像覆盖，RL 与 benchmark 环境（TerminalBench2、HermesSweEnv 等）会为它们的按任务 Docker 镜像自动这么做。

**安全加固：**

- `--cap-drop ALL`，只加回 `DAC_OVERRIDE`、`CHOWN`、`FOWNER`
- `--security-opt no-new-privileges`
- `--pids-limit 256`
- 给 `/tmp`（512MB）、`/var/tmp`（256MB）、`/run`（64MB）配容量受限的 tmpfs

**凭据转发：** `docker_forward_env` 里列出的环境变量先从你的 shell 环境解析，再回退到 `~/.hermes/.env`（若它曾用 `hermes config set` 保存）。Skill 也可以声明 `required_environment_variables`，会自动合并进来。

#### 环境变量覆盖

`terminal:` 下的每个键都有形如 `TERMINAL_<KEY_UPPERCASE>` 的环境变量覆盖。对 Docker backend 最有用的几个：

| 环境变量 | 对应 | 说明 |
|---|---|---|
| `TERMINAL_DOCKER_IMAGE` | `docker_image` | 基础镜像 |
| `TERMINAL_DOCKER_FORWARD_ENV` | `docker_forward_env` | JSON 数组：`'["GITHUB_TOKEN","OPENAI_API_KEY"]'` |
| `TERMINAL_DOCKER_ENV` | `docker_env` | JSON 字典：`'{"DEBUG":"1"}'` |
| `TERMINAL_DOCKER_VOLUMES` | `docker_volumes` | 由 `"host:container[:ro]"` 字符串组成的 JSON 数组 |
| `TERMINAL_DOCKER_EXTRA_ARGS` | `docker_extra_args` | JSON 数组 |
| `TERMINAL_DOCKER_MOUNT_CWD_TO_WORKSPACE` | `docker_mount_cwd_to_workspace` | `true` / `false` |
| `TERMINAL_DOCKER_RUN_AS_HOST_USER` | `docker_run_as_host_user` | `true` / `false` |
| `TERMINAL_DOCKER_SNAP_COMPAT` | `docker_snap_compat` | `true` / `false` —— 默认 `false` |
| `TERMINAL_DOCKER_NETWORK` | `docker_network` | `true` / `false` —— 默认 `true`；`false` = `--network=none` |
| `TERMINAL_DOCKER_PERSIST_ACROSS_PROCESSES` | `docker_persist_across_processes` | `true` / `false` —— 默认 `true` |
| `TERMINAL_DOCKER_SHARED_CONTAINER_KEY` | `docker_shared_container_key` | 给受信 profile 的显式共享身份；默认为空 |
| `TERMINAL_DOCKER_ORPHAN_REAPER` | `docker_orphan_reaper` | `true` / `false` —— 默认 `true` |
| `TERMINAL_CONTAINER_CPU` | `container_cpu` | CPU 核数 |
| `TERMINAL_CONTAINER_MEMORY` | `container_memory` | MB |
| `TERMINAL_CONTAINER_DISK` | `container_disk` | MB |
| `TERMINAL_CONTAINER_PERSISTENT` | `container_persistent` | `true` / `false` —— 控制 bind 挂载的 workspace 目录，与 `docker_persist_across_processes` 不同 |
| `TERMINAL_LIFETIME_SECONDS` | `lifetime_seconds` | 空闲回收窗口 |
| `TERMINAL_TEMP_DIR` | `temp_dir` | 会话临时根目录（local backend） |
| `TERMINAL_TIMEOUT` | `timeout` | 每命令超时 |
| `HERMES_DOCKER_BINARY` | _无_ | 强制指定 docker/podman 二进制路径 |

### SSH Backend

经 SSH 在远程服务器上执行命令。用 ControlMaster 复用连接（5 分钟空闲保活）。每条命令都是一次全新的 `ssh … bash -c`；工作目录始终延续，导出的环境变量在 `persistent_shell` 打开（默认）时延续。见[常驻 shell](#常驻-shell)。

```yaml
terminal:
  backend: ssh
  persistent_shell: true           # Carry exported env vars between commands (default: true)
```

**必需的环境变量：**

```bash
TERMINAL_SSH_HOST=my-server.example.com
TERMINAL_SSH_USER=ubuntu
```

**可选：**

| 变量 | 默认 | 说明 |
|----------|---------|-------------|
| `TERMINAL_SSH_PORT` | `22` | SSH 端口 |
| `TERMINAL_SSH_KEY` | （系统默认） | SSH 私钥路径 |
| `TERMINAL_SSH_PERSISTENT` | 跟随 `terminal.persistent_shell`（`true`） | 命令之间延续导出的环境变量 |

**工作原理：**初始化时用 `BatchMode=yes` 与 `StrictHostKeyChecking=accept-new` 连接，然后把远程登录 shell 的环境一次性捕获进一个快照文件。每条命令都以新的 `bash -c` 运行，该 shell source 那份快照、`cd` 到被跟踪的工作目录，再执行你的命令。

**Skill / 配置环境透传：**skill 在 `required_environment_variables` 里声明的变量，或你在 `terminal.env_passthrough` 下列出的变量，经 OpenSSH 的 `SendEnv` 转发——名字出现在 `ssh` 命令行上，值随客户端环境传递，绝不出现在远程命令文本里。远程 `sshd` 必须接受它们；在服务器的 `/etc/ssh/sshd_config` 里添加并重载 sshd：

```
AcceptEnv NEXTCLOUD_URL NEXTCLOUD_*      # or the names your skills need
```

没有匹配的 `AcceptEnv` 时，服务器会静默丢弃这些变量，远程 shell 看到它们未设置。Hermes 的 provider 凭据（`OPENAI_API_KEY`……）即使列出也绝不转发。见[环境变量透传](security.md#environment-variable-passthrough)。

### Modal Backend

在 [Modal](https://modal.com) 云沙箱里执行命令。每个任务拿到一台可配置 CPU、内存与磁盘的隔离 VM。文件系统可以在会话之间快照/还原。

```yaml
terminal:
  backend: modal
  container_cpu: 1                 # CPU cores
  container_memory: 5120           # MB (5GB)
  container_disk: 51200            # MB (50GB)
  container_persistent: true       # Snapshot/restore filesystem
```

**必需：** `MODAL_TOKEN_ID` + `MODAL_TOKEN_SECRET` 环境变量，或一个 `~/.modal.toml` 配置文件。

**持久化：**启用时，清理时快照沙箱文件系统，下次会话还原。快照记录在 `~/.hermes/modal_snapshots.json`，一直保留到你删除为止（Hermes 选择退出 Modal SDK 的 30 天快照过期）。它保留的是文件系统状态，不是活进程、PID 空间或后台作业。

**凭据文件：**自动从 `~/.hermes/` 挂载（OAuth token 等），并在每条命令前同步。

### Daytona Backend

在 [Daytona](https://daytona.io) 托管 workspace 里执行命令。支持停止/恢复以实现持久化。

```yaml
terminal:
  backend: daytona
  container_cpu: 1                 # CPU cores
  container_memory: 5120           # MB → converted to GiB
  container_disk: 10240            # MB → converted to GiB (max 10 GiB)
  container_persistent: true       # Stop/resume instead of delete
```

**必需：** `DAYTONA_API_KEY` 环境变量。

**持久化：**启用时，清理时沙箱被停止（不删除），下次会话恢复。沙箱名遵循 `hermes-{task_id}` 模式。

**磁盘上限：**Daytona 强制 10 GiB 上限。超过的请求会被截断并告警。

### Vercel Sandbox Backend

在 [Vercel Sandbox](https://vercel.com/docs/vercel-sandbox) 云 microVM 里执行命令。Hermes 使用常规的 terminal 与文件工具界面；没有 Vercel 专属的面向模型工具。

```yaml
terminal:
  backend: vercel_sandbox
  vercel_image: vercel/sandbox/universal:latest   # Vercel managed image or a VCR repository[:tag]
  cwd: /vercel/sandbox            # default workspace root
  container_persistent: true      # Snapshot/restore filesystem
  container_disk: 51200           # Shared default only; custom disk is unsupported
```

**必需安装：**安装可选的 SDK 扩展：

```bash
python -c "import pm; pm.sync_venv(['vercel'], explicit=True)"
```

**必需认证：**配置访问令牌认证，需同时具备 `VERCEL_TOKEN`、`VERCEL_PROJECT_ID`、`VERCEL_TEAM_ID` 三者。这是在 Render、Railway、Docker 及类似主机上做部署与常规长驻 Hermes 进程所支持的设置方式。

一次性本地开发时，Hermes 也接受短寿命的 Vercel OIDC token：

```bash
VERCEL_OIDC_TOKEN="$(vc project token <project-name>)" hermes chat
```

在已 link 的 Vercel 项目目录里可以省略项目名：

```bash
VERCEL_OIDC_TOKEN="$(vc project token)" hermes chat
```

OIDC token 寿命很短，不应作为文档推荐的部署路径。

**镜像：**`terminal.vercel_image` 为新沙箱挑选容器镜像：[Vercel 托管镜像](https://vercel.com/docs/sandbox/concepts/images)，例如 `vercel/sandbox/universal:latest`（默认：Ubuntu、Node.js 24、Python 3.14）、`vercel/sandbox/node:26` 或 `vercel/sandbox/python:3.14`，也可以是来自你项目 Vercel Container Registry 的仓库（裸名解析为 `latest`；tag 或 digest 可钉死）。较旧的 `terminal.vercel_runtime` 预设（`node24`、`node22`、`python3.13`）已被 [Vercel 弃用](https://vercel.com/docs/sandbox/concepts/runtimes)；钉死 runtime 仍然可用并覆盖镜像，但两者不能混用。快照还原自带文件系统，两者都不发送。

**持久化：**`container_persistent: true` 时，Hermes 在清理期间快照沙箱文件系统，并在之后为同一任务从该快照还原沙箱。快照内容可以包含被拷进沙箱的 Hermes 同步凭据、skill 与缓存文件。它只保留文件系统状态；不保留活的沙箱身份、PID 空间、shell 状态或运行中的后台进程。

**后台命令：**`terminal(background=true)` 走 Hermes 通用的非本地后台进程流程。沙箱存活期间你可以用常规 process 工具拉起、轮询、等待、查看日志与杀掉进程。清理或重启之后，Hermes 不提供原生的 Vercel 分离进程恢复。

**磁盘容量：**Vercel Sandbox 目前不支持 Hermes 的 `container_disk` 资源旋钮。请保持 `container_disk` 不设或用共享默认值 `51200`；非默认值会让诊断与 backend 创建失败，而不是被静默忽略。

### Singularity/Apptainer Backend

在 [Singularity/Apptainer](https://apptainer.org) 容器里执行命令。为 Docker 不可用的 HPC 集群与共享机器设计。它是官方的 [`singularity` 插件](https://github.com/NousResearch/hermes-official-plugins/tree/main/singularity)（曾内置在 core 中；`hermes update` 会为已经在用它的 profile 安装它）：

```bash
hermes plugins install singularity
```

```yaml
terminal:
  backend: singularity
  singularity_image: "docker://nousresearch/hermes-sandbox:desktop"
  container_cpu: 1                 # CPU cores
  container_memory: 5120           # MB
  container_persistent: true       # Writable overlay persists across sessions
```

**前置条件：**`singularity` 插件，且 `$PATH` 里有 `apptainer` 或 `singularity` 二进制。

**镜像处理：**Docker URL（`docker://...`）会自动转成 SIF 文件并缓存。已有的 `.sif` 文件直接使用。

**Scratch 目录：**按顺序解析：`TERMINAL_SCRATCH_DIR` → 当 `/scratch` 可写（HPC 惯例）时用 `/scratch/$USER/hermes-agent` → `TERMINAL_SANDBOX_DIR/singularity`（默认 `~/.hermes/sandboxes/singularity`）。

**隔离：**用 `--containall --no-home` 实现完整的 namespace 隔离，不挂载宿主 home 目录。

### 常见 Terminal Backend 问题

如果 terminal 命令立刻失败，或 terminal 工具被报为禁用：

- **Local** —— 无特殊要求。上手时最安全的默认。
- **Docker** —— 运行 `docker version` 确认 Docker 正常。失败就修 Docker，或 `hermes config set terminal.backend local`。
- **SSH** —— `TERMINAL_SSH_HOST` 与 `TERMINAL_SSH_USER` 必须都设置。缺任何一个 Hermes 都会记一条清晰的错误。
- **Modal** —— 需要 `MODAL_TOKEN_ID` 环境变量或 `~/.modal.toml`。运行 `hermes doctor` 检查。
- **Daytona** —— 需要 `DAYTONA_API_KEY`。服务器 URL 配置由 Daytona SDK 处理。
- **Singularity** —— 需要 `singularity` 插件（`hermes plugins install singularity`），且 `$PATH` 里有 `apptainer` 或 `singularity`。HPC 集群上常见。

拿不准时，把 `terminal.backend` 改回 `local`，先确认命令在那里跑得通。

### 拆除时的远程到宿主状态同步

对 **SSH**、**Modal**、**Daytona** backend，Hermes 在会话期间把你的 `~/.hermes/` 状态（凭据文件、skill、缓存）推进远程沙箱，并在拆除时**把改动过的变化状态文件同步回**宿主原位。与最初推送内容不同的文件（按内容哈希比较）会被原样应用回去；已同步目录下的新远程文件（例如 agent 远程创建的 skill）会被映射回对应的宿主路径。仅上传的凭据文件绝不会在宿主上被覆盖。

- 回传同步最多带退避重试 3 次，并拒绝解压超过 2 GiB 的远程归档；状态树更大时在 `config.yaml` 里设 `terminal.sync_back_max_bytes`（字节）以提高上限。远程 `~/.hermes/` 下的活 socket（例如 `gateway.sock`）会被跳过，而不是让传输失败。
- 下载的归档先落到系统临时目录（`hermes-sync-back-<pid>-*`）；被硬杀进程留下的残留在下次回传同步时回收。
- Docker 与 Singularity 用 bind 挂载（活的宿主文件系统视图），不需要这套机制。
- 这里覆盖的是 Hermes 状态（`~/.hermes/`），**不包括**沙箱内任意的工作树文件——请在沙箱销毁前让 agent 把重要产物显式拷出来（例如 `scp`、`modal volume put`）。

### Docker 卷挂载

使用 Docker backend 时，`docker_volumes` 让你把宿主目录共享给容器。每项用标准 Docker `-v` 语法：`host_path:container_path[:options]`。

```yaml
terminal:
  backend: docker
  docker_volumes:
    - "/home/user/projects:/workspace/projects"   # Read-write (default)
    - "/home/user/datasets:/data:ro"              # Read-only
    - "/home/user/.hermes/cache/documents:/output" # Gateway-visible exports
```

这适用于：

- **给 agent 提供文件**（数据集、配置、参考代码）
- **从 agent 接收文件**（生成的代码、报告、导出物）
- **共享 workspace**——你和 agent 访问同一批文件

如果你在用消息 gateway、并希望 agent 用 `MEDIA:/...` 发送生成的文件，优先用一个宿主可见的专用导出挂载，例如 `/home/user/.hermes/cache/documents:/output`：

- 在 Docker 里把文件写到 `/output/...`
- 在 `MEDIA:` 里给出**宿主路径**，例如：`MEDIA:/home/user/.hermes/cache/documents/report.txt`
- 除非该精确路径对宿主上的 gateway 进程同样存在，否则**不要**输出 `/workspace/...` 或 `/output/...`

:::warning
YAML 的重复键会静默覆盖先前的键。如果你已经有 `docker_volumes:` 块，请把新挂载合并进同一个列表，而不是在文件后面再加一个 `docker_volumes:` 键。
:::

也可以用环境变量设置：`TERMINAL_DOCKER_VOLUMES='["/host:/container"]'`（JSON 数组）。

### Docker 凭据转发

默认情况下，Docker terminal 会话不继承任意宿主凭据。如果你需要容器内的某个特定 token，把它加进 `terminal.docker_forward_env`。

```yaml
terminal:
  backend: docker
  docker_forward_env:
    - "GITHUB_TOKEN"
    - "NPM_TOKEN"
```

Hermes 先从你当前的 shell 解析所列的每个变量，若它曾用 `hermes config set` 保存则回退到 `~/.hermes/.env`。

:::warning
`docker_forward_env` 里列出的任何东西对容器内运行的命令都可见。只转发你愿意暴露给 terminal 会话的凭据。
:::

### 以你的宿主用户运行容器

默认情况下 Docker 容器以 `root`（UID 0）运行。在 `/workspace` 或其他 bind 挂载里创建的文件在宿主上归 root 所有，所以会话之后你得先 `sudo chown` 才能用宿主编辑器改它们。在 Linux 上，Hermes 停止并移除一个 root 容器时，会先把它自己沙箱 bind 挂载（`TERMINAL_SANDBOX_DIR` 下的 `/root` 与 `/workspace`）里的文件交还给你的用户（不涉及你的 `docker_volumes` 或挂载的宿主目录；rootless Docker 与 userns-remap 下跳过）。这些沙箱文件无论属主是谁都会失去 setuid/setgid 位与文件 capability，这样容器留在那里的东西在宿主上执行时不会带着提权跑；一个从不被移除的长寿命容器，每当有会话脱离或重新附着它、以及在陈旧容器清扫移除它之前，都会做这次剥离（不改属主）。`terminal.docker_run_as_host_user` 标志对每个挂载、以及从不被移除的长寿命容器都解决这个问题：

```yaml
terminal:
  backend: docker
  docker_run_as_host_user: true   # default: false
```

启用后，Hermes 给 `docker run` 追加 `--user $(id -u):$(id -g)`，于是写进 bind 挂载目录（`/workspace`、`/root`、`docker_volumes` 里的任何路径）的文件归你的宿主用户所有，而不是 root。取舍是：容器再也不能 `apt install`，也写不了 `/root/.npm` 这类 root 属主路径——两者都要的话，请用 `HOME` 归非 root 用户所有的基础镜像（或在镜像构建时加上你需要的工具链）。

要向后兼容的行为就保持 `false`（默认）。当你的工作流主要是「编辑挂载的宿主文件」、受够了 `sudo chown -R` 时再打开。

### Snap 打包的 Docker（AppArmor）

在 Docker 以 snap 安装的主机上（Ubuntu 云镜像上常见，例如 Azure VM），snap 的 AppArmor 限制会拒绝沙箱的两个加固标志，容器启动即死：

```
exec /sbin/docker-init: operation not permitted     # --init
exec /usr/bin/sleep: operation not permitted        # --security-opt no-new-privileges
```

这是 snapd 的限制（[LP#1908448](https://bugs.launchpad.net/snapd/+bug/1908448)），不是 Hermes 能绕过的探测问题。要么改从 Docker 的 apt 仓库安装（推荐——所有加固都保留），要么选择加入：

```yaml
terminal:
  docker_snap_compat: true   # drops --init and no-new-privileges; cap-drop, tmpfs, PID limits stay
```

打开之后，沙箱里的僵尸进程不会被 init 回收，容器内的 setuid 二进制可能重新获得特权；容器启动时会记一条警告。

### 可选：把启动目录挂进 `/workspace`

Docker 沙箱默认保持隔离。除非你显式选择加入，Hermes **不会**把你的当前宿主工作目录传进容器。

在 `config.yaml` 里启用：

```yaml
terminal:
  backend: docker
  docker_mount_cwd_to_workspace: true
```

启用后：

- 如果你从 `~/projects/my-app` 启动 Hermes，该宿主目录会被 bind 挂到 `/workspace`
- Docker backend 在 `/workspace` 里启动
- 文件工具与 terminal 命令看到同一个挂载的项目

关闭时，除非你通过 `docker_volumes` 显式挂载了什么，`/workspace` 归沙箱所有。

安全取舍：

- `false` 保留沙箱边界
- `true` 让沙箱直接访问你启动 Hermes 的那个目录

只有当你有意让容器操作活的宿主文件时才选择加入。

`terminal.cwd` 里的宿主路径（例如 Windows 上的 `C:\Users\me\project`，或桌面/TUI 会话的 workspace）绝不会成为容器的工作目录：当它是挂载到 `/workspace` 的目录时，文件工具与 terminal 命令用 `/workspace`；否则容器保持自己的工作目录。如果文件工具仍然进不去它的工作目录，错误信息会点名当前 backend 下无效的 `terminal.cwd`，而不是 shell 原始的 `cd:` 行。

### 常驻 shell

**local** 与 **SSH** backend 上的每条 terminal 命令都在一个全新的 `bash` 进程里运行。Hermes 一次性捕获你登录 shell 的环境（PATH、profile 里的导出、函数、别名），第一条命令从那份快照开始。设置关闭时，每条命令都从它开始。设置打开时，每条命令把自己的导出变量留给下一条，而那份保存的副本只含导出变量，因此 profile 函数与别名在第一条命令之后就没了。

| 内容 | 设置开（默认） | 设置关 |
|------|----------------------|-------------|
| 工作目录（`cd ~/project`） | 延续 | 延续 |
| 导出的环境变量（`export FOO=bar`） | 延续 | 重置为登录环境 |
| 普通 shell 变量（`MY_VAR=hello`） | **不**延续 | 不延续 |
| 会话中途定义的函数 / 别名 | **不**延续 | 不延续 |
| 登录环境（PATH、profile 导出） | 始终在 | 始终在 |
| Profile 函数 / 别名 | 仅第一条命令 | 始终在 |

工作目录始终延续，因为文件工具按它解析相对路径。想让变量在任一模式下留住，就 `export` 它（设置开时），或放进你的 shell profile 或 `terminal.env_passthrough`。

SSH backend 读 `terminal.persistent_shell`；local backend 有自己的开关。两者默认都为开。要让每条命令都从登录环境开始：

```bash
hermes config set terminal.persistent_shell false   # SSH
export TERMINAL_LOCAL_PERSISTENT=false              # local
```

**优先级：**

| Backend | 变量 | 默认 |
|---------|----------|---------|
| SSH | `TERMINAL_SSH_PERSISTENT`，否则 `terminal.persistent_shell`（`TERMINAL_PERSISTENT_SHELL`） | `true` |
| Local | `TERMINAL_LOCAL_PERSISTENT` | `true` |

Docker、Modal、Daytona、Vercel Sandbox 与插件 backend（含 Singularity）忽略这些设置。

各 backend 的细节见 [Code Execution](features/code-execution.md) 与 [README 的 Terminal 章节](features/tools.md)。

## Skill 设置

Skill 可以通过 SKILL.md 的 frontmatter 声明自己的配置项。这些是非机密值（路径、偏好、领域设置），存放在 `config.yaml` 的 `skills.config` 命名空间下。

```yaml
skills:
  config:
    myplugin:
      path: ~/myplugin-data   # Example — each skill defines its own keys
```

**skill 设置如何工作：**

- `hermes config migrate` 扫描所有启用的 skill，找出未配置的设置，并提出逐项询问你
- `hermes config show` 在「Skill Settings」下展示所有 skill 设置及其所属 skill
- skill 加载时，其解析后的配置值会自动注入 skill 上下文

**手动设置值：**

```bash
hermes config set skills.config.myplugin.path ~/myplugin-data
```

在自己的 skill 里声明配置项的细节，见[创建 Skill — 配置项](../developer-guide/creating-skills.md#config-settings-configyaml)。

### 每个会话自动加载 skill

把 skill 钉住，让它们在每个新会话开始时、在所有界面上都被完整加载：

```yaml
skills:
  auto_load:
    - my-workflow
    - github-pr-workflow
```

在 system prompt 首次构建时每个会话解析一次（这样 prompt 保持缓存稳定；改动对下一个会话生效）。缺失或被禁用的 skill 会告警并跳过；`--ignore-rules` / `HERMES_IGNORE_RULES=1` 可抑制该列表。按 profile 划分。见 [CLI — 持久自动加载](./cli.md#persistent-auto-load-via-config)。

### 守卫 agent 创建的技能写入

当 agent 用 `skill_manage` 创建、编辑、patch 或删除 skill 时，Hermes 可以选择扫描新/更新内容里的危险关键词模式（凭据收割、明显的 prompt 注入、外窃指令）。该扫描器**默认关闭**——那些正当地碰 `~/.ssh/` 或提到 `$OPENAI_API_KEY` 的真实 agent 工作流太容易触发这个启发式了。如果你希望 agent 的技能写入落地之前扫描器先询问你，就重新打开：

```yaml
skills:
  guard_agent_created: true   # default: false
```

打开后，任何被标记的 `skill_manage` 写入都会以带扫描器理由的审批提示出现。批准的写入落地；拒绝的写入向 agent 返回一条解释性错误。

### 技能写入的审批

与上面的内容扫描器无关，`skills.write_approval` 把**每一次** agent 技能写入（create / edit / patch / delete / 辅助文件）都卡在你的显式批准之后——与危险命令同一套批准/拒绝机制：

```yaml
skills:
  write_approval: false   # false = write freely (default) | true = stage every write for review
```

打开后，技能写入会暂存到 `~/.hermes/pending/skills/` 下，用 `/skills pending`、`/skills diff <id>`、`/skills approve <id>`、`/skills reject <id>` 复核——CLI 或任何消息平台都行。运行时用 `/skills approval on|off` 切换。记忆有同一道门（`memory.write_approval`，见下文）。完整走查见[门控 agent 的技能写入](./features/skills.md#gating-agent-skill-writes-skillswrite_approval)。

## 记忆配置

```yaml
memory:
  memory_enabled: true
  user_profile_enabled: true
  memory_char_limit: 2200   # ~800 tokens
  user_char_limit: 1375     # ~500 tokens
  write_approval: false     # true = require approval before any memory write
```

设 `memory.write_approval: true` 后，记忆写入需要你批准才能落地：交互式 CLI 回合就地提示；消息会话与后台自我改进 review 则把写入暂存，等你用 `/memory pending` → `/memory approve <id>` / `/memory reject <id>` 复核。运行时用 `/memory approval on|off` 切换。见[控制记忆写入](./features/memory.md#controlling-memory-writes-write_approval)。

## 上下文文件截断

控制 Hermes 在做头/尾截断之前，从每个自动上下文文件加载多少内容。这作用于注入 system prompt 的文件，例如 `SOUL.md`、`.hermes.md`、`AGENTS.md`、`CLAUDE.md`、`.cursorrules`。它**不影响** `read_file` 工具。

```yaml
context_file_max_chars: null  # default — dynamic cap scaled to the model's context window (floor 20K, ceiling 500K chars)
```

设一个正整数可钉死固定上限，替代动态行为：

```yaml
context_file_max_chars: 25000
```

每次上下文文件读取还受 `context_file_read_timeout`（秒，默认 `5.0`）约束。读取耗时更久的文件——通常在 iCloud Drive、OneDrive、NFS 这类网络文件系统上——会被跳过并记一条警告，让 system prompt 的其余部分照常加载：

```yaml
context_file_read_timeout: 5.0
```

## 文件读取安全

控制单次 `read_file` 调用最多能返回多少内容。超过上限的读取会被拒绝，并给出让 agent 用 `offset` 与 `limit` 缩小范围的错误。这防止单次读取一个压缩过的 JS bundle 或大文件把上下文窗口灌满。

```yaml
file_read_max_chars: 100000  # default — ~25-35K tokens
```

如果你用的是大上下文窗口模型且经常读大文件，就调高；小上下文模型则调低以保持读取高效：

```yaml
# Large context model (200K+)
file_read_max_chars: 200000

# Small local model (16K context)
file_read_max_chars: 30000
```

Agent 还会自动对文件读取去重——同一文件区域被读两次且文件没变时，返回一个轻量存根而不是重发内容。上下文压缩会重置这份去重，于是 agent 可以在内容被摘要掉之后重新读文件。

## 工具输出截断上限

三个相关上限控制工具在 Hermes 截断之前最多返回多少原始输出：

```yaml
tool_output:
  max_bytes: 50000        # terminal output cap (chars)
  max_lines: 2000         # read_file pagination cap
  max_line_length: 2000   # per-line cap in read_file's line-numbered view
```

- **`max_bytes`** —— 当 `terminal` 命令产出的 stdout/stderr 合计超过这个字符数时，Hermes 保留前 40% 与后 60%，中间插入一条 `[OUTPUT TRUNCATED]` 提示。默认 `50000`（在常见分词器上约 1.2–1.5 万 token）。
- **`max_lines`** —— 单次 `read_file` 调用 `limit` 参数的上限。超过的请求会被夹取，单次读取就灌不满上下文窗口。默认 `2000`。
- **`max_line_length`** —— `read_file` 输出带行号视图时的单行上限。超过该长度的行被截断到该字符数，后接 `... [truncated]`。默认 `2000`。

大上下文窗口、每次调用承受得起更多原始输出的模型就调高；小上下文模型则调低以保持工具结果紧凑：

```yaml
# Large context model (200K+)
tool_output:
  max_bytes: 150000
  max_lines: 5000

# Small local model (16K context)
tool_output:
  max_bytes: 20000
  max_lines: 500
```

### 工具结果溢出预算

与截断分开，超大的工具*结果*会被溢出到磁盘而不是切掉：完整输出存到 `$HERMES_HOME/cache/spillover/` 下，上下文里的内容换成一段预览加已存文件的路径（可用 `read_file` 配 `offset`/`limit` 阅读，或用 `execute_code` 处理）。通用的按结果溢出阈值是 100,000 字符，对小上下文模型会自动下调。只要还有某个会话的记录指向它，溢出文件就保留，并随该会话在被删除或清理时一起离开；gateway 的每小时家务与每个进程的首次溢出只清扫早于会话保留窗口（`sessions.retention_days`，默认 90 天，且不少于 24 小时）且无人引用的文件，因此之后恢复的会话仍能找到其记录指向的东西。

MCP 工具结果（名为 `mcp_*` 的工具）以更紧的 **50,000 字符**默认值溢出：MCP server 常常返回大块不分页的载荷（工具发现目录、批量执行），否则会落在通用阈值之下、并在之后每个回合里撑大上下文。什么都不会丢——完整结果保留在磁盘上。覆盖该阈值：

```yaml
tool_budget:
  mcp_result_size_chars: 50000   # per-result spillover threshold for mcp_* tools
```

MCP 阈值始终被夹在通用按结果阈值（可能随上下文伸缩）之内，所以调高它也不会超过活动模型窗口所允许的量。

Hermes 还会标出**提供方侧的省略**：当 MCP 或 web 工具结果自带截断标记（`...N more items`、`"has_more": true`、「saved to sandbox」之类说明）时，结果后会追加一行提示，警告可见数据不完整，在把任何枚举当作完整之前应先分页/抓取。

## 全局工具集禁用

要在一处同时对 CLI 与每个 gateway 平台压制特定工具集，就在 `agent.disabled_toolsets` 下列出它们的名字：

```yaml
agent:
  disabled_toolsets:
    - memory       # hide memory tools + MEMORY_GUIDANCE injection
    - web          # no web_search / web_extract anywhere
```

这在各平台工具配置（`hermes tools` 写入的 `platform_toolsets`）**之后**应用，所以列在这里的工具集总是被移除——即使某平台保存的配置仍列着它。当你想要一个「到处关掉 X」的总开关，而不想在 `hermes tools` 界面里改 15 多行平台配置时，用它。

移除是按工具进行的，所以列出的工具集也会把它的工具从任何共享这些工具的已启用工具集中拿走：`search`（只有 `web_search`）会从已启用的 `web` 里剥掉 `web_search`。`hermes tools list` 与 `hermes doctor` 会标出因这种方式失去工具的已启用工具集；在 `hermes tools`（复选清单、`hermes tools enable`、Desktop 或 dashboard）里启用某个工具集时，会清掉这里所有被已启用工具集完全覆盖的条目。

列表留空或省略该键都是空操作。

## Git worktree 隔离

启用隔离的 git worktree，以便在同一仓库上并行跑多个 agent：

```yaml
worktree: true    # Always create a worktree (same as hermes -w)
# worktree: false # Default — only when -w flag is passed
```

启用后，每个 CLI 会话在 `.worktrees/` 下创建一个带自己分支的新 worktree。Agent 可以编辑文件、提交、推送、开 PR，而互不干扰。干净的 worktree 在退出时移除；脏的保留下来供手工恢复。

默认情况下新 worktree 从**刚抓取的远端最新提交**分支（当前分支的上游，否则是远端的默认分支），这样它从项目最新状态开始，而不是从本地克隆可能过期的 `HEAD`。这让 PR 的 diff 只覆盖实际改动，而不会继承本地克隆落后的那些差异。设 `worktree_sync: false` 可改为从本地 `HEAD` 分支——离线时有用，或当你有意以克隆的当前精确状态为基底时。远端不可达时会自动回退到本地 `HEAD`。

```yaml
worktree_sync: true    # Default — branch from the fetched remote tip
# worktree_sync: false # Branch from local HEAD (offline / pinned base)
```

也可以在仓库根的 `.worktreeinclude` 里列出要拷进 worktree 的 gitignore 文件：

```
# .worktreeinclude
.env
.venv/
node_modules/
```

## 上下文压缩

Hermes 会自动压缩长对话，使其保持在模型的上下文窗口内。压缩摘要是一次独立的 LLM 调用——你可以指向任意 provider 或端点。

所有压缩设置都在 `config.yaml` 里（没有环境变量）。

### 完整参考

```yaml
compression:
  enabled: true                                     # Toggle compression on/off
  progress_notices: false                           # Opt-in: deliver routine compression progress notices to chat platforms — see below
  threshold: 0.50                                   # Compress at this % of context limit
  threshold_tokens: null                            # Absolute token cap (optional) — takes lower of ratio vs absolute
  target_ratio: 0.20                                # Fraction of threshold to preserve as recent tail
  tail_mode: lean                                   # Tail retention: "lean" (default — clamped 2.5% tail, 10K-25K, never above 20% of the window, with a detailed session log + anchor index + session_search recovery pointers in the summary, all from ONE auxiliary summarizer call; ~3x fewer retained tokens after compaction) or "legacy" (0.20×threshold verbatim tail)
  protect_last_n: 20                                # Min recent messages to keep uncompressed
  protect_first_n: 3                                # Non-system head messages pinned across compactions (0 = pin nothing)
  in_place: true                                    # Compact on the same session id (no rotation) — see below
  idle_compact_after_seconds: 0                     # Opt-in idle compaction (0 = disabled) — see below
  prepare_ahead: false                              # Opt-in: prepare the next summary in the background — see below
  hygiene_hard_message_limit: 5000                  # Gateway safety valve — see below
  hygiene_timeout_seconds: 30                       # Max seconds of NO summary-model output before hygiene compression is cut off
  hygiene_total_ceiling_seconds: 600                # Absolute cap on the hygiene wait even while tokens are still streaming
  hygiene_max_turn_hold_seconds: 10                 # Max wall-clock the incoming turn waits on hygiene compression before proceeding uncompressed — see below
  hygiene_failure_cooldown_seconds: 300             # First rung of the per-session hygiene-failure backoff (x1/x3/x9, capped at 1h)
  context_timeout_seconds: 120                      # Inactivity budget for in-agent compress_context (loop / compress / preflight) — see below
  context_total_ceiling_seconds: 600                # Absolute cap on the *pre-commit* in-agent compress_context wait even while tokens are still streaming (an already-started SessionDB commit is never abandoned; overruns are logged + surfaced)
  proactive_prune_tokens: 0                         # Opt-in tokens trigger for the no-LLM tool-result prune (0 = off; see below)
  proactive_prune_min_result_chars: 8000            # Prune's summarize pass only touches tool results larger than this (clamped >= 200)
  proactive_prune_min_reclaim_tokens: 4096          # Prune only commits when it reclaims at least this many tokens (0 = commit any)

# The summarization model/provider is configured under auxiliary:
auxiliary:
  compression:
    model: ""                                       # Empty = use main chat model. Override with e.g. "google/gemini-3-flash-preview" for cheaper/faster compression.
    provider: "auto"                                # Provider: "auto", "openrouter", "nous", "codex", "main", etc.
    base_url: null                                  # Custom OpenAI-compatible endpoint (overrides provider)
```

:::info 遗留配置迁移
带 `compression.summary_model`、`compression.summary_provider`、`compression.summary_base_url` 的旧配置会在首次加载时（配置版本 17）自动迁移到 `auxiliary.compression.*`。无需手动操作。
:::

`progress_notices`（默认 `false`）控制**常规**压缩进度状态是否到达聊天平台（Telegram、Discord、Slack 等）。按设计，自动压缩在聊天界面上是静默的——它在后台运行，只有服务端日志。设 `progress_notices: true` 即可选择在聊天平台上看到常规生命周期：「Compacting context…」开始提示、preflight/预 API 压缩触发、空闲压缩、重试进度（「Compressed 30 → 12 messages, retrying…」），以及「Context compaction complete」提示。这道门只针对压缩状态——无关的运行噪音（辅助模型失败、provider 限流/重试唠叨）无论怎么设都保持抑制。压缩**失败**提示与手动 `/compress` 的反馈始终可见，不受该设置影响。在运行中的 gateway 上编辑该值，下一条消息生效。

`hygiene_hard_message_limit` 是一个仅限 gateway 的**压缩前安全阀**。它用来打破一个死亡螺旋：当 API 调用在一个超大会话上不断断开时，gateway 根本收不到 token 用量数据，于是基于 token 的阈值无法触发，记录继续增长、断连愈发严重。这个按计数的下限只凭消息数触发（无论 API 是否失败，这个数总是已知的），强制压缩以恢复会话。默认 `5000`——远高于任何正常会话，包括做几千个短回合的大上下文（100 万+）模型，它们早在触及此数之前就按 token 阈值压缩了。平台异常就再调高，想更激进地压缩就调低。在运行中的 gateway 上编辑该值，下一条消息生效（见下）。

同一个上限还是**发送给模型内容的失败关闭边界**：当回合开始时 hygiene 尚未落地——回合等待预算已过期、摘要超时或失败、失败冷却生效、另一次压缩仍在进行、或压缩被禁用。此时 gateway 保留开头的 system/设置行加最新消息，总数至多 `hygiene_hard_message_limit`，且绝不让保留的尾巴从一个孤立的工具结果开始。只有那一个回合的载荷被裁剪：磁盘上的记录原样不动，什么都不删，稍后落地的摘要会被照常采纳。正是这一点，让一次长达一周的私聊在压缩反复落空时，不会把完整未压缩的历史喂给模型。

`hygiene_timeout_seconds` 是 gateway 给这次 agent 前压缩的**不活跃预算**——不是总墙钟上限。压缩摘要调用是从模型流式返回的，每个到达的 token 都算前进：一个仍在生成的慢推理模型会不断延长自己的期限，所以慢但健康的摘要模型绝不会在生成中途被切断。只有当摘要模型连续这么多秒**没有任何输出**（后端挂了、连接卡住、provider 沉默）时，gateway 才会警告用户、不压缩就继续处理进来的消息，并记一个临时的按会话失败冷却，而不是看起来卡死。

`hygiene_total_ceiling_seconds`（默认 `600`）在 token 仍在流动时也约束总等待，于是一条退化的涓流无法无限期扣住一个回合。它被夹到至少 `hygiene_timeout_seconds`。llama.cpp 服务器读 prompt 花的时间不计入（见 `context_total_ceiling_seconds`）。

`hygiene_max_turn_hold_seconds`（默认 `10`）是 gateway 的**回合等待预算**——进来的消息为等 hygiene 压缩最多被扣多久，超过就不再等、按未压缩的记录继续。它之所以存在，是因为单靠 `hygiene_total_ceiling_seconds` 可能让线路静默远超聊天传输的空闲超时：一个持续吐 token 的摘要模型会不断重置不活跃切片，于是没有回合等待预算的话，等待可能一路逼近上限而用户一个字节都收不到——Telegram（及类似传输）随后断开连接，回合看起来冻结了。把回合等待夹在这个预算内（远低于典型的约 30 秒传输空闲超时），保证消息被及时答复。

**预算耗尽时压缩并没有丢**：worker 会继续在分离状态下运行，而且——当它的提交被水位 fence 住时（有 session DB 时的常态）——它保住提交准入，于是完成的摘要在下一个安全边界被采纳，等待放弃之后追加的回合会作为并发尾巴逐字存活。这对**思考/推理型摘要模型**（DeepSeek、QwQ 等）尤其重要，它们光推理阶段就可能超过预算：其摘要只是晚一个回合落地，而不是永远不落地。如果提交无法被安全 fence，迟到的结果会被丢弃（`CompressionCommitFence`），它不能覆盖更新的回合。如果你更希望压缩在同一回合内生效、且你的传输承受得起等待，就调高该预算；在很慢的后端上要更快恢复就调低。

`hygiene_failure_cooldown_seconds` 控制 hygiene 原缩超时或中止之后那个按会话的冷却。冷却期间，gateway 对同一个超大会话跳过重复的 hygiene 尝试，这样每条进来的消息不会都堵在同一个坏掉的辅助后端上。`/compress`、`/reset` 或之后某个健康的回合仍能恢复会话。

这个值是升级阶梯的**第一级**，不是固定间隔：同一会话连续失败会等 `1x`、`3x`、然后 `9x` 这个值，上限一小时。摘要模型永久损坏的会话因此会退避，而不是按固定间隔永远重试；一次真正缩小了记录的运行会把它重置回第一级。升级按会话且进程内有效——gateway 重启会把它重置回第一级，而冷却截止时间本身仍然存活。

`context_timeout_seconds`（默认 `120`）是 agent 内 `compress_context` 的同一类**不活跃预算**——对话循环、preflight 压缩与手动 `/compress`——这样卡死的摘要模型不会无限期拖住会话。流式到达的摘要 token 会延长等待；只有完全沉默的 worker 才被切断。该预算以辅助压缩请求自身的超时（`auxiliary.compression.timeout`，最低 300 秒）为下限，因此宿主绝不会在请求本身放弃之前先放弃一个沉默的摘要器——一个在首个 token 之前思考的推理摘要器，或一条无法流式的路由，都会拿到 provider 调用同等的预算。超时时 Hermes 会用 `auxiliary.compression.fallback_chain` 的第一个条目重试一次摘要（若该条目声明了自己的 `timeout` 就用它）——一条卡死的路由从不抛异常，所以辅助客户端自己的 fallback 处理看不到它。如果那次也失败，或没配 fallback 链，接下来发生什么取决于该请求是否还塞得进模型上下文窗口：塞得进的请求本回合按未压缩发送（摘要失败冷却让重试不至于每回合重复）；塞不进的请求根本发不出去，于是 Hermes 提交它的确定性兜底摘要（裁掉旧工具结果、用静态交接替代被摘要的中段）来结束回合——用「压缩超时」的恢复结果结束回合（在消息 gateway 上还会自动重置会话）是最后手段，只有连确定性流程都缩小不了记录时才会走到。设为 `0` 可禁用。一次 preflight 在请求仍超出窗口时没能回收任何东西，会立即以「开新会话（`/new`）」的指引结束回合，而不是发送一个模型收不了的请求。Gateway 会话 hygiene 有它自己的 `hygiene_timeout_seconds` 路径，不会被二次包裹。

`context_total_ceiling_seconds`（默认 `600`）在 token 仍在流动时也约束 agent 内的**提交前**等待（摘要/流式阶段）。它被夹到至少 `context_timeout_seconds`。llama.cpp 服务器读 prompt 的时间不计入：在笔记本 GPU 上，光读一段 15 万 token 的对话就可能超过该上限。服务器把阅读上报为进度，每次上报新读到的 token 都把期限按阅读时间往后推；一个不上报任何阅读的服务器拿不到额外时间，两次上报之间仍适用空闲超时。

对已经超出模型上下文窗口的请求，提交前等待改由一份 `context_timeout_seconds` 预算约束，而不是这个上限：这种请求反正发不出未压缩版本，而一个持续流式却不回收任何东西的摘要会在每个回合把会话（以及 Desktop UI）占满整个上限——届时由确定性兜底摘要完成压缩。如果你的摘要器确实需要更久，调高 `context_timeout_seconds`。确切保证是：**摘要阶段受该上限约束；提交阶段若超限会被记录并上报。** 一旦 worker 进入压缩提交 fence、SessionDB 变更已在进行，提交绝不会中途放弃——那会有记录分叉的风险——但等待不再是静默的：提交若跑过上限，Hermes 会记录这次超限（WARNING，重复时升级为 ERROR），经用户可见的警告通道发一条一次性警告，并按有界的增量继续等待直到提交完成。

摘要阶段到达上限时，摘要模型的流会在同一瞬间在每条辅助线路（chat.completions、Codex Responses、Anthropic Messages）上关闭——一个被放弃的摘要不会在没人等待的连接上计费到完成，其会话租约被释放给下一次尝试。

`protect_first_n` 控制多少条**非 system** 的开头消息在每次压缩中都被钉住。默认 `3`——开头的用户/助手交换在每次摘要流程中都存活，原始目标始终可见。在开头回合已不相关的长跑滚动压缩会话上，设 `protect_first_n: 0`，只钉 system prompt + 摘要 + 尾巴。无论该设置如何，system prompt 本身始终保留。

`in_place`（默认 `true`）控制压缩触发时会话身份如何变化。为 `true` 时，压缩重写消息列表并重建 system prompt，**不轮换 session id**——整段对话一生只有一个持久 id（没有 `parent_session_id` 链，会话列表里没有 `name #2` / `#3` 重新编号）。压缩是非破坏性的：活的上下文被压缩，但压缩前的回合在同一 id 下软归档（标记为非活动/已压缩）——仍可经 `session_search` 搜索并可恢复，而不是被删除。Hook 通过 `session:compress` 事件上的 `in_place` 字段看到该模式。设 `in_place: false` 恢复遗留行为，每次压缩都轮换到一个与旧会话相连的新 session id。

`threshold_tokens` 为压缩触发设置一个可选的**绝对 token 上限**。设置后，压缩在按比例的 `threshold` 与该绝对数之间取较小者触发，因此无论活动模型是谁，压缩都不会晚于该 token 数才发生。当你想给每次调用一个固定成本上限时用它，例如 `threshold_tokens: 256000`，让 100 万窗口的模型在 256K 而不是 500K 时压缩。该上限被夹到模型上下文长度，所以超过窗口的值是空操作。默认 `null`（禁用——只用按比例的阈值）。该上限在模型切换与 fallback 激活后仍然有效。

`idle_compact_after_seconds` 是一个**可选的、基于时间**的触发器，与基于规模的 `threshold` 互补。默认 `0`（禁用）。设为大于 0 后，一个会话在至少这么多秒的不活动之后恢复时，会在第一次回复之前先把累积历史压缩掉——于是一个长寿命的话题（例如几小时后才回来的 Telegram 对话）不会在之后每个回合都重读整段过期上下文。当上下文已经处于或低于压缩后目标（`threshold × target_ratio`）时它从不触发，并与所有自动压缩一样遵守同样的失败冷却、防抖与按会话锁守卫。示例：`idle_compact_after_seconds: 1800` 在空闲 30 分钟后压缩。

`prepare_ahead`（默认 `false`）在会话接近触发点时，趁工具运行与回合间隙在后台写下一次压缩摘要。每次压缩准备一份摘要。当自动压缩触发、且被摘要的消息仍是同一批消息时（插件的文本编辑没问题；消息被丢弃或回退则不行），会采用这份准备好的摘要，而不是在那一刻再调一次摘要；比它更新的每条消息都留在它之外、处于未压缩的尾部。如果触发时准备中的摘要还没写完，压缩会等它（在通常的压缩时限内）而不是重写。没有准备好的摘要或它已不匹配时，压缩与不开该选项时完全一致。它会花掉一次可能用不上的辅助摘要调用，且不适用于手动 `/compress`、插件 context engine 或原生/app-server 压缩。对会给压缩摘要追加上下文的 memory provider，它会在第一次压缩后自我关闭，因为每份准备好的摘要都会被丢弃。

`proactive_prune_tokens` 启用一个确定性的、不调 LLM 的旧工具结果载荷裁剪，独立于 `threshold` 运行。在大窗口模型上，`threshold` 压缩（约窗口的 50%）很少触发，于是大块工具输出（terminal 转储、文件读取、网页提取）一路跟着历史、在之后每个回合被重发。当重发历史超过 `proactive_prune_tokens`（默认 `0` = 关；试 `48000` 启用）时，裁剪会对相同结果去重并摘要更旧的超大工具结果，保护最近的 `protect_last_n` 条消息，且从不调用模型。工具调用参数是执行记录，绝不会被裁剪改写；摘要模型对放进其 prompt 的副本有一个独立的有界序列化器。压力流程同样只降级工具结果正文。在完整语义压缩期间，携带的头/尾行保留这些工具结果降级（于是超大的尾巴仍能压缩），而工具调用参数保持逐字节一致。可选的主动裁剪仍会提交符合条件的工具结果正文降级，因此 `proactive_prune_min_reclaim_tokens`（默认 `4096`）让这些破坏缓存的提交保持偶发；`proactive_prune_min_result_chars`（默认 `8000`，夹到 ≥ 200）设定低于该尺寸的工具结果不动。这只在内置 `compressor` 引擎下运行；其他 context engine 继承一个空操作。

:::tip Gateway 对压缩与上下文长度的热重载
近期版本起，在运行中的 gateway 上编辑 `config.yaml` 里的 `model.context_length` 或任何 `compression.*` 键，下一条消息即生效——无需重启 gateway、无需 `/reset`、无需轮换会话。缓存的 agent 签名包含这些键，所以 gateway 一旦看到变化就透明地重建 agent。API key 与工具/skill 配置仍需走常规重载路径。
:::

### 常见设置

**默认（自动探测）——无需配置：**

```yaml
compression:
  enabled: true
  threshold: 0.50
```

使用你的主 provider 与主模型。想让压缩跑在比主聊天模型更便宜的模型上，就按任务覆盖（例如 `auxiliary.compression.provider: openrouter` + `model: google/gemini-2.5-flash`）。

**强制指定 provider**（基于 OAuth 或 API key）：

```yaml
auxiliary:
  compression:
    provider: nous
    model: gemini-3-flash
```

适用于任意 provider：`nous`、`openrouter`、`codex`、`anthropic`、`main` 等。

**自定义端点**（自托管、Ollama、zai、DeepSeek 等）：

```yaml
auxiliary:
  compression:
    model: glm-4.7
    base_url: https://api.z.ai/api/coding/paas/v4
```

指向一个自定义 OpenAI 兼容端点，用 `OPENAI_API_KEY` 做认证。

### 三个旋钮如何互动

| `auxiliary.compression.provider` | `auxiliary.compression.base_url` | 结果 |
|---------------------|---------------------|--------|
| `auto`（默认） | 未设置 | 自动探测最佳可用 provider |
| `nous` / `openrouter` 等 | 未设置 | 强制该 provider，用它的认证 |
| 任意 | 已设置 | 直接使用自定义端点（provider 被忽略） |

### 流式进度超时

摘要流式返回时（压缩在 chat-completions 与 Responses 路由上总是流式的，例如 `openai-codex` 或自定义 OpenAI 兼容端点），有两个超时生效，且彼此独立：

- `auxiliary.compression.timeout` —— 整体请求预算（默认 120 秒）。
- `auxiliary.compression.no_progress_timeout` —— 流最多可以多久没有**实质性**事件（文本/推理增量，或一个已完成的输出项），超过就中止该次尝试（`... stream stalled: no new output for Ns`），交给正常的重试/fallback 链。未设置时默认 **60 秒**。在 chat-completions 流上，该窗口从第一个 token 起算。在此之前，远程端点享有主循环的陈旧耐心（设置了的话用 provider 的 `providers.<id>.stale_timeout_seconds`，否则 180 秒，大 prompt 会提高，对 o3 或 DeepSeek R1 这类推理模型提高到 600 秒；以 `timeout` 为上限），所以一个默默思考的模型不会被切。在本地端点（localhost、局域网、Tailscale）上，静默 prefill 只受 `timeout` 约束。同一条规则适用于每个流式辅助任务，包括 MoA 参考调用。保活与生命周期帧（`response.in_progress`、ping）不算进度；每个实质性事件都会重新武装该窗口，所以一个慢但在推进的摘要绝不会被它切断。

只调高 `timeout` **不会**放宽进度窗口——配置成 600 秒的请求在 60 秒空档后仍会中止。要改这个空档请设 `no_progress_timeout`；有效窗口以 `timeout` 为上限，宿主的硬期限/取消仍然优先。宿主自己的不活跃预算是这里的外层上限：agent 内压缩在 `compression.context_timeout_seconds`（默认 120 秒，以生效的 `auxiliary.compression.timeout` 为下限，而后者至少 300 秒）后放弃一个沉默的摘要器，gateway hygiene 则在 `compression.hygiene_timeout_seconds`（默认 30 秒）后放弃，所以一个大于宿主预算的 `no_progress_timeout` 会被宿主静默截断。该键按任务设置（`auxiliary.<task>.no_progress_timeout`），所以为压缩放宽它不会改变其他辅助任务。非正数的值会被忽略并在日志里记一条警告，适用 60 秒默认值。

```yaml
auxiliary:
  compression:
    provider: openai-codex
    timeout: 600
    no_progress_timeout: 180   # tolerate a 3-minute silent gap on a long reasoning summary
```

:::warning 摘要模型的上下文长度要求
摘要模型的上下文窗口**必须**至少与你的主 agent 模型一样大。压缩器会把对话完整的中段发给摘要模型——如果那个模型的窗口比主模型小，摘要调用会以 context length 错误失败。发生时，中段回合会**不带摘要直接丢弃**，对话上下文被静默丢失。如果你覆盖了模型，请核对其上下文长度达到或超过主模型。
:::

## Gateway 回合租约超时

Gateway 按解析后的 session ID 串行化回合，这样两个路由键不会并发加载并写同一份记录。把最长租约等待与普通的 agent 不活动超时分开配置：

```yaml
agent:
  gateway_turn_lease_timeout: 5
```

如果这个预算耗尽时另一个回合仍持有会话租约，Hermes 会失败关闭：它不加载记录，也不为等待中的消息运行模型。用户收到一条拒绝提示，必须重发。Hermes 不会自动把消息重新入队，因为在没有持久化顺序与幂等的情况下那样做可能把消息处理两次。非正数值使用 5 秒默认。

## Gateway 重启 drain

Gateway 停止或重启时（SIGTERM、`hermes update`、`hermes gateway stop`，或 `hermes gateway restart` / `/restart` 的最后阶段），`agent.restart_drain_timeout` 决定它在打断在途聊天回合之前再让它们跑多少秒：

```yaml
agent:
  restart_drain_timeout: 0          # default: interrupt in-flight chat turns at once
  cron_drain_timeout: 30            # floor for cron jobs and api_server (/v1) runs
  restart_after_turn_timeout: 1800  # /restart and `gateway restart`: wait for turns BEFORE stopping
```

默认 `0` 时，重启立即打断正在跑的回合。该回合以「被打断」落定，绝不再次运行；TUI 与 Desktop 会在该回合上显示「Gateway restarting」（或「Gateway shutting down」）提示，等 Hermes 重连后你再发一次消息。排在它后面的消息会保留，并在新 gateway 上按顺序运行。

如果你更想让回合跑完，就设正值：

```yaml
agent:
  restart_drain_timeout: 60
```

更长的 drain 会让每次重启与更新都最多等这么久。`HERMES_RESTART_DRAIN_TIMEOUT` 覆盖配置值。

:::caution systemd 的 `TimeoutStopSec`
生成的 systemd unit 会按该值推算 `TimeoutStopSec`：取 `restart_drain_timeout` 与 `cron_drain_timeout` + 10 秒的较大者，再加 30 秒余量，且至少 60 秒（`gateway/restart.py`、`resolve_systemd_timeout_stop_sec`）。如果你调高了 `restart_drain_timeout`，请重新运行 `hermes gateway install` 让 unit 拿到新预算，否则 systemd 会在 drain 中途 SIGKILL 掉 gateway。launchd 把其停止超时上限定为 60 秒，所以在 macOS 上 drain 受限于装得下这个数的部分。
:::

## 会话停滞看门狗

Gateway 跑一个只通知的停滞看门狗（`agent.session_stall_timeout`，默认 `300` 秒，`0` = 禁用）。当一个忙碌会话有**待处理的入站后续消息**、且 agent 的共享活动时钟已至少这么久没有动静时，gateway 记一条 WARNING 并给用户发一条一次性通知：

```
⚠️ Agent session appears stalled (last activity N min ago). Try /new to reset.
```

语义：

- **只通知。** 看门狗从不杀掉回合——对比 `agent.gateway_timeout`，后者在长时间不活动后取消一次运行。停滞提示只是告诉你 agent 看起来卡住了，由你决定（`/stop`、`/new`，或继续等）。
- **每次停滞事件一条通知。** 待处理入站被排空或活动恢复时闩锁清除，所以一个恢复后再次停滞的会话会再次通知。
- 进度只来自共享活动快照（工具调用、API 流进度、压缩心跳）。待处理入站是通知闸门，不是进度时钟。

```yaml
agent:
  session_stall_timeout: 300   # seconds; 0 disables the watchdog
```

## 重连注意力升级

当某个平台 adapter 连不上（网络故障、bot token 被吊销、sidecar 损坏），gateway 会用带上限的指数退避无限重试——重试永不停止，所以瞬时故障总能自愈、无需运维介入。缺点是*永久*故障（被吊销的 Telegram token、缺失的 Discord privileged intents）看起来与一次抖动一模一样：「重试中」，永远。

两个机制让永久故障可见：

- **终局分类。** 异常*类型*证明其永远无法自愈的失败——被拒绝/吊销的 token（`telegram_auth_error`、`discord_auth_error`、`email_auth_error`）、缺失的 privileged intents（`discord_intents_required`）、依赖装不上的 Photon sidecar（`SIDECAR_DEPS_MISSING`）或 node 二进制缺失（`SIDECAR_NODE_MISSING`）——会被标为 fatal 而不是进入重试队列。分类严格基于类型；模糊的错误永远继续重试。
- **需要关注的升级。** 某平台在重试队列里连续超过 `agent.reconnect_attention_after`（默认 `7200` 秒 = 2 小时，`0` 禁用）后，会在 gateway 运行时状态（`hermes status`）里拿到 `needs_attention: true` 与一个 `retrying_since` 时间戳，外加一条 WARNING 日志。重试照旧继续——这是信号，不是熔断。成功重连后该标志清除。

```yaml
agent:
  reconnect_attention_after: 7200   # seconds; 0 disables the escalation flag
```

## Gateway agent 缓存

Gateway 为每个会话保留一个 agent，让对话复用其缓存的 prompt 前缀，而不是每回合重建 system prompt。那个缓存的 agent 还持有该会话的完整记录——含工具输出，在有上百次工具调用的会话上是几十 MB。于是在繁忙的多平台 gateway 上，这个缓存是进程里最大的单一内存消耗者。

```yaml
agent:
  agent_cache:
    max_size: 128            # LRU entry cap
    idle_ttl_secs: 3600      # evict an agent idle this long
    memory_high_mb: auto     # anon-RSS budget; number, "auto", or 0/off
    max_evictions_per_pass: 16
    protect_recent: 8
```

`max_size` 与 `idle_ttl_secs` 按条数和时间约束缓存。两者都不知道它占了多少字节，所以 `memory_high_mb` 加了第三重约束：匿名内存一旦越过预算，就丢弃最久未使用的记录，它们在下一回合从存储的会话重新加载。Gateway 与其他服务争内存时就调低；如果你想让每个前缀都保持温热，就调高（或设 `0` 关掉这一轮）。

`auto` 从 gateway 实际运行所受的内存限制推导预算——容器或 systemd unit 的 cgroup 限制，否则是总内存——于是 unit 上的 `MemoryMax`/`MemoryHigh` 会被尊重，不必再维护一个要同步的数字。在这种限制之下，测量范围也按同样方式划定：cgroup 自己的匿名计费（`memory.stat` 的 `anon`），其中包含 `execute_code` 内核与 terminal 命令这类计入该 unit 限额的子进程。没有上限时，测的是 gateway 自己的匿名 RSS。

正在回合中的会话、`protect_recent` 个最近使用的会话、以及记录尚未写完盘的会话，永远不会被丢弃。逐出会以 WARNING 记录测得的 RSS 与被丢的会话：

```
Agent cache pressure: anon RSS 6802MB over budget 6656MB — evicting 5 LRU session(s): ...
```

## Context Engine

Context engine 控制接近模型 token 上限时对话如何管理。内置的 `compressor` 引擎使用有损摘要（见[上下文压缩](../developer-guide/context-compression-and-caching.md)）。插件引擎可以用别的策略替代它。

```yaml
context:
  engine: "compressor"    # default — built-in lossy summarization
```

要用插件引擎（例如用于无损上下文管理的 LCM）：

```yaml
context:
  engine: "lcm"          # must match the plugin's name
```

插件引擎**从不自动激活**——你必须显式把 `context.engine` 设为插件名。可用引擎可在 `hermes plugins` → Provider Plugins → Context Engine 里浏览选择。

记忆插件的类似单选系统见 [Memory Providers](./features/memory-providers.md)。

## 迭代预算

Agent 在做工具调用很多的复杂任务时，可能烧光它的迭代预算（默认 500 个回合）。Hermes **不会**注入任务中途的压力告警——更早的构建在预算用到 70%/90% 时警告模型，那会导致模型过早放弃复杂任务，已于 2026 年 4 月移除。

取而代之的是：当预算真的耗尽（500/500）时，Hermes 注入一条让模型收尾的消息，并允许一次**宽限调用**，让它交出最终响应。如果那次宽限调用仍不产出文本，就要求 agent 总结它完成了什么。

```yaml
agent:
  max_turns: none              # Iterations per conversation turn (default: none = unlimited)
                               # Set a positive integer to cap; "none"/"null"/
                               # "unlimited"/"inf"/"infinity"/"infinite"/0/-1 = no limit
  budget_warning_ratio: null   # Optional one-time checkpoint warning, e.g. 0.75
  api_max_retries: 3           # Retries per provider before fallback engages (default: 3)
  auto_recovery_cycles: 5      # Wait-and-retry cycles after retries + fallback are spent on an outage (0 = off)
```

`agent.max_turns` **默认无上限**——回合上限带来的问题比它解决的还多（任务中途被静默截断），所以开箱状态下 Hermes 会把一个对话回合跑到完成。要施加上限就设正整数。要明确表达「无限制」，以下任意大小写不敏感写法都行：`"none"`、`"null"`、`"unlimited"`、`"infinite"`、`"infinity"`、`"inf"`、`0`、`-1`（它们解析成一个 `sys.maxsize` 哨兵，于是循环绝不会因回合数退出）。

普通与委派对话的 `agent.budget_warning_ratio` 默认关闭。当它被设为严格介于 `0` 与 `1` 之间的值、且 `max_turns` 有限时，Hermes 会在阈值到达后往最新的工具结果追加一条模型可见的检查点提示。该提示每个对话回合重新武装，并使用各 agent 自己的迭代预算。它只追加到当前工具结果的尾部，绝不追加到更早的回合，也不添加合成的用户/system 消息，也不改动既有的耗尽宽限调用。由 dispatcher 持有的 Kanban worker 默认在 90% 时收到完成检查点（显式比例会改这个阈值），此时它们的工具仍可用。检查点要求的是「已验证的完成」或一条持久的进度注释，而不是过早的成功。

`agent.api_max_retries` 控制 Hermes 在**切换到 fallback provider 之前**对一次瞬时错误（限流、连接断开、5xx）重试 provider API 调用多少次。默认是 `3`——总共四次尝试。如果你配了 [fallback providers](./features/fallback-providers.md) 并想更快切换，把它降到 `0`，这样主 provider 上第一个瞬时错误就立即交给 fallback，而不是对着不稳定的端点反复重试。

点名了重置时间的限流（`Retry-After` 或响应体的 `retry_after` 字段）会等过去，每次重试上限 600 秒。实时状态行会显示等待时长，以及（当 provider 点名时）限流何时解除。一个例外：在免费的 Nous 层级（未登录）上，有人正在看着的会话（Desktop 应用、TUI、`hermes` 终端聊天、ACP 编辑器）不会干等超过 60 秒的冷却，因为免费层级的暂停覆盖整个服务，重置前的重试只会撞上同一个拒绝。该回合立即结束并说明限流何时解除；已配置的 fallback 先运行。无人值守的运行（`hermes chat -q`、cron、消息平台、委派的 subagent）继续等。

`agent.auto_recovery_cycles` 是重试与 fallback 链都用尽*之后*的安全网。当故障是瞬时中断（HTTP 5xx、`overloaded`/529 响应、连接或读取超时），且还没有任何答案文本到达你这边时，Hermes 不会用「API 失败，已重试 N 次」结束回合——它等待并再试，至多这么多次周期（默认 `5`），按带抖动的 15/30/60/60/60 秒排程。provider 的 `Retry-After` 头优先于该排程（最多尊重 120 秒）。等待期间每个界面都显示同一行——CLI/TUI/Desktop 上是 `⏳ Provider temporarily unavailable — retrying automatically in 30s (cycle 2/5); press Esc to stop`，消息平台上是一个状态气泡（`send /stop to cancel`），API server 上是一个 `hermes.status` SSE 事件，cron 任务则是一行日志。按 Esc（或 `/stop`）立即取消等待。Fallback 仍然优先：配了 fallback 链时，耗尽后照旧换下一个 provider，只有当链上什么都没剩时这套阶梯才介入。认证、计费、请求格式、权限、内容政策与账户政策类错误从不进入该阶梯。设 `0` 禁用。

## 墙钟运行预算

与迭代预算分开，你可以给每次对话运行一个可选的**墙钟**预算。它为在硬性外部上限下运行的一次性与评测 harness 调用设计（例如每任务 900 秒的限制）：没有它，一次运行可能在工作基本完成时超时——差一次生成就能输出最终答案，或卡死在一次 provider 调用上。

```yaml
agent:
  run_budget_seconds: null     # Optional; unset/null = feature fully off (default)
```

也可以经 CLI 按次指定：

```bash
hermes chat --run-budget 850 -q "..."
```

设置预算后会发生两件事：

1. **80% 时的收尾提示。** 预算用掉 80% 时，Hermes 注入一条**一次性**提示（以缓存安全的方式投递，像 `/steer` 消息一样追加到最新工具结果上），让模型停止新的发现/验证工作，用它已有的状态产出最终交付物。每次运行至多触发一次，镜像既有的迭代预算收尾机制——没有反复的压力告警。
2. **随期限伸缩的陈旧超时。** 隐式的非流式陈旧超时（90 秒默认值与推理模型下限，例如 DeepSeek 推理模型 600 秒）被夹到 `max(60, 剩余预算 × 0.5)`，于是一次默默卡死的 provider 调用绝不可能耗掉运行的其余部分。这个上限只会*收紧*超时——绝不调高——而显式配置的 `stale_timeout_seconds`（provider/模型配置或 `HERMES_API_CALL_STALE_TIMEOUT`）始终原样优先。

该预算按 `run_conversation` 回合计算（每条用户消息重置），未设置时该功能完全休眠——不读时钟、不注入、不改超时。

## 停止时校验（编码验证）

启用后，如果 agent 在某个回合里编辑了 workspace 中的代码、却没有产出新的验证证据（通过的测试运行、构建、lint 等），Hermes 拒绝接受它的最终答案——会注入一条合成的后续消息，要求 agent 验证或解释为什么做不到。只改文档/markdown/skill 的编辑从不触发它，且循环有界，绝不会把 agent 困住。

```yaml
agent:
  verify_on_stop: false        # true | false | "auto" (surface-aware: on for CLI/TUI/desktop, off for messaging)
  verify_guidance: true        # Append creative-UI / clean-diff guidance to the missing-evidence nudge
  max_verify_nudges: 3         # Cap on consecutive continue nudges per turn (built-in + pre_verify hooks)
  coding_instructions: ""      # Standing project-wide coding rules appended to the coding brief
```

`verify_on_stop` 接受 `true`（到处开启）、`false`（关闭——默认），或 `"auto"`（遗留的按界面感知行为：交互式编码界面——CLI、TUI、desktop——与程序化调用方开启；Telegram/Discord 这类消息界面关闭，因为验证叙述在聊天里像噪音）。各处默认都是关：新装出货是 `false`，配置迁移也把它在既有安装上关掉，所以打开它是一次显式选择。设置 `HERMES_VERIFY_ON_STOP` 环境变量可覆盖配置值。

喂给这道守卫的证据（跑过哪些测试/lint/构建命令、此后改过哪些文件）存在 `~/.hermes/verification_evidence.db`。该台账只在守卫启用时才写入或创建；`verify_on_stop: false` 时不记录任何东西，既有文件可随意删除。

要在同一点上做用户/插件的策略闸门——用你自己的检查让 agent 继续——见 [`pre_verify` hook](./features/hooks.md#pre_verify)。

## 常驻目标（`/goal`）

常驻目标生效时，Hermes 会判断每条助手响应是否满足它。不满足就把一条继续提示喂回同一会话并继续干，直到目标完成、回合预算耗尽，或用户暂停/清除它。回合预算才是真正的兜底——判定失败按**放行**处理（继续），这样不稳定的判定器永远不会卡住进展。

```yaml
goals:
  max_turns: 20   # Max continuation turns before Hermes auto-pauses the goal (default: 20)
```

`max_turns` 限制一个目标最多能驱动多少个继续回合，超过 Hermes 就自动暂停该目标并请用户 `/goal resume`。它防的是判定器假阴性（目标其实完成了、判定器却说继续），以及模糊或不可达目标上的无界模型消耗。完整功能见 [Goals](./features/goals.md)。

### API 超时

Hermes 对流式另有一层超时，另有一个针对非流式调用的陈旧检测器。只有当你把陈旧检测器留在隐式默认值上时，它们才会对本地 provider 自动调整。

| 超时 | 默认 | 本地 provider | 配置 / 环境变量 |
|---------|---------|----------------|--------------|
| Socket 读超时 | 120 秒 | 自动提到 1800 秒 | `HERMES_STREAM_READ_TIMEOUT` |
| 陈旧流检测 | 180 秒 | 提到 900 秒上限（`agent.local_stream_stale_timeout`） | `HERMES_STREAM_STALE_TIMEOUT` |
| 流最长存活（可选） | 关（`0`） | 同上 | `agent.stream_max_lifetime` |
| 非流式陈旧检测 | 90 秒 | 隐式时自动禁用 | `providers.<id>.stale_timeout_seconds` 或 `HERMES_API_CALL_STALE_TIMEOUT` |
| Responses 首事件看门狗 | 120 秒 | 提到 900 秒上限（`agent.local_stream_stale_timeout`） | `HERMES_CODEX_TTFB_TIMEOUT_SECONDS` |
| API 调用（非流式） | 1800 秒 | 不变 | `providers.<id>.request_timeout_seconds` / `timeout_seconds` 或 `HERMES_API_TIMEOUT` |
| 终帧后流 drain（Codex/Responses） | 2 秒 | 不变 | `agent.stream_drain_timeout` |

**Socket 读超时**控制 httpx 等待 provider 下一块数据多久。本地 LLM 在大上下文上 prefill 可能要几分钟才产出第一个 token，所以 Hermes 检测到本地端点时会把它提到 30 分钟。如果你显式设置了 `HERMES_STREAM_READ_TIMEOUT`，无论端点探测结果如何都始终用该值。

**陈旧流检测**杀掉那些收到 SSE 保活 ping 却没有实际内容的连接。对本地 provider（它们在 prefill 期间不发保活 ping），默认值从 180 秒基准提到有限的 900 秒上限——可经 `agent.local_stream_stale_timeout` 或 `HERMES_LOCAL_STREAM_STALE_TIMEOUT` 环境变量配置。

**Responses 首事件看门狗**（Codex / `codex_responses` 传输，含用 Responses 传输声明的自定义 provider）会中止并重连这样一个请求：接受了连接却在 120 秒内没有发出任何流事件。本地服务器在 prefill 大上下文时合法地静默更久，所以在本地端点上隐式默认提到与陈旧流检测器相同的上限（`agent.local_stream_stale_timeout` / `HERMES_LOCAL_STREAM_STALE_TIMEOUT`，900 秒）。显式的 `HERMES_CODEX_TTFB_TIMEOUT_SECONDS` 始终原样使用（`0` 禁用看门狗）。

**流最长存活**是对一次流式响应总墙钟时间的可选上限。陈旧检测器每个数据块都重置，所以一条持续发数据却永不结束的流（一个滴答吐块的 gateway、一次失控生成）永远不会被切断。设 `agent.stream_max_lifetime`（秒）可切断这种流；连接以与陈旧杀相同的方式断掉，重试或部分响应续传接手。它绝不会在生效的陈旧流超时之前触发，被切断的尝试也不计入陈旧流熔断器（`HERMES_STREAM_STALE_GIVEUP`），因为 provider 当时在响应。该上限只覆盖 Chat Completions 与 Anthropic Messages 流；Codex/Responses 流（`codex_responses`，含用 Responses 传输声明的自定义 provider）与 Bedrock 流不受限。如果你跑的推理回合合法地流式很久，就保持 `0`（默认）。

**非流式陈旧检测**杀掉太久不产出响应的非流式调用。默认情况下 Hermes 在本地端点禁用它，以避免长 prefill 期间的误报。如果你显式设置了 `providers.<id>.stale_timeout_seconds`、`providers.<id>.models.<model>.stale_timeout_seconds` 或 `HERMES_API_CALL_STALE_TIMEOUT`，即使在本地端点也尊重该显式值。

**终帧后流 drain**约束一个 Codex/Responses 流在终帧 `response.completed` 之后还要读多久（这是一份礼节，好让中继的 finalizer 能跑）。有些中继在终帧之后从不关闭 SSE socket；没有界限的话，回合会一直卡到陈旧流看门狗触发、丢弃已经计费的响应，然后重试。`agent.stream_drain_timeout` 秒之后流被关闭，已完成的响应被返回。正常关闭连接的端点会立即结束 drain、从不等这么久；设 `0` 完全跳过 drain。

这个预算约束每一次非流式调用。一个接受请求后就沉默的 provider——连接开着、没有字节、没有错误——会在陈旧超时处被中止并重试，而不是一直挂着直到长得多的 socket 读超时（对无人值守的 cron 运行，就是直到外部某处杀掉进程）。

周期性的 provider 等待提示只在**静默满 60 秒**之后出现。Codex Responses 的**等待状态**描述的是静默，不是总生成时间：活跃的流事件（含推理）让它保持安静。事件停止时，它报告的是「没有流事件」的时长，而不是声称没有响应到达；事件恢复时提示清除。当重连开始一段全新的首事件看门狗阶段时，等待状态跟随该阶段。这段显示行为既不延长独立的墙钟陈旧调用预算，也不改变看门狗超时。状态每次静默显示一次（60 秒后），用中性措辞点名所处的等待阶段（`waiting for the first provider event` 对比 `provider stream active; Ns without stream events`）以及将要重连的那个看门狗（`TTFB`、`stream idle` 或 `wall-clock stale`）与它触发前的剩余秒数；只有阶段变化或期限临近时才重写，而不是每 30 秒的心跳都重写。Chat-completion 流遵循同一规则（`waiting for the first stream chunk` / `stream open; Ns without stream output`、`stream stale` 看门狗），同样在块恢复时及时清除静默提示，且不会覆盖本地模型加载状态。

Cron 任务与委派的 subagent 也是流式的。它们在自己的线程上内联运行请求（其他会话用的中断 worker 在 gateway 的嵌套线程池里会卡死），但线路请求仍是 `stream: true`，所以上面那套**陈旧流检测**预算约束它们——每个 token 都算存活，于是思考几分钟的推理模型不会被误认为卡死的 provider，而杀静默连接的边缘代理仍会持续看到字节。

### 关闭 API 流式

`model.streaming: false` 会强制整个会话——父 agent 与 subagent 一样——用非流式请求。它是给那些*流式*工具调用路径损坏的自托管 OpenAI 兼容服务器用的逃生口（例如 vLLM 配 `--tool-call-parser qwen3_xml` 加推理解析器，可能把工具调用标记漏进纯文本、返回零个 `tool_calls`，于是委派的任务静默空转）。默认是 `true`；除非你碰到那一类 bug，否则别改，因为非流式调用会丢掉上文描述的存活特性。这与 `display.streaming` 无关，后者只控制终端里的 token 渲染。

当流式无法推进时，Hermes 也会自己把会话切到非流式：provider 报告不支持流式，或一个 OpenAI 兼容网关用无内容的 SSE 帧回应流式请求（裸 `data:` / `event: ping` 保活、没有载荷，典型的降级中继）。该回合改为不带流式重试，显示一条警告，且该会话余下时间保持流式关闭。

```yaml
model:
  streaming: false
```

## 上下文压力告警

与迭代预算压力分开，上下文压力追踪对话离**压缩阈值**还有多近——即上下文压缩触发、开始摘要更早消息的那个点。这让你和 agent 都能理解对话什么时候变得太长。

| 进度 | 级别 | 发生什么 |
|----------|-------|-------------|
| 距阈值 **≥ 60%** | Info | CLI 显示青色进度条；gateway 发一条信息性提示 |
| 距阈值 **≥ 85%** | Warning | CLI 显示加粗黄条；gateway 警告压缩迫在眉睫 |

在 CLI 里，上下文压力表现为工具输出流里的一条进度条：

```
  ◐ context ████████████░░░░░░░░ 62% to compaction  48k threshold (50%) · approaching compaction
```

在消息平台上会发一条纯文本通知：

```
◐ Context: ████████████░░░░░░░░ 62% to compaction (threshold: 50% of window).
```

如果自动压缩被禁用，告警会改为提示上下文可能被截断。

上下文压力是自动的——无需配置。它纯粹作为面向用户的通知触发，不修改消息流，也不往模型上下文里注入任何东西。

## 凭据池策略

当你对同一个 provider 有多个 API key 或 OAuth token 时，配置轮转策略：

```yaml
credential_pool_strategies:
  openrouter: round_robin    # cycle through keys evenly
  anthropic: least_used      # always pick the least-used key
```

可选值：`fill_first`（默认）、`round_robin`、`least_used`、`random`。完整文档见 [Credential Pools](./features/credential-pools.md)。

## Prompt 缓存

当活动 provider 支持时，Hermes 会自动打开跨会话 prompt 缓存——无需用户配置。

对跑在**原生 Anthropic**、**OpenRouter**、**Nous Portal** 上的 Claude，Hermes 会在 system prompt 与 skill 块上附加带 1 小时时效（`ttl: "1h"`）的 `cache_control` 断点。新一小时内的第一次发送按全价输入计费；同一小时内跨任何会话的后续发送都以折扣的缓存读取费率从缓存取。这意味着 system prompt、已加载的 skill 内容、以及任何长上下文 include 的前段，在第一个小时内跨 `hermes` 会话、跨 fork 出的 subagent 都会复用。

Qwen Cloud（阿里 DashScope）上游把缓存时效上限定为 5 分钟，所以 Hermes 在那里改用 5 分钟断点时效。其他经第三方的 Claude 路径（AWS Bedrock、Azure Foundry）回退到 provider 自己的缓存默认值。xAI Grok 用另一套会话钉住的 conversation-id 机制——见 [xAI prompt caching](../integrations/providers.md#xai-grok--responses-api--prompt-caching)。

没有旋钮可以关掉它——缓存始终开启，即便单回合对话也省钱，因为光 system prompt 就占输入 token 数的可观比例。

唯一显式的旋钮是 Hermes 在 Anthropic 式断点上请求的缓存时效档位：

```yaml
prompt_caching:
  cache_ttl: "5m"   # "5m", "1h" (Anthropic-supported tiers) or "auto"; other values are ignored
```

`cache_ttl` 选择 Hermes 经原生 Anthropic API、OpenRouter 与 Nous Portal 为 Claude 附加的断点时效。两个 Anthropic 档位（`"5m"`、`"1h"`）原样发送；其他值被忽略。自带上限的 provider（例如 Qwen Cloud，上限 5 分钟）仍会夹到上游允许的范围。

1h 档按基础输入价的 2 倍写入（5m 档为 1.25 倍），只有当你的回合间隔超过五分钟时才划算——否则每个工具结果都按更贵的费率写入，存的却是没人用的保留。`"auto"` 按会话选择档位，看是谁在驱动：人打字的会话（CLI、TUI、Desktop、Telegram/Discord/Slack 及其他消息平台）用 `1h`，机器驱动的（subagent、cron、`hermes -q` 一次性、webhook、Kanban worker、API server、工具调用与批量运行）用 `5m`。在某个交互会话全天被挂起又恢复的安装上，`auto` 把交互式缓存写入账单大约砍了 40%，而扇出 subagent 的开销原封不动。委派的 subagent 无论该设置是什么都夹到 `5m`。

## 辅助模型

Hermes 用「辅助」模型做旁路任务，例如图像分析、浏览器截图分析、会话标题生成与上下文压缩。默认（`auxiliary.*.provider: "auto"`）下，Hermes 把每个辅助任务路由到你的**主聊天模型**——即你在 `hermes model` 里选的那个 provider/模型。上手无需任何配置，但要注意在昂贵的推理模型（Opus、MiniMax M2.7 等）上，辅助任务会带来可观成本。如果你想要无论主模型是什么都便宜快速的旁路任务，就显式设置 `auxiliary.<task>.provider` 与 `auxiliary.<task>.model`（例如在 OpenRouter 上用 Gemini Flash 做视觉）。（网页提取不是辅助任务：`web_extract` 与浏览器快照按确定性方式截断长内容，并把全文存下来供 `read_file` 分页——不涉及 LLM。）

:::note 为什么 `auto` 用你的主模型
更早的构建把聚合器用户（OpenRouter、Nous Portal）分到一个便宜的 provider 侧默认值上。那很令人意外——付了聚合器订阅费的用户会看到另一个模型在处理他们的辅助流量。现在 `auto` 对所有人都用主模型，`config.yaml` 里的按任务覆盖仍然优先（见下文[完整辅助配置参考](#完整辅助配置参考)）。
:::

### 交互式配置辅助模型

不必手改 YAML，运行 `hermes model` 并从菜单选 **"Configure auxiliary models"**。你会拿到一个交互式的按任务选择器：

```
$ hermes model
→ Configure auxiliary models

[ ] vision               currently: auto / main model
[ ] title_generation     currently: openrouter / google/gemini-3-flash-preview
[ ] tts_audio_tags       currently: auto / main model
[ ] voice_chat           currently: auto / main model
[ ] compression          currently: auto / main model
[ ] approval             currently: auto / main model
[ ] triage_specifier     currently: auto / main model
[ ] kanban_decomposer    currently: auto / main model
[ ] profile_describer    currently: auto / main model
[ ] delegation           currently: auto / inherit main agent
```

选一个任务、挑一个 provider（OAuth 流程会打开浏览器；API key 型 provider 会询问）、挑一个模型。改动持久化到 `config.yaml` 的 `auxiliary.<task>.*`。与主模型选择器同一套机制——没有额外语法要学。

**Delegation** 条目是特殊的：它路由 `delegate_task` subagent 使用的模型，并持久化到顶层 `delegation.*` 段（`delegation.provider` / `delegation.model`）而不是 `auxiliary.*`，因为 subagent 是完整的子 agent，不是旁路 LLM 调用。它的 `auto` 意思是「继承父 agent 的 provider、模型与凭据」。

**Voice chat** 条目挑选回答语音模式回合（含工具）的模型；打字的回合仍用主模型。见 [Voice chat model](./features/voice-mode.md#voice-chat-model)。

如果你不想让 Hermes 在首轮交换之后自动生成标题，设 `auxiliary.title_generation.enabled: false`。手动标题仍可通过 `/title` 与 `hermes sessions rename` 使用。

想保留即时派生标题（你开场消息的第一行）却从不花一次模型调用去升级它，设 `auxiliary.title_generation.model_upgrade_enabled: false`。这样不会启动后台 `auto-title` 线程，也不发自动标题模型请求；显式修复命令 `hermes sessions retitle-skills` 仍会调用模型。`enabled: false` 则两个阶段都禁用。

在 `custom` 主 provider（llama.cpp、Ollama、vLLM、LM Studio 及其他自托管 OpenAI 兼容服务器）上，标题模型调用在回合回复到达**之后**才发出，而不是与之并发，除非 `auxiliary.title_generation` 被钉到别的 provider 或 `base_url`。否则一个单槽位本地服务器在解码回复时收到 `json_schema` 标题请求，可能用 `{"title": ...}` 来回答那条回复，随后被存下来当作助手的回合重放。

在 Hermes Desktop 里，超过 3,000 字符的纯文本粘贴会变成一个生成的 `.txt` 附件。该粘贴的前约 1,000 字符会作为「只要标题」的提示交给标题阶段（agent 回合仍只看到附件引用），于是「summarize this」加大段粘贴会以粘贴的主题命名。你自己附加的文件从不被读取用于起名。

在本地消息 gateway 里，文本消息在加入频道绑定的 skill 与平台上下文之前，就把其原始请求提供给会话起名。主模型与对话历史仍保留完整的 skill 内容。仅附件的回合沿用既有的富消息标题兜底。这影响新的标题生成；不修复此前已命名的会话。

### 仅流式端点

有些 OpenAI 兼容端点直接拒绝非流式聊天请求（例如腾讯 Copilot 返回 HTTP 400 `"Non-stream chat request is currently not supported"`）。交互式聊天本来就是流式的，但辅助任务（标题生成、压缩、视觉）用的是非流式调用，每次尝试都会失败。Hermes 始终把 `copilot.tencent.com` 视为仅流式；其他此类端点请在 `auxiliary.stream_only_base_urls` 下列出 URL 子串：

```yaml
auxiliary:
  stream_only_base_urls:
    - "my-stream-only-proxy.example.com"
```

匹配的辅助调用会以 `stream=True` 发送，数据块（含工具调用增量）在客户端聚合——对其他任何端点没有行为变化。

### 视频教程

<div style={{position: 'relative', width: '100%', aspectRatio: '16 / 9', marginBottom: '1.5rem'}}>
  <iframe
    src="https://www.youtube.com/embed/NoF-YajElIM"
    title="Hermes Agent — Auxiliary Models Tutorial"
    style={{position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', border: 0}}
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
    allowFullScreen
  />
</div>

### 通用配置模式

Hermes 里每个模型槽位——辅助任务、压缩、fallback——都用同样三个旋钮：

| 键 | 作用 | 默认 |
|-----|-------------|---------|
| `provider` | 认证与路由用哪个 provider | `"auto"` |
| `model` | 请求哪个模型 | provider 的默认 |
| `base_url` | 自定义 OpenAI 兼容端点（覆盖 provider） | 未设置 |

辅助任务块还接受一个 `reasoning_effort` 旋钮：

| 键 | 作用 | 默认 |
|-----|-------------|---------|
| `reasoning_effort` | 该任务 LLM 调用的思考级别：`none`、`minimal`、`low`、`medium`、`high`、`xhigh`、`max`、`ultra` | 未设置（provider 默认） |

这是全局 `agent.reasoning_effort` 的按任务对应物：把压缩跑在 `low`、或视觉跑在 `none`，可以在主模型是昂贵推理模型时削减旁路任务的延迟与成本，而不动你的主聊天行为。它作用于辅助客户端任务，如 `vision`、`compression`、`title_generation`、`curator`，横跨三种辅助线路格式（chat completions、Codex Responses、Anthropic Messages）。同一任务上显式的 `extra_body.reasoning` 优先于这个简写。如果某个调用方为自己的调用关掉了思考（标题生成就是这样——一个 64 token 的标题没有推理空间），它优先于两者：该请求会丢掉任务级 effort，而不是与 provider 的关思考字段并列发送。

如果端点直接拒绝推理字段（一个 OpenAI 兼容中继后面的纯聊天模型回答 `400 Unrecognized request argument supplied: reasoning_effort`，或反过来措辞的 `400 reasoning_effort 'none' unsupported; use minimal|low|medium|high|xhigh`），辅助调用会省略所有推理字段重试一次，于是该任务（例如会话标题）仍以端点的默认行为完成。主对话适用同样的恢复：当某条路由拒绝 Hermes 为「只思考的截断续传」发出的关思考请求时，该会话余下时间都丢掉这个禁用，并用该路由的默认值重试请求。

有些模型根本关不掉思考（`400 Reasoning is mandatory for this endpoint and cannot be disabled`）。对这些模型，一次关思考的辅助调用（标题生成，或任何设为 `reasoning_effort: none` 的任务）会以最低 effort（`low`）发出，而不是发禁用。Hermes 提前就知道路由的模型目录何时把该模型标为强制（OpenRouter 与 Nous Portal 的 `/v1/models`，缓存在 `cache/reasoning_caps.json`），或该路由在同一进程里早先是否已这样回应过禁用。因此被拒绝的请求根本不会发出。没有缓存目录的新安装仍可能看到一次那个 400：查询会在后台抓取目录，之后的调用就用它。

**后台 review 不一样：**同模型的 review fork 始终继承父进程的 reasoning effort。`auxiliary.background_review.reasoning_effort` 在该路径上被忽略，即使父 provider/模型是显式选择的。这为 prompt 缓存对齐保留了逐字节相同的推理设置、system prompt、完整对话快照与工具定义；同模型 review 没有独立 effort 开关。见 [background review reasoning](./features/memory.md#same-model-review-reasoning)。当 review 路由到不同 provider/模型时，`reasoning_effort` 作用于那个被路由的 fork（未设 = 被路由 provider 的默认）。当该键已设置但 review 跑在主模型上时，Hermes 会打印一次性警告。

**MoA 用的也是另一套配置：**Mixture-of-Agents 的推理深度在 MoA 预设里**按槽位**配置（`moa.presets.<name>.reference_models[].reasoning_effort` / `aggregator.reasoning_effort`），而不是在 `moa_reference`/`moa_aggregator` 辅助块上——见 [Mixture of Agents](./features/mixture-of-agents.md)。

```yaml
auxiliary:
  compression:
    reasoning_effort: "low"    # summaries don't need deep thinking
  vision:
    reasoning_effort: "none"   # disable thinking for image description
```

设置 `base_url` 时，Hermes 忽略 provider 并直接调那个端点（用 `api_key` 或 `OPENAI_API_KEY` 认证）。只设 `provider` 时，Hermes 用该 provider 的内置认证与 base URL。

辅助任务可用的 provider：`auto`、`main`，加上 [provider 注册表](../reference/environment-variables.md)里的任何 provider——`openrouter`、`nous`、`openai-codex`、`anthropic`、`gemini`、`qwen-oauth`、`zai`、`kimi-coding`、`kimi-coding-cn`、`minimax`、`minimax-cn`、`minimax-oauth`、`deepseek`、`nvidia`、`xai`、`xai-oauth`、`ollama-cloud`、`alibaba`、`bedrock`、`huggingface`、`arcee`、`xiaomi`、`kilocode`、`opencode-zen`、`opencode-go`、`commandcode`、`commandcode-anthropic`、`ai-gateway`、`azure-foundry`——或你 `providers:` 字典里的任何具名自定义 provider（例如 `provider: "beans"`）。

本地 OpenAI 兼容服务器也能用自己的名字工作：`provider: ollama`（也支持 `vllm`、`llamacpp`、`llama.cpp`）配一个如 `http://127.0.0.1:11434` 的 `base_url` 与空 `api_key`，会经占位密钥走自定义端点，裸的 `host:port` base_url 会自动补上 `/v1` 后缀。

`provider: openai` 是直连 API 的别名：它经该块的 `base_url`、否则 `OPENAI_BASE_URL`、否则 `https://api.openai.com/v1` 的自定义端点路由，用 `api_key` 或 `OPENAI_API_KEY` 认证。每个辅助任务都以同样方式解析它——`compression`/`vision`/`title_generation` 以及 `background_review`、`curator` 与 MoA 槽位——所以保留 `provider: openai` 而删掉 `base_url` 会把该任务移到公开的 OpenAI 端点。你 `providers:` 字典里的 `providers.openai` 条目优先，并保留它自己的端点与密钥。

当被路由的 `auxiliary.<task>` 块无法解析（未知 provider、缺端点或凭据）时，该任务跑在主模型上，Hermes 会说明：`background_review` 发出一次性用户可见警告，点名 provider 与原因（外加每次 review 在 `agent.log` 里的一行 `WARNING`），`hermes doctor` 用同一解析器解析每个被路由的 `auxiliary.<task>` 块并报告失败的那些。

:::tip MiniMax OAuth
`minimax-oauth` 走浏览器 OAuth 登录（无需 API key）。运行 `hermes model` 并选择 **MiniMax (OAuth)** 完成认证。辅助任务自动使用 `MiniMax-M2.7-highspeed`。见 [MiniMax OAuth 指南](../guides/minimax-oauth.md)。
:::

:::tip xAI Grok OAuth
`xai-oauth` 面向 SuperGrok 与 X Premium+ 订阅者走浏览器 OAuth（无需 API key）。运行 `hermes model` 并选择 **xAI Grok OAuth (SuperGrok / Premium+)** 完成认证。同一个 OAuth token 会被所有直连 xAI 的界面复用（聊天、辅助任务、TTS、图像生成、视频生成、转写）。见 [xAI Grok OAuth 指南](../guides/xai-grok-oauth.md)；若 Hermes 在远程主机上，另见 [OAuth over SSH / Remote Hosts](../guides/oauth-over-ssh.md)。
:::

:::warning `"main"` 只用于辅助任务
`"main"` provider 选项意为「用我主 agent 用的那个 provider」——它只在 `auxiliary:`、`compression:` 与主 fallback 条目（`fallback_providers:` 或遗留的 `fallback_model:`）内有效。它**不是**顶层 `model.provider` 设置的合法值。如果你用自定义 OpenAI 兼容端点，请在 `model:` 段里设 `provider: custom`。主模型 provider 的全部选项见 [AI Providers](../integrations/providers.md)。
:::

### 完整辅助配置参考

```yaml
auxiliary:
  # Image analysis (vision_analyze tool + browser screenshots)
  vision:
    provider: "auto"           # "auto", "openrouter", "nous", "codex", "main", etc.
    model: ""                  # e.g. "openai/gpt-4o", "google/gemini-2.5-flash"
    base_url: ""               # Custom OpenAI-compatible endpoint (overrides provider)
    api_key: ""                # API key for base_url (falls back to OPENAI_API_KEY)
    timeout: 120               # seconds — LLM API call timeout; vision payloads need generous timeout
    download_timeout: 30       # seconds — image HTTP download; increase for slow connections
    max_concurrency: 8         # max concurrent image encode/resize bursts across the process
                               # (default: host CPU core count, no ceiling) — bounds only the
                               # CPU-bound encode step so a video-frame fan-out can't saturate
                               # every core and starve the event loop; LLM calls stay fully
                               # concurrent. Minimum 1; values < 1 are ignored.

  # Dangerous command approval classifier
  approval:
    provider: "auto"
    model: ""
    base_url: ""
    api_key: ""
    timeout: 30                # seconds

  # Gemini 3.1 TTS hidden audio-tag insertion
  tts_audio_tags:
    provider: "auto"
    model: ""                  # empty = main chat model
    base_url: ""
    api_key: ""
    timeout: 30

  # Context compression timeout (separate from compression.* config)
  compression:
    timeout: 120               # seconds — compression summarizes long conversations, needs more time
    # no_progress_timeout: 60   # seconds a streamed summary may go without a substantive chunk
    #                           # before the attempt fails fast into retry/fallback
    # fallback_chain:           # Optional — providers to try on rate-limit / connectivity failure
    #   - provider: nous
    #     model: deepseek/deepseek-chat
    #   - provider: openrouter
    #     model: google/gemini-2.5-flash
    #     base_url: ""
    #     api_key: ""
    # max_concurrency: 2       # Optional: cap simultaneous compression LLM calls so
                               # multiple sessions don't pile retries on a degraded provider

  # Auto-generated session titles. Empty language follows the conversation;
  # set e.g. "English" or "Japanese" to pin titles to one language.
  title_generation:
    enabled: true              # set false to disable auto-title generation
    model_upgrade_enabled: true  # set false to keep the instant derived title, never call a model
    provider: "auto"
    model: ""
    base_url: ""
    api_key: ""
    timeout: 30
    language: ""

  # Skills hub — skill matching and search
  skills_hub:
    provider: "auto"
    model: ""
    base_url: ""
    api_key: ""
    timeout: 30

  # MCP tool dispatch
  mcp:
    provider: "auto"
    model: ""
    base_url: ""
    api_key: ""
    timeout: 30

  # Auto-generated short session titles after the first exchange
  title_generation:
    provider: "auto"
    model: ""
    base_url: ""
    api_key: ""
    timeout: 30
    # max_concurrency: 2       # Optional: cap simultaneous title-generation calls

  # Kanban triage specifier — `hermes kanban specify <id>` (or the
  # dashboard's ✨ Specify button on Triage-column cards) uses this
  # slot to expand a one-liner into a concrete spec and promote the
  # task to `todo`. Cheap fast models work well here; spec expansion
  # is short and doesn't need reasoning depth.
  triage_specifier:
    provider: "auto"
    model: ""
    base_url: ""
    api_key: ""
    timeout: 120
```

:::tip
每个辅助任务都有可配置的 `timeout`（秒）。默认值：vision 120 秒、approval 30 秒、compression 120 秒、标题生成 30 秒、其他任务 30 秒。如果你用慢的本地模型做辅助任务就调高——一个在答案前先吐思考块的推理模型，起个标题通常要超过 30 秒，而撞上期限的请求会在 Hermes 尝试 fallback 链之前被记为 `Auxiliary <task>: request to <base_url> timed out after <N>s (raise auxiliary.<task>.timeout …)`。标题生成、压缩与视觉在主路由上经过一整个超时窗口后就放弃（不重试同 provider），这样慢模型不会把等待放大。视觉还有一个独立的 `download_timeout`（默认 30 秒）用于 HTTP 图片下载——慢连接或自托管图片服务器请调高。
:::

:::info
上下文压缩有自己的 `compression:` 块放阈值，另有 `auxiliary.compression:` 块放模型/provider 设置——见上文[上下文压缩](#上下文压缩)。主 fallback 链用顶层 `fallback_providers:` 列表——见 [Fallback Providers](../integrations/providers.md#fallback-providers)。三者遵循同样的 provider/model/base_url 模式。
:::

### 辅助任务的按任务 fallback 链

每个辅助任务都可以选择定义一个 `fallback_chain`——一串 provider/model 条目，当主辅助 provider 因限流、连通性问题或支付限制失败时按序尝试：

```yaml
auxiliary:
  compression:
    provider: openrouter
    model: openai/gpt-4o-mini
    fallback_chain:
      - provider: nous
        model: deepseek/deepseek-chat
      - provider: openrouter
        model: google/gemini-2.5-flash
```

当主辅助 provider（`openrouter` / `openai/gpt-4o-mini`）返回限流、连接超时或需要付费的错误时，Hermes 按序走 `fallback_chain`。它跳过 provider 与已失败 provider 相同的条目，逐个尝试剩余条目，直到某个成功或链耗尽。如果所有 fallback 都失败，Hermes 以主 agent 模型作为最终安全网。

每个条目支持与任何辅助任务配置相同的三个旋钮：

| 键 | 说明 |
|-----|-------------|
| `provider` | Provider 名（`nous`、`openrouter`、`anthropic`、`gemini`、`main` 等） |
| `model` | 该 provider 的模型名 |
| `base_url` | （可选）自定义 OpenAI 兼容端点 |

`fallback_chain` 在任何辅助任务上都可用——`compression`、`vision`、`approval`、`skills_hub`、`mcp` 等。

### 原生视觉嵌入预算（顶层 `vision:`）

与 `auxiliary.vision`（挑选描述模型的那个）分开：当*主*模型具备视觉能力时，`vision_analyze` 与浏览器截图会把真实像素嵌入工具结果，之后每个回合都要重发。`vision.embed_target_bytes`（默认 `262144`，夹在 64 KiB..4 MiB）设定单次嵌入的大小；`vision.max_calls_per_image` 限制同一张图每个会话最多嵌入几次（未设 = 委派 subagent 内为 3、主 agent 无限；`0` = 无限）；`vision.replay_recent_images`（默认 `3`，`0` = 关）在从会话数据库重建的回合上重发最新的用户图片（API server、`--resume`）。见 [Vision → Native embeds ride the session](./features/vision.md#native-embeds-ride-the-session-visionembed_target_bytes-and-visionmax_calls_per_image)。

### 限制辅助并发

`max_concurrency` 在整个进程内限制 `compression`、`title_generation` 这类辅助任务的在途 LLM 调用。`auxiliary.vision.max_concurrency` 被排除：它本来就只管 vision 那些 CPU 密集的图像编码/缩放 worker，不管理 LLM 请求。它在以下情况最有用：

- 许多会话可能同时派生后台工作（Discord/Telegram 频道、多个终端）
- 你的 provider 被限流或正在经历事故，重试会放大这次突发

默认无限制。典型的安全上限是 `2`：

```yaml
auxiliary:
  title_generation:
    max_concurrency: 2
  compression:
    max_concurrency: 2
```

信号量包住整次调用（含重试与 fallback），所以一次慢调用对限额只算一次。

### 辅助任务的 OpenRouter 路由与 Pareto Code

当某个辅助任务解析到 OpenRouter（显式指定，或你的主 agent 在 OpenRouter 上时经 `provider: "main"`），主 agent 的 `provider_routing` 与 `openrouter.min_coding_score` 设置**不会传播**——按设计，每个辅助任务都是独立的。要为某个辅助任务设置 OpenRouter provider 偏好、或使用 [Pareto Code 路由器](../integrations/providers.md#openrouter-pareto-code-router)，请经 `extra_body` 按任务设置：

```yaml
auxiliary:
  compression:
    provider: openrouter
    model: openrouter/pareto-code         # use the Pareto Code router for this task
    extra_body:
      provider:                            # OpenRouter provider routing prefs
        order: [anthropic, google]         # try these providers in order
        sort: throughput                   # or "price" | "latency"
        # only: [anthropic]                # restrict to a specific provider
        # ignore: [deepinfra]              # exclude specific providers
      plugins:                             # OpenRouter Pareto Code router knob
        - id: pareto-router
          min_coding_score: 0.5            # 0.0–1.0; higher = stronger coders
```

这个形状与 OpenRouter 在 chat completions 请求体里接受的字段一致。Hermes 把整个 `extra_body` 原样转发，所以 [openrouter.ai/docs](https://openrouter.ai/docs) 文档里任何其他 OpenRouter 请求体字段都同样好使。

### 更换视觉模型

想用 GPT-4o 而不是 Gemini Flash 做图像分析：

```yaml
auxiliary:
  vision:
    model: "openai/gpt-4o"
```

或用环境变量（写在 `~/.hermes/.env` 里）：

```bash
AUXILIARY_VISION_MODEL=openai/gpt-4o
```

### Provider 选项

这些选项作用于**辅助任务配置**（`auxiliary:`、`compression:`）与主 fallback 条目（`fallback_providers:` 或遗留的 `fallback_model:`），不作用于你的主 `model.provider` 设置。

| Provider | 说明 | 要求 |
|----------|-------------|-------------|
| `"auto"` | 最佳可用（默认）。视觉依次试 OpenRouter → Nous → Codex。 | — |
| `"openrouter"` | 强制 OpenRouter —— 路由到任意模型（Gemini、GPT-4o、Claude 等） | `OPENROUTER_API_KEY` |
| `"nous"` | 强制 Nous Portal | `hermes auth` |
| `"codex"` | 强制 Codex OAuth（ChatGPT 账户）。请显式设 `model`（例如 `gpt-5.4`）。 | `hermes model` → ChatGPT or Codex Subscription |
| `"minimax-oauth"` | 强制 MiniMax OAuth（浏览器登录，无需 API key）。辅助任务使用 MiniMax-M2.7-highspeed。 | `hermes model` → MiniMax (OAuth) |
| `"xai-oauth"` | 强制 xAI Grok OAuth（面向 SuperGrok 或 X Premium+ 订阅者的浏览器登录，无需 API key）。同一个 OAuth token 覆盖聊天、TTS、图像、视频与转写。 | `hermes model` → xAI Grok OAuth (SuperGrok / Premium+) |
| `"main"` | 用你活动的自定义/主端点。它可能来自 `OPENAI_BASE_URL` + `OPENAI_API_KEY`，或经 `hermes model` / `config.yaml` 保存的自定义端点。适用于 OpenAI、本地模型或任何 OpenAI 兼容 API。**仅限辅助任务 —— 对 `model.provider` 无效。** | 自定义端点凭据 + base URL |

主 provider 目录里的直连 API key 型 provider 在这里同样可用，当你想让旁路任务绕过默认路由器时。例如配好 `GMI_API_KEY` 后 `gmi` 就有效，配好 `FIREWORKS_API_KEY` 后 `fireworks` 就有效：

```yaml
auxiliary:
  compression:
    provider: "gmi"
    model: "anthropic/claude-opus-4.6"
```

GMI 辅助路由请使用 GMI 的 `/v1/models` 端点返回的精确模型 ID。Fireworks 模型 ID 用该 provider 原生的斜杠形式，例如 `accounts/fireworks/models/glm-5p2`。

### 常见设置

**使用直连自定义端点**（对本地/自托管 API 比 `provider: "main"` 更清楚）：

```yaml
auxiliary:
  vision:
    base_url: "http://localhost:1234/v1"
    api_key: "local-key"
    model: "qwen2.5-vl"
```

`base_url` 优先于 `provider`，所以这是把辅助任务路由到特定端点最显式的方式。直连端点覆盖时，Hermes 用配置的 `api_key`，否则回退到 `OPENAI_API_KEY`；它不会为那个自定义端点复用 `OPENROUTER_API_KEY`。两者都没设时，只有当 `base_url` 与主端点的 origin（scheme、host 与端口）完全一致才复用主模型的 key。主端点就是会话正在跑的那个（`/model` 切换后就是切换后的那个），且始终与它自己的 key 配对，绝不用别的端点的 key。

**用 OpenAI API key 做视觉：**

```yaml
# In ~/.hermes/.env:
# OPENAI_BASE_URL=https://api.openai.com/v1
# OPENAI_API_KEY=sk-...

auxiliary:
  vision:
    provider: "main"
    model: "gpt-4o"       # or "gpt-4o-mini" for cheaper
```

**用 OpenRouter 做视觉**（路由到任意模型）：

```yaml
auxiliary:
  vision:
    provider: "openrouter"
    model: "openai/gpt-4o"      # or "google/gemini-2.5-flash", etc.
```

**用 Codex OAuth**（ChatGPT Pro/Plus 账户 —— 无需 API key）：

```yaml
auxiliary:
  vision:
    provider: "codex"     # uses your ChatGPT OAuth token
    model: "gpt-5.4"      # no implicit default on the Codex route
```

**用 MiniMax OAuth**（浏览器登录，无需 API key）：

```yaml
model:
  default: MiniMax-M2.7
  provider: minimax-oauth
  base_url: https://api.minimax.io/anthropic
```

运行 `hermes model` 并选择 **MiniMax (OAuth)** 即可登录并自动设置。中国区的 base URL 是 `https://api.minimaxi.com/anthropic`。完整走查见 [MiniMax OAuth 指南](../guides/minimax-oauth.md)。

**用本地/自托管模型：**

```yaml
auxiliary:
  vision:
    provider: "main"      # uses your active custom endpoint
    model: "my-local-model"
```

`provider: "main"` 使用 Hermes 正常聊天所用的那个 provider——无论是具名自定义 provider（例如 `beans`）、`openrouter` 这类内置 provider，还是遗留的 `OPENAI_BASE_URL` 端点。

:::tip
如果你用 Codex OAuth 作为主模型 provider，视觉自动可用——无需额外配置。Codex 在视觉的自动探测链里。
:::

:::warning
**视觉需要多模态模型。** 如果你设了 `provider: "main"`，请确认你的端点支持多模态/视觉，否则图像分析会失败。
:::

### 环境变量（遗留）

辅助模型也可以经环境变量配置。不过 `config.yaml` 是首选方式——更好管理，且支持包括 `base_url` 与 `api_key` 在内的全部选项。

| 设置 | 环境变量 |
|---------|---------------------|
| Vision provider | `AUXILIARY_VISION_PROVIDER` |
| Vision model | `AUXILIARY_VISION_MODEL` |
| Vision endpoint | `AUXILIARY_VISION_BASE_URL` |
| Vision API key | `AUXILIARY_VISION_API_KEY` |

压缩与 fallback 模型设置只能写在 config.yaml。（`AUXILIARY_WEB_EXTRACT_*` 变量已废弃——网页提取不再使用辅助 LLM。）

:::tip
运行 `hermes config` 查看你当前的辅助模型设置。只有与默认值不同的覆盖项才会显示。
:::

## 推理力度

控制模型在回答之前「思考」多少：

```yaml
agent:
  reasoning_effort: ""   # empty = medium. Options: none, minimal, low, medium, high, xhigh, max, ultra
```

未设置（默认）时，推理力度为「medium」——对大多数任务都合适的均衡档。设一个值即覆盖它——更高的推理力度在复杂任务上给出更好结果，代价是更多 token 与延迟。

### 答案长度（`text_verbosity`）

Responses-API 模型（OpenAI GPT-5 系列及之后、直连 OpenAI、ChatGPT Codex 与 Azure 路由）还接受一个独立旋钮，控制最终自然语言回答有多长，与推理深度无关：

```yaml
agent:
  text_verbosity: ""   # empty = not sent (provider default). Options: low, medium, high
```

Hermes 只在 Responses 系路由上把它作为顶层 Responses `text: {verbosity: ...}` 字段发送；在 `chat_completions`、Anthropic 或 xAI 请求上从不发送，空值或未知值也不发送。经 `request_overrides` 设置的结构化输出（`text.format`）原样透传。

### OpenAI Daybreak（`daybreak`）

[Daybreak](https://help.openai.com/en/articles/20001258-openai-daybreak-trusted-access-for-cyber-overview) 是 OpenAI 的 Trusted Access for Cyber 计划：获批账户在受支持的模型上做授权安全工作时拒绝更少。在 ChatGPT/Codex 订阅（`openai-codex`）上，Hermes 可以请求它：

```yaml
agent:
  daybreak: false   # true = request Daybreak Blue on models your account is approved for
```

在 Desktop 里，在模型菜单中打开某个模型的选项：**Daybreak** 开关出现在 **Fast** 旁边，且只在你登录账户的 Codex 目录为 Daybreak 列出的模型上出现。没有 Daybreak 的账户永远看不到它。该开关与 Codex 自己的开关一样是 profile 级的，从下一个回合生效。

每个请求都会重新查目录，所以只有当开关打开**且**该请求的账户与模型都在列表中时才发送 `access_programs.cyber: daybreak_blue`。切到未列出的模型、轮转到没有权限的账户、或目录读不出来时都发标准请求。在 API key 路由与可选的 `codex_app_server` 运行时上不发送，且只有你自己的聊天回合用它（Desktop、TUI 与 CLI）。消息平台聊天、托管房间、A2A 对端、第三方 `--source tool` 集成、编辑器（ACP）客户端、cron 任务与 subagent 一律使用标准防护：OpenAI 不允许 Daybreak 被任何第三方或下游访问，而那些聊天里可能有别人。这个设置不授予任何权限：批准来自 OpenAI。

:::note OpenRouter 上的自适应思考模型（Claude 4.6+、Fable/Mythos 级）
这些模型用*自适应*思考，不接受通常的 `reasoning.effort` 字段——OpenRouter 对它们忽略该字段。Hermes 透明地把你的 `reasoning_effort` 改路由到 OpenRouter 的 `verbosity` 参数（它映射到 Anthropic 的 `output_config.effort`），于是同一个 effort 旋钮在所选模型支持的档位上继续工作。`none`（或不设置）让模型用自己的自适应默认值。原生 Anthropic provider 本来就直接控制 effort，不受影响。
:::

:::note OpenRouter 模型与受支持的 effort 档位
对其他经 OpenRouter 路由的模型，Hermes 读取实时模型目录的推理元数据（`supported_parameters` + 按模型的 `reasoning.supported_efforts`），决定是否发送推理控制，并把你请求的 effort 夹到该路由实际支持的最近档位（永远向下——例如在止于 `high` 的路由上 `ultra` 变成 `high`，绝不静默升级）。新的可推理 vendor 无需等 Hermes 更新即可自动生效；当目录不可达或模型未列出时，Hermes 回退到内置的模型家族列表，并原样传递你的 effort。
:::

:::note `ultra` 被夹到该路由接受的最强档位
`ultra` 是 Hermes 内部的阶梯档位：没有 provider 线路协议接受它，所以每条路由都把它夹到自己的最强档位（GPT-5.6 Codex 与 OpenAI 兼容路由上是 `max`，较旧的 Codex 模型上是 `xhigh`）。effort 选择器与 `/reasoning` 状态把它显示为 `ultra (sends max on this route)`，于是你看到的档位就是实际发送的档位。
:::

也可以用 `/reasoning` 命令在运行时改变推理力度：

```
/reasoning                # Show current effort level and display state
/reasoning high           # Set reasoning effort to high (this session only)
/reasoning high --global  # Set effort and persist to config.yaml
/reasoning none           # Disable reasoning (this session only)
/reasoning show           # Show model thinking above each response
/reasoning hide           # Hide model thinking
```

Effort 改动默认按会话生效；加 `--global` 可把新档位保存为你的 `agent.reasoning_effort` 默认值。

#### 按模型的推理覆盖

可以为不同模型设置不同的推理力度。当你想给复杂模型高推理、给更快的模型中推理时很有用：

```yaml
agent:
  reasoning_effort: "medium"       # global default
  reasoning_overrides:
    "openrouter/anthropic/claude-opus-4.5": "xhigh"
    "openai/gpt-5": "low"
    "claude-sonnet-4.6": "high"    # bare model name also works
```

键的匹配是**拼写宽容**的——任何合理拼写都能命中：

- `claude-opus-4.5`、`claude-opus-4-5`、`claude-opus.4.5`（点与横线可互换）
- `anthropic/claude-opus-4.5`、`openrouter/anthropic/claude-opus-4.5`（provider 前缀可选）
- 以具名自定义 provider 为前缀的键（`ollama-local/qwen3.6:27b-q4_k_m`）在请求只带裸模型 id（`qwen3.6:27b-q4_k_m`，即 fallback 条目与 `providers:` 路由发送的形式）时同样生效
- 精确匹配优先于变体

#### 自定义推理档位名

有些 OpenAI 兼容端点暴露标准阶梯之外的思考档位（一个中继提供 `fast`/`thinking` 而不是 `low`…`max`）。阶梯之外的裸字符串会被拒绝并报 `Unknown reasoning_effort '<value>', using default (medium)`，于是拼写错误绝不会到达线路。要请求 provider 自己的档位名，请用显式的字典形式——`effort` 的值原样作为顶层 `reasoning_effort` 字段发送：

```yaml
agent:
  reasoning_effort:
    enabled: true
    effort: thinking            # sent as-is
  reasoning_overrides:
    "my-relay/lumo-max":        # dict form works per model too
      enabled: true
      effort: fast
```

字典形式里的 `enabled: false` 关掉思考，与 `reasoning_effort: none` 相同。

字典形式通过直接编辑 `config.yaml` 来设置：`/reasoning` 菜单、`hermes model` 与 dashboard 的辅助模型选择器只提供标准阶梯（TUI 状态与设置向导在配置好之后仍会显示自定义档位名）。

:::note
模型 id 含点（`claude-opus-4.5`、`qwen3.6:27b`），而 `hermes config set` 把点当作嵌套分隔符。用反斜杠转义以写入字面键——`hermes config set 'agent.reasoning_overrides.ollama-local/qwen3\.6:27b-q4_k_m' low`——或直接编辑 YAML。见[键名内的点](../reference/cli-commands.md#dots-inside-key-names)。
:::

:::note OpenAI Responses（`openai-api`、`openai-codex`）
在接受它的模型（GPT-5.x）上，`reasoning_effort: none` 会显式作为 `reasoning.effort: "none"` 发送：省略该字段会让模型的默认 effort 保持开启（GPT-5.6 默认 `medium`）。只有未设置 effort 才是省略该字段的状态。`api.openai.com` 上的 chat 时代模型（`gpt-4o`、`gpt-4.1`、它们的 `-mini` 变体与微调版）拒绝任何 `reasoning` 参数，所以无论配置的 effort 是什么，Hermes 都不给它们发送该字段，而不是以 `400 Unsupported parameter: 'reasoning.effort'` 失败。如果模型拒绝 `none`，Hermes 会警告、在该会话丢掉这个禁用并用模型默认值重试。
:::

:::note 本地 OpenAI 兼容端点
自定义 `base_url`（`http://localhost:11434/v1`、vLLM、SGLang 或路由器端点）会收到解析后的 effort——`agent.reasoning_effort` 或匹配的按模型覆盖——作为标准顶层 `reasoning_effort` 请求字段，并夹到 OpenAI 兼容线路接受的值（`none`、`minimal`、`low`、`medium`、`high`、`xhigh`、`max`）。这里未设置的 effort 也按 `medium` 发送，与 Nous Portal 和 OpenRouter 路由的默认一致——不发该字段会把选择权交给端点，而一个托管推理模型自己的默认值可能是它的天花板（kimi-k3 默认 `max`：推理 token 与延迟约为 `medium` 的 3 倍）。对目录或 `model_overrides` 标为 `supports_reasoning: false` 的模型、对拉取时没带 `thinking` 能力的本地 Ollama 模型、以及端点对该字段回了 `400` 之后的该会话余下时间，该字段保持关闭。嵌套的 `reasoning` 对象保留给已知接受它的端点（Nous Portal、OpenRouter 可推理模型、GitHub Models），因为任意服务器都会以 HTTP 400 拒绝未知字段。如果你的服务器从别的字段读思考预算（Ollama 的 `think`、vLLM 的 `chat_template_kwargs`、路由器专属键），请在自定义 provider 的 [`extra_body`](../integrations/providers.md#named-custom-providers) 下设置，它会被合并进路由到那里的每个请求。
:::

**解析优先级：**

1. 按会话的 `/reasoning --session` 覆盖（仅 gateway）
2. `agent.reasoning_overrides` 里的按模型覆盖（拼写宽容）
3. 全局 `agent.reasoning_effort`
4. Provider 默认

该覆盖在所有地方自动生效：CLI 启动、`hermes -p` 一次性调用、消息 gateway、Desktop/TUI、ACP 会话、cron 任务、会话中途的 `/model` 切换（含第一条消息之前发出的切换）、会话恢复（`--resume`、`/resume`）、`/new`，以及 fallback 模型激活。

## Fast Mode

Fast mode 以溢价换取更快的输出：受支持的 OpenAI 模型上的 OpenAI [Priority Processing](https://openai.com/api-priority-processing/)（`service_tier: priority`）与 Ultrafast（`service_tier: ultrafast`）、Grok 4.6 上的 xAI Priority Processing，以及 Anthropic [Fast Mode](https://platform.claude.com/docs/en/build-with-claude/fast-mode)（`speed: fast`，仅 Opus 4.8 / Opus 5 / Opus 5.5）。`openai` 与 `openai-api` provider 使用第一方 OpenAI 端点。**默认关闭。**

```yaml
agent:
  service_tier: ""          # "" / normal | fast | priority | ultrafast | auto | cold
  fast_auto_seconds: 60     # window for auto / cold
```

| 模式 | 何时发送 fast 参数 | 用途 |
|------|---------------------------|------------|
| `normal`（默认，`""`） | 从不 | 最省；标准延迟 |
| `fast` | 每个请求 | 每次都想要速度的长交互会话 |
| `auto` | **每个**回合最初 `fast_auto_seconds` 内的请求 | 首答轻快；长工具循环回落到标准计价 |
| `cold` | 同一窗口，但只在会话的**第一个回合**（无此前历史） | 首条引导回复要快，之后标准计价 |

`/fast normal|fast|ultrafast|auto|cold` 为该会话切换模式（`/fast ultra` 是 `ultrafast` 的简写）。在 ChatGPT/Codex 订阅上，只有当你的账户 Codex 模型目录为当前模型列出 Ultrafast 时才提供；否则后端接受该请求并按标准速度服务。加 `--global` 持久化到 `config.yaml`。只运行 `/fast` 显示当前模式。

**成本说明：**两个 provider 都按标准费率的倍数对 fast 请求计费（Anthropic：Opus 5.5 上输入/输出每 MTok $8 / $40，Opus 5 与 Opus 4.8 上 $10 / $50），并与 prompt 缓存计价叠加。Hermes 按 API 在 `usage.speed` 里报告的速度给每个 Anthropic 响应定价。`auto`/`cold` 只把这笔溢价限制在窗口内。Fast 参数只发给支持它们的第一方端点（`api.openai.com` / Codex 订阅、`api.anthropic.com`、`api.x.ai`）；OpenRouter、Nous Portal、Azure、Bedrock 与自定义 `base_url` 路由在任何模式下都不会收到。

**Prompt 缓存：**请求之间只有每个请求的参数变化；system prompt、工具与消息保持逐字节相同。Anthropic 为每种速度保留独立的 prompt 缓存，所以在 Anthropic 上每个 `auto`/`cold` 窗口边界都会按新速度重写对话前缀。对长 Anthropic 会话，`fast` 或 `normal` 只保持一份温热缓存。

Fast mode 的提速体现在每秒输出 token 上，所以长回答获益最多。

当某个 Anthropic 组织对某模型没有 fast-mode 容量时（API 以 fast-mode 容量为 0 回应 fast 请求），Hermes 会在该会话余下时间把该模型切到标准速度并重试请求。

### 网关或代理之后的 fast 档位

只发第一方这条规则是有意为之：fast 档位参数是一条计费指令，Hermes 只把它发给自己知道价目表的那个端点。如果你运行的 OpenAI 兼容 gateway、路由器或代理暴露了自己的优先档位（它自己的 `service_tier` 值，或叫法不同的字段），请经该 provider 的 `extra_body` 请求它，而不是 `agent.service_tier`。[具名自定义 provider](../integrations/providers.md#named-custom-providers) 上的 `extra_body` 会被合并进路由到该端点的**每一个** chat-completions 请求，跨 gateway 回合与 `/fast` 改动存活，并在你 `/model` 切走该 provider 时再次丢弃：

```yaml
providers:
  my-gateway:
    api: https://gateway.example.com/v1
    key_env: MY_GATEWAY_KEY
    default_model: fast-lane-model
    extra_body:
      service_tier: priority     # whatever tier value your gateway documents
```

与 `agent.service_tier` 的差别：该档位对该 provider 始终开启（没有 `auto`/`cold` 窗口），`/fast` 不切换它，且 Hermes 不校验该值——gateway 决定接受什么、按什么计费。

## 工具使用强制

有些模型偶尔把打算做的动作写成文字而不是发工具调用（「我来跑测试……」而不是真的调 terminal）。工具使用强制会注入 system prompt 指引，把模型拉回到真正调用工具上。

```yaml
agent:
  tool_use_enforcement: "auto"   # "auto" | true | false | ["model-substring", ...]
```

| 值 | 行为 |
|-------|----------|
| `"auto"`（默认） | 对匹配的模型启用：`gpt`、`codex`、`gemini`、`gemma`、`grok`、`glm`、`qwen`、`deepseek`、`muse`。对其他所有模型禁用（例如 Claude）。 |
| `true` | 无论模型一律启用。当你注意到当前模型只会描述动作而不执行时有用。 |
| `false` | 无论模型一律禁用。 |
| `["gpt", "codex", "qwen", "llama"]` | 仅当模型名包含所列任一子串（大小写不敏感）时启用。 |

### 它注入什么

启用后，system prompt 可能被加上两层指引：

1. **通用工具使用强制**（所有匹配的模型）—— 指示模型立即发工具调用而不是描述意图、持续工作直到任务完成、绝不以对未来动作的许诺结束一个回合。

2. **Google 运维指引**（仅 Gemini 与 Gemma 模型）—— 简洁、绝对路径、并行工具调用，以及改前先验证的模式。

这些对用户透明，只影响 system prompt。本来就可靠使用工具的模型（如 Claude）不需要这些指引，这就是 `"auto"` 排除它们的原因。

### 什么时候打开

如果你用的模型不在默认自动列表里、又注意到它经常描述自己*会*做什么而不是去做，设 `tool_use_enforcement: true` 或把该模型子串加进列表：

```yaml
agent:
  tool_use_enforcement: ["gpt", "codex", "gemini", "grok", "my-custom-model"]
```

## 执行纪律指引

与工具使用强制分开，Hermes 还会为某几类模型注入一段**执行纪律**块，这些模型家族在评测轨迹中共享一组 agentic 失败模式：用散文而不是代码做算术、外部写入后跳过读回验证、「修复」格式错误的标识符、明明数量对不上却声称完整、以及没验证每条验收标准就宣布「完成」。

```yaml
agent:
  execution_guidance: "auto"   # "auto" | true | false | ["model-substring", ...]
```

| 值 | 行为 |
|-------|----------|
| `"auto"`（默认） | 对匹配的模型启用：`gpt`、`codex`、`grok`、`deepseek`、`kimi`、`qwen`、`glm`、`minimax`、`mimo`、`mistral`、`muse`。 |
| `true` | 无论模型一律启用。 |
| `false` | 无论模型一律禁用。 |
| `["deepseek", "my-custom-model"]` | 仅当模型名包含所列任一子串（大小写不敏感）时启用。 |

注入的块覆盖：

- **工具坚持** —— 持续调用工具直到任务完成*并且*被验证；结论下定之前，对空的、部分的或可疑地过窄的查找结果换更宽或不同的查询重试。
- **强制用工具** —— 算术、哈希、日期、系统状态与文件事实一律来自工具，绝不来自心算。
- **外部写入读回** —— 对外部系统做任何状态变更写入后，在宣称成功之前读回确切目标（工具已确认的内部文件编辑不再重复验证）。
- **计数对账** —— 声明的总数（`total`、`reply_count`、`has_more`）是硬断言；不一致就重新抓取或用程序解析。
- **字面保留** —— 绝不规范化或「修复」不符合既定格式的标识符；一次成功的查找不等于验证了畸形的源 token。
- **验证门控的完成** —— 「完成」意味着每条具名验收标准都已验证，绝不是一个貌似合理的子集。

这道闸门与 `tool_use_enforcement` 相互独立——任一都可以单独开启。指引在会话开始时按模型名选定一次，于是 system prompt 在整个对话期间保持字节稳定（对 prompt 缓存友好）。Gemini/Gemma 被排除在自动列表之外，因为它们会收到更具体的 Google 运维指引；Claude 被排除是因为它不表现出这些失败模式——用 `true` 或子串列表可以主动把任何模型加进来。

## 工具循环护栏

Hermes 会检测 agent 是否卡在无产出的工具调用循环里——同一个工具调用反复失败、同一个工具一次又一次失败，或一个幂等调用返回相同结果而毫无进展。默认情况下它会往工具结果里注入一条**警告**，让模型自我纠正。交互式 CLI、TUI、Desktop 与 ACP 会话保持只警告，因为人可以介入；无人值守的 gateway 与 cron 会话默认启用硬停止。

这个按平台感知的默认可以为无人值守部署关闭，也可以在每个平台上显式启用硬停止：

```yaml
tool_loop_guardrails:
  warnings_enabled: true       # inject warnings into tool results (default: true)
  hard_stop_enabled: false     # also BLOCK the call past the hard-stop threshold (default: false)
  non_interactive_hard_stop_enabled: true  # default hard stops for gateway/cron
  warn_after:
    exact_failure: 2           # identical failing call repeated N times
    same_tool_failure: 3       # same tool failing N times (different args)
    idempotent_no_progress: 2  # same result, no progress, N times
  hard_stop_after:
    exact_failure: 5
    same_tool_failure: 8
    idempotent_no_progress: 5
  loop_caps:
    max_web_searches: 50       # max web_search calls per turn (0 = unlimited)
    max_subagents: 50          # max subagents spawned per turn (0 = unlimited)
```

`hard_stop_enabled` 显式在每个平台启用硬停止。当它保持 `false` 时，`non_interactive_hard_stop_enabled` 仍会为无人值守的 gateway/cron 式平台启用硬停止，同时对 CLI、TUI、Desktop、ACP、subagent 与 `api_server` 运行（有活的父进程或客户端的受监管任务循环）保持只警告。设 `non_interactive_hard_stop_enabled: false` 可让无人值守部署退出。另见 [Docker / 无人值守部署](docker.md)。

硬停止的设计目标是抓住**重放**——同一次调用、毫无变化、其间什么都没发生——而不是合法的迭代：

- **改完再跑从不是循环。** 任何成功的变更调用（`write_file`、`patch`、跑绿的 `terminal`/`execute_code`、浏览器动作、任务/消息/cron 变更）都会为所有仍在计数的失败调用标记进展。下一次完全相同的重试（修完后重跑红的测试、点击后重新截图）开始一条新的连续计数，而不是累积走向阻断。
- **不同的红命令是诊断，不是循环。** 对非零退出码属正常输出的工具（`terminal`、`execute_code`、进程轮询器、`browser_exec`、`web_extract`），`same_tool_failure` 阈值只警告、从不停下。只有参数完全相同的重放且其间无变化，或一串相同结果，才能停住它们。
- **停机结束的是回合，不是会话。** Agent 会回复是哪道护栏触发、为什么；回复「continue」会以全新的按回合计数器恢复。

### 每回合失控循环上限

与上面基于失败的阈值分开，`loop_caps` 为单个 agent 循环（回合）最多能发多少 `web_search` 调用、派生多少 subagent 设硬上限。计数器在每个回合开始时重置，所以合法的多回合会话绝不会挨饿——但一个陷入无界搜索或委派循环的单回合会被停下。这些始终开启、无论 `hard_stop_enabled` 如何都会触发。单个回合发几十次 web 搜索或派生几十个 subagent 已经是病态了，所以默认值很低。到达上限时，越界的工具调用会连同解释性消息被阻断，该回合干净地停止，而不是烧掉剩余预算。把任一值设为 `0` 即彻底关闭该上限。

单次 `delegate_task` 批量会把每个任务计入 `max_subagents`（一批 3 个花掉 3 个），所以上限追踪的是实际派生的 subagent 数，而不是 `delegate_task` 调用次数。

这镜像了 Claude Code 按会话的 WebSearch 与 subagent 上限（v2.1.212），它们同样默认 200 并在 `/clear` 时重置。

### 运行时防停滞守卫

作为上面基于失败的护栏的补充，`agent.stall_guards`（默认 `true`）启用两个保守的运行时守卫来防止浪费回合。其一是**相同调用断路器**：当同一工具被以相同参数连续调用 3 次以上*且*返回相同结果时，会在该工具结果后追加一条简短的单行提示，告诉模型不要重复该调用——在只警告的会话里它从不阻断调用，且合法可重复的轮询器（`process_manage`、`*_get_result`、`*_poll`）豁免。当硬停止生效时（显式 `hard_stop_enabled`，或无人值守的 gateway/cron 平台），同一串连续相同调用达到 `hard_stop_after.idempotent_no_progress` 后也会变成硬停止——适用于**任何**工具，不只是 `idempotent_no_progress` 护栏追踪的只读工具——于是重放同一次成功的 `terminal` 或 `skill_view` 调用的模型会被停下，而不是耗光迭代预算（`identical_call_streak_halt`）。

其二是**继续意图恢复**：当模型以没有任何工具调用结束回合、但其简短回复的尾声在预告某个动作（「Let me now update the file…」）时，Hermes 会经同一套有界继续机制重新提示它行动（每回合最多 2 次重新提示）。两者都对缓存安全（提示在构造结果时添加，绝不事后追加），且可以一起关闭：

```yaml
agent:
  stall_guards: false
```

同一道闸门还启用**结果引用存根**：当重发的相同工具调用返回逐字节相同的新结果时，重复的载荷以一个指向先前结果的简短引用存根进入上下文（工具名、`tool_call_id`、参数摘要，以及——若第一个结果已持久化到磁盘——其溢出路径），而不是重复完整输出。工具每次仍会执行，所以轮询语义得以保留：变化的结果始终完整流过。小于 512 字符的结果、错误结果与多模态结果从不存根化，而轮询器*会*存根化（一次未变化的轮询恰恰就是重复载荷不携带任何信息的情形）。

### 回合存活看门狗

`agent.turn_liveness` 约束一个对话回合最多可以**没有任何可观测进展**多久，超过 Hermes 就强制恢复。看门狗以活动时钟为键（即给 API 等待、流式 token 与工具心跳盖戳的同一信号——租约续期从不计数），于是一个在中途默默卡死的回合（观测到的 issue #95548：没有工具执行、没有 API 调用、没有错误，但会话无限期保持「busy」）会被高调暴露、被打断以便以可重试的中断回合展开，而——当中断无法解开卡死时——它的持久回合租约会停止续期，让陈旧回合清理能收回该会话，而不是让它一直挂着直到进程被杀。

```yaml
agent:
  turn_liveness:
    timeout_s: 600.0   # idle bound; <= 0 disables the watchdog
    poll_s: 15.0        # sampling interval (seconds)
```

合法的慢工作不受罚：流式响应、工具心跳（工具运行期间每 30 秒一次）与审批等待都会持续拨动该时钟，所以只有在整个期限内进展为*零*的回合才触发看门狗。非法值（拼写错误、`NaN`、`Inf`、非正的 `poll_s`）记一条警告并回退默认——它们绝不让启动崩溃，也不静默禁用看门狗。被触发的中止在开始恢复时报告该停滞，并且只在中断真正提交之后才发布确定的中止/租约停止结果。

## TTS 配置

```yaml
tts:
  provider: "edge"              # "edge" | "elevenlabs" | "openai" | "minimax" | "mistral" | "gemini" | "xai" | "neutts" | "kittentts" | "piper" | "deepinfra"
  speed: 1.0                    # Global speed multiplier (fallback for all providers)
  keep_warm_seconds: 60         # Keep a local engine loaded this long after the last speech toggle turns off (0 = unload at once)
  edge:
    voice: "en-US-AriaNeural"   # 322 voices, 74 languages
    speed: 1.0                  # Speed multiplier (converted to rate percentage, e.g. 1.5 → +50%)
  elevenlabs:
    voice_id: "pNInz6obpgDQGcFmaJgB"
    model_id: "eleven_multilingual_v2"
  openai:
    model: "gpt-4o-mini-tts"
    voice: "alloy"              # alloy, echo, fable, onyx, nova, shimmer
    speed: 1.0                  # Speed multiplier (clamped to 0.25–4.0 by the API)
    base_url: "https://api.openai.com/v1"  # Override for OpenAI-compatible TTS endpoints
    pcm_sample_rate: 24000      # Streaming PCM rate; overridden by the endpoint's X-Audio-Sample-Rate header
  minimax:
    speed: 1.0                  # Speech speed multiplier
    # base_url: ""              # Optional: override for OpenAI-compatible TTS endpoints
  mistral:
    model: "voxtral-mini-tts-2603"
    voice_id: "c69964a6-ab8b-4f8a-9465-ec0925096ec8"  # Paul - Neutral (default)
  gemini:
    model: "gemini-2.5-flash-preview-tts"   # or gemini-3.1-flash-tts-preview
    voice: "Kore"               # 30 prebuilt voices: Zephyr, Puck, Kore, Enceladus, etc.
    audio_tags: false           # Hidden Gemini 3.1 TTS audio-tag insertion
    persona_prompt_file: ""      # Optional Markdown/text file with Gemini voice direction
  xai:
    voice_id: "eve"             # xAI TTS voice
    language: "en"              # ISO 639-1
    sample_rate: 24000
    bit_rate: 128000            # MP3 bitrate
    # base_url: "https://api.x.ai/v1"
  neutts:
    ref_audio: ''
    ref_text: ''
    model: neuphonic/neutts-air-q4-gguf
    device: cpu
```

它同时控制 `text_to_speech` 工具与语音模式下的口头回复（CLI 或消息 gateway 里的 `/voice tts`）。

**速度回退层级：**provider 专属速度（例如 `tts.edge.speed`）→ 全局 `tts.speed` → `1.0` 默认。设全局 `tts.speed` 可让所有 provider 统一速度，或按 provider 覆盖做细粒度控制。

## 显示设置

```yaml
display:
  tool_progress: all      # off | new | all | verbose
  tool_progress_command: false  # Enable /verbose slash command in messaging gateway
  focus_view: false       # CLI focus view (/focus) — reduced output, display-only
  platforms: {}           # Per-platform display overrides (see below)
  interim_assistant_messages: true  # Gateway: send natural mid-turn assistant updates as separate messages
  suppress_warning_notifications: false  # Opt-in: hide automatic warning/diagnostic notices (see messaging guide)
  show_commentary: true   # Codex models: deliver commentary-channel progress narration as visible mid-turn updates
  skin: default           # Built-in or custom CLI skin (see user-guide/features/skins)
  personality: ""         # Legacy cosmetic field still surfaced in some summaries
  compact: false          # Compact output mode (less whitespace)
  cli_multiline_shortcuts: true  # CLI: Ctrl+J, \ + Enter, and supported Shift+Enter insert newlines (false = legacy c-j submit fallback)
  resume_display: full    # full (show previous messages on resume) | minimal (one-liner only)
  bell_on_complete: false # Play terminal bell when agent finishes (great for long tasks)
  bell_on_prompt: false   # Play terminal bell when a blocking prompt opens (clarify, approval, sudo password, secret capture) — works over SSH
  # Both bell flags also emit an OSC 9 desktop notification (Ghostty, iTerm2, Kitty, WezTerm raise an OS
  # notification; other terminals ignore it) and, inside Warp (TERM_PROGRAM=WarpTerminal with the CLI-agent
  # protocol advertised), a warp://cli-agent OSC 777 event (`stop` on completion, `permission_request` on
  # blocking prompts) so Warp's tab status and notification mailbox track Hermes. No extra keys needed.
  show_reasoning: true    # Show model reasoning/thinking above each response (default: true; toggle with /reasoning show|hide)
  streaming: false        # Stream tokens to terminal as they arrive (real-time output)
  show_cost: false        # Show estimated $ cost in the CLI status bar
  vim_mode: false         # CLI only: vi/vim keybindings in the input composer (Esc → NORMAL, i → INSERT). The live NORMAL/INSERT/REPLACE mode shows at the right of the status bar. Config-only, read at startup.
  timestamps: false       # When true, prefixes user and assistant labels with timestamps in the CLI / TUI transcript
  timestamp_format: "%H:%M"  # strftime format for those timestamps (e.g. "%b-%d %H:%M" for month-day)
  tool_preview_length: 0  # Max chars for tool call previews (0 = no limit, show full paths/commands)
  turn_summary: true      # CLI only: print a one-line post-turn accounting footer after each interactive turn
  spinner_token_flow: true # CLI only: append live cumulative turn tokens to the spinner timer
  runtime_footer:         # Gateway: append a runtime-context footer to final replies
    enabled: false
    fields: ["model", "context_pct", "cwd"]
  status_bar:             # CLI/TUI: choose which status-bar fields are visible
    fields: []            # empty = show the default set; see below
  file_mutation_verifier: true    # Append an advisory footer when write_file/patch calls failed this turn
  credits_notices: true   # Nous credits status-bar notices (usage bands, grant-spent, depleted). false = silence them; /usage still works
  cli_rebuild_scrollback_on_redraw: false  # Classic CLI: also wipe terminal scrollback (CSI 3J) on /redraw / Ctrl+L / width-change resize recovery. Enable when a terminal/tmux stack stamps stale prompt chrome into scrollback on maximize/restore.
  language: en            # UI language for static messages (approval prompts, some gateway replies). en | zh | zh-hant | ja | de | es | fr | tr | uk | af | ko | it | ga | pt | ru | hu
```

### 每回合汇总与 spinner token 流

`display.turn_summary`（默认 `true`）在每个**交互式 CLI** 回合之后打印一行暗色的结算行，总结该回合实际做了什么：

```
⋯ 12.4s · edited 2 files +18 -3 · read 4 files · ran 3 commands
```

这份统计来自 CLI 本来就收到的工具进度流，因此不花额外成本。细节：

- 墙钟时间是该回合的真实时长（超过一分钟显示 `2m05s`）。
- 工具调用按动词分组（`edited`、`read`、`ran`、`searched`……），复数形式正确；没有精选动词的插件/MCP 工具归并为 `called N tools`。
- `+X -Y` 行差异只在工具结果本身已报告 diff 时出现（目前是 `patch`）。Hermes 从不为算它们而调用 git，所以一次 `write_file` 编辑会计数但没有差异。
- **失败的工具调用不计入** —— 一次被拒绝的写入绝不会渲染成成功的编辑（互补的警告见[文件变更校验器](#文件变更校验器)）。
- 长回合最多显示四个动词段加一条 `+N more` 尾巴，保证这行永不换行。
- 没有工具调用的快回合什么也不打印。

`display.spinner_token_flow`（默认 `true`）把当前回合累计的输出 token 追加到 CLI spinner 的实时计时器上：

```
  ⚡ Reading cli.py  (  2.3s · ↓ 1.2k tok)
```

计数按回合（会话总量在回合开始时归零基线），随该回合每次 API 调用报告用量而更新。第一份用量报告到达之前什么都不渲染，所以你绝不会看到误导性的 `↓ 0 tok`。

这两个键都只影响显示、且只作用于 CLI：安静模式下、`display.tool_progress` 为 `off` 时、单次查询/`-Q` 批量运行中，以及 gateway/消息界面上（那些改用 `display.runtime_footer`）都会被抑制。把任一键设为 `false` 即关闭。

### 文件变更校验器

当 `display.file_mutation_verifier` 为 `true`（默认）时，只要本回合中某次 `write_file` 或 `patch` 调用失败，且目标文件在其后既未成功写入（无论路径是什么写法）、回合结束前也未以其他方式在磁盘上发生变化，Hermes 就会在助手的最终响应后追加一行提示。这抓住了「一批并行 patch、一半静默失败、模型总结成功」这类过度声称，而无需你在每次编辑后手工跑 `git status`。

示例尾注：

```
⚠️ File-mutation verifier: 3 file edit(s) FAILED this turn despite any wording above that may suggest otherwise. Run `git status` or `read_file` to confirm what actually landed.
  • concepts/automatic-organization.md — [patch] Could not find match for old_string
  • concepts/lora.md — [patch] Could not find match for old_string
  • concepts/rag-pipeline.md — [patch] Could not find match for old_string
```

设 `file_mutation_verifier: false`（或 `HERMES_FILE_MUTATION_VERIFIER=0`）可抑制该尾注。校验器只在回合结束时仍有真实失败未处理时才触发——一个模型在同一回合内重试失败的 patch 并成功，不会为该文件触发它。

**相信校验器胜过相信模型的总结。** 该尾注意味着所列的编辑调用**失败**了，且 Hermes 没看到这些文件之后有任何变化，即使助手的收尾消息说任务已完成。它只追踪 `write_file`/`patch` 回执加回合结束时的修改时间检查，所以请跑 `git status` 或 `read_file` 确认到底落地了什么。常见原因：

- **写入被拒** —— 路径在凭据黑名单上，或在 `HERMES_WRITE_SAFE_ROOT` 之外（见[文件写入安全](./security.md#file-write-safety)）
- **Patch 不匹配** —— `old_string` 与磁盘上的文件对不上
- **语法闸门** —— 候选内容在写入前没通过 JSON/YAML/TOML 校验

写入被阻断时的示例尾注：

```
⚠️ File-mutation verifier: 2 file edit(s) FAILED this turn despite any wording above that may suggest otherwise. Run `git status` or `read_file` to confirm what actually landed.
  • ~/.hermes/cron/jobs.json — [patch] Write denied: '…' is outside HERMES_WRITE_SAFE_ROOT (/path/to/project)
  • ~/.hermes/scripts/monitor.py — [write_file] Write denied: '…' is outside HERMES_WRITE_SAFE_ROOT (/path/to/project)
```

如果对 Hermes 状态（`~/.hermes/` 下的 cron 任务、skill、脚本）的写入失败，请检查环境里是否设了 `HERMES_WRITE_SAFE_ROOT`。cron 改动请用 `cronjob_manage` 工具或 `hermes cron edit`，而不是直接 patch `jobs.json`。

### 静态消息的 UI 语言

`display.language` 设置翻译一小批静态的面向用户消息——CLI 审批提示、少数 gateway 斜杠命令回复（例如重启 drain 提示、「approval expired」、「goal cleared」）。它**不**翻译 agent 响应、日志行、工具输出、错误回溯或斜杠命令描述——那些保持英文。如果你想让 agent 本身用另一种语言回复，直接在 prompt 或 system 消息里告诉它。

内置值：`en`（默认）、`zh`（简体中文）、`zh-hant`（繁体中文）、`ja`（日语）、`de`（德语）、`es`（西班牙语）、`fr`（法语）、`tr`（土耳其语）、`uk`（乌克兰语）、`af`（南非荷兰语）、`ko`（韩语）、`it`（意大利语）、`ga`（爱尔兰语）、`pt`（葡萄牙语）、`ru`（俄语）、`hu`（匈牙利语）、`ar`（阿拉伯语）。

这个列表是**可插拔的**：[language pack](features/language-packs.md) 插件（`provides_locales`）或局部的 `<HERMES_HOME>/locales/<lang>.yaml` 覆盖层可以新增语言或改写措辞，`hermes config set display.language <id>` 接受内置目录、你的覆盖层或已安装语言包提供的任何 id。未知 id 会被拒绝并列出可用语言；运行时解析不出的值回退到英文。

也可以用 `HERMES_LANGUAGE` 环境变量按会话设置，它覆盖配置值。

```yaml
display:
  language: zh   # CLI approval prompts appear in Chinese
```

| 模式 | 你看到什么 |
|------|-------------|
| `off` | 静默 —— 只有最终响应 |
| `new` | 只在工具变化时显示指示 |
| `all` | 每次工具调用带简短预览（默认） |
| `verbose` | 完整参数、结果与调试日志 |

在 CLI 里用 `/verbose` 循环这些模式。要在消息平台（Telegram、Discord、Slack 等）里用 `/verbose`，在上面的 `display` 段设 `tool_progress_command: true`。该命令随后会循环模式并保存到配置。

工具进度需要一个能安全显示进度更新的 gateway adapter。不支持消息编辑的平台（含 Signal）即使 `/verbose` 保存了非 `off` 模式也会抑制工具进度气泡。

`off` 只隐藏工具调用的*外壳*。在 Desktop 应用与 TUI 里有自己界面的应用状态——任务列表（`todo_list`）、subagent 进度、clarify 问题与 MCP 同意卡片——不受该设置影响，照常流动。

### Focus view（`/focus`，CLI + TUI）

`display.focus_view: true` 启用 **focus view**——一种精简输出的显示模式，适用于你只要答案、不要逐招播报的时候。它是同一套 `tool_progress` 机制之上的一层薄皮，而不是第二条抑制路径：

- 打开它会把 `tool_progress` 钉为 `off`，并把先前的模式存进 `display.focus_saved_tool_progress`；
- `/focus off` 会精确恢复那个模式，于是 `/verbose verbose` 的设置经一个来回仍然存活；
- 每个完成的回合以一行暗色恢复行收尾——`⋯ 7 tool lines hidden · /focus off to show`——按你的*focus 之前*模式计数，所以它绝不会声称隐藏了你本来就已关掉的行；
- 状态栏上有一个常驻的 `◉ focus` 徽标（prompt_toolkit CLI 与 Ink TUI 都有），精简模式绝不会不可见；
- focus 开着时循环 `/verbose` 会把模式交还给 `/verbose` 并清除徽标。

Focus view **只影响显示**。它从不编辑对话历史、system prompt、工具 schema 或任何请求载荷——被隐藏的细节只是在屏幕上被抑制，从不丢弃，prompt 缓存完全不受影响。

### 状态栏字段选择（CLI/TUI）

CLI/TUI 底部的交互式状态栏显示模型、上下文用量、压缩次数、后台活动计数器、计时器与模式徽标。`display.status_bar.fields` 从中挑选可见的字段——对极简栏（只要模型 + 时长）或把可选的会话 token 总量显示出来很有用：

```yaml
display:
  status_bar:
    fields: ["model", "duration", "total_tokens"]   # visibility only; built-in order is preserved
```

支持的字段：`model`、`context_detail`（已用/总 token）、`context_pct`（百分比 + 量表）、`cache_hit`（prompt 缓存命中率——模型切换与压缩时重置）、`latency`（滚动平均 API 延迟，最近 10 次调用）、`tps`（滚动输出 token/秒，最近 10 次调用）、`compressions`、`bg_tasks`、`bg_processes`、`bg_subagents`、`goal`、`git_branch`（⎇ 工作目录当前 git 分支——仅可选，默认从不显示；detached HEAD 显示缩写提交）、`duration`、`prompt_elapsed`、`idle_since`、`focus`、`yolo`、`stash`、`battery`、`title`（右对齐的会话徽标），以及 `total_tokens`（会话 Σ——仅可选，默认从不显示）。

说明：

- 空列表（默认）保持标准集合——除 `total_tokens` 与 `git_branch` 外的全部。
- 配置控制的是**可见性，不是顺序**；字段按内置位置渲染。
- 窄终端仍会丢弃仅宽模式的字段（`context_detail`、`cache_hit`、`latency`、`tps`、`prompt_elapsed`、`idle_since`），无论配置如何（`cache_hit` 在中等 ≥52 列档位也会显示）。
- 在记录到 API 调用之前 `latency`/`tps` 保持隐藏（例如 Codex app-server 后端不报告延迟）。
- 这里 `battery` 与 `title` 的可见性与它们自己的开关（`/battery`、`/title`）组合——两者都打开该段才显示。
- 同一个键还过滤 **Ink TUI** 的状态栏（`hermes tui`），在那里 `cache_hit`、`latency`、`tps` 分别作为按宽度预算的尾段（◎ / ◷ / ↑）显示在 ≥96/104/110 列的终端上。
- 仅影响显示：对 prompt 缓存与请求载荷无作用。改动在下一个会话启动时生效。

### 运行时元数据尾注（仅 gateway）

当 `display.runtime_footer.enabled: true` 时，Hermes 会给每个 gateway 回合的**最终**消息追加一个小的运行时上下文尾注。当前尾注可以显示模型、上下文窗口百分比与当前工作目录。默认关闭；如果你们团队想让每条回复都带上这份出处，就按 gateway 选择加入。

```yaml
display:
  runtime_footer:
    enabled: true
    fields: ["model", "context_pct", "cwd"]   # order shown; drop any to hide
```

支持的字段：

| 字段 | 渲染 | 示例 |
| --- | --- | --- |
| `model` | 裸模型 id，去掉厂商前缀 | `gpt-5.4` |
| `context_pct` | 上次调用的上下文占用百分比 | `5%` |
| `latency` | 该回合的墙钟时长 | `22s`、`1m05s` |
| `served_model` | 实际作答的模型（与你配置的不同时）：路由代理在其 `x-litellm-model-id`（或 `x-litellm-model-api-base`）响应头里报告的部署，或 Hermes 该回合切换到的 fallback 模型 | `hermes-router → gpt-4o-2024-11-20` |
| `cwd` | 相对 home 的工作目录 | `~` |

默认字段集是 `["model", "context_pct", "cwd"]`。`latency` 与 `served_model` 是可选——加进 `fields` 才用。当实际服务的模型就是配置的那个（或代理不发该头）时，`served_model` 不渲染任何东西，所以在路由代理或活跃 fallback 之后，它正是让这次切换可见的字段。数据不可用的字段被静默跳过，而不是渲染一个空位。

`/footer` 斜杠命令可在任何会话里于运行时切换它。

追加到 Telegram/Discord/Slack 回复的尾注示例：

```
— claude-opus-4.7 · 12 tool calls · 2m 14s · $0.042
```

只有回合的**最终**消息带尾注；中途更新保持干净。

### 按平台的进度覆盖

不同平台的啰嗦度需求不同。用 `display.platforms` 按平台设置模式：

```yaml
display:
  tool_progress: all          # global default
  platforms:
    signal:
      tool_progress: 'off'    # Signal cannot currently display tool-progress bubbles
    telegram:
      tool_progress: verbose  # detailed progress on Telegram
    slack:
      tool_progress: 'off'    # quiet in shared Slack workspace
```

从 CLI 请用规范路径——`hermes config set display.platforms.telegram.streaming false`。简写 `hermes config set platforms.telegram.streaming false` 也会被接受：因为按平台的*显示*设置（`streaming`、`show_reasoning`、`tool_progress`……）只从 `display.platforms` 读取，`config set`/`get`/`unset` 会把该简写重定向到规范键并打印一条说明。顶层 `platforms.<name>` 块下的连接键（`token`、`enabled`、`reply_to_mode`、`extra`）不重定向。写在嵌套前缀下（`hermes config set gateway.platforms.telegram.enabled true`）会被重定向到顶层 `platforms.telegram.enabled` 并给出说明：gateway 两个块都读，但共享键上顶层胜出，所以嵌套写入会被既有的顶层值悄悄遮蔽。

没有覆盖的平台回退到全局 `tool_progress` 值。合法的平台键：`telegram`、`discord`、`slack`、`signal`、`whatsapp`、`matrix`、`mattermost`、`email`、`sms`、`dingtalk`、`feishu`、`wecom`、`weixin`、`bluebubbles`、`qqbot`，加上任何插件平台的名字（例如 Home Assistant 插件的 `homeassistant`）。遗留键 `display.tool_progress_overrides` 仍会加载以保持向后兼容，但已废弃，首次加载时迁移进 `display.platforms`。

Signal 之所以列为合法平台键，是因为该设置可以按平台保存，但当前的 Signal adapter 无法编辑已发送的消息、也不渲染工具进度气泡。请把 Signal 的 `tool_progress` 保持为 `off`；如果你想实时盯每次工具调用，请用 CLI 或支持编辑的消息平台。

`interim_assistant_messages` 仅限 gateway。启用后，Hermes 把完成的中途助手更新作为独立聊天消息发送。它独立于 `tool_progress`，也不需要 gateway 流式。

`show_commentary`（默认 `true`）控制 Codex Responses 模型的评论频道——这些模型在其私有推理之外产出的那段润色过的进度叙述。启用时，每条完成的评论消息作为可见的中途更新投递（在 gateway 上这还需要 `interim_assistant_messages`）。如果额外的叙述让你烦，设为 `false`：评论于是回落到推理频道，且只在 `show_reasoning` 打开时显示。

## 隐私

```yaml
privacy:
  redact_pii: false  # Strip PII from LLM context (gateway only)
```

`redact_pii` 为 `true` 时，gateway 会在支持的平台上把系统提示发给 LLM 之前遮蔽其中的个人可识别信息：

| 字段 | 处理 |
|-------|-----------|
| 电话号码（WhatsApp/Signal 上的用户 ID） | 哈希为 `user_<12-char-sha256>` |
| 用户 ID | 哈希为 `user_<12-char-sha256>` |
| 聊天 ID | 数字部分哈希，平台前缀保留（`telegram:<hash>`） |
| 主频道 ID | 数字部分哈希 |
| 用户名 | **不受影响**（用户自选、公开可见） |

**平台支持：**遮蔽适用于 WhatsApp、Signal 与 Telegram。Discord 与 Slack 被排除，因为它们的 mention 系统（`<@user_id>`）需要 LLM 上下文里的真实 ID。

哈希是确定性的——同一用户永远映射到同一哈希，模型因此仍能在群聊里区分不同用户。路由与投递内部使用原始值。

### OpenAI Codex 请求标识

OpenAI 要求第三方 Codex harness 自报身份。发往官方 Codex 端点的 ChatGPT 认证请求会自动发送 `originator: hermes-agent` 与 `User-Agent: HermesAgent/<version>`。既有的 ChatGPT 账户头被保留。不会发送额外的 prompt 内容或遥测请求。直连 OpenAI API 的请求与自定义代理端点不受影响。

## 语音转文字（STT）

```yaml
stt:
  enabled: true                # Auto-transcribe inbound voice messages (default: true)
  echo_transcripts: true       # Post raw transcripts back to the chat as 🎙️ "..." (default: true)
  provider: "local"            # "local" | "groq" | "openai" | "mistral" | "xai" | "elevenlabs" | "deepinfra" | ...
  language: "en"               # GLOBAL language hint for every provider (per-provider language wins); set "" for auto-detect
  streaming: false             # live partial text while you speak (openai, xai, elevenlabs); see Voice Mode > Live transcription
  cloud_trim_silence: true     # trim long pauses with ffmpeg before uploading to a cloud provider (default: true)
  cloud_trim_threshold_db: -40 # audio quieter than this counts as silence
  cloud_trim_keep_ms: 300      # how much of each pause survives the trim (keeps natural pacing)
  # prompt: "Hermes, Teknium, Nous Research, kanban"   # Static vocabulary hint (see below)
  local:
    model: "base"              # tiny, base, small, medium, large-v3, turbo
    language: ""               # per-provider override of stt.language
    initial_prompt: ""         # optional whisper prompt to bias vocabulary/script (e.g. Simplified Chinese)
    vad: true                  # Silero VAD filter (default on) — silence never reaches whisper; false = raw behavior (music/ambient)
    vad_min_silence_ms: 500    # min silence (ms) that splits speech chunks when vad is on
    no_speech_prob_threshold: 0.6  # drop a segment only when no_speech_prob > this...
    logprob_threshold: -1.0        # ...AND avg_logprob < this (both must hit — quiet real speech survives)
    unload_after_idle_seconds: 0   # 0=never unload (default); e.g. 300 = release the model after 5min idle
  groq:
    language: ""               # per-provider override of stt.language
  openai:
    model: "whisper-1"         # whisper-1 | gpt-4o-mini-transcribe | gpt-4o-transcribe | gpt-transcribe
    language: ""               # per-provider override of stt.language
    timeout: 60                # seconds per transcription request; raise for self-hosted model cold starts
    max_retries: 1             # SDK transport retries (connection errors, 408/409/429/5xx); 0 = single attempt
  xai:
    model: "grok-voice-transcribe-2.0"  # or grok-voice-transcribe-1.0; sent on every request
    language: ""               # per-provider override of stt.language
  # model: "whisper-1"         # Legacy fallback key still respected
```

**每个** STT provider（local、groq、openai、mistral、xai、elevenlabs、deepinfra、command 型 provider 与插件）的语言解析都相同：`stt.<provider>.language` → `stt.language` → `HERMES_LOCAL_STT_LANGUAGE` 环境变量 → provider 自动探测。**默认值是 `stt.language: "en"`**——Whisper 的自动探测经常误判短音频或带口音的片段，表现就是语音消息被转成错误语言。非英语使用者应当把自己的语言代码一次性设进 `stt.language`（例如 `"es"`、`"zh"`、`"uk"`）；多语混用时设为 `""` 恢复自动探测。

`stt.openai.timeout` 与 `stt.openai.max_retries` 塑形 `openai`、`groq`、`deepinfra` 三个 provider 共用的 OpenAI-SDK 转写客户端（目前还没有按 provider 的兄弟键，SDK 也不读这些环境变量）。默认值是 `60` / `1` 而不是此前固定的 30 秒 / 不重试，因为自托管的 OpenAI 兼容端点在首个请求上加载模型可能超过 30 秒，过去那条语音消息就直接丢了。取舍是：一个不可达的后端现在会占用一条语音消息至多两次尝试 × 超时时长，Hermes 才放弃；要旧形态请设 `timeout: 30` 与 `max_retries: 0`。

当 gateway 应当为 agent 转写语音消息、但绝不能把原始转写回贴到聊天里时（例如面向客户的 WhatsApp 机器人），设 `stt.echo_transcripts: false`。

Provider 行为：

- `local` 用跑在你机器上的 `faster-whisper`。单独安装：`python -c "import pm; pm.sync_venv(['stt-whisper'], explicit=True)"`。静默幻觉加固默认开启：Silero VAD 过滤器保证静默/噪音到不了 Whisper，跨窗口条件化被关闭，模型自己标为「大概不是语音」*且*置信度低的片段被丢弃。要以原始行为转写非语音音频（音乐、环境声）设 `stt.local.vad: false`。模型在两条语音消息之间保持加载以实现低延迟转写；设 `stt.local.unload_after_idle_seconds`（例如 5 分钟用 `300`）可在空闲时自动释放模型。这在 CUDA 主机上释放 GPU 显存（本地 LLM 与之共用 GPU 时的主要收益）；在 CPU 上内存变得可被进程复用，不过操作系统可见的占用可能要等进程别处需要空间时才缩小。下一条语音消息会透明地重新加载模型。
- `groq` 用 Groq 的 Whisper 兼容端点，读取 `GROQ_API_KEY`。传 `stt.groq.language`（或全局 `HERMES_LOCAL_STT_LANGUAGE` 环境变量）可跳过自动探测、降低延迟。
- `openai` 用 OpenAI 语音 API，读取 `VOICE_TOOLS_OPENAI_KEY`。

装了 `ffmpeg` 时，云端 provider（groq、openai、mistral、xai、elevenlabs、deepinfra）默认获得一次**上传前静默裁剪**：语音消息里的长停顿在客户端先折叠掉，每个停顿保留 `cloud_trim_keep_ms`，让自然节奏得以留存。更短的音频意味着更快的上传、更低的按音频分钟计费、以及远程模型更少的静默幻觉。短于 12 秒的片段完全跳过裁剪（那里的节省无关紧要，而且好几个 provider 反正有按请求最低计费）。裁剪是尽力而为——ffmpeg 缺失、裁剪失败、片段基本全是静默、或裁剪省不到约 10% 时，原文件原样上传。设 `stt.cloud_trim_silence: false` 可始终上传原文件（例如经云端 provider 转写音乐或环境声时）。command 型与插件型 provider 从不拿到被裁剪的音频。

超过 provider 单请求上传上限的录音（OpenAI/Groq/DeepInfra 25 MB，Mistral 与 xAI 500 MB，ElevenLabs 约 5 GB，外加 OpenAI `gpt-4o-transcribe` 系列与 `whisper-1` 的按模型长度限制）会被重编码为紧凑的 AAC，若仍然太大就在停顿处分段、逐段转写。见[长录音与上传限制](features/voice-mode.md#long-recordings-and-upload-limits)。

显式选择的 `stt.provider` 被严格执行——它不可用时，转写会报错并提示运行 `hermes tools`，而不是切换 provider。只有在从未选择过任何 provider 时，Hermes 才按此顺序自动探测：`local` → `groq` → `openai`。

Groq 与 OpenAI 的模型覆盖由环境变量驱动：

```bash
STT_GROQ_MODEL=whisper-large-v3-turbo
STT_OPENAI_MODEL=whisper-1
STT_XAI_MODEL=grok-voice-transcribe-2.0
GROQ_BASE_URL=https://api.groq.com/openai/v1
STT_OPENAI_BASE_URL=https://api.openai.com/v1
```

### 转写 prompt（词汇提示）

`stt.prompt` 是传给支持 prompt 的 STT 后端的可选静态提示。用来放 Whisper 系模型容易听错的专有名词、产品名与行话：

```yaml
stt:
  provider: "local"
  prompt: "Hermes, Teknium, Nous Research, kanban, Ollama"
```

**组合方式。** 配置值是基底。注册了 [`pre_transcription`](./features/hooks.md#pre_transcription) hook 的插件在其上做变更，按字段后写者胜。多个插件的提示按确定性方式组合：插件发现按插件 id 排序加载插件，每个插件的回调按其自身注册顺序运行，因此同一组插件总产生同一个最终 prompt。hook 对 `prompt` 返回空字符串会为该请求清掉配置里的 prompt。hook 还可以覆盖 `language` 与 `model`；`file_path` 是只读的，任何改动尝试都会被记录并丢弃。没有注册 hook 且未设 `stt.prompt` 时，发出的请求与以往版本相同。

**Provider 支持。**

| Provider | Prompt 参数 | 行为 |
|----------|-----------------|----------|
| `local`（faster-whisper） | `initial_prompt` | 原样转发给本地模型 |
| `openai` | `prompt` | 在转写请求中原样转发 |
| `groq` | `prompt` | 在转写请求中原样转发 |
| `mistral` | `prompt` | 在转写请求中原样转发 |
| `deepinfra` | `prompt` | OpenAI 兼容路径，原样转发 |
| `xai` | 不支持 | 记一条 DEBUG 日志，请求不带 prompt 继续 |
| `elevenlabs` | 不支持 | 记一条 DEBUG 日志，请求不带 prompt 继续 |
| `local_command` | 不支持 | 记一条 DEBUG 日志，请求不带 prompt 继续 |
| `stt.providers.<name>` 且 `type: command` | 不支持 | 记一条 DEBUG 日志，请求不带 prompt 继续 |
| 插件注册的 provider | `transcribe(**extra)` kwargs 里的 `prompt` | 只在设置了 prompt 时才发送，所以早于该键的 provider 看到的调用不变 |

**长度。** Whisper 系模型只以最后约 224 个 prompt token 为条件。对 whisper 系后端（`local`、`openai`、`groq`、`deepinfra`），Hermes 在客户端强制这个上限：过长的最终 prompt 会被截到尾部并记一条警告——请求绝不会因 prompt 长度而报错。其他后端（`mistral`、插件型 provider）原样收到 prompt，自行负责校验。无论如何，提示都要短而具体。

:::warning Prompt 会随你的音频一起上传
最终 prompt 会与音频文件一起发给配置的 STT provider。别把机密与会话派生的上下文放进 `stt.prompt` 或 `pre_transcription` hook 返回的任何内容里，尤其当 provider 是托管 API 而不是本地 `faster-whisper` 时。
:::

## 语音模式（CLI）

```yaml
voice:
  record_key: "ctrl+b"         # Push-to-talk key inside the CLI
  max_recording_seconds: 120    # Hard stop for long recordings
  auto_tts: false               # Enable spoken replies automatically when /voice on
  beep_enabled: true            # Play record start/stop beeps in CLI voice mode
  beep_volume: 0.3              # Beep amplitude (0.0-1.0); raise it on quiet systems / headphones
  silence_threshold: 200        # RMS threshold for speech detection
  silence_duration: 3.0         # Seconds of silence before auto-stop
```

在 CLI 里用 `/voice on` 开启麦克风模式，用 `record_key` 开始/停止录音，用 `/voice tts` 切换语音回复。端到端设置与各平台行为见 [Voice Mode](./features/voice-mode.md)。

## 流式输出

把 token 边到达边流到终端或消息平台，而不是等完整响应。

### CLI 流式

```yaml
display:
  streaming: true         # Stream tokens to terminal in real-time
  show_reasoning: true    # Also stream reasoning/thinking tokens (optional)
```

启用后，响应在一个流式框内逐 token 出现。工具调用仍被静默捕获。如果 provider 不支持流式，会自动回退到普通显示。

### Gateway 流式（Telegram、Discord、Slack）

```yaml
streaming:
  enabled: true           # Enable progressive message editing (default: false)
  transport: auto         # "auto" (default) | "edit" (progressive message editing) | "off"
  edit_interval: 0.8      # Seconds between message edits (default: 0.8)
  buffer_threshold: 24    # Characters before forcing an edit flush (default: 24)
  cursor: " ▉"            # Cursor shown during streaming
  fresh_final_after_seconds: 0    # Opt in to fresh final (Telegram) when preview is this old
```

启用后，bot 在第一个 token 时发一条消息，随后随更多 token 到达逐步编辑它。不支持消息编辑的平台（Signal、Email、Home Assistant）在首次尝试时被自动探测——该会话会优雅地关闭流式，而不是刷出一堆消息。

要没有渐进 token 编辑的、独立而自然的中途助手更新，请设 `display.interim_assistant_messages: true`。

**溢出处理：**如果流式文本超过平台的消息长度上限（约 4096 字符），当前消息被定稿并自动开始新的一条。

**Fresh final（Telegram）：**Telegram 的 `editMessageText` 保留原消息时间戳，于是一条长跑的流式回复即使完成后仍显示第一个 token 的时间戳。设 `fresh_final_after_seconds > 0` 可选择把过旧的预览作为全新最终消息投递，并尽力删除预览。默认 `0`，即始终就地定稿流式回复，避免在同时显示两种操作的客户端上出现短暂的重复消息/删除序列。

:::note 按平台的流式默认值
总开关 `streaming.enabled` 默认为 `false`——在你打开之前什么都不会流。一旦启用，流式**按平台**决定：Telegram 出货带 `display.platforms.telegram.streaming: true`（流式），Discord 则是 `display.platforms.discord.streaming: false`（不流）。所以启用流式之后，Telegram 开箱即流，Discord 在你改它的开关之前保持整条消息回复。你可以在 dashboard 的 **Channels** 开关里调整这些按平台的开关，或直接改 `~/.hermes/config.yaml`。
:::

## 群聊会话隔离

限制 CLI、TUI/dashboard 与消息 gateway 上最多能同时开着多少个聊天会话：

```yaml
max_concurrent_sessions: null  # null/0 = unlimited; positive integer = active session cap
```

槽位在某个会话跑它的**第一个回合**时被占用，而不是在聊天窗口被打开时。打开、恢复或重连一个聊天在你发消息之前都不花钱，所以空闲的桌面标签页（以及不稳 websocket 触发的后台恢复）不会饿死共享这个上限的消息 gateway。

到达上限时，Hermes 返回一条直接的限制消息，点名哪些界面占着槽位。既有的活动会话保持正常行为。运行 `hermes status --full` 查看当前槽位使用与每个持有者。

这是对并发 gateway 回合的唯一上限：gateway 把每个回合体跑在自己的线程上，所以在默认（未设置）下每个被接受的回合都立即开始，而不是排在其他运行中的回合后面。

规范键是顶层 `max_concurrent_sessions`。Hermes 也接受 `gateway.max_concurrent_sessions` 作为兜底，但两者都设置时顶层胜出。

上限由一个本地运行时租约文件强制执行，且是尽力而为：注册表读不出来或锁不上时 Hermes 会失败开放，让用户不至于被困。它面向单主机/profile 运行时，而不是跨多台机器挂载的共享 `$HERMES_HOME`。一个属主进程存在但存活无法证明的租约（例如 `hermes update` 重启后端之后容器内读不出来的 `/proc` 条目）仍计入上限、仍 fence 它自己的 session id，但不再阻塞认领或释放别的会话。

控制共享聊天是每个房间一个对话、还是每个参与者一个对话：

```yaml
group_sessions_per_user: true  # true = per-user isolation in groups/channels, false = one shared session per chat
```

- `true` 是默认且推荐的设置。在 Discord 频道、Telegram 群组、Slack 频道及类似共享场景里，只要平台提供用户 ID，每个发送者都有自己的会话。
- `false` 回到旧的共享房间行为。当你明确想让 Hermes 把一个频道当作一场协作对话时有用，但也意味着用户共享上下文、token 成本与中断状态。
- 私聊不受影响。Hermes 仍照常按聊天/私聊 ID 为 DM 分键。
- 无论哪种设置，thread 都与其父频道相互隔离；为 `true` 时，每位参与者在 thread 内也有自己的会话。

行为细节与示例见 [Sessions](./sessions.md) 与 [Discord 指南](./messaging/discord.md)。

## 原生托管房间讨论限制

原生的服务端托管房间在每个讨论内、对所有成员共享这些 Discussion 上限。它们作用于该服务拥有的所有原生托管房间，而不是 Desktop 渲染器驱动或镜像的房间。

```yaml
hosted_rooms:
  discussion:
    max_rounds: 3      # Default maximum scheduling rounds per discussion
    max_messages: 10   # Default total visible bot replies across all members
```

两个键都是可选的；省略时保持向后兼容的默认值 3 轮、10 条回复。值必须是正整数：`0`、负值、`null`、布尔值、字符串（含带引号的数字或 `"unlimited"`）与浮点数都不接受。非法值会被忽略并在 gateway 日志里记一条警告、适用默认值，所以一个拼写错误绝不会让群聊下线。例如设 `max_rounds: 6` 与 `max_messages: 30` 可得到更大但仍有限的讨论预算（5 人的房间就能超过 10 条回复的停点）。

把这些键写进持有房间存储的那个 Hermes home 的 `config.yaml`（`shared-state.db` 旁边的根 home），而不是某个房间成员的 profile 配置。它们对 gateway 提供的房间与 Desktop/TUI 后端提供的房间同样生效。每个服务器进程启动时读它们一次：改完后请重启共享该房间存储的每个进程。

这些是上限，不是目标，也不保证任务完成。讨论可以提前结束，Stop 与审批闸门仍然有效。

## 未授权私聊行为

控制 Hermes 在未知用户发来私信时做什么：

```yaml
unauthorized_dm_behavior: pair

whatsapp:
  unauthorized_dm_behavior: ignore
```

- `pair` 是聊天式 DM 平台的默认。Hermes 拒绝访问，但在私信里回复一次性配对码。
- `ignore` 静默丢弃未授权的私信。
- `decline` 发一条简短礼貌的婉拒而不是配对码，随后对该发送者保持 24 小时沉默。覆盖默认文案：

  ```yaml
  unauthorized_dm_behavior: decline
  unauthorized_dm_decline_message: "Sorry, this assistant is private."
  ```

  当你把允许列表留空时，`hermes gateway setup` 会把它作为「Politely decline unknown senders」提供；它写入 `platforms.<platform>.unauthorized_dm_behavior: decline`。

- Email 默认为 `ignore`，除非设置了 `platforms.email.unauthorized_dm_behavior: pair`，因为收件箱里可能有无关的未读邮件。
- 平台段覆盖全局默认，所以你可以大范围保持配对开启、同时让某个平台安静些。

## 快捷命令

定义自定义命令：要么运行 shell 命令而不调用 LLM，要么把一个斜杠命令别名到另一个。exec 型快捷命令零 token，在消息平台（Telegram、Discord 等）上做快速服务器检查或工具脚本很有用。

```yaml
quick_commands:
  status:
    type: exec
    command: systemctl status hermes-agent
  disk:
    type: exec
    command: df -h /
  update:
    type: exec
    command: hermes update
  gpu:
    type: exec
    command: nvidia-smi --query-gpu=name,utilization.gpu,memory.used,memory.total --format=csv,noheader
  restart:
    type: alias
    target: /gateway restart
```

用法：在 CLI 或任何消息平台输入 `/status`、`/disk`、`/update`、`/gpu` 或 `/restart`。`exec` 命令在宿主本地运行并直接返回输出——不调 LLM、不消耗 token。`alias` 命令被改写成配置的斜杠命令目标。

- **30 秒超时** —— 长跑命令会被杀掉并给出错误消息
- **优先级** —— 快捷命令在 skill 命令之前检查，所以你可以覆盖 skill 名
- **自动补全** —— 快捷命令在分发时解析，不出现在内置斜杠命令自动补全表里
- **类型** —— 支持的类型是 `exec` 与 `alias`；其他类型会报错
- **到处可用** —— CLI、Telegram、Discord、Slack、WhatsApp、Signal、Email、Home Assistant

只有字符串的 prompt 快捷方式不是合法的快捷命令。要复用的 prompt 工作流，请创建 skill 或别名到既有斜杠命令。

## 人工延迟

在消息平台上模拟类人的响应节奏：

```yaml
human_delay:
  mode: "off"                  # off | natural | custom
  min_ms: 800                  # Minimum delay (custom mode)
  max_ms: 2500                 # Maximum delay (custom mode)
```

读取的是每个 profile 自己的 `config.yaml`，所以多路复用的 profile 保持各自独立的节奏；没有进程环境覆盖。在 `custom` 模式下，非整数、负数或颠倒的 `min_ms`/`max_ms` 对会被拒绝并记一条点名该键的警告，改用 `natural` 区间（800–2500 毫秒）。

## 代码执行

配置 `execute_code` 工具：

```yaml
code_execution:
  mode: project                # project (default) | strict
  timeout: 300                 # Max execution time in seconds
  max_tool_calls: 50           # Max tool calls within code execution
```

**`mode`** 控制脚本的工作目录与 Python 解释器：

- **`project`**（默认）—— 脚本跑在会话的工作目录里，用活动的 virtualenv/conda 环境的 python。项目依赖（`pandas`、`torch`、项目包）与相对路径（`.env`、`./data.csv`）自然解析，与 `terminal()` 看到的一致。
- **`strict`** —— 脚本跑在一个临时暂存目录里，用 `sys.executable`（Hermes 自己的 python）。可复现性最高，但项目依赖与相对路径解析不出来。

环境清洗（剥掉 `*_API_KEY`、`*_TOKEN`、`*_SECRET`、`*_PASSWORD`、`*_CREDENTIAL`、`*_PASSWD`、`*_AUTH`）与工具白名单在两种模式下完全一致——切换模式不改变安全姿态。

## Web 搜索后端

`web_search` 与 `web_extract` 工具支持五个后端 provider。在 `config.yaml` 或经 `hermes tools` 配置后端：

```yaml
web:
  backend: firecrawl    # firecrawl | searxng | parallel | tavily | perplexity | keenable | exa

  # Or use per-capability keys to mix providers (e.g. free search + paid extract):
  search_backend: "searxng"
  extract_backend: "firecrawl"

  # Keyless free-tier fallback (default: true). With no backend configured
  # and no API keys present, web tools rotate across the Exa/Parallel/
  # Firecrawl/Keenable free tiers. Set false to disable.
  keyless_fallback: true

  # One-shot keyless rescue (default: true). When the chosen/keyed backend
  # fails a call, that single call retries on the keyless ring; the next
  # call attempts the chosen backend again (never sticky).
  keyless_rescue: true

  # Pin Exa/Parallel to a tier (set by the hermes tools Free/Paid rows).
  # free = always the anonymous endpoint; paid = always the keyed SDK path;
  # unset = auto (key present -> paid, otherwise free).
  provider_tier:
    parallel: free
    exa: paid
```

| 后端 | 环境变量 | 搜索 | 提取 |
|---------|---------|--------|---------|
| **Firecrawl**（默认） | `FIRECRAWL_API_KEY` | ✔ | ✔ |
| **SearXNG** | `SEARXNG_URL` | ✔ | — |
| **Parallel** | `PARALLEL_API_KEY`（可选——无密钥免费层） | ✔ | ✔ |
| **Tavily** | `TAVILY_API_KEY`（可选——选中时无密钥） | ✔ | ✔ |
| **Perplexity** | `PERPLEXITY_API_KEY` | ✔ | ✔（与查询相关的摘要） |
| **Exa** | `EXA_API_KEY`（可选——无密钥免费层） | ✔ | ✔ |

**后端选择：**运行时始终使用保存的 `web.backend` 选择（经 `hermes tools` 设置；`nous` 经托管的 Tool Gateway 路由）。只有在从未选择过 web 后端时，才会从可用 API key 里自动探测一个：只设了 `SEARXNG_URL` 就用 SearXNG；只设了 `EXA_API_KEY` 就用 Exa；只设了 `TAVILY_API_KEY` 就用 Tavily；只设了 `PERPLEXITY_API_KEY` 就用 Perplexity；只设了 `PARALLEL_API_KEY` 就用 Parallel；只设了 `KEENABLE_API_KEY` 就用 Keenable。**既无选择又完全没有凭据时**，请求在无密钥免费层环（Exa / Parallel / Firecrawl / Keenable）上轮转，遇限流自动切到下一家（搜索还会在 vendor 拒绝时切换）——细节见 [Web Search 指南](./features/web-search.md)。一旦有了选择，往 `.env` 加 key 也不会改变路由。在 `hermes tools` 里选 Tavily、Firecrawl 或 Keenable 同样不需要 key。

**SearXNG** 是免费、自托管、尊重隐私的元搜索引擎，查询 70 多个搜索引擎。无需 API key——只需把 `SEARXNG_URL` 指向你的实例（例如 `http://localhost:8080`）。SearXNG 只做搜索；`web_extract` 需要单独的提取 provider（设 `web.extract_backend`）。Docker 设置说明见 [Web Search 设置指南](./features/web-search.md)。

**自托管 Firecrawl：**把 `FIRECRAWL_API_URL` 指向你自己的实例。设置了自定义 URL 时 API key 变为可选（在服务器上设 `USE_DB_AUTHENTICATION=*** 来关闭认证）。

**Parallel 搜索模式：**设 `PARALLEL_SEARCH_MODE` 控制搜索行为——`fast`、`one-shot` 或 `agentic`（默认 `agentic`）。

**Exa：**在 `~/.hermes/.env` 里设 `EXA_API_KEY`。支持 `category` 过滤（`company`、`research paper`、`news`、`people`、`personal site`、`pdf`）与域名/日期过滤。

## 浏览器

配置浏览器自动化行为。每个 browser 键都在 `browser:` 之下；浏览器来源（本地 Chromium、云 provider、Lightpanda、`/browser connect`、真实 profile）如何配合见 [Browser 功能页](./features/browser.md)。

```yaml
browser:
  inactivity_timeout: 120        # Seconds before an idle browser is closed
  command_timeout: 30            # Chromium launch timeout floor (seconds)
  headed: false                  # true = visible Chromium window (local); keeps the browser open between turns
  engine: auto                   # auto (Chromium) | lightpanda ("chrome" is accepted as auto)
  # Local Chromium launched by Hermes
  executable_path: ""            # Chromium binary override; "" = the packaged Chromium
  user_data_dir: ""              # Persistent profile shared by every session; "" = fresh profile per session
  chromium_args: []              # Extra Chromium command-line flags, e.g. ["--lang=de-DE"]
  # Cloud browser selection (written by `hermes tools` → Browser Automation)
  cloud_provider: local          # local | browserbase | browser-use | firecrawl | nous | <provider plugin>; unset = autodetect from credentials
  auto_local_for_private_urls: true  # With a cloud provider, open LAN/localhost URLs in a local Chromium
                                     # (ignores allow_private_urls; false = refuse them instead)
  allow_private_urls: false      # Legacy alias of security.allow_private_urls (guards cloud/CDP browsers, not the local Chromium)
  # Optional CDP override — when set, the browser tools attach to your own
  # Chromium-family browser (as /browser connect does) instead of launching one.
  cdp_url: ""
  use_real_profile: false        # Browse on a managed copy of your real browser profile (opt-in)
  # Dialog supervisor — how native JS dialogs (alert / confirm / prompt / beforeunload) are handled
  dialog_policy: must_respond    # must_respond | auto_dismiss | auto_accept
  dialog_timeout_s: 300          # Safety auto-dismiss under must_respond (seconds)
```

**可执行文件解析。**Hermes 启动它找到的第一个 Chromium：`browser.executable_path` → Hermes 包管理器装的 Chromium（`hermes pm install chromium`）→ `/etc/hermes/chromium-executable-path`（官方 Docker 镜像）→ `PATH` 上的系统 `chromium` / `chromium-browser`（Termux 与没有打包构建的平台）。一个都没有时，浏览器工具会给出提示而不是静默失败。

**关闭浏览。**没有浏览器配置开关：用 `hermes tools` 禁用 `browser` 工具集（或 `hermes tools disable browser [--platform NAME]`）。

**对话框策略：**

- `must_respond`（默认）—— 捕获对话框并等待 agent 调用 `browser_dialog(action=...)`。`dialog_timeout_s` 秒后仍无响应时，对话框被自动关闭，防止页面的 JS 线程永远卡住。
- `auto_dismiss` —— 捕获后立即关闭。
- `auto_accept` —— 捕获后立即接受。对带激进 `beforeunload` 提示的页面有用。

完整对话框流程见 [browser 功能页](./features/browser.md#browser_dialog)。

**已移除的键（自动迁移）。**`browser.backend` 已消失——`browser_exec` 是唯一的浏览器路径。旧的 `backend: off`（带不带引号都一样）会被移除，并给出一次性提示改用禁用 `browser` 工具集，该提示由 `hermes update` 显示，或在 Hermes 启动时迁移了配置的情况下，作为第一条会话开头的警告显示。其他任何值也会被移除并附一条点名它及其替代者的说明（`camofox`：Camofox 插件；`local`：`browser_exec` 启动的打包 Chromium；云名：`browser.cloud_provider`）。

`snapshot_threshold`、`record_sessions`、`allow_unsafe_evaluate` 与 `restrict_evaluate` 属于已移除的内置浏览器工具，不再有任何效果。`browser.camofox.*` 键由 Camofox 插件（`hermes plugins install camofox`）读取，core 不读。

旧的 `AGENT_BROWSER_*` 环境变量不再被读取；更新时，若对应键未设置，它们的值会从 profile 的 `.env` 复制过去（`AGENT_BROWSER_EXECUTABLE_PATH` → `executable_path`、`AGENT_BROWSER_PROFILE` → `user_data_dir`、`AGENT_BROWSER_ARGS` → `chromium_args`、`AGENT_BROWSER_HEADED` → `headed`、`AGENT_BROWSER_ENGINE` → `engine`）。`engine: auto` 与 `headed: false` 视为未设置，因为过去是环境变量覆盖了它们。相对的 `AGENT_BROWSER_PROFILE` 当初相对工作目录解析，所以会以那个绝对路径（迁移配置那个进程的工作目录）写入，并附一条以同样方式显示、点名它所钉路径的说明，方便你核对浏览器登录态是否在那里。

## 时区

用 IANA 时区字符串覆盖服务器本地时区。影响 cron 调度与注入 system prompt 的时间。它不改变日志文件：`~/.hermes/logs/` 里的每一行都按机器本地时间盖戳，`hermes logs --since` 也是与之比较。

```yaml
timezone: "America/New_York"   # IANA timezone (default: "" = server-local time)
```

支持的值：任何 IANA 时区标识符（例如 `America/New_York`、`Europe/London`、`Asia/Kolkata`、`UTC`）。留空或省略即服务器本地时间。

`hermes doctor`（以及启动时的配置检查）会报告运行时加载不了的值——否则一个 `Asia/Tokio` 这样的拼写错误会把 agent 时钟与每个 cron 计划都静默放到服务器本地时间。设置 `HERMES_TIMEZONE` 会覆盖该键。

Agent 时钟、cron 计划与时间感知工具在所有操作系统上都跟随该时区。经 `execute_code` 运行的代码在 Linux 与 macOS 上还以 `TZ` 继承它；在 Windows 上那些子进程保持操作系统配置的时区（Windows 的 C 运行时只解析 POSIX 形式的 `TZ` 字符串，IANA 名在那儿会得出错误的 UTC 偏移），所以当子脚本必须按该时区渲染本地时间时，请直接设置 Windows 的时区。

## Discord

为消息 gateway 配置 Discord 专属行为：

```yaml
discord:
  require_mention: true          # Require @mention to respond in server channels
  free_response_channels: ""     # Comma-separated channel IDs where bot responds without @mention
  auto_thread: true              # Auto-create threads on @mention in channels
  free_response_auto_thread: false  # Free-response channels also auto-thread (default: reply inline)
```

- `require_mention` —— 为 `true`（默认）时，bot 只在被 `@BotName` 提及时才在服务器频道里回应。私信始终无需提及即可工作。
- `free_response_channels` —— 逗号分隔的频道 ID 列表，bot 对这些频道里的每条消息都回应、不要求提及。
- `auto_thread` —— 为 `true`（默认）时，频道里的提及自动为该对话建 thread，保持频道整洁（类似 Slack 的 thread）。
- `free_response_auto_thread` —— 为 `true` 时，`free_response_channels` 里的频道也为每条顶层消息自动建 thread。默认 `false`：自由回应频道就地回复。需要 `auto_thread: true`。

## 安全

机密遮蔽与网站黑名单：

```yaml
security:
  redact_secrets: true           # Redact API key patterns in tool output and logs (on by default)
  website_blocklist:             # See Website Blocklist section below
    enabled: false
    domains: []
    shared_files: []
```

- `redact_secrets` —— 为 `true` 时，在工具输出进入对话上下文与日志之前，自动检测并遮蔽看起来像 API key、token 与密码的模式。**默认开启**。只有当你需要原始的类凭据字符串做调试或遮蔽器开发时才显式设为 `false`。用 `read_file`、`search_files` 或终端 `cat`/`grep` 读取含机密的文件（`.env` 式文件、shell rc/profile 文件、`HERMES_HOME` 下的 Hermes `config.yaml` 及其 `backups/config/` 副本）时，也会把凭据形状的赋值（`SOME_API_TOKEN: …`）遮成一个不可复用的 `«redacted-secret»` 标记，无论值长什么样；普通源码与项目配置文件只保留厂商前缀模式，于是 `MAX_TOKENS: 100` 这类 fixture 绝不会被搞坏。

更早的版本还有给一个内置命令扫描器用的 `tirith_*` 键；它已被移除，升级时那些键会被丢弃。内容级命令检查见 [Content-Level Command Checks](security.md#content-level-command-checks)。

## 网站黑名单

阻止 agent 的 web 与浏览器工具访问特定域名：

```yaml
security:
  website_blocklist:
    enabled: false               # Enable URL blocking (default: false)
    domains:                     # List of blocked domain patterns
      - "*.internal.company.com"
      - "admin.example.com"
      - "*.local"
    shared_files:                # Load additional rules from external files
      - "/etc/hermes/blocked-sites.txt"
```

启用后，任何匹配被禁域名模式的 URL 在 web 或浏览器工具执行之前就被拒绝。这作用于 `web_search`、`web_extract`、浏览器导航以及任何访问 URL 的工具。

域名规则支持：

- 精确域名：`admin.example.com`
- 通配子域名：`*.internal.company.com`（封锁所有子域名）
- 顶级域通配：`*.local`

共享文件每行一条域名规则（空行与 `#` 注释被忽略）。缺失或不可读的文件会记一条警告，但不会禁用其他 web 工具。

该策略缓存 30 秒，所以配置改动无需重启即可快速生效。

## 智能审批

控制 Hermes 如何处理可能危险的命令：

```yaml
approvals:
  mode: smart   # smart | manual | off
```

| 模式 | 行为 |
|------|----------|
| `smart`（默认） | 用一个辅助 LLM 判断被标记的命令是否真的危险。低风险命令仅对那一次调用自动批准。真正有风险的命令被拒绝；拿不准的决定上报给用户。 |
| `manual` | 在执行任何被标记的命令之前询问用户。CLI 里显示交互式审批对话框；消息平台里排一条待审批请求。 |
| `off` | 跳过所有审批检查。等价于 `HERMES_YOLO_MODE=true`。**谨慎使用。** |

Smart 模式对减少审批疲劳尤其有用——它让 agent 在安全操作上更自主地工作，同时仍能拦住真正有破坏性的命令。

:::warning
设 `approvals.mode: off` 会关掉 terminal 命令的全部安全检查。只在受信的沙箱环境里使用。
:::

### 拒绝熔断器

`approvals.denial_breaker_threshold`（默认 `3`）防止 agent 反复重试智能审批复核者一直拒绝的某个命令变体——每次重试都要再烧一次守卫 LLM 调用。在一次会话里连续拒绝这么多次之后，拒绝消息会升级为一条硬停止指令，告诉 agent 停下、报告被阻断的操作，并请你手动运行或 `/approve`。任何一次批准都会重置计数；设 `0` 关闭：

```yaml
approvals:
  denial_breaker_threshold: 3   # 0 disables the breaker
```

### 拒绝规则

`approvals.deny` 是一组 glob 模式，无条件阻断匹配的 terminal 命令——即使在 `--yolo`、`/yolo` 或 `mode: off` 下也一样。它是内置硬性黑名单的可由用户编辑的对应物：

```yaml
approvals:
  deny:
    - "git push --force*"
    - "*curl*|*sh*"
```

模式是大小写不敏感的 fnmatch glob，且在 YAML 里必须加引号（开头裸的 `*` 是解析错误）。详见 [Security — User-Defined Deny Rules](./security.md#user-defined-deny-rules-approvalsdeny)。

### 自定义智能审批策略

`approvals.smart_policy` 让你把自己的规则追加进智能审批复核者的指令。设置后，该文本会被加进守卫 LLM 的 system prompt（可信通道——绝不与不可信的命令文本并列），于是你可以在不改代码的情况下为自己的环境收紧或放松它的判断：

```yaml
approvals:
  smart_policy: |
    Always ESCALATE commands that modify anything under /etc.
    APPROVE docker compose restarts in ~/deploys — they are routine here.
```

## 检查点

破坏性文件操作之前的自动文件系统快照。细节见 [Checkpoints & Rollback](./checkpoints-and-rollback.md)。

```yaml
checkpoints:
  enabled: false                 # Enable automatic checkpoints (also: hermes chat --checkpoints). Default: false (opt-in).
  max_snapshots: 20              # Max checkpoints to keep per directory (default: 20)
```

## 委派

为 delegate 工具配置 subagent 行为：

```yaml
delegation:
  backend: default                          # Delegation strategy routing each task: "default" = the keys below, or a plugin backend (model_map, profile_routes, ...)
  # backends:                               # Each plugin backend's own settings, keyed by its backend name
  #   model_map:
  #     options: [...]
  # model: "google/gemini-3-flash-preview"  # Override model (empty = inherit parent)
  # provider: "openrouter"                  # Override provider (empty = inherit parent)
  # base_url: "http://localhost:1234/v1"    # Direct OpenAI-compatible endpoint (takes precedence over provider)
  # api_key: "local-key"                    # API key for base_url (falls back to OPENAI_API_KEY)
  # api_mode: ""                            # Wire protocol for base_url: "chat_completions", "codex_responses", or "anthropic_messages". Empty = auto-detect from URL (e.g. /anthropic suffix → anthropic_messages). Set explicitly for non-standard endpoints the heuristic can't detect.
  compression_threshold_tokens: 0          # Optional absolute cap on a subagent's compaction trigger (>= 16000); 0 = off, children use the ratio threshold
  # request_overrides:                      # Per-child request settings sent on every subagent API call (all resolution branches).
  #   extra_body:                           # Merged into the request's extra_body — e.g. OpenRouter routing hints:
  #     provider:
  #       sort: throughput
  max_concurrent_children: 3                # Parallel children per batch (floor 1, no ceiling). Also via DELEGATION_MAX_CONCURRENT_CHILDREN env var.
  worktree_isolation: false                 # Give each child its own git worktree branched from HEAD (local backend + git repos only; inspired by Muse Code). See Subagent Delegation → Worktree Isolation.
  max_spawn_depth: 1                        # Delegation tree depth cap (1-3, clamped). 1 = flat (default): parent spawns leaves that cannot delegate. 2 = orchestrator children can spawn leaf grandchildren. 3 = three levels.
  orchestrator_enabled: true                # Global kill switch. When false, role="orchestrator" is ignored and every child is forced to leaf regardless of max_spawn_depth.
  oneshot_max_children: 2                   # Total subagents a one-shot run (hermes chat -q / --oneshot) may spawn; 0 = unlimited. Interactive and gateway sessions are never capped by this.
  gateway_mode: auto                        # Gateway sessions: auto | inline | background. auto = join children inside the turn (one answer) on a messaging chat whose display.interim_assistant_messages is off. See Subagent Delegation → Messaging chats without interim messages.
```

**委派策略（`backend`）：**`delegation.backend` 挑选决定每个 subagent 路由的策略插件。`default` 遵循下面的键（它们为空时用父进程的路由）。`model_map`（每个任务一个具名模型）与 `profile_routes`（每个任务一个 Hermes profile）这类插件策略从 `delegation.backends.<backend name>` 读设置。插件缺失或被禁用的 backend 会失败关闭：`delegate_task` 返回一条点名它与修复方法（`/delegation default`，或 `hermes config set delegation.backend default`）的工具错误，而不是把子任务跑在别的路由上。没有自己 `fallback_providers` 的 backend 路由使用 `delegation.fallback_providers`。见 [Subagent Delegation → Delegation strategies](features/delegation.md#delegation-strategies-delegationbackend)。

**Subagent 的 provider:model 覆盖：**默认情况下 subagent 继承父 agent 的 provider 与模型。设 `delegation.provider` 与 `delegation.model` 可把 subagent 路由到不同的 provider:model 对——例如主 agent 跑昂贵的推理模型时，用便宜快速的模型做范围狭窄的子任务。

**Subagent fallback 链：**设 `delegation.fallback_providers` 给 worker 自己的链（条目形状与顶层列表相同）。被显式 pin 的子任务（按 provider、端点或模型）只在声明了该链时使用它；否则会大声失败，而不是借用父 agent 的路由。对未 pin 的子任务，缺失或 `null` 的设置保持继承父链。在 `delegation:` 下用 `fallback_providers: []` 可彻底关闭子任务 fallback。

**直连端点覆盖：**如果你想要那条直白的自定义端点路径，设 `delegation.base_url`、`delegation.api_key` 与 `delegation.model`。这会把 subagent 直接发往那个 OpenAI 兼容端点，并优先于 `delegation.provider`。省略 `delegation.api_key` 时，Hermes 只回退到 `OPENAI_API_KEY`。当 `delegation.provider` 与 `delegation.base_url` 同时设置时，显式端点与密钥仍然胜出，但该 provider 的请求设置（`extra_body` 覆盖与来自你 `custom_providers` 条目的最大输出 token）会被带进 subagent。

**按子任务的请求设置（`request_overrides`）：**`delegation.request_overrides` 是随每次 subagent API 调用发送的请求设置字典。顶层键是 API kwargs（例如 `service_tier`）；`extra_body` 子字典会合并进请求的 `extra_body`。它在**全部三条**解析分支上都被尊重——直连 `base_url`、具名 `provider` 与纯继承——所以该键始终生效。优先级：显式的 `request_overrides` 值**覆盖合并**任何运行时或父进程派生的覆盖——顶层显式键胜出，`extra_body` 做一层深合并，于是运行时的 `extra_body` 键（例如某 provider 的 `thinking: {type: disabled}` 性格设置）会存活，除非你的键重新定义了它们。典型用例是给委派子任务的 OpenRouter 路由提示：

```yaml
delegation:
  model: "deepseek/deepseek-v4-flash-0731"
  base_url: "https://openrouter.ai/api/v1"
  api_key: "sk-or-..."
  request_overrides:
    extra_body:
      provider:
        sort: throughput   # route children to the fastest OpenRouter provider
```

**线路协议（`api_mode`）：**Hermes 从 `delegation.base_url` 自动探测线路协议（例如以 `/anthropic` 结尾的路径 → `anthropic_messages`；Codex / 原生 Anthropic / Kimi-coding 主机名保持既有探测）。对启发式无法归类的端点——例如 Azure AI Foundry、MiniMax、智谱 GLM，或把 Anthropic 形状后端挡在前面的 LiteLLM 代理——请把 `delegation.api_mode` 显式设为 `chat_completions`、`codex_responses` 或 `anthropic_messages` 之一。留空（默认）则保持自动探测。

委派 provider 使用与 CLI/gateway 启动相同的凭据解析。所有已配置的 provider 都支持：`openrouter`、`nous`、`zai`、`kimi-coding`、`minimax`、`minimax-cn`。设置了某个 provider 时，系统自动解析出正确的 base URL、API key 与 API 模式——无需手工接线凭据。

**优先级：**配置里的 `delegation.base_url` → 配置里的 `delegation.provider` → 父 provider（继承）。配置里的 `delegation.model` → 父模型（继承）。只设 `model` 不设 `provider` 只改模型名、保留父凭据（在同一 provider 内换模型时有用，例如 OpenRouter）。

**一次性运行：**有限的 `hermes chat -q` / `--oneshot` 会话没有后续回合来消费委派结果，也没有后续会话可学习，所以它以更小的足迹运行：skills prompt 只要求领域 skill 而不是流程 skill（`skill_manage` 仍可用，运行仍可撰写 skill），且 `oneshot_max_children` 限制该运行可派生的 subagent 总数（默认 `2`，`0` = 不限）。超过上限时 `delegate_task` 返回一条工具错误，让 agent 就地完成。一次性运行也没人能答复或引导，所以它还运行在：没有 `clarify` 工具、没有 system prompt 里的中途引导说明、以及一个省略了实时控制参数（`action` list/steer/stop、`subagent_id`、`message`）的 `delegate_task` schema 之下：它的子任务在调用内部被 join，因此从不存在需要控制的在跑子任务。

**宽度与深度：**`max_concurrent_children` 限制每批并行跑多少 subagent（默认 `3`，下限 1，无上限）。也可经 `DELEGATION_MAX_CONCURRENT_CHILDREN` 环境变量设置。当模型提交的 `tasks` 数组超过上限时，`delegate_task` 返回一条解释该限额的工具错误，而不是静默截断。`max_spawn_depth` 控制委派树深度（夹取到 1–3）。默认 `1` 时委派是平的：子任务不能派生孙任务，传 `role="orchestrator"` 会静默降级为 `leaf`。提到 `2` 让 orchestrator 子任务能派生 leaf 孙任务；`3` 则是三层树。Agent 经 `role="orchestrator"` 按次选择进入编排；`orchestrator_enabled: false` 会强制每个子任务回到 leaf。成本按乘法放大——在 `max_spawn_depth: 3` 配 `max_concurrent_children: 3` 时，树最多可达 3×3×3 = 27 个并发 leaf agent。用法模式见 [Subagent Delegation → Depth Limit and Nested Orchestration](features/delegation.md#depth-limit-and-nested-orchestration)。

**子进程通知：**subagent 启动的后台进程把其完成/监控通知路由到父对话，但那些通知在父对话里默认被**抑制**——子任务的合并结果才是交付物。设 `delegation.surface_child_process_notifications: true` 可投递它们（带 subagent 归属）。委派结果本身从不被抑制。见 [Subagent Delegation → Child background-process notifications](features/delegation.md#child-background-process-notifications)。

## 澄清

配置 Hermes 等待澄清问题的回答多久。一个值覆盖所有界面——经典 CLI 模态框、TUI/Desktop 卡片与消息 gateway。规范键是 `agent.clarify_timeout`（默认 `3600` 秒；`0` 或更小 = 不限）；显式设置的遗留顶层 `clarify.timeout` 仍被尊重：

```yaml
agent:
  clarify_timeout: 3600        # Seconds to wait for user clarification response (0 or less = unlimited)
```

超时到期时，agent 以 `"outcome": "timed_out"` 解除阻塞（用户已经锁定的答案保留）并自行继续。澄清提示绝不会被通用的按工具期限（`timeouts.tools.sequential_call`）切断；只有 `agent.clarify_timeout` 约束这次等待。

## 上下文文件（SOUL.md、AGENTS.md）

Hermes 使用两种不同的上下文作用域：

| 文件 | 用途 | 作用域 |
|------|---------|-------|
| `SOUL.md` | **主要 agent 身份** —— 定义 agent 是谁（system prompt 中的第 1 槽位） | `~/.hermes/SOUL.md` 或 `$HERMES_HOME/SOUL.md` |
| `.hermes.md` / `HERMES.md` | 项目专属指令（最高优先级） | 向上走到 git 根 |
| `AGENTS.md` | 项目专属指令、编码规范 | 递归目录遍历 |
| `CLAUDE.md` | Claude Code 上下文文件（也会被检测） | 仅工作目录 |
| `.cursorrules` | Cursor IDE 规则（也会被检测） | 仅工作目录 |
| `.cursor/rules/*.mdc` | Cursor 规则文件（也会被检测） | 仅工作目录 |

- **SOUL.md** 是 agent 的主要身份。它占据 system prompt 的第 1 槽位，完全替换内置默认身份。编辑它可以彻底定制 agent 是谁。
- 如果 SOUL.md 缺失、为空或加载不了，Hermes 回退到内置默认身份。
- **项目上下文文件用优先级系统** —— 只加载**一种**（先匹配者胜）：`.hermes.md` → `AGENTS.md` → `CLAUDE.md` → `.cursorrules`。SOUL.md 始终独立加载。
- **AGENTS.md** 是分层的：如果子目录里也有 AGENTS.md，全部合并。
- 如果尚不存在默认 `SOUL.md`，Hermes 会自动植入一个。
- 所有加载的上下文文件都被截断到 `context_file_max_chars` 字符（默认 20,000），并做智能截断。

另见：

- [Personality & SOUL.md](./features/personality.md)
- [Context Files](./features/context-files.md)

## 工作目录

| 场景 | 默认 |
|---------|---------|
| **CLI（`hermes`）** | 你运行命令时所在的当前目录 |
| **消息 gateway** | `~/.hermes/config.yaml` 的 `terminal.cwd`；未设置时为 home 目录 `~` |
| **Docker / Singularity / Modal / SSH** | 容器或远程机器里的用户 home 目录 |

覆盖工作目录：

```yaml
# In ~/.hermes/config.yaml:
terminal:
  cwd: /home/myuser/projects
```

`MESSAGING_CWD` 与 `~/.hermes/.env` 里直接的 `TERMINAL_CWD` 条目是遗留兼容兜底。新配置应使用 `terminal.cwd`。

## 网络

出站 HTTP 的连通性变通：

```yaml
network:
  force_ipv4: false   # Force IPv4 for outbound connections (default: false)
```

`force_ipv4` —— 在 IPv6 损坏或不可达的服务器上，Python 会先解析 AAAA 记录，可能在整个 TCP 超时里挂住才回退到 IPv4。Hermes 已经为每个出站连接同时赛跑 IPv6 与 IPv4（Happy Eyeballs，RFC 8305：IPv4 尝试在 IPv6 之后 250 毫秒开始，先连上的胜出），于是「宣称可达但被黑洞」的 IPv6 路由每次连接只花约四分之一秒，而不是整个超时。这覆盖 gateway 的 WebSocket 拨号（中继连接器、平台 adapter）以及 HTTP。只有当你想完全跳过 IPv6、直接走 IPv4 连接时才把它设为 `true`。`hermes doctor` 会跑一项 `IPv6 route` 检查，探测死掉的 IPv6 路径并指向该设置。

## 引导

首次接触的引导提示与首条消息的提议：

```yaml
onboarding:
  profile_build: "ask"   # "ask" (default) | "off"
  seen: {}               # internal latch — leave empty
  run: null              # desktop first-run onboarding: null (fresh install) | true | false
```

- `profile_build` —— 控制有史以来第一条消息上的提议，出现在 TUI、桌面应用与消息私信里（绝不在群聊）。`"ask"`（默认）提议构建一个用户画像；该提议是**选择加入且需同意**的——agent 在任何查询之前先询问，绝不静默读取已连接的账户，只把已确认的事实存入用户记忆。`"off"` 只停止该提议；agent 仍会给一段平实的介绍。该提议每个 profile 至多触发一次。
- `seen` —— 内部状态。Hermes 把每个显示过的提示闩在这里，使其不再触发；首条消息提议显示过一次也记在这里。不要手工编辑它——想重新看到所有提示，就把整个 `onboarding` 段清空。
- `run` —— 桌面应用下次启动时是否打开其首次运行引导聊天。未设置表示仅在全新安装时（还没有会话、也还没有 profile）。引导开始时 Hermes 写 `true`，完成或跳过时写 `false`。它始终放在默认 profile 的 `config.yaml` 里，无论应用跑在哪个 profile。设 `false` 可永不显示；受管安装可以在受管配置里钉住它。

## Webapp

Gateway 可以在自己的监听器上[在浏览器里提供 Desktop workspace](./desktop.md#use-the-desktop-workspace-from-a-browser)。在你打开之前它是关的。

```yaml
webapp:
  enabled: false     # true: the gateway serves the Webapp
  host: 127.0.0.1    # 127.0.0.1, ::1 or localhost; or 0.0.0.0 / :: for other machines (dashboard sign-in required)
  port: 9120         # fixed, so the browser's address stays the same across gateway restarts
  public_url: ""     # the https:// address a reverse proxy or tunnel serves the Webapp at (sign-in required)
```

- `enabled` —— gateway 启动时读它；改完重启 gateway（`hermes gateway restart`）。
- `host` —— `127.0.0.1`、`::1` 或 `localhost` 让 Webapp 留在本机。`0.0.0.0` 或 `::` 让它可从其他机器访问，并需要一个 [dashboard 登录提供方](./features/web-dashboard.md#authentication-gated-mode)；没有它时 gateway 只服务原生客户端，`hermes webapp --status` 会说明原因。添加提供方后重启 gateway。其他任何值（包括 `127.0.0.2` 这类回环地址）都让 Webapp 保持关闭。
- `port` —— 独立 profile 的 gateway 需要一个不同于默认 gateway 的端口。**Settings → Web Access → Start** 会为未设端口的独立 profile 挑一个（9120 之上第一个没被其他 profile 占用的空闲端口）并保存在这里；它绝不会替换你设过的端口。端口被占用时，gateway 同样只服务原生客户端，`hermes webapp --status` 报告原因。它还会替换 Webapp 的浏览器登录，因为端口可能已被别的程序拿走，所以端口空出来之后打开的标签页需要再跑一次 `hermes webapp`。
- `public_url` —— 当你运行的反向代理或隧道以自己的地址提供 Webapp（转发到 `host:port`）时设置它。它即使在回环 `host` 上也会打开 dashboard 登录，是 Webapp 接受请求的唯一外部主机名，登录回调也建立在它之上。没有登录提供方时 gateway 只服务原生客户端，与 `0.0.0.0` 一样。它必须是不含凭据、查询或片段的 `http://` 或 `https://` 地址；其他任何值都让 Webapp 关闭。`dashboard.public_url` 是给 `hermes dashboard` 的，从不适用于 Webapp。

当 `host` 为 `0.0.0.0` 或 `::`，或 `public_url` 已设置（无论 host 是什么）时，登录就会开启。随后 `hermes webapp` 会为你打开 Webapp 地址（设了 `public_url` 时就是它，也是登录回调返回之处），用你的 dashboard 账户登录：它的一次性链接只能打开不需要登录的 Webapp。原生客户端（CLI、TUI 与桌面应用）从不登录：无论配置怎么写，gateway 给它们的监听器从不开口要登录。

Webapp 设置从提供该 profile 的 gateway 的配置读取：具名 profile 用其服务方默认 profile 的配置，独立 profile 用自己的配置。

## Dashboard

[web dashboard](./features/web-dashboard.md) 的配置 —— 视觉主题、公开 URL 与认证提供方。认证提供方（OAuth、basic 密码、drain）在 web-dashboard 页有详细文档；这里给的是 `config.yaml` 的形状。

```yaml
dashboard:
  theme: "default"            # "default" | "midnight" | "ember" | "mono" | "cyberpunk" | "rose"
  show_token_analytics: false # Re-enable the (local-estimate-only) token/cost analytics surfaces
  public_url: ""              # Full public authority for OAuth redirect_uri (env: HERMES_DASHBOARD_PUBLIC_URL)
  trusted_proxies: []         # Proxy IPs/CIDRs allowed to supply X-Forwarded-* headers
  oauth:                      # Portal OAuth gate (engaged with --host and not --insecure)
    client_id: ""             # agent:{instance_id} — Portal provisions this
    portal_url: ""            # blank → plugin default (production Portal)
  basic_auth:                 # Self-hosted username/password gate (dashboard_auth/basic plugin)
    username: ""              # blank → plugin no-op
    password_hash: ""         # scrypt$... (preferred — no plaintext at rest)
    password: ""              # plaintext fallback (hashed in-memory at load)
    secret: ""                # token-signing key; blank → random per-process
    session_ttl_seconds: 0    # 0 → plugin default (12h)
  drain_auth:                 # Drain-control service-credential gate (dashboard_auth/drain plugin)
    scope: "drain"            # capability label on the verified principal
    min_secret_chars: 43      # entropy bar (url-safe-b64 chars; 43 ≈ 256 bits)
  ws_ping_interval: 20.0      # Non-loopback WebSocket keepalive ping interval (seconds)
  ws_ping_timeout: 20.0       # Non-loopback WebSocket keepalive pong timeout (seconds)
  ws_orphan_reap_grace_s: 20.0 # Grace before a WS-detached session is reaped (seconds)
  ssh_isolated_idle_grace_s: 900.0 # Desktop-over-SSH backend exits after this long with no client and no running turn
  ws_orphan_activity_stale_s: 600.0 # Activity idle bound before a detached RUNNING turn is interrupted (seconds)
  startup_orphan_sweep: true  # Close session rows orphaned by a dead gateway process at boot
```

- `theme` —— dashboard 视觉主题。

- `show_token_analytics` —— 默认关闭。Analytics 页面与 token/成本数字是**本地的下界估算**（它们排除辅助调用、重试、fallback 与缓存写入），所以读数可能远低于 provider 账单。只有理解它们不是计费数据时才设 `true`。

- `public_url` —— 设置后，它是构建 OAuth `redirect_uri` 所用的完整权威（scheme + host + 可选路径前缀）。为不可靠转发 `X-Forwarded-*` 头的反向代理之后的部署设置它。留空则用代理头重建。

- `trusted_proxies` —— 允许提供 `X-Forwarded-Proto` 与 `X-Forwarded-For` 的 IP 地址或受限 CIDR 网段。回环自动保持受信。当 TLS 反向代理从另一个容器或主机连入时配置它。优先用代理的确切 IP；只有其地址动态时才用一个小的专用网络。通配符与 `/0` 网络被拒绝。

- `oauth` / `basic_auth` / `drain_auth` —— 由内置 dashboard-auth 插件读取的认证提供方配置。drain 机密本身**不在这里设置**；它经 `HERMES_DASHBOARD_DRAIN_SECRET` 环境变量提供。完整认证设置见 [Web Dashboard](./features/web-dashboard.md)。

- `ws_ping_interval` / `ws_ping_timeout` —— 非回环绑定的 WebSocket 保活调优（回环连接从不 ping）。在高延迟链路（Tailscale、远距离 SSH 隧道）上调高它们，否则 20 秒默认值可能制造虚假的 1006 断连。

- `ssh_isolated_idle_grace_s`（默认 `900`）—— 经 SSH 抵达的、由 Desktop 持有的 `hermes serve --isolated` 后端会有意与 SSH 会话分离，这样连接中途睡眠的笔记本拆不掉它；过去每次暗唤醒重连都会留下另一个持有 `state.db` 的后端。现在，一旦这么久都没有客户端 WebSocket 连接、且没有 agent 回合在跑，后端就自行退役（回合会让它活着；读不出来的回合状态也让它活着）。如果你依赖分离后端在笔记本睡眠后跑完长任务，就设高。这类后端还会发一个慢速 WebSocket ping（60 秒、10 分钟超时），让半开的隧道能被发现。与该宽限无关，一旦远程主机上 Desktop 对该连接的所有权锁点名了同一连接的更新一次 spawn，后端就会（在回合之间）退役，于是重连风暴不会堆叠分离后端；这覆盖 POSIX 与原生 Windows SSH 主机。

- `ws_orphan_reap_grace_s` —— 一个 WS 分离的会话在被孤儿回收器收走之前等多久。客户端重连慢就与保活值一起调高。周期性会话维护还会为已关闭的 socket 完成清理并重新武装缺失的孤儿定时器，于是分离的聊天不能仅因初次清理或定时器丢失就一直握着它的所有权租约。重连会取消那个定时器；活跃的委派工作与健康的运行中回合仍受常规孤儿回收器检查保护。（`HERMES_TUI_WS_ORPHAN_REAP_GRACE_S` 作为内部覆盖保留。）

- `ws_orphan_activity_stale_s`（默认 `600`）—— 一个分离的**运行中**回合的活动时钟（即 `agent.turn_liveness` 看门狗采样的同一时钟：API 等待、流式 token、工具心跳）要空闲多久，孤儿回收器才打断它。没有客户端在场但仍在积极产出的回合会继续跑到完成——合上笔记本、把移动端切到后台、或一次桌面更新都不再取消健康的长回合；只有真正卡死的回合才会被打断。设 `0` 可无论活动如何都在宽限窗口处打断（旧行为）。

- `startup_orphan_sweep`（默认 `true`）—— 上面的 WS 孤儿回收定时器是进程内的，所以它触发前的 gateway 重启（更新、崩溃、systemd）会让会话行永远开着——`resume` 与 dashboard 里的幽灵「活跃」工作。每次 gateway 启动时——stdio TUI（`entry.main`）与 desktop/dashboard 的 WebSocket sidecar（`handle_ws`）都一样——`source` 为 `tui` / `desktop` / `subagent` / `unknown`（token 计费守卫不得不自己物化出来的行）且开始时间**与**最新消息都早于会话 TTL（`HERMES_TUI_SESSION_TTL_S`，默认 6 小时）的行，会被以 `end_reason: startup_orphan_reap` 关闭。消息平台会话（Telegram、Discord……）绝不动，活的内存会话（已经恢复过的客户端）被排除，被清扫的会话仍可恢复。

参考文献从略，见原文。
