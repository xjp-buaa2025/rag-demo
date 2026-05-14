"""Tests for backend.pipelines.assembly_scheme.stage3_concept.run_stage3_concept."""
from pathlib import Path
from unittest.mock import MagicMock
import json
import pytest
import jsonschema

from backend.pipelines.assembly_scheme.stage3_concept import (
    run_stage3_concept,
    PLACEHOLDER_STAGE3,
    query_kg_subgraph,
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
            "constraints": {"primary": "可靠性"},
        },
        "kg_snapshot": {"part_count": 35, "assembly_count": 13, "key_interfaces": [], "relations_sample": []},
        "web_search_results": [],
        "vision_notes": "",
        "compliance_scope": ["AS9100D §8.1"],
        "task_card_md": "## 任务说明书\n**目标**：测试",
    }


@pytest.fixture
def sample_stage2():
    return {
        "stage1_ref": "scheme-20260511-aaaaaa",
        "user_needs": [{"id": "U1", "text": "可靠", "weight": 5}],
        "engineering_metrics": [{"id": "M1", "name": "MTBF", "target": ">=4000h", "linked_needs": ["U1"]}],
        "assembly_features": [{"id": "F1", "name": "扭矩", "spec": "Cpk>=1.33", "linked_metrics": ["M1"]}],
        "key_characteristics": [{"id": "KC1", "name": "叶尖间隙", "target": "0.5-1.0mm", "criticality": "high", "linked_features": ["F1"]}],
        "dfa_score": {"overall": 0.7, "theoretical_min_parts": 25, "actual_parts": 35, "bottlenecks": []},
        "risks": [{"id": "R1", "text": "碰摩", "severity": 4, "linked_kcs": ["KC1"]}],
    }


def test_run_stage3_no_llm_no_kg_returns_placeholder(loaded_skill, sample_stage1, sample_stage2):
    result = run_stage3_concept(
        stage1_payload=sample_stage1,
        stage2_payload=sample_stage2,
        skill=loaded_skill,
        llm_client=None,
        neo4j_driver=None,
    )
    jsonschema.validate(instance=result, schema=loaded_skill.schemas["stage3"])
    assert result["stage1_ref"] == sample_stage1["scheme_id"]
    assert result["stage2_ref"] == sample_stage1["scheme_id"]
    assert len(result["candidate_architectures"]) >= 2
    assert result["recommended"] in {a["id"] for a in result["candidate_architectures"]}


def test_query_kg_subgraph_no_driver_returns_empty():
    sg = query_kg_subgraph(None, "PT6A HPC")
    assert sg == {"modules": [], "matesWith": [], "adjacentTo": []}


def test_query_kg_subgraph_handles_driver_exception():
    bad_driver = MagicMock()
    bad_driver.session.side_effect = RuntimeError("neo4j down")
    sg = query_kg_subgraph(bad_driver, "PT6A HPC")
    assert sg["modules"] == []


def test_run_stage3_with_llm(loaded_skill, sample_stage1, sample_stage2):
    mock_resp = {
        "stage1_ref": sample_stage1["scheme_id"],
        "stage2_ref": sample_stage1["scheme_id"],
        "candidate_architectures": [
            {
                "id": "A1", "name": "三段式",
                "modules": [{"id": "M1", "name": "前段", "parts": ["P1"]}],
                "key_interfaces": [{"from": "M1", "to": "M1", "type": "test"}],
                "assembly_simulation": {"reachability_pass": True, "interference_count": 0, "method": "KG-static"},
                "datum_consistency": {"unified": True, "issues": []},
                "pros": ["可拆"], "cons": ["重"],
                "fit_score_to_metrics": 0.8,
            },
            {
                "id": "A2", "name": "整体式",
                "modules": [{"id": "M1", "name": "整体", "parts": ["P1"]}],
                "key_interfaces": [{"from": "M1", "to": "M1", "type": "test"}],
                "assembly_simulation": {"reachability_pass": True, "interference_count": 0, "method": "KG-static"},
                "datum_consistency": {"unified": True, "issues": []},
                "pros": ["紧凑"], "cons": ["难修"],
                "fit_score_to_metrics": 0.6,
            },
        ],
        "recommended": "A1",
        "rationale_md": "推荐 A1：可拆 vs 难修，可拆胜出。\n第二行。\n第三行。",
        "uncertainty": "低",
    }
    mock_llm = MagicMock()
    mock_llm.chat.completions.create.return_value.choices[0].message.content = json.dumps(mock_resp, ensure_ascii=False)
    result = run_stage3_concept(
        stage1_payload=sample_stage1, stage2_payload=sample_stage2,
        skill=loaded_skill, llm_client=mock_llm, neo4j_driver=None,
    )
    jsonschema.validate(instance=result, schema=loaded_skill.schemas["stage3"])
    assert result["recommended"] == "A1"
    assert len(result["candidate_architectures"]) == 2


