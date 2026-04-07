"""
backend/routers/kg_stages.py — 知识图谱四阶段构建端点

设计原则：
- 每阶段独立，不走LangGraph，直接调用现有节点函数
- 每阶段结果写 storage/kg_stages/*.json（中间产物，人工可检查）
- 保留Neo4j写入（不可用时只写JSON并告知）
"""

import os
import tempfile
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.responses import JSONResponse

from backend.deps import get_state
from backend.state import AppState
from backend.sse import stage_gen_to_sse
from backend.kg_storage import (
    write_stage, read_stage, stage_exists,
    get_all_stages_status, check_prereq, STAGE_FILES,
)

router = APIRouter()


# ─────────────────────────────────────────────
# 内部辅助：BOM DataFrame JSON → 实体 + 三元组
# ─────────────────────────────────────────────

def _bom_df_to_entities_and_triples(df_json: str):
    import pandas as pd
    df = pd.read_json(df_json, orient="records")
    entities = []
    triples = []
    id_to_name = {}
    for _, row in df.iterrows():
        pid = str(row.get("part_id", "")).strip()
        name = str(row.get("part_name", "")).strip()
        if pid and name:
            id_to_name[pid] = name
    for _, row in df.iterrows():
        pid = str(row.get("part_id", "")).strip()
        name = str(row.get("part_name", "")).strip()
        if not name:
            continue
        # 判断类型（有子零件→Assembly，否则→Part）
        etype = "Assembly" if str(row.get("category", "")).lower() in ("assembly", "") else "Part"
        entities.append({
            "id": pid or name,
            "type": etype,
            "name": name,
            "part_number": pid,
            "material": str(row.get("material", "")).strip(),
            "quantity": row.get("qty") or row.get("quantity", 1),
        })
        parent_id = str(row.get("parent_id", "")).strip()
        if parent_id and parent_id in id_to_name:
            triples.append({
                "head": name, "relation": "isPartOf",
                "tail": id_to_name[parent_id],
                "confidence": 1.0, "source": "BOM",
                "head_type": etype, "tail_type": "Assembly",
            })
        elif not parent_id:
            triples.append({
                "head": name, "relation": "isPartOf",
                "tail": "ROOT", "confidence": 1.0,
                "source": "BOM", "head_type": etype, "tail_type": "ROOT",
            })
    return entities, triples


# ─────────────────────────────────────────────
# 内部辅助：扫描件 PDF → deepdoc OCR 文本
# ─────────────────────────────────────────────

