# W2：长程上下文管理、记忆蒸馏、经验→技能

> 状态：定稿 ｜ 检索日期：2026-11-01 ｜ 对应 brief-plan.md §12.1 第 W2 行、§12.2 W2 群组记忆模型子题

## 1. 检索式与日期

- 检索日期：2026-11-01（arXiv API，按 submittedDate 降序，重点覆盖 2026-09/10）
- 检索式：
  - `all:"memory distillation" OR all:"procedural memory" AND all:agent`
  - `all:agent AND all:skills AND all:"long-horizon"`
- 检索工具与局限：命中大量 2026-10 新工作（过程记忆/技能库方向当月集中爆发）。既有候选 AWM（2409.07429）/ExpeL（2308.10144）为 2024–25 基线，本轮 4 篇新文献全部更近且直接覆盖"晋升判据+生命周期治理"两个 AWM/ExpeL 未回答的问题。4 篇均下载 PDF 精读（[docs/papers/](../papers/README.md)）。

## 2. 入选论文（4 篇，全部 2026-10）

| 论文 | 一句话贡献 | 与本项目的关系 | 精读状态 |
|---|---|---|---|
| [SEPM](https://arxiv.org/abs/2610.14515)（arXiv 2610.14515，2026-10-10） | 以 task dependency graph 作多智能体记忆与协作的统一接口：显式 DAG 边=前置依赖、五道 gate 晋升、CAS 版本更新；六设置全第一，显式图换文本 SOP 掉 17pp | goal_plan_task DAG 边语义、技能晋升 gate、版本冻结的**完整工程模板**；§12.2 群组 scope 字段语义来源 | 已精读 |
| [HaMo](https://arxiv.org/abs/2610.34724)（arXiv 2610.34724，2026-10-26） | harness 经验卡（goal/初始条件/策略大纲三元组）+ retrieval-coverage 统计判据筛选值得参数化的经验 + LoRA 双时间尺度内化 | 经验→技能的**沉淀输出格式**与**晋升判据**；"训练/推理同构注入"启示 skill 存储格式=注入格式 | 已精读 |
| [CALM](https://arxiv.org/abs/2610.38573)（arXiv 2610.38573，2026-10-28） | 记忆生命周期状态机（CANDIDATE→ACTIVE→STABLE→SUPERSEDED/STALE→ARCHIVED）+ supersede 不删除 + 查询时准入 gate 先于 token 装箱；LongMemEval-S 最优 | goal_memory_digest 的**更新与读取语义基准**：过时记忆归档不删除；16KB 预算"挤出≠拒绝" | 已精读 |
| [SPEM](https://arxiv.org/abs/2610.26995)（arXiv 2610.26995，2026-10-19） | 结构感知过程记忆：技能库规模化后高效准确调用（全文已归档，本轮未深读） | 备选：W2 demo 若技能库检索慢可再评估 | 仅摘要级 |

## 3. 方向结论

- **采纳（记忆更新语义=生命周期+supersede 不删）**：goal_memory_digest 增加 lifecycle 状态（沿 CALM 状态机裁剪为 CANDIDATE/ACTIVE/STABLE/SUPERSEDED/ARCHIVED），过时记忆 validity 封顶+指针指向替代者，**不物理删除**——历史回放（W10 可复现）需要旧记忆重构当时决策。改造点：金融域"时间流逝不致 stale"不适用行情/持仓类事实，增加显式 validity interval（TTL）作为第二触发通道；状态迁移用确定性规则维护，digest 更新不必每次 LLM 重写全文（省 token 且可审计）。依据：CALM 消融——去 Stage II（lifecycle 治理）掉 4.0pp，污染注入 50% 时对照掉 16.8–18.8pp 而 CALM 只掉 7.0pp。
- **采纳（16KB 预算协议=gate 先于 packing）**：turn_context 组装顺序固定为"硬过滤（排除 CANDIDATE/ARCHIVED/SUPERSEDED）→ 准入打分 → 按分贪心装入 token 预算 → 挤出者留持久层可再检索"。挤出≠拒绝，是与 §5.1 有界摘要协议的关键差异点。依据：CALM 512-token 预算下 39.2 vs 基线 29.6。
- **采纳（技能晋升必须有可计算判据）**：经验→技能的晋升不能 LLM 拍板，采用三判据组合——SEPM 的 reproduction gate（≥1 次复现 trial+平均效用≥0+因果一致性≥0.65）作主 gate，HaMo 的 retrieval-coverage（被多任务检索支持且互补才值得沉淀）作前置过滤。依据：SEPM 消融中 OfficeBench 上 memory 单独几乎无效（+0.33），有 alignment/晋升才有兑现。
- **采纳（显式结构胜过散文摘要）**：DAG/生命周期等显式结构优于自由文本——SEPM 显式图换文本 SOP 掉 17.16pp，CALM 显式 lifecycle 消融掉 4.0–9.8pp。支持 goal_plan_task 显式边与 digest 结构化字段（不存纯散文）。
- **改造采纳（群组记忆分层）**：§12.2 的 scope 字段语义取 SEPM 的程序元数据模板（applicability/context conditions/exclusions 三元组作 eligible 判据）+ CALM 的 scope 准入；共享 blackboard 存 verified state、成员私有推理留本地（SEPM 消融：私有推理不减收益）。群组 turn_context 组装=共享摘要全量注入+成员私有摘要按角色选择性注入（与 §12.2 W2 落点一致，16KB 上限不放宽）。
- **改造采纳（经验卡格式）**：HaMo 三元组经验卡（goal, 初始观测, strategy-level outline）作为 memory fact→skill 蒸馏的输出模板，策略级大纲适配 16KB 注入；"存一套用一套"（训练/推理同构接口）→ skill 沉淀格式与注入格式统一。依据：HaMo 跨域终局 52.43 vs model-only 崩塌至 24.57。
- **不采纳**：HaMo 的持续 LoRA 训练路径（金融合规+基础设施成本；我们只做 harness 层记忆）；SEPM 的纯协商裁决（无外部真值时 LLM 互相对齐）——金融场景以行情/回测结果为权威源裁决（SEPM 自己的权威层级：环境>工具观测>验证产物>agent 推理，可直接移植）。
- **对 AWM/ExpeL 的升降级**：候选主推荐由 AWM/ExpeL 升级为 **SEPM（结构+晋升+版本）+ CALM（生命周期治理）并列主候选**，HaMo 补格式与判据，AWM 降为"workflow 归纳"机制参考（其网页导航场景迁移性仍需 W2 demo 用 T1 轨迹实测——§12.1 既有风险项不变）。

## 4. 对设计文档的修订

- [x] brief-plan.md §12.1 W2 行：候选论文增补 4 篇 2026-10 新工作（已同步更新）。
- [ ] §5.4 记忆蒸馏：主候选升级为 SEPM+CALM 双主线（待 W2 记忆蒸馏 demo 后走 PR 修订）。
- [ ] §12.2 W2 群组记忆 scope 字段语义定稿（三元组+准入 gate），随 §5.4 一起修订。
- [ ] W2 demo（@dev 执行）决策记录：用 T1 轨迹实测 AWM 式 workflow 归纳迁移性 + 经验卡晋升判据，结论落 decisions/0003 起。

## 5. 风险与待验证项

- SEPM/CALM 均在 ALFWorld/WebArena/LongMemEval 等文本环境验证，**金融代码任务迁移性未知**（与 §12.1 对 AWM 的既有风险同款）——W2 demo 必须实测，不得以论文结论代替。
- CALM 的 learned gate 需 dev 集监督，泛化未证；第一版用 CALM-ZS 免训练均值门起步。
- CALM 原文正文与表 13 的污染鲁棒性数字不一致（正文 11.6 vs 表 −18.8/−16.8pp），本笔记采用表内数值，引用时注意。
- SPEM 仅摘要级，若 W2 demo 出现技能库检索效率问题再深读补档。
