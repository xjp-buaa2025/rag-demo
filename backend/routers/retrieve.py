"""
backend/routers/retrieve.py — 向量检索接口

POST /retrieve
  请求体：{"query": "用户问题", "top_k": 4}
  响应：{"chunks": [{"text", "source", "page", "distance"}, ...]}

这是最简单的同步 JSON 接口，无流式，毫秒级响应。
"""

from typing import List
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from backend.deps import get_state
from backend.state import AppState

router = APIRouter()


class RetrieveRequest(BaseModel):
    query: str
    top_k: int = Field(default=4, ge=1, le=20)


class ChunkResult(BaseModel):
    text: str
    source: str
    page: int = 0
    distance: float


class RetrieveResponse(BaseModel):
    chunks: List[ChunkResult]


@router.post("/retrieve", response_model=RetrieveResponse, summary="向量检索")
def retrieve(body: RetrieveRequest, state: AppState = Depends(get_state)):
    """
    对 ChromaDB 执行向量检索，返回 top_k 个最相关文档块。
    n_results 不能超过 collection 总数，用 min() 保护。
    """
    n = min(body.top_k, state.collection.count())
    if n == 0:
        return RetrieveResponse(chunks=[])

    query_embedding = state.embedding_func([body.query])[0]
    results = state.collection.query(
        query_embeddings=[query_embedding],
        n_results=n,
        include=["documents", "metadatas", "distances"],
    )

    chunks = [
        ChunkResult(
            text=doc,
            source=meta.get("source", "未知"),
            page=meta.get("page", 0),
            distance=dist,
        )
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        )
    ]
    return RetrieveResponse(chunks=chunks)
