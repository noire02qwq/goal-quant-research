"""W2 记忆蒸馏 demo：记忆存储与生命周期（纯标准库 sqlite3）

生命周期状态机沿 CALM 裁剪（依据 docs/literature/W2-context-memory-distillation.md §3）：
    CANDIDATE → ACTIVE → STABLE → SUPERSEDED / STALE → ARCHIVED

两条核心语义：
- supersede 不物理删除：旧记忆置 SUPERSEDED + superseded_by 指针，历史回放仍可读；
- TTL 是第二触发通道（金融域"时间流逝不致 stale"，故用显式 validity interval）。
"""
from __future__ import annotations

import sqlite3
import time
import uuid

LIFECYCLES = ("CANDIDATE", "ACTIVE", "STABLE", "SUPERSEDED", "STALE", "ARCHIVED")

# 合法状态迁移（确定性规则维护，digest 更新不靠 LLM 重写全文）
ALLOWED_TRANSITIONS = {
    "CANDIDATE": {"ACTIVE", "SUPERSEDED", "ARCHIVED"},
    "ACTIVE": {"STABLE", "SUPERSEDED", "STALE", "ARCHIVED"},
    "STABLE": {"SUPERSEDED", "STALE", "ARCHIVED"},
    "SUPERSEDED": {"ARCHIVED"},
    "STALE": {"ARCHIVED"},
    "ARCHIVED": set(),
}

SCHEMA = """
CREATE TABLE IF NOT EXISTS memory_card (
    card_id            TEXT PRIMARY KEY,
    goal               TEXT NOT NULL,
    initial_conditions TEXT NOT NULL,
    strategy_outline   TEXT NOT NULL,
    scope              TEXT NOT NULL DEFAULT 'shared',   -- shared | private（§12.2 群组记忆分层）
    author_agent_id    TEXT,
    lifecycle          TEXT NOT NULL DEFAULT 'CANDIDATE',
    reproduction_count INTEGER NOT NULL DEFAULT 0,
    avg_utility        REAL NOT NULL DEFAULT 0.0,
    causal_consistency REAL NOT NULL DEFAULT 0.0,
    retrieval_coverage REAL NOT NULL DEFAULT 0.0,
    valid_until        REAL,                              -- epoch 秒；NULL = 不过期
    superseded_by      TEXT,
    created_at         REAL NOT NULL,
    updated_at         REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS memory_event (
    seq     INTEGER PRIMARY KEY AUTOINCREMENT,
    card_id TEXT,
    kind    TEXT NOT NULL,
    detail  TEXT NOT NULL,
    ts      REAL NOT NULL
);
"""


class InvalidTransition(Exception):
    pass


class MemoryStore:
    def __init__(self, path: str = ":memory:", now=None):
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)
        self.conn.commit()
        self._now = now or time.time

    # ---------- 写 ----------

    def add_card(self, goal: str, initial_conditions: str, strategy_outline: str,
                 scope: str = "shared", author_agent_id: str | None = None,
                 reproduction_count: int = 0, avg_utility: float = 0.0,
                 causal_consistency: float = 0.0, retrieval_coverage: float = 0.0,
                 valid_in_seconds: float | None = None) -> str:
        card_id = uuid.uuid4().hex[:12]
        now = self._now()
        valid_until = (now + valid_in_seconds) if valid_in_seconds else None
        self.conn.execute(
            """INSERT INTO memory_card
               (card_id, goal, initial_conditions, strategy_outline, scope, author_agent_id,
                lifecycle, reproduction_count, avg_utility, causal_consistency,
                retrieval_coverage, valid_until, created_at, updated_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (card_id, goal, initial_conditions, strategy_outline, scope, author_agent_id,
             "CANDIDATE", reproduction_count, avg_utility, causal_consistency,
             retrieval_coverage, valid_until, now, now))
        self.conn.commit()
        self.record(card_id, "created", "新经验卡入池（CANDIDATE，未过 gate 不进上下文）")
        return card_id

    def update_metrics(self, card_id: str, **metrics) -> None:
        cols = {"reproduction_count", "avg_utility", "causal_consistency", "retrieval_coverage"}
        unknown = set(metrics) - cols
        if unknown:
            raise ValueError(f"未知指标: {unknown}")
        sets = ", ".join(f"{k}=?" for k in metrics)
        self.conn.execute(
            f"UPDATE memory_card SET {sets}, updated_at=? WHERE card_id=?",
            (*metrics.values(), self._now(), card_id))
        self.conn.commit()
        self.record(card_id, "metrics_updated", f"复现证据更新: {metrics}")

    def transition(self, card_id: str, to: str, kind: str, detail: str) -> None:
        row = self.get_card(card_id)
        if row is None:
            raise KeyError(card_id)
        if to not in ALLOWED_TRANSITIONS[row["lifecycle"]]:
            raise InvalidTransition(f"{row['lifecycle']} → {to} 不在允许迁移表内")
        self.conn.execute(
            "UPDATE memory_card SET lifecycle=?, updated_at=? WHERE card_id=?",
            (to, self._now(), card_id))
        self.conn.commit()
        self.record(card_id, kind, detail)

    def supersede(self, old_id: str, new_id: str) -> None:
        """supersede 不删除：旧卡置 SUPERSEDED + 指针指向替代者，历史回放仍可读。"""
        if old_id == new_id:
            raise ValueError("不能用自己替代自己")
        if self.get_card(new_id) is None:
            raise KeyError(new_id)
        self.transition(old_id, "SUPERSEDED", "superseded",
                        f"被 {new_id} 替代（不删除，指针保留，历史回放可读）")
        self.conn.execute(
            "UPDATE memory_card SET superseded_by=?, updated_at=? WHERE card_id=?",
            (new_id, self._now(), old_id))
        self.conn.commit()

    def expire_due(self) -> list[str]:
        """TTL 第二触发通道：valid_until 已过的 ACTIVE/STABLE 卡置 STALE。"""
        now = self._now()
        rows = self.conn.execute(
            """SELECT card_id FROM memory_card
               WHERE valid_until IS NOT NULL AND valid_until <= ?
                 AND lifecycle IN ('ACTIVE','STABLE')""", (now,)).fetchall()
        hit = [r["card_id"] for r in rows]
        for cid in hit:
            self.transition(cid, "STALE", "ttl_expired",
                            f"TTL 到期（valid_until <= now={now:.0f}），退出上下文但不删除")
        return hit

    def record(self, card_id: str | None, kind: str, detail: str) -> None:
        self.conn.execute(
            "INSERT INTO memory_event (card_id, kind, detail, ts) VALUES (?,?,?,?)",
            (card_id, kind, detail, self._now()))
        self.conn.commit()

    # ---------- 读 ----------

    def get_card(self, card_id: str) -> sqlite3.Row | None:
        return self.conn.execute(
            "SELECT * FROM memory_card WHERE card_id=?", (card_id,)).fetchone()

    def list_cards(self) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM memory_card ORDER BY created_at, card_id").fetchall()
        return [dict(r) for r in rows]

    def events(self, limit: int = 200) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM memory_event ORDER BY seq DESC LIMIT ?", (limit,)).fetchall()
        return [dict(r) for r in reversed(rows)]

    def close(self) -> None:
        self.conn.close()
