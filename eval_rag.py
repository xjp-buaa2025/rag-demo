"""
eval_rag.py — RAG 系统性能评估工具

两种模式：
  --mode diagnose（默认）
    对内置测试题逐一做向量检索，打印召回质量报告：
    - 每道题召回的 Top-K chunks（片段 + 来源 + 余弦距离）
    - 整体距离统计（均值/中位数/最值）
    - 知识库 chunk 长度分布

  --mode judge
    在 diagnose 基础上，追加 LLM-as-Judge 打分：
    - 相关性 0-5：检索片段与问题是否相关
    - 完整性 0-5：片段是否涵盖回答该问题的信息
    - 可回答性 0-5：基于片段 LLM 能否给出满意答案
    - 输出每道题打分 + 三个维度全局均值

运行方式：
  PYTHONUTF8=1 python eval_rag.py --mode diagnose
  PYTHONUTF8=1 python eval_rag.py --mode judge

如何解读结果：
  余弦距离范围 [0, 2]，越小越好
  < 0.3   高度相关，召回质量优秀
  0.3-0.6 中等，基本可用
  0.6-0.8 较差，建议增大 chunk_size 或 TOP_K
  > 0.8   召回几乎无效，需要排查 Embedding 或切片策略
"""

import os
import sys
import json
import argparse
import statistics
from typing import List

from dotenv import load_dotenv
import chromadb
from sentence_transformers import SentenceTransformer
from openai import OpenAI

load_dotenv()
sys.path.append(os.path.join(os.path.dirname(__file__), 'document_processing'))


# ==========================================
# 配置
# ==========================================

CHROMA_DB_DIR = os.path.join(os.path.dirname(__file__), 'storage', 'chroma_db')
COLLECTION_NAME = "local_rag_knowledge"
EMBEDDING_MODEL_NAME = "BAAI/bge-m3"
TOP_K = 5  # 评估时多召回一个，覆盖更多候选

LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.siliconflow.cn/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "Qwen/Qwen2.5-14B-Instruct")

MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "").strip()
MINIMAX_BASE_URL = os.getenv("MINIMAX_BASE_URL", "https://api.minimaxi.com/v1")
MINIMAX_MODEL = os.getenv("MINIMAX_MODEL", "MiniMax-M2.5")

