# 项目进度记录（PROGRESS）

> 状态：活跃维护。每次有实质进展（规范变更、设计修订、研究/demo 完成、阻塞解除）由执行方追加一条记录；本文件只记结论与指针，细节写入对应文档后链接过去。日期为本地日期。

## 当前阶段

Phase 1 W2 已闭环、W3/W4 研究线进行中（@user 2026-11-10 指令「进行 W3W4 论文/文献/独立 demo 研究，harness-hub 集成开发先搁置」——**W3 暂停令就研究线解除**；harness 侧维持搁置不变）。当前：W1/W2 文献+demo+决策全闭环（决策 [0002](decisions/0002-w1-recovery-semantics.md)、[0003](decisions/0003-w2-memory-distillation.md) 均已采纳）；**W3/W4 文献线 2026-11-10 完成**——12 篇新 PDF 归档、[W3 笔记](literature/W3-backtest-reliability.md)（7 精读+1 摘要级）、[W4 笔记](literature/W4-hitl-approval-authorization.md)（4 精读，原「检索无结果」解除），brief-plan §12.1 W3/W4 行与 §12.2 W4 行已回填；**W3 demo 跑通（12/12 实测）且决策 [0004](decisions/0004-w3-backtest-reliability-and-lookahead-guard.md) 已采纳（@research 2026-11-10 双轮核验）——下一步：brief-plan 五处定点修订（@dev）→ W4 demo/0005 → 12 篇中译**；§3.1 四项目走读闭环（笔记 4/4 + 两轮核验通过）。2026-11-10 另有：Anthropic 记忆走读笔记与[全流程规范复盘](process-review-2026-11-10.md)落库、目录树各级规范文档对账补齐；复盘待拍板 **P3–P7 均未决**——当前无阻塞，待办见文末。

## 进度日志（倒序）

### 2026-11-10（W3/W4 文献研究：12 篇归档 + 双笔记 + brief-plan 回填）

- **[user] 指令（2026-11-10）**：根据进度进行 W3W4 的论文、文献、独立 demo 研究，harness-hub 集成开发先搁置——W3 暂停令就研究线解除，harness 侧维持搁置。
- **[research] 检索与归档**：arXiv API 四式补检（backtest+LLM / look-ahead bias+LLM / quantitative trading+LLM agent / trading strategy+LLM）+ W4 三式（HITL approval / authorization autonomy / multi-agent permission），**12 篇新 PDF 归档 `docs/papers/`**（`%%EOF` 全部校验通过），`papers/README.md` 索引 +12 行（W3 8 篇 / W4 4 篇）。
- **[research] 并行精读**（3 个子代理分组读完 `pdftotext -layout` 提取件，关键数字回抽 PDF `grep -a` 逐条核验）→ **[literature/W3-backtest-reliability.md](literature/W3-backtest-reliability.md)**（7 篇精读 + 1 摘要级：BacktestBench/MintEval/QuantHarness/Hard to Fool/Look-Ahead-Bench/What survives 全文升级/FinCutBench/When Alpha Disappears）与 **[literature/W4-hitl-approval-authorization.md](literature/W4-hitl-approval-authorization.md)**（4 篇精读：I-HITL/Loopjacking/From Approval to Abuse/Permitted but Unauthorized，**原「本轮检索未取得有效结果」解除**）。
- **[research] brief-plan 回填**（整行替换 + 列数校验 6 管道=5 列通过）：§12.1 W3 行——方向结论五条采纳（前视三层构造性防护、试验账本单入口三仪器齐算、行为等价验收、实测知识边界窗口、门禁合取+预算化选型）+ 改造（声明式词表→spec+行为校验）+ 不采纳（单分数验收）；§12.1 W4 行——补检结果与四条采纳（use-time 绑定原子消费、审批通道独立于 agent、矩阵不可变上限、矩阵模型之下强制）；§12.2 W4 群组行——候选补 4 篇精读 + 落点新增 ④–⑦ 四条（runtime 强制/委派记录权威/peer 动作不入候选空间/self-report effect 校验）。**机制级设计修订（§5.5/§5.6/§6.1/§8 A2）未动**——按「先 demo 后决策再改设计」留待 W3/W4 demo 证据，决策记录 0004/0005 顺延预留。
- **待办**：① ~~W3 独立 demo~~（**已完成 2026-11-10**：`w3-lookahead-proof-demo` 12/12 实测，[0004](decisions/0004-w3-backtest-reliability-and-lookahead-guard.md) 已采纳；vnpy 路径按 §13 风险行改 pandas 窗口回测替代）② W4 独立 demo（审批挂起-恢复语义验证，0005 前置）③ 12 篇新 PDF 中译入 `docs/translations/papers/` ④ §12.2 W3 群组子题（角色×DAG）文献仍待补。

