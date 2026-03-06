"""
main_ingest.py — 第二步：文档解析、向量化、写入 ChromaDB 知识库

职责：
  1. 扫描 data/ 目录，读取所有支持的文档（.txt .md .pdf）
  2. 用 deepdoc 解析文档，按语义边界切成文本块（chunk）
  3. 用 BAAI/bge-m3 模型将每个块转为向量（本地推理，不调外部 API）
  4. 将文本块 + 向量 upsert 到 ChromaDB

运行方式：
  PYTHONUTF8=1 python main_ingest.py           # 增量入库
  PYTHONUTF8=1 python main_ingest.py --clear   # 清空后重建（推荐首次或更换文档时使用）

重要约定：
  - 已有对应 .md 的 PDF 文件会被跳过（由 pdf_to_md.py 负责 PDF→MD，避免重复）
  - 用 upsert 而非 insert，同一文件重复运行安全，不会报主键冲突

详见 PROJECT_GUIDE.md § 6.2
"""

import os
import argparse
from typing import List, Dict, Any

# ChromaDB：轻量本地向量数据库
import chromadb
from chromadb.config import Settings

# SentenceTransformers：加载本地 Embedding 模型（BAAI/bge-m3）
from sentence_transformers import SentenceTransformer

# 将 document_processing/ 加入 Python 搜索路径，
# 这样 deepdoc 内部的 "from common.xxx import ..." 才能正确找到我们写的 shim 模块
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'document_processing'))

# deepdoc 的文本/Markdown 解析器（来自 RAGFlow）
try:
    from deepdoc.parser.txt_parser import RAGFlowTxtParser
except ImportError as e:
    print(f"警告：导入 TxtParser 失败: {e}")
    RAGFlowTxtParser = None

# PyMuPDF：作为 PDF 解析的 fallback（正式流程下 PDF 已由 pdf_to_md.py 转为 MD）
import fitz  # PyMuPDF


# ==========================================
# 配置常量
# ==========================================

# data/ 目录：原始文档放这里
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

# ChromaDB 数据文件目录（持久化到磁盘）
CHROMA_DB_DIR = os.path.join(os.path.dirname(__file__), 'storage', 'chroma_db')

# 知识库集合名称（类似数据库表名）
COLLECTION_NAME = "local_rag_knowledge"

# Embedding 模型：北京智源 bge-m3，支持中英文，本地运行
# 首次运行会从 HuggingFace 自动下载模型权重
EMBEDDING_MODEL_NAME = "BAAI/bge-m3"


class LocalEmbeddingFunction:
    """
    对 SentenceTransformer 的包装，使其符合 ChromaDB 的 EmbeddingFunction 接口协议。

    ChromaDB 要求 embedding_function 是一个 callable：
      - 输入：List[str]（字符串列表）
      - 输出：List[List[float]]（每个字符串对应一个向量）

    name() 方法是 ChromaDB 1.5+ 新增的要求，记录模型名称，防止不同模型混用。
    """
    def __init__(self, model_name: str):
        print(f"正在加载 Embedding 模型: {model_name} ...")
        self.model = SentenceTransformer(model_name)
        self._model_name = model_name

    def name(self) -> str:
        # ChromaDB 1.5+ 要求 EmbeddingFunction 实现 name() 方法
        return self._model_name

    def __call__(self, input: List[str]) -> List[List[float]]:
        # encode() 返回 numpy array，tolist() 转为 Python 原生列表
        embeddings = self.model.encode(input)
        return embeddings.tolist()


def _split_text(text: str, chunk_size: int = 500) -> List[str]:
    """
    按句子边界将长文本切分为不超过 chunk_size 字的块。

    为什么要切片：
      - LLM 有 context 长度限制，不能把整本书塞进去
      - 向量检索的粒度决定召回精度：太长→噪声多，太短→上下文不足
      - 500 字≈2-5 段正文，是经验上的平衡点

    切片策略：
      - 按中文句子结束符（。！？）和换行符分割
      - 不在句子中间截断，保证每个块语义完整
      - 积累到超过 chunk_size 才开新块
    """
    import re
    # 在句子结束符后面分割（用 lookahead 保留分隔符）
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
    # 过滤空块
    return [c for c in chunks if c]


