# OpenDots（CopilotKit/OpenDots）源码走读笔记（2026）

> 状态：定稿（本轮源码走读产出；机制映射候选只写在本笔记末尾，**未回填 brief-plan §3 主表**——子代理仅写笔记文件）
> 走读日期：2026-11-03
> 仓库：[CopilotKit/OpenDots](https://github.com/CopilotKit/OpenDots)，本地克隆 `~/agent-studio/goal-quant-research/oss-repos/OpenDots`，分支 `main`，走读时 HEAD = `8091324942b86789ed0da7facbee855145d933b0`（2026-10-22，Merge PR #148）
> 对应设计文档条目：`docs/brief-plan.md` §3.1 OpenDots 行（该行原为二手来源、状态"待读"）

## 0. 精读范围（读了什么 / 没读什么）

**全仓规模**：`src/` 86 个文件（server 31 + client 40 + shared 8 + browser 3 + build 1 等），`docs/` 6 篇，`tests/` 58 个测试文件。仓库规模中等，但**不是全仓精读**，以下为实读清单。

**已实读（逐行）**：

- 根目录：[README.md](https://github.com/CopilotKit/OpenDots/blob/main/README.md)、[LICENSE](https://github.com/CopilotKit/OpenDots/blob/main/LICENSE)、[package.json](https://github.com/CopilotKit/OpenDots/blob/main/package.json)、[.env.example](https://github.com/CopilotKit/OpenDots/blob/main/.env.example)、[compose.yml](https://github.com/CopilotKit/OpenDots/blob/main/compose.yml)
- 文档：[docs/SETUP.md](https://github.com/CopilotKit/OpenDots/blob/main/docs/SETUP.md)、[docs/COMPUTERS.md](https://github.com/CopilotKit/OpenDots/blob/main/docs/COMPUTERS.md)、[docs/CONNECTIONS.md](https://github.com/CopilotKit/OpenDots/blob/main/docs/CONNECTIONS.md)
- 服务端核心：[src/server/index.ts](https://github.com/CopilotKit/OpenDots/blob/main/src/server/index.ts)、[app.ts](https://github.com/CopilotKit/OpenDots/blob/main/src/server/app.ts)、[runner.ts](https://github.com/CopilotKit/OpenDots/blob/main/src/server/runner.ts)、[store.ts](https://github.com/CopilotKit/OpenDots/blob/main/src/server/store.ts)、[shutdown.ts](https://github.com/CopilotKit/OpenDots/blob/main/src/server/shutdown.ts)、[dot-agent.ts](https://github.com/CopilotKit/OpenDots/blob/main/src/server/dot-agent.ts)、[platform.ts](https://github.com/CopilotKit/OpenDots/blob/main/src/server/platform.ts)、[slack-channel.ts](https://github.com/CopilotKit/OpenDots/blob/main/src/server/slack-channel.ts)、[runtime-scope.ts](https://github.com/CopilotKit/OpenDots/blob/main/src/server/runtime-scope.ts)、[headless.ts](https://github.com/CopilotKit/OpenDots/blob/main/src/server/headless.ts)、[workspace.ts](https://github.com/CopilotKit/OpenDots/blob/main/src/server/workspace.ts)、[workspace-routes.ts](https://github.com/CopilotKit/OpenDots/blob/main/src/server/workspace-routes.ts)、[connection-tools.ts](https://github.com/CopilotKit/OpenDots/blob/main/src/server/connection-tools.ts)、[connection-store.ts](https://github.com/CopilotKit/OpenDots/blob/main/src/server/connection-store.ts)、[connection-routes.ts](https://github.com/CopilotKit/OpenDots/blob/main/src/server/connection-routes.ts)、[connections.ts](https://github.com/CopilotKit/OpenDots/blob/main/src/server/connections.ts)（前 60 行）、[page-tools.ts](https://github.com/CopilotKit/OpenDots/blob/main/src/server/page-tools.ts)、[computer-service.ts](https://github.com/CopilotKit/OpenDots/blob/main/src/server/computer-service.ts)、[computer-tools.ts](https://github.com/CopilotKit/OpenDots/blob/main/src/server/computer-tools.ts)、[computer-store.ts](https://github.com/CopilotKit/OpenDots/blob/main/src/server/computer-store.ts)、[tanstack-tools.ts](https://github.com/CopilotKit/OpenDots/blob/main/src/server/tanstack-tools.ts)
- 共享类型：[src/shared/types.ts](https://github.com/CopilotKit/OpenDots/blob/main/src/shared/types.ts)、[connection-types.ts](https://github.com/CopilotKit/OpenDots/blob/main/src/shared/connection-types.ts)、[page-review.ts](https://github.com/CopilotKit/OpenDots/blob/main/src/shared/page-review.ts)
- 客户端：[src/client/TaskActions.tsx](https://github.com/CopilotKit/OpenDots/blob/main/src/client/TaskActions.tsx)（全文）+ `grep` 定位若干组件（ComputerToolCard / ConnectionActionCard / WorkspaceDialog 等只取命中行）
- 测试：只读 `tests/` **文件名清单与用例名**（`runner/store/slack-channel/runtime-scope` 等的 `it(...)` 标题），**未读测试实现、未运行 `npm test`**

**未读（明确声明）**：`src/client/` 绝大部分组件与 `src/browser/`、`src/build/`；`src/server/` 中的 `voice.ts`、`parallel.ts`、`research.ts`、`pages.ts`、`page-service.ts`、`page-routes.ts`、`learning.ts`、`composio.ts`、`composio-tools.ts`、`platform-config.ts`、`setup-telemetry.ts`、`app-origin.ts`、`computer-routes.ts`；`docs/TELEMETRY.md`、`docs/SETUP-TELEMETRY.md`、`docs/demos/`、`deployment/`；全部测试正文。因此涉及**语音通话内部实现、Parallel 联网检索内部实现、Automatic Learning 路由细节**的结论只引 README/SETUP.md 的文字声明，不当作源码级结论。

**协议（LICENSE 实读确认）**：**MIT License**，`Copyright (c) Atai Barkai`（[LICENSE](https://github.com/CopilotKit/OpenDots/blob/main/LICENSE) 全文读过）。`package.json` 的 `"license": "MIT"`、`"private": true`、`"engines": {"node": ">=24.0.0"}` 与之一致。

**走读方式**：纯静态阅读（本地克隆 + 逐文件读取），**未编译、未启动服务、未跑测试**；README 中"某功能已于 2026-09-29/09-30 实测"属上游自述，本笔记未复核。

---

## 1. 与 brief-plan §3.1 二手定位的差异（留痕式记录）

§3.1 的二手描述是"always-on AI coworker 起点模板；常驻 agent 各配一台机器，可在 Slack 等处接活、会话内持续交接任务"。读源码后的核对：

| 二手表述 | 源码/文档实际 | 证据 |
|---|---|---|
| "各配一台**机器**" | 每 Dot 可配一台**容器**（OpenBot computer + supervisor），**可选且默认未配置**；未配置时 `ComputerService.configured=false`，computer 工具完全不装配、不执行 | [computer-service.ts:34-40](https://github.com/CopilotKit/OpenDots/blob/main/src/server/computer-service.ts#L34-L40)、[README:67](https://github.com/CopilotKit/OpenDots/blob/main/README.md#L67)、[docs/COMPUTERS.md](https://github.com/CopilotKit/OpenDots/blob/main/docs/COMPUTERS.md) |
| "**会话内持续交接任务**" | **没有 agent→agent 交接/委派**。只有三类"交接"：人→Dot（聊天/Slack/@提及）、Dot→人（审批卡片）、语音通话把 compute 委派回**同一会话**。README 明确 "multi-Dot group conversations and automatic delegation are further work" | [README:224](https://github.com/CopilotKit/OpenDots/blob/main/README.md#L224)、[src/server/voice.ts](https://github.com/CopilotKit/OpenDots/blob/main/src/server/voice.ts)（未精读，仅按 README/SETUP.md 引用） |
| "clone → **定义 Dot**" | 定义 Dot = 走 UI/API 填表写入 SQLite（zod 校验），**不是 clone 后改配置文件**；仓库内没有 Dot 的 schema 文件或样例定义 | [workspace-routes.ts:11-27](https://github.com/CopilotKit/OpenDots/blob/main/src/server/workspace-routes.ts#L11-L27)、[workspace.ts:23](https://github.com/CopilotKit/OpenDots/blob/main/src/server/workspace.ts#L23) |
| "always-on" 隐含长程目标 | **无 goal 概念、无事件触发**："Schedules are recurring instructions, not a complete goal or event-trigger system"，并把 "Add event triggers and a persistent responsibility lifecycle" 列为待做 | [README:224](https://github.com/CopilotKit/OpenDots/blob/main/README.md#L224)、[README:230](https://github.com/CopilotKit/OpenDots/blob/main/README.md#L230) |

结论：二手定位在"模板起点、Slack 接活、每 Dot 独立执行环境"三点上成立；"机器"实为**可选容器**，"持续交接任务"实为**会话内人机交接**，**群组分工并不存在**。§3.1 该行若回填，建议把"关联点"从"任务交接"改为"单 owner 多 Dot 的接活与审批边界"。

---

## 2. always-on 生命周期（关注点①）

### 2.1 进程形态：单 Node 进程 + 显式优雅退出

- 入口 [src/server/index.ts](https://github.com/CopilotKit/OpenDots/blob/main/src/server/index.ts)：Hono + `@hono/node-server` 单进程同时承载 API、静态前端、CopilotKit runtime（`/api/copilotkit`）、Channels（Slack）。监听成功回调里才 `runner.start()` 与 `platform.start()`（[index.ts:115-126](https://github.com/CopilotKit/OpenDots/blob/main/src/server/index.ts#L115-L126)）。
- 外部绑定强制鉴权：host 非 loopback 时必须提供 ≥24 字符 `OWNER_TOKEN`，否则直接抛错退出（[index.ts:20-27](https://github.com/CopilotKit/OpenDots/blob/main/src/server/index.ts#L20-L27)）。
- 优雅退出 [shutdown.ts](https://github.com/CopilotKit/OpenDots/blob/main/src/server/shutdown.ts)：SIGTERM/SIGINT → 先 `stopRunner()`（把**本进程正持有 lease 的 running 任务标为 interrupted**，原因写"Server stopped during this run. Review completed effects before retrying."，[runner.ts:26-37](https://github.com/CopilotKit/OpenDots/blob/main/src/server/runner.ts#L26-L37)），再以 8 秒 deadline 竞速停 Channels + 关 HTTP（[shutdown.ts:22-44](https://github.com/CopilotKit/OpenDots/blob/main/src/server/shutdown.ts#L22-L44)）。
- 部署层守护：`compose.yml` 中 `app`、`browser` 服务 `restart: unless-stopped`（[compose.yml:43](https://github.com/CopilotKit/OpenDots/blob/main/compose.yml#L43)、[compose.yml:59](https://github.com/CopilotKit/OpenDots/blob/main/compose.yml#L59)）；文档要求"Keep the server running for background work"（[docs/SETUP.md:26](https://github.com/CopilotKit/OpenDots/blob/main/docs/SETUP.md#L26)）。**模板本身不含 systemd/launchd/watchdog 配置**，常驻靠容器 restart 策略或用户自管。

### 2.2 后台"常驻工作"= 1 秒 tick 的单并发 Runner

- [runner.ts:20-25](https://github.com/CopilotKit/OpenDots/blob/main/src/server/runner.ts#L20-L25)：`setInterval(tick, 1000)` + 启动即跑一次。
- [runner.ts:56-63](https://github.com/CopilotKit/OpenDots/blob/main/src/server/runner.ts#L56-L63)：`if (this.active.size) return;` —— **同一时刻最多一个 Run**（单 worker 串行），claim 一次一个任务。
- 任务类型是 `Task`（prompt + intervalSeconds + nextRunAt + lease/leaseUntil，[types.ts:16-27](https://github.com/CopilotKit/OpenDots/blob/main/src/shared/types.ts#L16-L27)），Run 是每次执行的记录（[types.ts:39-47](https://github.com/CopilotKit/OpenDots/blob/main/src/shared/types.ts#L39-L47)），状态机 `queued/running/paused/completed/failed/interrupted/cancelled`（[types.ts:1-8](https://github.com/CopilotKit/OpenDots/blob/main/src/shared/types.ts#L1-L8)）。
- **定时任务回到原会话执行**：`POST /api/tasks` 必须带 `threadId` 且线程属于本 workspace，写 `task_threads` 绑定（[app.ts:129-155](https://github.com/CopilotKit/OpenDots/blob/main/src/server/app.ts#L129-L155)、[workspace.ts:300-311](https://github.com/CopilotKit/OpenDots/blob/main/src/server/workspace.ts#L300-L311)）；执行时 `platform.turn(threadId, prompt, …)` → `runThreadTurn` 走 Intelligence Agent 在**原对话**里追加一条带 `opendotsSource: 'scheduled_task'` 前缀的消息（[index.ts:75-91](https://github.com/CopilotKit/OpenDots/blob/main/src/server/index.ts#L75-L91)、[headless.ts:24-84](https://github.com/CopilotKit/OpenDots/blob/main/src/server/headless.ts#L24-L84)）。没有绑定线程的 legacy 任务直接报错不执行（[index.ts:80-84](https://github.com/CopilotKit/OpenDots/blob/main/src/server/index.ts#L80-L84)）。

### 2.3 重启后的状态恢复（三类数据三条路径）

| 数据 | 存放 | 重启后 |
|---|---|---|
| 任务/Run/事件/记忆/设置 | 本地 SQLite `data/opendots.sqlite`（WAL，[store.ts:30-39](https://github.com/CopilotKit/OpenDots/blob/main/src/server/store.ts#L30-L39)） | 直接可读；`claim()` 恢复调度 |
| 页面、Space、Dot、线程绑定、审批、计算机审计 | 同一 SQLite 的另一套表（[workspace.ts:21-27](https://github.com/CopilotKit/OpenDots/blob/main/src/server/workspace.ts#L21-L27)、[connection-store.ts:14-16](https://github.com/CopilotKit/OpenDots/blob/main/src/server/connection-store.ts#L14-L16)、[computer-store.ts:9-10](https://github.com/CopilotKit/OpenDots/blob/main/src/server/computer-store.ts#L9-L10)） | 直接可读 |
| **会话消息/工具调用/Run 事件流** | **不在本机**：CopilotKit Intelligence（hosted 云 或 local Docker 评估栈）；"OpenDots has no standalone SQLite conversation store" | 依赖 Intelligence 可用；只拷 SQLite 不算备份会话（[README:194](https://github.com/CopilotKit/OpenDots/blob/main/README.md#L194)、[docs/SETUP.md:30](https://github.com/CopilotKit/OpenDots/blob/main/docs/SETUP.md#L30)） |
| 每 Dot 容器内的浏览器 profile / 文件 | Docker 命名卷（OpenBot） | stop/start 保留（[docs/COMPUTERS.md](https://github.com/CopilotKit/OpenDots/blob/main/docs/COMPUTERS.md)） |

**崩溃/掉电恢复语义（关键）**：`Store.claim()` 在挑选任务前，先把 `status='running' AND leaseUntil<=now` 的任务批量 `invalidate` 为 **`interrupted`**，错误文案 = "Worker lease expired. Review completed effects before retrying."（[store.ts:216-225](https://github.com/CopilotKit/OpenDots/blob/main/src/server/store.ts#L216-L225)）。也就是说**重启后不会自动续跑被打断的 Run**，必须人工点重试；租约时长 = `max(180s, runTimeout*2)`（[runner.ts:59-62](https://github.com/CopilotKit/OpenDots/blob/main/src/server/runner.ts#L59-L62)、[store.ts:17](https://github.com/CopilotKit/OpenDots/blob/main/src/server/store.ts#L17)），给"超时后仍能落库"留窗口。

### 2.4 always-on 的边界（上游自述）

- 无事件触发、无目标/责任生命周期（[README:224](https://github.com/CopilotKit/OpenDots/blob/main/README.md#L224)、[README:230](https://github.com/CopilotKit/OpenDots/blob/main/README.md#L230)）。
- 单 owner：没有多用户、共享编辑、邀请（同上 224 行）。
- 对话能力依赖外部 Intelligence（缺失时进入 setup 状态，不伪造回复，[docs/SETUP.md:15](https://github.com/CopilotKit/OpenDots/blob/main/docs/SETUP.md#L15)）。

---

## 3. Dot 定义与能力声明是否 schema 化（关注点②）

**结论：半 schema 化——"配置结构"schema 化得很干净（zod + SQLite 行），"能力声明"不是自描述，而是服务端按权限开关在运行时装配。**

### 3.1 配置结构：zod strict schema + 关系表

- 路由级 schema [workspace-routes.ts:11-27](https://github.com/CopilotKit/OpenDots/blob/main/src/server/workspace-routes.ts#L11-L27)：`.strict()`，字段 = `name(≤40)`、`instructions(3–2000)`、`researchAllowed`、`memoryAllowed`、`appsAllowed`、`composioToolkits[]`（`^[a-z0-9_]+$`，≤100）、`learningContainerId`、`skillDeliveryEnabled`、`spaceIds[]`（1–100）、`spaceId`。错误信息固定为 "Provide a name, role instructions, and explicit tool permissions."（[workspace-routes.ts:76-85](https://github.com/CopilotKit/OpenDots/blob/main/src/server/workspace-routes.ts#L76-L85)）。
- 存储模型 [workspace.ts:23](https://github.com/CopilotKit/OpenDots/blob/main/src/server/workspace.ts#L23)：`dots` 主表 + `dot_spaces(dotId, spaceId)` 授权表；`spaceId` 是"保存页面的默认去向，不是所有权"（类型注释 [types.ts:81-82](https://github.com/CopilotKit/OpenDots/blob/main/src/shared/types.ts#L81-L82)）。迁移只做一次且注明"restarting must never restore a revoked grant"（[workspace.ts:45-57](https://github.com/CopilotKit/OpenDots/blob/main/src/server/workspace.ts#L45-L57)）。
- 首次启动自动播种默认 Space "Everyday" + 默认 Dot "Dot"（[workspace.ts:70-82](https://github.com/CopilotKit/OpenDots/blob/main/src/server/workspace.ts#L70-L82)）。
- 环境变量侧（`.env.example`）也是强结构：Intelligence/模型/浏览器/Composio/语音/Slack 四件套/计算机三件套/Web 搜索提供方，全部集中读入 `PlatformConfig`（[index.ts:34-63](https://github.com/CopilotKit/OpenDots/blob/main/src/server/index.ts#L34-L63)）。

### 3.2 能力声明：按权限**运行时装配**，无 capability 自描述

`DotAgent.run()` 每一轮现算工具集（[dot-agent.ts](https://github.com/CopilotKit/OpenDots/blob/main/src/server/dot-agent.ts)）：

- 研究工具：`dot.researchAllowed && 全局 researchAllowed && webSearchProvider==='browser' && !computer.configured` → 装 `read_public_page`；provider 为 `parallel` → 装 `search_web` + `read_public_page`（[dot-agent.ts:174-300](https://github.com/CopilotKit/OpenDots/blob/main/src/server/dot-agent.ts#L174-L300)）。
- 连接应用（Composio）：`composioApiKey && 全局 appsAllowed && dot.appsAllowed` 才建（[dot-agent.ts:338-354](https://github.com/CopilotKit/OpenDots/blob/main/src/server/dot-agent.ts#L338-L354)）。
- 页面工具恒在（受 Space 授权约束）、计算机工具仅 `computer.configured` 时装配（[dot-agent.ts:356-363](https://github.com/CopilotKit/OpenDots/blob/main/src/server/dot-agent.ts#L356-L363)）。
- MCP 连接工具按 Dot 过滤，逐工具 `enabled / requiresApproval` 开关（[connection-tools.ts:15-51](https://github.com/CopilotKit/OpenDots/blob/main/src/server/connection-tools.ts#L15-L51)、[connection-types.ts:13-16](https://github.com/CopilotKit/OpenDots/blob/main/src/shared/connection-types.ts#L13-L16)）。
- 角色提示 = 字符串拼接：`You are ${dot.name}, a specialist Dot … Role instructions: ${dot.instructions}` + 一大段安全约束（不可信数据、不得虚构工具结果、审批等待、owner-only 控制等），[dot-agent.ts:364](https://github.com/CopilotKit/OpenDots/blob/main/src/server/dot-agent.ts#L364)。
- 循环上限 `maxIterations(5 或 10)`、单轮 token 上限 `max_completion_tokens: 2200`（[dot-agent.ts:396-405](https://github.com/CopilotKit/OpenDots/blob/main/src/server/dot-agent.ts#L396-L405)）。

### 3.3 权限是**三层 AND**，且会话中热撤销

三层 = 全局 `Settings`（`paused/researchAllowed/memoryAllowed/appsAllowed`，[types.ts:9-15](https://github.com/CopilotKit/OpenDots/blob/main/src/shared/types.ts#L9-L15)，默认 `appsAllowed:false` [store.ts:18-24](https://github.com/CopilotKit/OpenDots/blob/main/src/server/store.ts#L18-L24)）× Dot 级开关 × 工具级开关（MCP `enabled/requiresApproval`、计算机 `{enabled,browser,files,shell}` 且**默认全关** [computer-store.ts:12-19](https://github.com/CopilotKit/OpenDots/blob/main/src/server/computer-store.ts#L12-L19)）。

**热撤销**是这套设计最值得抄的细节：

- 每轮 run 起一个 100ms 的 `check()` watcher，比对 settings、Dot 各权限字段、`spaceIds`、以及连接 `fingerprint(dotId)`（id+updatedAt 拼接，[connection-store.ts:93-101](https://github.com/CopilotKit/OpenDots/blob/main/src/server/connection-store.ts#L93-L101)），**任一变化立即 `abortRun()`**（[dot-agent.ts:133-168](https://github.com/CopilotKit/OpenDots/blob/main/src/server/dot-agent.ts#L133-L168)）。
- 计算机动作执行中每 50ms 重查 `allowed()`，被撤销就 abort（[computer-service.ts:348-354](https://github.com/CopilotKit/OpenDots/blob/main/src/server/computer-service.ts#L348-L354)）。
- 全局 pause/关权限会 `runner.abortAll()` 并把 running 任务 `invalidate` 为 interrupted（[app.ts:199-207](https://github.com/CopilotKit/OpenDots/blob/main/src/server/app.ts#L199-L207)、[store.ts:86-101](https://github.com/CopilotKit/OpenDots/blob/main/src/server/store.ts#L86-L101)）。
- 会话级学习容器在**建会话时冻结**（`Conversation.learningContainerId` "Frozen at creation"，[types.ts:102-103](https://github.com/CopilotKit/OpenDots/blob/main/src/shared/types.ts#L102-L103)、[workspace.ts:269-293](https://github.com/CopilotKit/OpenDots/blob/main/src/server/workspace.ts#L269-L293)）。

**缺什么**：没有"Dot 能力清单"式的自描述 schema（模型只能看到装配后的 tools 描述）；没有 per-Dot 模型/预算/超时配置（超时是全局 `agentRunTimeoutMs`）；没有工具白名单字段——要禁用某个能力只能关掉所属大类开关。

---

## 4. 任务交接与权限边界（关注点③）

### 4.1 Slack 接活：allowlist → 单 owner，且**降权运行**

- 配置四件套：`SLACK_CHANNEL_NAME / SLACK_TEAM_ID / SLACK_USER_IDS / SLACK_DOT_ID`（[index.ts:54-60](https://github.com/CopilotKit/OpenDots/blob/main/src/server/index.ts#L54-L60)、[docs/SETUP.md:152-163](https://github.com/CopilotKit/OpenDots/blob/main/docs/SETUP.md#L152-L163)）。
- 身份收敛：`slackIdentity()` 要求 provider=slack、tenant.id=团队白名单、actor 是 human 且在用户白名单里，**通过则一律返回 `{id: ownerId, name:'OpenDots owner'}`**（[slack-channel.ts:31-44](https://github.com/CopilotKit/OpenDots/blob/main/src/server/slack-channel.ts#L31-L44)）；`slackHandlers.eligible()` 再查 `message.user.id === ownerId` 且 `operation.kind === 'created'`（编辑/删除/非白名单用户不触发，[slack-channel.ts:56-61](https://github.com/CopilotKit/OpenDots/blob/main/src/server/slack-channel.ts#L56-L61)）。
- 会话语义：@提及 → `thread.subscribe()` → `runAgent()`；之后只回**已订阅线程**的后续消息（[slack-channel.ts:109-140](https://github.com/CopilotKit/OpenDots/blob/main/src/server/slack-channel.ts#L109-L140)）；`store: { concurrency: 'serial' }`（[slack-channel.ts:154](https://github.com/CopilotKit/OpenDots/blob/main/src/server/slack-channel.ts#L154)）。全局 paused 时只回一句"OpenDots is paused…"不执行（[slack-channel.ts:74-81](https://github.com/CopilotKit/OpenDots/blob/main/src/server/slack-channel.ts#L74-L81)）。
- **接活即自动建绑定**：channel 轮次若线程未绑定，自动 `bindThread(…, 'Slack conversation')`（[dot-agent.ts:105-115](https://github.com/CopilotKit/OpenDots/blob/main/src/server/dot-agent.ts#L105-L115)）。
- **降权（最关键）**：`this.channel === true` 时 `clientTools = []`，即**审批门工具（页面保存审批、连接动作审批）在 Slack/无头轮次里根本不下发**；注释直说 "Owner approval happens in the web app's chat, so channel turns and headless runs cannot use approval-gated connection tools."（[dot-agent.ts:301-312](https://github.com/CopilotKit/OpenDots/blob/main/src/server/dot-agent.ts#L301-L312)）。MCP 写工具此时返回 `status:'unavailable'`，提示"去网页端继续"（[connection-tools.ts:29-46](https://github.com/CopilotKit/OpenDots/blob/main/src/server/connection-tools.ts#L29-L46)）。channel 轮次的错误统一换成无细节的 `channelError()`，不外泄 provider 信息（[dot-agent.ts:32-36](https://github.com/CopilotKit/OpenDots/blob/main/src/server/dot-agent.ts#L32-L36)、[439-450](https://github.com/CopilotKit/OpenDots/blob/main/src/server/dot-agent.ts#L439-L450)）。
- Slack 只绑定**一个** Dot（`SLACK_DOT_ID` 缺省取第一个 Dot），且启动时校验必须存在，否则抛错（[platform.ts:60-80](https://github.com/CopilotKit/OpenDots/blob/main/src/server/platform.ts#L60-L80)）。

### 4.2 网页端边界：owner token + 路由白名单

- API 鉴权：host/origin/`sec-fetch-site` 校验 + `OWNER_TOKEN` 常量时间比较（[app.ts:38-91](https://github.com/CopilotKit/OpenDots/blob/main/src/server/app.ts#L38-L91)）。
- **runtime 路由白名单**（防"用任意 threadId 调别的 Dot"）[runtime-scope.ts](https://github.com/CopilotKit/OpenDots/blob/main/src/server/runtime-scope.ts)：只放行 `info`、`threads`、`threads/subscribe`、`agent/<id>/(run|connect|suggest)`、`agent/<id>/stop/<thread>`、`threads/<id>/(messages|events|state|archive)`；保留后缀（clear/inspector-*/transcribe/annotate…）直接 deny；**URL、body、query 三处出现的 agentId/threadId 必须互相一致**，`agentId` 必须是存在的 Dot，`threadId` 必须 `requireThread(threadId, agentId)` 绑定通过（[runtime-scope.ts:27-80](https://github.com/CopilotKit/OpenDots/blob/main/src/server/runtime-scope.ts#L27-L80)）。

### 4.3 审批门（写动作的唯一通路）

MCP 写工具链路（[connection-tools.ts](https://github.com/CopilotKit/OpenDots/blob/main/src/server/connection-tools.ts) → [connection-store.ts](https://github.com/CopilotKit/OpenDots/blob/main/src/server/connection-store.ts) → [connection-routes.ts](https://github.com/CopilotKit/OpenDots/blob/main/src/server/connection-routes.ts)）：

1. 模型调用 gated 工具 → **不执行**，只写 `mcp_approvals`（存 threadId/dotId/connectionId/tool/**arguments**）并返回 `approval_required + approvalId`（[connection-tools.ts:29-46](https://github.com/CopilotKit/OpenDots/blob/main/src/server/connection-tools.ts#L29-L46)、[connection-store.ts:104-124](https://github.com/CopilotKit/OpenDots/blob/main/src/server/connection-store.ts#L104-L124)）。
2. 模型调 `request_connection_action(approvalId, summary)` → 前端渲染审批卡片（[shared/connection-types.ts:38-49](https://github.com/CopilotKit/OpenDots/blob/main/src/shared/connection-types.ts#L38-L49)）。
3. **唯一执行路径** `POST /conversations/:id/connection-actions`（[connection-routes.ts:110-158](https://github.com/CopilotKit/OpenDots/blob/main/src/server/connection-routes.ts#L110-L158)），四重约束：同线程、1 小时 TTL（`APPROVAL_TTL_MS`，[connection-types.ts:37](https://github.com/CopilotKit/OpenDots/blob/main/src/shared/connection-types.ts#L37)）、该 Dot 的该工具此刻仍 enabled（`connections.bound`）、**`claimAction` 用 `INSERT OR IGNORE` 保证一个审批只跑一次**（[connection-store.ts:170-185](https://github.com/CopilotKit/OpenDots/blob/main/src/server/connection-store.ts#L170-L185)）；且"跑的是**存下来的** connection/tool/arguments，不是审批请求里带的参数"（[connection-routes.ts:110-112](https://github.com/CopilotKit/OpenDots/blob/main/src/server/connection-routes.ts#L110-L112)）。
4. 结果落 `mcp_actions`（主键 threadId+toolCallId，带 `approvalId` 外键式绑定），重开对话能看到回执；同审批换 toolCallId 重放会 409（[connection-routes.ts:119-153](https://github.com/CopilotKit/OpenDots/blob/main/src/server/connection-routes.ts#L119-L153)、[connection-store.ts:158-167](https://github.com/CopilotKit/OpenDots/blob/main/src/server/connection-store.ts#L158-L167)）。

同构的第二个审批门是**页面保存审批** `review_space_page`（[shared/page-review.ts](https://github.com/CopilotKit/OpenDots/blob/main/src/shared/page-review.ts)），也是 client-side HITL、同样不下发给 channel/headless。

### 4.4 计算机（每 Dot 容器）的边界

- 权限默认全关、按 Dot 存（[computer-store.ts:12-26](https://github.com/CopilotKit/OpenDots/blob/main/src/server/computer-store.ts#L12-L26)）。
- 每次动作 `audited()`：先插 `pending` 审计再执行，成功/失败回填；保留每 Dot 最近 1000 条、查询只回 50 条（[computer-service.ts:230-246](https://github.com/CopilotKit/OpenDots/blob/main/src/server/computer-service.ts#L230-L246)、[computer-store.ts:27-50](https://github.com/CopilotKit/OpenDots/blob/main/src/server/computer-store.ts#L27-L50)）；审计**刻意不含**输入值/文件内容/完整命令（[docs/COMPUTERS.md](https://github.com/CopilotKit/OpenDots/blob/main/docs/COMPUTERS.md)）。
- `human_*` 动作 owner-only，agent 调直接抛错（[computer-service.ts:334-336](https://github.com/CopilotKit/OpenDots/blob/main/src/server/computer-service.ts#L334-L336)）；agent 侧工具列表过滤掉所有 `human_` 前缀（[computer-tools.ts:10-11](https://github.com/CopilotKit/OpenDots/blob/main/src/server/computer-tools.ts#L10-L11)）。
- 每 Dot 派生独立凭据 `HMAC(computerToken, "opendots-computer:<dotId>")`（[computer-service.ts:41-45](https://github.com/CopilotKit/OpenDots/blob/main/src/server/computer-service.ts#L41-L45)）；上游返回的 URL 必须绑定到该 Dot 的容器/端口否则拒（[computer-service.ts:152-184](https://github.com/CopilotKit/OpenDots/blob/main/src/server/computer-service.ts#L152-L184)）；上游响应里的三个 secret 一律替换为 `[redacted]`（[computer-service.ts:109-116](https://github.com/CopilotKit/OpenDots/blob/main/src/server/computer-service.ts#L109-L116)）。
- 人工接管（take/release control）与 409 冲突提示"不要绕过 takeover"（[computer-service.ts:269-323](https://github.com/CopilotKit/OpenDots/blob/main/src/server/computer-service.ts#L269-L323)、[88-91](https://github.com/CopilotKit/OpenDots/blob/main/src/server/computer-service.ts#L88-L91)）。

### 4.5 日志与错误的脱敏纪律（可复用）

`safeFailure()` 只保留 Error 类名 + 合法 HTTP 状态码，绝不把 provider 消息/栈写进日志或 Slack（[slack-channel.ts:11-28](https://github.com/CopilotKit/OpenDots/blob/main/src/server/slack-channel.ts#L11-L28)）；Runner 的 tick 失败只打一行通用错误，"Do not log task content, provider responses, or database details"（[runner.ts:50-54](https://github.com/CopilotKit/OpenDots/blob/main/src/server/runner.ts#L50-L54)）；API 兜底错误也只回通用文案（[app.ts:242-251](https://github.com/CopilotKit/OpenDots/blob/main/src/server/app.ts#L242-L251)）。

---

## 5. "受管 Run"机制与本项目的同构点（关注点④前半）

OpenDots 的 `Task/Run` 与本项目 `GoalRun` 高度同构，逐条对照：

| 机制 | OpenDots 实现 | 证据 |
|---|---|---|
| 租约 claim | `BEGIN IMMEDIATE` 事务内：过期租约先失效 → 取 queued 或到期待跑 → 写 `lease`+`leaseUntil` → 插 `runs` 行 → 记 event | [store.ts:210-246](https://github.com/CopilotKit/OpenDots/blob/main/src/server/store.ts#L210-L246) |
| fencing | `owns(claim)` = 状态仍 running 且 lease 相等；执行期每 100ms 校验 + `progress()` 每次事件落库前再校验，失权即 abort | [store.ts:247-250](https://github.com/CopilotKit/OpenDots/blob/main/src/server/store.ts#L247-L250)、[runner.ts:66-91](https://github.com/CopilotKit/OpenDots/blob/main/src/server/runner.ts#L66-L91) |
| 落库只认所有权 | `finish/fail/interrupt` 全部先 `if (!this.owns(claim)) return` | [store.ts:251-298](https://github.com/CopilotKit/OpenDots/blob/main/src/server/store.ts#L251-L298) |
| **中断不静默重跑** | 租约过期/进程退出/权限变化 → `status='interrupted'` + 原因文案；UI 按钮显示 **"Retry after review"**（failed 才是 "Retry task"） | [store.ts:152-166](https://github.com/CopilotKit/OpenDots/blob/main/src/server/store.ts#L152-L166)、[TaskActions.tsx:30-33](https://github.com/CopilotKit/OpenDots/blob/main/src/client/TaskActions.tsx#L30-L33)、[WorkspaceDialog.tsx:422-423](https://github.com/CopilotKit/OpenDots/blob/main/src/client/WorkspaceDialog.tsx#L422-L423) |
| 效果可能已发生 | README："Completed effects may already be present even when a run has no final result" | [README:218](https://github.com/CopilotKit/OpenDots/blob/main/README.md#L218) |
| 事件时间线 | `events(taskId, runId, text, createdAt)`，detail 接口回 `task+runs+events` | [store.ts:34-39](https://github.com/CopilotKit/OpenDots/blob/main/src/server/store.ts#L34-L39)、[124-144](https://github.com/CopilotKit/OpenDots/blob/main/src/server/store.ts#L124-L144) |
| 超时上限 | `agentRunTimeoutMs` 全局；DotAgent 单轮也设同一超时并给 channel 轮次换通用文案 | [runner.ts:74-82](https://github.com/CopilotKit/OpenDots/blob/main/src/server/runner.ts#L74-L82)、[dot-agent.ts:72-85](https://github.com/CopilotKit/OpenDots/blob/main/src/server/dot-agent.ts#L72-L85) |

**差异**：OpenDots **没有**显式 `outcome_unknown` 字段（只有 `interrupted` + 文案），没有回执表（Run 的 `result` 直接存 runs 行）、没有产物指针、没有审批门对 Run 的归因字段；这些正是 §3 主表里 OpenMuse 已列、本项目要自己落的部分。另外它的"后台工作"与"会话"是同一 Conversation（任务回原会话跑），而非独立 Run 容器。

---

## 6. 与本项目形态的对照（关注点④后半，落 §7 / §12.2）

### 6.1 落 §7 目标工作台

- **"列表 → 详情（runs + events 时间线）"的形态可直接借鉴**：`GET /api/tasks/:id` 返回 `{task, runs[], events[]}`（[store.ts:124-144](https://github.com/CopilotKit/OpenDots/blob/main/src/server/store.ts#L124-L144)），前端把 `interrupted` 单独染色并给 "Retry after review" 按钮 —— 对应 §7 "运行结果区：GoalRun 列表 → 回执详情 + `outcome_unknown` 醒目标记"。OpenDots 证明了**中断态必须在 UI 上与失败态区分开**，否则用户会把"可能已生效"当成"没跑"。
- **状态卡片挂对话**：OpenDots 的做法是 Dot 头像/状态常驻会话上方 + side panel 显示结果或 computer（README "Text and calls" 节），与 §7 "对话面板显示关联目标实时状态卡片" 同构。
- **设置即权限**：OpenDots 把所有权限集中在 Settings + Dot 编辑对话框（`WorkspaceDialog`），§7 若要做"目标详情四区"，权限/预算/审批开关建议同屏可见，参考其 `dotSchema` 字段分组。

### 6.2 落 §12.2 群组分工

- **OpenDots 明确没有群组**（"multi-Dot group conversations and automatic delegation are further work"，[README:224](https://github.com/CopilotKit/OpenDots/blob/main/README.md#L224)）：多 Dot 是**并列的 specialist，各自独立会话**（`Platform.runtime.agents` 按 Dot 逐个注册，[platform.ts:89-104](https://github.com/CopilotKit/OpenDots/blob/main/src/server/platform.ts#L89-L104)）。所以 §12.2 的 `assigned_role`、群组消息表、成员归因**不能从 OpenDots 抄，只能从 Rakazo/MetaGPT/AutoGen 抄**；OpenDots 提供的是"多 Dot 并存的权限与接活边界"这一侧的反例基线。
- 可借的三条：①**外部渠道进来的 Run 必须降权**（channel 不下发审批门工具）→ §12.2 W4 "成员不得绕过审批门互相授权"的渠道版；②**身份收敛到 owner**（Slack 白名单→单一 ownerId）→ 群组若要多成员，必须先有 `actor_agent_id`/`requested_by` 归因，OpenDots 的单 owner 模型在这一层是不够的；③**会话绑定表**（`thread_bindings` 冻结 `learningContainerId`、`task_threads` 绑任务到会话）→ §12.2 W1 "群组消息锚点独立于 goal_run"的同族做法：**绑定关系单独成表，且创建时冻结**。

---

## 7. 机制映射候选（供 §3 主表回填，本笔记不改 brief-plan）

| # | OpenDots 机制（证据） | 落点 | 建议动作 | 置信度 |
|---|---|---|---|---|
| M1 | 租约 claim + `owns()` fencing + 过期/退出 → `interrupted` + "Retry after review"（[store.ts:210-250](https://github.com/CopilotKit/OpenDots/blob/main/src/server/store.ts#L210-L250)、[runner.ts:56-113](https://github.com/CopilotKit/OpenDots/blob/main/src/server/runner.ts#L56-L113)、[TaskActions.tsx:30-33](https://github.com/CopilotKit/OpenDots/blob/main/src/client/TaskActions.tsx#L30-L33)） | §5.2 执行规则、§4.3 状态机、§7 运行结果区 | 与 OpenMuse 的 claim/lease 互为佐证；补一条"UI 必须区分 interrupted 与 failed"的呈现规则 | 高（源码实读，且与 §3 openmuse 行同族） |
| M2 | 三层权限 AND（全局×Dot×tool）+ 100ms/50ms 热撤销 watcher（[dot-agent.ts:133-168](https://github.com/CopilotKit/OpenDots/blob/main/src/server/dot-agent.ts#L133-L168)、[computer-service.ts:348-354](https://github.com/CopilotKit/OpenDots/blob/main/src/server/computer-service.ts#L348-L354)） | §5.5 治理、§12.2 W4 授权矩阵 | 采纳"权限变更即刻中断在途 Run"语义；授权矩阵按 角色×工具 三层求值 | 高 |
| M3 | 审批门 = 存参 + claim-once + TTL + approvalId 回执，唯一执行路径在 owner 路由（[connection-tools.ts:24-50](https://github.com/CopilotKit/OpenDots/blob/main/src/server/connection-tools.ts#L24-L50)、[connection-routes.ts:110-158](https://github.com/CopilotKit/OpenDots/blob/main/src/server/connection-routes.ts#L110-L158)、[connection-store.ts:168-196](https://github.com/CopilotKit/OpenDots/blob/main/src/server/connection-store.ts#L168-L196)） | §5.5 审批、§12.2 W4 `requested_by` 归因 | 采纳"跑存下来的参数、一个审批只跑一次、结果绑定审批"三条；**需补**成员归因字段（OpenDots 只有单 owner） | 高（缺归因维度） |
| M4 | Slack allowlist → 单 owner 映射 + channel 轮次不下发审批门工具 + paused 熔断（[slack-channel.ts:31-61](https://github.com/CopilotKit/OpenDots/blob/main/src/server/slack-channel.ts#L31-L61)、[dot-agent.ts:301-312](https://github.com/CopilotKit/OpenDots/blob/main/src/server/dot-agent.ts#L301-L312)） | §12.2 群组接活边界、§5.5 | 采纳"外部渠道 = 降权执行面"；群组多成员时把"单 owner 收敛"换成 `actor_agent_id` 归因 | 中高 |
| M5 | Dot = SQLite 行 + zod strict schema + 运行时装配能力；会话绑定单独成表并创建时冻结（[workspace-routes.ts:11-27](https://github.com/CopilotKit/OpenDots/blob/main/src/server/workspace-routes.ts#L11-L27)、[workspace.ts:269-311](https://github.com/CopilotKit/OpenDots/blob/main/src/server/workspace.ts#L269-L311)） | §4.4 领域模型、§7、§12.2 W1 | 采纳"配置 schema 化 + 能力装配"分离的结构；**不采纳**其无 capability 自描述（本项目目标需可声明能力） | 中（结构可借鉴，能力模型需自建） |

---

## 8. 不确定处与未验证声明（明示）

1. **纯静态走读**：未编译、未 `npm test`、未起服务。`tests/` 只读了用例标题，因此"某行为有测试覆盖"只能说到"存在同名用例"，不能说"测试通过"。
2. **上游自述未复核**：README 中"Live Intelligence/model 2026-09-29 验证""computer 本地实测""Slack 与语音 compute delegation 仍需 connected-service 验证"等均为上游声明（[README:220](https://github.com/CopilotKit/OpenDots/blob/main/README.md#L220)）。
3. **未读文件导致的空白**：语音通话的 compute 委派实现（`voice.ts`）、Parallel 检索内部实现（`parallel.ts`/`research.ts`）、Automatic Learning 路由（`learning.ts`）、Composio 会话（`composio*.ts`）——本笔记对这些只引 README/SETUP.md 文字，**属文档级而非源码级结论**。
4. **`docs/brief-plan.md` §3.1 该行状态未改**（子代理禁改）：回填时应把"待读"改为"已走读（笔记见 `docs/essay-study/opendots-2026.md`）"，并按 §1 的差异表修正"关联点"列。
5. **仓库与二手定位的差异已按 CONVENTIONS §3 规则 2 留痕**（§1 表）；本笔记所有事实性论断均附源码路径与 GitHub 可点击链接，未读处均已标注。
