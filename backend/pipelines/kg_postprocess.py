"""
backend/pipelines/kg_postprocess.py — 三元组后处理管道

流程：
  1. 置信度过滤   (MIN_CONFIDENCE = 0.3)
  2. 实体名称归一化
  3. 本体约束校验
  4. 重复三元组去重（保留置信度最高的一条）

对外接口：
  postprocess_triples(triples: list[dict]) -> tuple[list[dict], dict]
  返回 (清洗后三元组, 统计报告)
"""

import re
from typing import Any, Optional

# ─── 置信度阈值 ───────────────────────────────
MIN_CONFIDENCE: float = 0.3

# ─── 本体约束规则 ─────────────────────────────
ONTOLOGY_RULES: dict[str, dict] = {
    "precedes":       {"head": ["Procedure"], "tail": ["Procedure"]},
    "participatesIn": {"head": ["Part", "Assembly"], "tail": ["Procedure"]},
    "requires":       {"head": ["Procedure"], "tail": ["Tool"]},
    "specifiedBy":    {
        "head": ["Procedure", "Interface", "Part", "Assembly"],
        "tail": ["Specification"],
    },
    "matesWith":      {
        "head": ["Part", "Assembly", "Interface"],
        "tail": ["Part", "Assembly", "Interface"],
    },
    "isPartOf":       {
        "head": ["Part", "Assembly"],
        "tail": ["Part", "Assembly", "ROOT"],
    },
}


# ─── 步骤1：置信度过滤 ────────────────────────

def _filter_confidence(triples: list[dict]) -> tuple[list[dict], int]:
    before = len(triples)
    kept = [t for t in triples if t.get("confidence", 0) >= MIN_CONFIDENCE]
    return kept, before - len(kept)


# ─── 步骤2：实体名称归一化 ────────────────────

def _normalize_entity(name: str) -> str:
    """
    统一实体名称：
      - strip 首尾空白
      - 合并多余内部空格
      - 统一中文标点 → 英文标点（逗号）
    注意：不做大小写转换，保留原始大小写用于显示；
    比对时使用 .lower() 做无大小写区分匹配。
    """
    name = name.strip()
    name = re.sub(r"\s+", " ", name)
    name = name.replace("，", ",").replace("。", ".").replace("；", ";")
    return name


def _normalize_triples(triples: list[dict]) -> list[dict]:
    result = []
    for t in triples:
        nt = dict(t)
        if nt.get("head"):
            nt["head"] = _normalize_entity(nt["head"])
        if nt.get("tail"):
            nt["tail"] = _normalize_entity(nt["tail"])
        result.append(nt)
    return result


# ─── 步骤3：本体约束校验 ──────────────────────

def _validate_ontology(triple: dict) -> bool:
    """
    校验三元组是否满足本体约束。
    未定义的关系类型暂时放行（返回 True）。
    """
    rule = ONTOLOGY_RULES.get(triple.get("relation", ""))
    if not rule:
        return True
    head_type = triple.get("head_type", "Unknown")
    tail_type = triple.get("tail_type", "Unknown")
    head_ok = head_type in rule["head"]
    tail_ok = tail_type in rule["tail"]
    return head_ok and tail_ok


def _filter_ontology(triples: list[dict]) -> tuple[list[dict], int]:
    before = len(triples)
    kept = [t for t in triples if _validate_ontology(t)]
    return kept, before - len(kept)


# ─── 步骤4：去重（保留最高置信度） ───────────

def _dedup_triples(triples: list[dict]) -> tuple[list[dict], int]:
    """
    以 (head.lower(), relation, tail.lower()) 为 key 去重，
    当同 key 有多条时保留 confidence 最高的一条。
    """
    seen: dict[tuple, dict] = {}
    for t in triples:
        key = (
            _normalize_entity(t.get("head", "")).lower(),
            t.get("relation", ""),
            _normalize_entity(t.get("tail", "")).lower(),
        )
        if key not in seen:
            seen[key] = t
        else:
            # 保留置信度更高的
            if t.get("confidence", 0) > seen[key].get("confidence", 0):
                seen[key] = t

    result = list(seen.values())
    removed = len(triples) - len(result)
    return result, removed


# ─── 主入口 ───────────────────────────────────

def postprocess_triples(
    triples: list[dict],
    *,
    skip_ontology: bool = False,
) -> tuple[list[dict], dict]:
    """
    对三元组列表执行完整后处理管道。

    参数：
      triples       — 原始三元组列表
      skip_ontology — 若为 True，跳过本体校验（适合来源不含类型信息的阶段）

    返回：
      (cleaned_triples, stats)
      stats 包含各步骤去除数量和最终保留率。
    """
    original_count = len(triples)
    stats: dict = {"original": original_count}

    # Step 1: 置信度过滤
    triples, removed_conf = _filter_confidence(triples)
    stats["removed_low_confidence"] = removed_conf

    # Step 2: 归一化
    triples = _normalize_triples(triples)
    stats["normalized"] = True

    # Step 3: 本体校验
    if not skip_ontology:
        triples, removed_onto = _filter_ontology(triples)
        stats["removed_ontology_violation"] = removed_onto
    else:
        stats["removed_ontology_violation"] = 0

    # Step 4: 去重
    triples, removed_dup = _dedup_triples(triples)
    stats["removed_duplicates"] = removed_dup

    # 汇总
    stats["final"] = len(triples)
    stats["total_removed"] = original_count - len(triples)
    stats["retention_rate"] = (
        round(len(triples) / original_count, 4) if original_count else 1.0
    )

    return triples, stats