def _extract_pdf_via_deepdoc(file_path: str, state: AppState) -> str:
    """
    用 deepdoc OCR 提取扫描件 PDF 的文本内容。
    优先使用 state.deepdoc_engine，回退到 pdfplumber（仅文本层）。
    返回按 [Page N] 分组的文本字符串，供 _split_for_llm 正确分段。
    """
    if hasattr(state, "deepdoc_engine") and state.deepdoc_engine:
        try:
            result = state.deepdoc_engine.parse_pdf(file_path)
            # 按页分组，加 [Page N] 标记让 _split_for_llm 能分段
            from collections import defaultdict
            pages: dict = defaultdict(list)
            for box in result.get("boxes", []):
                text = (box.get("text") or "").strip()
                if text:
                    page_num = box.get("page_number", 1)
                    pages[page_num].append(text)
            parts = []
            for page_num in sorted(pages.keys()):
                parts.append(f"[Page {page_num}]\n" + "\n".join(pages[page_num]))
            if parts:
                return "\n\n".join(parts)
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"deepdoc OCR 失败，降级 pdfplumber: {e}")

    # 最终降级：再试一次 pdfplumber（含 OCR 兜底文字）
    try:
        import pdfplumber
        parts = []
        with pdfplumber.open(file_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                if text.strip():
                    parts.append(f"[Page {i + 1}]\n{text}")
        return "\n\n".join(parts)
    except Exception:
        return ""


# ─────────────────────────────────────────────
# 内部辅助：OCR 文本 → BOM 记录（宽松 Prompt）
# ─────────────────────────────────────────────

_OCR_BOM_PROMPT = """你是一个BOM（物料清单）数据提取专家。以下是从扫描件PDF中OCR识别出的文本，可能包含零件编号、零件名称、数量、父子关系等信息。

请尽最大努力提取所有零件信息，输出JSON数组。每条记录包含以下字段：
- part_id: 零件编号（如有，否则用序号如 P001、P002）
- part_name: 零件名称（中文或英文，如看到的）
- parent_id: 父零件编号（如能判断父子关系，否则留空字符串""）
- qty: 数量（整数，默认1）
- unit: 单位（默认"件"）
- material: 材料（如有，否则留空""）
- category: "Assembly"（组件/含子零件）或"Part"（零件）或"Standard"（标准件），默认"Part"

重要：
- 即使文本凌乱，也要尽量提取所有能识别的零件行
- 不需要 level_code 字段
- 只输出JSON数组，不要解释

待处理的OCR文本：
{content}"""


def _llm_extract_bom_from_ocr(ocr_text: str, state: AppState) -> list:
    """用宽松 Prompt 从 OCR 文本中提取 BOM 记录，返回 records 列表。"""
    from backend.routers.bom import _split_for_llm, _parse_llm_json
    import logging
    logger = logging.getLogger(__name__)

    chunks = _split_for_llm(ocr_text, max_chars=12000)
    all_records = []
    for i, chunk in enumerate(chunks):
        prompt = _OCR_BOM_PROMPT.format(content=chunk)
        try:
            resp = state.llm_client.chat.completions.create(
                model=None,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
            )
            raw_json = resp.choices[0].message.content
            records = _parse_llm_json(raw_json)
            logger.info(f"[Stage1 OCR LLM] 第 {i+1}/{len(chunks)} 段：{len(records)} 条")
            all_records.extend(records)
        except Exception as e:
            logger.warning(f"[Stage1 OCR LLM] 第 {i+1} 段失败：{e}")
    return all_records


# ─────────────────────────────────────────────
# 内部辅助：写 JSON + 尝试 Neo4j（阶段1收尾）
# ─────────────────────────────────────────────

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


# ─────────────────────────────────────────────
# 内部生成器：阶段1 BOM 处理
# ─────────────────────────────────────────────

def _stage1_bom_gen(tmp_path: str, ext: str, clear_first: bool,
                    state: AppState, neo4j_cfg: dict):
    yield {"type": "log", "message": "[Stage1] 开始处理 BOM"}

    from backend.pipelines.nodes_bom import make_bom_nodes
    nodes = make_bom_nodes(state, neo4j_cfg)

    pipeline_state = {
        "file_path": tmp_path,
        "file_ext":  ext,
        "clear_first": clear_first,
    }

    # 根据扩展名选择入口节点
    if ext in ("xlsx", "xls", "csv"):
        yield {"type": "log", "message": f"[Stage1] 直接读取表格文件（{ext.upper()}）"}
        result = nodes["load_table"](pipeline_state)
    elif ext in ("pdf", "docx"):
        yield {"type": "log", "message": f"[Stage1] 提取 {ext.upper()} 中的表格…"}
        result = nodes["extract_tables"](pipeline_state)
        # 扫描件 PDF：pdfplumber 无法提取文字，降级走 deepdoc OCR + 宽松 Prompt
        if "error" in result and ext == "pdf" and "未找到" in result["error"]:
            yield {"type": "log", "message": "[Stage1] pdfplumber 未提取到内容，尝试 deepdoc OCR…"}
            ocr_text = _extract_pdf_via_deepdoc(tmp_path, state)
            if not ocr_text.strip():
                yield {"type": "error", "message": "PDF 扫描件 OCR 也未提取到文本，请确认文件可读"}
                return
            yield {"type": "log", "message": f"[Stage1] deepdoc OCR 提取完成（{len(ocr_text)} 字符），调用 LLM 识别零件…"}
            records = _llm_extract_bom_from_ocr(ocr_text, state)
            if not records:
                yield {"type": "error", "message": "LLM 未能从扫描件中识别出零件信息，请确认 PDF 包含 BOM 表格"}
                return
            yield {"type": "log", "message": f"[Stage1] LLM 识别到 {len(records)} 条零件记录"}
            # 将 records 转为 df_json 注入 pipeline_state，跳过 llm_to_csv
            import pandas as pd, json as _json
            df = pd.DataFrame(records)
            pipeline_state["bom_dataframe_json"] = df.to_json(orient="records", force_ascii=False)
            result = {"bom_dataframe_json": pipeline_state["bom_dataframe_json"], "log_messages": []}
            pipeline_state.update(result)
            # 跳过后续的 llm_to_csv 和 validate_bom_df，直接到三元组生成
            df_json = pipeline_state["bom_dataframe_json"]
            entities, triples = _bom_df_to_entities_and_triples(df_json)
            yield {"type": "log", "message": f"[Stage1] 生成 {len(triples)} 条三元组，{len(entities)} 个实体"}
            _finalize_stage1(tmp_path, entities, triples, pipeline_state, nodes, neo4j_cfg)
            yield {
                "type": "result",
                "triples_count": len(triples),
                "entities_count": len(entities),
                "stats": {"entities_count": len(entities), "triples_count": len(triples)},
                "output_file": STAGE_FILES["bom"],
            }
            yield {"type": "done", "success": True}
            return
        elif "error" in result:
            yield {"type": "error", "message": result["error"]}
            return
        pipeline_state.update(result)
        yield {"type": "log", "message": "[Stage1] 调用 LLM 转换为标准 BOM…"}
        result = nodes["llm_to_csv"](pipeline_state)
    else:
        yield {"type": "error", "message": f"不支持的文件格式：{ext}"}
        return

    if "error" in result:
        yield {"type": "error", "message": result["error"]}
        return
    pipeline_state.update(result)

    # 日志透传
    for msg in result.get("log_messages", []):
        yield {"type": "log", "message": msg}

    # 尝试标准字段清洗（仅当含 level_code 字段时执行，否则跳过以兼容不同 BOM 格式）
    import json as _json
    _df_json_raw = pipeline_state.get("bom_dataframe_json", "")
    _sample_cols = list((_json.loads(_df_json_raw) or [{}])[0].keys()) if _df_json_raw else []
    if "level_code" in _sample_cols:
        yield {"type": "log", "message": "[Stage1] 清洗与校验数据…"}
        result = nodes["validate_bom_df"](pipeline_state)
        if "error" in result:
            yield {"type": "error", "message": result["error"]}
            return
        pipeline_state.update(result)
        for msg in result.get("log_messages", []):
            yield {"type": "log", "message": msg}
    else:
        yield {"type": "log", "message": "[Stage1] 跳过标准字段校验（BOM 格式兼容模式）"}

    # 转换为三元组
    df_json = pipeline_state.get("bom_dataframe_json", "")
    entities, triples = _bom_df_to_entities_and_triples(df_json)
    yield {"type": "log", "message": f"[Stage1] 生成 {len(triples)} 条三元组，{len(entities)} 个实体"}

    _finalize_stage1(tmp_path, entities, triples, pipeline_state, nodes, neo4j_cfg)
    yield {
        "type": "result",
        "triples_count": len(triples),
        "entities_count": len(entities),
        "stats": {"entities_count": len(entities), "triples_count": len(triples)},
        "output_file": STAGE_FILES["bom"],
    }
    yield {"type": "done", "success": True}


# ─────────────────────────────────────────────
# POST /kg/stage1/bom
# ─────────────────────────────────────────────

@router.post("/stage1/bom", summary="阶段1：BOM 入库（SSE）")
async def stage1_bom(
    request: Request,
    file: UploadFile = File(...),
    clear_first: bool = Form(False),
    state: AppState = Depends(get_state),
):
    """
    上传 BOM 文件（xlsx/xls/csv/pdf/docx），解析为实体+三元组并写 JSON。
    响应为 SSE 流。
    """
    neo4j_cfg = request.app.state.neo4j_cfg

    # 保存上传文件到临时目录
    ext = (file.filename or "").rsplit(".", 1)[-1].lower()
    content = await file.read()

    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    def cleanup_and_gen():
        try:
            yield from _stage1_bom_gen(tmp_path, ext, clear_first, state, neo4j_cfg)
        finally:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass

    return stage_gen_to_sse(cleanup_and_gen())


# ─────────────────────────────────────────────
# 内部辅助：PDF → 文本 chunks
# ─────────────────────────────────────────────

def _extract_pdf_chunks(file_path: str, state: AppState):
    """
    从 PDF 提取文本 chunks。

    优先走 DeepDocEngine.parse_pdf()（若 app_state.deepdoc_engine 存在），
    否则 fallback 到 pdfplumber 逐页提取。

    返回: (chunks: list[dict], method: str)
      chunks 格式: [{"text": str, "chunk_id": str, "ata_section": str}]
    """
    if hasattr(state, "deepdoc_engine") and state.deepdoc_engine:
        try:
            result = state.deepdoc_engine.parse_pdf(file_path)
            boxes = result.get("boxes", [])
            chunks = []
            for box in boxes:
                text = (box.get("text") or "").strip()
                if not text:
                    continue
                page_num = box.get("page_number", 0)
                chunks.append({
                    "text": text,
                    "chunk_id": f"p{page_num}_box{len(chunks)}",
                    "ata_section": f"Page {page_num}",
                })
            return chunks, "deepdoc"
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"deepdoc 解析失败，降级 pdfplumber: {e}")

    import pdfplumber
    chunks = []
    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            if text.strip():
                chunks.append({
                    "text": text,
                    "chunk_id": f"p{i}",
                    "ata_section": f"Page {i + 1}",
                })
    return chunks, "pdfplumber"


