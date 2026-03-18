"""
backend/routers/chat.py — RAG 问答接口

POST /chat
  请求体：{"message": "用户问题", "history": [...OpenAI messages 格式...]}
  响应：SSE 流
    中间帧：data: {"delta": "<新增文本>"}\n\n
    最后帧：data: {"done": true, "sources_md": "<参考来源 Markdown>"}\n\n

迁移自 app.py chat()：
  - 向量检索 → 拼装 prompt → 流式调用 LLM → 追加来源
  - 支持 Gradio 5+ 和 Gradio 4 两种 history 格式（兼容 app.py 逻辑）
  - FastAPI 端统一使用 OpenAI messages 格式：[{"role": "user"|"assistant", "content": str}]
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from backend.deps import get_state, get_llm_model
from backend.state import AppState
from backend.sse import chat_gen_to_sse

router = APIRouter()

TOP_K = 4

SYSTEM_PROMPT = """你是一个专业的知识库问答助手。请严格根据提供的参考资料回答用户问题。
如果参考资料中没有相关信息，请如实说明"知识库中没有找到相关内容"，不要凭空捏造。
回答要详细、准确、有条理，尽量引用原文中的具体数据和技术细节，不要省略重要信息。"""


class MessageItem(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: List[MessageItem] = []


@router.post("/chat", summary="RAG 流式问答（SSE）")
def chat(body: ChatRequest, request: Request, state: AppState = Depends(get_state)):
    llm_model = request.app.state.llm_model
    gen = _chat_gen(state, llm_model, body.message, body.history)
    return chat_gen_to_sse(gen)


def _chat_gen(state: AppState, llm_model: str, message: str, history: List[MessageItem]):
    """RAG 问答生成器，迁移自 app.py chat()。"""
    if state.collection.count() == 0:
        yield "⚠️ 知识库为空，请先点击入库按钮导入文档。"
        return

    # 向量检索
    n = min(TOP_K, state.collection.count())
    query_embedding = state.embedding_func([message])[0]
    results = state.collection.query(
        query_embeddings=[query_embedding],
        n_results=n,
        include=["documents", "metadatas", "distances"],
    )
    chunks = [
        {"text": doc, "source": meta.get("source", "未知"),
         "page": meta.get("page", 0), "distance": dist}
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        )
    ]

    # 构建 messages（system + 历史 + 当前问题 + 参考资料）
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
