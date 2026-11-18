# W1–W5 三头对照闭环审计（原始需求 × 学习研究 × harness-hub 开发），2026-11-17

> 执行：@research ｜ 核验附注留 @dev 终核（互斥配对：本件 @research 执行）。
> **口径变更声明**：本审计**取代** `w1-w5-closure-audit-2026-11-12.md` 中「开发交付属平台仓、按搁置令不声称完成」的前提——@user 后续指令已启动 harness-hub Strategy Lab 开发，W1–W5 已于 2026-11-17 全线收口，故本审计对开发交付**声称完成并给出实测证据**。
> 所有数字均为 2026-11-17 @research 独立实跑，不采信回执自述（spec-execution-discipline 纪律 5）。

## §0 三断言结论摘要

| 断言 | 结论 | 一句话证据 |
|---|---|---|
| ① 学习研究成果 ⊇ 原始需求（满足全部 + 创新点） | **✓ 成立** | 需求 7/7 条目在研究线全承接（需求本身即 `brief-plan §1` 溯源头）；研究增量 = **IN1–IN7 创新点 7 条**（@dev 回源核验 PASS）+ W5 文献修订四件（τ_b 第四维/成本维度/三件套/宣称四档）+ demo 实测 **68/68** |
| ② harness-hub ⊇ 原始需求（完全涵盖） | **✓ 成立** | R1–R7 逐条「spec 落点 → 计划任务 → 实测证据」三件套齐（§1）；五周计划 **203 格 / 196 勾**，7 格未勾全部为同一根因（登录墙浏览器冒烟批），**无功能缺口** |
| ③ harness-hub 采纳了学习研究新内容 | **✓ 成立** | 决策 **0002–0006 全部已采纳**且逐条在开发侧有实现+测试（§3）；IN1–IN7 全落点（4 个子项 spec 明标「随平台/留后续」如实，未虚报） |

## §1 原始需求覆盖矩阵（需求原文 → 研究承接 → 开发落点 → 实测证据）

需求原文 = `docs/design/strategy-lab-w1-w5-requirements.html`「原始需求前一半逐条勾选」节（= `brief-plan.md §1`，Phase 1 六条 + 汇报场景）。

| # | 需求原文（§1 摘） | 研究承接 | 开发落点（spec → 计划任务） | 实测证据 |
|---|---|---|---|---|
| R1 | 解析目标/策略/约束 → 评价指标、任务拆解、执行计划 | brief-plan §1；W2 解析契约研究 | spec §4.1 向导 4 步 + §5 解析契约 → W2 T3/T8、W4 T5 Step3 审批提交 | `parse_contract 7 + parse_api 6`、`approval 16/16`（含 `plan_ready` 首接） |
| R2 | 智能体自主编写/测试/执行/调试回测代码（量化） | W3 文献 7+1 精读 → 决策 **0004**（已采纳）；w3 demo | spec §9 W3 GoalStrategyBase + W4/W5 模板 → W3 T4、W5 T1 | `strategy_base 12/12`（对拍表 14 用例逐条去向）、`codegen 11`（T1–T4 双面同步对齐断言） |
| R3 | 周期任务、交易日调度、任务依赖、异常处理 | W1 调度/恢复文献 → 决策 **0002**；workspace-automation 复用研究 | spec §9 W3 → W3 T1/T2/T3 | `trading_calendar 7`（seed 19 行带官方 note）、`scheduling 7`（引擎零日期算术源码断言）、`dag_runtime 8` |
| R4 | 持久保存/跨会话/中断恢复/多目标独立 | 决策 **0002** 双 oracle；w1 demo | spec §5 恢复语义（`:123`）→ W1 T4/T5 | `state_machine 23`、`recovery 6`（IN3 **w1 9/9**）、goal 9+1 表迁移链 0176→0189（2026-11-17 重编号后口径） |
| R5 | 权限、资源预算、人工审批、暂停/恢复/终止 | W4 HITL 4 精读 → 决策 **0005**（双轮核验 16/16） | spec §4 审批强口径 → W4 T1/T2 | `approval 16/16`（四强断言逐格）、`governance 10`（预算不硬切断序列 + 三控制） |
| R6 | 目标工作台：执行计划/任务状态/运行结果/历史记录 | spec §4.2 信息架构（需求稿四区形态差异见 §5-1） | spec §6.2 → W1 列表 + W4 T5 四区完整版 | `runs result 3`、四区断言、`workbench.test.mjs`（code_version 回显） |
| R7 | 汇报场景：提交→生成代码→验证→定时→持续交付 + 失败修复/重启恢复/改目标 | W5 8 篇精读 → 决策 **0006**（τ_b 逐位复算核验）；w5 demo | spec §9 W5 → W5 T3/T4 | `report_gate 8/8`、`drills 4/4`（七步裁决 demo.py:146）、`taub 10/10`（**w5 19/19**） |

