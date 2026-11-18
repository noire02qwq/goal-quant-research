# 编码智能体能否在不遗忘的前提下维持持续演化？（Can Coding Agents Sustain Continual Evolution without Forgetting?）

> 来源：https://arxiv.org/abs/2611.03219
> 原文：docs/papers/arXiv-2611.03219.pdf
> 翻译日期：2026-11-18 ｜ 范围：全文 ｜ 方式：机器翻译初稿，未经人工校对
> 引用于：docs/literature/W6-self-evolution-rsi.md

## 目录

- 摘要
- 1 引言
- 2 问题定义
- 3 实验设置
- 4 实验结果
- 5 相关工作
- 6 结论
- 参考文献（从略）
- 附录 A 实现细节
- 附录 B 数据集设置的讨论与案例研究

## 摘要

近年来，Harness 自演化已成为提升智能体性能的一个重要范式。已有研究表明，演化智能体 Harness 能在不修改基础模型参数的情况下有效增强智能体能力。我们发现，现有方法基本都只在单一任务上研究智能体演化。而在实践中，编码智能体可能需要随时间处理多种任务类型。一个智能体 Harness 能否跨多个任务持续演化而不遭受灾难性遗忘，至今仍是一个重要的开放问题。

本文通过一项关于持续 Harness 自演化的综合实证研究来考察这一开放问题。我们把三个软件工程任务数据集组织成六个不同的演化方向，并采用两种有代表性的 Harness 演化方法沿这些方向执行持续演化。实验结果表明，在后续数据集上的演化会严重损害在先前已见数据集上的性能。

例如，使用 DeepSeek-V4-Flash-0731 时，Meta-Harness 在演化后把 SWE-Bench 上的性能提升到 94.0%；然而，在 FeatureBench 上进一步演化之后，到第五轮时它在 SWE-Bench 上的性能已跌至 32.0%，对应 66% 的相对下降。最后，基于我们的实验发现，我们提炼出若干洞见，为智能体 Harness 的持续自演化提供方向。代码见 https://github.com/THU-Agent/continual-harness-evolution。

## 1 引言

编码智能体正越来越多地被用于软件工程任务（Liu et al., 2024），例如问题解决、功能添加与测试生成（Yang et al., 2024; Wang et al., 2025; Tao et al., 2024; Bouzenia et al., 2025）。一个编码智能体通常由一个基础模型和一个智能体 Harness 构成（Ning et al., 2026; Yang et al., 2024）。Harness 协调模型、工具与环境之间的交互，从而影响智能体如何感知任务信息、调用工具与执行任务。不同的 Harness 会显著影响智能体性能：在我们的实验中，固定基础模型时，不同 Harness 在 SWE-Bench 上的成绩相差悬殊，从 82.0% 到 96.0% 不等。

为了改进智能体 Harness，近期研究探索了 Harness 自演化——它让智能体通过分析轨迹、识别策略、并把这些洞见用于自动改进自己的运行时系统，从而从自身的执行经验中学习（Jiang et al., 2026）。近期已提出不少方法，在智能体能力上展示了可观的提升（Agrawal et al., 2026; Zhang et al., 2026c; Zhou et al., 2025; Chhikara et al., 2025; Zhang et al., 2026b; Xia et al., 2026; Lin et al., 2026; Lee et al., 2026; Zhang et al., 2026a; Chen et al., 2026）。例如，AHE（Lin et al., 2026）经过十轮演化，把种子 Harness 在 Terminal-Bench 2 上的成绩从 69.7% 提高到 77.0%。

然而，现有 Harness 自演化研究主要聚焦于针对单一类任务独立地演化 Harness。在实际场景中，编码智能体被期望能处理各种软件工程任务。Stack Overflow 开发者调查 2026 报告称，72.9% 的开发者用 AI 智能体编写、编辑或生成代码，62.2% 用于调试或排查故障，50.6% 用于编写或维护测试（Stack Exchange Inc., 2026）。在软件开发中，用户可能先让编码智能体添加一个新功能，稍后又让它编写测试文件。

