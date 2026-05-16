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

from typing import List

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


_NHA_PATTERN = _re.compile(r'SEE\s+FIG\.?\s*(\d+)\s+FOR\s+NHA', _re.IGNORECASE)


def _resolve_nha_triples(triples: list, entities: list) -> list:
    """
    将 tail==ROOT 且 head 含 'SEE FIG.X FOR NHA' 的三元组，
    重新连接到对应图的顶层 Assembly。

    fig_to_assembly 建立策略：entities 列表中第一个 type==Assembly 的实体
    视为 FIG.1 的顶层装配体（IPC 单图 BOM 场景，100% 准确）。
    """
    if not entities:
        return triples

    # 建立 fig_num → head_label 映射
    fig_to_assembly: dict = {}
    fig_counter = 0
    for e in entities:
        if e.get("type") == "Assembly":
            pn = e.get("part_number", "")
            nm = e.get("name", "")
            label = f"{pn} {nm}".strip() if pn else nm
            fig_counter += 1
            fig_to_assembly[str(fig_counter)] = label
            break  # 单图BOM：只取第一个顶层Assembly

    # 修正 NHA 三元组
    for t in triples:
        if t.get("tail") != "ROOT":
            continue
        head = t.get("head", "")
        m = _NHA_PATTERN.search(head)
        if not m:
            continue
        fig_num = m.group(1)
        assembly_label = fig_to_assembly.get(fig_num)
        if assembly_label and assembly_label != head:
            t["tail"] = assembly_label
            t["tail_type"] = "Assembly"

    return triples


def _apply_ipc_hierarchy(records: list) -> list:
    """
    对 LLM 提取的 IPC BOM 平铺记录应用确定性层级规则，填充 parent_id。

    规则优先级（高→低）：
      R1. nomenclature 含点号前缀（OCR原文保留）→ 优先使用点号栈逻辑
      R2. fig_item == "ATTACHING PARTS" → 标记附件块上下文，本行不生成实体
      R3. 附件块内的零件（ATTACHING PARTS 之后直到下一个非附件行）
          → parent_id = 附件块开始前最近的 Assembly part_id
      R4. fig_item 以 "-" 开头（-40、-40A）
          → 去掉 "-" 和尾部字母得到基础序号（"40"）
          → parent_id = 基础序号对应零件的 parent_id（同级，共享父节点）
      R5. fig_item 为普通整数（10, 20, 30）且 nomenclature 无点号
          → parent_id = 第一个顶层 Assembly 的 part_id
      R6. 其他无法确定 → parent_id 保持 ""（挂 ROOT）
    """
    import re as _r

    _FIG_INT = _r.compile(r'^\d+$')
    _FIG_DASH = _r.compile(r'^-(\d+)')

    # 找出第一个顶层 Assembly（fig_item 为 "-1" 或第一个 Assembly category）
    root_assembly_id = ""
    for rec in records:
        cat = str(rec.get("category", "")).strip()
        fig = str(rec.get("fig_item", "")).strip()
        pid = str(rec.get("part_id", "")).strip()
        if not pid:
            continue
        if cat == "Assembly" and (fig in ("-1", "1") or not root_assembly_id):
            root_assembly_id = pid
            break

    # fig_item 整数 → part_id 映射（用于 dash 前缀关联）
    fig_to_pid: dict = {}
    # fig_item → parent_id 映射（dash 系列共享同一父节点）
    fig_to_parent: dict = {}

    in_attaching = False
    attaching_parent_id = ""
    result = []

    for rec in records:
        rec = dict(rec)
        fig = str(rec.get("fig_item", "")).strip()
        pid = str(rec.get("part_id", "")).strip()
        nom = str(rec.get("nomenclature", "")).strip()
        cat = str(rec.get("category", "")).strip()

        # ATTACHING PARTS 标记行：不生成实体，记录上下文
        if fig == "ATTACHING PARTS" or cat == "AttachingParts":
            in_attaching = True
            # 上文最近有 part_id 的非 AttachingParts 条目作为附件归属父节点
            if result:
                for prev in reversed(result):
                    if prev.get("part_id") and prev.get("category") != "AttachingParts":
                        attaching_parent_id = prev["part_id"]
                        break
            continue  # 不输出 ATTACHING PARTS 行本身

        # 已有点号前缀 → 由 _bom_df_to_entities_and_triples 的栈逻辑处理，不覆盖
        dot_level = 0
        nom_stripped = nom
        while nom_stripped.startswith("."):
            dot_level += 1
            nom_stripped = nom_stripped[1:]
        if dot_level > 0:
            # 有点号 → 不填 parent_id，让栈逻辑处理
            in_attaching = False
            if pid and _FIG_INT.match(fig):
                fig_to_pid[fig] = pid
                fig_to_parent[fig] = rec.get("parent_id", "")
            result.append(rec)
            continue

        # ATTACHING PARTS 块内
        if in_attaching and attaching_parent_id:
            rec["parent_id"] = attaching_parent_id
            result.append(rec)
            continue

        # 脱离附件块（遇到整数 fig_item）
        if _FIG_INT.match(fig):
            in_attaching = False

        # 顶层Assembly自身（pid == root_assembly_id）→ 保持parent_id=""，不做任何赋值
        if pid == root_assembly_id:
            fig_to_pid[fig] = pid
            fig_to_parent[fig] = ""
            result.append(rec)
            continue

        # dash 前缀：-40、-40A → 基础序号 40 → 共享父节点
        m_dash = _FIG_DASH.match(fig)
        if m_dash:
            base_fig = m_dash.group(1)
            if base_fig in fig_to_parent:
                rec["parent_id"] = fig_to_parent[base_fig]
            elif root_assembly_id:
                rec["parent_id"] = root_assembly_id
            result.append(rec)
            continue

        # 普通整数 fig_item，nomenclature 无点号 → 顶层 Assembly 的直属子件
        if _FIG_INT.match(fig) and root_assembly_id and pid != root_assembly_id:
            rec["parent_id"] = root_assembly_id
            fig_to_pid[fig] = pid
            fig_to_parent[fig] = root_assembly_id
            result.append(rec)
            continue

        # 顶层 Assembly 自身 或 无法确定
        if pid:
            fig_to_pid[fig] = pid
            fig_to_parent[fig] = rec.get("parent_id", "")
        result.append(rec)

    return result


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

    # ── 路径0：level_code 预处理 → 补填 parent_id ──────────────────────────
    # llm_to_csv 输出 level_code (1/1.1/1.1.1)，需转换为 parent_id 供路径2使用
    cols = list(df.columns)
    if "level_code" in cols and "parent_id" not in cols:
        df["parent_id"] = ""
    if "level_code" in cols:
        level_map: dict = {}  # level_code → part_id
        for _, row in df.iterrows():
            lc  = str(row.get("level_code", "")).strip()
            pid = str(row.get("part_id", "")).strip()
            if lc and pid:
                level_map[lc] = pid
        def _lc_to_parent(lc: str) -> str:
            if "." not in lc:
                return ""
            return level_map.get(".".join(lc.split(".")[:-1]), "")
        df["parent_id"] = df.apply(
            lambda r: _lc_to_parent(str(r.get("level_code", "")).strip())
                      if not str(r.get("parent_id", "")).strip()
                      else str(r.get("parent_id", "")).strip(),
            axis=1,
        )

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
            "item_callout": str(row.get("fig_item", "")).strip(),
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

            # 弹出层级 >= 当前层级的条目，但保留栈底的顶层Assembly（level=0）
            while parent_stack and parent_stack[-1][0] >= level:
                if len(parent_stack) == 1 and parent_stack[0][0] == 0:
                    break  # 保留根Assembly，不弹出
                parent_stack.pop()

            if level == 0 and not parent_stack:
                # 第一个level=0条目 → 真正的顶层装配体，挂ROOT
                parent_label = "ROOT"
                tail_type    = "ROOT"
            elif level == 0 and parent_stack:
                # 后续level=0条目 → 挂到栈底的顶层Assembly（不再是ROOT）
                parent_label = parent_stack[0][1]
                tail_type    = "Assembly"
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

    triples = _resolve_nha_triples(triples, entities)
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

