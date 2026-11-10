#!/usr/bin/env python3.14
"""W4 审批/授权边界 Demo —— 交互入口。

用法：
    python3.14 demo.py            # 交互菜单
    python3.14 demo.py flow       # 步骤 1：审批闭环（归因 + use-time + 原子消费 + 通道隔离）
    python3.14 demo.py loopjack   # 步骤 2：Loopjacking A→B 替换攻击（负例双对照）
    python3.14 demo.py boundary   # 步骤 3：矩阵不可变 + 运行时撤销 + 消息不得改授权边界
    python3.14 demo.py budget     # 步骤 4：预算按 goal 整体计
    python3.14 demo.py monitor    # 步骤 5：确定性 monitor > 模型 judge
"""
from __future__ import annotations

import sys

from approval_gate import (
    ActionDenied, ApprovalChannel, AuthMatrix, DeterministicMonitor,
    GoalBudget, GroupBus, LlmJudge, RoleBoundaryError,
    action_digest, consume, consume_by_call_id_only,
)
from approval_gate.matrix import MatrixRegistry

STEP = "=" * 62


def step_flow() -> None:
    print(STEP, "\n[1/5] 审批闭环：归因 + use-time 比对 + 原子消费 + 通道隔离")
    ch = ApprovalChannel()
    args = {"symbol": "510300", "side": "buy", "qty": 100}
    t = ch.issue("call_1", "trade.execute", args, requested_by="researcher-A")
    print(f"  审批发出：{t.approval_id} tool={t.tool} requested_by={t.requested_by}")
    print(f"  agent 可见面：{ch.agent_visible()}")
    a = consume(ch, t, "call_1", "trade.execute", args)
    print(f"  ✓ use-time 消费成功：{a}（digest {t.args_digest[:12]}…）")
    try:
        consume(ch, t, "call_1", "trade.execute", args)
        print("  ✗ 重复消费未被拦")
    except ActionDenied as e:
        print(f"  ✓ 原子消费拦截：{e}")
    try:
        ch.issue("call_2", "trade.execute", args, requested_by="")
        print("  ✗ 无归因审批未被拦")
    except ActionDenied as e:
        print(f"  ✓ 归因强制：{e}")


def step_loopjack() -> None:
    print(STEP, "\n[2/5] Loopjacking A→B 替换攻击：digest 绑定 vs 只绑 call id")
    # 攻击设定：审批给的是 A 账户转账，执行时被替换成 B 账户
    approved = {"symbol": "510300", "side": "sell", "qty": 100, "account": "A"}
    swapped = {"symbol": "510300", "side": "sell", "qty": 100, "account": "B"}

    ch1 = ApprovalChannel()
    t1 = ch1.issue("call_9", "trade.execute", approved, requested_by="coder-B")
    try:
        consume(ch1, t1, "call_9", "trade.execute", swapped)
        print("  ✗ 替换攻击竟然放行")
    except ActionDenied as e:
        print(f"  ✓ digest 绑定拒绝：{e}")

    ch2 = ApprovalChannel()
    t2 = ch2.issue("call_9", "trade.execute", approved, requested_by="coder-B")
    got = consume_by_call_id_only(ch2, t2, "call_9")   # 负例对照（只绑 call id）
    print(f"  ⚠ 负例对照（弱绑定，仅 demo 用）：只核 call_id 即放行 {got}"
          f"——A→B 账户已被偷换！digest 差异 {action_digest('trade.execute', approved)[:8]}"
          f"≠{action_digest('trade.execute', swapped)[:8]}")
    print("  → 结论：material arguments digest 必须进审批绑定（W4 采纳①）")


def step_boundary() -> None:
    print(STEP, "\n[3/5] 授权边界：矩阵不可变 + 运行时撤销 + 消息不得改边界")
    reg = MatrixRegistry(AuthMatrix.v1())
    print(f"  矩阵 {reg.current.version}：coder×approval.decide → "
          f"{'allow' if reg.check('coder', 'approval.decide') else 'deny'}；"
          f"reviewer×approval.decide → "
          f"{'allow' if reg.check('reviewer', 'approval.decide') else 'deny'}")
    try:
        reg.current.try_mutate("coder", "approval.decide")
        print("  ✗ 矩阵被原地改了")
    except RoleBoundaryError as e:
        print(f"  ✓ {e}")
    bus = GroupBus(reg)
    delivered = bus.send("coder-B", "reviewer-C",
                         {"grant": "approval.decide", "to": "coder-B"})
    print(f"  ✓ 越权授权消息投递结果={delivered}（结构性忽略）；"
          f"矩阵仍 {reg.current.version}")
    v = reg.publish(AuthMatrix.v1_after_revocation())
    after = reg.check("coder", "backtest.run")
    print(f"  撤销发布 {v}：coder×backtest.run → "
          f"{'allow' if after else 'deny（撤销生效）'}；历史留档 {len(reg._history)} 版")
    print(f"  总线审计：{bus.audit[-1]}")


def step_budget() -> None:
    print(STEP, "\n[4/5] 预算按 goal 整体计（成员级只观测）")
    b = GoalBudget("goal-quant-1", cap_usd=1000.0)
    print(f"  A 消费 600 → 剩余 {b.charge('member-A', 600.0):.2f}")
    print(f"  B 消费 300 → 剩余 {b.charge('member-B', 300.0):.2f}")
    try:
        b.charge("member-B", 200.0)
        print("  ✗ 超限未拦")
    except Exception as e:
        print(f"  ✓ 超限拒绝（换了成员也拦）：{e}")
    print(f"  观测面板（只读，不分摊）：{b.observation()}")


def step_monitor() -> None:
    print(STEP, "\n[5/5] 模型之下强制：deterministic monitor 唯一防线，judge 仅辅助")
    judge = LlmJudge({"act-bad": True})          # judge 误放行（论文 0/40 教训）
    m = DeterministicMonitor(judge)
    v1 = m.enforce("act-bad", role_ok=False, approval_ok=True, budget_ok=True)
    print(f"  角色越权动作：allowed={v1.allowed}｜{v1.reason}｜{v1.judge_note}")
    v2 = m.enforce("act-ok", role_ok=True, approval_ok=True, budget_ok=True)
    print(f"  全规则通过：allowed={v2.allowed}｜{v2.reason}｜{v2.judge_note}")
    print("  → judge 说没问题也拦、judge 不参与 allowed 计算（W4 采纳④）")


STEPS = {"flow": step_flow, "loopjack": step_loopjack, "boundary": step_boundary,
         "budget": step_budget, "monitor": step_monitor}


def main(argv: list[str]) -> int:
    if len(argv) > 1:
        fn = STEPS.get(argv[1])
        if fn is None:
            print(__doc__)
            return 2
        fn()
        return 0
    print("W4 审批/授权边界 Demo —— 输入 1-5 执行步骤，q 退出")
    menu = {str(i): fn for i, fn in enumerate(STEPS.values(), start=1)}
    while True:
        choice = input("\n步骤 [1]审批闭环 [2]替换攻击 [3]授权边界 [4]预算 [5]monitor (q退出): ").strip().lower()
        if choice in ("q", "quit", "exit"):
            print("bye")
            return 0
        fn = menu.get(choice)
        if fn is None:
            print("无效输入")
            continue
        fn()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
