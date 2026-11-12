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
- **补检（2026-11-11，§12.2 W3 群组子题）**：四式 `abs:"role assignment" AND abs:"multi-agent" AND abs:LLM` / `abs:DAG AND abs:"multi-agent" AND abs:LLM` / `abs:"agent workflow" AND abs:(search OR optimize OR graph) AND abs:LLM` / `abs:"role" AND abs:"task decomposition" AND abs:LLM AND abs:agent`，32 候选入选 5 篇全文精读（见 §6）。

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
- [x] §12.2 W3 群组子题（角色分工×goal_plan_task DAG）：**2026-11-11 补检完成**——新增 5 篇全文精读（见 §6），MetaGPT/ChatDev 维持仅摘要级作经典对照；`assigned_role` opt-in 结论不变，补检方向作为落点参考已回填 brief-plan §12.2 W3 行。

## 5. 风险与待验证项

- 全部为 arXiv preprint（BacktestBench 标 KDD 2026 但 DOI 版未核），单作者/未评审占多数；数字均已回抽 PDF 原文核验（grep -a 命中），但结论强度按 preprint 对待。
- MintEval/QuantHarness 的验收机制在**本项目 T1–T4 规则型策略**上的迁移性未验证——行为等价比对需要参考实现，规则型策略的「参考」由谁写（人/spec/双盲）待 W3 demo 定。
- FinCutBoundary 实测依赖题库持续更新（月度），本项目只消费其方法结论，不接题库。
- ~~翻译债：本轮 12 篇新下载 PDF 尚未入 `docs/translations/papers/`~~（已清：12 篇 2026-11-10 入库并经 @dev 四项核验）。~~**新债**：§6 补检 5 篇（2505.13516/2604.02770/2605.06320/2610.07860/2610.17143）尚未中译~~（已清：5 篇 2026-11-12 入库、机器终检 33 OK / ALL PASS，待 @dev 四项核验，见 PROGRESS）。


## 6. 补检：§12.2 W3 群组子题（角色分工 × goal_plan_task DAG）

> 补检日期：2026-11-11 ｜ 触发：PROGRESS 待办④ ｜ 5 篇**全文精读**（2 个并行子代理分页读毕、关键数字由 @research 独立回抽命中：47.5% 提取件 L405、0.890 L116、62.6% L123（Tree 的 Sequential 均值；角色放置 Center=67.7% 另于 L131/L427 回抽，@dev 核验纠错后补）、46.4→8.4 L47、95.2/78.6/14.6 L427+L536）｜ 检索式见 §1 补检行

