"""
backend/routers/retrieve.py — 向量检索接口（图文双路版）

POST /retrieve
  请求体：{"query": "用户问题", "top_k": 4, "use_rerank": true}
  响应：{"chunks": [{"text", "source", "page", "distance", "chunk_type", "image_url", ...}, ...]}

双路检索策略：
  - 路径1：bge-m3(query) → 搜 Qdrant text_vec → 文本块 + Caption块
  - 路径2：Chinese-CLIP文本编码器(query) → 搜 Qdrant image_vec → 图片块
  合并去重 → CrossEncoder 精排 → 返回 top_k

向量度量：Qdrant 使用 COSINE（余弦相似度，值越高越相关）
"""

import os
from typing import List, Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from backend.deps import get_state
from backend.state import AppState, COLLECTION_NAME

router = APIRouter()

RETRIEVE_RECALL_MULTIPLIER = 3   # 召回倍数
RETRIEVE_RECALL_MAX = 20         # 最大召回数上限
IMAGE_SERVE_PREFIX = "/images"   # 图片静态文件服务前缀


class RetrieveRequest(BaseModel):
    query: str
    top_k: int = Field(default=4, ge=1, le=20)
    use_rerank: bool = True


class ChunkResult(BaseModel):
    text: str
    source: str
    page: int = 0
    distance: float
    rerank_score: Optional[float] = None
    chunk_type: str = "text"             # "text" | "image"
    image_url: Optional[str] = None      # 仅 chunk_type="image" 时非空


class RetrieveResponse(BaseModel):
    chunks: List[ChunkResult]


def _image_url(image_path: str) -> Optional[str]:
    """将本地 image_path 转为前端可访问的 URL（/images/{filename}），自动 URL 编码特殊字符。"""
    if not image_path:
        return None
    from urllib.parse import quote
    return f"{IMAGE_SERVE_PREFIX}/{quote(os.path.basename(image_path))}"


def _qdrant_point_to_dict(point) -> dict:
    """将 Qdrant ScoredPoint 转为统一的候选块 dict。"""
    payload = point.payload or {}
    image_path = payload.get("image_path", "")
    return {
        "id":          str(point.id),
        "text":        payload.get("text", ""),
        "source":      payload.get("source", "未知"),
        "page":        payload.get("page", 0),
        "distance":    point.score,   # Cosine 相似度，越高越相关
        "chunk_type":  payload.get("chunk_type", "text"),
        "image_path":  image_path,
        "image_url":   _image_url(image_path),
        "rerank_score": None,
    }


def qdrant_search_text(qdrant_client, embedding_mgr, query: str, n: int) -> List[dict]:
    """
    用 bge-m3 编码 query，搜 text_vec，返回文本块和 Caption 块。
    适合文字查询找文本内容和图片描述。
    """
    text_vec = embedding_mgr.encode_text([query])[0].tolist()
    results = qdrant_client.query_points(
        collection_name=COLLECTION_NAME,
        query=text_vec,
        using="text_vec",
        limit=n,
        with_payload=True,
    )
    return [_qdrant_point_to_dict(p) for p in results.points]


def qdrant_search_image(qdrant_client, embedding_mgr, query: str, n: int) -> List[dict]:
    """
    用 Chinese-CLIP 文本编码器编码 query，搜 image_vec，只找图片块。
    适合文字查图场景（文字描述 → 找相关图片）。
    """
    from qdrant_client.models import Filter, FieldCondition, MatchValue

    clip_vec = embedding_mgr.encode_texts_clip([query])[0].tolist()
    results = qdrant_client.query_points(
        collection_name=COLLECTION_NAME,
        query=clip_vec,
        using="image_vec",
        limit=n,
        with_payload=True,
        query_filter=Filter(
            must=[FieldCondition(key="chunk_type", match=MatchValue(value="image"))]
        ),
    )
    return [_qdrant_point_to_dict(p) for p in results.points]


def bm25_search_text(bm25_manager, query: str, n: int) -> List[dict]:
    """
    BM25 关键词检索。返回 [{"id": uuid, "bm25_score": float}, ...] 轻量结构（无 payload）。
    bm25_manager 为 None 或索引为空时返回 []。
    """
    if bm25_manager is None:
        return []
    try:
        hits = bm25_manager.search(query, n)
        return [{"id": pid, "bm25_score": score} for pid, score in hits]
    except Exception as e:
        print(f"[retrieve] BM25 检索异常（{e}）")
        return []


