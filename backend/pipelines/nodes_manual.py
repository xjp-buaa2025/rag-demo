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
        logs = [f"[deepdoc_parse] 开始解析: {os.path.basename(file_path)}"]

        if not app_state.deepdoc_engine:
            return {"error": "deepdoc_engine 未初始化，无法解析 PDF",
                    "log_messages": logs, "current_node": "deepdoc_parse_pdf"}

        try:
            def _progress(p, msg=""):
                pct = int(p * 100)
                logs.append(f"  [{pct}%] {msg}")

            result = app_state.deepdoc_engine.parse_pdf(file_path, progress_callback=_progress)
        except Exception as e:
            return {"error": f"deepdoc 解析失败: {e}",
                    "log_messages": logs, "current_node": "deepdoc_parse_pdf"}

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
                with fitz.open(file_path) as pdf:
                    for page_num in range(len(pdf)):
                        page = pdf[page_num]
                        blocks = page.get_text("dict", flags=11)["blocks"]
                        for block in blocks:
                            if block["type"] != 0:  # 只处理文本 block
                                continue
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
                logs.append(
                    f"[deepdoc_parse] fitz block 提取完成：{len(layout_regions)} 个区域"
                )
            except Exception as e:
                logs.append(f"[deepdoc_parse] fitz 提取失败: {e}")

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
    }
