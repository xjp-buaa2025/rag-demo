# 爆炸图与知识图谱关联 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 BOM/IPC 爆炸图和维修手册示意图与 Neo4j 知识图谱关联，在装配问答时自动附带相关爆炸图。

**Architecture:** PyMuPDF 从 PDF 提取爆炸图并保存至 `storage/images/kg_figures/`；Neo4j 新增 `ExplodedView` 节点，通过 `SHOWN_IN`（零件→图）和 `ILLUSTRATED_BY`（工序→图）关系连接；Assembly Chat SSE done 帧新增 `figure_urls` 字段，前端新增折叠式爆炸图面板。

**Tech Stack:** PyMuPDF (`fitz`)、Neo4j Cypher (MERGE)、FastAPI SSE、React + TypeScript + Tailwind CSS v4

---

## 文件变更总表

| 文件 | 操作 | 职责 |
|------|------|------|
| `backend/pipelines/nodes_figures.py` | **新建** | IPC/Manual 图片提取 + Neo4j 写入辅助函数 |
| `backend/routers/kg_stages.py` | **修改** | Stage1/Stage2 调用图片提取，写 ExplodedView 节点 |
| `backend/routers/assembly.py` | **修改** | 新增 `_query_exploded_views()`，注入 figure sources |
| `backend/sse.py` | **修改** | done 帧提取 `figure_urls`（chunk_type=exploded_view） |
| `frontend/src/types/index.ts` | **修改** | 新增 `FigureUrl` 类型，扩展 `SseDoneFrame` |
| `frontend/src/hooks/useChat.ts` | **修改** | 新增 `figureUrls` 状态 |
| `frontend/src/components/assembly/ExplodedViewPanel.tsx` | **新建** | 爆炸图卡片折叠面板 |
| `frontend/src/components/shared/UnifiedChat.tsx` | **修改** | 装配模式下渲染 ExplodedViewPanel |
| `tests/kg/test_figure_extraction.py` | **新建** | 图片提取函数的单元测试 |

---

## Task 1：捕获 BOM 实体的 `item_callout`，创建 `nodes_figures.py`（IPC 提取）

**Files:**
- Modify: `backend/routers/kg_stages.py:257-264`（`_bom_df_to_entities_and_triples` 的 entities.append 块）
- Create: `backend/pipelines/nodes_figures.py`
- Create: `tests/kg/test_figure_extraction.py`

- [ ] **Step 1: 写失败测试（item_callout 字段）**

```python
# tests/kg/test_figure_extraction.py
import json
import pandas as pd
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from backend.routers.kg_stages import _bom_df_to_entities_and_triples


def test_entities_include_item_callout():
    """BOM 实体必须携带 item_callout 字段，来自 fig_item 列"""
    records = [
        {"part_id": "3034344", "part_name": "COMPRESSOR ROTOR", "nomenclature": "COMPRESSOR ROTOR",
         "fig_item": "-1", "qty": 1, "category": "Assembly", "parent_id": "", "material": "", "unit": "件"},
        {"part_id": "MS9556-06", "part_name": "BOLT,MACHINE", "nomenclature": ".BOLT,MACHINE",
         "fig_item": "10", "qty": 4, "category": "Standard", "parent_id": "", "material": "", "unit": "件"},
    ]
    df_json = pd.DataFrame(records).to_json(orient="records", force_ascii=False)
    entities, _ = _bom_df_to_entities_and_triples(df_json)

    callouts = {e["part_number"]: e.get("item_callout") for e in entities}
    assert callouts.get("3034344") == "-1", f"expected '-1', got {callouts.get('3034344')}"
    assert callouts.get("MS9556-06") == "10", f"expected '10', got {callouts.get('MS9556-06')}"
```

- [ ] **Step 2: 运行测试，确认失败**

```bash
cd /c/xjp/代码/rag-demo
PYTHONUTF8=1 "C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" \
  -m pytest tests/kg/test_figure_extraction.py::test_entities_include_item_callout -v
```

预期：`FAILED` — `KeyError` 或 `item_callout` 为 `None`

- [ ] **Step 3: 修改 `_bom_df_to_entities_and_triples`，在 entities.append 块加入 item_callout**

在 `backend/routers/kg_stages.py` 找到：
```python
        entities.append({
            "id":          pid or name,
            "type":        etype,
            "name":        name,
            "part_number": pid,
            "material":    str(row.get("material", "")).strip(),
            "quantity":    row.get("qty") or row.get("quantity", 1),
        })
```

替换为：
```python
        entities.append({
            "id":          pid or name,
            "type":        etype,
            "name":        name,
            "part_number": pid,
            "material":    str(row.get("material", "")).strip(),
            "quantity":    row.get("qty") or row.get("quantity", 1),
            "item_callout": str(row.get("fig_item", "")).strip(),
        })
```

- [ ] **Step 4: 运行测试，确认通过**

```bash
PYTHONUTF8=1 "C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" \
  -m pytest tests/kg/test_figure_extraction.py::test_entities_include_item_callout -v
```

预期：`PASSED`

- [ ] **Step 5: 写 `extract_ipc_figures` 的失败测试**

在 `tests/kg/test_figure_extraction.py` 追加：

