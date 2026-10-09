# 海马体 (Hippocampus) 数据库结构说明

> Schema v0.3.0 | 存储引擎：SQLite 3 (WAL 模式) | 2026-06-08

## 一、概述

海马体是 development-assistant 的跨会话记忆层，持久化用户的技术偏好与决策历史。
迁移自原 JSON 文件方案 (`memory.json`)，改用 SQLite 以获得原子写入、结构化查询和全文搜索能力。

**数据库文件**：`~/.copilot/installed-plugins/development-assistant/hippocampus/memory.db`
**核心代码**：`hippocampus/core.py`
**MCP 入口**：`server/mcp_entry.py`

---

## 二、表结构

### 2.1 `entries` — 记忆条目主表

存储每一笔记忆记录，是海马体的核心表。

```sql
CREATE TABLE entries (
    id              TEXT PRIMARY KEY,       -- 唯一标识
    created_at      TEXT NOT NULL,          -- 创建时间 (ISO 8601)
    platform        TEXT NOT NULL,          -- 平台分类
    dimension       TEXT NOT NULL,          -- 记忆维度
    memory_type     TEXT NOT NULL DEFAULT 'user_preference'  -- 记忆类型（v0.3.0 新增）
                        CHECK(memory_type IN ('user_preference','coding_principle','maintenance_checklist','architecture_decision','known_issue')),
    content         TEXT NOT NULL,          -- 记忆内容正文
    signal_level    TEXT NOT NULL           -- 信号强度
                        CHECK(signal_level IN ('high','medium','weak')),
    weight          INTEGER NOT NULL DEFAULT 0,  -- 权重分值
    note            TEXT DEFAULT '',        -- 附注说明
    session_count   INTEGER NOT NULL DEFAULT 1,  -- 关联会话数
    superseded_by   TEXT,                   -- 被哪个新内容取代
    superseded_at   TEXT                    -- 取代时间 (ISO 8601)
);

CREATE INDEX idx_entries_platform ON entries(platform);
CREATE INDEX idx_entries_dimension ON entries(dimension);
CREATE INDEX idx_entries_memory_type ON entries(memory_type);
CREATE INDEX idx_entries_active ON entries(weight)
    WHERE weight > 0 AND superseded_by IS NULL;
```

#### 字段说明

| 字段            | 类型    | 业务含义                                                                                                                                                                                                                                                                                                                    |
| --------------- | ------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `id`            | TEXT PK | 全局唯一标识，格式：`{platform}_{dimension}_{YYYYMMDDHHmmss}`。如 `ios_architecture_20260519103131`。通过解析 ID 可快速获知记录的归属平台、维度和时间。                                                                                                                                                                     |
| `created_at`    | TEXT    | IS0 8601 格式时间戳，记录该条记忆首次写入的精确时刻。用于排序、审计和时效性判断（如淘汰陈旧记忆）。                                                                                                                                                                                                                         |
| `platform`      | TEXT    | 该记忆适用的平台/领域。取值范围：`ios` / `android` / `web` / `miniprogram` / `desktop` / `cross_platform` / `global` / `general`。其中 `global` 表示跨平台通用偏好（工具链、插件开发等），`general` 表示通用 CS 知识（算法、理论等）。查询时平台过滤依靠此字段。                                                                                                                                        |
| `dimension`     | TEXT    | 记忆所属的技术维度，用于同类偏好的冲突检测和分组聚合。典型值：`architecture`（架构）、`ui_framework`（UI框架）、`state_management`（状态管理）、`testing`（测试）、`code_conventions`（编码规范）、`memory_selection_criteria`（记忆筛选标准）、`plugin_architecture`（插件架构）、`learning_methodology`（学习方法论）等。 |
| `memory_type`   | TEXT    | **v0.3.0 新增**。记忆的类型分类，区分用户偏好与框架维护信息。取值见下方「记忆类型分类」章节。                                                                                                                                                                                                                               |
| `content`       | TEXT    | 记忆的正文内容。包含用户明确表达的技术偏好、踩坑经验、架构决策等。这是 AI 召回记忆时的核心文本。高密度写法：实战背景 + 决策公式/结论 + 结果。                                                                                                                                                                               |
| `signal_level`  | TEXT    | 信号的确认强度，分三档：`high`——用户显式修正或明确采纳后深入实现；`medium`——用户在比较后采纳某方案；`weak`——不写入（由 MCP 层过滤）。信号强度直接决定初始权重。                                                                                                                                                             |
| `weight`        | INTEGER | 该记忆的累积权重，越大代表被越多次确认或越重要。初始值由 `signal_level` 决定（high=2, medium=1）。当有冲突的同维度新记忆写入时，旧记忆权重减 1（降权机制）。AI 检索时按 weight 降序返回。权重为 0 的条目仍保留在库中但不会出现在活跃结果中。                                                                                |
| `note`          | TEXT    | 附加上下文或备注。记录该记忆的产生背景、来源文档、约束条件等。可选字段，用于帮助 AI 理解记忆的适用范围。                                                                                                                                                                                                                    |
| `session_count` | INTEGER | 该记忆被引用/确认的会话次数，当前版本固定为 1（未实现增量更新）。                                                                                                                                                                                                                                                           |
| `superseded_by` | TEXT    | 替代本记忆的新内容（存储新记忆的 content 值或新记忆的 id）。非 NULL 表示此记忆已被更新的同维度偏好所取代。被取代的条目在活跃查询中被过滤掉（`WHERE superseded_by IS NULL`），但保留在库中作为历史记录。                                                                                                                     |
| `superseded_at` | TEXT    | 被取代的时间戳（ISO 8601）。配合 `superseded_by` 使用，记录取代发生的精确时刻。                                                                                                                                                                                                                                             |