def reciprocal_rank_fusion(
    dense_results: List[dict],
    bm25_results: List[dict],
    k: int = 60,
) -> List[dict]:
    """
    RRF 融合两路排名结果。
    公式：RRF(d) = Σ 1/(k + rank_i(d))，rank 从 1 开始。
    以 dense_results 的完整 payload 为基准；
    仅出现在 BM25 而不在 dense 中的文档跳过（payload 不可用）。
    返回按 RRF 分数降序排列的 dict 列表，distance 字段替换为 rrf_score。
    """
    dense_rank = {c["id"]: i + 1 for i, c in enumerate(dense_results)}
    bm25_rank  = {c["id"]: i + 1 for i, c in enumerate(bm25_results)}

    all_ids = set(dense_rank) | set(bm25_rank)
    rrf_scores: dict = {}
    for cid in all_ids:
        score = 0.0
        if cid in dense_rank:
            score += 1.0 / (k + dense_rank[cid])
        if cid in bm25_rank:
            score += 1.0 / (k + bm25_rank[cid])
        rrf_scores[cid] = score

    id_to_chunk = {c["id"]: c for c in dense_results}
    fused = []
    for cid, rrf_score in sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True):
        if cid in id_to_chunk:
            chunk = dict(id_to_chunk[cid])
            chunk["distance"] = rrf_score   # 覆盖原 cosine distance，保持接口一致
            chunk["rrf_score"] = rrf_score
            fused.append(chunk)
        # 仅出现在 BM25 中的 id：跳过（dense 未召回，payload 无法还原）

    return fused


def hybrid_search_text(
    qdrant_client, embedding_mgr, bm25_manager,
    query: str, n: int,
) -> List[dict]:
    """
    混合文本检索：Dense(bge-m3) + BM25，通过 RRF(k=60) 融合。
    - bm25_manager 为 None 时降级为纯 Dense 检索
    - BM25 侧召回数为 n*2（计算廉价，多召回增加 RRF 融合覆盖面）
    - 任何 BM25 异常自动降级，不影响 Dense 检索结果
    返回 schema 与 qdrant_search_text 相同。
    """
    dense_results = qdrant_search_text(qdrant_client, embedding_mgr, query, n)

    if not bm25_manager or not dense_results:
        return dense_results

    try:
        bm25_hits = bm25_search_text(bm25_manager, query, n * 2)
        if not bm25_hits:
            return dense_results
        return reciprocal_rank_fusion(dense_results, bm25_hits, k=60)
    except Exception as e:
        print(f"[retrieve] BM25 混合检索失败（{e}），降级为纯 Dense")
        return dense_results


def merge_and_dedup(text_results: List[dict], image_results: List[dict]) -> List[dict]:
    """
    合并两路检索结果，按 ID 去重，保留同一块中 distance 最高（最相关）的版本。
    最终按 distance 降序排列（余弦相似度越高越相关）。
    """
    seen: dict = {}
    for chunk in text_results + image_results:
        cid = chunk["id"]
        if cid not in seen or chunk["distance"] > seen[cid]["distance"]:
            seen[cid] = chunk
    return sorted(seen.values(), key=lambda c: c["distance"], reverse=True)