```python
import tempfile, struct, zlib

def _make_minimal_pdf_with_figure(figure_number: int, img_bytes: bytes) -> bytes:
    """生成含有 'FIGURE N' 文本和一张嵌入图片的最小 PDF（用于测试）"""
    import fitz
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    page.insert_text((50, 100), f"FIGURE {figure_number}  COMPRESSOR ROTOR", fontsize=14)
    page.insert_text((50, 120), "COMPRESSOR ROTOR INSTALLATION", fontsize=10)
    # 嵌入一个 1x1 白色 PNG 作为测试图片（不需要真实爆炸图）
    import io
    from PIL import Image as PILImage
    img = PILImage.new("RGB", (400, 300), color=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    rect = fitz.Rect(50, 140, 450, 440)
    page.insert_image(rect, stream=buf.read())
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def test_extract_ipc_figures_finds_figure_page(tmp_path):
    """extract_ipc_figures 应检测到 FIGURE 1 页面，提取图片并返回元数据"""
    from backend.pipelines.nodes_figures import extract_ipc_figures

    pdf_bytes = _make_minimal_pdf_with_figure(1, b"")
    pdf_file = tmp_path / "test_ipc.pdf"
    pdf_file.write_bytes(pdf_bytes)

    results = extract_ipc_figures(str(pdf_file), figures_dir=str(tmp_path / "kg_figures"))

    assert len(results) == 1
    fig = results[0]
    assert fig["figure_number"] == 1
    assert fig["figure_id"] == "BOM_FIG_1"
    assert fig["source"] == "IPC"
    assert os.path.exists(os.path.join(str(tmp_path / "kg_figures"), os.path.basename(fig["image_path"])))
```

- [ ] **Step 6: 运行测试，确认失败（模块不存在）**

```bash
PYTHONUTF8=1 "C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" \
  -m pytest tests/kg/test_figure_extraction.py::test_extract_ipc_figures_finds_figure_page -v
```

预期：`FAILED` — `ModuleNotFoundError: backend.pipelines.nodes_figures`

- [ ] **Step 7: 创建 `backend/pipelines/nodes_figures.py`**

```python
"""backend/pipelines/nodes_figures.py — 爆炸图提取与 Neo4j 写入"""
import os
import re

import fitz  # PyMuPDF

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_DEFAULT_FIGURES_DIR = os.path.join(_ROOT, "storage", "images", "kg_figures")

_IPC_FIG_PATTERN = re.compile(r'FIGURE\s+(\d+)', re.IGNORECASE)
_MANUAL_FIG_PATTERN = re.compile(r'Figure\s+(\d+)', re.IGNORECASE)
_ATA_PATTERN = re.compile(r'\b(\d{2}-\d{2}-\d{2})\b')
_MIN_IMAGE_DIM = 200  # 爆炸图最小边长（过滤小图标）


def extract_ipc_figures(pdf_path: str, figures_dir: str = _DEFAULT_FIGURES_DIR) -> list:
    """
    扫描 IPC BOM PDF，找到含 'FIGURE N' 文本的页面，提取最大图片。
    返回 list[dict]：每项含 figure_number, figure_id, image_path(相对路径), title, page_number, source
    """
    os.makedirs(figures_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    results = []

    for page_num, page in enumerate(doc, 1):
        text = page.get_text()
        fig_match = _IPC_FIG_PATTERN.search(text)
        if not fig_match:
            continue

        images = page.get_images(full=True)
        best_xref, best_size = _pick_largest_image(images)
        if best_xref is None:
            continue

        figure_number = int(fig_match.group(1))
        base_image = doc.extract_image(best_xref)
        ext = base_image.get("ext", "png")
        filename = f"bom_fig_{figure_number}.{ext}"
        with open(os.path.join(figures_dir, filename), "wb") as f:
            f.write(base_image["image"])

        title = _extract_title_after_pattern(text, _IPC_FIG_PATTERN)

        results.append({
            "figure_number": figure_number,
            "figure_id":     f"BOM_FIG_{figure_number}",
            "image_path":    f"kg_figures/{filename}",
            "title":         title,
            "page_number":   page_num,
            "source":        "IPC",
            "ata_chapter":   None,
        })

    doc.close()
    return results


def _pick_largest_image(images: list):
    """从 fitz page.get_images() 列表中选出面积最大且超过最小尺寸的图片 xref。"""
    best_xref, best_size = None, 0
    for img_info in images:
        xref = img_info[0]
        w, h = img_info[2], img_info[3]
        if w > _MIN_IMAGE_DIM and h > _MIN_IMAGE_DIM and w * h > best_size:
            best_size = w * h
            best_xref = xref
    return best_xref, best_size


def _extract_title_after_pattern(text: str, pattern) -> str:
    """提取匹配行之后第一个非空行作为标题。"""
    lines = [l.strip() for l in text.split('\n')]
    for i, line in enumerate(lines):
        if pattern.search(line) and i + 1 < len(lines):
            candidate = lines[i + 1]
            if candidate and not pattern.search(candidate):
                return candidate
    return ""
```

- [ ] **Step 8: 运行测试，确认通过**

```bash
PYTHONUTF8=1 "C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" \
  -m pytest tests/kg/test_figure_extraction.py::test_extract_ipc_figures_finds_figure_page -v
```

预期：`PASSED`

- [ ] **Step 9: 提交**

```bash
cd /c/xjp/代码/rag-demo
git add backend/routers/kg_stages.py backend/pipelines/nodes_figures.py tests/kg/test_figure_extraction.py
git commit -m "feat(figures): add item_callout to BOM entities, add extract_ipc_figures"
```

---

## Task 2：Manual 图片提取 + Neo4j 写入函数

**Files:**
- Modify: `backend/pipelines/nodes_figures.py`（追加 `extract_manual_figures`, `write_exploded_views_to_neo4j`, `write_manual_figures_to_neo4j`）
- Modify: `tests/kg/test_figure_extraction.py`（追加测试）

