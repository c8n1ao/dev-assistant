#!/bin/bash
# Development Assistant MCP Server wrapper
# 记忆层 (SQLite) + 知识库语义检索 (LanceDB + SentenceTransformer)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

LOG_DIR="$PROJECT_DIR/server"
mkdir -p "$LOG_DIR"

export PYTHONUNBUFFERED=1

exec "$PROJECT_DIR/server/.venv/bin/python3" \
  -u \
  "$PROJECT_DIR/server/mcp_entry.py" \
  2>>"$LOG_DIR/stderr.log"
