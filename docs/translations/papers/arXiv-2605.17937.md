# BacktestBench：面向自动化量化策略回测的 LLM 基准（BacktestBench: Benchmarking Large Language Models for Automated Quantitative Strategy Backtesting）

> 来源：https://arxiv.org/abs/2605.17937
> 原文：docs/papers/arXiv-2605.17937.pdf
> 翻译日期：2026-11-10 ｜ 范围：全文 ｜ 方式：机器翻译初稿，未经人工校对
> 引用于：docs/literature/W3-backtest-reliability.md

作者：Zhensheng Wang、Wenmian Yang∗、Qingtai Wu、Lequan Ma、Yiquan Zhang、Weijia Jia∗（∗ 通讯作者）
（Beijing Normal University：北京 / 珠海；Elmleaf Ltd.：上海）
arXiv:2605.17937v2 [cs.CL]，2026-05-25 ｜ KDD 2026

## 目录

- 摘要
- 1 引言
- 2 数据集构建
  - 2.1 数据来源
  - 2.2 核心概念
  - 2.3 因子与 KPI 选择
    - 2.3.1 因子选择
    - 2.3.2 KPI 选择
  - 2.4 功能实现
    - 2.4.1 由因子实现原子策略函数
    - 2.4.2 KPI 计算函数的实现
  - 2.5 策略代码构建
  - 2.6 策略描述生成
    - 2.6.1 多模型并行生成
    - 2.6.2 自动过滤
  - 2.7 数据集统计与人工验证
- 3 AutoBacktest
  - 3.1 Summarizer
  - 3.2 Retriever
  - 3.3 Coder
- 4 实验
  - 4.1 实验设置
    - 4.1.1 模型配置
    - 4.1.2 评估指标
  - 4.2 主要结果
    - 4.2.1 闭源模型的主导与开源模型的追赶
    - 4.2.2 各任务对 Scaling Law 的敏感度差异
    - 4.2.3 缺少 CoT 导致的语法与逻辑能力解耦
    - 4.2.4 指标计算任务的准确率分析
  - 4.3 消融研究
    - 4.3.1 Short Code 对 SQL 生成的影响
    - 4.3.2 Short Code 与 SQL 质量的独立影响
- 5 相关工作
  - 5.1 基于 LLM 的策略回测
  - 5.2 策略回测数据集
- 6 结论
- 致谢
- 参考文献（从略）
- A 因子
- B 回测协议与标准化交易规则
- C 数据集
  - C.1 数据库表结构
  - C.2 策略数据生成细节
  - C.3 自然语言生成与评估细节
- D Agent 数据流与交互
- E 实验
  - E.1 BM25 在 Summarizer 中的作用
  - E.2 案例分析
    - E.2.1 案例 1：波动率计算失败的复合归因分析
    - E.2.2 案例 2：Sharpe 比率评估的系统性偏差
- F 实现细节
  - F.1 LLM 部署
  - F.2 Agent 实现
- G 提示词
  - G.1 数据集构建提示词
  - G.2 AutoBacktest Agent 提示词
- H 局限

## 摘要

量化回测是评估交易策略的关键手段，但长期受制于高技术门槛与有限的可扩展性。大语言模型（LLM）借助先进的代码生成、工具使用与 agentic planning，为自动化这一复杂、跨学科的工作流程提供了变革性路径；然而，当前缺少专门面向自动化量化回测的大规模基准，这显著阻碍了该领域的进展。为填补这一关键空白，我们提出 BacktestBench——首个面向自动化量化回测的大规模基准。它基于超过 600 万条真实市场记录构建，包含 18,246 个精心标注的问答（QA）对，覆盖四类任务：指标计算、标的选股、策略选择与参数确认。我们还提出 AutoBacktest，一个稳健的多智能体基线：它协调负责语义因子抽取的 Summarizer、负责经校验 SQL 生成的 Retriever，以及负责 Python 回测实现的 Coder，把自然语言策略转化为可复现的回测。我们对 23 个主流 LLM 进行评估，并辅以针对性的消融实验，识别出影响端到端表现的关键因素，凸显了基于真值的校验（grounded verification）与标准化指标表示的重要性。数据集与代码将在 https://github.com/jensenw1/BacktestBench 公开发布。

**CCS 概念**：• Computing methodologies → Language resources；Multi-agent systems；• Information systems → Question answering。

**关键词**：Large Language Models、Question Answering、Quantitative Investing、Automated Backtesting、Benchmark、Multi-agent Framework

**许可与出版信息**：本作品采用 Creative Commons Attribution 4.0 International 许可协议授权。KDD 2026，韩国济州岛，2026 年 8 月 9–13 日。© 2026 版权归作者（们）所有。ACM ISBN 979-8-4007-2259-2/2026/08。https://doi.org/10.1145/3770855.3817460

**ACM 引用格式**：Zhensheng Wang, Wenmian Yang, Qingtai Wu, Lequan Ma, Yiquan Zhang, and Weijia Jia. 2026. BacktestBench: Benchmarking Large Language Models for Automated Quantitative Strategy Backtesting. In Proceedings of the 32nd ACM SIGKDD Conference on Knowledge Discovery and Data Mining V.2 (KDD 2026), August 9–13, 2026, Jeju Island, Republic of Korea. ACM, New York, NY, USA, 25 pages. https://doi.org/10.1145/3770855.3817460

## 1 引言

> "History does not repeat itself, but it often rhymes." —— Mark Twain
>
> 「历史不会重复，但总会押韵。」—— Mark Twain

在量化投资中，这句格言道出了回测的根本作用：它在大量历史数据上重放交易逻辑，以严格评估策略的稳健性，以及其适应未来市场状态的潜力 [19]。通过报告 Sharpe 比率 [22]、最大回撤 [17] 等量化指标，回测提供了一套客观的评估框架，显著降低了对主观判断的依赖，并增强了不同投资策略之间的可比性 [5]。

然而，如图1所示，传统的回测工作流天然复杂且跨学科，需要专业知识。策略工程师必须精确构造因子组合，针对特定股票与时间窗口发出准确的历史数据查询，并写出无误的代码来执行复杂的策略逻辑。这一过程受制于高技术门槛，要求细致的数据检索、严格遵守市场时机以及精确的交易规则实现。近来 LLM 的出现，及其在代码生成、逻辑推理 [3, 16, 20]，尤其是交互环境中的 agentic planning [32]、工具调用 [21] 与迭代式改进 [23] 方面的先进能力，为自动化量化回测带来了变革性机遇。面对因子组合搜索空间的爆炸式增长与快速变化的市场需求，人工的策略实现与验证流程已无法满足现代量化研究对效率与可扩展性的要求。这促使我们探究：基于 LLM 的 agent 能否可靠地自动化整条回测流水线，涵盖数据检索、策略翻译与执行。这样的努力也可作为评估通用人工智能（AGI）[27] 在复杂垂直领域问题上能力的一块现实试金石。

**图1：量化回测工程师的真实工作流（原文第2页）**

尽管自然语言驱动的端到端自动回测前景十分诱人，其实际落地仍面临重大挑战。它要求模型同时具备对金融策略的精确语义理解、稳健的结构化数据检索能力，以及高度准确的代码生成技能 [30]。关键在于，学术界目前缺少专为这类复杂金融推理任务设计的高质量评估基准。现有的代码生成或 Text-to-SQL 数据集 [13, 14, 34] 虽有价值，却未能充分捕捉量化回测所特有的时间逻辑与多步推理需求。

为填补这一关键空白，我们提出 BacktestBench——一个面向自动化回测领域的新颖大规模基准数据集。它基于中国三大交易所超过 600 万条真实历史市场记录构建，包含 18,246 个高质量问答（QA）对。每个样本都经过精心标注，覆盖从自然语言策略描述、核心因子抽取、SQL 数据查询生成、Python 回测代码实现到最终客观答案的完整信息链。此外，为全面评估模型的整体能力，本基准系统性地设计了四类任务：指标计算、标的选股、策略选择与参数确认。这些类别完整覆盖了策略比较、优化、资产配置等真实回测场景，从而为衡量 LLM 在该垂直领域的智能水平提供了一把严格的标尺。

为系统性地应对 BacktestBench 的挑战，并有效评估 LLM 在该领域的推理与执行能力，本研究提出 AutoBacktest——一个作为稳健基线的多智能体协作系统。它把非结构化的自然语言策略描述转化为可复现的回测结果，通过将复杂的决策链解耦为专门的子任务，模仿人类量化研究员的工作流。具体而言，AutoBacktest 协调三个功能专化的 agent：(1) Summarizer，负责在语义层面抽取金融指标（包括交易因子与关键绩效指标）；(2) Retriever，负责数据层面的精确查询与质量校验；(3) Coder，负责逻辑层面的代码实现与回测执行。这种分层、模块化的架构不仅显著降低了端到端生成的内在难度，还通过各阶段的自我校验机制提升了整条回测流水线的稳健性，从而为后续研究建立了标准化的参考基线。

本文的主要贡献如下：

- 我们建立了 BacktestBench——一个面向自动化量化回测的大规模基准。它基于超过 600 万条真实市场记录构建，覆盖指标计算、标的选股、策略选择与参数确认四类任务。
- 我们提出 AutoBacktest——一个稳健的多智能体基线系统，通过语义因子抽取、SQL 生成与 Python 代码执行，把自然语言策略转化为可执行的回测。
- 我们在 BacktestBench 上评估了 23 个主流 LLM，并开展消融研究，以识别影响端到端回测表现的关键因素。
## 2 数据集构建

### 2.1 数据来源

为构建贴合真实场景的回测数据集，我们对 Elmleaf Information Technology 提供的原始股票数据进行了严格的清洗与整合。首先，我们收集了 2020 年 1 月 2 日至 2025 年 9 月 30 日期间，上海证券交易所、深圳证券交易所与北京证券交易所全部上市股票的每日交易数据。清洗后，数据集包含 6,549,254 条记录，覆盖 5,401 家上市公司、1,395 个交易日。更详细的表结构说明与补充统计见附录 C.1。

### 2.2 核心概念

在量化投资中，我们区分四个紧密相关的概念：factor（因子）、signal（信号）、strategy（策略）与 KPI。

因子是通过对原始市场观测值（如开盘价、最高价、最低价、收盘价、成交量）施加确定性的统计或技术公式计算出的数值变量，它量化某种特定的市场形态或状态 [33]。例如，5 日移动平均（MA5）把一个价格序列映射为标量时间序列，表示过去五个交易日的平均价格。

信号是在时刻 𝑡 对一个或多个因子施加约束或阈值规则后得到的布尔决策，表示某个交易条件是否满足。例如，买入信号可定义为 Open𝑡 > MA5𝑡−1，其中因子取值只使用时刻 𝑡 之前可得的信息，以避免前视偏差（look-ahead bias）。同理，卖出信号可由相反的不等式或对另一个因子的不同约束来定义。

策略规定了在回测协议下如何把买入、卖出信号组合成可执行的交易动作，包括进场与出场逻辑、持仓状态转移以及必需的约束（如只做多、买卖交替）。例如，一个简单的只做多策略在买入信号触发时进场，在卖出信号触发时出场，其余时间持仓。

KPI（key performance indicator，关键绩效指标）是在回测协议下用于评估因子、信号与策略的量化度量，涵盖可预测性、风险与可实施性。

总之，因子提供数值基础，信号把因子转化为可执行的条件，策略把买卖信号组合成完整、可复现的交易政策以供回测，而 KPI 则提供把这些概念连接到可测量、可比较结果上的评估标准。

### 2.3 因子与 KPI 选择

#### 2.3.1 因子选择

面对海量候选因子，本研究遵循两条核心筛选原则：

- 数据可得性（Data Availability）：现有数据库表结构必须完全支持因子计算所需的基础字段。
- 计算确定性（Computational Determinism）：因子必须具有严格的数学公式，以保证计算结果的唯一性与可复现性。基于这一原则，我们排除涉及随机性或主观判断的因子，例如 LLM 基于非确定性随机种子生成的新闻情绪分数，或依赖人工标注的软性指标。

依据这些标准，我们选取了 43 个因子，横跨 Risk、Quality、Momentum 与 Technical 四大类，其中 4 个仅用于卖出、2 个仅用于买入、37 个买卖双向可用。全部因子的详细清单见附录 A。

#### 2.3.2 KPI 选择

在领域专家指导下，我们选取七个 KPI 作为主要评估标准：Return Ratio（收益率比率）、Maximum Drawdown（最大回撤）、Volatility（波动率）、Annual Sharpe Ratio（年度 Sharpe 比率）、Win Rate（胜率）、Profit Loss Ratio（盈亏比）与 Calmar Ratio [8]。Calmar Ratio 定义为年化收益与最大回撤之比，是一个对下行风险敏感的指标。七个 KPI 的详细定义见附录表 6。

### 2.4 功能实现

#### 2.4.1 由因子实现原子策略函数