# ─────────────────────────────────────────────
# 内部辅助：kg_triples chunk格式 → 平铺三元组
# ─────────────────────────────────────────────

def _kg_chunks_to_flat_triples(kg_triples: list) -> list:
    """将 extract_kg_triples 返回的 chunk 格式三元组展开为平铺格式。"""
    flat = []
    for chunk in kg_triples:
        ent_map = {e["id"]: e.get("text", "") for e in chunk.get("entities", [])}
        ent_type_map = {e["id"]: e.get("type", "") for e in chunk.get("entities", [])}
        for rel in chunk.get("relations", []):
            head_id = rel.get("head") or rel.get("source_id", "")
            tail_id = rel.get("tail") or rel.get("target_id", "")
            head_text = ent_map.get(head_id, "")
            tail_text = ent_map.get(tail_id, "")
            if head_text and tail_text:
                flat.append({
                    "head": head_text,
                    "relation": rel["type"],
                    "tail": tail_text,
                    "confidence": round(rel.get("weight", 5) / 10.0, 2),
                    "source": "Manual",
                    "head_type": ent_type_map.get(head_id, ""),
                    "tail_type": ent_type_map.get(tail_id, ""),
                })
    return flat


# ─────────────────────────────────────────────
# 内部辅助：Neo4j 写入（阶段二）
# ─────────────────────────────────────────────

