# SPEM：面向 LLM Agent 高效技能利用的结构感知程序性记忆（SPEM: Structure-Aware Procedural Memory for Efficient Skill Use in LLM Agents）

> 来源：https://arxiv.org/abs/2610.26995
> 原文：docs/papers/arXiv-2610.26995.pdf
> 翻译日期：2026-11-03 ｜ 范围：全文（正文全译，参考文献从略） ｜ 方式：机器翻译初稿，未经人工校对
> 引用于：docs/literature/W2-context-memory-distillation.md、docs/brief-plan.md

作者：Ran Zhou、Zehui Kong、Fanyu Lin、Jiaheng Liu、Zhen Zhang、Yuxiang Ren（南京大学智能科学与技术学院）

## 目录

- 摘要
- 引言
- 相关工作
- 方法
  - 双层程序性记忆
  - 基于 Skill-GNN 的结构感知技能选择
  - 轨迹-DAG 提取
- 实验
  - 实验设置
  - 主要结果
  - DAG 模板有效性分析
  - 消融实验
- 结论
- 参考文献（从略）

译注：图表题注均已译出，公式、代码、变量名与指标名保留英文原文，术语首现时括注中文。原 PDF 共 9 页，正文之后即参考文献，无附录；文中多次引用的补充材料（Sections A–D）不在本 PDF 内，故无对应译文。图 1–3 为流程图/统计图，其图内标签在 PDF 文本提取中被打散，译文以题注加「译注」列出主要元素。

## 摘要

基于 LLM 的 agent 越来越依赖可复用的技能（skill）。然而技能库规模一旦扩大，高效而准确地利用技能就变得困难：全量加载技能会造成很高的 token 与运行时开销；扁平的语义检索则把技能当作彼此独立的文本条目，忽略依赖关系、执行顺序、状态转移和数据流约束。为此我们提出 SPEM——一个轻量的结构感知程序性记忆（procedural memory）框架，用于 LLM agent 的高效技能利用。SPEM 为单个技能维护 Atomic Skill Memory（原子技能记忆），并为从成功执行中提炼出的可复用组合维护 Skill-DAG Memory（技能 DAG 记忆）。

面对新任务，若有可用模板，SPEM 直接复用高置信度的 Skill-DAG 模板；否则就检索原子技能，并调用 Skill-GNN 进行状态感知、结构感知的技能选择。成功的执行会被写回为新的 Skill-DAG，使程序性记忆随时间不断积累。在 ALFWorld 和 SkillsBench 上的实验表明，SPEM 取得了最佳的整体效果—效率权衡：ALFWorld 成功率达到 87.1%，SkillsBench 奖励达到 38.38%，同时相比强基线降低了 token 与运行时成本。

## 引言

大型语言模型（LLM）agent 正日益被当作可执行系统使用：它们调用工具、复用技能、与复杂环境交互。在软件工程、数据分析、网页自动化和具身任务中，agent 依赖可复用的技能，例如文件解析、预处理和 API 调用（Schick et al. 2023; Mialon et al. 2023; Yao et al. 2023）。随着技能库扩展到成百上千个候选，核心问题也随之改变：从「是否存在有用技能」变为「agent 能否高效地检索、组织并复用所需技能」（Patil et al. 2023; Qin et al. 2024; Shi et al. 2025）。

在大规模技能库下，现有方法面临四点局限。其一，加载全部技能描述并不可行——token 成本高、上下文膨胀、运行时开销大，而且重要细节常常在长上下文中丢失（Liu et al. 2024a）。其二，扁平检索只优化语义相关性，却忽略了技能之间的结构性依赖，比如前置条件、执行顺序、状态转移和跨技能的数据流（Lewis et al. 2020; Karpukhin et al. 2020）。其三，成功的组合没有被存为可复用的程序性记忆；即便构建了依赖感知的规划，执行完也会被丢弃，迫使 agent 反复重新推导类似的工作流（Yao et al. 2023; Shinn et al. 2023）。

其四，随着 agent 系统部署得越来越频繁、模型能力持续提升，效率成为首要关切。为检索、规划和重组而反复调用模型，带来不必要的 token 消耗、延迟和计算开销。这些局限呼唤这样一个框架：既能紧凑地检索技能，又能以结构化方式组织它们，还能随时间积累可复用的程序性记忆。

