# 当智能体交易：面向 LLM 智能体的实盘多市场交易基准（When Agents Trade: Live Multi-Market Trading Benchmark for LLM Agents）

> 来源：https://arxiv.org/abs/2510.11695
> 原文：docs/papers/arXiv-2510.11695.pdf
> 翻译日期：2026-11-11 ｜ 范围：全文 ｜ 方式：机器翻译初稿，未经人工校对
> 引用于：docs/literature/W5-real-eval-fault-style.md

## 目录

- 摘要
- 1 引言
- 2 相关工作
  - 2.1 金融领域的 LLM 基准
  - 2.2 交易智能体与实盘基准
- 3 Agent Market Arena：实时交易与竞赛
  - 3.1 Market Intelligence Stream（MIS）
  - 3.2 Agent Execution Protocol（AEP）
  - 3.3 Performance Analytics Interface（PAI）
- 4 实验设置
- 5 结果
  - 5.1 智能体在实盘交易中的表现（RQ1）
  - 5.2 哪个更重要：智能体架构还是 LLM 骨干？（RQ2）
  - 5.3 理解由市场信号驱动的智能体决策（RQ3）
  - 5.4 揭示智能体交易风格与模式的影响（RQ4）
- 6 结论
- 参考文献（从略）
- 附录 A 质量控制细节
- 附录 B 智能体执行协议细节
- 附录 C 表现分析接口

## 摘要（Abstract）

虽然基于大语言模型（LLM）的智能体正被越来越多地用于金融交易，但它们能否在实盘市场中推理与适应仍不清楚，因为多数研究测试的是模型而不是智能体、覆盖的时段与资产有限、且依赖未经核实的数据。为填补这些空白，我们提出 Agent Market Arena（AMA），首个用于跨多个市场评估 LLM 交易智能体的终身（lifelong）、实时基准。AMA 在统一的交易框架中整合了经核实的交易数据、经专家核查的新闻与多样的智能体架构，从而支持在真实条件下公平且持续的比较。

它实现了四个智能体：InvestorAgent 作为单智能体基线，TradeAgent 与 HedgeFundAgent 具有不同的风险风格，DeepFundAgent 基于记忆进行推理；并在 GPT-4o、GPT-4.1、Claude-3.5-haiku、Claude-sonnet-4 与 Gemini-2.0-flash 上对它们逐一评估。在加密货币与股票市场上的实盘实验表明，智能体框架展现出显著不同的行为模式，从激进的风险承担到保守的决策不一而足，而模型骨干对结果差异的贡献较小。AMA 因此为对 LLM 智能体的金融推理与交易智能进行严格、可复现且持续演进的评估奠定了基础。

**CCS Concepts（保留原文）**：• Information systems → Data analytics; Data stream mining; • Computing methodologies → Multi-agent systems; • Applied computing → Economics.

**Keywords（保留原文）**：Live trading benchmark, Multi-agent, Large language models, Financial decision systems

译注：原文首页为 ACM 模板，含版权许可声明、会议占位信息（Conference acronym 'XX, Woodstock, NY；© 2018）与 ACM Reference Format 条目，均属排版占位内容，此处不逐字重复。

## 1 引言

基于大语言模型（LLM）的智能体能否真正实时交易？这个问题处在金融人工智能的最前沿：语言模型正从静态的文本生成器，转变为在动态环境中感知、规划并行动的自主决策系统 [11, 21]。金融市场动荡、高维且毫不留情，或许为这种新兴智能提供了最严苛的检验 [1, 20, 28]。交易不是孤立的预测，而是在一个每秒都在变化的世界里，做出一系列高风险的连续决策。要成功，智能体不仅要理解市场叙事，还必须持续适应不断展开的事件、不确定的反馈与对抗性力量 [7, 19, 39]。

已有不少工作尝试回答这个问题。DeepFund [17] 是重要的一步，它引入了一个集成实时数据流、模拟实时决策的多智能体框架。InvestorBench [18] 把静态评估扩展到交易仿真，通过回放历史数据来评估假想收益。除此之外，聚焦金融情感分析 [24, 25]、事件抽取 [12, 16] 与金融文本理解 [42, 46] 的基准推进了领域理解，但没有捕捉到适应性与反馈——而这两者正是现实交易的标志。

尽管有这些努力，回答这个问题仍非易事，因为现有基准持续面临三个根本挑战。**第一，现有工作主要评估的是模型而不是智能体。** 像 DeepFund [17] 与 InvestorBench [18] 这样的框架绑定在固定的智能体结构上，评估的是模型骨干而非智能体本身。即便替换成不同的 LLM，性能趋势依然相似，这说明相同的框架会导致趋同的决策行为。

**第二，评估范围极其有限。** DeepFund 只在 24 天的有限时段上测试智能体，且只覆盖美国股票（Apple、American Express、Bank of America、Coca-Cola 与 Chevron），也就是说每股总共只有 24 次决策。如此狭窄的设定，几乎无法说明智能体如何泛化到多样的市场状态，尤其是在牛熊切换或更长交易周期的情形下。

**第三，输入数据缺乏一致性与核实。** 现有交易基准依赖异构的数据源来获取市场价格与新闻，例如 yfinance（https://pypi.org/project/yfinance/）与 Finnhub（https://finnhub.io/）。然而，现有基准没有遵循统一的数据获取协议，其新闻流因聚合多个 API 源而经常互相重叠或矛盾。同一个市场事件可能在不同源中出现多次、或强调程度不一，带来冗余与不一致。这类未经核实的嘈杂输入扭曲了智能体可用的信息环境，进而损害其交易决策的可靠性与可解释性。

为填补这一空白，我们提出 Agent Market Arena（AMA），首个面向 LLM 交易智能体的终身、实时、多资产类评估框架，完全建立在经核实且持续更新的市场数据之上。AMA 已实盘运行两个月，并将作为一个开放的、不断演进的基准持续存在，与真实市场一同成长。AMA 的定义性特征在于其统一协议、经核实的信息流与多资产类的市场覆盖。该协议标准化了智能体与市场交互的方式：每个智能体以相同的初始资金起步，在固定的每日时点交易，并遵循完全相同的执行与反馈规则，从而保证公平且可复现的评估。

