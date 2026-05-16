"""Tests for backend.pipelines.assembly_scheme.stage4a_process.run_stage4a_process."""
from pathlib import Path
from unittest.mock import MagicMock
import json
import pytest
import jsonschema

from backend.pipelines.assembly_scheme.stage4a_process import (
    run_stage4a_process,
    PLACEHOLDER_STAGE4A,
    query_kg_procedures,
)
from backend.pipelines.assembly_scheme.skill_loader import SkillRegistry

SKILL_ROOT = Path(__file__).resolve().parents[2] / "skills" / "aero-engine-assembly-scheme"


@pytest.fixture(scope="module")
def loaded_skill():
    reg = SkillRegistry(SKILL_ROOT)
    reg.load()
    return reg


@pytest.fixture
def sample_stage3():
    return {
        "stage1_ref": "scheme-20260511-aaaaaa",
        "stage2_ref": "scheme-20260511-aaaaaa",
        "candidate_architectures": [
            {
                "id": "A1",
                "name": "三段分体式",
                "modules": [
                    {"id": "M1", "name": "前轴承座", "parts": ["P-001"]},
                    {"id": "M2", "name": "转子鼓筒", "parts": ["P-002"]},
                    {"id": "M3", "name": "后轴承座", "parts": ["P-003"]},
                ],
                "key_interfaces": [{"from": "M1", "to": "M2", "type": "法兰螺栓"}],
                "assembly_simulation": {
                    "reachability_pass": True,
                    "interference_count": 0,
                    "method": "KG-static",
                },
                "datum_consistency": {"unified": True, "issues": []},
                "pros": ["可拆"],
                "cons": ["螺栓多"],
                "fit_score_to_metrics": 0.82,
            },
            {
                "id": "A2",
                "name": "整体式",
                "modules": [{"id": "M1", "name": "整体外壳", "parts": ["P-001", "P-002", "P-003"]}],
                "key_interfaces": [],
                "assembly_simulation": {
                    "reachability_pass": True,
                    "interference_count": 1,
                    "method": "KG-static",
                },
                "datum_consistency": {"unified": False, "issues": ["基准不统一"]},
                "pros": ["紧凑"],
                "cons": ["维修难"],
                "fit_score_to_metrics": 0.58,
            },
        ],
        "recommended": "A1",
        "rationale_md": "A1 fit_score=0.82 > A2 fit_score=0.58，推荐三段分体。",
        "uncertainty": "低",
    }


def test_run_stage4a_no_llm_no_kg_returns_placeholder(loaded_skill, sample_stage3):
    result = run_stage4a_process(
        stage3_payload=sample_stage3,
        skill=loaded_skill,
        llm_client=None,
        neo4j_driver=None,
    )
    jsonschema.validate(instance=result, schema=loaded_skill.schemas["stage4a"])
    assert result["stage3_ref"] == sample_stage3["stage1_ref"]
    assert result["architecture_ref"] == "A1"
    assert len(result["procedures"]) >= 1
    # topology.sequence must cover all procedure ids
    proc_ids = {p["id"] for p in result["procedures"]}
    topo_ids = set(result["topology"]["sequence"])
    assert proc_ids == topo_ids


def test_query_kg_procedures_no_driver_returns_empty():
    rows = query_kg_procedures(None, "PT6A HPC")
    assert rows == []


def test_query_kg_procedures_handles_driver_exception():
    bad_driver = MagicMock()
    bad_driver.session.side_effect = RuntimeError("neo4j down")
    rows = query_kg_procedures(bad_driver, "PT6A HPC")
    assert rows == []


