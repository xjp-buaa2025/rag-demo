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
MINIMAX_API_KEY        = os.getenv("MINIMAX_API_KEY", "").strip()
MINIMAX_BASE_URL       = os.getenv("MINIMAX_BASE_URL","https://api.minimaxi.com/v1")
MINIMAX_MODEL          = os.getenv("MINIMAX_MODEL",   "MiniMax-M2.5")
# Vision 专用 Key：图片入库 Caption 使用付费 Token，与对话 LLM 隔离
MINIMAX_VISION_API_KEY = os.getenv("MINIMAX_VISION_API_KEY", "").strip() or MINIMAX_API_KEY
VISION_API_KEY  = os.getenv("VISION_API_KEY",  "").strip()
VISION_BASE_URL = os.getenv("VISION_BASE_URL", LLM_BASE_URL)
VISION_MODEL    = os.getenv("VISION_MODEL",    "Qwen/Qwen3-VL-8B-Instruct")


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
    minimax_model  = MINIMAX_MODEL
    if MINIMAX_API_KEY:
        _primary  = OpenAI(api_key=MINIMAX_API_KEY, base_url=MINIMAX_BASE_URL)
        _fallback = OpenAI(api_key=LLM_API_KEY,     base_url=LLM_BASE_URL)
        llm_client = FallbackLLMClient(_primary, MINIMAX_MODEL, _fallback, LLM_MODEL)
        label = f"MiniMax({MINIMAX_MODEL}) → fallback: {LLM_MODEL}"
    else:
        llm_client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)
        label = LLM_MODEL

    # Vision 专用 client：优先用 VISION_* 配置（SiliconFlow Qwen-VL，支持 data URI inline base64）
    # 回退到 MINIMAX_VISION_API_KEY；两者都没有则 Vision 不可用
    _vision_key = VISION_API_KEY or MINIMAX_VISION_API_KEY
    _vision_url = VISION_BASE_URL if VISION_API_KEY else MINIMAX_BASE_URL
    _vision_mdl = VISION_MODEL    if VISION_API_KEY else MINIMAX_MODEL
    if _vision_key:
        minimax_client = OpenAI(api_key=_vision_key, base_url=_vision_url)
        minimax_model  = _vision_mdl
        print(f"[backend] Vision client: {_vision_mdl} @ {_vision_url}")
    else:
        print("[backend] ⚠️ 未配置 Vision Key，图片描述功能不可用。")

    # 5. 将所有单例存入 app.state，供路由通过 Depends(get_state) 获取
    app.state.app_state = AppState(
        qdrant_client=qdrant_client,
        embedding_mgr=embedding_mgr,
        llm_client=llm_client,
        active_model_label=label,
        minimax_client=minimax_client,
        minimax_model=minimax_model,
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

    # 7. deepdoc AI 解析引擎初始化（PDF 精细化处理，首次运行下载 ONNX 模型）
    try:
        from backend.pipelines.deepdoc_wrapper import DeepDocEngine
        _state = app.state.app_state
        _state.deepdoc_engine = DeepDocEngine()
        print("[backend] deepdoc AI 解析引擎初始化完成（LayoutRecognizer + OCR + TSR 就绪）。")
    except Exception as _dd_err:
        print(f"[backend] deepdoc 初始化失败（{_dd_err}），PDF 精细化处理不可用，将回退基础路径。")

    # 8. LangGraph 管道初始化（渐进式，不影响原有功能）
    try:
        from backend.pipelines.factory import make_rag_pipeline, make_bom_pipeline, make_cad_pipeline
        _state = app.state.app_state
        _neo4j_cfg = app.state.neo4j_cfg

        _state.lg_rag_pipeline = make_rag_pipeline(_state, IMAGE_STORAGE_DIR, _neo4j_cfg)
        _state.lg_bom_pipeline = make_bom_pipeline(_state, _neo4j_cfg)
        try:
            _state.lg_cad_pipeline = make_cad_pipeline(_state, _neo4j_cfg)
            print("[backend] LangGraph 管道初始化完成（RAG + BOM + CAD 管道已就绪）。")
        except Exception as _cad_err:
            print(f"[backend] CAD 管道初始化失败（{_cad_err}），STEP 文件解析不可用。")
            print("[backend] LangGraph 管道初始化完成（RAG + BOM 管道已就绪）。")
    except Exception as _lg_err:
        print(f"[backend] LangGraph 管道初始化失败（{_lg_err}），管道模式不可用。")

    # 9. 联合 KG 构建管道 + 任务管理器初始化
    try:
        from backend.pipelines.factory import make_unified_kg_pipeline
        from backend.kg_task_manager import KGTaskManager
        _state = app.state.app_state
        _state.lg_kg_pipeline  = make_unified_kg_pipeline(_state, IMAGE_STORAGE_DIR, app.state.neo4j_cfg)
        _state.kg_task_manager = KGTaskManager(ttl_seconds=7200)
        print("[backend] 联合 KG 构建管道初始化完成（lg_kg_pipeline + KGTaskManager 已就绪）。")
    except Exception as _kg_err:
        print(f"[backend] 联合 KG 管道初始化失败（{_kg_err}），/kg 端点不可用。")

    # 10. BM25 索引初始化（混合检索支持）
    try:
        from backend.bm25_manager import BM25Manager
        _bm25_path = os.path.join(_ROOT, "storage", "bm25_index.pkl")
        _bm25_mgr = BM25Manager(index_path=_bm25_path)
        if not _bm25_mgr.has_index():
            _qdrant_count = app.state.app_state.get_doc_count()
            if _qdrant_count > 0:
                print(f"[backend] BM25 索引不存在，从 Qdrant 重建（约 {_qdrant_count} 个块）…")
                _rebuilt = _bm25_mgr.rebuild_from_qdrant(qdrant_client, COLLECTION_NAME)
                print(f"[backend] BM25 索引重建完成，共 {_rebuilt} 个文本块。")
            else:
                print("[backend] 知识库为空，BM25 索引待入库后自动更新。")
        else:
            print(f"[backend] BM25 索引已加载（{_bm25_mgr.doc_count()} 个文档）。")
        app.state.app_state.bm25_manager = _bm25_mgr
        # 将 bm25_manager 注入已初始化的 LangChain Retriever
        if app.state.app_state.lc_retriever is not None:
            app.state.app_state.lc_retriever.bm25_manager = _bm25_mgr
    except Exception as _bm25_err:
        print(f"[backend] BM25 初始化失败（{_bm25_err}），混合检索降级为纯 Dense。")

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
from backend.routers import kg as _kg_router  # noqa: E402

app.include_router(ingest.router,        tags=["知识库"])
app.include_router(retrieve.router,      tags=["检索"])
app.include_router(chat.router,          tags=["问答"])
app.include_router(eval_router.router,   tags=["评估"])
app.include_router(bom.router,           tags=["BOM"])
app.include_router(assembly.router,      tags=["装配"])
app.include_router(vision.router,        tags=["视觉"])
app.include_router(_kg_router.router,    prefix="/kg", tags=["KG联合构建"])


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
