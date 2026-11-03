# 同样的赢家，不同的成功率：LLM Agent 如何从失败中恢复（Same Winners, Different Success Rates: Evaluating How LLM Agents Recover from Failures）

> 来源：https://arxiv.org/abs/2609.34215
> 原文：docs/papers/arXiv-2609.34215.pdf
> 翻译日期：2026-11-03 ｜ 范围：全文（正文全译，参考文献从略） ｜ 方式：机器翻译初稿，未经人工校对
> 引用于：docs/literature/W1-durable-scheduling-recovery.md、docs/decisions/0002-w1-recovery-semantics.md、docs/brief-plan.md

## 目录

- 摘要
- 1 引言（Introduction）
- 2 相关工作（Related Work）
- 3 Checkpoint 设定与决策目标（Checkpoint Setting and Decision Targets）
- 4 仅靠 set agreement 为何不够（Why Set Agreement Alone Is Insufficient）
  - 4.1 最佳动作集合无法识别成功概率
  - 4.2 认证极限：精确平局与分离间隔
  - 4.3 记录指派改变 checkpoint 结论
- 5 实验（Experiments）
  - 5.1 RecoveryBench：高一致率、低成功率
  - 5.2 规划任务：一致率下降而质量保持
  - 5.3 记录指派改变比较结论
  - 5.4 认证需要大间隔
- 6 讨论（Discussion）
- 附录 A 定义与证明（Definitions and Proofs）
  - A.1 偏好与放行的联合识别
  - A.2 总体记录与固定状态目标
  - A.3 配对、单例认证与候选覆盖
  - A.4 动作集合的桥见证
  - A.5 安全边界与证据请求
- 附录 B 实验协议与重放控制（Experimental Protocols and Replay Controls）
  - B.1 评估总体与统计单元
  - B.2 工作流动作与执行记录
  - B.3 比较规则与结果度量
  - B.4 任务构造与划分构成
  - B.5 轨迹表示与动作契约
  - B.6 主要重放不确定性
  - B.7 选择器拟合稳定性
  - B.8 固定核重放控制
- 附录 C 相关工作与识别边界（Related Work and Identification Boundaries）
  - C.1 top-1 迁移的序列化敏感性
  - C.2 trace-only 门的观测不可识别性
  - C.3 一次性期望排序识别审计
  - C.4 有限分支认证与统计放行
- 附录 D 受控证据与决策研究（Controlled Evidence and Decision Studies）
  - D.1 主要放行与请求比较的生成器
  - D.2 契约级决策规则
  - D.3 模型类分支预算审计
  - D.4 确定性门控制与联合规律检验
  - D.5 证据分配
  - D.6 共享预算下的证据获取
  - D.7 证据覆盖与校准
  - D.8 核路径与机制控制
  - D.9 匹配签名的机制分离
- 附录 E 补充决策与关系审计（Supplementary Decision and Relation Audits）
  - E.1 源键机制见证
  - E.2 配对放行对比
  - E.3 同一结果抽样下的放行目标
  - E.4 重复稳定性与结果构成
- 附录 F 执行归档与记录重建（Execution Archives and Record Reconstruction）
  - F.1 制品有效性与动作一致率
  - F.2 补充物化控制
  - F.3 归档完备的本地放行门
  - F.4 顺序证据请求闭包
  - F.5 有键桥的敏感性
  - F.6 经验联合像审计
  - F.7 跨保留执行源的一致率
  - F.8 保留 checkpoint 绑定的检索
  - F.9 联合观测目标与本地放行资格
- 附录 G 前瞻性重复分支研究（Prospective Repeated-Branch Study）
  - G.1 独立规划复现
  - G.2 GPT-5.6 家族扩展
  - G.3 exact-set 一致率与经验平局变化
  - G.4 对自报总数的敏感性
  - G.5 经验近平局敏感性
  - G.6 一致率度量与经验平局
  - G.7 跨结果契约的集合一致率
  - G.8 置信关系开发试点
- 附录 H 冻结 RecoveryBench 验证（Frozen RecoveryBench Validation）
- 参考文献从略，见原文

## 摘要

评估 LLM agent 如何从任务中途失败中恢复，是部署可靠 agentic 系统的核心问题。现有基于 checkpoint 的基准通过比较独立运行中哪个动作被选为最佳来衡量恢复效果，这一量称为 set agreement（集合一致率）。然而，set agreement 是一个纯粹的序数度量：它只记录哪个动作"胜出"，并不反映绝对的性能水平。当所有动作都失败时，它们在零奖励上打平，而独立运行以高概率产生相同的并列集合，从而制造出一种稳定性的假象，掩盖了接近零的恢复成功率。我们通过一个 set-path symmetry（集合路径对称性）结果把这一局限形式化，证明对于等成本的 Bernoulli 动作，成功概率 (0.9, 0.8) 与 (0.2, 0.1) 在任何样本量下都产生完全相同的最佳动作集合分布。任何仅基于哪个动作胜出的程序都无法区分这两种机制。我们进一步证明：精确的总体平局在有限时间内不可能被认证；而且结果到 checkpoint 的指派携带了超出边际结果分布的信息。汇总成功概率（pooled success probability）就是消解这一序数歧义所缺失的标量。在 864 个冻结的 RecoveryBench episodes 以及两个规划队列共 3,456 条响应上的实验验证了理论预测。一致率与留出集（held-out）质量可以朝相反方向变化；置换 checkpoint 与动作的绑定会改变 8% 到 13% 的单元格级结论。基于这些发现，我们建议报告四个诊断量（agreement、全零比例、held-out success、pooled success），无需额外数据采集即可暴露这一失效模式。

## 1 引言（Introduction）

随着基于 LLM 的 agent 被部署到日益复杂的工作流中，从任务中途失败中恢复的能力已成为一项关键能力。当 agent 在某个中间步骤失败时，工作流可能重试该操作、验证当前结果，或者干脆把 agent 整个换掉。评估这些恢复策略，需要能够可靠识别哪个动作能带来任务成功完成的基准。近期工作引入了基于 checkpoint 的基准，例如 RecoveryBench（Tan et al., 2025）和 ToolMaze（Zhu et al., 2026），它们重放失败的 agent 状态，并在受控条件下测量恢复结果。

这些基准中广泛使用的稳定性指标是 set agreement，即独立运行选择同一最佳动作的频率。高一致率通常被解读为"评估稳定、所选动作确实更优"的证据。然而，这种解读假设一致率反映动作质量。我们证明它并不反映，因为 set agreement 把序数排名与基数性能混为一谈：同样高的一致率既可能来自普遍成功，也可能来自普遍失败。

核心问题在于 set agreement 是纯粹的序数度量。它记录哪个动作"胜出"，却不记录绝对的性能水平。当所有动作几乎必然失败时，它们在零奖励上打平，独立运行以高概率产生相同的并列集合。由此得到的一致率是共同失败的产物，而不是质量的信号。我们通过一个 set-path symmetry 结果（命题 4.1）把这一观察形式化。对两个等成本的 Bernoulli 动作，参数 (0.9, 0.8) 与 (0.2, 0.1) 在任何样本量下都产生相同的"观测最佳动作集合"分布；任何仅基于哪个动作胜出的程序都无法区分这两种机制。缺失的信息是一个标量——汇总成功概率，它需要观测实际结果。此外，我们证明精确的总体平局在有限时间内不可能被认证（式 (35)）；而且即使有了结果，结果到 checkpoint 的指派所携带的信息也超出边际分布。在保持每个动作的结果多重集不变的前提下置换 checkpoint 与动作的绑定，会改变 8% 到 13% 的单元格级结论。

我们在两种机制上实证确认了这种脱节。在 RecoveryBench 上，我们在三个 GPT-5.6 模型（Luna、Terra、Sol）和三个恢复动作（retry、verify、replace）上评估了 864 个冻结 episodes，每个动作抽样八次。k=1 时一致率达到 85.4%，但 held-out success 只有 1.4%，而这一致率完全由全零比较驱动。按一致率挑选模型只能达到 1.3% 的 held-out success，而按平均结果挑选可达 6.5%。在两个规划队列共 3,456 条响应、24 个冻结 checkpoint 上，当每个动作的样本预算从 1 增至 4 时，一致率下降五倍，而 held-out success 稳定在约 76%。按结果质量分解一致率可见，下降完全由平局消解驱动：k=1 时多动作匹配占总一致率 0.318 中的 0.310，到 k=4 降至 0.125，而单例（singleton）一致率仅略微上升。另一个覆盖 rank、path、filter 任务的 Qwen3-8B 面板证实这一模式可推广到 GPT-5.6 家族之外。

我们还验证了用于统计认证最佳动作的 Hoeffding 证书，表明只有在间隔（margin）很大时认证才切实可行（间隔 0.40 时 128 个分支达 97.9%），而间隔为 0.06 时即使 512 个分支仍低于 0.1%。在 agent 恢复实验中通常观察到的间隔（5 到 10 个百分点）下，要认证唯一的最佳动作需要每个动做成百上千次执行，远超当前的评估预算。

我们的贡献如下：

- **Identification theory（识别理论）。** 我们证明最佳动作集合序列能够识别偏好间隔（preference gap），但不能识别绝对成功概率——我们把这一性质称为 set-path symmetry。汇总成功概率消解了这一歧义。我们还证明精确的总体平局在有限时间内不可能被认证，并把识别集刻画为一个双元素参数族（式 (4)）。
- **Empirical evidence（实验证据）。** 我们在 864 个冻结 RecoveryBench episodes 和两个规划队列（3,456 条响应，覆盖 GPT-5.6 与 Qwen3-8B 模型）上把 set agreement 与 held-out success 一起评估，表明一致率与质量可以朝相反方向变化。一致率分解、容差敏感性与跨任务分析证实：驱动观测一致率的是平局结构，而不是动作质量。
- **Record provenance（记录来源）。** 我们证明 checkpoint 与动作的绑定携带超出边际结果分布的信息。在保持每个动作结果多重集不变的前提下置换这些绑定，会改变 8% 到 13% 的单元格级结论——这一错误率超过典型的测量噪声，且仅凭结果数据无法察觉。
- **Practical recommendations（实用建议）。** 我们建议报告四个诊断量（agreement、全零比较的比例、held-out success、pooled success），无需额外数据采集即可让这一失效模式显形。我们给出统计认证界，并在现实间隔下演示其样本需求。
## 2 相关工作（Related Work）

**Agent recovery（Agent 恢复）。** ReAct（Yao et al., 2023）、Reflexion（Shinn et al., 2023）与 AutoGen（Wu et al., 2023）提供了用于推理、自我改进与多 agent 协作的 agent 架构。AgentBench（Liu et al., 2024）与 WorkflowLLM（Fan et al., 2025）在多种环境中评估 agent。重放与恢复研究（Gonuguntla, 2026；Shah, 2026；Qi et al., 2026）考察从部分执行出发的干预。执行编辑（execution-edit）安全工作研究 checkpoint、fork、restore 与 merge 语义（Zheng et al., 2026）。RecoveryBench（Tan et al., 2025）从重放失败状态上的恢复成功率导出模型比较。我们证明它的 set-agreement 读出无法区分成功恢复与共同失败。

**Identification 与 best-arm selection（最佳臂选择）。** 部分识别（partial identification；Manski, 2003；Christensen et al., 2022）刻画与观测相容的目标，集合值决策（set-valued decisions；Fuentes-Vicente et al., 2026）保留尚未消解的备选项。固定置信度的 best-arm identification（Garivier & Kaufmann, 2016；Kaufmann & Kalyanakrishnan, 2013）返回最优臂，而多答案形式（Degenne & Koolen, 2019）允许任何正确答案。我们的设定与它们不同：最大化集合的基数在任意小的扰动下都可能变化，从而导致精确平局的认证在有限时间内不可能（式 (35)）。选择性预测（selective prediction；Geifman & El-Yaniv, 2017；Liu et al., 2026）允许弃权，我们的认证规则与之精神相通。EC2（Golovin et al., 2010）作为我们的检索基线。

**Repeated evaluation 与 provenance（重复评估与来源追溯）。** Stable Ranking Probability（Riley et al., 2024）与重复 LLM 评估（Alvarado Gonzalez et al., 2025）主张分别报告稳定性与质量。Provenance 方法（Wang, 2026a；Liao, 2026；Zhu & Chang, 2026）把动作与其支撑记录联系起来。我们补充了结果规律（outcome law）与 checkpoint 指派之间的形式化关联。附录 C 比较了这些设定下的目标、观测与假设。

## 3 Checkpoint 设定与决策目标（Checkpoint Setting and Decision Targets）

**Setup and notation（设定与记号）。** 我们把图 1 所示的评估流程形式化。固定一个 checkpoint 状态 s（例如一个失败的任务及其当前的部分结果）、一个有限的恢复动作集 A₀，以及一份评分契约（scoring contract）。每个动作 a 有成本 C(a)，由 λ ≥ 0 加权。执行动作 a 后，我们观测到一个二值结果。记 q̂_s(a) 为其样本均值减去成本惩罚 λC(a)。一个参考模型在同样的成本调整下给出期望分数 Q^sc(s, a)。关键集合是

$$R_s = \arg\max_{a \in A_0} Q^{sc}(s, a), \qquad \hat{L}^{obs}_s = \arg\max_{a \in A_0} \hat{q}_s(a), \qquad \hat{I}^{obs}_s = R_s \cap \hat{L}^{obs}_s. \tag{1}$$

这里 R_s 是 reference-best 集合，L̂^obs_s 是观测到的最佳动作集合（保留所有平局），Î^obs_s 是二者的交集。exact-set agreement 在同一 checkpoint 上比较不同独立执行块的 L̂^obs_s；当两个块给出相同的集合时，它们一致。

**Expected 与 observed 偏好。** 设 P 是二值成功 Y_{s,a} ∈ {0, 1} 的真实结果规律。期望最佳动作集合为

$$A^\star(P) = \arg\max_{a \in A_0} \{ E_P[Y_{s, a}] - \lambda C(a) \}. \tag{2}$$

观测集合 L̂^obs_s 估计 A⋆(P)，但可能因抽样噪声和平局而与之不同。核心问题是：对 L̂^obs_s 的一致——也就是独立运行选择同一组"赢家"这一事实——是否意味着关于这些赢家质量的任何信息，即 A⋆(P) 中的动作是否真的会成功。

**为什么小预算下平局占主导。** 考虑三个恢复动作各执行一次（k=1），结果为二值。如果三个都失败（在困难 checkpoint 上这是常见情形），每个动作都得零分，观测到的最佳动作集合就是 A₀ 本身。第二次独立运行若同样全部失败，就给出相同集合，于是得到完美一致——尽管对相对动作质量毫无信息。随着 k 增大，经验平局变少，一致率下降，但动作质量并未改变。这一由平局驱动的机制，是我们实验中一致率虚高的主要来源。

**Record provenance（记录来源）。** 除了结果本身，结果到 checkpoint 的指派也很重要。归档结果可能按动作分组，却不保留哪个 checkpoint 产生了哪次执行。我们在 5.3 节表明：在保持每个动作结果分布不变的前提下置换这些绑定，会改变 8% 到 13% 的单元格级结论。记录资格（record eligibility）的形式化定义与完整的审计契约见附录 A。

![图1：checkpoint 评估流水线总览](docs/papers/arXiv-2609.34215.pdf)

**图 1：checkpoint 评估流水线总览（原文位置：PDF 第 2 页）。** 步骤 1：冻结一个失败的 checkpoint 状态，并配上多个候选恢复动作（如 tool call、replan、retry、switch strategy）。步骤 2：每个动作从同一 checkpoint 出发、以不同随机种子独立执行多次。步骤 3：为每个"动作–运行"对记录二值结果（成功或失败），形成一个结果矩阵。步骤 4：对每次运行，选出总分最高的所有动作（保留平局）构成最佳动作集合，得到一组最佳动作集合，作为一致率与质量分析的基础。
## 4 仅靠 set agreement 为何不够（Why Set Agreement Alone Is Insufficient）

### 4.1 最佳动作集合无法识别成功概率（Best-action sets do not identify success probabilities）

我们把核心问题形式化。知道哪个动作"胜出"，通常并不能揭示恢复是否真的有效。考虑两个等成本的恢复动作，其结果独立且服从 Bernoulli 分布：Y_{a,t} ~ Bernoulli(p_a)，p_a ∈ (0, 1)，动作 a ∈ {1, 2}，轮次 t。经过 n 轮后，我们只保留观测到的最佳动作集合（这是 set agreement 报告中的标准做法）：

$$S_n = \arg\max_{a \in \{1,2\}} \sum_{t=1}^{n} Y_{a, t}, \qquad n \ge 1. \tag{3}$$

下面的结果表明，整条序列 (S₁, S₂, …) 无法区分高质量恢复与低质量恢复。

**命题（set-path symmetry）。** 令 P = (p₁, p₂)，P† = (1 − p₂, 1 − p₁)。完整的带标签路径 (S_n)_{n≥1} 在 P 与 P† 之下同分布。对任何仅基于这条路径选择的动作，它在一次新执行上的成功概率在两种规律之间恰好移动 1 − p₁ − p₂。

**证明。** 令 Y†_{1,t} = 1 − Y_{2,t}，Y†_{2,t} = 1 − Y_{1,t}。它们是服从规律 P† 的独立 Bernoulli 变量，并满足 Y†_{1,t} − Y†_{2,t} = Y_{1,t} − Y_{2,t}。由于累积差在每一轮都相同，带标签路径完全重合，包括平局在内。

**例子。** 取 (p₁, p₂) = (0.9, 0.8)，(p†₁, p†₂) = (0.2, 0.1)。两种情形下动作 1 都是唯一最优，且间隔同为 0.1。然而第一种情形 p₁ = 0.9，第二种情形 p†₁ = 0.2。仅凭路径估计最佳成功概率的 minimax 误差为 |1 − p₁ − p₂|/2（式 (54)）。把所有结果翻转（互换成功与失败）不会改变哪个动作更好——一个更常成功的动作也更少失败。然而这次翻转把高成功机制变成了低成功机制。任何只依赖相对表现的统计量，对这种翻转都是盲的。

**识别集（identified set）。** 为了刻画与路径规律相容的所有参数，令 u = Pr(S₁ = {1})，v = Pr(S₁ = {2})，d = u − v，h = 1 − 2(u + v) + d²。求解恰好得到两个相容的参数向量：

$$\Theta(u, v) = \left\{ \left( \frac{1 + d + \eta h}{2},\ \frac{1 - d + \eta h}{2} \right) : \eta \in \{-1, 1\} \right\}. \tag{4}$$

二者共享间隔 d = p₁ − p₂ 与相同的期望最佳动作集合，但每个坐标相差 h = |1 − p₁ − p₂|。

**消解（resolution）。** 若汇总成功概率 m = (p₁ + p₂)/2 已知，则两个均值都被识别：p₁ = m + d/2，p₂ = m − d/2。因此缺失的信息是一个标量——总体成功水平，而它需要观测结果，而不只是赢家。附录 G.3 处理有限样本估计。

### 4.2 认证极限：精确平局与分离间隔（Certification limits: exact ties and separated margins）

即使手头有结果，认证期望最佳动作集合仍面临根本性的限制。

**精确平局无法被认证。** 如果两个或更多动作在总体层面精确平局，任意小的扰动都会改变该集合。任何在所有可容许规律之下把错误认证水平控制在 δ 的程序，即使无限抽样，也只能以至多 δ 的概率在有限时间内认证这样的平局（式 (35)；证明见附录 C.4）。

**间隔足够大时唯一赢家可被认证。** 当存在唯一最佳动作——即某个动作的期望分数严格高于其余所有动作——原则上可以用有限数据认证它。对每个动作 n 次执行，同时 Hoeffding 界（Hoeffding, 1963）给出一个置信集。令 q̂_n(a) 为动作 a 的样本均值减去成本惩罚 λC(a)。对 |A₀| ≥ 2 个动作与错误水平 0 < δ < 1：

$$\rho_n(\delta) = \sqrt{\frac{\log(2|A_0|/\delta)}{2n}}, \qquad \hat{W}^{\mathrm{rob}}_{\delta, n} = \left\{ a \in A_0 : \hat{q}_n(a) > \max_{b \ne a} \hat{q}_n(b) + 2\rho_n(\delta) \right\}. \tag{5}$$

以至少 1 − δ 的概率，Ŵ^rob 中的任何动作都是唯一的期望最佳动作。当 Ŵ^rob 为空时该规则弃权，而间隔相对于 n 太小时就会出现这种情况。实践中，间隔 0.40 在 n = 128 时接近完全认证；而间隔 0.06 即使到 n = 512 仍未解决（见 5.4 节）。

### 4.3 记录指派改变 checkpoint 结论（Record assignments change checkpoint conclusions）

checkpoint 比较不仅取决于结果，还取决于哪些结果被指派给哪些 checkpoint。归档结果可能按动作分组，却不保留其 checkpoint 绑定。这即使在每个动作的结果多重集完全已知的情况下也会造成歧义。

**配对为何重要。** 假设两个结果规律 P⁺、P⁻ 有不同的最佳动作集合，两条执行记录 z⁺、z⁻ 具有不同的资格（一个通过来源检查，另一个没有）。同样的规律与记录可以按两种方式配对：对角配对（P⁺ 配 z⁺，P⁻ 配 z⁻）或交叉配对（P⁺ 配 z⁻，P⁻ 配 z⁺）。两种配对都与同样的边际观测相容，但对"哪个最佳动作集合由合格记录支撑"给出相反的结论。因此，结果到 checkpoint 的指派携带了超出边际结果分布所含内容的信息。我们在 5.3 节以实验检验这一预测。形式化构造（相容的规律–记录关系及其目标像）见附录 A。

**统计认证。** 对没有 checkpoint–动作标识符的执行块，我们使用 Clopper–Pearson 区间（Clopper & Pearson, 1934），并在动作集上做 Bonferroni 校正（Bonferroni, 1936），构造同时置信区域。被认证的最佳动作集合是该置信区域与可能的最大化者集合的交集（附录 C.4）。
## 5 实验（Experiments）

