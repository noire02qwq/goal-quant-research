# Rakazo 官网首页（Rakazo homepage）

> 来源：https://rakazo.com/
> 原文：https://rakazo.com/ （curl -sL 抓取成功，抓取日期 2026-11-03；原始 HTML 未入库存档）
> 翻译日期：2026-11-03 ｜ 范围：全文 ｜ 方式：机器翻译初稿，未经人工校对
> 引用于：docs/essay-study/rakazo-2026.md、docs/brief-plan.md §3/§3.1

> 说明：首页是营销页，含大量界面演示、滚动的用户评价和页脚链接。下文按页面区块顺序翻译；界面演示里的对话/卡片文字尽量译出，重复滚动两次的评价只收录一遍（原文为轮播重复），纯导航链接按原文保留。

## 页头

Rakazo ｜ 开源 Grok Bot 替代方案

导航：Docs、Integrations、Blog｜ ★ 6.8k｜ **Get started**

## 主视觉

**你真正拥有的开源 Grok Bot 替代方案**

给你的 bots 一份工作，从任何设备随时查看进度。

按钮：Get started、Download for iOS、Download for Android、Star on GitHub

界面演示（"用你的 agent 设置"）：

- 机器人列表（Bots +）：**Chief of Staff**（昨天：场地已订，合同已发出签署）、**Sales Outbound**（3:10 AM：完成，40 个客户已调研，18 份草稿排队）、**Inbox Manager**（12:11 AM：已发送，收件箱清零，5 份草稿待处理）、**Account Manager**（昨天：邀请已发给 sam，helix 备注已加）、**Talent Scout**（昨天：按你的口吻起草了 3 份引荐，暂扣待阅）、**Expense Manager**（昨天：报销已提交，9 张票据，无遗留）、**Bug Triage**（周一：6 个复现了 4 个，步骤已写进 issue）。
- 对话示例（Avery Kim 与 Inbox Manager）：用户说"周末收件箱失控了，清理一下？"；bot 回"收到。周五以来 41 封未读，先把噪音归档，剩下的起草。"屏幕显示 **Computer Done**，正在清扫 Gmail 到周五；结果：收件箱 5 份草稿待阅、读了 41 个会话、归档 26 封、回复 9 封、Nora 的续约暂扣。
- 用户指示"发 Nora 那封，其余的我明天看"；bot 回"已发送。收件箱清零，5 份草稿留给明天。"
- 计算机面板：**Take control**、**Routines**（Morning sweep 工作日 6 点；Reply Zero 每小时；+ New routine）。

## 你的机器人团队

**给每个 bot 一份工作**——从模板开始，再改成你自己的。

- **Sales Outbound**：调研潜在客户并起草跟进。
- **Inbox Manager**：整理邮件并起草回复。
- **Talent Scout**：审阅申请、筛出候选人。
- **Expense Manager**：把票据与付款对上。
- **Coding Agent**：在你的计算机上改代码。
- **Account Manager**：准备回复、跟踪续约。
- **Paid Media**：审阅广告花费并报告变化。
- **Chief of Staff**：准备简报并协调你的 bots。

## 在任何地方给它们发消息

在 Slack 里 @某个 bot，或用手机给它发短信。

Slack；iMessage & SMS（自托管）；WhatsApp（自托管）；Telegram（自托管）

示例（`# sales` 频道）：Avery Kim 9:41 问 "@Sales Outbound 今天谁需要跟进？"；Sales Outbound 9:41 答"本周有三个线索沉寂了。草稿已放在会话里。"

## 不止聊天

- **MCP，融入你的应用**：连接 Gmail、GitHub、Notion 和任何 MCP server。
- **看一遍就学会**：在它的计算机上演示一次任务，它会把步骤保存为 skill。
- **记得住**：bots 保留学到的东西并共享给团队（如"偏好简短回复"、"Acme 三月续约"）。
- **自己醒来**：按计划、webhook、GitHub 事件或它监视的变化启动（"工作日 9:00"、"新 GitHub issue"、"Webhook"）。
- **互相转交工作**：bots 之间互相委派，在群里协作。
- **它会给你打电话**：需要你介入时，bot 在 app 里打电话给你，当场把事情谈清楚。

