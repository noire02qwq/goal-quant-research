# 0005：W4 审批/授权边界——use-time 审批绑定定稿与授权治理口径（分层验证状态）

> 状态：已采纳（@research 双轮核验通过，2026-11-10：采纳①–④逐子项与 W4 笔记 §3 口径比对一致 + 实测回抽 16/16、5 步剧本逐项复现、`f7052ae` 后代码零改动（git diff 空）、27/40 回抽原文命中）｜ 日期：2026-11-10 ｜ 作者：@dev ｜ 核验：@research 2026-11-10 ｜ 关联：[literature/W4](../literature/W4-hitl-approval-authorization.md)（4 精读，采纳①–④）／[w4-approval-gate-demo](../../research-demos/w4-approval-gate-demo/README.md)（16/16 测试实测）／ brief-plan §5.5、§4.4、§12.1 W4、§12.2 W4

## 背景

W4 周主题「审批/人在回路与授权边界」的文献结论已由 W4 笔记定稿为采纳①–④（Loopjacking / I-HITL / From Approval to Abuse / Permitted but Unauthorized 四篇实证）。本决策记录把 **w4-approval-gate-demo 的实测证据**与四条采纳对齐。采纳③④为复合条目，demo 只覆盖部分——按 @research 2026-11-10 独立复跑后的口径**逐子项标注验证状态**，未覆盖项明确落点，防"研究方向"被读成"已实证"。

## 决策

1. **审批门 use-time 绑定 + 原子消费 + 归因**（W4 采纳①）——**已验证**：消费时重建完整操作、比对 material arguments digest、票据单次原子消费、`requested_by` 归因缺失即拒；负例复刻 Loopjacking A→B 替换攻击——只绑 call id 的弱绑定对照放行（账户被偷换），digest 绑定必拒。落点 §5.5 审批门与 §4.4 `goal_receipt`（canonical record 至少绑定 action/tool identity + material arguments + principal/scope + nonce/expiry/consumption，与 0002 原子认领/fencing 同族）。**字段面说明**：demo 票据以 `approval_id + consumed` 位承载最小等价，scope/nonce/expiry 完整字段随 §5.5 平台实现（harness 搁置中）。
2. **审批通道独立于 agent**（W4 采纳②）——**最小验证形态已验证**：审批令牌存放于 agent 不可读的独立命名空间（agent 可见面 `can_list_tickets: False`、零令牌数据）；对应 I-HITL 教训（9/10 frontier 模型自行读取 OTP）。**平台侧完整实现**（审批信号不放邮箱/同机文件/环境变量、金融动作独立通道）随 harness 解除搁置落地——本 demo 不声称覆盖。
3. **授权矩阵：不可变上限 ✓ + 提议来源约束 未验证**（W4 采纳③，**拆两半**）：
   - **immutable ceiling 已验证**：矩阵 frozen，原地改唯一结局 `RoleBoundaryError`；撤销=版本化整表替换（`v1 → v1-revoked`）、旧版留档、撤销后检查立拒；群组消息携带授权字段被总线结构性忽略（`BOUNDARY-TAMPER` 审计、矩阵零变化）。
   - **allow-rule 提议来源约束未覆盖**：提议不得源自不可信上下文、须绑 goal scope 与过期（From Approval to Abuse：条件于规则获批 47/58=81.0% 静默达成、blast radius 56.9%）——**标未验证**，落点 §12.2 W4「agent 不得经 harness 自扩权」规则 + 平台侧实现。
4. **授权治理"模型之下强制 + 委派记录权威"**（W4 采纳④，**四个子项覆盖 1.5 个**）：
   - ① **runtime deterministic monitor ✓ 已验证**：硬规则唯一防线——judge 误放行时照拦，且测试断言 judge 结果翻转 `allowed` 不变（零耦合是测出来的，`test_judge_not_part_of_decision`）；
   - ② **versioned delegation record = 部分/最小验证**：demo 的矩阵版本化是最小形态；与论文「ownership 取自 versioned delegation record（按资源委派、不从资源名推断）」**不是同一物**——按资源的委派记录留平台侧；
   - ③ **peer 动作不入候选动作空间：未验证**（可见性开关，0/52 那条）——留群组扩展/W8；
   - ④ **self-report effect 校验：未验证**（残余 severity misreport）——留群组扩展/W8。
5. **不采纳（进本记录）**：小模型 pre-execution judge 作**唯一**防线——demo 步骤 5 反证（judge 说"合规"照样拦）；权威必须是 deterministic monitor，judge 仅辅助信号。
6. **预算按 goal 整体计**（§12.2 W4 ②）——**已验证**：跨成员合计对 goal 上限、超限整笔拒绝（换成员也拦）、成员级用量只读观测不分摊。

