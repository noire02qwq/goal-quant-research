import { StatusBar } from "expo-status-bar";
import { useCallback, useEffect, useState } from "react";
import {
  Button,
  Pressable,
  ScrollView,
  StyleSheet,
  Switch,
  Text,
  TextInput,
  View,
} from "react-native";

const API = "http://127.0.0.1:8777";

type Card = {
  card_id: string;
  goal: string;
  initial_conditions: string;
  strategy_outline: string;
  lifecycle: string;
  scope: string;
  reproduction_count: number;
  avg_utility: number;
  causal_consistency: number;
  retrieval_coverage: number;
  superseded_by: string | null;
  valid_until: number | null;
  score: number;
};

type Check = {
  gate: string;
  pass: boolean;
  rule: string;
  actual?: number;
  sub?: { rule: string; actual: number | string; pass: boolean }[];
};

type State = {
  python: string;
  gates: Record<string, boolean>;
  cards: Card[];
  context: {
    budget: number;
    used_tokens: number;
    included: { card_id: string; lifecycle: string; score: number; tokens: number }[];
    evicted: { card_id: string; score: number; tokens: number; reason: string }[];
    excluded: { card_id: string; lifecycle: string; reason: string }[];
  };
  events: { seq: number; card_id: string | null; kind: string; detail: string; ts: number }[];
};

const LIFECOLOR: Record<string, string> = {
  CANDIDATE: "#8a8f98",
  ACTIVE: "#2f9e44",
  STABLE: "#1971c2",
  SUPERSEDED: "#e8590c",
  STALE: "#f08c00",
  ARCHIVED: "#868e96",
};

async function post<T>(path: string, body?: unknown): Promise<T> {
  const r = await fetch(API + path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body ?? {}),
  });
  return (await r.json()) as T;
}