为把 43 个理论因子转化为可执行的工程对象，我们使用 Pandas 与 NumPy 将其封装为 80 个原子策略函数。每个函数把因子计算与显式的信号触发逻辑耦合在一起，其中 41 个用于卖出侧、39 个用于买入侧。它们共同构成我们的信号池（signal pool）。

每个原子策略函数以目标股票的历史数据与特定超参数（如回看窗口、判定阈值）为输入。这些函数同时封装因子计算与信号评估，返回策略被触发的交易日期列表。阈值参数专门用于界定逻辑的边界条件，例如判断数值偏离是否足以产生信号。为保证回测的真实性，我们严格避免前视偏差：第 𝑇 天的交易决策只依赖截至 𝑇 − 1 的信息所计算出的统计量。示例见附录 A。

#### 2.4.2 KPI 计算函数的实现

由于若干金融 KPI 对实现方式敏感，且 LLM 在推理这类计算时可能产生幻觉，我们采用一套标准化回测协议，以确定性的交易规则与无歧义的指标定义来保证结果唯一且可复现。

该协议把执行微观结构固定为只做多（long-only）设定：买卖操作严格交替，禁止日内回转交易（T+0），买入按开盘价成交、卖出按收盘价成交，并在回测窗口结束时强制清算任何剩余持仓。

我们模拟无杠杆的固定资金组合，执行整手交易（至少 100 股），并在基线实验中把交易成本与税费设为零。业绩按逐日盯市（mark-to-market）会计口径评估：按每年 252 个交易日年化，计算年度 Sharpe Ratio 时日无风险利率固定为 0.0001，并假设输入时间序列完整且严格按交易日排序。执行机制、仓位约束、收益计算与数据完整性假设的完整规格见附录 B。

上述回测逻辑以 Python 实现，并封装为一个专用的指标计算函数。该函数的输入是一个包含市场数据的 DataFrame，以及由信号池生成的买卖信号序列，输出评估框架中定义的七个 KPI 值。

为保证实现的正确性与稳健性，本研究采用双盲校验流程。两名量化工程专家各自独立地严格按照共享回测协议实现同一指标计算函数，然后在随机选取的十个市场数据样本上进行交叉验证。只有当两份实现在所有测试用例上的输出完全一致时，该实现才被接受为正确；再经讨论选定更优的版本作为最终回测引擎。这一流程有效缓解了代码层面的潜在逻辑错误，提升了实验评估工具集的可靠性。

### 2.5 策略代码构建

为构建多样化的量化投资语料，我们设计了一个自动框架，动态合成可执行的回测代码。该框架通过采样并组合原子策略函数来运行。组合分析表明：不放回地最多选取四个原子函数，可产生巨大的搜索空间——92,170 个买入策略与 112,791 个卖出策略。借助 Python 反射机制，系统实例化这些原子算子，并把它们映射为四类规范决策任务：指标计算、标的选股、参数确认与策略选择。详细的构建流程与生成统计见附录 C.2。

**指标计算（Metrics Calculation）。** 该任务族评估模型在固定市场环境下为单一策略计算量化业绩指标的能力。每个实例给出策略的自然语言描述与一个指定的 KPI（如 Sharpe Ratio 或 Maximum Drawdown），模型需要输出对应的数值。

**标的选股（Ticker Selection）。** 标的选股任务模拟在共享策略设定下，从候选池中挑选表现最佳的资产。给定一个固定策略与多只股票的历史数据，模型必须识别出能使目标 KPI 最优的资产。

**参数确认（Parameter Confirmation）。** 参数确认任务关注在其余固定策略架构内挑选超参数。模型需要判断：在相同标的与回测窗口下，哪个候选参数值（如阈值或回看窗口）能带来最好的 KPI。

**策略选择（Strategy Selection）。** 策略选择任务位于决策层级的顶端，要求在相同市场条件下从多个相互竞争的策略逻辑中做出选择。给定若干共享标的、期限、初始资金与评估指标的候选策略，模型必须判断哪种逻辑能取得最高表现。

**说明。** 在全部四个任务族中，每个实例都配有可执行的 Python 代码、标准化的回测环境与真值标签，从而支持从自然语言到量化结果的端到端评估。更多实现细节，包括数据采样规则、代码合成流水线与过滤标准，见附录 C.2。

**图2：自然语言策略生成与评估流程（原文第4页）**

### 2.6 策略描述生成

在构建出可执行策略代码语料之后，我们采用 code-to-text 逆向工程范式，获得与实际回测行为一致、人类可读的策略描述。为兼顾语义准确性与金融合理性，我们使用带有严格验收规则的多模型生成与评估流水线。

#### 2.6.1 多模型并行生成

我们选取五个最先进的开源 LLM 作为生成 agent：Kimi-K2-Thinking-BF16 [1]、MiniMax-M2.1-BF16 [2]、GLM-4.7 [36]、GPT-OSS-120B-BF16 [18] 与 Qwen3-235B-A22B-Thinking-2507 [31]。这些模型使用 72 块 NVIDIA A800-SXM4-80GB GPU 本地部署。对每个策略代码样本，五个模型各自独立地进行逆向解析与改写，产出风格多样、面向回测场景的指令式自然语言描述。

关键在于，这些模型的输入并不止于原始函数体。如我们在代码库中所示，每个原子策略算子与 KPI 函数都带有完整的 docstring，明确给出策略逻辑（Strategy Logic）、数学公式（Mathematical Formula）与输入输出规格（Input/Output Specifications）。这些丰富的语义上下文提供了真值引导，显著减少了歧义，降低了生成过程中模型产生幻觉的风险。如图2左侧所示，这一过程遵循 code-to-strategy 流水线，把可执行回测程序转化为对齐的自然语言策略。提示词设计细节，包括我们如何强制时间一致性、如何把系统级默认设定与策略特定逻辑分开，见附录 C.3。

#### 2.6.2 自动过滤

为保证语料的高质量，我们实现了基于同行评审的严格自动过滤机制。对某个特定模型（如模型 A）生成的自然语言策略描述，另外四个模型（如模型 B、C、D、E）担任独立审计员。每位审计员从两个维度评估代码—文本对：代码保真度（code fidelity）与策略有效性（strategy validity）。代码保真度检查文本是否忠实重构了程序逻辑，策略有效性则核验交易规则在金融上是否合理、实践中是否可执行。我们执行严格的验收协议：一个样本保留，当且仅当它在两个维度上获得全部四位同行评估者的一致认可（共八张赞成票）。若同一段策略代码有多条描述通过该检查，则随机选取一条以避免重复。

### 2.7 数据集统计与人工验证

把严格的过滤流水线应用于最初 33,003 个策略程序的候选池，最终得到 18,246 个高质量代码—文本对。这些实例按任务类型分层为训练集（10,215）、验证集（4,195）与测试集（3,836）。各任务族的详细分布，以及被接受与被拒绝描述的对比示例，见附录 C.3。

为在统计上量化生成语料的质量，我们对随机抽取的 200 个实例（约占测试集的 5%）进行了人工审计。五名志愿者评估策略描述的完整性，通过率为 97.5%（195/200）。同时，六名 Python 实现专家核验代码正确性，确认代码与交易规则的一致性达 98.5%（197/200）。

此外，为对照人工标准检验合成数据的真实性，我们手工构建了覆盖七类 KPI 的另一组 70 个策略。这个专家手工子集通过前向生成流程开发，涵盖自然语言描述、SQL 数据检索与回测实现，并随后接受严格的专家交叉验证。
## 3 AutoBacktest

为应对该数据集带来的自动化回测挑战，我们设计了一个模仿量化研究员工作流的多智能体框架。三个专化 agent 在流水线中协作：Summarizer 把自然语言策略解析为结构化的指标表示；Retriever 生成并校验可执行的 SQL 以取回历史市场数据；Coder 生成并运行回测代码以获得最终数值结果。下面给出高层描述，交互细节、提示词与实现代码见附录 D。

### 3.1 Summarizer

Summarizer 首先使用一个由预定义提示词引导的 LLM，从用户的自然语言策略中抽取与因子、KPI 相关的关键词。这些汇总后的关键词再送入 BM25 检索机制，与一个全面的指标库进行匹配，识别出精确的标准指标名。最终输出是一份经过核验的标准指标名结构化列表，存入共享的中间状态。具体的提示词设计、JSON schema 与参考实现见附录 D。

### 3.2 Retriever

Retriever 在 Summarizer 输出的基础上构建回测的数据层。它先把识别出的指标名映射到各自的唯一 Short Code（短代码）——紧凑、节省 token 的标识符（例如把 "13-day Bull Power" 映射为 DELAY(HIGH,1)-DELAY(EMA(CLOSE,13),1)），作为数据库 schema 中无歧义的键。通过把这一增强上下文（Name + Short Code）与原始策略文本一并注入，促使 LLM 生成单条可执行 SQL 查询。随后 agent 执行基于运行的校验循环，确保该语句能在 PostgreSQL 数据库上成功运行并返回非空结果。最终确定的 SQL 字符串及其对应的模型消息保存在共享存储中；更多工程细节，包括确切的 SQL 提示模式与错误处理逻辑，见附录 D。

### 3.3 Coder

Coder 是执行端点，负责把取回的数据转化为最终回测结果。其输入包含三个关键要素：用户的自然语言策略、映射后的指标上下文（名称与 Short Code），以及 Retriever 所得 DataFrame 的数据预览（头尾若干行）。在强制严格执行回测协议的系统提示词引导下，Coder 调用一个 Python 执行工具，完整 DataFrame 已被预注入该运行环境。LLM 随后迭代地编写并调试代码，以计算所需指标或执行策略逻辑。完整的实现细节与答案抽取流程见附录 D。

**图3：AutoBacktest 总体框架（原文第5页）**
## 4 实验

### 4.1 实验设置

#### 4.1.1 模型配置

我们的实验基准涵盖 23 个 LLM，分为开源与闭源两大类。开源阵营横跨多个主要系列：Qwen3 系列（从 4B 到 235B A22B 混合专家模型）、Ministral 推理系列（14B 与 8B）、Kimi 系列（K2-Thinking 与 Linear 48B）、GLM 系列（4.7 与 Flash）、GPT-OSS 系列（120B 与 20B），以及若干独立模型，如 MiniMax-M2.1、Seed OSS 36B、Mimo V2 Flash [29] 与 DeepSeek V3.2 [6]。闭源阵营包含四个领先的专有模型：Gemini 3 Pro、Qwen3 Max、Qwen3 Coder Plus 与 Seed 1.8。详细部署规格见附录 F.1。值得注意的是，多数模型使用 CoT 推理，而 Kimi Linear 48B 与 Seed OSS 36B 不使用 CoT。为保证可比性并兼顾生成多样性与稳定性，我们在所有推理任务中统一把 temperature 设为 0.6。

#### 4.1.2 评估指标

本研究从三个维度量化模型表现。其一，对因子检索任务，我们采用 Accuracy、Precision、Recall 与 F1 Score 进行综合评估。其二，对 SQL 生成任务，除计算生成 SQL 语句的可执行率（Executable Rate，ECR）外，我们还关注执行准确率（Execution Accuracy，EA）[34]，它定义为生成 SQL 查询返回的结果集与真值结果集的匹配程度，忽略元素顺序。其三，对四类策略回测问题，我们报告模型生成的策略代码所产生的最终执行结果的准确率，反映端到端的整体表现。对指标计算问题，只有当预测值与真值的绝对误差低于 10⁻³ 时才计为预测正确，否则视为错误。

### 4.2 主要结果

**表1：本表报告模型在合成 BacktestBench 数据集上的表现，不含专家手工子集的结果。四类任务的总体表现对比。OA 表示跨这四类任务汇总的总体表现。缩写：MC：指标计算，TS：标的选股，PC：参数确认，SS：策略选择，ECR：执行正确率（Execution Correctness Rate），EA：执行准确率（Execution Accuracy）。**

