"""
main_ingest.py — 文档解析、向量化、写入 Qdrant 知识库（图文版）

职责：
  1. 扫描 data/ 目录，读取所有支持的文档（.txt .md .pdf）
  2. 文本块：deepdoc 解析 → bge-m3 向量 → 写入 Qdrant text_vec 字段
  3. 图片块：PyMuPDF 提取图片 → MiniMax Vision 生成 Caption → bge-m3（Caption）+ Chinese-CLIP（图片）双向量 → 写入 Qdrant

运行方式：
  PYTHONUTF8=1 python main_ingest.py           # 增量入库
  PYTHONUTF8=1 python main_ingest.py --clear   # 清空后重建

向量库：Qdrant（storage/qdrant.db，本地文件模式，无需 Docker）
图片存储：storage/images/

详见 PROJECT_GUIDE.md § 图文检索
"""

import os
import re
import sys
import uuid
import hashlib
import argparse
from typing import List, Dict, Any, Optional

# 将 document_processing/ 加入 Python 搜索路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'document_processing'))

# PyMuPDF
import fitz  # PyMuPDF

# deepdoc 文本解析器
try:
    from deepdoc.parser.txt_parser import RAGFlowTxtParser
except ImportError as e:
    print(f"警告：导入 TxtParser 失败: {e}")
    RAGFlowTxtParser = None


# ==========================================
# 配置常量
# ==========================================
DATA_DIR        = os.path.join(os.path.dirname(__file__), 'data')
QDRANT_DB_PATH  = os.path.join(os.path.dirname(__file__), 'storage', 'qdrant.db')
IMAGE_DIR       = os.path.join(os.path.dirname(__file__), 'storage', 'images')
COLLECTION_NAME = "rag_knowledge"
EMBEDDING_MODEL = "BAAI/bge-m3"
CLIP_MODEL      = "OFA-Sys/chinese-clip-vit-large-patch14"


# ==========================================
# 文本切片
# ==========================================

def _split_text(text: str, chunk_size: int = 500) -> List[str]:
    """
    按中文句子边界切分文本，每块不超过 chunk_size 字。
    500字≈2-5段正文，是语义完整性与检索精度的平衡点。
    """
    sentences = re.split(r'(?<=[。！？\n])', text)
    chunks, current = [], ""
    for sent in sentences:
        if len(current) + len(sent) > chunk_size and current:
            chunks.append(current.strip())
            current = sent
        else:
            current += sent
    if current.strip():
        chunks.append(current.strip())
    return [c for c in chunks if c]


# ==========================================
# 图片提取
# ==========================================

def extract_images_from_pdf(file_path: str, output_dir: str,
                             min_width: int = 100, min_height: int = 100) -> List[Dict]:
    """
    用 PyMuPDF 从 PDF 中提取图片，保存到 output_dir。

    过滤策略：宽/高小于 min_width/min_height 的图片（图标、装饰线条等噪声）被丢弃，
    节省 Vision LLM 调用次数和费用。

    Args:
        file_path: PDF 文件绝对路径
        output_dir: 图片保存目录（storage/images/）
        min_width:  最小宽度（像素），低于此值跳过
        min_height: 最小高度（像素），低于此值跳过

    Returns:
        图片信息列表，每项格式：
        {
          "image_path": "/abs/.../storage/images/doc_p3_img0.png",
          "page": 3,
          "context_text": "",  # 图片所在页面的部分文字，用于提升 Caption 质量
        }
    """
    os.makedirs(output_dir, exist_ok=True)
    results = []
    basename = os.path.splitext(os.path.basename(file_path))[0]

    try:
        doc = fitz.open(file_path)
        for page_num, page in enumerate(doc, 1):
            image_list = page.get_images(full=True)
            if not image_list:
                continue

            # 取该页前 200 字作为上下文提示（提升 Caption 质量）
            page_text = (page.get_text("text") or "").strip()[:200]

            for img_idx, img_info in enumerate(image_list):
                xref = img_info[0]
                try:
                    img_data = doc.extract_image(xref)
                except Exception:
                    continue

                width  = img_data.get("width", 0)
                height = img_data.get("height", 0)

                # 过滤装饰图
                if width < min_width or height < min_height:
                    continue

                ext = img_data.get("ext", "png")
                img_bytes = img_data.get("image", b"")
                if not img_bytes:
                    continue

                filename = f"{basename}_p{page_num}_img{img_idx}.{ext}"
                img_path = os.path.join(output_dir, filename)

                with open(img_path, "wb") as f:
                    f.write(img_bytes)

                results.append({
                    "image_path":    img_path,
                    "page":          page_num,
                    "context_text":  page_text,
                })

        doc.close()

    except Exception as e:
        print(f"  图片提取出错 {file_path}: {e}")

    return results