AMA 还维护着一条经核实的信息流水线，持续整合价格数据、金融新闻与公司报告。每条流都经过标准化、摘要，并通过专家核查来检验事实准确性、一致性与中立性，为交易决策提供可靠且无偏的输入。此外，AMA 连接了横跨股票与加密货币的多样市场，为适应性推理提供了一个真实且动态的试验台。

在此基础上，我们首次把一组最先进的 LLM 智能体系统部署到两只股票（Tesla（TSLA）与 Biomarin Pharmaceutical（BMRN））和两种加密货币（Ethereum（ETH）与 Bitcoin（BTC））上持续运行。部署始于两个月前，此后从未中断，每日执行交易并适应实时市场波动。该系统包括 InvestorBench [18]、TradeAgent [40]、HedgeFundAgent [37] 与 DeepFundAgent [17]，各自代表不同的推理策略，从激进交易到保守对冲，从基于角色到基于记忆的自适应决策。

对每个智能体框架，我们还测试多个 LLM 骨干，使 AMA 能够在相同交易条件下分离智能体架构与模型选择的影响。所有交易活动都通过 AMA 评估流水线记录（https://ama.thefin.ai/live ），形成一个持续增长的现实决策与结果数据集。表现用标准金融指标衡量，包括累积收益、年化波动率、最大回撤与 Sharpe 比率，以支持跨智能体、跨市场的一致且可解释的比较。

我们为期两个月的实盘交易结果表明，基于 LLM 的智能体能够持续展现出有前景的交易决策能力，在动态金融环境中表现出真正的推理能力。在所有资产与所有时段上，智能体架构被证明是塑造行为的主导因素。InvestorAgent 在 TSLA 上达到 6.47 的 Sharpe 比率，以更平滑的收益与更低的回撤跑赢买入并持有。DeepFundAgent 在 BTC 上达到 2.45，说明基于记忆的推理改善了波动环境下的适应性。TradeAgent 与 HedgeFundAgent 偏好激进的风险选择，带来可观收益的同时也伴随更高的波动。在 GPT-4o[15]、GPT-4.1[27]、Claude-3.5-haiku[2]、Claude-sonnet-4[3] 与 Gemini-2.0-flash[10] 之间更换 LLM 骨干所带来的结果变化，小于更换智能体框架，这确认了这些模式在不同模型之间是稳定且可复现的。

我们的贡献可概括如下：

- ⊲ 首先，我们提出 Agent Market Arena，首个在实盘市场条件下评估基于 LLM 的金融智能体的终身、实时基准。
- ⊲ 其次，我们构建了一个覆盖多个市场的经核实数据集，把真实交易数据与经专家评审的金融新闻整合起来，以保证事实准确性、中立性与持续更新。
- ⊲ 第三，我们实现了一套多样的交易智能体，包括单智能体、多智能体，以及各种角色化与记忆自适应设计，以考察智能体结构与交易风格如何在不同资产上塑造表现。
- ⊲ 最后，我们构建了一个透明的排行榜，记录盈利能力与适应性随时间的变化，为研究智能金融智能体提供一个开放且可复现的平台。
## 2 相关工作

### 2.1 金融领域的 LLM 基准

如今关于金融基准的工作越来越多。早期的金融 NLP 基准 [5, 6, 22, 33, 38, 42]，例如 FinBen [41]，把评估从情感与问答扩展到检索增强任务与多步决策问题，但它们在很大程度上仍是静态的、以英语为中心。另有工作 [29, 47] 引入了把语言焦点扩展到英语与中文之外的基准，而 MultiFinBen [30] 把这些观察延伸到多语言与多模态评估。FinReason [31] 进一步引入了金融推理任务，表明通用推理模型在金融数据上会退化。

### 2.2 交易智能体与实盘基准

另有一条不断增长的研究线，探索用 LLM 或智能体做决策并研究其决策表现。越来越多的研究开始设计与分析交易智能体。FinMem [44] 与 InvestorBench [18] 引入了记忆增强的 LLM 智能体，并在回测市场信息上为其建立基准。FLAG-TRADER [43] 把语言模型与策略梯度训练结合，用于序贯决策。FinCon [45] 把记忆更新扩展到多智能体交互，提出一个用于单只股票交易与组合管理的框架，纳入层级化沟通与风险控制。HedgeFundAgents [37] 通过建模对冲基金层级结构推进了这一方向，协调一名中央经理与多名对冲专家以获得更稳健的收益。TradeAgents [40] 进一步探索了专业交易智能体之间的去中心化协调，凸显分工如何改善市场决策。然而这些系统往往运行在静态环境中。为解决基准泄漏与过度干预问题，DeepFund [17] 提出了一个用于基金投资的实盘多智能体竞技场，实现对 LLM 驱动策略的动态评估。

图 1：Agent Market Arena 的整体框架。（原文第 3 页）

## 3 Agent Market Arena：实时交易与竞赛

Agent Market Arena 的整体框架如图 1 所示。它被设计用来评估不同智能体框架在获得实时市场环境访问权时的表现。它由三个主要组件构成。**其一，Market Intelligence Stream（MIS）** 持续从多个来源聚合数据，并生成高质量的每日市场状况摘要；摘要由金融专家复核，以保证准确性、完整性与中立性。**其二，Agent Execution Protocol（AEP）** 提供一个统一的环境来部署多个交易智能体，让每个智能体都能访问经核实的更新，并在被评估的资产上独立做出交易决策。**其三，Performance Analytics Interface（PAI）** 提供一个持续更新的仪表盘，跟踪并比较由不同 LLM 骨干构建的所有智能体的实时表现，对盈利能力、稳定性与适应性给出透明视图。

### 3.1 Market Intelligence Stream（MIS）

