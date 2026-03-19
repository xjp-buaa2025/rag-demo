"""
backend/routers/retrieve.py — 向量检索接口

POST /retrieve
  请求体：{"query": "用户问题", "top_k": 4, "use_rerank": true}
  响应：{"chunks": [{"text", "source", "page", "distance", "rerank_score"}, ...]}

同步 JSON 接口，毫秒级响应（reranker 打分约增加 50-200ms）。
use_rerank=true 时先召回 top_k*3 个候选，再用 CrossEncoder 精排取 top_k，
可通过对比 use_rerank=false/true 的结果验证重排序效果。
"""

from typing import List, Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from backend.deps import get_state
from backend.state import AppState

router = APIRouter()

RETRIEVE_RECALL_MULTIPLIER = 3   # 召回倍数：retrieve 接口召回 top_k * 3 个再精排
RETRIEVE_RECALL_MAX = 20         # 最大召回数上限


class RetrieveRequest(BaseModel):
    query: str
    top_k: int = Field(default=4, ge=1, le=20)
    use_rerank: bool = True      # 是否启用重排序（False 则直接按距离排序）


class ChunkResult(BaseModel):
    text: str
    source: str
    page: int = 0
    distance: float
    rerank_score: Optional[float] = None  # 重排序分数，use_rerank=true 时填充


class RetrieveResponse(BaseModel):
    chunks: List[ChunkResult]


@router.post("/retrieve", response_model=RetrieveResponse, summary="向量检索（支持重排序）")
def retrieve(body: RetrieveRequest, state: AppState = Depends(get_state)):
    """
    对 ChromaDB 执行向量检索。
    use_rerank=true 时先召回更多候选，用 CrossEncoder 精排后取 top_k。
    n_results 不能超过 collection 总数，用 min() 保护。
    """
    total = state.collection.count()
    if total == 0:
        return RetrieveResponse(chunks=[])

    # 若启用重排序，先召回更多候选
    recall_n = min(body.top_k * RETRIEVE_RECALL_MULTIPLIER, RETRIEVE_RECALL_MAX, total)
    if not body.use_rerank or state.reranker is None:
        recall_n = min(body.top_k, total)

    query_embedding = state.embedding_func([body.query])[0]
    results = state.collection.query(
        query_embeddings=[query_embedding],
        n_results=recall_n,
        include=["ids", "documents", "metadatas", "distances"],
    )

    candidates = [
        {
            "text": doc,
            "source": meta.get("source", "未知"),
            "page": meta.get("page", 0),
            "distance": dist,
            "rerank_score": None,
        }
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        )
    ]

    # 重排序
    if body.use_rerank and state.reranker is not None:
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
            rerank_score=c["rerank_score"],
        )
        for c in top
    ]
    return RetrieveResponse(chunks=chunks)
