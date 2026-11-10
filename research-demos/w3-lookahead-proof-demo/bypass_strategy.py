"""绕过策略：故意不用窗口视图、直读原始行情源——双 lint 的活靶子。

单独成文件的原因：静态扫描以**文件**为定罪单位（lint.py static_scan），
干净策略必须能被扫描为零发现。
"""
from __future__ import annotations


class BypassRaw:
    """绕开窗口视图直读原始源，赌明天涨就满仓。"""

    def __init__(self, feed) -> None:
        self.feed = feed          # 静态扫描命中：直接持有原始行情源对象

    def on_bar(self, view, position: int) -> int:
        t = view.now
        if t + 1 >= len(self.feed):        # 最后一根无"明天"可偷
            return position
        price_now = self.feed.raw_close(t)
        price_next = self.feed.raw_close(t + 1)   # 动态审计命中：读未来
        return 1 if price_next > price_now else 0
