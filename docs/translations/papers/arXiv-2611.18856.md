# 自改进记忆让持续递归自我改进成为可能（Self-Improvement Memory Enables Continual Recursive Self-Improvement）

> 来源：https://arxiv.org/abs/2611.18856
> 原文：docs/papers/arXiv-2611.18856.pdf
> 翻译日期：2026-11-18 ｜ 范围：全文 ｜ 方式：机器翻译初稿，未经人工校对
> 引用于：docs/literature/W6-self-evolution-rsi.md

## 目录

- 摘要
- 1 引言
- 2 相关工作
- 3 方法
  - 3.1 问题形式化
  - 3.2 自改进记忆
  - 3.3 通过 SIM 的持续 RSI
- 4 实验
  - 4.1 实验设置
  - 4.2 跨数据集 CRSI
  - 4.3 跨模型 CRSI
    - 4.3.1 跨模型族的 Harness 迁移
    - 4.3.2 跨模型代际的持续改进
    - 4.3.3 一个 Harness 服务多个模型
  - 4.4 分析：SIM 在 CRSI 中的作用
- 5 结论
- 局限
- 伦理声明
- 参考文献
- 附录指南
- 附录 A 扩展相关工作
- 附录 B 基准与评估
- 附录 C 实验设置
- 附录 D SIM 实现
- 附录 E 补充结果
- 附录 F 案例研究

## 摘要

Harness 优化研究通常假定策略模型与基准都是固定的。只要其中之一发生变化，优化器就必须决定演化得到的 Harness 中哪些部分可以复用、哪些需要修订；但仅凭 Harness 本身，往往解释不了当初为什么要做某处修改，也说明不了这些改动的效果如何。本文研究持续递归自我改进（Continual Recursive Self-Improvement，CRSI）：一种让既有 Harness 优化方法在兼容的基准或策略模型之间继续运行的设定。我们提出面向 Harness 优化器（而非解题策略）的自改进记忆（Self-Improvement Memory，SIM）。SIM 按反复出现的 Harness 问题对修改分组，并记录它们的修改理由、预测结果与实测结果，以及评估上下文；随着优化不断推进，新的尝试会继续扩充这份历史。我们在四个领域上的实验显示，在跨数据集比较与成对跨模型比较中，SIM 的最终得分高于「只保留 Harness」的延续和「只保留根因」的延续。在编码领域的十次独立源运行中，配合 SIM 的成对延续比只保留 Harness 的延续平均把最终得分提高 2.36 分（p = 0.003）。

关键词：递归自我改进、智能体 Harness、持续学习

## 1 引言

LLM 智能体既依赖它的策略模型，也依赖那套管理上下文、工具与执行流程的 Harness。改进 Harness 可以在不更新模型权重的前提下提升性能，但靠人工去找有用的改动，需要反复的工程与评估（Lin et al., 2026; Xia et al., 2026）。近期工作用递归自我改进（recursive self-improvement，RSI）把这一过程自动化：借助执行反馈，反复提出、评估并选择 Harness 修改（Lee et al., 2026; Lin et al., 2026; Xia et al., 2026）。

演化出的 Harness 虽然能在其他基准或模型上带来提升（Lin et al., 2026; Wu et al., 2026; Xia et al., 2026; Xu et al., 2026b），但优化通常是在一个固定设定内进行的。随着模型更新、智能体遇到新任务，Harness 优化往往需要越过这个设定继续下去。这带来两个根本性挑战。

**适配新模型。** 模型适配出现在两种设定里：一是多模型服务，即同一个共享 Harness 要支撑不同的策略模型；二是模型演进，即同一模型族内新版本取代旧版本。两者都指向同一件事——复用演化出的 Harness 及其改进经验，而不是为每个模型、每次发布都单独优化一套 Harness。然而，适配某个策略的修改换到另一个策略上，其相互作用可能完全不同，即使基准保持不变也一样（Yang et al., 2026; Yu et al., 2026d）。在我们的工作区实验中，一个由 Opus 演化出来的 Harness 在 Gemini 上的起始分只有 68.41，低于种子 Harness 的 73.89（图 4）。优化器必须判断：继承下来的机制里哪些仍在起作用、哪些需要修订。

**适配新数据。** 在策略固定的前提下，不同的任务分布会暴露出源优化没有处理掉的失败。举例来说，一个只检查命令是否成功执行的完成闸门，可能还得进一步检查「可行的解是否同时也是最优的」。在我们的文本分类实验中，源演化出的 FewShotAll Harness 在目标套件上的起始分是 72.92，低于种子的 75.72（图 3）。因此，一个在源侧很有用的修复，往往要先修订才能帮到目标侧。

无论在哪种迁移中，仅凭演化出的 Harness 都回答不了几个关键问题：某处修改当初为什么被提出？它预期修复什么？它被测试时又发生了什么？源优化会产生这些证据，但它们并不必然随 Harness 一起走。没有这份历史，目标优化就可能重复早先尝试过的路子，或者在不清楚用途的情况下改动继承来的组件。于是我们追问：源优化阶段积累的经验，能否帮助 Harness 适配新的模型或数据？

本文研究持续递归自我改进（CRSI）：在基准或策略模型发生变化之后，只要保持一个兼容的可执行接口，Harness 优化就可以继续进行。我们提出让改进经验与演化 Harness 一同迁移的自改进记忆（SIM，图 1）。SIM 按所解决的 Harness 问题对被选中的修改分组，让提议者与选择者能够读到它们的理由、预测结果与实测结果，以及评估上下文。它会为新问题建立条目，也会把后续尝试与结果追加到已有条目上，从而帮助优化器决定哪些修改应当保留、修订、替换或删除。

图1：超越直接迁移的持续改进。(a) CRSI 把演化 Harness 与 SIM 一并带入跨数据、跨模型的目标 RSI，SIM 指导复用与修订。(b) 两种条件都从同一个由 Opus 演化出的 Harness 出发，在 Gemini 的工作区任务上继续 RSI；箭头把轮次与候选都对齐的实测端点连起来。（原文第1页）

本文的贡献如下：

- **持续 Harness 优化。** 我们定义了两种设定：策略固定下的跨数据集延续，以及基准与数据划分固定下的跨模型延续。既有 Harness 优化方法可以在保留自身「提议—评估—选择」流程的同时直接使用这一设定。
- **自改进记忆。** 我们引入一份结构化记录，涵盖 Harness 问题、修改与结果，并同时约束提议与选择两个环节；它在保留源侧经验的同时，还能吸收目标优化期间的新尝试。
- **覆盖四个领域的受控证据。** 在起始 Harness、轮次数与候选预算都对齐的条件下，完整 SIM 在六个跨数据集设定与四个 Opus 到 Gemini 设定中都优于「只保留 Harness」和「只保留根因」的延续。在编码领域的十次独立源运行中，配合 SIM 的成对延续有 9 次取得提升，相对只保留 Harness 的延续平均高出 2.36 分（p = 0.003）。

## 2 相关工作

**智能体 Harness 的递归自我改进。** Yu et al. (2026b) 综述了 Harness 优化工作流、递归复用，以及演化出的修改在什么条件下可以迁移。Meta-Harness 与 AHE 在 Harness 代码上做搜索，依据是执行轨迹与得分（Lee et al., 2026; Lin et al., 2026）。另一些方法让智能体修改自己的系统（Zhang et al., 2026a,b,d），或学习一套编辑 Harness 的策略（Shao et al., 2026）。SIA 则把 Harness 修改与任务模型权重更新结合起来（Hebbar et al., 2026）。

**演化 Harness 的迁移。** 演化出的 Harness 可以在留出任务、其他模型或下游基准上保持增益（Lee et al., 2026; Lin et al., 2026; Shi et al., 2026）。近期方法通过基准互斥的演化与模块化修改（Wu et al., 2026）、正则化搜索（Xia et al., 2026），或把通用机制与基准特定机制分开（Yu et al., 2026a）来促进迁移。它们的效果仍然取决于模型与 Harness 如何相互作用（Yang et al., 2026; Yu et al., 2026d）。PluginRSI 同样会在后续优化中复用自己的插件库。

**改进过程的记忆。** 已有工作保留候选产物（Lee et al., 2026）、修改历史（Xia et al., 2026）、改进图（Zhang et al., 2026c）、技能修订记录（Li and Hu, 2026）与操作手册（Zhang et al., 2026f）。HarnessBank 按所解决的问题对候选 Harness 分组（Luo et al., 2026）。Xu (2026) 用自由文本笔记与源任务回放延续多任务演化；Harness2 跨基准复用一个改进库（Xu et al., 2026a）。Meta-Skill 与 Meta2 则迁移「如何构建或编辑任务特定 Harness」的已学指导（Qian et al., 2026; Yuan et al., 2026）。持续适配还引出保持与干扰问题（Chen et al., 2026; Zhao et al., 2026）。SIM 把 Harness 问题与修改、预测结果、实测结果以及来源信息连起来。我们在基准或模型变化之后，从同一个演化 Harness 出发，分别以「无 SIM」「只有根因」或「完整记录」三种条件延续优化，以此检验 SIM。附录 A 展开了这些比较，其中还包括解题智能体的延续优化与记忆。

## 3 方法

### 3.1 问题形式化

**Harness RSI。** 沿用 Meta-Harness（Lee et al., 2026），我们在一个固定策略模型 M 周围优化一个可执行 Harness H。Harness 决定模型的上下文、工具与执行流。我们把一个设定写成 σ = (M, X)，其中演化集与留出评估集 X_evo、X_eval 互不相交。得分 J(H; M, X) 遵循该基准的聚合规则（附录 B）。只有演化集的反馈可用于提出修改、选择候选、更新 SIM 或决定何时停止。

一次运行包含 N 轮。在第 t = 0, …, N−1 轮，评估器在 X_evo 上执行 H_t，并把得分、轨迹与错误作为 F_t 返回。提议者 P 用 F_t 与本轮运行的历史 D_t（更早的反馈与代码差异）生成 k 个候选 Harness C_t。选择者 S 在执行之前筛选提议，并在已评估的候选之间做权衡——综合考虑性能、复杂度、领域特异性与回归风险：

```
C_t = P(H_t, F_t, D_t),
H_{t+1} = S(H_t, F_t, C_t, F_tC)                                        (1)
```

这里 F_tC 来自通过筛选并被执行的那些候选的反馈。如果没有候选被接受，则 H_{t+1} = H_t。提议者与选择者都是基于 LLM 的 Harness 工程师；M 是执行任务的策略。

**持续设定。** 在 σ_S = (M_S, X_S) 上完成源 RSI 之后，优化从最终保留的 Harness H_S 出发，在 σ_T = (M_T, X_T) 中继续。跨数据集 CRSI 中，基准改变而策略保持不变（X_S ≠ X_T，M_S = M_T）；跨模型 CRSI 中，策略在相同基准与相同划分上改变（M_S ≠ M_T，X_S = X_T）。两者都要求一个共享的可执行 Harness 接口。我们把目标改进量度定义为 J(·; M_T, X_T^eval) 下的最终得分减去起始得分。

### 3.2 自改进记忆

SIM 按所解决的反复出现的 Harness 问题对修改分组。对于一个根因假设 c_i（例如「过早宣告完成」），一条记忆条目写作：

```
m_i = (c_i, [(a_ij, o_ij, p_ij)]_j)                                      (2)
```

> 译注：原文此处公式两侧的大括号在文本层提取失败，已按原文页面渲染复原为圆括号。

其中 j 按顺序索引各次尝试，M_t = {m_i} 就是当前记忆。每次尝试保存它带来的修改及其理由 a_ij、预测与实测的任务结果 o_ij，以及来源信息 p_ij（领域、基准、策略与轮次）。关于「某处修改会修复哪些任务」的预测在评估之前记录，评估之后再核对。

每一轮，提议者都会在系统提示里收到完整的 SIM，选择者在评估候选时读到同一份记录。双方读取全部条目，不做检索也不做截断。于是式 (1) 的循环变成：

```
C_t = P(H_t, F_t, D_t; M_t),
H_{t+1} = S(H_t, F_t, C_t, F_tC; M_t)                                    (3)
```