我们首先从大量异构来源采集实时市场数据，以兼顾覆盖度与准确性，这些来源包括通用 API 与在线新闻聚合器。我们利用的源有 OpenAI Web Search（https://platform.openai.com/docs/guides/tools-web-search?api-mode=responses ）、Finnhub、NewsData（https://newsdata.io/ ）、yifinance、CryptoNews（https://cryptonews.com/ ）与 Binance（https://www.binance.com/en ），它们不仅提供主流财经媒体的新闻流，也提供社交媒体内容。这样，无论是 API 驱动的订阅源、直接的新闻内容，还是来自 Twitter（https://x.com/?lang=en ）与 Reddit（https://www.reddit.com ）等平台的整合社交媒体信号，都会被纳入以捕捉新兴情绪。这种多源整合降低了依赖单一渠道的偏见，提供了更广、更均衡、且真正实时的市场环境视图。

尽管来源多样，许多内容可能部分重叠；如果同一条信息反复出现在智能体面前，就会引入偏见。为此，我们加入一个摘要步骤来合并新闻，防止冗余扭曲评估。我们用 GPT-5-nano 执行该任务，实现细节见附录 A。

**质量控制。** 为严格评估摘要新闻的质量，我们从生成结果中随机抽取 20 条日度条目，股票与加密货币各覆盖 20 天。沿用以往工作的关注点，两名独立标注者按以下标准评估每条条目：(1) 日期准确性 [8]：每条必须精确对应到预期的交易日期及相关资产。(2) 覆盖度 [36]：样本必须涵盖驱动价格的主要类别中，当日与目标资产直接相关的所有重大新闻，确保没有重要的资产相关信息被遗漏。(3) 偏见意识 [9]：判断摘要过程是否引入了原始内容中不存在的额外或明显偏见。每条标准采用三级量表：0 表示不满足，1 表示部分满足，2 表示完全满足。

评估由两名标注者各自独立完成，使用股票与加密货币的 20 天样本。结果显示出很强的一致性：日期准确性一致率达 87.5%，覆盖度 92.5%，偏见意识 100%。大多数日期差异（7 例，得分 = 1）源于 API 延迟——检索到的链接是当日的，但文章内容滞后一到两天。有四例覆盖度得 1 分，主要是因为摘要部分不完整，遗漏了次要更新，例如相关的公司名称变更（这标志着业务方向变化）。这些遗漏被认为可以接受，因为在被评估的摘要中，所有重大的影响市场的事件都被准确捕捉。在偏见意识方面，没有发现任何摘要引入了超出原始新闻源的偏见或情绪。这种严格的日常质量控制确保基准反映高保真的实时市场叙事，并最大程度减少过时或带偏见的信息进入智能体评估。

### 3.2 Agent Execution Protocol（AEP）

Agent Execution Protocol（AEP）定义了 AMA 中所有智能体如何与市场环境交互。它标准化了三个核心组件，包括输入、输出与配置，以保证表现差异来自推理能力而非实现差异。

**输入。** 每个智能体收到完全相同的每日输入，包括经核实的市场数据与来自 MIS 的摘要新闻。这些信息被组织成统一的提示格式，包含资产标识、历史价格、近期新闻摘要与上下文交易元数据。这种一致的输入设计保证了所有智能体在相同的市场知识与时间条件下运行。

**输出。** 智能体从同一动作空间中产生离散的每日动作：BUY、SELL、HOLD。这些动作用来更新模拟组合并计算次日收益。BUY 表示智能体预期资产价值上升并增加仓位；SELL 表示相反的预期；HOLD 反映中性或不确定，保持当前仓位不变。所有交易决策在同一固定时点同步执行，以保证跨模型、跨市场的公平比较。

**提示与超参数。** 每个智能体还由一个结构化的系统提示引导，其中定义了交易策略与动作说明。为保持公平，temperature、重试次数等生成参数在所有智能体与骨干上固定不变（更多细节见附录 B）。

**InvestorAgent [18]** 是一个集成了记忆模块的单智能体框架，用于存储历史交易决策与上下文信息。它分析过往结果以提取可执行的洞见，再用这些洞见改进后续的优化与决策过程。

**TradeAgent [40]** 采用受真实交易公司启发的多智能体架构。它不只依赖固定的技术指标，而是编排专业角色——如基本面分析师、情绪分析师、新闻分析师与技术分析师——其洞见由研究者智能体辩论，再由交易员智能体聚合。最终的交易提案在执行前由风险管理与组合经理检查。

**HedgefundAgent [37]** 通过编排遵循著名交易人物角色（如 Aswath Damodaran、Ben Graham 等）的专业智能体来建模一个对冲基金团队，各自模拟投资过程中的不同角色。它们的信号由组合经理聚合成交易意图，同时风险经理计算风险指标并执行仓位限制。

**DeepFundAgent [17]** 旨在通过处理流式输入、生成交易信号，并基于存储在记忆中的历史组合更新以及媒体、技术分析来更新仓位，从而检验适应性。这一设定使得可以在动态环境中评估基于 LLM 的决策系统，相对规则型或静态基准的表现。

### 3.3 Performance Analytics Interface（PAI）

每个智能体每天做一个交易决策，表示为信号 $w_t \in \{1, -1, 0\}$，其中 $w_t = 1$ 表示买入该资产，$w_t = -1$ 表示卖出，$w_t = 0$ 表示持有当前仓位。智能体的日收益为：

$$r_t = w_t \frac{P_t - P_{t-1}}{P_{t-1}}$$

其随时间的整体表现通过累积收益跟踪：

$$R_t = \prod_{i=1}^{t} (1 + r_i) - 1$$

为评估交易表现，我们采用五个广泛使用的金融指标。**累积收益（CR）** [13] 度量智能体组合在整个评估期的总增长，刻画其整体盈利能力。**年化收益（AR）** [34] 把该值调整为年度速率：

$$R_{annual} = (1 + R_t)^{252/T} - 1$$

从而允许跨不同时间跨度比较。为量化风险，我们把**年化波动率（AV）** [14] 计算为：

$$\sigma_{annual} = \sqrt{252} \times std(r_t)$$

它反映智能体日收益的波动幅度。**Sharpe 比率（SR）** [35] 由下式给出：

$$S = \frac{\bar{r} - r_f}{\sigma_{annual}}$$

在无风险利率 $r_f = 0$ 的假设下，评估智能体把风险转换为收益的效率。最后，**最大回撤（MDD）** [23] 定义为：

