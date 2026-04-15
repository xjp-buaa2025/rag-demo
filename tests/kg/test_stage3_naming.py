"""
测试 _parse_step_tree_from_text 的数字名前缀补全逻辑。
使用内联 STEP 文本，无需真实文件。
"""
import tempfile, os, pytest
from backend.pipelines.nodes_cad import _parse_step_tree_from_text

# 最小化 STEP 文本：根装配 C52696C，两个子零件 '10' 和 '180-blade'
_STEP_NUMERIC = """
ISO-10303-21;
HEADER; ENDSEC;
DATA;
#1 = PRODUCT ( 'C52696C', 'C52696C', '', ( #99 ) ) ;
#2 = PRODUCT ( '10', '10', '', ( #99 ) ) ;
#3 = PRODUCT ( '180-blade', '180-blade', '', ( #99 ) ) ;
#10 = PRODUCT_DEFINITION_FORMATION ( ' ', ' ', #1 ) ;
#11 = PRODUCT_DEFINITION_FORMATION ( ' ', ' ', #2 ) ;
#12 = PRODUCT_DEFINITION_FORMATION ( ' ', ' ', #3 ) ;
#20 = PRODUCT_DEFINITION ( 'design', ' ', #10 ) ;
#21 = PRODUCT_DEFINITION ( 'design', ' ', #11 ) ;
#22 = PRODUCT_DEFINITION ( 'design', ' ', #12 ) ;
#30 = NEXT_ASSEMBLY_USAGE_OCCURRENCE ( 'u1', ' ', ' ', #20, #21, $ ) ;
#31 = NEXT_ASSEMBLY_USAGE_OCCURRENCE ( 'u2', ' ', ' ', #20, #22, $ ) ;
ENDSEC;
END-ISO-10303-21;
"""

# 有意义名称的 STEP（C89119 风格），子零件名已经有前缀，不应被修改
_STEP_MEANINGFUL = """
ISO-10303-21;
HEADER; ENDSEC;
DATA;
#1 = PRODUCT ( 'C89119', 'C89119', '', ( #99 ) ) ;
#2 = PRODUCT ( 'C89119-270', 'C89119-270', '', ( #99 ) ) ;
#10 = PRODUCT_DEFINITION_FORMATION ( ' ', ' ', #1 ) ;
#11 = PRODUCT_DEFINITION_FORMATION ( ' ', ' ', #2 ) ;
#20 = PRODUCT_DEFINITION ( 'design', ' ', #10 ) ;
#21 = PRODUCT_DEFINITION ( 'design', ' ', #11 ) ;
#30 = NEXT_ASSEMBLY_USAGE_OCCURRENCE ( 'u1', ' ', ' ', #20, #21, $ ) ;
ENDSEC;
END-ISO-10303-21;
"""


def _write_tmp(content: str) -> str:
    f = tempfile.NamedTemporaryFile(mode='w', suffix='.step', delete=False, encoding='utf-8')
    f.write(content)
    f.close()
    return f.name


def test_numeric_children_get_prefix():
    """纯数字子零件名应被补全为 {root}-{num} 格式"""
    path = _write_tmp(_STEP_NUMERIC)
    try:
        tree = _parse_step_tree_from_text(path)
        assert 'C52696C' in tree, f"根节点未找到 C52696C，tree={tree}"
        children = set(tree['C52696C'].keys())
        assert 'C52696C-10' in children, f"期望 C52696C-10，实际 children={children}"
        assert 'C52696C-180-blade' in children, f"期望 C52696C-180-blade，实际 children={children}"
        assert '10' not in children
        assert '180-blade' not in children
    finally:
        os.unlink(path)


def test_meaningful_names_unchanged():
    """已有意义的子零件名（C89119-270）不应被修改"""
    path = _write_tmp(_STEP_MEANINGFUL)
    try:
        tree = _parse_step_tree_from_text(path)
        assert 'C89119' in tree
        children = set(tree['C89119'].keys())
        assert 'C89119-270' in children, f"期望 C89119-270，实际={children}"
        assert 'C89119-C89119-270' not in children
    finally:
        os.unlink(path)
