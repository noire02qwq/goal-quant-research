# tick-stock-panel（TSP · A股智能量化工作台）源码静态走读笔记

> **状态**：静态走读——**未安装依赖、未运行项目程序/测试/demo、未执行任何项目命令**；本笔记只来自 README/docs 全文阅读、python `ast` 静态解析与 6 个机制文件的行级读码。过程中仅执行了只读检视命令（`wc`/`du`/`git log -1`/`git remote -v`/`git count-objects`）与本地 ast 脚本，**无 git 写操作、未改任何文件（本笔记除外）**。
> **走读日期**：2026-11-12（@research 指令「oss 仓 tick-stock-panel 写静态走读笔记」）。
> **材料与版本**：
> - 仓库：origin `https://github.com/shy3130/tick-stock-panel`（本地浅克隆 `oss-repos/tick-stock-panel`，`--depth 1`；MIT；`VERSION` = **v0.3.36**）。
> - **HEAD = `a7868b7`**（全量 `a7868b783fc6057913bbc0a8d2b69817ad9b7d9b`，提交日期 2026-11-11 21:49 +0800）。
> - **体积 58M**（`du -sh` 含 `.git` 与工作区；`git count-objects -vH` 的 size-pack 为 21.52 MiB，口径不同、各自正确）。
> **读了什么**：`README.md` 全文（698 行）；`AGENTS.md`（12 行）；**`docs/` 下全部 27 份 Markdown 全文**（`docs/*.md` 26 份约 5,564 行 + `docs/examples/custom-data-source/README.md` 43 行）——`features`/`strategy`/`mining`/`market-phase`/`backtest-evidence`/`configuration`/`deployment`/`deploy-password`/`custom-data-source`/`plugin-development`/`external-data-source-packages`/`extension-packages`/`page-sdk`/`open-platform-plan`/`ext-architecture-plan`/`secondary-development`/`factor-platform-plan`/`factor-system-design`/`auto-strategy-lab-plan`/`robust-optimizer-plan`/`paper-trading-plan`/`stock-detail-lightweight-charts-plan`/`backend-data-performance-plan`/`tickflow-pro-phase1-probe`/`tickflow-pro-shared-rate-limit`/`strategy-iteration`/`docs/examples/.../README`；**全部 799 个 `.py` 的 AST 模块地图**（类/函数 + docstring 首行，213,310 行结构一次取全）；**6 个机制文件行级细读**（见 §3）；本项目 `docs/brief-plan.md` §4.1/§5.6/§7/§9/§10 用于映射比对。
> **没读的（明确未读，不得当作依据）**：`CONTRIBUTING.md`（864 行）、`操作说明书.md`（1,414 行）全文；`frontend/` 全部源码；`backend/` 除 §3 所列 6 个机制文件外的代码**未行级细读**（仅 AST 结构与 docstring）；467 个测试模块内容；`mcp-server/`、`examples/`、`scripts/`、`packaging/` 代码；`docs/sponsors/*.svg`、`screenshots/`、`assets/`；git 历史（仅 `log -1`）；官网 tsp.shy313.com、外部链接均未访问。**未运行任何测试或程序**——README/docs 中的性能与规模数字（3000+ 测试、约 100 秒跑完、65 端点、68 列指标/15 列基础数据、毫秒级全市场扫描、12 个 MCP 工具、21 查询 + 5 动作工具、108 万行内存实测等）**一律 claimed_unverified**（自报未复现）。

---

## 0. 一句话结论

TSP 是一条「**核心域 8 个拥有数据与语义、扩展域 5 条通道只消费契约**」的开放单体：插件边界有版本校验与**注册后冻结**、数据源有**统一归一化契约**（失败不得伪装成空数据）、长任务有**落盘状态 + 启动孤儿补录 + 协作式取消**。这三件与本项目 §4.1 插件分解、§5.6 数据适配器、§7 工作台运行结果区**静态同构**；但 TSP 是单用户、文件型存储、事件流可丢旧保新的自托管面板，与本项目 MySQL 权威表 + append-only 审计事件（`goal_event`）**不能照搬**——差异已在 §4 逐条标出。全部映射为**候选参考、未采纳、未改 brief-plan**。

