# W1–W5 研究闭环审计（原始需求 / 功能闭环 / 文档规范对账）

> 状态：定稿（待 @dev 全链终核）｜ 作者：@research ｜ 日期：2026-11-12 ｜ 触发：@user 指令「把 W1–W5 的剩余论文、文献、开源项目研究工作全部完成，确保能满足 W5 前所有原始需求，且有自己根据研究得到的创新点，前五周研究计划的功能可以闭环，仓库中各层级文档闭环对应规范」
> 口径：本文所有数字为 2026-11-12 当轮实测/回抽（测试现跑、索引现算、文件现数），不采信历史自述；@dev 独立复跑数据单列标注。研究闭环 ≠ 平台实现：§1 需求的「开发交付」列属 harness 平台仓（当前搁置），本仓只承载研究闭环，不声称实现完成。

## 1. §1 需求原文覆盖矩阵（第一阶段 W1–5）

需求原文见 [brief-plan §1](../brief-plan.md)（六条能力 + 汇报场景）。逐条对账：

| # | 需求（§1 原文） | 设计落点 | 决策记录 | 实测证据 | 状态 |
|---|---|---|---|---|---|
| 1 | 解析目标→评价指标、任务拆解、执行计划 | §4.3 状态机 / §5.1 期次协议 / §4.4 计划 DAG | [0002](../decisions/0002-w1-recovery-semantics.md) | w1 9/9（状态机恢复语义） | 研究闭环 ✓（实现留平台侧） |
| 2 | 智能体自主编写/测试/执行/调试金融代码 | §5.6 vnpy 集成 + 前视构造性防护 | [0004](../decisions/0004-w3-backtest-reliability-and-lookahead-guard.md) | w3 12/12（越界抛错/双 lint 定罪） | 研究闭环 ✓ |
| 3 | 周期任务、交易日调度、任务依赖、异常处理+恢复扫描 | §5.3 调度（trading_day 扩展）/ §5.2 规则 8 | [0002](../decisions/0002-w1-recovery-semantics.md) | w1 9/9（崩溃后 recovery 扫描恢复） | 研究闭环 ✓ |
| 4 | 持久保存目标/策略/代码版本/进度；跨会话、中断恢复、多目标 | §4.4 领域模型（全部带租户边界） | [0002](../decisions/0002-w1-recovery-semantics.md) + [0003](../decisions/0003-w2-memory-distillation.md) | w1 9/9 + w2 12/12（scope/author 字段） | 研究闭环 ✓ |
| 5 | 权限、资源预算、人工审批、暂停/恢复/终止 | §5.5 治理（审批门/预算/pause-resume-terminate） | [0005](../decisions/0005-w4-approval-binding-and-authorization-governance.md) | w4 16/16（use-time 绑定/digest 拒绝/独立通道） | 研究闭环 ✓（完整字段面留平台侧） |
| 6 | 目标工作台：计划、任务状态、运行结果、历史 | §7 工作台 UI（四区信息架构） | —（设计层，随 W4 细化产出） | 设计文档在位；无 demo（UI 类按 §12.0 归开发交付） | 设计闭环 ✓（实现留平台侧） |
| R | 汇报场景：提交目标→生成代码→验证→定时→交付 + 失败修复/重启恢复/改目标 | §12.1 W5 行 + §9 演示剧本 | [0006](../decisions/0006-reporting-and-metrics-taub.md) | w5 19/19 七步剧本（改坏/重启/改目标/interface/数据面/固定化/τ_b） | 研究级镜像 ✓（真演示随第一次汇报排期） |

**结论**：§1 六条 + 汇报场景在「研究闭环」层面全部有 设计落点→决策记录→实测证据 三件套；**开发交付列（插件脚手架、CRUD API、工作台实现等）属 harness 平台仓，按历次指令维持搁置，本审计不声称其完成**。

## 2. §12.0 每周自查表（demo+决策 / 文献笔记+方向结论 / 设计修订 / 中译）

