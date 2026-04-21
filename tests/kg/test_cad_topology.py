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
