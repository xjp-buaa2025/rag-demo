"""Tests for backend.pipelines.assembly_scheme.stage2_requirements.run_stage2_requirements."""
from pathlib import Path
from unittest.mock import MagicMock
import json
import pytest
import jsonschema

from backend.pipelines.assembly_scheme.stage2_requirements import (
    run_stage2_requirements,
    PLACEHOLDER_STAGE2,
)
from backend.pipelines.assembly_scheme.skill_loader import SkillRegistry

SKILL_ROOT = Path(__file__).resolve().parents[2] / "skills" / "aero-engine-assembly-scheme"


@pytest.fixture(scope="module")
def loaded_skill():
    reg = SkillRegistry(SKILL_ROOT)
    reg.load()
    return reg


@pytest.fixture
def sample_stage1():
    return {
        "scheme_id": "scheme-20260511-aaaaaa",
        "subject": {
            "system": "PT6A 高压压气机",
            "system_en": "PT6A HPC",
            "scope": ["3 级轴流"],
            "design_intent": "工艺优化",
            "constraints": {"primary": "可靠性", "secondary": "维修性"},
        },
        "kg_snapshot": {
            "part_count": 35,
            "assembly_count": 13,
            "key_interfaces": [],
            "relations_sample": ["isPartOf", "matesWith"],
        },
        "web_search_results": [],
        "vision_notes": "",
        "compliance_scope": ["AS9100D §8.1"],
        "task_card_md": "## 任务说明书\n**目标**：测试\n**范围**：测试\n**边界**：测试\n**约束**：测试\n**已知风险**：测试",
    }


def test_run_stage2_no_llm_returns_placeholder(loaded_skill, sample_stage1):
    result = run_stage2_requirements(
        stage1_payload=sample_stage1,
        skill=loaded_skill,
        llm_client=None,
        rag_searcher=None,
        neo4j_driver=None,
    )
    schema = loaded_skill.schemas["stage2"]
    jsonschema.validate(instance=result, schema=schema)
    assert result["stage1_ref"] == sample_stage1["scheme_id"]
    assert result["user_needs"]
    assert result.get("uncertainty") == "高"


def test_run_stage2_with_llm_uses_response(loaded_skill, sample_stage1):
    mock_resp = {
        "stage1_ref": sample_stage1["scheme_id"],
        "user_needs": [{"id": "U1", "text": "可靠", "weight": 5}],
        "engineering_metrics": [{"id": "M1", "name": "MTBF", "target": ">= 4000h", "linked_needs": ["U1"]}],
        "assembly_features": [{"id": "F1", "name": "扭矩一致", "spec": "Cpk>=1.33", "linked_metrics": ["M1"]}],
        "key_characteristics": [{"id": "KC1", "name": "叶尖间隙", "target": "0.5-1.0 mm", "criticality": "high", "linked_features": ["F1"]}],
        "dfa_score": {"overall": 0.7, "theoretical_min_parts": 25, "actual_parts": 35, "bottlenecks": []},
        "risks": [{"id": "R1", "text": "碰摩", "severity": 4, "linked_kcs": ["KC1"]}],
        "uncertainty": "低",
    }
    mock_llm = MagicMock()
    mock_llm.chat.completions.create.return_value.choices[0].message.content = json.dumps(mock_resp, ensure_ascii=False)
    result = run_stage2_requirements(
        stage1_payload=sample_stage1, skill=loaded_skill, llm_client=mock_llm,
        rag_searcher=None, neo4j_driver=None,
    )
    jsonschema.validate(instance=result, schema=loaded_skill.schemas["stage2"])
    assert result["user_needs"][0]["text"] == "可靠"
    mock_llm.chat.completions.create.assert_called_once()


def test_run_stage2_llm_returns_garbage_falls_back(loaded_skill, sample_stage1):
    mock_llm = MagicMock()
    mock_llm.chat.completions.create.return_value.choices[0].message.content = "not json at all"
    result = run_stage2_requirements(
        stage1_payload=sample_stage1, skill=loaded_skill, llm_client=mock_llm,
        rag_searcher=None, neo4j_driver=None,
    )
    jsonschema.validate(instance=result, schema=loaded_skill.schemas["stage2"])
    assert result.get("uncertainty") == "高"


def test_run_stage2_overrides_stage1_ref_even_if_llm_returns_wrong_id(loaded_skill, sample_stage1):
    bad_resp = {
        "stage1_ref": "scheme-20260101-deadbeef",
        "user_needs": [{"id": "U1", "text": "x", "weight": 1}],
        "engineering_metrics": [{"id": "M1", "name": "x", "target": ">=1", "linked_needs": ["U1"]}],
        "assembly_features": [{"id": "F1", "name": "x", "spec": "x", "linked_metrics": ["M1"]}],
        "key_characteristics": [{"id": "KC1", "name": "x", "target": "x", "criticality": "low", "linked_features": ["F1"]}],
        "dfa_score": {"overall": 0.5, "theoretical_min_parts": 1, "actual_parts": 2, "bottlenecks": []},
        "risks": [{"id": "R1", "text": "x", "severity": 1, "linked_kcs": ["KC1"]}],
    }
    mock_llm = MagicMock()
    mock_llm.chat.completions.create.return_value.choices[0].message.content = json.dumps(bad_resp, ensure_ascii=False)
    result = run_stage2_requirements(
        stage1_payload=sample_stage1, skill=loaded_skill, llm_client=mock_llm,
        rag_searcher=None, neo4j_driver=None,
    )
    assert result["stage1_ref"] == sample_stage1["scheme_id"]


def test_placeholder_validates_against_schema(loaded_skill, sample_stage1):
    p = dict(PLACEHOLDER_STAGE2)
    p["stage1_ref"] = sample_stage1["scheme_id"]
    jsonschema.validate(instance=p, schema=loaded_skill.schemas["stage2"])
