# 金融领域长期目标自主智能体 —— 设计方案

> 日期：2026-10-26 ｜ 项目：AgentStudio（harness-hub）｜ 周期：两阶段约 10 周（第 5 周、第 10 周各一次成果汇报）
>
> 本文档覆盖：思路溯源（调研借鉴）→ 总体设计 → 执行协议与治理 → Phase 2 测评优化闭环 → 创新功能 → 示例策略模板 → 数据模型与落地路线。

---

## 1. 需求原文与解读

**第一阶段（W1–5）：长期目标管理与自主执行**

建设从用户提出目标、制定策略到代码生成、定时执行和结果交付的完整能力：

- 解析用户目标、策略与约束 → 形成评价指标、任务拆解和执行计划
- 智能体自主编写、测试、执行和调试金融数据处理、指标分析及回测代码
- 周期任务、交易日调度、任务依赖、异常处理机制
- 持久保存目标、策略、代码版本和执行进度；跨会话跟进、中断恢复、多目标独立运行
- 权限、资源预算、人工审批、暂停/恢复/终止控制
- 目标工作台：执行计划、任务状态、运行结果、历史记录

汇报场景：完整金融场景演示"提交目标与策略→生成代码→验证运行→创建定时任务→持续交付结果"，外加任务失败修复、服务重启恢复、用户调整目标后的执行。

**第二阶段（W6–10）：效果测评与策略自主优化**

- 金融策略测评体系：历史回测、模拟跟踪、基准对比、样本外验证
- 按周期评价收益、回撤、波动、交易成本、信号有效性；分析目标偏差并生成报告
- 智能体根据测评结果提出改进假设，自主调整参数、策略或代码
- 新旧策略实验验证，按评价标准和授权范围决定是否应用
- 策略版本追踪、效果对比、变更审批、回退
- 动态调整执行计划；识别目标达成、持续无改善、预算耗尽、风险约束触发等状态
- 工作台展示策略演进、实验结果、决策依据

汇报场景：同一金融目标多轮"执行—测评—分析—优化—验证"运行记录、新旧策略对比、可复现验证、优化无效时保留原策略/回退/请求人工介入。

### 1.1 核心设计判断

| 判断 | 结论 |
|---|---|
| 本质 | 一个**状态机驱动 + 调度触发 + 测评闭环**的长程 Agent 系统，不是更强的聊天机器人 |
| 长程关键 | 上下文每轮重建且有界，权威状态在数据库，不依赖会话历史存活 |
| 平台合规 | 必须走 Cordis 插件边界，复用平台调度/Runtime/审批/产物协议，不造第二套执行内核 |
| 领域无关性 | 引擎不感知"交易日""夏普比率"；金融语义全部在领域层 profile，保证可扩展 |

---

## 2. 平台现状盘点（可直接复用的地基）

| 能力 | 现状 | 在本设计中的角色 |
|---|---|---|
| Cordis 插件架构 | 强制插件化；`agent.tools / agent.skills / agent.instructions / agent.turn_context / conversation.view / site.navigation / http.router` 等贡献点 | 新功能落地形态的全部接口 |
| 调度 | `workspace-automation` 插件：DB 原子认领 + lease 心跳 + fencing token + occurrence 幂等，`interval/cron/event` 三型，多节点安全，含 recovery | 定时执行地基；扩展 `trading_day` 日历类型 |
| 执行引擎 | DSH Runtime 会话 + 沙箱（local/AIO/THS 远程）+ S3 checkpoint + Artifact 协议 + `outcome_unknown` 语义 | 智能体写代码/跑回测的执行底座；天然支持中断恢复 |
| 金融数据 | `market-research` 插件（行情/K线/指标/回测审计/前视偏差 lint/双均线验证，公开导出 `MarketDataProvider` 协议与图表组件）；`/api/financial/*`（资产注册表、行情数据点、不可变口径 calibers） | quant-research 消费其公开契约；测评证据链复用资产注册表 |
| 治理编排 | WorkProject/WorkTask 全家桶：Attempt、PlanItem、审批 Inbox、投递 outbox、风险结果 | 审批/预算/风险控制的模式参照 |
| 评测 | Agent Eval：用例/批次/对比/趋势分类 | Phase 2 测评体系的模式参照 |
| 记忆 | memory 插件：`goal`、`work_summary` fact 类型 + Prior Work Recall；MySQL ngram 全文索引（支持中文） | 执行记忆蒸馏的存储与召回 |
| 渠道 | channel 插件（飞书/Slack/Telegram…） | 周期报告推送 |
| 金融工作台验收 | `seed_financial_workbench_acceptance.py` 已存在 fixture | 平台正朝金融场景演进，本功能与其同向 |

**平台没有的（即本功能新建）**：Goal 领域模型与状态机、计划 DAG、策略代码版本链、交易日历调度、目标进度持久化与恢复、测评驱动优化闭环、目标工作台。

---

## 3. 调研借鉴（四个参考项目的机制映射）

> 调研对象：Microsoft RD-Agent、vnpy(VeighNa)、NousResearch hermes-agent、CopilotKit openmuse（用户所指 openmuse 为 GitHub 量化定位候选缺失后最接近的长程 agent 项目；hermes 同理取 hermes-agent）。本表只收**已读出机制映射**的项目；要读的开源项目/官方文档清单（OpenMuse、OpenDots、Rakazo、Hermes）与执行判据见 §3.1。

| 来源 | 借鉴机制 | 落到本设计的位置 |
|---|---|---|
| **RD-Agent** | RDLoop（propose→coding→running→feedback）研究循环 | **Phase 2 策略迭代循环的直接原型**（§8.2） |
| | 失败跳 feedback 不终止循环（`skip_loop_error`） | 执行协议的韧性规则：回测报错生成修复任务重进循环 |
| | 按 loop/step 持久化会话、任意步恢复 | GoalRun/GoalEvent/代码版本链 = 等价物；中断恢复从最近一致状态继续 |
| | workspace checkpoint 沉淀代码版本，历史实验进入下轮上下文 | GoalCodeVersion 链 + S3 artifact；top-k 历史实验摘要注入 propose 上下文 |
| | 多臂老虎机自适应选研究方向 | B 组扩展：实验预算分配（§9） |
| | 因子-模型交替优化、多臂调度（RD-Agent(Q)，ARR 约为经典因子库 2 倍） | A8 因子库 + B 组组合优化扩展的依据 |
| **vnpy** | 策略模板（CtaTemplate：parameters/variables 白名单 + on_bar 回调 + 引擎注入） | **回测框架基座**：`GoalStrategyBase` 薄封装控制模型 API 面 |
| | 回测/实盘双引擎复用同一策略类（`get_engine_type` 分支） | 回测→模拟盘→（远期）实盘零改码切换的结构保证 |
| | 状态快照 JSON + 启动"回放历史→还原状态→再订阅"恢复 | 目标任务状态恢复协议的参照 |
| | Datafeed/Datastore 适配器抽象 | quant-research 数据服务适配器协议 |
| | vnpy.alpha 多因子模块（4.0，受 Qlib 启发） | 因子库的进阶参照 |
| **hermes**（文档+源码走读 2026-11-03，[hermes-2026.md](essay-study/hermes-2026.md)） | agent 自管记忆 + 周期蒸馏（nudge）；经验→技能沉淀 | **Run 收尾记忆蒸馏**：每期生成执行摘要+教训写入 memory facts；稳定经验**隐式沉淀为目标私有技能**（本地装载，不走 SkillHub 送审，形态同 agent-management/application-management 内部技能）。**走读出入**：蒸馏实为每 `nudge_interval=10` 轮的 turn 结束后台 review fork，非 Run 收尾、内置记忆无 `on_session_end`（仅外部 provider 有）；技能沉淀证实但落 profile 级全局 `~/.hermes/skills/`，「目标私有」形态 hermes 无对应（最接近 project-local skills + `skills.create_dir`），需本项目自建 |
| | cron + 持久化状态模块 + startup watchdog 组合 | 无人值守调度的工程样板（**证实**：jobs.json 原子写 + flock、missed-occurrence contract「每期至多一次且必交代」、300s fire-claim 租约、投递队列 fenced-unknown 永不重试、unreachable_retry 仅零副作用才重跑）；**「恢复扫描（孤儿 Run 清理）」推翻留痕**（CONVENTIONS §3 规则 7）：startup watchdog 实为「启动死锁 → faulthandler dump → `os._exit(75)` 由 supervisor 拉起」的存活看门狗，不扫描任何持久化任务——恢复扫描应改参照 kanban dispatcher（过期 claim/死 worker/`reconcile_orphans`）与 cron pending_slot 恢复 |
| **openmuse**（源码走读 2026-11-03，[openmuse-2026.md](essay-study/openmuse-2026.md)） | SQL lease 协调多 worker 并恢复被中断任务 | 与平台 `workspace-automation` 的 claim/lease/fencing 幂等同构——直接复用，文档互为佐证。**源码证实**（CAS 认领 + 60s 租约 + 心跳，guard/checkpoint 用 CAS 期望集带 `leaseId`，过期重认领 `attempts+1` 续跑 checkpoint）；出入：无单调 fencing token（由 CAS 期望集承担）、单表 `records`+jsonb 非专用表 |
| | durable plan 的 approvals/receipts 门控 | 任务回执（result_json+产物指针）；重试先查回执防重复执行。**证实但有出入**：幂等键命中直接返回回执 + `insertIfAbsent` 首写胜出、审批门控在源码，但门控对象是外部写 **Action 而非 plan**（plan 只是 `TaskStep[]`，无计划 DAG/计划审批）、无独立回执表、审批后**重新领起一次执行**而非同一 Run 继续 |
| | **结果不确定时不做隐藏重试** | 金融级执行安全：超时/中断标记 `outcome_unknown` → 显式恢复任务，绝不静默重跑（重复下单=真金白银）。**证实但有出入**：`OutcomeUnknownError` + 启动 `recoverInterruptedActions`（executing→outcome_unknown）+ 外部写不重发/流开始后不重试均在源码；但 `outcome_unknown` **只在 Action 层**，`TaskStatus` 无此态，任务租约过期仍是 CAS 回 `queued` 静默重跑（靠 `leaseId` CAS + `state.operations` 缓存兜底）——本项目须把「先标未知再决策」上提到任务层 |
| | 周期 Goal 巡检 + 告警去重 + 失败退避 | 巡检任务类型（数据源可用性/模拟盘持仓偏离/目标偏差）。**证实但有出入**：告警去重 = 确定性 id + `insertIfAbsent`、退避 `min(60,2^n)` 分钟、连续 5 次自动 `paused` 均在源码；但**无 Goal 级巡检**（Goal 仅 title/description/milestones），巡检对象只有公开网页三条件，无 cron/trading_day 调度 |
| **Rakazo**（源码走读 2026-11-03，[rakazo-2026.md](essay-study/rakazo-2026.md)） | 群组交接 `handoff_to_bot` 按源 Run 幂等（`clientNonce` 唯一键、一阶段一主、禁回弹、hop≤6、交接后 `handedOff` 禁全部工具并置空回复）；委派结果自动回传 `auto-outcome:<runId>` + `botOutcomeReturnedAt` + reconciler 兜底 | §12.2 W1/W3 群组交接 consume-once 与 §4.4 `goal_receipt` 两级幂等键同构；结果回传为**至少一次投递 + 幂等去重**（非严格一次），失败回传显式文案——`goal_group_message` / 回执设计的直接参照 |
| | Routines：`nextRunAt` 权威 + graphile 行级 CAS 认领 + nonce 幂等 + reconciler 补漏 + 迟到 occurrence 合并（`retryOfRunId` 唯一） | §5.3 调度 occurrence 幂等、失败退避、漏触发恢复的参照；Rakazo 只有 cron + watch，**无 trading_day、无 DAG 依赖**，交易日历与依赖编排仍自建 |
| | 人工控制租约（15min TTL + `waiting_takeover` 30min 自动取消 + 两种续跑提示） | §5.5 人工接管/挂起 Run 审批后同一 Run 继续的参照（屏幕级租约 → 交易级审批门属类比）；**全仓 grep `assigned_role` 零命中**——分工靠 roster + mention + 标志位，W3 角色字段需自建（与 decisions/0001 静态角色结论互证） |
| **OpenDots**（源码走读 2026-11-03，[opendots-2026.md](essay-study/opendots-2026.md)） | `claim+owns()` fencing、租约过期 → `interrupted`、UI 明示 "Retry after review"（重启不自动续跑） | §4.3/§5.2 状态机与 §7 运行结果区：**UI 必须区分 interrupted 与 failed**；与 openmuse claim/lease 同族互证 |
| | 权限三层 AND（全局 Settings × Dot × per-tool）+ 100ms/50ms watcher 热撤销（权限/连接 fingerprint 变化即 `abortRun`） | §5.5 治理与 §12.2 W4 授权矩阵：运行时撤销与「消息不得修改授权边界」同向 |
| | MCP 写动作：存参不执行 + `claimAction` INSERT OR IGNORE（claim-once）+ 1h TTL + 唯一 owner 路由；Slack 收敛到单 owner 白名单、channel 轮次不下发审批门工具 | §4.4/§5.5 审批门与 `requested_by` 归因参照；**与二手定位差异已留痕**：无 agent 间交接、无群组、无事件触发（README 自认 further work），always-on 仅为单进程 tick Runner |

