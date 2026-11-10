"""审批门：use-time 重建完整操作 + material arguments digest 比对 + 原子消费。

对齐 W4 采纳①（Loopjacking 教训：只绑 call id 时 A→B 替换攻击必拒——
digest 必须覆盖 material arguments）与 §12.2 W4 ①（审批归因 requested_by）。

审批通道（ApprovalChannel）模拟"独立于 agent"（采纳②的最小验证形态）：
令牌存放命名空间与 agent 可读命名空间分离，agent 侧列举不可见。
"""
from __future__ import annotations

import hashlib
import itertools
import json
import time
from dataclasses import dataclass, field


class ActionDenied(Exception):
    """审批缺失/失配/已消费/归因非法，统一拒绝出口。"""


def action_digest(tool: str, material_args: dict) -> str:
    """material arguments 的规范化摘要——审批与执行必须逐字比对。"""
    payload = json.dumps({"tool": tool, "args": material_args},
                         sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass
class ApprovalTicket:
    approval_id: str
    call_id: str              # 绑定调用 id（**不充分**，仅作关联）
    tool: str
    args_digest: str          # material arguments digest（充分绑定的关键）
    requested_by: str         # 归因：哪个成员发起（§12.2 W4 ①）
    issued_at: float = field(default_factory=time.time)
    consumed: bool = False    # 原子消费位（单次有效）


class ApprovalChannel:
    """审批通道：独立命名空间，agent 不可读（采纳②最小验证）。"""

    def __init__(self) -> None:
        self._tickets: dict[str, ApprovalTicket] = {}
        self._seq = itertools.count(1)
        self.audit: list[str] = []

    # -- agent 可见面（刻意不含任何令牌数据） --
    def agent_visible(self) -> dict:
        """agent 侧能列举到的东西：只有请求入口回执，无令牌。"""
        return {"can_list_tickets": False,
                "note": "审批令牌不在 agent 可读命名空间（通道独立）"}

    # -- 通道面（审批方/引擎侧调用） --
    def issue(self, call_id: str, tool: str, material_args: dict,
              requested_by: str) -> ApprovalTicket:
        if not requested_by:
            raise ActionDenied("审批归因缺失：requested_by 为空")
        t = ApprovalTicket(
            approval_id=f"appr_{next(self._seq)}",
            call_id=call_id,
            tool=tool,
            args_digest=action_digest(tool, material_args),
            requested_by=requested_by,
        )
        self._tickets[t.approval_id] = t
        self.audit.append(f"issue {t.approval_id} tool={tool} requested_by={requested_by}")
        return t

    def peek(self, approval_id: str) -> ApprovalTicket:
        t = self._tickets.get(approval_id)
        if t is None:
            raise ActionDenied(f"审批不存在：{approval_id}")
        return t


def consume(channel: ApprovalChannel, ticket: ApprovalTicket,
            call_id: str, tool: str, material_args: dict) -> str:
    """use-time 校验 + 原子消费：三道比对全过才放行，消费位 CAS 式单次。

    比对：①票据存在 ②call_id 关联 ③tool 一致 ④material arguments digest
    一致 ⑤未被消费（原子置位，重复消费拒绝）。
    """
    if ticket.consumed:                       # 原子消费：第二次直接拒
        raise ActionDenied(f"审批已消费（单次有效）：{ticket.approval_id}")
    if ticket.call_id != call_id:
        raise ActionDenied(f"call_id 失配：{ticket.call_id} != {call_id}")
    if ticket.tool != tool:
        raise ActionDenied(f"tool 失配：{ticket.tool} != {tool}")
    if ticket.args_digest != action_digest(tool, material_args):
        raise ActionDenied(
            f"material arguments digest 失配：审批时 {ticket.args_digest[:12]}… "
            f"执行时 {action_digest(tool, material_args)[:12]}…（替换攻击被拒）")
    ticket.consumed = True                   # 原子置位（单线程 demo 内等价 CAS）
    channel.audit.append(
        f"consume {ticket.approval_id} tool={tool} "
        f"digest={ticket.args_digest[:12]} requested_by={ticket.requested_by}")
    return ticket.approval_id


def consume_by_call_id_only(channel: ApprovalChannel, ticket: ApprovalTicket,
                            call_id: str) -> str:
    """【负例对照】只绑 call id 的弱消费——Loopjacking A→B 替换攻击会放行。

    仅用于 demo 对照展示"为什么必须 digest"，生产路径禁止使用（0005 记录）。
    """
    if ticket.consumed:
        raise ActionDenied(f"审批已消费：{ticket.approval_id}")
    if ticket.call_id != call_id:
        raise ActionDenied("call_id 失配")
    ticket.consumed = True
    channel.audit.append(f"consume-WEAK {ticket.approval_id}（未校验 material arguments）")
    return ticket.approval_id