| 模型 | 回测准确率 | | | | | SQL 生成 | | 指标检索 | | | |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **模型** | **OA** | **MC** | **TS** | **PC** | **SS** | **ECR** | **EA** | **Acc** | **P** | **R** | **F1** |
| **开源大语言模型** | | | | | | | | | | | |
| Qwen3 235B | 55.01 | 34.71 | 82.26 | 75.93 | 85.04 | 100.00 | 97.11 | 76.41 | 93.62 | 94.75 | 94.18 |
| Qwen3 Next 80B | 44.06 | 26.02 | 67.40 | 65.86 | 68.17 | 99.92 | 94.79 | 73.80 | 92.57 | 94.54 | 93.54 |
| Qwen3 32B | 47.81 | 27.93 | 75.93 | 70.34 | 72.21 | 100.00 | 90.72 | 67.41 | 90.44 | 93.99 | 92.18 |
| Qwen3 30B | 47.03 | 28.67 | 71.25 | 65.86 | 75.06 | 99.97 | 92.86 | 69.73 | 91.78 | 93.25 | 92.51 |
| Qwen3 14B | 36.97 | 16.96 | 62.04 | 61.57 | 64.61 | 99.95 | 87.59 | 60.92 | 87.56 | 90.50 | 89.01 |
| Qwen3 8B | 26.36 | 4.93 | 53.92 | 50.56 | 57.48 | 99.97 | 86.89 | 60.61 | 87.33 | 90.66 | 88.96 |
| Qwen3 4B | 19.63 | 1.77 | 39.06 | 42.54 | 48.22 | 98.85 | 69.94 | 58.34 | 87.16 | 89.84 | 88.48 |
| Seed OSS 36B | 11.34 | 4.60 | 20.08 | 13.06 | 28.50 | 91.16 | 87.96 | 68.07 | 90.49 | 91.89 | 91.18 |
| Ministral 3 14B | 26.98 | 7.76 | 47.73 | 50.93 | 58.91 | 97.18 | 72.26 | 59.62 | 86.77 | 90.75 | 88.71 |
| Ministral 3 8B | 17.26 | 2.83 | 34.11 | 37.31 | 36.34 | 92.23 | 46.35 | 47.99 | 82.20 | 87.69 | 84.86 |
| Kimi K2 Thinking | 44.97 | 30.02 | 66.57 | 58.02 | 67.46 | 98.20 | 96.06 | 79.82 | 95.09 | 96.86 | 95.96 |
| Kimi Linear 48B | 4.87 | 0.19 | 10.18 | 8.58 | 14.96 | 99.22 | 48.46 | 74.37 | 79.38 | 82.05 | 80.69 |
| GLM 4.7 | 56.83 | 39.13 | 80.33 | 77.24 | 80.76 | 99.92 | 94.86 | 74.35 | 93.48 | 94.53 | 94.00 |
| GLM 4.7 Flash | 20.26 | 4.41 | 47.59 | 37.31 | 32.30 | 97.81 | 56.80 | 56.18 | 88.03 | 90.80 | 89.39 |
| MiniMax M2.1 | 45.91 | 21.98 | 81.71 | 69.22 | 76.72 | 99.56 | 95.02 | 57.09 | 86.65 | 90.76 | 88.66 |
| GPT OSS 120B | 49.56 | 30.86 | 74.00 | 70.34 | 76.48 | 99.43 | 96.58 | 67.65 | 90.46 | 93.35 | 91.88 |
| GPT OSS 20B | 33.13 | 17.33 | 51.17 | 49.44 | 62.00 | 94.34 | 90.56 | 67.54 | 90.86 | 92.76 | 91.80 |
| Mimo V2 Flash | 40.43 | 17.43 | 73.04 | 64.37 | 71.26 | 97.84 | 80.42 | 58.58 | 86.67 | 93.38 | 89.90 |
| Deepseek V3.2 | 50.70 | 29.18 | 79.78 | 73.51 | 81.47 | 99.97 | 92.86 | 68.98 | 91.01 | 94.88 | 92.90 |
| **闭源大语言模型** | | | | | | | | | | | |
| Gemini 3 Pro | 67.41 | 51.67 | 90.37 | 82.46 | 89.07 | 99.64 | 98.70 | 87.15 | 96.08 | 96.07 | 96.08 |
| Qwen3 Max | 61.84 | 44.14 | 85.56 | 82.28 | 85.27 | 100 | 94.73 | 72.42 | 91.75 | 95.82 | 93.74 |
| Qwen3 Coder Plus | 42.05 | 20.59 | 63.41 | 71.08 | 77.91 | 99.95 | 94.03 | 65.09 | 89.94 | 94.24 | 92.04 |
| Seed 1.8 | 60.58 | 43.22 | 85.83 | 77.05 | 84.80 | 99.40 | 97.45 | 76.93 | 94.27 | 96.24 | 95.25 |

#### 4.2.1 闭源模型的主导与开源模型的追赶

表1显示，闭源模型 Gemini 3 Pro [10] 在总体表现上占据主导地位，总体准确率（Overall Accuracy，OA）达 67.41%。值得注意的是，在对逻辑推理要求最高的指标计算（Metrics Calculation，MC）任务上，它取得了 51.67% 的最高分。相比之下，表现最好的开源模型 GLM 4.7 的 OA 为 56.83%、MC 为 39.13%，在 OA 上落后 Gemini 3 Pro 10.58 个百分点，在 MC 上落后 12.54 个百分点。这一差距表明，开源模型在复杂金融逻辑运算上仍面临显著瓶颈。

#### 4.2.2 各任务对 Scaling Law 的敏感度差异

基于表1中 Qwen3 系列（参数从 4B 到 235B）的数据分析发现，不同任务对模型参数规模的敏感度差异显著。逻辑推理任务对参数规模高度敏感：当模型规模从 235B 缩小到 4B 时，指标计算（MC）得分从 34.71% 骤降至 1.77%，计算能力几乎完全丧失。相反，指标检索任务对参数规模的敏感度较低：在同一对比组中，指标检索的 F1 分数仅从 94.18% 降至 88.48%，Qwen3 4B 仍保持相对较高的检索水准。这说明，小参数模型虽难以完成复杂的策略逻辑计算，但在基础信息检索上仍有良好潜力。

#### 4.2.3 缺少 CoT 导致的语法与逻辑能力解耦

表1对非 CoT 模型的评估凸显了语法熟练度与逻辑推理之间的显著解耦。Kimi Linear 48B 就是典型：其执行正确率（ECR）高达 99.22%，但执行准确率（EA）仅 48.46%，指标计算（MC）得分更是只有 0.19%，说明其生成的是可执行但逻辑有缺陷的代码。类似地，Seed OSS 36B 取得 87.96% 的较高 EA，但 OA 仅 11.34%，表明成功的数据检索无法保证下游推理的成功。这些结果证实，CoT 对于把代码生成与量化回测所需的严密逻辑推导结合起来是必不可少的。

#### 4.2.4 指标计算任务的准确率分析

对涉及七类 KPI 的指标计算问题，我们可视化了表现前三的开源模型与前三的闭源模型的成绩（见图4）。

**复杂数学逻辑是最大瓶颈。** 图4显示，随着 KPI 复杂度上升，模型表现急剧下滑。像胜率、最大回撤这类逻辑上较简单的指标准确率较高，而波动率、Sharpe 比率等复杂统计指标在所有模型中都是「重灾区」，通过率明显更低。这一趋势印证：当任务从基础算术升级到复杂的统计运算（如方差、年化）时，LLM 生成代码的可靠性会急剧衰减（详细错误分析见附录 E.2）。

**闭源模型在「高阶逻辑」上的护城河。** 图4中，Gemini 3 Pro 以 51.67% 的综合准确率（All）领先，其核心优势在于对高难度指标的掌握。在最易出错的 Sharpe 与 Vol 指标上，Gemini 3 Pro 保持显著领先（分别比第二名 Qwen3 Max 高出约 4.48 与 1.62 个百分点）。这意味着顶级闭源模型在理解复杂数学公式并将其翻译为精确的 Python/SQL 实现时具有更强的逻辑严谨性，能够处理年化系数调整、除零保护这类细节。

**开源模型：极值强、统计弱。** 代表开源模型的 GLM 4.7（All 39.13%）在 MDD（最大回撤）计算上取得 54.55% 的准确率，甚至超过闭源模型 Seed 1.8（52.86%）。MDD 的核心逻辑是「追踪历史净值峰值以来的最大跌幅」，是典型的「极值追踪」逻辑。然而，在涉及「分布统计」逻辑的 Vol KPI 上，GLM 4.7 只得 22.37%。这一反差说明，顶级开源模型已完全有能力生成逻辑清晰的过程式计算代码，但在处理抽象统计计算时仍表现出高错误率（如公式误用、库函数调用错误）。

**基座模型的「逻辑塌陷」区。** 以 GPT OSS 120B 为例，其 Vol 与 Sharpe KPI 得分分别只有 16.71% 与 13.06%。这表明部分模型在面对复杂金融计算时，代码实现的正确性几乎完全丧失。如此低的分数很可能源于模型无法正确理解「年化波动率」与「日波动率」之间的换算关系，或在编码时忽略数据预处理（如对数收益转换），导致计算结果偏离标准值甚远。

**合成数据忠实镜像专家手工子集的难度。** 除绝对分数外，比较图4中合成集与专家手工子集的雷达图可以发现，二者外轮廓高度吻合：模型在 Vol 与 Sharpe 上始终最差，而在更简单的 KPI 上准确率高得多。这种形态上的一致性表明，合成的 BacktestBench 数据忠实保留了真实回测指标的内在难度层级，说明两个数据集具有相似的底层任务分布，而非我们数据生成流程造成的伪影。

**图4：Metrics Calculation 任务的模型性能详解。All 表示整个指标计算任务的总体成绩；缩写：Sharpe：年度 Sharpe 比率，Calmar：Calmar Ratio，MDD：最大回撤，P/L：盈亏比，Return：收益率比率，Vol：波动率，WR：胜率。前两行为合成 BacktestBench 数据集上的结果，最后一行的灰色雷达图报告专家手工评估集上的表现（原文第7页）**

### 4.3 消融研究

#### 4.3.1 Short Code 对 SQL 生成的影响

我们通过对比纳入与不纳入 Short Code 机制时的 SQL 生成表现，分析该机制的影响。如图5所示，引入 Short Code 在所有被评估模型上都一致提升了执行准确率（EA）。具体而言，MiniMax M2.1 与 GPT OSS 20B 的性能跃升最为显著，EA 提升超过 20 个百分点；而 GPT OSS 120B、GLM 4.7 这类稳健型选手也有明显增益。这些结果证实，Short Code 充当了关键的语义锚点，有效引导模型把自然语言意图映射到精确的数据库 schema 元素。

**图5：Short Code 消融实验（原文第7页）**

#### 4.3.2 Short Code 与 SQL 质量的独立影响

为深入探究 Short Code 与 SQL 生成质量对策略回测表现的独立影响，我们设计了五种实验配置进行对比分析。Vanilla 作为基线：LLM 直接从用户查询生成 SQL 与回测代码，不含任何 Short Code 信息。Ours 是 AutoBacktest 的完整实现，包含检索增强的 Short Code 上下文。此外我们引入三个变体：GI+PS（Gold Indicator + Predicted SQL）使用真值 Short Code（Gold Indicator）作上下文、由 LLM 预测 SQL；NI+GS（No Indicator + Gold SQL）不使用 Short Code、但提供真值 SQL（Gold SQL）；GI+GS（Gold Indicator + Gold SQL）同时提供真值 Short Code 与 Gold SQL，作为理论上性能上界。

图6的实验结果揭示了 Short Code 在策略生成流水线中的决定性作用。总体而言，所有包含 Short Code 信息的配置（Ours、GI+PS、GI+GS）都显著优于不含它的配置（Vanilla、NI+GS）。值得注意的是，尽管 NI+GS 方法使用了完美的 Gold SQL，其表现虽好于 Vanilla 基线，却仍大幅落后于三组含 Short Code 的配置。这一现象有力地证明：在提示词中加入 Short Code 能显著增强 LLM 理解与应用金融指标的能力，其收益远超单纯优化 SQL 语句。此外，Ours 与 GI+PS 相比差异极小，在部分 GPT OSS 模型上 Ours 甚至略好（可能源于实验随机误差）。这进一步说明，只要 Short Code 上下文准确，即使生成的 SQL 有小瑕疵，LLM 也能通过上下文理解生成正确的最终回测代码，凸显了 AutoBacktest 框架对 SQL 错误的稳健性。

**图6：Ground Truth 消融实验（原文第8页）**
## 5 相关工作

### 5.1 基于 LLM 的策略回测

近期工作探索了将 LLM 用于量化任务，但回测的严谨性上仍存在空白。Automate Strategy Finding [12] 与 QuantAgent [28] 关注因子挖掘与自我改进的交易 agent，优先考虑盈利能力，而非底层代码执行的标准化与可复现性。类似地，FinMem [35] 处理交易决策的长期记忆，却忽略了复杂数据检索与指标计算的挑战。AutoPrep [9] 自动化了通用的表格数据预处理，但缺少防止金融回测前视偏差所需的专业时间逻辑。

### 5.2 策略回测数据集

现有基准主要面向强化学习或特定子任务，而非完整的回测工作流。TradeMaster [26] 与 FinRL-Meta [15] 提供了广泛的市场环境用于训练 RL agent，但不评估可解释策略逻辑的生成。FNSPID [7] 把新闻与市场数据对齐，但主要作为信息检索资源。QuantEval [11] 评估策略编码，但规模仅限于 60 个问题。类似地，StockBench [4] 优先考虑 agentic 交易决策的盈利能力，Market-Bench [24] 评估入门级策略的实现准确率。相比之下，BacktestBench 开创了对端到端量化研究工作流的大规模评估：它跨越自然语言理解、SQL 检索与严格回测执行，全面评估把复杂自然语言翻译为可执行回测逻辑的能力。

