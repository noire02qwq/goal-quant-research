# W5：金融 agent 的真实评测、故障与风格差异

> 状态：定稿 ｜ 检索日期：2026-11-11 ｜ 对应 brief-plan.md §12.1 第 W5 行（§12.2 W5 群组行按计划无新增检索）
> 触发：@user 2026-11-11 指令「根据进度进行 W5 的论文、文献、独立 demo 研究，harness-hub 的集成开发先搁置」。

## 1. 检索式与日期

- 检索日期：2026-11-11；arXiv API 五式（`sortBy=submittedDate&sortOrder=descending`）：
  - `ti:"Agent Market Arena"`（计划内名字定位，**无果**——经 web 检索定位其 arXiv 号为 2510.11695《When Agents Trade》、ACM WWW'26 版 DOI 10.1145/3774904.3792821，再 `id_list` 回核标题后下载）
  - `abs:"live trading" AND abs:LLM`
  - `(abs:"paper trading" OR abs:"forward test*" OR abs:"out-of-sample") AND abs:LLM AND abs:trading`
  - `abs:"trading agent" AND abs:benchmark AND abs:LLM`
  - `abs:LLM AND abs:agent AND (abs:robustness OR abs:failure) AND abs:trading`
- 候选池 40+，入选 8 篇全文精读（计划内 3 篇升级 + 真实评测面 3 篇 + 故障面 2 篇）。
- 流程改进（HALO 错档教训，W3 补检事故）：**每个 ID 下载前先 `id_list` 回核标题**，8/8 通过；pdfinfo + `%%EOF` + 首页标题三查归档。
- 局限：仍全部走 arXiv API（dataPro 不可用）；Agent Market Arena 的 WWW'26 正式版以 arXiv v2 为准、未核 ACM 版差异。

## 2. 入选论文（8 篇全文精读）