### 2026-11-10（Anthropic 记忆文献走读 + oss-repos 增补 + 全流程规范复盘）

- **[dev] 目录树各级规范文档对账补齐**（按 technical-documentation skill review 流程）：`docs/essay-study/README.md` 补「已归档」6 篇索引（原只有规则无清单）；根 `README.md` 目录树补 `.github/`（PR 模板 + doc-lint CI）与 `process-review-*`/`readability-audit-*` 过程散档两行；`docs/CONVENTIONS.md` §2 `docs/` 行补过程散档命名口径 `<主题>-<YYYY-MM-DD>.md`；本文件「当前阶段」补 11-10 概况与 P3–P7 未决状态。对账实测：papers PDF 索引 8/8、translations 索引 67/67 零缺项零断链、decisions 3/3、research-demos 2/2、literature W1–W2 齐、essay-study 6 篇齐。

- **[user] 指令（2026-11-10）**：①能克隆的项目仓库落到 `oss-repos/`；②docs 对应部分补研究笔记；③重新复盘本仓整个研究、开发的流程规范。
- **[research] `oss-repos/` 增补两仓浅克隆**（gitignore 覆盖，不入库）：`claude-cookbooks`（410MB，HEAD `ce8b262` 2026-11-04）、`claude-quickstarts`（17MB，HEAD `4a4224b` 2026-11-06），为 Anthropic agent memory 走读提供本地源码。
- **[research] 走读笔记新增** → [essay-study/anthropic-agent-memory-2026.md](essay-study/anthropic-agent-memory-2026.md)：Anthropic《The components of agent memory》（2026-11-06）博客全文 + dreaming cookbook notebook（全部 markdown 单元）+ `dreaming_nightly.py` 全文 + knowledge-wiki quickstart README 的静态走读；四层记忆架构、CL-Bench/Pokémon 数据（first-party 未复现标注）、**共享可写页并发覆盖（57→41 条）必须分片**对 §12.2 的教训、与 0002/0003 设计的 7 条映射（2 条标"待拍板"，未改 brief-plan）。未跑端到端（无 Managed Agents 凭据，前置条件已按 @dev 2026-11-08 静态验证结论收录）。
- **[research] 全流程规范复盘** → [process-review-2026-11-10.md](process-review-2026-11-10.md)：现行"研究→决策→设计修订→demo→双轮核验→PROGRESS"链路与实测健康度（23 提交/8 PR/3 决策全已采纳/67 译文）；**已修正 2 项**——decisions 与 research-demos 两处索引把 0002/0003 误标"提议"（实为已采纳）、README 目录树与 CONVENTIONS §2 补 `oss-repos/`/`harness-hub/` 本地目录说明；**待拍板 5 项**（P3 直推 vs PR 口径与分支保护冲突、P4 提交署名 3 人不统一、P5 spike 模板零使用且与 §4 矛盾、P6 brief-plan §12.0 scratch 表述与 §4 冲突、P7 可读性修复挂起）；观察项 3 条。**未触碰 brief-plan 正文实质章节与 W3/harness 暂停令。**
- **[dev] W3 独立 demo 跑通** → `research-demos/w3-lookahead-proof-demo/`：`WindowedView` 接口层前视构造性不可能（越界抛 `LookaheadViolation`）+ 动态审计/静态扫描双 lint + 指标库单入口（三仪器齐算）+ assigned_role opt-in；纯标准库、Python 3.14.6 实测 **12/12 unittest**，4 步操作剧本全过（干净回测 +123.8% 零越界 / 越界读被拒、泄露预言机 536% 拦截展示 / 绕过策略 299+7 条双 lint 定罪 / 角色路径双路共存），README 实测口径已落。决策记录 0004 待按"先决策后修订"写入（落点对齐 W3 笔记采纳①–⑤）；W4 demo 脚手架同笔更新，依据文献改链 W4 笔记。
- **[dev] 口径校正 + 决策记录 0004 提议落库**：按 @research 独立复跑后的 2 条校正修改——①README/demo 的「三仪器齐算」改为**部分验证**（指标单入口 ✓，trial ledger+DSR/PBO/held-out 未实现、留 §8 A2/W6+）；②demo 输出标签「行为等价复核」→「因果合规复核」（access_log 只证明没读未来的必要条件，ActionMatch 语义等价留 W6），改后 12/12 测试复跑通过。新增 [decisions/0004](decisions/0004-w3-backtest-reliability-and-lookahead-guard.md)（状态：**提议**）：采纳①–⑤逐条标注验证状态（①部分实证/②部分验证/③拆两级：因果✓语义留/④⑤未验证留测评线）+ assigned_role 实证 + 实测数据表；brief-plan 修订待核验转已采纳后定点留痕。等 @research 双轮核验。
- **[research] 双轮核验通过，0004 转「已采纳」**（2026-11-10）：①口径比对——0004 采纳①–⑤验证状态标注与 [W3 笔记](literature/W3-backtest-reliability.md) §3/§4 逐条一致（①部分实证/②部分验证/③因果✓语义留 W6/④⑤未验证留测评线），备选方案表覆盖笔记全部不采纳项；②实测回抽——本机独立复跑 12/12、clean `1.238231/5.0515/-0.1027`、leak `LookaheadViolation`+536.10%、bypass 299+7、roles 双路径与实测表逐位一致，`124ac3a` diff 确认仅改标签/文档未动代码路径，3bp 费率回抽 `backtest.py cost_rate=0.0003` 命中；③decisions/README 索引同步已采纳。**后续：@dev 执行 brief-plan §5.6/§6.1/§8 A2/§12.1 W3/§12.2 W3 五处定点修订留痕**（注：demo README 第 56 行「0004 待写」为过期指针，随修订一并清）。
- **[dev] brief-plan 五处定点修订（依据已采纳的 [decisions/0004](decisions/0004-w3-backtest-reliability-and-lookahead-guard.md)）**：§5.6 增 GoalStrategyBase 三层构造性防护留痕（API面+registry flag+回调 buffer，接口层/双 lint 已实测、平台侧随 harness 落地）；§6.1 增字段状态留痕（指标单入口已实证、`trial_count/effective_trials/psr/dsr` 未实现禁按已就绪引用，验收拆因果✓/语义留 W6 两级）；§8 A2 补门禁合取+预算化落点（0004 决策 5，标未验证留测评线）；§12.1 W3 行回填 demo 证据（12/12、536% 拦截、299+7 定罪、①–⑤验证状态）；§12.2 W3 行补 assigned_role demo 实证。三张表行管道数校验不变（6/6/5）。demo README 过期指针「0004 待写」清为已采纳链接，research-demos 索引同步。等 @research 修订复核。
- **[dev] W4 独立 demo 跑通** → `research-demos/w4-approval-gate-demo/`：use-time 重建完整操作+material arguments digest 比对+原子消费（复刻 Loopjacking A→B 替换攻击作负例，弱绑定对照放行、digest 绑定必拒）、审批通道独立于 agent 命名空间（采纳②最小验证）、角色×工具矩阵 frozen 不可变+版本化撤销+总线授权载荷结构性忽略（BOUNDARY-TAMPER 审计）、预算按 goal 整体计、deterministic monitor 唯一防线（judge 误放行照拦、判定零耦合）。纯标准库 Python 3.14.6 实测 **16/16 unittest**，5 步操作剧本全过；README 实测口径与对齐说明（采纳①–④逐条）已落。决策记录 0005 待提议。
- **[research] brief-plan 工作区改动处置（@dev 落库前核验发现）**：工作区一处非本轮产出的内容更正——附录第 8 条"文档位置 Desktop 不进仓库"改删除线标注"已进仓库"——**保留并在复盘 §5 披露**；同批表格格式化噪声（含 `test_expired_*` code span 被破坏、Rakazo 行 bold 断行）已 `git checkout` 还原，brief-plan 仍 583 行、行号引用不受影响，`git diff` 仅剩该第 8 条一处。

