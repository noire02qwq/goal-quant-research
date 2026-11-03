# bot 的计算机（The bot's computer）

> 来源：https://github.com/elie222/rakazo/blob/main/docs/computer.md
> 原文：oss-repos/rakazo/computer.md
> 翻译日期：2026-11-03 ｜ 范围：全文 ｜ 方式：机器翻译初稿，未经人工校对
> 引用于：docs/essay-study/rakazo-2026.md、docs/brief-plan.md §3/§3.1
每个 bot 都有一台真正的计算机，带浏览器、终端、文件和桌面，因此能完成光靠聊天做不了的工作。

## 看它干活

点聊天顶部的 **Agent computer**，bot 的屏幕会开在对话旁边。选 **Open in full window** 视野更大。计算机在 bot 需要时启动，空闲时休眠；打开它就会唤醒。

在手机上，打开 bot 的 profile，选 **Open computer**。

## 接管操作

选 **Take control** 亲自使用屏幕，比如登录某个网站。在你选 **Release control**（手机上是 **Release**）之前，头部一直显示 **You have control**。

遇到只有你才能做的事，比如 CAPTCHA 或发到你手机的验证码，bot 会请你接手。头部显示 **Needs you**。做完这一步后选 **I'm done**；选 **Skip** 则让 bot 跳过这步继续。

> [!TIP]
> 下次想让 bot 自己登录？让它保存登录凭据。参见[可复用凭据](./bot-secrets.md)。

## Team 还是 Private

Bot 设置 **Advanced** 下的 **Computer** 可选 **Team** 或 **Private**。

- **Team**（默认）：[space](./spaces.md) 里的 bot 共享一台 Team Computer，文件和已装工具相同。每个 bot 有自己独立的屏幕和浏览器，你登录过的网站会带到其他 bot 那里。
- **Private**：bot 独享一台计算机。文件或登录凭据不能与其他 bot 共享时使用它。

## 文件

Bot 把工作成果存在计算机上，并以文件形式在聊天里发给你。Bot 发过的每个文件也在账户菜单的 **Artifacts** 下。

想让 bot 对文件变化作出反应，用[监视某个文件夹的 routine](./routines.md)。

## 修理计算机

打开计算机，选 **More computer actions**：

- **Stop computer**：立刻关机，需要时再启动。
- **Update computer**：保存工作区并安装当前软件。
- **Recover computer**：重建一台出故障的计算机。
- **Reset computer**：回到上次保存的工作区。计算机上未保存的工作会丢失。

## 使用你自己的计算机

在[桌面 app](./desktop-app.md) 里，bot 也可以在安装了该 app 的计算机上执行命令。在 **Settings → General** 的 **Computers** 下打开 **Let bots use this computer**。在任何[审批模式](./approvals.md)下，bot 在一个 space 里执行第一条命令前、以及首次使用该 space 里每个应用前都会询问，除非有 Block 规则直接拒绝。**Allow in this space** 覆盖该 space 之后的所有聊天，直到你把这台计算机从同一列表移除。

> [!WARNING]
> 有权访问你计算机的 bot 能以你的身份读取文件、运行程序。只对那些你愿意让 bot 无人值守使用的计算机打开这个开关。