每条提议要么引用一个已有的根因，要么命名一个新根因。选择之后，只有被选中的候选会记入 e_t，即使这处修改带来回归、或没能修复它预测的任务，其实测结果也会照记。更新 M_{t+1} = U(M_t, e_t) 把这条记录追加到被引用的问题上，或创建新条目，同时保留更早的尝试。若没有任何修改被接受，则 e_t = ∅ 且 U(M_t, ∅) = M_t。根因文本完全相同的条目会合并，且不丢弃任何历史。条目匹配的细节见附录 D.1。

### 3.3 通过 SIM 的持续 RSI

源 RSI 从一份空 SIM 开始，产出 (H_S, M_S)。完整 SIM 把二者一起带进目标优化（图 2）。提议者与选择者依据每处修改的理由、结果与评估上下文，判断它是否仍然适用于当前的失败；他们可以在保留早期记忆记录的前提下，保留、修订、替换或删除 Harness 修改。关于如何使用这份历史的提示词说明见附录 D.2。

图2：智能体外层循环中的 SIM。从 (H_S, M_S) 出发，提议者与选择者查阅 SIM（虚线箭头）以改进演化集任务上的 Harness。选择完成后，SIM 记录被选中的修改及其实测结果（青色箭头）。留出评估始终在循环之外。（原文第4页）

**迁移条件。** 我们比较四种条件：从种子 Harness 出发的冷启动（Cold Start）(H_0, ∅)；Harness 迁移（Harness Transfer）(H_S, ∅)；只含根因的问题记忆（Problem-Only Memory）(H_S, M_S^c)；以及完整 SIM（Full SIM）(H_S, M_S)。三个迁移条件从同一个 H_S 出发，四种条件使用相同的目标策略、任务以及轮次与候选预算。每种条件在目标 RSI 全程保持各自被分配的记忆条件，同时都保留普通的目标运行历史 D_t（附录 C.3）。源侧历史经由 SIM 进入；目标侧的新记录遵循同一记忆条件。

## 4 实验

我们的实验回答四个问题：

- SIM 能否在基准或策略模型变化之后改善延续的 RSI？（§4.2–4.3）
- 完整 SIM 记录是否比只保留根因更有帮助？（§4.2 与 §4.3.1）
- SIM 如何引导对继承 Harness 修改的复用与修订？（§4.4；附录 F.5）
- SIM 的收益在独立演化的源 Harness 之间是否稳定？（§4.4）

### 4.1 实验设置

**领域。** 我们研究四个领域，在其中源演化出的 Harness 在目标环境里仍然可执行（附录 B，表 4）。编码从 Terminal-Bench 2.1（TB2.1）迁到 Terminal-Bench 4（TB4）（Merrill et al., 2026; Terminal-Bench Team, 2026a,b），任务是跑在容器里的 shell 任务，由任务自带的测试打分。文本分类使用 Meta-Harness 的在线分类环境（Lee et al., 2026），从三数据集的源套件迁到八数据集的目标套件，后者在源 RSI 中从未出现过。智能体工作区从 Harvey LAB（Harvey AI, 2026）迁到 JobBench（Li et al., 2026）、GDPval（Patwardhan et al., 2026）与 APEX-Agents（Vidgen et al., 2026）的等权平均，打分接口改编自 RRSI（Xia et al., 2026），由 Gemini 3.8 Flash 担任评判者。工程设计从 EngDesign（Guo et al., 2025）迁到 Frontier-Eng（Chi et al., 2026），由冻结的验证器打分。任务按均匀随机方式划分、不做分层，得到规模近似相等的演化集与留出集；确切数量见附录 B。只有演化集的得分与执行轨迹会送到提议者、选择者与 SIM。主比较中每个任务做五次 rollout，且每次 rollout 都计入得分。

**迁移、模型与预算。** 跨数据集 CRSI 在两个阶段都以 Gemini 3.8 Flash（Google DeepMind, 2026b）为策略。跨模型迁移比较中，源 RSI 使用 Claude Opus 5.5（Anthropic, 2026），随后由 Gemini 3.8 Flash 在相同基准与划分上继续。两个阶段使用的目标基准都是上面列出的那几个：TB4、八数据集分类套件、合并后的工作区基准与 Frontier-Eng。策略权重保持冻结。主比较中的提议者与选择者同样由 Gemini 3.8 Flash 担任。一项源 RSI 消融把这两个角色换成 Claude Opus 5.5，结果在两个编码种子上都带来更大的增益（附录 E.4.2，表 7）。种子方面，编码用最小的 AHE 种子（Lin et al., 2026）与 Terminus-2（Merrill et al., 2026），文本分类用 NoMemory 与 FewShotAll（Lee et al., 2026），工作区与工程则用跑在 MCP 工具网关（Vidgen et al., 2026）之上的 ReAct 智能体（Yao et al., 2023）。后两个领域沿用 RRSI 的环境、种子 Harness 与评估接口（Xia et al., 2026）；模型与预算如上所述，划分、rollout 数量与工作区评判者见附录 B。每次源运行和目标运行都用 N = 10 轮，在 §3.1 描述的提议者—选择者循环中每轮提出 k = 5 个候选。在执行前被筛掉的提议不获得评估得分；每任务五次 rollout 指的是另一笔独立的评估预算。

**对比条件。** 冷启动从种子 Harness 开始且不带 SIM。Harness 迁移、问题记忆与完整 SIM 共用同一个源演化 Harness，分别对应「无 SIM」「只有根因」和「完整记录」三种记忆条件。这些条件贯穿目标优化全程，目标任务、策略、轮次数与候选预算均对齐（§3.3）。

**指标与报告。** 所有得分都换算到 0–100 量纲并保留两位小数：编码用 pass@1，文本分类用跨样本汇总的准确率，工作区用各基准自带的 rubric、胜率与 pass@1 得分，工程用通过率或奖牌得分（附录 B）。前后得分分别评估起始 Harness 与最终目标轮次结束后保留的那个版本，都在留出集上计算。除专门的成对研究外，每个条件都只是一次完整 RSI 运行，其每任务五次 rollout 估计的是执行性能而非优化方差。我们对各个设定做描述性报告，并用这组十对编码研究来评估跨独立源运行的变异（§4.4）。

### 4.2 跨数据集 CRSI

SIM 在全部六组数据集迁移上都提高了最终得分。图 3 的记忆消融从同一个演化 Harness 出发，比较「无 SIM」「只有根因」「完整记录」三种延续。完整 SIM 在六个设定里全部最高：比 Harness 迁移高 2.43–4.35 分，比问题记忆高 0.20–6.06 分。问题记忆的效果好坏参半：相对 Harness 迁移，低时低 1.82 分，高时高 2.40 分。因此，保留修改历史与评估证据，比只保留诊断更有帮助（附录 E.4.1）。

相对最强替代方案的领先幅度，从 NoMemory 上的 0.20 分到工程上的 4.35 分不等。§4.4 检验这一收益是否会独立演化的源 Harness 之间重复出现。附录 E.2 列出了两种迁移设定的确切起始分与最终分。

源侧改进并不保证目标侧有更好的起点。源 RSI 在全部六个设定上把留出源得分提高了 2.75–6.41 分（附录 E.1），但 FewShotAll Harness 进入目标 RSI 时却低于种子：72.92 对 75.72。只保留 Harness 的延续升到 74.12，仍低于冷启动的 75.92，而完整 SIM 升到 77.92。

在 NoMemory 上，冷启动的提升幅度反而大于完整 SIM（3.40 分对 2.20 分），但最终得分更低（72.00 对 73.60）。因此我们同时报告两个端点，并以与完整 SIM 起点相同的 Harness 迁移作为记忆流程的直接对照。

图3：跨数据集 CRSI：目标 RSI 之前（空心柱）与之后（实心柱）的留出目标得分。三个迁移条件共用源演化 Harness，冷启动使用种子。各领域的坐标轴范围不同。确切得分见表 5。（原文第7页）

### 4.3 跨模型 CRSI

我们考察三件事：模型族之间的迁移、跨模型代际的延续，以及多个模型共享一套 Harness。

#### 4.3.1 跨模型族的 Harness 迁移

Opus 演化出的 Harness 第一次在 Gemini 上运行时，在每个领域都低于 Gemini 的种子 Harness（图 4）。差距从文本分类的 0.60 分到工作区的 5.48 分不等。目标 RSI 并不总能扭转这一劣势：有三个领域里 Harness 迁移最终仍低于冷启动。完整 SIM 在四个领域中全部取得最高分，比只保留 Harness 的延续高 3.60–11.33 分；在四个领域中也全都高于问题记忆（附录 E.4.1）。差距最大的是工作区：两者都从 68.41 出发，完整 SIM 达到 84.75，而 Harness 迁移只有 73.42。

图4：从 Opus 5.5 到 Gemini 3.8 Flash 的跨模型 CRSI，基准与划分固定。空心柱与实心柱分别是 Gemini 目标 RSI 之前的留出得分与之后的留出得分。迁移条件共用 Opus 演化出的 Harness，冷启动使用种子（表 6）。（原文第7页）

#### 4.3.2 跨模型代际的持续改进

代际链在 TB2.1 上把演化 Harness 与 SIM 依次带过各代 Gemini 模型（表 1；设置见附录 C.5）。Fresh RSI 每一代都从种子出发。第一代里两种流程使用同一个种子，所以这一次比较检验的是初始运行期间 SIM 的作用。在随后三代中的两代里，延续都优于 Fresh RSI：Gemini 3.5 Flash 上高 3.5 分，Gemini 3.8 Flash 上高 1.6 分；而在 Gemini 4 Argon 上最终低 0.8 分。

| Gemini 模型 | Seed | Fresh RSI | CRSI |
|---|---|---|---|
| 2.5 Flash | 17.8 | 21.4 | 22.4 |
| 3.5 Flash | 70.2 | 73.3 | 76.8 |
| 3.8 Flash | 87.2 | 88.9 | 90.5 |
| 4 Argon | 89.7 | 95.6 | 94.8 |

表1：留出 TB2.1 上跨 Gemini 代际的成功率。Seed 使用未经演化的 Harness，Fresh RSI 独立优化它；CRSI 在第一代加入 SIM，此后继承上一代的 Harness 与 SIM。加粗用于比较 Fresh RSI 与 CRSI。

#### 4.3.3 一个 Harness 服务多个模型

我们还问：在文本分类目标套件上，一套 Harness 能否同时服务 Grok、Opus 与 Gemini（表 2；设置见附录 C.6）。我们比较三种做法：顺序 CRSI、汇总三个模型反馈的统一综合，以及把分别用各策略演化出的 Harness 迁过来。统一综合的平均分与分别演化的 Harness 相当：留出样本上 75.24 对 75.20，都高于共享种子的 73.28。顺序 CRSI 达到 74.20；三个 S3 Harness 在各评估模型上的均值落在 66.84–72.24 之间。这是一次针对「公共 Harness 性能」的描述性比较；对完整 SIM 流程的检验在 §4.3.1 那些起始 Harness 对齐的比较里进行。

| Harness 构造方式 | Evolve | Held-out | All |
|---|---|---|---|
| B1：各模型自有 Harness | 77.40 | 75.20 | 76.30 |
| B2：共享种子 | 72.36 | 73.28 | 72.82 |
| S1：顺序 CRSI | 76.72 | 74.20 | 75.46 |
| S2：统一综合 | 78.92 | 75.24 | 77.08 |
| S3：源策略（Gemini 3.8 Flash） | 74.28 | 71.24 | 72.76 |
| S3：源策略（Grok 4.20 Reasoning） | 68.24 | 66.84 | 67.54 |
| S3：源策略（Claude Opus 5.5） | 75.20 | 72.24 | 73.72 |

表2：在 Grok 4.20 Reasoning、Claude Opus 5.5 与 Gemini 3.8 Flash 上取平均的文本分类得分。S3 各行给出用于演化该 Harness 的策略，每个 Harness 都用三个模型评估。All 列对规模相等的演化集与留出集取平均。各列的最高均值加粗。

### 4.4 分析：SIM 在 CRSI 中的作用

