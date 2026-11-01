# 项目进度记录（PROGRESS）

> 状态：活跃维护。每次有实质进展（规范变更、设计修订、研究/demo 完成、阻塞解除）由执行方追加一条记录；本文件只记结论与指针，细节写入对应文档后链接过去。日期为本地日期。

## 当前阶段

Phase 1 W1 进行中（@user 2026-11-01 下令启动 W1–W2 研究/demo 循环；harness-hub 平台侧开发待回公司内网）。当前：recovery demo 已跑通、0002 已采纳（文献合入完成）；W1/W2 文献线达标（8 篇 2026H2 论文归档、7 篇精读 + DeepSeek Super-agent 精读）。下一步：@dev 走 PR 修订 brief-plan §4.4/§5.2/§12.2，随后进入 W2 记忆蒸馏 demo。

## 进度日志（倒序）

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

## 阻塞 / 待办

- harness-hub 平台侧开发（插件脚手架、goal_* schema 落地、状态机全转换表实现侧）待 @user 回公司内网后启动。
- @dev：走 PR 修订 brief-plan §4.4/§5.2/§12.2（依据 0002 已采纳 + W1 文献笔记）。
- W2：记忆蒸馏 demo（T1 轨迹实测 AWM 迁移性 + 经验卡晋升判据），决策记录从 0003 续编。
