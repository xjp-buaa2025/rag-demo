# 面向航空发动机装配工艺的多模态 GraphRAG 知识问答系统

> **课题定位**：跨学科科研课题报告
> **英文题目**：A Multimodal GraphRAG Knowledge Question-Answering System for Aero-Engine Assembly Processes
> **关键词**：检索增强生成 (RAG) · 知识图谱 · 多模态检索 · 航空发动机装配 · 大语言模型工业应用

---

## 一、课题基本情况

### 1.1 选题背景

航空发动机被誉为"工业皇冠上的明珠"，其装配工艺具有 **零件众多、精度严苛、知识密集** 三大特征：以典型涡扇发动机为例，整机零件约 2 万件、装配工序数百道，技术要求散落于 BOM（Bill of Materials，物料清单）、CAD 三维模型、维修手册（IPC/MM/CMM）、ATA 规范等多源异构资料中。一线装配/维护人员的"查资料—找零件—定工序"过程严重依赖个人经验，存在 **检索效率低、知识跨文档难关联、新人培训周期长** 等痛点。

近年来检索增强生成（Retrieval-Augmented Generation, RAG）技术的兴起，为大语言模型（LLM）注入领域知识提供了通用范式。然而，将通用 RAG 直接迁移到航空装配场景面临三大挑战：

1. **图文混排难处理**：装配手册中爆炸图、装配示意图、表格与正文紧耦合，纯文本检索无法召回图形语义；
2. **结构化与非结构化知识割裂**：BOM 层级是结构化图，工艺规范是非结构化文本，传统 RAG 仅消费后者；
3. **领域术语歧义重**：例如"盘"可指涡轮盘 / 压气机盘 / 风扇盘，缩写"HPC""HPT""LPT"语义上下文敏感，简单向量召回易漂移。

### 1.2 课题目标

研制一套 **本地化部署、面向航空发动机装配工艺的多模态 GraphRAG 知识问答系统**，能够：

- **回答装配工艺问题**：自然语言提问 → 给出有序工序、工具清单、技术规范、注意事项；
- **支持图文双向检索**：文字查文档 / 文字查图 / 以图搜图 / 以图搜文 四种模态；
- **三源知识融合**：将维修手册（PDF）、零件 BOM（Excel/PDF）、CAD 三维模型（STEP）统一进入知识库与图谱；
- **完全本地化**：Embedding/向量库/图数据库全部本地，仅 LLM 推理可走远端 API（满足国防敏感场景的合规要求）。

### 1.3 拟解决的科学问题

| 编号 | 科学问题 |
|------|----------|
| Q1 | 在工业图文混排文档中，如何同时编码文字语义与图形语义，使"文字查图""以图搜文"等跨模态检索具有可用精度？ |
| Q2 | 在 BOM 结构化层级与维修手册非结构化文本并存的条件下，如何构建统一的领域知识图谱并在问答时联合推理？ |
| Q3 | 在装配工艺这类强序约束领域中，如何利用图谱拓扑（如 `precedes` 关系）保证 LLM 输出的工序具有 DAG 一致性？ |
| Q4 | 在领域术语高度歧义的条件下，如何通过多查询扩展 + 稀疏密集混合检索 + 跨编码器精排，逼近"零样本"领域问答的人类专家水平？ |

---

## 二、研究内容与技术路线

### 2.1 系统总体架构

