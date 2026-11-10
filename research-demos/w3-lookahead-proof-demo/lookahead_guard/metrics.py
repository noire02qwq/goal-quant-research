"""指标库：收益/夏普/回撤统一由此计算，策略侧只产出仓位序列。

对应 brief-plan §12.1 W3 方向③（BacktestBench：不让模型自己写指标公式）。
"""
from __future__ import annotations

import math


def total_return(equity: list[float]) -> float:
    if not equity or equity[0] == 0:
        raise ValueError("权益曲线为空或首值为 0")
    return equity[-1] / equity[0] - 1.0


def sharpe(equity: list[float], periods_per_year: int = 252,
           risk_free: float = 0.0) -> float:
    """基于权益曲线逐期收益率的年化夏普（无交易费假设，demo 口径）。"""
    rets = [equity[i] / equity[i - 1] - 1.0 for i in range(1, len(equity))
            if equity[i - 1] != 0]
    if len(rets) < 2:
        raise ValueError("收益样本不足")
    mean = sum(rets) / len(rets)
    var = sum((r - mean) ** 2 for r in rets) / (len(rets) - 1)
    sd = math.sqrt(var)
    if sd == 0:
        raise ValueError("波动为 0，夏普无定义")
    return (mean - risk_free / periods_per_year) / sd * math.sqrt(periods_per_year)


def max_drawdown(equity: list[float]) -> float:
    """最大回撤（负数，如 -0.12 表示 12%）。"""
    peak, mdd = equity[0], 0.0
    for v in equity:
        peak = max(peak, v)
        mdd = min(mdd, v / peak - 1.0)
    return mdd


def report(equity: list[float]) -> dict:
    """汇报口径固定三仪器齐算（W3 笔记采纳②：账本单入口）。"""
    return {
        "total_return": round(total_return(equity), 6),
        "sharpe": round(sharpe(equity), 4),
        "max_drawdown": round(max_drawdown(equity), 6),
        "bars": len(equity),
    }
