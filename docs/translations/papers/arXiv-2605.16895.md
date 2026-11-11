# Alpha 幻觉：LLM 交易智能体报告的 Alpha 不应被当作部署证据（The Alpha Illusion: Reported Alpha from LLM Trading Agents Should Not Be Treated as Deployment Evidence）

> 来源：https://arxiv.org/abs/2605.16895
> 原文：docs/papers/arXiv-2605.16895.pdf
> 翻译日期：2026-11-11 ｜ 范围：全文 ｜ 方式：机器翻译初稿，未经人工校对
> 引用于：docs/literature/W5-real-eval-fault-style.md

## 目录

- 摘要
- 1 引言
- 2 报告的 Alpha 尚不构成部署证据
  - 2.1 正面的智能体结果说明了什么、又没有说明什么
  - 2.2 时间污染：当回测衡量的是记忆而非预测
  - 2.3 现实摩擦：更好的预测不意味着更高的净收益
  - 2.4 短窗口与搜索空间：高 Sharpe 不会自动成立
- 3 从评估混淆到结构性错配
  - 3.1 语言置信度不是可交易的概率
  - 3.2 金融叙事能力不是数值执行
  - 3.3 参数先验：未披露的隐式因子暴露
  - 3.4 为什么常见补丁单独不能解决问题
- 4 面向部署主张的最小证据协议
- 5 一种模块化替代方案：LLM 作为可审计的信息接口
- 6 另类观点、反对意见与局限
- 7 结论
- 参考文献（从略）
- 附录 A 三个 LLM 交易系统报告的逐标的 Sharpe
- 附录 B 摩擦覆盖度与复现的逐资产指标
- 附录 C 代表性系统的反例与分类
- 附录 D 参数先验锁定：详细的同侧证据
- 附录 E 实例：贯穿模块化流水线的 8-K 指引削减

## 摘要（Abstract）

端到端 LLM 交易智能体已经迅速从研究者的好奇心，变成一个由具名系统构成的小生态，包括 FinCon、FinMem、TradingAgents、FinAgent、QuantAgent 与 FLAG-Trader。其中若干系统报告的头条 Sharpe 比率，如果在部署端的交易桌上被照字面当真，将会是有分量的数字；相关基准（如 FinBen）报告的交易任务 Sharpe 统计量也落在同一区间。在学术界与产业界的分界两侧，架构研究与部署主张之间的鸿沟都被跨越得过于随意。我们对这一鸿沟表明立场：端到端 LLM 交易智能体所报告的 alpha 不应被当作部署证据。

在这些收益能够支撑「可部署交易能力」的主张之前，它们必须先通过一系列结构性效度检验：时间完整性、现实摩擦、反事实稳健性、预测校准、数值执行，以及多智能体去聚合（multi-agent disaggregation）。当前的公开证据还无法把稳健的预测能力与时间污染、未建模摩擦、短窗口 Sharpe 不确定性、叙事拟合（narrative fitting）以及参数先验区分开来。

这个问题不只是评估层面的，也是结构性的。语言上的置信度不是可交易的概率，叙事式的推理不是数值执行，而模型先验可能变成未披露的隐式因子暴露。我们提出一套最小报告协议 P1–P6，按主张强度分层适用，并给出一个保守的模块化替代方案：把 LLM 用作独立的校准、风险与执行模块上游的、可审计的信息接口。代码与复现工具：https://github.com/hj1650782738/Trading

## 1 引言

端到端 LLM 交易智能体处在两个评估话语已经渐行渐远的社群的交点上。量化交易产业问的是一个部署问题：一个语言模型智能体能否在实盘执行下产生净收益？学术界在过去两年里走向了另一个同样有效的方向——探索新架构、扩展设计空间。NeurIPS 2024 主会接收了 FinCon [30]（带组合决策的经理—分析师层级结构）；连同 FinMem [29]、TradingAgents [25]、FinAgent [33]、QuantAgent [27] 与 FLAG-Trader [28]，这批工作最好被读作探索性的架构研究，而这正是一个快速演进领域应有的姿态。

基准测试一侧也在并行推进：FinBen [26] 是 NeurIPS 2024 Datasets and Benchmarks Track 上的综合性金融 LLM 基准（36 个数据集、24 个任务），它报告了一个 FinTrade 子任务的 Sharpe，我们在后文将其用作评估锚点，而不是交易框架。从基准到部署的鸿沟本身就是已知的 ML 病理：Lipton 与 Steinhardt [12] 系统梳理了宽松评估、叙事膨胀、指标—机制混淆如何在各个子领域反复出现，而交易正是这种混淆最具体的地方。

困难出现在下游一步。因为没有任何共享的边界把「探索性架构」与「可部署系统」分开，读者有时会把短期、截断内回测的头条数字，连同单一成分的成本模型，当作部署证据向前传递。当产业尝试部署并发现这道鸿沟时，反应又会过度矫正为「学术界的 LLM 交易工作不可信」，两个社群便不再以正确的前提互相阅读：谨慎的探索性贡献被贬低，产业则认为学术界不接地气。

这种混淆有具体的形态：一个听起来合理的投资叙事不是可交易的概率；一段短期正收益不是稳健的 alpha；一条多智能体辩论流水线也不是独立专家的聚合。在排除训练语料污染、未计入的摩擦、短样本显著性、失准校准、数值执行错误与参数先验暴露的协议缺席之下，可回测但不可部署的智能体以「高 Sharpe」的标题进入文献，而团队带着失准的预期来到真实市场。

我们的论点是：在通过结构性效度检验之前，端到端 LLM 交易系统所报告的 alpha 不应被解读为可部署交易能力的证据。这一立场并不否认 LLM 在金融中的价值；同侧最强的证据 [16] 表明，LLM 能从新闻标题中提取与短期市场反应相关的语义信号，而这正是我们所支持的 LLM 模块化用法。当证据不足以支撑部署式解读时，更稳妥的设计是让 LLM 通过独立的校准、风险、执行与审计模块进入交易流水线，而不是直接承担最终的交易决策。