- [ ] **Step 1: 写 Manual 提取的失败测试**

在 `tests/kg/test_figure_extraction.py` 追加：

```python
def _make_manual_pdf_with_figure(figure_number: int, ata_chapter: str) -> bytes:
    """生成含有 'Figure NNN' 文本、ATA章节和嵌入图片的最小维修手册 PDF"""
    import fitz, io
    from PIL import Image as PILImage
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    page.insert_text((50, 600), f"Removal/Installation of Compressor Wash Ring", fontsize=10)
    page.insert_text((50, 620), f"Figure {figure_number}", fontsize=10)
    page.insert_text((50, 680), f"{ata_chapter}", fontsize=12)
    img = PILImage.new("RGB", (400, 300), color=(200, 200, 200))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    page.insert_image(fitz.Rect(50, 100, 450, 580), stream=buf.read())
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def test_extract_manual_figures_finds_figure_page(tmp_path):
    """extract_manual_figures 应检测到 Figure 201 页面，提取图片和 ATA 章节"""
    from backend.pipelines.nodes_figures import extract_manual_figures

    pdf_bytes = _make_manual_pdf_with_figure(201, "72-30-02")
    pdf_file = tmp_path / "test_manual.pdf"
    pdf_file.write_bytes(pdf_bytes)

    results = extract_manual_figures(str(pdf_file), figures_dir=str(tmp_path / "kg_figures"))

    assert len(results) == 1
    fig = results[0]
    assert fig["figure_number"] == 201
    assert fig["figure_id"] == "MANUAL_FIG_201"
    assert fig["ata_chapter"] == "72-30-02"
    assert fig["source"] == "Manual"
    assert os.path.exists(os.path.join(str(tmp_path / "kg_figures"), os.path.basename(fig["image_path"])))
```

- [ ] **Step 2: 运行测试，确认失败**

```bash
PYTHONUTF8=1 "C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" \
  -m pytest tests/kg/test_figure_extraction.py::test_extract_manual_figures_finds_figure_page -v
```

预期：`FAILED` — `ImportError: cannot import name 'extract_manual_figures'`

- [ ] **Step 3: 在 `nodes_figures.py` 追加 `extract_manual_figures` 函数**

在文件末尾追加：

```python

def extract_manual_figures(pdf_path: str, figures_dir: str = _DEFAULT_FIGURES_DIR) -> list:
    """
    扫描维修手册 PDF，找到含大图 + 'Figure NNN' + ATA章节的页面。
    返回 list[dict]：每项含 figure_number, figure_id, image_path, title, ata_chapter, page_number, source
    """
    os.makedirs(figures_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    results = []

    for page_num, page in enumerate(doc, 1):
        text = page.get_text()
        fig_match = _MANUAL_FIG_PATTERN.search(text)
        ata_match = _ATA_PATTERN.search(text)

        if not fig_match:
            continue

        images = page.get_images(full=True)
        best_xref, best_size = _pick_largest_image(images)
        if best_xref is None:
            continue

        figure_number = int(fig_match.group(1))
        ata_chapter = ata_match.group(1) if ata_match else None

        base_image = doc.extract_image(best_xref)
        ext = base_image.get("ext", "png")
        filename = f"manual_fig_{figure_number}.{ext}"
        with open(os.path.join(figures_dir, filename), "wb") as f:
            f.write(base_image["image"])

        title = _extract_title_before_pattern(text, _MANUAL_FIG_PATTERN)

        results.append({
            "figure_number": figure_number,
            "figure_id":     f"MANUAL_FIG_{figure_number}",
            "image_path":    f"kg_figures/{filename}",
            "title":         title,
            "ata_chapter":   ata_chapter,
            "page_number":   page_num,
            "source":        "Manual",
        })

    doc.close()
    return results


def _extract_title_before_pattern(text: str, pattern) -> str:
    """提取匹配行之前最后一个非空行作为标题（维修手册：标题在 Figure NNN 上方）。"""
    lines = [l.strip() for l in text.split('\n')]
    for i, line in enumerate(lines):
        if pattern.search(line) and i > 0:
            for j in range(i - 1, -1, -1):
                if lines[j] and not pattern.search(lines[j]):
                    return lines[j]
    return ""
```

- [ ] **Step 4: 运行测试，确认通过**

```bash
PYTHONUTF8=1 "C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" \
  -m pytest tests/kg/test_figure_extraction.py -v
```

预期：全部 `PASSED`

- [ ] **Step 5: 在 `nodes_figures.py` 追加 Neo4j 写入函数**

在文件末尾追加：

