"""
backend/routers/bom.py — BOM 图数据库接口

GET  /bom/status    — Neo4j 连接状态（JSON）
POST /bom/ingest    — BOM Excel → Neo4j 入库（multipart 文件上传 + SSE 日志流）
POST /bom/query     — 关键词查询 BOM 图谱（JSON）

Neo4j 驱动懒加载：首次调用时建立连接，用 state.neo4j_lock 防止并发重复连接。
迁移自 app.py：_get_neo4j()、check_neo4j_status()、run_bom_ingest_ui()、_query_bom_text()
"""

import os
import tempfile
from typing import Optional

import pandas as pd
from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from pydantic import BaseModel

from backend.deps import get_state, get_neo4j_cfg
from backend.state import AppState
from backend.sse import log_gen_to_sse

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

@router.post("/ingest", summary="BOM Excel 入库（SSE）")
def bom_ingest(
    request: Request,
    file: Optional[UploadFile] = File(default=None),
    clear_first: bool = Form(default=False),
    state: AppState = Depends(get_state),
    cfg: dict = Depends(get_neo4j_cfg),
):
    """
    上传 BOM Excel 文件（可选，不传则用默认 test_bom.xlsx），写入 Neo4j。
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

        # 读取 Excel
        yield emit("📖 读取 BOM 表…")
        try:
            df = pd.read_excel(filepath, dtype=str)
            df.columns = [c.strip().lower() for c in df.columns]
            for col in ("material", "weight_kg", "spec", "note"):
                if col not in df.columns:
                    df[col] = ""
            df = df.dropna(subset=["level_code", "part_id"])
            for col in df.columns:
                df[col] = df[col].fillna("").astype(str).str.strip()
            df["qty"] = pd.to_numeric(df["qty"], errors="coerce").fillna(1).astype(int)
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
