"""执行面诚实性（W5 采纳⑥-ii）：submitted≠filled 可见化 + 熔断必须真触发。

AllPath 教训：最有教益的生产事故全部通过所有 gate、由操作者手工发现，
共同修复是 interface 诚实；「熔断器全程武装但从未触发」= 演练无效。
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Order:
    order_id: str
    side: str            # buy / sell
    qty: int
    px: float            # 提交价（限价）
    status: str = "submitted"
    filled_px: float | None = None
    filled_qty: int = 0


@dataclass
class Broker:
    """模拟撮合：可注入「静默成交偏差」（submitted 但实际成交不同/未成交）。"""
    silent_fill_bugs: set[str] = field(default_factory=set)   # order_id 集合
    fills: dict[str, Order] = field(default_factory=dict)

    def submit(self, o: Order) -> Order:
        if o.order_id in self.silent_fill_bugs:
            # 静默故障：状态停在 submitted，但真实成交发生在更差价（界面看"正常"）
            self.fills[o.order_id] = Order(
                o.order_id, o.side, o.qty, o.px,
                status="filled_real", filled_px=o.px * 1.01, filled_qty=o.qty)   # 滑 1%
            return o                                     # 交给调用方的仍是 submitted
        real = Order(o.order_id, o.side, o.qty, o.px,
                     status="filled", filled_px=o.px, filled_qty=o.qty)
        self.fills[o.order_id] = real
        o.status = "filled"
        return o


class Reconciler:
    """对账器：柜台真实成交 vs 界面状态——静默偏差必须被点名（interface 诚实）。"""

    @staticmethod
    def reconcile(view: list[Order], broker: Broker) -> list[str]:
        findings = []
        for o in view:
            real = broker.fills.get(o.order_id)
            if real is None:
                findings.append(f"{o.order_id}: 界面 {o.status} 但柜台无成交记录")
            elif o.status != real.status:
                findings.append(
                    f"{o.order_id}: 界面 {o.status} ≠ 柜台 {real.status}"
                    f"（真实 {real.filled_qty}@{real.filled_px}，提交 {o.qty}@{o.px}）"
                    "——submitted≠filled，静默正常化被点名")
            elif real.filled_px != o.px:
                findings.append(f"{o.order_id}: 成交价偏差 {o.px}→{real.filled_px}")
        return findings


class Breaker:
    """熔断器：价格跳变超阈值即真触发（不是武装给人看的）。"""

    def __init__(self, max_gap_pct: float):
        self.max_gap_pct = max_gap_pct
        self.armed = True
        self.tripped = False
        self.trip_reason = ""

    def check(self, prev_px: float, px: float, halt) -> bool:
        if not self.armed:
            return False
        gap = abs(px / prev_px - 1.0) * 100
        if gap > self.max_gap_pct:
            self.tripped = True
            self.trip_reason = f"价格跳变 {gap:.2f}% > 阈值 {self.max_gap_pct}%"
            halt()                                  # 真停：回调挂起下单
            return True
        return False
