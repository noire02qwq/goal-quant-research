"""群组任务分解 opt-in：assigned_role 填与不填两条路径共存。

对应 brief-plan §12.2 W3：`goal_plan_task` 增加可选 assigned_role，
**默认单角色路径零改动**——不填即现有单受管 Run 行为，群组是 opt-in。
"""
from __future__ import annotations

from dataclasses import dataclass


class RoleBoundaryError(PermissionError):
    """任务有角色约束且认领者角色不匹配。"""


@dataclass(frozen=True)
class PlanTask:
    task_id: str
    title: str
    assigned_role: str | None = None   # None = 单角色路径（零改动语义）


def claim(task: PlanTask, worker_role: str) -> str:
    """认领任务：无角色约束任何人可领；有约束必须精确匹配。"""
    if task.assigned_role is None:
        return f"OK 任务 {task.task_id}（单角色路径，无约束）由 {worker_role} 认领"
    if worker_role != task.assigned_role:
        raise RoleBoundaryError(
            f"拒绝：任务 {task.task_id} 约束角色 {task.assigned_role!r}，"
            f"{worker_role!r} 无权认领"
        )
    return f"OK 任务 {task.task_id}（约束 {task.assigned_role}）由 {worker_role} 认领"