def _write_manual_to_neo4j(flat_triples: list, neo4j_cfg: dict):
    """
    将手册阶段三元组写入 Neo4j。

    对 Procedure/Tool/Specification/Interface 实体：MERGE by kg_name。
    对关系：MERGE by (head.kg_name, type, tail.kg_name)。
    失败时只记录日志，不抛异常。

    Returns: (success: bool, message: str)
    """
    import logging
    logger = logging.getLogger(__name__)

    try:
        from neo4j import GraphDatabase
    except ImportError:
        return False, "neo4j 包未安装"

    try:
        driver = GraphDatabase.driver(
            neo4j_cfg.get("uri", "bolt://localhost:7687"),
            auth=(neo4j_cfg.get("user", "neo4j"), neo4j_cfg.get("password", "neo4j")),
        )
    except Exception as e:
        return False, f"连接失败: {e}"

    # 收集所有实体（按 kg_name 去重）
    entity_map: dict = {}
    for t in flat_triples:
        for key, etype in ((t["head"], t["head_type"]), (t["tail"], t["tail_type"])):
            if key and key not in entity_map:
                entity_map[key] = etype or "Part"

    kg_entity_types = {"Procedure", "Tool", "Specification", "Interface", "Part", "Assembly"}
    nodes_to_write = [
        {"kg_name": name, "label": etype if etype in kg_entity_types else "Part"}
        for name, etype in entity_map.items()
    ]

    try:
        with driver.session() as session:
            # 写节点（按标签分组，Cypher 不支持动态标签参数）
            from collections import defaultdict
            by_label = defaultdict(list)
            for n in nodes_to_write:
                by_label[n["label"]].append(n["kg_name"])
            for label, names in by_label.items():
                try:
                    session.run(
                        f"UNWIND $names AS name MERGE (n:{label} {{kg_name: name}})",
                        names=names,
                    )
                except Exception as e:
                    logger.warning(f"[Stage2] Neo4j 写节点({label})失败: {e}")

            # 写关系
            merged_count = 0
            for t in flat_triples:
                rel_type = t["relation"]
                try:
                    session.run(
                        f"""
                        MATCH (a {{kg_name: $head}})
                        MATCH (b {{kg_name: $tail}})
                        MERGE (a)-[r:{rel_type}]->(b)
                        SET r.source = 'Manual', r.confidence = $conf
                        """,
                        head=t["head"], tail=t["tail"], conf=t["confidence"],
                    )
                    merged_count += 1
                except Exception:
                    pass

            driver.close()
            return True, f"Neo4j 写入完成：{len(nodes_to_write)} 节点，{merged_count} 关系"
    except Exception as e:
        try:
            driver.close()
        except Exception:
            pass
        return False, f"Neo4j 写入失败: {e}"


