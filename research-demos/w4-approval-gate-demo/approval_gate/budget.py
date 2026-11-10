"""预算按 goal 整体计（§12.2 W4 ②）：跨成员合计对 goal 上限，成员级只观测。

- 任何成员的消费都进同一 goal 池；合计超限 → 拒绝（不因成员而异）。
- 成员不能经消息/请求把 scope 改小来绕限（scope 面板只读，与 bus 边界守卫同源）。
"""
from __future__ import annotations

from dataclasses import dataclass, field


class BudgetExceeded(Exception):
    """goal 级预算超限。"""


@dataclass
class GoalBudget:
    goal_id: str
    cap_usd: float
    spent_by_member: dict[str, float] = field(default_factory=dict)

    @property
    def spent_total(self) -> float:
        return sum(self.spent_by_member.values())

    @property
    def remaining(self) -> float:
        return self.cap_usd - self.spent_total

    def charge(self, member: str, usd: float) -> float:
        """扣费：先按 goal 合计判定，超限整笔拒绝（不拆、不降级）。"""
        if usd < 0:
            raise ValueError("金额必须为正")
        if self.spent_total + usd > self.cap_usd:
            raise BudgetExceeded(
                f"goal {self.goal_id} 预算超限：合计 {self.spent_total:.2f}"
                f"+{usd:.2f} > 上限 {self.cap_usd:.2f}"
                f"（按 goal 整体计，与成员无关）")
        self.spent_by_member[member] = self.spent_by_member.get(member, 0.0) + usd
        return self.remaining

    def observation(self) -> dict:
        """成员级用量只读观测面板（不参与分摊决策）。"""
        return {"goal": self.goal_id, "cap": self.cap_usd,
                "total": round(self.spent_total, 2),
                "by_member": {k: round(v, 2)
                              for k, v in sorted(self.spent_by_member.items())}}
