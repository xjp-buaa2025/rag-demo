"""Tests for backend.pipelines.assembly_scheme.stage4b_tooling.run_stage4b_tooling."""
from pathlib import Path
from unittest.mock import MagicMock
import json
import pytest
import jsonschema

from backend.pipelines.assembly_scheme.stage4b_tooling import (
    run_stage4b_tooling,
    PLACEHOLDER_STAGE4B,
    query_kg_tools,
)
from backend.pipelines.assembly_scheme.skill_loader import SkillRegistry

SKILL_ROOT = Path(__file__).resolve().parents[2] / "skills" / "aero-engine-assembly-scheme"


@pytest.fixture(scope="module")
def loaded_skill():
    reg = SkillRegistry(SKILL_ROOT)
    reg.load()
    return reg


@pytest.fixture
def sample_stage4a():
    return {
        "stage3_ref": "scheme-20260511-aaaaaa",
        "architecture_ref": "A1",
        "procedures": [
            {
                "id": "P01",
                "name": "后轴承座定位装夹",
                "seq_no": 1,
                "depends_on": [],
                "parts_involved": ["后轴承座"],
                "tooling": ["定位夹具 JIG-001"],
                "spec_values": [{"param": "定位精度", "value": "±0.02mm"}],
            },
            {
                "id": "P02",
                "name": "转子鼓筒套装",
                "seq_no": 2,
                "depends_on": ["P01"],
                "parts_involved": ["转子鼓筒"],
                "tooling": ["液压套装工具"],
                "spec_values": [{"param": "热套温度", "value": "见 CMM"}],
            },
            {
                "id": "P03",
                "name": "前法兰螺栓紧固",
                "seq_no": 3,
                "depends_on": ["P02"],
                "parts_involved": ["法兰螺栓 M8"],
                "tooling": ["扭矩扳手"],
                "spec_values": [{"param": "力矩", "value": "见 CMM"}],
            },
        ],
        "topology": {
            "sequence": ["P01", "P02", "P03"],
            "method": "DFA-heuristic",
            "dfa_efficiency": 0.72,
        },
        "uncertainty": "中",
    }


def _valid_llm_resp(scheme_id: str) -> dict:
    return {
        "stage4a_ref": scheme_id,
        "tools": [
            {
                "id": "T01",
                "name": "定位夹具 JIG-001",
                "category": "special",
                "cost_tier": "高",
                "used_in_procedures": ["P01"],
                "design_requirements": "需定制，用于后轴承座精密定位",
            },
            {
                "id": "T02",
                "name": "液压套装工具",
                "category": "special",
                "cost_tier": "高",
                "used_in_procedures": ["P02"],
                "design_requirements": "液压驱动，最大压力 200MPa",
            },
            {
                "id": "T03",
                "name": "扭矩扳手",
                "category": "generic",
                "cost_tier": "低",
                "used_in_procedures": ["P03"],
                "notes": "标准扭矩扳手，量程 10-100 N·m",
            },
        ],
        "tooling_constraints": [
            {
                "procedure_id": "P02",
                "tool_id": "T02",
                "issue": "液压套装工具体积大，需工件翻转后操作",
                "suggested_action": "考虑在 P01 后增加工件翻转工序",
            }
        ],
        "dfa_tooling_score": 0.33,
        "uncertainty": "中",
    }


def test_run_stage4b_no_llm_returns_placeholder(loaded_skill, sample_stage4a):
    result = run_stage4b_tooling(
        stage4a_payload=sample_stage4a,
        skill=loaded_skill,
        llm_client=None,
        neo4j_driver=None,
    )
    jsonschema.validate(instance=result, schema=loaded_skill.schemas["stage4b"])
    assert result["stage4a_ref"] == sample_stage4a["stage3_ref"]
    assert len(result["tools"]) >= 1
    assert result["uncertainty"] == "高"
    # All used_in_procedures must reference real S4a proc ids
    proc_ids = {p["id"] for p in sample_stage4a["procedures"]}
    for tool in result["tools"]:
        for pid in tool["used_in_procedures"]:
            assert pid in proc_ids, f"placeholder tool {tool['id']} refs missing proc {pid}"