## 6 结论

本文提出了 BacktestBench——一个面向自动化量化策略回测的开创性基准，该领域以复杂的时间逻辑与严谨的精度要求为特征。为支撑这一工作，我们构建了一个大规模数据集，包含源自真实市场记录的 18,246 个高质量 QA 对，覆盖四类核心决策任务：指标计算、标的选股、策略选择与参数确认。与此资源配套，我们提出 AutoBacktest——一个模仿量化研究员专业工作流的多智能体协作框架，实现从自然语言策略描述到可执行回测代码的端到端自动化。我们在 BacktestBench 上系统评估了 23 个主流 LLM，并开展全面的消融研究，以识别该领域的关键性能驱动因素。通过建立标准化的评估协议与严格的数据资源，本工作弥合了通用代码生成与量化投资研究之间的鸿沟，为智能金融决策的未来发展奠定了坚实基础。

## 致谢

本工作部分受国家自然科学基金（NSFC）62272050 号项目资助，以及由广东省教育厅资助的北京师范大学—香港浸会大学联合国际学院项目资助；部分受珠海市科技创新局 2320004002772 号项目资助，以及北京师范大学（珠海）跨学科智能超级计算机中心资助。

## 参考文献（从略）

参考文献从略，见原文。

## A 因子

本节给出 BacktestBench 全程使用的所有因子与 KPI 的完整参考。表5列出基准所用因子的完整清单，表6与表7分别详述因子、KPI 的全名与短代码对应关系。

**图7：原子策略函数示例 AmountMa6SellStrategy（原文第19页）**

```python
def AmountMa6SellStrategy(df: pd.DataFrame, window: int = 6, threshold: float = 1.5) -> list:
  """
  Strategy Logic: Sell when the previous day's (T-1) trading amount significantly exceeds the average
  of the 6 days prior to that (T-2 to T-7). This "breakout" in volume signals potential distribution
  or abnormal selling pressure.
  Formula: Amount[T-1] > threshold * Average(Amount[T-2] ... Amount[T-7])
  Inputs:
     df (pd.DataFrame): Market Data containing 'trade_date' and 'amount_traded'.
     window (int): The lookback period for the moving average (default=6).
     threshold (float): The multiplier to define a volume spike (default=1.5).
  Outputs:
     list: List of 'trade_date' (T-day) where the sell signal is available for execution.
  """
  df = df.sort_values("trade_date").reset_index(drop=True)
  # 1. Get the trading amount for T-1 (The day we are analyzing for a spike)
  # At index T, this gives Amount[T-1]
  amount_t_minus_1 = df['amount_traded'].shift(1)
  # 2. Calculate the Moving Average of the amount for the period *prior* to T-1
  # We want to compare Amount[T-1] against the average of Amount[T-2]...Amount[T-7].
  # Step A: df['amount_traded'].rolling(window).mean() calculates Mean(Amount[i]...Amount[i-window+1]) at index i.
  # Step B: .shift(2) moves the value at index T-2 to index T.
  # So at index T, we get the rolling mean calculated at T-2 (which covers T-2 to T-7).
  ma_amount_prior = df['amount_traded'].rolling(window=window, min_periods=window).mean().shift(2)
  # 3. Generate Signal
  # Compare T-1 volume against the historical baseline (excluding T-1 itself to avoid bias)
  signal = amount_t_minus_1 > (threshold * ma_amount_prior)
  return df.loc[signal, 'trade_date'].tolist()
```

我们另外在图7中提供了一个原子策略函数示例。示例 AmountMa6SellStrategy 在 T − 1 日的交易量显著超过其前 6 天（T − 2 至 T − 7）平均值时触发卖出信号。这里，阈值参数用作乘数，界定何为显著的成交量激增：只有当 T − 1 日的成交量大于历史平均值乘以该阈值时才产生信号。这一设计通过把 T − 1 日的观测成交量与仅由 T − 1 之前数据计算出的基线相比较，严格避免前视偏差，保证第 𝑇 天的决策只依赖历史上可得的信息。

值得注意的是，看似相似但时间窗口不同的因子（如 5 日与 20 日移动平均）在本基准中被视为不同的因子。这一区分至关重要，因为这些差异捕捉的是根本不同的市场动态：较短窗口反映短期动量与波动模式，较长窗口则指示长期趋势与结构性运动。因此，每个时间窗口变体都是具有不同预测特征的独特因子，不能视为等价或可互换。

因子与 KPI 的命名体系在多阶段 AutoBacktest 流水线中扮演关键角色。在 Summarizer 阶段，系统用全名（如 "5-day Moving Average" 或 "Annual Sharpe Ratio"）检索并识别指标（包括因子与 KPI）。随后在 Retriever 与 Coder 阶段，全名及其对应短代码都会被注入提示词上下文。这种双重表示让 LLM 通过全名理解语义含义，同时借助短代码生成简洁、标准化的代码，从而保证一致性、减少自动化回测过程中的歧义。

**图8：数据集 QA 示例（原文第20页）**

```
strategy: We want to backtest China Nuclear Engineering Corporation Limited on the Shanghai Stock Exchange from
29 Nov 2022 to 13 Mar 2025 with an initial capital of CNY 1,970,000. Please open a position whenever yesterday's
traded volume is greater than the 12-day moving average of volume calculated from the 12 days ending on yesterday
(i.e., including yesterday). Close the entire position when yesterday's traded amount exceeds 1.5 times the 20-day
moving average of amount computed from the 20 days ending the day before yesterday (i.e., excluding yesterday).
Finally, compute the Calmar ratio for this strategy.
strategy_type: "metrics_calculation"
factors: ["20-day Moving Average of Trading Amount","12-day Moving Average of Volume","Calmar Ratio"]
KPI: "Calmar Ratio"
SQL_statement: SELECT amount_traded, closing_price, opening_price, trade_date, volume_traded FROM
shanghai_stock_exchange WHERE name IN ('China Nuclear Engineering Corporation Limited') AND trade_date >=
'2022-11-29' AND trade_date <= '2025-03-13';
code: """
import pandas as pd
import numpy as np
def VolumeMA12BuyStrategy(df: pd.DataFrame, window: int = 12) -> list:
        ······
        return df.loc[condition, 'trade_date'].tolist()
def AmountMa20SellStrategy(df: pd.DataFrame, window: int = 20, threshold: float = 1.5) -> list:
        ······
        return df.loc[signal, 'trade_date'].tolist()
def calculate_strategy_calmar_ratio(df, buy_dates, sell_dates, initial_capital):
        ······
        return round(calmar_ratio, 6)
# ========== Execution Logic Section ==========
# Stock Information
initial_capital = 1970000 # Initial Capital
stock_name = ['China Nuclear Engineering Corporation Limited'] # Stock Name
result = DATAFRAME
# Calculate buy/sell signals
buy_dates = list(set(VolumeMA12BuyStrategy(result)))
sell_dates = list(set(AmountMa20SellStrategy(result)))
# Calculate Strategy Performance Metric
strategy_target = calculate_strategy_calmar_ratio(result, buy_dates, sell_dates, initial_capital)
"""
answer: 0.41591
```

**表5：策略构建中使用的全部因子。Type 表示该因子用作买入信号、卖出信号还是两者皆可。**

| 因子 | 因子全名 | 类型 |
| --- | --- | --- |
| Amount MA 6 | 6-day MA of Trading Amount | 双向 |
| Amount MA 20 | 20-day MA of trading amount | 双向 |
| Amount Std 6 | 6-day Standard Deviation of Trading Amount | 卖出 |
| ATR 6 | 6-day Average True Range | 双向 |
| ATR 20 | 20-day Average True Range | 双向 |
| BBI | Bull and Bear Index | 双向 |
| BIAS 5 | 5-day Bias | 双向 |
| BIAS 60 | 60-day Bias | 双向 |
| Bollinger Lower Band | Bollinger Lower Band | 买入 |
| Bollinger Upper Band | Bollinger Upper Band | 卖出 |
| Bull Power 13 | 13-day Bull Power | 买入 |
| CCI 15 | 15-day Commodity Channel Index | 双向 |
| CCI 20 | 20-day Commodity Channel Index | 双向 |
| EMA 5 | 5-day Exponential Moving Average | 双向 |
| EMA 12 | 12-day Exponential Moving Average | 双向 |
| MA 5 | 5-day Moving Average | 双向 |
| MA 10 | 10-day Moving Average | 双向 |
| MA 20 | 20-day Moving Average | 双向 |
| MA 60 | 60-day Moving Average | 双向 |
| MACD | Moving Average Convergence Divergence | 双向 |
| Net Money Flow 20 | 20-day Net Money Flow | 双向 |
| PLRC 12 | 12-day Price Linear Regression Coefficient | 双向 |
| Price MA Ratio 5 | Price to 5-day MA Ratio | 双向 |
| Price MA Ratio 20 | Price to 20-day MA Ratio | 双向 |
| Price MA Ratio 120 | Price to 120-day MA Ratio | 双向 |
| PSY 6 | 6-day Psychological Line | 双向 |
| PSY 12 | 12-day Psychological Line | 双向 |
| Return Kurtosis 60 | 60-day Kurtosis of Daily Returns | 卖出 |
| Return Skewness 60 | 60-day Skewness of Daily Returns | 双向 |
| Return Variance 20 | 20-day Variance of Daily Returns | 卖出 |
| ROC 6 | 6-day Rate of Change | 双向 |
| ROC 12 | 12-day Rate of Change | 双向 |
| ROC 20 | 20-day Rate of Change | 双向 |
| ROC 120 | 120-day Rate of Change | 双向 |
| RSI | Relative Strength Index | 双向 |
| Sharpe Ratio 120 | 120-day Sharpe ratio | 双向 |
| Single Day VPT | Single-day Price Volume Trend | 双向 |
| Volume EMA 5 | 5-day Exponential Moving Average of Volume | 双向 |
| Volume EMA 10 | 10-day EMA of Volume | 双向 |
| Volume EMA 26 | 26-day Exponential Moving Average of Volume | 双向 |
| Volume MA 12 | 12-day Moving Average of Volume | 双向 |
| Volume ROC 12 | 12-day Volume Rate of Change | 双向 |
| Volume Std 10 | 10-day Standard Deviation of Trading Volume | 双向 |

**表6：带 Short Code 的因子。**

