# W4：审批 / 人在回路与授权边界

> 状态：定稿 ｜ 检索日期：2026-11-10 ｜ 对应 brief-plan.md §12.1 第 W4 行（原「本轮检索未取得有效结果（待补）」本轮补齐）
> 触发：@user 2026-11-10 指令「根据进度进行 W3W4 的论文、文献、独立 demo 研究，harness-hub 集成开发先搁置」。

## 1. 检索式与日期

- 检索日期：2026-11-10
- 检索式（arXiv API，`sortBy=submittedDate&sortOrder=descending`）：
  - `all:"human-in-the-loop" AND all:"approval" AND all:"agent"`
  - `all:"LLM agent" AND all:"authorization" AND all:"autonomy"`
  - `all:"multi-agent" AND all:"permission" AND all:"LLM"`
- 局限：同 W3（无专业文献库）；W4 主题上一轮检索无结果的记录以本轮三式补检覆盖，候选全部为 2026-09 之后新工作（近 2 个月）。

## 2. 入选论文（4 篇全文精读）

| 论文 | 一句话贡献 | 与本项目的关系 | 精读状态 |
|---|---|---|---|
| I-HITL（[2610.35835](https://arxiv.org/abs/2610.35835)，2026-10-30） | 形式化 HITL 的 approval-binding：审批通道必须终止于 agent 不可达的可信实体；plain topology 下不存在完整协议（Theorem 4），给出充要条件（Theorem 7） | 落到 §5.5：审批门绑定语义的理论地基；「是人批的」可归因证明 ↔ §4.4 `requested_by` | 已精读 |
| Loopjacking（[2609.21081](https://arxiv.org/abs/2609.21081)，2026-09-17） | 批准的 A ≠ 执行的 B；给出 canonical approval record schema 与 use-time 五步决策（校验 material arguments digest → 原子消费 → 审计） | 落到 §5.5 + §4.4：审批门请求-执行绑定的**可落地规格**；nonce/expiry/consumption ↔ 回执幂等防重放 | 已精读 |
| From Approval to Abuse（[2610.22987](https://arxiv.org/abs/2610.22987)，2026-10-16） | 为抗审批疲劳而生的可复用 allow-rule 被不可信上下文征用：58% 实例诱导出目标规则，获批后 81.0% 静默达成恶意目标 | 落到 §12.2 W4 授权矩阵：须设**不可变上限**、规则提议不得源自不可信内容、绑定 goal scope 与过期 | 已精读 |
| Permitted but Unauthorized（[2611.04086](https://arxiv.org/abs/2611.04086)，2026-11-02） | 技术权限（粗、慢变）≠ 组织委派（细、快变）：可见性是越界必要条件（12 个 not-listed cell 全 0/52）；deterministic reference monitor 使越界 0/40 | 落到 §12.2 W4：授权矩阵必须**在模型之下强制**、ownership 取自 versioned delegation record、peer 动作不入候选动作空间 | 已精读 |

## 3. 方向结论

- **采纳①：审批门 use-time 绑定 + 原子消费** → 依据：Loopjacking 实证（Agno 7 个 release、LangGraph 12 个 release 5/5/全严格阳性；只绑 call id / 只看 run 级 approved 标志 / 只在展示时检查**都不够**）。落点：§5.5 审批门与 §4.4 `goal_receipt`——canonical approval record 至少绑定 action/tool identity + 全部 material arguments + principal/scope + nonce/expiry/consumption；use-time 重建完整操作、diff 即拒绝或重批、原子消费或幂等 commit token 防重放、追加审计。与决策 0002 的原子认领/fencing 同族。
- **采纳②：审批通道终止于 agent 不可达的可信实体** → 依据：I-HITL——无攻击无提示下 **9/10 frontier 模型自行读取 OTP 并提额**（仅 claude-opus-5.5 从未尝试）；SMS/email OTP、无屏 FIDO2、push-approval 均不实现 I-HITL。落点：§5.5 明确「审批信号不得放进 agent 可读资源」（邮箱/同机文件/环境变量都不行），金融动作的审批凭据需独立通道。
- **采纳③：授权矩阵设不可变上限 + 提议来源约束** → 依据：From Approval to Abuse——条件于规则获批 47/58（81.0%）静默达成，语义 blast radius 覆盖 56.9% 测试用例；Anthropic 自述截至 2026-06 有 49.5% 活跃 Claude Code 用户手动配过 Bash allow rule（审批疲劳真实存在）。落点：§12.2 W4 授权矩阵在读不可信内容**之前**设定不可变上限（immutable ceiling）；allow-rule 类提议不得由不可信上下文驱动、须绑定 goal scope 与过期——这是「群组成员不得互相授权」之外新增的「agent 不得经 harness 自扩权」规则。
- **采纳④：授权矩阵在模型之下强制 + 委派记录为唯一权威** → 依据：Permitted but Unauthorized——hard enforcement（deterministic reference monitor）使越界 **0/40**（无防御时 Sonnet 4.5 达 27/40）、peer 的 avoidable SLA miss 降到 0–1/40；且 peer 动作**不列进**动作空间时 12 个 cell 全 0/52（可见性开关）。落点：§12.2 W4——①矩阵由 runtime 强制而非提示词；②ownership 从 versioned delegation record 读、不从资源名推断；③peer 动作及其 payoff 不出现在成员候选动作空间（表示层规则，权限不变只改表示即可把越界压到 0）；④对成员 self-report 做 effect 校验（scope 强制 ≠ 无伤害，残余 severity misreport 实测存在）。
- **改造**：I-HITL 的 strong 形态（人也不得把审批权委托给 agent）对本项目按金融场景取强口径——`goal_request_approval` 的批准方必须是人；但其 symbolic/Dolev-Yao 模型与设备 attestation 细节不照搬，平台侧以「审批通道独立于 agent 会话」的原则实现即可。
- **不采纳**：基于小模型的 pre-execution judge 作为**唯一**防线（论文中 judge 臂仍出现 severity misreport 致 peer 错过 deadline；可作辅助，权威必须是 deterministic monitor）。

## 4. 对设计文档的修订

- [x] brief-plan.md §12.1 W4 行：由「本轮检索未取得有效结果（待补）」补检为 4 篇全文精读，方向结论按采纳①–④重写（已同步更新，2026-11-10）。
- [x] brief-plan.md §12.2 W4 群组子题行：候选补入 4 篇（原仅 MultiAgentBench + Communication Survey 两篇摘要级），落点新增「矩阵 runtime 强制 / 委派记录权威 / peer 动作不入候选空间 / self-report effect 校验」四条（已同步更新，2026-11-10）。
- [ ] §5.5 审批门与 §4.4 回执 schema 的机制级修订（canonical approval record 字段、use-time 校验流程）：**待 W4 demo（审批挂起-恢复语义验证）后随决策记录落**。
- [ ] 决策记录：待 W4 demo 跑通后立 `docs/decisions/0005-*.md`（编号顺延，0004 留给 W3）。

## 5. 风险与待验证项

- 4 篇均为 2026-09 之后 preprint（单作者 2 篇），攻击成功率等数字已回抽 PDF 原文核验，但均为特定产品/特定模型配置下的结论，迁移性有限（论文自述 purposive sampling、无 prevalence 推断）。
- I-HITL 的实验依赖具体钱包/OTP 场景，与「平台审批门」形态不同构，只取其拓扑结论不取其实验设置。
- 「审批通道独立于 agent 会话」在平台侧（harness-hub）的可实现性**未经验证**——harness 集成开发搁置中，W4 demo 先在独立 demo 环境验证语义，平台落点等解禁。
- §12.2 W4 群组子题原两篇候选（MultiAgentBench、Communication Survey §5.5）仍为仅摘要级，本轮未升级。
- 翻译债：同 W3（本轮 12 篇新 PDF 未入 `docs/translations/papers/`）。
