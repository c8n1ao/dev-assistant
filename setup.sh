#!/usr/bin/env bash
# ============================================================
# Development Assistant — 一键初始化脚本
#
# 用法:
#   chmod +x setup.sh && ./setup.sh
#
# 完成后即可使用:
#   claude mcp add dev-assistant -- bash $(pwd)/server/run.sh
# ============================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_DIR="$SCRIPT_DIR"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m'

echo ""
echo -e "${BOLD}============================================${NC}"
echo -e "${BOLD} Development Assistant — 一键初始化${NC}"
echo -e "${BOLD}============================================${NC}"
echo ""

# ═════════════════════════════════════════════════
# Step 1: 替换所有 __PLUGIN_DIR__ 占位符
# ═════════════════════════════════════════════════
echo -e "${YELLOW}[1/5]${NC} 替换路径占位符..."

# 1a. hooks.json
HOOKS_EXAMPLE="$PLUGIN_DIR/hooks/hooks.json.example"
HOOKS_TARGET="$PLUGIN_DIR/hooks/hooks.json"

if [ -f "$HOOKS_EXAMPLE" ]; then
    sed "s|__PLUGIN_DIR__|$PLUGIN_DIR|g" "$HOOKS_EXAMPLE" > "$HOOKS_TARGET"
fi

# 1b. Agent 文件 + 派生文件
for f in \
    "$PLUGIN_DIR/agents/development.agent.md" \
    "$PLUGIN_DIR/agents/development.study.agent.md" \
    "$PLUGIN_DIR/rules/development.md" \
    "$PLUGIN_DIR/rules/development.study.md" \
    "$PLUGIN_DIR/skills/development/SKILL.md" \
    "$PLUGIN_DIR/skills/development-study/SKILL.md"; do
    if [ -f "$f" ]; then
        sed -i '' "s|__PLUGIN_DIR__|$PLUGIN_DIR|g" "$f"
    fi
done

echo -e "  ${GREEN}✓${NC} 路径占位符已替换"

# ═════════════════════════════════════════════════
# Step 2: Python venv + 依赖安装
# ═════════════════════════════════════════════════
echo -e "${YELLOW}[2/5]${NC} Python 虚拟环境 & 依赖..."

VENV_DIR="$PLUGIN_DIR/server/.venv"
REQS_FILE="$PLUGIN_DIR/server/requirements.txt"

if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
    echo "  虚拟环境已创建"
fi

# 检查是否已安装（比 requirements.txt 快）
if "$VENV_DIR/bin/python3" -c "import sentence_transformers, lancedb" 2>/dev/null; then
    echo -e "  ${GREEN}✓${NC} 依赖已就绪"
else
    echo "  安装依赖中..."
    "$VENV_DIR/bin/pip" install --quiet --upgrade pip 2>/dev/null
    "$VENV_DIR/bin/pip" install --quiet -r "$REQS_FILE"
    echo -e "  ${GREEN}✓${NC} 依赖安装完成"
fi

# ═════════════════════════════════════════════════
# Step 3: 下载 embedding 模型到项目目录
# ═════════════════════════════════════════════════
echo -e "${YELLOW}[3/5]${NC} Embedding 模型..."

MODEL_DIR="$PLUGIN_DIR/references/.models"
MODEL_SENTINEL="$MODEL_DIR/models--sentence-transformers--paraphrase-multilingual-MiniLM-L12-v2/snapshots"

if [ -d "$MODEL_SENTINEL" ] && [ "$(ls -A "$MODEL_SENTINEL" 2>/dev/null)" ]; then
    echo -e "  ${GREEN}✓${NC} 模型已就绪"
else
    echo "  下载 paraphrase-multilingual-MiniLM-L12-v2（首次约 500MB）..."
    mkdir -p "$MODEL_DIR"
    "$VENV_DIR/bin/python3" -c "
import os
os.environ['SENTENCE_TRANSFORMERS_HOME'] = '$MODEL_DIR'
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
print('  Model loaded OK')
"
    echo -e "  ${GREEN}✓${NC} 模型下载完成"
fi

# ═════════════════════════════════════════════════
# Step 4: 初始化海马体（空数据库）
# ═════════════════════════════════════════════════
echo -e "${YELLOW}[4/5]${NC} 海马体数据库..."

DB_PATH="$PLUGIN_DIR/hippocampus/memory.db"

if [ -f "$DB_PATH" ]; then
    echo -e "  ${GREEN}✓${NC} 数据库已存在"
else
    "$VENV_DIR/bin/python3" -c "
import sys
sys.path.insert(0, '$PLUGIN_DIR')
from hippocampus.core import init_db
init_db()
"
    echo -e "  ${GREEN}✓${NC} 空数据库已创建"
fi

# ═════════════════════════════════════════════════
# Step 5: 对种子文档建立向量索引
# ═════════════════════════════════════════════════
echo -e "${YELLOW}[5/5]${NC} References 向量索引..."

INDEX_DIR="$PLUGIN_DIR/references/.index/.lancedb"

if [ -d "$INDEX_DIR" ] && [ "$(ls -A "$INDEX_DIR" 2>/dev/null)" ]; then
    echo -e "  ${GREEN}✓${NC} 索引已存在"
else
    echo "  对种子文档建立索引..."
    "$VENV_DIR/bin/python3" -c "
import os
os.environ['SENTENCE_TRANSFORMERS_HOME'] = '$MODEL_DIR'
import sys
sys.path.insert(0, '$PLUGIN_DIR')
from references.core import references_reindex
result = references_reindex(force=True)
print(result)
"
    echo -e "  ${GREEN}✓${NC} 索引建立完成"
fi

# ═════════════════════════════════════════════════
echo ""
echo -e "${BOLD}============================================${NC}"
echo -e " ${GREEN}初始化完成！${NC}"
echo -e "${BOLD}============================================${NC}"
echo ""
echo "  添加 MCP server:"
echo -e "    ${BOLD}claude mcp add dev-assistant -- bash $PLUGIN_DIR/server/run.sh${NC}"
echo ""
