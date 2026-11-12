# HALO：面向多智能体 LLM 系统的分层自主逻辑导向编排（HALO: Hierarchical Autonomous Logic-Oriented Orchestration for Multi-Agent LLM Systems）

> 来源：https://arxiv.org/abs/2505.13516
> 原文：docs/papers/arXiv-2505.13516.pdf
> 翻译日期：2026-11-11 ｜ 范围：全文 ｜ 方式：机器翻译初稿，未经人工校对
> 引用于：docs/literature/W3-backtest-reliability.md

**作者**：Zhipeng Hou、Junyi Tang（南京邮电大学），Yipeng Wang（重庆大学）；\* 第一作者兼通讯作者，联系邮箱 japhonehou@gmail.com。arXiv:2505.13516v1 [cs.MA]，2025 年 5 月 17 日。

## 目录

- 摘要
- 1 引言
- 2 相关工作
  - 2.1 提示优化
  - 2.2 基于 LLM 架构中的角色设计
  - 2.3 合作优化策略
- 3 HALO 框架
  - 3.1 问题形式化
  - 3.2 自适应提示精炼
  - 3.3 分层推理栈
  - 3.4 工作流搜索引擎
- 4 实验
  - 4.1 实验设置
  - 4.2 主要结果
  - 4.3 消融实验
- 5 结论
- 致谢
- 参考文献
- 附录 A 自适应提示精炼的系统提示
- 附录 B 规划智能体与工作流搜索引擎的系统提示
- 附录 C 中层角色设计智能体的系统提示
- 附录 D 实验所用提示

## 摘要

近年来，由大语言模型（Large Language Models，LLM）驱动的多智能体系统（Multi-Agent Systems，MAS）在多样化的任务场景中展现出巨大潜力。然而，现有智能体系统通常依赖预定义的智能体角色设计空间与静态通信结构，限制了其在复杂交互环境中的适应性与灵活性，导致在高度专业化与专家级任务上表现欠佳。为解决这些问题，我们提出 HALO——一个基于分层推理架构的多智能体协作框架。具体而言，我们引入了用于任务分解的高层规划智能体、用于面向子任务的智能体实例化的中层角色设计智能体，以及用于子任务执行的底层推理智能体。特别是，子任务执行被重新表述为一个结构化的工作流搜索问题，蒙特卡洛树搜索（Monte Carlo Tree Search，MCTS）在其中系统地探索智能体动作空间，以构建最优推理轨迹。此外，由于大多数用户缺乏提示工程（prompt engineering）方面的专业知识，我们利用自适应提示精炼（Adaptive Prompt Refinement）模块将原始查询转化为面向任务的提示。在代码生成（HumanEval）、通用推理（MMLU）与算术推理（MATH）基准数据集上的实证评估凸显了 HALO 的有效性，其相比最先进的基线平均提升 14.4%。值得注意的是，HALO 在 MMLU 基准的 Moral Scenarios 学科上最高取得 13.3% 的性能提升，在 MATH 基准的 Algebra 子领域上最高取得 19.6% 的性能提升，表明其在处理高度专业化与专家级任务上具备先进水平。代码仓库地址为 https://github.com/23japhone/HALO。

## 1 引言

大语言模型（LLM），如 OpenAI o3 [1] 与 Deepseek R1 [2]，已在语言理解与推理方面展现出卓越能力。这些进展为基于 LLM 的多智能体系统解锁了巨大潜力，使其能够应对广泛的下游任务，包括代码生成 [3, 4]、移动设备控制 [5, 6]、视频游戏 [7] 与开放域问答 [8, 9]。因此，构建有效的智能体系统对于在多样化下游应用中充分发掘 LLM 的能力至关重要。

图1：HALO 框架总览。HALO 由三个模块组成：（1）自适应提示精炼（第 3.2 节），将用户查询精炼为高质量、LLM 可理解的提示；（2）分层推理栈（第 3.3 节），负责任务分解、角色实例化与子任务执行；（3）工作流搜索引擎（第 3.4 节），探索多智能体协作并构建最优工作流。绿色路径表示最优推理轨迹，红色路径则在搜索过程中被剪枝（原文第2页）。

然而，现有智能体系统往往难以在复杂交互环境与专家级任务中保持稳健的性能。这一局限源于预定义的智能体角色设计空间 [5, 10] 与静态通信工作流 [11, 12]，它们高度依赖专家洞察与人工设计的策略。与此同时，由于大多数用户缺乏提示工程专业知识，表述不佳的查询严重阻碍了智能体的理解，最终导致低效的任务执行。这些挑战共同凸显了两个根本问题：（1）智能体系统如何在陌生环境中以最少的人工干预实现自组织与协调；（2）如何精炼用户查询以提升多智能体协作的整体效率与有效性。

作为回应，我们提出 HALO，一个面向复杂交互环境与专家领域推理任务的分层自主逻辑导向编排（Hierarchical Autonomous Logic-Oriented Orchestration）框架。为此，HALO 引入了可扩展的智能体角色实例化机制与动态通信架构，以取代预定义角色空间与静态工作流的僵化性。此外，HALO 采用提示工程模块对用户查询进行精炼。HALO 的总览如图 1 所示。

具体而言，HALO 以三阶段范式运行。第一阶段是自适应提示精炼（详见第 3.2 节），将原始用户查询转化为高质量、LLM 可理解的提示。该模块由四个协作智能体组成，负责提示精炼的不同阶段，从查询解析一直到最终综合。第二阶段是分层推理栈（详见第 3.3 节），采用三层多智能体协作架构：顶层的高层规划智能体将整体任务分解为一系列子任务；中层的角色设计智能体依据每个子任务的需求动态实例化专用智能体；底层的推理智能体则通过协作机制负责执行每个子任务。第三阶段是工作流搜索引擎（详见第 3.4 节），探索底层推理智能体之间的协作并构建最优工作流。

我们将子任务执行重新表述为一个工作流搜索过程，由蒙特卡洛树搜索（MCTS）[13] 引导对动作空间的探索。搜索树中的每个节点对应一个智能体生成的响应或一个中间推理步骤，而边表示推理状态之间可能的转移。这些节点与边共同构成一条路径，代表每个子任务的一个候选推理轨迹。

