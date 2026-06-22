---
mode: 'agent'
description: 'development · 删除海马体中的指定记忆条目'
---

根据用户提供的条目 ID 或关键词，删除对应记忆。

执行逻辑：
1. 若用户已提供具体 ID，直接调用 `hippocampus_forget` 删除
2. 若未提供 ID，调用 `hippocampus_search` 列出相关条目，请用户确认要删除哪一条后再执行
3. 删除完成后输出：`🗑️ 已删除：[条目描述]`

若 hippocampus 工具不可用，输出：`⚠️ hippocampus 工具不可用，操作已取消`
