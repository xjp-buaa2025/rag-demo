"""
backend/pipelines/assembly_scheme/stage1_intake.py

S1: Task intake & research. See spec §2.1.

Steps:
  1. Build 3 web search queries from subject (zh + en + service_bulletin variants)
  2. Run KG snapshot (Neo4j) — degrades to {part_count: 0, warning: ...} when unavailable
  3. Run web_search for each query, collect results (await user review)
  4. Build LLM prompt = skill.prompts['s1_intake'] + methodology + retrieved data
  5. Call LLM to generate task_card_md (degrades to placeholder when llm_client is None)
  6. Return dict matching stage1.schema.json
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, List, Optional
import json
import logging

from backend.pipelines.assembly_scheme.skill_loader import SkillRegistry
from backend.tools.web_search import WebSearchClient

logger = logging.getLogger(__name__)


PLACEHOLDER_TASK_CARD = (
    "## 任务说明书\n\n"
    "（LLM 未配置或调用失败，返回占位符。请陛下手动补全后继续。）\n\n"
    "**目标**：（待 LLM 生成或人工填写）\n\n"
    "**范围**：（同上）\n\n"
    "**边界**：（同上）\n\n"
    "**约束**：（同上）\n\n"
    "**已知风险**：（同上）\n"
)


DEFAULT_COMPLIANCE_SCOPE = [
    "AS9100D §8.1 (运行的策划和控制)",
    "GJB 9001C §7.5 (生产和服务过程的控制)",
    "GJB 5060A-2014 (航空发动机装配通用要求)",
]


def build_search_queries(subject_name: str, subject_en: Optional[str] = None) -> List[str]:
    queries: List[str] = [f"{subject_name} 装配工艺规程 GJB"]
    if subject_en:
        queries.append(f"{subject_en} assembly procedure")
        queries.append(f"{subject_en} service bulletin assembly")
    return queries


def kg_snapshot(neo4j_driver: Any, subject_name: str) -> Dict[str, Any]:
    """Query Neo4j for an entity-count summary about subject_name.

    Degrades to {part_count: 0, ..., warning: ...} when driver is None or query fails.
    """
    if neo4j_driver is None:
        return {
            "part_count": 0,
            "assembly_count": 0,
            "key_interfaces": [],
            "relations_sample": [],
            "warning": "Neo4j driver unavailable",
        }

    cypher = (
        "MATCH (n) "
        "WHERE coalesce(n.kg_name, '') CONTAINS $subj OR coalesce(n.part_name, '') CONTAINS $subj "
        "OPTIONAL MATCH (n)-[r]->(m) "
        "RETURN count(DISTINCT n) AS nc, collect(DISTINCT type(r))[..5] AS rels"
    )
    try:
        with neo4j_driver.session() as session:
            rec = session.run(cypher, subj=subject_name).single()
            if rec:
                return {
                    "part_count": int(rec["nc"]),
                    "assembly_count": 0,  # split by label in future plan
                    "key_interfaces": [],
                    "relations_sample": list(rec["rels"]) if rec["rels"] else [],
                }
    except Exception as e:
        logger.error("KG snapshot query failed: %s", e)
        return {
            "part_count": 0,
            "assembly_count": 0,
            "key_interfaces": [],
            "relations_sample": [],
            "warning": f"KG query failed: {e}",
        }
    return {
        "part_count": 0,
        "assembly_count": 0,
        "key_interfaces": [],
        "relations_sample": [],
    }


def _call_llm_for_task_card(
    llm_client: Any,
    prompt_text: str,
) -> str:
    if llm_client is None:
        logger.warning("llm_client is None; returning placeholder task_card")
        return PLACEHOLDER_TASK_CARD
    try:
        resp = llm_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt_text}],
            temperature=0.3,
        )
        return resp.choices[0].message.content
    except Exception as e:
        logger.error("LLM call for task_card failed: %s", e)
        return PLACEHOLDER_TASK_CARD


def run_stage1_intake(
    user_input: Dict[str, Any],
    skill: SkillRegistry,
    web_search: WebSearchClient,
    llm_client: Any,
    neo4j_driver: Any,
) -> Dict[str, Any]:
    """Execute S1 pipeline. Returns a dict valid per stage1.schema.json."""
    subject = user_input["subject"]
    subject_name: str = subject["system"]
    subject_en: Optional[str] = subject.get("system_en")
    scheme_id: str = user_input["scheme_id"]

    # 1. KG snapshot
    snap = kg_snapshot(neo4j_driver, subject_name)

    # 2. Web search
    queries = build_search_queries(subject_name, subject_en)
    web_results: List[Dict[str, Any]] = []
    for q in queries:
        for r in web_search.search(q, max_results=3):
            d = asdict(r)
            d["selected"] = None  # awaiting user review
            web_results.append(d)

    # 3. Build LLM prompt
    prompt_template = skill.prompts.get("s1_intake", "")
    methodology = skill.methodology.get("s1_intake_and_research", "")
    full_prompt = (
        f"{prompt_template}\n\n"
        f"## 方法论上下文\n{methodology}\n\n"
        f"## 用户输入\n```json\n{json.dumps(user_input, ensure_ascii=False, indent=2)}\n```\n\n"
        f"## KG 快照\n```json\n{json.dumps(snap, ensure_ascii=False, indent=2)}\n```\n\n"
        f"## Web 检索摘要（已附 confidence，待审核）\n"
        f"```json\n{json.dumps([{'id': r['id'], 'title': r['title'], 'excerpt': r['excerpt'][:200], 'confidence': r['confidence']} for r in web_results], ensure_ascii=False, indent=2)}\n```\n\n"
        "请生成 task_card_md（仅 Markdown 文本，含五栏：目标 / 范围 / 边界 / 约束 / 已知风险）："
    )

    # 4. Call LLM
    task_card = _call_llm_for_task_card(llm_client, full_prompt)

    # 5. Assemble result
    return {
        "scheme_id": scheme_id,
        "subject": subject,
        "kg_snapshot": snap,
        "web_search_results": web_results,
        "vision_notes": user_input.get("vision_notes", ""),
        "compliance_scope": list(DEFAULT_COMPLIANCE_SCOPE),
        "task_card_md": task_card,
    }
