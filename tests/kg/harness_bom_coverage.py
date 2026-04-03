"""
tests/kg/harness_bom_coverage.py — 层二：BOM part_id 覆盖率

前提：已准备 tests/kg/fixtures/sample_bom.csv（含 part_id, part_name 列）。
依赖：conftest.py 中的 neo4j_session / bom_part_ids fixture。

核心指标：
  coverage_rate = |KG中已对齐的part_id ∩ BOM fixture中的part_id| / |BOM fixture中的part_id|

覆盖判断依据：Neo4j 节点的 aligned_part_id 或 bom_part_id 字段中包含该 part_id。

阈值说明：
  COVERAGE_THRESHOLD_LOW  = 0.60  — 硬性门槛，低于此值 FAIL
  COVERAGE_THRESHOLD_HIGH = 0.80  — 推荐目标，低于此值打印警告但不 FAIL
  GHOST_RATIO_MAX         = 0.20  — 幽灵 part_id（对齐到不存在零件）上限

运行方式：
  pytest tests/kg/harness_bom_coverage.py -v -s
"""

import pytest

COVERAGE_THRESHOLD_LOW  = 0.60
COVERAGE_THRESHOLD_HIGH = 0.80
GHOST_RATIO_MAX         = 0.20


def _fetch_aligned_part_ids(neo4j_session) -> set:
    """
    从 Neo4j 拉取所有已对齐的 part_id（去重）。
    同时检查 aligned_part_id 和 bom_part_id 两个字段（写入时 coalesce）。
    """
    rows = neo4j_session.run(
        """
        MATCH (n)
        WHERE n.aligned_part_id IS NOT NULL
           OR n.bom_part_id IS NOT NULL
        RETURN coalesce(n.aligned_part_id, n.bom_part_id) AS pid
        """
    ).data()
    return {r["pid"] for r in rows if r.get("pid")}


class TestBomCoverage:

    def test_coverage_rate_above_threshold(self, neo4j_session, bom_part_ids):
        """
        KG 对齐覆盖的 BOM part_id 比例不低于 COVERAGE_THRESHOLD_LOW。
        低于 COVERAGE_THRESHOLD_HIGH 时打印警告（不 FAIL）。
        """
        aligned_ids = _fetch_aligned_part_ids(neo4j_session)
        total   = len(bom_part_ids)
        covered = len(bom_part_ids & aligned_ids)

        if total == 0:
            pytest.skip("BOM fixture 无有效 part_id，请检查 sample_bom.csv 的 part_id 列")

        rate = covered / total

        # 计算详细报告内容
        missed   = sorted(bom_part_ids - aligned_ids)[:20]
        extra    = sorted(aligned_ids  - bom_part_ids)[:10]
        report = (
            f"\nBOM 覆盖率报告："
            f"\n  BOM fixture 总零件数: {total}"
            f"\n  KG 已覆盖:            {covered}  ({rate:.1%})"
            f"\n  未覆盖（前20）:       {missed}"
            f"\n  KG 额外对齐（前10）: {extra}"
        )

        if rate < COVERAGE_THRESHOLD_HIGH:
            import warnings
            warnings.warn(
                f"覆盖率 {rate:.1%} 低于推荐值 {COVERAGE_THRESHOLD_HIGH:.0%}，"
                f"建议优化对齐策略。{report}",
                stacklevel=2
            )

        assert rate >= COVERAGE_THRESHOLD_LOW, (
            f"BOM 覆盖率 {rate:.1%}（{covered}/{total}）低于硬性门槛 "
            f"{COVERAGE_THRESHOLD_LOW:.0%}。{report}\n"
            f"根因（按可能性排序）：\n"
            f"  ① 四级对齐整体失效（所有节点为 unmatched）\n"
            f"  ② 手册文本与 BOM 零件名称无重叠（完全不同领域）\n"
            f"  ③ BOM 阶段产物未被 merge 节点消费（检查 stages_done 是否含 'bom'）\n"
            f"  ④ 写入 Neo4j 时 aligned_part_id 字段被遗漏"
        )

    def test_no_ghost_part_ids(self, neo4j_session, bom_part_ids):
        """
        KG 中 aligned_part_id 不应大量指向 BOM fixture 中不存在的零件。
        幽灵 ID 比例超过 GHOST_RATIO_MAX 说明模糊对齐产生了虚假命中。
        """
        if not bom_part_ids:
            pytest.skip("BOM fixture 为空，跳过幽灵 ID 检测")

        aligned_ids = _fetch_aligned_part_ids(neo4j_session)
        if not aligned_ids:
            pytest.skip("KG 无对齐数据，跳过幽灵 ID 检测")

        ghost_ids   = aligned_ids - bom_part_ids
        ghost_ratio = len(ghost_ids) / len(aligned_ids)

        assert ghost_ratio <= GHOST_RATIO_MAX, (
            f"幽灵 part_id 比例 {ghost_ratio:.1%}（{len(ghost_ids)}/{len(aligned_ids)}）"
            f"超过上限 {GHOST_RATIO_MAX:.0%}。\n"
            f"示例幽灵 ID（前10）：{sorted(ghost_ids)[:10]}\n"
            f"根因：\n"
            f"  ① 模糊对齐阈值 0.85 仍过低，产生误匹配\n"
            f"  ② sample_bom.csv 不完整，缺少相关子装配件\n"
            f"  ③ 历史残留数据未清除（建议执行 MATCH (n) DETACH DELETE n 后重建）"
        )

    def test_per_source_coverage(self, neo4j_session, bom_part_ids, capsys):
        """
        分 source 来源统计覆盖率（信息性，不 FAIL）。
        帮助判断哪个阶段（BOM/CAD/KG）贡献了对齐，定位最薄弱阶段。
        """
        if not bom_part_ids:
            pytest.skip("BOM fixture 为空，跳过分 source 覆盖率统计")

        rows = neo4j_session.run(
            """
            MATCH (n)
            WHERE (n.aligned_part_id IS NOT NULL OR n.bom_part_id IS NOT NULL)
              AND n.source IS NOT NULL
            RETURN
                n.source AS src,
                collect(coalesce(n.aligned_part_id, n.bom_part_id)) AS pids
            """
        ).data()

        if not rows:
            pytest.skip("无分 source 对齐数据")

        total = len(bom_part_ids)
        with capsys.disabled():
            print(f"\n{'='*50}")
            print(f"分 source 覆盖率（BOM fixture 总零件数: {total}）：")
            print(f"{'='*50}")
            for row in rows:
                covered = len(bom_part_ids & set(row["pids"]))
                pct     = covered / total * 100 if total > 0 else 0
                bar     = "█" * int(pct / 5)
                print(f"  {row['src']:10s}: {covered:3d}/{total}  ({pct:5.1f}%)  {bar}")
            print(f"{'='*50}")
