# Harness²（google-research/harness2）源码走读笔记

> **状态**：已完成静态走读（README/docs 全文 + AST 模块地图 + 关键机制行级细读；**未安装、未运行、未跑 demo**——需 Linux/Python 3.12/uv 与 Vertex 凭据，本机未配置）。
> **走读日期**：2026-11-10（@user 指令「oss repos 研究一下 google research harness2」）。
> **材料与版本**：
> - 仓库：[github.com/google-research/harness2](https://github.com/google-research/harness2)（Apache-2.0，创建于 2026-10-06；web 搜索快照显示 23,350 stars / 161 open issues——页面数值未二次核验）。
> - 本地克隆 `oss-repos/harness2`（`.gitignore` L47 `oss-repos/` 覆盖，不入库），`--depth 1`，HEAD = `6868817`（2026-11-02），pack 6.83 MiB。
> - 论文：[arXiv:2610.14224](https://arxiv.org/abs/2610.14224)《Harness²: Recursive Agent Harnessing for an Open World》（摘要经 `export.arxiv.org` API 抓取；**论文全文未读**）。官网 harness2.github.io 未访问。
> **读了什么**：`README.md` 全文（209 行）；`docs/SETUP.md`（172 行）、`docs/EXPERIMENTS.md`（122 行）全文；`harness2/` 包 11 个核心模块的 AST 模块地图（类/函数 + docstring 全量）；`tree.py`/`context.py`/`selection.py`/`library.py`/`config.py` 关键函数行级细读；`substrate/opencode.py`、`substrate/codex.py` 两份 SurfaceSpec 定义；arXiv 摘要。
> **没读的（明确未读，不得当作依据）**：`core/prompts.py`（1,163 行）逐行、三个 benchmark adapter 实现（`jobbench.py` 1,184 行等）、`schedule.py`（918 行）逐行、`tests/`、`docs/BENCHMARKS.md` 全文、`third_party/`、论文正文。**未运行任何命令**——所有性能数字为 README/arXiv 摘要自报（claimed_unverified，未经独立复现）。

---

## 0. 一句话结论

Harness² 把 harness 本身当作可递归优化的对象：模型权重不动，**任务级**用无真值反馈的对比式 Propose–Probe–Compose 改当前任务的 harness，**harnessing 级**把采纳的 harness 与证据支撑的教训沉入按域经验库供后续任务读取。其 c1–c8 可编辑面（含「plugin 是模型唯一跳不过的强制杠杆」）、盲选与评测时序分离、答案键/grader 判决三道 tripwire、SCRUB_ENV 秘钥剥离，与本项目决策 0002/0003/0005 及 W3/W4 文献结论**多处机制同构**——是 harness-hub 恢复开发时最值得对照的开源实现（注意：本仓 harness-hub 是公司内部平台，与 Harness² 同名域不同物，本笔记仅作机制参照）。

## 1. 定位与论文口径

- **harness 定义**（README L19-21）：模型周围使其能作为 agent 行动的系统——prompts、tools、memory、skills、orchestration 等；**harnessing** = 优化该系统的过程。
- **开放世界两挑战**（arXiv 2610.14224 摘要）：①开放世界任务在 harness 设计期未见、测试期新颖，**没有真值 verifier 可靠引导在线编辑**；②RSI 过程高度任务特化，难泛化到新场景。
- **两层递归**（权重固定）：任务级 = 对比式 **Propose–Probe–Compose**（提编辑 → 同任务探测 → 从执行行为对比合成精化 harness，无 ground-truth 反馈）；harnessing 级 = 持续更新 *improvement harness*（采纳的 harness + 证据支撑教训）指导未来精化。
- **数字**（README L41-45 与 arXiv 摘要两处一致，均自报未复现）：单步 Harness² 在三个专业基准、四个 model–harness 配置上提升 GLM-5 与 Gemini 3.5 Flash——WorkBuddy-Bench 最多 **+11.5** 点、JobBench **+4.5** 点、LAB partial pass rate **+11.8pp**；增大任务级递归预算（k）继续上涨。
- **交付面**（README L47-48）：parallel / sequential 两递归模式、OpenCode 与 Codex 执行器、JobBench / LAB / WorkBuddy-Bench 三基准。

## 2. 源码架构

- **规模**：59 个 `.py` / **16,094 行**（不含 `third_party/`）；`tests/` 20+ 文件；`docs/` 3 篇共 418 行。
- **包布局**：`harness2/core`（方法本体）、`benchmarks/`（三个 adapter + 判分 + 渲染）、`substrate/`（OpenCode/Codex 适配与 c1–c8 surface）、`cli/`（`harness2` / `harness2-judge` / `harness2-report` / setup / check / demo）、`config.py`、`install.py` / `preflight.py` / `demo.py`。
- **core 模块地图**（行数为实测）：

| 模块 | 行 | 职责（docstring 摘） |
|---|---|---|
| `recursion.py` | 589 | 两模式任务级递归；`run_parallel`「WIDTH: 2k iid candidates from shared evidence, then k INDEPENDENT compositions」、`run_sequential`「DEPTH: k nested passes」 |
| `proposer.py` | 527 | improver 会话（隔离工作区 + 审计轨迹 + 缓存；`_call_fingerprint` 内容寻址，含 evidence 与 mode/task 路径；`ProposerError` 明确「never swallowed into an empty string」） |
| `selection.py` | 505 | 匿名盲选 + 采纳后反思蒸馏 |
| `context.py` | 546 | 证据树——「**The only way evidence reaches a model**」+ 三道 tripwire |
| `tree.py` | 427 | c1–c8 组件树读/写/校验/diff，`SurfaceSpec` 参数化 |
| `library.py` | 222 | 按域经验库 R（harnessing 级落盘） |
| `spec.py` | 277 | benchmark 接缝——「Implement these and the whole method works. **Nothing here is method logic.**」；`RunView`「Never carries a score.」 |
| `schedule.py` | 918 | 命名空间、种子化任务流、task/domain/sweep 驱动与 resume |
| `judge.py` | 171 | 「Measurement of the run that selection chose, **after it chose it**.」 |
| `runmark.py` | 177 | 试验身份：harness 指纹 + inputs 指纹 + 完成标记 |
| `prompts.py` | 1,163 | 提示词资产（**未逐行读**） |

## 3. 机制细读（重点）

### 3.1 两层递归与两模式（`recursion.py` + `docs/EXPERIMENTS.md` L8-19）

- 两模式都从**同一 base harness 的 k 次参考执行**起步。parallel：提/探 k 个 general（invariant）候选 + k 个 domain 候选，k 个**独立** composition 各自用全候选池与执行证据产出精化 harness；sequential：k 个 Propose–Probe–Compose 步进，精化 harness 与累积证据带入下一步。
- 鲁棒口径：`_roll`「A dead rollout is recorded, **never raised**」；`_run_stage` 对无效提案**重试一次**（`STAGE_ATTEMPTS`）；`_accept_tree` 先修复再校验。
- 成本警示（EXPERIMENTS L46-48）：LAB 全任务流 **1,143** 个，先用 `--only-domains`/`--max-tasks`（按域封顶）小选并核对模型价格；`--dry-run` 无模型调用预览；`--seed` 只打乱任务流、不控制模型采样。

### 3.2 c1–c8 可编辑面（`tree.py` `SurfaceSpec` + `substrate/`）

- **八组件**（README L70-71 顺序）：system prompt、guardrails、memory、tool guidance、subagents、skills、scripts、plugins。代码内 stub 注释直接确认 **c5=subagents、c6=skills、c7=scripts、c8=plugins**（`opencode.py` L72/83/67/78）；**c1–c4 按 README 顺序对应四份 always_on 文件**（`systemprompt.md` / `guardrails.md` / `LongTermMEMORY.md` / `tool_descriptions/tool_guidance.md`，`opencode.py` L44-49）——此映射为**顺序推定**，代码无注释直证。
- **预算帽与理由同写**：OpenCode `always_on_max=24_000`，理由「every token here competes with the agent's own output budget」（L50-51）；Codex `8_000`，理由「AGENTS.md is injected whole into EVERY turn, and codex additionally truncates it silently at 32,768 bytes」（`codex.py` L42-46）。
- **唯一强制杠杆**：plugin 注释「Acts INSIDE the tool loop -- **the only lever that can enforce something the model cannot skip**」（`opencode.py` L78-79）；Codex 侧 c8 = `.codex/hooks.json` 十个生命周期事件（PreToolUse/PostToolUse/PermissionRequest/PreCompact/PostCompact/SessionStart/SubagentStart/SubagentStop/UserPromptSubmit/Stop，`codex.py` L59-72）。
- **校验与多样性**：`validate()` 聚合全部问题一次抛（skill frontmatter、subagent、script 引用缺失、py 编译、hooks schema）；`autotrigger()` 给每个 skill 在 always-on 文本补触发行；`diversity()` 对候选树两两 line-Jaccard，**「so collapse to one body is visible」**（`tree.py` L407-408）。

### 3.3 防泄漏三道 tripwire（`context.py`）

1. `assert_no_leak_paths`（L399-411）：benchmark **声明的答案键路径模式**，fnmatch 命中即拒——在任何上下文到达模型之前。
2. `assert_no_grader_verdicts`（L454-465）：grader 自己的输出按**文件名 + 内容**双查；docstring 明言「A tripwire on the adapters' read boundary, **not the defence itself**: if it fires, find the read path that produced the match rather than widening the marker list」——触发时修读路径，**不许扩名单了事**。
3. `assert_tree_has_no_grader_verdicts`（L493-506）：对 **agent 自写的 harness 树**在 rollout/入库前同检（`library.add` L122-123 对 harness 与 EXPERIENCE 双检）——带判决的树「could never afterwards be served as evidence」。
- **网络侧同主题且自曝**（EXPERIMENTS L95-109）：三基准全公开、JobBench 在 Hugging Face 公开每任务 `RUBRICS.json`；「In a validation run of this release, **a Codex rollout on JobBench downloaded its task's rubric without being instructed to**」。对策 = setup 后在执行器主机网络层封锁 `huggingface.co`/`hf.co`/`github.com`/`raw.githubusercontent.com`（Codex sandbox 是关闭的，须 egress 防火墙/DNS 而非工具设置），并**随结果报告封锁方式**。

### 3.4 盲选 → 评测时序分离（`selection.py` + `judge.py`）

- **匿名**：候选渲染为 A..Z 各一文件（`assign_ids` = canonical sort + 种子洗牌，「stable across reruns」L72-76）；非答案先剔除并记录 `dropped` 及原因；每个候选**不裁剪**（`_write_candidates`「anonymised, untrimmed」）。
- **选择器只见匿名池**；回执解析为结构化标记——choice 代码块与 `<why>` 标签（正则见 `selection.py` L33-36）。
- **失败中性回退**：`_fallback`「The neutral stand-in after a selector failure: a delivered base, else the first final」（L237-238）；`run_selection` docstring「never raises」。
- **评测后置**：`judge.py` 模块 docstring——只测量 selection **选择的那一个**、且在**它选择之后**；`spec.RunView`「Never carries a score」（选择阶段模型看不到分数）。
- **反思蒸馏**：`reflect_adoption`（L402）在采纳后建证据树（chosen harness vs base vs pool 候选）；`_distil`（L454-475）「Extract a **supported** lesson from the complete task-local improvement record」——mission 注入采纳理由、匿名 ID 映射、要求先读 decisions 与执行对比再写。

### 3.5 按域经验库 R（`library.py`，harnessing 级落盘）

- 一个 (run, domain) 一库，「**read before each task, appended after**」；域内任务保序、**只读更早条目**（EXPERIMENTS L16-19），域间可 `--workers` 并发；库按 benchmark/executor/mode/k/seed 隔离。
- `add()`：`has_experience` 为空则**不入库**（防空教训）→ grader 判决双检 → 写盘；`rebuild_index()` **从磁盘重建** INDEX.md（不信任内存态）；`forget()`/`retain()` 支持重放修正（`_restore_libraries` 可把跳过的任务从已选 harness 回放进库）。

### 3.6 试验身份与复用（`runmark.py`）

- `fingerprint()` = harness 树稳定摘要（`None` = base）；`inputs_fingerprint()` = 「what the agent was asked and **what it was given**」的摘要；`is_complete()` 复用判据 = 当前标记 + 同一 inputs；`why_not()` 给日志一句可读解释。——**身份绑定到「输入 + 配置」**，与本项目 0002 `goal_receipt`/认领、0005 use-time 绑定同族。

### 3.7 秘钥剥离（`config.py` `SCRUB_ENV` + `docs/SETUP.md` L41-46）

- `SCRUB_ENV` 共 **21 项**：`HARNESS2_JUDGE_API_KEY`/`BRIDGE`/`CODEX`、Anthropic 五项（API key/token/base URL/Bedrock/`CLAUDE_CODE_USE_BEDROCK`）、`OPENAI_API_KEY`、Gemini 四项、`GITHUB_TOKEN`/`GH_TOKEN`、Slack 两项、`JIRA_API_TOKEN`、AWS 四项（`config.py` L193-215）。
- `scrub_env()` 返回剔除副本，`keep` 显式白名单；SETUP L41-46：**agent 与 judge 不继承**列表内 token——「Each keeps only the key its own model call needs, so a harness tool that needs another listed token, such as `GITHUB_TOKEN`, does not receive it」；列表外变量原样透传；本地 helper（render bridge）仍拿全量环境。

## 4. 与本项目的映射（静态同构比对；**候选参考、未采纳，未改 brief-plan**）

| Harness² 机制 | 本项目对应 | 关系 |
|---|---|---|
| c8 plugin/hook「模型唯一跳不过的强制」 | 0005 采纳④「模型之下 deterministic monitor 唯一防线」、§12.2 W4 ⑤ | **同构**：同论点（强制只能在 tool loop 内）的开源实现证据 |
| 三道答案键/grader tripwire + 「tripwire≠防线」措辞 + 网络 egress 自曝 | 0004 采纳①② 前视三层防护、W3 笔记「审计只证明它证明的那件事」 | **同族**：构造性拒入；与「必要条件不写成充分条件」口径一致 |
| 匿名盲选 + judge 后置 + `RunView` 不带分数 | 0005 采纳④ judge 零耦合、§12.2 ⑦ | **同构**：评测不参与选择 |
| 按域经验库 + 「supported lesson」蒸馏 + 空教训不入库 | 0003 记忆蒸馏、0002 恢复语义 | 同族；「只读先前条目」= 因果顺序纪律 |
| `inputs_fingerprint`（asked + given） | 0002 `goal_receipt`、0005 use-time 绑定 | 同族：身份 = 输入 + 配置摘要 |
| `SCRUB_ENV` + keep 白名单 | 0005 采纳② 通道隔离（demo 为最小验证形态，平台侧参照） | 可直接借名单结构 |
| always-on 预算帽 + 理由同写（24k/8k） | 本项目 memory/skill 注入预算（§5.4，W5+） | 参考：帽与理由成对记录 |
| `diversity()` line-Jaccard 塌缩可见 | 暂无对应 | 可借鉴：防 harness 候选塌缩 |
| 失败评测 unscored ≠ 0、JobBench revision 随报、`--dry-run` | 复盘 P5/P7 诚实口径、CONVENTIONS 数字可溯 | 同价值观 |

注：以上为**静态比对**——harness2 未运行、本仓设计未因此改动；harness-hub（公司平台，搁置中）恢复开发时可作对照实现清单。

## 5. 运行前置（文档静态转述，未跑）

- README L83-94：**Linux、Python 3.12、uv**；`uv venv --python 3.12 .venv` → `uv pip install -e '.[render]'` → `harness2-demo --output runs/demo --k 2`——本地 demo 用确定性编辑器 + 真实 Python 执行，**无需模型凭据**。
- 模型侧（SETUP）：Node.js 20+、Google Cloud CLI（`gcloud auth application-default login`）、Vertex 项目与模型 ID；LAB 需 Pandoc + Poppler、WorkBuddy 需 Docker；`harness2-check --bench <b>` 预检；`HARNESS2_SOLVER_MODEL`/`IMPROVER_MODEL`/`JUDGE_MODEL` 三通道配置。
- 评测前须配置网络限制（见 §3.3），且随结果报告。
- 本机未装 uv 环境、未跑 demo/benchmark——**本节不含任何实测**。

## 原文链接

- 仓库：https://github.com/google-research/harness2 （本地 `oss-repos/harness2`，HEAD `6868817`）
- 论文：https://arxiv.org/abs/2610.14224 ｜ 官网：https://harness2.github.io
- 关键文件：`README.md`、`docs/SETUP.md`、`docs/EXPERIMENTS.md`、`harness2/core/{recursion,proposer,selection,context,tree,library,spec,schedule,judge,runmark}.py`、`harness2/substrate/{opencode,codex}.py`、`harness2/config.py`
