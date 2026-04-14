"""
backend/routers/kg_stages.py — 知识图谱四阶段构建端点

设计原则：
- 每阶段独立，不走LangGraph，直接调用现有节点函数
- 每阶段结果写 storage/kg_stages/*.json（中间产物，人工可检查）
- 保留Neo4j写入（不可用时只写JSON并告知）
"""

import os
import re as _re
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

_OCR_NOISE_RULES = [
    (_re.compile(r'COMP0NENT'),          'COMPONENT'),
    (_re.compile(r'C0MPONENT'),          'COMPONENT'),
    (_re.compile(r'\b0F\b'),             'OF'),
    (_re.compile(r'\b0N\b'),             'ON'),
    (_re.compile(r'\b0VS\b'),            'OVS'),
    (_re.compile(r'\bN0\b(?=\.)'),       'NO'),   # NO.1 类型
]


def _clean_ocr_noise(text: str) -> str:
    """净化 OCR 常见噪声：数字0误识别为字母O。保留小数点中的数字0不变。"""
    for pattern, replacement in _OCR_NOISE_RULES:
        text = pattern.sub(replacement, text)
    return text


def _parse_indent_level(nomenclature: str) -> tuple:
    """从 IPC 零件名中解析点号缩进层级。
    返回 (层级深度 int, 清理后的名称 str)
    无点=0（顶层装配），.=1（直属子件），..=2（孙子件），以此类推。
    """
    name = str(nomenclature).lstrip()
    level = 0
    while name.startswith("."):
        level += 1
        name = name[1:]
    return level, name.strip()