# ─────────────────────────────────────────────
# 内部生成器：阶段2 手册 PDF 处理
# ─────────────────────────────────────────────

def _stage2_manual_gen(tmp_path: str, filename: str, state: AppState, neo4j_cfg: dict):
    yield {"type": "log", "message": "[Stage2] 开始处理手册"}

    # 1. PDF 文本提取
    try:
        chunks, method = _extract_pdf_chunks(tmp_path, state)
    except Exception as e:
        yield {"type": "error", "message": f"PDF 提取失败：{e}"}
        return
    yield {"type": "log", "message": f"[Stage2] {method} 提取完成，共 {len(chunks)} 段"}

    if not chunks:
        yield {"type": "error", "message": "[Stage2] PDF 无可提取文本，请检查是否为扫描件"}
        return

    # 2. LLM KG 提取（复用 nodes_kg.py，含两轮 gleaning）
    from backend.pipelines.nodes_kg import make_kg_nodes
    nodes = make_kg_nodes(state, neo4j_cfg)

    # extract_kg_triples 使用 state["manual_chunks"]
    pipeline_state = {"manual_chunks": chunks}
    try:
        result = nodes["extract_kg_triples"](pipeline_state)
    except Exception as e:
        yield {"type": "error", "message": f"KG 提取节点异常：{e}"}
        return

    for msg in result.get("log_messages", []):
        yield {"type": "log", "message": msg}

    kg_triples = result.get("kg_triples", [])
    yield {"type": "log", "message": f"[Stage2] 生成 {len(kg_triples)} 个三元组 chunk"}

    # 3. 展开为平铺格式
    flat_triples = _kg_chunks_to_flat_triples(kg_triples)
    yield {"type": "log", "message": f"[Stage2] 平铺后共 {len(flat_triples)} 条三元组"}

    if not flat_triples:
        yield {"type": "log", "message": "[Stage2] ⚠ 未提取到三元组（文本可能不含装配工序相关内容）"}

    # 4. 简单实体对齐（participatesIn 关系标注 bom_part_id）
    bom_data = read_stage("bom")
    bom_entities = []
    if bom_data:
        bom_entities = bom_data.get("entities", [])
    if bom_entities:
        bom_name_map = {e.get("name", "").lower(): e.get("id", "") for e in bom_entities}
        matched = 0
        for t in flat_triples:
            if t["relation"] == "participatesIn":
                head_lower = t["head"].lower()
                for bom_name, bom_id in bom_name_map.items():
                    if bom_name and (bom_name in head_lower or head_lower in bom_name):
                        t["bom_part_id"] = bom_id
                        matched += 1
                        break
        if matched:
            yield {"type": "log", "message": f"[Stage2] BOM 实体对齐：{matched} 条 participatesIn 关系命中"}

    # 5. 统计
    from collections import Counter
    total_entities = len({t["head"] for t in flat_triples} | {t["tail"] for t in flat_triples})
    relations_breakdown = dict(Counter(t["relation"] for t in flat_triples))

    # 6. 写中间产物 JSON
    output = {
        "stage": "manual",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_file": filename,
        "triples": flat_triples,
        "stats": {
            "total_triples": len(flat_triples),
            "entities_count": total_entities,
            "relations_breakdown": relations_breakdown,
        },
    }
    write_stage("manual", output)
    yield {"type": "log", "message": f"[Stage2] 已写入：{STAGE_FILES['manual']}"}

    # 7. 尝试写 Neo4j
    yield {"type": "log", "message": "[Stage2] 尝试写入 Neo4j…"}
    neo4j_ok, neo4j_msg = _write_manual_to_neo4j(flat_triples, neo4j_cfg)
    if neo4j_ok:
        yield {"type": "log", "message": f"[Stage2] {neo4j_msg}"}
    else:
        yield {"type": "log", "message": f"[Stage2] Neo4j 不可用（{neo4j_msg}），仅保存 JSON"}

    yield {
        "type": "result",
        "triples_count": len(flat_triples),
        "entities_count": total_entities,
        "stats": output["stats"],
        "output_file": STAGE_FILES["manual"],
    }
    yield {"type": "done", "success": True}


