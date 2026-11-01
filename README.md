# goal-quant-research

**金融领域长期目标自主智能体 —— 长程目标自进化记忆管理与量化交易策略迭代**

本仓库是项目的**研究与文档中枢**：任务说明、总体设计、每周文献笔记、决策记录、独立验证 demo 的索引。生产插件代码（`goal-agent` 通用目标引擎 / `quant-research` 金融领域层）在平台仓库（AgentStudio harness-hub）中开发；本仓库存放研究结论、设计修订与证据链文档。

> 项目周期：两阶段约 10 周（W5 / W10 各一次成果汇报）。推进方式为**研究-设计-开发交替循环**，详见 [docs/brief-plan.md](docs/brief-plan.md) §12。

## 核心文档

| 文档 | 内容 |
|---|---|
| [docs/mission.md](docs/mission.md) | 任务说明：两阶段目标与汇报要求（需求原文） |
| [docs/brief-plan.md](docs/brief-plan.md) | 总体设计：调研借鉴、领域模型、执行协议、测评闭环、里程碑与文献主题 |
| [docs/CONVENTIONS.md](docs/CONVENTIONS.md) | 仓库规范：目录用途、文档/提交/命名规则、demo 与敏感信息约定 |
| [docs/PROGRESS.md](docs/PROGRESS.md) | 进度记录：阶段状态、每日进展日志、阻塞与待办 |

## 目录结构

```
goal-quant-research/
├── README.md                     # 本文件：概览与快速导航
├── .gitignore
├── docs/                         # 全部研究/设计文档（本仓库主体）
│   ├── mission.md                # 任务说明（需求原文）
│   ├── brief-plan.md             # 总体设计方案
│   ├── CONVENTIONS.md            # 仓库与文档规范
│   ├── PROGRESS.md               # 进度记录（阶段状态、进展日志、阻塞）
│   ├── literature/               # 每周文献笔记（W1–W10，模板见 templates/）
│   ├── decisions/                # 决策记录（ADR，研究 demo 结论沉淀于此）
│   ├── essay-study/              # 论文/文章精读笔记（非每周检索式的深读材料）
│   ├── papers/                   # 研究涉及论文的 PDF 归档（arXiv-<ID>.pdf）
│   └── templates/                # 文献笔记 / 决策记录 / spike 报告模板
├── research-demos/               # brief-plan 定稿之后的研究 demo 本体（入库）
└── independent-demo-apps/        # 需独立仓库承载的 demo 索引区
    └── vn-demo/                  # vnpy 回测集成 demo（brief-plan 前的例外）—— 独立仓库，本仓忽略
```

## 重要约定（详见 [docs/CONVENTIONS.md](docs/CONVENTIONS.md)）

- **demo 入库以 brief-plan 定稿为界**：之后的研究 demo 本体入库 `research-demos/`（自带 README + 指向决策记录）；唯一例外是 `independent-demo-apps/vn-demo/`——写于 brief-plan 之前，保持独立仓库（[noire02qwq/vnpy-demo](https://github.com/noire02qwq/vnpy-demo)）+ 本仓索引，已被 gitignore。
- **引用必须带链接**：报告/笔记中引用来源论文或官方文档，必须附可点击链接；无链接视为未溯源，不得作为设计依据。论文 PDF 下载后归档 `docs/papers/`。
- **每周研究必须有文献笔记**：`docs/literature/W<周>-<主题>.md`，含检索式、入选论文、方向结论、对设计文档的修订。仅读摘要的论文标注"仅摘要级"，不得当作已验证结论。
- **凭证与真实账户信息禁止入库**（API key、token、券商账号等），本地用 `.env`（已 ignore）。

## 协作

- 主分支 `main`；功能改动走 feature 分支 + PR，文档类改动可直接提交。
- 提交信息使用 [Conventional Commits](https://www.conventionalcommits.org/)（`feat` / `docs` / `research` / `demo` / `chore`），描述用中文。