| 因子 | Short Code |
| --- | --- |
| Amount MA 6 | DELAY(AMOUNT,1)/DELAY(SMA(AMOUNT,6),2) |
| Amount MA 20 | DELAY(AMOUNT,1)/DELAY(SMA(AMOUNT,20),2) |
| Amount Std 6 | STD(DELAY(AMOUNT,1),6)/SMA(STD(DELAY(AMOUNT,1),6),20) |
| ATR 6 | DELAY(EMA(MAX(MAX(HIGH-LOW,ABS(HIGH-DELAY(CLOSE,1))),ABS(LOW-DELAY(CLOSE,1))),6),1) |
| ATR 20 | DELAY(EMA(MAX(HIGH-LOW,MAX(ABS(HIGH-DELAY(CLOSE,1)),ABS(LOW-DELAY(CLOSE,1)))),20),1) |
| BBI | (SMA(DELAY(CLOSE,1),3)+SMA(DELAY(CLOSE,1),6)+SMA(DELAY(CLOSE,1),12)+ SMA(DELAY(CLOSE,1),24))/4 |
| BIAS 5 | (DELAY(CLOSE,1)-SMA(DELAY(CLOSE,1),5))/SMA(DELAY(CLOSE,1),5)∗100 |
| BIAS 60 | DELAY((CLOSE-SMA(CLOSE,60))/SMA(CLOSE,60)∗100,1) |
| Bollinger Lower Band | SMA(DELAY(CLOSE,1),20)-2.0∗STD(DELAY(CLOSE,1),20) |
| Bollinger Upper Band | SMA(DELAY(CLOSE,1),20)+2.0∗STD(DELAY(CLOSE,1),20) |
| Bull Power 13 | DELAY(HIGH,1)-DELAY(EMA(CLOSE,13),1) |
| CCI 15 | DELAY(((HIGH+LOW+CLOSE)/3-SMA((HIGH+LOW+CLOSE)/3,15))/(0.015∗SMA(ABS((HIGH+LOW+CLOSE)/3- SMA((HIGH+LOW+CLOSE)/3,15)),15)),1) |
| CCI 20 | DELAY(((HIGH+LOW+CLOSE)/3-SMA((HIGH+LOW+CLOSE)/3,20))/(0.015∗SMA(ABS((HIGH+LOW+CLOSE)/3- SMA((HIGH+LOW+CLOSE)/3,20)),20)+1e-20),1) |
| EMA 5 | DELAY(EMA(CLOSE,5),1) |
| EMA 12 | DELAY(EMA(CLOSE,12),1) |
| MA 5 | SMA(DELAY(CLOSE,1),5) |
| MA 10 | SMA(DELAY(CLOSE,1),10) |
| MA 20 | SMA(DELAY(CLOSE,1),20) |
| MA 60 | SMA(DELAY(CLOSE,1),60) |
| MACD | (EMA(DELAY(CLOSE,1),12)-EMA(DELAY(CLOSE,1),26))-EMA(EMA(DELAY(CLOSE,1),12)- EMA(DELAY(CLOSE,1),26),9) |
| Net Money Flow 20 | DELAY(SUM(SIGN((HIGH+LOW+CLOSE)/3-DELAY((HIGH+LOW+CLOSE)/3,1))∗(HIGH+LOW+CLOSE)/3∗VOLUME,20),1) |
| PLRC 12 | LINEARREG_SLOPE(DELAY(CLOSE,1),12) |
| Price MA Ratio 5 | OPEN/SMA(DELAY(CLOSE,1),5) |
| Price MA Ratio 20 | OPEN/SMA(DELAY(CLOSE,1),20) |
| Price MA Ratio 120 | OPEN/SMA(DELAY(CLOSE,1),120) |
| PSY 6 | (100/6)∗SUM(DELAY(IF(CLOSE>DELAY(CLOSE,1),1,0),1),6) |
| PSY 12 | (100/12)∗SUM(IF(DELAY(CLOSE,1)>DELAY(CLOSE,2),1,0),12) |
| Return Kurtosis 60 | DELAY(SMA(((CLOSE/DELAY(CLOSE,1)-1)-SMA((CLOSE/DELAY(CLOSE,1)-1),60))∗∗4,60)/SMA(((CLOSE/DELAY(CLOSE,1)- 1)-SMA((CLOSE/DELAY(CLOSE,1)-1),60))∗∗2,60)∗∗2-3,1) |
| Return Skewness 60 | DELAY(SKEW(PERCENTAGE_CHANGE, 60), 1) |
| Return Variance 20 | DELAY(VAR(CLOSE/DELAY(CLOSE,1)-1,20),1) |
| ROC 6 | (DELAY(CLOSE,1)-DELAY(CLOSE,7))/DELAY(CLOSE,7)∗100 |
| ROC 12 | (DELAY(CLOSE,1)-DELAY(CLOSE,13))/DELAY(CLOSE,13)∗100 |
| ROC 20 | (DELAY(CLOSE,1)-DELAY(CLOSE,21))/DELAY(CLOSE,21)∗100 |
| ROC 120 | (DELAY(CLOSE,1)-DELAY(CLOSE,121))/DELAY(CLOSE,121)∗100 |
| RSI | DELAY(100-100/(1+EMA(MAX(CLOSE-DELAY(CLOSE,1),0),14)/EMA(ABS(MIN(CLOSE-DELAY(CLOSE,1),0)),14)),1) |
| Sharpe Ratio 120 | DELAY((SMA((CLOSE/DELAY(CLOSE,1)-1),120)-0.0001)∗SQRT(252)/STD((CLOSE/DELAY(CLOSE,1)-1),120),1) |
| Single Day VPT | (DELAY((CLOSE/DELAY(CLOSE,1)-1)∗VOLUME,1)-SMA(DELAY((CLOSE/DELAY(CLOSE,1)-1)∗VOLUME,2),20))/ STD(DELAY((CLOSE/DELAY(CLOSE,1)-1)∗VOLUME,2),20) |
| Volume EMA 5 | DELAY(VOLUME,1)/DELAY(EMA(VOLUME,5),1) |
| Volume EMA 10 | DELAY(VOLUME/EMA(VOLUME,10),1) |
| Volume EMA 26 | DELAY(VOLUME,1)/DELAY(EMA(VOLUME,26),1) |
| Volume MA 12 | DELAY(VOLUME,1)>DELAY(SMA(VOLUME,12),1) |
| Volume ROC 12 | (DELAY(VOLUME,1)-DELAY(VOLUME,13))/DELAY(VOLUME,13)∗100 |
| Volume Std 10 | STD(DELAY(VOLUME,1),10)/SMA(STD(DELAY(VOLUME,1),10),20) |

**表7：带计算代码的 KPI。（注：PV 表示 Portfolio Value；PNL 表示 Profit and Loss；N 表示计算窗口。）**

| KPI | KPI 全名 | Short Code |
| --- | --- | --- |
| Return | Return Ratio | (CASH_FINAL + POSITION_FINAL ∗CLOSE) INITIAL_CAPITAL- 1 |
| MDD | Max Drawdown | MAX((CUMMAX(CASH + POSITION ∗CLOSE) - (CASH + POSITION ∗CLOSE)) / CUMMAX(CASH + POSITION ∗CLOSE)) |
| Vol | Volatility | STD(PV / DELAY(PV, 1) - 1, N) |
| Sharpe | Annual Sharpe Ratio | (MEAN((PV - DELAY(PV,1)) / DELAY(PV,1)) - 0.0001) / STD((PV - DELAY(PV,1)) / DELAY(PV,1)) ∗SQRT(252) |
| WR | Win Rate | SUM(IF(PNL > 0, 1, 0)) / COUNT(PNL) ∗100 |
| P/L | Profit Loss Ratio | (SUM(IF(PNL > 0, PNL, 0)) / ABS(SUM(IF(PNL < 0, PNL, 0)))) * (SUM(IF(PNL < 0, 1, 0)) / SUM(IF(PNL > 0, 1, 0))) |
| Calmar | Calmar Ratio | ((POW(LAST(PV)/FIRST(PV),252/COUNT(PV))-1)/ABS(MIN((PV-CUMMAX(PV))/CUMMAX(PV)))) |

译注：表7 中 Return 行的公式在原文文本提取中疑似丢失了一个除号（应为除以 INITIAL_CAPITAL），此处按提取结果原样保留。

## B 回测协议与标准化交易规则

若干金融 KPI 对实现细节敏感，在非标准化设定下容易被错误设定。此外，LLM 在推理这类计算时容易产生幻觉。因此，我们定义了一套标准化的回测与交易协议，强制确定性规则与无歧义的计算逻辑，保证回测结果唯一且可复现。

**执行机制（Execution Mechanism）。** 回测框架采用只做多的交易方案，买卖操作严格交替，明确禁止日内回转交易（T+0）。所有交易都以可观察、定义明确的价格执行：买单按开盘价成交（Buy at Open），卖单按收盘价成交（Sell at Close），从而消除日内价格路径的歧义。若持仓在回测窗口最后一天仍未平仓，框架按相应收盘价强制清算。

**资金分配与约束（Allocation and Constraints）。** 模拟采用固定资金设定，初始财富记为 Cash0，不允许杠杆。在每个买入日 𝑡，交易规模 𝑄𝑡 按下式动态计算：

$$𝑄𝑡 = \frac{Cash𝑡}{Priceopen,𝑡}$$

并满足最小手数约束 𝑄𝑡 ∈ Z≥100，即以 100 股整手交易。在卖出日，框架强制完全平掉当前持仓。为隔离交易逻辑本身的影响，基线实验把交易成本与税费设为零。

**业绩评估（Performance Evaluation）。** 框架在计算收益时采用逐日盯市（mark-to-market）口径。组合价值 PV𝑡 在日期 𝑡 的值，等于所有持仓按收盘价计价的市值与剩余现金余额之和。日收益率按下式计算：

$$𝑟𝑡 = \frac{PV𝑡 − PV𝑡−1}{PV𝑡−1}$$

没有持仓的日子取 𝑟𝑡 = 0。年化收益与年化波动率遵循每年 252 个交易日的惯例，评估年度 Sharpe Ratio 时日无风险利率固定为 0.0001。Calmar Ratio 按年化收益与最大回撤之比计算，强调下行风险调整后的表现。

**数据完整性假设（Data Integrity Assumption）。** 回测假设输入价格时间序列完整且严格按交易日排序。当前框架不显式处理缺失交易日、不规则日历或乱序记录，我们把这些数据质量问题留作未来的扩展。
## C 数据集

### C.1 数据库表结构

表2给出股票 PostgreSQL [25] 数据库的表结构，详列 15 个组成列及其数据类型与说明。这一统一表结构一致应用于以下三张交易所表：

- beijing_stock_exchange
- shenzhen_stock_exchange
- shanghai_stock_exchange

**表2：股票数据库的表结构。**

| 列名 | 类型 |
| --- | --- |
| name | TEXT |
| stock_code | TEXT |
| trade_date | DATE |
| opening_price | NUMERIC |
| closing_price | NUMERIC |
| highest_price | NUMERIC |
| lowest_price | NUMERIC |
| volume_traded | NUMERIC |
| amount_traded | NUMERIC |
| percentage_change | NUMERIC |

译注：原文说明该表共 15 列，文本提取仅得到上列 10 列，其余 5 列原文此处无法提取。

### C.2 策略数据生成细节

本小节详述第 3 节引入的四类任务族的构建流水线。除非另有说明，所有策略实例均由附录 A 所述的信号池与 KPI 库在标准化回测协议下生成。

**表3：BacktestBench 在四类核心量化投资任务族（指标计算、标的选股、参数确认、策略选择）上的整体数据集统计。**

| 统计项 | 数值 |
| --- | --- |
| 问题总数 | 18,246 |
| 训练集 | 10,215 |
| 验证集 | 4,195 |
| 测试集 | 3,836 |
| 指标计算 | 10,244 |
| 标的选股 | 3,455 |
| 参数确认 | 2,548 |
| 策略选择 | 1,999 |
| 平均每策略长度 | 141.7 |

**基础框架与指标计算任务。** 对指标计算任务，生成流水线包含三个阶段：信号池采样、逻辑组合与基于回测的验证。首先，系统按预定义权重从中国三大交易所中采样一只股票，并截取一段至少 252 个交易日的连续历史窗口，标准化为包含 OHLCV 字段的 DataFrame。接着，借助代码内省，框架独立采样最多四个买入侧与四个卖出侧原子因子，通过集合交集融合它们的信号（只有当所有选中的因子在同一天触发时才发生交易），并随机选取一个 KPI 作为优化目标，组装成可执行的 Python 策略脚本。最后，脚本在隔离解释器中运行，KPI 值被记录为真值答案；交易稀疏或输出异常（如 NaN 或无穷值）的低质量样本被过滤掉，最终得到 17,082 个指标计算程序。

**标的选股任务。** 标的选股任务把上述框架扩展到多资产设定。系统不再只采样单一标的，而是采样一组候选股票，把同一随机生成的策略与 KPI 目标并行应用于每只资产，并在相同的实验条件下运行回测。根据 KPI 的经济含义，框架采用最大化原则（面向收益类指标，如收益率或 Sharpe Ratio）或最小化原则（面向下行或风险类指标，如最大回撤或波动率），把表现最好的股票标记为真值，得到 6,098 个标的选股程序。

**参数确认任务。** 参数确认任务模拟在固定策略与环境内受控的超参数调优。系统先用确定性的因子组合与 KPI 构造一个基线策略，再选取一个原子因子（如移动平均突破规则）作为优化目标，并从预定义空间中采样一组离散的候选参数值。对每个候选，保持其余逻辑不变、仅替换目标参数以形成一个策略变体；所有变体都在同一价格路径上回测，并按同一 KPI 选择规则评估，KPI 最优的参数被记录为标签，产生 4,709 个参数确认程序。

**策略选择任务。** 策略选择任务刻画在共享市场环境下从异质策略逻辑中抉择的决策问题。框架采样一小批候选策略（如二元对决 {𝐴, 𝐵} 或三元对决 {𝐴, 𝐵, 𝐶}），为每个候选独立生成买入、卖出因子组合，并约束全部候选在相同历史窗口交易相同标的、使用相同的初始资金与 KPI。随后，动态代码生成把所有候选策略嵌入同一脚本并并行回测；通过在相应的最大化或最小化准则下比较 KPI 值，系统识别出表现最好的逻辑（如 "B"）作为真值标签，得到 5,114 个策略选择程序。

**SQL 查询构建与标注。** 对每个策略实例，框架自动构建并标注一条 SQL 语句，精确复现回测所用的底层数据切片。所有查询遵循标准的 SELECT–FROM–WHERE 模式：采样时，所选交易所、股票与日期区间分别映射到 FROM 子句、股票约束与时间过滤条件（例如 `FROM shenzhen_stock_exchange WHERE name IN ('Ping An Bank') AND trade_date BETWEEN '2019-01-15' AND '2020-03-20'`）。策略代码生成后，系统解析代码以提取实际使用的列（如 opening_price、closing_price、volume_traded），并构造只含必需字段的最小 SELECT 子句，从而避免冗余的数据加载。最终确定的 SQL 字符串与策略代码、回测区间、股票列表一并存入 JSON 文件，保证代码、数据与环境之间的一一对应，便于精确复现与错误追踪。

### C.3 自然语言生成与评估细节

本小节为第 3 节引入的自然语言描述生成与质量评估流水线补充实现细节。

