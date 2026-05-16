"""
backend/pipelines/nodes_kg.py — 知识图谱提取管道节点

make_kg_nodes(app_state, neo4j_cfg) -> dict

4 个 LangGraph 节点：
  extract_kg_triples  — LLM 从文本块提取实体和关系（7类节点×9类关系）
  align_entities      — 三级级联实体对齐（规则→模糊→语义向量）
  validate_kg_dag     — Kahn 算法检测 precedes 关系成环并修复
  write_kg_neo4j      — MERGE 叠加写入 Neo4j（保留现有 CHILD_OF 结构）

节点间通过 PipelineState 传递数据：
  kg_triples          ← extract_kg_triples 输出
  kg_aligned_triples  ← align_entities 输出
  kg_dag_valid        ← validate_kg_dag 输出
  kg_stats            ← write_kg_neo4j 输出
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import deque, defaultdict
from difflib import SequenceMatcher
from typing import Any


# ── 航空缩写词典（规则对齐第一级）────────────────────────────────────────────
AVIATION_ABBREV: dict = {
    # 模块缩写
    "HPC": "高压压气机",  "LPC": "低压压气机",
    "HPT": "高压涡轮",    "LPT": "低压涡轮",
    "CC":  "燃烧室",      "FC":  "火焰筒",
    "FAN": "风扇",        "AGB": "附件齿轮箱",
    # 零件类型
    "Blade":   "叶片",    "Disk":    "叶盘",
    "Vane":    "导向叶片","Casing":  "机匣",
    "Rotor":   "转子",    "Stator":  "静子",
    "Seal":    "封严环",  "Bearing": "轴承",
    "Shaft":   "轴",      "Nozzle":  "喷嘴",
    # 单位规范化
    "N.m": "N·m",         "Nm": "N·m",
}
# Stage_3 / Stage-3 / Stage3 用正则处理（见 _apply_abbreviations）


# ── KG 抽取 Prompt ────────────────────────────────────────────────────────────
_KG_EXTRACTION_PROMPT = """\
你是航空发动机装配领域的知识抽取专家。
严格按照以下本体抽取实体和关系，不得添加本体之外的类型。
输入文本可能为中文或英文。实体的 text 字段保留输入文本的原始语言（英文输入用英文，中文输入用中文）。

实体类型（6类）：
- Part：具体零部件（需有明确名称，如"高压压气机第3级叶片" 或 "Stage 3 compressor blade"）
- Assembly：含子零件的子系统（如"高压压气机" 或 "High Pressure Compressor"）
- Procedure：具体装配操作动作（如"插入叶片榫头" 或 "Insert blade dovetail"）；必须包含 procedure_type 字段，取值规则：上下文来自 Removal/Installation 章节 → "installation"；来自 Inspection/Check 章节 → "inspection"；来自 Approved Repairs 章节 → "repair"；无法判断 → "unknown"
- Tool：装配工具器具（如"扭力扳手" 或 "Torque wrench"）
- Specification：数值技术要求（必须含具体数值和单位，如"50N·m"、"0.05~0.12mm"）；必须包含 spec_type 字段，取值规则：来自安装章节的数值 → "assembly_tolerance"；来自检验章节的数值 → "service_limit"；来自修理章节的数值 → "rejection_limit"；无法判断 → "unknown"
- Interface：配合面或接口（如"榫头-榫槽配合" 或 "Dovetail interface"）

关系类型（5类）：
- precedes：工序A必须在工序B之前完成（head和tail都必须是Procedure）
- participatesIn：零件参与工序（head是Part/Assembly，tail是Procedure）
- requires：工序需要工具（head是Procedure，tail是Tool）
- specifiedBy：工序/接口受规范约束（head是Procedure/Interface，tail是Specification）
- matesWith：零件间存在配合关系（head和tail都是Part/Assembly）

字段要求：
- 实体字段：id（局部唯一字符串）、type、text（原文名称，保留原始语言）、description（1-2句说明该实体功能/作用/特征，不可为空）、procedure_type（仅 Procedure 实体必填）、spec_type（仅 Specification 实体必填）
- 关系字段：head（实体id）、tail（实体id）、type、weight（整数1-10，该关系的置信度和重要性，10为最高）

Few-shot示例1（中文工序链，来自 Installation 章节）：
文本：首先检查叶片榫头表面，确认无毛刺，然后将叶片榫头对准叶盘榫槽缓慢插入，最后用扭力扳手施加50N·m预紧扭矩。
{{"entities":[{{"id":"e1","type":"Procedure","text":"检查叶片榫头表面","description":"装配前检查叶片榫头表面质量，确认无毛刺、划伤等缺陷","procedure_type":"installation"}},{{"id":"e2","type":"Procedure","text":"插入叶片榫头至叶盘榫槽","description":"将叶片榫头对准叶盘榫槽缓慢插入的装配工序","procedure_type":"installation"}},{{"id":"e3","type":"Procedure","text":"施加预紧扭矩","description":"使用扭力扳手对叶片施加规定预紧扭矩，确保装配可靠性","procedure_type":"installation"}},{{"id":"e4","type":"Part","text":"叶片榫头","description":"叶片根部的榫形结构，用于嵌入叶盘榫槽实现固定"}},{{"id":"e5","type":"Tool","text":"扭力扳手","description":"可控制输出扭矩大小的专用装配工具"}},{{"id":"e6","type":"Specification","text":"50N·m","description":"预紧扭矩的规定数值，确保叶片装配后的夹紧力满足设计要求","spec_type":"assembly_tolerance"}}],"relations":[{{"head":"e1","tail":"e2","type":"precedes","weight":9}},{{"head":"e2","tail":"e3","type":"precedes","weight":9}},{{"head":"e4","tail":"e2","type":"participatesIn","weight":8}},{{"head":"e3","tail":"e5","type":"requires","weight":9}},{{"head":"e3","tail":"e6","type":"specifiedBy","weight":10}}]}}

