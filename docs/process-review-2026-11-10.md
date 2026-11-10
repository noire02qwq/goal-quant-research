# 研究-开发流程规范复盘（process-review-2026-11-10）

> 状态：定稿（发现项分「已修正 / 待拍板 / 观察项」三级，待拍板项不擅自改设计）｜ 日期：2026-11-10 ｜ 触发：@user 指令「重新复盘 goal-quant-research 中整个的研究、开发的流程规范」
>
> 复盘方法：通读 `docs/CONVENTIONS.md`、根 `README.md`、`docs/brief-plan.md` §12、`docs/PROGRESS.md`、三份模板、`.github/` CI 与 PR 模板；`git log` 全量 23 提交按类型/作者统计；GitHub 分支保护 API 实测；decisions/demos/literature/essay-study/translations 各目录逐一清点对账。所有数字为 2026-11-10 实测。

## 1. 现行流程全貌（实际怎么转的）

```
研究（@research）                     开发（@dev）
  文献检索/精读 → docs/literature/W<n>-*.md
  源码走读      → docs/essay-study/*-<年>.md
  翻译/可读性   → docs/translations/、audit
        │
        ▼
  决策记录 docs/decisions/NNNN-*.md（先于设计）
        │  提议 → 复核 → 已采纳
        ▼
  brief-plan 定点修订（对应小节留痕：改了什么/依据哪份研究）
        │
        ▼
  demo/插件开发（research-demos/ 入库 + PR #1–#8）
        │
        ▼
  双轮独立核验（@dev 核 @research 走读行号；@research 核 @dev demo 复跑）
        │
        ▼
  PROGRESS.md 追加指针化条目（只记结论与链接）→ 推送 main
```

**角色分工**（CONVENTIONS §7）：文献/决策/走读/翻译/核验归 @research；平台代码与 demo 实现归 @dev；设计分歧以本仓设计修订 + 决策记录为准。

**实测健康度（2026-11-10）**：

| 指标 | 实测 |
|---|---|
| 提交 | 23 笔；类型 docs 12 / research 5 / chore 3 / demo 2 / ci 1 |
| PR | #1–#8 全合入；PR 模板「依据哪份研究」必填 |
| 决策记录 | 3 篇（0001–0003），**文件内状态全部为已采纳** |
| 入库 demo | 2 个（w1-recovery、w2-memory-distillation），均带操作剧本 |
| 周文献笔记 | 2 篇（W1/W2），W3 随暂停令未开 |
| 走读笔记 | 5 篇（rakazo/opendots/openmuse/hermes/deepseek）+ 本轮新增 anthropic-agent-memory |
| 翻译 | 67 篇（papers 8 全文 / literature 30 / projects 29）+ README，机器终检通过 |
| 论文 PDF | 8 份归档 docs/papers/ |
| CI | doc-lint：PR 标题 Conventional Commits、敏感文件/.DS_Store 守卫、markdown 行尾检查（警告级） |

## 2. 发现的不一致（按处置分级）

### 已修正（本轮直接改）

| # | 问题 | 证据 | 处置 |
|---|---|---|---|
| P1 | **索引状态过期**：`decisions/README.md` 归档表把 0002/0003 标为「提议」，`research-demos/README.md` 索引同样标「（提议）」，但两篇决策文件头与 PROGRESS 均为「已采纳」（0003 于 2026-11-01 文献复核后转正、设计修订 PR #8 已合入） | 三处交叉对账 | 两处索引已改为「已采纳」 |
| P2 | **本地目录无文档入口**：`oss-repos/`（本轮起含 claude-cookbooks/claude-quickstarts 共 7 仓）与 `harness-hub/`（12G 本地副本）均为 gitignore 本地目录，但根 README 目录树与 CONVENTIONS §2 目录表都没提，新会话容易误判其存在或误提交 | `.gitignore:47/55`、目录实测 | README 目录树与 CONVENTIONS §2 各补两行，标注「本地、不入库」 |

### 待拍板（涉及规范/设计变更，不擅动）

