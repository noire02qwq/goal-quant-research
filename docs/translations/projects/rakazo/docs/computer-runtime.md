# 计算机运行时（Computer runtime）

> 来源：https://github.com/elie222/rakazo/blob/main/docs/computer-runtime.md
> 原文：oss-repos/rakazo/docs/computer-runtime.md
> 翻译日期：2026-11-03 ｜ 范围：全文 ｜ 方式：机器翻译初稿，未经人工校对
> 引用于：docs/essay-study/rakazo-2026.md、docs/brief-plan.md §3/§3.1

Rakazo 把 agent 运行时和 computer 运行时分开：

```text
chat/API -> one Pi agent session -> Rakazo computer tools -> SandboxProvider -> E2B / Daytona / Boat
                                                   |-> Docker
                                                   |-> desktop/fake

SandboxProvider workspace <-> AgentHomeStore <-> Rakazo-owned DATA_DIR
```

Pi 运行在 Rakazo 的 API/worker 进程里，不由 E2B 安装或执行。内置工具是普通的 Pi 工具，不是 Claude 或 MCP 专用工具，所以任何经由 Pi 暴露的模型都能调用它们。屏幕操作仍然要求模型能接收图像工具结果并理解截图。

## 计算机契约（Computer contract）

每个 workspace 默认得到一台 Team Computer。Bot 共享它的文件和已装工具。每个 Team bot 从 `bots/<bot-id>/` 开始工作，故意共享的内容放在 `shared/`。这些目录只是用来组织工作，不是安全边界：任何 Team bot 都能访问整个 Team workspace。Bot 也可以改用 Private Computer，整个 workspace 都是它的家。

每个活跃的 Team bot 都有自己的 X display 和 Chrome 进程，带有以该 bot 身份为键的持久 Chrome profile。登录信息、cookie 和浏览器历史互相独立。Profile 从不从其他 bot 复制，也不会在桌面释放时被合并或删除。两个 bot 都保留自己的改动；重新打开某个 bot 时，即使用了不同的 display 槽位，也会沿用它已有的 profile。Team 运行使用带围栏的按 bot 数据库租约：不同 bot 可以并发操作，而同一个 bot 同一时刻只有一个 computer driver。

Docker、E2B、Daytona 和 Boat 使用同一套 Linux 桌面生命周期命令。远程 adapter 共享分配、观察、动作和控制处理；provider 代码负责提供命令执行、持久 workspace 路径和屏幕 URL。Boat 通过其 `hostPort` API 的受保护端口来暴露共享运行时，而不是用它默认的桌面 API。查看和控制使用各自独立、可撤销的 websocket capability；拆除时会先断开客户端，再复用 display 槽位。拆除失败则该槽位保持预留，供稍后重试。

桌面栈是懒启动的：bot 用到图形工具时才启动。默认没有配置桌面数量上限；一台计算机可以承载 100 个甚至更多 bot profile，同时运行的桌面上限取决于它的 RAM、CPU、进程容量和可用的本地 debugger 端口。Docker 运维可以设一个正数 `SANDBOX_TEAM_SCREEN_LIMIT` 来限制活跃桌面数（`0` 表示不设）。超出显式上限的请求返回 `MULTI_SCREEN_UNAVAILABLE`，此时 shell 和文件工具仍然可用。

所有桌面共享一个带 token 保护的屏幕网关，因此增加桌面不需要发布更多端口。每个查看/控制 capability 指向一个唯一的本地 Unix socket，回收某个 display 不会把旧连接重定向给下一个 bot。不活跃的 bot 不会各自常驻一个 Chrome。关闭 viewer 之后桌面保持完好。在 Docker 以及 Boat、E2B、Daytona、Railway 计算机的 Linux 桌面上，一次运行成功完成后会撤销该运行的控制权，但保留该 bot 的屏幕和浏览器给下一次运行——已打开的查看窗口和已登录的会话都保持不变。确实重启过的浏览器会恢复它上次的会话。如果达到了配置的 Team 屏幕上限，最老的空闲、无人控制的屏幕可能被拆掉，让给新的 bot。失败或取消的运行、以及显式删除计算机，仍然会拆除它们的屏幕。CreateOS 屏幕照旧释放。整机空闲关机会停掉剩余进程但保留 workspace。没有单独的"每桌面不活跃"计时器。持久 profile 占用磁盘，但不需要一个常驻的 Chrome 进程。