**提示词设计与生成设定。** 我们使用五个特定的本地部署模型进行生成：Kimi-K2-Thinking-BF16、MiniMax-M2.1-BF16、GLM-4.7、GPT-OSS-120B-BF16 与 Qwen3-235B-A22B-Thinking-2507。五个模型都支持 CoT 推理，并配置为指令跟随 LLM。提示词采用模仿真实回测请求的指令式语气，显式地把策略特定逻辑与系统级默认设定（如资金分配与执行微观结构）分开，并要求精确的时间表述（如 "based on T − 1 data"）以避免前视偏差。

**评估标准与报告。** 评估时，每个评估模型为每个代码—文本对生成结构化 JSON 报告，包含代码保真度（code fidelity）与策略有效性（strategy validity）的二值判定，以及简要的错误诊断（如 "parameter mismatch"、"future information usage" 或 "missing exit rule"）。只有获得全部评估者正面判定的描述才会被保留，其余报告用于归类与分析常见的失败模式。

**规模与资源消耗。** 整条流水线处理了 33,003 个策略程序，在部署于 72 块 NVIDIA A800-SXM4-80GB GPU 上的五个模型之间发起 825,075 次 LLM 调用。在严格的验收规则下，最终语料包含 10,244 个指标计算任务、3,455 个标的选股任务、2,548 个参数确认任务与 1,999 个策略选择任务，共 18,246 个样本，划分为 10,215 个训练实例、4,195 个验证实例与 3,836 个测试实例。更多数据集统计见表3。

## D Agent 数据流与交互

在 AutoBacktest 框架中，每个策略实例表示为一条共享记录，初始化为存储在 strategy 字段中的自然语言描述。Summarizer、Retriever 与 Coder 三个 agent 在这条记录上顺序运作，逐步把原始文本转化为完全规格化的回测样本，其中包含因子定义、可执行的数据查询与量化结果。

Summarizer 是系统的语义入口。其输入包括字段 strategy，以及可选的 Financial Indicator 词表全局定义（该词表显式涵盖 43 个交易因子与 7 个业绩 KPI）。基于这些信息，Summarizer 分析策略描述，抽取其中提到的指标，把非正式措辞规范化为标准的 Financial Indicator 名称，并产出一份预测指标的结构化列表，连同后续检索所需的辅助标注。该列表以 predict_indicators 以及精化版本 predict_indicators(BM25) 等字段写回共享记录，充当自由形式语言与金融指标库之间的语义桥梁。

Retriever 在 Summarizer 产出的增强记录之上构建。其输入包括原始策略文本 strategy、预测指标列表 predict_indicators(BM25)，以及一份独立的金融指标字典——它把每个金融指标名映射到实现层标识符（如 short code 或数据库列名）。利用这些输入，Retriever 构造一个紧凑的文本上下文，把金融指标与其短代码配对，然后生成单条 SQL 语句，指明该策略应从历史数据库取回哪只股票、哪个时间区间与哪些原始字段。在语句被接受之前，Retriever 会对数据库执行它，检查语法正确性与结果非空；如有必要，它会根据错误信息或空输出迭代修订查询。一旦得到有效查询，最终 SQL 字符串以 predict_SQL 存入共享记录。

Coder 是执行端点，把经校验的数据访问规格转化为具体的回测结果。其输入是 Retriever 阶段之后完全增强的记录，包括策略文本 strategy、策略类型 strategy_type（决定任务是指标计算、标的选股、参数确认还是策略选择）、指标上下文 predict_indicators(BM25) 连同指标字典，以及经校验的 SQL 语句 predict_SQL。Coder 先执行 predict_SQL，得到与所请求股票和时段相对应的时间序列市场数据；该数据被视为回测环境，若结果为空，则该记录被提前终止并打上错误标记。若得到非空数据切片，Coder 构造一个任务特定的提示词，把取回表格的预览、规范化指标信息与策略描述组合起来，然后使用工具增强的语言模型在该环境中编写并执行回测代码。最终模型消息被解析以抽取标准化答案，例如 KPI 值、表现最好股票的索引、所选参数或所选策略。抽出的标量答案以 pred_answer 字段追加到共享记录。

## E 实验

### E.1 BM25 在 Summarizer 中的作用

为评估我们框架中检索机制的必要性，我们对 Summarizer 模块开展了消融研究。具体而言，我们比较了各种 LLM 在纳入与不纳入 BM25 算法时的表现。在不带 BM25 的配置（"w/o"）中，Summarizer 仅依靠 LLM 的内部知识来识别相关意图与槽位。反之，带 BM25 的配置（"w"）会把与指标定义、项目元数据相关的检索上下文注入提示词。

**表4：带与不带 BM25 检索时 Summarizer 模块的性能对比。本表评估在各 LLM 的 Summarizer 阶段纳入 BM25 算法的有效性。"w/o" 表示不带 BM25 的基线表现，"w" 表示纳入 BM25 后的表现。指标包括 Accuracy（Acc）、Precision（P）、Recall（R）与 F1 Score。**

| 模型 | BM25 状态 | Acc (%) | P (%) | R (%) | F1 (%) |
| --- | --- | --- | --- | --- | --- |
| DeepSeek V3.2 | w/o | 17.65 | 64.35 | 69.71 | 66.92 |
| DeepSeek V3.2 | w | 68.98 | 91.01 | 94.88 | 92.90 |
| Qwen3 4B | w/o | 13.03 | 61.24 | 63.06 | 59.52 |
| Qwen3 4B | w | 58.34 | 87.16 | 89.84 | 88.48 |
| Qwen3 8B | w/o | 15.64 | 60.98 | 65.24 | 63.04 |
| Qwen3 8B | w | 60.61 | 87.33 | 90.66 | 88.96 |
| Qwen3 14B | w/o | 11.47 | 57.59 | 59.52 | 55.79 |
| Qwen3 14B | w | 60.92 | 87.56 | 90.50 | 89.01 |
| Qwen3 30B | w/o | 20.36 | 68.10 | 70.04 | 69.06 |
| Qwen3 30B | w | 69.73 | 91.78 | 93.25 | 92.51 |
| Qwen3 Next 80B | w/o | 27.42 | 73.88 | 76.39 | 75.12 |
| Qwen3 Next 80B | w | 73.80 | 92.57 | 94.54 | 93.54 |
| Qwen3 235B | w/o | 30.42 | 75.55 | 77.19 | 76.36 |
| Qwen3 235B | w | 76.41 | 93.62 | 94.75 | 94.18 |
| GLM 4.7 | w/o | 24.35 | 72.06 | 73.78 | 72.91 |
| GLM 4.7 | w | 74.35 | 93.48 | 94.53 | 94.00 |
| MiniMax M2.1 | w/o | 14.21 | 60.19 | 65.33 | 62.65 |
| MiniMax M2.1 | w | 57.09 | 86.65 | 90.76 | 88.66 |

表4给出对比结果。BM25 的引入在所有被测模型上都带来了显著的性能提升。例如，DeepSeek V3.2 的 Accuracy 从 17.65% 大幅升至 68.98%，F1 从 66.92% 升至 92.90%。更大的模型（如 Qwen3 235B）同样受益明显，Accuracy 从 30.42% 升至 76.41%。这些结果表明：LLM 虽具备强大的推理能力，但要精确识别量化投资中的领域特定指标与意图，仍需外部知识检索。BM25 算法通过提供准确的上下文有效弥合了这一缺口，从而显著增强了 Summarizer 把自然语言查询映射为正确结构化表示的能力。

### E.2 案例分析

为诊断指标计算任务——特别是波动率与 Sharpe 比率——性能下降的根本原因，我们针对回测过程构建了一个定向分析框架。在我们对 Gemini-3-Pro 的实验中，我们筛选出 SQL 查询准确、指标检索成功的样本，隔离出 Python 代码执行产生意外偏差的实例。分析识别出导致这些失败的两种主要机制。

#### E.2.1 案例 1：波动率计算失败的复合归因分析

本案例考察波动率计算任务中的失败机制：生成代码中的三个系统性逻辑缺陷累积扭曲了回测结果。

主要错误发生在业绩归因环节：代码未能正确初始化收益序列。由于忽略在序列头部插入初始资本作为「第 0 天」基线，首日收益被判为无效并被丢弃。这种左侧截断损害了时间序列的完整性，迫使波动率计算依赖不完整的样本集，引入了显著的数值误差。

此外，在指标构造上，模型误解了 Commodity Channel Index（CCI）中 Mean Absolute Deviation（MAD）的数学定义。代码实现的不是标准的「滚动窗口内的平均绝对偏差」，而是「绝对价格偏差的简单滚动平均」。这一算法差异使买入信号的触发偏离了预期策略。

再者，交易逻辑缺少回测周期所需的边界约束。由于没有禁止在最后一天开仓的过滤器，系统会执行不合规的日内双向交易（开盘时开仓、收盘时被强制清算）。这人为抬高了交易成本、扭曲了最终净值，使波动率计算失效。

#### E.2.2 案例 2：Sharpe 比率评估的系统性偏差

本案例研究影响 Sharpe 比率的失败机制——该指标的准确率高度依赖收益序列的完整性与对交易逻辑的严格遵守。我们观察到两个关键维度上的逻辑缺陷导致评估严重失真。

净值序列的构造存在一个关键缺陷：代码遗漏了「零点锚定」操作。未能在序列头部显式插入初始资本，导致差分计算时首日收益被排除。样本量的减少同时影响分子（年化超额收益）与分母（收益波动率），使算出的 Sharpe 比率来自破碎的时间窗口，统计有效性被破坏。

同时，代码在回测期末的边界控制不足。由于允许不合规的「当日开平仓」操作，系统产生了无效交易成本，并直接由净值序列承担。这人为压低了最终收益表现，使生成的 Sharpe 比率失去作为业绩基准的参考价值。

## F 实现细节

### F.1 LLM 部署

本节详述研究各阶段所用的 LLM 配置。部署分为两个不同阶段：数据构建阶段与实验评估阶段。

在数据构建阶段，我们使用配备 72 块 NVIDIA A800-SXM4-80GB GPU 的高性能计算集群部署五个最先进的开源 CoT 模型。选取这些模型是因为它们具有出色的推理能力，分别是 Kimi-K2-Thinking-BF16、MiniMax-M2.1-BF16、GLM-4.7、GPT-OSS-120B-BF16 与 Qwen3-235B-A22B-Thinking-2507。这些模型的详细规格见表8。为优化推理效率，我们采用 SGLang 与 vLLM 作为部署框架。所有模型统一使用 0.6 的 temperature 参数，以保持生成多样性与稳定性上的一致。

在实验阶段，我们把基础设施扩展到 100 块 NVIDIA A800-SXM4-80GB GPU，本地托管 18 个模型以进行全面基准测试。为补充本地部署，我们通过外部 API 访问若干专有模型：具体而言，Mimo V2 Flash 与 Gemini 3 Pro 通过 OpenRouter 访问，总花费 756 美元；DeepSeek V3.2、Qwen3 Max 与 Qwen3 Coder Plus 使用其官方兼容模式 API（https://dashscope.aliyuncs.com/compatible-mode/v1）；Seed 1.8 通过火山引擎 API（https://ark.cn-beijing.volces.com/api/v3）访问。为保证本地模型与 API 模型之间的公平对比，我们在整个实验中对所有推理严格保持 temperature 为 0.6。

**表8：模型推理配置对比。缩写：Backend = 推理后端，MFS = mem-fraction-static，CoT = Chain of Thought，Algo. = 投机算法（Speculative Algorithm），Steps = speculative-num-steps，TopK = speculative-eagle-topk，Draft = speculative-num-draft-tokens。**

| 模型 | GPUs | Backend | MFS | CoT | Algo. | Steps | TopK | Draft |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Qwen3-235B-A22B-Thinking-2507 | 8 | SGLang | 0.8 | Yes | EAGLE3 | 3 | 1 | 4 |
| Qwen3 Next 80B A3B Thinking | 4 | SGLang | 0.8 | Yes | NEXTN | 5 | 8 | 32 |
| Qwen3 32B | 4 | SGLang | 0.8 | Yes | None | - | - | - |
| Qwen3 30B A3B Thinking 2507 | 2 | SGLang | 0.9 | Yes | None | - | - | - |
| Qwen3 14B | 1 | SGLang | 0.9 | Yes | None | - | - | - |
| Qwen3 8B | 1 | SGLang | 0.9 | Yes | None | - | - | - |
| Qwen3 4B | 1 | SGLang | 0.9 | Yes | None | - | - | - |
| Seed OSS 36B | 2 | vLLM | 0.9 | No | None | - | - | - |
| Ministral 3 14B Reasoning 2512 | 2 | vLLM | 0.9 | Yes | None | - | - | - |
| Ministral 3 8B Reasoning 2512 | 1 | vLLM | 0.9 | Yes | None | - | - | - |
| Kimi-K2-Thinking-BF16 | 32 | SGLang | 0.9 | Yes | None | - | - | - |
| Kimi Linear 48B A3B Instruct | 4 | SGLang | 0.8 | No | None | - | - | - |
| GLM-4.7 | 16 | SGLang | 0.8 | Yes | EAGLE | 3 | 1 | 4 |
| GLM 4.7 Flash | 4 | vLLM | 0.8 | Yes | None | - | - | - |
| MiniMax-M2.1-BF16 | 8 | SGLang | 0.9 | Yes | None | - | - | - |
| GPT-OSS-120B-BF16 | 8 | SGLang | 0.8 | Yes | EAGLE3 | 3 | 1 | 4 |
| GPT OSS 20B BF16 | 2 | SGLang | 0.9 | Yes | None | - | - | - |