我们在一个由失败 checkpoint 组成的冻结 RecoveryBench 面板和两个规划队列上，把 exact-set agreement 与 held-out success 一起评估。执行记录来自 Qwen3-8B（Yang et al., 2025）和 GPT-5.6 家族（OpenAI, 2026）的 Luna、Terra、Sol。核心目标是判断高 set agreement 能否预测成功的恢复。所有实验都使用冻结 checkpoint——agent 状态从保存的快照重放，从而保证唯一的变异来源是恢复动作与解码随机性。每个实验把抽样划分为 selection block（用于确定最佳动作集合）和 held-out block（用于评估所选动作的质量）。完整的协议、统计单元与不确定性分析见附录 B。

### 5.1 RecoveryBench：高一致率、低成功率（High agreement, low success）

我们把整套集合读出应用于 RecoveryBench（Tan et al., 2025）中 12 个冻结的失败 Terminal-Bench（Merrill et al., 2026）checkpoint。每个 checkpoint 用三个 GPT-5.6 模型、以及 retry、verify、replace agent 三个动作评估，每个动作重复八次（共 864 个 episodes）。重复 0–3 构成 selection block，重复 4–7 构成 held-out block。对每个 k ∈ {1, 2, 4}（每个动作的抽样数），selection block 给出一个完整的原生奖励（native reward）最大化者集合，并与 held-out 集合比较。成功定义为原生验证器奖励 > 0。

k=1 时，Luna 的一致率达到 85.4%，而 held-out success 仅 1.4%（表 1）。全零对（all-zero pairs）的比例在 k=1 时恰好等于 Luna 的一致率（表 1），说明每一次匹配比较都完全由零奖励尝试构成。模型们之所以在"哪个动作最佳"上完美一致，是因为它们谁也没有成功过。

**表 1：12 个失败 checkpoint 上的 RecoveryBench 验证。** 每个模型行报告 k = 1、2、4（每个动作的抽样数）下的一致率、全零对与 held-out success。Agreement 跨块比较原生奖励最大化者集合；all-zero pairs 是"两个块中所有动作都得零分"的匹配比较所占比例。held-out success 评估所选集合；区间见附录表 47。

| Model | Agreement k=1 | Agreement k=2 | Agreement k=4 | All-zero pairs k=1 | All-zero pairs k=2 | All-zero pairs k=4 | Held-out success k=1 | Held-out success k=2 | Held-out success k=4 |
|---|---|---|---|---|---|---|---|---|---|
| Luna | 0.854 | 0.750 | 0.667 | 0.854 | 0.750 | 0.583 | 0.014 | 0.014 | 0.014 |
| Terra | 0.776 | 0.688 | 0.583 | 0.776 | 0.688 | 0.583 | 0.045 | 0.035 | 0.014 |
| Sol | 0.734 | 0.627 | 0.417 | 0.708 | 0.590 | 0.417 | 0.083 | 0.075 | 0.063 |

这一模式在三个模型和三种预算上都成立（表 1）：没有任何跨块配对在两个块中对所有动作都取得正奖励（"全部成功"的频率恰好为 0）。在 checkpoint 层面，一致率与 held-out success 呈负相关，k=1 时 Spearman 估计介于 −0.796 到 −0.443 之间（附录表 50）。恢复偶尔奏效的 checkpoint 产生的一致率更低，因为随机出现的成功打破了"普遍失败"式的平局。如果假设"一致率是质量的信号"，那么高一致率应当预示高成功率；然而事实正相反，一致率最高的 checkpoint 恰恰是任何动作都不成功的那些。

**按一致率选 vs. 按结果选。** k=1 时，按一致率挑选模型与动作只能达到 1.3% 的 held-out success，而按平均结果挑选可达 6.5%（附录 H）。因此，用 set agreement 选动作的从业者，会比简单选最高平均分的人表现更差——哪怕那个平均分本身不高。在 864 个 episodes 中，364 个有原生验证器观测，487 个带模型协议失败（model-protocol failure），13 个是无效的 adapter 尝试（附录表 49）。协议失败的普遍性解释了成功率为何如此之低：大多数 episode 根本走不到验证器，因为模型没能遵循恢复协议——但这些失败仍然产生零奖励结果，并照样计入一致率。

**增大 k 消解平局，却降低一致率。** k 从 1 增到 4，三个模型的一致率都下降，例如 Luna 从 0.854 降到 0.667，Sol 从 0.734 降到 0.417（表 1）。正如 set-path symmetry 结果所预测的，观测越多，经验平局越不可能出现，最佳动作集合变得更小、波动更大。然而 held-out success 在各预算下基本不变：无论 k 取何值，Luna 始终是 1.4%（表 1），这证实一致率的下降反映的是平局消解，而非质量退化。

### 5.2 规划任务：一致率下降而质量保持（Agreement drops while quality holds）

RecoveryBench 的结果在"近乎普遍失败"的机制中展示了这种脱节。下面的规划实验则检验：当动作具有中到高的成功率时，脱节是否依然存在。

我们用 GPT-5.6 的 Terra、Luna、Sol 评估两个冻结的 24-checkpoint 规划队列。每个"模型–队列"面板有三个恢复动作、每个动作八次抽样（每个面板 576 条响应，六个面板共 3,456 条）。研究队列（study cohort）先设计，复现队列（replication cohort）则独立抽取，用于检验发现能否复现。抽样被划分为 selection 与 evaluation 两块。对每个 k ∈ {1, 2, 4}，selection block 中所有大小为 k 的子集构成一个完整的公开分数（public score）最大化者集合。固定 verify（在单独的开发面板上选出）作为单次调用的基线。完整协议详见附录 G。

在全部六个面板上，exact agreement 从 k=1 到 k=4 都在下降（表 2），降幅介于 0.039 到 0.320 之间。复现队列中的 Terra，一致率从 40.4% 跌到 8.3%，缩为五分之一。然而 held-out strict success 大体稳定：k=1 时"所选减固定"的差值介于 −0.072 与 −0.006 之间，且复现队列中每个 95% bootstrap 区间都包含零。可见一致率主要跟踪的是平局结构，而非动作质量。这一模式在能力不同的模型上同样成立：最强的模型 Sol 在每个预算下一致率都最低，因为它更高的成功率给结果带来更多变化，破坏了弱模型靠"共同失败"维持的平局。

**表 2：GPT-5.6 在两个冻结队列上的规划结果（点估计；区间见附录表 39、40）。** Agreement 跨块比较公开分数最大化者集合；selected strict success 在 held-out 抽样上评估所选的动作混合。

| Cohort | Model | Set agreement k=1 | k=2 | k=4 | Selected strict success k=1 | k=2 | k=4 | Fixed verify |
|---|---|---|---|---|---|---|---|---|
| Study | Terra | 0.318 | 0.204 | 0.167 | 0.699 | 0.695 | 0.710 | 0.771 |
| Study | Luna | 0.234 | 0.150 | 0.083 | 0.575 | 0.568 | 0.538 | 0.635 |
| Study | Sol | 0.424 | 0.331 | 0.167 | 0.722 | 0.729 | 0.750 | 0.729 |
| Replication | Terra | 0.404 | 0.238 | 0.083 | 0.765 | 0.754 | 0.762 | 0.771 |
| Replication | Luna | 0.299 | 0.212 | 0.250 | 0.727 | 0.728 | 0.719 | 0.760 |
| Replication | Sol | 0.497 | 0.422 | 0.458 | 0.808 | 0.814 | 0.825 | 0.844 |

**一致率下降的来源。** 表 3 把原始 Terra 面板上的一致率分解为两部分贡献：单例匹配（两个块都选出唯一赢家）与多动作匹配（两个块保留同一个并列集合）。k=1 时，一致率几乎全部来自多动作匹配（0.318 中的 0.310）——两个块之所以一致，是因为大多数 checkpoint 在三个动作之间产生了平局。随着 k 增大，平均集合大小从 2.29 缩到 1.52，多动作一致率从 0.310 降到 0.125，而单例一致率只略微上升。成功与否全程不变：平局消解不影响哪些动作有效，只影响哪些动作被宣布为"最佳"。

一个 Bernoulli 对照从解析上证实了这一机制。设三个等成本动作的成功概率都是 0.9，单次抽样的一致率是 0.553，四次抽样时降到 0.183；然而期望成功率仍是 0.9。若成功概率是 0.1，单次抽样的一致率同样是 0.553——这正体现了动作层面的 set-path symmetry（附录 G.3）。

**表 3：原始 24 个规划 checkpoint 上集合一致率的分解（Terra）。** Single 与 Multiple 是按匹配集合大小划分的、对 Agreement 的互斥贡献；Mean size 对两个块取平均；Success 在 held-out block 上评估所选动作。

| k | Agreement | Single | Multiple | Mean size | Success |
|---|---|---|---|---|---|
| 1 | 0.318 | 0.008 | 0.310 | 2.286 | 0.699 |
| 2 | 0.204 | 0.039 | 0.164 | 1.913 | 0.695 |
| 4 | 0.167 | 0.042 | 0.125 | 1.521 | 0.710 |

复现队列独立证实了一致率的下降（表 2），并呈现同样的模式：一致率下跌而成功稳定。不要求自报总数正确也能算出收益，且两个面板中下降依然保持（附录 G.4）。覆盖 rank、path、filter 任务的 12-checkpoint Qwen3-8B 面板在 k=1 时给出 84.0% 的 strict agreement，同时所选动作成功率为 37.9%（附录表 46）。这里匹配集合同样既包含"全部失败"也包含"全部成功"的块：k=1 时多动作匹配集合贡献了 0.840 一致率中的 0.831，且 58.3% 的一致配对在两个块中最高分都为零（附录 G.7）。strict 成功集中在 rank 与 filter 任务族：path 任务族贡献为零，但三个任务族都产生高一致率。

**任务难度的作用。** 在两个队列中，一致率与成功率之间的脱节在两种机制下最明显：(i) 所有动作都成功的简单任务（一致率来自普遍成功）；(ii) 所有动作都失败的困难任务（一致率来自普遍失败）。只有中等难度的任务——部分动作成功、部分失败——才产生有信息量的不一致，而这些恰恰是"一致率本该对选动作有用"的情形。换句话说，set agreement 在最被需要的地方，信息量最少。

**经验近平局。** 提升一致率的一个自然想法是软化 exact-set 比较：保留所有与最佳均分差距在容差 εU_s 以内的动作，其中 U_s 是分数极差。这把"接近赢家"变成了"共同赢家"，吸收小幅波动。表 4 在 k=4 下对两个容差与精确比较做了评估，结果好坏参半：一个队列中一致率略有上升（从 0.083 到 0.250），另一个队列反而下降（从 0.167 到 0.125）。两种情况下 held-out success 都几乎没有变化。容差并不能可靠地改善一致率；即便改善了，反映的也是近平局被吸收，而不是关于动作质量的信号变好。全部容差与预算见附录 G.5。

**表 4：k = 4 时在每队列 24 个 checkpoint 上的经验容差敏感性。** Strict 是 held-out block 上的所选动作成功率；Public 是归一化的可行收益。

| ϵ | Original Terra：Agreement | Strict | Public | Independent Terra：Agreement | Strict | Public |
|---|---|---|---|---|---|---|
| 0.000 | 0.167 | 0.710 | 0.668 | 0.083 | 0.762 | 0.695 |
| 0.020 | 0.167 | 0.707 | 0.669 | 0.208 | 0.748 | 0.689 |
| 0.050 | 0.125 | 0.714 | 0.670 | 0.250 | 0.748 | 0.689 |
| 0.100 | 0.125 | 0.714 | 0.670 | 0.250 | 0.748 | 0.689 |

### 5.3 记录指派改变比较结论（Record assignments change comparisons）

我们检验 4.3 节的预测：在保持每个动作结果不变的前提下改变 checkpoint 指派，可以改变结论。在 48 个本地归档单元格（Qwen3-8B，12 个前缀 × 4 种故障）上，我们固定全部输出，只置换它们的 checkpoint 指派。

**表 5：48 个归档单元格上的置换控制。** "Changed" 统计置换关系与精确键控参考关系不同的单元格；各列报告单元格比例的中位数。

| Association | Direct | Overlap | Discordant | Changed | Mean set size |
|---|---|---|---|---|---|
| Independent permutation | 0.042 | 0.417 | 0.542 | 0.125 | 1.813 |
| Shared permutation | 0.042 | 0.438 | 0.521 | 0.083 | 1.875 |
| Exact keyed | 0.042 | 0.458 | 0.500 | 0.000 | 1.875 |

共享置换与独立置换在中位数上分别改变 48 个单元格结论中的 4 个和 6 个（表 5），尽管它们保持了每个动作的结果多重集。这一结果证实了 4.3 节的预测：checkpoint 与动作之间的绑定携带超出边际结果分布的信息。置换后只有 4.2% 的单元格仍保留单例的联合目标（表 5），也就是说，对大多数单元格而言，多种 checkpoint–动作指派都与同样的结果相容，而不同指派导致不同结论。如果评估流水线没有记录哪个 checkpoint 产生了哪次执行（例如因为批处理或异步派发），由此产生的置换绑定就会悄悄污染 8% 到 13% 的单元格级结论——超过 agent 评估中的典型测量噪声，且仅凭结果数据无法察觉。

在一次单独的检索审计中，EC2（Golovin et al., 2010）需要 26 次查询才能确定全部"动作–资格"结论，而 eligibility-first 结算只需 19 次（附录 F.9）。一个受限的候选类只覆盖 192 个规范元组中的 14 个，导致三个选择器在同样的三个单元格中都错误停止（附录 F.8）。

### 5.4 认证需要大间隔（Certification requires large margins）

我们在间隔已知的受控分布上验证 Hoeffding 证书（式 (5)；见图 2）。当间隔很大（0.40）时，有效认证率从 64 个分支时的 40.5% 升到 128 个分支时的 97.9%。相反，当间隔很小（0.06）时，即使每个动作 512 个分支，认证率仍低于 0.1%。在全部 36 个嵌套单元格与 10 种预算下都没有观察到错误证书（附录表 11）。在 agent 恢复实验中通常观察到的间隔（5 到 10 个百分点的成功率差）下，认证唯一的最佳动作需要每个动做成百上千次执行，远超当前评估预算。在一个 12-checkpoint 开发试点中（每动作 32 次抽样），只有一个逐点证书为正，而同时校正后全部悬而未决（附录 G.8）。因此，当前大多数评估都运行在"统计认证不可行"的机制里——这凸显了在一致率之外同时报告结果水平的重要性。认证所需与预算所能提供之间的差距，也解释了从业者为何一开始就默认使用 set agreement：它是唯一在小样本量下能给出确定答案的指标，尽管那个答案对质量毫无信息量。

**改变放行目标。** 在 10,000 次受控放行中（附录表 22），要求 replay 动作属于期望最大化者集合（overlap 目标）会接纳总体平局，而要求它是唯一赢家（unique-winner 目标）则会排除平局。在 overlap 目标下，status-aware 集合成员规则接纳的正例比完整门（full gate）更多、且没有观察到错误；而在 unique-winner 目标下，完整门的错误更少。两种规则下，记录检查都消除了构造出来的来源缺口错误（附录 E.3）。可见放行目标的选择有重大的实际后果：它决定了一个评估能支撑哪些结论、以及需要什么证据。

![图2：认证集大小与阈值门晋升率随分支预算的变化](docs/papers/arXiv-2609.34215.pdf)

**图 2：（A）平均认证集基数随样本预算的变化。** 间隔很大（0.40）时，集合在约 32 个分支处缩为单例；近平局（0.06）到 512 个分支仍未解决。support-only 包络（斜纹）始终保留全部三个动作。（B）阈值门晋升率：大间隔在 128 个分支处接近完全认证，近平局即使到 512 个分支仍低于 0.1%。所有条件下均未观察到错误证书（原文位置：PDF 第 8 页）。
## 6 讨论（Discussion）

一个一致的模式跨越不同基准、模型与样本预算反复出现：即使恢复性能接近零，set agreement 也可能很高——因为"共同失败"产生一致率的效率，与"共同成功"一样高。set-path symmetry（4.1 节）把这一点讲精确了：Bernoulli 参数 (p₁, p₂) 与 (1 − p₂, 1 − p₁) 给出完全相同的最佳动作集合分布。RecoveryBench 实验在经验上证实了它：85.4% 的一致率与 1.4% 的成功率并存。规划实验则把这一发现扩展到"恢复确实有效"的机制：样本预算增长时，一致率从 40% 掉到 8%，而 held-out success 保持稳定。

这些结果促成几条具体建议。每一份 set agreement 报告都应附上全零比较的比例、held-out success 与汇总成功概率——这些量都可以从已有数据算出。一致率应按结果质量分解，以揭示它究竟由共同失败、共同成功还是有信息量的区分所驱动。一致率随样本预算的下降不应被解读为质量下滑，因为它可能反映平局消解而非性能退化。最后，评估流水线应当记录 checkpoint 与动作的绑定，因为我们的置换实验表明，丢失这些绑定会悄悄污染 8% 到 13% 的单元格级结论。

**局限。** 我们的实验只使用二值结果。对连续值指标，对称性论证需要调整，不过"序数排名不能决定绝对水平"这一洞见在定性上依然成立。RecoveryBench 实验覆盖 12 个 checkpoint、三种恢复动作，更丰富的动作空间会加强实证结论。我们没有提出或评估更复杂的动作选择算法（如 Thompson sampling 或 UCB 变体），这仍是自然的后续方向。最后，我们的分析假设各轮之间是独立的 Bernoulli 结果；实践中 LLM 输出可能因温度或种子复用而呈现自相关，这可能同时影响一致率与认证率。

**附录导读。** 定义与证明集中在附录 A；重放实验与统计单元规定于附录 B。附录 C 展开识别边界，并与既有工作比较。受控证据研究见附录 D，更多关系审计见附录 E。执行归档与绑定检索记录于附录 F；前瞻性的重复分支研究见附录 G；冻结 RecoveryBench 面板与按状态分层的分析见附录 H。

## 附录 A 定义与证明（Definitions and Proofs）

本附录把 checkpoint 审计所用的"相容规律–记录关系"形式化，并证明相关认证主张。我们先定义契约与相容对，再导出正文所用的目标像。

### A.1 偏好与放行的联合识别（Joint identification of preference and release）

**审计契约。** 审计契约 κ 指定：checkpoint 状态空间 S、带成本 C : A₀ → R≥0（由 λ ≥ 0 加权）的恢复动作集 A₀、结果规律类 P_s，以及可容许的"规律–记录"关联 K^{joint}_{κ,s}。每个状态 s 有一个选择器可见的签名 o = ϕ(s)。契约固定可观测输入；评估器一侧的故障标签、答案键与未执行的反事实结果一律排除在外。

**相容对。** 给定观测结果 y 与记录字段 x，与 y 相容的结果规律集合为 P_s(y) := {P ∈ P_s : y ∈ supp(P)}，与 x 相容的记录为 Z^{all}_{κ,s}(x) := {z ∈ Z^{all}_{κ,s} : ψ_κ(z) = x}。相容关系取二者笛卡尔积与可容许关联的交：

$$H_{\kappa, s}(y, x) := \big( P_s(y) \times Z^{all}_{\kappa, s}(x) \big) \cap K^{joint}_{\kappa, s}. \tag{6}$$

当它等于完整的积 P_s(y) × Z^{all}_{κ,s}(x)（即该关联不施加任何额外约束）时，我们称这个关系是 raw-rectangular 的。

**源键与候选桥。** 源键 ℓ⋆（例如一个模型标识符）可以在计算任何目标之前限制该关系：B^{[ℓ⋆]}_{κ,s} 只保留记录映射到键 ℓ⋆ 的那些对。候选桥（candidate bridge）B 是一个声明出来的"规律–记录"对子集，代表一个假设的数据生成过程。在桥 B 之下、与观测数据相容的 checkpoint 状态集合为

$$S^{B}_{\kappa|o}(\ell^\star; y, x) := \{ s : \varphi(s) = o,\ B^{[\ell^\star]}_{\kappa, s} \cap \big( P_s(y) \times Z^{all}_{\kappa, s}(x) \big) \ne \emptyset \}. \tag{7}$$

两个桥系统若给出相同的"状态–规律–记录"相容元组集合，则称它们观测等价。与数据相容的全部候选桥组成的集合记作 B_{κ|o}(y, x, ℓ⋆) := {B ∈ B_cand : S^B_{κ|o}(ℓ⋆; y, x) ≠ ∅}。

### A.2 总体记录与固定状态目标（Population records and fixed-state targets）

**从单个 checkpoint 到总体。** 当评估覆盖 checkpoint 总体 D ⊆ S 时，记录空间与规律空间都是各 checkpoint 的积：Z^{all}_{κ,D} := ∏_{s∈D} Z^{all}_{κ,s}，P_{κ,D}(y) := ∏_{s∈D} P_s(y_s)。总体层面的相容关系要求每个"逐 checkpoint"的对都是可容许的，其目标像把各 checkpoint 的 overlap 集合与一个总体层面的资格位一起收集起来。对单个 checkpoint（|D| = 1），这就退化为固定状态情形；对更大的总体，它是一个向量值目标，不能用标量摘要替代。

**记录资格。** 三项二值检查决定一条记录能否支撑可靠结论：completeness P_rec（所有必需字段齐备）、linkage P_link（可追溯到生成它的模型）、observability O_κ（评分契约可重新计算）。记 C_κ := P_rec · P_link · O_κ 为组合检查。逐 checkpoint 的 overlap 状态 v_s(z) ∈ {A, B, D, NA} 对观测与参考最佳动作集合的关系分类：相等（A）、相交（B）、不相交（D）、缺失（NA）。直接迁移资格要求所有检查通过、且不存在不相交或含糊的单元格：

$$D^{D}_{\kappa}(z) := \mathbb{1}\{ P_{rec}(z) = P_{link}(z) = O_{\kappa}(z) = 1,\ d^{D}(z) = b^{D}(z) = 0 \}, \tag{8}$$

其中 d^D(z) = 1{∃s : v_s(z) = D} 标记任何不相交单元格，b^D(z) 在"无不相交"的前提下标记含糊性。若资格不同的记录总能被某种可观测证据区分开，则称该证据更新是"真值可分的"（truth-separating）。

**目标像。** 相容关系的联合目标把每个存活的对 (P, z) 映到它的 overlap 集合 I_s(P) = R_s ∩ A⋆(P) 与资格 D_κ(z)：