为此，我们研究大规模技能库下的高效技能利用，目标是在降低 token 成本、运行时开销和重复技能组织的同时提高任务成功率。我们提出 SPEM，一个轻量的结构感知程序性记忆框架。SPEM 维护两个互补的记忆层：Atomic Skill Memory 用语义、接口和反馈信号表示单个可执行技能；Skill-DAG Memory 存储从成功执行中提炼出的可复用技能组合。给定新任务，SPEM 先检索相关的程序性记忆，若有高置信度的 Skill-DAG 模板就直接复用；否则（或当现有指导不足时），Skill-GNN 会构建任务条件化的候选图，并在检索到的原子技能上做状态感知的技能选择。执行结束后，成功的轨迹被压缩成 Skill-DAG 并写回记忆，供未来复用。

我们在 SkillsBench 和 ALFWorld 上评估 SPEM（Li et al. 2026b; Shridhar et al. 2021）。SkillsBench 考验大规模技能检索与技术任务执行；ALFWorld 考验交互环境中的长程依赖、结构化技能利用和跨任务复用。我们将 SPEM 与全量技能加载、扁平向量检索以及基于图的技能选择基线进行比较。

我们的贡献有四点：

- 提出 SPEM：一个双层程序性记忆框架，把用于细粒度技能访问的 Atomic Skill Memory 与存放可复用程序性结构的 Skill-DAG Memory 结合起来。
- 设计 Skill-GNN 模块，在任务条件化的候选图上进行状态感知的技能选择。
- 提出 trajectory-DAG 提取，把成功执行蒸馏为可复用的 Skill-DAG 模板，并通过执行反馈更新程序性记忆。
- 在 ALFWorld 和 SkillsBench 上评估 SPEM：相比强结构感知基线，取得 87.1% 的 ALFWorld 成功率和 38.38% 的 SkillsBench 奖励，同时降低了 token 与运行时成本。

## 相关工作

**从工具调用到大规模技能检索。** 早期的工具增强语言模型关注工具调用、参数生成以及对返回结果的推理。ReAct、Toolformer 等开创性工作和相关综述通过「推理—行动」交错、自监督学习和系统性分析确立了这一范式（Yao et al. 2023; Schick et al. 2023; Mialon et al. 2023）。当外部能力从几个工具扩展到大型 API 库或技能库时，检索就变得不可或缺。Gorilla、API-Bank、ToolBench、ToolLLM 等方法通过文档检索、embedding、分层搜索、任务定制构建或查询改写来降低上下文开销和调用错误（Patil et al. 2023; Li et al. 2023; Xu et al. 2023; Qin et al. 2024; Hao et al. 2023; Du, Wei, and Zhang 2024; Yuan et al. 2023; Chen et al. 2024）。然而，多数检索方法仍把能力当作彼此独立的文本条目，主要优化语义相关性。技能检索要难得多，因为它涉及程序性知识、执行条件、输入输出约束和任务经验。SkillsBench、SWE-Skills-Bench 等基准表明，过多或不匹配的技能会抬高上下文成本，甚至损害性能（Li et al. 2026b; Han et al. 2026）。因此，大规模技能利用需要的是紧凑、相关、可执行的选择，而不只是语义相似。

**从结构化技能到演进式程序性记忆。** 随着技能成为可复用资产，近期工作开始用显式结构来组织它们。SkillNet 通过统一的本体与关系网络表示技能；AgentSkillOS 通过分类、检索、能力树和动态技能管理来管理技能（Liang et al. 2026; Li et al. 2026a）。基于图的方法进一步建模工具或技能之间的关系：ToolNet 支持在大型工具集合上做图导航；Graph of Skills 从技能依赖图中检索依赖感知的技能组合；GraSP 为长程任务构建带前置条件与效果关系的 DAG 式技能结构（Liu et al. 2024b, 2026; Xia et al. 2026）。这些方法说明显式结构有助于还原依赖与执行关系。但其中多数只是把结构用于当前任务，或作为静态组织层，很少关注成功执行该如何被提炼、更新并作为演进式程序性记忆来复用。SPEM 则把成功轨迹转化为可复用的 Skill-DAG 模板，并通过执行反馈更新其可靠度。

