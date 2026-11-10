# 仓库与文档规范（CONVENTIONS）

适用范围：`~/agent-studio/goal-quant-research`（远端：[noire02qwq/goal-quant-research](https://github.com/noire02qwq/goal-quant-research)）。本仓库只有文档与 demo 索引，不含生产插件代码。

## 1. 仓库定位与边界

| 属于本仓库 | 不属于本仓库 |
|---|---|
| 任务说明、总体设计及其修订 | 生产插件代码（goal-agent / quant-research，属平台仓库） |
| 每周文献笔记、决策记录、精读笔记 | vn-demo 的内容（写于 brief-plan 定稿之前，自带独立仓库） |
| brief-plan 之后的研究 demo 本体（`research-demos/`） | 凭证、密钥、真实账户信息 |
| 论文 PDF 资源（`docs/papers/`） | 体积超 20MB 的大型数据集/模型权重 |
| 模板、规范、演示剧本等过程资产 | |

设计依据：brief-plan.md §12.0（demo 位置约定）与附录决策记录 #8/#9/#10。

## 2. 目录用途

| 目录 | 用途 | 命名 |
|---|---|---|
| `docs/` | 稳定文档：任务说明、总体设计、规范 | 小写英文连字符，如 `brief-plan.md` |
| `docs/literature/` | 每周文献笔记 | `W<周号>-<主题关键词>.md`，如 `W2-context-memory-distillation.md` |
| `docs/decisions/` | 决策记录（ADR）：研究 demo 结论、设计取舍 | `NNNN-<主题>.md`，四位递增编号，如 `0001-vnpy-as-backtest-engine.md` |
| `docs/essay-study/` | 论文/文章精读笔记（非每周检索式产出的深读材料） | `<作者或论文短名>-<年份>.md` |
| `docs/papers/` | 研究涉及论文的 PDF 资源归档 | `arXiv-<ID>.pdf`，非 arXiv 来源用 `<短名>-<年份>.pdf` |
| `docs/translations/` | 引用英文原材料（论文/项目文档）的中文译文，规范见其 README | `papers/arXiv-<ID>.md`、`literature/arXiv-<ID>.md`、`projects/<仓库短名>/<原路径>.md` |
| `docs/templates/` | 文档模板，新增模板在此归档 | 见各模板文件 |
| `research-demos/` | brief-plan 定稿之后的研究 demo 本体（入库） | demo 目录小写连字符，每个 demo 自带 README |
| `oss-repos/` | 本地开源仓库浅克隆（走读/中译的引用源）；**已 gitignore，不入库、不推送** | 目录名 = GitHub 仓名，如 `rakazo` |
| `harness-hub/` | 公司平台仓本地副本；**已 gitignore，严禁入库**（§6） | 不适用 |
| `independent-demo-apps/` | 需要独立仓库承载的 demo 的索引；每个 demo 目录需自带 README | demo 目录小写连字符 |

## 3. 文档规范

1. **语言**：正文中文；术语、论文标题、指标名保留英文原文。
2. **溯源**：每个事实性论断给出来源（链接/论文编号/arXiv ID）；未读原文的文献必须标注"仅摘要级"。
3. **引用链接（硬性要求）**：研究报告/文献笔记/决策记录中凡引用来源论文或线上项目官方文档，必须附可点击的引用链接（arXiv abs 页、官方文档 URL 等），格式 `[#N] 标题 — 链接` 或行内 markdown 链接；无链接的引用视为未溯源，不得作为设计依据。
4. **论文 PDF 归档**：研究涉及的论文下载 PDF 存入 `docs/papers/`（命名见 §2），笔记中以 `docs/papers/arXiv-<ID>.pdf` 相对路径或 arXiv 链接指向。
5. **文献笔记**（每周研究必产出）：使用 [templates/literature-note.md](templates/literature-note.md)，必须包含 ①检索式与日期 ②3–5 篇入选论文（一句话贡献 + 与本项目关系 + 精读状态）③方向结论（采纳/改造/不采纳及理由）④对 brief-plan.md 哪一节的修订。
6. **决策记录**：使用 [templates/decision-record.md](templates/decision-record.md)。研究 demo 跑通后**先写决策记录再改设计**；结论推翻 brief-plan.md 假设时，必须显式更新对应章节，不允许默默绕过。
7. **设计文档修订**：brief-plan.md 的实质性修改在对应小节末尾或决策记录中留痕（改了什么、依据哪份研究）。
8. **文档状态**：进行中的文档在首部标注 `> 状态：草稿/定稿`；决策记录状态字段为 `提议/已采纳/已被取代`。

## 4. Demo 规则

1. **vn-demo 例外不入库**：`independent-demo-apps/vn-demo/` 写于 brief-plan 定稿之前、无对应设计约束，保持独立仓库（[noire02qwq/vnpy-demo](https://github.com/noire02qwq/vnpy-demo)）+ 本仓库索引 README 的形式，已在 .gitignore 排除。
2. **后续 demo 一律入库**：brief-plan 定稿之后的研究 demo 本体放 `research-demos/<demo名>/`，随本仓库版本管理；每个 demo 目录自带 README（验证目标、运行方式、结论指向的决策记录编号）。
3. demo 结论必须沉淀：一页决策记录（`docs/decisions/`）+ 必要的定点测试（放平台仓库测试目录）；demo README 与决策记录互相链接。
4. 耗时/体积/性能类测量（如 vnpy 安装耗时、回测批处理耗时）写入决策记录的"实测数据"段，作为后续设计参数依据。
5. demo 不得引入超 20MB 的数据/模型文件入库；数据集放本地或外部存储，README 记录获取方式。
6. **可交互演示（2026-11-01 @user 规定，适用于后续所有 demo）**：demo 不能只有脚本跑分——必须提供可实际操作的入口，让读者亲手触发并观察研究原理（如崩溃注入、恢复扫描、记忆晋升 gate 的开关与状态流转）；README 需附「操作剧本」：一步步怎么操作、看到什么现象、对应哪条研究结论。W1 recovery demo 已定稿不追溯，W2 起的 demo 一律适用。
7. **前端技术栈**：demo 如需图形界面，前端尽量用 React Native 生态（Expo / react-native-macos），**避免 Electron**；不引入 Electron 是默认项，确需偏离时在决策记录中说明理由。
8. **后端 Python 版本一致**：所有 demo 后端统一 Python 3.14（当前基线 3.14.6，与 w1-recovery-demo 实测版本一致），README 记录实测解释器版本（含 sqlite 版本）；跨 demo 不得混用不同大版本解释器。

## 5. 提交规范

- **提交身份**：本仓库统一配置为 `noire02qwq <noire02qwq@users.noreply.github.com>`（GitHub noreply，仓库级 git config，不改全局）。
- 使用 Conventional Commits：`feat`（新增内容）/ `docs`（文档修订）/ `research`（文献笔记、调研结论）/ `demo`（demo 索引更新）/ `chore`（杂项）。描述用中文，例：`research(w2): 新增长程上下文管理文献笔记`。
- 主分支 `main`。设计修订、规范类改动建议走 feature 分支 + PR；文献笔记/决策记录可直接提交 main。
- 每次提交前检查：无 `.DS_Store`、无凭证文件、无 demo 本体误入。

## 6. 敏感信息

- API key、token、券商/数据源凭证、真实账户与资金信息**一律不入库**；本地配置写 `.env`（已在 .gitignore）。
- 涉及真实资金的操作（哪怕模拟盘转实盘的参数）在文档中只写方案，不写可直接执行的凭证化脚本。
- **公司 harness 项目相关源码严禁入库**（2026-11-01 用户规定）：本仓库为公开仓库，只承载个人研究成果；公司项目至多可在文档中少量提及（不引用内部仓库、不贴内部代码/架构细节）。此规范在用户后续拉出 harness 分支后依然适用于 main。

## 7. 分支与协作

- 研究（@research）与开发（@dev）在 main 上协作：文献/决策文档归研究，平台仓库代码归开发，本仓库只同步设计修订。
- 当 brief-plan.md 与平台仓库实现出现分歧时，以本仓库的设计修订 + 决策记录为准，并同步更新平台仓库的实现说明。