受这一观察启发，我们提出持续 Harness 自演化（continual harness self-evolution），它指的是跨不同任务类型相继地演化同一个 Harness，与针对单一任务独立演化 Harness 相对。然而，据我们所知，现有工作尚未探索过编码智能体 Harness 跨不同任务种类的持续演化。

为填补上述研究空白，我们对编码智能体的持续 Harness 自演化做了一项系统研究。本研究旨在回答以下研究问题：

**RQ1：现有 Harness 自演化方法能否跨多个软件工程任务维持持续演化？** 持续 Harness 自演化要求智能体在每个新任务上不断进步，同时不丢失它在先前任务上获得的能力。为检验现有方法是否满足这一要求，我们构造了一个持续演化设置：Harness 在一系列软件工程任务类型上演化，而不是在单一任务上演化。具体而言，我们在三个软件工程数据集上评估两种有代表性的 Harness 自演化方法——AHE（Lin et al., 2026）与 Meta-Harness（Lee et al., 2026）：用于代码修复的 SWE-Bench（Jimenez et al., 2024）、用于测试用例生成的 SWT-Bench（Mündler et al., 2024）、以及生成功能特性的 FeatureBench（Zhou et al., 2026）。

每次持续演化实验构成一个两阶段的任务序列：Harness 先在较早的数据集上演化，随后在较晚的数据集上继续演化，使我们能够追踪随着演化推进，较早任务上的性能如何变化。结果揭示了持续 Harness 自演化过程中的严重灾难性遗忘，如图 1(a) 所示。例如，Meta-Harness 把 SWT-Bench 提升到 100.0%，但在 FeatureBench 上继续演化之后，它在 SWT-Bench 上的成绩跌到 62.0%。

**RQ2：Harness 中灾难性遗忘的根因是什么？** 如图 1(b) 所示，为理解持续 Harness 自演化为何会导致灾难性遗忘，我们收集了 520 多条智能体轨迹，并人工分析持续 Harness 自演化期间引入的 Harness 修改。我们把这些修改归入三类主要的 Harness 级冲突：验证冲突、工作流冲突与预算策略冲突。消融实验表明，不同冲突类型对智能体性能的影响差别显著。我们希望这些发现能启发未来能够感知此类冲突的自演化方法的设计，并呼吁更多关注这一被忽视却至关重要的问题。

本工作的主要贡献如下：

- ❶ 受编码智能体在多样任务中实际使用的启发，我们提出 Harness 持续自演化问题，并把灾难性遗忘识别为一个关键挑战。
- ❷ 我们在持续演化条件下评估现有 Harness 自演化方法，揭示了对先前已获能力的灾难性遗忘。
- ❸ 我们人工分析智能体轨迹，识别出导致遗忘现象的关键 Harness 级冲突。

图 1. 我们关于持续 Harness 自演化研究的总览。(a) RQ1：持续演化中的灾难性遗忘——Mini-SWE-Agent 的提示词与工具，520 条执行轨迹，3 个基准 · 6 个持续演化方向（SWE、SWT、Feature），沿迭代 D0 → D1 做持续演化，比较「对新任务的适应」与「在先前任务上的灾难性遗忘」，涉及 2 种 Harness 演化方法（AHE 与 Meta-Harness）。(b) RQ2：Harness 冲突分类——工作流（任务求解流程）、验证（交付物门控，区分 source fix 与 test-only）与预算（超时 / 收敛）三类冲突。（图内文字为示意性标注，原文此处以图形方式排版。）
## 2 问题定义

一个编码智能体由一个基础模型和一个智能体 Harness 构成，后者协调它与软件环境的交互（Ning et al., 2026; Yang et al., 2024）。近期工作探索了 Harness 自演化：在保持基础模型参数固定的前提下，根据执行经验修改 Harness 来提升智能体能力（Jiang et al., 2026）。形式化地，一个智能体表示为 A = ⟨M, H⟩，其中 M 表示基础模型，H 表示 Harness。给定从数据集 D 收集的执行轨迹 T，一个自演化方法 Ω 把 Harness 更新为 H′ = Ω(H, T)。

在实际场景中，编码智能体可能需要跨不同的软件工程任务类型演化，例如问题解决、功能添加与测试生成。我们把这一设置称为持续 Harness 自演化。给定一个有序的数据集序列 D = (D0, D1, …, DK)，其中每个数据集代表一类软件工程任务，Harness 按如下方式被反复更新：

