"""定点测试：前视构造性保证 + 双 lint + 指标库 + assigned_role 路径。

运行（demo 目录内）：python3.14 -m unittest discover -s tests -v
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import market                                    # noqa: E402
import roles                                      # noqa: E402
import strategies                                 # noqa: E402
from bypass_strategy import BypassRaw             # noqa: E402
from lookahead_guard import (                     # noqa: E402
    LookaheadViolation, WindowedView, dynamic_audit, static_scan,
)
from lookahead_guard import metrics               # noqa: E402
from lookahead_guard.backtest import oracle_equity, run_backtest  # noqa: E402


class TestWindowedView(unittest.TestCase):
    def test_future_read_raises(self):
        feed = market.make_feed(50)
        view = WindowedView(10, feed)
        with self.assertRaises(LookaheadViolation):
            view.close(11)

    def test_window_upper_bound_is_t(self):
        feed = market.make_feed(50)
        view = WindowedView(10, feed)
        w = view.window(100)                      # 请求 100 根，只有 11 根可给
        self.assertEqual(len(w), 11)              # 上界恰为 t，未来给不了
        raw = [feed.raw_close(i) for i in range(11)]
        self.assertEqual(w, raw)

    def test_window_length_short(self):
        feed = market.make_feed(50)
        view = WindowedView(10, feed)
        self.assertEqual(len(view.window(5)), 5)


class TestBacktestGuards(unittest.TestCase):
    def test_clean_run_full_audit_green(self):
        feed = market.make_feed()
        res = run_backtest(feed, strategies.DualMA())
        self.assertEqual(len(res.equity), len(feed))
        self.assertEqual(dynamic_audit(feed), [])
        self.assertEqual(static_scan(ROOT / "strategies.py"), [])
        self.assertIn("sharpe", res.report)

    def test_peek_blocked(self):
        feed = market.make_feed(60)
        with self.assertRaises(LookaheadViolation):
            run_backtest(feed, strategies.PeekViaView())

    def test_bypass_caught_by_both_lints(self):
        feed = market.make_feed()
        run_backtest(feed, BypassRaw(feed))
        dyn = dynamic_audit(feed)
        self.assertGreater(len(dyn), 0, "动态审计漏检")
        self.assertTrue(all("bypass_strategy" in f.where for f in dyn),
                        [f.where for f in dyn])
        sta = static_scan(ROOT / "bypass_strategy.py")
        self.assertGreater(len(sta), 0, "静态扫描漏检")
        self.assertTrue(any("raw_close" in f.detail for f in sta))

    def test_oracle_not_lint_target(self):
        feed = market.make_feed(60)
        oracle_equity(feed)
        self.assertEqual(dynamic_audit(feed), [])   # 测量侧豁免（harness-only）


class TestMetrics(unittest.TestCase):
    def test_known_values(self):
        eq = [100.0, 110.0, 99.0]
        self.assertAlmostEqual(metrics.total_return(eq), -0.01)
        self.assertAlmostEqual(metrics.max_drawdown(eq), 99.0 / 110.0 - 1.0)

    def test_sharpe_positive_for_uptrend(self):
        eq = [100.0, 101.0, 100.5, 102.0, 103.5, 103.0, 105.0]
        self.assertGreater(metrics.sharpe(eq), 0)

    def test_report_three_instruments(self):
        feed = market.make_feed()
        res = run_backtest(feed, strategies.DualMA())
        self.assertTrue({"total_return", "sharpe", "max_drawdown"} <= set(res.report))


class TestRoles(unittest.TestCase):
    def test_default_path_unconstrained(self):
        t = roles.PlanTask("T-1", "x")
        self.assertIn("OK", roles.claim(t, "coder"))
        self.assertIn("OK", roles.claim(t, "reviewer"))

    def test_constrained_mismatch_rejected(self):
        t = roles.PlanTask("T-2", "y", "reviewer")
        with self.assertRaises(roles.RoleBoundaryError):
            roles.claim(t, "coder")
        self.assertIn("OK", roles.claim(t, "reviewer"))


if __name__ == "__main__":
    unittest.main()