### 2026-11-03（全仓可读性排查 + docs/translations/ 中译目录建立）

- **[user] 指令（2026-11-03）**：①排查当前工作区所有文档的人类可读性；②docs 下加翻译目录，把所有下载的论文、引用到的网上英文文献、项目英文文档翻译成人类可读的中文。
- **[research] 可读性排查完成** → [readability-audit-2026-11-03.md](readability-audit-2026-11-03.md)：28 个自有 md 结构层全健康（0 断链 / 0 标题断层 / 0 围栏破损 / 0 敏感文件入库）；排版层 4 类问题——28 处墙式段落（最长 3996 字符）、走读笔记英文占比过高（opendots 2927:3288）、4 处缺状态头（brief-plan + hermes/openmuse/rakazo 笔记）、brief-plan 583 行无目录。**修复列为待拍板**：会移动 @dev 已核验的行号引用，建议批量改后重核；本轮未改任何既有文档。
- **[research] `docs/translations/` 建立**（规范 [translations/README.md](translations/README.md)）：三类收录（papers=已下载论文全文中译 / literature=仅摘要级引用的题录摘要中译 / projects=被引用项目英文文档中译），文件头模板 + §4 人类可读性硬要求（自然中文、单段 ≤500 汉字、术语保留英文、翻译深度诚实标注）。CONVENTIONS §2 与根 README 目录树已同步。
- **[research] 翻译批量执行完成（13 个并行子代理，三批）** → `docs/translations/` 共 **67 篇译文 / 1.6MB**：papers **8/8 全文**（含目录与图表题注，双栏提取交错各篇均换 `-layout`/`-raw` 重提解决并如实记录）；literature **30/30 摘要级**（23 篇 arXiv + 7 篇非 arXiv，零失败零「未获取」）；projects **29 篇**（rakazo 7 / opendots 5 / openmuse 4 / hermes 8 / dsh-superagent 5，含官网页中译与两篇官方中文 README 指路文件）。
- **[research] 机器终检通过**（`check_translations.py`）：文件头六字段全齐、单段 ≤500 汉字 0 违例、围栏 0 破损、目录对正文 0 缺项；mtime 快照连续三轮零变化确认落盘稳定。终检发现的 14 条「尾部疑似截断」经逐条人工核看全部为完整列表项/链接行的误报，rakazo 3 个漏头小文件已就地补头。README §5 索引 67 条从磁盘逐篇点名生成，链接 0 断。
- **[research] 终检补修（同日复检，提交见 git log）**：删除 7 处指向本地 PDF 的图片占位（`papers/2609.34215` ×2、`papers/2610.14515` ×5——紧邻段落已带「图X：…（原文位置：PDF 第N页）」文字说明，且 PDF 路径无法作为图片渲染）；`translations/README.md` §4 新增第 8 条**终检口径**：段落按空行/列表项切分、表格与代码块不计、源文相对链接保留原样（未译者指向原仓属预期）。按该口径 67 篇复检：文件头全齐（hermes 6 篇 Docusaurus frontmatter 在前属结构对齐）、围栏 0 破损、段落上限 0 违例（**按汉字计**，§4.3 已补计数口径）。
- **[research] 同类图链补修 28 处（@dev 首轮核验指出首修漏检）**：`2610.27645` ×13、`2610.34724` ×8、`2610.38573` ×4、`2610.26995` ×3——分别是指向本地 PDF 的 `![](…)` 与把说明文字塞进 URL 括号的无效图链，全部改为纯文字「（原文位置：…）」并保留页码与提取失败诚实标注。复扫全目录：非 URL 图链 **0 残留**（README 模板占位除外），「译文内链 0 失效」至此成立；邻接图题注均含图内容说明，信息无丢失。
- harness 先不开发、W3 先不开（@user 2026-11-03 拍板）不变；剩余待办 AWM spike（等 T1 回测数据）。