## 1. 定位与文档口径

- **一句话**（README L18）：自托管 · 零运维 · 核心能力全部开放成接口的 A 股量化工作台；策略 / 回测 / 监控 / 因子挖掘 / AI 助手，Polars + React。
- **明确不做**（README L61）：不对标同花顺/通达信，不内置「AI 荐股 / 涨停预测」；数据源已插件化。
- **架构主线**（README L159-198）：核心域 8 个 = 数据底座 / 能力路由 / 订阅锚点 / 策略与回测 / 因子与挖掘 / 环境数据生产 / 监控推送管道 / 扩展数据存储 + 认证配置；扩展域 5 通道 = 数据源插件 · 扩展数据表 · 自定义策略信号 · 页面扩展（单文件源码 + 运行时页面插件）· 后端 custom 模块——「**可整体替换或移除而不伤核心**：删除目录即卸载、复制目录即导入」；19 个页面里 11 个官方页面本身就是扩展。
- **关键机制表**（README L200-211）：能力路由矩阵（声明式数据集路由、fail-closed）、财务多源合并（按 `(symbol, period_end)` 报告期累积、公告日前一律空值绝不填 0）、回测 spawn worker 隔离 + 持久 run ID、开放网关（门禁→认证→六档 scope→每 Token 滑动窗口限流）、事件总线（慢消费者丢旧保新）、交易日探针、扩展自动发现。
- **数字口径**：README 自报的 65 端点契约、3000+ 测试、15/68 列、120 次/分限流、ms 级扫描等**均 claimed_unverified**；`docs/mining.md` 自报的基准（132 万行峰值 RSS 1.291 GiB / 25.140s、876 passed）、`docs/market-phase.md` 的 1454 交易日标定、`docs/stock-detail-lightweight-charts-plan.md` 的 545~595 项 vitest 等**均 claimed_unverified**。

## 2. 源码架构（AST 模块地图）

- **规模**（python `ast` 实测，本机脚本扫描）：**799 个 `.py` 模块 / 213,310 行**；其中**非测试 332 模块 / 118,490 行**，测试 467 模块（`backend/tests/` 为主）；699/799 模块带模块 docstring；非测试代码顶层类 444 个、顶层函数 2,868 个。
- **非测试包分布**（文件 / 行，实测）：

| 包 | 模块 | 行 | 职责（docstring 摘） |
|---|---:|---:|---|
| `backend/app/services` | 104 | 35,627 | 同步/行情/扩展数据/网关/任务/守护/资源包等服务层 |
| `backend/app/backtest` | 24 | 21,309 | 矩阵、引擎、优化、挖掘、守护、walk-forward、worker |
| `backend/app/api` | 42 | 20,031 | FastAPI 路由（kline/strategy/backtest/settings/ext_data…） |
| `backend/app/strategy` | 51 | 12,555 | 策略引擎、监控、25 个 seeds 模板、信号、AI 迭代 |
| `backend/app/custom` | 16 | 4,221 | 扩展域参考实现（assistant 对话助手、模拟盘执行、源码包管理） |
| `backend/app/tickflow` | 9 | 4,142 | `DataStore`（「唯一的存储入口」）、调度、限速 |
| `backend/app/data_providers` | 16 | 3,214 | Provider 契约、能力注册、YAML 自定义源、外部包 |
| `backend/app/indicators` | 3 | 3,178 | enriched 指标流水线 |
| `backend/app/plugins` | 7 | 3,148 | 内置数据源插件（fuyao / tdxquant） |
| `backend/app/factors` | 7 | 2,346 | 因子注册表、DSL、统计、物化缓存 |
| `backend/app/jobs` | 2 | 1,468 | 盘后管道等定时任务 |
| `backend/app/extensions` | 5 | 758 | 后端扩展契约/注册表/加载器/包管理 |
| 其余顶层模块 | 15 | ~3,000 | `main.py` 829、`enriched_generation.py` 676、`desktop.py` 492、`definitions.py` 331、`price_limits.py` 297、`config.py` 281… |
| `backend/scripts` / `examples` / `mcp-server` / `scripts` / `packaging` / `docs` | 15 | 1,194 | 基准与探针脚本、开放接口示例、MCP 服务、版本同步 |

