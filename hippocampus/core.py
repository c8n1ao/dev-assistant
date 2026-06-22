"""
海马体记忆层 — SQLite 持久化
为 dev-assistant 插件提供跨会话偏好记忆能力。
存储: hippocampus/memory.db
"""

import json
import math
import sqlite3
from datetime import datetime
from pathlib import Path

# ── 配置 ──────────────────────────────────────────────
DB_PATH = Path(__file__).resolve().parent / "memory.db"

SCHEMA_VERSION = "0.6.0"


# ═══════════════════════════════════════════════════════
# 数据库核心
# ═══════════════════════════════════════════════════════

def get_db() -> sqlite3.Connection:
    """获取数据库连接，启用 WAL 模式"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """初始化数据库表结构（幂等）"""
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS meta (
            key   TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS entries (
            id              TEXT PRIMARY KEY,
            created_at      TEXT NOT NULL,
            platform        TEXT NOT NULL,
            dimension       TEXT NOT NULL,
            memory_type     TEXT NOT NULL DEFAULT 'user_preference'
                            CHECK(memory_type IN ('user_preference','maintenance_checklist','architecture_decision','known_issue','coding_principle')),
            content         TEXT NOT NULL,
            signal_level    TEXT NOT NULL CHECK(signal_level IN ('high','medium','weak')),
            weight          INTEGER NOT NULL DEFAULT 0,
            note            TEXT DEFAULT '',
            session_count   INTEGER NOT NULL DEFAULT 1,
            superseded_by   TEXT,
            superseded_at   TEXT
        );

        CREATE INDEX IF NOT EXISTS idx_entries_platform ON entries(platform);
        CREATE INDEX IF NOT EXISTS idx_entries_dimension ON entries(dimension);
        CREATE INDEX IF NOT EXISTS idx_entries_active
            ON entries(weight) WHERE weight > 0 AND superseded_by IS NULL;

        CREATE TABLE IF NOT EXISTS platform_weights (
            platform    TEXT NOT NULL,
            dimension   TEXT NOT NULL,
            value       TEXT NOT NULL,
            weight      INTEGER NOT NULL DEFAULT 0,
            count       INTEGER NOT NULL DEFAULT 0,
            last_seen   TEXT NOT NULL,
            PRIMARY KEY (platform, dimension)
        );

        -- 清理 v0.4.0 迁移可能遗留的临时表
        DROP TABLE IF EXISTS entries_new;
    """)

    conn.execute("CREATE INDEX IF NOT EXISTS idx_entries_memory_type ON entries(memory_type)")
    conn.execute(
        "INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?)",
        ("schema_version", SCHEMA_VERSION)
    )
    conn.commit()
    conn.close()


# ═══════════════════════════════════════════════════════
# 工具函数
# ═══════════════════════════════════════════════════════

def simple_score(query: str, text: str) -> float:
    """简单关键词匹配评分"""
    query_lower = query.lower()
    text_lower = text.lower()

    query_words = set(query_lower.split())
    text_words = set(text_lower.split())
    if query_words:
        intersection = query_words & text_words
        word_score = len(intersection) / math.sqrt(len(query_words) * max(len(text_words), 1))
    else:
        word_score = 0.0

    if word_score == 0.0 and query_lower.strip():
        if query_lower in text_lower:
            return 0.1
    return word_score


def row_to_dict(row: sqlite3.Row) -> dict:
    """将 sqlite3.Row 转为普通 dict"""
    if row is None:
        return {}
    return dict(row)


# ═══════════════════════════════════════════════════════
# MCP 工具实现（无装饰器 — 由 server/mcp_entry.py 注册）
# ═══════════════════════════════════════════════════════