成对比较检验的是：从同一个起始 Harness 出发，SIM 是否改善了延续。随后我们追踪单条记忆条目，看早期的诊断如何影响后续修改。

**SIM 改善了从同一演化 Harness 出发的延续。** 我们从 Terminus-2 在 TB2.1 上重复源运行十次，再用每次得到的 Harness 各初始化两段十轮的 TB4 运行。每一对内部，起始 Harness、策略、基准以及轮次与候选预算都相同：一段继承该源运行的 SIM 并追加目标尝试，另一段则不带 SIM 继续（§4.4，表 3）。分析单位是相互独立的源运行。

SIM 在 10 对中有 9 对取得更高的最终分（表 3），只有一对偏向不带 SIM 的延续，领先 0.61 分。从共同的平均起始分 18.36 出发，带 SIM 的平均最终分为 21.70，不带 SIM 为 19.33。成对平均优势为 2.36 分（95% CI [1.05, 3.68]；双侧配对 t(9) = 4.06，p = 0.003）。双侧符号秩检验给出 p = 0.006；配对标准化效应量 dz = 1.28（统计细节见附录 C.4）。

| 运行 | Start | No SIM | SIM | ∆ |
|---|---|---|---|---|
| 1 | 18.18 | 20.61 | 22.42 | +1.81 |
| 2 | 16.97 | 17.58 | 19.39 | +1.81 |
| 3 | 17.58 | 20.00 | 20.61 | +0.61 |
| 4 | 18.18 | 18.18 | 23.64 | +5.46 |
| 5 | 17.58 | 18.79 | 20.61 | +1.82 |
| 6 | 19.39 | 20.00 | 23.64 | +3.64 |
| 7 | 18.79 | 20.00 | 21.82 | +1.82 |
| 8 | 18.18 | 20.00 | 19.39 | −0.61 |
| 9 | 19.39 | 18.18 | 23.03 | +4.85 |
| 10 | 19.39 | 20.00 | 22.42 | +2.42 |
| **均值** | **18.36** | **19.33** | **21.70** | **+2.36** |

表3：来自十个相互独立的 Terminus-2 源运行的成对编码延续。Start 是演化 Harness 的留出 TB4 得分；No SIM 与 SIM 是十轮目标运行之后的得分。∆ 为 SIM 减 No SIM（均值 +2.36；配对 p = 0.003）。

**SIM 引导对继承修改的复用与修订。** 完整 SIM 与 Harness 迁移都从 Terminus-2 源 RSI 继承了同一个完成闸门（图 11b，附录 F.3）。有了 SIM，提议者会读取闸门在源侧的条目 P5 及其理由与源侧结果，在保留完成验证的同时追加目标检查，其中包括「可行性与最优性」的对照。没有 SIM 的那次运行则把闸门改得更严，两次修复完成死锁，还把继承来的闸门误算到自己第一轮头上。需求本身迁移了过去，但它的实现需要修订。附录 F.5 与 F.6 总结了跨领域、跨模型的迁移模式以及这些案例对 SIM 的启示。

**SIM 在保留诊断的同时补充目标证据。** P3 记录了「交付物与验证器接口契约不一致」这一问题（图 12；附录 F.4）。目标第 5 轮与第 6 轮在这条诊断下追加了修订后的检查与实测结果，让源侧尝试和未兑现的预测对后续轮次仍然可用。

**SIM 在编码上同时支撑更早的目标进展与源侧保持。** 对两个编码种子，完整 SIM 在第 1–10 轮全程最好或并列最好（图 5a、5b）。以 AHE 为种子时它在第 5 轮、以 Terminus-2 为种子时在第 2 轮，就超过了最强对照的最终分（20.61）。在 AHE 的源侧保持曲线中，所有迁移条件在留出 TB2.1 上都从 90.22 出发（图 8，附录 E.3）：完整 SIM 在 225 次 rollout 中损失 3 次成功，问题记忆损失 4 次，Harness 迁移损失 6 次；同时它在 TB4 上的增益高于问题记忆（6.67 分对 0.61 分）。

图5：编码优化（TB2.1→TB4）。(a,b) 每一轮目标运行后保留 Harness 的留出 TB4 得分，第 0 轮即起始 Harness。(c) 十对延续中最终得分之差（SIM 减 No SIM），源 Harness 由独立演化的 Terminus-2 得到。虚线标出均值；个体得分见表 3。（原文第9页）

## 5 结论

CRSI 在基准或策略模型发生变化时继续 Harness 优化。SIM 把更早的诊断、修改与结果带进这一过程，并记录新的尝试。在起始 Harness 对齐的条件下，完整 SIM 在全部六个跨数据集设定与四个 Opus 到 Gemini 领域中都优于只保留 Harness 的延续。十对编码研究在独立源运行之间测得 2.36 分的平均优势。这些案例表明，这份历史能帮助提议者与选择者复用更早的推理，同时为新需求修订已有的修复方案。

## 局限

在我们的算力预算内，独立的 RSI 重复实验只覆盖编码领域；其他领域每个条件只跑一次。我们研究的是 Harness 接口兼容的设定，并把优化器的规划与搜索流程固定住。我们的比较把 SIM 当作一个完整流程来评估，即把继承的记忆与目标优化期间的更新合在一起考察。

后续工作可以把评估扩展到更多次重复运行与更长的迁移序列，并探索规划、token 分配与工具接口的适配。

## 伦理声明

本文实验中的优化智能体是基于 LLM 的，它们会重写 Harness 代码。得到的 Harness 运行在各基准的执行环境中，策略权重固定，得分由冻结的验证器或固定评判流程计算。一个自我修改的 Harness 完全可能在不解决预期任务的情况下通过评估器。我们把留出集反馈与优化智能体隔离，明确标出每个基准所用的验证器或评判者，并纳入一个「被接受、但没能修复其目标任务」的修改（附录 F.2）。工作区得分也可能反映 LLM 评判者的偏好。实验使用的是现有公开可用的基准与数据集。

## 参考文献

参考文献从略，见原文。

## 附录指南

附录 B–D 分别规定评估、实验设置与 SIM 实现；附录 E 给出补充的数值结果与消融；附录 F 用案例研究解释所观察到的修改。

| 附录 | 内容 |
|---|---|
| A | 扩展相关工作：Harness 优化、迁移与记忆。 |
| B | 基准与评估：数据集、划分、反馈可及性与打分。 |
| C | 实验设置：模型、种子、预算、对比条件与重复运行。 |
| D | SIM 实现：智能体如何读取、更新与存储 SIM。 |
| E | 补充结果：源侧与目标侧得分、源侧保持与消融。 |
| F | 案例研究：源 RSI、持续适配、记忆记录与迁移模式。 |

## 附录 A 扩展相关工作

本附录围绕三个问题展开 §2：Harness 是如何改进的；设定变化之后优化如何继续；记忆在这一过程中扮演什么角色。

### A.1 智能体 Harness 是如何改进的？

Harness RSI 围绕一个策略模型优化提示词、工具、控制流、记忆与上下文管理。GEPA 用轨迹反思与重组来优化提示词（Agrawal et al., 2026）。Meta-Harness 通过共享文件系统暴露既有实现、执行轨迹与得分（Lee et al., 2026）。AHE 让 Harness 组件与修改结果可观测，并把修改级的预测与后续任务结果对照（Lin et al., 2026）。在机器学习开发中，MLToolBench 通过监督学习与强化学习学会诊断性地使用工具（Yu et al., 2026c）。

另一些方法改变的是「改进本身如何进行」。Self-Harness 把弱点挖掘、Harness 提议与基于回归的验证结合起来（Zhang et al., 2026a）。DGM 与 Hyperagents 探索智能体程序的自我修改与开放式演化（Zhang et al., 2026b,d）；Hyperagents 还报告了元级改进跨领域的迁移。Harness-R1 用强化学习从失败轨迹中学出编辑 Harness 的策略（Shao et al., 2026），而 SIA 同时更新 Harness 与任务模型的权重（Hebbar et al., 2026）。Bai et al. (2026) 训练「想法级评论者」，在昂贵的实证验证之前筛掉机器学习修改。MLToolBench 学的是任务智能体的行为，评论者学的是候选评估；SIM 则为提议者与选择者保存修改历史。CRSI 为兼容的「提议—评估—选择」循环定义了基准或策略变化之后的延续（§3.1）。

### A.2 迁移之后优化如何继续？

**演化 Harness 的迁移。** AHE 评估了从 Terminal-Bench 迁到 SWE-bench Verified 而不重新演化的表现（Lin et al., 2026）；Meta-Harness 与 PluginRSI 报告了跨求解模型的迁移（Lee et al., 2026; Shi et al., 2026）。有若干方法试图改善这种迁移。ModularRSI 使用基准互斥的演化数据，对比成功与失败轨迹，把修改导向功能模块中反复出现的缺陷（Wu et al., 2026）。RRSI 约束打包式修改，并把陷入停滞的搜索重定向到探索不足的组件（Xia et al., 2026）。Harmony Harness 把通用机制与基准特定的适配分开（Yu et al., 2026a）。不过，模型与其 Harness 的相互作用仍可能要求模型特定的适配（Yang et al., 2026; Yu et al., 2026d）。

**延续优化。** 已有工作也会在后续优化中复用改进经验。PluginRSI 从初始 Harness 继续优化时会复用演化出的插件库（Shi et al., 2026）。Xu (2026) 用自由文本演化笔记与源任务回放，在新基准上延续多任务 Harness 演化。Harness2 把被采纳的 Harness 与精炼经验保存在库里，并测试其跨基准复用（Xu et al., 2026a）。相关设定还包括任务流与连续情节（Karten et al., 2026; Wei et al., 2026; Xiao et al., 2026）。Adaptive Auto-Harness 把持久的演化工作区与可部署 Harness 分开，可在已存分支间做可选路由（Liu et al., 2026）。EvoHarnessBench 研究当外部提供的工具、技能与专家智能体不断扩张时的保持与适配（Ke et al., 2026）。

**评估延续。** 留出评估以及反馈与推理预算对齐的基线，有助于把提升与「投入了更多优化资源」区分开（Wang et al., 2026）。SEAGym 在整个演化过程中跟踪验证、迁移、回放与成本（Zheng et al., 2026）。关于任务流漂移与编码基准的研究也记录了干扰与遗忘（Chen et al., 2026; Zhao et al., 2026）。我们报告演化 Harness 在目标 RSI 前后的得分，从同一个起始 Harness 出发、在轮次与候选预算对齐的条件下比较各记忆条件，并在一次编码迁移中单独跟踪源侧保持情况（附录 E.3）。

### A.3 记忆存了什么、谁在用它？

**面向 Harness 优化的记忆。** 保存改进历史已有若干先例。Meta-Harness 保留候选产物（Lee et al., 2026）；RRSI 记录假设、差异、得分与成本变化以及采纳决定，包括被拒绝的修改（Xia et al., 2026）。Causal Improvement Graph 把证据、假设、干预与结果连起来（Zhang et al., 2026c）。SkillHone 保存诊断、修订与评估证据（Li and Hu, 2026），Turbo Harness 把已完成的优化总结成面向实例特定修改的操作手册（Zhang et al., 2026f）。HarnessBank 按被修改的组件与被诊断出的失败对候选分组，保留高性能 Harness 供重组（Luo et al., 2026）。可见，围绕问题来组织改进同样有先例：Meta-Skill 冻结已学到的支撑设计原则，为每个测试任务构建一套 Harness（Qian et al., 2026）；Meta2 冻结可复用的演化指导，供任务执行期间做修改使用，并在任务运行之间重置 Harness（Yuan et al., 2026）。

**面向解题的记忆。** Reflexion 存储语言化反思来指导后续尝试（Shinn et al., 2023），Voyager 维护一个不断增长的可执行技能库（Wang et al., 2024）。ExpeL 从任务经验中提炼可复用的洞见（Zhao et al., 2024）；ReasoningBank 与 ACE 保留策略与经验教训（Ouyang et al., 2026; Zhang et al., 2026e）。ACE 从执行轨迹出发，增量式地扩展、精炼并去重自己的操作手册。Memory Transfer Learning 比较了不同编码领域与模型上的任务经验表示，在其研究设定中发现抽象洞见比具体轨迹更易迁移（Kim et al., 2026）。这些记忆支撑的是执行任务的智能体。

