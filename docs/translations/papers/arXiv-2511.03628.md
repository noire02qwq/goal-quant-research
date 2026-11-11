# LiveTradeBench：在真实交易中寻求大语言模型的 Alpha（LiveTradeBench: Seeking Real-World Alpha with Large Language Models）

> 来源：https://arxiv.org/abs/2511.03628
> 原文：docs/papers/arXiv-2511.03628.pdf
> 翻译日期：2026-11-11 ｜ 范围：全文 ｜ 方式：机器翻译初稿，未经人工校对
> 引用于：docs/literature/W5-real-eval-fault-style.md

## 目录

- 摘要
- 1. 引言
- 2. 相关工作
- 3. 为组合管理构建实时交易环境
  - 3.1 组合管理的定义
  - 3.2 市场选择
  - 3.3 观察空间
  - 3.4 动作空间
- 4. 为组合管理设计基于 LLM 的 agent
- 5. 在实时测试下评估基于 LLM 的 agent
  - 5.1 评估用的主干 LLM
  - 5.2 评估用的交易指标
  - 5.3 评估结果
  - 5.4 分析与讨论
- 6. 案例研究
  - 6.1 美国股票市场中的现金资产动态
  - 6.2 Polymarket 预测市场中的俄乌停火市场
- 7. 结论
- 局限与未来工作
- 开源应用
- 参考文献（从略）
- S1. 数据采集
- S2. Prompting 细节
- S3. 模型细节
- S4. 前端 UI 细节

## 摘要

大语言模型（LLM）在各类基准上表现出色——从知识问答、数学推理到 web-agent 任务——但这些测试都发生在静态环境中，缺乏真实的动态性与不确定性。因此，它们衡量的是孤立的推理或问题求解能力，而非不确定性下的决策能力。

为此，我们提出 LiveTradeBench：一个在真实且不断演变的市场中评估 LLM agent 的实时交易环境。LiveTradeBench 遵循三条设计原则：（i）市场价格与新闻的实时流式传输，消除对离线回测的依赖，在防止信息泄漏的同时捕捉实时不确定性；（ii）组合管理抽象，把控制从单一资产动作扩展到多资产配置，整合风险管理与跨资产推理；（iii）跨结构迥异环境的多市场评估——美国股票与 Polymarket 预测市场——二者在波动性、流动性与信息流上各不相同。

在每一步，agent 观察价格、新闻与自身组合，然后输出在风险与收益之间取得平衡的百分比配置。借助 LiveTradeBench，我们对来自多个家族的 21 个 LLM 进行为期 50 天的实时评估。结果表明：（1）LMArena 高分并不意味着更优的交易结果；（2）模型呈现出反映风险偏好与推理动态的差异化组合风格；（3）部分 LLM 能有效利用实时信号来调整决策。这些发现暴露了静态评估与真实世界能力之间的鸿沟，促使人们构建能够在实时不确定性下检验序列决策与一致性的基准。

## 1. 引言

大语言模型（LLM）在各类基准上已接近饱和——例如知识竞赛（Hendrycks et al., 2020; Phan et al., 2025; Rein et al., 2024）、数学推理测试（Cobbe et al., 2021; Contributors, 2023; Quan et al., 2025）以及指令遵循任务（Jiang et al., 2023; Pyatkin et al., 2025; Zhou et al., 2023a）。然而这些基准都是静态的：以固定输入和单轮推理来评估模型。在这类测试中得分高，并不必然是真实世界智能的体现——在真实世界中，agent 必须感知、行动，并在随时间而来的反馈中不断适应。

为了超越静态评估，近期工作引入了交互式环境，让 LLM 执行序列化动作并观察反馈（Jimenez et al., 2023; Zhou et al., 2023c）。例子包括 web 与 computer-use agent（He et al., 2024; Koh et al., 2024a; Xie et al., 2024; Zhou et al., 2023b），它们运行在离散且确定性的环境中——每个动作都产生由后端逻辑定义的可预测状态转移。这类环境检验感知与推理，但完全可控，并支持基于树的搜索（Aksitov et al., 2023; Koh et al., 2024b; Putta et al., 2024）。相比之下，交易环境是连续且自主的系统：世界独立于 agent 而演化，动作只能调整 agent 的内部组合状态，而不能直接决定未来的观察。反馈是延迟且含噪的，重点在于适应而非控制。这种环境结构上的差异——从确定性系统到动态过程——为评估 LLM agent 在开放式真实环境中推理与行动的能力划定了更深的前沿（Garrido-Merch'an et al., 2024; Li et al., 2024）。

尽管如此重要，当前构建 LLM 交易 agent 的应用仍然过于简化，且与实时市场动态脱节。具体而言：（1）大多数评估框架依赖离线回测，容易信息泄漏，无法捕捉真实环境的不确定性、波动与反馈（Li et al., 2025a,b,c; Papadakis et al., 2025）；（2）多数交易 agent 把交易建模为单一资产上的低层局部动作（如买/卖/持有），忽略了跨多个资产的高层推理与规划（Briola et al., 2021; Han et al., 2023a,b; Ma et al., 2025）。这自然引出一个更宽泛的问题：如何以低成本、在真实市场条件下有效评估基于 LLM 的 agent 的交易能力？

为了回答这个问题，我们提出 LiveTradeBench——一个为解决上述两方面局限而设计的实时交易环境。（1）LiveTradeBench 以流式方式提供实时市场数据、金融新闻与社交信号，消除对离线回测的依赖，从而从根本上避免信息泄漏，同时捕捉真实世界的不确定性与反馈。（2）它采用组合管理抽象，把交易表述为一个战略性配置过程，整合了风险管理、时间维度推理以及跨多个资产的决策一致性（Gu et al., 2024; Kou et al., 2024; Yu et al., 2024）。

每一步中，环境给出动态观察——市场状况、上下文信号以及 agent 的历史决策——而 LLM 必须输出一个在时间上平衡风险与收益的更新后组合配置。通过将实时数据流与组合层面的推理相结合，LiveTradeBench 提供了一个真实、端到端的平台，用于评估基于 LLM 的 agent 在不断演变的市场动态下的真实交易能力。

利用该基准，我们开展两类实时交易评估：股票市场（美国股票）交易与预测市场（Polymarket）投注。我们比较了横跨多个模型家族与能力层级的 21 个主流 LLM。分析得到三个关键发现：（1）LMArena（Chiang et al., 2024）中的 SOTA 模型并未表现出 SOTA 的交易性能——通用推理上的高基准分数并不转化为更优的交易结果；（2）LLM 呈现出差异化的组合管理风格，在风险偏好、资产选择模式与配置动态上各不相同；（3）LLM 能够有效利用实时市场与新闻信号，做出更有依据、更自适应的交易决策。这些结果共同揭示了传统 LLM 评估与真实金融能力之间的脱节，推动了更具适应性与稳健性的组合管理 agent 的发展。

表 1：LiveTradeBench 与现有交易基准的对比。我们从四个维度比较本文工作与其他工作：（1）序列决策——其当前交易动作是否依赖于此前的动作；（2）组合管理——其任务是否为多资产组合管理；（3）实时交易——其评估属于基于历史市场数据的回测，还是基于实时流式数据的实盘测试；（4）多市场评估——是否包含股票市场以外的市场。

| 基准 | 序列决策 | 组合管理 | 实时交易 | 多市场评估 |
|---|---|---|---|---|
| FinQA (Chen et al., 2021) | ✗ | ✗ | ✗ | ✗ |
| ConvFinQA (Chen et al., 2022) | ✗ | ✗ | ✗ | ✗ |
| FLUE (Shah et al., 2022) | ✗ | ✗ | ✗ | ✗ |
| FinEval (Zhang et al., 2023) | ✗ | ✗ | ✗ | ✗ |
| BizFinBench (Bigeard et al., 2025) | ✗ | ✗ | ✗ | ✗ |
| FinAgentBench (Bigeard et al., 2025) | ✗ | ✗ | ✗ | ✗ |
| FinSearchComp (Hu et al., 2025) | ✓ | ✗ | ✗ | ✗ |
| INVESTORBENCH (Li et al., 2024) | ✓ | ✗ | ✗ | ✗ |
| StockBench (Chen et al., 2025) | ✓ | ✓ | ✗ | ✗ |
| DeepFund (Li et al., 2025b) | ✓ | ✓ | ✓ | ✗ |
| LiveTradeBench (ours) | ✓ | ✓ | ✓ | ✓ |