# 内置测试题集（航空发动机领域）
TEST_QUESTIONS = [
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


# ==========================================
# Embedding 包装（与 main_ingest.py 保持一致）
# ==========================================

class LocalEmbeddingFunction:
    def __init__(self, model_name: str):
        print(f"正在加载 Embedding 模型: {model_name} ...")
        self.model = SentenceTransformer(model_name)
        self._model_name = model_name

    def name(self) -> str:
        return self._model_name

    def __call__(self, input: List[str]) -> List[List[float]]:
        return self.model.encode(input).tolist()


# ==========================================
# 工具函数
# ==========================================

def retrieve_chunks(collection, embedding_func, query: str, top_k: int = TOP_K):
    """向量检索，返回 [{text, source, page, distance}, ...]"""
    n = min(top_k, collection.count())
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


def get_all_chunk_lengths(collection) -> List[int]:
    """获取知识库中所有 chunk 的长度，用于分布分析"""
    total = collection.count()
    if total == 0:
        return []
    # ChromaDB 支持按 offset/limit 分页读取
    batch_size = 500
    lengths = []
    offset = 0
    while offset < total:
        result = collection.get(
            limit=batch_size,
            offset=offset,
            include=["documents"],
        )
        for doc in result["documents"]:
            lengths.append(len(doc))
        offset += batch_size
    return lengths


def print_separator(char="─", width=72):
    print(char * width)


def fmt_snippet(text: str, max_len: int = 100) -> str:
    """截断文本用于展示"""
    text = text.replace("\n", " ").strip()
    return text[:max_len] + "…" if len(text) > max_len else text


# ==========================================
# Mode 1: Diagnose
# ==========================================

def run_diagnose(collection, embedding_func):
    print("\n" + "=" * 72)
    print("  RAG 召回质量诊断报告")
    print("=" * 72)

    # 1. 知识库基本信息
    total_chunks = collection.count()
    print(f"\n知识库：{COLLECTION_NAME}")
    print(f"文档块总数：{total_chunks}")
    if total_chunks == 0:
        print("⚠️  知识库为空，请先运行 main_ingest.py 入库后再评估。")
        return

    # 2. Chunk 长度分布
    print("\n--- 文档块长度分布 ---")
    lengths = get_all_chunk_lengths(collection)
    if lengths:
        print(f"  均值：{statistics.mean(lengths):.0f} 字符")
        print(f"  中位数：{statistics.median(lengths):.0f} 字符")
        print(f"  最小值：{min(lengths)} 字符")
        print(f"  最大值：{max(lengths)} 字符")
        # 分桶统计
        buckets = {"<100": 0, "100-300": 0, "300-500": 0, "500-800": 0, ">800": 0}
        for l in lengths:
            if l < 100:
                buckets["<100"] += 1
            elif l < 300:
                buckets["100-300"] += 1
            elif l < 500:
                buckets["300-500"] += 1
            elif l < 800:
                buckets["500-800"] += 1
            else:
                buckets[">800"] += 1
        print("  长度分布：")
        for bucket, count in buckets.items():
            bar = "█" * (count * 20 // max(buckets.values()) if max(buckets.values()) > 0 else 0)
            print(f"    {bucket:>10}  {bar:<20} {count} 块 ({count/len(lengths)*100:.1f}%)")

    # 3. 逐题检索报告
    all_distances = []
    print(f"\n--- 逐题召回详情（Top-{TOP_K}，共 {len(TEST_QUESTIONS)} 道题）---")

    for i, question in enumerate(TEST_QUESTIONS, 1):
        print_separator()
        print(f"[{i:02d}] {question}")
        chunks = retrieve_chunks(collection, embedding_func, question)

        if not chunks:
            print("  无召回结果")
            continue

        distances = [c["distance"] for c in chunks]
        all_distances.extend(distances)
        avg_dist = statistics.mean(distances)

        # 质量判断
        if avg_dist < 0.3:
            quality = "优秀"
        elif avg_dist < 0.6:
            quality = "一般"
        elif avg_dist < 0.8:
            quality = "较差"
        else:
            quality = "很差"

        print(f"  平均距离: {avg_dist:.4f}  ({quality})")
        print()
        for j, chunk in enumerate(chunks, 1):
            dist_bar = "█" * max(1, int((1 - chunk["distance"] / 2) * 10))
            print(f"  [{j}] dist={chunk['distance']:.4f} {dist_bar}  来源: {chunk['source']}")
            print(f"      {fmt_snippet(chunk['text'])}")
        print()

    # 4. 全局距离统计
    if all_distances:
        print_separator("=")
        print("全局召回距离统计")
        print_separator()
        print(f"  均值:    {statistics.mean(all_distances):.4f}")
        print(f"  中位数:  {statistics.median(all_distances):.4f}")
        print(f"  最小值:  {min(all_distances):.4f}")
        print(f"  最大值:  {max(all_distances):.4f}")
        if len(all_distances) > 1:
            print(f"  标准差:  {statistics.stdev(all_distances):.4f}")

        # 判断整体质量
        avg = statistics.mean(all_distances)
        print()
        if avg < 0.3:
            print("  评估：召回质量优秀，embedding 对齐良好。")
        elif avg < 0.6:
            print("  评估：召回质量一般，可考虑增大 chunk_size 或 TOP_K 提升覆盖。")
        elif avg < 0.8:
            print("  评估：召回质量较差。建议排查：chunk_size 是否过小、入库文档质量、Embedding 模型适配性。")
        else:
            print("  评估：召回质量很差，检索结果基本无效。请检查 Embedding 模型是否正确加载，以及知识库内容是否与问题领域匹配。")
    print_separator("=")


# ==========================================
# Mode 2: LLM-as-Judge
# ==========================================

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


def judge_question(llm_client, question: str, chunks: List[dict]) -> dict:
    """调用 LLM 对一道题的召回结果打分，返回打分字典"""
    context = "\n\n".join(
        f"[{i+1}] 来源: {c['source']}\n{c['text']}"
        for i, c in enumerate(chunks)
    )
    prompt = JUDGE_PROMPT_TMPL.format(question=question, context=context)

    try:
        response = llm_client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,  # 打分用确定性模式
        )
        raw = response.choices[0].message.content.strip()
        # 提取 JSON（有时 LLM 会在前后加说明文字）
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start >= 0 and end > start:
            raw = raw[start:end]
        return json.loads(raw)
    except Exception as e:
        print(f"  [打分失败] {e}")
        return {}


def run_judge(collection, embedding_func, llm_client):
    print("\n" + "=" * 72)
    print("  RAG LLM-as-Judge 评估报告")
    print("=" * 72)

    total_chunks = collection.count()
    if total_chunks == 0:
        print("⚠️  知识库为空，请先运行 main_ingest.py 入库。")
        return

    all_scores = {"relevance": [], "completeness": [], "answerability": []}

    for i, question in enumerate(TEST_QUESTIONS, 1):
        print_separator()
        print(f"[{i:02d}] {question}")
        chunks = retrieve_chunks(collection, embedding_func, question)

        if not chunks:
            print("  无召回结果，跳过")
            continue

        avg_dist = statistics.mean(c["distance"] for c in chunks)
        print(f"  平均召回距离: {avg_dist:.4f}")
        print("  正在请求 LLM 打分...", end="", flush=True)

        scores = judge_question(llm_client, question, chunks)
        if not scores:
            print(" 失败")
            continue

        print(" 完成")
        r = scores.get("relevance", "N/A")
        c = scores.get("completeness", "N/A")
        a = scores.get("answerability", "N/A")
        print(f"  相关性={r}/5  完整性={c}/5  可回答性={a}/5")
        print(f"  相关性说明: {scores.get('reason_relevance', '')}")
        print(f"  完整性说明: {scores.get('reason_completeness', '')}")
        print(f"  可回答性说明: {scores.get('reason_answerability', '')}")

        for key in all_scores:
            v = scores.get(key)
            if isinstance(v, (int, float)):
                all_scores[key].append(v)

    # 全局平均分
    print_separator("=")
    print("全局 LLM-as-Judge 评分汇总")
    print_separator()
    for dim, label in [("relevance", "相关性"), ("completeness", "完整性"), ("answerability", "可回答性")]:
        vals = all_scores[dim]
        if vals:
            avg = statistics.mean(vals)
            stars = "★" * round(avg) + "☆" * (5 - round(avg))
            print(f"  {label}: {avg:.2f}/5  {stars}")
        else:
            print(f"  {label}: 无数据")

    total_avg = statistics.mean(
        v for vals in all_scores.values() for v in vals
    ) if any(all_scores.values()) else 0
    print(f"\n  综合得分: {total_avg:.2f}/5")
    if total_avg >= 4:
        print("  评估：RAG 整体质量优秀。")
    elif total_avg >= 3:
        print("  评估：RAG 质量良好，有提升空间。")
    elif total_avg >= 2:
        print("  评估：RAG 质量较差，建议调整 chunk_size / TOP_K / 重新入库。")
    else:
        print("  评估：RAG 质量很差，请检查知识库内容和检索配置。")
    print_separator("=")


# ==========================================
# RAGAS 评估 Prompt 模板
# ==========================================

CONTEXT_RELEVANCE_PROMPT = """你是一名 RAG 评估专家。给定以下问题和检索到的上下文，请提取上下文中与问题直接相关的句子。
每行输出一个相关句子，不要输出任何编号或解释。如果没有相关句子，仅输出 NONE。

【问题】
{question}

【上下文】
{context}"""

FAITHFULNESS_DECOMPOSE_PROMPT = """将以下答案拆解为原子化的事实声明（每个声明是一个简短、独立可验证的陈述句）。
每行输出一条声明，不要编号，不要解释。

【答案】
{answer}"""

FAITHFULNESS_VERIFY_PROMPT = """给定以下上下文和一条声明，判断该声明是否完全由上下文内容支撑。
只回答 YES 或 NO，不要有任何其他内容。

【上下文】
{context}

【声明】
{claim}"""

ANSWER_RELEVANCE_PROMPT = """给定以下答案，生成 3 个可能引发该答案的不同问题。
每行输出一个问题，不要编号，不要解释。

【答案】
{answer}"""

RAG_SYSTEM_PROMPT = """你是一个专业的知识库问答助手。请严格根据提供的参考资料回答用户问题。
如果参考资料中没有相关信息，请如实说明"知识库中没有找到相关内容"，不要凭空捏造。
回答要详细、准确、有条理。"""


# ==========================================
# RAGAS 三指标评估
# ==========================================

def generate_answer(llm_client, question: str, chunks: List[dict]) -> str:
    """用标准 RAG 流程（检索 + LLM）生成答案，供 RAGAS 各指标评估共用。"""
    context_parts = [f"[{i+1}] 来源: {c['source']}\n{c['text']}" for i, c in enumerate(chunks)]
    user_content = "参考资料：\n" + "\n\n".join(context_parts) + f"\n\n用户问题：{question}"
    try:
        resp = llm_client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": RAG_SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            temperature=0.3,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"  [答案生成失败] {e}")
        return ""


def eval_context_relevance(llm_client, question: str, chunks: List[dict]) -> float:
    """
    上下文相关性：检索片段中有多大比例与问题直接相关。
    Score = 提取的相关句子数 / chunks 总句子数，范围 [0, 1]。
    评估失败返回 -1.0。
    """
    import re
    context = "\n\n".join(c["text"] for c in chunks)
    all_sents = [s.strip() for s in re.split(r'[。！？\n]+', context) if s.strip()]
    total = len(all_sents)
    if total == 0:
        return 0.0
    prompt = CONTEXT_RELEVANCE_PROMPT.format(question=question, context=context)
    try:
        resp = llm_client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.01,
        )
        raw = resp.choices[0].message.content.strip()
        if not raw or raw.upper() == "NONE":
            return 0.0
        relevant = [l.strip() for l in raw.split("\n") if l.strip() and l.strip().upper() != "NONE"]
        return min(len(relevant) / total, 1.0)
    except Exception as e:
        print(f"  [Context Relevance 失败] {e}")
        return -1.0


