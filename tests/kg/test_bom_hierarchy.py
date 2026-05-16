"""tests/kg/test_bom_hierarchy.py — BOM 层级修复单元测试"""
import json
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


# ─────────────────────────────────────────────────────────────────────────────
# 新增：_apply_ipc_hierarchy 单元测试
# ─────────────────────────────────────────────────────────────────────────────

def _make_record(fig_item, part_id, part_name, nomenclature, category="Part"):
    return {
        "fig_item": fig_item, "part_id": part_id, "part_name": part_name,
        "nomenclature": nomenclature, "category": category,
        "qty": 1, "unit": "件", "material": "", "parent_id": "",
    }


class TestApplyIpcHierarchy:

    def test_plain_integer_items_get_root_assembly_as_parent(self):
        """fig_item为普通整数(10,20)且无点号 → parent_id应为顶层Assembly"""
        from backend.routers.kg_stages import _apply_ipc_hierarchy
        records = [
            _make_record("-1", "3034344", "COMPRESSOR ROTOR INSTALLATION",
                         "COMPRESSOR ROTOR INSTALLATION", "Assembly"),
            _make_record("10", "MS9556-06", "BOLT,MACHINE,DBL HEX",
                         "BOLT,MACHINE,DBL HEX", "Standard"),
            _make_record("20", "MS9556-07", "BOLT,MACHINE,DBL HEX",
                         "BOLT,MACHINE,DBL HEX", "Standard"),
        ]
        result = _apply_ipc_hierarchy(records)
        bolt1 = next(r for r in result if r["part_id"] == "MS9556-06")
        bolt2 = next(r for r in result if r["part_id"] == "MS9556-07")
        assert bolt1["parent_id"] == "3034344", f"BOLT1 parent应为3034344，实际={bolt1['parent_id']}"
        assert bolt2["parent_id"] == "3034344", f"BOLT2 parent应为3034344，实际={bolt2['parent_id']}"

    def test_top_assembly_parent_id_unchanged(self):
        """顶层Assembly的parent_id应保持为空（挂ROOT）"""
        from backend.routers.kg_stages import _apply_ipc_hierarchy
        records = [
            _make_record("-1", "3034344", "COMPRESSOR ROTOR INSTALLATION",
                         "COMPRESSOR ROTOR INSTALLATION", "Assembly"),
        ]
        result = _apply_ipc_hierarchy(records)
        assert result[0]["parent_id"] == "", "顶层Assembly不应有parent_id"

    def test_dash_prefix_item_shares_parent_with_base(self):
        """fig_item=-40A → 与基础序号40共享相同parent（即顶层Assembly）"""
        from backend.routers.kg_stages import _apply_ipc_hierarchy
        records = [
            _make_record("-1", "3034344", "COMPRESSOR ROTOR INSTALLATION",
                         "COMPRESSOR ROTOR INSTALLATION", "Assembly"),
            _make_record("40",  "3030349",    "SEAL ASSEMBLY,AIR", "SEAL ASSEMBLY,AIR", "Assembly"),
            _make_record("-40A","3103074-01", "SEAL ASSEMBLY,AIR PRE-SB15108",
                         "SEAL ASSEMBLY,AIR PRE-SB15108", "Assembly"),
        ]
        result = _apply_ipc_hierarchy(records)
        base_seal  = next(r for r in result if r["part_id"] == "3030349")
        alt_seal   = next(r for r in result if r["part_id"] == "3103074-01")
        assert base_seal["parent_id"] == "3034344", f"base seal parent={base_seal['parent_id']}"
        assert alt_seal["parent_id"] == base_seal["parent_id"], \
            f"-40A应与40共享父节点，40={base_seal['parent_id']}，-40A={alt_seal['parent_id']}"

    def test_attaching_parts_block_skipped_and_items_get_correct_parent(self):
        """ATTACHING PARTS行本身不出现在结果中，其后的零件挂到正确父节点"""
        from backend.routers.kg_stages import _apply_ipc_hierarchy
        records = [
            _make_record("-1", "3034344", "COMPRESSOR ROTOR INSTALLATION",
                         "COMPRESSOR ROTOR INSTALLATION", "Assembly"),
            _make_record("40",  "3030349", "SEAL ASSEMBLY,AIR", "SEAL ASSEMBLY,AIR", "Assembly"),
            _make_record("ATTACHING PARTS", "", "ATTACHING PARTS",
                         "ATTACHING PARTS", "AttachingParts"),
            _make_record("50", "MS9676-11", "NUT,DBL HEX", "NUT,DBL HEX", "Standard"),
        ]
        result = _apply_ipc_hierarchy(records)
        # ATTACHING PARTS 行被跳过
        part_ids = [r["part_id"] for r in result]
        assert "" not in part_ids or all(
            r["part_name"] != "ATTACHING PARTS" for r in result
        ), "ATTACHING PARTS行不应出现在结果中"
        # 附件块内的NUT应挂到其前最近的Assembly（3030349 SEAL ASSEMBLY）
        nut = next((r for r in result if r["part_id"] == "MS9676-11"), None)
        assert nut is not None, "NUT记录应在结果中"
        assert nut["parent_id"] == "3030349", \
            f"NUT应挂在SEAL ASSEMBLY下，实际parent={nut['parent_id']}"

    def test_dot_prefix_items_not_overridden(self):
        """nomenclature含点号前缀的条目不被改动（由栈逻辑处理）"""
        from backend.routers.kg_stages import _apply_ipc_hierarchy
        records = [
            _make_record("-1",  "3034344", "COMPRESSOR ROTOR INSTALLATION",
                         "COMPRESSOR ROTOR INSTALLATION", "Assembly"),
            _make_record("40",  "3030349", "SEAL ASSEMBLY,AIR",
                         ".SEAL ASSEMBLY,AIR", "Assembly"),
        ]
        result = _apply_ipc_hierarchy(records)
        seal = next(r for r in result if r["part_id"] == "3030349")
        # 点号条目parent_id应保持""（由栈逻辑处理，_apply_ipc_hierarchy不改动）
        assert seal["parent_id"] == "", \
            f"点号条目不应被_apply_ipc_hierarchy填充parent_id，实际={seal['parent_id']}"


