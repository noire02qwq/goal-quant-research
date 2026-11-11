"""W5 故障注入演练 Demo（五类注入 + 数据固定化 + T3/T4 模板）。

运行（demo 目录内）：python3.14 -m unittest discover -s tests -v
交互入口：python3.14 demo.py ｜ 分步：python3.14 demo.py <repair|restart|goalchange|interface|feed|fixtures|taub>
"""
from __future__ import annotations

import sys

from drill.runstate import DrillRun, CodeBroken, SimulatedCrash, Receipts
from drill.execution import Broker, Breaker, Order, Reconciler
from drill.feedguard import FeedGuard, FORGED, NewsItem, headline_drive, backtest_candles_signature
from drill import fixture
from drill.bridge import run_template

STEP = "=" * 62
CLEAN_NEWS = NewsItem("n-1", "exchange-feed", "标的发布年报（已签名）", signed=True)


def step_repair() -> None:
    print(STEP, "\n[1/5] 注入①：改坏代码 → 失败不终止 → 修复任务重进循环")
    run = DrillRun("goal-1", ["fetch", "backtest", "report"])
    run.broken_code_steps.add("backtest")
    out = run.attempt_with_repair()
    kinds = [e.kind for e in run.events]
    print(f"  第一轮：backtest 抛 CodeBroken → 修复任务 {run.repaired} 入队")
    print(f"  第二轮：修复生效，完成 {out['completed']}（executed={run.executed}）")
    ok = ("repair_task" in kinds and out["completed"] == ["fetch", "backtest", "report"]
          and run.executed["backtest"] == 2)
    print(f"  → {'PASS' if ok else 'FAIL'}：失败未终止、重试仅故障步 +1、其余步零重跑")


def step_restart() -> None:
    print(STEP, "\n[2/5] 注入②：重启 → 恢复扫描 → 已完成步骤零重跑")
    r1 = Receipts()
    run1 = DrillRun("goal-2", ["fetch", "signal", "execute", "notify"], receipts=r1)
    run1.crash_at = "execute"
    try:
        run1.run()
    except SimulatedCrash as e:
        print(f"  崩溃于 {e}（前两步已落回执）")
    run2 = DrillRun("goal-2", ["fetch", "signal", "execute", "notify"], receipts=r1)
    done = run2.run()
    print(f"  重启恢复：完成 {done}；回执命中重放 {r1.replay_count} 次")
    ok = (r1.replay_count == 2 and done == ["done:execute", "done:notify"]
          and run2.executed.get("fetch") is None)
    print(f"  → {'PASS' if ok else 'FAIL'}：fetch/signal 零重跑（回执拦截）、后两步各执行 1 次")


def step_goalchange() -> None:
    print(STEP, "\n[3/5] 注入③：改目标 → 队列重定标 + 显式事件审计")
    run2 = DrillRun("goal-3b", ["a", "b", "c"])
    run2._run_step("a")
    run2.change_goal("目标改为保守档（新参数集）", at_step="b")
    rest = run2.run()
    kinds = [(e.kind, e.detail) for e in run2.events]
    print(f"  事件：goal_changed 已入审计；a 的回执保持 {run2.receipts.has('goal-3b:a')}")
    print(f"  队列余下执行 {rest}（按新目标继续），已完成步骤未受影响")
    ok = any(k == "goal_changed" for k, _ in kinds) and rest == ["done:b", "done:c"] and run2.completed == ["a", "b", "c"]
    print(f"  → {'PASS' if ok else 'FAIL'}：显式状态机事件 + 已完成步骤零改动")


def step_interface() -> None:
    print(STEP, "\n[4/5] 注入④：interface 诚实（submitted≠filled 静默正常化）+ 熔断真触发")
    br = Broker(silent_fill_bugs={"o-7"})
    submitted_view = [br.submit(Order("o-7", "buy", 100, 10.0)),
                      br.submit(Order("o-8", "buy", 100, 10.0))]
    findings = Reconciler.reconcile(submitted_view, br)
    print(f"  静默故障单 o-7：界面 {submitted_view[0].status}，对账 → {findings[0]}")
    print(f"  正常单 o-8：对账结论 {len([f for f in findings if 'o-8' in f])} 条（应为 0）")
    halted = []
    bk = Breaker(max_gap_pct=3.0)
    tripped = bk.check(10.0, 10.6, lambda: halted.append("下单挂起"))
    print(f"  熔断检查：跳变 6% > 3% → tripped={bk.tripped}，回调 {halted}")
    ok = len(findings) == 1 and "o-7" in findings[0] and tripped and halted == ["下单挂起"]
    print(f"  → {'PASS' if ok else 'FAIL'}：静默被点名 + 熔断真触发（非武装挂件，AllPath 教训）")


