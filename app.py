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
import re
import json
import statistics
from typing import List

from dotenv import load_dotenv
import chromadb
from sentence_transformers import SentenceTransformer
from openai import OpenAI
import gradio as gr
import pandas as pd

try:
    from neo4j import GraphDatabase as _Neo4jDriver
    _NEO4J_AVAILABLE = True
except ImportError:
    _NEO4J_AVAILABLE = False

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

# Neo4j 配置（BOM 装配系统）
NEO4J_URI  = os.getenv("NEO4J_URI",  "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASS = os.getenv("NEO4J_PASS", "password")
DEFAULT_BOM_PATH = os.path.join(os.path.dirname(__file__), "data", "test_bom.xlsx")
COLLECTION_NAME = "local_rag_knowledge"
EMBEDDING_MODEL_NAME = "BAAI/bge-m3"
TOP_K = 4  # 每次检索返回 4 个相关块（比 main_chat.py 多一个，给 Web 用户更多参考）

LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.siliconflow.cn/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "Qwen/Qwen2.5-14B-Instruct")

MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "").strip()
MINIMAX_BASE_URL = os.getenv("MINIMAX_BASE_URL", "https://api.minimaxi.com/v1")
MINIMAX_MODEL = os.getenv("MINIMAX_MODEL", "MiniMax-M2.5")

SYSTEM_PROMPT = """你是一个专业的知识库问答助手。请严格根据提供的参考资料回答用户问题。
如果参考资料中没有相关信息，请如实说明"知识库中没有找到相关内容"，不要凭空捏造。
回答要详细、准确、有条理，尽量引用原文中的具体数据和技术细节，不要省略重要信息。"""

# 评估模块常量
EVAL_TOP_K = 5  # 评估时多召回一个，覆盖更多候选
EVAL_QUESTIONS = [
    "涡轮发动机的基本工作原理是什么？",
    "压气机的作用是什么？它有哪些主要类型？",
    "燃烧室的设计需要满足哪些基本要求？",
    "涡轮叶片在高温下如何保持强度？常见的冷却方式有哪些？",
    "发动机推力是如何产生的？影响推力大小的因素有哪些？",
    "什么是喘振？发动机喘振会造成什么危害？如何防止？",
    "加力燃烧室的工作原理是什么？它为什么能显著提升推力？",
    "航空发动机的主要故障类型有哪些？常用的故障诊断方法是什么？",
    "发动机零件的可靠性设计有哪些主要方法和原则？",
    "发动机试验中常用哪些参数来评估其性能？测试技术有哪些？",
]
JUDGE_PROMPT_TMPL = """你是一名 RAG 系统评估专家。请根据以下检索到的文档片段，对其质量进行评分。

【问题】
{question}

【检索到的文档片段】
{context}

请从以下三个维度各打 0-5 分（整数），并给出简短理由（各一句话）：
1. 相关性（0-5）：片段内容与问题的相关程度
2. 完整性（0-5）：片段是否包含足以回答该问题的信息
3. 可回答性（0-5）：仅凭这些片段，是否能给出令用户满意的答案

请严格按以下 JSON 格式输出，不要有其他内容：
{{
  "relevance": <0-5>,
  "completeness": <0-5>,
  "answerability": <0-5>,
  "reason_relevance": "<一句话>",
  "reason_completeness": "<一句话>",
  "reason_answerability": "<一句话>"
}}"""

RAGAS_CONTEXT_RELEVANCE_PROMPT = """你是一名 RAG 评估专家。给定以下问题和检索到的上下文，请提取上下文中与问题直接相关的句子。
每行输出一个相关句子，不要输出任何编号或解释。如果没有相关句子，仅输出 NONE。

【问题】
{question}

【上下文】
{context}"""

RAGAS_FAITHFULNESS_DECOMPOSE = """将以下答案拆解为原子化的事实声明（每个声明是一个简短、独立可验证的陈述句）。
每行输出一条声明，不要编号，不要解释。

【答案】
{answer}"""

RAGAS_FAITHFULNESS_VERIFY = """给定以下上下文和一条声明，判断该声明是否完全由上下文内容支撑。
只回答 YES 或 NO，不要有任何其他内容。

【上下文】
{context}

【声明】
{claim}"""

RAGAS_ANSWER_RELEVANCE_PROMPT = """给定以下答案，生成 3 个可能引发该答案的不同问题。
每行输出一个问题，不要编号，不要解释。

【答案】
{answer}"""


# ==========================================
# 全局初始化（模块加载时执行一次）
# ==========================================
# 设计原因：Embedding 模型加载耗时 10-30 秒，放在全局避免每次请求重复初始化。
# Gradio 是单进程多线程模型，全局对象在所有请求间共享，但 SentenceTransformer
# 和 ChromaDB 的读操作是线程安全的。

print("正在初始化，请稍候...")


