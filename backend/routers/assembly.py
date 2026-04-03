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
from backend.sse import chat_gen_to_sse, _SOURCES_JSON_SEP
from backend.routers.bom import _get_neo4j_driver, _query_bom_text, _query_bom_entities, _query_procedure_chain

router = APIRouter(prefix="/assembly")

TOP_K = 4

ASSEMBLY_SYSTEM_PROMPT = """你是一名资深航空发动机装配工程师，熟悉涡扇发动机的结构设计和装配工艺。
根据提供的 BOM 零件清单和技术知识库内容，生成详细的装配方案。
方案须包含：零件清单确认、装配顺序（步骤编号）、工艺要点（力矩/公差/工装）、注意事项。
若 BOM 或知识库无相关数据，请说明并基于通用工程知识回答。

**重要：引用标注要求**
参考资料已按编号 [1][2][3]... 标注。在回答中，每引用某条资料的具体内容时，请在该句末尾紧跟对应编号，例如："高压涡轮叶片装配需使用专用工装 [1]。"若同时引用多条，则写 [1][3]。请务必标注，不要遗漏。"""


REL_LABEL_MAP = {
    "CHILD_OF":       "子组件属于",
    "precedes":       "工序先于",
    "participatesIn": "参与工序",
    "requires":       "需要工具",
    "specifiedBy":    "遵循规范",
    "matesWith":      "配合关系",
    "adjacentTo":     "相邻关系",
    "hasInterface":   "具有接口",
    "constrainedBy":  "受约束于",
    "isPartOf":       "属于组件",
}


def _build_assembly_context_and_sources(
    bom_result: dict,
    rag_chunks: list,
    proc_text: str = "",
):
    """
    将有序工序链、BOM 实体/关系列表和 RAG 文档块合并为统一编号的上下文字符串和 Citation 列表。

    来源优先级：
      [1] 有序工序链（KG precedes 路径，如有）
      [2..N] BOM 实体（bom_entity）
      [N+1..M] BOM 关系（bom_relation）
      [M+1..] RAG 文档块

    兼容 bom_result 为空（{"entities":[], "relations":[]}）的情况。
    """
    import json as _json
    sources = []
    context_parts = []
    idx = 1

    # ── 有序工序链（最高优先级）────────────────────────────────
    if proc_text:
        context_parts.append(f"[{idx}] 来源：知识图谱工序链（Neo4j KG）\n{proc_text}")
        sources.append({
            "id":         idx,
            "source":     "知识图谱工序链（Neo4j KG）",
            "page":       0,
            "chunk_type": "kg_procedure",
            "text":       proc_text,
            "image_url":  None,
        })
        idx += 1

    entities = bom_result.get("entities", [])
    relations = bom_result.get("relations", [])

    # ── BOM 实体 → 独立 Citation ──────────────────────────────
    for entity in entities:
        part_id   = entity.get("part_id", "")
        part_name = entity.get("part_name", "")
        etype     = entity.get("entity_type", "Part")

        ctx_lines = [f"[{idx}] 来源：BOM图谱 实体（{etype}）"]
        ctx_lines.append(f"零件名称：{part_name}（{part_id}）")
        if entity.get("part_name_en"):
            ctx_lines.append(f"英文名称：{entity['part_name_en']}")
        if entity.get("qty") is not None:
            ctx_lines.append(f"数量：{entity['qty']} {entity.get('unit', '')}")
        if entity.get("material"):
            ctx_lines.append(f"材料：{entity['material']}")
        if entity.get("weight_kg") is not None:
            ctx_lines.append(f"重量：{entity['weight_kg']} kg")
        if entity.get("spec"):
            ctx_lines.append(f"规格：{entity['spec']}")
        if entity.get("note"):
            ctx_lines.append(f"备注：{entity['note']}")
        if entity.get("parent_name"):
            ctx_lines.append(f"上级组件：{entity['parent_name']}（{entity.get('parent_id', '')}）")
        context_parts.append("\n".join(ctx_lines))

        summary_parts = [part_name]
        if entity.get("material"):
            summary_parts.append(f"材料: {entity['material']}")
        if entity.get("qty") is not None:
            summary_parts.append(f"数量: {entity['qty']}{entity.get('unit', '')}")
        if entity.get("spec"):
            summary_parts.append(f"规格: {entity['spec']}")

        sources.append({
            "id":         idx,
            "source":     f"BOM · {etype} · {part_name}",
            "page":       0,
            "chunk_type": "bom_entity",
            "text":       "  |  ".join(summary_parts),
            "image_url":  None,
            "bom_entity": entity,
        })
        idx += 1

    # ── BOM 关系 → 独立 Citation ──────────────────────────────
    for rel in relations:
        rel_type  = rel.get("rel_type", "CHILD_OF")
        from_name = rel.get("from_name", "")
        to_name   = rel.get("to_name", "")
        rel_label = REL_LABEL_MAP.get(rel_type, rel_type)

        ctx_lines = [
            f"[{idx}] 来源：BOM图谱 关系（{rel_type}）",
            f"{from_name}（{rel.get('from_id', '')}）—[{rel_label}]→ {to_name}（{rel.get('to_id', '')}）",
        ]
        context_parts.append("\n".join(ctx_lines))

        sources.append({
            "id":          idx,
            "source":      f"BOM · {rel_label} · {from_name} → {to_name}",
            "page":        0,
            "chunk_type":  "bom_relation",
            "text":        f"{from_name} —[{rel_label}]→ {to_name}",
            "image_url":   None,
            "bom_relation": rel,
        })
        idx += 1

    # ── RAG 文档块（逻辑不变）────────────────────────────────
    for c in rag_chunks:
        label = f"[{idx}] 来源：{c['source']}"
        if c.get("page"):
            label += f" 第{c['page']}页"
        context_parts.append(f"{label}\n{c['text']}")
        sources.append({
            "id":         idx,
            "source":     c["source"],
            "page":       c.get("page", 0),
            "chunk_type": c.get("chunk_type", "text"),
            "text":       c["text"],
            "image_url":  c.get("image_url"),
        })
        idx += 1

    return "\n\n".join(context_parts), sources


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

    # 1. 三路数据：工序链（KG）+ BOM 实体/关系 + RAG 文档块
    yield "__STAGE__:正在查询 BOM 图谱与工序链..."
    _, proc_text = _query_procedure_chain(state, cfg, message)
    bom_result = _query_bom_entities(state, cfg, message)
    yield "__STAGE__:正在检索知识库..."
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

    # 2. 构建统一编号的上下文 + 结构化来源列表（每实体/关系独立编号）
    import json as _json
    context, sources = _build_assembly_context_and_sources(bom_result, rag_chunks, proc_text)

    # 3. 流式调用 Assembly Chain
    yield "__STAGE__:正在生成装配方案..."
    lc_history = ChatMemoryManager.history_to_messages(history, max_messages=8)
    assembly_chain = build_assembly_chain(state.lc_chat_model)

    full_answer = ""
    try:
        for chunk in assembly_chain.stream({
            "sections": context,
            "question": message,
            "history": lc_history,
        }):
            full_answer += chunk
            yield full_answer
    except Exception as e:
        yield f"❌ LLM 调用失败：{e}"
        return

    # 4. 追加结构化来源 JSON（供前端溯源侧边栏使用）
    if sources:
        yield full_answer + _SOURCES_JSON_SEP + _json.dumps(sources, ensure_ascii=False)