- **最大非测试模块**（行数 + 职责，实测）：

| 模块 | 行 | 职责（docstring 摘） |
|---|---:|---|
| `backtest/matrix.py` | 4,427 | 全市场矩阵构建与缓存预热（`MatrixPrewarmCancelledError`） |
| `backtest/engine.py` | 3,627 | 回测撮合与结果物化（`MatcherConfig`/`TradeRecord`/`SimulationOptions`） |
| `backtest/strategy.py` | 3,128 | 策略依赖解析（`StrategyDependencyResolver`） |
| `tickflow/repository.py` | 2,853 | `DataStore`「唯一的存储入口」、`KlineRepository` 读写入口 |
| `indicators/pipeline.py` | 2,525 | 指标流水线（模块 docstring 为空） |
| `api/settings.py` | 2,454 | 设置面（Key/能力/AI/性能等入参模型） |
| `services/quote_service.py` | 2,258 | 全局实时行情单例 + 每 SSE 连接独立队列订阅者 |
| `strategy/engine.py` | 1,997 | `StrategyDataContext`、叠加策略 `CompositeSpec` |
| `strategy/monitor.py` | 1,823 | 策略监控 + 通用监控规则引擎 |
| `services/ai_provider.py` | 1,512 | AI 工具调用协议（`AIToolProtocolError`） |
| `extensions/*`（合计） | 758 | 扩展契约、注册表、加载器（§3.1） |

> 完整地图（799 行，逐模块「相对路径 \| 模块 docstring 首行 \| 类及 docstring \| 类数/函数数/行数」）为本次走读的中间产物，未入库；关键结论已摘入本节与 §3。

## 3. 机制细读（6 个文件，行级）

### 3.1 扩展注册表与加载：staging → 校验 → 冻结（`app/extensions/{contracts,registry,loader}.py`）

- **契约极小**：`BACKEND_EXTENSION_API_VERSION = 1`；对扩展只暴露 `RepositoryAccess`（只读协议，仅 `get_name_map`）、frozen dataclass `ExtensionContext`、抽象 `NotificationFormatter`（「input event must not be mutated」）——`contracts.py` 模块 docstring 自述「Stable, small-grained contracts for in-repository secondary development」。
- **staging 语义**（`registry.py` L28-49）：`BackendExtensionRegistrar` docstring——「**a failed setup is discarded without partial registration**」；`include_router` 还带 `TypeError` 类型检查。
- **注册 = 先全量校验再变更**（L73-106）：`register()` docstring「Validate a staged extension fully before mutating the registry」——id 正则 `^[a-z0-9]+(?:[._-][a-z0-9]+)*$`、`api_version` 必须等于当前版本、扩展 id 与 formatter id 重复均拒绝；**一处不过，整个 registrar 不落库**。
- **冻结与默认回落**（L108-132）：`freeze()` 排序后置 `_frozen`；`notification_formatters()` 未冻结即 `RuntimeError`；**无任何自定义 formatter 时回落 `core/core.notification` 默认实现**——核心行为在未启用扩展时与当前版本一致。
- **`mutable_copy()`**（L114-119）：给可选包预检用的暂存副本，**不污染已发布快照**。
- **加载器**（`loader.py`）：`pkgutil` 扫 `app/custom` 下非下划线模块 → 要求 `EXTENSION_ID` 与 `setup(registrar)` → `_validate_router_conflicts` 以 `(path, method)` 查重（与核心及同批扩展均查）→ 单模块任何异常只 `warning` 并进 `errors` 元组，**不阻断其他扩展与主程序**；全部成功后才 `registry.freeze()` 并统一 `include_router`。`start_backend_extensions()` 在核心数据就绪后跑 `startup(context)`，`EXTENSION_ID` 不在 registry 的模块跳过。
- 与 `docs/secondary-development.md` §4 的文字一致：注册 ID 全局唯一、重复拒绝、启动完成后注册表冻结、单个实现失败只禁用自身。

