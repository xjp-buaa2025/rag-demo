"""
backend/routers/chat.py — RAG 问答接口（图文双路版）

POST /chat
  请求体：{"message": "用户问题", "history": [...OpenAI messages 格式...]}
  响应：SSE 流
    中间帧：data: {"delta": "<新增文本>"}\n\n
    最后帧：data: {"done": true, "sources": [...Citation...], "image_urls": [...]}\n\n

检索策略：
  1. 多查询：LLM 生成额外查询（静默），多查询分别检索
  2. 双路检索：bge-m3(text_vec) + Chinese-CLIP(image_vec) 两路，合并去重（Qdrant）
  3. CrossEncoder 重排，取 TOP_K 送 LLM
  4. 检索到图片块时，image_url 列表随 done 帧返回前端展示
"""

import json
import re
from typing import List, Optional
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from backend.deps import get_state, get_llm_model
from backend.state import AppState, COLLECTION_NAME
from backend.sse import chat_gen_to_sse, _SOURCES_JSON_SEP

router = APIRouter()

TOP_K = 4             # 最终送给 LLM 的文档块数
RECALL_K = 8          # 每个查询的初始召回候选数
MULTI_QUERY_COUNT = 2 # 额外生成的查询数

SYSTEM_PROMPT = """你是一个专业的知识库问答助手。请严格根据提供的参考资料回答用户问题。
如果参考资料中没有相关信息，请如实说明"知识库中没有找到相关内容"，不要凭空捏造。
回答要详细、准确、有条理，尽量引用原文中的具体数据和技术细节，不要省略重要信息。

**重要：引用标注要求**
参考资料已按编号 [1][2][3]... 标注。在回答中，每引用某条资料的具体内容时，请在该句末尾紧跟对应编号，格式为 [编号]，例如："涡扇发动机的风扇压比通常在1.3到1.8之间 [1]。"若同时引用多条，则写 [1][3]。请务必引用，不要遗漏。

如果参考资料中包含图片（标记为"图片描述"的条目会附带图片URL），请在回答中使用 Markdown 图片语法 ![描述](URL) 展示相关图片。只使用参考资料中提供的图片URL，不要编造URL。
当参考资料中包含以 [FLOWCHART NODE] 或 [FLOWCHART PATH] 开头的条目时，这些内容来自技术手册的故障排查流程图。请严格按照 YES/NO 分支逻辑组织回答，明确说明每个判断点的条件和对应操作，不要合并或省略关键的判断步骤，以正确的顺序引导用户完成故障排查程序。"""


class MessageItem(BaseModel):
    role: str
    content: str


class ImageChunkInput(BaseModel):
    text: str
    source: str = "上传图片"
    page: int = 0
    distance: float = 1.0
    image_url: Optional[str] = None


class ChatRequest(BaseModel):
    message: str
    history: List[MessageItem] = []
    image_chunks: Optional[List[ImageChunkInput]] = None