### 记忆类型分类（v0.3.0 新增）

`memory_type` 字段区分五类不同性质的记忆：

| 类型                    | 用途                                     | 启动注入行为               | 检索建议                  |
| ----------------------- | ---------------------------------------- | -------------------------- | ------------------------- |
| `user_preference`       | 用户技术偏好（默认值，向后兼容）         | 始终注入（按平台分组展示） | `hippocampus_search` 默认 |
| `coding_principle`      | 编码原则与最佳实践                       | 始终注入（按平台分组展示） | `hippocampus_search` 默认 |
| `maintenance_checklist` | 框架维护清单（如"两套 Hook 需同步维护"） | 仅在涉及框架内部问题时注入 | 按 `memory_type` 精确过滤 |
| `architecture_decision` | 框架自身的架构决策记录（ADR）            | 仅在涉及框架内部问题时注入 | 按 `memory_type` 精确过滤 |
| `known_issue`           | 已知问题 / 限制 / 临时规避方案           | 仅在涉及框架内部问题时注入 | 按 `memory_type` 精确过滤 |

> **设计原则**：`user_preference` 和 `coding_principle` 是高频优先信息，始终注入避免遗漏。后三类是低频维护信息，仅在框架内部话题时关注，避免日常对话被维护噪音污染。

---

### 2.2 `platform_weights` — 平台偏好权重表

聚合每个平台×维度组合的偏好摘要，用于决策表中的"历史参考"列。

```sql
CREATE TABLE platform_weights (
    platform    TEXT NOT NULL,
    dimension   TEXT NOT NULL,
    value       TEXT NOT NULL,         -- 最高权重条目的内容
    weight      INTEGER NOT NULL DEFAULT 0,  -- 累积权重
    count       INTEGER NOT NULL DEFAULT 0,  -- 写入次数
    last_seen   TEXT NOT NULL,         -- 最近一次更新时间

    PRIMARY KEY (platform, dimension)
);
```

#### 字段说明

| 字段        | 类型    | 业务含义                                                                                                                                     |
| ----------- | ------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| `platform`  | TEXT    | 平台标识，与 `entries.platform` 对应。                                                                                                       |
| `dimension` | TEXT    | 技术维度，与 `entries.dimension` 对应。`(platform, dimension)` 联合主键确保每个平台×维度只有一条聚合记录。                                   |
| `value`     | TEXT    | 该维度下最高权重条目的内容。这是调用 `hippocampus_get_weights` 时返回给 AI 的"当前偏好"，用于填写决策表中的"历史参考"列。                    |
| `weight`    | INTEGER | 该维度的累积权重，等于历史上所有同维度写入的权重之和。当同一维度被多次写入时（如先后确认 iOS 架构为 MVVM），权重会叠加，反映该偏好的稳定性。 |
| `count`     | INTEGER | 该维度的写入次数。count=1 表示一次性偏好，count≥3 表示经过多次确认的稳定偏好。用于评估偏好的可靠性。                                         |
| `last_seen` | TEXT    | 最近一次写入的时间。用于判断偏好的时效性——一个一年前记录的偏好可能已过时。                                                                   |

---

### 2.3 `meta` — 系统元信息表

K-V 键值对存储，替代原 JSON 的 `_meta` 和 `global` 段。

```sql
CREATE TABLE meta (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
```

#### 预定义键值

| key                              | 示例 value | 业务含义                                                                                     |
| -------------------------------- | ---------- | -------------------------------------------------------------------------------------------- |
| `schema_version`                 | `"0.3.0"`  | 数据库 schema 版本号，用于未来迁移判断。与 `entries`/`platform_weights` 的字段变更同步更新。 |
| `total_sessions`                 | `"17"`     | 累计会话计数（跨所有会话的写入总次数）。每次调用 `hippocampus_add` 时自增 1。                |
| `global_platform_priority`       | `[]`       | 平台优先级列表（JSON 数组）。历史偏好中用户对各平台的重视程度排序。当前版本未启用。          |
| `global_third_party_tolerance`   | `"null"`   | 第三方库容忍度（`"low"` / `"medium"` / `"high"` / `null`）。当前版本未启用。                 |
| `global_testing_culture`         | `"null"`   | 测试文化偏好。当前版本未启用。                                                               |
| `global_performance_sensitivity` | `"null"`   | 性能敏感度。当前版本未启用。                                                                 |

