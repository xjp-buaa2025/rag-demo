"""
backend/pipelines/nodes_manual.py — 技术手册精细化解析节点

节点链（PDF 路径）：
  analyze_pdf_type -> deepdoc_parse_pdf -> extract_structure
  -> build_cross_refs -> semantic_chunk -> extract_figures
  -> generate_tech_captions -> [encode_text_vectors / encode_image_vectors]

所有节点通过 make_manual_nodes(app_state, image_dir) 工厂函数创建，
闭包绑定 AppState 和 DeepDocEngine。
"""

import logging
import os
import re
import threading
import uuid
from typing import Any

logger = logging.getLogger(__name__)

# ATA 章节编号正则（如 72-10-00、72-10-00-200）
_ATA_RE = re.compile(r"\b(\d{2})-(\d{2})-(\d{2})(?:-(\d{3}))?\b")
# 步骤编号正则（如 1., (a), A., Step 1:）
_STEP_RE = re.compile(r"^(?:\d+\.|[a-zA-Z]\.|[a-zA-Z]\)|\(\d+\)|Step\s+\d+[:\.])", re.IGNORECASE)
# 交叉引用正则
_FIG_REF_RE = re.compile(r"(?:see|refer\s+to|figure|fig\.?)\s+([A-Z]?\d+[-–]\d+)", re.IGNORECASE)
_TBL_REF_RE = re.compile(r"(?:see\s+)?[Tt]able\s+([A-Z]?\d+[-–]\d+|\d+)", re.IGNORECASE)
# WARNING/CAUTION/NOTE 关键字
_ALERT_RE = re.compile(r"^(WARNING|CAUTION|NOTE)\b", re.IGNORECASE)


def _guess_region_type(text: str) -> str:
    """启发式判断 fitz block 的区域类型（title 或 text）。"""
    stripped = text.strip()
    if not stripped or len(stripped) > 100:
        return "text"
    # ATA 编号标题
    if _ATA_RE.search(stripped) and len(stripped.split("\n")) == 1:
        return "title"
    # 全大写短文本（常见英文标题格式）
    if stripped == stripped.upper() and len(stripped) > 3 and stripped[0].isalpha():
        return "title"
    return "text"


def _is_flowchart(caption_text: str, context_text: str) -> bool:
    """启发式检测是否为流程图（针对航空维护手册的故障排查图）。"""
    fc_keywords = [
        "troubleshoot", "fault isolation", "fault tree",
        "flow chart", "flowchart", "flow diagram",
        "from sheet", "to sheet", "isolation chart",
    ]
    combined = (caption_text + " " + context_text).lower()
    return any(kw in combined for kw in fc_keywords)


def _parse_flowchart_json(raw: str) -> dict:
    """从 LLM 原始输出中提取流程图 JSON（含多重容错）。"""
    import json as _json
    if not raw:
        return {}
    # 1. 直接解析
    try:
        return _json.loads(raw.strip())
    except Exception:
        pass
    # 2. 提取 ```json...``` 代码块
    m = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw)
    if m:
        try:
            return _json.loads(m.group(1).strip())
        except Exception:
            pass
    # 3. 提取第一个 { ... } 块（JSONDecoder 贪心匹配）
    m = re.search(r"\{", raw)
    if m:
        try:
            import json as _json2
            obj, _ = _json2.JSONDecoder().raw_decode(raw, m.start())
            return obj
        except Exception:
            pass
    return {}


def _expand_flowchart_to_chunks(fc: dict, rec: dict) -> list:
    """每个流程图节点 → 一个 chunk，包含 YES/NO 分支信息。"""
    figure_title = fc.get("figure_title", rec.get("caption_text", "Flowchart"))
    nodes = {n["id"]: n for n in fc.get("nodes", [])}
    edges = fc.get("edges", [])
    figure_id = rec.get("figure_id", "")
    page = rec.get("page", 0)
    source = rec.get("source", "")
    ata_section = rec.get("ata_section", "")

    # 建立出边映射
    out_edges: dict = {}
    for e in edges:
        out_edges.setdefault(e["from"], []).append(e)

    chunks = []
    for node_id, node in nodes.items():
        node_text = node.get("text", "").strip()
        if not node_text or node_text == "[ILLEGIBLE]":
            continue

        outs = out_edges.get(node_id, [])
        yes_targets = [nodes[e["to"]]["text"] for e in outs
                       if e.get("condition") == "YES" and e["to"] in nodes]
        no_targets = [nodes[e["to"]]["text"] for e in outs
                      if e.get("condition") == "NO" and e["to"] in nodes]
        other_targets = [nodes[e["to"]]["text"] for e in outs
                         if e.get("condition") not in ("YES", "NO") and e["to"] in nodes]

        lines = [f"[FLOWCHART NODE] {figure_title}", f"操作/问题: {node_text}"]
        if yes_targets:
            lines.append("YES → " + " / ".join(yes_targets))
        if no_targets:
            lines.append("NO → " + " / ".join(no_targets))
        if other_targets:
            lines.append("下一步 → " + " / ".join(other_targets))

        chunks.append({
            "text": "\n".join(lines),
            "chunk_type": "flowchart_node",
            "page": page,
            "source": source,
            "ata_section": ata_section,
            "figure_id": figure_id,
            "node_id": node_id,
            "node_type": node.get("type", "action"),
            "has_warning": False,
            "has_caution": False,
        })
    return chunks


