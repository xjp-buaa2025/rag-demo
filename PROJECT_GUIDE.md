# RAG Demo 项目完全指南

> 本文档随代码同步维护。每次新增/修改功能后同步更新对应章节。
> 目标：让你能完整理解每一行代码背后的思路，无需再看其他资料。

---

## 目录

1. [项目整体目标](#1-项目整体目标)
2. [核心概念：RAG 与图文检索](#2-核心概念rag-与图文检索)
3. [技术选型总览](#3-技术选型总览)
4. [架构总览](#4-架构总览)
5. [数据流全景](#5-数据流全景)
6. [文件结构说明](#6-文件结构说明)
7. [后端代码详解](#7-后端代码详解)
8. [图文检索详解](#8-图文检索详解)
9. [BOM-GraphRAG 扩展](#9-bom-graphrag-扩展)
10. [React 前端详解](#10-react-前端详解)
11. [配置系统（.env）](#11-配置系统env)
12. [运行方式](#12-运行方式)
13. [常见问题与排查](#13-常见问题与排查)
14. [变更日志](#14-变更日志)

---

## 1. 项目整体目标

构建一个**完全本地化**的**图文多模态 RAG**问答系统，能回答"知识库里有但大模型不知道"的内容，同时支持图片检索。

核心能力：
- **文字查文档**：传统 RAG，bge-m3 向量检索
- **文字查图片**：输入文字描述，召回 PDF 中的相关图片（Chinese-CLIP）
- **以图搜文**：上传图片，系统用 Vision LLM 生成描述后检索相关文档片段
- **BOM 装配问答**：Neo4j 零件图谱 + 技术知识库双路融合
- **Embedding 完全本地**：不调用任何外部 Embedding API

---

## 2. 核心概念：RAG 与图文检索

### 文字 RAG

```
用户问题
    ↓ bge-m3 将问题向量化（1024维）
    ↓ Qdrant 余弦检索 → Top-K 文本块
    ↓ 拼接 Prompt：系统提示 + 参考原文 + 问题
    ↓ LLM 生成回答
输出（有来源依据）
```

### 图文双路检索

```
用户问题（文字）
    ├─ bge-m3 → 搜 text_vec → 文本块 + 图片Caption块
    └─ Chinese-CLIP文本编码 → 搜 image_vec → 图片块
              ↓ 合并去重 → CrossEncoder 重排 → Top-K
              ↓ LLM 生成回答 + 相关图片展示

用户上传图片
    ├─ MiniMax Vision → 中文描述 → 走文字检索路径
    └─ Chinese-CLIP图片编码 → 搜 image_vec → 以图搜图
```

### 双向量设计

每个 Qdrant Point 存储两个向量：

| 字段 | 模型 | 用途 |
|------|------|------|
| `text_vec` | bge-m3（1024维） | 文本语义检索 |
| `image_vec` | Chinese-CLIP（1024维） | 图片跨模态检索 |

文本块的 `image_vec` 填零向量；图片块的 `text_vec` 填 Caption 的 bge-m3 向量。

---

## 3. 技术选型总览

| 组件 | 选型 | 说明 |
|------|------|------|
| 向量数据库 | **Qdrant**（本地文件模式） | `storage/qdrant.db`，无需 Docker，Windows 原生支持 |
| 文本 Embedding | **BAAI/bge-m3**（1024维） | 本地推理，中英文均优秀 |
| 图片 Embedding | **OFA-Sys/chinese-clip-vit-large-patch14**（1024维） | 中文 CLIP，图文跨模态 |
| 图片 Caption | **MiniMax M2.5 Vision** | PDF 图片→中文描述，入库时调用 |
| Reranker | **BAAI/bge-reranker-base** | CrossEncoder 精排，约 280MB |
| LLM（主） | MiniMax M2.5（远程 API） | 支持 Vision；failover 到 SiliconFlow |
| LLM（备） | SiliconFlow / vLLM | OpenAI 兼容，Qwen2.5-14B 等 |
| 图谱数据库 | **Neo4j** | BOM 零件树，Cypher 递归查询 |
| 后端框架 | **FastAPI** + uvicorn | SSE 流式响应 |
| 前端框架 | **React 18 + TypeScript + Vite** | Tailwind CSS v4，POST SSE |
| PDF 解析 | PyMuPDF（文本提取）+ MinerU（OCR） | 双路：可复制 PDF 直接提取，扫描版先 OCR |

---

## 4. 架构总览

```
┌────────────────────────────────────────────────────────────────┐
│  React 前端（:5173）                                            │
│  RAG问答 / 图片上传 / 知识库管理 / 评估 / BOM装配方案          │
└───────────────────────┬────────────────────────────────────────┘
                        │ POST SSE / JSON（/api/* → Vite代理）
┌───────────────────────▼────────────────────────────────────────┐
│  FastAPI 后端（:8000）                                          │
│  ├─ /ingest        文档入库（双向量，SSE 进度流）               │
│  ├─ /retrieve      向量检索（双路图文，JSON）                   │
│  ├─ /chat          RAG 问答（多查询+双路+重排序，SSE）          │
│  ├─ /eval/*        RAG 评估（诊断/RAGAS/LLM打分，SSE）         │
│  ├─ /bom/*         BOM 入库 + Neo4j 查询                       │
│  ├─ /assembly/chat BOM+知识库融合问答（SSE）                   │
│  ├─ /vision/*      图片描述 + 以图搜图                         │
│  └─ /images/*      图片静态文件服务（storage/images/）         │
├────────────────────────────────────────────────────────────────┤
│  核心组件层                                                     │
│  EmbeddingManager（bge-m3 + Chinese-CLIP）                     │
│  FallbackLLMClient（MiniMax → SiliconFlow 自动降级）           │
│  ImageCaptioner（MiniMax Vision，图片→中文描述）               │
│  CrossEncoder Reranker（BAAI/bge-reranker-base）               │
├────────────────────────────────────────────────────────────────┤
│  存储层                                                         │
│  Qdrant（storage/qdrant.db）— 双向量文本+图片                  │
│  Neo4j（Docker）— BOM 零件关系图谱                             │
│  storage/images/ — 提取的 PDF 图片文件                         │
└────────────────────────────────────────────────────────────────┘
```

---

## 5. 数据流全景

### 5.1 知识库入库（一次性，离线）

```
data/*.pdf
    ↓ [PyMuPDF] 逐页提取文本 → 按句子边界切块（500字/块）
    ↓ [PyMuPDF] page.get_images() → 过滤小图（<100×100）→ 保存 storage/images/
    ↓ [bge-m3] 文本块向量化 → text_vec（1024维）
    ↓ [MiniMax Vision] 图片 → 中文 Caption
    ↓ [bge-m3] Caption 向量化 → 图片块 text_vec
    ↓ [Chinese-CLIP] 图片 → image_vec（1024维）
    ↓ Qdrant upsert → 双向量存储
       每个 Point：{text_vec, image_vec, text, source, page, chunk_type, image_path, doc_id}

data/*.md / *.txt
    ↓ [RAGFlowTxtParser] deepdoc 解析 → 文本块
    ↓ [bge-m3] 向量化 → text_vec；image_vec = [0]*1024
    ↓ Qdrant upsert

（扫描版 PDF 需先执行 pdf_to_md.py，用 MinerU OCR 生成 .md 文件）
```

### 5.2 问答检索（实时）

```
用户输入文字问题
    ↓ [LLM] 生成2个额外查询角度（多查询召回，静默）
    ↓ 对每个查询：
       ├─ [bge-m3] → Qdrant text_vec 搜索（Top-8，文本+Caption）
       └─ [Chinese-CLIP] → Qdrant image_vec 搜索（Top-4，仅图片块）
    ↓ 合并去重（按 Point UUID，保留最高 score）
    ↓ [CrossEncoder] 精排 → Top-4
    ↓ 拼接 Prompt → LLM 流式生成回答
    ↓ SSE 帧：delta（增量）→ done（sources_md + image_urls）
前端：回答 + 参考来源脚注 + 相关图片缩略图
```

---

## 6. 文件结构说明

```
rag-demo/
├── pdf_to_md.py              # 扫描版 PDF → Markdown（MinerU OCR，可选预处理）
├── main_ingest.py            # CLI 入库工具（Qdrant 双向量，支持 --clear）
├── bom_ingest.py             # BOM Excel → Neo4j 零件图谱
├── run_backend.py            # FastAPI 快速启动（uvicorn --reload）
├── requirements.txt
├── .env                      # 密钥配置（不提交 git）
│
├── data/                     # 原始文档（.pdf .md .txt）
│
├── storage/
│   ├── qdrant.db/            # Qdrant 本地文件数据库
│   └── images/               # PDF 提取的图片文件（/images/* 静态服务）
│
├── backend/                  # FastAPI 后端
│   ├── main.py               # 应用入口：lifespan 初始化 + 路由注册
│   ├── state.py              # AppState dataclass + FallbackLLMClient
│   ├── embedding_manager.py  # EmbeddingManager（bge-m3 + Chinese-CLIP）
│   ├── image_captioner.py    # MiniMax Vision 图片描述
│   ├── deps.py               # FastAPI Depends（get_state / get_neo4j_cfg）
│   ├── sse.py                # 生成器 → SSE 响应适配
│   └── routers/
│       ├── ingest.py         # POST /ingest（SSE），GET /ingest/status
│       ├── retrieve.py       # POST /retrieve（双路检索，JSON）
│       ├── chat.py           # POST /chat（多查询+双路+重排，SSE）
│       ├── eval.py           # POST /eval/diagnose|judge|ragas|ranked|retrieval|generation（SSE）
│       ├── bom.py            # POST /bom/ingest（SSE），GET /bom/status，POST /bom/query
│       ├── assembly.py       # POST /assembly/chat（SSE）
│       └── vision.py         # POST /vision/describe，POST /vision/search
│
├── frontend/                 # React 前端
│   ├── src/
│   │   ├── App.tsx           # 根组件：Header + 双 Tab
│   │   ├── types/index.ts    # TypeScript 类型定义
│   │   ├── api/client.ts     # 所有后端 API 调用封装
│   │   ├── hooks/
│   │   │   ├── usePostSSE.ts # 日志类 SSE hook
│   │   │   └── useChat.ts    # 聊天类 SSE hook（含 imageUrls）
│   │   └── components/
│   │       ├── rag/
│   │       │   ├── KnowledgePanel.tsx  # 知识库入库 + 日志
│   │       │   ├── EvalPanel.tsx       # 六种评估报告
│   │       │   └── RagChat.tsx         # RAG 问答（含图片上传）
│   │       └── bom/
│   │           ├── Neo4jStatus.tsx     # Neo4j 连接状态
│   │           ├── BomIngest.tsx       # BOM 文件上传入库
│   │           └── AssemblyChat.tsx    # 装配方案融合问答
│   └── vite.config.ts        # /api/* 代理到 localhost:8000
│
└── document_processing/      # deepdoc 解析引擎（RAGFlow 抽离，不修改）
    ├── common/token_utils.py # shim：token 计数
    ├── rag/nlp/__init__.py   # shim：编码检测
    └── deepdoc/              # TxtParser / MarkdownParser 等
```

---

## 7. 后端代码详解

### 7.1 `backend/main.py` — 应用入口

**lifespan 初始化顺序**：
1. `EmbeddingManager` 加载（bge-m3 + Chinese-CLIP，约 2+2GB，首次需下载）
2. `_init_qdrant(QDRANT_DB_PATH, COLLECTION_NAME)` — 创建或打开本地 Qdrant
3. `CrossEncoder("BAAI/bge-reranker-base")` — Reranker（失败则降级为距离排序）
4. LLM 客户端配置（MINIMAX_API_KEY 存在则 MiniMax 为主，否则直接用 SiliconFlow）
5. 构造 `AppState` 放入 `app.state.app_state`
6. **兜底自动入库**：若 Qdrant 为空且 `data/` 有文件，后台线程触发 `_run_ingest`

**`_init_qdrant`** 创建 Named Multi-Vector Collection：
```python
vectors_config={
    "text_vec":  VectorParams(size=1024, distance=Distance.COSINE),
    "image_vec": VectorParams(size=1024, distance=Distance.COSINE),
}
```

### 7.2 `backend/state.py` — 全局状态

```python
@dataclass
class AppState:
    qdrant_client: Any              # QdrantClient（本地文件 storage/qdrant.db）
    embedding_mgr: Any              # EmbeddingManager（bge-m3 + Chinese-CLIP）
    llm_client: Any                 # FallbackLLMClient 或 openai.OpenAI
    active_model_label: str         # 显示用，e.g. "MiniMax(M2.5) → fallback: Qwen"
    minimax_client: Optional[Any]   # 原始 MiniMax OpenAI 实例，Vision 专用
    minimax_model: str
    reranker: Optional[Any]         # CrossEncoder，None 则按 score 排序
    neo4j_driver: Optional[Any]
    is_ingesting: bool
    collection_lock: Lock           # 防并发写冲突
    neo4j_lock: Lock
```

**`FallbackLLMClient`**：包装主/备两个 OpenAI 兼容客户端，主客户端抛异常时自动切换备用。接口与 `openai.OpenAI` 完全相同（`client.chat.completions.create(...)`）。Vision 调用必须直接使用 `minimax_client`，因为 SiliconFlow 不支持多模态。

### 7.3 `backend/embedding_manager.py` — 双模型管理

```python
class EmbeddingManager:
    encode_text(texts) → np.ndarray(N, 1024)      # bge-m3，normalize
    encode_texts_clip(texts) → np.ndarray(N, 1024) # Chinese-CLIP 文本编码器
    encode_images_clip(images) → np.ndarray(N, 1024) # Chinese-CLIP 图片编码器
    zero_image_vec() → List[float]                 # [0.0]*1024，文本块占位
```

**为什么同一个 1024 维可以用两个不同模型？**
bge-m3 和 Chinese-CLIP vit-large-patch14 的输出维度恰好相同，因此 Qdrant Collection 的 `text_vec` 和 `image_vec` 索引参数完全一致。两者训练目标不同：bge-m3 优化文本语义相似度，Chinese-CLIP 优化图文跨模态对齐。

### 7.4 `backend/image_captioner.py` — Vision Caption

```python
def describe_image(client, model, image_path, context_text="") -> str
```

- 读取图片 → base64 编码 → MiniMax M2.5 Vision API
- Prompt：请用中文详细描述这张图片内容，包括图中展示的结构、部件名称、工作原理或数据...
- `context_text` 是图片所在页面的前 200 字，帮助 Caption 更准确
- 失败返回 `""`，调用方跳过该图片块（不中断入库）

### 7.5 `backend/routers/ingest.py` — 入库

**核心流程（`_do_ingest`）**：
```
对每个文件：
  1. process_document(file_path) → 文本块 + 图片块列表
  2. 增量删旧（Qdrant FilterSelector by doc_id）
  3. 文本块：encode_text → text_vec；zero_image_vec → image_vec
  4. 图片块：describe_image → caption → encode_text → text_vec；
             encode_images_clip → image_vec
  5. PointStruct(id=uuid5(doc_id_chunk_i), vector={...}, payload={...})
  6. qdrant_client.upsert(points=batch, batch_size=32)
  7. yield 完整日志快照（SSE 覆盖式显示）
```

**增量更新原理**：每个文件的 `doc_id = sha256(filename)[:16]`，删旧时用 Qdrant Filter 按 `doc_id` payload 字段匹配删除，然后重新插入。幂等安全。

**Point UUID**：`str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{doc_id}_{i}"))` — 确定性生成，同文件同块号永远得到相同 UUID，避免重复插入。

### 7.6 `backend/routers/retrieve.py` — 双路检索

```python
def qdrant_search_text(qdrant_client, embedding_mgr, query, n) -> List[dict]:
    # bge-m3 编码 → query_points(using="text_vec")
    # 返回文本块 + Caption 块

def qdrant_search_image(qdrant_client, embedding_mgr, query, n) -> List[dict]:
    # Chinese-CLIP 文本编码 → query_points(using="image_vec")
    # query_filter: chunk_type == "image"，只返回图片块

def merge_and_dedup(text_results, image_results) -> List[dict]:
    # 按 Point UUID 去重，相同 ID 保留 score 更高的版本
    # 按 score 降序排列（余弦相似度越高越相关）
```

**`POST /retrieve`** 完整流程：
1. 路径1：`qdrant_search_text`（召回3×top_k，上限20）
2. 路径2：`qdrant_search_image`（召回top_k）
3. 合并去重 → CrossEncoder 精排 → 取 top_k
4. 返回 `ChunkResult`（含 `chunk_type`、`image_url`）

### 7.7 `backend/routers/chat.py` — 多查询 RAG 问答

**四阶段流程（全部为 SSE 流）**：
1. **多查询生成**（静默）：调 LLM 生成 2 个额外查询角度，扩大召回覆盖
2. **双路多查询检索**（静默）：对所有查询分别执行 text+image 双路检索，合并去重
3. **CrossEncoder 重排**（静默）：对候选块精排，取 Top-4
4. **LLM 流式生成**：边生成边 yield，最后附带来源脚注和图片 URL

**`_IMAGES_SEP`（`\n\n[__IMAGES__]`）协议**：最后一次 yield 在文本末尾附加此分隔符和 JSON 序列化的 `image_urls`，由 `sse.py` 的 done 帧解析逻辑拆分后透传前端。

### 7.8 `backend/sse.py` — SSE 协议

| 函数 | 用途 | 帧格式 |
|------|------|--------|
| `log_gen_to_sse(gen)` | 日志类（入库/评估） | `{"log": "完整日志快照"}` / `[DONE]` |
| `chat_gen_to_sse(gen)` | 聊天类（问答） | `{"delta": "..."}` + `{"done":true,"sources_md":"...","image_urls":[...]}` |

聊天流的帧分两类：中间帧发 `delta`（前端追加），最后帧发 `done`（前端解析来源脚注和图片列表）。

---

## 8. 图文检索详解

### 8.1 PDF 图片提取（`main_ingest.py`）

```python
def extract_images_from_pdf(file_path, output_dir, min_width=100, min_height=100):
    # page.get_images(full=True) → img_info
    # doc.extract_image(xref) → {image:bytes, width, height, ext}
    # 过滤 < 100×100 像素（装饰图/图标/线条）
    # 保存：{basename}_p{page}_img{idx}.{ext}
    # 提取页面前200字作为 context_text（提升 Caption 质量）
```

**过滤阈值 100×100**：经验值，能过滤掉页眉装饰、分隔线等噪声，同时保留正文插图（通常 > 200×200）。

### 8.2 以图搜文流程（前端驱动）

```
用户在前端上传图片
    → POST /vision/describe（图片 → MiniMax Vision → 中文描述）
    → 前端拼接：[图片内容：{description}] + 用户补充说明
    → POST /chat（正常走 bge-m3 文字检索流程）
```

**为什么这样设计？**
直接用 Chinese-CLIP 图片编码搜文本向量在跨模态时效果不稳定。先用 Vision LLM 把图片"翻译"成文字描述，再走 bge-m3 文字检索，效果更可控，且不依赖 CLIP 模型的中文语料质量。

### 8.3 文字查图流程（自动）

`/chat` 的每次双路检索自动包含：
```
Chinese-CLIP 文本编码器（query）→ Qdrant image_vec 搜索
    → 返回图片块（chunk_type="image"）
    → image_url = /images/{filename}
    → done 帧中 image_urls 数组
    → 前端回答下方展示图片缩略图
```

### 8.4 `/vision/search` — 纯 CLIP 以图搜图

```
用户上传图片
    → Chinese-CLIP 图片编码器 → image_vec
    → Qdrant query_points(using="image_vec", filter: chunk_type=="image")
    → 返回最相关的图片块（含 Caption 和 image_url）
```

无需 Vision LLM，纯向量匹配，速度快。用于"找与这张图相似的图"场景。

---

## 9. BOM-GraphRAG 扩展

### 9.1 功能概述

在 RAG 问答基础上，追加 Neo4j 图数据库存储发动机 BOM（物料清单）。装配方案问答同时查询：
- **Neo4j**：根据零件名/模块名递归查询子零件树
- **Qdrant 知识库**：查相关技术规范和工艺要求
- **融合 Prompt**：BOM 数据 + 技术知识 → LLM 生成装配方案

### 9.2 BOM 表格式规范

Excel 文件必须包含以下列：

| 列名 | 类型 | 示例 |
|------|------|------|
| `level_code` | 字符串（`.` 分隔层级） | `1.2.1` |
| `part_id` | 字符串（唯一主键） | `HPT-D01` |
| `part_name` | 字符串 | `涡轮盘` |
| `part_name_en` | 字符串 | `Turbine Disk` |
| `category` | `Assembly` / `Part` / `Standard` | `Part` |
| `qty` | 整数 | `80` |
| `unit` | 字符串 | `件` |
| `material` | 字符串（可空） | `GH4169` |
| `weight_kg` | 浮点（可空） | `42.0` |
| `spec` | 字符串（可空） | `φ520×120 mm` |
| `note` | 字符串（可空） | `粉末冶金盘` |

**层级规则**：`1.2.1` 的父节点为 `1.2`，`bom_ingest.py` 自动建立 `CHILD_OF` 关系。

### 9.3 Neo4j 图模型

```
(涡扇发动机:Assembly {part_id:"ENG-001"})
    └─[:CHILD_OF]─(高压涡轮模块:Assembly {part_id:"HPT-000"})
                       ├─[:CHILD_OF]─(涡轮盘:Part {material:"GH4169"})
                       └─[:CHILD_OF]─(涡轮叶片:Part {qty:80, material:"DD6"})
```

递归查询整棵子树（Cypher）：
```cypher
MATCH (n)-[:CHILD_OF*]->(root {part_id: "HPT-000"}) RETURN n
```

### 9.4 Neo4j Docker 快速启动

```bash
docker run -d --name neo4j -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password neo4j:5-community

# 后续重启
docker start neo4j

# Web 可视化
# http://localhost:7474（用户名 neo4j，密码 password）
```

---

## 10. React 前端详解

### 10.1 技术栈

| 层级 | 选型 |
|------|------|
| 框架 | React 18 + TypeScript |
| 构建 | Vite（`npm run dev` → `:5173`） |
| 样式 | Tailwind CSS v4（`@tailwindcss/vite` 插件） |
| Markdown 渲染 | react-markdown + remark-gfm |

### 10.2 POST SSE 实现

浏览器原生 `EventSource` 只支持 GET；所有聊天/入库接口是 POST，因此用 `fetch + ReadableStream`：

```
fetch(url, {method:'POST', body:JSON.stringify(...)})
  → res.body.getReader()
  → 循环 read() → TextDecoder → 按 \n 拆行
  → 找 "data: " 前缀 → JSON.parse(payload)
  → yield SseFrame
```

日志类流（`usePostSSE`）：每帧覆盖显示 `frame.log`
聊天类流（`useChat`）：中间帧追加 `frame.delta`，done 帧解析 `sources_md` 和 `image_urls`

### 10.3 图片上传（`RagChat.tsx`）

- **📷 按钮**：点击触发 `<input type="file" accept="image/*">`
- **粘贴**：`onPaste` 事件从剪贴板 `items` 中提取 `image/*` 类型
- **发送流程**：`pendingImage` 存在时，先调 `postVisionDescribe(file)` 获取描述，拼入消息前缀 `[图片内容：{description}]`，再正常走 `/chat`
- **图片展示**：`useChat` 返回 `imageUrls`，回答完成后在来源脚注下方渲染缩略图（点击新标签页放大）

### 10.4 Vite 代理

`vite.config.ts` 中 `/api/*` → `http://localhost:8000`，前端无需处理 CORS。

---

## 11. 配置系统（.env）

```env
# ===== LLM 备用（SiliconFlow，必填）=====
LLM_API_KEY=sk-xxx
LLM_BASE_URL=https://api.siliconflow.cn/v1
LLM_MODEL=Qwen/Qwen2.5-14B-Instruct

# ===== MiniMax（主 LLM + Vision，可选但推荐）=====
# 配置后：LLM 优先走 MiniMax，失败自动 fallback 到 SiliconFlow
# Vision 功能（图片 Caption + 以图搜文）必须配置此项
MINIMAX_API_KEY=your_minimax_key
MINIMAX_BASE_URL=https://api.minimaxi.com/v1
MINIMAX_MODEL=MiniMax-M2.5

# ===== Neo4j（BOM 装配方案，可选）=====
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASS=password
```

**不配置 MINIMAX_API_KEY 的影响**：
- 图片 Caption 生成不可用 → PDF 中的图片块被跳过，只入库文本块
- 前端图片上传后的以图搜文功能返回 503 错误
- 文字查图功能仍可用（如果之前入库过图片块的话）

---

## 12. 运行方式

### 12.1 首次环境准备

```bash
# 1. 创建 conda 环境
conda create -n rag_demo python=3.10
conda activate rag_demo

# 2. 安装依赖
PYTHONUTF8=1 pip install -r requirements.txt

# 3. 配置密钥
cp .env.example .env
# 编辑 .env，填写 API Key

# 4. 前端依赖
cd frontend && npm install && cd ..
```

### 12.2 启动服务

```bash
# 终端1：启动 FastAPI 后端
PYTHONUTF8=1 python run_backend.py
# 或：PYTHONUTF8=1 uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# 终端2：启动 React 前端
cd frontend && npm run dev
# 访问 http://localhost:5173
```

### 12.3 知识库入库

**方式 A：通过前端**（推荐）
在 React 界面 → "知识库" Tab → 点击"开始入库"按钮，日志实时显示。

**方式 B：命令行**
```bash
# 增量入库（已入库的文件不重复处理）
PYTHONUTF8=1 python main_ingest.py

# 清空后完整重建
PYTHONUTF8=1 python main_ingest.py --clear

# 只处理文本（跳过图片提取，无 MiniMax 时使用）
PYTHONUTF8=1 python main_ingest.py --no-image
```

### 12.4 扫描版 PDF 预处理

```bash
# 先用 MinerU OCR 转 Markdown（首次需下载模型 ~2-4GB）
PYTHONUTF8=1 python pdf_to_md.py
# 生成 data/{书名}.md 后，再执行 main_ingest.py 入库
```

### 12.5 BOM 数据入库

```bash
# 入库 data/test_bom.xlsx
PYTHONUTF8=1 python bom_ingest.py

# 指定文件
PYTHONUTF8=1 python bom_ingest.py --file data/my_bom.xlsx

# 清空重建
PYTHONUTF8=1 python bom_ingest.py --clear
```

---

## 13. 常见问题与排查

### Q: 后端启动时 `ModuleNotFoundError: No module named 'qdrant_client'`
```bash
pip install qdrant-client>=1.11
```

### Q: Chinese-CLIP 模型首次加载很慢
首次运行自动从 HuggingFace 下载 `OFA-Sys/chinese-clip-vit-large-patch14`（约 2GB），国内网络慢可设置：
```bash
export HF_ENDPOINT=https://hf-mirror.com
```

### Q: 图片 Caption 生成失败（"Caption 失败，跳过"）
检查 `.env` 中 `MINIMAX_API_KEY` 是否正确配置，以及 MiniMax API 配额是否充足。无 Caption 的图片块会被跳过（不影响文本块入库）。

### Q: Qdrant `collection_exists` 返回 False 但数据库文件存在
`QDRANT_DB_PATH` 是一个**目录**（不是单文件），路径为 `storage/qdrant.db/`。初始化时用 `os.makedirs(db_path, exist_ok=True)`，不要当成文件处理。

### Q: `GET /images/xxx.png` 返回 404
检查 `storage/images/` 目录是否存在。FastAPI `StaticFiles` 挂载依赖该目录在启动前存在，`backend/main.py` 的 `lifespan` 中已有 `os.makedirs(IMAGE_STORAGE_DIR, exist_ok=True)`。

### Q: Reranker 加载失败
CrossEncoder 约 280MB，加载失败时系统自动降级为按余弦相似度排序，不影响正常使用。如需使用：
```bash
pip install sentence-transformers
# 首次使用自动下载 BAAI/bge-reranker-base
```

### Q: Windows 路径中文乱码
所有 Python 命令前加 `PYTHONUTF8=1`：
```bash
PYTHONUTF8=1 python run_backend.py
```

---

## 14. 变更日志

| 日期 | 变更内容 |
|------|----------|
| 2026-03-06 | 初始化项目：架构设计、deepdoc 集成、ChromaDB 入库 |
| 2026-03-06 | MinerU pipeline 替换 pymupdf4llm，支持扫描版 PDF OCR |
| 2026-03-09 | `eval_rag.py`：RAG 性能评估（召回诊断 / LLM-as-Judge / RAGAS） |
| 2026-03-09 | MiniMax 主备 LLM 支持（`FallbackLLMClient`） |
| 2026-03-12 | BOM-GraphRAG：`bom_ingest.py`（BOM→Neo4j）、`data/test_bom.xlsx`（47条涡扇发动机测试数据） |
| 2026-03-18 | **FastAPI 后端重构**：`backend/` 目录，12 个 REST+SSE 接口 |
| 2026-03-18 | **React 前端**：Vite + React 18 + TypeScript + Tailwind CSS v4，全面替代 Gradio |
| 2026-03-20 | **图文检索重构**：向量库 ChromaDB → **Qdrant**（Windows 本地文件，无需 Docker）；`EmbeddingManager`（bge-m3 + Chinese-CLIP 双模型）；`image_captioner.py`（MiniMax Vision Caption）；`/vision/*` 路由；多查询+双路向量检索+CrossEncoder 重排；前端图片上传/粘贴/以图搜文/图片展示 |
| 2026-03-20 | 清理过时文件：删除 `app.py`（Gradio UI）、`main_chat.py`、`eval_rag.py`、`assembly_agent.py`（已全部由 FastAPI + React 替代） |
