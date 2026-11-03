# 文档人类可读性排查报告（2026-11-03）

> 状态：定稿 ｜ 触发：@user 2026-11-03 指令「排查当前工作区所有文档要求人类可读性」
> 范围：`goal-quant-research` 仓库全部自有 markdown（28 个，含根 README、docs/、research-demos/、.github/ 模板）；`independent-demo-apps/vn-demo/` 单列观察；`oss-repos/`、`harness-hub/`、`node_modules/`、`.venv/`、`Pods/` 为第三方/忽略目录，不在排查范围。

## 1. 排查方法与判定标准

标准取自 [CONVENTIONS.md](CONVENTIONS.md) §3（语言/溯源/引用链接/状态头）与 [translations/README.md](translations/README.md) §4（本次确立的可读性硬要求：自然中文、结构对齐、单段 ≤500 汉字、术语保留英文、诚实标注）。机器检查项：

| 检查项 | 判定 |
|---|---|
| 标题层级跳跃（H1→H3 断层） | 全部 28 文件 **0 跳跃** ✅ |
| 代码围栏配对（``` 奇偶） | 全部 **配对完整** ✅ |
| 相对链接可达性 | 自有文档 **0 断链** ✅（vn-demo `findings.md` 1 处 `params 内` 为方括号误报） |
| `.DS_Store` 入库 | **0 个被追踪** ✅（磁盘上 `docs/.DS_Store` 存在但已 ignore） |
| 状态头（§3.8 `> 状态：`） | 见 §3 问题 3 |
| 墙式段落（连续段 >600 字符） | 见 §3 问题 1 |
| 单行长度 / 英文占比 | 见 §3 问题 2、4 |

## 2. 总体结论

**结构层全部健康**：无断链、无标题断层、无围栏破损、无敏感文件入库——引用链（arXiv 链接 187/172/97/16 条级的走读笔记）可点可溯。**问题集中在「排版可读性」而非「结构正确性」**：墙式段落、英文占比、缺状态头、大文档无目录，共 4 类，全部有明确修复方案（§4），但修复会使 @dev 此前逐行核验引用的行号位移，**列为待拍板项，本轮未改任何既有文档**。

## 3. 问题清单（按严重度）

### 问题 1（P1）：墙式段落——最长 3996 字符

连续正文段 >600 字符共 28 处，超 1000 字符的重灾区。**切分口径**：按空行/列表项边界切分，单个列表项或段落各算一段（@dev 复算按空行合并无空行的连续列表项，openmuse 测得 5365；两口径都远超 500 上限，结论一致，此处取更保守的单元粒度）：

| 文件 | >600 段数 | 最长段（字符） |
|---|---|---|
| [essay-study/openmuse-2026.md](essay-study/openmuse-2026.md) | 2 | **3996** |
| [essay-study/rakazo-2026.md](essay-study/rakazo-2026.md) | 5 | 3454 |
| [essay-study/deepseek-super-agent-2026.md](essay-study/deepseek-super-agent-2026.md) | 3 | 2773 |
| [essay-study/opendots-2026.md](essay-study/opendots-2026.md) | 2 | 1630 |
| [brief-plan.md](brief-plan.md) | 4 | 1352 |
| [decisions/0002-w1-recovery-semantics.md](decisions/0002-w1-recovery-semantics.md) | 2 | 1283 |
| essay-study/hermes-2026.md、decisions/0003、CONVENTIONS、根 README | 各 1–2 | 821–985 |

对照 translations §4 的 500 汉字上限，**全部超标 1.6–8 倍**。走读笔记是重灾区，原因是把「论断+证据+行号」写进一整段。

### 问题 2（P1）：走读笔记英文占比过高

英文单词数 vs 中文字符数：opendots **2927 : 3288**（≈1:1.1）、rakazo 4398:5934、openmuse 2266:2890、hermes 1083:2870。代码标识符、文件路径保留英文是规范要求（§3.1），但散文叙述里夹大段英文原文引用（非代码块）会显著降低阅读速度。deepseek 笔记（556:2281）是正面样板。

### 问题 3（P2）：状态头缺失（CONVENTIONS §3.8）

应标未标的**实质性文档**：`brief-plan.md`（主设计文档，只有日期无状态）、`essay-study/` 的 **hermes / openmuse / rakazo** 三篇（同目录 deepseek、opendots 已标，标准不一致）。`mission.md` 为需求原文可豁免；各 README/模板不强制。

### 问题 4（P2）：大文档无目录 + 超长行

- `brief-plan.md`：583 行 / 38 个标题 / 无目录；最长单行 1349 字符（表格行，渲染正常但源码视图难读）；全文件 49 行 >400 字符。
- `essay-study/openmuse-2026.md`：23KB / 9 标题，无目录（未达 15 标题硬门槛，但 131 行里最长单行 1140）。
- opendots 最长单行 **1979**、rakazo 1212——均为宽表格行。

### 问题 5（P3，观察项，不动）

- `independent-demo-apps/vn-demo/`（独立仓库，本仓已 ignore）：两对**完全重复文件**（`2026-10-21-desktop-rnmacos-shadcn{,-design} 2.md`，与无 ` 2` 后缀版内容 MD5 相同）、空文件 `task-0-brief.md`（0 字节）、`findings.md` 77KB 无目录。
- `docs/.DS_Store` 磁盘残留（已 ignore，未入库）。

## 4. 修复方案与处置状态

| # | 修复 | 状态 |
|---|---|---|
| 1 | 28 处墙式段落拆分（拆段或改列点，单段 ≤500 汉字） | **待拍板**：会移动 @dev 已核验的行号引用（如 `brief-plan.md:83`、hermes 笔记第 8 行），建议一次性改完后请 @dev 重核 |
| 2 | 走读笔记散文段的英文长引文移入代码块或译注 | **待拍板**，同上 |
| 3 | brief-plan + hermes/openmuse/rakazo 四处补 `> 状态：定稿` | **待拍板**，同上（插入行即位移） |
| 4 | brief-plan 顶部加目录（38 标题）；openmuse 观察项 | **待拍板**，同上 |
| 5 | vn-demo 重复/空文件 | 不动——独立仓库，非本仓管辖；已在本报告留痕 |
| 6 | 新增译文目录的可读性 | ✅ 已落实：[translations/README.md](translations/README.md) §4 把上述标准写成硬要求，全部译文按此产出并逐篇自查 |

**处置原则**：本轮只排查、不改既有文档——两轮独立核验（`d36e83a`/`f6c99b6`）刚建立的行号证据链不因排版改动失效。修复 1–4 若 @user 拍板，走单次批量修订 + @dev 重核。

## 5. 排查产物

- 本报告：`docs/readability-audit-2026-11-03.md`
- 可读性标准固化：`docs/translations/README.md` §4（适用全部新增译文）
- 范围与例外：`oss-repos/`（上游克隆，保持原文）、`harness-hub/`（公司仓，禁改禁入库）、`vn-demo/`（独立仓库，仅观察）
