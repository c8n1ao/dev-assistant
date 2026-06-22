#!/usr/bin/env bash
# PreToolUse 提醒器 — 非阻断模式
#
# 当检测到应用开发相关话题，但会话尚未调用 hippocampus_search 时，
# 通过 systemMessage 提示用户切换到 development agent。
#
# 核心原则：
#   - 永不 DENY，所有工具始终放行
#   - 基于状态文件判断 hippocampus 是否已被调用
#   - 每个 session 最多提醒一次（防骚扰）
#
# 状态文件：/tmp/development-gate-{session_id}.json
#   {"phase": "pending", "reminded": false}

set -euo pipefail

STATE_DIR="/tmp/development-gate"

# ── 读取 stdin（hook 传入的 JSON）─────────────────
input=$(cat)
session_id=$(echo "$input" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('session_id',''))" 2>/dev/null || true)

if [ -z "$session_id" ]; then
    # 无 session_id，无法追踪状态，静默放行
    exit 0
fi

STATE_FILE="${STATE_DIR}/development-gate-${session_id}.json"

# ── 读取当前状态 ─────────────────────────────────
phase="pending"
reminded="false"
if [ -f "$STATE_FILE" ]; then
    phase=$(python3 -c "import json; d=json.load(open('$STATE_FILE')); print(d.get('phase','pending'))" 2>/dev/null || echo "pending")
    reminded=$(python3 -c "import json; d=json.load(open('$STATE_FILE')); print(str(d.get('reminded',False)).lower())" 2>/dev/null || echo "false")
fi

# ── 提取工具信息 ─────────────────────────────────
tool_name=$(echo "$input" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('tool_name',''))" 2>/dev/null || true)

# ── 状态更新：检测到 hippocampus_search 调用 ─────
if [ "$tool_name" = "hippocampus_search" ] || echo "$tool_name" | grep -q "hippocampus"; then
    mkdir -p "$STATE_DIR"
    python3 -c "
import json
state = {'phase': 'hippocampus_done', 'reminded': $reminded}
json.dump(state, open('$STATE_FILE', 'w'))
"
    # 放行，不提醒
    exit 0
fi

# ── 如果已经调过 hippocampus，放行 ─────────────
if [ "$phase" = "hippocampus_done" ]; then
    exit 0
fi

# ── 如果已经提醒过，不再重复 ───────────────────
if [ "$reminded" = "true" ]; then
    exit 0
fi

# ── 判断是否为应用开发相关工具调用 ─────────────
# 检测原则：任何非纯系统工具（如 memory、file_read 等）的调用，
# 在 hippocampus 未调用的情况下，注入提醒。
# 排除：hippocampus 系列（已在上面处理）、纯读取类（Skill 加载等）

irrelevant_tools="hippocampus|mcp_hippocampus|memory|Skill|read_file|list_dir|search"
if echo "$tool_name" | grep -qE "$irrelevant_tools"; then
    exit 0
fi

# ── 注入提醒 ────────────────────────────────────
mkdir -p "$STATE_DIR"
python3 -c "
import json
state = {'phase': '$phase', 'reminded': True}
json.dump(state, open('$STATE_FILE', 'w'))
"

# 输出 systemMessage 提醒（非阻断）
cat << 'EOF'
{"systemMessage": "💡 检测到应用开发相关操作，但尚未检索海马体历史偏好。\n\n建议切换到 **development agent** 以获得完整的决策支持（历史偏好 + References 参考文件）。\n\n在 VS Code 中：点击 chat 面板的 agent 选择器 → 选择「development」。"}
EOF
