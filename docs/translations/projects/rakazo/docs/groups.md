# 群组与团队协作（Groups and teamwork）

> 来源：https://github.com/elie222/rakazo/blob/main/docs/groups.md
> 原文：oss-repos/rakazo/docs/groups.md
> 翻译日期：2026-11-03 ｜ 范围：全文 ｜ 方式：机器翻译初稿，未经人工校对
> 引用于：docs/essay-study/rakazo-2026.md、docs/brief-plan.md §3/§3.1

一项工作需要不止一个帮手时，可以把几个 bot 放进同一个聊天，或者让它们互相转交任务。

## 发起群聊

选 **Create**（侧边栏顶部的 **+**），再选 **New group chat**。给群组起名，挑 2 到 10 个 bot，然后点 **Create group**。

每个 bot 保留自己的 memory、computer 和 instructions；群组只共享对话。

## 谁来回答

- 不 @任何人时，群里排第一的 bot 回答，并可以把其他 bot 拉进来。
- **@Name** 会唤醒那个 bot。同时 @ 多个可以全部唤醒。
- **@everyone** 唤醒群里所有 bot。

要重命名群组或调整成员，从群组头部打开 **Group settings**。**Delete group** 删除这个群聊。

## bot 之间互相提问

一个 bot 可以直接给你名下的另一个 bot 发消息，比如向你的 research bot 提问。聊天里会显示 **Messaged** 或 **Message from** 加上对方 bot 的名字。点开可以读往来内容，但只能看，不能改。

bot 决定该问谁，依据是各自设置里 **Advanced** 下 **How other bots see it** 的描述。写一行说明这个 bot 是干什么的就够了。

默认情况下 bot 只和同一个 [space](./spaces.md) 里的 bot 说话。在 bot 设置的 **Permissions** 下打开 **Allow cross-space bot communication**，它才能联系到你其他 space 里的 bot。

## 子智能体（Subagents）

遇到大任务，bot 可以分出短期帮手并行处理并回报结果。每个帮手在聊天里显示为一张卡片，标着 **Running**、**Completed** 或 **Failed**。Subagent 随任务结束而消失，没有自己的聊天和记忆。

## 会造 bot 的 bot

bot 可以创建新 bot；打开 **Manage other bots** 之后，它还能整理和配置你名下的 bot。参见[管理 bot 的 bot](./fleet-management.md)。