**持续 Harness 优化中的 SIM。** SIM 提供给提议者与选择者的是一份按 Harness 问题组织的记录，把被选中的修改与其理由、预测结果、实测结果和评估上下文连起来（§3.2）。这份记录随演化 Harness 一起跨越基准或模型的迁移，并在目标 RSI 期间获得新的尝试。我们与「无 SIM」「只有根因」的比较检验的正是这一完整流程——把继承的历史与目标侧的更新合在一起（附录 E.4.1）。

## 附录 B 基准与评估

本节规定主比较（跨数据集与 Opus 到 Gemini）以及成对编码研究所用的协议。我们列出基准与划分规模，说明哪些反馈可以指导优化，然后逐领域定义打分规则。模型代际实验与共享 Harness 实验另有设定，分别见附录 C.5 与 C.6。

### B.1 我们用了哪些基准？

**基准。** 我们研究四个领域，在其中源演化出的 Harness 在目标环境里仍然可执行。编码以 Terminal-Bench 2.1（TB2.1）为源、Terminal-Bench 4（TB4）为目标（Merrill et al., 2026; Terminal-Bench Team, 2026a,b）。文本分类使用 Meta-Harness 的在线分类环境（Lee et al., 2026）：源套件由 LawBench（Fei et al., 2024）、Gretel 对 Symptom2Disease 的改编版（Gretel AI, 2023）与 USPTO50k（Schneider et al., 2016）组合而成；目标套件包含八个源 RSI 中未出现的数据集——AG News（Zhang et al., 2015）、GoEmotions（Demszky et al., 2020）、Banking77（Casanueva et al., 2020）、Financial PhraseBank（Malo et al., 2014）、SciCite（Cohan et al., 2019）、TweetEval-Hate（Barbieri et al., 2020）、Amazon Reviews（Amazon5）（Keung et al., 2020）与 SciTail（Khot et al., 2018）。智能体工作区任务以 Harvey LAB（Harvey AI, 2026）为源，JobBench（Li et al., 2026）、GDPval（Patwardhan et al., 2026）与 APEX-Agents（Vidgen et al., 2026）共同构成目标环境。工程设计以 EngDesign（Guo et al., 2025）为源、Frontier-Eng（Chi et al., 2026）为目标。表 4 给出任务清单与 rollout 分配；划分与反馈可及性规则见附录 B.2，各领域打分协议见附录 B.3–B.6。

**源与目标的角色。** 跨数据集 CRSI 中，策略模型固定，基准从源换成上面列出的目标。跨模型 CRSI 中，基准及其任务划分固定而策略改变：源 RSI 用源策略在该基准上运行，目标 RSI 由目标策略继续。Opus 到 Gemini 的比较在两个阶段都使用表 4 中对应的 T 清单。

### B.2 划分如何使用？

表 4 中的任务（文本分类为样本）被均匀随机地划分为规模近似相等的演化集与留出集，不按类别、难度或来源数据集分层。当某基准的任务数为奇数时，演化半取偶数的一半。两个集合互不相交；划分之后没有任何任务或 rollout 被从打分分母中移除。

只有演化集的得分与执行轨迹可用于提议、选择、SIM 更新与停止决策。解题策略在留出任务上执行 Harness，以测量起始分、最终分与逐轮诊断得分（§4.4）；这些留出得分与轨迹不会传给 Harness 优化智能体。

在这些主比较与成对编码研究中，两个划分上的打分预算都是每任务五次 rollout，各条件之间对齐；Frontier-Eng 中重叠的组件按附录 B.6 的规则记零分。所报告的 Harness 版本、独立运行次数与统计比较见附录 C.4。

### B.3 编码：Terminal-Bench 2.1 与 4

**环境与指标。** Terminal-Bench 任务在容器中运行，配有任务描述、shell 访问与任务专属测试。我们报告 pass@1，由每次任务 rollout 的二元结果估计。对 n 个任务、每个任务五次 rollout，以 y_ir ∈ {0, 1} 表示任务 i 的第 r 次 rollout 是否通过任务验证器，则百分制得分为：

```
pasŝ@1 = (100 / n) ∑_{i=1}^{n} (1 / 5) ∑_{r=1}^{5} y_ir                  (4)
```

**失败的 rollout。** 因基础设施原因失败的 rollout 仍留在分母中，计零分。

| 领域 | 基准 | Total | Evolve 任务 / rollout | Held-out 任务 / rollout | Metric |
|---|---|---|---|---|---|
| Coding | S: TB2.1 | 89 | 44 / 220 | 45 / 225 | pass@1 |
| Coding | T: TB4 | 66 | 33 / 165 | 33 / 165 | pass@1 |
| Text cls. | S: 3 datasets | 412 | 206 / 1,030 | 206 / 1,030 | accuracy |
| Text cls. | T: 8 datasets | 1,000 | 500 / 2,500 | 500 / 2,500 | accuracy |
| Workspace | S: Harvey LAB | 160 | 80 / 400 | 80 / 400 | rubric |
| Workspace | T: JobBench | 65 | 32 / 160 | 33 / 165 | rubric |
| Workspace | T: GDPval | 220 | 110 / 550 | 110 / 550 | win rate |
| Workspace | T: APEX-Agents | 480 | 240 / 1,200 | 240 / 1,200 | pass@1 |
| Workspace | T: merged | 765 | 382 / 1,910 | 383 / 1,915 | mean of 3 |
| Engineering | S: EngDesign | 67 | 34 / 170 | 33 / 165 | pass rate |
| Engineering | T: Frontier-Eng | 47 | 24 / 120 | 23 / 115 | medal |

表4：本文实验所用的基准清单，并给出跨数据集 CRSI 中的源（S）与目标（T）角色。划分规模为「任务 / rollout」（文本分类为「样本 / rollout」）。每份清单都被均匀随机地划分为规模近似相等的两半，每任务名义上有五次 rollout。Frontier-Eng 中与 EngDesign 重叠的部分不计分，但保留在分母里。三个工作区目标被联合演化，并以等权平均报告；merged 行是它们任务数与 rollout 数之和。

### B.4 文本分类

在线分类环境沿用 Meta-Harness：由 Harness 控制样本的存储、检索与预测上下文。表 4 中的样本数是各套件的总数，不是单个数据集的分配数。

**评估期间的样本记忆。** 任务智能体只读取事先从训练/演化数据中提供的带标签样本。留出标签只用于打分，不会回流进它的样本记忆。对固定的 Harness，五次评估重复都从同一个初始样本记忆状态出发。这份记忆为任务智能体提供预测上下文，与支撑 Harness 优化的 SIM 是两回事。

**跨样本的准确率。** 我们在一个划分的全部样本上计算准确率，把三个源数据集或八个目标数据集汇总在一起。对划分 q ∈ {evo, eval}，记 n_q 为样本总数，y_ir(H; q) ∈ {0, 1} 表示 Harness H 在第 r 次 rollout 中是否为样本 i 预测出正确标签，则百分制准确率为：

```
A_cls(H; q) = (100 / (5·n_q)) ∑_{i=1}^{n_q} ∑_{r=1}^{5} y_ir(H; q)        (5)
```

每个样本权重相同，因此一个数据集的贡献与其样本数成比例。演化集与评估集使用同一种聚合方式。

### B.5 智能体工作区任务

**任务打分与评判。** 我们沿用 RRSI（Xia et al., 2026，附录 B.3–B.6）描述的各基准打分接口。我们的运行对所有工作区基准都用 Gemini 3.8 Flash 作为评判者，这与 RRSI 的混合评判配置和 GDPval 投票小组不同。Harvey LAB 报告满足的 rubric 条目比例，JobBench 使用其加权 rubric 得分。GDPval 把每份生成的交付物与该基准的专家交付物对比，报告相对该参照的胜率。APEX-Agents 报告 pass@1，单次 rollout 是否成功由该任务的 rubric 是否被满足决定；重复 rollout 用来估计这一成功概率。在每个基准内部，评判接口与模型在各对比条件之间固定不变。我们先把每个基准的得分换算到 0–100 量纲，再取等权平均。

**等权基准聚合。** 对划分 q ∈ {evo, eval}，记 S_b(H; q) 为 Harness H 在基准 b 上的百分制得分，则工作区得分为：

```
S_workspace(H; q) = (1 / 3) ∑_{b ∈ B} S_b(H; q)                          (6)
```

其中 B 包含 JobBench、GDPval 与 APEX-Agents。每个基准贡献三分之一，与其任务数或 rubric 条目数无关。用于选择目标 Harness 的演化集性能目标，以及所报告的评估汇总，都使用这一同一权重。每个基准内部的打分仍沿用它自己的评估惯例，取平均发生在算出该基准得分之后。表 5 的工作区行报告的就是这个汇总值。

### B.6 工程设计

Frontier-Eng 没有自己的 MCP 网关，沿用 EngDesign 的 runner 与网关。EngDesign 使用二元验证器判定通过；Frontier-Eng 使用相对冻结阈值的奖牌得分，金、银、铜分别映射为 1.00、0.67 与 0.33。这两个工程指标都不使用 LLM 评判者。

**源侧重叠。** Frontier-Eng 含有一个源自 EngDesign 的组件，包含七个子问题（Chi et al., 2026）。沿用 RRSI 的做法，我们给这个重叠组件记零分，同时把它留在原始分母中，即使在 24/23 的划分之后也一样。

## 附录 C 实验设置

本节规定模型、种子 Harness、对比条件与优化预算。通用设置覆盖跨数据集与 Opus 到 Gemini 的迁移（§4.2–4.3.1）；最后两个小节描述跨模型代际的延续与共享 Harness 的构造（§4.3.2–4.3.3）。基准打分见附录 B，SIM 实现见附录 D。

### C.1 使用哪些模型与预算？

**解题策略。** 跨数据集 CRSI 的两个阶段都以 Gemini 3.8 Flash 为策略。跨模型族比较以 Claude Opus 5.5 为源策略、Gemini 3.8 Flash 为目标策略。策略权重保持固定。

**Harness 优化智能体。** 提议者与选择者都使用 Gemini 3.8 Flash，即使任务由 Opus 执行时也是如此。附录 E.4.2 的消融在源 RSI 期间把提议者与选择者换成 Opus。

**优化预算。** 每次 RSI 运行使用 N = 10 轮，每轮 k = 5 个候选提议。候选提议与任务 rollout 是两笔独立预算：主比较在每个划分上每任务五次 rollout（附录 B）。在执行前被筛掉的提议不获得 rollout 得分。

**每轮成本。** 一轮编码运行约需 4 小时，其中评估 1.7 小时、候选采样 34 分钟。我们在各方法之间对齐轮次数与候选数量；token 用量与运行时长可能不同。

### C.2 从哪些 Harness 出发？

我们使用已有工作中公开可得的种子 Harness。编码与文本分类各用两个种子，以测试不同的起始 Harness；重复优化运行见附录 C.4。

**编码。** AHE 种子从一个基础 shell 工具起步，允许修改提示词、工具、中间件、技能、子智能体与记忆（Lin et al., 2026）。Terminus-2 随 Harbor 分发，RRSI 也使用它（Merrill et al., 2026; Xia et al., 2026）。

**文本分类。** NoMemory 不保存训练样本；FewShotAll 保存已观察到的带标签样本，并把它们作为少样本上下文（Lee et al., 2026）。

**工作区与工程。** 我们使用 RRSI 的 ReAct toolbelt 智能体来做文件操作、PDF 阅读与代码执行（Vidgen et al., 2026; Xia et al., 2026; Yao et al., 2023）。它的 6 个文件（1,743 行）由源与全部三个目标共享，因此 Harvey LAB 的 Harness 可以原样在目标上运行。工程使用同一个智能体，配一份空白系统提示与任务包装器，由固定的任务专属验证器评估（附录 B.6）。该种子有 7 个文件（1,857 行），提示词单独放在一个模块里。这两个领域沿用 RRSI 的环境、种子 Harness 与评估接口。模型与预算如上所述；划分、rollout 数量与工作区评判者见附录 B。

