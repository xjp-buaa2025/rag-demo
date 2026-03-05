import os
import sys
from typing import List

from dotenv import load_dotenv
import chromadb
from sentence_transformers import SentenceTransformer
from openai import OpenAI

load_dotenv()

sys.path.append(os.path.join(os.path.dirname(__file__), 'document_processing'))

# ==========================================
# 配置
# ==========================================
CHROMA_DB_DIR = os.path.join(os.path.dirname(__file__), 'storage', 'chroma_db')
COLLECTION_NAME = "local_rag_knowledge"
EMBEDDING_MODEL_NAME = "BAAI/bge-m3"
TOP_K = 3  # 召回最相关的 chunk 数量

LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.minimax.chat/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "MiniMax-Text-01")

SYSTEM_PROMPT = """你是一个专业的知识库问答助手。请严格根据以下检索到的参考资料回答用户问题。
如果参考资料中没有相关信息，请如实说明"知识库中没有找到相关内容"，不要凭空捏造。
回答要简洁、准确，并在适当时指出信息来源。"""


class LocalEmbeddingFunction:
    def __init__(self, model_name: str):
        print(f"正在加载 Embedding 模型: {model_name} ...")
        self.model = SentenceTransformer(model_name)
        self._model_name = model_name

    def name(self) -> str:
        return self._model_name

    def __call__(self, input: List[str]) -> List[List[float]]:
        return self.model.encode(input).tolist()


def retrieve(collection, embedding_func, query: str, top_k: int = TOP_K) -> List[dict]:
    """向量检索，返回最相关的 chunks"""
    query_embedding = embedding_func([query])[0]
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )
    chunks = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        chunks.append({"text": doc, "source": meta.get("source", ""), "distance": dist})
    return chunks


def build_prompt(query: str, chunks: List[dict]) -> str:
    """将检索结果拼入 user prompt"""
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        context_parts.append(f"[{i}] 来源: {chunk['source']}\n{chunk['text']}")
    context = "\n\n".join(context_parts)
    return f"参考资料：\n{context}\n\n用户问题：{query}"


def chat(client: OpenAI, messages: list) -> str:
    """调用 LLM 生成回答"""
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        temperature=0.3,
    )
    return response.choices[0].message.content


def main():
    # 初始化
    embedding_func = LocalEmbeddingFunction(EMBEDDING_MODEL_NAME)
    chroma_client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
    collection = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_func,
        metadata={"hnsw:space": "cosine"},
    )

    if collection.count() == 0:
        print("知识库为空，请先运行 main_ingest.py 导入文档。")
        return

    print(f"知识库已加载，共 {collection.count()} 条文档块。")

    client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    print("\n=== RAG 问答系统启动 ===")
    print("输入问题开始对话，输入 'exit' 或 Ctrl+C 退出。\n")

    while True:
        try:
            query = input("你: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n再见！")
            break

        if not query:
            continue
        if query.lower() in ("exit", "quit", "退出"):
            print("再见！")
            break

        # 检索
        chunks = retrieve(collection, embedding_func, query)
        if chunks:
            print(f"  [检索到 {len(chunks)} 个相关片段，最近距离: {chunks[0]['distance']:.4f}]")

        # 构建本轮 user message
        user_content = build_prompt(query, chunks)
        messages.append({"role": "user", "content": user_content})

        # 生成
        try:
            answer = chat(client, messages)
        except Exception as e:
            print(f"LLM 调用失败: {e}")
            messages.pop()  # 回滚失败的消息
            continue

        messages.append({"role": "assistant", "content": answer})
        print(f"\n助手: {answer}\n")


if __name__ == "__main__":
    main()