```text
H(i+1) = Ω ( H(i), T(i) )，                                               （1）
```

其中 T(i) 表示从 Di 的任务收集的执行轨迹，i = 0, …, K。

持续 Harness 自演化的一个核心挑战，是在适应新任务类型的同时，不大幅损害先前已遇到任务上的性能。这一挑战与持续学习中的稳定性-可塑性困境相关（Carpenter & Grossberg, 1987; Yang et al., 2026）。当对新经验的适应损害了先前获得的能力时，就可能发生灾难性遗忘（Kirkpatrick et al., 2016）。本文把灾难性遗忘定义为：在目标任务上进一步演化 Harness 之后，源任务上出现的大幅性能下降。

理想情况下，持续 Harness 自演化应当在提升每个新数据集上性能的同时，保持先前已遇到数据集上的性能。具体而言，在 Di 上演化之后得到的 Harness Hi+1 不应损害数据集 Dj 上的性能，其中 0 ≤ j < i ≤ K：

```text
Eval(H(i+1), D(i))  >  Eval(H(i), D(i))                                  （2）

Eval(H(i+1), D(j))  ≥  Eval(H(j+1), D(j))                                （3）
```

这里 Eval(H, D) 表示使用 Harness H 与固定基础模型的智能体在数据集 D 上的性能。第一个条件刻画对当前任务的适应，第二个条件刻画对先前任务性能的保持。

为量化灾难性遗忘，我们在先前数据集上度量绝对与相对的性能下降：

```text
Δ_forget  = Eval(H(j+1), D(j)) − Eval(H(i+1), D(j))                      （4）

ρ_forget  = [ Eval(H(j+1), D(j)) − Eval(H(i+1), D(j)) ]
            ─────────────────────────────────────────────                  （5）
                    Eval(H(j+1), D(j))
```

## 3 实验设置

在第 2 节定义的问题之上，我们开展了持续 Harness 自演化研究。本节介绍实验中使用的数据集、编码智能体框架、自演化方法与实现细节。

### 3.1 数据集

我们研究不同类型的软件工程任务之间的持续 Harness 自演化，涵盖代码修复、测试用例生成与代码生成。

**SWE-bench Verified**（Jimenez et al., 2024）是软件工程中最广泛使用的代码修复基准之一。它包含 500 个高质量实例，来自从 GitHub 收集的真实软件问题，并经人工标注者手工验证。每个任务的目标是通过修改相应仓库来定位并解决底层问题。

**SWT-Bench**（Mündler et al., 2024）关注评估智能体为真实软件问题生成测试用例的能力。每个任务向智能体提供源代码和一份从 GitHub 收集的问题报告，所生成的测试应当在原始实现上失败、而在应用相应修复之后通过。值得注意的是，所有任务提示词原本遵循完全相同的句子结构。为避免潜在捷径、并提高与其他数据集的一致性，我们对其做改写（paraphrase）而保留语义，使任务之间的表层形式变得多样，详见附录 B。

**FeatureBench**（Zhou et al., 2026）评估智能体在真实软件仓库中实现新功能的能力。给定一份功能需求及其接口描述，智能体需要实现所要求的功能，并把实现产物放进 testbed 目录。评估同时考虑 fail-to-pass（F2P）与 pass-to-pass（P2P）测试：F2P 测试检验新功能是否被正确实现，P2P 测试则验证改动没有破坏既有功能。

受资源限制，我们从每个数据集随机抽取有限数量的实例用于自演化，其中 SWE-bench Verified 50 个、SWT-Bench 50 个、FeatureBench 30 个。

### 3.2 初始智能体 Harness

我们用 Mini-SWE-Agent（Yang et al., 2024）初始化 Harness，这是一个常用的软件工程任务智能体框架。其核心实现只有约 100 行 Python 代码，却在 SWE-bench Verified 上取得超过 74% 的分数。原始实现提供了智能体控制流、模型接口、Bash 工具定义，以及本地与 Docker 环境的配置。为防止演化器修改接口规范或执行环境，我们把自演化范围限制在以下几个方面：修改系统提示词、修改智能体执行逻辑、以及添加或修改工具。

