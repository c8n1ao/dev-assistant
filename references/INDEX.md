# References Index

> 此文件由 development 框架维护，AI 在需要时可据此定位具体参考文档。
>
> **结构说明**：所有文档平铺在 `docs/` 目录下，分类由文档 frontmatter 中的 `tags` 字段声明。
> 标签注册表见 [TAGS.md](TAGS.md)，质量门规范见 [QUALITY_GATE.md](QUALITY_GATE.md)。

---

## 编码原则（tags: coding-principles）

| 文件                                    | 内容           | Tags              | Keywords                                     |
| --------------------------------------- | -------------- | ----------------- | -------------------------------------------- |
| `docs/coding-principles_methodology.md` | 好项目方法论   | coding-principles | 好项目方法论, methodology, coding-principles |
| `docs/_TEMPLATE.md`                     | 文档模板       | coding-principles | 模板, template, 文档格式                     |

---

## 使用说明

### 添加新文档

1. 创建 `docs/{tag}_{topic}.md`（参考 `_TEMPLATE.md` 的 frontmatter 格式）
2. 在 [TAGS.md](TAGS.md) 中注册新标签（如需）
3. 在本文件添加对应条目
4. 运行 `python3 references/core.py` 或调用 `knowledge_add_doc` MCP 工具触发增量索引

### 重建索引

首次使用或添加多个文档后，调用 `knowledge_reindex` MCP 工具进行全量重建。
