"""
tests/kg/harness_structural.py — 层一：KG 图结构自检

在 KG 构建完成后运行，验证 Neo4j 中图结构的基本不变量。
无需 sample_bom.csv 或 golden_triples.json，完全依赖 Neo4j 数据。

覆盖检查项：
  1. 节点类型完备性：6 种标签都存在节点
  2. 必要属性非空：kg_id / kg_name / part_id 不得缺失
  3. 关系类型覆盖：precedes / participatesIn / isPartOf 至少各有 1 条
  4. precedes 无环：Kahn 修复后不应存在 (a)-[:precedes*]->(a)
  5. 孤立节点率：无关系节点占比 ≤ 30%（阈值可调）
  6. 对齐方法分布：unmatched 占比 ≤ 70%，并打印分布报告

运行方式：
  pytest tests/kg/harness_structural.py -v -s
"""

import pytest

# ── 可调阈值 ──────────────────────────────────────────────────────────────────
MAX_ORPHAN_RATIO    = 0.30   # 孤立节点（无任何关系）占 KG 节点比例上限
MAX_UNMATCHED_RATIO = 0.70   # alignment_method='unmatched' 节点占比上限

# KG 实体标签（来自 nodes_kg.py _LABEL_MAP）
REQUIRED_LABELS = [
    "Part", "Assembly", "Procedure", "Tool", "Specification", "Interface"
]

# 必须存在的关系类型（各至少 1 条）
REQUIRED_REL_TYPES = ["precedes", "participatesIn", "isPartOf"]


# ── 层一·A：节点完备性 ─────────────────────────────────────────────────────────

class TestNodeCompleteness:
    """验证 KG 中各实体标签均有数据，排除空图或写入完全失败的情况。"""

    @pytest.mark.parametrize("label", REQUIRED_LABELS)
    def test_label_exists(self, neo4j_session, label):
        """每种实体标签都应至少有 1 个节点。"""
        result = neo4j_session.run(
            f"MATCH (n:{label}) RETURN count(n) AS cnt"
        ).single()
        cnt = result["cnt"] if result else 0
        assert cnt > 0, (
            f"标签 [{label}] 无节点。\n"
            f"可能根因：\n"
            f"  ① 该类型三元组提取失败（检查 LLM 提示词中 entity_type 映射）\n"
            f"  ② nodes_kg.py _LABEL_MAP 未包含该标签\n"
            f"  ③ 对应阶段的 pipeline 未执行（检查 stages_done）"
        )

    def test_total_node_count_reasonable(self, neo4j_session):
        """KG 总节点数应 > 10，排除空图写入场景。"""
        result = neo4j_session.run(
            """
            MATCH (n)
            WHERE n.kg_id IS NOT NULL OR n.part_id IS NOT NULL
            RETURN count(n) AS cnt
            """
        ).single()
        cnt = result["cnt"] if result else 0
        assert cnt > 10, (
            f"KG 节点总数仅 {cnt}，图可能未正确写入。\n"
            f"检查：① write_kg_neo4j_unified 是否成功执行；② Neo4j 连接是否指向正确数据库"
        )


# ── 层一·B：必要属性非空 ───────────────────────────────────────────────────────