$$D_{max} = \max_{t} \frac{\max_{i \le t} R_i - R_t}{\max_{i \le t} R_i}$$

它捕捉从峰值到谷底的最大观测损失，指示下行敞口。

所有指标每日更新，并显示在一个实时排行榜上，该排行榜比较不同 LLM 骨干与市场类型下智能体的盈利能力、稳定性与适应性。

**智能体初始化与评估。** 为建立历史依据并构建上下文记忆，智能体经历一个初始化阶段，使用 2025-05-01 至 2025-07-31 的数据，在此期间它们适应近期市场动态、模拟真实交易环境并形成有代表性的组合仓位。实时评估于 2025-08-01 开始。截至本文起草日期 2025-09-30，智能体已完成两个月的实盘交易，并继续自主运行，实时产生每日交易动作与表现评估。

## 4 实验设置

**LLM 选择。** 对每个智能体，我们评估来自 OpenAI、Claude 与 Gemini 的五个不同骨干模型，具体包括 GPT-4o、GPT-4.1、Gemini-2.0-flash、Claude-3.5-haiku 与 Claude-sonnet-4。

**资产。** 我们同时评估股票与加密货币市场，以捕捉不同的市场动态与行为模式。有代表性的测试资产包括加密货币领域的 Bitcoin（BTC）与 Ethereum（ETH），以及两只公开交易的股票 Tesla（TSLA）与 BioMarin Pharmaceutical（BMRN），分别代表高科技与生物医学板块。

BTC、ETH 之类的加密货币运行在高度波动、由情绪驱动的环境中，对宏观经济与政策信号反应迅速，为模型在极端市场波动下的适应性提供了严格检验 [4]。相比之下，TSLA 与 BMRN 之类的股票受板块特定的基本面影响——技术创新、生产指标或临床试验结果——这让我们得以评估系统在结构化、信息丰富的情境下处理得如何 [32]。通过把这些异构资产结合起来，我们确保评估横跨多样的资产类别与时间敏感度，为真实交易条件下决策智能体提供一个全面的基准。
## 5 结果

本节考察不同智能体在一个持续演进的实盘交易环境中的表现，以回答以下研究问题（RQ）：

- **RQ1**：基于 LLM 的智能体能否真正交易，即在实盘市场中做出有利可图且一致、能跑赢简单买入并持有策略的决策？
- **RQ2**：哪个因素对交易性能的贡献更大——智能体的结构框架，还是其底层 LLM 骨干的推理能力？
- **RQ3**：智能体能在多大程度上有效地解读复杂市场信息，并把它们转化为能够预判并适应价格波动的交易决策？
- **RQ4**：从激进到保守的不同交易哲学，如何影响跨市场的决策行为与整体盈利能力？

### 5.1 智能体在实盘交易中的表现（RQ1）

表 1 汇总了所有智能体在加密货币与股票市场上的实盘交易结果。总体而言，这些发现证实基于 LLM 的智能体确实能够实时地盈利交易，常常在动态市场条件下跑赢简单的买入并持有策略并保持稳定。不过，结果在不同智能体与资产类型之间差异显著，说明表现在很大程度上取决于设计哲学与市场情境。

**表 1：四个智能体在五种骨干模型上、于两只股票资产（TSLA、BMRN）与两种加密资产（BTC、ETH）上合并的实盘交易结果，时间为 8 月 1 日至 9 月 30 日。指标：CR（累积收益）、AR（年化收益）、AV（年化波动率）、SR（Sharpe 比率）、MDD（最大回撤）。「Vote」表示跨骨干的多数投票集成。（原文第 5 页）**