```python

def write_exploded_views_to_neo4j(driver, ipc_figures: list, entities: list) -> tuple:
    """
    写 IPC ExplodedView 节点 + SHOWN_IN 关系。
    entities: BOM 实体列表，每项含 part_number 和 item_callout。
    返回 (写入数量, 状态消息)
    """
    try:
        with driver.session() as session:
            for fig in ipc_figures:
                session.run(
                    """
                    MERGE (f:ExplodedView {figure_id: $figure_id})
                    SET f.image_path = $image_path,
                        f.title      = $title,
                        f.source     = $source,
                        f.page_number = $page_number,
                        f.ata_chapter = null
                    """,
                    figure_id=fig["figure_id"],
                    image_path=fig["image_path"],
                    title=fig["title"],
                    source=fig["source"],
                    page_number=fig["page_number"],
                )

            written = 0
            for entity in entities:
                pn = entity.get("part_number", "")
                callout = entity.get("item_callout", "")
                if not pn or not callout:
                    continue
                # 单图 BOM：所有实体归属 figure_number=1；多图扩展时此处使用 entity.get("figure_number",1)
                figure_id = f"BOM_FIG_{entity.get('figure_number', 1)}"
                session.run(
                    """
                    MATCH (p {part_number: $pn})
                    MATCH (f:ExplodedView {figure_id: $figure_id})
                    MERGE (p)-[:SHOWN_IN {item_callout: $callout}]->(f)
                    """,
                    pn=pn, figure_id=figure_id, callout=callout,
                )
                written += 1

        return written, "OK"
    except Exception as e:
        return 0, str(e)


def write_manual_figures_to_neo4j(driver, manual_figures: list) -> tuple:
    """
    写 Manual ExplodedView 节点 + ILLUSTRATED_BY 关系。
    返回 (写入数量, 状态消息)
    """
    try:
        with driver.session() as session:
            for fig in manual_figures:
                session.run(
                    """
                    MERGE (f:ExplodedView {figure_id: $figure_id})
                    SET f.image_path  = $image_path,
                        f.title       = $title,
                        f.source      = $source,
                        f.ata_chapter = $ata_chapter,
                        f.page_number = $page_number
                    """,
                    figure_id=fig["figure_id"],
                    image_path=fig["image_path"],
                    title=fig["title"],
                    source=fig["source"],
                    ata_chapter=fig.get("ata_chapter"),
                    page_number=fig["page_number"],
                )

                if fig.get("ata_chapter"):
                    session.run(
                        """
                        MATCH (proc:Procedure)
                        WHERE proc.ata_chapter = $ata_chapter
                        MATCH (f:ExplodedView {figure_id: $figure_id})
                        MERGE (proc)-[:ILLUSTRATED_BY]->(f)
                        """,
                        ata_chapter=fig["ata_chapter"],
                        figure_id=fig["figure_id"],
                    )

        return len(manual_figures), "OK"
    except Exception as e:
        return 0, str(e)
```

- [ ] **Step 6: 提交**

```bash
git add backend/pipelines/nodes_figures.py tests/kg/test_figure_extraction.py
git commit -m "feat(figures): add extract_manual_figures and Neo4j write helpers"
```

---

## Task 3：Stage 1 BOM 集成图片提取

**Files:**
- Modify: `backend/routers/kg_stages.py`（修改 `_finalize_stage1`，在 Stage 1 收尾时调用图片提取与 Neo4j 写入）

- [ ] **Step 1: 修改 `_finalize_stage1` 函数**

找到 `backend/routers/kg_stages.py` 中的：

```python
def _finalize_stage1(tmp_path: str, entities: list, triples: list,
                     pipeline_state: dict, nodes: dict, neo4j_cfg: dict) -> None:
    """将实体/三元组写入 JSON 文件，尝试写 Neo4j（失败静默）。"""
    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_file":  os.path.basename(tmp_path),
        "entities":     entities,
        "triples":      triples,
        "stats": {
            "entities_count": len(entities),
            "triples_count":  len(triples),
        },
    }
    write_stage("bom", output)
    # 尝试 Neo4j（静默失败）
    try:
        neo4j_result = nodes["write_neo4j"](pipeline_state)
        import logging
        if "error" in neo4j_result:
            logging.getLogger(__name__).info(f"[Stage1] Neo4j 不可用：{neo4j_result['error']}")
    except Exception as e:
        import logging
        logging.getLogger(__name__).info(f"[Stage1] Neo4j 跳过：{e}")
```

替换为：

```python
def _finalize_stage1(tmp_path: str, entities: list, triples: list,
                     pipeline_state: dict, nodes: dict, neo4j_cfg: dict) -> None:
    """将实体/三元组写入 JSON 文件，提取 IPC 爆炸图，尝试写 Neo4j（失败静默）。"""
    import logging
    logger = logging.getLogger(__name__)

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_file":  os.path.basename(tmp_path),
        "entities":     entities,
        "triples":      triples,
        "stats": {
            "entities_count": len(entities),
            "triples_count":  len(triples),
        },
    }
    write_stage("bom", output)

    # ── IPC 爆炸图提取（PDF 专用，XLSX/CSV 跳过）──────────────
    ext = os.path.splitext(tmp_path)[1].lower().lstrip(".")
    ipc_figures = []
    if ext == "pdf":
        try:
            from backend.pipelines.nodes_figures import extract_ipc_figures
            ipc_figures = extract_ipc_figures(tmp_path)
            logger.info(f"[Stage1] 提取到 {len(ipc_figures)} 张 IPC 爆炸图")
        except Exception as e:
            logger.warning(f"[Stage1] IPC 爆炸图提取失败（跳过）: {e}")

    # ── 写 Neo4j：BOM 三元组 + ExplodedView 节点 ──────────────
    try:
        neo4j_result = nodes["write_neo4j"](pipeline_state)
        if "error" in neo4j_result:
            logger.info(f"[Stage1] Neo4j 不可用：{neo4j_result['error']}")
        elif ipc_figures:
            from backend.routers.bom import _get_neo4j_driver
            from backend.state import AppState as _AppState
            # neo4j_cfg 直接传入驱动构建
            try:
                from neo4j import GraphDatabase
                driver = GraphDatabase.driver(
                    neo4j_cfg.get("uri", "bolt://localhost:7687"),
                    auth=(neo4j_cfg.get("user", "neo4j"), neo4j_cfg.get("password", "")),
                )
                from backend.pipelines.nodes_figures import write_exploded_views_to_neo4j
                written, msg = write_exploded_views_to_neo4j(driver, ipc_figures, entities)
                driver.close()
                logger.info(f"[Stage1] ExplodedView 写入 Neo4j：{written} 条 SHOWN_IN 关系，{msg}")
            except Exception as e:
                logger.warning(f"[Stage1] ExplodedView Neo4j 写入失败（跳过）: {e}")
    except Exception as e:
        logger.info(f"[Stage1] Neo4j 跳过：{e}")
```