# ==========================================
# 文档解析（文本块）
# ==========================================

def process_document(file_path: str, image_dir: Optional[str] = None,
                     images_only: bool = False) -> List[Dict]:
    """
    解析单个文件，返回块列表。

    块格式：
      文本块：{"text": str, "page": int, "chunk_type": "text", "image_path": ""}
      图片块：{"text": "",  "page": int, "chunk_type": "image", "image_path": str,
               "context_text": str}  # text 由调用方在生成 Caption 后填充

    Args:
        images_only: 为 True 时仅从 PDF 提取图片，跳过文本。用于有 .md 的 PDF。
    """
    ext = file_path.lower().split('.')[-1]
    results: List[Dict] = []

    try:
        if ext in ('txt', 'md') and not images_only:
            print(f"  使用 RAGFlowTxtParser 解析")
            if RAGFlowTxtParser:
                parser = RAGFlowTxtParser()
                with open(file_path, 'rb') as f:
                    content = f.read()
                raw_chunks = parser(file_path, binary=content, chunk_token_num=256)
                for chunk in raw_chunks:
                    text = chunk[0] if isinstance(chunk, (list, tuple)) else str(chunk)
                    if text.strip():
                        results.append({"text": text.strip(), "page": 1,
                                        "chunk_type": "text", "image_path": ""})
            else:
                # fallback：直接按行切分
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    raw = f.read()
                for chunk in _split_text(raw):
                    results.append({"text": chunk, "page": 1,
                                    "chunk_type": "text", "image_path": ""})

        elif ext == 'pdf':
            if not images_only:
                print(f"  使用 PyMuPDF 解析文本页")
                with fitz.open(file_path) as pdf:
                    total_pages = len(pdf)
                    pages_with_text = 0
                    for page_num, page in enumerate(pdf, 1):
                        page_text = (page.get_text("text") or "").strip()
                        if page_text:
                            pages_with_text += 1
                            for chunk in _split_text(page_text):
                                results.append({"text": chunk, "page": page_num,
                                                "chunk_type": "text", "image_path": ""})
                    print(f"  共 {total_pages} 页，{pages_with_text} 页有文本")

            # 提取图片块（text 待 ingest 层填充）
            if image_dir:
                print(f"  提取 PDF 图片…")
                img_records = extract_images_from_pdf(file_path, image_dir)
                for rec in img_records:
                    results.append({
                        "text":         "",          # Caption 由 ingest 层填充
                        "page":         rec["page"],
                        "chunk_type":   "image",
                        "image_path":   rec["image_path"],
                        "context_text": rec.get("context_text", ""),
                    })
                print(f"  提取到 {len(img_records)} 张图片")
        else:
            print(f"  不支持 {ext} 格式，跳过")

    except Exception as e:
        print(f"  解析出错: {e}")

    text_count  = sum(1 for c in results if c["chunk_type"] == "text")
    image_count = sum(1 for c in results if c["chunk_type"] == "image")
    print(f"  切分完成：文本块 {text_count} 个，图片块 {image_count} 个")
    return results


# ==========================================
# 主入库函数（供命令行和后端 ingest 路由复用）
# ==========================================

