"""Tests for backend.pipelines.assembly_scheme.stage5_review.run_stage5_review."""
from pathlib import Path
from unittest.mock import MagicMock
import json
import pytest
import jsonschema

from backend.pipelines.assembly_scheme.stage5_review import (
    run_stage5_review,
    PLACEHOLDER_STAGE5,
)
from backend.pipelines.assembly_scheme.skill_loader import SkillRegistry

SKILL_ROOT = Path(__file__).resolve().parents[2] / "skills" / "aero-engine-assembly-scheme"


@pytest.fixture(scope="module")
def loaded_skill():
    reg = SkillRegistry(SKILL_ROOT)
    reg.load()
    return reg


@pytest.fixture
def sample_stage4b():
    return {
        "stage4a_ref": "scheme-20260511-aaaaaa",
        "tools": [
            {"id": "T01", "name": "定位夹具 JIG-001", "category": "special",
             "cost_tier": "高", "used_in_procedures": ["P01"]},
            {"id": "T02", "name": "扭矩扳手", "category": "generic",
             "cost_tier": "低", "used_in_procedures": ["P02"]},
        ],
        "tooling_constraints": [],
        "dfa_tooling_score": 0.5,
        "uncertainty": "中",
    }


@pytest.fixture
def sample_stage4a():
    return {
        "stage3_ref": "scheme-20260511-aaaaaa",
        "procedures": [
            {"id": "P01", "name": "后轴承座定位装夹", "seq_no": 1, "depends_on": [],
             "parts_involved": ["后轴承座"], "tooling": ["定位夹具 JIG-001"],
             "spec_values": [{"param": "定位精度", "value": "±0.02mm"}]},
            {"id": "P02", "name": "螺栓紧固", "seq_no": 2, "depends_on": ["P01"],
             "parts_involved": ["法兰螺栓"], "tooling": ["扭矩扳手"],
             "spec_values": [{"param": "力矩", "value": "25 N·m"}]},
        ],
        "topology": {"sequence": ["P01", "P02"], "method": "DFA-heuristic", "dfa_efficiency": 0.72},
        "uncertainty": "中",
    }


@pytest.fixture
def sample_stage2():
    return {
        "stage1_ref": "scheme-20260511-aaaaaa",
        "user_needs": [{"id": "U1", "text": "高可靠性", "weight": 5}],
        "engineering_metrics": [{"id": "M1", "name": "叶尖间隙", "target": "0.3mm", "linked_needs": ["U1"]}],
        "assembly_features": [{"id": "F1", "name": "转子定心精度", "spec": "±0.02mm", "linked_metrics": ["M1"]}],
        "key_characteristics": [
            {"id": "KC1", "name": "叶尖间隙", "target": "0.3±0.05mm", "criticality": "high"},
            {"id": "KC2", "name": "轴向预紧力", "target": "2000±100N", "criticality": "medium"},
        ],
        "dfa_score": {"overall": 0.72, "theoretical_min_parts": 5, "actual_parts": 7, "bottlenecks": []},
        "risks": [{"id": "R1", "text": "叶尖间隙超差风险", "severity": 4}],
        "uncertainty": "中",
    }


def _valid_llm_resp(scheme_id: str) -> dict:
    return {
        "stage4b_ref": scheme_id,
        "review_panel": [
            {"role": "工艺工程师", "findings": ["工序 P01 定位精度满足要求"], "severity_issues": []},
            {"role": "质量工程师", "findings": ["KC1 叶尖间隙有 QC 检查点覆盖"], "severity_issues": []},
            {"role": "设计工程师", "findings": ["S2 需求 M1 已在工序中体现"], "severity_issues": []},
        ],
        "kc_traceability_matrix": [
            {"kc_id": "KC1", "kc_name": "叶尖间隙", "procedures": ["P01"],
             "qc_checkpoints": ["叶尖间隙测量（游标卡尺）"], "covered": True},
            {"kc_id": "KC2", "kc_name": "轴向预紧力", "procedures": ["P02"],
             "qc_checkpoints": ["轴向力矩核验"], "covered": True},
        ],
        "overall_score": 4.0,
        "recommendation": "approved_with_revision",
        "iterations": [],
        "uncertainty": "中",
    }


def test_run_stage5_no_llm_returns_placeholder(loaded_skill, sample_stage4b, sample_stage4a, sample_stage2):
    result = run_stage5_review(
        stage4b_payload=sample_stage4b,
        stage4a_payload=sample_stage4a,
        stage2_payload=sample_stage2,
        skill=loaded_skill,
        llm_client=None,
    )
    jsonschema.validate(instance=result, schema=loaded_skill.schemas["stage5"])
    assert result["stage4b_ref"] == sample_stage4b["stage4a_ref"]
    assert result["uncertainty"] == "高"
    assert result["recommendation"] in ("approved_with_revision", "rejected")
    assert len(result["review_panel"]) == 3