### 3.3 被评估的演化算法

我们选取两种有代表性的智能体 Harness 自演化方法，评估它们在持续演化中的灾难性遗忘。

**AHE**（Lin et al., 2026）构造了一个闭环的自演化过程。编码智能体通过当前 Harness 与环境交互，在目标任务数据集的任务上生成轨迹。随后 Agent Debugger 用通用 shell 命令与脚本工具访问轨迹文件，总结成功轨迹与失败轨迹的根因。最后 Evolve Agent 利用 Agent Debugger 产生的证据修改 Harness 代码，为下一轮演化准备好更新后的 Harness。

**Meta-Harness**（Lee et al., 2026）则与之不同，它持续维护一个 Harness 的帕累托前沿。在每一轮演化中，编码智能体参照既有 Harness 与累积经验提出新的修改；新修改出的 Harness 随后在当前数据集的任务上评估，评估日志存入文件系统供后续演化使用。

由于这两种方法公开的实现都不支持 Mini-SWE-Agent 的演化，我们基于它们的原始代码库实现了相应功能，并尽可能让我们的实现与原实验设置保持一致。

### 3.4 实现细节

超参方面，我们把 rollout 温度设为 0。对 AHE 与 Meta-Harness，我们沿用各自原论文的设置，分别执行 9 轮与 5 轮演化。每轮中同一批任务被执行两次，所得轨迹被分析以引导演化。

我们使用 DeepSeek-V4-Flash-0731（DeepSeek-AI, 2026）作为任务执行与 Harness 演化的基础模型。为保证所有实验的执行环境一致，我们统一使用 E2B 作为沙箱环境，并把每个任务执行的时间上限设为 1 小时。
## 4 实验结果

图 2. 单一数据集上的 Harness 演化。AHE 与 Meta-Harness 在 SWE-Bench、SWT-Bench 与 FeatureBench 上逐轮演化过程中的性能。标注给出每次演化过程中识别出的性能最佳的 Harness。

图 3. 持续 Harness 自演化中六个方向上的灾难性遗忘。对每个方向，先在单一数据集上演化出的 Harness 被继续在另一个数据集上演化，并在初始时、以及再经过 3 轮和 5 轮持续演化之后评估其在较早数据集上的性能（Initial、Iter 3 与 Iter 5）。演化后柱条上的标签给出性能分数与相对性能下降（ρ）。

### 4.1 RQ1：持续 Harness 自演化过程中的灾难性遗忘

为考察持续 Harness 自演化是否导致灾难性遗忘，本研究问题考察它如何影响先前已遇到任务上的性能。

**设置。** 在我们的实验中，我们在两个不同类型的数据集上搭建持续 Harness 自演化。由此实验设置得到的结论也可以推广到多个顺序数据集：一种在相邻任务上造成灾难性遗忘的演化方法，在跨多个数据集的持续演化中同样会造成遗忘。我们先分别在 SWE-Bench、SWT-Bench 与 FeatureBench 上独立进行自演化；随后，我们把每次演化过程中取得的最佳性能 Harness 选作初始 Harness，迁移到另一个数据集上继续演化，并评估它在先前数据集上的性能退化。当多个 Harness 取得相同的最高分时，我们选取最先达到该分数的 Harness。例如，对 FeatureBench 上的 AHE，我们选取第三轮之后得到的 Harness（成绩 30.0%）作为持续演化的初始。

**结果。** 实验结果得出以下关键发现：

- ❶ 两种自演化方法在单一数据集上演化时都展现出显著的性能提升。如图 2 所示，H0 表示 Mini-SWE-Agent 的初始 Harness，Hi 表示第 i 轮演化之后的 Harness。例如，AHE 把 SWE-Bench 上的成绩从初始的 82.0% 经九轮演化提高到 96.0%，而 Meta-Harness 最终达到 94.0%。在 SWT-Bench 上，两种方法都把随机抽取的 50 个任务上的成绩从初始的 82.0% 提高到 100.0%。在 FeatureBench 上，两种方法最终都提升了 10 个百分点以上。我们在图 2 的每条折线上用圆圈标出最高分点，以突出性能最佳的 Harness。

