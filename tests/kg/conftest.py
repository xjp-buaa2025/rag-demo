"""
tests/kg/conftest.py

KG Harness 公共 fixture 定义。所有层（层一/二/三）共享此文件。

Fixture 层级：
  neo4j_cfg      — session 级，从环境变量读取连接参数
  neo4j_driver   — session 级，连接 Neo4j，失败则 skip 整个会话
  neo4j_session  — function 级，从 driver 开启 session，自动关闭
  bom_dataframe  — session 级，加载 fixtures/sample_bom.csv
  bom_part_ids   — session 级，从 DataFrame 提取 part_id 集合
  golden_triples — session 级，从 fixtures/golden_triples.json 加载

跳过策略：
  - Neo4j 不可达 → pytest.skip 整个会话（不阻塞 CI）
  - fixture 文件不存在 → pytest.xfail（非阻塞性失败）
"""

import json
import os
from pathlib import Path

import pandas as pd
import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


# ── Neo4j 连接 ────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def neo4j_cfg():
    """从环境变量读取 Neo4j 连接参数，与 backend/main.py lifespan 保持一致。"""
    return {
        "uri":  os.getenv("NEO4J_URI",  "bolt://localhost:7687"),
        "user": os.getenv("NEO4J_USER", "neo4j"),
        "pass": os.getenv("NEO4J_PASS", "password"),
    }


@pytest.fixture(scope="session")
def neo4j_driver(neo4j_cfg):
    """
    会话级 Neo4j driver。
    若连接失败，pytest.skip 整个会话，避免每个测试重复报告同一错误。
    """
    try:
        from neo4j import GraphDatabase
        from neo4j.exceptions import ServiceUnavailable

        driver = GraphDatabase.driver(
            neo4j_cfg["uri"],
            auth=(neo4j_cfg["user"], neo4j_cfg["pass"]),
        )
        driver.verify_connectivity()
        yield driver
        driver.close()
    except ImportError:
        pytest.skip("neo4j Python driver 未安装：pip install neo4j")
    except Exception as e:
        pytest.skip(f"Neo4j 不可达，跳过所有 KG 测试：{e}")


@pytest.fixture(scope="function")
def neo4j_session(neo4j_driver):
    """函数级 session，测试结束后自动关闭，防止连接泄漏。"""
    with neo4j_driver.session() as session:
        yield session


# ── BOM Fixture ───────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def bom_dataframe():
    """
    从 fixtures/sample_bom.csv 加载 BOM 数据。

    CSV 必须包含列：part_id, part_name（其余列可选）。
    文件不存在时标记为 xfail（非阻塞性失败，不影响层一测试）。
    """
    csv_path = FIXTURES_DIR / "sample_bom.csv"
    if not csv_path.exists():
        pytest.xfail(
            f"BOM fixture 不存在：{csv_path}\n"
            f"请从真实 BOM 中截取 30-50 行创建该文件（含 part_id, part_name 列）"
        )
    df = pd.read_csv(csv_path, dtype=str).fillna("")
    assert "part_id"   in df.columns, "sample_bom.csv 缺少 part_id 列"
    assert "part_name" in df.columns, "sample_bom.csv 缺少 part_name 列"
    return df


@pytest.fixture(scope="session")
def bom_part_ids(bom_dataframe):
    """从 BOM DataFrame 提取 part_id 集合（去空值、去空格）。"""
    return set(bom_dataframe["part_id"].str.strip().replace("", pd.NA).dropna().tolist())


# ── Golden Set Fixture ────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def golden_triples():
    """
    从 fixtures/golden_triples.json 加载人工标注的黄金三元组。

    返回：list[dict]，每条含 head / relation / tail 字段。
    文件不存在时标记为 xfail（非阻塞性失败，不影响层一/二测试）。
    """
    json_path = FIXTURES_DIR / "golden_triples.json"
    if not json_path.exists():
        pytest.xfail(
            f"Golden set 不存在：{json_path}\n"
            f"请参考 fixtures/README.md 格式，人工标注 30 条三元组"
        )
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, list), "golden_triples.json 应为 JSON 数组"
    assert len(data) > 0, "golden_triples.json 不能为空数组"
    for i, item in enumerate(data):
        assert "head"     in item, f"第 {i} 条三元组缺少 head 字段"
        assert "relation" in item, f"第 {i} 条三元组缺少 relation 字段"
        assert "tail"     in item, f"第 {i} 条三元组缺少 tail 字段"
    return data