export default function App() {
  const [st, setSt] = useState<State | null>(null);
  const [budget, setBudget] = useState("16384");
  const [notice, setNotice] = useState("");
  const [form, setForm] = useState({
    goal: "",
    initial_conditions: "",
    strategy_outline: "",
    reproduction_count: "0",
    avg_utility: "0",
    causal_consistency: "0",
    retrieval_coverage: "0",
    valid_in_seconds: "",
  });

  const refresh = useCallback(async (b?: string) => {
    const q = b ? `?budget=${encodeURIComponent(b)}` : "";
    const r = await fetch(`${API}/api/state${q}`);
    setSt((await r.json()) as State);
  }, []);

  useEffect(() => {
    refresh().catch(() => setNotice("后端未启动：先运行 python3 server.py"));
    const t = setInterval(() => refresh(budget).catch(() => {}), 3000);
    return () => clearInterval(t);
  }, [refresh, budget]);

  const run = async (fn: () => Promise<unknown>, msg: string) => {
    try {
      await fn();
      await refresh(budget);
      setNotice(msg);
    } catch (e) {
      setNotice(`出错: ${e}`);
    }
  };

  if (!st) {
    return (
      <View style={styles.loading}>
        <Text style={styles.h1}>连接后端 {API} …</Text>
        <Text style={styles.dim}>python3 server.py</Text>
      </View>
    );
  }

  const ctx = st.context;

  return (
    <ScrollView style={styles.page} contentContainerStyle={{ paddingBottom: 48 }}>
      <StatusBar style="auto" />
      <Text style={styles.h1}>W2 记忆蒸馏 · 晋升 gate 与生命周期</Text>
      <Text style={styles.dim}>
        Python {st.python} · 预算 {ctx.budget} tok · 已用 {ctx.used_tokens} tok
      </Text>
      {notice ? <Text style={styles.notice}>▸ {notice}</Text> : null}

      {/* ── gate 开关：论文消融入口 ── */}
      <View style={styles.card}>
        <Text style={styles.h2}>① 晋升 gate（关掉 = 复现论文消融）</Text>
        {Object.entries(st.gates).map(([k, v]) => (
          <View key={k} style={styles.row}>
            <Switch
              value={v}
              onValueChange={(nv) =>
                run(() => post("/api/gates", { [k]: nv }), `gate ${k} → ${nv}`)
              }
            />
            <Text style={styles.label}>
              {k === "coverage"
                ? "coverage 前置过滤（HaMo：retrieval_coverage ≥ 0.30）"
                : "reproduction 主 gate（SEPM：≥1 复现 + 效用≥0 + 因果≥0.65）"}
            </Text>
          </View>
        ))}
        {!st.gates.reproduction && (
          <Text style={styles.warn}>
            ⚠ reproduction gate 已关（消融）：污染卡不再被主 gate 拦截；若 coverage 也关则完全放行
          </Text>
        )}
        {!st.gates.coverage && !st.gates.reproduction && (
          <Text style={styles.warn}>
            ⚠ 全消融：污染经验卡将放行进入上下文——观察下面 turn_context 被稀释
          </Text>
        )}
      </View>

      {/* ── 经验卡 + 逐卡评估 ── */}
      <View style={styles.card}>
        <Text style={styles.h2}>② 经验卡生命周期（点「评估」触发 gate）</Text>
        {st.cards.map((c) => (
          <View key={c.card_id} style={styles.cardRow}>
            <View style={{ flex: 1 }}>
              <View style={styles.row}>
                <View style={[styles.badge, { backgroundColor: LIFECOLOR[c.lifecycle] }]}>
                  <Text style={styles.badgeText}>{c.lifecycle}</Text>
                </View>
                <Text style={styles.cardId}>{c.card_id}</Text>
                {c.superseded_by ? <Text style={styles.dim}> → {c.superseded_by}</Text> : null}
              </View>
              <Text style={styles.goal}>{c.goal}</Text>
              <Text style={styles.dim}>初始: {c.initial_conditions}</Text>
              <Text style={styles.dim}>策略: {c.strategy_outline}</Text>
              <Text style={styles.metrics}>
                复现 {c.reproduction_count} · 效用 {c.avg_utility} · 因果{" "}
                {c.causal_consistency} · coverage {c.retrieval_coverage} · 分 {c.score}
                {c.valid_until
                  ? ` · TTL 剩 ${Math.max(0, Math.round(c.valid_until - Date.now() / 1000))}s`
                  : ""}
              </Text>
            </View>
            <View style={{ width: 96 }}>
              <Button
                title="评估"
                onPress={() =>
                  run(async () => {
                    const r = (await post(`/api/evaluate/${c.card_id}`)) as {
                      result: { pass: boolean; checks: Check[]; note?: string };
                    };
                    const lines = r.result.checks.map((ck) =>
                      `${ck.pass ? "✓" : "✗"} ${ck.gate}` +
                        (ck.sub
                          ? "（" +
                            ck.sub
                              .map((s) => `${s.pass ? "✓" : "✗"} ${s.rule}=${s.actual}`)
                              .join("，") +
                            "）"
                          : `（${ck.rule}，实际 ${ck.actual}）`),
                    );
                    setNotice(
                      `${c.card_id} gate ${r.result.pass ? "通过" : "拦截"}：${lines.join("；")}` +
                        (r.result.note ? `；${r.result.note}` : ""),
                    );
                  }, `已评估 ${c.card_id}`)
                }
              />
            </View>
          </View>
        ))}
      </View>

      {/* ── supersede / TTL ── */}
      <View style={styles.card}>
        <Text style={styles.h2}>③ supersede 与 TTL（不删除语义）</Text>
        <View style={styles.row}>
          <Button
            title="supersede 第1张→第3张"
            onPress={() =>
              run(
                () =>
                  post("/api/supersede", {
                    old_card_id: st.cards[0]?.card_id,
                    new_card_id: st.cards[2]?.card_id,
                  }),
                "旧卡置 SUPERSEDED + 指针，行仍可查（历史回放）",
              )
            }
          />
          <Button
            title="触发 TTL 扫描"
            onPress={() =>
              run(async () => {
                const r = (await post("/api/expire")) as { expired: string[] };
                setNotice(
                  r.expired.length
                    ? `过期命中 ${r.expired.join(",")} → STALE（不删除，退出上下文）`
                    : "无到期卡（第3张 15s TTL，等它到期再点）",
                );
              }, "TTL 扫描完成")
            }
          />
        </View>
        <Text style={styles.dim}>
          supersede 后旧卡 lifecycle=SUPERSEDED、superseded_by 指向新卡，仍可读取——历史回放需要它重构当时决策。
        </Text>
      </View>

      {/* ── turn_context 组装 ── */}
      <View style={styles.card}>
        <Text style={styles.h2}>④ turn_context 组装（gate 先于 packing）</Text>
        <View style={styles.row}>
          <TextInput
            style={styles.input}
            value={budget}
            onChangeText={setBudget}
            keyboardType="number-pad"
            placeholder="预算 tokens"
          />
          <Button title="按预算重组" onPress={() => run(() => refresh(budget), "已重组")} />
        </View>
        <Text style={styles.sub}>✓ 装入（{ctx.included.length}）</Text>
        {ctx.included.map((x) => (
          <Text key={x.card_id} style={styles.ok}>
            {x.card_id} · {x.lifecycle} · 分 {x.score} · {x.tokens} tok
          </Text>
        ))}
        <Text style={styles.sub}>↕ 挤出（{ctx.evicted.length}）</Text>
        {ctx.evicted.map((x) => (
          <Text key={x.card_id} style={styles.warn}>
            {x.card_id} · 分 {x.score} · {x.tokens} tok — {x.reason}
          </Text>
        ))}
        <Text style={styles.sub}>✗ 硬过滤（{ctx.excluded.length}）</Text>
        {ctx.excluded.map((x) => (
          <Text key={x.card_id} style={styles.dim}>
            {x.card_id} · {x.lifecycle} — {x.reason}
          </Text>
        ))}
        {ctx.included.length + ctx.evicted.length + ctx.excluded.length === 0 && (
          <Text style={styles.dim}>暂无卡片</Text>
        )}
      </View>

      {/* ── 新建经验卡 ── */}
      <View style={styles.card}>
        <Text style={styles.h2}>⑤ 新建经验卡（HaMo 三元组 + 判据输入）</Text>
        {(
          [
            ["goal", "goal（目标）"],
            ["initial_conditions", "初始条件"],
            ["strategy_outline", "策略大纲"],
          ] as const
        ).map(([k, ph]) => (
          <TextInput
            key={k}
            style={styles.inputFull}
            placeholder={ph}
            value={form[k]}
            onChangeText={(v) => setForm((f) => ({ ...f, [k]: v }))}
          />
        ))}
        <View style={styles.row}>
          {(
            [
              ["reproduction_count", "复现"],
              ["avg_utility", "效用"],
              ["causal_consistency", "因果"],
              ["retrieval_coverage", "cov"],
              ["valid_in_seconds", "TTL秒"],
            ] as const
          ).map(([k, ph]) => (
            <TextInput
              key={k}
              style={styles.inputSmall}
              placeholder={ph}
              keyboardType="numeric"
              value={form[k]}
              onChangeText={(v) => setForm((f) => ({ ...f, [k]: v }))}
            />
          ))}
        </View>
        <View style={styles.row}>
          <Button
            title="创建（入池为 CANDIDATE）"
            onPress={() =>
              run(
                () =>
                  post("/api/cards", {
                    ...form,
                    reproduction_count: Number(form.reproduction_count) || 0,
                    avg_utility: Number(form.avg_utility) || 0,
                    causal_consistency: Number(form.causal_consistency) || 0,
                    retrieval_coverage: Number(form.retrieval_coverage) || 0,
                    valid_in_seconds: form.valid_in_seconds
                      ? Number(form.valid_in_seconds)
                      : null,
                  }),
                "新卡入池为 CANDIDATE，点「评估」才可能进上下文",
              )
            }
          />
          <Button
            title="放一张污染卡"
            onPress={() =>
              run(
                () =>
                  post("/api/cards", {
                    goal: "污染经验：无止损追单",
                    initial_conditions: "任意行情，无复现",
                    strategy_outline: "1. 信号即满仓 2. 不止损 3. 亏损加倍",
                    reproduction_count: 0,
                    avg_utility: -0.9,
                    causal_consistency: 0.05,
                    retrieval_coverage: 0.05,
                  }),
                "污染卡已入池——gate 开着点评估应被拦截；两个 gate 都关再评估则放行",
              )
            }
          />
        </View>
      </View>

      {/* ── 事件日志 ── */}
      <View style={styles.card}>
        <Text style={styles.h2}>⑥ 事件日志（goal_event 风格审计流）</Text>
        {[...st.events].reverse().map((e) => (
          <Text key={e.seq} style={styles.log}>
            #{e.seq} [{e.kind}] {e.card_id ?? "-"} — {e.detail}
          </Text>
        ))}
      </View>

      <Pressable onPress={() => refresh(budget)} style={styles.refresh}>
        <Text style={styles.badgeText}>刷新</Text>
      </Pressable>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  page: { flex: 1, backgroundColor: "#f6f7f9", padding: 14 },
  loading: { flex: 1, alignItems: "center", justifyContent: "center", backgroundColor: "#f6f7f9" },
  h1: { fontSize: 19, fontWeight: "700", color: "#1a1d21", marginBottom: 2 },
  h2: { fontSize: 15, fontWeight: "700", color: "#1a1d21", marginBottom: 8 },
  sub: { fontSize: 13, fontWeight: "600", color: "#495057", marginTop: 8, marginBottom: 2 },
  dim: { fontSize: 12, color: "#868e96", marginBottom: 2 },
  notice: { fontSize: 13, color: "#1971c2", marginVertical: 6 },
  card: {
    backgroundColor: "#fff",
    borderRadius: 10,
    padding: 12,
    marginTop: 12,
    borderWidth: 1,
    borderColor: "#e9ecef",
  },
  cardRow: {
    flexDirection: "row",
    paddingVertical: 8,
    borderTopWidth: 1,
    borderTopColor: "#f1f3f5",
  },
  row: { flexDirection: "row", alignItems: "center", gap: 8, marginVertical: 4, flexWrap: "wrap" },
  label: { flex: 1, fontSize: 13, color: "#343a40" },
  badge: { borderRadius: 4, paddingHorizontal: 6, paddingVertical: 2, marginRight: 6 },
  badgeText: { color: "#fff", fontSize: 11, fontWeight: "700" },
  cardId: { fontSize: 12, color: "#868e96", fontFamily: "Menlo" },
  goal: { fontSize: 14, fontWeight: "600", color: "#212529", marginTop: 4 },
  metrics: { fontSize: 12, color: "#495057", marginTop: 4 },
  ok: { fontSize: 12, color: "#2f9e44", marginTop: 2 },
  warn: { fontSize: 12, color: "#e8590c", marginTop: 4 },
  log: { fontSize: 11, color: "#495057", fontFamily: "Menlo", marginTop: 2 },
  input: {
    borderWidth: 1,
    borderColor: "#dee2e6",
    borderRadius: 6,
    paddingHorizontal: 8,
    paddingVertical: 6,
    width: 120,
    fontSize: 13,
    backgroundColor: "#fff",
  },
  inputFull: {
    borderWidth: 1,
    borderColor: "#dee2e6",
    borderRadius: 6,
    paddingHorizontal: 8,
    paddingVertical: 7,
    fontSize: 13,
    marginBottom: 6,
    backgroundColor: "#fff",
  },
  inputSmall: {
    borderWidth: 1,
    borderColor: "#dee2e6",
    borderRadius: 6,
    paddingHorizontal: 6,
    paddingVertical: 6,
    fontSize: 12,
    width: 74,
    backgroundColor: "#fff",
  },
  refresh: {
    backgroundColor: "#1971c2",
    borderRadius: 8,
    padding: 10,
    alignItems: "center",
    marginTop: 16,
    marginHorizontal: 40,
  },
});