- ❷ 现有自演化方法难以在持续 Harness 自演化中保持先前获得的能力。如图 3 所示，几乎每一个持续 Harness 自演化方向都会在先前已遇到的任务上造成显著的性能下降。例如，当从 SWE-Bench 演化到 SWT-Bench 时，经过五轮演化，AHE 与 Meta-Harness 在 SWE-Bench 上分别出现 100% 与 98% 的性能下降；换言之，在 SWT-Bench 上演化之后，得到的智能体几乎完全无法解决 SWE-Bench 任务。类似地，在 SWE → Feature 设置下，AHE 与 Meta-Harness 的性能分别下降 29% 与 66%。

- ❸ 灾难性遗忘的程度在不同数据集与演化方向之间差异显著。在软件工程领域，SWT-Bench（Mündler et al., 2024）评估的是智能体的测试用例生成能力，而 SWE-Bench（Jimenez et al., 2024）与 FeatureBench（Zhou et al., 2026）要求智能体修改现有仓库的源代码。因此 SWT-Bench 与另外两个数据集的关联相对较弱，而 SWE-Bench 与 FeatureBench 涉及的任务类型更为接近。如图 3 所示，在 SWE-Bench 与 FeatureBench 之间演化，对先前已遇到数据集造成的性能下降相对较小；而在 SWT-Bench 与另外两个数据集之间演化，则导致大得多的下降。

这些结果表明，任务相关性可能在缓解持续 Harness 自演化中的灾难性遗忘上扮演重要角色。在一个差异很大的任务类型上演化，可能引入对从前一任务获得的能力极为有害的修改，从而造成更严重的遗忘。

**RQ1 作答**　现有 Harness 自演化方法能在单一任务类型上提升性能，但在持续演化中往往遭受灾难性遗忘；遗忘的程度与数据集及演化方向密切相关。

图 4. 持续 Harness 自演化中 Harness 冲突的示例。(a) Feature → SWT 过程中的验证冲突：SWT 特有的验证机制（evidence gate，证据门控）——「生成的测试在 buggy 代码上即通过」意味着不提供 fail-to-pass 证据，因此提交被拒绝（FAIL / rejected）；而 SWE 的提交门控为 source fix-only（仅接受源码修复），在持续演化于 SWE 之后变为 FAIL。(b) SWT → SWE 过程中的产物冲突：提交门控从「test-only patch」切换为「source fix」，PASS / rejected 极性反转。(c) SWE → SWT 过程中的工作流冲突：SWE 特有工作流为「检查问题 →编辑源码 → 运行测试 → 提交修复」，SWT 特有工作流为「检查问题 → 找测试 → 写测试 → 检查 FAIL2PASS → 回滚源码 → 提交测试」。(d) Feature → SWE 过程中的预算策略冲突：为 SWE 加入的时间预算策略是「超时感知收敛」——超时后推动智能体停止重试、收窄测试范围并更快收敛，结果是「性能≈不变 · 智能体耗时 ↑↓」。
### 4.2 RQ2：与灾难性遗忘相关的 Harness 组件

#### 4.2.1 Harness 冲突的分类

在本研究问题中，我们进一步分析 Harness 修改为何会导致先前已遇到任务上的性能下降。

**设置。** 为刻画持续 Harness 自演化期间引入的 Harness 冲突类型，我们对图 3 中的每个演化方向做两阶段分析。首先，我们提取初始 Harness 与经五轮持续演化所得 Harness 之间的代码差异，人工检查这些修改，识别演化过程引入的冲突类型。随后我们共分析 520 条执行轨迹，找出在持续 Harness 自演化之后出现「通过 → 失败」转变的任务；对这些案例，我们细致分析其执行轨迹，判定观察到的失败与哪些类型的 Harness 冲突相关。最后，我们计算每种冲突类型在这些「通过 → 失败」案例中的占比，以量化它们在观察到的性能下降中的普遍程度。

**结果。** 我们识别出三类可能引入此类冲突的主要修改：验证冲突、工作流冲突与预算策略。在「通过 → 失败」案例中，验证冲突占 87.1%，工作流冲突占 8.2%，预算冲突占 0.6%；其余案例不与特定冲突类型相关。

