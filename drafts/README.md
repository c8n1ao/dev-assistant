# Drafts — 知识草稿目录

## 用途

自主学习 agent（`/development-study`）产生的知识草稿统一存储于此。每份草稿一个 `.md` 文件。

## 草稿格式

```markdown
---
title: 主题标题
tags: [tag1, tag2]
keywords: [关键词1, 关键词2, keyword3, ...]  # 中英双语，5-15 个
credibility: 6
source:
  - url: https://...
    type: L1_官方文档
    accessed: YYYY-MM-DD
added: YYYY-MM-DD
status: draft       # ← 草稿标记，入库后去除
---

# 主题标题

[正文...]
```

## 生命周期

```
/development-study {topic} → agent 学习 → 草稿写入此目录
         │
    /development-study --review → 用户审核
         │
    ├── Accept → 移入 references/docs/ + 入库 + 删除草稿
    ├── Reject → 记录拒绝原因到海马体 + 删除草稿
    └── Modify → 重新生成
```

## 生命周期管理

- **命名冲突**：同一天对同一 tag+topic 多次学习，文件名加序号后缀 `{date}_{tag}_{topic}-2.md`
- **过期提醒**：`/development-study --review` 自动标注草稿年龄，> 14 天提醒 ⚠️，> 30 天警告 🔴 源可能过时
- **孤儿清理**：`--review` 自动检测空文件或损坏格式的草稿，标记为「损坏」并建议删除
- **积压上限**：drafts/ 下超过 20 份草稿时，`--review` 开头提示「📊 积压: {N} 份，建议批量处理」

## 文件命名

`{YYYY-MM-DD}_{tag}_{topic}.md` 或 `{YYYY-MM-DD}_{tag}_{topic}-{N}.md`（冲突时）

## 相关命令

- `/development-study {topic}` — 学习指定主题
- `/development-study --explore {领域}` — 探索学习
- `/development-study --review` — 审核待处理草稿
