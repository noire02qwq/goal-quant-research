# FactorMiner：面向金融 Alpha 发现的、具备技能与经验记忆的自进化智能体（FactorMiner: A Self-Evolving Agent with Skills and Experience Memory for Financial Alpha Discovery）

> 来源：https://arxiv.org/abs/2602.14670
> 原文：docs/papers/arXiv-2602.14670.pdf
> 翻译日期：2026-11-12 ｜ 范围：全文 ｜ 方式：机器翻译初稿，未经人工校对
> 引用于：docs/literature/W2-context-memory-distillation.md

## 目录

- 摘要

- 关键词

- CCS 分类概念

- 1 引言

- 2 相关工作

  - 2.1 自动化 Alpha 因子发现

  - 2.2 具备技能与记忆的 AI 智能体

- 3 方法

  - 3.1 问题形式化

  - 3.2 因子挖掘技能架构

  - 3.3 经验记忆

  - 3.4 Ralph Loop：自进化因子发现

- 4 实验

  - 4.1 实验设置

  - 4.2 主要结果
    - 4.2.1 因子质量与多样性
    - 4.2.2 跨异构市场的稳健性
    - 4.2.3 集成与学习式选择
    - 4.2.4 额外稳健性检验
  - 4.3 经验记忆的影响

  - 4.4 挖掘效率分析

- 5 讨论

- 6 结论

- 7 局限性与伦理考量

- 致谢

- 参考文献

- 附录 A 算子库与准入标准

- 附录 B 端到端信号相关性

- 附录 C 经验记忆：禁止方向

- 附录 D 完整因子库（110 个因子）

## 摘要

公式化 alpha 因子挖掘是量化投资中一项关键却极具挑战的任务，其特点是搜索空间巨大，且需要具备领域知识、可解释的信号。然而，随着因子库因高冗余而不断增长，发现新颖信号变得愈发困难。我们提出 FactorMiner，一个轻量且灵活的自进化智能体框架，通过持续的知识积累来驾驭这一复杂局面。FactorMiner 结合了模块化技能架构（Modular Skill Architecture），把系统化的金融评估封装为可执行工具，并配以结构化的经验记忆（Experience Memory），将历史挖掘尝试蒸馏为可行动的洞见（成功模式与失败约束）。通过实例化 Ralph Loop 范式——检索、生成、评估、蒸馏——FactorMiner 迭代地利用记忆先验引导探索，在聚焦有前景方向的同时削减冗余搜索。在跨资产、跨市场的多个数据集上的实验表明，FactorMiner 构建出一个多样化、高性能且具竞争力的高质量因子库，并在因子库扩张的同时保持因子间的低冗余。总体而言，FactorMiner 在“相关性红海”（Correlation Red Sea）约束下，为可解释公式化 alpha 因子的可扩展发现提供了一条实用途径。

## 关键词

量化投资；公式化 Alpha；因子挖掘智能体技能；经验记忆；并行评估；日内预测

## CCS 分类概念

- 信息系统 → 数据挖掘；

- 计算方法学 → 智能体；

- 应用计算 → 经济学。

ACM Reference Format:

Yanlong Wang, Jian Xu, Hongkang Zhang, Shao-Lun Huang, Danny Dongning Sun, and Xiao-Ping Zhang. 2026. FactorMiner: A Self-Evolving Agent with Skills and Experience Memory for Financial Alpha Discovery. In Proceedings of the 32nd ACM SIGKDD Conference on Knowledge Discovery and Data Mining V.2 (KDD ’26), August 09–13, 2026, Jeju Island, Republic of Korea. ACM, New York, NY, USA, 12 pages. https://doi.org/10.1145/3770855.3818978

## 1 引言

发现具有预测力的 alpha 因子是量化交易与投资组合构建的核心。在实践中，自动化因子发现面临三个根本挑战：(i) 巨大的搜索复杂度——公式化表达式的空间随算子组合与参数呈组合式增长；(ii) 知识积累能力差——传统搜索方法（遗传编程、强化学习）无法在探索会话之间保留并复用洞见，导致重复试验；(iii) 可解释性约束——与黑箱神经预测器不同，金融从业者需要透明、可审计、具有明确金融逻辑的公式，以满足合规与风险管理要求。

传统方法高度依赖领域专家，他们基于金融直觉手工构造因子 [5, 13]。更近期地，机器学习方法被应用于资产定价 [7, 9]，展现出强大的预测能力，但往往牺牲可解释性。遗传编程 [16] 与强化学习 [41, 42] 提供了自动化搜索，但存在知识遗忘问题：随着因子库增长、相关性约束收紧，这些方法缺乏积累“何种做法有效、何种做法无效”这类结构性知识的机制。此外，现有方法孤立地看待每个挖掘出的因子，而不考虑全局因子库视角——它们优化单个因子的质量，却忽略新因子与既有因子库之间的相互作用，从而导致冗余发现与低效探索。

我们把公式化因子挖掘视为自进化 AI 智能体的一项任务 [36, 40]。每个因子都是关于市场字段（如收盘价、成交量、VWAP）的显式表达式，由包含 60 多个算子的库组合而成。与端到端神经方法不同，公式化因子支持人在回路的审计，并能在不同市场状态之间实现组合泛化。核心研究问题是：智能体如何高效地探索这一巨大的程序空间，同时保持对因子库的全局视角，并在多次探索会话中自主积累结构性知识？

我们提出 FactorMiner，一个通过两种协同机制应对上述挑战的自进化智能体框架：组合式技能架构与经验记忆。首先，我们将因子挖掘设计为一个可复用的智能体技能，可由语言模型智能体按需调用 [33, 40]。该技能封装了领域知识——一个包含 60 多个金融算子的精选算子库、一条带 IC 阈值与相关性检查的多阶段验证流水线，以及标准化的评估协议——从而支持灵活的任务分解与独立升级，无需重新训练智能体。其次，我们引入经验记忆，使智能体能够通过积累的知识实现自进化 [28, 36]。记忆存储了从历史挖掘会话中提炼出的结构性模式：成功模式（持续通过质量阈值的因子模板）与禁止区域（与既有库成员高度相关的因子族）。关键在于，该记忆保持全局因子库视角：智能体通过考量候选因子如何补充既有因子库来决定挖掘方向，而非孤立地优化单个因子。

智能体采用 Ralph Loop 范式实现自进化：从经验记忆中检索相关模式，借助检索到的先验调用挖掘技能生成候选因子，通过并行评估检验候选，并将结果蒸馏回记忆。这形成一个正向反馈循环——每次挖掘会话都提升未来的探索效率，使智能体得以持续打磨其搜索策略。

为保证计算效率，我们构建了一个轻量而高性能的系统，采用 GPU 加速算子、多进程并行以及 C 编译的高效数值运算。相比标准 Python 实现（如 NumPy/Pandas），该系统获得显著加速，使大规模迭代评估在计算上可行。我们将主要贡献总结如下：

- 面向智能体因子挖掘的经验记忆。我们将结构化经验记忆引入基于智能体的因子发现，通过积累的知识实现自进化。记忆存储可复用的模式以引导探索，与无记忆基线相比减少冗余搜索。

- 面向按需调用的模块化技能架构。我们将因子挖掘设计为组合式、可复用的技能，把领域知识封装在独立模块中。这支持灵活的智能体调用、独立的技能升级，并清晰分隔智能体推理与技能执行。

- 轻量高效的挖掘系统。我们使用 GPU 加速算子、多进程并行与 C 编译的高效数值运算构建高性能因子评估引擎，支撑大规模因子挖掘。这支持快速迭代与大规模因子探索，同时适应不同的服务器配置与算力预算。

- 全局因子库视角。我们将因子库准入机制纳入挖掘循环，使智能体从全局因子库视角做出挖掘决策。智能体考虑候选因子如何补充既有库，而非孤立地优化单个因子。

- 具有研究与实用价值的开放因子库。我们提供 110 个具有显式公式表达、并经真实市场数据验证的 A 股股票因子。这些可解释因子可作为诊断工具，用于理解跨市场行为异常与市场微观结构低效，为量化交易提供研究洞见与实用价值。

## 2 相关工作

### 2.1 自动化 Alpha 因子发现

公式化 alpha 库提供显式、人类可读的表达式，对可解释研究颇具价值。Kakushadze [13] 给出 101 个具有显式表达式且互相关性低（15.9%）的公式化 alpha，表明紧凑的公式库既可以多样也可以有效；广泛使用的行业变体如 Alpha191 以约 191 个表达式扩展了这一点，覆盖更多微观结构模式。此类库背后的发现过程往往缺乏文档，可能结合专家设计与自动化搜索（如遗传编程），但发布的产物是显式公式。这些经典库大多局限于日频数据，且深层嵌套表达式的可解释性会下降，因此高频市场仍缺乏可用于系统研究的同等级精选因子库。

为自动化因子发现，遗传编程等进化程序搜索方法把因子公式表示为可执行程序，并通过交叉与变异使其演化 [2, 16, 23]。实践中，朴素遗传编程对表达式的探索效率不高，收敛缓慢且缺乏语义引导，因为遗传算子主要作用于程序语法而非程序行为 [21, 30]。更近期地，机器学习方法被应用于经验资产定价与高维模型选择 [7, 9, 11, 12, 17]。尽管这些方法具有强劲的预测性能，但它们往往不如公式化信号透明，在高风险场景下难以解释或审计 [32]。

