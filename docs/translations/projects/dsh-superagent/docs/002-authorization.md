# 002 授权（002 Authorization）

> 来源：https://github.com/deepseek-ai/dsh-superagent-prototype/blob/main/docs/002-authorization.md
> 原文：oss-repos/dsh-superagent-prototype/docs/002-authorization.md
> 翻译日期：2026-11-03 ｜ 范围：全文 ｜ 方式：机器翻译初稿，未经人工校对
> 引用于：docs/essay-study/deepseek-super-agent-2026.md

授权决定谁可以开工，以及这项工作可以包含什么。本文承接[001 领域模型](001-domain.md)。

宿主负责执行允许名单、规则和 Mandate。消息、评论和被引用的文档都是一次决定的输入，改变不了这些权限。

## Trigger 的两条路径

### Eval：判断是否开工

Source 会记录一条消息是否在对 agent 说话：`mention` 表示 @ 了 bot 或 agent 账号，`direct` 表示私聊。准入这一步检查发送者和该 Source 的 Policy：

- 名单上的人对 agent 说话，构成一次 explicit 请求。
- 人在已有 Ticket 的 Thread 上跟进，遵循下述规则。
- 其他人类消息，按其接收范围查准入表。
- Source bot 名单上的 bot 可以产生一个 inferred 候选，但永远不能构成 explicit 请求。其他 bot 不被准入。

### Subscription：延续既有的工作

订阅 Thread 上的每条消息都会以上下文的形式抵达它所订阅的 Ticket，包括 bot 和 CI 的消息。这条投递绕过准入检查，也不授予任何新的权威。每个 Ticket 仍然受它自己的 Mandate 限制。

Ticket 自己的 Thread 上由人发的消息，归该 Ticket 的 Executor 判断。主 Session 把消息挂到某个 Ticket 上时也一样。只要消息归某个 Executor 所有，它就不经过 Eval，也得不到 Decision。每个 Executor 要么在自己 Ticket 的范围内处理这个请求，要么把它交还回去，另行路由。

只要 Ticket 还活着，这种归属就继续有效，哪怕人撤掉了它的 Subscription。它也覆盖那种没有被人 stop、却带着等待恢复的消息的已结束 Ticket。

主 Session 会收到一条跟进通知。在 Executor 拥有这条消息期间，主 Session 只能应人的要求停止工作；accept、attach、ignore 和重新入队都会被拒绝。stop 本身仍要经过准入检查，用的是下文所说的跟进强度。

### 交还与释放 follow-up

当 Executor需要的工作超出 Ticket 的范围，或这条消息属于另一个 Ticket 时，它把消息交还一次。Ticket 保留它的 Subscription。如果被挂上的 Thread 与它无关，Executor 把自己在那里的消息交还回去。

一条消息只有在没有任何 Ticket 还拥有它时，才会进入一次新的 Eval。它的候选会带上各 Executor 给出的理由。准入把它当作该 Thread 上的一条普通消息来判断，主 Session 可以 accept、把它挂到别处，或者 ignore。交还一条本不属于该 Ticket 的消息（例如 bot 的消息，或人已经送去 Eval 的消息），不会入队任何东西。

Ticket 结束时，会释放它的 Executor 没有读取、也没有接手的 follow-up。这包括从未投递给 Executor 的消息，以及在它的最后一份 Report 或一轮结束之后才投递的消息——前提是它既没有确认、没有回答，也没有交还。每条被释放的消息，在没有别的 Ticket 拥有它时进入 Eval。一次 stop 只结束被 stop 的那个 Ticket 的工作。

被 stop 的 Ticket 不会把它的 stop 消息再次送进 Eval，除非另一个 Ticket 把它交还了回来。当初 stop 它的主 Session，可以把这条消息的其余部分作为新工作接单。

人可以从面板把一条已被拥有的 follow-up 送去 Eval。如果主 Session 随后把它挂回一个存活的 Ticket，Executor 会再次收到它。当没有任何有效的判断覆盖这条消息时，面板也提供"重新评估"。

### 仅供上下文的 Subscription

Executor 可以为了上下文跟进一个相关的 Thread，比如另一个 Issue 或 pull request。那些消息会抵达 Ticket，但不授予任何权威，也不带来跟进强度。那里的人发的消息不会恢复已结束的 Ticket，除非主 Session 挂上了来自那个 Thread 的消息。主 Session 关于其他工作的备注也只是上下文。

到不了任何 Ticket 的人发的消息（包括 Ticket 被人 stop 过的那些 Thread 上的消息），都走 Eval 这条路。bot 的消息走不走这条路，与它是否投递给了订阅 Ticket 无关。