```
┌────────────────────────────────────────────────────────────────────┐
│ 前端交互层  React 19 + TypeScript + Vite + Tailwind CSS v4         │
│ —— 统一聊天 / 知识库管理 / 图谱构建 / D3 力导向图谱可视化 / 评估面板 │
└─────────────────────────────┬──────────────────────────────────────┘
                              │ POST + Server-Sent Events (SSE)
┌─────────────────────────────▼──────────────────────────────────────┐
│ 服务编排层  FastAPI + LangChain + LangGraph                        │
│ —— 入库管道 / 检索管道 / KG 四阶段管道 / RAG Agent (Tool 调用)      │
└─────────────────────────────┬──────────────────────────────────────┘
                              │
   ┌──────────────────────────┼──────────────────────────────────┐
   ▼                          ▼                                  ▼
┌──────────┐         ┌──────────────────┐              ┌──────────────────┐
│ 向量库    │         │ 知识图谱 (Neo4j) │              │ LLM 推理         │
│ Qdrant   │         │ 7 类节点 ×       │              │ MiniMax M2.5     │
│ 双向量    │         │ 9 类关系         │              │ ↓ failover       │
│ text/img │         │ +DAG 校验        │              │ SiliconFlow/vLLM │
└──────────┘         └──────────────────┘              └──────────────────┘
   ▲                          ▲                                  ▲
   │                          │                                  │
┌──┴──────────────────────────┴──────────────────────────────────┴─┐
│ 三源数据层                                                        │
│ [维修手册 PDF/MD]   [零件 BOM xlsx/pdf/docx]   [CAD STEP 模型]    │
└──────────────────────────────────────────────────────────────────┘
```

### 2.2 数据层与知识抽取

#### 2.2.1 维修手册（非结构化）

- **解析引擎**：双轨并存
  - 方案 A — `MinerU CLI`（DocLayout-YOLO 版面识别 + PaddleOCR + UniMERNet 公式识别）：批量将含 LaTeX 公式的学术 PDF 离线转 Markdown；
  - 方案 B — `RAGFlow deepdoc`（YOLOv10 版面 + ONNX 表格→HTML + PaddleOCR）：技术手册/图表实时管道处理，大 PDF 自动分批 50 页防 OOM。
- **结构感知切块**：按 ATA 章节（如 `72-30-00`）、表格、`WARNING/CAUTION/NOTE`、编号步骤五级优先级切分，块软上限约 1600 字符；
- **图形提取与描述**：`PyMuPDF.page.get_images()` 抽取图形 → MiniMax Vision 生成中文 Caption（含航空技术图专用提示词）→ 双路向量化入库。

#### 2.2.2 零件 BOM（结构化）

- 支持 `.xlsx / .csv / .pdf / .docx`，PDF/DOCX 经 `pdfplumber + LLM` 自动转标准 BOM JSON；
- **职责分离架构**（v2，2026-04-20）：LLM 仅做忠实抽取（不推断层级），随后由确定性规则 `_apply_ipc_hierarchy` 填充 `parent_id`（R0–R5 五条规则），ROOT 误归率从 51% 降至 0.5%；
- **OCR 净化**：正则字典 (`COMP0NENT→COMPONENT, 0F→OF, 0VS→OVERSIZE …`) 修复 OCR 数字字母混淆。

#### 2.2.3 CAD 三维模型（几何拓扑）

- 使用 `pythonocc-core`（Open CASCADE 内核）解析 STEP 文件：
  - `cad_assembly_tree`：嵌套装配层级；
  - `cad_constraints`：配合约束（`{part_a, part_b, constraint_type}`）；
  - `cad_adjacency`：空间邻接（gap_mm < 2 mm 视为相邻）；
- 经 `cad_to_kg_triples` 节点转为 `isPartOf / matesWith / adjacentTo` 三类图三元组。

### 2.3 知识图谱层（KG Schema）

在 BOM 基础层（`CHILD_OF`）之上叠加结构化装配知识图谱，设计 **7 类节点 × 9 类关系**：

| 节点类型 | 主要属性 | 来源 |
|----------|----------|------|
| `Part` / `Assembly` | `part_id, part_name, material, quantity, function` | BOM + CAD |
| `Procedure` | `kg_id, kg_name, seq_no, ata_section, source_chunk_id` | 维修手册 LLM 抽取 |
| `Tool` | `kg_id, kg_name, tool_type` | 维修手册 LLM 抽取 |
| `Specification` | `kg_id, spec_type, spec_value, spec_unit` | 维修手册 LLM 抽取 |
| `Interface` | `kg_id, iface_type, description` | CAD 配合约束 |
| `GeoConstraint` | `kg_id, constraint_type, value` | CAD 几何约束 |

**9 类关系**：`isPartOf / precedes / participatesIn / requires / specifiedBy / matesWith / adjacentTo / hasInterface / constrainedBy`，覆盖装配层级、工序时序、零件—工序—工具—规范的多元关联。