我们的目标是捍卫学术界的探索性角色，而不是监管它。我们有三项贡献：(i) 我们把时间污染、摩擦、多重检验、失准校准、数值执行与参数先验问题，统一进一个「报告的 alpha 不是部署证据」的框架；(ii) 我们提出按主张强度分层的最小报告协议 P1–P6，给作者、审稿人与部署团队一把共同的标尺；(iii) 我们描述一种保守的模块化实践——LLM 作为独立校准、风险与执行模块上游的可审计信息接口。本文的焦点是证据性的，不是新的策略或基准。
## 2 报告的 Alpha 尚不构成部署证据

端到端 LLM 交易系统的现有结果不应被一笔抹杀：它们报告的收益首先应被理解为历史回测或原型证据，而不是部署证据。一段短期的正向轨迹不会自动意味着可迁移、可审计、可部署的交易能力；报告的 alpha 必须首先排除三个混淆因子：时间污染、现实摩擦与研究者自由度（researcher degrees of freedom）。

### 2.1 正面的智能体结果说明了什么、又没有说明什么

这些系统探索了不同的工程形态——分层记忆、分析师/交易员/风险角色层级、多模态摄入、经理—分析师 CVaR 风险控制、HFT 风格的指标/形态/趋势智能体，以及带 Sharpe 增量奖励的 PPO 微调——并让「LLM 能否直接交易」成为一个有意义的问题。但已发表的评估建立在短期的、针对特定提示的窗口上，发表时的头条数字一律很强（各系统窗口与逐标的 Sharpe 摘要见附录 A、图 3；FinCon [30] 达到逐标的 Sharpe 2.37、组合 Sharpe 3.27；QuantAgent 报告 HFT bar 上 50.7–63.7% 的方向准确率）。

这些数字证明的是「在给定协议下存在一条正收益轨迹」，而不是部署级的 alpha（截断之后、point-in-time、动态股票池、全摩擦）。在 Chen 等人 [2] 的无污染真实市场评估中，一旦控制了时间泄漏与执行真实度，多数 LLM 智能体难以持续跑赢被动的买入并持有。

### 2.2 时间污染：当回测衡量的是记忆而非预测

时间污染是 LLM 交易评估比传统量化回测更难的地方。传统的前视偏差（look-ahead bias）通常来自显式的数据错误——使用未来价格、未来盈利修正，或事后的指数成分。但 LLM 的污染可以更隐蔽：即便实验代码只喂入当下可见的信息，模型权重、后训练数据或检索语料也可能已经吸收了事件之后的新闻、市场复盘、价格路径摘要与年终回顾。模型无需显式访问未来价格，就能通过语义记忆泄漏未来信息。

最直接的定量锚点是 Li 等人 [11]：比较 LLM 交易智能体在预训练截断之内与之外的表现，一旦窗口越过截断点，FinMem 的总收益下降约 71.85%、QuantAgent 的 Sharpe 下降约 51.48%，从而直接量化了报告 alpha 中的污染成分。Merchant 与 Levy [19] 用 Divergence Decoding 在机制上佐证了这一点，它在推理时剥离未来的语义记忆——这支持了一个更根本的主张：污染不只是提示或检索时间戳的问题，它可能已经进入模型参数与语义关联。

污染问题也朝相反方向起作用。Shah 等人 [23] 表明，即便在所报告的截断之内，LLM 的金融知识也随公司规模与时近程度急剧偏斜——LLM 对 2017 年大盘股的营收问题回答准确率为 54.17%，而 1995 年只有 6.32%，且规模更大、时近程度更高的公司幻觉率上升；Kang 与 Liu [9] 在更广泛的金融领域记录了同样的事实性幻觉模式。因此，在一个近期的、以超大盘股为主的窗口里做强回测是双重脆弱的：它既可能通过语义记忆泄漏未来信息，又可能建立在真实部署同样必须处理的更小或更古老公司的知识缺口之上。

两个方向指向同一结论：LLM 的金融知识不是 point-in-time 可靠的。因此我们主张：截断之后且无污染的评估不是加分项，而是最低前提。如果一个端到端 LLM 交易系统只在模型知识截断之内、或在污染状况不明的条件下表现良好，更可信的解读是「回测表现可能包含历史语义记忆」，而不是「模型学会了预测市场」。

### 2.3 现实摩擦：更好的预测不意味着更高的净收益

交易系统最终由净收益来评判——不是解释质量、方向准确率，或毛收益曲线。任何从毛到净的转换都遵循一个最小分解：

$$\mathrm{PnL}_{net} = \mathrm{PnL}_{gross} - \sum_{t} \left( c \cdot |\Delta w_t| + s_t \cdot |\Delta w_t| + \kappa \cdot |\Delta w_t|^{\beta} \right) \tag{1}$$

其中 c 是佣金，$s_t$ 是 t 时刻的买卖价差，κ 与 β 刻画临时市场冲击（在标准 Almgren 与 Chriss [1] 设定下 β ≈ 1），订单簿弹性与执行成本动态则由 Obizhaeva 与 Wang [21] 建模。这个分解是描述性的，不是可选的：每一项都必须被估计、扣除并审计，否则所报告的毛 PnL 与可部署净 PnL 之间的缺口就始终存在。

对于多智能体 LLM 系统，右端还必须加上 token 成本与推理延迟；收益不仅被市场摩擦侵蚀，也被系统自身的推理成本侵蚀。Jang 等人 [7] 提供了一个直接的反例：经过强化学习训练后，BTC 市场状态分类准确率显著提升，但模拟交易下的累积收益反而下降——这正是公式 (1) 的核心含义：优化毛收益一侧的代理量（分类准确率、更锐利的方向、更连贯的理由、更长的辩论），并不会优化公式 (1) 净收益一侧的现实。

