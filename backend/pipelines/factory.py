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
    route_after_upsert,
    route_cad_by_ext,
    route_kg_by_stage,
)
from backend.pipelines.state import PipelineState


def make_rag_pipeline(app_state: Any, image_dir: str, neo4j_cfg: dict | None = None):
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
    kg_nodes = {}
    if neo4j_cfg:
        from backend.pipelines.nodes_kg import make_kg_nodes
        kg_nodes = make_kg_nodes(app_state, neo4j_cfg)

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

    # 注册 KG 提取节点（可选，仅在传入 neo4j_cfg 时启用）
    for name, fn in kg_nodes.items():
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
    graph.add_edge("extract_flowchart_structure", "extract_visual_kg")
    graph.add_edge("extract_visual_kg", "encode_text_vectors")

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

    # upsert_qdrant 之后：有 KG 节点则条件路由，否则直接终止
    if kg_nodes:
        graph.add_conditional_edges(
            "upsert_qdrant",
            route_after_upsert,
            {
                "extract_kg_triples": "extract_kg_triples",
                END: END,
            },
        )
        graph.add_edge("extract_kg_triples", "align_entities")
        graph.add_edge("align_entities", "verify_kg_entities")
        graph.add_edge("verify_kg_entities", "validate_kg_dag")
        graph.add_edge("validate_kg_dag", "write_kg_neo4j")
        graph.add_edge("write_kg_neo4j", END)
    else:
        graph.add_edge("upsert_qdrant", END)

    graph.add_edge("error_handler", END)

    return graph.compile()


def make_cad_pipeline(app_state: Any, neo4j_cfg: dict):
    """
    构建 CAD 模型入库管道。

    路由逻辑：
    - STEP/STP 文件 -> parse_cad_step -> cad_to_kg_triples -> END

    Returns:
        CompiledStateGraph — 可 .stream() / .invoke() 的图
    """
    from backend.pipelines.nodes_cad import make_cad_nodes

    cad_nodes = make_cad_nodes(app_state, neo4j_cfg)

    graph = StateGraph(PipelineState)
    graph.add_node("detect_input", detect_input)
    graph.add_node("error_handler", error_handler)
    graph.add_node("cad_entry", _noop)

    for name, fn in cad_nodes.items():
        graph.add_node(name, fn)

    graph.add_edge(START, "detect_input")
    graph.add_edge("detect_input", "cad_entry")

    graph.add_conditional_edges(
        "cad_entry",
        route_cad_by_ext,
        {
            "parse_cad_step": "parse_cad_step",
            "error_handler": "error_handler",
        },
    )

    graph.add_edge("parse_cad_step", "cad_to_kg_triples")
    graph.add_edge("cad_to_kg_triples", END)
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


