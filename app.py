import os
import sys
from typing import List

from dotenv import load_dotenv
import chromadb
from sentence_transformers import SentenceTransformer
from openai import OpenAI
import gradio as gr

load_dotenv()
sys.path.append(os.path.join(os.path.dirname(__file__), 'document_processing'))

# 复用 main_ingest 的文档解析逻辑
from main_ingest import process_document

# ==========================================
# 配置
# ==========================================
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
CHROMA_DB_DIR = os.path.join(os.path.dirname(__file__), 'storage', 'chroma_db')
COLLECTION_NAME = "local_rag_knowledge"
EMBEDDING_MODEL_NAME = "BAAI/bge-m3"
TOP_K = 4

LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.siliconflow.cn/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "Qwen/Qwen2.5-14B-Instruct")

SYSTEM_PROMPT = """你是一个专业的知识库问答助手。请严格根据提供的参考资料回答用户问题。
如果参考资料中没有相关信息，请如实说明"知识库中没有找到相关内容"，不要凭空捏造。
回答要简洁、准确。"""

# ==========================================
# 全局初始化（启动时加载一次）
# ==========================================
print("正在初始化，请稍候...")


class LocalEmbeddingFunction:
    def __init__(self, model_name: str):
        self.model = SentenceTransformer(model_name)
        self._model_name = model_name

    def name(self) -> str:
        return self._model_name

    def __call__(self, input: List[str]) -> List[List[float]]:
        return self.model.encode(input).tolist()


embedding_func = LocalEmbeddingFunction(EMBEDDING_MODEL_NAME)
chroma_client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
collection = chroma_client.get_or_create_collection(
    name=COLLECTION_NAME,
    embedding_function=embedding_func,
    metadata={"hnsw:space": "cosine"},
)
llm_client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)
print(f"初始化完成，知识库共 {collection.count()} 条文档块。")


# ==========================================
# 入库逻辑
# ==========================================
def run_ingest(clear_first: bool = False):
    """扫描 data/ 目录，解析所有文件写入 ChromaDB，yield (日志文本, 状态文本)"""
    global collection
    lines = []

    def emit(msg):
        lines.append(msg)
        return "\n".join(lines)

    os.makedirs(DATA_DIR, exist_ok=True)
    files = sorted([
        f for f in os.listdir(DATA_DIR)
        if os.path.isfile(os.path.join(DATA_DIR, f))
    ])

    if not files:
        yield emit("⚠️  data/ 目录下没有找到任何文件，请先放入文档。"), _status()
        return

    if clear_first:
        try:
            chroma_client.delete_collection(name=COLLECTION_NAME)
            collection = chroma_client.get_or_create_collection(
                name=COLLECTION_NAME,
                embedding_function=embedding_func,
                metadata={"hnsw:space": "cosine"},
            )
            yield emit("🗑️  已清空旧数据，重新开始入库…"), _status()
        except Exception as e:
            yield emit(f"清空失败: {e}"), _status()
            return

    yield emit(f"📂  共发现 {len(files)} 个文件，开始处理…\n"), _status()

    for fname in files:
        file_path = os.path.join(DATA_DIR, fname)
        yield emit(f"▶  {fname}"), _status()

        chunk_dicts = process_document(file_path)

        if not chunk_dicts:
            yield emit(f"   ⚠️  无有效内容，跳过"), _status()
            continue

        ids = [f"{fname}_chunk_{i}" for i in range(len(chunk_dicts))]
        documents = [c["text"] for c in chunk_dicts]
        metadatas = [
            {"source": fname, "page": c["page"], "chunk_index": i}
            for i, c in enumerate(chunk_dicts)
        ]

        yield emit(f"   向量化并写入 {len(chunk_dicts)} 个块…"), _status()
        collection.upsert(documents=documents, metadatas=metadatas, ids=ids)
        yield emit(f"   ✅  入库完成"), _status()

    yield emit(f"\n🎉  全部完成！知识库共 {collection.count()} 条文档块。"), _status()


