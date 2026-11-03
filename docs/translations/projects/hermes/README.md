# Hermes Agent 项目 README 中译（Hermes Agent ☤）

> 来源：https://github.com/NousResearch/hermes-agent/blob/main/README.md
> 原文：oss-repos/hermes-agent/README.md
> 翻译日期：2026-11-03 ｜ 范围：全文 ｜ 方式：机器翻译初稿，未经人工校对
> 引用于：本仓 essay-study/hermes-2026.md 泛引 hermes 文档

## 官方中文 README 在哪里（指路）

上游已提供官方简体中文 README，可优先对照阅读：

- 本地克隆：`oss-repos/hermes-agent/README.zh-CN.md`
- GitHub 链接：https://github.com/NousResearch/hermes-agent/blob/main/README.zh-CN.md

本文件仍按 `docs/translations/README.md` 规范给出英文 `README.md` 的全文中译（见下）；官方中文版与本译文如有出入，以官方中文版与英文原文为准。本目录其余译文收录的是上述中文 README 之外、被本仓研究笔记引用到的英文文档，例如 `website/docs/user-guide/features/` 下的专题页。

---

<p align="center">
  <img src="assets/banner.png" alt="Hermes Agent" width="100%">
</p>

# Hermes Agent ☤
<p align="center">
  <a href="https://hermes-agent.nousresearch.com/">Hermes Agent</a> | <a href="https://hermes-agent.nousresearch.com/">Hermes Desktop</a>
</p>
<p align="center">
  <a href="https://hermes-agent.nousresearch.com/docs/"><img src="https://img.shields.io/badge/Docs-hermes--agent.nousresearch.com-FFD700?style=for-the-badge" alt="Documentation"></a>
  <a href="https://discord.gg/NousResearch"><img src="https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="Discord"></a>
  <a href="https://github.com/NousResearch/hermes-agent/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License: MIT"></a>
  <a href="https://nousresearch.com"><img src="https://img.shields.io/badge/Built%20by-Nous%20Research-blueviolet?style=for-the-badge" alt="Built by Nous Research"></a>
  <a href="README.zh-CN.md"><img src="https://img.shields.io/badge/Lang-中文-red?style=for-the-badge" alt="中文"></a>
  <a href="README.ur-pk.md"><img src="https://img.shields.io/badge/Lang-اردو-green?style=for-the-badge" alt="اردو"></a>
  <a href="README.es.md"><img src="https://img.shields.io/badge/Lang-Español-orange?style=for-the-badge" alt="Español"></a>
</p>