- [ ] **Step 2: 运行现有 BOM 测试，确认不破坏原有逻辑**

```bash
PYTHONUTF8=1 "C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" \
  -m pytest tests/kg/ -v
```

预期：所有测试 `PASSED`

- [ ] **Step 3: 提交**

```bash
git add backend/routers/kg_stages.py
git commit -m "feat(figures): Stage1 BOM integrates IPC figure extraction and Neo4j write"
```

---

## Task 4：Stage 2 Manual 集成图片提取

**Files:**
- Modify: `backend/routers/kg_stages.py`（修改 `_stage2_manual_gen`，在 Neo4j 写入后调用 Manual 图片提取）

- [ ] **Step 1: 在 `_stage2_manual_gen` 的 Neo4j 写入块之后追加 Manual 图片提取**

找到 `backend/routers/kg_stages.py` 中 `_stage2_manual_gen` 函数内的：

```python
    # 7. 尝试写 Neo4j
    yield {"type": "log", "message": "[Stage2] 尝试写入 Neo4j…"}
    neo4j_ok, neo4j_msg = _write_manual_to_neo4j(flat_triples, neo4j_cfg)
    if neo4j_ok:
        yield {"type": "log", "message": f"[Stage2] {neo4j_msg}"}
    else:
        yield {"type": "log", "message": f"[Stage2] Neo4j 不可用（{neo4j_msg}），仅保存 JSON"}
```

替换为：

```python
    # 7. 尝试写 Neo4j
    yield {"type": "log", "message": "[Stage2] 尝试写入 Neo4j…"}
    neo4j_ok, neo4j_msg = _write_manual_to_neo4j(flat_triples, neo4j_cfg)
    if neo4j_ok:
        yield {"type": "log", "message": f"[Stage2] {neo4j_msg}"}
    else:
        yield {"type": "log", "message": f"[Stage2] Neo4j 不可用（{neo4j_msg}），仅保存 JSON"}

    # 8. 维修手册示意图提取（PDF 专用）
    try:
        from backend.pipelines.nodes_figures import extract_manual_figures, write_manual_figures_to_neo4j
        manual_figures = extract_manual_figures(tmp_path)
        yield {"type": "log", "message": f"[Stage2] 提取到 {len(manual_figures)} 张维修手册示意图"}

        if manual_figures and neo4j_ok:
            from neo4j import GraphDatabase
            driver = GraphDatabase.driver(
                neo4j_cfg.get("uri", "bolt://localhost:7687"),
                auth=(neo4j_cfg.get("user", "neo4j"), neo4j_cfg.get("password", "")),
            )
            written, msg = write_manual_figures_to_neo4j(driver, manual_figures)
            driver.close()
            yield {"type": "log", "message": f"[Stage2] Manual ExplodedView 写入 Neo4j：{written} 个节点，{msg}"}
    except Exception as e:
        yield {"type": "log", "message": f"[Stage2] 示意图提取跳过：{e}"}
```

- [ ] **Step 2: 运行测试确认无回归**

```bash
PYTHONUTF8=1 "C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" \
  -m pytest tests/kg/ -v
```

预期：全部 `PASSED`

- [ ] **Step 3: 提交**

```bash
git add backend/routers/kg_stages.py
git commit -m "feat(figures): Stage2 Manual integrates maintenance figure extraction and Neo4j write"
```

---

## Task 5：Assembly Chat 注入爆炸图 + `sse.py` figure_urls

**Files:**
- Modify: `backend/routers/assembly.py`（新增 `_query_exploded_views()`，注入 figure sources）
- Modify: `backend/sse.py`（done 帧提取 figure_urls）

- [ ] **Step 1: 在 `backend/routers/assembly.py` 末尾添加 `_query_exploded_views` 函数**

在文件末尾（`@router.post("/agent"...` 之前）追加：

```python

def _query_exploded_views(cfg: dict, part_numbers: list) -> list:
    """
    查询 BOM 零件关联的 IPC ExplodedView 节点（SHOWN_IN 关系）。
    返回 list[dict]：每项含 figure_id, image_path, title, source, callout
    """
    if not part_numbers:
        return []
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(
            cfg.get("uri", "bolt://localhost:7687"),
            auth=(cfg.get("user", "neo4j"), cfg.get("password", "")),
        )
        with driver.session() as session:
            result = session.run(
                """
                MATCH (p)-[r:SHOWN_IN]->(f:ExplodedView)
                WHERE p.part_number IN $part_numbers
                RETURN f.figure_id   AS figure_id,
                       f.image_path  AS image_path,
                       f.title       AS title,
                       f.source      AS source,
                       f.ata_chapter AS ata_chapter,
                       r.item_callout AS callout
                """,
                part_numbers=part_numbers,
            )
            rows = [dict(r) for r in result]
        driver.close()
        # 去重（多个零件可能指向同一张图）
        seen = set()
        deduped = []
        for row in rows:
            fid = row.get("figure_id")
            if fid and fid not in seen:
                seen.add(fid)
                deduped.append(row)
        return deduped
    except Exception:
        return []


def _query_manual_figures_by_ata(cfg: dict, ata_chapters: list) -> list:
    """
    查询工序节点关联的 Manual ExplodedView 节点（ILLUSTRATED_BY 关系）。
    返回 list[dict]：每项含 figure_id, image_path, title, ata_chapter
    """
    if not ata_chapters:
        return []
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(
            cfg.get("uri", "bolt://localhost:7687"),
            auth=(cfg.get("user", "neo4j"), cfg.get("password", "")),
        )
        with driver.session() as session:
            result = session.run(
                """
                MATCH (proc:Procedure)-[:ILLUSTRATED_BY]->(f:ExplodedView)
                WHERE proc.ata_chapter IN $ata_chapters
                RETURN f.figure_id   AS figure_id,
                       f.image_path  AS image_path,
                       f.title       AS title,
                       f.source      AS source,
                       f.ata_chapter AS ata_chapter
                """,
                ata_chapters=ata_chapters,
            )
            rows = [dict(r) for r in result]
        driver.close()
        return rows
    except Exception:
        return []
```

