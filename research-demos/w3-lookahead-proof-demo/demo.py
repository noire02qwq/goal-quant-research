#!/usr/bin/env python3.14
"""W3 前视偏差构造性不可能 Demo —— 交互入口。

用法：
    python3.14 demo.py            # 交互菜单（可实际操作入口）
    python3.14 demo.py clean      # 步骤 1：干净回测（双均线）
    python3.14 demo.py leak       # 步骤 2：越界读未来 → 接口层拒绝
    python3.14 demo.py bypass     # 步骤 3：绕过策略 → 双 lint 定罪
    python3.14 demo.py roles      # 步骤 4：assigned_role opt-in 双路径
"""
from __future__ import annotations

import sys

from lookahead_guard import LookaheadViolation, dynamic_audit, static_scan
from lookahead_guard.backtest import oracle_equity, run_backtest
import market
import roles as rolemod
import strategies
from bypass_strategy import BypassRaw

STEP = "=" * 62


def step_clean() -> None:
    print(STEP, "\n[1/4] 干净回测：DualMA 只经窗口视图读数据")
    feed = market.make_feed()
    res = run_backtest(feed, strategies.DualMA())
    dyn = dynamic_audit(feed)
    sta = static_scan("strategies.py")
    print(f"  回测完成：{res.report}")
    print(f"  行为等价复核：access_log {len(feed.access_log)} 条，index≤step 违例 {len(dyn)} 条")
    print(f"  双 lint：动态 {len(dyn)} 发现 / 静态 {len(sta)} 发现 → {'全绿 PASS' if not dyn and not sta else 'FAIL'}")
    print("  指标口径：全部来自 lookahead_guard.metrics（策略不得自写公式，BacktestBench 结论）")


def step_leak() -> None:
    print(STEP, "\n[2/4] 越界读未来：走合法接口也被结构性拒绝")
    feed = market.make_feed()
    try:
        run_backtest(feed, strategies.PeekViaView())
        print("  ✗ 竟然跑通了 —— 构造性保证失效！")
    except LookaheadViolation as e:
        print(f"  ✓ LookaheadViolation：{e}")
    oracle = oracle_equity(market.make_feed())
    from lookahead_guard import metrics
    print(f"  对照：泄露预言机（仅测量侧，不给策略）假想收益 "
          f"{metrics.total_return(oracle):.2%} —— 这就是被接口层挡掉的诱惑量级")


def step_bypass() -> None:
    print(STEP, "\n[3/4] 绕过窗口视图直读原始源：接口不拦，双 lint 定罪")
    feed = market.make_feed()
    run_backtest(feed, BypassRaw(feed))
    dyn = dynamic_audit(feed)
    sta = static_scan("bypass_strategy.py")
    print(f"  动态审计：{len(dyn)} 发现")
    for f in dyn[:3]:
        print(f"    - [{f.kind}] {f.where}：{f.detail}")
    if len(dyn) > 3:
        print(f"    … 另 {len(dyn) - 3} 条")
    print(f"  静态扫描 bypass_strategy.py：{len(sta)} 发现")
    for f in sta:
        print(f"    - [{f.kind}] {f.where}：{f.detail}")
    ok = bool(dyn) and bool(sta)
    print(f"  → {'双层均捕获 PASS' if ok else 'FAIL（漏检）'}")


def step_roles() -> None:
    print(STEP, "\n[4/4] assigned_role opt-in（brief-plan §12.2 W3）")
    t_plain = rolemod.PlanTask("T-101", "跑一次回测")                 # 不填 → 零改动路径
    t_review = rolemod.PlanTask("T-202", "复核策略改动", "reviewer")   # 填了 → 群组约束
    print("  " + rolemod.claim(t_plain, "coder"))
    print("  " + rolemod.claim(t_plain, "reviewer"))
    try:
        rolemod.claim(t_review, "coder")
        print("  ✗ coder 竟然领走了 reviewer 任务")
    except rolemod.RoleBoundaryError as e:
        print(f"  ✓ {e}")
    print("  " + rolemod.claim(t_review, "reviewer"))


STEPS = {"clean": step_clean, "leak": step_leak, "bypass": step_bypass,
         "roles": step_roles}


def main(argv: list[str]) -> int:
    if len(argv) > 1:
        fn = STEPS.get(argv[1])
        if fn is None:
            print(__doc__)
            return 2
        fn()
        return 0
    print("W3 前视偏差构造性不可能 Demo —— 输入 1-4 执行步骤，q 退出")
    menu = {"1": step_clean, "2": step_leak, "3": step_bypass, "4": step_roles}
    while True:
        choice = input("\n步骤 [1]干净回测 [2]越界拒绝 [3]双lint [4]角色路径 (q退出): ").strip().lower()
        if choice in ("q", "quit", "exit"):
            print("bye")
            return 0
        fn = menu.get(choice)
        if fn is None:
            print("无效输入")
            continue
        fn()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
