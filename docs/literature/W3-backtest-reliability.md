# W3：LLM 生成量化回测代码的可靠性、前视偏差

> 状态：定稿 ｜ 检索日期：2026-11-10 ｜ 对应 brief-plan.md §12.1 第 W3 行（含 §12.2 W3 群组子题衔接说明）
> 触发：@user 2026-11-10 指令「根据进度进行 W3W4 的论文、文献、独立 demo 研究，harness-hub 集成开发先搁置」——W3 暂停令就研究线解除，harness 侧维持搁置。

## 1. 检索式与日期

- 检索日期：2026-11-10
- 检索式（arXiv API，`sortBy=submittedDate&sortOrder=descending`）：
  - `all:"backtest" AND all:"LLM"`
  - `all:"look-ahead bias" AND all:"LLM"`
  - `all:"quantitative trading" AND all:"LLM agent"`
  - `all:"trading strategy" AND all:"large language model"`
- 与计划文档 §12.1 原检索式（`LLM automated quantitative backtesting benchmark`、`look-ahead bias LLM finance`）互补；原表三篇候选（BacktestBench / Look-Ahead-Bench / What survives）本轮全部从「已读摘要」升级为**全文精读**。
- 局限：本轮未接入专业文献库（dataPro 订阅仍不可用），全部走 arXiv API；检索结果以 2026-05 之后新工作为主，符合「优先近 12–18 个月」门槛。

## 2. 入选论文（7 篇全文精读 + 1 篇仅摘要级）

