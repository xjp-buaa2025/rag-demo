"""
三元组中英文翻译模块。翻译结果缓存到 translations.json，避免重复调用 LLM。
"""
from __future__ import annotations

import json
import os
from typing import Dict, List

from backend.kg_storage import read_translations, write_translations

# 关系类型固定译名（无需 LLM）
_RELATION_MAP: Dict[str, str] = {
    "isPartOf": "属于",
    "matesWith": "配合",
    "precedes": "先于",
    "participatesIn": "参与",
    "requires": "需要",
    "specifiedBy": "规定于",
    "hasInterface": "具有接口",
    "interchangesWith": "可互换",
    "hasComponent": "包含",
    "hasConstraint": "有约束",
    "isAdjacentTo": "相邻",
}


def _create_llm_client():
    from openai import OpenAI
    return OpenAI(
        api_key=os.environ.get("LLM_API_KEY", ""),
        base_url=os.environ.get("LLM_BASE_URL", ""),
    )


_TRANSLATE_PROMPT = """请将以下航空发动机领域的英文术语翻译为中文。
返回严格的 JSON 对象，key 为英文原文，value 为中文译名。
不要添加任何解释。

术语列表：
{terms}"""


def translate_terms(terms: List[str]) -> Dict[str, str]:
    """
    翻译一批术语。优先从缓存读取，未命中的批量调用 LLM。
    """
    cache = read_translations()

    # 先用固定映射填充
    for t in terms:
        if t in _RELATION_MAP and t not in cache:
            cache[t] = _RELATION_MAP[t]

    missing = [t for t in terms if t not in cache]
    if not missing:
        return {t: cache[t] for t in terms}

    # 调用 LLM 翻译缺失部分
    client = _create_llm_client()
    prompt = _TRANSLATE_PROMPT.format(terms="\n".join(f"- {t}" for t in missing))
    resp = client.chat.completions.create(
        model=os.environ.get("LLM_MODEL", ""),
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0,
    )
    raw = resp.choices[0].message.content.strip()

    # 解析 JSON（容错：去掉 markdown 代码块）
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    try:
        new_translations = json.loads(raw)
        cache.update(new_translations)
        write_translations(cache)
    except json.JSONDecodeError:
        pass  # 解析失败时保持原英文，不中断流程

    return {t: cache.get(t, t) for t in terms}


def translate_triples_batch(triples: List[dict]) -> List[dict]:
    """
    为三元组列表增加 head_zh / relation_zh / tail_zh 字段。
    修改原始 dict（返回同一列表，方便链式调用）。
    """
    all_terms: List[str] = []
    for t in triples:
        all_terms.extend([t.get("head", ""), t.get("relation", ""), t.get("tail", "")])
    unique_terms = list(set(filter(None, all_terms)))
    translations = translate_terms(unique_terms)

    for t in triples:
        t["head_zh"] = translations.get(t.get("head", ""), t.get("head", ""))
        t["relation_zh"] = translations.get(t.get("relation", ""), t.get("relation", ""))
        t["tail_zh"] = translations.get(t.get("tail", ""), t.get("tail", ""))

    return triples