## 强度（Strength）

| 强度 | 情形 |
| --- | --- |
| explicit | 名单上的人对 agent 说话，或在已有 Ticket 的 Thread 上跟进；准入表中某一格设为 explicit 请求 |
| inferred | 不在名单上的人在有 Ticket 的 Thread 上跟进，除非他那一格设为 explicit；准入表中某一格设为 inferred 候选；Source bot 名单上的 bot 对 agent 说话，或把消息发到 Source 接收全部消息的范围 |
| not admitted | 其他 bot 的消息、准入表忽略的一切，以及 accept 模式为 `off` 时的所有 inferred 情形 |

对于不在名单上的人，即便在有 Ticket 的 Thread 上，explicit 的准入格也优先，并且在任何 accept 模式下都生效。否则他的跟进就是 inferred，在 `off` 模式下不被准入。仅为上下文而跟进的 Thread 上的消息，用准入表判断，而不是跟进强度。

## 准入（Admission）

每个 Source 的 Policy 都有一张准入表。它的行是接收范围：

- **飞书：**每个配置过的群聊、bot 收到过 @ 的其他群聊，以及私聊。其他群聊只有在飞书卡片上把 **其他群** 设为 **仅 @** 时才会被接收。
- **GitHub：**新的 Issue、新的 pull request、评论，以及默认分支的 CI。

一行最多有三格。每一格决定一条消息是变成 explicit 请求、inferred 候选，还是什么都不是：

| 格 | 可选值 | 默认 |
| --- | --- | --- |
| 在名单上、没有对 agent 说话 | inferred、ignore | inferred |
| 不在名单上、对 agent 说话 | explicit、inferred、ignore | ignore |
| 不在名单上、没有对 agent 说话 | inferred、ignore | ignore |

针对"没对 agent 说话"的格，只有 Source 接收全部消息的范围才有，例如飞书群聊设为 **全部消息**，或 GitHub 范围打开了接收全部的开关。CI 结果没有发送者，所以它的行只有最后一格。bot 的消息用 bot 名单，不用这些格。

把"不在名单上且对 agent 说话"这一格设成 explicit，该范围内任何人都可以 @ agent 来派活。这对专门的答疑群可能有用。inferred 候选仍然取决于 accept 模式。跟进通常绕过这张表，例外是 explicit 的格仍然授予 explicit 强度。

准入表是 Policy 版本的一部分。放宽某一格，不会立刻停止在它之下接单的在办 Ticket；但这些 Ticket 在恢复前重新校验时，可能会被撤销 Mandate。

### bot 与自动化 reviewer

宿主把 GitHub App、以 `[bot]` 结尾的登录名，以及飞书 bot 都认作 bot。Source 可以列出 `dependabot[bot]` 这样的 bot，它们的消息可以变成 inferred 候选。它们必须要么对 agent 说话，要么发在接收全部消息的范围里。它们不能提出 explicit 请求，也不能 stop Ticket。

使用普通账号的自动化 reviewer，在宿主看来算作人。它的评论会抵达订阅的 Ticket，并产生跟进通知。团队的 prompt 文本必须把这类账号标明为自动化 reviewer。

## 候选的路由

主 Session 用 `orchestrator_route` 路由 explicit 候选。一次调用可以包含多条 accept、attach、stop 或 ignore 决定。每一项独立处理：某一项被拒绝或缺少字段，不影响其余各项执行。

inferred 候选通常需要一次完整的研判。只有一条捷径：如果它的卡片明显不触及任何启用的规则（例如纯闲聊或无关的讨论），主 Session 可以直接 ignore。Decision 会记录 `ignoredFromCard`，以区别于按规则研判的结果。主 Session 从它的 Policy prompt 段落中读取启用的规则。

接单一个 inferred 候选永远需要一次研判。直接 accept 会拒绝一个准入未把它判为 explicit 的 Trigger。

## accept 模式与规则

accept 模式是 Policy 的一部分：

| 模式 | 效果 |
| --- | --- |
| `off` | 任何 inferred 的东西都不成为候选，例如没对 agent 说话的消息、bot 的消息、不在名单上的人的跟进 |
| `observe`（默认） | 研判 inferred 候选；研判为正的记为一条标注"would accept"的 ignore，不接任何单 |
| `auto` | inferred 候选研判为正即接单 |

explicit 请求在任何模式下都工作。先从 `observe` 开始，审阅记录下来的 Decision 之后再切到 `auto`。每一次研判都对每条启用的规则各判一次，不论是否命中。主动接单至少需要命中一条规则。

