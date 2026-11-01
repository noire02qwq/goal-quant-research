# 独立 demo 应用区

这里放**可长期运行、需要独立仓库承载**的 demo 应用。本仓库只跟踪索引 README，不跟踪 demo 本体代码。

## 约定

- 每个 demo 目录自带独立 git 仓库与自己的 GitHub 远端；本仓库 `.gitignore` 中排除其目录。
- 更新 demo 本体：进入该目录 `git add/commit/push`，与本仓库无关。
- 新增 demo：在本 README 追加一行索引 + 在根 `.gitignore` 追加排除规则。
- 短期一次性研究 demo（spike）**不放这里**，放本地 scratch（见根 README 与 docs/CONVENTIONS.md §4）。

## 索引

| Demo | 用途 | 独立仓库 |
|---|---|---|
| `vn-demo/` | vnpy（VeighNa）回测集成验证：策略模板、数据源适配、双均线出标准统计 | [noire02qwq/vnpy-demo](https://github.com/noire02qwq/vnpy-demo) |