| 论文 | 一句话贡献 | 与本项目的关系 | 状态 |
|---|---|---|---|
| LATTE（[2605.06320](https://arxiv.org/abs/2605.06320)，2026-05） | 动态任务图协调：1 Lead+N Worker、七算子（DISCOVER/ASSIGN/CLAIM/COMPLETE/RELEASE/CLOSE/VERIFY）按「图级后果」分权限、frontier 决定并行数；token 成本 47.5% vs 静态图消融 86.9%、准确率 79.7% vs 57.6%（p<0.01，MetaGPT 对照仅 33.9%） | `assigned_role` 应为**节点可变属性**（RELEASE 可退回重派）；五态状态机+heartbeat 兜底；领取式（CLAIM FIFO）分工；校验按需插入（19% trial 才触发） | 已精读 |
| WorkflowOps（[2610.07860](https://arxiv.org/abs/2610.07860)，2026-10） | 编排先验学习：角色转移矩阵 P 给 DAG 补**软边**（硬依赖不可覆盖）、子任务能力描述与角色卡 embedding 余弦指派（τ=0.45 以下才 LLM 复核/新建角色）；Mixed 0.890 vs 最强基线 0.751（+13.9pp，p<0.001） | **能力驱动的 assigned_role** + 匹配阈值门槛（两级匹配省 80%+ LLM 路由调用）；角色卡 schema（id/description/instructions/…）可直接借用；软硬依赖分层=角色分工无权否决任务逻辑 | 已精读 |
| OpenDGO（[2610.17143](https://arxiv.org/abs/2610.17143)，2026-10） | 组织基准：组织五元组 O=(G,R,P,I,B)，**任务依赖图 H 与通信图 G 解耦**（同一 DAG 可挂不同组织评测）；learned 组织赢 13/18 条件；Sequential 任务关键角色放 Center **67.7%**、移到 Edge 降至 60.2%（Δ7.5pp；62.6% 是 Tree 的 Sequential 均值，勿混） | **DAG 形状 → 角色放置查表**（Sequential→Center+集中输入、Parallel/Integration→Bridge+分散）；角色分配本身是性能变量非实现细节 | 已精读 |
| Role Clarity（[2604.02770](https://arxiv.org/abs/2604.02770)，2026-04） | 角色越界（disobey role specification）量化：行为-角色相似度经 softmax 得清晰度矩阵 M，对角=一致性、非对角=越界；微调后越界率 Qwen 46.4%→8.4%、Llama 43.4%→0.2% | `assigned_role` 的**守规审计**：群组结束算一次清晰度分；无护栏基线近半任务越界 → 越界告警有动机；格式合规与角色遵守分开报数 | 已精读 |
| HALO（[2505.13516](https://arxiv.org/abs/2505.13516)，2025-05） | 三层编排 plan（逐步分解）→ assign（按子任务实例化角色+模板）→ execute，MCTS 搜索工作流边；Avg 78.6 vs ADAS 64.0（+14.6pp）；去分解层 −11.3pp | `assigned_role` 三元组（角色名, 子任务, prompt 模板）随节点下发而非全局静态角色表；分解一步一做、回看执行历史 | 已精读（ID 见事故披露） |

**方向结论（文献级，未在本项目实证；供 §12.2 落点参考，随群组 opt-in/W8 实证）**：

- **采纳方向①：`assigned_role` 为节点可变属性，不是规划期定死的枚举**。依据：LATTE——固定分解在非平稳任务系统性失配（MetaGPT 对照 33.9% vs 79.7%）、RELEASE 把节点退回 pending 重派；**边界条件**：结构完全预知的任务上动态与静态持平（40±2 vs 40±2），动态化收益依赖任务非平稳性。
- **采纳方向②：改图级权限按「图级后果」分层**。依据：LATTE 七算子权限表——局部发现/完成归执行者，RELEASE/VERIFY/CLOSE 等全图操作归协调者；与 0005「矩阵不可变上限、越权拒」同族。
- **采纳方向③：能力驱动指派 + 阈值门槛**。依据：WorkflowOps——子任务带能力需求描述、余弦匹配 argmax、τ 以下才走 LLM 复核/新建角色；角色池持续演化**不作默认**（+1.7 点要 2.7× token、长期复用未测），静态池+按需开关。
- **采纳方向④：角色守规可审计（清晰度分/越界告警）**。依据：Role Clarity——行为-角色相似度对角值即映射质量；基线越界 43–46%（无护栏近半违规）。
- **采纳方向⑤：任务图与通信图解耦，DAG 形状决定角色放置**。依据：OpenDGO——H（任务依赖）与 G（组织）分离评测；Sequential→Center 67.7%（vs Edge 60.2%）、Parallel/Integration→Bridge；**注意**：结构-属性关联作者自认非因果（not an identified causal chain），查表规则按经验参考对待。
- **不采纳/存疑**：WorkflowOps 角色池持续演化作默认（性价比与长期效果未证）；HALO 66% 早停阈值（拜占庭类比、未调参敏感性）；全部 preprint、多为单框架单骨干（GPT-4o/gpt-5/同质模型 N=5），「专家型异质分工」证据有限；OpenDGO 胜场口径正文两处不一（12/18 L121 vs 13/18 L384，以后者附录拆解 7+5+1=13 为准并双注）。
- **执行细节留设计参考**（不升格为结论）：五态状态机（pending/assigned/in_progress/done/verified）+ heartbeat 掉队兜底、领取式 FIFO 分工、协调指标五项（跨执行者覆盖/并发写/浪费字符/空闲轮/掉队尾延迟）、按拓扑层并行+多前驱 fan-in——随 §12.2 落点、留群组扩展实证。

**事故披露（ID 错档，已修复）**：初检 API 结果把 HALO 误配为 2605.13516（实为 eess.SP 的 UAV 论文），下载后由精读子代理发现标题不符、经 `id_list` API 复核正确 ID 为 **2505.13516**（cs.MA）。处置：错档 PDF 删除未入库、正确 PDF 重下（2,866,963 字节、`%%EOF` 通过）、重提取与子代理提取件前 20 行一致、README 索引行已改。教训：**ID 关键的下载前先按 `id_list` 回核标题**（本轮子代理与我各复核一次才闭环）。
