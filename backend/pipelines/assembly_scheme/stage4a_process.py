"""backend/pipelines/assembly_scheme/stage4a_process.py — S4a Detailed assembly process design."""

from __future__ import annotations
from typing import Any, Dict, List, Optional
import json
import logging
import jsonschema
from backend.pipelines.assembly_scheme.skill_loader import SkillRegistry

logger = logging.getLogger(__name__)

PLACEHOLDER_STAGE4A: Dict[str, Any] = {
    "stage3_ref": "PLACEHOLDER",
    "architecture_ref": "A1",
    "procedures": [
        {
            "id": "P01",
            "name": "（占位）基准件定位与装夹",
            "seq_no": 1,
            "depends_on": [],
            "parts_involved": ["（占位）基准件"],
            "tooling": ["通用工装待确认"],
            "spec_values": [{"param": "待补充", "value": "见 CMM"}],
            "access_direction": "axial",
            "dfa_flag": "ok",
        },
        {
            "id": "P02",
            "name": "（占位）主要配合件安装",
            "seq_no": 2,
            "depends_on": ["P01"],
            "parts_involved": ["（占位）配合件"],
            "tooling": ["通用工装待确认"],
            "spec_values": [{"param": "待补充", "value": "见 CMM"}],
            "access_direction": "axial",
            "dfa_flag": "merge_candidate",
        },
        {
            "id": "P03",
            "name": "（占位）紧固与力矩检验",
            "seq_no": 3,
            "depends_on": ["P02"],
            "parts_involved": ["（占位）紧固件"],
            "tooling": ["通用工装待确认"],
            "spec_values": [{"param": "力矩", "value": "见 CMM", "standard": "待确认"}],
            "access_direction": "axial",
            "dfa_flag": "ok",
        },
    ],
    "topology": {
        "sequence": ["P01", "P02", "P03"],
        "method": "placeholder",
        "dfa_efficiency": 0.5,
    },
    "uncertainty": "高",
}


def query_kg_procedures(neo4j_driver: Any, subject_name: str) -> List[Dict]:
    """Query existing Procedure nodes and precedes chain from KG."""
    if neo4j_driver is None:
        return []
    try:
        with neo4j_driver.session() as session:
            rows = session.run(
                "MATCH (p:Procedure) "
                "WHERE coalesce(p.kg_name, '') CONTAINS $subj "
                "OPTIONAL MATCH (p)-[:precedes]->(q:Procedure) "
                "RETURN p.kg_name AS name, p.seq_no AS seq_no, "
                "       q.kg_name AS next_name LIMIT 30",
                subj=subject_name,
            ).data()
            return rows
    except Exception as e:
        logger.warning("Stage4a KG procedure query failed: %s", e)
        return []


def _build_prompt(skill, stage3_payload, kg_procedures, user_guidance):
    prompt_template = skill.prompts.get("s4_process", "")
    methodology = skill.methodology.get("s4_detailed_process", "")
    return (
        f"{prompt_template}\n\n"
        f"## 方法论上下文\n{methodology}\n\n"
        f"## S3 产物\n```json\n{json.dumps(stage3_payload, ensure_ascii=False, indent=2)}\n```\n\n"
        f"## KG 已有工序链\n```json\n{json.dumps(kg_procedures, ensure_ascii=False, indent=2)}\n```\n\n"
        f"## chamberlain 指导意见\n{user_guidance or '（无）'}\n\n"
        "请生成符合 stage4a.schema.json 的 JSON 对象（至少 3 条工序）："
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
        logger.error("Stage4a LLM call failed: %s", e)
        return None


def _parse_and_validate(raw: str, schema: dict) -> Optional[Dict]:
    try:
        s = raw.strip()
        if s.startswith("```"):
            s = s.strip("`")
            if s.lower().startswith("json\n"):
                s = s[5:]
        obj = json.loads(s)
    except json.JSONDecodeError as e:
        logger.warning("Stage4a LLM JSON parse failed: %s; raw=%s", e, raw[:200])
        return None
    try:
        jsonschema.validate(instance=obj, schema=schema)
    except jsonschema.ValidationError as e:
        logger.warning("Stage4a LLM output failed schema: %s", e.message)
        return None
    # Integrity: topology.sequence must contain exactly the ids in procedures
    proc_ids = {p["id"] for p in obj.get("procedures", [])}
    topo_ids = set(obj.get("topology", {}).get("sequence", []))
    if proc_ids != topo_ids:
        logger.warning(
            "Stage4a topology.sequence mismatch: procedures=%s topo=%s",
            proc_ids, topo_ids,
        )
        return None
    return obj


def run_stage4a_process(
    stage3_payload: Dict[str, Any],
    skill: SkillRegistry,
    llm_client: Any,
    neo4j_driver: Any = None,
    user_guidance: Optional[str] = None,
) -> Dict[str, Any]:
    """Execute S4a pipeline. Returns a dict valid per stage4a.schema.json."""
    schema = skill.schemas["stage4a"]
    scheme_id = stage3_payload.get("stage1_ref", "PLACEHOLDER")

    subject_name = ""
    # Try to derive subject from upstream refs embedded in stage3 payload
    if "subject" in stage3_payload:
        subject_name = stage3_payload["subject"].get("system", "")

    kg_procs = query_kg_procedures(neo4j_driver, subject_name)
    prompt = _build_prompt(skill, stage3_payload, kg_procs, user_guidance)
    raw = _call_llm(llm_client, prompt)
    parsed = _parse_and_validate(raw, schema) if raw else None

    if parsed is None:
        result = json.loads(json.dumps(PLACEHOLDER_STAGE4A, ensure_ascii=False))
        result["stage3_ref"] = scheme_id
        # Inherit recommended architecture from S3
        result["architecture_ref"] = stage3_payload.get("recommended", "A1")
        return result

    parsed["stage3_ref"] = scheme_id
    return parsed
