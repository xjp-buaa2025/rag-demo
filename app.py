"""
app.py — Gradio Web 问答界面（完整功能版）

职责：
  提供基于浏览器的图形界面，集成了：
  1. 知识库管理面板：一键扫描 data/ 并入库，支持增量/清空重建
  2. 流式问答对话：打字机效果，回答下方显示参考来源

与 main_chat.py 的区别：
  - main_chat.py：终端交互，适合调试
  - app.py：Web 界面，适合正式使用，功能更完整

运行方式：
  PYTHONUTF8=1 python app.py
  然后浏览器访问 http://127.0.0.1:7860

详见 PROJECT_GUIDE.md § 6.4
"""

import os
import sys
from typing import List

from dotenv import load_dotenv
import chromadb
from sentence_transformers import SentenceTransformer
from openai import OpenAI
import gradio as gr

# 加载 .env 配置
load_dotenv()
# 加入 document_processing/ 搜索路径（deepdoc shim 模块）
sys.path.append(os.path.join(os.path.dirname(__file__), 'document_processing'))

# 复用 main_ingest 的文档解析逻辑，避免重复代码
from main_ingest import process_document


# ==========================================
# 配置
# ==========================================

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
CHROMA_DB_DIR = os.path.join(os.path.dirname(__file__), 'storage', 'chroma_db')
COLLECTION_NAME = "local_rag_knowledge"
EMBEDDING_MODEL_NAME = "BAAI/bge-m3"
TOP_K = 4  # 每次检索返回 4 个相关块（比 main_chat.py 多一个，给 Web 用户更多参考）

LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.siliconflow.cn/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "Qwen/Qwen2.5-14B-Instruct")

SYSTEM_PROMPT = """你是一个专业的知识库问答助手。请严格根据提供的参考资料回答用户问题。
如果参考资料中没有相关信息，请如实说明"知识库中没有找到相关内容"，不要凭空捏造。
回答要简洁、准确。"""


# ==========================================
# 全局初始化（模块加载时执行一次）
# ==========================================
# 设计原因：Embedding 模型加载耗时 10-30 秒，放在全局避免每次请求重复初始化。
# Gradio 是单进程多线程模型，全局对象在所有请求间共享，但 SentenceTransformer
# 和 ChromaDB 的读操作是线程安全的。

print("正在初始化，请稍候...")


class LocalEmbeddingFunction:
    """SentenceTransformer 的 ChromaDB 接口包装，与 main_ingest.py 保持一致。"""
    def __init__(self, model_name: str):
        self.model = SentenceTransformer(model_name)
        self._model_name = model_name

    def name(self) -> str:
        return self._model_name

    def __call__(self, input: List[str]) -> List[List[float]]:
        return self.model.encode(input).tolist()


# 全局单例：启动时初始化，之后所有请求复用
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
    """
    扫描 data/ 目录，解析所有文件写入 ChromaDB。

    这是一个生成器函数（有 yield），每处理一步就 yield 一次日志，
    Gradio 会把每次 yield 的内容实时显示在 UI 上（而不是等全部完成才更新）。

    yield 格式：(日志文本, 状态文本)，对应两个 Gradio 输出组件。

    参数：
      clear_first：True = 先清空旧数据再入库，False = 增量追加
    """
    global collection  # 需要修改全局 collection 引用（clear 时重新创建）
    lines = []

    def emit(msg):
        """追加一行日志，返回累计全文（用于 Gradio 的 Textbox 更新）"""
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
        # 删除旧 collection 并重新创建（全量重建知识库）
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

        # 构建 ChromaDB 所需的三个并行列表
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
    """返回知识库当前状态文本（用于 UI 状态栏显示）"""
    return f"知识库：**{collection.count()} 条文档块**"


# ==========================================
# 检索 & 问答逻辑
# ==========================================

def retrieve(query: str) -> List[dict]:
    """
    向量检索。

    注意：n_results 不能超过 collection.count()，
    否则 ChromaDB 会报错，所以用 min() 取最小值。
    """
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
    """
    将检索结果格式化为 Markdown，追加在回答末尾展示参考来源。

    格式示例：
      ---
      📚 参考来源
      [1] book.md · 第 42 页
      _原文片段开头…_
    """
    if not chunks:
        return ""
    lines = ["\n\n---\n**📚 参考来源**\n"]
    for i, c in enumerate(chunks, 1):
        page_info = f" · 第 {c['page']} 页" if c.get("page") else ""
        snippet = c["text"][:80].replace("\n", " ")
        lines.append(f"**[{i}] {c['source']}{page_info}**  \n_{snippet}…_\n")
    return "\n".join(lines)


