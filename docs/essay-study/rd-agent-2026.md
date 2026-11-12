# RD-Agent（microsoft/RD-Agent）源码静态走读笔记

> **状态**：静态走读（README + docs 全文 + 571 模块 AST 模块地图 + 6 组关键机制行级细读；**未安装、未运行**——未 `pip install`、未执行任何 `rdagent …` 命令/demo/回测/测试，**未执行任何仓库内程序**；仅做本地只读文件查看与 Python `ast` 解析收集元数据，未做任何 git 写操作、未改仓库内任何文件）。
> **走读日期**：2026-11-12（@user 指令：为 oss 仓 RD-Agent 写静态走读笔记，验证 brief-plan §6.2/§12.1 W7 的设计假设）。
> **材料与版本**：
> - 仓库：[origin https://github.com/microsoft/RD-Agent](https://github.com/microsoft/RD-Agent)（MIT 类开源，README 徽章 CI/CodeQL/mypy/ruff/pre-commit 齐全）。
> - 本地克隆 `oss-repos/RD-Agent`（浅克隆，原小写目录名 2026-11-12 按 CONVENTIONS §2「目录名=GitHub 仓名」两步改名），**HEAD = `484776c`**，**体积 21M**（含 `.git` 7.7M）。
> - 论文（**正文均未读**，仅仓库内引用）：[arXiv:2505.15155](https://arxiv.org/abs/2505.15155) RD-Agent(Q)（README 称 NeurIPS 2025 accepted，claimed_unverified）、[arXiv:2505.14738](https://arxiv.org/abs/2505.14738) 总体技术报告、[arXiv:2407.18690](https://arxiv.org/abs/2407.18690) Co-STEER。
> **读了什么**：`README.md` 全文（668 行 / 41,910 字节）；`docs/` 下**全部 20 个 `.rst/.md` 文档共 2,467 行**（`installation_and_configuration.rst` 527 行、`scens/data_science.rst` 566 行、`ui.rst` 209 行、`development.rst` 138 行、`scens/*` 7 篇、`research/*` 3 篇等，逐页读完无跳节；`docs/conf.py` 构建配置亦读）；**AST 模块地图**：`ast` 解析全部 571 个 `.py`（0 失败，wc 口径 72,845 行）；行级细读 6 组机制文件（见 §3，逐文件行号引用）；本项目 `docs/brief-plan.md` §4.4 / §6.2 / §12.0 / §12.1 W7 行（映射目标节，仅读不改）；格式范例 `docs/essay-study/harness2-2026.md`。
> **没读的（明确未读，不得当作依据）**：三篇论文正文（2505.15155 / 2505.14738 / 2407.18690——所有性能数字均为 README/docs 自报，**claimed_unverified**，未复现）；`test/` 36 个模块逐行；`web/` 前端（Vite/TS）；`rdagent/scenarios/` 331 个模块中除 qlib 关键文件外（data_science、kaggle 模板、finetune、rl、general_model 等）未逐行；`T()` 指向的提示词资产（各场景 prompts/yaml）未逐条读；`rdagent/log/ui/*`（Streamlit，`app.py` 1,134 行、`ds_trace.py` 1,199 行）与 `rdagent/log/server/app.py`（688 行）；`rdagent/oai/backend/base.py`（793 行，仅检索到 sqlite 缓存相关 3 处）；`docs/_static/` 图片与 `RD2bench.json`；`CONTRIBUTING/CHANGELOG/SECURITY/SUPPORT/TODO/Makefile/pyproject/requirements` 未通读。**未安装未运行**，故本笔记不含任何实测。

---

## 0. 一句话结论

RD-Agent 把「研究迭代」实现为一个**由元类收集步骤、可断点续跑的五步循环**（`direct_exp_gen`(propose+exp_gen) → `coding` → `running` → `feedback` → `record`），**没有独立的 decide 步**——实验是否采纳的 `decision` 由 LLM 在 `feedback` 步内产出，方向（factor/model）调度是**二臂 Thompson 采样**在下一轮 `propose` 入口做 `record→decide`；`coding` 步内部是 Co-STEER 多步进化（知识库三路检索：历史失败 trace / 组件图 / 错误图），实验记录以「Trace(hist+dag_parent) + 每步签名 pickle 快照 + 文件日志」持久化——**是文件快照库而非关系型实验数据库**。与本项目 §6.2 骨架、§12.1 W7 ②程序数据库/③假设树**多处机制同构，但 decide 语义与「任务 DAG」两处与二手文献口径有实出入**（见 §5），映射全部为候选参考、未采纳、未改 brief-plan。

## 1. 定位与文档口径

- **定位**（README L101-108 + `docs/introduction.rst`）：R=提新想法（Research），D=实现（Development），两者「effectiveness ultimately get feedbacks through practice」；`docs/project_framework_introduction.rst` L15-17 把循环描述为 propose hypothesis → design experiments → implement → execute → feedback，并自称「first scientific research automation framework that supports linking with real-world verification」（**claimed_unverified**，README/docs 自报）。
- **场景面**（README L478-513 + `docs/scens/catalog.rst`）：Finance（`rdagent fin_quant`/`fin_factor`/`fin_model`/`fin_factor_report`）、General（`general_model`、Kaggle、`data_science`）、FT-Agent（`llm_finetune`）；文档按 🦖copilot（听指令）/🤖agent（自主提想法）二分。
- **RD-Agent(Q) 口径**（README L86-94）：「first data-centric, multi-agent framework … coordinated factor-model co-optimization」；数字（README L92，**claimed_unverified**）：成本 <$10、相对 benchmark factor libraries **约 2× ARR、少 >70% 因子**；另有 MLE-bench 榜首表（README L66-78：o3(R)+GPT-4.1(D) All 30.22±1.5 vs AIDE o1-preview 16.9±1.1，**claimed_unverified**）。
- **框架组件图**：`docs/project_framework_introduction.rst` 附类级图（图片未解析，仅文字）；`docs/api_reference.rst` 只暴露 `rdagent.core.proposal` 一个 automodule——即 **Hypothesis/Trace/Feedback 抽象是官方钦定的 API 面**。
- **安全/工程约束**（`docs/development.rst` L88-138、`docs/installation_and_configuration.rst` L204-283）：生成代码按不可信输入处理；workspace 路径防穿越；归档解压拒 symlink/设备节点/>10,000 成员；`shell=False` + 禁 `eval()` 解析容器输出；持久化对象走 **HMAC 签名 envelope**（`RDAGENT_SIGNED_PICKLE_V1`），默认拒未签名 pickle，密钥 `~/.rdagent/artifact_signing.key`；容器结果跨进程用 JSON/Parquet/NPY 而非 pickle。
- **运行前置**（README L131-176，静态转述）：**仅支持 Linux**、Docker（免 sudo）、conda Python 3.10/3.11、`.env` 配 `CHAT_MODEL`/`EMBEDDING_MODEL`（LiteLLM 默认后端）、`rdagent health_check` 预检。本机（macOS）未装未跑。

## 2. 源码架构与 AST 模块地图

- **规模**：571 个 `.py` 全部 `ast` 解析成功（0 SyntaxError），wc 口径 **72,845 行**；分布 = `rdagent/` 534 + `test/` 36 + `docs/conf.py` 1。`rdagent/` 二层分布：`scenarios/` 331（大头，含 kaggle 模板）、`components/` 90、`app/` 48、`log/` 26、`utils/` 17、`core/` 14、`oai/` 8。
- **包布局**（`docs/development.rst` L36-66 官方分层）：`core`=抽象骨架（「All classes should be abstract」）、`components/`=可复用组件（多数 core 子类在此）、`scenarios/X`=场景特化（跨场景不可复用）、`app`=场景入口（删了不影响系统）、`scripts`=杂项候选。**RDLoop 本体在 `components/workflow/`，各场景 loop 在 `app/`**——与「骨架可搬、场景不可搬」的分层一致。
- **机制相关模块地图**（行数为 `wc -l` 实测；docstring 首行/类职责取自 AST）：

| 模块 | 行 | 职责（docstring 或代码摘） |
|---|---|---|
| `components/workflow/rd_loop.py` | 241 | `RDLoop`：「Model workflow with session control」；步骤 `direct_exp_gen`(内含 `_propose`+`_exp_gen`) / `coding` / `running` / `feedback` / `record` |
| `utils/workflow/loop.py` | 567 | `LoopMeta` 元类按定义序收集公共方法为 `steps`；`LoopBase`「Assumption: **The last step is responsible for recording information!!!!**」——会话 dump/load、skip/withdraw、并发信号量 |
| `app/qlib_rd_loop/quant.py` | 159 | `QuantRDLoop(RDLoop)`：按 `hypothesis.action∈{factor,model}` 分支 coder/runner/summarizer；`skip_loop_error=(FactorEmptyError, ModelEmptyError)` |
| `app/qlib_rd_loop/factor.py` | 66 | `FactorRDLoop`：`skip_loop_error=(FactorEmptyError, CoderError)`、**`skip_loop_error_stepname="feedback"`** |
| `app/qlib_rd_loop/conf.py` | 176 | `QuantBasePropSetting` 默认装配（`quant_hypothesis_gen=QlibQuantHypothesisGen`、factor/model 双 coder+runner+summarizer）；**`action_selection: str = "bandit"`**（L151-152） |
| `scenarios/qlib/proposal/bandit.py` | 109 | `Metrics`(8 维指标)/`LinearThompsonTwoArm`/`EnvController.decide`+`record`——二臂 Thompson 方向调度 |
| `scenarios/qlib/proposal/quant_proposal.py` | 179 | `QuantTrace`(持 controller) + `QlibQuantHypothesisGen.prepare_context`——bandit/llm/random 三档方向选择与上下文分层注入 |
| `scenarios/qlib/developer/feedback.py` | 186 | `QlibFactorExperiment2Feedback`/`QlibModelExperiment2Feedback`：`IMPORTANT_METRICS` 3 项对比 SOTA → JSON 反馈 |
| `core/proposal.py` | 471 | `Hypothesis`/`ExperimentFeedback`/`HypothesisFeedback`/`Trace`(hist+dag_parent)/`HypothesisGen`/`Hypothesis2Experiment`/`Experiment2Feedback`——官方 API 面 |
| `components/coder/CoSTEER/knowledge_management.py` | 1,055 | `CoSTEERKnowledgeBaseV1/V2`、`CoSTEERRAGStrategyV1`（docstring：**「it is deprecated」**）/`V2`（`former_trace_query`/`component_query`/`error_query` 三路检索） |
| `components/coder/CoSTEER/__init__.py` | 178 | `CoSTEER.develop`：`RAGEvoAgent.multistep_evolve` 多步进化 + `should_use_new_evo` 回退（fallback 到最佳可接受版本） |
| `components/coder/CoSTEER/config.py` | 42 | `max_loop=10`、`fail_task_trial_limit=20`、`v2_query_former_trace_limit=3`、`v2_query_component_limit=1`、`v2_query_error_limit=1`、`v2_knowledge_sampler=1.0` |
| `core/evolving_framework.py` | 187 | `EvoStep`/`EvolvingStrategy`/`IterEvaluator`/`RAGStrategy` 抽象（进化循环的底座） |
| `core/experiment.py` | 521 | `Task`/`Workspace`/`FBWorkspace`（文件工作区，含 `create_ws_ckp` 检查点）/`Experiment`/`ExperimentPlan` |
| `log/storage.py` + `core/serialization.py` | 118 + 104 | `FileStorage`（tag→目录、时间戳 `.pkl/.json/.log`）+ HMAC 签名 pickle（`_MAGIC=RDAGENT_SIGNED_PICKLE_V1`，密钥自动生成 0600） |

- **步骤推导（AST 实证）**：`LoopMeta.__new__`（`loop.py` L54-75）只收集**不以 `_` 开头**的可调用属性并排除 `load/dump`；`RDLoop` 的 `_propose/_exp_gen/_interact_*` 全部下划线开头 → 实际 `steps = ["direct_exp_gen","coding","running","feedback","record"]`。**代码里没有名为 `propose` 的步**（`quant.py` main 文档串里 `__session__/1/0_propose` 是旧步名残留，当前步名为 `direct_exp_gen`，会话文件名按 `loop.py` L308 `{loop_idx}/{step_idx}_{step_name}` 生成）。

## 3. 机制细读（6 组，行级）

### 3.1 M1：RDLoop 五步循环、并行编排与失败跳转（`rd_loop.py` + `loop.py` + `quant.py`/`factor.py`）

- **步序与数据流**：`direct_exp_gen`（L199-210）先按 `get_unfinished_loop_cnt < get_max_parallel()` 自旋等待并发额度，再 `_propose`（L184，`hypothesis_gen.gen(trace, plan)` → 可选人工 `_interact_hypo`）+ `_exp_gen`（L193），返回 `{"propose": hypo, "exp_gen": exp}`；`coding`（L212）→ `runner.develop`（L217）→ `feedback`（L222）→ `record`（L238）。`record` 把 `(exp, feedback)` 通过 `trace.sync_dag_parent_and_hist(...)` 入 Trace——**最后一步负责记录**是 `LoopBase` 的明文假设（`loop.py` L86-89）。
- **异常→feedback**：`_run_step`（`loop.py` L248-264）捕获 `skip_loop_error` 后：若配了 `skip_loop_error_stepname` 就跳那一步（**且禁止向后/原地跳**，L253-256），否则默认跳 `feedback`（存在时）或末步 `record`；异常对象存 `loop_prev_out[li][EXCEPTION_KEY]`。`feedback` 步（`rd_loop.py` L222-231）读该键：有异常就**不调 LLM**，直接构造 `HypothesisFeedback(reason=str(e), decision=False, ...)`——**失败也必须产出一条 feedback 记录**，与本项目 §6.2「失败跳 feedback、重进循环不终止」逐点同构。
- **并发纪律**：`get_semaphore`（`loop.py` L145-159）对 `record`/`feedback` **强制 limit=1**，注释给出理由：record 改全局环境、`(-1,)` 局部选择与 record 父节点要对齐——「prevent parallelism in `feedback` and `record` to avoid inconsistency」。`direct_exp_gen` 是唯一 async 步（用 `asyncio.sleep(1)` 让出）。
- **退出与恢复**：每步成功后立即 `dump()` 快照（L302-308，签名 pickle 落 `__session__/{li}/{si}_{name}`），所以 `load(path, checkout=True)` 可从任意步续跑（`quant.py` L144 文档串：`python .../quant.py $LOG_PATH/__session__/1/0_propose --step_n 1`）；`withdraw_loop` 把 `self.__dict__` 整体回滚到上一 loop 的快照（L407-425）；`step_n/loop_n/all_duration` 三类终止条件（L173-193）。`kill_subprocesses` 兜底强杀 `force_subproc` 孤儿进程（L546-567）。
- **Quant 分支**（`quant.py` L74-128）：`propose` 后 `assert hypo.action in ["factor","model"]`，四个步骤各自按 action 路由到 factor/model 两套 coder/runner/summarizer；`FactorEmptyError`（因子提取失败）在 `running` 抛出并由 `skip_loop_error` 接住跳 feedback。

### 3.2 M2：propose 入口的上下文分层注入（`quant_proposal.py`）

- `prepare_context`（L50-166）三档方向选择：**bandit**（默认，见 M3）/ **llm**（两次调 LLM 问 action）/ **random**；随后按 action 构造注入内容：
  - `hypothesis_and_feedback`：**action=="factor" 注入全部因子实验 + 最近一次被采纳（decision=True）的模型实验**；action=="model" 则注入全部模型实验 + 每类被采纳因子实验各一（L102-135，倒序遍历 `trace.hist`）——这是「按方向裁剪历史」的**结构化记忆注入**，对应本项目 propose 上下文「历史实验摘要」的现成实现样例。
  - `last_hypothesis_and_feedback`：最近一次**同向**实验（L138-143）；`SOTA_hypothesis_and_feedback`：仅 model 方向时取最近被采纳的模型（L145-152）。
  - `RAG`：两条**手写固定提示**（L92-97）——前 6 轮「先试最简单最快的因子」，之后「试高 IC 的 ML 因子、别和 SOTA 因子库重复」；model 方向则固定「用 GRU/LSTM、别用 GNN、按 478k/128k 样本设计超参」——**领域先验是硬编码字符串，不是学到的**（静态可核）。
- 假设对象 `QlibQuantHypothesis` 比基类多一个 `action` 字段（L23-43），`convert_response` 从 JSON mode 响应取 `hypothesis/reason/concise_*` 五段 + `action`。

### 3.3 M3：多臂老虎机方向调度（`bandit.py` + `conf.py`）

- **数据结构**：`Metrics` 8 维 = `[ic, icir, rank_ic, rank_icir, arr, ir, -mdd, sharpe]`（L21-33，**回撤取负**使「越大越好」统一）；指标从 `experiment.result` 抽取（L36-52），`sharpe = arr / -mdd`（L47，自定义口径）；键名含一个**尾随空格** `"1day.excess_return_with_cost.annualized_return "`（L44）——照抄时须原样保留（literal preservation）。
- **算法**：`LinearThompsonTwoArm`（L55-92）——两臂各持线性高斯后验（`mean` + `precision`），`sample_reward` 用 Cholesky 采权重算期望奖励（`LinAlgError` 回退后验均值），`update` 做秩-1 精度更新；`next_arm` 对两臂采样取 argmax。`EnvController`（L95-109）：`prior_var=10.0, noise_var=0.5, dim=8`，`reward = weights·metrics`，默认权重 `(0.1,0.1,0.05,0.05,0.25,0.15,0.1,0.2)`——**ARR 权重最高 0.25、Sharpe 0.2**。
- **调用时序**（`quant_proposal.py` L53-60）：只在**下一轮 propose 入口**执行：`record(上一轮 metrics, 上一轮 action)` → `decide(上一轮 metrics)`；**首轮固定 `action="factor"`**。即：反馈先入库、再选方向——方向决策**不在 feedback/decide 步**（源码没有该步）。
- **旁证**：Kaggle 场景另有一套 UCB（`scenarios/kaggle/proposal/proposal.py` L245「Select action with highest UCB」，开关 `if_action_choosing_based_on_UCB`，默认 False）——**同一仓库内「方向调度」有 bandit（qlib/quant 默认）与 UCB（kaggle 可选）两套实现**。

### 3.4 M4：feedback 上下文构造（`scenarios/qlib/developer/feedback.py` + `core/proposal.py`）

- **因子侧**（L54-118）：上下文四件——① 假设原文；② 每个子任务的 `get_task_information_and_implementation_result()`；③ **当前 vs SOTA 只保留 3 个 `IMPORTANT_METRICS`**（L17-21：`IC`、`1day.excess_return_with_cost.annualized_return`、`...max_drawdown`），由 `process_results` 拼成「metric of Current Result is x, of SOTA Result is y」一句话（L43-51）；④ 场景描述（`QlibQuantScenario` 时按 action 取因子/模型版）。请求走 `json_mode=True, json_target_type=Dict[str, str|bool|int]`（L95-100），解析出 `Observations/Feedback for Hypothesis/New Hypothesis/Reasoning/**Replace Best Result**` 五字段，`decision = convert2bool("Replace Best Result")`（L110）。
- **模型侧**（L121-186）：上下文改为 `SOTA_hypothesis + sota_task + sota_code(model.py 源码) + sota_result(3 指标) + hypothesis + exp + exp_result`（L148-157，失败时 `"execution failed"` 占位）；decision 字段名为 `Decision`（L185）。**注意 L159-179 同一 prompt 连调了两次 LLM、第二次结果覆盖第一次**（第一份 `response_json_hypothesis` 被立即丢弃）——静态可见的冗余调用，成本翻倍，走读如实记录。
- **反馈的数据形状**（`core/proposal.py`）：`HypothesisFeedback`（L96-134）= `decision + reason + code_change_summary + observations + hypothesis_evaluation + new_hypothesis + acceptable(+exception)`；`Trace`（L141-176）= `hist: list[(Experiment, ExperimentFeedback)]` + `dag_parent: list[tuple[int,...]]` + `idx2loop_id`，选择语法糖 `(-1,)=最近节点`、`(,)=新树根`；`get_sota_hypothesis_and_experiment`（L178-185）=倒序找第一个 `decision=True`。

### 3.5 M5：Co-STEER 知识库与失败案例检索（`knowledge_management.py` + `CoSTEER/__init__.py` + `config.py`）

- **两代知识库**：V1（L142-280）`implementation_trace + success_task_info_set`，查询=同任务历史失败 trace（截 `v1_query_former_trace_limit=3`）+ embedding 最相似成功任务 top-3；`CoSTEERRAGStrategyV1` 的 `generate_knowledge/query` 均 `raise NotImplementedError`，docstring 明写 **「we encourage everyone to use v2」**（L171/L184-186/L226-228）——**V1 已废弃但代码保留**。V2（L356-1055）是现行实现。
- **V2 检索三路**（`query` L433-457 串行调用）：
  1. `former_trace_query`（L532-593）：未成功且尝试次数 ≥ `fail_task_trial_limit=20` → 进 `failed_task_info_set`（**失败封顶**）；否则取最近失败 trace，且**先删「由成功转失败」的退化步**（L561-571，注释比作「wrong gradient descent」）；可选附上「最后一次失败尝试」防死循环（L574-584）。
  2. `component_query`（L595-723）：LLM 把任务映射到图中 `component` 节点（`analyze_component` L459-488，解析失败返回空表），沿图找 `task_description`→`task_success_implement`，再并 **embedding 相似成功任务**；`v2_knowledge_sampler` 是**按概率随机丢弃**（L689-696，不是多样性采样）；**「保证至少一半来自 GT」**（L698-721，`final_decision_based_on_gt` 配额）。
  3. `error_query`（L725-851）：从最近失败 trace 的**错误分析节点**出发（`analyze_error` L490-530 用正则抽 traceback 的 `ErrorType/Error line`，value 检查错误用 5 个固定模式匹配），图上找同错误的 `task_trace`→`task_success_implement`，产出 **(错误描述, (失败实现, 成功实现)) 三元组对**——这就是「失败案例检索」的本体：**给 LLM 看"同样报错的人后来怎么改成功的"**。
- **图谱结构**：`CoSTEERKnowledgeBaseV2`（L854-929）持 `UndirectedGraph`（持久化于 `Path.cwd()/graph.pkl`，L859），5 类节点 `component/task_description/task_trace/error/task_success_implement`；任务成功时 `update_success_task` 把 working trace 整链搬进图（L886-926）。
- **coding 步内的进化与回退**（`CoSTEER/__init__.py` L93-155）：`develop` 起 `RAGEvoAgent(max_loop=settings.max_loop=10)` 逐轮 `multistep_evolve`；每轮用 `should_use_new_evo`（L82-91：`new_fb.is_acceptable()` 即接受）维护 fallback 快照（`create_ws_ckp` 防原地变异），**最后回退到「最佳可接受」而非最后一轮**（L140-146）；全部子任务不可接受则抛 `CoderError` 汇总（L174-176）。

### 3.6 M6：实验记录与持久化（`Trace.record` + `LoopBase.dump` + `log/storage.py` + `core/serialization.py`）

- **三级落盘**：① 进程内 `Trace.hist/dag_parent`（实验→反馈的树）；② 每步 `dump()` 到 `__session__/{li}/{si}_{name}`（签名 pickle，可续跑/回滚）；③ `logger.log_object(obj, tag=...)` 经 `FileStorage.log` 按 tag 转目录、时间戳文件名落 `.pkl/.json/.log`（`storage.py` L40-73），`iter_msg` 按时间戳排序回放（L81-107），`truncate` 支持 checkout 后截断（L109-115）。
- **完整性**：`core/serialization.py` 对每份 pickle 附 HMAC-SHA256（`_MAGIC + digest + payload`，L64-67），加载时先验签再反序列化（L70-91），旧版未签名数据默认拒（`ALLOW_UNSAFE_LEGACY_PICKLE` 才放行）；密钥 0600 自动生成（L40-53）。
- **静态结论**：RD-Agent **没有关系型/SQL 实验数据库**——检索全仓仅 `oai/backend/*` 两处 sqlite（LLM 缓存）。「实验数据库」在本仓的对应物 = **Trace 树 + 逐步签名快照 + 文件日志 + Co-STEER 知识图谱**四件套；若本项目要 SQL 化（`goal_experiment`/`goal_trial_ledger`），记录**字段与语义**可借、**存储形态需自建**。

## 4. 与本项目的映射（静态同构比对；**逐条：候选参考、未采纳、未改 brief-plan**）

| # | 本项目目标节 | RD-Agent 对应机制（源码） | 关系 | 状态 |
|---|---|---|---|---|
| 1 | §6.2 ①propose/②coding/③running/④feedback 骨架 | `RDLoop` 五步 `direct_exp_gen→coding→running→feedback→record`（`rd_loop.py` L199-241） | **同构**：骨架可逐槽映射；差异=RD-Agent 第五步是 record（记录）不是 decide | 候选参考、未采纳、未改 brief-plan |
| 2 | §6.2「失败跳 feedback、重进循环不终止」 | `skip_loop_error` + `skip_loop_error_stepname="feedback"` + `EXCEPTION_KEY` 直构 `decision=False` 反馈（`factor.py` L18-19、`loop.py` L248-264、`rd_loop.py` L222-231） | **同构**：连「禁止向后跳」「失败也产反馈」都同口径 | 候选参考、未采纳、未改 brief-plan |
| 3 | §6.2 ⑤decide（授权范围→自动应用 / 否则审批门） | 源码**无 decide 步**；实验级 `decision` 内嵌 feedback（LLM `Replace Best Result`），另有 `EnvController.decide` 只选 factor/model 方向（`bandit.py` L103） | **差异（同名不同物）**：治理型 decide（审批门）RD-Agent 完全没有，须本项目自持 | 候选参考、未采纳、未改 brief-plan |
| 4 | §6.2 并发循环与顺序纪律 | `LoopMeta` 步骤收集 + `get_semaphore` 对 `record/feedback` 强制串行 + 每步快照（`loop.py` L145-159/L302-308） | **同族**：并发下的「记录一致性」口径可借 | 候选参考、未采纳、未改 brief-plan |
| 5 | §4.4 `goal_experiment`（P2）hypothesis→版本→结果→结论全程记录 | `Trace.hist[(exp,feedback)]+dag_parent+idx2loop_id`，每步 `__session__` 签名快照 + `FileStorage` 日志（`core/proposal.py` L141-176、`loop.py` L308、`storage.py`） | **同族**：记录字段/时序可借；存储为文件快照而非 MySQL 表，表结构需自建 | 候选参考、未采纳、未改 brief-plan |
| 6 | §4.4 `goal_experiment` 的 verdict/decision 字段形状 | `HypothesisFeedback(observations, hypothesis_evaluation, new_hypothesis, reason, decision, acceptable)`（`core/proposal.py` L96-134） | **同构**：六字段可直接对照 `verdict/reviewer_opinion/decision` 设计 | 候选参考、未采纳、未改 brief-plan |
| 7 | §12.1 W7 方向建议②「程序数据库：按高分+多样性采样历史版本做 propose 上下文」 | Co-STEER KB V2 成功/失败/组件/错误四桶+知识图谱（`knowledge_management.py` L854-929）与三路检索；propose 注入「全部同向历史+最近同向+SOTA」（`quant_proposal.py` L102-157） | **部分同构**：结构化持久记忆同构；**「高分+多样性采样」源码无对应**（`v2_knowledge_sampler` 是随机丢弃，历史注入按方向全量） | 候选参考、未采纳、未改 brief-plan |
| 8 | §12.1 W7 方向建议③「假设树：`goal_experiment.parent_experiment`+`hypothesis_class`」 | `Trace.dag_parent` 实验树 + `local_selection`/`(-1,)`/`NEW_ROOT` 选择语法（`core/proposal.py` L141-284；多父注释明写「not implemented yet」L157） | **同构（结构）/差异（分类）**：parent 链可借；`hypothesis_class`（参数/过滤/风控/信号）RD-Agent 无对应，仅 `action=factor/model` 二分 | 候选参考、未采纳、未改 brief-plan |
| 9 | §12.1 W7 方向建议（多臂老虎机方向调度） | `LinearThompsonTwoArm` 两臂 + `record→decide` 在 propose 入口、首轮固定 factor（`bandit.py` L55-109、`quant_proposal.py` L53-60、默认 `action_selection="bandit"` `conf.py` L151） | **同构**：时序（先记后选）与特征（8 维指标）可直接参照；实为**二臂**非多臂 | 候选参考、未采纳、未改 brief-plan |
| 10 | §12.0 W7「精读 RD-Agent feedback 上下文构造；demo=历史实验摘要注入 propose 提示词」 | 本笔记 §3.4（feedback 侧 3 指标对比 SOTA + JSON 五字段）与 §3.2（propose 侧分层注入）即该精读项的源码交付 | **同构**：直接对应 W7 精读任务，可作 demo 提示词协议的输入 | 候选参考、未采纳、未改 brief-plan |

映射共 **10 条**，全部静态比对：RD-Agent 未运行、本仓设计未因此改动、brief-plan 未改一字。

## 5. 与 §12.1 W7 二手结论的一致 / 出入（源码核对）

W7 行现有二手结论：「RD-Agent(Q)（2505.15155，NeurIPS 2025）：Research/Development/Feedback 循环，**Co-STEER（任务 DAG+失败案例知识库检索）**与**多臂老虎机方向调度**，**相对经典因子库约 2 倍年化、少 70% 因子**」。逐项核对：

**一致（3 项）**
1. **「约 2 倍年化、少 70% 因子」** ↔ README L92 逐句对应：「at a cost under $10, RD-Agent(Q) achieves approximately **2× higher ARR** than benchmark factor libraries while using **over 70% fewer factors**」。口径一致（措辞小差：brief-plan「经典因子库」↔ README「benchmark factor libraries」）。**该数字为 README/论文自报，本笔记未读论文正文、未复现 —— claimed_unverified。**
2. **「多臂老虎机方向调度」** ↔ 源码实证：默认 `action_selection="bandit"`（`conf.py` L151），`LinearThompsonTwoArm(dim=8)` 两臂 factor/model、8 维指标线性 Thompson、reward 加权点积（`bandit.py` L95-109），在 propose 入口 `record→decide`。一致（严格说 quant 场景是**二臂**；Kaggle 场景另有可选 UCB 多动作）。
3. **「Co-STEER 失败案例知识库检索」** ↔ 源码实证：`former_trace_query`/`error_query` 两路直接以失败 trace 与错误节点为键（`knowledge_management.py` L532-593/L725-851），`fail_task_trial_limit=20` 失败封顶，V1 已标 deprecated、V2 为现行。一致。

**出入（3 项，如实记录）**
1. **「任务 DAG」在源码无对应**：RD-Agent 的任务是 `Experiment.sub_tasks` **平铺列表**；DAG 只存在于**实验层** `Trace.dag_parent`（`core/proposal.py` L153），且注释明写多父「Multiple parent is not implemented yet」（L157）；Co-STEER 知识库是**无向图**（5 类节点），不是任务依赖 DAG。→ 二手表述应修正为「**实验 Trace 树 + 无向知识图谱**」，brief-plan §12.1 横向结论 3「按结构而非按时间存历史」仍成立，但结构形态需按实况描述。
2. **循环步序与 decide 不符**：源码步序是 `propose(exp_gen)→coding→running→feedback→record`，**没有独立 decide 步**；唯一的 `decide`（`bandit.py` L103）是下一轮 propose 入口的方向选择，实验采纳与否的 `decision` 由 LLM 在 feedback 步内产出（`Replace Best Result`）。brief-plan §6.2 的 ⑤decide = **授权范围/审批门（治理语义）**，RD-Agent 全仓无审批概念（docs 仅有 Web UI token 与生成代码安全边界）——**同名不同物**；落地时该步必须本项目自持，不能指望 RDLoop 现成实现（映射表 #3）。
3. **「Research/Development/Feedback 循环」是文档层口径**：README/`introduction.rst` 确为 R/D 二分叙事，但代码层没有名为 Research/Development/Feedback 的步（feedback 步存在、R/D 是组件分类）；且 `docs/scens/data_agent_fin.rst` 把场景步序写成 6 步（Hypothesis→Factor Creation→Implementation→Backtest→Feedback→Refinement）与代码 5 步不一一对应。→ 引用时宜写「**代码五步（…→feedback→record）**」而非循环名。

（附注：README 的 MLE-bench 表、$10 成本、NeurIPS 2025 接收，docs 的「bench_test_round=10 约 2 小时」等全部为项目自报，**claimed_unverified**。）

## 6. 运行前置（文档静态转述，未跑）

- Linux + Docker（免 sudo）+ conda py3.10/3.11 + `pip install rdagent` 或 `make dev`；`.env` 配 `CHAT_MODEL`/`EMBEDDING_MODEL`（LiteLLM，DeepSeek/Azure 例齐备）；`rdagent health_check` 先行。
- 量化场景数据面：Qlib 本地数据 `~/.qlib/qlib_data/cn_data`，默认时间切分 train 2008-01-01~2014-12-31 / valid 2015~2016 / test 2017-01-01~2020-08-01（`docs/scens/quant_agent_fin.rst` L80-92），CSI300 + `TopkDropoutStrategy`（top50 drop5）回测 2017~2020-08、初始资金 1e8（L104-108）；时间窗可用 `QLIB_FACTOR_*` 等环境变量覆盖（`installation_and_configuration.rst` L286-368）。
- 知识库/缓存开关：`FACTOR_CoSTEER_knowledge_base_path`/`new_knowledge_base_path`、`max_loop`（默认 10）、`fail_task_trial_limit`（默认 20）；LLM 缓存 sqlite（`prompt_cache.db`，docs 配置表 L487-505，claimed_unverified 为文档默认值）。
- 本机未安装、未运行，**本节不含任何实测**。

## 原文链接

- 仓库：https://github.com/microsoft/RD-Agent （本地 `oss-repos/RD-Agent`，HEAD `484776c`，21M）
- 论文：https://arxiv.org/abs/2505.15155 ｜ https://arxiv.org/abs/2505.14738 ｜ https://arxiv.org/abs/2407.18690 （均未读正文）
- 关键文件：`README.md`、`docs/`（20 篇 .rst/.md）、`rdagent/components/workflow/rd_loop.py`、`rdagent/utils/workflow/loop.py`、`rdagent/app/qlib_rd_loop/{quant,factor,conf}.py`、`rdagent/scenarios/qlib/proposal/{bandit,quant_proposal}.py`、`rdagent/scenarios/qlib/developer/feedback.py`、`rdagent/core/{proposal,experiment,evolving_framework,serialization}.py`、`rdagent/components/coder/CoSTEER/{__init__,knowledge_management,config}.py`、`rdagent/log/storage.py`

## 核验附注

（留空，供回源核验时填写）