_OCR_BOM_PROMPT = """你是航空IPC（图解零件目录）数据提取专家。以下是从扫描PDF中OCR识别的文本，来自 Pratt & Whitney Canada 发动机零件清单。

你的任务：**忠实提取**每行的零件数据，输出JSON数组。层级关系由后续程序根据规则计算，你不需要推断父子关系。

每条记录包含以下字段：
- part_id: 零件编号（如 3034344、MS9556-06、AS3209-267；若原文无编号则填 ""）
- part_name: 零件名称（去掉前缀点号后的纯名称）
- nomenclature: NOMENCLATURE列原文，**完整保留前缀点号**（如 ".SEAL, AIR"、"..SEAL 0.129 IN."）
- fig_item: FIG. ITEM 列原文（如 "-1"、"10"、"-40A"、"ATTACHING PARTS"；若无则 ""）
- qty: 数量整数（原文无数字则填 1）
- unit: 单位（默认 "件"）
- material: 材料（原文有则填，否则 ""）
- category: "Assembly"（含子件的组件）/ "Part"（零件）/ "Standard"（螺栓螺母等标准件），默认 "Part"
- parent_id: 一律填 ""（层级由程序计算，禁止猜测）

【提取规则】
1. nomenclature 忠实保留原文前缀点号：无点=顶层装配，"."=一级子件，".."=二级子件
2. part_name 是 nomenclature 去掉所有前缀点号后的名称
3. parent_id 固定填 ""，禁止填任何 part_id
4. 遇到 "ATTACHING PARTS" 行：fig_item 填 "ATTACHING PARTS"，part_id 填 ""，part_name 填 "ATTACHING PARTS"，category 填 "AttachingParts"
5. 含 "SEE FIG.X FOR NHA" 的零件：nomenclature 填 ".零件名"（单点前缀），part_name 去掉 "SEE FIG.X FOR NHA" 后缀
6. fig_item 带 dash 且含 "INTRCHG" 的互换件（如 "-40A ... INTRCHG WITH P/N ..."）：nomenclature 与被替代件同层级点号
7. 爆炸图页（行内容主要是图号如 "Figure 1  72-30-05  Page 2"）：整页跳过，不输出任何记录
8. "NOT USED" / "NOT ILLUSTRATED" 行：输出记录，fig_item 填原值，part_id 填 ""
9. PRE-SB / POST-SB 版本信息：完整保留在 part_name 中（如 "SEAL ASSEMBLY,AIR PRE-SB15108"）
10. 只输出JSON数组，不加任何说明文字

【fig_item 字段说明（帮助你识别，不要推断层级）】
- "-1" 或第一个整数条目通常是顶层装配体
- 普通整数（10, 20, 30...）是该图的子件序号
- 带 "-" 前缀（-40, -40A, -40B）是某序号的变体/替换件
- "ATTACHING PARTS" 标记一个附件块的开始

【示例输入→输出】
输入行: "-1  3034344  COMPRESSOR ROTOR INSTALLATION  1"
输出: {{"part_id":"3034344","part_name":"COMPRESSOR ROTOR INSTALLATION","nomenclature":"COMPRESSOR ROTOR INSTALLATION","fig_item":"-1","qty":1,"category":"Assembly","parent_id":"","material":"","unit":"件"}}

输入行: "10  MS9556-06  BOLT,MACHINE,DBL HEX  1"
输出: {{"part_id":"MS9556-06","part_name":"BOLT,MACHINE,DBL HEX","nomenclature":"BOLT,MACHINE,DBL HEX","fig_item":"10","qty":1,"category":"Standard","parent_id":"","material":"","unit":"件"}}

输入行: "40  3030349  .SEAL ASSEMBLY,AIR COMPRESSOR REAR  1"
输出: {{"part_id":"3030349","part_name":"SEAL ASSEMBLY,AIR COMPRESSOR REAR","nomenclature":".SEAL ASSEMBLY,AIR COMPRESSOR REAR","fig_item":"40","qty":1,"category":"Assembly","parent_id":"","material":"","unit":"件"}}

输入行: "-40A  3103074-01  .SEAL ASSEMBLY,AIR PRE-SB15108  1"
输出: {{"part_id":"3103074-01","part_name":"SEAL ASSEMBLY,AIR PRE-SB15108","nomenclature":".SEAL ASSEMBLY,AIR PRE-SB15108","fig_item":"-40A","qty":1,"category":"Assembly","parent_id":"","material":"","unit":"件"}}

输入行: "ATTACHING PARTS"
输出: {{"part_id":"","part_name":"ATTACHING PARTS","nomenclature":"ATTACHING PARTS","fig_item":"ATTACHING PARTS","qty":1,"category":"AttachingParts","parent_id":"","material":"","unit":"件"}}

输入行: "50  MS9676-11  NUT,DBL HEX  4"
输出: {{"part_id":"MS9676-11","part_name":"NUT,DBL HEX","nomenclature":"NUT,DBL HEX","fig_item":"50","qty":4,"category":"Standard","parent_id":"","material":"","unit":"件"}}

输入行: "5  3102464-03  .ROTOR BALANCING ASSEMBLY SEE FIG.2 FOR NHA  1"
输出: {{"part_id":"3102464-03","part_name":"ROTOR BALANCING ASSEMBLY","nomenclature":".ROTOR BALANCING ASSEMBLY","fig_item":"5","qty":1,"category":"Assembly","parent_id":"","material":"","unit":"件"}}

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
            # 应用 IPC 确定性层级规则（填充 parent_id）
            records = _apply_ipc_hierarchy(records)
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
        # llm_to_csv 只写 bom_records，需在此补转 bom_dataframe_json
        if not pipeline_state.get("bom_dataframe_json") and pipeline_state.get("bom_records"):
            import pandas as _pd
            _df = _pd.DataFrame(pipeline_state["bom_records"])
            pipeline_state["bom_dataframe_json"] = _df.to_json(orient="records", force_ascii=False)

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
    # ── HITL: 生成 StageReport ───────────────────────────────────────
    try:
        from backend.pipelines.kg_report import generate_stage_report
        from backend.kg_storage import (
            write_stage_report, write_stage_state, StageState,
            STAGE_REPORT_FILES,
        )
        current_data = read_stage("bom") or {}
        report = generate_stage_report("bom", current_data, prev_data=None)
        write_stage_report("bom", report)
        write_stage_state("bom", StageState(stage="bom", status="awaiting_review"))
        yield {"type": "stage_report_ready", "stage": "bom", "issues_count": len(report.issues)}
    except Exception as e:
        yield {"type": "log", "message": f"[Report] 报告生成失败（不影响主流程）: {e}"}
    # ────────────────────────────────────────────────────────────────
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
# 内部辅助：MD → 文本 chunks（按 <!-- Page N --> 切分）
# ─────────────────────────────────────────────

def _extract_md_chunks(file_path: str):
    """
    从 Markdown 文件提取文本 chunks，按 <!-- Page N --> 注释切分页面。
    与 PDF pdfplumber 的逐页 chunk 结构完全一致。

    返回: (chunks: list[dict], method: str)
      chunks 格式: [{"text": str, "chunk_id": str, "ata_section": str}]
    """
    import re
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    parts = re.split(r"<!--\s*Page\s+\d+\s*-->", content)
    chunks = []
    for i, part in enumerate(parts):
        text = part.strip()
        if text:
            chunks.append({
                "text": text,
                "chunk_id": f"p{i}",
                "ata_section": f"Page {i + 1}",
            })
    return chunks, "markdown"


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
        ent_map      = {e["id"]: e.get("text", "")           for e in chunk.get("entities", [])}
        ent_type_map = {e["id"]: e.get("type", "")           for e in chunk.get("entities", [])}
        ent_pt_map   = {e["id"]: e.get("procedure_type", "") for e in chunk.get("entities", [])}
        ent_st_map   = {e["id"]: e.get("spec_type", "")      for e in chunk.get("entities", [])}
        ent_desc_map = {e["id"]: e.get("description", "")    for e in chunk.get("entities", [])}
        for rel in chunk.get("relations", []):
            head_id = rel.get("head") or rel.get("source_id", "")
            tail_id = rel.get("tail") or rel.get("target_id", "")
            head_text = ent_map.get(head_id, "")
            tail_text = ent_map.get(tail_id, "")
            if head_text and tail_text:
                flat.append({
                    "head":                head_text,
                    "relation":            rel["type"],
                    "tail":                tail_text,
                    "confidence":          round(rel.get("weight", 5) / 10.0, 2),
                    "source":              "Manual",
                    "head_type":           ent_type_map.get(head_id, ""),
                    "tail_type":           ent_type_map.get(tail_id, ""),
                    "head_procedure_type": ent_pt_map.get(head_id, ""),
                    "tail_procedure_type": ent_pt_map.get(tail_id, ""),
                    "head_spec_type":      ent_st_map.get(head_id, ""),
                    "tail_spec_type":      ent_st_map.get(tail_id, ""),
                    "head_description":    ent_desc_map.get(head_id, ""),
                    "tail_description":    ent_desc_map.get(tail_id, ""),
                })
    return flat


def _post_process_triples(triples: list) -> list:
    """后处理过滤：低置信度、噪音实体、本体约束校验。"""
    import re as _re
    import unicodedata as _ud
    _noise_pattern = _re.compile(
        r"^(figure|fig|table|tab|sb|amm|cmm|ipc)\s*[\d\-]+$", _re.IGNORECASE
    )

    def _is_garbled(text: str) -> bool:
        if not text:
            return False
        bad = sum(
            1 for c in text
            if c == "\ufffd" or _ud.category(c) in ("Cs", "Co", "Cn")
        )
        return bad / len(text) > 0.3

    filtered = []
    for t in triples:
        if t.get("confidence", 0) < 0.3:
            continue
        head, tail = t.get("head", ""), t.get("tail", "")
        if len(head) < 4 or len(tail) < 4:
            continue
        if _noise_pattern.match(head.strip()) or _noise_pattern.match(tail.strip()):
            continue
        if _is_garbled(head) or _is_garbled(tail):
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

    # 收集所有实体（按 kg_name 去重），保留 procedure_type / spec_type / description
    entity_map: dict = {}
    for t in flat_triples:
        for side in ("head", "tail"):
            name  = t.get(side, "")
            etype = t.get(f"{side}_type", "") or "Part"
            if not name:
                continue
            if name not in entity_map:
                entity_map[name] = {
                    "label":          etype,
                    "procedure_type": t.get(f"{side}_procedure_type", ""),
                    "spec_type":      t.get(f"{side}_spec_type", ""),
                    "description":    t.get(f"{side}_description", ""),
                }
            else:
                if not entity_map[name]["procedure_type"]:
                    entity_map[name]["procedure_type"] = t.get(f"{side}_procedure_type", "")
                if not entity_map[name]["spec_type"]:
                    entity_map[name]["spec_type"] = t.get(f"{side}_spec_type", "")
                if not entity_map[name]["description"]:
                    entity_map[name]["description"] = t.get(f"{side}_description", "")

    kg_entity_types = {"Procedure", "Tool", "Specification", "Interface", "Part", "Assembly"}
    nodes_to_write = [
        {
            "kg_name":        name,
            "label":          info["label"] if info["label"] in kg_entity_types else "Part",
            "procedure_type": info["procedure_type"] or "unknown",
            "spec_type":      info["spec_type"] or "unknown",
            "description":    info["description"],
        }
        for name, info in entity_map.items()
    ]

    try:
        with driver.session() as session:
            # 写节点（按标签分组，Cypher 不支持动态标签参数）
            from collections import defaultdict
            by_label = defaultdict(list)
            for n in nodes_to_write:
                by_label[n["label"]].append(n)
            for label, node_list in by_label.items():
                try:
                    session.run(
                        f"""UNWIND $nodes AS n
                            MERGE (x:{label} {{kg_name: n.kg_name}})
                            SET x.procedure_type = CASE WHEN n.procedure_type IS NOT NULL AND n.procedure_type <> ''
                                                        THEN n.procedure_type
                                                        ELSE coalesce(x.procedure_type, 'unknown') END,
                                x.spec_type      = CASE WHEN n.spec_type IS NOT NULL AND n.spec_type <> ''
                                                        THEN n.spec_type
                                                        ELSE coalesce(x.spec_type, 'unknown') END,
                                x.description    = CASE WHEN n.description IS NOT NULL AND n.description <> ''
                                                        THEN n.description
                                                        ELSE coalesce(x.description, '') END
                        """,
                        nodes=node_list,
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
    对所有 flat_triples 中的 Part/Assembly 实体做四级对齐：
    0. 从实体文本提取内嵌零件号，直接查 BOM part_number 索引
    1a. 精确名称匹配（去除图号噪声后）
    1b. 双向子串匹配（min长度>=4）
    2. SequenceMatcher 模糊匹配（阈值0.75）
    3. Token 交集匹配（阈值0.60，min(A,B)作分母，防止泛化误匹配）
    写入 head_bom_id / tail_bom_id 字段。返回命中字段总数。
    """
    import re as _re
    from difflib import SequenceMatcher

    PART_TYPES = {"Part", "Assembly"}
    _STOP = {'the', 'a', 'an', 'and', 'or', 'for', 'of', 'to', 'in', 'at', 'on'}

    # ── BOM 双索引：名称 + 零件号 ─────────────────────────────────────
    bom_name_map: dict = {}   # lower_name → (orig_name, id)
    bom_pn_map:   dict = {}   # lower_part_number → id
    for e in bom_entities:
        name = e.get("name", "")
        bid  = e.get("id", "")
        pn   = e.get("part_number", "")
        if name and bid:
            bom_name_map[name.lower()] = (name, bid)
        if pn and bid:
            bom_pn_map[pn.lower()] = bid
    bom_lower_names = list(bom_name_map.keys())

    # ── 噪声清洗正则（图号/表号/see引用）───────────────────────────────
    _FIG_RE   = _re.compile(r'\s*\((?:Figure|Fig\.?|Table)\s+[\d\-]+[^\)]*\)', _re.IGNORECASE)
    _ITEMS_RE = _re.compile(r'\s*\(items?\s+[\d\s,and]+\)', _re.IGNORECASE)
    _SEE_RE   = _re.compile(r'\s*\(see\s+[^\)]+\)', _re.IGNORECASE)
    # 零件号模式：如 MS9556-07、AS3209-267、3034521
    _PN_RE    = _re.compile(r'\b([A-Z]{1,4}\d[\w\-]+|\d{5,}[\w\-]*)\b', _re.IGNORECASE)

    def _clean(text: str) -> str:
        text = _FIG_RE.sub('', text)
        text = _ITEMS_RE.sub('', text)
        text = _SEE_RE.sub('', text)
        return text.strip()

    def _token_match(key: str):
        tokens = set(_re.findall(r'[a-z]+', key)) - _STOP
        if len(tokens) < 2:
            return None
        best_score, best_id = 0.0, None
        for bn, (_, bid) in bom_name_map.items():
            bn_tokens = set(_re.findall(r'[a-z]+', bn)) - _STOP
            if not bn_tokens:
                continue
            overlap = len(tokens & bn_tokens) / min(len(tokens), len(bn_tokens))
            if overlap > best_score:
                best_score, best_id = overlap, bid
        return best_id if best_score >= 0.60 else None

    entity_cache: dict = {}

    def _lookup(text: str):
        raw_key = text.lower().strip()
        if raw_key in entity_cache:
            return entity_cache[raw_key]

        # 级别0：从实体文本提取内嵌零件号，直接查 part_number 索引
        for m in _PN_RE.finditer(text):
            pn_candidate = m.group(1).lower()
            if pn_candidate in bom_pn_map:
                entity_cache[raw_key] = bom_pn_map[pn_candidate]
                return entity_cache[raw_key]

        # 预处理：去除图号噪声再做名称匹配
        cleaned = _clean(text)
        key = cleaned.lower().strip()

        # 级别1a：精确匹配
        if key in bom_name_map:
            entity_cache[raw_key] = bom_name_map[key][1]
            return entity_cache[raw_key]

        # 级别1b：双向子串匹配（min长度>=4 防止误匹配）
        for bn, (_, bid) in bom_name_map.items():
            if bn and len(bn) >= 4 and len(key) >= 4:
                if bn in key or key in bn:
                    entity_cache[raw_key] = bid
                    return bid

        # 级别2：SequenceMatcher 模糊匹配（阈值0.75）
        best_r, best_id = 0.0, None
        for bn in bom_lower_names:
            r = SequenceMatcher(None, key, bn).ratio()
            if r > best_r:
                best_r, best_id = r, bom_name_map[bn][1]
        if best_r >= 0.75 and best_id:
            entity_cache[raw_key] = best_id
            return best_id

        # 级别3：Token 交集匹配（阈值0.60，min分母防止泛化）
        result = _token_match(key)
        if result:
            entity_cache[raw_key] = result
            return result

        entity_cache[raw_key] = None
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

    # 1. 文本提取（按文件类型分发）
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    try:
        if ext == "md":
            chunks, method = _extract_md_chunks(tmp_path)
        else:
            chunks, method = _extract_pdf_chunks(tmp_path, state)
    except Exception as e:
        yield {"type": "error", "message": f"文本提取失败：{e}"}
        return
    yield {"type": "log", "message": f"[Stage2] {method} 提取完成，共 {len(chunks)} 段"}

    if not chunks:
        yield {"type": "error", "message": "[Stage2] 无可提取文本，请检查文件内容"}
        return

    # 2. LLM KG 提取（直接循环，支持实时进度推送）
    from backend.pipelines.nodes_kg import (
        _is_procedure_text, _KG_EXTRACTION_PROMPT, _KG_GLEANING_PROMPT, _parse_kg_json,
        _build_prompt_with_bom,
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
        # ── BOM 速查表（一次性加载，循环内复用）─────────────────────────
        _bom_ents: list = []
        if stage_exists("bom"):
            _bom_data = read_stage("bom") or {}
            _bom_ents = _bom_data.get("entities", [])
        # ─────────────────────────────────────────────────────────────────
        for i, chunk in enumerate(proc_chunks):
            chunk_id = chunk.get("chunk_id", f"c{i}")
            ata_section = chunk.get("ata_section", "Unknown")
            text = chunk.get("text", "")[:1500]

            yield {"type": "log", "message": f"[Stage2] LLM提取第 {i+1}/{total} 段 — {ata_section}"}

            try:
                base_prompt = _KG_EXTRACTION_PROMPT.format(
                    ata_section=ata_section,
                    chunk_text=text,
                )
                prompt = _build_prompt_with_bom(base_prompt, _bom_ents)
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
        from backend.pipelines.kg_postprocess import enrich_bom_links as _enrich
        enrich_result = _enrich(flat_triples, bom_entities)
        es = enrich_result["stats"]
        enriched = es["regex_hits"] + es["cad_hits"] + es["keyword_hits"]
        yield {"type": "log", "message": (
            f"[Stage2] BOM 关联增强：{enriched}/{es['total']} 条三元组命中"
            f"（regex={es['regex_hits']}, cad={es['cad_hits']}, keyword={es['keyword_hits']}）"
        )}

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
    # ── HITL: 生成 StageReport ───────────────────────────────────────
    try:
        from backend.pipelines.kg_report import generate_stage_report
        from backend.kg_storage import (
            write_stage_report, write_stage_state, StageState,
            STAGE_REPORT_FILES,
        )
        current_data = read_stage("manual") or {}
        bom_data = read_stage("bom")
        report = generate_stage_report("manual", current_data, prev_data=None, bom_data=bom_data)
        write_stage_report("manual", report)
        write_stage_state("manual", StageState(stage="manual", status="awaiting_review"))
        yield {"type": "stage_report_ready", "stage": "manual", "issues_count": len(report.issues)}
    except Exception as e:
        yield {"type": "log", "message": f"[Report] 报告生成失败（不影响主流程）: {e}"}
    # ────────────────────────────────────────────────────────────────
    yield {"type": "done", "success": True}


# ─────────────────────────────────────────────
# POST /kg/stage2/manual
# ─────────────────────────────────────────────

@router.post("/stage2/manual", summary="阶段2：手册PDF/MD → 知识三元组（SSE）")
async def stage2_manual(
    request: Request,
    file: UploadFile = File(...),
    state: AppState = Depends(get_state),
):
    """
    上传手册 PDF 或 Markdown，使用 LLM 提取 KG 三元组并写 JSON。
    响应为 SSE 流。
    """
    neo4j_cfg = request.app.state.neo4j_cfg

    ext = (file.filename or "manual.pdf").rsplit(".", 1)[-1].lower()
    if ext not in ("pdf", "md"):
        from fastapi.responses import JSONResponse as _JR
        return _JR(status_code=400, content={"error": "仅支持 PDF 或 Markdown 文件"})

    content = await file.read()
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    filename = file.filename or f"manual.{ext}"

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

def _cad_data_to_flat_triples(assembly_tree, constraints, adjacency, source_file: str = ""):
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

    if source_file:
        for t in triples:
            t["cad_source_file"] = source_file

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

    flat_triples = _cad_data_to_flat_triples(
        assembly_tree, constraints, adjacency,
        source_file=os.path.basename(tmp_path),
    )
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
        # ── 拓扑结构对齐 hint ────────────────────────────────────────────
        from backend.pipelines.nodes_cad import _topology_align_cad_bom
        topo_map = _topology_align_cad_bom(assembly_tree, bom_entities_for_cad)
        for t in flat_triples:
            for field in ("head", "tail"):
                name = t.get(field, "")
                if name in topo_map and not t.get(f"{field}_bom_id"):
                    info = topo_map[name]
                    t[f"{field}_bom_id"]     = info["bom_id"]
                    t[f"{field}_bom_name"]   = info["bom_name"]
                    t[f"{field}_bom_method"] = "topology"
        topo_hits = sum(
            1 for t in flat_triples
            if t.get("head_bom_method") == "topology"
            or t.get("tail_bom_method") == "topology"
        )
        yield {"type": "log", "message": f"[Stage3] 拓扑对齐 hint：{topo_hits} 条三元组"}
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


# 内部生成器：阶段3 CAD 批量处理（多文件）
# ─────────────────────────────────────────────

def _stage3_cad_batch_gen(tmp_items: list, state: AppState, neo4j_cfg: dict):
    """
    tmp_items: [(tmp_path, orig_filename), ...]
    逐文件解析，合并三元组后统一 BOM 对齐并写 JSON。
    """
    yield {"type": "log", "message": f"[Stage3] 开始批量处理 {len(tmp_items)} 个 CAD 文件"}

    from backend.pipelines.nodes_cad import make_cad_nodes
    nodes = make_cad_nodes(state, neo4j_cfg)

    all_triples: list = []
    source_files: list = []

    for tmp_path, orig_name in tmp_items:
        yield {"type": "log", "message": f"[Stage3] 解析：{orig_name}"}
        result = nodes["parse_cad_step"]({"file_path": tmp_path, "file_ext": orig_name.rsplit(".", 1)[-1].lower()})
        if "error" in result:
            yield {"type": "log", "message": f"[Stage3] ⚠ {orig_name} 解析失败：{result['error']}，跳过"}
            continue
        for msg in result.get("log_messages", []):
            yield {"type": "log", "message": msg}

        assembly_tree = result.get("cad_assembly_tree", {})
        constraints   = result.get("cad_constraints", [])
        adjacency     = result.get("cad_adjacency", [])
        flat = _cad_data_to_flat_triples(
            assembly_tree, constraints, adjacency,
            source_file=orig_name,
        )
        all_triples.extend(flat)
        source_files.append(orig_name)
        yield {"type": "log", "message": f"[Stage3] {orig_name} → {len(flat)} 条三元组，累计 {len(all_triples)} 条"}

    if not all_triples:
        yield {"type": "error", "message": "[Stage3] 所有文件解析后无三元组"}
        return

    yield {"type": "log", "message": f"[Stage3] 生成 {len(all_triples)} 条扁平三元组（{len(source_files)} 个文件）"}

    # BOM 对齐（一次性，针对所有三元组）
    bom_entities_for_cad = []
    if stage_exists("bom"):
        bom_data = read_stage("bom")
        bom_entities_for_cad = (bom_data or {}).get("entities", [])

    if bom_entities_for_cad:
        cad_mapping = _align_cad_to_bom(all_triples, bom_entities_for_cad, state)
        method_dist: dict = {}
        for v in cad_mapping.values():
            m = v["method"]
            method_dist[m] = method_dist.get(m, 0) + 1
        hit = sum(1 for t in all_triples if t.get("head_bom_id") or t.get("tail_bom_id"))
        yield {"type": "log", "message": f"[Stage3] BOM 对齐命中 {hit} 个实体字段，方法分布：{method_dist}"}
        if not cad_mapping:
            yield {"type": "log", "message": "[Stage3] ⚠ CAD 零件命名对齐率有限"}
    else:
        yield {"type": "log", "message": "[Stage3] ⚠ 无BOM数据，跳过CAD对齐"}

    # 写中间产物 JSON
    output = {
        "generated_at":  datetime.now(timezone.utc).isoformat(),
        "source_files":  source_files,
        "triples":       all_triples,
        "stats": {
            "triples_count":  len(all_triples),
            "assembly_nodes": sum(1 for t in all_triples if t["relation"] == "isPartOf"),
            "constraints":    sum(1 for t in all_triples if t["relation"] in ("matesWith", "hasInterface", "constrainedBy")),
            "adjacency":      sum(1 for t in all_triples if t["relation"] == "adjacentTo"),
        },
    }
    write_stage("cad", output)
    yield {
        "type":          "result",
        "triples_count": len(all_triples),
        "stats":         output["stats"],
        "output_file":   STAGE_FILES["cad"],
    }
    yield {"type": "log", "message": f"[Stage3] 已写入：{STAGE_FILES['cad']}"}

    # 批量模式下跳过直写 Neo4j，统一由 Stage4 sync 接口同步
    yield {"type": "log", "message": "[Stage3] 批量模式：跳过直写 Neo4j，请通过「同步到 Neo4j」完成入库"}

    yield {"type": "done", "success": True}


# ─────────────────────────────────────────────
# POST /kg/stage3/cad
# ─────────────────────────────────────────────

@router.post("/stage3/cad", summary="阶段3：CAD 模型入库（SSE，支持多文件）")
async def stage3_cad(
    request: Request,
    files: List[UploadFile] = File(...),
    state: AppState = Depends(get_state),
):
    """
    上传一个或多个 STEP/STP 文件，提取装配树/配合约束/空间邻接并生成三元组。
    多文件时三元组合并写入 stage3_cad_triples.json。
    响应为 SSE 流。
    """
    neo4j_cfg = request.app.state.neo4j_cfg

    if not files:
        return JSONResponse(status_code=400, content={"error": "请至少上传一个 STEP/STP 文件"})

    # 校验所有文件扩展名
    for f in files:
        ext = (f.filename or "").rsplit(".", 1)[-1].lower()
        if ext not in ("step", "stp"):
            return JSONResponse(
                status_code=400,
                content={"error": f"不支持的文件格式：{ext}（{f.filename}），仅支持 STEP/STP"},
            )

    # 写所有临时文件
    tmp_items = []
    for upload_file in files:
        ext = (upload_file.filename or "file").rsplit(".", 1)[-1].lower()
        content = await upload_file.read()
        if not content:
            return JSONResponse(
                status_code=400,
                content={"error": f"文件 {upload_file.filename or 'unknown'} 内容为空"},
            )
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
            tmp.write(content)
            tmp_items.append((tmp.name, upload_file.filename or f"file.{ext}"))

    def cleanup_and_gen():
        try:
            yield from _stage3_cad_batch_gen(tmp_items, state, neo4j_cfg)
        finally:
            for tmp_path, _ in tmp_items:
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

            # 写 BOM 节点：kg_name 必须与 triple 的 head/tail 一致（含 pid 前缀），
            # 否则 _bom_df_to_entities_and_triples 生成的 head_label 在 MATCH 时找不到节点。
            # head_label 格式：f"{pid} {name}" if pid else name
            for e in entities:
                name = e.get("name", "")
                pid = (e.get("id") or e.get("part_number") or "").strip()
                if not name:
                    continue
                # 与 _bom_df_to_entities_and_triples L275 head_label 完全一致
                kg_name = f"{pid} {name}" if pid else name
                lbl = e.get("type", "Part")
                try:
                    session.run(
                        f"MERGE (n:{lbl} {{kg_name: $kg_name}}) "
                        "SET n.part_id = $pid, n.part_name = $name, "
                        "n.source = 'BOM', n.quantity = $qty",
                        kg_name=kg_name, pid=pid, name=name, qty=e.get("quantity", 1),
                    )
                    stats["bom_nodes"] += 1
                except Exception:
                    pass

            # 创建 ROOT 节点（用于装配树最顶层）
            try:
                session.run("MERGE (r:Assembly {kg_name: 'ROOT'}) SET r.source = 'BOM-virtual'")
            except Exception:
                pass

            # 写 BOM 关系：head/tail 直接是 head_label，节点 kg_name 已对齐
            for t in triples:
                head_name = (t.get("head") or "").strip()
                tail_name = (t.get("tail") or "").strip()
                rel = t.get("relation", "isPartOf")
                if not head_name or not tail_name:
                    continue
                # 仅允许已知 BOM 关系类型（避免注入）
                if rel not in ("isPartOf", "interchangesWith"):
                    continue
                try:
                    session.run(
                        f"""
                        MATCH (a {{kg_name: $h}})
                        MATCH (b {{kg_name: $t}})
                        MERGE (a)-[r:{rel}]->(b)
                        SET r.source = 'BOM'
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

            # ── BOM 关联增强 ──────────────────────────────────────────────────
            if bom_data:
                from backend.pipelines.kg_postprocess import enrich_bom_links as _enrich
                _er = _enrich(triples, bom_data.get("entities", []))
                _es = _er["stats"]
                _enriched = _es["regex_hits"] + _es["cad_hits"] + _es["keyword_hits"]
                _log.info(
                    f"[EnrichBOM] Manual: {_enriched}/{_es['total']} 命中 "
                    f"(regex={_es['regex_hits']}, cad={_es['cad_hits']}, keyword={_es['keyword_hits']})"
                )
                postprocess_stats["manual_bom_enrich"] = _es
            # ──────────────────────────────────────────────────────────────────

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


# ══════════════════════════════════════════════════════
# HITL 端点
# ══════════════════════════════════════════════════════

from fastapi import Body
from backend.pipelines.kg_report import generate_stage_report as _gen_report
from backend.kg_storage import (
    read_stage_report, write_stage_report,
    read_stage_state, write_stage_state, StageState,
    read_stage, write_stage,
)

_STAGE_SLUG = {"1": "bom", "2": "manual"}


def _resolve_stage(n: str) -> str:
    s = _STAGE_SLUG.get(n)
    if not s:
        from fastapi import HTTPException
        raise HTTPException(404, f"Stage {n} not supported for HITL")
    return s


@router.get("/stage{n}/report")
async def get_stage_report(n: str):
    stage = _resolve_stage(n)
    report = read_stage_report(stage)
    if report is None:
        data = read_stage(stage)
        if data is None:
            from fastapi import HTTPException
            raise HTTPException(404, "Stage data not found. Run the stage first.")
        bom_data = read_stage("bom") if stage == "manual" else None
        report = _gen_report(stage, data, prev_data=None, bom_data=bom_data)
        write_stage_report(stage, report)
    from dataclasses import asdict
    return asdict(report)


@router.post("/stage{n}/approve")
async def approve_stage(n: str):
    stage = _resolve_stage(n)
    from datetime import datetime, timezone
    state = StageState(
        stage=stage,
        status="approved",
        approved_at=datetime.now(timezone.utc).isoformat(),
    )
    write_stage_state(stage, state)
    return {"ok": True, "stage": stage, "status": "approved"}


@router.get("/stage{n}/state")
async def get_stage_state(n: str):
    stage = _resolve_stage(n)
    state = read_stage_state(stage)
    if state is None:
        return {"stage": stage, "status": "idle"}
    from dataclasses import asdict
    return asdict(state)


@router.get("/stage{n}/triples")
async def list_triples_hitl(n: str, offset: int = 0, limit: int = 50):
    stage = _resolve_stage(n)
    data = read_stage(stage)
    if data is None:
        from fastapi import HTTPException
        raise HTTPException(404, "Stage data not found")
    triples = data.get("triples", [])
    page = triples[offset: offset + limit]
    try:
        from backend.pipelines.kg_translate import translate_triples_batch
        page = translate_triples_batch([dict(t) for t in page])
    except Exception:
        pass
    return {"total": len(triples), "offset": offset, "limit": limit, "triples": page}


@router.patch("/stage{n}/triples/{idx}")
async def update_triple(n: str, idx: int, triple: dict = Body(...)):
    stage = _resolve_stage(n)
    data = read_stage(stage)
    if data is None or idx >= len(data.get("triples", [])):
        from fastapi import HTTPException
        raise HTTPException(404, "Triple not found")
    data["triples"][idx] = triple
    write_stage(stage, data)
    return {"ok": True, "updated": triple}


@router.delete("/stage{n}/triples/{idx}")
async def delete_triple_hitl(n: str, idx: int):
    stage = _resolve_stage(n)
    data = read_stage(stage)
    if data is None or idx >= len(data.get("triples", [])):
        from fastapi import HTTPException
        raise HTTPException(404, "Triple not found")
    removed = data["triples"].pop(idx)
    write_stage(stage, data)
    return {"ok": True, "removed": removed}


@router.post("/stage{n}/triples")
async def add_triple_hitl(n: str, triple: dict = Body(...)):
    stage = _resolve_stage(n)
    data = read_stage(stage)
    if data is None:
        from fastapi import HTTPException
        raise HTTPException(404, "Stage data not found")
    triple.setdefault("source", "expert")
    triple.setdefault("confidence", 1.0)
    data.setdefault("triples", []).append(triple)
    write_stage(stage, data)
    return {"ok": True, "added": triple, "total": len(data["triples"])}


@router.post("/stage{n}/diagnose")
async def diagnose_stage(n: str):
    stage = _resolve_stage(n)
    report = read_stage_report(stage)
    if report is None:
        from fastapi import HTTPException
        raise HTTPException(404, "No report found. Call /report first.")

    from backend.pipelines.kg_diagnose import diagnose_issues_stream
    import json as _json

    async def _gen():
        async for frame in diagnose_issues_stream(report):
            yield f"data: {_json.dumps(frame, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"

    from fastapi.responses import StreamingResponse
    return StreamingResponse(_gen(), media_type="text/event-stream")