### 3.2 数据源 Provider 契约：换源不换口径（`app/data_providers/base.py`，98 行）

- 模块 docstring：首个实现包 TickFlow，其他源（Tushare/AkShare…）「**should return the same normalized Polars schemas so storage, indicators and backtests stay data-source agnostic**」。
- **`ProviderRequestError`**（L19-20）docstring：「数据源明确请求失败; **调用方须标记失败, 不得转换成成功的空数据**」——失败语义显式化，与 `docs/plugin-development.md` 异常语义表（软失败仅限 realtime，其余明确抛错、不跨源）一致。
- `ProviderCapabilities` 7 个 bool（instruments/daily/adj_factor/minute/realtime/depth5/financial）= 能力路由矩阵的声明端。
- `MarketDataProvider` 为 **Protocol**（6 个方法，全部返回归一化 schema）；`StreamingMinuteProvider` 可选流式能力——「请求分批/分页/限频与有界输出**由源负责**」，`on_chunk_done` 回调异常必须透传以支持取消。

### 3.3 策略模板形态：META + 白名单参数 + 矩阵信号（`app/strategy/seeds/ma_golden_cross.py`，87 行）

- 单文件即完整策略：`META` 字典（`id/name/description/tags`、`asset_types`、`timeframes`、**类型化 `params`**（`bool/float` 带 `min/max/step/default`，供 UI 调参）、`scoring` 权重（`momentum_20d 0.5 + vol_ratio_5d 0.3 + change_pct 0.2`，和为 1.0）、`order_by/limit`）→ `EXECUTION_BACKEND = "matrix_native"` → `ENTRY_SIGNALS`/`EXIT_SIGNALS` → `STOP_LOSS`/`MAX_HOLD_DAYS`。
- 类只实现三件事：`required_fields()`、`required_warmup_bars()`、`compute_signals(market, params)`——信号在矩阵上向量化产出，`valid_shift as shift` **别名导入防未来函数**（`from app.backtest.matrix import valid_shift as shift`）。
- AST 地图证实 **25 个 seed 全部同一形态**（每文件一个 `XxxMatrixStrategy`），另有 `research/factor_rank_research.py`（research_only 模板）。`docs/strategy.md` 的三扩展方式（UI 自定义信号 / AI 生成经 ast 安全校验 / 手写 .py）与该结构互为印证。

### 3.4 统一定义存储 + 导入即冒烟（`app/definitions.py`，331 行）

- 模块 docstring 给出统一契约 `{id, kind, version, params, inputs(依赖列), expression, meta}`，本模块只承载「与计算无关的公共半边」。
- **`JsonDefinitionStore`**：`data_dir/<subdir>` 下 JSON 的 load/save/delete **单一实现**——`atomic_write_text` 原子写、**损坏文件跳过并告警**（「插件隔离要求」）、`fingerprint()` 用 `(文件名, mtime_ns)` 目录签名做缓存失效。
- **kind 注册表**：`DefinitionKind`（存储 + id 规则 + 校验 + 依赖提取）+ `register_kind`（同 kind 换描述器**拒绝**，fail-closed）；内置 kind 惰性导入（`signal → custom_signals`、`factor → factors.store`），消费方无需预导入领域模块。
- **`smoke_definition()`**：validate → 编译（信号经 `build_expressions` 并捕获告警、因子经 `to_spec`）→ 依赖可解析（依赖列 ∉ 已知输入列则 `W001`）——「**导入即知道定义能不能算**」，`ok=False` 时 issues 至少一条、不静默通过。
- **`catalog()`**：跨 kind 统一目录，单个坏定义只写 `item["error"]`，「目录不因单个坏定义失败」。

### 3.5 进程内事件总线：有界、丢旧保新、scope 过滤（`app/services/events.py`，74 行）