模型权重与投机解码配置来源（原文脚注）：

1. https://www.modelscope.cn/models/Qwen/Qwen3-235B-A22B-Thinking-2507
2. https://www.modelscope.cn/models/lmsys/Qwen3-235B-A22B-EAGLE3
3. https://www.modelscope.cn/models/Qwen/Qwen3-Next-80B-A3B-Thinking
4. https://www.modelscope.cn/models/Qwen/Qwen3-32B
5. https://www.modelscope.cn/models/Qwen/Qwen3-30B-A3B-Thinking-2507
6. https://www.modelscope.cn/models/Qwen/Qwen3-14B
7. https://www.modelscope.cn/models/Qwen/Qwen3-8B
8. https://www.modelscope.cn/models/Qwen/Qwen3-4B
9. https://huggingface.co/ByteDance-Seed/Seed-OSS-36B-Instruct
10. https://huggingface.co/mistralai/Ministral-3-14B-Reasoning-2512
11. https://huggingface.co/mistralai/Ministral-3-8B-Reasoning-2512
12. https://www.modelscope.cn/models/unsloth/Kimi-K2-Thinking-BF16
13. https://www.modelscope.cn/models/moonshotai/Kimi-Linear-48B-A3B-Instruct
14. https://www.modelscope.cn/models/ZhipuAI/GLM-4.7
15. https://docs.sglang.io/basic_usage/glm45.html
16. https://www.modelscope.cn/models/ZhipuAI/GLM-4.7-Flash
17. https://www.modelscope.cn/models/QuixiAI/MiniMax-M2.1-bf16
18. https://www.modelscope.cn/models/unsloth/gpt-oss-120b-BF16
19. https://www.modelscope.cn/models/nv-community/gpt-oss-120b-Eagle3
20. https://www.modelscope.cn/models/unsloth/gpt-oss-20b-BF16

### F.2 Agent 实现

我们使用 LangGraph 框架实现 AutoBacktest agent，采用 ReAct（Reasoning and Acting）架构来编排回测工作流。agent 与 PostgreSQL 数据库交互以取回金融数据，并转换为 Pandas DataFrame。我们为 agent 配备了 Python REPL 工具（'create_python_repl_tool'），使其能在该 DataFrame 上直接执行 Python 代码，进行复杂的计算与逻辑校验。

为保证稳健性与标准化输出，该实现包含几个关键组件：

1. 动态上下文构建：系统通过注入特定交易策略、经 BM25 Summarizer 检索的指标定义以及 dataframe schema 动态生成提示词。这保证 LLM 具备代码生成所需的全部上下文。
2. 结构化输出解析：我们为不同任务类型（如指标计算或标的选股）定义了特定的 Pydantic 模型（如 ClassA_FinalAnswerFormat）。这强制了严格的输出格式，便于从 agent 的回复中准确抽取答案。
3. 执行约束：为平衡推理深度与效率、防止无限循环，agent 被配置为每个查询最多 25 步迭代。

系统还包含一个稳健的答案抽取机制，可处理各种回复格式，包括 CoT 轨迹（原文此处标签名无法提取）与 JSON 结构，从而可靠地评估模型的预测。
## G 提示词

本节给出我们工作中使用的五个关键提示词，分为两个不同阶段：数据集构建与 AutoBacktest Agent 工作流。译注：原文这五个提示词以图（图9–图13）的形式给出，文本可完整提取，按规范以代码块保留英文原文。

### G.1 数据集构建提示词

BacktestBench 数据集的构建依赖「Code-to-Text」逆向工程范式。图9展示 Code-to-Strategy 提示词，用于把合成生成的原子策略代码翻译为自然语言描述。该提示词指示 LLM 解释 Python 逻辑，并以模仿人类量化研究员的语气描述交易规则。随后，为保证这些生成描述的高质量与逻辑一致性，我们采用图10所示的 Strategy Evaluation 提示词。该提示词引导另一组 LLM 对照原始代码交叉验证生成文本，检查逻辑、参数值上的差异或潜在幻觉。

**图9：Python 代码转自然语言策略的提示词（原文第21页）**

````
You are a quantitative researcher submitting a backtest request. Your task is to translate the Python code logic into a direct, natural language
request for a simulation.
### 1. Goal: Request Narrative
- Tone: Use an Instructional/Requesting tone (e.g., "We want to backtest...", "Please execute...").
- Precision: While the tone should be natural, the logic must be mathematically precise. Do not sacrifice accuracy for brevity.
- Flow: Write as a continuous, logical request paragraph.
### 2. Implicit Framework Rules (STRICTLY OMIT THESE)
The following are system defaults and must NOT be mentioned. Focus ONLY on the unique strategy logic:
1. Order Sizing: Do not mention minimum 100 shares, odd lots, integers, or full position exits.
2. Session Logic: Do not mention "No buying on last day" or "Forced close on last day."
3. Conflict Resolution: Do not mention simultaneous signal priority.
4. Capital Management: Do not mention fixed capital limits or cash sufficiency checks.
5. Execution: Do not mention "Buy at Open / Sell at Close" unless the code *deviates* from this standard.
6. Math Details: Do not explain standard return formulas, annualization, or window warmups.
7. Data Handling: Do not mention NaN handling.
### 3. Language Guidelines
- Humanize Time (BUT BE PRECISE):
   - Forbidden: "T", "T-1", "Day t".
   - Required: "Today," "yesterday," "the previous day," "the past 20 days."
- Time Reference Precision (CRITICAL):
   - Never describe an indicator vaguely (e.g., "Check the RSI").
   - Always specify the reference day (e.g., "Check yesterday's RSI," "Calculate the MA using data prior to today").
   - If a calculation uses `shift(1)`, explicitly state it is based on yesterday's data.
- Standardize Terms:
   - Forbidden: Variable names (`rolling_mean`, `ma_5`).
   - Required: Financial terms ("Moving Average," "Volume Volatility").
