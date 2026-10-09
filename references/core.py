"""
References 知识库语义检索 — LanceDB + SentenceTransformer
为 dev-assistant 插件提供领域知识文档的语义向量检索能力。
存储: references/.index/.lancedb/  +  references/.models/
"""

import json
import hashlib
from pathlib import Path

# ── 配置 ──────────────────────────────────────────────
_PROJECT_ROOT = Path(__file__).resolve().parent.parent  # references/ -> project root
REFERENCES_ROOT = _PROJECT_ROOT / "references"
REFERENCES_DOCS_DIR = REFERENCES_ROOT / "docs"
REFERENCES_INDEX_DIR = REFERENCES_ROOT / ".index"
REFERENCES_LANCEDB_DIR = REFERENCES_INDEX_DIR / ".lancedb"
REFERENCES_HASHES_FILE = REFERENCES_INDEX_DIR / "_file_hashes.json"
_MODEL_BASE = REFERENCES_ROOT / ".models" / "models--sentence-transformers--paraphrase-multilingual-MiniLM-L12-v2"
_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# 全局变量（懒加载）
_embedding_model = None
_lancedb_table = None


# ═══════════════════════════════════════════════════════
# Helper 函数
# ═══════════════════════════════════════════════════════

def _parse_frontmatter(text: str) -> tuple:
    """手动解析 YAML frontmatter，返回 (fm_dict, body)"""
    if not text.startswith('---'):
        return {}, text
    parts = text.split('---', 2)
    if len(parts) < 3:
        return {}, text
    fm_text = parts[1]
    body = parts[2]
    fm = {}
    for line in fm_text.strip().split('\n'):
        line = line.strip()
        if ':' in line:
            key, val = line.split(':', 1)
            key = key.strip()
            val = val.strip()
            if val.startswith('[') and val.endswith(']'):
                val = [v.strip().strip("'\"") for v in val[1:-1].split(',') if v.strip()]
            else:
                val = val.strip("'\"")
                if val.lower() == 'true': val = True
                elif val.lower() == 'false': val = False
                elif val.lower() == 'null': val = None
                else:
                    try: val = int(val)
                    except ValueError:
                        try: val = float(val)
                        except ValueError: pass
            fm[key] = val
    return fm, body


def _split_by_h2(text: str, min_len: int = 100, max_len: int = 2000) -> list:
    """按 ## 标题切分 Markdown 正文，h3 归入父 h2"""
    sections = __import__('re').split(r'\n(?=## )', text)
    chunks = []
    for section in sections:
        section = section.strip()
        if not section:
            continue
        first_line = section.split('\n')[0]
        title = first_line.replace('## ', '').strip()
        if len(section) < min_len and chunks:
            chunks[-1]['content'] += '\n\n' + section
            continue
        if len(section) > max_len:
            paragraphs = section.split('\n\n')
            current = ''
            for para in paragraphs:
                if len(current) + len(para) > max_len and current:
                    chunks.append({'section_title': title, 'content': current.strip()})
                    current = para
                else:
                    current += ('\n\n' + para) if current else para
            if current.strip():
                chunks.append({'section_title': title, 'content': current.strip()})
        else:
            chunks.append({'section_title': title, 'content': section})
    return chunks


