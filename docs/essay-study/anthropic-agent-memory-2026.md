# Anthropic《The components of agent memory》精读与 cookbook/quickstarts 源码走读笔记

> **状态**：已完成精读与静态走读（博客全文 + notebook markdown 单元全文 + 辅助脚本全文/头部；未编译、未运行、未跑通——本机无 Managed Agents 凭据）。
> **精读日期**：2026-11-10。
> **材料与版本**：
> - 博客：[The components of agent memory](https://www.anthropic.com/research/components-of-agent-memory)（Anthropic Engineering，2026-11-06，作者 Lance Martin）。
> - 本地克隆 `oss-repos/claude-cookbooks`（`.gitignore` 覆盖，不入库），`origin = https://github.com/anthropics/claude-cookbooks.git`，HEAD = `ce8b262`（2026-11-04）。
> - 本地克隆 `oss-repos/claude-quickstarts`（同上），HEAD = `4a4224b`（2026-11-06）。
> - 配套文档：[Dreams API 文档](https://platform.claude.com/docs/en/managed-agents/dreams)（@dev 2026-11-08 核对 beta header `dreaming-2026-04-21` 仍有效）。
> **精读范围（读了什么）**：
> - 博客正文（分段抓取全文）。
> - `managed_agents/CMA_dreaming_with_a_dynamic_workflow.ipynb`：全部 markdown 单元（1301 行 notebook），代码单元只读结构不逐行。
> - `managed_agents/dreaming_nightly.py`（全文 91 行）、`managed_agents/memory_distill_utils.py`（前 80 行 + 文件头 docstring）。
> - `managed-agents/knowledge-wiki/README.md`（全文）与目录清单、`prompts/` 文件名清单。
> - 博客外链的第三方报道（用于交叉核对数据口径，均已在正文标注）。
> **没读的（明确未读，不得当作依据）**：notebook 全部代码单元逐行、`memory_distill_utils.py` 其余 2500 行、quickstart 的 `utilities.py`/`distill_*.ipynb` 内容、cookbook 仓库其余 16 个 notebook、Dreams API 的 OpenAPI 全量 schema、平台端实现。**因此本笔记对"运行期实测行为"不作断言**：所有 benchmark 数字均为 Anthropic first-party 报告值，未经独立复现（第三方评述同样标注 claimed_unverified）。

---

## 0. 一句话结论

Anthropic 把 agent 长期记忆定成 **四层存储（transcripts → notes → representations → injected context）+ 离线 "dreaming" 归档整理** 的工程蓝图：**memory 是对未来的预测而非日志转储**（写得少而准优于写得多），提示词只该告诉模型"记忆是干什么的"而不是"怎么写"；官方 cookbook 用 Managed Agents 的 dynamic workflow 实现了一个可每晚 cron 的 dream，**不依赖 Dreams 原生 API**。

---

## 1. 博客核心机制

### 1.1 定义边界（对齐本项目术语）

agent memory = "Claude 从经验中获得、跨会话保留、以后可读回的 context"，**明确排除**：①权重更新 ②单对话 in-context learning ③compaction 摘要（[博客](https://www.anthropic.com/research/components-of-agent-memory)）。→ 与 brief-plan §5.4 的"记忆蒸馏产物"口径一致：我们落库的 `goal_memory_digest` 属于此类，回测/权重侧不算记忆。

### 1.2 四层结构与"memory as prediction"

| 层 | 内容 | 要点 |
|---|---|---|
| transcripts | 会话日志原文 | dream 的输入 |
| memory notes | 会话中写的便签 | 写入时打 salient 标签 |
| memory representations | wiki 等重组表示 | dream 构建/修正 |
| injected context | 预加载进未来会话的片段 | Claude Code 的 MEMORY.md 只取前 200 行/25KB 作索引 |

核心论断："**By writing down a rule, an agent predicts that the pattern it's describing will be relevant again**"——写记忆是对未来的赌注，因此写错的记忆比没有记忆更贵（顶层注入的错误记忆会污染**每一个**后续会话）。

### 1.3 Dreaming（离线整理）

会话间空闲期重读日志：纠错笔记、建 wiki、决定下次预加载什么。概念credit给 Letta/UC Berkeley 的 [sleep-time compute](https://arxiv.org/abs/2504.13171)；产品侧 2026-05 在 Managed Agents 以 research preview 发布，本次是**首个系统性评估**。API 设计非破坏性：输入 store 不动，输出克隆重组后的 store（可审计/回滚）。

### 1.4 评估与数据（均 first-party，未复现）

- **CL-Bench 1.0**（数据库问答长程任务，每题新会话 + 持久记忆目录）：Opus 4.7 带记忆 mean reward 0.383→0.700、Opus 5 0.564→0.828、Opus 5.5 0.655→0.838（数字据 [FCMO 摘录](https://fcmo-ai.github.io/FCMO-AI-Newsletter/2026/11/07/anthropic-reports-internal-tests-of-persistent-memory-and-offline.md) 与 [AI/TLDR](https://ai-tldr.dev/releases/anthropic-components-of-agent-memory) 交叉核对）。模型代际差异=学习闭环成熟度：Sonnet 4.6 只有未检验猜测 → Opus 4.7 单文档汇总+标注已核 → **Opus 5 起闭环**（规则+依据+历史答案+陷阱警告）。
- **Pokémon Red 显著性判断**：Sonnet 3.7 写 413 文件/225 目录只得 1 徽章（游戏状态常变，档案永不过期 → 第 10000 步起 17 步内建 6 删 9 不动游戏）；Fable 5 写 9 文件 + `global.md` 得 4 徽章。→ **少而准胜过多而全**。
- **Wiki 收益边界**：35 万文件（约 420M tokens）语料，dreaming 2→128 会话使 25 题得分 13%→48%；wiki+search 61% vs search-only 53%；并购 24 题 wiki 87% vs 纯搜索 73%；**单文档可检索题无增益**，且出现过 wiki 比源文档还大的 Borges 式失败；wiki+search 每题省约 2 万 token。
- **提示词工程结论**：原则是"**告诉 Claude 记忆是干什么的，不要规定怎么写**"——给强模型加"只记失败"类硬规则反而**削弱**记忆收益（Opus 5/4.7 均下降）；steering 只救老模型（Sonnet 4.6 加"答前先读记忆+显式检验假设"几乎翻倍；Sonnet 5 十次里九次自发读）。
- **开放问题（博客自述）**：dreaming cadence 应按**记忆被访问频率**调，而非全量循环校验——明确未解点。

### 1.5 多 agent 并发写共享页的竞态（对 §12.2 的直接教训）

LAB 合同任务中多个 agent 同写**一张共享表**互相覆盖，57 条事实只留 41 条（72%）；改为"**每份合同一个 agent、独占一页、逐字引用条款**"后 57/57（100%）。
→ **设计含义**：brief-plan §12.2 W2 的共享 blackboard（`scope=shared` 的 `goal_memory_digest`）必须**分片或按 author 串行化写入**，共享可写页无分片必然丢写。这一条与 Rakazo 走读的"一阶段一主"、W1 的 consume-once 幂等同族，建议在 §12.2 补一句写入分片规则（**待 @user 拍板后改 brief-plan**）。

---

## 2. Cookbook 源码走读（`oss-repos/claude-cookbooks`）

### 2.1 架构：dynamic workflow 实现 dream（不走 Dreams API）

[`CMA_dreaming_with_a_dynamic_workflow.ipynb`](https://github.com/anthropics/claude-cookbooks/blob/main/managed_agents/CMA_dreaming_with_a_dynamic_workflow.ipynb)（93KB，1301 行）：

1. **Load**：把 agent 已结束 session 导出为 transcript 文件（一 session 一文件；示例是 11 个 `tidewick` 合成文件——10 个编码会话 + 1 份团队聊天 md；难点刻意设计：事实过期/互相矛盾/分散多文件）。
2. **Dream**：单条普通 `user.message` 描述工作 → lead agent（`memory-distiller`，只有 read/glob 工具，读不到 transcript）**自己写 workflow** 并启动 workflow run → 平台跑两阶段：**Analyze**（每 transcript 一个 analyzer，并行分批约 20 个）→ **Organize**（一个 organizer 收尾）→ 产物是带 `_index.md` 目录的 memory store。
3. **Use**：未来 session 以 `access: "read_only"` 挂载 store + 一行 `instructions`；部分预加载 = 创建 session 时读小文件（如 `_index.md`）作 mount instructions。

关键事实：
- **与 Dreams 原生 API 的区分**：notebook 全程用 agents/sessions/workflow-runs（`grep beta.dreams` 零命中）——**只依赖 Managed Agents beta，不需要 Dreams research preview 的 Request access 门票**（@dev 2026-11-08 结论，本地复核一致）。
- **预算门**：首 cell 先估价，超 `BUDGET_USD`（示例 $40）直接停，什么都不创建；示例 11 条 transcript 实测约 **$0.36 / 2.5 分钟**（cookbook 口径）。
- **清理语义**：中途失败清掉整个 run 的一切（session/upload 删除、agent/environment 归档），**只有 store 留下**；成功路径也提供 **Clean up** cell。→ 对 W1 恢复语义的参照：这是"要么全有要么全无"的另一侧，与我们 `outcome_unknown` + 恢复扫描的设计不冲突（不同层）。
- **审计**：每次写入都是可审计的 **memory version**，run 前先复制一份 store 文件（[Dreams 文档](https://platform.claude.com/docs/en/managed-agents/dreams)同口径）。

### 2.2 `dreaming_nightly.py`（全文 91 行）——每晚 cron 的状态机

[`dreaming_nightly.py`](https://github.com/anthropics/claude-cookbooks/blob/main/managed_agents/dreaming_nightly.py)：

- **窗口状态**存 `~/.cache/memory_distill/nightly.json` 的 `last_run`；**失败之夜保留窗口、下一晚重取同一批 session**（exit 1，`state[“last_run”] = since`）——即 **at-least-once 重放语义**：失败后同批 transcript 会被再次 dream。→ 推论：analyzer 对同一 transcript 的**更新必须幂等/可覆盖**，否则重放会污染 store。这与 W1 决策 0002 的"幂等回执"同构，可作 §5.2 规则 4 的外部佐证。
- **无无人值守安装**：删掉且只允许一个 `%pip install` cell（形状变了直接 `sys.exit`）——notebook 结构漂移即失败，不静默降级。
- 日志 ipynb 与状态文件 `chmod 0600`（含记忆文本与 transcript 摘录，按敏感处理）——对应 CONVENTIONS §6 的本地敏感文件纪律。
- `NothingToDistill` 视为成功（exit 0）；`COOKBOOK_SINCE` 支持自定义窗口起点。

### 2.3 安全边界（notebook "What this does and doesn't do" 段）

- **不可信 transcript 只能改 store 内容与花掉预算，仅此而已**——除非把 store 文本放进 system prompt，那才能 steering 每个 session。→ 对应 brief-plan §5.5 治理：挂载必须 read_only + instructions 收窄；**记忆库是新的注入面**，群组共享记忆（§12.2 W2 scope=shared）同样适用。
- 记忆只是 transcript 的函数："analyzer 不知道 transcript 之后发生了什么"→ 事实带 staleness 注记，关键事实仍需复核。→ 与 0003 的 `valid_until`/`superseded_by` 字段同向。

---

## 3. Knowledge-wiki quickstart 走读（`oss-repos/claude-quickstarts`）

[`managed-agents/knowledge-wiki/`](https://github.com/anthropics/claude-quickstarts/tree/main/managed-agents/knowledge-wiki)（README 全文 + 目录）：

- **定位**：慢变语料**一次性读入** wiki（纯 markdown，存 memory store），之后 agent 只读 wiki 答问；**provenance 挂在每条事实上、文档间冲突保持冲突、被替代的数字保持被替代**（不合并）。
- **经济性（README 口径）**：小模型带 wiki 答问 ≈ 大模型裸搜原文 ±1 分，约 **1/15 单价**；建一次约 **$19**（记录 run $16），约 **240 问回本**。
- **结构**：`distill_*.ipynb`（主 notebook，每 cell 附真实运行输出，可当案例通读）+ `prompts/`（analyzer/organizer/lead/baseline 四份系统提示）+ `utilities.py` + `build_manifest.py`（查 SEC EDGAR 出分档清单）+ `fetch_*.py` + 5 档 manifest。README 明确"**指向 dreaming cookbook** 保持 wiki 随 agent transcript 更新"——两仓是一条流水线。
- **访问前置**（README Access 段，@dev 2026-11-08 核对）：一切跑在 Managed Agents (beta)，"enabled by default for API organizations; the SDK sends the beta headers"，`client.beta.agents.create` 报 permission error 就找组织 admin；Python ≥3.11 + `anthropic` SDK ≥2,<3。
- **不可信输入**：对方 Office 文件是 untrusted input，建议容器内或转文本后再处理（README 原文）。

---

## 4. 与本项目的映射（落点）

| # | 本笔记要点 | brief-plan / 决策落点 | 状态 |
|---|---|---|---|
| 1 | 共享可写记忆页必须分片/独占，否则并发覆盖（57→41） | §12.2 W2 `scope=shared` 黑板写入规则 | **待拍板**（建议补"按 author 分片或串行化写入"一句） |
| 2 | dreaming 的 memory version + run 前复制 = 审计与回滚 | §5.4 `goal_memory_digest` 已有 `superseded_by`（0003 决策 3） | 一致，可作外部佐证 |
| 3 | 失败夜重放同批 transcript → analyzer 更新须幂等 | §5.2 规则 4 幂等回执（0002 决策） | 同构，建议在 0002 补"记忆写入同属幂等域" |
| 4 | 注入层是污染面：顶层错误记忆污染所有后续 session | §5.1 turn_context 组装（gate 先于 packing）+ §5.5 治理 | 一致；"只取索引 25KB"可作 MEMORY.md 式上限的参照 |
| 5 | 提示词原则："tell what memory is for, not how"；硬规则伤强模型 | 0003 的可计算晋升 gate（coverage≥0.30 等） | **张力点**：Anthropic 反对硬规则写"记什么"，我们 gate 管的是"**晋升**判据"而非"写入内容"——对象不同不冲突，但 demo 若把 salience 也硬编码需重新评估 |
| 6 | cadence 按访问频率而非全量校验（开放问题） | §5.4 记忆维护调度 | 未解，W3+ 可作 spike 候选 |
| 7 | memory ≠ weights / in-context / compaction | §5.4 术语口径 | 一致 |

**未改 brief-plan**：本笔记按 CONVENTIONS §3.7 只读映射；上表 #1/#3/#5 涉及设计修订，按"先决策记录后改设计"流程，待 @user 拍板后另立决策记录或定点修订。

## 5. 运行前置（@dev 2026-11-08 验证结论，静态）

- cookbook：Python ≥3.11、`anthropic` 2.x（本机 2.7.0 验证 `client.beta.dreams.create` 存在但本 cookbook 不需要它）、Managed Agents beta 凭据（`ant auth login` 或 `ANTHROPIC_API_KEY`）。
- quickstart：同上；需组织已开 Managed Agents（API 组织默认开）。
- 两者端到端实跑**均未做**（无凭据）；真跑时先按 README 通读 notebook 内置输出再执行。

## 原文链接

- 博客：https://www.anthropic.com/research/components-of-agent-memory
- Dreams API 文档：https://platform.claude.com/docs/en/managed-agents/dreams
- Dreaming cookbook：https://platform.claude.com/cookbook/managed-agents-cma-dreaming-with-a-dynamic-workflow
- Knowledge wiki quickstart：https://github.com/anthropics/claude-quickstarts/tree/main/managed-agents/knowledge-wiki
- Sleep-time compute（论文）：https://arxiv.org/abs/2504.13171
- Google Sleep Framework：https://research.google/blog/the-sleep-framework-a-new-way-for-llms-to-retain-knowledge-in-continual-learning/
- 相关早文：[Harness design for long-running application development](https://www.anthropic.com/research)（2026-03-24）
