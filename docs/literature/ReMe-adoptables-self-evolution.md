# ReMe 项目可采取部分研究（自进化向）

> 日期：2026-11-20 ｜ 作者：@research ｜ 状态：**研究交付，采取项待 @user 拍板** ｜ 触发：@user「研究 reme 项目对于自进化的可采取部分」
>
> 依据（一手）：①仓库 `github.com/agentscope-ai/ReMe`（Apache-2.0，3.8k★，前身 MemoryScope）README、`docs/en/auto_dream.md`、`docs/en/memory_as_file.md`、`docs/en/framework.md`（均 2026-11-20 curl 实取）；②论文 **Remember Me, Refine Me: A Dynamic Procedural Memory Framework for Experience-Driven Agent Evolution**，arXiv `2512.10696v2`（2026-04-15 v2，20pp，**ACL 2026 Findings**，Cao et al.，交大+通义实验室）摘要与正文段（curl export.arxiv API 实取）；③集成矩阵（README/博客）。
> 映射对象：harness-hub 功能二（L2 自进化，[decisions/0007](../decisions/0007-self-evolution-l2-positioning.md)）、复盘缺口 G1–G8（2026-11-19 复盘）、[W2](W2-context-memory-distillation.md)/[W6](W6-self-evolution-rsi.md) 笔记、SIM（2611.18856）。

---

## 1. 项目双身份

| 身份 | 实体 | 与「自进化」的关系 |
|---|---|---|
| **工程项目** | `agentscope-ai/ReMe`：local-first **自进化个人知识库**——「Memory as File, File as Memory」，Markdown+frontmatter+wikilink 即记忆节点；`capture → index → consolidate → recall` 四环；集成面含 **DSH 插件**（`reme_search`/轮次捕获/定时 Auto Dream/ReMe Status）与 Hermes provider（**调用前 recall + 轮后异步 auto_memory**） | 自进化=**知识库的进化**（记忆的提炼、整合、召回），属 L2 记忆脚手架，**不含**策略自改/失败重进/改目标重规划 |
| **论文** | arXiv 2512.10696（ACL'26 Findings）：三机制——multi-faceted distillation / context-adaptive reuse / **utility-based refinement**；另含 failure-aware reflection 与 memory-scaling 实证 | 与我们 W6 文献线同族（SIM/遗忘曲线邻域），**直接可抄的工程参数最多** |

**能力边界先例（可引用）**：ReMe v4 明文「单会话上下文管理超出范围（压缩/注入摘要/trim 属宿主框架职责）」（framework.md Capability Boundary）——与我们 0007 的 L2 边界声明同法，可作「能力边界写进 spec」的业界先例引用。

---

## 2. 机制清单（一手实取）

**工程面（repo docs）**：
- **四层工作区**：`session/ + resource/`（源记录）→ `daily/`（轻加工日记忆）→ `digest/{procedure,personal,wiki}/`（长期记忆三分桶）→ `metadata/`（**可重建**索引/图/缓存，非事实源）；
- **auto_dream（daily→digest 蒸馏，四步流水）**：①Extract——扫描 `scan_days=2` 变更窗（mtime 对比 file_catalog，只取变更文件），**跨文件全局提取**结构化 units（`name/bucket/summary/paths`），**单轮 `max_units=5` 封顶**，合并同抽象、丢弃顺带提及/逐文件摘要/弱候选；②Integrate——**逐 unit 独立 agent**，先 `node_search` 召回相似节点，再对单个 digest 节点执行 **create / corroborate / refine / correct** 四动词（并承担 auto_link）；③Finish 目录小结；④auto_tag；
- **auto_memory**：轮次蒸馏为日卡，**保留过滤后的会话源记录**（`session/dialog/*.jsonl`，刻意剔除工具结果与 base64——防「工具输出冒充用户证据」）；
- **检索**：BM25 + 可选向量（RRF 融合）+ wikilink 图扩展，**行级段落**召回（不整库进上下文）；
- **proactive_read**：读 `daily/<date>/interests.yaml` 兴趣主题，**宿主 agent 决定是否提及**（不自主联网/不改库）。

**论文面**：①**multi-faceted distillation**——细粒度提取三面：成功模式 / 失败触发 / 对比洞察；②**context-adaptive reuse**——场景感知索引 + 重排 + 自适应改写，把历史洞见裁进新任务上下文；③**utility-based refinement**——**复用时追踪每条经验的效用**，增验过的、剪过时低效的，保持池子紧凑；④**failure-aware reflection**——失败→LLM 提炼教训→重试，**教训只有后续 trial 成功才入记忆、失败即丢弃**，**自反思上限 3 次**（防模型能力不足死循环）；⑤实证：BFCL-V3/AppWorld SOTA；**memory-scaling**——Qwen3-8B+ReMe > 无记忆 Qwen3-14B（Avg@4 +8.83% / Pass@4 +7.29%）；附 `reme.library` 数据集（成功模式+失败教训结构化语料）。

---

## 3. 可采取部分（按优先级；每条=现状→采取形态→依据→落点）

