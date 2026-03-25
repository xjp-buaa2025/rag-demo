"""
backend/routers/bom.py — BOM 图数据库接口

GET  /bom/status    — Neo4j 连接状态（JSON）
POST /bom/ingest    — BOM 文件 → Neo4j 入库（支持 xlsx/pdf/docx，multipart + SSE）
POST /bom/query     — 关键词查询 BOM 图谱（JSON）

支持 PDF/DOCX 上传：先提取文本/表格，再调用 LLM 自动转换为标准 BOM 格式。
Neo4j 驱动懒加载：首次调用时建立连接，用 state.neo4j_lock 防止并发重复连接。
"""

import json
import os
import re
import tempfile
from typing import Optional

import pandas as pd
import pdfplumber
from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from pydantic import BaseModel

from backend.deps import get_state, get_neo4j_cfg
from backend.state import AppState
from backend.sse import log_gen_to_sse

try:
    from docx import Document as DocxDocument
    _DOCX_AVAILABLE = True
except ImportError:
    _DOCX_AVAILABLE = False

router = APIRouter(prefix="/bom")

try:
    from neo4j import GraphDatabase as _Neo4jDriver
    _NEO4J_AVAILABLE = True
except ImportError:
    _NEO4J_AVAILABLE = False


# ==========================================
# Neo4j 懒加载辅助函数
# ==========================================

def _get_neo4j_driver(state: AppState, cfg: dict):
    """获取 Neo4j 驱动，首次建立连接时加锁，失败返回 None。"""
    if state.neo4j_driver is not None:
        return state.neo4j_driver
    if not _NEO4J_AVAILABLE:
        return None
    with state.neo4j_lock:
        if state.neo4j_driver is not None:
            return state.neo4j_driver
        try:
            driver = _Neo4jDriver.driver(cfg["uri"], auth=(cfg["user"], cfg["pass"]))
            driver.verify_connectivity()
            state.neo4j_driver = driver
        except Exception:
            state.neo4j_driver = None
    return state.neo4j_driver


# ==========================================
# PDF / DOCX 文本提取
# ==========================================

def _extract_from_pdf(filepath: str) -> str:
    """从 PDF 提取文本，优先提取表格（转 Markdown table），无表格则提取纯文本。"""
    all_content = []
    with pdfplumber.open(filepath) as pdf:
        for i, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            if tables:
                for table in tables:
                    if not table or not table[0]:
                        continue
                    header = table[0]
                    md = "| " + " | ".join(str(c or "") for c in header) + " |\n"
                    md += "| " + " | ".join("---" for _ in header) + " |\n"
                    for row in table[1:]:
                        md += "| " + " | ".join(str(c or "") for c in row) + " |\n"
                    all_content.append(f"[Page {i + 1} Table]\n{md}")
            else:
                text = page.extract_text() or ""
                if text.strip():
                    all_content.append(f"[Page {i + 1}]\n{text}")
    return "\n\n".join(all_content)


def _extract_from_docx(filepath: str) -> str:
    """从 DOCX 提取表格（转 Markdown table）和标题段落。
    BOM 数据主要在表格中，段落仅保留标题级别的作为上下文，避免正文过多。"""
    doc = DocxDocument(filepath)
    all_content = []
    # 仅保留标题段落作为上下文（Heading 1-4 或短段落）
    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
        is_heading = para.style and para.style.name and "Heading" in para.style.name
        if is_heading or (len(text) < 80 and not text.endswith("。")):
            all_content.append(text)
    # 提取所有表格（BOM 数据的主要来源）
    for idx, table in enumerate(doc.tables):
        rows = []
        for row in table.rows:
            rows.append([cell.text.strip() for cell in row.cells])
        if rows:
            header = rows[0]
            md = "| " + " | ".join(header) + " |\n"
            md += "| " + " | ".join("---" for _ in header) + " |\n"
            for row in rows[1:]:
                md += "| " + " | ".join(row) + " |\n"
            all_content.append(f"[Table {idx + 1}]\n{md}")
    return "\n\n".join(all_content)


# ==========================================
# LLM BOM 格式转换
# ==========================================