在 FinMem、TradingAgents、FinAgent、FinCon 与 QuantAgent 之间，40 个「系统 × 摩擦成分」单元中有 35 个未被建模（覆盖矩阵见附录 B、图 4）；因此所报告的毛 Sharpe 是任何可部署净 Sharpe 的上界。图 1 以 TradingAgents 与 QuantAgent 的一年期、五标的复现为这一缺口定锚：在计入佣金、token 成本、价差与市场冲击（完整设定见附录 B）后，组合 Sharpe 对 TradingAgents 从 0.43 降到 0.22，对 QuantAgent 从 −0.96 降到 −1.15，两个智能体最终都低于买入并持有。

在多智能体辩论场景中，成本吃掉收益的问题变得更加系统性：Zhang 等人 [32] 报告，在 36 种配置（4 个模型 × 9 个基准）中，多智能体辩论的胜率不到 20%，而且增加轮次或智能体不会改善表现——反而可能使其退化。

图 1：TradingAgents（TA）与 QuantAgent（QA）相对买入并持有（B&H）的一年期复现（TSLA/NVDA/KO/XOM/MSTR 等权，起始 $100K）。「净额（Net）」计入佣金、token 成本、价差与市场冲击；「毛额（Gross）」是扣摩擦前的轨迹。设定与逐资产拆解见附录 B。（原文第 2 页）

### 2.4 短窗口与搜索空间：高 Sharpe 不会自动成立

第三个混淆来自短期窗口估计与研究者自由度。许多 LLM 交易论文在几个月或单一年度的窗口上报告高 Sharpe 比率、高累积收益，或相对基准的显著超额表现。但金融计量经济学文献早已确立，短窗口的 Sharpe 估计带有相当大的不确定性，而对候选信号、规则集与窗口选择的反复搜索会推高假阳性率。

Lo [15] 给出 Sharpe 标准误近似：

$$SE(SR) \approx \sqrt{\frac{K + SR^{2}/2}{T}} \tag{2}$$

其中周期 Sharpe 取 K = 1，按日频年化的 Sharpe 取 K = 252；除非论文披露它们采用哪种约定，否则头条 Sharpe 在系统之间不可比。不确定性恰恰在头条最讨喜的区域——小 T、大 SR——最大。图 2 画出了由此得到的 95% 置信区间半宽，并叠加了有代表性的 LLM 交易头条；FinBen GPT-4 FinTrade 的 Sharpe 为 1.51 ± 1.08（标准差超过均值的一半）[26] 落在同一象限，因此标准误常常大于系统之间的典型差距。

研究者自由度让问题更糟。传统量化策略在因子定义、回看窗口、调仓频率、交易成本假设与组合权重上都有自由度；LLM 系统还额外加上模型版本、temperature、系统提示、few-shot 示例、RAG 语料、记忆长度、智能体人设、辩论轮次、输出解析规则与工具调用策略。实证资产定价文献已经表明，即便在纪律严明的 ML 流水线下，月度个股层面的 R² 很少超过约 0.4%，组合层面的 R² 约 1–2% [3]；面对这一天花板，跨数十年的 factor-zoo 工作 [5] 早已主张用接近 3.0 的 t 统计量门槛来控制多重检验。Novy-Marx 与 Velikov [20] 证明，LLM 可以用来从三万多个候选信号中筛选并产出完整论文，并警示工业化的 HARKing。

图 2：Lo [15]（式 2，K=1）下周期 Sharpe 的 95% 置信区间半宽热图，横轴 c ∈ [0, 8]、纵轴 T ∈ [20, 500] 个交易日观测。虚线标出 95% 置信区间恰好覆盖零的位置。叠加的 TradingAgents、FinMem、FinAgent 与 FinCon [30] 头条 Sharpe 仅为示意（FinCon：单股 NFLX 2.37，最优组合 (TSLA, MSFT, PFE) 3.27）；QuantAgent 因报告的是 HFT 方向准确率而非日频 Sharpe 而被略去。年化头条使用 K=252 的式 2。这些叠加用于说明报告不确定性，而非对原论文置信区间的重新估计，因为原文的 Sharpe 约定并不总是可比。（原文第 5 页）

## 3 从评估混淆到结构性错配

对第 2 节一个自然的反驳是：更严格的截断后数据、完整的摩擦建模与统计检验可以解决一切。更好的评估纪律是必要的，但不充分：端到端 LLM 交易仍面临三个结构性错配——语言置信度不是可交易的概率；金融叙事能力不是数值执行；模型权重中的参数先验可能变成未披露的隐式因子暴露。

### 3.1 语言置信度不是可交易的概率

交易系统需要的不是「听起来合理」的解释，而是一个可校准、可定规模、受风险约束的概率对象。仓位规模、止损阈值、风险预算与组合优化都依赖某种条件概率或条件收益分布。相比之下，LLM 的自然输出来自语言空间上的 next-token 分布，其优化目标是在语料分布下产生更可能、更连贯、更符合偏好的文本。语言空间上的置信度与金融收益空间上的条件概率不是同一个对象。

校准（calibration）是这一区分的可量化形式。Kadavath 等人 [8] 表明，LLM 对自身答案的自我报告置信虽然并非没有信息量，但系统性地失准，并且在分布外输入上急剧退化——任何把口头置信灌入交易规模的系统都会直接继承这一模式。Guo 等人 [4] 提出了被广泛使用的期望校准误差：

$$ECE = \sum_{m=1}^{M} \frac{|B_m|}{n} \left| acc(B_m) - conf(B_m) \right| \tag{3}$$

其中 $\{B_m\}_{m=1}^{M}$ 按预测置信把样本划分成 M 份。ECE 度量「声称的概率」与「经验频率」之间的加权平均距离；任何把 LLM 的自我报告置信当作仓位输入的系统，都隐含地承诺了 ECE ≈ 0，而这一承诺必须被独立测量，而不是靠语气来证实。

