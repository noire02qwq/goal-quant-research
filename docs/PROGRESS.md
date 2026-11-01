# 项目进度记录（PROGRESS）

> 状态：活跃维护。每次有实质进展（规范变更、设计修订、研究/demo 完成、阻塞解除）由执行方追加一条记录；本文件只记结论与指针，细节写入对应文档后链接过去。日期为本地日期。

## 当前阶段

Phase 1 W1–W2 进行中（@user 2026-11-01 下令启动循环；harness-hub 平台侧开发待回公司内网）。当前：W1/W2 文献线达标（8 篇 2026H2 论文归档、7 篇精读 + DeepSeek Super-agent 精读）；W1、W2 demo 均合入 main，决策记录 [0002](decisions/0002-w1-recovery-semantics.md)、[0003](decisions/0003-w2-memory-distillation.md) 均已采纳（W1 设计修订 PR #4 已合入）；W2 设计修订 PR 走完后三件套闭环。下一步：进入 W3（角色分工×DAG + 群组记忆注入策略）。

## 进度日志（倒序）

### 2026-11-01（brief-plan 按 0003 设计修订）

- **[dev] brief-plan 按 [decisions/0003](decisions/0003-w2-memory-distillation.md)（已采纳）完成设计修订**（PR 中）：§4.4 `goal_memory_digest` 增 lifecycle/valid_until/superseded_by/scope/author_agent_id 字段 + HaMo 三元组格式；§5.1 补 turn_context 记忆组装四步顺序（gate 先于 packing、挤出≠拒绝）；§5.4 主候选升级 SEPM+CALM 双主线（生命周期状态机、可计算晋升判据、TTL 第二通道、组装顺序、隐式沉淀须过 gate），含 @research 两条校准——coverage ≥0.30 为本项目实例化参数（HaMo 原文无固定阈值，机制为互补边际覆盖贪心+knee point）、SEPM safety/state-verification 两道 gate 未纳入（state 由回测/数据校验承担，safety 留平台侧）；§12.2 W2 群组记忆落点转「已定稿」（scope 三元组 + 准入 gate + 共享/私有注入规则）。四处均带修订留痕。

### 2026-11-01（0003 转已采纳）

- **[@research] 决策记录 [0003](decisions/0003-w2-memory-distillation.md) 文献复核后转「已采纳」**：七条决策逐条对照 [literature/W2](literature/W2-context-memory-distillation.md) 精读并回抽 PDF 核验数值——SEPM 晋升判据三数值（因果 0.65 / 复现≥1 / 效用≥0）与 CALM 关键数据（512-token 39.2 vs 29.6、污染 50% 注入仅掉 7.0pp）均确证。**一处校准**：coverage ≥0.30 是 demo 实例化参数，HaMo 原文为边际覆盖贪心 + knee point、无此固定阈值（机制方向忠实，不改决策，随 brief-plan 修订注明）。**简化项备查**：demo 未含 SEPM 原文同批的 safety/state gate，state 验证可由回测/数据校验承担，safety gate 留平台侧补。本机独立复跑：12/12 unittest + gate 三态冒烟（拦截/消融放行/好卡通过）与 README 操作剧本一致。
- literature/W2 §4「W2 demo 决策记录」项勾销（AWM 迁移性 spike 拆 W3+，风险项不动）。

### 2026-11-01（W2 记忆蒸馏 demo 跑通）

- **[dev] W2 demo 落地**（`research-demos/w2-memory-distillation-demo/`，PR 中）：SEPM/HaMo 双 gate（coverage 前置 ≥0.30 + reproduction 主 gate ≥1 复现/效用≥0/因果≥0.65）、CALM 裁剪生命周期（CANDIDATE→ACTIVE→STABLE→SUPERSEDED/STALE→ARCHIVED，迁移白名单）、16KB 组装 gate 先于 packing 且挤出≠拒绝、supersede 不删除+指针、TTL 第二触发通道。**12 个定点 unittest 全绿**；操作剧本 1–8 步在真实后端逐条验证（gate 拦截/全消融放行→污染进上下文/复评升 STABLE/TTL→STALE 行保留/supersede 保行/预算挤出标注）；Expo web 打包 193 modules 通过。
- **[dev] 遵守新规范（CONVENTIONS §4 规则 6/7/8）**：README 附十步操作剧本（操作→现象→对应结论）；前端 React Native/Expo 58 无 Electron；后端 Python 3.14.6 纯标准库（sqlite 3.53.2），环境实测表入 README。
- **[dev] 决策记录 [0003](decisions/0003-w2-memory-distillation.md)（提议态）**：七条——可计算晋升判据、gate 先于 packing、生命周期白名单、supersede 不删、TTL 第二通道、scope 字段级落库、demo 形态规范。待 @research W2 精读复核后转已采纳，再走 PR 修订 brief-plan §5.1/§5.4/§12.2。
- AWM workflow 归纳迁移性未进本 demo：需真实 T1 轨迹（W2 笔记 §5 风险项原样保留），留 W3+ 单独 spike。

