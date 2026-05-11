"""
backend/pipelines/assembly_scheme/skill_loader.py

Load the aero-engine-assembly-scheme skill into memory for runtime use.

The skill directory layout (see spec §4.1):
  SKILL.md (frontmatter + body)
  methodology/{s1..s5}.md
  prompts/{stage_key}.prompt.md
  templates/schemas/{stage_key}.schema.json
"""

from pathlib import Path
from typing import Dict, Any
import json
import logging

import yaml

logger = logging.getLogger(__name__)


class SkillRegistry:
    """In-memory representation of one assembly-scheme skill.

    Usage:
        reg = SkillRegistry(Path("skills/aero-engine-assembly-scheme"))
        reg.load()
        reg.frontmatter  # {"name": ..., "version": ...}
        reg.prompts["s1_intake"]      # str
        reg.methodology["s1_intake_and_research"]  # str
        reg.schemas["stage1"]          # dict
    """

    def __init__(self, skill_root: Path):
        self.skill_root = Path(skill_root)
        self.frontmatter: Dict[str, Any] = {}
        self.skill_md_body: str = ""
        self.methodology: Dict[str, str] = {}
        self.prompts: Dict[str, str] = {}
        self.schemas: Dict[str, dict] = {}
        self._loaded = False

    def load(self) -> None:
        skill_md_path = self.skill_root / "SKILL.md"
        if not skill_md_path.exists():
            raise FileNotFoundError(f"SKILL.md not found at {skill_md_path}")

        # 1. Parse frontmatter from SKILL.md
        content = skill_md_path.read_text(encoding="utf-8")
        if content.startswith("---\n"):
            end = content.find("\n---\n", 4)
            if end > 0:
                fm_text = content[4:end]
                self.frontmatter = yaml.safe_load(fm_text) or {}
                self.skill_md_body = content[end + 5 :].lstrip("\n")
            else:
                self.skill_md_body = content
        else:
            self.skill_md_body = content

        # 2. Methodology files
        method_dir = self.skill_root / "methodology"
        if method_dir.exists():
            for p in sorted(method_dir.glob("*.md")):
                self.methodology[p.stem] = p.read_text(encoding="utf-8")

        # 3. Prompt templates: filename "{key}.prompt.md"
        prompt_dir = self.skill_root / "prompts"
        if prompt_dir.exists():
            for p in sorted(prompt_dir.glob("*.prompt.md")):
                key = p.name[: -len(".prompt.md")]
                self.prompts[key] = p.read_text(encoding="utf-8")

        # 4. JSON schemas: filename "{stage_key}.schema.json"
        schema_dir = self.skill_root / "templates" / "schemas"
        if schema_dir.exists():
            for p in sorted(schema_dir.glob("*.schema.json")):
                key = p.name[: -len(".schema.json")]
                self.schemas[key] = json.loads(p.read_text(encoding="utf-8"))

        self._loaded = True
        logger.info(
            "Skill loaded: name=%s methodology=%d prompts=%d schemas=%d",
            self.frontmatter.get("name"),
            len(self.methodology),
            len(self.prompts),
            len(self.schemas),
        )

    def is_loaded(self) -> bool:
        return self._loaded
