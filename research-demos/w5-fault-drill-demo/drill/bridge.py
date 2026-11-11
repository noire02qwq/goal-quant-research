"""桥接 w3-lookahead-proof-demo 的 lookahead_guard：窗口回测 + 指标库单入口复用。

跨 demo 复用经路径注入显式完成（两仓同库、均为公开仓资产），w5 自身零回测实现。
"""
from __future__ import annotations

import sys
from pathlib import Path

W3_DIR = Path(__file__).resolve().parent.parent.parent / "w3-lookahead-proof-demo"
if str(W3_DIR) not in sys.path:
    sys.path.insert(0, str(W3_DIR))

from lookahead_guard import Bar, MarketFeed                      # noqa: E402
from lookahead_guard.backtest import run_backtest                # noqa: E402
from lookahead_guard import metrics                              # noqa: E402


def feed_from_tuples(bars: list[tuple]) -> MarketFeed:
    """(o,h,l,c) → w3 Bar（固定窗口夹具直接喂给窗口回测）。"""
    return MarketFeed([Bar(i, o, h, l, c, 1_000_000.0)
                       for i, (o, h, l, c) in enumerate(bars)])


def run_template(strategy, bars: list[tuple], cost_rate: float = 0.0003) -> dict:
    """用 w3 的构造性防护回测跑一个策略模板，返回指标报告。

    cost_rate 即执行假设档位（佣金+滑点合并口径，见 report.EXEC_TIERS）。
    """
    res = run_backtest(feed_from_tuples(bars), strategy, cost_rate=cost_rate)
    return dict(res.report)
