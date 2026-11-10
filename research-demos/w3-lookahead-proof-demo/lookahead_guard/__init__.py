"""前视偏差构造性不可能：窗口化数据访问 + 动态/静态双 lint + 指标库。"""
from .data import Bar, MarketFeed, WindowedView, LookaheadViolation
from .metrics import total_return, sharpe, max_drawdown
from .backtest import run_backtest, BacktestResult
from .lint import static_scan, dynamic_audit

__all__ = [
    "Bar", "MarketFeed", "WindowedView", "LookaheadViolation",
    "total_return", "sharpe", "max_drawdown",
    "run_backtest", "BacktestResult", "static_scan", "dynamic_audit",
]