**由 [Nous Research](https://nousresearch.com) 打造的自我改进型 AI agent。** 它是唯一内置学习循环的 agent——从经验中创建 skill、在使用中改进 skill、主动提醒自己沉淀知识、检索自己过往的会话，并在跨会话的过程中不断加深对「你是谁」的建模。你可以把它跑在一台 5 美元的 VPS 上、一组 GPU 集群上，或几乎零闲置成本的 serverless 基础设施上。它不被绑在你的笔记本电脑上——它在云端 VM 干活时，你可以从 Telegram 跟它对话。

模型随你挑——[Nous Portal](https://portal.nousresearch.com)、OpenRouter、OpenAI、你自己的 endpoint，以及[其他许多 provider](https://hermes-agent.nousresearch.com/docs/integrations/providers)。用 `hermes model` 一键切换——不改代码，不被锁定。

<table>
<tr><td><b>真正的终端界面</b></td><td>完整的 TUI：多行编辑、斜杠命令自动补全、会话历史、中断并改向、流式工具输出。</td></tr>
<tr><td><b>住在你所在的地方</b></td><td>Telegram、Discord、Slack、WhatsApp、Signal 与 CLI——全部由单个 gateway 进程承载。语音备忘录转写、跨平台会话连续性。</td></tr>
<tr><td><b>闭环的学习循环</b></td><td>由 agent 自主整理的记忆，配合定期提醒。复杂任务之后自动创建 skill。skill 在使用中自我改进。基于 FTS5 的会话检索加 LLM 摘要，支持跨会话回忆。兼容 <a href="https://agentskills.io">agentskills.io</a> 开放标准。</td></tr>
<tr><td><b>定时自动化</b></td><td>内置 cron 调度器，可投递到任意平台。日报、夜间备份、每周审计——全部用自然语言描述，无人值守地运行。</td></tr>
<tr><td><b>可委派、可并行</b></td><td>派生隔离的 subagent 并行推进多条工作流。在 Desktop 里可在 Settings → Model → Subagents 下选择它们的 provider、模型与限额，再 Apply 完整路由。也可以写 Python 脚本通过 RPC 调用工具，把多步流水线折叠成零上下文成本的轮次。</td></tr>
<tr><td><b>跑在任何地方，不只是你的笔记本</b></td><td>六种内置终端后端——local、Docker、SSH、Modal、Daytona、Vercel Sandbox——外加 Singularity/Apptainer 等插件后端。Daytona 与 Modal 提供 serverless 持久化：agent 空闲时环境休眠、按需唤醒，会话之间几乎不花钱。可以跑在 5 美元的 VPS 上，也可以跑在 GPU 集群上。</td></tr>
<tr><td><b>面向研究就绪</b></td><td>批量轨迹生成、轨迹压缩，用于训练下一代 tool-calling 模型。</td></tr>
</table>

---

## 快速安装

### Linux、macOS、WSL2

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
```

### Windows（原生，PowerShell）

> **注意：** 原生 Windows 无需 WSL 即可运行 Hermes——CLI、gateway、TUI 与工具都能原生工作。如果你更想用 WSL2，上面那条 Linux/macOS 单行命令同样适用。发现 bug？欢迎[提 issue](https://github.com/NousResearch/hermes-agent/issues)。

在 PowerShell 中运行：

```powershell
iex (irm https://hermes-agent.nousresearch.com/install.ps1)
```

源码安装器会把 Python 3.14、Node.js、npm、ripgrep、FFmpeg 与 Python 依赖的安装交给 PM 处理。如果系统没有 Git，它会把经过校验的 Git for Windows 压缩包暂存到 Hermes 的工具仓库中，不会替换你系统里的 Git。MSIX/App Installer 包及其更新归属见[安装方式文档](https://hermes-agent.nousresearch.com/docs/getting-started/installation)。

> **Android / Termux：** 提供面向 aarch64 设备的签名 APT 仓库，含 `stable` 通道（打标签的发布版）与预发布 `canary` 通道。该软件包自带 Python、Node.js 与 TUI。请使用 [Termux 指南](https://hermes-agent.nousresearch.com/docs/getting-started/termux)，而不是桌面/服务器安装脚本。
>
> **Windows：** 原生 Windows 完全受支持——上面那条 PowerShell 单行命令会装好一切。如果你更想用 WSL2，Linux 那条命令同样适用。原生 Windows 安装在 `%LOCALAPPDATA%\hermes` 下；WSL2 则像 Linux 一样装在 `~/.hermes`。

安装完成后：

```bash
source ~/.bashrc    # 重新加载 shell（或：source ~/.zshrc）
hermes              # 开始聊天！
```

### 故障排查

#### Windows Defender 或杀毒软件把 `uv.exe` 标记为恶意软件

如果你的杀毒软件（Bitdefender、Windows Defender 等）把 Hermes `bin` 目录（`%LOCALAPPDATA%\hermes\bin\uv.exe`）里的 `uv.exe` 隔离了，这是**误报**。该文件是 Astral 的 `uv`——Hermes 捆绑的 Rust 编写的 Python 包管理器，用来管理自己的 Python 环境。基于机器学习的杀毒引擎经常误报未签名的 Rust 二进制文件，尤其是会下载并安装包的那类。

**要验证你的副本是正版：**

```powershell
# 如未安装 GitHub CLI，先安装
winget install --id GitHub.cli

# 登录 GitHub
gh auth login

# 运行校验
$uv = "$env:LOCALAPPDATA\hermes\bin\uv.exe"
$ver = (& $uv --version).Split(' ')[1]
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$zip = "$env:TEMP\uv.zip"
Invoke-WebRequest "https://github.com/astral-sh/uv/releases/download/$ver/uv-x86_64-pc-windows-msvc.zip" -OutFile $zip -UseBasicParsing
gh attestation verify $zip --repo astral-sh/uv
Expand-Archive $zip "$env:TEMP\uv_x" -Force
(Get-FileHash "$env:TEMP\uv_x\uv.exe").Hash -eq (Get-FileHash $uv).Hash
```

如果 attestation 显示「Verification succeeded」且最后一行输出 `True`，就没问题。

**把 Hermes 加入白名单：**
- **Windows Defender：** 以管理员身份运行 PowerShell → `Add-MpPreference -ExclusionPath "$env:LOCALAPPDATA\hermes\bin"`
- **Bitdefender：** 在 Bitdefender 控制台添加例外（Protection > Antivirus > Settings > Manage Exceptions）
- 白名单加**文件夹**，不要加文件哈希——Hermes 会更新 `uv`，每个版本哈希都会变

更多背景见上游 Astral 的 issue：[astral-sh/uv#13553](https://github.com/astral-sh/uv/issues/13553)、[astral-sh/uv#15011](https://github.com/astral-sh/uv/issues/15011)、[astral-sh/uv#10079](https://github.com/astral-sh/uv/issues/10079)。

---

## 快速上手

```bash
hermes              # 交互式 CLI——开始一段对话
hermes model        # 选择你的 LLM provider 与模型
hermes tools        # 配置启用哪些工具
hermes config set   # 设置单个配置项
hermes config get   # 打印单个配置项
hermes gateway      # 启动消息网关（Telegram、Discord 等）
hermes setup        # 运行完整设置向导（一次性配置所有东西）
hermes update       # 更新到最新版本
hermes doctor       # 诊断各种问题
```

📖 **[完整文档 →](https://hermes-agent.nousresearch.com/docs/)**

---

## 跳过收集 API key——Nous Portal

Hermes 照样支持任何你想要的 provider——这一点不会变。但如果你不想为模型、网页搜索、图像生成、TTS、云浏览器分别去凑五个 API key，**[Nous Portal](https://portal.nousresearch.com)** 用一份订阅全覆盖：

- **300+ 模型** —— 用 `/model <name>` 随便挑
- **Tool Gateway** —— 网页搜索、图像生成（FAL）、text-to-speech（OpenAI）、云浏览器（Browser Use），全部走你的订阅路由，无需额外账号

全新安装后只需一条命令：

```bash
hermes setup --portal
```

它会通过 OAuth 完成登录，把 Nous 设为你的 provider，并开启 Tool Gateway。随时用 `hermes portal info` 查看接通了哪些能力。完整细节见 [Tool Gateway 文档页](https://hermes-agent.nousresearch.com/docs/user-guide/features/tool-gateway)。

你仍然可以按工具自带 key——gateway 是按后端逐个开关的，不是全有或全无。

---

## CLI 与消息平台速查

Hermes 有两个入口：用 `hermes` 启动终端 UI，或者跑起 gateway，然后从 Telegram、Discord、Slack、WhatsApp、Signal 或 Email 跟它说话。一旦进入对话，很多斜杠命令在两种界面间是通用的。

| 操作 | CLI | 消息平台 |
| ------------------------------ | --------------------------------------------- | -------------------------------------------------------------------------------- |
| 开始聊天 | `hermes` | 运行 `hermes gateway setup` + `hermes gateway start`，然后给 bot 发消息 |
| 开启全新会话 | `/new` 或 `/reset` | `/new` 或 `/reset` |
| 切换模型 | `/model [provider:model]` | `/model [provider:model]` |
| 设置人格 | `/personality [name]` | `/personality [name]` |
| 重试或撤销上一轮 | `/retry`、`/undo` | `/retry`、`/undo` |
| 压缩上下文 / 查看用量 | `/compress`、`/usage`、`/insights [--days N]` | `/compress`、`/usage`、`/insights [days]` |
| 浏览 skill | `/skills` 或 `/<skill-name>` | `/<skill-name>` |
| 中断当前工作 | `Ctrl+C` 或发一条新消息 | `/stop` 或发一条新消息 |
| 平台相关状态 | `/platforms` | `/status`、`/sethome` |

完整命令列表见 [CLI 指南](https://hermes-agent.nousresearch.com/docs/user-guide/cli)与[消息网关指南](https://hermes-agent.nousresearch.com/docs/user-guide/messaging)。

---

## 文档

全部文档都在 **[hermes-agent.nousresearch.com/docs](https://hermes-agent.nousresearch.com/docs/)**：

| 板块 | 内容 |
| --------------------------------------------------------------------------------------------------- | ---------------------------------------------------------- |
| [Quickstart](https://hermes-agent.nousresearch.com/docs/getting-started/quickstart) | 2 分钟内完成安装 → 设置 → 第一段对话 |
| [CLI Usage](https://hermes-agent.nousresearch.com/docs/user-guide/cli) | 命令、键位、人格、会话 |
| [Configuration](https://hermes-agent.nousresearch.com/docs/user-guide/configuration) | 配置文件、provider、模型、全部选项 |
| [Messaging Gateway](https://hermes-agent.nousresearch.com/docs/user-guide/messaging) | Telegram、Discord、Slack、WhatsApp、Signal、Home Assistant |
| [Security](https://hermes-agent.nousresearch.com/docs/user-guide/security) | 命令审批、私信配对、容器隔离 |
| [Tools & Toolsets](https://hermes-agent.nousresearch.com/docs/user-guide/features/tools) | 40+ 工具、toolset 系统、终端后端 |
| [Skills System](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills) | 程序性记忆、Skills Hub、创建 skill |
| [Memory](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory) | 持久记忆、用户画像、最佳实践 |
| [MCP Integration](https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp) | 接入任意 MCP server 扩展能力 |
| [Cron Scheduling](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron) | 定时任务并投递到平台 |
| [Context Files](https://hermes-agent.nousresearch.com/docs/user-guide/features/context-files) | 塑造每段对话的项目上下文 |
| [Architecture](https://hermes-agent.nousresearch.com/docs/developer-guide/architecture) | 项目结构、agent 循环、关键类 |
| [Contributing](https://hermes-agent.nousresearch.com/docs/developer-guide/contributing) | 开发环境搭建、PR 流程、代码风格 |
| [CLI Reference](https://hermes-agent.nousresearch.com/docs/reference/cli-commands) | 全部命令与旗标 |
| [Environment Variables](https://hermes-agent.nousresearch.com/docs/reference/environment-variables) | 完整环境变量参考 |

---

## 从 OpenClaw 或其他 agent 迁移过来

如果你来自 OpenClaw、Claude Code、Codex CLI 或 Cursor，Hermes 可以导入你的设置、记忆与 skill（对 OpenClaw 还能在你要求时导入 API key）。

**设置过程中：** `hermes setup` 会询问是否从其他 agent 导入，预先选中它发现的那些（`~/.openclaw`、`~/.claude`、`~/.codex`、`~/.cursor`），安装官方 `agent-importers` 插件，并先做预览再执行导入。

**安装之后随时可做：**

```bash
hermes plugins install agent-importers          # 每个 profile 装一次
hermes import-agent openclaw                    # 交互式迁移（完整预设）
hermes import-agent openclaw --dry-run          # 预览将要迁移的内容
hermes import-agent openclaw --migrate-secrets  # 连同白名单内的 API key 一起迁移
hermes import-agent claude-code                 # 或 codex / cursor
```

从 OpenClaw 导入的内容：

- **SOUL.md** —— 人格文件
- **Memories** —— MEMORY.md 与 USER.md 条目
- **Skills** —— 用户创建的 skill → `~/.hermes/skills/openclaw-imports/`
- **Command allowlist** —— 审批模式
- **Messaging settings** —— 平台配置、允许的用户、工作目录
- **API keys** —— 白名单内的密钥（Telegram、OpenRouter、OpenAI、Anthropic、ElevenLabs），仅在带 `--migrate-secrets` 时迁移
- **TTS assets** —— 工作区音频文件
- **Workspace instructions** —— AGENTS.md（配合 `--workspace-target`）

`hermes claw migrate` 作为旧拼写仍然可用。参见 [OpenClaw 迁移指南](https://hermes-agent.nousresearch.com/docs/guides/migrate-from-openclaw)与[从其他 agent 导入](https://hermes-agent.nousresearch.com/docs/user-guide/import-from-other-agents)。

---

## 参与贡献

欢迎贡献！开发环境搭建、代码风格与 PR 流程见[贡献指南](https://hermes-agent.nousresearch.com/docs/developer-guide/contributing)。

可先看 [PM 开发者工作流](website/docs/reference/package-management.md#developer-workflow)，了解激活、日常使用、依赖变更与退出环境。
[Development Setup](CONTRIBUTING.md#development-setup) 覆盖独立的测试环境与校验命令。

---

## 社区

- 💬 [Discord](https://discord.gg/NousResearch)
- 📚 [Skills Hub](https://agentskills.io)
- 🐛 [Issues](https://github.com/NousResearch/hermes-agent/issues)
- 🔌 [computer-use-linux](https://github.com/avifenesh/computer-use-linux) —— 面向 Hermes 及其他 MCP host 的 Linux 桌面控制 MCP server，支持 AT-SPI 无障碍树、Wayland/X11 输入、截图与 compositor 窗口定位。
- 🔌 [HermesClaw](https://github.com/AaronWong1999/hermesclaw) —— 社区微信桥接：在同一个微信账号上同时跑 Hermes Agent 与 OpenClaw。

---

## 许可证

MIT —— 见 [LICENSE](LICENSE)。

由 [Nous Research](https://nousresearch.com) 打造。