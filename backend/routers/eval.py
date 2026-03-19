"""
backend/routers/eval.py — RAG 性能评估接口

POST /eval/diagnose  — 向量召回诊断（秒级，无 LLM）→ SSE
POST /eval/judge     — LLM-as-Judge 三维打分（~1-2 分钟）→ SSE
POST /eval/ragas     — RAGAS 三指标评估（~5-15 分钟）→ SSE
POST /eval/ranked    — 有监督检索指标 Recall@K/MRR/NDCG@K（LLM 自动标注）→ SSE

全部迁移自 app.py：run_eval_diagnose()、run_eval_judge()、run_eval_ragas()。
业务逻辑与 app.py 完全一致，仅去掉对全局变量的直接引用，改为通过 state 传入。
"""

import json
import math
import re
import statistics
from fastapi import APIRouter, Depends, Request
from backend.deps import get_state
from backend.state import AppState
from backend.sse import log_gen_to_sse

router = APIRouter(prefix="/eval")

EVAL_TOP_K = 5

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

SYSTEM_PROMPT = """你是一个专业的知识库问答助手。请严格根据提供的参考资料回答用户问题。
如果参考资料中没有相关信息，请如实说明"知识库中没有找到相关内容"，不要凭空捏造。
回答要详细、准确、有条理，尽量引用原文中的具体数据和技术细节，不要省略重要信息。"""

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
# 辅助：评估专用检索
# ==========================================

