"""数据面注入（W5 采纳⑥-iii）：伪造新闻喂入；与执行面故障**正交**、
backtest 缓存数据内**不可见**——必须在 feed 摄入口设防。

依据：Fake News Real Crashes——未设防 61.7% vs 设防 13.8%；
标记化注入评测会系统性低估脆弱性（显式标记 0% → 混入 feed 46%）。
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NewsItem:
    item_id: str
    source: str          # 已知数据源白名单外 = 可疑
    headline: str
    signed: bool         # 数据源签名（provenance）


FORGED = NewsItem("n-evil", "unknown-feed", "突发：标的将停牌（伪造）", signed=False)


class FeedGuard:
    """摄入口守卫：无签名/白名单外来源 → 拦截并留审计。"""

    def __init__(self, trusted_sources: set[str]):
        self.trusted = trusted_sources
        self.blocked: list[NewsItem] = []
        self.admitted: list[NewsItem] = []

    def ingest(self, item: NewsItem) -> bool:
        ok = item.signed and item.source in self.trusted
        (self.admitted if ok else self.blocked).append(item)
        return ok


def headline_drive(headline: str) -> int:
    """新闻驱动力：含「停牌」等恐慌词 → 空仓信号（被注入时即被操纵）。"""
    return -1 if any(w in headline for w in ("停牌", "退市", "暴跌")) else 0


def backtest_candles_signature(candles: list[tuple]) -> str:
    """回测只看 candle——伪造新闻不改变 candle，签名必然与干净集相同。

    这正是「与执行面故障正交、backtest 内均不可见」的可执行证明：
    被污染 feed 的回测报告与干净 feed 逐字节一致（对 candle 签名比对）。
    """
    import hashlib
    payload = repr(candles).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()