- 模块 docstring 三条设计约束：只做进程内广播（自托管单进程）、**订阅队列有界 200——慢消费者丢最旧而不是拖垮发布方**、事件带 `required_scope`（票据只继承 scope 不放大权限）。
- SSE `id` 用「毫秒时间戳但严格递增」（`max(ts*1000, last+1)`）——同一毫秒多条各得不同 id、时钟回拨不倒退，客户端按 `lastEventId` 去重不误丢。
- 进程级单例 `bus = EventBus()`，域模块与 API 层共用。

### 3.6 任务注册表：落盘快照 + 启动孤儿补录 + 协作式取消（`app/services/pipeline_jobs.py`，616 行）

- 模块 docstring：每 job 一个 JSON 文件；`create()/start()` **即落盘 pending/running 快照**——「进程意外死亡时记录不蒸发」；实例化时 `_reap_orphans()` 把上个进程遗留的 pending/running 补标为 `failed(中断)`，**`finished_at` 取文件 mtime（最后已知存活时刻），不用下次开机时间虚增时长**，并夹住时钟回拨导致的负时长。
- **单飞去重条件是 `pending ∨ running`**（L218-229 docstring 明说旧实现只查 running 导致双窗口竞态、两条全市场拉取并发读改写同一 parquet）。
- **卡死判定 = 进度停滞而非总时长**（L31-45）：普通任务 1200s、分钟 K 长任务 1800s 无进度才 reap；总时长 12h 硬上限兜底；`pending` 排队停滞也回收。reap 在 `/run` 与轮询端点都会调，「任意轮询都能自愈」。
- **`JobCancelledError(BaseException)`**（L48-55）：继承 BaseException 防止分块的 `except Exception: continue` 吞掉取消信号；取消标志独立于 job 记录存活（`fail()` 弹出记录后僵尸线程仍能感知），有界 32 条淘汰最老。
- **执行槽所有权 token**（L566-611）：`release_run_slot(owner)` 非持有者释放一律忽略——修复「僵尸线程 finally 误释放新任务的锁」；代价是真卡死需重启进程才能再跑重任务（优先保证数据不损坏）。

## 4. 与本项目的映射（静态同构比对；**候选参考、未采纳，未改 brief-plan**）

| # | TSP 机制（文件/行级证据） | 本项目对应节 | 关系（仅静态同构） |
|---|---|---|---|
| 1 | 扩展域「只消费契约、删除目录即卸载」+ `loader.py` 扫 `app/custom` 自动发现、单模块失败只告警不阻断 | **§4.1 插件分解**（goal-agent / quant-research 两插件公开契约通信） | **候选参考**：同为「核心自洽 + 扩展只经契约接入 + 失败隔离」；TSP 是目录约定式发现，本项目走 Cordis 贡献点，不采纳其实现、只借边界理由 |
| 2 | `BackendExtensionRegistrar` staging（失败整体丢弃、无半注册）+ `api_version` 必须相等 + `freeze()` 后注册表不可变 | **§4.1** 插件加载/禁用生命周期（禁用即停、不半注册） | **候选参考**：版本门 + 冻结 + 重复 ID 拒绝三件套可作插件契约验收清单；未采纳 |
| 3 | `MarketDataProvider` Protocol + `ProviderCapabilities` 声明式能力（换源不换 storage/indicators/backtest 口径） | **§5.6 vnpy 集成**（Datafeed 适配器 → vnpy BarData；A股 profile 封装复权/T+1） | **同构**：数据适配器协议同族；TSP 按「数据集」路由、本项目按「引擎输入」适配，静态比对，未采纳 |
| 4 | `ProviderRequestError`「不得转换成成功的空数据」+ 软失败仅限 realtime 的异常语义表 | **§5.6** 三层构造性防护 / §5.2 规则 4「结果不确定不隐藏重试」 | **同价值观**：失败必须显式；TSP 只到「报错不伪装」，本项目还要 `outcome_unknown` 语义——不可降级照搬 |
| 5 | 25 个 `seeds/*.py` 单文件策略模板：类型化 `params` 白名单 + `scoring` 权重 + `ENTRY/EXIT_SIGNALS` + 防未来 `valid_shift` | **§9 策略模板 T1–T4**（T1 双均线即 MA 金叉同族）+ **§5.6** `GoalStrategyBase` 白名单参数 | **候选参考**：模板「一个文件 = 逻辑 + 可调参数 + 进出场 + 风控」的信息架构可直接对照 T1–T4 落法；TSP 无版本链/评价指标字段，未采纳 |
| 6 | `JobStore` 落盘快照 + `_reap_orphans` 孤儿补标 failed(中断)、`finished_at`=mtime | **§7 目标工作台 UI**（运行结果区：GoalRun 列表、任务状态着色、历史记录）+ §5.2 恢复扫描 | **候选参考**：工作台「任务状态不蒸发」的最小实现样板；**差异**：TSP 把孤儿标 `failed`，本项目要求先标 `outcome_unknown` 再决策——语义更严，不得照抄其状态集 |
| 7 | `reap_stale` 进度停滞判定（1200/1800s）+ 协作式取消 + 所有权 token 执行槽 | **§7** 运行结果区（失败修复、异常处理）+ §5.5 控制（pause/resume/terminate） | **候选参考**：卡死判定与「谁有权释放槽」的工程细节；未采纳 |
| 8 | `EventBus` 有界队列**丢旧保新** + `required_scope` 过滤 + 单调 SSE id | **§7** 对话面板状态卡片 / `goal_event` 时间线 | **候选参考（带反例）**：scope 过滤与单调 id 可借；**丢旧保新与审计 append-only 冲突**——`goal_event` 是全程可追溯底座，不能引入丢弃语义，此条标「不采纳丢旧」 |
| 9 | `JsonDefinitionStore` 原子写 + 损坏跳过 + mtime 签名；`DefinitionKind` 注册表；`smoke_definition` 导入即冒烟（W001 未知依赖列） | **§10 数据模型**（`goal_*` 表、`goal_code_version` 指纹、迁移自管）+ §4.1 定义契约 `{id,kind,version,inputs,expression}` | **候选参考**：契约字段形状与「导入即校验、坏条目隔离」高度同构；TSP 是文件型 JSON（本项目 MySQL + S3 权威），实现不采纳，**字段与冒烟语义可比照** |

