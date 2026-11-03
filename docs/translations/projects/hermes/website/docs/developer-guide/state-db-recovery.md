# 状态数据库与 FTS 恢复（State database and FTS recovery）

> 来源：https://github.com/NousResearch/hermes-agent/blob/main/website/docs/developer-guide/state-db-recovery.md
> 原文：oss-repos/hermes-agent/website/docs/developer-guide/state-db-recovery.md
> 翻译日期：2026-11-03 ｜ 范围：全文 ｜ 方式：机器翻译初稿，未经人工校对
> 引用于：docs/essay-study/hermes-2026.md、docs/brief-plan.md §3

关于面向用户的完整操作指引（该停什么、`state.db` 旁边的文件各是什么、为什么维护命令在写入方存活时会拒绝执行），见 [Session storage recovery](../user-guide/session-storage-recovery.md)。

`state.db` 里存着两类不同的数据：

- `sessions` 与 `messages` 是权威的会话记录（canonical transcript）。
- `messages_fts*` 表及其同步触发器是派生的搜索索引。

派生索引可以临时摘掉，但绝不能因为索引故障，就把一次本来正常的实时消息写入或搜索，变成一次无界的全量记录重建。

## FTS 损坏时的实时行为

如果某次 FTS 写入或搜索报出损坏类错误，`SessionDB` 会：

1. 记录持久化的 `fts_stale` 标记；
2. 在同一个事务里移除 FTS 同步触发器；
3. 重试权威写入，但不再写派生索引；并且
4. 改用 `LIKE` 回退，从权威行直接提供搜索。

出错的实时操作**绝不会**执行 `FTS5('rebuild')`。既有的恢复职责归属不变：之后某次 `SessionDB` 打开时，可以在跨进程准入锁与外部持有者守卫之下执行重建。如果那次受守卫的重建跑不起来，FTS 就保持摘除状态，权威写入照常可用，`hermes doctor` 会报告明确的修复命令。

## 文件本身损坏时的实时行为

如果一次实时写入报出裸的 `SQLITE_CORRUPT` / `SQLITE_NOTADB`（`database disk image is malformed`、`file is not a database`），且没有任何 FTS 来源，那损坏就在权威 B 树、schema 或 freelist 上。此时 `SessionDB` 会把该句柄隔离（quarantine，抛出 `StateDbCorruptError`）：

1. 出错的写入直接抛出这个类型化错误，不做任何重试；
2. 该句柄后续的写入立刻失败，完全不碰文件；
3. `close()` 之后该句柄永远不再重开连接；并且
4. `close()` 跳过它显式的 WAL checkpoint。

**停止写入就是保护本身。** 现场案例：有一个句柄在第一次结构性错误之后又持续写了约 50 分钟，关闭时在错误的页号下 checkpoint 了 15 个页（第 1 页被写入了 `messages_fts_trigram_data` 的叶子节点），把一个「损坏但仍可读」的文件变成了完全打不开的文件。跳过显式 checkpoint 是第二道防线；在 Python 3.12+ 上，隔离还会关掉 SQLite 自己的「最后连接关闭时 checkpoint」（`SQLITE_DBCONFIG_NO_CKPT_ON_CLOSE`），于是 `-wal` 伴生文件能在 `close()` 之后留下来供取证。Python 3.11 上没有这个开关，SQLite 关闭时仍可能 checkpoint 一次，所以在重启任何东西之前，先把 `state.db`、`state.db-wal` 和 `state.db-shm` 一起复制出来。

gateway 与 agent 的落盘路径把隔离句柄当作「文件已被换掉」来处理：待写会话记录改走 `sessions/<id>.jsonl` 和 gateway 的 `pending_messages/` 缓冲区，而不是重试队列；FTS 的一次性重建也绝不会在损坏文件上执行。隔离是**按进程**的——共享句柄对所有持有者都是中毒状态，直到进程在一个已修复或已还原的文件上重启为止。gateway 还在跑的时候不要执行 `hermes doctor --fix`。后续步骤：

```bash
hermes gateway stop
HERMES_HOME="$HOME/.hermes" hermes sessions recover --source "$HOME/.hermes/state.db" --inspect-only
# if recoverable:
HERMES_HOME="$HOME/.hermes" hermes sessions recover --source "$HOME/.hermes/state.db" --output "$HOME/recovered-state.db"
```

或者从 `state-snapshots/` 里还原最新的快照。

## 显式修复

修复之前，先停掉所有可能打开该 profile 数据库的进程，并在整个修复与验证窗口期间保持它们停着。

```bash
hermes gateway stop
HERMES_HOME="$HOME/.hermes" hermes sessions repair --check-only
HERMES_HOME="$HOME/.hermes" hermes sessions repair
```

`sessions repair` 默认会创建一份 SQLite 备份，并通过仓库里带守卫的「快照 + 提升」路径完成结构性操作。不要用 `cp` 分别拷贝 `state.db`、`state.db-wal` 和 `state.db-shm`——这三个文件是同一个活着的 SQLite 映像。

修复完成后、重启 gateway 之前，先验证健康探针、陈旧标记、触发器集合和权威行数：

```bash
HERMES_HOME="$HOME/.hermes" hermes sessions repair --check-only
sqlite3 "$HOME/.hermes/state.db" \
  "SELECT key, value FROM state_meta WHERE key = 'fts_stale';"
sqlite3 "$HOME/.hermes/state.db" \
  "SELECT type, name FROM sqlite_master WHERE name IN
   ('messages_fts_insert','messages_fts_update','messages_fts_delete')
   ORDER BY name;"
sqlite3 "$HOME/.hermes/state.db" \
  "SELECT 'sessions', COUNT(*) FROM sessions
   UNION ALL SELECT 'messages', COUNT(*) FROM messages;"
```

标记查询应当返回空行，预期的 FTS 触发器应当都在，权威行数不得减少。如果修复失败，把线上数据库和报告出来的备份都保留好；永远不要为了消掉一个派生索引报错而删除权威行。

参考文献从略，见原文。