| # | 采取项 | 我们现状 | 采取形态（适配 L2/事件流/0003/0007） | 依据 |
|---|---|---|---|---|
| **A** | **记忆效用账本（utility-based refinement）** | 有生命周期状态机（候选→活跃→稳定/supersede，0003/W2）但**无「召回后是否真帮到忙」的回路**——记忆只进不出、不辨优劣 | 记忆卡加 `reuse_count / hits / misses`：召回注入→执行结果回写效用；低效用**降级或标 stale（不物理删——0003 supersede+事件审计，比论文的 prune 更合 0007 可回滚）**；低效用同时是 G7（投毒/可疑）信号之一 | 论文机制③；与 G5 试验账本同族近邻 |
| **B** | **失败教训「成功才入库」+ 反思上限 3** | 失败修复重进（R7/W5）在，但**失败教训直接沉淀，无验证门槛** | 失败教训一律落**候选态**，**须被一次后续成功 trial 证实才升活跃**；自我反思/重试循环**硬上限 3 次**（超限转人工，接 W5 恢复语义） | 论文 failure-aware reflection（≤3、成功才入库两条原样可抄）；与 SIM 可证伪（2611.18856）同族，**直接强化 G2 修法** |
| **C** | **三面蒸馏 schema（闭 G2）** | 蒸馏单形态（一句话教训）；**复盘 G2 实锤：`memory_lifecycle.py` 94 行无预测/观察字段** | 蒸馏结构改三面：**成功模式 / 失败触发 / 对比洞察**，并强制**预测 vs 观察成对**（SIM）——记忆卡 schema 一次补齐 | 论文机制① + SIM + G2 缺口 |
| **D** | **auto_dream 四步流水参数** | 蒸馏的触发窗、批量上限、同抽象合并、弱候选丢弃均无工程化定义 | 照抄：**变更窗 2 天（mtime 增量，不全量扫）**、**单轮 ≤5 units 封顶**、跨文件同抽象合并、弱候选不入池；**逐 unit 独立 agent，先 node_search 召回相似再四动词整合**（create/corroborate/refine/correct = 我们 supersede 的超集） | repo `auto_dream.md` 实文（scan_days=2/max_units=5/四步/工具清单） |
| **E** | **召回环（recall-before-act）** | 记忆面板只展示；**执行上下文不注入相关记忆**——四环缺最后一环 | goal runner 起步前检索相关记忆卡注入 prompt（BM25 级即可，事件流可查）；召回的记忆同时作为**提案诊断上下文**（G3 修法的一半） | capture→index→consolidate→**recall**；DSH/Hermes 集成的 call-time recall 模式 |
| **F** | **Memory as File 导出视图** | GoalEvent JSON + 面板只读 | **单向导出**记忆为 md（frontmatter+Sources 溯源段，Obsidian/VSCode 可读）；**编辑走事件回写**（改文件=新事件），保持事件流单一事实源——不引双写 | memory_as_file.md 设计目标表（Readable/Editable/Traceable/Portable/Indexable/Collaborative） |
| **G** | **能力边界声明先例** | 0007 已有 L2 边界 | 无需实现——引用 framework.md「单会话上下文管理属宿主职责」作为边界的业界同款表述 | framework.md Capability Boundary |

**佐证数字（引用即用）**：memory-scaling（8B+记忆 >14B 无记忆，+8.83%/+7.29%）与 BFCL-V3/AppWorld SOTA——支持 0007「L2 脚手架是算力高效路径」的定位表述；`reme.library` 数据集可作我们蒸馏 prompt 的对照语料。

---

## 4. 不采取 / 暂不采取（含理由）

1. **不把 ReMe 整体换装为 harness-hub 记忆后端**（DSH/MCP 集成现成，是真实备选）——我们已有 CALM 链+事件流+记忆面板（自研在位），换装=引入外部服务依赖+双写+两套事实源；**触发条件**：若未来要**跨 agent 共享同一记忆工作区**（ReMe 最强卖点），再做 A/B 评估立项。
2. **proactive interests/主动探索**——超出功能二范围（Phase2 邻域，同 0007 的 L3+ 不沾边）。
3. **context compaction/单会话压缩**——ReMe 自己都划给宿主，我们同样不做（非记忆层职责）。
4. **论文的 scenario-aware rerank/改写管线**——检索质量项，等 E（召回环）落地后有真实召回数据再评估，避免先建管线后找场景。

---

## 5. 与既有决策/缺口的映射速查

- **0003（supersede 不删）**：A 的降级/剪枝必须走事件审计，不物理删——比论文更严，保留我方口径；
- **0007（L2 定位）**：G 的边界先例 + 佐证数字；ReMe 的「自进化」恰= L2 记忆面，**不含**功能二其余三件（失败重进/改目标重规划/回归护栏）——覆盖对照表见 §2 末；
- **复盘缺口**：**C→G2**（预测/观察字段）、**E→G3**（提案诊断上下文之半）、**A→G5 邻域**（效用账本与试验账本同构互补）、**A→G7**（低效用=可疑信号）；
- **IN4/SIM**：C、B 是 SIM 的工程落地位；W6 笔记的「遗忘曲线 94→32」（2611.03219）说明只增不减必退化——**A 正是对此的结构性回应**；
- **G1（对比分辨率）**：ReMe 未解（其 utility 是逐条复用效用，非策略对比），维持 v1.1 排期不动。

---

## 6. 状态

- 采取项 A–G **待 @user 拍板**；拍板后建议按 A+C（记忆卡 schema 与效用字段一并设计，一次迁移面）→ B+D（蒸馏/反思流水）→ E（召回注入）排期，全部零迁移可走事件流/字段扩展。
- 未做全文 PDF 精读（摘要+正文引用段+repo 实文已足够支撑采取判断）；若进入实现，补读论文 §3 utility 度量细节（效用=复用成功判据的具体定义）。