Guo 等人 [4] 的发现来自判别式图像分类器，因此这里的跨域外推是间接的（方向一致，但证据取自不同领域）；金融领域有同侧实证，最直接的是 Lee 等人 [10] 的反事实干预——即便显式呈现反向证据，自我报告的模型置信与方向翻转行为也并不严格一致。我们的主张不是 Guo 等人 [4] 直接证明了 LLM 交易的失准校准，而是任何把口头置信转换成仓位规模的系统都会继承一项可测量的校准义务。Shen 等人 [24] 把下游一侧形式化：喂给决策算法的预测中的校准误差，会转化为所诱导动作的有界次优性，从而使校准成为任何建立在预测分布之上的决策规则的前提。

### 3.2 金融叙事能力不是数值执行

第二个错配是叙事推理与数值执行之间的鸿沟。LLM 能解释复杂的金融概念——期权收益结构、宏观事件影响、资产负债表变化、板块轮动逻辑，或一个交易策略的直觉。但交易系统最终执行的是数值运算：计算风险敞口、估计波动率、处理现金流、控制杠杆、满足组合约束、设置止损与拆分订单。

TraderBench 把这一差距操作化：它把金融智能体放进静态知识任务、分析推理任务、期权交易与对抗性加密交易场景，并用可实现的指标来评估，包括 Sharpe、收益、回撤、P&L、Greeks 与风险管理 [31]。其公开摘要显示，扩展思考（extended thinking）显著改善检索类任务，但对交易表现几乎没有帮助；在期权任务中，模型表现出明显的概念与计算之间的鸿沟——它们能识别策略或解释概念，却难以精确量化 P&L、Greeks 与风险敞口。

Ma 等人 [18] 提供了一个互补的同侧锚点：在一个带买卖盘互动的虚拟零和股市中，LLM 智能体在纯文本的数值推理上很吃力——当同一数值状态以图表而非文本呈现时，它们的表现明显更好，这表明瓶颈在数值执行而不在金融词汇。这正是我们的要点：流利地谈论金融，不等于在真实交易约束下正确地计算它。FinToolBench [17] 进一步表明，金融工具的使用必须在金融关键维度上评估，例如调用级合规、时效、意图对齐与领域对齐，而不是只看二元的执行成功。因此，我们把工具调用视为必要的安全补丁，而不是充分的架构修复。

### 3.3 参数先验：未披露的隐式因子暴露

第三个错配发生在权重层。LLM 不是金融信息的中性处理器。它的预训练语料包含历史新闻、市场评论、投资叙事、公司覆盖、社交媒体讨论与事后的复盘；偏好优化进一步奖励清晰、有用、解释性、符合人类偏好的回答。这些过程合在一起，会在模型面对金融问题时产生稳定的默认偏好——例如偏向超大盘科技股、叙事上有趣的公司，或主流板块。

我们把它作为一个解释性框架而非已确立的统一机制提出，称为 PARAMETRIC PRIOR LOCK-IN（参数先验锁定）。它指的是：在任何实时输入之前，模型权重已经包含稳定的行业、规模、风格或叙事倾斜；这些倾斜塑造最终的交易推荐，但与传统因子暴露不同，通常不被显式披露、测量或施加风险约束。一个带有科技、超大盘、动量、质量、价值或逆向暴露的传统量化组合，可以通过因子回归、板块中性化与风险模型来测量；而在端到端 LLM 交易系统中，风格偏好可能藏在自然语言推理里，以「看似自主的分析」形态浮出水面。

PPL 允许一个最小的反事实诊断。沿用 Lee 等人 [10]，我们把反向证据强度 ρ ∈ [0, 1] 下的观点翻转率定义为：

$$\phi_{vol}(\rho) = Pr\left[ \hat{a}_{t+1} \neq \hat{a}_{t} \mid e_t, \rho \right] \tag{4}$$

其中 $\hat{a}_t$ 是基线观点，$\hat{a}_{t+1}$ 是在强度 ρ 下用反向证据 $e_t$ 更新后的观点。我们并不主张贝叶斯理性的智能体必须驱动 $\phi_{vol} \to 1$：强反向证据可能理性地要求降低置信或缩小仓位，而不是符号翻转。

我们主张一个更弱的单调性：一个更新良好的智能体应在 (i) 方向翻转率、(ii) 自我报告置信、(iii) 实际仓位规模这三者中至少一个上，随 ρ 增大表现出单调响应；而被参数先验锁定的智能体会在这三条轴上同时违反这一单调性。Lee 等人 [10] 的反事实干预提供了同侧证据；附录 D 展开了关于板块倾斜、跨模型同质性，以及人设提示与多智能体辩论无法消除共享先验的支撑性发现。对交易系统而言，这类倾斜不是普通的文本偏差，而是未披露的隐式因子暴露。

### 3.4 为什么常见补丁单独不能解决问题

四种标准的乐观回应——规模、更长上下文/RAG、工具调用与多智能体辩论——在第 6 节的关注点 2–5 中被逐一讨论；单靠其中任何一个都支撑不了端到端的部署主张，而且从基准到部署的鸿沟并非金融独有：web 智能体与通用 LLM 智能体基准在更长、摩擦更重、对抗性的轨迹下同样表现出高估 [13, 34]，交易只是同一病理在更严苛摩擦下的样子。
## 4 面向部署主张的最小证据协议

我们的主张是：端到端 LLM 交易系统报告的 alpha，在通过结构性效度检验之前，不应被当作可部署交易能力的证据。当一篇论文把交易收益解读为部署就绪的 alpha 或自主交易能力时，它必须承担更重的举证责任。我们提出六个报告协议 P1–P6，并把它们视为必要而非充分的最小筛查：通过 P1–P6 本身并不意味着现实可部署——操作风险、模型治理、订单路由、容量、尾部风险行为与对抗性市场影响仍然是开放的。更确切地说，P1–P6 是一组紧凑的失败模式：以现有证据看，只要违反其中任何一条，就足以否定对所报告数字的部署强度解读。

**表 1：面向 LLM 交易部署主张的六条最小证据协议。每一行是一种单独的失败模式，只要违反它，就足以取消对所报告数字的部署强度解读。证据锚点在第 2–3 节内联列出。（原文第 7 页）**

