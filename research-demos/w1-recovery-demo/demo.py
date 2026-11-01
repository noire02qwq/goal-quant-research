#!/usr/bin/env python3
"""W1 recovery demo 场景编排：三组场景各跑一遍并输出证据。

    python3 demo.py [--workdir /tmp/w1-recovery-demo]

场景 A：双 worker 抢占（原子认领，验证无双写）
场景 B：进程崩溃 → 租约过期 → 恢复扫描 → 幂等续跑（已完成步骤不重跑）
场景 C：群组会话中断 → 从持久化消息恢复（§12.2 W1 群组维度）
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import cast

from goalstore import GoalStore

HERE = Path(__file__).resolve().parent
WORKER = HERE / "worker.py"


def spawn(db: Path, owner: str, *extra: str, lease: float = 3.0) -> subprocess.Popen:
    return subprocess.Popen(
        [sys.executable, str(WORKER), "--db", str(db), "--owner", owner,
         "--lease", str(lease), *extra],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
    )


def drain(procs: list[subprocess.Popen]) -> dict[str, str]:
    out = {}
    for p in procs:
        stdout, _ = p.communicate(timeout=60)
        argv = cast(list[str], p.args)
        owner = argv[argv.index("--owner") + 1]
        out[owner] = (p.returncode, stdout)
    return out


def scenario_a_dual_worker(db: Path, n_tasks: int = 12) -> None:
    print("=== 场景 A：双 worker 抢占 ===")
    store = GoalStore(str(db))
    store.seed_tasks([f"task-{i:02d}" for i in range(n_tasks)])
    store.close()

    p1 = spawn(db, "worker-1", "--step-sleep", "0.03")
    p2 = spawn(db, "worker-2", "--step-sleep", "0.03")
    results = drain([p1, p2])

    store = GoalStore(str(db))
    stats = store.stats()
    store.close()

    succeeded = stats["runs"].get("succeeded", 0)
    # 每个 (exec_key, step) 完成次数必须恰好为 1 → 无重复执行
    dup = [e for e in stats["exec"] if e["outcome"] == "completed" and e["n"] != 1]
    total_claims = sum(
        e["n"] for e in stats["exec"] if e["step_no"] == 1
    )
    w1 = results["worker-1"][1].count("] claimed=")
    w2 = results["worker-2"][1].count("] claimed=")
    print(f"  任务数 {n_tasks}，succeeded {succeeded}，worker-1 认领 {w1}，worker-2 认领 {w2}")
    print(f"  步骤证据条目 {len(stats['exec'])}，重复执行 {len(dup)}")
    assert succeeded == n_tasks, f"期望全部成功，实际 {succeeded}"
    assert not dup, f"出现重复执行: {dup}"
    assert w1 > 0 and w2 > 0, "两个 worker 应都有认领（抢占真实发生）"
    print("  PASS：原子认领下无重复执行，无丢失")


def scenario_b_crash_recovery(db: Path) -> None:
    print("=== 场景 B：进程崩溃 + 恢复扫描 + 幂等续跑 ===")
    store = GoalStore(str(db))
    store.seed_tasks(["task-crash"])
    occ = "task-crash#2026W45"
    store.close()

    # worker 在第 2 步硬崩溃（不写回执、不释放租约）
    p = spawn(db, "crash-worker", "--crash-at", "2", "--step-sleep", "0.05", lease=1.5)
    rc = p.communicate(timeout=30)[0]
    print(f"  崩溃 worker 退出码 {p.returncode}（137=硬退出）")

    store = GoalStore(str(db))
    run = store.get_run(occ)
    assert run["status"] == "running", f"崩溃后应为 running（租约未释放），实际 {run['status']}"
    print(f"  崩溃后状态：{run['status']}，lease 剩余 {run['lease_expires_at'] - time.time():.2f}s")

    # 等租约过期后恢复扫描
    time.sleep(1.6)
    stats = store.recovery_scan()
    run = store.get_run(occ)
    print(f"  恢复扫描：{stats} → 状态 {run['status']}")
    assert stats["requeued"] == 1, f"应重排 1 个，实际 {stats}"
    assert run["status"] == "queued"

    # 恢复 worker 幂等续跑
    p2 = spawn(db, "recovery-worker", "--step-sleep", "0.05")
    p2.communicate(timeout=30)

    store = GoalStore(str(db))
    stats = store.stats()
    run = store.get_run(occ)
    store.close()

    steps = [e for e in stats["exec"] if e["exec_key"] == occ]
    by_step = {}
    for e in steps:
        by_step.setdefault(e["step_no"], []).append((e["outcome"], e["n"]))
    print(f"  最终状态 {run['status']}；步骤执行证据：{by_step}")
    assert run["status"] == "succeeded"
    # 步骤 1 崩溃前已完成 → 恢复后不重跑（completed 恰好 1 次、无新 attempt）
    s1 = by_step[1]
    assert len(s1) == 1 and s1[0] == ("completed", 1), f"步骤1不应重跑: {s1}"
    # 步骤 2 崩溃时 running → 被标 interrupted 后重跑一次 completed
    s2 = dict(by_step[2])
    assert s2.get("interrupted") == 1 and s2.get("completed") == 1, f"步骤2应 interrupted+completed: {s2}"
    # 步骤 3 崩溃后由恢复 worker 完成
    s3 = by_step[3]
    assert len(s3) == 1 and s3[0] == ("completed", 1), f"步骤3不应重复: {s3}"
    print("  PASS：崩溃不隐藏（outcome_unknown→requeue），已完成步骤零重跑，中断步骤重跑一次")


def scenario_c_group_resume(db: Path) -> None:
    print("=== 场景 C：群组会话中断恢复（§12.2 W1）===")
    session = "group-session-1"

    # 群组 worker 在第 4 步崩溃
    p = spawn(db, "group-worker-1", "--mode", "group", "--group-session", session,
              "--crash-at", "4", "--step-sleep", "0.05")
    p.communicate(timeout=30)
    print(f"  群组 worker-1 退出码 {p.returncode}")

    store = GoalStore(str(db))
    msgs = store.messages(session)
    actors = sorted({m["sender_agent_id"] for m in msgs})
    print(f"  崩溃后持久化消息 {len(msgs)} 条，参与者 {actors}")
    assert len(msgs) == 4, f"崩溃前应持久化 4 条消息，实际 {len(msgs)}"
    store.close()

    # 恢复 worker 从持久化消息续跑
    p2 = spawn(db, "group-worker-2", "--mode", "group", "--group-session", session,
               "--step-sleep", "0.05")
    out = p2.communicate(timeout=30)[0]
    print(f"  恢复输出：{out.strip().splitlines()[-1]}")

    store = GoalStore(str(db))
    msgs = store.messages(session)
    seqs = [m["seq"] for m in msgs]
    store.close()
    print(f"  恢复后消息 {len(msgs)} 条，seq={seqs}")
    assert seqs == list(range(1, 7)), f"消息应完整且无重复: {seqs}"
    print("  PASS：中断后从持久化消息恢复，续传无重复、步骤幂等")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workdir", default=None)
    args = parser.parse_args()

    workdir = Path(args.workdir) if args.workdir else Path(tempfile.mkdtemp(prefix="w1-recovery-"))
    workdir.mkdir(parents=True, exist_ok=True)
    try:
        scenario_a_dual_worker(workdir / "a.db")
        scenario_b_crash_recovery(workdir / "b.db")
        scenario_c_group_resume(workdir / "c.db")
        print("\n三组场景全部 PASS")
        return 0
    finally:
        if args.workdir is None:
            shutil.rmtree(workdir, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