class TestRequiredProperties:
    """验证 pipeline 写入时不遗漏关键标识字段。"""

    @pytest.mark.parametrize("label", ["Procedure", "Tool", "Specification"])
    def test_kg_id_not_null(self, neo4j_session, label):
        """
        从手册提取的 KG 节点必须有 kg_id（write_kg_neo4j 的 MERGE key）。
        缺失说明 _make_entity_id 返回了空串或 None。
        """
        result = neo4j_session.run(
            f"MATCH (n:{label}) WHERE n.kg_id IS NULL RETURN count(n) AS cnt"
        ).single()
        cnt = result["cnt"] if result else 0
        assert cnt == 0, (
            f"[{label}] 节点中有 {cnt} 个缺少 kg_id。\n"
            f"检查 nodes_kg.py::_make_entity_id，确保 entity.text 非空"
        )

    def test_kg_name_not_null(self, neo4j_session):
        """所有带 kg_id 的节点都应有 kg_name（entity.text 映射字段）。"""
        result = neo4j_session.run(
            """
            MATCH (n)
            WHERE n.kg_id IS NOT NULL
              AND (n.kg_name IS NULL OR n.kg_name = '')
            RETURN count(n) AS cnt
            """
        ).single()
        cnt = result["cnt"] if result else 0
        assert cnt == 0, (
            f"{cnt} 个 KG 节点缺少 kg_name。\n"
            f"检查 write_kg_neo4j 中 SET n.kg_name = entity['text'] 是否执行"
        )

    def test_bom_nodes_have_part_id(self, neo4j_session):
        """
        来源为 BOM 的节点应有 part_id 或 bom_part_id。
        缺失说明 bom_to_triples_node 构造的 entity 未携带 part_id。
        """
        result = neo4j_session.run(
            """
            MATCH (n)
            WHERE n.source = 'BOM'
              AND n.part_id IS NULL
              AND n.bom_part_id IS NULL
            RETURN count(n) AS cnt
            """
        ).single()
        cnt = result["cnt"] if result else 0
        assert cnt == 0, (
            f"{cnt} 个 BOM 来源节点缺少 part_id/bom_part_id。\n"
            f"检查 nodes_kg_unified.py::bom_to_triples_node 的 entity 构造"
        )


# ── 层一·C：关系类型覆盖 ───────────────────────────────────────────────────────

class TestRelationTypes:
    """验证三源合并后图中存在必要的关系类型。"""

    @pytest.mark.parametrize("rel_type", REQUIRED_REL_TYPES)
    def test_relation_type_exists(self, neo4j_session, rel_type):
        """每种必要关系类型至少存在 1 条。"""
        result = neo4j_session.run(
            f"MATCH ()-[r:{rel_type}]->() RETURN count(r) AS cnt"
        ).single()
        cnt = result["cnt"] if result else 0
        assert cnt > 0, (
            f"关系类型 [{rel_type}] 无数据。\n"
            f"根因分析：\n"
            f"  precedes / participatesIn 缺失 → 手册解析链（nodes_manual.py → extract_kg_triples）未完成\n"
            f"  isPartOf 缺失 → BOM 或 CAD 阶段未完成，或 merge 阶段未执行"
        )

    def test_precedes_dag_no_self_loop(self, neo4j_session):
        """
        precedes 关系经 validate_kg_dag（Kahn 算法）修复后不应存在自回路。
        使用最大深度 20 防止 Cypher 超时。
        """
        result = neo4j_session.run(
            "MATCH (a:Procedure)-[:precedes*1..20]->(a) "
            "RETURN count(a) AS cnt LIMIT 1"
        ).single()
        cnt = result["cnt"] if result else 0
        assert cnt == 0, (
            f"发现 {cnt} 个 precedes 循环节点，validate_kg_dag 修复未生效。\n"
            f"检查 nodes_kg.py::validate_kg_dag 的 Kahn 算法实现"
        )


# ── 层一·D：孤立节点率 ─────────────────────────────────────────────────────────

