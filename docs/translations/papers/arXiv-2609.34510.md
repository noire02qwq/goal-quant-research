# AI 能在加密货币市场赚钱吗？衡量回测与真实市场的差距（Can AI Make Money in Crypto? Measuring the Gap from Backtests to Real Markets）

> 来源：https://arxiv.org/abs/2609.34510
> 原文：docs/papers/arXiv-2609.34510.pdf
> 翻译日期：2026-11-11 ｜ 范围：全文 ｜ 方式：机器翻译初稿，未经人工校对
> 引用于：docs/literature/W5-real-eval-fault-style.md

**作者**：Xingtong Yu¹、Jiarun Zhou²、Guanlin Ding²、Wenkang Wei²、Jiarui Liu³、Chang Zhou²、Fangzhou Ge¹、Chenyi Xu¹、Xikun Zhang⁴、Renqiang Luo³、Jie Zhang⁵、Hong Cheng¹、Xinming Zhang²、Hui Zhang²*、Yuan Fang⁶*

**机构**：¹香港中文大学　²中国科学技术大学　³吉林大学　⁴RMIT 大学　⁵Infplane Computing Lab　⁶新加坡管理大学

arXiv:2609.34510v1 [cs.AI]，2026 年 9 月 28 日

## 目录

- 摘要
- 1 引言
- 2 相关工作
- 3 基准评测协议（3.1 被评估方法 / 3.2 交易任务形式化 / 3.3 评估协议）
- 4 实证结果与分析（4.1 历史回测 / 4.2 基于交易所的模拟盘交易 / 4.3 实盘交易 / 4.4 洞见与未来方向讨论）
- 5 结论
- AI 使用声明、伦理声明与可重复性声明
- 附录 A 被评估方法
- 附录 B 实现细节（B.1 通用设置 / B.2 资产细节 / B.3 超参数设置 / B.4 提示词设计）

## 摘要

基于 AI 的交易方法已从机器学习、强化学习迅速演进到大语言模型（LLM）与交易智能体，但其性能仍主要依靠历史回测来评估。这类评估所能提供的证据十分有限：既难以说明方法能否泛化到未曾见过的未来市场，也难以说明回测表现能否在现实交易摩擦（如延迟、滑点、流动性约束与市场冲击）下维持。我们提出一个统一基准，通过三个逐步逼近现实的阶段——历史回测、面向未来行情的交易所模拟盘交易、真金白银的实盘交易——在加密货币市场中评估代表性的机器学习、强化学习、基于 LLM 以及基于智能体的交易方法。这三个阶段从历史走向未见的未来市场以提升时间真实性，从离线模拟走向实盘执行以提升执行真实性。借助这一协议，我们可以量化"回测到实盘"之间的差距，识别性能从何时开始恶化，并比较该差距在不同主要 AI 交易方法类别之间有何不同。我们还提供了一个支持全部三个评估阶段的统一开源系统，以及一个持续更新基准结果的公开平台。代码见 https://github.com/Starlien95/Awesome-TradingAI。

## 1 引言

人工智能在金融交易中的应用日益广泛，催生了大量基于机器学习（ML）、强化学习（RL）、大语言模型（LLM）和交易智能体的方法。这些方法在处理市场信息、做出交易决策的方式上各不相同，但通常都在历史回测或模拟环境中接受评估。此类评估可以展示方法在过去市场数据上的表现，却难以证明这种表现能否在未见过的未来数据或真实交易条件下延续。

回答这一问题需要考虑评估真实性的两个维度。其一是时间真实性：在历史数据上表现良好的方法，未必能随着市场状况的变化而泛化到未来市场；当模型使用历史数据进行大量调参与筛选时，这一问题尤为突出。其二是执行真实性：离线评估简化了交易决策转化为实际订单与已实现收益的过程，而部署后的系统必须在延迟、滑点、流动性、市场冲击等现实执行约束下与交易所交互。这两个维度共同帮助我们区分：性能下降究竟源于对未来市场泛化能力不足，还是源于交易决策在实盘市场中的执行过程。

现有基准尚不能提供这一完整视角。许多基准仍依赖历史或预先采集的数据集。较新的基准通过在新到达的市场数据上评估系统来提升时间真实性，但仍未采用贯穿历史回测、交易所模拟盘交易与真金白银实盘交易的统一分阶段协议来评估方法。此外，现有基准通常局限于特定的方法类别，只关注 RL 或基于 LLM 的交易系统，这使得在同一评估协议下比较不同类别的 AI 交易方法、或判断"回测到实盘"的差距在各类方法之间有何不同都变得困难。

为填补这些空白，我们提出一个用于在加密货币市场评估 AI 交易方法的统一基准与开源系统。我们的基准覆盖 ML、RL、基于 LLM 与智能体交易算法中的代表性方法，并通过包含历史回测、交易所模拟盘交易和实盘交易的三阶段协议进行一致评估。这些阶段从历史走向未见的未来市场、从离线模拟走向交易所执行或实盘执行，逐步提升时间真实性与执行真实性。分阶段评估使我们能够测量回测到实盘的差距，并比较不同类别 AI 交易方法的交易表现如何变化。我们将所有方法整合进统一的执行与评估框架，发布完整代码库，并提供一个持续更新三个阶段结果的公开仪表盘。

概括起来，本文有以下贡献。（1）我们提出一个统一基准，在共同的评估协议下评估加密货币市场中代表性的 ML、RL、基于 LLM 与智能体交易方法。（2）我们设计了贯穿历史回测、交易所模拟盘交易与真金白银实盘交易的分阶段评估协议，逐步提升时间真实性与执行真实性。（3）我们系统刻画了不同类别 AI 交易方法之间"回测到实盘"的差距。（4）我们发布了支持全部三个评估阶段的完整开源系统，包括被评估方法的实现，以及一个持续更新基准结果的公开平台。

## 2 相关工作

**AI 用于交易。** 基于 AI 的交易方法涵盖若干主要范式。ML 方法通常从历史市场数据中学习预测信号，并用这些信号构建交易策略。近期工作进一步改进了在时间分布漂移、含噪金融数据和跨资产依赖下的预测能力。RL 则直接从交互奖励中学习交易策略，近期方法为高频交易引入了分层决策与市场感知适应机制。更近期的基于 LLM 的方法把文本信息与推理能力纳入交易决策，而交易智能体进一步引入了记忆、反思与多智能体协作等机制。

**AI 交易基准。** 现有 AI 交易基准主要在评估真实性与方法覆盖范围上有所不同。早期基准如 FinRL-Meta 和 TradeMaster 标准化了交易环境与评估协议，但主要在历史市场数据上评估强化学习方法。FinBen、InvestorBench 和 StockBench 将评估扩展到基于 LLM 的金融决策，但仍以语言模型或智能体为中心，而非比较不同类别的交易方法。更近期的基准，包括 DeepFund、Agent Market Arena、LiveTradeBench 和 AI-Trader，通过在新到达的市场数据上评估系统进一步提升了时间真实性。然而，这些基准仍以基于 LLM 的系统为中心，没有在同一贯穿历史回测、交易所模拟盘交易与真金白银交易的分阶段协议下评估异构的交易方法。我们的基准在同一协议下覆盖 ML、RL、基于 LLM 的方法与交易智能体，对这些工作形成补充。

## 3 基准评测协议

### 3.1 被评估方法

我们评估了涵盖 ML、RL、基于 LLM 的交易以及交易智能体的 32 种 AI 交易方法，并以 Bitcoin 买入并持有（Buy & Hold）作为被动市场基准。被评估的方法包括预测模型、序贯决策策略、直接基于 LLM 的交易，以及具备记忆与多智能体协作的基于智能体的系统。详细描述见附录 A。为保证可复现性，凡有公开代码库的方法我们都基于其公开发布的代码构建，并适配到我们的统一交易框架。模型选择完全通过历史回测在模型超参数与交易配置（包括交易窗口、持仓限制和杠杆）上进行。对每种方法，我们选择验证表现最好的配置，并在后续阶段保持不变。详细配置见附录 B。为控制随机性，非 LLM 方法使用固定随机种子，而基于 LLM 的方法与交易智能体的每次历史回测运行三次并取平均。

### 3.2 交易任务形式化

