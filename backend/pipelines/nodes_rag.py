"""
backend/pipelines/nodes_rag.py — RAG 管道节点

阶段一（PDF 入口）：
  pdf_to_md         — PDF -> Markdown 文本 + 图片提取
  generate_captions  — 图片 -> MiniMax Vision 中文描述

阶段二（MD 入口，PDF 转换后或直接 MD 文件）：
  chunk_text          — Markdown/TXT -> 文本块切分
  encode_text_vectors — bge-m3 编码文本块
  encode_image_vectors — bge-m3(Caption) + CLIP(图片) 双向量
  upsert_qdrant       — 批量写入 Qdrant

所有节点通过 make_rag_nodes() 工厂函数创建，闭包绑定 AppState。
"""

import os
import uuid
import hashlib
from typing import Any


def make_rag_nodes(app_state: Any, image_dir: str):
    """
    工厂函数：通过闭包绑定 AppState，返回所有 RAG 节点函数的字典。

    Args:
        app_state: AppState 实例
        image_dir: 图片保存目录（storage/images/）
    """

    def _make_doc_id(file_path: str) -> str:
        fname = os.path.basename(file_path)
        return hashlib.sha256(fname.encode()).hexdigest()[:16]

    # ------------------------------------------------------------------
    # 阶段一：PDF 转换
    # ------------------------------------------------------------------

    def pdf_to_md(state: dict) -> dict:
        """PDF -> Markdown 文本 + 图片提取。
        复用 main_ingest.py 的 process_document() 和 extract_images_from_pdf()。"""
        import fitz
        import sys
        sys.path.append(os.path.join(os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)))), "document_processing"))

        from main_ingest import _split_text, extract_images_from_pdf

        file_path = state["file_path"]
        logs = ["[pdf_to_md] 开始解析 PDF…"]

        # 提取文字 -> Markdown
        text_parts = []
        try:
            with fitz.open(file_path) as pdf:
                total_pages = len(pdf)
                pages_with_text = 0
                for page_num, page in enumerate(pdf, 1):
                    page_text = (page.get_text("text") or "").strip()
                    if page_text:
                        pages_with_text += 1
                        text_parts.append(page_text)
                logs.append(f"[pdf_to_md] {total_pages} 页，{pages_with_text} 页有文本")
        except Exception as e:
            return {"error": f"PDF 文字提取失败: {e}", "log_messages": logs}

        markdown_text = "\n\n".join(text_parts)

        # 提取图片
        os.makedirs(image_dir, exist_ok=True)
        img_records = extract_images_from_pdf(file_path, image_dir)
        logs.append(f"[pdf_to_md] 提取到 {len(img_records)} 张图片")

        return {
            "markdown_text": markdown_text,
            "image_records": img_records,
            "current_node": "pdf_to_md",
            "log_messages": logs,
        }

    def generate_captions(state: dict) -> dict:
        """为 PDF 提取的图片生成中文描述。
        优先 MiniMax Vision API，降级用页面上下文文字。"""
        image_records = state.get("image_records", [])
        if not image_records:
            return {"captions": [], "current_node": "generate_captions",
                    "log_messages": ["[generate_captions] 无图片，跳过"]}

        logs = [f"[generate_captions] 为 {len(image_records)} 张图片生成描述…"]
        captions = []

        for rec in image_records:
            image_path = rec["image_path"]
            basename = os.path.basename(image_path)
            caption = ""

            # 优先 MiniMax Vision
            if app_state.minimax_client and app_state.minimax_model:
                try:
                    from backend.image_captioner import describe_image
                    caption = describe_image(
                        app_state.minimax_client, app_state.minimax_model,
                        image_path, rec.get("context_text", "")
                    )
                except Exception:
                    pass

            # 降级：用页面上下文文字
            if not caption:
                fallback = rec.get("context_text", "").strip()
                if fallback:
                    caption = fallback
                    logs.append(f"  {basename}: 使用页面文字做降级 Caption")
                else:
                    logs.append(f"  {basename}: 无 Caption 也无页面文字，跳过")
                    continue

            captions.append({"image_path": image_path, "caption": caption})

        logs.append(f"[generate_captions] 完成，{len(captions)} 张图片有描述")
        return {
            "captions": captions,
            "current_node": "generate_captions",
            "log_messages": logs,
        }

    # ------------------------------------------------------------------
    # 阶段二：文本处理（MD 入口）
    # ------------------------------------------------------------------

    def chunk_text(state: dict) -> dict:
        """从 Markdown/TXT 切分文本块。
        如果 markdown_text 有内容（PDF 转换结果）则用它，否则直接读文件。"""
        from main_ingest import _split_text

        file_path = state["file_path"]
        source = os.path.basename(file_path)
        logs = []

        # 确定文本来源
        md_text = state.get("markdown_text", "")
        if md_text:
            logs.append(f"[chunk_text] 使用 PDF 转换的 Markdown（{len(md_text)} 字符）")
        else:
            # 直接从 MD/TXT 文件读取
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    md_text = f.read()
                logs.append(f"[chunk_text] 从文件读取（{len(md_text)} 字符）")
            except Exception as e:
                return {"error": f"读取文件失败: {e}", "log_messages": logs}

        chunks = _split_text(md_text)
        text_chunks = [
            {"text": c, "page": 1, "source": source}
            for c in chunks if c.strip()
        ]
        logs.append(f"[chunk_text] 切分为 {len(text_chunks)} 个文本块")

        return {
            "text_chunks": text_chunks,
            "current_node": "chunk_text",
            "log_messages": logs,
        }

    def encode_text_vectors(state: dict) -> dict:
        """bge-m3 编码文本块 -> PointStruct 列表。

        数据来源（互斥，优先 manual_chunks）：
          - manual_chunks: deepdoc 精细化路径产出的结构化文本块
          - text_chunks:   MD/TXT 简单路径产出的文本块
        """
        from qdrant_client.models import PointStruct

        # 优先使用 deepdoc 精细化路径的 manual_chunks
        manual_chunks = state.get("manual_chunks", [])
        text_chunks = state.get("text_chunks", [])
        chunks = manual_chunks if manual_chunks else text_chunks

        if not chunks:
            return {"points": [], "current_node": "encode_text_vectors",
                    "log_messages": ["[encode_text] 无文本块"]}

        file_path = state["file_path"]
        doc_id = _make_doc_id(file_path)
        source = os.path.basename(file_path)
        is_manual = bool(manual_chunks)
        logs = [f"[encode_text] 编码 {len(chunks)} 个文本块"
                f"（{'deepdoc精细化' if is_manual else '简单路径'}）…"]

        texts = [c["text"] for c in chunks]
        text_vecs = app_state.embedding_mgr.encode_text(texts)
        zero_img = app_state.embedding_mgr.zero_image_vec()

        points = []
        for i, (chunk, vec) in enumerate(zip(chunks, text_vecs)):
            chunk_id = f"{doc_id}_{i}"
            point_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk_id))
            payload = {
                "text": chunk["text"],
                "source": source,
                "page": chunk.get("page", 1),
                "chunk_type": chunk.get("chunk_type", "text"),
                "image_path": "",
                "doc_id": doc_id,
                "chunk_index": i,
            }
            # 注入 deepdoc 增强元数据
            if is_manual:
                payload.update({
                    "ata_section": chunk.get("ata_section", ""),
                    "section_title": chunk.get("section_title", ""),
                    "section_hierarchy": chunk.get("section_hierarchy", 0),
                    "figure_refs": chunk.get("figure_refs", []),
                    "table_refs": chunk.get("table_refs", []),
                    "has_warning": chunk.get("has_warning", False),
                    "has_caution": chunk.get("has_caution", False),
                    "doc_type": "maintenance_manual",
                })
            points.append(PointStruct(
                id=point_uuid,
                vector={"text_vec": vec.tolist(), "image_vec": zero_img},
                payload=payload,
            ))

        logs.append(f"[encode_text] 完成，{len(points)} 个文本向量")
        return {
            "points": [_serialize_point(p) for p in points],
            "current_node": "encode_text_vectors",
            "log_messages": logs,
        }

    def encode_image_vectors(state: dict) -> dict:
        """bge-m3(Caption) + CLIP(图片) 双向量编码图片块。

        数据来源（互斥，优先 figure_records）：
          - figure_records: deepdoc 精细化路径产出的图形记录（含 caption_text）
          - captions:       旧版 PDF 路径产出的图片描述
        """
        from PIL import Image as PILImage
        from qdrant_client.models import PointStruct

        figure_records = state.get("figure_records", [])
        captions = state.get("captions", [])

        if not figure_records and not captions:
            return {"current_node": "encode_image_vectors",
                    "log_messages": ["[encode_img] 无图片描述"]}

        file_path = state["file_path"]
        doc_id = _make_doc_id(file_path)
        source = os.path.basename(file_path)
        existing_points = state.get("points", [])
        offset = len(existing_points)

        is_manual = bool(figure_records)
        if is_manual:
            items = [{"image_path": r["image_path"],
                      "caption": r.get("caption_text", ""),
                      "page": r.get("page", 0),
                      "ata_section": r.get("ata_section", ""),
                      "figure_id": r.get("figure_id", ""),
                      "referencing_chunks": r.get("referencing_chunks", [])}
                     for r in figure_records if r.get("image_path") and r.get("caption_text")]
        else:
            items = [{"image_path": c["image_path"],
                      "caption": c["caption"],
                      "page": 0, "ata_section": "", "figure_id": "", "referencing_chunks": []}
                     for c in captions]

        logs = [f"[encode_img] 编码 {len(items)} 张图片"
                f"（{'deepdoc精细化' if is_manual else '简单路径'}）…"]

        new_points = []
        for j, item in enumerate(items):
            image_path = item["image_path"]
            caption_text = item["caption"]
            i = offset + j

            text_vec = app_state.embedding_mgr.encode_text([caption_text])[0].tolist()

            try:
                pil_img = PILImage.open(image_path).convert("RGB")
                image_vec = app_state.embedding_mgr.encode_images_clip([pil_img])[0].tolist()
            except Exception as e:
                logs.append(f"  CLIP 编码失败（{e}），跳过: {os.path.basename(image_path)}")
                continue

            chunk_id = f"{doc_id}_{i}"
            point_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk_id))
            payload = {
                "text": caption_text,
                "source": source,
                "page": item["page"],
                "chunk_type": "image",
                "image_path": image_path,
                "doc_id": doc_id,
                "chunk_index": i,
            }
            if is_manual:
                payload.update({
                    "ata_section": item["ata_section"],
                    "figure_id": item["figure_id"],
                    "referencing_chunks": item["referencing_chunks"],
                    "doc_type": "maintenance_manual",
                })
            new_points.append(PointStruct(
                id=point_uuid,
                vector={"text_vec": text_vec, "image_vec": image_vec},
                payload=payload,
            ))

        logs.append(f"[encode_img] 完成，{len(new_points)} 个图片向量")
        return {
            "points": existing_points + [_serialize_point(p) for p in new_points],
            "current_node": "encode_image_vectors",
            "log_messages": logs,
        }

    def upsert_qdrant(state: dict) -> dict:
        """批量写入 Qdrant（文本块 + 图片块）。"""
        from qdrant_client.models import (
            PointStruct, FilterSelector, Filter, FieldCondition, MatchValue,
        )
        from backend.state import COLLECTION_NAME

        serialized_points = state.get("points", [])
        if not serialized_points:
            return {"stats": {"upserted": 0}, "current_node": "upsert_qdrant",
                    "log_messages": ["[upsert] 无数据可写入"]}

        file_path = state["file_path"]
        doc_id = _make_doc_id(file_path)
        clear_first = state.get("clear_first", False)
        logs = []

        # 清空（如果需要）
        if clear_first:
            try:
                app_state.qdrant_client.delete_collection(COLLECTION_NAME)
                from backend.main import _init_qdrant, QDRANT_DB_PATH
                app_state.qdrant_client = _init_qdrant(QDRANT_DB_PATH, COLLECTION_NAME)
                logs.append("[upsert] 已清空旧数据")
            except Exception as e:
                logs.append(f"[upsert] 清空失败: {e}")

        # 增量更新：先删旧块
        try:
            app_state.qdrant_client.delete(
                collection_name=COLLECTION_NAME,
                points_selector=FilterSelector(
                    filter=Filter(
                        must=[FieldCondition(key="doc_id", match=MatchValue(value=doc_id))]
                    )
                ),
            )
        except Exception:
            pass

        # 反序列化 PointStruct
        points = [_deserialize_point(p) for p in serialized_points]

        # 分批写入
        batch_size = 32
        total = len(points)
        logs.append(f"[upsert] 写入 {total} 个块（批大小 {batch_size}）…")
        for start in range(0, total, batch_size):
            batch = points[start:start + batch_size]
            app_state.qdrant_client.upsert(collection_name=COLLECTION_NAME, points=batch)
            end = min(start + batch_size, total)
            logs.append(f"  [{end}/{total}] 已写入…")

        count = app_state.get_doc_count()
        logs.append(f"[upsert] 完成！本次入库 {total} 块，知识库共 {count} 条")

        return {
            "stats": {"upserted": total, "total": count},
            "current_node": "upsert_qdrant",
            "log_messages": logs,
        }

    # ------------------------------------------------------------------
    # 辅助：PointStruct 序列化/反序列化（LangGraph state 需要可序列化）
    # ------------------------------------------------------------------

    def _serialize_point(p) -> dict:
        return {"id": p.id, "vector": p.vector, "payload": p.payload}

    def _deserialize_point(d: dict):
        from qdrant_client.models import PointStruct
        return PointStruct(id=d["id"], vector=d["vector"], payload=d["payload"])

    # ------------------------------------------------------------------
    # 返回节点字典
    # ------------------------------------------------------------------
    return {
        "pdf_to_md": pdf_to_md,
        "generate_captions": generate_captions,
        "chunk_text": chunk_text,
        "encode_text_vectors": encode_text_vectors,
        "encode_image_vectors": encode_image_vectors,
        "upsert_qdrant": upsert_qdrant,
    }
