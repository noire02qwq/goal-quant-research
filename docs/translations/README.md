# 文献 / 项目文档中译（docs/translations/）

> 状态：定稿（规范）｜ 建立：2026-11-03 @user 指令

把本仓库**引用到的英文原材料**翻译成人类可读的中文，让研究笔记的引用链可以直接中文阅读，不必逐篇开英文原文。翻译件是**阅读辅助**，不替代原文——所有事实性引用仍以英文原文 + 原始链接为准（CONVENTIONS §3.2/§3.3）。

## 1. 收录范围（三类）

| 子目录 | 收什么 | 对应英文源 | 翻译深度 |
|---|---|---|---|
| `papers/` | `docs/papers/` 已下载的论文 | 本地 PDF | **全文**（正文全译，参考文献从略） |
| `literature/` | 笔记/设计文档引用但未下载的论文 | arXiv abs 页 | **题录 + 摘要**（与"仅摘要级"引用深度一致） |
| `projects/` | 引用到的开源项目英文文档 | `oss-repos/` 本地克隆、官网 | **全文**（被引用的文档 + 项目 README） |

不收：中文来源（知乎/CSDN 等原文即中文）、第三方依赖自带文档（如 vn-demo `.venv`/`Pods` 内 LICENSE/README）、公司 harness 项目任何文档（CONVENTIONS §6）。

## 2. 命名

- `papers/arXiv-<ID>.md` —— 与 `docs/papers/arXiv-<ID>.pdf` 同名换后缀。
- `literature/arXiv-<ID>.md` —— 未下载论文的题录摘要译文。
- `projects/<仓库短名>/<原文件路径>.md` —— 保持源文档相对路径，如 `projects/rakazo/docs/groups.md`。
- 仓库短名：`rakazo` / `opendots` / `openmuse` / `hermes` / `dsh-superagent`。

## 3. 文件头（每篇必带）

```markdown
# <中文译题>（<English Original Title>）

> 来源：<可点击原始链接>
> 原文：<本地路径，如 docs/papers/arXiv-2608.03836.pdf 或 oss-repos/rakazo/docs/groups.md>
> 翻译日期：YYYY-MM-DD ｜ 范围：全文 / 摘要级 ｜ 方式：机器翻译初稿，未经人工校对
> 引用于：<本仓库哪些文档引用了它>
```

## 4. 人类可读性要求（2026-11-03 全仓可读性排查后确立）

1. **自然中文**：译文要像人写的中文，不是逐词直译；定语过长就拆句。
2. **结构对齐原文**：标题层级与原文一致；超过 15 个标题或 500 行的译文在文件头下加目录。
3. **段落上限 500 汉字**：超过就拆段或改列点——本次排查测得原文档最长达 3996 字符的墙式段落，译文不得复制这个毛病。**计数口径：只数汉字**（规范原文即「500 汉字」），代码标识符、英文词与标点不计入；若按总字符另测会有更多段越线（如含大量代码标识符的英文文档译文），那是更严的口径，复核时请注明用的是哪一种。
4. **术语保留英文**：论文标题、方法名、指标名、代码标识符保留英文原文（CONVENTIONS §3.1），首现可括注中文解释。
5. **公式 / 代码块 / 表格结构原样保留**，表头可译中文；图片以 `![图X：<中文说明>](<原文图片URL>)` 占位并注明原文位置（占位符中的 URL 换成实际图片地址，无地址时改写为文字说明「图X：<中文说明>（原文第N页）」）。
6. **参考文献表从略**，注一行「参考文献从略，见原文」。
7. **诚实标注**：翻译深度（全文/摘要级）、机器翻译未经校对、原文提取失败的段落（标「原文此处无法提取」）都必须写明，不得默认省略。
8. **终检口径（2026-11-03 确立）**：段落上限的统计按「空行 / 列表项边界」切分，**表格与代码块不计入**（§4.5 要求结构原样保留，无法拆段）；文内相对链接**保留原文相对路径**（§4.2 结构对齐），因此指向未译源文档（如 `docs/000-philosophy.md`、`CONTRIBUTING.md`）的链接在译文目录内不解析属预期，以原仓可解析为准；图片无可提取图链时只留文字说明「图X：（原文位置：PDF 第N页）」，不指向本地 PDF。

## 5. 索引