## 用户怎么说

（原文轮播，此处各取一次）

- "用过 Grok Bot 之后来到这里……找到了这个替代品，可以确认你们做得太棒了。它完全替掉了 Grok Bot，手机 app 也非常流畅。"——@dilog1114
- "我是联合创始人兼 CTO，很喜欢 rakazo，我们用强 GPU 的私有 Qwen 3.8 跑它，全私有部署。"——@bc101101
- "我用它在 eBay 和其他所有市场找便宜的服务器和电脑配件，把所有它认为划算的都发给我。"——@michaelortnerit
- "Hermes 也不错但配置更复杂。Rakazo 的多智能体工作流更好，配置更简单。"——@notabot_92732
- "用 claude oauth 跑了一个月 rakazo，还没出过问题。"——@hey_cabron
- "今天用 expo 装好了手机 app，第一次用 expo，但 rakazo 带着我走完了，很容易。"——@mithril0x

## 自托管

**你的机器、你的模型、你说了算。**（View on GitHub、Read the docs）

- **你的模型**：给每个 bot 选不同的模型（示例：Claude Sonnet 5.5、GPT-6.1 Sol）。
- **按计划工作**：你的电脑关机时它也在继续干活（"工作日 9:00"）。
- **需要审批**：由你决定哪些动作要先经过你（Approve / Deny）。

兼容：Claude、ChatGPT、OpenRouter、Grok、Ollama、LM Studio。

## 无处不在

- **Web**：Get started
- **Desktop**：macOS、Windows、Linux
- **Mobile**：iOS、Android

（页面另附手机界面演示：Inbox Manager 的会话摘要与操作清单，内容同上。）

## 开源

Apache-2.0。跑起来、改代码、变成你自己的。

Star on GitHub｜elie222/rakazo ★ 6.8k

最近的 GitHub 动态（节选）：

- Answer other people in Slack without the owner's memory and notes #3158（Nov 3）
- Stop SSO links from keeping someone in another person's account #3156（Nov 3）
- Answer app and direct-line messages first, and every mid-task message at once #3107（Nov 3）
- Forward only the headers noVNC needs to the computer screen #3153（Nov 3）
- Let bots choose between connected accounts of the same app #3141（Nov 3）

## 常见问题（FAQ）

**能用我的 Claude Pro/Max 或 ChatGPT Plus/Pro 订阅吗？**
可以——用该订阅登录，或者用 API key / OpenRouter / 本地 OpenAI 兼容服务器（Ollama、LM Studio 等）。Rakazo 不承担模型费用。

**我已经付了 Claude 或 ChatGPT 的钱，还需要 API key 吗？**
不需要。用 Claude Pro/Max 或 ChatGPT Plus/Pro 登录，订阅就覆盖了模型开销。另一条路是 API key，支持 Anthropic、OpenAI、OpenRouter 或 Grok。两种方式下 Rakazo 都不付费。

**能跑本地模型吗？**
可以。把 bot 指向本地 OpenAI 兼容服务器，比如 Ollama 或 LM Studio。每个 bot 可以用不同的模型。

**托管套餐包含什么？**
每月最多 100 个计算机小时，同时可跑 5 台计算机。对绝大多数人来说绰绰有余，而且不产生超额费用。

## 认识你的第一个 bot

把下一项任务交出去。

按钮：Get started、Download for iOS、Download for Android、Download for macOS、Download for Windows、Download for Linux、View on GitHub

数据：6.8k GitHub stars｜Apache-2.0 许可｜开源，全部功能免费｜自托管，跑在你的机器上

## 页脚

语言：English、Deutsch、한국어、简体中文、日本語、Español、Français、Português (Brasil)、Nederlands、Русский、Türkçe、עברית、हिन्दी、繁體中文

© 2026 Inbox Zero Inc. Apache-2.0

- **Product**：iPhone app、Android app、Docs、Submit a plugin、Changelog、GitHub
- **Alternatives**：Grok Bot、Muse、Dots、Instinct、Hermes、Claude Duet、Hark、OpenClaw、All
- **Company**：Blog、About、Brand、Support、Privacy、Terms