## 2. 相关工作

**交易 agent 的评估** 基于 LLM 的交易 agent 的评估通常依赖三类环境或基准。（1）基于历史市场数据的回测是主流做法（Li et al., 2025c; Tang et al., 2025; Tian et al., 2025; Xiao et al., 2024a）。然而这类评估常受信息泄漏之苦（Li et al., 2025a,d），且在更长或多市场状态（regime）的时段上泛化能力差（Gao et al., 2024a; Jiang and Zhou, 2025）。为解决这些问题，若干研究提出数据污染审计、实体匿名化与时序去偏协议，以实现更公平的回测评估（He and Xu, 2024; Wu and Zhang, 2025）。

（2）市场模拟器通过构建合成或自行设计的交易环境提供替代方案（Chen et al., 2023; Emmanoulopoulos et al., 2025; Lopez-Lira, 2025; Papadakis et al., 2025; Zhang et al., 2024a）。但这些模拟器主要用作行为分析的试验台，而非产出与真实市场动态一致的现实交易动作。（3）基于实时数据的实时评估是一个新兴方向。尽管它已在问答（Kasai et al., 2022; Nie et al., 2025）与编程（Liang and Zhang, 2024）等领域被广泛探索，但在交易领域仍基本未被触及（Li et al., 2025b）。我们的工作聚焦于这一实时评估范式，我们认为它能对 LLM 交易智能给出最忠实、也最面向未来的评估。

**面向交易 agent 的动作空间设计** 交易任务的设计因目标不同而差异显著，这些差异可以通过交易 agent 动作空间的形式化来刻画。在股票市场中，多数基于 LLM 的系统采用单资产交易形式，动作是买入、持有或卖出这类离散决策（Gao et al., 2024b; Li et al., 2023; Ma et al., 2025; Zhang et al., 2024b, 2025）。这种设定虽然直观，却忽视了跨资产依赖与现实的组合交互。

另一类方法聚焦于 alpha 预测，输出连续的 alpha 信号向量，表示各资产的预期超额收益或相对表现（Heinrich et al., 2021; Islam, 2025; Sun et al., 2024; Zhang et al., 2020）。然而这些信号描述的是预测，而非可直接执行的交易动作。在投注市场中，agent 常为互斥结果（如 "Yes" 与 "No"）输出概率估计（DeHaven et al., 2024; Jumadinova and Dasgupta, 2011; Koning and Zijm, 2022），这可以解释为互补资产上的隐式组合头寸。我们把这些视角统一到一个组合管理框架之下：agent 在多个资产或结果之间输出配置比例（Lucarelli and Borrotti, 2020; Sun et al., 2021; Ye et al., 2020）。这一形式化在一个连续决策空间内统一了离散交易、alpha 预测与概率化投注，并天然强调风险—收益权衡与资产间相关性。

* https://polymarket.com/

**基于 LLM 的交易 agent 框架** 各种框架以不同风格利用 LLM 构建交易 agent。一条研究路线聚焦于用强化学习（RL）微调单个 LLM，以增强决策与交易表现（Koa et al., 2024; Wang et al., 2025; Xiong et al., 2025; Zha and Liu, 2025; Zhang et al., 2025）。另一条路线探索多智能体系统，agent 通过角色分工协作或竞争，以模拟真实的市场动态（Li and Zhao, 2025; Xu et al., 2024; Zhang and Wang, 2025）。

此外，工具使用（如 API 调用、数据采集器）（Islam, 2025; Papadakis et al., 2025）、自我反思（Koa et al., 2024）与记忆（Li et al., 2024, 2023; Yu et al., 2023）等能力已被视为提升交易智能的关键组成部分。为了给出一个受控而又可扩展的设定，我们采用配备工具使用与记忆的 ReAct 风格（Yao et al., 2022）框架作为 agent 配置。

## 3. 为组合管理构建实时交易环境

### 3.1 组合管理的定义

**问题定义** 我们把组合管理任务形式化为部分可观测马尔可夫决策过程（POMDP）E = ⟨S, A, O, T, Ω⟩，其中 S 是隐市场状态空间，A 是动作空间，O 是观察空间，T 是转移动力学，Ω 是观察生成函数。在每个时间步 t，环境处于隐状态 st ∈ S，它封装了真实的市场状况，包括资产基本面、波动性、流动性及其他未观测因素。agent 收到部分观察

```
o_t = (q_t, p_t, c_t) = Ω(s_t)                                      (1)
```

其中 qt ∈ R^N 表示当前资产持仓（含现金），pt ∈ R^N 表示可观测的市场价格，ct 表示新闻、情绪或宏观指标等上下文信号。组合总价值计算为 vt = q⊤_t p_t。在观察历史 o≤t 的条件下，agent 产生一个动作 at ∈ A，表示目标配置向量，满足 ∑_i at^(i) = 1。

**状态转移函数** 环境转移刻画了市场与 agent 组合的联合演化。它由两个耦合过程组成：一个是外生的市场状态演化，由真实世界动力学支配，表现为 (pt, ct) → (pt+1, ct+1)；另一个是内生的组合调整，由 agent 在新市场状态下的配置决策 at 引发，导致 qt → qt+1。

具体而言，执行 at 之后，市场按 T 演化，产生新价格 pt+1 与上下文信号 ct+1。组合在新价格下被重新估值与再平衡：

```
ṽ_t+1 = q_t^⊤ p_t+1 ,   q_t+1 = ṽ_t+1 · a_t / p_t+1 ,   v_t+1 = q_t+1^⊤ p_t+1 = ṽ_t+1    (2)
```

其中除法为逐元素运算。下一个观察 ot+1 由 Ω 生成，反映更新后的组合状态与市场上下文。由于我们选取 Nvidia（NVDA）股票等高流动性资产以及热门 Polymarket 市场来构成组合，agent 的单笔交易对真实世界价格的影响可以忽略。这一假设使得把模拟转移函数 T 建模得与真实世界高度一致成为合理。

**从配置决策到可执行交易动作** 在每个时间步 t，输出配置决策 at 之后，agent 可以通过可执行交易动作（BUY/SELL/HOLD）把持仓从 qt 更新为 qt+1。成交的交易向量定义为 Δqt = qt+1 − qt，其中为正的 Δqt^(i) > 0 表示买入 Δqt^(i) 股资产 i，为负的 Δqt^(i) < 0 表示卖出 |Δqt^(i)| 股，Δqt^(i) = 0 对应持有当前头寸。这些交易执行后，组合转到新持仓 qt+1，组合总价值 vt+1 按式 2 更新。该形式化提供了从高层配置动作空间到显式买入、卖出、持有操作的直接映射，而无需对低层订单执行机制建模。

图 1：LiveTradeBench 的市场选择。上排图板分别展示美国股票市场中的 AAPL（左）与 Polymarket 预测市场中的合约"OpenAI has the best AI model by the end of 2025"（右）。在预测市场中，价格直接反映给定结果的概率。两个市场都会对新闻与历史价格趋势作出反应，但 Polymarket 的波动更剧烈、反应更快、对外部信号更敏感。下排图板展示覆盖科技、金融、加密货币、制造业与政治等多个领域的代表性资产。（原文第 5 页）

### 3.2 市场选择

我们在两个互补环境（股票市场与预测市场）中评估 agent，旨在检验它们在结构化与信息驱动两种市场状态下的泛化能力。这一双重设定使我们能够全面评估 agent 是否能在结构、信息流与反应速度各异的市场上保持一致的表现。重要的是，这两个市场要实现盈利需要截然不同的策略与推理视角：股票市场奖励长周期分析与有纪律的分散化，而预测市场则要求短周期适应与事件驱动的信念更新。

**美国股票市场** 美国股票市场是一个成熟、受制度监管的体系，资产价格平滑演化，呈现强烈的跨行业相关性，并随时间反映聚合后的基本面与宏观经济信号。在这一环境中做好组合管理，需要捕捉长期依赖、对隐藏相关性建模，并保持分散化的风险敞口。

我们构建了一个由 15 只股票与 ETF 组成的代表性组合，覆盖美国主要行业，以确保对外部信息与宏观变化有多样化的反应。组合包括科技股——Apple（AAPL）、Microsoft（MSFT）、NVIDIA（NVDA）与 Meta Platforms（META）；金融股——JPMorgan Chase（JPM）与 Visa（V）；能源与工业股——Exxon Mobil（XOM）、Caterpillar（CAT）与 Tesla（TSLA）；消费股——Procter & Gamble（PG）、Coca-Cola（KO）、Amazon（AMZN）与 Walmart（WMT）；以及医疗股——Johnson & Johnson（JNJ）与 UnitedHealth Group（UNH）。

