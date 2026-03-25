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
        # OpenCV BGR → RGB
        if img_data.ndim == 3 and img_data.shape[2] == 3:
            img_data = img_data[:, :, ::-1]
        return PILImage.fromarray(img_data.astype(np.uint8))
    raise TypeError(f"无法将 {type(img_data)} 转换为 PIL.Image")


def open_image_for_processing(path: str):
    """打开图片文件并返回 PIL.Image（RGB模式）。"""
    from PIL import Image as PILImage
    return PILImage.open(path).convert("RGB")


def is_image_like(obj) -> bool:
    """判断对象是否为图像类型（PIL.Image / bytes / numpy.ndarray）。"""
    from PIL import Image as PILImage
    return isinstance(obj, (PILImage.Image, bytes, np.ndarray))
