"""
backend/main.py — FastAPI 应用入口

职责：
  1. lifespan：启动时初始化所有全局单例（Embedding、Qdrant、LLM、Chinese-CLIP），关闭时清理
  2. 注册所有 Router（/ingest、/retrieve、/chat、/eval、/bom、/assembly、/vision）
  3. 配置 CORS（允许 React 开发服务器 localhost:3000）
  4. 挂载 /images 静态文件服务（用于访问知识库中提取的图片）
  5. 提供 GET /health 健康检查接口

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
from fastapi.staticfiles import StaticFiles

# 加载环境变量（.env 文件）
load_dotenv()

# 将项目根目录加入 sys.path，使 document_processing/ shim 模块可以被 main_ingest 找到
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "document_processing"))

# ==========================================
# 配置常量（从 .env 读取）
# ==========================================
QDRANT_DB_PATH     = os.path.join(_ROOT, "storage", "qdrant.db")
IMAGE_STORAGE_DIR  = os.path.join(_ROOT, "storage", "images")
COLLECTION_NAME    = "rag_knowledge"
EMBEDDING_MODEL    = "BAAI/bge-m3"
CLIP_MODEL         = "OFA-Sys/chinese-clip-vit-large-patch14"

LLM_API_KEY        = os.getenv("LLM_API_KEY")
LLM_BASE_URL       = os.getenv("LLM_BASE_URL",   "https://api.siliconflow.cn/v1")
LLM_MODEL          = os.getenv("LLM_MODEL",       "Qwen/Qwen2.5-14B-Instruct")
MINIMAX_API_KEY    = os.getenv("MINIMAX_API_KEY", "").strip()
MINIMAX_BASE_URL   = os.getenv("MINIMAX_BASE_URL","https://api.minimaxi.com/v1")
MINIMAX_MODEL      = os.getenv("MINIMAX_MODEL",   "MiniMax-M2.5")


def _init_qdrant(db_path: str, collection_name: str, clip_dim: int = 768):
    """
    初始化 Qdrant 本地文件客户端，创建 Collection（如不存在）。
    使用命名多向量：
      text_vec  — bge-m3 1024维，余弦相似度（文本检索）
      image_vec — Chinese-CLIP clip_dim维（默认768），余弦相似度（图片检索）
    Payload 字段（无需预先定义 Schema）：
      text、source、page、chunk_type、image_path、doc_id、chunk_index
    """
    from qdrant_client import QdrantClient
    from qdrant_client.models import VectorParams, Distance

    os.makedirs(db_path, exist_ok=True)
    client = QdrantClient(path=db_path)

    if not client.collection_exists(collection_name):
        print(f"[backend] 创建 Qdrant Collection: {collection_name}（text_vec=1024, image_vec={clip_dim}）")
        client.create_collection(
            collection_name=collection_name,
            vectors_config={
                "text_vec":  VectorParams(size=1024, distance=Distance.COSINE),
                "image_vec": VectorParams(size=clip_dim, distance=Distance.COSINE),
            },
        )
        print(f"[backend] Qdrant Collection 创建完成。")
    else:
        # 检查已有 collection 的 image_vec 维度是否匹配
        try:
            info = client.get_collection(collection_name)
            existing_dim = info.config.params.vectors["image_vec"].size
            if existing_dim != clip_dim:
                print(f"[backend] ⚠️ 已有 Collection 的 image_vec 维度为 {existing_dim}，"
                      f"当前模型需要 {clip_dim}。请执行 --clear 重建索引！")
        except Exception:
            pass
        print(f"[backend] Qdrant Collection 已存在（{collection_name}），直接使用。")

    return client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan：yield 前为启动逻辑，yield 后为关闭逻辑。
    uvicorn 在 lifespan 完成前不接受任何请求，保证初始化完成后才上线。
    """
    from openai import OpenAI
    from backend.state import AppState, FallbackLLMClient
    from backend.embedding_manager import EmbeddingManager

    print("[backend] 正在初始化，请稍候…")

    # 1. Embedding 模型：bge-m3（文本）+ Chinese-CLIP（图文）
    print(f"[backend] 加载 Embedding 模型：{EMBEDDING_MODEL} + {CLIP_MODEL}")
    embedding_mgr = EmbeddingManager(EMBEDDING_MODEL, CLIP_MODEL)
    print("[backend] Embedding 模型加载完成。")

    # 2. Qdrant 本地文件初始化（image_vec 维度从 EmbeddingManager 自动获取）
    os.makedirs(IMAGE_STORAGE_DIR, exist_ok=True)
    qdrant_client = _init_qdrant(QDRANT_DB_PATH, COLLECTION_NAME, embedding_mgr.clip_dim)

    # 3. Reranker（CrossEncoder，约 280MB，失败则降级为距离排序）
    reranker = None
    try:
        from sentence_transformers import CrossEncoder
        print("[backend] 正在加载 Reranker 模型 BAAI/bge-reranker-base…")
        reranker = CrossEncoder("BAAI/bge-reranker-base")
        print("[backend] Reranker 加载成功。")
    except Exception as _re:
        print(f"[backend] ⚠️ Reranker 加载失败（{_re}），将降级为距离排序。")

    # 4. LLM 客户端（主备降级）
    minimax_client = None
    if MINIMAX_API_KEY:
        _primary  = OpenAI(api_key=MINIMAX_API_KEY, base_url=MINIMAX_BASE_URL)
        _fallback = OpenAI(api_key=LLM_API_KEY,     base_url=LLM_BASE_URL)
        llm_client = FallbackLLMClient(_primary, MINIMAX_MODEL, _fallback, LLM_MODEL)
        minimax_client = _primary  # Vision API 专用，直接使用 MiniMax 原始 client
        label = f"MiniMax({MINIMAX_MODEL}) → fallback: {LLM_MODEL}"
    else:
        llm_client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)
        label = LLM_MODEL

    if minimax_client is None:
        print("[backend] ⚠️ 未配置 MINIMAX_API_KEY，图片 Caption 生成功能不可用。")

    # 5. 将所有单例存入 app.state，供路由通过 Depends(get_state) 获取
    app.state.app_state = AppState(
        qdrant_client=qdrant_client,
        embedding_mgr=embedding_mgr,
        llm_client=llm_client,
        active_model_label=label,
        minimax_client=minimax_client,
        minimax_model=MINIMAX_MODEL,
        reranker=reranker,
    )
    app.state.llm_model      = LLM_MODEL
    app.state.data_dir       = os.path.join(_ROOT, "data")
    app.state.image_dir      = IMAGE_STORAGE_DIR
    app.state.collection_name = COLLECTION_NAME
    app.state.bom_default    = os.path.join(_ROOT, "data", "test_bom.xlsx")
    app.state.neo4j_cfg      = {
        "uri":  os.getenv("NEO4J_URI",  "bolt://localhost:7687"),
        "user": os.getenv("NEO4J_USER", "neo4j"),
        "pass": os.getenv("NEO4J_PASS", "password"),
    }

    # 6. LangChain 组件初始化（渐进式，不影响原有功能）
    try:
        from backend.langchain_components.models import build_chat_model
        from backend.langchain_components.retrievers import QdrantDualPathRetriever
        from backend.langchain_components.memory import ChatMemoryManager

        lc_chat_model = build_chat_model()
        lc_retriever = QdrantDualPathRetriever(
            qdrant_client=qdrant_client,
            embedding_mgr=embedding_mgr,
            reranker=reranker,
            collection_name=COLLECTION_NAME,
        )
        lc_memory_manager = ChatMemoryManager(window_k=6)

        app.state.app_state.lc_chat_model = lc_chat_model
        app.state.app_state.lc_retriever = lc_retriever
        app.state.app_state.lc_memory_manager = lc_memory_manager
        print("[backend] LangChain 基础组件初始化完成（Models + Retriever + Memory）。")

        # Agent + Tools（需要 neo4j_cfg，在 app.state 设置之后初始化）
        try:
            from backend.langchain_components.tools import create_tools
            from backend.langchain_components.agents import build_rag_agent

            lc_tools = create_tools(app.state.app_state, app.state.neo4j_cfg)
            lc_agent = build_rag_agent(lc_chat_model, lc_tools)
            app.state.app_state.lc_agent = lc_agent
            print(f"[backend] LangChain Agent 初始化完成（{len(lc_tools)} 个工具）。")
        except Exception as _agent_err:
            print(f"[backend] LangChain Agent 初始化失败（{_agent_err}），Agent 模式不可用。")

    except Exception as _lc_err:
        print(f"[backend] LangChain 组件初始化失败（{_lc_err}），降级为原生模式。")

    count = app.state.app_state.get_doc_count()
    print(f"[backend] 初始化完成，知识库共 {count} 条文档块。LLM: {label}")

    # 兜底：若 Qdrant 为空且 data/ 目录有文件，后台自动触发入库
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
            _state_ref = app.state.app_state
            print(f"[backend] 知识库为空，检测到 {len(_files)} 个文件，后台自动入库中…")

            def _bg_ingest():
                # 后台自动入库：临时禁用 Vision（避免 API 调用拖慢启动）
                # 图片块使用页面上下文文字做降级 Caption + CLIP 向量，仍可检索和显示
                orig_minimax = _state_ref.minimax_client
                _state_ref.minimax_client = None
                try:
                    for _ in _bg_run_ingest(_state_ref, _data_dir, False):
                        pass
                    print(f"[backend] 后台入库完成（图片用降级 Caption），共 {_state_ref.get_doc_count()} 条文档块。")
                except Exception as _e:
                    print(f"[backend] 后台入库失败：{_e}")
                finally:
                    _state_ref.minimax_client = orig_minimax

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
    title="RAG + BOM 装配系统 API（图文检索版）",
    description="本地 RAG 知识库（Qdrant + bge-m3 + Chinese-CLIP）+ Neo4j BOM 图谱的 FastAPI 后端",
    version="2.0.0",
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

# 图片静态文件服务：/images/{filename} → storage/images/{filename}
_image_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                          "storage", "images")
os.makedirs(_image_dir, exist_ok=True)
app.mount("/images", StaticFiles(directory=_image_dir), name="images")

# ==========================================
# 注册路由
# ==========================================
from backend.routers import (  # noqa: E402
    ingest, retrieve, chat, eval as eval_router, bom, assembly, vision
)

app.include_router(ingest.router,       tags=["知识库"])
app.include_router(retrieve.router,     tags=["检索"])
app.include_router(chat.router,         tags=["问答"])
app.include_router(eval_router.router,  tags=["评估"])
app.include_router(bom.router,          tags=["BOM"])
app.include_router(assembly.router,     tags=["装配"])
app.include_router(vision.router,       tags=["视觉"])


# ==========================================
# 健康检查
# ==========================================
@app.get("/health", summary="健康检查")
def health(request: Request):
    state = request.app.state.app_state
    return {
        "status": "ok",
        "collection_count": state.get_doc_count(),
        "model": state.active_model_label,
        "vision_enabled": state.minimax_client is not None,
    }