- ❶ **验证冲突**产生于 Harness 引入了为某一数据集需求量身定制的检查、约束或提醒。Harness 可能规定应当检查哪些证据、提交前必须满足哪些条件、或应当交付哪种产物。这些干预直接影响智能体的执行轨迹，并可能与先前已遇到任务的需求冲突。图 4(a) 给出从 FeatureBench 持续演化到 SWT-Bench 过程中的一个正常例子：它意味着如果新生成的测试在 buggy 代码上就已经通过，那么它没有提供 fail-to-pass 证据，提交因此被阻断。这一针对 SWT-Bench 的特定修改可能对先前任务的性能产生负面影响。

  在验证冲突中，**产物冲突**最为突出。当一个智能体 Harness 从一类任务演化到另一类任务时，可能被纳入产物特定的约束，例如在提交时强制要求预期的产物类型。这些修改可能与先前任务的需求冲突，导致智能体产出不恰当的产物，进而造成任务失败。如图 4(b) 所示，在从 SWT-Bench 演化到 SWE-Bench 的过程中，所需提交产物从「仅测试补丁」切换为「源码修复」，伴随而来的是提交门控极性的反转。

- ❷ **工作流冲突**源于求解不同类型任务所需流程的差异。这类差异通常体现在 Harness 的提示词或与工作流相关的辅助内容中。如图 4(c) 所示，在从 SWE-Bench 演化到 SWT-Bench 的过程中，提示词被修改以改变智能体的问题求解工作流：智能体不再在定位问题后直接修改源代码，而是先找到相关测试文件、编写回归测试、验证它在修复前失败而在修复后通过，最后回滚临时的源代码修改。这些修改可能有利于当前任务类型，却会干扰更适合先前已遇到任务的工作流。

- ❸ **预算策略**关注 Harness 如何管理分配给智能体的有限时间与计算资源。这类策略包括基于已消耗墙钟时间或步数的提醒，以及针对反复命令失败、超时或执行缓慢的守卫。在持续 Harness 自演化中，这些预算相关机制可能被修改以适应当前任务的资源需求。图 4(d) 给出从 FeatureBench 演化到 SWE-Bench 期间引入的一个有代表性的预算策略修改：在反复命令超时之后，Harness 提示智能体停止反复重试同一批命令、收窄测试范围，并更快地收敛到一个解。

#### 4.2.2 不同 Harness 冲突类型的影响与案例研究

**表 1**　各类 Harness 冲突对 SWE-Bench 性能与智能体执行时间的影响。

| Harness 配置 | SWE 性能（%） | 智能体耗时（秒） |
| --- | --- | --- |
| 原始最佳 Harness | 96.0 | 245.5 |
| + 验证冲突 | 0.0（↓100%） | 415.7（↑69%） |
| + 工作流冲突 | 66.0（↓31%） | 821.5（↑235%） |
| + 预算策略 | 96.0（↓0%） | 439.7（↑79%） |

不同冲突类型的普遍程度并不必然反映它们对智能体性能的影响。为检验各自的效应，我们把与每种冲突类型相关的代表性修改引入 Harness，并把由此得到的性能与原始 Harness 的性能做对比。我们还进一步分析失败案例，以理解每种冲突如何导致任务失败。

**设置。** 我们以 AHE 从 SWE-Bench 到 FeatureBench 的演化为例：把持续 Harness 自演化期间识别出的工作流与时间预算相关修改，加入到此前在 SWE-Bench 上演化出的最佳性能 Harness 中，考察每项修改在 SWE-Bench 上造成的性能影响。由于 SWE-Bench 与 FeatureBench 在提交产物方面差异不大，我们转而以从 SWE-Bench 到 SWT-Bench 的演化作为验证冲突修改的来源。

**结果。** 如表 1 所示，我们发现引入一个强制性的产物约束会立刻把 SWE-Bench 上的性能降到 0.0。在从 SWE-Bench 到 SWT-Bench 的持续 Harness 自演化中，不同的交付物要求反转了提交逻辑：演化出的 Harness 会在提交前自动检查智能体的修改，并拒绝任何改动了测试文件之外文件的解。这一约束适合 SWT-Bench，却与 SWE-Bench 不兼容——后者需要修改源代码才能修复问题。