| 论文 | 一句话贡献 | 与本项目的关系 | 精读状态 |
|---|---|---|---|
| BacktestBench（[2605.17937](https://arxiv.org/abs/2605.17937)，KDD 2026） | 18,246 题 A 股回测基准 + 标准化回测协议（long-only、T-1 信号、双盲 KPI 实现、误差 <1e-3 判分） | 落到 §5.6/§6.1：指标计算统一走指标库不讓模型写公式；其 look-ahead 约束**只写在 prompt** 是反面教材 | 已精读 |
| MintEval（[2610.03080](https://arxiv.org/abs/2610.03080)，2026-10） | 行为等价基准：逐 bar 动作比对而非读码；引擎物理强制因果（bar t 回调前才入 buffer，访问 t+1 抛错） | 落到 §5.6：GoalStrategyBase 把前视从约定变成**不可违反的 API 事实**；读码 LLM judge 会放行全部静默失败（Opus 5.5 0.275 silent 全过） | 已精读 |
| QuantHarness（[2610.26101](https://arxiv.org/abs/2610.26101)，2026-10） | 三边界（Information/Action/Commitment）harness 治理策略开发全程；FinRelBench 97 任务 Task Success 90.72% | 落到 §8 A2/§6.1：append-only budget ledger、commitment seal（路径+内容哈希）、预算化优化（≤3+1、final 期不回流）、repair AST guard | 已精读 |
| Hard to Fool（[2611.06607](https://arxiv.org/abs/2611.06607)，2026-11-04） | 约 24 个 campaign 只有 2 个幸存；绝对门合取 + 单次 holdout receipt + 哈希链账本 | 落到 §8 A2：门禁合取替代单分数、holdout 凭 receipt 只开一次、重复先于 trial 拒收 | 已精读 |
| Look-Ahead-Bench（[2601.13770](https://arxiv.org/abs/2601.13770)，2026-01） | 双时段 alpha 衰减区分真预测与记忆：DeepSeek 3.2 P1 alpha +20.73pp → 衰减 −21.77pp；PiT 模型稳定（+0.31~+1.30pp） | 落到 §6.1/样本外窗口：模型时间泄露是**可测量的**，「Scaling Paradox」——标准模型越大衰减越狠 | 已精读 |
| What survives honest evaluation?（[2608.27734](https://arxiv.org/abs/2608.27734)，2026-08） | 两个结构性护栏：注册表让前视**不可表达** + 单入口试验账本喂 DSR/PBO；泄漏 oracle（design SR 34.7）DSR 仍 1.00，只有结构护栏能拦 | 落到 §5.6/§8 A2/§6.1 三处：registry flag、账本单入口、evaporation curve；本轮从仅摘要级升级全文 | 已精读 |
| FinCutBench（[2611.11588](https://arxiv.org/abs/2611.11588)，2026-11-08） | 9,000 题（2023-01～2026-09）月度知识剖面测**实测知识边界**（FinCut Boundary + Tight/Wide 置信标签） | 落到 §6.1：样本外窗口起点从「vendor 披露日期」升级为「实测 boundary + 置信标签」 | 已精读 |
| When Alpha Disappears（[2605.23959](https://arxiv.org/abs/2605.23959)，2026-05） | one-switch 配对消融量化单个评测约定贡献的 Leakage Gain（中心化时序特征与 same-day-open 执行贡献最大） | 落到 §5.6：作为「API 规则确实生效」的**验证工具**（报 Leakage Gain 而非断言无视视） | 仅摘要级 |

## 3. 方向结论

- **采纳①：前视偏差构造性防护再加固（三篇互证）** → 依据：What survives 的注册表 flag（前视构造不可表达，泄漏 oracle 过 DSR/PBO 也过不了结构护栏）+ MintEval 的物理因果引擎（越界访问抛不可吞错误）+ BacktestBench 的反面教训（look-ahead 只写 prompt，防线为零）。GoalStrategyBase（§5.6）目标不变、证据升级：**API 面 + 数据 registry flag + 回调前入 buffer** 三层。
- **采纳②：试验账本单入口，三仪器齐算不可省** → 依据：What survives——账本经单一 evaluation entry point 构造性完整，DSR 的 N/V 从账本读、CSCV 候选矩阵列数=N 为不变式；且 E3 案例 PBO 0.01 仍样本外崩（eval SR 0.18 vs B&H +40.8%），**PBO 低不豁免 held-out CI**。Hard to Fool 补哈希链 append-only、重复先于 trial 拒收、holdout 凭 receipt 单次消耗。落点：§8 A2 强制 gate + §6.1 `trial_count/effective_trials/psr/dsr` 从账本取数。
- **采纳③：回测代码验收用行为等价，不读码** → 依据：MintEval——1,767 个 spec 完全正确的编译运行中 0.792 的 ActionMatch<0.9；QuantCode-Bench 的读码 judge 放行 Opus 5.5 全部 55 个静默失败。落点：demo/验收以**与参考实现逐 bar 动作比对**（ActionMatch/TradeF1/|ES|）为准；KPI 数值用 BacktestBench 的 <1e-3 容差 + 双盲实现。
- **采纳④：样本外窗口起点用实测知识边界** → 依据：FinCutBench——GPT-5.6-Sol 披露 2026-02-16、实测 Boundary 2026-06（晚约 4 个月），GPT-6-Astra 披露 2026-04-30、实测 2026-06；Haiku-4.5 实测 2025-02 但 Boundary Range 为 Wide（2024-07～2025-04）。把 §12.1 既有结论「样本外窗口取晚于模型知识截止」从**单点 vendor 日期升级为实测 boundary + Tight/Wide 置信标签**，Wide/ND 模型取更晚起点或弃用。
- **采纳⑤：门禁合取 + 预算化选型** → 依据：Hard to Fool（绝对门合取、ranking 只在过门者中选、5% 下尾按 shortlist 校正）+ QuantHarness（≤3 次优化评估 + 1 次 final、候选哈希去重、final 结果不回流、repair AST guard 禁止为出单改规则）。落点：§8 A2 与 DSR/PBO 并列为合取项。
- **改造**：Hard to Fool 的声明式 JSON 词表（模型只许 propose 数据、不写代码）与本项目「LLM 生成回测代码」前提冲突 → 改造为「**代码必须实现声明式 spec + 行为等价/引擎因果校验**」，词表思想用于 spec 层而非禁掉代码生成。
- **不采纳**：单一分数/单一仪器验收（任一论文均证明单仪器有盲区——DSR 拦不住泄漏、PBO 拦不住绝对崩塌、ranking 分不能放行）；不采纳把 Leakage Gain 消融当认证（2605.23959 自述 diagnostic only，不能替代 DSR/PBO/held-out）。

## 4. 对设计文档的修订

- [x] brief-plan.md §12.1 W3 行：候选论文升级为 7 篇全文精读 + 1 摘要级，方向结论按采纳①–⑤重写（已同步更新，2026-11-10）。
- [ ] brief-plan.md §5.6/§6.1/§8 A2 的机制级修订（registry flag、账本单入口字段来源、行为等价验收、实测边界窗口）：**待 demo 证据后随决策记录落**，本轮不直接改设计正文。
- [ ] 决策记录：待 W3 demo（回测验收路径）跑通后立 `docs/decisions/0004-*.md`。
- §12.2 W3 群组子题（角色分工×goal_plan_task DAG）：本轮检索未产出直接新增文献，MetaGPT/ChatDev 维持仅摘要级，**该子题文献待补**，不阻塞 `assigned_role` 既有设计（opt-in 结论不变）。

## 5. 风险与待验证项

- 全部为 arXiv preprint（BacktestBench 标 KDD 2026 但 DOI 版未核），单作者/未评审占多数；数字均已回抽 PDF 原文核验（grep -a 命中），但结论强度按 preprint 对待。
- MintEval/QuantHarness 的验收机制在**本项目 T1–T4 规则型策略**上的迁移性未验证——行为等价比对需要参考实现，规则型策略的「参考」由谁写（人/spec/双盲）待 W3 demo 定。
- FinCutBoundary 实测依赖题库持续更新（月度），本项目只消费其方法结论，不接题库。
- 翻译债：本轮 12 篇新下载 PDF 尚未入 `docs/translations/papers/`（待办，见 PROGRESS）。