**核心方法**：

1. **Gleaning 两轮抽取**（借鉴 GraphRAG）：第一轮 LLM 抽取，第二轮以已识别实体摘要为上下文再抽，提升召回 20–40%；
2. **三级实体对齐级联**：① 规则词典（航空缩写 + BOM 精确匹配，~70%）→ ② `difflib.SequenceMatcher.ratio() ≥ 0.85` 模糊匹配（~20%）→ ③ bge-m3 语义向量召回 + 反向匹配（~9%）；
3. **DAG 校验**：Kahn 算法检测 `precedes` 关系成环并自动断环，保证装配序列拓扑可排序；
4. **三元组后处理流水线**（置信度过滤 ≥0.3 → 名称归一化 → 本体约束校验 → 去重）：690 → 498 条，清除率 27.8%；
5. **黄金三元组基准集**：人工精读 P&W Canada 维修手册 3013242 第 72-30 章，构建 108 实体 / 99 三元组 / 7 类节点 × 9 类关系的评测金标，作为 KG 召回率/精度评估基线。

### 2.4 检索与生成层

```
用户问题
   ├─[LLM]→ 多查询扩展（额外 2 个角度，缓解航空术语歧义）
   ↓
   ├─ Dense 检索：bge-m3(query) → Qdrant text_vec    Top-N
   └─ Sparse 检索：jieba+regex 双轨分词 → BM25Okapi   Top-2N
                       ↓
                Reciprocal Rank Fusion (k=60)
                       ↓
   ├─ Cross-modal：Chinese-CLIP → Qdrant image_vec    Top-N/2（图片块）
                       ↓
            Cross-Encoder 精排（bge-reranker-base） → Top-K
                       ↓
   [GraphRAG 路径] _query_procedure_chain：
     问题关键词 → Cypher MATCH (Procedure) -[:precedes*..5]-> ...
     OPTIONAL MATCH Tool / Specification → Kahn 拓扑排序
                       ↓
   上下文优先级注入：[1] KG 有序工序 > [2..N] BOM 实体 > [N+1..] RAG 文本块
                       ↓
   LLM 流式生成（SSE：stage 帧 → delta 帧 → done 帧含 sources/image_urls）
```

### 2.5 工程化能力

- **SSE 阶段化进度反馈**：`stage` 帧（多查询 / 检索 / 重排 / 生成）+ 大型 PDF 分批进度（`queue.Queue` 侧信道，每 50 页推送）；
- **LangGraph 多步骤管道**：RAG / BOM / CAD / KG 四条独立 StateGraph，每节点独立可观测；
- **KG 四阶段独立端点**：`/kg/stage1/bom`、`/kg/stage2/manual`、`/kg/stage3/cad`、`/kg/stage4/validate` + `/kg/stages/sync-neo4j`，中间产物落 JSON 便于人工审查与论文取证；
- **主备 LLM 自动降级**：`FallbackLLMClient` 包装 MiniMax → SiliconFlow，Vision 调用专走原始 MiniMax 客户端；
- **D3 力导向图可视化**：`/bom/kg/graph` 端点 + 7 节点配色 / 9 关系配色 / 拖拽缩放 / 邻居高亮。

---

## 三、关键技术与创新点