**轻量级技能检索与选择。** 大规模技能利用对上下文、延迟和算力都构成约束，近期工作因此探索轻量级的技能路由、表示与复用。SkillRouter 用紧凑模型在大技能集上做「先召回、再重排」的选择；Formal Skill 用可执行的技能结构取代冗长的 Markdown 描述；CUA-Skill 把 GUI 操作知识封装成可复用技能，支持动态检索与参数实例化（Zheng et al. 2026; Zhang et al. 2026; Chen et al. 2026）。另一些方法强调可复用经验：ProcMEM 把交互经验转化为程序性记忆；SkillDAG 维护技能间的带类型关系并跨 episode 演化；Compositional Skill Routing 为分解后的子任务检索技能，并用依赖感知的 DAG 规划器加以组合（Mi et al. 2026; Bai et al. 2026; Gao 2026）。这些研究表明，轻量级技能利用不只是减少检索到的技能，而是同时关乎紧凑表示、高效选择、执行约束与经验复用。SPEM 通过统一的程序性记忆框架来填补这一空白：它结合有界的原子检索、可复用的 Skill-DAG Memory 和 Skill-GNN 组织。

## 方法

给定一个任务请求和大规模技能库，SPEM 通过两个记忆层提供紧凑、可执行的技能指导：Atomic Skill Memory 负责单个技能，Skill-DAG Memory 负责从成功执行中提炼出的可复用组合。如图 1 所示，若有匹配的 Skill-DAG 模板，SPEM 直接复用；否则检索原子技能，并在需要时调用 Skill-GNN 做状态感知的重排。成功的执行会作为新的 Skill-DAG 写回，使程序性记忆得以不断积累。完整协议见补充材料 Section A.1。

### 双层程序性记忆

SPEM 把程序性知识拆成两个互补的记忆层：Atomic Skill Memory 支持对单个技能的细粒度访问，Skill-DAG Memory 支持对成功技能组合的直接复用。完整的 schema 与更新规则见补充材料 Section A.2。

**原子技能记忆（Atomic Skill Memory）。** Atomic Skill Memory 把每个技能表示为一个可复用的执行单元，而不是孤立的文本片段。记作

$$M_a = \{s_i\}_{i=1}^{N} \tag{1}$$

其中每个技能表示为

$$s_i = (d_i, e_i, \sigma_i). \tag{2}$$

$d_i$ 是技能元数据，$e_i$ 是语义 embedding，$\sigma_i$ 是轻量的执行反馈，例如使用频率、成功率和执行成本。这样，检索可以同时考虑语义相关性和历史执行证据，而不必把整个技能库加载进 LLM 上下文。

**Skill-DAG 记忆（Skill-DAG Memory）。** Skill-DAG Memory 存储从成功执行中提取的可复用程序性模板，记作

$$M_d = \{G_j\}_{j=1}^{M} \tag{3}$$

每个 Skill-DAG 表示为

$$G_j = (V_j, E_j, e_j, m_j). \tag{4}$$

$V_j$ 是程序性节点，$E_j$ 是有向依赖边，$e_j$ 是与该模板关联的任务 embedding，$m_j$ 存储紧凑的执行元数据。一个 Skill-DAG 刻画了一种可复用的执行结构，让 agent 直接复用过去成功的流程，而不必从零重构。

**程序性记忆检索（Procedural Memory Retrieval）。** 给定任务请求 $q$，SPEM 先在 Skill-DAG Memory 中搜索可复用模板：

$$C_d(q) = \{G_j \in M_d \mid \mathrm{sim}(e_q, e_j) \ge \tau\} \tag{5}$$

$e_q$ 是任务 embedding，$\tau$ 是模板匹配阈值。若 $C_d(q)$ 非空，得分最高的 Skill-DAG 会作为结构化程序性指导被注入。若没有模板达到阈值，SPEM 就检索一组有界的原子候选：

$$C_a(q) = \mathrm{TopK}_{s_i \in M_a} \mathrm{sim}(e_q, e_i) \tag{6}$$

随后，当需要结构化组织时，检索到的模板或原子候选会被送入后续的 Skill-GNN 编排阶段。这一检索策略既避免了全库加载，又保留了两种互补的复用方式：直接复用成功的 Skill-DAG 模板，以及针对新颖任务状态灵活组织原子技能。

（原文位置：docs/papers/arXiv-2610.26995.pdf 第 3 页）

**图 1：SPEM 总览。** 系统从双层程序性记忆中检索原子技能或匹配的 Skill-DAG 模板，构建任务条件化的候选技能图，并用 Skill-GNN 为 LLM 执行器生成紧凑的指导。成功的轨迹会被蒸馏回可复用的 Skill-DAG 记忆。

