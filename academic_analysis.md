# 航空发动机装配工艺领域 RAG 系统 — 学术价值分析与论文参考

## 一、系统学术定位

本系统是一个面向**航空发动机装配工艺**领域的**多模态 GraphRAG 知识问答系统**，在学术上处于以下三个研究方向的交叉点：

```
多模态检索增强生成 (Multimodal RAG)
        ╲
         ╲
知识图谱增强问答 (GraphRAG)  ──→  航空发动机智能装配
         ╱
        ╱
工业领域大模型应用 (Industrial LLM)
```

## 二、核心技术创新点（可写入论文的贡献）

### 创新点 1：图文双路检索融合架构
- bge-m3（文本语义 1024 维） + Chinese-CLIP（跨模态 768 维）双向量
- 同一 Qdrant Point 存储命名多向量，支持"文字查文档"和"文字查图片"
- **学术意义**：现有工业 RAG 多为纯文本，本系统首次在航空装配领域引入图文跨模态检索，可召回 PDF 中的结构示意图、装配示意图

### 创新点 2：结构化 BOM 图谱 + 非结构化知识库融合问答
- Neo4j 存储 BOM 零件层级（83 个节点，CHILD_OF 关系）
- 装配问答时并行查询 Neo4j（零件清单）+ Qdrant（工艺知识）
- LLM 融合两路信息生成装配方案
- **学术意义**：解决了工程领域"结构化数据与非结构化文档如何联合推理"的开放问题

### 创新点 3：面向航空发动机的多查询+重排序检索优化
- 多查询生成（LLM 从不同角度重述问题）→ 双路并行检索 → CrossEncoder 精排
- **学术意义**：Dense Retrieval + Multi-Query + Reranking 三层融合，专门针对航空发动机术语多义性（如"盘"可指涡轮盘、压气机盘、风扇盘）

### 创新点 4：全本地化部署 + 领域知识安全
- Embedding 完全本地（bge-m3 + Chinese-CLIP），不经过外部 API
- **学术意义**：航空发动机属于国防敏感领域，本地化部署有合规价值

## 三、高度相关论文（按相关度排序）

### A. 直接对标（制造/航空 + RAG/知识图谱）

| # | 论文 | 发表 | 年份 | 与本系统的关系 |
|---|------|------|------|---------------|
| 1 | **Document GraphRAG: Knowledge Graph Enhanced RAG for Document QA Within the Manufacturing Domain** | MDPI Electronics | 2024 | **最直接对标**：制造业文档 QA 中融合知识图谱与 RAG，与本系统的 Neo4j BOM + Qdrant 架构高度一致 |
| 2 | **An intelligent guided troubleshooting method for aircraft based on HybridRAG** | Nature Scientific Reports | 2025 | 航空故障排查的混合 RAG 框架，融合知识图谱和 LLM 多维检索 |
| 3 | **AI based decision-making system for tooling design of aircraft product assembly with developed knowledge retrieval algorithm** | Nature Scientific Reports | 2025 | 飞机装配工装设计的 AI 决策系统，基于本体知识检索 |
| 4 | **The joint knowledge reasoning model based on knowledge representation learning for aviation assembly domain** | Science China Technological Sciences | 2023 | 航空装配领域的联合知识推理模型，知识图谱表示学习 |
| 5 | **The Construction of Knowledge Graphs in the Aviation Assembly Domain Based on a Joint Knowledge Extraction Model** | IEEE Xplore | 2023 | 航空装配领域知识图谱的构建方法 |

### B. RAG 技术基础与综述

| # | 论文 | 发表 | 年份 | 价值 |
|---|------|------|------|------|
| 6 | **Retrieval-Augmented Generation for Large Language Models: A Survey** (arXiv:2312.10997) | arXiv | 2023 | RAG 经典综述，定义 Naive/Advanced/Modular RAG 范式分类 |
| 7 | **A Survey on RAG Meets LLMs: Towards Retrieval-Augmented Large Language Models** (arXiv:2405.06211) | arXiv | 2024 | RAG 架构、训练策略和工业集成综述 |
| 8 | **Engineering RAG Systems for Real-World Applications** (arXiv:2506.20869) | arXiv | 2025 | 面向实际应用的 RAG 系统工程化方法 |