def _generate_extra_queries(state: AppState, llm_model: str,
                             original_question: str, count: int) -> List[str]:
    """
    调用 LLM 从不同角度生成额外检索查询。失败时返回 []，降级为单查询。
    SSE 约束：此函数绝不 yield，在 LLM 流式输出前静默完成。
    """
    prompt = (
        f"Please generate {count} supplementary search queries for the following question "
        f"from {count} different angles.\n"
        "Requirements:\n"
        "1. One query per line, no numbering or symbols\n"
        "2. Use different expressions, focus on different aspects or keywords\n"
        "3. Keep concise (under 50 words per query)\n"
        "4. IMPORTANT: Use the SAME language as the original question\n\n"
        f"Original question: {original_question}\n\n"
        f"Output {count} queries, one per line:"
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
    from backend.routers.retrieve import hybrid_search_text, qdrant_search_image

    total = state.get_doc_count()
    if total == 0:
        return []

    n = min(recall_k, total)
    seen: dict = {}

    for query in queries:
        # 路径1：bge-m3 Dense + BM25 混合文本检索（RRF 融合）
        for chunk in hybrid_search_text(state.qdrant_client, state.embedding_mgr,
                                        state.bm25_manager, query, n):
            cid = chunk["id"]
            if cid not in seen or chunk["distance"] > seen[cid]["distance"]:
                seen[cid] = chunk

        # 路径2：Chinese-CLIP 图片检索（兜底防护，维度修复后不应报错）
        try:
            for chunk in qdrant_search_image(state.qdrant_client, state.embedding_mgr,
                                              query, min(recall_k // 2, total)):
                cid = chunk["id"]
                if cid not in seen or chunk["distance"] > seen[cid]["distance"]:
                    seen[cid] = chunk
        except Exception as e:
            import traceback
            print(f"[chat] ⚠️ CLIP 图片检索失败（{e}），跳过图片路径")
            traceback.print_exc()

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


_FAULT_KEYWORDS = frozenset([
    "fault", "fail", "error", "problem", "issue", "troubleshoot",
    "故障", "失效", "报错", "异常", "不工作", "无法", "排查", "诊断",
])


def _boost_flowchart_chunks(candidates: List[dict], query: str) -> List[dict]:
    """
    对故障诊断类查询，将 flowchart_path chunk 提前排序，
    使其更可能进入 rerank 的 top_K 候选。
    不修改 distance，只调整列表顺序。
    """
    q_lower = query.lower()
    if not any(kw in q_lower for kw in _FAULT_KEYWORDS):
        return candidates
    paths = [c for c in candidates if c.get("chunk_type") == "flowchart_path"]
    others = [c for c in candidates if c.get("chunk_type") != "flowchart_path"]
    return paths + others


@router.post("/chat", summary="RAG 流式问答（SSE）")
def chat(body: ChatRequest, request: Request, state: AppState = Depends(get_state)):
    llm_model = request.app.state.llm_model
    img_chunks = None
    if body.image_chunks:
        img_chunks = [
            {"id": f"clip_upload_{i}", "chunk_type": "image",
             "text": c.text, "source": c.source, "page": c.page,
             "distance": c.distance, "image_url": c.image_url}
            for i, c in enumerate(body.image_chunks)
        ]
    gen = _chat_gen(state, llm_model, body.message, body.history, img_chunks)
    return chat_gen_to_sse(gen)


def _format_context(chunks, broken_img_re=None):
    """
    将检索结果格式化为带来源标签的上下文字符串。
    供 LangChain Chain 和原生路径共用。

    Args:
        chunks: 检索结果列表（dict 或 LangChain Document）
    Returns:
        格式化后的上下文字符串
    """
    if broken_img_re is None:
        broken_img_re = re.compile(r'!?\[[^\]]*\]\(images/[^)]+\)\s*')

    context_parts = []
    for i, c in enumerate(chunks):
        # 兼容 dict（原生路径）和 Document（LangChain 路径）
        if hasattr(c, "page_content"):
            text = c.page_content
            source = c.metadata.get("source", "未知")
            page = c.metadata.get("page", 0)
            chunk_type = c.metadata.get("chunk_type", "text")
            image_url = c.metadata.get("image_url")
        else:
            text = c["text"]
            source = c["source"]
            page = c.get("page", 0)
            chunk_type = c.get("chunk_type", "text")
            image_url = c.get("image_url")

        label = f"[{i+1}] 来源：{source}"
        if page:
            label += f" 第{page}页"
        if chunk_type == "image":
            label += "（图片描述）"
        text = broken_img_re.sub('', text)
        part = f"{label}\n{text}"
        if chunk_type == "image" and image_url:
            part += f"\n图片URL：{image_url}"
        context_parts.append(part)
    return "\n\n".join(context_parts)


def _build_sources(chunks) -> list:
    """
    从检索结果中提取结构化来源列表（Citation），供前端侧边栏溯源展示。
    供 LangChain Chain 和原生路径共用。

    Returns:
        list of Citation dicts:
          {id, source, page, chunk_type, text, image_url}
    """
    sources = []
    for i, c in enumerate(chunks, 1):
        if hasattr(c, "page_content"):
            text = c.page_content
            source = c.metadata.get("source", "未知")
            page = c.metadata.get("page", 0)
            chunk_type = c.metadata.get("chunk_type", "text")
            image_url = c.metadata.get("image_url")
        else:
            text = c["text"]
            source = c["source"]
            page = c.get("page", 0)
            chunk_type = c.get("chunk_type", "text")
            image_url = c.get("image_url")

        sources.append({
            "id": i,
            "source": source,
            "page": page,
            "chunk_type": chunk_type,
            "text": text,
            "image_url": image_url,
        })
    return sources


def _chat_gen(state: AppState, llm_model: str, message: str, history: List[MessageItem],
              image_chunks=None):
    """RAG 问答生成器：多查询 + 双路检索 + 重排序 + 图片 URL 透传。"""
    if state.get_doc_count() == 0:
        yield "⚠️ 知识库为空，请先点击入库按钮导入文档。"
        return

    # ===== 判断是否使用 LangChain 路径 =====
    use_langchain = (
        state.lc_chat_model is not None
        and state.lc_retriever is not None
        and state.lc_memory_manager is not None
    )

    if use_langchain:
        yield from _chat_gen_langchain(state, message, history, image_chunks)
    else:
        yield from _chat_gen_native(state, llm_model, message, history, image_chunks)


def _chat_gen_langchain(state: AppState, message: str, history: List[MessageItem], image_chunks=None):
    """LangChain 路径：使用 Chain + Retriever + Memory 组件。"""
    from backend.langchain_components.chains import build_multi_query_chain, build_rag_chain
    from backend.langchain_components.memory import ChatMemoryManager

    lc = state.lc_chat_model
    retriever = state.lc_retriever
    memory_mgr = state.lc_memory_manager

    # ===== 阶段一：多查询生成（通过 LangChain Chain）=====
    yield "__STAGE__:正在生成多角度检索查询..."
    try:
        multi_query_chain = build_multi_query_chain(lc)
        extra_queries = multi_query_chain.invoke({
            "question": message, "count": MULTI_QUERY_COUNT
        })
        extra_queries = extra_queries[:MULTI_QUERY_COUNT]
        print(f"[chat-lc] 多查询生成成功：{extra_queries}")
    except Exception as e:
        print(f"[chat-lc] 多查询生成失败（{e}），降级为单查询")
        extra_queries = []

    # ===== 阶段二+三：多查询分别检索 + 去重 + 重排序（通过 Retriever）=====
    yield "__STAGE__:正在向量检索知识库..."
    all_queries = [message] + extra_queries
    try:
        # 用多查询分别调 Retriever，合并去重
        seen = {}
        for q in all_queries:
            for doc in retriever.invoke(q):
                doc_id = doc.metadata.get("id", id(doc))
                dist = doc.metadata.get("distance", 0)
                if doc_id not in seen or dist > seen[doc_id].metadata.get("distance", 0):
                    seen[doc_id] = doc
        docs = sorted(seen.values(),
                      key=lambda d: d.metadata.get("rerank_score") or d.metadata.get("distance", 0),
                      reverse=True)[:TOP_K]
    except Exception as e:
        yield f"❌ 向量检索失败，请尝试重新入库。（{e}）"
        return

    if not docs:
        yield "⚠️ 知识库为空，请先点击入库按钮导入文档。"
        return

    # 注入 CLIP 以图搜图的图片块
    if image_chunks:
        from langchain_core.documents import Document
        existing_ids = {d.metadata.get("id") for d in docs}
        for ic in image_chunks:
            if ic.get("id") not in existing_ids:
                docs.append(Document(
                    page_content=ic["text"],
                    metadata={
                        "id": ic.get("id"),
                        "source": ic.get("source", "上传图片"),
                        "page": ic.get("page", 0),
                        "chunk_type": "image",
                        "image_url": ic.get("image_url"),
                        "distance": ic.get("distance", 1.0),
                    }
                ))

    # ===== 阶段四：构建上下文 + 流式 LLM 调用（通过 LCEL Chain）=====
    yield "__STAGE__:正在生成回答..."
    context = _format_context(docs)
    lc_history = ChatMemoryManager.history_to_messages(history)
    rag_chain = build_rag_chain(lc)

    full_answer = ""
    try:
        for chunk in rag_chain.stream({
            "context": context,
            "question": message,
            "history": lc_history,
        }):
            full_answer += chunk
            yield full_answer
    except Exception as e:
        yield f"❌ LLM 调用失败：{e}"
        return

    # ===== 阶段五：追加结构化来源 JSON（供前端溯源侧边栏使用）=====
    sources = _build_sources(docs)
    yield full_answer + _SOURCES_JSON_SEP + json.dumps(sources, ensure_ascii=False)


def _chat_gen_native(state: AppState, llm_model: str, message: str, history: List[MessageItem],
                     image_chunks=None):
    """原生路径（fallback）：使用 OpenAI SDK 直接调用，与原有逻辑完全一致。"""
    # ===== 阶段一：多查询生成 =====
    yield "__STAGE__:正在生成多角度检索查询..."
    extra_queries = _generate_extra_queries(state, llm_model, message, MULTI_QUERY_COUNT)
    all_queries = [message] + extra_queries

    # ===== 阶段二：双路多查询检索 + 去重 =====
    yield "__STAGE__:正在向量检索知识库..."
    try:
        candidates = _multi_query_retrieve(state, all_queries, RECALL_K)
    except Exception as e:
        yield f"❌ 向量检索失败，请尝试重新入库。（{e}）"
        return
    if not candidates:
        yield "⚠️ 知识库为空，请先点击入库按钮导入文档。"
        return

    # ===== 阶段三：流程图提权 + 重排序 =====
    yield "__STAGE__:正在对检索结果重排序..."
    candidates = _boost_flowchart_chunks(candidates, message)
    chunks = _rerank(state, message, candidates, TOP_K)

    # 注入 CLIP 以图搜图的图片块（前端上传图片时传来，去重合并）
    if image_chunks:
        existing_ids = {c.get("id") for c in chunks}
        for ic in image_chunks:
            if ic.get("id") not in existing_ids:
                chunks.append(ic)

    # ===== 阶段四：构建 messages 并流式调用 LLM =====
    yield "__STAGE__:正在生成回答..."
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for item in history[-12:]:
        if item.role in ("user", "assistant"):
            messages.append({"role": item.role, "content": item.content or ""})

    context = _format_context(chunks)
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

    # ===== 阶段五：追加结构化来源 JSON（供前端溯源侧边栏使用）=====
    sources = _build_sources(chunks)
    yield full_answer + _SOURCES_JSON_SEP + json.dumps(sources, ensure_ascii=False)
