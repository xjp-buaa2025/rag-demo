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
