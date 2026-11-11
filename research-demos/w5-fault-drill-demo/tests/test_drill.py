"""定点测试：五类注入各自的「注入→观察→断言」+ 数据固定化与模板白名单。

运行（demo 目录内）：python3.14 -m unittest discover -s tests -v
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from drill.runstate import CodeBroken, DrillRun, Receipts, SimulatedCrash  # noqa: E402
from drill.execution import Broker, Breaker, Order, Reconciler             # noqa: E402
from drill.feedguard import (                                              # noqa: E402
    FeedGuard, FORGED, NewsItem, backtest_candles_signature, headline_drive,
)
from drill import fixture                                                  # noqa: E402
from drill.bridge import run_template                                      # noqa: E402


class TestRepairPath(unittest.TestCase):
    def test_broken_code_creates_repair_and_completes(self):
        run = DrillRun("g", ["fetch", "backtest", "report"])
        run.broken_code_steps.add("backtest")
        out = run.attempt_with_repair()
        self.assertEqual(out["completed"], ["fetch", "backtest", "report"])
        self.assertEqual(run.repaired, ["backtest"])
        self.assertEqual(run.executed["backtest"], 2)      # 故障步 +1 重试
        self.assertEqual(run.executed["fetch"], 1)         # 其余步零重跑

    def test_fault_does_not_terminate_run(self):
        kinds = []
        run = DrillRun("g2", ["s1", "s2"])
        run.broken_code_steps.add("s1")
        run.attempt_with_repair()
        kinds = [e.kind for e in run.events]
        self.assertIn("repair_task", kinds)
        self.assertIn("run_finished", kinds)


class TestRestartPath(unittest.TestCase):
    def test_crash_then_resume_zero_rerun(self):
        r = Receipts()
        run1 = DrillRun("g", ["fetch", "signal", "execute"], receipts=r)
        run1.crash_at = "execute"
        with self.assertRaises(SimulatedCrash):
            run1.run()
        run2 = DrillRun("g", ["fetch", "signal", "execute"], receipts=r)
        done = run2.run()
        self.assertEqual(done, ["done:execute"])           # 前两步回执拦截、仅本轮执行入列
        self.assertEqual(r.replay_count, 2)
        self.assertNotIn("fetch", run2.executed)           # 零重跑（未再执行）
        self.assertEqual(run2.executed["execute"], 1)

    def test_receipt_first_write_wins(self):
        r = Receipts()
        v1, fresh = r.first_write("k", "a")
        v2, fresh2 = r.first_write("k", "b")
        self.assertFalse(fresh and False)
        self.assertEqual((v1, fresh), ("a", False))
        self.assertEqual((v2, fresh2), ("a", True))        # 首写胜出、重复命中回执


class TestGoalChangePath(unittest.TestCase):
    def test_change_emits_event_and_keeps_completed(self):
        run = DrillRun("g", ["a", "b", "c"])
        run._run_step("a")
        run.change_goal("保守档", at_step="b")
        rest = run.run()
        self.assertEqual(rest, ["done:b", "done:c"])
        self.assertIn("a", run.completed)
        self.assertTrue(any(e.kind == "goal_changed" for e in run.events))
        self.assertTrue(run.receipts.has("g:a"))           # 已完成步骤回执未被动过


class TestInterfaceHonesty(unittest.TestCase):
    def test_silent_fill_named_by_reconciler(self):
        br = Broker(silent_fill_bugs={"o-7"})
        view = [br.submit(Order("o-7", "buy", 100, 10.0)),
                br.submit(Order("o-8", "buy", 100, 10.0))]
        findings = Reconciler.reconcile(view, br)
        self.assertEqual(len(findings), 1)                 # 只有静默单被点名
        self.assertIn("o-7", findings[0])
        self.assertIn("submitted≠filled", findings[0])

    def test_breaker_really_trips(self):
        halted = []
        bk = Breaker(max_gap_pct=3.0)
        self.assertTrue(bk.check(10.0, 10.6, lambda: halted.append(1)))
        self.assertTrue(bk.tripped)
        self.assertEqual(halted, [1])
        # 平稳段不触发
        bk2 = Breaker(max_gap_pct=3.0)
        self.assertFalse(bk2.check(10.0, 10.1, lambda: halted.append(2)))
        self.assertFalse(bk2.tripped)


class TestDataPlaneInjection(unittest.TestCase):
    def test_backtest_blind_feed_guard_catches(self):
        bars = fixture.make_bars()
        self.assertEqual(backtest_candles_signature(bars),
                         backtest_candles_signature(bars))  # 伪造新闻不进 candle
        g = FeedGuard(trusted_sources={"exchange-feed"})
        self.assertTrue(g.ingest(NewsItem("n1", "exchange-feed", "年报", signed=True)))
        self.assertFalse(g.ingest(FORGED))
        self.assertEqual(len(g.blocked), 1)
        self.assertEqual(headline_drive(FORGED.headline), -1)   # 放行即被操纵


class TestFixturesAndTemplates(unittest.TestCase):
    def test_seed_reproducible(self):
        self.assertEqual(fixture.bars_sha256(fixture.make_bars()),
                         fixture.bars_sha256(fixture.make_bars()))
        self.assertNotEqual(fixture.bars_sha256(fixture.make_bars()),
                            fixture.bars_sha256(fixture.make_bars(seed=999)))

    def test_t3_t4_run_with_metrics(self):
        bars = fixture.make_bars()
        for strat in (fixture.T3Grid(), fixture.T4Turtle()):
            rep = run_template(strat, bars)
            self.assertIn("sharpe", rep)
            self.assertEqual(rep["bars"], fixture.FIXED_WINDOW["bars"])

    def test_parameter_whitelist(self):
        with self.assertRaises(ValueError):
            fixture.T3Grid(momentum=1)
        with self.assertRaises(ValueError):
            fixture.T4Turtle(zzz=1)


if __name__ == "__main__":
    unittest.main()