class TestOrphanNodes:
    """验证写入关系时 MATCH 命中率，避免大量节点成为孤岛。"""

    def test_orphan_ratio_below_threshold(self, neo4j_session):
        """
        无任何关系的 KG 节点占比不超过 MAX_ORPHAN_RATIO。
        孤立节点过多说明 _write_kg_relations_batch 中 MATCH (a {kg_id:...}) 大量未命中。
        """
        total_r = neo4j_session.run(
            "MATCH (n) WHERE n.kg_id IS NOT NULL RETURN count(n) AS cnt"
        ).single()
        orphan_r = neo4j_session.run(
            "MATCH (n) WHERE n.kg_id IS NOT NULL AND NOT (n)--() "
            "RETURN count(n) AS cnt"
        ).single()

        total  = total_r["cnt"]  if total_r  else 0
        orphan = orphan_r["cnt"] if orphan_r else 0

        if total == 0:
            pytest.skip("KG 节点总数为 0，跳过孤立节点检测")

        ratio = orphan / total
        assert ratio <= MAX_ORPHAN_RATIO, (
            f"孤立节点率 {ratio:.1%}（{orphan}/{total}）超过阈值 {MAX_ORPHAN_RATIO:.0%}。\n"
            f"根因：\n"
            f"  ① 关系写入时 MATCH (a {{kg_id: ...}}) 未命中（kg_id 与节点写入时不一致）\n"
            f"  ② 三源 ID 混用（bom_xxx/cad_xxx/LLM-local），merge 阶段 gid 对齐失败\n"
            f"  ③ from_id/to_id 在 align 阶段被修改，但关系列表未同步更新"
        )


# ── 层一·E：对齐方法分布 ───────────────────────────────────────────────────────

class TestAlignmentDistribution:
    """验证实体对齐四级级联的整体效果。"""

    def test_unmatched_ratio_below_threshold(self, neo4j_session):
        """
        alignment_method='unmatched' 的节点占比不超过 MAX_UNMATCHED_RATIO。
        超过说明四级对齐整体失效，通常是 BOM 未先于手册入库。
        """
        total_r = neo4j_session.run(
            "MATCH (n) WHERE n.alignment_method IS NOT NULL "
            "RETURN count(n) AS cnt"
        ).single()
        unmatched_r = neo4j_session.run(
            "MATCH (n) WHERE n.alignment_method = 'unmatched' "
            "RETURN count(n) AS cnt"
        ).single()

        total     = total_r["cnt"]     if total_r     else 0
        unmatched = unmatched_r["cnt"] if unmatched_r else 0

        if total == 0:
            pytest.skip("无带 alignment_method 的节点，跳过对齐分布检测（可能 BOM 阶段未完成）")

        ratio = unmatched / total
        assert ratio <= MAX_UNMATCHED_RATIO, (
            f"unmatched 率 {ratio:.1%}（{unmatched}/{total}）超过阈值 {MAX_UNMATCHED_RATIO:.0%}。\n"
            f"根因（按可能性排序）：\n"
            f"  ① BOM 未先于手册入库（stages_done 缺少 'bom'）\n"
            f"  ② AVIATION_ABBREV 缩写词典未覆盖当前文本中的术语\n"
            f"  ③ 语义对齐 Qdrant 连接失败或集合为空\n"
            f"  ④ 模糊匹配阈值 0.85 过高，导致合理匹配被拒"
        )

    def test_alignment_method_distribution(self, neo4j_session, capsys):
        """
        打印对齐方法分布报告（信息性，不 FAIL）。
        帮助调优：pre_align > rule > fuzzy > semantic > unmatched 是健康分布。
        """
        results = neo4j_session.run(
            """
            MATCH (n) WHERE n.alignment_method IS NOT NULL
            RETURN n.alignment_method AS method, count(n) AS cnt
            ORDER BY cnt DESC
            """
        ).data()

        if not results:
            pytest.skip("无对齐数据，跳过分布报告")

        total = sum(r["cnt"] for r in results)
        lines = [f"\n{'='*50}", "对齐方法分布报告：", f"{'='*50}"]
        for r in results:
            pct  = r["cnt"] / total * 100
            bar  = "█" * int(pct / 2)
            flag = " ⚠ 过高" if r["method"] == "unmatched" and pct > 70 else ""
            lines.append(f"  {r['method']:25s}: {r['cnt']:5d}  ({pct:5.1f}%)  {bar}{flag}")
        lines.append(f"{'='*50}")
        with capsys.disabled():
            print("\n".join(lines))
