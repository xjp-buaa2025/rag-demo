"""
bom_ingest.py — BOM 表解析并写入 Neo4j 图数据库

职责：
  读取 data/test_bom.xlsx（或通过参数指定其他 BOM 文件），
  将零件层级关系和属性写入 Neo4j，建立：
    - 节点：Assembly（组件）、Part（零件）、Standard（标准件）
    - 关系：CHILD_OF（层级隶属）

BOM 表格式要求（Excel 列名，顺序不限）：
  level_code  : 层级编号，如 1 / 1.1 / 1.1.2
  part_id     : 零件唯一编号
  part_name   : 零件中文名
  part_name_en: 零件英文名
  category    : Assembly / Part / Standard
  qty         : 数量（整数）
  unit        : 单位（件/套/台…）
  material    : 材料牌号（可为空）
  weight_kg   : 重量 kg（可为空）
  spec        : 规格说明（可为空）
  note        : 备注（可为空）

运行方式：
  PYTHONUTF8=1 python bom_ingest.py
  PYTHONUTF8=1 python bom_ingest.py --file data/my_bom.xlsx
  PYTHONUTF8=1 python bom_ingest.py --clear   # 清空后重建

Neo4j 连接配置（.env 文件）：
  NEO4J_URI=bolt://localhost:7687
  NEO4J_USER=neo4j
  NEO4J_PASS=password

详见 PROJECT_GUIDE.md § BOM-GraphRAG
"""

import os
import sys
import argparse
import pandas as pd
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

