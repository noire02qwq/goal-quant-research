"""W4 审批/授权边界最小实现：use-time 审批消费、角色×工具矩阵、隔离审批通道、
goal 级预算、确定性 monitor——全部进程内、纯标准库。

对齐 W4 文献笔记采纳①–④（brief-plan §12.1 W4 / §12.2 W4）。
"""
from .gate import (
    ApprovalTicket, ApprovalChannel, ActionDenied,
    action_digest, consume, consume_by_call_id_only,
)
from .matrix import AuthMatrix, RoleBoundaryError
from .bus import GroupBus
from .budget import GoalBudget, BudgetExceeded
from .monitor import DeterministicMonitor, LlmJudge

__all__ = [
    "ApprovalTicket", "ApprovalChannel", "ActionDenied",
    "action_digest", "consume", "consume_by_call_id_only",
    "AuthMatrix", "RoleBoundaryError",
    "GroupBus", "GoalBudget", "BudgetExceeded",
    "DeterministicMonitor", "LlmJudge",
]
