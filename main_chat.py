"""
main_chat.py — 终端交互式 RAG 问答（调试/轻量使用）

职责：
  在命令行实现多轮对话，每轮自动检索相关文本块，拼入 prompt 后调用 LLM 生成回答。

与 app.py 的区别：
  - 本文件：纯终端，无界面，适合快速验证效果、调试
  - app.py：Gradio Web 界面，适合正式使用

运行方式：
  PYTHONUTF8=1 python main_chat.py

详见 PROJECT_GUIDE.md § 6.3
"""

import os
import sys
from typing import List

from dotenv import load_dotenv   # 读取 .env 文件中的配置
import chromadb
from sentence_transformers import SentenceTransformer
from openai import OpenAI        # OpenAI 兼容 SDK，对接 SiliconFlow / vLLM

# 加载 .env 文件（LLM_API_KEY、LLM_BASE_URL、LLM_MODEL）
load_dotenv()

# 将 document_processing/ 加入搜索路径（deepdoc shim 模块需要）
sys.path.append(os.path.join(os.path.dirname(__file__), 'document_processing'))


# ==========================================
# 配置（从环境变量读取，默认值用于开发时的 fallback）
# ==========================================

CHROMA_DB_DIR = os.path.join(os.path.dirname(__file__), 'storage', 'chroma_db')
COLLECTION_NAME = "local_rag_knowledge"
EMBEDDING_MODEL_NAME = "BAAI/bge-m3"
TOP_K = 3  # 每次检索返回最相关的 3 个文本块

LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.minimax.chat/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "MiniMax-Text-01")

# 系统提示：限制 LLM 只根据检索到的参考资料回答，防止幻觉
SYSTEM_PROMPT = """你是一个专业的知识库问答助手。请严格根据以下检索到的参考资料回答用户问题。
如果参考资料中没有相关信息，请如实说明"知识库中没有找到相关内容"，不要凭空捏造。
回答要简洁、准确，并在适当时指出信息来源。"""


class LocalEmbeddingFunction:
    """
    SentenceTransformer 的 ChromaDB 接口包装。
    与 main_ingest.py 中的版本完全相同——两处保持一致，确保入库和检索使用同一个模型。

    注意：入库和查询必须用同一个 Embedding 模型，否则向量空间不一致，检索结果无意义。
    """
    def __init__(self, model_name: str):
        print(f"正在加载 Embedding 模型: {model_name} ...")
        self.model = SentenceTransformer(model_name)
        self._model_name = model_name

    def name(self) -> str:
        return self._model_name

    def __call__(self, input: List[str]) -> List[List[float]]:
        return self.model.encode(input).tolist()


def retrieve(collection, embedding_func, query: str, top_k: int = TOP_K) -> List[dict]:
    """
    向量检索：将用户问题向量化，在 ChromaDB 中找最相似的 top_k 个文本块。

    步骤：
      1. 把用户问题转为向量（和入库时用同一个 Embedding 模型）
      2. ChromaDB 用余弦距离找最近的 top_k 个向量
      3. 返回对应的文本、来源文件名、距离

    distance 的含义：
      - 余弦距离范围 [0, 2]，越小越相似（0 = 完全相同，2 = 完全相反）
      - 实践中 < 0.3 表示高度相关，> 0.8 可能已经不相关
    """
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
    """
    将检索到的文本块拼入用户消息。

    格式：
      参考资料：
      [1] 来源: xxx.md
      （原文内容）

      [2] 来源: yyy.md
      （原文内容）

      用户问题：XXX

    为什么这样拼：
      LLM 读到"参考资料"时会优先基于原文回答，而不是靠自己的参数知识，
      从而大幅降低幻觉概率，并且可以溯源。
    """
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        context_parts.append(f"[{i}] 来源: {chunk['source']}\n{chunk['text']}")
    context = "\n\n".join(context_parts)
    return f"参考资料：\n{context}\n\n用户问题：{query}"


def chat(client: OpenAI, messages: list) -> str:
    """
    调用 LLM 生成回答。

    messages 格式符合 OpenAI ChatCompletion 规范：
      [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}, ...]

    temperature=0.3：
      RAG 问答需要"忠实于原文"，低温度 = 低创造性 = 更确定性的回答。
      0 = 完全确定性（每次结果相同），1 = 最大发散，0.3 是保守且流畅的平衡点。
    """
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        temperature=0.3,
    )
    return response.choices[0].message.content


def main():
    # ──────────────────────────────────────────
    # 初始化各组件
    # ──────────────────────────────────────────
    embedding_func = LocalEmbeddingFunction(EMBEDDING_MODEL_NAME)

    # 连接 ChromaDB（PersistentClient 读取磁盘上已有的数据库文件）
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

    # 初始化 LLM 客户端（OpenAI SDK 兼容任意符合该接口的服务）
    client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)

    # messages 维护完整对话历史，实现多轮对话
    # 第一条始终是系统提示，后续交替追加 user/assistant 消息
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

        # ── 检索阶段 ──────────────────────────
        chunks = retrieve(collection, embedding_func, query)
        if chunks:
            print(f"  [检索到 {len(chunks)} 个相关片段，最近距离: {chunks[0]['distance']:.4f}]")

        # ── 构建本轮 user 消息（问题 + 检索原文） ──
        user_content = build_prompt(query, chunks)
        messages.append({"role": "user", "content": user_content})

        # ── LLM 生成阶段 ──────────────────────
        try:
            answer = chat(client, messages)
        except Exception as e:
            print(f"LLM 调用失败: {e}")
            # 生成失败时回滚刚才追加的 user 消息，保持 messages 一致性
            messages.pop()
            continue

        # 把本轮回答也加入历史，下一轮 LLM 可以看到上下文
        messages.append({"role": "assistant", "content": answer})
        print(f"\n助手: {answer}\n")


if __name__ == "__main__":
    main()
