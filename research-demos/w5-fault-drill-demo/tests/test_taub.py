"""τ_b 定点测试：已知值对拍（0004/0005 模式：数值可独立复算）。"""
from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from drill.report import EXEC_TIERS, kendall_tau_b, stability, tier_table
from drill import fixture


class TestKendallTauB(unittest.TestCase):
    def test_identical_order(self):
        self.assertAlmostEqual(kendall_tau_b([1, 2, 3], [10, 20, 30]), 1.0)

    def test_reversed_order(self):
        self.assertAlmostEqual(kendall_tau_b([1, 2, 3], [30, 20, 10]), -1.0)

    def test_known_partial(self):
        # 3 对中 2 同 1 异 → (2-1)/3 = 1/3
        self.assertAlmostEqual(kendall_tau_b([1, 2, 3], [1, 3, 2]), 1.0 / 3.0)

    def test_tie_correction(self):
        # x 单侧同分：C=0 D=2 tie_x=1 → -2/sqrt(6)
        self.assertAlmostEqual(kendall_tau_b([1, 1, 2], [3, 2, 1]),
                               -2 / math.sqrt(6))

    def test_degenerate_nan(self):
        self.assertTrue(math.isnan(kendall_tau_b([1, 1, 1], [5, 6, 7])))

    def test_length_mismatch(self):
        with self.assertRaises(ValueError):
            kendall_tau_b([1], [1, 2])


class TestTierRanking(unittest.TestCase):
    def test_two_tiers_full_roster(self):
        bars = fixture.make_bars()
        roster = [("T3Grid", fixture.T3Grid()), ("T4Turtle", fixture.T4Turtle())]
        table = tier_table(bars, roster)
        self.assertEqual(list(table), list(EXEC_TIERS))
        for scores in table.values():
            self.assertEqual(set(scores), {"T3Grid", "T4Turtle"})
        names, x, y, tau = stability(table)
        self.assertEqual(names, ["T3Grid", "T4Turtle"])
        self.assertTrue(-1.0 <= tau <= 1.0)

    def test_deterministic(self):
        bars = fixture.make_bars()
        roster = [("T3Grid", fixture.T3Grid()), ("T4Turtle", fixture.T4Turtle())]
        self.assertEqual(stability(tier_table(bars, roster)),
                         stability(tier_table(bars, roster)))


if __name__ == "__main__":
    unittest.main()