| # | 创新点 | 学术价值 |
|---|--------|----------|
| C1 | **图文双向量统一存储**：同一 Qdrant Point 命名多向量（`text_vec` 1024 维 bge-m3 + `image_vec` 768 维 Chinese-CLIP），单次检索同时召回文字与图形 | 在航空装配这一图文密集领域首次实现"四向跨模态"检索 |
| C2 | **三源异构知识联合图谱**：BOM（人工层级） + 维修手册（LLM 抽取） + CAD（几何拓扑）→ Neo4j 统一图谱，通过 `REPRESENTED_BY` 边连接 BOM 节点与 KG 节点，避免孤岛 | 解决了工程领域"结构化与非结构化知识如何联合推理"的开放问题 |
| C3 | **职责分离的 BOM 层级算法**：LLM 只抽取，规则只填层级，五条 IPC 规则 (R0–R5) + 栈算法层级守卫，将 ROOT 错归率从 51% → 0.5% | 提供了 LLM 与符号规则在工业知识抽取中的协同范式 |
| C4 | **DAG 校验 + 拓扑排序的有序工序输出**：Kahn 算法保证 `precedes` 无环，问答时按拓扑序注入"有序工序链" | 解决了装配工艺这类强序领域 LLM 输出乱序的问题 |
| C5 | **多查询 + 稀疏密集混合 + Cross-Encoder 三层精排**：针对航空术语歧义，BM25Okapi（jieba + regex 双轨分词，连字符子 token 扩展） + bge-m3 + RRF + bge-reranker | 通用 RAG 优化在专业领域的端到端落地实证 |
| C6 | **完全本地化 Embedding + 主备 LLM 降级**：bge-m3 / Chinese-CLIP / Reranker 全本地，LLM 走 OpenAI 兼容协议主备切换 | 兼顾国防敏感场景合规与生产可用性 |
| C7 | **黄金三元组基准集（108 实体 / 99 三元组）**：人工精读 P&W 维修手册产出，覆盖 7 类节点 × 9 类关系 | 为航空装配领域 KG 抽取算法提供可复现的评测基线 |

---

## 四、涉及的专业知识体系

本课题处于 **人工智能、软件工程、航空制造** 三大学科交叉处，主要涉及以下专业方向：

### 4.1 计算机科学与人工智能

- **自然语言处理（NLP）**：分词（jieba）、tokenization（tiktoken）、稀疏检索（BM25Okapi）、密集检索（Sentence-BERT 范式）、跨编码器精排
- **大语言模型（LLM）**：Prompt 工程（含 few-shot）、Tool Use / Function Calling、Vision LLM 多模态、流式生成（SSE）、主备降级
- **检索增强生成（RAG）**：Naive / Advanced / Modular RAG 范式，多查询扩展、混合检索（RRF）、Reranking、GraphRAG / Hybrid RAG
- **多模态学习**：CLIP 系列跨模态对比学习、图文统一表示、零样本图像描述
- **知识图谱**：本体设计（Schema）、实体链接、关系抽取、Gleaning 多轮抽取、图查询语言（Cypher）
- **图算法**：Kahn 拓扑排序、DAG 检测、力导向布局（Fruchterman-Reingold）

### 4.2 软件工程与系统架构

- **后端**：FastAPI、SSE、LangChain（7 大组件：Models/Prompts/Chains/Memory/Tools/Agents/Retrievers）、LangGraph StateGraph、依赖注入
- **前端**：React 19、TypeScript、Vite、Tailwind v4、D3.js v7（力导向图）、`fetch + ReadableStream` 实现 POST SSE
- **数据库**：向量库（Qdrant 双向量）、图数据库（Neo4j Cypher）、稀疏索引持久化（pickle + 启动重建）
- **DevOps**：Docker（Neo4j）、conda 环境管理、UTF-8 跨平台兼容（PYTHONUTF8）

### 4.3 文档智能与计算机视觉

- **文档解析**：DocLayout-YOLO / YOLOv10 版面识别、PaddleOCR、UniMERNet 数学公式识别、ONNX 表格识别
- **图像处理**：PyMuPDF 图像抽取、PIL/numpy 图像统一、CLIP 视觉编码

### 4.4 计算几何与 CAD

- **STEP 文件解析**：ISO 10303-21 标准、Open CASCADE 内核 (`pythonocc-core`)
- **装配建模**：装配树、配合约束（`mate / contact / fixed`）、空间邻接（gap 距离）

### 4.5 航空发动机装配工艺（领域知识）

- **航空规范**：ATA 100 章节体系（72 章为发动机）、IPC（图解零件目录）、MM/CMM（维修/部件维修手册）
- **装配工艺**：BOM 层级、ATTACHING PARTS 子件挂载、INTRCHG 互换件、PRE/POST-SB 服务通告
- **典型对象**：涡扇发动机（PT6A、压气机模块、HPT/LPT 等），扭矩规范（如 50±2 N·m）、材料代号（GH4169 等）

---

## 五、预期成果与验证方案

### 5.1 系统级成果