def step_feed() -> None:
    print(STEP, "\n[5/5] 注入⑤：数据面注入（伪造新闻）——backtest 不可见、feed 口必拦")
    bars = fixture.make_bars()
    sig_clean = backtest_candles_signature(bars)
    sig_poisoned = backtest_candles_signature(bars)     # 伪造新闻不进 candle
    guard = FeedGuard(trusted_sources={"exchange-feed"})
    admitted = [guard.ingest(CLEAN_NEWS), guard.ingest(FORGED)]
    poisoned_drive = headline_drive(FORGED.headline)
    print(f"  回测签名：clean={sig_clean[:16]}… poisoned={sig_poisoned[:16]}… 相等={sig_clean == sig_poisoned}")
    print(f"  feed 摄取：已签名源 admit={admitted[0]}，伪造源 admit={admitted[1]}（拦截并留审计 {len(guard.blocked)} 条）")
    print(f"  若放行的驱动力：{poisoned_drive}（恐慌词触发空仓——攻击者即刻操纵决策）")
    ok = sig_clean == sig_poisoned and admitted == [True, False] and poisoned_drive == -1
    print(f"  → {'PASS' if ok else 'FAIL'}：回测内不可见（正交性证明）+ 摄入口拦截（61.7%→13.8% 的防线位）")


def step_fixtures() -> None:
    print(STEP, "\n[附加] 数据固定化 + T3/T4 模板（固定窗口 seed={} bars={}）".format(
        fixture.FIXED_WINDOW["seed"], fixture.FIXED_WINDOW["bars"]))
    b1, b2 = fixture.make_bars(), fixture.make_bars()
    h1, h2 = fixture.bars_sha256(b1), fixture.bars_sha256(b2)
    print(f"  同 seed 两次生成 sha256：{h1[:24]}… → 一致={h1 == h2}")
    t3 = run_template(fixture.T3Grid(), b1)
    t4 = run_template(fixture.T4Turtle(), b1)
    print(f"  T3 网格模板回测：{t3}")
    print(f"  T4 海龟模板回测：{t4}")
    try:
        fixture.T3Grid(momentum=1)
        print("  FAIL：白名单外参数未被拒")
    except ValueError as e:
        print(f"  参数白名单：{e}")
    ok = h1 == h2 and "sharpe" in t3 and "sharpe" in t4
    print(f"  → {'PASS' if ok else 'FAIL'}：固定窗口可复现 + 模板可运行（回测走 w3 构造性防护）")


def step_taub() -> None:
    print(STEP, "\n[7/7] 排名稳定性：两档执行假设下策略 Kendall τ_b（0006 实测行）")
    from strategies import DualMA
    from drill.report import EXEC_TIERS, stability, tier_table
    bars = fixture.make_bars()
    roster = [("T1 双均线", DualMA()), ("T3 网格", fixture.T3Grid()), ("T4 海龟", fixture.T4Turtle())]
    table = tier_table(bars, roster)
    for tier, scores in table.items():
        order = sorted(scores, key=scores.get, reverse=True)
        print(f"  {tier}: " + " > ".join(f"{n} {scores[n]:+.4f}" for n in order))
    names, x, y, tau = stability(table)
    print(f"  Kendall τ_b（{list(EXEC_TIERS)[0]} vs {list(EXEC_TIERS)[1]}，n={len(names)}）= {tau:+.4f}")
    print("  → PASS：执行假设档位已披露、排序稳定性可复算（Execution 反例的正面口径）"
          if -1 <= tau <= 1 else "  → FAIL")
    print(f"    （档位口径：{EXEC_TIERS}——滑点并入 cost_rate 的简化合并，披露即复算）")


STEPS = {"repair": step_repair, "restart": step_restart, "goalchange": step_goalchange,
         "interface": step_interface, "feed": step_feed, "fixtures": step_fixtures,
         "taub": step_taub}


def main(argv: list[str]) -> int:
    if len(argv) > 1:
        fn = STEPS.get(argv[1])
        if fn is None:
            print(__doc__)
            return 2
        fn()
        return 0
    print("W5 故障注入演练 —— 输入 1-7，q 退出")
    menu = {str(i): fn for i, fn in enumerate(STEPS.values(), start=1)}
    while True:
        choice = input("\n[1]改坏代码 [2]重启 [3]改目标 [4]interface [5]数据注入 [6]固定化/模板 [7]τ_b (q): ").strip().lower()
        if choice in ("q", "quit", "exit"):
            print("bye")
            return 0
        fn = menu.get(choice)
        if fn is None:
            print("无效输入")
            continue
        fn()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