| Protocol | Failure mode | Minimum reporting | If unmet |
|---|---|---|---|
| **Group A. Evidence-source confounds** | | | |
| P1. Temporal integrity | Time-travel alpha; pretraining or retrieval leakage; semantic future leakage | Model version, knowledge cutoff, post-training boundary, retrieval-corpus timestamps, memory-update rules; at least one post-cutoff or point-in-time window | At most historical-backtest evidence |
| P2. Dynamic universe | Survivorship bias; ex-post-cleaned samples; static universes overstating returns | Time-varying tradable universe; delisting and suspension handling; liquidity filters; index-component changes; borrow and short-sale constraints | Alpha may come from ex-post-filtered universes |
| P3. Counterfactual robustness | Parametric prior lock-in; insensitivity to reverse evidence; implicit sector or style tilts | Direction-flip rate, confidence shift, position-size shift under strong reverse evidence; sector-neutral and style-neutral prompt tests | Recommendations may reflect priors, not information |
| **Group B. Evidence-to-decision-mapping confounds** | | | |
| P4. Epistemic calibration | Language confidence misread as trading probability; uncalibrated self-reported confidence | ECE, reliability curves, regime-conditioned calibration, out-of-sample calibration of any probability or confidence score used in sizing or risk control | LLM confidence should not control sizing |
| P5. Realistic implementation | Gross-alpha illusion; accurate prediction with negative net return; token and latency costs cannibalizing returns | Layered gross-to-net cleansing: spread, slippage, commission, market impact, borrow cost, execution delay, token cost, inference latency | Profits cannot show deployability |
| P6. Multi-agent disaggregation | Multi-agent consensus illusion; correlated errors across same-source models; echo-chamber and groupthink dynamics | Single-agent baseline, role similarity, disagreement rate, debate-round cost, coordination latency, multi-agent net-return delta | Debate is not independent-expert aggregation |

为什么是这六条。P1–P3 控制证据来源混淆（窗口、样本、先验）；P4–P6 控制证据到决策的映射混淆（概率对象、净收益清洗、独立性）。两组无重叠地划分了「证据 → 决策」链条，而且我们把清单限制在 LLM 特有、或被 LLM 显著放大的失败模式上（因子漂移之类的一般金融混淆在传统量化文献中已有充分覆盖）。

分层适用。P1–P6 应按主张强度分层适用：

**表 2：按主张强度分层的协议要求。更强的主张要求严格更强的证据：每一行继承其上一行的协议，右栏显示在该证据下限之下仍然站得住的表述语言。（原文第 8 页）**

| Claim strength | Required protocols | Permissible language |
|---|---|---|
| LLM-as-text-extractor or research aid | P1 (light), P3 (light) | "improves information extraction"; "semantic features have marginal contribution" |
| Historical backtest or prototype | P1 + P2 + P5 (minimum) | "produces a positive-return trajectory in this window"; no deployment language |
| Deployable alpha claim | Full P1–P5 | "retains net return under structural tests" |
| Autonomous trading ability | Full P1–P6 | "retains net return after multi-agent disaggregation" |

参考实现。一个覆盖 P1（截断后窗口）、P2（动态股票池）与 P5（全摩擦清洗）的可复现审计工具——在统一执行模型与图 4 摩擦分类下，对 TradingAgents 与 QuantAgent 做一年期、五标的复现——发布在 https://github.com/hj1650782738/Trading 。逐标的的毛/净指标见附录 B。

## 5 一种模块化替代方案：LLM 作为可审计的信息接口

我们不是在提出一个新框架。本节描述的是当第 4 节的 P1–P6 协议被工程化落实后自然产生的保守模块化实践：LLM 作为可审计的信息接口进入，位于独立的校准、风险与执行模块的上游，而不是作为最终交易决策的权威。这与 Lopez-Lira 与 Tang [16] 一致，他们表明 LLM 能提取与短期市场反应相关的语义信号。

标准量化流水线早已把 alpha 研究、风险建模、组合构建与执行分成带显式接口与审计的独立模块——这种分工早于 LLM，并出现在主动组合管理教材与公开文档化的金融 ML 平台中，例如 FinRL-Meta [14]（它显式地分离数据、环境与智能体层，并把回测规则与风险控制编码为独立组件）。

流水线分六个阶段运行——(1) 信息提取、(2) 特征构建、(3) 信号合成、(4) 概率校准、(5) 规模与风险控制、(6) 执行与审计——其中站得住的 LLM 角色集中在阶段 1（从新闻、公告、电话会中做 schema 约束的提取），并在阶段 5–6 渐变为观察者/解释者的角色；完整的 owner / role / audit-object 分解见附录 E（表 5），其中还以一个 8-K 指引削减为例，把它贯穿阶段 1–6 走了一遍。

仓位层面的含义。LLM 在交易中站得住的角色是可审计的上游接口，而不是最终权威。作者应在提出部署主张之前，先在六个阶段上标出这条边界；审稿人应核查最终权威是否不落在一个未校准的 LLM 手上；部署团队应确保阶段 4–6 由能够覆盖 LLM 输出的独立模块负责。

## 6 另类观点、反对意见与局限

我们的主张是：端到端 LLM 交易系统报告的 alpha，在通过结构性效度检验之前，不应被当作可部署交易能力的证据。第 2–3 节已就技术性反驳做了内联回应；这里我们回应范式层面的反驳，它们同时也是本立场的现实局限——每一处让步都标记出我们的一个子主张，如果反对者在相关 P1–P6 协议下提供了证据，该子主张将被收窄。

**关注点 1。** 我们在打稻草人：多数论文只主张回测表现，而不是部署就绪。
**回应。** 部分正确。我们不争论局部的「研究原型」式表述。我们的靶子是从所报告收益滑向能力语言的那一步——摘要、演讲与下游综述把同一套数字重新包装成「LLM 能交易」。P1–P6 是按部署级主张校准的，不是按研究存在性校准的。

