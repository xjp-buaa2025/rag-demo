"""backend/pipelines/assembly_scheme/stage2_requirements.py — S2 Requirements & constraints analysis."""

from __future__ import annotations
from typing import Any, Dict, Optional
import json
import logging
import jsonschema
from backend.pipelines.assembly_scheme.skill_loader import SkillRegistry

logger = logging.getLogger(__name__)

PLACEHOLDER_STAGE2: Dict[str, Any] = {
    "stage1_ref": "PLACEHOLDER",
    "user_needs": [{"id": "U1", "text": "（占位：高可靠性，待 chamberlain 补全）", "weight": 5}],
    "engineering_metrics": [{"id": "M1", "name": "MTBF", "target": "（占位：待补具体数字）", "linked_needs": ["U1"]}],
    "assembly_features": [{"id": "F1", "name": "（占位）关键装配特征", "spec": "（占位）", "linked_metrics": ["M1"]}],
    "key_characteristics": [{"id": "KC1", "name": "（占位）关键尺寸", "target": "（占位）", "criticality": "high", "linked_features": ["F1"]}],
    "dfa_score": {"overall": 0.5, "theoretical_min_parts": 1, "actual_parts": 1, "method": "placeholder", "bottlenecks": []},
    "risks": [{"id": "R1", "text": "（占位）需要 chamberlain 在 HITL 补具体风险", "severity": 3, "linked_kcs": ["KC1"]}],
    "uncertainty": "高",
}


def _build_prompt(skill, stage1_payload, rag_methodology, kg_failure_modes, user_guidance):
    prompt_template = skill.prompts.get("s2_requirements", "")
    methodology = skill.methodology.get("s2_requirements_qfd", "")
    return (
        f"{prompt_template}\n\n"
        f"## 方法论上下文\n{methodology}\n\n"
        f"## 额外 RAG 方法论片段\n{rag_methodology or '（无）'}\n\n"
        f"## KG 失效模式（历史）\n{json.dumps(kg_failure_modes, ensure_ascii=False, indent=2)}\n\n"
        f"## S1 产物\n```json\n{json.dumps(stage1_payload, ensure_ascii=False, indent=2)}\n```\n\n"
        f"## chamberlain 指导意见\n{user_guidance or '（无）'}\n\n"
        "请生成符合 stage2.schema.json 的 JSON 对象："
    )


def _query_failure_modes(neo4j_driver, subject_name):
    if neo4j_driver is None:
        return []
    try:
        cypher = (
            "MATCH (p)-[:failureMode]->(f) "
            "WHERE coalesce(p.kg_name, '') CONTAINS $subj OR coalesce(p.part_name, '') CONTAINS $subj "
            "RETURN f.text AS text, f.severity AS severity LIMIT 10"
        )
        with neo4j_driver.session() as session:
            return session.run(cypher, subj=subject_name).data()
    except Exception as e:
        logger.warning("KG failure-mode query failed: %s", e)
        return []


def _call_llm(llm_client, prompt):
    if llm_client is None:
        return None
    try:
        resp = llm_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}], temperature=0.2,
        )
        return resp.choices[0].message.content
    except Exception as e:
        logger.error("Stage2 LLM call failed: %s", e)
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
        logger.warning("Stage2 LLM JSON parse failed: %s; raw=%s", e, raw[:200])
        return None
    try:
        jsonschema.validate(instance=obj, schema=schema)
    except jsonschema.ValidationError as e:
        logger.warning("Stage2 LLM output failed schema: %s", e.message)
        return None
    return obj


def run_stage2_requirements(
    stage1_payload: Dict[str, Any],
    skill: SkillRegistry,
    llm_client: Any,
    rag_searcher: Any = None,
    neo4j_driver: Any = None,
    user_guidance: Optional[str] = None,
) -> Dict[str, Any]:
    """Execute S2 pipeline. Returns a dict valid per stage2.schema.json."""
    schema = skill.schemas["stage2"]
    scheme_id = stage1_payload["scheme_id"]

    rag_methodology = ""
    if rag_searcher is not None:
        try:
            hits = rag_searcher.search("装配可靠性 指标 QFD", top_k=3)
            rag_methodology = "\n---\n".join(h.get("text", "") for h in hits)
        except Exception as e:
            logger.warning("Stage2 RAG search failed: %s", e)

    failure_modes = _query_failure_modes(neo4j_driver, stage1_payload["subject"]["system"])
    prompt = _build_prompt(skill, stage1_payload, rag_methodology, failure_modes, user_guidance)
    raw = _call_llm(llm_client, prompt)
    parsed = _parse_and_validate(raw, schema) if raw else None

    if parsed is None:
        result = json.loads(json.dumps(PLACEHOLDER_STAGE2, ensure_ascii=False))
        result["stage1_ref"] = scheme_id
        return result

    parsed["stage1_ref"] = scheme_id
    return parsed