def _hash_file(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


def _load_hashes() -> dict:
    if REFERENCES_HASHES_FILE.exists():
        with open(REFERENCES_HASHES_FILE, 'r') as f:
            return json.load(f)
    return {}


def _save_hashes(hashes: dict):
    REFERENCES_INDEX_DIR.mkdir(parents=True, exist_ok=True)
    with open(REFERENCES_HASHES_FILE, 'w') as f:
        json.dump(hashes, f, indent=2)


def _find_model_snapshot():
    """Auto-detect snapshot directory (hash varies by model version)."""
    snapshots_dir = _MODEL_BASE / "snapshots"
    if snapshots_dir.is_dir():
        snapshots = [p for p in snapshots_dir.iterdir() if p.is_dir()]
        if snapshots:
            return snapshots[0]
    return None


def _get_embedding_model():
    """懒加载 SentenceTransformer embedding 模型。
    优先从项目内 .models/ 加载（setup.sh 预下载），
    未找到时自动从 HuggingFace 下载到项目目录。"""
    global _embedding_model
    if _embedding_model is None:
        from sentence_transformers import SentenceTransformer
        snap = _find_model_snapshot()
        if snap:
            _embedding_model = SentenceTransformer(
                str(snap), local_files_only=True,
                model_kwargs={"ignore_mismatched_sizes": True}
            )
        else:
            import os
            _cache = os.environ.get(
                "SENTENCE_TRANSFORMERS_HOME",
                str(REFERENCES_ROOT / ".models")
            )
            _embedding_model = SentenceTransformer(
                _MODEL_NAME, cache_folder=_cache,
                model_kwargs={"ignore_mismatched_sizes": True}
            )
    return _embedding_model


def _get_lancedb():
    """懒加载 LanceDB 连接 + 表"""
    global _lancedb_table
    if _lancedb_table is None:
        import lancedb
        REFERENCES_LANCEDB_DIR.mkdir(parents=True, exist_ok=True)
        db = lancedb.connect(str(REFERENCES_LANCEDB_DIR))
        try:
            _lancedb_table = db.open_table("chunks")
        except Exception:
            _lancedb_table = None
    return _lancedb_table


def _build_single_file_chunks(filepath: Path, rel_path: str) -> list:
    """解析单个文档，返回 chunk dict 列表（不含 vector）"""
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    fm, body = _parse_frontmatter(text)
    credibility = fm.get('credibility', 5)
    if isinstance(credibility, (int, float)) and credibility <= 1:
        return []
    tags = fm.get('tags', [])
    if isinstance(tags, str):
        tags = [tags]
    tags_str = ','.join(tags) if tags else 'general'
    sections = _split_by_h2(body)
    if not sections:
        sections = [{'section_title': fm.get('title', filepath.stem), 'content': body[:2000]}]
    overview_content = f"# {fm.get('title', filepath.stem)}\n{fm.get('source', '')}\n\n{body[:500]}"
    rows = [{
        'file_path': rel_path,
        'section_title': f"[概览] {fm.get('title', filepath.stem)}",
        'content': overview_content[:2000],
        'tags': tags_str,
        'credibility': credibility if isinstance(credibility, (int, float)) else 5,
    }]
    for section in sections:
        rows.append({
            'file_path': rel_path,
            'section_title': section['section_title'],
            'content': section['content'],
            'tags': tags_str,
            'credibility': credibility if isinstance(credibility, (int, float)) else 5,
        })
    return rows


# ═══════════════════════════════════════════════════════
# MCP 工具实现（无装饰器 — 由 server/mcp_entry.py 注册）
# ═══════════════════════════════════════════════════════

def references_search(
    query: str, top_k: int = 5, tags: list[str] = [], min_credibility: int = 0,
) -> str:
    """
    在 References 知识库中执行语义搜索。

    Args:
        query: 自然语言查询，如 "SwiftUI 深色模式适配"
        top_k: 返回最多几个结果（默认 5）
        tags: 标签过滤，如 ["ios"]（可选）
        min_credibility: 最低可信度阈值（可选，默认 0 不过滤）
    """
    table = _get_lancedb()
    if table is None:
        return json.dumps({
            "results": [], "query": query, "total_hits": 0,
            "warning": "索引尚未构建。请先调用 knowledge_reindex(force=True)。"
        }, ensure_ascii=False, indent=2)

    model = _get_embedding_model()
    query_vec = model.encode([query], show_progress_bar=False)[0].tolist()

    # LanceDB 混合查询：向量 + 标量过滤
    try:
        search_builder = table.search(query_vec).metric("cosine")
        if tags:
            tag_conds = " OR ".join(f"tags LIKE '%{t}%'" for t in tags)
            search_builder = search_builder.where(f"({tag_conds})")
        if min_credibility > 0:
            search_builder = search_builder.where(f"credibility >= {min_credibility}")
        raw = search_builder.limit(top_k).to_list()
    except Exception as e:
        return json.dumps({
            "results": [], "query": query, "total_hits": 0, "error": str(e)
        }, ensure_ascii=False, indent=2)

    # 后处理：同文件去重 + 相似度转换
    seen_files = set()
    results = []
    for r in raw:
        fp = r.get('file_path', '')
        if fp in seen_files:
            continue
        seen_files.add(fp)
        content = r.get('content', '')
        snippet = content[:1000] + ('...' if len(content) > 1000 else '')
        dist = r.get('_distance', 2.0)
        similarity = round(max(0.0, 1.0 - float(dist) / 2.0), 4)

        tags_str = r.get('tags', '')
        tags_list = [t.strip() for t in tags_str.split(',') if t.strip()] if isinstance(tags_str, str) else []

        results.append({
            'file_path': fp,
            'section_title': r.get('section_title', ''),
            'content_snippet': snippet,
            'tags': tags_list,
            'credibility': r.get('credibility', 0),
            'similarity': similarity,
        })
        if len(results) >= top_k:
            break

    return json.dumps({
        "results": results, "query": query, "total_hits": len(results),
    }, ensure_ascii=False, indent=2)


def references_index_file(doc_path: str = "") -> str:
    """
    对单个 References 文档执行增量索引（写入或更新后调用）。

    Args:
        doc_path: 相对于 docs/ 的文件路径，如 "docs/ios_new-topic.md"
    """
    table = _get_lancedb()
    if table is None:
        return json.dumps({
            "status": "error", "reason": "索引尚未初始化。请先调用 knowledge_reindex(force=True)。"
        }, ensure_ascii=False)

    if doc_path.startswith('docs/'):
        rel_path = doc_path
    else:
        rel_path = f"docs/{doc_path}"

    full_path = REFERENCES_DOCS_DIR.parent / rel_path
    if not full_path.exists():
        return json.dumps({"status": "error", "reason": f"文件不存在: {full_path}"}, ensure_ascii=False)

    hashes = _load_hashes()
    file_hash = _hash_file(full_path)
    if hashes.get(rel_path) == file_hash:
        return json.dumps({"status": "skipped", "reason": "unchanged"}, ensure_ascii=False)

    rows = _build_single_file_chunks(full_path, rel_path)
    if not rows:
        return json.dumps({"status": "skipped", "reason": "credibility <= 1"}, ensure_ascii=False)

    model = _get_embedding_model()
    texts = [row['content'] for row in rows]
    vectors = model.encode(texts, show_progress_bar=False).tolist()
    for i, row in enumerate(rows):
        row['vector'] = vectors[i]

    try:
        table.delete(f"file_path = '{rel_path}'")
    except Exception:
        pass
    table.add(rows)

    hashes[rel_path] = file_hash
    _save_hashes(hashes)

    return json.dumps({"status": "indexed", "chunks_added": len(rows)}, ensure_ascii=False)


def references_reindex(force: bool = False) -> str:
    """
    全量重建 References 向量索引（LanceDB）。

    Args:
        force: 是否强制重建（忽略文件哈希缓存）
    """
    import lancedb
    import numpy as np

    global _embedding_model, _lancedb_table

    hashes = _load_hashes() if not force else {}
    all_rows = []
    indexed_files = 0
    errors = []

    # recurse_symlinks: docs/obsidian-knowledge is a symlink to the Obsidian vault's
    # knowledge/ dir; without it rglob skips the linked subtree and the vault stays
    # unsearchable. Requires Python 3.13+ (the venv pins 3.13).
    for md_file in sorted(REFERENCES_DOCS_DIR.rglob("*.md", recurse_symlinks=True)):
        rel_path = str(md_file.relative_to(REFERENCES_DOCS_DIR.parent))
        try:
            rows = _build_single_file_chunks(md_file, rel_path)
            if rows:
                indexed_files += 1
                hashes[rel_path] = _hash_file(md_file)
                all_rows.extend(rows)
        except Exception as e:
            errors.append({"file": rel_path, "error": str(e)})

    if not all_rows:
        return json.dumps({"status": "error", "reason": "未找到任何可索引的文档"}, ensure_ascii=False)

    model = _get_embedding_model()
    texts = [row['content'] for row in all_rows]
    vectors = model.encode(texts, show_progress_bar=True, batch_size=32).tolist()
    for i, row in enumerate(all_rows):
        row['vector'] = vectors[i]

    REFERENCES_LANCEDB_DIR.mkdir(parents=True, exist_ok=True)
    db = lancedb.connect(str(REFERENCES_LANCEDB_DIR))
    try:
        db.drop_table("chunks")
    except Exception:
        pass
    _lancedb_table = db.create_table("chunks", all_rows)

    _embedding_model = model
    _save_hashes(hashes)

    return json.dumps({
        "status": "complete", "indexed_files": indexed_files,
        "total_chunks": len(all_rows), "errors": errors,
    }, ensure_ascii=False, indent=2)


REF_ROOT = _PROJECT_ROOT


def knowledge_read_file(path: str) -> str:
    """
    读取插件目录下的任意文件（MCP 文件通道）。

    当 Agent 处于 Skill 沙箱环境，无法通过 read 工具直接访问插件文件时，
    通过此 MCP 工具读取 INDEX.md、reference 文档等内容。

    Args:
        path: 相对路径（如 "references/INDEX.md", "references/docs/ios_architecture.md",
              "hippocampus/INDEX.md"）或绝对路径
    """
    import os as _os
    try:
        # 支持相对路径和绝对路径
        if _os.path.isabs(path):
            logical = _os.path.normpath(path)
        else:
            logical = _os.path.normpath(_os.path.join(str(REF_ROOT), path))

        # 安全检查：逻辑路径必须在插件根目录内。用 normpath 而非 resolve——
        # resolve 会把 references/docs/obsidian-knowledge 这类指向 vault 的软链解析
        # 到根目录外而误拒，而该软链正是知识库的读入口。normpath 仍能挡掉 `..` 穿越。
        root = str(REF_ROOT)
        if not (logical == root or logical.startswith(root + _os.sep)):
            return json.dumps({
                "status": "error",
                "reason": f"路径超出插件根目录范围: {path}"
            }, ensure_ascii=False)

        target = Path(logical).resolve()

        if not target.is_file():
            return json.dumps({
                "status": "not_found",
                "path": str(target),
                "reason": "文件不存在"
            }, ensure_ascii=False)

        content = target.read_text(encoding="utf-8")
        return json.dumps({
            "status": "success",
            "path": str(target),
            "size": len(content),
            "lines": content.count("\n") + 1,
            "content": content
        }, ensure_ascii=False)

    except Exception as e:
        return json.dumps({
            "status": "error",
            "reason": str(e)
        }, ensure_ascii=False)


DRAFTS_DIR = REF_ROOT / "drafts"


def knowledge_write_drafts(filename: str, content: str) -> str:
    """
    写入草稿文件。仅允许写入 drafts/ 目录下的 .md 文件。

    安全约束（硬编码）：
    - 禁止路径穿越（/ \\ ..）
    - 仅允许 .md 后缀
    - 强制写入 drafts/ 目录
    - 文件名 ≤ 200 字符

    Args:
        filename: 文件名（不含路径），如 "2026-06-17_ios_swiftdata.md"
        content: 完整文件内容（Markdown + frontmatter）
    """
    import os as _os
    try:
        # ── 安全校验 ──
        if "/" in filename or "\\" in filename or ".." in filename:
            return json.dumps({
                "success": False,
                "error": "不允许的路径字符：filename 不能含 / \\ ..  ，仅接受纯文件名"
            }, ensure_ascii=False)

        if not filename.endswith(".md"):
            return json.dumps({
                "success": False,
                "error": "仅允许 .md 文件"
            }, ensure_ascii=False)

        if len(filename) > 200:
            return json.dumps({
                "success": False,
                "error": f"文件名过长（{len(filename)} > 200）"
            }, ensure_ascii=False)

        # ── 确保目录 ──
        _os.makedirs(DRAFTS_DIR, exist_ok=True)

        # ── 写入 ──
        target = DRAFTS_DIR / filename
        target.write_text(content, encoding="utf-8")

        return json.dumps({
            "success": True,
            "path": f"drafts/{filename}",
            "bytes": len(content.encode("utf-8"))
        }, ensure_ascii=False)

    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        }, ensure_ascii=False)