def _make_doc_id(file_path: str) -> str:
    """用文件名（不含路径）的 sha256 前 16 位作为 doc_id，用于增量更新定位。"""
    fname = os.path.basename(file_path)
    return hashlib.sha256(fname.encode()).hexdigest()[:16]


def ingest_to_qdrant(qdrant_client, embedding_mgr, file_path: str,
                     image_dir: str, minimax_client=None, minimax_model: str = "",
                     batch_size: int = 32, images_only: bool = False) -> int:
    """
    解析单个文件并写入 Qdrant。
    文本块：text_vec（bge-m3），image_vec（零向量）
    图片块：先生成 Caption（调 Vision LLM），再编码 text_vec（Caption）+ image_vec（CLIP）
    无 MiniMax 时，用页面上下文文字做降级 Caption（仍可用 CLIP 向量检索图片）。

    Args:
        images_only: 仅提取图片块（跳过文本），用于有 .md 的 PDF。

    Returns:
        成功写入的块数（含文本块和图片块）
    """
    from PIL import Image as PILImage
    from qdrant_client.models import PointStruct, FilterSelector, Filter, FieldCondition, MatchValue

    fname    = os.path.basename(file_path)
    doc_id   = _make_doc_id(file_path)
    chunks   = process_document(file_path, image_dir=image_dir, images_only=images_only)

    if not chunks:
        return 0

    # 增量更新：先删除该文档的旧块
    try:
        qdrant_client.delete(
            collection_name=COLLECTION_NAME,
            points_selector=FilterSelector(
                filter=Filter(
                    must=[FieldCondition(key="doc_id", match=MatchValue(value=doc_id))]
                )
            ),
        )
    except Exception:
        pass  # 首次入库时无旧数据，忽略

    points = []
    for i, chunk in enumerate(chunks):
        chunk_id  = f"{doc_id}_{i}"
        point_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk_id))

        if chunk["chunk_type"] == "text":
            text_vec  = embedding_mgr.encode_text([chunk["text"]])[0].tolist()
            image_vec = embedding_mgr.zero_image_vec()
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
            if minimax_client and minimax_model:
                from backend.image_captioner import describe_image
                print(f"    生成 Caption: {os.path.basename(image_path)}")
                caption = describe_image(minimax_client, minimax_model,
                                         image_path, chunk.get("context_text", ""))
            if not caption:
                # 降级：用 PDF 页面上下文文字做 Caption（仍可用 CLIP 向量检索）
                fallback = chunk.get("context_text", "").strip()
                if fallback:
                    caption = fallback
                    print(f"    📝  使用页面文字做降级 Caption: {os.path.basename(image_path)}")
                else:
                    print(f"    ⚠️  无 Caption 也无页面文字，跳过: {os.path.basename(image_path)}")
                    continue

            # 编码 Caption 文本向量（bge-m3）
            text_vec = embedding_mgr.encode_text([caption])[0].tolist()

            # 编码图片向量（Chinese-CLIP）
            try:
                pil_img   = PILImage.open(image_path).convert("RGB")
                image_vec = embedding_mgr.encode_images_clip([pil_img])[0].tolist()
            except Exception as e:
                print(f"    ⚠️  CLIP 编码失败（{e}），跳过: {os.path.basename(image_path)}")
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
    total_inserted = 0
    for start in range(0, len(points), batch_size):
        batch = points[start: start + batch_size]
        qdrant_client.upsert(collection_name=COLLECTION_NAME, points=batch)
        total_inserted += len(batch)

    return total_inserted


# ==========================================
# 命令行入口
# ==========================================