- [ ] **Step 2: 修改 `_build_assembly_context_and_sources`，接受并注入 figure sources**

找到函数签名：
```python
def _build_assembly_context_and_sources(
    bom_result: dict,
    rag_chunks: list,
    proc_text: str = "",
):
```

替换为：
```python
def _build_assembly_context_and_sources(
    bom_result: dict,
    rag_chunks: list,
    proc_text: str = "",
    figures: list = None,
):
```

在函数末尾（`return "\n\n".join(context_parts), sources` 之前）追加：

```python
    # ── 爆炸图（exploded_view）→ 独立 Citation ────────────────
    for fig in (figures or []):
        image_url = f"/images/{fig.get('image_path', '')}"
        callout_info = f"（Item: {fig['callout']}）" if fig.get("callout") else ""
        ata_info = f"（ATA: {fig['ata_chapter']}）" if fig.get("ata_chapter") else ""
        label = f"爆炸图 · {fig.get('title', fig.get('figure_id', ''))} {callout_info}{ata_info}"
        sources.append({
            "id":           idx,
            "source":       label,
            "page":         fig.get("page_number", 0),
            "chunk_type":   "exploded_view",
            "text":         fig.get("title", ""),
            "image_url":    image_url,
            "figure_data":  fig,
        })
        idx += 1

```

- [ ] **Step 3: 修改 `_assembly_chat_gen_langchain` 和 `_assembly_chat_gen_native`，查询图片并传入**

在 `_assembly_chat_gen_langchain` 中找到：
```python
    # 2. 构建统一编号的上下文 + 结构化来源列表（每实体/关系独立编号）
    import json as _json
    context, sources = _build_assembly_context_and_sources(bom_result, rag_chunks, proc_text)
```

替换为：
```python
    # 2. 查询爆炸图（SHOWN_IN + ILLUSTRATED_BY）
    import re as _re
    part_numbers = [e.get("part_id", "") for e in bom_result.get("entities", []) if e.get("part_id")]
    ata_chapters = list({c for c in _re.findall(r'\b\d{2}-\d{2}-\d{2}\b', proc_text)})
    ipc_figs = _query_exploded_views(cfg, part_numbers)
    manual_figs = _query_manual_figures_by_ata(cfg, ata_chapters)
    all_figures = ipc_figs + manual_figs

    # 3. 构建统一编号的上下文 + 结构化来源列表（每实体/关系独立编号）
    import json as _json
    context, sources = _build_assembly_context_and_sources(bom_result, rag_chunks, proc_text, figures=all_figures)
```

同样修改 `_assembly_chat_gen_native` 中对应的 `_build_assembly_context_and_sources` 调用：

找到：
```python
    context, sources = _build_assembly_context_and_sources(bom_result, rag_chunks, proc_text)
```

替换为：
```python
    import re as _re
    part_numbers = [e.get("part_id", "") for e in bom_result.get("entities", []) if e.get("part_id")]
    ata_chapters = list({c for c in _re.findall(r'\b\d{2}-\d{2}-\d{2}\b', proc_text)})
    ipc_figs = _query_exploded_views(cfg, part_numbers)
    manual_figs = _query_manual_figures_by_ata(cfg, ata_chapters)
    all_figures = ipc_figs + manual_figs
    context, sources = _build_assembly_context_and_sources(bom_result, rag_chunks, proc_text, figures=all_figures)
```

- [ ] **Step 4: 修改 `backend/sse.py`，从 sources 提取 figure_urls 并加入 done 帧**

找到：
```python
        # 从 sources 中提取图片 URL（chunk_type=="image" 且有 image_url）
        image_urls = [
            s["image_url"] for s in sources
            if s.get("chunk_type") == "image" and s.get("image_url")
        ]

        yield _sse_data({"done": True, "sources": sources, "image_urls": image_urls})
```

替换为：
```python
        # 从 sources 中提取图片 URL（chunk_type=="image" 且有 image_url）
        image_urls = [
            s["image_url"] for s in sources
            if s.get("chunk_type") == "image" and s.get("image_url")
        ]

        # 提取爆炸图（chunk_type=="exploded_view"）
        figure_urls = [
            {
                "url":         s["image_url"],
                "title":       s.get("figure_data", {}).get("title", ""),
                "source":      s.get("figure_data", {}).get("source", ""),
                "callout":     s.get("figure_data", {}).get("callout"),
                "ata_chapter": s.get("figure_data", {}).get("ata_chapter"),
                "figure_id":   s.get("figure_data", {}).get("figure_id", ""),
            }
            for s in sources
            if s.get("chunk_type") == "exploded_view" and s.get("image_url")
        ]

        yield _sse_data({"done": True, "sources": sources, "image_urls": image_urls, "figure_urls": figure_urls})
```