### 2026-11-03（harness-hub 本地副本 + `zdf-dev-goal-quant` 分支）

- **[research] harness-hub 本地副本建立**（@user 指令）：`../harness-hub`（源仓 `/Users/amoris/agent-studio/harness-hub`）复制为 `goal-quant-research/harness-hub/`（12G，APFS clonefile）；`.gitignore` 新增 `harness-hub/`（已 `check-ignore` 验证命中）——按 CONVENTIONS §6 **不入库**，仅作本地研究引用源。源仓未被改动（复制期间其 HEAD 由另一会话从 `ae0d71aa6` 推进到 `653791df8`，仍在 `zdf-dev-1102`）。
- **[research] 分支拉出**：在副本内 `git fetch origin fix-20261019203013`（公司 GitLab 可达，最新 `ee50ae7d3`）→ `git checkout -B zdf-dev-goal-quant origin/fix-20261019203013`，副本工作树现为该分支内容；源仓与远端分支均未动。
- **[user] 指令（2026-11-03）**：harness 部分**先不开发**；**W3 也先不开**（暂停令维持，不进入 W3）；其余照常处理——§3.1 已闭环、通道已恢复、推送正常，当前无阻塞。

### 2026-11-03（通道恢复：oss-repos 建立 + 五仓克隆 + 四项目走读完成 + DeepSeek 源码增补）

