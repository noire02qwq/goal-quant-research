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

## 目录结构

```
goal-quant-research/
├── README.md                     # 本文件：概览与快速导航
├── .gitignore
├── docs/                         # 全部研究/设计文档（本仓库主体）
│   ├── mission.md                # 任务说明（需求原文）
│   ├── brief-plan.md             # 总体设计方案
│   ├── CONVENTIONS.md            # 仓库与文档规范
│   ├── literature/               # 每周文献笔记（W1–W10，模板见 templates/）
│   ├── decisions/                # 决策记录（ADR，研究 demo 结论沉淀于此）
│   ├── essay-study/              # 论文/文章精读笔记（非每周检索式的深读材料）
│   └── templates/                # 文献笔记 / 决策记录 / spike 报告模板
└── independent-demo-apps/        # 独立可运行 demo 索引区
    └── vn-demo/                  # vnpy 回测集成 demo —— 独立 git 仓库，本仓忽略
```

## 重要约定（详见 [docs/CONVENTIONS.md](docs/CONVENTIONS.md)）

- **研究 demo 本体不入库**：demo 是临时产物，放本地 scratch 目录（如 `~/Desktop/goal-agent-research/<主题>/`）；结论以**决策记录**（`docs/decisions/`）+ 定点测试沉淀，并回写 `brief-plan.md` 对应章节。
- **每周研究必须有文献笔记**：`docs/literature/W<周>-<主题>.md`，含检索式、入选论文、方向结论、对设计文档的修订。仅读摘要的论文标注"仅摘要级"，不得当作已验证结论。
- **`independent-demo-apps/vn-demo/` 已被 gitignore**：它自带独立仓库（[noire02qwq/vnpy-demo](https://github.com/noire02qwq/vnpy-demo)），更新需进入该目录单独提交推送，本仓库不跟踪其内容。
- **凭证与真实账户信息禁止入库**（API key、token、券商账号等），本地用 `.env`（已 ignore）。

## 协作

- 主分支 `main`；功能改动走 feature 分支 + PR，文档类改动可直接提交。
- 提交信息使用 [Conventional Commits](https://www.conventionalcommits.org/)（`feat` / `docs` / `research` / `demo` / `chore`），描述用中文。
