"""三个策略对照组：

1. dual_ma —— 干净路径：只经 view.window 读数据，静态/动态双 lint 全绿。
2. peek_via_view —— 越界走合法接口：被接口层结构性拒绝（LookaheadViolation）。
3. bypass 见独立文件 bypass_strategy.py（静态扫描按文件定罪，
   干净策略与绕过策略必须分文件，否则一锅端）。
"""
from __future__ import annotations

from lookahead_guard import LookaheadViolation  # noqa: F401（供测试导入）


class DualMA:
    """双均线（T1 形态）：短均线上穿长均线持多，下穿空仓。"""

    def __init__(self, fast: int = 5, slow: int = 20):
        self.fast, self.slow = fast, slow

    def on_bar(self, view, position: int) -> int:
        # 一次性取 slow+1 根：当前与前一根的快/慢均线都从同一段历史切，
        # 保证金叉判定 = 两条序列在 t 与 t-1 的严格对比（口径一致）。
        hist = view.window(self.slow + 1)
        if len(hist) < self.slow + 1:
            return position                      # 数据不足保持原仓
        fast_now = sum(hist[-self.fast:]) / self.fast
        slow_now = sum(hist[-self.slow:]) / self.slow
        fast_prev = sum(hist[-self.fast - 1:-1]) / self.fast
        slow_prev = sum(hist[-self.slow - 1:-1]) / self.slow
        if fast_now > slow_now and fast_prev <= slow_prev:
            return 1                             # 金叉 → 持多
        if fast_now < slow_now and fast_prev >= slow_prev:
            return 0                             # 死叉 → 空仓
        return position


class PeekViaView:
    """用合法接口读未来：接口层构造性拒绝（demo 步骤 2 展示）。"""

    def on_bar(self, view, position: int) -> int:
        _ = view.close(view.now + 1)   # ← 抛 LookaheadViolation
        return position