| Agent | Model | TSLA CR% | TSLA AR% | TSLA AV% | TSLA SR | TSLA MDD% | BMRN CR% | BMRN AR% | BMRN AV% | BMRN SR | BMRN MDD% | BTC CR% | BTC AR% | BTC AV% | BTC SR | BTC MDD% | ETH CR% | ETH AR% | ETH AV% | ETH SR | ETH MDD% |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Buy & Hold | - | 46.88 | 962.13 | 40.89 | 6.00 | 6.34 | -6.89 | -35.53 | 29.03 | -1.37 | 15.03 | 0.66 | 4.02 | 30.05 | 0.28 | 11.95 | 18.56 | 176.92 | 71.71 | 1.77 | 20.23 |
| InvestorAgent | GPT-4o | 33.01 | 783.38 | 42.32 | 5.37 | 6.34 | -5.33 | -25.93 | 26.99 | -0.98 | 14.36 | -1.22 | -7.10 | 20.77 | -0.25 | 8.79 | -1.98 | -11.29 | 55.58 | 0.06 | 22.13 |
| InvestorAgent | GPT-4.1 | 40.83 | 764.39 | 34.35 | 6.47 | 4.38 | 3.79 | 23.19 | 24.33 | 0.98 | 7.35 | -3.34 | -18.40 | 20.32 | -0.90 | 9.92 | 1.35 | 8.38 | 50.73 | 0.41 | 23.76 |
| InvestorAgent | Gemini-2.0-flash | 10.57 | 80.22 | 42.30 | 1.60 | 8.50 | -13.88 | -53.62 | 25.23 | -2.92 | 19.57 | -2.78 | -15.51 | 19.58 | -0.76 | 10.20 | -6.39 | -32.64 | 64.98 | -0.28 | 32.27 |
| InvestorAgent | Claude-3.5-haiku | 11.55 | 124.83 | 38.35 | 2.30 | 8.35 | -8.35 | -41.48 | 25.49 | -1.97 | 15.24 | -7.06 | -35.46 | 30.02 | -1.31 | 15.18 | 5.05 | 34.29 | 71.94 | 0.76 | 22.98 |
| InvestorAgent | Claude-sonnet-4 | 28.91 | 328.14 | 41.01 | 3.76 | 8.41 | -6.89 | -34.58 | 28.34 | -1.36 | 15.12 | -6.48 | -33.04 | 25.93 | -1.42 | 12.62 | 5.56 | 38.20 | 61.40 | 0.83 | 27.17 |
| InvestorAgent | Vote | 29.13 | 293.80 | 37.68 | 3.83 | 8.37 | -5.47 | -28.08 | 27.50 | -1.06 | 13.64 | -2.19 | -12.43 | 22.16 | -0.49 | 9.68 | -1.97 | -11.20 | 58.80 | 0.09 | 28.80 |
| TradeAgent | GPT-4o | -4.25 | -54.22 | 22.36 | -3.38 | 5.73 | -1.95 | -22.97 | 21.56 | -1.11 | 7.81 | -5.05 | -26.67 | 7.50 | -4.09 | 5.05 | -6.23 | -31.95 | 31.78 | -1.05 | 15.95 |
| TradeAgent | GPT-4.1 | -38.72 | -94.33 | 50.68 | -5.38 | 38.72 | 4.84 | 27.51 | 23.39 | 1.15 | 6.20 | -5.65 | -29.41 | 28.83 | -1.07 | 9.76 | -11.42 | -51.61 | 68.44 | -0.72 | 24.75 |
| TradeAgent | Gemini-2.0-flash | 21.91 | 203.20 | 30.23 | 3.82 | 6.41 | -0.31 | -1.61 | 22.11 | 0.04 | 9.46 | 5.02 | 34.09 | 24.27 | 1.33 | 5.83 | 9.78 | 74.78 | 52.88 | 1.32 | 16.01 |
| TradeAgent | Claude-3.5-haiku | -6.62 | -36.48 | 25.72 | -1.64 | 11.05 | -9.45 | -40.61 | 16.81 | 3.01 | 13.85 | -14.51 | -60.85 | 24.07 | -3.77 | 16.37 | -12.93 | -56.31 | 50.12 | -1.40 | 15.21 |
| TradeAgent | Claude-sonnet-4 | -5.43 | -24.10 | 26.42 | -0.91 | 12.89 | 14.57 | 121.92 | 21.86 | 3.76 | 3.81 | -13.02 | -56.61 | 26.36 | -3.03 | 15.02 | -12.35 | -54.57 | 41.10 | -1.71 | 20.50 |
| TradeAgent | Vote | -0.36 | -2.30 | 24.44 | 0.02 | 9.03 | 1.22 | 7.55 | 18.90 | 0.48 | 6.70 | -7.28 | -36.39 | 23.83 | -1.78 | 11.53 | -9.89 | -46.39 | 40.12 | -1.35 | 14.57 |
| HedgeFundAgent | GPT-4o | -29.15 | -84.86 | 40.94 | -4.39 | 29.15 | 23.70 | 247.76 | 26.59 | 4.83 | 5.59 | -9.09 | -43.46 | 29.97 | -1.76 | 11.14 | 39.66 | 638.04 | 69.75 | 3.21 | 14.63 |
| HedgeFundAgent | GPT-4.1 | -29.15 | -84.86 | 40.94 | -4.39 | 29.15 | 23.70 | 247.76 | 26.59 | 4.83 | 5.59 | -9.09 | -43.46 | 29.97 | -1.76 | 11.14 | 39.66 | 638.04 | 69.75 | 3.21 | 14.63 |
| HedgeFundAgent | Gemini-2.0-flash | -29.15 | -84.86 | 40.94 | -4.39 | 29.15 | 23.70 | 247.76 | 26.59 | 4.83 | 5.59 | -9.09 | -43.46 | 29.97 | -1.76 | 11.14 | 39.66 | 638.04 | 69.75 | 3.21 | 14.63 |
| HedgeFundAgent | Claude-3.5-haiku | -29.15 | -84.86 | 40.94 | -4.39 | 29.15 | 23.70 | 247.76 | 26.59 | 4.83 | 5.59 | -9.09 | -43.46 | 29.97 | -1.76 | 11.14 | 39.66 | 638.04 | 69.75 | 3.21 | 14.63 |
| HedgeFundAgent | Claude-sonnet-4 | -29.15 | -84.86 | 40.94 | -4.39 | 29.15 | 23.70 | 247.76 | 26.59 | 4.83 | 5.59 | -9.09 | -43.46 | 29.97 | -1.76 | 11.14 | 39.66 | 638.04 | 69.75 | 3.21 | 14.63 |
| HedgeFundAgent | Vote | -29.15 | -84.86 | 40.94 | -4.39 | 29.15 | 23.70 | 247.76 | 26.59 | 4.83 | 5.59 | -9.09 | -43.46 | 29.97 | -1.76 | 11.14 | 39.66 | 638.04 | 69.75 | 3.21 | 14.63 |
| DeepFundAgent | GPT-4o | 13.89 | 95.19 | 37.14 | 1.98 | 7.61 | 3.72 | 22.68 | 25.89 | 0.92 | 8.92 | -0.30 | -1.80 | 24.35 | 0.04 | 7.98 | 18.03 | 169.68 | 71.07 | 1.74 | 21.86 |
| DeepFundAgent | GPT-4.1 | -5.52 | -27.77 | 37.30 | -0.69 | 19.22 | 4.86 | 29.67 | 16.67 | 1.64 | 3.49 | 0.44 | 2.68 | 1.08 | 2.45 | 0.00 | 2.89 | 18.56 | 58.62 | 0.57 | 26.08 |
| DeepFundAgent | Gemini-2.0-flash | -8.04 | -55.62 | 20.40 | -3.88 | 8.04 | 3.59 | 20.84 | 24.77 | 0.89 | 6.57 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | -13.11 | -56.85 | 40.55 | -1.87 | 22.20 |
| DeepFundAgent | Claude-3.5-haiku | -15.43 | -57.76 | 38.49 | -2.04 | 28.48 | -1.12 | -6.01 | 26.80 | -0.10 | 12.25 | 1.67 | 10.40 | 27.51 | 0.50 | 7.91 | 10.74 | 84.08 | 69.93 | 1.21 | 23.11 |
| DeepFundAgent | Claude-sonnet-4 | -6.96 | -32.07 | 35.81 | -0.90 | 12.99 | 5.48 | 34.81 | 25.27 | 1.31 | 8.52 | -8.24 | -40.23 | 21.91 | -2.24 | 10.18 | 8.20 | 60.29 | 56.87 | 1.11 | 18.58 |
| DeepFundAgent | Vote | 8.61 | 55.75 | 36.68 | 1.39 | 10.14 | 9.45 | 52.43 | 22.82 | 1.96 | 6.42 | -0.54 | -3.20 | 1.33 | -2.45 | 0.54 | 4.91 | 33.22 | 65.65 | 0.75 | 13.00 |