class FallbackLLMClient:
    """
    优先调用主 LLM（MiniMax），失败时自动 fallback 到备用（SiliconFlow）。
    接口与 openai.OpenAI 完全兼容（client.chat.completions.create(...)），
    所有现有调用点无需修改。
    """
    def __init__(self, primary_client, primary_model, fallback_client=None, fallback_model=None):
        self._primary = primary_client
        self._primary_model = primary_model
        self._fallback = fallback_client
        self._fallback_model = fallback_model
        self.chat = self._Chat(self)

    class _Chat:
        def __init__(self, outer):
            self.completions = FallbackLLMClient._Completions(outer)

    class _Completions:
        def __init__(self, outer):
            self._outer = outer

        def create(self, model=None, **kwargs):
            # 忽略调用方传入的 model，使用各自配置的模型名称
            try:
                return self._outer._primary.chat.completions.create(
                    model=self._outer._primary_model, **kwargs
                )
            except Exception as e:
                if self._outer._fallback is None:
                    raise
                print(f"  ⚠️  主 LLM 失败（{e}），切换到备用 LLM…")
                return self._outer._fallback.chat.completions.create(
                    model=self._outer._fallback_model, **kwargs
                )


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
try:
    collection = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_func,
        metadata={"hnsw:space": "cosine"},
    )
    _probe = collection.count()  # 触发索引加载，尽早发现 HNSW 损坏
except Exception as _e:
    print(f"[警告] ChromaDB 索引损坏（{_e}），自动重建集合，请重新运行入库脚本…")
    try:
        chroma_client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_func,
        metadata={"hnsw:space": "cosine"},
    )
if MINIMAX_API_KEY:
    _primary = OpenAI(api_key=MINIMAX_API_KEY, base_url=MINIMAX_BASE_URL)
    _fallback = OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)
    llm_client = FallbackLLMClient(_primary, MINIMAX_MODEL, _fallback, LLM_MODEL)
    _active_model_label = f"MiniMax({MINIMAX_MODEL}) → fallback: {LLM_MODEL}"
else:
    llm_client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)
    _active_model_label = LLM_MODEL
print(f"初始化完成，知识库共 {collection.count()} 条文档块。LLM: {_active_model_label}")


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


# ==========================================
# 性能评估逻辑
# ==========================================

def _retrieve_eval(query: str) -> List[dict]:
    """评估专用检索，使用 EVAL_TOP_K"""
    n = min(EVAL_TOP_K, collection.count())
    if n == 0:
        return []
    query_embedding = embedding_func([query])[0]
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n,
        include=["documents", "metadatas", "distances"],
    )
    return [
        {"text": doc, "source": meta.get("source", "未知"), "distance": dist}
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        )
    ]


def _get_chunk_lengths() -> List[int]:
    """分页读取知识库中所有 chunk 的字符长度，用于分布分析"""
    total = collection.count()
    lengths, offset = [], 0
    while offset < total:
        result = collection.get(limit=500, offset=offset, include=["documents"])
        lengths.extend(len(doc) for doc in result["documents"])
        offset += 500
    return lengths