Few-shot示例2（英文工序链，实体保留英文，来自 Installation 章节）：
文本：First inspect the blade dovetail surface for burrs. Then carefully insert the blade dovetail into the disk slot. Finally, apply 50 N·m torque using a torque wrench.
{{"entities":[{{"id":"e1","type":"Procedure","text":"Inspect blade dovetail surface","description":"Pre-assembly check of blade dovetail surface for burrs or defects","procedure_type":"installation"}},{{"id":"e2","type":"Procedure","text":"Insert blade dovetail into disk slot","description":"Carefully insert blade dovetail into disk slot during assembly","procedure_type":"installation"}},{{"id":"e3","type":"Procedure","text":"Apply torque","description":"Apply specified torque using torque wrench to secure blade","procedure_type":"installation"}},{{"id":"e4","type":"Part","text":"Blade dovetail","description":"Root of blade with dovetail shape for fitting into disk slot"}},{{"id":"e5","type":"Tool","text":"Torque wrench","description":"Specialized tool for applying precise torque values"}},{{"id":"e6","type":"Specification","text":"50 N·m","description":"Required torque value for blade assembly","spec_type":"assembly_tolerance"}}],"relations":[{{"head":"e1","tail":"e2","type":"precedes","weight":9}},{{"head":"e2","tail":"e3","type":"precedes","weight":9}},{{"head":"e4","tail":"e2","type":"participatesIn","weight":8}},{{"head":"e3","tail":"e5","type":"requires","weight":9}},{{"head":"e3","tail":"e6","type":"specifiedBy","weight":10}}]}}

Few-shot示例3（中文配合关系，来自 Inspection 章节）：
文本：高压压气机转子叶片通过榫头-榫槽配合安装在叶盘上，配合间隙为0.05~0.12mm。
{{"entities":[{{"id":"e1","type":"Part","text":"高压压气机转子叶片","description":"高压压气机级的旋转叶片，通过榫头安装在叶盘上，承受高温高压气流"}},{{"id":"e2","type":"Part","text":"叶盘","description":"压气机转子盘，盘缘设有榫槽用于安装叶片"}},{{"id":"e3","type":"Interface","text":"榫头-榫槽配合","description":"叶片榫头与叶盘榫槽之间的配合界面，是叶片固定的关键接口"}},{{"id":"e4","type":"Specification","text":"0.05~0.12mm","description":"榫头-榫槽配合间隙的允许范围，超出则影响装配质量","spec_type":"service_limit"}}],"relations":[{{"head":"e1","tail":"e2","type":"matesWith","weight":9}},{{"head":"e3","tail":"e4","type":"specifiedBy","weight":10}}]}}

Few-shot示例4（中文工具和规范，来自 Approved Repairs 章节）：
文本：使用T-205专用工具锁紧锁片，再用扭力扳手施加规定扭矩，分三次施加不得一次到位。
{{"entities":[{{"id":"e1","type":"Procedure","text":"锁紧锁片","description":"使用专用工具将锁片锁紧固定的装配工序","procedure_type":"repair"}},{{"id":"e2","type":"Procedure","text":"施加规定扭矩","description":"分三次用扭力扳手施加规定扭矩，不得一次到位","procedure_type":"repair"}},{{"id":"e3","type":"Tool","text":"T-205专用锁紧工具","description":"型号T-205的专用工具，用于锁紧锁片操作"}},{{"id":"e4","type":"Tool","text":"扭力扳手","description":"可控制输出扭矩大小的专用装配工具"}}],"relations":[{{"head":"e1","tail":"e2","type":"precedes","weight":9}},{{"head":"e1","tail":"e3","type":"requires","weight":10}},{{"head":"e2","tail":"e4","type":"requires","weight":10}}]}}

Few-shot示例5（英文含零件编号，实体保留完整编号，来自 Removal/Installation 章节）：
文本：Remove nuts (MS9767-09), washers and bolts (MS9556-07) securing ring halves to brackets. Apply torque 32 to 36 lb.in to mounting nuts.
{{"entities":[{{"id":"e1","type":"Procedure","text":"Remove nuts, washers and bolts securing ring halves to brackets","description":"Removal procedure for fasteners securing ring halves to mounting brackets","procedure_type":"installation"}},{{"id":"e2","type":"Procedure","text":"Apply torque to mounting nuts","description":"Torque application procedure for mounting nuts to specified range","procedure_type":"installation"}},{{"id":"e3","type":"Part","text":"Nut MS9767-09","description":"Mounting nut with part number MS9767-09 used to secure ring halves"}},{{"id":"e4","type":"Part","text":"Bolt MS9556-07","description":"Bolt with part number MS9556-07 used to fasten ring halves to brackets"}},{{"id":"e5","type":"Tool","text":"Torque wrench","description":"Calibrated torque wrench for applying specified torque to fasteners"}},{{"id":"e6","type":"Specification","text":"32-36 lb.in","description":"Required torque range for mounting nuts during assembly","spec_type":"assembly_tolerance"}}],"relations":[{{"head":"e1","tail":"e2","type":"precedes","weight":9}},{{"head":"e3","tail":"e1","type":"participatesIn","weight":8}},{{"head":"e4","tail":"e1","type":"participatesIn","weight":8}},{{"head":"e2","tail":"e5","type":"requires","weight":9}},{{"head":"e2","tail":"e6","type":"specifiedBy","weight":10}}]}}

【实体命名规则】（中英文均适用）
1. Part/Assembly 名称必须保留完整描述，禁止简化为 "Bolt"、"Nut"、"Washer"、"Ring" 等泛称
2. 若文本中出现零件编号（如 MS9556-07、SB1445），必须附加到名称中（格式："名称 编号"）
3. 命名示例：
   ✓ "Mounting bolt MS9556-07"  ✗ "Bolt"
   ✓ "Nut MS9767-09"            ✗ "Nut"
   ✓ "Center Fireseal Mount Ring" ✗ "Ring"
4. 图表编号（"Figure 201"、"Table 1"）、文件编号（"SB1445"单独出现）不得作为实体提取

当前文本块（ATA章节：{ata_section}）：
{chunk_text}

输出格式（严格JSON，不包含任何其他内容）："""



def _build_prompt_with_bom(base_prompt: str, bom_entities: list) -> str:
    """
    动态在 base_prompt 末尾追加 BOM 编号+名称速查表（≤80 条）。
    同时注入 [BOM:{零件号}] 打标指令，让 LLM 提取实体时直接标注 bom_id。
    """
    if not bom_entities:
        return base_prompt
    lines = []
    for e in bom_entities[:80]:
        pn   = e.get("part_number", "")
        name = e.get("name", "")
        if pn and name:
            lines.append(f"  {pn:<16} {name}")
        elif name:
            lines.append(f"  {'':16} {name}")
        elif pn:
            lines.append(f"  {pn:<16}")
    if not lines:
        return base_prompt
    section = (
        "\n\n【当前 BOM 零件编号速查表（按零件号或名称匹配）】\n"
        "提取实体时，若实体名称或文本中的零件编号能对应以下任一条目，\n"
        "请在该实体的 text 字段末尾加注 [BOM:{零件号}]，"
        "例如：\"Center Fireseal Mount Ring [BOM:3034521]\"。\n"
        "零件号列（左）      名称列（右）\n"
        + "\n".join(lines)
    )
    return base_prompt + section


# ── KG Gleaning（第二轮补全）Prompt ──────────────────────────────────────────
_KG_GLEANING_PROMPT = """\
上一轮从以下文本中提取了实体和关系，但可能有遗漏。
请仔细重新阅读文本，找出上一轮**未提取**的实体和关系，以补充形式返回。
实体的 text 字段保留输入文本的原始语言，不要翻译。