# ─────────────────────────────────────────────
# POST /kg/stage2/manual
# ─────────────────────────────────────────────

@router.post("/stage2/manual", summary="阶段2：手册PDF → 知识三元组（SSE）")
async def stage2_manual(
    request: Request,
    file: UploadFile = File(...),
    state: AppState = Depends(get_state),
):
    """
    上传手册 PDF，使用 LLM 提取 KG 三元组并写 JSON。
    响应为 SSE 流。
    """
    neo4j_cfg = request.app.state.neo4j_cfg

    ext = (file.filename or "manual.pdf").rsplit(".", 1)[-1].lower()
    if ext != "pdf":
        from fastapi.responses import JSONResponse as _JR
        return _JR(status_code=400, content={"error": "仅支持 PDF 文件"})

    content = await file.read()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    filename = file.filename or "manual.pdf"

    def cleanup_and_gen():
        try:
            yield from _stage2_manual_gen(tmp_path, filename, state, neo4j_cfg)
        finally:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass

    return stage_gen_to_sse(cleanup_and_gen())


# ─────────────────────────────────────────────
# 内部辅助：CAD 数据 → 扁平三元组
# ─────────────────────────────────────────────

def _cad_data_to_flat_triples(assembly_tree, constraints, adjacency):
    triples = []

    # 装配树 → isPartOf
    def _traverse(node, parent_name=None):
        for child_name, subtree in node.items():
            if parent_name:
                triples.append({
                    "head": child_name, "relation": "isPartOf",
                    "tail": parent_name, "confidence": 1.0, "source": "CAD",
                })
            _traverse(subtree, child_name)
    _traverse(assembly_tree)

    # 配合约束 → matesWith + hasInterface + constrainedBy
    for c in constraints:
        if c.get("part_a") and c.get("part_b"):
            triples.append({
                "head": c["part_a"], "relation": "matesWith",
                "tail": c["part_b"], "confidence": 0.9, "source": "CAD",
            })
        if c.get("interface") and c.get("part_a"):
            triples.append({
                "head": c["part_a"], "relation": "hasInterface",
                "tail": c["interface"], "confidence": 0.9, "source": "CAD",
            })
        if c.get("constraint_type") and c.get("interface"):
            triples.append({
                "head": c["interface"], "relation": "constrainedBy",
                "tail": c["constraint_type"], "confidence": 0.9, "source": "CAD",
            })

    # 空间邻接 → adjacentTo
    for a in adjacency:
        if a.get("part_a") and a.get("part_b"):
            triples.append({
                "head": a["part_a"], "relation": "adjacentTo",
                "tail": a["part_b"], "confidence": 0.7, "source": "CAD",
            })

    return triples


# ─────────────────────────────────────────────
# 内部辅助：P/R/F1 计算
# ─────────────────────────────────────────────

import re as _re


def _normalize(text: str) -> str:
    """归一化：小写、去标点、去多余空格"""
    t = text.lower().strip()
    t = _re.sub(r"[^\w\s]", " ", t)
    t = _re.sub(r"\s+", " ", t).strip()
    return t