def _retrieve_eval(state: AppState, query: str):
    n = min(EVAL_TOP_K, state.collection.count())
    if n == 0:
        return []
    q_emb = state.embedding_func([query])[0]
    results = state.collection.query(
        query_embeddings=[q_emb],
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


def _get_chunk_lengths(state: AppState):
    total = state.collection.count()
    lengths, offset = [], 0
    while offset < total:
        result = state.collection.get(limit=500, offset=offset, include=["documents"])
        lengths.extend(len(doc) for doc in result["documents"])
        offset += 500
    return lengths


# ==========================================
# POST /eval/diagnose
# ==========================================

@router.post("/diagnose", summary="向量召回诊断（SSE）")
def eval_diagnose(state: AppState = Depends(get_state)):
    return log_gen_to_sse(_run_diagnose(state))


def _run_diagnose(state: AppState):
    lines = []

    def emit(msg=""):
        lines.append(msg)
        return "\n".join(lines)

    total = state.collection.count()
    yield emit("=" * 60)
    yield emit("  RAG 召回质量诊断报告")
    yield emit("=" * 60)
    yield emit(f"知识库文档块总数：{total}")
    if total == 0:
        yield emit("⚠️ 知识库为空，请先完成入库后再评估。")
        return

    yield emit("\n--- 文档块长度分布 ---")
    yield emit("正在统计，请稍候…")
    lengths = _get_chunk_lengths(state)
    lines.pop()
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

    all_distances = []
    yield emit(f"\n--- 逐题召回详情（Top-{EVAL_TOP_K}）---")
    for i, question in enumerate(EVAL_QUESTIONS, 1):
        yield emit(f"\n[{i:02d}] {question}")
        chunks = _retrieve_eval(state, question)
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


# ==========================================
# POST /eval/judge
# ==========================================

@router.post("/judge", summary="LLM-as-Judge 评估（SSE）")
def eval_judge(request: Request, state: AppState = Depends(get_state)):
    llm_model = request.app.state.llm_model
    return log_gen_to_sse(_run_judge(state, llm_model))


def _run_judge(state: AppState, llm_model: str):
    lines = []

    def emit(msg=""):
        lines.append(msg)
        return "\n".join(lines)

    total = state.collection.count()
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
        chunks = _retrieve_eval(state, question)
        if not chunks:
            yield emit("  无召回结果，跳过")
            continue

        avg_dist = statistics.mean(c["distance"] for c in chunks)
        yield emit(f"  平均召回距离: {avg_dist:.4f}")
        yield emit("  正在请求 LLM 打分…")

        context = "\n\n".join(
            f"[{j+1}] 来源: {c['source']}\n{c['text']}" for j, c in enumerate(chunks)
        )
        prompt = JUDGE_PROMPT_TMPL.format(question=question, context=context)
        try:
            resp = state.llm_client.chat.completions.create(
                model=llm_model,
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

        lines.pop()
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


# ==========================================
# POST /eval/ragas
# ==========================================

@router.post("/ragas", summary="RAGAS 三指标评估（SSE）")
def eval_ragas(request: Request, state: AppState = Depends(get_state)):
    llm_model = request.app.state.llm_model
    return log_gen_to_sse(_run_ragas(state, llm_model))


def _run_ragas(state: AppState, llm_model: str):
    lines = []

    def emit(msg=""):
        lines.append(msg)
        return "\n".join(lines)

    total = state.collection.count()
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
        chunks = _retrieve_eval(state, question)
        if not chunks:
            yield emit("  无召回结果，跳过")
            continue

        avg_dist = statistics.mean(c["distance"] for c in chunks)
        yield emit(f"  召回距离: {avg_dist:.4f}")

        yield emit("  生成答案中…")
        context_parts = [f"[{j+1}] 来源: {c['source']}\n{c['text']}" for j, c in enumerate(chunks)]
        user_content = "参考资料：\n" + "\n\n".join(context_parts) + f"\n\n用户问题：{question}"
        try:
            resp = state.llm_client.chat.completions.create(
                model=llm_model,
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

        # Context Relevance
        yield emit("  [CR] 计算 Context Relevance…")
        context_full = "\n\n".join(c["text"] for c in chunks)
        all_sents = [s.strip() for s in re.split(r'[。！？\n]+', context_full) if s.strip()]
        try:
            cr_resp = state.llm_client.chat.completions.create(
                model=llm_model,
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

        # Faithfulness
        yield emit("  [F ] 计算 Faithfulness（拆解声明 + 逐条核验）…")
        context_numbered = "\n\n".join(f"[{j+1}] {c['text']}" for j, c in enumerate(chunks))
        try:
            decompose_resp = state.llm_client.chat.completions.create(
                model=llm_model,
                messages=[{"role": "user", "content": RAGAS_FAITHFULNESS_DECOMPOSE.format(answer=answer)}],
                temperature=0.01,
            )
            claims = [l.strip() for l in decompose_resp.choices[0].message.content.strip().split("\n") if l.strip()]
            n_yes = 0
            for claim in claims:
                verify_resp = state.llm_client.chat.completions.create(
                    model=llm_model,
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

        # Answer Relevance
        yield emit("  [AR] 计算 Answer Relevance…")
        try:
            ar_resp = state.llm_client.chat.completions.create(
                model=llm_model,
                messages=[{"role": "user", "content": RAGAS_ANSWER_RELEVANCE_PROMPT.format(answer=answer)}],
                temperature=0.3,
            )
            gen_qs = [l.strip() for l in ar_resp.choices[0].message.content.strip().split("\n") if l.strip()][:3]
            q_emb = state.embedding_func.model.encode([question], normalize_embeddings=True)[0].tolist()
            sims = []
            for gq in gen_qs:
                gq_emb = state.embedding_func.model.encode([gq], normalize_embeddings=True)[0].tolist()
                sims.append(max(0.0, sum(a * b for a, b in zip(q_emb, gq_emb))))
            ar = statistics.mean(sims) if sims else 0.0
            lines[-1] = f"  [AR] Answer Relevance: {ar:.3f}"
            yield "\n".join(lines)
            all_ar.append(ar)
        except Exception as ex:
            lines[-1] = f"  [AR] 失败: {ex}"
            yield "\n".join(lines)

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


# ==========================================
# 有监督检索指标：Recall@K / MRR / NDCG@K
# ==========================================

RELEVANCE_JUDGE_PROMPT = """判断以下文档片段是否与问题直接相关。
只回答 YES 或 NO，不要有任何其他内容。

【问题】
{question}

【文档片段】
{chunk}"""

RANKED_RETRIEVE_K = 10  # 构建 ground truth 时取 top-10
RANKED_EVAL_K = 5       # 计算指标时取 top-5


def _annotate_relevance(state: AppState, llm_model: str, question: str, chunks: list) -> list:
    """对每个 chunk 调用 LLM 判断是否与 question 相关，返回 bool 列表。"""
    labels = []
    for chunk in chunks:
        try:
            resp = state.llm_client.chat.completions.create(
                model=llm_model,
                messages=[{"role": "user", "content": RELEVANCE_JUDGE_PROMPT.format(
                    question=question, chunk=chunk["text"][:500]
                )}],
                temperature=0.0,
            )
            ans = resp.choices[0].message.content.strip().upper()
            labels.append("YES" in ans)
        except Exception:
            labels.append(False)
    return labels


def _recall_at_k(retrieved: list, relevant_set: set, k: int) -> float:
    """Recall@K = |retrieved[:K] ∩ relevant| / max(|relevant|, 1)"""
    if not relevant_set:
        return 0.0
    hits = sum(1 for c in retrieved[:k] if c["text"] in relevant_set)
    return hits / len(relevant_set)


def _mrr(retrieved: list, relevant_set: set) -> float:
    """MRR = 1/rank_of_first_relevant；若无相关文档则返回 0。"""
    for i, c in enumerate(retrieved, 1):
        if c["text"] in relevant_set:
            return 1.0 / i
    return 0.0


def _ndcg_at_k(retrieved: list, relevant_set: set, k: int) -> float:
    """NDCG@K（binary relevance）= DCG@K / IDCG@K"""
    dcg = sum(
        (1.0 if c["text"] in relevant_set else 0.0) / math.log2(i + 2)
        for i, c in enumerate(retrieved[:k])
    )
    ideal_hits = min(len(relevant_set), k)
    idcg = sum(1.0 / math.log2(i + 2) for i in range(ideal_hits))
    return dcg / idcg if idcg > 0 else 0.0


@router.post("/ranked", summary="有监督检索指标 Recall@K/MRR/NDCG@K（SSE）")
def eval_ranked(request: Request, state: AppState = Depends(get_state)):
    llm_model = request.app.state.llm_model
    return log_gen_to_sse(_run_ranked(state, llm_model))


def _run_ranked(state: AppState, llm_model: str):
    lines = []

    def emit(msg=""):
        lines.append(msg)
        return "\n".join(lines)

    total = state.collection.count()
    yield emit("=" * 60)
    yield emit("  有监督检索指标：Recall@K / MRR / NDCG@K")
    yield emit("  （LLM-as-Annotator 自动构建 Ground Truth）")
    yield emit("=" * 60)
    yield emit(f"知识库文档块总数：{total}")
    if total == 0:
        yield emit("⚠️ 知识库为空，请先完成入库后再评估。")
        return

    yield emit("\n📋 Ground Truth 构建中（每题检索 Top-10，LLM 逐块标注相关性）…")
    yield emit("  预计耗时：约 1-3 分钟")

    all_r1, all_r3, all_r5, all_mrr, all_ndcg = [], [], [], [], []

    for i, question in enumerate(EVAL_QUESTIONS, 1):
        yield emit(f"\n[{i:02d}/{len(EVAL_QUESTIONS)}] {question}")

        # 取 top-10 用于标注
        n_label = min(RANKED_RETRIEVE_K, total)
        q_emb = state.embedding_func([question])[0]
        label_results = state.collection.query(
            query_embeddings=[q_emb],
            n_results=n_label,
            include=["documents", "metadatas", "distances"],
        )
        label_chunks = [
            {"text": doc, "source": meta.get("source", "未知"), "distance": dist}
            for doc, meta, dist in zip(
                label_results["documents"][0],
                label_results["metadatas"][0],
                label_results["distances"][0],
            )
        ]

        yield emit(f"  标注 {len(label_chunks)} 个候选块…")
        labels = _annotate_relevance(state, llm_model, question, label_chunks)
        relevant_set = {c["text"] for c, rel in zip(label_chunks, labels) if rel}
        n_rel = len(relevant_set)
        yield emit(f"  标注完成：{n_rel}/{len(label_chunks)} 块相关")

        if n_rel == 0:
            yield emit("  ⚠️  无相关块，该题跳过（可能问题与语料不匹配）")
            continue

        # 取 top-5 作为"被评估的检索结果"
        n_eval = min(RANKED_EVAL_K, total)
        eval_results = state.collection.query(
            query_embeddings=[q_emb],
            n_results=n_eval,
            include=["documents", "metadatas", "distances"],
        )
        eval_chunks = [
            {"text": doc, "source": meta.get("source", "未知"), "distance": dist}
            for doc, meta, dist in zip(
                eval_results["documents"][0],
                eval_results["metadatas"][0],
                eval_results["distances"][0],
            )
        ]

        r1 = _recall_at_k(eval_chunks, relevant_set, 1)
        r3 = _recall_at_k(eval_chunks, relevant_set, 3)
        r5 = _recall_at_k(eval_chunks, relevant_set, 5)
        mrr = _mrr(eval_chunks, relevant_set)
        ndcg = _ndcg_at_k(eval_chunks, relevant_set, 5)

        all_r1.append(r1); all_r3.append(r3); all_r5.append(r5)
        all_mrr.append(mrr); all_ndcg.append(ndcg)

        yield emit(f"  Recall@1={r1:.3f}  Recall@3={r3:.3f}  Recall@5={r5:.3f}")
        yield emit(f"  MRR={mrr:.3f}  NDCG@5={ndcg:.3f}")

    yield emit(f"\n{'=' * 60}")
    yield emit("全局指标汇总")
    yield emit("-" * 40)
    metrics = [
        ("Recall@1", all_r1,  "前1个结果中召回相关文档的比例"),
        ("Recall@3", all_r3,  "前3个结果中召回相关文档的比例"),
        ("Recall@5", all_r5,  "前5个结果中召回相关文档的比例"),
        ("MRR     ", all_mrr, "第一个相关结果排名的倒数均值"),
        ("NDCG@5  ", all_ndcg, "综合排名与相关性的折损累计增益"),
    ]
    for name, vals, desc in metrics:
        if vals:
            avg = statistics.mean(vals)
            bar = "█" * int(avg * 10) + "░" * (10 - int(avg * 10))
            yield emit(f"  {name}  {avg:.3f}  [{bar}]  {desc}")
        else:
            yield emit(f"  {name}  无有效数据")

    all_vals = all_r5 + all_mrr + all_ndcg
    if all_vals:
        overall = statistics.mean(all_vals)
        yield emit(f"\n  综合检索分:  {overall:.3f} / 1.0")
        if overall >= 0.7:
            yield emit("  ✅ 检索质量优秀。")
        elif overall >= 0.5:
            yield emit("  🟡 检索质量良好，有提升空间。")
        elif overall >= 0.3:
            yield emit("  🟠 检索质量中等，建议调整 chunk_size / TOP_K。")
        else:
            yield emit("  🔴 检索质量较差，请检查知识库内容和 Embedding 适配性。")
    yield emit("=" * 60)


# ==========================================
# 检索阶段评估：CP@K / Recall@K / MRR / NDCG@K
# ==========================================

def _context_precision_at_k(labels: list, k: int) -> float:
    """Context Precision@K = 前K个结果中相关块数 / K（信噪比）"""
    return sum(1 for v in labels[:k] if v) / k if k > 0 else 0.0


@router.post("/retrieval", summary="检索阶段评估（SSE）")
def eval_retrieval(request: Request, state: AppState = Depends(get_state)):
    llm_model = request.app.state.llm_model
    return log_gen_to_sse(_run_retrieval(state, llm_model))


def _run_retrieval(state: AppState, llm_model: str):
    lines = []

    def emit(msg=""):
        lines.append(msg)
        return "\n".join(lines)

    total = state.collection.count()
    yield emit("=" * 60)
    yield emit("  检索阶段评估")
    yield emit("  上下文精确率 / Recall@K / MRR / NDCG@K")
    yield emit("=" * 60)
    yield emit(f"知识库文档块总数：{total}")
    if total == 0:
        yield emit("⚠️ 知识库为空，请先完成入库后再评估。")
        return

    yield emit("\n📋 Ground Truth 构建中（每题 Top-10，LLM 逐块标注相关性）…")
    yield emit("  预计耗时：约 1-3 分钟")

    all_cp, all_r1, all_r3, all_r5, all_mrr, all_ndcg = [], [], [], [], [], []

    for i, question in enumerate(EVAL_QUESTIONS, 1):
        yield emit(f"\n[{i:02d}/{len(EVAL_QUESTIONS)}] {question}")

        n_label = min(RANKED_RETRIEVE_K, total)
        q_emb = state.embedding_func([question])[0]
        label_results = state.collection.query(
            query_embeddings=[q_emb],
            n_results=n_label,
            include=["documents", "metadatas", "distances"],
        )
        label_chunks = [
            {"text": doc, "source": meta.get("source", "未知"), "distance": dist}
            for doc, meta, dist in zip(
                label_results["documents"][0],
                label_results["metadatas"][0],
                label_results["distances"][0],
            )
        ]

        yield emit(f"  标注 {len(label_chunks)} 个候选块…")
        labels = _annotate_relevance(state, llm_model, question, label_chunks)
        relevant_set = {c["text"] for c, rel in zip(label_chunks, labels) if rel}
        n_rel = len(relevant_set)
        yield emit(f"  标注完成：{n_rel}/{len(label_chunks)} 块相关")

        if n_rel == 0:
            yield emit("  ⚠️  无相关块，该题跳过")
            continue

        # 取 top-5 作为被评估的检索结果
        n_eval = min(RANKED_EVAL_K, total)
        eval_results = state.collection.query(
            query_embeddings=[q_emb],
            n_results=n_eval,
            include=["documents", "metadatas", "distances"],
        )
        eval_chunks = [
            {"text": doc, "source": meta.get("source", "未知"), "distance": dist}
            for doc, meta, dist in zip(
                eval_results["documents"][0],
                eval_results["metadatas"][0],
                eval_results["distances"][0],
            )
        ]
        # top-5 各块是否相关（直接用已标注的 label_chunks 前5个的标签）
        eval_labels = labels[:n_eval]

        cp  = _context_precision_at_k(eval_labels, n_eval)
        r1  = _recall_at_k(eval_chunks, relevant_set, 1)
        r3  = _recall_at_k(eval_chunks, relevant_set, 3)
        r5  = _recall_at_k(eval_chunks, relevant_set, 5)
        mrr = _mrr(eval_chunks, relevant_set)
        ndcg = _ndcg_at_k(eval_chunks, relevant_set, 5)

        all_cp.append(cp); all_r1.append(r1); all_r3.append(r3)
        all_r5.append(r5); all_mrr.append(mrr); all_ndcg.append(ndcg)

        yield emit(f"  精确率@5={cp:.3f}  Recall@1={r1:.3f}  Recall@3={r3:.3f}  Recall@5={r5:.3f}")
        yield emit(f"  MRR={mrr:.3f}  NDCG@5={ndcg:.3f}")

    yield emit(f"\n{'=' * 60}")
    yield emit("检索阶段全局汇总")
    yield emit("-" * 40)
    metrics = [
        ("上下文精确率@5", all_cp,   "检索结果信噪比（相关块占比）"),
        ("Recall@1   ", all_r1,   "Top-1 中召回相关文档的比例"),
        ("Recall@3   ", all_r3,   "Top-3 中召回相关文档的比例"),
        ("Recall@5   ", all_r5,   "Top-5 中召回相关文档的比例"),
        ("MRR        ", all_mrr,  "第一个相关文档排名的倒数均值"),
        ("NDCG@5     ", all_ndcg, "综合排名与相关性的归一化折损增益"),
    ]
    for name, vals, desc in metrics:
        if vals:
            avg = statistics.mean(vals)
            bar = "█" * int(avg * 10) + "░" * (10 - int(avg * 10))
            yield emit(f"  {name}  {avg:.3f}  [{bar}]  {desc}")
        else:
            yield emit(f"  {name}  无有效数据")

    core = all_r5 + all_mrr + all_ndcg
    if core:
        overall = statistics.mean(core)
        yield emit(f"\n  综合检索分:  {overall:.3f} / 1.0")
        verdict = (
            "✅ 检索质量优秀。" if overall >= 0.7 else
            "🟡 检索质量良好，有提升空间。" if overall >= 0.5 else
            "🟠 检索质量中等，建议调整 chunk_size / TOP_K。" if overall >= 0.3 else
            "🔴 检索质量较差，请检查知识库内容和 Embedding 适配性。"
        )
        yield emit(f"  {verdict}")
    yield emit("=" * 60)


# ==========================================
# 生成阶段评估：忠实度 / 相关性 / 可回答性
# ==========================================

ANSWERABILITY_PROMPT = """根据以下检索内容，评估模型能否充分回答该问题。
只输出一个 0-5 的整数分数，不要有任何其他内容。
5=完全可以回答，4=基本可以，3=部分可以，2=勉强，1=几乎不能，0=完全不能。

【问题】
{question}

【检索内容】
{context}"""


@router.post("/generation", summary="生成阶段评估（SSE）")
def eval_generation(request: Request, state: AppState = Depends(get_state)):
    llm_model = request.app.state.llm_model
    return log_gen_to_sse(_run_generation(state, llm_model))


def _run_generation(state: AppState, llm_model: str):
    lines = []

    def emit(msg=""):
        lines.append(msg)
        return "\n".join(lines)

    total = state.collection.count()
    yield emit("=" * 60)
    yield emit("  生成阶段评估")
    yield emit("  忠实度 / 相关性 / 可回答性")
    yield emit("=" * 60)
    yield emit(f"知识库文档块总数：{total}")
    if total == 0:
        yield emit("⚠️ 知识库为空，请先完成入库后再评估。")
        return

    all_faith, all_ar, all_ans = [], [], []

    for i, question in enumerate(EVAL_QUESTIONS, 1):
        yield emit(f"\n[{i:02d}/{len(EVAL_QUESTIONS)}] {question}")

        chunks = _retrieve_eval(state, question)
        if not chunks:
            yield emit("  无召回结果，跳过")
            continue

        # —— 生成答案 ——
        yield emit("  生成答案中…")
        context_parts = [f"[{j+1}] 来源: {c['source']}\n{c['text']}" for j, c in enumerate(chunks)]
        user_content = "参考资料：\n" + "\n\n".join(context_parts) + f"\n\n用户问题：{question}"
        try:
            resp = state.llm_client.chat.completions.create(
                model=llm_model,
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

        context_numbered = "\n\n".join(f"[{j+1}] {c['text']}" for j, c in enumerate(chunks))

        # —— 忠实度（Faithfulness）——
        yield emit("  [忠实度] 拆解声明 + 逐条核验…")
        try:
            decompose_resp = state.llm_client.chat.completions.create(
                model=llm_model,
                messages=[{"role": "user", "content": RAGAS_FAITHFULNESS_DECOMPOSE.format(answer=answer)}],
                temperature=0.01,
            )
            claims = [l.strip() for l in decompose_resp.choices[0].message.content.strip().split("\n") if l.strip()]
            n_yes = 0
            for claim in claims:
                vr = state.llm_client.chat.completions.create(
                    model=llm_model,
                    messages=[{"role": "user", "content": RAGAS_FAITHFULNESS_VERIFY.format(
                        context=context_numbered, claim=claim)}],
                    temperature=0.01,
                )
                if "YES" in vr.choices[0].message.content.strip().upper():
                    n_yes += 1
            faith = n_yes / len(claims) if claims else 0.0
            lines[-1] = f"  [忠实度] {faith:.3f}  ({n_yes}/{len(claims)} 声明有上下文支撑)"
            yield "\n".join(lines)
            all_faith.append(faith)
        except Exception as ex:
            lines[-1] = f"  [忠实度] 失败: {ex}"
            yield "\n".join(lines)

        # —— 相关性（Answer Relevance）——
        yield emit("  [相关性] 反向生成问题 + 余弦相似度…")
        try:
            ar_resp = state.llm_client.chat.completions.create(
                model=llm_model,
                messages=[{"role": "user", "content": RAGAS_ANSWER_RELEVANCE_PROMPT.format(answer=answer)}],
                temperature=0.3,
            )
            gen_qs = [l.strip() for l in ar_resp.choices[0].message.content.strip().split("\n") if l.strip()][:3]
            q_emb = state.embedding_func.model.encode([question], normalize_embeddings=True)[0].tolist()
            sims = []
            for gq in gen_qs:
                gq_emb = state.embedding_func.model.encode([gq], normalize_embeddings=True)[0].tolist()
                sims.append(max(0.0, sum(a * b for a, b in zip(q_emb, gq_emb))))
            ar = statistics.mean(sims) if sims else 0.0
            lines[-1] = f"  [相关性] {ar:.3f}"
            yield "\n".join(lines)
            all_ar.append(ar)
        except Exception as ex:
            lines[-1] = f"  [相关性] 失败: {ex}"
            yield "\n".join(lines)

        # —— 可回答性（Answerability）——
        yield emit("  [可回答性] LLM 打分…")
        try:
            context_plain = "\n\n".join(c["text"] for c in chunks)
            ans_resp = state.llm_client.chat.completions.create(
                model=llm_model,
                messages=[{"role": "user", "content": ANSWERABILITY_PROMPT.format(
                    question=question, context=context_plain)}],
                temperature=0.01,
            )
            raw = ans_resp.choices[0].message.content.strip()
            score = int("".join(c for c in raw if c.isdigit())[:1]) if any(c.isdigit() for c in raw) else 0
            score = max(0, min(5, score))
            lines[-1] = f"  [可回答性] {score}/5"
            yield "\n".join(lines)
            all_ans.append(score)
        except Exception as ex:
            lines[-1] = f"  [可回答性] 失败: {ex}"
            yield "\n".join(lines)

    yield emit(f"\n{'=' * 60}")
    yield emit("生成阶段全局汇总")
    yield emit("-" * 40)
    for vals, label, desc in [
        (all_faith, "忠实度  ", "答案声明由上下文支撑的比例（0-1）"),
        (all_ar,    "相关性  ", "答案针对问题的语义相似度（0-1）"),
        (all_ans,   "可回答性", "上下文充分性 LLM 打分（0-5）"),
    ]:
        if vals:
            avg = statistics.mean(vals)
            # 可回答性归一化到 0-1 显示进度条
            bar_val = avg / 5 if label.strip() == "可回答性" else avg
            bar = "█" * int(bar_val * 10) + "░" * (10 - int(bar_val * 10))
            unit = "/5" if label.strip() == "可回答性" else ""
            yield emit(f"  {label}  {avg:.2f}{unit}  [{bar}]  {desc}")
        else:
            yield emit(f"  {label}  无有效数据")

    norm_vals = [v / 5 for v in all_ans] + all_faith + all_ar
    if norm_vals:
        overall = statistics.mean(norm_vals)
        yield emit(f"\n  综合生成分:  {overall:.3f} / 1.0")
        verdict = (
            "✅ 生成质量优秀。" if overall >= 0.7 else
            "🟡 生成质量良好，有提升空间。" if overall >= 0.5 else
            "🟠 生成质量中等，建议优化 prompt 或 TOP_K。" if overall >= 0.3 else
            "🔴 生成质量较差，请检查 LLM 和知识库配置。"
        )
        yield emit(f"  {verdict}")
    yield emit("=" * 60)
