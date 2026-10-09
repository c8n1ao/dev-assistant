# 公共约束规范

> 本文档是海马体（hippocampus）和知识库（references）固有规则的精简聚合版。
> 原文件 `hippocampus/INDEX.md` 和 `references/QUALITY_GATE.md` 保留作为详细参考。

## 维护规则

- **CONVENTIONS.md 是 agent 引用的唯一入口**——development.agent.md 和 study.agent.md 只引用本文档的 §N 章节
- 当原文件（INDEX.md / QUALITY_GATE.md）更新时，**必须同步更新**本文档对应章节
- 当本文档与原文件出现分歧时，**以本文档为准**——本文档是 agent 读取的单一真相源
- 新增规则时，先更新本文档，再同步到原文件的对应位置（保持双向一致）

---

## §1 海马体信号级别（signal_level）

决定何时写入记忆及初始权重：

| 级别 | 触发条件 | 初始权重 | AI 行为 |
|:----:|---------|:-------:|---------|
| `high` | 用户显式修正（"不对，应该是…"） | 2 | 自动写入 |
| `medium` | 深度追问某方向 / 采纳某选项进入执行 | 1 | 提议写入，用户确认后执行 |
| `weak` | 沉默 / 话题漂移 | — | **不写入**（MCP 层直接拒绝） |
| 标注 | 压力或妥协情境下的选择 | 同 medium | 写入但标注（降权提示） |

---

## §2 海马体记忆类型（memory_type）

| 类型 | 用途 | 启动注入 |
|------|------|:--------:|
| `user_preference` | 用户技术偏好（默认） | 始终 |
| `maintenance_checklist` | 框架维护清单 | 仅框架内部话题 |
| `architecture_decision` | 架构决策记录 (ADR) | 仅框架内部话题 |
| `known_issue` | 已知问题/限制/规避方案 | 仅框架内部话题 |
| `coding_principle` | 编码原则与最佳实践 | 始终 |

> **设计原则**：`user_preference` 和 `coding_principle` 高频注入避免遗漏；后三类是低频维护信息，仅在框架内部话题时关注。

---

## §3 海马体内容结构规范

写入 `content` 时使用**锚点+自由叙述**格式：

```
排除: <被排除的替代方案及排除原因，自由叙述>
选择: <最终决策>
情境: <决策背景：团队规模、时间约束、技术栈上下文等>
失效条件: <什么可观测事件会使该偏好失效>
```

| 锚点 | 是否必填 | 说明 |
|------|:--------:|------|
| `排除:` | 推荐 | 记录了「为什么不选 B」——方案名 + 排除原因 |
| `选择:` | 推荐 | 最终决策，有具体方案描述 |
| `情境:` | 推荐 | 决策背景：团队规模、时间约束、已有技术栈 |
| `失效条件:` | **必填** | 偏好的边界——什么可观测事件发生时需重新评估。写不出时用「暂不明确，需在实际使用中观察后补充」 |

**校验规则**（`hippocampus_add` 写入前自动执行）：

| 条件 | 行为 |
|------|:----:|
| `失效条件:` 锚点缺失或值为空 | **block**（拒写） |
| `排除:` / `选择:` 锚点缺失 | warning（写成功但提示） |
| `排除:` 存在但值 < 10 字 | warning（只有名称没有原因） |

**写入前自检**：三年后 AI 读到这条记忆，能否据此还原当时的判断逻辑？不能就别写。

### §3.1 按记忆类型的格式适配

不同 `memory_type` 的内容性质不同，锚点格式需相应调整：

**`user_preference` / `architecture_decision`（决策型）**：使用完整四锚点格式。

```
排除: <被排除的替代方案及排除原因>
选择: <最终决策>
情境: <决策背景：团队规模、时间约束、技术栈上下文等>
失效条件: <什么可观测事件会使该偏好失效>
```

**`coding_principle`（原则型）**：原则不是"选择"，是"规则"。使用原则格式。

```
原则: <编码原则的核心规则，用 1-3 句话概括>
适用场景: <什么情境下应遵循此原则>
反例: <违反此原则的典型模式，含具体代码示例或场景描述>
失效条件: <什么可观测条件下可以打破此原则>
```

> ⚠️ `coding_principle` 条目的「反例」锚点等同于决策型的「排除」——记录"不做什么及为什么"。禁止写「原则: 代码应可读」这种空洞声明——必须附具体反例（如 `dataArr`、`tempVal` 命名）。

**`maintenance_checklist` / `known_issue`（记录型）**：记录事实而非决策。

```
事项: <需要记住的维护事项或已知问题>
触发条件: <什么时候需要关注此事项>
失效条件: <什么可观测事件会使此事项不再需要关注>
```

### §3.2 维度命名与注册规则

`dimension` 字段必须在 `hippocampus/INDEX.md` 的「常用维度」表中已注册。未注册维度会导致：