大量实验（详见第 4.2 节）表明，HALO 在代码生成（HumanEval）[14]、通用推理（MMLU）[15] 与算术推理（MATH）[16] 基准上优于强力基线，平均提升 14.4%。值得注意的是，HALO 在 MMLU 的 Moral Scenarios 学科上最高取得 13.3% 的性能提升，在 MATH 的 Algebra 子领域上最高取得 19.6% 的性能提升，凸显了其在高度专业化与专家级任务上的先进水平。

本工作的主要贡献如下：

- 我们提出了一个名为 HALO 的新颖框架，以三个阶段实现面向任务的智能体协作，显著超越了专家洞察与人工设计策略的局限。
- 在三个不同任务上的实验表明，我们的方法优于最先进的基线，证实了 HALO 在复杂交互环境与专家领域推理任务中的有效性与适应性。

## 2 相关工作

### 2.1 提示优化

提示设计是 LLM 智能体理解指令与协调行动的基础。近期工作将这一过程自动化，以减少人工干预并提升模块化程度。Promptor [17] 将目标分解为结构化的、面向特定角色的提示，使智能体能够专注于各自的任务。CAMEL [12] 集成了一个任务规划智能体来生成角色提示，通过指令驱动的模拟引导多智能体交互。尽管这些方法提升了模块化与任务分解能力，当前智能体系统仍依赖手工制作的提示模板或面向特定任务的工程处理，这限制了其跨领域泛化能力。ComfyAgent [18] 等近期框架开始将提示生成纳入不断演化的工作流之中。尽管如此，如何设计既可复用、又能响应运行时上下文变化的提示，在很大程度上仍是一个开放问题，尤其是在智能体角色或任务目标并非预定义的场景中。

### 2.2 基于 LLM 架构中的角色设计

角色设计已成为近期多智能体架构的核心主题。人工角色分配是组织智能体行为的常见策略。例如，MetaGPT [19] 将智能体与真实世界的职位对齐，并通过标准操作规程约束其行为。这种静态角色配置提供了清晰性与可复现性，在定义良好的领域尤其如此。然而，固定角色在开放式或动态场景中往往难以为继——在这些场景中，智能体的职责必须随任务变化而演进。为此，较新的框架引入了角色生成机制，允许智能体动态地创建、调整或继承角色。TPTU [20] 与 DyLAN [21] 采用分层或层级结构，使智能体能够在协作推进过程中委派、转换或细化职责。这些方法标志着向更高灵活性的转变，尽管现有智能体系统仍在部分预定义的边界内运行。

### 2.3 合作优化策略

随着基于 LLM 的多智能体系统规模与复杂度不断增长，优化智能体之间的协作变得愈发关键。总体而言，当前系统采用集中式或去中心化范式。集中式框架如 AgentLaboratory [22]、ScoreFlow [23] 与 WORKFLOW-LLM [24]，依赖控制智能体来管理调度、通信与输出聚合。这类架构提供了清晰的监管能力，但在实时或异步场景中可能遭遇可扩展性问题并成为瓶颈。相比之下，去中心化方法试图将控制与决策分布到各个智能体：一些采用点对点通信或基于身份的协议 [25]，另一些则采用博弈论协商 [26]。这些设计在非结构化环境中提供了更高的自主性与鲁棒性。最近，若干框架将合作重构为一个结构化搜索过程。例如，AFlow [27] 通过动态图遍历探索分层任务工作流，而非依赖固定的执行路径。这类方法使智能体能够基于特定任务的信号或对等响应自适应地构建交互计划，为构建更具上下文敏感度的智能体团队指出了一个有前景的方向。值得注意的是，一些研究将强化学习应用于优化合作策略 [28–32]。

表 1 给出了这些合作框架在五个维度上的对比总结。与之相比，HALO 引入了分层推理架构，并将子任务执行重构为结构化推理搜索。这一设计在模块化协调与动态适应性之间提供了平衡的路径，尤其适用于复杂交互环境。

表1：HALO 与现有代表性基于 LLM 的多智能体框架在五个关键维度上的对比分析。

| 方法 | 结构 | 多角色支持 | 角色分配 | 动态结构 | 团队优化 |
| --- | --- | --- | --- | --- | --- |
| ScoreFlow [23] | Central + Score-based | ✗ | ✗ | ✗ | ✓ |
| CAMEL [12] | Feedback Triplet | Manual | Manual | ✗ | ✗ |
| AgentVerse [33] | Hierarchical Tree | ✓ | Generated | ✗ | ✗ |
| MetaGPT [19] | SOP-guided Workflow | ✓ | Manual | ✗ | ✗ |
| DyLAN [21] | DAG + Feedback Loop | ✓ | Manual + Gen | ✓ | ✓ |
| ComfyAgent [18] | Modular Workflow | ✓ | Generated | ✓ | ✗ |
| AgentLaboratory [22] | Centralized Scheduler | ✓ | Manual | ✗ | ✓ |
| TPTU [20] | Hierarchical Planner | ✓ | Manual + Gen | ✓ | ✗ |
| AFlow [27] | Multi-layer DAG | ✓ | Manual + Gen | ✓ | ✓ |
| WORKFLOW-LLM [24] | Centralized Workflow | ✓ | Manual | ✗ | ✓ |
| Game-theoretic Workflow [26] | Decentralized Negotiation | ✓ | Adaptive | ✓ | ✓ |
| HALO (Ours) | Hierarchical Structure + MCTS | ✓ | Adaptive | ✓ | ✓ |

## 3 HALO 框架

### 3.1 问题形式化

在所提出的工作流搜索过程中，一个工作流 W 由一系列子任务 {T1, T2, . . . , TK } 组成，每个子任务 Tk 由一组角色特化的基于 LLM 的智能体 Ak = {ak(1), ak(2), . . . } 处理。我们将子任务执行重新表述为工作流空间 S 上的工作流搜索过程，其中每个候选工作流 W ∈ S 代表子任务与多智能体交互的一次独特实例化。给定以自然语言表达的用户查询 Q，目标是构造一个最优推理工作流 W ∗，使其生成与用户查询 Q 相一致的期望答案 Ŷ。HALO 的优化问题定义如下：

```
W ∗ = arg max  Value(Q, W)                                              (1)
          W∈S
```

其中 Value(Q, W) 评估工作流 W 在解决用户查询 Q 上的有效性。HALO 的整体框架如图 1 所示，算法见算法 1。接下来我们详细阐述三阶段范式的每个组成部分。

