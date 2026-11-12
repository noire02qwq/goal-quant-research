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
- [x] W2 demo 决策记录：晋升判据 + 生命周期 + gate 先于 packing 已落 [decisions/0003](../decisions/0003-w2-memory-distillation.md)（@research 复核后转已采纳，2026-11-01）；**AWM workflow 归纳迁移性未入本 demo**（需真实 T1 轨迹，拆为 W3+ 独立 spike，风险项见 §5）。

## 5. 风险与待验证项

- SEPM/CALM 均在 ALFWorld/WebArena/LongMemEval 等文本环境验证，**金融代码任务迁移性未知**（与 §12.1 对 AWM 的既有风险同款）——W2 demo 必须实测，不得以论文结论代替。
- CALM 的 learned gate 需 dev 集监督，泛化未证；第一版用 CALM-ZS 免训练均值门起步。
- CALM 原文正文与表 13 的污染鲁棒性数字不一致（正文 11.6 vs 表 −18.8/−16.8pp），本笔记采用表内数值，引用时注意。
- SPEM 仅摘要级，若 W2 demo 出现技能库检索效率问题再深读补档。
- **FactorMiner 补检 7 条采纳建议（2026-11-12，§6）**：正负知识对、检索键改状态诊断、propose 全局视角、Stage2.5 判据作 gate 输入（动作仍走人批）、A8 评估管线+准入双判据、公平比较协议、轨迹 τ 并 W6 账本——全部**文献级未落决策**，待 demo 证据后按 0003/0006 模式处理。

## 6. 补检：FactorMiner（2026-11-12 @user 点名加入）

- **触发与归档**：@user 2026-11-12 指令「[2602.14670v2#A2](https://arxiv.org/html/2602.14670v2#A2) 这篇论文加入研究和翻译」（非检索式命中）。`id_list` 回核题名一致；PDF 归档 [docs/papers/arXiv-2602.14670.pdf](../papers/README.md)（1,431,239 B / 12 页，pdfinfo+%%EOF 过闸，v2=2026-08-19 q-fin.TR）；**KDD '26 会议论文**（[DOI 10.1145/3770855.3818978](https://doi.org/10.1145/3770855.3818978)），非 preprint，但**全部实验数字为作者自报、无第三方复现**。
- **一句话贡献**：[FactorMiner](https://arxiv.org/abs/2602.14670)——把公式化因子挖掘封装为可调用 Agent Skill（60+ 类型化算子 + check_ic→check_correlation→admit 确定性验证管线）+ 结构化经验记忆（Psucc/Pfail 双份、F/E/R 三算子）+ Ralph Loop（retrieve→generate→evaluate→distill）的自演化 agent，评估走确定性代码防 LLM 指标幻觉。
- **关键数字（本机独立回抽 12/12 命中，行号=提取件 2602.14670.txt）**：默认准入 τ_IC=0.04、θ=0.5（L7555）；替换判据 IC≥0.10 且 ≥1.3×被替换者且唯一冲突（L7560）；消融有记忆 96 个高质量候选 60.0% yield vs 无记忆 32 个 20.0%（L7333/L7281）、拒绝率 55.2% vs 43.8%（L7287）；主结果 CSI500 IC 8.25%/ICIR 0.77 vs RF 2.68（L7188/L7182）；全库 110 因子平均非对角 |ρ|=0.203（L7131）；1,000 候选评估约 6 分钟 vs Pandas 约 70 分钟（L7417）；VWAP_Deviation 变体相关 0.82 被重分类 Pfail（L321）。
- **用户锚定 #A2 解析**：arXiv HTML 附录 id 编号为 A1–A4，**#A2 实为 Appendix B: End-to-End Signal Correlations**（非附录 A 的 A.2 小节）——检验 PatchTST/Chronos-2/LightGBM 三个端到端信号与 110 因子库的冗余：Avg|ρ| 分别 0.0365/0.0399/0.0146、单因子 max ≤0.23、三者两两 0.043/0.171/0.224（L7529/L7538）→ **互补非重复**。对本项目的用处：这是「因子库 vs ML/端到端信号」的**冗余性防御检查范式**——§8 A8 沉淀库与 §6.1 测评若引入 ML 选择器/端到端信号，可用同口径（Avg|ρ|/Max|ρ|/最近邻表）证明互补而非重复。
- **与本笔记主线的关系**：①W2 方向②「经验技能四环节」逐环节对应——获取（Formation 蒸馏）/表示（Mining State S+Structural P+Strategic I 三层 NL 模板）/调用（按「库诊断+最近拒绝原因」检索）/精炼（Evolution 合并丢弃）；**缺口**：其 skill 是人工构建算子库、不自演化，「获取→技能沉淀+版本哈希」这一跳没有，我方 §5.4 第 5 条原设计不被替代。②**金融域实证旁证**：AWM/ExpeL/SEPM/CALM 全在文本/导航环境，FactorMiner 是本候选池唯一量化场景实证，部分缓解 §5 风险项「金融迁移性」；但其记忆无生命周期状态机、无晋升 gate、无 TTL——CALM/SEPM 那套独有价值仍在。
- **方向结论（采纳 7 条，均文献级、待 demo 证据后按 0003/0006 模式落决策或随 W6+ 修订）**：① §5.4 经验蒸馏升级为**正负知识对**（每期同写 Psucc 与 Pfail+冲突证据，重分类不物理删除）；② §5.4/§5.1 记忆检索键从时间近因改为「当前状态诊断+最近否决原因」匹配；③ §6.2 propose 输入加全局库饱和度/拥挤度视角（Mining State S）；④ §6.2/§8 A5 采纳 Stage2.5 替换**判据**作 gate 输入——**替换动作仍走 §5.5 人批门，不照搬其自动生效**；⑤ §8 A8 采纳四段评估管线（fast IC→相关性→批内去重→全量验证）+ 准入双判据 + 禁止方向表（Table 10）作沉淀库 schema；⑥ §6.1 采纳公平比较协议（同准入规则/同评估引擎/等规模集合）；⑦ 轨迹 τ 结构化字段（formula/IC/ICIR/max ρ/准入-拒绝-替换结果）并入 W6 试验账本最小记录集，不另起炉灶。
- **不采纳**：自动替换不经审批（与 0005「批准方必须是人」冲突）；LLM=闭源 Gemini 3.0 Flash 且不披露 prompt（我方 goal_experiment 必须可复现）；无反方评审/版本回退/终态判定的循环终点；消融口径（|IC|>0.02、θ=0.85 与默认不一致）的 60%/20% 效应量不外推；「Correlation Red Sea」「概率测度收缩」等叙事概念不作结论引用。
- **存疑**：其 IC 为 |E[IC]| 绝对值口径，与我方带符号 IC **不可横向比**；无显著性检验/多种子方差/交易成本（作者自认留 future work）；表 4 稳健性只到 2026-03；Alpha101 基线被适配成每公式 10 变体取最优，引用基线数字须带此限定。
- **W7 交叉引用（不占 W7 主条目）**：Ralph Loop≈RDLoop 骨架、因子库准入/替换≈程序数据库 archive 的两条思想性佐证；W7 主候选仍为 RD-Agent(Q)/QuantAgent/AlphaEvolve。
- **归档与中译**：本补检节为主档（不单开笔记）；全文中译入 `docs/translations/papers/arXiv-2602.14670.md`（引用于本笔记），索引与终检随收尾提交。
