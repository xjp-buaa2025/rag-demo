"""
backend/state.py — 全局应用状态

持有所有需要在请求间共享的单例对象：
  - ChromaDB 客户端 + 集合
  - Embedding 函数（SentenceTransformer）
  - LLM 客户端（支持主备降级）
  - Neo4j 驱动（懒加载，None 直到首次调用）
  - 线程锁（保护并发写操作）

设计原因：
  FastAPI 是多线程（uvicorn + threadpool）模型，所有请求共享同一进程内存。
  将单例放在 AppState 中（通过 app.state.app_state 访问），而非模块级全局变量，
  方便测试时注入 mock 对象，也避免循环导入问题。
"""

import os
import threading
from dataclasses import dataclass, field
from typing import List, Optional, Any

from sentence_transformers import SentenceTransformer


class FallbackLLMClient:
    """
    优先调用主 LLM（MiniMax），失败时自动 fallback 到备用（SiliconFlow）。
    接口与 openai.OpenAI 完全兼容（client.chat.completions.create(...)）。
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


class LocalEmbeddingFunction:
    """SentenceTransformer 的 ChromaDB 接口包装。"""
    def __init__(self, model_name: str):
        self.model = SentenceTransformer(model_name)
        self._model_name = model_name

    def name(self) -> str:
        return self._model_name

    def __call__(self, input: List[str]) -> List[List[float]]:
        return self.model.encode(input).tolist()


@dataclass
class AppState:
    """应用级全局状态，由 lifespan 在启动时初始化，通过 app.state.app_state 访问。"""
    embedding_func: LocalEmbeddingFunction
    chroma_client: Any          # chromadb.PersistentClient
    collection: Any             # chromadb.Collection
    llm_client: Any             # FallbackLLMClient 或 openai.OpenAI
    active_model_label: str
    neo4j_driver: Optional[Any] = None
    is_ingesting: bool = False          # 防并发：入库期间置 True，结束后清除
    collection_lock: threading.Lock = field(default_factory=threading.Lock)
    neo4j_lock: threading.Lock = field(default_factory=threading.Lock)