def run_eval_diagnose():
    """召回质量诊断生成器：检索 + 距离统计，逐步 yield 报告文本。"""
    lines = []

    def emit(msg=""):
        lines.append(msg)
        return "\n".join(lines)

    total = collection.count()
    yield emit("=" * 60)
    yield emit("  RAG 召回质量诊断报告")
    yield emit("=" * 60)
    yield emit(f"知识库文档块总数：{total}")
    if total == 0:
        yield emit("⚠️ 知识库为空，请先完成入库后再评估。")
        return

    # Chunk 长度分布
    yield emit("\n--- 文档块长度分布 ---")
    yield emit("正在统计，请稍候…")
    lengths = _get_chunk_lengths()
    lines.pop()  # 删掉"正在统计"占位行
    if lengths:
        yield emit(f"  均值: {statistics.mean(lengths):.0f}  中位数: {statistics.median(lengths):.0f}  最小: {min(lengths)}  最大: {max(lengths)}")
        buckets = {"<100": 0, "100-300": 0, "300-500": 0, "500-800": 0, ">800": 0}
        for ln in lengths:
            if ln < 100:        buckets["<100"] += 1
            elif ln < 300:      buckets["100-300"] += 1
            elif ln < 500:      buckets["300-500"] += 1
            elif ln < 800:      buckets["500-800"] += 1
            else:               buckets[">800"] += 1
        max_cnt = max(1, max(buckets.values()))
        for bucket, count in buckets.items():
            bar = "█" * (count * 15 // max_cnt)
            yield emit(f"  {bucket:>10}  {bar:<15} {count} 块 ({count/len(lengths)*100:.1f}%)")

    # 逐题检索报告
    all_distances = []
    yield emit(f"\n--- 逐题召回详情（Top-{EVAL_TOP_K}）---")
    for i, question in enumerate(EVAL_QUESTIONS, 1):
        yield emit(f"\n[{i:02d}] {question}")
        chunks = _retrieve_eval(question)
        if not chunks:
            yield emit("  无召回结果")
            continue
        distances = [c["distance"] for c in chunks]
        all_distances.extend(distances)
        avg = statistics.mean(distances)
        quality = "优秀" if avg < 0.3 else "一般" if avg < 0.6 else "较差" if avg < 0.8 else "很差"
        yield emit(f"  平均距离: {avg:.4f}  [{quality}]")
        for j, chunk in enumerate(chunks, 1):
            bar = "█" * max(1, int((1 - chunk["distance"] / 2) * 8))
            snippet = chunk["text"].replace("\n", " ")[:80]
            yield emit(f"  [{j}] dist={chunk['distance']:.4f} {bar}  {chunk['source']}")
            yield emit(f"      {snippet}…")

    # 全局统计
    if all_distances:
        avg_g = statistics.mean(all_distances)
        yield emit(f"\n{'=' * 60}")
        yield emit("全局距离统计")
        yield emit(f"  均值: {avg_g:.4f}  中位数: {statistics.median(all_distances):.4f}  最小: {min(all_distances):.4f}  最大: {max(all_distances):.4f}")
        if avg_g < 0.3:
            verdict = "✅ 召回质量优秀，embedding 对齐良好。"
        elif avg_g < 0.6:
            verdict = "🟡 召回质量一般，可考虑增大 chunk_size 或 TOP_K。"
        elif avg_g < 0.8:
            verdict = "🟠 召回质量较差，建议排查切片策略和 Embedding 适配性。"
        else:
            verdict = "🔴 召回质量很差，请检查知识库内容是否与问题领域匹配。"
        yield emit(f"  {verdict}")
        yield emit("=" * 60)


def run_eval_judge():
    """LLM-as-Judge 评估生成器：对每道题的召回结果请 LLM 三维打分，逐步 yield 报告。"""
    lines = []

    def emit(msg=""):
        lines.append(msg)
        return "\n".join(lines)

    total = collection.count()
    yield emit("=" * 60)
    yield emit("  RAG LLM-as-Judge 评估报告")
    yield emit("=" * 60)
    yield emit(f"知识库文档块总数：{total}")
    if total == 0:
        yield emit("⚠️ 知识库为空，请先完成入库后再评估。")
        return

    all_scores = {"relevance": [], "completeness": [], "answerability": []}

    for i, question in enumerate(EVAL_QUESTIONS, 1):
        yield emit(f"\n[{i:02d}] {question}")
        chunks = _retrieve_eval(question)
        if not chunks:
            yield emit("  无召回结果，跳过")
            continue

        avg_dist = statistics.mean(c["distance"] for c in chunks)
        yield emit(f"  平均召回距离: {avg_dist:.4f}")
        yield emit("  正在请求 LLM 打分…")

        context = "\n\n".join(
            f"[{j+1}] 来源: {c['source']}\n{c['text']}"
            for j, c in enumerate(chunks)
        )
        prompt = JUDGE_PROMPT_TMPL.format(question=question, context=context)
        try:
            resp = llm_client.chat.completions.create(
                model=LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.01,
            )
            raw = resp.choices[0].message.content.strip()
            s, e = raw.find("{"), raw.rfind("}") + 1
            scores = json.loads(raw[s:e]) if s >= 0 and e > s else {}
        except Exception as ex:
            lines[-1] = f"  打分失败: {ex}"
            yield "\n".join(lines)
            continue

        lines.pop()  # 删掉"正在请求"占位行
        r  = scores.get("relevance",     "N/A")
        c_ = scores.get("completeness",  "N/A")
        a  = scores.get("answerability", "N/A")
        yield emit(f"  相关性={r}/5  完整性={c_}/5  可回答性={a}/5")
        yield emit(f"  └ 相关性: {scores.get('reason_relevance', '')}")
        yield emit(f"  └ 完整性: {scores.get('reason_completeness', '')}")
        yield emit(f"  └ 可回答性: {scores.get('reason_answerability', '')}")

        for key, val in [("relevance", r), ("completeness", c_), ("answerability", a)]:
            if isinstance(val, (int, float)):
                all_scores[key].append(val)

    # 汇总
    yield emit(f"\n{'=' * 60}")
    yield emit("全局评分汇总")
    yield emit("-" * 40)
    for dim, label in [("relevance", "相关性"), ("completeness", "完整性"), ("answerability", "可回答性")]:
        vals = all_scores[dim]
        if vals:
            avg = statistics.mean(vals)
            stars = "★" * round(avg) + "☆" * (5 - round(avg))
            yield emit(f"  {label}: {avg:.2f}/5  {stars}")
    flat = [v for vals in all_scores.values() for v in vals]
    if flat:
        total_avg = statistics.mean(flat)
        yield emit(f"\n  综合得分: {total_avg:.2f}/5")
        if total_avg >= 4:
            verdict = "✅ RAG 整体质量优秀。"
        elif total_avg >= 3:
            verdict = "🟡 RAG 质量良好，有提升空间。"
        elif total_avg >= 2:
            verdict = "🟠 RAG 质量较差，建议调整 chunk_size / TOP_K / 重新入库。"
        else:
            verdict = "🔴 RAG 质量很差，请检查知识库内容和检索配置。"
        yield emit(f"  {verdict}")
    yield emit("=" * 60)


def run_eval_ragas():
    """
    RAGAS 三指标评估生成器：Context Relevance / Faithfulness / Answer Relevance。

    每道题流程：检索 → 生成答案 → 计算 CR / F / AR
    注意：Faithfulness 对每条声明单独调用 LLM，10 道题约需 5–15 分钟。
    """
    lines = []

    def emit(msg=""):
        lines.append(msg)
        return "\n".join(lines)

    total = collection.count()
    yield emit("=" * 60)
    yield emit("  RAGAS 三指标评估报告")
    yield emit("  Context Relevance / Faithfulness / Answer Relevance")
    yield emit("=" * 60)
    yield emit(f"知识库文档块总数：{total}")
    if total == 0:
        yield emit("⚠️ 知识库为空，请先完成入库后再评估。")
        return

    all_cr, all_f, all_ar = [], [], []

    for i, question in enumerate(EVAL_QUESTIONS, 1):
        yield emit(f"\n[{i:02d}] {question}")
        chunks = _retrieve_eval(question)
        if not chunks:
            yield emit("  无召回结果，跳过")
            continue

        avg_dist = statistics.mean(c["distance"] for c in chunks)
        yield emit(f"  召回距离: {avg_dist:.4f}")

        # 1. 生成答案
        yield emit("  生成答案中…")
        context_parts = [f"[{j+1}] 来源: {c['source']}\n{c['text']}" for j, c in enumerate(chunks)]
        user_content = "参考资料：\n" + "\n\n".join(context_parts) + f"\n\n用户问题：{question}"
        try:
            resp = llm_client.chat.completions.create(
                model=LLM_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_content},
                ],
                temperature=0.3,
            )
            answer = resp.choices[0].message.content.strip()
            lines[-1] = f"  答案: {answer[:100].replace(chr(10), ' ')}…"
            yield "\n".join(lines)
        except Exception as ex:
            lines[-1] = f"  答案生成失败: {ex}"
            yield "\n".join(lines)
            continue

        # 2. Context Relevance
        yield emit("  [CR] 计算 Context Relevance…")
        context_full = "\n\n".join(c["text"] for c in chunks)
        all_sents = [s.strip() for s in re.split(r'[。！？\n]+', context_full) if s.strip()]
        try:
            cr_resp = llm_client.chat.completions.create(
                model=LLM_MODEL,
                messages=[{"role": "user", "content": RAGAS_CONTEXT_RELEVANCE_PROMPT.format(
                    question=question, context=context_full)}],
                temperature=0.01,
            )
            cr_raw = cr_resp.choices[0].message.content.strip()
            if not cr_raw or cr_raw.upper() == "NONE":
                cr = 0.0
            else:
                relevant = [l.strip() for l in cr_raw.split("\n") if l.strip() and l.strip().upper() != "NONE"]
                cr = min(len(relevant) / max(len(all_sents), 1), 1.0)
            lines[-1] = f"  [CR] Context Relevance: {cr:.3f}"
            yield "\n".join(lines)
            all_cr.append(cr)
        except Exception as ex:
            lines[-1] = f"  [CR] 失败: {ex}"
            yield "\n".join(lines)
            cr = None

        # 3. Faithfulness（拆解声明 + 逐条验证）
        yield emit("  [F ] 计算 Faithfulness（拆解声明 + 逐条核验）…")
        context_numbered = "\n\n".join(f"[{j+1}] {c['text']}" for j, c in enumerate(chunks))
        try:
            decompose_resp = llm_client.chat.completions.create(
                model=LLM_MODEL,
                messages=[{"role": "user", "content": RAGAS_FAITHFULNESS_DECOMPOSE.format(answer=answer)}],
                temperature=0.01,
            )
            claims = [l.strip() for l in decompose_resp.choices[0].message.content.strip().split("\n") if l.strip()]
            n_yes = 0
            for claim in claims:
                verify_resp = llm_client.chat.completions.create(
                    model=LLM_MODEL,
                    messages=[{"role": "user", "content": RAGAS_FAITHFULNESS_VERIFY.format(
                        context=context_numbered, claim=claim)}],
                    temperature=0.01,
                )
                if "YES" in verify_resp.choices[0].message.content.strip().upper():
                    n_yes += 1
            f_score = n_yes / len(claims) if claims else 0.0
            lines[-1] = f"  [F ] Faithfulness: {f_score:.3f}  ({n_yes}/{len(claims)} 声明有支撑)"
            yield "\n".join(lines)
            all_f.append(f_score)
        except Exception as ex:
            lines[-1] = f"  [F ] 失败: {ex}"
            yield "\n".join(lines)
            f_score = None

        # 4. Answer Relevance
        yield emit("  [AR] 计算 Answer Relevance…")
        try:
            ar_resp = llm_client.chat.completions.create(
                model=LLM_MODEL,
                messages=[{"role": "user", "content": RAGAS_ANSWER_RELEVANCE_PROMPT.format(answer=answer)}],
                temperature=0.3,
            )
            gen_qs = [l.strip() for l in ar_resp.choices[0].message.content.strip().split("\n") if l.strip()][:3]
            q_emb = embedding_func.model.encode([question], normalize_embeddings=True)[0].tolist()
            sims = []
            for gq in gen_qs:
                gq_emb = embedding_func.model.encode([gq], normalize_embeddings=True)[0].tolist()
                sims.append(max(0.0, sum(a * b for a, b in zip(q_emb, gq_emb))))
            ar = statistics.mean(sims) if sims else 0.0
            lines[-1] = f"  [AR] Answer Relevance: {ar:.3f}"
            yield "\n".join(lines)
            all_ar.append(ar)
        except Exception as ex:
            lines[-1] = f"  [AR] 失败: {ex}"
            yield "\n".join(lines)

    # 全局汇总
    yield emit(f"\n{'=' * 60}")
    yield emit("RAGAS 全局评分汇总")
    yield emit("-" * 40)
    for vals, label in [(all_cr, "Context Relevance"), (all_f, "Faithfulness"), (all_ar, "Answer Relevance")]:
        if vals:
            avg = statistics.mean(vals)
            bar = "█" * int(avg * 10) + "░" * (10 - int(avg * 10))
            yield emit(f"  {label:22s}  {avg:.3f}  [{bar}]")
        else:
            yield emit(f"  {label:22s}  无数据")

    all_vals = all_cr + all_f + all_ar
    if all_vals:
        ragas_score = statistics.mean(all_vals)
        yield emit(f"\n  RAGAS 综合分:  {ragas_score:.3f} / 1.0")
        if ragas_score >= 0.8:
            yield emit("  ✅ RAG 整体质量优秀。")
        elif ragas_score >= 0.6:
            yield emit("  🟡 RAG 质量良好，有提升空间。")
        elif ragas_score >= 0.4:
            yield emit("  🟠 RAG 质量中等，建议优化 chunk 策略和 TOP_K。")
        else:
            yield emit("  🔴 RAG 质量较差，请检查知识库内容、Embedding 模型和生成策略。")
    yield emit("=" * 60)


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
    # Gradio 5+ history 格式：平铺的 dict 列表 [{"role":..,"content":..}, ...]
    # Gradio 4  history 格式：配对列表 [[user, assistant], ...]
    for item in history[-12:]:  # 12 = 最近 6 轮 × 每轮 2 条
        if isinstance(item, dict):
            role = item.get("role", "")
            content = item.get("content") or ""
            if role in ("user", "assistant"):
                messages.append({"role": role, "content": content})
        else:
            # 兼容旧格式：[user_msg, assistant_msg]
            user_msg, assistant_msg = item[0], item[1]
            if user_msg:
                messages.append({"role": "user", "content": user_msg})
            if assistant_msg:
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
# BOM 装配系统 — 后端逻辑
# ==========================================