在被评估的系统中，DeepFundAgent 给出了最均衡、最一致的结果，在 TSLA 上取得 8.61%、在 BMRN 上取得 9.45% 的累积收益，年化波动率分别为 36.68% 与 22.82%，Sharpe 比率分别为 1.39 与 1.96。InvestorAgent 同样具有竞争力，尤其是在 GPT-4.1 下，在 TSLA 上达到 40.83% 的累积收益与 6.47 的 Sharpe 比率。它对骨干模型与资产也表现出敏感性：其在 BMRN 上的 CR 从 3.79%（GPT-4.1）降至 –6.89%（Claude-sonnet-4）。

TradeAgent 与 HedgeFundAgent 的波动更大，TradeAgent 在 TSLA 上的收益从 –38.72%（GPT-4.1）到 21.91%（Gemini-2.0-Flash）不等。HedgeFundAgent 的结果好坏参半，在一种设定下于 ETH 取得 39.66% 的 CR，却在 BTC 上为负；但凭借其层级协调——十六个专业子智能体向两个聚合信号的管理智能体供数——它在各骨干之间保持了相对稳健，减少了单个 LLM 引入的方差。

在这些实验中，没有任何单个 LLM 或智能体能在所有资产上持续领先。尽管如此，结果清楚地显示出智能体与模型的互补性（agent–model complementarity），某些配对会带来明显更强的结果。例如，TradeAgent 与 Gemini-2.0-flash 结合时在 TSLA、ETH 与 BTC 上取得领先表现，在 BMRN 上排名第二；InvestorAgent 与 GPT-4.1 配对时表现最好，在 TSLA 与 BMRN 上都给出强劲结果。同样，DeepFundAgent 在 GPT-4o 下取得其最高收益，在 ETH 与 TSLA 上表现稳健，并在其余资产上保持竞争力。这凸显了开展多市场评估的重要性——相比局限于少量资产与结果的分析，它能提供更广的洞见。

### 5.2 哪个更重要：智能体架构还是 LLM 骨干？（RQ2）

为分离智能体设计与 LLM 骨干对实盘交易表现的相对影响，我们在所有智能体—模型配对上聚合结果，如图 2 所示。图 2a 报告每个智能体在不同 LLM 下的表现，图 2b 总结每个 LLM 在各智能体架构上的表现。

总体而言，结果表明：在固定智能体框架内更换底层 LLM，只会带来盈利能力上的适度变化；而在保持 LLM 不变的情况下更换智能体设计，则会导致大得多的表现分化。例如在图 2a 中，InvestorAgent 在 TSLA 上的结果紧密聚簇，跨 LLM 配置的 spread 极小，说明换模型效果有限。相比之下，图 2b 显示 GPT-4.1（浅蓝）在各智能体上的收益跨度很大，说明智能体的结构设计对交易结果的影响，强于骨干模型本身的推理能力。

这些发现意味着，智能体的架构——包括其决策逻辑、协调策略与风险控制机制——在塑造盈利能力与稳定性上，比单纯升级到更强大的模型起着更决定性的作用。在 AMA 环境中，改进智能体使用 LLM 的方式，可能比改进 LLM 本身带来更大的收益。

图 2：不同智能体与不同 LLM 在四种资产上的聚合表现。实线表示平均累积收益，阴影区域表示更换 LLM 或智能体框架时观测到的最大与最小 CR 之间的范围。（原文第 6 页）

### 5.3 理解由市场信号驱动的智能体决策（RQ3）

为更好地理解智能体在实时、波动的市场条件下如何做出交易决策，我们分析了 TradeAgent 与 InvestorAgent 在 BTC 上的行为，分别以 Gemini-2.0-flash 与 GPT-4.1 为骨干。选择 BTC 是因为它对市场新闻与情绪高度敏感。我们比较了它们相对买入并持有基准的累积收益轨迹（图 3），并考察每个智能体如何解读宏观经济信号、如何在重大波动事件期间调整策略。我们聚焦三个关键片段：8 月 13 日、8 月 28 日与 9 月 28 日，它们既包含成功的交易，也包含失败的预测。

在 8 月 13–14 日，全球股市进入一轮广泛的多头动能，美国、欧洲与亚洲的主要指数纷纷创下历史新高。这轮由政策宽松预期与主权资金回流推动的同步上涨，被媒体广泛描述为近年来最协调的全球反弹之一 [26]。尽管压倒性地看多，TradeAgent 识别出这种极端乐观的脆弱性，认识到一个「前所未有」的事件缺少历史均衡。它在接近顶部时正确地对冲了风险，在价格回归正常时获利。

8 月 28–29 日期间发生了几起罕见的结构性变化：(1) 政治资本遇上挖矿——由 Trump 支持的 American Bitcoin Corp. 通过与 Gryphon Digital Mining 合并在 NASDAQ 上市，标志着政治与比特币基础设施之间最早的明确交集之一。(2) 亚洲的机构囤积激增，主要日韩企业宣布计划把比特币纳入其财政储备。(3) 生态创新在推进——由 RGB 协议与 Tether 在比特币网络上的集成驱动，把比特币的角色扩展到价值储存之外。尽管这些是长期看多信号，TradeAgent 检测到技术面上的短期耗尽并执行了 SELL，准确预判了一次短期回调。

相比之下，在 9 月 28–29 日，智能体的空头头寸起初以 ETF 资金流出与同步回撤为理由，却被流动性的突然激增与主权资金流入逆转，导致一次轧空（short squeeze）。所有智能体都犯了同样的误判，反映出对突发宏观反转作出反应的困难。

图 3：不同市场事件下智能体在 BTC 上的表现。柱子表示 TradeAgent（Gemini-2.0-flash）与 InvestorAgent（GPT-4.1）之间的利润差。（原文第 7 页）