def _build_path_summaries(fc: dict, rec: dict) -> list:
    """
    从每个出口节点反向 BFS 追溯主路径（每个 exit 一条 chunk），
    受控生成，不枚举全部路径，避免路径爆炸。
    """
    from collections import deque

    figure_title = fc.get("figure_title", rec.get("caption_text", "Flowchart"))
    nodes = {n["id"]: n for n in fc.get("nodes", [])}
    edges = fc.get("edges", [])
    entry = fc.get("entry_node", "")
    figure_id = rec.get("figure_id", "")
    page = rec.get("page", 0)
    source = rec.get("source", "")
    ata_section = rec.get("ata_section", "")

    if not nodes or not entry or entry not in nodes:
        return []

    # 建立出边映射
    out_edges: dict = {}
    for e in edges:
        out_edges.setdefault(e["from"], []).append(e)

    # 出口节点：无出边
    exit_nodes = [nid for nid in nodes if not out_edges.get(nid) and nid != entry]

    MAX_PATH_LEN = 15
    chunks = []

    for exit_id in exit_nodes[:5]:  # 最多 5 条路径
        queue: deque = deque([(entry, [(entry, None)])])
        visited: set = set()
        found_path = None

        while queue:
            curr, path = queue.popleft()
            if curr in visited:
                continue
            visited.add(curr)
            if curr == exit_id:
                found_path = path
                break
            if len(path) >= MAX_PATH_LEN:
                continue
            for e in out_edges.get(curr, []):
                nxt = e["to"]
                if nxt not in visited and nxt in nodes:
                    queue.append((nxt, path + [(nxt, e.get("condition"))]))

        if not found_path:
            continue

        parts = []
        for nid, condition in found_path:
            n_text = nodes[nid].get("text", nid).strip()
            if not n_text or n_text == "[ILLEGIBLE]":
                continue
            parts.append(f"{condition}: {n_text}" if condition else n_text)

        if len(parts) < 2:
            continue

        text = f"[FLOWCHART PATH] {figure_title}\n排查路径: {' → '.join(parts)}"
        chunks.append({
            "text": text,
            "chunk_type": "flowchart_path",
            "page": page,
            "source": source,
            "ata_section": ata_section,
            "figure_id": figure_id,
            "has_warning": False,
            "has_caution": False,
        })

    return chunks


