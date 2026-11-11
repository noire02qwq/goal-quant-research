# W5 故障注入演练 + 演示数据固定化 Demo

> 状态：**可运行（2026-11-11 实测，七步剧本全过）**｜ 周主题：W5（brief-plan §12.0 W5 研究项，@dev 主导）｜ 关联：§12.1 W5 方向①②③、§12.2 W5 追加条、W5 笔记采纳⑥故障分类学

## 1. 验证目标（对应 brief-plan / W5 笔记）

1. **注入① 改坏代码**（§12.0 W5 研究项）：故障 → 生成修复任务 → 修复 → 重进循环，**失败不终止**（§6.2 韧性）；重试仅故障步 +1、其余步零重跑。
2. **注入② 重启**：崩溃 → 恢复 → **已完成步骤零重跑**（步骤级幂等回执，0002 语义的进程内演练形态：首写胜出 + 回执命中计数）。与 §12.2 W5 追加条同语义——群组消息"语义统一、锚点独立"（0002 决策 5），本 demo 在单 Run 上演练该回执语义，**群组消息面留集成验收（搁置中）**，不声称覆盖。
3. **注入③ 改目标**：`goal_changed` 显式事件入审计、已完成步骤及其回执零改动、队列余下按新目标继续。
4. **注入④ interface 诚实类**（W5 笔记采纳⑥-ii，AllPath 教训）：静默成交偏差（界面 submitted、柜台实滑 1%）被对账器**点名**；**熔断真触发**（6% 跳变 > 3% 阈值 → `tripped=True` + 挂起回调），不做"武装但从未触发"的挂件。
5. **注入⑤ 数据面注入类**（采纳⑥-iii，Fake News 教训）：伪造新闻**不进 candle**——被污染与干净回测签名逐字节相等（**backtest 内不可见的正交性证明**）；feed 摄入口按签名+白名单**拦截**（61.7%→13.8% 的防线位），放行则恐慌词立即驱动力 −1 操纵决策。
6. **演示数据固定化**（§12.0 W5 + §12.1 方向①）：固定窗口（seed=20261111, bars=120）两次生成 sha256 一致；**T3 网格 / T4 经典海龟**模板可运行（参数白名单强制），回测经 w3 `lookahead_guard` 构造性防护（跨 demo 复用，本仓零回测实现）。
7. **注入分级**：已有平稳/超阈值两级阈值对照（测试断言平稳不触发）；takeover-depth 式**多级梯度**留汇报剧本排练时补（**当前未实现，如实标注**）。
8. **排名稳定性 Kendall τ_b（第 7 步，0006 实测行）**：两档执行假设（A 低摩擦 3bp / B 保守摩擦 25bp，滑点并入 cost_rate 的**简化合并口径、随输出披露**）下 T1/T3/T4 全套排名的 τ_b 可独立复算（τ_b 本体有已知值对拍测试）。**本 fixture 实测 +1.0000（n=3、仅此两档此窗口，不外推）**——正面意义是"假设披露后排序稳定性可报"，对照 Execution 论文 τ_b=0.21 的反面（不披露则排序本身不稳）。

**范围边界**：harness-hub 集成验收按 @user 指令搁置——全部为**独立进程内演练**；汇报剧本（逐句排练稿）与 0006 的汇报口径分档**不声称覆盖**；τ_b 实测已按第 8 条落（机制级修订 §6.1/§5.6 仍待 0006 已采纳）。

## 2. 运行方式（2026-11-11 实测）

- 环境：**Python 3.14.6**（CONVENTIONS §4.8）、本 demo 包 `drill/` **纯标准库**；回测仅经 `drill/bridge.py` 路径注入复用 w3-lookahead-proof-demo 的 `lookahead_guard`（零重复实现）
- 定点测试（demo 目录内）：

```bash
python3.14 -m unittest discover -s tests -v   # 实测 19/19 OK（含 τ_b 已知值对拍）
```

- 交互入口 / 分步命令（demo 目录内）：

```bash
python3.14 demo.py              # 交互菜单（可实际操作入口）
python3.14 demo.py repair       # 注入① 改坏代码
python3.14 demo.py restart      # 注入② 重启
python3.14 demo.py goalchange   # 注入③ 改目标
python3.14 demo.py interface    # 注入④ interface 诚实 + 熔断
python3.14 demo.py feed         # 注入⑤ 数据面注入
python3.14 demo.py fixtures     # 数据固定化 + T3/T4 模板
python3.14 demo.py taub         # 第 7 步：两档执行假设排名 τ_b
```

## 3. 操作剧本（实测输出，2026-11-11）

**`repair`——改坏代码**：修复任务 `['backtest']` 入队 → 第二轮完成 `['fetch','backtest','report']`、`executed={'fetch':1,'backtest':2,'report':1}` → **PASS**（失败未终止、仅故障步重试）

**`restart`——重启恢复**：崩溃于 `execute`（前两步已落回执）→ 重启完成 `['done:execute','done:notify']`、回执命中重放 **2** 次 → **PASS**（fetch/signal 零重跑）

**`goalchange`——改目标**：`goal_changed` 入审计、a 的回执保持 `True` → 队列余下 `['done:b','done:c']` 按新目标继续 → **PASS**（显式事件 + 已完成步骤零改动）

**`interface`——静默正常化 + 熔断**：`o-7: 界面 submitted ≠ 柜台 filled_real（真实 100@10.1，提交 100@10.0）——submitted≠filled 被点名`；正常单 0 条；跳变 6%>3% → `tripped=True, 回调 ['下单挂起']` → **PASS**

**`feed`——数据面注入**：回测签名 clean=`bafaac4fc874db88…` = poisoned=`bafaac4fc874db88…` **相等**（正交性证明）；伪造源 `admit=False` 拦截留审计 1 条；放行驱动力 **−1** → **PASS**

**`fixtures`——固定化 + 模板**：同 seed 两次 sha256 `bafaac4fc874db88…` 一致；T3 回测 `{'total_return': 0.13396, 'sharpe': 1.9005, 'max_drawdown': -0.056111}`、T4 `{'total_return': -0.069499, 'sharpe': -1.3921, 'max_drawdown': -0.069499}`；白名单外参数 `['momentum']` 被拒 → **PASS**

**`taub`——排名稳定性（第 7 步）**：A 档 `T3 +0.1340 > T1 -0.0160 > T4 -0.0695`；B 档 `T3 +0.1315 > T1 -0.0310 > T4 -0.0837`；**Kendall τ_b = +1.0000**（n=3）→ **PASS**（两档假设已披露、排序稳定性可复算；数值范围与对拍由 `tests/test_taub.py` 6 例锁定）

## 4. 结论指向的决策记录

- **0006（预留，@research 立）**：τ_b 排名稳定性第四维 + 汇报口径分档——依据 W5 笔记 §3.1-C 修正②③与 §3.2-采纳⑦；**τ_b 实测行已就位**（第 7 步：两档 +1.0000、τ_b 本体已知值对拍 6 例），五类注入与固定化为其余证面；机制级修订（§6.1/§5.6）按"先决策后修订"待 0006 已采纳后落
- 依据文献：[docs/literature/W5-real-eval-fault-style.md](../../docs/literature/W5-real-eval-fault-style.md)（8 篇全文精读，commit `f42838b`）；恢复语义基座 [decisions/0002](../../docs/decisions/0002-w1-recovery-semantics.md)