# Neo4j 连接（懒加载，首次调用时建立）
_neo4j_driver = None


def _get_neo4j():
    """获取 Neo4j 连接，失败时返回 None（不抛异常，保证 UI 不崩溃）。"""
    global _neo4j_driver
    if _neo4j_driver is not None:
        return _neo4j_driver
    if not _NEO4J_AVAILABLE:
        return None
    try:
        driver = _Neo4jDriver.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
        driver.verify_connectivity()
        _neo4j_driver = driver
    except Exception:
        _neo4j_driver = None
    return _neo4j_driver


def check_neo4j_status() -> str:
    """检测 Neo4j 连接，返回 Markdown 状态文本（供 UI 直接显示）。"""
    global _neo4j_driver
    _neo4j_driver = None          # 强制重新连接
    driver = _get_neo4j()
    if not _NEO4J_AVAILABLE:
        return "🔴 **Neo4j 未安装**：请运行 `pip install neo4j`"
    if driver is None:
        return (
            "🔴 **Neo4j 未连接**  \n"
            f"URI：`{NEO4J_URI}`  \n"
            "请先启动 Docker 容器：  \n"
            "```\ndocker start neo4j\n```"
        )
    try:
        with driver.session() as s:
            r = s.run("""
                MATCH (n) WHERE n:Assembly OR n:Part OR n:Standard
                RETURN count(n) AS nodes
            """).single()
            nodes = r["nodes"] if r else 0
            edges = s.run("MATCH ()-[r:CHILD_OF]->() RETURN count(r) AS cnt").single()["cnt"]
        return (
            f"🟢 **已连接** `{NEO4J_URI}`  \n"
            f"图谱：**{nodes} 个节点**，**{edges} 条关系**  \n"
            f"可视化：[http://localhost:7474](http://localhost:7474)"
        )
    except Exception as e:
        return f"🟡 **连接异常**：{e}"


