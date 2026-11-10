"""定点测试：审批 use-time 绑定/原子消费、矩阵不可变与撤销、总线边界守卫、
goal 级预算、确定性 monitor 优先于 judge。

运行（demo 目录内）：python3.14 -m unittest discover -s tests -v
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from approval_gate import (                       # noqa: E402
    ActionDenied, ApprovalChannel, AuthMatrix, BudgetExceeded,
    DeterministicMonitor, GoalBudget, GroupBus, LlmJudge, RoleBoundaryError,
    consume, consume_by_call_id_only,
)
from approval_gate.matrix import MatrixRegistry   # noqa: E402

ARGS = {"symbol": "510300", "side": "buy", "qty": 100}


class TestApprovalGate(unittest.TestCase):
    def test_issue_requires_attribution(self):
        ch = ApprovalChannel()
        with self.assertRaises(ActionDenied):
            ch.issue("c1", "t", ARGS, requested_by="")

    def test_use_time_roundtrip_then_atomic_second_consume(self):
        ch = ApprovalChannel()
        t = ch.issue("c1", "trade.execute", ARGS, requested_by="researcher-A")
        self.assertEqual(consume(ch, t, "c1", "trade.execute", ARGS), t.approval_id)
        with self.assertRaises(ActionDenied):
            consume(ch, t, "c1", "trade.execute", ARGS)      # 原子：单次有效

    def test_loopjack_arg_swap_rejected(self):
        ch = ApprovalChannel()
        approved = dict(ARGS, account="A")
        swapped = dict(ARGS, account="B")
        t = ch.issue("c9", "trade.execute", approved, requested_by="coder-B")
        with self.assertRaises(ActionDenied) as cm:
            consume(ch, t, "c9", "trade.execute", swapped)
        self.assertIn("digest 失配", str(cm.exception))

    def test_weak_callid_only_binding_allows_attack(self):
        """负例对照：只绑 call id 会放行 A→B——记录"为什么必须 digest"。"""
        ch = ApprovalChannel()
        t = ch.issue("c9", "trade.execute", dict(ARGS, account="A"),
                     requested_by="coder-B")
        got = consume_by_call_id_only(ch, t, "c9")
        self.assertEqual(got, t.approval_id)      # 弱绑定放行（demo 对照用途）

    def test_call_id_mismatch_rejected(self):
        ch = ApprovalChannel()
        t = ch.issue("c1", "trade.execute", ARGS, requested_by="x")
        with self.assertRaises(ActionDenied):
            consume(ch, t, "other-call", "trade.execute", ARGS)

    def test_channel_isolated_from_agent_namespace(self):
        ch = ApprovalChannel()
        ch.issue("c1", "trade.execute", ARGS, requested_by="x")
        visible = ch.agent_visible()
        self.assertFalse(visible["can_list_tickets"])
        self.assertNotIn("appr_1", repr(visible))         # agent 可见面无令牌


class TestMatrix(unittest.TestCase):
    def test_reviewer_gate_coder_denied(self):
        reg = MatrixRegistry(AuthMatrix.v1())
        self.assertTrue(reg.check("reviewer", "approval.decide"))
        self.assertFalse(reg.check("coder", "approval.decide"))

    def test_matrix_immutable(self):
        with self.assertRaises(RoleBoundaryError):
            AuthMatrix.v1().try_mutate("coder", "approval.decide")

    def test_runtime_revocation_by_version_swap(self):
        reg = MatrixRegistry(AuthMatrix.v1())
        self.assertTrue(reg.check("coder", "backtest.run"))
        reg.publish(AuthMatrix.v1_after_revocation())
        self.assertFalse(reg.check("coder", "backtest.run"))
        self.assertEqual(len(reg._history), 2)            # 旧版留档

    def test_bus_blocks_authorization_payload(self):
        reg = MatrixRegistry(AuthMatrix.v1())
        bus = GroupBus(reg)
        before = reg.current.version
        self.assertFalse(bus.send("coder-B", "reviewer-C",
                                  {"grant": "approval.decide", "to": "coder-B"}))
        self.assertEqual(reg.current.version, before)     # 矩阵零变化
        self.assertIn("BOUNDARY-TAMPER", bus.audit[-1])
        # 普通业务消息不受影响
        self.assertTrue(bus.send("coder-B", "reviewer-C", {"task": "review PR 42"}))


class TestBudget(unittest.TestCase):
    def test_goal_level_cap_across_members(self):
        b = GoalBudget("g1", cap_usd=1000)
        b.charge("A", 600)
        b.charge("B", 300)
        self.assertEqual(b.remaining, 100)

    def test_cap_enforced_regardless_of_member(self):
        b = GoalBudget("g1", cap_usd=1000)
        b.charge("A", 600)
        b.charge("B", 300)
        with self.assertRaises(BudgetExceeded) as cm:
            b.charge("B", 200)                          # 换成员照样拦
        self.assertIn("按 goal 整体计", str(cm.exception))

    def test_observation_is_readonly_view(self):
        b = GoalBudget("g1", cap_usd=1000)
        b.charge("A", 100)
        panel = b.observation()
        self.assertEqual(panel["total"], 100)
        self.assertIn("by_member", panel)


class TestMonitor(unittest.TestCase):
    def test_deny_wins_over_judge_ok(self):
        judge = LlmJudge({"bad": True})                 # judge 误放行
        m = DeterministicMonitor(judge)
        v = m.enforce("bad", role_ok=False, approval_ok=True, budget_ok=True)
        self.assertFalse(v.allowed)
        self.assertIn("角色授权", v.reason)
        self.assertIn("judge", v.judge_note)

    def test_allow_when_all_rules_pass(self):
        m = DeterministicMonitor()
        v = m.enforce("ok", role_ok=True, approval_ok=True, budget_ok=True)
        self.assertTrue(v.allowed)

    def test_judge_not_part_of_decision(self):
        """judge 结果翻转，allowed 不变（judge 不参与判定）。"""
        m1 = DeterministicMonitor(LlmJudge({"x": True}))
        m2 = DeterministicMonitor(LlmJudge({"x": False}))
        args = dict(role_ok=False, approval_ok=True, budget_ok=True)
        self.assertEqual(m1.enforce("x", **args).allowed,
                         m2.enforce("x", **args).allowed)


if __name__ == "__main__":
    unittest.main()
