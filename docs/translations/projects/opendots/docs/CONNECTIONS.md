# 连接（Connections）

> 来源：https://github.com/CopilotKit/OpenDots/blob/main/docs/CONNECTIONS.md
> 原文：oss-repos/OpenDots/docs/CONNECTIONS.md
> 翻译日期：2026-11-03 ｜ 范围：全文 ｜ 方式：机器翻译初稿，未经人工校对
> 引用于：docs/essay-study/opendots-2026.md、docs/brief-plan.md §3/§3.1

Connections 让 Dot 获得远程 [MCP](https://modelcontextprotocol.io) 服务器提供的工具：邮件、日历、问题跟踪器、笔记，或者你自己的服务。每个 connection 归属且仅归属一个 Dot。

## 添加 connection

1. 打开某个 Dot 的设置（**Edit specialist**）。
2. 在 **Connections** 一栏填写名称、服务器的 Streamable HTTP 端点（例如 `https://example.com/mcp`），以及可选的 bearer token。
3. 点击 **Connect**。OpenDots 会列出该服务器的工具并保存下来。

服务器新增或修改工具后，点击 **Refresh** 重新拉取；你对已有工具所做的选择会被保留。

## 审批（Approvals）

每个工具默认处于启用状态。被服务器标记为只读的工具（`readOnlyHint`）可以直接自行运行，其余工具默认开启 **Ask first**。

当 Dot 调用一个 **Ask first** 工具时，该工具不会真正执行。服务器会原样保存这次调用所对应的 connection、工具名和参数，Dot 则在聊天中弹出一张审批卡，附带摘要和这些已保存的参数。只有当你点击 **Approve & run**，动作才会通过一条仅限 owner 使用的服务器路由执行。该路由执行的是当初保存的请求，而不是审批时随附的任何参数；而且只有当当前会话里的 Dot 仍然启用着同一个工具时才会执行。请求在一小时后过期，每次审批至多执行一次。重新打开会话时，会显示已保存的结果；若动作仍在运行，则会继续轮询等待。已保存的结果只会出现在产生它的那次审批中。

只读提示来自服务器，因此只是一种提示。对任何不完全信任的工具都建议打开 **Ask first**，并关闭 Dot 用不到的工具。

审批卡只出现在 Web 应用中。通过 Slack 或在定时运行里触发时，**Ask first** 工具会让 Dot 提示你回到 Web 应用中继续操作。

修改某个 Dot 的 connection 或工具设置，会中止该 Dot 当前正在进行的轮次。

## 安全说明

- token 保存在服务器的 SQLite 数据库里，绝不会发送到浏览器。请像保护 `.env` 一样保护 `DATABASE_PATH`。
- 工具结果会作为不可信数据传给模型。
- 端点必须使用 `http` 或 `https`，且 URL 中不能携带凭据。允许使用本地地址，因此你可以在同一台机器上运行 MCP 服务器。只添加你信任的服务器。
- 目前尚不支持仅使用 OAuth 的服务器。请选用接受 bearer token 的服务器，或在其前面架设一个带 token 认证的代理。