译注（图内主要元素）：上排流程为「检索与模板匹配 → 候选技能图构建 → Skill-GNN 指导 → LLM Agent/执行器」；模板命中（Hit!）即注入结构化技能指导，未命中（No Hit）或执行失败（Fail）则走原子技能检索（Atomic Skill Retrieval）与候选技能子图；下排为双层程序性记忆——Atomic Skill Memory 存储单个技能（Skill Embeddings、Usage、Success Rate、Description），Skill-DAG Memory 存储可复用的结构化工作流（Validated Reusable Workflows、Dependency Structure、Procedural Template）；右侧为轨迹提取（1. Action A 至 6. Action F）经环境反馈（Environment Feedback）后回写更新（Update）。

### 基于 Skill-GNN 的结构感知技能选择

当可复用模板缺失、或不足以覆盖当前执行上下文时，SPEM 用 Skill-GNN 对检索到的原子候选做结构感知的排序与选择。目标不只是找出语义相关的技能，还要选出与任务状态相容、且候选之间依赖关系合理的技能。

**候选技能图构建（Candidate Skill Graph Construction）。** 给定任务请求 $q$、检索到的原子候选 $C_a(q)$ 和当前执行上下文，SPEM 构建任务条件化的候选图

$$G_q = (V_q, E_q, R) \tag{7}$$

$V_q$ 包含任务、上下文和候选技能节点，$E_q$ 包含带类型的边，$R$ 表示关系类型。技能节点的特征把语义 embedding 与轻量执行反馈结合起来；任务节点和上下文节点编码请求、当前状态与执行历史；边连接任务–技能、上下文–技能、技能–技能这几类节点对，刻画相关性、状态相容性、语义关联以及可用的依赖线索。更多构建细节见补充材料 Section A.5。

**Skill-GNN 打分（Skill-GNN Scoring）。** 给定 $G_q$，Skill-GNN 先通过消息传递做节点编码和关系感知推理（见图 1）。设 $h_i^{(0)}$ 为节点 $i$ 的初始表示，在第 $\ell$ 层，节点表示由来自各关系特定邻居的消息聚合更新：

$$h_i^{(\ell+1)} = \phi_\ell \Big( h_i^{(\ell)}, \sum_{r \in R} \sum_{j \in N_r(i)} \alpha_{ij}^{r(\ell)} W_r^{(\ell)} h_j^{(\ell)} \Big) \tag{8}$$

其中 $N_r(i)$ 表示关系类型 $r$ 下节点 $i$ 的邻居，$W_r$ 是关系特定的变换，$\alpha_{ij}^{r(\ell)}$ 是消息权重，$\phi_\ell$ 是该层的更新函数。经过 $L$ 层消息传递后，Skill-GNN 对技能打分：为每个候选技能 $s_i \in C_a(q)$ 赋予一个依赖上下文的效用分

$$p_i = f_\theta \big( h_i^{(L)} \big). \tag{9}$$

排名靠前的技能（在可用时连同紧凑的依赖线索）会被作为结构化指导注入 LLM agent。这种基于图的打分把任务相关性、运行时状态和技能间依赖一并纳入技能选择过程。

**冷启动部署（Cold-Start Deployment）。** SPEM 同时支持轨迹充足和轨迹稀缺两种部署场景。当目标领域有轨迹时，Skill-GNN 以轨迹前缀监督训练：每个前缀定义当前的程序性状态，其后实际执行的技能作为训练目标。当轨迹稀缺或缺失时，SPEM 仅用技能库本身做库级热启动：

$$D_{e_0} = \{(\tilde{q}_i, s_i)\}_{s_i \in M_a}, \tag{10}$$

$$E_{e_0} = \{(s_i, r, s_j) \mid \kappa_r(s_i, s_j) \ge \eta_r\}, \tag{11}$$

