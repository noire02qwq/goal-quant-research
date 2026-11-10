# W4 审批/授权边界与群组治理 Demo（草稿）

> 状态：草稿（脚手架已建，实现中）｜ 周主题：W4 审批/人在回路与授权边界（brief-plan §12.1 W4）｜ 群组挂靠：§12.2 W4 群组治理

## 1. 验证目标（对应 brief-plan 设计问题）

1. **审批归因**（§12.2 W4 ①）：审批门记录 `requested_by`（哪个成员发起）；**群组成员不得绕过审批门互相授权**——demo 注入"成员 A 经消息让成员 B 代批"的绕过尝试，断言被拒并留审计记录。
2. **授权矩阵按"角色×工具"**（§12.2 W4 ③）：researcher/coder/reviewer × 工具集的静态矩阵；为 W8 反方评审预留 reviewer 角色位。运行时权限撤销（OpenDots 100ms watcher 同向，§3 走读结论）至少演示一次生效。
3. **消息不得修改授权边界**（§12.2 W4 ① + OpenDots 教训）：群组消息通道只能传业务内容，注入"授予某工具权限"类消息被结构性忽略。
4. **预算按 goal 整体计**（§12.2 W4 ②）：成员级 token 用量只做观测字段，不参与分摊决策。

## 2. 运行方式（待补：实现完成后填写实测命令与解释器版本）

- 后端：Python 3.14（CONVENTIONS §4.8）
- 形态：进程内审批门 + 群组消息总线的最小可交互实现（不依赖 harness-hub——集成开发按 @user 2026-11-10 指令搁置）

## 3. 操作剧本（待补：逐步操作 → 观察现象 → 对应研究结论）

## 4. 结论指向的决策记录（待写：demo 跑通后先写 `docs/decisions/0005-*.md`，再回写 brief-plan）

- 依据文献：[docs/literature/W4-hitl-approval-authorization.md](../../docs/literature/W4-hitl-approval-authorization.md)（4 精读，commit `58f9c2a`）；demo 落点以笔记 §4 采纳①–④为准（use-time 绑定原子消费 / 审批通道独立于 agent / 矩阵不可变上限 / 模型之下强制+委派记录权威）