def _compute_prf1(golden, predicted):
    g_set = {(_normalize(t["head"]), t["relation"], _normalize(t["tail"])) for t in golden}
    p_set = {(_normalize(t["head"]), t["relation"], _normalize(t["tail"])) for t in predicted}

    tp = len(g_set & p_set)
    prec = tp / len(p_set) if p_set else 0.0
    rec  = tp / len(g_set) if g_set else 0.0
    f1   = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0

    rel_types = set(t["relation"] for t in golden)
    per_relation = {}
    for rel in rel_types:
        g_rel = {(t[0], t[2]) for t in g_set if t[1] == rel}
        p_rel = {(t[0], t[2]) for t in p_set if t[1] == rel}
        tp_r  = len(g_rel & p_rel)
        pr_r  = tp_r / len(p_rel) if p_rel else 0.0
        re_r  = tp_r / len(g_rel) if g_rel else 0.0
        f1_r  = 2 * pr_r * re_r / (pr_r + re_r) if (pr_r + re_r) else 0.0
        per_relation[rel] = {
            "precision": round(pr_r, 4), "recall": round(re_r, 4), "f1": round(f1_r, 4),
            "golden_count": len(g_rel), "predicted_count": len(p_rel),
        }

    comparison = []
    for t in golden:
        key = (_normalize(t["head"]), t["relation"], _normalize(t["tail"]))
        comparison.append({**t, "matched": key in p_set})

    return {
        "precision": round(prec, 4), "recall": round(rec, 4), "f1": round(f1, 4),
        "tp": tp, "fp": len(p_set) - tp, "fn": len(g_set) - tp,
        "per_relation": per_relation,
        "comparison": comparison,
    }


# ─────────────────────────────────────────────
# 内部生成器：阶段3 CAD 处理
# ─────────────────────────────────────────────

def _stage3_cad_gen(tmp_path: str, ext: str, state: AppState, neo4j_cfg: dict):
    import difflib

    yield {"type": "log", "message": "[Stage3] 开始处理 CAD 文件"}

    from backend.pipelines.nodes_cad import make_cad_nodes
    nodes = make_cad_nodes(state, neo4j_cfg)

    result = nodes["parse_cad_step"]({"file_path": tmp_path, "file_ext": ext})
    if "error" in result:
        yield {"type": "error", "message": result["error"]}
        return

    for msg in result.get("log_messages", []):
        yield {"type": "log", "message": msg}

    assembly_tree = result.get("cad_assembly_tree", {})
    constraints   = result.get("cad_constraints", [])
    adjacency     = result.get("cad_adjacency", [])

    flat_triples = _cad_data_to_flat_triples(assembly_tree, constraints, adjacency)
    yield {"type": "log", "message": f"[Stage3] 生成 {len(flat_triples)} 条扁平三元组"}

    # 简单 BOM 对齐（模糊匹配）
    bom_part_names = []
    if stage_exists("bom"):
        bom_data = read_stage("bom")
        bom_part_names = [e.get("name", "") for e in (bom_data or {}).get("entities", []) if e.get("name")]

    if bom_part_names:
        matched_count = 0
        for triple in flat_triples:
            for field in ("head", "tail"):
                val = triple.get(field, "")
                matches = difflib.get_close_matches(val, bom_part_names, n=1, cutoff=0.8)
                if matches:
                    triple[f"{field}_bom_match"] = matches[0]
                    matched_count += 1
        yield {"type": "log", "message": f"[Stage3] BOM 对齐命中 {matched_count} 个实体字段"}

    # 写中间产物 JSON
    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_file":  os.path.basename(tmp_path),
        "triples":      flat_triples,
        "stats": {
            "triples_count": len(flat_triples),
            "assembly_nodes": sum(1 for t in flat_triples if t["relation"] == "isPartOf"),
            "constraints":    sum(1 for t in flat_triples if t["relation"] in ("matesWith", "hasInterface", "constrainedBy")),
            "adjacency":      sum(1 for t in flat_triples if t["relation"] == "adjacentTo"),
        },
    }
    write_stage("cad", output)
    yield {
        "type": "result",
        "triples_count": len(flat_triples),
        "stats": output["stats"],
        "output_file": STAGE_FILES["cad"],
    }
    yield {"type": "log", "message": f"[Stage3] 已写入：{STAGE_FILES['cad']}"}

    # 尝试写 Neo4j（失败不中断）
    try:
        yield {"type": "log", "message": "[Stage3] 尝试写入 Neo4j…"}
        neo4j_result = nodes["cad_to_kg_triples"]({
            "cad_assembly_tree": assembly_tree,
            "cad_constraints":   constraints,
            "cad_adjacency":     adjacency,
        })
        for msg in neo4j_result.get("log_messages", []):
            yield {"type": "log", "message": msg}
    except Exception as e:
        yield {"type": "log", "message": f"[Stage3] Neo4j 写入跳过：{e}"}

    yield {"type": "done", "success": True}


