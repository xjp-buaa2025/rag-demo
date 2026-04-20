"""
LLM 诊断模块：为每个 StageIssue 生成专家行动建议，SSE 流式 yield。
"""
from __future__ import annotations

import os
from typing import AsyncGenerator

from backend.kg_storage import StageReport, StageIssue


def _create_llm_client():
    """复用项目 LLM 配置（OpenAI 兼容 API）"""
    from openai import OpenAI
    return OpenAI(
        api_key=os.environ.get("LLM_API_KEY", ""),
        base_url=os.environ.get("LLM_BASE_URL", ""),
    )


_DIAGNOSIS_PROMPT = """你是一位知识图谱质量专家，正在帮助领域专家理解知识图谱构建过程中出现的问题。

以下是某个阶段（{stage}）的分析报告摘要：
- 实体总数：{entities_count}
- 三元组总数：{triples_count}
- 低置信度三元组（<0.5）：{low_conf_count}
- 孤立实体：{isolated_count}
{coverage_line}

其中检测到的问题是：
【{severity}】{title_zh}
详情：{description}

请用2-3句简洁的中文，向领域专家解释：
1. 这个问题最可能的根本原因是什么（数据质量？Prompt 设计？还是领域知识缺失？）
2. 专家最应该优先做什么（提供更好的数据？直接编辑三元组？还是补充领域知识？）

回答要直接、具体，不要泛泛而谈。"""


async def diagnose_issues_stream(
    report: StageReport,
) -> AsyncGenerator[dict, None]:
    """
    为 report 中的每个 issue 调用 LLM 生成详细建议。
    yield dict：
      {"type": "diagnosis_chunk", "issue_index": int, "content": str}
      {"type": "diagnosis_done"}
    """
    client = _create_llm_client()
    stats = report.stats
    coverage_line = (
        f"- BOM 覆盖率：{stats.bom_coverage_ratio:.0%}"
        if stats.bom_coverage_ratio is not None
        else ""
    )

    for i, issue in enumerate(report.issues):
        prompt = _DIAGNOSIS_PROMPT.format(
            stage=report.stage,
            entities_count=stats.entities_count,
            triples_count=stats.triples_count,
            low_conf_count=stats.low_confidence_count,
            isolated_count=stats.isolated_entities_count,
            coverage_line=coverage_line,
            severity=issue.severity,
            title_zh=issue.title_zh,
            description=issue.description,
        )

        stream = client.chat.completions.create(
            model=os.environ.get("LLM_MODEL", ""),
            messages=[{"role": "user", "content": prompt}],
            stream=True,
            max_tokens=200,
            temperature=0.3,
        )

        # stream 可能是同步可迭代（真实 OpenAI SDK）或异步生成器（测试 mock）
        import inspect
        if inspect.isasyncgen(stream):
            async for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    yield {"type": "diagnosis_chunk", "issue_index": i, "content": content}
        else:
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    yield {"type": "diagnosis_chunk", "issue_index": i, "content": content}

    yield {"type": "diagnosis_done"}
