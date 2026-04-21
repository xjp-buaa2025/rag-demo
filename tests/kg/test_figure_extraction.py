# tests/kg/test_figure_extraction.py
import json
import pandas as pd
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from backend.routers.kg_stages import _bom_df_to_entities_and_triples


def test_entities_include_item_callout():
    """BOM 实体必须携带 item_callout 字段，来自 fig_item 列"""
    records = [
        {"part_id": "3034344", "part_name": "COMPRESSOR ROTOR", "nomenclature": "COMPRESSOR ROTOR",
         "fig_item": "-1", "qty": 1, "category": "Assembly", "parent_id": "", "material": "", "unit": "件"},
        {"part_id": "MS9556-06", "part_name": "BOLT,MACHINE", "nomenclature": ".BOLT,MACHINE",
         "fig_item": "10", "qty": 4, "category": "Standard", "parent_id": "", "material": "", "unit": "件"},
    ]
    df_json = pd.DataFrame(records).to_json(orient="records", force_ascii=False)
    entities, _ = _bom_df_to_entities_and_triples(df_json)

    callouts = {e["part_number"]: e.get("item_callout") for e in entities}
    assert callouts.get("3034344") == "-1", f"expected '-1', got {callouts.get('3034344')}"
    assert callouts.get("MS9556-06") == "10", f"expected '10', got {callouts.get('MS9556-06')}"


import tempfile, os


def _make_minimal_ipc_pdf(figure_number: int, tmp_path) -> str:
    """生成含有 'FIGURE N' 文本和一张嵌入图片的最小 PDF（用于测试）"""
    import fitz
    import io
    from PIL import Image as PILImage
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    page.insert_text((50, 100), f"FIGURE {figure_number}  COMPRESSOR ROTOR", fontsize=14)
    page.insert_text((50, 120), "COMPRESSOR ROTOR INSTALLATION", fontsize=10)
    img = PILImage.new("RGB", (400, 300), color=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    rect = fitz.Rect(50, 140, 450, 440)
    page.insert_image(rect, stream=buf.read())
    pdf_path = str(tmp_path / f"test_ipc_{figure_number}.pdf")
    doc.save(pdf_path)
    doc.close()
    return pdf_path


def test_extract_ipc_figures_finds_figure_page(tmp_path):
    """extract_ipc_figures 应检测到 FIGURE 1 页面，提取图片并返回元数据"""
    from backend.pipelines.nodes_figures import extract_ipc_figures

    pdf_path = _make_minimal_ipc_pdf(1, tmp_path)
    figures_dir = str(tmp_path / "kg_figures")

    results = extract_ipc_figures(pdf_path, figures_dir=figures_dir)

    assert len(results) == 1
    fig = results[0]
    assert fig["figure_number"] == 1
    assert fig["figure_id"] == "BOM_FIG_1"
    assert fig["source"] == "IPC"
    saved_path = os.path.join(figures_dir, os.path.basename(fig["image_path"]))
    assert os.path.exists(saved_path), f"图片文件不存在: {saved_path}"
