"""
backend/pipelines/nodes_kg_unified.py — 联合 KG 构建专用节点

提供四个节点函数，由 make_unified_kg_nodes() 工厂返回：

  bom_to_triples_node          — BOM DataFrame → 标准三元组 + bom_entities 字典
  cad_to_triples_node          — CAD 装配树/约束/邻接 → 标准三元组 + cad_entities 字典
  merge_multi_source_triples   — 三源合并 + 预对齐标注
  align_entities_multi_source  — 扩展四级对齐（含 CAD 名称模糊对齐）

全局实体标识体系：
  gid = "G_" + MD5(f"{source}:{normalize(name)}:{type}")[:16]
  融合优先级：BOM > CAD > KG（BOM gid 最权威）
"""

from __future__ import annotations

import hashlib
import json
from difflib import SequenceMatcher
from typing import Any


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------

def _normalize(name: str) -> str:
    """规范化实体名称（小写+去空格+展开缩写），用于跨源匹配。"""
    try:
        from backend.pipelines.nodes_kg import _apply_abbreviations
        name = _apply_abbreviations(name)
    except Exception:
        pass
    return name.strip().lower()


def _compute_gid(source: str, name: str, entity_type: str) -> str:
    """
    计算全局实体 ID（gid）。

    source:      "BOM" | "CAD" | "KG"
    name:        原始名称（_normalize 会在内部应用）
    entity_type: 实体类型字符串（Part / Assembly / Procedure / ...）
    """
    norm = _normalize(name)
    raw = f"{source}:{norm}:{entity_type}"
    return "G_" + hashlib.md5(raw.encode("utf-8")).hexdigest()[:16]


# ---------------------------------------------------------------------------
# 工厂函数
# ---------------------------------------------------------------------------

