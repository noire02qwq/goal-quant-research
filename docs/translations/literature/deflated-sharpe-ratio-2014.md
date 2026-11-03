# 去膨胀 Sharpe 比率与回测过拟合概率（The Deflated Sharpe Ratio / The Probability of Backtest Overfitting）

> 来源：DSR — https://ssrn.com/abstract=2460551 ｜ 作者站 PDF（本机实际抓取到摘要的来源）https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf ；PBO — https://ssrn.com/abstract=2840838 ｜ 作者站 PDF https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf
> 原文：未下载（仅摘要级引用；两篇均只取摘要，PDF 仅用于读取摘要页）
> 翻译日期：2026-11-03 ｜ 范围：摘要级 ｜ 方式：机器翻译初稿，未经人工校对
> 引用于：docs/brief-plan.md

## 1. The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting and Non-Normality

> 来源同上（DSR）。SSRN 摘要页对本机抓取返回 Content Blocked，摘要文本取自作者站公开 PDF 的 Abstract 页，内容与 SSRN 摘要一致。

### 摘要

近年来，随着大规模金融数据集、机器学习与高性能计算的出现，分析师已经可以对数百万（甚至数十亿）个备选投资策略做回测。回测优化器会搜索能让策略模拟历史绩效最大化的参数组合，从而导致回测过拟合。

绩效虚高的问题并不止于回测。更一般地，研究者与投资经理倾向于只报告正向结果，这种现象称为选择偏差（selection bias）。若不对某项发现所涉及的试验次数加以控制，就会带来过于乐观的绩效预期。

Deflated Sharpe Ratio（DSR）针对两类主要的绩效虚高来源做修正：多次检验下的选择偏差，以及非正态分布的收益。借此，DSR 有助于把真正的实证发现与统计侥幸区分开。

- **关键词**：Sharpe ratio、Non-Normality、Probabilistic Sharpe ratio、Backtest overfitting、Minimum Track Record Length、Minimum Backtest Length
- **题录**：David H. Bailey, Marcos López de Prado；Journal of Portfolio Management 40(5), pp. 94–107, 2014（40 周年特刊）；成稿日期 2014-07-31

## 2. The Probability of Backtest Overfitting（PBO / CSCV）

> 来源同上（PBO）。SSRN 摘要页对本机抓取返回 Content Blocked，摘要文本取自作者站公开 PDF 的 Abstract 页。

### 摘要

许多投资公司与组合管理者依赖回测（即基于历史市场数据的绩效模拟）来选择投资策略并分配资金。为防止回归过拟合而设计的标准统计技术——例如留出法（hold-out）——在投资回测的语境中往往并不可靠、也不准确。

我们提出一个评估回测过拟合概率（PBO）的一般框架，并在投资模拟的语境下给出具体、通用、无模型且非参数的实现，称之为组合对称交叉验证（combinatorially symmetric cross-validation，CSCV）。我们表明，CSCV 在若干有用的算例上都能给出合理的 PBO 估计。

- **关键词**：backtest、historical simulation、probability of backtest overfitting、investment strategy、optimization、Sharpe ratio、minimum backtest length、performance degradation
- **题录**：David H. Bailey, Jonathan Borwein, Marcos López de Prado, Qiji Jim Zhu；Journal of Computational Finance（Risk Journals），2015/2017；本机读取的 PDF 版本标注 2015-02-27（2015 年 2 月修订版）；SSRN 2840838（另有 2013 年首发版 SSRN 2326253）
