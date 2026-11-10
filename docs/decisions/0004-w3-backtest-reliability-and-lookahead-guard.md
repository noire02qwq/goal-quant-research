# 0004：W3 回测可靠性——前视构造性防护定稿与回测验收口径（分层验证状态）

> 状态：已采纳（@research 双轮核验通过，2026-11-10：0004 vs W3 笔记采纳①–⑤逐条口径比对一致 + demo 实测独立回抽 12/12、四步数字逐位复现、3bp 费率回抽 `backtest.py cost_rate=0.0003`）｜ 日期：2026-11-10 ｜ 作者：@dev ｜ 核验：@research 2026-11-10 ｜ 关联：[literature/W3](../literature/W3-backtest-reliability.md)（7 精读 + 1 摘要级，采纳①–⑤）／[w3-lookahead-proof-demo](../../research-demos/w3-lookahead-proof-demo/README.md)（12/12 测试实测）／ brief-plan §5.6、§6.1、§8 A2、§12.1 W3、§12.2 W3

## 背景

W3 周主题「LLM 生成量化回测代码的可靠性、前视偏差」的文献结论已由 W3 笔记定稿为采纳①–⑤。本决策记录把 **w3-lookahead-proof-demo 的实测证据**与五条采纳的落点对齐，并按实测边界**逐条标注验证状态**——demo 证明了什么、没证明什么，避免"研究方向"被读成"已实证"（口径校正两条经 @research 2026-11-10 独立复跑后提出，已采纳进本记录）。

## 决策

1. **前视偏差的接口层构造性防护为目标不变，证据升级为三层**（W3 采纳①）：`GoalStrategyBase`（§5.6）API 面只暴露截至当前 bar 的数据 + 数据 registry flag（前视不可表达）+ 回调前入 buffer、越界抛不可吞错误（MintEval 形态）。
   - **验证状态：部分实证**。demo 已实证接口层钳制（`WindowedView` 钳制 `[0,t]`，越界抛 `LookaheadViolation`，步骤 2 实测）与第二道防线双 lint（步骤 3 实测：动态 299 + 静态 7）；registry flag 与 buffer 时序属平台实现，随 harness 集成落地（集成按 @user 2026-11-10 指令搁置）。
2. **指标单入口落地；账本与三仪器不并入本决策的"已实现"范围**（W3 采纳②，**部分验证**）：指标计算统一走 `lookahead_guard/metrics.py` 单入口（策略只产出仓位序列，实测 ✓）——这是账本单入口的前提。**trial ledger、DSR/PBO/held-out 三仪器本 demo 未实现**，按采纳②落点留 §8 A2 强制 gate 与 §6.1 `trial_count/effective_trials/psr/dsr` 字段，待测评阶段（W6+）实现验证。
3. **回测验收口径拆分为两级**（W3 采纳③）：
   - **因果合规**（access_log 全量复核 index ≤ step = "没读未来"的必要条件）——**已验证**（步骤 1：6390 条读取零违例）；
   - **语义等价**（ActionMatch/TradeF1 与参考实现逐 bar 动作比对）——**未实现、未验证**，留 W6 验收路径；不采纳读码 judge（QuantCode-Bench：放行全部 55 个静默失败）。
   - demo 输出标签已由「行为等价复核」更正为「因果合规复核」（@research 校正，2026-11-10）。
4. **样本外窗口起点用实测知识边界 + Tight/Wide 置信标签**（W3 采纳④）——**未验证，留测评线**；§12.1 既有"取晚于模型知识截止"结论待测评阶段升级，本 demo 不涉样本外划分。
5. **门禁合取 + 预算化选型**（W3 采纳⑤：绝对门合取、ranking 只在过门者中选、≤3+1 次评估、候选哈希去重）——**未验证，留测评线**，落点 §8 A2 与 DSR/PBO 并列。
6. **assigned_role opt-in 群组路径成立**（brief-plan §12.2 W3）：任务可选角色约束，不填即单角色零改动路径、填了则角色不匹配认领被拒（步骤 4 实测）——`goal_plan_task` 增加可选 `assigned_role` 字段的设计前提在 demo 中成立。