def test_run_stage4a_with_valid_llm_output(loaded_skill, sample_stage3):
    mock_resp = {
        "stage3_ref": sample_stage3["stage1_ref"],
        "architecture_ref": "A1",
        "procedures": [
            {
                "id": "P01",
                "name": "后轴承座定位装夹",
                "seq_no": 1,
                "depends_on": [],
                "parts_involved": ["后轴承座"],
                "tooling": ["定位夹具 JIG-001"],
                "spec_values": [{"param": "定位精度", "value": "±0.02mm", "standard": "CMM-3-1"}],
                "access_direction": "axial",
                "dfa_flag": "ok",
            },
            {
                "id": "P02",
                "name": "转子鼓筒套装",
                "seq_no": 2,
                "depends_on": ["P01"],
                "parts_involved": ["转子鼓筒"],
                "tooling": ["液压套装工具"],
                "spec_values": [{"param": "热套温度", "value": "见 CMM"}],
                "access_direction": "axial",
                "dfa_flag": "critical",
            },
            {
                "id": "P03",
                "name": "前法兰螺栓紧固",
                "seq_no": 3,
                "depends_on": ["P02"],
                "parts_involved": ["法兰螺栓 M8"],
                "tooling": ["扭矩扳手"],
                "spec_values": [{"param": "力矩", "value": "见 CMM", "standard": "AMM-72-20"}],
                "access_direction": "axial",
                "dfa_flag": "ok",
            },
        ],
        "topology": {
            "sequence": ["P01", "P02", "P03"],
            "method": "DFA-heuristic",
            "dfa_efficiency": 0.72,
        },
        "uncertainty": "中",
    }
    mock_llm = MagicMock()
    mock_llm.chat.completions.create.return_value.choices[0].message.content = (
        json.dumps(mock_resp, ensure_ascii=False)
    )
    result = run_stage4a_process(
        stage3_payload=sample_stage3,
        skill=loaded_skill,
        llm_client=mock_llm,
        neo4j_driver=None,
    )
    jsonschema.validate(instance=result, schema=loaded_skill.schemas["stage4a"])
    assert result["architecture_ref"] == "A1"
    assert len(result["procedures"]) == 3
    assert result["topology"]["method"] == "DFA-heuristic"


def test_run_stage4a_bad_json_falls_back_to_placeholder(loaded_skill, sample_stage3):
    mock_llm = MagicMock()
    mock_llm.chat.completions.create.return_value.choices[0].message.content = "not json at all"
    result = run_stage4a_process(
        stage3_payload=sample_stage3,
        skill=loaded_skill,
        llm_client=mock_llm,
        neo4j_driver=None,
    )
    jsonschema.validate(instance=result, schema=loaded_skill.schemas["stage4a"])
    assert result["uncertainty"] == "高"


def test_run_stage4a_topo_mismatch_falls_back_to_placeholder(loaded_skill, sample_stage3):
    """LLM output where topology.sequence doesn't match procedure ids → placeholder."""
    bad_resp = {
        "stage3_ref": sample_stage3["stage1_ref"],
        "architecture_ref": "A1",
        "procedures": [
            {
                "id": "P01", "name": "步骤1", "seq_no": 1, "depends_on": [],
                "parts_involved": ["X"], "tooling": ["T1"],
                "spec_values": [{"param": "p", "value": "v"}],
            },
        ],
        "topology": {
            "sequence": ["P01", "P99"],  # P99 doesn't exist → mismatch
            "method": "placeholder",
        },
    }
    mock_llm = MagicMock()
    mock_llm.chat.completions.create.return_value.choices[0].message.content = (
        json.dumps(bad_resp, ensure_ascii=False)
    )
    result = run_stage4a_process(
        stage3_payload=sample_stage3,
        skill=loaded_skill,
        llm_client=mock_llm,
        neo4j_driver=None,
    )
    jsonschema.validate(instance=result, schema=loaded_skill.schemas["stage4a"])
    assert result["uncertainty"] == "高"


def test_placeholder_stage4a_validates(loaded_skill, sample_stage3):
    p = json.loads(json.dumps(PLACEHOLDER_STAGE4A, ensure_ascii=False))
    p["stage3_ref"] = sample_stage3["stage1_ref"]
    jsonschema.validate(instance=p, schema=loaded_skill.schemas["stage4a"])
