"""
tests/kg/test_postprocess.py

后处理管道测试，分两组：
  1. 单元测试 — 纯内存，测试各步骤行为
  2. 验收测试 — 读取真实 stage2_manual_triples.json，断言 Plan D 验收标准
"""

import json
from pathlib import Path

import pytest

from backend.pipelines.kg_postprocess import (
    _filter_confidence,
    _normalize_entity,
    _filter_ontology,
    _dedup_triples,
    postprocess_triples,
)

# ─── 单元测试 ─────────────────────────────────────────────────────────────────


def test_confidence_filter_removes_below_threshold():
    """confidence < 0.3 的三元组被过滤，边界值 0.3 保留。"""
    triples = [
        {"head": "A", "relation": "r", "tail": "B", "confidence": 0.1},
        {"head": "C", "relation": "r", "tail": "D", "confidence": 0.3},
        {"head": "E", "relation": "r", "tail": "F", "confidence": 0.9},
    ]
    kept, removed = _filter_confidence(triples)
    assert removed == 1
    assert len(kept) == 2
    assert all(t["confidence"] >= 0.3 for t in kept)


def test_confidence_filter_missing_field_treated_as_zero():
    """缺少 confidence 字段的三元组视为 0，应被过滤。"""
    triples = [{"head": "A", "relation": "r", "tail": "B"}]
    kept, removed = _filter_confidence(triples)
    assert removed == 1
    assert kept == []


def test_normalize_entity_strips_whitespace():
    assert _normalize_entity("  GAS GENERATOR  ") == "GAS GENERATOR"


def test_normalize_entity_collapses_internal_spaces():
    assert _normalize_entity("GAS   GENERATOR  CASE") == "GAS GENERATOR CASE"


def test_normalize_entity_replaces_chinese_punctuation():
    assert _normalize_entity("组件，零件。") == "组件,零件."


def test_ontology_precedes_violation_removed():
    """precedes 关系 head/tail 非 Procedure 时被删除。"""
    triples = [
        {
            "head": "COMPRESSOR ROTOR",
            "relation": "precedes",
            "tail": "INSPECTION STEP",
            "confidence": 0.9,
            "head_type": "Part",       # 违规：应为 Procedure
            "tail_type": "Procedure",
        },
    ]
    kept, removed = _filter_ontology(triples)
    assert removed == 1
    assert kept == []


def test_ontology_valid_precedes_passes():
    """合规的 precedes 三元组（head/tail 均为 Procedure）保留。"""
    triples = [
        {
            "head": "STEP 1",
            "relation": "precedes",
            "tail": "STEP 2",
            "confidence": 0.8,
            "head_type": "Procedure",
            "tail_type": "Procedure",
        },
    ]
    kept, removed = _filter_ontology(triples)
    assert removed == 0
    assert len(kept) == 1


def test_ontology_unknown_relation_passes():
    """未定义的关系类型放行（不阻断）。"""
    triples = [
        {
            "head": "X",
            "relation": "unknownRelation",
            "tail": "Y",
            "confidence": 0.7,
            "head_type": "Whatever",
            "tail_type": "Whatever",
        },
    ]
    kept, removed = _filter_ontology(triples)
    assert removed == 0
    assert len(kept) == 1


def test_dedup_keeps_highest_confidence():
    """同 (head, relation, tail) key 保留置信度最高的一条。"""
    triples = [
        {"head": "A", "relation": "r", "tail": "B", "confidence": 0.5},
        {"head": "A", "relation": "r", "tail": "B", "confidence": 0.9},
        {"head": "A", "relation": "r", "tail": "B", "confidence": 0.3},
    ]
    kept, removed = _dedup_triples(triples)
    assert removed == 2
    assert len(kept) == 1
    assert kept[0]["confidence"] == 0.9


def test_dedup_case_insensitive_key():
    """去重时 head/tail 大小写不敏感（'gas generator' 和 'GAS GENERATOR' 视为同一实体）。"""
    triples = [
        {"head": "gas generator", "relation": "r", "tail": "casing", "confidence": 0.6},
        {"head": "GAS GENERATOR", "relation": "r", "tail": "CASING", "confidence": 0.8},
    ]
    kept, removed = _dedup_triples(triples)
    assert removed == 1
    assert kept[0]["confidence"] == 0.8


def test_pipeline_stats_fields_complete():
    """postprocess_triples 返回的 stats 包含所有必要字段。"""
    triples = [
        {"head": "A", "relation": "matesWith", "tail": "B",
         "confidence": 0.8, "head_type": "Part", "tail_type": "Part"},
    ]
    _, stats = postprocess_triples(triples)
    required_keys = {
        "original", "removed_low_confidence", "removed_ontology_violation",
        "removed_duplicates", "final", "total_removed", "retention_rate",
    }
    assert required_keys.issubset(stats.keys())


def test_pipeline_empty_input():
    """空列表输入时返回空列表，retention_rate 为 1.0。"""
    cleaned, stats = postprocess_triples([])
    assert cleaned == []
    assert stats["retention_rate"] == 1.0
    assert stats["original"] == 0
    assert stats["final"] == 0


# ─── 验收测试 — 读取真实 JSON ─────────────────────────────────────────────────

STAGE2_PATH = Path(__file__).parents[2] / "storage" / "kg_stages" / "stage2_manual_triples.json"


@pytest.fixture(scope="module")
def manual_triples():
    if not STAGE2_PATH.exists():
        pytest.skip(f"stage2_manual_triples.json 不存在：{STAGE2_PATH}")
    data = json.loads(STAGE2_PATH.read_text(encoding="utf-8"))
    triples = data.get("triples", [])
    if not triples:
        pytest.skip("stage2_manual_triples.json 的 triples 数组为空")
    return triples


def test_manual_stage_retention_rate(manual_triples):
    """
    Plan D 验收标准：stage2_manual 经完整后处理后，保留率 ≤ 0.85（减少 ≥ 15%）。
    若当前数据集减少率不足，说明三元组质量已经较高或数据量过少，
    可手动确认后调整阈值；但默认应达标。
    """
    _, stats = postprocess_triples(manual_triples, skip_ontology=False)
    assert stats["retention_rate"] <= 0.85, (
        f"后处理保留率 {stats['retention_rate']:.2%} 超过 85%，"
        f"未达到 Plan D 要求的 ≥15% 减少量。"
        f"统计详情：{stats}"
    )


def test_no_precedes_ontology_violation(manual_triples):
    """
    Plan D 验收标准：清洗后所有 precedes 关系的 head_type 和 tail_type 均为 Procedure。
    """
    cleaned, _ = postprocess_triples(manual_triples, skip_ontology=False)
    violations = [
        t for t in cleaned
        if t.get("relation") == "precedes"
        and (t.get("head_type") != "Procedure" or t.get("tail_type") != "Procedure")
    ]
    assert violations == [], (
        f"发现 {len(violations)} 条 precedes 本体违规残留：\n"
        + "\n".join(
            f"  head_type={v.get('head_type')} tail_type={v.get('tail_type')} "
            f"head={v.get('head')} tail={v.get('tail')}"
            for v in violations[:5]
        )
    )