### C.3 四种方法有何不同？

图 6 总结了 §3.3 的四种条件：

- **冷启动（Cold Start）：** 种子 Harness H_0，不带 SIM。
- **Harness 迁移（Harness Transfer）：** 源演化 Harness H_S，不带 SIM。
- **问题记忆（Problem-Only）：** 同一个 H_S，只有根因，省略修改、结果与来源信息。
- **完整 SIM（Full SIM）：** 同一个 H_S，带完整的源侧记录 M_S，并在目标 RSI 期间更新。

| 条件 | Harness | 目标 RSI 期间的 SIM |
|---|---|---|
| 冷启动 | H_0 | 无 |
| Harness 迁移 | H_S | 无 |
| 问题记忆 | H_S | 只有根因 |
| 完整 SIM | H_S | 完整记录；在目标侧更新 |

图6：迁移条件。后三行共用源演化 Harness。表中所列的记忆条件贯穿目标 RSI 全程；完整记录包含根因、修改、结果与来源信息。目标轮次与候选预算对齐。

每种条件都在目标 RSI 全程保持不变。所有方法都保留普通的目标运行历史 D_t。四者使用相同的目标策略、演化任务、轮次与候选预算、评估预算，并通过同一个 RSI 循环接收反馈。Harness 迁移采用的是已有工作中研究过的「演化 Harness 起点」（Lee et al., 2026; Lin et al., 2026; Xu, 2026）。

### C.4 运行如何报告与重复？

**所报告的 Harness。** 每一轮为下一轮保留一个 Harness；H_S 是最终保留的源侧 Harness。before 得分评估用于初始化目标 RSI 的那个 Harness，after 得分评估最终目标轮次结束时保留的那个版本，目标改进量就是二者之差。曲线画的是每个保留版本的实测得分，不对历史得分取滚动最大值。

**独立运行。** 重复的任务 rollout 与独立的优化运行是两类不同的变异来源。每个主跨数据集条件与 Opus 到 Gemini 条件都只跑一次完整 RSI。成对编码研究从 Terminus-2 重复源 RSI 十次；每个演化 Harness 各初始化两段目标延续，一段带 SIM、一段不带（§4.4，表 3）。任务 rollout 估计的是执行性能。这十次独立源运行为成对研究提供跨运行区间；单次运行的条件只做描述性报告。对成对研究，配对 t 区间与双侧检验使用十个最终得分之差；符号秩检验对并列取平均秩，并枚举全部 2^10 个符号指派。

### C.5 跨代际迁移如何检验？

我们让优化依次经过 Gemini 2.5 Flash（Gemini Team, 2025）、3.5 Flash（Google DeepMind, 2026a）、3.8 Flash（Google DeepMind, 2026b）与 4 Argon（Google DeepMind, 2026c），基准保持为 TB2.1。Fresh RSI 每一代都从种子 Harness 出发；CRSI 第一代从同一个种子出发，之后把演化 Harness 与 SIM 传给每一代后继模型。第一行检验的是初始 RSI 运行期间 SIM 的作用，只有后面的行检验来自更早代际的迁移。表 1 报告一位小数的得分，结果在 §4.3.2 讨论。

外部得分使用了不同的评估设置，仅作参考：已发表的分数中，Gemini 2.5 Flash 配 Terminus-2 在 TB2.0 上为 16.9（Merrill et al., 2026），Gemini 3.5 与 3.8 Flash 在 TB2.1 上分别为 76.2 与 89.4（Google DeepMind, 2026a,b）。这些是外部参照，不是对齐的对照组。我们不给出 Gemini 4 Argon 的外部得分。

### C.6 共享 Harness 如何检验？

我们在文本分类目标套件上测试一套由 Grok 4.20 Reasoning、Claude Opus 5.5 与 Gemini 3.8 Flash 共享的 Harness（表 2）。演化集与留出集各含 500 个样本，每个样本五次 rollout（每个划分 2,500 次 rollout）。

**Harness 构造方式。** 我们比较两个基线和三种构造共享 Harness 的做法：

- **B1：各模型自有 Harness。** 每个策略模型跑自己的 RSI，并用自己演化出的 Harness 接受评估。
- **B2：共享种子。** 三个模型都用同一个未经演化的 Harness。
- **S1：顺序 CRSI。** 顺序为 Grok 4.20 Reasoning、Gemini 3.8 Flash、Claude Opus 5.5，在这一设定下由弱到强。每个模型把演化 Harness 与 SIM 传给下一个。
- **S2：统一综合。** 每一轮汇总三个模型的轨迹反馈，提议对同一套共享 Harness 的更新。
- **S3：单智能体迁移。** 用三个策略模型各自单独演化一套 Harness，再用全部三个模型评估每一套结果。

本实验测试的是公共 Harness 的性能；表 6 另外检验从对齐的起始 Harness 迁移 SIM 的效果。

**得分聚合。** 所有跨模型平均都用等权。B1 对三对「模型— Harness」取平均，每个模型用各自的 Harness；B2、S1、S2 对共用同一 Harness 的三个模型取平均。每个 S3 行给出演化该 Harness 所用的源策略，并报告它在同一组评估模型上的均值。All 列为 (Evolve + Held-out)/2，即两个等规模划分的平均。

每种流程各跑一次，不比较优化成本。§4.3.3 的结果描述的是观察到的均值；小差异既不能确立统计等价，也不能给出每个模型上的排名。

## 附录 D SIM 实现

我们在 §3 之外补充条目匹配细节、提示词指导与所存储的记录格式。

### D.1 条目如何匹配？

对 §3.2 的更新而言，由提议者自行判断某个诊断是否与已有根因相符，不使用额外的相似度模型。它的选择会在评估之前写进该轮的变更清单。根因文本完全相同的条目会被确定性地合并，并保留全部尝试。

### D.2 提议者与选择者如何使用 SIM？

§3.3 的提示词指导可归纳如下：

1. 把条目当作先验经验，同时保留选择不同修改的灵活性。
2. 核对每条条目背后的领域、基准与模型。
3. 当已有诊断能解释当前失败时，优先从它出发。
4. 在基准或模型变化之后复用其理由，并重新评估该修改。
5. 当新证据支持时，修订、替换或覆盖某处 Harness 修改。
6. 只有在新证据足以支持时，才重访一个已被测试过的方向。
7. 当已有诊断都解释不了这次失败时，新建一条问题条目。
8. 在相似设定中更看重任务特定的证据；当基准与模型同时改变时则降低其权重。

### D.3 一条 SIM 记录包含什么？

每次运行把 SIM 存成一个 JSON 文件，示意结构如下：

```
{ "next_id": 10,
  "carried_from": { "arm": <源运行>, "domain": "coding_enriched",
                    "into": <目标运行> },
  "aliases": { "P6": "P5" },          // P6 被并入 P5
  "problems": [ ...条目 P1 P2 P3 P4 P5 P7 P8 P9... ] }
```

每个问题条目包含 {id, name, opened_round, attempts[]}：name 给出根因假设，opened_round 记录它第一次被诊断出来的轮次。每次尝试包含：

```
{ round, sample, accepted, backfilled, what,
  files, predicted, fixed, missed, passed, total, domain }
```

what 与 files 描述这处修改，domain 标明它所属的设定。predicted 列出评估之前认为会被修复的任务，fixed 与 missed 在事后记录实际结果。passed/total 是该尝试在演化集评估中的成功次数与总次数。accepted 表示选择者在该轮采纳了这处修改，即使某些预测中的修复并未成功。这处修改日后可能被改动或替换，而它的记录仍留在 SIM 里——附录 F.2 的 P8 就是一例。不同轮次中针对同一任务的预测属于彼此独立的观察。

carried_from 标明源运行与目标运行；aliases 保存被合并条目的标识符（例如 P6→P5）。每条条目的 ID 与 opened_round 要在其所记录的那次运行的上下文中读取。附录 F 给出了按原样保存的记录，包括图 12 中的 P3。

## 附录 E 补充结果

我们报告源 RSI 得分（§E.1）、目标侧确切得分（§E.2）、源侧保持（§E.3）以及记忆与 Harness 智能体的消融（§E.4）。模型代际、共享 Harness 与十对编码的结果在正文（表 1、表 2、表 3）；修改历史与案例在附录 F。评估与报告遵循附录 B 与 C.4；差值均为绝对分差。

### E.1 源 RSI 能改进种子 Harness 吗？

源 RSI 在全部六个设定上都提高了留出源得分，幅度为 2.75–6.41 分（图 7）。其中五个设定里，留出集的增益大于演化集的增益；例外是 FewShotAll，其留出集与演化集增益分别为 6.41 分与 6.60 分。§4.2 检验这些源侧增益是否能换来更好的目标起点。

图7：Gemini 3.8 Flash 上的源 RSI：种子 Harness H_0 与源演化 Harness H_S 在源演化集和留出源评估集上的得分。(a) 以 AHE 为种子、在 TB2.1 上的编码；(b) 以 Terminus-2 为种子的编码；(c) 以 NoMemory 为种子、在源套件上的文本分类；(d) 以 FewShotAll 为种子的同一任务；(e) Harvey LAB 上的工作区任务；(f) EngDesign 上的工程设计。H_S 是图 3 中 Harness 迁移、问题记忆与完整 SIM 的起始 Harness。空心柱与青色柱分别给出各划分的种子分与源演化分，两个值都有标注。所有子图共享零基线与相同得分量纲。（原文第23页）

### E.2 各方法在目标侧表现如何？

表 5 与表 6 分别给出图 3 与图 4 所绘结果的确切数值。

| 领域 / 种子 | 冷启动 Before | 冷启动 After | Harness 迁移 Before | Harness 迁移 After | 问题记忆 Before | 问题记忆 After | 完整 SIM Before | 完整 SIM After |
|---|---|---|---|---|---|---|---|---|
| Coding / AHE | 16.36 | 19.39 | 18.18 | 20.61 | 18.18 | 18.79 | 18.18 | **24.85** |
| Coding / Terminus-2 | 18.18 | 19.39 | 19.39 | 19.39 | 19.39 | 20.61 | 19.39 | **21.82** |
| Text cls. / NoMemory | 68.60 | 72.00 | 71.40 | 71.00 | 71.40 | 73.40 | 71.40 | **73.60** |
| Text cls. / FewShotAll | 75.72 | 75.92 | 72.92 | 74.12 | 72.92 | 75.52 | 72.92 | **77.92** |
| Workspace / ReAct | 73.89 | 82.98 | 74.93 | 85.07 | 74.93 | 85.54 | 74.93 | **87.89** |
| Engineering / ReAct | 39.13 | 40.87 | 39.13 | 42.61 | 39.13 | 42.61 | 39.13 | **46.96** |

表5：跨数据集 CRSI：图 3 中六个设定在目标 RSI 前后的留出目标得分。第一列给出领域与种子 Harness。加粗标出每个设定中最高的最终分。

| 领域 / 种子 | 冷启动 Before | 冷启动 After | Harness 迁移 Before | Harness 迁移 After | 问题记忆 Before | 问题记忆 After | 完整 SIM Before | 完整 SIM After |
|---|---|---|---|---|---|---|---|---|
| Coding / AHE | 16.36 | 19.39 | 13.94 | 18.18 | 13.94 | 20.61 | 13.94 | **21.82** |
| Text cls. / FewShotAll | 78.32 | 82.72 | 77.72 | 80.20 | 77.72 | 81.32 | 77.72 | **83.80** |
| Workspace / ReAct | 73.89 | 82.98 | 68.41 | 73.42 | 68.41 | 79.22 | 68.41 | **84.75** |
| Engineering / ReAct | 39.13 | 40.87 | 39.13 | 42.61 | 39.13 | 46.96 | 39.13 | **50.43** |

表6：跨模型 CRSI（Claude Opus 5.5 到 Gemini 3.8 Flash）：图 4 的确切留出得分。Before 与 After 指 Gemini 的目标 RSI。两个阶段使用相同基准与划分；三个迁移条件共用 Opus 演化的起始 Harness。第一列给出领域与种子 Harness。编码领域以 Terminus-2 为种子的冷启动对应值为目标 RSI 前 18.18、后 19.39。加粗标出每行最高的最终分。