工作流冲突的影响同样显著，把性能从 96.0 降到约 66.0。在从 SWE-Bench 到 FeatureBench 的持续演化中，演化器大幅修改了系统提示词中智能体的工作流，同时在 Harness 层面引入硬约束来强制执行该工作流。具体而言，演化出的 Harness 会拦截 pip、curl、git 等网络相关命令，阻止智能体访问外部资源。结果是智能体失去对可能有用的外部资源的访问，SWE-Bench 性能因此大幅下降。此外，遵循 FeatureBench 特有的工作流会让智能体执行大量不必要的探索操作，使平均任务执行时间增加 235%。

相比之下，预算策略对任务性能影响很小，其效应主要体现在任务执行效率的变化上。如表 1 所示，引入从 FeatureBench 学到的预算策略使智能体执行时间增加 79%。

**RQ2 作答**　Harness 中的冲突可分为三类：验证冲突、工作流冲突与预算策略冲突。它们的影响差别显著——产物冲突与工作流冲突造成最严重的性能下降，而预算策略主要反映在智能体的执行时间上。

## 5 相关工作

### 5.1 Harness 自演化

近期关于 Harness 自演化的工作聚焦于改进围绕基础模型的运行时系统（Lin et al., 2026; Lee et al., 2026; Zhang et al., 2026a; Chen et al., 2026）。给定一组任务，智能体先产生一批执行轨迹；演化过程随后分析这些轨迹，识别成功行为或诊断失败根因，并在累积证据的基础上对智能体 Harness 做出可归因的修改。大量工作聚焦于演化单个 Harness 组件，包括提示词（Agrawal et al., 2026; Zhang et al., 2026c）、记忆（Zhou et al., 2025; Chhikara et al., 2025）与技能（Zhang et al., 2026b; Xia et al., 2026）；另一些方法则把 Harness 作为整体来优化，例如 AHE（Lin et al., 2026）、Meta-Harness（Lee et al., 2026）、Self-Harness（Zhang et al., 2026a）与 HarnessX（Chen et al., 2026）。

然而，现有 Harness 自演化研究主要评估演化过程能否在单一类型的任务上提升智能体能力，没有明确考虑现有方法能否跨多种任务持续演化 Harness。

### 5.2 智能体的持续学习

近年来，持续学习研究逐渐从面向 LLM 的持续学习扩展到面向基于 LLM 的智能体的持续学习（Zheng et al., 2026）。例如，Voyager（Wang et al., 2024）在交互过程中持续积累并复用技能，CER（Liu et al., 2025）与 LifeMem（Qiu et al., 2026）则聚焦于保留和利用历史经验来辅助智能体完成当前任务。也有若干基准被提出用于评估智能体的持续学习：LifelongAgentBench（Zheng et al., 2025）与 EvoAgentBench（Gao et al., 2026）关注基于技能的智能体，AGENTCL（Shu et al., 2026）、Continual Learning Bench（Asawa et al., 2026）与 SWE-Bench-CL（Joshi et al., 2025）则考虑任务顺序与随时间累积的经验，主要评估记忆增强的智能体。

然而，人们对智能体 Harness 作为整体的持续演化关注相对较少——在那里，多个组件可以基于累积的执行经验被联合修改。

## 6 结论

本文研究了持续 Harness 自演化，并把灾难性遗忘识别为核心挑战。我们在三个软件工程基准、六个跨任务演化方向上评估了两种有代表性的 Harness 自演化方法。两种方法虽然都能提升单一任务上的性能，但当演化跨及不同任务时，其性能往往大幅下降。进一步的分析识别出三类导致灾难性遗忘的 Harness 级冲突：验证冲突、工作流冲突与预算策略冲突。这些发现凸显了让编码智能体跨多样软件工程任务可靠演化的挑战。

## 参考文献（从略）

参考文献从略，见原文。

## 附录 A 实现细节

**表 2**　可复现性配置。

