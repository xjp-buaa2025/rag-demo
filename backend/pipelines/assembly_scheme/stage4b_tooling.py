"""backend/pipelines/assembly_scheme/stage4b_tooling.py — S4b Tooling planning."""

from __future__ import annotations
from typing import Any, Dict, List, Optional
import json
import logging
import jsonschema
from backend.pipelines.assembly_scheme.skill_loader import SkillRegistry

logger = logging.getLogger(__name__)

PLACEHOLDER_STAGE4B: Dict[str, Any] = {
    "stage4a_ref": "PLACEHOLDER",
    "tools": [
        {
            "id": "T01",
            "name": "（占位）通用定位夹具",
            "category": "generic",
            "cost_tier": "低",
            "used_in_procedures": ["P01"],
            "notes": "占位，待 chamberlain 补全",
        },
        {
            "id": "T02",
            "name": "（占位）专用套装工具",
            "category": "special",
            "cost_tier": "高",
            "used_in_procedures": ["P01"],
            "design_requirements": "（占位）待补充设计要求",
        },
        {
            "id": "T03",
            "name": "（占位）通用扭矩扳手",
            "category": "generic",
            "cost_tier": "低",
            "used_in_procedures": ["P01"],
            "notes": "占位",
        },
    ],
    "tooling_constraints": [],
    "dfa_tooling_score": 0.67,
    "uncertainty": "高",
}


def query_kg_tools(neo4j_driver: Any, subject_name: str) -> List[Dict]:
    """Query existing Tool nodes and requires relationships from KG."""
    if neo4j_driver is None:
        return []
    try:
        with neo4j_driver.session() as session:
            rows = session.run(
                "MATCH (t:Tool) "
                "WHERE coalesce(t.kg_name, '') CONTAINS $subj "
                "OPTIONAL MATCH (p:Procedure)-[:requires]->(t) "
                "RETURN t.kg_name AS name, t.tool_type AS tool_type, "
                "       p.kg_name AS used_in_procedure LIMIT 30",
                subj=subject_name,
            ).data()
            return rows
    except Exception as e:
        logger.warning("Stage4b KG tool query failed: %s", e)
        return []


def _cross_validate(obj: dict, stage4a_payload: dict) -> bool:
    """Return True if all id cross-references are valid, False otherwise."""
    proc_ids = {p["id"] for p in stage4a_payload.get("procedures", [])}
    tool_ids = {t["id"] for t in obj.get("tools", [])}

    for tool in obj.get("tools", []):
        for pid in tool.get("used_in_procedures", []):
            if pid not in proc_ids:
                logger.warning(
                    "Stage4b cross-validate: tool %s refs unknown proc %s", tool["id"], pid
                )
                return False

    for constraint in obj.get("tooling_constraints", []):
        pid = constraint.get("procedure_id", "")
        tid = constraint.get("tool_id", "")
        if pid not in proc_ids:
            logger.warning("Stage4b cross-validate: constraint refs unknown proc %s", pid)
            return False
        if tid not in tool_ids:
            logger.warning("Stage4b cross-validate: constraint refs unknown tool %s", tid)
            return False

    return True


def _build_prompt(skill, stage4a_payload, kg_tools, user_guidance):
    prompt_template = skill.prompts.get("s4b_tooling", "")
    methodology = skill.methodology.get("s4_detailed_process", "")
    return (
        f"{prompt_template}\n\n"
        f"## 方法论上下文\n{methodology}\n\n"
        f"## S4a 产物\n```json\n{json.dumps(stage4a_payload, ensure_ascii=False, indent=2)}\n```\n\n"
        f"## KG 已有工装节点\n```json\n{json.dumps(kg_tools, ensure_ascii=False, indent=2)}\n```\n\n"
        f"## chamberlain 指导意见\n{user_guidance or '（无）'}\n\n"
        "请生成符合 stage4b.schema.json 的 JSON 对象："
    )


def _call_llm(llm_client, prompt):
    if llm_client is None:
        return None
    try:
        resp = llm_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}], temperature=0.2,
        )
        return resp.choices[0].message.content
    except Exception as e:
        logger.error("Stage4b LLM call failed: %s", e)
        return None


def _parse_and_validate(raw: str, schema: dict, stage4a_payload: dict) -> Optional[Dict]:
    try:
        s = raw.strip()
        if s.startswith("```"):
            s = s.strip("`")
            if s.lower().startswith("json\n"):
                s = s[5:]
        obj = json.loads(s)
    except json.JSONDecodeError as e:
        logger.warning("Stage4b LLM JSON parse failed: %s; raw=%s", e, raw[:200])
        return None
    try:
        jsonschema.validate(instance=obj, schema=schema)
    except jsonschema.ValidationError as e:
        logger.warning("Stage4b LLM output failed schema: %s", e.message)
        return None
    if not _cross_validate(obj, stage4a_payload):
        return None
    return obj


def run_stage4b_tooling(
    stage4a_payload: Dict[str, Any],
    skill: SkillRegistry,
    llm_client: Any,
    neo4j_driver: Any = None,
    user_guidance: Optional[str] = None,
) -> Dict[str, Any]:
    """Execute S4b pipeline. Returns a dict valid per stage4b.schema.json."""
    schema = skill.schemas["stage4b"]
    scheme_id = stage4a_payload.get("stage3_ref", "PLACEHOLDER")

    subject_name = stage4a_payload.get("subject", {}).get("system", "")

    kg_tools = query_kg_tools(neo4j_driver, subject_name)
    prompt = _build_prompt(skill, stage4a_payload, kg_tools, user_guidance)
    raw = _call_llm(llm_client, prompt)
    parsed = _parse_and_validate(raw, schema, stage4a_payload) if raw else None

    if parsed is None:
        result = json.loads(json.dumps(PLACEHOLDER_STAGE4B, ensure_ascii=False))
        result["stage4a_ref"] = scheme_id
        # Fix used_in_procedures to reference real S4a procedure ids
        proc_ids = [p["id"] for p in stage4a_payload.get("procedures", [])]
        if proc_ids:
            for tool in result["tools"]:
                tool["used_in_procedures"] = [proc_ids[0]]
        return result

    parsed["stage4a_ref"] = scheme_id
    return parsed
