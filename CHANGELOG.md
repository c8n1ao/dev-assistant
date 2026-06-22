# Changelog

## 0.1.0 (2026-06-22) — Initial Open-Source Release

### Added
- 海马体记忆层 (Hippocampus)：SQLite 持久化，跨会话用户技术偏好
- References 知识库：LanceDB + SentenceTransformer 语义向量检索
- MCP Server 统一入口 (FastMCP)，提供 hippocampus_*/knowledge_* 工具
- SessionStart / PreToolUse 钩子，自动注入历史偏好与知识索引
- 一键初始化脚本 `setup.sh`：venv、依赖、模型下载、DB 建表、向量索引
- Agent 系统提示词（development / development-study）
- 种子参考文档（编码方法论 + 文档模板）
- 质量门规范 (QUALITY_GATE.md) 与标签注册系统 (TAGS.md)
- 项目相对路径架构，支持任意位置部署
- MIT License
