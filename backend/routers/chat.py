"""
backend/routers/chat.py — RAG 问答接口

POST /chat
  请求体：{"message": "用户问题", "history": [...OpenAI messages 格式...]}
  响应：SSE 流
    中间帧：data: {"delta": "<新增文本>"}\n\n
    最后帧：data: {"done": true, "sources_md": "<参考来源 Markdown>"}\n\n

检索优化（v2）：
  1. 多查询检索：LLM 生成 MULTI_QUERY_COUNT 个额外查询，分别检索后去重合并
  2. 重排序：CrossEncoder 对合并候选块精打分，取 TOP_K 最优块送 LLM
  降级策略：生成查询失败 → 单查询；reranker 未加载 → 按距离排序
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from backend.deps import get_state, get_llm_model
from backend.state import AppState
from backend.sse import chat_gen_to_sse

router = APIRouter()

# ==========================================
# 配置参数（集中管理）
# ==========================================
TOP_K = 4             # 最终送给 LLM 的文档块数
RECALL_K = 8          # 每个查询的初始召回候选数
MULTI_QUERY_COUNT = 2 # 额外生成的查询数（共 1+MULTI_QUERY_COUNT 个查询）

SYSTEM_PROMPT = """你是一个专业的知识库问答助手。请严格根据提供的参考资料回答用户问题。
如果参考资料中没有相关信息，请如实说明"知识库中没有找到相关内容"，不要凭空捏造。
回答要详细、准确、有条理，尽量引用原文中的具体数据和技术细节，不要省略重要信息。"""


class MessageItem(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: List[MessageItem] = []


def _generate_extra_queries(
    state: AppState,
    llm_model: str,
    original_question: str,
    count: int,
) -> List[str]:
    """
    调用 LLM 从不同角度为原始问题生成 count 个额外检索查询。
    返回额外查询列表（不含原始问题）。失败时返回 []，调用方降级为单查询。

    SSE 约束：此函数为同步调用，绝不 yield，在 LLM 流式输出前静默完成。
    """
    prompt = (
        f"请为以下问题从{count}个不同角度生成{count}个补充检索查询。\n"
        "要求：\n"
        "1. 每个查询独占一行，无需编号或其他符号\n"
        "2. 与原问题表达不同，侧重不同方面或使用不同关键词\n"
        "3. 保持简洁，不超过50字\n\n"
        f"原问题：{original_question}\n\n"
        f"仅输出{count}个查询，每行一个："
    )
    try:
        resp = state.llm_client.chat.completions.create(
            model=llm_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            stream=False,
        )
        raw = resp.choices[0].message.content.strip()
        lines = [line.strip() for line in raw.split("\n") if line.strip()]
        extra = lines[:count]
        print(f"[chat] 多查询生成成功：{extra}")
        return extra
    except Exception as e:
        print(f"[chat] 多查询生成失败（{e}），降级为单查询")
        return []


def _multi_query_retrieve(
    state: AppState,
    queries: List[str],
    recall_k: int,
) -> List[dict]:
    """
    对多个查询分别执行向量检索，按 chunk ID 去重合并。
    相同 ID 保留 distance 最小（最相关）的结果。
    返回按 distance 升序排列的候选块列表。

    SSE 约束：此函数绝不 yield，在 LLM 流式输出前静默完成。
    """
    total = state.collection.count()
    if total == 0:
        return []

    n = min(recall_k, total)
    seen: dict = {}  # id → chunk dict

    for query in queries:
        q_emb = state.embedding_func([query])[0]
        results = state.collection.query(
            query_embeddings=[q_emb],
            n_results=n,
            include=["ids", "documents", "metadatas", "distances"],
        )
        ids       = results["ids"][0]
        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        for chunk_id, doc, meta, dist in zip(ids, documents, metadatas, distances):
            if chunk_id not in seen or dist < seen[chunk_id]["distance"]:
                seen[chunk_id] = {
                    "id": chunk_id,
                    "text": doc,
                    "source": meta.get("source", "未知"),
                    "page": meta.get("page", 0),
                    "distance": dist,
                }

    # 按距离升序排列（reranker 不可用时的兜底顺序）
    return sorted(seen.values(), key=lambda c: c["distance"])


def _rerank(
    state: AppState,
    question: str,
    candidates: List[dict],
    top_k: int,
) -> List[dict]:
    """
    用 CrossEncoder 对候选块重打分，返回分数最高的 top_k 个块。
    若 reranker 未加载（state.reranker is None），降级为按距离取 top_k。

    CrossEncoder 分数越高越相关（与 distance 方向相反）。
    SSE 约束：此函数绝不 yield，在 LLM 流式输出前静默完成。
    """
    if state.reranker is None or not candidates:
        return candidates[:top_k]

    try:
        pairs = [(question, c["text"]) for c in candidates]
        scores = state.reranker.predict(pairs)
        ranked = sorted(
            zip(scores, candidates),
            key=lambda x: x[0],
            reverse=True,  # 分数高 → 更相关 → 排前面
        )
        return [c for _, c in ranked[:top_k]]
    except Exception as e:
        print(f"[chat] Reranker 打分失败（{e}），降级为距离排序")
        return candidates[:top_k]


@router.post("/chat", summary="RAG 流式问答（SSE）")
def chat(body: ChatRequest, request: Request, state: AppState = Depends(get_state)):
    llm_model = request.app.state.llm_model
    gen = _chat_gen(state, llm_model, body.message, body.history)
    return chat_gen_to_sse(gen)


def _chat_gen(state: AppState, llm_model: str, message: str, history: List[MessageItem]):
    """RAG 问答生成器，支持多查询检索 + 重排序（v2）。"""
    if state.collection.count() == 0:
        yield "⚠️ 知识库为空，请先点击入库按钮导入文档。"
        return

    # ===== 阶段一：多查询生成（静默，不 yield）=====
    extra_queries = _generate_extra_queries(state, llm_model, message, MULTI_QUERY_COUNT)
    all_queries = [message] + extra_queries

    # ===== 阶段二：多查询检索 + 去重（静默，不 yield）=====
    candidates = _multi_query_retrieve(state, all_queries, RECALL_K)
    if not candidates:
        yield "⚠️ 知识库为空，请先点击入库按钮导入文档。"
        return

    # ===== 阶段三：重排序（静默，不 yield）=====
    chunks = _rerank(state, message, candidates, TOP_K)

    # ===== 阶段四：构建 messages 并流式调用 LLM =====
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for item in history[-12:]:
        if item.role in ("user", "assistant"):
            messages.append({"role": item.role, "content": item.content or ""})

    context = "\n\n".join(
        f"[{i+1}] 来源：{c['source']}" + (f" 第{c['page']}页" if c.get("page") else "") + f"\n{c['text']}"
        for i, c in enumerate(chunks)
    )
    user_content = f"参考资料：\n{context}\n\n用户问题：{message}" if chunks else message
    messages.append({"role": "user", "content": user_content})

    # 流式调用 LLM
    full_answer = ""
    try:
        stream = state.llm_client.chat.completions.create(
            model=llm_model,
            messages=messages,
            temperature=0.3,
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            full_answer += delta
            yield full_answer
    except Exception as e:
        yield f"❌ LLM 调用失败：{e}"
        return

    # 追加参考来源（使用 sse.py 约定的分隔符）
    if chunks:
        sources = ["\n\n---\n**📚 参考来源**\n"]
        for i, c in enumerate(chunks, 1):
            page_info = f" · 第 {c['page']} 页" if c.get("page") else ""
            snippet = c["text"][:80].replace("\n", " ")
            sources.append(f"**[{i}] {c['source']}{page_info}**  \n_{snippet}…_\n")
        yield full_answer + "\n".join(sources)
