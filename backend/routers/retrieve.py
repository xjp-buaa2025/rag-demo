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
