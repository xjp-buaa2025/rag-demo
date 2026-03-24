"""
backend/langchain_components/agents.py — Agents 组件

构建 RAG Agent，根据用户问题动态选择工具（知识库检索、BOM 查询、图片处理等）。
主要应用场景：/assembly/chat 路由的智能化改造。

核心函数：
  build_rag_agent() — 构建 Agent（基于 langchain.agents.create_agent / LangGraph）

Agent 决策示例：
  - "高压涡轮的装配步骤" → rag_search + bom_query
  - "涡轮盘的材料是什么" → bom_query
  - "什么是喘振" → rag_search
  - "描述这张图片" → vision_describe
  - "找一张燃烧室的图" → image_search
  - "计算叶片应力" → calculator + rag_search
"""

from typing import List

from langchain_core.tools import BaseTool


_AGENT_SYSTEM_PROMPT = (
    "你是一个智能装配助手，可以使用多种工具回答用户关于航空发动机的问题。\n"
    "根据用户问题的类型，选择最合适的工具：\n"
    "- 如果问题涉及零件清单、BOM结构、零件关系 -> 使用 bom_query 工具\n"
    "- 如果问题涉及技术知识、工艺参数、原理说明 -> 使用 rag_search 工具\n"
    "- 如果问题同时涉及 BOM 和技术知识 -> 两个工具都使用\n"
    "- 如果用户上传了图片或提到图片描述 -> 使用 vision_describe 或 image_search 工具\n"
    "- 如果需要数值计算（力矩、公差等）-> 使用 calculator 工具\n"
    "请始终使用中文回答。"
)


def build_rag_agent(llm, tools: List[BaseTool]):
    """
    构建 RAG Agent。

    langchain 1.2.10+ 使用 create_agent()（底层基于 LangGraph），
    替代旧版 AgentExecutor + create_openai_tools_agent。

    Args:
        llm: FallbackChatModel（需支持 tool calling）
        tools: create_tools() 返回的工具列表

    Returns:
        CompiledStateGraph — 可 invoke / stream 的 Agent 图
    """
    from langchain.agents import create_agent

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=_AGENT_SYSTEM_PROMPT,
    )

    return agent