我们考虑由十只大市值加密货币构成的可交易资产池，它作为整个基准中共同的候选资产集合。资产细节见附录 B.2。根据交易形式化方式的不同，方法可以在该资产池中操作预先指定的资产，也可以自主选择资产。在每个决策步 t，交易方法 m 使用截至该时刻可得的市场信息来决定交易什么、如何交易。我们把这一过程概括为：

```
St,m = Sm (It,m ),       at,m = Πm (It,m , St,m ),                       (1)
```

其中 I_{t,m} 表示方法 m 可得的市场信息，例如历史开高低收与成交量（OHLCV）数据、衍生的市场因子、组合状态，或与所交易资产相关的文本信息。S_{t,m} 表示被选中交易的资产，例如多资产策略中选中的加密货币，或预先指定的资产。动作 a_{t,m} 指定所选资产应当如何交易，例如买入、卖出或持有，选择做多或做空方向，确定仓位大小，或指定止损、目标价等风险控制指令。

**机器学习。** 对 ML 方法而言，I_{t,m} 由从历史 OHLCV 数据中提取的 52 个市场因子（Alpha52）组成。我们从原始市场数据构造这些因子，并把它们作为 ML 模型的唯一输入。每个模型随后在预先指定的时间跨度上预测每只候选资产的未来收益。沿用先前工作的做法，我们按预测收益对候选资产排序，选取前 k 只作为 S_{t,m}，并在所选资产上构建只做多的组合。

**强化学习。** 对 RL 方法而言，交易资产是预先指定的，而不是从候选资产池中动态选择的。RL 智能体使用与 ML 方法相同的 Alpha52 市场因子作为输入。RL 策略不预测未来收益并对资产排序，而是直接根据当前市场状态决定如何调整预先指定资产上的持仓。我们采用只做多的设定，并在把每个 RL 方法的决策映射为可执行订单时保留其原始的动作形式化。

**基于 LLM 的方法与交易智能体。** 对基于 LLM 的方法与交易智能体，我们根据候选资产可得的市场数据与资产相关文本信息构造方法特定的提示词。视方法不同，提示词或指定目标资产，或提供一组候选资产的信息供方法自行选择交易对象，随后方法确定相应的交易动作。详细提示词模板与输入配置见附录 B。具体而言，DeepSeek 与 Qwen 输出所选资产以及买入、卖出或持有决定、交易数量、止损价与目标价；FinGPT 采用只做多的策略，决定交易哪只资产以及是否对现有持仓买入或卖出；FinMem 选择一只资产，并在三种离散动作中做选择——建立全部多头、建立全部空头、维持当前持仓；FinAgent 与 TradingAgents 输出所选资产、多空方向以及相应的仓位大小，仓位上限按其各自的交易协议设为账户价值的 15%。

### 3.3 评估协议

我们通过三个阶段评估交易方法：历史回测、交易所模拟盘交易与真金白银交易。对任何进入后续阶段的方法，其交易形式化与所选配置保持不变，而市场时间轴与执行环境则逐步逼近真实部署。

**评估指标。** 我们使用量化金融中成熟的表现与风险指标评估交易结果。具体而言，累计收益（Cumulative return）衡量评估期内组合价值的净变化；Jensen's alpha（Jensen, 1968）衡量策略相对于其市场风险敞口所隐含收益的超额收益，本评估以 Bitcoin 买入并持有作为市场基准；Sharpe 比率（Sharpe, 1966）衡量收益相对于策略所承担总风险的水平，给出风险调整后的表现度量；最大回撤（Maximum drawdown，Magdon-Ismail & Atiya, 2004）刻画组合价值从峰值到谷底的最大跌幅，反映持续亏损的严重程度；波动率（Volatility，Fabozzi et al., 2008）衡量组合收益的变异性，刻画收益风险的整体水平。

**执行与交易成本。** 我们使用 OKX 加密货币交易所作为模拟盘与实盘交易的执行环境。所有交易都以 taker 订单提交，以便利用市场可得流动性更快成交。多头仓位通过现货交易实现，每笔交易收取 0.10% 的手续费；空头仓位通过永续合约实现，每笔收取 0.05% 的 taker 手续费。这些费率遵循本实验所用的 OKX taker 费率表。我们在历史回测中应用相同的交易成本，以保证各评估阶段的交易成本假设一致。

**历史回测。** 我们首先在从 OKX 加密货币交易所收集的历史市场数据上评估每种方法。训练数据为 2021-01-01 至 2023-12-31，验证数据为 2024-01-01 至 2024-12-31，测试数据为 2025-01-01 至 2025-12-31。验证期用于模型与交易配置的选择，而所有报告的回测结果都在留出的 2025 年测试期上计算。在每个决策步，方法只使用当时可得的信息，其交易按相应的历史市场价格模拟。该阶段衡量每种方法在模拟交易下本会在过去市场中取得怎样的表现，为后续前瞻性评估提供历史基线。

**模拟盘交易。** 随后，我们把历史回测中表现最好的方法推进到交易所托管的模拟盘环境中，在新到达的市场数据上进行前瞻性评估。模拟盘交易从 2026-06-04 持续到 2026-09-21。为保持各方法类别的代表性，我们依据回测结果从每个类别中选出表现最好的方法。与回测不同，在做决策时未来市场走势尚属未知，订单以模拟资金提交到交易所环境。因此，该阶段检验的是：强劲的回测表现能否在更真实的执行条件下于未见的未来市场中延续。

**实盘交易。** 最后，我们把交易所模拟盘交易中表现最好的方法推进到交易所上的实盘交易。实盘交易从 2026-08-24 持续到 2026-09-21。具体而言，我们选择模拟盘期间 Jensen's alpha 最高的五种方法，以真实资金部署。这些方法继续进行前瞻性决策，但其订单现在在实盘市场中执行并产生真实的交易结果。该阶段检验的是：强劲的模拟盘表现在方法以真实资金部署后能否延续。

## 4 实证结果与分析

我们的实验遵循第 3 节引入的三阶段评估协议。我们先通过历史回测评估所有方法，然后从每个方法类别中选出表现具有代表性的方法进行交易所模拟盘交易，最后把截至 2026-08-23 模拟盘 alpha 最高的前四种方法部署到真金白银的交易中。

### 4.1 历史回测

**RQ1：不同类别的 AI 交易方法在历史回测下表现如何？**

表 1：所评估交易方法在 2025-01-01 至 2025-12-31 的回测表现。

```
  Method                  Cum. Ret. (%)↑      Alpha (%)↑      Sharpe↑     Max DD (%)↓        Vol. (%)↓
  BUY&HOLD                    -7.63              0.00          -0.18          33.01           41.74
  LightGBM                    8.57             13.70          0.31           52.05           42.14
  CatBoost                   21.46             25.61          0.57           61.93           58.07
  Linear                     21.08             25.87          0.63           44.59           51.30
  XGBoost                    41.93             53.60          1.08           42.42           59.50
  MLP                        30.33             39.15          1.08           35.24           43.06
  TabNet                     34.52             45.34          1.27           32.67           41.59
  TCN                        62.94             86.10           1.62          29.10           59.48
  GRU                        29.66             37.40          1.02           38.14           44.49
  LSTM                       32.90             39.33          0.82           44.07           61.76
  SFM                        18.31             21.60          0.68           43.95           41.37
  GeneralPTNN                16.44             20.54          0.55           34.04           45.80
  ALSTM                      21.17             26.30          0.70           51.26           46.48
  TFT                        10.53             13.93          0.38           50.30           42.47
  Transformer                 5.32              8.90          0.20           41.11           41.64
  KRNN                        9.78             15.32          0.33           35.75           45.88
  Localformer                24.38             30.63          0.68           51.19           55.30
  TRA                        25.08             31.39          0.54           52.94           70.66
  AdaRNN                     19.41             26.87          0.46           45.59           64.38
  TCTS                       10.92             16.53          0.40           50.06           41.56
  ADD                        -1.37              1.71          -0.05          52.05           41.72
  DoubleEnsemble             37.48             47.97          1.04           48.39           55.52
  GATs                       71.70             98.03          1.57           33.97           70.08
  Sandwich                   23.16             28.66          0.62           35.89           57.12
  IGMTF                       1.72              5.54          0.06           58.33           44.80
  MacroHFT                  -10.07             -3.10          0.04           45.18           50.58
  EarnHFT                    -38.57            -76.96         -1.75          45.75           44.43
  DeepSeek                   -43.30            278.44         -0.22          96.85          261.12
  Qwen                       -68.62             38.38         -0.62          82.85          188.58
  FinGPT                     -15.15             -7.03          0.03          45.13           60.08
  FinMem                     -20.76            -19.30         -0.78          41.08           29.95
  FinAgent                   -41.06            -48.14         -1.61          45.51           32.78
  TradingAgents               -9.16             -3.36         -0.25          31.79           38.02
```

