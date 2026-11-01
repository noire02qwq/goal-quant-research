#!/usr/bin/env python3
"""W1 recovery demo 的 worker 进程：认领 → 回执先查 → 分步执行 → 回执/终态。

可作为子进程运行（真实进程崩溃注入用 os._exit 硬退出）：

    python3 worker.py --db <path> --owner w1 [--mode run|group]
        [--lease 5.0] [--step-sleep 0.02] [--crash-at N] [--group-session S]

崩溃注入：--crash-at N 在第 N 步 exec_start 之后硬退出，
不写回执、不释放租约，模拟进程崩溃（对应 §5.2 规则 4 的 outcome_unknown 路径）。
"""

from __future__ import annotations

import argparse
import os
import sys
import time

from goalstore import GoalStore

RUN_STEPS = ["fetch_history", "compute_indicators", "emit_report"]

GROUP_STEPS = [
    ("researcher", "literature scan done; candidate workflow: AWM-style归纳"),
    ("coder", "implement workflow extractor with bounded context"),
    ("researcher", "review: edge case found in parser fallback"),
    ("coder", "fix parser, tests green"),
    ("researcher", "summarize experiment results"),
    ("coder", "archive artifacts and receipts"),
]


def run_one_task(
    store: GoalStore,
    run,
    *,
    owner: str,
    lease_seconds: float,
    step_sleep: float,
    crash_at: int | None,
) -> str:
    key = run["occurrence_key"]
    token = run["fencing_token"]

    # 规则 2：回执先查再执行
    if store.receipt_exists(key):
        store.complete_run(run["id"], token, {"skipped": True}, owner)
        return "skipped_by_receipt"

    for step_no, step_name in enumerate(RUN_STEPS, 1):
        step_key = f"{key}#{step_no}"
        if store.receipt_exists(step_key):
            continue  # 步骤级幂等：恢复重跑不重复执行已完成步骤
        store.exec_start(key, step_no, step_name)
        if crash_at == step_no:
            os._exit(137)  # 硬崩溃：不写回执、不释放租约
        if not store.renew_lease(run["id"], owner, token, lease_seconds):
            store.interrupt_orphans(key)
            return "stale_abort"  # 租约易主（fencing）：放弃本地执行
        time.sleep(step_sleep)
        store.write_receipt(
            step_key, {"step": step_name}, run_id=run["id"], token=token, actor=owner
        )
        store.exec_finish(key, step_no)

    ok = store.complete_run(
        run["id"], token, {"steps": len(RUN_STEPS)}, actor=owner
    )
    return "succeeded" if ok else "stale_abort"


def run_group_session(
    store: GoalStore,
    session_id: str,
    *,
    crash_at: int | None,
    step_sleep: float,
) -> str:
    # 启动即从持久化消息重建会话上下文（§12.2 W1：中断后从持久化消息恢复）
    transcript = store.messages(session_id)
    store.interrupt_orphans(session_id)

    for seq, (sender, content) in enumerate(GROUP_STEPS, 1):
        store.append_message(session_id, seq, sender, content)  # 幂等（PK 冲突忽略）
        step_key = f"{session_id}#step{seq}"
        if store.receipt_exists(step_key):
            continue  # 已完成步骤不重跑（群组幂等回执复用）
        store.exec_start(session_id, seq, f"step{seq}")
        if crash_at == seq:
            os._exit(137)
        time.sleep(step_sleep)
        store.write_receipt(step_key, {"by": sender, "seq": seq})
        store.exec_finish(session_id, seq)
        store.emit_event(sender, "group_step_done", {"session": session_id, "seq": seq})

    final = store.messages(session_id)
    print(
        f"[group] session={session_id} transcript {len(transcript)} -> {len(final)} messages",
        flush=True,
    )
    return "succeeded"


def main() -> int:
    parser = argparse.ArgumentParser(description="W1 recovery demo worker")
    parser.add_argument("--db", required=True)
    parser.add_argument("--owner", required=True)
    parser.add_argument("--mode", choices=["run", "group"], default="run")
    parser.add_argument("--group-session", default="session-1")
    parser.add_argument("--lease", type=float, default=5.0)
    parser.add_argument("--step-sleep", type=float, default=0.02)
    parser.add_argument("--crash-at", type=int, default=None)
    args = parser.parse_args()

    store = GoalStore(args.db)
    claimed = 0
    try:
        if args.mode == "group":
            outcome = run_group_session(
                store,
                args.group_session,
                crash_at=args.crash_at,
                step_sleep=args.step_sleep,
            )
            print(f"[{args.owner}] group outcome={outcome}", flush=True)
            return 0

        while True:
            run = store.claim_next(args.owner, args.lease)
            if run is None:
                break
            claimed += 1
            outcome = run_one_task(
                store,
                run,
                owner=args.owner,
                lease_seconds=args.lease,
                step_sleep=args.step_sleep,
                crash_at=args.crash_at,
            )
            print(
                f"[{args.owner}] claimed={run['occurrence_key']} outcome={outcome}",
                flush=True,
            )
            if outcome == "stale_abort":
                break
    finally:
        store.close()
    print(f"[{args.owner}] done, claimed={claimed}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