# ─────────────────────────────────────────────
# POST /kg/stage3/cad
# ─────────────────────────────────────────────

@router.post("/stage3/cad", summary="阶段3：CAD 模型入库（SSE）")
async def stage3_cad(
    request: Request,
    file: UploadFile = File(...),
    state: AppState = Depends(get_state),
):
    """
    上传 STEP/STP 文件，提取装配树/配合约束/空间邻接并生成三元组。
    响应为 SSE 流。
    """
    neo4j_cfg = request.app.state.neo4j_cfg

    ext = (file.filename or "").rsplit(".", 1)[-1].lower()
    if ext not in ("step", "stp"):
        return JSONResponse(
            status_code=400,
            content={"error": f"不支持的文件格式：{ext}，仅支持 STEP/STP"},
        )

    content = await file.read()
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    def cleanup_and_gen():
        try:
            yield from _stage3_cad_gen(tmp_path, ext, state, neo4j_cfg)
        finally:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass

    return stage_gen_to_sse(cleanup_and_gen())


# ─────────────────────────────────────────────
# POST /kg/stage4/validate
# ─────────────────────────────────────────────

@router.post("/stage4/validate", summary="阶段4：Golden 验证（同步 JSON）")
def kg_stage4_validate(state: AppState = Depends(get_state)):
    """
    读取已有阶段中间产物，与 golden_triples.json 计算 P/R/F1。
    无需上传文件，同步返回 JSON 报告。
    """
    import json as _json
    from backend.kg_storage import GOLDEN_PATH

    if not os.path.exists(GOLDEN_PATH):
        return JSONResponse(
            status_code=404,
            content={"error": f"golden_triples.json 不存在，路径：{GOLDEN_PATH}"},
        )

    golden = _json.loads(open(GOLDEN_PATH, encoding="utf-8").read())

    all_predicted = []
    stages_included = []
    for stage in ("bom", "manual", "cad"):
        if stage_exists(stage):
            data = read_stage(stage)
            all_predicted.extend((data or {}).get("triples", []))
            stages_included.append(stage)

    report = _compute_prf1(golden, all_predicted)
    report["stages_included"]  = stages_included
    report["golden_count"]     = len(golden)
    report["predicted_count"]  = len(all_predicted)
    return JSONResponse(report)


# ─────────────────────────────────────────────
# GET /kg/stages/status
# ─────────────────────────────────────────────

@router.get("/stages/status", summary="各阶段状态")
def stages_status():
    """返回三个阶段（bom/manual/cad）的文件存在状态和生成时间。"""
    return get_all_stages_status()


# ─────────────────────────────────────────────
# GET /kg/stages/{stage}/preview
# ─────────────────────────────────────────────

@router.get("/stages/{stage}/preview", summary="预览阶段三元组")
def stages_preview(stage: str, offset: int = 0, limit: int = 50):
    """分页返回指定阶段的三元组列表。"""
    valid_stages = ("bom", "manual", "cad")
    if stage not in valid_stages:
        return JSONResponse(
            status_code=400,
            content={"error": f"未知阶段：{stage}，有效值：{valid_stages}"},
        )
    data = read_stage(stage)
    if data is None:
        return JSONResponse(
            status_code=404,
            content={"error": f"阶段 {stage} 尚未生成，请先上传文件"},
        )
    triples = data.get("triples", [])
    return {
        "stage": stage,
        "total": len(triples),
        "offset": offset,
        "limit": limit,
        "triples": triples[offset: offset + limit],
    }