`SandboxProvider` 是 provider 边界。后端必须实现：

- 生命周期：provision/reconnect、stop、destroy；
- 桌面：观察、有序的批量动作、用户输入，以及实时屏幕会话；
- 执行：机器内的命令；
- 文件：列目录/读/写，以及完整的 workspace 导入/导出。

在支持图形的计算机上，模型会得到 `browser_navigate`、`browser_snapshot` 和 `browser_act`，用于读取页面文本和元素 ref。默认的 `computer` 浏览器 provider 通过沙箱可选的 `pageBrowser` 契约驱动可见的 Chromium 标签页。Docker 用与桌面控制相同的托管屏幕和租约检查来实现该契约；更新计算机镜像即可安装 helper。Boat 则在 bot 自己的屏幕上实现它：其保存的基础快照自带 agent-browser，每次启动都会从 API 自己的副本写入 helper，因此一台计算机运行的 helper 总是与发布它的那版 API 配套。其他 provider 在实现该契约之前继续使用现有的桌面工具。不需要任何托管浏览器服务或 API key。

计算机容器是安全边界。Team bot 共享同一个 OS 用户、workspace、浏览器 profile 和 shell/X11 访问；屏幕租约协调的是工具调用，而不是容器内彼此不信任的进程。CDP 只绑定到容器的 loopback 接口，不作为主机端口发布。需要隔离的工作负载请使用单独的计算机。