此外还加入一个单价恒定、收益率为零的现金资产，用以代表无风险资金配置。这一构成在高度流动且受监管的金融环境中提供了对关键行业的均衡敞口，我们采集实时股票价格作为评估的数据源。

**Polymarket 预测市场** 相比之下，Polymarket 预测市场是去中心化的、情绪驱动的，其合约松耦合，对实时信息的反应尖锐且异步。这些市场往往比股票变动更突兀、一致性更弱，反映的是集体信念而非基本面的转变。因此，这里的有效组合管理要求快速适应、事件驱动的推理以及对不断演变的叙事的敏感度。

我们持续追踪 Polymarket 上十个活跃的二元预测市场，聚焦于政治、加密货币、科技与金融相关的投注市场——例如"2025 年美联储会加息吗？""2025 年 Tether 会破产吗？""2025 年美国会衰退吗？""2025 年 USDT 会脱锚吗？"。我们假设预测市场与股票市场对同一信息的反应在时滞与幅度上不同：股票市场通过机构共识逐步消化信号，而预测市场则即时反应，并常常因投机情绪而过度反应。这两个环境——结构化的金融市场与去中心化的预测市场——共同为在稳定与不确定两种条件下评估 agent 提供了互补的试验台。

图 2：LiveTradeBench 的观察空间与动作空间。我们用美国股票市场与 Polymarket 预测市场两个示例来演示观察空间与动作空间。观察空间由三部分组成：agent 的头寸、市场价格与相关新闻上下文。动作空间表示 agent 生成的组合配置决策，它们可以直接转换为可执行的交易动作。（原文第 6 页）

### 3.3 观察空间

在每个时间步，agent 收到观察 ot = (qt, pt, ct)，它封装了当前市场状况、外部上下文与组合状态。该观察是 agent 决策过程的主要输入，整合了量化的市场信号、头寸信息与定性的上下文线索。基于这些动态输入，agent 决定下一步的配置动作，以适应不断演变的市场趋势与外部变化。观察空间的数据采集细节见附录 §S1。

**头寸 qt** 头寸观察 qt 表示 agent 在所有资产上的当前持仓，包括现金。每个分量 qt^(i) 是一个连续、非负的值，表示组合中当前持有的资产 i 的数量（或其分数部分）。这一形式化不同于传统交易形式中离散的买入/持有/卖出信号，而是提供了连续资金配置的细粒度表示。非负约束确保 agent 不能建立空头头寸，反映现实的市场限制，并强调资金在只做多资产之间的分配。

**市场价格 pt** 价格观察包含组合中所有标的的最新资产价格及对应时间戳。对股票市场，pt 包含 15 只入选股票的收盘价；对预测市场，它包含 10 个热门 Polymarket 市场的实时交易价格。这些数值是组合估值与配置更新的直接依据，使 agent 能够跟踪资产价值随时间的演变。

**市场上下文 ct** 上下文观察 ct 主要提供实时市场新闻。我们用资产与主题特定的关键词（如 "Federal Reserve"、"inflation"、"NVIDIA stock"）从 Google News 采集近期文章。这类信息反映短期市场情绪、投资者注意力以及往往先于价格变动出现的宏观层面信号。

为了使模型能够对这些因素进行推理，我们把这些新闻的文本摘要直接放进 prompt，让基于 LLM 的 agent 把情绪转变、政策预期或公司相关事件等定性上下文纳入交易决策。

### 3.4 动作空间

在每个时间步 t，agent 执行动作 at ∈ A，其中 A 表示概率单纯形动作空间。每个分量 at^(i) 指定分配给资产 i 的组合总价值 vt 的比例，满足预算约束 ∑_i at^(i) = 1。默认假设为只做多设定，即对所有 i 有 at^(i) ≥ 0。这种基于连续配置的形式化抽象掉了低层交易执行，聚焦于高层组合再平衡，使 agent 能够随时间表达平滑的战略转移，并直接针对收益、风险与稳定性等组合层面的目标进行优化。

**股票市场动作** 在股票市场环境中，每个动作分量 at^(i) 表示要配置给股票 i 的组合总价值 vt 的百分比。该配置通过按比例再平衡决定交易后的头寸 qt+1，直接反映 agent 在各行业间的资金分布。

**预测市场动作** 在预测市场环境中，每个二元合约对应两个互补资产——YES 与 NO。对 k 个活跃市场，动作向量 at 有 2k 个分量，其中 at,YES^(k) 与 at,NO^(k) 分别表示对市场 k 的 YES 与 NO 结果的组合配置。agent 的净敞口定义为 et^(k) = at,YES^(k) − at,NO^(k)，正值表示对 YES 结果的信心更高。

图 3：LiveTradeBench 中的 agent 与环境框架。左侧为模拟环境，它持续检索真实世界的市场价格与新闻，并相应更新内部状态；还根据已执行的动作调整 agent 的组合头寸。右侧为组合管理 agent，配备分析工具以处理来自环境的观察。agent 维护对过去观察的记忆，从而实现自适应、依赖上下文的决策。（原文第 8 页）

## 4. 为组合管理设计基于 LLM 的 agent

在我们的框架中，agent 是核心决策实体，把观察到的信息转化为可执行的组合配置。它是外部市场与内部组合记忆之间的桥梁，不断根据变化的条件调整策略。agent 整合三种交织的能力——工具使用、记忆与推理——使它能够感知、回忆与行动，形成信息获取、反思与执行的闭环。形式化地，在每个时间步 t，agent 收到观察 ot。此外，agent 维护一个内部记忆状态 Mt，存储当前观察之外的历史观察。在当前观察与记忆的共同条件下，agent 产生配置

```
a_t = f_θ(o_t, M_t)                                                 (3)
```

其中 fθ 是定义 agent 交易行为的参数化策略。agent prompt 的构建细节见附录 §S2。

**工具使用** 第一个工具使用组件使 agent 能够与我们提供的实时环境交互——获取、过滤并提取实时市场与上下文信息。市场价格 pt 与上下文信号 ct 由环境发出，而工具使用模块决定 agent 如何主动获取与处理它们。它是 agent 与真实世界的接口，把原始输入转换为结构化的特征表示

```
õ_t = h(o_t)                                                        (4)
```

既捕捉量化的动态（如由 pt 导出的价格变动、收益率与波动率特征），也捕捉定性的线索（如从 ct 中提取的、与特定市场相关的新闻）。通过工具使用，agent 把感知扩展到静态观察之外，动态收集与精炼证据，为其配置决策提供依据。

**记忆** 第二个记忆组件维护 agent 近期观察及其动作结果的紧凑表示。在每个时间步，agent 存储一段固定长度的历史观察序列，并把它们拼接为统一的记忆状态：

```
M_t = { o_τ | t − ∆ ≤ τ < t }                                      (5)
```

其中 ∆ 表示记忆跨度。这种拼接记忆提供了超出当前观察的时间上下文，使 agent 能够捕捉波动率动态、配置调整与回撤趋势等依赖关系。通过让决策同时以 ot 和 Mt 为条件，agent 随时间适应不断演变的市场状况。

**推理** 第三个推理组件是 agent 的决策核心。它把通过工具使用收集的信息与记忆中保留的上下文知识相融合，对每一时刻的市场形成连贯的理解。在执行任何动作之前，agent 会进行遵循 ReAct（Yao et al., 2022）框架的推理过程：先生成中间思考来解释信号、回忆相关经验，并对潜在结果作出假设。与 chain-of-thought prompting（Wei et al., 2022）类似，这一步产生连接感知与决策的显式推理痕迹。

这种可解释性使产出的动作可以被分析，并被视为对不断演变的市场情境的理性回应。通过这种刻意的"先推理、后行动"循环，agent 在组合管理中同时获得适应性与透明度。这类推理依据还可潜在地用于帮助研究者理解模型行为，并作为改进 LLM 的资源。

## 5. 在实时测试下评估基于 LLM 的 agent