# ─────────────────────────────────────────────────────────────────────────────
# 新增：_bom_df_to_entities_and_triples level=0 修复测试
# ─────────────────────────────────────────────────────────────────────────────

class TestLevel0Fix:

    def test_level0_non_first_assembly_hangs_under_root_assembly(self):
        """level=0的非首条记录（通过parent_id填好）应挂在顶层Assembly下，不挂ROOT"""
        from backend.routers.kg_stages import _bom_df_to_entities_and_triples
        records = [
            {"part_id": "3034344", "part_name": "COMPRESSOR ROTOR INSTALLATION",
             "nomenclature": "COMPRESSOR ROTOR INSTALLATION", "fig_item": "-1",
             "parent_id": "", "qty": 1, "category": "Assembly",
             "material": "", "unit": "件"},
            # MS9556-06 parent_id 已由 _apply_ipc_hierarchy 填好
            {"part_id": "MS9556-06", "part_name": "BOLT,MACHINE,DBL HEX",
             "nomenclature": "BOLT,MACHINE,DBL HEX", "fig_item": "10",
             "parent_id": "3034344", "qty": 1, "category": "Standard",
             "material": "", "unit": "件"},
        ]
        df_json = json.dumps(records)
        entities, triples = _bom_df_to_entities_and_triples(df_json)
        bolt_triple = next((t for t in triples if "BOLT" in t["head"]), None)
        assert bolt_triple is not None, "BOLT三元组不存在"
        assert bolt_triple["tail"] != "ROOT", \
            f"BOLT不应挂ROOT，实际tail={bolt_triple['tail']}"
        assert "3034344" in bolt_triple["tail"], \
            f"BOLT应挂在3034344下，实际tail={bolt_triple['tail']}"

    def test_level0_first_assembly_still_at_root(self):
        """顶层Assembly本身（第一个level=0条目）仍应挂ROOT"""
        from backend.routers.kg_stages import _bom_df_to_entities_and_triples
        records = [
            {"part_id": "3034344", "part_name": "COMPRESSOR ROTOR INSTALLATION",
             "nomenclature": "COMPRESSOR ROTOR INSTALLATION", "fig_item": "-1",
             "parent_id": "", "qty": 1, "category": "Assembly",
             "material": "", "unit": "件"},
        ]
        df_json = json.dumps(records)
        entities, triples = _bom_df_to_entities_and_triples(df_json)
        top_triple = next((t for t in triples
                           if "COMPRESSOR ROTOR INSTALLATION" in t["head"]), None)
        assert top_triple is not None
        assert top_triple["tail"] == "ROOT", \
            f"顶层Assembly应挂ROOT，实际={top_triple['tail']}"

    def test_dot_child_still_hangs_under_assembly_not_root(self):
        """nomenclature有点号的子件在level=0保护后仍正确挂父节点"""
        from backend.routers.kg_stages import _bom_df_to_entities_and_triples
        records = [
            {"part_id": "3034344", "part_name": "COMPRESSOR ROTOR INSTALLATION",
             "nomenclature": "COMPRESSOR ROTOR INSTALLATION", "fig_item": "-1",
             "parent_id": "", "qty": 1, "category": "Assembly",
             "material": "", "unit": "件"},
            {"part_id": "3030349", "part_name": "SEAL ASSEMBLY,AIR",
             "nomenclature": ".SEAL ASSEMBLY,AIR", "fig_item": "40",
             "parent_id": "", "qty": 1, "category": "Assembly",
             "material": "", "unit": "件"},
        ]
        df_json = json.dumps(records)
        entities, triples = _bom_df_to_entities_and_triples(df_json)
        seal_triple = next((t for t in triples if "SEAL" in t["head"]), None)
        assert seal_triple is not None
        assert seal_triple["tail"] != "ROOT", \
            f"SEAL子件不应挂ROOT，tail={seal_triple['tail']}"
        assert "3034344" in seal_triple["tail"]


