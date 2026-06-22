---
mode: 'agent'
description: 'development · 激活自主学习 agent，采集技术知识生成草稿'
---

# /development-study — 自主学习命令

激活自主学习 agent。从官方文档和技术社区主动收集、筛选、提炼技术知识，
生成结构化草稿供用户审核后入库。

## 使用方式

- `/development-study iOS 18 SwiftData 迁移最佳实践` — 定向学习指定主题
- `/development-study --explore 计算机图形学` — 探索学习（含子主题拆分）
- `/development-study --review` — 审核待处理草稿
- `/development-study --discover` — 自由发现（v2 预留）

## 前置操作

调用 hippocampus 相关工具前，必须先用 `activate_memory_management_tools` 激活工具组。

## 执行流程

严格按 `skills/development-study/SKILL.md` 中的 Step 0 → Step 1 → Step 2 → Step 3 流程执行。
所有写入操作遵循 `CONVENTIONS.md` 中的公共约束规范。