**回测表现。** 表 1 报告了所有被评估方法在 2025 年的历史回测表现。我们首先观察到不同方法类别之间存在明显的性能差异。在 24 种 ML 方法中，有 23 种取得正的累计收益，而在同一时期，被评估的 RL、LLM 与基于智能体的方法无一盈利。在后几类方法中，TradingAgents 的表现最接近 Buy & Hold，而其他若干方法的亏损要大得多。其次，类别层面的强势并不意味着每个个体方法都一贯强劲。在 ML 方法内部，累计收益从 −1.37% 到 71.70% 不等，尽管这些方法使用相同的市场因子与交易协议。GATs 与 TCN 取得了最强的结果，而另外若干 ML 方法只有适度的收益。因此，即便在共同的交易形式化下，性能差异依然可观。第三，不同方法在各个评估维度上各有所长。GATs 取得最高的累计收益，而 TCN 取得最高的 Sharpe 比率与最低的最大回撤。DeepSeek 尽管最终收益为负却取得了最高的 alpha，这反映出一条波动极大的杠杆交易轨迹，中间夹杂着大量盈亏。其高波动率与最大回撤进一步说明，某一指标上的强势并不必然对应稳健的整体交易表现。这些结果表明，没有任何单一指标能够完全刻画方法的交易表现，因此需要同时在盈利性与风险两个维度上进行评估。

图1：模拟盘交易的累计收益（原文第6页）

图2：实盘交易的累计收益（原文第6页）

表 2：回测（BT）与模拟盘交易（PT）的表现。

```
 Method               Cum. Ret. (%)↑        Alpha (%)↑        Sharpe↑       Max DD (%)↓       Vol. (%)↓
                       BT         PT       BT          PT    BT        PT    BT       PT      BT      PT
 BUY&HOLD                  30.35             0.00            1.88              13.56         41.78
 XGBoost              33.95      27.53     64.23    45.32   2.90 2.59 12.01          9.56   37.88   32.15
 MLP                  -45.56     -46.79   -256.24   -251.80 -4.69 -4.77 49.63        48.97   45.52   44.03
 TabNet             -54.37     -50.80   -257.37   -237.74 -10.30 -8.34 56.27       52.72   24.91   27.67
 TCN                  -35.24     -33.20   -191.51   -188.46 -3.42 -3.24 37.76        37.45   42.30   42.81
 LSTM                  24.09      34.08     18.49    35.62   1.40 1.68 17.00         17.00   55.03   56.53
 TRA                   -3.84      -2.98    -80.01    -82.15 -0.04 -0.01 19.05        20.53   44.59   46.01
 DoubleEnsemble    -18.96     -10.78   -118.59    -97.65 -2.04 -0.98 29.60        23.91   35.19   40.13
 GATs                -15.88      -8.79   -147.79   -117.05 -1.24 -0.56 28.28        22.80   49.15   50.42
 MacroHFT           41.01      38.12    30.09     24.20    2.45    2.32   16.69    16.68   47.80 47.40
 DeepSeek           7.35       9.53    1.61      -0.91    1.43    1.32   3.31      8.83   12.40 25.38
 Qwen                11.35      37.77    15.66     53.15    1.18    2.94   8.49     11.83   20.77 38.99
 FinGPT             20.04      16.85    14.15      3.51    1.90    1.62   9.41     8.97    35.38 36.13
 FinMem            -6.63       5.28    -20.98     -2.93   -0.51   0.74   20.43    15.10   34.23 28.68
 FinAgent            0.20        1.73    -10.08    -15.28   -0.21   0.43   15.31     7.88   22.50 16.56
```

### 4.2 基于交易所的模拟盘交易

**RQ2：回测表现在前瞻性模拟盘交易中还能保留多少？**

**模拟盘交易表现。** 图 1 报告了所选方法在模拟盘交易期间的累计收益曲线，表 2 汇总了它们的最终表现。这些结果呈现出与历史回测明显不同的模式。我们首先观察到不同方法类别之间出现了惊人的反转。在进入模拟盘交易的方法中，八种 ML 方法在 2025 年历史回测里全部盈利，而入选的六种 RL、LLM 与基于智能体的方法则全部亏损。在模拟盘交易中，这一模式几乎反转：八种 ML 方法中只有两种仍然盈利，而其他类别的六种方法全部取得正收益。其次，这种反转也体现在各组内部的典型表现上。所选 ML 方法的收益中位数从历史回测的 36.0% 降至模拟盘交易的 −9.8%，而非 ML 方法的收益中位数则从 −29.9% 升至 13.2%。这些结果表明，当评估从历史走向未见的未来市场时，不同交易范式的相对优势可能发生实质性变化。

图3：回测与模拟盘交易的累计收益（原文第7页）

**回测与模拟盘交易的对比。** 我们进一步在 2026-06-04 至 2026-09-21 的同一市场区间上比较回测与模拟盘交易。表 2 报告了两种设定下的结果，图 3 则对比了代表性方法的累计收益曲线。我们首先观察到，即便对同一方法、同一市场区间，回测与模拟盘交易之间也存在显著差异，Qwen 的累计收益差距高达 26.42 个百分点（pp）。值得注意的是，模拟盘交易并非系统性地劣于回测：14 种被评估方法中有 10 种在模拟盘交易中取得了更高的累计收益。其次，这种差异不止于累计收益，而是扩展到更广泛的风险收益画像。在这 14 种方法上，回测到模拟盘的平均绝对差距在累计收益上达到 6.25 pp，在 alpha 上达到 14.05 pp，此外 Sharpe 比率相差 0.62、最大回撤相差 2.98 pp、波动率相差 4.53 pp。因此，回测不仅会误估盈利能力，也会误估交易方法的风险特征。第三，这些差异大到足以改变关于单个方法的实践结论。例如 FinMem 从回测中的负收益变为模拟盘交易中 +5.28% 的正收益；Qwen 从大幅落后于 Buy & Hold 基准变为跑赢它，而 XGBoost 则呈现相反的模式。这些反转表明，仅凭回测就可能得出关于某方法是否盈利、是否具有市场竞争力的定性不同的结论。

**模拟盘执行差异。** 为探究回测与模拟盘交易之间性能差距的一个可能来源，我们在表 3 中考察预期交易决策与其实际执行之间的差异。我们度量三种差异：延迟（latency），即从生成交易决策到执行之间以秒计的时间；价格差异（price difference），即预期价格与实际成交价格之间的相对差异；以及订单价值偏差（order value deviation），即预期订单价值与实际订单价值之差，按当前账户资金归一化。

表 3：模拟盘交易的执行差异。

```
 Method                    Latency Price Diff. Order Value
                             (s)     (‰)       Dev. (‰)
 XGBoost                14.57    0.31        0.41
 MLP                    13.31     0.35        0.22
 TabNet                18.17    0.50        0.63
 TCN                    16.89    0.33        0.22
 LSTM                   27.98    0.40        0.30
 TRA                    23.07    0.35        0.23
 DoubleEnsemble 17.48       0.35        0.16
 GATs                17.45    0.27        0.08

 MacroHFT            5.32     0.27        0.14
 DeepSeek            53.26    2.37        0.37
 Qwen                90.61    0.18        0.18
 FinGPT              416.89    1.88        0.12
 FinMem           545.33    2.19        1.94
 FinAgent           500.56    1.38        0.26
```

我们首先观察到，执行差异在不同方法类别之间差别显著。ML 方法的平均延迟为 18.6 秒、平均价格差异为 0.36‰，而基于 LLM 的方法这两项分别升至 186.9 秒和 1.48‰，交易智能体则升至 522.9 秒和 1.79‰。因此，在离线回测下看似可比的方法，一旦部署到交易所环境中就可能遇到大不相同的执行条件。其次，更大的执行差异并不会直接转化为更大的回测到模拟盘性能差距。累计收益的绝对差距与延迟（r ≈ 0.05）、价格差异（r ≈ −0.15）或订单价值偏差（r ≈ 0.19）的 Pearson 相关系数（r）（Benesty et al., 2009）都很小。这说明执行效应比单一的延迟、价格或订单规模惩罚更为复杂，其本身无法解释前瞻性表现中观察到的变化。