强化学习已被用于遍历公式化因子表达式的离散空间，把评估指标（如 IC/ICIR）作为奖励 [41, 42]，代价通常是额外的训练与重复评估开销。与此同时，神经与 LLM 驱动的框架生成并精炼公式化因子，其探索策略旨在缓解衰减与冗余 [35, 38]。尽管有这些进展，这些方法仍面临如何在多次挖掘会话之间显式且持续地复用结构性模式的挑战；随着因子库增长、冗余与相关性约束收紧，探索会变得越来越重复 [7, 17]。

### 2.2 具备技能与记忆的 AI 智能体

近期的语言模型智能体从一次性文本生成转向通过工具调用与反馈执行闭环任务。Toolformer [33] 以自监督方式训练 LLM 插入 API 调用，而 ReAct [40] 把推理轨迹与行动交织——智能体规划、调用工具、观察结果并迭代。这种工具增强、基于技能的视角启发了我们的设计：因子挖掘被打包为智能体可按需调用的可执行技能。把领域流程打包为可复用技能，使智能体无需微调模型权重即可处理复杂的专业任务，同时削减重复的上下文内指令及其 token 开销，提升多步领域工作流的可靠性。

记忆与自我改进机制进一步使智能体能够随时间积累经验。Reflexion [36] 使用基于语言的自我反思把教训存储为自然语言，生成式智能体 [28] 维护记忆流（如观察、反思、计划）以调节未来行为；更广泛地，持续学习研究如何在不发生灾难性遗忘的情况下保留知识 [27]。在我们的设定中，我们为符号程序综合实例化记忆：不再存储稠密表示或回放缓冲 [4]，而是保留因子挖掘过程中发现的可复用符号规则与结构性模式，以及有助于避开搜索空间中冗余区域的汇总统计量。

从理论角度看，元学习与元强化学习通过从先前任务或 episode 中提取可迁移的学习偏好来形式化“学会学习” [8, 10, 24]。类似地，记忆引导的挖掘过程可视为获取搜索先验：除产出单个因子外，系统还积累塑造未来探索的结构性知识。

除学习调用工具外，系统研究领域倡导模块化智能体架构，把子问题路由给专用模型、外部知识源与离散推理模块（如 MRKL [14]、HuggingGPT [34]）。与此同时，近期的基准与训练流程研究如何大规模地把 LLM 输出落地为可执行的 API 调用并减少工具幻觉，包括 API-Bank [18]、ToolLLM/ToolBench [31] 与 Gorilla/APIBench [29]。这些工作共同强调了把高层规划与可靠执行分离的重要性，以及以支持检索与持续更新的形式来表示工具与技能的重要性。

另一条研究线通过引入显式长期记忆管理器来应对有限上下文窗口下的长时程智能体行为。MemGPT [26] 提出受操作系统启发的分层记忆，在快速记忆与慢速记忆之间受控换页；Voyager [39] 则展示了一个开放式具身智能体，它积累可执行技能库并复用以泛化到新任务。这类设定往往是非平稳的：随着智能体获得新工具与技能（或外部库增长），可行的动作空间与冗余模式随之演化，从而促使经验总结机制的出现，以捕捉可复用模式并避免反复探索已知的死胡同。

## 3 方法

### 3.1 问题形式化

我们在由 𝑀 个资产、时间跨度 𝑇 构成的范围上定义 alpha 因子发现任务。原始市场输入表示为张量 D ∈ R^{𝑀×𝑇×𝐹}，其中每个元素 𝑑_{𝑚,𝑡}^{(𝑗)} 表示资产 𝑚 在时刻 𝑡 的特征 𝑗（如价格、成交量）的取值。

符号因子空间。一个符号 alpha 因子 𝛼 是由算子集 Ω 构成的计算程序，它把市场状态变换为截面预测信号 s𝑡 ∈ R^𝑀：

```
𝛼 : D:,:𝑡,: → s𝑡 ,   𝑠𝑡(𝑚) = 𝛼 (𝑑𝑚,:𝑡 )        (1)
```

其中 𝑠𝑡(𝑚) 表示资产 𝑚 相对同侪的预测分数。每个算子 𝑜 ∈ Ω 具有固定的元数与带类型的签名（如 time-series → time-series、cross-section → cross-section），程序 𝛼 ∈ P (Ω) 对应由 Ω 与允许参数构成的表达式树；Ω 的详细定义与分类见附录 A 与表 7。

𝛼 的有效性用信息系数（Information Coefficient，IC）来量化，它定义为信号 s𝑡 与后续收益 r𝑡 +1 ∈ R^𝑀 之间的截面 Spearman 秩相关：

```
IC𝑡 (𝛼) = Corr_rank( s𝑡 , r𝑡 +1 )                 (2)
```

其跨时间一致性用信息比率（ICIR）来度量：ICIR(𝛼) = 𝜇 (IC𝑡 )/𝜎 (IC𝑡 )。

相关性度量。为保证因子库的多样性，我们用两个因子 𝛼 与 𝛽 的已实现信号的截面 Spearman 相关的时间平均来度量它们之间的冗余：

```
             1 ∑︁
 𝜌 (𝛼, 𝛽) =            Corr_rank( s𝑡 (𝛼), s𝑡 (𝛽) ) ,   (3)
            |T | 𝑡 ∈ T
```

其中 T 表示评估时间戳的集合。该定义与我们当前的实现一致，但框架可以通过相应地替换 𝜌 (·, ·) 来容纳其他依赖性度量（如时序相关、偏相关或非线性依赖性度量）。

目标：正交因子库合成。FactorMiner 把该问题视为对多样化因子库 L = {𝛼 1, . . . , 𝛼 𝐾 } 的迭代构建。目标是在全局冗余约束下最大化因子库的总体预测质量：

```
                       ∑︁
   L ∗ = arg max           Φ(𝛼) s.t. ∀𝛼𝑖 ≠ 𝛼 𝑗 ∈ L : |𝜌 (𝛼𝑖 , 𝛼 𝑗 )| < 𝜃
               L⊂ P
                      𝛼∈L
                                                        (4)
```

其中 P 是可构造程序的无穷空间，Φ(·) 是适应度度量，𝜃 是相关性预算。

相关性红海。随着因子库 L 不断被填充，新正交因子的可行域——P_orth = {𝛼 ∈ P : max_{𝑔∈L} |𝜌 (𝛼, 𝑔)| < 𝜃 }——会随着多样性约束收紧而迅速收缩。标准搜索方法（如 GP 或 RL）常常陷入这一相关性红海，因为它们缺乏追踪已探索区域或失败模式的机制。

决策论式记忆形式化。为穿越相关性红海，我们把发现过程重新表述为在一个不断演化的内部知识状态 𝑆𝑡 = (L𝑡 , M𝑡 ) 上的序贯决策任务，其中 M𝑡 表示持久的经验记忆。智能体首先从 M𝑡 与 L𝑡 中检索出上下文相关的记忆信号 𝑚𝑡 ，然后从记忆条件化的策略中采样候选：

```
𝛼 ∼ 𝜋 (𝛼 | 𝑚𝑡 ),   𝑚𝑡 = 𝑅(M𝑡 , L𝑡 )                   (5)
```

M 的作用是在程序空间 P 上诱导概率测度的收缩。通过把历史轨迹 𝜏 = {(𝛼𝑖 , 𝑅𝑖 )}𝑖=1𝐵 蒸馏为结构化模式，M 把采样质量移向正交流形 P_orth。从数学上说，记忆的演化由一个蒸馏算子 Ψ 支配：

```
M𝑡 +1 = Ψ(M𝑡 , 𝜏𝑡 )                           (6)
```

它更新智能体的信念分布，使未来探索被导向 P 中效用更高、冗余更低的区域。

### 3.2 因子挖掘技能架构

与传统 RL 或整体式（monolithic）智能体方法不同——后者领域逻辑往往被硬编码或与智能体的推理循环纠缠在一起——FactorMiner 采用模块化的、基于技能的架构。受工具增强范式 [33] 启发，我们把整个因子挖掘过程封装为一个独立、可复用的 Agent Skill：一个标准化接口，向 LLM 暴露高层能力，同时把底层执行细节抽象掉。整体交互模式如图 1 所示。

图1：FactorMiner 系统架构。Ralph Loop 框架整合三个关键组件：(1) 经验记忆，存储过去挖掘会话中的成功模式与禁止区域；(2) 智能体技能，封装多阶段验证流水线（IC 筛选、相关性检查、去重与完整验证）；(3) 因子库，在保持正交性约束的同时动态增长。智能体迭代地检索记忆先验、通过技能生成候选，并把结果蒸馏回记忆，以改进未来的探索。（原文第3页）

组合式设计。该技能被组织为一个层次化的工具库：

- 算子层（Operator Layer）：一组精选的 60 多个金融算子（如 TsRank、Rsquare），以 GPU 加速后端实现。这确保智能体的符号化提议是可执行的，且计算上高效。

- 验证流水线（Validation Pipeline）：一套严格、标准化的因子评估协议（check_ic → check_correlation → admit）。通过把验证与生成解耦，我们确保智能体的“创造力”被严格的定量约束所限制，从而减少幻觉或无效的候选。

基于技能的方法的优势。这种模块化设计相比整体式架构有三个显著优势：

(1) 防止计算幻觉：大语言模型往往难以进行精确算术与算法执行。通过把评估卸载给确定性的、基于代码的技能，FactorMiner 避免了“幻觉指标”：所报告的 IC 与 ICIR 是确定性计算得到的。