- **[research] 境外通道恢复实测**：`github.com`/`api.github.com`/`arxiv.org` 探针全 200，`gh auth status`（noire02qwq，keyring）有效——2026-11-02 的「不推远端」限制按 @user 指令解除，本轮提交全部已推送。
- **[research] `oss-repos/` 本地克隆目录建立**（已 gitignore，提交 `0343e0c`）：克隆 `dsh-superagent-prototype` / `rakazo` / `openmuse` / `OpenDots` / `hermes-agent` 五仓（depth 1，约 538MB），为研究笔记提供可引用的本地源码。
- **[research] DeepSeek Super-agent 笔记源码级增补**（`c80f4eb`）：新增 §7 七条——Decision 五值修正（`reopen`，docs/007 只列四值）、Policy 变更三段式（在途 Eval 重排队 / Effect 投递 / revalidate 失权才撤）、**W1 恢复语义五条对拍清单**（recovery note、未入史 Input 保留、被杀作业下轮读取、Input 幂等、KV 读取位置）、danger-full-access 与 Watchdog 缺席升级为代码证据 → [essay-study/deepseek-super-agent-2026.md](essay-study/deepseek-super-agent-2026.md)。
- **[research] §3.1 四项目源码走读全部完成**（并行执行，笔记 4/4）：[rakazo-2026.md](essay-study/rakazo-2026.md)（交接 `clientNonce` 幂等 + 禁回弹 hop≤6、Routines 行级 CAS、15min 控制租约、**全仓无 `assigned_role`**——W3 角色字段需自建）；[openmuse-2026.md](essay-study/openmuse-2026.md)（四条映射逐条判定：一证实、三证实但有出入，`outcome_unknown` 仅 Action 层需上提到任务层）；[opendots-2026.md](essay-study/opendots-2026.md)（claim/interrupted UI 区分、权限三层 AND 热撤销、MCP 写动作 claim-once；与二手定位差异已留痕：无 agent 间交接/群组/事件触发）；[hermes-2026.md](essay-study/hermes-2026.md)（映射①主体证实+两处出入；**映射②后半推翻**——startup watchdog 是启动死锁看门狗不扫孤儿，恢复扫描改参照 kanban `reconcile_orphans` 与 cron pending_slot）。
- **[research] §3 主表回填 + §3.1 状态更新**（提交 `d36e83a`）：openmuse 四条升级为源码判定并附出入、hermes 两行按判定修正（watchdog 推翻按 CONVENTIONS §3 规则 7 留痕）、新增 Rakazo 三行与 OpenDots 三行；§3.1 状态 4/4「已读」、执行前置段标注「已解除」。**@dev 第二轮独立核验已通过（2026-11-03）**：四份笔记关键论断逐条回源属实（含 Rakazo 全仓无 `assigned_role`、OpenMuse 租约/退避数值、OpenDots 100ms/50ms watcher 行段、Hermes `jobs.py:260` 行号精确命中），§3.1 完成判据（走读→回填→留痕）本轮闭环。
- W3 暂停令不变；harness-hub 平台侧照旧等 @user 回公司内网。

### 2026-11-02（开源项目/文档研究计划增补）

- **[research] brief-plan 新增 §3.1「开源项目 / 官方文档研究计划」**（@user 指令）：纳入 **OpenMuse、OpenDots、Rakazo、Hermes** 四个对象，逐项列仓库/文档链接、二手定位、与本项目的关联点、通道恢复后的研读任务与状态；完成判据为 `docs/essay-study/<repo短名>-<年>.md` 走读笔记 → 机制映射回填 §3 主表 → 推翻假设按 CONVENTIONS §3 规则 7 留痕；优先级 **Rakazo**（§12.2 W3 群组分工/`group-handoff` 直接同构）> OpenMuse（§3 已有四条映射待源码验证）> OpenDots > Hermes（自身项目，利益相关需标注）。**OpenDots 仓库归属经 @user 确认取 `CopilotKit/OpenDots`**（同名 diggerhq/opendots 不在计划内），表内「待确认」已改为「待读」。
- **阻塞（境外通道，2026-11-02 实测）**：`github.com`/`api.github.com` TLS reset、代理 CONNECT 503、`gh` token 失效——四个项目的 README 与源码**均未读**，§3.1 表中定位取自可访问的二手来源（必应索引 + 中文技术站），已在表头显式标注"未读源码、不得当设计依据"。按 @user 指令**本轮只本地提交、不推远端**。
- W3 暂停令不变；harness-hub 平台侧照旧等 @user 回公司内网。

### 2026-11-01（brief-plan 按 0003 设计修订）

