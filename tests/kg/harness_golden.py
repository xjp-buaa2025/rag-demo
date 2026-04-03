"""
tests/kg/harness_golden.py — 层三：Golden Set P/R/F1 评估

前提：已准备 tests/kg/fixtures/golden_triples.json（人工标注，至少 20 条）。
依赖：conftest.py 中的 neo4j_session / golden_triples fixture。

评估逻辑：
  1. 从 Neo4j 查询所有关系三元组（head_text, rel_type, tail_text）
  2. 对 head_text 和 tail_text 执行归一化（与 golden_triples.json 生成时一致）
  3. 计算 Precision / Recall / F1

归一化规则（必须与标注 golden_triples.json 时保持一致）：
  - 全角 → 半角（NFKC）
  - Stage-N / Stage_N 变体 → 第N级
  - AVIATION_ABBREV 缩写展开
  - 小写 + 去首尾空格

初期门槛说明：
  F1 ≥ 0.50 是最低门槛。由于 KG 三元组数量（~数百条）远多于 golden set（~30条），
  Precision 通常偏低而 Recall 偏高，F1 主要受 Recall 驱动。
  扩大 golden set 到 200+ 条后可同时提升 Precision 评估的可靠性。

运行方式：
  pytest tests/kg/harness_golden.py -v -s
"""

import re
import unicodedata

import pytest

F1_THRESHOLD = 0.50

# ── 归一化工具 ────────────────────────────────────────────────────────────────
# 复用 nodes_kg.py 中的 AVIATION_ABBREV，不直接 import backend 避免服务依赖
_ABBREV: dict[str, str] = {
    "HPC": "高压压气机",  "LPC": "低压压气机",
    "HPT": "高压涡轮",    "LPT": "低压涡轮",
    "CC":  "燃烧室",      "FC":  "火焰筒",
    "FAN": "风扇",        "AGB": "附件齿轮箱",
    "Blade":   "叶片",    "Disk":    "叶盘",
    "Vane":    "导向叶片","Casing":  "机匣",
    "Rotor":   "转子",    "Stator":  "静子",
    "Seal":    "封严环",  "Bearing": "轴承",
    "Shaft":   "轴",      "Nozzle":  "喷嘴",
    "N.m":     "N·m",     "Nm":      "N·m",
}

_STAGE_RE = re.compile(r"[Ss]tage[-_\s]?(\d+)")


def normalize_text(text: str) -> str:
    """
    归一化文本，用于三元组精确匹配比对。
    此函数的规则必须与 golden_triples.json 的标注约定完全一致。
    """
    if not text:
        return ""
    # 全角 → 半角
    text = unicodedata.normalize("NFKC", text)
    # Stage 变体统一：Stage-3 / Stage_3 / stage3 → 第3级
    text = _STAGE_RE.sub(lambda m: f"第{m.group(1)}级", text)
    # 缩写展开（按长度降序，避免子串误替换）
    for abbr in sorted(_ABBREV, key=len, reverse=True):
        text = text.replace(abbr, _ABBREV[abbr])
    # 小写 + 去首尾空格
    return text.strip().lower()


def normalize_triple(triple: dict) -> tuple:
    """将三元组 dict 归一化为 (head, relation, tail) 元组。"""
    return (
        normalize_text(triple.get("head", "")),
        triple.get("relation", "").strip().lower(),
        normalize_text(triple.get("tail", "")),
    )


# ── 从 Neo4j 提取三元组 ────────────────────────────────────────────────────────

_TARGET_REL_TYPES = [
    "precedes", "participatesIn", "requires",
    "specifiedBy", "matesWith", "isPartOf",
]


def fetch_kg_triples(neo4j_session) -> set:
    """
    从 Neo4j 查询所有关系三元组，返回归一化后的集合。
    使用 kg_name 优先（KG 来源节点），part_name 次之（BOM 来源节点）。
    LIMIT 5000 防止超大图超时。
    """
    query = """
    MATCH (a)-[r]->(b)
    WHERE type(r) IN $rel_types
      AND (a.kg_name IS NOT NULL OR a.part_name IS NOT NULL)
      AND (b.kg_name IS NOT NULL OR b.part_name IS NOT NULL)
    RETURN
        coalesce(a.kg_name, a.part_name) AS head,
        type(r)                           AS relation,
        coalesce(b.kg_name, b.part_name) AS tail
    LIMIT 5000
    """
    rows = neo4j_session.run(query, rel_types=_TARGET_REL_TYPES).data()
    result = set()
    for row in rows:
        h = normalize_text(row.get("head", ""))
        r = row.get("relation", "").strip().lower()
        t = normalize_text(row.get("tail", ""))
        if h and r and t:
            result.add((h, r, t))
    return result


# ── P/R/F1 计算 ────────────────────────────────────────────────────────────────

def compute_prf1(predicted: set, gold: set) -> dict:
    """
    计算精确率、召回率、F1。
    返回：{"precision", "recall", "f1", "tp", "fp", "fn"}
    """
    tp = len(predicted & gold)
    fp = len(predicted - gold)
    fn = len(gold - predicted)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall    = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall) > 0 else 0.0
    )
    return {
        "precision": round(precision, 4),
        "recall":    round(recall,    4),
        "f1":        round(f1,        4),
        "tp": tp, "fp": fp, "fn": fn,
    }


# ── 测试类 ────────────────────────────────────────────────────────────────────