### E.3 源侧性能保持了多少？

在这次运行中，两个记忆条件都保持了更多源侧性能。图 8 中，完整 SIM 与问题记忆从共同的起始分 90.22 出发，最终分别停在 88.89 与 88.44；两者的最低源侧得分为 88.44，即下跌 1.78 分。Harness 迁移在第 2 轮跌到 86.67，最终为 87.56；冷启动从 85.78 开始，最终为 85.33。§4.4 把这条曲线与目标进展联系起来：两个记忆条件保持的源侧性能相近，而完整 SIM 在 TB4 上的改进更大。

图8：目标 RSI 期间的源侧得分（编码，TB2.1→TB4，Gemini 3.8 Flash）：以 AHE 为种子、每个条件各跑一次时，每一轮目标运行后所保留 Harness 的留出 TB2.1 得分（45 个任务、225 次 rollout，一次 rollout 折合 0.44 分）。三个迁移条件都从源演化 Harness 出发，冷启动从种子出发。（原文第24页）

### E.4 消融说明了什么？

#### E.4.1 只记录根因够吗？

从同一个演化 Harness 出发，完整 SIM 在全部十个设定中都高于「无记忆」与「只保留根因」的延续（表 5 与表 6）。这一比较在目标 RSI 全程检验各记忆条件，既覆盖继承来的信息，也覆盖目标阶段的更新（附录 C.3）。正文结果讨论的是领先幅度，以及只保留根因带来的好坏参半的效果（§4.2 与 §4.3.1）。

#### E.4.2 Harness 智能体的选择重要吗？

Opus 的得分更高，但在 Terminus-2 上留出集的领先幅度更小。表 7 在 TB2.1 源 RSI 期间把 Gemini 3.8 Flash 换成 Claude Opus 5.5 担任提议者与选择者：AHE 的留出得分用 Opus 时高 1.06 分，Terminus-2 高 0.05 分。本实验改变的是优化智能体；策略模型之间的迁移另在 §4.3 研究。

| Set | Seed | Gemini 3.8 Flash Before | Gemini 3.8 Flash After | Gemini 3.8 Flash Gain | Claude Opus 5.5 After | Claude Opus 5.5 Gain |
|---|---|---|---|---|---|---|
| Evolve | AHE | 86.82 | 90.45 | +3.63 | **91.23** | +4.41 |
| Evolve | Terminus-2 | 85.91 | 89.09 | +3.18 | **92.21** | +6.30 |
| Held-out | AHE | 85.78 | 90.22 | +4.44 | **91.28** | +5.50 |
| Held-out | Terminus-2 | 87.56 | 91.56 | +4.00 | **91.61** | +4.05 |

表7：在 TB2.1 上做源 RSI，分别以 Gemini 3.8 Flash 或 Claude Opus 5.5 作为 Harness 智能体（即提议并选择 Harness 修改的优化智能体）：种子 Harness 的得分，以及各自做完源 RSI 之后的得分。Gain 是相对 Before 的变化；每行中更高的 After 得分加粗。

## 附录 F 案例研究

我们把「固定设定内的改进」与「迁移之后的延续优化」区分开来。源 RSI 的案例展示对命令传输与解析的改动（§F.1）；CRSI 的案例追踪完成控制从 TB2.1 到 TB4 的演化（§F.2）、对比带 SIM 与不带 SIM 的延续（§F.3），并追踪追加到 P3 的新证据（§F.4）。这些是同一项编码迁移研究的不同侧面，而不是相互独立的重复实验。随后我们总结四个领域中的迁移模式（§F.5），并汇总它们对 SIM 的启示（§F.6）。详细的编码案例使用 Terminus-2 与 Gemini 3.8 Flash。

**案例中的证据。** 这些案例记录的是修改历史，而不是估计每处修改对最终得分的贡献。代码片段经过简化；展示出来的 SIM 记录保留其存储时的原文，包括截断部分。各字段的定义见附录 D.3。

### F.1 RSI 如何改进源 Harness？

这些例子都停留在源 RSI 内部：反馈指出一次 Harness 失败，随后导出一处修改，期间不涉及基准或策略的变化。传输案例包含一个实测的任务结果，解析案例则说明修复机制本身。

#### F.1.1 adaptive-rejection-sampler：不可靠的命令传输

**任务。** 用 R 实现自适应拒绝采样，写到 /app/ars.R，并带输入校验与测试。

**根因（c）。** 智能体把整个程序写进了一条约 22.8 KB 的 shell 命令，超过了本次运行报告的命令传输上限（约 16 KB）。这条命令从未执行，文件因此从未生成，验证器以 No ars.R file found 失败。

**修改（a）。** 现有 run_shell_command 工具背后的传输层，现在会把字面输入切成至多 2,048 字符的块，把回车等特殊键作为独立按键事件发送，并在发送失败时抛出错误而不是静默失败（简化后）：

```python
MAX_KEY_CHUNK_SIZE = 2048
def _tmux_send_keys(self, keys):
    cmds = []
    for key in keys:
        if key in SPECIAL_KEYS:  # key event
            cmds.append(f"{prefix} {quote(key)}")
            continue
        for chunk in self._split_key(key):
            cmds.append(f"{prefix} {quote(chunk)}")
    return cmds
```

**结果（o）。** 该任务的成功 rollout 从 5 次中的 1 次提高到 5 次中的 5 次。

#### F.1.2 gpt2-codegolf：脆弱的工具调用解析

**任务。** 用 C 写一个紧凑的 GPT-2 推理程序（/app/gpt2.c），加载权重、贪心解码，并在代码体积限制下用 gcc -O3 -lm 编译通过。

**根因（c）。** Terminus-2 期望一个 JSON 响应，其中 keystrokes 字段存放 shell 输入。当模型把含有未转义引号的 C 代码写进该字段时，例如：

```
"keystrokes": "...FILE *f = fopen("model.bin", "rb")
;..."
```

json.loads 会失败，命令被拒绝。该解析器本已能补上缺失的右花括号、剥掉周边文本，但无法修复字段内部的引号。

**修改（a）。** 增加一个仅在常规解析失败之后才运行的修复步骤：它把每个字符串字段真正的结束引号定位为「其后紧跟下一个预期键」的那个（对 keystrokes 而言即 "duration" 或右花括号），并转义它之前的每一个引号。

**结果（o）。** 这处修改为畸形调用增加了一条恢复路径；这次解析器修复没有报告修改后的任务成功率。它对模型输出格式的依赖在 §F.5.1 中讨论。§F.4 的 P3 记录涉及的是另一次提示词干预。

### F.2 CRSI 如何适配演化 Harness？

这个案例在策略固定的前提下，追踪完成控制跨越基准变化的过程。源 RSI 在 TB2.1 上构建了一个执行检查；目标 RSI 继承它，并在 TB4 上补充关于解的质量的检查。P5 记录源侧「过早宣告完成」的问题，P8 增加一条关于解的质量的目标侧诊断。两者都指向那个被继承的完成闸门，但属于彼此独立的条目，没有显式的「父/精化」链接。

#### F.2.1 源侧：执行验证的完成

**任务与评估接口。** 「配置一个 git 服务器，让我在自己机器上可以 git clone user@server:/git/server，提交 hello.html、推送，然后 curl http://server:8080/hello.html 显示 'hello world'。」智能体必须构建四个可组合的部分：位于 /git/server 的裸仓库、部署到 web 根目录的 post-receive 钩子、名为 user 的可 SSH 访问账户，以及监听 8080 端口的 HTTP 服务。验证器在容器之外运行，并以 user 身份通过 SSH 执行克隆，因此「本地能跑通」并不能证明对外可见的接口是对的。

**观察到的失败与诊断。** 在所描述的失败 rollout 中，智能体配置好了仓库、钩子与 web 服务器，把「I will set up login myself」理解为账户会由外部配置，因而从未创建 user。它用预先存在的 ubuntu 账户测试了整条流程，看到每条本地命令都成功，于是宣告 task_complete: true。随后 SSH 拒绝了这个不存在的用户，推送失败，页面返回 404。种子 Harness 抓不到这个问题，因为它的完成检查只是让模型复述自己的主张（自 terminus_2.py 简化）：

```python
if is_task_complete:
    if self._pending_completion:   # second claim
        return episode + 1         # terminate
    self._pending_completion = True  # first: ask again
    obs = self._confirmation_message(out)
```

而确认消息问的是意图、不是证据：「Are you sure you want to mark the task as complete? … If so, include "task_complete": true in your JSON response again.」根因是：结束一个 episode 是智能体的一项特权，不需要任何执行证据。

**Harness 干预。** 这次干预在 Harness 中引入了完成控制中间件。源 RSI 用三个被采纳的轮次构建了它：

| 轮次 | 修改 |
|---|---|
| r6 | 新建 execution_gating_interlock.py（137 行），接入 terminus_2.py：一台跨轮次状态机，当上一轮出现解析错误、或实际上没有命令被执行时拒绝宣告完成，最多拒绝三次。 |
| r8 | 还会拦截模拟的多轮文本、被丢弃命令块之后的截断输出，以及只执行了至多一条真实命令就宣告完成的情况（新增 terminus_json_plain_parser.py）。 |
| r10 | 在请求宣告完成的那一刻检测终端崩溃、断言失败、HTTP 404 与测试错误（两个提示词模板都新增）。 |

该联锁装置跨轮次跟踪执行情况，并使用四条拒绝路径（简化后）：

```python
def check_completion_attempt(self, cmds, out, pending=False):
    if self._consecutive_rejections >= self._max_rej:
        return False, ""  # never lock out a done task
    if self.detect_terminal_error(out):  # Case 0
        return self._reject(...)
    if pending:
        return False, ""
    ran = any(c.keystrokes.strip() for c in cmds)
    if self._last_turn_had_error and not ran:  # A
        return self._reject(...)
    if self._last_turn_discarded and not ran:  # B
        return self._reject(...)
    if self._total_executed <= 1 and not ran:  # C
        return self._reject(...)
    return False, ""
```

联锁装置负责执行这些完成检查，提示词中的提醒则提供额外引导。到源 RSI 结束时，该文件已增长到 275 行。

**所报告的任务结果。** 在 configure-git-webserver 上，成功 rollout 从 5 次中的 1 次提高到 5 次中的 5 次。同一次 P5 干预也把 circuit-fibsqrt 从 5 次中的 1 次提高到 5 次中的 5 次：该任务用 /app/sim.c 测试斐波那契电路与平方根电路（含大整数输入），此前智能体在命令失败后就停了下来。这是同一次源侧干预带来的两个任务结果。

三次源侧尝试都留在 P5 里（图 9）。有两个目标提议引用了 P5，但都未被采纳，因此没有目标尝试被追加到该条目。

```json
{ "id": "P5",
  "name": "premature completion without execution verification",
  "opened_round": 6,
  "attempts": [
    { "round": 6, "sample": "s2", "accepted": true, "domain": "coding_enriched",
      "what": "Implemented ExecutionGatingInterlock in Terminus2 to intercept premature
               task completion attempts when previous commands failed to execute
               (e.g. on unescaped JSON parse errors) or when no commands wer...",
      "files": "execution_gating_interlock.py, terminus_2.py",
      "predicted": ["circuit-fibsqrt", "configure-git-webserver"],
      "fixed":    ["circuit-fibsqrt", "configure-git-webserver"],
      "missed": [], "passed": 49, "total": 60 },
    { "round": 8, "sample": "s1", "accepted": true, "domain": "coding_enriched",
      "what": "Intercept premature completion when LLM generates multi-turn simulated
               text or output-length truncations with unexecuted discarded command
               blocks or completes with trivial session execution (<=1 comma...",
      "files": "execution_gating_interlock.py, terminus_2.py,
                terminus_json_plain_parser.py +1 more",
      "predicted": ["constraints-scheduling"],
      "fixed":    ["constraints-scheduling"],
      "missed": [], "passed": 45, "total": 60 },
    { "round": 10, "sample": "s1", "accepted": true, "domain": "coding_enriched",
      "what": "Enhance ExecutionGatingInterlock in Terminus2 to detect active terminal
               crashes, assertion failures, HTTP 404s, and test errors when task
               completion is requested, prevent immediate termination when co...",
      "files": "execution_gating_interlock.py, templates/terminus-json-plain.txt,
                templates/terminus-xml-plain.txt +1 more",
      "predicted": ["configure-git-webserver", "protein-assembly", "train-fasttext"],
      "fixed":    ["configure-git-webserver"],
      "missed":   ["protein-assembly", "train-fasttext"],
      "passed": 47, "total": 60 } ] }
```

