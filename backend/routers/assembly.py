"""
backend/routers/assembly.py — 装配方案问答接口

POST /assembly/chat
  请求体：{"message": "用户问题", "history": [...]}
  响应：SSE 流（同 /chat）

双路融合：同时查询 Neo4j BOM 图谱 + Qdrant 知识库，再流式生成装配方案。
迁移自 app.py assembly_chat()。
"""

from typing import List
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from backend.deps import get_state, get_neo4j_cfg
from backend.state import AppState
from backend.sse import chat_gen_to_sse
from backend.routers.bom import _get_neo4j_driver, _query_bom_text

router = APIRouter(prefix="/assembly")

TOP_K = 4

ASSEMBLY_SYSTEM_PROMPT = """你是一名资深航空发动机装配工程师，熟悉涡扇发动机的结构设计和装配工艺。
根据提供的 BOM 零件清单和技术知识库内容，生成详细的装配方案。
方案须包含：零件清单确认、装配顺序（步骤编号）、工艺要点（力矩/公差/工装）、注意事项。
若 BOM 或知识库无相关数据，请说明并基于通用工程知识回答。"""


class MessageItem(BaseModel):
    role: str
    content: str


class AssemblyChatRequest(BaseModel):
    message: str
    history: List[MessageItem] = []


@router.post("/chat", summary="装配方案流式问答（SSE）")
def assembly_chat(
    body: AssemblyChatRequest,
    request: Request,
    state: AppState = Depends(get_state),
    cfg: dict = Depends(get_neo4j_cfg),
):
    llm_model = request.app.state.llm_model
    gen = _assembly_chat_gen(state, cfg, llm_model, body.message, body.history)
    return chat_gen_to_sse(gen)


def _assembly_chat_gen(
    state: AppState, cfg: dict, llm_model: str, message: str, history: List[MessageItem]
):
    """装配方案生成器，迁移自 app.py assembly_chat()。"""
    # 1. 并行查询两路数据（同步调用，在线程池中执行）
    bom_text   = _query_bom_text(state, cfg, message)
    n          = min(TOP_K, state.get_doc_count())
    rag_chunks = []
    if n > 0:
        from backend.routers.retrieve import qdrant_search_text
        hits = qdrant_search_text(state.qdrant_client, state.embedding_mgr, message, n)
        rag_chunks = [
            {"text": h["text"], "source": h["source"], "page": h["page"]}
            for h in hits
        ]

    # 2. 构建融合 prompt
    sections = []
    if bom_text:
        sections.append(f"【BOM 零件清单（来自图数据库）】\n{bom_text}")
    if rag_chunks:
        rag_ctx = "\n\n".join(
            f"[{i+1}] 来源:{c['source']}\n{c['text']}"
            for i, c in enumerate(rag_chunks)
        )
        sections.append(f"【技术知识库（来自教材）】\n{rag_ctx}")

    user_content = "\n\n".join(sections) + f"\n\n【用户问题】\n{message}" if sections else message

    # 3. 构建多轮历史
    messages = [{"role": "system", "content": ASSEMBLY_SYSTEM_PROMPT}]
    for item in history[-8:]:
        if item.role in ("user", "assistant"):
            messages.append({"role": item.role, "content": item.content or ""})
    messages.append({"role": "user", "content": user_content})

    # 4. 流式 LLM 调用
    full_answer = ""
    try:
        stream = state.llm_client.chat.completions.create(
            model=llm_model, messages=messages, temperature=0.3, stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            full_answer += delta
            yield full_answer
    except Exception as e:
        yield f"❌ LLM 调用失败：{e}"
        return

    # 5. 追加来源注脚（使用 sse.py 约定的分隔符前缀）
    footnote = ""
    if bom_text:
        footnote += "\n\n---\n**🔩 BOM 数据来源**：Neo4j 图数据库"
    if rag_chunks:
        refs = "".join(
            f"**[{i+1}] {c['source']}**  \n_{c['text'][:80].replace(chr(10),' ')}…_\n"
            for i, c in enumerate(rag_chunks, 1)
        )
        footnote += f"\n\n---\n**📚 知识库参考**\n{refs}"
    if footnote:
        yield full_answer + footnote