### 4.3 实盘交易

**RQ3：回测与模拟盘交易在多大程度上反映实盘交易表现？**

**实盘交易表现。** 图 2 报告了 2026-08-24 至 2026-09-21 实盘交易的累计收益曲线，表 4 汇总了相应表现。我们首先观察到真金白银交易中的盈利十分有限。四种方法中只有一种盈利，且没有任何一种跑赢 Bitcoin 买入并持有。四种方法的收益中位数为 −0.56%，而同期市场上涨了 11.63%。其次，即便表现最强的实盘方法也没能产生相对市场的正超额表现。四种方法的 alpha 全部为负，只有 Qwen 维持了正的 Sharpe 比率。因此，通过前述评估阶段筛选出来的方法，在以真实资金部署后仍可能无法给出正的风险调整超额表现。

表 4：回测（BT）、模拟盘交易（PT）与实盘交易（LT）的表现。

```
                  Cum. Ret. (%)↑              Alpha (%)↑                       Sharpe↑            Max DD (%)↓             Vol. (%)↓
 Method
                 BT     PT     LT     BT         PT         LT          BT       PT      LT     BT     PT     LT     BT      PT       LT
 BUY&HOLD           11.63          0.00       0.00      0.00         1.59    1.59     1.59          7.48                 40.66
 LSTM           -2.25 -0.48 -0.33 -54.89 -107.36 -90.88 -1.96 -5.53 -4.88 8.12 9.29 7.66 24.86 18.75 17.25
 TRA            -9.21 -10.82 -14.74 -160.46 -235.95 -284.03 -2.18 -3.11 -4.41 18.38 19.14 21.49 58.71 58.26 51.85
 XGBoost       -3.60 0.34    -0.79  -9.51   -52.32 -57.90 -0.11 -1.31 -1.59 10.24 8.73 9.00 28.54 27.74 25.20
 Qwen          6.18   10.10   3.72   -0.63     15.80      -28.10       1.34    1.85     0.34   4.85   7.27   6.06   29.91 39.28 32.02
```

图4：回测、模拟盘交易与实盘交易的累计收益（原文第8页）

**回测、模拟盘与实盘交易的对比。** 我们进一步在 2026-08-24 至 2026-09-21 之间比较回测、模拟盘交易与实盘交易。表 4 报告了三种设定下的表现，图 4 对比了它们的累计收益曲线。我们首先观察到，从模拟盘交易走到实盘交易会引入额外的性能差距。四种方法中有三种在实盘交易中取得更低的累计收益，模拟盘到实盘的收益差距最高达 6.38 pp。因此，即便市场区间与方法配置保持不变，交易所模拟盘交易也无法完全复现真金白银的结果。其次，总体而言，模拟盘交易仍然比回测更接近实盘交易。在四种方法上取平均后，模拟盘到实盘的绝对差异在全部五项评估指标上都小于回测到实盘的差异。风险调整后表现的改善尤其明显：alpha 的平均绝对差距从 58.85 pp 降至 28.51 pp，Sharpe 比率从 1.91 降至 0.94，降幅分别约为 52% 和 51%。相比之下，累计收益与最大回撤的降幅约为 9%，波动率约为 11%。这些结果表明，模拟盘交易在若干维度上大幅缩小了与真金白银交易的差距，但并未消除直接实盘评估的必要性。

**实盘执行差异。** 为探究模拟盘交易与实盘交易之间残余性能差距的一个可能来源，我们在表 5 中考察真金白银交易下的执行差异。我们沿用与模拟盘交易相同的三项度量：延迟、价格差异与订单价值偏差。我们首先观察到，从模拟盘交易走到真金白银交易时，执行差异显著变大。对四种部署的方法而言，平均价格差异从模拟盘的约 0.31‰ 升至实盘的 1.86‰，增加了近 6 倍；平均订单价值偏差也从 0.28‰ 升至 0.60‰，翻了一倍多。相比之下，平均执行延迟的变化要小得多，从约 39 秒变为约 47 秒。其次，这一增幅因此更多集中在交易决策如何被实现上，而非执行耗时上。特别是执行价格与订单价值上的大幅偏差，为残余的模拟盘到实盘性能差距提供了一个合理来源。模拟盘交易捕捉了基于交易所的执行，但真金白银交易在意图交易与实际成交之间引入了额外差异，这些差异无法在模拟环境中被完全复现。

表 5：实盘交易的执行差异。

```
 Method       Latency Price Diff. Order Value
               (s)       (‰)          Dev. (‰)
 LSTM           10.63      2.63           1.23
 TRA            14.23      2.28           0.50
 XGBoost 13.57            1.39           0.41
 Qwen         151.00      1.13           0.27
```

### 4.4 洞见与未来方向讨论

**回测成功并不能可靠迁移到前瞻性交易结果。** 历史回测中的强劲表现，在方法接受前瞻性评估时可能发生实质性变化。2025 年回测中观察到的方法学模式在模拟盘交易中明显改观：此前较弱的方法变得有竞争力，而许多强劲的 ML 方法失去了优势。更重要的是，这种差异不能仅归因于市场状况的变化：即便在同一市场区间内，回测与模拟盘交易也可能产生实质不同的盈利与风险画像。这些发现说明，仅靠历史回测不足以估计前瞻性交易表现。因此，未来工作应同时强调在变化的市场状况与执行环境下的稳健性，而不是优化单一的历史回测。

**模拟盘交易缩小了与真金白银交易的差距，但没有消除它。** 模拟盘交易在回测与实盘部署之间提供了一个有意义的中间阶段。在所评估的指标上，模拟盘结果平均而言始终比回测结果更接近实盘结果，其中 alpha 与 Sharpe 比率的改善尤其显著。然而，在相同方法、相同市场区间上评估时，模拟盘与实盘之间仍存在可度量的差异。因此，未来工作应采用分阶段评估协议：在回测之后进行模拟盘交易以评估前瞻性表现，在最终实盘验证与部署之前提供一个必要的、不承担真实资金风险的中间阶段。

**当前交易方法在实盘部署下无法维持跑赢市场的表现。** 真金白银交易暴露出一个更根本的局限：所部署的方法无一跑赢市场，且全部呈现负 alpha。这说明主要挑战不只是在基准内找出最强的方法，而是开发出一旦暴露于变化的市场与真实执行便仍能维持超额收益的策略。因此，未来工作应超越对绝对回测收益的优化，明确以持久超额收益、部署稳健性，以及离线评估与真实交易结果之间的一致性为目标。

## 5 结论

我们提出了一个超越历史回测的 AI 交易方法统一评估基准，在贯穿历史回测、交易所模拟盘交易与真金白银实盘交易的三阶段协议下，覆盖代表性的 ML、RL、基于 LLM 与基于智能体的方法。通过逐步提升时间真实性与执行真实性，该基准得以系统测量回测到实盘的差距。我们的结果表明，强劲的历史表现并不能可靠迁移到前瞻性交易，而模拟盘交易虽比回测更接近实盘表现，但在真金白银执行下仍留有明显差距。此外，被评估的方法无一能在实盘交易中维持跑赢市场的表现，凸显了超越单一历史场景下性能优化的必要性。最后，我们发布了一个开源系统与公开平台，支持在全部三个阶段上进行可复现的评估，并在新到达的市场数据上持续更新模拟盘与实盘交易结果。

## AI 使用声明

我们仅使用 AI 工具润色语言、提升稿件可读性。这些工具未被用于产生研究想法、设计或实现方法、开展实验，或分析与解释结果。作者对本文最终内容承担全部责任。

## 伦理声明

我们未发现本研究引发的具体伦理关切。该基准面向研究与评估用途，所报告的结果不应被解读为投资建议或对未来交易表现的保证。

## 可重复性声明

实现细节在附录中提供，以支持实验的复现。我们还公开了源代码，便于独立验证与进一步研究。

*（参考文献从略）*

## 附录 A 被评估方法

我们在此详细描述基准中评估的方法。该基准覆盖基于 AI 交易的四大主要范式——机器学习、强化学习、基于 LLM 的交易与交易智能体——以及一个被动的 Buy & Hold 基准。这些方法在如何表示市场信息、如何生成交易决策上差异很大，从数值预测模型到自主的基于 LLM 的交易系统不一而足。我们在表 6 中汇总被评估的方法。该表比较各方法所使用的信息（包括直接市场数据、构造的市场因子与文本新闻信息），以及其交易形式化的关键方面（包括是否动态选择资产、允许的交易方向，以及是否显式生成止损或目标价等风险控制指令）。