def run_bom_ingest_ui(file_obj, clear_first: bool):
    """
    BOM 入库生成器（供 Gradio yield 实时刷新日志）。
    file_obj：Gradio File 组件上传的临时文件对象，为 None 时使用默认测试 BOM。
    """
    lines = []

    def emit(msg):
        lines.append(msg)
        return "\n".join(lines)

    # 确定文件路径
    if file_obj is None:
        filepath = DEFAULT_BOM_PATH
        yield emit(f"📌 未上传文件，使用默认测试 BOM：{os.path.basename(filepath)}")
    else:
        filepath = file_obj.name if hasattr(file_obj, "name") else str(file_obj)
        yield emit(f"📌 使用上传文件：{os.path.basename(filepath)}")

    if not os.path.exists(filepath):
        yield emit(f"❌ 文件不存在：{filepath}")
        return

    # 读取 Excel
    yield emit("📖 读取 BOM 表…")
    try:
        df = pd.read_excel(filepath, dtype=str)
        df.columns = [c.strip().lower() for c in df.columns]
        for col in ("material", "weight_kg", "spec", "note"):
            if col not in df.columns:
                df[col] = ""
        df = df.dropna(subset=["level_code", "part_id"])
        for col in df.columns:
            df[col] = df[col].fillna("").astype(str).str.strip()
        df["qty"] = pd.to_numeric(df["qty"], errors="coerce").fillna(1).astype(int)
        yield emit(f"✅ 读取成功：共 {len(df)} 条零件记录")
    except Exception as e:
        yield emit(f"❌ 读取失败：{e}")
        return

    # 连接 Neo4j
    yield emit(f"🔌 连接 Neo4j（{NEO4J_URI}）…")
    driver = _get_neo4j()
    if driver is None:
        yield emit("❌ Neo4j 不可用，请先启动：docker start neo4j")
        return
    yield emit("✅ 连接成功")

    with driver.session() as session:
        # 建立 Schema
        for label in ("Assembly", "Part", "Standard"):
            session.run(f"CREATE CONSTRAINT IF NOT EXISTS FOR (n:{label}) REQUIRE n.part_id IS UNIQUE")
        yield emit("🔧 Schema 约束已就绪")

        # 可选清空
        if clear_first:
            r = session.run("""
                MATCH (n) WHERE n:Assembly OR n:Part OR n:Standard
                DETACH DELETE n RETURN count(n) AS cnt
            """).single()
            yield emit(f"🗑️ 已清空旧数据（{r['cnt']} 个节点）")

        # 写入节点
        records = df.to_dict(orient="records")
        for category in ("Assembly", "Part", "Standard"):
            batch = [r for r in records if r["category"] == category]
            if not batch:
                continue
            session.run(f"""
                UNWIND $rows AS row
                MERGE (n:{category} {{part_id: row.part_id}})
                SET n.level_code   = row.level_code,
                    n.part_name    = row.part_name,
                    n.part_name_en = row.part_name_en,
                    n.qty          = toInteger(row.qty),
                    n.unit         = row.unit,
                    n.material     = row.material,
                    n.weight_kg    = CASE row.weight_kg WHEN '' THEN null ELSE toFloat(row.weight_kg) END,
                    n.spec         = row.spec,
                    n.note         = row.note
            """, rows=batch)
            yield emit(f"   ✅ {category}：写入 {len(batch)} 个节点")

        # 建立关系
        level_map = dict(zip(df["level_code"], df["part_id"]))
        edges = []
        for _, row in df.iterrows():
            code = str(row["level_code"])
            if "." not in code:
                continue
            parent_code = ".".join(code.split(".")[:-1])
            parent_id = level_map.get(parent_code)
            if parent_id:
                edges.append({"child_id": row["part_id"], "parent_id": parent_id})
        if edges:
            session.run("""
                UNWIND $edges AS e
                MATCH (child  {part_id: e.child_id})
                MATCH (parent {part_id: e.parent_id})
                MERGE (child)-[:CHILD_OF]->(parent)
            """, edges=edges)
        yield emit(f"   ✅ CHILD_OF 关系：建立 {len(edges)} 条")

        # 统计
        r2 = session.run("""
            MATCH (n) WHERE n:Assembly OR n:Part OR n:Standard
            RETURN count(CASE WHEN n:Assembly THEN 1 END) AS a,
                   count(CASE WHEN n:Part THEN 1 END) AS p,
                   count(CASE WHEN n:Standard THEN 1 END) AS s
        """).single()
        yield emit(
            f"\n🎉 入库完成！Assembly:{r2['a']}  Part:{r2['p']}  Standard:{r2['s']}  "
            f"关系:{len(edges)} 条  \n"
            f"可视化查看：http://localhost:7474"
        )


