"""
Stage3 批量解析集成测试。
直接调用 _parse_step_tree_from_text 和 _cad_data_to_flat_triples，
无需启动服务器，验证两个真实 STEP 文件的三元组数量。
"""
import pytest, os, re

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'kg')
C52696C_PATH = os.path.join(DATA_DIR, 'C52696C.STEP')
C89119_PATH  = os.path.join(DATA_DIR, 'C89119.STEP')


@pytest.mark.skipif(
    not os.path.exists(C52696C_PATH),
    reason="C52696C.STEP 不存在，跳过集成测试"
)
def test_c52696c_triple_count():
    """C52696C.STEP 应提取到 ≥ 100 条三元组。
    注：STEP 中 300 NAUO 经去重后为 56 个唯一装配关系（叶片等多实例零件），
    加上 matesWith 共 112 条；阈值 100 留余量以容纳解析变化。
    """
    from backend.pipelines.nodes_cad import _parse_step_tree_from_text, _parse_step_constraints
    from backend.routers.kg_stages import _cad_data_to_flat_triples

    tree = _parse_step_tree_from_text(C52696C_PATH)
    constraints = _parse_step_constraints(C52696C_PATH)
    triples = _cad_data_to_flat_triples(tree, constraints, [])

    assert len(triples) >= 100, f"期望 ≥ 100 条，实际 {len(triples)} 条"


@pytest.mark.skipif(
    not os.path.exists(C52696C_PATH),
    reason="C52696C.STEP 不存在，跳过集成测试"
)
def test_c52696c_no_bare_numeric_names():
    """C52696C 解析结果中不应出现裸数字零件名（如 '10'、'120'）"""
    from backend.pipelines.nodes_cad import _parse_step_tree_from_text, _parse_step_constraints
    from backend.routers.kg_stages import _cad_data_to_flat_triples

    tree = _parse_step_tree_from_text(C52696C_PATH)
    constraints = _parse_step_constraints(C52696C_PATH)
    triples = _cad_data_to_flat_triples(tree, constraints, [])

    _BARE_NUMERIC = re.compile(r'^\d[\d\-a-zA-Z]*$')
    bare = [t for t in triples if _BARE_NUMERIC.match(t['head']) or _BARE_NUMERIC.match(t['tail'])]
    assert len(bare) == 0, f"发现 {len(bare)} 条含裸数字名的三元组，例：{bare[:3]}"


@pytest.mark.skipif(
    not os.path.exists(C89119_PATH),
    reason="C89119.STEP 不存在，跳过集成测试"
)
def test_c89119_names_unchanged():
    """C89119.STEP 的零件名应保持 C89119-xxx 格式，不受前缀补全影响"""
    from backend.pipelines.nodes_cad import _parse_step_tree_from_text, _parse_step_constraints
    from backend.routers.kg_stages import _cad_data_to_flat_triples

    tree = _parse_step_tree_from_text(C89119_PATH)
    constraints = _parse_step_constraints(C89119_PATH)
    triples = _cad_data_to_flat_triples(tree, constraints, [])

    assert len(triples) >= 20, f"C89119 应有 ≥ 20 条三元组，实际 {len(triples)}"
    double_prefix = [t for t in triples if 'C89119-C89119' in t['head'] or 'C89119-C89119' in t['tail']]
    assert len(double_prefix) == 0, f"发现双前缀三元组：{double_prefix[:3]}"
