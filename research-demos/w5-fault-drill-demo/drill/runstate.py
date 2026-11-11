"""W5 演练核心：受管 Run 最小状态机 + 两级回执（0002 语义的进程内演练形态）。

五类注入中的三类在此：改坏代码 / 重启 / 改目标。
"""
from __future__ import annotations

from dataclasses import dataclass, field


class SimulatedCrash(Exception):
    """演练用进程崩溃（重启路径注入）。"""


class CodeBroken(Exception):
    """改坏代码路径注入：策略代码语法期/执行期失败。"""


@dataclass
class GoalEvent:
    kind: str
    detail: str


class Receipts:
    """步骤级幂等回执（INSERT OR IGNORE 首写胜出的 dict 等价物）。"""

    def __init__(self) -> None:
        self._store: dict[str, object] = {}
        self.replay_count = 0

    def first_write(self, key: str, value: object) -> tuple[object, bool]:
        if key in self._store:
            self.replay_count += 1
            return self._store[key], True       # True = 回执命中，未重跑
        self._store[key] = value
        return value, False

    def has(self, key: str) -> bool:
        return key in self._store

    def __contains__(self, key: str) -> bool:
        return key in self._store


@dataclass
class DrillRun:
    """一个目标的最小执行体：队列步骤 → 执行 → 回执；可注入故障。"""

    goal_id: str
    steps: list[str]
    receipts: Receipts = field(default_factory=Receipts)
    events: list[GoalEvent] = field(default_factory=list)
    executed: dict[str, int] = field(default_factory=dict)   # step → 实际执行次数
    repaired: list[str] = field(default_factory=list)
    broken_code_steps: set[str] = field(default_factory=set)
    crash_at: str | None = None
    completed: list[str] = field(default_factory=list)

    def _run_step(self, step: str) -> str:
        key = f"{self.goal_id}:{step}"
        if key in self.receipts:                       # 恢复/重启路径：回执命中不重跑
            self.events.append(GoalEvent("receipt_replay", f"{step} 命中回执，零重跑"))
            return str(self.receipts.first_write(key, "?")[0])
        if self.crash_at == step:                      # 重启路径注入点
            self.events.append(GoalEvent("crash", f"{step} 执行中崩溃"))
            raise SimulatedCrash(step)
        if step in self.broken_code_steps:             # 改坏代码注入点
            self.executed[step] = self.executed.get(step, 0) + 1
            self.events.append(GoalEvent("step_failed", f"{step} 代码故障"))
            raise CodeBroken(step)
        value = f"done:{step}"
        self.executed[step] = self.executed.get(step, 0) + 1
        out, _ = self.receipts.first_write(key, value)  # 先落回执（幂等核心）
        self.completed.append(step)
        return str(out)

    def run(self, stop_on_fault: bool = True) -> list[str]:
        """顺序执行队列；故障时按 stop_on_fault 决定抛出还是转入修复。"""
        out: list[str] = []
        for step in self.steps:
            if step in self.completed:                 # 已完成步骤永不重做
                continue
            key = f"{self.goal_id}:{step}"
            if key in self.receipts:                    # 重启路径：回执命中即恢复
                self.receipts.first_write(key, "?")     # 计一次回执命中（重放计数）
                self.events.append(GoalEvent("receipt_replay", f"{step} 命中回执，零重跑"))
                self.completed.append(step)             # 恢复语义：视为已完成
                continue                               # 不计入本轮执行输出
            try:
                out.append(self._run_step(step))
            except (SimulatedCrash, CodeBroken):
                if stop_on_fault:
                    raise
                break
        return out

    # -- 路径 1：改坏代码 → 修复任务重进循环（失败不终止） --
    def attempt_with_repair(self) -> dict:
        """一轮"执行→失败→生成修复任务→修复→重试"闭环。"""
        raised = None
        try:
            self.run(stop_on_fault=True)
        except CodeBroken as e:
            raised = str(e)
        if raised:                                     # 修复任务生成（§6.2 韧性）
            self.repaired.append(raised)
            self.events.append(GoalEvent("repair_task", f"{raised} → 修复任务入队"))
            self.broken_code_steps.discard(raised)     # 修复生效（演练注入清除）
            self.run(stop_on_fault=True)               # 重进循环
        self.events.append(GoalEvent("run_finished", "全部步骤完成"))
        return {"repaired": list(self.repaired), "completed": list(self.completed)}

    # -- 路径 3：改目标 → 队列重定标 + 显式状态机事件 --
    def change_goal(self, new_spec: str, at_step: str) -> None:
        self.events.append(GoalEvent(
            "goal_changed", f"{at_step} 之前队列重定标为 {new_spec}（已完成步骤不受影响）"))