### 3.2 自适应提示精炼

由于大多数用户缺乏提示工程专业知识，用户查询 Q 往往结构松散或意图模糊。为解决这一局限并提升下游推理的可靠性，我们在 HALO 框架的开头提出自适应提示精炼模块，将原始用户查询 Q 精炼为结构化且 LLM 可理解的提示 Q∗。该模块由四个协作智能体组成，每个智能体被形式化为一个函数映射，记为 P1 至 P4。这些智能体负责提示精炼的不同阶段，从查询解析直至最终综合（详见附录 A）。该过程形式化如下。

过程从任务解析智能体 P1 开始，它对原始查询 Q 进行语义分析，提取三个基本组成部分：任务类型 T、核心意图 I 与关键细节 D。这些部分随后被组装为一个结构化三元组：

```
F = P1(Q) = (T , I, D)                                                 (2)
```

这一结构化任务表示 F 在整个推理工作流中充当全局语义上下文。

基于这一结构化任务表示 F 与原始用户查询 Q，提示模板智能体 P2 构造初始提示框架 Q0，其中包含重述后的任务描述、明确的推理目标、有界的输入条件以及显式的输出格式：

```
Q0 = P2(Q, F)                                                          (3)
```

为进一步精炼初始提示模板，提示优化智能体 P3 引入慢思考提示策略 [34–38] 以及工具调用 [39] 指令，生成优化后的提示 Qopt：

```
Qopt = P3(Q0 , F)                                                      (4)
```

最后，提示生成智能体 P4 将优化后的结构综合为最终精炼提示 Q∗，它作为下游多智能体推理的入口：

```
Q∗ = P4(Qopt , F)                                                      (5)
```

### 3.3 分层推理栈

在精炼提示 Q∗ 之后，HALO 进入分层推理栈模块，它由三个协作层组成：用于任务分解的高层规划智能体 Aplan、用于动态智能体实例化的中层角色设计智能体 Arole，以及用于子任务执行的底层推理智能体 Ak = {ak(1), ak(2), . . . }。

在顶层，高层规划智能体 Aplan 接收精炼提示 Q∗ 与全局结构化任务表示 F。基于这些信息，它将整体任务分解为一系列子任务 {T1 , T2 , . . . , TK }（详见附录 B）。Aplan 并不预先执行完整分解，而是采用逐步策略，每次生成一个子任务，并依据前面各子任务的执行历史迭代更新其分解策略：

```
Tk = Aplan (Q∗ , F , Hk−1 )                                            (6)
```

其中 Hk−1 表示子任务 Tk 之前各子任务的执行历史。

每个生成的子任务 Tk 被委派给中层角色设计智能体 Arole，后者实例化一组专用的基于 LLM 的智能体 Ak = {ak(1), ak(2), . . . } 来执行子任务 Tk。该实例化过程由子任务 Tk 的语义、精炼提示 Q∗ 与全局结构化任务表示 F 共同引导，确保每个生成的智能体 ak(i) 与子任务 Tk 的要求良好对齐。对于每个生成的智能体 ak(i)，都会分配一个角色特定的系统提示 ρk(i)，以约束其在子任务 Tk 中的行为（详见附录 C）：

```
ak(i) = Arole (Tk , Q∗ , F )  ⇒  ρk(i)                                (7)
```

对于每个子任务 Tk，底层推理智能体 Ak = {ak(1), ak(2), . . . } 接收子任务 Tk、精炼提示 Q∗ 与全局结构化任务表示 F，随后展开协同推理，产生一组中间输出：

```
Yk = {yk(1) , yk(2) , . . . } = Ak (Tk , Q∗ , F )                      (8)
```

为进一步提升效率并避免不必要的子任务生成，HALO 在高层规划智能体 Aplan 中集成了早停机制。该设计受到拜占庭共识（Byzantine Consensus）理论 [40] 的启发：在单轮通信中，至少需要 3p + 1 个智能体才能容忍 p 个故障智能体。遵循这一原则，如果执行历史 Hk 中已完成子任务里至少有 66% 给出一致的答案 Ŷ，HALO 将终止推理过程。此外，当达到允许的最大子任务数时，推理过程同样会终止。

### 3.4 工作流搜索引擎

为动态探索多智能体协作并自适应地构建最优工作流，HALO 基于蒙特卡洛树搜索（MCTS）[13] 构建了工作流搜索引擎模块。工作流搜索过程将多智能体推理形式化为树结构的动作空间，其中每个节点代表一个执行子任务 Tk 的角色特化智能体 ak(i)，每条边表示智能体之间的通信转移。这些节点与边共同构成一条路径，对应每个子任务 Tk 的一个候选推理轨迹。在每次搜索迭代中，HALO 遵循标准的四阶段优化 MCTS 范式（选择、扩展、模拟与回溯），如图 2 所示。

图2：蒙特卡洛树搜索（MCTS）如何通过选择、扩展、模拟与回溯阶段引导多智能体推理的示意。每个节点代表一个智能体，边的转移由执行结果与评估反馈共同引导（原文第6页）。

**选择（Selection）。** HALO 使用 UCT 算法 [41] 递归地选出最佳智能体 ak(i) 并将其加入轨迹：

```
                                  (i)
                                v_k
UCT(a_k) = ------------------ + α ⋅ √( log N / n_k(i) )                (9)
                                (i)
                               n_k
```

其中 vk(i) 是智能体 ak(i) 的分值，nk(i) 是对智能体 ak(i) 的访问次数，N 是对父智能体 ak(i−1) 的访问次数，α 是探索系数。

**扩展（Expansion）。** 给定选择阶段选出的智能体 ak(i)，如果它包含尚未尝试的动作，HALO 便通过实例化一个新的角色特化智能体 ak(i+1) 作为其子节点来扩展搜索树。

**模拟（Simulation）。** 智能体 ak(i+1) 为子任务 Tk 发起一条模拟推理轨迹，其中一系列额外的智能体 ãk(i+2)、ãk(i+3)、. . . 参与模拟推理路径上假设的未来步骤。每个模拟智能体 ãk(j) 生成一个中间输出 ỹk(j)：

```
ỹ_k(j) = ã_k(j) (T_k , Q∗ , F )                                       (10)
```