def main():
    parser = argparse.ArgumentParser(description="图文 RAG 知识库入库工具")
    parser.add_argument("--clear", action="store_true",
                        help="清空已有向量数据库后重新入库")
    parser.add_argument("--no-image", action="store_true",
                        help="跳过图片提取（无 MiniMax Vision 配置时使用）")
    args = parser.parse_args()

    from dotenv import load_dotenv
    load_dotenv()

    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(IMAGE_DIR, exist_ok=True)

    # 先初始化 EmbeddingManager（需要从模型获取 clip_dim 再创建 Qdrant Collection）
    print(f"加载 Embedding 模型：{EMBEDDING_MODEL} + {CLIP_MODEL}")
    from backend.embedding_manager import EmbeddingManager
    embedding_mgr = EmbeddingManager(EMBEDDING_MODEL, CLIP_MODEL)

    # 初始化 Qdrant（image_vec 维度从 EmbeddingManager 自动获取）
    from backend.main import _init_qdrant
    qdrant_client = _init_qdrant(QDRANT_DB_PATH, COLLECTION_NAME, embedding_mgr.clip_dim)

    if args.clear:
        try:
            qdrant_client.delete_collection(COLLECTION_NAME)
            print(f"已清空: {COLLECTION_NAME}")
        except Exception:
            pass
        # 在同一个 client 上重建 collection（避免创建新 QdrantClient 导致文件锁冲突）
        from qdrant_client.models import VectorParams, Distance
        qdrant_client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config={
                "text_vec":  VectorParams(size=1024, distance=Distance.COSINE),
                "image_vec": VectorParams(size=embedding_mgr.clip_dim, distance=Distance.COSINE),
            },
        )
        print(f"已重建 Collection: {COLLECTION_NAME}（text_vec=1024, image_vec={embedding_mgr.clip_dim}）")

    # 初始化 MiniMax Vision 客户端（可选）
    minimax_client = None
    minimax_model  = ""
    if not args.no_image:
        _mm_key  = os.getenv("MINIMAX_API_KEY", "").strip()
        _mm_url  = os.getenv("MINIMAX_BASE_URL", "https://api.minimaxi.com/v1")
        _mm_mdl  = os.getenv("MINIMAX_MODEL", "MiniMax-M2.5")
        if _mm_key:
            from openai import OpenAI
            minimax_client = OpenAI(api_key=_mm_key, base_url=_mm_url)
            minimax_model  = _mm_mdl
            print(f"Vision API 已配置：{_mm_mdl}")
        else:
            print("⚠️  未配置 MINIMAX_API_KEY，图片 Caption 生成不可用，仅入库文本块。")

    # 扫描 data/ 目录
    all_files = [
        os.path.join(DATA_DIR, f) for f in os.listdir(DATA_DIR)
        if os.path.isfile(os.path.join(DATA_DIR, f))
    ]

    # 构建处理计划：.md 优先文本，对应 .pdf 仅提取图片
    plan = []  # [(file_path, images_only), ...]
    md_stems = set()
    for f in all_files:
        if f.lower().endswith('.md'):
            md_stems.add(os.path.splitext(f)[0])
            plan.append((f, False))  # .md → 文本块
    for f in all_files:
        if f.lower().endswith('.pdf'):
            stem = os.path.splitext(f)[0]
            if stem in md_stems:
                if not args.no_image:
                    plan.append((f, True))  # 有 .md → 仅提取图片
            else:
                plan.append((f, False))  # 无 .md → 文本+图片
    # 其他格式文件
    for f in all_files:
        ext = f.lower().split('.')[-1]
        if ext not in ('md', 'pdf', 'rar', 'xlsx', 'py'):
            plan.append((f, False))

    if not plan:
        print(f"在 {DATA_DIR} 目录下没有找到任何文件。")
        return

    total = 0
    for file_path, img_only in plan:
        fname = os.path.basename(file_path)
        mode = "（仅图片）" if img_only else ""
        print(f"\n>>>> 处理: {fname} {mode}")
        _img_dir = None if args.no_image else IMAGE_DIR
        inserted = ingest_to_qdrant(
            qdrant_client, embedding_mgr, file_path, _img_dir,
            minimax_client, minimax_model, images_only=img_only
        )
        print(f"  {fname} 入库 {inserted} 块。")
        total += inserted

    count = qdrant_client.get_collection(COLLECTION_NAME).points_count or 0
    print(f"\n✅ 所有文件处理完毕。总入库: {total} 块。")
    print(f"Qdrant 知识库当前总块数: {count}")


if __name__ == "__main__":
    main()
