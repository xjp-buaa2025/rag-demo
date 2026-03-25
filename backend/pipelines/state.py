"""
backend/pipelines/state.py — LangGraph 管道状态定义

PipelineState 是两条管道（RAG / BOM）共享的统一状态类型。
使用 Annotated[list, add] 让 log_messages 支持跨节点自动追加。
"""

from __future__ import annotations

from operator import add
from typing import Annotated, List, Literal, Optional, TypedDict


class PipelineState(TypedDict, total=False):
    """LangGraph 管道的统一状态，贯穿所有节点。"""

    # === 输入 ===
    file_path: str                      # 源文件绝对路径
    file_ext: str                       # 扩展名（不含点）：pdf / docx / md / txt / xlsx / csv
    pipeline_mode: Literal["rag", "bom"]
    clear_first: bool

    # === RAG 中间产物 ===
    markdown_text: str                  # PDF 转出的 Markdown（也可直接读入 MD 文件）
    text_chunks: list[dict]             # 切分后的文本块 [{text, page, source}]
    image_records: list[dict]           # PDF 提取的图片 [{image_path, page, context_text}]
    captions: list[dict]                # 图片描述 [{image_path, caption}]
    points: list[dict]                  # Qdrant PointStruct 序列化

    # === BOM 中间产物 ===
    tables_markdown: str                # PDF/DOCX 提取的表格（Markdown 格式）
    bom_records: list[dict]             # LLM 解析后的 BOM JSON 记录
    bom_dataframe_json: str             # DataFrame JSON 序列化（也可直接从 CSV/Excel 读入）

    # === PDF 精细化处理（deepdoc 路径）===
    pdf_type: Literal["text", "scanned", "mixed"]
    # [{page, type: "text"|"title"|"figure"|"table"|..., text, x0, x1, top, bottom,
    #   positions, image_path}]
    layout_regions: list[dict]
    # [{ata_code, title, level, page_start, page_end}]
    section_tree: list[dict]
    # [{source_page, source_text, ref_type, ref_id, target_page}]
    cross_refs: list[dict]
    # [{text, chunk_type, page, source, ata_section, section_title, section_hierarchy,
    #   figure_refs, table_refs, has_warning, has_caution}]
    manual_chunks: list[dict]
    # [{figure_id, image_path, page, ata_section, caption_text,
    #   referencing_chunks, context_text}]
    figure_records: list[dict]

    # === 进度追踪 ===
    log_messages: Annotated[list[str], add]   # 各节点追加日志，reducer 自动合并

    # === 状态标记 ===
    current_node: str
    error: Optional[str]
    stats: dict