本节给出 2025 年 8 月 18 日至 2025 年 10 月 24 日开展的实时交易的详细评估结果与分析——共计 50 个交易日——覆盖建立在 21 个不同 LLM 主干之上的交易 agent。§5.1 与 §5.2 描述评估设定，包括模型主干与性能指标；§5.3 报告主要结果，§5.4 提供深入分析与讨论。

### 5.1 评估用的主干 LLM

为了在实时交易环境中对性能进行基准比较，我们评估了一组多样的主流 LLM 作为交易 agent。具体而言，我们考虑六个代表性模型家族。这些模型基于两条主要标准选取：（1）它们在通用推理、知识与 agentic 基准上的 SOTA 表现；（2）它们在模型规模、架构与性能层级上的多样性，使我们能够研究异构系统在金融决策任务上的性能梯度。

**LLM 家族** 我们纳入以下代表性模型：Claude 家族（Claude-Sonnet-3.7（Anthropic, 2025a）、Claude-Opus-4 与 Claude-Sonnet-4（Anthropic, 2025b）、Claude-Opus-4.1（Anthropic, 2025c））、Grok 家族（Grok-3（xAI, 2025a）、Grok-4（xAI, 2025b））、Qwen 家族（Qwen2.5-72B-Instruct（Yang et al., 2024）、Qwen3-235B-A22B-Instruct 与 Qwen3-235B-A22B-Thinking（Yang et al., 2025））。

LLaMA 家族（Llama3.3-70B-Instruct-Turbo（Meta, 2025a）、Llama4-Scout 与 Llama4-Maverick（Meta, 2025b））、GPT 家族（GPT-5（OpenAI, 2025b）、GPT-4o（Hurst et al., 2024）、GPT-4.1（OpenAI, 2025a）、GPT-o3（OpenAI, 2025c））、Kimi 家族（Kimi-K2-Instruct（Team et al., 2025））以及 DeepSeek 家族（DeepSeek-V3.1（DeepSeek, 2025）、DeepSeek-R1（Guo et al., 2025））。

每个模型都被包装在同一个 agentic 框架中：该框架把市场观察转换为自然语言 prompt，并把模型输出解析为结构化的组合配置向量。统一的设定确保性能差异主要反映模型内在的推理与决策能力，而非 prompt 格式或执行方式上的差异。模型选取的细节见附录 §S3。

### 5.2 评估用的交易指标

为了评估交易 agent 的表现，我们采用四个广泛使用的金融指标：累计收益（cumulative return）、波动率（volatility）、Sharpe 比率（Sharpe ratio）与最大回撤（MDD）。这些指标共同捕捉盈利能力、风险敞口、风险调整后效率与下行保护，给出跨不同市场的交易表现全貌。

- **累计收益（CR = (v_T − v_0) / v_0）** 衡量投资策略在给定评估期内的整体盈利能力。这里 v0 与 vT 分别是初始与最终组合价值，T 是评估期间的总时间步数。累计收益 CR 越高，表示交易 agent 取得的累计收益越强。
- **Sharpe 比率（SR = (r̄ − r_f) / σ）** 评估收益相对于所承担风险的效率。这里 r̄ 表示平均收益，r_f 是无风险利率，代表无风险投资的基线收益，σ 是收益的波动率。在美国股票中，r_f 对应短期国债收益率（通常为正）；而在 Polymarket 中，r_f 设为 0，以反映以稳定币计价的资产没有收益这一事实。Sharpe 比率 SR 越高，表示策略每单位风险获得的回报越大，即风险调整后表现更优。
- **最大回撤（MDD = max_{t∈[1,T]} max_{i∈[1,t]} (v_i − v_t) / v_i）** 刻画在创新高之前，组合价值从历史峰值到随后谷底的最大观察跌幅。这里 vt 表示时间步 t 的组合价值。MDD 越小，说明下行保护越好、抵御严重亏损的能力越强。
- **胜率（WR = (1 / (T − 1)) ∑_{t=2}^{T} I(r_t > 0)）** 衡量盈利交易步骤所占比例，捕捉 agent 产生正收益的一致性。这里 I(·) 在收益 rt 为正时等于 1，否则为 0。胜率 WR 越高，表示 agent 获利越频繁，通过反映短期决策可靠性来补充累计与风险调整类指标。
- **波动率（σ = √[(1 / (T − 1)) ∑_{t=1}^{T} (r_t − r̄)²]）** 反映收益的变异性，用作投资风险的度量。这里 r_t = (v_t − v_{t−1}) / v_{t−1} 表示时间步 t 的收益，r̄ = (1 / T) ∑_{t=1}^{T} r_t 是平均收益，T 是评估时间步总数。波动率 σ 较低的策略随时间表现出更稳定的性能。

表 2：美国股票市场与 Polymarket 预测市场交易表现的对比。我们使用五个关键指标：累计收益（CR）、Sharpe 比率（SR）、最大回撤（MDD）、胜率（WR）与波动率（σ）。原文中每列的最高值以粗体标出。

| 模型 | 美国股票市场 |  |  |  |  | Polymarket 预测市场 |  |  |  |  |
|---|---|---|---|---|---|---|---|---|---|---|
|  | CR↑ | SR↑ | MDD↓ | WR↑ | σ↓ | CR↑ | SR↑ | MDD↓ | WR↑ | σ↓ |
| Claude-Sonnet-3.7 | 3.63 | 1.45 | 2.65 | 59.18 | 10.25 | 20.54 | 2.38 | 10.65 | 51.02 | 44.64 |
| Claude-Sonnet-4 | 2.45 | 0.72 | 3.23 | 53.06 | 12.86 | −40.32 | −2.40 | 51.10 | 38.78 | 92.16 |
| Claude-Opus-4 | 3.93 | 1.72 | 2.11 | 63.27 | 9.45 | −2.04 | 0.09 | 13.67 | 46.94 | 56.38 |
| Claude-Opus-4.1 | 3.73 | 1.51 | 1.84 | 63.27 | 10.17 | −25.69 | −3.02 | 30.53 | 48.98 | 46.81 |
| Grok-3 | 3.22 | 1.26 | 2.13 | 65.31 | 10.17 | −8.35 | −0.55 | 18.80 | 53.06 | 54.35 |
| Grok-4 | 4.30 | 1.75 | 1.92 | 59.18 | 10.43 | 7.38 | 1.01 | 13.04 | 46.94 | 46.92 |
| Qwen2.5-72B-Instruct | 5.15 | 2.18 | 2.22 | 65.31 | 10.24 | 1.63 | 0.43 | 7.46 | 59.18 | 30.36 |
| Qwen3-235B-A22B-Instruct | 3.52 | 1.32 | 2.04 | 61.22 | 10.89 | −54.24 | −2.97 | 54.24 | 40.82 | 112.37 |
| Qwen3-235B-A22B-Thinking | 1.78 | 0.60 | 2.32 | 59.18 | 9.28 | −57.62 | −1.81 | 72.10 | 38.78 | 166.92 |
| Llama3.3-70B-Instruct-Turbo | 2.72 | 0.88 | 3.54 | 61.22 | 11.95 | 1.58 | 0.40 | 19.41 | 57.14 | 38.15 |
| Llama4-Scout | 4.65 | 1.99 | 2.62 | 59.18 | 9.98 | −16.05 | −1.18 | 24.80 | 51.02 | 60.37 |
| Llama4-Maverick | 4.46 | 1.65 | 2.45 | 53.06 | 11.59 | −18.31 | −1.92 | 28.63 | 34.69 | 48.21 |
| GPT-4o | 3.55 | 1.39 | 2.43 | 55.10 | 10.38 | −30.96 | −3.26 | 35.31 | 30.61 | 53.75 |
| GPT-4.1 | 6.25 | 2.64 | 1.92 | 65.31 | 10.51 | −33.69 | −1.74 | 37.98 | 40.82 | 95.27 |
| GPT-5 | 5.31 | 2.19 | 2.53 | 65.31 | 10.60 | −23.96 | −0.49 | 38.92 | 44.90 | 130.37 |
| GPT-o3 | 6.04 | 2.57 | 2.27 | 61.22 | 10.41 | −54.84 | −3.68 | 60.99 | 40.82 | 97.27 |
| Gemini-2.5-Flash | 2.10 | 0.72 | 3.10 | 55.10 | 11.25 | −22.40 | −0.82 | 42.35 | 38.78 | 115.42 |
| Gemini-2.5-Pro | 1.95 | 0.61 | 2.85 | 50.00 | 10.98 | −35.15 | −1.65 | 49.80 | 34.69 | 101.87 |
| Kimi-K2-Instruct | 3.07 | 1.15 | 3.32 | 53.06 | 10.53 | −53.44 | −5.26 | 54.74 | 28.57 | 69.41 |
| DeepSeek-V3.1 | 2.46 | 0.86 | 2.45 | 59.18 | 10.61 | −4.68 | −0.07 | 22.43 | 48.98 | 64.74 |
| DeepSeek-R1 | 2.10 | 0.78 | 2.20 | 61.22 | 9.11 | −13.19 | 0.14 | 44.16 | 42.86 | 143.25 |

