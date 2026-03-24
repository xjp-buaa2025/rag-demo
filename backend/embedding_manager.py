"""
embedding_manager.py
统一管理双 Embedding 模型：
  - bge-m3：纯文本编码（1024维），用于文本块检索
  - Chinese-CLIP：图文跨模态编码（768维，projection_dim），用于图片块检索和以图搜文

两个模型维度不同：bge-m3=1024，Chinese-CLIP=768（由模型 config 自动检测）。
Qdrant Collection 使用命名多向量，text_vec=1024，image_vec=768。
"""

import numpy as np
from typing import List
from PIL import Image
from sentence_transformers import SentenceTransformer
from transformers import ChineseCLIPProcessor, ChineseCLIPModel
import torch


TEXT_MODEL_NAME = "BAAI/bge-m3"
CLIP_MODEL_NAME = "OFA-Sys/chinese-clip-vit-large-patch14"

TEXT_DIM = 1024  # bge-m3 输出维度（固定）
# Chinese-CLIP 的 projection_dim 由 __init__ 从模型配置自动检测（vit-large = 768）


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

        # 从模型配置自动获取 CLIP 投影维度（chinese-clip-vit-large = 768）
        self.clip_dim = self.clip_model.config.projection_dim

    # ------------------------------------------------------------------
    # 文本编码（bge-m3）
    # ------------------------------------------------------------------

    def encode_text(self, texts: List[str]) -> np.ndarray:
        """
        用 bge-m3 编码文本列表，返回 shape (N, 1024) 的 float32 数组。
        用于：文本块入库 / 文字查询搜 text_vec
        """
        if not texts:
            return np.zeros((0, TEXT_DIM), dtype=np.float32)
        vecs = self.text_model.encode(texts, normalize_embeddings=True,
                                      show_progress_bar=False)
        return np.array(vecs, dtype=np.float32)

    # ------------------------------------------------------------------
    # 图文编码（Chinese-CLIP）
    # ------------------------------------------------------------------

    def encode_texts_clip(self, texts: List[str]) -> np.ndarray:
        """
        用 Chinese-CLIP 文本编码器编码文本，返回 shape (N, clip_dim) 的 float32 数组。
        用于：文字查询搜 image_vec（文字查图路径）
        """
        if not texts:
            return np.zeros((0, self.clip_dim), dtype=np.float32)
        raw = self.clip_processor(text=texts, return_tensors="pt",
                                  padding=True, truncation=True, max_length=52)
        inputs = {k: v.to(self.device) for k, v in raw.items() if v is not None}
        with torch.no_grad():
            # 绕过 get_text_features()：transformers 4.57+ 的 ChineseCLIPModel
            # 用 add_pooling_layer=False 初始化文本模型，导致 pooler_output=None，
            # 但 get_text_features 仍试图对其做线性投影 → 崩溃。
            # 手动调用 text_model + text_projection，pooler 缺失时回退到 [CLS] token。
            text_outputs = self.clip_model.text_model(**inputs)
            pooled = text_outputs.pooler_output
            if pooled is None:
                pooled = text_outputs.last_hidden_state[:, 0, :]
            features = self.clip_model.text_projection(pooled)
            features = features / features.norm(dim=-1, keepdim=True)
        return features.cpu().numpy().astype(np.float32)

    def encode_images_clip(self, images: List[Image.Image]) -> np.ndarray:
        """
        用 Chinese-CLIP 图片编码器编码 PIL Image 列表，返回 shape (N, clip_dim) 的 float32 数组。
        用于：图片块入库 / 用户上传图片搜 image_vec（以图搜文路径）
        """
        if not images:
            return np.zeros((0, self.clip_dim), dtype=np.float32)
        raw = self.clip_processor(images=images, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in raw.items() if v is not None}
        with torch.no_grad():
            features = self.clip_model.get_image_features(**inputs)
            features = features / features.norm(dim=-1, keepdim=True)
        return features.cpu().numpy().astype(np.float32)

    def zero_image_vec(self) -> List[float]:
        """返回 clip_dim 维零向量（文本块的 image_vec 占位符）"""
        return [0.0] * self.clip_dim
