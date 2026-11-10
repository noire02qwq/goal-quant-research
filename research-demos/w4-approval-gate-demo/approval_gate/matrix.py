"""角色×工具授权矩阵（§12.2 W4 ③）：静态定义、**不可变**——越权修改必须失败。

- 消息/成员不能原地改矩阵；撤销 = 发布新版本矩阵（整表替换、旧版留档）。
- reviewer 角色位预留给 W8 反方评审（A3）。
- 撤销生效即检查拒（OpenDots 运行时热撤销同向，§3 走读结论）。
"""
from __future__ import annotations

from dataclasses import dataclass


class RoleBoundaryError(PermissionError):
    """角色无权使用该工具，或试图修改授权边界。"""


@dataclass(frozen=True)
class AuthMatrix:
    version: str
    grants: frozenset[tuple[str, str]]   # (role, tool) 白名单；frozen = 不可变

    @classmethod
    def v1(cls) -> "AuthMatrix":
        return cls("v1", frozenset({
            ("researcher", "market_data.read"),
            ("researcher", "backtest.run"),
            ("coder", "code.edit"),
            ("coder", "backtest.run"),
            ("reviewer", "approval.decide"),     # 审批仅 reviewer（W8 预留位）
            ("reviewer", "approval.revoke"),
        }))

    @classmethod
    def v1_after_revocation(cls) -> "AuthMatrix":
        """撤销 coder 的 backtest.run：发布新版本，而非原地改（不可变上限）。"""
        return cls("v1-revoked", frozenset({
            ("researcher", "market_data.read"),
            ("researcher", "backtest.run"),
            ("coder", "code.edit"),
            ("reviewer", "approval.decide"),
            ("reviewer", "approval.revoke"),
        }))

    def allows(self, role: str, tool: str) -> bool:
        return (role, tool) in self.grants

    def try_mutate(self, role: str, tool: str) -> None:
        """越权修改授权边界的唯一合法结局：抛错（frozen dataclass 保证）。"""
        try:
            self.grants = self.grants | {(role, tool)}   # type: ignore[misc]
        except AttributeError as e:
            raise RoleBoundaryError(
                f"授权矩阵不可变（version={self.version}）："
                f"成员/消息不得原地加入 ({role}, {tool})") from e


class MatrixRegistry:
    """矩阵版本管理：当前生效版 + 历史留档；检查与撤销都走这里（可审计）。"""

    def __init__(self, initial: AuthMatrix):
        self._history: list[AuthMatrix] = [initial]
        self.audit: list[str] = []

    @property
    def current(self) -> AuthMatrix:
        return self._history[-1]

    def check(self, role: str, tool: str) -> bool:
        ok = self.current.allows(role, tool)
        self.audit.append(
            f"check v={self.current.version} {role}×{tool} → {'allow' if ok else 'deny'}")
        return ok

    def publish(self, new: AuthMatrix) -> str:
        self._history.append(new)
        self.audit.append(f"publish matrix {new.version}（整表替换，"
                          f"旧版 {self._history[-2].version} 留档）")
        return new.version