- [ ] **Step 5: 运行测试确认无回归**

```bash
PYTHONUTF8=1 "C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" \
  -m pytest tests/kg/ -v
```

预期：全部 `PASSED`

- [ ] **Step 6: 提交**

```bash
git add backend/routers/assembly.py backend/sse.py
git commit -m "feat(figures): assembly chat queries exploded views, SSE done frame adds figure_urls"
```

---

## Task 6：前端类型 + useChat + ExplodedViewPanel + UnifiedChat 集成

**Files:**
- Modify: `frontend/src/types/index.ts`（新增 `FigureUrl`，扩展 `SseDoneFrame`）
- Modify: `frontend/src/hooks/useChat.ts`（新增 `figureUrls` 状态）
- Create: `frontend/src/components/assembly/ExplodedViewPanel.tsx`
- Modify: `frontend/src/components/shared/UnifiedChat.tsx`（装配模式下渲染 ExplodedViewPanel）

- [ ] **Step 1: 扩展 `frontend/src/types/index.ts`**

找到：
```typescript
/** SSE 聊天完成帧（/chat、/assembly/chat 最后一帧） */
export interface SseDoneFrame {
  done: true
  sources: Citation[]              // 结构化来源列表（供溯源侧边栏使用）
  image_urls?: string[]            // 图片块 URL 列表（从 sources 中提取）
}
```

替换为：
```typescript
/** 爆炸图 URL 及元数据 */
export interface FigureUrl {
  url: string
  title: string
  source: 'IPC' | 'Manual' | string
  callout?: string | null
  ata_chapter?: string | null
  figure_id: string
}

/** SSE 聊天完成帧（/chat、/assembly/chat 最后一帧） */
export interface SseDoneFrame {
  done: true
  sources: Citation[]              // 结构化来源列表（供溯源侧边栏使用）
  image_urls?: string[]            // 图片块 URL 列表（从 sources 中提取）
  figure_urls?: FigureUrl[]        // 爆炸图列表（装配模式专用）
}
```

- [ ] **Step 2: 修改 `frontend/src/hooks/useChat.ts`，新增 `figureUrls` 状态**

找到：
```typescript
interface UseChatResult {
  messages: Message[]
  /** 当前正在流式输出的文本（streaming 期间显示，done 后归档到 messages） */
  streamingText: string
  /** 最新回复的结构化来源列表（供溯源侧边栏使用） */
  sources: Citation[]
  /** 最新回复关联的图片 URL 列表（图文检索） */
  imageUrls: string[]
  loading: boolean
  /** 当前执行阶段描述（loading 期间有值，首个 token 或 done 后清空） */
  currentStage: string
  sendMessage: (
    userText: string,
    gen: AsyncGenerator<SseFrame>,
  ) => Promise<void>
  clearMessages: () => void
}
```

替换为：
```typescript
interface UseChatResult {
  messages: Message[]
  streamingText: string
  sources: Citation[]
  imageUrls: string[]
  /** 最新回复关联的爆炸图列表（装配模式专用） */
  figureUrls: FigureUrl[]
  loading: boolean
  currentStage: string
  sendMessage: (
    userText: string,
    gen: AsyncGenerator<SseFrame>,
  ) => Promise<void>
  clearMessages: () => void
}
```

在 import 行添加 `FigureUrl`：
```typescript
import type { Message, Citation, SseFrame, SseDeltaFrame, SseDoneFrame, SseErrorFrame, SseStageFrame, FigureUrl } from '../types'
```

在 `useChat` 函数体内找到：
```typescript
  const [imageUrls, setImageUrls] = useState<string[]>([])
```

在其后追加：
```typescript
  const [figureUrls, setFigureUrls] = useState<FigureUrl[]>([])
```

找到：
```typescript
          } else if ('done' in frame) {
            // 完成帧：从 streaming 区归档到 messages，提取结构化来源和图片
            setCurrentStage('')
            const done = frame as SseDoneFrame
            setSources(done.sources ?? [])
            setImageUrls(done.image_urls ?? [])
```

替换为：
```typescript
          } else if ('done' in frame) {
            setCurrentStage('')
            const done = frame as SseDoneFrame
            setSources(done.sources ?? [])
            setImageUrls(done.image_urls ?? [])
            setFigureUrls(done.figure_urls ?? [])
```

在 `sendMessage` 开头 `setSources([])` 处追加：
```typescript
      setFigureUrls([])
```

在 return 块添加 `figureUrls`：
```typescript
  return { messages, streamingText, sources, imageUrls, figureUrls, loading, currentStage, sendMessage, clearMessages }
```

- [ ] **Step 3: 创建 `frontend/src/components/assembly/ExplodedViewPanel.tsx`**

先创建目录：
```bash
mkdir -p "/c/xjp/代码/rag-demo/frontend/src/components/assembly"
```

创建文件：