(2) 跨领域可迁移性：该技能通过配置文件进行参数化，以支持多个市场（如 A 股与 Crypto）。同一套高层智能体推理逻辑只需切换底层技能上下文，即可应用于不同的金融领域，我们的跨市场实验（4.2.2 节）验证了这一点。

(3) 独立优化：技能的执行后端与评估流水线可以独立于智能体的推理模型进行优化，在不重新训练 LLM 主干的情况下提升吞吐。

### 3.3 经验记忆

FactorMiner 的一个关键组件是经验记忆 M，一个从历史挖掘会话中积累洞见的结构化知识库。我们通过三个概念算子来形式化记忆系统的动态：形成（Formation）、演化（Evolution）与检索（Retrieval）。

记忆形成。在每个挖掘批次 𝑡 结束时，智能体分析挖掘轨迹 𝜏𝑡 = {(𝛼𝑖 , 𝑅𝑖 )}𝑖=1𝐵，其中 𝑅𝑖 表示评估反馈（IC、相关性等）。形成算子 𝐹 选择性地抽取信息性产物：

```
M𝑡 +1^form = 𝐹 (M𝑡 , 𝜏𝑡 )                             (7)
```

这一过程把原始数据蒸馏为符号模式，并把它们归类为成功模式 P_succ（通过准入的那些）与禁止区域 P_fail（因高相关而被拒绝的那些）。

记忆演化。已形成的记忆候选通过演化算子 𝐸 被整合进既有知识库：

```
M𝑡 +1 = 𝐸 (M𝑡 , M𝑡 +1^form )                            (8)
```

该算子合并冗余条目并丢弃低价值信息。举例来说，如果某个特定的 VWAP_Deviation 变体被准入但与既有因子呈现 0.82 的相关性，它会被重新归入 P_fail，以阻止进一步的冗余探索。

记忆检索。在因子生成阶段，智能体通过检索算子 𝑅 获取上下文相关的记忆信号 𝑚𝑡 ：

```
𝑚𝑡 = 𝑅(M𝑡 , L𝑡 )                         (9)
```

信号 𝑚𝑡 充当 LLM 策略的提示级约束，有效地塑造采样分布 𝜋 (𝛼 | 𝑚𝑡 )。在实践中，我们把经验存储为紧凑的自然语言模板，并附带典型示例（如“推荐方向”与“禁止方向”），通过与当前因子库诊断结果及近期拒绝原因相匹配来检索它们。

记忆内容。所得的记忆 M 维护一份关于不断演化的挖掘版图的持久记录：

(1) 挖掘状态（S）：追踪因子库的全局演化，包括当前因子库规模 |L|、近期准入日志，以及指示特定逻辑域（如价量反转）是否趋于过饱和的饱和度指标。

(2) 结构化经验（P）：这是智能体引导系统的核心，分为：

- 推荐方向（P_succ）：从近期批次蒸馏出的高成功率逻辑模板，例如高阶矩状态（用 Skew/Kurt 进行环境切换）与稳健效率交互。

- 禁止方向（P_fail）：因与既有因子库持续高度相关而被标记为“红海”的区域，例如简单的 VWAP 偏离或标准化收益。

(3) 战略洞见（I）：从挖掘过程中学到的高层经验，例如“非线性组合策略（如基于 XGBoost 的合成）往往优于线性策略”这一观察，或特定算子层面的警示（如高频数据中高阶矩的不稳定性）。

### 3.4 Ralph Loop：自进化因子发现

FactorMiner 采用 Ralph Loop 范式——一种智能体通过反复交互积累经验并自进化迭代精炼的哲学。我们通过把经验记忆整合进搜索过程（算法 1），为因子挖掘实例化了这一范式。其关键洞见在于：记忆使智能体学会“如何搜索”——在聚焦有前景区域的同时避免冗余探索。

```
算法 1 Ralph Loop：自进化因子发现
输入：算子库 Ω，经验记忆 M，目标因子库规模 𝐾
输出：因子库 L
Initialize L ← ∅
repeat
    Step 1: 记忆检索
        Retrieve memory signal 𝑚 ← 𝑅 ( M, L )
    Step 2: 引导式生成
        Sample batch C ∼ 𝜋 (𝛼 | 𝑚) using Ω
    Step 3: 多阶段评估
        Stage 1: 快速 IC 筛选（𝑀fast 个资产）
            C1 ← {𝛼 ∈ C : | IC (𝛼 ) | ≥ 𝜏IC }
        Stage 2: 针对 L 的相关性检查
            C2 ← {𝛼 ∈ C1 : max𝑔∈L |𝜌 (𝛼, 𝑔 ) | < 𝜃 }
        Stage 2.5: 替换检查
            For 𝛼 ∈ C1 \\ C2 , let 𝑔★ = arg max𝑔∈L |𝜌 (𝛼, 𝑔 ) |
            Replace 𝑔★ with 𝛼 if |𝜌 (𝛼, 𝑔★ ) | ≥ 𝜃 ,
            max𝑔∈L\\{𝑔★ } |𝜌 (𝛼, 𝑔 ) | < 𝜃 , and Φ(𝛼 ) ≥ Φ(𝑔★ ) + Δ
        Stage 3: 批内去重（批内 𝜌 < 𝜃 ）
        Stage 4: 完整验证（𝑀full 个资产）并收集轨迹 𝜏
    Step 4: 因子库更新
        Admit validated factors: L ← L ∪ Cadmitted
    Step 5: 记忆演化
        Update strategy: M ← 𝐸 ( M, 𝐹 (𝜏 ) )
until | L | ≥ 𝐾 或预算耗尽
```

我们对 Ralph Loop 的因子挖掘实例化具有四个关键性质：

全局因子库视角。与孤立优化单个因子的方法不同，我们的方法考虑每个候选如何补充既有因子库 L。相关性约束（阶段 2）保证多样性，而替换机制（阶段 2.5）允许高质量因子取代劣质因子。

记忆引导的探索。通过维护 P_succ 与 P_fail ，智能体避免对已知失败区域的冗余探索，同时聚焦于有前景的结构化模式。

多阶段评估。多阶段流水线在效率与准确性之间取得平衡：阶段 1 用小规模资产子集做快速筛选，阶段 2–3 施加相关性约束（因子之间与批内），阶段 4 只对存活下来的候选做完整验证。

自进化。每次迭代之后，记忆通过演化算子 𝐸 得到更新（整合来自 𝐹 的洞见），形成一个反馈回路，使智能体持续改进其搜索策略。这实现了持续学习：早期会话中积累的知识让后续探索受益。

轨迹语义。轨迹 𝜏𝑡 记录每个被评估候选的公式 𝛼、质量统计量（如 IC/ICIR）、冗余诊断量（如 max𝑔∈L |𝜌 (𝛼, 𝑔)|），以及拒绝或准入的结果（包括是否触发了替换）。这些字段是形成算子 𝐹 的输入，并支撑跨批次的经验蒸馏。

## 4 实验

### 4.1 实验设置

数据集。我们在 A 股股票与加密货币市场上评估 FactorMiner，以考察其发现效率与跨资产泛化能力。对于 A 股，我们使用三个指数成分池的日内 10 分钟 bar：中证 500 与中证 1000 成分股（覆盖中盘及更广泛的小/中盘），以及沪深 300 成分股（代表大盘），合计超过 2500 万个数据点。对于加密货币市场，我们使用来自 Binance 的 64 个主流资产的 10 分钟 bar。所有数据集覆盖 2024-Q1 至 2024-Q4 的训练期与 2025 年的留出测试期。预测目标被实例化为同一 10 分钟频率上的不重叠下一期收益比率，而挖掘框架可以容纳其他目标与时间跨度。

基线与指标。我们与六种代表性方法进行比较：(1) Alpha101 (Classic) [13]，一个手工公式的静态库；(2) Alpha101 (Adapted)，其参数针对高频数据调优；(3) Random Formula Exploration (RF)，在有界的深度/大小分布下从 P (Ω) 随机采样类型正确的表达式树；(4) GPLearn [37]，一种改进的遗传编程方法；(5) AlphaForge [35]，一个挖掘并动态组合公式化 alpha 因子的神经框架；以及 (6) AlphaAgent [38]，一个 LLM 驱动的提议-精炼框架。为公平比较，我们对每种方法应用相同的准入规则，并评估同等规模的因子集合；如果某方法准入的因子更少，我们就用 IC 最高的剩余候选补齐该集合。我们还在 4.3 节中把 No Memory 变体作为内部基线。性能用标准预测指标量化：用秩信息系数（Rank Information Coefficient）衡量预测精度，用其比值（ICIR）衡量跨时间稳定性。除非另有说明，我们用 IC 指代这一基于 Spearman 相关的 IC。在适用的情况下，所有基线共享同一算子库 Ω、数据字段与评估/准入协议，并由统一的评估引擎打分。对于需要基于 LLM 的提议生成的方法，我们使用 Gemini 3.0 Flash（除非另有说明）。我们不微调也不更新 LLM 权重；自进化来自检索条件化的生成、确定性技能执行、因子库准入与记忆蒸馏。

### 4.2 主要结果

#### 4.2.1 因子质量与多样性

表 1 报告了严格协议下的 2025 年样本外结果：Top-40 因子先在 CSI500 (2024) 上选出一次，随后冻结用于多数据集评估。在该协议下，FactorMiner 在四个市场上与所比较方法相比表现具有竞争力。在 Factor Library 设定下，它在 CSI500 上取得 IC/ICIR 为 8.25%/0.77，在其他市场上也有相近的竞争力提升（见表 1）。