其中 $\tilde{q}_i$ 是由技能 $s_i$ 元数据生成的伪查询，$E_{e_0}$ 包含由语义相似度、共享工具、标签或 schema 兼容性诱导出的弱技能–技能关系。这一初始化不使用任何任务结果、验证器奖励或评测轨迹。部署初期，Atomic Skill Memory 的检索和可用的 Skill-DAG 模板提供主要指导，热启动的 Skill-GNN 只用于有界的重排。随着成功执行不断积累，trajectory-DAG 提取会把它们转化为新的 Skill-DAG 模板和轨迹前缀训练样本，使系统逐渐从纯检索指导过渡到状态感知的图选择。由于 Skill-GNN 对动态构建的候选图是归纳式（inductive）的，它可以泛化到未见任务、未见技能组合以及新提取的 Skill-DAG 变体。更多协议与防泄漏细节见补充材料 Section A.4。

### 轨迹-DAG 提取（Trajectory-DAG Extraction）

如图 2 所示，SPEM 在执行结束后把成功的交互轨迹转化为可复用的 Skill-DAG 模板。完整轨迹可能包含失败尝试、冗余探索和环境特有细节，因此系统不存储完整轨迹，而是提取一条紧凑的执行骨干（backbone）——它保留了到达成功状态所必需的步骤。给定执行轨迹 $\tau$，系统先构建执行图

$$G_\tau = (V_\tau, E_\tau) \tag{12}$$

节点表示已执行的步骤和与任务相关的状态；边编码时间顺序、实体依赖、状态转移和终止可达性。从成功的终止节点 $v_{succ}$ 出发，系统做反向切片（backward slicing）以识别与成功相关的节点：

$$V_\tau^* = \{v \in V_\tau \mid v \to^* v_{succ}\} \tag{13}$$

$v \to^* v_{succ}$ 表示 $v$ 能经由时间或依赖路径到达成功终止状态。失败分支、冗余探索以及对最终结果没有贡献的操作都被移除；剩下的节点及其诱导出的依赖边按时间和依赖约束排序并修复，形成紧凑的 Skill-DAG：

$$G_\tau^* = (V_\tau^*, E_\tau^*). \tag{14}$$

最后，$G_\tau^*$ 被写回 Skill-DAG Memory 供未来复用：成功的非模板执行引入新模板；成功的模板引导执行会强化或精化既有模板；失败的模板执行只更新可靠度统计。详细的提取规则、打分信号和更新策略见补充材料 Section A.3。

（原文位置：docs/papers/arXiv-2610.26995.pdf 第 5 页）

**图 2：trajectory-DAG 提取总览。** 成功轨迹先被转换为执行图，再通过反向切片、剪枝和依赖修复识别出必要步骤；得到的骨干被存储为可复用的 Skill-DAG 模板，供未来任务使用。

译注（图内主要元素）：左侧为执行轨迹 → 构建执行图（任务节点、步骤节点、时间边、实体节点、实体依赖边、终止目标、成功节点）；中间为必要骨干提取（成功过滤 Success Filter、反向切片 Backward Slicing、剪除无关探索 Prune irrelevant exploration、排序与依赖修复 Sort & Repair），失败轨迹被丢弃；右侧产出「可复用的成功模板」进入 Skill-DAG Library；底部为模板指导——命中模板时直接提供给 agent，未找到高置信模板时改用 GNN。

## 实验

### 实验设置

**基准（Benchmarks）。** 我们在两个互补的技能利用基准上评估 SPEM。ALFWorld（Shridhar et al. 2021）是一个交互式文本具身环境，要求完成多步家务任务，考验长程依赖、状态转移和程序性复用。SkillsBench（Li et al. 2026b）用大型技能库评估技术型 agent 任务，检验 agent 能否在有限的上下文预算内检索并应用与任务相关的技能。

**指标（Metrics）。** ALFWorld 上报告 Success（↑）、Steps（↓）、Tokens（↓）和 Runtime（↓）：Success 是最大步数预算内的任务成功率；Steps 是平均环境交互次数；Tokens 是 agent 执行期间的平均 token 消耗；Runtime 是仅计算 agent 的平均执行时间。

SkillsBench 上报告验证器奖励 R（↑）、平均输入 token 数 T（↓）和仅 agent 运行时 S（↓）。按照基准协议，R 由官方验证器给出。为公平计账，S 只衡量 agent 执行阶段，不含环境搭建、依赖安装、Docker 构建和验证器运行时间；SPEM 在执行过程中触发的在线技能检索或重排也计入所测的 agent 阶段。

