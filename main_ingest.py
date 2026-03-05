import os
import argparse
from typing import List, Dict, Any

# 1. 导入 ChromaDB 作为轻量级本地向量数据库
import chromadb
from chromadb.config import Settings

# 2. 导入本机的 Embedding 模型 (SentenceTransformers)
from sentence_transformers import SentenceTransformer

# 3. 导入 RAGFlow 抽离出的 DeepDoc 用于高精度的文档切片
# 注意：我们要确保 Python 的包搜索路径能找到 document_processing
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'document_processing'))

try:
    from deepdoc.parser.txt_parser import RAGFlowTxtParser
except ImportError as e:
    print(f"警告：导入 TxtParser 失败: {e}")
    RAGFlowTxtParser = None

# PDF 解析器：PyMuPDF，对中文 PDF 文本提取能力强，直接作为主解析器
import fitz  # PyMuPDF


# ==========================================
# 配置常量
# ==========================================
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
CHROMA_DB_DIR = os.path.join(os.path.dirname(__file__), 'storage', 'chroma_db')
COLLECTION_NAME = "local_rag_knowledge"
# 这里我们选用 BAAI 的 m3 中文兼容轻量模型作为 Embedding，第一次运行会自动下载
EMBEDDING_MODEL_NAME = "BAAI/bge-m3" 


class LocalEmbeddingFunction:
    """包装 SentenceTransformer 以符合 ChromaDB 的 EmbeddingFunction 接口协议"""
    def __init__(self, model_name: str):
        print(f"正在加载 Embedding 模型: {model_name} ...")
        self.model = SentenceTransformer(model_name)
        self._model_name = model_name

    def name(self) -> str:
        # ChromaDB 1.5+ 要求 EmbeddingFunction 实现 name() 方法
        return self._model_name

    def __call__(self, input: List[str]) -> List[List[float]]:
        # SentenceTransformer 的 encode 返回 numpy array，转换为 list 即可
        embeddings = self.model.encode(input)
        return embeddings.tolist()


def _split_text(text: str, chunk_size: int = 500) -> List[str]:
    """按句子边界将长文本切分为不超过 chunk_size 字的块"""
    import re
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


def process_document(file_path: str) -> List[dict]:
    """解析文件，返回 [{"text": ..., "page": ...}, ...] 列表"""
    ext = file_path.lower().split('.')[-1]
    results = []

    try:
        if ext in ('txt', 'md'):
            print(f"  使用 RAGFlowTxtParser 解析")
            parser = RAGFlowTxtParser()
            with open(file_path, 'rb') as f:
                content = f.read()
            raw_chunks = parser(file_path, binary=content)
            for chunk in raw_chunks:
                text = chunk[0] if isinstance(chunk, (list, tuple)) else str(chunk)
                if text.strip():
                    results.append({"text": text.strip(), "page": 1})

        elif ext == 'pdf':
            print(f"  使用 PyMuPDF (fitz) 解析")
            with fitz.open(file_path) as pdf:
                total_pages = len(pdf)
                pages_with_text = 0
                for page_num, page in enumerate(pdf, 1):
                    page_text = (page.get_text("text") or "").strip()
                    if page_text:
                        pages_with_text += 1
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
    parser.add_argument("--clear", action="store_true", help="如果设置，清空已有的向量数据库")
    args = parser.parse_args()

    # 1. 确保数据目录存在
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(CHROMA_DB_DIR, exist_ok=True)
    
    files_to_process = [os.path.join(DATA_DIR, f) for f in os.listdir(DATA_DIR) if os.path.isfile(os.path.join(DATA_DIR, f))]

    # 跳过已有对应 .md 文件的 PDF（由 pdf_to_md.py 转换，避免重复入库）
    files_to_process = [
        f for f in files_to_process
        if not (f.lower().endswith('.pdf') and
                os.path.exists(os.path.splitext(f)[0] + '.md'))
    ]

    if not files_to_process:
        print(f"在 {DATA_DIR} 目录下没有找到任何文件。请放入您的文本文件或 PDF。")
        return

    # 2. 初始化 ChromaDB 与 Embedding
    chroma_client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
    embedding_func = LocalEmbeddingFunction(EMBEDDING_MODEL_NAME)
    
    if args.clear:
        try:
            chroma_client.delete_collection(name=COLLECTION_NAME)
            print(f"已清空旧库集合: {COLLECTION_NAME}")
        except ValueError:
            pass # 要删除的 collection 不存在

    collection = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME, 
        embedding_function=embedding_func,
        metadata={"hnsw:space": "cosine"} # 对纯文本比对建议用余弦距离
    )
    
    # 3. 解析文件并灌库
    for file_path in files_to_process:
        fname = os.path.basename(file_path)
        print(f"\n>>>> 开始处理: {fname}")
        chunk_dicts = process_document(file_path)

        if not chunk_dicts:
            continue

        ids = [f"{fname}_chunk_{i}" for i in range(len(chunk_dicts))]
        documents = [c["text"] for c in chunk_dicts]
        metadatas = [
            {"source": fname, "page": c["page"], "chunk_index": i}
            for i, c in enumerate(chunk_dicts)
        ]

        print(f"  正在生成向量并写入 ChromaDB...")
        collection.upsert(documents=documents, metadatas=metadatas, ids=ids)
        print(f"  {fname} 成功入库！")
        
    print("\n✅ 所有文件处理完毕。知识集已持久化到 Storage 目录。")
    print("总计入库文档树:", collection.count())

if __name__ == "__main__":
    main()