BOM_CONVERSION_PROMPT = """你是一个BOM（物料清单）数据结构化专家。请将以下文档内容解析为标准BOM格式的JSON数组。

## 必填字段说明
- level_code: 层级编码，如 "1", "1.1", "1.1.1"（用.分隔，表示父子关系层级）
- part_id: 零件编号/图号（如文档中无编号，请根据零件名称生成如 P001, P002 格式的编号）
- part_name: 零件中文名称
- part_name_en: 零件英文名称（如无法确定，留空字符串）
- category: 分类，必须是以下三者之一：
  - "Assembly"：组件/总成（包含子零件的装配体）
  - "Part"：零件（最底层不可拆分的零件）
  - "Standard"：标准件（螺栓、螺母、垫圈、轴承等通用标准件）
- qty: 数量（整数，默认1）
- unit: 单位（件、个、套等，默认"件"）

## 选填字段
- material: 材料（如钛合金、不锈钢等，无则留空字符串）
- weight_kg: 重量(kg)，数字字符串或空字符串
- spec: 规格型号（无则留空字符串）
- note: 备注（无则留空字符串）

## 层级编码规则
- 最顶层组件编码为 "1"（如有多个顶层则为 "1", "2", "3"...）
- 子零件编码在父零件后追加，如 "1.1", "1.2"
- 更深层级类推："1.1.1", "1.1.2"
- 根据文档中的缩进、编号或上下文关系推断层级

## 输出要求
仅输出JSON数组，不要有任何其他说明文字。示例：
```json
[
  {{"level_code":"1","part_id":"ASM-001","part_name":"高压压气机","part_name_en":"HPC","category":"Assembly","qty":1,"unit":"套","material":"","weight_kg":"","spec":"","note":""}},
  {{"level_code":"1.1","part_id":"BLD-001","part_name":"第一级叶片","part_name_en":"Stage 1 Blade","category":"Part","qty":36,"unit":"件","material":"钛合金TC4","weight_kg":"0.5","spec":"","note":""}}
]
```

## 待解析的文档内容：
{content}"""


def _split_for_llm(text: str, max_chars: int = 15000) -> list:
    """按 [Page N] / [Table N] 标记分割文本，保证单个表格不被截断。
    max_chars 默认 15000（约 5000-7000 中文 token），平衡调用次数与上下文质量。"""
    sections = re.split(r"(?=\[(?:Page|Table) \d+)", text)
    chunks, current = [], ""
    for section in sections:
        if len(current) + len(section) > max_chars and current:
            chunks.append(current)
            current = section
        else:
            current += section
    if current:
        chunks.append(current)
    return chunks if chunks else [text]