**基线（Baselines）。** 我们与四个基线比较，它们在技能访问方式和结构感知程度上构成一组受控递进。Vanilla Skills 加载完整技能库，检验「只靠穷举上下文」是否足够；Vector Skills 按 embedding 相似度检索 top-k 技能，以隔离扁平语义检索的效果；GoS 作为静态图检索方法的代表，用预构建的技能图检索结构上相关的技能；SkillDAG 作为近期 sota 基线，以自演化图结构做依赖感知的技能选择。SPEM（Ours）进一步引入双层程序性记忆、trajectory-DAG 提取和按需 Skill-GNN 重排。这组基线使我们能够区分收益的来源：更多上下文、语义检索、静态图结构、带类型的图选择，还是可复用的程序性记忆。

**实现细节（Implementation Details）。** 为公平比较，所有方法使用相同的基准划分、技能库、agent 接口、执行环境和验证协议。我们用两个 backbone LLM 评估：MiniMax-M2.7（MiniMax 2026）和 GPT-5.2-Codex（OpenAI 2025），分别代表较弱和较强的模型设置。

ALFWorld 上，我们使用含 140 个 episode 的 dev 划分，环境最大步数设为 30。所有基于技能的方法都使用同一个含 37 个 alfworld-* 技能的库：SPEM 从该库构建 Atomic Skill Memory，只用成功的非评测轨迹构建 Skill-DAG Memory，并在训练与评测实例互不重叠的条件下用轨迹前缀监督训练 Skill-GNN。

SkillsBench 上，我们沿用 GoS 的执行设置：基于 Docker 的环境、Harbor agent 执行、基于验证器的评估、每任务最多两次尝试、两个并发试验。按照基准惯例，因基础设施故障在允许的重试后仍无法解决的任务被排除，而不计为模型失败，因此所有方法都使用同样 67 个有效模型任务。所有方法使用同一个 skills_200 技能库；SPEM 从同一库构建 Atomic Skill Memory，并采用库级热启动加 Skill-GNN 重排。详细超参数、防泄漏规则、重试处理和更多推理细节见补充材料 Section B。

### 主要结果

**整体效果—效率权衡。** 表 1 显示，SPEM 在两个基准、两种 backbone 上都取得了最好的整体权衡。ALFWorld 上，SPEM 在 MiniMax-M2.7 和 GPT-5.2-Codex 下都取得最高成功率，分别比 GoS 高 2.1 和 1.8 个百分点，同时运行时也最低。SkillsBench 上，SPEM 在 GPT-5.2-Codex 下取得最佳奖励，在 MiniMax-M2.7 下排第二——后一组中 SkillDAG 奖励更高，但 token 和运行时开销大得多。特别是与 MiniMax-M2.7 下的 SkillDAG 相比，SPEM 把输入 token 降低了 26.3%、运行时降低了 24.3%，而奖励仍具竞争力。

**模型越强，效率越重要。** 随着 backbone 变强，GoS、SkillDAG 这类结构感知基线也能拿到有竞争力的奖励，在 SkillsBench 上尤其如此。这使效率成为关键的区分因素，而不再是次要指标。GPT-5.2-Codex 下，SPEM 把 SkillsBench 奖励从 GoS 的 37.50% 提升到 38.38%，同时输入 token 减少 15.7%、运行时减少 12.3%。ALFWorld 上 SkillDAG 用的步数更少，但 token 和运行时成本高得多；SPEM 则以低得多的执行开销保持最高成功率。这说明可复用的程序性记忆只有在提供紧凑指导时才最有价值，而不是靠更长的规划或更大的上下文。

**结构为何重要。** Vector Skills、GoS、SkillDAG 与 SPEM 的对比澄清了结构的作用。Vector Skills 通常能缩小上下文，却可能丢掉重要的程序性依赖，导致奖励或成功率下降。GoS 和 SkillDAG 表明显式技能结构能改善任务表现，但它们主要依赖静态或预构建的结构，可能引入额外的上下文或执行开销。SPEM 进一步把 Atomic Skill Memory、可复用的 Skill-DAG Memory 与状态感知的 Skill-GNN 重排结合起来，让 agent 在保持注入指导紧凑的同时复用成功的程序性结构。这些结果说明，SPEM 的主要优势不在于检索到更多技能，而在于有限的 token 和运行时预算下选择并复用结构化的程序性指导。SPEM 的详细案例分析见补充材料 Section D。