def hippocampus_search(query: str, platform: str = "", memory_type: str = "", top_k: int = 5) -> str:
    """
    检索与当前请求相关的历史偏好记忆。

    Args:
        query: 检索查询，如「架构选型」「状态管理」
        platform: 平台过滤，如 ios / android / web / miniprogram / desktop（可选）
        memory_type: 记忆类型过滤（可选）
        top_k: 返回最多几条记忆
    """
    conn = get_db()
    try:
        where_parts = ["1=1"]
        params = []
        if platform:
            where_parts.append("platform IN ('', ?, 'global')")
            params.append(platform)
        if memory_type:
            where_parts.append("memory_type = ?")
            params.append(memory_type)

        where = " AND ".join(where_parts)
        rows = conn.execute(
            f"SELECT * FROM entries WHERE {where} ORDER BY weight DESC", params
        ).fetchall()

        has_filter = bool(memory_type or platform)
        scored = []
        for row in rows:
            d = row_to_dict(row)
            text = f"{d.get('dimension', '')} {d.get('content', '')} {d.get('note', '')}"
            score = simple_score(query, text)
            if has_filter:
                score = max(score, 0.01)
            if score > 0:
                scored.append((score, d))

        scored.sort(key=lambda x: (-x[0], -x[1].get("weight", 0)))
        results = [e for _, e in scored[:top_k]]

        platform_weights = {}
        if platform:
            pw_rows = conn.execute(
                "SELECT * FROM platform_weights WHERE platform = ?", (platform,)
            ).fetchall()
            platform_weights = {r["dimension"]: row_to_dict(r) for r in pw_rows}

        total = conn.execute("SELECT COUNT(*) as c FROM entries").fetchone()["c"]

        return json.dumps({
            "memories": results,
            "platform_weights_summary": platform_weights,
            "total_memories": total
        }, ensure_ascii=False, indent=2)
    finally:
        conn.close()


def _validate_content_structure(content: str) -> dict:
    """
    校验 content 是否包含必要的字段锚点（锚点+自由叙述格式）。
    只检测字段标签是否存在以及值是否为空，不解析语义内容。

    返回 {"blocks": [...], "warnings": [...]}，blocks 非空时必须拒绝写入。
    """
    blocks = []
    warnings = []

    # 支持中英文冒号两种写法
    def _extract_field(field_name: str) -> str | None:
        """提取字段锚点后的值（到下一个锚点或文本末尾），返回 None 表示锚点不存在。
        自动匹配中文冒号（：）和英文冒号（:）。"""
        for colon in (":", "："):
            label = field_name + colon
            if label in content:
                start = content.index(label) + len(label)
                # 截取到下一个字段锚点或文本末尾
                rest = content[start:]
                cut_markers = []
                for fn in ("排除", "选择", "情境", "失效条件"):
                    for c in (":", "："):
                        cut_markers.append(f"\n{fn}{c}")
                end = len(rest)
                for m in cut_markers:
                    pos = rest.find(m)
                    if pos != -1 and pos < end:
                        end = pos
                value = rest[:end].strip()
                return value
        return None

    # ── 失效条件（必填，缺失或为空 → block） ──
    expiry = _extract_field("失效条件")
    if expiry is None:
        blocks.append("缺少必填字段「失效条件」。记忆必须声明失效条件——即使暂不明确也应写「暂不明确，需在实际使用中观察后补充」")
    elif not expiry:
        blocks.append("「失效条件」字段不能为空。如暂不明确请写「暂不明确，需在实际使用中观察后补充」")

    # ── 排除（推荐，缺失 → warning；存在但过短 → warning） ──
    exclusion = _extract_field("排除")
    if exclusion is None:
        warnings.append("建议包含「排除」字段，记录被排除的替代方案及原因")
    elif len(exclusion) < 10:
        warnings.append("「排除」字段内容过短（< 10 字），建议补充排除原因，而非仅列举排除项名称")

    # ── 选择（推荐，缺失 → warning） ──
    choice = _extract_field("选择")
    if choice is None:
        warnings.append("建议包含「选择」字段，记录最终决策")
    elif len(choice) < 3:
        warnings.append("「选择」字段内容过短，建议补充具体方案描述")

    # ── 情境（推荐，不强制） ──
    situation = _extract_field("情境")
    if situation is None:
        warnings.append("建议包含「情境」字段（如团队规模、时间约束、技术栈上下文），帮助未来判断偏好是否仍然适用")

    return {"blocks": blocks, "warnings": warnings}