def _bom_df_to_entities_and_triples(df_json: str):
    import pandas as pd
    df = pd.read_json(df_json, orient="records")
    entities = []
    triples = []

    # 构建 part_id → head_label 映射（用于 parent_id fallback 路径）
    id_to_head: dict = {}
    for _, row in df.iterrows():
        pid  = str(row.get("part_id", "")).strip()
        name = str(row.get("part_name", "")).strip()
        if pid and name:
            id_to_head[pid] = f"{pid} {name}"

    # 层级栈：[(level, head_label)]，用于点号前缀路径
    parent_stack: list = []  # [(int, str)]

    for _, row in df.iterrows():
        pid  = str(row.get("part_id", "")).strip()
        name = _clean_ocr_noise(str(row.get("part_name", "")).strip())
        if not name:
            continue

        # head 使用 part_number + name 组合，避免同名不同号合并
        head_label = f"{pid} {name}" if pid else name

        # 判断类型
        etype = "Assembly" if str(row.get("category", "")).strip().lower() == "assembly" else "Part"

        entities.append({
            "id":          pid or name,
            "type":        etype,
            "name":        name,
            "part_number": pid,
            "material":    str(row.get("material", "")).strip(),
            "quantity":    row.get("qty") or row.get("quantity", 1),
        })

        # ── 路径1：nomenclature 含点号前缀 → 用栈结构推断父节点 ──────────
        nomenclature = _clean_ocr_noise(str(row.get("nomenclature", "")).strip())
        fig_item     = str(row.get("fig_item", "")).strip()
        if nomenclature:
            # 互换件优先检测：fig_item 带 dash（-1A/-1B）且含 INTRCHG
            # 互换件无点号前缀，不参与层级栈，直接指向栈顶（与被替代件共享父节点）
            if fig_item.startswith("-") and "INTRCHG" in nomenclature.upper():
                base_label = parent_stack[-1][1] if parent_stack else "ROOT"
                triples.append({
                    "head": head_label, "relation": "interchangesWith",
                    "tail": base_label,
                    "confidence": 0.9, "source": "BOM",
                    "head_type": etype, "tail_type": "Assembly",
                })
                continue

            level, _ = _parse_indent_level(nomenclature)

            # 弹出层级 >= 当前层级的条目（找到真正的父节点）
            while parent_stack and parent_stack[-1][0] >= level:
                parent_stack.pop()

            if level == 0:
                parent_label = "ROOT"
                tail_type    = "ROOT"
            elif parent_stack:
                parent_label = parent_stack[-1][1]
                tail_type    = "Assembly"
            else:
                parent_label = "ROOT"
                tail_type    = "ROOT"

            parent_stack.append((level, head_label))

            if head_label != parent_label:
                triples.append({
                    "head": head_label, "relation": "isPartOf",
                    "tail": parent_label,
                    "confidence": 1.0, "source": "BOM",
                    "head_type": etype, "tail_type": tail_type,
                })
            continue

        # ── 路径2：无 nomenclature → fallback 到 parent_id 查表 ───────────
        parent_id = str(row.get("parent_id", "")).strip()
        if parent_id == pid:
            parent_id = ""  # 自引用保护

        if parent_id and parent_id in id_to_head:
            parent_label = id_to_head[parent_id]
            if parent_label != head_label:
                triples.append({
                    "head": head_label, "relation": "isPartOf",
                    "tail": parent_label,
                    "confidence": 1.0, "source": "BOM",
                    "head_type": etype, "tail_type": "Assembly",
                })
                continue

        # parent_id 为空或找不到 → 挂到 ROOT
        triples.append({
            "head": head_label, "relation": "isPartOf",
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

_OCR_BOM_PROMPT = """你是一个BOM（物料清单）数据提取专家。以下是从扫描件PDF中OCR识别出的文本，包含航空发动机零件清单（IPC 格式）。

请提取所有零件信息，输出JSON数组。每条记录字段：
- part_id: 零件编号（字母数字组合，如 3034344、MS9556-06；若无则用 P001、P002 等序号）
- part_name: 零件名称（去掉前缀点号后的纯名称，如 "SEAL, AIR"）
- nomenclature: 原始 NOMENCLATURE 列内容，**完整保留前缀点号**（如 ".SEAL, AIR"、"..SEAL, 0.129-0.131 IN."）
- fig_item: FIG. ITEM 列内容（如 "1"、"-1A"、"-1B"；若无则 ""）
- parent_id: 父零件的 part_id（仅当你能从缩进/编号/文档结构中确认父子关系时才填写，否则必须填 ""）
- qty: 数量（整数；从文本中找数字，找不到才默认1）
- unit: 单位（件/套/个等，默认"件"）
- material: 材料（如有，否则""）
- category: "Assembly"（组件，包含子零件）、"Part"（零件）、"Standard"（标准件如螺栓螺母），默认"Part"

【严格规则】
1. nomenclature 必须保留原文的前缀点号（IPC 规范：无点=顶层装配，.=直属子件，..=孙子件）
2. part_name 是 nomenclature 去掉前缀点号后的纯名称
3. parent_id 必须是本批文本中另一个零件的 part_id，不能填自己的 part_id
4. 若不确定父子关系，parent_id 填 "" —— 宁可留空，不要猜错
5. 顶层装配体（最高层级）的 parent_id 填 ""
6. 只输出JSON数组，不加任何说明

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
        prompt = _OCR_BOM_PROMPT.format(content=_clean_ocr_noise(chunk))
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
            # 按页号分组合并：818个小box → ~52个页级chunk，保证LLM上下文充足
            from collections import defaultdict as _defaultdict
            page_texts: dict = _defaultdict(list)
            for box in boxes:
                text = (box.get("text") or "").strip()
                if text:
                    page_num = box.get("page_number", 0)
                    page_texts[page_num].append(text)
            chunks = []
            for page_num in sorted(page_texts.keys()):
                combined_text = "\n".join(page_texts[page_num])
                if combined_text.strip():
                    chunks.append({
                        "text": combined_text,
                        "chunk_id": f"p{page_num}",
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


def _post_process_triples(triples: list) -> list:
    """后处理过滤：低置信度、噪音实体、本体约束校验。"""
    import re as _re
    _noise_pattern = _re.compile(
        r"^(figure|fig|table|tab|sb|amm|cmm|ipc)\s*[\d\-]+$", _re.IGNORECASE
    )
    filtered = []
    for t in triples:
        if t.get("confidence", 0) < 0.3:
            continue
        head, tail = t.get("head", ""), t.get("tail", "")
        if len(head) < 4 or len(tail) < 4:
            continue
        if _noise_pattern.match(head.strip()) or _noise_pattern.match(tail.strip()):
            continue
        rel = t.get("relation", "")
        head_type = t.get("head_type", "")
        tail_type = t.get("tail_type", "")
        if rel == "specifiedBy":
            if head_type not in ("Procedure", "Interface", "Part", "Assembly"):
                continue
        if rel == "precedes":
            if head_type != "Procedure" or tail_type != "Procedure":
                continue
        filtered.append(t)
    return filtered


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
            auth=(neo4j_cfg.get("user", "neo4j"),
                  neo4j_cfg.get("pass", neo4j_cfg.get("password", "neo4j"))),
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
                    ).consume()
                    merged_count += 1
                except Exception as e:
                    logger.warning(f"[Stage2] Neo4j 写关系失败({rel_type}): {e}")

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

def _align_manual_to_bom(flat_triples: list, bom_entities: list) -> int:
    """
    对所有 flat_triples 中的 Part/Assembly 实体做两级对齐：
    1. 精确子串匹配（双向，min长度>=4）
    2. SequenceMatcher 模糊匹配（阈值0.75）
    写入 head_bom_id / tail_bom_id 字段。返回命中字段总数。
    """
    from difflib import SequenceMatcher

    PART_TYPES = {"Part", "Assembly"}

    # 构建 BOM 查找索引（小写名称 → (原名, id)）
    bom_name_map: dict = {}
    for e in bom_entities:
        name = e.get("name", "")
        bid  = e.get("id", "")
        if name and bid:
            bom_name_map[name.lower()] = (name, bid)
    bom_lower_names = list(bom_name_map.keys())

    # 缓存避免重复计算
    entity_cache: dict = {}  # lower_text -> bom_id or None

    def _lookup(text: str):
        key = text.lower().strip()
        if key in entity_cache:
            return entity_cache[key]

        # 级别1a：精确匹配
        if key in bom_name_map:
            entity_cache[key] = bom_name_map[key][1]
            return entity_cache[key]

        # 级别1b：双向子串匹配（min长度>=4 防止误匹配）
        for bn, (_, bid) in bom_name_map.items():
            if bn and len(bn) >= 4 and len(key) >= 4:
                if bn in key or key in bn:
                    entity_cache[key] = bid
                    return bid

        # 级别2：SequenceMatcher 模糊匹配（阈值0.75）
        best_r, best_id = 0.0, None
        for bn in bom_lower_names:
            r = SequenceMatcher(None, key, bn).ratio()
            if r > best_r:
                best_r, best_id = r, bom_name_map[bn][1]
        if best_r >= 0.75 and best_id:
            entity_cache[key] = best_id
            return best_id

        entity_cache[key] = None
        return None

    matched = 0
    for t in flat_triples:
        if t.get("head_type") in PART_TYPES:
            bid = _lookup(t.get("head", ""))
            if bid:
                t["head_bom_id"] = bid
                matched += 1
        if t.get("tail_type") in PART_TYPES:
            bid = _lookup(t.get("tail", ""))
            if bid:
                t["tail_bom_id"] = bid
                matched += 1
        # 向后兼容：participatesIn 保留原 bom_part_id 字段
        if t.get("relation") == "participatesIn" and t.get("head_bom_id"):
            t["bom_part_id"] = t["head_bom_id"]

    return matched


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

    # 2. LLM KG 提取（直接循环，支持实时进度推送）
    from backend.pipelines.nodes_kg import (
        _is_procedure_text, _KG_EXTRACTION_PROMPT, _KG_GLEANING_PROMPT, _parse_kg_json,
    )
    import json as _json

    proc_chunks = [c for c in chunks if _is_procedure_text(c["text"])]
    yield {"type": "log", "message": f"[Stage2] 关键词过滤：{len(proc_chunks)}/{len(chunks)} 段进入KG提取"}

    kg_triples = []
    if not proc_chunks:
        yield {"type": "log", "message": "[Stage2] ⚠ 无装配相关文本，写入空结果"}
    else:
        errors = 0
        total = len(proc_chunks)
        for i, chunk in enumerate(proc_chunks):
            chunk_id = chunk.get("chunk_id", f"c{i}")
            ata_section = chunk.get("ata_section", "Unknown")
            text = chunk.get("text", "")[:1500]

            yield {"type": "log", "message": f"[Stage2] LLM提取第 {i+1}/{total} 段 — {ata_section}"}

            try:
                prompt = _KG_EXTRACTION_PROMPT.format(
                    ata_section=ata_section,
                    chunk_text=text,
                )
                resp1 = state.llm_client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                )
                raw1 = resp1.choices[0].message.content or ""
                parsed1 = _parse_kg_json(raw1, chunk_id)

                if not parsed1:
                    errors += 1
                    yield {"type": "log", "message": f"[Stage2] ⚠ 第 {i+1}/{total} 段解析失败，跳过"}
                    continue

                # Gleaning 第二轮
                existing_summary = _json.dumps(
                    [{"id": e["id"], "type": e["type"], "text": e["text"]}
                     for e in parsed1["entities"]],
                    ensure_ascii=False,
                )
                try:
                    gleaning_prompt = _KG_GLEANING_PROMPT.format(
                        ata_section=ata_section,
                        chunk_text=text,
                        existing_entities=existing_summary,
                    )
                    resp2 = state.llm_client.chat.completions.create(
                        messages=[{"role": "user", "content": gleaning_prompt}],
                        temperature=0.1,
                    )
                    raw2 = resp2.choices[0].message.content or ""
                    parsed2 = _parse_kg_json(raw2, chunk_id)
                    if parsed2 and (parsed2["entities"] or parsed2["relations"]):
                        existing_ids = {e["id"] for e in parsed1["entities"]}
                        new_entities = [e for e in parsed2["entities"] if e["id"] not in existing_ids]
                        existing_rel_keys = {(r["head"], r["type"], r["tail"]) for r in parsed1["relations"]}
                        new_entity_ids = existing_ids | {e["id"] for e in new_entities}
                        new_relations = [
                            r for r in parsed2["relations"]
                            if (r["head"], r["type"], r["tail"]) not in existing_rel_keys
                            and r["head"] in new_entity_ids
                            and r["tail"] in new_entity_ids
                        ]
                        # Gleaning 第二轮补全的关系置信度衰减 ×0.8
                        for nr in new_relations:
                            nr["weight"] = round(nr.get("weight", 5) * 0.8, 1)
                        parsed1["entities"] += new_entities
                        parsed1["relations"] += new_relations
                except Exception:
                    pass  # 第二轮失败不影响第一轮

                parsed1["ata_section"] = ata_section
                kg_triples.append(parsed1)
                yield {
                    "type": "log",
                    "message": (
                        f"[Stage2] ✅ 第 {i+1}/{total} 段完成："
                        f"实体{len(parsed1['entities'])}，关系{len(parsed1['relations'])}"
                    ),
                }

            except Exception as exc:
                errors += 1
                yield {"type": "log", "message": f"[Stage2] ⚠ 第 {i+1}/{total} 段异常：{exc}"}

        yield {"type": "log", "message": f"[Stage2] KG提取完成：成功{len(kg_triples)}/{total}，失败{errors}"}

    yield {"type": "log", "message": f"[Stage2] 生成 {len(kg_triples)} 个三元组 chunk"}

    # 3. 展开为平铺格式
    flat_triples = _kg_chunks_to_flat_triples(kg_triples)
    yield {"type": "log", "message": f"[Stage2] 平铺后共 {len(flat_triples)} 条三元组（过滤前）"}

    # 3.5 后处理过滤：低置信度 / 噪音实体 / 本体约束
    before_count = len(flat_triples)
    flat_triples = _post_process_triples(flat_triples)
    yield {"type": "log", "message": f"[Stage2] 后处理过滤：{before_count} → {len(flat_triples)} 条三元组"}

    if not flat_triples:
        yield {"type": "log", "message": "[Stage2] ⚠ 未提取到三元组（文本可能不含装配工序相关内容）"}

    # 4. 增强实体对齐（所有关系类型，Part + Assembly 实体，双向子串+模糊匹配）
    bom_data = read_stage("bom")
    bom_entities = (bom_data or {}).get("entities", []) if bom_data else []
    if bom_entities:
        aligned_count = _align_manual_to_bom(flat_triples, bom_entities)
        yield {"type": "log", "message": f"[Stage2] BOM 实体对齐：{aligned_count} 个实体字段命中（覆盖全部关系类型）"}

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
import unicodedata as _unicodedata


_KG_ABBREV_EXPAND = {
    "HPC": "高压压气机", "LPC": "低压压气机",
    "HPT": "高压涡轮",   "LPT": "低压涡轮",
    "CC": "燃烧室",      "FC": "火焰筒",
    "FAN": "风扇",       "AGB": "附件齿轮箱",
    "Blade": "叶片",     "Disk": "叶盘",
    "Vane": "导向叶片",  "Casing": "机匣",
    "Rotor": "转子",     "Stator": "静子",
    "Seal": "封严环",    "Bearing": "轴承",
    "Shaft": "轴",       "Nozzle": "喷嘴",
}
_KG_STAGE_RE = _re.compile(r"[Ss]tage[-_\s]?(\d+)")

def _normalize(text: str) -> str:
    """归一化：NFKC全角→半角 + Stage变体统一 + 缩写展开 + 小写（与 harness_golden 保持一致）"""
    if not text:
        return ""
    text = text.lstrip(".")          # 剥离BOM层级前缀（.SEAL → SEAL）
    text = _unicodedata.normalize("NFKC", text)
    text = _KG_STAGE_RE.sub(lambda m: f"第{m.group(1)}级", text)
    for abbr in sorted(_KG_ABBREV_EXPAND, key=len, reverse=True):
        text = text.replace(abbr, _KG_ABBREV_EXPAND[abbr])
    return text.strip().lower()


def _audit_golden(golden: list) -> dict:
    """自动检测 golden_triples 中的潜在质量问题，返回审计报告。"""
    valid_relations = {
        "precedes", "participatesIn", "isPartOf", "matesWith",
        "requires", "specifiedBy", "hasInterface", "constrainedBy", "adjacentTo"
    }
    procedure_verbs = {
        "remove", "install", "apply", "locate", "tighten",
        "clean", "inspect", "loosen", "face", "torque"
    }
    issues = []
    for i, t in enumerate(golden):
        rel = t.get("relation", "")
        if rel not in valid_relations:
            issues.append({"idx": i, "type": "invalid_relation",
                           "desc": f"未知关系类型 '{rel}'"})
        for field in ("head", "tail"):
            v = t.get(field, "")
            if v and len(v) < 3:
                issues.append({"idx": i, "type": "too_short_entity",
                               "desc": f"{field}='{v}' 过短，可能截断"})
            if v.startswith("."):
                issues.append({"idx": i, "type": "bom_prefix_entity",
                               "desc": f"{field}='{v}' 含BOM层级前缀，_normalize 已自动剥离"})
        if rel == "precedes":
            for field in ("head", "tail"):
                v = t.get(field, "").lower()
                if not any(verb in v for verb in procedure_verbs):
                    issues.append({"idx": i, "type": "suspicious_precedes",
                                   "desc": f"precedes 中 {field}='{t.get(field)}' 不像 Procedure（启发式，需人工确认）"})
    return {
        "total": len(golden),
        "issues_count": len(issues),
        "issues": issues,
        "reliability_score": round(1.0 - len(issues) / max(len(golden) * 2, 1), 3),
        "note": "bom_prefix_entity 已由_normalize自动处理；suspicious_precedes为启发式，需人工核查",
    }


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


def _align_cad_via_llm(unmatched_parts: list, flat_triples: list,
                        bom_entities: list, state, mapping_out: dict):
    """
    LLM兜底：根据CAD配合拓扑推断 Part_XXXXXX 对应的BOM实体。
    仅在 len(unmatched_parts) <= 20 时触发，节省token。
    """
    # 构建邻接摘要：每个未命中零件的配合邻居（优先用已映射的BOM名称）
    adjacency: dict = {}
    for p in unmatched_parts:
        neighbors = []
        for t in flat_triples:
            if t.get("relation") != "matesWith":
                continue
            if t.get("head") == p:
                n = t.get("tail", "")
            elif t.get("tail") == p:
                n = t.get("head", "")
            else:
                continue
            n_display = mapping_out.get(n, {}).get("bom_name", n)
            neighbors.append(n_display)
        adjacency[p] = neighbors[:5]  # 最多5个邻居

    bom_candidates = [
        {"id": e["id"], "name": e["name"]}
        for e in bom_entities[:80] if e.get("name")
    ]

    prompt = (
        "你是航空发动机知识图谱专家。\n"
        "以下CAD零件（Part_XXXXXX格式）及其matesWith配合邻居（部分已映射为BOM名称）：\n"
        f"{adjacency}\n\n"
        "以下是BOM零件候选列表（id + name）：\n"
        f"{bom_candidates}\n\n"
        "请根据每个CAD零件的配合邻居推断它最可能对应的BOM零件。\n"
        "仅在置信度较高时给出BOM零件name，不确定时返回null。\n"
        '严格返回JSON格式，例：{"Part_283904": "COMPRESSOR ROTOR INSTALLATION", "Part_290891": null}'
    )

    try:
        resp = state.llm_client.chat.completions.create(
            model=state.llm_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
        )
        import json as _json, re as _re
        raw = (resp.choices[0].message.content or "").strip()
        m = _re.search(r"\{.*\}", raw, _re.DOTALL)
        if not m:
            return
        result = _json.loads(m.group())
        bom_name_idx = {e["name"]: e for e in bom_entities if e.get("name")}
        for cad_part, bom_name in result.items():
            if bom_name and isinstance(bom_name, str) and bom_name in bom_name_idx:
                if cad_part not in mapping_out:
                    mapping_out[cad_part] = {
                        "bom_id": bom_name_idx[bom_name]["id"],
                        "bom_name": bom_name,
                        "method": "llm_topology",
                        "confidence": 0.5,
                    }
    except Exception:
        pass  # LLM失败不中断流程


def _align_cad_to_bom(flat_triples: list, bom_entities: list, state) -> dict:
    """
    CAD Part_XXXXXX → BOM 实体对齐，三级策略：
    1. 有名称的CAD零件：模糊匹配（阈值0.70）
    2. 数字ID零件：装配层级结构匹配（子节点数量差≤2）
    3. LLM拓扑推断（≤20个未命中时触发）
    返回 mapping: {cad_part_name -> {bom_id, bom_name, method, confidence}}
    """
    from difflib import SequenceMatcher

    # 收集所有CAD实体
    cad_parts: set = set()
    for t in flat_triples:
        for field in ("head", "tail"):
            v = t.get(field, "")
            if v:
                cad_parts.add(v)

    named_parts   = {p for p in cad_parts if not p.startswith("Part_")}
    numeric_parts = {p for p in cad_parts if p.startswith("Part_")}

    # BOM索引（小写名称 → entity dict）
    bom_map = {e["name"].lower(): e for e in bom_entities if e.get("name")}
    mapping: dict = {}

    # 级别1：有名称的CAD零件 → 模糊匹配（阈值0.70）
    for part in named_parts:
        best_r, best_e = 0.0, None
        for bn, be in bom_map.items():
            r = SequenceMatcher(None, part.lower(), bn).ratio()
            if r > best_r:
                best_r, best_e = r, be
        if best_r >= 0.70 and best_e:
            mapping[part] = {
                "bom_id": best_e["id"], "bom_name": best_e["name"],
                "method": "fuzzy_name", "confidence": round(best_r, 3),
            }

    # 级别2：装配层级结构匹配（子节点数量相似度）
    # 统计CAD装配树中每个父节点的子节点数
    cad_child_count: dict = {}
    for t in flat_triples:
        if t.get("relation") == "isPartOf":
            parent = t.get("tail", "")
            if parent:
                cad_child_count[parent] = cad_child_count.get(parent, 0) + 1

    # 统计BOM中每个Assembly的子节点数（从entity的parent_id字段反推）
    bom_child_count: dict = {}
    for e in bom_entities:
        pid = e.get("parent_id")
        if pid:
            bom_child_count[pid] = bom_child_count.get(pid, 0) + 1

    bom_entities_by_id = {e["id"]: e for e in bom_entities}
    for cad_part, cad_count in cad_child_count.items():
        if cad_part in mapping:
            continue  # 已命中，跳过
        best_match, best_diff = None, float("inf")
        for bid, be in bom_entities_by_id.items():
            bc = bom_child_count.get(bid, 0)
            diff = abs(cad_count - bc)
            if diff < best_diff:
                best_diff, best_match = diff, be
        if best_diff <= 2 and best_match:
            mapping[cad_part] = {
                "bom_id": best_match["id"], "bom_name": best_match["name"],
                "method": "structure_match",
                "confidence": round(1.0 / (1 + best_diff), 3),
            }

    # 级别3：LLM拓扑推断（仅≤20个未命中数字ID时触发）
    unmatched = [p for p in numeric_parts if p not in mapping]
    if unmatched and len(unmatched) <= 20:
        _align_cad_via_llm(unmatched, flat_triples, bom_entities, state, mapping)

    # 将对齐结果写回 flat_triples
    for t in flat_triples:
        for field in ("head", "tail"):
            part = t.get(field, "")
            if part in mapping:
                t[f"{field}_bom_id"]       = mapping[part]["bom_id"]
                t[f"{field}_bom_name"]     = mapping[part]["bom_name"]
                t[f"{field}_align_method"] = mapping[part]["method"]

    return mapping


# ─────────────────────────────────────────────
# 内部生成器：阶段3 CAD 处理
# ─────────────────────────────────────────────

def _stage3_cad_gen(tmp_path: str, ext: str, state: AppState, neo4j_cfg: dict):
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

    # 增强 CAD → BOM 对齐（三级：名称模糊 + 装配结构 + LLM拓扑兜底）
    bom_entities_for_cad = []
    if stage_exists("bom"):
        bom_data = read_stage("bom")
        bom_entities_for_cad = (bom_data or {}).get("entities", [])

    if bom_entities_for_cad:
        cad_mapping = _align_cad_to_bom(flat_triples, bom_entities_for_cad, state)
        method_dist = {}
        for v in cad_mapping.values():
            m = v["method"]
            method_dist[m] = method_dist.get(m, 0) + 1
        hit = sum(1 for t in flat_triples if t.get("head_bom_id") or t.get("tail_bom_id"))
        yield {"type": "log", "message": f"[Stage3] BOM 对齐命中 {hit} 个实体字段，方法分布：{method_dist}"}
        if not cad_mapping:
            yield {"type": "log", "message": "[Stage3] ⚠ CAD 零件命名均为数字ID（STEP文件PRODUCT名称为空），对齐率有限。建议重新导出含零件编号的STEP文件。"}
    else:
        yield {"type": "log", "message": "[Stage3] ⚠ 无BOM数据，跳过CAD对齐（建议先完成Stage1再处理Stage3）"}

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

    from backend.pipelines.kg_postprocess import postprocess_triples

    all_predicted = []
    stages_included = []
    postprocess_report: dict = {}
    for stage in ("bom", "manual", "cad"):
        if stage_exists(stage):
            data = read_stage(stage)
            if isinstance(data, list):
                raw_triples = data
            else:
                raw_triples = (data or {}).get("triples", [])
            skip_onto = stage in ("bom", "cad")
            cleaned, pp_stats = postprocess_triples(raw_triples, skip_ontology=skip_onto)
            all_predicted.extend(cleaned)
            stages_included.append(stage)
            postprocess_report[stage] = pp_stats

    report = _compute_prf1(golden, all_predicted)
    report["stages_included"]  = stages_included
    report["golden_count"]     = len(golden)
    report["predicted_count"]  = len(all_predicted)
    report["golden_audit"]     = _audit_golden(golden)
    report["postprocess"]      = postprocess_report
    return JSONResponse(report)


# ─────────────────────────────────────────────
# POST /kg/stages/sync-neo4j
# ─────────────────────────────────────────────

def _write_all_stages_to_neo4j(neo4j_cfg: dict) -> dict:
    """
    从已有的 stage1/2/3 JSON 文件读取三元组，统一写入 Neo4j。

    节点体系（统一标签）：
      - Part / Assembly               —— 来自 BOM + CAD + 手册
      - Procedure / Tool / Specification / Interface  —— 来自手册
    关系体系（统一类型）：
      - isPartOf     —— BOM层级 + 手册层级 + CAD装配树
      - matesWith    —— 手册配合 + CAD约束
      - precedes / requires / specifiedBy / participatesIn —— 手册工序
      - SAME_AS      —— 跨阶段名称模糊匹配产生的对齐边

    写入前对每阶段三元组执行后处理（过滤 + 归一化 + 去重）。
    """
    from backend.pipelines.kg_postprocess import postprocess_triples
    import logging as _logging
    _log = _logging.getLogger(__name__)
    postprocess_stats: dict = {}

    try:
        from neo4j import GraphDatabase
    except ImportError:
        return {"ok": False, "error": "neo4j 包未安装"}

    try:
        driver = GraphDatabase.driver(
            neo4j_cfg.get("uri", "bolt://localhost:7687"),
            auth=(neo4j_cfg.get("user", "neo4j"),
                  neo4j_cfg.get("pass", neo4j_cfg.get("password", "neo4j"))),
        )
        driver.verify_connectivity()
    except Exception as e:
        return {"ok": False, "error": f"Neo4j 连接失败: {e}"}

    stats = {"bom_nodes": 0, "bom_rels": 0,
             "manual_nodes": 0, "manual_rels": 0,
             "cad_nodes": 0, "cad_rels": 0,
             "same_as_rels": 0}
    logs = []

    # ── 辅助：动态标签 MERGE（不支持参数化标签，逐条执行）
    KG_LABELS = {"Part", "Assembly", "Procedure", "Tool", "Specification", "Interface"}

    def _merge_node(session, label: str, name: str, extra: dict = None):
        lbl = label if label in KG_LABELS else "Part"
        q = f"MERGE (n:{lbl} {{kg_name: $name}}) SET n.source = coalesce(n.source, $src)"
        params = {"name": name, "src": extra.get("source", "unknown") if extra else "unknown"}
        if extra:
            for k, v in extra.items():
                if k != "source":
                    q = q.rstrip() + f" SET n.{k} = ${k}"
                    params[k] = v
        session.run(q, **params)

    def _merge_rel(session, head: str, rel: str, tail: str, props: dict = None):
        p = props or {}
        session.run(
            f"""
            MATCH (a {{kg_name: $h}})
            MATCH (b {{kg_name: $t}})
            MERGE (a)-[r:{rel}]->(b)
            SET r += $props
            """,
            h=head, t=tail, props=p,
        )

    with driver.session() as session:
        # ── 初始化约束（幂等）
        for lbl in KG_LABELS:
            try:
                session.run(f"CREATE CONSTRAINT IF NOT EXISTS FOR (n:{lbl}) REQUIRE n.kg_name IS UNIQUE")
            except Exception:
                pass

        # ══ Stage1：BOM ══
        bom_data = read_stage("bom") if stage_exists("bom") else None
        if bom_data:
            entities = bom_data.get("entities", [])
            triples  = bom_data.get("triples",  [])
            # BOM 置信度均为 1.0，跳过本体校验（isPartOf 在 ROOT 处理会被误伤）
            triples, _pp = postprocess_triples(triples, skip_ontology=True)
            postprocess_stats["bom"] = _pp
            _log.info(f"[PostProcess] BOM: {_pp}")

            # 写 BOM 节点（统一用 kg_name = part_name）
            for e in entities:
                name = e.get("name", "")
                if not name:
                    continue
                lbl = e.get("type", "Part")
                try:
                    session.run(
                        f"MERGE (n:{lbl} {{kg_name: $name}}) "
                        "SET n.part_id = $pid, n.source = 'BOM', n.quantity = $qty",
                        name=name, pid=e.get("id", ""), qty=e.get("quantity", 1),
                    )
                    stats["bom_nodes"] += 1
                except Exception:
                    pass

            # 写 BOM 关系（isPartOf，替代旧的 CHILD_OF）
            name_map = {e.get("id", ""): e.get("name", "") for e in entities}
            for t in triples:
                head_name = t.get("head", "")
                tail_name = t.get("tail", "")
                if not head_name or not tail_name:
                    continue
                try:
                    session.run(
                        """
                        MATCH (a {kg_name: $h})
                        MATCH (b {kg_name: $t})
                        MERGE (a)-[:isPartOf]->(b)
                        """,
                        h=head_name, t=tail_name,
                    )
                    stats["bom_rels"] += 1
                except Exception:
                    pass

            logs.append(f"BOM: {stats['bom_nodes']} 节点, {stats['bom_rels']} 关系")

        # ══ Stage2：手册 ══
        manual_data = read_stage("manual") if stage_exists("manual") else None
        if manual_data:
            triples = manual_data.get("triples", [])
            # 手册三元组有 head_type/tail_type，执行完整后处理含本体校验
            triples, _pp = postprocess_triples(triples, skip_ontology=False)
            postprocess_stats["manual"] = _pp
            _log.info(f"[PostProcess] Manual: {_pp}")

            # 收集实体（去重）
            entity_map: dict = {}
            for t in triples:
                for key, etype in ((t.get("head"), t.get("head_type")),
                                   (t.get("tail"), t.get("tail_type"))):
                    if key and key not in entity_map:
                        entity_map[key] = etype or "Part"

            # 写手册节点
            from collections import defaultdict
            by_label = defaultdict(list)
            for name, label in entity_map.items():
                lbl = label if label in KG_LABELS else "Part"
                by_label[lbl].append(name)

            for lbl, names in by_label.items():
                try:
                    session.run(
                        f"UNWIND $names AS name "
                        f"MERGE (n:{lbl} {{kg_name: name}}) "
                        "SET n.source = coalesce(n.source + ',Manual', 'Manual')",
                        names=names,
                    )
                    stats["manual_nodes"] += len(names)
                except Exception:
                    pass

            # 写手册关系
            for t in triples:
                rel = t.get("relation", "")
                head = t.get("head", "")
                tail = t.get("tail", "")
                if not rel or not head or not tail:
                    continue
                try:
                    session.run(
                        f"""
                        MATCH (a {{kg_name: $h}})
                        MATCH (b {{kg_name: $t}})
                        MERGE (a)-[r:{rel}]->(b)
                        SET r.source = 'Manual', r.confidence = $conf
                        """,
                        h=head, t=tail, conf=t.get("confidence", 1.0),
                    )
                    stats["manual_rels"] += 1
                except Exception:
                    pass

            logs.append(f"手册: {stats['manual_nodes']} 节点, {stats['manual_rels']} 关系")

        # ══ Stage3：CAD ══
        cad_data = read_stage("cad") if stage_exists("cad") else None
        if cad_data:
            triples = cad_data if isinstance(cad_data, list) else cad_data.get("triples", [])
            # CAD 三元组类型信息不全，跳过本体校验
            triples, _pp = postprocess_triples(triples, skip_ontology=True)
            postprocess_stats["cad"] = _pp
            _log.info(f"[PostProcess] CAD: {_pp}")

            for t in triples:
                rel  = t.get("relation", "")
                head = t.get("head", "")
                tail = t.get("tail", "")
                if not rel or not head or not tail:
                    continue
                # 写节点
                for name in (head, tail):
                    try:
                        session.run(
                            "MERGE (n:Part {kg_name: $name}) "
                            "SET n.source = coalesce(n.source + ',CAD', 'CAD'), n.cad_id = $name",
                            name=name,
                        )
                        stats["cad_nodes"] += 1
                    except Exception:
                        pass
                # 写关系
                try:
                    session.run(
                        f"""
                        MATCH (a {{kg_name: $h}})
                        MATCH (b {{kg_name: $t}})
                        MERGE (a)-[r:{rel}]->(b)
                        SET r.source = 'CAD', r.confidence = $conf
                        """,
                        h=head, t=tail, conf=t.get("confidence", 0.9),
                    )
                    stats["cad_rels"] += 1
                except Exception:
                    pass

            logs.append(f"CAD: {stats['cad_nodes']} 节点操作, {stats['cad_rels']} 关系")

        # ══ SAME_AS：跨阶段对齐边 ══
        # 对手册三元组中已对齐到BOM的 Part/Assembly 实体，添加 SAME_AS 边
        if manual_data and bom_data:
            from difflib import SequenceMatcher
            bom_entities = bom_data.get("entities", [])
            bom_name_map = {e.get("name", "").lower(): e.get("name", "")
                            for e in bom_entities if e.get("name")}

            manual_triples = manual_data.get("triples", [])
            aligned_pairs: set = set()
            PART_TYPES = {"Part", "Assembly"}

            for t in manual_triples:
                for field, ftype in (("head", "head_type"), ("tail", "tail_type")):
                    if t.get(ftype) not in PART_TYPES:
                        continue
                    manual_name = t.get(field, "")
                    if not manual_name:
                        continue
                    key = manual_name.lower()
                    # 精确 + 双向子串
                    bom_match = None
                    if key in bom_name_map:
                        bom_match = bom_name_map[key]
                    else:
                        for bn, orig in bom_name_map.items():
                            if bn and len(bn) >= 4 and len(key) >= 4:
                                if bn in key or key in bn:
                                    bom_match = orig
                                    break
                    # 模糊匹配兜底
                    if not bom_match:
                        best_r, best_orig = 0.0, None
                        for bn, orig in bom_name_map.items():
                            r = SequenceMatcher(None, key, bn).ratio()
                            if r > best_r:
                                best_r, best_orig = r, orig
                        if best_r >= 0.75:
                            bom_match = best_orig

                    if bom_match and (manual_name, bom_match) not in aligned_pairs:
                        aligned_pairs.add((manual_name, bom_match))
                        try:
                            session.run(
                                """
                                MATCH (a {kg_name: $m})
                                MATCH (b {kg_name: $b})
                                MERGE (a)-[:SAME_AS]->(b)
                                """,
                                m=manual_name, b=bom_match,
                            )
                            stats["same_as_rels"] += 1
                        except Exception:
                            pass

            logs.append(f"SAME_AS 对齐边: {stats['same_as_rels']} 条")

    driver.close()
    return {"ok": True, "stats": stats, "logs": logs, "postprocess": postprocess_stats}


@router.post("/stages/sync-neo4j", summary="同步所有阶段数据到 Neo4j")
def kg_sync_neo4j(request: Request, state: AppState = Depends(get_state)):
    """
    读取已生成的 stage1/2/3 JSON 文件，统一写入 Neo4j。
    无需重新上传文件。各阶段用 kg_name 属性统一标识节点，
    跨阶段同名实体通过 SAME_AS 关系关联。
    """
    neo4j_cfg = request.app.state.neo4j_cfg
    result = _write_all_stages_to_neo4j(neo4j_cfg)
    if not result.get("ok"):
        return JSONResponse(status_code=503, content=result)
    return JSONResponse(result)


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
