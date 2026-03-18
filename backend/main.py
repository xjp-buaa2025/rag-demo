"""
backend/main.py — FastAPI 应用入口

职责：
  1. lifespan：启动时初始化所有全局单例（Embedding、ChromaDB、LLM），关闭时清理
  2. 注册所有 Router（/ingest、/retrieve、/chat、/eval、/bom、/assembly）
  3. 配置 CORS（允许 React 开发服务器 localhost:3000）
  4. 提供 GET /health 健康检查接口

运行方式：
  PYTHONUTF8=1 uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
  或使用 run_backend.py 快捷启动。

详见 PROJECT_GUIDE.md § FastAPI 后端
"""

import os
import sys
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

# 加载环境变量（.env 文件）
load_dotenv()

# 将项目根目录加入 sys.path，使 document_processing/ shim 模块可以被 main_ingest 找到
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "document_processing"))

# ==========================================
# 配置常量（从 .env 读取，保持与 app.py 一致）
# ==========================================
CHROMA_DB_DIR      = os.path.join(_ROOT, "storage", "chroma_db")
COLLECTION_NAME    = "local_rag_knowledge"
EMBEDDING_MODEL    = "BAAI/bge-m3"

LLM_API_KEY        = os.getenv("LLM_API_KEY")
LLM_BASE_URL       = os.getenv("LLM_BASE_URL",   "https://api.siliconflow.cn/v1")
LLM_MODEL          = os.getenv("LLM_MODEL",       "Qwen/Qwen2.5-14B-Instruct")
MINIMAX_API_KEY    = os.getenv("MINIMAX_API_KEY", "").strip()
MINIMAX_BASE_URL   = os.getenv("MINIMAX_BASE_URL","https://api.minimaxi.com/v1")
MINIMAX_MODEL      = os.getenv("MINIMAX_MODEL",   "MiniMax-M2.5")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan：yield 前为启动逻辑，yield 后为关闭逻辑。
    uvicorn 在 lifespan 完成前不接受任何请求，保证初始化完成后才上线。
    """
    import chromadb
    from openai import OpenAI
    from backend.state import AppState, FallbackLLMClient, LocalEmbeddingFunction

    print("[backend] 正在初始化，请稍候…")

    # 1. Embedding 模型（耗时 10-30 秒，CPU 纯推理）
    embedding_func = LocalEmbeddingFunction(EMBEDDING_MODEL)

    # 2. ChromaDB 持久化客户端 + 集合
    # 两层恢复机制：
    #   a) 客户端层：若存储目录格式与当前版本不兼容（如从旧版本升降级），清空目录重建
    #   b) 集合层：若 HNSW 索引文件损坏（强制杀进程导致），重建集合
    import shutil as _shutil
    try:
        chroma_client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
    except Exception as _e:
        print(f"[警告] ChromaDB 存储格式不兼容（{_e}），清空目录重建…")
        _shutil.rmtree(CHROMA_DB_DIR, ignore_errors=True)
        os.makedirs(CHROMA_DB_DIR, exist_ok=True)
        chroma_client = chromadb.PersistentClient(path=CHROMA_DB_DIR)

    try:
        collection = chroma_client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=embedding_func,
            metadata={"hnsw:space": "cosine"},
        )
        # 用 dummy query 触发 HNSW 文件加载，尽早暴露索引损坏
        # count() 只查 SQLite，无法检测 HNSW 文件缺失/损坏
        if collection.count() > 0:
            _dummy = embedding_func(["test"])
            collection.query(query_embeddings=_dummy, n_results=1)
    except Exception as _e:
        print(f"[警告] ChromaDB 索引损坏（{_e}），自动重建集合…")
        try:
            chroma_client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass
        collection = chroma_client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=embedding_func,
            metadata={"hnsw:space": "cosine"},
        )

    # 3. LLM 客户端（主备降级）
    if MINIMAX_API_KEY:
        _primary  = OpenAI(api_key=MINIMAX_API_KEY, base_url=MINIMAX_BASE_URL)
        _fallback = OpenAI(api_key=LLM_API_KEY,     base_url=LLM_BASE_URL)
        llm_client = FallbackLLMClient(_primary, MINIMAX_MODEL, _fallback, LLM_MODEL)
        label = f"MiniMax({MINIMAX_MODEL}) → fallback: {LLM_MODEL}"
    else:
        llm_client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)
        label = LLM_MODEL

    # 4. 将所有单例存入 app.state，供路由通过 Depends(get_state) 获取
    app.state.app_state = AppState(
        embedding_func=embedding_func,
        chroma_client=chroma_client,
        collection=collection,
        llm_client=llm_client,
        active_model_label=label,
    )
    app.state.llm_model   = LLM_MODEL
    app.state.data_dir    = os.path.join(_ROOT, "data")
    app.state.bom_default = os.path.join(_ROOT, "data", "test_bom.xlsx")
    app.state.neo4j_cfg   = {
        "uri":  os.getenv("NEO4J_URI",  "bolt://localhost:7687"),
        "user": os.getenv("NEO4J_USER", "neo4j"),
        "pass": os.getenv("NEO4J_PASS", "password"),
    }

    count = collection.count()
    print(f"[backend] 初始化完成，知识库共 {count} 条文档块。LLM: {label}")

    # 兜底机制：若 collection 为空（通常因 HNSW 损坏被自动重建）
    # 且 data/ 目录存在可入库文件，则在后台线程自动触发重建入库。
    # 入库在独立线程执行，不阻塞服务启动，接口立即可用。
    if count == 0:
        import glob as _glob
        import threading as _threading
        from backend.routers.ingest import _run_ingest as _bg_run_ingest

        _data_dir = app.state.data_dir
        _exts = ('.md', '.txt', '.pdf', '.docx')
        _files = [
            f for f in _glob.glob(os.path.join(_data_dir, "**", "*"), recursive=True)
            if os.path.isfile(f) and f.lower().endswith(_exts)
        ]
        if _files:
            _state_ref = app.state.app_state  # 绑定引用，避免闭包捕获问题
            print(f"[backend] 知识库为空，检测到 {len(_files)} 个文件，后台自动入库中…")

            def _bg_ingest():
                try:
                    for _ in _bg_run_ingest(_state_ref, _data_dir, False):
                        pass  # 消费生成器（yield 的是日志字符串，后台无需展示）
                    print(f"[backend] 后台入库完成，共 {_state_ref.collection.count()} 条文档块。")
                except Exception as _e:
                    print(f"[backend] 后台入库失败：{_e}")

            _threading.Thread(target=_bg_ingest, daemon=True).start()

    yield  # ← 此处 uvicorn 开始接受请求

    # 关闭：释放 Neo4j 连接
    state = app.state.app_state
    if state.neo4j_driver is not None:
        try:
            state.neo4j_driver.close()
        except Exception:
            pass
    print("[backend] 已关闭。")


# ==========================================
# FastAPI 应用实例
# ==========================================
app = FastAPI(
    title="RAG + BOM 装配系统 API",
    description="本地 RAG 知识库 + Neo4j BOM 图谱的 FastAPI 后端",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS：允许 React 开发服务器（localhost:3000）跨域调用
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 注册路由
# ==========================================
from backend.routers import ingest, retrieve, chat, eval as eval_router, bom, assembly  # noqa: E402

app.include_router(ingest.router,       tags=["知识库"])
app.include_router(retrieve.router,     tags=["检索"])
app.include_router(chat.router,         tags=["问答"])
app.include_router(eval_router.router,  tags=["评估"])
app.include_router(bom.router,          tags=["BOM"])
app.include_router(assembly.router,     tags=["装配"])


# ==========================================
# 健康检查
# ==========================================
@app.get("/health", summary="健康检查")
def health(request: Request):
    state = request.app.state.app_state
    return {
        "status": "ok",
        "collection_count": state.collection.count(),
        "model": state.active_model_label,
    }
