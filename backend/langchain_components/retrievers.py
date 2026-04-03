"""
backend/langchain_components/retrievers.py — Vector Stores & Retrievers 组件

自定义 BaseRetriever 子类，将现有的双路检索（text_vec + image_vec）+ 去重 +
CrossEncoder 重排序逻辑封装为标准 LangChain Retriever 接口。

核心类：
  QdrantDualPathRetriever — 双路检索 + 重排序，返回 LangChain Document 列表

与现有代码的关系：
  - 内部复用 retrieve.py 中的 qdrant_search_text()、qdrant_search_image()、merge_and_dedup()
  - 这些底层函数保持不变，Retriever 在其上层封装
  - 替换 chat.py 中的 _multi_query_retrieve() 和 _rerank()
"""

from typing import Any, List, Optional

from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from pydantic import Field


class QdrantDualPathRetriever(BaseRetriever):
    """
    自定义双路检索器，封装现有的 Qdrant 检索逻辑为 LangChain Retriever 接口。

    检索流程：
      1. bge-m3 编码 query -> 搜 text_vec（文本块 + Caption 块）
      2. Chinese-CLIP 编码 query -> 搜 image_vec（图片块）
      3. 合并去重（ID 去重，保留 distance 最高的版本）
      4. CrossEncoder 重排序（如果 reranker 可用）
      5. 返回 top_k 个 LangChain Document

    Document.metadata 包含：source, page, distance, rerank_score,
                           chunk_type, image_url, image_path, id
    """

    qdrant_client: Any = None
    embedding_mgr: Any = None
    reranker: Any = None
    bm25_manager: Optional[Any] = None     # BM25Manager，None 时降级为纯 Dense 检索
    collection_name: str = "rag_knowledge"
    recall_k: int = Field(default=8, description="每路检索的初始召回数")
    top_k: int = Field(default=4, description="最终返回的文档数")
    use_rerank: bool = Field(default=True, description="是否启用重排序")

    class Config:
        arbitrary_types_allowed = True

    def _get_doc_count(self) -> int:
        """查询 Qdrant 中的文档块总数。"""
        try:
            info = self.qdrant_client.get_collection(self.collection_name)
            return info.points_count or 0
        except Exception:
            return 0

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        """
        执行双路检索 + 重排序，返回 LangChain Document 列表。
        底层调用 retrieve.py 中的现有函数，保证检索逻辑一致。
        """
        from backend.routers.retrieve import (
            merge_and_dedup,
            qdrant_search_image,
            hybrid_search_text,
        )

        total = self._get_doc_count()
        if total == 0:
            return []

        n = min(self.recall_k, total)

        # 路径 1：Dense + BM25 混合文本检索（RRF 融合）
        text_results = hybrid_search_text(
            self.qdrant_client, self.embedding_mgr, self.bm25_manager, query, n
        )

        # 路径 2：Chinese-CLIP 图片检索（兜底防护）
        image_results = []
        try:
            image_results = qdrant_search_image(
                self.qdrant_client, self.embedding_mgr, query,
                min(self.recall_k // 2, total)
            )
        except Exception as e:
            import traceback
            print(f"[Retriever] CLIP 图片检索失败（{e}），跳过图片路径")
            traceback.print_exc()

        # 合并去重
        candidates = merge_and_dedup(text_results, image_results)

        # 重排序
        if self.use_rerank and self.reranker is not None and candidates:
            try:
                pairs = [(query, c["text"]) for c in candidates]
                scores = self.reranker.predict(pairs)
                for c, score in zip(candidates, scores):
                    c["rerank_score"] = float(score)
                candidates = sorted(
                    candidates, key=lambda c: c["rerank_score"], reverse=True
                )
            except Exception as e:
                print(f"[Retriever] Reranker 打分失败（{e}），降级为距离排序")

        # 取 top_k 并转为 Document
        top = candidates[: self.top_k]
        return [
            Document(
                page_content=c["text"],
                metadata={
                    "source": c["source"],
                    "page": c.get("page", 0),
                    "distance": c["distance"],
                    "rerank_score": c.get("rerank_score"),
                    "chunk_type": c.get("chunk_type", "text"),
                    "image_url": c.get("image_url"),
                    "image_path": c.get("image_path", ""),
                    "id": c["id"],
                },
            )
            for c in top
        ]