### C. 工业领域 RAG 应用

| # | 论文 | 发表 | 年份 | 价值 |
|---|------|------|------|------|
| 9 | **An advanced RAG system for manufacturing quality control** | ScienceDirect | 2024 | 制造业质量控制中的 RAG 实践 |
| 10 | **Application of RAG for interactive industrial knowledge management via LLM** | ScienceDirect | 2025 | 工业知识管理中的 RAG 交互系统 |
| 11 | **AviationGPT: A Large Language Model for the Aviation Domain** (arXiv:2311.17686) | AIAA Aviation Forum | 2024 | 航空领域专用 LLM，可作为对比基线 |
| 12 | **CAMB: A comprehensive industrial LLM benchmark on civil aviation maintenance** (arXiv:2508.20420) | arXiv | 2025 | 民航维护领域 LLM 评估基准 |

### D. 多模态检索

| # | 论文 | 发表 | 年份 | 价值 |
|---|------|------|------|------|
| 13 | **MMA-RAG: A Survey on Multimodal Agentic RAG** | HAL | 2025 | 多模态 Agent-RAG 综述 |
| 14 | **Multi-RAG: A Multimodal Retrieval-Augmented Generation** (arXiv:2505.23990) | arXiv | 2025 | 多模态 RAG 最新框架 |

### E. 中文相关文献

| # | 论文 | 发表 | 年份 | 价值 |
|---|------|------|------|------|
| 15 | **浅谈大模型时代下的检索增强：发展趋势、挑战与展望** | ACL CCL-2 | 2024 | 中文 RAG 综述，国内视角 |
| 16 | **人工智能在航空发动机全产业流程中的应用** | 中国航空学报 | 2024 | AI 在航发全产业链的系统应用 |
| 17 | **航空发动机关键装配技术综述与展望** | 北京航空航天大学学报 | 2022 | 航发装配技术综述（领域背景） |

## 四、论文选题建议

基于本系统的技术特点，以下是三个可行的论文选题方向：

### 方向 A：面向航空发动机装配的多模态 GraphRAG 知识问答系统
- **切入点**：BOM 图谱 + 技术文档 + 装配示意图的三源融合
- **对比实验**：纯文本 RAG vs 多模态 RAG vs GraphRAG vs 本系统（Full）
- **评估指标**：Recall@K、MRR、NDCG + 人工评审装配方案质量
- **投稿方向**：《计算机集成制造系统》、《航空制造技术》、CSCWD

### 方向 B：基于检索增强生成的航空发动机智能装配工艺规划
- **切入点**：从"知识问答"上升到"装配工艺自动规划"
- **强调**：LLM + 领域知识库如何生成可执行的装配工序
- **投稿方向**：《机械工程学报》、CIRP Annals、Journal of Manufacturing Systems

### 方向 C：多模态检索增强在工业技术文档中的应用研究
- **切入点**：工业 PDF 中图文混排的处理（图片提取 → Vision Caption → 双向量入库 → 跨模态检索）
- **通用性更强**：不局限于航空，可扩展到其他制造业
- **投稿方向**：《中国图象图形学报》、ACM MM Industrial Track

## 五、行业背景数据（可用于论文引言）

- RAG 市场规模：2024 年 18.2 亿美元 → 2035 年预计 150 亿美元（CAGR 21.1%）
- 2024 年 arXiv 上 RAG 论文 1223 篇，同比增长 1229%
- 企业 RAG 采用率已达 75%（2025 年数据）
- 航空发动机装配属于典型的"知识密集型"工艺，零件精度要求极高（如涡轮叶片壁厚 0.5±0.05mm）
