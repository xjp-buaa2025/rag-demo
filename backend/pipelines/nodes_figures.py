"""backend/pipelines/nodes_figures.py — 爆炸图提取与 Neo4j 写入"""
import os
import re

import fitz  # PyMuPDF

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_DEFAULT_FIGURES_DIR = os.path.join(_ROOT, "storage", "images", "kg_figures")

_IPC_FIG_PATTERN = re.compile(r'FIGURE\s+(\d+)', re.IGNORECASE)
_MANUAL_FIG_PATTERN = re.compile(r'Figure\s+(\d+)', re.IGNORECASE)
_ATA_PATTERN = re.compile(r'\b(\d{2}-\d{2}-\d{2})\b')
_MIN_IMAGE_DIM = 200  # 爆炸图最小边长（过滤小图标）


def extract_ipc_figures(pdf_path: str, figures_dir: str = _DEFAULT_FIGURES_DIR) -> list:
    """
    扫描 IPC BOM PDF，找到含 'FIGURE N' 文本的页面，提取最大图片。
    返回 list[dict]：每项含 figure_number, figure_id, image_path(相对路径), title, page_number, source
    """
    os.makedirs(figures_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    results = []

    for page_num, page in enumerate(doc, 1):
        text = page.get_text()
        fig_match = _IPC_FIG_PATTERN.search(text)
        if not fig_match:
            continue

        images = page.get_images(full=True)
        best_xref, best_size = _pick_largest_image(images)
        if best_xref is None:
            continue

        figure_number = int(fig_match.group(1))
        base_image = doc.extract_image(best_xref)
        ext = base_image.get("ext", "png")
        filename = f"bom_fig_{figure_number}.{ext}"
        with open(os.path.join(figures_dir, filename), "wb") as f:
            f.write(base_image["image"])

        title = _extract_title_after_pattern(text, _IPC_FIG_PATTERN)

        results.append({
            "figure_number": figure_number,
            "figure_id":     f"BOM_FIG_{figure_number}",
            "image_path":    f"kg_figures/{filename}",
            "title":         title,
            "page_number":   page_num,
            "source":        "IPC",
            "ata_chapter":   None,
        })

    doc.close()
    return results


def _pick_largest_image(images: list):
    """从 fitz page.get_images() 列表中选出面积最大且超过最小尺寸的图片 xref。"""
    best_xref, best_size = None, 0
    for img_info in images:
        xref = img_info[0]
        w, h = img_info[2], img_info[3]
        if w > _MIN_IMAGE_DIM and h > _MIN_IMAGE_DIM and w * h > best_size:
            best_size = w * h
            best_xref = xref
    return best_xref, best_size


def _extract_title_after_pattern(text: str, pattern) -> str:
    """提取匹配行之后第一个非空行作为标题。"""
    lines = [l.strip() for l in text.split('\n')]
    for i, line in enumerate(lines):
        if pattern.search(line) and i + 1 < len(lines):
            candidate = lines[i + 1]
            if candidate and not pattern.search(candidate):
                return candidate
    return ""


def _extract_title_before_pattern(text: str, pattern) -> str:
    """提取匹配行之前最后一个非空行作为标题（维修手册：标题在 Figure NNN 上方）。"""
    lines = [l.strip() for l in text.split('\n')]
    for i, line in enumerate(lines):
        if pattern.search(line) and i > 0:
            for j in range(i - 1, -1, -1):
                if lines[j] and not pattern.search(lines[j]):
                    return lines[j]
    return ""