输出 ỹk(j) 由两个辅助智能体评估。评判智能体（judging agent）赋予一个状态标签 ℓ̃k(j) ∈ {success, fail, continue}，指示子任务是否已经完成；评分智能体（scoring agent）则计算质量分值 ṽk(j) ∈ [0, 1]，以反映所生成输出的有效性（详见附录 B）。

**回溯（Backpropagation）。** 受 CoAT [42] 中价值聚合策略的启发，HALO 通过融入模拟反馈，更新搜索路径上所有已遍历节点的评估分数。为增强对任务完成状态的敏感性，我们额外引入了基于判断结果的奖励信号调整机制。

设 λ(ℓ̃k(j)) 为与状态标签 ℓ̃k(j) 相关联的影响因子，其中 λ 反映模拟结果所带来的奖励或惩罚。节点 ak(i) 的更新值计算如下：

```
                        (i)  (i)      (j † )           (j)
                       v_k ⋅ n_k + λ(ℓ̃_k     ) +   Σ   ṽ_k
v_k(i)∗ =  ──────────────────────────────────────────────────           (11)
                            (i)          (i)
                          n_k   + |Child(a_k )|
```

其中 ℓ̃k(j†) 表示推理轨迹上模拟叶节点智能体 ãk(j†) 的终态状态标签，Child(ak(i)) 指其模拟子节点的集合。

算法1：HALO 的算法

```text
Algorithm 1 Algorithm of HALO
Input: User query Q, prompt refinement agents P1 ∼ P4 , planning agent Aplan , role-design agent
Arole , inference agent pool Ak , subtask budget K
Output: Final answer Ŷ
 1: F ← P1 (Q)                                               ▷ Parse task type T, intent I, and details D
 2: Q0 ← P2 (Q, F)                                                         ▷ Build initial prompt template
 3: Qopt ← P3 (Q0 , F)                                             ▷ Optimize with prompting strategies
 4: Q∗ ← P4 (Qopt , F)                                                          ▷ Synthesize final prompt
 5: H0 ← ∅                                                          ▷ Initialize subtask execution history
 6: for k = 1 to K do
 7:       Tk ← Aplan (Q∗ , F , Hk−1 )                                     ▷ Decompose query into subtask
 8:       if Tk = stop then
 9:           break                               ▷ Terminate if planning agent signals task completion
10:       end if
11:       Ak ← Arole (Tk , Q∗ , F)                                         ▷ Generate role-specific agents
12:       for each agent ak(i) ∈ Ak do
13:           yk(i) ← ak(i) (Tk , Q∗ , F)             ▷ Generate intermediate output by executing subtask Tk
14:           ℓk(i) , vk(i) ← Evaluate(yk(i))                 ▷ Evaluate status label and quality score for output
15:           MCTS_Backpropagate(a_k(i) , ℓk(i) , vk(i) )                           ▷ Propagate execution feedback
16:       end for
17:       Hk ← Hk−1 ∪ {Tk , Ŷk }                                     ▷ Update subtask execution history
18:       if early-stop(Hk ) is True then
19:           break                               ▷ Terminate if early-stopping mechanism is triggered
20:       end if
21: end for
22: Ŷ ← Aggregate({yk(i) })                                                            ▷ Select final answer
23: return Ŷ
```

## 4 实验

### 4.1 实验设置

**代码生成。** 我们使用 HumanEval [14] 数据集，它包含 164 个 Python 编程问题及相应的单元测试。单元测试用于验证所生成代码的正确性。我们报告 pass@1 指标以评估代码准确率。

**通用推理。** 我们使用 MMLU [15] 数据集，它涵盖 57 个学科、共 15,908 道题目。每道题目以提供四个选项的多选题形式呈现。由于题目数量庞大，我们按照学科分布从整个数据集中随机抽取 13%。我们报告准确率指标以衡量答案的正确性。

**算术推理。** 我们使用 MATH [16] 数据集，它由 7 个子领域、5 个难度级别上的 12,500 道数学题组成。同样，我们按照子领域与级别的分布随机抽取 500 道数学题。我们报告准确率指标以衡量正确答案的比例。

**基线。** 我们在三个类别中将 HALO 与六个有竞争力的基线进行比较，包括单智能体框架（ReAct [11]）、静态多智能体系统（CAMEL [12]、LLM-Debate [43]），以及动态多智能体编排方法（DyLAN [21]、AgentVerse [33]、ADAS [44]）。

**HALO 设置。** 我们使用 GPT-4o [45] 实现 HALO 并开展这些实验，随机种子为 10，温度设置为 0.8，最大 token 数限制为 2048。为保证公平比较，我们在所有方法中使用相同数量的少样本示例，并且仅在代码生成任务中为 HALO 配备代码解释器作为工具（详见附录 D）。

表2：HALO 与有竞争力的基线在三个基准上的性能对比。指标包括 HumanEval 的 pass@1 (%)、MMLU 与 MATH 的准确率 (%)，以及三次运行的平均性能 Avg. (%)。所有方法均基于 GPT-4o 执行。

| 基线类型 | 方法 | 结构 | HumanEval | MMLU | MATH | Avg. |
| --- | --- | --- | --- | --- | --- | --- |
| 单智能体 | ReAct [11] | Monolithic Sequential Reasoning Flow | 69.1 | 57.6 | 29.2 | 52.0 |
| 静态 MAS | CAMEL [12] | Feedback Triplet | 72.4 | 64.3 | 31.9 | 56.2 |
| 静态 MAS | LLM-Debate [43] | Fully Connected Bipartite | 73.7 | 66.3 | 32.6 | 57.5 |
| 动态 MAS | DyLAN [21] | DAG + Feedback Loop | 81.7 | 70.1 | 35.2 | 62.3 |
| 动态 MAS | AgentVerse [33] | Hierarchical Tree | 75.2 | 67.5 | 34.4 | 59.0 |
| 动态 MAS | ADAS [44] | Search-Based Dynamic Graph Structure | 82.4 | 72.8 | 36.9 | 64.0 |
| 动态 MAS | HALO (Ours) | Hierarchical Structure + MCTS | 95.2 | 81.6 | 58.9 | 78.6 |

表3：从 MMLU 数据集中选取的五个抽象学科上的性能对比。指标为三次运行平均的准确率 (%)。