- 冲突检测失效——同 platform 下不同主题的条目可能因维度名不匹配而无法正确取代
- 检索精度下降——AI 无法通过维度名推断条目的技术领域
- `platform_weights` 聚合碎片化——每个未注册维度独立一行，无法反映真实的偏好稳定性

**维度命名规范**：
- 使用 `snake_case` 英文（如 `code_conventions`、`state_management`）
- 禁止 kebab-case（如 `coding-standards`）、空格
- 知识库维护相关维度可使用中文（如 `知识库维护`），但仅限于已在 INDEX.md 维度表中注册的中文维度
- 新增维度必须先注册到 `hippocampus/INDEX.md` 的维度表，再使用
- **INDEX.md 维度表是唯一权威源**——本节的命名规范从属于它。若维度表中已存在中文维度，以表为准

**写入前维度校验**（agent 侧强制执行）：
- [ ] 拟用的 `dimension` 是否在 `hippocampus/INDEX.md` 维度表中？
- [ ] 若不在 → 先判断：现有维度能否覆盖此条目的技术领域？能则归类到已有维度
- [ ] 若确实需要新维度 → 先在 INDEX.md 维度表末尾追加一行，再写入记忆

### §3.3 失效条件可观测性标准

`失效条件` 必须描述**可观测的触发事件**——能被自动化检查或人工明确判断的条件。

✅ **可观测**：
- "VS Code 版本 ≥ 1.125.0 时重新验证"（版本号明确，可检查）
- "团队扩展到 5 人以上时重新评估"（人数阈值明确）
- "记忆条目超过 10,000 条且查询延迟 > 100ms 时"（量化指标）

❌ **不可观测**（禁止使用）：
- "重大版本更新时重新评估"（什么是"重大"？谁的版本？）
- "新权威源发布时重新学习"（什么算"权威"？如何发现？）
- "AI 能力跃迁时重新评估"（无法定义"跃迁"）
- "项目需求变化时重新考虑"（什么变化？怎么判断？）

> ⚠️ 若暂时写不出可观测的失效条件，使用诚实占位：「失效条件: 暂不明确，需在实际使用中观察后补充」。这比模糊的伪条件更好——至少不会给 AI 一种"这个条件可以被检查"的错觉。

---

## §4 QG-1 写入触发条件

四个条件**全部满足**才触发写入：

1. 该主题**可能再次被问到**（非一次性问题）
2. 有明确的「正确答案」或**可验证的领域共识**（非纯观点/偏好）
3. 内容不重复已有文档 — 若 knowledge_search 和 INDEX.md 语义对齐均未命中，即视为满足
4. 内容具有**参考复用价值**（适用于多个场景/项目）

---

## §5 QG-2 写入流程（七步）

1. AI 生成草稿（含 keywords 字段，中英双语 5-15 个）
2. 呈现决策点，等待用户确认
3. 写入 vault 对应目录（`references/docs/obsidian-knowledge/` 是软链；跨项目 → `global/`，项目特定 → `projects/<project>/`；按 QG-8 命名）
4. 更新 `TAGS.md`（references 侧元数据；新标签先注册再使用，QG-9）
5. 更新**写入目录自己的** INDEX（`global/INDEX.md` 用 Markdown 链接、`projects/<project>/INDEX.md` 用 wiki link）
6. 调用 `knowledge_add_doc()` 增量索引
7. 海马体记录

> 若任一步骤失败，立即停止后续步骤，输出 `⚠️ QG-2 写入中断：{步骤名} 失败`，询问用户是否重试。

---

## §6 QG-3 Frontmatter 必填字段

| 字段 | 必填 | 说明 |
|------|:--:|------|
| `title` | 是 | 文档标题 |
| `primary_tag` | 是* | 主标签，须为 tags 列表中的一项，用作文件名前缀（*study agent 专用，手动文档可选） |
| `tags` | 是 | 标签列表，须在 TAGS.md 中已注册 |
| `keywords` | 是 | 中英双语，5-15 个，参见 QG-11 |
| `added` | 是 | 添加日期 (YYYY-MM-DD) |
| `source` | 是 | 来源 URL 或描述（字符串），或增强格式的对象数组 `[{url, type, accessed, covers, freshness}]`（study agent 专用）。增强格式向上兼容简单格式 |
| `credibility` | 是 | 可信度评分 1-10，参见 QG-4 |
| `verified` | 否 | 是否已被验证 |
| `reviewed_by` | 否 | 审核者 |
| `supersedes` | 否 | 取代的文档路径 |
| `superseded_by` | 否 | 被取代的文档路径 |

> **source 字段的两种形式**：简单形式为字符串 `"https://..."` 或描述文本；增强形式为对象数组，每个对象含 `url`、`type` (L1/L2/L3)、`accessed` (日期)、`covers` (覆盖的子要点列表)、`freshness` (verified/stale)，由 study agent 使用。两种形式兼容——增强形式是该字段的合法扩展。

---

## §7 QG-4 Credibility 评分量表

