"""Tests for backend.pipelines.assembly_scheme.stage1_intake.run_stage1_intake."""
from pathlib import Path
from unittest.mock import MagicMock
import json
import pytest

from backend.pipelines.assembly_scheme.stage1_intake import (
    run_stage1_intake,
    build_search_queries,
    kg_snapshot,
)
from backend.pipelines.assembly_scheme.skill_loader import SkillRegistry
from backend.tools.web_search import WebSearchClient, SearchResult

SKILL_ROOT = Path(__file__).resolve().parents[2] / "skills" / "aero-engine-assembly-scheme"


# ── build_search_queries ─────────────────────────────────────────────────────

def test_build_search_queries_with_en():
    qs = build_search_queries("PT6A 高压压气机", "PT6A HPC")
    assert len(qs) == 3
    assert any("GJB" in q for q in qs)
    assert any("PT6A HPC assembly procedure" in q for q in qs)
    assert any("service bulletin" in q for q in qs)


def test_build_search_queries_no_en():
    qs = build_search_queries("PT6A 高压压气机", None)
    assert len(qs) == 1
    assert "GJB" in qs[0]


# ── kg_snapshot ──────────────────────────────────────────────────────────────

def test_kg_snapshot_no_driver_returns_zero_with_warning():
    snap = kg_snapshot(None, "PT6A HPC")
    assert snap["part_count"] == 0
    assert snap["assembly_count"] == 0
    assert "warning" in snap


def test_kg_snapshot_uses_driver_when_available():
    mock_driver = MagicMock()
    mock_session = MagicMock()
    mock_record = {"nc": 12, "rels": ["isPartOf", "matesWith"]}
    mock_session.run.return_value.single.return_value = mock_record
    mock_driver.session.return_value.__enter__.return_value = mock_session

    snap = kg_snapshot(mock_driver, "PT6A HPC")
    assert snap["part_count"] == 12
    assert "isPartOf" in snap["relations_sample"]


# ── run_stage1_intake (smoke + integration with skill registry) ──────────────

@pytest.fixture(scope="module")
def loaded_skill():
    reg = SkillRegistry(SKILL_ROOT)
    reg.load()
    return reg


def test_run_stage1_intake_no_llm_no_web_no_kg(loaded_skill):
    """Minimal: no LLM, no web key, no Neo4j — should still return valid stage1 dict."""
    web = WebSearchClient(api_key=None, cache_dir=Path("storage/web_cache"))

    user_input = {
        "scheme_id": "scheme-20260508-aaaaaa",
        "subject": {
            "system": "PT6A 高压压气机",
            "system_en": "PT6A HPC",
            "scope": ["3 级轴流"],
            "design_intent": "工艺优化",
            "constraints": {"primary": "可靠性"},
        },
        "vision_notes": "",
    }

    result = run_stage1_intake(
        user_input=user_input,
        skill=loaded_skill,
        web_search=web,
        llm_client=None,
        neo4j_driver=None,
    )

    assert result["scheme_id"] == "scheme-20260508-aaaaaa"
    assert result["subject"]["system"] == "PT6A 高压压气机"
    assert result["kg_snapshot"]["part_count"] == 0
    assert result["web_search_results"] == []
    assert result["compliance_scope"]
    assert "task_card_md" in result
    assert isinstance(result["task_card_md"], str)


def test_run_stage1_intake_with_mocked_llm(loaded_skill):
    """LLM is called and its output appears in task_card_md."""
    web = MagicMock(spec=WebSearchClient)
    web.search.return_value = []

    mock_llm = MagicMock()
    mock_llm.chat.completions.create.return_value.choices[0].message.content = (
        "## 任务说明书\n\n**目标**：测试用 task card\n\n**范围**：测试\n\n**边界**：测试\n\n**约束**：测试\n\n**已知风险**：测试"
    )

    user_input = {
        "scheme_id": "scheme-20260508-bbbbbb",
        "subject": {
            "system": "Test Subject",
            "scope": ["test"],
            "design_intent": "工艺优化",
            "constraints": {"primary": "可靠性"},
        },
    }
    result = run_stage1_intake(
        user_input=user_input,
        skill=loaded_skill,
        web_search=web,
        llm_client=mock_llm,
        neo4j_driver=None,
    )
    assert "测试用 task card" in result["task_card_md"]
    mock_llm.chat.completions.create.assert_called_once()


def test_run_stage1_intake_validates_against_schema(loaded_skill):
    """Output must validate against stage1 schema."""
    import jsonschema
    schema = loaded_skill.schemas["stage1"]

    web = WebSearchClient(api_key=None, cache_dir=Path("storage/web_cache"))
    user_input = {
        "scheme_id": "scheme-20260508-cccccc",
        "subject": {
            "system": "PT6A HPC",
            "scope": ["3 级轴流"],
            "design_intent": "工艺优化",
            "constraints": {"primary": "可靠性"},
        },
    }
    result = run_stage1_intake(
        user_input=user_input,
        skill=loaded_skill,
        web_search=web,
        llm_client=None,
        neo4j_driver=None,
    )
    jsonschema.validate(instance=result, schema=schema)