**表 1：不同 backbone 模型下 SkillsBench 与 ALFWorld 的主要结果。** SkillsBench 中 R 为验证器奖励，T 为平均输入 token 数，S 为仅 agent 的运行时（秒）；ALFWorld 中 Success 为任务成功率，Steps、Tokens、Runtime 分别为平均环境步数、平均 token 消耗和仅 agent 运行时。↑ 表示越高越好，↓ 表示越低越好。**加粗**为各 backbone 分组内、每个基准下的最优结果（原文另以下划线标注次优结果，此处从略）。

| Backbone | 方法 | ALFWorld Success↑ | Steps↓ | Tokens↓ | Runtime↓ | SkillsBench R↑ | T↓ | S↓ |
|---|---|---|---|---|---|---|---|---|
| MiniMax-M2.7 | Vanilla Skills | 59.3 | 21.24 | 152,242.1 | 55.95s | 21.61 | 798,323 | 469.3 |
| MiniMax-M2.7 | Vector Skills | 63.9 | 18.36 | 55,816.6 | 55.71s | 13.07 | 722,765 | 439.5 |
| MiniMax-M2.7 | GoS | 68.6 | 20.26 | 62,033.9 | 54.22s | 23.50 | 735,113 | 399.4 |
| MiniMax-M2.7 | SkillDAG | 63.3 | **16.37** | 296,512.4 | 137.38s | **27.09** | 979,781 | 476.1 |
| MiniMax-M2.7 | SPEM (Ours) | **70.7** | 18.29 | **45,785.7** | **51.56s** | 25.14 | **721,926** | **360.5** |
| GPT-5.2-Codex | Vanilla Skills | 84.9 | 14.65 | 99,023.9 | 84.57s | 28.87 | 2,785,485 | 686.8 |
| GPT-5.2-Codex | Vector Skills | 83.7 | 16.18 | **47,357.3** | 80.43s | 23.44 | 1,047,698 | 763.4 |
| GPT-5.2-Codex | GoS | 85.3 | 16.46 | 48,805.6 | 71.23s | 37.50 | 1,162,375 | 705.2 |
| GPT-5.2-Codex | SkillDAG | 85.7 | **11.73** | 105,449.9 | 169.10s | 34.38 | 1,370,270 | 861.1 |
| GPT-5.2-Codex | SPEM (Ours) | **87.1** | 15.07 | 47,409.1 | **66.01s** | **38.38** | **980,029** | **618.7** |

### DAG 模板有效性分析

我们分析提取出的 Skill-DAG 是否既紧凑又有用。如图 3(a) 所示，trajectory-DAG 提取把成功轨迹从平均 13.4 步压缩到 6.0 步的骨干，剪掉 54.9% 的操作，同时保留可执行的核心。这初步证明了 DAG 模板的压缩效果。

接着评估 DAG 模板的可用性与有效性。如表 2 所示，ALFWorld 上 SPEM 在 MiniMax-M2.7 和 GPT-5.2-Codex 下的模板命中率分别为 56.43% 和 60.71%；在命中的任务中，成功率分别为 74.68% 和 85.88%。这些结果表明，DAG 模板能够为后续任务积累可复用的程序性结构。

与 ALFWorld 不同，SkillsBench 的技术任务高度异质，精确的程序性模板复用天然受限。因此我们主要用 SkillsBench 评估大规模原子技能检索与结构感知重排，而用 ALFWorld 分析 Skill-DAG 模板复用。

最后，我们在 ALFWorld 上做了一次精确模板分析，以隔离「正确的 DAG 骨架本身」的作用：对每个成功完成的任务，提取其轨迹，并在重新执行该任务时直接提供该 DAG。这一设置检验 DAG 模板能否提高执行效率。如图 3(b) 所示，精确 DAG 指导在所有评测任务上都保持了成功率，同时把平均步数从 11.42 降到 6.26、token 消耗从 23.77K 降到 11.93K、运行时从 28.01s 降到 20.88s，降幅分别为 45.2%、49.8% 和 25.5%。这说明模板能为提升任务效率提供有效的程序性指导。

**表 2：ALFWorld 上的模板可用性分析。所有数值均为百分比。**

| Backbone | Hit | Fallback | Ineffective Hit | Success |
|---|---|---|---|---|
| MiniMax-M2.7 | 56.43 | 43.57 | 25.32 | 74.68 |
| GPT-5.2-Codex | 60.71 | 39.29 | 14.12 | 85.88 |

（原文位置：docs/papers/arXiv-2610.26995.pdf 第 7 页）