- **可运行原型系统**：完整 React + FastAPI 双端，本地一键启动；
- **三源知识库**：基于 P&W Canada PT6A 系列维修手册 / BOM / 公开 CAD 模型构建；
- **黄金评测集**：108 实体 / 99 三元组人工金标，公开供学界复现。

### 5.2 评估指标

| 任务 | 指标 |
|------|------|
| 文本检索 | Recall@K (K=5,10)、MRR、NDCG |
| 跨模态检索（文→图） | Recall@K、人工相关性评分 |
| KG 抽取 | 实体 P/R/F1、关系 P/R/F1（对照黄金集） |
| 装配问答 | RAGAS（faithfulness/answer_relevancy/context_relevancy）+ LLM 打分 + 领域专家人工评审 |
| 工序拓扑一致性 | DAG 合规率（无环占比）、工序顺序 Kendall τ 系数 |

### 5.3 对比实验设计

| 基线 | 配置 |
|------|------|
| B1 | 纯文本 RAG（bge-m3 + Qdrant） |
| B2 | + 多查询扩展 |
| B3 | + BM25 混合检索（RRF） |
| B4 | + Cross-Encoder 重排 |
| B5 | + 多模态（Chinese-CLIP） |
| **Full** | **B5 + GraphRAG（KG 三源融合 + 工序链注入）** |

### 5.4 拟投稿方向

- 中文核心：《计算机集成制造系统》《航空制造技术》《机械工程学报》
- 国际期刊/会议：CIRP Annals、Journal of Manufacturing Systems、ACM MM Industrial Track、CSCWD

---

## 六、关键风险与应对

| 风险 | 影响 | 应对策略 |
|------|------|----------|
| 维修手册多为受控文档，公开数据有限 | 评测样本不足 | 使用 P&W Canada 公开手册 + 仿真 BOM；与企业合作获取脱敏数据 |
| LLM 抽取召回率不稳定 | KG 质量受限 | Gleaning 两轮 + 三级实体对齐 + 三元组后处理流水线 + 黄金集驱动迭代 |
| 大型 PDF（500+ 页）解析 OOM | 入库失败 | 分批 50 页 + Queue 侧信道实时进度 + fitz fallback 三层降级链 |
| Vision LLM 对工程图理解能力有限 | 图片 Caption 质量参差 | 航空技术图专用提示词 + 失败块跳过不阻塞文本入库 |
| 远端 LLM API 不稳定 | 服务中断 | `FallbackLLMClient` 主备双客户端自动降级，可切本地 vLLM |

---

## 七、参考文献（节选）

1. Lewis P. et al. *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*. NeurIPS 2020.
2. Gao Y. et al. *Retrieval-Augmented Generation for Large Language Models: A Survey*. arXiv:2312.10997, 2023.
3. Edge D. et al. *From Local to Global: A Graph RAG Approach to Query-Focused Summarization*. Microsoft Research, 2024.
4. *Document GraphRAG: Knowledge Graph Enhanced RAG for Document QA Within the Manufacturing Domain*. MDPI Electronics, 2024.
5. *An Intelligent Guided Troubleshooting Method for Aircraft Based on HybridRAG*. Nature Scientific Reports, 2025.
6. *AI-based Decision-making System for Tooling Design of Aircraft Product Assembly with Developed Knowledge Retrieval Algorithm*. Nature Scientific Reports, 2025.
7. *The Joint Knowledge Reasoning Model Based on Knowledge Representation Learning for Aviation Assembly Domain*. Science China Technological Sciences, 2023.
8. *CAMB: A Comprehensive Industrial LLM Benchmark on Civil Aviation Maintenance*. arXiv:2508.20420, 2025.
9. Yang A. et al. *Chinese CLIP: Contrastive Vision-Language Pretraining in Chinese*. arXiv:2211.01335, 2022.
10. Chen J. et al. *BGE M3-Embedding: Multi-Lingual, Multi-Functionality, Multi-Granularity Text Embeddings Through Self-Knowledge Distillation*. ACL 2024.

---

*本课题报告基于 `rag-demo` 工程实现整理，工程演进详见 `PROJECT_GUIDE.md` 第 15 章变更日志。*
