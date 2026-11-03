# OpenMuse（CopilotKit/openmuse）源码走读笔记

- **状态**：已完成源码走读；对 brief-plan §3 主表四条二手映射逐条给出判定（见 §2）。
- **走读日期**：2026-11-03
- **走读对象**：本地克隆仓库 `~/agent-studio/goal-quant-research/oss-repos/openmuse`，HEAD = `a4944f4c471d3dc93b8bfc060b5da309b5216ab2`（commit 时间 2026-10-26，`fix: keep surrogate numeric character references from failing the mail list (#183)`）。
- **链接约定**：所有源码引用给仓库内路径 + `https://github.com/CopilotKit/openmuse/blob/main/<path>`。⚠️ 链接指向 GitHub `main` 分支，本次走读**只读了本地 clone**，未联网核对 main 是否与本地 HEAD 一致（境外通道状态见 brief-plan §3.1），两者若有差异以本地 commit 为准——此为本笔记主要不确定项之一。

## 1. 精读范围

**已精读（逐行）**

- 存储层：[`apps/server/src/db.ts`](https://github.com/CopilotKit/openmuse/blob/main/apps/server/src/db.ts)（单表 `records(owner,kind,id,data jsonb,updated_at)`、`compareAndSwap`、`insertIfAbsent`、`claim`、`recoverInterruptedActions`）
- 任务执行内核：[`apps/server/src/engine/worker.ts`](https://github.com/CopilotKit/openmuse/blob/main/apps/server/src/engine/worker.ts)（TaskWorker：poll/认领/租约/心跳/guard/checkpoint/中断处理）、[`apps/server/src/engine/service.ts`](https://github.com/CopilotKit/openmuse/blob/main/apps/server/src/engine/service.ts)（1209 行全读：任务/目标/监控/告警/审批编排/维护循环）、[`apps/server/src/engine/model.ts`](https://github.com/CopilotKit/openmuse/blob/main/apps/server/src/engine/model.ts)（模型任务执行、工具幂等缓存、重试边界）、[`apps/server/src/engine/routes.ts`](https://github.com/CopilotKit/openmuse/blob/main/apps/server/src/engine/routes.ts)
- 审批与外部写：[`apps/server/src/actions.ts`](https://github.com/CopilotKit/openmuse/blob/main/apps/server/src/actions.ts)（ActionService：propose/decide/claim/outcome_unknown）
- 计算机（Linux 容器）租约与回执：[`apps/server/src/computer.ts`](https://github.com/CopilotKit/openmuse/blob/main/apps/server/src/computer.ts) 第 180–619 行（`Lease` 状态机、命令回执、中断/超时/stale-executor fencing）
- 浏览器 worker 与 profile 持久化：[`apps/worker/src/browser.ts`](https://github.com/CopilotKit/openmuse/blob/main/apps/worker/src/browser.ts)（全读）
- 领域模型：[`packages/domain/src/agent.ts`](https://github.com/CopilotKit/openmuse/blob/main/packages/domain/src/agent.ts)（TaskStatus/AgentTask/Monitor/Goal/RunEvent）、[`apps/server/src/config.ts`](https://github.com/CopilotKit/openmuse/blob/main/apps/server/src/config.ts)（`MODEL_MAX_RETRIES` 注释块）
- 定点测试：[`tests/engine.test.ts`](https://github.com/CopilotKit/openmuse/blob/main/tests/engine.test.ts)、[`tests/persistence.test.ts`](https://github.com/CopilotKit/openmuse/blob/main/tests/persistence.test.ts)、[`tests/model-retry.test.ts`](https://github.com/CopilotKit/openmuse/blob/main/tests/model-retry.test.ts)、[`tests/prepare-lease-loss.test.ts`](https://github.com/CopilotKit/openmuse/blob/main/tests/prepare-lease-loss.test.ts)
- 文档关键段：`README.md`、`ROADMAP.md`、`docs/VERIFICATION.md`、`docs/FEATURES.md`、`docs/COMPUTER.md`、`docs/WORKER`（`apps/worker/README.md`）、`SECURITY.md`（grep 定位后读命中段落）

**未精读（明确列出）**

- `apps/mobile/**`（仅 grep `waiting_approval`/`notifications`/`monitor` 看消费侧，未读实现）
- `apps/server/src/` 其余：`agent.ts`、`app.ts`、`auth.ts`、`browser.ts`、`computer-backend.ts`、`computer-e2b-desktop.ts`、`files.ts`、`workspace.ts`、`search.ts`、`rate-limit.ts`、`jev/**`、`engine/conversation.ts`、`engine/finance.ts`、`engine/page-diff.ts`、`engine/tanstack-agent.ts`
- `apps/server/src/computer.ts` 第 1–179 行与 620 行之后（Docker/E2B 后端细节、桌面截图）
- `apps/worker/src/` 除 `browser.ts` 外（`server.ts`、`downloads.ts`、`proxy.ts`、`network.ts` 等）
- `packages/integrations/**`（只读了 `google.ts` 中 `OutcomeUnknownError` 定义片段）、`packages/backends/openbot.ts`
- `tests/` 大部分（如 `monitor-recovery.test.ts` 830 行、`workflows.test.ts`、`computer.test.ts` 只 grep 到测试名，未逐行读）
- `docs/` 其余、`infra/`、`.github/`

## 2. brief-plan §3 四条二手映射的逐条判定

### ① "SQL lease 协调多 worker 并恢复被中断任务" —— **源码证实**

**证据**

- 认领即带条件的 CAS：TaskWorker `run()` 用 `compareAndSwap(owner,"tasks",id, expected={status, leaseId, (running 时) leaseUntil}, patch={status:"running", leaseId:randomUUID(), leaseUntil:now+60s, attempts+1})`；`compareAndSwap` 的 SQL 是 `UPDATE ... WHERE data @> $expected`（jsonb 包含匹配），失败返回 null 即认领不到——见 [`apps/server/src/engine/worker.ts:124-140`](https://github.com/CopilotKit/openmuse/blob/main/apps/server/src/engine/worker.ts#L124) 与 [`apps/server/src/db.ts:93-105`](https://github.com/CopilotKit/openmuse/blob/main/apps/server/src/db.ts#L93)。
- 租约心跳：每 `leaseMs/3`（≥10ms，leaseMs 默认 60000）刷新 `leaseUntil`，CAS 期望 `{leaseId, status:"running"}`，刷不上即 `controller.abort()`（[`worker.ts:174-190`](https://github.com/CopilotKit/openmuse/blob/main/apps/server/src/engine/worker.ts#L174)）。
- 每步写保护（fencing 语义）：`guard()` 校验 `latest.leaseId === leaseId && status==="running"`，`checkpoint()` 与 `event()` 的 CAS 期望集都含 `leaseId`，租约易主后旧持有者的写入被拒并抛 `LostLeaseError`（[`worker.ts:144-161`](https://github.com/CopilotKit/openmuse/blob/main/apps/server/src/engine/worker.ts#L144)）。
- 被中断任务恢复：tick 把 `status==="running" && leaseUntil <= now` 的任务列为到期（[`worker.ts:79-86`](https://github.com/CopilotKit/openmuse/blob/main/apps/server/src/engine/worker.ts#L79)），重新认领（attempts+1），从 `task.state` checkpoint 续跑；测试 `expired leases recover saved checkpoints after the database restarts`（[`tests/engine.test.ts:70-99`](https://github.com/CopilotKit/openmuse/blob/main/tests/engine.test.ts#L70)）与 `two workers claim one task only once`（[`tests/engine.test.ts:30-45`](https://github.com/CopilotKit/openmuse/blob/main/tests/engine.test.ts#L30)）是定点实证；`docs/VERIFICATION.md` 亦记录 "two-worker lease races, expired-lease recovery" 已测。
- 多进程部署：README 明示 "Run one API instance; task workers coordinate through SQL leases"（[`README.md:186`](https://github.com/CopilotKit/openmuse/blob/main/README.md#L186)），PGlite 不能跨进程、独立 worker 需 PostgreSQL。

**与 brief-plan 表述的实现差异（不影响判定，但落设计时要知道）**

- 没有独立的单调整数 fencing token 字段：fencing 由"CAS 期望集里带 `leaseId`"实现，`AgentTask` 上只有 `leaseId`/`leaseUntil`/`attempts` 三个字段（[`packages/domain/src/agent.ts:41-43`](https://github.com/CopilotKit/openmuse/blob/main/packages/domain/src/agent.ts#L41)）。等价于"每次认领换新 UUID 即 token"，但**没有全序比较**——平台 `workspace-automation` 的单调 fencing token 比它更强（可拒绝旧 token 的迟到写，openmuse 靠 CAS 期望集达到同样效果）。
- 不是专用表：任务/租约/回执全部是单表 `records` 的 jsonb 行（`kind='tasks'` 等），没有 `lease_expires_at` 列与索引，tick 是全表 `scan("tasks")` 内存过滤（[`worker.ts:78`](https://github.com/CopilotKit/openmuse/blob/main/apps/server/src/engine/worker.ts#L78)）——规模上限远低于平台关系表方案。
- 租约过期恢复**不是**"标 `outcome_unknown` 再决策"，而是直接 requeue 重跑（见 ③）。

### ② "durable plan 的 approvals/receipts 门控（重试先查回执防重复执行）" —— **证实但有出入**

**证实部分**

- **回执先行查重**：`ComputerService.execute` 支持 `idempotencyKey`，主键 = `sha256("computer-command:"+key)`，先 `db.get(...)`，命中且命令一致就**直接返回既有回执**，不重跑（[`apps/server/src/computer.ts:444-453`](https://github.com/CopilotKit/openmuse/blob/main/apps/server/src/computer.ts#L444)）；写入用 `insertIfAbsent`（`ON CONFLICT DO NOTHING RETURNING`）首写胜出（[`db.ts:122-132`](https://github.com/CopilotKit/openmuse/blob/main/apps/server/src/db.ts#L122)、[`computer.ts:470-475`](https://github.com/CopilotKit/openmuse/blob/main/apps/server/src/computer.ts#L470)）。
- 任务创建同样幂等：`createTask(owner, raw, idempotencyKey)` → id=`sha256("task:"+key)`，已有即返回（[`service.ts:193-197`](https://github.com/CopilotKit/openmuse/blob/main/apps/server/src/engine/service.ts#L193)）；审批提案 `propose(..., idempotencyKey)` 同构（[`actions.ts:45-52,90-98`](https://github.com/CopilotKit/openmuse/blob/main/apps/server/src/actions.ts#L45)），测试 `no duplicate proposal minted`（[`tests/prepare-lease-loss.test.ts:97-114`](https://github.com/CopilotKit/openmuse/blob/main/tests/prepare-lease-loss.test.ts#L97)）。
- **审批门控执行**：外部写（邮件/日历）只能走 `prepare_email`/`prepare_event` → `ActionProposal(status:"awaiting_review")` → 任务转 `waiting_approval`；模型没有任何"批准"工具（`model.ts` 系统提示明写 "there is no tool to approve them"，[`engine/model.ts:340`](https://github.com/CopilotKit/openmuse/blob/main/apps/server/src/engine/model.ts#L340)）。worker tick 对 `waiting_approval` 任务：action 仍 `awaiting_review` 则跳过（不消耗执行槽），action 变 `succeeded` 才继续执行（[`worker.ts:90-111`](https://github.com/CopilotKit/openmuse/blob/main/apps/server/src/engine/worker.ts#L90)）；测试 `scheduled tasks wait for due time and approvals wait for a recorded outcome`（[`tests/engine.test.ts:100-137`](https://github.com/CopilotKit/openmuse/blob/main/tests/engine.test.ts#L100)）。
- 审批一次性消费（CAS 式）：`Store.claim` 只在 `status='awaiting_review'` 且未过期时把 action 置 `executing`/`denied`，且置 `executing` 还要求关联任务处于 `running|waiting_approval`（EXISTS 子查询）（[`db.ts:140-152`](https://github.com/CopilotKit/openmuse/blob/main/apps/server/src/db.ts#L140)）；重复 decide 拿不到 claim 就返回现状。
- 重试被回执门控：`control(...,"retry")` 要求任务 `failed`，且若任务挂了 action、action 未 `succeeded`，直接 409 ——"Check the reviewed action before retrying; its outcome may be uncertain. Start a new task when reconciled."（[`service.ts:279-286`](https://github.com/CopilotKit/openmuse/blob/main/apps/server/src/engine/service.ts#L279)）。

**出入部分**

- **门控对象是"外部副作用动作（Action）"，不是 plan**。openmuse 的 "durable plan" 只是 `AgentTask.plan: TaskStep[]`（步骤数组，[`packages/domain/src/agent.ts:34`](https://github.com/CopilotKit/openmuse/blob/main/packages/domain/src/agent.ts#L34)，由 `set_plan` 工具写入，[`engine/model.ts:105-115`](https://github.com/CopilotKit/openmuse/blob/main/apps/server/src/engine/model.ts#L105)）——**没有计划 DAG、没有计划审批门**；brief-plan 里"计划审批（planning→awaiting_approval 必经）"在 openmuse 没有对应物。
- 没有独立的回执表/`goal_receipt` 等价物：回执散落在 `kind='computer-commands'`（按 provider 分的 receipts kind，[`computer.ts:222-224`](https://github.com/CopilotKit/openmuse/blob/main/apps/server/src/computer.ts#L222)）、`kind='actions'`、`kind='agent-artifacts'`（`save_artifact`/`finish_task` 产物，[`service.ts:740-760`](https://github.com/CopilotKit/openmuse/blob/main/apps/server/src/engine/service.ts#L740)）。没有"两级幂等键（期次 occurrence + 步骤 step）"的统一回执表，但**步骤级幂等另有等价物**（见 §3 新候选：`state.operations` 缓存）。
- 审批不是"挂起 Run 后同一 Run 继续"：openmuse 的任务在 `waiting_approval` 时整个执行上下文丢弃，批准后由 worker **重新领起一次全新执行**，从 `task.state`/回执续跑（[`service.ts:811-827`](https://github.com/CopilotKit/openmuse/blob/main/apps/server/src/engine/service.ts#L811)）。brief-plan §5.5 的"审批后同一 Run 继续"与之不同，需自行实现或改为 openmuse 式重入。

### ③ "结果不确定时不做隐藏重试（outcome_unknown 显式恢复）" —— **证实但有出入**

**证实部分（外部写链路完整成立）**

- 专用错误类型：`OutcomeUnknownError`，`code="outcome_unknown"`，文案 "Google may have completed this action. Check Google before trying again."（[`packages/integrations/src/google.ts:20-27`](https://github.com/CopilotKit/openmuse/blob/main/packages/integrations/src/google.ts#L20)）。
- 执行失败分类：`ActionService.decide` 的 catch 里，错误带 `outcomeUnknown===true` 或 `code==='outcome_unknown'` 就落 `status:"outcome_unknown"`，否则 `failed`（[`actions.ts:193-203`](https://github.com/CopilotKit/openmuse/blob/main/apps/server/src/actions.ts#L193)）；测试 `network failures and 5xx write responses produce outcome_unknown without retrying`（`tests/google.test.ts:711`，仅见测试名与断言 grep 命中，未逐行读）。
- 进程重启的显式恢复：启动时 `recoverInterruptedActions()` 把所有 `kind='actions' AND status='executing'` 一次性置 `outcome_unknown`，错误文案 "Server restarted during execution. Check the provider before creating another action."（[`db.ts:153-157`](https://github.com/CopilotKit/openmuse/blob/main/apps/server/src/db.ts#L153)，调用点 [`apps/server/src/index.ts:11`](https://github.com/CopilotKit/openmuse/blob/main/apps/server/src/index.ts#L11)），测试 [`tests/persistence.test.ts:8-22`](https://github.com/CopilotKit/openmuse/blob/main/tests/persistence.test.ts#L8)。
- 不确定就挡住重试：`control("retry")` 对未 `succeeded` 的关联 action 报 409（同 ②）；模型侧重试边界写死在 `config.ts` 注释：只对响应开始前的瞬时错误重试、`MODEL_MAX_RETRIES = 2`、"External writes never re-fire here: they are dispatched outside the model loop through reviewed, idempotency-keyed actions"（[`apps/server/src/config.ts:97-104`](https://github.com/CopilotKit/openmuse/blob/main/apps/server/src/config.ts#L97)）；测试证明"已开始的流不重试""已提交的工具结果不被重试重放"（[`tests/model-retry.test.ts:82-136`](https://github.com/CopilotKit/openmuse/blob/main/tests/model-retry.test.ts#L82)）。
- Linux 命令中断不伪装成功：租约过期或用户 Stop 时，`running` 命令回执被 CAS 改成 `interrupted`，stderr 写 "Execution was interrupted. Its outcome is unknown; inspect files before running it again." / "Stopped by the user."（[`computer.ts:311-331, 396-408`](https://github.com/CopilotKit/openmuse/blob/main/apps/server/src/computer.ts#L311)）；迟到执行者的完成写入因 `status='running'` 不匹配而失败，改写为 `interrupted`（[`computer.ts:577-590`](https://github.com/CopilotKit/openmuse/blob/main/apps/server/src/computer.ts#L577)）；测试 `an expired lease from a dead executor recovers as interrupted without replay`（`tests/computer.test.ts:269`，仅见测试名）。

**出入部分**

- **`outcome_unknown` 是动作（action）级状态，不是任务级状态**。`TaskStatus` 枚举里没有 `outcome_unknown`（[`packages/domain/src/agent.ts:3-12`](https://github.com/CopilotKit/openmuse/blob/main/packages/domain/src/agent.ts#L3)：queued/running/waiting_approval/waiting_input/scheduled/paused/succeeded/failed/cancelled）。任务租约过期/丢失后的处理是 **CAS 回 `status:"queued"` 静默重排队**（[`worker.ts:213-220`](https://github.com/CopilotKit/openmuse/blob/main/apps/server/src/engine/worker.ts#L213)），run 记录标 `interrupted`（[`worker.ts:240-249`](https://github.com/CopilotKit/openmuse/blob/main/apps/server/src/engine/worker.ts#L240)）。也就是说：**任务层其实会自动重跑**（`attempts+1`），安全性靠三件事兜底：① `guard/checkpoint` 的 leaseId CAS 防旧 worker 续写；② `task.state.operations` 幂等缓存防步骤重复副作用（见 §3）；③ 有外部副作用的步骤必须走 approval/action，而 action 层才有 `outcome_unknown`。
- 若按 brief-plan 规则 4 的字面（"Run 超时/连接中断 → 显式落 `outcome_unknown`，恢复扫描决定重跑或人工确认"），openmuse 只对**外部写动作**做到这一点，任务本体是"到期即重跑"而非"先标未知再决策"——**差异需在平台侧自行补齐**（平台 `goal_run.outcome_unknown` 状态正是 openmuse 没有的那部分）。
- 模型 run 有 5 分钟硬超时（`Model run timed out after five minutes`，[`engine/model.ts:367-371`](https://github.com/CopilotKit/openmuse/blob/main/apps/server/src/engine/model.ts#L367)），超时后任务按"执行失败 → failed"处理，不标未知（因为模型调用本身无副作用保证）。

### ④ "周期 Goal 巡检 + 告警去重 + 失败退避" —— **证实但有出入**

**证实部分**

- **周期巡检存在，但主体是 Monitor（网页看护）而非 Goal**：`Monitor{intervalMinutes, nextCheckAt, status: active|paused|stopped, lastHash, checks}`（[`packages/domain/src/agent.ts:67-82`](https://github.com/CopilotKit/openmuse/blob/main/packages/domain/src/agent.ts#L67)）；执行完写 `nextRunAt = now + intervalMinutes`、任务置 `status:"scheduled"`（[`service.ts:1131,1166-1168`](https://github.com/CopilotKit/openmuse/blob/main/apps/server/src/engine/service.ts#L1131)），worker tick 到点才认领（[`worker.ts:83`](https://github.com/CopilotKit/openmuse/blob/main/apps/server/src/engine/worker.ts#L83)）。测试 `scheduled tasks wait for due time`（[`tests/engine.test.ts:100-122`](https://github.com/CopilotKit/openmuse/blob/main/tests/engine.test.ts#L100)）。
- **告警去重是构造性的**：通知 id = `hash(deterministic key)` + `insertIfAbsent`（`ON CONFLICT DO NOTHING`），重复发布天然被吞（[`service.ts:726-736`](https://github.com/CopilotKit/openmuse/blob/main/apps/server/src/engine/service.ts#L726)）。key 形如 `monitor:<id>:<alertSequence>:<hash>`、`task-done:<taskId>`、`task-error:<taskId>:<attempts>`、`watch-error:<taskId>:<failureStreak>:<retry|paused>`（[`service.ts:866, 916-958, 1188`](https://github.com/CopilotKit/openmuse/blob/main/apps/server/src/engine/service.ts#L866)）；`alertSequence` 与结果同 checkpoint 提交，"publication retries still deduplicate on the same saved notice key"（[`service.ts:1126-1130`](https://github.com/CopilotKit/openmuse/blob/main/apps/server/src/engine/service.ts#L1126)）；另有"只有相对时间变化则静默继续不告警"的 `quiet` 抑制（[`service.ts:1119-1122`](https://github.com/CopilotKit/openmuse/blob/main/apps/server/src/engine/service.ts#L1119)）与"每段失败只告警一次"的 `failureStreak`（[`service.ts:836-837`](https://github.com/CopilotKit/openmuse/blob/main/apps/server/src/engine/service.ts#L836)）。README 亦自述 "deduplicated alerts and failure backoff"（[`README.md:55`](https://github.com/CopilotKit/openmuse/blob/main/README.md#L55)）。
- **失败退避存在且参数明确**：巡检失败 → `nextCheckAt = now + min(60, 2**failures) 分钟`（指数退避、封顶 60 分钟），任务转 `scheduled` 带 error；**连续 5 次失败自动转 `paused`**（"Watch paused after repeated failures"），成功或 resume 后 `failures` 清零（[`service.ts:835-869`](https://github.com/CopilotKit/openmuse/blob/main/apps/server/src/engine/service.ts#L835)、[`service.ts:554`](https://github.com/CopilotKit/openmuse/blob/main/apps/server/src/engine/service.ts#L554)）；任务 paused 落定后同步把 monitor 置 paused（[`service.ts:966-974`](https://github.com/CopilotKit/openmuse/blob/main/apps/server/src/engine/service.ts#L966)）。
- 另有一层常驻维护循环：`AgentService.start()` 每 60s 跑 `maintain()`——补发未发布的任务结局、激活 monitor、恢复 accepted idea、每 15 分钟刷新一次 Ideas（[`service.ts:71-128`](https://github.com/CopilotKit/openmuse/blob/main/apps/server/src/engine/service.ts#L71)）。

**出入部分**

- **没有"Goal 巡检"**：Goal 只是 `{title, description, category, status: active|paused|completed, milestones[]}`（[`packages/domain/src/agent.ts:58-66`](https://github.com/CopilotKit/openmuse/blob/main/packages/domain/src/agent.ts#L58)），**没有健康检查/偏差巡检/告警规则**。最接近的是 `refreshIdeas()` 周期扫 active goal，若无里程碑就产出 "Let's make a plan for ..." 的 idea（[`service.ts:626-640`](https://github.com/CopilotKit/openmuse/blob/main/apps/server/src/engine/service.ts#L626)），这是"建议"而非"巡检告警"。
- 巡检对象只有**公开网页**（change/contains/price_below 三条件，[`packages/domain/src/agent.ts:144-160`](https://github.com/CopilotKit/openmuse/blob/main/packages/domain/src/agent.ts#L144)），没有 brief-plan 设想的"数据源可用性/持仓偏离/目标偏差"巡检类型。
- 没有 cron/trading_day 之类调度表达式：只有 `nextRunAt` 时间点 + `intervalMinutes` 固定间隔。

**判定汇总**

| # | brief-plan §3 二手映射 | 判定 |
|---|---|---|
| ① | SQL lease 协调多 worker 并恢复被中断任务 | **源码证实**（fencing 形式为 CAS 期望集带 leaseId，非单调 token；单表 jsonb 存储） |
| ② | durable plan 的 approvals/receipts 门控；重试先查回执 | **证实但有出入**（门控对象是外部写 Action 而非 plan；无计划 DAG/计划审批；无独立回执表，回执=幂等键记录+步骤级 operations 缓存；审批后是重新领起执行而非同一 Run 继续） |
| ③ | 结果不确定时不做隐藏重试（outcome_unknown 显式恢复） | **证实但有出入**（`outcome_unknown` 只存在于 action 层；任务租约过期是 requeue 自动重跑，靠 leaseId CAS + 幂等缓存兜底，而非"先标未知再决策"） |
| ④ | 周期 Goal 巡检 + 告警去重 + 失败退避 | **证实但有出入**（周期巡检主体是 Monitor 网页看护，无 Goal 级巡检；告警去重与 2^n≤60min 退避、5 次暂停的实现为源码实证） |

## 3. 新机制映射候选（源码新发现，brief-plan §3 尚未收录）

1. **CAS 期望集 = 通用并发原语**：`UPDATE records SET data=data||$patch WHERE data @> $expected`（[`db.ts:93-105`](https://github.com/CopilotKit/openmuse/blob/main/apps/server/src/db.ts#L93)）一个原语同时承担认领、心跳、fencing、状态迁移、审批一次性消费、告警发布。→ 平台 `goal_*` 关系表方案之外，可作为"期望状态包含式 CAS"的写法参照（尤其是"期望集里带 leaseId+status"这条 fencing 规则）。
2. **幂等键直接当主键**：`id = sha256(kind + idempotencyKey)` + `insertIfAbsent`（首写胜出），重复请求返回既有记录（任务 [`service.ts:195-197`](https://github.com/CopilotKit/openmuse/blob/main/apps/server/src/engine/service.ts#L195)、动作 [`actions.ts:45-52`](https://github.com/CopilotKit/openmuse/blob/main/apps/server/src/actions.ts#L45)、命令 [`computer.ts:444-453`](https://github.com/CopilotKit/openmuse/blob/main/apps/server/src/computer.ts#L444)、监控 [`service.ts:408-413`](https://github.com/CopilotKit/openmuse/blob/main/apps/server/src/engine/service.ts#L408)）。→ 与 `goal_receipt.idempotency_key` + `INSERT OR IGNORE` 同构，且证明"服务端哈希派生主键"比客户端生成 UUID 更能防重复提交。
3. **审批内容哈希绑定**：`ActionProposal.hash = sha256({input, connection, target, targetVersion})`，decide 时 hash 不符即 409 "This proposal changed"（[`actions.ts:77-86, 110-111`](https://github.com/CopilotKit/openmuse/blob/main/apps/server/src/actions.ts#L77)）——**审批只对它看到的那份内容生效**。→ 直接可搬到 `goal_plan.approval`（计划 v2 内容变了，v1 的批准自动失效）。
4. **审批有效期**：`expiresAt = 创建+30min`，过期由 worker CAS 转 `expired`（[`actions.ts:88`](https://github.com/CopilotKit/openmuse/blob/main/apps/server/src/actions.ts#L88)、[`worker.ts:98-109`](https://github.com/CopilotKit/openmuse/blob/main/apps/server/src/engine/worker.ts#L98)）→ 未决审批不应永久挂起任务。
5. **审批与任务状态双向校验 + 孤儿清理**：approve 要求任务处于 `running|waiting_approval`（[`actions.ts:113-120`](https://github.com/CopilotKit/openmuse/blob/main/apps/server/src/actions.ts#L113)）；任务被 pause/cancel 导致提案写不进去时，自动 deny 孤儿提案（[`service.ts:782-792`](https://github.com/CopilotKit/openmuse/blob/main/apps/server/src/engine/service.ts#L782)，测试 [`tests/prepare-lease-loss.test.ts:116-144`](https://github.com/CopilotKit/openmuse/blob/main/tests/prepare-lease-loss.test.ts#L116)）。
6. **步骤级幂等缓存（等价 step_key 回执）**：模型工具结果按 `sha256(name+JSON(args))` 存进 `task.state.operations` 并 checkpoint，重入时直接命中缓存（[`engine/model.ts:86-96`](https://github.com/CopilotKit/openmuse/blob/main/apps/server/src/engine/model.ts#L86)）；配套 `serial()` 队列保证并发工具调用的 checkpoint 有序（[`engine/model.ts:46-56`](https://github.com/CopilotKit/openmuse/blob/main/apps/server/src/engine/model.ts#L46)）。→ `goal_receipt.step_key` 的最小实现形态。
7. **模型重试边界写成硬规则**（可直接抄进执行协议）：仅响应开始前的瞬时错误（408/409/429/5xx/连接错）重试 ≤2 次；400/401/403 首次即失败；**流开始后任何失败都不重试**；已提交的工具结果与已投递给客户端的输出永不重放（[`config.ts:97-104`](https://github.com/CopilotKit/openmuse/blob/main/apps/server/src/config.ts#L97) + [`tests/model-retry.test.ts`](https://github.com/CopilotKit/openmuse/blob/main/tests/model-retry.test.ts) 六个定点测试）。
8. **资源级租约（比任务级更细一层）**：`computer-state/lease` 带 `token/expiresAt/stopping/stopInFlight/stopAttempt/stopConfirmed/executorDone/operation` 状态机，命令执行者必须 `executorDone` 后生命周期操作才能放行，防"延迟的 Docker client exec 进重启后的容器"（[`computer.ts:194-310`](https://github.com/CopilotKit/openmuse/blob/main/apps/server/src/computer.ts#L194)）。→ 平台沙箱/独占资源（同一时刻只能有一个回测占沙箱）可参考；测试 `stale-executor restart fencing`（`docs/VERIFICATION.md:35`）。
9. **事件流 schema**：`RunEvent.kind ∈ plan|step|observation|approval|result|error|status`，按 taskId 落 `run-events`（[`packages/domain/src/agent.ts:50-57`](https://github.com/CopilotKit/openmuse/blob/main/packages/domain/src/agent.ts#L50)）→ 与 `goal_event` 高度同构，可对拍字段命名。
10. **任务并发上限与防饿死**：非终态任务 ≤100（[`service.ts:203-207`](https://github.com/CopilotKit/openmuse/blob/main/apps/server/src/engine/service.ts#L203)）、每 worker 同时 3 个执行槽、`waiting_approval` 不占槽（[`worker.ts:88-90`](https://github.com/CopilotKit/openmuse/blob/main/apps/server/src/engine/worker.ts#L88)）、长任务不阻塞后续 tick（[`worker.ts:114-122`](https://github.com/CopilotKit/openmuse/blob/main/apps/server/src/engine/worker.ts#L114)，测试 `pending reviews do not starve queued work` / `a long-running task does not starve queued work`）。
11. **持久化 Chromium profile 保留机制**（任务书指定项）：
    - 每会话一个目录 `<dataDir>/<uuid>/{profile,session.json,storage.json,downloads/}`，profile 用 Playwright `chromium.launchPersistentContext(profileDir)`（[`apps/worker/src/browser.ts:176-203`](https://github.com/CopilotKit/openmuse/blob/main/apps/worker/src/browser.ts#L176)）。
    - 启动时扫描 `dataDir` 恢复已保存会话为 `closed` 态，重开用同一 UUID（[`browser.ts:50-61`](https://github.com/CopilotKit/openmuse/blob/main/apps/worker/src/browser.ts#L50)）；`session.json` 用 `tmp+rename` 原子写（[`browser.ts:63-67`](https://github.com/CopilotKit/openmuse/blob/main/apps/worker/src/browser.ts#L63)）。
    - Cookie 额外落 `storage.json`：优雅关闭时 `storageState({path})` 尽力保存（失败也不阻塞释放槽位），重开时 `addCookies` 回灌（[`browser.ts:144-158, 213-222`](https://github.com/CopilotKit/openmuse/blob/main/apps/worker/src/browser.ts#L144)）。
    - 配额与生命周期：3 个并发会话、20 个已存 profile、30 分钟 idle 自动关闭（关闭只回收运行态，**profile 文件保留**）、60s 扫描器（[`browser.ts:44, 163-174, 292-298`](https://github.com/CopilotKit/openmuse/blob/main/apps/worker/src/browser.ts#L44)）。
    - 失败语义：**首次启动失败才删目录**（无既有 profile 可保护），**重开失败保留 profile 并标 error**，"Existing profiles survive a failed reopen"（[`browser.ts:271-289`](https://github.com/CopilotKit/openmuse/blob/main/apps/worker/src/browser.ts#L271)、`apps/worker/README.md:51-53`）；Docker 卷 `browser-profiles` 跨重启保留。
    - → 平台若有"跨任务保留登录态的浏览器会话"需求，这套"profile 目录按 UUID 常驻 + 运行态/持久态分离 + 关闭不删档"是可直接照搬的最小方案。

## 4. 不确定处 / 未验证项

1. **GitHub 链接与本地 HEAD 一致性未核对**（本轮未联网）：链接统一指向 `main`，若上游在 2026-10-26 后有改动，行号与内容可能漂移。引用以本地 commit `a4944f4` 为准。
2. **只读了实现与少量定点测试**：`tests/monitor-recovery.test.ts`（830 行，看护去重/恢复的最重测试）、`tests/workflows.test.ts`、`tests/computer.test.ts`、`tests/google.test.ts` 只 grep 到测试名/断言片段，**未逐行读**——文中引用这些测试时仅作"存在该测试"级别的证据。
3. `docs/VERIFICATION.md` 是**项目自述的验证记录**（自称"tested"），不是本笔记独立复跑的结果；本轮**没有运行任何测试**。
4. openmuse 的部署形态是"单 API 进程 + 可选独立 task worker（需 PostgreSQL）"；brief-plan 设想的是多节点平台调度，openmuse 的 `scan("tasks")` 全表轮询方案**没有证明可扩展到平台规模**，只证明了语义正确性。
5. Jev（生成式 UI）、OpenBot 集成、E2B desktop 后端等旁路能力未走读，与四条映射无关但可能含别的可借鉴机制，标注为**未读**。
