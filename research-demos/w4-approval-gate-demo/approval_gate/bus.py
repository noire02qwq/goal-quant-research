"""群组消息总线：消息只承载业务内容，**不得修改授权边界**（§12.2 W4 ①）。

注入"授权类"消息的结构性结局：被总线忽略 + 留审计，矩阵零变化。
"""
from __future__ import annotations

from .matrix import MatrixRegistry


# 越权载荷模式：出现在消息里即触发边界守卫（deterministic，非模型判断）
_TAMPER_KEYS = {"grant", "revoke", "role", "permission", "matrix",
                "authorize", "allow_tools", "budget_scope"}


class GroupBus:
    def __init__(self, registry: MatrixRegistry):
        self._registry = registry
        self.delivered: list[tuple[str, str, dict]] = []   # (sender, recipient, payload)
        self.audit: list[str] = []

    def send(self, sender: str, recipient: str, payload: dict) -> bool:
        hits = _TAMPER_KEYS & set(payload)
        if hits:
            before = self._registry.current.version
            self.audit.append(
                f"BOUNDARY-TAMPER blocked sender={sender} → {recipient}："
                f"载荷含授权字段 {sorted(hits)}，消息被结构性忽略（矩阵 {before} 不变）")
            return False                       # 不投递、不生效
        self.delivered.append((sender, recipient, dict(payload)))
        return True