def _status() -> str:
    return f"知识库：**{collection.count()} 条文档块**"


# ==========================================
# 检索 & 问答逻辑
# ==========================================
def retrieve(query: str) -> List[dict]:
    n = min(TOP_K, collection.count())
    if n == 0:
        return []
    query_embedding = embedding_func([query])[0]
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n,
        include=["documents", "metadatas", "distances"],
    )
    return [
        {
            "text": doc,
            "source": meta.get("source", "未知"),
            "page": meta.get("page", 0),
            "distance": dist,
        }
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        )
    ]


def format_sources(chunks: List[dict]) -> str:
    if not chunks:
        return ""
    lines = ["\n\n---\n**📚 参考来源**\n"]
    for i, c in enumerate(chunks, 1):
        page_info = f" · 第 {c['page']} 页" if c.get("page") else ""
        snippet = c["text"][:80].replace("\n", " ")
        lines.append(f"**[{i}] {c['source']}{page_info}**  \n_{snippet}…_\n")
    return "\n".join(lines)


def chat(message: str, history: list):
    if collection.count() == 0:
        yield "⚠️ 知识库为空，请先点击上方「扫描入库」按钮导入文档。"
        return

    chunks = retrieve(message)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for user_msg, assistant_msg in history[-6:]:
        messages.append({"role": "user", "content": user_msg})
        messages.append({"role": "assistant", "content": assistant_msg})

    context = "\n\n".join(
        f"[{i+1}] 来源：{c['source']}" + (f" 第{c['page']}页" if c.get("page") else "") + f"\n{c['text']}"
        for i, c in enumerate(chunks)
    )
    user_content = f"参考资料：\n{context}\n\n用户问题：{message}" if chunks else message
    messages.append({"role": "user", "content": user_content})

    full_answer = ""
    try:
        stream = llm_client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            temperature=0.3,
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            full_answer += delta
            yield full_answer
    except Exception as e:
        yield f"❌ LLM 调用失败：{e}"
        return

    yield full_answer + format_sources(chunks)


# ==========================================
# Gradio UI
# ==========================================
with gr.Blocks(title="本地知识库 RAG 问答") as demo:
    gr.Markdown("## 📖 本地知识库 RAG 问答")
    gr.Markdown(f"模型：`{LLM_MODEL}` &nbsp;·&nbsp; Embedding：`{EMBEDDING_MODEL_NAME}`")

    # 知识库管理面板
    with gr.Accordion("📂 知识库管理", open=False):
        status_md = gr.Markdown(_status())
        with gr.Row():
            ingest_btn = gr.Button("🔄 扫描 data/ 并入库（增量）", variant="primary", scale=2)
            clear_btn = gr.Button("🗑️ 清空后重建", variant="stop", scale=1)
        ingest_log = gr.Textbox(
            label="入库日志",
            lines=10,
            interactive=False,
            placeholder="点击按钮后这里会显示入库进度…",
        )

    # 问答主界面
    gr.ChatInterface(
        fn=chat,
        examples=["RAG是什么？", "RAG有哪些核心步骤？", "RAG和直接微调模型有什么区别？"],
        chatbot=gr.Chatbot(height=460, render_markdown=True),
        textbox=gr.Textbox(placeholder="输入问题，按 Enter 发送…", scale=9),
    )

    # 按钮事件（必须用具名 generator 函数，lambda 不会被 Gradio 识别为 generator）
    def do_ingest():
        yield from run_ingest(clear_first=False)

    def do_clear_ingest():
        yield from run_ingest(clear_first=True)

    ingest_btn.click(fn=do_ingest, outputs=[ingest_log, status_md])
    clear_btn.click(fn=do_clear_ingest, outputs=[ingest_log, status_md])


if __name__ == "__main__":
    os.environ.setdefault("NO_PROXY", "127.0.0.1,localhost")
    os.environ.setdefault("no_proxy", "127.0.0.1,localhost")
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        theme=gr.themes.Soft(),
        show_error=True,
    )
