---
sidebar_position: 2
title: "Skills 系统"
description: "按需加载的知识文档 —— 渐进式披露、agent 自管的 skill 与 Skills Hub"
---

# 技能系统（Skills System）

> 来源：https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/skills.md
> 原文：oss-repos/hermes-agent/website/docs/user-guide/features/skills.md
> 翻译日期：2026-11-03 ｜ 范围：全文 ｜ 方式：机器翻译初稿，未经人工校对
> 引用于：docs/essay-study/hermes-2026.md、docs/brief-plan.md §3

Skill 是按需加载的知识文档，agent 可以在需要时载入。它们遵循**渐进披露**（progressive disclosure）模式以尽量减少 token 消耗，并兼容 [agentskills.io](https://agentskills.io/specification) 开放标准。

所有 skill 都放在 **`~/.hermes/skills/`** ——这是主目录，也是唯一事实来源。全新安装时，内置 skill 会从仓库复制过来；从 Hub 安装的和 agent 创建的 skill 也放在这里。agent 可以修改或删除任何 skill。

你也可以让 Hermes 指向**外部 skill 目录**——与本地目录一同被扫描的额外文件夹，见下文[外部 skill 目录](#外部-skill-目录)。

另见：

- [内置技能目录](../../reference/skills-catalog.md)
- [官方可选技能目录](../../reference/optional-skills-catalog.md)

## 目录

- [从网站安装](#从网站安装)
- [从白纸开始](#从白纸开始)
- [使用 Skill](#使用-skill)
  - [一条命令叠多个 skill](#一条命令叠多个-skill)
- [从各种来源学一个 skill（`/learn`）](#从各种来源学一个-skilllearn)
  - [大体量来源会变成 knowledge-base skill](#大体量来源会变成-knowledge-base-skill)
- [渐进披露](#渐进披露)
  - [对话期间新增的 skill](#对话期间新增的-skill)
- [SKILL.md 格式](#skillmd-格式)
  - [平台限定的 skill](#平台限定的-skill)
- [Skill 输出与媒体投递](#skill-输出与媒体投递)
  - [强制文档式投递：`[[as_document]]`](#强制文档式投递as_document)
  - [条件激活（兜底 skill）](#条件激活兜底-skill)
- [加载时的安全设置](#加载时的安全设置)
  - [Skill 配置项](#skill-配置项)
- [Skill 目录结构](#skill-目录结构)
  - [咨询性的 SkillEvaluator 扫描](#咨询性的-skillevaluator-扫描)
- [外部 Skill 目录](#外部-skill-目录)
  - [工作方式](#工作方式)
  - [示例](#示例)
- [重定向 Skill 创建位置（`skills.create_dir`）](#重定向-skill-创建位置skillscreate_dir)
- [项目本地 Skill](#项目本地-skill)
  - [信任一个项目](#信任一个项目)
  - [优先级](#优先级)
  - [重名 skill](#重名-skill)
  - [扫描期隔离](#扫描期隔离)
  - [非交互式界面（cron、API、ACP）](#非交互式界面cronapiacp)
- [Skill 技能包（Skill Bundles）](#skill-技能包skill-bundles)
  - [快速示例](#快速示例)
  - [YAML schema](#yaml-schema)
  - [管理 bundle](#管理-bundle)
  - [行为](#行为)
  - [什么时候 bundle 胜过逐个安装](#什么时候-bundle-胜过逐个安装)
- [Agent 管理的 Skill（skill_manage 工具）](#agent-管理的-skillskill_manage-工具)
  - [Agent 何时创建 Skill](#agent-何时创建-skill)
  - [一条 skill 长什么样](#一条-skill-长什么样)
  - [动作](#动作)
  - [门控 agent 的技能写入（`skills.write_approval`）](#门控-agent-的技能写入skillswrite_approval)
- [Skills Hub](#skills-hub)
  - [常用命令](#常用命令)
  - [支持的 hub 来源](#支持的-hub-来源)
  - [已集成的 hub 与注册表](#已集成的-hub-与注册表)
  - [安全扫描与 `--force`](#安全扫描与---force)
  - [信任级别](#信任级别)
  - [更新生命周期](#更新生命周期)
  - [发布自定义 skill tap](#发布自定义-skill-tap)
- [内置 skill 的更新（`hermes skills reset`）](#内置-skill-的更新hermes-skills-reset)
  - [斜杠命令（聊天内）](#斜杠命令聊天内)

## 从网站安装

公开的 [Skills Hub](/skills) 上每张可安装卡片都有一个 **Install in Hermes** 按钮。它会打开 Hermes Desktop，并带上一个 URL 编码、标明来源的 skill 目标：可选 skill 用 `official/...`，ClawHub 用 `clawhub/...`，内置 skill 则用明确的仓库路径而不是含糊的裸名。卡片上的 CLI 命令用的也是同一个目标：

```text
hermes://skill/install?identifier=official%2Fsecurity%2F1password
```

Desktop 会显示 **Install "skill-name"?**，并分列 **Source** 与 **Install to** 两行。点取消不做任何改动。确认后对话框先显示 **Installing…**，然后是 **Installed** 与一条完成通知；出错时错误留在对话框里，方便你重试。安装走的是正常的 Skills Hub 流水线（安全扫描、动作日志、已装列表刷新）。如果确认框开着的时候你切换了 profile 或连接，需要重新打开链接以指向新目标；链接不能绕过扫描，也不能选别的 profile。已开着的对话会在下一条消息时得知新 skill。

`skill/install` 路由需要较新的 Desktop 构建。如果应用缺失或不认这个链接，就展开卡片复制它的 CLI 安装命令。

## 从白纸开始

默认情况下每个 profile 都会被植入内置技能目录，每次 `hermes update` 也会补上新增的内置 skill。如果你想要一个**没有内置 skill**、且更新后仍保持空的 profile，有两条路：

**安装时**（适用于默认的 `~/.hermes` profile）：安装器没有 `--no-skills` 选项。它的设置阶段在你选择 Blank Slate 配置时会问要不要植入内置目录；回答「否」就会写下文提到的那个退出标记。非交互式安装会植入目录，所以想让 profile 保持为空的话，事后运行 `hermes skills opt-out`。

**创建 profile 时**（具名 profile）：

```bash
hermes profile create research --no-skills
```

**对已装好的 profile**（默认或具名），在运行时切换：

```bash
hermes skills opt-out            # stop future seeding — nothing on disk is touched
hermes skills opt-out --remove   # also delete UNMODIFIED bundled skills (confirms first)
hermes skills opt-in --sync      # undo: remove the marker and re-seed now
```

这些路径都会往 profile 目录写入一个 `.no-bundled-skills` 标记。标记存在期间，安装器、`hermes update` 以及任何 skill 同步都会跳过该 profile 的内置 skill 植入。删掉标记（或运行 `hermes skills opt-in`）即可重新启用。

:::note 默认即安全
`hermes skills opt-out` 只停止*未来*的植入——它绝不会删除磁盘上已有的东西。可选的 `--remove` 选项**只**在内置 skill 未被改动（与 Hermes 安装的版本逐字节相同）时才删除它们。你编辑过的 skill、从 Hub 安装的 skill、以及你自己写的 skill 永远保留。
:::

## 使用 Skill

每个已安装的 skill 都会自动成为一个斜杠命令：

```bash
# In the CLI or any messaging platform:
/excalidraw sketch the request flow for our API
/axolotl help me fine-tune Llama 3 on my dataset
/github-pr-workflow create a PR for the auth refactor
/youtube-content summarize https://youtu.be/dQw4w9WgXcQ

# Just the skill name loads it and lets the agent ask what you need:
/excalidraw
```

### 一条命令叠多个 skill

在一条消息开头串起多个斜杠命令，就能同时调用多个 skill——每个开头的 `/skill` 词元（最多 5 个）都会被加载，剩下的部分成为你的指令：

```bash
/github-pr-workflow /test-driven-development fix issue #123 and open a PR
```

解析遇到第一个不是已安装 skill 的词元就停止，所以恰好以 `/` 开头的参数（比如文件路径）绝不会被吞掉：

```bash
/ocr-and-documents ~/.hermes/cache/scratch/scan.pdf extract the tables   # loads one skill; ~/.hermes/cache/scratch/scan.pdf is the argument
```

反复使用的组合，优先考虑 [skill bundle](#skill-技能包skill-bundles)——一条短命令即可达到同样效果。

（Plan 模式用法相同，但如今它是内置命令：`/plan [request]` 会让 Hermes 按需检查上下文，写一份 markdown 实施计划而不是直接执行任务，并把结果保存在相对当前 workspace/backend 工作目录的 `.hermes/plans/` 下。）

也可以用自然对话与 skill 交互：

```bash
hermes chat --toolsets skills -q "What skills do you have?"
hermes chat --toolsets skills -q "Show me the axolotl skill"
```

## 从各种来源学一个 skill（`/learn`）

`/learn` 是把你已有的知识——或一堆参考材料——变成可复用 skill 的快捷方式，不必手写 `SKILL.md`。它是开放式的：指向*任何你能描述的东西*，agent 用它手头已有的工具收集材料，然后撰写一个遵循[本仓撰写规范](#skillmd-格式)的 skill（描述 ≤60 字符、标准章节顺序、用 Hermes 工具的措辞框架、不发明命令）。

```bash
# A local SDK or doc directory — read with read_file / search_files
/learn the REST client in ~/projects/acme-sdk, focus on auth + pagination

# An online doc page — fetched with web_extract
/learn https://docs.example.com/api/quickstart

# The workflow you just walked the agent through in this conversation
/learn how I just deployed the staging server

# Pasted notes / a described procedure
/learn filing an expense: open the portal, New > Expense, attach the receipt, submit

# A whole book, paper stack, or large docs corpus — becomes a knowledge-base skill
/learn ~/books/designing-data-intensive-applications.pdf
```

### 大体量来源会变成 knowledge-base skill

当来源是一本书、一摞论文、一份规范或一个大文档目录时，agent 不会把它硬塞进一个文件，也不会压缩成有损摘要。它会撰写一个**扩展型 knowledge-base skill**：一份精炼的 `SKILL.md`，承载来源的核心心智模型加一份索引，外加 `references/` 下每个章节或主题一个蒸馏文件（来源配得上的话再加术语表或速查表）。参考文件在问题真正需要之前不花任何成本——agent 用 `skill_view` 按需加载，所以查询成本与答案成正比，而不是与来源体量成正比。用新材料对同一主题重跑 `/learn`，会把新材料折进既有 skill，而不是造出一个重复项。

这种蒸馏综合的是结构——框架、定义、决策规则、反模式——绝不复制来源文本的原段落。

因为取材由活着的 agent 完成，`/learn` 在 CLI、消息 gateway、TUI 和 dashboard 里行为一致，也能跑在任何 terminal backend 上（本地、Docker、远程），并不存在单独的摄取引擎。在 **dashboard** 里，Skills 页面有一个 **Learn a skill** 按钮，打开的面板含目录字段、URL 字段和一个开放式文本框；它组装出一条 `/learn` 请求并在聊天里执行。

它不占用模型工具面：`/learn` 构造一个受规范引导的 prompt，作为普通回合交给 agent。agent 用 `skill_manage` 工具保存结果，所以如果你开了[写入审批门](#门控-agent-的技能写入skillswrite_approval)，它同样生效。

## 渐进披露

Skill 使用一种省 token 的加载模式：

```
Level 0: skills_list()           → [{name, description, category}, ...]   (~3k tokens)
Level 1: skill_view(name)        → Full content + metadata       (varies)
Level 2: skill_view(name, path)  → Specific reference file       (varies)
```

agent 只在真正需要时才加载 skill 的完整内容。

### 对话期间新增的 skill

agent 用来挑选的那份技能列表是会话 system prompt 的一部分，它保持固定，provider 的 prompt 缓存才能持续生效。当对话开着的时候有 skill 被安装、创建或删除（来自 Skills Hub、另一个终端里的 `hermes skills install`、插件、curator 或 agent 自己），你发给 agent 的下一条消息会带一则简短说明，列出新 skill 的名字与描述以及被移除的 skill。这则说明每次变更只发一次；system prompt 本身要到下一次 compaction 才吸收变更。为此不需要 `/reload-skills`，它仍然只负责刷新 `/skill-name` 斜杠命令。

## SKILL.md 格式

```markdown
---
name: my-skill
description: Brief description of what this skill does
version: 1.0.0
platforms: [macos, linux]     # Optional — restrict to specific OS platforms
metadata:
  hermes:
    tags: [python, automation]
    category: devops
    fallback_for_toolsets: [web]    # Optional — conditional activation (see below)
    requires_toolsets: [terminal]   # Optional — conditional activation (see below)
    config:                          # Optional — config.yaml settings
      - key: my.setting
        description: "What this controls"
        default: "value"
        prompt: "Prompt for setup"
---

# Skill Title

## When to Use
Trigger conditions for this skill.

## Procedure
1. Step one
2. Step two

## Pitfalls
- Known failure modes and fixes

## Verification
How to confirm it worked.
```

### 平台限定的 skill

Skill 可以用 `platforms` 字段把自己限制到特定操作系统：

| 值 | 匹配 |
|-------|---------|
| `macos` | macOS（Darwin） |
| `linux` | Linux |
| `windows` | Windows |

```yaml
platforms: [macos]            # macOS only (e.g., iMessage, Apple Reminders, FindMy)
platforms: [macos, linux]     # macOS and Linux
```

设置之后，在不兼容的平台上该 skill 会自动从 system prompt、`skills_list()` 和斜杠命令中隐藏。省略时，skill 在所有平台都会加载。

## Skill 输出与媒体投递

当 skill 的响应（或任何 agent 响应）里出现一个媒体文件的裸绝对路径——例如 `/home/user/screenshots/diagram.png`——gateway 会自动识别它，从可见文本中剔除该路径，并把文件原生投递到用户的聊天里（Telegram 照片、Discord 附件等），而不是把裸路径留在消息里。

就音频而言，`[[audio_as_voice]]` 指令会把音频文件升级为支持平台（Telegram、WhatsApp）上的原生语音气泡。

### 强制文档式投递：`[[as_document]]`

有时你要的是内联预览的**反面**：希望文件作为可下载附件投递，而不是被重压成图片气泡。典型例子是高分辨率截图或图表——Telegram 的 `sendPhoto` 会把它重压到 1280 px、约 200 KB，可读性尽毁。而用 `sendDocument` 发送的 1–2 MB PNG 能完整保留原始字节。

如果响应（或其中任意文本——通常是最后一行）含有字面指令 `[[as_document]]`，那么从该响应提取出的所有媒体路径都会以文档/文件附件而非图片气泡投递：

```
Here is your rendered chart:

/home/user/.hermes/cache/chart-q4-2025.png

[[as_document]]
```

该指令在投递前会被剥掉，用户永远看不到。粒度刻意做成「按响应全有或全无」：发出一次 `[[as_document]]`，同一响应里的所有图片路径都按文档投递。这与 `[[audio_as_voice]]` 的作用范围一致。

以下情况可从 skill 里使用它：

- 你产出的截图或图表用户需要以文件形式拿到（在别的工具里编辑、归档、完整分享）。
- 默认的有损预览会掩盖细节（小字号文字、像素级精确的示意图、对色彩敏感的渲染）。

没有独立文档通道的平台（如 SMS）会回退到它们现有的附件机制。

### 条件激活（兜底 skill）

Skill 可以根据当前会话里有哪些工具可用，自动显示或隐藏自己。这最适合**兜底 skill**——免费或本地的替代品，只应在付费工具不可用时出现。

```yaml
metadata:
  hermes:
    fallback_for_toolsets: [web]      # Show ONLY when these toolsets are unavailable
    requires_toolsets: [terminal]     # Show ONLY when these toolsets are available
    fallback_for_tools: [web_search]  # Show ONLY when these specific tools are unavailable
    requires_tools: [terminal]        # Show ONLY when these specific tools are available
```

| 字段 | 行为 |
|-------|----------|
| `fallback_for_toolsets` | 所列工具集**可用**时 skill **隐藏**，缺失时显示。 |
| `fallback_for_tools` | 同上，但检查的是单个工具而非工具集。 |
| `requires_toolsets` | 所列工具集不可用时 skill **隐藏**，可用时显示。 |
| `requires_tools` | 同上，但检查的是单个工具。 |

**示例：**内置的 `duckduckgo-search` skill 用 `fallback_for_toolsets: [web]`。当你设置了 `FIRECRAWL_API_KEY`，web 工具集可用，agent 用 `web_search`——DuckDuckGo skill 保持隐藏。API key 缺失时 web 工具集不可用，DuckDuckGo skill 就会作为兜底自动出现。

没有任何条件字段的 skill 行为与从前完全一致——始终显示。

## 加载时的安全设置

Skill 可以声明必需的环境变量，同时不从可发现列表中消失：

```yaml
required_environment_variables:
  - name: TENOR_API_KEY
    prompt: Tenor API key
    help: Get a key from https://developers.google.com/tenor
    required_for: full functionality
```

遇到缺失值时，Hermes 只在该 skill 真正于本地 CLI 中被加载时才安全地询问。你也可以跳过设置继续用这个 skill。消息类界面从不在聊天里索要机密——它们会提示你改用本地的 `hermes setup` 或 `~/.hermes/.env`。

一旦设置，声明的环境变量会**自动透传**给 `execute_code` 与 `terminal` 沙箱——skill 的脚本可以直接用 `$TENOR_API_KEY`。非 skill 的环境变量请用 `terminal.env_passthrough` 配置项，详见[环境变量透传](../security.md#environment-variable-passthrough)。

### Skill 配置项

Skill 也可以声明存在 `config.yaml` 里的非机密配置项（路径、偏好）：

```yaml
metadata:
  hermes:
    config:
      - key: myplugin.path
        description: Path to the plugin data directory
        default: "~/myplugin-data"
        prompt: Plugin data directory path
```

这些设置存放在 config.yaml 的 `skills.config` 之下。`hermes config migrate` 会逐项询问未配置的设置，`hermes config show` 会展示它们。skill 加载时，其解析后的配置值会被注入上下文，agent 因此自动知道配置值。

详见 [Skill 设置](../configuration.md#skill-settings) 与 [创建 Skill — 配置项](../../developer-guide/creating-skills.md#config-settings-configyaml)。

## Skill 目录结构

```text
~/.hermes/skills/                  # Single source of truth
├── mlops/                         # Category directory
│   ├── axolotl/
│   │   ├── SKILL.md               # Main instructions (required)
│   │   ├── references/            # Additional docs
│   │   ├── templates/             # Output formats
│   │   ├── scripts/               # Helper scripts callable from the skill
│   │   ├── examples/              # Referenced example outputs
│   │   └── assets/                # Supplementary files
│   └── vllm/
│       └── SKILL.md
├── devops/
│   └── deploy-k8s/                # Agent-created skill
│       ├── SKILL.md
│       └── references/
├── .hub/                          # Skills Hub state
│   ├── lock.json
│   ├── quarantine/
│   └── audit.log
└── .bundled_manifest              # Tracks seeded bundled skills
```

第三方 URL 与 GitHub 安装会带上 `SKILL.md`，以及它在 `references/`、`templates/`、`scripts/`、`assets/`、`examples/` 下引用到的确切本地文件。未被引用的仓库文件不会复制。Hermes 扫描完整的隔离包，并把来源 URL、精确内容哈希、扫描器版本、发现项、时间戳与「新鲜还是缓存」状态记入 `skills/.hub/lock.json`。

### 咨询性的 SkillEvaluator 扫描

除了内置安全扫描器（它执行上文的安装策略），Hermes 还可以对每次 Hub 安装额外跑一遍 [NVIDIA SkillEvaluator](https://github.com/NVIDIA/SkillEvaluator) 的 Tier 1 检查，作为第二意见。Tier 1 是确定性且无需密钥的——PII 检测（泄露的邮箱、个人路径、连接串）、unicode 走私检测、脚本 lint、许可证合规，以及经 [NVIDIA SkillSpector](https://github.com/NVIDIA/SkillSpector) 的静态安全扫描。

该扫描**仅供参考**：发现项会连同文件与行号打印在安装确认之前，安装照常继续。看起来像真实凭据的发现项（私钥、云访问密钥、token、带凭据的连接串）会标红，方便你在决定前复核被标记的行。PII 类发现项只是信息性的——上游扫描器存在已知的误报类别（例如 `git@github.com` 这种 SSH 写法、文档示例邮箱），所以它们从不阻断任何安装。

要启用它，请安装可选的扫描器二进制（第二个为 `security` 检查提供支持；没有它，该项检查只会报「未运行」）：

```bash
uv tool install --python 3.13 \
  "skillevaluator @ git+https://github.com/NVIDIA/SkillEvaluator.git@v0.1.0"
uv tool install "git+https://github.com/NVIDIA/SkillSpector.git@v2.9.5"
```

PATH 上没有该二进制时，扫描会被静默跳过。要彻底关掉：

```yaml
skills:
  tier1_advisory: false
```

dashboard 的 Browse-hub 扫描按钮会在响应里（`tier1` 字段）给出同样的咨询性数据，与内置扫描器的结论并列。

## 外部 Skill 目录

如果你在 Hermes 之外维护 skill——例如一个被多个 AI 工具共用的 `~/.agents/skills/` 目录——可以让 Hermes 也扫描这些目录。

在 `~/.hermes/config.yaml` 的 `skills` 段下加 `external_dirs`：

```yaml
skills:
  external_dirs:
    - ~/.agents/skills
    - /home/shared/team-skills
    - ${SKILLS_REPO}/skills
```

路径支持 `~` 展开与 `${VAR}` 环境变量替换。

### 工作方式

- **本地创建、原地更新**：新建的 agent skill 写入 `~/.hermes/skills/`（配置了 `skills.create_dir` 时写那里——见下文）。agent 使用 `skill_manage` 的 `patch`（定点或整文件重写）、`write_file`、`remove_file`、`delete` 等动作时，既有 skill 就在它被发现的位置被修改，包括 `external_dirs` 下的 skill。
- **外部目录不是写保护边界**：如果某个外部 skill 目录对 Hermes 进程可写，agent 管理的 skill 更新就能改那个目录里的文件。若共享外部 skill 必须保持只读，请用文件系统权限或单独的 profile/工具集设置。
- **优先级**：同一 skill 名存在于多个目录时，优先级高的目录在所有地方都胜出——技能索引、`skills_list`、`hermes skills list`、`skill_view`、斜杠命令、`-s` 预载与 cron：`project → local（~/.hermes/skills/）→ skills.create_dir → external_dirs`。被遮蔽的副本会记一条 shadowed 日志。见[重名 skill](#重名-skill)。
- **完整集成**：外部 skill 会出现在 system prompt 索引、`skills_list`、`skill_view` 里，也会成为 `/skill-name` 斜杠命令——与本地 skill 没有区别。
- **不存在的路径被静默跳过**：配置的目录不存在时，Hermes 不报错地忽略它。这对可能并非每台机器都有的可选共享目录很有用。

### 示例

```text
~/.hermes/skills/               # Local (primary, read-write)
├── devops/deploy-k8s/
│   └── SKILL.md
└── mlops/axolotl/
    └── SKILL.md

~/.agents/skills/               # External (shared, mutable if writable)
├── my-custom-workflow/
│   └── SKILL.md
└── team-conventions/
    └── SKILL.md
```

这四个 skill 都会出现在你的技能索引里。如果你在本地新建一个叫 `my-custom-workflow` 的 skill，它会遮蔽外部那份。

## 重定向 Skill 创建位置（`skills.create_dir`）

默认情况下 agent 把新 skill 写进 profile 本地的 `~/.hermes/skills/`。如果你希望 agent 创建的 skill 落到别处——共享的「大脑」目录、git 跟踪的仓库、或全机队共用的 skill 卷——就在 `skills` 段下设置 `create_dir`：

```yaml
skills:
  create_dir: /opt/brain/skills
```

这会改变什么：

- **`skill_manage` 的 create 写到那里。** 新 skill（含类别子目录）建在 `create_dir` 之下而不是本地 skill 目录。目录不存在时在首次写入时创建。
- **agent 的指令跟随配置。** 每条点名 skill 创建路径的面向 agent 的指令——`skill_manage` 工具描述及相关 prompt 文本——都会动态渲染成配置的目录，因此 agent 会被告知在那里创建 skill。不需要改 system prompt，也不需要文件系统花招。
- **该目录被完整集成。** `create_dir` 下的 skill 与本地目录一同被扫描：它们出现在技能索引、`skills_list`、`skill_view`、斜杠命令里，也能像本地 skill 一样被 patch 或删除。
- **其余一切仍留在本地。** 既有 skill 仍在其所在位置被原地修改；内置 skill 同步、Hub 与 curator 继续作用于 profile 本地目录。

路径支持 `~` 展开与 `${VAR}` 替换；相对路径相对你的 Hermes home 解析。把 `create_dir` 设成本地 skill 目录等于不设。

## 项目本地 Skill

仓库可以自带 skill，只对在该项目内启动的会话生效——这与其他 agent harness 用于仓库级配置的模式相同。当你在某个 git 检出里启动 Hermes 时，它会在这些位置找 skill：

```text
<project-root>/.hermes/skills/    # Hermes-native location
<project-root>/.agents/skills/    # cross-tool convention (shared with other agent CLIs)
```

项目根是离得最近的含 `.git` 的祖先目录（worktree 与 submodule 也算）。

### 信任一个项目

Skill 是 agent 要遵循的流程文档，所以 Hermes **不会**从任意克隆的仓库里自动加载它们。你第一次在带项目 skill 的仓库里运行 Hermes 时，横幅会显示一条提示：

```text
◆ 3 project skill(s) found in /home/you/myproject but not loaded — run `hermes skills trust` to enable them.
```

信任该仓库一次（在仓库内部运行，或显式传路径）：

```bash
hermes skills trust             # trust the current repo
hermes skills trust ~/myproject # or explicitly
hermes skills untrust           # revoke
```

受信任的根目录存在 `~/.hermes/config.yaml` 的 `skills.trusted_project_dirs` 里。设置 `skills.project_discovery: false` 可彻底关闭该功能（不扫描、不提示）。

### 优先级

项目 skill 是**最高优先级的一层**：`project → local（~/.hermes/skills/）→ skills.create_dir → external_dirs`。在该仓库内的会话里，名为 `deploy` 的项目 skill 会覆盖同名的 profile 或内置 skill——这正是要点：随仓库附带的 skill 在自己的主场获胜，而不动你的全局 profile。项目 skill 在 agent 的技能索引里会打上 `[project]` 标签，来源一目了然。

与外部目录一样，项目 skill 目录被视为仓库所有：自主的技能维护（curator）从不修改它们，新建的 agent skill 一律去 `~/.hermes/skills/`。

### 重名 skill

每个界面都用同样的方式解析 skill 名：

- **跨目录**时，优先级高的目录胜出（`project → local → skills.create_dir → external_dirs`），同一相对路径也一样（本地和外部都有 `productivity/xdup` 时加载本地那份）。被遮蔽的副本隐藏起来并记一条警告。
- **同一目录内**两个*不同*的 skill 撞名时，绝不猜测加载哪一个。两者都按各自的完整相对路径列出（例如 `a/one` 与 `b/two`），加载裸名会失败并报 `Ambiguous skill name dup-demo: use one of a/one, b/two`。`hermes -s dup-demo` 与 cron 任务报的也是这条消息。同一个 skill 的完全相同副本（符号链接视图或逐字节相同的拷贝）解析到最浅的路径。

插件 skill 用它们自己的 `plugin:skill` 名，永远不会与这些冲突。

### 扫描期隔离

信任是仓库级的决定，但仓库的 skill 内容每次 `git pull` 都可能变。为了堵上这个缺口，每个项目 skill 在进入索引之前，都会用 Skills Hub 安装所用的同一套安全扫描器扫一遍。扫描结论为**危险**的 skill（prompt 注入指令、凭据外窃命令、隐藏文本花招）会被隔离：它不出现在技能索引、`skills_list`、斜杠命令里，按名加载也会被拒绝并给出解释性错误。扫描结果按内容哈希缓存在 `~/.hermes/cache/project_skill_scans/`（绝不在你的仓库内），skill 内容变化时自动重扫。

### 非交互式界面（cron、API、ACP）

Cron 任务和其他非交互式界面继承你的交互式信任决定——它们从不询问，也从不自动信任。项目根从该界面的工作目录解析（cron 任务的 `workdir`，走与 terminal 工具相同的机制）。`workdir` 位于你先前信任过的仓库内的 cron 任务会加载该仓库的项目 skill；位于未信任或未决定仓库中的任务一个也不加载。

在 TUI 与 Desktop 里，项目根跟随每个**会话的 workspace**（侧边栏显示的目录 / workspace 选择器设定的目录），所以在受信任仓库里启动 `hermes --tui` 会把该项目的 skill 注册为斜杠命令，即使 `terminal.cwd` 仍是默认占位符 `.`；在两个仓库里各开一个会话，各自看到各自的。

## Skill 技能包（Skill Bundles）

Skill bundle 是把若干 skill 归到一条斜杠命令下的小 YAML 文件。运行 `/<bundle-name>` 时，bundle 里列出的每个 skill 一次性全部加载——当某类任务总是需要同一组 skill 配合时很有用。

### 快速示例

```bash
# Create a bundle for backend feature work
hermes bundles create backend-dev \
  --skill github-code-review \
  --skill test-driven-development \
  --skill github-pr-workflow \
  -d "Backend feature work — review, test, PR workflow"
```

然后在 CLI 或任何 gateway 平台上：

```
/backend-dev refactor the auth middleware
```

agent 收到的是一条把三个 skill 全部加载进去的用户消息，斜杠命令之后的文本作为用户指令附在其后。

### YAML schema

Bundle 存放在 **`~/.hermes/skill-bundles/<slug>.yaml`**，形如：

```yaml
name: backend-dev
description: Backend feature work — review, test, PR workflow.
skills:
  - github-code-review
  - test-driven-development
  - github-pr-workflow
instruction: |
  Always start by writing failing tests, then implement.
  Open the PR through the standard workflow with co-author tags.
```

字段：

- `name`（可选——默认取文件名主干）——bundle 的显示名。斜杠命令会把它归一化成连字符 slug（`Backend Dev` → `/backend-dev`）。
- `description`（可选）——在 `/bundles` 与 `hermes bundles list` 里显示的短文本。
- `skills`（必填、非空列表）——skill 名，或相对你 skill 目录的路径。用与 `/<skill-name>` 相同的标识符。
- `instruction`（可选）——追加在已加载 skill 内容之前的额外指引。适合固化「我们总是这样一起用它们」。

### 管理 bundle

```bash
# List all installed bundles
hermes bundles list

# Inspect one bundle
hermes bundles show backend-dev

# Create a bundle interactively (omit --skill flags to enter them one per line)
hermes bundles create research

# Overwrite an existing bundle
hermes bundles create backend-dev --skill ... --force

# Delete a bundle
hermes bundles delete backend-dev

# Re-scan ~/.hermes/skill-bundles/ and report changes
hermes bundles reload
```

在聊天会话里，`/bundles` 会列出每个已安装 bundle 及其 skill。

### 行为

- **Slug 冲突时 bundle 优先于单个 skill。** 如果你把 bundle 命名为 `research`，同时又有一个叫 `research` 的 skill，`/research` 调用的是 bundle。这是有意为之——你用命名选择了这个 bundle。
- **缺失的 skill 被跳过，不是致命错误。** bundle 列了 `skill-foo` 而你没装，bundle 仍会加载能解析出来的那些，agent 会收到一条列出被跳过项的说明。
- **Bundle 在所有界面都可用**——交互式 CLI、TUI、dashboard 聊天，以及每个 gateway 平台（Telegram、Discord、Slack……）——因为分发逻辑与单个 skill 命令集中在同一处。
- **Bundle 不会使 prompt 缓存失效。** 它们在调用时生成一条全新的用户消息，与 `/<skill-name>` 的做法相同——不改动 system prompt。

### 什么时候 bundle 胜过逐个安装

以下情况用 bundle：

- 你总是为某个反复出现的任务搭配同一组 skill（`/backend-dev`、`/release-prep`、`/incident-response`）。
- 你想用比连敲好几个 `/skill` 调用短一个字符的心智模型。
- 你想交付一个全队通用的「任务画像」：把 bundle 的 YAML 提交进共享 dotfiles 仓库，再软链进 `~/.hermes/skill-bundles/`。

bundle 只是一个 YAML 别名 —— 它不替你安装 skill。skill 本身必须已经存在（在 `~/.hermes/skills/` 或某个外部 skill 目录里）。否则 bundle 调用只会跳过缺失的那些。

## Agent 管理的 Skill（skill_manage 工具）

agent 可以用 `skill_manage` 工具创建、更新、删除自己的 skill。这是 agent 的**程序性记忆**——当它摸索出一个不平凡的工作流，就把这个方法存成 skill 供日后复用。

Skill 与记忆在自我改进循环里分工协作：记忆存放那些应当始终在上下文里的小而持久的事实，skill 存放只在相关时才加载的较长流程。后台 review 可以在会话结束后建议或暂存 skill 变更，但下文的写入审批门让你可以要求这些变更先经过人工复核再落地。

### Agent 何时创建 Skill

System prompt 会要求 agent 用 `skill_manage` 把不平凡的工作流记下来供日后复用。实践中包括：

- 它理清了一套值得重复的多步流程时
- 它碰到错误或死胡同、最终找到可行路径时
- 用户纠正了它的做法时

### 一条 skill 长什么样

Skill 是「按你的规格、以最高效最正确的方式做某类任务」的说明：按顺序的流程、行得通的命令与工具调用、你期望结果长什么样、以及那些费过时间的坑。无论写在前台回合、后台 review，还是 curator 的整合流程里，它记录的都是**教训，不是日志**：一个坑是一条可泛化的规则，加上一句*为什么*（机制），附在它影响的那一步上，只说一遍。事故叙述、PR 或 issue 编号、日期、引用的聊天记录都不是 skill 内容；规则必须离开背后的故事也能独立成立。始终生效的规则放在 `SKILL.md` 本体里；`references/` 存一小撮按主题命名的文件（一张决策表、一份配方、provider 的怪癖），原地扩展，而不是每次会话堆一个文件。Skill 也不去复述每回合已经加载的东西（仓库的 `AGENTS.md`、工具 schema）。

`skill_manage` 在 `create`、`SKILL.md` 的 patch、以及 `references/` 写入时会跑一个咨询性 linter，并把发现项放在工具结果里返回。专为这种形态设了三条规则：`incident-log-shape`（正文密布 PR/issue 编号）、`references-sprawl`（参考文件超过 60 个）、`oversized-body`（`SKILL.md` 正文超过约 2.4 万字符——`skill_view` 会整份加载，且在会话余下时间里一直占着上下文）。它们只警告，从不阻断写入。

### 动作

| 动作 | 用途 | 关键参数 |
|--------|---------|------------|
| `create` | 从零新建 skill | `name`、`content`（完整 SKILL.md）、可选 `category` |
| `patch` | 定点修改（首选） | `name`、`old_string`、`new_string` |
| `patch` 加 `content` | 大幅结构重写（替换整个 SKILL.md；`edit` 是遗留别名） | `name`、`content` |
| `delete` | 彻底删除 skill | `name` |
| `write_file` | 新增/更新辅助文件 | `name`、`file_path`、`file_content` |
| `remove_file` | 删除辅助文件 | `name`、`file_path` |

每个动作都以自己的形状声明：文本槽只属于一个动作（`content` → create / 整文件重写，`new_string` → 定点 patch，`file_content` → write_file）。带着别的动作槽位的操作——例如在 `create` 上带 `file_content`——对工具 schema 来说非法（语法约束的本地后端根本不会产生它），即使真的到达，也会在**批次里任何操作被应用之前**被拒绝，错误信息会指出文本放在了哪个键、该挪到哪里。

:::tip
更新优先用定点 `patch`——它比整文件重写省 token，因为工具调用里只出现改动的文本。
:::

### 门控 agent 的技能写入（`skills.write_approval`）

默认情况下 agent 可以随意写 skill——包括来自[后台自我改进 review](./memory.md#控制记忆写入write_approval) 的写入（它在每个回合后运行）。如果你希望每次技能写入都先审批（小模型会误判自己学到的东西、安全环境、或只是想盯着自我改进循环），打开写入审批门：

```yaml
skills:
  write_approval: false     # false = write freely (default) | true = require approval
```

`write_approval: true` 时，每一次 `skill_manage` 写入（create / edit / patch / delete / write_file / remove_file）都会被**暂存**而不是直接提交——SKILL.md 太大，不适合内联复核，所以无论写入来自前台回合还是后台 review，一律暂存。暂存的写入存放在 `~/.hermes/pending/skills/` 之下，重启后仍在，并用你熟悉的、与危险命令相同的批准/拒绝流程复核：

```
/skills pending             # list staged skill writes + a one-line gist each
/skills diff <id>           # full unified diff (best viewed in CLI or dashboard)
/skills approve <id>        # apply it (or 'all')
/skills reject <id>         # drop it (or 'all')
/skills approval on         # turn the gate on (or 'off') and persist it
```

复核界面在交互式 CLI 与消息平台上都可用（聊天气泡里 diff 会截断——完整 diff 请在 CLI 或 pending JSON 文件里看）。记忆写入在 `memory.write_approval` 下有同一道门，见[控制记忆写入](./memory.md#控制记忆写入write_approval)。

要彻底禁止 agent 改动某个*特定* skill，把它锁定：`hermes curator lock <skill>`（或 Desktop 里的锁定开关）。被锁的 skill 仍可读、仍可自动加载，但 `skill_manage`、`write_file`、`patch`、`terminal` 在任何会话里都会拒绝改动它；你自己的编辑照常生效。见[锁定一个 skill](./curator.md#lock-一个-skill)。

> 另一个设置 `skills.guard_agent_created` 是内容扫描器（危险模式启发式），不是审批门——两者相互独立。见[守卫 agent 创建的技能写入](../configuration.md#guard-on-agent-created-skill-writes)。

## Skills Hub

浏览、搜索、安装与管理来自在线注册表、`skills.sh`、直连的 well-known skill 端点以及官方可选 skill 的技能。

未加过滤的搜索（CLI、TUI 与 dashboard）由一份缓存的集中索引回答，该索引覆盖外部注册表。索引会定期重建，所以当它对你的查询没有匹配时，Hermes 还会直接问 `skills.sh`、ClawHub、LobeHub 和 well-known 端点——几分钟前才发布的 skill 也能出现。这份额外查询最多占 8 秒搜索预算，慢注册表不会把「没找到」变成长时间等待。自定义 GitHub tap 不在这条回退路径里（用 `--source github` 搜它们，或等索引追上后再搜），`--source nvidia` 这类 provider 过滤也不会触发它（那些注册表不带 provider 数据）。

### 常用命令

```bash
hermes skills browse                              # Browse all hub skills (official first)
hermes skills browse --source official            # Browse only official optional skills
hermes skills search kubernetes                   # Search all sources
hermes skills search react --source skills-sh     # Search the skills.sh directory
hermes skills search https://mintlify.com/docs --source well-known
hermes skills inspect openai/skills/k8s           # Preview before installing
hermes skills install openai/skills/k8s           # Install with security scan
hermes skills install official/security/1password
hermes skills install skills-sh/vercel-labs/json-render/json-render-react --force
hermes skills install well-known:https://mintlify.com/docs/.well-known/skills/mintlify
hermes skills install https://sharethis.chat/SKILL.md              # Direct URL (+ referenced support files)
hermes skills install https://example.com/SKILL.md --name my-skill # Override name when frontmatter has none
hermes skills list --source hub                   # List hub-installed skills
hermes skills check                               # Check installed hub skills for upstream updates
hermes skills update                              # Reinstall hub skills with upstream changes when needed
hermes skills audit                               # Re-scan all hub skills for security
hermes skills uninstall k8s                       # Remove a hub skill
hermes skills reset google-workspace              # Un-stick a bundled skill from "user-modified" (see below)
hermes skills reset google-workspace --restore    # Also restore the bundled version, deleting your local edits
hermes skills publish skills/my-skill --to github --repo owner/repo
hermes skills snapshot export setup.json          # Export skill config
hermes skills tap add myorg/skills-repo           # Add a custom GitHub source
```

### 支持的 hub 来源

| 来源 | 示例 | 说明 |
|--------|---------|-------|
| `official` | `official/security/1password` | Hermes 附带的可选 skill。 |
| `skills-sh` | `skills-sh/vercel-labs/agent-skills/vercel-react-best-practices` | 可用 `hermes skills search <query> --source skills-sh` 搜索。当 skills.sh 的 slug 与仓库目录不同时，Hermes 会解析别名式 skill。 |
| `well-known` | `well-known:https://mintlify.com/docs/.well-known/skills/mintlify` | 直接由网站上的 `/.well-known/skills/index.json` 提供的 skill。用站点或文档 URL 搜索。 |
| `url` | `https://sharethis.chat/SKILL.md` | 指向 `SKILL.md` 的直接 HTTP(S) URL，外加显式引用的辅助文件。名字解析顺序：frontmatter → URL slug → 交互式询问 → `--name` 选项。 |
| `github` | `openai/skills/k8s` | 直接的 GitHub 仓库/路径安装与自定义 tap。 |
| `clawhub`、`lobehub`、`browse-sh` | 各来源自己的标识符 | 社区或市场集成。 |

### 已集成的 hub 与注册表

Hermes 目前与以下技能生态和发现源集成：

#### 1. 官方可选 skill（`official`）

这些维护在 Hermes 仓库本身，以内置信任安装。

- 目录：[官方可选技能目录](../../reference/optional-skills-catalog)
- 仓库内来源：`optional-skills/`
- 示例：

```bash
hermes skills browse --source official
hermes skills install official/security/1password
```

#### 2. skills.sh（`skills-sh`）

这是 Vercel 的公开技能目录。Hermes 可以直接搜索它、查看 skill 详情页、解析别名式 slug，并从底层源仓库安装。

- 目录：[skills.sh](https://skills.sh/)
- CLI/工具仓库：[vercel-labs/skills](https://github.com/vercel-labs/skills)
- Vercel 官方 skill 仓库：[vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills)
- 示例：

```bash
hermes skills search react --source skills-sh
hermes skills inspect skills-sh/vercel-labs/json-render/json-render-react
hermes skills install skills-sh/vercel-labs/json-render/json-render-react --force
```

#### 3. Well-known skill 端点（`well-known`）

这是基于 URL 的发现机制，面向发布 `/.well-known/skills/index.json` 的站点。它不是单一的集中式 hub——而是一种 web 发现约定。

- 在线端点示例：[Mintlify docs skills index](https://mintlify.com/docs/.well-known/skills/index.json)
- 参考服务端实现：[vercel-labs/skills-handler](https://github.com/vercel-labs/skills-handler)
- 示例：

```bash
hermes skills search https://mintlify.com/docs --source well-known
hermes skills inspect well-known:https://mintlify.com/docs/.well-known/skills/mintlify
hermes skills install well-known:https://mintlify.com/docs/.well-known/skills/mintlify
```

#### 4. 直连 GitHub skill（`github`）

Hermes 可以直接从 GitHub 仓库与基于 GitHub 的 tap 安装。当你已经知道仓库/路径，或想加自己的自定义源仓库时，这很有用。

默认 tap（无需任何设置即可浏览）：

- [openai/skills](https://github.com/openai/skills)
- [anthropics/skills](https://github.com/anthropics/skills)
- [huggingface/skills](https://github.com/huggingface/skills)
- [NVIDIA/skills](https://github.com/NVIDIA/skills) —— NVIDIA 验证过的 skill（签名 `skill.oms.sig` + 治理文件 `skill-card.md`）
- [wandb/skills](https://github.com/wandb/skills)、[qdrant/skills](https://github.com/qdrant/skills)、[pinecone-io/skills](https://github.com/pinecone-io/skills) —— 各厂商为其产品自带的 skill
- [garrytan/gstack](https://github.com/garrytan/gstack)
- [K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills) 与 [synthetic-sciences/openscience](https://github.com/synthetic-sciences/openscience) —— 约 480 个科研 skill（生信、化学、物理、ML 训练、学术工具），归在一个 `science` 类别下。社区信任：每次安装都过安全扫描。许多 skill 用自己的许可证包装第三方工具（部分是 GPL；KEGG 非学术用途需要商业授权）——请逐个检查 skill 的前置条件。

- 示例：

```bash
hermes skills install openai/skills/k8s
hermes skills tap add myorg/skills-repo
```

**类别分组（`skills.sh.json`）。** GitHub tap 可以在其仓库根目录放一个 `skills.sh.json` 文件，遵循 [skills.sh schema](https://skills.sh/schemas/skills.sh.schema.json)。它的 `groupings`（每项含一个 `title` 和一组 skill 名）在索引时被读取，成为 [Skills Hub](https://hermes-agent.nousresearch.com/docs) 页面上显示的类别标签——替代原先靠标签猜测的做法。这是通用机制：任何附带该文件的 tap 都能获得真实分类，无需改动 Hermes 侧代码。

```json
{
  "$schema": "https://skills.sh/schemas/skills.sh.schema.json",
  "groupings": [
    { "title": "Inference AI", "skills": ["dynamo-recipe-runner", "dynamo-router-sla"] },
    { "title": "Decision Optimization", "skills": ["cuopt-developer", "cuopt-install"] }
  ]
}
```

#### 5. ClawHub（`clawhub`）

作为社区来源集成的第三方 skill 市场。

- 站点：[clawhub.ai](https://clawhub.ai/)
- Hermes source id：`clawhub`

#### 6. LobeHub（`lobehub`）

Hermes 可以搜索 LobeHub 公开目录里的 agent 条目，并把它们转换成可安装的 Hermes skill。

- 站点：[LobeHub](https://lobehub.com/)
- 公开 agent 索引：[chat-agents.lobehub.com](https://chat-agents.lobehub.com/)
- 底层仓库：[lobehub/lobe-chat-agents](https://github.com/lobehub/lobe-chat-agents)
- Hermes source id：`lobehub`

#### 7. browse.sh（`browse-sh`）

Hermes 与 [browse.sh](https://browse.sh) 集成——Browserbase 收录的 200 多个站点专用浏览器自动化 SKILL.md（Airbnb、Amazon、arXiv、12306.cn、Etsy、Xero 等等）。每个 skill 描述如何端到端地驱动一个网站，适合配合 Hermes 的浏览器工具以及你已安装的任何浏览器自动化 skill 使用。

- 站点：[browse.sh](https://browse.sh/)
- 目录 API：`https://browse.sh/api/skills`
- Hermes source id：`browse-sh`
- 信任级别：`community`

```bash
hermes skills search airbnb --source browse-sh
hermes skills inspect browse-sh/airbnb.com/search-listings-ddgioa
hermes skills install browse-sh/airbnb.com/search-listings-ddgioa
```

标识符形如 `browse-sh/<hostname>/<task-id>`，与 browse.sh 目录暴露的 slug 对应。内容经每个 skill 的详情端点解析（`/api/skills/<slug>` → `skillMdUrl`），不走目录的 GitHub `sourceUrl`。

#### 8. 直连 URL（`url`）

直接从任意 HTTP(S) URL 安装 `SKILL.md`——当作者把 skill 托管在自己站点上（没有 hub 收录、也没有 GitHub 路径可输）时很有用。Hermes 还会抓取 `references/`、`templates/`、`scripts/`、`assets/`、`examples/` 下显式引用的文件，然后扫描并安装完整包。

- Hermes source id：`url`
- 标识符：URL 本身（无需前缀）
- 范围：`SKILL.md` 加上白名单目录里被精确引用的辅助文件。Hermes 不会枚举或复制宿主上无关的文件。

```bash
hermes skills install https://sharethis.chat/SKILL.md
hermes skills install https://example.com/my-skill/SKILL.md --category productivity
```

名字解析顺序：

1. SKILL.md YAML frontmatter 里的 `name:` 字段（推荐——每个格式规范的 skill 都有）。
2. URL 路径的父目录名（例如 `.../my-skill/SKILL.md` → `my-skill`，或 `.../my-skill.md` → `my-skill`），前提是它是个合法标识符（`^[a-z][a-z0-9_-]*$`）。
3. 带 TTY 的终端上的交互式询问。
4. 在非交互式界面上（TUI 内的 `/skills install` 斜杠命令、gateway 平台、脚本），给出一条指向 `--name` 覆盖项的清晰错误。

```bash
# Frontmatter has no name and the URL slug is unhelpful — supply one:
hermes skills install https://example.com/SKILL.md --name sharethis-chat

# Or inside a chat session:
/skills install https://example.com/SKILL.md --name sharethis-chat
```

信任级别始终是 `community`——与其他来源一样跑同一套安全扫描。URL 作为安装标识符保存，所以想刷新时 `hermes skills update` 会自动从同一 URL 重新抓取。

### 安全扫描与 `--force`

所有从 hub 安装的 skill 都要过一道**安全扫描器**，检查数据外窃、prompt 注入、破坏性命令、供应链信号及其他威胁。

`hermes skills inspect ...` 现在也会在有上游元数据时展示出来：

- 仓库 URL
- skills.sh 详情页 URL
- 安装命令
- 每周安装量
- 上游安全审计状态
- well-known 索引/端点 URL

当你已经复核过某个第三方 skill、想覆盖一次非危险级的策略阻断时，用 `--force`：

```bash
hermes skills install skills-sh/anthropics/skills/pdf --force
```

重要行为：

- `--force` 可以覆盖 caution/warn 类发现项的策略阻断。
- `--force` **不能**覆盖 `dangerous` 扫描结论。
- 官方可选 skill（`official/...`）视为内置信任，不显示第三方警告面板。

### 信任级别

| 级别 | 来源 | 策略 |
|-------|--------|--------|
| `builtin` | 随 Hermes 发行 | 始终信任 |
| `official` | 仓库里的 `optional-skills/` | 内置信任，无第三方警告 |
| `trusted` | 受信任的注册表/仓库，如 `openai/skills`、`anthropics/skills`、`huggingface/skills`、`NVIDIA/skills`、`wandb/skills`、`qdrant/skills`、`pinecone-io/skills` | 比社区来源更宽松的策略 |
| `community` | 其余全部（`skills.sh`、well-known 端点、自定义 GitHub 仓库、多数市场） | 非危险发现项可用 `--force` 覆盖；`dangerous` 结论仍被阻断 |

### 更新生命周期

Hub 现在记录了足够的来源信息，可以重新检查已安装 skill 的上游副本：

```bash
hermes skills check          # Report which installed hub skills changed upstream
hermes skills update         # Reinstall only the skills with updates available
hermes skills update react   # Update one specific installed hub skill
hermes skills update react --force   # Overwrite a skill you've edited locally
```

它用存储的来源标识符加上当前上游包内容哈希来检测漂移。

对于缺失或非目录的安装（`orphaned`），以及不安全或无法解析的已记录路径（`invalid_install`），检查会跳过网络请求。缺失目录的条目可用 `hermes skills uninstall <name>` 移除；无效路径则需要先检查并修复当前 profile 的 `skills/.hub/lock.json` 再重试。没有任何条目会被自动删除。

有效安装继续使用其来源 adapter 既有的同步抓取与传输超时。更新检查没有严格的总时限：某个已安装条目的来源不可达或很慢，仍可能拖慢后面的条目。

你本地编辑过的 skill（磁盘内容与安装时记录的哈希不再一致）会被 `hermes skills update` **跳过**，所以你的改动绝不会被悄悄覆盖。要强制以上游版本替换，传 `--force`。

:::tip GitHub 速率限制
Skills hub 操作使用 GitHub API，未认证用户每小时 60 次请求。一次安装大约花两次 API 调用（仓库及其文件树）；skill 的文件本身从 `raw.githubusercontent.com` 下载，不计入限额。如果安装或搜索时遇到限流错误，在 `.env` 文件里设置 `GITHUB_TOKEN`，限额会提到每小时 5000 次。这种情况下的错误信息会带上可操作的提示。
:::

### 发布自定义 skill tap

如果你想分享一组精选 skill——给团队、给组织、或公开发布——可以把它们发布为一个 **tap**：一个别的 Hermes 用户用 `hermes skills tap add <owner/repo>` 添加的 GitHub 仓库。不需要服务器，不用注册注册表，不用发布流水线，只要一个装着 `SKILL.md` 的目录。

#### 仓库布局

Tap 可以是任何 GitHub 仓库（公开或私有——私有需要 `GITHUB_TOKEN`），布局如下：

```
owner/repo
├── skills/                       # default path; configurable per-tap
│   ├── my-workflow/
│   │   ├── SKILL.md              # required
│   │   ├── references/           # optional supporting files
│   │   ├── templates/
│   │   └── scripts/
│   ├── another-skill/
│   │   └── SKILL.md
│   └── third-skill/
│       └── SKILL.md
└── README.md                     # optional but helpful
```

规则：

- 每个 skill 各自住在 tap 根路径（默认 `skills/`）下的一个目录里。
- 目录名成为该 skill 的安装 slug。
- 每个 skill 目录必须含一个带标准 [SKILL.md frontmatter](#skillmd-格式) 的 `SKILL.md`（`name`、`description`，外加可选的 `metadata.hermes.tags`、`version`、`author`、`platforms`、`metadata.hermes.config`）。
- `references/`、`templates/`、`scripts/`、`assets/` 这类子目录会在安装时随 `SKILL.md` 一起下载。
- 目录名以 `.` 或 `_` 开头的 skill 被忽略。

Hermes 通过列出 tap 路径下的每个子目录、逐个探测 `SKILL.md` 来发现 skill。

#### 最小 tap 示例

```
my-org/hermes-skills
└── skills/
    └── deploy-runbook/
        └── SKILL.md
```

`skills/deploy-runbook/SKILL.md`：

```markdown
---
name: deploy-runbook
description: Our deployment runbook — services, rollback, Slack channels
version: 1.0.0
author: My Org Platform Team
metadata:
  hermes:
    tags: [deployment, runbook, internal]
---

# Deploy Runbook

Step 1: ...
```

推到 GitHub 之后，任何 Hermes 用户都能订阅并安装：

```bash
hermes skills tap add my-org/hermes-skills
hermes skills search deploy
hermes skills install my-org/hermes-skills/deploy-runbook
```

#### 非默认路径

如果你的 skill 不在 `skills/` 之下（往既有项目里加一棵 `skills/` 子树时很常见），编辑 `~/.hermes/skills/.hub/taps.json` 里的 tap 条目：

```json
{
  "taps": [
    {"repo": "my-org/platform-docs", "path": "internal/skills/"}
  ]
}
```

`hermes skills tap add` CLI 给新 tap 的默认值是 `path: "skills/"`；需要别的路径就直接改文件。`hermes skills tap list` 会显示每个 tap 的生效路径。

#### 直接安装单个 skill（不添加 tap）

用户也可以从任何公开 GitHub 仓库安装单个 skill，而不必把整个仓库加成 tap：

```bash
hermes skills install owner/repo/skills/my-workflow
```

当你只想分享一个 skill、又不想让用户订阅你的整个注册表时，这很有用。

#### Tap 的信任级别

新 tap 默认被赋予 `community` 信任。从这些 tap 安装的 skill 会走标准安全扫描，首次安装时显示第三方警告面板。如果你的组织或某个广受信任的来源应当获得更高信任，把它的仓库加进 `tools/skills_guard.py` 的 `TRUSTED_REPOS`（需要一个 Hermes core PR）。

#### Tap 管理

```bash
hermes skills tap list                                # show all configured taps
hermes skills tap add myorg/skills-repo               # add (default path: skills/)
hermes skills tap remove myorg/skills-repo            # remove
```

在运行中的会话里：

```
/skills tap list
/skills tap add myorg/skills-repo
/skills tap remove myorg/skills-repo
```

Tap 存放在 `~/.hermes/skills/.hub/taps.json`（按需创建）。

## 内置 skill 的更新（`hermes skills reset`）

Hermes 在仓库的 `skills/` 里附带了一组内置 skill。安装时以及每次 `hermes update` 时，一次同步会把它们复制进 `~/.hermes/skills/`，并在 `~/.hermes/skills/.bundled_manifest` 记一份清单，把每个 skill 名映射到它同步时的内容哈希（即**来源哈希**）。

每次同步时，Hermes 会重算你本地副本的哈希并与来源哈希比较：

- **未改动** → 可以安全拉取上游变更，复制新的内置版本进来，记录新的来源哈希。
- **已改动** → 视为**用户已修改**并永久跳过，所以你的编辑永远不会被踩掉。

skill 内部生成的运行时缓存（`__pycache__/`、`.pytest_cache/`、`.mypy_cache/`、`.ruff_cache/`，以及躺在 `.py` 旁边的 `.pyc`）不计入哈希，所以跑一个 skill 的辅助脚本绝不会把它标成用户已修改，也不会让它从 `hermes skills list-modified` / `diff` 里消失。

这层保护很好，但有一处锋利的边：如果你编辑过内置 skill，之后又想放弃改动、直接从 `~/.hermes/hermes-agent/skills/` 复制粘贴回内置版本，清单里存的仍是上次成功同步时那份*旧*来源哈希。你新粘贴的内容（当前内置哈希）与那个过期的来源哈希对不上，于是同步会一直把它标为用户已修改。

`hermes skills reset` 是逃生口：

```bash
# Safe: clears the manifest entry for this skill. Your current copy is preserved,
# but the next sync re-baselines against it so future updates work normally.
hermes skills reset google-workspace

# Full restore: also deletes your local copy and re-copies the current bundled
# version. Use this when you want the pristine upstream skill back.
hermes skills reset google-workspace --restore

# Non-interactive (e.g. in scripts or TUI mode) — skip the --restore confirmation.
hermes skills reset google-workspace --restore --yes
```

同一条命令在聊天里以斜杠命令形式可用：

```text
/skills reset google-workspace
/skills reset google-workspace --restore
```

:::note Profile
每个 profile 在自己的 `HERMES_HOME` 下有自己的 `.bundled_manifest`，所以 `hermes -p coder skills reset <name>` 只影响那个 profile。
:::

### 斜杠命令（聊天内）

同样的命令都能用 `/skills` 前缀：

```text
/skills browse
/skills search react --source skills-sh
/skills search https://mintlify.com/docs --source well-known
/skills inspect skills-sh/vercel-labs/json-render/json-render-react
/skills install openai/skills/skill-creator --force
/skills check
/skills update
/skills reset google-workspace
/skills list
```

官方可选 skill 仍使用 `official/security/1password`、`official/mcp/fastmcp` 这类标识符。

参考文献从略，见原文。
