"""
backend/routers/ingest.py — 知识库入库接口

POST /ingest          — 扫描 data/ 目录并入库（SSE 流式日志）
GET  /ingest/status   — 返回当前知识库文档块数量（JSON）

入库逻辑：
  - 文本块：deepdoc 解析 → bge-m3 向量 → Qdrant text_vec
  - 图片块：PyMuPDF 提取图片 → MiniMax Vision Caption → bge-m3（Caption）+ Chinese-CLIP（图片）双向量 → Qdrant
  - 用 collection_lock 防并发写冲突
"""

import os
import uuid
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from backend.deps import get_state
from backend.state import AppState, COLLECTION_NAME
from backend.sse import log_gen_to_sse

router = APIRouter()


class IngestRequest(BaseModel):
    clear_first: bool = False


@router.get("/ingest/status", summary="知识库状态")
def ingest_status(state: AppState = Depends(get_state)):
    """返回当前知识库文档块总数。"""
    return {"count": state.get_doc_count()}


@router.post("/ingest", summary="扫描 data/ 目录并入库（SSE）")
def ingest(body: IngestRequest, request: Request, state: AppState = Depends(get_state)):
    """
    扫描 data/ 目录，逐文件解析并写入 Qdrant（图文双向量）。
    响应为 SSE 流，每条事件携带完整日志快照：data: {"log": "..."}\n\n
    结束时发送：data: [DONE]\n\n
    """
    data_dir = request.app.state.data_dir
    image_dir = request.app.state.image_dir
    gen = _run_ingest(state, data_dir, body.clear_first, image_dir)
    return log_gen_to_sse(gen)


def _run_ingest(state: AppState, data_dir: str, clear_first: bool,
                image_dir: str = None):
    """
    入库生成器，yield 完整日志快照字符串。
    collection_lock 防并发，is_ingesting 标志防重入。
    """
    with state.collection_lock:
        if state.is_ingesting:
            yield "⚠️  已有入库任务正在运行，请稍候再试。"
            return
        state.is_ingesting = True

    try:
        yield from _do_ingest(state, data_dir, clear_first, image_dir)
    finally:
        state.is_ingesting = False


def _do_ingest(state: AppState, data_dir: str, clear_first: bool,
               image_dir: str = None):
    """实际入库逻辑（由 _run_ingest 调用）。"""
    from main_ingest import process_document, _make_doc_id
    from PIL import Image as PILImage
    from qdrant_client.models import PointStruct, FilterSelector, Filter, FieldCondition, MatchValue

    if image_dir is None:
        # 推断默认图片目录
        image_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__)))), "storage", "images")
    os.makedirs(image_dir, exist_ok=True)

    lines = []

    def emit(msg: str) -> str:
        lines.append(msg)
        return "\n".join(lines)

    os.makedirs(data_dir, exist_ok=True)
    files = sorted([
        f for f in os.listdir(data_dir)
        if os.path.isfile(os.path.join(data_dir, f))
    ])
    # 跳过已有对应 .md 的 PDF
    files = [
        f for f in files
        if not (f.lower().endswith('.pdf') and
                os.path.exists(os.path.join(data_dir, os.path.splitext(f)[0] + '.md')))
    ]

    if not files:
        yield emit("⚠️  data/ 目录下没有找到任何文件，请先放入文档。")
        return

    if clear_first:
        with state.collection_lock:
            try:
                state.qdrant_client.delete_collection(COLLECTION_NAME)
                from backend.main import _init_qdrant, QDRANT_DB_PATH
                state.qdrant_client = _init_qdrant(QDRANT_DB_PATH, COLLECTION_NAME)
                yield emit("🗑️  已清空旧数据，重新开始入库…")
            except Exception as e:
                yield emit(f"清空失败: {e}")
                return

    yield emit(f"📂  共发现 {len(files)} 个文件，开始处理…\n")

    total_all = 0
    for fname in files:
        file_path = os.path.join(data_dir, fname)
        yield emit(f"▶  {fname}")

        chunk_dicts = process_document(file_path, image_dir=image_dir)
        if not chunk_dicts:
            yield emit("   ⚠️  无有效内容，跳过")
            continue

        doc_id = _make_doc_id(file_path)

        # 增量更新：先删旧块
        try:
            state.qdrant_client.delete(
                collection_name=COLLECTION_NAME,
                points_selector=FilterSelector(
                    filter=Filter(
                        must=[FieldCondition(key="doc_id", match=MatchValue(value=doc_id))]
                    )
                ),
            )
        except Exception:
            pass

        points = []
        for i, chunk in enumerate(chunk_dicts):
            chunk_id = f"{doc_id}_{i}"
            point_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk_id))

            if chunk["chunk_type"] == "text":
                text_vec  = state.embedding_mgr.encode_text([chunk["text"]])[0].tolist()
                image_vec = state.embedding_mgr.zero_image_vec()
                points.append(PointStruct(
                    id=point_uuid,
                    vector={"text_vec": text_vec, "image_vec": image_vec},
                    payload={
                        "text":        chunk["text"],
                        "source":      fname,
                        "page":        chunk["page"],
                        "chunk_type":  "text",
                        "image_path":  "",
                        "doc_id":      doc_id,
                        "chunk_index": i,
                    },
                ))

            elif chunk["chunk_type"] == "image":
                image_path = chunk["image_path"]

                # 生成 Caption
                caption = ""
                if state.minimax_client and state.minimax_model:
                    from backend.image_captioner import describe_image
                    yield emit(f"   📷  生成 Caption: {os.path.basename(image_path)}")
                    caption = describe_image(
                        state.minimax_client, state.minimax_model,
                        image_path, chunk.get("context_text", "")
                    )
                if not caption:
                    yield emit(f"   ⚠️  Caption 失败，跳过: {os.path.basename(image_path)}")
                    continue

                # 编码 Caption → text_vec
                text_vec = state.embedding_mgr.encode_text([caption])[0].tolist()

                # 编码图片 → image_vec（Chinese-CLIP）
                try:
                    pil_img   = PILImage.open(image_path).convert("RGB")
                    image_vec = state.embedding_mgr.encode_images_clip([pil_img])[0].tolist()
                except Exception as e:
                    yield emit(f"   ⚠️  CLIP 编码失败（{e}），跳过: {os.path.basename(image_path)}")
                    continue

                points.append(PointStruct(
                    id=point_uuid,
                    vector={"text_vec": text_vec, "image_vec": image_vec},
                    payload={
                        "text":        caption,
                        "source":      fname,
                        "page":        chunk["page"],
                        "chunk_type":  "image",
                        "image_path":  image_path,
                        "doc_id":      doc_id,
                        "chunk_index": i,
                    },
                ))

        # 分批写入 Qdrant
        total = len(points)
        batch_size = 32
        yield emit(f"   向量化完成，写入 {total} 个块（批大小 {batch_size}）…")
        for start in range(0, total, batch_size):
            batch = points[start: start + batch_size]
            state.qdrant_client.upsert(collection_name=COLLECTION_NAME, points=batch)
            end = min(start + batch_size, total)
            yield emit(f"   [{end}/{total}] 已写入…")

        yield emit(f"   ✅  {fname} 入库完成（{total} 块）")
        total_all += total

    count = state.get_doc_count()
    yield emit(f"\n🎉  全部完成！本次入库 {total_all} 块，知识库共 {count} 条文档块。")
