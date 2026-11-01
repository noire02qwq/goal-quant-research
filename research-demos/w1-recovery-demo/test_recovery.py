"""W1 recovery demo 定点测试（stdlib unittest，无第三方依赖）。

    python3 -m unittest test_recovery -v

覆盖：原子认领无双写、fencing 拒绝过期写入、回执幂等、恢复扫描语义、
群组消息持久化恢复（brief-plan §5.2 规则 1/2/4/5 + §12.2 W1）。
"""

from __future__ import annotations

import os
import tempfile
import unittest

from goalstore import GoalStore


class StoreTestCase(unittest.TestCase):
    def setUp(self) -> None:
        fd, self.db_path = tempfile.mkstemp(suffix=".db", prefix="w1-test-")
        os.close(fd)
        os.unlink(self.db_path)
        self.store = GoalStore(self.db_path)

    def tearDown(self) -> None:
        self.store.close()
        for suffix in ("", "-wal", "-shm"):
            try:
                os.unlink(self.db_path + suffix)
            except FileNotFoundError:
                pass


class TestAtomicClaim(StoreTestCase):
    def test_sequential_claims_are_exclusive(self) -> None:
        self.store.seed_tasks(["t1", "t2", "t3"])
        a = self.store.claim_next("w1", 5.0)
        b = self.store.claim_next("w2", 5.0)
        self.assertIsNotNone(a)
        self.assertIsNotNone(b)
        self.assertNotEqual(a["id"], b["id"])
        # 第三个任务仍可被认领，前两个不再是 queued
        c = self.store.claim_next("w3", 5.0)
        self.assertIsNotNone(c)
        self.assertIsNone(self.store.claim_next("w4", 5.0), "不应认领到已认领任务")

    def test_claim_increments_fencing_token(self) -> None:
        self.store.seed_tasks(["t1"])
        run = self.store.claim_next("w1", 5.0)
        self.assertEqual(run["fencing_token"], 1)
        self.assertEqual(run["status"], "running")
        self.assertEqual(run["attempts"], 1)


class TestFencing(StoreTestCase):
    def test_stale_token_write_rejected(self) -> None:
        self.store.seed_tasks(["t1"])
        run = self.store.claim_next("w1", 5.0)
        # 租约过期 → 恢复扫描重排 → w2 重新认领（token 递增）
        self.store.recovery_scan(now=run["lease_expires_at"] + 1)
        run2 = self.store.claim_next("w2", 5.0)
        self.assertEqual(run2["fencing_token"], 2)
        # w1 持旧 token 写回执 → 必须被拒
        rejected = self.store.write_receipt(
            "t1#1", {"x": 1}, run_id=run["id"], token=run["fencing_token"], actor="w1"
        )
        self.assertFalse(rejected, "过期 fencing token 的写入必须被拒绝")
        # w2 新 token 写入成功
        accepted = self.store.write_receipt(
            "t1#1", {"x": 2}, run_id=run2["id"], token=run2["fencing_token"], actor="w2"
        )
        self.assertTrue(accepted)


class TestReceiptIdempotency(StoreTestCase):
    def test_receipt_exists_after_write(self) -> None:
        self.assertFalse(self.store.receipt_exists("k1"))
        self.store.write_receipt("k1", {"v": 1})
        self.assertTrue(self.store.receipt_exists("k1"))
        # 重复写不覆盖、不报错（INSERT OR IGNORE）
        self.store.write_receipt("k1", {"v": 2})
        row = self.store.db.execute(
            "SELECT payload_json FROM goal_receipt WHERE idempotency_key = 'k1'"
        ).fetchone()
        self.assertIn('"v": 1', row["payload_json"])


class TestRecoveryScan(StoreTestCase):
    def test_expired_running_requeued(self) -> None:
        self.store.seed_tasks(["t1"])
        run = self.store.claim_next("w1", 1.0)
        # 未过期：扫描不动它
        stats = self.store.recovery_scan(now=run["lease_expires_at"] - 1)
        self.assertEqual(stats["expired"], 0)
        # 过期：标记 outcome_unknown 并重排
        stats = self.store.recovery_scan(now=run["lease_expires_at"] + 1)
        self.assertEqual(stats, {"expired": 1, "requeued": 1, "completed_via_receipt": 0})
        after = self.store.get_run("t1#2026W45")
        self.assertEqual(after["status"], "queued")
        self.assertIsNone(after["claim_owner"])

    def test_expired_with_receipt_completes(self) -> None:
        self.store.seed_tasks(["t1"])
        run = self.store.claim_next("w1", 1.0)
        # 崩溃前期次回执已写入（complete_run 前的窗口）
        self.store.write_receipt(run["occurrence_key"], {"done": True})
        stats = self.store.recovery_scan(now=run["lease_expires_at"] + 1)
        self.assertEqual(stats["completed_via_receipt"], 1)
        self.assertEqual(self.store.get_run("t1#2026W45")["status"], "succeeded")

    def test_orphan_exec_marked_interrupted(self) -> None:
        self.store.seed_tasks(["t1"])
        run = self.store.claim_next("w1", 1.0)
        self.store.exec_start(run["occurrence_key"], 1, "step1")
        self.store.recovery_scan(now=run["lease_expires_at"] + 1)
        row = self.store.db.execute(
            "SELECT outcome FROM step_exec_log WHERE exec_key = ? AND step_no = 1",
            (run["occurrence_key"],),
        ).fetchone()
        self.assertEqual(row["outcome"], "interrupted", "崩溃步骤不得伪装成 completed")


class TestGroupPersistence(StoreTestCase):
    def test_append_is_idempotent_and_ordered(self) -> None:
        self.store.append_message("s1", 1, "researcher", "a")
        self.store.append_message("s1", 2, "coder", "b")
        self.store.append_message("s1", 1, "researcher", "a-dup")  # 重复 seq 忽略
        msgs = self.store.messages("s1")
        self.assertEqual([m["seq"] for m in msgs], [1, 2])
        self.assertEqual(msgs[0]["content"], "a", "重复写入不得覆盖原消息")

    def test_events_carry_actor_attribution(self) -> None:
        self.store.emit_event("researcher", "group_step_done", {"seq": 1})
        self.store.emit_event("coder", "group_step_done", {"seq": 2})
        rows = self.store.db.execute(
            "SELECT actor_agent_id FROM goal_event ORDER BY id"
        ).fetchall()
        self.assertEqual(
            [r["actor_agent_id"] for r in rows], ["researcher", "coder"],
            "goal_event 必须记录 actor_agent_id（§12.2 W1 落点）",
        )


if __name__ == "__main__":
    unittest.main()