def test_query_kg_tools_no_driver_returns_empty():
    rows = query_kg_tools(None, "PT6A HPC")
    assert rows == []


def test_query_kg_tools_handles_exception():
    bad_driver = MagicMock()
    bad_driver.session.side_effect = RuntimeError("neo4j down")
    rows = query_kg_tools(bad_driver, "PT6A HPC")
    assert rows == []


def test_run_stage4b_with_valid_llm_output(loaded_skill, sample_stage4a):
    scheme_id = sample_stage4a["stage3_ref"]
    mock_llm = MagicMock()
    mock_llm.chat.completions.create.return_value.choices[0].message.content = (
        json.dumps(_valid_llm_resp("scheme-00000000-000000"), ensure_ascii=False)
    )
    result = run_stage4b_tooling(
        stage4a_payload=sample_stage4a,
        skill=loaded_skill,
        llm_client=mock_llm,
        neo4j_driver=None,
    )
    jsonschema.validate(instance=result, schema=loaded_skill.schemas["stage4b"])
    assert result["stage4a_ref"] == scheme_id
    assert len(result["tools"]) == 3
    assert result["dfa_tooling_score"] == pytest.approx(0.33, abs=0.01)
    assert len(result["tooling_constraints"]) == 1


def test_run_stage4b_bad_json_falls_back(loaded_skill, sample_stage4a):
    mock_llm = MagicMock()
    mock_llm.chat.completions.create.return_value.choices[0].message.content = "not json"
    result = run_stage4b_tooling(
        stage4a_payload=sample_stage4a,
        skill=loaded_skill,
        llm_client=mock_llm,
        neo4j_driver=None,
    )
    jsonschema.validate(instance=result, schema=loaded_skill.schemas["stage4b"])
    assert result["uncertainty"] == "高"


def test_run_stage4b_dangling_procedure_ref_falls_back(loaded_skill, sample_stage4a):
    """used_in_procedures references a procedure id (P99) that doesn't exist in S4a."""
    scheme_id = sample_stage4a["stage3_ref"]
    bad_resp = _valid_llm_resp(scheme_id)
    bad_resp["tools"][0]["used_in_procedures"] = ["P99"]  # P99 doesn't exist
    mock_llm = MagicMock()
    mock_llm.chat.completions.create.return_value.choices[0].message.content = (
        json.dumps(bad_resp, ensure_ascii=False)
    )
    result = run_stage4b_tooling(
        stage4a_payload=sample_stage4a,
        skill=loaded_skill,
        llm_client=mock_llm,
        neo4j_driver=None,
    )
    jsonschema.validate(instance=result, schema=loaded_skill.schemas["stage4b"])
    assert result["uncertainty"] == "高"


def test_run_stage4b_dangling_constraint_tool_ref_falls_back(loaded_skill, sample_stage4a):
    """tooling_constraints references a tool id (T99) not in tools list."""
    scheme_id = sample_stage4a["stage3_ref"]
    bad_resp = _valid_llm_resp(scheme_id)
    bad_resp["tooling_constraints"][0]["tool_id"] = "T99"  # T99 not in tools
    mock_llm = MagicMock()
    mock_llm.chat.completions.create.return_value.choices[0].message.content = (
        json.dumps(bad_resp, ensure_ascii=False)
    )
    result = run_stage4b_tooling(
        stage4a_payload=sample_stage4a,
        skill=loaded_skill,
        llm_client=mock_llm,
        neo4j_driver=None,
    )
    jsonschema.validate(instance=result, schema=loaded_skill.schemas["stage4b"])
    assert result["uncertainty"] == "高"


def test_placeholder_stage4b_validates(loaded_skill, sample_stage4a):
    p = json.loads(json.dumps(PLACEHOLDER_STAGE4B, ensure_ascii=False))
    p["stage4a_ref"] = sample_stage4a["stage3_ref"]
    # Fix used_in_procedures to point at real proc ids
    proc_ids = [proc["id"] for proc in sample_stage4a["procedures"]]
    for tool in p["tools"]:
        tool["used_in_procedures"] = [proc_ids[0]]
    jsonschema.validate(instance=p, schema=loaded_skill.schemas["stage4b"])
