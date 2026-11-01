"""W2 记忆蒸馏 demo 定点测试（纯标准库 unittest）。

覆盖三条研究结论的可失败断言：
1. 晋升 gate 可计算、可拦截、可消融（关掉 gate → 污染卡放行）；
2. supersede 不删除 + TTL 第二触发通道；
3. turn_context：gate 先于 packing、挤出≠拒绝、硬过滤正确。
"""
from __future__ import annotations

import time
import unittest

import context as ctx
import gate
import memstore
from memstore import InvalidTransition


def make_store() -> memstore.MemoryStore:
    return memstore.MemoryStore(":memory:")


class GateTest(unittest.TestCase):
    def test_good_card_passes(self):
        c = dict(reproduction_count=2, avg_utility=0.4, causal_consistency=0.8, retrieval_coverage=0.6)
        self.assertTrue(gate.evaluate(c)["pass"])

    def test_polluted_card_blocked_with_reasons(self):
        c = dict(reproduction_count=0, avg_utility=-0.3, causal_consistency=0.1, retrieval_coverage=0.05)
        res = gate.evaluate(c)
        self.assertFalse(res["pass"])
        blocked = [x for x in res["checks"] if not x["pass"]]
        self.assertEqual(len(blocked), 2)  # 两个 gate 都拦

    def test_ablation_gate_off_polluted_card_passes(self):
        """关掉 reproduction gate = 论文消融：污染卡放行，模拟上下文被稀释的根源。"""
        c = dict(reproduction_count=0, avg_utility=-0.3, causal_consistency=0.1, retrieval_coverage=0.6)
        self.assertTrue(gate.evaluate(c, gates={"reproduction": False})["pass"])

    def test_causal_threshold_boundary(self):
        c = dict(reproduction_count=1, avg_utility=0.0, causal_consistency=0.649, retrieval_coverage=0.5)
        self.assertFalse(gate.evaluate(c, gates={"coverage": False})["pass"])
        c["causal_consistency"] = 0.65
        self.assertTrue(gate.evaluate(c, gates={"coverage": False})["pass"])


class LifecycleTest(unittest.TestCase):
    def _cid(self, s, **kw):
        return s.add_card(goal="g", initial_conditions="i", strategy_outline="o", **kw)

    def test_candidate_not_in_context_until_gate(self):
        s = make_store()
        cid = self._cid(s)
        out = ctx.assemble(s.list_cards())
        self.assertEqual(out["included"], [])
        self.assertEqual(out["excluded"][0]["lifecycle"], "CANDIDATE")
        s.transition(cid, "ACTIVE", "gate_passed", "t")
        self.assertEqual(len(ctx.assemble(s.list_cards())["included"]), 1)

    def test_supersede_keeps_row_and_pointer(self):
        s = make_store()
        old = self._cid(s, reproduction_count=2, avg_utility=0.4, causal_consistency=0.8, retrieval_coverage=0.6)
        new = self._cid(s, reproduction_count=2, avg_utility=0.5, causal_consistency=0.9, retrieval_coverage=0.7)
        s.transition(old, "ACTIVE", "gate_passed", "t")
        s.transition(new, "ACTIVE", "gate_passed", "t")
        s.supersede(old, new)
        row = s.get_card(old)
        self.assertIsNotNone(row, "supersede 不得物理删除")
        assert row is not None
        self.assertEqual(row["lifecycle"], "SUPERSEDED")
        self.assertEqual(row["superseded_by"], new)
        out = ctx.assemble(s.list_cards())
        self.assertNotIn(old, [x["card_id"] for x in out["included"]])
        self.assertNotIn(old, [x["card_id"] for x in out["evicted"]])

    def test_ttl_expiry_marks_stale_not_deleted(self):
        now = [1000.0]
        s = memstore.MemoryStore(":memory:", now=lambda: now[0])
        cid = s.add_card(goal="g", initial_conditions="i", strategy_outline="o",
                         valid_in_seconds=10, reproduction_count=1,
                         avg_utility=0.3, causal_consistency=0.7, retrieval_coverage=0.5)
        s.transition(cid, "ACTIVE", "gate_passed", "t")
        self.assertEqual(s.expire_due(), [], "未到期不应命中")
        now[0] += 11
        self.assertEqual(s.expire_due(), [cid])
        self.assertEqual(s.get_card(cid)["lifecycle"], "STALE")
        self.assertIsNotNone(s.get_card(cid), "STALE 不得物理删除")
        self.assertEqual(ctx.assemble(s.list_cards())["included"], [])

    def test_illegal_transition_rejected(self):
        s = make_store()
        cid = self._cid(s)
        with self.assertRaises(InvalidTransition):
            s.transition(cid, "STABLE", "x", "CANDIDATE 不能直接 STABLE")


class ContextTest(unittest.TestCase):
    def _card(self, cid, lifecycle, util, cov, repro=1, causal=0.7, valid=None):
        return dict(card_id=cid, goal="g", initial_conditions="i", strategy_outline="o",
                    lifecycle=lifecycle, avg_utility=util, retrieval_coverage=cov,
                    reproduction_count=repro, causal_consistency=causal, valid_until=valid)

    def test_budget_eviction_keeps_retrievable(self):
        cards = [self._card(f"c{i}", "ACTIVE", 0.5, 0.5) for i in range(5)]
        out = ctx.assemble(cards, budget=60)  # 只装得下少量
        self.assertGreater(len(out["evicted"]), 0)
        self.assertIn("≠拒绝", out["evicted"][0]["reason"])
        self.assertLessEqual(out["used_tokens"], 60)

    def test_stable_scores_higher_than_active(self):
        a = self._card("a", "ACTIVE", 0.5, 0.5)
        b = self._card("b", "STABLE", 0.5, 0.5)
        self.assertGreater(ctx.score(b), ctx.score(a))

    def test_gate_before_packing_order(self):
        """CANDIDATE 即便分数再高也不进上下文——gate 先于 packing。"""
        junk = self._card("hi", "CANDIDATE", 1.0, 1.0)
        good = self._card("lo", "ACTIVE", 0.1, 0.1)
        out = ctx.assemble([junk, good])
        self.assertEqual([x["card_id"] for x in out["included"]], ["lo"])


class GroupScopeTest(unittest.TestCase):
    def test_scope_field_roundtrip(self):
        s = make_store()
        cid = s.add_card(goal="g", initial_conditions="i", strategy_outline="o",
                         scope="private", author_agent_id="coder")
        got = s.get_card(cid)
        self.assertIsNotNone(got)
        row = dict(got)
        self.assertEqual(row["scope"], "private")
        self.assertEqual(row["author_agent_id"], "coder")


if __name__ == "__main__":
    unittest.main(verbosity=2)
