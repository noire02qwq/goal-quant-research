"""回测主循环：每步先推进可见地平线，再回调策略；执行价为当根收盘。

因果合规复核（W3 笔记采纳③的必要条件，非语义等价）：策略在干净
路径上看到的每一条数据都满足 index ≤ t，循环结束由 access_log 全量
复核；ActionMatch 式逐 bar 语义比对留 W6 验收路径，本 demo 不声称。
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .data import Bar, MarketFeed, WindowedView
from . import metrics as _m   # 指标只经此单入口（W3 采纳②）


@dataclass
class BacktestResult:
    equity: list[float] = field(default_factory=list)
    positions: list[int] = field(default_factory=list)
    report: dict = field(default_factory=dict)


def run_backtest(feed: MarketFeed, strategy, initial_cash: float = 1_000_000.0,
                 cost_rate: float = 0.0003) -> BacktestResult:
    """strategy 需实现 on_bar(view, position) -> 目标仓位 (1 持多 / 0 空仓)。"""
    cash, qty, pos = initial_cash, 0.0, 0   # 全仓进出：target=1 满仓、0 空仓
    equity: list[float] = []
    positions: list[int] = []
    for t in range(len(feed)):
        feed.set_step(t)
        view = WindowedView(t, feed)
        target = int(strategy.on_bar(view, pos))
        if target not in (0, 1):
            raise ValueError(f"demo 只支持 0/1 仓位，收到 {target}")
        price = feed.raw_close(t, where="backtest.execute")
        if target != pos:
            if target == 1:
                buy_qty = cash / (price * (1 + cost_rate))   # 满仓买入（含费）
                cash -= buy_qty * price * (1 + cost_rate)
                qty = buy_qty
            else:
                cash += qty * price * (1 - cost_rate)        # 全部卖出（含费）
                qty = 0.0
            pos = target
        equity.append(cash + qty * price)
        positions.append(pos)
    return BacktestResult(equity=equity, positions=positions,
                          report=_m.report(equity))


def oracle_equity(feed: MarketFeed, initial_cash: float = 1_000_000.0) -> list[float]:
    """泄露预言机（仅演示被拦截的诱惑量级，属测量侧，不给策略）：

    每根 bar 收盘后直接读次根收盘涨跌决定持仓——纯粹的前视作弊基线。
    对应 W3 笔记采纳①的对照组。
    """
    cash, qty, pos = initial_cash, 0.0, 0
    equity = []
    for t in range(len(feed)):
        price = feed.raw_close(t, where="oracle(harness-only)")
        if t + 1 < len(feed):
            nxt = feed.raw_close(t + 1, where="oracle(harness-only)")
            want = 1 if nxt > price else 0
        else:
            want = pos
        if want != pos:
            if want == 1:
                buy_qty = cash / price
                cash -= buy_qty * price
                qty = buy_qty
            else:
                cash += qty * price
                qty = 0.0
            pos = want
        equity.append(cash + qty * price)
    return equity