def eval_faithfulness(llm_client, question: str, answer: str, chunks: List[dict]) -> tuple:
    """
    忠实度：答案中的原子声明有多少比例能从检索内容中找到支撑。
    返回 (score, n_yes, n_total)；评估失败返回 (-1.0, 0, 0)。
    """
    context = "\n\n".join(f"[{i+1}] {c['text']}" for i, c in enumerate(chunks))

    # Step 1: 拆解答案为原子声明
    try:
        resp = llm_client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": FAITHFULNESS_DECOMPOSE_PROMPT.format(answer=answer)}],
            temperature=0.01,
        )
        claims = [l.strip() for l in resp.choices[0].message.content.strip().split("\n") if l.strip()]
    except Exception as e:
        print(f"  [Faithfulness 拆解失败] {e}")
        return (-1.0, 0, 0)

    if not claims:
        return (0.0, 0, 0)

    # Step 2: 逐条验证
    n_yes = 0
    for claim in claims:
        try:
            resp = llm_client.chat.completions.create(
                model=LLM_MODEL,
                messages=[{"role": "user", "content": FAITHFULNESS_VERIFY_PROMPT.format(context=context, claim=claim)}],
                temperature=0.01,
            )
            if "YES" in resp.choices[0].message.content.strip().upper():
                n_yes += 1
        except Exception as e:
            print(f"  [Faithfulness 验证失败] {e}")

    return (n_yes / len(claims), n_yes, len(claims))