**关注点 2。** 更大的模型、更长的上下文与更强的 RAG 将弥合关键的信息缺口。
**回应。** 部分正确。这些改进主要作用于输入层；它们不会自动产生可校准的收益概率、可审计的仓位控制，也不会移除模型权重中的行业/规模/风格先验。Merchant 与 Levy [19] 指出，仅靠 RAG 与提示限制并不能消除预训练的语义记忆。如果在一个预先指定的截断后区间、跨越多种市场状态下，规模 + RAG 同时改善 ECE 与净收益（P1、P4），我们 3.1 节的子主张就应被收窄。

**关注点 3。** 集成与多智能体辩论可以抵消单模型偏差。
**回应。** 只有当误差来源足够独立时才部分正确。Zhang 等人 [32] 报告 36 种配置下辩论胜率低于 20%，Henning 等人 [6] 表明头条的多智能体增益在不同模型族与随机种子上不能稳定复现；AMA 实盘交易基准 [22] 进一步发现，在相同执行规则下主导结果差异的是智能体架构而非骨干模型选择——「再加一个 LLM 智能体」不等于「加一个独立专家」。声称多智能体改进的作者必须报告单智能体消融、角色相似度、分歧率，以及在控制同质性与协调成本之后的净收益增量（P5、P6）。

**关注点 4。** LLM 确有金融语义价值，因此端到端方法未必失败。
**回应。** 正交——语义价值 [16] 支持第 5 节的模块化实践，而不是直接的端到端部署。如果 LLM 派生的情绪确实有预测力，它应当以特征的形式进入下游模型，并伴随消融、校准与扣摩擦后的验证。

**关注点 5。** 工具调用与强化学习微调已经改变了架构。
**回应。** 部分正确。FLAG-Trader [28] 用 PPO 与 Sharpe 增量奖励微调了一个 135M 的 LLM，并报告在一小批标的上跑赢买入并持有。我们把它视为工程进展，而非反驳：已发表的评估尚未同时满足 P1（截断披露）、P5（全摩擦清洗）与 P3（反事实稳健性）。决定性的问题是最终决策权威是否仍掌握在一个未被独立校准的 LLM 手中；如果未来的修订通过 P3–P5，我们第 3 节的子主张就应被收窄。

**关注点 6。** P1–P6 对早期原型过于严格。
**回应。** 正确——表 2 按主张强度对要求分层。原型只需避免部署语言；早期论文可以报告正收益轨迹，只要它不被晋升为「可部署 alpha」。

层级可证伪性。子主张层面的修订条件：(i) 在预先指定的截断后区间上、跨越市场状态的显著扣摩擦净收益，收窄第 2 节；(ii) 用于定规模的、经校准的 LLM 置信（预先指定的 ECE），收窄 3.1 节；(iii) 控制同质性与协调成本后的显著多智能体净收益增量，收窄关注点 3。

## 7 结论

端到端 LLM 交易智能体这两年的轨迹，在其自身尺度上是富有成果的：它逼出了关于语言模型在被要求产生可下单决策时如何表现的具体问题，由此得到的架构目录也有真实的研究价值。问题始于这种探索性进展被报告为部署进展——短期、截断内窗口的头条 Sharpe 数字被带进摘要、演讲与后续综述，仿佛它们已经回答了部署问题。

我们的论证狭窄但具体。公开证据还无法把稳健的预测能力与时间污染、未建模摩擦、短样本噪声、叙事拟合与参数先验区分开来；而且即便每一步评估都被清洗干净，三个结构性鸿沟仍然存在——语言置信度不是可交易的概率，叙事能力不是数值执行，模型先验可能变成未披露的隐式因子暴露。P1–P6 与模块化替代方案不是新框架，而是让读者分辨一篇论文提供的是哪一类证据——历史回测、原型、可部署主张，或自主交易能力——的最小记账，并让审稿人把每一级主张对应到它的证据下限上。

我们并不打算监管学术文献；它所做出的探索性贡献是真实的、值得捍卫的。我们只是主张让它以正确的范围说话。回测就是回测，原型就是原型，部署主张就是部署主张。在报告的 alpha 通过第 4 节的结构检验之前，把它读作探索性证据而非可部署交易能力是更诚实的读法——而第 5 节的模块化实践，正是让 LLM 继续进入交易系统、却不作为交易权威最终来源的路径。

## 参考文献（从略）
## 附录 A 三个 LLM 交易系统报告的逐标的 Sharpe

供参考，图 3 给出四个采用可比 Sharpe 报告方式的 LLM 交易系统所报告的标的级头条 Sharpe 比率。QuantAgent [27] 被略去，因为它报告的是 HFT 工具上的方向准确率与短期相对超额收益，而不是日频 Sharpe。

图 3：四个 LLM 交易系统的（系统 × 标的）报告 Sharpe。柱子显示 FinMem（6 个月，2022 年 10 月–2023 年 4 月）、TradingAgents（3 个月，2024 年 1–3 月）、FinAgent（7 个月，2023 年 6 月–2024 年 1 月）与 FinCon [30]（8.5 个月，2022 年 10 月–2023 年 6 月）所报告的头条 Sharpe。除 FinAgent 只建模佣金外，所有数字均为扣摩擦前的毛值。（原文第 12 页）

## 附录 B 摩擦覆盖度与复现的逐资产指标

**各系统之间的摩擦覆盖度。** 图 4 把八个标准成本成分映射到五个有代表性的端到端 LLM 交易框架上。只有佣金被全部五个系统显式建模；市场冲击、延迟、滑点、融资、税费与 token 成本在多数系统中缺失——40 个「系统 × 摩擦」单元中有 35 个未被建模。

图 4：FinMem、TradingAgents、FinAgent、FinCon 与 QuantAgent 在八个标准成本成分上的摩擦建模覆盖度。（原文第 13 页）

