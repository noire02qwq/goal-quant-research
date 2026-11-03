# DeepSeek Super-agent 设计探索精读（2026）

> 状态：已按本地源码核对增补（2026-11-03）｜ 精读日期：2026-11-01（文档）/ 2026-11-03（源码）｜ 材料：官方技术文章 + 开源原型仓库，非每周检索式产出（归 docs/essay-study/）

## 材料与来源

- 官方文章《Super-agent 设计探索：迈向更自主的 Agent 系统》（2026-10-31 晚 DeepSeek Harness 团队发布；全文转载：[知乎机构号](https://zhuanlan.zhihu.com/p/2099987320443237060)）
- 开源原型：[deepseek-ai/dsh-superagent-prototype](https://github.com/deepseek-ai/dsh-superagent-prototype)（MIT；README + docs/000–008 设计文档 2026-11-01 读；**2026-11-03 本地克隆 `oss-repos/dsh-superagent-prototype/` 源码走读** `src/`、`tests/`，增补见 §7——精读范围：核心域模型与授权路径，未逐行读 sources/ 各平台适配与 client UI）
- 交叉核对：[智东西](https://www.zhidx.com/p/606311.html)、[钛媒体](https://www.tmtpost.com/8189032.html)、[第一财经](https://www.yicai.com/news/103419784.html)（数字与表述一致）

## 1. 背景与动机

Coding Agent 已证明模型能自主解决复杂问题，人上移到决策与验收；但主流设计以单一 Session 为单位，**一个人通常只能同时跟进 3–5 个活跃 Session**——"单任务上限取决于模型能力，多任务上限取决于人的注意力"。Super-agent 定义为跨会话保持上下文、并行推进多任务的连续实体（连续、高效、主动、持久），断言"Session 应是系统实现细节，而非用户认知负担"。

## 2. 五大架构设计

1. **双层架构（Router/Worker）**：常驻 Router 承接全部人类交互、作全局协调点/记忆，**只分派不执行**（可不配 Bash，轻量模型即可）；Worker 上下文隔离、各挂完整工具、配最强模型，单 Worker 只做一件事，推理不外泄由 Router 统一回复。Router 抗突发靠**批处理**：上轮推理期间积压的 Trigger 下一轮一并注入、Prefill 并行，批越大单个决定越便宜。
2. **事件驱动与两级过滤**：主输入从人写 prompt 变为环境 Trigger。程序层先做确定性准入（来源/白名单/群组范围，三档：仅响应明确请求/作候选/忽略），语义层再由 LLM 按提示词策略研判（策略即提示词）。通过后 Router 冷启动任务；同话题构成 **Thread**，Worker 订阅后后续事件由程序**直通** Worker 不再经 Router。上下文按 Cache 管理：Inline（近期高概率用到内联）/Spill（超预算外置留引用或摘要）+ 链式召回（Trigger/Thread/Session 唯一 ID 内联关联形成引用图）。**投机执行**：后台先试，有价值才交付。
3. **异步多信道交互**：**Source** 抽象封装事件流、持读取位置（重启不重放）、持 bot 身份；异步 ReAct Loop 把耗时工具改 `start()`/`stop()`（start 立即返回，后台结果作为新事件回投）——已在 DeepSeek Harness 实现但**尚未默认开启**。输出匹配信道带宽：IM 单次回复硬性 ≤100 词，GitHub/邮件高密度结构化。
4. **存算分离**：计算（无状态弹性容器）／会话状态（持久化入 DB）／执行环境（重状态留原地，端侧只跑不存状态的轻量 daemon）三解耦。
5. **外部 Watchdog**：主系统之外的独立 Watchdog Session，定时消息驱动构成外部 Control Loop；除基础设施故障外，由模型判断各 Worker **有无实质进展、是否偏离目标**（针对无效循环等非崩溃异常），可在线增删提示词与触发规则。**原型未实现该模块**（属设计方向）。

## 3. 授权与治理（原型 docs/002）

链路：Source→Trigger→Thread→**Eval**（gate 确定性准入 + assessment 模型研判，Decision 五值 accept/stop/ignore/unavailable/**reopen**——前四值是 Eval 的产出（[docs/007](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/main/docs/007-architecture.md)），第五值 `reopen` 由人工在 Thread 发消息恢复已结束 Ticket 时写入，[src/core/model.ts:190,251-253](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/main/src/core/model.ts)）→ accept 生成 **Mandate** → **Ticket** → **Assignment** → Executor。

- **Mandate** 是不可变授权记录：Policy version、scope、strength、命中规则名、发送者在该 Source 的身份、Trigger 来源；仅三种变更——accept 创建、**人的 stop 撤回**、恢复前按当前 Policy **重校验失败吊销**。
- **"消息不得修改授权边界"**：聊天内容、评论、引用文档只是决策输入，权限只能源自 Policy。
- **主动接纳模式**：`off` / `observe`（**默认**：研判并记录 would accept 但不执行）/ `auto`（inferred 候选正向研判直接接单）。官方路线：先 observe 审阅记录再切 auto。
- Thread 内的"stop"只是普通 Trigger，Executor 不得自称被要求停止；只有 Panel 的 stop 才是人工命令直接撤权。

## 4. 实验数据

端到端消融（群聊+CI 流，单次约 300 条消息/约 20 条工作请求，时间按 1/4 缩放，每方案 5 次）：

- Super-agent p50 **12.4 分钟**、p95 **15.7 分钟**；
- 单 Session+Subagent 工具：中性提示下 5 次**一次都没调用 Subagent**（全被新消息打断），p95 **29.5 分钟**；
- 去订阅直通：完成时间基本一致，但 Router 决定数 **+约 30%**，读缓存 token **2323 万→3177 万（+37%）**——直通不提速，纯为 Router 省 token；
- Router 批处理压测（Trigger 1→40 条/分钟）：平均 batch 1.0→2.8，单次请求 2.5s→3.9s，单个决定分摊推理 **6.4s→1.6s**；
- 总取舍：**拿更多 token 换更短更稳的完成时间**，实验基于合成负载与简化环境。

## 5. 原型实现程度与自述局限

README 首行声明 "Research prototype for reference only, not an official DeepSeek product"；部分设计属未来方向、原型未实现（Watchdog 缺席，异步机制未默认开）。安全边界：worker/router 两个 preset 均以 `danger-full-access`、**部署者 OS 身份**运行，官方明示隔离须用专用 OS 账号——与最小权限直接冲突，是其自认开放问题。官方开放问题还包括：Router 扩展切分粒度、脱离 Session 的协作与人中途接管、组织级上下文边界与 A2A、云端 Agent 接入端侧凭据的安全。

## 6. 与"目标状态机+受管 Run"的对照

**直接可借鉴：**

1. **Mandate ≈ 审批归因**：授权依据固化为不可变记录+恢复前重校验+仅人工撤回，正是金融审批门审计留痕范式；"聊天内容不得修改权限边界"→ 落为"会话/群组消息不得扩大授权"（对应 §12.2 W4 群组治理）。
2. **Policy version 治理**（源码核对后为三段式，见 §7.2）：在途 Eval 撞上 Policy 变更 → 记 `unavailable` 并**按新版本立即重排队**（不作废业务）；规则的 disabled/changed 差异以 Effect **投递给存活 Ticket** 而非强杀；Mandate 按 `basis.via` 分路持续 `revalidate`，失权才撤——与"规则升级不破坏在途 Run"同构。
3. **Watchdog ≈ 恢复扫描的语义层**：外部 Control Loop 判断"有无实质进展/是否偏航"，补纯心跳检测不到的无效循环异常（对应 §13 stalled 判据、A6 目标健康分）。
4. **Source/Thread/Subscription ≈ goal_event 持久化+直通**：读取位置重启不重放、Trigger 幂等与 DB 权威+工具幂等回执完全同构；订阅直通=后续事件绕调度器直达受管 Run（实验：为调度层省约 37% 读缓存 token）。
5. **Router/Worker ≈ 群组角色分工**（§12.2）：Router 只分派不执行、Worker 隔离单任务，与研究/开发/评审分工一致；Worker 靠共享 Thread 自发现冲突可减少中心化协调；Router 批处理可搬到调度器突发场景；Inline/Spill+链式召回是 16KB turn_context 预算的现成方法论（与 W2 笔记 CALM"gate 先于 packing"互补）。
6. **异步 start()/stop()** 与受管 Run 的异步执行、pause/resume 语义天然契合。

**冲突或不采纳：**

1. **auto 主动接活 vs 金融强制审批**：`observe`（研判留痕不动作）可借鉴为影子验证；`auto` 不可默认——命中规则也只能生成待审批 Ticket，执行必须过审批门。
2. **inferred 强度+白名单的宽松准入**不适用：金融侧授权只能来自审批系统/工单。
3. **Executor 以部署者身份 danger-full-access 运行**与最小权限冲突，须专用身份+沙箱+凭据代理。
4. **投机执行**在高风险动作上不可行；仅纯读分析类任务可有限采用且产出只作草稿不外发。
5. dsh 无预算/pause-resume-terminate 语义，金融侧自建（brief-plan §7 既有设计）。

## 7. 源码走读增补（2026-11-03，本地克隆 `oss-repos/dsh-superagent-prototype/`）

对文档叙事的**实证与修正**，引用均为仓库内路径（链接指向 GitHub `main` 同路径）：

1. **observe 模式精确实现**：`mode` 默认即 `observe`（[src/policy.ts:84](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/main/src/policy.ts)，`z.enum(['off','observe','auto']).default('observe')`）；inferred 候选在非 auto 模式下判 `ignore`，但写入 `audit.would_accept=true` + `reason.code='observed'`（policy.ts:55-57）——"研判留痕不动作"是**一条代码路径**，可直接抄为影子验证的审计字段设计。准入强度三档 `ignore<inferred<explicit`（policy.ts:141 `STRENGTH` 表），机器触发另设 `machineGate`：非白名单 bot 一律 `not_human` 拒绝。
2. **Policy 变更三段式**（§6.2 的源码依据）：① 在途 Eval 发现 `policy().version !== evaluation.policyVersion` → 记 `unavailable` 并重排队到当前版本（[src/core/evals.ts:285](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/main/src/core/evals.ts)、[docs/002](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/main/docs/002-authorization.md) L151"immediately queues the batch under the current version"）；② `policyEffects()` 对每个在途 Ticket 计算规则 `disabled/changed` 差异并作为 Effect 投递，requester 失权→`requesterAllowed:false`，auto→非 auto 时 inferred 候选降级 `proactive=false`（policy.ts:144-161）；③ `revalidate()` 按 `basis.via`（followup/bot/admission）分路持续重校验（policy.ts:213 起）——**只有重校验失败才撤权**，与"规则升级不破坏在途 Run"精确对应。
3. **中断恢复语义（新增，W1 直接参照）**：Assignment 忙时被中断 → **重启时带 recovery note**（[docs/003](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/main/docs/003-execution.md) L45）；关停等待各 worker 后台作业最多 10s、未入 Session 史的 Input 保留（同 L45）；后台作业 30 分钟上限被杀后 Ticket 报 waiting、**Executor 下一轮读被杀作业的结果**（L35）；Input 投递幂等（"Add an Input once (idempotently)"，[src/core/tickets.ts:231](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/main/src/core/tickets.ts)）；重启不重放：读取位置存 KV（[src/sources/feishu-loops.ts:146-151](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/main/src/sources/feishu-loops.ts)）。这五条是 brief-plan §5.2 恢复扫描规则可逐条对拍的**已运行实现**。
4. **批处理实证**：Thread 的 Eval 串行运行、把期间到达的 Trigger 并入下一批（[docs/001](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/main/docs/001-domain.md) L43）；调度层 `evaluateDue()` 每 Thread 启一个 Eval、把等待 Trigger 合为一批（[src/app/passes.ts](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/main/src/app/passes.ts)、docs/007 L93）；Eval 过期重排队两次、第三次记 `unavailable`（docs/007 L93）。
5. **danger-full-access 实锤**：worker session 初始化即 `permissionPresets.set(session, 'danger-full-access')`（[src/app/sessions.ts:152](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/main/src/app/sessions.ts)），docs/003 L27 明言"run commands without approval as the operator's OS user"——§5 自认的安全边界开放问题**在代码里成立**，非措辞。
6. **Watchdog 确认缺席**：全仓 docs/ README grep `watchdog` **0 命中**——§2 第 5 条"原型未实现"从自述升级为代码证据。
7. **文档与代码的一处出入**：docs/007 L57 把 Eval 结局列作"accept, stop, ignore or unavailable"四值，但域模型 `DecisionKind` 实为五值（含 `reopen`，model.ts:190）——`reopen` 不出自 Eval 而出自人工恢复路径，文档表述与类型定义粒度不一致，引用其 Decision 语义时以**类型定义**为准。

## 8. 落点

- W1：Watchdog 语义层 + Source 读取位置/Trigger 幂等 → recovery demo 参照（决策记录随 demo 落）；§7.3 的五条恢复语义（recovery note / 未入史 Input 保留 / 被杀作业下轮读取 / Input 幂等 / KV 读取位置）作 recovery demo 的逐条对拍清单。
- §12.2 W2/W4：Mandate→审批归因字段设计、Router/Worker→群组静态编排参照（与 decisions/0001 的静态角色+SOP 结论互证）。
- W2：Inline/Spill 链式召回补充 turn_context 组装协议候选方案（与 CALM gate 方案对比后定稿）。