@router.post("/retrieve", response_model=RetrieveResponse, summary="向量检索（双路图文，支持重排序）")
def retrieve(body: RetrieveRequest, state: AppState = Depends(get_state)):
    """
    双路向量检索：
      - 路径1：bge-m3 文字查文本块/Caption（text_vec）
      - 路径2：Chinese-CLIP 文字查图片（image_vec）
    合并去重后用 CrossEncoder 重排，返回 top_k 结果。

    优先使用 LangChain Retriever（如已初始化），否则走原生路径。
    """
    total = state.get_doc_count()
    if total == 0:
        return RetrieveResponse(chunks=[])

    # ===== LangChain 路径 =====
    if state.lc_retriever is not None:
        retriever = state.lc_retriever
        # 动态调整 retriever 参数
        retriever.top_k = body.top_k
        retriever.use_rerank = body.use_rerank
        recall_n = min(body.top_k * RETRIEVE_RECALL_MULTIPLIER, RETRIEVE_RECALL_MAX, total)
        if not body.use_rerank or state.reranker is None:
            recall_n = min(body.top_k, total)
        retriever.recall_k = recall_n

        docs = retriever.invoke(body.query)
        chunks = [
            ChunkResult(
                text=doc.page_content,
                source=doc.metadata.get("source", "未知"),
                page=doc.metadata.get("page", 0),
                distance=doc.metadata.get("distance", 0.0),
                rerank_score=doc.metadata.get("rerank_score"),
                chunk_type=doc.metadata.get("chunk_type", "text"),
                image_url=doc.metadata.get("image_url"),
            )
            for doc in docs
        ]
        return RetrieveResponse(chunks=chunks)

    # ===== 原生路径（fallback）=====
    recall_n = min(body.top_k * RETRIEVE_RECALL_MULTIPLIER, RETRIEVE_RECALL_MAX, total)
    if not body.use_rerank or state.reranker is None:
        recall_n = min(body.top_k, total)

    text_results = hybrid_search_text(
        state.qdrant_client, state.embedding_mgr, state.bm25_manager, body.query, recall_n
    )

    image_results = []
    try:
        image_results = qdrant_search_image(
            state.qdrant_client, state.embedding_mgr, body.query, min(body.top_k, total)
        )
    except Exception as e:
        import traceback
        print(f"[retrieve] CLIP 图片检索失败（{e}），跳过图片路径")
        traceback.print_exc()

    candidates = merge_and_dedup(text_results, image_results)

    if body.use_rerank and state.reranker is not None and candidates:
        try:
            pairs = [(body.query, c["text"]) for c in candidates]
            scores = state.reranker.predict(pairs)
            for c, score in zip(candidates, scores):
                c["rerank_score"] = float(score)
            candidates = sorted(candidates, key=lambda c: c["rerank_score"], reverse=True)
        except Exception as e:
            print(f"[retrieve] Reranker 打分失败（{e}），按距离排序")

    top = candidates[:body.top_k]
    chunks = [
        ChunkResult(
            text=c["text"],
            source=c["source"],
            page=c["page"],
            distance=c["distance"],
            rerank_score=c.get("rerank_score"),
            chunk_type=c.get("chunk_type", "text"),
            image_url=c.get("image_url"),
        )
        for c in top
    ]
    return RetrieveResponse(chunks=chunks)


# ═════════════════════════════════════════════════════════════════════════════
# /retrieve_ablation —— 主实验消融端点（支持 path_mask）
# ═════════════════════════════════════════════════════════════════════════════

class AblationRequest(BaseModel):
    query: str
    top_k: int = Field(default=5, ge=1, le=50)
    paths: List[str] = Field(default=["dense", "bm25", "clip", "kg"])
    use_rerank: bool = True
    recall_n: int = Field(default=20, ge=1, le=100)
    fusion_k: int = Field(default=60, ge=1, le=200)


_KG_INDEX = {"names": None, "labels": None, "vectors": None, "loaded": False}


def _ensure_kg_index(neo4j_cfg: dict, embedding_mgr):
    """懒加载：从 Neo4j 取全部 entity 名，用 BGE-M3 编码缓存"""
    if _KG_INDEX["loaded"]:
        return
    try:
        from neo4j import GraphDatabase
        import numpy as np
        drv = GraphDatabase.driver(
            neo4j_cfg.get("uri", "bolt://localhost:7687"),
            auth=(neo4j_cfg.get("user", "neo4j"),
                  neo4j_cfg.get("pass", neo4j_cfg.get("password", "neo4j"))),
        )
        rows = []
        with drv.session() as s:
            cypher = (
                "MATCH (n) WHERE n.kg_name IS NOT NULL "
                "RETURN n.kg_name AS name, labels(n)[0] AS lbl, "
                "coalesce(n.description, n.part_name, '') AS desc"
            )
            for r in s.run(cypher).data():
                if r.get("name"):
                    rows.append(r)
        drv.close()
        if not rows:
            return
        # 编码文本：name + 截断的 description
        texts = []
        for r in rows:
            n = r["name"]
            d = (r.get("desc") or "")[:60]
            texts.append(f"{n} {d}".strip() if d else n)
        # BGE-M3 批量编码（已 L2 normalize）
        vecs = embedding_mgr.encode_text(texts)
        _KG_INDEX["names"] = [r["name"] for r in rows]
        _KG_INDEX["labels"] = [r["lbl"] for r in rows]
        _KG_INDEX["vectors"] = np.asarray(vecs, dtype="float32")
        _KG_INDEX["loaded"] = True
        print(f"[kg_index] BGE-M3 ANN index built: {len(rows)} entities, "
              f"vec shape={_KG_INDEX['vectors'].shape}")
    except Exception as e:
        import traceback
        print(f"[kg_index] build err: {e}")
        traceback.print_exc()