| [papers/arXiv-2608.03836.md](papers/arXiv-2608.03836.md) | Resume Means Resume：工作流持久化层中 Checkpoint、Interrupt 与 Resume 语义的机器校验一致性契约 | 全文 |
| [papers/arXiv-2608.14380.md](papers/arXiv-2608.14380.md) | AgentRewind：面向长时程 LLM Agent 的可恢复执行 | 全文 |
| [papers/arXiv-2609.34215.md](papers/arXiv-2609.34215.md) | 同样的赢家，不同的成功率：LLM Agent 如何从失败中恢复 | 全文 |
| [papers/arXiv-2610.14515.md](papers/arXiv-2610.14515.md) | SEPM：扎根任务图的自进化程序记忆，用于多智能体协作 | 全文 |
| [papers/arXiv-2610.26995.md](papers/arXiv-2610.26995.md) | SPEM：面向 LLM Agent 高效技能利用的结构感知程序性记忆 | 全文 |
| [papers/arXiv-2610.27645.md](papers/arXiv-2610.27645.md) | CUA-Recovery：长时程计算机使用 agent 的错误恢复基准 | 全文 |
| [papers/arXiv-2610.34724.md](papers/arXiv-2610.34724.md) | 面向长时程持续学习的 Harness–Model 协作 | 全文 |
| [papers/arXiv-2610.38573.md](papers/arXiv-2610.38573.md) | CALM：面向长程语言智能体的冲突感知生命周期记忆治理 | 全文 |

`literature/` 30 篇（23 篇 arXiv + 7 篇非 arXiv 短名文件），全部摘要级：

- [agent-market-arena-2026](literature/agent-market-arena-2026.md) — 当智能体开始交易：面向 LLM 智能体的实时多市场交易基准
- [agent-skills-survey-2026](literature/agent-skills-survey-2026.md) — 从程序性记忆看 Agent Skills：一篇综述
- [alphaagent-2025](literature/alphaagent-2025.md) — AlphaAgent：以正则化探索对抗 alpha 衰减的 LLM 驱动 Alpha 挖掘
- [arXiv-2307.07924](literature/arXiv-2307.07924.md) — ChatDev：面向软件开发的交流型智能体
- [arXiv-2308.00016](literature/arXiv-2308.00016.md) — Alpha-GPT：面向量化投资的人机交互式 Alpha 挖掘
- [arXiv-2308.00352](literature/arXiv-2308.00352.md) — MetaGPT：面向多智能体协作框架的元编程
- [arXiv-2308.08155](literature/arXiv-2308.08155.md) — AutoGen：以多智能体对话支撑下一代 LLM 应用
- [arXiv-2308.10144](literature/arXiv-2308.10144.md) — ExpeL：大语言模型智能体是经验学习者
- [arXiv-2402.03755](literature/arXiv-2402.03755.md) — QuantAgent：以自我改进的大语言模型寻求交易「圣杯」
- [arXiv-2402.18485](literature/arXiv-2402.18485.md) — 面向金融交易的多模态基础智能体：工具增强、多元与通用
- [arXiv-2409.07429](literature/arXiv-2409.07429.md) — Agent Workflow Memory：智能体工作流记忆
- [arXiv-2412.20138](literature/arXiv-2412.20138.md) — TradingAgents：基于多智能体 LLM 的金融交易框架
- [arXiv-2501.06322](literature/arXiv-2501.06322.md) — 多智能体协作机制：基于大语言模型的综述
- [arXiv-2502.14321](literature/arXiv-2502.14321.md) — 超越自我对话：以通信为核心的 LLM 多智能体系统综述
- [arXiv-2503.01935](literature/arXiv-2503.01935.md) — MultiAgentBench：评估 LLM 智能体的协作与竞争
- [arXiv-2505.15155](literature/arXiv-2505.15155.md) — R&D-Agent-Quant：面向数据的因子与模型联合优化多智能体框架
- [arXiv-2505.22954](literature/arXiv-2505.22954.md) — Darwin Gödel Machine：自我改进智能体的开放式演化
- [arXiv-2506.13131](literature/arXiv-2506.13131.md) — AlphaEvolve：用于科学与算法发现的编码智能体
- [arXiv-2510.01617](literature/arXiv-2510.01617.md) — AMAS：面向基于 LLM 的多智能体系统的通信拓扑自适应确定
- [arXiv-2511.03628](literature/arXiv-2511.03628.md) — LiveTradeBench：在真实交易中寻求大语言模型的 Alpha
- [arXiv-2601.13770](literature/arXiv-2601.13770.md) — Look-Ahead-Bench：金融场景下 Point-in-Time LLM 前视偏差的标准化基准
- [arXiv-2601.21526](literature/arXiv-2601.21526.md) — KAPSO：知识驱动的自主程序合成与优化框架
- [arXiv-2605.06024](literature/arXiv-2605.06024.md) — Strat-LLM：结合实时多源信号的分层策略对齐股票交易框架
- [arXiv-2606.11926](literature/arXiv-2606.11926.md) — 通过假设树精化走向通用自主研究
- [arXiv-2608.27734](literature/arXiv-2608.27734.md) — 诚实评估能留下什么？LLM 驱动的交易策略发现之防泄漏、感知搜索强度的评估
- [arXiv-2610.25851](literature/arXiv-2610.25851.md) — 学习谁与谁通信：面向高效 LLM 多智能体协作的角色感知通信拓扑调度
- [backtestbench-2026](literature/backtestbench-2026.md) — BacktestBench：面向自动化量化策略回测的 LLM 基准
- [deflated-sharpe-ratio-2014](literature/deflated-sharpe-ratio-2014.md) — 去膨胀 Sharpe 比率与回测过拟合概率
- [effective-trial-counts-2026](literature/effective-trial-counts-2026.md) — 你究竟试了多少个策略？LLM 提出回测的有效试验次数
- [sok-agentic-skills-2026](literature/sok-agentic-skills-2026.md) — SoK：Agentic Skills——超越 LLM 智能体的工具调用

