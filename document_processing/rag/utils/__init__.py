"""
document_processing/rag/utils/__init__.py — deepdoc rag.utils shim
"""
from .lazy_image import ensure_pil_image, open_image_for_processing, is_image_like

__all__ = ["ensure_pil_image", "open_image_for_processing", "is_image_like"]
