#!/usr/bin/env python3
"""
Development Assistant MCP Server — 统一入口
两个平行的能力模块在此注册到同一个 MCP 实例：

  hippocampus/core.py  →  海马体记忆层 (SQLite)
      偏好记忆、决策模式、跨会话持久化

  references/core.py   →  References 知识库 (LanceDB + SentenceTransformer)
      语义向量检索、文档索引、增量更新
"""

import sys
from pathlib import Path

# 确保插件根目录在 import 路径中（hippocampus/ 和 references/ 是同级目录）
PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from mcp.server.fastmcp import FastMCP

# ── 创建 MCP 实例 ──────────────────────────────────────
mcp = FastMCP("dev-assistant")

# ── 注册海马体记忆工具 ────────────────────────────────
from hippocampus.core import register_hippocampus_tools
register_hippocampus_tools(mcp)

# ── 注册知识库检索工具 ────────────────────────────────
from references.core import register_references_tools
register_references_tools(mcp)

# ── 启动 ───────────────────────────────────────────────
if __name__ == "__main__":
    mcp.run(transport="stdio")