表 6：被评估交易方法概览。

```
                                            Information                          Trading Decision
Method                 Category
                                   Market Data   Factors   News     Asset Sel.       Direction      Risk Ctrl.
BUY&Hold            Passive         ×           ×         ×         ×             Long-only         ×
LightGBM             ML              ×           ✓         ×         ✓             Long-only         ×
CatBoost            ML              ×           ✓         ×         ✓             Long-only         ×
Linear                ML              ×           ✓         ×         ✓             Long-only         ×
XGBoost               ML              ×           ✓         ×         ✓             Long-only         ×
MLP                    ML              ×           ✓         ×         ✓             Long-only         ×
TabNet               ML              ×           ✓         ×         ✓             Long-only         ×
TCN                    ML              ×           ✓         ×         ✓             Long-only         ×
GRU                    ML              ×           ✓         ×         ✓             Long-only         ×
LSTM                   ML              ×           ✓         ×         ✓             Long-only         ×
SFM                    ML              ×           ✓         ×         ✓             Long-only         ×
GeneralPTNN        ML              ×           ✓         ×         ✓             Long-only         ×
ALSTM                  ML              ×           ✓         ×         ✓             Long-only         ×
TFT                    ML              ×           ✓         ×         ✓             Long-only         ×
Transformer           ML              ×           ✓         ×         ✓             Long-only         ×
KRNN                   ML              ×           ✓         ×         ✓             Long-only         ×
Localformer           ML              ×           ✓         ×         ✓             Long-only         ×
TRA                    ML              ×           ✓         ×         ✓             Long-only         ×
AdaRNN               ML              ×           ✓         ×         ✓             Long-only         ×
TCTS                   ML              ×           ✓         ×         ✓             Long-only         ×
ADD                    ML              ×           ✓         ×         ✓             Long-only         ×
DoubleEnsemble      ML              ×           ✓         ×         ✓             Long-only         ×
GATs                  ML              ×           ✓         ×         ✓             Long-only         ×
Sandwich              ML              ×           ✓         ×         ✓             Long-only         ×
IGMTF                  ML              ×           ✓         ×         ✓             Long-only         ×
MacroHFT             RL              ×           ✓         ×          ×            Long-only         ×
EarnHFT              RL              ×           ✓         ×          ×            Long-only         ×
DeepSeek            LLM             ✓           ×         ×         ✓            Long/Short         ✓
Qwen                  LLM             ✓           ×         ×         ✓            Long/Short         ✓
FinGPT               LLM             ×           ×         ✓         ✓            Long-only          ×
FinMem              Agent           ✓           ×         ✓         ✓            Long/Short         ×
FinAgent              Agent           ✓           ×         ✓         ✓            Long/Short         ×
TradingAgents        Agent           ✓           ×         ✓         ✓            Long/Short         ×
```

**机器学习方法。** 我们评估了一大批通过数值市场观测预测未来市场走势来生成交易信号的机器学习方法。具体包括：

- **Linear**（Yang et al., 2020）学习从市场特征到预测目标的线性映射，为评估更复杂的非线性模型是否带来额外预测价值提供了一个简单基线。
- **LightGBM**（Ke et al., 2017）采用叶节点生长的梯度提升决策树与高效的特征离散化，对市场特征与未来收益之间的非线性关系建模。
- **XGBoost**（Chen & Guestrin, 2016）使用带正则的梯度提升决策树，在控制模型复杂度的同时迭代修正预测误差。
- **CatBoost**（Prokhorenkova et al., 2018）是一个梯度提升框架，通过有序提升与正则化策略提升稳健性，这里用作另一个基于树的市场信号预测器。
- **MLP**（Yang et al., 2020）使用多层前馈神经网络，学习从数值市场特征到未来市场走势的非线性映射。
- **TabNet**（Arik & Pfister, 2021）在不同决策步上使用序列注意力选择并变换输入特征中信息丰富的子集，为结构化市场数据提供基于注意力的神经模型。
- **TCN**（Bai et al., 2018）使用因果空洞时间卷积对历史市场序列建模，使模型无需循环计算即可捕捉长程时间依赖。
- **GRU**（Cho et al., 2014）采用门控循环单元总结历史市场观测，同时控制过去信息随时间的保留与更新方式。
- **LSTM**（Hochreiter & Schmidhuber, 1997）使用门控循环记忆单元捕捉金融时间序列中的长期依赖，并从历史观测预测未来市场走势。
- **SFM**（Zhang et al., 2017）引入状态频率记忆，把时间动态分解为多个频率分量，使模型能够捕捉发生在不同频率上的交易模式。
- **GeneralPTNN**（Yang et al., 2020）提供一个通用的基于 PyTorch 的预测框架，不同神经网络骨干可通过统一接口训练。我们使用实现中指定的模型配置从历史市场特征中学习预测信号。
- **ALSTM**（Qin et al., 2017）在基于 LSTM 的时间编码器上加入注意力机制，在产生最终市场预测时对历史观测赋予不同的重要性。
- **TFT**（Lim et al., 2021）结合循环序列建模、门控与变量选择机制以及时间注意力，捕捉多变量时间序列中的局部与长程依赖。
- **Transformer**（Vaswani et al., 2017）依靠自注意力直接对不同时间步观测之间的依赖建模，提供一种非循环的架构来学习时间市场模式。
- **KRNN**（Yang et al., 2020）采用多个循环分支捕捉市场序列中的异质时间模式，并组合其表示用于预测。
- **Localformer**（Yang et al., 2020）以局部卷积操作扩展 Transformer 式序列建模，把局部时间模式提取与基于注意力的长程依赖建模结合起来。
- **TRA**（Lin et al., 2021）引入时间路由适配器，包含面向不同交易模式的多个预测器以及把样本动态分配给这些预测器的路由器，并用最优传输来引导潜在市场模式的发现与分配。
- **AdaRNN**（Du et al., 2021）通过学习跨不同时间段的可迁移表示来应对时间分布漂移，减少序列预测中历史市场状态之间的差异。
- **TCTS**（Wu et al., 2021）利用时间相关的辅助预测任务，并在训练中动态调度它们，使相关预测时域的信息能够改善目标预测任务。
- **ADD**（Tang et al., 2020）使用增强解耦蒸馏，从含噪金融特征中分离全市场信息与超额收益信息，并结合自蒸馏与数据增强来改进股票趋势预测。
- **DoubleEnsemble**（Zhang et al., 2020）把基于学习轨迹的样本重加权与基于洗牌的特征选择相结合，旨在降低对非平稳金融数据中含噪样本与无关特征的过拟合。
- **GATs**（Veličković et al., 2018）把图注意力应用于金融实体之间关系的建模，使相关实体在构建预测表示时的贡献得以自适应加权。
- **Sandwich**（Yang et al., 2020）堆叠卷积与循环编码模块，联合捕捉市场观测中的局部时间模式与更长程的序列依赖。
- **IGMTF**（Xu et al., 2021a）在多变量时间序列观测上构造逐实例的图，并在相关变量与历史实例之间聚合信息，显式建模同时跨越变量与时间的依赖。

**强化学习方法。** 与预测式 ML 模型不同，强化学习方法直接按照与市场序贯交互所产生的奖励优化交易策略。我们评估：

- **EarnHFT**（Qin et al., 2024）为高频交易构建了一个分层强化学习框架。它训练多个专门的低层交易智能体，并用更高层的路由策略在不同市场状况下选择合适的智能体，从而降低在极长高频轨迹上学习的难度。
- **MacroHFT**（Zong et al., 2024）进一步把市场上下文与记忆纳入分层高频交易。它为不同市场状态训练上下文条件化的子智能体，并用一个带记忆的超智能体来组合它们的决策，使最终交易策略适应变化的市场状况。

**基于 LLM 的交易方法。** 我进一步评估了使用大语言模型解读市场信息并直接生成交易决策的方法。这些方法与传统数值预测器的不同之处在于：交易决策是通过对结构化或文本市场上下文进行语言模型推理而产生的。