图2：已发布的 A 股因子库的成对 Spearman 相关性热图（110 个准入因子），由共同时间–资产面板上截面标准化后的已实现因子信号计算得到。非对角线平均绝对相关为 Avg |ρ| = 0.203。（原文第6页）

在冗余方面，FactorMiner 选出的因子集合表现出中等程度的成对依赖。如表 1 中的 Avg |ρ| 所汇总，平均成对绝对相关在 A 股为 0.30–0.31、在 Crypto 为 0.25。相关性分布还显示出一个可控的尾部（A 股 |ρ| ≈ 0.44–0.45、Crypto 为 0.42），说明性能提升并非由少数近重复信号所驱动。我们进一步在图 2 中可视化完整准入因子库的相关结构。完整的因子公式见附录 D。

表1：更严格协议下的样本外性能对比。Top-40 因子在 CSI500 (2024) 上选出，并在 2025 年于各数据集上评估。对于 Alpha101，Classic 被限制在与 Adapted 相同的候选集上。所有报告的 IC 与 ICIR 均使用本文的绝对 IC 汇总方式：|E[𝐼𝐶𝑡 ]| 与 |E[𝐼𝐶𝑡 ]|/std(𝐼𝐶𝑡 )。Factor Combination 使用冻结的 Top-40，配以 EW 与 ICW（权重/符号在 2024 年上确定）。Factor Selection 在 2024 年上训练、在 2025 年上测试，使用 Lasso 与 XGBoost。

| 数据集 | 方法 | IC (%) | ICIR | Avg \|ρ\| | EW IC | EW ICIR | ICW IC | ICW ICIR | Las. IC | Las. ICIR | XGB. IC | XGB. ICIR |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CSI500 | RF‡ | 2.68 | 0.25 | 0.13 | 6.98 | 0.41 | 12.02 | 0.90 | 13.81 | 1.15 | 8.99 | 0.90 |
| CSI500 | Alpha101 (Classic) | 4.49 | 0.42 | 0.19 | 10.85 | 0.88 | 12.89 | 0.99 | 14.09 | 1.27 | 12.07 | 1.21 |
| CSI500 | Alpha101 (Adapted) | 5.06 | 0.43 | 0.21 | 11.53 | 0.86 | 14.71 | 1.13 | 13.70 | 1.08 | 13.76 | 1.20 |
| CSI500 | GPLearn | 6.04 | 0.43 | 0.44 | 10.30 | 0.62 | 13.38 | 1.00 | 12.44 | 1.17 | 9.86 | 0.95 |
| CSI500 | AlphaForge | 4.48 | 0.38 | 0.36 | 7.12 | 0.60 | 11.13 | 0.93 | 10.49 | 0.87 | 11.30 | 1.25 |
| CSI500 | AlphaAgent | 5.90 | 0.46 | 0.32 | 10.99 | 0.92 | 11.86 | 0.99 | 13.87 | 1.19 | 11.93 | 1.24 |
| CSI500 | FactorMiner (Ours) | 8.25 | 0.77 | 0.31 | 14.95 | 1.29 | 15.11 | 1.31 | 14.59 | 1.21 | 14.03 | 1.29 |
| CSI1000 | RF‡ | 2.88 | 0.30 | 0.13 | 7.48 | 0.49 | 12.28 | 1.00 | 13.72 | 1.24 | 9.54 | 1.03 |
| CSI1000 | Alpha101 (Classic) | 4.86 | 0.50 | 0.19 | 11.37 | 1.02 | 13.14 | 1.08 | 14.64 | 1.42 | 11.11 | 1.17 |
| CSI1000 | Alpha101 (Adapted) | 5.32 | 0.49 | 0.21 | 11.95 | 0.98 | 14.78 | 1.21 | 13.08 | 1.09 | 13.88 | 1.26 |
| CSI1000 | GPLearn | 5.86 | 0.48 | 0.44 | 11.10 | 0.73 | 13.66 | 1.11 | 12.87 | 1.23 | 9.53 | 0.96 |
| CSI1000 | AlphaForge | 4.64 | 0.42 | 0.35 | 7.60 | 0.71 | 11.25 | 1.02 | 10.42 | 0.93 | 12.20 | 1.34 |
| CSI1000 | AlphaAgent | 6.21 | 0.51 | 0.32 | 11.17 | 1.04 | 12.00 | 1.12 | 13.73 | 1.27 | 11.42 | 1.22 |
| CSI1000 | FactorMiner (Ours) | 7.78 | 0.76 | 0.30 | 14.62 | 1.37 | 14.76 | 1.39 | 14.25 | 1.25 | 12.42 | 1.30 |
| CSI300 | RF‡ | 1.94 | 0.15 | 0.13 | 5.46 | 0.30 | 9.49 | 0.61 | 9.98 | 0.63 | 5.55 | 0.46 |
| CSI300 | Alpha101 (Classic) | 3.44 | 0.26 | 0.18 | 8.55 | 0.57 | 10.31 | 0.65 | 11.84 | 0.85 | 9.70 | 0.74 |
| CSI300 | Alpha101 (Adapted) | 4.00 | 0.28 | 0.20 | 9.31 | 0.60 | 12.03 | 0.76 | 12.04 | 0.77 | 11.81 | 0.90 |
| CSI300 | GPLearn | 4.12 | 0.16 | 0.45 | 8.01 | 0.44 | 10.64 | 0.66 | 9.59 | 0.58 | 7.92 | 0.61 |
| CSI300 | AlphaForge | 3.53 | 0.25 | 0.36 | 5.19 | 0.35 | 8.54 | 0.57 | 6.79 | 0.43 | 10.89 | 0.91 |
| CSI300 | AlphaAgent | 4.69 | 0.30 | 0.33 | 8.83 | 0.59 | 9.65 | 0.65 | 12.26 | 0.86 | 9.66 | 0.84 |
| CSI300 | FactorMiner (Ours) | 7.46 | 0.38 | 0.31 | 12.49 | 0.88 | 12.66 | 0.88 | 11.23 | 0.82 | 11.33 | 0.94 |
| Crypto | RF‡ | 1.45 | 0.09 | 0.07 | 3.31 | 0.19 | 7.91 | 0.48 | 8.04 | 0.51 | 3.50 | 0.24 |
| Crypto | Alpha101 (Classic) | 2.11 | 0.14 | 0.14 | 5.91 | 0.41 | 8.05 | 0.53 | 9.63 | 0.54 | 5.61 | 0.37 |
| Crypto | Alpha101 (Adapted) | 2.40 | 0.15 | 0.15 | 6.09 | 0.41 | 9.21 | 0.62 | 8.45 | 0.48 | 4.51 | 0.30 |
| Crypto | GPLearn | 2.50 | 0.15 | 0.38 | 4.44 | 0.25 | 7.62 | 0.42 | 9.07 | 0.48 | 4.04 | 0.27 |
| Crypto | AlphaForge | 2.52 | 0.16 | 0.31 | 4.63 | 0.29 | 7.44 | 0.44 | 8.39 | 0.42 | 5.00 | 0.33 |
| Crypto | AlphaAgent | 2.86 | 0.17 | 0.27 | 7.94 | 0.34 | 8.40 | 0.36 | 7.48 | 0.41 | 2.35 | 0.17 |
| Crypto | FactorMiner (Ours) | 3.82 | 0.28 | 0.25 | 9.48 | 0.61 | 9.48 | 0.62 | 8.98 | 0.51 | 6.82 | 0.47 |

注：IC 按每个 bar 计算为 Spearman 秩相关，并汇总为 |E[𝐼𝐶𝑡 ]|。Las.=Lasso，XGB.=XGBoost。‡ RF=Random Formula Exploration。

#### 4.2.2 跨异构市场的稳健性

跨市场评估揭示了所发现因子的泛化能力。尽管加密货币市场代表着根本不同的微观结构（7×24 交易、无价格涨跌幅限制），且相比 A 股 [19] 具有其独特的风险因子结构，FactorMiner 在 Crypto 上仍保持有竞争力的表现：单因子库评估中 IC/ICIR 为 3.82%/0.28，在简单的 IC 加权组合下为 9.48%/0.62（见表 1）。这一稳健性表明 FactorMiner 捕捉到了跨资产类别不变的基本价量动态（如流动性受限的反转、波动率聚集），而非过拟合到单一市场的特异性。

为解释为何单一准入阈值未必适用于所有市场，我们用截面离散度（cross-sectional dispersion，CSD）[6]——即单个 bar 内跨资产的收益离散度——以及收益同步性（return synchronicity，SYN）[22]——即资产与市场总量共同变动的程度——来刻画每个市场（表 2）。A 股股票池表现出更大的截面离散度，而 Crypto 呈现正的 SYN，说明其存在更强的全市场共同变动。这种异质性促使自适应准入：在离散度更低、同步性更高的市场（如 Crypto）中，较低的截面 IC 阈值与时序导向的目标更有信息量；而 A 股更丰富的截面离散度使严格的截面准入更有意义。

表2：以半年度窗口衡量的市场异质性——截面离散度（CSD，‰）与收益同步性（SYN）。