| 分数 | 含义 | 示例 |
|:---:|------|------|
| 9-10 | 极高可信 | 官方文档、语言规范、WWDC/Google IO 官方 talk |
| 7-8 | 高可信 | 社区高票答案（SO >100 票）、权威博客 |
| 5-6 | 中等可信 | 知名开发者博客、项目实战经验 |
| 3-4 | 低可信 | 个人博客、未验证的经验分享 |
| 1-2 | 不可信 | 匿名来源、无日期、无作者背景 |

> AI 生成内容的默认 credibility 为 5。学习源可信度指南见 §11。

---

## §8 QG-8 文件命名规范

格式：`{tag}_{topic}.md`，使用下划线分隔。

- 示例：`ios_swiftui-navigation.md`、`flutter_gorouter-deep-linking.md`
- TDesign 等有子目录的组件库为例外情况，使用 `tdesign/miniprogram/components/{name}.md`

---

## §9 QG-9 标签注册规范

新标签**必须先注册到 `references/TAGS.md`**，再在文档 frontmatter 中使用。禁止使用未注册标签。

---

## §10 QG-11 Keywords 填写规范

- **数量**：5-15 个
- **语言**：必须中英双语，禁止单语种
- **覆盖**：核心概念 + 常见同义词 + 口语化表达
- 示例：`iOS 网络层, URLSession, networking, 请求封装, HTTP client`

---

## §11 学习源可信度指南

| 层级 | 源 | credibility |
|------|---|:---:|
| L1 | 官方文档（swift.org, developer.apple.com, developer.android.com） | 9-10 |
| L2 | SO >100 票已接受答案、WWDC/Google IO 官方 talk | 7-8 |
| L3 | 权威技术博客（nshipster, objc.io, kodeco） | 5-6 |
| 排除 | 低票 SO、Medium 无作者背景、付费墙、无日期文章 | — |

### 领域特化规则

```
iOS/macOS:
  L1: developer.apple.com, Swift.org, Swift Evolution proposals
  L2: WWDC session videos + transcripts, NSHipster, objc.io
  L3: 知名 iOS 开发者博客, Swift by Sundell

Android:
  L1: developer.android.com, Kotlin docs, AndroidX release notes
  L2: Google IO talks, Android Developers Blog
  L3: 知名 Android 开发者博客

Flutter:
  L1: docs.flutter.dev, api.flutter.dev, pub.dev (官方包)
  L2: Flutter Forward / Fluttercon talks, pub.dev (verified publisher)
  L3: 知名 Flutter 开发者博客

React:
  L1: react.dev, nextjs.org/docs
  L2: React Conf talks, SO >100 票答案
  L3: 知名 React 开发者博客, kentcdodds.com

Web 通用:
  L1: MDN Web Docs, web.dev, W3C 规范
  L2: Chrome Developers Blog, webkit.org/blog
  L3: CSS-Tricks, Smashing Magazine

AI/ML:
  L1: arXiv 高引论文, paperswithcode.com SOTA, 官方模型文档
  L2: 顶会论文 (NeurIPS/ICML/ICLR), OpenAI/Anthropic 官方博客
  L3: 知名 ML 工程师博客, Distill.pub
```

---

## §12 Obsidian 文档规范

### §12.1 Wiki Links 要求

文档内的相关概念、技术、框架必须用 `[[文件名]]` 进行交叉引用：

| 规则 | 说明 |
|------|------|
| 语法 | `[[文件名]]` 或 `[[文件名\|显示文字]]` |
| 别名优先 | 使用 `[[文件名\|显示文字]]` 增强可读性 |
| Dangling Link | 禁止引用不存在的文件，除非该文件是计划中即将创建的 |
| 覆盖范围 | 技术概念、相关框架、前置知识、进阶阅读均可链接 |

### §12.2 文档末尾 Backlinks 区（See Also）

每个文档末尾必须包含 `## 参见` 小节：

- 列出 3-8 个最相关的文档 wiki links，按相关性递减排列
- 格式：`- [[相关文档]] — 一句话说明关系`
- MoC 文件也应互相链接（跨域导航）

### §12.3 MoC 内容地图

每个领域/标签创建一个 `_moc_{domain}.md` 文件：

- 文件名格式：`_moc_{domain}.md`，放在 `docs/` 下
- frontmatter 必须含 `tags: [moc]`（新增 `moc` 标签，注册在 TAGS.md）
- MoC 包含：领域概述（1-2 句）、指向该领域所有文档的 wiki links 按子主题分组、指向相邻领域 MoC 的链接
- MoC 文件同样注册到向量索引

### §12.4 QG-2 流程补充

从 §5 QG-2 写入流程的 Step 1（AI 生成草稿）开始嵌入 wiki links：

- 草稿必须包含指向相关文档的 `[[wiki links]]`（不少于 3 个）
- 草稿末尾必须包含 `## 参见` 小节
- 若新文档属于某个已有 MoC 领域，必须在 QG-2 Step 7（海马体记录）后追加：确认 MoC 文件是否已包含新文档链接，未包含则更新 MoC