每条规则描述一类主动工作。Ticket 的 Mandate 记录命中的规则，它的 Executor 会收到这些规则的名字和指示。

对那个 Ticket 而言，某条规则在流程和沟通上的要求会覆盖默认值。一条静默规则可以压掉一次确认；一条 review 规则可以指明合并前必需的 reviewer 和批准。适用于每个 Ticket 的要求，应当放进团队 prompt 段落。

## Policy 版本

规则、accept 模式和每个 Source 的 Policy 共同构成 Policy 版本。每个 Mandate 都记录它是在哪个版本下接的单。

版本变更会作废正在运行的 Eval，并把它们的 Trigger 重新入队。它还会给每个受影响的在办 Ticket 发送一条 policy-changed 的 Input。这条 Input 说明属于以下哪种情况：

- 命中的规则变了（包括它新的文本），或者不再适用；
- 请求者不再能开工；或
- 主动工作不再被接单，例如模式从 `auto` 改掉了。

未受影响的 Ticket 收不到通知。这次变更不会立刻撤销在办 Ticket 的 Mandate。

Source 的配置与 Policy 是分开的。它控制什么能进入系统：读哪些群聊、某个范围接收全部消息还是只接收 @。Mandate 记录它的 Source 和接收范围。恢复要求 Source 仍然在监听那个 Thread，但不要求它仍然接收那里的全部消息。

回复会在其 Source 关闭时等待；如果 Source 不再监听它的目的地，回复就会被丢弃。

关于 Executor 能拿自己的结果做什么的条件（例如什么时候可以合并），并不决定谁可以授权工作。它属于 agent 的指示，不属于 Policy。

## 恢复与 stop

已结束的 Ticket 保留它的 Mandate。人发在它自己某个 Thread 上的消息，可以不经新的 Eval 或 Decision 就恢复同一项工作，不论是谁发的。bot 和 CI 不会唤醒已结束的 Ticket。Executor 判断这个请求是否在范围之内，不在就结束这一轮。

只有三种操作会改变一个 Mandate：accept 创建它、人的 stop 撤回它、重新校验失败撤销它。被人 stop 的 Ticket 保持 ended，什么都不再接收。那里再要工作，需要一次新的 accept。

### 恢复前的重新校验

Source 必须仍在监听原来的 Thread。其余检查取决于 Mandate 的依据：

- explicit 的跟进 Mandate 直接通过。
- inferred 的 Mandate 需要 `auto` 模式，且它命中的规则仍然启用。
- 由某个准入格放行的 Mandate，在今天的准入表和发送者名单状态下，必须仍能拿到至少原来的强度。因此，把发送者移出名单，可能撤销一个经"名单内发送者"那一格接下的 Mandate。
- bot 的 Mandate 要求该 bot 仍在 Source 的 bot 名单上。经准入表和经 bot 的 inferred Mandate 还需要 `auto` 模式和启用的命中规则。
- 其他 Mandate 要求发送者仍在 Source 的允许名单上。

重新校验失败时，Ticket 保持 ended，也不接收它等着的任何消息。每条消息都被当作没有抵达任何 Ticket；如果没有别的 Ticket 拥有它，就进入 Eval。主 Session 不会被告知这条消息曾到达 worker。处理暂停之后也是如此。挂到该 Ticket 会被拒绝，后续工作需要一次新的 accept。

- **人在 Thread 里说"停"是一条普通的 Trigger**，由 Eval 决定是否 stop。Executor 不能声称是人让它停的。
- **面板里的 stop 是一条命令。**它直接作用于 Ticket，并记为一次手动 stop。
- **等待条件属于 Source。**"N 小时没有指派人"这种条件，应当是一个自己等待、自己再检查的 Source；Eval 永不等待。

## Eval 没能结束时

时限从候选抵达主 Session 起算。等待投递的时间不计，而没有投递出去的候选永不过期。

超时的 Eval 会把它的 Trigger 重新入队再试。连续重试两次之后，第三次超时记为 `unavailable`。研判失败也记为 `unavailable`；之后的一条 Trigger 可以开启一次新的 Eval。Policy 变更、或依据过期 Policy 作出的决定，记为 `unavailable` 并立刻按当前版本把该批次重新入队。

`evals` 这条健康项会报告最近一小时内未解决的 unavailable Decision。`scripts/dsh-superagent status` 包含这个错误。

只有当 unavailable Decision 不足 24 小时、仍是其 Thread 上最新的 Decision、尚未被 dismiss、且该 Thread 既不在排队也不在评估时，面板才会请求人工处理。人可以重新评估那条 Trigger，或者 dismiss 这个问题。