def kg_search_neo4j(neo4j_cfg: dict, query: str, n: int, embedding_mgr=None) -> List[dict]:
    """
    KG 检索（v2）：BGE-M3 语义 ANN 召回锚点 entity → 1 跳邻域。
    embedding_mgr=None 时降级回旧的关键词 CONTAINS 匹配。
    """
    if not neo4j_cfg:
        return []
    try:
        from neo4j import GraphDatabase
    except ImportError:
        return []

    # ── ANN 路径（推荐） ────────────────────────────────────
    if embedding_mgr is not None:
        try:
            import numpy as np
            _ensure_kg_index(neo4j_cfg, embedding_mgr)
            if _KG_INDEX["loaded"]:
                qvec = embedding_mgr.encode_text([query])[0]
                qvec = np.asarray(qvec, dtype="float32")
                sims = _KG_INDEX["vectors"] @ qvec  # cosine（已 L2 norm）
                top_idx = np.argsort(-sims)[:n]
                top_names = [_KG_INDEX["names"][i] for i in top_idx]
                top_labels = [_KG_INDEX["labels"][i] for i in top_idx]
                top_scores = [float(sims[i]) for i in top_idx]

                # 拉 1 跳邻居
                cypher = """
                UNWIND $names AS nm
                MATCH (n {kg_name: nm})
                OPTIONAL MATCH (n)-[r]->(neighbor)
                RETURN n.kg_name AS name, labels(n)[0] AS lbl,
                       collect(DISTINCT {rel: type(r), tail: neighbor.kg_name})[0..6] AS edges
                """
                drv = GraphDatabase.driver(
                    neo4j_cfg.get("uri", "bolt://localhost:7687"),
                    auth=(neo4j_cfg.get("user", "neo4j"),
                          neo4j_cfg.get("pass", neo4j_cfg.get("password", "neo4j"))),
                )
                rows_by_name = {}
                with drv.session() as s:
                    for row in s.run(cypher, names=top_names).data():
                        rows_by_name[row["name"]] = row
                drv.close()

                chunks = []
                for nm, lbl, score in zip(top_names, top_labels, top_scores):
                    row = rows_by_name.get(nm, {})
                    edges = row.get("edges") or []
                    edge_lines = []
                    for e in edges:
                        if e and e.get("rel") and e.get("tail"):
                            edge_lines.append(f"  -[{e['rel']}]→ {e['tail']}")
                    edge_str = "\n".join(edge_lines) if edge_lines else "  (no outgoing edges)"
                    text = f"[KG entity: {nm} ({lbl})]\n{edge_str}"
                    chunks.append({
                        "id": f"kg::{nm[:80]}",
                        "text": text,
                        "source": f"KG-{lbl}",
                        "page": 0,
                        "distance": score,  # 余弦相似度
                        "chunk_type": "kg_subgraph",
                        "image_path": "",
                        "image_url": None,
                        "rerank_score": None,
                        "kg_anchor": nm,
                        "kg_ann_score": score,
                    })
                return chunks
        except Exception as e:
            import traceback
            print(f"[kg_search ANN] err: {e}, fallback to keyword")
            traceback.print_exc()

    # ── 关键词降级（向后兼容） ─────────────────────────────
    import re
    en_tokens = [t for t in re.findall(r"[A-Za-z][A-Za-z0-9_/\-]*", query) if len(t) >= 3]
    anchors = en_tokens[:4]
    if not anchors:
        return []
    cypher = """
    UNWIND $anchors AS kw
    MATCH (n) WHERE n.kg_name CONTAINS kw
    WITH n, kw LIMIT 30
    OPTIONAL MATCH (n)-[r]->(neighbor)
    RETURN n.kg_name AS name, labels(n)[0] AS lbl,
           collect(DISTINCT {rel: type(r), tail: neighbor.kg_name})[0..6] AS edges,
           kw AS hit_keyword
    LIMIT $n
    """
    chunks = []
    try:
        drv = GraphDatabase.driver(
            neo4j_cfg.get("uri", "bolt://localhost:7687"),
            auth=(neo4j_cfg.get("user", "neo4j"),
                  neo4j_cfg.get("pass", neo4j_cfg.get("password", "neo4j"))),
        )
        with drv.session() as s:
            for row in s.run(cypher, anchors=anchors, n=n).data():
                name = row.get("name", "")
                lbl = row.get("lbl", "")
                edges = row.get("edges") or []
                edge_lines = []
                for e in edges:
                    if e and e.get("rel") and e.get("tail"):
                        edge_lines.append(f"  -[{e['rel']}]→ {e['tail']}")
                edge_str = "\n".join(edge_lines) if edge_lines else "  (no outgoing edges)"
                text = f"[KG entity: {name} ({lbl})]\n{edge_str}"
                chunks.append({
                    "id": f"kg::{name[:80]}",
                    "text": text,
                    "source": f"KG-{lbl}",
                    "page": 0,
                    "distance": 1.0,
                    "chunk_type": "kg_subgraph",
                    "image_path": "",
                    "image_url": None,
                    "rerank_score": None,
                    "kg_anchor": name,
                })
        drv.close()
    except Exception as e:
        print(f"[retrieve_ablation] KG search error: {e}")
    return chunks