- **DeepSeek**（Guo et al., 2025）作为通用 LLM 交易基线。我们在每个决策步向模型提供可得的市场上下文，并提示其推理当前市场状况、生成相应交易动作。
- **Qwen**（Yang et al., 2025）在相同的直接 LLM 交易设定下评估：标准化的市场信息被转换为模型输入上下文，模型通过语言推理生成交易决策。
- **FinGPT**（Yang et al., 2023）是一个面向金融的开源 LLM 框架，依托金融数据整理与轻量适配开发。在交易设定中，它利用金融领域表示与语言推理把市场信息转化为交易信号。

**交易智能体。** 交易智能体通过引入显式的智能体架构来组织信息、维护经验或协调多个推理角色，从而扩展了直接基于 LLM 的决策。我们评估：

- **FinMem**（Li et al., 2025b）为 LLM 交易智能体配备分层记忆架构，在不同时间跨度上组织金融信息。其画像、记忆与决策模块使智能体能够检索相关历史经验，并用以指导后续投资决策。
- **FinAgent**（Zhang et al., 2024）是一个多模态交易智能体，整合数值市场数据、金融文本与视觉市场信息。它把工具增强的市场分析与多样化记忆及双层反思结合起来，从历史经验中学习并改进后续交易决策。
- **TradingAgents**（Xiao et al., 2024）把一家交易公司建模为一组专门的 LLM 智能体。不同智能体分别进行技术面、基本面与情绪分析，展开多空辩论，评估风险，并通过结构化的多智能体协作把这些观点综合成最终交易决策。

**被动基准。** 我们还纳入 Buy & Hold，它在评估期初买入目标资产并在整个期间持仓不做主动交易。它提供了一个被动市场基准，用以衡量主动交易方法是否产生超额收益。

## 附录 B 实现细节

本节详细说明第 3 节引入的完整实现细节与超参数配置。

### B.1 通用设置

**优化器。** 所有实验均使用 Adam 优化器（Kingma & Ba, 2015）。

**环境。** 实验服务器配置如下：

- 操作系统：AlmaLinux 9.8
- CPU：AMD EPYC 7513
- 内存：188.2 GiB RAM
- GPU：1× NVIDIA L40，46,068 MB 显存
- NVIDIA 驱动：610.43.02
- CUDA Toolkit：12.6.85
- PyTorch：2.12.0
- Python：3.10.20

### B.2 资产细节

我们用 10 只大市值、交易广泛的加密货币构建可交易资产池。按基准构建时的市值排序，这些资产为 Bitcoin（BTC）、Ethereum（ETH）、XRP（XRP）、Dogecoin（DOGE）、Cardano（ADA）、TRON（TRX）、Chainlink（LINK）、Litecoin（LTC）、Hedera（HBAR）与 OKB（OKB）。所选资产覆盖不同类型的加密货币，包括支付导向的资产、智能合约平台的原生资产以及生态或效用代币。这 10 只资产定义了基准的候选交易资产池，但各方法并不一定交易全部资产。例如，ML 方法进行跨资产预测并从该资产池中选择资产，而 RL 方法操作预先指定的资产 ETH，如第 3 节所述。

### B.3 超参数设置

ML 基线凡有官方实现均直接采用。除非另有说明，神经网络模型使用 Adam 训练，初始学习率 10⁻³，批大小 2,000，最多 200 个 epoch，早停耐心值 20；在支持的情况下随机种子设为 42。对基于序列的模型，我们使用 60 根 bar 的回看窗口。我们主要测试 5 分钟、15 分钟、1 小时与 4 小时四种周期，并最终为模拟交易选择最佳时间框架。

对 Linear（Yang et al., 2020），我们使用不带截距、无额外正则化的普通最小二乘。

对 LightGBM（Ke et al., 2017）、XGBoost（Chen & Guestrin, 2016）与 CatBoost（Prokhorenkova et al., 2018），我们最多使用 1,000 轮 boosting，早停耐心值为 50。模型特定的树参数（如学习率与树深）沿用相应实现的默认值。

对 DoubleEnsemble（Zhang et al., 2020），我们使用六个基于 LightGBM 的组件模型，每个组件 100 轮 boosting，同时启用样本重加权与特征选择。

对 MLP（Yang et al., 2020），我们使用一个含 256 个单元的隐藏层，dropout 率 0.05。与其他神经基线不同，MLP 使用 SGD 优化，最多 300 个更新步，早停耐心值为 50 个评估轮次。

对 LSTM（Hochreiter & Schmidhuber, 1997）、GRU（Cho et al., 2014）与 ALSTM（Qin et al., 2017），我们使用两个循环层，隐藏维度 64，不使用 dropout。

对 GeneralPTNN（Yang et al., 2020），我们使用两层 GRU 骨干，隐藏维度 64。

对 GATs（Veličković et al., 2018）、HIST（Xu et al., 2021b）与 IGMTF（Xu et al., 2021a），我们使用两层 GRU 骨干，隐藏维度 64，这些模型保留其原生的截面批处理机制。

对 SFM（Zhang et al., 2017），我们把隐藏维度设为 64、频率维度设为 10，并使用 SGD 优化。

对 TCN（Bai et al., 2018），我们使用两个时间卷积层级，128 个通道，卷积核大小 5。

对 KRNN（Yang et al., 2020），我们把 CNN 与 RNN 的隐藏维度都设为 64，卷积核大小 3，并采用三个并行循环分支。

对 Sandwich（Yang et al., 2020），两个 CNN 阶段的隐藏维度分别为 64 与 32，两个循环阶段的隐藏维度分别为 16 与 8，并使用三个并行循环分支。

对 AdaRNN（Du et al., 2021），我们使用两个域与 40 个预训练 epoch，迁移损失权重设为 0.5。

对 ADD（Tang et al., 2020），我们使用两个循环层，隐藏维度 64，批大小提高到 5,000，γ = 0.1，µ = 0.05。

对 Transformer（Vaswani et al., 2017）与 Localformer（Yang et al., 2020），我们使用模型维度 64、两个注意力头、两层；学习率降为 10⁻⁴，权重衰减 10⁻³；最多训练 100 个 epoch，早停耐心值为 5。标准实现与时间序列实现的批大小分别为 2,048 与 8,192。

对 TabNet（Arik & Pfister, 2021），我们使用表示维度 64、松弛因子 1.3、虚拟批大小 2,048；学习率设为 10⁻²，批大小 4,096；模型先预训练 50 个 epoch，再进行最多 100 个 epoch 的监督训练。

对 TCTS（Wu et al., 2021），我们使用两层，隐藏维度 64，三个优化步；预测网络与加权网络都使用学习率 5 × 10⁻⁷。

对 TRA（Lin et al., 2021），我们使用两层 GRU 骨干，隐藏维度 64，单一潜在状态；批大小 256，最多训练 500 个 epoch，早停耐心值 50。

对 TFT（Lim et al., 2021），我们使用模型维度 64、四个注意力头、两层，dropout 率 0.2；学习率 10⁻³，权重衰减 10⁻⁴，批大小 128；最多训练 100 个 epoch，早停耐心值 10。

我们使用 DeepSeek V4 Flash（deepseek-v4-flash）与 Qwen 3.6 Max Preview（qwen3.6-max-preview），两者都启用 thinking。两个基线共享同一提示词生成器与执行器，从而只有语言模型不同。每次决策时，提示词包含：五十根 3 分钟 bar，以价格与技术指标序列表示；五十根 4 小时 bar，以趋势、波动率与成交量指标表示；资金费率与持仓量（open interest）；账户权益与当前持仓；以及最多五条近期决策。我们不向这两个直接基线提供新闻。每个模型返回一个 JSON 对象，包含 buy/sell/hold、建议的合约数量、止损、盈利目标、失效条件、置信度、估计风险与理由。执行器支持单独的平仓操作，但当前直接模型的提示词并不请求它。

对 FinGPT（Yang et al., 2023），我们使用 NousResearch/Llama-2-13b-hf 作为基座模型，并从公开的 FinGPT/fingpt-sentiment llama2-13b lora adapter 初始化。最终部署的模型是面向新闻的 Stage-2 适配器 stage2_news_focused。我们进行两个 SFT 阶段：阶段 1 使用学习率 8 × 10⁻⁵、种子 42，阶段 2 使用 5 × 10⁻⁵、种子 43。两个阶段都训练 1 个 epoch，每设备批大小 2，梯度累积 16 步，对应单设备有效批大小 32。我们使用 AdamW，权重衰减 0.01，线性学习率调度，warmup 比例 0.03，最大序列长度 512；训练采用 4-bit NF4 量化与 FP16 计算。