def _query_bom_text(question: str) -> str:
    """从 Neo4j 查询与问题相关的 BOM 信息，返回格式化文本。"""
    driver = _get_neo4j()
    if driver is None:
        return ""

    KNOWN_KEYWORDS = [
        "风扇", "压气机", "高压压气机", "低压压气机", "燃烧室",
        "高压涡轮", "低压涡轮", "涡轮", "附件", "尾喷管",
        "叶片", "涡轮盘", "火焰筒", "喷嘴", "机匣", "转子", "静子",
    ]
    keywords = [kw for kw in KNOWN_KEYWORDS if kw in question] or [question[:15]]

    with driver.session() as session:
        lines = []
        seen = set()
        for kw in keywords:
            rows = session.run("""
                MATCH (parent) WHERE parent.part_name CONTAINS $kw
                OPTIONAL MATCH (child)-[:CHILD_OF*1..2]->(parent)
                WITH parent, collect(child) AS children
                RETURN parent.part_name AS module,
                       parent.part_id   AS module_id,
                       parent.spec      AS spec,
                       [c IN children | {
                         name:c.part_name, id:c.part_id,
                         qty:c.qty, unit:c.unit,
                         material:c.material, spec:c.spec, note:c.note
                       }] AS parts
            """, kw=kw).data()

            for r in rows:
                mod = r.get("module", "")
                if not mod or mod in seen:
                    continue
                seen.add(mod)
                lines.append(f"【{mod}】({r.get('module_id','')})")
                if r.get("spec"):
                    lines.append(f"  规格：{r['spec']}")
                for p in (r.get("parts") or []):
                    mat  = f" 材料:{p['material']}" if p.get("material") else ""
                    spec = f" 规格:{p['spec']}"     if p.get("spec") else ""
                    note = f" 备注:{p['note']}"     if p.get("note") else ""
                    lines.append(
                        f"  - {p['name']}({p['id']}) ×{p['qty']}{p['unit']}{mat}{spec}{note}"
                    )
        return "\n".join(lines) if lines else ""


ASSEMBLY_SYSTEM_PROMPT = """你是一名资深航空发动机装配工程师，熟悉涡扇发动机的结构设计和装配工艺。
根据提供的 BOM 零件清单和技术知识库内容，生成详细的装配方案。
方案须包含：零件清单确认、装配顺序（步骤编号）、工艺要点（力矩/公差/工装）、注意事项。
若 BOM 或知识库无相关数据，请说明并基于通用工程知识回答。"""