| 基线类型 | 方法 | Abstract Algebra | College Physics | Formal Logic | High School Mathematics | Moral Scenarios |
| --- | --- | --- | --- | --- | --- | --- |
| 单智能体 | ReAct [11] | 44.2 | 46.5 | 40.3 | 44.7 | 37.6 |
| 静态 MAS | CAMEL [12] | 50.4 | 54.7 | 49.8 | 51.9 | 44.2 |
| 静态 MAS | LLM-Debate [43] | 51.1 | 54.6 | 48.3 | 52.8 | 45.1 |
| 动态 MAS | DyLAN [21] | 52.9 | 60.4 | 51.2 | 58.8 | 49.6 |
| 动态 MAS | AgentVerse [33] | 53.6 | 59.4 | 50.3 | 57.1 | 48.7 |
| 动态 MAS | ADAS [44] | 55.7 | 62.4 | 52.6 | 60.0 | 51.3 |
| 动态 MAS | HALO (Ours) | 69.7 | 77.3 | 66.8 | 75.5 | 64.6 |

### 4.2 主要结果

我们开展了大量实验，在三个任务上将 HALO 与六个基线进行比较，基于 GPT-4o 的结果见表 2。此外，我们在表 3 中给出了执行 MMLU 五个抽象学科的表现，并在图 3 中给出了 MATH 三个计算密集型子领域的表现。基于这些结果，我们得出以下关键观察。

**HALO 提出的分层推理架构克服了认知过载的局限。** 与 ReAct [11] 这类要求单个智能体同时管理规划、推理与反思的框架不同，HALO 将这些职责分布到专门负责任务分解、角色实例化与子任务推理的分层推理架构之中。这一设计使智能体行为更加聚焦，并降低了认知过载。具体而言，如表 2 所示，HALO 在所有基准上相比 ReAct 均取得显著提升：HumanEval pass@1 提升 26.1%（95.2% vs. 69.1%），MMLU 准确率提升 24.0%（81.6% vs. 57.6%），MATH 准确率提升 29.7%（58.9% vs. 29.2%）。平均而言，HALO 将性能提升 26.6%（78.6% vs. 52.0%），凸显了分层推理架构相对于整体式单智能体推理的优势。

**HALO 利用自适应智能体实例化与基于搜索的工作流探索，提升任务执行的粒度。** 相比于依赖固定智能体角色与手工工作流的静态 MAS 方法（如 CAMEL [12] 与 LLM-Debate [43]），以及缺乏任务与智能体之间细粒度对齐的动态 MAS 系统（如 DyLAN [21]、AgentVerse [33] 与 ADAS [44]），HALO 引入了自适应智能体实例化与 MCTS 驱动的工作流探索。这一设计使 HALO 能够动态实例化合适的智能体角色，并基于实时反馈迭代地精炼执行轨迹。因此，在表 2 中，HALO 平均比最强基线（ADAS）高出 14.6%（78.6% vs. 64.0%），并在所有基准上持续取得最高性能：HumanEval pass@1 提升 12.8%（95.2% vs. 82.4%），MMLU 准确率提升 8.8%（81.6% vs. 72.8%），MATH 准确率提升 22.0%（58.9% vs. 36.9%）。这些结果凸显了 HALO 在大规模编排多智能体推理方面的有效性。

**HALO 擅长处理高度复杂与专家级的推理任务。** 为进一步评估 HALO 解决高专业要求任务的能力，我们在 MMLU 与 MATH 数据集的困难子领域上进行了细粒度比较，结果见表 3 与图 3。HALO 在这些具有挑战性的问题上持续优于所有基线。在 MMLU 的抽象学科上，HALO 相比最强基线（ADAS [44]）取得显著提升，平均准确率为 70.8%，而基线为 56.4%，提升 14.4%。类似地，在计算密集型的 MATH 子领域上，HALO 的平均准确率达到 43.9%，显著超过 ADAS 的 24.4%。这些结果展示了 HALO 在处理高度专业化且非平凡的推理任务上的实力。

图3：从 MATH 数据集中选取的三个计算密集型子领域上的性能对比。指标为三次运行平均的准确率 (%)（原文第9页）。

图4：在 GPT-4o 上移除自适应提示精炼模块与高层规划智能体的消融研究，覆盖三个基准（原文第9页）。

### 4.3 消融实验

为评估 HALO 各组件的影响，我们通过逐一移除组件的方式开展消融实验，在 HumanEval、MMLU 与 MATH 上测量性能。结果汇总于图 4。

**自适应提示精炼的有效性。** 我们检验了自适应提示精炼模块的必要性。移除该组件并将原始用户查询 Q 直接传入下游智能体后，我们在所有基准上都观察到明显的性能退化。如图 4 所示，性能平均下降 5.3%，其中 MMLU 受影响最大（81.6% → 75.4%）。这一结果凸显了结构化提示构建在增强任务理解、并使推理轨迹与用户意图对齐方面的重要性。

**高层规划智能体的有效性。** 我们移除高层规划智能体，将精炼后的用户查询 Q∗ 视为单步任务而不进行迭代分解。如图 4 所示，这导致所有基准的平均性能下降 11.3%。HumanEval（95.2% → 83.8%）与 MATH（58.9% → 44.7%）上的显著下降表明，移除任务分解会损害推理的连贯性，凸显了其在 HALO 中的关键作用。

## 5 结论

在本工作中，我们提出了 HALO——一个致力于应对复杂交互环境与专家领域推理任务的多智能体协作框架。HALO 以三阶段范式运行。在自适应提示精炼中，用户查询被精炼为结构化提示，以增强下游推理；在分层推理栈中，HALO 将下游流程委派给三个专门的层级，克服了认知过载的局限；在工作流搜索引擎中，HALO 利用基于搜索的工作流探索来构造最优的协作工作流。实验结果表明，与有竞争力的基线相比，HALO 取得了显著的性能提升。此外，我们发现通过引入长期记忆机制与外部知识集成可以进一步提升性能，这为未来的工作提供了新的方向。

## 致谢

本工作独立完成，未获得任何机构或资金方面的支持。

## 参考文献

参考文献从略，见原文。

## 附录 A 自适应提示精炼的系统提示

图 5 展示了自适应提示精炼模块所使用的系统提示，其中包含四个智能体的提示原文，下面按智能体逐一列出。

**任务解析智能体（Task Parser Agent）：**