| 指标 | 期间 | CSI500 | CSI1000 | CSI300 | Crypto |
| --- | --- | --- | --- | --- | --- |
| CSD (‰) | 2024H1 | 5.58 | 5.00 | 3.50 | 2.74 |
| CSD (‰) | 2024H2 | 5.05 | 10.56 | 6.44 | 2.64 |
| CSD (‰) | 2025H1 | 3.87 | 4.73 | 3.09 | 2.39 |
| CSD (‰) | 2025H2 | 4.26 | 4.41 | 3.64 | 2.48 |
| CSD (‰) | Avg | 4.69 | 6.18 | 4.17 | 2.56 |
| SYN | 2024H1 | -1.04 | -0.80 | -1.41 | 0.47 |
| SYN | 2024H2 | -0.41 | -0.49 | -0.48 | 0.47 |
| SYN | 2025H1 | -1.31 | -1.28 | -1.40 | 0.80 |
| SYN | 2025H2 | -2.01 | -2.01 | -2.14 | 0.90 |
| SYN | Avg | -1.19 | -1.14 | -1.36 | 0.66 |

#### 4.2.3 集成与学习式选择

除单个因子之外，我们通过两类方法评估挖掘所得因子库对下游投资组合构建的价值：简单因子组合（等权与 IC 加权）以及学习式选择模型（Lasso 与 XGBoost，在 2024 年上训练、在 2025 年上评估）。在大多数基线上，学习式模型相对简单集成带来明显提升，这与候选因子库中存在异质但部分冗余的信号相一致。然而对 FactorMiner 而言，学习式选择带来的额外收益有限，在某些数据集上甚至略为负（例如 CSI500：EW 与 ICW 的 ICIR = 1.29/1.31，而 Lasso 与 XGBoost 为 1.21/1.29），这表明在 Train’24/Test’25 协议下，简单集成信号已经捕捉到大部分可利用的预测能力（见表 1）。

#### 4.2.4 额外稳健性检验

我们进一步与直接把 10 分钟市场面板映射为预测分数的端到端预测基线进行比较：PatchTST [25]、Chronos-2 [3] 与 LightGBM [15]。这些神经或树模型提供了非平凡的信号，但其准确性与稳定性不及可解释的公式化因子库。如表 3 所示，FactorMiner 在所评估市场上取得强于这些端到端基线的 IC/ICIR。差距在 A 股最大，LightGBM 在 CSI500 上达到 5.53%/0.51，而 FactorMiner 达到 8.25%/0.77。

表3：与端到端预测基线在 2025 测试期上的对比。IC 以 % 计；越高越好。

| 市场 | PatchTST IC (%) | PatchTST ICIR | Chronos-2 IC (%) | Chronos-2 ICIR | LightGBM IC (%) | LightGBM ICIR | FactorMiner IC (%) | FactorMiner ICIR |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CSI500 | 2.21 | 0.19 | 4.52 | 0.37 | 5.53 | 0.51 | 8.25 | 0.77 |
| CSI1000 | 1.84 | 0.20 | 3.36 | 0.26 | 4.85 | 0.45 | 7.78 | 0.76 |
| CSI300 | 1.80 | 0.15 | 3.01 | 0.19 | 4.66 | 0.34 | 7.46 | 0.38 |
| Crypto | 1.58 | 0.06 | 2.62 | 0.16 | 2.88 | 0.13 | 3.82 | 0.28 |

为检验主要 2025 评估窗口之外的时间持续性，我们还在 CSI500 上对完整的 110 因子库评估到 2026-Q1 的近几个月。表 4 显示，原始因子库与 XGBoost 选出的复合信号在 2026-01 至 2026-03 期间仍保持预测能力，这支持了“所挖掘因子能够泛化到原始训练年份之外，而不只是拟合 2024 年特有模式”的观点。这些结果凸显了因子时效性与长期稳定性之间的一种实际权衡：市场会演化，已发表的异常在为人所知并被套利之后可能逐渐消失 [20]，而日内微观结构信号的半衰期可能更短，因此在当前市场状态下取得的证据尤其重要 [1]。

表4：CSI500 上完整因子库的近期稳健性。

| 期间 | Lib. IC (%) | Lib. ICIR | XGB IC (%) | XGB ICIR |
| --- | --- | --- | --- | --- |
| 2025-10 | 5.52 | 0.49 | 13.42 | 1.16 |
| 2025-11 | 6.74 | 0.65 | 15.83 | 1.46 |
| 2025-12 | 6.83 | 0.68 | 16.16 | 1.55 |
| 2026-01 | 4.78 | 0.46 | 12.56 | 1.03 |
| 2026-02 | 6.23 | 0.64 | 15.23 | 1.38 |
| 2026-03 | 5.52 | 0.51 | 14.96 | 1.17 |

学习式选择器也是有用的诊断工具，可用来理解因子库的哪些部分带来非线性的边际价值。表 5 显示，XGBoost 的重要性并不集中在单一的 VWAP 式锚点上：排名靠前的因子横跨 VWAP 偏离、现代化的 Alpha101 公式、动量、状态切换、价格区间交互、发散、高阶矩、基于中位数的变换以及金额效率信号。这种广泛的支撑有助于解释为何树模型选择能够改善若干较弱的因子库，而 FactorMiner 自身的简单集成在学习之前就已具有竞争力，因为准入的因子库在学习前就更加多样。

表5：完整 FactorMiner 因子库上 XGBoost 的特征重要性（前 20 个因子）。

| 排名 | ID | 因子 | 重要性 | 类别 |
| --- | --- | --- | --- | --- |
| 1 | 006 | VWAP Deviation | 6.04 | VWAP |
| 2 | 061 | Alpha101-12 Modern | 4.06 | Classic |
| 3 | 023 | Norm.-Momentum TsRank | 3.59 | Momentum |
| 4 | 068 | Skewness Regime PV-Div | 3.55 | Regime |
| 5 | 028 | Close-Low × Volume | 3.03 | Price range |
| 6 | 070 | Price-Pos. Vol. Interact. | 2.27 | Interaction |
| 7 | 057 | TsRank PV Divergence | 2.26 | Divergence |
| 8 | 029 | High-Close × Volume | 2.15 | Price range |
| 9 | 018 | Range-Position Vol. Regime | 1.62 | Range |
| 10 | 045 | Kurtosis-Regime Range | 1.57 | Higher moment |
| 11 | 048 | Vol-Price Rank Div. | 1.47 | Divergence |
| 12 | 104 | Median LogSwap | 1.46 | Median |
| 13 | 053 | Alpha101-1-V | 1.44 | Classic |
| 14 | 101 | Median Returns Switch | 1.41 | Median |
| 15 | 004 | High-Vol Rel. Weakness | 1.34 | Volume |
| 16 | 055 | Skew Open-Close Prod. | 1.24 | Distribution |
| 17 | 019 | VWAP-Gap Regime Range | 1.20 | VWAP |
| 18 | 092 | Amt Efficiency EMA | 1.16 | Efficiency |
| 19 | 073 | Amt Velocity Regime | 1.16 | Efficiency |
| 20 | 043 | Skewed Volume Momentum | 1.11 | Distribution |

### 4.3 经验记忆的影响

为隔离经验记忆（M）的贡献，我们开展了一项消融研究，将 FactorMiner 与禁用了算子 𝐹、𝐸、𝑅 的“No Memory”变体进行比较，使系统退化为标准的基于 LLM 的演化（汇总见图 3）。由于该实验被设计为受控的机制消融，我们采用相对宽松的筛选阈值以保证足够的比较样本（IC 阈值 |IC| > 0.02；冗余阈值 𝜃 = 0.85）。图 3 突出显示了记忆引导的影响：

- 精准导航（高产出）：Have Memory 变体生成 96 个高质量候选（产出率 60.0%），而 No Memory 基线只生成 32 个（产出率 20.0%）。这表明检索算子有效地刻画了搜索空间，使智能体能够把探索引向预期产出更高的区域，而不是随机探索。

- 激进过滤（高多样性）：尽管生成了 3.0 倍的有效信号，Have Memory 变体因冗余而主动拒绝了更高比例的信号（55.2% 对 43.8%）。这证实了演化算子 𝐸 起到了战略过滤器的作用，优先追求独特信号的发现，而不仅仅是数量。

图3：Have Memory 与 No Memory 之间的消融对比。通过 IC 阈值的高质量候选。柱状图报告计数以及相应的产出率与拒绝率。（原文第9页）

除汇总计数之外，检索到的记忆还暴露出可复用的搜索先验，而非不透明的提示。表 6 汇总了那些反复带来准入、低冗余因子的代表性方向。这些先验让搜索更少试错：智能体被引向诸如高阶矩状态、金额效率与趋势回归自适应等机制族，而后续的记忆更新则可以抑制那些坍缩回拥挤 VWAP 偏离簇的方向。

表6：从经验记忆中蒸馏出的推荐挖掘方向。

| 模式 | 搜索先验 | 产出 |
| --- | --- | --- |
| Higher moments（高阶矩） | 用 Skew/Kurt 作为反转逻辑的状态条件 | High |
| PV corr. interaction（量价相关交互） | 把量价相关与金额或趋势算子结合 | High |
| Robust efficiency（稳健效率） | 用中位数或稳健统计量平滑收益/金额效率 | High |
| Smoothed efficiency rank（平滑效率排名） | 在截面排序之前施加 EMA/WMA | High |
| Trend regression（趋势回归） | 依据 Rsquare 可靠性在 Slope 与 Resi 之间切换 | High |
| Extreme regimes（极端状态） | 用逻辑 Or 把价格/成交量极值作为状态触发器 | High |
| Kurtosis regime（峰度状态） | 在肥尾环境下调整反转窗口 | High |
| Amt-efficiency interaction（金额效率交互） | 把金额效率排名与 Skew/Kurt 特征交叉 | Med. |