部署的 LoRA 适配器使用秩 r = 8、缩放因子 α = 32、dropout 0.1，并应用于 query、key 与 value 投影模块。训练数据合并 DLT-Sentiment-News 与 stocktwits-crypto：阶段 1 对每个来源各使用 60,000 条样本，阶段 2 把新闻数据比例提高到 48,000 条 DLT 样本与 12,000 条 StockTwits 样本。另有一个独立验证集，包含 7,200 条 DLT 与 1,800 条 StockTwits 样本，对负面、中性、正面三类情绪做均衡采样。

推理时，我们在三个情绪标签上做 label-logprob 分类：每个标签按 token 对数概率均值打分，文章级情绪分数定义为 P(positive) − P(negative)。最大输入长度 512 token，部署的推理批大小为 1，模型以 FP16 加载，不做 4-bit 或 8-bit 推理量化。

构建交易信号时，每只资产单独选择参数。候选策略包括仅资产、仅市场、固定资产–市场融合与自适应融合。所选配置的资产新闻 top-N 取值在 6 到 24 之间，市场新闻 top-N 在 12 到 48 之间，信号阈值在 0.03 到 0.15 之间；固定融合权重在 0.65 到 0.80 之间，自适应配置使用 k = 4，资产权重截断到 [0.65, 0.95]。信号按日评估并滞后一天；每只资产分配独立的资金桶，策略在 long/flat 状态下运行。

对 FinMem（Li et al., 2025b），我们使用 qwen3-max 作为决策模型，Qdrant 作为向量记忆数据库。我们检索前五条记忆，并使用三天的回看与动量窗口；用 60 天的预热期初始化记忆系统。短期、中期、长期与反思记忆的初始重要性分数分别设为 50、60、90、80，新近性衰减因子分别为 3、90、365、365，重要性衰减因子分别为 0.92、0.96、0.96、0.98；记忆提升阈值设为 55 与 85，反思相似度阈值为 0.95。Qdrant 以余弦相似度存储 1,024 维嵌入。每次日度决策保留当天及此前 10 天的上下文，其中最多包含五条资产特定与五条全市场新闻。

对 FinAgent，我们使用启用 thinking 的 DeepSeek V4 Flash 完成市场情报摘要、低层与高层反思以及最终决策。在正常 OKX 数据通路下，FinAgent 接收最多 100 根已收盘的 4 小时 OHLCV bar、最多 30 天的新闻、当前账户与已签署持仓、检索到的市场情报记忆、价格反思、决策反思以及当前执行约束。记忆检索默认返回五条，市场情报检索每类查询最多返回三条。FinAgent 返回 XML 字段 analysis、action 与 reasoning，action 取 BUY、SELL、HOLD 或 CLOSE 之一；模型不输出可执行的合约数量。

对 TradingAgents，我们对快速与深度推理角色都使用启用 thinking 的 DeepSeek V4 Flash。所部署的配置选择市场分析师与新闻分析师，其报告依次经过一轮初始多头研究、研究主管、交易员、一轮初始激进风险分析，以及投资组合经理。多空辩论轮数与三方风险讨论轮数都设为零，因此空头、保守与中性的后续回合被跳过。最终模型输出包含五档评级之一——Buy、Overweight、Hold、Underweight 或 Sell——以及执行摘要、投资论点，以及可选的目标价与时间跨度。

**历史直接模型回放。** 为说明出处，主结果中报告的 2025 年直接模型回测使用 BTC-USDT 永续合约、4 小时决策、10× 逐仓杠杆、10,000 USDT 初始权益与 0.10% 的交易费。所报告的 DeepSeek 轨迹是一次续跑的结果：其早期区段使用 Pro 变体，后期区段使用 Flash 变体，因此应把它读作混合模型轨迹，而非单一固定模型的估计。

**前瞻性执行设置。** 在前瞻性模拟盘交易中，所有四个系统每 300 秒轮询一次，但对每个新收盘的 UTC 4 小时 bar 最多只做一次决策。永续仓位使用固定 2× 杠杆的逐仓保证金。执行器把单一资产的绝对名义价值上限设为当前账户权益的 15%，四个资产的总名义价值上限设为 60%。直接基线跳过低于 10 USDT 的订单变更；FinAgent 则遵循交易所合约的最小数量与手数规则。

模型输出与可执行订单被有意分离。对 DeepSeek 与 Qwen，当建议数量超过任一敞口上限时会相应缩减；对 FinAgent，BUY 与 SELL 以两个上限所允许的最大多头或空头仓位为目标，CLOSE 以零为目标，HOLD 维持当前持仓；对 TradingAgents，Buy 与 Sell 映射为单资产上限的 +100% 与 −100%，Overweight 与 Underweight 映射为该上限的 +75% 与 −75%。随后执行器减去当前已签署持仓，按交易所合约面值把名义差额换算为合约张数，并向下取整到允许的手数。提示词中建议的止损、盈利目标与自然语言仓位建议会被记录供分析，但不会覆盖这些确定性的敞口限制，也不会创建交易所原生的条件订单。

### B.4 提示词设计

我们在此报告各基于 LLM 的方法所使用的提示词契约（prompt contracts）。以下提示词按原文保留为英文代码块。

**DeepSeek 与 Qwen 的系统提示词：**

```text
System Prompt for DeepSeek and Qwen

You are a professional cryptocurrency trading assistant. Produce risk-aware 4-hour decisions that pre-
serve capital first and grow it second. Do not trade merely to remain active; return hold when trend,
momentum, volatility, or multi-timeframe evidence is mixed, late, or noisy. Treat current account value
as principal. For every non-hold trade, the expected loss at the proposed stop should normally be
0.5–2.0% of principal and must not exceed 3.0%. Every non-hold decision must include a stop-loss,
profit target, and explicit invalidation condition. Return only valid JSON with the following fields for
each asset: signal, quantity, stop loss, profit target, invalidation condition,
justification, confidence, and risk usd. For hold, set quantity and risk usd to zero.
The percentage range and ceiling are model-side sizing guidance recorded with the response; the executor
does not enforce risk usd or submit the proposed stop as a conditional order.
```

**DeepSeek 与 Qwen 的决策时提示词：**

```text
Decision-Time Prompt for DeepSeek and Qwen

Current time: {timestamp}. Invocation count: {decision index}. All time series are ordered
from oldest to newest. For each asset, the prompt supplies: current price; the latest ten 3-minute closes;
20-period exponential moving average, moving-average convergence divergence, and 7- and 14-period
relative-strength-index series computed from the latest fifty 3-minute bars; 20- and 50-period exponen-
tial moving averages, 3- and 14-period average true range, current and mean volume, and the latest
ten moving-average-convergence-divergence and 14-period relative-strength-index values computed from
fifty 4-hour bars; funding rate; open interest; available cash; account value; and current perpetual po-
sitions. The prompt then appends up to five recent decisions, if available. Using only this market and
account state, return the JSON decision required by the system prompt. No news is supplied to these two
baselines.
```

**FinAgent 的系统与决策提示词：**

```text
System and Decision Prompt for FinAgent

System role. You are an expert trader making disciplined 4-hour cryptocurrency decisions from market
information, news summaries, account state, retrieved memories, and reflections. The execution context
states whether the instrument is spot or a perpetual contract. In perpetual mode, BUY targets a bounded
long position, SELL targets a bounded short position, CLOSE targets a flat position, and HOLD preserves
the current signed position. Do not infer quantity, or account capability beyond the supplied execution
constraints.
Decision instruction. Instrument: {asset}; date: {date}; reference price: {price}; cash: {cash};
current position: {position}; cumulative and recent returns: {returns}. Consider the latest and
retrieved past market-intelligence summaries, short-, medium-, and long-horizon price reflections, reflec-
tions on prior trading decisions, and the supplied execution constraints. Assess whether each item is
positive, negative, neutral, stale, or unrelated; do not chase a missed entry or panic-sell a missed exit. Re-
turn only XML with analysis, one action from BUY/SELL/HOLD/CLOSE, and reasoning. The
model supplies direction and reasoning; the executor computes the contract quantity.
```