图 4：BTC 累积收益与买入并持有基准的对比（2025 年 8–9 月），标注了每日新闻情绪（绿 = 看多，灰 = 中性，红 = 看空）与智能体投票信号（方块：蓝 = BUY，灰 = HOLD，橙 = SELL）。（原文第 8 页）

图 4 显示，在大部分时间里，InvestorAgent（GPT-4.1）与 TradeAgent（Gemini-2.0-flash）之间的表现差距都很小。InvestorAgent 抓住了 8 月 13 日前后的早期上涨，却错过了后来的转折点，让 TradeAgent 得以利用波动、更动态地适应情绪变化而反超。这些结果表明，最成功的智能体是那些能够利用波动时段的智能体，而不只是跟随长期趋势——利用波动的智能体更契合 AMA 的日频交易。

这一分析也凸显了建立在经核实、多源市场数据之上的持续更新、多资产类基准的价值。股票与加密货币两侧的实时进展都表明，静态或单一市场的评估无法公平地衡量智能体表现。通过整合经核实的数据流与标准化的决策协议，AMA 使得在一致且动态的市场条件下系统地比较多个智能体成为可能。这种设计对不同智能体架构如何解读真实金融环境，提供了更全面、更可泛化的理解。

### 5.4 揭示智能体交易风格与模式的影响（RQ4）

我们进一步考察交易风格如何在 AMA 框架中塑造智能体行为。图 4 显示了每日市场情绪、BTC 价格动态与智能体投票行为之间的相互作用。尽管所有智能体运行在完全相同的市场信息上，它们的交易策略从第一天起就出现分歧：HedgeFundAgent 与 InvestorAgent 偏好空头，DeepFundAgent 偏好买入，而 TradeAgent 倾向于持有。随着交易推进，这些策略对比变得更加分明，反映出每个框架内在的风险偏好与决策逻辑。

在为期两个月的实盘交易中，整体市场情绪保持乐观。尽管如此，HedgeFundAgent 始终维持空头头寸，暴露出其逆向与高风险的本性。TradeAgent 尽管通常波动更大，却在大多数日子选择持有仓位，说明它虽然天生激进，但会依骨干模型表现出保守行为。InvestorAgent 的决策在很大程度上跟随主流市场趋势，这反映在其累积收益曲线（图 2a）上——该曲线在大部分交易时段领先于其他智能体。该智能体频繁执行买卖动作，展现出主动、愿意冒险的交易风格。不过，它在各资产上的整体盈利能力仍属中等，说明在风险升高期间它采取了相对谨慎的立场。

相比之下，DeepFundAgent 展现出更保守的决策模式，经常选择「vote」动作，并在多个资产上保持稳定收益。两个智能体策略中观察到的审慎，可能源于它们的记忆自适应机制——使其能够借鉴先前的高风险经历，并把决策调整得更规避风险。这些发现与表 1 一致，凸显交易风格是盈利能力与风险敞口的关键决定因素：DeepFundAgent 取得了持续、温和的收益，而激进的 HedgeFundAgent 在 ETH 与 BMRN 上分别产生 39.66% 与 23.70% 的可观利润，却在 TSLA 与 BTC 上遭受重大亏损。这些结果共同重申了一条基本的市场原则：更高风险可能带来更大回报，也带来更大的潜在损失。

## 6 结论

在本工作中，我们提出了 AMA，首个持续更新的、多资产类的基准，用于实时评估基于 LLM 的交易智能体。它建立在三个核心组件之上——经核实的多市场信息流、统一的交易协议与透明的表现接口——AMA 为在真实市场条件下研究金融交易智能体建立了一个可复现且动态的基础，弥合了语言理解与实时决策之间的鸿沟。

我们的发现揭示了四点关键洞见。**第一**，基于 LLM 的智能体能够有效交易，并在实盘环境中持续跑赢简单的买入并持有策略。**第二**，对盈利能力与适应性影响最强的是智能体架构，而不是 LLM 骨干的选择。**第三**，智能体在解读复杂、快速变化的市场信号时表现出不同的推理行为，更自适应的框架被证明更善于驾驭波动。**第四**，从激进到保守的交易风格，塑造了每个智能体的风险—收益画像与随时间的稳定性。在未来工作中，我们计划为 AMA 增加智能体间通信、跨资产动态与强化学习反馈，朝着更深入地理解 LLM 驱动系统中的自主金融智能迈进。

## 参考文献（从略）
## 附录 A 质量控制细节

为确保交付给智能体的每日市场信息是高质量的，我们对摘要提示做了多轮迭代精化。最初，我们基于 5 月 1 日至 5 月 10 日收集的数据做了一次初步复核与调整，显著提升了生成质量。随后，我们分别从加密货币与股票市场抽取了 20 天的 BTC 与 TSLA 新闻，由两名领域专家独立核实其准确性与覆盖度，以保证所生成摘要的质量与可靠性。

这一迭代过程确保最终摘要同时捕捉了市场广度与事实精度，最大程度减少了跨来源的冗余与偏见。由此，精化后的每日输入为智能体提供了经一致、经核实且信息丰富的市场情境，用于决策。

**摘要提示（Prompt For Summarization，保留原文）**

```text
Task: Analyze the provided {symbol} news articles from the
{date_str} and produce a clear, comprehensive, and well-
structured summary.

Instructions:
• Use only the provided articles for your analysis.
• Do not retrieve or reference any external informa-
tion.
• Refrain from including current prices or speculative
forecasts.
• Focus strictly on the events, sentiment, and con-
textual details presented in the articles.
• Do not mention or enumerate article IDs in the out-
put.

Articles from {date_str}:
{articles_text}

Output Requirements:
(1) Provide a cohesive summary highlighting the key
developments for {symbol}.
(2) Identify major themes or emerging narratives within
the content.
(3) Assess and articulate the overall market sentiment
reflected in the articles.

Compose your response as a coherent and polished narra-
tive that maintains logical flow and clarity throughout.
```

**质量控制指引（Quality Control Guideline，保留原文）**

**Purpose.** This guideline outlines the procedures to ensure high-quality and unbiased daily news summaries used by agents.

**1. Objective**

Daily summarized news must accurately represent the key information from multiple sources without introducing bias. Each asset's daily summary should be:

