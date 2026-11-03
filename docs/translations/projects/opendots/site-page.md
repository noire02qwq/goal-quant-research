# OpenDots 产品页（OpenDots | CopilotKit）

> 来源：https://www.copilotkit.ai/opendots
> 原文：官网页面（无本地克隆；抓取方式 `curl -sL --max-time 30`，2026-11-03 抓取，HTTP 200，HTML 231,310 字节）
> 翻译日期：2026-11-03 ｜ 范围：全文 ｜ 方式：机器翻译初稿，未经人工校对
> 引用于：docs/essay-study/opendots-2026.md、docs/brief-plan.md §3/§3.1

抓取说明：该页是 Next.js 客户端渲染，本次抓取拿到了完整 HTML，正文与 FAQ 答案（藏在内嵌的 RSC 载荷中）均已提取；页面中的产品演示是嵌在 DOM 里的界面模拟，其文字已按出现顺序一并翻译。

## 目录

- [页头横幅与导航](#top-banner)
- [主视觉](#hero)
- [主视觉演示界面](#hero-demo)
- [Spaces](#spaces)
- [Specialist Dots](#specialist-dots)
- [Dot 的电脑](#dot-computers)
- [保存前审批](#human-in-the-loop)
- [文本、通话与 Slack](#text-calls-slack)
- [基于 AG-UI 构建](#built-on-ag-ui)
- [状态：模板里都有什么](#status)
- [快速开始](#get-started)
- [常见问题](#faqs)
- [打造你自己的 Dot](#final-cta)
- [页脚](#footer)

<a id="top-banner"></a>

## 页头横幅与导航

- 顶部推广条：**Save your spot** —— 线上活动 · 11 月 5 日 上午 10 点（太平洋时间），主题 Building Enterprise-Ready Functional Copilots（打造面向企业就绪的功能型 Copilot），可点 **Get early access** 抢先体验。
- 另一条公告：**Introducing CopilotKit Soar - Powered by OpenBot**（CopilotKit Soar 亮相，由 OpenBot 驱动）。
- 顶部导航：Docs（文档）、Blog（博客）、Products（产品：Generative UI、AG-UI、Pricing）、Resources（资源）、Get Started、Talk to an Engineer。
- 产品下拉菜单：Products Overview、CopilotKit Intelligence、CopilotKit Frontend SDKs、Agentic Backend Connections、Channels、OpenBot、CopilotKit Soar、OpenMuse、OpenDots、OpenDuet。
- 解决方案：Agents inside your product、Agents in Slack and Teams、Agent workspace for employees、Self-improving agents、Product insights for agents。
- 资源：Learn the concepts、The Three Buckets of the Agentic World、MCP vs. A2A vs. AG-UI、What is agentic UI?、Human-in-the-loop、What is agent learning?、Examples & demos、All examples、Dojo、Generative UI、The Generative UI Spectrum、Overview、A2UI、MCP Apps、AG-UI。
- 另有 Pricing、Discord community、Talk to an Engineer、Get Started 等入口。

<a id="hero"></a>

## 主视觉

**徽标行：** OpenDots · Open-source template · Alpha（开源模板 · Alpha 阶段）

**Always-on AI coworkers for text, calls and Slack**（全天候在线的 AI 同事，覆盖文本、通话与 Slack）

每个 Dot 都有自己的角色、自己的权限和自己的电脑，它产出的成果会落成页面，供你继续编辑。克隆这个模板，自己托管，把它变成你自己的东西。

按钮：**View source**（查看源码）、**Talk to us**（与我们联系）。

<a id="hero-demo"></a>

## 主视觉演示界面

页面首屏是一整块产品界面模拟，展示一次完整的"提问 → 浏览 → 审批 → 保存"流程（界面文字按出现顺序）：

- 侧栏：`OpenDots`、`Search...`；**Spaces**：`Launch`（3）、`Research`（2）；**Dots**：`Scout`（11:42 AM，Saved "Acme Agents SDK — notes" to Launch，把《Acme Agents SDK — notes》保存到 Launch）、`Quill`（10:15 AM，Revised the launch brief opening，修改了启动简报的开头）、`Relay`（9:03 AM，Answered in #launch，在 #launch 中作答）；**Memory**、**Settings**；**DM**：`David McKay`。
- 会话区：`Scout`（Researcher · computer running，研究员 · 电脑运行中）。用户消息：*"Open Acme's Agents SDK announcement, summarize what they shipped, and save notes I can use in the launch brief."*（打开 Acme 的 Agents SDK 公告，总结他们发布了什么，并把能用在启动简报里的要点存下来。）Scout 回复：*"Opening it on my computer."*（我用我的电脑打开。）
- 内嵌浏览器：地址 `acme.dev/blog/agents-sdk`，页面标题 *Announcement — Introducing the Acme Agents SDK*，导航 Runtime / Tools / Traces；标注 `Opened in Scout's browser`、`Live`（实时）。
- 文件与终端：`Saved file ~/notes/acme-agents-sdk.md · 2.1 KB`；`Ran wc -l ~/notes/acme-agents-sdk.md → 41 lines`。
- 审批卡（Review before saving）：标题 *Acme Agents SDK — notes → Launch*，摘要 *"Acme shipped a hosted agent runtime with tool calling and traces. No UI layer, no human-in-the-loop primitives, and agents run on Acme's servers only."*（Acme 发布了带工具调用和 trace 的托管 agent runtime：没有 UI 层，没有 human-in-the-loop 原语，agent 只能跑在 Acme 的服务器上。）按钮 **Decline** / **Approve & save**；批准后显示 `Approved · saved to Launch`。
- 后续消息：*"Saved. The short version: they shipped the runtime, not the interface."*（已保存。一句话总结：他们发布的是 runtime，不是界面。）*"Nothing in the announcement covers what the user sees while an agent works — that's the gap the brief should lean on."*（公告完全没提 agent 工作时用户看到什么——简报就该抓住这个空档。）
- 输入框 `Ask anything`；右侧面板 **Computer**：Browser / Files / Terminal，状态 `Running`，当前页面 `acme.dev/blog/agents-sdk`；说明文案 *"Scout's browser profile and files persist across stop and start."*（Scout 的浏览器 profile 和文件在停止、启动之间持续保留。）按钮 **Take over**（接管）、**Permissions**（权限：Browser / Files / Shell）。

<a id="spaces"></a>

## Spaces

**Where the work ends up**（工作成果落在哪里）

Space 是工作文档的归宿。你可以在可搜索的资料库中浏览页面、把它们嵌套成子页面，并在专注的编辑器中打开任意一篇。可以自己写、把对话保存成页面，也可以让某个 Dot 起草和修改。

- **A real editor**（真编辑器）：支持格式化、slash commands、撤销与重做，随时可切到 Markdown 源码模式。
- **Edits that don't collide**（互不覆盖的编辑）：自动保存汇报进度，保存失败会保留草稿，修订检查防止过期修改覆盖更新内容。

页面列表示意：`Launch`（🚀 Launch brief，Edited by Quill）、`🔎 Acme Agents SDK — notes`（Saved by Scout）、`✅ Launch checklist`（Edited by you）；编辑器底部提示 `Type / for commands`。

<a id="specialist-dots"></a>

## Specialist Dots

**Coworkers with one job each**（各司其职的同事）

给每个 Dot 一个名字、一段角色说明、一些指示和它可用的工具。researcher 负责调研主题，writer 负责把发现写成草稿。每个 Dot 都有自己的会话，由你决定它能访问哪些 Space。

- **Permissions per Dot**（权限按 Dot 划分）：浏览器、文件、shell 和记忆按 Dot 逐个授予，writer 永远不会持有 researcher 的权限。
- **Always on**（始终在线）：安排周期性工作，它会在原会话的服务端运行，并支持暂停与重试。

卡片示意：`Scout · Researcher`（Browser / Files / Shell）、`Quill · Writer`（Memory）。

<a id="dot-computers"></a>

## Dot 的电脑

**Each Dot gets its own computer**（每个 Dot 都有自己的电脑）

Dot 可以拥有一台隔离的电脑，底层使用 OpenBot 的容器 supervisor。它的浏览器 profile 和工作区文件在停止、启动之间持续保留，每一步操作都会实时内嵌显示在聊天中。

- **Watch, then take over**（先旁观，再接管）：Computer 面板展示浏览器、文件、终端输出和活动记录，你可以随时接管。
- **Credentials stay on the server**（凭据留在服务器端）：服务 key 绝不下发到浏览器，每个 Dot 各有自己的电脑凭据。

命令序列示意：`Open Acme's announcement, summarize it, and save notes.` → `Open acme.dev/blog/agents-sdk` → `Save notes to ~/notes/acme.md` → `Verify the file with wc -l` → `Ask you before saving the page`（保存页面前先问你）；标题 `Scout's computer`。

<a id="human-in-the-loop"></a>

## 保存前审批

**Human in the loop — Nothing is saved until you say so**（human-in-the-loop——你点头之前，什么都不会保存）

先让 Dot 把草稿拿给你看。审阅卡会暂停对话，等你点 **Approve & save** 或 **Decline**；批准后会在你授权的 Space 中创建页面并把链接交给你，之后 Dot 继续往下走。

- **Retries don't duplicate**（重试不会产生重复）：重试保存时会找回已创建的那一页，而不是再写一份。

审阅卡示意：*Review before saving — Acme Agents SDK — notes → Launch*，摘要为 Acme 公告要点，按钮 **Decline** / **Approve & save**。

<a id="text-calls-slack"></a>

## 文本、通话与 Slack

**One conversation, wherever you are**（无论身在何处，都是同一段对话）

给 Dot 发消息、直接通话，或者在 Slack 里 @ 它，回头再接着聊。通话中，实时语音照常对话，另有一个独立的 compute agent 负责较耗时的工作，二者共用同一份上下文和同一套权限。

- **A proper call screen**（像样的通话界面）：实时计时器、你与 Dot 分开的字幕、麦克风静音、扬声器，以及可回到聊天继续的最小化视图。
- **Slack through Channels SDK**（经由 Channels SDK 接入 Slack）：托管的 Slack 连接，带显式的 workspace 与用户白名单。

通话示意：`Call with Scout`、`4 min · 1 task handed to the compute agent`（4 分钟 · 有 1 项任务移交给了 compute agent），Dot 说 *"Their docs don't mention approvals at all. Added that to your notes."*（他们的文档压根没提审批。已加进你的笔记。）；Slack 侧 `#launch` 中用户 @Scout 留言 `post the notes here too`（把笔记也发这儿）。

<a id="built-on-ag-ui"></a>

## 基于 AG-UI 构建

**From the team behind the protocol**（来自协议背后的团队）

AG-UI 是一套开放协议，规定 agent 如何与人们正在看的应用对话。它由我们撰写、由我们维护参考实现，而 OpenDots 从头到尾都构建在它之上。（页面标注 "AG-UI is adopted by"，即"AG-UI 的采用者"。）

- **AG-UI**：把流式消息、工具调用和 agent 状态送到界面，让电脑活动与审批卡随 agent 工作同步出现。
- **CopilotKit React SDK and runtime**：聊天、工具渲染器和 human-in-the-loop 暂停都是 CopilotKit 组件，可换样式也可替换。
- **Intelligence Threads**：持久的会话历史，每个页面、每位专家各一条 thread。
- **Channels SDK**：经由托管连接把 Dot 带进 Slack，遵循 OpenTag。
- **TanStack AI**：模型流式输出与服务端工具执行，兼容任何 OpenAI 协议的服务商。
- **OpenBot computers**：支撑每个 Dot 浏览器、文件与 shell 的容器 supervisor 与 computer service。

<a id="status"></a>

## 状态：模板里都有什么

**What's in the template**

OpenDots 是一个 alpha 阶段的模板，不是托管产品。由你来运行它、配置它的服务。下面是它包含的内容，以及每一部分验证到什么程度。

| 模块 | 内容 | 状态 |
| --- | --- | --- |
| Conversations（会话） | React SDK chat、Threads、按页面区分的会话、来源链接 | Tested with live services（已用真实服务验证） |
| Spaces and pages（空间与页面） | 资料库、可视化编辑器、slash commands、自动保存、修订检查 | Tested with live services |
| Dot computers（Dot 电脑） | 按 Dot 的浏览器 profile、文件、shell、接管、操作记录 | Tested with live services |
| Calls（通话） | WebRTC 语音、通话控制、有时长上限的会话、时间线回执 | Tested with live services |
| Specialist Dots（专家 Dot） | 角色、指示说明、按 Dot 的研究与记忆权限 | Tested locally（本地已验证） |
| Background work（后台任务） | 原会话中的定时轮次、暂停与重试 | Tested locally |
| Spoken delegation（语音委托） | 把通话中的耗时工作交给 compute agent | Needs live testing（需真实环境测试） |
| Slack | 托管 Channels SDK 连接，含 workspace 与用户白名单 | Needs live testing |

页面同时注明：当前在设计上就是单 owner；共同编辑、邀请、文件上传和多 Dot 群聊都列为仓库中的后续工作。

<a id="get-started"></a>

## 快速开始

**Running locally in five commands**（五条命令本地跑起来）

克隆、运行——在接入任何服务之前，你就可以开始写页面、配置 Dot。想开始聊天时，再把会话与模型设置写进 `.env`。

提示：需要 Node.js 24 和 npm；通话、Slack 和 Dot 电脑在仓库中各有专门的配置指南。

```sh
git clone https://github.com/CopilotKit/OpenDots.git
cd OpenDots
npm ci
cp .env.example .env
npm run dev
```

<a id="faqs"></a>

## 常见问题（FAQs / Questions）

**What is OpenDots?（OpenDots 是什么？）**
一个面向全天候 AI 同事的开源模板。每个 Dot 都是专家：有自己的角色、权限、会话，还可以有自己的电脑。你可以用文本、通话或 Slack 与它们交谈，它们的成果会以页面形式落在你的 Space 里。

**Is it a hosted product?（它是托管产品吗？）**
不是。它是一个由你自己克隆、自己运行的模板，MIT 许可，可完全自托管。模型服务商、会话服务，以及所需的 channel 或语音服务商，都由你配置。

**What do I need to run it?（运行它需要什么？）**
起步只需要 Node.js 24 和 npm。页面、Space 和 Dot 配置开箱即用。聊天需要会话服务和一个兼容 OpenAI 协议的模型服务商；通话需要语音服务商；Dot 电脑需要构建并接好 OpenBot 的 computer services。

**How is this different from OpenBot?（它和 OpenBot 有什么区别？）**
OpenBot 是面向整家公司的自托管 agent 平台，具备企业知识、管理控制和带权限感知的检索。OpenDots 则是个人 agent 工作区的起点——Spaces、专家 Dot、通话与 Slack——它的 Dot 电脑借用了 OpenBot 的 computer service。

**Can Dots work together on the same task?（Dot 能在同一任务上协作吗？）**
目前还不能。每位专家各有各的角色和会话。多 Dot 群聊与自动分工列为后续工作——我们更愿意说清已经发版的东西，而不是计划中的东西。

**Does a Dot's computer run on my machine?（Dot 的电脑跑在我机器上吗？）**
只有你主动配置了才会。computer 工具依赖那些固定版本的 computer services，未经配置的模板不会在你的宿主机上执行命令。每个 Dot 的电脑彼此隔离，各有自己的浏览器 profile 和文件。

**Can I use it for a team?（能给团队用吗？）**
目前它是为单 owner 构建的。README 建议为多用户部署优先补充身份、Space 成员关系和页面共同编辑——这些我们的工程师也可以帮你实现。

<a id="final-cta"></a>

## 打造你自己的 Dot（Build your own Dots）

克隆模板，把它变成你自己的：定义你的 Dot，接入你的服务，改造界面和工具以适配你的工作方式。如果你要在此之上做更大的东西，我们的工程师可以帮忙。

按钮：**View source**（查看源码）、**Talk to us**（与我们联系）。

<a id="footer"></a>

## 页脚

- 产品：Overview、Frontend SDKs、Backend Connections、Channels、CopilotKit Intelligence、OpenBot、OpenMuse、Pricing、Generative UI（Gen UI、A2UI、MCP Apps）、AG-UI Protocol。
- 开发者：Docs、Examples、Dojo、News、Blog。
- 公司：Contact Us、Careers、FAQ。
- 版权：© Tawkit, Inc. All rights reserved.（Tawkit, Inc. 保留所有权利。）；链接 Terms of service（服务条款）、Privacy Policy（隐私政策）。

---

抓取与降级说明（如实记录）：

- 抓取成功：`curl -sL --max-time 30 https://www.copilotkit.ai/opendots` 返回 HTTP 200、231,310 字节，无失败项。
- 正文与 7 条 FAQ 的答案均从 HTML 内嵌的 Next.js RSC 载荷中提取；FAQ 答案在可视 DOM 中由客户端渲染，初次文本抽取为空，改从载荷中解析得到。
- 页面顶部导航、产品下拉菜单与页脚为全站通用样板，已按栏目翻译罗列；各演示区的界面模拟文字按出现顺序翻译并保留英文界面术语。
- 图片（SVG/PNG 装饰图、Dot 头像）未做翻译，仅保留其文字说明。