def test_run_stage3_rejects_single_architecture(loaded_skill, sample_stage1, sample_stage2):
    bad = {
        "stage1_ref": sample_stage1["scheme_id"],
        "stage2_ref": sample_stage1["scheme_id"],
        "candidate_architectures": [
            {
                "id": "A1", "name": "唯一",
                "modules": [{"id": "M1", "name": "X", "parts": ["P1"]}],
                "key_interfaces": [],
                "assembly_simulation": {"reachability_pass": True, "interference_count": 0, "method": "KG-static"},
                "datum_consistency": {"unified": True, "issues": []},
                "pros": ["x"], "cons": [],
                "fit_score_to_metrics": 0.9,
            }
        ],
        "recommended": "A1",
        "rationale_md": "x",
    }
    mock_llm = MagicMock()
    mock_llm.chat.completions.create.return_value.choices[0].message.content = json.dumps(bad, ensure_ascii=False)
    result = run_stage3_concept(
        stage1_payload=sample_stage1, stage2_payload=sample_stage2,
        skill=loaded_skill, llm_client=mock_llm, neo4j_driver=None,
    )
    jsonschema.validate(instance=result, schema=loaded_skill.schemas["stage3"])
    assert len(result["candidate_architectures"]) >= 2
    assert result.get("uncertainty") == "高"


def test_run_stage3_enforces_refs(loaded_skill, sample_stage1, sample_stage2):
    bad_resp = {
        "stage1_ref": "scheme-20260101-deadbeef",
        "stage2_ref": "scheme-20260101-deadbeef",
        "candidate_architectures": [
            {"id": "A1", "name": "a", "modules": [{"id": "M1", "name": "x", "parts": ["P1"]}],
             "key_interfaces": [], "assembly_simulation": {"reachability_pass": True, "interference_count": 0, "method": "KG-static"},
             "datum_consistency": {"unified": True, "issues": []}, "pros": ["x"], "cons": [], "fit_score_to_metrics": 0.7},
            {"id": "A2", "name": "b", "modules": [{"id": "M1", "name": "x", "parts": ["P1"]}],
             "key_interfaces": [], "assembly_simulation": {"reachability_pass": True, "interference_count": 0, "method": "KG-static"},
             "datum_consistency": {"unified": True, "issues": []}, "pros": ["x"], "cons": [], "fit_score_to_metrics": 0.5},
        ],
        "recommended": "A1",
        "rationale_md": "abc",
    }
    mock_llm = MagicMock()
    mock_llm.chat.completions.create.return_value.choices[0].message.content = json.dumps(bad_resp, ensure_ascii=False)
    result = run_stage3_concept(
        stage1_payload=sample_stage1, stage2_payload=sample_stage2,
        skill=loaded_skill, llm_client=mock_llm, neo4j_driver=None,
    )
    assert result["stage1_ref"] == sample_stage1["scheme_id"]
    assert result["stage2_ref"] == sample_stage2["stage1_ref"]


def test_placeholder_stage3_validates(loaded_skill, sample_stage1):
    p = json.loads(json.dumps(PLACEHOLDER_STAGE3, ensure_ascii=False))
    p["stage1_ref"] = sample_stage1["scheme_id"]
    p["stage2_ref"] = sample_stage1["scheme_id"]
    jsonschema.validate(instance=p, schema=loaded_skill.schemas["stage3"])
