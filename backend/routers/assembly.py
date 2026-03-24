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
    """
    装配方案生成器。
    优先使用 LangChain Chain 模式（如已初始化），否则走原生路径。
    Agent 模式通过 /assembly/agent 路由单独提供。
    """
    use_langchain = (
        state.lc_chat_model is not None
        and state.lc_memory_manager is not None
    )

    if use_langchain:
        yield from _assembly_chat_gen_langchain(state, cfg, message, history)
    else:
        yield from _assembly_chat_gen_native(state, cfg, llm_model, message, history)


def _assembly_chat_gen_langchain(
    state: AppState, cfg: dict, message: str, history: List[MessageItem]
):
    """LangChain Chain 路径：使用 LCEL 装配链。"""
    from backend.langchain_components.chains import build_assembly_chain
    from backend.langchain_components.memory import ChatMemoryManager

    # 1. 查询两路数据
    bom_text = _query_bom_text(state, cfg, message)
    rag_chunks = []
    n = min(TOP_K, state.get_doc_count())
    if n > 0:
        if state.lc_retriever is not None:
            docs = state.lc_retriever.invoke(message)
            rag_chunks = [
                {"text": d.page_content, "source": d.metadata.get("source", ""),
                 "page": d.metadata.get("page", 0)}
                for d in docs
            ]
        else:
            from backend.routers.retrieve import qdrant_search_text
            hits = qdrant_search_text(state.qdrant_client, state.embedding_mgr, message, n)
            rag_chunks = [
                {"text": h["text"], "source": h["source"], "page": h["page"]}
                for h in hits
            ]

    # 2. 构建融合上下文
    sections = []
    if bom_text:
        sections.append(f"【BOM 零件清单（来自图数据库）】\n{bom_text}")
    if rag_chunks:
        rag_ctx = "\n\n".join(
            f"[{i+1}] 来源:{c['source']}\n{c['text']}"
            for i, c in enumerate(rag_chunks)
        )
        sections.append(f"【技术知识库（来自教材）】\n{rag_ctx}")
    sections_text = "\n\n".join(sections) if sections else ""

    # 3. 流式调用 Assembly Chain
    lc_history = ChatMemoryManager.history_to_messages(history, max_messages=8)
    assembly_chain = build_assembly_chain(state.lc_chat_model)

    full_answer = ""
    try:
        for chunk in assembly_chain.stream({
            "sections": sections_text,
            "question": message,
            "history": lc_history,
        }):
            full_answer += chunk
            yield full_answer
    except Exception as e:
        yield f"❌ LLM 调用失败：{e}"
        return

    # 4. 追加来源注脚
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


def _assembly_chat_gen_native(
    state: AppState, cfg: dict, llm_model: str, message: str, history: List[MessageItem]
):
    """原生路径（fallback）：与原有逻辑完全一致。"""
    bom_text = _query_bom_text(state, cfg, message)
    n = min(TOP_K, state.get_doc_count())
    rag_chunks = []
    if n > 0:
        from backend.routers.retrieve import qdrant_search_text
        hits = qdrant_search_text(state.qdrant_client, state.embedding_mgr, message, n)
        rag_chunks = [
            {"text": h["text"], "source": h["source"], "page": h["page"]}
            for h in hits
        ]

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

    messages = [{"role": "system", "content": ASSEMBLY_SYSTEM_PROMPT}]
    for item in history[-8:]:
        if item.role in ("user", "assistant"):
            messages.append({"role": item.role, "content": item.content or ""})
    messages.append({"role": "user", "content": user_content})

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


# ==========================================
# Agent 模式路由（独立入口，不影响原有 /assembly/chat）
# ==========================================

class AgentChatRequest(BaseModel):
    message: str
    history: List[MessageItem] = []


@router.post("/agent", summary="Agent 智能问答（SSE，自动选择工具）")
def assembly_agent_chat(
    body: AgentChatRequest,
    request: Request,
    state: AppState = Depends(get_state),
    cfg: dict = Depends(get_neo4j_cfg),
):
    """
    Agent 模式：根据问题自动选择工具（知识库/BOM/图片/计算器）。
    与 /assembly/chat 的区别：Chain 模式总是查 BOM+知识库，Agent 模式由 LLM 自主决策。
    """
    if state.lc_agent is None:
        # Agent 未初始化，降级到 Chain 模式
        llm_model = request.app.state.llm_model
        gen = _assembly_chat_gen(state, cfg, llm_model, body.message, body.history)
        return chat_gen_to_sse(gen)

    gen = _assembly_agent_gen(state, body.message, body.history)
    return chat_gen_to_sse(gen)


def _assembly_agent_gen(state: AppState, message: str, history: List[MessageItem]):
    """Agent 模式生成器：LangGraph Agent 自主选择工具。"""
    from backend.langchain_components.memory import ChatMemoryManager
    from langchain_core.messages import AIMessage, HumanMessage

    lc_history = ChatMemoryManager.history_to_messages(history, max_messages=8)

    # create_agent (LangGraph) 输入格式：messages 列表
    input_messages = list(lc_history) + [HumanMessage(content=message)]

    full_answer = ""
    try:
        for event in state.lc_agent.stream({"messages": input_messages}):
            # LangGraph agent 的流式输出：每个 event 是 {node_name: {"messages": [...]}}
            for node_output in event.values():
                msgs = node_output.get("messages", [])
                for msg in msgs:
                    if isinstance(msg, AIMessage) and msg.content and not msg.tool_calls:
                        full_answer = msg.content
                        yield full_answer
    except Exception as e:
        yield f"❌ Agent 调用失败：{e}"