def knowledge_write_file(path: str, content: str) -> str:
    """
    写入插件根目录下的 .md 文件。仅允许 references/ 和 drafts/ 子目录。

    安全约束（硬编码）：
    - 禁止路径穿越（..  ）
    - 仅允许 .md 后缀
    - 仅允许 references/ 和 drafts/ 下的子路径
    - 路径 ≤ 500 字符

    Args:
        path: 相对路径（相对插件根目录），如 "references/docs/ios_xxx.md"
        content: 完整文件内容
    """
    import os as _os
    try:
        # ── 安全校验 ──
        if ".." in path:
            return json.dumps({
                "success": False,
                "error": "不允许的路径字符：.. "
            }, ensure_ascii=False)

        if not path.endswith(".md"):
            return json.dumps({
                "success": False,
                "error": "仅允许 .md 文件"
            }, ensure_ascii=False)

        if len(path) > 500:
            return json.dumps({
                "success": False,
                "error": f"路径过长（{len(path)} > 500）"
            }, ensure_ascii=False)

        # 目录白名单检查
        allowed = False
        for prefix in ("references/", "drafts/"):
            if path.startswith(prefix):
                allowed = True
                break
        if not allowed:
            return json.dumps({
                "success": False,
                "error": f"不允许的目录：仅允许 references/ 和 drafts/ 子目录，收到: {path}"
            }, ensure_ascii=False)

        # 路径穿越已由上面的 ".." 判断挡掉；此处不再 resolve——resolve 会把
        # references/docs/obsidian-knowledge 这类指向 vault 的软链解析到根目录外
        # 而误拒，而该软链正是知识库的写入目标（skill 产出落 knowledge/global/）。
        target = Path(_os.path.normpath(_os.path.join(str(REF_ROOT), path)))

        # ── 确保父目录 ──
        _os.makedirs(target.parent, exist_ok=True)

        # ── 写入 ──
        target.write_text(content, encoding="utf-8")

        return json.dumps({
            "success": True,
            "path": path,
            "bytes": len(content.encode("utf-8"))
        }, ensure_ascii=False)

    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        }, ensure_ascii=False)


