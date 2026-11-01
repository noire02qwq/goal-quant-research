# 0003：W2 记忆蒸馏语义——可计算晋升 gate + 生命周期 supersede 不删除 + gate 先于 packing

> 状态：已采纳 ｜ 日期：2026-11-01 ｜ 作者：@dev ｜ 关联：[W2 文献笔记](../literature/W2-context-memory-distillation.md)、[w2-memory-distillation-demo](../../research-demos/w2-memory-distillation-demo/README.md)、brief-plan §5.4 / §12.1 W2 行 / §12.2 W2 群组记忆子题

## 背景

W2 文献精读（2026-10 四篇新工作）把记忆蒸馏的两个未决问题钉死了：经验→技能的**晋升判据**（SEPM 的 reproduction gate、HaMo 的 retrieval-coverage）和记忆的**生命周期治理**（CALM 的状态机 + supersede 不删除）。既有设计 §5.4 只写了"Run 收尾蒸馏 + top-k 召回"，没有回答"什么样的经验有资格进上下文"和"过时记忆怎么退出"。W2 demo 用最小实现把三篇论文的核心语义跑通并交互化，验证这些语义在金融策略场景可操作。

## 决策

1. **晋升必须可计算，不靠 LLM 拍板**：双 gate 组合——前置 HaMo retrieval-coverage（≥0.30）+ 主 gate SEPM reproduction（≥1 次复现 trial、平均效用≥0、因果一致性≥0.65）。任一不过即拦截，拦截原因逐项落 `goal_event` 审计（规则名 + 实际值 vs 阈值）。
2. **gate 先于 packing（16KB 协议）**：turn_context 组装固定四步——硬过滤（只放行 ACTIVE/STABLE）→ 准入打分（0.5·效用 + 0.3·coverage + STABLE 加成 0.2 + TTL 剩余度衰减）→ 按分贪心装箱 → **挤出者留持久层可再检索**（挤出≠拒绝）。未过 gate 的记忆分数再高也不注入。
3. **生命周期状态机沿 CALM 裁剪**：`CANDIDATE → ACTIVE → STABLE → SUPERSEDED / STALE → ARCHIVED`，迁移走**确定性白名单**（非法迁移直接拒绝），不靠 LLM 重写全文。
4. **supersede 不删除**：替代关系置 `SUPERSEDED` + `superseded_by` 指针，行永久可读——历史回放（W10 可复现）需要旧记忆重构当时决策。
5. **TTL 是第二触发通道**（金融域改造采纳）：显式 `valid_until` 到期 → `STALE`，独立于生命周期迁移；行情/持仓类事实不适用"时间流逝不致 stale"，须显式有效期。
6. **群组记忆分层落字段级**（§12.2 W2）：`scope`（shared/private）+ `author_agent_id` 先入库，注入策略（共享全量 + 私有按角色选择性注入）留 W3 群组 demo 做交互版。
7. **demo 形态遵循 CONVENTIONS §4 规则 6/7/8**：可交互操作剧本（README 十步）、React Native/Expo 前端无 Electron、Python 3.14.6 纯标准库后端。

## 实测数据（如适用）

环境：macOS 26.6.2，Python 3.14.6（Anaconda build）+ sqlite 3.53.2，Node 24.16.0 + Expo 58.0.22 / React Native 0.88.1。窗口：2026-11-01。

| 验证项 | 结果 |
|---|---|
| 定点 unittest | **12 passed**（gate 拦截/消融/阈值边界、CANDIDATE 不进上下文、supersede 保行+指针、TTL→STALE 不删除、非法迁移拒绝、预算挤出、STABLE 加成、scope 往返） |
| gate 全开 + 污染卡评估 | 拦截，coverage 与 reproduction 双 ✗，逐项原因可审计 |
| 全消融（两 gate 关）+ 污染卡评估 | **放行** → ACTIVE → 进入 turn_context（复现 SEPM"无 gate 则污染稀释"直觉） |
| 好卡两次评估 | CANDIDATE → ACTIVE → STABLE（复现≥2 且 gate 通过） |
| TTL 卡激活后 15s 扫描 | → STALE，行保留，退出 included |
| supersede | 旧卡 SUPERSEDED + 指针，行仍可查，上下文排除 |
| 预算 40 tok | 装箱溢出 → evicted 标注「预算挤出（≠拒绝：留持久层，可再检索）」 |
| Expo web 打包 | 193 modules，bundle 415KB，构建通过 |
| 后端启动 | `[w2-demo] Python 3.14.6 \| sqlite 3.53.2 \| http://127.0.0.1:8777`，预置 3 张卡 |

## 理由

- **可计算判据**：SEPM 消融显示 OfficeBench 上 memory 单独几乎无效（+0.33），有 alignment/晋升才有兑现；HaMo 的 retrieval-coverage 给了"值得沉淀"的统计口径。demo 实测：判据是显式输入（复现/效用/因果/cov），同输入必同结果，可审计可回归。
- **gate 先于 packing**：CALM 512-token 预算下 39.2 vs 基线 29.6，且消融去 Stage II（lifecycle 治理）掉 4.0pp。demo 把顺序固化成代码路径，`ContextTest.test_gate_before_packing_order` 是可失败断言。
- **不删除**：CALM 污染注入 50% 时对照掉 16.8–18.8pp 而 CALM 只掉 7.0pp；且 W10 可复现要求旧记忆可读。demo 实测 supersede 后行仍在。
- **TTL 第二通道**：金融域"时间流逝不致 stale"是文献结论在本域的必要改造（W2 笔记 §3 改造采纳项）。
- **零依赖后端 + RN 前端**：规则 7/8 要求；标准库 `ThreadingHTTPServer` 足够，避免依赖供应链进公开仓库。