Helper 通过 [agent-browser](https://github.com/vercel-labs/agent-browser) 驱动那个 Chromium，版本在镜像里以 sha256 固定并校验（`infra/sandboxes/computer/install-agent-browser.sh`）。它有自己的配置，不自动接受对话框，也没有域名白名单（agent-browser 在 CDP 层没有白名单；导航策略留在 helper 里）。每次动作之前，helper 都会用一份全新的 snapshot 核对每个 ref——否则 agent-browser 可能对一个角色和名字相同、甚至位于另一个页面上的替代元素动手。

已保存的登录凭据、卡片和支付 token 从不经过 agent-browser：`page_secrets.py` 直接在 CDP 上输入它们，输入前会先在字段所属 frame 的隔离世界里核对该 frame 确实位于正确的站点。Snapshot 包含有上限的页面文本和最多 80 个可交互元素，并遮蔽密码、已保存的登录和卡片。`browser_navigate` 返回页面的形式与 `browser_snapshot` 相同。Frame 按所属站点列出、按 ref 操作；支付提供方的 frame 被排除在外，只能通过 `fill_card` 输入卡片。动作失败时会报告已确认的进展，以及结果是否不确定：继续之前先检查当前状态，永远不要自动重放已完成或不确定的动作。对于没有视觉能力的模型，页面工具无法操作时应请求接管。

Fake 计算机或显式指定 `BROWSER_PROVIDER=fake|emulator` 时，测试使用进程内会话。这些会话并不是实时已登录的浏览器。浏览器改动沿用现有的 teaching guard 和 workspace 检查点流程。`computer_observe`、批量 `computer_act`、`open_path`、`launch_app`、`shell` 和文件工具会根据计算机与模型的能力继续可用。连续相同的桌面帧保留元数据，但省略重复的图像字节，不送进模型上下文。工具结果会说明上一张截图仍然有效。当重复的相同视觉动作多次都未能改变画面之后，computer_act 会拒绝再执行同一动作，并把 agent 指向页面文本工具。

人类输入和 agent 输入可以在不同的 Team 屏幕上并存。"Take control" 授予用户对该 bot 屏幕的独占控制租约，嵌入式 viewer 便接受输入。对 Team bot 而言，如果该 bot 正持有活跃的 computer 执行租约或正在运行的 run，接管会被拒绝并返回 HTTP 409（"Stop the bot first"），除非该 run 处于 `waiting_takeover`（bot 正在请求受保护输入）。先停掉 bot 再接管；释放之后 agent 可以继续。当模型明确需要受保护输入或人类判断时，`request_takeover` 仍然可用。在运行不计费的 provider 上，等待中的接管会让计算机在请求之后保持唤醒 30 分钟，使用户到达时登录、2FA 或 CAPTCHA 页面还开着；之后计算机挂起，而 run 继续等待。计费的 provider 按正常空闲计时器处理，该请求会重置计时器。

## 终端与文件（Terminal and files）

网页和桌面的计算机视图会在屏幕上方的一个 dock 里打开终端和文件浏览器。dock 上的浏览器按钮会隐藏这些窗口但保留其会话，于是整块屏幕重新可见。

**终端（Terminal）**

- Activity 视图始终显示 bot 在它计算机上做过的事，实时与历史都有。每个动作记录为一条 `computer.command` 事件：
  - `shell` 命令，附带脱敏后的命令和输出尾部；
  - `write_file`、`attach_file`、`open_path` 和 `launch_app`，各记一行，写入类带文件大小，失败的带错误信息。

  只读工具（`read_file`、`list_files`）不计入。用户持有控制权时 bot 仍可以执行命令，所以这条动态不会消失。
- 不持有控制权时（例如控制已释放或已过期），"Open shell" 按钮可以重新取得控制并切到 shell。
- 持有控制权的用户还会看到一个带交互式 shell 的 Shell 标签页。它首次使用时启动，切换标签时保持连接，断线后会重连到一个全新的 shell。`computer.terminalUrl` 在屏幕网关旁启动一个小的 PTY 服务器。
  - 它绑定到该 display 的控制 token，通过与控制屏幕相同的封存 capability 和网关访问。同一租约下的后续会话（另一个标签、重新打开的窗口）会带着自己的 shell 加入该服务器，因此已经打开的 shell 继续运行。
  - 它以计算机的 workspace 用户运行（绝不是 root），环境与 bot 的 `shell` 工具相同。Docker exec 继承容器的非 root 用户；E2B、Daytona 和 Boat 使用与 `shell` 相同的命令运行器。当计算机以一个没有 passwd 条目的 host uid 运行时（macOS 上的 Docker），终端通过 nss_wrapper 在自己的会话里把它命名为 `rakazo`，使提示符和 `whoami` 正常工作；`/etc/passwd` 保持不变。
  - 释放控制、控制过期或屏幕拆除都会停掉它，断开所有 shell，并删除其会话文件。
- Provider 通过 `SandboxProvider.connectTerminal` 选择支持它。Docker、E2B、Daytona 和 Boat 都支持。Host（`desktop`）计算机从不暴露浏览器 shell；没有该能力的其他计算机只显示 Activity。
- Fake provider 从一个 loopback websocket 网关提供模拟 shell，使用同一套帧协议。这样测试可以通过封存 capability 和 web 代理驱动浏览器终端，而不暴露主机 shell。

**文件（Files）**

- 停止状态的计算机也能通过已存储的 workspace 浏览文件、预览文本。
- Files 窗口可见时，打开的文件夹每隔几秒、以及 bot 每条命令之后刷新一次，shell 或 bot 造成的改动无需重新打开就能看到。
- 下载需要计算机处于运行状态。
- 上传还需要控制权。上传落在 bot 的 workspace 路径下，受附件大小上限限制。

## 屏幕连接诊断（Screen connection diagnostics）

Web 服务会记录 `screen.proxy.target_rejected`、`screen.proxy.http_failed`、`screen.proxy.http_upstream_response`、`screen.proxy.websocket_handshake_failed`、`screen.proxy.websocket_error`、`screen.proxy.websocket_upgraded`、`screen.proxy.websocket_closed` 以及撤销事件。每个事件都带一个随机的 `screen.connection_id` 和一份查看/控制策略。WebSocket 关闭事件还包含上游握手是否完成、耗时，以及发起关闭的一方（`client`、`upstream` 或 `revoked`）。日志不含 capability URL、socket token、provider 主机名、cookie 和请求头。

Web 和 Electron 的屏幕 frame 是沙箱化的，应用看不到它内部。给代理页面加框之前，应用会先取一次该页面，并在屏幕位置显示一段固定的、本地化的代理拒绝原因（例如 "The screen did not respond."）。代理会给每个 noVNC 页面注入一个小 reporter：页面一运行就上报 `loading`，随后上报 `connecting`、`connected`、`failed`（其状态文本从不显示）或 `disconnected` 给应用；Rakazo 自己的 `embed.html` 设置同样的 noVNC class，因此 Docker 计算机也会上报。收到 `failed` 上报，或者停在 `loading` 之后 15 秒内再无动静，就显示错误和 Retry，而不是一个空白 frame。手机 app 遵循同样的屏幕上报，连接失败时提供 Retry。一直沉默的 frame 说明文档在该浏览器里从未执行；停在 `loading` 说明 noVNC 的模块从未完成求值；`failed` 上报说明页面运行了，但 noVNC 连不上。

这个 shim 还会从页面移除 `VideoDecoder`。1.7 之前的 noVNC 版本用顶层 `await` 探测 WebCodecs H.264 支持，而在某些 Android 设备上 `VideoDecoder.flush()` 永不返回，页面就卡在 `noVNC_loading` 且没有报错。屏幕从不使用 H.264。每个代理的屏幕响应都带 `Cache-Control: no-transform` 发送，这样 web 服务前面的 CDN 不会往页面里注入脚本或压缩页面。

屏幕显示连接错误时，先查 API 日志里 `computer.screenUrl` 是否成功，再看大致同一时刻 web 服务的 `screen.proxy.*` 事件。遇到 `screen.proxy.target_rejected`，读 `reason`：`invalid_path` 表示不是会话路径（没有联系 API）；`authority_rejected` 表示 API 响应非 OK（过期、已撤销或 API 出错）；`invalid_authority_response` 表示响应 OK 但 target body 无效或格式错误；`authority_unavailable` 表示请求、连通性或超时失败。上游错误或非 101 的握手指向 provider 的屏幕网关。升级成功但很快关闭的连接，指向握手之后的传输中断。如果 API 已经发出 URL 却没有出现 web 服务事件，检查浏览器 Network 面板及其 WebSocket 请求。不要把完整的 capability URL 贴进 issue 或日志。

## E2B 后端（E2B backend）

E2B adapter 使用 `@e2b/desktop`，Novita adapter 使用 `novita-sandbox`，负责机器生命周期、shell 命令、文件和端口 URL。每个 bot 桌面都使用共享的 Linux 运行时，包括第一个 bot。它的 X display、截图、输入和查看/控制传输与其他托管 provider 遵循相同的生命周期。

## Daytona 后端（Daytona backend）

数据库存储 provider 类型和不透明的 `providerRef`。该引用是一条加速路径，不是持久数据，只会回传给相同类型的 provider。机器缺失或 provider 类型发生变更时，会创建替代机器，并通过 provider 中立的契约恢复其 workspace。

## Boat 后端（Boat backend）

Boat adapter 使用 Boat 官方 TypeScript SDK 做生命周期、命令和文件操作。它以 `noEnv: true` 创建和恢复沙箱（由第三方提供 API key 时必需），并在计算机活跃期间刷新两小时的 TTL。共享运行时创建每个 bot 的 display 和 noVNC 传输，通过受保护的 Boat 端口托管暴露。Rakazo 加密的屏幕 capability 代理绑定查看/控制策略，不让 provider 凭据出现在浏览器可见的 URL 里。观察和动作都指向分配给该 bot 的 display。

Boat stop 会归档机器，resume 重新连接同一个不透明的沙箱 id。每个 bot 的 Chrome profile 位于可移植 workspace 下，并包含在 checkpoint/导出中。Boat 列出的 API 无法恢复的状态（已删除、已取消、快照数据过期，或 resume 修不了的 `error`）会报告为 gone，于是计算机被替换，并从它最后一个 checkpoint 恢复。

## 持久化（Persistence）

可移植的计算机 workspace 是持久边界。E2B 用 `/home/user/rakazo-home`；Docker 和本地 provider 暴露等价的 home。在 E2B 上，浏览器 profile 根植于该 workspace 的 `.browser-profiles` 下。Rakazo 在运行完成或失败时、显式 stop 之前、以及空闲挂起之前，把 workspace 检查点写入 `AgentHomeStore`。Docker 直接挂载 Rakazo 所有的 home，只在这些边界推进它的修订标记。新的或替换的机器在使用前会导入最新存储的 workspace。

`LocalAgentHomeStore` 把最新的 workspace 存在 `DATA_DIR/homes/<computer-home-key>` 下，检查点元数据单独存在 `DATA_DIR/home-revisions`。替换副本先暂存，再与当前副本互换，检查点按计算机串行化。这个实现只保留最新版，而不是不可变的修订归档。使用它的部署必须把 `DATA_DIR` 放在 Rakazo 所有的持久卷上，对该卷做静态加密，并把它纳入异地备份。

设置了 `OBJECT_STORAGE_BUCKET` 时，`ObjectAgentHomeStore` 让一个 S3 兼容 bucket 成为事实来源，`DATA_DIR/homes` 成为缓存，且不改变 agent 工具和沙箱 provider。每次检查点把 home 打包成一个包含目录和常规文件的归档，用 home 的数据密钥封存（64 KiB 一段的 AES-256-GCM，绑定到该 home 的 storage id 和 revision），以 `homes/<storage id>/<revision>` 上传，在计算机行上推进 revision，然后删除上一个对象。读取、恢复和 Docker 启动都会先把缓存提升到已存储的 revision。数据密钥由 space 的 content key 包裹并存在计算机行上，因此删除计算机就使它的对象不可读；worker 的 reconciler 随后删除没有任何计算机认领的对象。恢复只接受不含 `.` 或 `..` 段的相对路径，只创建目录和常规文件，并强制执行大小与条目上限。参见[自托管存储](./self-host-storage.md#bot-homes-in-object-storage)。

导出远程 workspace 之前，远程后端会让桌面浏览器安静下来，从而一致地复制 profile 数据库和登录状态。当另一个 bot 持有执行或用户控制租约时，运行检查点会推迟；最后完成的运行或空闲任务保存共享 workspace。空闲关机会先认领计算机再导出，防止快照期间有新 bot 启动。所有 home 的保存和恢复都排除可重建的缓存（`.cache`、`.npm`、`.pnpm-store`、`.yarn/cache`）、依赖（`node_modules`、`.venv`）、Python 字节码（`__pycache__`）、构建产物（`.next`、`.turbo`）、任意深度下的 `*.log` 文件，以及名为 `core` 或 `core.<digits>` 的常规文件。像 `packages/core` 这样的目录会保留。`.browser-profiles` 里现有的临时浏览器缓存、组件和锁同样被排除；登录状态保留。被排除的目录在遍历之前就跳过，不计入保存上限。保存绝不会把它们从一台运行中的计算机上删掉。超过 5 GiB 或一百万个文件的 home 保持运行但不保存，并在 bot 的会话线程里留一条系统提示。

一次性 OS 镜像不是可移植的磁盘快照。workspace 之外安装的系统包在换到另一个 provider 时会丢失；持久的机器定制应当用可复现的镜像或安装配方来表达。正因如此，将来切换后端才切实可行，而不必费力去翻译厂商专用的 VM 快照。

Docker 计算机自带 `uv`，可以做 rootless 的 Python CLI 安装。运行 `uv tool install <package>`；工具环境、命令 shim、托管的 Python 版本和缓存都留在持久 home 下。它安装的是 Python 命令行工具，不是 `apt` 依赖这类系统包。镜像还带 GitHub 的 `gh` CLI；bot 通过 device flow 认证 CLI，gh 把该凭据存在持久 home 下。`pdftotext`、`pandoc` 和 `openpyxl` 可用于从 PDF、文档和电子表格中提取文本。

## 验证（Verification）

[agent 验证指南](agent-verification.md)还描述了一次通过真实 Pi 的确定性联系人导出回放，可以使用有状态的 fake computer，也可以使用真实的 Docker Chromium。它不需要推理，与下面的视觉验收测试互补。

离线测试覆盖工具结果图像、动作解析、provider 一致性（包括 page-browser adapter 和 computer_act 回退）、workspace 检查点/恢复、provider SDK 翻译、生命周期集成，以及针对内存版 Boat API 的真实 Boat adapter。它们从不调用模型或真实沙箱。

显式验收测试需要 Docker（用于临时 Postgres）、`E2B_API_KEY`、`OPENROUTER_API_KEY`，以及一个有视觉能力的 OpenRouter 模型 id：

```bash
COMPUTER_E2E_MODEL=<vision-capable-openrouter-model-id> pnpm test:computer
```

它启动完整的 API，开通一台真实的 E2B 桌面，在沙箱内提供一个确定性页面，并请一个真实模型观察并点击某个按钮。该按钮在服务端创建一个标记；随后测试要求模型使用终端和文件工具，并核对该标记与记录的工具调用。最后，它销毁 provider 机器，通过过期的 provider 引用启动一台替代机器，并核对外部检查点确实恢复了模型创建的文件。该命令是选择性执行的，除非显式调用，否则 `pnpm test` 和 CI 都不会运行它。

### Docker 桌面生命周期回归（Docker desktop lifecycle regression）

先构建计算机镜像，然后运行 `VERIFY_DOCKER_TEAM_SCREENS=1 pnpm exec vitest run infra/sandboxes/supervisor/src/team-desktops.docker.test.ts`。设置 `RAKAZO_COMPUTER_IMAGE` 可以选择预构建镜像。测试使用一个禁用网络、带假浏览器状态的隔离 Docker 容器；它验证并行 Chrome 桌面访问本地 fixture 站点、cookie 相互独立、释放后的 profile 持久性、传输拆除，以及槽位复用之后旧的查看/控制 token 被拒绝。它同时覆盖 Docker 监督路径和远程 provider 使用的命令路径。默认单元测试在没有 Docker 的情况下离线验证 profile 持久性、分配和租约围栏。

## 计算机维护（Computer maintenance）

更新和恢复作为持久的后台任务运行。整机级预留会在操作保存并替换 workspace 期间，排除新的执行租约、stop、接管、空闲挂起和 computer 模式变更。进度单独存储，与计算机的开通围栏分开。Web 和 Electron 显示对话框或紧凑的后台胶囊，手机端用原生 sheet。重新打开 app 时，会从 API 恢复进行中的操作和失败记录。

更新会用配置的 provider/镜像显式重建；`canUpdate` 表示计算机支持该动作，不表示检测到了更新的镜像。Provider 迁移和镜像版本发现不属于这个 UI。更新会在拆除前为活跃工作打检查点；在拆除之前就失败的更新会让正在运行的计算机继续运行，因此 Recover 仍然可以先保存那些工作。当 Recover 已经导出工作却无法存储或记录时，它会停止而不是重建。恢复可以回退到最后保存的 workspace，因此它的失败操作会警告未保存的工作可能丢失。

Reconciler 在漏掉入队之后会重新发布排队的操作。已经被认领的任务绝不会被破坏性地重放。一个心跳停止十分钟的 worker 会被标记为中断，并保持预留状态，直到它的 provider 调用尘埃落定。只有在那之后，恢复才可用。如果某个 worker 已经永久消失，运维人员必须先停止受影响的 worker、确认 provider 操作已经停止，然后才能在中断对话框里使用仅服务器 owner 可用的 **Release computer** 操作。它的确认要求显式断言 worker 和 provider 操作均已停止，之后才开放正常的恢复。对应的 RPC 是 `computer/releaseInterrupted`，参数为 `{ id, workersStopped: true }`，只接受 owner 当前 workspace 中的中断操作。仅仅一个过期的心跳绝不会授权接管。进度报告的是实际的生命周期阶段，而不是估算的百分比；workspace 文件和浏览器 profile 是可移植的，workspace 之外的系统包则不然。
