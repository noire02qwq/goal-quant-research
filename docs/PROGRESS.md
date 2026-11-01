# 项目进度记录（PROGRESS）

> 状态：活跃维护。每次有实质进展（规范变更、设计修订、研究/demo 完成、阻塞解除）由执行方追加一条记录；本文件只记结论与指针，细节写入对应文档后链接过去。日期为本地日期。

## 当前阶段

Phase 1 W1 进行中（@user 2026-11-01 下令启动 W1–W2 研究/demo 循环；harness-hub 平台侧开发待回公司内网）。当前：recovery demo 已跑通、决策记录 0002 提议态；文献精读线由 @research 并行推进。

## 进度日志（倒序）

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

- 无阻塞。**等 @user 下令启动 W1**（插件脚手架 + goal 领域模型/状态机 + workspace-automation 源码精读 + recovery demo）。