| 周 | 文献笔记（方向结论） | 独立 demo（本机实测 2026-11-12） | 决策记录 | brief-plan 定点修订 | 中译 |
|---|---|---|---|---|---|
| W1 | [W1 笔记](../literature/W1-durable-scheduling-recovery.md)（4 精读） | w1-recovery-demo **9/9 OK**（@dev 独立复跑同数） | [0002](../decisions/0002-w1-recovery-semantics.md) 已采纳 | 留痕 6 处（§5.2/§5.3/§12.1/§12.2…） | 4 篇已译已核 |
| W2 | [W2 笔记](../literature/W2-context-memory-distillation.md)（3 精读+1 摘要级） | w2-memory-distillation-demo **12/12 OK** | [0003](../decisions/0003-w2-memory-distillation.md) 已采纳 | 留痕 3 处（§4.4/§5.4/§12.2） | 4 篇已译已核 |
| W3 | [W3 笔记](../literature/W3-backtest-reliability.md)（7+1 精读 + §6 补检 5 篇） | w3-lookahead-proof-demo **12/12 OK** | [0004](../decisions/0004-w3-backtest-reliability-and-lookahead-guard.md) 已采纳 | 留痕 4 处（§5.6/§6.1/§8 A2/§12.1；§12.2 W3 为纯文本引用不计入） | 8 篇已译已核 + 5 篇补检 **2026-11-12 入库已核（@dev PASS）** |
| W4 | [W4 笔记](../literature/W4-hitl-approval-authorization.md)（4 精读） | w4-approval-gate-demo **16/16 OK** | [0005](../decisions/0005-w4-approval-binding-and-authorization-governance.md) 已采纳 | 留痕 4 处（§5.5/§4.4/§12.1/§12.2 W4） | 4 篇已译已核 |
| W5 | [W5 笔记](../literature/W5-real-eval-fault-style.md)（8 精读，A–D 判定+新增⑤⑥⑦） | w5-fault-drill-demo **19/19 OK**（含 τ_b 第 7 步） | [0006](../decisions/0006-reporting-and-metrics-taub.md) 已采纳 | 留痕 1 处（§6.1 两块修订） | 8 篇 **入库已核（@dev PASS 2026-11-12）** |
| 合计 | **5/5 笔记**（模板四段齐） | **68/68 OK**（9+12+12+16+19；@dev 独立复跑逐数一致） | **0001–0006 全部已采纳** | **18 处留痕**（0002×6/0003×3/0004×4/0005×4/0006×1） | **57 篇全部已核**（44 既有 + 13 本两批，@dev 2026-11-12 双 PASS） |

**§12.2 群组增量线**（W1–W5 挂靠子题）：W1 决策 5、W2 决策 6 已定稿；W3 assigned_role opt-in demo 实证 + §6 补检五方向（文献级留 W8）；W4 七条落点含实证/未验证分标；W5 追加演练一条。逐行状态见 brief-plan §12.2 表。

## 3. 创新点（自有研究增量）

按用户要求产出 [innovation-points-w1-w5.md](innovation-points-w1-w5.md)：**IN1–IN7** 七条，每条含 来源链（文献→决策→实测）、与文献差异、验证状态、落点。诚实边界在该文 §2（不声称发明文献原始概念；实现边界不外溢）。待 @dev 回源核验。

## 4. 文档层级规范对账（CONVENTIONS 逐目录）

| 层级 | 规范要求 | 实测终态（2026-11-12） | 结论 |
|---|---|---|---|
| 根 README | 目录树与规范文档指针 | brief-plan/CONVENTIONS/process-review 等在位；本轮新增文档由本文件与创新点文档补指针（见 §5 修订） | ✓（本轮补） |
| docs/CONVENTIONS | 目录/命名/提交/敏感信息 | §2 目录表与实际一致；oss-repos「目录名=GitHub 仓名」经 `rd-agent→RD-Agent` 改名对齐 | ✓（本轮修） |
| docs/literature | 每周笔记 + README 已归档 | **5/5**（W1–W5）；README W3 行补 §6 补检 5 篇（初版日期 11-10 更正） | ✓（本轮修） |
| docs/decisions | NNNN 编号 + 状态字段 + 索引 | **6/6**（0001–0006 全已采纳）+ README 索引 6 行 | ✓ |
| docs/essay-study | `<短名>-<年>.md` + README 已归档 | **9/9**（本轮 +tick-stock-panel/+RD-Agent）+ 索引 9 行 | ✓（本轮修） |
| docs/papers | `arXiv-<ID>.pdf` + 索引 | **33 PDF / 33 索引行**（pdfinfo 闸全过，2605.17937 损坏件已重下） | ✓ |
| docs/translations | README 规范 + 双向索引 | **92/92**（papers 33 + literature 30 + projects 29，索引=有效=磁盘、零断链）；机器终检 `check_translations.py --include-readme` **33 OK / ALL PASS**（papers 分区） | ✓（本轮 +5） |
| research-demos | 每 demo 自带 README 四段 | **5/5**（w1–w5），测试 68/68 | ✓ |
| docs/PROGRESS | 当前阶段 + 进度日志 + 待办 | 本轮刷新（见 §6） | ✓（本轮修） |
| docs/templates | 文献/决策模板 | literature-note、decision-record 在位，W1–W5 笔记与 0001–0006 均按模板 | ✓ |
| oss-repos/（gitignored） | 浅克隆不入库 | **10 仓**；本轮 +tick-stock-panel（a7868b7，58M）+RD-Agent（484776c，21M），`git check-ignore` 覆盖复核 | ✓ |
| harness-hub/（gitignored） | 严禁入库 | 未入库；其内 b2b 统计插件补丁属本地配置（PROGRESS 2026-11-11 留痕） | ✓ |