def make_unified_kg_nodes(app_state: Any, neo4j_cfg: dict) -> dict:
    """
    工厂函数：通过闭包绑定 AppState 和 Neo4j 配置，返回四个节点函数的字典。

    返回：
    {
        "bom_to_triples":         Callable,
        "cad_to_triples":         Callable,
        "merge_triples":          Callable,
        "align_entities_unified": Callable,
    }
    """

    # -----------------------------------------------------------------------
    # 节点 A：bom_to_triples_node
    # -----------------------------------------------------------------------

    def bom_to_triples_node(state: dict) -> dict:
        """
        BOM DataFrame JSON → 标准三元组格式 + bom_entities 字典。

        输入：state["bom_dataframe_json"]
        输出：state["bom_kg_triples"], state["bom_entities"]

        三元组格式（与 nodes_kg.py 的 kg_triples 保持一致）：
        {
            "chunk_id": str,
            "entities": [{"id", "type", "text", "description", "bom_part_id", "gid"}],
            "relations": [{"source_id", "target_id", "type"}],
            "source": "BOM",
        }
        """
        bom_json = state.get("bom_dataframe_json") or ""
        if not bom_json:
            return {
                "bom_kg_triples": [],
                "bom_entities":   {},
                "log_messages":   ["[BOM→Triples] bom_dataframe_json 为空，跳过三元组转换"],
                "current_node":   "bom_to_triples",
            }

        try:
            records = json.loads(bom_json)
        except Exception as e:
            return {
                "bom_kg_triples": [],
                "bom_entities":   {},
                "log_messages":   [f"[BOM→Triples] JSON 解析失败：{e}"],
                "current_node":   "bom_to_triples",
            }

        if not records:
            return {
                "bom_kg_triples": [],
                "bom_entities":   {},
                "log_messages":   ["[BOM→Triples] 空记录，跳过"],
                "current_node":   "bom_to_triples",
            }

        # ---- 构建实体和父子关系 ----
        entities:  list[dict] = []
        relations: list[dict] = []
        bom_entities: dict = {}          # normalize(name) → entity metadata

        # part_id → entity_id 用于建立 isPartOf 关系
        id_map: dict[str, str] = {}

        for row in records:
            part_id   = str(row.get("part_id", "")).strip()
            part_name = str(row.get("part_name", row.get("name", ""))).strip()
            parent_id = str(row.get("parent_id", "")).strip()
            category  = str(row.get("category", "Part")).strip()

            if not part_name:
                continue

            # 将 category 映射到合法实体类型
            etype = "Assembly" if "assembly" in category.lower() or "总成" in category else "Part"
            gid   = _compute_gid("BOM", part_name, etype)
            eid   = f"bom_{part_id or _normalize(part_name)}"

            entity = {
                "id":          eid,
                "type":        etype,
                "text":        part_name,
                "description": str(row.get("description", row.get("备注", ""))).strip(),
                "bom_part_id": part_id,
                "gid":         gid,
                "source":      "BOM",
            }
            entities.append(entity)
            id_map[part_id] = eid

            norm_name = _normalize(part_name)
            bom_entities[norm_name] = {
                "gid":       gid,
                "part_id":   part_id,
                "part_name": part_name,
                "type":      etype,
                "entity_id": eid,
            }

        # 父子关系（isPartOf）
        for row in records:
            part_id   = str(row.get("part_id", "")).strip()
            parent_id = str(row.get("parent_id", "")).strip()
            if part_id in id_map and parent_id in id_map:
                relations.append({
                    "source_id": id_map[part_id],
                    "target_id": id_map[parent_id],
                    "type":      "isPartOf",
                })

        # 每 100 个实体打包为一个 triple（减少后续处理开销）
        triples: list[dict] = []
        batch_size = 100
        for i in range(0, max(len(entities), 1), batch_size):
            batch_ents = entities[i:i + batch_size]
            # 只包含本 batch 内实体相关的关系
            batch_ids  = {e["id"] for e in batch_ents}
            batch_rels = [r for r in relations
                          if r["source_id"] in batch_ids or r["target_id"] in batch_ids]
            triples.append({
                "chunk_id":  f"bom_batch_{i // batch_size}",
                "entities":  batch_ents,
                "relations": batch_rels,
                "source":    "BOM",
            })

        return {
            "bom_kg_triples": triples,
            "bom_entities":   bom_entities,
            "log_messages":   [
                f"[BOM→Triples] 转换完成：{len(entities)} 实体，"
                f"{len(relations)} 关系，{len(triples)} 批次"
            ],
            "current_node": "bom_to_triples",
        }

    # -----------------------------------------------------------------------
    # 节点 B：cad_to_triples_node
    # -----------------------------------------------------------------------

    def cad_to_triples_node(state: dict) -> dict:
        """
        CAD 装配树 / 约束 / 邻接 → 标准三元组格式 + cad_entities 字典。

        不直接写 Neo4j，仅返回三元组到 state。

        输入：state["cad_assembly_tree"], state["cad_constraints"], state["cad_adjacency"]
        输出：state["cad_kg_triples"], state["cad_entities"]
        """
        assembly_tree = state.get("cad_assembly_tree") or {}
        constraints   = state.get("cad_constraints")   or []
        adjacency     = state.get("cad_adjacency")     or []

        if not assembly_tree and not constraints:
            return {
                "cad_kg_triples": [],
                "cad_entities":   {},
                "log_messages":   ["[CAD→Triples] 无 CAD 数据，跳过"],
                "current_node":   "cad_to_triples",
            }

        entities:     list[dict] = []
        relations:    list[dict] = []
        cad_entities: dict = {}          # normalize(name) → entity metadata
        name_to_eid:  dict = {}

        def _get_or_create_entity(part_name: str) -> str:
            """确保零件实体存在，返回 entity_id。"""
            norm = _normalize(part_name)
            if norm in name_to_eid:
                return name_to_eid[norm]
            gid  = _compute_gid("CAD", part_name, "Part")
            eid  = f"cad_{norm[:40]}"
            entities.append({
                "id":           eid,
                "type":         "Part",
                "text":         part_name,
                "description":  "",
                "cad_part_name": part_name,
                "gid":          gid,
                "source":       "CAD",
            })
            name_to_eid[norm] = eid
            cad_entities[norm] = {
                "gid":          gid,
                "cad_part_name": part_name,
                "type":         "Part",
                "entity_id":    eid,
            }
            return eid

        # 装配树 → isPartOf 关系（递归 DFS）
        def _traverse(node: dict, parent_name: str | None = None):
            name = node.get("name", "").strip()
            if not name:
                return
            eid = _get_or_create_entity(name)
            if parent_name:
                parent_eid = _get_or_create_entity(parent_name)
                relations.append({
                    "source_id": eid,
                    "target_id": parent_eid,
                    "type":      "isPartOf",
                })
            for child in node.get("children", []):
                _traverse(child, name)

        if assembly_tree:
            _traverse(assembly_tree)

        # 约束关系 → matesWith
        for c in constraints:
            part_a = str(c.get("part_a", "")).strip()
            part_b = str(c.get("part_b", "")).strip()
            if not part_a or not part_b:
                continue
            eid_a = _get_or_create_entity(part_a)
            eid_b = _get_or_create_entity(part_b)
            relations.append({
                "source_id":       eid_a,
                "target_id":       eid_b,
                "type":            "matesWith",
                "constraint_type": c.get("constraint_type", ""),
                "interface":       c.get("interface", ""),
            })

        # 邻接关系 → adjacentTo（联合KG任务默认包含，可设 state["skip_adjacency"]=True 跳过）
        if not state.get("skip_adjacency"):
            for adj in adjacency:
                part_a = str(adj.get("part_a", "")).strip()
                part_b = str(adj.get("part_b", "")).strip()
                if not part_a or not part_b:
                    continue
                eid_a = _get_or_create_entity(part_a)
                eid_b = _get_or_create_entity(part_b)
                relations.append({
                    "source_id": eid_a,
                    "target_id": eid_b,
                    "type":      "adjacentTo",
                    "gap_mm":    adj.get("gap_mm", 0),
                })

        # 打包成单个 triple（CAD 数据通常来自单个文件）
        triple = {
            "chunk_id":  "cad_main",
            "entities":  entities,
            "relations": relations,
            "source":    "CAD",
        }

        return {
            "cad_kg_triples": [triple],
            "cad_entities":   cad_entities,
            "log_messages":   [
                f"[CAD→Triples] 转换完成：{len(entities)} 实体，"
                f"{len(relations)} 关系（isPartOf/matesWith/adjacentTo）"
            ],
            "current_node": "cad_to_triples",
        }

    # -----------------------------------------------------------------------
    # 节点 C：merge_multi_source_triples
    # -----------------------------------------------------------------------

    def merge_multi_source_triples(state: dict) -> dict:
        """
        三源合并 + 预对齐标注。

        输入：
            bom_kg_triples, cad_kg_triples, kg_triples（手册）
            bom_entities, cad_entities
        输出：
            merged_kg_triples（含预对齐标注字段）
        """
        bom_triples = state.get("bom_kg_triples") or []
        cad_triples = state.get("cad_kg_triples") or []
        kg_triples  = state.get("kg_triples")     or []
        bom_ents    = state.get("bom_entities")   or {}
        cad_ents    = state.get("cad_entities")   or {}

        pre_align_hits = 0

        def _pre_align_entity(entity: dict) -> dict:
            """
            快速路径：若实体 text 在内存 bom_entities/cad_entities 中有精确规范化匹配，
            注入 aligned_part_id/aligned_cad_name/gid，跳过后续慢路径对齐。
            """
            nonlocal pre_align_hits
            text = entity.get("text", "")
            norm = _normalize(text)

            result = dict(entity)

            # BOM 优先
            if norm in bom_ents:
                meta = bom_ents[norm]
                result["aligned_part_id"]  = meta.get("part_id")
                result["gid"]              = meta.get("gid")
                result["alignment_method"] = "pre_align_bom"
                pre_align_hits += 1
                return result

            # CAD 次之
            if norm in cad_ents:
                meta = cad_ents[norm]
                result["aligned_cad_name"] = meta.get("cad_part_name")
                result["gid"]              = meta.get("gid")
                result["alignment_method"] = "pre_align_cad"
                pre_align_hits += 1
                return result

            return result

        def _annotate_triples(triples: list[dict]) -> list[dict]:
            """对三元组列表中的每个实体执行预对齐。"""
            annotated = []
            for triple in triples:
                t = dict(triple)
                t["entities"] = [_pre_align_entity(e) for e in triple.get("entities", [])]
                annotated.append(t)
            return annotated

        merged = (
            _annotate_triples(bom_triples) +
            _annotate_triples(cad_triples) +
            _annotate_triples(kg_triples)
        )

        total_ents = sum(len(t.get("entities", [])) for t in merged)

        return {
            "merged_kg_triples": merged,
            "log_messages": [
                f"[Merge] 三源合并完成："
                f"BOM={len(bom_triples)} batches，"
                f"CAD={len(cad_triples)} batches，"
                f"KG={len(kg_triples)} batches，"
                f"共 {total_ents} 实体，预对齐命中 {pre_align_hits}"
            ],
            "current_node": "merge_multi_source_triples",
        }

    # -----------------------------------------------------------------------
    # 节点 D：align_entities_multi_source
    # -----------------------------------------------------------------------

    def align_entities_multi_source(state: dict) -> dict:
        """
        四级级联实体对齐（扩展自原 align_entities，新增 CAD 模糊对齐）。

        Level 0: pre_align（merge 节点已注入，直接跳过）
        Level 1: 规则对齐（BOM part_name 精确匹配 + 缩写展开）
        Level 2: 模糊对齐（difflib ≥0.85，BOM 优先 + CAD fallback）
        Level 3: 语义对齐（Qdrant bge-m3 向量检索）
        Level 4: CAD 名称模糊对齐（英文 CAD 名 vs 中文手册名，阈值 0.72）

        输入：merged_kg_triples, bom_entities, cad_entities
        输出：kg_aligned_triples
        """
        merged_triples = state.get("merged_kg_triples") or []
        bom_ents       = state.get("bom_entities")      or {}
        cad_ents       = state.get("cad_entities")      or {}

        if not merged_triples:
            return {
                "kg_aligned_triples": [],
                "log_messages":       ["[Align-MS] 无三元组需要对齐"],
                "current_node":       "align_entities_multi_source",
            }

        # 构建内存参考集（规范化名称 → {part_id, cad_name, gid}）
        bom_norm_to_meta: dict[str, dict] = {k: v for k, v in bom_ents.items()}
        cad_norm_to_meta: dict[str, dict] = {k: v for k, v in cad_ents.items()}

        # 补充从 Neo4j 历史数据（仅当本次内存 bom_ents 为空时才查库）
        if not bom_norm_to_meta:
            try:
                from neo4j import GraphDatabase
                driver = GraphDatabase.driver(
                    neo4j_cfg.get("uri", "bolt://localhost:7687"),
                    auth=(neo4j_cfg.get("user", "neo4j"), neo4j_cfg.get("pass", "neo4j")),
                )
                with driver.session() as session:
                    rows = session.run(
                        "MATCH (n) WHERE n.part_name IS NOT NULL AND n.part_id IS NOT NULL "
                        "RETURN n.part_name AS name, n.part_id AS pid, n.gid AS gid"
                    ).data()
                    for r in rows:
                        k = _normalize(r["name"])
                        bom_norm_to_meta[k] = {
                            "part_id":   r["pid"],
                            "part_name": r["name"],
                            "gid":       r.get("gid"),
                        }
                driver.close()
            except Exception:
                pass

        bom_norms = list(bom_norm_to_meta.keys())
        cad_norms = list(cad_norm_to_meta.keys())
        stats = {"pre_align": 0, "rule": 0, "fuzzy_bom": 0,
                 "fuzzy_cad": 0, "semantic": 0, "cad_fuzzy4": 0, "unmatched": 0}

        def _align_one(entity: dict) -> dict:
            """对单个实体执行四级对齐，返回注入了对齐结果的 entity dict。"""
            # Level 0: pre_align 已命中，直接跳过
            if entity.get("alignment_method", "").startswith("pre_align"):
                stats["pre_align"] += 1
                return entity

            text     = entity.get("text", "")
            expanded = _normalize(text)
            result   = dict(entity)

            # Level 1: 规则对齐
            if expanded in bom_norm_to_meta:
                meta = bom_norm_to_meta[expanded]
                result.update({
                    "aligned_part_id":  meta.get("part_id"),
                    "gid":              meta.get("gid") or _compute_gid("BOM", text, entity.get("type", "Part")),
                    "alignment_method": "rule",
                })
                stats["rule"] += 1
                return result

            # Level 2: 模糊对齐（BOM 优先）
            best_ratio, best_norm, best_source = 0.0, "", "bom"
            for norm in bom_norms:
                r = SequenceMatcher(None, expanded, norm).ratio()
                if r > best_ratio:
                    best_ratio, best_norm, best_source = r, norm, "bom"
            for norm in cad_norms:
                r = SequenceMatcher(None, expanded, norm).ratio()
                if r > best_ratio:
                    best_ratio, best_norm, best_source = r, norm, "cad"

            if best_ratio >= 0.85 and best_norm:
                if best_source == "bom":
                    meta = bom_norm_to_meta[best_norm]
                    result.update({
                        "aligned_part_id":  meta.get("part_id"),
                        "gid":              meta.get("gid") or _compute_gid("BOM", text, entity.get("type", "Part")),
                        "alignment_method": "fuzzy_bom",
                    })
                    stats["fuzzy_bom"] += 1
                else:
                    meta = cad_norm_to_meta[best_norm]
                    result.update({
                        "aligned_cad_name": meta.get("cad_part_name"),
                        "gid":              meta.get("gid") or _compute_gid("CAD", text, entity.get("type", "Part")),
                        "alignment_method": "fuzzy_cad",
                    })
                    stats["fuzzy_cad"] += 1
                return result

            # Level 3: 语义对齐（Qdrant bge-m3）
            if best_ratio < 0.70:
                try:
                    vecs = app_state.embedding_mgr.encode_text([text])
                    qres = app_state.qdrant_client.query_points(
                        collection_name="rag_knowledge",
                        query=vecs[0].tolist(),
                        using="text_vec",
                        limit=1,
                        with_payload=["text"],
                    )
                    if qres.points:
                        hit_text = qres.points[0].payload.get("text", "")
                        for norm, meta in bom_norm_to_meta.items():
                            if meta.get("part_name", "") in hit_text:
                                result.update({
                                    "aligned_part_id":  meta.get("part_id"),
                                    "gid":              meta.get("gid") or _compute_gid("BOM", text, entity.get("type", "Part")),
                                    "alignment_method": "semantic",
                                })
                                stats["semantic"] += 1
                                return result
                except Exception:
                    pass

            # Level 4: CAD 名称模糊对齐（专门处理英文 CAD 名 vs 中文手册名，阈值放低到 0.72）
            if cad_norms and best_ratio < 0.72:
                best4_r, best4_n = 0.0, ""
                for norm in cad_norms:
                    # 也尝试原始文本（不规范化）与 CAD 原始名称对比
                    raw_cad = cad_norm_to_meta[norm].get("cad_part_name", "")
                    r = SequenceMatcher(None, text.lower(), raw_cad.lower()).ratio()
                    if r > best4_r:
                        best4_r, best4_n = r, norm
                if best4_r >= 0.72 and best4_n:
                    meta = cad_norm_to_meta[best4_n]
                    result.update({
                        "aligned_cad_name": meta.get("cad_part_name"),
                        "gid":              meta.get("gid") or _compute_gid("CAD", text, entity.get("type", "Part")),
                        "alignment_method": "cad_fuzzy4",
                    })
                    stats["cad_fuzzy4"] += 1
                    return result

            # 未对齐：仍生成 gid（基于 KG 源）
            result["gid"] = _compute_gid("KG", text, entity.get("type", "Part"))
            result["alignment_method"] = "unmatched"
            stats["unmatched"] += 1
            return result

        # 对 merged_kg_triples 中所有实体执行对齐
        aligned_triples = []
        for triple in merged_triples:
            t = dict(triple)
            t["entities"] = [_align_one(e) for e in triple.get("entities", [])]
            aligned_triples.append(t)

        total = sum(stats.values()) or 1
        rate_str = ", ".join(f"{k}:{v/total:.0%}" for k, v in stats.items() if v)
        return {
            "kg_aligned_triples": aligned_triples,
            "log_messages":       [f"[Align-MS] 多源对齐完成：{rate_str}"],
            "current_node":       "align_entities_multi_source",
        }

    # -----------------------------------------------------------------------
    # 返回节点字典
    # -----------------------------------------------------------------------
    return {
        "bom_to_triples":         bom_to_triples_node,
        "cad_to_triples":         cad_to_triples_node,
        "merge_triples":          merge_multi_source_triples,
        "align_entities_unified": align_entities_multi_source,
    }
