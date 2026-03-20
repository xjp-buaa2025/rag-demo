"""
backend/routers/chat.py — RAG 问答接口（图文双路版）

POST /chat
  请求体：{"message": "用户问题", "history": [...OpenAI messages 格式...]}
  响应：SSE 流
    中间帧：data: {"delta": "<新增文本>"}\n\n
    最后帧：data: {"done": true, "sources_md": "...", "image_urls": [...]}\n\n

检索策略：
  1. 多查询：LLM 生成额外查询（静默），多查询分别检索
  2. 双路检索：bge-m3(text_vec) + Chinese-CLIP(image_vec) 两路，合并去重（Qdrant）
  3. CrossEncoder 重排，取 TOP_K 送 LLM
  4. 检索到图片块时，image_url 列表随 done 帧返回前端展示
"""

import json
from typing import List, Optional
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from backend.deps import get_state, get_llm_model
from backend.state import AppState, COLLECTION_NAME
from backend.sse import chat_gen_to_sse, _IMAGES_SEP

router = APIRouter()

TOP_K = 4             # 最终送给 LLM 的文档块数
RECALL_K = 8          # 每个查询的初始召回候选数
MULTI_QUERY_COUNT = 2 # 额外生成的查询数

SYSTEM_PROMPT = """你是一个专业的知识库问答助手。请严格根据提供的参考资料回答用户问题。
如果参考资料中没有相关信息，请如实说明"知识库中没有找到相关内容"，不要凭空捏造。
回答要详细、准确、有条理，尽量引用原文中的具体数据和技术细节，不要省略重要信息。"""


class MessageItem(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: List[MessageItem] = []


def _generate_extra_queries(state: AppState, llm_model: str,
                             original_question: str, count: int) -> List[str]:
    """
    调用 LLM 从不同角度生成额外检索查询。失败时返回 []，降级为单查询。
    SSE 约束：此函数绝不 yield，在 LLM 流式输出前静默完成。
    """
    prompt = (
        f"请为以下问题从{count}个不同角度生成{count}个补充检索查询。\n"
        "要求：\n1. 每个查询独占一行，无需编号或其他符号\n"
        "2. 与原问题表达不同，侧重不同方面或使用不同关键词\n"
        "3. 保持简洁，不超过50字\n\n"
        f"原问题：{original_question}\n\n仅输出{count}个查询，每行一个："
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


def _multi_query_retrieve(state: AppState, queries: List[str],
                           recall_k: int) -> List[dict]:
    """
    对多个查询分别执行双路向量检索（text_vec + image_vec），按 ID 去重合并。
    相同 ID 保留 distance 最高（最相关）的结果。
    返回按 distance 降序排列的候选块列表（Qdrant 余弦相似度越高越相关）。
    SSE 约束：此函数绝不 yield。
    """
    from backend.routers.retrieve import qdrant_search_text, qdrant_search_image

    total = state.get_doc_count()
    if total == 0:
        return []

    n = min(recall_k, total)
    seen: dict = {}

    for query in queries:
        # 路径1：bge-m3 文本检索
        for chunk in qdrant_search_text(state.qdrant_client, state.embedding_mgr, query, n):
            cid = chunk["id"]
            if cid not in seen or chunk["distance"] > seen[cid]["distance"]:
                seen[cid] = chunk

        # 路径2：Chinese-CLIP 图片检索
        for chunk in qdrant_search_image(state.qdrant_client, state.embedding_mgr,
                                          query, min(recall_k // 2, total)):
            cid = chunk["id"]
            if cid not in seen or chunk["distance"] > seen[cid]["distance"]:
                seen[cid] = chunk

    return sorted(seen.values(), key=lambda c: c["distance"], reverse=True)


def _rerank(state: AppState, question: str, candidates: List[dict],
            top_k: int) -> List[dict]:
    """
    CrossEncoder 对候选块重打分，返回分数最高的 top_k 个块。
    reranker 未加载时降级为按 distance 取 top_k。
    SSE 约束：此函数绝不 yield。
    """
    if state.reranker is None or not candidates:
        return candidates[:top_k]
    try:
        pairs = [(question, c["text"]) for c in candidates]
        scores = state.reranker.predict(pairs)
        ranked = sorted(zip(scores, candidates), key=lambda x: x[0], reverse=True)
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
    """RAG 问答生成器：多查询 + 双路检索 + 重排序 + 图片 URL 透传。"""
    if state.get_doc_count() == 0:
        yield "⚠️ 知识库为空，请先点击入库按钮导入文档。"
        return

    # ===== 阶段一：多查询生成（静默）=====
    extra_queries = _generate_extra_queries(state, llm_model, message, MULTI_QUERY_COUNT)
    all_queries = [message] + extra_queries

    # ===== 阶段二：双路多查询检索 + 去重（静默）=====
    try:
        candidates = _multi_query_retrieve(state, all_queries, RECALL_K)
    except Exception as e:
        yield f"❌ 向量检索失败，请尝试重新入库。（{e}）"
        return
    if not candidates:
        yield "⚠️ 知识库为空，请先点击入库按钮导入文档。"
        return

    # ===== 阶段三：重排序（静默）=====
    chunks = _rerank(state, message, candidates, TOP_K)

    # ===== 阶段四：构建 messages 并流式调用 LLM =====
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for item in history[-12:]:
        if item.role in ("user", "assistant"):
            messages.append({"role": item.role, "content": item.content or ""})

    # 构建上下文：文本块直接引用，图片块引用 Caption
    context_parts = []
    for i, c in enumerate(chunks):
        label = f"[{i+1}] 来源：{c['source']}"
        if c.get("page"):
            label += f" 第{c['page']}页"
        if c.get("chunk_type") == "image":
            label += "（图片描述）"
        context_parts.append(f"{label}\n{c['text']}")
    context = "\n\n".join(context_parts)

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

    # ===== 阶段五：追加参考来源 + 图片 URL =====
    sources_text = ""
    if chunks:
        source_lines = ["\n\n---\n**📚 参考来源**\n"]
        for i, c in enumerate(chunks, 1):
            page_info = f" · 第 {c['page']} 页" if c.get("page") else ""
            type_tag = " 🖼️" if c.get("chunk_type") == "image" else ""
            snippet = c["text"][:80].replace("\n", " ")
            source_lines.append(f"**[{i}] {c['source']}{page_info}{type_tag}**  \n_{snippet}…_\n")
        sources_text = "\n".join(source_lines)

    # 收集检索到的图片 URL
    image_urls = [
        c["image_url"] for c in chunks
        if c.get("chunk_type") == "image" and c.get("image_url")
    ]

    # 最后一次 yield：回答 + 来源 + 图片 URL 标记（sse.py 会解析）
    final = full_answer + sources_text
    if image_urls:
        final += _IMAGES_SEP + json.dumps(image_urls, ensure_ascii=False)
    yield final
