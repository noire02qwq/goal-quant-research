"""前视 lint：第二道防线（API 拦截正常路径，lint 捕获绕过路径）。

对应 brief-plan §12.1 W3 方向②：复用 market-research 前视 lint 思路——
即便策略绕开 WindowedView 直读原始数据，动态审计 + 静态扫描仍能定罪。
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .data import MarketFeed

# 静态扫描的禁用模式：出现在**策略源码**里即高危（harness 自身文件不扫）
FORBIDDEN = [
    (re.compile(r"\bfeed\b"), "直接持有原始行情源对象"),
    (re.compile(r"\.bars\s*\("), "整段导出行情（含未来）"),
    (re.compile(r"raw_close"), "调用未钳制的直读接口"),
    (re.compile(r"\[.*\+.*\]"), "下标算术访问（疑似自行推算未来下标）"),
]

# harness 自身的合法读取前缀（回测执行、窗口视图、测量侧预言机）
_HARNESS = ("WindowedView", "backtest", "oracle")


@dataclass
class Finding:
    kind: str          # "dynamic" | "static"
    where: str         # file:line 或 (step, index)
    detail: str


def dynamic_audit(feed: MarketFeed) -> list[Finding]:
    """运行期审计：任何 index > step 的读取 = 前视行为，记录定罪证据。"""
    out = []
    for a in feed.access_log:
        if a.where.startswith(_HARNESS):
            continue
        if a.index > a.step:
            out.append(Finding(
                kind="dynamic",
                where=a.where,
                detail=f"step={a.step} 时读取了未来 bar {a.index}（越界 {a.index - a.step} 根）",
            ))
    return out


def static_scan(source_path: str | Path) -> list[Finding]:
    """静态扫描策略源码中的绕过模式，返回行号级发现。"""
    path = Path(source_path)
    out: list[Finding] = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        code = line.split("#", 1)[0]
        for pat, why in FORBIDDEN:
            if pat.search(code):
                out.append(Finding(
                    kind="static",
                    where=f"{path.name}:{lineno}",
                    detail=f"{why}：{line.strip()[:80]}",
                ))
    return out
