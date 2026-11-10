"""窗口化行情数据：策略只能看到"截至当前 bar"，越界读取结构性抛错。

对应 brief-plan §12.1 W3 方向①：前视防护在接口层构造性保证，
而非提示词或事后 lint（lint 是第二道防线，见 lint.py）。
参照实现：W3 文献笔记 §MintEval「bar 回调前入 buffer、越界抛错」。
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from typing import NamedTuple


class LookaheadViolation(Exception):
    """策略试图读取可见地平线（当前 bar）之后的数据。"""


class Bar(NamedTuple):
    t: int
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass(frozen=True)
class RawAccess:
    """一次原始数据读取的审计记录（动态 lint 的输入）。"""
    step: int          # 读取发生时回测进行到的 bar
    index: int         # 被读取的 bar 下标
    where: str         # 调用点 "file:line"


class MarketFeed:
    """原始行情源。策略**不应**直接持有它；直读由动态 lint 捕获。"""

    def __init__(self, bars: list[Bar]):
        self._bars = list(bars)
        self._step = 0
        self.access_log: list[RawAccess] = []

    def __len__(self) -> int:
        return len(self._bars)

    def set_step(self, t: int) -> None:
        self._step = t

    def raw_close(self, i: int, where: str = "?") -> float:
        """直读收盘价（bypass 路径）。读取发生即记账，供动态 lint 审计。"""
        if where == "?":
            fr = sys._getframe(1)
            where = f"{os.path.basename(fr.f_code.co_filename)}:{fr.f_lineno}"
        self.access_log.append(RawAccess(step=self._step, index=i, where=where))
        return self._bars[i].close

    def bars(self) -> tuple[Bar, ...]:
        """整段导出——等价于把未来一次性交给策略，静态 lint 的头号目标。"""
        return tuple(self._bars)


class WindowedView:
    """策略唯一合法的数据入口：所有访问被钳制在 [0, t]。"""

    def __init__(self, t: int, feed: MarketFeed):
        if not 0 <= t < len(feed):
            raise IndexError(f"t={t} 越界（feed 共 {len(feed)} bar）")
        self._t = t
        self._feed = feed

    @property
    def now(self) -> int:
        return self._t

    def close(self, i: int) -> float:
        if i > self._t:
            raise LookaheadViolation(
                f"bar {i} 超出可见地平线 t={self._t}（未来数据被接口层拒绝）"
            )
        if i < 0:
            raise IndexError("负下标")
        return self._feed.raw_close(i, where="WindowedView.close")

    def window(self, n: int) -> list[float]:
        """最近 n 根收盘价（不足 n 根时从 0 开始），恒 ≤ 当前 bar。"""
        lo = max(0, self._t - n + 1)
        return [self._feed.raw_close(i, where="WindowedView.window")
                for i in range(lo, self._t + 1)]
