"""Tests for backend.pipelines.assembly_scheme.skill_loader.SkillRegistry."""
from pathlib import Path
import pytest

from backend.pipelines.assembly_scheme.skill_loader import SkillRegistry

SKILL_ROOT = Path(__file__).resolve().parents[2] / "skills" / "aero-engine-assembly-scheme"


def test_skill_md_exists():
    assert (SKILL_ROOT / "SKILL.md").exists(), "SKILL.md missing"


def test_skill_md_has_frontmatter():
    content = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    assert content.startswith("---\n")
    assert "name: aero-engine-assembly-scheme" in content
    assert "version: 1.0" in content


def test_registry_load_parses_frontmatter():
    reg = SkillRegistry(SKILL_ROOT)
    reg.load()
    assert reg.is_loaded()
    assert reg.frontmatter["name"] == "aero-engine-assembly-scheme"
    assert reg.frontmatter["version"] == 1.0
    assert reg.frontmatter["type"] == "domain-workflow"


def test_registry_load_collects_methodology_files():
    reg = SkillRegistry(SKILL_ROOT)
    reg.load()
    expected = {
        "s1_intake_and_research",
        "s2_requirements_qfd",
        "s3_concept_architecture",
        "s4_detailed_process",
        "s5_review_and_export",
    }
    assert set(reg.methodology.keys()) == expected
    # Each methodology body is non-empty
    for k, v in reg.methodology.items():
        assert v.strip(), f"methodology/{k}.md is empty"


def test_registry_load_collects_prompts():
    reg = SkillRegistry(SKILL_ROOT)
    reg.load()
    assert "s1_intake" in reg.prompts
    assert "你是航空发动机装配工艺资深专家" in reg.prompts["s1_intake"]


def test_registry_load_collects_schemas():
    reg = SkillRegistry(SKILL_ROOT)
    reg.load()
    expected = {"stage1", "stage2", "stage3", "stage4a", "stage4b", "stage4c", "stage4d", "stage5"}
    assert set(reg.schemas.keys()) == expected
    # Each schema is a dict with $schema key
    for k, v in reg.schemas.items():
        assert isinstance(v, dict)
        assert "$schema" in v


def test_registry_skill_md_body_extracted_after_frontmatter():
    reg = SkillRegistry(SKILL_ROOT)
    reg.load()
    assert "# 航空发动机装配方案设计 Skill" in reg.skill_md_body
    assert "name: aero-engine-assembly-scheme" not in reg.skill_md_body  # body excludes frontmatter


def test_registry_load_missing_skill_md_raises(tmp_path):
    reg = SkillRegistry(tmp_path)
    with pytest.raises(FileNotFoundError):
        reg.load()
