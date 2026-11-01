"""goal_run 持久化与恢复语义的最小实现（W1 recovery demo）。

覆盖 brief-plan §5.2 执行规则 2/4/5（回执先查再执行、结果不确定不隐藏重试、
恢复扫描）与 §12.2 W1 群组维度（group_message 持久化 + goal_event.actor_agent_id）。

独立原创实现，纯标准库 sqlite3；仅语义对照设计文档，不引用任何公司内部代码。
"""

from __future__ import annotations

import json
import sqlite3
import time
import uuid

SCHEMA = """
CREATE TABLE IF NOT EXISTS goal_run (
  id TEXT PRIMARY KEY,
  task_id TEXT NOT NULL,
  occurrence_key TEXT NOT NULL UNIQUE,
  status TEXT NOT NULL,
  claim_owner TEXT,
  lease_expires_at REAL,
  fencing_token INTEGER NOT NULL DEFAULT 0,
  attempts INTEGER NOT NULL DEFAULT 0,
  result_json TEXT,
  created_at REAL NOT NULL,
  updated_at REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS goal_receipt (
  idempotency_key TEXT PRIMARY KEY,
  payload_json TEXT NOT NULL,
  fencing_token INTEGER,
  written_at REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS step_exec_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  exec_key TEXT NOT NULL,
  step_no INTEGER NOT NULL,
  step_name TEXT NOT NULL,
  attempt INTEGER NOT NULL,
  started_at REAL NOT NULL,
  finished_at REAL,
  outcome TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_exec_key ON step_exec_log (exec_key, step_no);

CREATE TABLE IF NOT EXISTS goal_event (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  actor_agent_id TEXT,
  type TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  created_at REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS group_message (
  session_id TEXT NOT NULL,
  seq INTEGER NOT NULL,
  sender_agent_id TEXT NOT NULL,
  content TEXT NOT NULL,
  created_at REAL NOT NULL,
  PRIMARY KEY (session_id, seq)
);
"""