- Accurate: Correctly aligned with the trading date.
- Comprehensive: Cover all major price-driving categories.
- Unbiased: Maintain balanced sentiment and tone.
- Diverse: Incorporate multiple independent sources.

**2. Rules and Scoring**

- Rule 1: Date Accuracy – Ensure all articles correspond to the correct trading date.
  - 0 = Not aligned – multiple off-date items.
  - 1 = Mostly aligned – minor off-date presence.
  - 2 = Fully aligned – all sources match the target date.
- Rule 2: Coverage of Key News Drivers – Include all major asset-specific developments.
  - 0 = Very limited – one category only.
  - 1 = Partial – two to three categories.
  - 2 = Comprehensive – all four key drivers.
- Rule 3: Bias Awareness – Evaluate sentiment balance across sources and summaries.
  - 0 = Skewed – one-sided sentiment.
  - 1 = Moderate – partial balance.
  - 2 = Balanced – neutral overall tone.
- Rule 4: Source Diversity – Verify multi-outlet representation.
  - 0 = Low diversity – one outlet dominant.
  - 1 = Moderate – two to three outlets.
  - 2 = High diversity – four or more outlets.

## 附录 B 智能体执行协议细节

**提示（原文标题为 Prompt For Summarization，内容为交易决策提示，保留原文）**

```text
You are a professional financial decision-making agent spe-
cialized in quantitative and fundamental reasoning with
a daily trading frequency. Your primary task is to analyze
the reasoning outputs of other agent roles and integrate
their insights into a unified, evidence-based conclusion.

Based on your analysis and the provided definitions, deter-
mine the most appropriate trading decision for the target
asset [ASSET] given its current market price [PRICES]and
contextual signals.

Your possible actions are defined as follows:
- Buy: Indicates a bullish outlook or perceived undervalu-
ation, suggesting the asset price is likely to rise. And you
choose to be in long position.
- Sell: Indicates a bearish outlook or perceived overvalu-
ation, suggesting the asset price is likely to fall. And you
choose to be in short position.
- Hold: Indicates market uncertainty or equilibrium, sug-
gesting no immediate trading action. And you choose to
go flat position.

Return your final output strictly in the following format:
[Decision]: Buy / Sell / Hold
```

**系统提示定义（System Prompt Definition）。** 每个智能体在一个结构化的系统提示下运行，该提示定义了它的分析目标与推理行为。提示引导模型整合多源金融信息，产生一致且可解释的交易决策。具体而言，智能体被指派如下角色与任务。这一设计保证了跨智能体、跨骨干的可解释性与可复现性。为保持一致与公平，所有基于 LLM 的智能体共享完全相同的生成设置，包括 temperature、top-p 与最大 token 长度，详列如下。

**超参数。** 表 2 总结了 DeepFund 使用的关键参数。这些参数控制模型随机性、重试行为、数据覆盖与决策记忆。所有设置在评估期间保持固定，以保证跨模型、跨运行的公平比较。

译注：原文此页含模板占位的收稿日期行（Received 20 February 2007; revised 12 March 2009; accepted 5 June 2009），属排版占位内容。

**表 2：DeepFund 参数设置。（原文第 12 页）**

| Parameter | Default Value | Usage |
|---|---|---|
| LLM temperature | 0.5 | Controls randomness of the LLM inference. |
| Retry times | 3 | Number of retries for LLM inference if the LLM do not give correct response. |
| Warm-up windows | 90 | Trading days that used to initialize the agents. |
| Decision memory size | 7 | Number of past recent actions and price history for decision-making. |

## 附录 C 表现分析接口

为实现对实盘交易行为透明且可复现的评估，我们为 AMA 构建了一个交互式网页监控界面（图 5–6）。该平台允许用户实时观察、分析与比较 LLM 驱动交易智能体的表现。

**总览仪表盘（Overview Dashboard）。** 主界面（图 5）聚合了实时市场条件下所有智能体的表现，显示核心指标，包括总余额、累积收益（含/不含费用）、Sharpe 比率与胜率。智能体按收益动态排名，而自动刷新机制（默认每 30 秒）保证与实时市场数据流同步。用户可以快速识别表现领先的智能体，并下钻查看详细的表现轨迹。

筛选面板支持四个正交维度：

- Agents：TradeAgent、InvestorAgent、HedgeFundAgent 与 DeepFundAgent。
- Assets：如 BTC、ETH、TSLA 与 BMRN，覆盖金融与加密两个市场。
- Models：包括 GPT-4.1、GPT-4o 等骨干。
- Strategies：如 Baseline、Flip on Reversal 与 Pyramid Exit，支持自定义评估模式。

这一多轴筛选框架允许在模型架构、市场领域与交易策略之间灵活比较。

**收益曲线对比视图（Equity Comparison View）。** 第二个界面（图 6）引入了一个用于跨智能体收益分析的交互式可视化模块。用户可以选取智能体、资产与 LLM 模型的子集，渲染出代表组合随时间增长轨迹的同步收益曲线。每条线表示一个智能体—模型组合（例如 InvestorAgent-BTC-GPT4o），动态 tooltip 显示每日余额、模型类型与策略。

这一设计使得可以在相同的市场信号下，细致地目视检查相对表现动态、稳定性与分化模式。研究者因此可以考察智能体在波动容忍度、恢复行为与决策一致性上的差异，为表格指标提供直观补充。

**分析效用。** 两个界面合在一起，既提供宏观快照，也提供微观分析视图：

- 总览仪表盘便于对实盘智能体做纵向跟踪与排名。
- 收益曲线对比视图支持时间维度与智能体间分析，用于理解决策稳健性。

通过整合这些视图，系统让研究者能够在持续演进的市场环境中，系统地评估智能体架构、LLM 骨干与策略适应性之间的相互作用。

图 5：Agent Market Arena 仪表盘（总览视图）。该界面提供统一视图，用于监控、比较与分析基于 LLM 的交易智能体在资产、模型与策略上的实时表现。（原文第 12 页）

图 6：收益曲线对比视图。用户可以选定特定的智能体、资产与模型，可视化对比收益曲线，从而对表现动态做多维度评估。（原文第 12 页）
