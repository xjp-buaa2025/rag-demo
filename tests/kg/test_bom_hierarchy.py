"""tests/kg/test_bom_hierarchy.py — BOM 层级修复单元测试"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[2]))

from backend.routers.kg_stages import _clean_ocr_noise


class TestCleanOcrNoise:

    def test_fixes_0F(self):
        assert _clean_ocr_noise("COMP0NENT 0F ENGINE") == "COMPONENT OF ENGINE"

    def test_fixes_C0MPONENT(self):
        assert _clean_ocr_noise("C0MPONENT SEAL") == "COMPONENT SEAL"

    def test_fixes_N0(self):
        assert _clean_ocr_noise("BEARING N0.1") == "BEARING NO.1"

    def test_fixes_0VS(self):
        assert _clean_ocr_noise("0VS SEAL") == "OVS SEAL"

    def test_preserves_decimal(self):
        # 小数点不应被误改
        assert _clean_ocr_noise("0.129-0.131 IN.") == "0.129-0.131 IN."

    def test_no_change_on_clean_text(self):
        text = "SEAL ASSEMBLY, AIR, COMPRESSOR"
        assert _clean_ocr_noise(text) == text

    def test_fixes_0N(self):
        assert _clean_ocr_noise("RATIO 0N ASSEMBLY") == "RATIO ON ASSEMBLY"

    def test_combined_noise(self):
        assert _clean_ocr_noise("C0MPONENT 0F 0N SEAL") == "COMPONENT OF ON SEAL"


class TestCleanOcrNoiseIntegration:
    """验证 _bom_df_to_entities_and_triples 内部对字段做了净化。"""

    def test_nomenclature_cleaned_in_triples(self):
        import json
        from backend.routers.kg_stages import _bom_df_to_entities_and_triples

        records = [
            {
                "part_id": "3034344",
                "part_name": "COMP0NENT SEAL",
                "nomenclature": "COMP0NENT SEAL",
                "fig_item": "1",
                "parent_id": "",
                "qty": 1,
                "category": "Assembly",
            },
            {
                "part_id": "3030349",
                "part_name": "SEAL AIR",
                "nomenclature": ".SEAL AIR",
                "fig_item": "2",
                "parent_id": "",
                "qty": 1,
                "category": "Part",
            },
        ]
        df_json = json.dumps(records)
        entities, triples = _bom_df_to_entities_and_triples(df_json)
        # 实体名称中不应包含 COMP0NENT
        names = [e["name"] for e in entities]
        assert all("COMP0NENT" not in n for n in names), f"OCR噪声未被清理: {names}"
        # 第二条应挂到第一条下（点号层级）
        child_triple = next((t for t in triples if "SEAL AIR" in t["head"]), None)
        assert child_triple is not None
        assert child_triple["tail"] != "ROOT", f"子件未正确连接父节点，tail={child_triple['tail']}"


class TestOcrBomPrompt:
    """验证 Prompt 包含关键规则和示例。"""

    def test_prompt_has_nha_rule(self):
        from backend.routers.kg_stages import _OCR_BOM_PROMPT
        assert "SEE FIG" in _OCR_BOM_PROMPT, "Prompt 缺少 NHA 跨图规则"
        assert "level=1" in _OCR_BOM_PROMPT or "单点" in _OCR_BOM_PROMPT, \
            "Prompt 未说明 NHA 零件的 nomenclature 应填单点前缀"

    def test_prompt_has_intrchg_rule(self):
        from backend.routers.kg_stages import _OCR_BOM_PROMPT
        assert "INTRCHG" in _OCR_BOM_PROMPT, "Prompt 缺少互换件规则"

    def test_prompt_has_fewshot(self):
        from backend.routers.kg_stages import _OCR_BOM_PROMPT
        assert "示例" in _OCR_BOM_PROMPT, "Prompt 缺少 few-shot 示例"
        assert "3034344" in _OCR_BOM_PROMPT, "Prompt 缺少具体 few-shot 数据"


class TestResolveNhaTriples:

    def _make_entities(self):
        return [
            {"id": "3034344", "type": "Assembly", "name": "COMPRESSOR ROTOR INSTALLATION",
             "part_number": "3034344", "material": "", "quantity": 1},
        ]

    def _make_triples(self):
        return [
            # 顶层装配，已正确挂到 ROOT（应保持不变）
            {"head": "3034344 COMPRESSOR ROTOR INSTALLATION", "relation": "isPartOf",
             "tail": "ROOT", "tail_type": "ROOT", "confidence": 1.0, "source": "BOM",
             "head_type": "Assembly"},
            # NHA 零件，应被修正到顶层 Assembly
            {"head": "3102464-03 ROTOR BALANCING ASSEMBLY SEE FIG.1 FOR NHA",
             "relation": "isPartOf", "tail": "ROOT", "tail_type": "ROOT",
             "confidence": 1.0, "source": "BOM", "head_type": "Assembly"},
            # 普通 ROOT 条目，不含 NHA，应保持不变
            {"head": "MS9356-09 NUT,PLAIN,HEX", "relation": "isPartOf",
             "tail": "ROOT", "tail_type": "ROOT", "confidence": 1.0,
             "source": "BOM", "head_type": "Part"},
        ]

    def test_nha_triple_gets_resolved(self):
        from backend.routers.kg_stages import _resolve_nha_triples
        entities = self._make_entities()
        triples = self._make_triples()
        result = _resolve_nha_triples(triples, entities)
        nha_triple = next(t for t in result if "SEE FIG" in t["head"])
        assert nha_triple["tail"] != "ROOT", \
            f"NHA 零件未被修正，仍挂到 ROOT: {nha_triple}"
        assert nha_triple["tail"] == "3034344 COMPRESSOR ROTOR INSTALLATION"
        assert nha_triple["tail_type"] == "Assembly"

    def test_non_nha_root_unchanged(self):
        from backend.routers.kg_stages import _resolve_nha_triples
        entities = self._make_entities()
        triples = self._make_triples()
        result = _resolve_nha_triples(triples, entities)
        nut_triple = next(t for t in result if "NUT" in t["head"])
        assert nut_triple["tail"] == "ROOT", "非NHA的ROOT条目不应被修改"

    def test_no_entities_returns_unchanged(self):
        from backend.routers.kg_stages import _resolve_nha_triples
        triples = self._make_triples()
        result = _resolve_nha_triples(triples, [])
        nha_triple = next(t for t in result if "SEE FIG" in t["head"])
        assert nha_triple["tail"] == "ROOT", "无实体时应保留 ROOT"