当前的 FinAgent 模板继承自一个更宽泛的多模态设计，但这里使用的加密货币适配器会填充 OHLCV、新闻、记忆、反思、账户与执行上下文字段。可选的指导、情绪、经济与视觉小节若在某次运行中不可用，则留空而不做推断。仍有一段继承来的指令片段只枚举 BUY、SELL 与 HOLD；任务描述与输出 schema 显式允许 CLOSE，且响应解析器与执行器都接受它。尽管存在这段残留的三动作片段，这些组件才是部署系统的权威来源。

**TradingAgents 的角色提示词：**

```text
Role Prompts for TradingAgents

Market analyst. Analyze the current cryptocurrency pair using local OHLCV data and at most eight
complementary indicators. Emphasize trend, momentum, volatility regime, volume confirmation, support
and resistance, trend exhaustion, and downside risk; return a detailed evidence-grounded market report.
News analyst. Analyze recent asset-specific and global news, focusing on macro liquidity, rates, dollar
strength, regulation, fund-flow narratives, exchange events, security incidents, protocol upgrades, and
broad risk appetite; return an evidence-grounded news report.
Trader. Given the research plan and analyst reports, return a structured Buy, Hold, or Sell proposal
with reasoning and optional entry, stop, and natural-language sizing guidance.
Initial directional and risk passes. A bull researcher constructs one evidence-based case from the market
and news reports before the research manager forms the investment plan. After the trader proposal, an
aggressive risk analyst performs one initial risk–reward pass before the portfolio manager produces the
final rating. With both configured debate-round counts set to zero, these two initial passes still execute,
while the bear, conservative, and neutral follow-up turns are skipped.
```

**TradingAgents 的最终决策提示词：**

```text
Final Decision Prompt for TradingAgents

As the Portfolio Manager, synthesize the research plan, trader proposal, lessons from prior deci-
sions, and any available risk-analysis history for {instrument}. Select exactly one rating: Buy,
Overweight, Hold, Underweight, or Sell. Be decisive and ground the decision in specific ev-
idence from the supplied reports. Return a structured object with rating, executive summary,
investment thesis, and optional price target and time horizon. The rating, rather than a
model-generated quantity, is passed to the deterministic position-mapping rule described above.
```

在所部署的配置中，TradingAgents 运行市场与新闻分析师、一轮初始多头研究、研究主管与交易员、一轮初始激进风险分析，以及投资组合经理；后续的多空辩论与三方风险辩论轮次被禁用。因此，最终决策提示词收到的是由当前报告导出的研究计划与交易员提案、初始风险分析历史，以及既往经验教训，而没有任何后续辩论回合。

FinMem 把结构化响应格式与阶段特定指令结合起来。下面的系统提示词规定了一个 JSON 响应，其中包含投资决策、文字理由，以及按记忆层分组的支撑记忆标识。这些标识把解释与检索到的证据联系起来，而结构化输出则支持下游的决策记录与记忆更新。

**FinMem 的系统提示词：**

```text
System Prompt for FinMem

You are a financial trading assistant. You MUST respond STRICTLY and ONLY in valid JSON
format.    The JSON object MUST include the following keys: investment decision,
summary reason,          short memory ids,             mid memory ids,          long memory ids,
reflection memory ids. The field investment decision MUST be exactly one of:
"buy", "sell", "hold". The field summary reason MUST be a non-empty string. The memory id
fields MUST be arrays of integers. If there is no evidence for a memory field, output an empty array.
Do not output markdown. Do not output any text outside the JSON object.
```

在预热阶段，FinMem 会得到一个来自历史数据的、已观测到的次日价格变化信号，并被要求用可得的记忆解释该结果。这是一个回顾性解释任务，而非对未观测结果的预测。生成的解释会被存入反思记忆以供后续检索，使后续决策能够借鉴早前市场观测的总结。

**FinMem 的指令模板：**

```text
Instruction for FinMem

Braced fields are runtime substitutions; italic conditions are not sent to the model. Empty memory
layers and their headings are omitted. Here {future record} is (pt − pt+1 )/pt in the implemen-
tation.
The current date is {cur date}. Here are the observed financial market facts: for {symbol}, the
price difference between the next trading day and the current trading day is: {future record}.
{short memory section}
If short-term memories are present:
In investment decision-making, analyzing financial sentiment is pivotal, offering insights into mar-
ket perceptions and forecasting potential market trends. Sentiment analysis divides market opinions
into three categories: positive, negative, and neutral. A positive sentiment signals optimism about fu-
ture prospects, often leading to increased buying activity, while negative sentiment reflects pessimism,
likely causing selling pressures. Neutral sentiment indicates either uncertainty or a balanced view,
suggesting that investors are neither overly bullish nor bearish. Leveraging these sentiment indicators
enables investors and analysts to fine-tune their strategies to better match the prevailing market atmo-
sphere. Additionally, news about competitors can significantly impact a company's cryptocurrency
price. For example, if a competitor unveils a groundbreaking product, it may lead to a decline in the
cryptocurrency prices of other companies within the same industry as investors anticipate potential
market share losses.
{mid memory section}
{long memory section}
{reflection memory section}
If three-day momentum is nonzero:
The information below provides a summary of cryptocurrency price fluctuations over the previous
few days, which is the "Momentum" of a cryptocurrency. It reflects the trend of a cryptocurrency.
Momentum is based on the idea that securities that have performed well in the past will continue to
perform well, and conversely, securities that have performed poorly will continue to perform poorly.
The cumulative return of past 3 days is {positive or negative}.
Given the following information, can you explain to me why the financial market fluctuation from
current day to the next day behaves like this? Summarize the reason of the decision. Your should
provide a summary information and the id of the information to support your summary.
```

在测试与模拟盘交易期间，该指令会省略次日结果，改为要求基于检索到的记忆与历史动量做出决策。空的记忆层被排除；当存在短期记忆时加入情绪段落，仅当动量非零时加入三日动量段落。指令明确鼓励在情绪或动量为正时买入，在买卖选择不清时可以持有，同时要求用记忆标识支撑决策。

**测试与模拟盘交易指令：**

```text
Test and Paper-Trading Instruction

Braced fields are runtime substitutions; italic conditions are not sent to the model. Empty memory
layers and their headings are omitted. The constructor does not insert a numerical value for current
holdings.
The ticker of the cryptocurrency to be analyzed is {symbol} and the current date is {cur date}.
{short memory section}
If short-term memories are present:
In investment decision-making, analyzing financial sentiment is pivotal, offering insights into mar-
ket perceptions and forecasting potential market trends. Sentiment analysis divides market opinions
into three categories: positive, negative, and neutral. A positive sentiment signals optimism about fu-
ture prospects, often leading to increased buying activity, while negative sentiment reflects pessimism,
likely causing selling pressures. Neutral sentiment indicates either uncertainty or a balanced view,
suggesting that investors are neither overly bullish nor bearish. Leveraging these sentiment indicators
enables investors and analysts to fine-tune their strategies to better match the prevailing market atmo-
sphere. Additionally, news about competitors can significantly impact a company's cryptocurrency
price. For example, if a competitor unveils a groundbreaking product, it may lead to a decline in the
cryptocurrency prices of other companies within the same industry as investors anticipate potential
market share losses.
{mid memory section}
{long memory section}
{reflection memory section}
If three-day momentum is nonzero:
The information below provides a summary of cryptocurrency price fluctuations over the previous
few days, which is the "Momentum" of a cryptocurrency. It reflects the trend of a cryptocurrency.
Momentum is based on the idea that securities that have performed well in the past will continue to
perform well, and conversely, securities that have performed poorly will continue to perform poorly.
The cumulative return of past 3 days is {positive or negative}.
Given the information, can you make an investment decision? Just summarize the reason of the deci-
sion. please consider the mid-term information, the long-term information, the reflection-term infor-
mation only when they are available. If there no such information, directly ignore the impact for ab-
sence such information. please consider the available short-term information and sentiment associated
with them. please consider the momentum of the historical cryptocurrency price. When momentum or
cumulative return is positive, you are a risk-seeking investor. When momentum or cumulative return
is negative, you are a risk-averse investor. In particular, you should choose to 'buy' when the overall
sentiment is positive or momentum/cumulative return is positive. please consider how much shares of
the cryptocurrency the investor holds now. You should provide exactly one of the following investment
decisions: buy or sell. When it is very hard to make a 'buy'-or-'sell' decision, then you could go with
'hold' option. You also need to provide the ids of the information to support your decision.
```