**后一半（W6–10 测评优化闭环）**：研究线留接口位、需求稿明标「不在本稿声称完成」，开发侧零声称——双向一致（§5-3）。

## §2 超集验证（研究 ⊇ 需求 + 创新增量清单）

- **承接面**：需求 7/7 全承接（§1 研究列无空格）——研究以需求为输入（`brief-plan §1` 即需求原文），不存在漏承接。
- **超出原始需求的研究增量**（原需求未要求、研究引入并已被开发采纳的部分——即「创新点」）：

| 增量 | 来源 | 开发采纳证据 |
|---|---|---|
| IN1 构造性前视防护三层 | W3 文献 → 0004 | `strategy_base 12/12` + 报告证据区 `in1-evidence`（registry flag/越界记录读 payload） |
| IN2 宣称-证据同档（τ_b 必报 + 四档锁 + 三件套） | W5 文献（Alpha Illusion/AllPath/Execution Assumptions）→ **0006** | `report_gate 8/8`（四决策出口单点）+ `taub 10/10` + 五禁词双语扫描 |
| IN3 双 oracle 恢复 | W1 文献 → 0002 | `goal_effect_ledger` 表 + recovery 6 |
| IN4 记忆 scope 字段化（SEPM/CALM） | W2 文献 → 0003 | `goal_memory_digest` 13 列 + `memory_lifecycle` 用例 |
| IN5 人批 + use-time 绑定强口径 | W4 HITL 4 精读 → 0005 | `approval 16/16` 四强断言（digest 失配 409 / uk 单次消费） |
| IN6 故障七步剧本（interface 诚实 + 数据面注入） | W5 故障分类学 → 0006 关联 | `drills 4/4` + 剧本入口 quant-only 两处 |
| IN7 群组 opt-in `assigned_role` | W2 群组研究 | 0001 列 + 角色列 NULL→`—` 断言 |
| 文献修订四件（τ_b 第四维、成本必报、三件套、宣称档 1–2） | W5 8 篇精读（brief-plan `:320` 修订留痕） | `report.py` 出口四校验逐条对应 |
| 使用便利（模板一键/引导向导/剧本直达/双语） | 需求稿 IN 节 | T1–T4 模板卡、向导 4 步、双语断言 |

**结论**：研究结果 = 需求（7/7 承接）∪ 创新增量（IN1–IN7 + 文献修订），是原始需求的**真超集**；且每条超集项都有「文献/决策 → spec → 测试」来源链，无凭空项。

## §3 开发采纳研究新内容逐条核（决策 0002–0006）

| 决策 | 状态（grep 实证） | 开发侧采纳 |
|---|---|---|
| 0002 恢复/调度 | 已采纳（2026-11-01，双轮） | spec `:123` 恢复语义逐字承接 → W1 `recovery 6` + `goal_effect_ledger` |
| 0003 记忆蒸馏 | 已采纳（2026-11-01） | W2 `goal_memory_digest` 13 列 + lifecycle 用例 + §5 注入规则 |
| 0004 前视防护 | 已采纳（2026-11-10 @research 双轮：12/12 回抽、3bp 回抽 `cost_rate=0.0003`） | `strategy_base`（`COST_RATE=0.0003` 同值断言）+ 双 lint（`static_scan` 出口自检） |
| 0005 审批授权 | 已采纳（2026-11-10 双轮：16/16、27/40 回抽命中） | `approval 16/16` 四强口径 + `governance` 人判复用 |
| 0006 报告/τ_b | 已采纳（2026-11-11 双轮：τ_b 逐位复算） | `report_gate 8/8` 四决策 + `taub 10/10` + 首报宣称档自查 |

IN1–IN7 → 开发落点对照见 §2 增量表与 `plans/notes/w5-first-report.md` §2（spec §10 表原样 + 本仓证据列）。

## §4 计划完成度与未勾格归因

- 五周计划（W1 51 / W2 43 / W3 39 / W4 36 / W5 34）：**总 203 格，196 勾，7 未勾**。
- **7 格全部同一根因**：登录墙浏览器冒烟批（W1 Step6 视觉 + 深链视觉、W2 解析两态/d1/记忆面板、W3、W4、W5 各一格）——缺 @user 登录授权（「再存一次」），非功能缺口；源码断言面全部实测通过（导航 7/7、前端 34/34、旧仓 cwd 5/5、深链 200 已验）。
- 汇总证据链（2026-11-17 实跑）：后端我方全套 **187 passed + 1 skipped**；五 demo pytest 实收 **9+12+12+16+19 = 68/68**（与 spec 总锚、IN 表各行 9/9·12/12·16/16·19/19 三方互证）；`alembic heads` 单头 0189（重编号后口径，原 0184）；提交合规（首行 `YGZYPT-13066` + 尾行 trailer）逐笔核。