def chat(message: str, history: list):
    """
    Gradio ChatInterface 的回调函数，必须是生成器（有 yield）。

    Gradio 约定：
      - 输入：message（当前用户输入），history（历史对话列表，每项为 [user, assistant]）
      - 输出：yield 字符串，每次 yield 更新界面（流式效果）

    流式输出实现：
      stream=True → LLM 边生成边返回 token
      每次收到 token 就 yield 累积内容，Gradio 刷新 UI
      最后一次 yield 追加参考来源

    历史窗口限制：
      只取最近 6 轮历史（history[-6:]），防止 prompt 超出 LLM context 长度限制。
    """
    if collection.count() == 0:
        yield "⚠️ 知识库为空，请先点击上方「扫描入库」按钮导入文档。"
        return

    # 检索相关文本块
    chunks = retrieve(message)

    # 构建 messages 列表（OpenAI 格式）
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    # 追加近期历史（实现多轮对话上下文）
    for user_msg, assistant_msg in history[-6:]:
        messages.append({"role": "user", "content": user_msg})
        messages.append({"role": "assistant", "content": assistant_msg})

    # 将检索原文拼入用户消息（RAG 的核心：让 LLM "开卷作答"）
    context = "\n\n".join(
        f"[{i+1}] 来源：{c['source']}" + (f" 第{c['page']}页" if c.get("page") else "") + f"\n{c['text']}"
        for i, c in enumerate(chunks)
    )
    user_content = f"参考资料：\n{context}\n\n用户问题：{message}" if chunks else message
    messages.append({"role": "user", "content": user_content})

    # 流式调用 LLM，逐 token yield 给 Gradio
    full_answer = ""
    try:
        stream = llm_client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            temperature=0.3,
            stream=True,  # 关键：开启流式输出
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            full_answer += delta
            yield full_answer  # 每次 yield 触发 Gradio 刷新
    except Exception as e:
        yield f"❌ LLM 调用失败：{e}"
        return

    # 最后一次 yield：在回答末尾追加参考来源（Markdown 格式）
    yield full_answer + format_sources(chunks)


# ==========================================
# Gradio UI 布局
# ==========================================

with gr.Blocks(title="本地知识库 RAG 问答") as demo:
    gr.Markdown("## 📖 本地知识库 RAG 问答")
    gr.Markdown(f"模型：`{LLM_MODEL}` &nbsp;·&nbsp; Embedding：`{EMBEDDING_MODEL_NAME}`")

    # 折叠面板：知识库管理（默认折叠，不干扰问答主界面）
    with gr.Accordion("📂 知识库管理", open=False):
        status_md = gr.Markdown(_status())   # 显示当前知识库文档块数
        with gr.Row():
            ingest_btn = gr.Button("🔄 扫描 data/ 并入库（增量）", variant="primary", scale=2)
            clear_btn = gr.Button("🗑️ 清空后重建", variant="stop", scale=1)
        ingest_log = gr.Textbox(
            label="入库日志",
            lines=10,
            interactive=False,
            placeholder="点击按钮后这里会显示入库进度…",
        )

    # 主界面：对话组件
    gr.ChatInterface(
        fn=chat,
        examples=["RAG是什么？", "RAG有哪些核心步骤？", "RAG和直接微调模型有什么区别？"],
        chatbot=gr.Chatbot(height=460, render_markdown=True),
        textbox=gr.Textbox(placeholder="输入问题，按 Enter 发送…", scale=9),
    )

    # 注意：Gradio 要求事件回调必须是具名函数，lambda 无法被正确识别为生成器
    def do_ingest():
        yield from run_ingest(clear_first=False)

    def do_clear_ingest():
        yield from run_ingest(clear_first=True)

    # 绑定按钮事件：输出写入日志框和状态栏
    ingest_btn.click(fn=do_ingest, outputs=[ingest_log, status_md])
    clear_btn.click(fn=do_clear_ingest, outputs=[ingest_log, status_md])


if __name__ == "__main__":
    # Windows 代理可能导致本地请求被拦截，显式绕过代理
    os.environ.setdefault("NO_PROXY", "127.0.0.1,localhost")
    os.environ.setdefault("no_proxy", "127.0.0.1,localhost")
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,          # 不生成公网链接
        theme=gr.themes.Soft(),
        show_error=True,      # 在 UI 上显示后端报错，方便调试
    )