```text
You are a Task Parser Agent. Your role is to analyze user queries and
extract the underlying task type, main objective, and any key details that
will guide the completion of the task.

### Inputs
You will be given these fields:
- "User Query": The user prompt containing user's intent.

### Outputs
Your output should be clear, structured, and focused on the following points:
1. **Task Type**: The general category of the task (e.g., data analysis, text
   generation, image processing).
2. **Core Intent**: The main goal or purpose of the task (e.g., "analyze
   trends," "generate summary," "predict outcomes").
3. **Key Details**: Any specific instructions or constraints that are
   important for task execution (e.g., "for the last 3 months," "in Python,"
   "based on given data").

Your response should be in the following format:
{
  "Task Type": "<task_type>",
  "Core Intent": "<core_intent>",
  "Key Details": "<key_details>"
}
```

**提示模板智能体（Prompt Template Agent）：**

```text
You are a Prompt Template Generator Agent. Your role is to generate a structured
prompt template based on the task type, core intent, and key details provided by
the Task Parser Agent. Your response should help guide the completion of the task
effectively and should be tailored to the specified task requirements.

### Inputs
You will be given these fields:
- "User Query": The user prompt containing user's intent.
- "Task Type": The general category of the task.
- "Core Intent": The main goal or purpose of the task.
- "Key Details": Any specific instructions or constraints that are important for task
  execution.

### Outputs
The structure of the output should follow the format below:
1. **Task Type**: The general category of the task as identified by Task Parser
   Agent (e.g., data analysis, text generation, image processing).
2. **Core Intent**: The main objective or purpose of the task as defined by Task
   Parser Agent (e.g., "analyze trends," "generate summary," "predict outcomes").
3. **Key Details**: Any important constraints or instructions for executing the task,
   as identified by Task Parser Agent (e.g., "for the last 3 months," "in Python,"
   "based on given data").
4. **Generated Prompt Template**: Construct a detailed template in Python string
   format that will guide the task's completion. The template should include
   placeholders for the key details identified, ensuring that it is general enough for
   reuse and clear for execution.

The generated prompt template should follow this example structure:
{
  "Task Type": "<task_type>",
  "Core Intent": "<core_intent>",
  "Key Details": "<key_details>",
  "Generated Prompt Template": "<template_string>"
}
```

**提示优化智能体（Prompt Optimization Agent）：**

```text
You are a Prompt Optimizer Agent. Your role is to refine and enhance
the prompt template generated by the Prompt Template Generator
Agent. Your task is to ensure that the generated prompt template is
clear, concise, and optimized for effective task completion. You should
focus on improving clarity, precision, and usability without changing the
core intent or task details.

### Inputs
You will be given these fields:
- "User Query": The user prompt containing user's intent.
- "Task Type": The general category of the task.
- "Core Intent": The main goal or purpose of the task.
- "Key Details": Any specific instructions or constraints that are
  important for task execution.
- "Generated Prompt Template": A detailed template in Python string
  format that will guide the task's completion.

### Outputs
The structure of your output should follow the format below:
1. **Task Type**: The general category of the task as identified by the
   Task Parser Agent.
2. **Core Intent**: The main objective or purpose of the task as defined
   by the Task Parser Agent.
3. **Key Details**: Any important constraints or instructions for
   executing the task, as identified by the Task Parser Agent.
4. **Optimized Prompt Template**: The optimized version of the prompt
   template provided by the Prompt Template Generator Agent. This
   should include any necessary improvements, such as simplifying
   language, clarifying instructions, and removing unnecessary complexity.

Your output should be a Python string containing the optimized
template. The format should look like this:
{
  "Task Type": "<task_type>",
  "Core Intent": "<core_intent>",
  "Key Details": "<key_details>",
  "Optimized Prompt Template": "<optimized_template_string>"
}
```

**提示生成智能体（Prompt Generator Agent）：**

```text
You are a Final Prompt Generator Agent. Your role is to integrate and finalize
the optimized prompt template provided by the Prompt Optimizer Agent. Your
task is to ensure that the final prompt is structured, clear, and perfectly
tailored to the task requirements. You should ensure the prompt is effective
for guiding task completion and meets the specifications provided by the
previous agents.

### Inputs
You will be given these fields:
- "User Query": The user prompt containing user's intent.
- "Task Type": The general category of the task.
- "Core Intent": The main goal or purpose of the task.
- "Key Details": Any specific instructions or constraints that are important for
  task execution.
- "Optimized Prompt Template": The optimized version of the prompt template
  provided by the Prompt Template Generator Agent.

### Outputs
The structure of your output should follow the format below:
1. **Task Type**: The general category of the task as identified by Task
   Parser Agent.
2. **Core Intent**: The main objective or purpose of the task as defined by
   Task Parser Agent.
3. **Key Details**: Any important constraints or instructions for executing the
   task, as identified by Task Parser Agent.
4. **Final Prompt**: The final version of the prompt, generated based on the
   optimized template. This should be a Python string that is ready for execution
   and should be clearly formatted for the task at hand.

Your output should be a Python string containing the final prompt. The format
should look like this:
{
  "Task Type": "<task_type>",
  "Core Intent": "<core_intent>",
  "Key Details": "<key_details>",
  "Final Prompt": "<final_prompt_string>"
}
```

图5：自适应提示精炼模块所使用的系统提示。精炼过程由四个专用智能体执行：任务解析智能体从用户查询中提取任务语义；提示模板智能体构建结构化提示模板；提示优化智能体增强清晰度与可用性；提示生成智能体产出最终提示（原文第13页）。

## 附录 B 规划智能体与工作流搜索引擎的系统提示

图 6 展示了高层规划智能体与工作流搜索引擎模块的系统提示，下面按智能体逐一列出。

**任务分解智能体（Task Decomposition Agent）：**

You are a Task Decomposition Agent. Your job is to break a user's overall task into a sequence of clear, actionable subtasks—one at a time.

**Inputs**

You will be given these fields:

- "User Query": the original prompt from the user
- "Task Type": the category of the user's request
- "Core Intent": the user's main goal
- "Key Details": any important constraints or context
- "Implementation history of subtasks": Implementation of past subtasks. Maybe contain "subtask name", "subtask answer", "subtask result".

**Your Objective**

1. Analyze the provided fields and the progress so far.
2. Generate exactly one new subtask that advances toward fulfilling the Core Intent.
3. Make the subtask as specific and actionable as possible.
4. If the overall task is already complete (no further decomposition needed), reply with exactly: stop.

**Output Format**

Return either:

