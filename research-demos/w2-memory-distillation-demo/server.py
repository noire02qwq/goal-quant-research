#!/usr/bin/env python3
"""W2 记忆蒸馏 demo 交互后端（Python 3.14 标准库，零第三方依赖）。

启动: python3 server.py   （默认 http://127.0.0.1:8777）
前端: ../frontend 下 npx expo start --web（React Native / Expo，无 Electron）
"""
from __future__ import annotations

import json
import os
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import context as ctx
import gate
import memstore

BASE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE, "w2_memory.db")

store = memstore.MemoryStore(DB_PATH)
gates = dict(gate.DEFAULT_GATES)
lock = threading.Lock()

SEED = [
    dict(goal="T1 双均线：金叉买入信号过滤",
         initial_conditions="上证日线 2020-2024，均线 5/20，含手续费",
         strategy_outline="1. 双均线交叉生成信号 2. 用成交量过滤假金叉 3. 止损 8%",
         reproduction_count=2, avg_utility=0.42, causal_consistency=0.81,
         retrieval_coverage=0.65, valid_in_seconds=None),
    dict(goal="T1 双均线：追涨强势股",
         initial_conditions="任意行情，无过滤条件",
         strategy_outline="1. 金叉即满仓 2. 不设止损 3. 亏损后加倍",
         reproduction_count=0, avg_utility=-0.35, causal_consistency=0.12,
         retrieval_coverage=0.08, valid_in_seconds=None),
    dict(goal="T1 双均线：财报季参数微调",
         initial_conditions="2026Q3 财报窗口，窗口内有效",
         strategy_outline="1. 财报窗口内缩短均线至 3/10 2. 窗口结束后失效",
         reproduction_count=1, avg_utility=0.30, causal_consistency=0.70,
         retrieval_coverage=0.55, valid_in_seconds=15),
]


def seed_if_empty() -> None:
    if store.list_cards():
        return
    for s in SEED:
        store.add_card(**s)
    store.record(None, "seed", f"预置 {len(SEED)} 张经验卡（含 1 张待 gate 拦截的污染卡、1 张 15s TTL 卡）")


def public_card(c: dict) -> dict:
    return dict(c, score=ctx.score(c, time.time()))


def state_payload(budget: int = ctx.BUDGET_DEFAULT) -> dict:
    cards = store.list_cards()
    return {
        "python": f"{sys.version_info.major}.{sys.version_info.minor}",
        "gates": gates,
        "cards": [public_card(c) for c in cards],
        "context": ctx.assemble(cards, budget=budget, now=time.time()),
        "events": store.events(limit=60),
    }


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):  # 静默访问日志
        pass

    # ---------- 基础 ----------

    def _send(self, code: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()
        self.wfile.write(body)

    def _body(self) -> dict:
        n = int(self.headers.get("Content-Length") or 0)
        if not n:
            return {}
        return json.loads(self.rfile.read(n).decode() or "{}")

    def do_OPTIONS(self):
        self._send(204, {})

    def do_GET(self):
        if self.path.startswith("/api/state"):
            budget = ctx.BUDGET_DEFAULT
            if "budget=" in self.path:
                try:
                    budget = int(self.path.split("budget=")[1].split("&")[0])
                except ValueError:
                    pass
            with lock:
                self._send(200, state_payload(budget))
        else:
            self._send(404, {"error": "not found"})

    def do_POST(self):
        try:
            self._route(self._body())
        except (memstore.InvalidTransition, KeyError, ValueError) as e:
            self._send(400, {"error": str(e)})
        except Exception as e:  # noqa: BLE001 — demo 服务器兜底
            self._send(500, {"error": f"{type(e).__name__}: {e}"})

    # ---------- 路由 ----------

    def _route(self, b: dict) -> None:
        p = self.path
        with lock:
            if p == "/api/cards":
                cid = store.add_card(
                    goal=b.get("goal", ""), initial_conditions=b.get("initial_conditions", ""),
                    strategy_outline=b.get("strategy_outline", ""),
                    scope=b.get("scope", "shared"), author_agent_id=b.get("author_agent_id"),
                    reproduction_count=int(b.get("reproduction_count", 0)),
                    avg_utility=float(b.get("avg_utility", 0.0)),
                    causal_consistency=float(b.get("causal_consistency", 0.0)),
                    retrieval_coverage=float(b.get("retrieval_coverage", 0.0)),
                    valid_in_seconds=b.get("valid_in_seconds"))
                self._send(200, {"card_id": cid, **state_payload()})

            elif p == "/api/gates":
                gates.update({k: bool(v) for k, v in b.items() if k in gate.DEFAULT_GATES})
                store.record(None, "gates_changed", f"gate 开关 → {gates}"
                             + ("（消融模式：污染卡将放行）" if not gates["reproduction"] else ""))
                self._send(200, state_payload())

            elif p.startswith("/api/evaluate/"):
                cid = p.rsplit("/", 1)[1]
                card = store.get_card(cid)
                if card is None:
                    raise KeyError(cid)
                res = gate.evaluate(dict(card), gates)
                if res["pass"]:
                    if card["lifecycle"] == "CANDIDATE":
                        store.transition(cid, "ACTIVE", "gate_passed",
                                         "gate 通过 → ACTIVE（进入 turn_context 候选）")
                    elif card["lifecycle"] == "ACTIVE" and card["reproduction_count"] >= 2:
                        store.transition(cid, "STABLE", "stabilized",
                                         "复现 ≥2 次且 gate 通过 → STABLE（得分加成）")
                    elif card["lifecycle"] in ("STALE", "SUPERSEDED"):
                        res["note"] = "已过期/已被替代的卡不再回到上下文（历史回放可读）"
                else:
                    store.record(cid, "gate_blocked",
                                 "gate 拦截：" + "；".join(
                                     f"{c['gate']} 不通过" for c in res["checks"] if not c["pass"]))
                self._send(200, {"result": res, **state_payload()})

            elif p == "/api/metrics":
                cid = b.pop("card_id")
                store.update_metrics(cid, **{k: float(v) for k, v in b.items()})
                self._send(200, state_payload())

            elif p == "/api/supersede":
                store.supersede(b["old_card_id"], b["new_card_id"])
                self._send(200, state_payload())

            elif p == "/api/expire":
                hit = store.expire_due()
                self._send(200, {"expired": hit, **state_payload()})

            elif p == "/api/context":
                self._send(200, state_payload(budget=int(b.get("budget", ctx.BUDGET_DEFAULT))))

            else:
                self._send(404, {"error": "not found"})


def main() -> None:
    seed_if_empty()
    port = int(os.environ.get("W2_PORT", "8777"))
    print(f"[w2-demo] Python {sys.version.split()[0]} | sqlite {memstore.sqlite3.sqlite_version}"
          f" | http://127.0.0.1:{port}")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()


if __name__ == "__main__":
    main()