def assembly_chat(message: str, history: list):
    """
    装配方案问答（流式）：并行查 BOM 图谱 + RAG 知识库，再流式生成装配方案。
    比 LangChain ReAct Agent 更快（无多轮 LLM 推理决策），直接两路融合。
    """
    # 1. 并行查询两路信息
    bom_text  = _query_bom_text(message)
    rag_chunks = retrieve(message)   # 复用现有向量检索

    # 2. 构建 prompt
    rag_context = ""
    if rag_chunks:
        rag_context = "\n\n".join(
            f"[{i+1}] 来源:{c['source']}\n{c['text']}"
            for i, c in enumerate(rag_chunks)
        )

    sections = []
    if bom_text:
        sections.append(f"【BOM 零件清单（来自图数据库）】\n{bom_text}")
    if rag_context:
        sections.append(f"【技术知识库（来自教材）】\n{rag_context}")

    if sections:
        user_content = "\n\n".join(sections) + f"\n\n【用户问题】\n{message}"
    else:
        user_content = message

    # 3. 构建多轮历史
    messages = [{"role": "system", "content": ASSEMBLY_SYSTEM_PROMPT}]
    for item in history[-8:]:
        if isinstance(item, dict):
            if item.get("role") in ("user", "assistant"):
                messages.append({"role": item["role"], "content": item.get("content") or ""})
        else:
            if item[0]: messages.append({"role": "user",      "content": item[0]})
            if item[1]: messages.append({"role": "assistant",  "content": item[1]})
    messages.append({"role": "user", "content": user_content})

    # 4. 流式生成
    full_answer = ""
    try:
        stream = llm_client.chat.completions.create(
            model=LLM_MODEL, messages=messages, temperature=0.3, stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            full_answer += delta
            yield full_answer
    except Exception as e:
        yield f"❌ LLM 调用失败：{e}"
        return

    # 5. 追加 BOM 来源注脚
    if bom_text:
        full_answer += "\n\n---\n**🔩 BOM 数据来源**：Neo4j 图数据库"
    if rag_chunks:
        full_answer += "\n\n---\n**📚 知识库参考**\n" + "".join(
            f"**[{i+1}] {c['source']}**  \n_{c['text'][:80].replace(chr(10),' ')}…_\n"
            for i, c in enumerate(rag_chunks, 1)
        )
    yield full_answer


# ==========================================
# Gradio UI 布局
# ==========================================

with gr.Blocks(title="航空发动机知识库 & 装配系统") as demo:
    gr.Markdown("## 🚀 航空发动机知识库 & 装配系统")
    gr.Markdown(
        f"LLM：`{_active_model_label}` &nbsp;·&nbsp; Embedding：`{EMBEDDING_MODEL_NAME}`"
    )

    with gr.Tabs():

        # ── Tab 1：RAG 知识库问答 ──────────────────────────────────────────
        with gr.Tab("📖 RAG 知识库问答"):

            with gr.Accordion("📂 知识库管理", open=False):
                status_md = gr.Markdown(_status())
                with gr.Row():
                    ingest_btn = gr.Button("🔄 扫描 data/ 并入库（增量）", variant="primary", scale=2)
                    clear_btn  = gr.Button("🗑️ 清空后重建", variant="stop", scale=1)
                ingest_log = gr.Textbox(
                    label="入库日志", lines=10, interactive=False,
                    placeholder="点击按钮后这里会显示入库进度…",
                )

            with gr.Accordion("📊 性能评估", open=False):
                gr.Markdown(
                    "**召回诊断**：秒出，无需 LLM。&nbsp;&nbsp;"
                    "**LLM 打分**：三维打分，约 1–2 分钟。&nbsp;&nbsp;"
                    "**RAGAS 评估**：完整链路，约 5–15 分钟。"
                )
                with gr.Row():
                    diagnose_btn = gr.Button("🔍 召回诊断", variant="primary", scale=2)
                    judge_btn    = gr.Button("⚖️ LLM 打分", variant="secondary", scale=1)
                    ragas_btn    = gr.Button("🧪 RAGAS 评估", variant="secondary", scale=1)
                eval_log = gr.Textbox(
                    label="评估结果", lines=25, max_lines=60, interactive=False,
                    placeholder="点击按钮后这里会实时显示评估报告…",
                )

            # RAG 问答对话区
            rag_chatbot = gr.Chatbot(
                height=460, render_markdown=True, label="知识库问答",
                placeholder="<center>请先完成知识库入库，再开始提问</center>",
            )
            with gr.Row():
                rag_input = gr.Textbox(
                    placeholder="输入问题，按 Enter 发送…", scale=9, show_label=False,
                )
                rag_send_btn = gr.Button("发送", variant="primary", scale=1)
            with gr.Row():
                rag_clear_btn = gr.Button("🗑️ 清空对话", scale=1)
                gr.Examples(
                    examples=["RAG是什么？", "压气机的工作原理？", "涡轮叶片如何冷却？"],
                    inputs=rag_input, label="示例问题",
                )

        # ── Tab 2：BOM 装配系统 ────────────────────────────────────────────
        with gr.Tab("🔩 BOM 装配系统"):

            with gr.Accordion("⚙️ Neo4j 图数据库状态", open=True):
                neo4j_status_md = gr.Markdown(
                    "点击「检测连接」按钮查看 Neo4j 状态"
                )
                with gr.Row():
                    neo4j_check_btn = gr.Button("🔍 检测连接", variant="primary", scale=1)
                    with gr.Column(scale=3):
                        gr.Markdown(
                            f"默认地址：`{NEO4J_URI}` &nbsp; "
                            "启动命令：`docker start neo4j`"
                        )

            with gr.Accordion("📋 BOM 入库", open=False):
                gr.Markdown(
                    "上传 BOM Excel 文件（或留空使用内置测试数据 `data/test_bom.xlsx`）。  \n"
                    "BOM 格式要求：含 `level_code / part_id / part_name / category / qty / unit` 列。"
                )
                bom_file_input = gr.File(
                    label="BOM Excel 文件（留空则用默认测试数据）",
                    file_types=[".xlsx"],
                )
                with gr.Row():
                    bom_ingest_btn = gr.Button("📥 入库（增量）", variant="primary", scale=2)
                    bom_clear_btn  = gr.Button("🗑️ 清空后重建", variant="stop", scale=1)
                bom_ingest_log = gr.Textbox(
                    label="入库日志", lines=12, interactive=False,
                    placeholder="点击「入库」按钮后这里会显示进度…",
                )

            # 装配方案问答区
            gr.Markdown("### 💬 装配方案生成")
            gr.Markdown(
                "Agent 自动查询 **BOM 图谱**（零件清单/材料/规格）+ **RAG 知识库**（工艺规范）  \n"
                "并融合两路信息，生成完整装配方案。"
            )
            assembly_chatbot = gr.Chatbot(
                height=500, render_markdown=True, label="装配方案",
                placeholder=(
                    "<center>Neo4j 连接后即可开始提问<br/>"
                    "示例：生成高压涡轮模块的完整装配方案</center>"
                ),
            )
            with gr.Row():
                assembly_input = gr.Textbox(
                    placeholder="输入问题，如：生成高压涡轮模块装配方案…",
                    scale=9, show_label=False,
                )
                assembly_send_btn = gr.Button("发送", variant="primary", scale=1)
            with gr.Row():
                assembly_clear_btn = gr.Button("🗑️ 清空对话", scale=1)
                gr.Examples(
                    examples=[
                        "生成高压涡轮模块的完整装配方案",
                        "燃烧室模块包含哪些零件？装配注意事项是什么？",
                        "风扇叶片安装有哪些工艺要求？",
                    ],
                    inputs=assembly_input, label="示例问题",
                )

    # ── 事件绑定 ─────────────────────────────────────────────────────────────

    # Tab 1：知识库管理
    def do_ingest():       yield from run_ingest(clear_first=False)
    def do_clear_ingest(): yield from run_ingest(clear_first=True)
    ingest_btn.click(fn=do_ingest,       outputs=[ingest_log, status_md])
    clear_btn.click( fn=do_clear_ingest, outputs=[ingest_log, status_md])

    # Tab 1：性能评估
    def do_eval_diagnose(): yield from run_eval_diagnose()
    def do_eval_judge():    yield from run_eval_judge()
    def do_eval_ragas():    yield from run_eval_ragas()
    diagnose_btn.click(fn=do_eval_diagnose, outputs=eval_log)
    judge_btn.click(   fn=do_eval_judge,    outputs=eval_log)
    ragas_btn.click(   fn=do_eval_ragas,    outputs=eval_log)

    # Tab 1：RAG 问答对话（流式）
    def rag_submit(message, history):
        history = history or []
        if not message.strip():
            yield "", history
            return
        history = history + [{"role": "user", "content": message}]
        history.append({"role": "assistant", "content": ""})
        yield "", history
        for partial in chat(message, history[:-2]):
            history[-1]["content"] = partial
            yield "", history

    rag_send_btn.click(fn=rag_submit,  inputs=[rag_input, rag_chatbot], outputs=[rag_input, rag_chatbot])
    rag_input.submit(  fn=rag_submit,  inputs=[rag_input, rag_chatbot], outputs=[rag_input, rag_chatbot])
    rag_clear_btn.click(fn=lambda: ([], ""), outputs=[rag_chatbot, rag_input])

    # Tab 2：Neo4j 状态检测
    neo4j_check_btn.click(fn=check_neo4j_status, outputs=neo4j_status_md)

    # Tab 2：BOM 入库
    def do_bom_ingest(file_obj):       yield from run_bom_ingest_ui(file_obj, clear_first=False)
    def do_bom_clear_ingest(file_obj): yield from run_bom_ingest_ui(file_obj, clear_first=True)
    bom_ingest_btn.click(fn=do_bom_ingest,       inputs=bom_file_input, outputs=bom_ingest_log)
    bom_clear_btn.click( fn=do_bom_clear_ingest, inputs=bom_file_input, outputs=bom_ingest_log)

    # Tab 2：装配方案问答（流式）
    def assembly_submit(message, history):
        history = history or []
        if not message.strip():
            yield "", history
            return
        history = history + [{"role": "user", "content": message}]
        history.append({"role": "assistant", "content": ""})
        yield "", history
        for partial in assembly_chat(message, history[:-2]):
            history[-1]["content"] = partial
            yield "", history

    assembly_send_btn.click(fn=assembly_submit, inputs=[assembly_input, assembly_chatbot], outputs=[assembly_input, assembly_chatbot])
    assembly_input.submit(  fn=assembly_submit, inputs=[assembly_input, assembly_chatbot], outputs=[assembly_input, assembly_chatbot])
    assembly_clear_btn.click(fn=lambda: ([], ""), outputs=[assembly_chatbot, assembly_input])


if __name__ == "__main__":
    # Windows 代理可能导致本地请求被拦截，显式绕过代理
    os.environ.setdefault("NO_PROXY", "127.0.0.1,localhost")
    os.environ.setdefault("no_proxy", "127.0.0.1,localhost")
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        show_error=True,
        theme=gr.themes.Soft(),
    )