```typescript
// frontend/src/components/assembly/ExplodedViewPanel.tsx
// 装配模式爆炸图折叠面板

import { useState } from 'react'
import type { FigureUrl } from '../../types'

interface Props {
  figures: FigureUrl[]
}

export default function ExplodedViewPanel({ figures }: Props) {
  const [open, setOpen] = useState(true)
  const [lightbox, setLightbox] = useState<string | null>(null)

  if (figures.length === 0) return null

  return (
    <>
      <div className="mt-3 border border-slate-200 rounded-lg overflow-hidden">
        <button
          onClick={() => setOpen(!open)}
          className="w-full flex items-center justify-between px-4 py-2 bg-slate-50 hover:bg-slate-100 transition-colors text-sm font-medium text-slate-700"
        >
          <span>📐 相关爆炸图（{figures.length} 张）</span>
          <span className="text-slate-400">{open ? '▲' : '▼'}</span>
        </button>

        {open && (
          <div className="p-3 flex flex-wrap gap-3">
            {figures.map((fig) => (
              <div
                key={fig.figure_id}
                className="flex flex-col items-center w-40 cursor-pointer group"
                onClick={() => setLightbox(fig.url)}
              >
                <div className="w-40 h-28 border border-slate-200 rounded overflow-hidden bg-white group-hover:border-orange-400 transition-colors">
                  <img
                    src={fig.url}
                    alt={fig.title || fig.figure_id}
                    className="w-full h-full object-contain"
                    onError={(e) => { (e.target as HTMLImageElement).style.display = 'none' }}
                  />
                </div>
                <p className="mt-1 text-xs text-center text-slate-600 leading-tight max-w-full truncate" title={fig.title}>
                  {fig.title || fig.figure_id}
                </p>
                <p className="text-[10px] text-slate-400">
                  {fig.source === 'IPC' && fig.callout ? `Item: ${fig.callout}` : fig.ata_chapter ?? ''}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 全屏弹窗 */}
      {lightbox && (
        <div
          className="fixed inset-0 z-50 bg-black/80 flex items-center justify-center"
          onClick={() => setLightbox(null)}
        >
          <img
            src={lightbox}
            alt="爆炸图"
            className="max-w-[90vw] max-h-[90vh] object-contain rounded shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          />
          <button
            className="absolute top-4 right-6 text-white text-3xl hover:text-slate-300"
            onClick={() => setLightbox(null)}
          >
            ×
          </button>
        </div>
      )}
    </>
  )
}
```

- [ ] **Step 4: 修改 `frontend/src/components/shared/UnifiedChat.tsx`，渲染 ExplodedViewPanel**

找到 import 行：
```typescript
import { useChat } from '../../hooks/useChat'
```

在其后追加：
```typescript
import ExplodedViewPanel from '../assembly/ExplodedViewPanel'
```

找到：
```typescript
  const { messages, streamingText, sources, imageUrls, loading, currentStage, sendMessage, clearMessages } = useChat()
```

替换为：
```typescript
  const { messages, streamingText, sources, imageUrls, figureUrls, loading, currentStage, sendMessage, clearMessages } = useChat()
```

在消息气泡渲染区找到 assistant 消息渲染的地方（包含 `ReactMarkdown` 的代码块），在 `assistant` 最后一条消息渲染后、且 `mode === 'assembly'` 时渲染面板。

找到：
```typescript
              {msg.role === 'assistant' && (
```

在 assistant 气泡的 `</div>` 结束标签之后，**最后一条 assistant 消息**处追加（找到消息列表渲染的循环结束处，在 `streamingText` 流式渲染块下方）：

找到 RAG 模式图片展示块（约在 `{/* 图片展示（仅 RAG 模式，无侧边栏时） */}` 注释下方）：

```typescript
          {/* 图片展示（仅 RAG 模式，无侧边栏时） */}
          {mode === 'rag' && !streamingText && !hasSources && messages.at(-1)?.role === 'assistant' && imageUrls.length > 0 && (
```

在该整个图片展示块的 `</div>` 结束标签之后（即 `<div ref={bottomRef} />` 之前）追加：

```typescript
          {/* 装配模式：爆炸图面板，跟随最新回答 */}
          {mode === 'assembly' && !loading && !streamingText && figureUrls.length > 0 && (
            <ExplodedViewPanel figures={figureUrls} />
          )}
```

- [ ] **Step 5: 启动前端，手动验证**

```bash
cd /c/xjp/代码/rag-demo
# 启动后端
PYTHONUTF8=1 "C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" -m uvicorn backend.main:app --reload &
# 启动前端
cd frontend && npm run dev
```

打开 `http://localhost:5173`，切换到「装配问答」模式，提问"压气机转子装配方案"。若 Neo4j 中已有 ExplodedView 节点，回答下方应出现爆炸图折叠区。

- [ ] **Step 6: 提交**

```bash
cd /c/xjp/代码/rag-demo
git add frontend/src/types/index.ts \
        frontend/src/hooks/useChat.ts \
        frontend/src/components/assembly/ExplodedViewPanel.tsx \
        frontend/src/components/shared/UnifiedChat.tsx
git commit -m "feat(figures): frontend ExplodedViewPanel + useChat figureUrls + UnifiedChat integration"
```

---

## 验收标准

1. **Stage 1 BOM 处理 PDF 时**：`storage/images/kg_figures/bom_fig_*.png` 文件被创建
2. **Stage 2 Manual 处理 PDF 时**：`storage/images/kg_figures/manual_fig_*.png` 文件被创建
3. **Neo4j 在线时**：可查询 `MATCH (p)-[:SHOWN_IN]->(f:ExplodedView) RETURN p,f LIMIT 5`
4. **装配问答时**：SSE done 帧包含 `figure_urls` 字段（即使 Neo4j 无数据也返回空数组）
5. **前端装配模式**：回答下方出现折叠爆炸图区，点击可全屏查看
6. **所有测试通过**：`pytest tests/kg/ -v` 全绿
