# OpenMuse 官网产品页（OpenMuse | CopilotKit 官网）

> 来源：https://www.copilotkit.ai/openmuse
> 原文：官网页面 https://www.copilotkit.ai/openmuse（curl 抓取成功，HTTP 200，约 185 KB；仓库内无对应本地文件）
> 翻译日期：2026-11-03 ｜ 范围：全文 ｜ 方式：机器翻译初稿，未经人工校对
> 引用于：docs/essay-study/openmuse-2026.md、docs/brief-plan.md §3/§3.1

> 说明：页面为 Next.js 动态渲染，FAQ 的答案在嵌入的 RSC 数据里而非可见 DOM 中，已从该数据中提取翻译；页面顶部导航、促销横幅与页脚链接列表按结构译出，纯图标（[SVG]）略去。

**Open source · Alpha · MIT｜OpenMuse · Built with CopilotKit**

## Ask it. Watch it work.（开口问，看它做）

一个自带浏览器、终端、文件的个人 agent，你关掉 App 之后它照样把活干完。开源，支持 iOS、Android 和 web，兼容任何 agent harness。

[View on GitHub] · [Talk to us]

（页面切换标签：Web / Mobile）

## An agent that gets better / Build it once. Watch it learn.（一次构建，看它越用越聪明）

OpenMuse 是起点；让 CopilotKit Intelligence 在上线之后持续让它变强。

1. **Build with any agent or frontend（用任何 agent 或前端来构建）** —— 把你已经在用的 agent harness 和前端带来即可。OpenMuse 说的是 AG-UI，各个部件都可以随意替换。
2. **Intelligence learns and proposes skills（Intelligence 学习并提议 skill）** —— CopilotKit Intelligence 从你的 agent 身上学习，为它提议新的 skill。
3. **Approved skills flow into the agent（批准后自动注入 agent）** —— 批准一个 skill，它就会被自动吸收进你的 agent。没有你的批准，什么都不会被加进去。

链接：How agent learning works（agent 学习是如何工作的）｜Explore CopilotKit Intelligence（了解 CopilotKit Intelligence）

## What's inside / Everything a personal agent needs, in one app（一个应用装下个人 agent 所需的一切）

说出你想要的结果，跟着计划走，审阅关键操作，最后回来拿成果。下面每个界面在今天的 alpha 版里都能跑。

- **Chat** —— 流式 AG-UI 聊天，内嵌邮件、浏览器、PDF、计划和理财卡片。发送/停止共用一个胶囊按钮，停止不会丢草稿。
- **Agent computer** —— 常驻的 Chromium profile 加一个可选的 Linux 终端。随时打开同一个会话接管操作。
- **Activity** —— 可持久化的任务计划，带进度、审批和回执。可暂停、恢复、取消或重试，被打断的工作会接着跑。
- **Ideas** —— 带出处证据的建议。可以编辑、接受或忽略，你已经处理过的会自动消失。
- **Goals & tracking** —— 带里程碑的目标，外加对公开网页的周期性检查：内容变化、可用性，或价格越过你设定的阈值。
- **Documents** —— 从邮件附件到填好的 PDF，再到一份待审阅的回复。原生和 web 端都能查看、翻页、缩放、分享。
- **Gmail & Calendar** —— 完整邮件会话、草稿，以及通过 Google OAuth 变更日历。每一次发送、每一次事件变更都在等你审阅。
- **Personal context** —— 你的名字、语气、头像和记忆，全都可以编辑。后台更新会以应用内通知送达。
- **AG-UI Streams** —— 一个稳定的主对话，外加可重命名、归档、恢复和回放的侧边聊天，由 CopilotKit Intelligence 持久化。

## iOS, Android, and web / One codebase, in your pocket and on your desk（一份代码，既在口袋里也在桌上）

基于 CopilotKit React Native 构建，同一套无头 hooks 同时驱动手机 App 和 web 应用。