**图 3：有效性与可扩展性分析。** (a) trajectory-DAG 提取把成功轨迹压缩为紧凑的 DAG 骨干；(b) 精确 DAG 模板复用降低归一化执行成本；(c) 不同技能库规模下的 Hit@K；(d) 不同技能库规模下的 Recall@K 与 MRR。实线表示基于 GNN 的重排，虚线表示纯检索选择。

译注（图内主要元素）：(a) 柱状对比原始轨迹、被剪除步骤与 DAG 骨干的平均步数和归一化成本（100% → 约 50%）；(b) 精确 DAG 模板 vs 纯检索的三项对比——Steps 6.26 vs 11.42、Tokens 11.93K vs 23.77K、Runtime 20.88s vs 28.01s；(c)(d) 横轴为技能库规模 37 / 200 / 500 / 1000 / 2000。

### 消融实验

**SPEM 组件分析。** 表 3 在 ALFWorld 上评估 SPEM 各个组件的贡献。

**表 3：SPEM 在 ALFWorld 上的组件消融。** Succ.、Steps、Time、Tokens 分别为任务成功率、平均完成步数、平均运行时和平均 token 消耗。† 表示移除基于图的 Skill-GNN，改为使用检索到的程序性记忆。

| 方法变体 | Succ.↑ | Steps↓ | Time↓ | Tokens↓ |
|---|---|---|---|---|
| w/o Skill-DAG | 56.8 | 23.0 | 55.4 | 67.5K |
| w/o Skill-GNN† | 58.3 | 20.3 | 54.7 | 53.6K |
| w/o DAG Extraction | 63.0 | 18.9 | 57.8 | 56.2K |
| Full SPEM | 70.7 | 18.3 | 51.6 | 45.8K |

- Skill-DAG 模板提供可复用的程序性指导。去掉它们，成功率降到 56.8%，平均步数升到 23.0，说明出现了更多冗余探索。
- Skill-GNN 支持状态感知的技能选择：没有基于图的打分，成功率跌到 58.3%，说明在任务状态不断变化时，仅靠检索到的记忆不足以稳定执行。
- DAG 提取让程序性记忆保持紧凑。用完整执行轨迹替换提取出的 Skill-DAG 骨架，成功率降到 63.0%，token 和运行时成本也上升，因为完整轨迹包含冗余探索和环境特有细节。
- 完整的 SPEM 在所有指标上都取得最佳结果。这证明可复用的 Skill-DAG 模板、结构感知的技能选择和紧凑的轨迹提取是互补的。

**更大技能库上的可扩展性。** 图 3(c)、(d) 进一步考察技能库增长时结构感知技能选择是否依然有效。纯检索选择在库规模变大时迅速退化，尤其在 1000 和 2000 个技能时，仅靠语义相似度很难把所需技能排到前列。相比之下，Skill-GNN 在所有库规模下都稳定取得更高的 Hit@K、Recall@K 和 MRR：例如在 2000 个技能时，Skill-GNN 把 Hit@1 从 0.0 提升到 0.51、MRR 从 0.112 提升到 0.573。尽管随着候选池扩大两种方法都更难排序，差距依然显著，说明基于图的上下文化有助于在大规模技能库下保持可靠的技能选择。

更多 backbone 对比和超参数敏感性分析见补充材料 Section C。

## 结论

我们提出了 SPEM——一个面向 LLM agent 的可复用、结构感知的技能记忆框架。SPEM 不再把技能当作扁平的提示词集合，而是把它们组织为表示单个能力的 Atomic Skill Memory 和存放可复用程序性结构的 Skill-DAG Memory。Skill-GNN 进一步在动态构建的候选图上做状态条件化的技能选择，让 agent 在执行过程中调整指导，同时对新任务和新技能组合保持归纳泛化能力。在 ALFWorld 和 SkillsBench 上的实验表明，在较弱和较强的 backbone 模型下，SPEM 都同时改善了任务效果与执行效率。结果说明，有效的技能利用不止于语义检索：agent 需要紧凑的程序性指导，它既要说明哪些技能相关，也要说明这些技能应如何组合。尽管当前性能仍依赖检索质量和 agent 执行所检索指导的能力，SPEM 为构建可扩展、可自适应、可复用的 LLM agent 技能记忆迈出了务实的一步。

## 参考文献（从略）

参考文献从略，见原文。
