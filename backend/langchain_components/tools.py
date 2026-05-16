"""
backend/langchain_components/tools.py — Tools 组件

将现有的检索、BOM 查询、Vision 等功能封装为 LangChain @tool，
供 Agent 动态调用。

工具列表：
  rag_search      — 知识库检索（bge-m3 文本检索）
  bom_query       — BOM 图谱查询（Neo4j）
  vision_describe — 图片中文描述（MiniMax Vision API）
  image_search    — 以文搜图（Chinese-CLIP）
  calculator      — 数学计算（力矩/公差等）

通过 create_tools() 工厂函数创建，用闭包绑定 AppState。
"""

import math

from langchain_core.tools import tool


def create_tools(state, neo4j_cfg: dict):
    """
    工厂函数：创建所有工具实例，通过闭包绑定 AppState。

    Args:
        state: AppState 实例（提供 qdrant_client, embedding_mgr 等）
        neo4j_cfg: Neo4j 连接配置 {"uri", "user", "pass"}

    Returns:
        List[BaseTool] — 5 个工具的列表
    """

    @tool
    def rag_search(query: str) -> str:
        """搜索技术知识库。适用于查询技术原理、工艺参数、设计规范、故障诊断等知识性问题。输入用户的查询问题（中文），返回检索到的相关文档片段。"""
        from backend.routers.retrieve import qdrant_search_text

        n = min(4, state.get_doc_count())
        if n == 0:
            return "知识库为空，无法检索。"
        hits = qdrant_search_text(
            state.qdrant_client, state.embedding_mgr, query, n
        )
        if not hits:
            return "未找到相关内容。"
        parts = []
        for i, h in enumerate(hits, 1):
            source = h["source"]
            page = h.get("page", 0)
            page_info = f" 第{page}页" if page else ""
            parts.append(f"[{i}] 来源：{source}{page_info}\n{h['text']}")
        return "\n\n".join(parts)

    @tool
    def bom_query(question: str) -> str:
        """查询零件清单与知识图谱。适用于查询零件编号、料号、组装关系、材料规格、装配接口等信息。输入关于零件或装配结构的问题（中文），返回包含真实料号的 BOM + KG 查询结果。"""
        from backend.routers.bom import _query_kg_context, _query_bom_text

        kg_result = _query_kg_context(state, neo4j_cfg, question)
        bom_result = _query_bom_text(state, neo4j_cfg, question)
        parts = []
        if kg_result:
            parts.append(kg_result)
        if bom_result:
            parts.append(f"【补充 BOM 信息】\n{bom_result}")
        return "\n\n".join(parts) if parts else "图谱中未找到相关零件信息。"

    @tool
    def vision_describe(image_path: str) -> str:
        """获取图片的中文描述。适用于需要理解图片内容的场景。输入图片文件的路径，返回图片的中文描述文字。"""
        if state.minimax_client is None:
            return "Vision 功能未启用（未配置 MiniMax API Key）。"
        from backend.image_captioner import describe_image

        desc = describe_image(
            state.minimax_client, state.minimax_model, image_path
        )
        return desc if desc else "图片描述生成失败。"

    @tool
    def image_search(query: str) -> str:
        """用文字描述搜索知识库中的相关图片。适用于根据文字描述找图片的场景。输入描述要搜索图片的文字（中文），返回匹配的图片列表。"""
        from backend.routers.retrieve import qdrant_search_image

        total = state.get_doc_count()
        if total == 0:
            return "知识库为空。"
        try:
            hits = qdrant_search_image(
                state.qdrant_client, state.embedding_mgr, query, min(4, total)
            )
            if not hits:
                return "未找到相关图片。"
            parts = []
            for i, h in enumerate(hits, 1):
                parts.append(
                    f"[{i}] 来源：{h['source']} (相似度：{h['distance']:.3f})\n{h['text']}"
                )
            return "\n\n".join(parts)
        except Exception as e:
            return f"图片检索失败：{e}"

    @tool
    def calculator(expression: str) -> str:
        """计算数学表达式。适用于需要数值计算的场景（如力矩、公差、面积计算）。输入 Python 数学表达式（如 '3.14 * 2.5 ** 2'），返回计算结果。"""
        allowed = {
            k: getattr(math, k)
            for k in dir(math)
            if not k.startswith("_")
        }
        allowed.update({"abs": abs, "round": round, "min": min, "max": max})
        try:
            result = eval(expression, {"__builtins__": {}}, allowed)
            return str(result)
        except Exception as e:
            return f"计算错误：{e}"

    @tool
    def procedure_chain_query(question: str) -> str:
        """查询装配工序、工具和规范。适用于询问装配步骤、操作顺序、所需工具、技术参数等问题。返回从知识图谱提取的工序列表（含工具名称和规范参数）以及相关零件料号。"""
        from backend.routers.bom import _query_kg_context

        result = _query_kg_context(state, neo4j_cfg, question)
        return result if result else "知识图谱中未找到相关装配工序信息。"

    return [rag_search, bom_query, procedure_chain_query, vision_describe, image_search, calculator]