**经验复现的逐资产拆解。** 表 3 报告了图 1（2.3 节）组合曲线背后的逐资产指标。设定相同：一年期回测，2025-01 至 2026-01，初始资金 $100K，等权五标的组合（TSLA/NVDA/KO/XOM/MSTR）；净额计入佣金、token 成本、价差与市场冲击。合计来看，买入并持有最终为 $104.8K；TradingAgents 为 $106.4K 毛 / $102.3K 净；QuantAgent 为 $81.4K 毛 / $77.9K 净。

**表 3：复现工具得到的逐资产毛/净日频交易指标。CR：累积收益；SR：Sharpe 比率；MDD：最大回撤；下标 g/n：毛/净。净额列计入佣金、token 成本、价差与市场冲击。TCost 列只报告佣金成分（token 成本在组合层面摊销）。Buy&Hold 的净额扣除了一次性进场成本；TCost 因显示需要而省略。（原文第 13 页）**

| Asset | Agent | CRg (%) | SRg | MDDg (%) | CRn (%) | SRn | MDDn (%) | TCost ($) |
|---|---|---|---|---|---|---|---|---|
| TSLA | Buy&Hold | +9.61 | 0.45 | 49.41 | +9.56 | 0.45 | 49.44 | - |
| TSLA | TradingAgents | -2.01 | 0.23 | 55.50 | -10.17 | 0.09 | 58.33 | 1,632 |
| TSLA | QuantAgent | -26.07 | -0.32 | 49.68 | -29.12 | -0.38 | 51.42 | 609 |
| NVDA | Buy&Hold | +37.16 | 0.85 | 41.62 | +37.11 | 0.85 | 41.64 | - |
| NVDA | TradingAgents | +16.32 | 0.59 | 29.66 | +11.49 | 0.48 | 30.34 | 967 |
| NVDA | QuantAgent | -56.07 | -1.79 | 56.07 | -59.30 | -1.91 | 59.28 | 646 |
| KO | Buy&Hold | +12.82 | 0.76 | 11.24 | +12.77 | 0.76 | 11.25 | - |
| KO | TradingAgents | -10.84 | -0.87 | 17.89 | -17.17 | -1.42 | 22.34 | 1,265 |
| KO | QuantAgent | -2.64 | -0.08 | 13.94 | -7.04 | -0.36 | 16.80 | 878 |
| XOM | Buy&Hold | +12.75 | 0.58 | 16.42 | +12.70 | 0.58 | 16.43 | - |
| XOM | TradingAgents | +11.26 | 0.55 | 16.39 | +10.71 | 0.54 | 16.40 | 111 |
| XOM | QuantAgent | -28.29 | -1.49 | 36.87 | -31.57 | -1.67 | 39.58 | 657 |
| MSTR | Buy&Hold | -48.26 | -0.59 | 65.69 | -48.31 | -0.59 | 65.71 | - |
| MSTR | TradingAgents | +17.41 | 0.62 | 52.16 | +16.89 | 0.61 | 52.48 | 105 |
| MSTR | QuantAgent | +20.15 | 0.61 | 44.96 | +16.62 | 0.56 | 46.35 | 707 |

**是什么吃掉了毛与净之间的差距。** 两条智能体曲线的毛—净距离，就是公式 (1) 中各项的累积和；我们实际计入的子集——佣金、token 成本、价差与市场冲击——把 TradingAgents 在 TSLA 上的 CRg = −2.01% 变成 CRn = −10.17%，把 KO 上的 CRg = −10.84% 变成 CRn = −17.17%。净额的买入并持有仍在 5 个标的中的 4 个上击败两个智能体；唯一的例外是 MSTR，那里买入并持有本身回撤了 −48.31%。

这些数字佐证了 2.3 节的核心判断：所报告的毛 Sharpe 是上界，不是一个可部署的数字。第 2.4 节的 Sharpe 不确定性论证进一步强化了同一结论——在一年（约 252 个交易日观测）之内，智能体净 Sharpe 的 95% 置信区间半宽大到足以覆盖买入并持有与智能体之间的全部差距。

## 附录 C 代表性系统的反例与分类

我们按各系统/论文与本论题的关系分类：(a) 表面冲突但可由 P1–P6 解释；(b) 与本论题相容；(d) 接近模块化方案且具支持性。在公开证据中，我们尚未发现一个确定的 (c) 类挑战反例；一旦发现，它将触发层级可证伪性条件。

**表 4：代表性系统及其与论题的关系。（原文第 14 页）**

| System or paper | Class | Note |
|---|---|---|
| FinMem [29] and TradingAgents [25] | (a) | Report short-window positive returns but lack P1 (cutoff), P5 (cleansing), and P6 (disaggregation); fits Section 2.4 |
| FinCon [30] (NeurIPS 2024 main) | (a) | manager–analyst multi-agent + conceptual verbal reinforcement; per-ticker Sharpe 0.335–2.370, portfolio Sharpe up to 3.269; OOS window Oct 2022 – Jun 2023 still constrained by P1 cutoff and P5 cleansing |
| FinAgent [33] | (a) | Multimodal inputs and tool calls but only deducts commission inside reward; remaining frictions unmodeled—see Figure 4 |
| QuantAgent [27] | (a) and (d) | Reports headline Sharpe 1.76–2.02 on HFT instruments—surface-level a counterexample to our thesis. On inspection, the architecture is mostly modular: the LLM emits structured reasoning over Indicator/Pattern/Trend/Risk roles, while execution and the 5 bp stop-loss are off-LLM components. We therefore read it as already approximating the modular boundary advocated in Section 5, with residual P1 (cutoff disclosure) and P5 (full-friction net) gaps as the remaining deployment-evidence gaps |
| FLAG-Trader [28] | (a) | RL fine-tune of a 135M LLM with PPO actor–critic and Sharpe-increment reward; reports SR ≈ 1.36–1.73 on a small ticker set + BTC, but evaluation lacks explicit cutoff disclosure (P1) and friction cleansing beyond commission prompt mention (P5) |
| FinBen [26] (NeurIPS 2024 D&B) | (b) | Holistic benchmark over 36 datasets and 24 tasks; GPT-4 FinTrade Sharpe 1.51 ± 1.08 (std exceeds half the mean) is a direct anchor for P1 + P5 |
| FinRL-Meta [14] | (d) | Already adopts modular division of labor, consistent with the inductive practice of Section 5 |
| Merchant and Levy [19] (Divergence Decoding) | (b) | Mechanistic anchor for P1: shows look-ahead bias is embedded in model parameters, supporting our argument rather than serving as a counterexample |

