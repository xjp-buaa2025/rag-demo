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
