# 例行任务（Routines）

> 来源：https://github.com/elie222/rakazo/blob/main/docs/routines.md
> 原文：oss-repos/rakazo/routines.md
> 翻译日期：2026-11-03 ｜ 范围：全文 ｜ 方式：机器翻译初稿，未经人工校对
> 引用于：docs/essay-study/rakazo-2026.md、docs/brief-plan.md §3/§3.1
Routine 是 bot 自己跑的一段 prompt：按计划定时跑、在某个变化发生时跑，或者被别的服务调用时跑。

## 在聊天里直接要一个

最快的方式就是开口说：

- "每个工作日早上 8 点，汇总我的收件箱。"
- "20 分钟后提醒我给 Dana 打电话。"
- "每周一看看竞争对手的定价页，告诉我有什么变化。"

Bot 会创建这个 routine，并把每次运行的结果回报到同一个聊天里。

## 自己创建或编辑

点聊天顶部的 **Agent computer** 打开 bot 的计算机。屏幕下方是 bot 的 **Routines** 列表。选 **Create Routine**（**+**），或点某个 routine 进行编辑。

1. 给 routine 起个 **Name**，写好 **Instruction**：每次运行该做什么。
2. 在 **When to run** 下选 **Add trigger**。
3. 选 **Save**。

**Advanced** 下可以给 routine 单独指定 **Model** 和 **Thinking** 级别，比如简单的每日检查用便宜一点的模型。

## 触发器

### 定时

每小时、每天、工作日、每周、每月，或者自定义间隔。**Advanced...** 接受 cron 表达式。时间用你在 **Settings → General** 设置的时区。

### 有变化时

Bot 按固定间隔（**Check every**，5 分钟到一天）检查某样东西，只有它变了才运行。**What to watch** 可以是计算机上的文件或文件夹、某条命令的输出，或者某个已连接 app 的工具。想每次都留个记录，就打开 **Post "No changes" in chat**。监视不能和定时同时使用。

### Webhook

给你一个 URL 和 key。任何能发 POST 请求的服务都能启动这个 routine。

### Git 事件

给你一个 URL，可以加为 GitHub webhook，于是 push、issue 和 pull request 都能启动 routine。

### Slack 消息

Bot 在 Slack 收到消息时运行。需要先[连接 Slack](./messaging-apps.md)。

> [!NOTE]
> 由 webhook 或外部消息触发的运行遵循更严格的[审批](./approvals.md)规则，因为外部文本可能左右 bot 的行为。

## 测试、暂停与回顾

- **Test run** 立即运行已保存的 routine。
- 关掉 **Active** 可以暂停 routine 而不删除它。
- **Run history** 显示每次历史运行及其结果。
- 正在运行的 routine 在列表里显示 **Running**，并带 **Stop**。

## 在手机上

手机 app 从 bot 的 profile 列出它的 routines，可以在那里暂停、删除和查看。要新建或修改，请在聊天里吩咐 bot，或使用网页版 / 桌面 app。
