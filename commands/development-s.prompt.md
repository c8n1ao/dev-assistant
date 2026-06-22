---
mode: 'agent'
description: 'development · 快捷启动：激活海马体并检索相关历史偏好'
---

FIRST call `activate_memory_management_tools`.
Then call `hippocampus_search` with a query that captures the session topic.
Report results briefly: "🧠 检索到 N 条相关记忆" with a one-line summary of each.
If tools are unavailable, say "⚠️ 海马体不可用" and proceed.