# ─────────────────────────────────────────────────────────────────────────────
# 新增：_align_manual_to_bom 增强匹配单元测试
# ─────────────────────────────────────────────────────────────────────────────

def _make_bom_entities():
    return [
        {"id": "MS9556-07", "name": "BOLT, MACHINE, DBL HEX",    "part_number": "MS9556-07"},
        {"id": "MS9767-09", "name": "NUT, SELF-LOCKING ANCHOR",  "part_number": "MS9767-09"},
        {"id": "3034521",   "name": "CENTER FIRESEAL MOUNT RING","part_number": "3034521"},
        {"id": "AS3209-267","name": "PACKING, PREFORMED",        "part_number": "AS3209-267"},
    ]


class TestAlignManualToBom:

    def _run(self, head, head_type, bom_entities=None):
        from backend.routers.kg_stages import _align_manual_to_bom
        triples = [{"head": head, "head_type": head_type,
                    "tail": "some procedure", "tail_type": "Procedure",
                    "relation": "participatesIn", "confidence": 0.8}]
        _align_manual_to_bom(triples, bom_entities or _make_bom_entities())
        return triples[0]

    def test_exact_name_match(self):
        t = self._run("BOLT, MACHINE, DBL HEX", "Part")
        assert t.get("head_bom_id") == "MS9556-07", \
            f"精确匹配应命中MS9556-07，实际={t.get('head_bom_id')}"

    def test_figure_ref_stripped_before_matching(self):
        """含图号噪声的实体去除括号后应能匹配 BOM"""
        t = self._run("Bolt (Figure 201 items 1 and 7)", "Part")
        assert t.get("head_bom_id") == "MS9556-07", \
            f"去除图号后应匹配MS9556-07，实际={t.get('head_bom_id')}"

    def test_part_number_extracted_from_entity_text(self):
        """实体名称内嵌零件号时应直接命中 BOM part_number"""
        t = self._run("Nut MS9767-09", "Part")
        assert t.get("head_bom_id") == "MS9767-09", \
            f"应从文本提取零件号MS9767-09，实际={t.get('head_bom_id')}"

    def test_token_overlap_matches_reordered_name(self):
        """词组重排/逗号格式不同时，Token 交集匹配应命中"""
        t = self._run("Nut, Self-locking", "Part")
        assert t.get("head_bom_id") == "MS9767-09", \
            f"Token匹配应命中MS9767-09，实际={t.get('head_bom_id')}"

    def test_token_overlap_partial_name_matches(self):
        """部分名称匹配（'Fireseal Mount Ring' ⊂ 'CENTER FIRESEAL MOUNT RING'）"""
        t = self._run("Fireseal Mount Ring, Top Half", "Part")
        assert t.get("head_bom_id") == "3034521", \
            f"应命中3034521，实际={t.get('head_bom_id')}"

    def test_non_part_type_not_aligned(self):
        """Procedure 类型实体不应被 BOM 对齐"""
        t = self._run("Install compressor rotor", "Procedure")
        assert t.get("head_bom_id") is None, \
            "Procedure类型不应被BOM对齐"

    def test_no_false_positive_on_short_generic_name(self):
        """单字泛称 'Bolt' 不应误匹配（单 token 不参与 token 匹配）"""
        t = self._run("Bolt", "Part")
        # 'Bolt' 太短，不应通过 token 匹配命中具体零件号
        # 注意：子串匹配可能命中，但不应命中错误条目
        if t.get("head_bom_id"):
            assert t["head_bom_id"] == "MS9556-07", \
                f"若命中应为MS9556-07，不应误匹配={t.get('head_bom_id')}"
