# W2 记忆蒸馏 demo：晋升 gate、记忆生命周期与 turn_context 组装

> 验证目标：SEPM/CALM/HaMo 三篇 2026-10 文献的「可计算晋升判据 + supersede 不删除 + gate 先于 packing」语义
> 结论指向：`docs/decisions/0003-w2-memory-distillation.md`（提议态）
> 前置阅读：[W2 文献笔记](../../docs/literature/W2-context-memory-distillation.md)

## 1. 验证目标（对应文献结论）

| # | 研究结论 | demo 里的可操作验证 |
|---|---|---|
| 1 | 晋升必须有**可计算判据**（SEPM reproduction gate + HaMo retrieval-coverage），不靠 LLM 拍板 | 逐卡点「评估」，看两个 gate 的逐项 ✓/✗ 与拦截原因 |
| 2 | **gate 先于 packing**（CALM：16KB 预算协议，挤出≠拒绝） | 关/开 gate、调预算，观察 included / evicted / excluded 三桶 |
| 3 | **supersede 不删除**（CALM 生命周期状态机） | 点「supersede」，旧卡 SUPERSEDED + 指针，行仍可查 |
| 4 | **TTL 是第二触发通道**（金融域改造采纳） | TTL 卡激活后到期，点「TTL 扫描」→ STALE，不删除 |
| 5 | **消融：无 gate 则污染进上下文**（SEPM 消融复现） | 两个 gate 全关 → 污染卡放行 → turn_context 被稀释 |
| 6 | 群组记忆分层 `scope`（§12.2 W2 落点，字段级） | 卡带 scope/author_agent_id，API 往返验证 |

## 2. 运行方式

环境（CONVENTIONS §4 规则 8）：

- **Python 3.14.6**（实测：`Python 3.14.6 | sqlite 3.53.2`，纯标准库零依赖）
- Node 24 / Expo 58（React Native 0.88 + react-native-web，**无 Electron**，规则 7）

```bash
# ① 后端（默认 http://127.0.0.1:8777，首次启动自动预置 3 张经验卡）
python3 server.py

# ② 前端（另开终端；web 直接在浏览器看，也可 expo start 用 iOS 模拟器/Expo Go）
cd frontend && npm install && npx expo start --web

# ③ 定点测试（12 个，纯标准库）
python3 -m unittest test_w2 -v
```

> 若不想装前端，纯后端也能跑完整剧本：`curl` 调 `GET /api/state`、`POST /api/evaluate/<id>` 等（见 `server.py` 路由表）。

## 3. 操作剧本（怎么操作 → 看到什么 → 对应哪条结论）

预置三张卡：**A 好卡**（复现2/效用0.42/因果0.81/cov0.65）、**B 污染卡**（复现0/效用-0.35/因果0.12/cov0.08）、**C TTL卡**（15 秒过期）。初始全部 CANDIDATE，不进上下文。

| 步骤 | 操作 | 现象 | 对应结论 |
|---|---|---|---|
| 1 | 看「④ turn_context」 | 3 张卡全在**硬过滤**桶（CANDIDATE 不进上下文），included=0 | 结论 2：gate 先于 packing，未过 gate 的记忆分数再高也不注入 |
| 2 | 对 A 点「评估」 | 两个 gate 全 ✓ → A 变 **ACTIVE**，出现在 included | 结论 1：可计算判据放行 |
| 3 | 对 B 点「评估」 | coverage 与 reproduction **双双 ✗**，逐项列出实际值 vs 阈值 → B 仍是 CANDIDATE | 结论 1：拦截原因可审计，不是黑盒 |
| 4 | 再对 A 点一次「评估」 | 复现≥2 且 gate 通过 → A 升 **STABLE**，分数加成 | 结论 1+3：生命周期迁移由确定性规则维护 |
| 5 | **把①里两个 gate 全关**，再对 B 点「评估」 | B **放行** 变 ACTIVE 并进入 included——上下文被污染卡稀释 | 结论 5：论文消融的直觉复现（SEPM：memory 无 gate 几乎无效） |
| 6 | 把 gate 全开回来；点「③ supersede 第1张→第3张」 | 旧卡 **SUPERSEDED** + `superseded_by` 指针，**行仍可查**（上方卡片列表还在） | 结论 3：历史回放需要旧记忆重构当时决策 |
| 7 | 对 C（TTL 卡）点「评估」激活，等 15 秒后点「触发 TTL 扫描」 | C → **STALE**，行保留、退出 included | 结论 4：TTL 是独立于生命周期的第二触发通道 |
| 8 | 在④把预算改成 `60` 点「按预算重组」 | 高分卡留在 included，低分卡进 **evicted**，标注「预算挤出（≠拒绝：留持久层，可再检索）」 | 结论 2：挤出≠拒绝 |
| 9 | 用⑤「放一张污染卡」+「创建」自建卡，再回②评估 | 自建卡从 CANDIDATE 起步，判据输入（复现/效用/因果/cov/TTL）直接决定命运 | 结论 1：判据是输入而非模型心情 |
| 10 | 看「⑥ 事件日志」 | 每一步迁移都有 kind+detail 审计记录（gate_passed / gate_blocked / superseded / ttl_expired…） | goal_event 风格：状态变迁可回放 |

## 4. 关键实现点

- `memstore.py`：sqlite 记忆库 + CALM 裁剪后的生命周期状态机（CANDIDATE/ACTIVE/STABLE/SUPERSEDED/STALE/ARCHIVED）+ **合法迁移白名单**（非法迁移抛 `InvalidTransition`）+ 事件审计表。
- `gate.py`：SEPM reproduction gate（≥1 复现 + 效用≥0 + 因果≥0.65）+ HaMo coverage 前置（≥0.30），两个 gate 均可独立开关（开关=论文消融开关）。
- `context.py`：固定顺序组装——硬过滤 → 准入打分（0.5·效用 + 0.3·coverage + STABLE 加成 0.2 + TTL 剩余度衰减）→ 贪心装箱 → 挤出留持久层。token 为无分词器粗估（CJK≈1/字，其余≈0.25），README 声明仅 demo 口径。
- `server.py`：标准库 `ThreadingHTTPServer` JSON API，CORS 放开供 Expo web 连接。
- `test_w2.py`：12 个定点测试——gate 拦截/消融/阈值边界、CANDIDATE 不进上下文、supersede 保行+指针、TTL→STALE 不删除、非法迁移拒绝、预算挤出、STABLE 加成、scope 往返。

## 5. 已知简化（与生产设计的差距）

- token 估算非真实分词器；16KB 协议的**顺序与语义**是验证对象，绝对数值不是。
- CALM 的 learned gate 未做，按文献笔记 §5 用免判据（CALM-ZS 思路）起步。
- 群组记忆只落字段级（scope/author_agent_id），共享/私有注入策略在 W3 群组记忆 demo 里做交互版。
- AWM 式 workflow 归纳未进本 demo：文献笔记 §5 的迁移性风险项需要真实 T1 轨迹，留待有回测数据后单独 spike。

## 6. 环境实测记录

| 项 | 值 |
|---|---|
| Python | 3.14.6（Anaconda build，Clang 20.1.8） |
| sqlite | 3.53.2 |
| 后端依赖 | 零（纯标准库） |
| Node / npm | 24.16.0 / 11.13.0 |
| Expo / React Native | 58.0.22 / 0.88.1（react-native-web 打包 193 modules 通过） |
| 定点测试 | 12 passed（`python3 -m unittest test_w2`） |
| 操作剧本 | 第 1–8 步已在真实后端逐条验证（2026-11-01） |
