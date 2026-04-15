"""
tests/kg/test_bom_stage1_acceptance.py

静态验收测试：读取已有的 stage1_bom_triples.json，验证指标。
不触发 LLM，纯离线验证。

注意：此测试验证的是最新一次 Stage1 运行的产物。
每次重新跑 Stage1 后再运行此测试。
"""
import json
from pathlib import Path
import pytest

STAGE1_PATH = Path(__file__).parents[2] / "storage/kg_stages/stage1_bom_triples.json"


@pytest.fixture(scope="module")
def stage1_data():
    if not STAGE1_PATH.exists():
        pytest.skip(f"stage1 产物不存在: {STAGE1_PATH}")
    with open(STAGE1_PATH, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def triples(stage1_data):
    return stage1_data.get("triples", [])


@pytest.fixture(scope="module")
def ispartof_triples(triples):
    return [t for t in triples if t.get("relation") == "isPartOf"]


class TestStage1Acceptance:

    def test_root_ratio_below_threshold(self, ispartof_triples):
        """tail==ROOT 占比应 < 40%。"""
        total = len(ispartof_triples)
        assert total > 0, "无 isPartOf 三元组，Stage1 未运行或产物为空"
        root_count = sum(1 for t in ispartof_triples if t.get("tail") == "ROOT")
        ratio = root_count / total
        assert ratio < 0.40, (
            f"ROOT 占比 {ratio:.1%}（{root_count}/{total}）仍超过 40% 门槛。\n"
            f"可能原因：LLM 仍漏填 nomenclature 点号，或 _resolve_nha_triples 未生效。"
        )

    def test_has_deep_hierarchy(self, ispartof_triples):
        """应存在至少一条非 ROOT 且 tail 也不是直接顶层的三元组（间接验证深度 ≥ 2）。"""
        non_root = [t for t in ispartof_triples if t.get("tail") != "ROOT"]
        assert len(non_root) > 0, "所有 isPartOf 均挂到 ROOT，层级完全扁平"
        tail_values = {t["tail"] for t in ispartof_triples if t.get("tail") != "ROOT"}
        assert len(tail_values) >= 2, (
            f"只有 {len(tail_values)} 种非ROOT父节点，层级可能仍然过于扁平"
        )

    def test_has_interchanges_relation(self, triples):
        """应存在至少 2 条 interchangesWith 关系。"""
        interchanges = [t for t in triples if t.get("relation") == "interchangesWith"]
        assert len(interchanges) >= 2, (
            f"interchangesWith 关系仅 {len(interchanges)} 条，互换件识别可能失效"
        )

    def test_no_ocr_noise_in_entities(self, stage1_data):
        """实体名称中不应含 OCR 噪声（COMP0NENT 等）。"""
        entities = stage1_data.get("entities", [])
        noisy = [
            e["name"] for e in entities
            if "COMP0NENT" in e.get("name", "") or "C0MPONENT" in e.get("name", "")
        ]
        assert len(noisy) == 0, f"发现 {len(noisy)} 条含OCR噪声的实体名: {noisy[:5]}"
