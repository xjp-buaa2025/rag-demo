import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from backend.pipelines.nodes_kg import _build_prompt_with_bom


def test_bom_table_includes_name_column():
    """速查表应同时包含零件号和名称两列。"""
    bom_entities = [
        {"part_number": "3034521", "name": "CENTER FIRESEAL MOUNT RING"},
        {"part_number": "3034344", "name": "COMPRESSOR ROTOR INSTALLATION"},
    ]
    result = _build_prompt_with_bom("BASE_PROMPT", bom_entities)
    assert "CENTER FIRESEAL MOUNT RING" in result
    assert "3034521" in result
    assert "COMPRESSOR ROTOR INSTALLATION" in result
    assert "3034344" in result


def test_bom_table_includes_bom_id_annotation_instruction():
    """速查表说明中应包含 [BOM:{零件号}] 注释指令。"""
    bom_entities = [{"part_number": "3034521", "name": "MOUNT RING"}]
    result = _build_prompt_with_bom("BASE_PROMPT", bom_entities)
    assert "[BOM:" in result


def test_empty_bom_entities_returns_base_prompt():
    """空列表时返回原始 prompt 不变。"""
    result = _build_prompt_with_bom("MY_PROMPT", [])
    assert result == "MY_PROMPT"


def test_entities_without_part_number_still_show_name():
    """只有名称没有零件号的实体也应出现在速查表中。"""
    bom_entities = [{"part_number": "", "name": "THRUST BEARING"}]
    result = _build_prompt_with_bom("BASE_PROMPT", bom_entities)
    assert "THRUST BEARING" in result
