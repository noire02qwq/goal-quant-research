# 研究创新点（W1–W5：从文献与实测中提炼的自有增量）

> 状态：草稿（待 @dev 双轮核验）｜ 作者：@research ｜ 日期：2026-11-11 ｜ 范围：W1–W5 文献笔记、决策记录 0002–0006、五个独立 demo 的实测证据
> 口径：本文只声称「**相对公开文献的组合与工程化增量**」，不声称发明文献中的原始概念；每条创新点标注验证状态（已验证 / 部分验证 / 未验证留落点），验证状态以决策记录与 demo 实测为准。

## 0. 这份文档回答什么问题

用户要求：前五周研究不能只是「读了论文、改了设计」，要产出**我们自己根据研究得到的创新点**。本文把 W1–W5 五个研究循环里「文献各自提出单点、我们合成协议并实测」的部分提炼为 7 条创新点，逐条给出：来源链（文献→决策→实测）、与文献现有做法的差异（我们的增量在哪）、验证状态、落点。

## 1. 创新点清单

### IN1 构造性前视防护：「不可表达优于可检测」的三层接口协议

- **一句话**：把回测前视防护从「prompt 约束 / 事后统计检验」前移到**接口构造层**——API 只暴露截至当前 bar 的数据、数据 registry flag 使前视在类型上不可表达、回调前入 buffer 越界即抛 `LookaheadViolation`，统计检验只作第二道防线。
- **来源链**：文献——[BacktestBench (2605.17937)](https://arxiv.org/abs/2605.17937) 的 look-ahead 约束只在 prompt（零防线反例）、[What survives (2608.27734)](https://arxiv.org/abs/2608.27734) 的泄漏 oracle（design SR 34.7）连 DSR 仍给 1.00、[Look-Ahead-Bench (2601.13770)](https://arxiv.org/abs/2601.13770) 双时段 alpha 衰减 → 决策 [0004](../decisions/0004-w3-backtest-reliability-and-lookahead-guard.md) 采纳① → 实测 `w3-lookahead-proof-demo` 12/12（干净回测零越界 / 泄露预言机 536% 拦截 / 绕过策略 299+7 条双 lint 定罪）。
- **与文献的差异（增量）**：文献分别证明了「prompt 不够」和「统计检验会被绕过」，但把**构造性不可表达**做成可运行的接口协议（WindowedView 越界抛错 + registry flag）并配双 lint 的组合工程化，是本项目的自有设计。
- **验证状态**：已验证（demo 12/12，[0004](../decisions/0004-w3-backtest-reliability-and-lookahead-guard.md) 已采纳）。
- **落点**：brief-plan §5.6、§6.1。

### IN2 「宣称-证据同档」报告协议：τ_b 必报 + 四档收口 + 报告三件套

- **一句话**：任何策略报告必须携带**执行假设披露与排名稳定性 τ_b**（至少一档敏感性重跑），宣称强度按四档收口（只许 historical backtest / prototype，禁 deployable claim / autonomous trading ability），固定窗口、执行档位、敏感性 τ_b 三件套缺一不得出报告；凡报收益必同报回撤与成本。
- **来源链**：文献——[Execution Assumptions (2610.05077)](https://arxiv.org/abs/2610.05077) 换成交假设使高波板 τ_b=0.21（排序塌掉）、[The Alpha Illusion (2605.16895)](https://arxiv.org/abs/2605.16895) 宣称四档与 P1–P6 证据地板、[AllPath (2610.26662)](https://arxiv.org/abs/2610.26662) 明文不报收益（零收益边界）、[Crypto 三阶段 (2609.34510)](https://arxiv.org/abs/2609.34510) 实盘 4/4 负 alpha → 决策 [0006](../decisions/0006-reporting-and-metrics-taub.md) → 实测 `w5-fault-drill-demo` τ_b=+1.0000（两档执行假设、n=3，`python3.14 demo.py taub` 可逐位复算），测试 19/19。
- **与文献的差异（增量）**：四篇文献各出一个单点（敏感性、分档、不报收益、实盘负例），**本项目把它们合成一份可执行的报告协议**（字段级 metrics 增 `rank_stability_tau` + `exec_tier`、缺件即拒报告），并用 demo 把「正面（τ_b=+1.0 可报）与反面（τ_b=0.21 不可报）」成对实证。
- **验证状态**：已验证（[0006](../decisions/0006-reporting-and-metrics-taub.md) 已采纳；top-3 Jaccard 扩展位半采纳留痕，报告模板定稿时评估）。
- **落点**：brief-plan §6.1。

### IN3 恢复语义统一、锚点独立 + 外部 effect ledger 双 oracle

- **一句话**：群组消息与 goal_run 共享同一套 consume-once / 幂等追加 / fencing 语义但**锚点独立**（消息不挂 goal_run，会话可横跨多次期次 Run）；恢复正确性不信任框架内部状态，用**外部 effect ledger 作第二 oracle**。
- **来源链**：文献——[Resume Means Resume (2608.03836)](https://arxiv.org/abs/2608.03836) 机器可查 resume 契约（5 框架全部部分违约）、[Same Winners (2609.34215)](https://arxiv.org/abs/2609.34215) set-agreement 掩盖近零恢复率、[AgentRewind (2608.14380)](https://arxiv.org/abs/2608.14380) 决策边界对齐回放 → 决策 [0002](../decisions/0002-w1-recovery-semantics.md)（6 性质 + fork-intent + liveness 作状态机验收清单；demo 场景 C 群组实证）→ `w1-recovery-demo` 9/9。
- **与文献的差异（增量）**：文献给出契约与诊断口径，**本项目把它落到「双 oracle + 群组锚点独立」的领域模型**——框架显示正确而外部 ledger 显示重复的实测反例（文献）直接决定了「不信框架自报」的设计。
- **验证状态**：已验证（[0002](../decisions/0002-w1-recovery-semantics.md) 已采纳，demo 场景 C 实证；外部 ledger 第二 oracle 在 w5 故障演练中复用）。
- **落点**：brief-plan §5.2、§4.4、§12.2 W1。

### IN4 记忆蒸馏双主线：SEPM 程序元数据三元组 + CALM 生命周期 gate，scope 落到字段

- **一句话**：`goal_memory_digest` 增 `scope`（共享/私有）与 `author_agent_id`；共享判据取 SEPM 的 applicability/context/exclusions 三元组 + CALM 准入 gate 与 supersede 不删；群组 turn_context 组装 = 共享全量注入 + 私有按角色选择性注入，**上限不放宽**。
- **来源链**：文献——[SEPM (2610.14515)](https://arxiv.org/abs/2610.14515) 显式图换文本 SOP 掉 17pp、[CALM (2610.38573)](https://arxiv.org/abs/2610.38573) 记忆生命周期状态机、[HaMo (2610.34724)](https://arxiv.org/abs/2610.34724) 晋升判据 → 决策 [0003](../decisions/0003-w2-memory-distillation.md) → `w2-memory-distillation-demo` 12/12（scope/author 字段实证）。
- **与文献的差异（增量）**：把两篇独立文献（结构化记忆接口 + 生命周期治理）**合成一个字段级可实现的群组记忆模型**，并明确「共享 blackboard 只存 verified state、成员私有推理留本地」的边界（SEPM 私有推理不减收益）。
- **验证状态**：已验证（字段与 scope 语义；workflow 归纳注入（AWM 式）标未验证留 W2 后续轨迹实测——见 [0003](../decisions/0003-w2-memory-distillation.md) 逐子项状态）。
- **落点**：brief-plan §5.4、§12.2 W2。

### IN5 审批 use-time 绑定 + 「金融动作批准方必须是人」强口径

- **一句话**：canonical approval record 绑定 action/tool identity + 全部 material arguments + principal/scope + nonce/expiry/consumption，use-time 重建完整操作 diff 失配即拒、单次原子消费防重放；叠加金融强口径——**批准方必须是人，agent/工具自批一律无效**，审批通道独立于 agent 可读资源。
- **来源链**：文献——[Loopjacking (2609.21081)](https://arxiv.org/abs/2609.21081) 批准的 A≠执行的 B（Agno/LangGraph 全部可复现）、[I-HITL (2610.35835)](https://arxiv.org/abs/2610.35835) 审批通道必须终止于 agent 不可达的可信实体（Theorem 4 不可能性）、[From Approval to Abuse (2610.22987)](https://arxiv.org/abs/2610.22987) 58% 诱导率/81.0% 静默达成 → 决策 [0005](../decisions/0005-w4-approval-binding-and-authorization-governance.md) → `w4-approval-gate-demo` 16/16（digest 绑定 379a39a0≠900b2fe8 拒绝实证、独立通道最小形态）。
- **与文献的差异（增量）**：文献给形式化与攻击面，**本项目给出金融场景的最小可运行实现 + 比文献更严的口径**（I-HITL 允许设备 attestation 等替代信任根，我们直接规定「必须是人」，不照搬设备方案）。
- **验证状态**：已验证（use-time 绑定与原子消费）/ 部分（命名空间隔离最小形态）/ 未验证留平台侧（完整字段面、提议来源约束）——逐子项见 [0005](../decisions/0005-w4-approval-binding-and-authorization-governance.md)。
- **落点**：brief-plan §5.5、§4.4。

### IN6 故障分类学 → 七步可执行演练剧本（含 interface 诚实与数据面注入）

- **一句话**：把 W5 文献的三类故障（评测口径六类 / 部署链路 interface 诚实 / 数据面注入）转成**可执行的故障注入演练协议**：改坏代码、重启恢复、改目标、interface 对账（submitted≠filled）、数据面污染（回测签名逐字节相等 + 摄取拦截）、数据固定化（seed 两次 sha256 一致）、τ_b 排名稳定性复算。
- **来源链**：文献——[Fake News (2610.26438)](https://arxiv.org/abs/2610.26438) 数据面注入 ASR 61.7% vs 控制面 13.8%、[AllPath (2610.26662)](https://arxiv.org/abs/2610.26662) 三层验证、[LiveTradeBench (2511.03628)](https://arxiv.org/abs/2511.03628)/[AMA (2510.11695)](https://arxiv.org/abs/2510.11695) 真实评测面 → [W5 笔记](../literature/W5-real-eval-fault-style.md) 新增结论⑤⑥⑦ → `w5-fault-drill-demo` 19/19 实测。
- **与文献的差异（增量）**：文献给分类与评测基准，**本项目把它落成七步剧本**（每步输入→现象→对应研究结论），并用「污染/干净回测签名相等」这种正交性证明落地数据面防御。
- **验证状态**：已验证（七步实测，README 逐步记录输出）。
- **落点**：brief-plan §12.1 W5 行、汇报演示直接依据。

### IN7 群组 opt-in：默认单角色零改动的 assigned_role 增量线

- **一句话**：`goal_plan_task.assigned_role` 为**可选**字段——不填即现有单受管 Run 行为零改动，群组能力全部 opt-in；配合 W3 补检五篇的文献级方向（节点可变属性重派、图级后果权限分层、能力余弦匹配 + τ 门槛、清晰度审计、任务图与通信图解耦）留群组扩展/W8 实证。
- **来源链**：决策 [0001](../decisions/0001-multi-agent-group-research-increment.md) 增量原则 + [0004](../decisions/0004-w3-backtest-reliability-and-lookahead-guard.md) 决策 6（demo 步骤 4 双路径共存实证）+ [W3 笔记 §6](../literature/W3-backtest-reliability.md) 补检五篇 → brief-plan §12.2 W3 行。
- **与文献的差异（增量）**：文献都以「群组为默认形态」评测，**本项目反向设计「单角色为默认、群组为增量」**，使金融场景可先落地单 Run 治理、群组按需启用——这是与审批可归因目标一致的结构选择。
- **验证状态**：已验证（opt-in 零改动路径 + 约束拒绝路径共存实测）/ 未验证留 W8（补检五条方向全部文献级）。
- **落点**：brief-plan §12.2 W3 行。

## 2. 边界与不是创新的地方（诚实口径）

1. **不声称发明**：Kendall τ_b、consume-once、fencing、use-time 绑定、SEPM/CALM 机制本身均来自文献或既有工程；创新点是**组合协议 + 金融强口径 + 构造性工程化 + 实测成对证据**。
2. **验证边界**：本文每条的验证状态以对应决策记录为准；「未验证留 <落点>」的子项（如群组五方向、审批完整字段面、workflow 归纳注入）不得当已验证引用。
3. **实现边界**：W1–W5 闭环是**研究闭环**（文献→demo→决策→设计修订）；平台侧插件实现属 harness 集成开发（当前搁置），§1 需求的「开发交付」列在平台仓，不在本仓声称完成。
4. **与 §8 的关系**：brief-plan §8 的 A 组创新功能是**设计层**创新（2026-11-02 前确认），本文是**研究层**创新（W1–W5 文献+实测提炼），两者互补不重复；本文未改 brief-plan（如需吸收进 §8，走已采纳决策 + @dev 定点修订流程）。

## 3. 索引

| 编号 | 创新点 | 决策记录 | 实测 demo | 状态 |
|---|---|---|---|---|
| IN1 | 构造性前视防护三层协议 | [0004](../decisions/0004-w3-backtest-reliability-and-lookahead-guard.md) | w3 12/12 | 已验证 |
| IN2 | 宣称-证据同档报告协议（τ_b+四档+三件套） | [0006](../decisions/0006-reporting-and-metrics-taub.md) | w5 19/19（τ_b=+1.0） | 已验证 |
| IN3 | 恢复语义统一锚点独立 + 双 oracle | [0002](../decisions/0002-w1-recovery-semantics.md) | w1 9/9 | 已验证 |
| IN4 | 记忆蒸馏双主线 scope 字段化 | [0003](../decisions/0003-w2-memory-distillation.md) | w2 12/12 | 已验证（子项部分） |
| IN5 | 审批 use-time 绑定 + 人批强口径 | [0005](../decisions/0005-w4-approval-binding-and-authorization-governance.md) | w4 16/16 | 已验证（子项部分） |
| IN6 | 故障分类学→七步演练剧本 | [W5 笔记](../literature/W5-real-eval-fault-style.md) 结论⑤⑥⑦ | w5 19/19 | 已验证 |
| IN7 | 群组 opt-in assigned_role | [0001](../decisions/0001-multi-agent-group-research-increment.md)+[0004](../decisions/0004-w3-backtest-reliability-and-lookahead-guard.md) 决策 6 | w3 步骤 4 | 已验证（方向文献级留 W8） |

> 测试计数为 2026-11-11 本机实测（w1 9 / w2 12 / w3 12 / w4 16 / w5 19，全部 OK）。