| 项目 | 待报告的设置 |
| --- | --- |
| 初始 Harness | Mini-SWE-Agent v2.4.6，扩展了工具注册表 |
| 可演化表面 | `src/minisweagent/config/mini.yaml`（提示词）、`src/minisweagent/agents/**`（控制流）、`src/minisweagent/models/utils/**`（工具、解析器、观察） |
| 模型 | DeepSeek-V4-Flash-0731 |
| Rollout | 每任务每轮 2 次 |
| 沙箱 | E2B，沙箱生命周期 1 小时 |
| 演化轮数 | AHE：9 轮演化（共评估 10 个 Harness）；Meta-Harness：5 轮 |
| 数据集 | SWE-bench Verified（50）、改写后的 SWT-bench（50）、FeatureBench（30） |

## 附录 B 数据集设置的讨论与案例研究

在第 3 节中，我们描述了实验采用的一个具体设置：在保留 SWT-Bench 实例原有语义的前提下，改写了它们共有的固定语言模式。本节进一步讨论并验证这一实验设置背后的理据。

如果保持原始 SWT-Bench 提示词不变，如图 5(a) 所示，我们会观察到：从 SWE-Bench 到 SWT-Bench 的 Meta-Harness 演化引入了一个用于判定提交产物的条件分支，如图 5(c) 所示。具体而言，如果 Harness 把当前任务识别为代码修改任务，它就要求智能体提交源代码；否则要求智能体提交测试文件。这一行为是缓解灾难性遗忘的积极信号，因为它使演化出的 Harness 能区分不同类型的任务、并保留相应的提交要求。

然而，用于判定 `test_deliverable` 的条件完全基于 SWT-Bench 所用的固定语言模板构造，如图 5(b) 所示。这种演化模式显然不利于泛化，因为学到的条件与 SWT-Bench 提示词的表层形式紧密绑定，而非与底层任务语义绑定。

在改写 SWT-Bench 提示词之后，我们在自演化过程中不再观察到类似的、依赖模板的条件分支。这一观察表明，提示词改写能够降低自演化利用数据集特定语言模式的风险，促使演化出的 Harness 更多依赖任务层面的特征。

图 5. 从 SWE-Bench 演化到 SWT-Bench 期间引入的 Harness 修改案例研究，三个子图依次为改写前的提示词模板、演化出的 Harness 中的测试交付物提示词、以及引入的提交条件分支。

```text
The following text contains a user issue (in <issue/> brackets) posted at a repository. It may be necessary to use code
from third party dependencies or files not contained in the attached documents however. Your task is to identify the issue
and implement a test case that verifies a proposed solution to this issue. More details at the end of this text.
<issue/>
...
</issue>
Please generate test cases that check whether an implemented solution resolves the issue of the user (at the top, within
<issue/> brackets).
You may apply changes to several files.
Apply as much reasoning as you please and see necessary.
Make sure to implement only test cases and don't try to fix the issue itself.
```

图 5(a) 改写前的 SWT-Bench 提示词模板。

```python
_TEST_DELIVERABLE_HINTS=("implement a test case","implement test cases","test case that verifies","test cases that verify",
"don't try to fix the issue","do not try to fix the issue","implement only test cases","only test cases")
def task_requests_test_deliverable(task_text: str) -> bool:
    """Return True when the issue text asks for a test-writing deliverable."""
    if not isinstance(task_text, str):
        return False
    return any(hint in task_text for hint in _TEST_DELIVERABLE_HINTS)
```

图 5(b) 演化出的 Harness 中的测试交付物提示词。

```python
for action in message.get("extra", {}).get("actions", []):
    output = self.env.execute(action)
    if test_deliverable:
        # Test-writing issue: source edits are the failure mode (the graded patch is the full diff), so warn about source
        # edits instead of telling the agent to revert test edits.
        output = source_edit_guard.maybe_annotate_source_edits(self.env, action, output)
    else:
        output = test_edit_guard.maybe_annotate_test_edits(self.env, action, output)
    if not self._verification_guide_fired:
        annotated, fired = verification_guide.maybe_annotate_verification_guide(self.env, action, output)
        if fired:
            self._verification_guide_fired = True
        output = annotated
    outputs.append(output)
```

图 5(c) 从 SWE-Bench 演化到 SWT-Bench 期间引入的提交条件分支。