| # | 问题 | 证据 | 建议 |
|---|---|---|---|
| P3 | **「文档可直接提交 main」与分支保护冲突**：CONVENTIONS §5 与根 README 都写「文献笔记/决策记录可直接提交」，但 main 实测保护为 PR 必须 + `lint` status 必须（strict），实际靠管理员 bypass 直推（@dev 2026-11-04 推送即触发 bypass） | 分支保护 API 实测；git log 直推记录 | 二选一：①规范改为「一律 PR」；②维持 bypass 并在 §5 写明「admin 直推为例外操作，需在 PROGRESS 留痕」 |
| P4 | **提交身份不统一**：CONVENTIONS §5 要求统一 `noire02qwq`，实测 3 个作者（noire02qwq 13 / 夕波千鳥 8 / Yuunami 2）——后两者来自 PR squash 合并的作者名与初始提交 | `git log --format='%an'` | 拍板口径：历史不追改；今后 PR 合并统一 squash 署名 noire02qwq，或在 §5 注明「PR 合并作者名可异」 |
| P5 | **spike-report 模板与规范矛盾且零使用**：模板写「demo 本体不入库、位置 `~/Desktop/goal-agent-research/<主题>/`」，与 CONVENTIONS §4 规则 2「后续 demo 一律入库 research-demos/」相反；磁盘上 0 份 spike 报告（W1/W2 直接走了决策记录 + demo README） | `docs/templates/spike-report.md`、`find` 零命中 | 改模板措辞（demo 本体指入库路径，spike 报告仅作本地快速验证索引）或废止该模板 |
| P6 | **brief-plan §12.0 与 CONVENTIONS §4 矛盾**：§12.0 仍写「研究 demo 是临时产物，放本地 scratch 目录」，而 CONVENTIONS §1 还把 §12.0 引为「demo 位置约定」的设计依据；实际 W1/W2 demo 均入库 `research-demos/` | brief-plan L463 附近 vs CONVENTIONS §4 规则 2 | 按 CONVENTIONS §3 规则 7 给 §12.0 定点修订留痕（「demo 位置以 CONVENTIONS §4 为准，本节 scratch 表述废止」） |
| P7 | **可读性排查修复仍挂起**：2026-11-03 audit 列出的 28 处墙式段落、brief-plan 583 行无目录、4 处缺状态头，因「会移动 @dev 已核验的行号引用」标为待拍板，至今未处理 | `docs/readability-audit-2026-11-03.md`、`wc -l docs/brief-plan.md`=583 | 批量改后请 @dev 重核行号引用，一次闭环 |

### 观察项（不急）

- **O1** `docs/PROGRESS.md` 单文件倒序日志持续增长（本轮又 +1 条）；若到 W5 汇报仍单文件，可按月归档 `PROGRESS/2026-11.md`，根文件只留当前阶段与最近 3 条。
- **O2** 文献线 W3 起未开（暂停令维持），`docs/literature/` 仅 W1/W2——非流程问题，等令。
- **O3** 翻译 `projects/` 仓库短名清单（translations/README §2）未含 claude-cookbooks/claude-quickstarts；本轮只走读未翻译，若后续要中译再补登记。

## 3. 运转良好、保持不动的部分

1. **决策先行 + 设计留痕**：0002/0003 均「demo 跑通 → 决策记录 → brief-plan 定点修订（PR #4/#8）」，推翻假设有显式留痕（hermes watchdog 推翻一例）。
2. **双轮独立核验**：走读行号由 @dev 逐条回源（Rakazo `assigned_role` 缺席、OpenDots 100ms/50ms 等精确命中）；demo 由 @research 独立复跑（12/12 unittest）。
3. **溯源硬要求**：引用无链接视为未溯源；仅摘要级标注制度在 W1/W2 笔记中执行到位。
4. **机器终检**：翻译六字段头/段落上限/围栏/断链由脚本三轮快照验证，人工核看误报——可读性治理从「人看」升级为「脚本+人」。
5. **CI 守卫**：敏感文件、.DS_Store、PR 标题规范三道自动门；demo 新规范（可交互剧本 / RN 不用 Electron / Python 3.14 统一）自 W2 起执行无回退。
6. **PROGRESS 指针化**：只记结论与链接、细节回链对应文档，日志没有变成第二正文。

## 4. 建议的下一步顺序

1. （本轮已做）P1 索引修正、P2 本地目录文档化、流程复盘落档、Anthropic agent memory 走读笔记入库。
2. 待 @user 拍板：P3 直推 vs PR 口径 → P6 §12.0 留痕修订 → P5 模板去留 → P4 署名口径（可合并一次规范修订 PR）。
3. P7 可读性批量修复排期（改后 @dev 重核）。
4. 观察项 O1–O3 到对应时点再动。

## 5. 本轮产出与边界

- 新增：`docs/essay-study/anthropic-agent-memory-2026.md`（Anthropic 记忆博客 + cookbook/quickstarts 走读）、本复盘文件。
- 本地：`oss-repos/claude-cookbooks`（410MB，HEAD `ce8b262`）、`oss-repos/claude-quickstarts`（17MB，HEAD `4a4224b`）浅克隆，已被 `.gitignore` 覆盖。
- **brief-plan.md 落库前工作区改动披露（@dev 核验发现，2026-11-10）**：工作区存在一处**非本复盘产出**的内容更正——附录「已确认决策记录」第 8 条 `文档位置：Desktop（用户指定，不进仓库）` 改为删除线标注「正式开启研究后已进仓库」（来源为落库前的编辑器改动，@research 本轮未 patch 此文件；内容与仓库现状一致，予以保留并在此披露）。同批的**表格格式化噪声已还原**（`git checkout`），其中被格式化破坏的 `` `test_expired_*` `` code span 与 Rakazo 行 bold 断行一并复原；还原后 brief-plan 仍 583 行、`git diff` 仅剩上述第 8 条一处。
- 未触碰：brief-plan 正文实质设计章节（P6 只列建议未改）、W3/harness 暂停令、平台仓库。
