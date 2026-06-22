#!/usr/bin/env bash
# ============================================================
# sync-derived-files.sh
# 手动同步脚本：将 agents/development.agent.md（唯一真相源）的
# body 同步到所有派生文件，保留各文件的 frontmatter。
#
# 用法：
#   ./sync-derived-files.sh              # 同步内部派生文件
#   ./sync-derived-files.sh --dry-run    # 仅显示差异，不写入
#   ./sync-derived-files.sh --all        # 同步所有目标（含外部编辑器）
#
# 插件内部派生文件：
#   1. rules/development.instructions.md (Copilot)
#   2. rules/development.md (Claude Code / Cursor)
#   3. skills/development/SKILL.md (Agent Skills spec)
#
# Study agent 派生文件:
#   4. rules/development.study.md (Claude Code / Cursor)
#   5. skills/development-study/SKILL.md (Agent Skills spec)
#
# 外部编辑器目标（需 --all 启用，文件不存在时静默跳过）:
#   6. VS Code prompts/development.agent.md
#   7. VS Code prompts/development.instructions.md
#   8. VS Code prompts/development-study.agent.md
# ============================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

DRY_RUN=false
SYNC_ALL=false
for arg in "${@}"; do
    case "$arg" in
        --dry-run) DRY_RUN=true ;;
        --all) SYNC_ALL=true ;;
    esac
done

if $DRY_RUN; then
    echo "🔍 DRY RUN 模式 — 仅显示差异，不写入文件"
    echo ""
fi

python3 - "$DRY_RUN" "$SYNC_ALL" "$PROJECT_DIR" << 'PYEOF'
import os, sys

dry_run = sys.argv[1] == "true"
sync_all = sys.argv[2] == "true"
PLUGIN = sys.argv[3]

def sync_source(src_rel, targets):
    """同步单个 agent 的 body 到所有派生文件。"""
    src_path = os.path.join(PLUGIN, src_rel)
    if not os.path.isfile(src_path):
        print(f"  ⚠️  源文件不存在: {src_path}", file=sys.stderr)
        return 0, 0, 0

    with open(src_path, 'r') as f:
        src_raw = f.read()
    src_parts = src_raw.split('---', 2)
    src_body = src_parts[2] if len(src_parts) > 2 else src_raw

    changed = 0
    skipped = 0
    errors = 0

    for t in targets:
        path = os.path.expanduser(t["path"]) if t["path"].startswith("~") else t["path"]
        label = t["label"]

        if not os.path.isfile(path):
            print(f"  ⚠️  跳过（不存在）: {label}")
            skipped += 1
            continue

        try:
            with open(path, 'r') as f:
                derived_raw = f.read()
            derived_parts = derived_raw.split('---', 2)
            derived_fm = derived_parts[1] if len(derived_parts) > 1 else ''
            new_content = f'---{derived_fm}---{src_body}'

            if new_content.strip() == derived_raw.strip():
                print(f"  ✅ 已同步: {label}")
                continue

            if dry_run:
                old_lines = derived_raw.strip().split('\n')
                new_lines = new_content.strip().split('\n')
                diff = len(new_lines) - len(old_lines)
                sign = '+' if diff > 0 else ''
                print(f"  🔍 将更新: {label} (行数变化: {sign}{diff})")
                changed += 1
            else:
                with open(path, 'w') as f:
                    f.write(new_content)
                print(f"  ✍️  已写入: {label}")
                changed += 1

        except Exception as e:
            print(f"  ❌ 错误: {label} — {e}", file=sys.stderr)
            errors += 1

    return changed, skipped, errors

# ── development agent 目标 ────────────────────────
dev_targets = [
    {
        "path": os.path.join(PLUGIN, "rules/development.instructions.md"),
        "label": "plugin rules/development.instructions.md (Copilot)",
    },
    {
        "path": os.path.join(PLUGIN, "rules/development.md"),
        "label": "plugin rules/development.md (Claude Code / Cursor)",
    },
    {
        "path": os.path.join(PLUGIN, "skills/development/SKILL.md"),
        "label": "plugin skills/development/SKILL.md (Agent Skills spec)",
    },
]

# 外部编辑器目标（仅 --all 时启用）
if sync_all:
    dev_targets.extend([
        {
            "path": os.path.expanduser("~/Library/Application Support/Code/User/prompts/development.agent.md"),
            "label": "VS Code prompts/development.agent.md (agent mode)",
        },
        {
            "path": os.path.expanduser("~/Library/Application Support/Code/User/prompts/development.instructions.md"),
            "label": "VS Code prompts/development.instructions.md (instructions)",
        },
    ])

# ── study agent 目标 ──────────────────────────────
study_targets = [
    {
        "path": os.path.join(PLUGIN, "rules/development.study.md"),
        "label": "plugin rules/development.study.md (Claude Code / Cursor)",
    },
    {
        "path": os.path.join(PLUGIN, "skills/development-study/SKILL.md"),
        "label": "plugin skills/development-study/SKILL.md (Agent Skills spec)",
    },
]

if sync_all:
    study_targets.append({
        "path": os.path.expanduser("~/Library/Application Support/Code/User/prompts/development-study.agent.md"),
        "label": "VS Code prompts/development-study.agent.md (agent mode)",
    })

total_changed = 0
total_skipped = 0
total_errors = 0

for src, targets, name in [
    ("agents/development.agent.md", dev_targets, "development"),
    ("agents/development.study.agent.md", study_targets, "study"),
]:
    print(f"\n── {name} agent ──")
    ch, sk, er = sync_source(src, targets)
    total_changed += ch
    total_skipped += sk
    total_errors += er

print()
if dry_run:
    print(f"DRY RUN 完成 — {total_changed} 个文件需要更新, {total_skipped} 跳过, {total_errors} 错误")
else:
    print(f"同步完成 — {total_changed} 个文件已更新, {total_skipped} 跳过, {total_errors} 错误")

if total_errors > 0:
    sys.exit(1)
PYEOF