def make_unified_kg_pipeline(app_state: Any, image_dir: str, neo4j_cfg: dict):
    """
    构建联合 KG 知识图谱入库管道。

    按 kg_task_stage 条件路由到四条子链：
      bom    → BOM 文件处理链  → bom_to_triples → END
      cad    → CAD 文件处理链  → cad_to_triples_node → END
      manual → 手册深度解析链  → extract_kg_triples → END
      merge  → 三源合并+对齐+验证+写库 → END

    复用策略：
      - bom 阶段：直接复用 make_bom_nodes() 中的所有节点
      - cad 阶段：直接复用 make_cad_nodes() 的 parse_cad_step，
                  加上 nodes_kg_unified 的 cad_to_triples_node
      - manual 阶段：复用 make_manual_nodes() + make_kg_nodes() 的 extract_kg_triples
      - merge 阶段：使用 nodes_kg_unified 的 merge/align 节点
                   + make_kg_nodes() 的 verify/dag/write_unified 节点

    Returns:
        CompiledStateGraph — 可 .stream() / .invoke() 的图
    """
    from backend.pipelines.nodes_cad import make_cad_nodes
    from backend.pipelines.nodes_kg import make_kg_nodes
    from backend.pipelines.nodes_kg_unified import make_unified_kg_nodes

    bom_nodes     = make_bom_nodes(app_state, neo4j_cfg)
    cad_nodes     = make_cad_nodes(app_state, neo4j_cfg)
    manual_nodes  = make_manual_nodes(app_state, image_dir)
    rag_nodes     = make_rag_nodes(app_state, image_dir)
    kg_nodes      = make_kg_nodes(app_state, neo4j_cfg)
    unified_nodes = make_unified_kg_nodes(app_state, neo4j_cfg)

    graph = StateGraph(PipelineState)

    # ── 共用节点 ────────────────────────────────────────────────
    graph.add_node("detect_input",  detect_input)
    graph.add_node("error_handler", error_handler)

    # ── 阶段入口占位节点 ─────────────────────────────────────────
    graph.add_node("bom_entry",    _noop)
    graph.add_node("cad_entry",    _noop)
    graph.add_node("manual_entry", _noop)
    graph.add_node("merge_entry",  _noop)

    # ── BOM 阶段节点 ─────────────────────────────────────────────
    for name, fn in bom_nodes.items():
        graph.add_node(name, fn)

    # ── CAD 阶段节点 ─────────────────────────────────────────────
    # parse_cad_step 来自 cad_nodes；cad_to_triples 来自 unified_nodes
    graph.add_node("parse_cad_step",      cad_nodes["parse_cad_step"])
    graph.add_node("cad_to_triples_node", unified_nodes["cad_to_triples"])

    # ── 手册阶段节点（deepdoc 全链）────────────────────────────────
    for name, fn in manual_nodes.items():
        graph.add_node(name, fn)
    # 手册链还需要 rag_nodes 中的编码+写入节点
    for name in ("encode_text_vectors", "encode_image_vectors", "upsert_qdrant"):
        graph.add_node(name, rag_nodes[name])
    # extract_kg_triples 来自 kg_nodes
    graph.add_node("extract_kg_triples_manual", kg_nodes["extract_kg_triples"])

    # ── Merge 阶段节点 ───────────────────────────────────────────
    graph.add_node("merge_multi_source_triples",  unified_nodes["merge_triples"])
    graph.add_node("align_entities_multi_source", unified_nodes["align_entities_unified"])
    graph.add_node("verify_kg_entities",          kg_nodes["verify_kg_entities"])
    graph.add_node("validate_kg_dag",             kg_nodes["validate_kg_dag"])
    graph.add_node("write_kg_neo4j_unified",      kg_nodes["write_kg_neo4j_unified"])

    # ── 边定义 ──────────────────────────────────────────────────

    graph.add_edge(START, "detect_input")

    # detect_input → 按 kg_task_stage 路由
    graph.add_conditional_edges(
        "detect_input",
        route_kg_by_stage,
        {
            "bom_entry":    "bom_entry",
            "cad_entry":    "cad_entry",
            "manual_entry": "manual_entry",
            "merge_entry":  "merge_entry",
            "error_handler": "error_handler",
        },
    )

    # ── BOM 链 ───────────────────────────────────────────────────
    graph.add_conditional_edges(
        "bom_entry",
        route_bom_by_ext,
        {
            "extract_tables": "extract_tables",
            "load_table":     "load_table",
        },
    )
    graph.add_edge("extract_tables",  "llm_to_csv")
    graph.add_edge("llm_to_csv",      "validate_bom_df")
    graph.add_edge("load_table",      "validate_bom_df")
    graph.add_edge("validate_bom_df", "bom_to_triples")
    graph.add_edge("bom_to_triples",  END)

    # ── CAD 链 ───────────────────────────────────────────────────
    graph.add_conditional_edges(
        "cad_entry",
        route_cad_by_ext,
        {
            "parse_cad_step": "parse_cad_step",
            "error_handler":  "error_handler",
        },
    )
    graph.add_edge("parse_cad_step",      "cad_to_triples_node")
    graph.add_edge("cad_to_triples_node", END)

    # ── 手册链（deepdoc 精细化全链）─────────────────────────────
    graph.add_edge("manual_entry",     "analyze_pdf_type")
    graph.add_edge("analyze_pdf_type", "deepdoc_parse_pdf")
    graph.add_edge("deepdoc_parse_pdf", "vision_layout_agent")
    graph.add_edge("vision_layout_agent", "extract_structure")
    graph.add_edge("extract_structure", "build_cross_refs")
    graph.add_edge("build_cross_refs",  "semantic_chunk")
    graph.add_edge("semantic_chunk",    "extract_figures")
    graph.add_conditional_edges(
        "extract_figures",
        route_after_extract_figures,
        {
            "generate_tech_captions": "generate_tech_captions",
            "encode_text_vectors":    "encode_text_vectors",
        },
    )
    graph.add_edge("generate_tech_captions",     "extract_flowchart_structure")
    graph.add_edge("extract_flowchart_structure","extract_visual_kg")
    graph.add_edge("extract_visual_kg",          "encode_text_vectors")
    graph.add_conditional_edges(
        "encode_text_vectors",
        route_after_encode_text,
        {
            "encode_image_vectors": "encode_image_vectors",
            "upsert_qdrant":        "upsert_qdrant",
        },
    )
    graph.add_edge("encode_image_vectors",         "upsert_qdrant")
    graph.add_edge("upsert_qdrant",                "extract_kg_triples_manual")
    graph.add_edge("extract_kg_triples_manual",    END)

    # ── Merge 链 ─────────────────────────────────────────────────
    graph.add_edge("merge_entry",                 "merge_multi_source_triples")
    graph.add_edge("merge_multi_source_triples",  "align_entities_multi_source")
    graph.add_edge("align_entities_multi_source", "verify_kg_entities")
    graph.add_edge("verify_kg_entities",          "validate_kg_dag")
    graph.add_edge("validate_kg_dag",             "write_kg_neo4j_unified")
    graph.add_edge("write_kg_neo4j_unified",      END)

    graph.add_edge("error_handler", END)

    return graph.compile()


def _noop(state: dict) -> dict:
    """空节点，仅用于路由分发。"""
    return {}