def hippocampus_add(
    content: str, platform: str, dimension: str, signal_level: str,
    note: str = "", memory_type: str = "user_preference"
) -> str:
    """
    向海马体写入新的记忆条目。

    content 格式要求（锚点+自由叙述）：
        排除: <被排除方案及原因，自由叙述>
        选择: <最终决策>
        情境: <决策背景：团队/时间/技术栈等>
        失效条件: <什么可观测事件会使该偏好失效>

    Args:
        content: 记忆内容（含字段锚点）
        platform: 平台标识
        dimension: 记忆维度
        signal_level: 信号强度 high / medium / weak
        note: 附加上下文
        memory_type: 记忆类型
    """
    if signal_level == "weak":
        return json.dumps({"status": "skipped", "reason": "弱信号不写入，防止噪音污染记忆"})

    allowed_types = ("user_preference", "maintenance_checklist", "architecture_decision", "known_issue", "coding_principle")
    if memory_type not in allowed_types:
        return json.dumps({"status": "error", "reason": f"无效的 memory_type，允许值：{allowed_types}"})

    # ── 内容结构校验 ──
    validation = _validate_content_structure(content)
    if validation["blocks"]:
        return json.dumps({
            "status": "blocked",
            "reason": "内容结构不完整，必须修复后才能写入",
            "blocks": validation["blocks"],
            "warnings": validation["warnings"],
            "help": "content 格式：\n"
                    "排除: <被排除方案及原因>\n"
                    "选择: <最终决策>\n"
                    "情境: <决策背景>\n"
                    "失效条件: <可观测的失效事件或「暂不明确，需在实际使用中观察后补充」>"
        }, ensure_ascii=False)

    weight_map = {"high": 2, "medium": 1}
    weight = weight_map.get(signal_level, 0)
    now = datetime.now()
    entry_id = f"{platform}_{dimension}_{now.strftime('%Y%m%d%H%M%S')}"

    conn = get_db()
    try:
        conflict_found = False
        old_entries = conn.execute(
            "SELECT id, content, weight FROM entries WHERE platform = ? AND dimension = ?",
            (platform, dimension)
        ).fetchall()
        for old in old_entries:
            if old["content"] != content:
                new_weight = max(0, old["weight"] - 1)
                conn.execute(
                    "UPDATE entries SET weight = ?, superseded_by = ?, superseded_at = ? WHERE id = ?",
                    (new_weight, content, now.isoformat(), old["id"])
                )
                conflict_found = True

        conn.execute(
            """INSERT INTO entries
               (id, created_at, platform, dimension, memory_type, content, signal_level,
                weight, note, session_count)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (entry_id, now.isoformat(), platform, dimension, memory_type, content,
             signal_level, weight, note, 1)
        )

        # 从 entries 重算 platform_weights（与 forget 一致，避免累加偏差）
        remaining = conn.execute(
            "SELECT content, weight FROM entries WHERE platform = ? AND dimension = ? AND weight > 0 AND superseded_by IS NULL",
            (platform, dimension)
        ).fetchall()
        if not remaining:
            conn.execute(
                "DELETE FROM platform_weights WHERE platform = ? AND dimension = ?",
                (platform, dimension)
            )
        else:
            total_weight = sum(r["weight"] for r in remaining)
            total_count = len(remaining)
            best = max(remaining, key=lambda r: r["weight"])
            conn.execute(
                """INSERT OR REPLACE INTO platform_weights (platform, dimension, value, weight, count, last_seen)
                   VALUES (?,?,?,?,?,?)""",
                (platform, dimension, best["content"], total_weight, total_count, now.isoformat())
            )

        conn.execute(
            "UPDATE meta SET value = CAST(CAST(value AS INTEGER) + 1 AS TEXT) WHERE key = 'total_sessions'"
        )
        conn.commit()

        result = {
            "status": "success", "entry_id": entry_id, "conflict_resolved": conflict_found,
            "message": f"{'⚠️ 检测到与旧记忆冲突，旧记忆已降权。' if conflict_found else ''}记忆已写入。"
        }
        if validation["warnings"]:
            result["warnings"] = validation["warnings"]
        return json.dumps(result, ensure_ascii=False)
    finally:
        conn.close()


def hippocampus_get_weights(platform: str, dimension: str = "") -> str:
    """获取指定平台的偏好权重摘要"""
    conn = get_db()
    try:
        if dimension:
            rows = conn.execute(
                "SELECT * FROM platform_weights WHERE platform = ? AND dimension = ?",
                (platform, dimension)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM platform_weights WHERE platform = ?", (platform,)
            ).fetchall()

        formatted = {}
        for r in rows:
            d = row_to_dict(r)
            if d.get("count", 0) > 0:
                formatted[d["dimension"]] = f"历史选择 {d['count']} 次（权重 {d['weight']}）：{d['value']}"
            else:
                formatted[d["dimension"]] = "无历史"

        if dimension and not formatted:
            formatted[dimension] = "无历史"

        return json.dumps(formatted, ensure_ascii=False, indent=2)
    finally:
        conn.close()


def hippocampus_forget(entry_id: str) -> str:
    """删除指定记忆条目，并同步更新 platform_weights 聚合"""
    conn = get_db()
    try:
        # 1. 查询要删除的条目（获取 platform + dimension 用于后续聚合修正）
        entry = conn.execute("SELECT platform, dimension, weight FROM entries WHERE id = ?", (entry_id,)).fetchone()
        if not entry:
            return json.dumps({"status": "not_found", "message": f"未找到条目 {entry_id}"})

        platform = entry["platform"]
        dimension = entry["dimension"]

        # 2. 删除条目
        conn.execute("DELETE FROM entries WHERE id = ?", (entry_id,))

        # 3. 重算 platform_weights：查询该 (platform, dimension) 下的剩余条目
        remaining = conn.execute(
            "SELECT content, weight FROM entries WHERE platform = ? AND dimension = ? AND weight > 0 AND superseded_by IS NULL",
            (platform, dimension)
        ).fetchall()

        if not remaining:
            # 无剩余活跃条目 → 删除聚合行
            conn.execute(
                "DELETE FROM platform_weights WHERE platform = ? AND dimension = ?",
                (platform, dimension)
            )
        else:
            # 重新计算聚合
            total_weight = sum(r["weight"] for r in remaining)
            total_count = len(remaining)
            # value 取最高权重条目的内容
            best = max(remaining, key=lambda r: r["weight"])
            from datetime import datetime
            conn.execute(
                """UPDATE platform_weights
                   SET value = ?, weight = ?, count = ?, last_seen = ?
                   WHERE platform = ? AND dimension = ?""",
                (best["content"], total_weight, total_count, datetime.now().isoformat(), platform, dimension)
            )

        conn.commit()
        return json.dumps({"status": "success", "message": f"条目 {entry_id} 已删除，聚合表已同步更新"})
    finally:
        conn.close()


def hippocampus_reset(confirm: str) -> str:
    """清空所有记忆（需二次确认）"""
    if confirm != "CONFIRM_RESET":
        return json.dumps({"status": "aborted", "message": "需要传入 'CONFIRM_RESET' 确认才会清空记忆"})

    conn = get_db()
    try:
        conn.execute("DELETE FROM entries")
        conn.execute("DELETE FROM platform_weights")
        conn.execute("INSERT OR REPLACE INTO meta (key, value) VALUES ('total_sessions', '0')")
        conn.commit()
        return json.dumps({"status": "success", "message": "海马体已清空，所有记忆已删除"})
    finally:
        conn.close()


def register_hippocampus_tools(mcp):
    """向 FastMCP 实例注册所有海马体工具"""
    init_db()
    mcp.tool(name="dev-assistant-mcp_hippocampus_search")(hippocampus_search)
    mcp.tool(name="dev-assistant-mcp_hippocampus_add")(hippocampus_add)
    mcp.tool(name="dev-assistant-mcp_hippocampus_get_weights")(hippocampus_get_weights)
    mcp.tool(name="dev-assistant-mcp_hippocampus_forget")(hippocampus_forget)
    mcp.tool(name="dev-assistant-mcp_hippocampus_reset")(hippocampus_reset)
