# 每个 Dot 一台电脑（A computer for each Dot）

> 来源：https://github.com/CopilotKit/OpenDots/blob/main/docs/COMPUTERS.md
> 原文：oss-repos/OpenDots/docs/COMPUTERS.md
> 翻译日期：2026-11-03 ｜ 范围：全文 ｜ 方式：机器翻译初稿，未经人工校对
> 引用于：docs/essay-study/opendots-2026.md、docs/brief-plan.md §3/§3.1

OpenDots 通过 [OpenBot](https://github.com/CopilotKit/OpenBot) 的 computer service 与 supervisor，把每个 specialist 连接到它专属的容器。Dot 的 ID 决定它使用的电脑和持久化卷。文件与浏览器 profile 在容器停止、重启后依然保留；它们与 Spaces 页面、CopilotKit 会话历史彼此独立。

应用把选定的 computer tools 暴露给 Dot 自己的 agent——网页聊天、Slack、定时任务和语音的 compute delegation 用的都是同一个 agent。浏览器、工作区文件和 shell 权限按 Dot 逐个保存，由服务器校验，且默认全部关闭。一旦 computer service 不可用，任何操作都不会降级回你宿主机的 shell 或文件。

## 本地开发时启动服务

需要一个可用的 Docker Engine，带 Compose v2，并支持 BuildKit 的额外构建上下文。应用本身请按 [Setup](SETUP.md) 的说明使用 Node.js 24。往 `.env` 里加入两个不同的随机密钥（各至少 24 个字符），并设置：

```dotenv
COMPUTER_SUPERVISOR_URL=http://127.0.0.1:4312
COMPUTER_SUPERVISOR_TOKEN=REPLACE_WITH_A_RANDOM_SECRET
COMPUTER_TOKEN=REPLACE_WITH_A_DIFFERENT_RANDOM_SECRET
COMPUTER_NAMESPACE=opendots
```

不要沿用占位值。supervisor token 用于鉴权生命周期请求；computer token 则是一个 master，用来为每个 Dot 派生各自的凭据，master 本身只保存在应用和 supervisor 中。

启动 supervisor 之前先构建两个镜像：

```sh
docker compose -f compose.computers.yml build computer-image computer-supervisor
docker compose -f compose.computers.yml up -d computer-supervisor
npm run dev
```

computer-image 服务只是一个构建目标，并不是拿来运行的共享电脑。你启动某个 Dot 的电脑时，supervisor 才会创建容器。在本地这种部署方式下，每台电脑都会发布一个动态的 loopback 端口供应用访问；端口 4312 是 loopback 上的 supervisor 端点。本地控制网络使用普通 bridge 网络，这样 Docker 才能发布该端口。container-app overlay 则把控制网络设为 internal 并去掉宿主端口，应用改用服务 DNS 进行连接。

打开某个 Dot 的 **Computer** 面板，开启 computer access 和你想要的能力，然后点击 **Start**。检查它的状态，访问一个页面，再刷新它的屏幕。只有当该 Dot 确实需要执行命令时，才授予 shell 访问权限。

## 在容器中运行应用

除了 computer 相关的密钥，还要配置好既有的 `OWNER_TOKEN` 和 `BROWSER_SECRET`。使用把应用接入 supervisor 与 computer 网络的那份 overlay：

```sh
docker compose -f compose.yml -f compose.computers.yml -f compose.computers-app.yml build computer-image computer-supervisor app browser
docker compose -f compose.yml -f compose.computers.yml -f compose.computers-app.yml up -d app browser computer-supervisor
```

在这种方式下，应用通过容器名访问各台电脑，电脑不发布任何宿主端口。supervisor 位于独立的控制网络上，且只有 supervisor 挂载 Docker socket——Web 应用和 Dot 的电脑都拿不到这个 socket。修改 namespace 会改变选中哪些容器和卷；每次部署都请保持 namespace 稳定且唯一。

## 使用电脑

- **浏览器**：访问并查看当前页面，包括截图和元素快照。浏览器 profile 会在容器重启后保留 cookie 和登录状态。
- **接管（Take control）**：你可以在浏览器里点击、输入、滚动、按键，同时暂停 agent 的输入；用完后交还控制权。agent 恢复元素操作前必须先获取一份新的快照。
- **文件**：列出、读取、写入该 Dot 工作区中的文本文件。路径必须相对于该工作区；这些文件不会自动加入 Spaces 页面。
- **终端**：在 shell 访问开启时，于该 Dot 的容器内执行一条受限命令。命令输出会显示出来；执行并不发生在 OpenDots 宿主机上。
- **活动（Activity）**：查看动作名称、发起者以及成功或失败状态。审计记录有意不包含键入的值、文件内容和完整命令。

停止会保留文件和浏览器 profile。应用不提供破坏性的重置操作。停掉 supervisor 并不会停掉它动态创建的那些电脑；若要让它们全部下线，请先逐个停止每个 Dot 的电脑。Compose 并不拥有这些动态创建的容器和卷，不要把删除命名的工作区/profile 卷当作日常清理手段。

撤销某项能力会取消应用当前活跃的请求，并阻止后续动作。取消无法撤销已经完成的副作用，而且被取消的请求对应的上游浏览器操作仍可能在之后完成。需要彻底结束容器内的所有活动时，请停止该电脑。Activity 为每个 Dot 保留最近 1,000 条已完成记录，外加尚未完成的请求。

模板使用标准的 Docker 容器隔离，容器共享宿主内核。shell 访问意味着容器内可以运行任意程序、访问网络，并能读取该 Dot 自己的浏览器 profile。请把这套东西部署在与这一信任级别相匹配的基础设施上。`COMPUTER_RUNTIME=runsc` 可以选用已安装的 gVisor 运行时；模板本身不会安装它，默认也不宣称提供更强的隔离。模板不会配置受限的网络出站策略。

## 验证与排障

创建两个 Dot，启用要测试的能力。在第一台电脑里写一个文件，然后确认第二个 Dot 无法列出它。停止再启动第一台电脑，确认文件仍然存在。还要测试：浏览器会话跨重启保留、接管与交还、权限关闭后的行为、暂停行为。并确认在服务不可用时，computer tools 会给出清晰的失败提示。

配置好了端点，并不等于 Docker 成功 provision 出了一台电脑。状态显示不可用可能意味着：Docker 守护进程没在运行、镜像没有构建、凭据不一致，或者应用访问不到返回的电脑地址。宿主机直接运行应用时用本地那套部署方式，容器化运行应用时用 app overlay。不要随手替换成任意返回的服务 URL，也不要把 computer API 直接暴露到公网。

源码版本与按 Dot 收窄的凭据补丁记录在 [deployment/computers](../deployment/computers/README.md) 中。master token 或镜像发生变更时，supervisor 会在这些电脑的下一次 ensure 请求时替换掉自己管理的容器，同时保留其 profile 和工作区卷。这一过程会中断正在进行的一切活动，请与进行中的工作协调好更新时机。

自动化测试使用受控的服务 fixture 来覆盖策略、请求和生命周期行为。真实的 Docker、模型、Slack 和语音检查，必须与这些测试分开记录。
