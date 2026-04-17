"""tests/kg/test_enrich_bom.py — enrich_bom_links 三级对齐单元测试"""
import pytest
from backend.pipelines.kg_postprocess import enrich_bom_links

# ── 公共 BOM fixture ──────────────────────────────────────────────────────────
BOM_ENTITIES = [
    {"id": "MS9556-07", "name": "BOLT,MACHINE,DBL HEX",     "part_number": "MS9556-07"},
    {"id": "3034344",   "name": "COMPRESSOR ROTOR INSTALLATION", "part_number": "3034344"},
    {"id": "MS9767-09", "name": "NUT,SELF-LOCKING,HEX",     "part_number": "MS9767-09"},
    {"id": "AS3209-267","name": "PACKING,PREFORMED",        "part_number": "AS3209-267"},
    {"id": "3103074-01","name": "COMPRESSOR ROTOR",         "part_number": "3103074-01"},
]


# ── Task 1: Level 1.5 正则零件编号提取 ────────────────────────────────────────

class TestLevel15Regex:
    def test_ms_number_in_head(self):
        """head 文本中含 MS 编号，应命中 Level 1.5"""
        triples = [{"head": "Nut MS9767-09", "tail": "SomeProc",
                    "head_type": "Part", "tail_type": "Procedure",
                    "relation": "participatesIn"}]
        result = enrich_bom_links(triples, BOM_ENTITIES)
        t = result["triples"][0]
        assert t["head_bom_id"] == "MS9767-09"
        assert t["head_align_method"] == "regex"
        assert result["stats"]["regex_hits"] == 1

    def test_7digit_number_in_tail(self):
        """tail 文本中含 7 位数字编号，应命中 Level 1.5"""
        triples = [{"head": "SomeProc", "tail": "Assembly 3034344",
                    "head_type": "Procedure", "tail_type": "Assembly",
                    "relation": "precedes"}]
        result = enrich_bom_links(triples, BOM_ENTITIES)
        t = result["triples"][0]
        assert t["tail_bom_id"] == "3034344"
        assert t["tail_align_method"] == "regex"

    def test_as_number_matched(self):
        """AS 前缀编号（如 AS3209-267）应被正则捕获"""
        triples = [{"head": "Packing AS3209-267", "tail": "Install",
                    "head_type": "Part", "tail_type": "Procedure",
                    "relation": "participatesIn"}]
        result = enrich_bom_links(triples, BOM_ENTITIES)
        assert result["triples"][0]["head_bom_id"] == "AS3209-267"

    def test_no_number_not_matched_by_regex(self):
        """无编号的纯文本不应被 Level 1.5 命中"""
        triples = [{"head": "COMPRESSOR BLADE", "tail": "Install",
                    "head_type": "Part", "tail_type": "Procedure",
                    "relation": "participatesIn"}]
        result = enrich_bom_links(triples, BOM_ENTITIES)
        assert result["stats"]["regex_hits"] == 0


# ── Task 2: Level 1.6 CAD 启发式映射 ─────────────────────────────────────────

class TestLevel16CadHeuristic:
    def test_cad_style_name_matched(self):
        """CAD 风格名称 C3034344 应通过数字主体子串匹配到 BOM"""
        triples = [{"head": "C3034344", "tail": "Install",
                    "head_type": "Part", "tail_type": "Procedure",
                    "relation": "participatesIn"}]
        result = enrich_bom_links(triples, BOM_ENTITIES)
        t = result["triples"][0]
        assert t.get("head_bom_id") == "3034344"
        assert t.get("head_align_method") == "cad_heuristic"
        assert result["stats"]["cad_hits"] == 1

    def test_ambiguous_cad_not_matched(self):
        """数字主体不在 BOM 中时，返回 unmatched"""
        triples2 = [{"head": "CXXX0000", "tail": "Install",
                     "head_type": "Part", "tail_type": "Procedure",
                     "relation": "participatesIn"}]
        result = enrich_bom_links(triples2, BOM_ENTITIES)
        assert result["triples"][0].get("head_bom_id") is None


# ── Task 2: Level 1.7 Jaccard 关键词匹配 ─────────────────────────────────────

class TestLevel17Jaccard:
    def test_compressor_rotor_matched(self):
        """'COMPRESSOR ROTOR' 与 BOM 'COMPRESSOR ROTOR INSTALLATION' Jaccard 应命中"""
        triples = [{"head": "COMPRESSOR ROTOR", "tail": "Install",
                    "head_type": "Assembly", "tail_type": "Procedure",
                    "relation": "participatesIn"}]
        result = enrich_bom_links(triples, BOM_ENTITIES)
        t = result["triples"][0]
        # Jaccard("COMPRESSOR ROTOR", "COMPRESSOR ROTOR INSTALLATION") = 2/3 ≈ 0.67 ≥ 0.35
        assert t.get("head_bom_id") in ("3034344", "3103074-01")
        assert t.get("head_align_method") == "keyword_jaccard"
        assert result["stats"]["keyword_hits"] == 1

    def test_procedure_entity_not_aligned(self):
        """Procedure 类型实体不应参与 BOM 对齐"""
        triples = [{"head": "Install Rotor", "tail": "Install",
                    "head_type": "Procedure", "tail_type": "Procedure",
                    "relation": "precedes"}]
        result = enrich_bom_links(triples, BOM_ENTITIES)
        assert result["triples"][0].get("head_bom_id") is None
        assert result["triples"][0].get("tail_bom_id") is None

    def test_low_jaccard_not_matched(self):
        """Jaccard < 0.35 的实体不应被命中"""
        triples = [{"head": "TURBINE BLADE", "tail": "Install",
                    "head_type": "Part", "tail_type": "Procedure",
                    "relation": "participatesIn"}]
        result = enrich_bom_links(triples, BOM_ENTITIES)
        # TURBINE BLADE vs BOM names: 无交集满足 ≥0.35
        assert result["triples"][0].get("head_bom_id") is None

    def test_stats_total_counts_triples_not_fields(self):
        """stats.total 应为三元组数量"""
        triples = [
            {"head": "Nut MS9767-09", "tail": "Install",
             "head_type": "Part", "tail_type": "Procedure", "relation": "participatesIn"},
            {"head": "TURBINE BLADE", "tail": "Install",
             "head_type": "Part", "tail_type": "Procedure", "relation": "participatesIn"},
        ]
        result = enrich_bom_links(triples, BOM_ENTITIES)
        assert result["stats"]["total"] == 2
        assert result["stats"]["regex_hits"] == 1
