# Development Assistant

通用信息技术领域的 AI 开发决策助理插件，适用于 Claude Code / Cursor。

## 功能

- **海马体记忆层** (Hippocampus) — 跨会话持久化用户技术偏好，基于 SQLite 的轻量记忆系统
- **References 知识库** — LanceDB + SentenceTransformer 语义向量检索，支持自然语言查询
- 覆盖 iOS / Android / Web / 小程序 / Flutter / React Native 等技术栈
- 架构设计、技术选型、性能优化、代码审查等决策支持

## 目录结构

```
├── agents/          # Agent 定义文件（真相源）
├── commands/        # 斜杠命令定义
├── skills/          # Skill 定义
├── hooks/           # SessionStart / PreToolUse 钩子
├── rules/           # 派生规则文件（由 agent body 自动同步）
├── server/          # MCP Server 入口（FastMCP）
├── references/      # 知识库模块
│   ├── docs/        # 参考文档（Markdown + frontmatter）
│   ├── .index/      # LanceDB 向量索引（自动生成）
│   └── .models/     # Embedding 模型（自动下载）
├── hippocampus/     # 海马体记忆模块
│   └── memory.db    # SQLite 数据库（自动生成）
└── setup.sh         # 一键初始化脚本
```

## 快速开始

### 1. 克隆项目

```bash
git clone <repo-url> dev-assistant
cd dev-assistant
```

### 2. 运行初始化脚本

```bash
chmod +x setup.sh
./setup.sh
```

初始化脚本会自动完成：
- 生成 `hooks/hooks.json`（根据实际路径）
- 创建 Python 虚拟环境并安装依赖
- 下载 SentenceTransformer embedding 模型（约 500MB，仅首次）
- 初始化空海马体数据库
- 对种子参考文档建立向量索引

### 3. 配置 MCP Server

在 Claude Code 中添加 MCP server：

```bash
claude mcp add dev-assistant -- bash /path/to/dev-assistant/server/run.sh
```

### 4. 添加参考文档

1. 在 `references/docs/` 下创建 `{tag}_{topic}.md`
2. 参考 `references/docs/_TEMPLATE.md` 的 frontmatter 格式
3. 在 `references/TAGS.md` 注册新标签（如需）
4. 在 `references/INDEX.md` 添加条目
5. 调用 `knowledge_add_doc` MCP 工具触发增量索引

## 依赖

- Python 3.11+
- [SentenceTransformer](https://www.sbert.net/) — 文本向量化
- [LanceDB](https://lancedb.github.io/lancedb/) — 向量数据库
- [FastMCP](https://github.com/jlowin/fastmcp) — MCP Server 框架

## License

MIT — 详见 [LICENSE](LICENSE)
