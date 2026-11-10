# W4 审批/授权边界与群组治理 Demo

> 状态：**可运行（2026-11-10 实测）**｜ 周主题：W4 审批/人在回路与授权边界（brief-plan §12.1 W4）｜ 群组挂靠：§12.2 W4 群组治理

## 1. 验证目标（对应 brief-plan / W4 笔记采纳①–④）

1. **审批 use-time 绑定 + 原子消费 + 归因**（§12.2 W4 ①，W4 采纳①）：消费时**重建完整操作并比对 material arguments digest**，票据单次原子消费；`requested_by` 归因缺失即拒。负例复刻 **Loopjacking A→B 替换攻击**：只绑 call id 的弱绑定对照会放行（账户被偷换），digest 绑定必拒。
2. **审批通道独立于 agent**（W4 采纳②的最小验证形态）：审批令牌存放于 agent 不可读的独立命名空间，agent 可见面只有请求入口回执——平台侧完整实现照旧随 harness 解除搁置。
3. **角色×工具矩阵：不可变 + 运行时撤销 + 消息不得改边界**（§12.2 W4 ①③）：矩阵 frozen 不可原地改（越权修改唯一结局是抛错）；撤销=发布新版本整表替换、旧版留档、撤销后检查立拒；群组消息携带授权字段（grant/role/…）被总线**结构性忽略**并留 `BOUNDARY-TAMPER` 审计，矩阵零变化。reviewer 角色位预留给 W8 反方评审（A3）。
4. **预算按 goal 整体计**（§12.2 W4 ②）：跨成员合计对 goal 上限，超限整笔拒绝（换成员也拦）；成员级用量只读观测、不分摊。
5. **模型之下强制**（W4 采纳④）：deterministic monitor 是唯一防线——judge 误放行时硬规则照拦，且 judge 结果翻转不影响 `allowed`（判定零耦合）；LLM judge 只作辅助信号（论文实测 0/40 教训，笔记不采纳项）。

## 2. 运行方式（2026-11-10 实测）

- 实测环境：**Python 3.14.6**（CONVENTIONS §4.8）、**零第三方依赖**（纯标准库）；不依赖 harness-hub（集成按 @user 2026-11-10 指令搁置）
- 定点测试（demo 目录内）：

```bash
python3.14 -m unittest discover -s tests -v   # 实测 16/16 OK
```

- 交互入口 / 分步命令（demo 目录内）：

```bash
python3.14 demo.py            # 交互菜单（可实际操作入口）
python3.14 demo.py flow       # 步骤 1：审批闭环
python3.14 demo.py loopjack   # 步骤 2：替换攻击双对照
python3.14 demo.py boundary   # 步骤 3：授权边界三连
python3.14 demo.py budget     # 步骤 4：goal 级预算
python3.14 demo.py monitor    # 步骤 5：确定性 monitor
```

## 3. 操作剧本（实测输出，2026-11-10）

**步骤 1 `flow`——审批闭环**
- 现象：审批发出 `appr_1 requested_by=researcher-A`；agent 可见面 `{'can_list_tickets': False, 'note': '审批令牌不在 agent 可读命名空间（通道独立）'}`；use-time 消费成功（digest `ac208a5bec53…`）；**重复消费被原子拦截**（`审批已消费（单次有效）`）；**空归因被拒**（`审批归因缺失：requested_by 为空`）
- 对应结论：归因强制 ✓、通道独立最小验证 ✓（W4 采纳②）

**步骤 2 `loopjack`——A→B 替换攻击双对照**
- 现象：digest 绑定**拒绝**（`审批时 379a39a053ea… 执行时 900b2fe83bb0…（替换攻击被拒）`）；负例弱绑定对照（仅 demo 用）**放行**——`只核 call_id 即放行 appr_1——A→B 账户已被偷换！`
- 对应结论：material arguments digest 必须进审批绑定（W4 采纳①）；只绑 call id 的方案被对照证伪

**步骤 3 `boundary`——授权边界三连**
- 现象：`coder×approval.decide → deny；reviewer×approval.decide → allow`；原地改矩阵 → `✓ 授权矩阵不可变…不得原地加入`；越权授权消息 `投递结果=False`、矩阵仍 v1、审计 `BOUNDARY-TAMPER blocked…`；撤销发布 `v1-revoked` 后 `coder×backtest.run → deny`、历史留档 2 版
- 对应结论：矩阵不可变上限 ✓、运行时撤销 ✓、消息不得修改授权边界 ✓（§12.2 W4 ①③）

**步骤 4 `budget`——goal 整体计**
- 现象：A 600 → 剩 400；B 300 → 剩 100；B 再 200 → `✓ 超限拒绝（换了成员也拦）：合计 900+200 > 上限 1000（按 goal 整体计，与成员无关）`；观测面板只读（`by_member` 分列仅展示）
- 对应结论：预算按 goal 计、成员级只观测（§12.2 W4 ②）

**步骤 5 `monitor`——确定性强制**
- 现象：角色越权动作 `allowed=False｜硬规则拦截：角色授权｜judge: 操作看起来合规`（judge 误放行照样拦）；全规则通过时 `allowed=True` 且标注 `（辅助信号，不参与判定）`
- 对应结论：模型之下 deterministic monitor 唯一防线，judge 仅辅助（W4 采纳④）

## 4. 结论指向的决策记录

- **待写**：demo 跑通后先写 `docs/decisions/0005-*.md`（提议 → @research 双轮核验 W4 笔记采纳①–④口径 + 实测回抽 → 转已采纳 → brief-plan §5.5/§4.4/§12.1 W4/§12.2 W4 定点修订）
- 依据文献：[docs/literature/W4-hitl-approval-authorization.md](../../docs/literature/W4-hitl-approval-authorization.md)（4 精读，commit `58f9c2a`）；demo 落点以笔记 §4 采纳①–④为准（use-time 绑定原子消费 / 审批通道独立于 agent / 矩阵不可变上限 / 模型之下强制+委派记录权威）