### 5.3 评估结果

**单一市场上的交易表现无法泛化到另一个市场。** 如表 2 所示，两个市场之间的 Sharpe 比率相关性接近于零，说明在一个市场的成功并不意味着在另一个市场也会成功。这凸显了针对特定市场制定交易策略的必要性。例如，Qwen2.5-72B-Instruct 与 Grok-4 在股票与预测市场上都表现出相对一致的性能，暗示其策略更稳定、波动更低。相比之下，GPT-4.1 在股票市场取得了最高的累计收益率（> 6%），但在 Polymarket 上表现糟糕（收益 < −30%），这很可能是由于在较高波动下配置变动过度反应所致。总体而言，预测市场呈现出更快的动态、更大的波动与更深的回撤（MDD），要求更敏捷、更能承受风险的策略。

**通用 LLM 能力强并不意味着金融表现出色。** 图 4 显示，以 LMArena 分数衡量的通用 LLM 能力与交易能力呈微弱负相关。在股票市场，LMArena 分数与累计收益的 Spearman 相关性仅为 0.054——几乎没有关系。在 Polymarket，该相关性降至 −0.38，意味着通用语言能力更强的模型在这种动态市场中往往表现更差。因此，通用基准上的 SOTA LLM 并不一定转化为动态、真实交易中的 SOTA 表现。这凸显了我们环境的独特性与必要性。

**各模型呈现出差异化的组合管理风格。** 不同模型表现出明显的管理偏好。Claude-Opus-4.1 与 Grok-4 采取保守策略，特点是波动更低、回撤更小，优先考虑稳定而非激进收益。相比之下，Kimi-K2-Instruct 与 GPT-5 表现出更强的风险寻求行为——为追求更高收益而接受更高的波动与 MDD。

除了收益与风险指标，模型在组合构成与现金管理模式上也差异显著。例如，GPT-4o 始终聚焦于少数核心资产（AAPL、MSFT、NVDA），而 GPT-5 则以更小的仓位比例分散到更广的股票范围。同样，Llama4-Scout 长期保持高现金比例（20% 以上），反映更谨慎的流动性立场；而 GPT-5 除极高风险情形外，交易全程都把现金保持在 10% 以下。这些行为模式并不局限于单一市场——类似的管理风格在两个市场上都一致出现。

**大型推理模型并不带来交易优势。** 与 Chen et al.（2025）的发现一致，专为推理设计的模型——如 DeepSeek-R1、Qwen3-235B-A22B-Thinking 与 GPT-o3——在交易表现上并不优于其他模型。相反，它们表现出明显更高的波动（在 Polymarket 上超过 140），意味着决策过程中的过度调整。对数学或编程任务有益的那种推理，并不能直接迁移到金融或社会推理上。事实上，在这些模型交易时观察到的过度斟酌会引入不稳定性，损害交易的一致性。

图 4：LMArena 分数与两个市场 Sharpe 比率的相关性。（左）美国股票市场。（右）Polymarket 预测市场。不同家族的模型以不同颜色显示，虚线为线性回归拟合。（原文第 12 页）

图 5：美国股票的 rolling k-delta 分析。我们评估再平衡间隔 k ∈ {1, 2, 4, 8, 16}。黑线表示 21 个模型的平均表现，灰色阴影区域表示 25–75% 置信区间。（原文第 13 页）

图 6：Polymarket 的 rolling k-delta 分析。我们同样评估再平衡间隔 k ∈ {1, 2, 4, 8, 16}。黑线表示 21 个模型的平均表现，灰色阴影区域表示 25–75% 置信区间。（原文第 13 页）

图 7：决策依据分析。每根柱子表示推理痕迹中引用头寸、价格或新闻信息的比例。单条推理痕迹可能包含多个信息来源。（原文第 13 页）

### 5.4 分析与讨论

本节我们定量分析两个核心问题，它们探究基于 LLM 的交易 agent 的基本能力。（1）基于 LLM 的 agent 只是随机猜测者吗？——检验 agent 的交易行为是否反映了有意义的市场理解，还是仅仅随机波动。（2）agent 如何推理并做出交易决策？——考察其动作背后的内部依据，揭示其决策是否建立在连贯的推理模式之上。这两个分析共同揭示了基于 LLM 的 agent 在动态、不确定市场环境中的有效性与可解释性。

**LLM agent 只是在随机猜测吗？** 为了验证基于 LLM 的交易 agent 表现出真正的市场感知而非随机行为，我们设计了 rolling-k delta（∆k）分析。核心思想是：如果 agent 的决策是随机的，把它们的动作推迟几天不应系统性地影响表现；反之，如果它们确实适应了变化的市场状况，过时的决策应导致可测量的性能退化。对每个交易日 t，我们把组合头寸固定为 k 天前所取的头寸，qt^(k) = qt−k，并计算日收益与累计收益：

```
                 (q_t−k)^⊤ (p_t+1 − p_t)                      T − k − 1
r_t^(k) = ———————————————————————— ,   CR^(k) = ∏_{t=k}            (1 + r_t^(k)) − 1    (6)
                (q_t−k)^⊤ p_t
```

rolling-k delta 随后定义为 ∆k = CR^(k) − CR^(0)，刻画 agent 动作落后市场 k 天时的累计收益损失。∆k 为负说明更频繁的再平衡能改善表现。如图 5 与图 6 所示，k 越大（更新越慢）退化越严重，证实及时更新决策是有益的。

有趣的是，在股票市场，当 k = 2 时收益反而略微提高到 0.03%，说明与 Polymarket 相比其动态更平滑、时间敏感度更低——后者的表现随 k 增大而退化约 2%。总体而言，这些结果表明基于 LLM 的 agent 并非随机行动——它们的交易策略依赖于同期市场信号，而系统性地推迟其动作会损害表现。

**LLM agent 如何推理并做决策？** 为了考察决策依据，我们采用基于 LLM 的推理标注。对每天的推理痕迹，另一个 LLM 自动识别 agent 的解释是否提及：（1）组合头寸、（2）市场价格历史，或（3）市场新闻。图 7 总结了这些因素的分布。在两个市场中，新闻都是被引用最多的因素，其次是市场价格历史，而头寸信息占比最低。此外，Polymarket 的 agent 更依赖新闻信号，而股票市场的 agent 更强调价格趋势——这验证了我们关于两个市场呈现不同动态的假设。由于推理引用的总百分比超过 100%，许多决策整合了多个信息来源，表明推理过程复杂。具体而言，agent 在分析价格历史时常提到 "price momentum"，在讨论市场新闻时则聚焦于潜在结果或影响。

## 6. 案例研究

本节我们分别从美国股票与 Polymarket 预测市场中选取代表性资产，并各挑出两个鲜明且极端的时间点加以分析，以此展示两个市场的例子。这使我们得以考察 agent 决策背后的推理，并理解其选择与市场状况的关联。

### 6.1 美国股票市场中的现金资产动态

在图 8 中，我们分析组合内现金资产的动态，并在美国股票市场中给出两个对比鲜明的市场情形——一个正面（看涨）案例与一个负面（看跌）案例。现金比例是风险管理的一个信息性指标：现金比例较高通常反映更强的风险厌恶与防御姿态，而现金比例较低则意味着更强的市场信心与更积极的投资姿态。

**8 月 28 日的科技股上涨** 8 月 28 日，全部 21 个模型的平均现金比例连续三天稳步下降，在四个交易日内从 17% 降至 7.5%。这一趋势与 Meta（META）、Apple（AAPL）、Microsoft（MSFT）等主要科技股的强劲反弹同步，促使 agent 更积极地投资、减少现金持有。值得注意的是，取得最高累计收益率的 agent GPT-4.1 为它的配置决策给出了如下理由："This allocation increases exposure to leading AI and tech growth stocks (NVDA, MSFT, META) following strong earnings momentum and positive analyst sentiment, while maintaining solid positions in diversified blue chips for stability and sector balance."（本次配置在强劲的盈利动能与积极的分析师情绪之下，增加对领先 AI 与科技成长股（NVDA、MSFT、META）的敞口，同时在分散的蓝筹股中保持稳固头寸，以兼顾稳定性与行业平衡。）这一推理与观察到的看涨阶段现金比例下降明显一致。

