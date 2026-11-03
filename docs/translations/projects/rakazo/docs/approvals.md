# 审批（Approvals）

> 来源：https://github.com/elie222/rakazo/blob/main/docs/approvals.md
> 原文：oss-repos/rakazo/approvals.md
> 翻译日期：2026-11-03 ｜ 范围：全文 ｜ 方式：机器翻译初稿，未经人工校对
> 引用于：docs/essay-study/rakazo-2026.md、docs/brief-plan.md §3/§3.1
决定 bot 不先问你能做多少事。

## 选择模式

打开 **Settings → Approvals**，挑一个 **Mode**：

- **Ask**：任何会改变状态的动作（发邮件、编辑文档等）之前 bot 都要问。读取类操作通常不问。
- **Auto**：一个审批模型会把每个动作与你的要求对照。相符的直接执行；偏离任务的、或者不可撤销而你又没要求过的动作，bot 会问。
- **Never ask**：所有动作不等确认直接执行。

**Auto** 需要一个 **Approval model**，在 **Settings → Models** 设置。参见 [Models](./models.md)。

> [!TIP]
> 先从 **Ask** 或 **Auto** 开始。同一个动作你批准过几次之后，在卡片上选 **Always allow**，bot 就不再为它询问。

## 审批卡片

Bot 需要你点头时，会在聊天里发一张卡片，写明它想做什么：

- **Allow once**：仅此一次。
- **Always allow this tool**，或对某个网站 **Always allow**：以后不再问。
- **Deny**：bot 不做这件事，继续其他工作。

卡片从不阻塞聊天。你随时可以继续和 bot 对话，等方便了再答卡片。Bot 等你的时候会发通知（前提是 bot 设置里开了通知）。

## 允许与阻止列表

每个 **Always allow** 的选择都保存在 **Settings → Approvals**。任何条目都可以在 **Allow** 和 **Block** 之间切换，或者 **Remove**。被阻止的动作在任何模式下都不弹卡片，直接拒绝。**Preview** 可以在改动之前看某个工具会发生什么。

要禁止某个 bot 使用某个工具，打开该 bot 的设置，展开 **Advanced**，用 **Tools** 下的 **Disable a tool**。

## 哪些一定会问

在 **Auto** 和 **Ask** 下，以下动作总是弹卡片，**Always allow** 也不能跳过：

- 修改 bot 的 instructions 或 model，以及创建 space。
- 不是你写的文本可能在引导行为的动作，例如 webhook 启动的运行中的改动。
- 监视某条命令的 routine，或 routine 报告它在外部内容里发现的某个网站。

**Never ask** 会全部执行。唯一的例外是接受其他 owner 的 bot 连接：当运行由他人发起、或有外部内容进入运行时，它会拒绝。

## 按 space 定制

审批设置是账户默认值，每个 [space](./spaces.md) 都遵循。要给某个 space 不同的规则，打开它的设置，选 **Approvals** 旁的 **Customize**。
