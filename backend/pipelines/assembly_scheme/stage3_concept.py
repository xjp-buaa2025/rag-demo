"""backend/pipelines/assembly_scheme/stage3_concept.py — S3 Concept architecture design."""

from __future__ import annotations
from typing import Any, Dict, Optional
import json
import logging
import jsonschema
from backend.pipelines.assembly_scheme.skill_loader import SkillRegistry

logger = logging.getLogger(__name__)

PLACEHOLDER_STAGE3: Dict[str, Any] = {
    "stage1_ref": "PLACEHOLDER",
    "stage2_ref": "PLACEHOLDER",
    "candidate_architectures": [
        {
            "id": "A1",
            "name": "（占位）baseline 三段式架构",
            "modules": [
                {"id": "M1", "name": "（占位）前段", "parts": ["P-placeholder-1"]},
                {"id": "M2", "name": "（占位）中段", "parts": ["P-placeholder-2"]},
                {"id": "M3", "name": "（占位）后段", "parts": ["P-placeholder-3"]},
            ],
            "key_interfaces": [
                {"from": "M1", "to": "M2", "type": "（占位）法兰螺栓"},
                {"from": "M2", "to": "M3", "type": "（占位）法兰螺栓"},
            ],
            "assembly_simulation": {
                "reachability_pass": True,
                "interference_count": 0,
                "method": "placeholder",
                "notes": "数据不足，未做实际可达性分析",
            },
            "datum_consistency": {"unified": True, "issues": []},
            "pros": ["（占位）拆装方便"],
            "cons": ["（占位）紧固件数量偏多"],
            "fit_score_to_metrics": 0.5,
        },
        {
            "id": "A2",
            "name": "（占位）baseline 整体式架构",
            "modules": [
                {"id": "M1", "name": "（占位）整体外壳", "parts": ["P-placeholder-1", "P-placeholder-2", "P-placeholder-3"]},
            ],
            "key_interfaces": [],
            "assembly_simulation": {
                "reachability_pass": True,
                "interference_count": 0,
                "method": "placeholder",
            },
            "datum_consistency": {"unified": True, "issues": []},
            "pros": ["（占位）零件少"],
            "cons": ["（占位）维修困难"],
            "fit_score_to_metrics": 0.4,
        },
    ],
    "recommended": "A1",
    "rationale_md": "（占位）chamberlain 需在 HITL 提供更多 KG/CAD 数据后重新生成。当前两候选均为占位，A1 略高仅因模块更分散。",
    "uncertainty": "高",
}


def query_kg_subgraph(neo4j_driver: Any, subject_name: str) -> Dict[str, list]:
    empty = {"modules": [], "matesWith": [], "adjacentTo": []}
    if neo4j_driver is None:
        return empty
    try:
        with neo4j_driver.session() as session:
            modules = session.run(
                "MATCH (a)-[:isPartOf]->(b) "
                "WHERE coalesce(b.kg_name, '') CONTAINS $subj OR coalesce(b.part_name, '') CONTAINS $subj "
                "RETURN a.kg_name AS child, b.kg_name AS parent LIMIT 30",
                subj=subject_name,
            ).data()
            mates = session.run(
                "MATCH (a)-[:matesWith]->(b) "
                "WHERE coalesce(a.kg_name, '') CONTAINS $subj OR coalesce(b.kg_name, '') CONTAINS $subj "
                "RETURN a.kg_name AS p1, b.kg_name AS p2 LIMIT 30",
                subj=subject_name,
            ).data()
            adj = session.run(
                "MATCH (a)-[:adjacentTo]->(b) "
                "WHERE coalesce(a.kg_name, '') CONTAINS $subj OR coalesce(b.kg_name, '') CONTAINS $subj "
                "RETURN a.kg_name AS p1, b.kg_name AS p2 LIMIT 30",
                subj=subject_name,
            ).data()
            return {"modules": modules, "matesWith": mates, "adjacentTo": adj}
    except Exception as e:
        logger.warning("Stage3 KG subgraph query failed: %s", e)
        return empty


def _build_prompt(skill, stage1_payload, stage2_payload, kg_subgraph, user_guidance):
    prompt_template = skill.prompts.get("s3_concept", "")
    methodology = skill.methodology.get("s3_concept_architecture", "")
    return (
        f"{prompt_template}\n\n"
        f"## 方法论上下文\n{methodology}\n\n"
        f"## S1 产物\n```json\n{json.dumps(stage1_payload, ensure_ascii=False, indent=2)}\n```\n\n"
        f"## S2 产物\n```json\n{json.dumps(stage2_payload, ensure_ascii=False, indent=2)}\n```\n\n"
        f"## KG 子图\n```json\n{json.dumps(kg_subgraph, ensure_ascii=False, indent=2)}\n```\n\n"
        f"## chamberlain 指导意见\n{user_guidance or '（无）'}\n\n"
        "请生成符合 stage3.schema.json 的 JSON 对象（至少 2 个 candidate_architectures）："
    )


def _call_llm(llm_client, prompt):
    if llm_client is None:
        return None
    try:
        resp = llm_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}], temperature=0.3,
        )
        return resp.choices[0].message.content
    except Exception as e:
        logger.error("Stage3 LLM call failed: %s", e)
        return None


def _parse_and_validate(raw, schema):
    try:
        s = raw.strip()
        if s.startswith("```"):
            s = s.strip("`")
            if s.lower().startswith("json\n"):
                s = s[5:]
        obj = json.loads(s)
    except json.JSONDecodeError as e:
        logger.warning("Stage3 LLM JSON parse failed: %s; raw=%s", e, raw[:200])
        return None
    try:
        jsonschema.validate(instance=obj, schema=schema)
    except jsonschema.ValidationError as e:
        logger.warning("Stage3 LLM output failed schema: %s", e.message)
        return None
    return obj


def run_stage3_concept(
    stage1_payload: Dict[str, Any],
    stage2_payload: Dict[str, Any],
    skill: SkillRegistry,
    llm_client: Any,
    neo4j_driver: Any = None,
    user_guidance: Optional[str] = None,
) -> Dict[str, Any]:
    """Execute S3 pipeline. Returns a dict valid per stage3.schema.json."""
    schema = skill.schemas["stage3"]
    scheme_id_1 = stage1_payload["scheme_id"]
    scheme_id_2 = stage2_payload["stage1_ref"]

    kg_sub = query_kg_subgraph(neo4j_driver, stage1_payload["subject"]["system"])
    prompt = _build_prompt(skill, stage1_payload, stage2_payload, kg_sub, user_guidance)
    raw = _call_llm(llm_client, prompt)
    parsed = _parse_and_validate(raw, schema) if raw else None

    if parsed is None:
        result = json.loads(json.dumps(PLACEHOLDER_STAGE3, ensure_ascii=False))
        result["stage1_ref"] = scheme_id_1
        result["stage2_ref"] = scheme_id_2
        return result

    parsed["stage1_ref"] = scheme_id_1
    parsed["stage2_ref"] = scheme_id_2
    return parsed