**10 月 10 日的市场回撤** 相比之下，10 月 10 日市场的急剧回撤引发了相反的行为。多数股价显著下跌——Tesla（TSLA）跌超 5%，Amazon（AMZN）与 Nvidia（NVDA）跌逾 4%——导致当天所有 agent 都录得负收益。作为应对，多数 agent 增加现金持有以降低风险，反映出集体转向防御策略。如图 8 右侧所示，多个 agent 给出了类似的推理，与 "increasing CASH positions to protect against volatility"（提高 CASH 头寸以抵御波动）相关。其中，Gemini-2.5-Pro 维持了相对较高的现金头寸，并在下跌前把额外资产转为现金，当天损失最小。

图 8：美国股票市场案例研究。（左）21 个模型在 50 个交易日中的平均现金比例。（右）10 月 10 日急剧回撤的放大视图，其间组合的现金持有突然增加。我们呈现了市场状况（价格变动），并给出 10 月 10 日表现最好模型（Gemini-2.5-Pro）与表现最差模型之一（DeepSeek-V3.1）的推理痕迹以作对比。（原文第 15 页）

### 6.2 Polymarket 预测市场中的俄乌停火市场

我们分析 Polymarket 上的 "Russia × Ukraine ceasefire in 2025?" 市场，聚焦实时新闻如何影响基于 LLM 的 agent 的决策。Polymarket 对外部信息高度敏感，使其成为评估模型如何解读并响应动态地缘政治信号的天然试验台。我们选择该市场做案例研究，是因为它在 50 个交易日内波动频繁，导致各模型表现出截然不同的行为与收益。如图 9 所示，Grok-3 模型能够进行基于信念的推理，把其对停火概率的内部估计从 10 月 13 日的 0.15 调整到 10 月 17 日的 0.22。

**10 月 13 日的反应式变动未带来利润** 10 月 13 日，在两条乐观新闻事件之后，多数 agent 突然把组合从 No 头寸切换到 Yes 头寸：（1）Zelenskyy 表示 "the Gaza deal brings hope for Ukraine"（加沙协议给乌克兰带来希望）；（2）有报道称 Trump 分享了美国情报以帮助基辅打击俄罗斯能源目标。这些标题看似与停火相关，促使 agent 买入 Yes 头寸。然而 Polymarket 的价格实际上几乎没有变动，这种反应式变动没有带来利润。这些新闻最终被证明对停火可能性的因果影响有限。该案例凸显了基于 LLM 的 agent 的一个关键挑战：区分抢眼但非决定性的新闻与真正有影响力的事件。基于表面相关性行动可能导致过度反应与亏损交易。

**10 月 17 日的策略性持有带来利润** 相比之下，10 月 17 日当 Zelenskyy 到访白宫的消息传出时，多数 agent 加强了 Yes 头寸并持有到次日。这一次，Polymarket 价格从 10 月 17 日到 18 日稳步上升，带来了实实在在的利润。与此前的过度反应不同，agent 表现出更扎实的推理——引用 "recent diplomatic developments"（近期外交进展），并把 "a significant price jump to 0.18"（价格跃升至 0.18）视为确证证据。这一情形说明，围绕可信、高影响力的事件持有头寸，比基于弱信号的频繁反应式切换能带来更好的结果。

图 9：Polymarket 预测市场案例研究。（左）21 个模型在 "Russia × Ukraine ceasefire in 2025?" 市场中 "Yes" 与 "No" 头寸比例的平均持有比例。（右）两次突变（10 月 13 日与 10 月 17 日）的放大视图，以及相应新闻事件与 Grok-3 解释这些配置决策的推理痕迹。（原文第 16 页）

## 7. 结论

本文我们提出 LiveTradeBench——一个用于在真实组合管理任务中评估基于 LLM 的 agent 的实时多市场环境。LiveTradeBench 引入了超越静态基准评估模型智能的新范式，使连续的交互、推理与适应能够在实时的股票与预测市场中进行。通过为期 50 天的实时实验，我们发现一个市场上的强势表现无法泛化到其他市场，凸显了跨市场类型所需的异质性与专业化。此外，在 LMArena 这类通用基准上的高分并不必然转化为更优越的交易表现，揭示了文本智能与动态决策之间的鸿沟。最后，我们的分析表明，基于 LLM 的 agent 联合依赖历史价格趋势、市场新闻与配置历史，并在极端条件下表现出截然不同的行为模式。总体而言，LiveTradeBench 为研究基于 LLM 的 agent 如何在实时、真实的交易环境中感知、推理与行动奠定了基础——为开发更具适应性、更扎根金融、也更具社会智能的 agent 系统铺平道路。

## 局限与未来工作

尽管已在实时多市场环境中证明了评估基于 LLM 的交易 agent 的可行性，我们的框架仍有三个主要局限，它们指向未来研究与开发中有前景的方向。

**交易成本与市场摩擦** 我们当前的环境与评估未考虑交易费用、买卖价差、流动性约束或其他真实交易摩擦。忽略这些因素可能高估可实现收益，尤其是对依赖频繁再平衡的策略。未来工作将引入更现实的成本模型与滑点模拟，以更好地逼近真实交易条件。

**受限的观察与动作空间** 由于现有 LLM 的上下文长度有限，当前框架同时限制了观察空间与动作空间。在观察空间方面，agent 只能访问有限时间窗口内的价格、头寸与新闻历史，且这些历史仅限于股票市场与预测市场中的一小部分市场。此外，新闻输入被截断为标题与摘要而非全文，使 agent 无法纳入可能蕴含更深市场信号的长文本信息。在动作空间方面，可能的交易动作范围同样受限于受支持的市场数量，降低了配置决策的复杂度与丰富度。未来工作可以把框架扩展到支持更长的时间跨度、更丰富的文本上下文与动态的市场扩展——使 agent 能够在更真实、信息更丰富的环境中观察与行动。

**简化的 agent 设计** 当前 agent 架构在 ReAct 框架下集成了基础的工具使用与记忆，但在推理深度与时间抽象上仍有限。未来工作可以系统性地增强每个组件。工具使用方面，可以为 agent 配备更专业的分析与检索工具，用于金融推理、新闻解读与风险评估。记忆方面，可以引入更丰富的分层与长期记忆机制，以捕捉时间依赖并在更长跨度上保留跨市场知识。

除基于 ReAct 的基础设定外，当前框架还可以扩展到多智能体范式，例如 TradingAgents（Xiao et al., 2024b），以更好地建模异质角色与市场交互。最后，引入强化学习（RL）来训练交易 agent（Xiao et al., 2025）是提升决策质量的一个有前景的方向——使 agent 能从经验中学习、改进推理，并持续适应动态的市场状况。

## 开源应用

为了推动基于 LLM 的交易 agent 研究的普及，我们开源了一个 Python 包 live-trade-bench†，提供数据采集、环境搭建与 agent 构建的简洁 API。基于该包，我们还开发了一个 Web 应用，把我们的交易环境实时部署，支持实时数据流与对 agent 表现的交互式监控。用户界面（UI）设计细节见附录 §S4。

† https://pypi.org/project/live-trade-bench/

## 参考文献

参考文献从略，见原文。

## S1. 数据采集

我们采集实时价格与新闻信号，以填充股票市场与 Polymarket 两个市场的观察空间。价格来自一个公开金融 API（股票）与 Polymarket CLOB 端点（预测市场）；上下文来自 Google News 与 Reddit。所有抓取器都使用随机延迟、标准 User-Agent 与指数退避重试；JSON 解析以保守的超时重试少量次数。取回的条目绑定到代码或市场 ID，并与账户历史一起呈现给 agent。

### S1.1 市场新闻数据

**来源与时间窗** 对交易日 t，我们在短窗口 [t−3, t−1] 上查询 Google News，以在保持时效性的同时减少同日泄漏。当目标日期可用时，结果按与 t 的接近程度排序，否则按新鲜度排序。

