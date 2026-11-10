"""模型之下强制（W4 采纳④）：deterministic monitor 是唯一防线，
LLM judge 只作辅助信号、绝不单独放行（论文实测 judge 0/40 的教训）。

判定结构：`enforce()` 只读规则与事实（确定性），judge 结果最多作为
告警附注；judge 即便说"没问题"，规则违规照拦。
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Verdict:
    allowed: bool
    reason: str
    judge_note: str = ""     # 辅助信号，永不参与 allowed 计算


class LlmJudge:
    """模拟小模型 judge：会犯错（demo 里给一个"误放行"样例）。"""

    def __init__(self, verdicts: dict[str, bool] | None = None):
        self._verdicts = verdicts or {}

    def review(self, action_id: str) -> tuple[bool, str]:
        ok = self._verdicts.get(action_id, True)   # 默认"看起来没问题"
        return ok, ("judge: 操作看起来合规" if ok else "judge: 存疑")


class DeterministicMonitor:
    """规则引擎：逐条硬规则判定，与 judge 输出零耦合。"""

    def __init__(self, judge: LlmJudge | None = None):
        self.judge = judge or LlmJudge()
        self.audit: list[str] = []

    def enforce(self, action_id: str, *, role_ok: bool, approval_ok: bool,
                budget_ok: bool) -> Verdict:
        checks = {"角色授权": role_ok, "审批有效": approval_ok, "预算内": budget_ok}
        failed = [k for k, v in checks.items() if not v]
        j_ok, j_note = self.judge.review(action_id)
        verdict = Verdict(
            allowed=not failed,
            reason="全部硬规则通过" if not failed else f"硬规则拦截：{'、'.join(failed)}",
            judge_note=j_note + ("（辅助信号，不参与判定）" if not failed else ""),
        )
        self.audit.append(
            f"enforce {action_id} → {'ALLOW' if verdict.allowed else 'DENY'} "
            f"[{verdict.reason}] judge_said_ok={j_ok}")
        return verdict
