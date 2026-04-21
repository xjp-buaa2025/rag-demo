import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from backend.pipelines.nodes_cad import _clean_composite_name


def test_ampersand_pair_splits_into_two():
    """'100&110' 应拆分为 ['C52696C-100', 'C52696C-110']。"""
    result = _clean_composite_name("100&110", "C52696C")
    assert result == ["C52696C-100", "C52696C-110"]


def test_ampersand_triple_splits_into_three():
    """'100&110&120' 应拆分为三个带前缀的名称。"""
    result = _clean_composite_name("100&110&120", "C52696C")
    assert result == ["C52696C-100", "C52696C-110", "C52696C-120"]


def test_non_numeric_ampersand_not_split():
    """'190&200' 两边均为纯数字，应拆分。"""
    result = _clean_composite_name("190&200", "C52696C")
    assert result == ["C52696C-190", "C52696C-200"]


def test_descriptive_name_with_spaces_not_split():
    """'370-2 holes' 有空格，不是纯数字组合，不应拆分。"""
    result = _clean_composite_name("370-2 holes", "C52696C")
    assert result == ["370-2 holes"]


def test_already_prefixed_name_not_split():
    """'C52696C-10' 已带前缀，不含 '&'，直接原样返回。"""
    result = _clean_composite_name("C52696C-10", "C52696C")
    assert result == ["C52696C-10"]


def test_single_numeric_not_split():
    """'100' 单个纯数字，不含 '&'，直接原样返回（单元素列表）。"""
    result = _clean_composite_name("100", "C52696C")
    assert result == ["100"]


from backend.pipelines.nodes_cad import _topology_align_cad_bom


def test_topology_align_matches_by_depth_and_sibling_index():
    """
    CAD 树和 BOM 树结构相同时，应按 (depth, sibling_index) 位置对齐。
    """
    cad_tree = {
        "C52696C": {
            "C52696C-10": {},
            "C52696C-20": {},
        }
    }
    bom_entities = [
        {"id": "ROOT", "name": "COMPRESSOR ASSY",    "part_number": "3034344", "parent_id": "ROOT"},
        {"id": "P001", "name": "COMPRESSOR ROTOR",   "part_number": "3034100", "parent_id": "ROOT"},
        {"id": "P002", "name": "COMPRESSOR STATOR",  "part_number": "3034200", "parent_id": "ROOT"},
    ]
    result = _topology_align_cad_bom(cad_tree, bom_entities)
    assert "C52696C-10" in result
    assert result["C52696C-10"]["method"] == "topology"
    assert result["C52696C-10"]["bom_id"] == "P001"
    assert "C52696C-20" in result
    assert result["C52696C-20"]["bom_id"] == "P002"


def test_topology_align_returns_empty_when_no_bom():
    """BOM 实体为空时返回空字典。"""
    cad_tree = {"C89119": {"C89119-10": {}}}
    result = _topology_align_cad_bom(cad_tree, [])
    assert result == {}


def test_topology_align_unmatched_cad_node_not_in_result():
    """CAD 树节点多于 BOM 节点时，多余的 CAD 节点不出现在结果中。"""
    cad_tree = {
        "C52696C": {
            "C52696C-10": {},
            "C52696C-20": {},
            "C52696C-30": {},
        }
    }
    bom_entities = [
        {"id": "ROOT", "name": "ASSY",   "part_number": "0001", "parent_id": "ROOT"},
        {"id": "P001", "name": "PART A", "part_number": "0002", "parent_id": "ROOT"},
        {"id": "P002", "name": "PART B", "part_number": "0003", "parent_id": "ROOT"},
    ]
    result = _topology_align_cad_bom(cad_tree, bom_entities)
    assert "C52696C-30" not in result
