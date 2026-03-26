"""
document_processing/rag/utils/lazy_image.py — deepdoc rag.utils.lazy_image shim

deepdoc operators.py 通过以下方式使用：
  from rag.utils.lazy_image import ensure_pil_image
"""

import io
import numpy as np


def ensure_pil_image(img_data):
    """
    将 bytes / numpy.ndarray / PIL.Image 统一转换为 PIL.Image。

    deepdoc 内部图像数据可能以多种形式传递，此函数做归一化处理。
    """
    from PIL import Image as PILImage

    if isinstance(img_data, PILImage.Image):
        return img_data
    if isinstance(img_data, bytes):
        return PILImage.open(io.BytesIO(img_data)).convert("RGB")
    if isinstance(img_data, np.ndarray):
        # numpy 数组直接返回，调用方通过 isinstance(pil, Image.Image) 判断
        # 不强制转 PIL，避免 float32→uint8 数据损失（会破坏 NormalizeImage 后的精度）
        return img_data
    raise TypeError(f"无法将 {type(img_data)} 转换为 PIL.Image")


def open_image_for_processing(path: str):
    """打开图片文件并返回 PIL.Image（RGB模式）。"""
    from PIL import Image as PILImage
    return PILImage.open(path).convert("RGB")


def is_image_like(obj) -> bool:
    """判断对象是否为图像类型（PIL.Image / bytes / numpy.ndarray）。"""
    from PIL import Image as PILImage
    return isinstance(obj, (PILImage.Image, bytes, np.ndarray))