**查询构造** 股票使用 `<TICKER> stock news OR <Company Name>`；Polymarket 使用市场问题文本。抓取器按日期对结果分页获取。

**归一化** 我们解析每篇文章的标题、摘要、链接（已清理 Google 重定向）、来源与时间戳。相对时间（如 "3 hours ago"）与绝对日期（如 "Oct 12, 2025"）被归一化为 UNIX 时间。缺少有效时间戳的条目被丢弃。剩余条目标注其来源标的/问题，并在窗口内排序。

### S1.2 股票价格数据

**来源与时间窗** 我们从公开金融 API（yfinance）获取美国股票价格。对交易日 t，构成截至 t−1 的 10 天回看窗口以缓解同日泄漏；若未给定日期，则使用最新快照。

**标的池与查询** 我们追踪一个小型精选标的池（默认 15 个代码）。对带日期的查询，我们在半开区间 [start, end+1) 下载日线数据，以匹配数据提供方的约定；当前价格取为最近可用的成交/报价。

**归一化** 我们在暴露当前价格的同时，提供一份紧凑的日线历史，包含日期、复权收盘价与成交量。若某日的收盘价不可用，则回退到当天内可得的最佳价格。

### S1.3 Polymarket 价格数据

**来源与时间窗** 我们使用公开端点进行市场发现以及价格/历史查询。与股票一样，每个 token 的历史使用截至 t−1 的 10 天回看窗口以减少泄漏。

**市场发现** 我们发现活跃（或按日期过滤）的市场，收集问题、类别、结果、token ID 与 URL（缺失时从 event slug 构造）。我们进一步通过以下方式过滤出经过验证的子集：对共享同一 event slug 的市场去重、要求有可观察的历史、并移除价格区间低于最小阈值的近似平坦序列。

**归一化** 对每个 token，我们暴露当前价格（在 t 或最新）以及带日期与价格的逐日历史。交易所报价被归一化为 [0, 1] 区间的概率（端点返回分币时除以 100）。

## S2. Prompting 细节

在 LiveTradeBench 中，每个交易步骤被构造成一个结构化文本 prompt，引导 LLM 的决策过程。我们定义了一个市场特定的决策 prompt，它构成完整的模型输入，由两部分组成：动态上下文 prompt 与固定指令头。上下文 prompt 总结 agent 的当前观察——市场状态、近期新闻与账户信息——而指令头给出全局目标、组合原则与输出要求。由于全文较长，我们把每个市场的 prompt 分放在两张表中（股票：表 S2、S3；Polymarket：表 S4、S5）。以下小节详细描述它们。

**股票上下文 prompt** 上下文 prompt 与观察空间对应，包含三个要素：市场分析（每个代码的当前价格与简短近期历史）、按代码分组的近期新闻，以及显示历史配置与累计表现的账户信息（表 S2）。这个动态块提供了决策推理所需的局部状态与外部信号。

**股票决策 prompt** 决策 prompt（表 S3）把上述上下文与带日期的头部、明确的交易目标与评估标准（风险调整后收益、分散化、换手率意识）、组合原则、可交易资产列表，以及只输出 JSON 的 schema（指定 reasoning 与 allocations 字段，权重之和为 1.0，含 CASH）结合在一起。这构成发送给模型的完整 prompt，并把输出约束为与组合动作空间一致。

**Polymarket 上下文 prompt** 对预测市场，上下文 prompt 按问题组织市场分析，给出 YES/NO 价格（隐含概率）与简短历史、按问题分组的近期新闻，以及显示配置（含 CASH）与表现的账户信息（表 S4）。这种表示强调 agent 的信念状态与头寸历史。

**Polymarket 决策 prompt** 决策 prompt（表 S5）把上下文信息与任务特定指令结合起来：agent 对每个问题最多只能选择一侧（YES 或 NO），把内部信念（p）与市场概率 pmkt 相比较，同时考虑交易成本，并输出在可用结果与 CASH 上归一化为和 1.0 的配置。与股票设定一样，这构成完整的模型输入，强制产出可执行的组合配置。

表 S2：股票上下文 prompt 示例。

```
Example of stock context prompt
MARKET ANALYSIS:
AAPL: Current price is $263.51
  - 2025-10-24: close price $263.52 (Change: +3.94 (+1.52%))
  - 2025-10-23: close price $259.58 (Change: +1.13 (+0.44%))
  - 2025-10-22: close price $258.45 (Change: -4.32 (-1.64%))
  - 2025-10-21: close price $262.77 (Change: +0.53 (+0.20%))
  - 2025-10-20: close price $262.24 (Change: +9.95 (+3.94%))
  - 2025-10-17: close price $252.29 (Change: +4.84 (+1.96%))
  - 2025-10-16: close price $247.45 (Change: -1.89 (-0.76%))
  - 2025-10-15: close price $249.34 (Change: +1.57 (+0.63%))
  - 2025-10-14: close price $247.77 (Change: N/A)
...
AMZN: ...

RECENT NEWS:
• AAPL:
  - Did Buffett Sell Apple and Bank of America too Early? (2025-10-23)
    (0:30) - How Do You Know When To Sell Your Investments? (4:10)
    - Breaking Down Warren Buffett's
    Recent Stock Moves; (12:00) - Should You Consider Selling......
  - Apple (AAPL) Stock Rockets to Record High on iPhone 17 Hype
  | What's Next? (2025-10-23)
    Apple (AAPL) Stock Rockets to Record High on iPhone 17
    Hype | What's Next? - TechStock²....
  - AMZN, META and AAPL Forecast { Major US Stocks Look to Rally (2025-10-23)
    Major U.S. tech stocks are showing signs of strength ahead of Friday's session.
    Amazon, Meta, and Apple all
    point to continued bullish momentum,......
...
• AMZN: ...

ACCOUNT INFO:
  Recent Historical Allocations under this account:
    - Asset Allocation at 2025-10-10: {'AAPL': '0.08',
    'MSFT': '0.11', 'NVDA': '0.12', 'JPM': '0.05', 'V':
    '0.04', 'JNJ': '0.05', 'UNH': '0.05', 'PG': '0.04',
    'KO': '0.03', 'XOM': '0.04', 'CAT': '0.05', 'WMT':
    '0.05', 'META': '0.10', 'TSLA': '0.05', 'AMZN':
    '0.08', 'CASH': '0.06'} (Accumulated return rate: 3.6%)
...
    - Asset Allocation at 2025-10-23: {'AAPL': '0.16',
    'MSFT': '0.11', 'NVDA': '0.11', 'JPM': '0.04', 'V':
    '0.04', 'JNJ': '0.04', 'UNH': '0.04', 'PG': '0.03',
    'KO': '0.03', 'XOM': '0.05', 'CAT': '0.05', 'WMT':
    '0.04', 'META': '0.10', 'TSLA': '0.06', 'AMZN':
    '0.07', 'CASH': '0.03'} (Accumulated return rate: 5.6%)
```

表 S3：股票决策 prompt 示例。

```
Example of stock decision prompt

Today is 2025-10-24 (US Eastern Time).
You are a professional portfolio manager.
Analyze the market data and generate a complete portfolio allocation.
MARKET ANALYSIS: ...
RECENT NEWS: ...
ACCOUNT INFO: ...
PORTFOLIO MANAGEMENT OBJECTIVE:
- Improve total returns by selecting allocations with
higher expected return per unit of risk.
- Aim to outperform a reasonable baseline (e.g., equal-weight of AVAILABLE ASSETS)
over the next 1{3 months.
- Use CASH tactically for capital protection in unfavorable markets.
EVALUATION CRITERIA:
- Prefer allocations that increase expected excess return and
improve risk-adjusted return.
- Maintain sector and factor diversification.
- Be mindful of turnover and liquidity.
PORTFOLIO PRINCIPLES:
- Diversify across sectors and market caps.
- Consider market momentum and fundamentals.
- Balance growth and value opportunities.
- Maintain appropriate position sizes.
- Total allocation must equal 1.0.
- CASH is a valid asset.

AVAILABLE ASSETS: AAPL, MSFT, NVDA, JPM, V, JNJ, UNH, PG,
KO, XOM, CAT, WMT, META, TSLA, AMZN, CASH

CRITICAL: Return ONLY valid JSON. No extra text.
REQUIRED JSON FORMAT:
{
 "reasoning": "Brief explanation about why this allocation improves return rate",
 "allocations": {
   "AAPL": 0.25,
   "MSFT": 0.20,
   "NVDA": 0.15,
   "CASH": 0.40
 }
}
RULES:
1. Return ONLY the JSON object.
2. Allocations must sum to 1.0.
3. CASH allocation should reflect market conditions.
4. Use double quotes for strings.
5. No trailing commas.
6. No extra text outside the JSON.
Your objective is to maximize return while considering
previous allocations and performance history.
```

