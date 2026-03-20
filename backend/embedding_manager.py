"""
embedding_manager.py
统一管理双 Embedding 模型：
  - bge-m3：纯文本编码（1024维），用于文本块检索
  - Chinese-CLIP：图文跨模态编码（1024维），用于图片块检索和以图搜文

两个模型的向量维度均为 1024，可复用同一 Qdrant Collection 索引参数。
"""

import numpy as np
from typing import List
from PIL import Image
from sentence_transformers import SentenceTransformer
from transformers import ChineseCLIPProcessor, ChineseCLIPModel
import torch


TEXT_MODEL_NAME = "BAAI/bge-m3"
CLIP_MODEL_NAME = "OFA-Sys/chinese-clip-vit-large-patch14"

VECTOR_DIM = 1024  # bge-m3 和 chinese-clip-vit-large 均为 1024 维


class EmbeddingManager:
    """
    管理 bge-m3（文本）+ Chinese-CLIP（图文）两个 Embedding 模型。
    提供统一的编码接口，供 ingest / retrieve 层调用。
    """

    def __init__(self, text_model_name: str = TEXT_MODEL_NAME,
                 clip_model_name: str = CLIP_MODEL_NAME):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # bge-m3：文本块的向量编码
        self.text_model = SentenceTransformer(text_model_name, device=self.device)

        # Chinese-CLIP：图片块（图片编码）+ 文字查图（文本编码）
        self.clip_model = ChineseCLIPModel.from_pretrained(clip_model_name).to(self.device)
        self.clip_processor = ChineseCLIPProcessor.from_pretrained(clip_model_name)
        self.clip_model.eval()

    # ------------------------------------------------------------------
    # 文本编码（bge-m3）
    # ------------------------------------------------------------------

    def encode_text(self, texts: List[str]) -> np.ndarray:
        """
        用 bge-m3 编码文本列表，返回 shape (N, 1024) 的 float32 数组。
        用于：文本块入库 / 文字查询搜 text_vec
        """
        if not texts:
            return np.zeros((0, VECTOR_DIM), dtype=np.float32)
        vecs = self.text_model.encode(texts, normalize_embeddings=True,
                                      show_progress_bar=False)
        return np.array(vecs, dtype=np.float32)

    # ------------------------------------------------------------------
    # 图文编码（Chinese-CLIP）
    # ------------------------------------------------------------------

    def encode_texts_clip(self, texts: List[str]) -> np.ndarray:
        """
        用 Chinese-CLIP 文本编码器编码文本，返回 shape (N, 1024) 的 float32 数组。
        用于：文字查询搜 image_vec（文字查图路径）
        """
        if not texts:
            return np.zeros((0, VECTOR_DIM), dtype=np.float32)
        inputs = self.clip_processor(text=texts, return_tensors="pt",
                                     padding=True, truncation=True, max_length=52).to(self.device)
        with torch.no_grad():
            features = self.clip_model.get_text_features(**inputs)
            features = features / features.norm(dim=-1, keepdim=True)  # L2 归一化
        return features.cpu().numpy().astype(np.float32)

    def encode_images_clip(self, images: List[Image.Image]) -> np.ndarray:
        """
        用 Chinese-CLIP 图片编码器编码 PIL Image 列表，返回 shape (N, 1024) 的 float32 数组。
        用于：图片块入库 / 用户上传图片搜 image_vec（以图搜文路径）
        """
        if not images:
            return np.zeros((0, VECTOR_DIM), dtype=np.float32)
        inputs = self.clip_processor(images=images, return_tensors="pt").to(self.device)
        with torch.no_grad():
            features = self.clip_model.get_image_features(**inputs)
            features = features / features.norm(dim=-1, keepdim=True)
        return features.cpu().numpy().astype(np.float32)

    def zero_image_vec(self) -> List[float]:
        """返回 1024 维零向量（文本块的 image_vec 占位符）"""
        return [0.0] * VECTOR_DIM