def process_document(file_path: str) -> List[dict]:
    """
    解析单个文件，返回文本块列表，格式：[{"text": str, "page": int}, ...]

    支持的格式：
      - .txt / .md → deepdoc RAGFlowTxtParser（语义切片）
      - .pdf → PyMuPDF（fallback，扫描版 PDF 应先用 pdf_to_md.py 转换）

    为什么用 deepdoc 而不是简单 split：
      deepdoc 按段落、章节等语义边界切片，保留上下文完整性；
      简单按字数切会在关键句子中间截断，影响检索质量。
    """
    ext = file_path.lower().split('.')[-1]
    results = []

    try:
        if ext in ('txt', 'md'):
            print(f"  使用 RAGFlowTxtParser 解析")
            parser = RAGFlowTxtParser()
            # deepdoc 解析器需要传 binary 内容（bytes），同时需要文件路径（用于类型判断）
            with open(file_path, 'rb') as f:
                content = f.read()
            # 注意：必须传 binary=content，不能只传路径，beartype 会做类型校验
            raw_chunks = parser(file_path, binary=content)
            for chunk in raw_chunks:
                # deepdoc 返回的每个 chunk 可能是 tuple(text, ...) 或纯字符串
                text = chunk[0] if isinstance(chunk, (list, tuple)) else str(chunk)
                if text.strip():
                    results.append({"text": text.strip(), "page": 1})

        elif ext == 'pdf':
            # 注意：正式流程中 PDF 应先用 pdf_to_md.py 转为 MD 再入库
            # 这里是 fallback：处理没有对应 MD 的 PDF（效果可能不佳）
            print(f"  使用 PyMuPDF (fitz) 解析（建议先用 pdf_to_md.py 转换）")
            with fitz.open(file_path) as pdf:
                total_pages = len(pdf)
                pages_with_text = 0
                for page_num, page in enumerate(pdf, 1):
                    page_text = (page.get_text("text") or "").strip()
                    if page_text:
                        pages_with_text += 1
                        # 每页文字再做二次切片（避免单页内容过长）
                        for chunk in _split_text(page_text):
                            results.append({"text": chunk, "page": page_num})
                print(f"  共 {total_pages} 页，{pages_with_text} 页有文本")
        else:
            print(f"  不支持 {ext} 格式，跳过")

    except Exception as e:
        print(f"  解析出错: {e}")

    print(f"  切分完成，共 {len(results)} 个块")
    return results


def main():
    parser = argparse.ArgumentParser(description="一键化本地数据写入知识库")
    parser.add_argument(
        "--clear",
        action="store_true",
        help="清空已有向量数据库后重新入库（推荐首次或更换文档集时使用）"
    )
    args = parser.parse_args()

    # 确保目录存在
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(CHROMA_DB_DIR, exist_ok=True)

    # 扫描 data/ 下所有文件（只取文件，不递归子目录）
    files_to_process = [
        os.path.join(DATA_DIR, f)
        for f in os.listdir(DATA_DIR)
        if os.path.isfile(os.path.join(DATA_DIR, f))
    ]

    # 跳过已有对应 .md 的 PDF（这些 PDF 应由 pdf_to_md.py 转换，再以 .md 入库）
    # 目的：防止同一本书以 PDF 和 MD 两种形式重复入库
    files_to_process = [
        f for f in files_to_process
        if not (f.lower().endswith('.pdf') and
                os.path.exists(os.path.splitext(f)[0] + '.md'))
    ]

    if not files_to_process:
        print(f"在 {DATA_DIR} 目录下没有找到任何文件。请放入文档或先运行 pdf_to_md.py。")
        return

    # ──────────────────────────────────────────
    # 初始化 ChromaDB 和 Embedding 模型
    # ──────────────────────────────────────────
    # PersistentClient 会把数据写到磁盘，重启后数据不丢失
    chroma_client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
    embedding_func = LocalEmbeddingFunction(EMBEDDING_MODEL_NAME)

    if args.clear:
        # 删除旧 collection，从头重建（常用于文档集更换后）
        try:
            chroma_client.delete_collection(name=COLLECTION_NAME)
            print(f"已清空旧库集合: {COLLECTION_NAME}")
        except ValueError:
            pass  # collection 不存在时忽略

    # get_or_create：不存在则新建，已存在则直接用
    # hnsw:space=cosine：使用余弦距离，对文本语义匹配比欧氏距离效果好
    collection = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_func,
        metadata={"hnsw:space": "cosine"},
    )

    # ──────────────────────────────────────────
    # 解析文件并写入向量库
    # ──────────────────────────────────────────
    for file_path in files_to_process:
        fname = os.path.basename(file_path)
        print(f"\n>>>> 开始处理: {fname}")
        chunk_dicts = process_document(file_path)

        if not chunk_dicts:
            continue

        # 构建唯一 ID：文件名 + 块序号，确保幂等（重复运行时 upsert 更新而不是报错）
        ids = [f"{fname}_chunk_{i}" for i in range(len(chunk_dicts))]
        documents = [c["text"] for c in chunk_dicts]
        # 元数据：来源文件名、页码、块索引（检索结果展示时用于溯源）
        metadatas = [
            {"source": fname, "page": c["page"], "chunk_index": i}
            for i, c in enumerate(chunk_dicts)
        ]

        print(f"  正在生成向量并写入 ChromaDB...")
        # upsert = insert or update，ID 已存在则覆盖，避免重复数据
        collection.upsert(documents=documents, metadatas=metadatas, ids=ids)
        print(f"  {fname} 成功入库！")

    print("\n✅ 所有文件处理完毕。知识集已持久化到 storage/ 目录。")
    print("总计入库文档块:", collection.count())


if __name__ == "__main__":
    main()