### 4.4 挖掘效率分析

为展示因子挖掘技能的实际优势，我们对三种执行后端进行了严格基准测试：(1) 标准 Python (Pandas)，(2) 面向高效 CPU 执行的 C 编译（Bottleneck），以及 (3) 面向大规模并行的 GPU 加速。这种多后端支持使智能体保持轻量，同时通过按需加速达到工业级效率。

结果。图 4 报告了 CSI500 数据集（12,610 × 500）上的算子级与因子级基准，测量不含 I/O 的纯计算时间。在算子级，GPU 后端相对 Pandas 实现 8–59 倍加速，相对优化的 C 后端实现 2–13 倍加速。C 后端适合轻量的纯 CPU 运行，而 GPU 后端对重复的大批量评估起决定性作用。对于端到端因子评估（图 4，因子级），排序密集型因子（F43、F48、F53）获得 23–27 倍的显著加速，即使是高度优化的 C 实现平均也比 GPU 后端慢 5.4 倍（1,092 ms 对 202 ms）。通过把这些密集原语下放到 GPU/C 并对批量评估做并行化，FactorMiner 使大规模迭代发现在普通硬件上可行：评估 1,000 个候选因子约需 6 分钟，而用 Pandas 约需 70 分钟，从而使迭代式的“生成–评估–精炼”循环保持实用。

图4：Python、优化 CPU (C) 与 GPU 后端下的算子级与因子级计算时间（ms，对数尺度）；越低越好。GPU 后端带来稳定的数量级收益。（原文第9页）

## 5 讨论

高频市场可以被视为一个数据丰富的复杂自适应系统，而每个公式化因子都可以被视为关于市场微观结构的一个显式、可证伪的假设。除预测性能之外，FactorMiner 还产出 110 个可解释的高频 alpha 因子与一套标准化评估协议，用于对市场微观结构进行可复现的、假设驱动的分析。

经验记忆即持续学习。我们的结果证实，记忆引导、基于技能的智能体能够在保持可可解释性的同时，把神经符号程序综合扩展到更大规模。经验记忆充当跨会话积累的机构性知识，从而实现元学习：系统学到的不只是单个因子，而是如何更有效地搜索。关键洞见包括：成功模式（通过 Skew/Kurt 实现的高阶矩状态、通过 Rsquare/Slope/Resi 实现的趋势回归自适应、金额效率交互），它们产出高 IC、低相关的因子；失败模式（VWAP 偏离变体、标准化收益、简单 Delta 反转），它们与既有因子相关；以及相关性红海——在没有记忆引导的情况下，随着因子库增长，新的正交因子越来越难以找到。

## 6 结论

FactorMiner 通过把模块化挖掘技能与经验记忆相结合，提供了一个面向可解释高频 alpha 发现的轻量级自进化智能体框架。由此得到的 110 因子库与标准化协议构成了一件可复现的成果，支持对市场微观结构进行假设检验、机理审视与跨市场迁移研究。未来工作将纳入考虑交易成本的回测、扩展到更广泛的资产与频率，并为非平稳市场开发在线记忆更新。

## 7 局限性与伦理考量

尽管我们包含了与端到端模型的比较，但这些基线并未被穷尽调参，且其可解释性仍不及公式化因子。我们的流水线同样以预测 IC、ICIR、冗余与组合诊断为目标，考虑交易成本的部署留待未来工作。所发现的因子可能被滥用于投机或操纵性策略；部署应当遵循合规与风控要求。

## 致谢

本工作部分受深圳市泛在数据赋能重点实验室基金（编号 ZDSYS20220527171406015）资助，并部分受清华大学深圳国际研究生院—深圳鹏瑞基金会讲席教授计划资助。

## 参考文献

参考文献从略，见原文。

## 附录 A 算子库与准入标准

每个符号因子 𝛼 ∈ P 都是一棵表达式树，由原始特征引用（$open、$high、$low、$close、$volume、$amt、$vwap、$returns）与一个精选的 60 多个带类型算子的库构建而成，这些算子按表 7 所示的类别组织；为便于阅读，表 7 只列出代表性算子，而完整的 FactorMiner 注册表包含 60 多个带类型的算子。

表7：因子挖掘技能中的算子类别（代表性算子；共 60 多个）。

| 类别 | 代表性算子 |
| --- | --- |
| Arithmetic（算术） | Add, Sub, Mul, Div, Neg, Abs, Log, SignedPower, Power, Inv, Sqrt, Square, Exp, Tanh |
| Statistical（统计） | Mean, Std, Var, Skew, Kurt, Med, Sum, Product |
| Time-series（时序） | Delay, Delta, TsRank, TsMax, TsMin, TsArgMax, TsArgMin, TsDecay |
| Cross-sectional（截面） | CsRank, Scale |
| Smoothing（平滑） | SMA, EMA, WMA |
| Regression（回归） | Slope, Rsquare, Resi |
| Logical（逻辑） | IfElse, Greater, Less, GreaterEqual, LessEqual, And, Or, Eq, Ne |

准入与替换。符号因子 𝛼 被准入到因子库 L 的条件是满足

```
IC(𝛼) ≥ 𝜏IC   ∧   max𝑔∈L |𝜌 (𝛼, 𝑔 )| < 𝜃,                    (10)
```

其中 𝜏IC 与 𝜃 分别是 IC 阈值与相关性阈值（除非另有说明，A 股挖掘的默认值为 𝜏IC = 0.04、𝜃 = 0.5）。我们进一步为那些原本会因相关性而被拒绝的高质量候选引入因子替换机制：如果新因子 𝛼 满足

```
IC(𝛼) ≥ 0.10 ∧ IC(𝛼) ≥ 1.3 IC(𝑔 ) ∧ |{𝑔 ∈ L : 𝜌 (𝛼, 𝑔 ) > 𝜃 }| = 1,
                                                        (11)
```

则 𝛼 替换掉唯一那个相关的因子 𝑔 ，使因子库在保持多样性的同时向更高质量演化。

可复现性。符号提议由 Gemini 3.0 Flash 生成，全程不进行任何权重更新。因子评估使用 GPU/C 加速算子（NumPy/CuPy）以及一个 40 worker 的多进程池；代表性算子的运行时间见图 4。原本为日频的 Alpha101 基线通过为每个公式生成至多 10 个窗口参数变体并保留最佳配置，被改造为 10 分钟 bar 版本。

## 附录 B 端到端信号相关性

我们检验端到端基线（PatchTST、Chronos-2、LightGBM）是否与已发布的 110 因子库冗余。表 8 显示重叠很小：平均绝对相关低于 0.04，单个因子的最大相关至多 0.23。表 9 显示三者信号之间的成对相关同样不大。这些模型在预测性能上并没有支配公式化因子库，但它们的输出可能为未来的混合系统携带互补信息。

表8：端到端模型信号与 110 因子库之间的相关性。

| 模型 | Avg \|ρ\| | Max \|ρ\| | 最近邻因子 | 第 2 | 第 3 |
| --- | --- | --- | --- | --- | --- |
| PatchTST | 0.0365 | 0.18 | 002 EMA Deviation | 108 | 006 |
| Chronos-2 | 0.0399 | 0.23 | 062 Amount-stability adj. returns | 002 | 081 |
| LightGBM | 0.0146 | 0.08 | 062 Amount-stability adj. returns | 006 | 084 |

表9：端到端信号之间的成对相关。

| 模型 | Chronos-2 | LightGBM | PatchTST |
| --- | --- | --- | --- |
| Chronos-2 | 1.000 | 0.043 | 0.171 |
| LightGBM | 0.043 | 1.000 | 0.224 |
| PatchTST | 0.171 | 0.224 | 1.000 |

## 附录 C 经验记忆：禁止方向

除成功模板之外，记忆还蒸馏负性知识：那些反复产出与既有因子库高度相关的候选的结构性方向。表 10 汇总了主要的禁止方向及其与准入因子的典型相关；记录它们可以防止智能体浪费预算去重新发现已知信号。

表10：禁止的挖掘方向（高相关风险）。

| 方向 | 相关因子 | \|ρ\| |
| --- | --- | --- |
| Standardized Returns/Amount（标准化收益/金额） | 006, 008, 009 | >0.6 |
| VWAP Deviation variants（VWAP 偏离变体） | 006, 009, 012, 013, 016 | >0.5 |
| Mean Reversion / Price Deviation（均值回归 / 价格偏离） | 001, 002 | >0.5 |
| Simple Delta Reversal（简单 Delta 反转） | 023, 024 | >0.5 |
| Close-Position Location（收盘价位置） | 028, 044 | 0.87+ |
| Volatility + Price Position Branch（波动率 + 价格位置分支） | 046, 064 | >0.6 |
| High R2 Trend Following（高 R2 趋势跟随） | 081, 083 | >0.6 |
| Rsquare Weighted Momentum（Rsquare 加权动量） | 002, 023 | >0.7 |
| WMA/EMA Smoothed Efficiency（WMA/EMA 平滑效率） | 092 | >0.9 |

VWAP 簇（因子 006 及其变体）是最密集的相关区域：按波动率或成交量归一化的接近 VWAP 的信号几乎总是与它相关超过 0.5。随着因子库增长到 70 个因子以上，即使是高 IC 的候选也越来越频繁地与既有因子发生碰撞，这表明“容易的”信号空间已基本被耗尽。

## 附录 D 完整因子库（110 个因子）