- **[dev] brief-plan 按 [decisions/0003](decisions/0003-w2-memory-distillation.md)（已采纳）完成设计修订**（PR 中）：§4.4 `goal_memory_digest` 增 lifecycle/valid_until/superseded_by/scope/author_agent_id 字段 + HaMo 三元组格式；§5.1 补 turn_context 记忆组装四步顺序（gate 先于 packing、挤出≠拒绝）；§5.4 主候选升级 SEPM+CALM 双主线（生命周期状态机、可计算晋升判据、TTL 第二通道、组装顺序、隐式沉淀须过 gate），含 @research 两条校准——coverage ≥0.30 为本项目实例化参数（HaMo 原文无固定阈值，机制为互补边际覆盖贪心+knee point）、SEPM safety/state-verification 两道 gate 未纳入（state 由回测/数据校验承担，safety 留平台侧）；§12.2 W2 群组记忆落点转「已定稿」（scope 三元组 + 准入 gate + 共享/私有注入规则）。四处均带修订留痕。

### 2026-11-01（0003 转已采纳）

- **[@research] 决策记录 [0003](decisions/0003-w2-memory-distillation.md) 文献复核后转「已采纳」**：七条决策逐条对照 [literature/W2](literature/W2-context-memory-distillation.md) 精读并回抽 PDF 核验数值——SEPM 晋升判据三数值（因果 0.65 / 复现≥1 / 效用≥0）与 CALM 关键数据（512-token 39.2 vs 29.6、污染 50% 注入仅掉 7.0pp）均确证。**一处校准**：coverage ≥0.30 是 demo 实例化参数，HaMo 原文为边际覆盖贪心 + knee point、无此固定阈值（机制方向忠实，不改决策，随 brief-plan 修订注明）。**简化项备查**：demo 未含 SEPM 原文同批的 safety/state gate，state 验证可由回测/数据校验承担，safety gate 留平台侧补。本机独立复跑：12/12 unittest + gate 三态冒烟（拦截/消融放行/好卡通过）与 README 操作剧本一致。
- literature/W2 §4「W2 demo 决策记录」项勾销（AWM 迁移性 spike 拆 W3+，风险项不动）。

### 2026-11-01（W2 记忆蒸馏 demo 跑通）

- **[dev] W2 demo 落地**（`research-demos/w2-memory-distillation-demo/`，PR 中）：SEPM/HaMo 双 gate（coverage 前置 ≥0.30 + reproduction 主 gate ≥1 复现/效用≥0/因果≥0.65）、CALM 裁剪生命周期（CANDIDATE→ACTIVE→STABLE→SUPERSEDED/STALE→ARCHIVED，迁移白名单）、16KB 组装 gate 先于 packing 且挤出≠拒绝、supersede 不删除+指针、TTL 第二触发通道。**12 个定点 unittest 全绿**；操作剧本 1–8 步在真实后端逐条验证（gate 拦截/全消融放行→污染进上下文/复评升 STABLE/TTL→STALE 行保留/supersede 保行/预算挤出标注）；Expo web 打包 193 modules 通过。
- **[dev] 遵守新规范（CONVENTIONS §4 规则 6/7/8）**：README 附十步操作剧本（操作→现象→对应结论）；前端 React Native/Expo 58 无 Electron；后端 Python 3.14.6 纯标准库（sqlite 3.53.2），环境实测表入 README。
- **[dev] 决策记录 [0003](decisions/0003-w2-memory-distillation.md)（提议态）**：七条——可计算晋升判据、gate 先于 packing、生命周期白名单、supersede 不删、TTL 第二通道、scope 字段级落库、demo 形态规范。待 @research W2 精读复核后转已采纳，再走 PR 修订 brief-plan §5.1/§5.4/§12.2。
- AWM workflow 归纳迁移性未进本 demo：需真实 T1 轨迹（W2 笔记 §5 风险项原样保留），留 W3+ 单独 spike。

### 2026-11-01（demo 新规范：可交互 + React Native + Python 版本一致）

