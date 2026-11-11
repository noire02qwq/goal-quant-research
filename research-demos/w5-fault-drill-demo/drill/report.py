"""排名稳定性（W5 笔记 §3.1-C 修正②③→0006 实测行）：两档执行假设下
策略排名的 Kendall τ_b——「仅固定窗口不够，成交假设不披露则排序本身不稳」
（Execution Assumptions→Sharpe 排序）的可执行度量。

档位口径（简化合并）：滑点/冲击并入 cost_rate，两档差即执行假设敏感性。
"""
from __future__ import annotations

import math
from itertools import combinations

# A：低摩擦（3bp 佣金、无滑点）；B：保守摩擦（3bp 佣金 + 22bp 滑点/冲击）
EXEC_TIERS = {
    "A 低摩擦(3bp)": 0.0003,
    "B 保守摩擦(25bp)": 0.0025,
}


def kendall_tau_b(x: list[float], y: list[float]) -> float:
    """Kendall τ_b（双侧同分修正）：排序稳定性 ∈ [-1, 1]，分母 0 → nan。"""
    if len(x) != len(y):
        raise ValueError("长度不一致")
    con = dis = tie_x = tie_y = 0
    for i, j in combinations(range(len(x)), 2):
        dx = (x[i] > x[j]) - (x[i] < x[j])
        dy = (y[i] > y[j]) - (y[i] < y[j])
        if dx == 0 and dy == 0:
            continue
        if dx == 0:
            tie_x += 1
        elif dy == 0:
            tie_y += 1
        elif dx * dy > 0:
            con += 1
        else:
            dis += 1
    denom = math.sqrt((con + dis + tie_x) * (con + dis + tie_y))
    if denom == 0:
        return float("nan")
    return (con - dis) / denom


def tier_table(bars, roster: list[tuple[str, object]]) -> dict[str, dict[str, float]]:
    """每个执行假设档下跑全套策略 → {tier: {name: total_return}}。"""
    from drill.bridge import run_template
    table: dict[str, dict[str, float]] = {}
    for tier, cost in EXEC_TIERS.items():
        table[tier] = {
            name: run_template(strat, bars, cost_rate=cost)["total_return"]
            for name, strat in roster
        }
    return table


def stability(table: dict[str, dict[str, float]]) -> tuple[list[str], list[float], list[float], float]:
    """两档间 τ_b：返回 (策略序, A 序分, B 序分, τ_b)。"""
    (t1, s1), (t2, s2) = list(table.items())
    names = list(s1)
    x = [s1[n] for n in names]
    y = [s2[n] for n in names]
    return names, x, y, kendall_tau_b(x, y)