| 论文 | 一句话贡献 | 与本项目的关系 | 状态 |
|---|---|---|---|
| LiveTradeBench（[2511.03628](https://arxiv.org/abs/2511.03628)，2025-11） | 50 交易日实时流式双市场（15 股+Polymarket 10 市场）评 21 个 LLM；LMArena 分数与收益 Spearman 仅 0.054/−0.38；rolling-k delta 检验行为非随机 | 「live 才可信」的直接实证 + 通用榜单≠金融能力；**无成本模型**是其自认局限 | 已精读 |
| Agent Market Arena（[2510.11695](https://arxiv.org/abs/2510.11695)，WWW 2026） | 实时多市场基准：统一协议下 4 框架×5 骨架；**固定框架换 LLM 变化小、固定 LLM 换框架差异巨大**（风格差异核心证据） | 风格是**结构属性非模型属性**；其自身「跑赢 B&H」强宣称是 B 的反面教材 | 已精读 |
| Strat-LLM（[2605.06024](https://arxiv.org/abs/2605.06024)，2026-05） | Free/Guided/Strict **规则约束强度三档** + T+1 开盘成交扣成本 live-forward 2025；高胜率陷阱（WR 66.67% 的 TR 10.55% < WR 54.55% 的 TR 12.31%）；90 日窗显著优于 15 日窗 | **D 结论（授权档位）的主要来源**；A 的 T+1 具体实现；档位效用随市场状态翻转的警示 | 已精读 |
| Can AI Make Money in Crypto?（[2609.34510](https://arxiv.org/abs/2609.34510)，2026-09） | 三阶段协议（回测→模拟盘→实盘）量化差距：模拟盘比回测接近实盘（alpha 平均差 58.85→28.51pp）；ML 与 LLM/agent 族在回测与前瞻中**完全对调**；实盘 4 方法无人跑赢 B&H | 模拟盘中间层的实证支撑 + B 的最强基准事实 + 方法族排名依赖评测阶段 | 已精读 |
| The Alpha Illusion（[2605.16895](https://arxiv.org/abs/2605.16895)，2026-05） | 立场论文：reported alpha ≠ 部署证据；**P1–P6 最小报告协议** + **宣称强度四档措辞表**；35/40 摩擦单元未建模；净口径复现 TA gross $106.4K→net $102.3K（Sharpe 0.43→0.22） | **B 与 D 的直接来源**（措辞分档=档位原型）；六类故障分类学 | 已精读 |
| AllPath（[2610.26662](https://arxiv.org/abs/2610.26662)，2026-10，ICAIF workshop non-archival） | 部署期三层验证（code/agent 自验/人）+ 执行授权四档 notify/confirm/auto/hard + human-gated vs autonomous 修订 regime 对照；**明文不报账户收益**；人工否决 median 8.8h，自由档 11/19 条事后撤销 median 8 天 | D 的部署证据 + B 的最直接同口径先例 + 故障账本（20 起事故全过 gate 由人发现） | 已精读 |
| Execution Assumptions（[2610.05077](https://arxiv.org/abs/2610.05077)，2026-10） | 换成交假设改的不只是收益是**排序**：高波动压缩板 E0→E1 Kendall τ_b=0.21；5 个 LLM 策略名次上移 2–7 位系执行伪影 | **C 的第四维（排名稳定性）来源**；A 的补充条款（执行假设显式披露+敏感性重跑） | 已精读 |
| Fake News, Real Crashes（[2610.26438](https://arxiv.org/abs/2610.26438)，2026-10） | 数据面信息注入攻击：mean ASR **61.7%** vs 控制面 13.8%（4.5×）；呈现风格去掉来源/紧迫标记 ASR 100%→0%；拓扑 star 9% vs debate 74%；防御须 ASR@固定 FPR + 状态条件化 | 故障面另一半（输入证据污染）；「档位收益状态条件化」修正；评测协议风格可伪造免疫的警告 | 已精读 |

## 3. 方向结论

### 3.1 对 §12.1 W5 既有四条的逐条判定（8 篇合议）

- **A「固定窗口+模拟盘 T+1 前向跟踪」→ 支持 + 三处修正**。
  支持：实时流式防泄漏（LTB）、固定协议+warm-up 后前向（AMA）、T+1 开盘成交扣成本（Strat-LLM）、三阶段冻结配置（Crypto）、paper simulator next-open 无前视（Fake News）。
  修正 ①**「T+1」措辞收窄**：只有 Strat-LLM 直接实现 T+1 开盘成交，其余为 t→t+1 前向定价/next-open——汇报口径写「日频 t→t+1 前向（Strat-LLM 为 T+1 开盘成交扣成本的具体实现）」；修正 ②**窗口长度须披露并论证**（Strat-LLM 90d>15d；Alpha Illusion 短窗 Sharpe 必须带 CI；Crypto 实盘仅 28 天不足以支撑统计结论）；修正 ③**新增条款：执行假设显式披露 + 至少一档敏感性重跑并报排名稳定性 τ_b**（Execution——仅固定窗口不够，窗口内成交/延迟/成本假设不披露则排序本身不稳）。
- **B「不宣称跑赢，口径=流程可靠+证据完整」→ 8 篇全部强支持**。
  Crypto 实盘 4/4 负 alpha、无人跑赢 B&H（基准事实）；AllPath 明文「不报收益，7.5 周窗口统计上不支持任何方向的绩效声称」；Alpha Illusion 表 2 给出与证据同档的可用措辞（「A backtest is a backtest」）；Execution 明拒比较交易能力；LiveTradeBench 全文无基准对照结果；AMA 自身「consistently outperform」宣称因无显著性检验 + 表内大量负单元恰成反面教材；Fake News 给机制理由——注入环境下 P&L 符号由攻击者与市场共同决定，「盈利的战役仍是被劫持的战役」。
- **C「指标同含收益/回撤/成本、不止胜率」→ 支持 + 三处修正**。
  支持：五指标联合（LTB：WR 65.31% 的 Grok-3 CR 仅 3.22，胜率不可互代）、成本恒等式必扣项（Alpha Illusion 35/40 未建模→gross 是上界）、成本参数显式（Execution 1bp 佣金+2bp 滑点）、回撤与成本同报的必要性论证（Fake News：bullish 战役 +$1,309 却 +7.9pp 无控回撤）。
  修正 ①**成本维度须自补**——LTB/AMA/Strat-LLM 三篇均无独立成本指标（LTB 还自认未计成本会高估收益），不能引它们为成本维度依据；修正 ②**加第四维：排名稳定性（τ_b/top-3 Jaccard）随收益同报**（Execution）；修正 ③**措辞改写**：C 应表述为「**凡报收益必须同时报回撤与成本**」而非「必须报收益」——AllPath 是边界反例（部署期评测刻意零收益指标、全用 operational 指标）。
- **D「严格/引导/自由授权档位可借鉴为策略修改权限档位」→ 两处主要来源 + 三处修正，判定「可借鉴但需换轴」**。
  来源：Strat-LLM 的 Free/Guided/Strict 三档（并给出档位规律：推理模型宜 Free、标准模型需 Strict 当风险锚、超大模型需 Guided、档位效用随市场状态翻转）；Alpha Illusion 的宣称强度四档「证据→协议→可用措辞」表（档位设计原型）；AllPath 的部署证据（执行档 notify/confirm/auto/hard、修订档 human-gated/autonomous、chat 通道两 regime 恒为人审的 within 对照）。
  修正 ①**两层轴**：执行授权档 × 修改权限档是两根轴（AllPath/Fake News 的档位作用于交易动作与仓位，策略修改权限由 regime+字段冻结单独控制），不可合并；修正 ②**冻结与非对称**：档位本身必须是自修改不可达字段（self-revision 永不能改 auth/status），且机器可收紧不可放宽（熔断降级自动、升格人做）；修正 ③**状态条件化报告 + 证据强度上限**：档位安全收益按 agent 状态分层（Fake News：conservative 对 BUY 基线零保护），且 AllPath 两 regime 是顺序自然实验只支持存在性结论——「哪个档更安全」不可由此宣称。

### 3.2 新增方向结论（原四条之外）

- **采纳⑤：风格差异对比必须在统一协议 + 披露执行假设下进行**。三源合取：AMA「框架>骨架」（同一信息四框架首日起分歧）× Strat-LLM「风格=档位×市场状态×模型类型×规模的交互」（同一模型换档位即翻转风格）× Execution「排名差异可能是执行伪影」（高波板经典→LLM 的翻转由成交假设制造）。另加 Fake News 的评测风格警告：标记化注入评测会系统性低估脆弱性（显式标记 0% → 混入 feed 46%）——**呈现方式本身能伪造「免疫」印象**。
- **采纳⑥：故障分类学三分**，供故障注入演练设计（§12.1 W5 研究项）：(i) **评测口径故障**六类——时间污染/摩擦漏计/短窗多重检验/未校准置信/数值执行失败/多 agent 回声室（Alpha Illusion）；(ii) **部署链路故障**——AllPath 20 起事故编目，最有教益的 6 起生产事故**全部通过所有 gate、由操作者手工发现**，共同修复是 interface 诚实（submitted≠filled、静默可见化）；「熔断器全程武装但从未触发」= 演练必须真触发 backstop；(iii) **输入证据故障**——数据面注入未设防（61.7% vs 13.8%），与 (ii) 正交、backtest 内均不可见。
- **采纳⑦：模拟盘中间层协议（汇报演示直接依据）**。Crypto 三阶段：配置跨阶段冻结、top 晋级、同成本口径贯穿；实证模拟盘比回测接近实盘（alpha 差 −52%、Sharpe 差 −51%）但**不能替代实盘**；配合 LiveTradeBench 的 t→t+1 前向与 rolling-k delta 非随机检验（行为真实性最低门槛）。→ §12.1 W5 落点①「固定窗口+模拟盘 T+1 前向」升级为**三阶段冻结配置 + 中间层定位**的完整表述。
- **工具件清单**（可直接进演示与验收）：P1–P6 报告清单、宣称强度四档措辞表、ASR@固定 FPR + Pareto、rolling-k delta、Kendall τ_b 排名稳定性、gross→net 分层恒等式。

### 3.3 不采纳/存疑（跨篇）

- AMA 表 1 HedgeFundAgent 五行逐位全同（疑表格错误，该行数据不采纳）；其「跑赢 B&H」宣称不采纳（2 月无 CI、CR 口径 B&H 反而更高）。
- Execution τ_b=0.21 不可外推（作者自认「最强结果也是最窄的」）；其 LLM 标识 4/5 为路由别名不可复现，模型间比较不采纳。
- LiveTradeBench 无成本模型、无基准对照、单窗口单次运行（temp 0.3）——收益数字不外推；图 7 柱值原文此处无法可靠提取。
- Strat-LLM「A 股=上涨、美股=下跌」状态与市场混杂，regime 结论不作普适规律；表 II 提取件乱码部分不引用。
- Crypto 实盘仅 28 天、按回测挑 top 有幸存者晋级；DeepSeek 高 alpha 系 10× 杠杆轨迹，不引为能力证据。
- AllPath 单系统单操作者（human verifier 即第一作者）、workshop non-archival、paper trading——按非正式同行评审对待，human 层结论读作现象下界。
- Fake News 多数为均值无 CI、部分 grid 极值无多重校正；经济数字自标 order-of-magnitude。
- 全部为 arXiv 预印本（2 篇 workshop/非归档），结论强度按 preprint 对待。

## 4. 对设计文档的修订

- [x] brief-plan §12.1 W5 行：候选升级 8 篇全文精读、四条结论按本笔记 3.1 修正版重写并补 ⑤⑥⑦（2026-11-11 同步）。
- [ ] §6.1 指标行加「排名稳定性 τ_b」为第四维、§5.6 汇报口径按 B 的分档措辞收口：**机制级修订，待 W5 demo + 决策记录（0006 预留）后落**，本轮不改设计正文。
- [ ] §12.2 W5 群组行：按计划**无新增检索**，「成员 Run 崩溃/消息丢失不重复执行」幂等回执落点不变（AllPath/Fake News 的结论不进群组行，留 W8 合并精读）。
- 演示线输入（交接 @dev）：故障注入三路径（改坏代码/重启/改目标）之外，按采纳⑥追加两类——**interface 诚实类**（submitted≠filled 式静默正常）与**数据面注入类**（伪造新闻喂入）；熔断类注入必须真触发 backstop（AllPath 教训）。

## 5. 风险与待验证项

- 「T+1 前向」在 8 篇中仅 Strat-LLM 直接实现——W5 汇报演示的成交时序口径须先自定（T+1 开盘 vs next-open vs 日频 t→t+1）并写进剧本，不能含混引用。
- 全部预印本 + 短窗普遍（50d/2 月/28d/7.5 周），数字按方向性参考；AMA/Strat-LLM 均无显著性检验。
- 翻译债：本轮 8 篇新 PDF 尚未入 `docs/translations/papers/`（待办见 PROGRESS）。