### 2026-11-01（demo 新规范：可交互 + React Native + Python 版本一致）

- **[@user 提出，@research 落入 CONVENTIONS §4（新增规则 6/7/8）**：
  1. **可交互演示**：后续 demo 必须让人能实际操作、亲手感受研究原理（操作剧本：怎么操作 → 看到什么 → 对应哪条结论），不能只有脚本跑分；W1 recovery demo 已定稿不追溯，W2 起适用。
  2. **前端**：demo 图形界面尽量用 React Native 生态（Expo / react-native-macos），**避免 Electron**；偏离需在决策记录说明。
  3. **后端 Python**：所有 demo 统一 Python 3.14（基线 3.14.6，与 W1 实测一致），不混用大版本。
- **[@dev 当前状态**：W1 三件套已闭环（demo `cf941d8` + 0002 已采纳 + 设计修订 PR #4 `0e2eb13` 合入 main）；按其上一条消息正进入 **W2 记忆蒸馏 demo**（AWM 式 workflow 归纳最小 spike，SEPM/CALM 的 gate 与 supersede 语义进 demo 验证），决策记录从 0003 续编；harness-hub 平台侧仍等 @user 回公司内网。

### 2026-11-01（brief-plan 设计修订）

- **[dev] brief-plan 按 [decisions/0002](decisions/0002-w1-recovery-semantics.md)（已采纳）完成设计修订**（PR 中）：§4.4 领域模型——`goal_run` 状态/认领/租约/fencing 字段定稿、`goal_receipt` 两级幂等回执独立成表、新增 `goal_group_message`（锚点独立）与 `goal_effect_ledger`（第二 oracle）、`goal_event.actor_agent_id` 采纳；§5.2 规则 2/4/5 细化 + 新增规则 6（fencing 写保护）/7（外部 effect 台账对账）/8（六性质+FI+liveness 恢复语义验收清单）；§12.2 W1 落点定稿为「语义统一、锚点独立」。三处均带修订留痕。

### 2026-11-01（W1 文献线完成）

- **[research] W1/W2 文献补检与精读完成**（arXiv API，2026-11-01）：8 篇 2026 下半年（8–10 月）新论文 PDF 归档 `docs/papers/`（索引已更新），7 篇全文精读。W1 四篇（[Resume Means Resume](https://arxiv.org/abs/2608.03836)、[AgentRewind](https://arxiv.org/abs/2608.14380)、[Same Winners, Different Success Rates](https://arxiv.org/abs/2609.34215)、[CUA-Recovery](https://arxiv.org/abs/2610.27645)）→ [literature/W1](literature/W1-durable-scheduling-recovery.md)；W2 三篇精读+一篇摘要级（[SEPM](https://arxiv.org/abs/2610.14515)、[HaMo](https://arxiv.org/abs/2610.34724)、[CALM](https://arxiv.org/abs/2610.38573)、[SPEM](https://arxiv.org/abs/2610.26995)）→ [literature/W2](literature/W2-context-memory-distillation.md)。§12.1 W1/W2 行已回填（W1"待补"解除）。
- **[research] DeepSeek Super-agent 精读**：官方技术文章（2026-10-31）+ 开源原型 [dsh-superagent-prototype](https://github.com/deepseek-ai/dsh-superagent-prototype) 设计文档全文 → [essay-study/deepseek-super-agent-2026.md](essay-study/deepseek-super-agent-2026.md)。要点：Mandate 授权记录≈审批归因、Watchdog≈恢复扫描语义层、Source/Thread≈goal_event 持久化+订阅直通、Router/Worker≈群组静态分工；auto 主动接活与 danger-full-access 运行身份不采纳。
- **[research] 决策记录 [0002](decisions/0002-w1-recovery-semantics.md) 转「已采纳」**：五条决策逐条对照 W1 精读结果复核（语义校准：群组持久化=「语义统一、锚点独立」），并追加文献复核结论段——三项补充采纳（外部 effect ledger 第二 oracle、六性质+liveness 验收清单、takeover-depth 演练设计+检测/修复双指标）。@dev 可走 PR 修订 brief-plan §4.4/§5.2/§12.2。
- **[research] 关键方向结论**（详见两份文献笔记）：W2 主候选由 AWM/ExpeL 升级为 SEPM+CALM 并列（显式结构、生命周期 supersede 不删、gate 先于 token packing、晋升必须可计算判据），HaMo 补经验卡格式；§12.2 群组 scope 字段语义取 SEPM context conditions/exclusions。
- **[research] 规范更新**：CONVENTIONS §6 新增——公开仓库严禁公司 harness 项目源码（2026-11-01 用户规定，harness 分支拉出后 main 仍适用）。

### 2026-11-01（W1 启动）

- **[dev] W1 recovery demo 跑通**（`research-demos/w1-recovery-demo/`，PR 中）：三场景两连跑全 PASS——双 worker 抢占 12 任务 0 重复 0 丢失；第 2 步硬崩溃（exit 137）后 `running`+lease 过期 → 恢复扫描显式 `outcome_unknown` → 重排 → 幂等续跑（已完成步骤零重跑、中断步骤重跑一次）；双 agent 群组会话第 4 步崩溃后从持久化消息恢复，seq 1–6 完整无重复。9 个定点 unittest 全绿（fencing 拒旧 token、回执幂等、actor 归因等）。
- **[dev] 决策记录 [0002](decisions/0002-w1-recovery-semantics.md)（提议态）**：恢复语义五条定稿——`outcome_unknown` 显式化、调度四件套不重造、期次+步骤两级回执、fencing 写保护、群组消息独立于 goal_run 持久化（回答 §12.2 W1 问题）。待 @research W1 文献精读结论合入后转「已采纳」，再走 PR 修订 brief-plan §4.4/§5.2/§12.2。
- 约束确认：公开仓库不入公司 harness 源码（CONVENTIONS §6 已写入），demo 为独立原创最小实现；harness-hub 平台侧开发待 @user 回公司内网后启动。

### 2026-11-01

- **[dev] main 分支保护已开启**（GitHub 侧）：PR 必经 + `lint`（doc-lint）状态检查必过 + 禁 force push/删分支。enforce_admins=false（admin 紧急时可绕过，普通路径锁死）。至此「设计修订必须走 PR、必须过 lint」落地。此前 doc-lint workflow 已确认 active，main 最近两次 push 运行均 success。
- **[research] 规范更新（`888b001`）**：demo 入库以 brief-plan 定稿为界（vn-demo 为唯一例外，后续 demo 入 `research-demos/`）；新增引用链接硬性要求与 `docs/papers/` PDF 归档规范；仓库级提交身份配为 `noire02qwq <noire02qwq@users.noreply.github.com>`。
- **[dev] brief-plan §12.2 新增「多智能体群组配合交互」W1–W5 增量研究线**（决策记录 [decisions/0001](decisions/0001-multi-agent-group-research-increment.md)，走 PR）：每周挂靠一个群组子主题（W1 持久化基座 / W2 群组记忆模型 / W3 角色分工×DAG / W4 群组治理 / W5 群组故障注入），不动既有各周交付；候选论文均为仅摘要级且带 arXiv 链接；明确 W8 反方评审复用 W4 授权矩阵合流、不采纳 MARL 动态拓扑。
- **[dev] 仓库基建（`0cf5d1d`）**：PR 模板（设计修订 PR 强制填依据与留痕）、doc-lint workflow（PR 标题 Conventional Commits / 敏感文件守卫 / markdown 基础检查）、gitignore 收紧。

### 2026-11-01（暂停令）

- **[user] 指令：今天先不做 W3**。@research 手头无在途 W3 工作（W3 检索式尚未启动，无草稿产出），确认即停；W2 闭环（`867526d` → `42164cb` → `3426729`）为当前停点。恢复时间等 @user 下令。

## 阻塞 / 待办

- harness-hub 平台侧开发（插件脚手架、goal_* schema 落地、状态机全转换表实现侧）待 @user 回公司内网后启动。
- @dev：走 PR 修订 brief-plan §5.1/§5.4/§12.2（依据 0003 已采纳；含 coverage 阈值实例化参数说明 + safety gate 平台侧待补）。0002 的 §4.4/§5.2/§12.2 W1 修订已随 PR #4 完成。
- AWM workflow 归纳迁移性 spike：等真实 T1 回测轨迹数据（W3+，依赖回测链路）。
- @research：W3 文献检索式启动（角色分工×DAG 方向 + 群组记忆注入策略）。**已按 @user 指令暂停（2026-11-01）：当日不做 W3，未产生任何 W3 产物（检索式/笔记/草稿均未启动），W2 三件套闭环为当前停点。**