@router.post("/retrieve_ablation", response_model=RetrieveResponse,
             summary="消融实验端点（按 path_mask 启用各路径）")
def retrieve_ablation(body: AblationRequest, state: AppState = Depends(get_state)):
    """
    支持论文§4.6 消融的 4 路检索：
      paths=['dense']                  -> Dense-only
      paths=['bm25']                   -> BM25-only
      paths=['dense','bm25']           -> Hybrid (RRF)
      paths=['dense','bm25','clip']    -> +CLIP
      paths=['dense','bm25','clip','kg'] -> MHRAG full
    """
    total = state.get_doc_count()
    if total == 0:
        return RetrieveResponse(chunks=[])

    paths = set(body.paths or [])
    n = min(body.recall_n, total)

    dense_results = []
    bm25_results = []
    clip_results = []
    kg_results = []

    if "dense" in paths:
        try:
            dense_results = qdrant_search_text(state.qdrant_client, state.embedding_mgr, body.query, n)
        except Exception as e:
            print(f"[retrieve_ablation] dense err: {e}")

    if "bm25" in paths:
        try:
            bm25_results = bm25_search_text(state.bm25_manager, body.query, n * 2)
        except Exception as e:
            print(f"[retrieve_ablation] bm25 err: {e}")

    if "clip" in paths:
        try:
            clip_results = qdrant_search_image(state.qdrant_client, state.embedding_mgr, body.query,
                                                 max(1, n // 2))
        except Exception as e:
            print(f"[retrieve_ablation] clip err: {e}")

    if "kg" in paths:
        neo4j_cfg = {
            "uri": os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            "user": os.getenv("NEO4J_USER", "neo4j"),
            "pass": os.getenv("NEO4J_PASS", "password"),
        }
        kg_results = kg_search_neo4j(
            neo4j_cfg, body.query, max(1, n // 2),
            embedding_mgr=state.embedding_mgr,
        )

    # 融合 dense + bm25
    if "dense" in paths and "bm25" in paths and dense_results and bm25_results:
        text_fused = reciprocal_rank_fusion(dense_results, bm25_results, k=body.fusion_k)
    elif "dense" in paths:
        text_fused = dense_results
    elif "bm25" in paths:
        # 单 BM25：从 Qdrant 拿 payload
        ids = [b["id"] for b in bm25_results[:n]]
        text_fused = []
        if ids:
            try:
                points = state.qdrant_client.retrieve(
                    collection_name=COLLECTION_NAME, ids=ids, with_payload=True,
                )
                id_map = {str(p.id): p for p in points}
                for b in bm25_results[:n]:
                    p = id_map.get(b["id"])
                    if p:
                        payload = p.payload or {}
                        text_fused.append({
                            "id": str(p.id),
                            "text": payload.get("text", ""),
                            "source": payload.get("source", "未知"),
                            "page": payload.get("page", 0),
                            "distance": b["bm25_score"],
                            "chunk_type": payload.get("chunk_type", "text"),
                            "image_path": payload.get("image_path", ""),
                            "image_url": _image_url(payload.get("image_path", "")),
                            "rerank_score": None,
                        })
            except Exception as e:
                print(f"[retrieve_ablation] bm25 payload err: {e}")
    else:
        text_fused = []

    # 合并 text_fused + clip + kg
    all_results = []
    seen_ids = set()
    for c in text_fused + clip_results + kg_results:
        cid = c["id"]
        if cid not in seen_ids:
            seen_ids.add(cid)
            all_results.append(c)

    if body.use_rerank and state.reranker is not None and all_results:
        try:
            pairs = [(body.query, c["text"]) for c in all_results]
            scores = state.reranker.predict(pairs)
            for c, s in zip(all_results, scores):
                c["rerank_score"] = float(s)
            all_results = sorted(all_results, key=lambda c: c["rerank_score"], reverse=True)
        except Exception as e:
            print(f"[retrieve_ablation] rerank err: {e}")

    top = all_results[:body.top_k]
    chunks = [
        ChunkResult(
            text=(c.get("text") or "")[:2000],
            source=c.get("source") or "未知",
            page=c.get("page", 0),
            distance=c.get("distance", 0.0),
            rerank_score=c.get("rerank_score"),
            chunk_type=c.get("chunk_type", "text"),
            image_url=c.get("image_url"),
        )
        for c in top
    ]
    return RetrieveResponse(chunks=chunks)
