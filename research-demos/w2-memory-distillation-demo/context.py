"""turn_context 组装协议（CALM：gate 先于 packing，挤出≠拒绝）。

固定顺序（对应 W2 文献笔记 §3"16KB 预算协议"）：
  1. 硬过滤：排除 CANDIDATE / ARCHIVED / SUPERSEDED / STALE（scope 准入另计）；
  2. 准入打分：utility + coverage + STABLE 加成 + TTL 剩余度；
  3. 按分贪心装入 token 预算；
  4. 被挤出者留持久层，可再检索——不是被拒绝。

token 估算为无分词器粗估（CJK≈1 token/字，其余≈0.25），仅 demo 口径。
"""
from __future__ import annotations

BUDGET_DEFAULT = 16 * 1024   # §5.1 有界摘要协议 16KB 上限，不因群组放宽

ELIGIBLE_LIFECYCLES = ("ACTIVE", "STABLE")


def est_tokens(text: str) -> int:
    cjk = sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff")
    other = len(text) - cjk
    return max(1, cjk + other // 4)


def card_text(card: dict) -> str:
    return (f"[{card['lifecycle']}] goal: {card['goal']}\n"
            f"初始条件: {card['initial_conditions']}\n"
            f"策略大纲: {card['strategy_outline']}")


def score(card: dict, now: float | None = None) -> float:
    util = max(0.0, min(1.0, (float(card["avg_utility"]) + 1.0) / 2.0))
    cov = max(0.0, min(1.0, float(card["retrieval_coverage"])))
    s = 0.5 * util + 0.3 * cov + (0.2 if card["lifecycle"] == "STABLE" else 0.0)
    if now is not None and card.get("valid_until"):
        # TTL 越临近过期分越低（剩余额度），到期后已由 STALE 硬过滤掉
        remaining = max(0.0, float(card["valid_until"]) - now)
        s *= 0.5 + 0.5 * min(1.0, remaining / 86400.0)
    return round(s, 4)


def assemble(cards: list[dict], budget: int = BUDGET_DEFAULT, now: float | None = None) -> dict:
    excluded, eligible = [], []
    for c in cards:
        if c["lifecycle"] not in ELIGIBLE_LIFECYCLES:
            excluded.append({"card_id": c["card_id"], "lifecycle": c["lifecycle"],
                             "reason": "硬过滤：非 ACTIVE/STABLE（CANDIDATE 未过 gate、"
                                       "SUPERSEDED 已被替代、STALE 过期、ARCHIVED 归档）"})
        else:
            eligible.append(c)

    ranked = sorted(eligible, key=lambda c: score(c, now), reverse=True)
    included, evicted, used = [], [], 0
    for c in ranked:
        cost = est_tokens(card_text(c))
        if used + cost <= budget:
            included.append({"card_id": c["card_id"], "lifecycle": c["lifecycle"],
                             "score": score(c, now), "tokens": cost})
            used += cost
        else:
            evicted.append({"card_id": c["card_id"], "lifecycle": c["lifecycle"],
                            "score": score(c, now), "tokens": cost,
                            "reason": "预算挤出（≠拒绝：留持久层，可再检索）"})

    return {"budget": budget, "used_tokens": used,
            "included": included, "evicted": evicted, "excluded": excluded}
