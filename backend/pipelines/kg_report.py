"""
Stage 完成后的统计分析模块。不调用 LLM，同步执行。
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from backend.kg_storage import (
    StageReport, StageStats, StageIssue, StageDiff,
)


def generate_stage_report(
    stage: str,
    current_data: dict,
    prev_data: Optional[dict] = None,
    bom_data: Optional[dict] = None,
) -> StageReport:
    """
    Args:
        stage: "bom" | "manual"
        current_data: 当前 Stage 的 JSON 数据（含 triples/entities/stats）
        prev_data: 上次运行的 JSON 数据（用于生成 diff），首次为 None
        bom_data: Stage 2 时传入 Stage 1 的数据，用于计算覆盖率
    """
    triples = current_data.get("triples", [])
    entities = current_data.get("entities", [])

    stats = _compute_stats(stage, triples, entities, bom_data)
    issues = _detect_issues(stage, stats)
    diff = _compute_diff(triples, prev_data.get("triples", []) if prev_data else None)

    return StageReport(
        stage=stage,
        generated_at=datetime.now(timezone.utc).isoformat(),
        stats=stats,
        issues=issues,
        diff=diff,
    )


def _compute_stats(
    stage: str,
    triples: list,
    entities: list,
    bom_data: Optional[dict],
) -> StageStats:
    # 关系类型分布
    relation_breakdown: dict[str, int] = {}
    for t in triples:
        rel = t.get("relation", "unknown")
        relation_breakdown[rel] = relation_breakdown.get(rel, 0) + 1

    # 置信度直方图（5个区间）
    boundaries = [0.0, 0.2, 0.4, 0.6, 0.8, 1.001]
    counts = [0] * 5
    for t in triples:
        c = float(t.get("confidence", 0))
        for i in range(5):
            if boundaries[i] <= c < boundaries[i + 1]:
                counts[i] += 1
                break
    total = len(triples) or 1
    histogram = [round(c / total, 4) for c in counts]

    # 低置信度
    low_conf = sum(1 for t in triples if float(t.get("confidence", 0)) < 0.5)

    # 孤立实体（在 entities 里但未出现在任何三元组中）
    appeared = set()
    for t in triples:
        appeared.add(t.get("head", ""))
        appeared.add(t.get("tail", ""))
    entity_names = {e.get("name", e.get("id", "")) for e in entities}
    isolated = entity_names - appeared if entity_names else set()
    isolated_count = len(isolated)

    # BOM 覆盖率（Stage 2 专用）
    bom_coverage = None
    if stage == "manual" and bom_data:
        bom_entity_ids = {
            e.get("id", e.get("name", ""))
            for e in bom_data.get("entities", [])
        }
        covered = set()
        for t in triples:
            if t.get("head_bom_id"):
                covered.add(t["head_bom_id"])
            if t.get("tail_bom_id"):
                covered.add(t["tail_bom_id"])
        bom_coverage = round(len(covered) / len(bom_entity_ids), 4) if bom_entity_ids else 0.0

    return StageStats(
        entities_count=len(entities),
        triples_count=len(triples),
        relation_breakdown=relation_breakdown,
        confidence_histogram=histogram,
        bom_coverage_ratio=bom_coverage,
        isolated_entities_count=isolated_count,
        low_confidence_count=low_conf,
    )


def _detect_issues(stage: str, stats: StageStats) -> list[StageIssue]:
    issues: list[StageIssue] = []

    # 规则1：低置信度三元组占比超过 30%
    low_ratio = stats.low_confidence_count / (stats.triples_count or 1)
    if low_ratio > 0.3:
        issues.append(StageIssue(
            severity="critical",
            title="High low-confidence triple ratio",
            title_zh="低置信度三元组占比过高",
            description=f"{stats.low_confidence_count} / {stats.triples_count} 条三元组置信度 < 0.5（占比 {low_ratio:.0%}）",
            suggestion="建议调低置信度阈值或检查 LLM Prompt 质量；也可在编辑面板手动修正",
        ))

    # 规则2：孤立实体超过 10%
    isolated_ratio = stats.isolated_entities_count / (stats.entities_count or 1)
    if isolated_ratio > 0.1:
        issues.append(StageIssue(
            severity="warning",
            title="Isolated entities detected",
            title_zh="存在孤立实体",
            description=f"{stats.isolated_entities_count} 个实体没有与任何其他实体建立关系（占比 {isolated_ratio:.0%}）",
            suggestion="在编辑面板为孤立实体手动补充关系，或确认是否为数据噪声",
        ))

    # 规则3：Stage 2 BOM 覆盖率过低
    if stage == "manual" and stats.bom_coverage_ratio is not None:
        if stats.bom_coverage_ratio < 0.4:
            issues.append(StageIssue(
                severity="critical",
                title="Low BOM coverage in manual stage",
                title_zh="手册对 BOM 覆盖率过低",
                description=f"手册三元组仅覆盖了 {stats.bom_coverage_ratio:.0%} 的 BOM 实体（预期 > 40%）",
                suggestion="建议提供更完整的手册章节，或通过「输入领域知识」补充关键零件的装配关系",
            ))

    # 规则4：三元组总数过少
    min_triples = {"bom": 10, "manual": 20}.get(stage, 10)
    if stats.triples_count < min_triples:
        issues.append(StageIssue(
            severity="critical",
            title="Too few triples extracted",
            title_zh="提取三元组数量过少",
            description=f"仅提取到 {stats.triples_count} 条三元组（{stage} 阶段预期至少 {min_triples} 条）",
            suggestion="检查输入文件质量；若为扫描件，建议提供更清晰版本或文字版 PDF",
        ))

    return issues


def _compute_diff(
    current_triples: list,
    prev_triples: Optional[list],
) -> Optional[StageDiff]:
    if prev_triples is None:
        return None

    def triple_key(t: dict) -> str:
        return f"{t.get('head','')}__{t.get('relation','')}__{t.get('tail','')}"

    prev_keys = {triple_key(t): t for t in prev_triples}
    curr_keys = {triple_key(t): t for t in current_triples}

    added = [curr_keys[k] for k in curr_keys if k not in prev_keys]
    removed = [prev_keys[k] for k in prev_keys if k not in curr_keys]

    return StageDiff(added_triples=added, removed_triples=removed, modified_triples=[])
