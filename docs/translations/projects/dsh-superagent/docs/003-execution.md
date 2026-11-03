# 003 执行（003 Execution）

> 来源：https://github.com/deepseek-ai/dsh-superagent-prototype/blob/main/docs/003-execution.md
> 原文：oss-repos/dsh-superagent-prototype/docs/003-execution.md
> 翻译日期：2026-11-03 ｜ 范围：全文 ｜ 方式：机器翻译初稿，未经人工校对
> 引用于：docs/essay-study/deepseek-super-agent-2026.md

本文跟踪一个已接单的 Ticket，看它如何执行、投递与恢复。它承接[001 领域模型](001-domain.md)和[002 授权](002-authorization.md)。

## 目录

- [Ticket 阶段](#ticket-stages)
- [执行器](#the-executor)
  - [后台任务与 worker 槽位](#background-work-and-worker-slots)
  - [准备 Ticket 目录](#preparing-a-ticket-directory)
  - [并发](#concurrency)
  - [执行变量](#execution-variables)
- [合并](#merging)
- [Ticket 如何结束](#how-a-ticket-ends)
  - [Pull request](#pull-requests)
  - [Follow-up 与上下文 Thread](#follow-ups-and-context-threads)
- [故障与恢复](#failure-and-recovery)
  - [执行器受阻或失败](#executor-blocked-or-failed)
  - [重试](#retry)
  - [重启](#restart)
  - [持久化的待办工作](#stored-work)
  - [Source 故障](#source-failure)
  - [Channel 故障](#channel-failure)
  - [暂停处理](#pause-processing)
  - [配置无效](#invalid-configuration)

<a id="ticket-stages"></a>

## Ticket 阶段

每个 open 的 Ticket 只有一个阶段，由它在等什么决定。表格从上往下读，先匹配到的行生效。

| 阶段 | 条件 | 面板标签 |
| --- | --- | --- |
| person / delivery | 向执行器 Session 投递 Input 失败；2 秒后重试，之后按翻倍的延迟重试、最长到一分钟；一次成功、一次新的 Assignment 或 Ticket 结束都会清掉它 | Input 未投递 |
| person / answer | 它有一个待人工决定的问题 | 等待回答 |
| person / review | 最新的 Report 是 `ready` | 等待 review |
| person / blocked, failed | 最新的 Report 是 `blocked` 或 `failed`，此后没有人的消息抵达该 Ticket | 受阻 · 失败 |
| working / queued | 没有 Assignment，或有一个 pending 的 | 排队中 |
| idle | 最新的 Report 是 `waiting`，或 Assignment 已结束 | 等待 Trigger |
| working | 其余一切 | 工作中 |

`person` 阶段意味着没有人的输入，Ticket 就无法继续。一条新的人发的消息会把 `blocked` 或 `failed` 的 Ticket 交还给它的 Executor，于是它进入下一个匹配的阶段，通常是 `working`。

`idle` 的 Ticket 已经结束本轮，且没有悬而未决的问题。订阅 Thread 上的一条 Trigger 可以让它继续。

<a id="the-executor"></a>

## 执行器

每个 Ticket 会得到一个名为 `worker-<ticket id>` 的执行器 Session，以及一个以 Ticket 短名命名的目录。目录建在配置的执行根目录下，默认是 `<stateDir>/work`。

执行器 Session 以操作者的 OS 用户身份运行命令，无需批准。它们的 `dsh-superagent-worker` 预设包含工作所需的工具，并会在 5 秒后把前台 shell 命令转成后台任务。这样 worker 在下一步就能收到新消息，而不必等一条长命令跑完。

主 Session 使用 `dsh-superagent-router`，同样有 5 秒的 shell 与任务等待上限，工具集更小，专用于路由。Session 保留创建时选定的预设。worker 的 subagent 使用 DeepSeek Harness 的 `standard` 预设。

<a id="background-work-and-worker-slots"></a>

### 后台任务与 worker 槽位

当一轮结束时还有 shell 任务或 subagent 在跑，Ticket 会保留它的 worker 槽位并保持工作状态。它不会被报告为等待，主 Session 也收不到等待报告。任务或 subagent 完成后，会带着结果在同一个槽位里唤醒 Executor。一旦某轮结束时已无后台工作，Executor 就正常报告等待。

每轮之后，后台工作最多有 30 分钟完成。到限后 shell 任务被杀掉，Ticket 被报告为等待。报告里会带上 Executor 最后说的话，以及哪些任务被杀、哪些 subagent 仍在活跃。subagent 允许继续。Executor 在下一轮读取被杀任务的结果。

移交给人会立刻释放槽位，Report 继续生效。这适用于 `ready` 报告或问题之后（除非此后又来了新的 Input），也适用于任何 `blocked` 或 `failed` 报告之后。

移交时 subagent 会停止。shell 任务（例如一个供 review 的服务器）可以继续，直到 Assignment 结束。它们不占槽位，也不受 30 分钟上限约束，包括后续各轮之后也一样。它们的完成不会唤醒 Executor；Executor 在下一轮读取结果。

人也可以直接在执行器 Session 里写东西来开启一轮。它的后台工作遵循同样的规则。

Assignment 结束时，它的 shell 任务会在不唤醒 Session 的情况下被杀掉。它的 subagent 被释放，subagent 唤醒的任何完成轮都会被丢弃。替换它的 Assignment 和等待中的 Input，要等这次关闭完成后才开始。

在 DeepSeek Harness 进程内停止或重启插件，走的是同一条关闭路径。尚未进入 Session 历史的 Input 会被保留。关闭最多等每个 worker 的后台工作 10 秒；进程重启则直接结束这些工作。一个在忙碌中被打断的 Assignment，会带着一条恢复说明重新开始。

worker 的 subagent（含嵌套的）使用 DeepSeek Harness 的 `standard` 预设，权限与 worker 相同。它们只保留 worker 获准使用的工作类工具，Ticket 结束时连这些工具也一并失去。在 `standard` 下，一条 shell 命令 60 秒后转入后台。subagent 结束时，它的任务会被杀掉。

<a id="preparing-a-ticket-directory"></a>

### 准备 Ticket 目录

第一个 Assignment 之前，如果 Ticket 目录不存在，prepare 命令会在执行根目录下用 `sh` 跑一次，限时十分钟完成。没有 prepare 命令时，worker 就在一个空目录里开始。

命令失败会让 Ticket 失败，并记录它的输出。一次重试、或人在该 Ticket 某个 Thread 上发的消息，都会再试一次准备。典型的命令用 `git worktree` 创建一份检出。当某个 pull request 的分支最后一段与 Ticket 的短名一致时，它就属于这个 Ticket。

<a id="concurrency"></a>

### 并发

Ticket 从一次启动（含准备）开始、或从唤醒它闲置 Executor 的那次投递开始，就占用一个 worker 槽位。在活跃的一整轮期间它也占着槽位。

配置的并发上限作用于这些槽位，另外为人发的消息或状态查询留一个额外槽位。正常槽位占满时，这样的唤醒可以用那个额外槽位，并在新启动之前拿到下一个空闲槽位。因此，新工作不会挡住人继续一个既有的 Ticket。

其他 Input（例如 CI 结果）等待普通槽位。一次启动会在 `working / queued` 等到有空位。启动之间是并发执行的，所以一条慢的 prepare 命令只会拖慢它自己那个 Ticket。

<a id="execution-variables"></a>

### 执行变量

prepare 命令和 Executor 的指示收到同一套执行变量。命令读环境变量；Executor 在它的 prompt 里读这些变量的值和描述。其中不含任何凭据。

| 变量 | 注册者 | 值 |
| --- | --- | --- |
| `DSH_SUPERAGENT_DIR`、`DSH_SUPERAGENT_NAME`、`DSH_SUPERAGENT_TICKET` | Executor | Ticket 的目录、短名和 id |
| `DSH_SUPERAGENT_BLOCKED_COMMANDS` | Executor | Executor 不得运行的命令 |
| `DSH_SUPERAGENT_GITHUB_REPOSITORY` | GitHub | Source 监视的仓库，`owner/name` |
| `DSH_SUPERAGENT_GITHUB_ACCOUNT`、`DSH_SUPERAGENT_GITHUB_COMMIT_EMAIL` | GitHub | agent 账号及其提交邮箱 |
| `DSH_SUPERAGENT_GITHUB_NUMBER`、`DSH_SUPERAGENT_GITHUB_PR_HEAD` | GitHub | 触发该 Ticket 的 Issue 或 pull request，以及它是 pull request 时的 head ref |
| `DSH_SUPERAGENT_FEISHU_BOT`、`DSH_SUPERAGENT_FEISHU_CHAT` | 飞书 | bot，以及触发该 Ticket 的群聊 |

与 Ticket 相关的取值来自它的目录和最初的 Trigger，其余取值来自当前部署设置。只有面板能改执行环境设置；发给主 Session 的文本改不了已配置的 shell 命令。

worker 通过 agent 账号的 `gh` 访问 GitHub，通过 bot 的 `lark-cli` 访问飞书。被禁的命令按名字调用时会失败。

这些包装器和目录确立的是默认值，不是安全边界。worker 仍可以用绝对路径执行程序。

<a id="merging"></a>

## 合并

自动合并由 **Delivery requirements** 这段 prompt 约束。宿主没有针对合并的决定逻辑。

默认情况下，Executor 永远不会以 agent 账号开启 auto-merge：GitHub 会把合并记在开启它的人头上。交付要求必须指名另一个账号的 CLI 来执行合并。没有指名的话，就由人来合并 pull request。

默认指示只允许对为该 Ticket 开的 pull request 开启 auto-merge，且要求它已就绪、必需的批准覆盖了 head commit、新增加删除合计少于 200 行。在推送另一个修订之前，Executor 会撤掉 auto-merge。

没有正文的 review（例如批准）同样以 Trigger 的形式抵达，可以唤醒一个等待 review 的 Executor。这些指示约束的是 agent，而不是 GitHub 的合并规则。要强制批准，就在分支保护里要求批准并忽略过期的批准。省略合并 CLI、或删掉 auto-merge 那一段，就可以要求手动合并。

<a id="how-a-ticket-ends"></a>

## Ticket 如何结束

- **就绪但没有 pull request：**`ready` 报告把 Ticket 以完成结束。
- **无事可做：**Executor 发现没有需要人出手的工作（例如请求无法复现、或已被取代），会报告 `dropped`。Ticket 在不发消息的情况下结束，除非命中的规则要求发消息；人后来在它的 Thread 上发消息可以恢复它。

<a id="pull-requests"></a>

### Pull request

一旦它的 Executor 报告了那个 pull request，Ticket 就跟踪它开出来的那个 pull request。它也跟踪从自己分支开出的每个 pull request——由 Executor 报告、或由 GitHub Source 发现。被重新打开的 pull request 会再次被跟踪。

当它开的 pull request 全都不再处于 open 时，Ticket 就完成了。如果它一个也没开，那么它跟踪的所有 pull request 都必须已关闭。随后它以最后一次相关关闭的结果结束，并保留它的 Subscription，好让后来的人类评论能恢复它。

只要恢复的、重试的、恢复处理的工作还没做完，关闭并不会结束 Ticket。如果 Executor 确认或回答了它所拥有的 follow-up，却在读了那条消息之后既没有给出非 progress 的 Report、也没有结束一轮，Ticket 也会等。之后的一份 `ready` 报告，一旦满足同样的 pull request 完成规则，就结束 Ticket。

聊天 Channel 会收到一条关于 pull request 结果的最终通知。GitHub 本身已经在 pull request 上展示了结果。去掉 Ticket 对某个 pull request 的 Subscription，也会停止跟踪它。

因此，"等待 review"指的是一份带着 pull request 的 `ready` 报告。

<a id="follow-ups-and-context-threads"></a>

### Follow-up 与上下文 Thread

Executor 决定其 Ticket 自己 Thread 上的人类 follow-up。它处理范围内的请求，把超出范围或属于另一个 Ticket 的请求交还回去。一旦没有 Executor 拥有这条消息，它就成为主 Session 的候选。主 Session 对这条 follow-up 除此之外只能应人的要求停止工作。

一个 Input 在 Session 把它纳入某一步、随后报告或结束一轮之后，才算已读。Ticket 结束时，未读且未被确认、未被回答、也未被交还的消息回到 Eval，见[002 授权](002-authorization.md)。已读但没采取行动的消息（例如道谢）不会回去。

仅为上下文而跟进的 Thread 仍会投递消息，但不把人类 follow-up 的所有权交给 Ticket，也不恢复已结束的 Ticket。那些消息可以被独立研判。

只要在办 Ticket 订阅着，Source 就轮询订阅的 Thread；并且在最后一个 Trigger 与订阅 Ticket 的结束两者中较晚的那个之后，再轮询两周。此后，消息只通过常规入口进来：GitHub 通知或飞书实时事件。

<a id="failure-and-recovery"></a>

## 故障与恢复

<a id="executor-blocked-or-failed"></a>

### 执行器受阻或失败

当执行器 Session 报告 `blocked` 或 `failed`，或者启动失败、出错（这会记为 `failed`）时，Ticket 不再自动接收 Input。

模型服务商或网络的偶发失败（HTTP 408、429、5xx，或被拒绝、被重置、超时的连接）会先重试三次，退避时间逐次拉长：启动会再跑一次，轮次失败的 worker 会被告知继续；失败的 prepare 命令不会重试。

一旦失败，CI 和 bot 的消息会记录在它上面，但不投递，也不唤醒 Session。

它的工具保持可用，所以人可以直接在 Session 里继续。

一次失败的启动不会自动重试。

一条人发的消息、一份既非 `blocked` 也非 `failed` 的后续 Report、或者一次重试，都能解除这种扣留。

这个状态是从存储的 Report 和 Input 推出来的，所以重启后仍在。

<a id="retry"></a>

### 重试

open 的 Ticket 处于 `person / delivery`、`person / blocked` 或 `person / failed` 时可用：一次新的 Assignment（会重新启动它的 worker 并取走等待中的 Input）就是这些问题各自的解法。

只要人发的消息已经抵达一个受阻或失败的 Ticket，Executor 就有了这条消息，于是 Ticket 显示为工作中（失败的启动重新开始时显示为排队中），不再提供重试——除非那条消息投递失败。

一次重试会结束当前 Assignment，并在同一个执行器 Session、目录、分支和 pull request 里开一个新的。

执行器模型只在创建 Session 时生效；已有的 Session 保留自己的模型。

<a id="restart"></a>

### 重启

正在运行的 Assignment 以"宿主已重启"结束，新的 Assignment 带着一条恢复说明开始，告诉 Executor 在重复任何外部动作之前先检查它的目录、git 历史和 GitHub，并且从最老的 Ticket 开始。

处于等待、就绪、受阻或失败的 Assignment 保持原样，除非那份 Report 之后又有 Input 到达——那种情况下它们也会重新开始。

Session、目录、Subscription、挂起的消息，以及下面这些存下来的工作，都能挺过重启；同样挺得过的还有"每个执行器 Session 把哪些消息纳入了它的历史"的记录——某一步在认领了这些消息之后、调用模型之前会记一次：被重启截断的那一轮所取走的消息，只要之后来了 Report 或一轮结束，就算已读；而某一步认领了、却在进入历史之前被取消或错误截断的消息，算未读。

一次重试或重启，会把被它替换的那个 Assignment 收到过、而它的执行器 Session 没有取走的消息，再交给新 Assignment 一次——这些消息可能被一次取消或被截断的那一步丢掉了；如果 Session 里还留着一份副本（由重启保留、或在崩溃中持久化），它会在新 Assignment 的第一条消息之前被取走，于是新投递的这份就是唯一副本。

<a id="stored-work"></a>

### 持久化的待办工作

dsh-superagent 在一次决定之后要做的事——例如把候选、follow-up 或报告转发给主 Session、启动一个 Assignment、投递一个 Input——都是先存下来，再执行。

转发或投递失败（例如 Session 联系不上）时，2 秒后重试，之后按翻倍的延迟重试、最长到一分钟；一次失败的启动会让它的 Ticket 失败，除非那是一次偶发失败，如上所述。

每类工作只有在某一项连续失败三次之后，才在总览的"系统问题"里报错；投递失败的 Input 显示在它自己的 Ticket 上。

转发给主 Session 的消息保持顺序，通知也一样；某一条失败会压住同类中在它之后的消息。

<a id="source-failure"></a>

### Source 故障

GitHub Source 自己逐个读取每个 Issue、pull request 和 Thread：一次读取失败，错误就留在它的 Thread 上，下次轮询时再读一次，并计入 Source 的一次错误——默认连续三次轮询失败后它就报告；任何一次成功的轮询都会把计数清零。

当 agent 失去对私有仓库的访问时，GitHub 同样返回 404，所以 404 会被重试。

一个已收到通知的 Issue 或 pull request，如果读取一直失败，会在首次读取失败一天后被丢弃；GitHub 报告它已删除时则立刻丢弃。此后它不再导致轮询失败，它的 Thread 保留错误，Source 的状态里会点它的名。

它的读取位置保持原地，于是后来的通知或对它 Thread 的轮询，会读到那些失败的读取漏掉的内容。

飞书事件消费者会报告每一次失败，订阅话题的轮询则把每次失败留在它的 Thread 上。

GitHub 列表或飞书分页里格式不对的条目会被跳过，Source 的状态会把它计数。

<a id="channel-failure"></a>

### Channel 故障

外发消息作为持久化的待办工作存储并发送，按指数退避重试，从 5 秒起翻倍，最长 300 秒。

一个 Ticket 发往同一会话的消息按入队顺序发出，所以它的确认会排在它后来的回答或结果之前：同一个 Ticket 发往同一会话的前一条消息还没发出时，后一条就等着，直到那条连续失败三次并显示为一个问题为止。

其他 Ticket 的消息、以及不属于任何 Ticket 的消息，不等它。

一条尝试过失败的消息，在发出或被撤回之前一直算一个系统问题。

只有它的 Source 不再监听该会话、或 Source 回答该会话永远收不到它时，消息才会被丢弃；Source 关闭期间它一直等待。

GitHub 上已删除的 Issue 或已锁定的会话、飞书上被撤回的消息或飞书再也找不到的消息，Source 会给出这种回答。

回复一条已不存在的 review 评论时，改发到该 pull request 的会话里。

被丢弃的消息保留它的记录，包括何时、为何被丢弃，以及它是为哪个 Ticket 发的，所以它永不再入队；被丢弃的确认显示为已丢弃，而不是已发送。

<a id="pause-processing"></a>

### 暂停处理

暂停会停掉派发、新的 Eval、Eval 超时、Input 投递和回复；已经在进行的一次启动会等到处理恢复。

Source 继续记录 Trigger，正在跑的 Executor 轮次不会被打断。

人发给已结束 Ticket 的消息会等待：暂停之后的第一轮处理会恢复该 Ticket，前提是它的 Mandate 在当时的 Policy 下仍然成立。

进行中的 Eval 在暂停期间不会过期；它的截止时间按暂停的时长相应后移。

<a id="invalid-configuration"></a>

### 配置无效

存储下来的 Source 配置如果被它的 kind 拒绝，该 Source 实例会被禁用。
