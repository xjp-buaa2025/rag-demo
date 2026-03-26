"""
backend/pipelines/deepdoc_wrapper.py — deepdoc AI 解析引擎封装层

封装 RAGFlow deepdoc 的完整 PDF 解析流程：
  - OCR（双轨：pdfplumber 文字优先 + OCR 兜底）
  - LayoutRecognizer（YOLOv10 ONNX，11类区域检测）
  - TableStructureRecognizer（ONNX，表格行列识别→HTML）
  - 文本合并 + 表图裁剪

对外提供 DeepDocEngine 单例类，通过 parse_pdf() 方法返回结构化结果。

大PDF自动分批：超过 CHUNK_SIZE 页时，用 fitz 拆分为临时小PDF分批调用 deepdoc。
文本空洞检测：deepdoc 返回的 boxes 若文本为空，用 fitz 按页回填文本。

注意：首次初始化会从 HuggingFace 下载 ONNX 模型到 rag/res/deepdoc/。
"""

import logging
import os
import sys
import tempfile
from math import ceil

logger = logging.getLogger(__name__)

# 大 PDF 分批阈值：超过此页数则拆分为多个临时 PDF 分批处理
# 50页/批：每批 pdfplumber 渲染约 680MB，避免 200页/批的 2.7GB OOM 问题
CHUNK_SIZE = 50

# 确保 deepdoc 的 shim 层在 sys.path 中
_DOC_PROCESSING = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "document_processing"
)
if _DOC_PROCESSING not in sys.path:
    sys.path.insert(0, _DOC_PROCESSING)