# ─── BOM 关联增强（跨源对齐 Level 1.5 / 1.6 / 1.7）────────────────────────────

# 零件编号正则模式（按优先级排列）
_PN_PATTERNS = [
    re.compile(r'\b(\d{7}(?:-\d+)?)\b'),           # 7位数字，如 3034344、3103074-01
    re.compile(r'\b(MS\d+(?:-\d+)?)\b'),            # MS规格，如 MS9556-07
    re.compile(r'\b([A-Z]{2}\d+(?:-\d+)?)\b'),      # AS/AN类，如 AS3209-267、AN150568
]

# Jaccard 停用词
_STOPWORDS = {'THE', 'A', 'AN', 'OF', 'FOR', 'AND', 'OR', 'WITH', 'TO', 'IN', 'AT', 'ON'}

# 需要对齐的实体类型
_PART_TYPES = {"Part", "Assembly"}


def _build_pn_index(bom_entities: list) -> dict[str, str]:
    """构建 part_number → bom_entity_id 的精确索引。"""
    idx: dict[str, str] = {}
    for e in bom_entities:
        pn = e.get("part_number", "")
        bid = e.get("id", "")
        if pn and bid:
            idx[pn.upper()] = bid
    return idx


def _extract_pn_from_text(text: str, pn_index: dict[str, str]) -> str | None:
    """Level 1.5：从文本中用正则提取零件编号，查索引返回 bom_id。"""
    for pattern in _PN_PATTERNS:
        for m in pattern.finditer(text):
            candidate = m.group(1).upper()
            if candidate in pn_index:
                return pn_index[candidate]
    return None


def _keyword_set(name: str) -> set[str]:
    """将名称拆为关键词集合，过滤停用词，最短 2 个字符。"""
    tokens = set(re.findall(r'[A-Z]{2,}', name.upper()))
    return tokens - _STOPWORDS


def _jaccard(a: str, b: str) -> float:
    """计算两个名称的关键词 Jaccard 相似度。"""
    sa, sb = _keyword_set(a), _keyword_set(b)
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def enrich_bom_links(
    triples: list[dict],
    bom_entities: list[dict],
) -> dict[str, Any]:
    """
    对三元组列表执行三级 BOM 关联增强，就地写入 head_bom_id / tail_bom_id 字段。

    参数：
      triples      — 三元组列表（来自 stage2_manual 或 stage3_cad）
      bom_entities — BOM 实体列表，每条含 {id, name, part_number}

    返回：
      {
        "triples": List[dict],   # 原列表引用（已就地修改）
        "stats": {
          "regex_hits": int,
          "cad_hits": int,
          "keyword_hits": int,
          "unmatched": int,
          "total": int,
        }
      }
    """
    if not triples or not bom_entities:
        total = len(triples)
        return {
            "triples": triples,
            "stats": {"regex_hits": 0, "cad_hits": 0, "keyword_hits": 0,
                      "unmatched": total, "total": total},
        }

    pn_index = _build_pn_index(bom_entities)
    _cad_cache: dict[str, str | None] = {}

    stats = {"regex_hits": 0, "cad_hits": 0, "keyword_hits": 0, "unmatched": 0, "total": 0}

    def _align_text(text: str, entity_type: str) -> tuple[str | None, str]:
        if entity_type not in _PART_TYPES:
            return None, "skip"

        # Level 1.5: 正则编号提取
        bid = _extract_pn_from_text(text, pn_index)
        if bid:
            return bid, "regex"

        # Level 1.6: CAD 启发式编号映射
        cad_match = re.match(r'^[A-Z]+(\d[\d-]*)$', text.strip().upper())
        if cad_match:
            numeric_core = cad_match.group(1).split('-')[0]
            if numeric_core not in _cad_cache:
                hits = [e["id"] for e in bom_entities
                        if numeric_core in e.get("part_number", "").upper()]
                _cad_cache[numeric_core] = hits[0] if len(hits) == 1 else None
            bid = _cad_cache[numeric_core]
            if bid:
                return bid, "cad_heuristic"

        # Level 1.7: Jaccard 关键词匹配
        best_score, best_id = 0.0, None
        for e in bom_entities:
            score = _jaccard(text, e.get("name", ""))
            if score > best_score:
                best_score, best_id = score, e["id"]
        if best_score >= 0.35 and best_id:
            return best_id, "keyword_jaccard"

        return None, "unmatched"

    for t in triples:
        stats["total"] += 1
        for field, ftype_key in (("head", "head_type"), ("tail", "tail_type")):
            text = t.get(field, "")
            etype = t.get(ftype_key, "")
            if not text:
                continue
            if t.get(f"{field}_bom_id"):
                continue
            bid, method = _align_text(text, etype)
            if bid:
                t[f"{field}_bom_id"] = bid
                t[f"{field}_align_method"] = method
                if method == "regex":
                    stats["regex_hits"] += 1
                elif method == "cad_heuristic":
                    stats["cad_hits"] += 1
                elif method == "keyword_jaccard":
                    stats["keyword_hits"] += 1
            else:
                if method != "skip":
                    stats["unmatched"] += 1

    return {"triples": triples, "stats": stats}
