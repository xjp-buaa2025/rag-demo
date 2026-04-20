import pytest
from backend.pipelines.kg_report import generate_stage_report
from backend.kg_storage import StageReport

BOM_TRIPLES = {
    "entities": [
        {"id": "P1", "name": "ROTOR", "type": "Assembly"},
        {"id": "P2", "name": "BOLT", "type": "Part"},
        {"id": "P3", "name": "SEAL", "type": "Part"},
    ],
    "triples": [
        {"head": "BOLT", "relation": "isPartOf", "tail": "ROTOR", "confidence": 1.0, "source": "BOM", "head_type": "Part", "tail_type": "Assembly"},
        {"head": "SEAL", "relation": "isPartOf", "tail": "ROTOR", "confidence": 0.9, "source": "BOM", "head_type": "Part", "tail_type": "Assembly"},
        {"head": "BOLT_ALT", "relation": "interchangesWith", "tail": "BOLT", "confidence": 0.3, "source": "BOM", "head_type": "Part", "tail_type": "Part"},
    ],
    "stats": {"entities_count": 3, "triples_count": 3},
    "generated_at": "2026-04-20T00:00:00Z",
}

def test_generate_bom_report_stats():
    report = generate_stage_report("bom", BOM_TRIPLES, prev_data=None)
    assert isinstance(report, StageReport)
    assert report.stage == "bom"
    assert report.stats.entities_count == 3
    assert report.stats.triples_count == 3
    assert report.stats.relation_breakdown["isPartOf"] == 2
    assert report.stats.low_confidence_count == 1  # confidence 0.3 < 0.5

def test_isolated_entities_detected():
    report = generate_stage_report("bom", BOM_TRIPLES, prev_data=None)
    assert report.stats.isolated_entities_count == 0  # P1/P2/P3 都出现在三元组中

def test_confidence_histogram():
    report = generate_stage_report("bom", BOM_TRIPLES, prev_data=None)
    hist = report.stats.confidence_histogram
    assert len(hist) == 5  # 5个区间
    assert abs(sum(hist) - 1.0) < 1e-6  # 总和为1

def test_bom_coverage_for_manual():
    manual_data = {
        "triples": [
            {"head": "ROTOR", "relation": "matesWith", "tail": "BLADE", "confidence": 0.8, "source": "Manual",
             "head_type": "Assembly", "tail_type": "Part", "head_bom_id": "P1"},
        ],
        "stats": {},
        "generated_at": "2026-04-20T01:00:00Z",
    }
    report = generate_stage_report("manual", manual_data, prev_data=None, bom_data=BOM_TRIPLES)
    assert report.stats.bom_coverage_ratio is not None
    assert 0 < report.stats.bom_coverage_ratio <= 1.0

def test_diff_when_prev_exists():
    prev = {**BOM_TRIPLES, "triples": BOM_TRIPLES["triples"][:2]}
    report = generate_stage_report("bom", BOM_TRIPLES, prev_data=prev)
    assert report.diff is not None
    assert len(report.diff.added_triples) == 1  # 第3条是新增的