表 S4：Polymarket 上下文 prompt 示例。

```
Example of Polymarket context prompt
MARKET ANALYSIS:
Question: US recession in 2025?
  - Betting YES current price: 0.050
  - Betting NO current price: 0.930
  - Betting YES History:
  - 2025-10-21: 0.0600 (Change: +0.00 (+9.09%))
  - 2025-10-20: 0.0550 (Change: +0.00 (+0.00%))
  ...
  - 2025-10-12: 0.0650 (Change: +0.00 (+0.00%))
  - 2025-10-11: 0.0650 (Change: N/A)
  - Betting NO History:
  - 2025-10-21: 0.9400 (Change: -0.01 (-0.53%))
  - 2025-10-20: 0.9450 (Change: +0.00 (+0.00%))
  ...
  - 2025-10-12: 0.9350 (Change: +0.00 (+0.00%))
  - 2025-10-11: 0.9350 (Change: N/A)
...
Question: Russia x Ukraine ceasefire in 2025?
    ...

RECENT NEWS:
• Fed rate hike in 2025?:
  - Fed Interest Rate Predictions for the Next 3 Years: 2025-2027
  (2025-10-20)
    Expert analysis of interest rate predictions for 2025, 2026, and 2027.
    Understand the factors driving rate changes and their impact on consumers and......
  - Best CD rates Oct. 21, 2025 (2025-10-20)
    Investors need to recognize that average CD rates rise and fall in close alignment
    with Federal Reserve monetary policy changes, specifically fluctuations......
  - Hawkish BOJ board member keeps up calls for more rate hikes (2025
  -10-20)
    Japan has a "prime opportunity" to raise interest rates as its economy is
    weathering the hit from U.S. tariffs, central bank board member Hajime Takata
    said......
...
• Russia x Ukraine ceasefire in 2025?:
    ...

ACCOUNT INFO:
Recent Historical Allocations under this account:
    - Asset Allocation at 2025-10-07: {'Will Gold close under $2,500 at the end of 2025?
    _No': '0.20', 'Fed rate hike in 2025?_No': '0.15', 'Tether insolvent in 2025?_No':
    '0.15', 'Will 1 Fed rate cut happen in 2025?_No': '0.15', 'Will Google have the top
    AI model on December 31?_Yes': '0.10', 'Sundar Pichai out as Google CEO in
    2025_No': '0.10', 'USDT depeg in 2025?_No': '0.10', 'CASH': '0.05'} (Accumulated
    \\return rate: -0.1%)
...
    - Asset Allocation at 2025-10-20: ...
```

表 S5：Polymarket 决策 prompt 示例。

```
Example of Polymarket decision prompt

Today is 2025-10-21 (UTC).
You are a professional prediction-market portfolio manager. Analyze
the market data and generate a complete portfolio allocation.
MARKET ANALYSIS: ...
RECENT NEWS: ...
ACCOUNT INFO: ...

PORTFOLIO MANAGEMENT OBJECTIVE:
- For each market, YES and NO are two assets. Allocate to only one at
a time. CASH is also valid.
- YES and NO prices represent public-implied probabilities.
DECISION LOGIC:
- Derive market probability p_mkt from price.
- Go LONG {question}_YES if p > p_mkt + costs.
- Go LONG {question}_NO if p < p_mkt - costs.
- ...

PORTFOLIO PRINCIPLES:
- Diversify across markets.
- No simultaneous YES and NO allocations.
- ...

AVAILABLE ASSETS: US recession in 2025?_Yes, US recession in 2025?_No,
Tether insolvent in 2025?_Yes, Tether insolvent in 2025?_No, Fed rate
hike in 2025?_Yes, Fed rate hike in 2025?_No, USDT depeg in 2025?_Yes,
USDT depeg in 2025?_No, Sundar Pichai out as Google CEO in 2025?_Yes,
Sundar Pichai out as Google CEO in 2025?_No, Fed emergency rate cut in
2025?_Yes, Fed emergency rate cut in 2025?_No, Russia x Ukraine
ceasefire in 2025?_Yes, Russia x Ukraine ceasefire in 2025?_No, CASH

CRITICAL: Return ONLY valid JSON. No extra text.
REQUIRED JSON FORMAT:
{
 "reasoning": "Brief explanation of the allocation",
 "allocations": {
   "US recession in 2025?_Yes": 0.25,
   "Tether insolvent in 2025?_No": 0.15,
   "CASH": 0.60
 }
}

RULES:
1. Return ONLY the JSON object.
2. Allocations must sum to 1.0.
3. Only one side (YES or NO) per question may be non-zero.
4. Use double quotes; no trailing commas.
Your objective is to maximize portfolio return using past allocations
and performance history.
```

## S3. 模型细节

我们评估跨家族的主流 chat LLM，股票与 Polymarket 设定使用同一模型池。表 S1 总结了评估中包含的家族与具体变体。

**供应商路由** 我们通过一个薄客户端（LiteLLM）调用模型，自动解析供应商。以厂商名为前缀的模型字符串会相应路由（如 openai/gpt-4o-mini、anthropic/claude-3-5-sonnet、gemini/gemini-2.5-pro、x-ai/grok-4）；无前缀的名称默认走 Together AI。对标准 chat 模型，我们设 temperature = 0.3、max tokens = 16000；对结构化推理风格（如 gpt-5、o3-2025-04-16），我们省略这些参数以匹配供应商默认值。

表 S1：LiveTradeBench 中使用的模型家族与变体。

| 家族 | 模型 |
|---|---|
| OpenAI | GPT-5, GPT-4.1, GPT-4o, GPT-o3 |
| Anthropic | Claude-Opus-4.1, Claude-Opus-4, Claude-Sonnet-4, Claude-Sonnet-3.7 |
| Google | Gemini-2.5-Pro, Gemini-2.5-Flash |
| xAI | Grok-4, Grok-3 |
| Meta | Llama4-Maverick, Llama4-Scout, Llama3.3-70B-Instruct-Turbo |
| Qwen | Qwen3-235B-A22B-Instruct, Qwen3-235B-A22B-Thinking, Qwen2.5-72B-Instruct |
| DeepSeek | DeepSeek-R1, DeepSeek-V3.1 |
| Moonshot | Kimi-K2-Instruct |

**响应 schema** 所有模型都被要求返回单个 JSON 对象，字段为 reasoning 与 allocations。allocations 在可用资产上之和必须为 1.0，可以包含 CASH。响应在应用到账户之前会被解析与校验。

## S4. 前端 UI 细节

本节详细描述 LiveTradeBench 的前端 UI，它由六个主要页面组成。第一个是 Leaderboard 页面（图 S1），按收益率显示各 LLM 模型的排名。每个 Stock 模型起始资金为 1000 USD，每个 Polymarket 模型起始资金为 500 USD。第二个是 Stock 页面（图 S2），展示全部 21 个 LLM Stock 模型；该页面上有每个 LLM Stock 模型的详细 model card（图 S3）。第三个是 Polymarket 页面（图 S4），展示全部 21 个 LLM Polymarket 模型；该页面上有每个 LLM Stock 模型的详细 model card（图 S5）。第四个是 News 页面（图 S6），展示股票市场与 Polymarket 的最新新闻。

图 S1：Leaderboard 页面截图。该页面按收益率显示各 LLM 模型的排名。（原文第 32 页）

图 S2：Stock 页面。该页面展示 21 个不同的 LLM Stock 模型。（原文第 33 页）

图 S3：Stock model card。某个 model card 的详细视图，显示当前与历史配置、收益以及 LLM 输入/输出。（原文第 34 页）

图 S4：Polymarket 页面截图。该页面展示 21 个不同的 LLM Polymarket 模型。（原文第 35 页）

图 S5：Polymarket model card。某个 model card 的详细视图，显示当前与历史配置、收益以及 LLM 输入/输出。（原文第 36 页）

图 S6：News 页面截图。该页面展示股票市场与 Polymarket 的新闻。每张新闻卡片都会跳转到原始来源。（原文第 37 页）
