# 独立 demo 应用区

这里放**需要独立仓库承载**的 demo 应用。本仓库只跟踪索引 README，不跟踪 demo 本体代码。

## 约定

- **默认去 `../research-demos/`**：brief-plan 定稿之后的研究 demo 一律入库本仓库；只有确实需要独立仓库/独立生命周期的 demo 才放这里（docs/CONVENTIONS.md §4）。
- 每个 demo 目录自带独立 git 仓库与自己的 GitHub 远端；本仓库 `.gitignore` 中排除其目录。
- 更新 demo 本体：进入该目录 `git add/commit/push`，与本仓库无关。
- 新增 demo：在本 README 追加一行索引 + 在根 `.gitignore` 追加排除规则。

## 索引

| Demo | 用途 | 独立仓库 |
|---|---|---|
| `vn-demo/` | vnpy（VeighNa）回测集成验证：策略模板、数据源适配、双均线出标准统计 | [noire02qwq/vnpy-demo](https://github.com/noire02qwq/vnpy-demo) |
