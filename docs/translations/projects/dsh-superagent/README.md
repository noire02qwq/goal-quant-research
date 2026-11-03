# dsh-superagent 项目自述（dsh-superagent）

> 来源：https://github.com/deepseek-ai/dsh-superagent-prototype/blob/main/README.md
> 原文：oss-repos/dsh-superagent-prototype/README.md
> 翻译日期：2026-11-03 ｜ 范围：全文 ｜ 方式：机器翻译初稿，未经人工校对
> 引用于：docs/essay-study/deepseek-super-agent-2026.md

**仅供研究参考的原型，不是 DeepSeek 官方产品。** 这份代码出自我们团队的日常开发工作，其中很大一部分工程工作是 coding agent 做的。请把它当作研究代码，而不是可直接投产的软件。它可能仍有 bug，编码风格和工程实践也可能前后不一致。在自己的环境中使用之前，请先审查，并按需调整。

我们为发布做了改编，所以它既不等同于内部版本，也不等同于 *Exploring Super-agent Design: Towards a More Autonomous Agent System* 一文中所描述的实现。文中讨论的某些设计属于未来的发展方向，并未在这个原型里实现。

dsh-superagent 是一个面向单一 GitHub 仓库的主动式 coding agent，以 bundle 的形式打包给 [DeepSeek Harness](https://www.deepseek.com/en/harness/)。它监听 GitHub，也可以选配监听飞书。当某个被允许的人给 agent 派活时，它会开一个 work item，在自己的 agent session 和目录里干活，再回到原对话里给出答复——比如一个 pull request。一个网页面板会显示哪些事情需要人来处理。

它也是一种与 agent 共事的方式：**占的人的注意力尽可能少，给的价值尽可能大。** 一个能替整个团队行动的 agent，也能浪费整个团队的注意力。所以它只在被要求时、或团队写下的某条规则允许时才行动，只在必须有人出手、或有人能用上结果时才开口。[docs/000-philosophy.md](docs/000-philosophy.md) 解释了这条原则，以及它对操作者提出的要求。

## 安装配置（Setup）

安装配置步骤很多，所以让一个 agent 陪你一起做。对你的 coding agent 说：

> 读这个仓库里的 SETUP.md，和我一起把 dsh-superagent 配置好。

它每次只问一个简短的问题，先把完整计划展示一遍，然后安装并配置好所有东西。它遵循的是 [SETUP.md](SETUP.md)。

## 文档（Documentation）

按编号顺序读这些文档；每一篇只建立在它前面几篇的基础上。

- [000 哲学](docs/000-philosophy.md)
- [001 领域模型](docs/001-domain.md)
- [002 授权](docs/002-authorization.md)
- [003 执行](docs/003-execution.md)
- [004 提示词](docs/004-prompts.md)
- [005 面板](docs/005-panel.md)
- [006 部署](docs/006-deployment.md)：手动安装、配置、升级与故障排查
- [007 架构](docs/007-architecture.md)
- [008 实践手册](docs/008-cookbook.md)：新增一个 Source

## 开发（Development）

`pnpm check` 会依次跑类型检查、测试和构建。

## 许可（License）

[MIT](LICENSE)