## 实测数据（2026-11-10，Python 3.14.6，纯标准库零依赖）

| 项 | 实测 |
|---|---|
| 定点测试 | `python3.14 -m unittest discover -s tests -v` → **12/12 OK** |
| 步骤 1 干净回测 | `total_return 1.238231 / sharpe 5.0515 / max_drawdown -0.1027`（300 bars，全仓进出含费 3bp） |
| 因果合规复核 | access_log **6390** 条读取，index≤step 违例 **0**；双 lint（动态/静态）发现 **0/0** |
| 步骤 2 越界读未来 | `LookaheadViolation: bar 1 超出可见地平线 t=0`（接口层拒绝）；泄露预言机（测量侧对照）假想收益 **536.10%** |
| 步骤 3 绕过策略 | 动态审计 **299** 条（file:line 级，index>step）+ 静态扫描 **7** 条（持有原始源/`raw_close` 直读）→ 双层均捕获 |
| 步骤 4 角色路径 | 无约束任务双角色均可领（零改动路径）；`reviewer` 约束任务被 coder 认领 → 拒绝；reviewer 认领成功 |
| 独立复跑 | @research 本机逐条复现，数字与 README 逐位一致（2026-11-10） |

## 理由

- **接口层 > 提示词/事后 lint**：BacktestBench 反面教训（look-ahead 只写 prompt、防线为零）+ What survives（泄漏 oracle 过 DSR/PBO 也过不了结构护栏，统计修正不能替代）；demo 给出同向实测：预言机 536% 的诱惑在接口层直接不可达。
- **因果合规与语义等价必须分开声称**：access_log 零越界只证明"没读未来"，MintEval（spec 完全正确的编译运行中 0.792 的 ActionMatch<0.9）说明语义等价需独立验收——混写会把必要条件当成充分条件。
- **指标单入口先行**：BacktestBench「不让模型自写指标公式」可即刻落地且已落地；账本/三仪器依赖测评管线，强行并入 demo 会造成"已实现"错觉（@research 校正 1 的核心）。

## 备选方案（不采纳的）

| 备选 | 不采纳理由 |
|---|---|
| 只靠提示词约束前视 + 事后 lint 单防线 | BacktestBench 反面教训：防线为零；demo 证明 lint 是第二道防线，不能替代接口层 |
| 单一分数/单一仪器验收 | W3 笔记不采纳项：DSR 拦不住泄漏、PBO 拦不住绝对崩塌、ranking 分不能放行 |
| 读码 judge 验收回测代码 | QuantCode-Bench：放行 Opus 5.5 全部 55 个静默失败 |
| 把 demo 的因果合规审计当语义等价证据 | MintEval ActionMatch 数据：逐 bar 语义比对缺位时 0.792 的实现会通过"没读未来"审计 |
| demo 内实现完整 trial ledger + DSR/PBO | 超出 W3 demo 验证目标；属 §8 A2/测评线（W6+），提前实现会造成口径混淆 |

## 对设计文档的修订

- brief-plan.md §5.6（GoalStrategyBase 三层防护证据升级）、§6.1（指标/账本字段状态标注）、§8 A2（门禁合取落点）、§12.1 W3 行（demo 证据回填）、§12.2 W3 行（assigned_role demo 实证）：**是否已更新：是**（2026-11-10 五处定点修订留痕，commit `d9bf005`，转已采纳 `0ec7d40` 后执行）。

## 后续动作

- [x] @research 双轮核验：0004 vs W3 笔记 §3 采纳①–⑤口径 + demo 实测回抽（2026-11-10 通过：①–⑤验证状态标注与笔记一致；`124ac3a` 仅改标签/文档未动代码路径，回抽与上轮复跑逐位一致）
- [ ] 核验通过转"已采纳"后，brief-plan §5.6/§6.1/§8/§12.1/§12.2 定点修订留痕（@dev）
- [ ] registry flag + 回调前入 buffer 的平台侧实现（harness 集成解除搁置后，@dev）
- [ ] ActionMatch 参考比对验收 + trial ledger/DSR/PBO/held-out 三仪器（W6 测评线，@dev/@research 分工随 W6 定）
