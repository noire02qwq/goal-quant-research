# 运行这个模板（Running the template）

> 来源：https://github.com/CopilotKit/OpenDots/blob/main/docs/SETUP.md
> 原文：oss-repos/OpenDots/docs/SETUP.md
> 翻译日期：2026-11-03 ｜ 范围：全文 ｜ 方式：机器翻译初稿，未经人工校对
> 引用于：docs/essay-study/opendots-2026.md、docs/brief-plan.md §3/§3.1

## 目录

- [本地开发](#local-development)
- [会话服务](#conversation-services)
  - [托管 Intelligence](#hosted-intelligence)
  - [本地 Intelligence 评估](#local-intelligence-evaluation)
  - [连接设置](#connection-settings)
- [页面与页面会话](#pages-and-page-conversations)
- [浏览器工具](#browser-tool)
- [Composio](#composio)
- [持久化的 Dot 电脑](#persistent-dot-computers)
- [Slack](#slack)
  - [创建托管 channel](#create-the-managed-channel)
  - [接入 specialist](#connect-a-specialist)
  - [验证你的部署](#verify-your-deployment)
- [通话](#calls)
- [容器](#containers)
- [Automatic Learning](#automatic-learning)
- [开发检查](#development-checks)

OpenDots 由一个 React 应用和一个 Node 服务器组成。服务器把页面、Space 与 Dot 配置以及 thread 绑定关系存在 SQLite 中，并连接到你所配置的会话、模型和消息服务。

<a id="local-development"></a>

## 本地开发

使用 Node.js 24 和 npm。

```sh
npm ci
cp .env.example .env
npm run dev
```

打开 http://127.0.0.1:5173。API 运行在 4310 端口。没有服务凭据时，应用会显示它的配置状态页，而不会生成模拟回复。

`npm run dev` 运行期间，http://localhost:5173 和 http://127.0.0.1:5173 都是允许的浏览器来源。UI 通过 Vite 的 `/api` 代理发送 API 请求。若要换用其他代理或自定义域名，把 `APP_ORIGIN` 设为一个精确的 origin，或用逗号分隔的列表，例如 `APP_ORIGIN=http://localhost:5173,http://127.0.0.1:5173`。显式设置的值会取代开发默认值。origin 必须在协议、主机名和端口上完全一致，不要带路径或末尾斜杠。列表项前后的空白会被裁掉，空项会被忽略。开发环境之外，`APP_ORIGIN` 不设置时，浏览器 origin 必须与请求 URL 的 origin 完全匹配。这个设置保留了对跨站请求的拦截，并不会开放浏览器对 API 的直接跨域访问。

构建本地应用：

```sh
npm run build
npm start
```

打开 http://127.0.0.1:4310。请让服务器保持运行，后台任务才能工作。

<a id="conversation-services"></a>

## 会话服务

OpenDots 的对话依赖 CopilotKit Intelligence。可以选择下文的本地评估、带许可的[自托管部署](https://docs.copilotkit.ai/intelligence/self-hosting)，或托管 Intelligence。页面与工作区元数据留在 SQLite 中，会话历史则单独存放，见 [Data and privacy](../README.md#data-and-privacy)。

<a id="hosted-intelligence"></a>

### 托管 Intelligence

要拿到托管项目 key，在执行 `cp .env.example .env` 之后，于 OpenDots 文件夹中运行：

```sh
npx copilotkit@latest login
npx copilotkit@latest project select
```

`login` 会打开浏览器供你登录或注册账户。`project select` 让你选择或创建项目，并把一个项目级 key 以 `CPK_INTELLIGENCE_API_KEY` 写入 `.env`。部署时（包括 Docker）请把生成的 `CPK_TELEMETRY_ID` 与项目 key 一起保留：它把 SDK 遥测关联到所选的 Intelligence 账户，见 [signup and usage tracking](TELEMETRY.md)。该命令还会删除 `INTELLIGENCE_API_KEY` 那一行，使文件里只保留一份凭据。下文的 Slack 和 Automatic Learning 也请使用同一个项目。

不要在这个文件夹里运行 `copilotkit onboard`。onboarding 是给还没接入 CopilotKit 的应用用的，OpenDots 已经有了自己的集成。

<a id="local-intelligence-evaluation"></a>

### 本地 Intelligence 评估

[本地评估预览](https://docs.copilotkit.ai/intelligence/self-hosting-local)在 macOS 上以 Docker Desktop 运行 Intelligence。请至少分配 4 个 CPU、12 GiB 内存和 40 GiB 可用存储。OpenDots 需要 Node.js 24。需要一个 CopilotKit 账户；免费的 Developer 计划即可获得可续期的 30 天评估许可。这不是一套生产环境安装。

在执行 `cp .env.example .env` 之后，确保 Docker Desktop 正在运行，然后在 OpenDots 文件夹中执行：

```sh
npx copilotkit@latest login
npx copilotkit@latest local setup
npx copilotkit@latest local connect
npx copilotkit@latest local connect --approve-connection
```

`local connect` 会先预览将要做的改动；带批准的那条命令把本地 API URL、网关 WebSocket URL 和项目 key 写入 `.env`，OpenDots 可以直接接受这些值。之后不要运行 `project select`——它选择的是托管项目。再给应用补上 `OPENAI_API_KEY` 和 `OPENAI_MODEL`，然后重启 `npm run dev`。Setup 的 Learning 模型与应用的模型是分开的。

发送一条消息，确认它出现在本地仪表盘（`npx copilotkit@latest local login`）中。用 `local status` 查看各服务健康状况。Threads、Automatic Learning 和 Channels 包含在内；User Memory 和 Product Analytics 不包含。Channels 需要一个 Slack 或 Teams 能访问到的公网 HTTPS 地址。

要恢复之前的连接，运行 `npx copilotkit@latest local cancel` 并重启应用；这套操作会保留整个技术栈及其数据。用 `local stop` 停止技术栈，用 `local renew` 续评估许可。既有的托管会话不会被复制到本地项目中。

这个预览版本要求 OpenDots 直接在你的 Mac 上用 `npm run dev` 运行，Intelligence 则跑在 Docker 里。CLI 给出的 `localhost` URL 在 OpenDots 容器内是打不通的。容器化运行的应用需要一个容器可达的 API 地址，以及一个服务器和浏览器都能访问的网关地址——因为 runtime 会把这个网关地址告知浏览器客户端。只把网关改成仅限 Docker 内部的主机名是不够的。

<a id="connection-settings"></a>

### 连接设置

在服务器上编辑 `.env`，改完后重启：

| 变量 | 用途 |
| --- | --- |
| `INTELLIGENCE_API_KEY` | 用于会话持久化的项目凭据 |
| `INTELLIGENCE_API_URL` | 覆盖你的 Intelligence 部署的 API 端点 |
| `INTELLIGENCE_GATEWAY_WS_URL`、`INTELLIGENCE_WS_URL` | 覆盖网关 WebSocket（优先用 CLI 的命名，旧命名仍受支持） |
| `OPENAI_API_KEY`、`OPENAI_MODEL` | 模型凭据与模型标识 |
| `OPENAI_BASE_URL` | 兼容协议的模型 API 端点 |
| `OWNER_ID` | 本次部署的会话所使用的稳定身份 |
| `DATABASE_PATH` | 存放页面、工作区与任务元数据的 SQLite 文件 |
| `OWNER_TOKEN` | 应用访问 token；外部绑定需要它 |
| `APP_ORIGIN` | 供代理或自定义域名使用的逗号分隔精确浏览器 origin |

`npx copilotkit project select` 会删除 `INTELLIGENCE_API_KEY` 那一行，并把同一份凭据写成 `CPK_INTELLIGENCE_API_KEY`。服务器两种名字都认；`CPK_INTELLIGENCE_API_KEY` 只要非空就优先于 `INTELLIGENCE_API_KEY`。

`INTELLIGENCE_GATEWAY_WS_URL` 只要非空就优先于 `INTELLIGENCE_WS_URL`。两者都不设置时，OpenDots 使用托管网关。接入自托管部署时，API 和网关端点要同时设置。

模型环境变量的命名跟随所配置的服务商适配器。服务商凭据应放在 `.env` 里，不要放在客户端变量或源码中。会话历史存放在所配置的 Intelligence 项目里，只备份 SQLite 文件并不等于备份了会话历史。

<a id="pages-and-page-conversations"></a>

## 页面与页面会话

选择一个 Space，即可打开它的页面资料库。你可以搜索文档、在网格视图和列表视图之间切换，或新建页面。可视化编辑器支持格式化、标题、列表、清单、表格和 slash commands。按 `/` 插入块，按 Cmd/Ctrl+S 立即保存。编辑停顿后页面会自动保存，保存状态会告诉你改动是否已经到达服务器。

页面操作包括：创建子页面、在 Space 内移动页面、删除页面（其子页面会上移一级到被删页面的父页面），以及编辑 Markdown 源码。已有的文档若含有可视化编辑器不支持的语法，会停留在源码模式以保全内容。没有会话凭据时，手动编辑照常可用。

打开某个页面的聊天，选择一位有该 Space 访问权限的 specialist。访问权限在侧边栏该 Dot 的设置中授予。服务器会为该页面与该 specialist 创建或复用一个 CopilotKit Thread。Dot 会把当前已保存的页面作为上下文，并能在其获授权的 Space 中读取、创建和编辑页面。页面会话默认使用该页面所属的 Space；其他聊天则使用该 Dot 的默认页面保存位置。让它修改文档之前，先保存你的手动编辑。修订检查会拒绝过期的写入；发生冲突时，你本地的草稿仍可用于恢复。保存失败后会停止自动重试，直到你手动重试或解决冲突为止——这样断开的会话就不会悄悄覆盖更新的内容。

用会话中的"保存到页面"操作，可以把已保存的文本历史变成一份文档，这需要会话服务正常可用。页面会保留指向来源会话的链接，聊天中的页面链接会打开文档工作区。

两层存储都要备份：SQLite 存着页面内容与 thread 绑定关系，Intelligence 项目存着会话历史。模板不包含多用户页面共享、实时协同、文件上传或任意交互式嵌入。

<a id="browser-tool"></a>

## 浏览器工具

默认选中 Parallel（`WEB_SEARCH_PROVIDER=parallel`）。真实研究需要模型配置，但不需要浏览器 worker。在服务器上设置可选的 `PARALLEL_API_KEY` 可以启用带认证的用法并获得更高配额；匿名 MCP 端点对轻量使用是免费的。查询、选中的 URL、研究目标和一个稳定的会话标识会发送给 Parallel。数据共享、权限和限制见 [public-web research](../README.md#public-web-research)。

设置 `WEB_SEARCH_PROVIDER=disabled` 可关闭这些研究工具；设 `WEB_SEARCH_PROVIDER=browser` 则使用既有的仅限 URL 的读取器。浏览器服务读取给定的公开 URL，返回页面文本和一份抓取结果。先配置 `BROWSER_URL` 和 `BROWSER_SECRET`，然后运行：

```sh
npx playwright install chromium
npm run browser
```

应用进程和浏览器进程要用同一个 secret。浏览器导航是只读的，并禁用了 JavaScript。不支持内网地址、重定向和需要认证的页面，请提供规范的公开 URL。这是一个受限的研究工具，不是通用的桌面或 shell。

<a id="composio"></a>

## Composio

设置 `COMPOSIO_API_KEY`，Dot 就能使用 owner 的已连接应用。重启 OpenDots，在全局设置和某个 Dot 的设置里都启用 Connected apps，然后可选择把该 Dot 限制在逗号分隔的 toolkit slug 上，例如 `gmail`、`google_calendar`。toolkit 列表留空，Dot 就可以检索 Composio 项目可用的全部 toolkit。

只添加 API key 时，已连接的应用仍处于关闭状态。Composio 工具能够读取和修改真实账号里的数据，而空的 toolkit 列表意味着 Composio 项目下所有 toolkit 都被放行。全局和按 Dot 的开关都需要 owner 显式授予这项访问权限。

OpenDots 用稳定的 `OWNER_ID` 作为 Composio 的用户身份，绑定账号之后不要再改它。当某个工具需要认证时，打开聊天中显示的 HTTPS Connect 链接，完成服务商的登录流程。关闭任一权限都会阻止新的应用调用，并停止正在进行的工作。没有 `COMPOSIO_API_KEY` 时，不会创建任何 Composio 客户端和工具，相关控件也不会显示。

测试这个集成时：先配置一个可用的模型，把某个 Dot 限制在一个 toolkit 上，然后从只读请求开始，例如列出最近的消息或日历事件。提示时完成 Connect 流程，再重复同一条请求。只有当误操作也无妨的账号，才适合用来测试写操作。

工具参数和结果会经过 Composio 与所连接的应用服务商。凭据请留在服务器环境中，并查阅 [Composio 的文档](https://docs.composio.dev)以及各家服务商的隐私与数据保留条款。

<a id="persistent-dot-computers"></a>

## 持久化的 Dot 电脑

若想让每位 specialist 拥有独立的浏览器、持久的文件和可选的 shell，请按 [Computer setup](COMPUTERS.md) 操作。它使用固定版本的 OpenBot computer/supervisor 服务和按 Dot 的权限。配置了 computer tools 之后，Parallel 研究工具仍然可用；选中浏览器服务商时，Dot 会用它们的 computer tools 代替那只读的公共页面工具——使用前请先为每个 Dot 启用所需能力。

<a id="slack"></a>

## Slack

OpenDots 通过托管的 Slack 连接使用 `@copilotkit/channels`，沿用了 [OpenTag](https://github.com/CopilotKit/OpenTag) 的 runtime 与 channel 模式。应用负责声明 channel 及其 specialist agent；Intelligence 负责管理 Slack adapter 与消息投递。你不需要在 OpenDots 中另外搭建 Slack webhook 服务器或 Socket Mode 连接。

下文的 CLI 项目选择命令面向托管 Intelligence。本地评估请在本地仪表盘中配置 Channels，并遵循[本地 Channels 要求](https://docs.copilotkit.ai/intelligence/self-hosting-local#connect-slack-or-microsoft-teams)，其中包含一个公网 HTTPS 地址。不要用 `project select` 覆盖本地项目 key。

<a id="create-the-managed-channel"></a>

### 创建托管 channel

选择本应用所使用的同一个 Intelligence 项目，然后创建一个名称唯一的 channel：

```sh
npx --yes copilotkit@latest project select
npx --yes copilotkit@latest channels add --name opendots --display-name "OpenDots" --adapter slack --json
```

按 CLI 返回的 `nextAction` 操作：用它生成的 manifest 创建 Slack 应用，在托管配置流程中提供凭据，再运行它给出的 `resumeCommand`。返回 `blocked` 表示还有 Slack 控制台的步骤要做；返回 `failed` 则必须先解决才能继续。保持 Socket Mode 关闭。用它请求的 scopes 在你的 workspace 中安装或重新安装生成的应用。不同部署请使用不同的 channel 名，以免互相争抢消息投递。

Slack 控制台的操作步骤见 [OpenTag 的配置指南](https://github.com/CopilotKit/OpenTag/blob/main/setup.md)。Slack bot token 和签名密钥属于托管 adapter 配置，不应放进浏览器或本应用的 `.env`。

<a id="connect-a-specialist"></a>

### 接入 specialist

在应用服务器的 `.env` 中，与 Intelligence 和模型凭据一起配置：

```dotenv
SLACK_CHANNEL_NAME=opendots
SLACK_TEAM_ID=T_REPLACE_WITH_WORKSPACE_ID
SLACK_USER_IDS=U_REPLACE_WITH_YOUR_USER_ID
SLACK_DOT_ID=REPLACE_WITH_DOT_ID
```

`SLACK_CHANNEL_NAME` 必须与托管 channel 的名字完全一致，而不是 `#general` 这类 Slack 会话名。OpenTag 把这个设置叫作 `INTELLIGENCE_CHANNEL_NAME`，OpenDots 用的是 `SLACK_CHANNEL_NAME`。`SLACK_TEAM_ID` 与逗号分隔的 `SLACK_USER_IDS` 用来限定谁可以调用这位 specialist。`SLACK_DOT_ID` 选择一个已有的 Dot，其 ID 可在已认证的 `/api/workspace` 响应中找到；不填则默认为初始 Dot。

修改环境设置后重启 OpenDots，并在 Settings & setup 中查看 Slack 状态。发消息测试之前，channel 必须先完成激活。在 bot 可访问的频道里 @ 它；此后该 thread 中的后续消息都会发给同一位 specialist。无关的 thread、bot 事件、编辑、删除，以及白名单之外的用户都不会触发 agent 运行。不支持通过编辑消息来补一个 @，请改发新消息。

这个模板把获准的 Slack 用户映射到唯一的 OpenDots owner。回复对该 Slack 会话的所有可见，因此请据此斟酌这位 specialist 的 Space 访问权限和可用工具。这不是一个多用户身份模型。

<a id="verify-your-deployment"></a>

### 验证你的部署

用一个获准的用户 @ bot，确认它在同一个 Slack thread 中作出回应。在该 thread 中回复，确认上下文得以延续。再确认无关的 thread 和未获准的用户都无法调用它。在 OpenDots 中暂停助手，确认获准的请求会收到一条暂停提示。检查 Settings & setup 中有没有 channel 连接失败。

本地测试用 fixture 验证 channel 行为。在你配好托管连接和模型凭据之前，真实的 Slack @ 与回复仍未验证。扩展 adapter 和 channel 行为的方式见 [Channels SDK documentation](https://github.com/CopilotKit/channels-sdk)。

<a id="calls"></a>

## 通话

内置的语音 adapter 使用 `api.openai.com` 上的 Realtime API。把 `VOICE_API_KEY` 设为有该 API 访问权限的 key，把 `VOICE_MODEL` 设为受支持的 Realtime 模型（本地 UI 测试用的是 `gpt-realtime-2.1`），`VOICE_NAME` 用于选择音色。`OPENAI_BASE_URL` 只改变计算模型的端点，不影响语音。通话使用浏览器麦克风权限和 WebRTC；托管部署需要 HTTPS。服务器负责中介服务商侧的配置，并把计算任务委托给所选 Dot 的会话。

配好了 key 并不等于通话能成功。依赖语音工作流之前，请在你自己的部署上验证麦克风访问、音频播放、compute delegation、打断、挂断以及已保存的回执。

<a id="containers"></a>

## 容器

在 `.env` 中把 `OWNER_TOKEN` 和 `BROWSER_SECRET` 设为两个不同的随机密钥（各至少 24 个字符），然后运行：

```sh
docker compose up --build -d
```

打开 http://localhost:4310，应用端口绑定在 loopback 上。浏览器服务是可选的：设置一个 24 个字符以上的 `BROWSER_SECRET`，再运行 `docker compose --profile browser up --build` 即可启用，它没有对外发布的端口。应用元数据存放在 `opendots-data` 卷中。

```sh
# Stop services while retaining saved data.
docker compose down
```

远程托管时，请配置 HTTPS 反向代理和匹配的 `APP_ORIGIN`。模板的部署边界见 [Security](../SECURITY.md)。

<a id="automatic-learning"></a>

## Automatic Learning

OpenDots 把 [CopilotKit Automatic Learning](https://docs.copilotkit.ai/learning) 接到各个 Dot 上。它使用服务端的 Intelligence 凭据（`CPK_INTELLIGENCE_API_KEY` 或 `INTELLIGENCE_API_KEY`）以及可选的 `INTELLIGENCE_API_URL`，不需要额外的模型 key 或前端 key。

1. 在同一个 Intelligence 项目中打开 **Learning**，为一个聚焦的工作流创建容器，例如 `research-workflow`。ID 由 1–64 个小写字母、数字和单个连字符组成。
2. 在 OpenDots 中编辑该 Dot，在 **Automatic Learning** 一栏填入这个 ID。保存 ID 只是配置了路由，并不会创建或校验远程容器。
3. 开启新会话并完成相关工作流。每条会话沿用它创建时所分配的容器。既有会话（包括这次集成之前创建的）不会被追溯纳入。修改或清空 Dot 的 ID 只影响新会话——涵盖这些会话中的页面聊天、定时与语音计算，以及新的 Slack thread。
4. 在 Intelligence 中检查证据，手动运行 Learning 或使用它的调度，并审阅、发布它提议的技能。默认的自动阈值是 15 个符合条件的 thread，请以你部署中显示的就绪计数为准。
5. 在 Intelligence 容器上启用 **Skill delivery**，然后在 Dot 的设置中启用 **Use published skills**，并在已纳入的会话中开启新一轮。BuiltInAgent 会加载最新验证过的已发布目录；它的 TanStack AI factory 运行模型，并暴露 `copilotkit_load_skill` 和 `copilotkit_read_skill_file`，由模型决定加载哪些相关技能。请检查该轮的工具调用来确认是否真的用上了——只保存设置并不能证明连通。

技能投递始终使用该会话最初分配的容器，即使 Dot 之后被指向另一个容器也一样。Dot 上的投递勾选项对它的所有会话生效；取消勾选会在后续轮次停止投递；修改 Learning 设置同样会停止进行中的工作。没有容器的会话不会请求技能。既有的研究、记忆、页面和电脑权限照常适用。

摄取与投递是两回事：清空容器不会让较早的会话退订，要停止分析得在 Intelligence 中暂停 Learning；关闭投递并不会停止证据收集。投递被拒绝或初始技能快照不可用时，该轮会直接失败，而不是在缺少已配置技能的情况下默默继续。要继续运行，要么恢复投递，要么取消勾选 **Use published skills**。技能需要在 Intelligence 中经审阅并发布，OpenDots 不会自动批准它们。

这套集成使用显式的容器列表，因此环境里若存在 `CPK_INTELLIGENCE_LEARNING_CONTAINER_ID` 和 `CPK_INTELLIGENCE_SKILLS_REVISION` 变量，也不会覆盖某条会话的配置。自托管的 Intelligence 必须支持[技能投递端点](https://docs.copilotkit.ai/intelligence/learned-skills)。

<a id="development-checks"></a>

## 开发检查

```sh
npm run check-format
npm run lint
npm run typecheck
npm test
npm run build
```

自动化测试使用服务 fixture。真实的模型、Intelligence、Slack 和语音验证，需要你自己配置相应的服务。

