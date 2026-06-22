#!/usr/bin/env bash
# SessionStart hook for Development Assistant
# 1. 读取海马体记忆 (SQLite)，注入用户历史偏好
# 2. 读取 References 索引，注入可用技能清单
# 两者独立：即使无记忆，也会注入索引

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# 在 heredoc 之前捕获 hook stdin（hook 系统通过管道传入 JSON）
HOOK_INPUT=$(cat)
export HOOK_INPUT
export PROJECT_DIR

python3 << 'PYEOF'
import json, os, sys, sqlite3

PROJECT = os.environ["PROJECT_DIR"]

# ── 第一部分：海马体偏好 ──────────────────────────
memory_section = ""
db_path = os.path.join(PROJECT, "hippocampus", "memory.db")

try:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT platform, dimension, memory_type, content, weight, note FROM entries "
        "WHERE weight > 0 AND superseded_by IS NULL ORDER BY weight DESC"
    ).fetchall()
    conn.close()

    if rows:
        # 按 memory_type 分组
        user_prefs = [r for r in rows if r["memory_type"] == "user_preference"]
        maintenance = [r for r in rows if r["memory_type"] == "maintenance_checklist"]
        arch_decisions = [r for r in rows if r["memory_type"] == "architecture_decision"]
        known_issues = [r for r in rows if r["memory_type"] == "known_issue"]

        lines = ["【🧠 海马体 · 历史偏好记忆】"]

        # 用户偏好（主要关注）
        if user_prefs:
            lines.append("以下是从历史会话中提炼的用户技术偏好：")
            by_platform = {}
            for row in user_prefs:
                platform = row["platform"]
                by_platform.setdefault(platform, []).append(row)

            for platform in sorted(by_platform.keys()):
                platform_label = {
                    'ios': 'iOS', 'android': 'Android', 'web': 'Web',
                    'miniprogram': '小程序', 'desktop': '桌面', 'cross_platform': '跨平台',
                    'global': '通用'
                }.get(platform, platform)
                lines.append(f"\n### {platform_label}")
                for r in by_platform[platform]:
                    dim = r["dimension"]
                    content = r["content"]
                    weight = r["weight"]
                    note = r["note"] or ""
                    note_str = f"（{note}）" if note else ''
                    lines.append(f"- [{dim}] {content}{note_str}  权重={weight}")

        # 维护清单（框架内部问题相关时关注）
        if maintenance:
            lines.append("\n\n### 🔧 框架维护清单")
            for r in maintenance:
                lines.append(f"- [maintenance] {r['content']}  (note: {r.get('note', '')})")

        # 架构决策记录（框架内部问题相关时关注）
        if arch_decisions:
            lines.append("\n\n### 📐 架构决策记录 (ADR)")
            for r in arch_decisions:
                lines.append(f"- [adr] {r['content']}  (note: {r.get('note', '')})")

        # 已知问题
        if known_issues:
            lines.append("\n\n### ⚠️ 已知问题")
            for r in known_issues:
                lines.append(f"- [known_issue] {r['content']}  (note: {r.get('note', '')})")

        memory_section = '\n'.join(lines)
except Exception:
    pass  # 无记忆或读取失败，静默跳过

# ── 第二部分：References 索引 ─────────────────────
index_section = ""
index_file = os.path.join(PROJECT, "references", "INDEX.md")

try:
    with open(index_file, 'r', encoding='utf-8') as f:
        index_content = f.read()
    if index_content.strip():
        index_section = "\n\n【📚 References · 可用参考技能】\n"
        index_section += "以下列出了各平台的参考文档清单。当你需要进行技术决策、代码实现或设计还原时，\n"
        index_section += "请先查阅此清单确认有哪些领域参考可用，再根据需要读取对应文件全文。\n\n"
        index_section += index_content
except Exception:
    pass  # 无索引或读取失败，静默跳过

# ── 2.5：References 检索路径提示 ──────────
knowledge_search_section = ""

# ── 第三部分：初始化 PreToolUse 状态文件 ────────
gate_init = ""
try:
    input_data = json.loads(os.environ.get("HOOK_INPUT", "{}"))
    session_id = input_data.get("session_id", "")
except Exception:
    session_id = ""

if session_id:
    state_dir = "/tmp/development-gate"
    try:
        os.makedirs(state_dir, exist_ok=True)
        state_file = os.path.join(state_dir, f"development-gate-{session_id}.json")
        with open(state_file, 'w') as f:
            json.dump({"phase": "pending", "reminded": False}, f)
    except Exception:
        pass  # 静默处理（非关键路径）

# ── 第四部分：同步 agent.md body 到插件内派生文件 ─────
# 仅同步插件内部文件，不涉及外部 VS Code / Cursor 等编辑器路径。
# 如需编辑器同步，请使用 hooks/sync-derived-files.sh 手动执行。
try:
    import os as _os

    plugin_src = os.path.join(PROJECT, "agents", "development.agent.md")
    if not _os.path.isfile(plugin_src):
        plugin_src = None

    if plugin_src:
        with open(plugin_src, 'r') as f:
            plugin_raw = f.read()
        plugin_parts = plugin_raw.split('---', 2)
        plugin_body = plugin_parts[2] if len(plugin_parts) > 2 else plugin_raw

        # 插件内部派生文件
        internal_targets = [
            os.path.join(PROJECT, "rules", "development.instructions.md"),
            os.path.join(PROJECT, "rules", "development.md"),
            os.path.join(PROJECT, "skills", "development", "SKILL.md"),
        ]
        for target in internal_targets:
            if not _os.path.isfile(target):
                continue
            with open(target, 'r') as f:
                raw = f.read()
            parts = raw.split('---', 2)
            fm = parts[1] if len(parts) > 1 else ''
            new_content = f'---{fm}---{plugin_body}'
            if new_content.strip() != raw.strip():
                with open(target, 'w') as f:
                    f.write(new_content)

        # study agent
        study_src = os.path.join(PROJECT, "agents", "development.study.agent.md")
        if _os.path.isfile(study_src):
            with open(study_src, 'r') as f:
                study_raw = f.read()
            study_parts = study_raw.split('---', 2)
            study_body = study_parts[2] if len(study_parts) > 2 else study_raw
            study_targets = [
                os.path.join(PROJECT, "rules", "development.study.md"),
                os.path.join(PROJECT, "skills", "development-study", "SKILL.md"),
            ]
            for target in study_targets:
                if not _os.path.isfile(target):
                    continue
                with open(target, 'r') as f:
                    raw = f.read()
                parts = raw.split('---', 2)
                fm = parts[1] if len(parts) > 1 else ''
                new_content = f'---{fm}---{study_body}'
                if new_content.strip() != raw.strip():
                    with open(target, 'w') as f:
                        f.write(new_content)
except Exception:
    pass  # 同步失败不影响主流程

# ── 组装输出 ─────────────────────────────────────
message = (memory_section + index_section + knowledge_search_section).strip()
if message:
    print(json.dumps({"systemMessage": message}))
PYEOF