def eval_answer_relevance(embedding_func, llm_client, question: str, answer: str) -> float:
    """
    回答相关性：从答案逆向生成 3 个问题，计算与原问题的语义相似度均值。
    使用归一化 embedding 点积作为余弦相似度，范围 [0, 1]。
    评估失败返回 -1.0。
    """
    try:
        resp = llm_client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": ANSWER_RELEVANCE_PROMPT.format(answer=answer)}],
            temperature=0.3,
        )
        gen_qs = [l.strip() for l in resp.choices[0].message.content.strip().split("\n") if l.strip()][:3]
    except Exception as e:
        print(f"  [Answer Relevance 生成失败] {e}")
        return -1.0

    if not gen_qs:
        return 0.0

    # 归一化 embedding 后用点积计算余弦相似度
    q_emb = embedding_func.model.encode([question], normalize_embeddings=True)[0].tolist()
    sims = []
    for gq in gen_qs:
        gq_emb = embedding_func.model.encode([gq], normalize_embeddings=True)[0].tolist()
        sim = max(0.0, sum(a * b for a, b in zip(q_emb, gq_emb)))
        sims.append(sim)
    return statistics.mean(sims)


def run_ragas(collection, embedding_func, llm_client):
    """
    RAGAS 三指标完整评估：
      - Context Relevance（上下文相关性）
      - Faithfulness（忠实度 / 幻觉检测）
      - Answer Relevance（回答相关性）

    注意：每道题需要多次 LLM 调用（生成答案 + CR + Faithfulness × N声明 + AR），
    10 道题约需 5–15 分钟，请耐心等待。
    """
    print("\n" + "=" * 72)
    print("  RAGAS 三指标评估报告")
    print("  Context Relevance / Faithfulness / Answer Relevance")
    print("=" * 72)

    if collection.count() == 0:
        print("⚠️  知识库为空，请先运行 main_ingest.py 入库。")
        return

    all_cr, all_f, all_ar = [], [], []

    for i, question in enumerate(TEST_QUESTIONS, 1):
        print_separator()
        print(f"[{i:02d}] {question}")

        chunks = retrieve_chunks(collection, embedding_func, question)
        if not chunks:
            print("  无召回结果，跳过")
            continue

        avg_dist = statistics.mean(c["distance"] for c in chunks)
        print(f"  召回距离: {avg_dist:.4f}")

        # 生成答案（CR / Faithfulness / Answer Relevance 共用）
        print("  生成答案…", end="", flush=True)
        answer = generate_answer(llm_client, question, chunks)
        if not answer:
            print(" 失败，跳过")
            continue
        print(f" 完成\n  答案: {fmt_snippet(answer, 120)}")

        # Context Relevance
        print("  [CR] 计算 Context Relevance…", end="", flush=True)
        cr = eval_context_relevance(llm_client, question, chunks)
        print(f" {cr:.3f}" if cr >= 0 else " 失败")

        # Faithfulness
        print("  [F ] 计算 Faithfulness…", end="", flush=True)
        f_score, n_yes, n_total = eval_faithfulness(llm_client, question, answer, chunks)
        if f_score >= 0:
            print(f" {f_score:.3f}  ({n_yes}/{n_total} 声明有支撑)")
        else:
            print(" 失败")

        # Answer Relevance
        print("  [AR] 计算 Answer Relevance…", end="", flush=True)
        ar = eval_answer_relevance(embedding_func, llm_client, question, answer)
        print(f" {ar:.3f}" if ar >= 0 else " 失败")

        # 本题汇总框
        print(f"\n  ┌─ Context Relevance:  {cr:.3f}" if cr >= 0 else "  ┌─ Context Relevance:  失败")
        print(f"  ├─ Faithfulness:       {f_score:.3f}" if f_score >= 0 else "  ├─ Faithfulness:       失败")
        print(f"  └─ Answer Relevance:   {ar:.3f}" if ar >= 0 else "  └─ Answer Relevance:   失败")

        if cr >= 0:     all_cr.append(cr)
        if f_score >= 0: all_f.append(f_score)
        if ar >= 0:     all_ar.append(ar)

    # 全局汇总
    print_separator("=")
    print("RAGAS 全局评分汇总")
    print_separator()

    def fmt_score(vals, label):
        if vals:
            avg = statistics.mean(vals)
            bar = "█" * int(avg * 10) + "░" * (10 - int(avg * 10))
            print(f"  {label:22s}  {avg:.3f}  [{bar}]")
        else:
            print(f"  {label:22s}  无数据")

    fmt_score(all_cr, "Context Relevance")
    fmt_score(all_f,  "Faithfulness")
    fmt_score(all_ar, "Answer Relevance")

    all_vals = all_cr + all_f + all_ar
    if all_vals:
        ragas_score = statistics.mean(all_vals)
        print(f"\n  RAGAS 综合分:  {ragas_score:.3f} / 1.0")
        if ragas_score >= 0.8:
            print("  ✅ RAG 整体质量优秀。")
        elif ragas_score >= 0.6:
            print("  🟡 RAG 质量良好，有提升空间。")
        elif ragas_score >= 0.4:
            print("  🟠 RAG 质量中等，建议优化 chunk 策略和 TOP_K。")
        else:
            print("  🔴 RAG 质量较差，请检查知识库内容、Embedding 模型和生成策略。")
    print_separator("=")