### 3.1 开源项目 / 官方文档研究计划（2026-11-02 @user 增补）

> **与 §3 主表的关系**：主表只收**已读出机制映射**的项目结论；本节是**研读计划**——列出要读的开源项目与官方文档、读什么、提取什么机制、落到本文档哪一节、当前状态。走读笔记产出归 `docs/essay-study/`（该目录职责含"外部项目源码走读笔记"，命名 `<repo短名>-<年>.md`，见 [essay-study/README](essay-study/README.md)）。
>
> **执行前置（已解除）**：境外通道于 2026-11-03 恢复（三探针 200、`gh auth` 有效），同日 `oss-repos/` 本地克隆目录建立（已 gitignore）并按优先级完成四项源码走读——本节状态全部更新为「已读」，机制映射已回填 §3 主表（含 Hermes watchdog 推翻留痕）。下表「定位」列保留为 2026-11-02 的二手初判，**已由源码走读核实或修正，差异见各笔记**。

| 项目 | 仓库 / 文档 | 定位（2026-11-02 二手初判，已由 2026-11-03 源码走读核实/修正） | 与本项目的关联点（初步） | 研读任务 | 状态 |
|---|---|---|---|---|---|
| **Rakazo** | [elie222/rakazo](https://github.com/elie222/rakazo)（官网 [rakazo.com](https://rakazo.com/)；协议据 [CSDN 拆解](https://blog.csdn.net/gitblog_00752/article/details/166776412) 记为 Apache-2.0，待读 LICENSE 确认） | 开源 Grok Bot 替代：持久 Bot（对话线程 / 记忆 / Routines / Artifacts 产物面板）、Pi 模型层 BYOM、**Team Computer vs Private Computer**（Docker/E2B/Daytona 沙箱，容器暂停重建后状态保留）、浏览器/终端/文件/GUI 全访问 + Take control 接管、语音通话、**Bot 间委派与短命子代理**（`child-bots.ts`、`group-handoff.ts`）、Composio/MCP/OpenAPI 连接器；TypeScript + React 19 + PostgreSQL | **与 §12.2 群组分工/交接直接同构**（`assigned_role`、群组消息、handoff）；Routines ≈ `trading_day`/cron 调度（§5.3）；Artifacts 面板 ≈ 产物交付；Take control ≈ 人工接管/审批（§5.5） | 走读 ①`group-handoff`/`child-bots` 的委派与结果回传语义（是否 consume-once、失败归属）②Routines 触发与持久化（幂等键、断点恢复）③Computer 状态在容器重建后的保留机制；结论回填 §12.2 / §5.3 / §4.4 | **已读**（2026-11-03 源码走读，[rakazo-2026.md](essay-study/rakazo-2026.md)；映射已回填 §3） |
| **OpenMuse** | [CopilotKit/openmuse](https://github.com/CopilotKit/openmuse)（MIT，官网 [copilotkit.ai/openmuse](https://www.copilotkit.ai/openmuse)；中文拆解见 [知乎](https://zhuanlan.zhihu.com/p/2088284963326185703)、[mushroom.cv](https://blog.mushroom.cv/blog/openmuse-copilotkit-personal-ai-agent-browser-workspace/)） | 自托管个人 agent 模板：持久化 Chromium 浏览器（跨任务保留 profile）、可选 Linux 工作区（终端+文件）、**持久化后台任务（SQL 租约协调）**、Gmail/Google Calendar 连接器、iOS/Android/Web 三端 | §3 主表已有四条映射（SQL lease ≈ `workspace-automation`、approvals/receipts 门控、`outcome_unknown` 不隐藏重试、周期巡检） | 走读 durable background task 的租约/回执实现与中断恢复路径、approval gating、不确定结果标记；与 `goal_run`/`goal_receipt` 对拍，差异回填 §4.4 / §5.2 | **已读**（2026-11-03 源码走读，[openmuse-2026.md](essay-study/openmuse-2026.md)；四条映射逐条判定完成并回填 §3） |
| **OpenDots** | [CopilotKit/OpenDots](https://github.com/CopilotKit/OpenDots)（官网 [copilotkit.ai/opendots](https://www.copilotkit.ai/opendots)；仓库归属经 @user 2026-11-02 确认取 CopilotKit，同名的 [diggerhq/opendots](https://github.com/diggerhq/opendots) 不在本计划内）；中文报道 [腾讯新闻](https://news.qq.com/rain/a/20261003A03BJP00) | "always-on AI coworker" 起点模板：clone → 定义 Dot → 接服务 → 改界面与工具；常驻 agent 各配一台机器，可在 Slack 等处接活、会话内持续交接任务 | 与本项目"常驻目标 + 目标工作台 + 受管 Run"形态对照；关注 Dot 定义/服务连接是否 schema 化 | ①读 README + 官方 FAQ，提取 always-on 生命周期、Dot 定义 schema、任务交接与权限边界 ②落 §7 工作台与 §12.2 | **已读**（2026-11-03 源码走读，[opendots-2026.md](essay-study/opendots-2026.md)；映射已回填 §3，二手定位差异已留痕） |
| **Hermes** | [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)（本 agent 运行时，[官方文档](https://hermes-agent.nousresearch.com/docs)） | 自管记忆 + 周期蒸馏（nudge）、经验 → 技能沉淀、cron + 持久化状态模块 + startup watchdog | §3 主表已有两条映射（Run 收尾记忆蒸馏、无人值守调度工程样板） | 文档级走读：memory/skill 生命周期与 cron 恢复语义，对照 §5.4 CALM 语义与 §5.2 规则 8 恢复扫描；笔记须标注"自身项目"利益相关 | **已读**（2026-11-03 文档+源码走读，[hermes-2026.md](essay-study/hermes-2026.md)；两条映射判定：主体证实+两处出入、watchdog 恢复扫描**推翻**，已回填 §3） |

**完成判据**：每个项目一页走读笔记（`docs/essay-study/<repo短名>-<年>.md`，标注精读范围、附可点击链接）→ 机制映射回填 §3 主表 → 若推翻本文档假设，按 CONVENTIONS §3 规则 7 在对应小节留痕。**2026-11-03：四项全部完成**（笔记 4/4、回填完成、hermes watchdog 推翻已按规则 7 留痕）。

**优先级**：Rakazo（§12.2 W3 群组分工直接同构）> OpenMuse（§3 已有映射待源码验证）> OpenDots（仓库已确认 CopilotKit/OpenDots）> Hermes（自身项目，利益相关需标注）。

---

## 4. 总体设计

### 4.1 定位与插件分解（已确认）

**通用"长期目标自主智能体"引擎 + 金融领域层**，两个新插件，通过公开契约通信：

```
plugins/
├── goal-agent/          # 通用长期目标引擎（市场无关）
│   ├── src/server/       # Goal/Plan/Task/Run 领域模型与状态机、调度触发、
│   │                     # 受管 Run 协议、turn_context 组装、控制 API、恢复扫描
│   ├── src/client/       # 目标工作台（导航入口 + 列表 + 详情四区）
│   ├── src/runtime/      # （如需）runtime 侧贡献
│   ├── migrations/       # 插件自有迁移（goal_* 表）
│   └── tests/
└── quant-research/      # 金融领域层插件（首个领域 profile）
    ├── 交易日历（A股 profile：节假日/周末顺延）
    ├── 金融数据服务（复权日线、基准指数；DataFeed 适配器协议）
    ├── 策略运行规范（GoalStrategyBase、vnpy 回测封装、指标计算库）
    ├── 策略测评协议实现（指标口径 → goal-agent 评价维度）
    ├── 示例策略模板（T1–T4 内置资产）与策略演进面板
    └── migrations/（quant_* 表：日历缓存、因子库等）
```

**边界理由**：goal-agent 不知道什么是"交易日"和"夏普比率"；quant-research 不知道调度和状态机。market-research 保持不动，quant-research 只消费其公开导出（`MarketDataProvider` 协议、`@agentstudio/market-research/chart`），不引用其内部源码——符合 pluginization 协议"插件之间只能通过公开契约通信"。

**领域 Profile 契约**（goal-agent 定义的公开贡献点，quant-research 是首个实现者）：

```json
{
  "type": "goal.domain_profile",
  "id": "finance.a-share",
  "calendar": "trading_calendar_factory",     // 下一个执行时点查询
  "task_types": ["backtest", "paper_track", "evaluation", "report"],
  "eval_dimensions": [{"name": "max_drawdown", "direction": "lower", "default_bound": 0.15}],
  "risk_rules": [{"type": "drawdown_limit", "action": "pause+approval"}],
  "report_template": "periodic_report_factory",
  "terminal_predicates": {"stalled": "consecutive_no_improvement>=3"}
}
```

换市场（美股 profile）或换领域（基本面研究 profile）= 新 profile 插件，引擎零改动。

### 4.2 执行形态（已确认：方案 B）

**目标状态机 + 调度触发的受管 Run**。目标/计划/任务/代码版本/进度全部落插件数据库（权威源）；调度器到点创建一次性的短受管 Run；每轮通过 `agent.turn_context` 注入有界状态摘要（≤16KB：目标、计划进度、上期回执、记忆召回、预算余量、审批门状态），Run 结束通过工具把回执写回数据库。交互会话与目标**关联但不等同**。

排除项：方案 A（目标即长期会话——数周级上下文膨胀、clarification 挂起使无人值守不可控）；方案 C（独立编排 Worker——绕开平台 trace/审批/沙箱/租户隔离，违反统一 DSH Runtime 边界）。

### 4.3 目标状态机

```
draft → planning → awaiting_approval → running ⇄ paused
                                          │
        ┌───────────┬─────────────┬──────┴────────┬──────────────┐
    achieved     stalled   budget_exhausted  risk_triggered  cancelled
```

- `planning`：智能体解析目标 → 产出策略声明+评价指标+计划 v1 → `awaiting_approval`（**计划审批必经**，对应 mission"人工审批"）
- `running` 中可转 `paused`（用户手动或风险约束触发）；恢复从**下一个未完成任务**继续，已完成的期次不重跑（幂等由调度层 occurrence 键保证）
- 终态四分支 = mission Phase 2 要求：目标达成 / 持续无改善 / 预算耗尽 / 风险约束触发
- `stalled` / `risk_triggered` 判据由领域 profile 提供（引擎只提供钩子）

### 4.4 领域模型（goal-agent 插件自有表，全部带租户边界）

| 实体 | 关键字段 | 说明 |
|---|---|---|
| `goal` | status、kind(profile id)、budget_json、description、bound_agent_id | 一个目标一行；多目标=多行独立运行 |
| `goal_strategy` | 策略逻辑、约束（风险偏好/禁止操作）、**评价指标定义**（名称/方向/阈值/权重） | 从用户输入解析生成，人工可编辑；Phase 2 的评判依据 |
| `goal_plan` | version、任务 DAG(JSON)、generated_by(run_id)、approval_status | 计划有版本，重规划产生 v2/v3 |
| `goal_plan_task` | type(code/schedule/eval/report/approval/patrol)、schedule_spec、depends_on、status、last_run_id | DAG 节点；schedule 型带 cron 或 `trading_day` 规则 |
| `goal_run` | task_id、run_source(scheduled/manual/recovery)、agent_run_id、status(queued/running/succeeded/failed/**outcome_unknown**)、claim_owner、lease_expires_at、fencing_token、attempts | 每次受管 Run 执行记录，关联平台 AgentRun；认领/租约/fencing 字段支撑恢复语义（[decisions/0002](decisions/0002-w1-recovery-semantics.md)） |
| `goal_receipt` | idempotency_key（期次 occurrence_key / 步骤 step_key **两级**）、payload_json、fencing_token、written_at | 独立幂等回执表（原 goal_run.receipt_json 升格）；INSERT OR IGNORE 首写胜出、重复写不覆盖；恢复路径先查回执（0002 决策 3/4） |
| `goal_group_message` | session_id+seq（主键）、sender_agent_id、content、created_at | 群组会话消息独立持久化：**锚点不挂 goal_run**（会话横跨多次期次 Run），恢复语义与 goal_run 统一（consume-once/幂等追加/fencing）（0002 决策 5） |
| `goal_effect_ledger` | effect_key、关联 occurrence/step、count、observed_at | 外部 effect 台账：恢复正确性**第二 oracle**，独立于执行路径对账实际 effect 次数（[2608.03836](https://arxiv.org/abs/2608.03836)，0002 补充采纳①） |
| `goal_code_version` | kind(strategy/data)、S3 artifact 指针、parent_version、test_status | 智能体自写代码版本链；回测报告绑定具体版本 |
| `goal_event` | 事件流（状态流转/审批/异常/恢复/决策）、**actor_agent_id** | 工作台时间线 + 全程可追溯审计底座；actor_agent_id 记录事件触发成员（§12.2 W1 采纳） |
| `goal_memory_digest` | run_id、摘要文本（HaMo 三元组格式）、教训、嵌入/关键词、**lifecycle**、**valid_until**、**superseded_by**、**scope**(shared/private)、**author_agent_id** | 记忆蒸馏产物（另写一份进 memory facts 供召回）；生命周期/有效期/替代指针按 §5.4 CALM 语义（0003 决策 3/4/5），scope/author_agent_id 支持 §12.2 群组分层（0003 决策 6） |
| `goal_experiment`（P2） | hypothesis_json、code_version、eval_before/after、verdict、reviewer_opinion、decision | RDLoop 全程记录 |
| `goal_strategy_version`（P2） | parent、代码+配置指针、status(candidate/active/rolled_back)、eval_snapshot | 策略版本链 |
| `goal_evaluation`（P2） | strategy_version、period、eval_kind、metrics_json、verdict_per_metric、evidence[]、**trial_count、effective_trials、psr、dsr** | 不可变测评快照；去膨胀字段由试验账本计算（待 W6 定稿） |
| `goal_trial_ledger`（P2，新增） | goal_id、experiment_id、code_version、window、returns 指针(S3)、is_design_window | **每一次**候选回测都入账（含被否决者），DSR/有效试验数/PBO 只从账本计算；不可删改 |

MySQL 规范遵循：无外键/CHECK/触发器，关系字段显式索引，迁移经 `EXPLAIN` 门禁；插件迁移归插件 `migrations/` 自管。

> 修订留痕（2026-11-01，@dev）：`goal_run` 状态与字段、新增 `goal_receipt`/`goal_group_message`/`goal_effect_ledger`、`goal_event.actor_agent_id`——依据 [decisions/0002](decisions/0002-w1-recovery-semantics.md)（已采纳）+ [literature/W1](literature/W1-durable-scheduling-recovery.md)。
>
> 修订留痕（2026-11-01，@dev）：`goal_memory_digest` 增 lifecycle/valid_until/superseded_by/scope/author_agent_id 字段与 HaMo 三元组格式——依据 [decisions/0003](decisions/0003-w2-memory-distillation.md)（已采纳）+ [literature/W2](literature/W2-context-memory-distillation.md)。

---

## 5. 执行协议、调度与治理（Phase 1 核心）

### 5.1 一次"期次执行"的完整协议

```
调度器(交易日 08:30)                     Runtime(DSH)                      goal-agent 服务端
    │ 创建 GoalRun(claim/lease/fencing)      │                                  │
    ├─ 受管 Run 提交 ───────────────────────→│ turn_context 注入:               │
    │                                       │  目标+策略+计划进度               │
    │                                       │  上期结果摘要 + top-k 记忆召回     │ ← hermes 蒸馏记忆
    │                                       │  当前代码版本 + 本期任务           │
    │                                       │  预算余量 + 审批门状态            │
    │                                       │ agent 执行:                      │
    │                                       │  goal_read_context 工具(按需细读)  │
    │                                       │  bash 沙箱: vnpy 回测/数据处理     │
    │                                       │  quant_run_backtest 结构化工具 ──→│ 标准化统计采集
    │                                       │  goal_write_receipt 幂等回执 ────→│ result_json+产物指针
    │                                       │  goal_report_progress ──────────→│ 状态机流转+事件流
    │                                       │  goal_request_approval(可选) ───→│ 挂起→审批→同一 Run 继续
    │ ← 终态回执 ───────────────────────────│                                  │
    ├─ 记忆蒸馏子步骤 → memory facts + goal_memory_digest                       │
    ├─ 巡检任务(数据源/持仓偏离/目标偏差)                                        │
    └─ 计划下一期 occurrence(幂等键)                                            │
```

**执行工具组**（`agent.tools` 贡献，group `goal`，仅 goal 绑定任务装配）：

| 工具 | 作用 |
|---|---|
| `goal_read_context` | 按需读取完整目标状态/计划/历史回执（turn_context 只放摘要，细节按需） |
| `goal_write_receipt` | 幂等写回执（task_id+occurrence 键去重） |
| `goal_report_progress` | 上报任务状态变化（含失败原因），驱动状态机 |
| `goal_request_approval` | 挂起 Run 请求人工审批（复用平台 user-question continuation 语义） |
| `goal_update_plan` | 提交计划修订（产生计划 v2，进审批流） |
| `quant_run_backtest` | 结构化回测：指定代码版本+窗口 → 沙箱跑 vnpy → 标准化统计回传（quant-research 提供） |
| `quant_get_calendar` / `quant_fetch_history` | 交易日查询 / 复权行情拉取（缓存到任务文件存储） |

**turn_context 记忆组装顺序**（有界摘要协议，16KB 上限不因群组放宽）：记忆注入部分固定四步——① 硬过滤（只放行 ACTIVE/STABLE 记忆，CANDIDATE 未过晋升 gate 不注入）→ ② 准入打分 → ③ 按分贪心装入 token 预算 → ④ **挤出者留持久层可再检索（挤出≠拒绝）**。未过 gate 的记忆分数再高也不注入（**gate 先于 packing**）；细节仍靠 `goal_read_context` 按需细读。

### 5.2 关键执行规则（借鉴采纳的落点）

1. **上下文每轮重建、总量有界**：turn_context 由服务端组装；细节靠工具按需读——会话膨胀不影响长程运行（RD-Agent 每轮重建 loop 上下文同款思路）
2. **回执先查再执行（两级幂等）**：期次级 `occurrence_key` 回执防整期重跑 + 步骤级 `step_key` 回执防期内重复（独立 `goal_receipt` 表，INSERT OR IGNORE 首写胜出）；重试/恢复路径一律先查回执，已成功则跳过（[decisions/0002](decisions/0002-w1-recovery-semantics.md) 决策 3，w1-recovery-demo 场景 B 实测：崩溃恢复后已完成步骤零重跑）
3. **失败不终止**：任务失败 → 状态机生成修复任务重进循环；连续 N 次修复失败升级人工介入事件（RD-Agent 韧性）——即 mission 要求的"任务失败修复"演示能力
4. **结果不确定不隐藏重试**：Run 超时/连接中断 → 显式落 `outcome_unknown`（**不伪装终态、不静默重试**），恢复扫描决定重跑或人工确认（0002 决策 1；审计视角必须能区分"从未执行"与"执行结果未知"）
5. **恢复扫描**：服务启动 + 周期扫描 lease 过期的"孤儿 Run"：先标 `outcome_unknown` 再决策——有期次回执补判 succeeded、无回执重排（requeue）；中断中的步骤证据标 `interrupted` 不得伪装 completed；扫描本身幂等（0002 决策 1/3，w1-recovery-demo 场景 B + `test_expired_*` 定点测试）
6. **fencing 写保护**：回执/终态写入携带当前 fencing token 并在**同一事务内校验**，租约易主后旧持有者的写入被拒绝——"重启后的旧 worker 不污染新执行"的构造性保证（0002 决策 4，`test_stale_token_write_rejected`）
7. **恢复正确性第二 oracle**：恢复对账不信任执行路径自身状态，自建外部 effect 台账（`goal_effect_ledger`）核对"声明完成"与"实际 effect 次数"（[Resume Means Resume](https://arxiv.org/abs/2608.03836) 实测 5 框架内部状态全部部分违约：CrewAI 显示 correct=11 而外部 ledger 实际 effect=2）
8. **恢复语义验收清单**：状态机全转换表（状态×事件→动作，含异常路径）逐条翻译为可失败测试，对拍 [2608.03836](https://arxiv.org/abs/2608.03836) 六性质 + fork-intent + liveness（恢复决策=DB durable state 纯函数、审批门 CAS 式消费一次、写入 schema loud reject、resume 带 retry/fork 判别位、"永不恢复"也算违约）；框架/实现升级不得使清单退化

> 修订留痕（2026-11-01，@dev）：规则 2/4/5 细化 + 新增规则 6/7/8——依据 [decisions/0002](decisions/0002-w1-recovery-semantics.md)（已采纳，含 @research 文献复核结论与三项补充采纳）+ [literature/W1](literature/W1-durable-scheduling-recovery.md) 方向结论。

### 5.3 调度层（扩展而非重造）

- 复用 `workspace-automation` 的 DB 原子认领 + lease 心跳 + fencing + occurrence 幂等（多节点安全）
- **交易日历**：`schedule_spec` 新增 `trading_day` 类型——quant-research 的 A股 profile 提供日历查询（节假日闭市自动顺延到下一交易日）；引擎只调 profile 的"下一个执行时点"，不内嵌市场知识
- **任务依赖**：DAG 拓扑就绪检查（上游回执齐全才入队）；`depends_on` 支持跨期（"每周五调仓依赖本周每日数据任务"）
- **异常处理**：失败退避（巡检/修复类指数退避）、告警去重（同类未处理事件不重复推送）

### 5.4 记忆与经验技能（主候选：SEPM+CALM 双主线，2026-11-01 修订）

- **Run 收尾记忆蒸馏**：每期结束由模型生成"本期执行摘要+关键教训"，写 `work_summary` facts（memory 插件 MySQL ngram 全文索引，中文友好）+ `goal_memory_digest` 表——**产物格式采 HaMo 经验卡三元组**（goal / 初始条件 / 策略级大纲），策略级大纲适配 16KB 注入，且"存一套用一套"：沉淀格式与注入格式统一
- **记忆生命周期（CALM 裁剪，确定性状态机）**：`CANDIDATE → ACTIVE → STABLE → SUPERSEDED / STALE → ARCHIVED`，迁移走白名单、非法迁移拒绝、不靠 LLM 重写全文；**supersede 不物理删除**（置 SUPERSEDED + `superseded_by` 指针，历史回放需旧记忆重构当时决策）；**TTL 第二触发通道**（金融域改造采纳）：显式 `valid_until` 到期 → STALE——行情/持仓类事实不适用"时间流逝不致 stale"，须显式有效期
- **晋升必须可计算判据**（不靠 LLM 拍板）：前置 HaMo retrieval-coverage + 主 gate SEPM reproduction（≥1 次复现 trial、trial 平均效用≥0、因果一致性≥0.65）；任一不过即拦截，拦截原因逐项落 `goal_event` 审计。**参数出处注明**：coverage 阈值（demo 实例化为 ≥0.30）是本项目自设参数、实现可调——HaMo 原文机制为互补边际覆盖贪心选择 + knee point 定预算，并无固定阈值。**简化项**：SEPM 原文同批的 safety/state-verification 两道 gate 未纳入——金融域 state 验证由回测/数据校验工具承担，safety gate 留平台侧设计时补
- **16KB 组装顺序**：见 §5.1 有界摘要协议四步（gate 先于 packing、挤出≠拒绝）；实证见 [w2-memory-distillation-demo](../research-demos/w2-memory-distillation-demo/README.md)（12 定点测试 + 交互剧本）
- **经验技能隐式沉淀**：同类任务重复稳定后蒸馏为可复用技能，**存 goal 插件自有存储（目标私有），运行时装载进该目标的 Run material，版本+哈希随 Run 冻结**——不走 SkillHub 送审、不进技能库、不进通用选择目录，形态同 agent-management / application-management 的内部技能；晋升须过本节可计算 gate，不因"模型觉得有用"直接沉淀
- 风险项不变：SEPM/CALM 均在文本环境（ALFWorld/WebArena/LongMemEval）验证，金融代码任务迁移性以 demo 实测为准，不以论文结论代替；AWM workflow 归纳迁移性 spike 拆 W3+（需真实 T1 轨迹），见 [W2 文献笔记 §5](literature/W2-context-memory-distillation.md)

> 修订留痕（2026-11-01，@dev）：主候选由 AWM/ExpeL 升级为 SEPM+CALM 双主线 + HaMo 格式——依据 [decisions/0003](decisions/0003-w2-memory-distillation.md)（已采纳，含 @research 文献复核与 coverage 阈值实例化校准、safety/state gate 简化项备查两条）+ [literature/W2](literature/W2-context-memory-distillation.md)。

### 5.5 治理：权限、预算、审批、控制

| 能力 | 设计 |
|---|---|
| 权限 | Goal 归属 owner+租户（+团队，对齐 ACL user/team grantee）；受管 Run actor claims 走平台 managed_run 契约；所有工具读写经服务端校验 goal 所有权 |
| 预算 | `budget_json`：token 上限/单期与总预算/最长运行天数；每期 Run 前查余量，耗尽→`budget_exhausted`（走完当前期，不硬切断） |
| 审批门 | 三类：**计划审批**（planning→running 必经）、**应用审批**（P2 新策略上线）、**敏感操作审批**（工具级 `goal_request_approval`，挂起 Run、审批后同一 Run 继续）；未决审批自动挂起对应任务 |
| 控制 | pause（当前期完成后暂停）/ resume（从下一未完成任务继续）/ terminate（终止排队任务+终态）——全部是状态机显式转换，写 GoalEvent 审计 |

### 5.6 vnpy 集成（quant-research）

- 沙箱内 `pip install vnpy`（核心包轻量，不含 UI/gateway；生产镜像已有内网 pypi 代理链路）
- `GoalStrategyBase` **薄封装**：`parameters`/`variables` 白名单 + `on_bar` 回调 + `buy/sell/short/cover` 模拟下单——控制模型面对的 API 面，不让模型重新发明模板
- 数据链路：行情适配器（akshare/tushare/内部行情）→ Datafeed 适配器 → vnpy BarData → 回测引擎；日线缓存落任务文件存储（S3 权威）
- A股 profile 封装复权/涨跌停/T+1 约束进回测配置；市场无关架构留美股 profile 位
- 测评统计：vnpy 回测 statistics（收益/回撤/夏普/盈亏比/成本）直接采集 + 平台侧统一口径补充（成本拖累、信号有效性）
- 回测与模拟盘复用同一策略类（vnpy `get_engine_type` 分支）——模拟→实盘零改码的结构保证

---

## 6. Phase 2：测评体系与策略自主优化闭环

### 6.1 测评快照（GoalEvaluation）

每周期（周度/月度，trading_day 调度）产出**不可变快照**：

```
GoalEvaluation {
  strategy_version, period, eval_kind: backtest | paper | benchmark | oos,
  metrics: {
    returns, max_drawdown, volatility, sharpe, win_rate,
    turnover, cost_drag,           # 交易成本拖累（平台统一口径）
    signal_hit_rate, signal_lead,  # 信号有效性（命中率/提前量）
    benchmark_relative             # 相对基准超额
  },
  verdict_per_metric: {met / below / above},   # 对照 goal_strategy 评价指标定义
  deviation_analysis,                # 模型生成的偏差归因
  evidence: [回测报告 artifact, 净值曲线 artifact, 交易明细]   # 复用资产注册表 evidence citations
}
```

四种 `eval_kind` 对应 mission 四项：**历史回测**（vnpy 滚动窗口）、**模拟跟踪**（paper：当日信号次日开盘价模拟成交、实盘数据回流）、**基准对比**（同窗口持有基准/等权组合）、**样本外验证**（holdout 窗口，oos 权重高于 backtest——防过拟合是测评可信度关键）。

### 6.2 策略迭代循环（RD-Agent RDLoop 落地）

```
                ┌────────────────────────────────────────────┐
                ↓                                            │
  ①propose: 测评快照+偏差分析+历史实验摘要 → 改进假设        │
     (每条: 动机/预期改善指标/改动范围/风险)                  │
                ↓                                            │
  ①b 反方评审（A3）: 挑刺智能体出具反对意见存档              │ 失败→生成修复任务
                ↓                                            │ 重进循环，不终止
  ②coding: StrategyVersion v(n+1)                          │
     (parent=v(n)，代码+S3 artifact+变更说明)                │
                ↓                                            │
  ③running: vnpy 回测 + 样本外验证 + 影子并行（A1，若启用）   │
                ↓                                            │
  ④feedback: 新旧快照对比（A2 过拟合防御 gate 在此强制）      │
     (改善=加权分提升；劣化/持平=否决并归档)                  │
                ↓                                            │
  ⑤decide: 授权范围内? ──是→ 自动应用(激活新版本)            │
            └─否→ 审批门: 人工批准/拒绝/要求更多验证 ──────────┘
```

- `goal_experiment` 记录全程（假设→版本→结果→反方意见→结论→决策），工作台完整展示决策依据
- **失败跳 feedback**：回测报错生成修复任务重进循环，连续失败升级人工
- **版本链与回退**：`candidate → (auto|approved) → active → rolled_back`；激活/回退都是 GoalEvent 审计事件；模拟跟踪劣化可一键回退上任 active 版本
- **终态判定**（引擎钩子 + profile 判据）：`achieved`（指标连续达标+完成声明）/ `stalled`（连续 N 期无改善，默认 3）/ `budget_exhausted` / `risk_triggered`（回撤超约束、单期亏损超限等）——stalled/风险触发自动 `paused` 并请求人工介入

---

## 7. 目标工作台 UI

两个贡献面（`site.navigation` 资源中心入口 + `conversation.view` sidepanel）：

**工作台页面**：目标列表（健康分/状态/预算/下一执行时点）→ 目标详情四区：

| 区 | 内容 |
|---|---|
| 执行计划 | DAG 时间线（甘特/依赖图），任务状态着色，下期调度预览 |
| 运行结果 | GoalRun 列表 → 回执详情（产物预览、指标快照卡、`outcome_unknown` 醒目标记） |
| 策略演进（P2） | 策略进化树（A5：节点染色，悬停看假设+证据+反方意见）、新旧对比雷达/折线、实验记录 |
| 历史与事件 | GoalEvent 时间线（恢复/审批/异常全审计，支持回放"当时看到什么数据、依据什么标准"） |

**对话面板**：交互会话侧栏显示关联目标的实时状态卡片，点击跳工作台；对话里改目标，面板即时反映。对话问询（"最近为什么表现差？"）由智能体调取测评快照归因作答。

---

## 8. 创新功能（已确认 A 组全部纳入；A6/A8 可做简化版）

| # | 创新 | 说明 | 阶段 |
|---|---|---|---|
| A1 | **影子策略并行模拟（shadow mode）** | 新版本与现任版本在同一模拟盘并行 2–4 周，工作台并排净值曲线，分歧收敛后审批切换 | P2 |
| A2 | **过拟合防御强制门** | 样本外/走查验证、参数数÷样本量比、参数邻域扰动（±20% 网格找性能悬崖）、**试验账本 + Deflated Sharpe（按有效试验数去膨胀）+ PBO/CSCV**（文献依据见 §12.1 W6），做成**引擎强制 gate**而非提示词建议 | P2 |
| A3 | **反方评审智能体** | 循环中"挑刺"角色：专查过拟合嫌疑、数据窥探、幸存者偏差，反对意见随实验存档 | P2 |
| A4 | **市场状态（regime）分桶测评** | 按趋势/震荡/高波动分桶统计——"趋势市赚、震荡市亏"归因直接驱动假设生成 | P2 |
| A5 | **策略进化树** | 版本树可视化，改善绿/劣化红/否决灰，悬停看假设+证据 | P2 |
| A6 | **目标健康分** | 预算消耗+指标达成+迭代效率+风险余量合成单一分数与趋势 | P2（简化版） |
| A7 | **周期报告自动生成 + IM 推送** | 周报/月报经 channel 插件推飞书 | P1 即可做推送骨架 |
| A8 | **因子/信号沉淀库** | 有效信号进入目标私有因子库（附 IC/IR 证据），后续策略引用；租户级共享需审批 | P2（简化版） |
| — | **记忆蒸馏+经验技能隐式沉淀** | 越用越懂自己的目标；技能目标私有、不污染技能库 | P1 |
| — | **不确定结果不隐藏重试** | 金融级执行安全（openmuse + 平台 Runtime 语义同构） | P1 |
| — | **失败即修复的韧性循环** | 服务重启/任务失败/代码报错都不中断长期目标 | P1 |
| — | **市场无关引擎+领域 profile** | 换市场/换领域只需新 profile 插件 | P1 架构位 |

**B 组远期路线图**（写入文档，不占 10 周）：多臂老虎机实验预算分配；增量回测；信号漂移检测（PSI）；风险瓶塞（连续回撤自动降仓、恢复后渐进放大）；多策略组合目标（相关性矩阵+权重再平衡）；实盘 Gateway 适配器（vnpy 双引擎同构预留）。

---

## 9. 示例策略模板（用户 30 分钟看懂产品）

每个模板 = 预置 Goal 模板（目标描述+初始策略代码 v1+评价指标+调度规则），是 quant-research 插件内置资产，**一键创建目标跑通全流程**。

### T1 双均线择时（最短路径入门）

| 项 | 内容 |
|---|---|
| 逻辑 | MA5/20 金叉买入、死叉卖出，单标的（沪深300ETF 510300），日线 |
| 演示 | 目标→生成代码→vnpy 回测→日报定时任务→模拟盘，全流程最短路径 |
| 内置迭代空间 | v1 故意在震荡市频繁假信号 → 优化假设：加 MA60 趋势过滤 / ATR 止损 |

### T2 ETF 动量轮动（Phase 1 主演示模板）

| 项 | 内容 |
|---|---|
| 逻辑 | 每周五收盘按 20 日动量持有最强 3/5 只 ETF（股票/国债/黄金/原油类） |
| 演示 | **多标的+周度 trading_day 调度+组合权重**；周期任务与依赖的样板 |
| 内置迭代空间 | 动量窗口 20→10、加回撤止损、持仓数调整；预期真实改善 |

### T3 网格交易（regime 互补对照）

| 项 | 内容 |
|---|---|
| 逻辑 | ETF 跌 2% 买一格、涨 2% 卖一格，区间网格 |
| 演示 | 与 T2 形成 **regime 对照**（震荡市 T3 优、趋势市 T2 优，A4 的天然素材） |
| 内置迭代空间 | 演示"优化无效→保留原策略"和"回撤超限→风险触发暂停" |

### T4 经典海龟策略（完整交易系统，新增）

| 项 | 内容 |
|---|---|
| 逻辑 | 唐奇安通道 20 日突破入场（系统一）；**ATR 头寸管理**：Unit=1% 账户风险/(ATR×乘数)，2N 止损，每上涨 0.5N 加一单位（上限 4 单位），10 日反向突破离场；demo 简化为 4–8 只流动性 ETF 日线 |
| 演示 | **策略≠信号**：资金管理（头寸规模/止损/金字塔加仓）进策略——vnpy 官方有海龟示例先例，评委认知成本低 |
| 内置迭代空间 | 入场通道 20→55、N 周期、加仓单位数、趋势过滤；**参数多 → 天然演示 A2 参数敏感性与过拟合防御**；高波动回撤 → 天然演示风险触发与自动降仓/回退 |

### 演示剧本

**第一次汇报（Phase 1，W5）**：提交 T2 目标（一句话+约束）→ 审批计划 v1 → 智能体写代码、vnpy 回测出报告 → 建每周五调仓定时任务 → 模拟盘持续交付 3 期 → **故障注入三连**：改坏代码（失败修复）、重启服务（状态恢复）、"把回撤容忍从 15% 改到 10%"（重规划 v2 并审批）。

**第二次汇报（Phase 2，W10）**：同一目标继续——周测评报告 → 假设"动量窗口缩短" → 反方评审 → 影子并行 2 周 → 进化树+对比雷达 → 审批应用 → 后续回测触发风险约束 → 自动降仓+一键回退 → GoalEvent 时间线全程回放。T3/T4 备用：优化无效保留原策略（T3）、过拟合 gate 拦截脆弱参数（T4）。

---

## 10. 数据模型、迁移与部署

- 全部新表归两个插件 `migrations/` 自管（Cordis 插件自管迁移），前缀 `goal_` / `quant_`，带租户边界列
- MySQL 8：无外键/CHECK/触发器；关系字段显式索引；关键查询过 `EXPLAIN` 门禁；迁移前核对实库结构
- 大对象（代码版本、回测报告、净值曲线）走平台 Artifact/S3（权威源）；本地文件仅缓存
- 镜像同步检查：核对 `docker/Dockerfile*` 受影响角色；插件及其 `package.json`/lib 产物进镜像；容器内验证插件注册与服务启动；记录核对依据
- 无新增部署必填环境变量/密钥/人工步骤（复用现有 Secret Store 与调度基建）——遵循"禁止随意增加部署复杂度"

**前端**：两仓（frontend + frontend-react）都要适配贡献点；插件必须走 `src` 别名导入（既有迁移缺口教训）；lib 产物与源码同提交。

---

## 11. 与平台边界的合规对照

| pluginization 要求 | 满足方式 |
|---|---|
| 一个插件一项能力 | goal-agent=通用目标引擎；quant-research=金融领域层 |
| 不引用其他插件内部源码 | 只消费 market-research 公开导出（MarketDataProvider 协议、chart 组件）与平台公开贡献点 |
| 禁用即停 | 调度任务/工具/页面/API 均随 Cordis 注册生命周期，禁用后停止注册与执行 |
| 卸载保留业务数据 | goal_* 表数据默认保留 |
| UI 融入主体 | 使用平台设计 Token、Slot 挂载，不造第二套导航 |
| 状态权威源 | 目标/计划/回执/版本全部 DB 权威；产物 S3 权威；无 local-first fallback |
| 不新增第二套执行内核 | 执行全部走 DSH 受管 Run；RDLoop 是状态机+执行协议，不是新引擎 |
| 权限复用 | owner/租户/团队 + managed_run actor claims + 现有审批语义 |

---

## 12. 里程碑映射（研究-设计-开发交替循环，两阶段 10 周）

### 12.0 工作方式说明

10 周不是纯线性开发：每个模块按 **研究（Spike）→ 细化设计 → 开发实现** 交替推进。约定：

- **研究以独立 demo 为主体**：对一个模块或主题写最小可运行 demo 来建立理解（如"沙箱里 vnpy 能不能装、跑多快""双 worker 抢占调度怎么表现"），demo 跑通即获得该模块的设计依据。
- **demo 位置**：研究 demo 是临时产物，放本地 scratch 目录（如 `~/Desktop/goal-agent-research/<主题>/`），**不进生产插件包**；结论沉淀为一页决策记录（写入本文档附录或 `docs/` 专项目录）+ 必要的定点测试。
- **细化设计的触发**：研究 demo 揭示接口形状/约束后，回到本文档修订对应章节（领域模型、协议 schema、UI 交互），再进入开发；研究结论推翻本文档假设时**显式更新文档**而不是默默绕过。
- **每周研究 = demo + 文献**：每个研究主题除写 demo 外，必须**按主题检索最新论文**（arXiv/ACM/KDD/NeurIPS/ICML/WWW 等，优先近 12–18 个月），产出一页《文献笔记》：①检索式与日期 ②3–5 篇入选论文（一句话贡献+与本项目的关系）③**方向结论**（采纳/改造/不采纳及理由）④对本文档哪一节的修订。文献笔记与 demo 决策记录同目录归档，未读原文的论文只能标注"仅摘要级"，不得当作已验证结论引用。具体各周主题、检索式与候选方向见 §12.1。
- **每个里程碑周完成时自查**：本周研究项是否都有 demo 证据或决策记录？**是否有文献笔记与方向结论？**本周开发是否有可失败测试先行？

**Phase 1（W1–5）**

| 周 | 开发交付 | 研究 / Spike（独立 demo） | 细化设计产出 |
|---|---|---|---|
| W1 | 插件脚手架×2；goal 领域模型+状态机+迁移；基础 CRUD API | 精读 `workspace-automation` 调度层源码；demo：模拟双 worker 抢占 + 进程崩溃后 recovery 扫描恢复 | goal_* 表结构定稿；**状态机全转换表**（状态×事件→动作，含异常路径）；profile 契约字段定稿 |
| W2 | 执行协议：turn_context 组装、goal 工具组、幂等回执、记忆蒸馏；对接调度 | demo①：最小插件贡献 `agent.turn_context`，验证 16KB 上限与轨迹 CONTEXT 呈现；demo②：手动触发最小受管 Run 走通 managed_run 契约与 actor claims 冻结 | turn_context 摘要组装协议（放什么/优先级/截断规则）；工具清单与授权矩阵；回执 schema |
| W3 | 交易日历+`trading_day` 调度；DAG 依赖；异常处理+恢复扫描；vnpy 集成 | **（最高风险研究）**demo①：目标环境/沙箱内行情数据源可达性（akshare/tushare/内部行情），拉取指定 ETF 日线落缓存；demo②：干净容器 pip install vnpy + 最小回测跑通，测量依赖体积与耗时；demo③：GoalStrategyBase 最小子集封装，双均线策略出标准统计 | Datafeed 适配器协议定稿；日历数据来源与刷新策略；回测超时与拆批策略（依 demo② 实测）；GoalStrategyBase 接口文档 |
| W4 | 治理（审批门/预算/pause/resume/terminate）；T1/T2 模板；工作台（列表/详情/计划/运行结果） | 验证受管 Run 场景下审批挂起-恢复语义（平台既有规则是"unattended clarification 显式失败"，需确认 `goal_request_approval` 的挂起路径）；小 demo：双前端仓贡献点适配（沿用 skill-lab 先例） | 工作台四区信息架构（线框级）；审批门交互流程；预算字段口径定义；T1/T2 模板内容定稿 |
| W5 | T3/T4 模板；周期报告推送骨架（A7）；故障演练集成验收；**第一次汇报** | 故障注入演练脚本设计（改坏代码/重启/改目标三条路径的验证清单）；演示数据固定化方案（固定窗口与 seed，防现场翻车） | 演示剧本逐句排练稿；Phase 2 范围复核（依 Phase 1 实际进度裁剪 A6/A8 简化幅度） |

> 注：多智能体群组配合交互为 2026-11-01 增补的 W1–W5 增量研究线，每周一个子主题挂靠当周既有主题，不增删本周交付，见 §12.2。

**Phase 2（W6–10）**

| 周 | 开发交付 | 研究 / Spike（独立 demo） | 细化设计产出 |
|---|---|---|---|
| W6 | GoalEvaluation 测评体系（四类 eval、快照与证据链） | demo①：用 T1 回测产出全指标快照 JSON，校准 vnpy statistics ↔ mission 指标 ↔ 平台统一口径（cost_drag/信号有效性）的计算定义；demo②：walk-forward 滚动窗口脚本验证样本外切分方法 | GoalEvaluation schema 定稿；指标口径表（公式+数据来源+边界条件）；证据链与资产注册表对接方式 |
| W7 | 迭代循环（propose/coding/running/feedback/decide）；StrategyVersion 链；实验记录 | 精读 RD-Agent feedback 上下文构造；demo：历史实验摘要注入 propose 的提示词原型，用 T2 假数据试跑一轮假循环 | 实验记录 schema；**迭代循环各步的输入/输出提示词协议**（propose/反方/coding/feedback 各轮契约） |
| W8 | 审批应用/回退；影子模式（A1）；过拟合防御 gate（A2）；反方评审（A3） | demo①：vnpy 同一模拟盘并行跑两个策略实例的记账方案（shadow 的核心可行性）；demo②：T4 参数 ±20% 扰动网格的算力耗时测量，定网格密度 | 影子模式的调度与对比展示设计；gate 判定阈值（参数数/样本量比、悬崖判定）；反方评审输出 schema |
| W9 | 进化树+对比 UI（A5）；regime 分桶（A4）；健康分（A6 简化）；因子库（A8 简化）；终态判定 | 小 demo：进化树可视化组件选型（现有图表库可行性）；用 T3 调参标定 stalled/risk 终态阈值合理性 | 健康分公式；因子库 schema（IC/IR 证据字段）；终态判定阈值定稿 |
| W10 | 全链路验收、可复现验证、历史回放演示；**第二次汇报** | 可复现验证方法研究：同一目标重放清单、证据完整性校验（回执+快照+代码版本哈希对账） | 可复现性验证报告模板；项目复盘与后续路线图更新 |

### 12.1 各周文献研究主题与方向建议

> 检索日期 2026-10-29。"已读摘要"= 仅阅读检索结果摘要/片段，**尚未精读全文**；每周研究时需精读入选论文并更新文献笔记。无法确认的论文编号不写入。方向结论是**初步建议**，由各周 demo+精读验证后定稿。

| 周   | 研究主题                   | 建议检索式                                                                                                | 候选论文（已读摘要）                                                                                                                                                                                                                                                                                                                                                                                | 初步方向建议（落到本方案哪里）                                                                                                                                                                                                                                                                                                                                                                                    |
| --- | ---------------------- | ---------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| W1  | 长程任务的持久化调度与恢复          | `durable execution LLM agent checkpoint recovery`、`long-running agent reliability`                   | 2026-11-01 补检（已精读 4 篇，见 [literature/W1](literature/W1-durable-scheduling-recovery.md)）：**Resume Means Resume**（[2608.03836](https://arxiv.org/abs/2608.03836)）：机器可查的 checkpoint/resume 契约（6 性质+fork-intent+liveness），实测 LangGraph/CrewAI 等 5 框架全部部分违约；**AgentRewind**（[2608.14380](https://arxiv.org/abs/2608.14380)）：决策边界对齐 checkpoint+日志回放，成对恢复率 8.0%→30.0%；**Same Winners, Different Success Rates**（[2609.34215](https://arxiv.org/abs/2609.34215)）：set-agreement 指标掩盖近零恢复率，提出 4 量诊断口径；**CUA-Recovery**（[2610.27645](https://arxiv.org/abs/2610.27645)）：takeover-depth 梯度注入恢复基准，最强模型 Pass@3≤25.5%、检测≠修复 | ① 恢复语义采纳 6 性质+FI+liveness 作状态机验收清单：恢复决策=DB 状态纯函数、**审批门 CAS 式消费一次**、写入时 schema loud reject、resume 带 retry/fork 判别位 ② 自建外部 effect ledger 作恢复正确性第二 oracle（框架内部状态不可信，实测有框架显示正确而外部 ledger 显示重复）③ W5 演练口径固定报 4 量（agreement/all-zero fraction/held-out success/pooled success）+ (goal_run, step, action) provenance 绑定 ④ 故障注入用 takeover-depth 梯度设计 ⑤ §12.2 群组持久化结论（[decisions/0002](decisions/0002-w1-recovery-semantics.md) 第 5 条，demo 场景 C 实证）：**语义统一、锚点独立**——群组消息不挂 goal_run（会话横跨多次期次 Run），但复用同一套 consume-once/幂等追加/fencing 语义，`goal_event.actor_agent_id` 归因 |
| W2  | 长程上下文管理、记忆蒸馏、经验→技能     | `Agent Workflow Memory`、`ExpeL`、`procedural memory agent skills survey`                              | 2026-11-01 增补精读 4 篇（见 [literature/W2](literature/W2-context-memory-distillation.md)）：**SEPM**（[2610.14515](https://arxiv.org/abs/2610.14515)）：task DAG 作多智能体协作记忆接口，五道 gate 晋升+CAS 版本化，显式图换文本 SOP 掉 17pp；**HaMo**（[2610.34724](https://arxiv.org/abs/2610.34724)）：经验卡三元组+retrieval-coverage 晋升判据；**CALM**（[2610.38573](https://arxiv.org/abs/2610.38573)）：记忆生命周期状态机+supersede 不删+查询准入 gate；**SPEM**（[2610.26995](https://arxiv.org/abs/2610.26995)，仅摘要级）。既有候选 **AWM**（Wang 等，ICML 2025，arXiv 2409.07429）：从轨迹归纳可复用 workflow 并按需注入，Mind2Web/WebArena 相对成功率提升 24.6%/51.1%；**ExpeL**（2308.10144）：无参数更新地提炼自然语言经验；**Agent Skills Survey**（过程记忆视角）与 **SoK: Agentic Skills**（获取/表示/调用/精炼框架）                                                                                                                                                                     | ① §5.4 记忆蒸馏改用 **AWM 式"workflow 归纳"**：不只存摘要，而是从成功 Run 轨迹归纳"可复用步骤序列"，下期按相似度选择性注入 ② 经验技能沉淀采用 survey 的四环节（获取/表示/调用/精炼），**精炼环节必须带版本+哈希冻结**（与现设计一致）③ 风险：AWM 在网页导航验证，**金融代码任务迁移性未知**，W2 demo 需用 T1 轨迹实测                                                                                                                                                                                                   |
| W3  | LLM 生成量化回测代码的可靠性、前视偏差 | `LLM automated quantitative backtesting benchmark`、`look-ahead bias LLM finance`；2026-11-10 补检追加 `all:"backtest" AND all:"LLM"`、`all:"look-ahead bias" AND all:"LLM"`、`all:"quantitative trading" AND all:"LLM agent"`、`all:"trading strategy" AND all:"large language model"` | 2026-11-10 入选 8 篇（7 篇全文精读，见 [literature/W3](literature/W3-backtest-reliability.md)）。原三候选升级精读：**BacktestBench**（[2605.17937](https://arxiv.org/abs/2605.17937)，KDD 2026）18,246 题+标准化回测协议（T-1 信号、双盲 KPI、<1e-3 判分），但其 look-ahead 约束只在 prompt；**Look-Ahead-Bench**（[2601.13770](https://arxiv.org/abs/2601.13770)）双时段 alpha 衰减：DeepSeek 3.2 P1 alpha +20.73pp→衰减 −21.77pp，PiT 模型稳定；**What survives**（[2608.27734](https://arxiv.org/abs/2608.27734)）升级全文：注册表使前视不可表达+单入口试验账本喂 DSR/PBO，泄漏 oracle（design SR 34.7）DSR 仍 1.00 只有结构护栏能拦。新入选：**MintEval**（[2610.03080](https://arxiv.org/abs/2610.03080)）行为等价逐 bar 比对，读码 judge 放行 Opus 5.5 全部 0.275 静默失败；**QuantHarness**（[2610.26101](https://arxiv.org/abs/2610.26101)）三边界 harness+FinRelBench 97 任务 90.72%，budget ledger ≤3+1、final 不回流；**Hard to Fool**（[2611.06607](https://arxiv.org/abs/2611.06607)）约 24 campaign 仅 2 幸存，绝对门合取+单次 holdout receipt+哈希链账本（Sharpe 2.94→0.26）；**FinCutBench**（[2611.11588](https://arxiv.org/abs/2611.11588)）9,000 题月度知识剖面测实测边界（GPT-5.6-Sol 披露 2026-02-16 实测 Boundary 2026-06）；仅摘要级 When Alpha Disappears（[2605.23959](https://arxiv.org/abs/2605.23959)，one-switch Leakage Gain 消融） | ① **前视构造性防护三层加固**（§5.6）：API 面只暴露截至当前 bar+数据 registry flag 使前视不可表达+回调前入 buffer 越界抛错——prompt 约束为零防线（BacktestBench 反例）② **试验账本单入口**（§8 A2/§6.1）：单一 evaluation entry point 构造性完整，DSR 的 N/V 从账本读、CSCV 列数=N 不变式；**三仪器齐算**——E3 案例 PBO 0.01 仍样本外崩，PBO 低不豁免 held-out CI ③ **回测验收用行为等价不读码**（§6.1）：逐 bar 动作比对+KPI <1e-3 容差；指标计算统一走 quant-research 指标库 ④ **样本外窗口起点升级为实测知识边界**：vendor 披露 vs 实测 FinCut Boundary 差可达约 4 个月，Wide/ND 模型取更晚起点或弃用 ⑤ **门禁合取+预算化选型**（§8 A2）：绝对门合取（成本后 edge/bootstrap 下界/抬成本存活/逐年稳定/样本地板）、≤3 次优化+1 次 final 不回流、repair AST guard；改造：Hard to Fool 声明式词表与「LLM 生成代码」冲突→改为代码须实现声明式 spec+行为等价校验；不采纳：单分数验收与把 Leakage Gain 当认证 |
| W4  | 审批/人在回路与授权边界 | `human-in-the-loop approval LLM agent autonomy levels`（2026-10-29 首轮无结果）；2026-11-10 补检追加 `all:"human-in-the-loop" AND all:"approval" AND all:"agent"`、`all:"LLM agent" AND all:"authorization" AND all:"autonomy"`、`all:"multi-agent" AND all:"permission" AND all:"LLM"` | 2026-11-10 补检成功，入选 4 篇全文精读（见 [literature/W4](literature/W4-hitl-approval-authorization.md)）：**I-HITL**（[2610.35835](https://arxiv.org/abs/2610.35835)）形式化 approval-binding——审批通道必须终止于 agent 不可达的可信实体（plain topology 不可能性 Theorem 4+充要条件 Theorem 7），实测无提示下 9/10 frontier 模型自行读 OTP 提额（仅 opus-5.5 从未尝试）；**Loopjacking**（[2609.21081](https://arxiv.org/abs/2609.21081)）批准的 A≠执行的 B——canonical approval record schema+use-time 五步（material arguments digest 校验→原子消费→审计），Agno 7 release/LangGraph 12 release 全部可复现；**From Approval to Abuse**（[2610.22987](https://arxiv.org/abs/2610.22987)）抗审批疲劳的 allow-rule 被不可信上下文征用——58% 实例诱导出规则、获批后 81.0% 静默达成（47/58），Anthropic 自述 49.5% 活跃用户配过 Bash allow rule；**Permitted but Unauthorized**（[2611.04086](https://arxiv.org/abs/2611.04086)）技术权限≠组织委派——可见性是越界必要条件（12 个 not-listed cell 全 0/52），deterministic reference monitor 使越界 0/40（无防御 Sonnet 4.5 达 27/40） | ① **审批门 use-time 绑定+原子消费**（§5.5/§4.4）：canonical record 绑定 action identity+全部 material arguments+principal/scope+nonce/expiry/consumption；use-time 重建完整操作 diff 即拒绝、原子消费防重放——只绑 call id/只看 approved 标志/只在展示时检查都不够（Loopjacking 实证） ② **审批通道独立于 agent 会话**（§5.5）：审批信号不得进 agent 可读资源（邮箱/同机文件/环境变量），金融动作批准方必须是人（I-HITL 拓扑结论，设备 attestation 细节不照搬） ③ **授权矩阵不可变上限+提议来源约束**（§12.2 W4）：读不可信内容前设 immutable ceiling；allow-rule 提议不得源自不可信上下文、须绑 goal scope 与过期——新增「agent 不得经 harness 自扩权」规则 ④ **矩阵在模型之下强制+委派记录唯一权威**（§12.2 W4）：runtime deterministic monitor 强制、ownership 取自 versioned delegation record、peer 动作不入成员候选动作空间（表示层规则即可把越界压到 0）、对 self-report 做 effect 校验；改造：I-HITL strong 形态按金融取强口径但不照搬设备方案；不采纳：小模型 pre-execution judge 作唯一防线（judge 臂仍有 severity misreport） |
| W5  | 金融 agent 的真实评测与故障/风格差异 | `live trading benchmark LLM agent`、`Agent Market Arena`                                              | **LiveTradeBench**（2511.03628）：50 天实时评估 21 个 LLM，**高通用榜单分不等于交易表现**；**Agent Market Arena**（WWW 2026）：agent 框架对行为的影响大于底座模型；**Strat-LLM**（2605.06024）：A 股/美股 2025 live-forward，规则约束强度的效用**随市场状态变化**，标准模型陷入"高胜率陷阱"                                                                                                                                                                            | ① 汇报演示坚持**固定窗口+模拟盘 T+1 前向跟踪**（对应文献"live-forward 才可信"）② 不宣称"跑赢市场"，汇报口径为**流程可靠+证据完整** ③ 评价指标不能只看胜率（高胜率陷阱）：§6.1 指标必须同时含收益/回撤/成本拖累 ④ "严格/引导/自由"授权档位可借鉴为 Goal 的**策略修改权限档位**（只调参 / 可改逻辑 / 可改代码）                                                                                                                                                                                                          |
| W6  | 策略测评口径与统计显著性           | `Deflated Sharpe Ratio`、`probability of backtest overfitting CSCV`、`walk-forward`                    | **Bailey & López de Prado：DSR/PBO**（经典方法）；**What survives honest evaluation?**（2608.27734）：记录**每一次**候选评估（试验账本）并按试验数 N 对 Sharpe 去膨胀，实验中其测试的 LLM 发现策略均未通过诚实评估；**Effective Trial Counts for LLM-Proposed Backtests**（System report，2026-07）：LLM 候选高度相关，原始提案数高估独立试验数，用收益相关矩阵特征值估计有效试验数 M_eff；开源工具 **oos-lab**（PSR/DSR/PBO/walk-forward/Harvey-Liu haircut）可作参照                                | ① **GoalEvaluation 新增必填字段：**`trial_count`**、**`effective_trials`**、**`psr`**、**`dsr`；② 新增**试验账本**（见 §4.4 补充）：所有 propose→回测都入账，**测评永远基于全量账本**而非"最优那一次" ③ A2 过拟合 gate 升级为：样本外 + DSR + PBO/CSCV + 参数邻域扰动四项（§8）④ oos-lab 仅作**公式对拍参照**，是否引入依赖由 W6 demo 评估（小型独立项目，需核对许可与维护状态后再决定，默认自实现）                                                                                                                  |
| W7  | LLM 驱动的研究迭代循环          | `R&D-Agent-Quant`、`QuantAgent self-improving`、`Alpha-GPT`、`AlphaEvolve`、`hypothesis tree refinement` | **RD-Agent(Q)**（2505.15155，NeurIPS 2025）：Research/Development/Feedback 循环，**Co-STEER**（任务 DAG+失败案例知识库检索）与**多臂老虎机方向调度**，相对经典因子库约 2 倍年化、少 70% 因子；**QuantAgent**（2402.03755）：内循环用知识库精炼、**外循环用真实场景检验回灌知识库**；**Alpha-GPT**（2308.00016）：ideation→implementation→review，人机交互；**AlphaEvolve**（2506.13131）：LLM 产生代码 diff + 自动评测 + 程序数据库的进化；**Arbor/HTR**（2606.11926）：持久化假设树，关联假设/产物/证据/保留集验证（已读摘要） | ① 迭代循环保持 RDLoop 骨架（§6.2）② **新增"程序数据库"思想**：策略版本链记录 parent+评测快照，propose 时按"高分+多样性"采样历史版本做上下文（AlphaEvolve/DGM 的 archive 思路），避免只看最近一次 ③ **假设树**：`goal_experiment` 增加 `parent_experiment` 与 `hypothesis_class`（参数/过滤/风控/信号四类），为进化树（A5）与老虎机预算（B 组）提供数据基础 ④ QuantAgent 的"外循环=真实结果回灌"对应我们的**模拟盘跟踪结果回流 propose**，保证优化依据不止回测 ⑤ **不采纳**：DGM 式"agent 自改自身代码"——超出授权边界且无法满足金融审批要求，仅学习其"每次修改必须经实证验证+沙箱+人工监督"的安全做法 |
| W8  | 影子并行、反方评审、多智能体辩论       | `TradingAgents`、`multi-agent debate trading`、`alpha decay regularized exploration`                   | **TradingAgents**（2412.20138）：Bull/Bear 研究员辩论 + 风控团队 + 交易员综合，报告累计收益/夏普/回撤改善（已读摘要，注意其评测窗口与真实性需精读核实）；**AlphaAgent**（Tang 等，KDD 2025，"regularized exploration to counteract alpha decay"，仅见引用条目，**需精读确认**）；**FinAgent**（2402.18485）：工具增强+双层反思+多样化记忆检索                                                                                                                                        | ① 反方评审（A3）采用 TradingAgents 的 Bull/Bear 对抗结构，但**评审对象是"策略改动提案"而非"买卖决策"**，输出结构化 schema（过拟合嫌疑/数据窥探/幸存者偏差）② 参考 AlphaAgent 的"对新因子相对已有因子的**原创性/复杂度正则**"，作为 propose 阶段的**去重+复杂度惩罚**（需精读后定稿）③ FinAgent 双层反思 → 执行期反思（本期决策）与周期反思（多期复盘）分层，对应 `goal_memory_digest` 两个粒度                                                                                                                                         |
| W9  | 市场状态（regime）与终态阈值      | `market regime detection LLM agent`、`Strat-LLM regime`、`alpha decay`                                 | Strat-LLM 的 regime 依赖结论（已读摘要）；regime 检测文献**本轮未检索到合格结果，W9 补检**                                                                                                                                                                                                                                                                                                                             | regime 分桶（A4）先用**规则法**（趋势：MA 斜率/ADX；波动：已实现波动分位），不引入 HMM/学习法，除非 W9 文献+demo 证明收益；终态阈值（stalled=3 期）用 T3 实测定标                                                                                                                                                                                                                                                                                          |
| W10 | 可复现与证据完整性              | `reproducibility LLM agent experiments`、`trial ledger audit`                                         | What survives honest evaluation? 的**试验账本全量可审计**思想；其余待补                                                                                                                                                                                                                                                                                                                                    | 可复现验证 = 账本对账：回执+快照+代码哈希+**试验账本条数**四项一致；汇报时给出"试验总数与去膨胀后结论"，比单一最优曲线更可信                                                                                                                                                                                                                                                                                                                               |

**文献研究产出的横向结论（将进入本文档修订）**：

1. **诚实评估是比"提升收益"更重要的卖点**。多篇 2026 工作（What survives honest evaluation?、Effective Trial Counts）指出：LLM 大量试错后挑最优，若不按试验数去膨胀，"优化成功"大概率是选择偏差。→ 本方案已将"优化无效时保留原策略"列为演示场景，应进一步**把试验账本+DSR 作为引擎强制 gate**，并在汇报中主动展示"被拦下的假改善"。
2. **前视防护要在接口层构造性保证**，统计修正不能替代（那篇论文用一个夏普 35 的"泄露预言机"证明它可以通过 DSR/PBO 检验）。→ GoalStrategyBase 只暴露截至当前时点的数据。
3. **研究循环需要结构化持久记忆**：RD-Agent(Q) 的 Co-STEER 知识库、AWM 的 workflow 归纳、AlphaEvolve/DGM 的 archive、Arbor 的假设树，共同指向"**按结构而非按时间顺序**存历史实验"。→ `goal_experiment`/策略版本链按树/archive 组织。
4. **真实前向跟踪优于回测**（LiveTradeBench、AMA、Strat-LLM）：→ 模拟盘跟踪是 P2 的一等公民，不是附属项。
5. **不采纳项**：agent 自改自身框架代码（DGM）、HFT 类（QuantAgent 2509.09995）、多模态 K 线图理解（FinAgent 的图像模块）——与本项目日频、规则型、可审批的目标不符。

**检索工具局限**：本轮部分检索（durable execution、HITL 审批、regime）未返回有效结果，且专业文献库（dataPro）当前订阅不可用，故上表对应项标注"待补"。对应周需重新检索后再定稿，不得以现有结论代替。

### 12.2 多智能体群组配合交互（W1–W5 增量研究线，2026-11-01 增补）

> 状态：草稿（待各周 demo+精读后定稿）。决策依据：[decisions/0001](decisions/0001-multi-agent-group-research-increment.md)。**增量原则**：不改动 §12.0/§12.1 既有各周的开发交付与研究项，仅在 W1–W5 每周**挂靠一个群组协作子主题**（研究/demo 载荷落在同周，共用该周已有的 demo 基建）；W6–W10 不新增子主题，其衔接点为 W8 反方评审（A3）复用 W4 群组治理产出的授权矩阵。检索日期 2026-10-31/11-01，候选论文均**仅摘要级**。

**动机**：mission 要求研究"多智能体群组配合交互"。本项目的目标执行形态（§4.2）是"调度触发的受管 Run"，群组能力不是推翻该形态，而是回答三个问题：①一个目标的执行如何从单受管 Run 扩展为**多角色群组协作**（研究/开发/评审角色分工）；②群组成员间的消息、共享记忆与上下文如何持久化（复用 goal_event/goal_memory_digest 而非另起炉灶）；③群组引入后治理语义（审批/预算/授权）如何归因到成员。

| 周 | 挂靠主题 | 群组子主题 | 候选论文（仅摘要级，含链接） | 落点（增量，不改既有交付） |
|---|---|---|---|---|
| W1 | 持久化调度与恢复 | 群组状态的持久化基座：多 agent 会话/消息是否需要独立于 goal_run 的持久化 | [Multi-Agent Collaboration Mechanisms: A Survey of LLMs](https://arxiv.org/abs/2501.06322)（协作机制可扩展框架）；[Beyond Self-Talk: Communication-Centric Survey of LLM-MAS](https://arxiv.org/abs/2502.14321)（通信视角：架构/协议/消息对象分层） | **已定稿（[decisions/0002](decisions/0002-w1-recovery-semantics.md) 决策 5，w1-recovery-demo 场景 C 实证）**：**语义统一、锚点独立**——群组消息用独立持久化表 `goal_group_message`（session+seq 主键，不挂 goal_run，会话横跨多次期次 Run），但恢复语义与 goal_run 完全一致（consume-once/幂等追加/fencing，不允许第二套恢复语义）；`goal_event.actor_agent_id` 采纳（§4.4 已落） |
| W2 | 长程上下文、记忆蒸馏 | 群组记忆模型：共享记忆 vs 成员私有记忆；成员间消息摘要如何蒸馏 | [AutoGen](https://arxiv.org/abs/2308.08155)（GroupChatManager 选 speaker+广播；对话即编排）；[MetaGPT](https://arxiv.org/abs/2308.00352)（**结构化消息**优于自由对话：publish-subscribe + schema 化产出，降低信息丢失与幻觉级联） | **已定稿（[decisions/0003](decisions/0003-w2-memory-distillation.md) 决策 6，scope/author_agent_id 字段已在 w2 demo 实证）**：① `goal_memory_digest` 增加 `scope`（goal 共享 / 成员私有）与 `author_agent_id` 字段；② scope 语义取 SEPM 程序元数据三元组（applicability / context conditions / exclusions）作 eligible 判据 + CALM 准入 gate；③ 群组 turn_context 组装规则：共享摘要全量注入 + 成员私有摘要按角色选择性注入（复用 §5.1 有界摘要协议与 §5.4 gate/生命周期语义，上限不放宽）；共享 blackboard 只存 verified state、成员私有推理留本地（SEPM：私有推理不减收益） |
| W3 | 回测代码可靠性、DAG | 群组任务分解：角色分工如何映射到 goal_plan_task DAG | [MetaGPT](https://arxiv.org/abs/2308.00352)（SOP 流水线：PM→架构→工程师→QA，角色间以标准化产物交接）；[ChatDev](https://arxiv.org/abs/2307.07924)（phase-based 群组聊天流水线） | `goal_plan_task` 增加可选 `assigned_role`（如 researcher/coder/reviewer）；**默认单角色路径零改动**——不填 assigned_role 即现有单受管 Run 行为，群组是 opt-in |
| W4 | 审批/授权边界 | 群组治理：多成员下的审批归因、预算分摊、权限矩阵 | [MultiAgentBench](https://arxiv.org/abs/2503.01935)（协调/竞争评测，含 Coordination 语义指标，仅摘要级）；[Communication-Centric Survey §5.5](https://arxiv.org/abs/2502.14321)（通信攻击面：成员被注入后经消息污染群组的风险，仅摘要级）；2026-11-10 增补 4 篇全文精读（见 [literature/W4](literature/W4-hitl-approval-authorization.md)）：[I-HITL](https://arxiv.org/abs/2610.35835)、[Loopjacking](https://arxiv.org/abs/2609.21081)、[From Approval to Abuse](https://arxiv.org/abs/2610.22987)、[Permitted but Unauthorized](https://arxiv.org/abs/2611.04086) | ① 审批门记录 `requested_by`（成员归因），群组成员不得绕过审批门互相授权；② 预算按 goal 整体计（不按成员分摊，避免成员间博弈），成员级 token 用量只做观测字段；③ 授权矩阵按"角色×工具"定义，为 W8 反方评审角色（A3）预留 reviewer 角色位；**2026-11-10 增补（W4 文献）**：④ 矩阵由 runtime deterministic monitor 在模型之下强制，ownership 取自 versioned delegation record（不从资源名/推断得来）（[2611.04086](https://arxiv.org/abs/2611.04086) 实测强制后越界 0/40）；⑤ peer 动作及其 payoff 不进入成员候选动作空间（表示层规则即可把越界压到 0，可见性是必要条件）；⑥ allow-rule 类提议不得源自不可信上下文、须绑 goal scope 与过期，矩阵读不可信内容前设 immutable ceiling（[2610.22987](https://arxiv.org/abs/2610.22987)：58% 诱导率、获批后 81.0% 静默达成）；⑦ 对成员 self-report 做 effect 校验（scope 强制 ≠ 无伤害，残余 severity misreport 实测存在） |
| W5 | 故障演练与汇报 | 群组故障注入与最小演示 | 沿用 W1–W4 入选文献，无新增检索（本周主线负载已满）；群组评测方法如需深挖推迟到 W8 与辩论主题合并精读 | 故障演练清单**追加一条**：成员 Run 崩溃/消息丢失时群组不重复执行已完成步骤（幂等回执复用）；汇报演示可选加 30 秒"双角色协作出策略改动提案"片段（不进必演剧本） |

**跨周衔接与明确不做**：

1. **W8 合流**：反方评审（A3）的 Bull/Bear 对抗即群组交互的评审场景，直接复用 W4 的角色×工具授权矩阵与 W2 的结构化消息 schema，不在 W8 重新发明。
2. **不采纳**：动态拓扑学习/MARL 类通信调度（如 [ACTS](https://arxiv.org/abs/2610.25851)、[AMAS](https://arxiv.org/abs/2510.01617) 的自适应拓扑）——与"审批可归因、行为可审计"的金融治理目标冲突，且增加不可预测性；群组拓扑用**静态角色+SOP 固定编排**（MetaGPT/AutoGen 的 group chat 模式）。
3. **规模假设**：群组规模 ≤ 5 成员（研究/开发/评审/汇报），不做大规模 agent 社会仿真类研究——超出本项目"单目标执行协作"的范围。
4. **修订留痕**：本节为增量新增，未触碰 §4 领域模型主表；W1–W4 各周 demo 若证明某字段（actor_agent_id、scope、assigned_role）无必要，删字段即可，不构成对既有设计的推翻。

**验收与测试策略**：每个能力先立可失败测试（后端 pytest 定点、插件契约测试、前端渲染测试）；里程碑以**可运行功能+实际执行记录+验证证据**为据（两次汇报要求同源）；研究 demo 证据与决策记录计入里程碑证据；演示前完成故障注入演练（失败修复/重启恢复/目标调整）与 MySQL EXPLAIN 门禁；不以"历史基线失败"代替结论。

---

## 13. 风险与开放问题

| 风险/开放项 | 影响 | 缓解 |
|---|---|---|
| 生产行情数据源可用性（akshare/tushare 需外网；内网环境待确认） | 数据链路是 demo 命脉 | W1 优先验证：内部行情服务 or 数据落地缓存；market-research 公开行情接口兜底日线 |
| vnpy 在沙箱镜像的依赖安装与体积 | 回测可用性 | 生产镜像已有内网 pypi 代理（pypi-tsinghua）；只装核心包；W3 容器内验证 |
| 受管 Run 的执行时长上限 vs 回测耗时 | 长窗口回测可能超时 | 数据缓存+增量窗口；超长回测拆批；平台 run 超时配置核对 |
| 双前端仓适配工作量 | UI 交付节奏 | 贡献点先行、frontend-react 侧沿用既有 outlet 模式；注意 pnpm lock 漂移（仅刷快照后还原） |
| 模拟盘数据回流的实时性 | paper 跟踪可信度 | 首版 T+1 收盘后批处理回流即可，不做盘中实时 |
| 多目标并发的沙箱/预算争抢 | 资源隔离 | 平台沙箱池既有约束；goal 级预算先于执行检查 |
| stalled/risk 判据的领域合理性 | 终态误判 | 判据全部 profile 化+阈值显式可配，演示前用 T3 调参验证 |

---

## 附：已确认决策记录

1. 插件定位：**通用引擎（goal-agent）+ 金融领域层（quant-research）**，两插件公开契约通信
2. 市场：**市场无关设计 + A股 profile 首发**
3. 执行形态：**方案 B——目标状态机 + 调度触发受管 Run**（turn_context 注入、工具回执）
4. 回测框架：**vnpy**（GoalStrategyBase 薄封装 + 双引擎复用）
5. 记忆：hermes 式蒸馏落 memory facts；**经验技能隐式沉淀目标私有，不走 SkillHub**
6. 创新：A1–A8 全部纳入设计（A6/A8 简化版），B 组为远期路线图
7. 示例策略：T1 双均线 / T2 动量轮动 / T3 网格 / **T4 经典海龟**
8. 文档位置：~~Desktop（用户指定，不进仓库）~~正式开启研究后已进仓库
9. 推进方式：**研究-设计-开发交替循环**；每模块先以独立 demo（本地 scratch，不进生产包）建立理解，研究结论以决策记录+定点测试沉淀，并回写本文档后再开发（见 §12.0）
10. 研究要求：**每周研究主题除 demo 外必须按主题检索最新论文并出文献笔记与方向结论**（见 §12.0/§12.1）；仅读摘要的文献不得当作已验证结论

---

## 附：参考文献（2026-10-29 检索，除标注外均为仅摘要级）

- RD-Agent(Q): *R&D-Agent-Quant*, arXiv 2505.15155（NeurIPS 2025）
- QuantAgent: *Seeking Holy Grail in Trading by Self-Improving LLM*, arXiv 2402.03755
- Alpha-GPT: arXiv 2308.00016；AlphaAgent（KDD 2025，仅见引用）
- FinAgent: arXiv 2402.18485；TradingAgents: arXiv 2412.20138
- BacktestBench: KDD 2026, doi 10.1145/3770855.3817460
- Look-Ahead-Bench: arXiv 2601.13770；What survives honest evaluation?: arXiv 2608.27734
- Effective Trial Counts for LLM-Proposed Backtests（系统报告，非同行评审，2026-07）
- Bailey & López de Prado, Deflated Sharpe Ratio（2014）；Bailey 等, PBO/CSCV
- LiveTradeBench: arXiv 2511.03628；Agent Market Arena（WWW 2026）；Strat-LLM: arXiv 2605.06024
- Agent Workflow Memory: arXiv 2409.07429（ICML 2025）；ExpeL: arXiv 2308.10144；Agent Skills Survey；SoK: Agentic Skills
- AlphaEvolve: arXiv 2506.13131；Darwin Gödel Machine: arXiv 2505.22954；Hypothesis-Tree Refinement: arXiv 2606.11926；KAPSO: arXiv 2601.21526