class DeepDocEngine:
    """
    封装 RAGFlowPdfParser，提供面向 LangGraph 节点的干净接口。

    使用 parse_into_bboxes() 方法（比 __call__() 更适合结构化分析）：
    - 返回包含 layout_type 标注的 bbox 列表
    - 每个 bbox 含 text, image(PIL), positions, layout_type
    - 表格和图形以结构化方式嵌入到 self.boxes 中

    线程安全：单个实例可被多个请求复用（pdfplumber 内部已加锁）。
    """

    def __init__(self):
        logger.info("正在初始化 DeepDocEngine（首次运行将下载 ONNX 模型）…")
        from deepdoc.parser.pdf_parser import RAGFlowPdfParser
        self._parser = RAGFlowPdfParser()
        logger.info("DeepDocEngine 初始化完成")

    def parse_pdf(self, file_path: str, progress_callback=None,
                  zoomin: int = 3) -> dict:
        """
        完整解析 PDF 文件，返回结构化结果字典。

        大PDF（> CHUNK_SIZE 页）自动拆分为多批处理，避免 deepdoc 的
        __images__ 默认 page_to=299 限制和内存溢出。

        每批处理后做文本空洞检测：若 >50% 的 text boxes 文本为空，
        用 fitz 按页回填文本（保留 deepdoc 的布局分析结果）。

        Args:
            file_path: PDF 文件绝对路径
            progress_callback: 可选进度回调 fn(progress: float, msg: str)

        Returns:
            dict with keys:
              "boxes"   — list[dict] 统一的 bbox 列表
              "total_pages": int
              "is_english": bool
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF 文件不存在: {file_path}")

        import fitz
        with fitz.open(file_path) as doc:
            total_pages = len(doc)

        logger.info(f"开始解析 PDF: {os.path.basename(file_path)}（{total_pages} 页）")

        if total_pages <= CHUNK_SIZE:
            return self._parse_single(file_path, total_pages, progress_callback,
                                      zoomin=zoomin)

        # ── 大 PDF：分批处理 ──────────────────────────────────────
        num_chunks = ceil(total_pages / CHUNK_SIZE)
        logger.info(f"大 PDF（{total_pages} 页），分 {num_chunks} 批处理（每批 {CHUNK_SIZE} 页）")

        all_boxes = []

        with fitz.open(file_path) as src_doc:
            for chunk_idx in range(num_chunks):
                start = chunk_idx * CHUNK_SIZE
                end = min(start + CHUNK_SIZE, total_pages)
                logger.info(f"  批次 {chunk_idx+1}/{num_chunks}：第 {start+1}-{end} 页")

                # 用 fitz 提取子 PDF 到临时文件
                chunk_doc = fitz.open()
                chunk_doc.insert_pdf(src_doc, from_page=start, to_page=end - 1)
                tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
                chunk_path = tmp.name
                tmp.close()
                try:
                    chunk_doc.save(chunk_path)
                    chunk_doc.close()

                    # 计算该批次在整体进度中的比例
                    base_progress = chunk_idx / num_chunks
                    scale = 1.0 / num_chunks

                    def _cb(progress, msg="", _base=base_progress, _scale=scale,
                            _cidx=chunk_idx):
                        overall = _base + progress * _scale
                        logger.debug(f"  [{overall*100:.0f}%] {msg}")
                        if progress_callback:
                            progress_callback(overall, f"[批次{_cidx+1}] {msg}")

                    chunk_boxes = self._parse_with_retry(
                        chunk_path, callback=_cb, zoomin=zoomin
                    )

                    # 修正 page_number 为全局页码（deepdoc 返回的是批次内 1-based）
                    for box in chunk_boxes:
                        box["page_number"] = box.get("page_number", 1) + start
                        box["positions"] = [
                            [p[0] + start, *p[1:]]
                            for p in box.get("positions", [])
                        ]

                    # 空洞检测 + fitz 补文本
                    _fill_empty_text(chunk_path, chunk_boxes, page_offset=start)

                    all_boxes.extend(chunk_boxes)
                    logger.info(
                        f"  批次 {chunk_idx+1} 完成：{len(chunk_boxes)} 个块，"
                        f"有文本 {sum(1 for b in chunk_boxes if b.get('text','').strip())} 个"
                    )

                    # ── 批次完成结构化汇报（走 progress_callback → 实时推送到前端）──
                    if progress_callback:
                        text_c = sum(1 for b in chunk_boxes
                                     if b.get("layout_type") not in ("figure",))
                        fig_c  = sum(1 for b in chunk_boxes
                                     if b.get("layout_type") == "figure")
                        tbl_c  = sum(1 for b in chunk_boxes
                                     if b.get("layout_type") == "table")
                        done_ratio = (chunk_idx + 1) / num_chunks
                        progress_callback(
                            done_ratio,
                            f"[批次 {chunk_idx+1}/{num_chunks} 完成] "
                            f"第 {start+1}-{end} 页 | "
                            f"{len(chunk_boxes)} 区域（文本 {text_c}，表格 {tbl_c}，图形 {fig_c}）"
                        )
                finally:
                    try:
                        os.unlink(chunk_path)
                    except OSError:
                        pass

        logger.info(f"全部批次完成：共 {len(all_boxes)} 个块，{total_pages} 页")
        return {
            "boxes": all_boxes,
            "total_pages": total_pages,
            "is_english": False,
        }

    def _parse_with_retry(self, file_path: str, callback=None,
                          zoomin: int = 3, max_zoomin: int = 9) -> list:
        """
        调用 parse_into_bboxes 并在结果为空时自动重试更高 zoomin。

        补偿上游 pdf_parser.py 第 1518 行的重试逻辑 bug：
        原始代码检查 len(self.boxes)==0，但 boxes 是 list-of-lists，
        多页 PDF 即使全空也 len>0，导致重试永不触发。
        """
        boxes = self._parser.parse_into_bboxes(
            file_path, callback=callback, zoomin=zoomin
        )
        if not boxes and zoomin < max_zoomin:
            retry_zoomin = min(zoomin * 2, max_zoomin)
            logger.warning(
                f"deepdoc 返回 0 boxes (zoomin={zoomin})，"
                f"重试 zoomin={retry_zoomin}"
            )
            boxes = self._parser.parse_into_bboxes(
                file_path, callback=callback, zoomin=retry_zoomin
            )
        return boxes

    def _parse_single(self, file_path: str, total_pages: int,
                      progress_callback=None, zoomin: int = 3) -> dict:
        """单次 deepdoc 解析（小 PDF，<= CHUNK_SIZE 页）。"""
        def _cb(progress, msg=""):
            logger.debug(f"  [{progress*100:.0f}%] {msg}")
            if progress_callback:
                progress_callback(progress, msg)

        boxes = self._parse_with_retry(file_path, callback=_cb, zoomin=zoomin)
        total_pages = getattr(self._parser, "total_page", 0) or total_pages
        is_english = getattr(self._parser, "is_english", False)

        # 空洞检测 + fitz 补文本
        _fill_empty_text(file_path, boxes, page_offset=0)

        logger.info(
            f"解析完成: {len(boxes)} 个块，共 {total_pages} 页 | "
            f"有文本 {sum(1 for b in boxes if b.get('text','').strip())} 个"
        )
        return {
            "boxes": boxes,
            "total_pages": total_pages,
            "is_english": bool(is_english),
        }

    def analyze_pdf_type(self, file_path: str, sample_pages: int = 10) -> str:
        """
        快速采样判断 PDF 类型（文本型/扫描件/混合），不做完整解析。

        通过 pdfplumber 检查前 N 页的可提取文字数量来判断。

        Returns:
            "text"    — 85%+ 的页面有可提取文字
            "scanned" — 15%- 的页面有可提取文字
            "mixed"   — 介于两者之间
        """
        import pdfplumber

        text_pages = 0
        checked = 0

        try:
            with pdfplumber.open(file_path) as pdf:
                total = len(pdf.pages)
                pages_to_check = min(sample_pages, total)
                for i in range(pages_to_check):
                    page = pdf.pages[i]
                    chars = page.chars
                    if len(chars) > 20:  # 有实质性文字
                        text_pages += 1
                    checked += 1
        except Exception as e:
            logger.warning(f"analyze_pdf_type 失败: {e}，默认 text")
            return "text"

        if checked == 0:
            return "text"

        ratio = text_pages / checked
        if ratio >= 0.85:
            return "text"
        elif ratio <= 0.15:
            return "scanned"
        else:
            return "mixed"


def _fill_empty_text(pdf_path: str, boxes: list, page_offset: int = 0):
    """
    检测 deepdoc boxes 的文本空洞率，若过高则用 fitz 按页回填文本。

    保留 deepdoc 的布局分析结果（坐标、layout_type），仅补充空缺的文本。
    """
    text_boxes = [b for b in boxes if b.get("layout_type") not in ("figure",)]
    if not text_boxes:
        return

    empty_count = sum(1 for b in text_boxes if not b.get("text", "").strip())
    empty_ratio = empty_count / len(text_boxes)

    if empty_ratio <= 0.5:
        return

    logger.warning(
        f"文本空洞率 {empty_ratio:.0%}（{empty_count}/{len(text_boxes)}），"
        f"启用 fitz 文本回填"
    )

    # 按页分组空文本 boxes
    empty_by_page = {}
    for box in boxes:
        if box.get("layout_type") in ("figure",):
            continue
        if not box.get("text", "").strip():
            pg = box["page_number"]
            empty_by_page.setdefault(pg, []).append(box)

    if not empty_by_page:
        return

    import fitz
    filled = 0
    try:
        with fitz.open(pdf_path) as doc:
            for local_page in range(len(doc)):
                global_page = local_page + 1 + page_offset
                if global_page not in empty_by_page:
                    continue
                page = doc[local_page]
                page_text = (page.get_text("text") or "").strip()
                if not page_text:
                    continue

                page_boxes = empty_by_page[global_page]
                if len(page_boxes) == 1:
                    page_boxes[0]["text"] = page_text
                    filled += 1
                else:
                    # 多个空 box：按段落分配
                    paragraphs = [p.strip() for p in page_text.split("\n\n") if p.strip()]
                    if not paragraphs:
                        paragraphs = [page_text]
                    sorted_boxes = sorted(page_boxes, key=lambda b: b.get("top", 0))
                    for i, box in enumerate(sorted_boxes):
                        if i < len(paragraphs):
                            box["text"] = paragraphs[i]
                        else:
                            # 剩余 boxes：合并剩余段落
                            box["text"] = "\n".join(paragraphs[i:])
                            break
                    filled += sum(1 for b in sorted_boxes if b.get("text", "").strip())
    except Exception as e:
        logger.error(f"fitz 文本回填失败: {e}")
        return

    logger.info(f"fitz 文本回填完成：{filled} 个 box 已补充文本")