- A JSON object containing a single key `"next subtask"` whose value is your new subtask description, for example:

```json
{
  "next subtask": "<description of the next actionable subtask>"
}
```

- Or if no more subtasks are required, The value of a single key `"next subtask"` should be `"stop"`, for example:

```json
{
  "next subtask": "stop"
}
```

**Guidelines**

- Place instructions first.
- Use triple quote delimiters around this prompt.
- Be concise, precise, and unambiguous.
- Only produce one subtask per response.
- Do not include any commentary or extra fields.

**评分智能体（Scoring Agent）：**

You are a **Score Agent** whose sole responsibility is to evaluate the output generated by a role specific agent for a given subtask and assign a numeric quality score between **0** and **1** (inclusive), with a preference for smoother, non-extreme values across the scale.

**Input:**

You will be given these fields:

- "Task Type": the category of the user's overall request
- "Core Intent": the user's main goal
- "Key Details": any important constraints or context
- "User Query": the original prompt from the user
- "Current Subtask": the specific subtask being executed
- "Agent Role": the role of the agent whose output you must score
- "Output of the Agent Role": the actual result produced by that agent
- "Judge Agent Output": the output of the Judge Agent, which indicates whether the subtask was a success, fail, or continue.

**Your Task:**

1. Assess how well the **Output of the Agent Role** satisfies the **Current Subtask** in light of the **Task Type**, **Core Intent**, and **Key Details**.
2. Consider correctness, completeness, relevance, and adherence to the specified role.
3. Carefully evaluate the **Judge Agent Output** to give appropriate incentives, not to give incentives, or to give penalties based on the performance of the agent.
4. Provide a quality score between **0** and **1**. The score should not be biased toward extreme values (0 or 1). It should reflect the degree to which the output meets the task requirements in a balanced way.

**Output Format:**

Return **only** a JSON object with a single key `"score"` whose value is a decimal number between **0** and **1**, rounded to up to four decimal places. Do **not** include any additional keys, commentary, or formatting.

**Example:**

**Input:**

"Task Type": "data processing",
"Core Intent": "prepare data for model training",
"Key Details": "normalize all features to [0,1]",
"User Query": "Normalize feature columns",
"Current Subtask": "data normalization",
"Agent Role": "min max normalizer",
"Output of the Agent Role": "applied min-max to each column, but used [−1,1] scaling"
"Judge Agent Output": "continue"

**Correct Output:**

```json
{
  "score": 0.55
}
```

**评判智能体（Judging Agent）：**

You are a **Judge Agent** whose responsibility is to determine whether a role specific agent's output has completed the given subtask. Your evaluation must result in one of three statuses: **"success"**, **"fail"**, or **"continue"**.

**Input:**

You will be given these fields:

- "Task Type": the category of the user's overall request
- "Core Intent": the user's main goal
- "Key Details": any important constraints or context
- "User Query": the original prompt from the user
- "Current Subtask": the specific subtask being executed
- "Agent Role": the role of the agent whose output you must judge
- "Output of the Agent Role": the actual result produced by that agent

**Your Task:**

1. Assess whether the **Output of the Agent Role** fully satisfies the **Current Subtask** in light of the **Task Type**, **Core Intent**, and **Key Details**.
2. If the subtask is correctly and completely done, return **"success"**.
3. If the subtask cannot be completed based on this output (e.g., wrong method or errors), return **"fail"**.
4. If the subtask is partially completed or needs further refinement before moving on, return **"continue"**.

**Output Format:**

Return **only** a JSON object with a single key `"status"` whose value is one of **"success"**, **"fail"**, or **"continue"**. Do **not** include any extra keys, commentary, or formatting.

**Example:**

**Input:**

"Task Type": "data processing",
"Core Intent": "prepare data for model training",
"Key Details": "normalize all features to [0,1]",
"User Query": "Normalize feature columns",
"Current Subtask": "data normalization",
"Agent Role": "min max normalizer",
"Output of the Agent Role": "applied min max scaling to each column with correct [0,1] range"

**Correct Output:**

```json
{
  "status": "success"
}
```

图6：高层规划智能体与工作流搜索引擎模块的系统提示，包括任务分解智能体、评分智能体与评判智能体（原文第14页）。

## 附录 C 中层角色设计智能体的系统提示

图 7 展示了中层角色设计智能体的系统提示，包括面向子任务的角色生成与提示构建，下面按智能体逐一列出。

**子任务智能体生成器（Agent Generator for Subtask）：**

You are an Agent Generation Expert. Your task is to generate a list of agent roles that would be required to complete a specific subtask based on the provided input.

**Input:**

You will be given these fields:

- "Task Type": the category of the user's request
- "Core Intent": the user's main goal
- "Key Details": any important constraints or context
- "User Query": the original prompt from the user
- "Current Subtask": A subtask that will be implemented.

**Your Objective:**

1. Based on the 'Current Subtask', generate a list of possible agents' roles that would help solve this subtask.
2. Consider the context provided in the 'Task Type', 'Core Intent', 'Key Details', and 'User Query' to ensure that the generated roles are highly relevant.
3. You can generate multiple agent roles if the subtask requires it (e.g., for a data processing task, the roles could be 'Data Cleaning', 'Data Normalization', etc.).
5. Ensure that the roles are clearly defined and can be directly used to guide other agents in performing their tasks.

**Output:**

Return a JSON object with the following format:

```json
{
  "agent roles": ["<role_1>", "<role_2>", ...]
}
```

**子任务提示模板生成器（Prompt Template Generator for Subtask）：**

```text
You are a Prompt Template Generator Agent. Your role is to create a clear,
structured, and reusable prompt template for an agent based on the provided
subtask and agent role. The template should guide the agent's behavior precisely
and include placeholders for any dynamic details.

### Inputs
You will be given these fields:
- "Subtask": The specific subtask instructions.
- "Agent Role": The role description of a specific agent.

### Outputs
Your output must be a valid Python string representing a JSON-like object with the
following keys:
1. **Agent Role**: the role description (e.g., "Data Cleaning Agent").
2. **Subtask**: the specific subtask instructions (e.g., "Remove duplicate entries
   from the sales dataset.").
3. **Prompt Template**: a detailed template string that will instruct the agent how to
   perform the subtask, incorporating placeholders for any inputs or parameters (for
   example, `<input_data>`, `<parameters>`).

Example format:
{
  "Agent Role": "<agent_role>",
  "Subtask": "<subtask_description>",
  "Prompt Template": "You are a <agent_role>. Your task is to
  <subtask_description>. Use <input_data> and follow these rules: <guidelines>."
}
```