图9：被带入目标运行记录的 SIM 条目 P5（what 字段按存储时的状态截断）。三次尝试全部属于源侧轮次，由 domain 字段 "coding_enriched" 标识。（原文第28页）

#### F.2.2 目标侧：可行性与解的质量

**任务与评估接口。** 为 /app/layout_spec.json 中描述的九条光波导布线，并把航点路径写入 /app/routing_result_1.json。每条路径都必须从精确的起点走到精确的终点，使用半径 50 µm 的 90 度弯与合法的 s 弯，保持在板内、避开障碍物净空区与自相交，并在不同网络之间保持最小间距。得分为所有网络上「带权布线代价之和」的相反数。任务自带可行性检查器 check_routing.py，它只回答约束是否被满足，而奖励是一个代价函数——解可能通过全部检查却仍然得分很差。

**观察到的失败与诊断。** 演化 Harness 里带着源侧联锁装置，完好且已接入。在这个任务上，智能体产出一条可行布线，写出输出，运行 check_routing.py 并看到通过，没有遇到终端错误，于是请求宣告完成。四条拒绝条件一条都没触发：命令执行了、没有解析错误、没有内容被丢弃、也没检测到可见的终端失败，于是闸门放行。目标侧的失败由此引出一个关于「完成所需证据是否充分」的问题：

| | 源侧闸门所问 | 本任务还需要 |
|---|---|---|
| 问题 | 已经执行得足够多、整个流程不至于明显失败了吗？ | 这个可行的解好到可以停止改进了吗？ |
| 证据 | 执行活动、错误、崩溃 | 相对可达界的客观指标值 |

**Harness 干预与安装后的行为。** 目标 RSI 保留了状态机与有界拒绝，并在若干目标条目下把该组件从 275 行扩展到 437 行。归因于这一缺陷、并在目标第 2 轮被采纳的改动，增加了一个检测器：识别「只检查约束、却又顺带打印分数」这一特征，并在确认步骤把命中结果转成一条提示（简化后）：

```python
PATTERNS = [re.compile(
    r"(?:ALL CHECKS PASSED|ASSERTIONS PASSED"
    r"|CONSTRAINTS? SATISFIED).*?"
    r"(?:score|cost|loss|metric)\s*[:=]\s*[-+]?\d+",
    re.I | re.S), ...]
def detect_optimization_feasibility_notice(cls, out):
    if any(p.search(out[-4000:]) for p in PATTERNS):
        return ("[ExecutionGatingInterlock NOTICE]: "
                "passing constraint checks (e.g. "
                "check_routing.py) only proves "
                "FEASIBILITY, "
                "NOT OPTIMALITY ... compare your current "
                "score against theoretical bounds ...")
```

完成前检查清单也加了对应条款，要求智能体确认自己「没有停在第一个可行解上」，并且「已针对理论界量化了自身的次优差距」。目标第 4 轮，被采纳的候选加入了第五条拒绝路径：一旦检测到「带指标值的可行性输出」，就阻断一次宣告完成。后续修改改变了这一行为：最终 Harness 保留了 check_completion_attempt 的源侧主体及其四条拒绝路径；喂给 Case 0 的错误模式被扩展，以捕获「自报不可行」的交付物（例如 "route_feasible": false）。因此最终行为是：阻断「自报不可行」，并对可能的次优发出警告；SIM 保留了早先那次阻断尝试及其结果。

**所记录的任务结果。** 记录下来的预测与结果，把「预期的修复」与「实测结果」区分得很清楚：

| 尝试 | 预测会修复的任务 | 实际修复 |
|---|---|---|
| P8，第 2 轮 | photonic-waveguide-routing、production-planning | 无 |
| P8，第 4 轮 | photonic-waveguide-routing、production-planning | 无 |

两次尝试都被采纳了，但都没有修复它们针对的任务；这些预测在 P8 中仍标记为未兑现（图 10）。本案例说明的是适配与记忆更新；目标侧的整体性能另在 §4.2 报告。

| | P5（继承自源侧） | P8（目标侧原生） |
|---|---|---|
| 来源（Provenance） | coding_enriched，源第 6 轮 | tb4，目标第 2 轮 |
| 缺失的证据 | 执行未发生，或执行未成功 | 执行成功了，但解只是可行 |
| 被采纳的预测 | 3 / 3，全在源侧 | 2 / 2，全在目标侧 |
| 已兑现的预测 | 4 / 6 | 0 / 4 |
| 诊断开启于 | 源 RSI | 目标 RSI |
| 组件 | 联锁装置被创建 | 联锁装置被扩展 |
| 完成行为 | 四条源自源侧的拒绝路径 | 最终 Harness 中的最优性建议 |

这两条条目把继承来的执行问题与新的解质量问题区分开来。

```json
{ "id": "P8",
  "name": "premature termination on feasible but suboptimal solutions
           in optimization tasks",
  "opened_round": 2,
  "attempts": [
    { "round": 2, "sample": "s3", "accepted": true, "domain": "tb4",
      "what": "Add objective optimality vs constraint feasibility guidelines to prompt
               templates and enhance ExecutionGatingInterlock with optimality audit
               checklist and feasibility score notice to prevent premature...",
      "files": "execution_gating_interlock.py, templates/terminus-json-plain.txt,
                templates/terminus-xml-plain.txt +1 more",
      "predicted": ["photonic-waveguide-routing", "production-planning"],
      "fixed": [],
      "missed":   ["photonic-waveguide-routing", "production-planning"],
      "passed": 5, "total": 33 },
    { "round": 4, "sample": "s4", "accepted": true, "domain": "tb4",
      "what": "Active optimization gating and terminal error precision in
               ExecutionGatingInterlock: enforce completion interception when
               constraint feasibility outputs with score/metric are detected
               without verified...",
      "files": "execution_gating_interlock.py",
      "predicted": ["photonic-waveguide-routing", "production-planning"],
      "fixed": [],
      "missed":   ["photonic-waveguide-routing", "production-planning"],
      "passed": 10, "total": 36 } ] }
```

图10：SIM 条目 P8，由目标 RSI 在第 2 轮开启（what 字段按存储时的状态截断）。其来源字段 domain: "tb4" 表明它属于目标运行内部。第 4 轮那处修改先被采纳、后来又被改动，其记录仍留在 SIM 中。（原文第29页）

**记忆在 Harness 变化的同时保存了历史。** P5 保存了源侧联锁装置为何被引入；P8 记录了为评估解的质量而做的目标尝试，其中也包括那次后来被改动的阻断尝试。两者合在一起，保住了最终 Harness 里已经看不到的理由与结果。

### F.3 SIM 如何引导延续？

**带 SIM 的那次运行在继承来的闸门上追加了目标检查。** 图 11b 追踪从 TB2.1 继承下来的完成闸门，把 §F.2 描述的延续与「同一 Harness、不带 SIM」的运行作对比。第 2 轮，带 SIM 的提议者读到该闸门的源侧条目 P5——它诊断的是「缺少执行验证的过早宣告完成」。提议者保留闸门，并要求智能体在宣告完成之前把自己的得分与理论界作对照：满足约束只证明了可行性，更优的解可能仍然存在。后续修改又加入了对规格参数与生命周期状态的检查。

**不带 SIM 的运行则把同一个闸门改了四次，其中两次是为了修复完成死锁。** 它第 3 轮的理由把闸门与死锁都归到第 1 轮名下，尽管这个闸门其实继承自源 RSI。

| 目标增益（分） | 不带 SIM（Harness 迁移） | 带 SIM（完整 SIM） |
|---|---|---|
| Coding / AHE | +2.43 | +6.67 |
| Coding / Terminus-2 | +0.00 | +2.43 |
| Text / NoMemory | −0.40 | +2.20 |
| Text / FewShotAll | +1.20 | +5.00 |
| Workspace | +10.14 | +12.96 |
| Engineering | +3.48 | +7.83 |

| 轮次 | 带 SIM：同一闸门 + 源侧记录 | 不带 SIM：同一闸门，无记录 |
|---|---|---|
| R1 | Gate + 规格参数审计 | Gate：更严的错误模式 |
| R2 | Gate + 可行 ≠ 最优 检查 | Prompt：配置完备性 |
| R3 | tmux 传输修复 | Gate：修复完成死锁 |
| R4 | Gate + 可行性分数阻断（P8） | — |
| R5 | Gate + 耦合字段与测试套件审计 | Gate：跨轮次测试失败锁存 |
| R6 | Gate + 防御式函数契约 | — |
| R7 | Gate + 不可行标记 | Gate：修复被锁存错误导致的死锁 |
| R8 | — | — |
| R9 | Gate + 生命周期状态检查 | — |

图11：带 SIM 与不带 SIM 的目标增益和修改历史。(a) 图 3 中六组跨数据集目标增益，均以共同的源演化起始 Harness 为基准测量。(b) Terminus-2（TB2.1→TB4）在目标第 1–9 轮被采纳的修改。两次运行继承同一个 Harness 与同一个完成闸门。「Gate +」表示增加一项检查，— 表示该轮没有被采纳的修改；第 10 轮未列出。第 4 轮的 P8 阻断后来被改动（§F.2）；第 5、6 轮扩展的是 P3（图 12）。（原文第30页）


### F.4 SIM 如何扩展已有记录？

图 12 给出图 11b 中第 5、6 轮闸门修改背后的记录。源 RSI 诊断出「交付物内部正确、却违反验证器所检查的外部 schema 或 API 契约」这一不一致。源侧第 4 轮的修改加入了系统提示指引，在四个预测任务中修复了一个，剩下三个未解决。目标 RSI 在同一条诊断下追加了两次尝试：第 5 轮扩展出 schema 交付物与测试审计，第 6 轮加入防御式契约检测器。它们分别在两个预测任务中修复 0 个与 1 个。因此，P3 在累积来自不同干预、不同设定的证据的同时，始终只保留一条诊断。

| 阶段 | 被采纳的修改 | 记录的结果 |
|---|---|---|
| 源侧，TB2.1 第 4 轮，继承下来 | 系统提示。执行与验证指引：交付物完整性、schema 符合性、防御式 API 兼容性、评估卫生，以及用显式不变量检查取代静默抑制。 | 4 个中修复 1 个。gpt2-codegolf 被修复；protein-assembly、torch-pipeline-parallelism 与 train-fasttext 仍未解决。 |
| 目标，TB4 第 5 轮，追加 | 验证层。在完成联锁与提示词模板中加入 schema 交付物条款；把检查清单扩展到程序化断言与测试套件审计。 | 2 个中修复 0 个。atrx-vep-crispr 与 intrastat-meldung 都未被修复。 |
| 目标，TB4 第 6 轮，追加 | 验证层。在完成检查清单中加入防御式契约检测器。 | 2 个中修复 1 个。embedding-drift-monitor 被修复；biped-contact-dynamics 仍未解决。 |

> 译注：该表顶部标注「SIM 条目 P3 ｜ 策略：Gemini 3.8 Flash」，根因为「交付物可能内部正确却违反验证器的外部契约：schema、耦合属性、API 签名或数据划分卫生」。

图12：跨越源 RSI 与目标 RSI 的 SIM 条目 P3。源侧尝试兑现了四条「修复任务」预测中的一条；目标第 5、6 轮分别兑现两条中的零条与两条中的一条。所有尝试在同一条根因假设下保留各自的结果与来源信息，包括未兑现的预测。（原文第32页）

### F.5 哪些东西跨数据集与模型迁移？