> 以上 9 条全部为**静态同构比对**：tick-stock-panel 未安装未运行、本项目 brief-plan **未因此改动**；状态统一为「**候选参考、未采纳、未改 brief-plan**」。

## 5. 运行前置（文档静态转述，未跑）

- Dev 模式（README 方式 D / `docs/deployment.md`）：Python ≥ 3.11 · Node ≥ 20 · `uv` · `pnpm`；`cp .env.example .env && ./dev.sh`（后端 3018、前端 3011）。
- Docker（方式 A/B）：`ghcr.io/shy3130/tick-stock-panel:latest` 单容器，数据挂 `-v ${PWD}/data:/app/data`；`docker compose up --build` 本地构建。另有桌面客户端（Windows/macOS Apple Silicon）与「本机 AI 代部署」提示词。
- 回测依赖为可选 extras（vectorbt → numba 体积大，`uv sync --extra backtest`）；老 CPU 走 `BACKEND_EXTRAS=legacy-cpu`。
- **本机未装依赖、未起服务、未跑任何测试与 demo**——本节不含任何实测；所有安装与性能描述均为文档转述（claimed_unverified）。

## 原文链接

- 仓库：https://github.com/shy3130/tick-stock-panel （本地 `oss-repos/tick-stock-panel`，HEAD `a7868b7`，v0.3.36，58M）
- 关键文件：`README.md`、`AGENTS.md`、`docs/{features,strategy,mining,market-phase,backtest-evidence,custom-data-source,plugin-development,open-platform-plan,ext-architecture-plan,secondary-development,factor-system-design,auto-strategy-lab-plan,robust-optimizer-plan,page-sdk,extension-packages,deployment}.md`、`backend/app/extensions/{contracts,registry,loader}.py`、`backend/app/data_providers/base.py`、`backend/app/strategy/seeds/ma_golden_cross.py`、`backend/app/definitions.py`、`backend/app/services/{events,pipeline_jobs}.py`

## 6. 核验附注（回源核验）

> 回源核验：<角色> <日期>