`projects/` 共 29 篇（5 个仓库，按被引用文档全文中译；README 为指路文件）：

**rakazo**（7 篇）：
- [rakazo/README.md](projects/rakazo/README.md) — Rakazo 项目 README 中译指路
- [rakazo/docs/approvals.md](projects/rakazo/docs/approvals.md) — 审批
- [rakazo/docs/computer-runtime.md](projects/rakazo/docs/computer-runtime.md) — 计算机运行时
- [rakazo/docs/computer.md](projects/rakazo/docs/computer.md) — bot 的计算机
- [rakazo/docs/groups.md](projects/rakazo/docs/groups.md) — 群组与团队协作
- [rakazo/docs/routines.md](projects/rakazo/docs/routines.md) — 例行任务
- [rakazo/site-home.md](projects/rakazo/site-home.md) — Rakazo 官网首页

**opendots**（5 篇）：
- [opendots/README.md](projects/opendots/README.md) — OpenDots 项目说明
- [opendots/docs/COMPUTERS.md](projects/opendots/docs/COMPUTERS.md) — 每个 Dot 一台电脑
- [opendots/docs/CONNECTIONS.md](projects/opendots/docs/CONNECTIONS.md) — 连接
- [opendots/docs/SETUP.md](projects/opendots/docs/SETUP.md) — 运行这个模板
- [opendots/site-page.md](projects/opendots/site-page.md) — OpenDots 产品页

**openmuse**（4 篇）：
- [openmuse/COMPUTER.md](projects/openmuse/COMPUTER.md) — agent 计算机
- [openmuse/FEATURES.md](projects/openmuse/FEATURES.md) — OpenMuse 特性清单
- [openmuse/README.md](projects/openmuse/README.md) — OpenMuse 项目 README
- [openmuse/site-page.md](projects/openmuse/site-page.md) — OpenMuse 官网产品页

**hermes**（8 篇）：
- [hermes/README.md](projects/hermes/README.md) — Hermes Agent 项目 README 中译
- [hermes/website/docs/developer-guide/cron-internals.md](projects/hermes/website/docs/developer-guide/cron-internals.md) — Cron 内部机制
- [hermes/website/docs/developer-guide/state-db-recovery.md](projects/hermes/website/docs/developer-guide/state-db-recovery.md) — 状态数据库与 FTS 恢复
- [hermes/website/docs/user-guide/configuration.md](projects/hermes/website/docs/user-guide/configuration.md) — Hermes Agent 配置
- [hermes/website/docs/user-guide/features/curator.md](projects/hermes/website/docs/user-guide/features/curator.md) — Curator
- [hermes/website/docs/user-guide/features/kanban.md](projects/hermes/website/docs/user-guide/features/kanban.md) — Kanban——多 Agent Profile 协作
- [hermes/website/docs/user-guide/features/memory.md](projects/hermes/website/docs/user-guide/features/memory.md) — 持久记忆
- [hermes/website/docs/user-guide/features/skills.md](projects/hermes/website/docs/user-guide/features/skills.md) — 技能系统

**dsh-superagent**（5 篇）：
- [dsh-superagent/README.md](projects/dsh-superagent/README.md) — dsh-superagent 项目自述
- [dsh-superagent/docs/001-domain.md](projects/dsh-superagent/docs/001-domain.md) — 001 领域模型
- [dsh-superagent/docs/002-authorization.md](projects/dsh-superagent/docs/002-authorization.md) — 002 授权
- [dsh-superagent/docs/003-execution.md](projects/dsh-superagent/docs/003-execution.md) — 003 执行
- [dsh-superagent/docs/007-architecture.md](projects/dsh-superagent/docs/007-architecture.md) — 007 架构

## 6. 引用关系

译文不改变任何既有引用规则：研究笔记仍引用**英文原文链接**（CONVENTIONS §3.3），译文只是同链的中文阅读入口。回填 §3 主表、写决策记录时，可以「原文链接 + 中译路径」并列给出。