$$\Gamma^{I}_{\kappa, s}(y, x) := \{ (I_s(P),\ D_{\kappa}(z)) : (P, z) \in H_{\kappa, s}(y, x) \}. \tag{9}$$

二值版本 Γ_{κ,s}(y, x) 把 I_s(P) 换成 T_s(P) = 1{I_s(P) ≠ ∅}（即 overlap 是否非空）。我们还把坐标投影分别记作 Γ^pref_s（偏好像）与 Γ^rel_{κ,s}（资格像）。

### A.3 配对、单例认证与候选覆盖（Pairing, singleton certification, and candidate coverage）

**精确像 vs. 边际包络。** 对规律与记录之间的关系 B，精确联合像 (I_s, D_κ)(B) 只收集实际被配对的"overlap 集合/资格"取值；而边际包络 I_s(pr_P B) × D_κ(pr_Z B) 取坐标投影的笛卡尔积，因而可能包含没有支撑的组合。精确像总是包含于包络之中；取等号时称该关系是 target-rectangular 的。然而，单例认证对这一区别免疫：

$$|\Gamma^{I}(B)| = 1 \iff |I_s(\mathrm{pr}_P B)| = |D_{\kappa}(\mathrm{pr}_Z B)| = 1. \tag{10}$$

**证明。** 单例的联合像迫使两个坐标都是单例；反之，单例坐标恰好产生一个笛卡尔对，而非空关系总能取到它。

**配对为何重要。** 这一区别在单例之外的情形非常尖锐。两个坐标投影完全相同、但"规律–记录"配对方式不同（对角 vs. 交叉）的关系，会产生不同的联合像：

$$\Gamma^{I}(B_{\mathrm{diag}}) = \{ (I^+, 1),\ (I^-, 0) \}, \qquad \Gamma^{I}(B_{\mathrm{cross}}) = \{ (I^+, 0),\ (I^-, 1) \}. \tag{11}$$

任何只看坐标投影的读出，对这两种关系给出相同答案，因而无法区分它们（表 6）。

**表 6：有限构造上的精确联合像查询。** N 是查询次数；Correct、FP、Miss 是各读出的计数。

| Query | N | Joint readout Correct | Joint FP | Joint Miss | Marginal readout Correct | Marginal FP | Marginal Miss |
|---|---|---|---|---|---|---|---|
| Possible image | 15 | 15 | 0 | 0 | 13 | 2 | 0 |
| Singleton | 15 | 15 | 0 | 0 | 15 | 0 | 0 |
| Hidden pairing | 2 | 2 | 0 | 0 | 1 | 1 | 0 |

**整集合认证。** 一个返回 CONTINUE(I†) 的门是可靠的（sound），当且仅当稳健候选像 Γ^{I,rob}_{κ|o}（在所有存活候选上的联合像，可能再受源键 ℓ⋆ 限制）等于单例 {(I†, 1)}。规范的整集合查询把这一单例检查与记录资格检查合在一起：

$$\mathrm{JointImage}^{\mathrm{rob}}_{\kappa}(I^\star \mid y, x) \iff \Gamma^{I, \mathrm{rob}}_{\kappa|o}(y, x; \ell^\star) = \{(I^\star, 1)\} \wedge C_{\kappa} = 1. \tag{12}$$

如果像等于上面那个单例，说明每个存活候选都共享同一个非空 overlap 集合、且拥有合格记录，因而晋升是可靠的。像中只要出现任何额外取值（不合格的记录、空 overlap、或不同的 overlap 集合），晋升就不可靠。

**活跃桥覆盖。** 上面的认证是相对于所声明的候选类而言的。要把它推广到活跃关系（真实的生成过程），我们需要每个可容许的活跃对都被某个候选桥覆盖：覆盖性（Coverage）保证"正的候选单例"对活跃关系同样可靠。若源键 ℓ⋆ 能分离可观测的桥类（Sep^{obs}_κ = 1），它会进一步细化候选纤维，使得该键下的单例像意味着规范整集合门返回 CONTINUE(I†)。

### A.4 动作集合的桥见证（Action-set bridge witness）

这个最小例子说明为什么桥（即"规律–记录"配对）必须是可观测的。考虑两个等成本动作 {r, v}，成功概率都是 0.90，但"谁胜出"不同：在规律 P_r 下动作 r 是唯一的期望赢家，在 P_v 下则是 v：

$$P_r = 0.90\,\delta_{(1,1)} + 0.10\,\delta_{(1,0)}, \qquad P_v = 0.90\,\delta_{(1,1)} + 0.10\,\delta_{(0,1)}. \tag{13}$$

每条规律与它自己的合格记录（z_r 或 z_v）配对，产生两个候选桥 B_r = {(P_r, z_r)} 与 B_v = {(P_v, z_v)}。它们的联合像都是指向相反赢家的单例：Γ^I(B_r) = {({r}, 1)}，Γ^I(B_v) = {({v}, 1)}。如果没有能识别"观测由哪条记录生成"的键，稳健像里两个正的动作集合都在其中，门便无法授权 Continue。只有当候选契约把源键单射地关联到对应规律时，源键才能消解这个歧义。

### A.5 安全边界与证据请求（Safety boundary and evidence requests）

派发器（dispatcher）通过最小化存活目标像 Γ 上的最坏情形损失，在 PROMOTE、HOLD 与 REJECT 之间做选择。令 θ = (T_s(P), D_κ(z)) 编码"overlap 是否非空"与"记录是否合格"，损失对错误晋升（false promotion）的惩罚高于漏掉晋升（c_FP > c_H > 0）：

$$\ell(a, \theta) = c_{FP}\,\mathbb{1}\{ a = \mathrm{PROMOTE},\ \theta \ne (1,1) \} + c_{H}\,\mathbb{1}\{ a \ne \mathrm{PROMOTE},\ \theta = (1,1) \}. \tag{14}$$

minimax 决策 G⋆(Γ) := arg min_d sup_{θ∈Γ} ℓ(d, θ)：当 Γ = {(1,1)} 时只包含 Promote，只要还有任何非正状态存活，就排除 Promote。

当像还不是单例时，派发器沿着每个未消解的坐标请求额外证据：

$$U_{\kappa, s}(H) = \{ \mathrm{Repeat} : \Gamma^{pref}_s = \{0, 1\} \} \cup \{ \mathrm{Collect} : \Gamma^{rel}_{\kappa, s} = \{0, 1\} \}. \tag{15}$$

Repeat 请求再做一次任务尝试，以消解偏好坐标；Collect 请求记录证据，以消解资格坐标。真值可分的证据（式 (A.2)）会把更新后纤维上的相应坐标压缩成单例。
## 附录 B 实验协议与重放控制（Experimental Protocols and Replay Controls）

### B.1 评估总体与统计单元（Evaluation populations and statistical units）

坐标压力审计在四种机制（eligible、near-tie、missing-linkage、insufficient-observability）中各抽取 2,000 个独立结果向量。单独的放行比较还有第五种 discordant 机制。获取研究使用 4,000 个受控状态，配以真实的信息性响应与 64 个配对种子；校准式选择使用 32 个校准种子与 32 个不相交的评估种子。偏好研究在 36 个嵌套单元格上、每个工作点使用 10,000 个独立向量。有限关系查询使用枚举出的真值，依赖性研究在积规律与耦合规律下复用 4,000 个潜在规格。

重放总体分为开发集、同分布（ID）集与结构性分布外（OOD）集。Qwen3-8B 归档（Yang et al., 2025）含 12 个前缀、四种故障、三个动作与两次重复（48 个单元格、288 个分支）；指派控制与不确定性按前缀聚类。严格的 score-aware 过滤器在 24 个开发前缀中保留 13 个、48 个 ID 前缀中保留 28 个、48 个 OOD 前缀中保留 27 个（共 68 个前缀、220 个留出的"前缀–故障"单元格）。

### B.2 工作流动作与执行记录（Workflow actions and execution records）

重放在一个共享目标下比较固定策略、仅状态（status-only）策略与学习得到的仅轨迹（trace-only）策略；迁移实验冻结选择器而移动重放核，完成率、重放效用与干预成本分别报告。Luna、Terra、Sol 在同一 48 单元格面上各为每个动作提供两次执行（每模型 288 个分支）；Qwen3-8B 提供一个具有同样两次重复预算的独立本地归档。GPT-5.6 第二次执行中的全部 144 个分支都满足严格谓词。汇总分数先对每个动作的两个严格结果取平均，再减去成本。严格有效性要求语义正确且公开分数一致；本地键把输出绑定到 checkpoint/动作指派，提供方（provider）的 linkage 另行处理，且为保证制品有效性、记录资格与观测关系，来源分组保持分离。提供方归档有 12 个留出前缀，其中 9 个满足严格的 score-aware 契约，构成 108 个分支的评估总体；其记录缺少完整的 linkage。

### B.3 比较规则与结果度量（Comparison rules and outcome measures）

放行比较固定分支；对 status-aware 规则，还固定所提供的记录信息。完整门把观测到的动作关系与记录检查结合；A-only 省去记录检查；集合成员与序列化 top-1 在平局处理上不同；Robust-95 要求统计上的分离。获取实验固定预算上限与最终资格判据，同时比较"精确/校准"选择与"固定本地/联合"请求模式；请求成本与覆盖率一起报告，且校准获取不计入校准评估的成本。

三类控制把关联隔离出来：有限构造在保持坐标投影的前提下改变"规律–记录"配对；依赖性研究在保持边际动作概率的前提下改变联合结果分布；归档控制在保持每个"动作 × 前缀"内多重集不变的前提下，把保留的输出重新指派给故障单元格。晋升与获取覆盖使用合格案例；错误与漏掉的计数使用各表所声明的分母。精确查询报告正确、无支撑与漏掉的计数，归档比较报告观测到的单元格关系变化，统计认证则报告固定预算下的有效证书与错误证书。

### B.4 任务构造与划分构成（Task construction and split composition）

该基准包含类型化有向无环图（DAG）上的排序（ranking）、路径选择（path-selection）与受限过滤（constrained-filtering）任务，变化深度、广度、信息视界与并行度。工作者产出结构化制品，对照确定性答案键评估。对任务图 D = (V, E, τ, δ)，τ 把节点映到有限类型，δ 存放带类型的载荷与依赖标注。故障 checkpoint 为 s = Ψ_f(s₀)；对动作 a 与生成器噪声 u ~ ν_{s,a}：