## 备选方案（不采纳的）

| 备选 | 不采纳理由 |
|---|---|
| LLM 主导记忆取舍（自由文本摘要 + 模型判断） | 不可审计、不可回归；SEPM 实测显式结构换文本 SOP 掉 17.16pp |
| AWM 式 workflow 归纳作本 demo 主体 | 迁移性风险未测（W2 笔记 §5），需真实 T1 轨迹；AWM 已降为机制参考，另起 spike |
| ELECTRON 前端 | 违反 CONVENTIONS §4 规则 7（用户 2026-11-01 规定） |
| CALM learned gate（dev 集监督） | 文献笔记 §5：泛化未证，第一版用免训练判据起步 |
| supersede 时物理删除/覆盖旧行 | 破坏历史回放；CALM 原文即 supersede 不删 |

## 对设计文档的修订

- brief-plan.md §5.4 记忆蒸馏：主候选升级为 SEPM+CALM 双主线 + HaMo 格式，落三 gate/生命周期/16KB 顺序语义（是否已更新：**是，2026-11-01 PR**）
- brief-plan.md §12.2 W2 群组记忆：scope 三元组 + 准入 gate 语义，随 §5.4 一起修订（是否已更新：**是，同上 PR**）
- brief-plan.md §5.1 有界摘要协议：补"gate 先于 packing、挤出≠拒绝"（是否已更新：**是，同上 PR**）
- brief-plan.md §4.4 `goal_memory_digest` 字段：增 lifecycle/valid_until/superseded_by/scope/author_agent_id（是否已更新：**是，同上 PR**）

## 文献复核结论（@research，2026-11-01）

对七条决策逐条对照 [literature/W2](../literature/W2-context-memory-distillation.md) 精读结果，并回抽原始 PDF 核验引用数值：

1. **可计算晋升判据 —— 文献支撑确认，一处参数出处校准**。SEPM 原文（[2610.14515](https://arxiv.org/abs/2610.14515)，App. B）确证：causal-confidence 阈值默认 0.65、最小复现次数 1、trial 平均效用 ≥0，三项判据与本记录一致。**校准**：coverage 前置的 `≥0.30` 是 demo 自设阈值——HaMo 原文（[2610.34724](https://arxiv.org/abs/2610.34724)）的机制是互补边际覆盖贪心选择直到边际增益为零 + knee point 定预算，并无 0.30 这一固定阈值；机制方向（retrieval-coverage 作"值得沉淀"判据）忠实，数值属本项目实例化参数，实现可调。
2. **gate 先于 packing —— 文献支撑确认**。CALM 512-token 预算下 39.2 vs 29.6 已回原文核对无误；demo 把顺序固化为可失败断言（`test_gate_before_packing_order`），与笔记 §3 采纳项一致。
3. **生命周期白名单 —— 与 CALM 状态机一致**（CANDIDATE→ACTIVE→STABLE→SUPERSEDED/STALE→ARCHIVED），非法迁移拒绝属确定性规则维护，符合"不靠 LLM 重写全文"的采纳理由。
4. **supersede 不删 —— 文献支撑确认**。回原文核对污染鲁棒性：0→50% 注入 CALM 仅掉 7.0pp（对照 11.6/16.8pp）；笔记 §5 已记录的"正文 vs 表 13 数值不一致"风险保留，本记录引用取正文口径。
5. **TTL 第二触发通道 —— 金融域改造采纳项**，笔记 §3 已载，非论文原文结论，标注正确。
6. **scope 字段级落库 —— 与 §12.2 W2 落点一致**，注入策略完整版留 W3，与笔记"共享全量+私有按角色注入"的落点不冲突。
7. **AWM 降级与 spike 拆分 —— 与笔记 §3/§5 一致**：迁移性风险（需真实 T1 轨迹）原样保留，未被 demo 结论掩盖；CALM learned gate 不采纳亦与笔记 §5 泛化未证的判断一致。

**简化项备查**（demo 层面，不阻塞采纳）：demo 的 reproduction gate 只实现三判据，未含 SEPM 原文同批的 safety/state-verification 两道 gate——金融域可由回测/数据校验承担 state 验证，safety gate 留平台侧设计时补，届时在 brief-plan §5.4 修订中注明。

独立复核（本机实跑，非转述 @dev 结果）：`python3 -m unittest test_w2` 12/12 通过；gate 三态冒烟（全开拦截污染卡且逐项可审计 / 全关放行 / 好卡通过）与 README 操作剧本第 1–8 步结论一致；前端 package.json 无 electron 依赖；后端 `python3 --version` = 3.14.6 与 §4 规则 8 基线一致。

**结论：七条决策与 W2 文献精读无实质冲突，转「已采纳」**；唯一校准项（coverage 0.30 为实例化参数）不改决策本身，随 brief-plan 修订时注明即可。

## 后续动作

- [x] @research 复核 W2 文献精读与本记录的一致性，合入后转「已采纳」（@research，2026-11-01）
- [x] @dev 走 PR 修订 brief-plan §5.1/§5.4/§12.2（带留痕；注意补 coverage 阈值为实例化参数的说明）（2026-11-01，连带 §4.4 字段与 safety/state gate 简化项注明）
- [ ] AWM workflow 归纳迁移性 spike：等 T1 回测轨迹数据（W3+，依赖回测链路）
- [ ] W3 群组记忆 demo：共享/私有注入策略交互版（scope 字段本 demo 已备）