## 附录 D 参数先验锁定：详细的同侧证据

本附录展开第 3 节单调性主张背后的同侧证据。Lee 等人 [10] 的反事实干预展示了与 PPL 相关的三种模式：

- 即便显式给出反向证据，模型仍固守既有的板块倾斜与风格叙事——观点翻转率保持在低位，自我报告的置信并不成比例地收缩。
- 来自同一生态、预训练语料或对齐范式的模型，表现出高度趋同的板块与主题偏好，这表明该先验为那些本应被当作「独立」的智能体所共享。
- 人设提示、多模型投票与多智能体辩论只产生表面的修辞差异，并不能移除底层的同质先验；因此多智能体的一致性是独立专家一致性的糟糕代理。

**Lee 等人 [10] 的定量锚点。** 跨模型的 Tech-vs-Defensive 偏好分数差距（图 5a）从 0.09（GPT-4.1：0.13 vs. 0.04）到 0.36（Mistral-24B：0.38 vs. 0.02）不等，且对每一个被评估的模型都具有统计显著性（Lee 等人表 1 中独立样本 t 检验 p < 0.001）。在体量翻转率一侧（图 5b），在最对抗的比例 2|3（即 60% 反向证据）下，先验最强的模型（Llama4-Scout）只在约 8% 的情形中翻转观点，而偏见最低的 GPT-4.1 约翻转 30%，相差 3.8 倍，并且该差距随模型自身的板块偏见分数（面板 a）单调增大。在强度驱动的翻转下出现同样的单调对应（Lee 等人图 7）：即便在 ∆ = 10（反向证据声称价格影响是对支持证据的 2 倍）时，高偏见模型仍低于 $\phi_{int} = 0.6$，远低于「完美的理性更新」。面板 (a) 与 (b) 共同说明了为什么把方向翻转率、置信位移与仓位位移作为 P3 的三条单调性轴。

这些模式促使我们把 P3（反事实稳健性）当作核心协议而非可选消融：一个在反向证据提示下推荐不发生移动的系统，无法与一个仅凭参数先验运作的系统区分开来。

图 5：参数先验锁定的两副面孔，改绘自 Lee 等人 [10]。(a) 六个 LLM 在最受偏爱与最不受偏爱板块（Technology vs. Consumer Defensive）之间的板块偏好分数 $\pi_s \in [-1, +1]$；六个模型都表现出正的 Tech 倾斜，且模型内差距具有统计显著性（p < 0.001）。(b) 观点翻转率 $\phi_{vol}$ 作为反向证据占比的函数，读自 Lee 等人报告的体量比例 {0|2, 1|3, 2|4, 1|2, 2|3}，分别对应 {100%, 75%, 66%, 66%, 60%} 的反向证据（为清晰起见，两个 66% 的比例取平均）。在 100% 反向证据下，所有模型都接近 1.0 翻转；在 60% 反向证据下，强先验模型（Llama4-Scout、DeepSeek-V3）几乎不翻转（< 0.15），而面板 (a) 中板块倾斜最强的同一批模型在面板 (b) 中位置最低。这一跨轴对应正是 PPL 的经验证据：更高的潜在先验，转化为反向证据下更黏的后验。（原文第 15 页）

**表 5：模块化量化交易系统的共同阶段结构（第 5 节引用）。（原文第 15 页）**

| Stage | Owner | Reasonable LLM role | Audit object |
|---|---|---|---|
| 1. Information extraction | LLM-led, schema-bound | Extract structured propositions from news, filings, calls, announcements | Source span, publication time, retrieval time, entity/event labels |
| 2. Feature construction | Quant module | Provides candidate structured inputs, does not set feature weights | Point-in-time feature table, missing-data handling, normalization rules |
| 3. Signal synthesis | Quant model | One of many information sources | Ablation and marginal contribution of LLM-derived features |
| 4. Probability calibration | Independent statistical module | Does not provide self-rated trading probabilities | ECE, reliability curves, regime-conditioned calibration, out-of-sample stability |
| 5. Sizing and risk control | Portfolio and risk modules | Explains sources of risk, does not directly determine size | Factor exposures, sector exposures, leverage, drawdown, liquidity constraints |
| 6. Execution and audit | Execution system | Observer or summarizer | Order log, fill prices, slippage, latency, failed orders, risk-stop records |

## 附录 E 实例：贯穿模块化流水线的 8-K 指引削减

本附录以一个具体事件走一遍模块化的阶段结构（表 5），作为对既有实践的描述，而不是提案。假设在时刻 t 发布了一份 8-K，声明公司 X 将下调下一季度的营收指引。

- 阶段 1（LLM 提取）：发出 JSON `{entity: X, event: 'guidance_cut', evidence_quote: '...', source_time: t, retrieval_time: t+δ}`。
- 阶段 2（特征构建）：量化系统把它映射为一个意外值特征，并与历史 EPS 意外值及指引修正历史拼接。
- 阶段 3（信号合成）：量化模型在多年面板数据上度量 IC 与边际贡献。
- 阶段 4（校准）：一个独立的校准模块评估样本外 ECE。
- 阶段 5（规模与风险控制）：组合模块执行板块中性的风险预算上限。
- 阶段 6（执行与审计）：执行系统记录时间戳、滑点与风控拦截记录。

LLM 主导阶段 1；在随后的阶段中它至多是观察者或解释者。这个例子的重点不在于架构本身——那是标准做法——而在于：一旦最终权威从 LLM 手中移走，对 P1–P6（截断披露、校准、摩擦清洗、多智能体去聚合）的符合就是按构造达成的。