def make_manual_nodes(app_state: Any, image_dir: str) -> dict:
    """
    工厂函数：返回 PDF 精细化处理的所有节点字典。

    Args:
        app_state: AppState 实例（含 deepdoc_engine, minimax_client 等）
        image_dir: 图片保存目录（storage/images/）
    """

    # ------------------------------------------------------------------
    # 节点 1：analyze_pdf_type
    # ------------------------------------------------------------------

    def analyze_pdf_type(state: dict) -> dict:
        """
        快速采样判断 PDF 是文本型/扫描件/混合，不做完整解析。
        输出 pdf_type 供日志和下游节点参考，不影响路由（deepdoc 均可处理）。
        """
        file_path = state["file_path"]
        logs = ["[analyze_pdf_type] 采样检测 PDF 类型…"]

        if not app_state.deepdoc_engine:
            logs.append("[analyze_pdf_type] deepdoc_engine 未初始化，跳过检测")
            return {"pdf_type": "text", "log_messages": logs,
                    "current_node": "analyze_pdf_type"}

        try:
            pdf_type = app_state.deepdoc_engine.analyze_pdf_type(file_path)
        except Exception as e:
            pdf_type = "text"
            logs.append(f"[analyze_pdf_type] 检测失败 ({e})，默认 text")

        logs.append(f"[analyze_pdf_type] PDF 类型: {pdf_type}")

        # 提前报告 PDF 规模，让用户知道后续解析可能耗时
        try:
            import fitz as _fitz
            from math import ceil as _ceil
            from backend.pipelines.deepdoc_wrapper import CHUNK_SIZE as _CS
            with _fitz.open(file_path) as _doc:
                _total_pages = len(_doc)
            _batches = _ceil(_total_pages / _CS)
            if _total_pages > _CS:
                logs.append(
                    f"[analyze_pdf_type] ⚠ 大型文档：{_total_pages} 页，"
                    f"将分 {_batches} 批解析（每批 {_CS} 页）。"
                    f"下一步 deepdoc 解析耗时较长，前端日志暂停更新属正常现象，请勿关闭页面。"
                )
            else:
                logs.append(f"[analyze_pdf_type] 文档共 {_total_pages} 页")
        except Exception:
            pass

        return {"pdf_type": pdf_type, "log_messages": logs,
                "current_node": "analyze_pdf_type"}

    # ------------------------------------------------------------------
    # 节点 2：deepdoc_parse_pdf
    # ------------------------------------------------------------------

    def deepdoc_parse_pdf(state: dict) -> dict:
        """
        调用 DeepDocEngine.parse_pdf()，执行完整的 deepdoc 解析流程：
          - OCR（pdfplumber + ONNX OCR 兜底）
          - LayoutRecognizer（11类区域标注）
          - TableStructureRecognizer（表格行列结构）
          - 文本合并 + 表图裁剪

        输出 layout_regions：统一的区域列表（含 layout_type、text、image）。
        """
        file_path = state["file_path"]
        pdf_type = state.get("pdf_type", "text")
        logs = [f"[deepdoc_parse] 开始解析: {os.path.basename(file_path)}"]

        # 根据 PDF 类型选择渲染分辨率（zoomin × 72 = DPI）
        # text 用 zoomin=2（144DPI）：pdfplumber 已能提取字符，低 DPI 节省 ~40% 内存
        _ZOOMIN_MAP = {"scanned": 6, "mixed": 4, "text": 2}
        zoomin = _ZOOMIN_MAP.get(pdf_type, 2)
        logs.append(f"[deepdoc_parse] pdf_type={pdf_type}, zoomin={zoomin} (DPI={72*zoomin})")

        # ── 预报批次信息，让前端感知进度 ──────────────────────────
        try:
            import fitz as _fitz
            from math import ceil as _ceil
            from backend.pipelines.deepdoc_wrapper import CHUNK_SIZE as _CS
            with _fitz.open(file_path) as _doc:
                _total = len(_doc)
            _batches = _ceil(_total / _CS)
            if _total > _CS:
                logs.append(
                    f"[deepdoc_parse] 大型PDF：{_total} 页，将分 {_batches} 批处理"
                    f"（每批 {_CS} 页）。大型文档耗时较长，请耐心等待…"
                )
        except Exception:
            pass

        if not app_state.deepdoc_engine:
            return {"error": "deepdoc_engine 未初始化，无法解析 PDF",
                    "log_messages": logs, "current_node": "deepdoc_parse_pdf"}

        # 侧信道：从 app_state 读取进度队列（由 ingest_pipeline 路由注入）
        _q = getattr(app_state, '_ingest_progress_q', None)

        # 心跳线程：每60s向队列注入一次"处理中"消息，防止 SSE 因静默期（如 TSR）误判超时
        _hb_stop = threading.Event()

        def _heartbeat():
            waited = 0
            while not _hb_stop.wait(60):
                waited += 1
                if _q is not None:
                    try:
                        _q.put_nowait(
                            ("log", f"[deepdoc_parse] ⏳ 解析进行中，请耐心等待…（已等待约 {waited} 分钟）")
                        )
                    except Exception:
                        pass

        _hb_thread = threading.Thread(target=_heartbeat, daemon=True, name="deepdoc-heartbeat")
        _hb_thread.start()

        try:
            def _progress(p, msg=""):
                pct = int(p * 100)
                line = f"  [{pct}%] {msg}"
                logs.append(line)
                # 实时推送到 SSE：通过队列越过 LangGraph 节点边界
                if _q is not None:
                    try:
                        _q.put_nowait(("log", f"[deepdoc_parse] {line}"))
                    except Exception:
                        pass  # 队列满不影响解析

            result = app_state.deepdoc_engine.parse_pdf(
                file_path, progress_callback=_progress, zoomin=zoomin
            )
        except Exception as e:
            logger.exception("deepdoc parse_pdf 异常")
            logs.append(f"[deepdoc_parse] ⚠ deepdoc 解析异常: {e}")
            result = {"boxes": [], "total_pages": 0, "is_english": False}
        finally:
            _hb_stop.set()
            _hb_thread.join(timeout=2)

        # 将 deepdoc boxes 转换为 layout_regions（去掉不可序列化的 PIL.Image）
        # PIL.Image 另存为文件，path 存在 regions 中
        os.makedirs(image_dir, exist_ok=True)
        source = os.path.basename(file_path)
        doc_prefix = source.rsplit(".", 1)[0]

        layout_regions = []
        fig_idx = 0
        for box in result["boxes"]:
            region = {
                "page": box.get("page_number", 1),
                "type": box.get("layout_type", "text"),
                "text": box.get("text", ""),
                "x0": box.get("x0", 0),
                "x1": box.get("x1", 0),
                "top": box.get("top", 0),
                "bottom": box.get("bottom", 0),
                "positions": box.get("positions", []),
                "image_path": "",
            }
            # 图形区域：保存裁剪图到磁盘
            pil_img = box.get("image")
            if pil_img is not None and region["type"] == "figure":
                img_fname = f"{doc_prefix}_fig_{fig_idx:03d}_p{region['page']}.png"
                img_path = os.path.join(image_dir, img_fname)
                try:
                    pil_img.save(img_path)
                    region["image_path"] = img_path
                    fig_idx += 1
                except Exception as e:
                    logger.warning(f"保存图片失败: {e}")

            layout_regions.append(region)

        text_count = sum(1 for r in layout_regions if r["type"] not in ("figure",))
        fig_count = sum(1 for r in layout_regions if r["type"] == "figure")
        tbl_count = sum(1 for r in layout_regions if r["type"] == "table")
        logs.append(
            f"[deepdoc_parse] 完成：{len(layout_regions)} 个区域"
            f"（文本 {text_count}，表格 {tbl_count}，图形 {fig_count}）"
        )

        # 诊断日志：空文本区域检测
        non_empty_text = sum(
            1 for r in layout_regions
            if r["type"] not in ("figure",) and r["text"].strip()
        )
        total_chars = sum(len(r["text"]) for r in layout_regions)
        logs.append(
            f"[deepdoc_parse] 诊断：{non_empty_text}/{text_count} 个文本区域有内容，"
            f"总字符数 {total_chars}"
        )
        if text_count > 0 and non_empty_text == 0:
            logs.append(
                "[deepdoc_parse] ⚠ 所有文本区域为空！deepdoc 字符提取可能失败"
            )

        # 降级兜底：deepdoc 结果为空 或 文本空洞率过高 时，用 fitz block 提取
        text_regions = [r for r in layout_regions if r["type"] not in ("figure",)]
        non_empty = sum(1 for r in text_regions if r["text"].strip())
        empty_ratio = 1.0 - (non_empty / max(len(text_regions), 1))
        need_fallback = not layout_regions or (
            len(text_regions) > 0 and empty_ratio > 0.8
        )

        if need_fallback:
            reason = (
                "deepdoc 结果为空"
                if not layout_regions
                else f"文本空洞率过高（{empty_ratio:.0%}）"
            )
            logs.append(f"[deepdoc_parse] {reason}，切换到 fitz block 提取模式…")
            layout_regions = []  # 清空，完全用 fitz 重做
            try:
                import fitz
                fig_idx_fb = 0
                with fitz.open(file_path) as pdf:
                    for page_num in range(len(pdf)):
                        page = pdf[page_num]
                        blocks = page.get_text("dict", flags=11)["blocks"]
                        for block in blocks:
                            # 文本 block
                            if block["type"] == 0:
                                text = ""
                                for line in block["lines"]:
                                    for span in line["spans"]:
                                        text += span["text"]
                                    text += "\n"
                                text = text.strip()
                                if not text:
                                    continue
                                bbox = block["bbox"]
                                layout_regions.append({
                                    "page": page_num + 1,
                                    "type": _guess_region_type(text),
                                    "text": text,
                                    "x0": bbox[0], "x1": bbox[2],
                                    "top": bbox[1], "bottom": bbox[3],
                                    "positions": [],
                                    "image_path": "",
                                })
                            # 图片 block（type=1）：提取嵌入图片
                            elif block["type"] == 1:
                                try:
                                    bbox = block["bbox"]
                                    # 用高 DPI 渲染裁剪区域获取图片
                                    clip = fitz.Rect(bbox)
                                    mat = fitz.Matrix(2, 2)  # 144 DPI
                                    pix = page.get_pixmap(matrix=mat, clip=clip)
                                    if pix.width < 32 or pix.height < 32:
                                        continue
                                    img_fname = (
                                        f"{doc_prefix}_fig_{fig_idx_fb:03d}"
                                        f"_p{page_num+1}_fb.png"
                                    )
                                    img_path = os.path.join(image_dir, img_fname)
                                    pix.save(img_path)
                                    layout_regions.append({
                                        "page": page_num + 1,
                                        "type": "figure",
                                        "text": "",
                                        "x0": bbox[0], "x1": bbox[2],
                                        "top": bbox[1], "bottom": bbox[3],
                                        "positions": [],
                                        "image_path": img_path,
                                    })
                                    fig_idx_fb += 1
                                except Exception as _e:
                                    logger.debug(f"fitz 图片提取跳过: {_e}")

                text_fallback = sum(1 for r in layout_regions if r["type"] != "figure")
                fig_fallback = sum(1 for r in layout_regions if r["type"] == "figure")
                logs.append(
                    f"[deepdoc_parse] fitz block 提取完成："
                    f"{text_fallback} 文本区域，{fig_fallback} 图片区域"
                )
            except Exception as e:
                logs.append(f"[deepdoc_parse] fitz 提取失败: {e}")

        # ── Fallback B: OCR-only（扫描件专用） ──────────────────────
        if not layout_regions:
            logs.append(
                "[deepdoc_parse] fitz 也无文本，启用 OCR-only 降级…"
            )
            try:
                import fitz
                import numpy as np

                ocr_engine = app_state.deepdoc_engine._parser.ocr
                OCR_DPI = 300

                with fitz.open(file_path) as pdf:
                    total_pg = len(pdf)
                    for page_num in range(total_pg):
                        page = pdf[page_num]
                        pix = page.get_pixmap(dpi=OCR_DPI)
                        img_np = np.frombuffer(
                            pix.samples, dtype=np.uint8
                        ).reshape(pix.h, pix.w, pix.n)
                        if pix.n == 4:
                            img_np = img_np[:, :, :3]

                        ocr_result = ocr_engine(img_np)
                        # __call__ 返回 list[(box, (text, score))]
                        # 或 (None, None, time_dict) 当无检测结果时
                        if (
                            not ocr_result
                            or (isinstance(ocr_result, tuple)
                                and ocr_result[0] is None)
                        ):
                            continue

                        page_texts = [
                            text.strip()
                            for _box, (text, score) in ocr_result
                            if text and text.strip()
                        ]

                        if page_texts:
                            full_text = "\n".join(page_texts)
                            layout_regions.append({
                                "page": page_num + 1,
                                "type": "text",
                                "text": full_text,
                                "x0": 0, "x1": pix.w,
                                "top": 0, "bottom": pix.h,
                                "positions": [],
                                "image_path": "",
                            })

                        if page_num % 100 == 99:
                            logs.append(
                                f"  OCR 降级进度: {page_num+1}/{total_pg} 页"
                            )

                logs.append(
                    f"[deepdoc_parse] OCR-only 降级完成："
                    f"{len(layout_regions)} 个区域"
                )
            except Exception as e:
                logs.append(f"[deepdoc_parse] OCR 降级失败: {e}")
                logger.exception("OCR-only fallback failed")

        return {
            "layout_regions": layout_regions,
            "current_node": "deepdoc_parse_pdf",
            "log_messages": logs,
        }

    # ------------------------------------------------------------------
    # 节点 3：extract_structure
    # ------------------------------------------------------------------

    def extract_structure(state: dict) -> dict:
        """
        从 layout_regions 中 type='title' 的区域识别章节层级结构。

        支持：
          - ATA 编号（如 72-10-00，自动推断层级 1/2/3）
          - 通用标题（按文字格式推断：全大写=Level1，混合=Level2+）
        输出 section_tree：章节树列表。
        """
        layout_regions = state.get("layout_regions", [])
        logs = ["[extract_structure] 识别章节结构…"]

        section_tree = []
        current_sections = {}  # level -> section_dict

        for region in layout_regions:
            if region["type"] not in ("title",):
                continue

            text = region["text"].strip()
            if not text:
                continue

            page = region["page"]

            # 尝试匹配 ATA 编号
            ata_match = _ATA_RE.search(text)
            if ata_match:
                ch, sec, sub = ata_match.group(1), ata_match.group(2), ata_match.group(3)
                ata_code = f"{ch}-{sec}-{sub}"
                if sub != "00":
                    level = 3
                elif sec != "00":
                    level = 2
                else:
                    level = 1
            else:
                ata_code = ""
                # 全大写通常是主章节
                if text == text.upper() and len(text) > 3:
                    level = 1
                elif text[0].isupper() and len(text.split()) <= 6:
                    level = 2
                else:
                    level = 3

            section = {
                "ata_code": ata_code,
                "title": text,
                "level": level,
                "page_start": page,
                "page_end": page,  # 后续会更新
            }

            # 更新上级章节的 page_end
            for lv, sec_dict in list(current_sections.items()):
                if lv >= level:
                    sec_dict["page_end"] = page - 1
                    del current_sections[lv]

            current_sections[level] = section
            section_tree.append(section)

        logs.append(f"[extract_structure] 识别到 {len(section_tree)} 个章节")
        return {
            "section_tree": section_tree,
            "current_node": "extract_structure",
            "log_messages": logs,
        }

    # ------------------------------------------------------------------
    # 节点 4：build_cross_refs
    # ------------------------------------------------------------------

    def build_cross_refs(state: dict) -> dict:
        """
        从文本中匹配"See Figure X-Y"/"See Table X"等交叉引用，
        并从 layout_regions 中 figure caption 反向映射目标区域。

        输出 cross_refs：交叉引用列表。
        """
        layout_regions = state.get("layout_regions", [])
        logs = ["[build_cross_refs] 构建图文交叉引用…"]

        cross_refs = []
        # 建立 figure caption -> page 的映射
        figure_captions = {}
        for region in layout_regions:
            if region["type"] in ("figure caption", "figure"):
                txt = region["text"].strip()
                # 从 caption 中提取图号（如 Figure 4-12）
                m = re.search(r"[Ff]ig(?:ure)?\s*\.?\s*([A-Z]?\d+[-–]\d+|\d+)", txt)
                if m:
                    figure_captions[m.group(1).replace("–", "-")] = region["page"]

        for region in layout_regions:
            if region["type"] in ("figure", "table"):
                continue
            text = region["text"]
            page = region["page"]

            # 找图引用
            for m in _FIG_REF_RE.finditer(text):
                ref_id = m.group(1).replace("–", "-")
                cross_refs.append({
                    "source_page": page,
                    "source_text": m.group(0),
                    "ref_type": "figure",
                    "ref_id": ref_id,
                    "target_page": figure_captions.get(ref_id, 0),
                })

            # 找表引用
            for m in _TBL_REF_RE.finditer(text):
                ref_id = m.group(1).replace("–", "-")
                cross_refs.append({
                    "source_page": page,
                    "source_text": m.group(0),
                    "ref_type": "table",
                    "ref_id": ref_id,
                    "target_page": 0,
                })

        logs.append(f"[build_cross_refs] 发现 {len(cross_refs)} 条交叉引用")
        return {
            "cross_refs": cross_refs,
            "current_node": "build_cross_refs",
            "log_messages": logs,
        }

    # ------------------------------------------------------------------
    # 节点 5：semantic_chunk（核心分块节点）
    # ------------------------------------------------------------------

    def semantic_chunk(state: dict) -> dict:
        """
        基于文档结构的语义分块，产生 manual_chunks。

        分块规则（优先级递减）：
          1. ATA Section 边界 — 绝不跨 section
          2. 表格 — 独立成块（deepdoc TSR 产生的完整表格文本）
          3. WARNING/CAUTION/NOTE — 独立或附加到前后步骤
          4. 编号步骤组 — 同一连续步骤序列保持完整
          5. 段落软上限 — ~800 token（约 1600 字符）

        每个 chunk 携带增强元数据：
          ata_section, section_title, section_hierarchy,
          figure_refs, table_refs, step_number, has_warning, has_caution,
          chunk_type: "text"|"table"|"step"|"alert"
        """
        layout_regions = state.get("layout_regions", [])
        section_tree = state.get("section_tree", [])
        cross_refs = state.get("cross_refs", [])
        file_path = state["file_path"]
        source = os.path.basename(file_path)
        logs = ["[semantic_chunk] 开始语义分块…"]

        MAX_CHARS = 1600  # 约 800 token

        # 建立页码 -> 章节映射
        def _page_to_section(page: int) -> dict:
            best = {}
            for sec in section_tree:
                if sec["page_start"] <= page:
                    if not best or sec["level"] >= best.get("level", 0):
                        best = sec
            return best

        # 建立页码 -> 图/表引用映射
        page_fig_refs = {}
        page_tbl_refs = {}
        for ref in cross_refs:
            pg = ref["source_page"]
            if ref["ref_type"] == "figure":
                page_fig_refs.setdefault(pg, []).append(ref["ref_id"])
            else:
                page_tbl_refs.setdefault(pg, []).append(ref["ref_id"])

        manual_chunks = []

        def _flush(buf_regions: list):
            """将缓冲区中的 regions 合并为一个 chunk。"""
            if not buf_regions:
                return
            text = "\n".join(r["text"].strip() for r in buf_regions if r["text"].strip())
            if not text.strip():
                logger.debug(
                    f"[semantic_chunk] 丢弃空文本 chunk"
                    f"（{len(buf_regions)} regions, "
                    f"types={[r['type'] for r in buf_regions]}）"
                )
                return
            page = buf_regions[0]["page"]
            sec = _page_to_section(page)

            # 确定 chunk_type
            types = {r["type"] for r in buf_regions}
            if "table" in types:
                chunk_type = "table"
            elif any(_ALERT_RE.match(r["text"].strip()) for r in buf_regions):
                chunk_type = "alert"
            elif any(_STEP_RE.match(r["text"].strip()) for r in buf_regions):
                chunk_type = "step"
            else:
                chunk_type = "text"

            has_warning = any("WARNING" in r["text"].upper() for r in buf_regions)
            has_caution = any("CAUTION" in r["text"].upper() for r in buf_regions)

            manual_chunks.append({
                "text": text,
                "chunk_type": chunk_type,
                "page": page,
                "source": source,
                "ata_section": sec.get("ata_code", ""),
                "section_title": sec.get("title", ""),
                "section_hierarchy": sec.get("level", 0),
                "figure_refs": page_fig_refs.get(page, []),
                "table_refs": page_tbl_refs.get(page, []),
                "has_warning": has_warning,
                "has_caution": has_caution,
            })

        buffer = []
        buf_chars = 0
        last_ata = None

        for region in layout_regions:
            r_type = region["type"]
            r_text = region["text"].strip()
            r_page = region["page"]

            if not r_text and r_type != "figure":
                continue

            # 表格：单独成块
            if r_type == "table":
                _flush(buffer)
                buffer = []
                buf_chars = 0
                _flush([region])
                continue

            # 图形区域跳过（由 extract_figures 节点处理）
            if r_type == "figure":
                continue

            # 章节标题：触发 section 边界分块
            if r_type == "title":
                _flush(buffer)
                buffer = []
                buf_chars = 0
                sec = _page_to_section(r_page)
                ata_code = sec.get("ata_code", "")
                if ata_code != last_ata:
                    last_ata = ata_code
                # 标题本身不单独成块，作为下一块的首行
                buffer.append(region)
                buf_chars += len(r_text)
                continue

            # WARNING/CAUTION/NOTE：单独成块
            if _ALERT_RE.match(r_text):
                _flush(buffer)
                buffer = [region]
                buf_chars = len(r_text)
                continue

            # 超出软上限：分块
            if buf_chars + len(r_text) > MAX_CHARS and buffer:
                _flush(buffer)
                buffer = []
                buf_chars = 0

            buffer.append(region)
            buf_chars += len(r_text)

        _flush(buffer)

        logs.append(f"[semantic_chunk] 分块完成，共 {len(manual_chunks)} 个块")
        logs.append(f"  文本块: {sum(1 for c in manual_chunks if c['chunk_type']=='text')}")
        logs.append(f"  表格块: {sum(1 for c in manual_chunks if c['chunk_type']=='table')}")
        logs.append(f"  步骤块: {sum(1 for c in manual_chunks if c['chunk_type']=='step')}")
        logs.append(f"  警告块: {sum(1 for c in manual_chunks if c['chunk_type']=='alert')}")

        if not manual_chunks:
            total_regions = len(layout_regions)
            empty_regions = sum(
                1 for r in layout_regions
                if not r["text"].strip() and r["type"] != "figure"
            )
            logs.append(
                f"[semantic_chunk] ⚠ 产出 0 个 chunk！"
                f"总区域 {total_regions}，空文本区域 {empty_regions}。"
                f"请检查 deepdoc 文本提取是否成功。"
            )
            logger.warning(
                f"semantic_chunk 产出 0 chunks from {total_regions} regions "
                f"({empty_regions} empty)"
            )

        return {
            "manual_chunks": manual_chunks,
            "current_node": "semantic_chunk",
            "log_messages": logs,
        }

    # ------------------------------------------------------------------
    # 节点 6：extract_figures
    # ------------------------------------------------------------------

    def extract_figures(state: dict) -> dict:
        """
        从 layout_regions 中提取 type='figure' 的区域，
        关联 cross_refs 中引用它们的文本块，构建 figure_records。

        图片文件已在 deepdoc_parse_pdf 节点保存到磁盘。
        """
        layout_regions = state.get("layout_regions", [])
        cross_refs = state.get("cross_refs", [])
        logs = ["[extract_figures] 提取图形记录…"]

        # 建立 figure_id -> 引用来源列表
        fig_ref_sources = {}
        for ref in cross_refs:
            if ref["ref_type"] == "figure":
                ref_id = ref["ref_id"]
                fig_ref_sources.setdefault(ref_id, []).append(ref["source_text"])

        figure_records = []
        fig_idx = 0
        source = os.path.basename(state["file_path"])
        doc_prefix = source.rsplit(".", 1)[0]

        for region in layout_regions:
            if region["type"] != "figure":
                continue
            image_path = region.get("image_path", "")
            if not image_path or not os.path.exists(image_path):
                continue

            # 寻找最近的 figure caption
            page = region["page"]
            caption_text = ""
            for r in layout_regions:
                if r["type"] in ("figure caption",) and abs(r["page"] - page) <= 1:
                    cap_m = re.search(r"[Ff]ig(?:ure)?\s*\.?\s*([A-Z]?\d+[-–]\d+|\d+)", r["text"])
                    if cap_m:
                        fig_ref_id = cap_m.group(1).replace("–", "-")
                        caption_text = r["text"].strip()
                        break

            figure_id = f"{doc_prefix}_fig_{fig_idx:03d}"
            figure_records.append({
                "figure_id": figure_id,
                "image_path": image_path,
                "page": page,
                "ata_section": "",  # 将在 encode 阶段填充
                "caption_text": caption_text,
                "referencing_chunks": fig_ref_sources.get(
                    re.search(r"\d+[-–]\d+", caption_text).group(0) if re.search(r"\d+[-–]\d+", caption_text) else "", []
                ),
                "context_text": caption_text,
                "figure_type": "flowchart" if _is_flowchart(caption_text, region.get("text", "")) else "illustration",
                "flowchart_json": None,
                "source": source,
            })
            fig_idx += 1

        logs.append(f"[extract_figures] 提取到 {len(figure_records)} 张图形")
        return {
            "figure_records": figure_records,
            "current_node": "extract_figures",
            "log_messages": logs,
        }

    # ------------------------------------------------------------------
    # 节点 7：generate_tech_captions
    # ------------------------------------------------------------------

    def generate_tech_captions(state: dict) -> dict:
        """
        为技术图形生成航空领域专用的中英文描述。

        使用 MiniMax Vision API（与 generate_captions 相同接口），
        但采用航空技术图专用提示词，关注：
          - 图形类型（剖视图、安装图、流程图、接线图…）
          - 零件编号（P/N 格式）
          - 空间关系（箭头方向、安装位置）
          - ATA 章节相关性

        降级策略：Vision API 失败 → 使用 caption_text + context_text。
        """
        figure_records = state.get("figure_records", [])
        if not figure_records:
            return {"current_node": "generate_tech_captions",
                    "log_messages": ["[gen_tech_cap] 无图形，跳过"]}

        logs = [f"[gen_tech_cap] 为 {len(figure_records)} 张图形生成描述…"]

        TECH_PROMPT = (
            "You are analyzing a technical figure from an aircraft engine maintenance manual. "
            "Describe the figure in detail, focusing on: "
            "1) Figure type (cross-section, installation diagram, schematic, wiring diagram, etc.), "
            "2) Part numbers visible (P/N format), "
            "3) Spatial relationships and directional arrows, "
            "4) Component names and their functions, "
            "5) Any measurements, tolerances, or specifications shown. "
            "Be concise but precise. Respond in English."
        )

        updated_records = []
        for rec in figure_records:
            image_path = rec["image_path"]
            basename = os.path.basename(image_path)
            caption = rec.get("caption_text", "")

            # 优先 Vision API
            if app_state.minimax_client and app_state.minimax_model:
                try:
                    from backend.image_captioner import describe_image
                    caption = describe_image(
                        app_state.minimax_client,
                        app_state.minimax_model,
                        image_path,
                        rec.get("context_text", ""),
                        extra_prompt=TECH_PROMPT,
                    )
                    logs.append(f"  {basename}: Vision API 成功")
                except Exception as e:
                    logs.append(f"  {basename}: Vision API 失败 ({e})，用 caption 降级")

            # 降级：用现有 caption_text
            if not caption:
                caption = rec.get("caption_text", "") or rec.get("context_text", "")
                if caption:
                    logs.append(f"  {basename}: 使用 caption 降级")
                else:
                    logs.append(f"  {basename}: 无描述，跳过")
                    continue

            updated_rec = dict(rec)
            updated_rec["caption_text"] = caption
            updated_records.append(updated_rec)

        logs.append(f"[gen_tech_cap] 完成，{len(updated_records)} 张图形有描述")
        return {
            "figure_records": updated_records,
            "current_node": "generate_tech_captions",
            "log_messages": logs,
        }

    # ------------------------------------------------------------------
    # 节点 7b：extract_flowchart_structure
    # ------------------------------------------------------------------

    def extract_flowchart_structure(state: dict) -> dict:
        """
        对 figure_type='flowchart' 的图片调用 Vision LLM，
        提取结构化 JSON（nodes/edges/entry/exits），
        然后生成两种 chunk 追加到 manual_chunks：
          - flowchart_node: 每个节点一个 chunk（含 YES/NO 分支）
          - flowchart_path: 每个出口节点一条从入口到出口的路径 chunk
        """
        figure_records = state.get("figure_records", [])
        manual_chunks = list(state.get("manual_chunks", []))
        logs = [f"[extract_fc] 检查 {len(figure_records)} 张图形是否含流程图…"]

        FLOWCHART_PROMPT = (
            "You are analyzing a troubleshooting flowchart from an aircraft engine maintenance manual. "
            "Extract the complete flow structure. "
            "Return ONLY valid JSON (no markdown fences, no extra text), using this schema:\n"
            "{\n"
            '  "figure_title": "string (e.g., ENGINE START FAULT ISOLATION)",\n'
            '  "sheet_info": "string (e.g., SHEET 7 OF 8, or empty)",\n'
            '  "entry_node": "id of the first node",\n'
            '  "nodes": [\n'
            '    {"id": "n0", "type": "terminal|decision|action|connector", "text": "exact text"}\n'
            "  ],\n"
            '  "edges": [\n'
            '    {"from": "n0", "to": "n1", "condition": "YES|NO|null"}\n'
            "  ],\n"
            '  "sheet_refs": {"FROM SHEET X": "note"}\n'
            "}\n\n"
            "Rules:\n"
            "- Decision diamonds → type 'decision'\n"
            "- Action/procedure rectangles → type 'action'\n"
            "- Start/End ovals → type 'terminal'\n"
            "- 'FROM SHEET X' / 'TO SHEET X' connectors → type 'connector'\n"
            "- Use null (not the string 'null') for unconditional edges\n"
            "- If text is unreadable, write [ILLEGIBLE]\n"
            "- Accuracy over completeness"
        )

        fc_count = sum(1 for r in figure_records if r.get("figure_type") == "flowchart")
        if fc_count == 0:
            logs.append("[extract_fc] 未检测到流程图，跳过")
            return {"manual_chunks": manual_chunks, "log_messages": logs,
                    "current_node": "extract_flowchart_structure"}

        logs.append(f"[extract_fc] 检测到 {fc_count} 张流程图，开始结构提取…")
        extracted = 0
        updated_records = []

        for rec in figure_records:
            if rec.get("figure_type") != "flowchart":
                updated_records.append(rec)
                continue

            image_path = rec["image_path"]
            basename = os.path.basename(image_path)

            fc_data = {}
            if app_state.minimax_client and app_state.minimax_model:
                try:
                    from backend.image_captioner import describe_image
                    raw = describe_image(
                        app_state.minimax_client,
                        app_state.minimax_model,
                        image_path,
                        rec.get("context_text", ""),
                        extra_prompt=FLOWCHART_PROMPT,
                    )
                    fc_data = _parse_flowchart_json(raw)
                    if fc_data.get("nodes"):
                        logs.append(
                            f"  {basename}: 提取到 {len(fc_data['nodes'])} 个节点, "
                            f"{len(fc_data.get('edges', []))} 条边"
                        )
                    else:
                        logs.append(f"  {basename}: JSON 解析失败或节点为空，降级为普通图片")
                except Exception as e:
                    logs.append(f"  {basename}: Vision API 调用失败 ({e})，降级为普通图片")
            else:
                logs.append(f"  {basename}: 无 Vision API，跳过流程图提取")

            rec = dict(rec)
            if fc_data.get("nodes"):
                # 补充 ata_section（从 manual_chunks 中查找最近的章节）
                if not rec.get("ata_section"):
                    page = rec.get("page", 0)
                    for chunk in reversed(manual_chunks):
                        if chunk.get("page", 0) <= page and chunk.get("ata_section"):
                            rec["ata_section"] = chunk["ata_section"]
                            break

                node_chunks = _expand_flowchart_to_chunks(fc_data, rec)
                path_chunks = _build_path_summaries(fc_data, rec)
                manual_chunks.extend(node_chunks)
                manual_chunks.extend(path_chunks)
                rec["flowchart_json"] = fc_data
                extracted += 1
                logs.append(
                    f"  {basename}: 生成 {len(node_chunks)} 个节点 chunk, "
                    f"{len(path_chunks)} 条路径 chunk"
                )

            updated_records.append(rec)

        logs.append(f"[extract_fc] 完成，成功提取 {extracted}/{fc_count} 张流程图")
        return {
            "figure_records": updated_records,
            "manual_chunks": manual_chunks,
            "current_node": "extract_flowchart_structure",
            "log_messages": logs,
        }

    # ------------------------------------------------------------------
    # 节点 8：vision_layout_agent
    # ------------------------------------------------------------------

    def vision_layout_agent(state: dict) -> dict:
        """
        矢量插图页布局检测智能体。

        对 layout_regions 中无 figure 记录且文本覆盖 < 30% 的页面：
        1. 收集 deepdoc OCR 出的短文本标签（P/N 编号、工具名等，≤30字符）
        2. 对标签的 Y/X 坐标做 1D 聚类，推断行列数
        3. 若检测到格栅（行≥2 && 列≥2 && 标签数≥格子数50%）：
           - 逐格裁切为 N 张独立图片（label 作为 context_text 传给 Vision caption）
        4. 否则全页渲染为 1 张图（适用于爆炸图等单幅大图）
        """
        layout_regions = list(state.get("layout_regions", []))
        file_path = state["file_path"]
        logs = ["[vision_layout] 检查矢量插图页…"]

        # ── 辅助函数 ────────────────────────────────────────────────────
        def _cluster_pos(positions, tol):
            if not positions:
                return []
            sorted_pos = sorted(set(positions))
            clusters, cur = [], [sorted_pos[0]]
            for p in sorted_pos[1:]:
                if p - cur[-1] <= tol:
                    cur.append(p)
                else:
                    clusters.append(sum(cur) / len(cur))
                    cur = [p]
            clusters.append(sum(cur) / len(cur))
            return clusters

        def _cell_bounds(centers, lo, hi):
            if len(centers) == 1:
                return [(lo, hi)]
            mids = [(centers[i] + centers[i + 1]) / 2 for i in range(len(centers) - 1)]
            return ([(lo, mids[0])]
                    + [(mids[i - 1], mids[i]) for i in range(1, len(mids))]
                    + [(mids[-1], hi)])

        # ── 找出稀疏页（无 figure 且文本覆盖 < 30%） ────────────────────
        pages_with_figs = {r["page"] for r in layout_regions if r["type"] == "figure"}

        try:
            import fitz as _fitz
            vg_idx = sum(1 for r in layout_regions if r["type"] == "figure")
            doc_prefix = os.path.basename(file_path).rsplit(".", 1)[0]

            with _fitz.open(file_path) as pdf:
                for pn in range(len(pdf)):
                    pn1 = pn + 1
                    if pn1 in pages_with_figs:
                        continue

                    page = pdf[pn]
                    rect = page.rect
                    page_area = rect.width * rect.height

                    page_regs = [r for r in layout_regions
                                 if r["page"] == pn1 and r["type"] != "figure"]
                    text_area = sum(
                        (r["x1"] - r["x0"]) * (r["bottom"] - r["top"])
                        for r in page_regs
                    )
                    if text_area / max(page_area, 1) >= 0.30:
                        continue  # 文本覆盖充足，非插图页

                    # ── 文本标签聚类检测格栅布局 ────────────────────────
                    # deepdoc 已将 P/N 编号、工具名等短标签 OCR 出来，
                    # 利用它们的 Y/X 坐标聚类直接推断是否为格栅布局，
                    # 无需 Vision API（MiniMax 不接受 data: base64 URI）。
                    layout_info = None
                    labels = [r for r in page_regs
                              if r.get("text", "").strip()
                              and len(r["text"].strip()) <= 30
                              and "\n" not in r["text"].strip()]

                    if len(labels) >= 4:
                        row_c = _cluster_pos([r["top"] for r in labels], tol=40)
                        col_c = _cluster_pos([r["x0"]  for r in labels], tol=60)
                        n_rows, n_cols = len(row_c), len(col_c)
                        # 至少 2 行 2 列，且标签数填充了至少一半格子
                        if (n_rows >= 2 and n_cols >= 2
                                and len(labels) >= max(4, n_rows * n_cols * 0.5)):
                            layout_info = {
                                "page_type": "grid",
                                "grid_rows": n_rows,
                                "grid_cols": n_cols,
                                "description": "",
                            }
                            logs.append(
                                f"[vision_layout] 第{pn1}页 聚类检测: "
                                f"{len(labels)} 个标签 → {n_rows}行×{n_cols}列格栅"
                            )

                    # ── 按布局信息决策 ──────────────────────────────────
                    # JSON null → Python None；用 or 保证始终是字符串/默认值
                    page_type = (layout_info or {}).get("page_type") or "single_figure"
                    description = (layout_info or {}).get("description") or ""

                    if page_type == "text_only":
                        logs.append(f"[vision_layout] 第{pn1}页：纯文字页，跳过")
                        continue

                    if page_type == "grid":
                        rows = int((layout_info or {}).get("grid_rows", 1))
                        cols = int((layout_info or {}).get("grid_cols", 1))
                        logs.append(
                            f"[vision_layout] 第{pn1}页：格栅 {rows}×{cols}"
                            + (f" — {description}" if description else "")
                        )

                        # 文本标签聚类推算格栅边界
                        labels = [r for r in page_regs
                                  if len(r["text"].strip()) <= 25
                                  and "\n" not in r["text"].strip()]
                        row_c = _cluster_pos([r["top"] for r in labels], tol=40)
                        col_c = _cluster_pos([r["x0"]  for r in labels], tol=60)

                        # 聚类不足时退回均匀分割
                        if len(row_c) < rows:
                            row_c = [rect.height * (i + 0.5) / rows
                                     for i in range(rows)]
                        if len(col_c) < cols:
                            col_c = [rect.width * (i + 0.5) / cols
                                     for i in range(cols)]

                        row_bounds = _cell_bounds(row_c, 0, rect.height)
                        col_bounds = _cell_bounds(col_c, 0, rect.width)

                        for ri, (ry0, ry1) in enumerate(row_bounds[:rows]):
                            for ci, (cx0, cx1) in enumerate(col_bounds[:cols]):
                                cell_label = next(
                                    (lb["text"].strip() for lb in labels
                                     if ry0 <= lb["top"] <= ry1
                                     and cx0 <= lb["x0"] <= cx1),
                                    ""
                                )
                                clip_pix = page.get_pixmap(
                                    matrix=_fitz.Matrix(2, 2),
                                    clip=_fitz.Rect(cx0, ry0, cx1, ry1)
                                )
                                if clip_pix.width < 32 or clip_pix.height < 32:
                                    continue
                                fname = (
                                    f"{doc_prefix}_fig_{vg_idx:03d}"
                                    f"_p{pn1}_r{ri}c{ci}.png"
                                )
                                fpath = os.path.join(image_dir, fname)
                                clip_pix.save(fpath)
                                layout_regions.append({
                                    "page": pn1,
                                    "type": "figure",
                                    "text": cell_label,
                                    "x0": cx0, "x1": cx1,
                                    "top": ry0, "bottom": ry1,
                                    "positions": [],
                                    "image_path": fpath,
                                })
                                vg_idx += 1

                    else:  # single_figure（或 layout_info 为 None 的降级）
                        full_pix = page.get_pixmap(matrix=_fitz.Matrix(2, 2))
                        if full_pix.width < 64 or full_pix.height < 64:
                            continue
                        fname = f"{doc_prefix}_fig_{vg_idx:03d}_p{pn1}_vg.png"
                        fpath = os.path.join(image_dir, fname)
                        full_pix.save(fpath)
                        layout_regions.append({
                            "page": pn1,
                            "type": "figure",
                            "text": description,
                            "x0": float(rect.x0), "x1": float(rect.x1),
                            "top": float(rect.y0), "bottom": float(rect.y1),
                            "positions": [],
                            "image_path": fpath,
                        })
                        vg_idx += 1
                        logs.append(
                            f"[vision_layout] 第{pn1}页：全页渲染"
                            + (f" — {description}" if description else "")
                        )

        except Exception as _e:
            logger.exception("vision_layout_agent 异常")
            logs.append(f"[vision_layout] 异常: {_e}")

        added = sum(1 for r in layout_regions if r["type"] == "figure") - len(pages_with_figs)
        if added > 0:
            logs.append(f"[vision_layout] 共补充 {added} 个图形区域")

        return {
            "layout_regions": layout_regions,
            "current_node": "vision_layout_agent",
            "log_messages": logs,
        }

    # ------------------------------------------------------------------
    # 返回节点字典
    # ------------------------------------------------------------------
    return {
        "analyze_pdf_type": analyze_pdf_type,
        "deepdoc_parse_pdf": deepdoc_parse_pdf,
        "extract_structure": extract_structure,
        "build_cross_refs": build_cross_refs,
        "semantic_chunk": semantic_chunk,
        "extract_figures": extract_figures,
        "generate_tech_captions": generate_tech_captions,
        "extract_flowchart_structure": extract_flowchart_structure,
        "vision_layout_agent": vision_layout_agent,
    }
