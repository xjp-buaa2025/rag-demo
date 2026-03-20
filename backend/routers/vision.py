"""
backend/routers/vision.py — 图片描述接口

POST /vision/describe
  接收用户上传的图片（multipart/form-data），调用 MiniMax M2.5 Vision 生成中文描述。
  前端用返回的描述文字进行后续向量检索（以图搜文流程）。

POST /vision/search_by_image
  接收用户上传的图片，用 Chinese-CLIP 编码后直接搜索 image_vec，返回最相关的图片块。
  这是真正的以图搜图路径，不依赖 Vision LLM。
"""

import os
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from backend.deps import get_state
from backend.state import AppState, COLLECTION_NAME

router = APIRouter()

IMAGE_SERVE_PREFIX = "/images"


class VisionDescribeResponse(BaseModel):
    description: str      # Vision LLM 生成的中文描述
    query_text: str       # 推荐用于后续检索的文本（当前等同于 description）


class ImageSearchResult(BaseModel):
    text: str             # Caption 文字（描述）
    source: str
    page: int
    distance: float
    image_url: Optional[str] = None


class ImageSearchResponse(BaseModel):
    results: List[ImageSearchResult]


@router.post("/vision/describe", response_model=VisionDescribeResponse,
             summary="上传图片，获取中文描述（用于以图搜文）")
async def describe_image_upload(
    file: UploadFile = File(...),
    state: AppState = Depends(get_state),
):
    """
    接收前端上传的图片（multipart/form-data）。
    调用 MiniMax M2.5 Vision API 生成中文描述，供前端用于后续 /chat 或 /retrieve 调用。

    前端流程：
      1. 用户上传图片 → POST /vision/describe → 得到 description
      2. 前端拼入用户输入：f"[图片内容：{description}] {用户的问题}"
      3. 正常走 POST /chat 流程
    """
    if state.minimax_client is None:
        raise HTTPException(
            status_code=503,
            detail="Vision 功能未启用，请配置 MINIMAX_API_KEY 环境变量。"
        )

    # 读取图片内容
    content = await file.read()
    if len(content) > 20 * 1024 * 1024:  # 20MB 限制
        raise HTTPException(status_code=413, detail="图片大小不能超过 20MB")

    # 保存到临时位置供 describe_image 使用（base64 编码）
    import base64, tempfile
    from pathlib import Path

    suffix = Path(file.filename or "upload.png").suffix or ".png"
    try:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        from backend.image_captioner import describe_image
        description = describe_image(
            state.minimax_client, state.minimax_model, tmp_path
        )
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass

    if not description:
        raise HTTPException(status_code=500, detail="图片描述生成失败，请检查图片格式或稍后重试。")

    return VisionDescribeResponse(description=description, query_text=description)


@router.post("/vision/search", response_model=ImageSearchResponse,
             summary="上传图片，用 CLIP 直接以图搜图")
async def search_by_image(
    file: UploadFile = File(...),
    top_k: int = 4,
    state: AppState = Depends(get_state),
):
    """
    接收用户上传的图片，用 Chinese-CLIP 编码图片向量，直接搜索 Qdrant image_vec。
    无需 Vision LLM，纯向量匹配，速度快。
    返回最相关的图片块（及其 Caption 和 image_url）。
    """
    from PIL import Image as PILImage
    import io

    content = await file.read()
    if len(content) > 20 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="图片大小不能超过 20MB")

    # 编码上传图片的 CLIP 向量
    try:
        pil_img  = PILImage.open(io.BytesIO(content)).convert("RGB")
        image_vec = state.embedding_mgr.encode_images_clip([pil_img])[0].tolist()
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"图片解码失败：{e}")

    # 搜索 image_vec（仅图片块）
    total = state.get_doc_count()
    if total == 0:
        return ImageSearchResponse(results=[])

    limit = min(top_k, total)
    try:
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        results = state.qdrant_client.query_points(
            collection_name=COLLECTION_NAME,
            query=image_vec,
            using="image_vec",
            limit=limit,
            with_payload=True,
            query_filter=Filter(
                must=[FieldCondition(key="chunk_type", match=MatchValue(value="image"))]
            ),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"向量搜索失败：{e}")

    out = []
    for point in results.points:
        payload  = point.payload or {}
        img_path = payload.get("image_path", "")
        img_url  = f"{IMAGE_SERVE_PREFIX}/{os.path.basename(img_path)}" if img_path else None
        out.append(ImageSearchResult(
            text=payload.get("text", ""),
            source=payload.get("source", ""),
            page=payload.get("page", 0),
            distance=point.score,
            image_url=img_url,
        ))

    return ImageSearchResponse(results=out)