表 8 总结了哪些机制被直接复用、经调整后复用、继承并扩展，哪些又依赖于目标设定。各领域的摘要把「有记录的改动」与「限制复用的条件」区分开：一个被保留下来的机制可能一直处于未激活状态。它们把编码案例推广到其他领域，但不把每个机制都当成一次独立的 SIM 消融。

| 领域 / 变化 | 直接复用 | 经调整后复用 | 继承并扩展 | 依赖于目标设定 |
|---|---|---|---|---|
| Coding / 数据集 | shell、终端与进程层 | 粘贴缓冲区传输（按键归一化、前台检测） | 完成契约，带新的目标谓词 | 源侧完成谓词；拒答处理（未激活） |
| Coding / 模型 | 终端与进程层；联锁计数 | — | 生命周期控制，拦截启发式经重标定 | 针对某个模型输出调过的解析器修复 |
| Text cls. / 数据集 | BM25 索引与检索器；查询清洗 | top-k、分数过滤与类别配额（常数经重标定） | 多模板路由骨架 | 数据特定的后处理（SMILES 归一化） |
| Text cls. / 模型 | 索引；查询清洗 | 检索预算（按模型容量重新调参） | 路由骨架，rubric 被重写 | 输出 schema 与解码契约 |
| Workspace / 数据集 | final_answer 之前的软闸门 | 证据探测（文件系统 → 调用历史） | 截断上限与上下文预算 | 评估器特定的注册假设；子串启发式 |
| Workspace / 模型 | 系统提示注入流水线 | 按预算触发的稀疏干预 | 带反例的 rubric 分类法 | 针对某个模型失败率或 API schema 的标定 |
| Engineering / 数据集 | 中央工具调用拦截点 | 交付物检查 → 连续检查点 | 上下文缓冲与截断预算 | 无 SIM 时的提示词指引（已被回退） |
| Engineering / 模型 | 交付物观测层；重执行检查 | 干预调度（时间与步数阈值） | 可组合的软闸门谓词 | 干预强度；环境特定的旁路 |

表8：跨数据集与模型的机制复用。最后一列既包含未激活或已被移除的组件，也包含在新设定下需要重新评估的假设与启发式。破折号表示没有列出任何机制。支撑案例见 §F.5.1–§F.5.4。

#### F.5.1 编码

**源 RSI 改进了执行、解析与完成。** 演化出的工具层在超时之后保留 stdout 与 stderr、检查后台进程及其退出码、找回放错位置的产物，并通过粘贴缓冲区发送长命令（§F.1）。Terminus-2 的解析器会先尝试修复畸形 JSON 再拒绝它，并能识别安全拒答。完成控制要求在接受「完成」主张之前先看到证据：AHE 的中间件在智能体没有调用工具就停下时强制继续，Terminus-2 的跨轮次联锁则在命令未执行或出错之后阻断完成（附录 F.2）。

**核心执行处理在 TB4 上被保留。** 命令执行例程随共享的容器与终端接口一起迁移过来，而会话检查则按下文方式适配。所记录的那次冷启动运行在八轮之内没有重新发现工具层的这些改动；十轮之后它有一个更大的解析器，却并不比继承来的 Harness 更好。

**粘贴缓冲区检查适配了 TB4。** TB4 暴露出 TB2.1 上没有的失败：特殊键序列必须先归一化才能让中断生效；还必须识别前台进程，以免把正在运行的命令误判成卡住的会话。粘贴缓冲区的结构保留了下来，检查针对这些新的目标失败做了调整。

**完成检查补上了目标侧判据。** 两个继承来的 Harness 都保留了完成控制，同时修订了在 TB4 上所需的证据。附录 F.3 追踪被采纳的修改，附录 F.2 给出任务层面的证据与 P5/P8 记录。已经不再触发的源侧谓词会被删掉，而不是重新调参。两个分支还都在第一轮加入了一条由剩余步数预算触发的提醒——这是源侧并不需要的目标特定机制。

**拒答处理保持未激活。** 拒答处理被继承了下来，但在 TB4 上没有可触发的任务。因此它的存在本身既不能证明迁移有收益，也不能证明有损失。

**解析器修复依赖策略模型。** Opus 与 Gemini 演化出的 Harness，其终端与进程结构几乎完全一致，迁移后被原样保留。解析器修复针对的则是模型特定的输出错误：未转义的控制字符、非法转义与被截断的响应。每处修复都需要针对目标模型的输出重新检查。完成控制同样保留了「已执行命令数」「被丢弃块数」「连续拒绝次数」的计数，同时对「模拟执行」与「过早完成」的检查做了重标定。目标运行还加入了源 RSI 中没有的格式约束与分步引导。

#### F.5.2 文本分类

**源 RSI 构建了结构化检索。** 记忆写入从「不保留」（NoMemory）或「非结构化存储」（FewShotAll）转为可检索的索引：在词、字符 n-gram 与化学式 n-gram 上做多粒度 BM25，之后又扩展出基于类别的候选池、难负例错误索引与类别原型中心性。提示词组装把检索限制在 BM25 分数为正的前八个样本，检索前先剥掉查询中的基准套话，并选出对比式、类别均衡的示例。后处理会归一化数据特定的格式，例如 USPTO-50k 的 SMILES 字符串——开放式词表生成要求精确匹配。

**检索在阈值调整后存活下来。** 目标套件改变了输入类型与标签空间。BM25 索引与检索器类保持完整，检索常数被重标定，查询清洗为新数据集加入了分隔符。路由结构被保留，rubric 与示例针对目标重写。有了 SIM，目标 RSI 还加入了平滑的类别配额与对比式排序；类别均衡作用于目标的有限标签集合，而不是源侧的开放式词表输出。

**SMILES 归一化保持未激活。** 源 RSI 用到的 SMILES 归一化在目标套件上仍然未激活，因为后者不再使用该格式。那次冷启动运行则自行发展出相关性门控检索与有界上下文。

**索引迁移了，输出规则变了。** 四次运行中有三次从不同的起始 Harness 出发演化出 BM25 索引，并使用适合输入的特征，例如面向 SMILES 的化学 n-gram 与面向中文法律文本的字符二元组。索引与查询清洗依赖输入数据，可以跨模型迁移；top-k 之类的检索预算需要重新调参。输出规则更依赖策略行为：answer-first 这一 schema 针对的是 Gemini 被截断的推理。目标 RSI 对继承 rubric 的重写在 Banking77 与 GoEmotions 上比在 SciTail 与 TweetEval-Hate 上更彻底。

#### F.5.3 智能体工作区

**源 RSI 增加了输出处理与审计。** 超长工具输出通过「首尾截断」保留下来，配额分别提高到三倍与五倍。final_answer 之前的一次性审计闸门可以追加工具消息，并把策略送回循环。交付物审计器为该闸门提供候选输出目录中的文件名与文件大小。

**终止闸门在 rubric 变化后仍然存活。** 源 RSI 与一次冷启动目标运行各自独立地在同一个提前返回分支前加入了一条工具消息，谓词与消息内容并不相同。目标侧的闸门只在三个条件同时满足时触发：没有登记任何交付物、代码执行期间确实写过文件、且闸门此前未触发过；第二个条件保证纯对话任务不会被拦截。这个插入点依赖 ReAct 循环，在评估 rubric 改变之后依然可用。

**注册检查取代了文件系统探测。** 源侧的探测采样文件系统，而目标侧的失败来自调用历史：文件在磁盘上创建了、却从未通过 write_file 注册。因此目标检查使用工具调用历史而非文件系统探测。目标侧把这个检查分三级、在单次执行中逐级升级：检测到保存文件时给出建议性提示；步数预算用掉 75% 仍未注册时给出强制指令；最后在 final_answer 处做条件性阻断。

**注册检查依赖评估器。** 该检查假设评估器认可通过 write_file 注册的文件；如果评估器直接读取输出目录，就需要重新考虑。它对工具参数做的子串匹配（例如 /tmp/、.docx 或 savefig）也依赖参数的书写格式。

**提示词基础设施跨模型迁移。** Opus 的源运行加入了可编辑的系统提示指引与一个六级严重度分类法（配反例），控制流与工具执行保持不变。注入机制用的是消息结构，而分类法描述的是那个并未改变的评估器。Gemini 的冷启动运行走了另一条路：在步数预算 80% 处发出提示，要求它补上待填字段，好在 final_answer 之前产出交付物；这条曲线之后七轮都没有带来提升。这类干预的时机与措辞取决于策略本身的行为。

#### F.5.4 工程设计

**源 RSI 增加了设计与验证指引。** 源运行加入了关于解析式计算、自包含交付物、工具失败恢复，以及在宣告完成前重读已写文件的提示词指引。它还导入了一个语法解析器与一个工具注册表，但在源 RSI 期间并不调用它们。

**目标 RSI 扩展了检查与上下文预算。** 工具注册表的导入在源 Harness 中未被使用，却成了 Harness 迁移目标运行的入口——它借此在注册表调用处强制实施集中式输出截断。三次目标运行各自独立地提高了共享的上下文常数：输出 token 上限、首尾长度与摘要触发阈值。完整 SIM 的目标运行把源侧的一次性生成后检查改造为检查点协议：把得分超过基线的中间产物写到磁盘，使其免于不明不宣的超时。冷启动目标运行所保留的修改只限于提示词改动：从评估脚本重建目标函数、在交付物中嵌入自调优优化代码，以及用回退到基线实现的方式对输出做钳制。

**这次追踪中，SIM 保留了源侧指引。** Harness 迁移的目标运行继承了源侧指引，却在第一轮把它们回退成种子提示词；完整 SIM 的目标运行则全程保留并扩展它们。这一对运行保留了相似的代码结构，差别在于是否保住继承来的指引。

**交付物检查在模型变化后存活。** 一个独立于模型输出记录交付物状态的追踪器，无需重构即可迁移；另一个在「交付物被改动却未重新执行」时阻断 final_answer 的检查也原样迁移。预算提示在 Opus 运行中表现为墙钟触发（每 600 秒一次、至多三次），在 Gemini 运行中则表现为步数预算比例（0.8 与 0.75）。两者都在 final_answer 之前使用该闸门，检查的状态变量却不同。所记录的零分率在 Opus（0.09%）与 Gemini（4.49%）之间差别很大，因此干预阈值需要按策略逐一检查。对缺失沙箱二进制文件的处理程序，在环境已完整配置时保持空闲。

**接口解释了观察到的大部分复用。** 跨这些案例来看，基准变化改变的是「完成所需的证据」，模型变化改变的则是「Harness 如何应对策略失败」。基准固定时，模型变化不会动成功判据，但可能要求不同的检测与引导。稳定的接口有利于复用；输出修复与干预阈值则需要对照目标设定逐一检查。

### F.6 这些案例告诉我们 SIM 的什么？

这些案例提示了 SIM 在延续 Harness 优化中的四种角色。

**更早的理由决定了该保留什么。** 在工程领域，带 SIM 的运行保留并扩展了继承来的指引，而只保留 Harness 的延续把它回退掉了（§F.5.4）。记录「某处修改为什么被做出」，让优化器有了评估它是否仍然相关的依据，而不只是看它是否还在继承来的 Harness 里。

**可迁移的理由可能需要不同的实现。** 编码运行继承了同一个完成闸门，但带 SIM 的那次运行把它扩展为检查目标特定的需求（§F.3）。「需要完成证据」这一点迁移了过来，而「什么才算充分的证据」变了。这正说明：更早的推理可以引导适配，而不必把源侧实现当成固定不变。

**新结果为既有诊断补上证据。** P3 把一条源侧诊断与后续的目标干预及其结果连起来（§F.4）。把这些尝试放在一起，后续轮次就能查看：试过哪些补救手段、在什么设定下、还有哪些预测没有兑现。可复用的经验包含的是诊断背后的证据，而不只是诊断的名字。

**修改被替换之后，经验依然可用。** 后续修改改变了行为之后，P8 仍然保留着当初被采纳的那次阻断尝试及其未兑现的预测（§F.2）。只看最终 Harness 会漏掉这段搜索历史；SIM 让这次尝试、它的诊断与它未兑现的结果在 Harness 变化过程中始终在一起。
