"""晋升 gate：可计算判据，不靠 LLM 拍板（依据 W2 文献笔记 §3）。

主 gate = SEPM reproduction gate（≥1 次复现 trial + 平均效用≥0 + 因果一致性≥0.65）
前置过滤 = HaMo retrieval-coverage（被多任务检索支持才值得沉淀）

两个 gate 都可在交互界面开关——关掉即论文消融复现：
gate 全开时垃圾经验被拦截；关掉 reproduction gate 后污染卡进入 ACTIVE，
随后 turn_context 被稀释（对应 SEPM"memory 单独几乎无效，须有晋升才有兑现"）。
"""
from __future__ import annotations

COVERAGE_MIN = 0.30   # HaMo retrieval-coverage 前置阈值
CAUSAL_MIN = 0.65     # SEPM 因果一致性阈值
UTILITY_MIN = 0.0     # SEPM 平均效用下界

DEFAULT_GATES = {"coverage": True, "reproduction": True}


def evaluate(card: dict, gates: dict | None = None) -> dict:
    """返回 {pass, checks:[{gate, pass, ...}], gates}，逐项给出拦截原因。"""
    g = dict(DEFAULT_GATES)
    if gates:
        g.update(gates)
    checks: list[dict] = []
    passed = True

    if g.get("coverage", True):
        actual = float(card["retrieval_coverage"])
        ok = actual >= COVERAGE_MIN
        checks.append({"gate": "coverage 前置过滤 (HaMo)", "pass": ok,
                       "rule": f"retrieval_coverage >= {COVERAGE_MIN}",
                       "actual": actual})
        passed = passed and ok

    if g.get("reproduction", True):
        sub = [
            {"rule": "reproduction_count >= 1", "actual": card["reproduction_count"],
             "pass": card["reproduction_count"] >= 1},
            {"rule": "avg_utility >= 0", "actual": card["avg_utility"],
             "pass": card["avg_utility"] >= UTILITY_MIN},
            {"rule": "causal_consistency >= 0.65", "actual": card["causal_consistency"],
             "pass": card["causal_consistency"] >= CAUSAL_MIN},
        ]
        ok = all(s["pass"] for s in sub)
        checks.append({"gate": "reproduction 主 gate (SEPM)", "pass": ok,
                       "rule": "≥1 次复现 + 效用≥0 + 因果一致性≥0.65", "sub": sub})
        passed = passed and ok

    return {"pass": passed, "checks": checks, "gates": g}
