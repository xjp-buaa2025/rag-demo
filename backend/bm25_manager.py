"""
backend/bm25_manager.py — BM25 稀疏检索索引管理

封装 BM25 关键词检索，与 Qdrant Dense 检索配合实现混合检索（Hybrid Retrieval）。

核心功能：
  - 使用 rank_bm25（BM25Okapi）构建关键词倒排索引
  - 双轨分词：regex 提取英文/零件编码 + jieba 中文分词（中英文混合文档友好）
  - 持久化到 storage/bm25_index.pkl，重启自动恢复
  - 支持按 doc_id 增量删除，透明从 Qdrant 重建（透明迁移，无需重新入库）

与 Qdrant 的关系：
  - 每条 BM25 记录对应一个 Qdrant 文本块，以 point_uuid 为公共主键
  - 图片块不参与 BM25（chunk_type="image" 的块不加入索引）
"""

import os
import re
import pickle
import threading
import logging
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)


class BM25Manager:
    """
    BM25 关键词检索索引管理器。线程安全（读写均持锁）。

    内部维护三个并行结构：
      _ids     — Qdrant point UUID 列表
      _corpus  — 对应的分词 token 列表
      _doc_to_ids — doc_id -> [point_uuid, ...] 映射（增量删除用）
    """

    def __init__(self, index_path: str):
        self._lock = threading.Lock()
        self._index_path = index_path
        self._ids: List[str] = []
        self._corpus: List[List[str]] = []
        self._doc_to_ids: dict = {}
        self._bm25 = None   # BM25Okapi 实例，None 表示索引为空
        self._load_or_init()

    # ------------------------------------------------------------------
    # 公开接口
    # ------------------------------------------------------------------

    def search(self, query: str, n: int) -> List[Tuple[str, float]]:
        """
        对 query 执行 BM25 检索，返回 [(point_uuid, normalized_score), ...]。
        score 归一化到 [0, 1]（除以 max_score）。
        n=0 时返回全部（调试用）。线程安全。
        """
        with self._lock:
            if self._bm25 is None or not self._ids:
                return []
            tokens = self._tokenize(query)
            if not tokens:
                return []
            scores = self._bm25.get_scores(tokens)
            ids_snapshot = list(self._ids)

        max_score = float(scores.max()) if len(scores) > 0 else 0.0
        if max_score <= 0:
            return []

        norm_scores = scores / max_score
        top_n = n if n > 0 else len(ids_snapshot)
        top_indices = norm_scores.argsort()[::-1][:top_n]
        return [
            (ids_snapshot[i], float(norm_scores[i]))
            for i in top_indices
            if norm_scores[i] > 0
        ]

    def add_documents(self, id_text_pairs: List[Tuple[str, str]],
                      doc_id: str = None) -> None:
        """
        增量添加文档。按 point_uuid 去重（已存在则跳过，实现幂等）。
        重建 BM25 并异步持久化。

        Args:
            id_text_pairs: [(point_uuid, text), ...] 列表
            doc_id:        可选，关联的文档 ID（用于按文档批量删除）
        """
        if not id_text_pairs:
            return
        with self._lock:
            existing_ids = set(self._ids)
            added_ids = []
            for pid, text in id_text_pairs:
                if pid not in existing_ids:
                    tokens = self._tokenize(text)
                    self._ids.append(pid)
                    self._corpus.append(tokens)
                    existing_ids.add(pid)
                    added_ids.append(pid)
            if not added_ids:
                return
            if doc_id is not None:
                self._doc_to_ids.setdefault(doc_id, []).extend(added_ids)
            self._rebuild_bm25()
        self._save_async()

    def remove_by_doc_id(self, doc_id: str) -> None:
        """
        通过 doc_id 批量删除关联的所有文档块。
        重建 BM25 并异步持久化。
        """
        with self._lock:
            ids_to_remove = set(self._doc_to_ids.pop(doc_id, []))
            if not ids_to_remove:
                return
            keep = [
                (pid, tok) for pid, tok in zip(self._ids, self._corpus)
                if pid not in ids_to_remove
            ]
            if keep:
                self._ids, self._corpus = map(list, zip(*keep))
            else:
                self._ids, self._corpus = [], []
            self._rebuild_bm25()
        self._save_async()

    def rebuild_from_qdrant(self, qdrant_client, collection_name: str) -> int:
        """
        从 Qdrant 全量重建 BM25 索引（透明迁移，启动时调用）。
        只拉 chunk_type="text" 的点，分页 scroll 避免内存峰值（每批 500）。
        返回重建的文档数。
        """
        try:
            from qdrant_client.models import Filter, FieldCondition, MatchValue
        except ImportError:
            logger.error("[BM25] qdrant_client 未安装，无法重建索引")
            return 0

        new_ids: List[str] = []
        new_corpus: List[List[str]] = []
        new_doc_to_ids: dict = {}
        offset = None

        while True:
            try:
                results, next_offset = qdrant_client.scroll(
                    collection_name=collection_name,
                    scroll_filter=Filter(
                        must=[FieldCondition(
                            key="chunk_type",
                            match=MatchValue(value="text")
                        )]
                    ),
                    with_payload=["text", "doc_id"],
                    limit=500,
                    offset=offset,
                )
            except Exception as e:
                logger.error(f"[BM25] Qdrant scroll 失败: {e}")
                break

            for p in results:
                payload = p.payload or {}
                text = payload.get("text", "").strip()
                if not text:
                    continue
                pid = str(p.id)
                new_ids.append(pid)
                new_corpus.append(self._tokenize(text))
                doc_id = payload.get("doc_id", "")
                if doc_id:
                    new_doc_to_ids.setdefault(doc_id, []).append(pid)

            if next_offset is None or len(results) < 500:
                break
            offset = next_offset

        with self._lock:
            self._ids = new_ids
            self._corpus = new_corpus
            self._doc_to_ids = new_doc_to_ids
            self._rebuild_bm25()

        self._save_async()
        return len(new_ids)

    def reset(self) -> None:
        """清空所有数据并删除 pkl 文件（clear_first 入库时调用）。"""
        with self._lock:
            self._ids = []
            self._corpus = []
            self._doc_to_ids = {}
            self._bm25 = None
        try:
            if os.path.exists(self._index_path):
                os.remove(self._index_path)
        except Exception:
            pass

    def has_index(self) -> bool:
        """判断 pkl 持久化文件是否存在（启动时决定是否重建）。"""
        return os.path.exists(self._index_path)

    def doc_count(self) -> int:
        """返回当前索引中的文档数（线程安全）。"""
        with self._lock:
            return len(self._ids)

    # ------------------------------------------------------------------
    # 内部方法
    # ------------------------------------------------------------------

    def _tokenize(self, text: str) -> List[str]:
        """
        双轨分词策略（中英文混合文档）：
          轨道1：regex 提取英文/数字/零件编码（如 P/N-1234、ABC-XYZ-001、v1.2）
                 匹配 [A-Za-z0-9][A-Za-z0-9\\-/\\.\\:_]*，长度 > 1，统一转小写
          轨道2：jieba 中文分词（过滤纯 ASCII token，避免与轨道1重复）
        合并去重后返回。
        """
        # 轨道1：英文/数字/零件编码（含子 token 扩展，提升部分匹配能力）
        code_pattern = re.compile(r'[A-Za-z0-9][A-Za-z0-9\-/\.\:_]*')
        code_tokens = []
        for m in code_pattern.finditer(text):
            token = m.group().lower()
            if len(token) <= 1:
                continue
            code_tokens.append(token)
            # 去除尾部标点（如 "p/n:" → 追加 "p/n"）
            stripped = token.rstrip('.:,;_')
            if stripped != token and len(stripped) > 1:
                code_tokens.append(stripped)
            # 连字符拆分（如 "1234567-a" → 追加 "1234567"、"a"）
            if '-' in token:
                for part in token.split('-'):
                    if len(part) > 1:
                        code_tokens.append(part)

        # 轨道2：jieba 中文分词
        try:
            import jieba
            cn_tokens = [
                t.strip() for t in jieba.lcut(text)
                if len(t.strip()) > 1 and not t.strip().isascii()
            ]
        except ImportError:
            cn_tokens = []

        return list(set(code_tokens + cn_tokens))

    def _rebuild_bm25(self) -> None:
        """用当前 _corpus 重建 BM25Okapi 对象（须在锁内调用）。"""
        if not self._corpus:
            self._bm25 = None
            return
        try:
            from rank_bm25 import BM25Okapi
            self._bm25 = BM25Okapi(self._corpus)
        except ImportError:
            logger.error("[BM25] rank_bm25 未安装，BM25 检索不可用")
            self._bm25 = None
        except Exception as e:
            logger.error(f"[BM25] 重建索引失败: {e}")
            self._bm25 = None

    def _save_async(self) -> None:
        """在后台线程将索引序列化到 pkl（不阻塞调用方）。使用 tmp+replace 保证原子写入。"""
        def _write():
            with self._lock:
                data = {
                    "version": 1,
                    "ids": list(self._ids),
                    "corpus": list(self._corpus),
                    "doc_to_ids": dict(self._doc_to_ids),
                }
            try:
                os.makedirs(os.path.dirname(self._index_path) or ".", exist_ok=True)
                tmp_path = self._index_path + ".tmp"
                with open(tmp_path, "wb") as f:
                    pickle.dump(data, f, protocol=4)
                os.replace(tmp_path, self._index_path)
                logger.debug(f"[BM25] 索引已持久化（{len(data['ids'])} 个文档）")
            except Exception as e:
                logger.warning(f"[BM25] 持久化失败（{e}），内存索引仍有效")

        threading.Thread(target=_write, daemon=True).start()

    def _load_or_init(self) -> None:
        """启动时尝试从 pkl 加载；文件不存在或损坏则静默初始化为空索引。"""
        if not os.path.exists(self._index_path):
            return
        try:
            with open(self._index_path, "rb") as f:
                data = pickle.load(f)
            self._ids = data.get("ids", [])
            self._corpus = data.get("corpus", [])
            self._doc_to_ids = data.get("doc_to_ids", {})
            self._rebuild_bm25()
            logger.info(f"[BM25] 索引加载完成（{len(self._ids)} 个文档）")
        except Exception as e:
            logger.warning(f"[BM25] 索引加载失败（{e}），将在首次入库时重建")
            self._ids, self._corpus, self._doc_to_ids = [], [], {}
