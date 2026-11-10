# W3 前视偏差构造性不可能 Demo

> 状态：**可运行（2026-11-10 实测）**｜ 周主题：W3 LLM 生成量化回测代码的可靠性、前视偏差（brief-plan §12.1 W3）｜ 群组挂靠：§12.2 W3 任务分解（assigned_role opt-in）

## 1. 验证目标（对应 brief-plan 设计问题）

1. **前视偏差在接口层构造性不可能**（§12.1 W3 方向①）：策略唯一数据入口 `WindowedView` 把一切读取钳制在 `[0, t]`，越界即抛 `LookaheadViolation`——正常路径下拿不到未来数据，不靠提示词、不靠事后 lint。参照 W3 文献笔记采纳①（MintEval「bar 回调前入 buffer、越界抛错」）。
2. **第二道防线前视 lint**（§12.1 W3 方向②）：绕过视图直读原始源的策略，由**动态审计**（access_log 中 index > step 即定罪，带 file:line）+ **静态扫描**（策略源文件禁用模式行号级命中）双层捕获。
3. **指标统一计算，不让模型自己写公式**（§12.1 W3 方向③，BacktestBench 结论）：收益/夏普/回撤全部走 `lookahead_guard/metrics.py`，策略只产出 0/1 仓位序列；汇报三仪器齐算（W3 笔记采纳②"账本单入口"）。
4. **群组任务分解 opt-in**（§12.2 W3）：任务 `assigned_role` 可选——不填即单角色路径零改动，填了则角色不匹配的认领被拒；两条路径在同一函数里共存。

## 2. 运行方式（2026-11-10 实测）

- 实测环境：**Python 3.14.6**（CONVENTIONS §4.8 基线 3.14.6；sqlite 3.53.2，本 demo 不用数据库）、**零第三方依赖**（纯标准库）
- 后端取舍：核心为**框架无关的窗口回测**（pandas/vnpy 均非必需）——对应 §13 风险行「vnpy 在 3.14 的安装待验证」，不阻塞本 demo 的验证目标；vnpy 集成留作后续可选路径
- 定点测试（demo 目录内）：

```bash
python3.14 -m unittest discover -s tests -v   # 实测 12/12 OK
```

- 交互入口 / 分步命令（demo 目录内）：

```bash
python3.14 demo.py            # 交互菜单（可实际操作入口）
python3.14 demo.py clean      # 步骤 1：干净回测
python3.14 demo.py leak       # 步骤 2：越界拒绝
python3.14 demo.py bypass     # 步骤 3：双 lint 定罪
python3.14 demo.py roles      # 步骤 4：assigned_role 双路径
```

## 3. 操作剧本（实测输出，2026-11-10）

**步骤 1 `clean`——干净回测双 lint 全绿**
- 输入：`python3.14 demo.py clean`
- 现象：`{'total_return': 1.238231, 'sharpe': 5.0515, 'max_drawdown': -0.1027, 'bars': 300}`；access_log 6390 条中 index≤step 违例 **0** 条；动态 0 发现 / 静态 0 发现 → **全绿 PASS**
- 对应结论：接口层构造性保证下策略吃到了埋藏行情（+123.8%）且全程零越界——行为等价验收（W3 笔记采纳③）成立

**步骤 2 `leak`——走合法接口读未来也被拒绝**
- 输入：`python3.14 demo.py leak`
- 现象：`✓ LookaheadViolation：bar 1 超出可见地平线 t=0（未来数据被接口层拒绝）`；对照的**泄露预言机**（仅测量侧，不给策略）假想收益 **536.10%**
- 对应结论：这就是被接口层挡掉的诱惑量级——防护在接口层构造性成立（W3 采纳①），统计修正不能替代

**步骤 3 `bypass`——绕过视图直读原始源，双 lint 定罪**
- 输入：`python3.14 demo.py bypass`
- 现象：**动态审计 299 发现**（如 `bypass_strategy.py:20：step=0 时读取了未来 bar 1`）+ **静态扫描 7 发现**（持有原始源、`raw_close` 直读，行号级）→ **双层均捕获 PASS**
- 对应结论：API 拦截正常路径、lint 捕获绕过路径，两道防线互不替代（W3 采纳①的第二道防线，方向②）

**步骤 4 `roles`——assigned_role 填与不填双路径**
- 输入：`python3.14 demo.py roles`
- 现象：无约束任务 coder/reviewer 均可领（单角色路径零改动）；`约束 'reviewer'` 的任务被 coder 认领 → `✓ 拒绝`；reviewer 认领成功
- 对应结论：§12.2 W3「群组是 opt-in、默认路径零改动」成立

## 4. 结论指向的决策记录

- **待写**：demo 跑通后先写 `docs/decisions/0004-*.md`，按 CONVENTIONS §3.6「先决策、后设计修订」再回写 brief-plan（落点以 W3 笔记 §4 采纳①–⑤为准：前视三层防护 / 账本单入口三仪器齐算 / 行为等价验收 / 实测知识边界窗口 / 门禁合取+预算化）
- 依据文献：[docs/literature/W3-backtest-reliability.md](../../docs/literature/W3-backtest-reliability.md)（7 精读 + 1 摘要级，commit `58f9c2a`）；对应 PDF 见 [docs/papers/README.md](../../docs/papers/README.md) 索引