- Clean Numbers: Write "0" instead of "0.0".
### 4. Required Content
Embed the following into your request naturally:
1. Scope: Exchange name, Stock name, Initial Capital, Date Range.
2. Entry Logic: The specific condition to open a position. Explicitly state if it uses today's or yesterday's data.
3. Exit Logic: The specific condition to close the position. Explicitly state if it uses today's or yesterday's data.
4. Metric: The specific performance indicator to calculate.
### 5. Output Format (CRITICAL)
You must output a single JSON object. Do not include markdown formatting (like ```
<!-- 译注：上句括号内的三反引号（```）在原 PDF 提示词中即未闭合（干净重提的 pdftotext 输出同行可证），系原文伪影，忠实保留、不作补全；该三反引号位于行中，不构成 markdown 代码围栏，渲染安全；本注释引用一次该记号亦使全文围栏计数配对。 -->
The JSON key containing the narrative must be exactly matches the expected schema.
Example Structure:
{"nlp_strategy": "YOUR GENERATED TEXT HERE"}
### 6. Few-Shot Examples (Strictly Follow JSON Format)
   Bad Example (Do NOT do this - Pure Text):
   "We want to backtest Stock X... Sell if the 60-day Bias is above 10."
Example:
   {"nlp_strategy": "We want to backtest Shanghai Stock Exchange-listed Stock X from Jan 1, 2020, to Dec 31, 2022, with an initial capital of
CNY 1,000,000. For this test, the strategy should open a position whenever yesterday's closing price exceeds the 20-day Moving Average
(calculated using data up to yesterday). Conversely, please execute a sell if the price falls back below this average. Finally, please calculate the
Sharpe Ratio."}
````

**图10：评估自然语言策略的提示词（原文第22页）**

````
You are a senior quantitative backtesting engineer (Python expert) with 10 years of experience. Your task is to conduct a strict Code Review.
### Input Data Structure
You will receive three parts of input:
1. Base Rules: Hard constraints of the backtesting framework (e.g., lot size, execution price, calculation standards), which are considered absolute
truth and must not be questioned.
2. Trading Strategy: Specific trading ideas defined by the user (e.g., signal triggering conditions, parameter settings).
3. Code Implementation: The Python script written based on the above two points.
### Your Task: Dual-Dimension Audit
Please verify the following two dimensions item by item and generate a JSON audit report.
#### Dimension 1: Code Fidelity
Core Goal: Does the code 100% faithfully reproduce the [Base Rules] and [Trading Strategy]?
Review Checklist:
1. Parameter Consistency: Do values such as `window_size`, `threshold`, and `cash` correspond exactly to the text?
2. Definition Precision: If the [Trading Strategy] is vague (e.g., writing only "moving average" without specifying "N-day", or "price" without
specifying "closing price"), treat it as an implementation error (`False`). The code must not "hallucinate" undefined logic.
3. No Hidden Logic: Does the code contain extra logic not mentioned in the text (e.g., secretly added stop-loss, filters)? If so, treat it as an error.
4. Future Function Detection: Check if future data is used when calculating the signal for the current day (Look-ahead Bias).
#### Dimension 2: Strategy Validity
Core Goal: Is the [Trading Strategy] itself valid regarding quantitative principles? (Note: Do not evaluate the [Base Rules])
Review Checklist:
1. Executability: Can the signal trigger point be executed in the real market? (e.g., requiring a buy at today's highest price, which is unpredictable
in real-time).
2. Logical Closed Loop: Are opening and closing conditions complete? Are there logical loopholes like "buy only, never sell" or "infinite loops"?
3. Causal Logic: Is there reverse causality? (e.g., using position results to infer buy signals).
### Few-Shot Examples (Strictly Follow Logic)
#### Example 1: Mismatch in Parameters (Code False)
*Strategy says "20-day MA", Code uses `rolling(30)`.*
{ "code_correct": false,
   "code_correct_reason": "Parameter mismatch: Strategy specifies a 20-day MA, but code implements `window=30` in `rolling()` function.",
   "strategy_reasonable": true,
   "strategy_reasonable_reason": "Trading strategy is basically reasonable."}
······
########## Base Rules ##########
- Trading Mechanism (Execution): This study adopts a Long-only mechanism. Buy and sell operations strictly alternate; simultaneous buying and
selling in a single trading day is prohibited. Trades are executed as Buy at Open, Sell at Close. No buying is performed on the last day of the
backtest period, and positions are forced closed at the closing price.
- Buy/Sell Constraints: Single buy quantity is `int(cash balance // buy price)` (rounded down to an integer and at least 100 shares); Full Liquidation
is strictly executed when selling. Commission fees and income tax are not considered during trading.
- Capital Management (Allocation Schemes): Fixed principal mode: Initial principal, no leverage. Buy quantity is dynamically calculated = `(cash
balance // buy price)` (subject to the minimum lot size limit of the Constraints).
- Performance Evaluation (Metrics): Performance evaluation uses the mark-to-market method. Daily return is calculated based on the percentage
change in the total portfolio value. Total value includes the closing market value of held assets and cash balance. Total value at today's close is
`(held quantity * today's closing price + cash balance)`. Annualized return is calculated based on 252 trading days. Empty positions (cash holding
periods) must be taken into account when calculating indicators.
- Look-ahead Bias Control: In daily frequency trading strategies, data such as today's high, low, close, volume, turnover, and percentage change are
only available after the market closes. To avoid look-ahead bias, factor calculations in this strategy strictly use historical data from T-1 and before,
excluding any real-time information from day T, ensuring logic consistency between backtesting and live trading.
- Trading Pricing Standard: Since the timing of the highest and lowest prices is uncertain and can only be confirmed at the close, they are not
actionable in practice. Considering this strategy uses daily frequency data (no intraday information), our strategy's buy and sell pricing standards
rely on these two prices (Open and Close).
````

### G.2 AutoBacktest Agent 提示词

推理阶段涉及三个专化 agent，每个都由精心设计的提示词驱动，处理量化工作流中的特定子任务。

- **Summarizer 提示词（图11）**：该提示词引导 Summarizer agent 分析用户的原始自然语言查询。其主要功能是识别并抽取相关金融指标（如 "5-day Moving Average"）与 Key Performance Indicators（KPIs）的全名。它充当语义解析器，把非结构化文本映射到我们指标库的标准化术语。
- **Retriever 提示词（图12）**：一旦指标被识别，Retriever agent 用该提示词定位所需数据。关键的是，在这一阶段系统把全名及其对应 Short Code（如 SMA(CLOSE, 5)）都注入提示词上下文。这使 LLM 能精确理解需要哪些数据库字段，并构建准确的 SQL 查询以取回底层市场数据。
- **Coder 提示词（图13）**：最后，Coder agent 用该提示词生成可执行的 Python 回测脚本。与 Retriever 类似，该提示词也富含指标 Short Code。通过显式提供这些标准化短代码，我们约束 LLM 使用我们预定义、经过严格测试的计算逻辑，而不是凭空幻觉任意公式。这保证生成的代码不仅语法正确，而且金融上有效、与用户的原始意图一致。

**图11：Summarizer 提示词（Factor Retrieval Prompt，原文第23页）**

````
### Role Definition
You are a Quantitative Factor Analysis Expert. Your task is to analyze a trading strategy description and extract all factor names, and KPI names
mentioned.
### Task Instructions
1. Analyze the user's strategy description carefully.
2. Identify every technical indicator (e.g., moving averages, RSI, volatility) and performance metric (e.g., Sharpe Ratio, Max Drawdown).
3. Standardize & Extract the factor names using the following rules:
   - Full Names: Convert abbreviations to full English names (e.g., use "Rate of Change" instead of "ROC", "Moving Average" instead of "MA").
   - Time Windows: Always put the time window at the beginning (e.g., "20-day", "12-day").
   - Format: Use the format "[Time Period]-[Full Factor Name]" (e.g., "20-day Moving Average").
   - Consistency: If the text mentions a specific parameter (like "ROC6"), extract it as "6-day Rate of Change".
4. Output the result as a strictly valid JSON object containing a single key "factors".
### Output Format Rules
{format_instructions}
### Few-Shot Examples
Example 1
Input:
"We need to determine the optimal threshold value for the volume-based buy condition in the combined strategy for Yunnan Copper listed on the
Shenzhen Stock Exchange. Please conduct a backtest from March 12, 2021, to August 7, 2023, with an initial capital of CNY 4,434,000. The
strategy opens a position only when both of the following conditions are satisfied based on yesterday's (1) yesterday's 6-day Rate of Change
(ROC6) is positive, and (2) the rolling standard deviation of trading volume over the previous ten days up to yesterday exceeds its 20-day moving
average by a factor of the variable threshold. Conversely, the strategy closes the position when both of the following conditions are satisfied
based on yesterday's (1) yesterday's trading volume exceeds its 12-day moving average, and (2) yesterday's 12-day Rate of Change (ROC12) is
negative. The candidate threshold values to be tested are 1.8 and 2.0. Please calculate the Profit/Loss Ratio for each scenario and identify the
threshold value that yields the maximum ratio."
Output:
{"factors": ["6-day Rate of Change", "10-day Standard Deviation of Trading Volume ", "12-day Moving Average of Volume", "12-day Rate of
Change", "Profit Loss Ratio"]}
...
````

**图12：Retriever 提示词（原文第24页）**

````
### Role
You are a Data Engineer and SQL Specialist.
Your ONLY task is to write a simple SQL SELECT query that retrieves the RAW market data required for a backtest.
You are NOT asked to implement the strategy logic in SQL, and you MUST NOT compute indicators in SQL.
### Critical Requirement (Read Carefully)
- Output ONLY the raw data rows needed for downstream backtesting in Python.
- Do NOT calculate indicators (MA/EMA/ROC/MACD/Sharpe/Volatility/etc.) in SQL.
- Do NOT translate entry/exit rules into SQL conditions.
- Do NOT use WITH / CTE / WITH RECURSIVE.
- Do NOT use window functions (OVER, LAG, AVG OVER, STDDEV OVER, etc.).
- Do NOT use ORDER BY: The execution tool AUTOMATICALLY sorts the result by `trade_date` ASC.
- Keep the SQL as a plain data extraction query: SELECT columns FROM one table WHERE filters.
### Database Context & Schema (STRICT VALIDATION)
You have access to a PostgreSQL database with 3 tables: `shanghai_stock_exchange`, `beijing_stock_exchange`, `shenzhen_stock_exchange`
ALLOWED Database Columns (Whitelist):
You can ONLY select columns from this list. If a word is not here, it is NOT a column.
- `trade_date`
······
### Tool Usage & Execution Context
You have access to a tool named `executePostgresQuery`.
- Input: A standard SQL SELECT statement.
- Auto-Processing: The tool will automatically:
  1. Execute your query.
  2. Convert the result into a Pandas DataFrame.
  3. Sort the data by `trade_date` (ascending) automatically.
  4. Generate a text preview.
- Return Value:
  - If `status` is "success": It returns a text preview of the sorted data (first 5 and last 5 rows) and the total row count.
  - If `status` is "error": It returns the specific error message.
- TOOL USAGE LIMIT: You use tools at most 25 times.
### Data Mapping: Short Codes to Database Columns
The user strategy contains formulas with Short Codes. You must map them to the ALLOWED columns.
1. Column Mapping Table (Map these codes to SQL columns):
| Short Code in Formula | Required Database Column |
|-----------------------|--------------------------|
| `OPEN`                | `opening_price`            |
······
2. Ignored Short Codes (NOT Columns):
The following terms represent variables or functions, NOT database columns. Do NOT select them:
- `CASH`, `POSITION`, `PORTFOLIO`
- `DELAY`, `SMA`, `EMA`, `MAX`, `MIN`, `STD`, `MEAN`, `SQRT`, `ABS`, `CUMMAX`
Example Logic:
- If formula is `(CASH + POSITION * CLOSE) / DELAY(PERCENTAGE_CHANGE,1)`:
  - `CASH` -> Ignore.
  - `POSITION` -> Ignore.
······
### Date Range Rule
Strictly use the start and end dates provided in the user's strategy description.
- Do NOT extend the start date backwards.
- Do NOT add any extra buffer.
### Workflow Instructions
1) Identify the correct table based on exchange.
2) Match Company Name Smartly: Use English full names (e.g., 'Shenzhen Anche Technologies').
3) Parse Formulas: Look at the "Factors & Indicators" section. Map Valid Codes -> DB Columns. Ignore Variables (CASH/POSITION).
4) Produce ONE simple SELECT query to fetch these raw columns.
5) Call `executePostgresQuery` to verify.
6) When verified, output ONLY the final JSON.
### Final Output Protocol
Output ONLY a JSON object:
{"sql_statement": "YOUR_VERIFIED_SQL_HERE"}
````

**图13：Coder 提示词（原文第25页）**

````
# Role
You are a quantitative trading strategy backtesting expert specialized in Python and Pandas operations. Your goal is to accurately implement the user's trading strategy, run the
backtest, and return the precise result in JSON format.
# ENVIRONMENT & DATA (CRITICAL)
   - PRE-LOADED DATA: A pandas DataFrame named `df` is ALREADY loaded in your Python environment.
   - NO FILE I/O: DO NOT attempt to read any CSV, JSON, or other files. `pd.read_csv()` will fail.
   - DIRECT ACCESS: You must access `df` directly in your code (e.g., `df.head()`, `df['closing_price']`).
   - DATA ASSUMPTION: Do not consider missing or disordered trading days (assume data is continuous and ordered).
# Data preview:
{dataframe_heads}
# Task Workflow (MUST FOLLOW)
   1. CODE GENERATION:
     - Input Analysis: Read the Strategy Description (Natural Language) and the provided Factors (Short Code format).
     - Indicator Translation: Convert the provided "Short Code" factors into Pandas Series by referencing the "Translation Table".
     - Logic Construction: Translate the natural language rules (e.g., "Buy when SMA > Close") into Python logical conditions using the calculated Pandas indicators.
     - Backtest Loop: Wrap this logic into a backtesting script that strictly adheres to the "Trading Rules" below.
   2. EXECUTE & VERIFY:
     - Run Code: Execute the script using the `python_repl_ast` tool.
     - Validation: Check if the output directly answers the user's specific question (e.g., a specific metric value or stock name).
     - Self-Correction: If the execution fails or yields invalid results (like NaN), debug and re-run within the same turn.
   3. OUTPUT JSON:
     - Extract the final answer from the successful execution.
     - Format the result strictly as a JSON object.
     - DO NOT include any code, explanations, or reasoning in the final response.
# TRADING RULES & PROTOCOLS (STRICT ENFORCEMENT)
### 1. Execution Mechanism (Long-Only)
   - Type: Long-only (no short selling).
   - Alternation: Buy and Sell must strictly alternate. Simultaneous buying and selling in a single trading day is PROHIBITED.
   - Prices:
     - Buy at Opening Price (`Price_open`).
     - Sell at Closing Price (`Price_close`).
   - Last Day Rule: On the final day of the backtest period, DO NOT Buy. If holding a position, force a Full Liquidation at the Closing Price.
### 2. Constraints (Buy & Sell)
   - Buy Quantity (Q): Must be an integer greater than or equal to 100 (e.g., 101 shares are allowed).
   - Sell Quantity: Strict Full Liquidation (sell all shares held).
   - Costs: Transaction fees and income taxes are NOT considered (0 cost).
### 3. Allocation Schemes (Money Management)
   - Mode: Fixed Capital Mode (Initial Capital = `Cash_0`). No leverage.
   - Dynamic Sizing:
     - $Q_t = floor(Cash_t / Price_open_t)$
     - Subject to the minimum size constraint (must be >= 100 shares).
### 4. Look-ahead Bias Control
   - Principle: In daily trading strategies, data such as High, Low, Close, Volume, Amount, and Change are only known after the close.
   - Constraint: Factor calculations MUST strictly use historical data from T-1 day and prior, with ONE exception.
   - Exception: You ARE ALLOWED to use the current day's Opening Price (`Price_open_t`) for signal generation, as it is known at the time of execution.
   - Prohibition: Factor calculations must NOT contain Day T's Close, High, Low, Volume, or Amount.
### 5. Performance Metrics (Mark-to-Market)
   - Method: Daily Mark-to-Market.
   - Daily Return ($r_t$):
     - Formula: $r_t = (PV_t - PV_{{t-1}}) / PV_{{t-1}}$
     - Where $PV_t$ (Portfolio Value) = (Holding Quantity * Close Price_t) + Cash Balance_t.
   - Metric Scope: Metrics must account for periods of empty positions (cash only).
   - Annualized Return: Calculated based on a benchmark of 252 trading days.
   - Risk-Free Rate: Fixed value of 0.0001 (daily).
### 6. Pricing Standard
   - Criterion: Since High and Low prices have uncertain timing and are only confirmed at close, they are not operable. Trading execution is strictly based on Open and Close
prices.
# STRICT CONSTRAINTS
   1. NO GUESSING: You cannot answer questions like "which stock" or "what parameter" without running code to verify data.
   2. SINGLE TOOL CALL: Combine all logic (indicators, signals, backtest loop) into ONE Python block.
   3. PRINT RESULTS: Your Python code MUST `print()` the final result so you can read it.
   4. NO CODE IN ANSWER: The final response must ONLY be the JSON.
   5. TOOL USAGE LIMIT: You use tools at most 25 times.
````

## H 局限

本研究为评估 LLM 在量化金融领域的能力建立了严格的基准，并展示了「code-to-text」逆向工程在对齐自然语言指令与可执行交易逻辑方面的潜力，但当前的数据范围与任务设计仍存在若干局限。

第一，数据集主要关注由日频价格波动驱动的短期择时策略，尚未纳入需要综合多模态信息（如宏观经济指标、公司财务报告或非结构化新闻文本）的长期价值投资策略。

第二，研究目标被严格限定为评估 LLM 在「策略理解—数据检索—代码生成—回测验证」流水线中的能力。因此，模型输出以可行性校验与代码正确性为优化目标，而非为实盘部署生成能够产生 alpha 的投资建议。

第三，受目前仅支持日频市场数据的数据库限制，所有回测模拟都遵循简化的逐日盯市逻辑（「开盘买入、收盘卖出」）。这种做法没有考虑滑点、日内价格路径依赖或高频微观结构细节等真实执行摩擦。

此外，为隔离并严格检验模型的工具使用与代码实现能力，实验设定抽象掉了某些复杂的市场约束。框架不显式建模动态交易费用、变化的税率或随市场状态切换的最小交易单位，也不涉及动态仓位 sizing、均值—方差优化等高级组合管理任务。方法论上，本基准围绕经典的「指标—信号—回测」范式构建；它目前不覆盖基于机器学习模型的策略（如时间序列预测或强化学习），也不覆盖涉及指标加权与集成方法的复杂元策略，主要原因是网格搜索这类高维空间的计算成本高得难以承受。

总之，当前基准作为基础基线，用于在结构化金融环境中测试 LLM 的策略理解与代码生成能力。然而，面向更现实的设定——建模多模态输入、多频率数据与动态市场约束——仍有很大的扩展空间。