**子任务提示优化器（Prompt Optimizer for Subtask）：**

```text
You are a Prompt Optimizer Agent. Your role is to refine and enhance
the prompt template created by the Prompt Template Generator Agent
for a specific subtask and agent role. Your goal is to improve clarity,
precision, and effectiveness of the template without altering the core
task requirements.

### Inputs
You will be given these fields:
- "Subtask": The specific subtask instructions.
- "Agent Role": The role description of a specific agent.
- "Original Prompt Template": A detailed template string that will instruct
  the agent how to perform the subtask.

### Outputs
Your output must be a valid Python string representing a JSON-like
object with the following keys:
1. **Agent Role**: the role description (e.g., "Data Cleaning Agent").
2. **Subtask**: the specific subtask instructions (e.g., "Remove
   duplicate entries from the sales dataset.").
3. **Optimized Prompt Template**: your improved version of the prompt
   template, with clearer language and precise instructions.

Example format:
{
  "Agent Role": "<agent_role>",
  "Subtask": "<subtask_description>",
  "Optimized Prompt Template": "<optimized_template>"
}
```

**子任务最终提示生成器（Final Prompt Generator for Subtask）：**

```text
You are a Final Prompt Generator Agent. Your role is to integrate the
optimized prompt template provided by the Prompt Optimizer Agent for a
specific agent role and subtask, and produce the final system prompt that the
agent will execute. The final prompt should be clear, actionable, and self-
contained.

### Inputs
You will be given these fields:
- "Subtask": The specific subtask instructions.
- "Agent Role": The role description of a specific agent.
- "Optimized Prompt Template": Improved version of the prompt template,
  with clearer language and precise instructions.

### Outputs
Your output must be a valid Python string representing a JSON-like object
with the following keys:
1. **Agent Role**: the role description (e.g., "Data Cleaning Agent").
2. **Subtask**: the specific subtask instructions (e.g., "Remove duplicate
   entries from the sales dataset.").
3. **Final Prompt**: the final prompt string that the agent should receive,
   incorporating the optimized template exactly as intended for execution.

Example format:
{
  "Agent Role": "<agent_role>",
  "Subtask": "<subtask_description>",
  "Final Prompt": "You are a <agent_role>. Your task is to
  <subtask_description>. <any additional instructions>."
}
```

图7：中层角色设计智能体的系统提示，包括面向子任务专用智能体的角色生成与提示构建（原文第15页）。

## 附录 D 实验所用提示

图 8 展示了 HumanEval、MMLU 与 MATH 实验所使用的提示，包括查询前缀与少样本示例，内容如下。

**HumanEval Query Prefix：**

Now you will generate a function according to the following description. Remember **not** to include the function signature in your answer. Do **not** include any other text in your answer.

Attention: just generate coding, you are not required to test the code.

Coding prompt is as follows:

```python
{}
```

**MMLU Query Prefix：**

Now can you answer the following question as accurately as possible?
question:

```text
{}
```

options:

```text
{}
```

your answer:

**MATH Few Shot：**

[example 1]

Problem:

```text
Kevin Kangaroo begins hopping on a number line at 0. He wants to get to 1, but he can hop only $\frac{1}{3}$ of the distance. Each hop tires him out so that he continues to hop $\frac{1}{3}$ of the remaining distance. How far has he hopped after five hops? Express your answer as a common fraction.
```

Answer:

```text
Let's think step by step
Kevin hops $1/3$ of the remaining distance with every hop.
His first hop takes $1/3$ closer.
For his second hop, he has $2/3$ left to travel, so he hops forward $(2/3)(1/3)$.
For his third hop, he has $(2/3)^2$ left to travel, so he hops forward $(2/3)^2(1/3)$.
In general, Kevin hops forward $(2/3)^{k-1}(1/3)$ on his $k$th hop.
We want to find how far he has hopped after five hops.
This is a finite geometric series with first term $1/3$, common ratio $2/3$, and five terms.
Thus, Kevin has hopped $\frac{\frac{1}{3}\left(1-\left(\frac{2}{3}\right)^5\right)}{1-\frac{2}{3}} = \boxed{\frac{211}{243}}$.
The answer is \frac{211}{243}}
```

[example 2]

Problem:

```text
What is the area of the region defined by the equation $x^2+y^2 - 7 = 4y-14x+3$?
```

Answer:

```text
Let's think step by step
We rewrite the equation as $x^2 + 14x + y^2 - 4y = 10$ and then complete the square,
resulting in $(x+7)^2-49 + (y-2)^2-4=10$,
or $(x+7)^2+(y-2)^2=63$.
This is the equation of a circle with center $(-7, 2)$ and radius $\sqrt{63},$
so the area of this region is $\pi r^2 = \boxed{63\pi}$.
The answer is 63\pi
```

[example 3]

Problem:

```text
If $x^2+y^2=1$, what is the largest possible value of $|x|+|y|$?
```

Answer:

```text
Let's think step by step
If $(x,y)$ lies on the circle,
so does $(x,-y),$ $(-x,-y),$ and $(-x,-y),$ (which all give the same value of $|x| + |y|$),
so we can assume that $x \ge 0$ and $y \ge 0.$
Then $|x| + |y| = x + y.$ Squaring, we get
\[(x + y)^2 = x^2 + 2xy + y^2 = 1 + 2xy.\]
Note that $(x - y)^2 \ge 0.$
Expanding, we get $x^2 - 2xy + y^2 \ge 0,$ so $2xy \le x^2 + y^2 = 1.$
Hence,\[1 + 2xy \le 2,\]which means $x + y \le \sqrt{2}.$
Equality occurs when $x = y = \frac{1}{\sqrt{2}},$
so the maximum value of $|x| + |y|$ is $\boxed{\sqrt{2}}.$
The answer is \sqrt{2}
```

**MATH Few Shot Prefix：**

Follow the given examples and answer the mathematics problem:

```text
{}
```

Now please follow the above given examples and answer the mathematics problem:

Problem:

```text
{}
```

Your answer:

图8：HumanEval、MMLU 与 MATH 实验所使用的提示，包括查询前缀与少样本示例（原文第16页）。
