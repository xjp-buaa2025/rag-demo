"""
backend/state.py — 全局应用状态

持有所有需要在请求间共享的单例对象：
  - Qdrant 本地客户端（QdrantClient，替代 ChromaDB）
  - EmbeddingManager（bge-m3 + Chinese-CLIP 双模型）
  - LLM 客户端（支持主备降级）
  - minimax_client：用于 Vision API（图片Caption生成）
  - Reranker（CrossEncoder，可选）
  - Neo4j 驱动（懒加载）
  - 线程锁（保护并发写操作）
"""

import threading
from dataclasses import dataclass, field
from typing import Optional, Any


class FallbackLLMClient:
    """
    优先调用主 LLM（MiniMax），失败时自动 fallback 到备用（SiliconFlow）。
    接口与 openai.OpenAI 完全兼容（client.chat.completions.create(...)）。
    Vision 调用请直接使用 AppState.minimax_client（SiliconFlow 不支持多模态）。
    """
    def __init__(self, primary_client, primary_model, fallback_client=None, fallback_model=None):
        self._primary = primary_client
        self._primary_model = primary_model
        self._fallback = fallback_client
        self._fallback_model = fallback_model
        self.chat = self._Chat(self)

    class _Chat:
        def __init__(self, outer):
            self.completions = FallbackLLMClient._Completions(outer)

    class _Completions:
        def __init__(self, outer):
            self._outer = outer

        def create(self, model=None, **kwargs):
            try:
                return self._outer._primary.chat.completions.create(
                    model=self._outer._primary_model, **kwargs
                )
            except Exception as e:
                if self._outer._fallback is None:
                    raise
                print(f"  ⚠️  主 LLM 失败（{e}），切换到备用 LLM…")
                return self._outer._fallback.chat.completions.create(
                    model=self._outer._fallback_model, **kwargs
                )


COLLECTION_NAME = "rag_knowledge"


@dataclass
class AppState:
    """应用级全局状态，由 lifespan 在启动时初始化，通过 app.state.app_state 访问。"""
    # --- 核心组件 ---
    qdrant_client: Any              # qdrant_client.QdrantClient（本地文件存储）
    embedding_mgr: Any              # backend.embedding_manager.EmbeddingManager（bge-m3 + Chinese-CLIP）
    llm_client: Any                 # FallbackLLMClient 或 openai.OpenAI
    active_model_label: str

    # --- Vision 专用（图片 Caption，不走 FallbackLLMClient）---
    minimax_client: Optional[Any] = None   # 原始 openai.OpenAI(MiniMax) 实例
    minimax_model: str = ""

    # --- 可选组件 ---
    reranker: Optional[Any] = None         # CrossEncoder，None 则按距离排序
    neo4j_driver: Optional[Any] = None

    # --- LangChain 组件（渐进式启用，由 lifespan 初始化）---
    lc_chat_model: Optional[Any] = None       # FallbackChatModel（langchain_components.models）
    lc_retriever: Optional[Any] = None        # QdrantDualPathRetriever（langchain_components.retrievers）
    lc_memory_manager: Optional[Any] = None   # ChatMemoryManager（langchain_components.memory）
    lc_agent: Optional[Any] = None            # AgentExecutor（langchain_components.agents）

    # --- 并发控制 ---
    is_ingesting: bool = False
    collection_lock: threading.Lock = field(default_factory=threading.Lock)
    neo4j_lock: threading.Lock = field(default_factory=threading.Lock)

    def get_doc_count(self) -> int:
        """查询 Qdrant collection 中的文档块总数。"""
        try:
            info = self.qdrant_client.get_collection(COLLECTION_NAME)
            return info.points_count or 0
        except Exception:
            return 0
