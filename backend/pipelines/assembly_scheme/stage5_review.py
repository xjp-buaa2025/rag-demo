"""backend/pipelines/assembly_scheme/stage5_review.py — S5 三角色虚拟评审."""

from __future__ import annotations
from typing import Any, Dict, List, Optional
import json
import logging
import jsonschema
from backend.pipelines.assembly_scheme.skill_loader import SkillRegistry

logger = logging.getLogger(__name__)

PLACEHOLDER_STAGE5: Dict[str, Any] = {
    "stage4b_ref": "PLACEHOLDER",
    "review_panel": [
        {
            "role": "工艺工程师",
            "findings": ["（占位）工序链未经验证，需 LLM 生成完整评审"],
            "severity_issues": [],
        },
        {
            "role": "质量工程师",
            "findings": ["（占位）KC 追溯矩阵待生成"],
            "severity_issues": [],
        },
        {
            "role": "设计工程师",
            "findings": ["（占位）需求覆盖度待核实"],
            "severity_issues": [],
        },
    ],
    "kc_traceability_matrix": [],
    "overall_score": 0.0,
    "recommendation": "approved_with_revision",
    "iterations": [],
    "uncertainty": "高",
}


def _cross_validate(obj: dict) -> bool:
    """Return False if high severity issues exist but recommendation is 'approved'."""
    has_high = any(
        si.get("severity") == "high"
        for reviewer in obj.get("review_panel", [])
        for si in reviewer.get("severity_issues", [])
    )
    if has_high and obj.get("recommendation") == "approved":
        logger.warning(
            "Stage5 cross-validate: recommendation='approved' but high severity issues present"
        )
        return False
    return True


def _build_prompt(
    skill: SkillRegistry,
    stage4b_payload: dict,
    stage4a_payload: dict,
    stage2_payload: dict,
    user_guidance: Optional[str],
) -> str:
    prompt_template = skill.prompts.get("s5_review", "")
    methodology = skill.methodology.get("s5_review_and_export", "")
    return (
        f"{prompt_template}\n\n"
        f"## 方法论上下文\n{methodology}\n\n"
        f"## S2 需求分析产物\n```json\n{json.dumps(stage2_payload, ensure_ascii=False, indent=2)}\n```\n\n"
        f"## S4a 工序链\n```json\n{json.dumps(stage4a_payload, ensure_ascii=False, indent=2)}\n```\n\n"
        f"## S4b 工装清单\n```json\n{json.dumps(stage4b_payload, ensure_ascii=False, indent=2)}\n```\n\n"
        f"## 评审指导意见\n{user_guidance or '（无）'}\n\n"
        "请生成符合 stage5.schema.json 的 JSON 对象："
    )


def _call_llm(llm_client: Any, prompt: str) -> Optional[str]:
    if llm_client is None:
        return None
    try:
        resp = llm_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}], temperature=0.2,
        )
        return resp.choices[0].message.content
    except Exception as e:
        logger.error("Stage5 LLM call failed: %s", e)
        return None


def _parse_and_validate(raw: str, schema: dict) -> Optional[Dict]:
    try:
        s = raw.strip()
        if s.startswith("```"):
            lines = s.splitlines()
            end = -1 if lines and lines[-1].strip() == "```" else len(lines)
            s = "\n".join(lines[1:end])
        obj = json.loads(s)
    except json.JSONDecodeError as e:
        logger.warning("Stage5 LLM JSON parse failed: %s; raw=%s", e, raw[:200])
        return None
    try:
        jsonschema.validate(instance=obj, schema=schema)
    except jsonschema.ValidationError as e:
        logger.warning("Stage5 LLM output failed schema: %s", e.message)
        return None
    if not _cross_validate(obj):
        return None
    return obj


def run_stage5_review(
    stage4b_payload: Dict[str, Any],
    stage4a_payload: Dict[str, Any],
    stage2_payload: Dict[str, Any],
    skill: SkillRegistry,
    llm_client: Any,
    neo4j_driver: Any = None,
    user_guidance: Optional[str] = None,
) -> Dict[str, Any]:
    """Execute S5 pipeline. Returns a dict valid per stage5.schema.json."""
    schema = skill.schemas["stage5"]
    scheme_id = stage4b_payload.get("stage4a_ref", "PLACEHOLDER")

    prompt = _build_prompt(skill, stage4b_payload, stage4a_payload, stage2_payload, user_guidance)
    raw = _call_llm(llm_client, prompt)
    parsed = _parse_and_validate(raw, schema) if raw else None

    if parsed is None:
        result = json.loads(json.dumps(PLACEHOLDER_STAGE5, ensure_ascii=False))
        result["stage4b_ref"] = scheme_id
        return result

    parsed["stage4b_ref"] = scheme_id
    return parsed
