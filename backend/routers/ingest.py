"""
backend/routers/ingest.py — 知识库入库接口

POST /ingest          — 扫描 data/ 目录并入库（SSE 流式日志）
GET  /ingest/status   — 返回当前知识库文档块数量（JSON）

入库逻辑迁移自 app.py run_ingest()：
  - 同步生成器，FastAPI 自动在线程池执行（路由函数为普通 def）
  - collection 写操作用 state.collection_lock 保护，防止并发入库冲突
"""

import os
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from backend.deps import get_state, get_data_dir
from backend.state import AppState
from backend.sse import log_gen_to_sse

router = APIRouter()

# 与 app.py 保持一致的常量
COLLECTION_NAME = "local_rag_knowledge"


class IngestRequest(BaseModel):
    clear_first: bool = False


@router.get("/ingest/status", summary="知识库状态")
def ingest_status(state: AppState = Depends(get_state)):
    """返回当前知识库文档块总数。"""
    return {"count": state.collection.count()}


@router.post("/ingest", summary="扫描 data/ 目录并入库（SSE）")
def ingest(body: IngestRequest, request: Request, state: AppState = Depends(get_state)):
    """
    扫描 data/ 目录，逐文件解析并写入 ChromaDB。
    响应为 SSE 流，每条事件携带完整日志快照：data: {"log": "..."}\n\n
    结束时发送：data: [DONE]\n\n
    """
    data_dir = request.app.state.data_dir
    gen = _run_ingest(state, data_dir, body.clear_first)
    return log_gen_to_sse(gen)


def _run_ingest(state: AppState, data_dir: str, clear_first: bool):
    """
    入库生成器，迁移自 app.py run_ingest()。
    yield 完整日志快照字符串（与 app.py 保持相同的 yield 语义）。
    collection_lock 保护并发检查与 clear_first 时对 state.collection 的替换。
    """
    # 防并发：用 collection_lock 原子地检查并设置 is_ingesting 标志
    with state.collection_lock:
        if state.is_ingesting:
            yield "⚠️  已有入库任务正在运行，请稍候再试。"
            return
        state.is_ingesting = True

    try:
        yield from _do_ingest(state, data_dir, clear_first)
    finally:
        state.is_ingesting = False


def _do_ingest(state: AppState, data_dir: str, clear_first: bool):
    """实际入库逻辑（由 _run_ingest 在持有 is_ingesting 标志时调用）。"""
    from main_ingest import process_document  # 运行时导入，避免循环依赖

    lines = []

    def emit(msg):
        lines.append(msg)
        return "\n".join(lines)

    os.makedirs(data_dir, exist_ok=True)
    files = sorted([
        f for f in os.listdir(data_dir)
        if os.path.isfile(os.path.join(data_dir, f))
    ])

    if not files:
        yield emit("⚠️  data/ 目录下没有找到任何文件，请先放入文档。")
        return

    if clear_first:
        with state.collection_lock:
            try:
                state.chroma_client.delete_collection(name=COLLECTION_NAME)
                state.collection = state.chroma_client.get_or_create_collection(
                    name=COLLECTION_NAME,
                    embedding_function=state.embedding_func,
                    metadata={"hnsw:space": "cosine"},
                )
                yield emit("🗑️  已清空旧数据，重新开始入库…")
            except Exception as e:
                yield emit(f"清空失败: {e}")
                return

    yield emit(f"📂  共发现 {len(files)} 个文件，开始处理…\n")

    for fname in files:
        file_path = os.path.join(data_dir, fname)
        yield emit(f"▶  {fname}")

        chunk_dicts = process_document(file_path)
        if not chunk_dicts:
            yield emit("   ⚠️  无有效内容，跳过")
            continue

        ids       = [f"{fname}_chunk_{i}" for i in range(len(chunk_dicts))]
        documents = [c["text"] for c in chunk_dicts]
        metadatas = [
            {"source": fname, "page": c["page"], "chunk_index": i}
            for i, c in enumerate(chunk_dicts)
        ]

        total = len(chunk_dicts)
        batch_size = 64
        yield emit(f"   向量化并写入 {total} 个块（每批 {batch_size}）…")
        for start in range(0, total, batch_size):
            end = min(start + batch_size, total)
            state.collection.upsert(
                documents=documents[start:end],
                metadatas=metadatas[start:end],
                ids=ids[start:end],
            )
            yield emit(f"   [{end}/{total}] 已写入…")
        yield emit("   ✅  入库完成")

    yield emit(f"\n🎉  全部完成！知识库共 {state.collection.count()} 条文档块。")