下表给出完整因子库的全部 110 个因子公式（按 ID排列，公式原样保留）。

```
ID     Formula
  001   Neg(CsRank(Div(Sub($close, Min($close, 48)), Add(Sub(Max($close, 48), Min(
         $close, 48)), 1e-8))))
  002   Neg(Div(Sub($close, EMA($close, 10)), EMA($close, 10)))
  003   Sub(CsRank(Delta($volume, 1)), CsRank(Div(Sub($close, $vwap), $vwap)))
  004   Mul(CsRank(Div($volume, Mean($volume, 24))), CsRank(Neg($returns)))
  005   Neg(Mul(TsRank(Div(Sub($close, TsMin($close, 12)), Add(Sub(TsMax($close,
         12), TsMin($close, 12)), 1e-6)), 12), CsRank(Abs(Cov($returns, $volume, 12)
         ))))
  006   Neg(Div(Sub($close, $vwap), $vwap))
  007   Neg(Sub(CsRank(Div(Sub($close, $low), Add(Sub($high, $low), 0.0001))),
         CsRank(Delta(EMA($volume, 5), 5))))
  008   Neg(Mul(CsRank(Div($returns, Add(Std($returns, 12), 0.0001))), CsRank(Div(
         $volume, Mean($volume, 12)))))
  009   Neg(Mul(CsRank($returns), CsRank(Std($returns, 12))))
  010   Neg(CsRank(Sub(CsRank(Div($close, Delay($close, 5))), CsRank(Div($volume,
         Delay($volume, 5))))))
  011   Neg(Sub(CsRank(Delta($close, 6)), CsRank(Delta($vwap, 6))))
  012   Mul(CsRank(Neg(Div(Sub($close, $vwap), $vwap))), CsRank(Div($volume, EMA(
         $volume, 12))))
  013   Mul(CsRank(Neg(Div(Sub($close, $vwap), $vwap))), Sub(1, CsRank($volume)))
  014   Mul(Add(Mul(CsRank(Neg(Div(Sub($close, $vwap), $vwap))), 0.6), Mul(CsRank(
         Delta(Neg(Div(Sub($close, $vwap), $vwap)), 3)), 0.4)), CsRank(Delta(Div(
         Mean(Div(Abs($returns), Add($volume, 1)), 24), Add(Div(Abs($returns), Add(
         $volume, 1)), 1e-6)), 3)))
015   Mul(CsRank(Neg(Delta($returns, 3))), Mul(Sub(1, CsRank(Std($returns, 12))),
       CsRank(Std($returns, 12))))
016   Neg(Mul(CsRank(Delta(Div(Sub($close, $vwap), $vwap), 3)), CsRank(Div(
       $volume, EMA($volume, 12)))))
017   Neg(Mul(TsRank(Delta(Div(Sub($close, $vwap), $vwap), 3), 12), TsRank(Std(
       $returns, 12), 12)))
018   Neg(Mul(TsRank(Div(Sub($close, TsMin($close, 12)), Add(Sub(TsMax($close,
       12), TsMin($close, 12)), 1e-6)), 12), TsRank(Div($volume, EMA($volume, 12))
       , 12)))
019   IfElse(Greater(Abs(Div(Sub($close, $vwap), $vwap)), 0.01), Neg(CsRank(Sub(
       $close, TsMax($close, 12)))), Neg(CsRank(Sub($close, TsMin($close, 12)))))
020   TsRank(Sub(CsRank(Delta($volume, 3)), CsRank(Delta($close, 3))), 18)
021   Neg(Mul(TsRank(Delta(Div($volume, EMA($volume, 12)), 3), 12), TsRank(Delta(
       Div(Sub($close, $vwap), $vwap), 3), 12)))
022   Neg(CsRank(Div(Sub(Min2($open, $close), $low), Add(Sub($high, $low),
       0.0001))))
023   Neg(TsRank(Div(Delta($close, 3), Mean(Abs(Delta($close, 3)), 12)), 12))
024   Sub(TsRank(Delta($open, 6), 12), TsRank(Delta($close, 6), 12))
025   Sub(TsRank(Delta($open, 9), 18), TsRank(Delta($close, 9), 18))
026   Neg(Mul(TsRank(Cov(TsRank($close, 18), TsRank($volume, 18), 10), 18),
       TsRank(Div(Sub($close, $low), Sub($high, $low)), 18)))
027   Neg(Mul(TsRank(Cov(TsRank($open, 12), TsRank($volume, 12), 5), 12), TsRank(
       Div(Sub($close, $low), Sub($high, $low)), 12)))
028   Neg(Mul(Sub($close, $low), Div($volume, Mean($volume, 12))))
029   Mul(Sub($high, $close), Div($volume, Mean($volume, 12)))
030   Mul(Delta(Sub($high, $close), 3), Div($volume, Mean($volume, 12)))
031   IfElse(Greater(Delta($close, 1), 0), Neg(TsRank(Delta($close, 3), 12)),
       TsRank(Delta($close, 3), 12))
032   Neg(TsRank(Sub(CsRank(Delta($returns, 2)), CsRank(Delta($volume, 2))), 12))
033   Neg(Mul(TsRank(Corr(TsRank(Div($volume, Mean($volume, 24)), 12), TsRank(
       Sub($high, $low), 12), 12), 24), CsRank(Delta($close, 2))))
034   IfElse(Greater(Delta($close, 2), 0), Neg(TsRank(Delta($close, 5), 15)),
       TsRank(Delta($close, 5), 15))
035   Neg(Mul(TsRank(Delta(Sub($high, $low), 2), 12), CsRank(Delta($close, 2))))
036   IfElse(Greater(Std($returns, 12), Mean(Std($returns, 12), 48)), Neg(CsRank(
       Div(Sub(Min2($open, $close), $low), Add(Sub($high, $low), 0.0001)))), Neg(
       CsRank($returns)))
037   Neg(TsRank(Mul(CsRank(Delta($close, 3)), CsRank(Delta($volume, 3))), 18))
038   IfElse(Greater(Std($returns, 12), Mean(Std($returns, 12), 48)), Neg(TsRank(
       Sub(CsRank(Delta($volume, 3)), CsRank(Delta($close, 3))), 18)), Neg(
       TsRank(Div(Sub($close, $vwap), Add(Std($returns, 24), 0.0001)), 12)))
039   Neg(Mul(CsRank(Delta($close, 5)), CsRank(Kurt($returns, 24))))
040   Neg(Mul(CsRank(Div(Sub($close, $low), Add(Sub($high, $low), 0.0001))),
       CsRank(Skew($returns, 24))))
041   Mul(CsRank(Div(Sub($high, $close), Add(Sub($high, $low), 1e-8))), CsRank(
       Neg(Skew($returns, 24))))
042   IfElse(Greater(Abs(Skew($returns, 24)), 1.0), Neg(CsRank($returns)), Neg(
       CsRank(Skew($returns, 24))))
043   Neg(TsRank(Mul(CsRank(Skew($volume, 24)), CsRank(Delta($close, 3))), 12))
044   Neg(Mul(CsRank(Kurt($volume, 24)), CsRank(Div(Sub($close, $low), Add(Sub(
       $high, $low), 0.0001)))))
045   IfElse(Greater(Kurt($returns, 24), 3.0), Neg(CsRank(Div(Sub($high, $close),
       Add(Sub($high, $low), 0.0001)))), Neg(CsRank(Div(Sub($close, $low), Add(
       Sub($high, $low), 0.0001)))))
046   IfElse(Greater(Std($returns, 12), Mean(Std($returns, 12), 48)), Neg(CsRank(
       Delta($close, 3))), Neg(CsRank(Div(Sub($close, $low), Add(Sub($high, $low),
       0.0001)))))
047   Neg(Mul(CsRank(TsRank(Delta(Log(Add($volume, 1)), 3), 6)), CsRank(Div(
       Delta($close, 6), $close))))
048   TsRank(Sub(CsRank(Std($returns, 12)), CsRank(Delta($close, 6))), 18)
049   IfElse(Greater(Skew($returns, 24), 0.5), CsRank(Delta($volume, 3)), Neg(
       CsRank(Std($returns, 12))))
050   IfElse(Greater(Skew($returns, 24), 0.5), Neg(CsRank(Div(Sub($close, $low),
       Add(Sub($high, $low), 1e-6)))), Neg(CsRank(Delta($close, 6))))
051   IfElse(Less(Skew($returns, 24), -0.5), CsRank(Delta($close, 5)), Neg(
       CsRank(Std($returns, 12))))
052   IfElse(Less(Skew($returns, 24), -0.5), Neg(TsRank($returns, 12)), Neg(
       CsRank(Delta($close, 6))))
053   Neg(CsRank(TsArgMax(SignedPower(IfElse(Less($returns, 0), Std($returns, 20)
       , $close), 2), 5)))
054   IfElse(Greater($amt, Mean($amt, 24)), CsRank(Delta($close, 3)), Neg(CsRank(
       Div(Sub($close, $vwap), $vwap))))
055   IfElse(Greater(Corr($close, $volume, 12), 0.5), Neg(CsRank($returns)),
       CsRank(Delta($volume, 3)))
056   IfElse(Greater(Kurt($returns, 24), 3.0), Neg(CsRank(Div($amt, Add($volume,
       1e-6)))), Neg(CsRank(Delta($close, 3))))
057   Neg(Sub(TsRank(Delta($close, 6), 24), TsRank(Delta($volume, 6), 24)))
058   IfElse(Greater($amt, Mean($amt, 48)), Neg(CsRank(Div($amt, Add($volume,
       1e-6)))), Neg(TsRank($returns, 12)))
059   IfElse(Greater(Std($returns, 12), Mean(Std($returns, 12), 24)), Neg(CsRank(
       Skew($amt, 12))), Neg(CsRank(Delta($close, 3))))
060   IfElse(Greater(Div($amt, Mean($amt, 24)), 1.2), Sub(CsRank($close), CsRank(
       $volume)), Neg(CsRank(Delta($close, 3))))
061   Neg(Mul(TsRank(Delta($volume, 1), 12), TsRank(Delta($close, 1), 12)))
062   Neg(Div(CsRank($returns), Add(Std($amt, 12), 1e-6)))
063   Neg(TsRank(Add(Add(CsRank(Delta($returns, 3)), CsRank(Delta($amt, 3))),
       CsRank(Kurt($volume, 12))), 12))
064   IfElse(Less(Corr($close, $volume, 12), -0.5), CsRank($returns), Neg(CsRank(
       Delta($close, 3))))
065   IfElse(Greater(Std($returns, 12), Mean(Std($returns, 12), 48)), Neg(CsRank(
       Delta($amt, 6))), Neg(CsRank(Delta($close, 1))))
  066   IfElse(Greater(Kurt($volume, 24), 3), Neg(CsRank(Delta($amt, 3))), Neg(
  CsRank($returns)))
  067   Neg(Mul(CsRank(Div(Sub($low, $close), Add(Sub($low, $high), 1e-6))),
  CsRank(Delta($amt, 6))))
  068   Neg(IfElse(Less(Skew($returns, 24), -0.5), Neg(Sub(TsRank($close, 12),
  TsRank($volume, 12))), CsRank(Delta($returns, 3))))
  069   Neg(IfElse(Greater(Kurt($returns, 12), 3.0), Neg(CsRank(Std($returns, 6))),
  CsRank(Delta($returns, 3))))
  070   Neg(Mul(CsRank(Div(Sub($close, $low), Add(Sub($high, $low), 0.0001))),
  TsRank(Std($returns, 24), 24)))
  071   Mul(CsRank(Div(Sub($high, $close), Add(Sub($high, $low), 1e-6))), TsRank(
  Std($volume, 12), 12))
  072   IfElse(Greater(Kurt($volume, 24), 3.0), Neg(Corr($close, $volume, 12)),
  Neg(TsRank($returns, 24)))
  073   IfElse(Greater($amt, EMA($amt, 12)), Neg(TsRank(Delta($volume, 3), 12)),
  Neg(CsRank($returns)))
  074   Neg(Mul(CsRank(Div(Sub($close, $low), Add(Sub($high, $low), 1e-6))),
  TsRank(Skew($volume, 24), 12)))
  075   Neg(Mul(CsRank(Div($returns, $amt)), TsRank(Std($volume, 20), 20)))
  076   Neg(IfElse(Greater(Div($amt, Mean($amt, 24)), 2.0), Neg(Delta($close, 1)),
  SMA($returns, 6)))
  077   Neg(Mul(TsRank(Std(Div($volume, Mean($volume, 24)), 24), 24), TsRank(
  $returns, 12)))
  078   Neg(Mul(CsRank(Div($returns, $amt)), TsRank(Kurt($volume, 20), 20)))
  079   IfElse(Greater(Std($returns, 12), EMA(Std($returns, 12), 48)), Neg(Div(Sub(
  $close, $low), Add(Sub($high, $low), 1e-6))), Div(Sub($high, $close), Add(
  Sub($high, $low), 1e-6)))
  080   IfElse(Greater(Rsquare($close, 24), 0.7), Neg(CsRank(Slope($close, 24))),
  Neg(CsRank(Resi($close, 12))))
  081   IfElse(And(Greater(Rsquare($close, 24), 0.6), Greater(Std($returns, 12),
  Mean(Std($returns, 12), 48))), Slope($close, 12), Neg(SMA($returns, 6)))
  082   IfElse(Or(Greater(Div(Sub($high, Max2($open, $close)), Add(Sub($high, $low)
  , 1e-6)), 0.6), Greater(Div(Sub(Min2($open, $close), $low), Add(Sub($high,
  $low), 1e-6)), 0.6)), Slope($close, 12), Neg(SMA($returns, 6)))
  083   IfElse(And(Greater(Rsquare($close, 24), 0.5), Less(Std($returns, 12), Mean(
  Std($returns, 12), 48))), Slope($close, 12), Neg($returns))
  084   IfElse(Eq(Sign(Delta(Std($returns, 12), 1)), Sign(Delta($returns, 1))),
  Neg(Resi($close, 12)), Neg(Slope($close, 24)))
  085   Neg(Mul(CsRank(Rsquare($close, 24)), CsRank(Resi($close, 12))))
  086   IfElse(Eq(Sign(Delta(Resi($close, 12), 1)), Sign(Resi($close, 12))), Neg(
  Resi($close, 6)), Neg(Slope($close, 12)))
  087   IfElse(Greater(Kurt($returns, 24), 3.0), Neg(Resi($close, 6)), Neg(Resi(
  $close, 24)))
  088   Neg(Mul(CsRank(Div($returns, Add($amt, 1e-6))), TsRank(Skew($returns, 24),
  24)))
  089   IfElse(Or(Greater($volume, Mean($volume, 24)), Greater(Abs($returns), Std(
  $returns, 24))), Neg(Resi($close, 6)), Neg(Slope($close, 12)))
  090   IfElse(Greater(Rsquare($close, 24), 0.75), Neg(Slope($close, 12)), Neg(
  TsRank($returns, 12)))
  091   Neg(Mul(TsRank(Div($returns, Add($amt, 1e-6)), 24), TsRank(Kurt($returns,
  24), 24)))
  092   Neg(CsRank(EMA(Div($returns, Add($amt, 1e-6)), 6)))
  093   Neg(TsRank(Delta(Div($returns, Add($amt, 1e-6)), 3), 24))
  094   IfElse(And(Greater(Std($returns, 12), Mean(Std($returns, 12), 60)), Less(
  Kurt($returns, 24), 2)), Neg(Delta($close, 3)), Neg(TsRank($returns, 24)))
  095   IfElse(Or(Greater(Abs(Skew($returns, 24)), 1.5), Greater(Kurt($returns, 24)
  , 4.0)), Neg(Resi($close, 6)), Neg(TsRank($returns, 24)))
  096   Neg(Mul(TsRank(WMA(Div($returns, Add($amt, 1e-6)), 6), 24), TsRank(Corr(
  $close, $volume, 24), 24)))
  097   Neg(CsRank(Med(Div($returns, Add($amt, 1e-6)), 6)))
  098   Neg(CsRank(Delta(WMA(Div($returns, Add($amt, 1e-6)), 6), 3)))
  099   Neg(Sub(EMA(Div($returns, Add($amt, 1e-6)), 6), EMA(Div($returns, Add($amt,
  1e-6)), 24)))
  100   Neg(Resi(Delta(Resi($close, 24), 3), 12))
  101   Neg(IfElse(Greater(Abs(Skew($returns, 24)), 1.0), TsRank(Div(Sub($returns,
  Med($returns, 24)), Add(Std($returns, 24), 1e-6)), 24), CsRank(Resi($close,
  12))))
  102   IfElse(Greater(Skew($high, 24), 0), TsRank(Log(Div($high, Add($close, 1e-6)
  )), 24), CsRank(Resi($low, 24)))
  103   Neg(IfElse(Greater(Skew($open, 24), 0), TsRank(Resi($open, 24), 24),
  CsRank(SignedPower($returns, 0.5))))
  104   Neg(IfElse(Greater(Med($returns, 24), 0), TsRank(Log(Div($close, Add($open,
  1e-6))), 24), CsRank(Sign(Resi($close, 24)))))
  105   Neg(IfElse(Greater(Skew($returns,24),0.4), CsRank(Sign(Resi($open,24))),
  TsRank(SignedPower($returns,0.6),24)))
  106   Neg(IfElse(Greater(Std($volume,24),Mean(Std($volume,24),48)), CsRank(Div(
  $amt, Add($volume,1e-6))), TsRank(Div($returns, Add(Std($returns,24),1e-6)
  ),24)))
  107   IfElse(Greater(Std($returns, 12), Med(Std($returns, 12), 48)), Mul(CsRank(
  Neg(Div(Sub($close, $vwap), $vwap))), CsRank(Div($volume, EMA($volume, 12))
  )), Neg(TsRank(Div(Sub($close, $vwap), $vwap), 24)))
  108   Neg(IfElse(Less(Skew($returns, 24), -0.3), Mul(CsRank(Neg(Div(Sub($close,
  $vwap), $vwap))), CsRank(Div($volume, EMA($volume, 12)))), TsRank(Div(Sub(
  $close, $vwap), $vwap), 12)))
  109   IfElse(Greater(Rsquare($close, 24), 0.6), Neg(CsRank(Slope($close, 24))),
  Mul(CsRank(Neg(Div(Sub($close, $vwap), $vwap))), CsRank(Div($volume, EMA(
  $volume, 12)))))
  110   Neg(Mul(CsRank(Div(Sub($close, $low), Add(Sub($high, $low), 1e-6))),
  CsRank(Mul(Skew($returns, 24), Slope($close, 12)))))
```

以上即 FactorMiner 公布的 110 个 A 股因子的完整公式列表，与原文附录 D 一致。

