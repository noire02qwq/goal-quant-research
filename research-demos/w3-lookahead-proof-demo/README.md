# W3 前视偏差构造性不可能 Demo（草稿）

> 状态：草稿（脚手架已建，实现中）｜ 周主题：W3 LLM 生成量化回测代码的可靠性、前视偏差（brief-plan §12.1 W3）｜ 群组挂靠：§12.2 W3 任务分解（assigned_role opt-in）

## 1. 验证目标（对应 brief-plan 设计问题）

1. **前视偏差在接口层构造性不可能**（§12.1 W3 方向①）：数据访问 API 只暴露"截至当前 bar"的窗口视图——策略代码在正常路径下**拿不到未来数据**，而不是靠提示词或事后 lint。对照组：同一策略的"泄露变体"（尝试读未来）在 API 层被结构性拒绝。
2. **第二道防线前视 lint**（§12.1 W3 方向②）：绕过封装直读原始数据的路径由 lint 检测（对应 market-research 既有前视 lint 思路），demo 展示"API 拦截 + lint 捕获"双层。
3. **指标统一计算，不让模型自己写公式**（§12.1 W3 方向③，BacktestBench 结论）：收益/夏普/回撤全部走指标库函数，策略侧只产出持仓序列。
4. **群组任务分解 opt-in**（§12.2 W3）：任务可选填 `assigned_role`（researcher/coder/reviewer），不填则单角色路径零改动——demo 中以双 worker 抢占场景演示"填与不填"两种路径共存。

## 2. 运行方式（待补：实现完成后填写实测命令与解释器版本）

- 后端：Python 3.14（CONVENTIONS §4.8，当前基线 3.14.6 已确认）
- 回测引擎：优先纯 pandas 窗口回测核心（框架无关）；vnpy 集成作为可选路径（§13 风险：vnpy 在 3.14 的安装待验证，不阻塞核心验证）

## 3. 操作剧本（待补：逐步操作 → 观察现象 → 对应研究结论）

## 4. 结论指向的决策记录（待写：demo 跑通后先写 `docs/decisions/0004-*.md`，再回写 brief-plan）

- 依据文献：W3 精读（BacktestBench / Look-Ahead-Bench / What survives honest evaluation?，见 `docs/literature/W3-backtest-reliability.md`——@research 产出中）