class TestGoldenSetF1:

    def test_f1_above_threshold(self, neo4j_session, golden_triples, capsys):
        """
        整体 F1 不低于 F1_THRESHOLD（初期 0.50）。
        同时打印详细评估报告和漏召回示例，辅助定位问题。
        """
        gold_set = {normalize_triple(t) for t in golden_triples}
        pred_set = fetch_kg_triples(neo4j_session)

        if not gold_set:
            pytest.skip("Golden set 为空，请检查 golden_triples.json 格式")
        if not pred_set:
            pytest.fail(
                "KG 中无可查询的三元组（层三依赖层一通过）。\n"
                "请先确认层一 harness_structural.py 全部通过。"
            )

        metrics = compute_prf1(pred_set, gold_set)

        fn_examples = sorted(gold_set - pred_set)[:10]
        fp_examples = sorted(pred_set - gold_set)[:5]

        with capsys.disabled():
            print(f"\n{'='*55}")
            print(f"Golden Set 评估报告")
            print(f"{'='*55}")
            print(f"  Gold  三元组数: {len(gold_set)}")
            print(f"  Pred  三元组数: {len(pred_set)}")
            print(f"  TP={metrics['tp']}  FP={metrics['fp']}  FN={metrics['fn']}")
            print(f"  Precision: {metrics['precision']:.4f}")
            print(f"  Recall:    {metrics['recall']:.4f}")
            print(f"  F1:        {metrics['f1']:.4f}  (门槛: {F1_THRESHOLD})")
            print(f"{'='*55}")
            if fn_examples:
                print(f"\n  漏召回示例（FN，前10）：")
                for h, r, t in fn_examples:
                    print(f"    ({h}) -[{r}]-> ({t})")
            if fp_examples:
                print(f"\n  误召回示例（FP，前5）：")
                for h, r, t in fp_examples:
                    print(f"    ({h}) -[{r}]-> ({t})")
            print(f"{'='*55}")

        assert metrics["f1"] >= F1_THRESHOLD, (
            f"F1={metrics['f1']:.4f} 低于阈值 {F1_THRESHOLD}。\n"
            f"Precision={metrics['precision']:.4f}  Recall={metrics['recall']:.4f}\n"
            f"根因分析：\n"
            f"  低 Recall（漏召回多）：\n"
            f"    ① LLM 提取遗漏 → 增加 Gleaning 轮次或优化 few-shot 示例\n"
            f"    ② 关键文本块被 _PROCEDURE_KEYWORDS 过滤器误拦截\n"
            f"    ③ 实体名称归一化不一致（检查 normalize_text 与手册标注是否一致）\n"
            f"  低 Precision（误召回多）：\n"
            f"    ① 实体对齐错位（fuzzy/semantic 阶段误匹配）\n"
            f"    ② Golden set 过小（仅 {len(gold_set)} 条），建议扩充到 100+ 条"
        )

    def test_per_relation_f1(self, neo4j_session, golden_triples, capsys):
        """
        分关系类型计算 F1，识别最弱类型（信息性，不 FAIL）。
        帮助优先改进最薄弱的关系提取逻辑。
        """
        gold_set = {normalize_triple(t) for t in golden_triples}
        pred_set = fetch_kg_triples(neo4j_session)

        if not gold_set:
            pytest.skip("Golden set 为空")

        rel_types = sorted({t[1] for t in gold_set})
        with capsys.disabled():
            print(f"\n{'='*70}")
            print(f"分关系类型 F1：")
            print(f"{'='*70}")
            weakest = None
            weakest_f1 = 1.0
            for rel in rel_types:
                g = {t for t in gold_set if t[1] == rel}
                p = {t for t in pred_set if t[1] == rel}
                m = compute_prf1(p, g)
                flag = ""
                if m["f1"] < weakest_f1:
                    weakest_f1 = m["f1"]
                    weakest    = rel
                if m["f1"] < 0.3:
                    flag = " ← 需优先改进"
                print(
                    f"  {rel:22s}: P={m['precision']:.3f}  R={m['recall']:.3f}  "
                    f"F1={m['f1']:.3f}  (gold={len(g)}, pred={len(p)}){flag}"
                )
            if weakest:
                print(f"\n  最弱关系类型：[{weakest}]（F1={weakest_f1:.3f}）")
            print(f"{'='*70}")

    def test_high_confidence_recall(self, neo4j_session, golden_triples, capsys):
        """
        confidence=1.0 的黄金三元组（人工 100% 确认）召回率应 ≥ 0.60。
        这是比整体 F1 更严格的质量信号。
        """
        high_conf = [t for t in golden_triples if t.get("confidence", 1.0) >= 1.0]
        if len(high_conf) < 5:
            pytest.skip(f"高置信度三元组不足 5 条（当前 {len(high_conf)} 条），跳过")

        gold_high = {normalize_triple(t) for t in high_conf}
        pred_set  = fetch_kg_triples(neo4j_session)

        recalled = len(gold_high & pred_set)
        recall   = recalled / len(gold_high)

        with capsys.disabled():
            print(f"\n  高置信度三元组（confidence=1.0）召回率: {recall:.1%}（{recalled}/{len(gold_high)}）")

        assert recall >= 0.60, (
            f"高置信度三元组召回率 {recall:.1%}（{recalled}/{len(gold_high)}）低于 60%。\n"
            f"这些是您人工确认 100% 正确的三元组，LLM 应能准确提取。\n"
            f"建议检查对应文本段落是否被正确分块并送入 extract_kg_triples。"
        )