def _assembly_chat_gen_native(
    state: AppState, cfg: dict, llm_model: str, message: str, history: List[MessageItem]
):
    """原生路径（fallback）：三路数据融合（KG工序链 + BOM + RAG）。"""
    yield "__STAGE__:正在查询 BOM 图谱与工序链..."
    _, proc_text = _query_procedure_chain(state, cfg, message)
    bom_result = _query_bom_entities(state, cfg, message)
    yield "__STAGE__:正在检索知识库..."
    n = min(TOP_K, state.get_doc_count())
    rag_chunks = []
    if n > 0:
        from backend.routers.retrieve import qdrant_search_text
        hits = qdrant_search_text(state.qdrant_client, state.embedding_mgr, message, n)
        rag_chunks = [
            {"text": h["text"], "source": h["source"], "page": h["page"]}
            for h in hits
        ]

    import json as _json
    context, sources = _build_assembly_context_and_sources(bom_result, rag_chunks, proc_text)
    user_content = f"{context}\n\n【用户问题】\n{message}" if context else message

    yield "__STAGE__:正在生成装配方案..."
    llm_messages = [{"role": "system", "content": ASSEMBLY_SYSTEM_PROMPT}]
    for item in history[-8:]:
        if item.role in ("user", "assistant"):
            llm_messages.append({"role": item.role, "content": item.content or ""})
    llm_messages.append({"role": "user", "content": user_content})

    full_answer = ""
    try:
        stream = state.llm_client.chat.completions.create(
            model=llm_model, messages=llm_messages, temperature=0.3, stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            full_answer += delta
            yield full_answer
    except Exception as e:
        yield f"❌ LLM 调用失败：{e}"
        return

    # 追加结构化来源 JSON（供前端溯源侧边栏使用）
    if sources:
        yield full_answer + _SOURCES_JSON_SEP + _json.dumps(sources, ensure_ascii=False)


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