$$\omega = (B, g) = \mathrm{Branch}(s, a, u), \qquad K^{\mathrm{rep}, \kappa}(\cdot \mid s, a) = \big( Y^{Y, \kappa}_{s, a} \big)_{\#} K^{\mathrm{rep}, \mathrm{raw}}(\cdot \mid s, a). \tag{16}$$

这里 F 包含四个注入的故障面；Branch 覆盖类型化转移、制品物化与传播抽样，Clean 检查 schema、证据与语义。该契约固定共享的 checkpoint/动作接口，同时让重放规律与端点记录保持分离。

### B.5 轨迹表示与动作契约（Trace representation and action contract）

选择器收到：任务问题、转录前缀、中间制品、依赖上下文、验证器可见的检查项，以及公开的候选表。制品检查覆盖 status/schema/version、角色兼容性、候选成员资格、证据有效性、分数存在性与分数重算；结构特征记录深度、广度、信息视界与并行度。注入的故障、答案键、反事实分支与未来结果始终留在评估器一侧。

动作词表是 continue、retry、verify、replace agent，协议成本分别为 0、1、1、2；物化只使用三个恢复动作。重放效用减去级联惩罚 0.01G，而物化止于恢复出的制品，并使用共享成本比较器。严格的 score-aware 成功要求语义干净，且公开分数在声明的容差内一致。冻结的轨迹选择器是一棵无依赖的 CART（Breiman et al., 1984），深度 5、类别权重平衡、随机种子 2026。它在把动作行折叠后、按"每个开发 checkpoint–故障一行"拟合，随后在留出重放与端点物化之前冻结；无效或低置信度的轨迹（最大类别概率 < 0.60）转去 verify。划分清单、反事实行、目标对齐记录与后端仍保留在发布包中；语义干净敏感性与端点族构成仍留在实时归档中。

### B.6 主要重放不确定性（Primary replay uncertainty）

Declared reference 在原始重放核下选出期望效用最高的动作，并用固定顺序打破平局。在移动核的比较中，Oracle 在移动核下选出效用最高的动作。二者都使用评估器对其各自核的知识；Trace-only 则从可见的 checkpoint 特征中选择。

下面所有重放区间都是 95% 中心的"前缀聚类 bootstrap"区间；重抽样单元是前缀而非故障单元格（Efron, 1979；Cameron et al., 2008）。同一个冻结转移核提供目标对齐、重放余量与单次参考各行。Trace-only 相对 Verify 的完成率差在 ID 上为 0.4196（[0.3571, 0.4732]），在结构 OOD 上为 0.4537（[0.3889, 0.5185]）；效用差分别为 0.4620（[0.4537, 0.4704]）与 0.5732（[0.5562, 0.5911]）（表 7）。移动核审计只改变"动作–结果"概率；状态、轨迹、动作、成本、故障面与评分契约全部保持固定。

**效用/遗憾区间。** 在同一前缀聚类平面上，每个条目写作 估计值 [下界, 上界]：Original Reference 的 ID 效用为 0.805 [0.803, 0.808]，OOD 效用 0.779 [0.774, 0.783]，OOD 遗憾 0.000 [0.000, 0.000]；Original Trace-only 为 0.805 [0.803, 0.808]、0.778 [0.773, 0.783]、0.001 [0.000, 0.002]；移动核的 Oracle 为 0.753 [0.750, 0.756]、0.720 [0.714, 0.725]、0.000 [0.000, 0.000]；移动核的 Trace-only 三项分别为 0.735 [0.731, 0.738]、0.691 [0.684, 0.698]、0.029 [0.027, 0.031]。

**表 7：score-aware 重放成功率的 95% 中心前缀聚类区间。** 前缀是重抽样单元；端点向外取整到三位小数。

| Policy | ID Estimate | ID Lower | ID Upper | Structural OOD Estimate | OOD Lower | OOD Upper |
|---|---|---|---|---|---|---|
| Continue | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| Blind retry | 0.268 | 0.232 | 0.304 | 0.250 | 0.213 | 0.287 |
| Always verify | 0.438 | 0.366 | 0.500 | 0.407 | 0.343 | 0.472 |
| Always replace | 0.893 | 0.839 | 0.938 | 0.889 | 0.824 | 0.944 |
| Status-only | 0.670 | 0.589 | 0.741 | 0.611 | 0.546 | 0.676 |
| Declared reference | 0.857 | 0.795 | 0.920 | 0.852 | 0.796 | 0.907 |
| Trace-only | 0.857 | 0.795 | 0.920 | 0.861 | 0.806 | 0.917 |

原始核下 Trace-only 的结构 OOD 遗憾区间 [0.000, 0.002] 跨越了预先声明的 0.001 边界，因此 OOD 标签只是一个点估计层面的状态，不支持向该划分之外迁移。移动核下 Trace-only 的区间 [0.027, 0.031] 则保持在该边界之上。在原始核上，Trace-only 相对 Always replace 的效用在 ID 与 OOD 上都是 +0.0250；完成率对比在 ID 上为 −0.0357（[−0.0893, 0.0179]），在 OOD 上为 −0.0278（[−0.0926, 0.0278]）。这些是在冻结重放面上的协议成本对比，并不估计端点质量。

**单元匹配的统计审计。** Wilson 区间（Wilson, 1927）适用于独立抽样；配对种子的结果保留聚类范围，放行向量的结果使用"放行向量聚类 bootstrap"（Efron, 1979；Cameron et al., 2008）。每一行都保留其生成单元：分配用 seed，联合规律控制用 cell，坐标压力用 draw，模型类证书用 vector。在 near-tie 证书行，估计值在取整前为 2 × 10⁻⁵，原始端点为 1 × 10⁻⁵ 与 4 × 10⁻⁵；显示的 0.000 不一定表示观测到的零。几条关键的不利行是：坐标 near-tie 0.049 [0.040, 0.060]（N = 2000）、联合 discordant FP 0.000 [0.000, 0.001]（N = 4000）、near-tie 认证 0.000 [0.000, 0.001]（n = 256，N = 10000）；完整的行级审计仍留在放行记录中。

### B.7 选择器拟合稳定性（Selector-fit stability）

两百次"严格开发前缀"的 bootstrap 重拟合，使动作选择在 ID 与结构 OOD 上都保持不变：留出效用的范围分别是 [0.805, 0.806] 与 [0.778, 0.778]，两个划分上的遗憾都是 0.000，与冻结拟合的动作一致率为 1.000。

### B.8 固定核重放控制（Fixed-kernel replay controls）

**表 8：用 U_pol 评估的冻结重放策略。** C_emp 为严格完成率，U_pol 为期望重放效用，c 为 112 个 ID 与 108 个 OOD 单元格上的平均干预成本。

| Policy | ID C_emp | ID U_pol | ID c | Struct. OOD C_emp | Struct. OOD U_pol | OOD c |
|---|---|---|---|---|---|---|
| Blind retry | 0.268 | 0.145 | 1.000 | 0.250 | -0.039 | 1.000 |
| Always verify | 0.438 | 0.343 | 1.000 | 0.407 | 0.205 | 1.000 |
| Always replace | 0.893 | 0.780 | 2.000 | 0.889 | 0.753 | 2.000 |
| Status-only | 0.670 | 0.583 | 1.000 | 0.611 | 0.499 | 1.000 |
| Trace-only | 0.857 | 0.805 | 1.500 | 0.861 | 0.778 | 1.500 |

Trace-only 的重放效用最高：在两个划分上都比 Always replace 高 0.025，而平均成本是 1.50 对 2.00；不过 Always replace 的完成率最高（表 8）。传播感知（propagation-aware）控制为

$$U_{pol}(s, a) = E_{\omega \sim K^{\mathrm{rep}, \mathrm{raw}}(\cdot \mid s, a)} \left[ Y^{\mathrm{rep}, \kappa_{pol}}(s, a; \omega) - \lambda C(a) - 0.01\,G(s, a; \omega) \right]. \tag{17}$$

它是一个工作流控制，不改变共享成本的偏好或放行估计目标。重放在 ID、结构 OOD 与合并的严格测试上，前两名间隔的最小值都是 0.010；替换比例的敏感性保留在放行包中。
## 附录 C 相关工作与识别边界（Related Work and Identification Boundaries）

best-arm identification 提供了重复臂的参照（Audibert et al., 2010；Garivier & Kaufmann, 2016；Jamieson et al., 2014；Kaufmann et al., 2016；Truong, 2025）；部分识别工作提供相容集的语言（Manski, 2003；Fan et al., 2017；Yata, 2021；Christensen et al., 2022）；选择性预测与集合值预测提供弃权与替代动作的接口（Fuentes-Vicente et al., 2026；Geifman & El-Yaniv, 2017；Liu et al., 2026）。重放与恢复研究度量标量效用、修复或轨迹有效性（Gonuguntla, 2026；Shah, 2026；Qi et al., 2026）；执行编辑安全工作研究 checkpoint、fork、restore 与 merge 语义（Zheng et al., 2026）；provenance 与动作证书研究校验来源或执行对象（Liao, 2026；She et al., 2026；Wang, 2026a,b；Zhu & Chang, 2026）。OrchLoop 在单个 checkpoint 上增加了一个"契约相对的动作集合关系"，并与放行状态配对。

在线端点（live endpoint）收到任务与候选文档、故障制品、依赖上下文，以及保留的先前制品分数；验证器可见的检查项对选择器可用，但不会额外序列化给端点。故障标签、答案键、未来结果与未执行的反事实结果，从两侧输入中都被排除。重建输入的清单对全部 108 个恢复输入做哈希；缺少提供方请求标识符、完整提示词与来源完备的响应记录，会使 provider linkage 置为 0。

### C.1 top-1 迁移的序列化敏感性（Serialization sensitivity of top-1 transfer）

对固定的动作顺序 σ，令 Pref_σ(k) 为其前 k 个动作，H_σ(s; L) 为最早动作读出，M_s(L) = 1{R^sc_s ∩ L ≠ ∅}。则

$$\left[ \forall\, \emptyset \ne L \subseteq A^{rec} : H_{\sigma}(s; L) = M_s(L) \right] \iff R^{sc}_s = \mathrm{Pref}_{\sigma}(|R^{sc}_s|). \tag{18}$$

因此物化（materialization）是集合值且与顺序无关的，而 top-1 会随序列化方式改变。主要读出保留平局；唯一赢家的敏感性仅作诊断。

对非空的在线最佳集合 L，相对于重放的状态为

$$\nu_R(L) = \begin{cases} A, & L = R, \\ B, & L \cap R \ne \emptyset,\ L \ne R, \\ D, & L \cap R = \emptyset. \end{cases} \tag{19}$$

对非空的单元格总体 D，记 d_D = 1{∃s : v_s = D}，b_D = 1{d_D = 0, ∃s : v_s = B}，并令 P_rec、P_link、O_κ 分别是记录、linkage 与可观测性检查。在所声明的三状态域上，

$$M_D = 1\{ \forall s : v_s \in \{A, B\} \} = 1 - d_D. \tag{20}$$

可容许的接口类及其充分商为

$$\mathcal{A}_{\kappa}(R; D) = \mathbb{V}^{D}_{R} \times \{0, 1\}^3 \times \mathrm{Bij}(A^{rec}, [m]), \tag{21}$$
$$Q_{\kappa}(D) = (M_D,\ d_D,\ b_D,\ P_{rec},\ P_{link},\ O_{\kappa}). \tag{22}$$

化简后的接口丢掉了冗余坐标 M_D = 1 − d_D。两位的卡片摘要是不够的：Partial 卡片与 Provider-gap 卡片可以共享相同的 (min M, min H_σ) = (1, 1)，而契约却分别返回 Hold-Ambiguity 与 Hold-Record-Completeness。证明通过逐个翻转状态或记录坐标来完成；序列化影响 H_σ，但不影响门的任何坐标。如果允许缺失信息状态 NA，则 M_D 必须显式排除 D 和 NA，而必需的 NA 会强制一个 completeness 搁置。

### C.2 trace-only 门的观测不可识别性（Observational non-identifiability of a trace-only gate）

掩码探针替换五个标记键，同时重算公开的派生字段。令 U_T 为变换后的可观测类，C_u 为相应的碰撞类。如果一个类中包含不同的恢复标签，那么任何只用该可观测输入的确定性选择器都无法匹配全部标签。在单例重放标签下，

$$B_{acc} = \frac{1}{N_{obs}} \sum_{u \in U_T} \max_{a \in A^{rec}} n_{u, a}, \tag{23}$$

$$B_U = \frac{1}{N_{obs}} \sum_{u \in U_T} \max_{a \in A^{rec}} \sum_{z \in C_u} Q^{\mathrm{replay}}_{\kappa_{pol}}(z, a), \tag{24}$$

其中 n_{u,a} 统计 C_u 中的标签数，且

$$Q^{\mathrm{replay}}_{\kappa_{pol}}(z, a) = E_{\omega \sim K^{\mathrm{rep}, \mathrm{raw}}(\cdot \mid z, a)} \left[ \Pi_{pol}(z, a; \omega) \right]. \tag{25}$$

五键掩码在某个留出 ID 见证中产生了"同前缀碰撞、但恢复最优标签不同"的情形。字段向量与见证标识符保留在发布制品中；该构造确立了掩码之下的不可识别性，而针对特定模型推断隐藏机制的能力仍未被测量。其单元是单工作者 checkpoint；工作者池的独立性与常驻进程不在测量对象之内。

### C.3 一次性期望排序识别审计（One-shot expected-ranking identification audit）

**为什么一次观测永远不够。** 设富类 P_rich 包含恢复动作上所有独立 Bernoulli 的积规律，其成本调整效用为 q_a(P) = p_a − λC(a)，最佳动作集合为 A⋆(P) = arg max_a q_a(P)。在该类下，任何结果向量 y 都在某条规律下有正概率，而该规律的最佳动作排除任意给定的目标集合 R^sc（把目标动作的成功率设到接近 0、竞争者设到接近 1 即可）。因此，任何错误晋升率为零的门，对每一次单独观测都必须弃权：

$$\sup_{P \in \mathcal{P}_{rich} : A^\star(P) \cap R^{sc} = \emptyset} P\{ g(Y) = 1 \} = 0 \quad \Longrightarrow \quad g \equiv 0. \tag{26}$$

同样的论证可推广到任意固定有限数量的独立分支。要实现受控风险的放行，要么需要重复证据，要么需要对规律类施加结构性限制。

**可观测的隐藏状态混合。** 当多个隐藏 checkpoint 共享同一个可观测签名 o 时，观测结果是各 checkpoint 特定核的混合。混合效用集 U^{obs}_o(y) 收集所有与 y 及所声明混合族相容的期望效用向量；迁移位 TR^{obs}(y) 记录目标动作集合 R 是否与每个此类效用向量的最佳动作集合相交。纤维中一条全支撑的"坏规律"会恢复一次性弃权的边界。

**重复支撑与匹配耦合。** 有了重复的独立结果向量，一个支撑覆盖整个样本空间的坏规律类，依然不留下安全的晋升区域。不过，支撑的几何形状取决于每个向量内部动作之间的耦合。考虑两条每动作边际相同（Bernoulli(θ) 与 Bernoulli(1 − θ)）的规律：一条是共同冲击（shared-shock）规律（动作通过一个共同的均匀抽样 U 一起成功或失败），另一条是积规律（动作相互独立）：

$$P^{ss}_{\theta} = \mathrm{Law}\left( \mathbb{1}\{U \le \theta\},\ \mathbb{1}\{U \le 1 - \theta\} \right), \qquad P^{\times}_{\theta} = \mathrm{Bernoulli}(\theta) \otimes \mathrm{Bernoulli}(1 - \theta). \tag{27}$$

积规律在 {0, 1}² 上是全支撑的，所以它的坏子族不留下安全区域。而 θ < 1/2 时的共同冲击规律无法产生 (1, 0)，于是该结果成为目标 {1} 的一个安全晋升见证：

$$X^{\mathrm{safe}}_{\{1\}}(\{P^{\times}_{\theta}\}) = \emptyset, \qquad X^{\mathrm{safe}}_{\{1\}}(\{P^{ss}_{\theta}\}) = \{10\}. \tag{28}$$

如果耦合没有被声明，安全区域就是所有可容许类的交——因此，无法区分耦合的门，必须在任何类含有坏规律的地方都保守行事。

### C.4 有限分支认证与统计放行（Finite-branch certification and statistical release）

**基于 Hoeffding 的证书。** 给定每个动作 n 个分支，经验成本调整效用 q̂_{a,n} = n⁻¹ ∑_i Y_{a,i} − λC(a) 与 Hoeffding 半径 ε_n(δ) = √(log(2m/δ)/(2n)) 定义一个"单例或弃权"的证书：

$$\hat{R}_{n, \delta} = \left\{ a : \hat{q}_{a, n} - \max_{b \ne a} \hat{q}_{b, n} > 2\varepsilon_n(\delta) \right\}, \qquad \Pr\{ \hat{R}_{n, \delta} \subseteq A^\star \} \ge 1 - \delta. \tag{29}$$

证明用的是联合界；向量内部的依赖是允许的。若唯一目标间隔 ∆ > 0，则当 n > 8 log(2m/δ)/∆² 时认证以至少 1 − δ 的概率成功，且误识别概率指数衰减：

$$\Pr\{ \hat{A}_n \ne \{a^\star\} \} \le 2(m - 1) \exp(-n\Delta^2 / 2). \tag{30}$$

近平局间隔 0.06 在 n = 512 时大体仍未解决，而大间隔证书从 n = 64 时的 40.5% 升到 n = 128 时的 97.9%，且没有错误证书。

**统计放行。** 若置信关系覆盖真实的"规律–记录"对（失败概率 ≤ δ），且解码器正确（失败概率 ≤ η），那么单例放行必然等于真实目标：

$$\Pr\{ \text{STATISTICAL CONTINUE 输出不正确的目标} \} \le \delta + \eta. \tag{31}$$

若再加一项"桥遗漏" α，则为 α + δ + η；已经包含桥遗漏的覆盖界不能重复计数。由同时效用区间 [l_a, u_a] 给出的保守最大化者像为：

$$S(l, u) = \left\{ \emptyset \ne S \subseteq A_0 : \max_{a \in S} l_a \le \min_{a \in S} u_a,\ \max_{b \notin S} l_b < \min_{a \in S} u_a \right\}. \tag{32}$$

**校准边界。** 对"赢家未知但间隔至少为 ∆"的模型类，Le Cam–Pinsker 下界（Le Cam, 1986；Pinsker, 1964）给出在间隔为 2ζ 时用 n 个分支识别最佳动作的 minimax 误差：

$$\inf_{\hat{a}} \sup_{\theta \in \{+, -\}} \Pr_{\theta}\{ \hat{a} \ne a_{\theta}^\star \} \ge \frac{1}{2} \left( 1 - \sqrt{2n\zeta \log \frac{1 + 2\zeta}{1 - 2\zeta}} \right). \tag{33}$$

这也是集合认证的下界，因为正确的单例会诱导出正确的选择器。固定预算下的分辨遵循 best-arm 分析（Audibert et al., 2010；Kaufmann et al., 2016；Jamieson et al., 2014；Lattimore & Szepesvári, 2020）；感知停止时刻的证据则需要时间一致的置信序列（Howard et al., 2021）。

**从匿名执行块构造关系。** 假设有 m 个各含 n 次观测的存储块，每个动作一个块，但动作绑定是隐藏的。令 M(x) 枚举与可见元数据一致的所有"块到动作"双射。对每个块 j，在水平 δ/m 下构造 Clopper–Pearson 区间 [L_j, U_j]（Clopper & Pearson, 1934；Bonferroni, 1936）。置信关系为

$$\hat{H}_{\delta} = \bigcup_{\beta \in M(x)} \{ (P, z_{\beta}) : L_j \le E_P[Y_{\beta(j)}] \le U_j\ \ \forall j \}. \tag{34}$$

覆盖 ≥ 1 − δ 成立，因为只需覆盖真实绑定的 m 个均值，且 |M(x)| 不带来多重性惩罚。若元数据或一份来源回执能以失败概率 α_M、α_R 排除真实绑定，则由联合界，覆盖变为 1 − δ − α_M − α_R。这一构造把"可检查的来源指派契约"与"偏好推断所需的抽样假设"分离开来。

**受控错误下的精确平局。** 整集合认证在精确平局处面临根本限制。若 p₀ 是两个或更多动作精确平局的参数，且附近的参数 p_k → p₀ 会打破平局，则任何一致有效的认证器都满足

$$\sup_{p} \Pr_p\{ \text{放行错误集合} \} \le \delta \quad \Longrightarrow \quad \Pr_{p_0}\{ \text{有限时间内放行 } I_0 \} \le \delta. \tag{35}$$

**证明。** 在每个 p_k 处放行 I₀ 都是错误的，故 Pr_{p_k}(E ∩ {T ≤ N}) ≤ δ。有限时域的 TV 连续性给出 p₀ 处同样的界；令 N → ∞ 即得证。

因此，在无限制的规律类上，受控错误规则无法可靠地用有限结果认证精确的多动作平局。声明的间隔或基于容差的目标会改变这个问题；标准的"唯一最佳臂"形式化则显式施加唯一性（Garivier & Kaufmann, 2016）。

**相容边界。** 只有一个分支向量时，实现出的 overlap 是精确的，但富类允许任何动作成为可能的唯一期望赢家。因此期望迁移位在每个单元格上都有与支撑相容的取值范围 {0, 1}。同时 95% Clopper–Pearson 区间（Clopper & Pearson, 1934；Bonferroni, 1936）作为模型类诊断报告，与实现出来的读出分开。
## 附录 D 受控证据与决策研究（Controlled Evidence and Decision Studies）

### D.1 主要放行与请求比较的生成器（Generators for the main release and request comparisons）

**放行总体。** 表 22 使用独立的门决策 comparison.py：五个等权机制，各 2,000 次独立放行，每次放行四个单元格。动作顺序为 retry、verify、replacement，归一化成本 (1, 1, 2)，λ = 0.05，扣减 c_a = λC(a)。每次放行均匀选择 replay 动作 r，b 是该顺序中排在后面的另一个动作。在顺序 (r, b, 其余) 下，Bernoulli 均值三元组为：eligible 与两个 record-gap 机制取 (0.76, 0.44, 0.44)，tied 机制取 (0.62 + c_r, 0.62 + c_b, 0.44)，discordant 机制取 (0.46, 0.76, 0.44)。四个单元格都用该三元组，每个动作 32 次抽样。在这些选择给定的条件下，结果在抽样、动作、单元格与放行之间相互独立；每条规则看到相同的抽样。单独的八次抽样输出不计入本表。

completeness 只在 provider gap 下为 0，observability 只在 observability gap 下为 0，linkage 恒为 1。因此 h_i = P_{rec,i} · O_{κ,i} 已包含全部会变化的所供检查。eligible 机制的 (u_i, o_i) = (1, 1)，tied 机制为 (0, 1)，其余三个为 (0, 0)，使用 E.2 节的定义。这些是设计权重，不是估计出的任务频率。每个观测集合最大化"经验均值减成本"，数值平局容差为 10⁻¹²。成员资格要求每个单元格的观测集合都含 r；Full gate 要求每个集合恰好等于 {r} 且所供检查全部通过。Top-1 使用固定动作顺序。Robust-95 要求 replay 的下界超过每个竞争者的上界，半径为 √(log(6/0.05)/(2 · 32))。生成器种子为 20260825。

**请求总体与响应。** 表 15 使用 4,000 个状态：按"任务族（rank、path、filter、delegation）× 未消解坐标机制（仅 preference、仅 release、两者、都不）"四类配对，每组 250 个。在每个"族–机制"组内，状态按 k = 0, …, 249 编号。未消解坐标的初值为 {0, 1}，已消解坐标的初值为 {1}。四种机制下的真值 (t_P, t_R) 分别为 (k mod 2, 1)、(1, k mod 2)、(⌊k/2⌋ mod 2, k mod 2)、(1, 1)。总体含 2,248 个 eligible 状态与 1,752 个 ineligible 状态，其中 248 个 eligible 状态的两个坐标都未消解。

五种请求是 Repeat、Collect、JointCertificate、RepeatReplica、CollectReplica，成本依次为 (0.700, 0.800, 1.100, 0.850, 0.650)，覆盖集依次为 {P}、{R}、{P, R}、{P}、{R}。预算为 1.50。32 个子集全部被考虑，受总成本与其覆盖约束。各任务族的 (q_R, q_C) 分别为 (0.90, 0.84)、(0.82, 0.88)、(0.86, 0.84)、(0.78, 0.92)。其余信息性概率为 q_J = q_R q_C + 0.04、q_R′ = max(0.05, q_R − 0.06)、q_C′ = max(0.05, q_C − 0.08)。五个响应指示变量在"族/状态"条件下相互独立；联合请求有自己的指示变量。信息性响应会揭示真正被覆盖的坐标，否则纤维保持不变。精确选择在可行子集上最大化"完整信息性覆盖"。

按种子、状态与请求索引的潜在响应在各策略间共享。精确规则与固定规则使用 64 个种子；校准式选择使用 32 个校准种子与 32 个不相交的评估种子，且在没有真值标签的情况下仅凭响应覆盖做选择。表 15 的评估成本不含校准；其单独的成本分析见 D.7 节。源文件与冻结的响应摘要按表标签列在补充代码索引中。

**可观测契约与效用。** 可观测扰动固定严格的 score-aware 重放状态、动作核、标签、前缀聚类 bootstrap，以及每个前缀八个嵌套的确定性噪声抽样，只改变轨迹。被掩码的五个键是 status timeout、version current、role extractor、schema v1、score matches answer，中性取值为 (0, 1, 1, 1, 1)；派生的 status 与 score 字段被重算。未掩码视图没有跨故障碰撞，而五键视图制造出所声明的冲突类，并提供 O = 1 与 O = 0 的审计对照。公开调度器包包含 90 个任务上下文与 392 个不透明决策状态。码本控制只重映射四个故障签名码，评估全部 24 个"前缀内"双射，并做冻结与变换视图的重拟合（表 9）。

碰撞审计使用完整的变换后选择器输入，并允许跨故障单元格依赖。其最佳公共动作准确率与效用上界见表 10。冻结选择器在 112 个 ID 单元格上的移动核遗憾为 0.019，在 108 个结构 OOD 单元格上为 0.029；其选择在全部 220 个单元格上与主选择器一致。把原始核与迁移核按 p_α = (1 − α)p_original + α p_transfer 插值（α ∈ {0, .25, .50, .75, 1}），得到 ID 上的冻结遗憾 (0.000, 0.001, 0.004, 0.008, 0.019) 与 OOD 上的 (0.001, 0.004, 0.008, 0.015, 0.029)。除 OOD 上 α = 0 时的 0.001 外，条件重拟合遗憾在每个显示的插值点都为零。

**表 9：留出重放上的可观测码本漂移。** Agreement 是与留出重放动作的一致率；固定与重拟合选择器收到同样的变换单元格。

| Split | Original | Fixed | Refit | Fixed regret |
|---|---|---|---|---|
| ID | 1.000 | 0.375 | 1.000 | 0.293 |
| Structural OOD | 0.880 | 0.405 | 0.880 | 0.361 |

**表 10：五键视图下的碰撞类上界与观测一致率。** 率与计数分列报告；B_U 是最佳公共动作的重放效用上界，Floor 是其碰撞遗憾下界。

| Split | Obs. rate | Obs. n | Bacc | Bacc n | BU | Floor |
|---|---|---|---|---|---|---|
| ID | 0.500 | 56 | 0.750 | 84 | 0.804 | 0.002 |
| Structural OOD | 0.380 | 41 | 0.870 | 94 | 0.779 | 0.000 |

对 checkpoint s、动作 a 与重放分支 ω，定义语义结果 Y^sem(s, a; ω)，并令

$$U^{\kappa_{pol}}(s, a) = E_{\omega \sim K^{\mathrm{rep}, \mathrm{raw}}(\cdot \mid s, a)} [ \Pi_{pol}(s, a; \omega) ], \qquad \Pi_{pol} = Y^{\kappa_{pol}} - 0.05 C(a) - 0.01 G(s, a; ω). \tag{36}$$

这里 Y^{κ_pol} = Y^sem · S^score 要求语义有效且分数一致；分数比较使用相对容差 10⁻⁴、绝对容差 0.05。重放读出在 K^{rep,raw} 上求值该谓词，在线读出则在没有传播坐标的保留端点制品上求值。费用 G 使用冻结的级联质量抽样。策略参考为

$$R_{pol}(s) = \arg\max_{a \in A^{full}} U^{\kappa_{pol}}(s, a). \tag{37}$$

单次 score-aware 关系去掉 G 并限制在 A^rec 上；碰撞审计使用仅恢复的投影。全部 462 个语义干净的反事实分支都与分数一致。90 前缀的语义干净运行是一次单独的敏感性分析，其在线效用不含级联质量，因为执行在恢复后即停止。

### D.2 契约级决策规则（Contract-level decision rule）

放行门把六维二值输入（总体不相交性 d_D、含糊性 b_D、记录完整性 P_rec、linkage P_link、可观测性 O_κ、成员资格 M_D）按下述"首个适用分支"映射为一个处置（disposition）：

$$\tilde{G}_{\kappa} = \begin{cases} H_R, & P_{rec} = 0, \\ H_L, & P_{rec} = 1,\ P_{link} = 0, \\ H_O, & P_{rec} = P_{link} = 1,\ O_{\kappa} = 0, \\ R_D, & P_{rec} = P_{link} = O_{\kappa} = 1,\ d_D = 1, \\ H_A, & C_{\kappa} = 1,\ d_D = 0,\ (b_D = 1 \lor M_D = 0), \\ P^{obs}_{\kappa}, & C_{\kappa} = M_D = 1,\ d_D = b_D = 0. \end{cases} \tag{38}$$

只有在"目标可分的含糊性 + 正的间隔 + 预算可用"时才发出 Repeat 请求；它不能绕过记录或可观测性的搁置。

**坐标的必要性。** 每个坐标都是必要的。从全通过状态 (0, 0, 1, 1, 1) = PROMOTE 出发，翻转任一单独坐标都会改变处置（分别变为拒绝、含糊搁置、记录搁置、linkage 搁置或可观测性搁置）。没有任何坐标可以在不合并不同处置的前提下被移除。

只看到"重放最佳集合"与"观测最佳集合"的端点标量无法复现该门：两条标量完全相同、但 P_rec 分别为 0 与 1 的记录，会得到 HOLD 与 PROMOTE 两种不同处置。

### D.3 模型类分支预算审计（Model-class branch-budget audit）

有限分支审计改变重复证据的数量，此时评估器知道唯一的期望赢家与成本调整后的间隔：大间隔类为 0.40，近平局为 0.06，异质（heterogeneous）类为 0.36–0.40。36 个嵌套单元格各自使用预算 n ∈ {1, 2, 4, 8, 16, 32, 64, 128, 256, 512} 与 10,000 次独立放行（种子 20260822）。每个预算都使用式 (5) 中同一个 Hoeffding 规则。n = 32、64、128、256、512 时的充分间隔阈值 4ρ_n(0.05) 分别为 1.094、0.774、0.547、0.387、0.274。

**表 11：δ = 0.05 下的有限分支偏好认证。** Valid 是 360,000 个单元格中给出正确唯一赢家证书的比例；False 为错误证书计数。很小的非零比率可能取整显示为 0.0000；确切计数列在下方。

| Class | n=32 Valid | n=32 False | n=64 Valid | n=64 False | n=128 Valid | n=128 False | n=256 Valid | n=256 False | n=512 Valid | n=512 False |
|---|---|---|---|---|---|---|---|---|---|---|
| Near tie | 0.0000 | 0 | 0.0000 | 0 | 0.0000 | 0 | 0.0000 | 0 | 0.0004 | 0 |
| Heterogeneous | 0.0124 | 0 | 0.3084 | 0 | 0.9353 | 0 | 1.0000 | 0 | 1.0000 | 0 |
| Large margin | 0.0174 | 0 | 0.4054 | 0 | 0.9785 | 0 | 1.0000 | 0 | 1.0000 | 0 |

大间隔类与异质类到 256 个分支时认证率达到 1，而近平局在 512 个分支时仍为 0.0004。近平局的确切有效计数在 n = 32、64、128、256、512 时分别为 0、1、0、7、136（分母 360,000），且每个"类 × 预算"条件的错误证书都为零。在 32 个分支时，set membership、序列化 top-1、Robust-95 与 Contract-A-only 在 12,000 次抽样上的 (overlap, FP_all, Miss_all) 分别为 (0.493, 0.090, 0.045)、(0.481, 0.083, 0.051)、(0.001, 0.000, 0.448)、(0.469, 0.077, 0.057)。

### D.4 确定性门控制与联合规律检验（Deterministic gate control and joint-law checks）

联合规律检验比较在"匹配的动作边际"下、积族与共同冲击族之间的观测相容性（表 12）。

**表 12：匹配动作边际的联合结果规律下的观测相容性。** 每个机制内，两个族使用同样的 N = 4,000 个潜在规律规格；两个族共享 replay 动作、成本、边际成功概率与每动作分支预算。分支结果对两个族分别抽样。所有比率都是这些规格中的比例。OC 表示观测相容性（observed compatibility），FP 与 Miss 分别表示错误晋升与漏掉的 overlap。

| Family | Regime | 1 branch OC | FP | Miss | 32 branches OC | FP | Miss |
|---|---|---|---|---|---|---|---|
| Product | Discordant | 0.372 | 0.372 | 0.000 | 0.002 | 0.002 | 0.000 |
| Product | Near tie | 0.514 | 0.269 | 0.101 | 0.472 | 0.255 | 0.128 |
| Product | Aligned | 0.646 | 0.000 | 0.354 | 0.992 | 0.000 | 0.008 |
| Coupled | Discordant | 0.427 | 0.427 | 0.000 | 0.000 | 0.000 | 0.000 |
| Coupled | Near tie | 0.624 | 0.311 | 0.033 | 0.470 | 0.220 | 0.095 |
| Coupled | Aligned | 0.748 | 0.000 | 0.252 | 0.999 | 0.000 | 0.001 |

"构造即已知"（known-by-construction）的控制使用 36 个单元格、在三个动作上循环的单例重放标签、五种场景，以及每动作 1 与 8 个分支下的 20,000 次 Monte Carlo 抽样（表 13）。Strict 要求对齐、来源完备且无碰撞；τ = 0.95、集合求交与最早序列化是基线。在表 13 中，严格实现在 5 张留出卡片上标签分歧为 0/5、对齐晋升为 1/1；仅按重放晋升则在 5/5 张留出卡片上与之分歧。

**表 13：构造即已知的门控制。** 接受率使用预先声明的真值；显示的 0 表示 0/20,000。

| Scenario | Truth | 1 br Strict | τ | Set | Top-1 | 8 br Strict | τ | Set | Top-1 |
|---|---|---|---|---|---|---|---|---|---|
| Discordant | hold | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| Ambiguous | hold | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| Provider | hold | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.656 | 0.553 |
| Codebook | hold | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.654 | 0.551 |
| Aligned | promote | 0.000 | 0.000 | 0.000 | 0.000 | 0.466 | 0.622 | 0.651 | 0.549 |

仅按重放投影的规则可能接受"来源缺失"或"有碰撞"的卡片，这正是放行门同时保留记录坐标与可观测性坐标的原因。

联合规律检验在积族与共同冲击族下复用 4,000 个固定种子的潜在规律规格，其中共同冲击族含概率 0.80 的共同成分加概率 0.20 的独立成分。每动作参数位于 (0, 1)，因此两个族都是全支撑；重复向量相互独立，而向量内部的动作可以相关。匹配的边际、放行签名、预算与重放身份全部固定。机制分离审计每个条件使用 8,000 个配对单元格：γ_i = (族, 深度分箱) 共享；link 条件使用 a*_{i,link} = g(γ_i)，置换条件使用按折平衡的动作置换。成本调整效用取 λ = 0.05、C = (1, 1, 2)，间隔为 0.16 或 0.03，预算为 1、8、32。留折码本预测器以及集合值、序列化与 Robust-95 读出只使用可见签名，其配对结果列在下文。
### D.5 证据分配（Evidence allocation）

坐标局部审计把四个任务族（rank、path、filter、delegation）与四种需求机制（preference-only、release-only、joint、resolved）交叉，每单元格 250 个状态，共 4,000 个状态、64 个配对种子。信息性响应会用真值替换其目标纤维；非信息性响应则保持不变。同一个潜在响应在各策略间配对使用。

**表 14：坐标定向请求的预算可行性。** TP、FP、Miss 分别以 eligible、ineligible、eligible 为分母；Joint TP 限于两个坐标都未消解的 eligible 状态。Cost 与 Rounds 是全部 4,000 个状态上的均值。

| Rule | Budget | TP | FP | Miss | Joint TP | Cost | Rounds |
|---|---|---|---|---|---|---|---|
| Scalar projection | 0 | 0.667 | 0.285 | 0.333 | 0.000 | 0.000 | 0.000 |
| Typed-greedy | 1 | 0.826 | 0.000 | 0.174 | 0.000 | 0.750 | 0.750 |
| Typed-parallel | 2 | 0.911 | 0.000 | 0.089 | 0.774 | 1.000 | 0.750 |

有两条证据通道可用：结果证据（重做任务以观测新结果）与记录证据（收集来源或可观测性信息）。每条通道都建模为一次配对的 Bernoulli 抽样——信息性响应揭示坐标的真实取值，非信息性响应则使纤维保持不变。**证据更新。** 新证据把相容关系限制到与观测一致的对；可分的响应会把相应的坐标像压缩成单例。

**未消解坐标与请求词表。** 可能未消解的坐标有三个：桥身份（bridge identity）、偏好 overlap、记录资格。它们各自映射到一种请求类型，依次是 VERIFY（桥）、REPEAT（偏好）、COLLECT（资格）。挂起的记录检查（完整性 σ_R、linkage σ_L、可观测性 σ_O，各 ∈ {⊥, 0, 1}）扩充请求集合：完整性或可观测性挂起时追加 COLLECT，linkage 挂起时追加 VERIFY。

**派发逻辑。** 派发器遵循三分支规则：若整集合证书成立，返回 CONTINUE(I†)；若未确认失败且仍有请求可用，返回 REQUEST(Q_all)；否则返回 HOLD。

$$\pi_C(\Gamma, \sigma, U) = \begin{cases} \mathrm{CONTINUE}(I^\star), & e = 1, \\ \mathrm{REQUEST}(Q_{all}), & e = 0,\ F = 0,\ Q_{all} \ne \emptyset, \\ \mathrm{HOLD}, & \text{其他情形}. \end{cases} \tag{39}$$

带预算的版本在请求总成本超过剩余预算 B 时以 HOLD 替代。已确认的失败（F = 1）是终止性的；缺失的检查是挂起状态，而非终止。真实限制只能收缩目标像，因此 Continue 保留原有证书，而没有正目标的类也不可能凭空获得正目标。设初始预算 B₀、最小请求成本 c_min，则最多进行 ⌊B₀ / c_min⌋ 轮。

**坐标局部保证。** 在两个坐标的独立信息性概率 q_{rep,c}、q_{rec,c} 之下，typed-parallel 规则晋升 eligible 案例的概率等于其未消解坐标上概率的乘积：

$$\Pr(\hat{E}_c = 1) = \mathbb{1}\{ \theta_c = (1, 1) \} \cdot q^{u_{rep, c}}_{rep, c} \cdot q^{u_{rec, c}}_{rec, c}, \tag{40}$$

其中 u_{rep,c}、u_{rec,c} ∈ {0, 1} 指示坐标是否未消解。错误晋升恰好为零，因为不合格坐标不可能被真实证据消解为 {1}。

**共享预算与耦合证据。** 当两条证据通道正相关（联合信息性概率 q^rep q^rec + κ，耦合 κ = 0.04）时，typed-parallel 规则仍然实现零错误晋升：

$$\Pr(\hat{E}_c = 1 \mid \theta_c = (1, 1)) = p^{U_{req}}_c, \qquad \Pr(\hat{E}_c = 1 \mid \theta_c \ne (1, 1)) = 0, \tag{41}$$

其中 p^{U_req}_c 是未消解坐标上的联合信息性概率。当预算无法同时覆盖两条请求时，单轮规则必须搁置，因为总有一个纤维仍未消解。只投影偏好、漏掉放行坐标的规则，会有一个正的错误晋升下界。

### D.6 共享预算下的证据获取（Evidence acquisition under a shared budget）

获取比较使用一个目录，内含：每个坐标的本地请求、成本与可靠性不同的替代本地请求，以及一条覆盖两个坐标的联合请求。Local-coordinate 分别请求每个未消解坐标；Joint-coordinate 只要还有任何需求就用联合请求；Exact typed 用声明的请求规律最大化可行覆盖；Calibrated typed 则从单独的响应观测估计覆盖。这四条 typed 规则共享同一个最终晋升条件。在共同预算上限 B = 1.50 下，Exact typed 达到 93.2% 的 eligible 覆盖，而 Local-coordinate 为 90.6%、Joint-coordinate 为 87.2%（表 15）。Exact typed 比 Local-coordinate 用掉更多允许预算；相对 Joint-coordinate，它在降低平均支出的同时提高了覆盖。

**表 15：共享请求预算 B = 1.50 下的证据获取。** 覆盖率与错误晋升分别以 eligible 与 ineligible 状态为分母；平均成本对全部状态取平均。该审计覆盖 4,000 个状态，精确规则与固定规则每状态 64 个配对响应向量；校准式选择每状态用 32 个校准向量与 32 个独立评估向量。信息性更新是真实的，覆盖与错误晋升都是比例，评估成本不含校准获取。

| Rule | Coverage | False promotion | Mean cost |
|---|---|---|---|
| Scalar projection | 0.667 | 0.285 | 0.000 |
| Joint-coordinate | 0.872 | 0.000 | 0.825 |
| Local-coordinate | 0.906 | 0.000 | 0.750 |
| Calibrated typed | 0.924 | 0.000 | 0.856 |
| Exact typed | 0.932 | 0.000 | 0.813 |

校准式选择在独立评估抽样上达到 92.4% 覆盖，而精确选择器在同样抽样上为 93.3%（附录表 16）。在一次单独的模拟中（响应独立、请求规律在每个案例族内共享），含校准的每个评估案例成本为 9.034，高于固定策略的成本（附录表 17）。正如"真实更新模型 + 共享最终门"所预期的，精确与校准选择器、以及本地与联合控制都记录到零错误晋升。漏掉放行需求的 Scalar projection 尽管没发任何请求，却晋升了 28.5% 的 ineligible 状态。

在两个坐标都未消解的 248 个 eligible 案例中，Exact typed 与 Joint-coordinate 都达到 77.0% 覆盖，而 Local-coordinate 为 73.3%。总体比较还包含只有一个坐标未消解的案例——在那里本地请求可以省下联合请求的费用。单独的预算可行性比较见附录表 14。

### D.7 证据覆盖与校准（Evidence coverage and calibration）

本审计使用坐标局部接口：每个二值坐标纤维独立更新，不做跨坐标推断。目录中每条请求 r 有成本 c_r > 0、一个可覆盖坐标集 S_r，以及一个信息性指示变量 Z_r。当至少有一条指向该坐标的信息性请求返回真值时，该坐标被覆盖；未覆盖的纤维保持不变：

$$F^{A, Z}_{c, u} = \begin{cases} \{ \theta_{c, u} \}, & \exists r \in A : u \in S_r,\ Z_r = 1, \\ V_{c, u}, & \text{其他情形}. \end{cases} \tag{42}$$

**定理（带预算的证据覆盖）。** 在真实更新、以及在预算 B 内选择请求集 A 的单轮非自适应规则下，最优真阳性率与假阳性率满足

$$TP^{\star}_c(B) = \max_{A \in \mathcal{F}_B(U_c)} p^{cov}_c(A) \ \ (c \text{ 为 eligible}), \qquad FP_c(B) = 0 \ \ (c \text{ 为 ineligible}), \tag{43}$$

其中 p^cov_c(A) 是"所有未消解坐标都收到信息性响应"的概率。当预算低于最小覆盖成本时，TP = 0。

**证明。** eligible 案例晋升，当且仅当每个未消解坐标都被信息性响应覆盖。真实更新不可能让不合格坐标显得为正。在可行覆盖上取最大值即得最优；对覆盖做随机化只会得到凸组合，无法改进。对两个坐标，最优值由精确枚举给出。

覆盖事件是"对坐标取析取、再对请求取合取"的结构：在指示变量独立时，容斥原理给出精确的覆盖概率。对两个未消解坐标，本地请求的联合成功率为 p_L = Pr(Z₁ = Z₂ = 1)，联合请求的成功率为 p_J = Pr(Z₁₂ = 1)。只比较可行覆盖：p_L > p_J 时选本地对，p_J > p_L 时选联合证书，两者都不合适则搁置。若在指示变量独立时三种请求都装得下，则覆盖为

$$p^{cov}_c = 1 - (1 - q_{12})(1 - q_1 q_2) = q_{12} + q_1 q_2 - q_1 q_2 q_{12} \ge q_1 q_2 q_{12}. \tag{44}$$

该审计枚举五种声明请求类型的全部 32 个子集；在 B = 1.50 时，期望覆盖与经验覆盖分别为 0.933 与 0.932。

**精确选择与校准选择。** 在同样的坐标局部转移下，令 Π_B(c) 索引一族在校准之前固定的可行请求集 A_π ∈ F_B(U_c)，记 p_c(π) = p^cov_c(A_π)。若 Π_B(c) = ∅，则不发请求直接返回 Hold；否则精确选择使用声明的请求规律取 π_c⋆ ∈ arg max_{π∈Π_B(c)} p_c(π)。枚举全部可行集即恢复式 (43)。

对非空的族，校准选择使用 m ≥ 1 个来自"给定 c 且 θ_c = (1, 1)"条件请求规律的独立响应向量 Z_{c,1}, …, Z_{c,m}。每个向量评估每个候选集合，其中的响应可以相关。这类数据可来自独立标注的 eligible 校准总体。无标注校准则要求"信息性响应规律在给定观测上下文时与资格独立"，否则它估计的是混合分布，下面的界未必成立。我们的有限模拟按构造满足该独立性——响应概率仅由观测到的族决定。记 S_Z(A) = ⋃_{r∈A: Z_r=1} S_r 为信息性响应揭示的坐标，则覆盖事件为 C_c(A, Z) = 1{U_c ⊆ S_Z(A)}。经验覆盖与所选请求索引为

$$\hat{p}^{m}_c(\pi) = \frac{1}{m} \sum_{i=1}^{m} C_c(A_{\pi}, Z_{c, i}), \qquad \hat{\pi} \in \arg\max_{\pi \in \Pi_B(c)} \hat{p}^{m}_c(\pi). \tag{45}$$

选择器发出 A_{π̂}，平局按固定规则打破。在来自同一条件规律的新响应上，其覆盖损失满足（0 < δ < 1）：

$$\Pr_{cal}\left( p_c(\pi^{\star}_c) - p_c(\hat{\pi}_c) \le \sqrt{\frac{2 \log(2|\Pi_B(c)| / \delta)}{m}} \right) \ge 1 - \delta. \tag{46}$$

模拟的初始纤维为 {1} 或 {0, 1}，因此从条件目标中排除已知阴性状态，不会改变任何已报告的初始请求选择。该审计使用 32 个校准种子与 32 个不相交的评估种子；最大的候选族含七个请求集合。

**表 16：证据选择的有限样本校准。** 界使用 δ = 0.05 与最大的非空候选族；TP 与 FP 分别以 eligible、ineligible 为分母。

| Rule | m | \|Π_B\| | Bound | TP | Oracle TP | Regret | FP |
|---|---|---|---|---|---|---|---|
| Calibrated coverage | 32 | 7 | 0.593 | 0.924 | 0.933 | 0.009 | 0.000 |

单独案例的迁移审计使用 1,000 个校准案例与 3,000 个评估案例，其中 248 个校准案例无需请求，752 个提供五个响应指示变量。估计器能看到族与响应，但没有资格标签。评估集含 1,675 个 eligible 与 1,325 个 ineligible 案例，每个配 32 个新响应向量。固定本地与联合策略在请求成本 0.750 与 0.824 下分别取得 0.908 与 0.873 的 eligible TP；声明规律的 oracle 在成本 0.812 下达到 0.935。当每案例 8 次校准抽样时，按族估计器对每个"请求 × 族"用 1,504 个观测，并在每个评估案例上都与 oracle 选出相同的子集。汇总（pooled）估计器在请求成本 0.974 下达到同样的 TP。8 抽样按族的总成本 9.034 高于两种固定策略的成本，因此该迁移结果并未确立成本优势。"族恒定的独立响应规律"是本模拟的假设；划分与响应记录允许直接重算。

**表 17：校准向独立合成案例的迁移。** TP 的分母是 1,675 个 eligible 案例；Request 是全部 3,000 个评估案例上所选请求成本的均值。Total 加上"完整校准成本 ÷ 3,000"，每个响应向量成本 4.100；部署上限为 1.500，离线校准另有专项经费。

| Estimator | 1 draw TP | Request | Total | 8 draws TP | Request | Total | 32 draws TP | Request | Total |
|---|---|---|---|---|---|---|---|---|---|
| Pooled | 0.930 | 0.912 | 1.940 | 0.935 | 0.974 | 9.196 | 0.935 | 0.812 | 33.699 |
| By family | 0.932 | 0.902 | 1.930 | 0.935 | 0.812 | 9.034 | 0.935 | 0.812 | 33.699 |

### D.8 核路径与机制控制（Kernel-path and mechanism controls）

冻结选择器在 U_pol 下训练，并在一条独立指定的移动重放规律下评估，动作契约与成本目标固定（表 18）。它在全部 220 个单元格上与主选择器一致；移动核遗憾在 112 个 ID 单元格上为 0.019、在 108 个结构 OOD 单元格上为 0.029。上文的碰撞分解把"最佳公共动作上界"与"不可约下界"分开。去掉答案、证据内容与分数派生的轨迹字段后，ID 一致率为 1.000、OOD 一致率为 0.859，遗憾分别为 0.000 与 0.001（表 19）。

**表 18：移动重放规律下对冻结选择器的评估。** N 为 checkpoint 单元格计数；Trace regret = 移动核 oracle 效用 − Trace-only 效用。

| Split | N | Trace U_pol | Oracle U_pol | Trace regret |
|---|---|---|---|---|
| ID | 112 | 0.735 | 0.753 | 0.019 |
| Structural OOD | 108 | 0.691 | 0.720 | 0.029 |

**表 19：结果盲的重放控制。** 答案、证据内容与分数派生字段在重拟合前被移除；参考选择器与盲选择器使用同样的标签与留出单元格。

| Split | Agreement | Same | Regret |
|---|---|---|---|
| ID | 1.000 | 1.000 | 0.000 |
| Structural OOD | 0.859 | 1.000 | 0.001 |

### D.9 匹配签名的机制分离（Matched-signature mechanism separation）

机制审计保留公开签名与逐动作的重放边际，同时保留或置换它们与潜在赢家的关联（表 20）。每个条件含 8,000 个配对单元格。Codebook acc. 是"可见签名下的赢家准确率"；One-shot FP 是单分支的集合错误晋升率；Robust FP 与 miss 使用 32 分支的 Robust-95 读出。分母是每行 8,000 个配对单元格。可见关联可以完全可预测，而单次偏好迁移仍会出现错误晋升；32 分支的稳健读出在两种条件下都是零错误晋升，且各漏掉约三分之一的正例。

**表 20：匹配签名的机制分离。**

| Condition | Codebook acc. | One-shot FP | Robust FP | Robust miss |
|---|---|---|---|---|
| Link permuted | 0.333 | 0.297 | 0.000 | 0.333 |
| Link preserved | 1.000 | 0.411 | 0.000 | 0.332 |
## 附录 E 补充决策与关系审计（Supplementary Decision and Relation Audits）

### E.1 源键机制见证（Source-key mechanism witness）

源键装置固定公开签名与放行状态，用一个键分离两个 eligible 的单例动作集合像（表 21）。在收到键响应之前，当前未消解集合同时包含桥坐标与偏好坐标，因此 typed 派发器在现有请求词表下返回 VERIFY+REPEAT。单独一条键响应就足以压缩动作集合像；但响应前的派发器报告的是全部未消解的证据操作，它并不是一个最小覆盖优化器。

**表 21：一个可分的源坐标改变单例决策。** 无键行报告响应前的完整请求集合。

| Key view | Action-set image | Next evidence | Disposition |
|---|---|---|---|
| Key absent | {({RETRY}, 1), ({VERIFY}, 1)} | VERIFY+REPEAT | HOLD |
| Key ℓr | {({RETRY}, 1)} | None | PREFERENCE-CERT |
| Key ℓv | {({VERIFY}, 1)} | None | PREFERENCE-CERT |

### E.2 配对放行对比（Paired release contrasts）

所有放行规则在每个机制上使用同样的 2,000 个独立结果向量与同样的所供记录。在本来源抽象中 linkage 恒为 1。令 h_i = P_{rec,i} · O_{κ,i}，r_s 为 replay 动作。overlap 估计目标为

$$o_i = h_i \prod_{s \in D_i} \mathbb{1}\{ r_s \in A^\star(P_s) \}, \tag{47}$$

唯一赢家估计目标为

$$u_i = h_i \prod_{s \in D_i} \mathbb{1}\{ A^\star(P_s) = \{r_s\} \}. \tag{48}$$

因此 eligible 机制的 (u_i, o_i) = (1, 1)，tied 机制为 (0, 1)，discordant、provider-gap 与 observability-gap 机制为 (0, 0)。配对差值使用相同的抽样，并对 discordant 放行计数给出等尾 Clopper–Pearson 区间（Clopper & Pearson, 1934）。

### E.3 同一结果抽样下的放行目标（Release targets on the same outcome draws）

我们在两种需求下评估同一批观测到的放行决策。overlap 需求接受"replay 动作属于每个单元格的期望最大化者"；更严的 unique-winner 需求则排除平局。两者都要求所供记录检查通过。生成器为这些评估器标签提供期望效用，其名为 near tie 的机制中 replay 动作与某个竞争者的期望效用恰好相等。

Set membership 接受非空的观测交集，序列化 top-1 使用固定动作顺序，Full gate 要求每个观测最佳集合都等于 replay 参考。前两条规则的 status-aware 变体使用与 Full gate 相同的记录检查。这些规则用观测结果对照两种偏好需求；候选证书则单独由式 (12) 定义。

对 overlap 目标，Status-aware set 接纳的正例比 Full gate 多，且两种规则都没有观察到错误（表 22）。要求唯一赢家会把"平局接纳"从正确变为错误。于是 Full gate 相对 Status-aware set 把近平局错误降低 3.90 个百分点，代价是在 eligible 晋升上损失 0.65 个百分点。逐点配对区间不含零；分机制的比率与对比见附录表 23。

对 provider 与 observability 缺口，所有 status-aware 规则中的记录检查都解释了零错误。去掉它们就得到 A-only，其缺口错误率超过 95%。在该预算下，Status-aware Robust-95 不犯错误，但也一个 eligible 放行都不接纳。

**表 22：同一批 10,000 次放行的事后再分析（每动作 32 个分支）：eligible、tied、discordant、provider-gap、observability-gap 五种机制各 2,000 次。** Overlap 与 unique-winner 标签分别有 4,000 和 2,000 个正例，并包含同样的所供状态检查。Correct 与 Error 统计被接纳的正例与负例放行；Miss 统计被扣留的正例。

| Rule | Overlap Correct | Error | Miss | Unique winner Correct | Error | Miss |
|---|---|---|---|---|---|---|
| Replay-only | 4000 | 6000 | 0 | 2000 | 8000 | 0 |
| Set membership | 2100 | 3847 | 1900 | 1924 | 4023 | 76 |
| Serialized top-1 | 2059 | 3830 | 1941 | 1919 | 3970 | 81 |
| Status-aware set | 2100 | 0 | 1900 | 1924 | 176 | 76 |
| Status-aware top-1 | 2059 | 0 | 1941 | 1919 | 140 | 81 |
| Status-aware Robust-95 | 0 | 0 | 4000 | 0 | 0 | 2000 |
| A-only | 2009 | 3820 | 1991 | 1911 | 3918 | 89 |
| Full gate | 2009 | 0 | 1991 | 1911 | 98 | 89 |

**表 23：unique-winner 放行的工作特性（每动作 32 个分支、每机制 2,000 次独立放行）。** 比率与配对差值均为比例。T_elig 为 eligible 晋升；E_tie、E_prov、E_obs 分别是 tied、provider-gap、observability-gap 机制的错误率。ΔT 与 ΔE 是 Full gate 减去该行的 eligible 晋升与 tied 机制错误。逐点精确 95% 区间端点向外取整。

| Rule | T_elig | E_tie | E_prov | E_obs | ΔT Est | ΔT Lower | ΔT Upper | ΔE Est | ΔE Lower | ΔE Upper |
|---|---|---|---|---|---|---|---|---|---|---|
| Replay-only | 1.000 | 1.000 | 1.000 | 1.000 | -0.045 | -0.055 | -0.035 | -0.951 | -0.961 | -0.940 |
| Set membership | 0.962 | 0.088 | 0.959 | 0.965 | -0.007 | -0.012 | -0.003 | -0.039 | -0.049 | -0.030 |
| Serialized top-1 | 0.960 | 0.070 | 0.953 | 0.962 | -0.004 | -0.008 | -0.001 | -0.021 | -0.029 | -0.015 |
| Status-aware set | 0.962 | 0.088 | 0.000 | 0.000 | -0.007 | -0.012 | -0.003 | -0.039 | -0.049 | -0.030 |
| Status-aware top-1 | 0.960 | 0.070 | 0.000 | 0.000 | -0.004 | -0.008 | -0.001 | -0.021 | -0.029 | -0.015 |
| Status-aware Robust-95 | 0.000 | 0.000 | 0.000 | 0.000 | 0.956 | 0.945 | 0.965 | 0.049 | 0.039 | 0.060 |
| A-only | 0.956 | 0.049 | 0.952 | 0.959 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| Full gate | 0.956 | 0.049 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |

### E.4 重复稳定性与结果构成（Replicate stability and outcome composition）

配对本地重复审计含 144 个匹配的动作分支与 48 个 checkpoint 单元格。重复间 strict success 一致 134/144（0.931），semantic success 一致 134/144（0.931），schema 一致 140/144（0.972）。严格列联表为：49 个共同失败、6 个仅 replicate 0 失败、4 个仅 replicate 1 失败、85 个共同成功。跨单元格看，汇总关系为 direct 2/48（0.042）、overlap 22/48（0.458）、discordant 24/48（0.500）；discordant 单元格中有 5 个是部分 strict 成功（表 25）。

**表 24：144 个匹配分支上配对本地重复的 strict success 列联表。**

| | Replicate 1 fail | Replicate 1 success | Total |
|---|---|---|---|
| Replicate 0 fail | 49 | 4 | 53 |
| Replicate 0 success | 6 | 85 | 91 |
| Total | 55 | 89 | 144 |

**表 25：单次端点关系与严格动作质量交叉。** 计数使用每单元格的全部三个动作。

| Relation | Cells | Fraction | All success | Partial | All fail |
|---|---|---|---|---|---|
| Direct | 1 | 0.021 | 0 | 1 | 0 |
| Overlap | 23 | 0.479 | 15 | 0 | 8 |
| Discordant | 24 | 0.500 | 13 | 4 | 7 |
## 附录 F 执行归档与记录重建（Execution Archives and Record Reconstruction）

### F.1 制品有效性与动作一致率（Artifact validity and action agreement）

每个模型的动作分支覆盖每个工作流前缀下的四种故障场景。我们评估语义正确性与公开分数一致性，再把成本调整后的动作集合与 replay 参考比较（第 3 节）。Retry、verify 与 replacement 的归一化成本依次为 1、1、2，λ = 0.05。Replay 参考在仿真中单独评估，包括固定策略比较与移动的重放规律（附录 B.8、D.8）。

**表 26：每个来源 48 个"checkpoint–故障"单元格上的保留执行。** 每个来源为每个动作提供两次执行（288 个分支）：b = 1 用第一次执行，b = 2 汇总两次。Strict144 是 144 个 b = 1 分支中满足严格谓词的比例。D、O、X 分别统计"单例集合相等"、"其他非空交集"、"集合不相交"的单元格数。

| Source | Strict144 (b=1) | D | O | X | Mean \|L̂obs\| (b=1) | D (b=2) | O | X | Mean \|L̂obs\| (b=2) |
|---|---|---|---|---|---|---|---|---|---|
| Luna | 1.000 | 0 | 24 | 24 | 2.000 | 0 | 24 | 24 | 2.000 |
| Terra | 0.958 | 1 | 22 | 25 | 1.896 | 1 | 22 | 25 | 1.896 |
| Sol | 1.000 | 0 | 24 | 24 | 2.000 | 0 | 24 | 24 | 2.000 |
| Qwen3-8B | 0.632 | 1 | 23 | 24 | 1.917 | 2 | 22 | 24 | 1.875 |

Luna 与 Sol 每个动作都成功，可它们的成本调整集合在一半单元格里与 replay 参考不相交（表 26）。相同的成功偏向更便宜的 retry 与 verify 动作；只要 replay 选了 replacement，就会出现不一致。汇总两次执行不改变任何 GPT-5.6 单元格的最佳集合。记录资格遵循附录 B.2 中按来源规定的条件。对 Qwen3-8B，匹配集合既含"全部失败"也含"全部成功"的单元格（附录表 24）：当所有动作都失败时，成本调整偏向 retry 与 verify，因此稳定的观测集合仍需先做结果质量检查，才能支撑恢复的主张。

版本锁定的提供方池使用一个 DeepSeek API 端点（DeepSeek, 2026）、12 个前缀（六个 filter、三个 rank、三个 path），协议为 live-recovery-calibration/2，模型 deepseek-chat、temperature 0、240 token 上限。九个分数一致的前缀进入严格审计（六个 filter、三个 rank）。四种故障机制与三个恢复动作给出 36 个单元格与 108 个"每动作一分支"的行。每个单元格保留确定性的 continue；retry、verify 与 replace 使用全新的提示词分支。提供方制品保留归一化输出与 token 字段，但缺少请求标识符、完整提示词与来源完备的响应记录，因此 P_link = P_fields^{(1)} = 0（表 27）。

对 48 个来源完备单元格的终局放行审计给出：replay-only 放行 48/48，set membership 24/48，序列化 top-1 14/48，抹去记录的门一律 HOLD 48/48；精确键控门的决策为放行 2、HOLD 22、拒绝 24，一致率 1.000（表 28）。额外授权率（extra authorization）对精确键控门为 0，对 replay-only 为 0.958。

**表 27：12 个前缀上"分数已抹除"的本地模型物化。** Branches/action 是动作列的分母（每故障 24 个，共 96 个）；Schema 使用全部动作行。

| Fault | Branches/action | Retry 严格恢复 | Verify | Replace | Schema 结构 |
|---|---|---|---|---|---|
| Transient tool failure | 24 | 0.667 | 0.667 | 0.667 | 0.986 |
| Semantic error | 24 | 0.583 | 0.583 | 0.583 | 0.944 |
| Stale message | 24 | 0.583 | 0.583 | 0.583 | 0.931 |
| Delegation mismatch | 24 | 0.708 | 0.583 | 0.708 | 0.944 |
| All branches | 96 | 0.635 | 0.604 | 0.635 | 0.951 |

**表 28：48 个来源完备单元格上的终局放行决策。** Agreement 以精确键控的"观测相容性门"为参照。

| Readout | Release | Hold | Reject | Agreement | Extra auth. |
|---|---|---|---|---|---|
| Replay-only | 48 | 0 | 0 | 0.042 | 0.958 |
| Set membership | 24 | 0 | 24 | 0.542 | 0.458 |
| Serialized top-1 | 14 | 0 | 34 | 0.542 | 0.250 |
| Record-erased gate | 0 | 48 | 0 | 0.458 | 0.000 |
| Exact keyed gate | 2 | 22 | 24 | 1.000 | 0.000 |

### F.2 补充物化控制（Supplementary materialization controls）

在语义干净条件下的 16 个留出、非注入错误单元格中，blind retry 成功 0/16，always replace 3/16（0.188），always verify 16/16（1.000），带 verify 回退的 trace-only 16/16（1.000）（表 29）。Clopper–Pearson 95% 区间（Clopper & Pearson, 1934）为：blind retry (0.000, 0.206)，always replace (0.040, 0.456)；两个完美行的下端点为 0.794、上端点为 1.000。使用评估器键的 verify 行是特权行。

**表 29：语义干净条件下的留出非注入错误回退。** 计数与比率每行使用 16 个单元格；区间端点向外取整。

| Action | Cells | Count | Rate | Lower | Upper |
|---|---|---|---|---|---|
| Blind retry | 16 | 0 | 0.000 | 0.000 | 0.206 |
| Always replace | 16 | 3 | 0.188 | 0.040 | 0.456 |
| Always verify | 16 | 16 | 1.000 | 0.794 | 1.000 |
| Trace-only with verify fallback | 16 | 16 | 1.000 | 0.794 | 1.000 |

"分数已抹除"的 Qwen3-8B 归档使用 bfloat16 权重、36 层、隐藏维 4096、32 个注意力头、8 个 key–value 头、最大上下文 40,960、temperature 0.7、采样、128 token 上限。种子产生 12 × 4 × 3 × 2 = 288 个分支。按 task id、fault、action、replicate 做键控连接，可把运行时元数据与内嵌配置分开，并支持关系表的直接再生。本地归档有完整的键控回执，故 P_rec^loc = P_link^loc = 1；14 个 schema 无效的补全仍属解码器结果。完整未掩码轨迹的 O_κ^loc = 1，而五键扰动提供 O_κ = 0 的对照。

因此单次端点集合通常是平局，且每个单元格都与置信区间相容（表 30）。没有单元格有稳健的期望赢家，且在该样本量下，与支撑相容的汇总期望迁移率横跨 [0, 1]。

**表 30：严格在线单元格上的单次部分识别审计。** 除另有说明外，计数与比率使用 36 个单元格。

| Quantity | Cells | Count | Rate |
|---|---|---|---|
| Observed live set is singleton | 36 | 5 | 0.139 |
| Observed live set is tied | 36 | 31 | 0.861 |
| All actions confidence-compatible | 36 | 36 | 1.000 |
| Cell has a robust expected winner | 36 | 0 | 0.000 |
| Expected-transfer rate lower endpoint | 1 | 0 | 0.000 |
| Expected-transfer rate upper endpoint | 1 | 1 | 1.000 |

### F.3 归档完备的本地放行门（Archive-complete local release gate）

归档完备门在每个动作保留一到两个分支之后，施加同一组放行坐标。只把 P_rec^loc 或 O_κ^loc 之一置零，就会把每个单元格送到相应的搁置。在 16 个"初始记录不满足来源完备 schema"的留出单元格上，派发器请求校验；全部 16 个生成的制品仍不满足 schema，产生 16 个终局 HOLD、零个不安全晋升。仅看分支的完成率：verify 1.000、retry 0.000、replace 0.188，平均成本依次为 1.000、1.000、2.000。

### F.4 顺序证据请求闭包（Sequential evidence-request closure）

闭包审计从不完整的记录开始，在读取响应之前先请求校验。全部 16 个生成的制品仍不满足 schema，因此门返回 16 个终局 HOLD。源键装置起始于"桥坐标与偏好坐标都未消解"的状态，派发器在现有词表下请求 VERIFY+REPEAT；可分的键给出单例的动作集合像并继续，非信息性响应则停留在 HOLD-AMBIGUITY。

### F.5 有键桥的敏感性（Keyed-bridge sensitivity）

在每个前缀内，共享的与逐动作独立的故障置换会抹掉故障键，同时保留每个动作各自的、由四个故障索引结果构成的多重集。在 10,000 次确定性置换（种子 20260903）下，与精确键控门的决策一致率的经验区间为：共享族 (0.854, 0.979)，逐动作独立置换 (0.813, 0.938)；错误晋升区间分别为 (0.000, 0.063) 与 (0.000, 0.104)。这些桥区间是在固定归档上取的经验分位数，不是对新生成端点结果的不确定性。
### F.6 经验联合像审计（Empirical joint-image audit）

对一个含四个故障坐标的前缀，指派 β = (β_a)_{a∈A^rec} 是一个逐动作的置换；两个保留的重复使用同一个指派。键族只含恒等映射，共享族含一个公共置换，独立族含全部逐动作元组。对保留的 n 个分支，

$$\hat{y}^{\beta, n}_{c, a} = n^{-1} \sum_{r=1}^{n} s^{\beta}_{c, a, r} - \lambda C(a), \qquad \hat{L}^{\beta, n}_{c} = \arg\max_{a \in A^{rec}} \hat{y}^{\beta, n}_{c, a}. \tag{49}$$

给定 replay 集合 R_c，在二值投影之前保留动作集合像：

$$\hat{\Gamma}^{J, n}_{c, I} = \{ (R_c \cap \hat{L}^{\beta, n}_{c},\ 1) : \beta \in J \}. \tag{50}$$

字面的回执坐标对每个保留分支都为 1，它不断言 provider linkage，也不断言掩码探针的可观测性。精确键控像为单例；对照族包含恒等映射，因此键控的正对留在稳健并集中，而额外的指派可能移除单例状态。施加同一个门就得到上文的桥表。两次重复的审计在 144 对中有 134 对 strict 与 semantic 一致、140 对 schema 一致。每动作汇总一次执行得到 direct、overlap、discordant 关系分别为 1/48、23/48、24/48；汇总两次则为 2/48、22/48、24/48。在同一冻结来源池上做语义干净敏感性，得到 22/48 个物化单元格（0.458），41 个在线平局；按族看，filter、rank、path 的物化率在 24、12、12 个单元格上分别为 0.458、0.417、0.500。该敏感性在提供方提示词中保留先前制品分数，只改变评估器的结果谓词。

### F.7 跨保留执行源的一致率（Agreement across retained execution sources）

每个来源贡献 48 个"前缀–故障"单元格，三种恢复指令下各保留两次执行（表 31）。比较保留全部最大化者，包括平局。Qwen3-8B 在"全部失败"与"全部成功"的单元格里都有匹配的多动作集合，而 GPT 来源几乎全部是"全部成功"。

Qwen3-8B 使用分数已抹除的提示词，且与 GPT-5.6 来源用的是不同的 12 前缀面板——后者的提示词保留先前制品分数。共同前缀交集含九个任务。下面的区间是来源内部的描述性 95% 百分位区间。每次 bootstrap 重抽样以放回方式抽取 12 个工作流前缀，并保留被抽中前缀内的全部四种故障条件与全部分支；分析使用 10,000 次重抽样、种子 742031。"Cost-adjusted strict"使用"strict success 减 0.05C(a)"（C = (1, 1, 2)）的完整最大化者集合；"Raw strict"使用未调整的 strict success 最大化者集合。Selected success 是另一次执行上"均匀平局的期望 strict success"，在两个方向上取平均。

**表 31：每来源 48 个单元格、288 个分支的保留来源诊断。** All-failed 与 All-passed 统计"六个分支全部失败/全部通过"的等集合单元格。Lower 与 Upper 是描述性 95% bootstrap 区间；重抽样保持 12 个前缀聚类。

| Source | Rule | All-failed | All-passed | Agreement Est | Lower | Upper | Branch success Est | Lower | Upper | Selected success Est | Lower | Upper |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Qwen3-8B | Adjusted | 15 | 26 | 0.875 | 0.750 | 0.979 | 0.625 | 0.368 | 0.858 | 0.620 | 0.365 | 0.870 |
| Terra | Adjusted | 0 | 42 | 0.896 | 0.771 | 1.000 | 0.979 | 0.955 | 1.000 | 0.974 | 0.943 | 1.000 |
| Luna | Adjusted | 0 | 48 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| Sol | Adjusted | 0 | 48 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| Qwen3-8B | Raw | 15 | 26 | 0.875 | 0.771 | 0.979 | 0.625 | 0.378 | 0.865 | 0.625 | 0.377 | 0.875 |
| Terra | Raw | 0 | 42 | 0.875 | 0.729 | 1.000 | 0.979 | 0.955 | 1.000 | 0.979 | 0.955 | 1.000 |
| Luna | Raw | 0 | 48 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| Sol | Raw | 0 | 48 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |

### F.8 保留 checkpoint 绑定的检索（Retrieval of retained checkpoint bindings）

保留的 Qwen3-8B、Luna、Terra、Sol 归档各在 12 个前缀内贡献 48 个单元格，每动作两次执行。选择器看到每个动作四组数据（每组两个 strict 结果与一个成本调整均值）外加 replay 参考；模型、checkpoint、来源、提示词、故障标签与规范绑定留在评估器一侧。每个单元格起始有 3³ = 64 种逐动作指派。一次查询取回某个动作的存储分组并缩小候选类。Fixed order、score range、target-directed minimax 与 EC2 使用同样的掩码视图，在"单例 overlap 像"或"预算耗尽"时停止（表 32）。EC2 在 64 个绑定上使用均匀先验，并在具有不同 overlap 目标的假设之间连边；成本只计记录查询次数。

**表 32：每模型 12 个前缀内 48 个单元格上的 checkpoint 绑定检索。** Resolved 统计单例 overlap 像（含空集）；Positive 统计两次查询后被解析出的非空目标。

| Policy | Luna Resolved q=1 | q=2 | Luna Positive q=2 | Terra Resolved q=1 | q=2 | Terra Positive q=2 | Sol Resolved q=1 | q=2 | Sol Positive q=2 |
|---|---|---|---|---|---|---|---|---|---|
| Fixed order | 48 | 48 | 24 | 45 | 48 | 23 | 48 | 48 | 24 |
| Score range | 48 | 48 | 24 | 45 | 48 | 23 | 48 | 48 | 24 |
| EC2 | 48 | 48 | 24 | 47 | 48 | 23 | 48 | 48 | 24 |
| Target-directed | 48 | 48 | 24 | 47 | 48 | 23 | 48 | 48 | 24 |

Luna 与 Sol 的分数在各候选分组间是常数，因此指派无法改变它们的目标。在 Qwen3-8B 归档中，fixed order 在预算 1 和 2 下分别解析 40 和 44 个单元格，EC2 解析 44 和 47 个；预算 2 下的正目标计数分别为 21 和 23（表 33）。到预算 3 时，所有策略都解析全部 48 个单元格。单独的整集合读出不会替代 R_c ∩ L̂_c。

**表 33：Qwen3-8B 归档上的补充检索比较（12 个前缀内 48 个单元格）。** Resolved 统计单例 overlap 像（含空集）；Positive 统计两次查询后被解析出的非空目标。

| Policy | Resolved q=1 | Resolved q=2 | Positive q=2 |
|---|---|---|---|
| Fixed order | 40 | 44 | 21 |
| Score range | 41 | 43 | 20 |
| EC2 | 44 | 47 | 23 |
| Target-directed | 42 | 44 | 21 |

**候选类遗漏。** 一个共享槽位的压力类只保留 64 种指派中的 4 种，且在 192 个单元格中的 14 个里含规范绑定。做一次真实查询后，三个选择器都在同样 3 处错误停止，报告两个非空目标与一个空目标。在第二个控制中，十二个类各遗漏一个"动作–槽位"取值，把每个规范绑定排除三次。预算 3 时，EC2 在 2,304 次相关的"单元格 × 类"评估中产生 1 个错误空目标与 50 个空像；fixed order 与 minimax 分别不产生错误目标、并产生 50 与 47 个空像。空像触发 Hold。这些是候选类的后果，而不是"某检索策略识别出了未知结果规律"的证据。

### F.9 联合观测目标与本地放行资格（Joint observed targets and local release eligibility）

**表 34：全部 48 个 Qwen3-8B 单元格上的检索。** Image 计数识别出的完整 (I^obs, D_κ) 取值；Decision 计数识别出的 Continue 或 ineligible 处置。未消解的 Hold 不算被识别的处置。表头 1、2 是逐单元格查询预算；Queries 列是预算 2 下的查询总次数。初始时有 32 个像与 34 个处置被识别。

| Query rule | Stop target | Image q=1 | Image q=2 | Decision q=1 | Decision q=2 | Queries q=2 |
|---|---|---|---|---|---|---|
| Fixed order | Image | 36 | 44 | 39 | 46 | 28 |
| Minimax, joint | Image | 41 | 44 | 43 | 46 | 23 |
| EC2, eligibility first | Image | 40 | 45 | 44 | 47 | 24 |
| EC2, joint | Image | 41 | 45 | 44 | 47 | 23 |
| EC2, joint | Decision | 39 | 42 | 44 | 47 | 18 |
| EC2, eligibility first | Decision | 38 | 41 | 44 | 47 | 18 |

联合目标扩展使用全部 48 个本地 Qwen3-8B 单元格与 288 个保留分支（表 34）。本地回执与 linkage 检查固定为 1，O_κ^loc = 1。对指派 β，目标为 (I_c^obs(β), D_c^loc(β))，其中 D_c^loc = 1 表示 L̂_c^{β,2} = R_c。全部 64 种指派初始都可能；规范元组包含在内，真实回复会保留它。枚举全部八种回复子集得到 384 个"单元格–历史"对。初始有 16 个联合像与 14 个资格坐标未消解。坐标像的乘积在 12 个单元格中引入了无支撑的对；施加 D_c^loc = 1 ⇒ I_c^obs = R_c 后仍有 6 个不精确的像。一次与两次回复之后，更强的联合构造仍分别在 9/144 与 4/144 个历史中不精确。

主要的联合检索表显示：eligibility-first 与 joint EC2 在预算 2 下分别查询 24 和 23 次，识别出 45/48 个完整像与 47/48 个资格取值。以决策为停止条件的变体只用 18 次查询，识别出 42/48 与 41/48 个完整像，同时识别出 47/48 个处置。在该预算下，规范的 Qwen3-8B 归档含两个正单元格。顺序控制与 joint EC2 使用相同的均匀先验与动作顺序平局打破；精确坐标表示保留了"动作成员向量"与"资格位"之间的关联。可见，更丰富的完整像目标需要额外的解析工作，却并未确立任何表示优势。

**一个完整的查询例子。** 每动作两个分支时，Qwen3-8B 归档有两个正的规范单元格：semantic-error 故障下的 task id-1004（verify 同时是观测赢家与 replay 赢家），以及 stale-message 故障下的 task id-1004（replacement 同时是两者）。在所述目标下，其余 46 个单元格要么已知 ineligible，要么未消解。这些结果说明：查询的目标是"动作 × 资格"的联合结论，它并不估计结果规律。

**事后目标停止审计。** 该比较复用同样的 48 个单元格、64 指派的查询视图与真实查询，不发起任何模型调用。它区分"仍未消解、操作上仍是 HOLD 的像"与"已被识别的 ineligible 处置"。预算 2 时，整目标联合规则用 23 次查询识别出 45 个完整像与 47 个放行处置；联合处置规则用 18 次查询识别出 42 个完整像与 47 个处置；eligibility-first 处置停止用 18 次查询识别出 41 个完整像与 47 个处置。预算 3 时，整目标规则用 26 次查询识别出全部 48 个完整像；两条处置停止规则各用 19 次查询，分别识别出 43 与 42 个完整像，同时识别出全部 48 个处置。每条处置规则都给出 2 个正确的 Continue 决策、46 个已知 ineligible 处置、0 个错误处置。这一同归档比较说明：当放行决策可以更早被认证时，更丰富的目标需要更多解析工作。
## 附录 G 前瞻性重复分支研究（Prospective Repeated-Branch Study）

**原始 Terra 参考面板。** 在 24 个受限规划 checkpoint 上，每个动作抽样一次时 held-out strict success 为 0.699，而固定 verify 为 0.771（表 37）。增加选择抽样数并不能缩小这一差距，反而抬高调用成本。selection 与 evaluation 两块之间的公开最佳集合一致率在 k = 1 时为 0.318，到 k = 2、4 降至 0.204 与 0.167；strict 集合一致率分别为 0.378、0.262、0.250（表 36）。主要对比是"held-out strict success 上所选策略减固定 verify"。

该面板含 12 个 12 项任务与 12 个 16 项任务。每项有整数的 benefit、cost、time、prerequisite、conflicting-pair、budget 与 subset-size 字段。一次确定性贪心扫描构造出一个可行但次优的当前计划；当前平均 benefit 与精确最优之比为 0.650。Retry、verify 与 replace 收到同样的公开任务与当前计划，replacement 使用同样的模型与权限。

GPT-5.6 Terra 以 medium 推理强度运行在全新的一次性上下文中，禁止使用工具。这 576 次调用在每个 checkpoint 上为三个动作各取八次抽样：抽样 0–3 为 selection，4–7 为 evaluation，采用固定的交错调度、并发四个请求。提示词中不含任务标识符、抽样序号、分块指派与最优值。两次因容量失败的调用在允许的第二次尝试中成功。576 个完成输出中，557 个有可行的所选子集，522 个总数自洽；这些检查在重叠的行上可能同时失败。没有发生任何工具调用。全新上下文并不意味着提供方是 iid 抽样。Luna 与 Sol 扩展使用同样的冻结提示词与调度，小结见下文。

公开分数（public score）在以下条件同时满足时为"重算后的 benefit"：子集可行、自报总数一致、且未调用工具；strict success 还额外要求等于离线精确最优。对每个 k ∈ {1, 2, 4}，四个 selection 索引的全部大小为 k 的子集给出一个 argmax 动作集合；均匀打破平局定义出所选混合，并在每动作四个留出抽样上评估。六任务、36 次调用的开发面板预先选定了固定 verify；固定 retry、固定 replacement 与均匀动作选择是另外的基线。固定动作花费一次最终调用，选择花费 3k + 1 次调用。性能与 token 由留出抽样估计，而非在线部署。完整面板使用 12,376,363 个输入 token（11,631,104 个已缓存）与 592,590 个输出 token；缓存 token 仍计入输入总量。

Checkpoint 是统计单元。描述性 95% 百分位区间在两个任务规模层内做 10,000 次 bootstrap 重抽样，并保持完整的策略比较；重复抽样与重叠子集不是独立任务。exact set agreement 对平局敏感，未必随 k 上升。在 192 个三动作抽样向量中，20 个没有任何严格成功的动作，90 个三个都成功——平局集合在两个极端都会出现。12 项任务上，"所选减 verify"的 strict success 差在 k = 1、2、4 时分别为 −0.131、−0.133、−0.104；16 项任务上分别为 −0.012、−0.019、−0.017。赤字集中在较小任务的层内。该面板检验的是规划 checkpoint 上的分支复现与动作选择（表 35）。

**表 35：原始 Terra 规划队列上的 held-out strict success 与归一化公开收益。** Calls 含选择与最后一次动作；每个指标都有描述性的 95% checkpoint-bootstrap 区间。

| Policy | Calls | Strict Est | Lower | Upper | Norm. benefit Est | Lower | Upper |
|---|---|---|---|---|---|---|---|
| Fixed retry | 1 | 0.677 | 0.552 | 0.802 | 0.848 | 0.763 | 0.922 |
| Fixed replacement | 1 | 0.688 | 0.562 | 0.802 | 0.887 | 0.825 | 0.945 |
| Uniform | 1 | 0.712 | 0.608 | 0.806 | 0.882 | 0.841 | 0.920 |
| Fixed verification | 1 | 0.771 | 0.656 | 0.875 | 0.912 | 0.853 | 0.963 |
| Selected, k = 1 | 4 | 0.699 | 0.591 | 0.798 | 0.872 | 0.824 | 0.913 |
| Selected, k = 2 | 7 | 0.695 | 0.583 | 0.797 | 0.870 | 0.812 | 0.917 |
| Selected, k = 4 | 13 | 0.710 | 0.594 | 0.816 | 0.880 | 0.807 | 0.939 |

**表 36：原始 Terra 规划队列上 selection 与 evaluation 两块之间的精确最佳集合一致率。** Public 用可观测分数，Strict 用仅评估器可见的最优性标签。

| k | Public Estimate | Lower | Upper | Strict Estimate | Lower | Upper |
|---|---|---|---|---|---|---|
| 1 | 0.318 | 0.216 | 0.424 | 0.378 | 0.268 | 0.492 |
| 2 | 0.204 | 0.119 | 0.303 | 0.262 | 0.161 | 0.377 |
| 4 | 0.167 | 0.042 | 0.333 | 0.250 | 0.083 | 0.417 |

**表 37：原始 Terra 规划队列上所选策略的对比与每次决策的期望输入加输出 token。** 差值相对固定 verify；区间是配对的 strict success 差。

| k | Calls | Mean tokens | Strict-success diff Estimate | Lower | Upper |
|---|---|---|---|---|---|
| 1 | 4 | 89997.928 | -0.072 | -0.142 | -0.001 |
| 2 | 7 | 157445.139 | -0.076 | -0.156 | 0.001 |
| 4 | 13 | 292310.155 | -0.061 | -0.160 | 0.035 |

### G.1 独立规划复现（Independent planning replication）

我们在采集之前固定了一个新的 24-checkpoint 面板、提示词、请求顺序、评分、两个执行块以及主要的 A1 − A4 对比。12 个种子（98231 起、步长 101，至 99342）与任务规模 12、16 的完整叉乘使用生成器种子 seed + n，避免不同规模之间出现嵌套的随机流。全部 576 次完成的 Terra medium 执行都被保留。公开任务与当前制品在各恢复指令间共享；评估器最优值、任务标识符、种子与块序号不进提示词。调用使用全新上下文与打乱后的顺序——这降低顺序混杂，但并不确立提供方的独立抽样。传输失败允许重试一次；已完成的无效或次优输出从不重试。科学制品保留协议、调用顺序与时间、用量、输出以及离线评分输入。

主要对比为 0.320（95% 配对区间 [0.240, 0.406]）。区间在规模层内对 24 个 checkpoint 重抽样 10,000 次，种子 98419。差值在每个配对重抽样内部计算，而不是把两个独立均值的区间相减。这一实现修正是在分析完成的面板之前做出的。全部三种预算的结果见表 38。匹配的多动作贡献为 0.391、0.205、0.083；匹配的单例贡献为 0.013、0.034、0.000；平均集合大小为 2.411、2.122、1.833。这些分解是描述性的。

**表 38：24 个新规划 checkpoint 上的独立复现。** Agreement 用公开分数集合；Success 在 held-out block 上评估"从这些集合中均匀选择"的策略。每个指标都有描述性的 95% checkpoint-bootstrap 区间。

| k | Agreement Estimate | Lower | Upper | Success Estimate | Lower | Upper |
|---|---|---|---|---|---|---|
| 1 | 0.404 | 0.307 | 0.503 | 0.765 | 0.677 | 0.844 |
| 2 | 0.238 | 0.148 | 0.341 | 0.754 | 0.665 | 0.835 |
| 4 | 0.083 | 0.000 | 0.208 | 0.762 | 0.665 | 0.847 |

公共动作重叠（common-action overlap）在 k = 1、2、4 时为 0.940、0.863、0.750；Jaccard 相似度为 0.693、0.557、0.375。固定 verify 达到 0.771 的 strict success。"所选减 verify"的差按同样预算顺序为 −0.006 [−0.049, 0.037]、−0.016 [−0.064, 0.031]、−0.009 [−0.054, 0.036]。每个区间都含零，因此该面板支撑"一致率下降"，但并未确立"选择存在赤字"。选择成本仍是 3k + 1 次调用，固定动作只有 1 次。采集使用 12,401,744 个输入 token（11,590,656 个已缓存）与 599,798 个输出 token；缓存 token 计入输入总量。

### G.2 GPT-5.6 家族扩展（GPT-5.6 family extension）

家族扩展复用两个冻结队列、公开任务文件、当前计划、动作指令、分块指派与评分代码。Terra 贡献上面两个已完成的参考面板；Luna 与 Sol 后采集，使用同样的八抽样调度、全新上下文、medium 推理强度并禁止工具。每个"模型–队列"面板含 576 条响应，六个面板共 3,456 条。因此 Terra 与后续运行在任务和提示词上是匹配的，但采集窗口不同。面板层面的"可行行/严格行"计数保留在运行清单中；它们是响应契约的诊断量，不是额外的统计单元。

**表 39：GPT-5.6 家族的精确公开分数集合一致率。** 每个条目是按任务规模分层的 10,000 次 checkpoint-bootstrap 重抽样给出的 Estimate、Lower 或 Upper。六个面板各含 24 个 checkpoint。

| Cohort | Model | k=1 Est | Lower | Upper | k=2 Est | Lower | Upper | k=4 Est | Lower | Upper |
|---|---|---|---|---|---|---|---|---|---|---|
| Study | Terra | 0.318 | 0.221 | 0.424 | 0.204 | 0.122 | 0.306 | 0.167 | 0.042 | 0.333 |
| Study | Luna | 0.234 | 0.164 | 0.312 | 0.150 | 0.109 | 0.199 | 0.083 | 0.000 | 0.208 |
| Study | Sol | 0.424 | 0.341 | 0.503 | 0.331 | 0.242 | 0.428 | 0.167 | 0.042 | 0.333 |
| Replication | Terra | 0.404 | 0.307 | 0.503 | 0.238 | 0.148 | 0.343 | 0.083 | 0.000 | 0.208 |
| Replication | Luna | 0.299 | 0.224 | 0.388 | 0.212 | 0.139 | 0.303 | 0.250 | 0.083 | 0.417 |
| Replication | Sol | 0.497 | 0.427 | 0.570 | 0.422 | 0.326 | 0.520 | 0.458 | 0.292 | 0.625 |

**表 40：GPT-5.6 家族在留出抽样上的所选 strict success。** 每个条目来自同一 checkpoint-bootstrap 流程；Fixed verify 是对应"模型–队列"面板内的单次调用基线。

| Cohort | Model | k=1 Est | Lower | Upper | k=2 Est | Lower | Upper | k=4 Est | Lower | Upper | Fixed Est | Lower | Upper |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Study | Terra | 0.699 | 0.588 | 0.795 | 0.695 | 0.581 | 0.794 | 0.710 | 0.590 | 0.816 | 0.771 | 0.656 | 0.865 |
| Study | Luna | 0.575 | 0.469 | 0.674 | 0.568 | 0.460 | 0.669 | 0.538 | 0.417 | 0.660 | 0.635 | 0.510 | 0.750 |
| Study | Sol | 0.722 | 0.655 | 0.790 | 0.729 | 0.668 | 0.794 | 0.750 | 0.684 | 0.819 | 0.729 | 0.646 | 0.823 |
| Replication | Terra | 0.765 | 0.678 | 0.844 | 0.754 | 0.666 | 0.835 | 0.762 | 0.665 | 0.847 | 0.771 | 0.667 | 0.865 |
| Replication | Luna | 0.727 | 0.644 | 0.803 | 0.728 | 0.646 | 0.804 | 0.719 | 0.630 | 0.802 | 0.760 | 0.656 | 0.854 |
| Replication | Sol | 0.808 | 0.745 | 0.867 | 0.814 | 0.739 | 0.881 | 0.825 | 0.743 | 0.903 | 0.844 | 0.760 | 0.917 |

六个面板在 k = 4 时的精确一致率都低于 k = 1，尽管幅度取决于模型与队列。在任务匹配的面板中，所选 strict success 保持在固定的"模型–队列"验证器附近；相应的点对比与配对区间保留在分析清单中。事后模型选择审计用重复 0–3 做稳定性选择、重复 4–7 做留出评估，作为描述性的敏感性分析报告，而非预先设定的模型排名。
### G.3 exact-set 一致率与经验平局变化（Exact-set agreement and changing empirical ties）

**表 41：原始 24 个规划 checkpoint 上观测公开分数集合一致率的事后分解。** Single 与 Multiple 是按匹配集合大小划分的、对 Agreement 的互斥贡献；Mean size 对两个块取平均；Success 在 held-out block 上评估抽样分数的动作混合；固定 verify 一次调用达到 0.771，选择需要 3k + 1 次调用。

| k | Agreement | Single | Multiple | Mean size | Success | Calls |
|---|---|---|---|---|---|---|
| 1 | 0.318 | 0.008 | 0.310 | 2.286 | 0.699 | 4 |
| 2 | 0.204 | 0.039 | 0.164 | 1.913 | 0.695 | 7 |
| 4 | 0.167 | 0.042 | 0.125 | 1.521 | 0.710 | 13 |

表 41 的分解使用附录 G 描述的原始 24 个规划 checkpoint 与公开分数子集。对每个 k，我们把一对估计的最大化者集合归为四类：相等的单例、相等的多动作集合、大小不等、大小相等但成员不同。它们按 checkpoint 取平均的比例之和为 1。k = 1、2、4 时，单个估计集合中单例的占比为 0.193、0.368、0.604；大小不等的配对贡献 0.544、0.557、0.292，大小相等但成员不同的配对贡献 0.138、0.240、0.542。这些是 checkpoint 内部相关的子集比较，不是额外的独立观测。

一个有限模型可以说明：为什么 exact-set 一致率与动作质量之间没有单调关系。设 m ≥ 2 个等成本动作具有独立同分布的 Bernoulli 结果、成功概率同为 p ∈ (0, 1)，每动作 n 次独立抽样。记 f_n(k) 与 F_n(k) 为 Binomial(n, p) 的概率质量与分布函数，F_n(−1) = 0。指定的 j 个动作恰好构成经验最大化者集合，当且仅当它们的计数都等于某个 k、而其余计数都更小。其概率因此为

$$a_{n, j} = \sum_{k=0}^{n} f_n(k)^j F_n(k - 1)^{m - j}, \qquad j = 1, \dots, m. \tag{51}$$

当 j = m 时约定 0⁰ = 1。两个独立块的 exact-set 记为 A_n，而恢复完整总体最大化者集合的概率记为 F^set_n：

$$A_n = \sum_{j=1}^{m} \binom{m}{j} a_{n, j}^2 \longrightarrow \frac{1}{m}, \qquad F^{set}_n = a_{n, m} = \sum_{k=0}^{n} f_n(k)^m \longrightarrow 0. \tag{52}$$

为看清极限：二项分布的最大质量趋于零，由联合界，任何"两计数相等"的概率也趋于零。于是经验最大化者以趋于 1 的概率唯一，由对称性每个动作的极限概率为 1/m。两块的独立性给出一致率的极限。此外 ∑_k f_n(k)^m ≤ (max_k f_n(k))^{m−1} → 0。然而，从任一块选出的任何动作，在一次全新的独立执行上的期望成功仍是 p。

单次抽样时，完整的平局集合发生在所有动作都成功或都失败，概率为 p^m + (1 − p)^m。每个大小为 j 的真非空子集出现的概率为 p^j(1 − p)^{m−j}。把它们的平方概率求和得

$$A_1(p) = \left( p^m + (1 - p)^m \right)^2 + \sum_{j=1}^{m-1} \binom{m}{j} p^{2j} (1 - p)^{2(m-j)} = A_1(1 - p). \tag{53}$$

因此，即便精确知道这个一致率，在等均值族中也无法区分"新动作成功概率 p"与"1 − p"。交叉项对应"一个全成功块配上一个全失败块"——两者的完整最大化者集合相同。

即使赢家唯一，完整的集合路径也可能隐藏质量。考虑两个动作，结果独立且 Y_{a,t} ~ Bernoulli(p_a)，跨动作、跨轮次。每轮为每个动作提供一次抽样，且只保留 S_n = arg max_a {n⁻¹ ∑_t Y_{a,t} − λC(a)}。记 p = (p₁, p₂)，并定义 p̃ = (1 − p₂, 1 − p₁)。耦合 Ỹ_{1,t} = 1 − Y_{2,t}、Ỹ_{2,t} = 1 − Y_{1,t} 在 p̃ 下给出所需的独立 Bernoulli 坐标，并保持每个差 Y_{1,t} − Y_{2,t} 不变。因此在同样的固定成本下，它保持整条带标签路径 (S_n)_{n≥1}（含平局）不变。任何只依赖集合的停止规则或随机化动作选择器，在这两组参数下都有相同的转录规律。两个成功概率都平移 c = 1 − p₁ − p₂，因此总体偏好间隔不变。对从这条路径选出的任何动作，其在独立新执行上的期望成功平移 c。等成本时，(p₁, p₂) = (0.9, 0.8) 与 p̃ = (0.2, 0.1) 共享同样的唯一最佳动作与同样的 set-path 法律，而它们的最佳动作成功率分别是 0.9 与 0.2。

令 θ_max = max_a θ_a 表示最佳的绝对成功率。对只用集合路径与独立随机化的估计器 v̂，尖锐的两点界为

$$\inf_{\hat{v}} \max_{\theta \in \{p, \tilde{p}\}} E_{\theta} | \hat{v} - \theta_{max} | = \frac{|1 - p_1 - p_2|}{2}. \tag{54}$$

估计器在两组参数下同分布，故由三角不等式，两者风险之和至少为 |1 − p₁ − p₂|；θ_max 两个取值的中点这一常数估计器达到等号。当 p₁ = p₂ = p 时，退化为常见的"质量歧义"p 对 1 − p，风险为 |1 − 2p|/2。原始计数或绝对分数能提供这条"仅集合"观测通道所缺少的信息。

**绝对信息与有限抽样。** 等成本时，第一步的规律决定增量 Y_{1,t} − Y_{2,t} 的 iid 分布：取 1、−1、0 的概率分别为 u、v、1 − u − v，因而决定完整的路径规律。解出均值即得式 (4)。于是，一个总体统计量 r(p) 恰好在"对每一组不同的配对都有 r(p) ≠ r(1 − p₂, 1 − p₁)"时消除剩余歧义。汇总成功满足这一条件。保留"两个动作是否都成功"也够：若 t = Pr(Y₁ = Y₂ = 1)，则 p₁ = u + t、p₂ = v + t。总成功数的方差在该变换下不变，因此不够。

对有限样本构造，保留 B 次独立的单轮集合观测与 N 次独立的配对总成功观测。令 d̂ 在前者上对 1{S₁ = {1}} − 1{S₁ = {2}} 取平均，ŝ 在后者上对 Y₁ + Y₂ 取平均。两组样本可以重叠，但各自内部必须独立。对 0 < α_d, α_s < 1，取 ε_d = √(2 log(2/α_d)/B)，ε_s = √(2 log(2/α_s)/N)。Hoeffding 不等式（Hoeffding, 1963）与联合界（Bonferroni, 1936）给出

$$\Pr\{ | \hat{d} - d | \le \varepsilon_d,\ | \hat{s} - (p_1 + p_2) | \le \varepsilon_s \} \ge 1 - \alpha_d - \alpha_s. \tag{55}$$

于是在该事件上，p̂₁ = (ŝ + d̂)/2 与 p̂₂ = (ŝ − d̂)/2 的绝对误差都不超过 (ε_d + ε_s)/2。这些界使用独立的重启观测；沿同一条累积路径的相继集合是相关的，不能替代那些样本。达到式 (54) 的中点在所指定的两点参数类上最优，但它不断言未知间隔可以在没有抽样误差的情况下被估计。

当 m = 3、p = 0.9 时，A₁ = 0.552826、A₄ = 0.182657，期望成功仍是 0.9——这并非普遍的下降趋势。p = 0.5 时 A₁ = 0.156250，而同一极限是 1/3。该计算为"exact-set 指标的变化"给出了受控的解释。Terra 分解度量的是相伴的经验集合大小变化，并不断言其未知动作均值相等。

### G.4 对自报总数的敏感性（Sensitivity to self-reported totals）

规划契约既检查所选项，也检查自报的 benefit、cost 与 time。为把"解题质量"与"报告准确性"分开，我们用所选项标识符与公开任务字段重算 benefit。只要选择满足每个任务约束与工具契约——无论其自报总数如何——敏感性分数就保留这个 benefit。Semantic success 要求可行且最优的选择；strict success 还保留原有的报告要求。二者都在用敏感性分数完成选择之后、于 held-out block 上评估。这次事后分析在每个队列使用全部 576 次执行与 24 个 checkpoint，分块、子集比较与 checkpoint bootstrap 均与主分析相同。

自报总数与重算值不一致的执行，原始队列有 53 个、独立队列有 48 个。去掉该要求分别在 35 与 24 次执行中改变了选择分数；不可行的选择仍然无效。k = 4 时，所选最大化者集合在原始队列 9 个、独立队列 3 个 checkpoint 上发生改变。两个队列的 exact agreement 仍从 k = 1 降到 k = 4（表 42）。对所选动作质量的影响则不同：在语义评分下，semantic success 在原始队列从 0.725 变到 0.700，在独立队列从 0.796 变到 0.799。

**表 42：用重算的可行收益做选择。** Agreement 比较完整最大化者集合；Semantic 与 Strict 在 held-out block 上评估所选动作混合。每个队列 24 个 checkpoint；Lower 与 Upper 是描述性 95% checkpoint-bootstrap 区间的端点。

| Cohort | k | Agreement Est | Lower | Upper | Semantic Est | Lower | Upper | Strict Est | Lower | Upper |
|---|---|---|---|---|---|---|---|---|---|---|
| Original | 1 | 0.359 | 0.250 | 0.479 | 0.725 | 0.614 | 0.827 | 0.697 | 0.592 | 0.796 |
| Original | 2 | 0.221 | 0.126 | 0.339 | 0.713 | 0.600 | 0.819 | 0.686 | 0.577 | 0.788 |
| Original | 4 | 0.125 | 0.000 | 0.250 | 0.700 | 0.580 | 0.812 | 0.679 | 0.562 | 0.786 |
| Independent | 1 | 0.477 | 0.365 | 0.594 | 0.796 | 0.706 | 0.877 | 0.764 | 0.678 | 0.843 |
| Independent | 2 | 0.325 | 0.203 | 0.459 | 0.786 | 0.691 | 0.871 | 0.753 | 0.664 | 0.834 |
| Independent | 4 | 0.208 | 0.042 | 0.375 | 0.799 | 0.698 | 0.889 | 0.764 | 0.668 | 0.849 |

### G.5 经验近平局敏感性（Empirical near-tie sensitivity）

这次事后分析保留每个 Terra 面板的全部 24 个 checkpoint。对 checkpoint s，令 m_s 为所选项数的公开上限，b_{s,(j)} 为第 j 大的公开项收益。忽略其余可行性约束，得到公开上界

$$U_s = \sum_{j=1}^{m_s} b_{s, (j)}. \tag{56}$$

令 v_{s,a,r} 为动作 a 在第 r 次重复中重算得到的可行公开收益，无效响应记 0。对 k 次重复的子集 J，经验容差集合为

$$A_{s, J, \epsilon} = \left\{ a \in A_0 : \sum_{r \in J} v_{s, a, r} \ge \max_{a' \in A_0} \sum_{r \in J} v_{s, a', r} - \epsilon k U_s \right\}. \tag{57}$$

四种容差为 ε ∈ {0, 0.02, 0.05, 0.10}，k ∈ {1, 2, 4}（表 43）。我们保留原始"四次抽样 selection 块 + 四次抽样 evaluation 块"中所有块内子集对。所选动作混合在 A_{s,J,ε} 上均匀，并在全部四个留出抽样上评估。strict 标签与真实最优只进入评估环节；选择分数与 U_s 用公开任务信息。整数分求和与有理阈值保留了精确平局。这些是经验集合，不主张任何总体覆盖。

**表 43：完整的经验容差敏感性。** Agree 为 exact-set 一致率，Common 为非空交集频率，Jacc. 为 Jaccard 重叠，Size 为两个块上集合基数的平均；Strict 与 Public 在 held-out block 上评估所选混合。每个队列 24 个 checkpoint。

| ε | k | Orig Agree | Common | Jacc. | Size | Strict | Public | Indep Agree | Common | Jacc. | Size | Strict | Public |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.000 | 1 | 0.318 | 0.898 | 0.619 | 2.286 | 0.699 | 0.662 | 0.404 | 0.940 | 0.693 | 2.411 | 0.765 | 0.699 |
| 0.000 | 2 | 0.204 | 0.755 | 0.472 | 1.913 | 0.695 | 0.661 | 0.238 | 0.863 | 0.557 | 2.122 | 0.754 | 0.695 |
| 0.000 | 4 | 0.167 | 0.458 | 0.299 | 1.521 | 0.710 | 0.668 | 0.083 | 0.750 | 0.375 | 1.833 | 0.762 | 0.695 |
| 0.020 | 1 | 0.474 | 0.948 | 0.727 | 2.510 | 0.702 | 0.665 | 0.458 | 0.982 | 0.759 | 2.578 | 0.756 | 0.695 |
| 0.020 | 2 | 0.358 | 0.919 | 0.660 | 2.361 | 0.704 | 0.663 | 0.346 | 0.958 | 0.680 | 2.438 | 0.758 | 0.695 |
| 0.020 | 4 | 0.167 | 0.875 | 0.556 | 2.083 | 0.707 | 0.669 | 0.208 | 0.917 | 0.535 | 2.229 | 0.748 | 0.689 |
| 0.050 | 1 | 0.576 | 0.984 | 0.810 | 2.677 | 0.710 | 0.668 | 0.578 | 0.992 | 0.829 | 2.714 | 0.761 | 0.697 |
| 0.050 | 2 | 0.377 | 0.954 | 0.704 | 2.476 | 0.708 | 0.667 | 0.411 | 0.965 | 0.733 | 2.538 | 0.758 | 0.695 |
| 0.050 | 4 | 0.125 | 0.917 | 0.569 | 2.188 | 0.714 | 0.670 | 0.250 | 0.917 | 0.562 | 2.271 | 0.748 | 0.689 |
| 0.100 | 1 | 0.596 | 0.984 | 0.826 | 2.714 | 0.709 | 0.668 | 0.609 | 0.992 | 0.844 | 2.740 | 0.761 | 0.697 |
| 0.100 | 2 | 0.395 | 0.954 | 0.714 | 2.493 | 0.710 | 0.667 | 0.434 | 0.965 | 0.741 | 2.552 | 0.758 | 0.695 |
| 0.100 | 4 | 0.125 | 0.917 | 0.569 | 2.188 | 0.714 | 0.670 | 0.250 | 0.917 | 0.562 | 2.271 | 0.748 | 0.689 |

不确定性方面，10,000 次 checkpoint bootstrap 在层内重抽样 12 个 12 项任务与 12 个 16 项任务，保留每一对配对观测（种子 98519）。表 44 报告配对的"k = 4 减 k = 1"对比；区间按队列分别汇总。与原始零容差区间端点的小差异，来自本次敏感性分析所用的独立 bootstrap 流。

**表 44：配对变化及其描述性 95% 百分位区间。** 每个对比在指定经验容差下比较 k = 4 与 k = 1。

| Cohort | ε | Agreement ΔEst | Lower | Upper | Strict ΔEst | Lower | Upper | Public ΔEst | Lower | Upper |
|---|---|---|---|---|---|---|---|---|---|---|
| Original | 0.000 | -0.151 | -0.281 | -0.005 | 0.011 | -0.033 | 0.057 | 0.006 | -0.021 | 0.034 |
| Original | 0.020 | -0.307 | -0.451 | -0.156 | 0.005 | -0.020 | 0.028 | 0.004 | -0.014 | 0.020 |
| Original | 0.050 | -0.451 | -0.573 | -0.315 | 0.004 | -0.015 | 0.023 | 0.002 | -0.009 | 0.013 |
| Original | 0.100 | -0.471 | -0.589 | -0.341 | 0.004 | -0.014 | 0.023 | 0.003 | -0.008 | 0.013 |
| Independent | 0.000 | -0.320 | -0.406 | -0.237 | -0.003 | -0.029 | 0.023 | -0.005 | -0.025 | 0.013 |
| Independent | 0.020 | -0.250 | -0.378 | -0.115 | -0.008 | -0.024 | 0.006 | -0.006 | -0.018 | 0.004 |
| Independent | 0.050 | -0.328 | -0.448 | -0.208 | -0.013 | -0.029 | 0.000 | -0.008 | -0.021 | 0.003 |
| Independent | 0.100 | -0.359 | -0.484 | -0.232 | -0.013 | -0.029 | 0.000 | -0.008 | -0.021 | 0.003 |

容差为零时，每个经验动作集合都与原始整数分数的 argmax 一致，复现了一致率、平局结构与所选 strict success。容差为正时，报告集合的变化由公开分数的间隔决定。全部阈值与 checkpoint 级输出都保留在科学制品中。
### G.6 一致率度量与经验平局（Agreement metrics and empirical ties）

这次事后分析使用与 5.2 节相同的 24 个 checkpoint 和全部块内子集。对两个非空最大化者集合 A、B，公共动作一致率为 1{A ∩ B ≠ ∅}，Jaccard 相似度为 |A ∩ B|/|A ∪ B|，两次独立均匀选择的一致概率为 |A ∩ B|/(|A||B|)。每个度量先在 checkpoint 内对子集对取平均，再对 checkpoint 等权平均。在这个面板上，四种一致率度量全部下降（表 45）。

一个描述性参照保留每个块的经验集合大小分布，同时独立随机化动作身份。记 p̂_{b,j} 为块 b 中大小 j 集合的占比，其 exact-set 一致率为 ∑_{j=1}^{3} p̂_{1,j} p̂_{2,j}。超额一致率（excess agreement）= 观测一致率减去该参照。这个重新贴标签的参照去除了持久的动作身份，它并不假设真实动作均值相等。超额一致率变化的区间包含零，因此该面板无法分辨下降中有多少归因于集合大小、多少归因于动作身份。

**表 45：24 个 checkpoint 上的替代一致率度量。** Change 为 k = 4 减 k = 1；Lower 与 Upper 是按 checkpoint 规模分层的 10,000 次 bootstrap 给出的描述性 95% 百分位界。所有比较在 checkpoint 内保持配对。

| Metric | k=1 | k=2 | k=4 | Change Est | Lower | Upper |
|---|---|---|---|---|---|---|
| Exact set | 0.318 | 0.204 | 0.167 | -0.151 | -0.281 | -0.005 |
| Common action | 0.898 | 0.755 | 0.458 | -0.440 | -0.607 | -0.271 |
| Jaccard | 0.619 | 0.472 | 0.299 | -0.320 | -0.428 | -0.197 |
| Uniform choice | 0.318 | 0.300 | 0.194 | -0.123 | -0.206 | -0.027 |
| Size reference | 0.336 | 0.230 | 0.264 | -0.072 | -0.180 | 0.024 |
| Excess agreement | -0.018 | -0.026 | -0.097 | -0.079 | -0.189 | 0.049 |

匹配的单例集合在 k = 1、2、4 时对 exact 一致率贡献 0.008、0.039、0.042。两个块都达到精确最优的匹配多动作集合贡献 0.294、0.159、0.083；其余匹配多动作集合贡献 0.016、0.006、0.042。没有任何匹配的多动作配对在两个块中公开分数都为零。因此，成功的经验平局主导了单次抽样的匹配。这些类别描述的是观测输出；最优值只用于本次评估，从不提供给选择器。

### G.7 跨结果契约的集合一致率（Set agreement across outcome contracts）

这次事后分析复用下文 12-checkpoint 开发试点的全部 1,152 次 Qwen3-8B 执行，含四个 rank、四个 path 与四个 filter 任务（表 46）。每个动作的 32 次抽样构成四组连续的八抽样组；每组的前四次与后四次抽样定义配对的块。对 k ∈ {1, 2, 4}，在每对块之间比较全部大小为 k 的子集。平均时：组内子集对等权、checkpoint 内四组等权、12 个 checkpoint 等权。checkpoint bootstrap 在任务族内重抽样。这些区间描述的是这个固定面板；该分析不把试点变成确证性研究。

**表 46：12 个 Qwen3-8B checkpoint 上的整集合一致率。** Strict 要求答案正确且所报分数一致；Answer 只要求答案正确。成本调整行分别减去 retry、verify、replacement 的固定罚分 0.05、0.05、0.10。Change 为 k = 4 减 k = 1，附各自的 95% bootstrap 界。

| Outcome | k=1 | k=2 | k=4 | Change Est | Lower | Upper |
|---|---|---|---|---|---|---|
| Strict | 0.840 | 0.811 | 0.854 | 0.014 | -0.135 | 0.167 |
| Strict, cost-adjusted | 0.889 | 0.859 | 0.896 | 0.007 | -0.117 | 0.112 |
| Answer | 0.840 | 0.811 | 0.854 | 0.014 | -0.135 | 0.167 |
| Answer, cost-adjusted | 0.889 | 0.859 | 0.896 | 0.007 | -0.117 | 0.112 |

在严格评分下，匹配的多动作集合在 k = 1、2、4 时对一致率贡献 0.831、0.764、0.708。"两个块最高分都为零"的占比在每个预算下都是 0.583，而"全部成功"的占比从 0.247 降到 0.125。公共动作一致率为 0.999、0.997、1.000，Jaccard 相似度为 0.930、0.910、0.927。严格成功来自 rank 与 filter 族；path 族一个都没有。

在第一个块的经验最大化者中均匀选择、再到第二个块上评估，得到的 strict success 为 0.379、0.389、0.401——这些值是对全部平局选择解析积分得到的。仅按答案的对应值为 0.462、0.472、0.485；exact-set 一致率不变，因为"仅答案"契约改变了结果，却没有改变该面板上的所选集合划分。制品保留每个 checkpoint、成本敏感性、两个评估方向，以及最初抽样的平局打破诊断。我们不从这些事后比较推断任何总体偏好或恢复改进。

### G.8 置信关系开发试点（Confidence-relation development pilot）

一个单独的开发试点在 12 个新 checkpoint 上实例化了式 (34)，rank、path、filter 任务各四个，每个恢复动作 32 次独立种子抽样，固定参考 R = {verify}。Qwen3-8B 以 temperature 0.7、128 token 上限生成全部 1,152 个分支。公开检查器只用问题与文档；其输出在 120 个预检案例上与评估器一致，在每条采集到的分支上与存储的评估一致。六种可能的动作绑定之后接一次模拟的来源回执，该回执恢复出正确的绑定。此处资格要求回执完整、且请求与消息可关联；错误或不可解析的答案算作失败结果，而其完整的执行记录仍属资格内。在一次固定查看下，三个 Bonferroni 校正的双侧 Clopper–Pearson 区间给出候选均值盒。其抽样解释以固定的模型、软件与独立抽样的种子规律为条件。

1,152 个分支中，396 个通过严格评估，586 个答案错误，96 个答案正确但分数错误，74 个不可解析。所有回执都通过。回执之后有 11 个 overlap 像仍为 {∅, {verify}}；一个是单例 {verify}，产生一个正的统计证书。预先设定的开发阈值是三个正 checkpoint，因此该面板只是可行性结果。总用量为 622,272 个输入 token 与 103,199 个输出 token。事后"仅答案"检查得到 492 个正确答案：两个 checkpoint 在 96 个分支中全对，六个一个都不对，其余四个分别有 91、88、67、54 个正确答案。逐点置信区间只在那个单例像的 checkpoint 上排除 verify；在两种结果契约与全部 12 个 checkpoint 上做同时区间后，每个 overlap 都仍未解决。冻结协议、原始响应与评估与早先的执行归档分开保留。
## 附录 H 冻结 RecoveryBench 验证（Frozen RecoveryBench Validation）

**协议与统计单元。** 我们把 RecoveryBench 源码版本冻结在 commit c5f83f2ba4f882a9b544c7bf0fa9be1bc3859c78，把 Terminal-Bench 2.0 任务源码（Merrill et al., 2026）冻结在 commit 69671fbaac6d67a7ef0dfec016cc38a64ef7a77。该面板沿用 RecoveryBench（Tan et al., 2025）的失败 checkpoint 恢复设定，含 12 个固定 checkpoint、retry / verify / replace agent 三个动作，以及 GPT-5.6 的 Luna、Terra、Sol。每个"模型–checkpoint–动作"组合重复八次，共 12 × 3 × 3 × 8 = 864 个 episodes。合并审计含 864 个期望键与 864 个观测键，没有缺失或重复的 episode 键。所有主汇总都以 checkpoint 为统计单元。

**读出与分块。** 重复 0–3 是 selection block，4–7 是 held-out block。对 k ∈ {1, 2, 4}，每块中所有大小为 k 的子集产生一个完整的原生验证器奖励最大化者集合。Agreement 是"集合相等的跨块子集对"的比例。All-zero pairs 是"两个被比较子集里每个动作在两块中奖励都为零"的跨块子集对占全部跨块子集对的比例。Held-out success 对 selection 最大化者集合中的动作取二值原生奖励结果的平均；选择阶段不使用重复 4–7 的任何结果。二值成功定义为原生验证器奖励 > 0；原始连续奖励作为描述性量保留。互补的"全部成功配对"频率在全部九个"模型 × 预算"单元格中都是 0。checkpoint 层面的排名诊断报告在下文，其区间以非恒定的 bootstrap 重抽样为条件，属描述性，不构成模型排名主张。

**表 47：RecoveryBench 集合读出区间。** 每个条目是 10,000 次配对 checkpoint-bootstrap 重抽样给出的 Estimate、Lower 或 Upper。bootstrap 在 12 个 checkpoint 上重抽样，并保留 checkpoint 内全部模型、动作与重复观测。Held-out success 是所选动作集合上二值原生奖励结果的平均。

| Model | k | Agreement Est | Lower | Upper | All-zero Est | Lower | Upper | Held-out Est | Lower | Upper |
|---|---|---|---|---|---|---|---|---|---|---|
| Luna | 1 | 0.854 | 0.729 | 0.958 | 0.854 | 0.729 | 0.958 | 0.014 | 0.000 | 0.035 |
| Luna | 2 | 0.750 | 0.583 | 0.917 | 0.750 | 0.583 | 0.917 | 0.014 | 0.000 | 0.035 |
| Luna | 4 | 0.667 | 0.417 | 0.917 | 0.583 | 0.333 | 0.833 | 0.014 | 0.000 | 0.035 |
| Terra | 1 | 0.776 | 0.583 | 0.943 | 0.776 | 0.583 | 0.943 | 0.045 | 0.007 | 0.090 |
| Terra | 2 | 0.688 | 0.458 | 0.896 | 0.688 | 0.458 | 0.896 | 0.035 | 0.007 | 0.069 |
| Terra | 4 | 0.583 | 0.333 | 0.833 | 0.583 | 0.333 | 0.833 | 0.014 | 0.000 | 0.035 |
| Sol | 1 | 0.734 | 0.563 | 0.891 | 0.708 | 0.510 | 0.885 | 0.083 | 0.000 | 0.196 |
| Sol | 2 | 0.627 | 0.438 | 0.815 | 0.590 | 0.375 | 0.799 | 0.075 | 0.000 | 0.182 |
| Sol | 4 | 0.417 | 0.167 | 0.667 | 0.417 | 0.167 | 0.667 | 0.063 | 0.000 | 0.167 |

**决策价值分析。** 为把模型与动作的选择同留出评估分开，所有选择都只用重复 0–3。Agreement-guided 选择先在两个 selection 子块中选一致率更高的模型，再选 selection block 均值最大的动作，平局均匀平均。Outcome-mean 选择用同样的分块，但按 selection block 的结果均值选"模型–动作"对。直接的九臂规则与两阶段 outcome 规则在该面板上重合。由此得到的任务级 held-out success 区间见表 48。

**执行来源。** 每条合并行都有官方 reward，而执行状态记录该 reward 是如何获得的。原生验证器观测占 364 个 episodes，其中 46 个正奖励；模型协议失败占 487 个，其中 1 个正奖励；无效 adapter 尝试占 13 个，没有正奖励。这些类别是来源（provenance）字段，不是额外的统计单元。主表遵循声明的 reward 契约，下面的状态拆分把语义结果证据与执行协议证据分开。

**表 48：冻结 RecoveryBench 面板上的描述性决策价值分析。** Selection 用重复 0–3，evaluation 用重复 4–7。每个条目是 10,000 次任务 bootstrap 重抽样给出的 held-out success Estimate、Lower 或 Upper。

| Policy | Estimate | Lower | Upper |
|---|---|---|---|
| Agreement-guided, k = 1 | 0.013 | 0.000 | 0.028 |
| Agreement-guided, k = 2 | 0.030 | 0.003 | 0.066 |
| Outcome-mean direct | 0.065 | 0.000 | 0.171 |
| Fixed verify, Luna | 0.000 | 0.000 | 0.000 |
| Fixed verify, Terra | 0.021 | 0.000 | 0.063 |
| Fixed verify, Sol | 0.146 | 0.000 | 0.313 |

**表 49：全部 864 个 RecoveryBench episode 的执行来源。** Positive rate 是该行中"奖励为正的官方回执数"除以该行 episode 数。

| Execution status | Episodes | Reward-positive | Positive rate |
|---|---|---|---|
| Native verifier observed | 364 | 46 | 0.126 |
| Model protocol failure | 487 | 1 | 0.002 |
| Invalid adapter attempt | 13 | 0 | 0.000 |
| All episodes | 864 | 47 | 0.054 |

**排名一致性。** 我们对每个模型与预算，把 checkpoint 层面的一致率与 held-out success 求相关。九个单元格的 Spearman 估计全部为负，Kendall's τb 同号。表中报告 Spearman 区间。

**表 50：12 个 RecoveryBench checkpoint 上 exact-set 一致率与 held-out success 的 checkpoint 层面排名一致性。** 每个条目是 10,000 次 checkpoint-bootstrap 重抽样给出的 Estimate、Lower 或 Upper；恒定向量的重抽样被剔除。

| Model | k | Estimate | Lower | Upper |
|---|---|---|---|---|
| Luna | 1 | -0.443 | -1.000 | -0.094 |
| Luna | 2 | -0.443 | -1.000 | -0.094 |
| Luna | 4 | -0.632 | -1.000 | -0.357 |
| Terra | 1 | -0.783 | -1.000 | -0.283 |
| Terra | 2 | -0.741 | -1.000 | -0.266 |
| Terra | 4 | -0.529 | -1.000 | -0.255 |
| Sol | 1 | -0.796 | -0.936 | -0.535 |
| Sol | 2 | -0.776 | -0.916 | -0.535 |
| Sol | 4 | -0.376 | -0.693 | -0.174 |

---

参考文献从略，见原文。
