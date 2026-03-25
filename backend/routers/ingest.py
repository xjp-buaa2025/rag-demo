"""
backend/routers/ingest.py — 知识库入库接口

POST /ingest          — 扫描 data/ 目录并入库（SSE 流式日志，原生模式）
POST /ingest/pipeline — 单文件 LangGraph 管道入库（SSE 流式日志）
GET  /ingest/status   — 返回当前知识库文档块数量（JSON）

入库逻辑：
  - 文本块：deepdoc 解析 → bge-m3 向量 → Qdrant text_vec
  - 图片块：PyMuPDF 提取图片 → MiniMax Vision Caption → bge-m3（Caption）+ Chinese-CLIP（图片）双向量 → Qdrant
  - 用 collection_lock 防并发写冲突
"""

import os
import uuid
from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from pydantic import BaseModel
from typing import Optional

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


@router.post("/ingest/pipeline", summary="LangGraph 管道入库单文件（SSE）")
def ingest_pipeline(
    request: Request,
    file: Optional[UploadFile] = File(default=None),
    clear_first: bool = Form(default=False),
    state: AppState = Depends(get_state),
):
    """
    LangGraph 管道入库：上传单个文件（PDF/MD/TXT），通过节点化流程处理。
    - PDF：pdf_to_md（转Markdown+提取图片）→ generate_captions → chunk_text → 向量化 → Qdrant
    - MD/TXT：直接 chunk_text → 向量化 → Qdrant
    响应为 SSE 日志流。
    """
    import tempfile
    from backend.pipelines.sse_bridge import pipeline_to_log_generator

    if state.lg_rag_pipeline is None:
        def _err():
            yield "❌ LangGraph RAG 管道未初始化，请检查后端日志"
        return log_gen_to_sse(_err())

    if file is None:
        def _err():
            yield "❌ 请上传文件（PDF/MD/TXT）"
        return log_gen_to_sse(_err())

    # 将上传文件写入临时目录
    suffix = os.path.splitext(file.filename or "doc.pdf")[1] or ".pdf"
    tmp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    try:
        tmp.write(file.file.read())
        tmp.close()
        tmp_path = tmp.name
    except Exception as e:
        def _err():
            yield f"❌ 文件保存失败: {e}"
        return log_gen_to_sse(_err())

    image_dir = request.app.state.image_dir
    initial_state = {
        "file_path": tmp_path,
        "pipeline_mode": "rag",
        "clear_first": clear_first,
        "log_messages": [f"[pipeline] 开始处理：{file.filename}"],
    }

    def _cleanup_gen():
        try:
            yield from pipeline_to_log_generator(state.lg_rag_pipeline, initial_state)
        finally:
            try:
                os.remove(tmp_path)
            except Exception:
                pass

    return log_gen_to_sse(_cleanup_gen())


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
    all_files = sorted([
        f for f in os.listdir(data_dir)
        if os.path.isfile(os.path.join(data_dir, f))
    ])

    # 构建处理计划：.md 优先文本，对应 .pdf 仅提取图片
    plan = []  # [(fname, images_only), ...]
    md_stems = set()
    for f in all_files:
        if f.lower().endswith('.md'):
            md_stems.add(os.path.splitext(f)[0])
            plan.append((f, False))
    for f in all_files:
        if f.lower().endswith('.pdf'):
            stem = os.path.splitext(f)[0]
            if stem in md_stems:
                plan.append((f, True))   # 有 .md → 仅提取图片
            else:
                plan.append((f, False))  # 无 .md → 文本+图片

    if not plan:
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

    yield emit(f"📂  共发现 {len(plan)} 个文件，开始处理…\n")

    total_all = 0
    for fname, img_only in plan:
        file_path = os.path.join(data_dir, fname)
        mode = "（仅图片）" if img_only else ""
        yield emit(f"▶  {fname} {mode}")

        chunk_dicts = process_document(file_path, image_dir=image_dir, images_only=img_only)
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

                # 生成 Caption（优先 MiniMax Vision，降级为页面上下文文字）
                caption = ""
                if state.minimax_client and state.minimax_model:
                    from backend.image_captioner import describe_image
                    yield emit(f"   📷  生成 Caption: {os.path.basename(image_path)}")
                    caption = describe_image(
                        state.minimax_client, state.minimax_model,
                        image_path, chunk.get("context_text", "")
                    )
                if not caption:
                    fallback = chunk.get("context_text", "").strip()
                    if fallback:
                        caption = fallback
                        yield emit(f"   📝  使用页面文字做降级 Caption: {os.path.basename(image_path)}")
                    else:
                        yield emit(f"   ⚠️  无 Caption 也无页面文字，跳过: {os.path.basename(image_path)}")
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