def knowledge_delete_draft(filename: str) -> str:
    """
    删除指定草稿文件。仅允许删除 drafts/ 目录下的文件。

    Args:
        filename: 文件名（不含路径）
    """
    try:
        # ── 安全校验 ──
        if "/" in filename or "\\" in filename or ".." in filename:
            return json.dumps({
                "success": False,
                "error": "不允许的路径字符"
            }, ensure_ascii=False)

        if len(filename) > 200:
            return json.dumps({
                "success": False,
                "error": f"文件名过长（{len(filename)} > 200）"
            }, ensure_ascii=False)

        target = DRAFTS_DIR / filename

        if not target.is_file():
            return json.dumps({
                "success": False,
                "error": "文件不存在"
            }, ensure_ascii=False)

        target.unlink()

        return json.dumps({
            "success": True,
            "path": f"drafts/{filename}"
        }, ensure_ascii=False)

    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        }, ensure_ascii=False)


def register_references_tools(mcp):
    """向 FastMCP 实例注册所有 References 检索工具"""
    mcp.tool(name="dev-assistant-mcp_knowledge_search")(references_search)
    mcp.tool(name="dev-assistant-mcp_knowledge_add_doc")(references_index_file)
    mcp.tool(name="dev-assistant-mcp_knowledge_reindex")(references_reindex)
    mcp.tool(name="dev-assistant-mcp_knowledge_read_file")(knowledge_read_file)
    mcp.tool(name="dev-assistant-mcp_knowledge_write_drafts")(knowledge_write_drafts)
    mcp.tool(name="dev-assistant-mcp_knowledge_write_file")(knowledge_write_file)
    mcp.tool(name="dev-assistant-mcp_knowledge_delete_draft")(knowledge_delete_draft)