class GoalStore:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self.db = sqlite3.connect(db_path, timeout=10, isolation_level=None)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA busy_timeout=10000")
        self.db.executescript(SCHEMA)

    def close(self) -> None:
        self.db.close()

    # ---------- 种子与查询 ----------

    def seed_tasks(self, task_ids: list[str]) -> None:
        now = time.time()
        for task_id in task_ids:
            self.db.execute(
                """INSERT OR IGNORE INTO goal_run
                   (id, task_id, occurrence_key, status, created_at, updated_at)
                   VALUES (?, ?, ?, 'queued', ?, ?)""",
                (uuid.uuid4().hex, task_id, f"{task_id}#2026W45", now, now),
            )

    def get_run(self, occurrence_key: str) -> sqlite3.Row | None:
        return self.db.execute(
            "SELECT * FROM goal_run WHERE occurrence_key = ?", (occurrence_key,)
        ).fetchone()

    # ---------- 规则 1：原子认领 + 租约 + fencing ----------

    def claim_next(self, owner: str, lease_seconds: float) -> sqlite3.Row | None:
        now = time.time()
        row = self.db.execute(
            """UPDATE goal_run
               SET status = 'running', claim_owner = ?,
                   lease_expires_at = ?, fencing_token = fencing_token + 1,
                   attempts = attempts + 1, updated_at = ?
               WHERE id = (SELECT id FROM goal_run WHERE status = 'queued'
                           ORDER BY rowid LIMIT 1)
                 AND status = 'queued'
               RETURNING *""",
            (owner, now + lease_seconds, now),
        ).fetchone()
        return row

    def renew_lease(
        self, run_id: str, owner: str, token: int, lease_seconds: float
    ) -> bool:
        cur = self.db.execute(
            """UPDATE goal_run SET lease_expires_at = ?, updated_at = ?
               WHERE id = ? AND claim_owner = ? AND fencing_token = ?
                 AND status = 'running'""",
            (time.time() + lease_seconds, time.time(), run_id, owner, token),
        )
        return cur.rowcount == 1

    # ---------- 规则 2：幂等回执（先查再执行） ----------

    def receipt_exists(self, idempotency_key: str) -> bool:
        row = self.db.execute(
            "SELECT 1 FROM goal_receipt WHERE idempotency_key = ?",
            (idempotency_key,),
        ).fetchone()
        return row is not None

    def write_receipt(
        self,
        idempotency_key: str,
        payload: dict,
        *,
        run_id: str | None = None,
        token: int | None = None,
        actor: str | None = None,
    ) -> bool:
        """写回执。带 run_id/token 时做 fencing 校验：租约易主后旧写入被拒。"""
        self.db.execute("BEGIN IMMEDIATE")
        try:
            if run_id is not None:
                run = self.db.execute(
                    "SELECT * FROM goal_run WHERE id = ?", (run_id,)
                ).fetchone()
                if (
                    run is None
                    or run["fencing_token"] != token
                    or run["status"] != "running"
                ):
                    self.db.execute("ROLLBACK")
                    return False
            self.db.execute(
                """INSERT OR IGNORE INTO goal_receipt
                   (idempotency_key, payload_json, fencing_token, written_at)
                   VALUES (?, ?, ?, ?)""",
                (idempotency_key, json.dumps(payload, ensure_ascii=False), token, time.time()),
            )
            self.db.execute("COMMIT")
            return True
        except Exception:
            self.db.execute("ROLLBACK")
            raise

    def complete_run(self, run_id: str, token: int, result: dict, actor: str) -> bool:
        """期次完成：写期次回执 + 状态终态 + 事件，单事务。"""
        self.db.execute("BEGIN IMMEDIATE")
        try:
            run = self.db.execute(
                "SELECT * FROM goal_run WHERE id = ?", (run_id,)
            ).fetchone()
            if (
                run is None
                or run["fencing_token"] != token
                or run["status"] != "running"
            ):
                self.db.execute("ROLLBACK")
                return False
            self.db.execute(
                """INSERT OR IGNORE INTO goal_receipt
                   (idempotency_key, payload_json, fencing_token, written_at)
                   VALUES (?, ?, ?, ?)""",
                (
                    run["occurrence_key"],
                    json.dumps(result, ensure_ascii=False),
                    token,
                    time.time(),
                ),
            )
            self.db.execute(
                """UPDATE goal_run
                   SET status = 'succeeded', result_json = ?,
                       claim_owner = NULL, lease_expires_at = NULL, updated_at = ?
                   WHERE id = ?""",
                (json.dumps(result, ensure_ascii=False), time.time(), run_id),
            )
            self.emit_event(actor, "run_succeeded", {"occurrence_key": run["occurrence_key"]})
            self.db.execute("COMMIT")
            return True
        except Exception:
            self.db.execute("ROLLBACK")
            raise

    # ---------- 步骤执行证据 ----------

    def exec_start(self, exec_key: str, step_no: int, step_name: str) -> None:
        attempt = self.db.execute(
            """SELECT COALESCE(MAX(attempt), 0) + 1 FROM step_exec_log
               WHERE exec_key = ? AND step_no = ?""",
            (exec_key, step_no),
        ).fetchone()[0]
        self.db.execute(
            """INSERT INTO step_exec_log
               (exec_key, step_no, step_name, attempt, started_at, outcome)
               VALUES (?, ?, ?, ?, ?, 'running')""",
            (exec_key, step_no, step_name, attempt, time.time()),
        )

    def exec_finish(self, exec_key: str, step_no: int) -> None:
        self.db.execute(
            """UPDATE step_exec_log SET outcome = 'completed', finished_at = ?
               WHERE id = (SELECT id FROM step_exec_log
                           WHERE exec_key = ? AND step_no = ? AND outcome = 'running'
                           ORDER BY id DESC LIMIT 1)""",
            (time.time(), exec_key, step_no),
        )

    def interrupt_orphans(self, exec_key: str) -> int:
        """把遗留 running 的步骤证据标为 interrupted（崩溃/恢复语义，不隐藏）。"""
        cur = self.db.execute(
            """UPDATE step_exec_log SET outcome = 'interrupted', finished_at = ?
               WHERE exec_key = ? AND outcome = 'running'""",
            (time.time(), exec_key),
        )
        return cur.rowcount

    # ---------- 规则 4/5：恢复扫描 ----------

    def recovery_scan(self, now: float | None = None) -> dict:
        now = now if now is not None else time.time()
        expired = self.db.execute(
            """SELECT * FROM goal_run
               WHERE status = 'running' AND lease_expires_at < ?""",
            (now,),
        ).fetchall()
        stats = {"expired": len(expired), "requeued": 0, "completed_via_receipt": 0}
        for run in expired:
            self.db.execute("BEGIN IMMEDIATE")
            try:
                cur = self.db.execute(
                    """UPDATE goal_run SET status = 'outcome_unknown', updated_at = ?
                       WHERE id = ? AND status = 'running' AND lease_expires_at < ?""",
                    (now, run["id"], now),
                )
                if cur.rowcount == 0:
                    self.db.execute("ROLLBACK")
                    continue
                self.emit_event(
                    "system:recovery",
                    "lease_expired",
                    {"occurrence_key": run["occurrence_key"]},
                )
                if self.receipt_exists(run["occurrence_key"]):
                    self.db.execute(
                        """UPDATE goal_run SET status = 'succeeded', updated_at = ?
                           WHERE id = ?""",
                        (time.time(), run["id"]),
                    )
                    self.emit_event(
                        "system:recovery",
                        "recovered_via_receipt",
                        {"occurrence_key": run["occurrence_key"]},
                    )
                    stats["completed_via_receipt"] += 1
                else:
                    self.db.execute(
                        """UPDATE goal_run
                           SET status = 'queued', claim_owner = NULL,
                               lease_expires_at = NULL, updated_at = ?
                           WHERE id = ?""",
                        (time.time(), run["id"]),
                    )
                    self.emit_event(
                        "system:recovery",
                        "requeued",
                        {"occurrence_key": run["occurrence_key"]},
                    )
                    stats["requeued"] += 1
                self.interrupt_orphans(run["occurrence_key"])
                self.db.execute("COMMIT")
            except Exception:
                self.db.execute("ROLLBACK")
                raise
        return stats

    # ---------- 事件流（actor 归因） ----------

    def emit_event(self, actor: str | None, event_type: str, payload: dict) -> None:
        self.db.execute(
            """INSERT INTO goal_event (actor_agent_id, type, payload_json, created_at)
               VALUES (?, ?, ?, ?)""",
            (actor, event_type, json.dumps(payload, ensure_ascii=False), time.time()),
        )

    # ---------- §12.2 群组消息持久化 ----------

    def append_message(self, session_id: str, seq: int, sender: str, content: str) -> None:
        self.db.execute(
            """INSERT OR IGNORE INTO group_message
               (session_id, seq, sender_agent_id, content, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            (session_id, seq, sender, content, time.time()),
        )

    def messages(self, session_id: str) -> list[sqlite3.Row]:
        return self.db.execute(
            """SELECT * FROM group_message WHERE session_id = ?
               ORDER BY seq""",
            (session_id,),
        ).fetchall()

    # ---------- 证据统计 ----------

    def stats(self) -> dict:
        runs = {
            row["status"]: row["n"]
            for row in self.db.execute(
                "SELECT status, COUNT(*) AS n FROM goal_run GROUP BY status"
            )
        }
        exec_rows = [
            dict(row)
            for row in self.db.execute(
                """SELECT exec_key, step_no, step_name, outcome, COUNT(*) AS n
                   FROM step_exec_log
                   GROUP BY exec_key, step_no, step_name, outcome
                   ORDER BY exec_key, step_no"""
            )
        ]
        receipts = self.db.execute(
            "SELECT COUNT(*) AS n FROM goal_receipt"
        ).fetchone()["n"]
        events = [
            dict(row)
            for row in self.db.execute(
                """SELECT actor_agent_id, type, COUNT(*) AS n FROM goal_event
                   GROUP BY actor_agent_id, type ORDER BY actor_agent_id, type"""
            )
        ]
        return {
            "runs": runs,
            "exec": exec_rows,
            "receipts": receipts,
            "events": events,
        }