- **[@user 提出，@research 落入 CONVENTIONS §4（新增规则 6/7/8）**：
  1. **可交互演示**：后续 demo 必须让人能实际操作、亲手感受研究原理（操作剧本：怎么操作 → 看到什么 → 对应哪条结论），不能只有脚本跑分；W1 recovery demo 已定稿不追溯，W2 起适用。
  2. **前端**：demo 图形界面尽量用 React Native 生态（Expo / react-native-macos），**避免 Electron**；偏离需在决策记录说明。
  3. **后端 Python**：所有 demo 统一 Python 3.14（基线 3.14.6，与 W1 实测一致），不混用大版本。
- **[@dev 当前状态**：W1 三件套已闭环（demo `cf941d8` + 0002 已采纳 + 设计修订 PR #4 `0e2eb13` 合入 main）；按其上一条消息正进入 **W2 记忆蒸馏 demo**（AWM 式 workflow 归纳最小 spike，SEPM/CALM 的 gate 与 supersede 语义进 demo 验证），决策记录从 0003 续编；harness-hub 平台侧仍等 @user 回公司内网。

### 2026-11-01（brief-plan 设计修订）

- **[dev] brief-plan 按 [decisions/0002](decisions/0002-w1-recovery-semantics.md)（已采纳）完成设计修订**（PR 中）：§4.4 领域模型——`goal_run` 状态/认领/租约/fencing 字段定稿、`goal_receipt` 两级幂等回执独立成表、新增 `goal_group_message`（锚点独立）与 `goal_effect_ledger`（第二 oracle）、`goal_event.actor_agent_id` 采纳；§5.2 规则 2/4/5 细化 + 新增规则 6（fencing 写保护）/7（外部 effect 台账对账）/8（六性质+FI+liveness 恢复语义验收清单）；§12.2 W1 落点定稿为「语义统一、锚点独立」。三处均带修订留痕。

### 2026-11-01（W1 文献线完成）

- **[research] W1/W2 文献补检与精读完成**（arXiv API，2026-11-01）：8 篇 2026 下半年（8–10 月）新论文 PDF 归档 `docs/papers/`（索引已更新），7 篇全文精读。W1 四篇（[Resume Means Resume](https://arxiv.org/abs/2608.03836)、[AgentRewind](https://arxiv.org/abs/2608.14380)、[Same Winners, Different Success Rates](https://arxiv.org/abs/2609.34215)、[CUA-Recovery](https://arxiv.org/abs/2610.27645)）→ [literature/W1](literature/W1-durable-scheduling-recovery.md)；W2 三篇精读+一篇摘要级（[SEPM](https://arxiv.org/abs/2610.14515)、[HaMo](https://arxiv.org/abs/2610.34724)、[CALM](https://arxiv.org/abs/2610.38573)、[SPEM](https://arxiv.org/abs/2610.26995)）→ [literature/W2](literature/W2-context-memory-distillation.md)。§12.1 W1/W2 行已回填（W1"待补"解除）。
- **[research] DeepSeek Super-agent 精读**：官方技术文章（2026-10-31）+ 开源原型 [dsh-superagent-prototype](https://github.com/deepseek-ai/dsh-superagent-prototype) 设计文档全文 → [essay-study/deepseek-super-agent-2026.md](essay-study/deepseek-super-agent-2026.md)。要点：Mandate 授权记录≈审批归因、Watchdog≈恢复扫描语义层、Source/Thread≈goal_event 持久化+订阅直通、Router/Worker≈群组静态分工；auto 主动接活与 danger-full-access 运行身份不采纳。
- **[research] 决策记录 [0002](decisions/0002-w1-recovery-semantics.md) 转「已采纳」**：五条决策逐条对照 W1 精读结果复核（语义校准：群组持久化=「语义统一、锚点独立」），并追加文献复核结论段——三项补充采纳（外部 effect ledger 第二 oracle、六性质+liveness 验收清单、takeover-depth 演练设计+检测/修复双指标）。@dev 可走 PR 修订 brief-plan §4.4/§5.2/§12.2。
- **[research] 关键方向结论**（详见两份文献笔记）：W2 主候选由 AWM/ExpeL 升级为 SEPM+CALM 并列（显式结构、生命周期 supersede 不删、gate 先于 token packing、晋升必须可计算判据），HaMo 补经验卡格式；§12.2 群组 scope 字段语义取 SEPM context conditions/exclusions。
- **[research] 规范更新**：CONVENTIONS §6 新增——公开仓库严禁公司 harness 项目源码（2026-11-01 用户规定，harness 分支拉出后 main 仍适用）。

### 2026-11-01（W1 启动）

- **[dev] W1 recovery demo 跑通**（`research-demos/w1-recovery-demo/`，PR 中）：三场景两连跑全 PASS——双 worker 抢占 12 任务 0 重复 0 丢失；第 2 步硬崩溃（exit 137）后 `running`+lease 过期 → 恢复扫描显式 `outcome_unknown` → 重排 → 幂等续跑（已完成步骤零重跑、中断步骤重跑一次）；双 agent 群组会话第 4 步崩溃后从持久化消息恢复，seq 1–6 完整无重复。9 个定点 unittest 全绿（fencing 拒旧 token、回执幂等、actor 归因等）。
- **[dev] 决策记录 [0002](decisions/0002-w1-recovery-semantics.md)（提议态）**：恢复语义五条定稿——`outcome_unknown` 显式化、调度四件套不重造、期次+步骤两级回执、fencing 写保护、群组消息独立于 goal_run 持久化（回答 §12.2 W1 问题）。待 @research W1 文献精读结论合入后转「已采纳」，再走 PR 修订 brief-plan §4.4/§5.2/§12.2。
- 约束确认：公开仓库不入公司 harness 源码（CONVENTIONS §6 已写入），demo 为独立原创最小实现；harness-hub 平台侧开发待 @user 回公司内网后启动。

### 2026-11-01

- **[dev] main 分支保护已开启**（GitHub 侧）：PR 必经 + `lint`（doc-lint）状态检查必过 + 禁 force push/删分支。enforce_admins=false（admin 紧急时可绕过，普通路径锁死）。至此「设计修订必须走 PR、必须过 lint」落地。此前 doc-lint workflow 已确认 active，main 最近两次 push 运行均 success。
- **[research] 规范更新（`888b001`）**：demo 入库以 brief-plan 定稿为界（vn-demo 为唯一例外，后续 demo 入 `research-demos/`）；新增引用链接硬性要求与 `docs/papers/` PDF 归档规范；仓库级提交身份配为 `noire02qwq <noire02qwq@users.noreply.github.com>`。
- **[dev] brief-plan §12.2 新增「多智能体群组配合交互」W1–W5 增量研究线**（决策记录 [decisions/0001](decisions/0001-multi-agent-group-research-increment.md)，走 PR）：每周挂靠一个群组子主题（W1 持久化基座 / W2 群组记忆模型 / W3 角色分工×DAG / W4 群组治理 / W5 群组故障注入），不动既有各周交付；候选论文均为仅摘要级且带 arXiv 链接；明确 W8 反方评审复用 W4 授权矩阵合流、不采纳 MARL 动态拓扑。
- **[dev] 仓库基建（`0cf5d1d`）**：PR 模板（设计修订 PR 强制填依据与留痕）、doc-lint workflow（PR 标题 Conventional Commits / 敏感文件守卫 / markdown 基础检查）、gitignore 收紧。

### 2026-11-01（暂停令）

- **[user] 指令：今天先不做 W3**。@research 手头无在途 W3 工作（W3 检索式尚未启动，无草稿产出），确认即停；W2 闭环（`867526d` → `42164cb` → `3426729`）为当前停点。恢复时间等 @user 下令。

## 阻塞 / 待办

- ~~境外通道恢复~~（**已解除 2026-11-03**：三探针 200 + `gh auth` 有效）→ §3.1 四项目走读已于同日完成（笔记 4/4、§3 回填），@dev 第二轮独立核验**已通过**，§3.1 判据闭环——**无阻塞**。~~待 @user 拍板是否解除 W3 暂停令~~ → **@user 2026-11-03 拍板：W3 先不开，暂停令维持**（无 W3 产物启动）。

- harness-hub 平台侧开发（插件脚手架、goal_* schema 落地、状态机全转换表实现侧）：**本地副本已就位 2026-11-03**（`harness-hub/`，gitignored，分支 `zdf-dev-goal-quant` ← `origin/fix-20261019203013` `ee50ae7d3`），但 @user 指示 **harness 部分先不开发**——源码引用可读，开发待后续下令。
- ~~@dev：走 PR 修订 brief-plan §5.1/§5.4/§12.2~~（**已完成 2026-11-01，PR #8 合入**：§4.4 字段 + §5.1 组装四步 + §5.4 SEPM+CALM 主线 + §12.2 W2 行，coverage 实例化说明与 safety gate 平台侧待补均注明，落点清单见 [decisions/0003](decisions/0003-w2-memory-distillation.md) 修订落点段）；0002 的 §4.4/§5.2/§12.2 W1 修订已随 PR #4 完成。
- AWM workflow 归纳迁移性 spike：等真实 T1 回测轨迹数据（W3+，依赖回测链路）。
- ~~@research：W3 文献检索式启动（已暂停）~~ → **@user 2026-11-10 指令恢复：W3/W4 文献线当日完成**（[W3 笔记](literature/W3-backtest-reliability.md)、[W4 笔记](literature/W4-hitl-approval-authorization.md)，原暂停令就研究线解除）。**剩余待补**：§12.2 W3 群组子题（角色分工×DAG）文献本轮未产出新增，MetaGPT/ChatDev 维持仅摘要级。
- @research：W3/W4 独立 demo 与 12 篇新 PDF 中译（见 2026-11-10 进度日志待办）。
