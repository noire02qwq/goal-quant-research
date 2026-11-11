"""演示数据固定化（§12.0 W5 研究项）：固定窗口 + 固定 seed，两次生成哈希一致。

同时承载 T3 网格 / T4 经典海龟两个策略模板（brief-plan §9，参数白名单形态），
回测执行复用 w3-lookahead-proof-demo 的 lookahead_guard（窗口回测 + 指标库单入口）。
"""
from __future__ import annotations

import hashlib
import random

# 固定窗口（演示口径：固定起止 + seed，防现场翻车——§12.1 W5 方向①）
FIXED_WINDOW = {"start": "2025-01-02", "end": "2025-06-30", "seed": 20261111, "bars": 120}


def make_bars(n: int = FIXED_WINDOW["bars"], seed: int = FIXED_WINDOW["seed"]) -> list[tuple]:
    """确定性合成日线（open, high, low, close)。同 seed 两次生成逐字节一致。"""
    rng = random.Random(seed)
    out: list[tuple] = []
    px = 100.0
    for i in range(n):
        drift = 0.15 * ((i // 25) - 2)          # 两段温和趋势 + 震荡
        px = max(5.0, px + rng.gauss(drift, 1.2))
        o = px * 0.999
        c = px
        h = max(o, c) * 1.003
        lo = min(o, c) * 0.997
        out.append((round(o, 4), round(h, 4), round(lo, 4), round(c, 4)))
    return out


def bars_sha256(bars: list[tuple]) -> str:
    return hashlib.sha256(repr(bars).encode("utf-8")).hexdigest()


class T3Grid:
    """T3 网格策略模板：区间内固定步长网格，触下沿持多、触上沿空仓（0/1 形态）。"""

    parameters = {"lower": 90.0, "upper": 115.0, "step": 5.0}     # 白名单
    variables: dict = {}

    def __init__(self, **kw):
        unknown = set(kw) - set(self.parameters)
        if unknown:
            raise ValueError(f"参数白名单外：{sorted(unknown)}")
        self.parameters.update(kw)

    def on_bar(self, view, position: int) -> int:
        px = view.close(view.now)
        if px <= self.parameters["lower"]:
            return 1                              # 触下沿买入网格
        if px >= self.parameters["upper"]:
            return 0                              # 触上沿出网格
        return position


class T4Turtle:
    """T4 经典海龟：Donchian N 期突破入场、跌回中轨离场（简化教学形）。"""

    parameters = {"entry_n": 20, "exit_n": 10}
    variables: dict = {}

    def __init__(self, **kw):
        unknown = set(kw) - set(self.parameters)
        if unknown:
            raise ValueError(f"参数白名单外：{sorted(unknown)}")
        self.parameters.update(kw)

    def on_bar(self, view, position: int) -> int:
        n = self.parameters["entry_n"]
        closes = view.window(n + 1)
        if len(closes) < n + 1:
            return position
        hi = max(closes[:-1])
        lo = min(closes[-(self.parameters["exit_n"] + 1):-1])
        px = closes[-1]
        if px >= hi:
            return 1                              # 突破 N 期高点入场
        if position and px <= lo:
            return 0                              # 跌破 exit_n 期低点离场
        return position