def _parse_llm_json(raw: str) -> list:
    """从 LLM 输出中提取 JSON 数组，容错处理。"""
    raw = re.sub(r"```json\s*", "", raw)
    raw = re.sub(r"```\s*", "", raw)
    raw = raw.strip()
    try:
        data = json.loads(raw)
        return data if isinstance(data, list) else [data]
    except json.JSONDecodeError:
        pass
    match = re.search(r"\[.*\]", raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return []


class _LlmBomConverter:
    """调用 LLM 将提取的原始文本分段转换为标准 BOM DataFrame。
    用 run() 生成器逐段 yield 日志消息，转换完成后从 .df 获取结果。"""

    def __init__(self, raw_text: str, state: AppState):
        self._raw_text = raw_text
        self._state = state
        self.df: Optional[pd.DataFrame] = None

    def run(self):
        """生成器：逐段调用 LLM，每一步 yield 一条日志字符串。"""
        chunks = _split_for_llm(self._raw_text)
        yield f"   文档分为 {len(chunks)} 段，开始 LLM 转换…"

        all_records = []
        for i, chunk in enumerate(chunks):
            yield f"   🤖 LLM 转换第 {i + 1}/{len(chunks)} 段…"
            prompt = BOM_CONVERSION_PROMPT.format(content=chunk)
            try:
                resp = self._state.llm_client.chat.completions.create(
                    model=None,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                )
                raw_json = resp.choices[0].message.content
                records = _parse_llm_json(raw_json)
                yield f"   ✅ 第 {i + 1} 段提取到 {len(records)} 条记录"
                all_records.extend(records)
            except Exception as e:
                yield f"   ⚠️ 第 {i + 1} 段 LLM 调用失败：{e}"

        if not all_records:
            self.df = None
            return

        df = pd.DataFrame(all_records)
        required = ["level_code", "part_id", "part_name", "part_name_en",
                     "category", "qty", "unit"]
        optional = ["material", "weight_kg", "spec", "note"]
        for col in required + optional:
            if col not in df.columns:
                df[col] = ""
        df["qty"] = pd.to_numeric(df["qty"], errors="coerce").fillna(1).astype(int)
        df["unit"] = df["unit"].replace("", "件")
        df["category"] = df["category"].replace("", "Part")
        df = df.dropna(subset=["level_code", "part_id"])
        df = df[df["level_code"].astype(str).str.strip() != ""]
        df = df[df["part_id"].astype(str).str.strip() != ""]
        for col in df.columns:
            df[col] = df[col].fillna("").astype(str).str.strip()
        df["qty"] = pd.to_numeric(df["qty"], errors="coerce").fillna(1).astype(int)

        self.df = df
        yield f"   ✅ LLM 转换完成：共 {len(df)} 条有效记录"


# ==========================================
# GET /bom/status
# ==========================================

@router.get("/status", summary="Neo4j 连接状态")
def bom_status(state: AppState = Depends(get_state), cfg: dict = Depends(get_neo4j_cfg)):
    """检测 Neo4j 连接，返回节点/关系数量。"""
    # 强制重新连接（等同于 app.py 中的 _neo4j_driver = None 重置）
    with state.neo4j_lock:
        if state.neo4j_driver is not None:
            try:
                state.neo4j_driver.close()
            except Exception:
                pass
        state.neo4j_driver = None

    if not _NEO4J_AVAILABLE:
        return {"connected": False, "error": "neo4j 包未安装，请运行 pip install neo4j", "uri": cfg["uri"]}

    driver = _get_neo4j_driver(state, cfg)
    if driver is None:
        return {"connected": False, "error": "无法连接 Neo4j，请确认 Docker 容器已启动", "uri": cfg["uri"]}

    try:
        with driver.session() as s:
            nodes = s.run("""
                MATCH (n) WHERE n:Assembly OR n:Part OR n:Standard
                RETURN count(n) AS cnt
            """).single()["cnt"]
            edges = s.run("MATCH ()-[r:CHILD_OF]->() RETURN count(r) AS cnt").single()["cnt"]
        return {"connected": True, "nodes": nodes, "edges": edges, "uri": cfg["uri"]}
    except Exception as e:
        return {"connected": False, "error": str(e), "uri": cfg["uri"]}


# ==========================================
# POST /bom/ingest
# ==========================================

@router.post("/ingest/pipeline", summary="LangGraph 管道 BOM 入库（SSE）")
def bom_ingest_pipeline(
    request: Request,
    file: Optional[UploadFile] = File(default=None),
    clear_first: bool = Form(default=False),
    state: AppState = Depends(get_state),
    cfg: dict = Depends(get_neo4j_cfg),
):
    """
    LangGraph 管道 BOM 入库：
    - PDF/DOCX：extract_tables → llm_to_csv → validate_bom_df → write_neo4j
    - Excel/CSV：load_table → validate_bom_df → write_neo4j
    响应为 SSE 日志流。
    """
    from backend.pipelines.sse_bridge import pipeline_to_log_generator

    if state.lg_bom_pipeline is None:
        def _err():
            yield "❌ LangGraph BOM 管道未初始化，请检查后端日志"
        return log_gen_to_sse(_err())

    bom_default = request.app.state.bom_default

    if file is None:
        # 使用默认 BOM 文件
        filepath = bom_default
        filename = os.path.basename(filepath)
        tmp_path = None
    else:
        # 将上传文件写入临时目录
        suffix = os.path.splitext(file.filename or "bom.xlsx")[1] or ".xlsx"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(file.file.read())
            tmp_path = tmp.name
        filepath = tmp_path
        filename = file.filename

    if not os.path.exists(filepath):
        def _err():
            yield f"❌ 文件不存在：{filepath}"
        return log_gen_to_sse(_err())

    initial_state = {
        "file_path": filepath,
        "pipeline_mode": "bom",
        "clear_first": clear_first,
        "log_messages": [f"[pipeline] 开始处理 BOM：{filename}"],
    }

    def _cleanup_gen():
        try:
            yield from pipeline_to_log_generator(state.lg_bom_pipeline, initial_state)
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass

    return log_gen_to_sse(_cleanup_gen())


@router.post("/ingest", summary="BOM 文件入库（xlsx/pdf/docx，SSE）")
def bom_ingest(
    request: Request,
    file: Optional[UploadFile] = File(default=None),
    clear_first: bool = Form(default=False),
    state: AppState = Depends(get_state),
    cfg: dict = Depends(get_neo4j_cfg),
):
    """
    上传 BOM 文件（xlsx/pdf/docx，可选），写入 Neo4j。
    PDF/DOCX 会自动通过 LLM 转换为标准 BOM 格式。
    响应为 SSE 日志流。
    """
    bom_default = request.app.state.bom_default
    gen = _run_bom_ingest(state, cfg, file, clear_first, bom_default)
    return log_gen_to_sse(gen)


def _run_bom_ingest(state: AppState, cfg: dict, file, clear_first: bool, bom_default: str):
    """BOM 入库生成器，迁移自 app.py run_bom_ingest_ui()。"""
    lines = []

    def emit(msg):
        lines.append(msg)
        return "\n".join(lines)

    tmp_path = None
    try:
        # 确定文件路径
        if file is None:
            filepath = bom_default
            yield emit(f"📌 未上传文件，使用默认测试 BOM：{os.path.basename(filepath)}")
        else:
            # 将上传文件写入临时路径
            suffix = os.path.splitext(file.filename or "bom.xlsx")[1] or ".xlsx"
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
                tmp.write(file.file.read())
                tmp_path = tmp.name
            filepath = tmp_path
            yield emit(f"📌 使用上传文件：{file.filename}")

        if not os.path.exists(filepath):
            yield emit(f"❌ 文件不存在：{filepath}")
            return

        # 根据文件类型读取 BOM
        ext = os.path.splitext(filepath)[1].lower()
        yield emit(f"📖 读取 BOM 表（{ext}）…")

        try:
            if ext in (".xlsx", ".xls"):
                # Excel 直接读取
                df = pd.read_excel(filepath, dtype=str)
                df.columns = [c.strip().lower() for c in df.columns]
                for col in ("material", "weight_kg", "spec", "note"):
                    if col not in df.columns:
                        df[col] = ""
                df = df.dropna(subset=["level_code", "part_id"])
                for col in df.columns:
                    df[col] = df[col].fillna("").astype(str).str.strip()
                df["qty"] = pd.to_numeric(df["qty"], errors="coerce").fillna(1).astype(int)

            elif ext == ".pdf":
                yield emit("📄 正在提取 PDF 内容…")
                raw_text = _extract_from_pdf(filepath)
                if not raw_text.strip():
                    yield emit("❌ PDF 中未找到可识别的文本或表格")
                    return
                yield emit(f"✅ PDF 提取完成（{len(raw_text)} 字符）")
                yield emit("🤖 调用 LLM 自动转换 BOM 格式…")
                converter = _LlmBomConverter(raw_text, state)
                for log_line in converter.run():
                    yield emit(log_line)
                df = converter.df
                if df is None or df.empty:
                    yield emit("❌ LLM 未能从文档中提取有效 BOM 记录，请检查文档内容")
                    return

            elif ext == ".docx":
                if not _DOCX_AVAILABLE:
                    yield emit("❌ 缺少 python-docx，请运行：pip install python-docx")
                    return
                yield emit("📄 正在提取 DOCX 内容…")
                raw_text = _extract_from_docx(filepath)
                if not raw_text.strip():
                    yield emit("❌ DOCX 中未找到可识别的文本或表格")
                    return
                yield emit(f"✅ DOCX 提取完成（{len(raw_text)} 字符）")
                yield emit("🤖 调用 LLM 自动转换 BOM 格式…")
                converter = _LlmBomConverter(raw_text, state)
                for log_line in converter.run():
                    yield emit(log_line)
                df = converter.df
                if df is None or df.empty:
                    yield emit("❌ LLM 未能从文档中提取有效 BOM 记录，请检查文档内容")
                    return

            elif ext == ".doc":
                yield emit("❌ 不支持旧版 .doc 格式，请将文件另存为 .docx 后重新上传")
                return
            else:
                yield emit(f"❌ 不支持的文件格式：{ext}（支持 xlsx/pdf/docx）")
                return

            yield emit(f"✅ 读取成功：共 {len(df)} 条零件记录")
        except Exception as e:
            yield emit(f"❌ 读取失败：{e}")
            return

        # 连接 Neo4j
        yield emit(f"🔌 连接 Neo4j（{cfg['uri']}）…")
        driver = _get_neo4j_driver(state, cfg)
        if driver is None:
            yield emit("❌ Neo4j 不可用，请先启动：docker start neo4j")
            return
        yield emit("✅ 连接成功")

        with driver.session() as session:
            for label in ("Assembly", "Part", "Standard"):
                session.run(f"CREATE CONSTRAINT IF NOT EXISTS FOR (n:{label}) REQUIRE n.part_id IS UNIQUE")
            yield emit("🔧 Schema 约束已就绪")

            if clear_first:
                r = session.run("""
                    MATCH (n) WHERE n:Assembly OR n:Part OR n:Standard
                    DETACH DELETE n RETURN count(n) AS cnt
                """).single()
                yield emit(f"🗑️ 已清空旧数据（{r['cnt']} 个节点）")

            records = df.to_dict(orient="records")
            for category in ("Assembly", "Part", "Standard"):
                batch = [r for r in records if r["category"] == category]
                if not batch:
                    continue
                session.run(f"""
                    UNWIND $rows AS row
                    MERGE (n:{category} {{part_id: row.part_id}})
                    SET n.level_code   = row.level_code,
                        n.part_name    = row.part_name,
                        n.part_name_en = row.part_name_en,
                        n.qty          = toInteger(row.qty),
                        n.unit         = row.unit,
                        n.material     = row.material,
                        n.weight_kg    = CASE row.weight_kg WHEN '' THEN null ELSE toFloat(row.weight_kg) END,
                        n.spec         = row.spec,
                        n.note         = row.note
                """, rows=batch)
                yield emit(f"   ✅ {category}：写入 {len(batch)} 个节点")

            level_map = dict(zip(df["level_code"], df["part_id"]))
            edges = []
            for _, row in df.iterrows():
                code = str(row["level_code"])
                if "." not in code:
                    continue
                parent_code = ".".join(code.split(".")[:-1])
                parent_id = level_map.get(parent_code)
                if parent_id:
                    edges.append({"child_id": row["part_id"], "parent_id": parent_id})
            if edges:
                session.run("""
                    UNWIND $edges AS e
                    MATCH (child  {part_id: e.child_id})
                    MATCH (parent {part_id: e.parent_id})
                    MERGE (child)-[:CHILD_OF]->(parent)
                """, edges=edges)
            yield emit(f"   ✅ CHILD_OF 关系：建立 {len(edges)} 条")

            r2 = session.run("""
                MATCH (n) WHERE n:Assembly OR n:Part OR n:Standard
                RETURN count(CASE WHEN n:Assembly THEN 1 END) AS a,
                       count(CASE WHEN n:Part     THEN 1 END) AS p,
                       count(CASE WHEN n:Standard THEN 1 END) AS s
            """).single()
            yield emit(
                f"\n🎉 入库完成！Assembly:{r2['a']}  Part:{r2['p']}  Standard:{r2['s']}  "
                f"关系:{len(edges)} 条\n可视化查看：http://localhost:7474"
            )
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass


# ==========================================
# POST /bom/query
# ==========================================

class BomQueryRequest(BaseModel):
    question: str


@router.post("/query", summary="查询 BOM 图谱")
def bom_query(body: BomQueryRequest, state: AppState = Depends(get_state), cfg: dict = Depends(get_neo4j_cfg)):
    """从 Neo4j 查询与问题相关的 BOM 零件信息，返回格式化文本。"""
    bom_text = _query_bom_text(state, cfg, body.question)
    return {"bom_text": bom_text}


def _query_bom_text(state: AppState, cfg: dict, question: str) -> str:
    """BOM 图谱查询，迁移自 app.py _query_bom_text()。"""
    driver = _get_neo4j_driver(state, cfg)
    if driver is None:
        return ""

    KNOWN_KEYWORDS = [
        "风扇", "压气机", "高压压气机", "低压压气机", "燃烧室",
        "高压涡轮", "低压涡轮", "涡轮", "附件", "尾喷管",
        "叶片", "涡轮盘", "火焰筒", "喷嘴", "机匣", "转子", "静子",
    ]
    keywords = [kw for kw in KNOWN_KEYWORDS if kw in question] or [question[:15]]

    with driver.session() as session:
        lines = []
        seen = set()
        for kw in keywords:
            rows = session.run("""
                MATCH (parent) WHERE parent.part_name CONTAINS $kw
                OPTIONAL MATCH (child)-[:CHILD_OF*1..2]->(parent)
                WITH parent, collect(child) AS children
                RETURN parent.part_name AS module,
                       parent.part_id   AS module_id,
                       parent.spec      AS spec,
                       [c IN children | {
                         name:c.part_name, id:c.part_id,
                         qty:c.qty, unit:c.unit,
                         material:c.material, spec:c.spec, note:c.note
                       }] AS parts
            """, kw=kw).data()

            for r in rows:
                mod = r.get("module", "")
                if not mod or mod in seen:
                    continue
                seen.add(mod)
                lines.append(f"【{mod}】({r.get('module_id','')})")
                if r.get("spec"):
                    lines.append(f"  规格：{r['spec']}")
                for p in (r.get("parts") or []):
                    mat  = f" 材料:{p['material']}" if p.get("material") else ""
                    spec = f" 规格:{p['spec']}"     if p.get("spec") else ""
                    note = f" 备注:{p['note']}"     if p.get("note") else ""
                    lines.append(
                        f"  - {p['name']}({p['id']}) ×{p['qty']}{p['unit']}{mat}{spec}{note}"
                    )
        return "\n".join(lines) if lines else ""
