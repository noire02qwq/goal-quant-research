# 仓库与文档规范（CONVENTIONS）

适用范围：`~/agent-studio/goal-quant-research`（远端：[noire02qwq/goal-quant-research](https://github.com/noire02qwq/goal-quant-research)）。本仓库只有文档与 demo 索引，不含生产插件代码。

## 1. 仓库定位与边界

| 属于本仓库 | 不属于本仓库 |
|---|---|
| 任务说明、总体设计及其修订 | 生产插件代码（goal-agent / quant-research，属平台仓库） |
| 每周文献笔记、决策记录、精读笔记 | 研究 demo 本体（本地 scratch 目录） |
| 独立 demo 的索引与说明 | vnpy-demo 的内容（其自带独立仓库） |
| 模板、规范、演示剧本等过程资产 | 凭证、密钥、真实账户信息 |

设计依据：brief-plan.md §12.0（demo 位置约定）与附录决策记录 #8/#9/#10。

## 2. 目录用途

| 目录 | 用途 | 命名 |
|---|---|---|
| `docs/` | 稳定文档：任务说明、总体设计、规范 | 小写英文连字符，如 `brief-plan.md` |
| `docs/literature/` | 每周文献笔记 | `W<周号>-<主题关键词>.md`，如 `W2-context-memory-distillation.md` |
| `docs/decisions/` | 决策记录（ADR）：研究 demo 结论、设计取舍 | `NNNN-<主题>.md`，四位递增编号，如 `0001-vnpy-as-backtest-engine.md` |
| `docs/essay-study/` | 论文/文章精读笔记（非每周检索式产出的深读材料） | `<作者或论文短名>-<年份>.md` |
| `docs/templates/` | 文档模板，新增模板在此归档 | 见各模板文件 |
| `independent-demo-apps/` | 独立可运行 demo 的索引；每个 demo 目录需自带 README | demo 目录小写连字符 |

## 3. 文档规范

1. **语言**：正文中文；术语、论文标题、指标名保留英文原文。
2. **溯源**：每个事实性论断给出来源（链接/论文编号/arXiv ID）；未读原文的文献必须标注"仅摘要级"。
3. **文献笔记**（每周研究必产出）：使用 [templates/literature-note.md](templates/literature-note.md)，必须包含 ①检索式与日期 ②3–5 篇入选论文（一句话贡献 + 与本项目关系 + 精读状态）③方向结论（采纳/改造/不采纳及理由）④对 brief-plan.md 哪一节的修订。
4. **决策记录**：使用 [templates/decision-record.md](templates/decision-record.md)。研究 demo 跑通后**先写决策记录再改设计**；结论推翻 brief-plan.md 假设时，必须显式更新对应章节，不允许默默绕过。
5. **设计文档修订**：brief-plan.md 的实质性修改在对应小节末尾或决策记录中留痕（改了什么、依据哪份研究）。
6. **文档状态**：进行中的文档在首部标注 `> 状态：草稿/定稿`；决策记录状态字段为 `提议/已采纳/已被取代`。

## 4. Demo 规则

1. demo 本体放**本地 scratch**（如 `~/Desktop/goal-agent-research/<主题>/`），不进本仓库、不进生产插件包。
2. demo 结论必须沉淀：一页决策记录（`docs/decisions/`）+ 必要的定点测试（放平台仓库测试目录）。
3. 耗时/体积/性能类测量（如 vnpy 安装耗时、回测批处理耗时）写入决策记录的"实测数据"段，作为后续设计参数依据。
4. `independent-demo-apps/` 里的 demo 是**例外**：可长期运行、需要独立仓库承载的 demo 放这里并单独建 git 仓库；本仓库只保留索引 README。当前 `vn-demo/` 已在 .gitignore 中排除。

## 5. 提交规范

- 使用 Conventional Commits：`feat`（新增内容）/ `docs`（文档修订）/ `research`（文献笔记、调研结论）/ `demo`（demo 索引更新）/ `chore`（杂项）。描述用中文，例：`research(w2): 新增长程上下文管理文献笔记`。
- 主分支 `main`。设计修订、规范类改动建议走 feature 分支 + PR；文献笔记/决策记录可直接提交 main。
- 每次提交前检查：无 `.DS_Store`、无凭证文件、无 demo 本体误入。

## 6. 敏感信息

- API key、token、券商/数据源凭证、真实账户与资金信息**一律不入库**；本地配置写 `.env`（已在 .gitignore）。
- 涉及真实资金的操作（哪怕模拟盘转实盘的参数）在文档中只写方案，不写可直接执行的凭证化脚本。

## 7. 分支与协作

- 研究（@research）与开发（@dev）在 main 上协作：文献/决策文档归研究，平台仓库代码归开发，本仓库只同步设计修订。
- 当 brief-plan.md 与平台仓库实现出现分歧时，以本仓库的设计修订 + 决策记录为准，并同步更新平台仓库的实现说明。
