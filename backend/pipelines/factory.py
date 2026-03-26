"""
backend/pipelines/factory.py — LangGraph 管道工厂函数

提供两个管道构建函数：
  make_rag_pipeline(app_state, image_dir) -> CompiledStateGraph
  make_bom_pipeline(app_state, neo4j_cfg) -> CompiledStateGraph

图结构：
  RAG: detect_input -> [pdf_to_md -> generate_captions ->] chunk_text
       -> encode_text_vectors -> [encode_image_vectors ->] upsert_qdrant
       PDF路径: ... -> generate_tech_captions -> extract_flowchart_structure -> encode_text_vectors

  BOM: detect_input -> [extract_tables -> llm_to_csv ->] load_table
       -> validate_bom_df -> write_neo4j
"""

from typing import Any

from langgraph.graph import END, START, StateGraph

from backend.pipelines.nodes_common import detect_input, error_handler
from backend.pipelines.nodes_rag import make_rag_nodes
from backend.pipelines.nodes_bom import make_bom_nodes
from backend.pipelines.nodes_manual import make_manual_nodes
from backend.pipelines.routes import (
    route_entry,
    route_rag_by_ext,
    route_bom_by_ext,
    route_after_pdf_to_md,
    route_after_encode_text,
    route_after_extract_figures,
)
from backend.pipelines.state import PipelineState


def make_rag_pipeline(app_state: Any, image_dir: str):
    """
    构建 RAG 知识库入库管道（统一智能入口）。

    路由逻辑：
    - PDF 文件 -> analyze_pdf_type -> deepdoc_parse_pdf -> vision_layout_agent -> extract_structure
                -> build_cross_refs -> semantic_chunk -> extract_figures
                -> [generate_tech_captions ->] encode_text_vectors
                -> [encode_image_vectors ->] upsert_qdrant
    - MD/TXT 文件 -> chunk_text -> encode_text_vectors -> upsert_qdrant

    Returns:
        CompiledStateGraph — 可 .stream() / .invoke() 的图
    """
    rag_nodes = make_rag_nodes(app_state, image_dir)
    manual_nodes = make_manual_nodes(app_state, image_dir)

    graph = StateGraph(PipelineState)

    # 注册共用节点
    graph.add_node("detect_input", detect_input)
    graph.add_node("error_handler", error_handler)

    # 路由占位节点
    graph.add_node("rag_entry", _noop)

    # 注册 RAG 功能节点（MD/TXT 路径）
    for name, fn in rag_nodes.items():
        graph.add_node(name, fn)

    # 注册 PDF 精细化节点（deepdoc 路径）
    for name, fn in manual_nodes.items():
        graph.add_node(name, fn)

    # ── 边定义 ──────────────────────────────────────────────────

    graph.add_edge(START, "detect_input")
    graph.add_edge("detect_input", "rag_entry")

    # rag_entry -> analyze_pdf_type（PDF）或 chunk_text（MD/TXT）
    graph.add_conditional_edges(
        "rag_entry",
        route_rag_by_ext,
        {
            "analyze_pdf_type": "analyze_pdf_type",
            "chunk_text": "chunk_text",
        },
    )

    # ── PDF 精细化链 ──────────────────────────────────────────
    graph.add_edge("analyze_pdf_type", "deepdoc_parse_pdf")
    graph.add_edge("deepdoc_parse_pdf", "vision_layout_agent")
    graph.add_edge("vision_layout_agent", "extract_structure")
    graph.add_edge("extract_structure", "build_cross_refs")
    graph.add_edge("build_cross_refs", "semantic_chunk")
    graph.add_edge("semantic_chunk", "extract_figures")

    # extract_figures -> generate_tech_captions（有图形）或 encode_text_vectors
    graph.add_conditional_edges(
        "extract_figures",
        route_after_extract_figures,
        {
            "generate_tech_captions": "generate_tech_captions",
            "encode_text_vectors": "encode_text_vectors",
        },
    )

    graph.add_edge("generate_tech_captions", "extract_flowchart_structure")
    graph.add_edge("extract_flowchart_structure", "encode_text_vectors")

    # ── MD/TXT 简单链 ─────────────────────────────────────────
    graph.add_edge("chunk_text", "encode_text_vectors")

    # ── 共用编码+写入链 ───────────────────────────────────────
    graph.add_conditional_edges(
        "encode_text_vectors",
        route_after_encode_text,
        {
            "encode_image_vectors": "encode_image_vectors",
            "upsert_qdrant": "upsert_qdrant",
        },
    )

    graph.add_edge("encode_image_vectors", "upsert_qdrant")

    # 终止
    graph.add_edge("upsert_qdrant", END)
    graph.add_edge("error_handler", END)

    return graph.compile()


def make_bom_pipeline(app_state: Any, neo4j_cfg: dict):
    """
    构建 BOM 图数据库入库管道。

    入口灵活：
    - PDF/DOCX -> extract_tables -> llm_to_csv -> validate_bom_df -> ...
    - Excel/CSV -> 直接 load_table -> validate_bom_df -> ...

    Returns:
        CompiledStateGraph — 可 .stream() / .invoke() 的图
    """
    bom_nodes = make_bom_nodes(app_state, neo4j_cfg)

    graph = StateGraph(PipelineState)

    # 共用节点
    graph.add_node("detect_input", detect_input)
    graph.add_node("error_handler", error_handler)

    # BOM 路由占位节点
    graph.add_node("bom_entry", _noop)

    # BOM 功能节点
    for name, fn in bom_nodes.items():
        graph.add_node(name, fn)

    # 边定义
    graph.add_edge(START, "detect_input")
    graph.add_edge("detect_input", "bom_entry")

    # bom_entry -> extract_tables 或 load_table（按文件类型）
    graph.add_conditional_edges(
        "bom_entry",
        route_bom_by_ext,
        {
            "extract_tables": "extract_tables",
            "load_table": "load_table",
        },
    )

    # extract_tables -> llm_to_csv -> validate_bom_df
    graph.add_edge("extract_tables", "llm_to_csv")
    graph.add_edge("llm_to_csv", "validate_bom_df")

    # load_table -> validate_bom_df
    graph.add_edge("load_table", "validate_bom_df")

    # validate_bom_df -> write_neo4j
    graph.add_edge("validate_bom_df", "write_neo4j")

    # 终止
    graph.add_edge("write_neo4j", END)
    graph.add_edge("error_handler", END)

    return graph.compile()


def _noop(state: dict) -> dict:
    """空节点，仅用于路由分发。"""
    return {}