## 实测数据（2026-11-10，Python 3.14.6，纯标准库零依赖）

| 项 | 实测 |
|---|---|
| 定点测试 | `python3.14 -m unittest discover -s tests -v` → **16/16 OK** |
| 步骤 1 审批闭环 | 归因 `requested_by=researcher-A` ✓；use-time 消费成功（digest `ac208a5bec53…`）；重复消费原子拦截；空归因拒发；agent 可见面 `can_list_tickets: False` |
| 步骤 2 替换攻击 | digest 绑定拒绝（`379a39a053ea… ≠ 900b2fe83bb0…`）；弱绑定负例对照放行——A→B 账户被偷换（证伪"只绑 call id"） |
| 步骤 3 授权边界 | `coder×approval.decide → deny / reviewer → allow`；原地改矩阵抛错；越权消息 `投递=False` + `BOUNDARY-TAMPER` 审计 + 矩阵 v1 不变；`v1-revoked` 发布后 `coder×backtest.run → deny`、历史 2 版 |
| 步骤 4 预算 | A600+B300 后 B 再 200 → 拒（`按 goal 整体计，与成员无关`）；观测面板只读 |
| 步骤 5 monitor | 角色越权 + judge 误放行 → `allowed=False｜硬规则拦截：角色授权`；judge 翻转 `allowed` 不变（测试断言） |
| 独立复跑 | @research 本机 16/16 + 5 步逐项复现，与 README 自述一致（2026-11-10） |

## 理由

- **绑定不足=攻击面**：Loopjacking 多框架实证（只绑 call id / run 级 approved 标志 / 展示时检查都不够）——demo 用弱绑定对照把"不够"变成可复现的放行证据。
- **审批信号与 agent 隔离**：I-HITL 实测 9/10 模型自行读 OTP，隔离是构造性要求而非提示词要求——demo 验证命名空间隔离的最小形态。
- **强制必须在模型之下**：deterministic reference monitor 使越界 0/40（无防御 27/40）；judge 臂仍现 severity misreport——judge 零耦合写进测试而非仅写进文档。
- **不可变上限先于读不可信内容**：81% 静默达成的实证说明"审批疲劳"真实存在，上限须在 harness 层构造，不可依赖每次审批。

## 备选方案（不采纳的）

| 备选 | 不采纳理由 |
|---|---|
| 只绑 call id / run 级 approved 标志 | Loopjacking 实证全严格阳性；demo 弱绑定对照复现 A→B 放行 |
| 审批令牌放 agent 可读资源（邮箱/文件/环境变量） | I-HITL：9/10 frontier 模型自行读取 OTP 提额 |
| 小模型 pre-execution judge 作唯一防线 | judge 臂 severity misreport 致 peer 错过 deadline；W4 笔记不采纳项，demo 步骤 5 反证 |
| 矩阵原地可改（运行时热改不走版本） | 失去不可变上限语义：越权修改无失败出口、不可审计；撤销必须走版本发布 |
| 预算按成员分摊 | 成员间博弈与单位不一致（§12.2 W4 ②既有结论，demo 复证超限必须按 goal 判） |

## 对设计文档的修订

- brief-plan.md §5.5（审批门 use-time 绑定字段与独立通道）、§4.4（`goal_receipt` 绑定语义）、§12.1 W4 行（demo 证据回填）、§12.2 W4 行（immutable ceiling 实证 + 提议来源约束/子项③④状态标注）：**是否已更新：否**——按 CONVENTIONS §3.6，本记录转"已采纳"后由 @dev 定点修订并留痕。

## 后续动作

- [x] @research 双轮核验：0005 vs W4 笔记 §3 采纳①–④逐子项口径 + demo 实测回抽（2026-11-10 通过：③拆两半与④四子项 1.5 覆盖的标注与笔记逐子项一致；数字 47/58=81.0%/56.9%/9/10/0/40/27/40 全部回抽命中；一处非阻塞提醒——笔记采纳②的「金融动作批准方必须是人」请在 §5.5 修订留痕中带上，勿因 demo 最小形态而丢失）
- [ ] 核验通过转"已采纳"后，brief-plan §5.5/§4.4/§12.1 W4/§12.2 W4 定点修订留痕（@dev）
- [ ] allow-rule 提议来源约束（不可信上下文、绑 goal scope 与过期）平台侧实现（harness 解除搁置后，@dev）
- [ ] 按资源的 versioned delegation record、peer 动作可见性开关、self-report effect 校验——留群组扩展/W8 合并推进（@dev/@research 随 W8 定）