def test_run_stage5_with_valid_llm_output(loaded_skill, sample_stage4b, sample_stage4a, sample_stage2):
    scheme_id = sample_stage4b["stage4a_ref"]
    mock_llm = MagicMock()
    mock_llm.chat.completions.create.return_value.choices[0].message.content = (
        json.dumps(_valid_llm_resp(scheme_id), ensure_ascii=False)
    )
    result = run_stage5_review(
        stage4b_payload=sample_stage4b,
        stage4a_payload=sample_stage4a,
        stage2_payload=sample_stage2,
        skill=loaded_skill,
        llm_client=mock_llm,
    )
    jsonschema.validate(instance=result, schema=loaded_skill.schemas["stage5"])
    assert result["stage4b_ref"] == scheme_id
    assert result["overall_score"] == pytest.approx(4.0, abs=0.01)
    assert len(result["kc_traceability_matrix"]) == 2


def test_run_stage5_bad_json_falls_back(loaded_skill, sample_stage4b, sample_stage4a, sample_stage2):
    mock_llm = MagicMock()
    mock_llm.chat.completions.create.return_value.choices[0].message.content = "not valid json"
    result = run_stage5_review(
        stage4b_payload=sample_stage4b,
        stage4a_payload=sample_stage4a,
        stage2_payload=sample_stage2,
        skill=loaded_skill,
        llm_client=mock_llm,
    )
    jsonschema.validate(instance=result, schema=loaded_skill.schemas["stage5"])
    assert result["uncertainty"] == "高"


def test_run_stage5_high_severity_with_approved_fails_crossvalidate(loaded_skill, sample_stage4b, sample_stage4a, sample_stage2):
    """If LLM outputs approved + high severity issue, cross_validate rejects → PLACEHOLDER."""
    scheme_id = sample_stage4b["stage4a_ref"]
    bad_resp = _valid_llm_resp(scheme_id)
    bad_resp["recommendation"] = "approved"
    bad_resp["review_panel"][0]["severity_issues"] = [
        {"issue": "工序 P02 力矩超差风险极高", "severity": "high", "iterate_to": "4a"}
    ]
    mock_llm = MagicMock()
    mock_llm.chat.completions.create.return_value.choices[0].message.content = (
        json.dumps(bad_resp, ensure_ascii=False)
    )
    result = run_stage5_review(
        stage4b_payload=sample_stage4b,
        stage4a_payload=sample_stage4a,
        stage2_payload=sample_stage2,
        skill=loaded_skill,
        llm_client=mock_llm,
    )
    jsonschema.validate(instance=result, schema=loaded_skill.schemas["stage5"])
    assert result["uncertainty"] == "高"


def test_run_stage5_schema_fail_falls_back(loaded_skill, sample_stage4b, sample_stage4a, sample_stage2):
    """LLM returns JSON that fails schema (wrong recommendation value)."""
    scheme_id = sample_stage4b["stage4a_ref"]
    bad_resp = _valid_llm_resp(scheme_id)
    bad_resp["recommendation"] = "maybe"  # not in enum
    mock_llm = MagicMock()
    mock_llm.chat.completions.create.return_value.choices[0].message.content = (
        json.dumps(bad_resp, ensure_ascii=False)
    )
    result = run_stage5_review(
        stage4b_payload=sample_stage4b,
        stage4a_payload=sample_stage4a,
        stage2_payload=sample_stage2,
        skill=loaded_skill,
        llm_client=mock_llm,
    )
    jsonschema.validate(instance=result, schema=loaded_skill.schemas["stage5"])
    assert result["uncertainty"] == "高"


def test_placeholder_stage5_validates(loaded_skill, sample_stage4b):
    p = json.loads(json.dumps(PLACEHOLDER_STAGE5, ensure_ascii=False))
    p["stage4b_ref"] = sample_stage4b["stage4a_ref"]
    jsonschema.validate(instance=p, schema=loaded_skill.schemas["stage5"])


def test_run_stage5_fence_stripped_json(loaded_skill, sample_stage4b, sample_stage4a, sample_stage2):
    """LLM wraps output in ```json...``` — should be stripped and parsed correctly."""
    scheme_id = sample_stage4b["stage4a_ref"]
    raw = "```json\n" + json.dumps(_valid_llm_resp(scheme_id), ensure_ascii=False) + "\n```"
    mock_llm = MagicMock()
    mock_llm.chat.completions.create.return_value.choices[0].message.content = raw
    result = run_stage5_review(
        stage4b_payload=sample_stage4b,
        stage4a_payload=sample_stage4a,
        stage2_payload=sample_stage2,
        skill=loaded_skill,
        llm_client=mock_llm,
    )
    jsonschema.validate(instance=result, schema=loaded_skill.schemas["stage5"])
    assert result["stage4b_ref"] == scheme_id


def test_run_stage5_llm_exception_falls_back(loaded_skill, sample_stage4b, sample_stage4a, sample_stage2):
    """LLM raises exception → PLACEHOLDER."""
    mock_llm = MagicMock()
    mock_llm.chat.completions.create.side_effect = RuntimeError("API timeout")
    result = run_stage5_review(
        stage4b_payload=sample_stage4b,
        stage4a_payload=sample_stage4a,
        stage2_payload=sample_stage2,
        skill=loaded_skill,
        llm_client=mock_llm,
    )
    jsonschema.validate(instance=result, schema=loaded_skill.schemas["stage5"])
    assert result["uncertainty"] == "高"
