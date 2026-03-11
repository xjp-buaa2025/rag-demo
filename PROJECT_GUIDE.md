# RAG Demo 项目完全指南

> 本文档随代码同步维护。每次新增/修改功能后同步更新对应章节。
> 目标：让你能完整理解每一行代码背后的思路，无需再看其他资料。

---

## 目录

1. [项目整体目标](#1-项目整体目标)
2. [核心概念：什么是 RAG](#2-核心概念什么是-rag)
3. [架构总览（五层设计）](#3-架构总览五层设计)
4. [数据流全景](#4-数据流全景)
5. [文件结构说明](#5-文件结构说明)
6. [各代码文件详解](#6-各代码文件详解)
   - [pdf_to_md.py](#61-pdf_to_mdpy)
   - [main_ingest.py](#62-main_ingestpy)
   - [main_chat.py](#63-main_chatpy)
   - [app.py](#64-apppy)
   - [eval_rag.py](#65-eval_ragpy)
   - [document_processing/common/token_utils.py](#66-document_processingcommontoken_utilspy)
   - [document_processing/rag/nlp/__init__.py](#67-document_processingragnlp__init__py)
7. [关键工具库详解](#7-关键工具库详解)
8. [配置系统（.env）](#8-配置系统env)
9. [运行方式](#9-运行方式)
10. [常见问题与排查](#10-常见问题与排查)
11. [变更日志](#11-变更日志)

---

## 1. 项目整体目标

构建一个**完全本地化**的 RAG（检索增强生成）问答系统，能回答"知识库里有但大模型不知道"的内容。

核心约束：
- **Embedding 完全本地**：不调用任何外部 Embedding API，用本机 GPU/CPU 跑 `BAAI/bge-m3`
- **向量库轻量**：ChromaDB，单文件数据库，无需独立服务
- **LLM 外接**：对接任意 OpenAI 兼容接口（SiliconFlow / vLLM 自部署均可）
- **PDF OCR 支持**：用 MinerU 处理扫描版 PDF，不依赖 GPU

---

## 2. 核心概念：什么是 RAG

```
用户问题
    ↓
【Embedding 模型】将问题向量化
    ↓
【向量数据库】检索最相似的文本块（召回 Top-K）
    ↓
【LLM】把检索到的原文 + 用户问题一起发给大模型，让它"看着原文回答"
    ↓
回答（有来源依据，不会幻觉）
```

**为什么不直接问 LLM？**
大模型的知识截止于训练数据，企业内部文档/最新论文/私有资料它完全不知道。RAG 让大模型"开卷考试"——考试时翻书，而不是靠死记硬背。

**为什么要 Embedding？**
文字不能直接比较相似度，把文字转成向量（一组数字）后，相似含义的句子在向量空间里距离近，可以用数学方法快速找到最相关的段落。

---

## 3. 架构总览（五层设计）

```
┌─────────────────────────────────────────────────────┐
│  Layer 5: 编排 / UI 层                               │
│  app.py (Gradio Web UI)  main_chat.py (终端交互)     │
├─────────────────────────────────────────────────────┤
│  Layer 4: LLM 生成层                                 │
│  OpenAI 兼容 API → SiliconFlow / vLLM               │
│  模型：Qwen2.5-14B-Instruct（通过 .env 配置）        │
├─────────────────────────────────────────────────────┤
│  Layer 3: 检索召回层                                  │
│  ChromaDB 向量检索（余弦距离）Top-K 召回              │
│  未来可扩展：BM25 混合检索 + Reranker                 │
├─────────────────────────────────────────────────────┤
│  Layer 2: 向量存储层                                  │
│  ChromaDB（storage/chroma_db/）                      │
│  Embedding 模型：BAAI/bge-m3（本地推理）              │
├─────────────────────────────────────────────────────┤
│  Layer 1: 文档处理层                                  │
│  MinerU（PDF→MD，支持 OCR）                          │
│  deepdoc TxtParser / MarkdownParser（文本解析切片）   │
└─────────────────────────────────────────────────────┘
```

---

## 4. 数据流全景

### 入库流程（一次性，离线）

```
data/*.pdf
    ↓ pdf_to_md.py（MinerU OCR）
data/*.md
    ↓ main_ingest.py
    ├─ deepdoc 解析 .md/.txt → 文本块列表
    ├─ BAAI/bge-m3 对每个块生成向量（本地推理）
    └─ upsert → ChromaDB（storage/chroma_db/）
```

### 问答流程（实时）

```
用户输入问题
    ↓ BAAI/bge-m3 将问题向量化
    ↓ ChromaDB 余弦检索 → Top-3 文本块
    ↓ 拼接 Prompt：系统提示 + 参考原文 + 用户问题
    ↓ OpenAI API（SiliconFlow）→ LLM 生成回答
输出（含来源）
```

---

## 5. 文件结构说明

```
rag-demo/
├── pdf_to_md.py              # 第一步：PDF 批量转 Markdown（MinerU OCR）
├── main_ingest.py            # 第二步：文档解析+向量化+写入 ChromaDB
├── main_chat.py              # 终端交互问答（轻量调试用）
├── app.py                    # Gradio Web UI（完整功能界面）
├── eval_rag.py               # RAG 性能评估工具（召回诊断 / LLM 打分 / RAGAS 三指标）
├── requirements.txt          # Python 依赖列表
├── .env                      # 密钥配置（不提交 git）
├── .gitignore
│
├── data/                     # 放你的文档（.pdf .md .txt）
│   └── rag_intro.md          # 示例文档
│
├── storage/
│   └── chroma_db/            # ChromaDB 数据文件（不提交 git）
│
├── document_processing/      # 文档解析层
│   ├── common/
│   │   ├── __init__.py
│   │   └── token_utils.py    # shim：token 计数（tiktoken）
│   ├── rag/
│   │   ├── __init__.py
│   │   └── nlp/__init__.py   # shim：编码检测（chardet）
│   └── deepdoc/              # RAGFlow 抽离的解析引擎（第三方，不修改）
│       ├── parser/           # TxtParser, MarkdownParser 等
│       └── vision/           # OCR/布局相关（暂未使用）
│
└── prompts/
    └── ragflow_prompts/      # RAGFlow 工业级提示词库（参考用）
```

---

## 6. 各代码文件详解

---

### 6.1 `pdf_to_md.py`

**职责**：将 `data/` 目录下所有 PDF 批量转换为 Markdown 文件，供 `main_ingest.py` 入库。

**为什么需要这一步？**
- PyMuPDF 的 `get_text("text")` 对扫描版 PDF 完全无效（图像 PDF 无文字层）
- 即使是"可复制"的 PDF，中文字体嵌入问题也常导致乱码或内容缺失
- MinerU 先做布局分析（找到文字区域），再做 OCR，输出结构化 Markdown，效果远好于直接提取

**工具选型：MinerU（pipeline 后端）**
- `pipeline` 后端 = PaddleOCR + DocLayout-YOLO 布局检测，CPU 即可运行
- `auto` 方法 = 自动判断：有文字层的页面用文字提取，扫描页用 OCR（混合文档友好）
- `-l ch` = 中文优先，提升中文识别率

**关键设计：两步走**
```
pdf_to_md.py  →  data/*.md  →  main_ingest.py
```
中间产物（`.md` 文件）可以人工打开检查质量，如果某本书转换效果差，可以手动修正再入库，而不是让错误数据污染知识库。

**输出目录结构（MinerU 内部）**：
```
临时目录/
└── {书名}/
    └── auto/
        └── {书名}.md    ← 我们读这个文件
```
脚本读取后写到 `data/{书名}.md`，临时目录自动删除。

**幂等性**：已存在同名 `.md` 的 PDF 直接跳过，重复运行安全。

---

### 6.2 `main_ingest.py`

**职责**：扫描 `data/` 目录，解析所有文档，生成向量，写入 ChromaDB。

**核心类/函数**：

#### `LocalEmbeddingFunction`
ChromaDB 的 `embedding_function` 参数要求传入一个可调用对象（callable），输入字符串列表，返回向量列表。这个类就是对 `SentenceTransformer` 的包装，让它符合这个接口。

`name()` 方法是 ChromaDB 1.5+ 新增要求，用于在元数据中记录使用的 Embedding 模型名称，防止用不同模型混存导致向量不一致。

#### `_split_text(text, chunk_size=500)`
**为什么要切片？**
- 大模型有 context 长度限制，一整本书塞不进去
- 向量检索的粒度决定召回精度：太长→噪声多，太短→上下文不足
- 500 字是经验值，覆盖约 2-5 段正文

**切片策略**：按句子边界（`。！？\n`）分割，不在句中间截断，保证每个块语义完整。

#### `process_document(file_path)`
统一的文件解析入口，根据扩展名分发：
- `.txt` / `.md` → deepdoc `RAGFlowTxtParser`
- `.pdf` → PyMuPDF（fallback；正式流程下 PDF 已被 `pdf_to_md.py` 转为 MD）

#### `main()`
`--clear` 参数删除旧的 ChromaDB collection 再重建，用于全量重建知识库。

**跳过已有 MD 的 PDF**：
```python
files_to_process = [
    f for f in files_to_process
    if not (f.lower().endswith('.pdf') and
            os.path.exists(os.path.splitext(f)[0] + '.md'))
]
```
防止同一本书被入库两次（一次以 PDF、一次以 MD）。

**ChromaDB upsert vs insert**：
用 `upsert`（不是 `insert`）是为了幂等性——用文件名+块序号构成唯一 ID，重复运行时更新而不是报错。

---

### 6.3 `main_chat.py`

**职责**：终端交互式问答，适合调试和快速验证效果。

**多轮对话实现**：
维护一个 `messages` 列表，格式为 OpenAI ChatCompletion 规范：
```python
[
  {"role": "system", "content": "系统提示"},
  {"role": "user",   "content": "问题1（含检索原文）"},
  {"role": "assistant", "content": "回答1"},
  {"role": "user",   "content": "问题2（含检索原文）"},
  ...
]
```
每轮都把历史带上，LLM 可以理解"你刚才说的 XX" 这类指代。

**检索注入方式**：
每轮用户消息不是直接发用户原话，而是：
```
参考资料：
[1] 来源: xxx.md
（检索到的原文段落）

用户问题：XXX
```
LLM 看到参考资料后，会优先根据原文回答，而不是靠自己的"记忆"。

**为什么 temperature=0.3？**
RAG 问答需要"忠实于原文"，创造性越低越好（0 = 完全确定性，1 = 最大发散）。0.3 是保守但不死板的平衡点。

---

### 6.4 `app.py`

**职责**：基于 Gradio 的 Web 问答界面，集成了入库管理和流式对话。

**与 `main_chat.py` 的关系**：
功能相同，但 `app.py` 是图形界面，适合非技术用户使用。两者共享 `main_ingest.process_document()` 逻辑（直接 import）。

**关键设计点**：

#### 全局初始化（模块级代码）
```python
embedding_func = LocalEmbeddingFunction(...)  # 启动时加载一次
chroma_client = chromadb.PersistentClient(...)
collection = ...
llm_client = OpenAI(...)
```
Embedding 模型加载耗时约 10-30 秒，放在全局避免每次请求都重新加载。

#### 流式输出（streaming）
```python
stream = llm_client.chat.completions.create(..., stream=True)
for chunk in stream:
    delta = chunk.choices[0].delta.content or ""
    full_answer += delta
    yield full_answer  # Gradio 每次 yield 都刷新 UI
```
`stream=True` 让 LLM 边生成边返回，用户看到文字逐渐出现，而不是等待全部生成完才显示。

#### `run_ingest()` 生成器
同样用 `yield` 让入库日志实时显示在 UI 上，而不是等全部完成才更新。

#### 历史窗口限制与 Gradio 版本兼容

Gradio 5+ 将 history 格式从配对列表 `[[user, assistant], ...]` 改为平铺的消息字典列表 `[{"role": "user", "content": "..."}, ...]`。代码兼容两种格式：

```python
for item in history[-12:]:  # 12 = 最近 6 轮 × 每轮 2 条
    if isinstance(item, dict):
        # Gradio 5+ 新格式
        messages.append({"role": item["role"], "content": item["content"]})
    else:
        # Gradio 4 旧格式
        user_msg, assistant_msg = item[0], item[1]
        ...
```

只取最近 12 条消息（6 轮），防止 prompt 超长。

#### 性能评估面板

`app.py` 还集成了 RAG 性能评估功能，在 UI 中以折叠面板（`📊 性能评估`）呈现：

- **🔍 召回诊断**：调用 `run_eval_diagnose()`，对 10 道内置测试题做向量检索，输出每题 Top-5 召回片段、余弦距离和全局统计。不调用 LLM，秒出结果。
- **⚖️ LLM 打分**：调用 `run_eval_judge()`，在召回基础上请 LLM 从相关性/完整性/可回答性三个维度各打 0-5 分，最后输出综合得分。

两个函数均为生成器（`yield`），结果实时流式显示到 Textbox，与 `run_ingest()` 模式一致。

---

### 6.5 `eval_rag.py`

**职责**：独立的 RAG 性能评估脚本，同时作为 `app.py` 性能评估面板的逻辑来源参考。

**三种运行模式**（通过 `--mode` 参数切换）：

#### `--mode diagnose`（默认）
1. 读取知识库所有 chunk，统计长度分布（均值/中位数/分桶直方图）
2. 对 10 道内置测试题逐一做向量检索（Top-5）
3. 打印每题召回片段（文本前 80 字 + 来源 + 余弦距离）
4. 输出全局距离统计和质量判断

#### `--mode judge`
在 diagnose 基础上，追加 LLM-as-Judge 打分：
- 把每道题的检索原文发给 LLM，要求输出 JSON 格式打分
- 三个维度：**相关性**（片段与问题相关程度）、**完整性**（片段能否覆盖回答）、**可回答性**（能否给出令用户满意的答案）
- 输出每道题三维分数 + 全局均值

#### `--mode ragas`
对齐学术界 RAGAS 框架，走完整 **检索→生成→评估** 链路，计算三个无需 Ground Truth 的指标：

| 指标 | 含义 | 计算方式 |
|------|------|---------|
| **Context Relevance**（上下文相关性） | 检索片段中有多少内容真正与问题相关 | LLM 从 chunks 中提取相关句子，计算比例 |
| **Faithfulness**（忠实度）| 答案中的事实声明是否都有检索内容支撑（幻觉检测） | 拆解答案为原子声明 → 逐条核验是否有 chunk 支撑 |
| **Answer Relevance**（回答相关性） | 答案是否直接针对了用户提问 | 从答案逆向生成 3 个问题 → 与原问题的 embedding 余弦相似度均值 |

与 `judge` 模式的区别：
- `judge`：只评估**检索阶段**（chunks 本身的质量），不生成答案
- `ragas`：评估**完整 RAG 链路**（包括生成阶段），指标更贴近真实使用效果
- `ragas` 运行时间更长（每道题多次 LLM 调用），10 道题约需 5–15 分钟

**如何解读余弦距离**（`diagnose` 模式）：
| 距离范围 | 含义 |
|---------|------|
| < 0.3 | 高度相关，召回质量优秀 |
| 0.3–0.6 | 中等，基本可用 |
| 0.6–0.8 | 较差，建议增大 chunk_size 或 TOP_K |
| > 0.8 | 很差，需排查 Embedding 或文档质量 |

**设计原则**：不引入额外依赖（只用 stdlib + 已有包），可直接运行：
```bash
PYTHONUTF8=1 python eval_rag.py --mode diagnose
PYTHONUTF8=1 python eval_rag.py --mode judge
PYTHONUTF8=1 python eval_rag.py --mode ragas
```

---

### 6.6 `document_processing/common/token_utils.py`  <!-- 原 6.5 -->

**职责**：为 deepdoc 提供 token 计数功能的"垫片"（shim）。

**背景**：deepdoc 的原始代码从 RAGFlow 内部导入 `from common.token_utils import num_tokens_from_string`，RAGFlow 用的是自己实现的版本。我们把这个包单独实现，让 deepdoc 的导入语句能正常工作。

**实现**：用 OpenAI 官方的 `tiktoken` 库，`cl100k_base` 编码方案（GPT-3.5/4 使用的 tokenizer）。对中文 token 计数有一定误差（中文字符的 tokenizer 不同），但 deepdoc 用这个只是做粗粒度的长度判断，精度要求不高。

---

### 6.7 `document_processing/rag/nlp/__init__.py`

**职责**：为 deepdoc 提供编码检测功能的"垫片"（shim）。

**背景**：deepdoc 的 txt_parser 需要 `from rag.nlp import find_codec` 来判断文件的字符编码（GBK / UTF-8 / Big5 等），原来从 RAGFlow 的 NLP 模块导入。

**实现**：用 `chardet` 库检测二进制内容的编码，并做标准化处理（`ascii` → `utf-8`，`utf_8_sig` → `utf-8`）。

---

## 7. 关键工具库详解

### ChromaDB
- **是什么**：纯 Python 向量数据库，数据存为 SQLite 文件，无需独立部署
- **为什么选它**：轻量（单文件）、API 简单、支持余弦/欧氏距离
- **核心概念**：`Collection`（类似数据库的表）、`upsert`（插入或更新）、`query`（向量检索）
- **距离度量**：余弦距离（cosine）。对文本语义匹配比欧氏距离（L2）效果好，因为向量长度不影响相似度

### BAAI/bge-m3
- **是什么**：北京智源研究院开发的多语言 Embedding 模型
- **为什么选它**：原生支持中文、英文，1792 维向量，效果优异，可本地运行
- **运行方式**：`SentenceTransformer` 封装，CPU 可运行（慢），有 GPU 会自动加速
- **向量维度**：1024（默认），越高维度越精确但越占内存

### MinerU（mineru）
- **是什么**：OpenDataLab 开发的开源 PDF 解析工具
- **核心能力**：布局检测（DocLayout-YOLO）+ OCR（PaddleOCR）+ 阅读顺序排序
- **pipeline 后端**：纯 CPU 可运行，适合本地部署
- **首次运行**：自动从 HuggingFace 下载模型（约 2-4 GB），国内可设 `MINERU_MODEL_SOURCE=modelscope`
- **输出**：结构化 Markdown，保留标题层级、表格，图片保存为单独文件

### deepdoc（RAGFlow 抽离）
- **是什么**：RAGFlow 项目的文档解析模块，支持 PDF/Word/Excel/TXT/MD 等格式
- **我们用的部分**：`RAGFlowTxtParser`（处理 .txt/.md）
- **为什么用它而不是直接 split**：deepdoc 按语义边界（段落、章节）切片，比简单按字数切效果好

### SentenceTransformers
- **是什么**：Hugging Face 的 Sentence Embedding 框架，封装了 BERT 系列模型
- **作用**：把文本转为定长向量，语义相近的文本向量距离小
- **batch 推理**：一次可以传入多个字符串列表，比逐个推理快很多

### OpenAI Python SDK
- **是什么**：OpenAI 官方 Python 客户端
- **我们用它连的**：MiniMax（主力）或 SiliconFlow（备用），均兼容 OpenAI 接口格式
- **流式输出**：`stream=True` + `for chunk in stream` 实现打字机效果
- **FallbackLLMClient**：`app.py` 中定义的代理类，优先调 MiniMax，失败时自动切换 SiliconFlow，对外接口与 `openai.OpenAI` 完全兼容

### Gradio
- **是什么**：快速构建 ML 演示 Web UI 的 Python 库
- **`gr.ChatInterface`**：内置的对话 UI 组件，自动处理历史记录显示
- **`gr.Blocks`**：更灵活的自定义布局，可以加按钮、文本框等控件

---

## 8. 配置系统（.env）

`.env` 文件放在项目根目录，**不提交 git**（已加入 .gitignore）。

```env
# 备用 LLM（SiliconFlow）
LLM_API_KEY=sk-xxxxxxxx        # SiliconFlow API Key
LLM_BASE_URL=https://api.siliconflow.cn/v1
LLM_MODEL=Qwen/Qwen2.5-14B-Instruct

# 主力 LLM（MiniMax，优先使用；留空则退回 SiliconFlow）
MINIMAX_API_KEY=               # MiniMax API Key（填入后自动启用）
MINIMAX_BASE_URL=https://api.minimax.chat/v1
MINIMAX_MODEL=MiniMax-Text-01
```

`python-dotenv` 的 `load_dotenv()` 在脚本启动时自动读取这个文件，注入到 `os.environ`，代码通过 `os.getenv()` 读取。

**LLM 优先级**：`MINIMAX_API_KEY` 非空时，`app.py` 会用 `FallbackLLMClient` 优先调 MiniMax，失败时自动降级到 SiliconFlow；`eval_rag.py` 直接切换为 MiniMax client。`MINIMAX_API_KEY` 为空时两者均使用 SiliconFlow。

**好处**：密钥不硬编码，不会被 git 记录，换模型只改 `.env` 不改代码。

---

## 9. 运行方式

> 所有命令需在激活 `rag_demo` conda 环境后运行，或使用完整 Python 路径。

```bash
PYTHON="C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe"

# 第一步：PDF 转 Markdown（首次运行会下载 MinerU 模型，耐心等待）
PYTHONUTF8=1 $PYTHON pdf_to_md.py

# 第二步：文档入库（首次运行会下载 BAAI/bge-m3 模型）
PYTHONUTF8=1 $PYTHON main_ingest.py --clear   # --clear 清空重建
PYTHONUTF8=1 $PYTHON main_ingest.py           # 增量入库

# 方式A：终端问答
PYTHONUTF8=1 $PYTHON main_chat.py

# 方式B：Web 界面（访问 http://127.0.0.1:7860）
PYTHONUTF8=1 $PYTHON app.py
```

---

## 10. 常见问题与排查

| 现象 | 原因 | 解决 |
|------|------|------|
| PDF 入库后块数极少 | PDF 是扫描版，无文字层 | 先运行 `pdf_to_md.py` 做 OCR |
| MinerU 下载模型失败 | HuggingFace 网络不通 | `set MINERU_MODEL_SOURCE=modelscope` |
| `num_tokens_from_string` 报错 | shim 未加入 sys.path | 确认 `document_processing/` 在 sys.path 中 |
| ChromaDB `collection.count()` 返回 0 | 未运行入库或 --clear 清空后未重新入库 | 运行 `main_ingest.py` |
| LLM 返回"知识库中没有找到" | 检索距离太大，语义不匹配 | 检查入库块数是否正常，检查 Embedding 模型是否加载成功 |
| GBK 编码错误 | Windows 控制台编码问题 | 命令前加 `PYTHONUTF8=1` |
| 多轮对话第二问报错 `too many values to unpack` | Gradio 5+ 修改了 history 格式 | 已修复，`app.py` 的 `chat()` 函数已兼容新旧两种格式 |
| ChromaDB `Error loading hnsw index` | 强制杀进程导致索引文件损坏 | 用 PowerShell `Remove-Item -Recurse` 清空 `storage/chroma_db/` 目录后重启 |
| 回答内容太短 | SYSTEM_PROMPT 要求"简洁" | 已修改 SYSTEM_PROMPT 为"详细、准确、有条理" |

---

## 11. 变更日志

| 日期 | 变更内容 |
|------|----------|
| 2026-03-06 | 初始化项目，完成架构设计，deepdoc 集成，ChromaDB 入库 |
| 2026-03-06 | 用 MinerU pipeline 替换 pymupdf4llm，支持扫描版 PDF OCR |
| 2026-03-06 | 创建本文档，为所有代码文件添加中文注释 |
| 2026-03-09 | 修复 Gradio 6.x 多轮对话报错（history 格式兼容 dict 和 list 两种形式） |
| 2026-03-09 | 新增 `eval_rag.py`：RAG 性能评估工具，支持召回诊断和 LLM-as-Judge 两种模式 |
| 2026-03-09 | `app.py` 新增"📊 性能评估"前端面板，召回诊断和 LLM 打分结果实时显示 |
| 2026-03-09 | 调整 `app.py` 和 `main_chat.py` 的 SYSTEM_PROMPT，去掉"简洁"限制，改为详细输出 |
| 2026-03-09 | `eval_rag.py` 新增 `--mode ragas`：实现 RAGAS 三指标（Context Relevance / Faithfulness / Answer Relevance） |
| 2026-03-09 | `app.py` 性能评估面板新增"🧪 RAGAS 评估"按钮，走完整检索→生成→评估链路 |
| 2026-03-09 | 新增 MiniMax 支持：`.env` 加 `MINIMAX_API_KEY/BASE_URL/MODEL`；`app.py` 引入 `FallbackLLMClient`（优先 MiniMax，失败降级 SiliconFlow）；`eval_rag.py` 同步支持 MiniMax 优先 |