# ── 配置 ──────────────────────────────────────────────────────────────────────
NEO4J_URI  = os.getenv("NEO4J_URI",  "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASS = os.getenv("NEO4J_PASS", "password")
DEFAULT_BOM = os.path.join(os.path.dirname(__file__), "data", "test_bom.xlsx")

REQUIRED_COLUMNS = {
    "level_code", "part_id", "part_name", "part_name_en",
    "category", "qty", "unit",
}
OPTIONAL_COLUMNS = {"material", "weight_kg", "spec", "note"}
ALL_COLUMNS = REQUIRED_COLUMNS | OPTIONAL_COLUMNS

# ── 数据读取 ──────────────────────────────────────────────────────────────────

def load_bom(filepath: str) -> pd.DataFrame:
    """加载并校验 BOM Excel，返回清洗后的 DataFrame。"""
    if not os.path.exists(filepath):
        print(f"[错误] 文件不存在：{filepath}")
        sys.exit(1)

    df = pd.read_excel(filepath, dtype=str)
    df.columns = [c.strip().lower() for c in df.columns]

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        print(f"[错误] BOM 文件缺少必要列：{missing}")
        sys.exit(1)

    # 补全可选列（缺失时填空字符串）
    for col in OPTIONAL_COLUMNS:
        if col not in df.columns:
            df[col] = ""

    # 清洗：去除空行、去除首尾空白
    df = df.dropna(subset=["level_code", "part_id"])
    for col in df.columns:
        df[col] = df[col].fillna("").astype(str).str.strip()

    # level_code 统一转字符串（防止 1.0 → '1.0'）
    df["level_code"] = df["level_code"].apply(_normalize_level)
    df["qty"] = pd.to_numeric(df["qty"], errors="coerce").fillna(1).astype(int)

    print(f"[BOM] 读取成功：{len(df)} 条零件记录，来自 {filepath}")
    return df


def _normalize_level(val: str) -> str:
    """将 '1.0' → '1'，'1.1.0' → '1.1'，正常值不变。"""
    parts = val.split(".")
    parts = [p.lstrip("0") or "0" for p in parts]
    # 移除末尾 '0'（如 '1.0' → ['1','0'] → '1'）
    while len(parts) > 1 and parts[-1] == "0":
        parts.pop()
    return ".".join(parts)


# ── Neo4j 写入 ────────────────────────────────────────────────────────────────

def build_schema(session):
    """建立约束与索引（幂等）。"""
    # 唯一约束（每类节点各一条，Neo4j 5.x 语法）
    for label in ("Assembly", "Part", "Standard"):
        session.run(f"""
            CREATE CONSTRAINT IF NOT EXISTS FOR (n:{label})
            REQUIRE n.part_id IS UNIQUE
        """)
    print("[Neo4j] Schema 约束已就绪")


def clear_bom_data(session):
    """清空所有 BOM 节点和关系（保留其他数据不受影响）。"""
    result = session.run("""
        MATCH (n) WHERE n:Assembly OR n:Part OR n:Standard
        DETACH DELETE n
        RETURN count(n) AS deleted
    """)
    count = result.single()["deleted"]
    print(f"[Neo4j] 已清空旧数据，删除 {count} 个节点")


def ingest_nodes(session, df: pd.DataFrame):
    """批量写入节点（MERGE 确保幂等）。"""
    records = df.to_dict(orient="records")
    # 按 category 分组写入，方便设置不同 label
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
                n.weight_kg    = CASE row.weight_kg
                                   WHEN '' THEN null
                                   ELSE toFloat(row.weight_kg) END,
                n.spec         = row.spec,
                n.note         = row.note
        """, rows=batch)
        print(f"[Neo4j] 写入 {category} 节点：{len(batch)} 个")


def ingest_relations(session, df: pd.DataFrame):
    """根据 level_code 建立 CHILD_OF 关系。"""
    # 建立 level_code → part_id 的映射
    level_map = dict(zip(df["level_code"], df["part_id"]))

    edges = []
    for _, row in df.iterrows():
        code = row["level_code"]
        if "." not in code:
            continue  # 顶层节点无父节点
        parent_code = ".".join(code.split(".")[:-1])
        parent_id = level_map.get(parent_code)
        if parent_id is None:
            print(f"[警告] 找不到父节点 level_code={parent_code}（子节点 {row['part_id']}），跳过")
            continue
        edges.append({"child_id": row["part_id"], "parent_id": parent_id})

    if edges:
        session.run("""
            UNWIND $edges AS e
            MATCH (child  {part_id: e.child_id})
            MATCH (parent {part_id: e.parent_id})
            MERGE (child)-[:CHILD_OF]->(parent)
        """, edges=edges)
    print(f"[Neo4j] 建立 CHILD_OF 关系：{len(edges)} 条")


def print_stats(session):
    """打印图谱统计信息。"""
    r = session.run("""
        MATCH (n) WHERE n:Assembly OR n:Part OR n:Standard
        RETURN
          count(CASE WHEN n:Assembly THEN 1 END) AS assemblies,
          count(CASE WHEN n:Part     THEN 1 END) AS parts,
          count(CASE WHEN n:Standard THEN 1 END) AS standards
    """).single()
    edges = session.run("MATCH ()-[r:CHILD_OF]->() RETURN count(r) AS cnt").single()["cnt"]
    print(f"\n{'─'*45}")
    print(f"  图谱统计")
    print(f"  Assembly（组件） : {r['assemblies']:>4} 个")
    print(f"  Part    （零件） : {r['parts']:>4} 个")
    print(f"  Standard（标准件）: {r['standards']:>4} 个")
    print(f"  CHILD_OF 关系    : {edges:>4} 条")
    print(f"{'─'*45}\n")


# ── 主流程 ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="BOM → Neo4j 图谱入库")
    parser.add_argument("--file",  default=DEFAULT_BOM, help="BOM Excel 文件路径")
    parser.add_argument("--clear", action="store_true",  help="清空后重建")
    args = parser.parse_args()

    # 1. 读取 BOM
    df = load_bom(args.file)

    # 2. 连接 Neo4j
    print(f"\n[Neo4j] 连接 {NEO4J_URI} …")
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
        driver.verify_connectivity()
        print("[Neo4j] 连接成功")
    except Exception as e:
        print(f"[错误] Neo4j 连接失败：{e}")
        print("请确认 Docker 已启动：docker start neo4j")
        sys.exit(1)

    with driver.session() as session:
        # 3. 建立 Schema
        build_schema(session)

        # 4. 可选清空
        if args.clear:
            clear_bom_data(session)

        # 5. 写入节点
        ingest_nodes(session, df)

        # 6. 建立关系
        ingest_relations(session, df)

        # 7. 打印统计
        print_stats(session)

    driver.close()
    print("[完成] BOM 已成功写入 Neo4j。")
    print(f"  浏览器可视化：http://localhost:7474")
    print(f"  示例 Cypher  ：MATCH (n)-[:CHILD_OF*]->(r {{part_name:'涡扇发动机整机'}}) RETURN n,r")


if __name__ == "__main__":
    main()