---

## 三、索引策略

| 索引名                  | 作用               | 覆盖场景                                                   |
| ----------------------- | ------------------ | ---------------------------------------------------------- |
| `idx_entries_platform`  | 按平台快速过滤     | `hippocampus_search` 的 platform 参数                      |
| `idx_entries_dimension` | 按维度筛选         | 冲突检测：查找同 platform+dimension 的旧条目               |
| `idx_entries_active`    | 活跃条目的部分索引 | SessionStart hook 注入偏好时只查 weight>0 且未被取代的条目 |

> 当前数据量（< 100 条）下索引开销可忽略，但为未来扩展预留。

---

## 四、核心业务逻辑

### 4.1 写入流程 (`hippocampus_add`)

```
1. signal_level == "weak" → 拒绝写入（防止噪音）
2. 查询同 platform + dimension 的旧条目
3. 如果存在且 content 不同 → 旧条目 weight-1, 标记 superseded_by/at
4. 插入新条目 (weight = high→2, medium→1)
5. UPSERT platform_weights (weight 累加, count+1)
6. meta.total_sessions += 1
```

### 4.2 检索流程 (`hippocampus_search`)

```
1. 如果指定 platform → 过滤 WHERE platform IN ('', ?, 'global')
2. 全量查询 entries (按 weight DESC)
3. Python 侧对 content+dimension+note 做关键词匹配评分 (simple_score)
4. 按评分降序取 top_k
5. 同步返回 platform_weights 摘要
```

### 4.3 冲突检测

同 platform + dimension 的新旧内容冲突时：

- 新内容立即写入（权重 = signal_weight）
- 旧内容权重 -1（最低降至 0）
- 旧内容记录 `superseded_by`（指向新 content）和时间戳
- 这些被取代条目不出现在活跃查询中，但保留在库中可追溯

### 4.4 活跃条目的定义

满足 `weight > 0 AND superseded_by IS NULL` 的条目视为"活跃"。

- SessionStart hook 只注入活跃条目
- `hipp.py` 显示总条目和活跃条目分别计数
- 权重降为 0 或被取代的条目不再注入 AI 上下文中，节省 token

---

## 五、MCP 工具映射

| MCP Tool                  | 主要操作的表                      | SQL 操作类型             |
| ------------------------- | --------------------------------- | ------------------------ |
| `hippocampus_search`      | entries + platform_weights        | SELECT (带评分)          |
| `hippocampus_add`         | entries + platform_weights + meta | INSERT + UPDATE + UPSERT |
| `hippocampus_get_weights` | platform_weights                  | SELECT                   |
| `hippocampus_forget`      | entries                           | DELETE                   |
| `hippocampus_reset`       | entries + platform_weights + meta | DELETE (清空)            |

---

## 六、版本历史

| 版本  | 日期       | 变更                                                  |
| ----- | ---------- | ----------------------------------------------------- |
| 0.1.0 | 2026-05-19 | 初始 JSON 文件方案 (`memory.json`)                    |
| 0.2.0 | 2026-06-08 | 迁移到 SQLite (`memory.db`)：3 表 + 3 索引 + WAL 模式 |

---

## 七、维护指南

### 查询常用 SQL

```sql
-- 查看平台记忆分布
SELECT platform, COUNT(*) FROM entries GROUP BY platform;

-- 查看所有活跃条目
SELECT platform, dimension, weight, substr(content,1,60)
FROM entries
WHERE weight > 0 AND superseded_by IS NULL
ORDER BY weight DESC;

-- 查看已被取代的条目（历史审计）
SELECT id, platform, dimension, substr(content,1,60), superseded_by
FROM entries WHERE superseded_by IS NOT NULL;

-- 查看各维度偏好稳定性
SELECT platform, dimension, count, weight
FROM platform_weights
ORDER BY count DESC;
```

### 备份

```bash
# SQLite 安全备份（在线）
sqlite3 ~/.copilot/installed-plugins/development-assistant/hippocampus/memory.db ".backup ~/Desktop/memory-backup.db"

# 或直接复制文件（WAL 模式下需同时复制 -wal 和 -shm）
cp ~/.copilot/installed-plugins/development-assistant/hippocampus/memory.db ~/Desktop/
```

### 迁移到未来版本

1. 记录当前 `meta.schema_version`
2. 执行 `ALTER TABLE` / 新表 DDL
3. 更新 `meta.schema_version`
4. 更新 `db_migration.py`