原始文本（ATA章节：{ata_section}）：
{chunk_text}

上一轮已提取的实体（仅供参考，不要重复）：
{existing_entities}

要求：
1. 只返回新发现的实体和关系，不要重复已有内容
2. 新实体的 id 从 g1 开始编号（区分第一轮的 e1、e2...）
3. 新关系的 head/tail 可以引用上一轮已有实体的 id，或本轮新实体的 id
4. 每个实体必须包含：id、type、text、description 字段
5. 每条关系必须包含：head、tail、type、weight 字段
6. 若确认无遗漏，返回：{{"entities":[],"relations":[]}}

实体类型限制：Part / Assembly / Procedure / Tool / Specification / Interface
关系类型限制：precedes / participatesIn / requires / specifiedBy / matesWith / hasInterface / constrainedBy

输出格式（严格JSON，不包含任何其他内容）："""


# ── 过滤关键词（判断是否为装配相关文本）────────────────────────────────────
_PROCEDURE_KEYWORDS = [
    "装配", "安装", "拆卸", "步骤", "工序", "程序",
    "拧紧", "扭矩", "间隙", "公差", "工具", "工装",
    "锁紧", "对准", "插入", "施加", "检查", "确认",
    "拆下", "卸下", "清洗", "涂抹", "润滑",
]

_PROCEDURE_KEYWORDS_EN = [
    "install", "remove", "assemble", "disassemble", "procedure", "step",
    "torque", "clearance", "tolerance", "tighten", "loosen", "inspect",
    "apply", "lubricate", "align", "insert", "attach", "detach",
    "fasten", "secure", "check", "verify", "replace", "clean",
    "tool", "fixture", "nut", "bolt", "screw", "washer", "seal",
    "n·m", "ft·lb", "in·lb", "warning", "caution",
]

VALID_ENTITY_TYPES = {
    "Part", "Assembly", "Procedure", "Tool", "Specification", "Interface"
}
VALID_RELATION_TYPES = {
    "precedes", "participatesIn", "requires", "specifiedBy",
    "matesWith", "hasInterface", "constrainedBy",
}

# Neo4j 标签映射
_LABEL_MAP = {
    "Part": "Part",
    "Assembly": "Assembly",
    "Procedure": "Procedure",
    "Tool": "Tool",
    "Specification": "Specification",
    "Interface": "Interface",
    "GeoConstraint": "GeoConstraint",
}


# ── 工具函数 ─────────────────────────────────────────────────────────────────

def _is_procedure_text(text: str) -> bool:
    """判断文本块是否包含装配/工序相关内容（支持中英文）。"""
    text_lower = text.lower()
    return (
        any(kw in text for kw in _PROCEDURE_KEYWORDS)
        or any(kw in text_lower for kw in _PROCEDURE_KEYWORDS_EN)
    )


def _apply_abbreviations(text: str) -> str:
    """展开航空缩写，规范化文本用于对齐匹配。"""
    result = text
    for abbrev, full in AVIATION_ABBREV.items():
        result = result.replace(abbrev, full)
    result = re.sub(r"Stage[-_]?(\d+)", r"第\1级", result, flags=re.IGNORECASE)
    result = re.sub(r"\bS(\d+)\b", r"第\1级", result)
    return result


def _make_entity_id(chunk_id: str, local_id: str, entity_type: str) -> str:
    """生成全局唯一实体 ID（避免跨块冲突）。"""
    raw = f"{chunk_id}_{local_id}_{entity_type}"
    return hashlib.md5(raw.encode()).hexdigest()[:12]


def _parse_kg_json(raw: str, chunk_id: str) -> dict | None:
    """解析并校验 LLM 输出的 KG JSON。description 和 weight 为可选字段，缺失时补默认值。"""
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        return None
    try:
        data = json.loads(match.group())
    except json.JSONDecodeError:
        return None

    entities = data.get("entities", [])
    relations = data.get("relations", [])
    if not isinstance(entities, list) or not isinstance(relations, list):
        return None

    valid_entities = []
    for e in entities:
        if e.get("type") in VALID_ENTITY_TYPES and e.get("id") and e.get("text"):
            # description 可选：缺失时补空字符串，保证下游可无条件访问
            if not e.get("description"):
                e["description"] = ""
            valid_entities.append(e)

    entity_ids = {e["id"] for e in valid_entities}
    valid_relations = []
    for r in relations:
        if (r.get("type") in VALID_RELATION_TYPES
                and r.get("head") in entity_ids
                and r.get("tail") in entity_ids):
            # weight 可选：缺失时默认 5，存在时强转 int 并裁剪到 [1, 10]
            if "weight" not in r:
                r["weight"] = 5
            else:
                try:
                    r["weight"] = max(1, min(10, int(r["weight"])))
                except (TypeError, ValueError):
                    r["weight"] = 5
            valid_relations.append(r)

    if not valid_entities:
        return None
    return {
        "entities": valid_entities,
        "relations": valid_relations,
        "chunk_id": chunk_id,
    }


def _kahn_detect_cycle(nodes: list, edges: list) -> list:
    """Kahn 算法检测有向图中的环，返回成环节点列表（空列表=无环）。"""
    in_degree: dict = defaultdict(int)
    adj: dict = defaultdict(list)
    node_set = set(nodes)

    for u, v in edges:
        if u in node_set and v in node_set:
            adj[u].append(v)
            in_degree[v] += 1

    queue = deque([n for n in node_set if in_degree[n] == 0])
    visited = 0
    while queue:
        node = queue.popleft()
        visited += 1
        for neighbor in adj[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if visited == len(node_set):
        return []
    return [n for n in node_set if in_degree[n] > 0]


def _init_kg_constraints(session) -> None:
    """初始化 KG 扩展节点类型的唯一约束（幂等）。"""
    for label in ("Procedure", "Tool", "Specification", "Interface", "GeoConstraint"):
        try:
            session.run(
                f"CREATE CONSTRAINT IF NOT EXISTS FOR (n:{label}) REQUIRE n.kg_id IS UNIQUE"
            )
        except Exception:
            pass

    # === 联合KG构建：gid 全局唯一约束（幂等） ===
    for label in ("Part", "Assembly", "Procedure", "Tool", "Specification", "Interface"):
        try:
            session.run(
                f"CREATE CONSTRAINT IF NOT EXISTS FOR (n:{label}) REQUIRE n.gid IS UNIQUE"
            )
        except Exception:
            pass

    # === 实体名称全文索引（跨源模糊检索用） ===
    try:
        session.run(
            "CREATE FULLTEXT INDEX entity_name_idx IF NOT EXISTS "
            "FOR (n:Part|Assembly|Procedure|Tool) "
            "ON EACH [n.part_name, n.kg_name, n.cad_part_name]"
        )
    except Exception:
        pass


def _write_kg_nodes_batch(session, batch: list) -> None:
    """批量 MERGE 写入 KG 节点（按标签分组，因为 Cypher 不支持动态标签参数）。"""
    by_type: dict = defaultdict(list)
    for node in batch:
        by_type[node["type"]].append(node)

    for ntype, nodes in by_type.items():
        label = _LABEL_MAP.get(ntype, ntype)
        cypher = f"""
            UNWIND $nodes AS n
            MERGE (x:{label} {{kg_id: n.global_id}})
            SET x.kg_name          = n.text,
                x.ata_section      = n.ata_section,
                x.source_chunk_id  = n.source_chunk_id,
                x.aligned_part_id  = n.aligned_part_id,
                x.alignment_method = n.alignment_method,
                x.gid              = coalesce(n.gid, n.global_id),
                x.bom_part_id      = n.bom_part_id,
                x.cad_part_name    = n.cad_part_name,
                x.sources          = coalesce(x.sources, []) + [n.source],
                x.description      = CASE WHEN n.description IS NOT NULL AND n.description <> ''
                                          THEN n.description
                                          ELSE coalesce(x.description, '')
                                     END,
                x.procedure_type   = CASE WHEN n.procedure_type IS NOT NULL AND n.procedure_type <> ''
                                          THEN n.procedure_type
                                          ELSE coalesce(x.procedure_type, 'unknown')
                                     END,
                x.spec_type        = CASE WHEN n.spec_type IS NOT NULL AND n.spec_type <> ''
                                          THEN n.spec_type
                                          ELSE coalesce(x.spec_type, 'unknown')
                                     END
        """
        session.run(cypher, nodes=nodes)


def _write_kg_relations_batch(session, batch: list) -> None:
    """批量 MERGE 写入 KG 关系。"""
    by_type: dict = defaultdict(list)
    for rel in batch:
        by_type[rel["type"]].append(rel)

    cypher_map = {
        "precedes": """
            UNWIND $rels AS r
            MATCH (a:Procedure {kg_id: r.from_id})
            MATCH (b:Procedure {kg_id: r.to_id})
            MERGE (a)-[rel:precedes]->(b)
            SET rel.weight = CASE WHEN rel.weight IS NULL
                                  THEN r.weight
                                  ELSE toInteger((rel.weight + r.weight) / 2)
                             END
        """,
        "participatesIn": """
            UNWIND $rels AS r
            MATCH (a {kg_id: r.from_id})
            MATCH (b:Procedure {kg_id: r.to_id})
            MERGE (a)-[rel:participatesIn]->(b)
            SET rel.weight = CASE WHEN rel.weight IS NULL
                                  THEN r.weight
                                  ELSE toInteger((rel.weight + r.weight) / 2)
                             END
        """,
        "requires": """
            UNWIND $rels AS r
            MATCH (a:Procedure {kg_id: r.from_id})
            MATCH (b:Tool {kg_id: r.to_id})
            MERGE (a)-[rel:requires]->(b)
            SET rel.weight = CASE WHEN rel.weight IS NULL
                                  THEN r.weight
                                  ELSE toInteger((rel.weight + r.weight) / 2)
                             END
        """,
        "specifiedBy": """
            UNWIND $rels AS r
            MATCH (a {kg_id: r.from_id})
            MATCH (b:Specification {kg_id: r.to_id})
            MERGE (a)-[rel:specifiedBy]->(b)
            SET rel.weight = CASE WHEN rel.weight IS NULL
                                  THEN r.weight
                                  ELSE toInteger((rel.weight + r.weight) / 2)
                             END
        """,
        "matesWith": """
            UNWIND $rels AS r
            MATCH (a {kg_id: r.from_id})
            MATCH (b {kg_id: r.to_id})
            MERGE (a)-[rel:matesWith]->(b)
            SET rel.weight = CASE WHEN rel.weight IS NULL
                                  THEN r.weight
                                  ELSE toInteger((rel.weight + r.weight) / 2)
                             END
        """,
        "hasInterface": """
            UNWIND $rels AS r
            MATCH (a {kg_id: r.from_id})
            MATCH (b:Interface {kg_id: r.to_id})
            MERGE (a)-[rel:hasInterface]->(b)
            SET rel.weight = CASE WHEN rel.weight IS NULL
                                  THEN r.weight
                                  ELSE toInteger((rel.weight + r.weight) / 2)
                             END
        """,
        "constrainedBy": """
            UNWIND $rels AS r
            MATCH (a:Interface {kg_id: r.from_id})
            MATCH (b:GeoConstraint {kg_id: r.to_id})
            MERGE (a)-[rel:constrainedBy]->(b)
            SET rel.weight = CASE WHEN rel.weight IS NULL
                                  THEN r.weight
                                  ELSE toInteger((rel.weight + r.weight) / 2)
                             END
        """,
    }

    for rtype, rels in by_type.items():
        cypher = cypher_map.get(rtype)
        if cypher:
            try:
                session.run(cypher, rels=rels)
            except Exception:
                pass


def _write_kg_relations_batch_unified(session, batch: list) -> None:
    """
    批量写入联合 KG 的关系，兼容 isPartOf / matesWith / adjacentTo 等新类型。
    旧类型（precedes 等）委托给原 _write_kg_relations_batch。
    新类型通过 gid 定位节点（不再限定标签）。
    """
    new_types = {"isPartOf", "adjacentTo"}
    old_rels, new_rels_by_type = [], defaultdict(list)

    for rel in batch:
        if rel["type"] in new_types:
            new_rels_by_type[rel["type"]].append(rel)
        else:
            old_rels.append(rel)

    # 旧类型走原路径（使用 kg_id 匹配）
    if old_rels:
        _write_kg_relations_batch(session, old_rels)

    # isPartOf —— 使用 gid 或 kg_id 定位
    for rtype, rels in new_rels_by_type.items():
        if rtype == "isPartOf":
            try:
                session.run("""
                    UNWIND $rels AS r
                    MATCH (a) WHERE a.gid = r.from_id OR a.kg_id = r.from_id
                    MATCH (b) WHERE b.gid = r.to_id   OR b.kg_id = r.to_id
                    MERGE (a)-[:isPartOf]->(b)
                """, rels=rels)
            except Exception:
                pass
        elif rtype == "adjacentTo":
            try:
                session.run("""
                    UNWIND $rels AS r
                    MATCH (a) WHERE a.gid = r.from_id OR a.kg_id = r.from_id
                    MATCH (b) WHERE b.gid = r.to_id   OR b.kg_id = r.to_id
                    MERGE (a)-[rel:adjacentTo]->(b)
                    SET rel.gap_mm = coalesce(r.rel_props.gap_mm, 0)
                """, rels=rels)
            except Exception:
                pass


def _write_kg_represents_edges(session, nodes: list) -> None:
    """为对齐成功的 KG 节点创建 BOM→KG 的 REPRESENTED_BY 图边。"""
    aligned = [n for n in nodes if n.get("aligned_part_id")]
    if not aligned:
        return
    try:
        session.run("""
            UNWIND $nodes AS n
            MATCH (kg_node {kg_id: n.global_id})
            MATCH (bom_node {part_id: n.aligned_part_id})
            MERGE (bom_node)-[:REPRESENTED_BY]->(kg_node)
        """, nodes=aligned)
    except Exception:
        pass


# ── 主工厂函数 ────────────────────────────────────────────────────────────────

def make_kg_nodes(app_state: Any, neo4j_cfg: dict) -> dict:
    """
    工厂函数：创建 KG 提取管道所有节点，通过闭包绑定 app_state 和 neo4j_cfg。

    Returns:
        dict — {节点名: 节点函数}
    """
    # 统一检查 neo4j 包可用性（比各节点内部重复 import 更清晰）
    try:
        from neo4j import GraphDatabase as _Neo4jGD  # noqa: F401
        _neo4j_available = True
    except ImportError:
        _neo4j_available = False

    def extract_kg_triples(state: dict) -> dict:
        """节点1：LLM 从文本块提取实体和关系三元组。"""
        chunks = state.get("manual_chunks") or state.get("text_chunks") or []
        proc_chunks = [c for c in chunks if _is_procedure_text(c.get("text", ""))]

        if not proc_chunks:
            return {
                "kg_triples": [],
                "log_messages": ["[KG] 无装配相关文本块，跳过知识抽取"],
                "current_node": "extract_kg_triples",
            }

        # 侧信道进度推送：每处理一个 chunk 立即通知前端，无需等待整个节点完成
        def _push(msg: str):
            q = getattr(app_state, "_ingest_progress_q", None)
            if q is not None:
                q.put(("log", msg))

        total = len(proc_chunks)
        all_triples = []
        errors = 0

        _push(f"[KG] 开始知识抽取：共 {total} 个装配相关文本块")

        for i, chunk in enumerate(proc_chunks):
            chunk_id = chunk.get("id") or chunk.get("doc_id") or ""
            ata_section = (
                chunk.get("ata_section")
                or chunk.get("section_title")
                or "未知章节"
            )
            text = chunk.get("text", "")
            chunk_text_truncated = text[:1500]

            _push(f"[KG] 第 {i+1}/{total} 块 — {ata_section[:40]}")

            _bom_ents = list((state.get("bom_entities") or {}).values()) \
                if isinstance(state.get("bom_entities"), dict) \
                else (state.get("bom_entities") or [])
            _base_prompt = _KG_EXTRACTION_PROMPT.format(
                ata_section=ata_section,
                chunk_text=chunk_text_truncated,
            )
            prompt = _build_prompt_with_bom(_base_prompt, _bom_ents)

            try:
                # ── 第一轮：初始提取 ──────────────────────────────────────────
                resp1 = app_state.llm_client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                )
                raw1 = resp1.choices[0].message.content or ""
                parsed1 = _parse_kg_json(raw1, chunk_id)

                if not parsed1:
                    errors += 1
                    _push(f"[KG] ⚠ 第 {i+1}/{total} 块解析失败，跳过")
                    continue

                # ── 第二轮：Gleaning 补全 ─────────────────────────────────────
                existing_summary = json.dumps(
                    [{"id": e["id"], "type": e["type"], "text": e["text"]}
                     for e in parsed1["entities"]],
                    ensure_ascii=False,
                )
                gleaning_prompt = _KG_GLEANING_PROMPT.format(
                    ata_section=ata_section,
                    chunk_text=chunk_text_truncated,
                    existing_entities=existing_summary,
                )

                parsed2 = None
                try:
                    resp2 = app_state.llm_client.chat.completions.create(
                        messages=[{"role": "user", "content": gleaning_prompt}],
                        temperature=0.1,
                    )
                    raw2 = resp2.choices[0].message.content or ""
                    parsed2 = _parse_kg_json(raw2, chunk_id)
                except Exception:
                    pass  # 第二轮失败不影响第一轮结果

                # ── 合并两轮结果 ──────────────────────────────────────────────
                if parsed2 and (parsed2["entities"] or parsed2["relations"]):
                    existing_keys = {
                        (e["text"], e["type"]) for e in parsed1["entities"]
                    }
                    new_entities = [
                        e for e in parsed2["entities"]
                        if (e["text"], e["type"]) not in existing_keys
                    ]
                    all_entity_ids = (
                        {e["id"] for e in parsed1["entities"]}
                        | {e["id"] for e in new_entities}
                    )
                    new_relations = [
                        r for r in parsed2["relations"]
                        if r.get("head") in all_entity_ids
                        and r.get("tail") in all_entity_ids
                    ]
                    merged = {
                        "entities":    parsed1["entities"] + new_entities,
                        "relations":   parsed1["relations"] + new_relations,
                        "chunk_id":    chunk_id,
                        "ata_section": ata_section,
                    }
                    all_triples.append(merged)
                    _push(
                        f"[KG] ✅ 第 {i+1}/{total} 块完成，"
                        f"实体 {len(merged['entities'])} 个，"
                        f"关系 {len(merged['relations'])} 条"
                    )
                else:
                    parsed1["ata_section"] = ata_section
                    all_triples.append(parsed1)
                    _push(
                        f"[KG] ✅ 第 {i+1}/{total} 块完成，"
                        f"实体 {len(parsed1['entities'])} 个，"
                        f"关系 {len(parsed1['relations'])} 条"
                    )

            except Exception:
                errors += 1
                _push(f"[KG] ⚠ 第 {i+1}/{total} 块提取失败")

        # 合并视觉抽取的三元组（若有）
        visual = state.get("visual_kg_triples") or []
        if visual:
            all_triples.extend(visual)

        return {
            "kg_triples": all_triples,
            "log_messages": [
                f"[KG] 知识抽取完成：文本 {len(proc_chunks)} 块，"
                f"成功 {len(all_triples) - len(visual)} 个，"
                f"视觉补充 {len(visual)} 个，失败 {errors} 个"
            ],
            "current_node": "extract_kg_triples",
        }

    def align_entities(state: dict) -> dict:
        """节点2：三级级联实体对齐（规则→模糊→语义向量）。"""
        kg_triples = state.get("kg_triples") or []
        if not kg_triples:
            return {
                "kg_aligned_triples": [],
                "log_messages": ["[KG] 无三元组需要对齐"],
                "current_node": "align_entities",
            }

        # 从 Neo4j 拉取所有 BOM 零件名（用于对齐）
        bom_name_to_id: dict = {}
        try:
            from neo4j import GraphDatabase
            driver = GraphDatabase.driver(
                neo4j_cfg.get("uri", "bolt://localhost:7687"),
                auth=(neo4j_cfg.get("user", "neo4j"), neo4j_cfg.get("pass", "neo4j")),
            )
            with driver.session() as session:
                rows = session.run(
                    "MATCH (n) WHERE n.part_name IS NOT NULL AND n.part_id IS NOT NULL "
                    "RETURN n.part_name AS name, n.part_id AS pid"
                ).data()
                bom_name_to_id = {r["name"]: r["pid"] for r in rows}
            driver.close()
        except Exception:
            bom_name_to_id = {}

        bom_names = list(bom_name_to_id.keys())
        stats: dict = {"rule": 0, "fuzzy": 0, "semantic": 0, "unmatched": 0}

        aligned_triples = []
        for triple in kg_triples:
            aligned_entities = []
            for entity in triple.get("entities", []):
                text = entity.get("text", "")
                expanded = _apply_abbreviations(text)

                pid, method = None, "unmatched"

                # 第一级：规则对齐
                if expanded in bom_name_to_id:
                    pid, method = bom_name_to_id[expanded], "rule"
                elif bom_names:
                    # 第二级：模糊对齐（difflib，标准库，无需新依赖）
                    best_ratio, best_name = 0.0, ""
                    for name in bom_names:
                        ratio = SequenceMatcher(None, expanded, name).ratio()
                        if ratio > best_ratio:
                            best_ratio, best_name = ratio, name
                    if best_ratio >= 0.85 and best_name:
                        pid, method = bom_name_to_id[best_name], "fuzzy"
                    elif best_ratio < 0.70:
                        # 第三级：语义对齐（查 Qdrant 已有 text_vec）
                        try:
                            vecs = app_state.embedding_mgr.encode_text([expanded])
                            results = app_state.qdrant_client.query_points(
                                collection_name="rag_knowledge",
                                query=vecs[0].tolist(),
                                using="text_vec",
                                limit=1,
                                with_payload=["text"],
                            )
                            if results.points:
                                hit_text = results.points[0].payload.get("text", "")
                                for bname in bom_names:
                                    if bname in hit_text:
                                        pid, method = bom_name_to_id[bname], "semantic"
                                        break
                        except Exception:
                            pass

                stats[method if method in stats else "unmatched"] += 1
                aligned_entity = dict(entity)
                aligned_entity["aligned_part_id"] = pid
                aligned_entity["alignment_method"] = method
                aligned_entity["global_id"] = _make_entity_id(
                    triple.get("chunk_id", ""), entity["id"], entity["type"]
                )
                aligned_entities.append(aligned_entity)

            aligned_triple = dict(triple)
            aligned_triple["entities"] = aligned_entities
            aligned_triples.append(aligned_triple)

        total = sum(stats.values()) or 1
        rate_str = ", ".join(f"{k}:{v/total:.0%}" for k, v in stats.items())
        return {
            "kg_aligned_triples": aligned_triples,
            "log_messages": [f"[KG] 实体对齐完成：{rate_str}"],
            "current_node": "align_entities",
        }

    def verify_kg_entities(state: dict) -> dict:
        """节点2.5：三级验证——BOM 对齐存在性 + ATA 一致性 + 关系权重置信度。"""
        triples = state.get("kg_aligned_triples") or state.get("kg_triples") or []
        if not triples:
            return {
                "kg_verification_report": {
                    "total": 0, "verified": 0, "low_conf": 0,
                    "inconsistent": 0, "details": [],
                },
                "log_messages": ["[KG] 无三元组，跳过验证"],
                "current_node": "verify_kg_entities",
            }

        # 从 Neo4j 拉取 BOM 权威 part_id 集合（Level 1 验证用）
        bom_part_ids: set = set()
        try:
            from neo4j import GraphDatabase
            driver = GraphDatabase.driver(
                neo4j_cfg.get("uri", "bolt://localhost:7687"),
                auth=(neo4j_cfg.get("user", "neo4j"), neo4j_cfg.get("pass", "neo4j")),
            )
            with driver.session() as session:
                rows = session.run(
                    "MATCH (n) WHERE n.part_id IS NOT NULL RETURN n.part_id AS pid"
                ).data()
                bom_part_ids = {r["pid"] for r in rows}
            driver.close()
        except Exception:
            pass

        total = 0
        verified = 0
        low_conf = 0
        inconsistent = 0
        details = []

        for triple in triples:
            entity_map = {e["id"]: e for e in triple.get("entities", [])}
            relations = triple.get("relations", [])

            # 计算每个实体参与关系的平均 weight（Level 3）
            entity_rel_weights: dict = defaultdict(list)
            for rel in relations:
                w = rel.get("weight", 5)
                entity_rel_weights[rel["head"]].append(w)
                entity_rel_weights[rel["tail"]].append(w)

            for entity in triple.get("entities", []):
                total += 1
                eid = entity["id"]
                aligned_pid = entity.get("aligned_part_id")
                ata = entity.get("ata_section") or triple.get("ata_section", "")
                flags = []
                confidence = 0.0

                # Level 1：BOM 对齐存在性
                if aligned_pid:
                    if aligned_pid in bom_part_ids:
                        confidence += 0.4
                        verified += 1
                    else:
                        flags.append("bom_not_found")
                        inconsistent += 1

                # Level 2：ATA 章节一致性（仅 Procedure 实体）
                if entity.get("type") == "Procedure" and ata:
                    # 查找该 Procedure 参与的零件的 ata_section
                    part_atas = set()
                    for rel in relations:
                        if rel.get("tail") == eid and rel.get("type") == "participatesIn":
                            part_e = entity_map.get(rel["head"], {})
                            part_ata = part_e.get("ata_section", "")
                            if part_ata:
                                part_atas.add(part_ata[:5])  # 比较前5位（如"72.00"）
                    if part_atas and ata[:5] not in part_atas:
                        flags.append("ata_mismatch")
                        confidence -= 0.2
                    else:
                        confidence += 0.3

                # Level 3：关系权重置信度
                weights = entity_rel_weights.get(eid, [])
                if weights:
                    avg_w = sum(weights) / len(weights)
                    confidence += 0.3 * (avg_w / 10.0)

                confidence = round(max(0.0, min(1.0, confidence)), 3)
                if confidence < 0.5:
                    low_conf += 1
                    details.append({
                        "kg_id":      entity.get("global_id", eid),
                        "kg_name":    entity.get("text", ""),
                        "type":       entity.get("type", ""),
                        "confidence": confidence,
                        "flags":      flags,
                    })

        report = {
            "total":        total,
            "verified":     verified,
            "low_conf":     low_conf,
            "inconsistent": inconsistent,
            "details":      details,
        }
        rate = f"{verified}/{total}" if total else "0/0"
        return {
            "kg_verification_report": report,
            "log_messages": [
                f"[KG] 验证完成：{rate} 实体与 BOM 对齐，"
                f"低置信度 {low_conf} 个，不一致 {inconsistent} 个"
            ],
            "current_node": "verify_kg_entities",
        }

    def validate_kg_dag(state: dict) -> dict:
        """节点3：Kahn 算法检测 precedes 关系是否成环，成环则移除成环边。"""
        triples = state.get("kg_aligned_triples") or state.get("kg_triples") or []
        if not triples:
            return {
                "kg_dag_valid": True,
                "log_messages": ["[KG] 无三元组，跳过 DAG 校验"],
                "current_node": "validate_kg_dag",
            }

        # 收集所有 precedes 边（使用 global_id）
        proc_nodes: set = set()
        precedes_edges: list = []
        for triple in triples:
            entity_map = {e["id"]: e for e in triple.get("entities", [])}
            for rel in triple.get("relations", []):
                if rel["type"] == "precedes":
                    h_e = entity_map.get(rel["head"], {})
                    t_e = entity_map.get(rel["tail"], {})
                    h_id = h_e.get("global_id") or rel["head"]
                    t_id = t_e.get("global_id") or rel["tail"]
                    proc_nodes.update([h_id, t_id])
                    precedes_edges.append((h_id, t_id))

        if not precedes_edges:
            return {
                "kg_dag_valid": True,
                "log_messages": ["[KG] 无 precedes 关系，DAG 校验通过"],
                "current_node": "validate_kg_dag",
            }

        cycle_nodes = _kahn_detect_cycle(list(proc_nodes), precedes_edges)
        if not cycle_nodes:
            return {
                "kg_dag_valid": True,
                "log_messages": [
                    f"[KG] DAG 校验通过，precedes 关系数：{len(precedes_edges)}"
                ],
                "current_node": "validate_kg_dag",
            }

        # 有环：移除涉及成环节点的 precedes 关系
        cycle_set = set(cycle_nodes)
        removed = 0
        for triple in triples:
            entity_map = {e["id"]: e for e in triple.get("entities", [])}
            filtered = []
            for rel in triple.get("relations", []):
                if rel["type"] == "precedes":
                    h_id = (entity_map.get(rel["head"], {}).get("global_id")
                            or rel["head"])
                    t_id = (entity_map.get(rel["tail"], {}).get("global_id")
                            or rel["tail"])
                    if h_id in cycle_set or t_id in cycle_set:
                        removed += 1
                        continue
                filtered.append(rel)
            triple["relations"] = filtered

        return {
            "kg_dag_valid": False,
            "log_messages": [
                f"[KG] DAG 发现 {len(cycle_nodes)} 个成环节点，已移除 {removed} 条 precedes 关系"
            ],
            "current_node": "validate_kg_dag",
        }

    def write_kg_neo4j(state: dict) -> dict:
        """节点4：将对齐后的三元组 MERGE 写入 Neo4j（叠加在现有 CHILD_OF 之上）。"""
        triples = state.get("kg_aligned_triples") or state.get("kg_triples") or []
        if not triples:
            return {
                "kg_stats": {"nodes": 0, "relations": 0, "errors": 0},
                "log_messages": ["[KG] 无三元组，跳过写入"],
                "current_node": "write_kg_neo4j",
            }

        try:
            from neo4j import GraphDatabase
            driver = GraphDatabase.driver(
                neo4j_cfg.get("uri", "bolt://localhost:7687"),
                auth=(neo4j_cfg.get("user", "neo4j"), neo4j_cfg.get("pass", "neo4j")),
            )
        except Exception as e:
            return {
                "kg_stats": {"nodes": 0, "relations": 0, "errors": 1},
                "log_messages": [f"[KG] Neo4j 连接失败：{e}"],
                "current_node": "write_kg_neo4j",
                "error": str(e),
            }

        nodes_written = 0
        relations_written = 0
        errors = 0

        try:
            with driver.session() as session:
                _init_kg_constraints(session)

                # 收集所有节点和关系
                all_nodes: list = []
                all_relations: list = []

                for triple in triples:
                    entity_map = {e["id"]: e for e in triple.get("entities", [])}
                    chunk_id = triple.get("chunk_id", "")
                    ata_section = triple.get("ata_section", "")

                    for entity in triple.get("entities", []):
                        all_nodes.append({
                            "global_id":        entity.get("global_id", entity["id"]),
                            "type":             entity["type"],
                            "text":             entity["text"],
                            "ata_section":      ata_section,
                            "source_chunk_id":  chunk_id,
                            "aligned_part_id":  entity.get("aligned_part_id"),
                            "alignment_method": entity.get("alignment_method", "unmatched"),
                            "description":      entity.get("description", ""),
                            "procedure_type":   entity.get("procedure_type", ""),
                            "spec_type":        entity.get("spec_type", ""),
                        })

                    for rel in triple.get("relations", []):
                        h_e = entity_map.get(rel["head"])
                        t_e = entity_map.get(rel["tail"])
                        if h_e and t_e:
                            all_relations.append({
                                "type":      rel["type"],
                                "from_id":   h_e.get("global_id", h_e["id"]),
                                "to_id":     t_e.get("global_id", t_e["id"]),
                                "from_type": h_e["type"],
                                "to_type":   t_e["type"],
                                "weight":    rel.get("weight", 5),
                            })

                # 批量写入节点（每批 200 条）
                BATCH = 200
                for i in range(0, len(all_nodes), BATCH):
                    try:
                        _write_kg_nodes_batch(session, all_nodes[i:i + BATCH])
                        nodes_written += len(all_nodes[i:i + BATCH])
                    except Exception:
                        errors += 1

                # 批量写入关系（每批 200 条）
                for i in range(0, len(all_relations), BATCH):
                    try:
                        _write_kg_relations_batch(session, all_relations[i:i + BATCH])
                        relations_written += len(all_relations[i:i + BATCH])
                    except Exception:
                        errors += 1

                # 跨源连接：为对齐成功的 KG 节点创建 REPRESENTED_BY 图边
                _write_kg_represents_edges(session, all_nodes)

        except Exception:
            errors += 1
        finally:
            driver.close()

        stats = {
            "nodes": nodes_written,
            "relations": relations_written,
            "errors": errors,
        }
        return {
            "kg_stats": stats,
            "log_messages": [
                f"[KG] Neo4j 写入完成：节点 {nodes_written} 个，"
                f"关系 {relations_written} 条，错误 {errors} 次"
            ],
            "current_node": "write_kg_neo4j",
        }

    def write_kg_neo4j_unified(state: dict) -> dict:
        """
        联合 KG 写入节点（Sprint 2.2）：处理 merged_kg_triples（三源合并后）。

        相比 write_kg_neo4j 的扩展：
        1. 优先消费 kg_aligned_triples（已对齐），回退到 merged_kg_triples
        2. 节点写入时同步 gid / bom_part_id / cad_part_name / sources
        3. 写完节点后追加跨源边：
           - CAD 来源节点 → 统一节点 SAME_AS（当 gid 匹配但来源不同时）
           - BOM 来源节点 → KG 节点 REPRESENTED_BY（同现有逻辑）
        """
        triples = (state.get("kg_aligned_triples")
                   or state.get("merged_kg_triples")
                   or [])
        if not triples:
            return {
                "kg_stats": {"nodes": 0, "relations": 0, "errors": 0},
                "log_messages": ["[KG-Unified] 无三元组，跳过写入"],
                "current_node": "write_kg_neo4j_unified",
            }

        try:
            from neo4j import GraphDatabase
            driver = GraphDatabase.driver(
                neo4j_cfg.get("uri", "bolt://localhost:7687"),
                auth=(neo4j_cfg.get("user", "neo4j"), neo4j_cfg.get("pass", "neo4j")),
            )
        except Exception as e:
            return {
                "kg_stats": {"nodes": 0, "relations": 0, "errors": 1},
                "log_messages": [f"[KG-Unified] Neo4j 连接失败：{e}"],
                "current_node": "write_kg_neo4j_unified",
                "error": str(e),
            }

        nodes_written = 0
        relations_written = 0
        errors = 0

        try:
            with driver.session() as session:
                _init_kg_constraints(session)

                all_nodes:     list = []
                all_relations: list = []

                for triple in triples:
                    entity_map  = {e["id"]: e for e in triple.get("entities", [])}
                    chunk_id    = triple.get("chunk_id", "")
                    ata_section = triple.get("ata_section", "")
                    source      = triple.get("source", "KG")

                    for entity in triple.get("entities", []):
                        all_nodes.append({
                            "global_id":        entity.get("gid") or entity.get("global_id") or entity["id"],
                            "type":             entity["type"],
                            "text":             entity["text"],
                            "ata_section":      ata_section,
                            "source_chunk_id":  chunk_id,
                            "aligned_part_id":  entity.get("aligned_part_id") or entity.get("bom_part_id"),
                            "alignment_method": entity.get("alignment_method", "unmatched"),
                            "description":      entity.get("description", ""),
                            "gid":              entity.get("gid"),
                            "bom_part_id":      entity.get("bom_part_id"),
                            "cad_part_name":    entity.get("cad_part_name"),
                            "source":           source,
                            "procedure_type":   entity.get("procedure_type", ""),
                            "spec_type":        entity.get("spec_type", ""),
                        })

                    for rel in triple.get("relations", []):
                        # 支持 head/tail（kg_triples 格式）和 source_id/target_id（unified 格式）
                        src_key = rel.get("head") or rel.get("source_id")
                        tgt_key = rel.get("tail") or rel.get("target_id")
                        h_e = entity_map.get(src_key)
                        t_e = entity_map.get(tgt_key)
                        if h_e and t_e:
                            all_relations.append({
                                "type":      rel["type"],
                                "from_id":   h_e.get("gid") or h_e.get("global_id") or h_e["id"],
                                "to_id":     t_e.get("gid") or t_e.get("global_id") or t_e["id"],
                                "from_type": h_e["type"],
                                "to_type":   t_e["type"],
                                "weight":    rel.get("weight", 5),
                                "rel_props": {
                                    k: v for k, v in rel.items()
                                    if k not in ("type", "head", "tail", "source_id", "target_id", "weight")
                                },
                            })

                BATCH = 200
                for i in range(0, len(all_nodes), BATCH):
                    try:
                        _write_kg_nodes_batch(session, all_nodes[i:i + BATCH])
                        nodes_written += len(all_nodes[i:i + BATCH])
                    except Exception:
                        errors += 1

                for i in range(0, len(all_relations), BATCH):
                    try:
                        _write_kg_relations_batch_unified(session, all_relations[i:i + BATCH])
                        relations_written += len(all_relations[i:i + BATCH])
                    except Exception:
                        errors += 1

                # 跨源边：REPRESENTED_BY（BOM → KG）
                _write_kg_represents_edges(session, all_nodes)

                # 跨源边：SAME_AS（CAD 孤立节点 → 对齐后的统一节点）
                cad_nodes = [n for n in all_nodes
                             if n.get("source") == "CAD" and n.get("aligned_part_id")]
                if cad_nodes:
                    try:
                        session.run("""
                            UNWIND $nodes AS cn
                            MATCH (cad_n {kg_id: cn.global_id})
                            MATCH (unified {part_id: cn.aligned_part_id})
                            WHERE id(cad_n) <> id(unified)
                            MERGE (cad_n)-[:SAME_AS]->(unified)
                        """, nodes=cad_nodes)
                    except Exception:
                        pass

        except Exception:
            errors += 1
        finally:
            driver.close()

        stats = {"nodes": nodes_written, "relations": relations_written, "errors": errors}
        return {
            "kg_stats": stats,
            "log_messages": [
                f"[KG-Unified] Neo4j 写入完成：节点 {nodes_written} 个，"
                f"关系 {relations_written} 条，错误 {errors} 次"
            ],
            "current_node": "write_kg_neo4j_unified",
        }

    return {
        "extract_kg_triples":     extract_kg_triples,
        "align_entities":         align_entities,
        "verify_kg_entities":     verify_kg_entities,
        "validate_kg_dag":        validate_kg_dag,
        "write_kg_neo4j":         write_kg_neo4j,
        "write_kg_neo4j_unified": write_kg_neo4j_unified,
    }
