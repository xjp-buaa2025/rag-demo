# RAG Demo 项目完全指南

> 随代码同步维护。每次新增/修改功能后同步更新对应章节。

---

## 目录

1. [项目整体目标](#1-项目整体目标)
2. [技术选型总览](#2-技术选型总览)
3. [架构总览](#3-架构总览)
4. [数据流全景](#4-数据流全景)
5. [文件结构说明](#5-文件结构说明)
6. [后端代码详解](#6-后端代码详解)
7. [LangChain 集成详解](#7-langchain-集成详解)
8. [图文检索详解](#8-图文检索详解)
9. [BOM-GraphRAG 扩展](#9-bom-graphrag-扩展)
10. [LangGraph 多步骤管道](#10-langgraph-多步骤管道)
11. [React 前端详解](#11-react-前端详解)
12. [配置系统（.env）](#12-配置系统env)
13. [运行方式](#13-运行方式)
14. [常见问题与排查](#14-常见问题与排查)
15. [变更日志](#15-变更日志)
16. [Assembly Scheme Skill (Plan 1, v0)](#16-assembly-scheme-skill-plan-1-v0)

---

## 1. 项目整体目标

构建一个**完全本地化**的**图文多模态 RAG** 问答系统，能回答"知识库里有但大模型不知道"的内容。

核心能力：
- **文字查文档**：传统 RAG，bge-m3 向量检索 + BM25 混合检索
- **文字查图片**：输入文字描述，召回 PDF 中相关图片（Chinese-CLIP）
- **以图搜文**：上传图片 → Vision LLM 生成描述 → bge-m3 文字检索
- **BOM 装配问答**：Neo4j 零件图谱 + 技术知识库双路融合
- **知识图谱提取**：LLM 从文本自动抽取实体/关系写入 Neo4j
- **CAD 装配解析**：STEP 文件 → Open CASCADE → 装配树/约束/邻接写入 Neo4j
- **Embedding 完全本地**：不调用任何外部 Embedding API

---

## 2. 技术选型总览

| 组件 | 选型 | 说明 |
|------|------|------|
| 向量数据库 | **Qdrant**（本地文件模式） | `storage/qdrant.db/`，无需 Docker |
| 文本 Embedding | **BAAI/bge-m3**（1024维） | 本地推理，中英文均优秀 |
| 图片 Embedding | **OFA-Sys/chinese-clip-vit-large-patch14**（768维） | 中文 CLIP，图文跨模态 |
| 稀疏检索 | **rank_bm25 + jieba** | BM25Okapi，双轨分词（中文 jieba + 英文/编码 regex），RRF 融合 |
| Reranker | **BAAI/bge-reranker-base** | CrossEncoder 精排，约 280MB |
| 图片 Caption | **MiniMax M2.5 Vision** | PDF 图片 → 中文描述，入库时调用 |
| LLM（主） | MiniMax M2.5（远程 API） | 支持 Vision；failover 到 SiliconFlow |
| LLM（备） | SiliconFlow / vLLM | OpenAI 兼容，Qwen2.5-14B 等 |
| 图谱数据库 | **Neo4j** | BOM 零件树 + 知识图谱，Cypher 递归查询 |
| 后端框架 | **FastAPI** + uvicorn | SSE 流式响应 |
| 前端框架 | **React 18 + TypeScript + Vite** | Tailwind CSS v4，POST SSE |
| PDF 解析 | **MinerU CLI**（方案A）+ **RAGFlow deepdoc**（方案B） | 双轨：方案A独立批量转Markdown（DocLayout-YOLO+PaddleOCR+UniMERNet公式）；方案B在入库管道中实时处理（YOLOv10布局+ONNX表格→HTML+PaddleOCR），大PDF自动分批50页防OOM。技术手册/图表优选方案B；含LaTeX公式的学术PDF优选方案A |
| CAD 解析 | **pythonocc-core**（Open CASCADE） | STEP 文件装配树 / 约束 / 空间邻接 |

---

## 3. 架构总览

```
┌────────────────────────────────────────────────────────────────┐
│  React 前端（:5173）                                            │
│  RAG问答 / 图片上传 / 知识库管理 / 评估 / BOM装配方案          │
└───────────────────────┬────────────────────────────────────────┘
                        │ POST SSE / JSON（/api/* → Vite代理）
┌───────────────────────▼────────────────────────────────────────┐
│  FastAPI 后端（:8000）                                          │
│  ├─ /ingest            文档入库（双向量，SSE 进度流）           │
│  ├─ /ingest/pipeline   LangGraph 精细化入库管道（SSE）          │
│  ├─ /retrieve          向量检索（双路图文，JSON）               │
│  ├─ /chat              RAG 问答（多查询+双路+重排序，SSE）      │
│  ├─ /eval/*            RAG 评估（诊断/RAGAS/LLM打分，SSE）     │
│  ├─ /bom/*             BOM 入库 + Neo4j 查询                   │
│  ├─ /bom/kg/graph      知识图谱可视化数据（JSON，D3 用）        │
│  ├─ /bom/ingest/pipeline  LangGraph BOM 管道（SSE）            │
│  ├─ /assembly/chat     BOM+知识库融合问答（SSE）               │
│  ├─ /vision/*          图片描述 + 以图搜图                     │
│  └─ /images/*          图片静态文件服务（storage/images/）     │
├────────────────────────────────────────────────────────────────┤
│  核心组件层                                                     │
│  EmbeddingManager（bge-m3 + Chinese-CLIP）                     │
│  BM25Manager（rank_bm25 + jieba，稀疏检索索引）                │
│  FallbackLLMClient（MiniMax → SiliconFlow 自动降级）           │
│  ImageCaptioner（MiniMax Vision，图片→中文描述）               │
│  CrossEncoder Reranker（BAAI/bge-reranker-base）               │
├────────────────────────────────────────────────────────────────┤
│  存储层                                                         │
│  Qdrant（storage/qdrant.db/）— 双向量文本+图片                 │
│  BM25 索引（storage/bm25_index.pkl）— 稀疏检索（pickle）       │
│  Neo4j（Docker）— BOM 零件树 + 知识图谱                        │
│  storage/images/ — 提取的 PDF 图片文件                         │
└────────────────────────────────────────────────────────────────┘
```

---

## 4. 数据流全景

### 4.1 知识库入库（离线）

```
data/*.pdf
    ↓ [PyMuPDF] 文本提取 → 按句子边界切块（500字/块）
    ↓ [PyMuPDF] page.get_images() → 过滤小图（<100×100）→ 保存 storage/images/
    ↓ [bge-m3] 文本块向量化 → text_vec（1024维）
    ↓ [MiniMax Vision] 图片 → 中文 Caption
    ↓ [bge-m3] Caption 向量化 → 图片块 text_vec
    ↓ [Chinese-CLIP] 图片 → image_vec（768维）
    ↓ Qdrant upsert → 双向量存储

/ingest/pipeline 路径（deepdoc 精细化，推荐 PDF）：
    ↓ detect_input → analyze_pdf_type → deepdoc_parse_pdf
    ↓ extract_structure（ATA章节） → semantic_chunk → extract_figures
    ↓ generate_tech_captions → encode_text_vectors → upsert_qdrant
```

### 4.2 问答检索（实时）

```
用户输入文字问题
    ↓ [LLM] 生成2个额外查询角度（多查询召回）
    ↓ 对每个查询执行混合检索（hybrid_search_text）：
       ├─ Dense：[bge-m3] → Qdrant text_vec（Top-N）
       └─ BM25：[jieba+regex 分词] → BM25Manager（Top-2N）→ RRF(k=60) 融合
    ↓ merge_and_dedup → [Chinese-CLIP] → Qdrant image_vec（Top-N/2，仅图片块）
    ↓ [CrossEncoder] 精排 → Top-4
    ↓ 拼接 Prompt → LLM 流式生成回答
    ↓ SSE：stage帧（阶段提示）→ delta帧（增量）→ done帧（sources_md + image_urls）
```

---

## 5. 文件结构说明

```
rag-demo/
├── main_ingest.py            # CLI 入库工具（Qdrant 双向量，支持 --clear）
├── bom_ingest.py             # BOM Excel → Neo4j 零件图谱
├── start.sh                  # 一键启动脚本（后端 + 前端）
├── requirements.txt
├── .env                      # 密钥配置（不提交 git）
│
├── data/                     # 原始文档（.pdf .md .txt）
│
├── storage/
│   ├── qdrant.db/            # Qdrant 本地文件数据库（目录，非文件）
│   ├── bm25_index.pkl        # BM25 稀疏检索索引（pickle，重启自动恢复）
│   └── images/               # PDF 提取的图片文件（/images/* 静态服务）
│
├── backend/
│   ├── main.py               # 应用入口：lifespan 初始化 + 路由注册
│   ├── state.py              # AppState dataclass + FallbackLLMClient
│   ├── bm25_manager.py       # BM25Manager（稀疏检索索引）
│   ├── embedding_manager.py  # EmbeddingManager（bge-m3 + Chinese-CLIP）
│   ├── image_captioner.py    # MiniMax Vision 图片描述
│   ├── deps.py               # FastAPI Depends（get_state / get_neo4j_cfg）
│   ├── sse.py                # 生成器 → SSE 响应适配
│   ├── langchain_components/ # LangChain 7 大组件集成层
│   │   ├── models.py         # FallbackChatModel（主备降级）
│   │   ├── prompts.py        # 所有 ChatPromptTemplate 统一管理
│   │   ├── chains.py         # LCEL 工作流（rag/multi_query/assembly/judge）
│   │   ├── memory.py         # ChatMemoryManager（滑动窗口对话历史）
│   │   ├── tools.py          # 5 个工具（rag_search/bom_query/vision/image_search/calculator）
│   │   ├── agents.py         # RAG Agent（动态选择工具）
│   │   └── retrievers.py     # QdrantDualPathRetriever（双路检索+重排）
│   ├── pipelines/
│   │   ├── state.py          # PipelineState TypedDict
│   │   ├── factory.py        # make_rag_pipeline() / make_bom_pipeline() 工厂
│   │   ├── deepdoc_wrapper.py# DeepDocEngine：封装 RAGFlowPdfParser
│   │   ├── nodes_manual.py   # 7 个 deepdoc 精细化节点（PDF AI 解析）
│   │   ├── nodes_rag.py      # RAG 节点（encode_text_vectors / encode_image_vectors）
│   │   ├── nodes_bom.py      # BOM 5 个节点函数
│   │   ├── nodes_cad.py      # CAD 2 个节点（parse_cad_step / cad_to_kg_triples）
│   │   ├── nodes_kg.py       # KG 4 个节点（extract_kg_triples / align_entities / validate_kg_dag / write_kg_neo4j）
│   │   ├── nodes_common.py   # 公共节点工具
│   │   ├── routes.py         # 条件路由函数
│   │   └── sse_bridge.py     # LangGraph stream → SSE 适配
│   └── routers/
│       ├── ingest.py         # POST /ingest（SSE），GET /ingest/status
│       ├── retrieve.py       # POST /retrieve（双路检索，JSON）
│       ├── chat.py           # POST /chat（多查询+双路+重排，SSE）
│       ├── eval.py           # POST /eval/*（6种评估，SSE）
│       ├── bom.py            # POST /bom/ingest（SSE），POST /bom/query
│       ├── assembly.py       # POST /assembly/chat（SSE），/assembly/agent
│       └── vision.py         # POST /vision/describe，/vision/search
│
├── frontend/
│   └── src/
│       ├── App.tsx
│       ├── types/index.ts    # TypeScript 类型定义（含 SseStageFrame）
│       ├── api/client.ts     # 所有后端 API 调用封装
│       ├── hooks/
│       │   ├── usePostSSE.ts # 日志类 SSE hook
│       │   └── useChat.ts    # 聊天类 SSE hook（含 imageUrls / currentStage）
│       └── components/
│           ├── rag/          # KnowledgePanel / EvalPanel
│           ├── bom/          # Neo4jStatus / BomIngest（旧，已保留供兼容）
│           ├── kg/           # KgBuilder（图谱构建）/ KgViewer（D3 可视化）
│           └── shared/       # UnifiedChat（合并聊天）/ SourceCard
│
└── document_processing/      # deepdoc 解析引擎（RAGFlow 抽离，不修改）
    ├── common/               # shim：file_utils / misc_utils / settings / token_utils
    ├── rag/                  # shim：nlp（find_codec + rag_tokenizer）/ prompts / utils/lazy_image
    └── deepdoc/              # TxtParser / MarkdownParser / RAGFlowPdfParser 等
```

---

## 6. 后端代码详解

### 6.1 `backend/main.py` — lifespan 初始化顺序

1. `EmbeddingManager` 加载（bge-m3 + Chinese-CLIP，首次需下载）
2. `_init_qdrant` — 创建/打开本地 Qdrant，Named Multi-Vector：`text_vec`(1024) + `image_vec`(768)
3. `CrossEncoder("BAAI/bge-reranker-base")` — 失败时降级为按余弦排序
4. `FallbackLLMClient` 配置（MINIMAX 为主 → SiliconFlow 备用）
5. 构造 `AppState` 注入 `app.state.app_state`
6. LangChain 组件初始化（`FallbackChatModel` + `QdrantDualPathRetriever` + `ChatMemoryManager` + Agent）
7. deepdoc `DeepDocEngine` 初始化（失败降级 None）
8. LangGraph 管道构建（RAG（含 KG 链）+ BOM + CAD）
9. BM25 索引：加载 `storage/bm25_index.pkl`；不存在则从 Qdrant scroll 全量重建，完成后注入 `lc_retriever.bm25_manager`
10. 兜底自动入库：若 Qdrant 为空且 `data/` 有文件，后台线程触发入库

### 6.2 `backend/state.py` — 全局状态

```python
@dataclass
class AppState:
    qdrant_client: Any              # QdrantClient（本地文件 storage/qdrant.db/）
    embedding_mgr: Any              # EmbeddingManager（bge-m3 + Chinese-CLIP）
    llm_client: Any                 # FallbackLLMClient
    active_model_label: str         # 显示用标签
    minimax_client: Optional[Any]   # Vision 专用原始 MiniMax 客户端
    minimax_model: str
    reranker: Optional[Any]         # CrossEncoder，None 则按 score 排序
    bm25_manager: Optional[Any]     # BM25Manager，None 时降级纯 Dense
    neo4j_driver: Optional[Any]
    lc_chat_model / lc_retriever / lc_memory_manager / lc_agent  # LangChain 四组件
    lg_rag_pipeline / lg_bom_pipeline / lg_cad_pipeline          # LangGraph 三管道
    deepdoc_engine: Optional[Any]   # DeepDocEngine（PDF 精细化）
    is_ingesting: bool
    collection_lock / neo4j_lock: Lock
    _ingest_progress_q: Optional[Any]  # Queue 侧信道，deepdoc 批次进度→SSE
```

`FallbackLLMClient`：包装主/备两个 OpenAI 兼容客户端，接口与 `openai.OpenAI` 完全相同。Vision 调用必须直接使用 `minimax_client`（SiliconFlow 不支持多模态）。

### 6.3 `backend/embedding_manager.py` — 双模型管理

```python
class EmbeddingManager:
    clip_dim: int                                    # 从模型 config.projection_dim 自动检测（768）
    encode_text(texts) → np.ndarray(N, 1024)         # bge-m3，L2 normalize
    encode_texts_clip(texts) → np.ndarray(N, 768)    # Chinese-CLIP 文本编码
    encode_images_clip(images) → np.ndarray(N, 768)  # Chinese-CLIP 图片编码
    zero_image_vec() → List[float]                   # [0.0]*768，文本块占位
```

### 6.4 `backend/sse.py` — SSE 协议

| 函数 | 帧格式 |
|------|--------|
| `log_gen_to_sse(gen)` | `{"log": "完整日志快照"}` / `[DONE]` |
| `chat_gen_to_sse(gen)` | `{"stage":"..."}` + `{"delta":"..."}` + `{"done":true,...}` |

生成器通过 `yield "__STAGE__:文字"` 特殊前缀触发 stage 帧；`_IMAGES_SEP`（`\n\n[__IMAGES__]`）协议在 done 帧中传递图片 URL 列表。

### 6.5 混合检索（`backend/routers/retrieve.py`）

```
hybrid_search_text(query, n):
  ├─ Dense:  bge-m3(query) → Qdrant text_vec → ranked_list_A（含 payload）
  └─ BM25:   jieba+regex(query) → BM25Manager → ranked_list_B（仅 id+score）
             ↓ reciprocal_rank_fusion(A, B, k=60)
             fused_candidates（以 A 的 payload 为基准）

qdrant_search_image(query, n):  # Chinese-CLIP 文本编码 → image_vec，仅图片块

merge_and_dedup → CrossEncoder 精排 → Top-K
```

BM25Manager 双轨分词：英文/编码（regex `[A-Za-z0-9][A-Za-z0-9\-/\.\:_]*`）+ 中文（jieba）；连字符子 token 扩展确保 `1234567` 能命中 `1234567-A`。BM25 任何故障自动降级为纯 Dense。

---

## 7. LangChain 集成详解

`backend/langchain_components/` — 设计原则：**渐进式替换**，LangChain 不可用时自动降级到原生 Python。

| 模块 | 核心类/函数 | 功能 |
|------|------------|------|
| `models.py` | `FallbackChatModel` | 自定义 BaseChatModel，`_generate()` + `_stream()` 支持 MiniMax→SiliconFlow 降级 |
| `prompts.py` | 12 个 ChatPromptTemplate | RAG_QA / MULTI_QUERY / JUDGE / ASSEMBLY / VISION_CAPTION / AGENT_SYSTEM / RAGAS_* |
| `chains.py` | LCEL 工作流 | `build_rag_chain()` / `build_multi_query_chain()` / `build_assembly_chain()` / `build_judge_chain()` |
| `memory.py` | `ChatMemoryManager` | 多会话历史，LRU 淘汰（上限100），`history_to_messages()` 格式转换 |
| `tools.py` | 6 个 `@tool` | rag_search / bom_query / **procedure_chain_query** / vision_describe / image_search / calculator（沙箱 eval） |
| `agents.py` | `build_rag_agent()` | OpenAI Tools Agent，`max_iterations=5`，用于 `/assembly/agent` |
| `retrievers.py` | `QdrantDualPathRetriever` | 自定义 BaseRetriever，封装双路检索+重排，`bm25_manager` 由 main.py 步骤9注入 |

路由中的双路径切换：检查 `state.lc_chat_model / lc_retriever / lc_memory_manager` 均非 None 才走 LangChain 路径，否则降级原生。

---

## 8. 图文检索详解

### 8.1 双向量设计

每个 Qdrant Point 存两个命名向量：

| 字段 | 模型 | 维度 | 文本块值 | 图片块值 |
|------|------|------|----------|----------|
| `text_vec` | bge-m3 | 1024 | 文本编码 | Caption 编码 |
| `image_vec` | Chinese-CLIP | 768 | `[0.0]*768` | 图片编码 |

### 8.2 以图搜文（前端驱动）

```
用户上传图片
    → POST /vision/describe → MiniMax Vision → 中文描述
    → 前端拼接：[图片内容：{description}] + 用户说明
    → POST /chat（走 bge-m3 文字检索，效果更稳定）
```

### 8.3 文字查图（自动）

每次 `/chat` 的双路检索自动包含 Chinese-CLIP 图片路径，`done` 帧携带 `image_urls`，前端回答下方展示缩略图。

### 8.4 `/vision/search` — 纯 CLIP 以图搜图

```
用户上传图片 → Chinese-CLIP 图片编码 → Qdrant image_vec（filter: chunk_type=="image"）
```

---

## 9. BOM-GraphRAG 扩展

### 9.1 Neo4j 图模型

```
(涡扇发动机:Assembly {part_id:"ENG-001"})
    └─[:CHILD_OF]─(高压涡轮模块:Assembly {part_id:"HPT-000"})
                       ├─[:CHILD_OF]─(涡轮盘:Part {material:"GH4169"})
                       └─[:CHILD_OF]─(涡轮叶片:Part {qty:80})
```

递归子树查询：`MATCH (n)-[:CHILD_OF*]->(root {part_id: "HPT-000"}) RETURN n`

### 9.2 BOM 支持的文件格式

| 格式 | 处理路径 |
|------|---------|
| `.xlsx / .csv` | 直接读取，需含标准列（level_code / part_id / part_name / category / qty 等） |
| `.pdf / .docx` | pdfplumber/python-docx 提取 → LLM 自动转标准 BOM JSON，大文档分段处理 |

### 9.3 Neo4j Docker 启动

```bash
docker run -d --name neo4j -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password neo4j:5-community
docker start neo4j   # 后续重启
# 可视化：http://localhost:7474
```

### 9.4 知识图谱 Schema（7 节点 × 9 关系）

在 BOM 基础层（`CHILD_OF`）之上叠加结构化装配知识图谱，全部通过 `MERGE` 幂等写入，原有 BOM 结构不受影响。

**7 类节点**

| 标签 | 核心属性（`kg_id` 为全局唯一 MD5） | 来源 |
|---|---|---|
| `Part`（已有） | `part_id`, `part_name`, `material`, `quantity` | BOM + CAD |
| `Assembly`（已有） | `part_id`, `part_name`, `level`, `function` | BOM + CAD |
| `Procedure` | `kg_id`, `kg_name`, `seq_no`, `ata_section`, `source_chunk_id` | 手册 LLM 抽取 |
| `Tool` | `kg_id`, `kg_name`, `tool_type` | 手册 LLM 抽取 |
| `Specification` | `kg_id`, `spec_type`, `spec_value`, `spec_unit` | 手册 LLM 抽取 |
| `Interface` | `kg_id`, `iface_type`, `description` | CAD 配合约束 |
| `GeoConstraint` | `kg_id`, `constraint_type`, `value` | CAD 几何约束 |

**9 类关系**

| 关系 | 语义 | 写入节点 |
|---|---|---|
| `isPartOf` | 装配层级（语义标准化 CHILD_OF） | CAD `parse_cad_step` + BOM |
| `precedes` | 工序 A 在工序 B 之前 | `extract_kg_triples` |
| `participatesIn` | 零件参与某工序 | `extract_kg_triples` |
| `requires` | 工序需要某工具 | `extract_kg_triples` |
| `specifiedBy` | 工序/接口受某规范约束 | `extract_kg_triples` |
| `matesWith` | 两零件存在配合关系 | CAD `cad_to_kg_triples` |
| `adjacentTo` | 两零件空间邻接（gap_mm < 2mm） | CAD `cad_to_kg_triples` |
| `hasInterface` | 零件拥有某配合接口 | CAD `cad_to_kg_triples` |
| `constrainedBy` | 接口受几何约束 | CAD `cad_to_kg_triples` |

**实体对齐三级级联**（`align_entities` 节点）：
1. **规则**（~70%）：`AVIATION_ABBREV` 词典展开（HPC→高压压气机, Stage-3→第3级, Nm→N·m 等 20 条）+ 精确匹配 BOM `part_name`
2. **模糊**（~20%）：`difflib.SequenceMatcher.ratio() >= 0.85` 自动绑定（Python 标准库，无新依赖）
3. **语义**（~9%）：`EmbeddingManager.encode_text` → `qdrant_client.query_points(using="text_vec")` → 反向匹配 BOM 零件名

**DAG 校验**（`validate_kg_dag` 节点）：Kahn 算法（`collections.deque`）检测 `precedes` 关系成环，自动移除环边并记录日志。

### 9.5 装配工序链查询（`_query_procedure_chain`）

`backend/routers/bom.py` 新增，供 `/assembly/chat` 和 `procedure_chain_query` Agent 工具调用。

**调用链**：
```
问题关键词（前20字）
  → Cypher：MATCH (p:Procedure) WHERE p.kg_name CONTAINS $kw
  → 沿 precedes 链扩展最多 5 跳，同时 OPTIONAL MATCH Tool / Specification
  → Python Kahn 拓扑排序（_topological_sort_kahn）
  → 格式化：
      【装配工序（有序）】
        步骤1：安装叶片  工具：专用工具  规范：50 N·m
        步骤2：拧紧螺栓  工具：扭矩扳手  规范：50±2 N·m
        ...
```

**注入优先级**（`_build_assembly_context_and_sources`）：
- `[1]` KG 有序工序链（`kg_procedure` 类型，优先级最高）
- `[2..N]` BOM 实体（Assembly/Part）
- `[N+1..]` RAG 文本块

### 9.5 KG 四阶段构建管道（kg_stages.py）

**What**：以独立 REST+SSE 端点取代 LangGraph 一体化管道，每阶段产物写 JSON 文件（可人工审查），最终统一同步至 Neo4j。

**Why**：避免 LangGraph 大图 OOM；阶段解耦便于局部重跑；中间 JSON 可供论文截图取证。

**阶段划分**

| 阶段 | 端点 | 来源 | 输出文件 |
|------|------|------|----------|
| Stage1 BOM | `POST /kg/stage1/bom` | BOM xlsx/csv/pdf | `stage1_bom_triples.json` |
| Stage2 Manual | `POST /kg/stage2/manual` | 维修手册 PDF/docx | `stage2_manual_triples.json` |
| Stage3 CAD | `POST /kg/stage3/cad` | STEP 文件 | `stage3_cad_triples.json` |
| Stage4 Validate | `POST /kg/stage4/validate` | 读已有 JSON | 报告（P/R/F1）|
| Sync Neo4j | `POST /kg/stages/sync-neo4j` | 读所有 JSON | Neo4j 写入 |

**How（调用链）**

```
上传文件 → _stage1/2/3_gen() → LLM/deepdoc/OCC 抽取
  → write_stage("bom/manual/cad", {entities, triples})
  → (sync-neo4j 时) postprocess_triples()
  → _write_all_stages_to_neo4j()
  → Neo4j MERGE
```

### 9.6 三元组后处理管道（kg_postprocess.py）

**What**：`backend/pipelines/kg_postprocess.py`，对外暴露 `postprocess_triples(triples, skip_ontology)` 单一函数。

**Why**：原始三元组约 690 条，含 ~15% 低置信、大量大小写重复、本体约束违反，直接写入 Neo4j 会污染图谱影响查询质量。

**How（四步流水线）**

1. **置信度过滤** `confidence >= 0.3`，BOM 不受影响（全为 1.0），手册过滤 44 条
2. **实体名称归一化** strip + 合并空格 + 统一中文标点，不改大小写（保留显示形式）
3. **本体约束校验** 按 `ONTOLOGY_RULES` 字典校验 head_type/tail_type，手册过滤 108 条；BOM/CAD 因类型信息不完整传 `skip_ontology=True` 跳过
4. **去重** 以 `(head.lower(), relation, tail.lower())` 为 key，同 key 保留最高置信度，BOM 去重 38 条

**验证结果（2026-04-13）**

| 阶段 | 原始 | 最终 | 清除率 |
|------|------|------|--------|
| BOM | 175 | 137 | 21.7% |
| Manual | 459 | 305 | 33.5% |
| CAD | 56 | 56 | 0% |
| **合计** | **690** | **498** | **27.8%** |

接入点：`_write_all_stages_to_neo4j`（写入前清洗）+ `/kg/stage4/validate`（验证时同步清洗），清洗统计随响应返回 `postprocess` 字段。

---

## 10. LangGraph 多步骤管道

`backend/pipelines/` — 基于 LangGraph StateGraph，每步独立可观测节点，SSE 实时日志。

### 10.1 RAG 管道（POST /ingest/pipeline）

```
PDF 文件
    ↓ detect_input → analyze_pdf_type（采样判断 text/scanned/mixed）
    ↓ deepdoc_parse_pdf（OCR + LayoutRecognizer + TSR，按 pdf_type 自动选 DPI）
    ↓ extract_structure（ATA 章节识别，正则 72-10-00 格式）
    ↓ build_cross_refs（"See Figure X-Y" 交叉引用）
    ↓ semantic_chunk（结构感知分块：section边界/表格独立/WARNING独立/步骤完整）
    ↓ extract_figures → generate_tech_captions（航空技术图专用提示词 + MiniMax Vision）
    ↓ encode_text_vectors（bge-m3，payload 含 ata_section/figure_refs）
    ├─（有图形时）encode_image_vectors（bge-m3(Caption) + CLIP(图片)）
    ↓ upsert_qdrant（先按 doc_id 删旧，再批量写入）

MD/TXT 文件：detect_input → chunk_text → encode_text_vectors → upsert_qdrant
```

**大型 PDF 进度流**：pipeline 移入后台线程，通过 `AppState._ingest_progress_q`（`queue.Queue`）侧信道，每批（约50页）完成即推送到前端 SSE，无需等待节点结束。

**semantic_chunk 分块优先级**：① ATA Section 边界 → ② 表格独立 → ③ WARNING/CAUTION/NOTE → ④ 编号步骤 → ⑤ ~1600 字符软上限

### 10.2 BOM/CAD 管道（POST /bom/ingest/pipeline）

```
PDF/DOCX → detect_input → extract_tables → llm_to_csv → validate_bom_df → write_neo4j
Excel/CSV → detect_input → load_table → validate_bom_df → write_neo4j
STEP/STP  → lg_cad_pipeline（parse_cad_step → cad_to_kg_triples）
```

**路由**：`bom_ingest_pipeline` 路由函数按文件扩展名分流——`.step/.stp` 走 `state.lg_cad_pipeline`，其余走 `state.lg_bom_pipeline`。

**后台线程**：BOM/CAD 管道同 RAG 管道一样，使用 `progress_queue + 后台线程` 运行（`pipeline_to_log_generator(pipeline, state, progress_queue=q)`），LLM 调用（`llm_to_csv`）期间实时推送日志，不会因 LLM 等待导致 SSE 静默、前端"构建中"永久转圈。

### 10.3 CAD 管道（`nodes_cad.py`）

```
STEP 文件
    ↓ parse_cad_step（pythonocc-core Open CASCADE）
      → cad_assembly_tree（嵌套装配层级）
      → cad_constraints（配合约束：{part_a, part_b, constraint_type}）
      → cad_adjacency（空间邻接：{part_a, part_b, gap_mm}）
    ↓ cad_to_kg_triples → Neo4j（isPartOf / matesWith / adjacentTo 三类关系）
```

依赖：`conda install -c conda-forge pythonocc-core`

### 10.4 知识图谱管道（`nodes_kg.py`）

```
文本块（已入库后触发）
    ↓ extract_kg_triples（LLM → 7类节点 × 9类关系三元组；两轮 Gleaning 提升召回）
    ↓ align_entities（三级对齐：规则词典 → 模糊匹配 → 语义向量）
    ↓ verify_kg_entities（三级验证：BOM 存在性0.4 + ATA 一致性0.3 + 关系权重0.3 → confidence score）
    ↓ validate_kg_dag（Kahn 算法检测 precedes 关系成环并修复）
    ↓ write_kg_neo4j（MERGE 叠加写入；含 _write_kg_represents_edges → REPRESENTED_BY 图边）
```

**GraphRAG 借鉴改进**：
- 实体新增 `description`（1~2句功能描述），关系新增 `weight`（1~10置信度整数）
- 两轮 Gleaning：第一轮提取后，第二轮以已有实体摘要为上下文再次提取遗漏实体（`g1,g2…` 编号），提升覆盖率 20~40%
- Cypher MERGE 时 `weight` 取均值（`(old+new)/2`），description 优先保留非空值

**三源跨图连接**：
- CAD MERGE 去标签约束（无 `:Part/:Assembly` 限定），叠加到 BOM 同名节点上，避免产生孤岛
- `write_kg_neo4j` 节点内调用 `_write_kg_represents_edges()`，为对齐成功的 KG 节点创建 `(BOM节点)-[:REPRESENTED_BY]->(KG节点)` 图边
- `verify_kg_entities` 节点输出 `kg_verification_report`：`{total, verified, low_conf, inconsistent, details}`

**视觉 KG 提取**（`extract_visual_kg` 节点，`nodes_manual.py`）：
- 扫描 `figure_records` 中 caption 含关键词（爆炸图/装配图/结构图等）的图片
- 调用 `app_state.minimax_client`（Vision LLM）提取 isPartOf/matesWith 三元组
- LLM 不可用时静默跳过，不影响文本 KG 提取
- 结果存入 `visual_kg_triples`，在 `extract_kg_triples` 节点中合并到主三元组

**完整管道流（RAG+KG 分支）**：
```
... → extract_flowchart_structure → extract_visual_kg → encode_text_vectors → ...
                                                                               ↓
extract_kg_triples → align_entities → verify_kg_entities → validate_kg_dag → write_kg_neo4j
```

### 10.5 deepdoc 集成架构

**Shim 层**（`document_processing/`）：

| Shim 文件 | 替换的 RAGFlow 模块 |
|-----------|-------------------|
| `common/file_utils.py` | `get_project_base_directory()` |
| `common/misc_utils.py` | `pip_install_torch()` / `thread_pool_exec()` |
| `common/settings.py` | `PARALLEL_DEVICES = 0` |
| `rag/utils/lazy_image.py` | `ensure_pil_image()`（bytes/ndarray/PIL 统一转换，不强转 uint8） |
| `rag/nlp/__init__.py` | `find_codec()` + `rag_tokenizer` |
| `rag/prompts/generator.py` | `vision_llm_describe_prompt()`（空实现） |

**注意**：`xgboost` 需固定 2.x（`pip install "xgboost==2.1.4"`），3.x 移除旧 binary 模型格式支持。

---

## 11. React 前端详解

### 11.1 技术栈

| 层级 | 选型 |
|------|------|
| 框架 | React 19 + TypeScript |
| 构建 | Vite 8（`npm run dev` → `:5173`） |
| 样式 | Tailwind CSS v4 |
| Markdown 渲染 | react-markdown + remark-gfm |
| 图谱可视化 | **D3.js v7**（`d3` + `@types/d3`，力导向图） |

### 11.2 页面布局（App.tsx）

统一扁平布局（无 Tab 切换）：

```
Header（后端健康状态：知识库块数 + 模型名）
├── Accordion: 📂 知识库管理（KnowledgePanel）
├── Accordion: 📊 性能评估（EvalPanel）
├── Accordion: 🔗 图谱构建（KgBuilder）
├── Accordion: 🕸️ 知识图谱（KgViewer）
└── UnifiedChat（内含 RAG/装配 模式切换）
```

### 11.3 UnifiedChat（`components/shared/UnifiedChat.tsx`）

合并了原 `RagChat`（蓝色主题）和 `AssemblyChat`（橙色主题）：

- **模式切换**：顶部分段控件 `mode: 'rag' | 'assembly'`，切换时自动 `clearMessages()` + 清理图片
- **主题色**：`THEMES` 对象按 mode 映射所有颜色 class（bubble/button/badge/cursor/dots）
- **Vision 功能**：仅 `mode === 'rag'` 时显示 📷 按钮和粘贴处理
- **路由逻辑**：`mode === 'rag'` → `postChat()`；`mode === 'assembly'` → `postAssemblyChat()`
- **processChildren**：inline 保留，badge 颜色随 mode 动态切换

### 11.4 KgBuilder（`components/kg/KgBuilder.tsx`）

图谱构建面板，三栏卡片式 UI，每栏独立上传对应类别文件：

| 栏 | 颜色 | 接受后缀 | 调用端点 | 管道 |
|----|------|---------|---------|------|
| 📖 维修手册 | 蓝色 | `.pdf/.md/.txt/.docx` | `POST /ingest/pipeline` | RAG 管道（含 KG 三元组提取） |
| 🔩 BOM 清单 | 绿色 | `.xlsx/.xls/.csv/.pdf/.docx` | `POST /bom/ingest/pipeline` | BOM 管道 |
| 📦 CAD 模型 | 紫色 | `.step/.stp` | `POST /bom/ingest/pipeline` | CAD 管道 |

**关键实现细节**：
- 三个独立 `<input type="file" ref>` 分别绑定各栏，accept 仅限对应类型
- `addFiles(fileList, forcedCategory)` 中 `forcedCategory` 以点击的栏为准——避免 `.docx/.pdf` 等共享后缀被 `detectCategory()` 误归为维修手册
- 构建时 `CATEGORY_ORDER`（BOM=0 → CAD=1 → RAG=2）自动排序，确保权威数据先入库
- `clearFirst` 仅传给第一个文件（排序后首位），后续文件始终追加
- 集成 Neo4j 状态检测（挂载时自动查询 `/bom/status`），SSE 日志实时显示构建进度

### 11.5 KgViewer（`components/kg/KgViewer.tsx`）

D3 v7 力导向图可视化，数据来源：`GET /bom/kg/graph?keyword=&limit=200`。

- **节点颜色**：`TYPE_COLORS` 映射（Part=蓝/Assembly=绿/Procedure=橙/Tool=紫/Specification=红/Interface=灰）
- **边颜色**：`REL_COLORS` 映射（precedes=橙/CHILD_OF=灰/requires=紫/matesWith=绿...）
- **交互**：拖拽节点、缩放/平移（d3-zoom）、点击高亮邻居、hover tooltip（实体属性）
- **搜索**：输入框带关键词重新查询后端，留空显示全图

### 11.6 后端 `/bom/kg/graph`

`backend/routers/bom.py` 新增 `GET /bom/kg/graph(keyword, limit=200)`：

- 无关键词：全图模式（MATCH (n) LIMIT limit 后 OPTIONAL MATCH 邻居）
- 有关键词：匹配 `kg_name / part_name / ata_section` 后取 1 跳邻居
- 响应格式：`{"nodes": [{id, label, type, ...attrs}], "links": [{source, target, type}]}`
- 节点 id 优先 `kg_id` → `part_id` → element_id

### 11.7 POST SSE 实现

浏览器原生 `EventSource` 只支持 GET；聊天/入库均为 POST，使用 `fetch + ReadableStream`：
- 日志类流（`usePostSSE`）：每帧覆盖显示 `frame.log`
- 聊天类流（`useChat`）：中间帧追加 `frame.delta`，done 帧解析 `sources` + `image_urls`；首个 delta 到达时自动清空 `currentStage`

### 11.8 图片上传（UnifiedChat RAG 模式）

- 📷 按钮或 `onPaste` 剪贴板 → `pendingImage`
- 发送时：先调 `/vision/describe` 获取描述 → 拼入 `[图片内容：{description}]` → POST `/chat`

### 11.9 Vite 代理

`vite.config.ts`：`/api/*` + `/images/*` 均代理到 `http://localhost:8000`。

---

## 12. 配置系统（.env）

```env
# ===== LLM 备用（SiliconFlow，必填）=====
LLM_API_KEY=sk-xxx
LLM_BASE_URL=https://api.siliconflow.cn/v1
LLM_MODEL=Qwen/Qwen2.5-14B-Instruct

# ===== MiniMax（主 LLM + Vision，可选但推荐）=====
MINIMAX_API_KEY=your_minimax_key
MINIMAX_BASE_URL=https://api.minimaxi.com/v1
MINIMAX_MODEL=MiniMax-M2.5

# ===== Neo4j（BOM 装配方案，可选）=====
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASS=password
```

不配置 `MINIMAX_API_KEY` 的影响：图片 Caption 生成不可用（PDF 图片块跳过）；以图搜文返回 503；文字查图仍可用（若已有图片块）。

---

## 13. 运行方式

### 13.1 首次环境准备

```bash
conda create -n rag_demo python=3.10 && conda activate rag_demo
PYTHONUTF8=1 pip install -r requirements.txt
cp .env.example .env  # 编辑填写 API Key
cd frontend && npm install && cd ..
```

### 13.2 启动服务

```bash
# 终端1：后端
PYTHONUTF8=1 python run_backend.py

# 终端2：前端
cd frontend && npm run dev
# 访问 http://localhost:5173
```

或使用 `start.sh` 一键启动（后台启动后端 + 前端）。

### 13.3 知识库入库

**前端**（推荐）：React 界面 → 知识库 Tab → 开始入库，日志实时显示。

**命令行**：
```bash
PYTHONUTF8=1 python main_ingest.py          # 增量入库
PYTHONUTF8=1 python main_ingest.py --clear  # 清空重建
PYTHONUTF8=1 python main_ingest.py --no-image  # 纯文本（无 MiniMax 时）
```

### 13.4 BOM 数据入库

```bash
PYTHONUTF8=1 python bom_ingest.py                     # 入库 data/test_bom.xlsx
PYTHONUTF8=1 python bom_ingest.py --file data/my.xlsx # 指定文件
PYTHONUTF8=1 python bom_ingest.py --clear             # 清空重建
```

---

## 14. 常见问题与排查

### Q: 后端启动 `ModuleNotFoundError: No module named 'qdrant_client'`
```bash
pip install qdrant-client>=1.11
```

### Q: 模型首次加载很慢
首次从 HuggingFace 下载 bge-m3（~1.2GB）、Chinese-CLIP（~2GB）、bge-reranker-base（~280MB）。国内可设置镜像：
```bash
export HF_ENDPOINT=https://hf-mirror.com
```

### Q: 图片 Caption 生成失败（"Caption 失败，跳过"）
检查 `.env` 中 `MINIMAX_API_KEY` 是否正确，以及 API 配额是否充足。失败的图片块会被跳过，不影响文本块入库。

### Q: `GET /images/xxx.png` 返回 404
1. `storage/images/` 目录不存在 — lifespan 中 `os.makedirs` 会创建，重启后端即可
2. Vite 代理未配置 `/images` — `vite.config.ts` 需同时代理 `/api` 和 `/images`
3. 文件名含特殊字符 — `retrieve.py` 的 `_image_url()` 已使用 `urllib.parse.quote()` 编码

### Q: Qdrant `collection_exists` 返回 False 但文件存在
`QDRANT_DB_PATH` 是**目录**（`storage/qdrant.db/`），不是单文件，不要用文件路径操作处理。

### Q: PDF 入库 0 chunks
降级链（三层）：① deepdoc 高 DPI 重试 → ② fitz block 提取 → ③ OCR-only。若日志显示 `fitz block 提取完成：N 个区域`，说明 deepdoc ONNX 有问题但 fitz 正常产出 chunks，可先用这个结果。xgboost 版本必须是 2.x（`pip install "xgboost==2.1.4"`）。

### Q: 大型 PDF（500+页）日志长时间不更新
正常行为。进度通过后台 Queue 侧信道推送，每批（50页）约 30-90 秒刷新一次。`analyze_pdf_type` 节点完成后会提前显示"⚠ 大型文档：N 页，将分 X 批解析"预警。

### Q: Windows 路径中文乱码
所有 Python 命令前加 `PYTHONUTF8=1`。

---

## 15. 变更日志

| 日期 | 变更内容 |
|------|----------|
| 2026-03-06 | 初始化项目：架构设计、deepdoc 集成、Qdrant 入库 |
| 2026-03-09 | RAG 评估模块、MiniMax 主备 LLM |
| 2026-03-12 | BOM-GraphRAG：bom_ingest.py + Neo4j |
| 2026-03-18 | FastAPI 后端重构（12 个 REST+SSE 接口）+ React 前端（替代 Gradio） |
| 2026-03-20 | 图文检索：向量库迁移至 Qdrant；Chinese-CLIP 双向量；Vision Caption；多查询+CrossEncoder 重排 |
| 2026-03-23 | 修复 Chinese-CLIP 维度（projection_dim=768）；修复图片显示（Vite代理/URL编码/断裂引用） |
| 2026-03-24 | LangChain 集成（7大组件全覆盖）；BOM 多格式入库（PDF/DOCX） |
| 2026-03-25 | LangGraph 管道：RAG管道（/ingest/pipeline）+ BOM管道（/bom/ingest/pipeline）+ deepdoc AI 解析引擎集成 |
| 2026-03-26 | 修复大型 PDF OOM + 图片丢失：CHUNK_SIZE 200→50；fitz fallback 支持嵌入图片；引入 Queue 侧信道实现 SSE 实时进度流 |
| 2026-03-26 | 修复 deepdoc 0 chunks（4层根因）：zoomin 参数化；wrapper 层补偿重试死代码；ONNX uint8/float 类型错误修复 |
| 2026-03-27 | SSE stage 帧：多查询/检索/重排序阶段向用户实时显示进度（类 Claude status line） |
| 2026-03-30 | 混合检索：BM25（rank_bm25+jieba）+ Dense RRF 融合；BM25Manager 持久化（pickle）+ 启动自动重建 |
| 2026-03-31 | 知识图谱升级：新建 `nodes_kg.py`（4节点：LLM抽取/实体对齐/DAG校验/Neo4j写入）、`nodes_cad.py`（2节点：STEP解析/规则转三元组）；扩展 PipelineState（KG+CAD字段）；`_query_procedure_chain`（Kahn拓扑排序有序工序链）；`make_rag_pipeline` 接入 KG 链；`make_cad_pipeline` 新增；装配问答注入有序工序优先上下文；Agent 新增 `procedure_chain_query` 工具（第6个） |
| 2026-04-01 | 修复 `_topological_sort_kahn` 孤立节点追踪 bug（`d["proc_id"]` → `sorted_node_ids` set）；`main.py` lifespan 补传 `neo4j_cfg` 至 RAG 管道 + 编译 CAD 管道；全链路导入+逻辑测试通过 |
| 2026-03-31 | 新增 CAD 管道（nodes_cad.py：STEP → Open CASCADE → Neo4j）；知识图谱管道（nodes_kg.py：LLM抽取 → 实体对齐 → DAG验证 → Neo4j） |
| 2026-04-01 | 前端大重构：① 合并 RagChat+AssemblyChat → UnifiedChat（模式切换+主题色动态）；② 新建 KgBuilder（BOM/RAG/CAD 统一入库面板）；③ 新建 KgViewer（D3 力导向图，7实体颜色/9关系颜色/拖拽缩放/点击高亮）；④ 移除双 Tab，改为扁平 Accordion 布局；⑤ 后端新增 GET /bom/kg/graph 可视化数据端点；⑥ types/index.ts 新增 KgNode/KgLink/KgGraphData；⑦ 安装 D3 v7 依赖 |
| 2026-04-02 | 三源互补知识图谱：① nodes_kg.py 引入 GraphRAG Gleaning（两轮抽取）+ description/weight 字段 + verify_kg_entities 节点（三级置信度验证）+ REPRESENTED_BY 图边（BOM→KG）；② nodes_manual.py 新增 extract_visual_kg 节点（爆炸图关键词过滤→视觉LLM→isPartOf/matesWith 三元组）；③ nodes_cad.py MERGE 去标签约束（CAD关系叠加到BOM节点）；④ factory.py 接入两个新节点；⑤ state.py 新增 visual_kg_triples/kg_verification_report 字段 |
| 2026-04-02 | KgBuilder 前端重构：平铺列表→三栏卡片（各栏独立 file input + forcedCategory 修复 .docx 误归类问题）；bom_ingest_pipeline 路由修复（CAD 文件正确走 lg_cad_pipeline；BOM/CAD 均改为后台线程+队列，修复 LLM 等待期间 SSE 静默/前端永久"构建中"的 bug）|
| 2026-04-13 | 三元组后处理管道（TASK_05）：新建 `backend/pipelines/kg_postprocess.py`（置信度过滤MIN=0.3 + 归一化 + 本体校验 + 去重四步流水线）；接入 `_write_all_stages_to_neo4j` 与 `/kg/stage4/validate` 端点；690→498 条，清除率 27.8%，response 新增 `postprocess` 统计字段 |
| 2026-04-15 | BOM 层级修复 Phase1（TASK_01）：① 新增 `_clean_ocr_noise`（正则净化 COMP0NENT/0F/0N/0VS/N0. 等 OCR 噪声，接入 OCR chunk 预处理和每行字段后处理）；② 强化 `_OCR_BOM_PROMPT`（新增规则7 NHA跨图单点前缀/规则8 INTRCHG互换件层级 + 4条 few-shot）；③ 新增 `_resolve_nha_triples`（后处理修正 tail==ROOT 且含 SEE FIG.X FOR NHA 的三元组，连接到顶层 Assembly）；新增测试 `tests/kg/test_bom_hierarchy.py`（15条单元测试）+ `tests/kg/test_bom_stage1_acceptance.py`（4条验收测试）|
| 2026-04-20 | BOM 层级修复 Phase2（职责分离架构）：ROOT 率从 51%（73/142 条）→ 0.5%（1/220 条）。① 重写 `_OCR_BOM_PROMPT`——严禁 LLM 推断层级（`parent_id` 恒为 `""`），仅忠实提取；补充 ATTACHING PARTS/爆炸图页跳过/PRE-POST-SB 保留/6条 IPC few-shot；② 新增 `_apply_ipc_hierarchy(records)`——纯确定性规则填 `parent_id`：R0 root自保/R2 ATTACHING PARTS块标记/R3 attaching子件挂最近Assembly/R4 dash前缀与基件共享父/R5 整数 fig_item 挂 root_assembly；③ 修复 `_bom_df_to_entities_and_triples` 栈算法——while 循环增加 `len==1 and level==0` 守卫防止 root Assembly 被弹出；④ 扩展测试（TestApplyIpcHierarchy 5条 + TestLevel0Fix 3条），23/23 全绿；报告文件：`docs/reports/2026-04-20-bom-hierarchy-fix.md` |
| 2026-04-22 | 新增黄金三元组集（Ground Truth Benchmark）：人工精读维修手册 3013242（72-30 章）生成 `storage/kg_stages/golden_triples.json` v2；108 个实体 / 99 条三元组 / 覆盖 7 实体类型 + 9 关系类型；写入 PROJECT_GUIDE §9.4.1，作为后续所有 KG 构建代码的评测基准。 |
| 2026-05-09 | Assembly Scheme Skill Plan 1（T1-T13）：新增 skill 骨架（SKILL.md + 5阶段方法论 + 8个 JSON Schema + PT6A HPC golden 示范 + S1 提示词）+ 后端管道（skill_loader / stage1_intake / web_search）+ REST 路由（assembly_design.py）+ lifespan 集成 + 43 条测试全绿 |

---

## 16. Assembly Scheme Skill (Plan 1, v0)

> 状态：Plan 1 (P1+P2) 完成 — Skill 骨架 + S1 端到端可跑通。Plan 2-N 待续。

### What
新增"航空发动机装配方案设计师" skill，从单纯工具堆叠跃迁到"专家心智 + 工作流 + HITL + 自我生长"的领域智能体。
首版示范标的：PT6A HPC 子系统。Plan 1 仅实现 S1（任务调研 + 资料采集）端到端管道。

### Why
现有 RAG/KG/CAD/BOM 工具都是"底层能力"，缺少把它们组装成"像装配工艺师那样设计方案"的高层方法论与流程。
本 skill 沉淀 5 阶段方法论（S1 调研 / S2 需求 / S3 概念 / S4 详细工艺 / S5 评审），用 SKILL.md 作为 source of truth。

### How
- **Layer 1 — Skill 文档**：`skills/aero-engine-assembly-scheme/`
  - `SKILL.md` 主入口（frontmatter + checklist + 决策图 + 反模式）
  - `methodology/` x 5（S1 完整、S2-S5 outline v1）
  - `templates/schemas/` x 8 个 JSON Schema
  - `templates/golden/` PT6A HPC S1 示范
  - `prompts/s1_intake.prompt.md` LLM 提示词模板
  - `references/` 反哺写入目标（v1 仅留 _index.md 和 _ingest_log.json 占位）
- **Layer 2 — 后端管道**：`backend/pipelines/assembly_scheme/`
  - `skill_loader.py`：`SkillRegistry` 类，启动时加载整套 skill
  - `stage1_intake.py`：`run_stage1_intake(user_input, skill, web_search, llm_client, neo4j_driver) -> dict`
  - 调用链：构建 web 查询 -> KG snapshot -> Tavily 检索 -> LLM 生成 task_card_md -> 返回符合 stage1 schema 的 dict
- **Layer 2 — Web 工具**：`backend/tools/web_search.py`
  - `WebSearchClient`：Tavily 封装，含 sha256 文件缓存（`storage/web_cache/`），未配置 key 时优雅降级
- **Layer 2 — REST 端点**：`backend/routers/assembly_design.py`
  - `POST /assembly-design/scheme/new` 创建方案
  - `GET /assembly-design/scheme/list` 列出
  - `GET /assembly-design/scheme/{id}` 取详情
  - `POST /assembly-design/scheme/{id}/stage/{stage_key}` 跑某阶段（v0 仅 stage_key="1" 可用，其余返回 501）
  - `POST /scheme/{id}/reflux` / `POST /scheme/{id}/iterate` / `GET /scheme/{id}/export` v0 全返回 501
- **Lifespan 集成**：`backend/main.py` 启动时加载 skill_registry + 初始化 web_search_client，注入到 AppState；skill 加载失败时降级为 None（assembly 端点返回 503，不影响其他模块）

### Where（证据）
- 测试：`tests/assembly/test_*.py`（全部 PASS）
- E2E：`tests/assembly/test_e2e_stage1.py` — 创建方案 -> stage1 生成 -> schema 校验 -> 取回
- Spec：`docs/superpowers/specs/2026-05-08-assembly-scheme-skill-design.md`
- Plan：`docs/superpowers/plans/2026-05-08-assembly-scheme-p1-p2.md`

### 配置
新增环境变量 `TAVILY_API_KEY`（可选）：
- 已配置：S1 联网检索三组查询，结果含 confidence 待用户审核
- 未配置：web_search 静默返回空列表，S1 仍能跑通（仅用本地 KG + LLM）

---

### 16.P2 Plan 2 进展 — S2 需求分析 + S3 概念架构 (2026-05-14)

> 状态：Plan 2 完成 — S2/S3 端到端可跑通，69 条 assembly 测试全绿。

#### What
在 P1（S1 管道）基础上，新增 S2（需求与约束分析）和 S3（概念架构生成）两个阶段，并补足 P1 遗留的三个缺陷修复。

**新增管道**
- `backend/pipelines/assembly_scheme/stage2_requirements.py`：`run_stage2_requirements()` — QFD-轻量 + Boothroyd-Dewhurst DFA-lite + KC + 风险
- `backend/pipelines/assembly_scheme/stage3_concept.py`：`run_stage3_concept()` — 多候选架构生成（≥2），含 KG-静态可达性评估和 fit_score_to_metrics

**新增 Skill 资产**
- `methodology/s2_requirements_qfd.md`：QFD 三柱映射（用户需求→工程指标→装配特征）+ DFA-lite 算法 + KC 分级方法
- `methodology/s3_concept_architecture.md`：候选架构综合评估五因子（reachability/interference/datum/KC_coverage/maintainability）
- `prompts/s2_requirements.prompt.md`、`prompts/s3_concept.prompt.md`：LLM 提示词模板
- `templates/schemas/stage2.schema.json`：7 个必填字段（stage1_ref + QFD 三柱 + KC + dfa_score + risks），minItems≥1
- `templates/schemas/stage3.schema.json`：candidate_architectures minItems≥2，每条必含 assembly_simulation + datum_consistency + fit_score_to_metrics
- `templates/golden/pt6a_hpc_stage2.json`、`templates/golden/pt6a_hpc_stage3.json`：PT6A HPC 示范数据，验证通过 jsonschema

**P1 缺陷修复**
- `subject_scope` 空列表防御：`NewSchemeRequest.subject_scope: List[str] = Field(..., min_length=1)` → POST 422
- `assembly_lock`：`threading.Lock` 保护 meta.json 读-改-写，防并发 stages_done 损坏
- 阶段顺序门控：stage/2 → 409 if stage1.json 缺失；stage/3 → 409 if stage2.json 缺失

#### Why
S1 仅产出任务卡片，无法进入实际设计决策；S2 将用户意图量化为可追溯的工程指标（QFD），S3 将指标映射到候选架构并通过 KG 可达性客观评分，使 HITL 复核有数据依据而非主观判断。  
JSON Schema 强校验每个阶段输出，确保后续阶段读入时数据完整，避免"字段缺失导致的静默错误"。

#### How（核心调用链）

**stage/2 → run_stage2_requirements**
```
POST /assembly-design/scheme/{id}/stage/2
  → router: check stage1.json exists (→ 409 if missing)
  → assembly_lock.acquire()
  → run_stage2_requirements(stage1_payload, skill, llm_client, ...)
      → 构建 s2_requirements prompt（含 skill.prompts["s2_requirements"] + methodology）
      → LLM call（None → PLACEHOLDER，parse fail → PLACEHOLDER）
      → jsonschema.validate(result, stage2.schema.json)
      → 强制覆写 stage1_ref = stage1_payload["scheme_id"]
      → 返回 stage2 dict
  → 写 stage2.json，更新 meta.json stages_done += "2"
  → assembly_lock.release()
```

**stage/3 → run_stage3_concept**
```
POST /assembly-design/scheme/{id}/stage/3
  → router: check stage2.json (→ 409 "stage2 not done")，check stage1.json
  → assembly_lock.acquire()
  → run_stage3_concept(stage1_payload, stage2_payload, skill, llm_client, neo4j_driver=None, ...)
      → query_kg_subgraph(neo4j_driver, subject_name)  # None/异常 → 空 dict，优雅降级
      → 构建 s3_concept prompt（含 KG 子图 + stage2 QFD 摘要）
      → LLM call（None/fail → PLACEHOLDER，minItems<2 → PLACEHOLDER）
      → jsonschema.validate(result, stage3.schema.json)
      → 强制覆写 stage1_ref、stage2_ref
      → 返回 stage3 dict
  → 写 stage3.json，更新 meta.json stages_done += "3"
  → assembly_lock.release()
```

**降级策略（三层保险）**
1. LLM=None → 直接返回 PLACEHOLDER（含 `uncertainty:"高"`）
2. LLM 返回无效 JSON → `json.JSONDecodeError` 捕获 → PLACEHOLDER
3. LLM JSON 不过 schema → `jsonschema.ValidationError` 捕获 → PLACEHOLDER

#### Where（证据）
- 单元测试：`tests/assembly/test_stage2_requirements.py`（5 tests）、`tests/assembly/test_stage3_concept.py`（7 tests）
- E2E 链路：`tests/assembly/test_e2e_s1_s2_s3.py`（2 tests：S1→S2→S3 全链 + S4/S5 仍返回 501）
- 路由测试：`tests/assembly/test_assembly_design_router.py`（含 stage2/stage3 happy path + 409 门控 + save_edits）
- Schema 测试：`tests/assembly/test_schemas.py`（含 stage2/stage3 schema 结构 + golden 验证）
- 全套结果：69 passed in 0.79s（branch `feat/assembly-scheme-p2-s2-s3`）