## §5 形态差异与观察项（如实，不掩盖）

1. **R6 四区形态差异**：需求稿四区含「策略演进（通用=计划演进）」独立区，spec §4.2 细化为「任务状态」区——开发按 spec 执行；策略演进功能面**未缺**，承载改形为 `GET /strategies?goalId` 列表（模板卡内）+ `code_version` 运行结果回显（`run-results.tsx:60`、`workbench.test.mjs:37` 断言在案）。以 spec 为准，差异留档。
2. **需求稿为 2026-11-13 前静态样例**：其勾选节与页面数据为当时研究态演示样例，完成度以本审计与五周计划勾选为准。
3. **后一半与部分 IN 子项双向一致地不声称**：W6–10 测评闭环（oos/benchmark、A1–A8、群组实跑）、IN1 的 registry flag/buffer 时序（demo 已实证接口层，平台侧随平台）、IN4 workflow 归纳注入、IN5 完整字段面、IN7 五方向（W8）、top-3 Jaccard（半采纳）、推送通道（零定义留接口位）——研究侧标「留后续」、开发侧零声称，**无单边超前**。
4. **三件 @user 依赖**（详见 `harness-hub docs/superpowers/plans/notes/w5-first-report.md` §4）：浏览器冒烟（缺登录）、DSH 真链路（缺 `~/.dsh/.credentials.yaml` refs 修复，一键脚本 `w5-dsh-retry.sh` 留档）、最终 MR 早期 7 笔无 trailer 处理（待批）。

## §6 可复核素材（对方独立复跑入口）

- 需求/研究：`goal-quant-research/docs/brief-plan.md §1`、`docs/decisions/0002–0006`（状态头 grep）、`docs/literature/W1–W5`、`docs/innovation-points-w1-w5.md`、`research-demos/w1–w5`（各 README 命令，pytest 实收 68）
- 开发：`harness-hub/docs/superpowers/specs/2026-11-13-strategy-lab-design.md`（R 表 `:19-25`、IN 表 `:179-185`、§9 周表 `:203-207`）、`plans/2026-11-1*strategy-lab-w*.md`（203 格）、`plans/notes/w5-first-report.md`
- 实测：`cd harness-hub/backend && PYTHONPATH=. .venv/bin/python -m pytest tests/test_goal_*.py tests/test_quant_*.py tests/test_trading_*.py -q`（187+1）；demo 逐仓 `python -m pytest --collect-only -q`（9/12/12/16/19）

## 核验附注（@dev 终核，2026-11-17）

**结论：三断言全部认可，审计通过。** 独立复跑证据（不采信文档自述）：

1. **后端**：按 §6 复核命令复跑 **187 passed + 1 skipped** ✓；R 表引用的计数（parse_contract 7 / parse_api 6 / approval 16 / governance 10 / report_gate 8 / drills 4 / taub 10）均含于本套件且五周内逐笔实跑过；
2. **demo 68/68**：逐仓独立复算——w1 `python3 -m unittest test_recovery` 9 ok、w2 `test_w2` 12 ok、w3–w5 `unittest discover` 12/16/19 ok ✓（注：demo 为 unittest 体系，`pytest --collect-only` 不适用，§6 该行的命令形态以本附注为准）；
3. **决策采纳**：0002–0006 状态头 grep 全「已采纳」✓；
4. **§5 形态差异处置全部认可**：R6 改形以 spec 为准且功能面证据在案（run-results code_version ×3 处 + workbench 断言 ×2 复核）；后一半与 IN 子项双向不声称；三件 @user 依赖与 w5-first-report §4 一致；
5. **无遗漏需求条目**：R1–R7 与需求稿「原始需求前一半逐条勾选」节逐条对齐。

**一处计数精度注记（不影响结论）**：§4 的「203 格 / 196 勾」把五份计划文件模板导语行（「For agentic workers…」内嵌的 `- [ ]` 示例字样，每份 1 条）计入了总数——严格勾选格计数为 **198 格 / 191 勾 / 7 未勾**；关键断言「7 格未勾、全部同一根因（登录墙浏览器冒烟批）」经逐条列名核实**成立**（5 条导语行非勾选格，其余 7 条全为冒烟批），分类与归因不变。

—— @dev，2026-11-17