**本轮对账修缮 4 处**：① literature README W3 行补 §6；② essay-study README +2 行；③ RD-Agent 目录改名对齐 §2；④ translations 索引 +5 行至 92/92。

## 5. 索引终态汇总（供 @dev 抽核）

- translations：**92/92/92**（索引/有效/磁盘）；papers 分区终检 **33 OK / ALL PASS**
- papers：**33/33**（PDF/索引行）
- literature：**5/5**；decisions：**6/6**（全已采纳）；research-demos：**5/5**；essay-study：**9/9**
- 测试：**68/68**（w1 9 / w2 12 / w3 12 / w4 16 / w5 19，2026-11-12 现跑；@dev 独立复跑逐数一致）
- brief-plan 决策留痕：18 处（0002×6 / 0003×3 / 0004×4 / 0005×4 / 0006×1）

## 6. 观察项、边界与遗留（不阻塞闭环结论）

1. **测试布局跨周不一致**（@dev 素材）：w1/w2 测试在仓根（`test_recovery.py`/`test_w2.py`）、w3–w5 在 `tests/`——README 均有实测命令、实质合规；本轮不统一（w1 已定稿不追溯），留 W6 前随复盘 P 系列一并拍板。
2. **复盘 P3–P7 仍全部未决**（[process-review-2026-11-10.md](process-review-2026-11-10.md)）：直推 vs PR 口径、提交署名 3 人、spike 模板、§12.0 scratch 表述、可读性修复——不属本审计范围，待 @user 拍板。
3. ~~13 篇中译待 @dev 四项核验~~（**已清 2026-11-12**：W5 批次 8 篇 `23f4d87` + W3 补检批次 5 篇 `37efd5a` 双双 **PASS**，见 §7 附注——六字段头/围栏/单段≤500 零违例、抽样数字 PDF↔译文命中、两笔提交零夹带）。
4. **harness 平台实现搁置**：§1「开发交付」与 §12.0 各周开发列全部属平台仓，按历次指令搁置；本审计只闭研究线。
5. **W6–10 不在本次范围**（用户指令为「W5 前所有原始需求」）。
6. **本轮流程留痕**：W3 补检 5 篇中译由 5 个并行子代理完成（2026-11-12）；HALO 篇文件头曾按我方提示词字面写成「# 中文译题（…）」占位形态，与全库 32 篇「中文译题（English）」形态不一致，已当轮修正为规范译题行——提示词占位符歧义为我方责任，记此防再发。

## 7. 核验附注

回源核验：@dev 2026-11-12，**全链终核 PASS**——
- **IN1–IN7 回源**：全部实测数字与我方 demo 逐位一致（68/68、τ_b=+1.0000、536.10%、299+7、16/16 digest `379a39a0≠900b2fe8`）；文献引用中 5 处此前未经我方回抽的数字本轮 pdftotext 独立命中——What survives「design SR 34.7 … DSR of 1.00」逐字（IN1）、SEPM「reduces task scores by 17.16」→ 17pp 取整成立（IN4，注意与另一处 17.17 的 self-evolving 增益区分）、I-HITL「(Theorem 4)」（IN5）、Fake News `II overall 61.7% / CI overall 13.8%`（IN6）、Crypto「All four methods exhibit negative alpha」（IN2）；其余引用均在 W1–W5 笔记既有核验链内。
- **translations 三项**：13 篇（W5 8 + W3 补检 5）六字段头/围栏/单段≤500 汉字独立复检零违例；索引=有效=磁盘 **92/92/92** 双向差集为空；抽样数字 6/6 同时命中 PDF 与译文（61.7/13.8、62.6/67.7、79.7/47.5），Fake News/LATTE 尾部完整（前者带完整性译注）。提交归属：`23f4d87` 10 文件（W5 笔记翻译债清账行属同笔正当同步）、`37efd5a` 7 文件零夹带，坑 4 效应级验证通过。
- **本表抽核**：papers 33/33、essay-study 9/9、decisions 6/6、literature 5/5、demos 5/5 与 §5 汇总逐数一致；**18 处留痕口径破解并复算命中**（= brief-plan 中含 `decisions/NNNN` 链接的行数：0002×6/0003×3/0004×4/0005×4/0006×1）。
- **两处标签级小疵（数字无误，建议后续顺手改）**：①§2 W2 行标注留痕「§5.4/§12.1/§12.2」，实际链接行为 §4.4/§5.4/§12.2（§12.1→应为 §4.4）；②§2 W3 行「§12.1+§12.2 W3」中 §12.2 W3 行为纯文本引用（无链接、不计入 18 处），标注宜写明。
- 结论：**六项要求的研究侧闭环成立**（研究三件套齐、IN1–IN7 有实证边界、68/68、索引终态、文档对账），维持 §1 口径——平台实现列不在此声称。