# ==========================================
# main
# ==========================================

def main():
    parser = argparse.ArgumentParser(description="RAG 性能评估工具")
    parser.add_argument(
        "--mode",
        choices=["diagnose", "judge", "ragas"],
        default="diagnose",
        help="diagnose: 检索诊断报告（默认）；judge: LLM-as-Judge 打分；ragas: RAGAS 三指标评估",
    )
    args = parser.parse_args()

    # 初始化 Embedding 模型和 ChromaDB
    embedding_func = LocalEmbeddingFunction(EMBEDDING_MODEL_NAME)
    chroma_client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
    collection = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_func,
        metadata={"hnsw:space": "cosine"},
    )

    if args.mode == "diagnose":
        run_diagnose(collection, embedding_func)
    else:
        # 优先使用 MiniMax；未配置时退回 SiliconFlow
        global LLM_MODEL
        if MINIMAX_API_KEY:
            llm_client = OpenAI(api_key=MINIMAX_API_KEY, base_url=MINIMAX_BASE_URL)
            LLM_MODEL = MINIMAX_MODEL  # 让所有函数都使用 MiniMax 模型名
            print(f"LLM: MiniMax ({MINIMAX_MODEL})")
        else:
            llm_client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)
            print(f"LLM: SiliconFlow ({LLM_MODEL})")
        if args.mode == "judge":
            run_diagnose(collection, embedding_func)
            print()
            run_judge(collection, embedding_func, llm_client)
        else:  # ragas
            run_ragas(collection, embedding_func, llm_client)


if __name__ == "__main__":
    main()
