"""
backend/pipelines/routes.py — 条件路由函数

根据 pipeline_mode + file_ext 决定从哪个节点开始执行。
支持灵活入口：PDF 走完整流程，MD/CSV/Excel 从中间节点切入。
"""


def route_entry(state: dict) -> str:
    """detect_input 之后的主路由：分流到 RAG 或 BOM 分支。"""
    if state.get("error"):
        return "error_handler"
    mode = state["pipeline_mode"]
    if mode == "rag":
        return "rag_entry"
    else:
        return "bom_entry"


def route_rag_by_ext(state: dict) -> str:
    """RAG 分支：根据文件类型选择入口节点。
    PDF -> analyze_pdf_type（deepdoc 精细化路径）
    其他 -> chunk_text（直接从文本切块开始）"""
    ext = state.get("file_ext", "")
    if ext == "pdf":
        return "analyze_pdf_type"
    return "chunk_text"


def route_bom_by_ext(state: dict) -> str:
    """BOM 分支：根据文件类型选择入口节点。
    xlsx/xls/csv -> load_table（直接读表）
    pdf/docx -> extract_tables（先提取表格再 LLM 转换）"""
    ext = state.get("file_ext", "")
    if ext in ("xlsx", "xls", "csv"):
        return "load_table"
    return "extract_tables"


def route_after_pdf_to_md(state: dict) -> str:
    """pdf_to_md 之后：如果有图片记录则先处理图片，否则直接切块。"""
    if state.get("image_records"):
        return "generate_captions"
    return "chunk_text"


def route_after_captions(state: dict) -> str:
    """generate_captions 之后：进入文本切块。"""
    return "chunk_text"


def route_after_encode_text(state: dict) -> str:
    """encode_text_vectors 之后：如果有图片记录则编码图片向量，否则直接 upsert。"""
    if state.get("captions") or state.get("figure_records"):
        return "encode_image_vectors"
    return "upsert_qdrant"


def route_after_semantic_chunk(state: dict) -> str:
    """semantic_chunk 之后：进入图形提取。"""
    return "extract_figures"


def route_after_extract_figures(state: dict) -> str:
    """extract_figures 之后：有图形记录则生成描述，否则直接编码文本。"""
    if state.get("figure_records"):
        return "generate_tech_captions"
    return "encode_text_vectors"
