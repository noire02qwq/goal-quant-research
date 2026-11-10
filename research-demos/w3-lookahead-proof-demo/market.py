"""合成行情：确定性数据 + 两段"埋藏行情"（150–199 强升、220–249 回落），
让干净策略与预言机的收益差异可复现、可解释。
"""
from __future__ import annotations

import math

from lookahead_guard import Bar, MarketFeed


def make_feed(n: int = 300, seed_trend: bool = True) -> MarketFeed:
    def tri(t: int, start: int, peak: int, end: int, amp: float) -> float:
        """三角包络：start 起坡 → peak 到顶/底 → end 归零（连续，无跳空断崖）。"""
        if t < start or t >= end:
            return 0.0
        if t <= peak:
            return amp * (t - start) / (peak - start)
        return amp * (end - t) / (end - peak)

    bars: list[Bar] = []
    for t in range(n):
        base = 100.0 + 8.0 * math.sin(2 * math.pi * t / 40)
        drift = 0.0
        if seed_trend:
            drift += tri(t, 150, 190, 230, 64.0)    # 埋藏：单边强升后回落
            drift += tri(t, 245, 275, 305, -45.0)   # 埋藏：二次回撤（尾段未完全收复）
        close = base + drift
        open_ = close * 0.999
        high = max(open_, close) * 1.002
        low = min(open_, close) * 0.998
        bars.append(Bar(t, round(open_, 4), round(high, 4),
                        round(low, 4), round(close, 4), 1_000_000.0))
    return MarketFeed(bars)
