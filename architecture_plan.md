# 本地 RAG 项目架构设计方案

## 1. 架构目标
搭建一个轻量、本地化、高可扩展的 RAG (Retrieval-Augmented Generation) 项目，实现本地大模型（异地 vLLM 提供 API）检索本地数据来完成特定问答任务。项目架构需支持未来平滑接入 LangChain 与各类 Skills 功能。

## 2. 模块划分
项目划分为低耦合的五个核心层：

- **文档处理层 (Document Processing Layer)**
  - 职责：读取本地源文件（PDF/Word/TXT等），进行数据清洗与智能切片（Chunking）。
  - 实现：集成并应用 RAGFlow 仓库中核心的 `deepdoc` 模块，依赖其视觉文档理解 (VDU) 和专业切分能力。
- **向量与存储层 (Storage Layer)**
  - 职责：调用 Embedding 模型，并将向量化后的文本片段进行持久化存储。
  - 实现：使用 ChromaDB 等轻量级本地向量数据库。
- **检索与召回层 (Retrieval Layer)**
  - 职责：查询向量化转化并进行最近邻检索，支持在未来扩展全文+向量混合检索及 Reranker（重排）功能。
- **大模型生成层 (LLM Layer)**
  - 职责：管理与配置对大模型的请求调用。
  - 实现：通过标准兼容 OpenAI 的 API 对接已经部署在另一台机器上的基于 vLLM 部署的 Qwen3.5 量化模型。
  - Prompt 控制：复用并优化来自 RAGFlow `rag/prompts` 下的工业级提示词引擎模板。
- **编排与 Agent 层 (Orchestrator & Agents)**
  - 职责：控制和编排总体业务流，串行组合 Document Retrieval 和 LLM Generation 步骤。
  - 实现：前期采用原生 Python 代码进行组装，后期通过预留的 `SkillRegistry` 机制，将其转化为 LangChain 的 Agent Tools 进行驱动。

## 3. 项目目录结构规划

```text
rag-demo/
├── architecture_plan.md    # 架构方案文档（当前文档，动态更新）
├── requirements.txt        # 项目依赖库文件
├── core/                   # 核心配置文件及常量环境参数
├── document_processing/    # 本地文件读取Loader与基于 deepdoc 的文本切片模块
│   └── deepdoc/            # [外部克隆] RAGFlow 的深度文档解析引擎代码
├── prompts/                # 提示词库
│   └── ragflow_prompts/    # [外部克隆] RAGFlow 的工业级提示词模板
├── storage/                # 向量数据库（ChromaDB）与 Embedding 模型调用模块
├── retrieval/              # 搜索引擎，构建 RAG 召回与重排逻辑
├── llms/                   # vLLM API 调用客户端与通用 LLM 基准接口
├── agents/                 # 【预留】日后支持的 Skills / LangChain Route 工具集成
├── data/                   # 预备导入大模型学习的私人文档资料库
├── main_ingest.py          # 脚本：知识库文档一键解析灌库入口
└── main_chat.py            # 脚本：终端交互式 RAG 问答入口
```

## 4. 实施阶段与追踪 (Progress Tracker)
- [ ] **Phase 1: 基础设施准备** 
  - [x] 完成整体架构设计与目录规划
  - [x] 克隆 RAGFlow 代码，抽离 `deepdoc` 和 `rag/prompts`
  - [x] 编写生成 `requirements.txt` 依赖信息
- [ ] **Phase 2: 构建文档管道 (Ingest)** 
  - [ ] 跑通 `deepdoc` 本地解析
  - [ ] 搭配基于本地 Embedding 模型的向量生成
  - [ ] 连接 ChromaDB 完成向量数据入库存储 (`main_ingest.py`)
- [ ] **Phase 3: 构建检索与生成 (Chat)** 
  - [ ] 配置 vLLM 的远程 Qwen3.5 服务接入
  - [ ] 结合本地召回文本和 RAGFlow Prompt，调试最终问答效果 (`main_chat.py`)
- [ ] **Phase 4: LangChain 与 Agent 演进** 
  - [ ] 封装之前的基础模块，使用 LangChain 进行 Agent 化重构
  - [ ] 添加基础的 Tool / Skill 扩展示例
