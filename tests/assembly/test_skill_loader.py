"""Tests for backend.pipelines.assembly_scheme.skill_loader.SkillRegistry."""
from pathlib import Path
import pytest

SKILL_ROOT = Path(__file__).resolve().parents[2] / "skills" / "aero-engine-assembly-scheme"


def test_skill_md_exists():
    assert (SKILL_ROOT / "SKILL.md").exists(), "SKILL.md missing"


def test_skill_md_has_frontmatter():
    content = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    assert content.startswith("---\n"), "SKILL.md must start with YAML frontmatter"
    assert "name: aero-engine-assembly-scheme" in content
    assert "version: 1.0" in content