- **Its own computer（它自己的计算机）** —— 浏览器和文件始终跟着你的 agent。随时打开会话接管。
- **Real documents（真实文档）** —— 读一个附件，填好你要的表单字段，再交回一份副本供你审阅。
- **Rich results（丰富的结果）** —— 导入交易 CSV，得到一份可交互的支出摘要，附带一个储蓄目标行动。

## Quick start / Running locally in five commands（五条命令本地跑起来）

示例应用不需要模型 key、Google 账号、Docker，也不需要 Intelligence 订阅。想要真实能力时再加。

- `apps/mobile` —— 基于 CopilotKit 无头 hooks 的 iOS、Android、web 共用 UI。
- `apps/server` —— Hono API，带 CopilotKit runtime、任务引擎、审阅和持久化。
- `apps/worker` —— 带 token 保护、使用常驻 profile 的 Playwright 浏览服务。
- `apps/computer` —— 用于可选终端与工作区的非 root Linux 镜像。

环境：Node 24 · pnpm 11

```sh
git clone https://github.com/CopilotKit/OpenMuse.git openmuse
cd openmuse
pnpm install --frozen-lockfile
cp .env.example .env
pnpm dev          # API on :8787
pnpm dev:web      # app on :8081, in a second terminal
```

## FAQ / Questions, answered plainly（问题，直白作答）

**What is OpenMuse?（OpenMuse 是什么？）**
一个你自己运行的开源个人 agent。它有自己的浏览器、一个可选的 Linux 工作区和文件系统，并且在你关掉 App 之后仍会继续处理任务。它是一个模板：克隆它，在 MIT 许可下随便改。

**Is it ready for production?（可以用于生产了吗？）**
它是 alpha 版，面向自托管和在其上构建。开放式推理、真实 Google 账号、CopilotKit AG-UI Streams 各自都需要单独配置。仓库里明确记录了哪些已经验证、哪些在路线图上。

**Do I need a model key to try it?（试用需要模型 key 吗？）**
不需要。本地示例应用不接模型、不接 Google 账号、不用 Docker、也不需要 Intelligence 订阅。等你准备好了，把它指向 OpenAI、Anthropic 或 Google 的模型即可。provider key 只留在服务端。

**Can it send email or change my calendar on its own?（它能自己发邮件或改我的日历吗？）**
不能。每一次发送、每一次日历变更都要经过各自已保存的审阅流程。网站、邮件和文档内容对 agent 来说是证据，永远不是行动的许可。

**Where does my data live?（我的数据存在哪里？）**
默认在你自己的机器上。内嵌的 PGlite、文档和浏览器 profile 放在本地的 `.openmuse` 目录里，Google 凭据在静态存储时是加密的。需要时你可以切换到 PostgreSQL 并运行独立的任务 worker。

**How does it relate to OpenBot?（它和 OpenBot 是什么关系？）**
两者相互独立。OpenMuse 是给一个人用的个人 agent；OpenBot 是给整个公司用的平台。OpenMuse 附带一个默认禁用、经过契约测试的 OpenBot 适配器，把两者接起来是未来工作。

## 🪁 Make it your own personal agent（把它变成你自己的个人 agent）

克隆这个模板，从界面到背后的 agent harness 想改什么就改什么。如果你想把这样一款个人 agent 做进自己的产品，我们的工程师很乐意一起聊聊。

[View on GitHub] · [Talk to us]

## 页脚（导航链接，译出以存结构）

- **Product**：Overview、Frontend SDKs、Backend Connections、Channels、CopilotKit Intelligence、OpenBot、OpenMuse、Pricing、Generative UI（Gen UI / A2UI / MCP Apps / AG-UI Protocol）
- **Developers**：Docs、Examples、Dojo
- **News**：Blog
- **Company**：Contact Us、Careers、FAQ

© Tawkit, Inc. All rights reserved.｜Terms of service · Privacy Policy
