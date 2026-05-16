"""
论文 §4 / §5 实验图表生成器（task #12 收尾）

输入：docs/experiments/raw/{baseline}/qa_*.json
输出：
  paper/figures/fig8_main_compare.pdf      Fig 4-1 主实验柱状对比
  paper/figures/fig9_ablation_delta.pdf    Fig 4-2 消融 Δ 跌幅
  paper/figures/fig10_subtype_heatmap.pdf  Fig 4-3 subtype × baseline 热力图
  paper/figures/fig11_kg_relations.pdf     Fig 3-X KG 关系类型饼图
  docs/experiments/table_subtype.csv       subtype × baseline 详细数据
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import rcParams

# 中文字体
rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "DejaVu Sans"]
rcParams["axes.unicode_minus"] = False
rcParams["font.size"] = 11
rcParams["pdf.fonttype"] = 42  # TrueType

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW = _PROJECT_ROOT / "docs" / "experiments" / "raw"
FIG = _PROJECT_ROOT / "paper" / "figures"
TBL = _PROJECT_ROOT / "docs" / "experiments"
FIG.mkdir(parents=True, exist_ok=True)
TBL.mkdir(parents=True, exist_ok=True)

BASELINES = {
    "B1_dense": "Dense-only",
    "B2_bm25": "BM25-only",
    "B3_hybrid": "Hybrid (RRF)",
    "B4_clip": "+CLIP",
    "B5_kg": "+KG",
    "B6_full": "MHRAG (full)",
    "A1_no_rerank": "B6 −Rerank",
}

CATEGORY_LABELS = {
    "A_structure": "A 零件结构",
    "B_procedure": "B 工序工具",
    "C_specification": "C 技术规范",
    "D_geometry": "D 几何配合",
}


def load_all_records():
    """{baseline: [record, ...]}"""
    out = {}
    for b in BASELINES:
        out[b] = []
        d = RAW / b
        if not d.exists():
            continue
        for f in d.glob("qa_*.json"):
            r = json.load(open(f, encoding="utf-8"))
            out[b].append(r)
    return out


def aggregate(records: list, tier: int = 1, category: str = None):
    keys = ["recall@5", "mrr", "hit@1", "hit@5", "ndcg@5",
            "judge_relevance", "judge_completeness", "judge_correctness"]
    sums = defaultdict(float)
    n = 0
    for r in records:
        if r.get("tier") != tier:
            continue
        if category and r.get("category") != category:
            continue
        m = r.get("metrics") or {}
        if not m:
            continue
        for k in keys:
            v = m.get(k, 0)
            sums[k] += float(v) if isinstance(v, (int, float)) else 0
        n += 1
    if n == 0:
        return None
    return {"n": n, **{k: sums[k] / n for k in keys}}


# ─────────────────────────────────────────────────────────────────────────────
# Fig 8：主实验柱状对比（Tier-1）
# ─────────────────────────────────────────────────────────────────────────────
def plot_fig8(all_recs):
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    baselines = list(BASELINES.keys())
    labels = [BASELINES[b] for b in baselines]
    metrics_left = ["recall@5", "mrr", "hit@1"]
    metric_left_zh = ["Recall@5", "MRR", "Hit@1"]
    metrics_right = ["judge_relevance", "judge_completeness", "judge_correctness"]
    metric_right_zh = ["Relevance", "Completeness", "Correctness"]

    aggs = {b: aggregate(all_recs[b], tier=1) for b in baselines}

    # 左：检索指标（0-1）
    x = np.arange(len(baselines))
    width = 0.26
    colors_l = ["#3a7bd5", "#00a98f", "#f5a623"]
    for i, (m, zh) in enumerate(zip(metrics_left, metric_left_zh)):
        ys = [aggs[b][m] if aggs[b] else 0 for b in baselines]
        axes[0].bar(x + (i - 1) * width, ys, width, label=zh, color=colors_l[i], edgecolor="white", linewidth=0.5)
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(labels, rotation=20, ha="right", fontsize=9)
    axes[0].set_ylim(0.6, 1.05)
    axes[0].set_ylabel("Score", fontsize=11)
    axes[0].set_title("(a) 检索阶段指标（Tier-1, 60题）", fontsize=12)
    axes[0].legend(loc="lower left", fontsize=9, frameon=True)
    axes[0].grid(axis="y", alpha=0.3, linestyle="--")

    # 右：LLM-Judge（0-5）
    colors_r = ["#7b68ee", "#d56b3a", "#3aa55a"]
    for i, (m, zh) in enumerate(zip(metrics_right, metric_right_zh)):
        ys = [aggs[b][m] if aggs[b] else 0 for b in baselines]
        axes[1].bar(x + (i - 1) * width, ys, width, label=zh, color=colors_r[i], edgecolor="white", linewidth=0.5)
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(labels, rotation=20, ha="right", fontsize=9)
    axes[1].set_ylim(0, 5)
    axes[1].set_ylabel("LLM-Judge Score (0-5)", fontsize=11)
    axes[1].set_title("(b) 生成阶段 LLM-Judge 三维评分", fontsize=12)
    axes[1].legend(loc="lower left", fontsize=9, frameon=True)
    axes[1].grid(axis="y", alpha=0.3, linestyle="--")

    plt.tight_layout()
    out = FIG / "fig8_main_compare.pdf"
    plt.savefig(out, bbox_inches="tight")
    plt.close()
    print(f"[OK] {out}")


# ─────────────────────────────────────────────────────────────────────────────
# Fig 9：消融 Δ 跌幅（vs B6）
# ─────────────────────────────────────────────────────────────────────────────
def plot_fig9(all_recs):
    base = aggregate(all_recs["B6_full"], tier=1)
    if not base:
        return
    ablations = {
        "−BM25": "B1_dense",       # 关闭 BM25 退化为 Dense-only
        "−CLIP": "B5_kg",          # 没 CLIP（dense+bm25+kg）
        "−KG": "B4_clip",          # 没 KG（dense+bm25+clip）
        "−Rerank": "A1_no_rerank",
    }
    metrics = [("recall@5", "Recall@5"), ("mrr", "MRR"),
               ("judge_relevance", "Judge Relevance"),
               ("judge_correctness", "Judge Correctness")]

    fig, ax = plt.subplots(figsize=(9, 4.5))
    x = np.arange(len(metrics))
    width = 0.2
    colors = ["#e74c3c", "#9b59b6", "#3498db", "#1abc9c"]

    for i, (label, baseline_id) in enumerate(ablations.items()):
        agg = aggregate(all_recs[baseline_id], tier=1)
        if not agg:
            continue
        deltas = []
        for mk, _ in metrics:
            # judge 是 0-5，归一化到百分比
            if "judge" in mk:
                d = (agg[mk] - base[mk]) / 5.0 * 100
            else:
                d = (agg[mk] - base[mk]) * 100  # 直接百分点
            deltas.append(d)
        ax.bar(x + (i - 1.5) * width, deltas, width, label=label, color=colors[i], edgecolor="white", linewidth=0.5)

    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels([m[1] for m in metrics], fontsize=10)
    ax.set_ylabel("相对 B6 (full) 的变化（百分点）", fontsize=11)
    ax.set_title("消融实验：各路径关闭后相对 B6 的指标变化", fontsize=12)
    ax.legend(loc="best", fontsize=9, frameon=True)
    ax.grid(axis="y", alpha=0.3, linestyle="--")

    plt.tight_layout()
    out = FIG / "fig9_ablation_delta.pdf"
    plt.savefig(out, bbox_inches="tight")
    plt.close()
    print(f"[OK] {out}")


# ─────────────────────────────────────────────────────────────────────────────
# Fig 10：subtype × baseline 热力图（KG 在哪类题占优）
# ─────────────────────────────────────────────────────────────────────────────
def plot_fig10(all_recs):
    cats = list(CATEGORY_LABELS.keys())
    cat_zh = [CATEGORY_LABELS[c] for c in cats]
    baselines = list(BASELINES.keys())
    labels = [BASELINES[b] for b in baselines]

    # 用 judge_relevance 作主指标（最能体现 KG 价值）
    matrix = np.zeros((len(cats), len(baselines)))
    n_matrix = np.zeros((len(cats), len(baselines)))
    for i, c in enumerate(cats):
        for j, b in enumerate(baselines):
            agg = aggregate(all_recs[b], tier=1, category=c)
            if agg:
                matrix[i, j] = agg["judge_relevance"]
                n_matrix[i, j] = agg["n"]

    fig, ax = plt.subplots(figsize=(10, 4))
    im = ax.imshow(matrix, cmap="RdYlGn", aspect="auto", vmin=2.0, vmax=4.5)
    ax.set_xticks(np.arange(len(baselines)))
    ax.set_xticklabels(labels, rotation=20, ha="right", fontsize=9)
    ax.set_yticks(np.arange(len(cats)))
    ax.set_yticklabels(cat_zh, fontsize=10)
    ax.set_title("LLM-Judge Relevance：题型 × Baseline 热力图（Tier-1）", fontsize=12)

    # 数字标注
    for i in range(len(cats)):
        for j in range(len(baselines)):
            val = matrix[i, j]
            n = int(n_matrix[i, j])
            if val > 0:
                color = "white" if val < 2.8 else "black"
                ax.text(j, i, f"{val:.2f}", ha="center", va="center", color=color, fontsize=9)

    cbar = plt.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label("Judge Relevance (0-5)", fontsize=10)
    plt.tight_layout()
    out = FIG / "fig10_subtype_heatmap.pdf"
    plt.savefig(out, bbox_inches="tight")
    plt.close()
    print(f"[OK] {out}")

    # 同时输出 subtype CSV
    csv_lines = ["category," + ",".join(BASELINES[b] for b in baselines)]
    for i, c in enumerate(cats):
        csv_lines.append(CATEGORY_LABELS[c] + "," + ",".join(f"{matrix[i, j]:.3f}" for j in range(len(baselines))))
    (TBL / "table_subtype_judge_relevance.csv").write_text("\n".join(csv_lines), encoding="utf-8-sig")
    print(f"[OK] {TBL / 'table_subtype_judge_relevance.csv'}")


# ─────────────────────────────────────────────────────────────────────────────
# Fig 11：KG 关系分布饼图
# ─────────────────────────────────────────────────────────────────────────────
def plot_fig11():
    """直连 Neo4j 取边类型分布"""
    try:
        from neo4j import GraphDatabase
        drv = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
        rels = []
        with drv.session() as s:
            for row in s.run("MATCH ()-[r]->() RETURN type(r) as rel, count(*) as c ORDER BY c DESC").data():
                rels.append((row["rel"], row["c"]))
        drv.close()
    except Exception as e:
        print(f"[WARN] Neo4j 不可达：{e}，跳过 fig11")
        return

    # 过滤太小的关系（合并为 "其他"）
    total = sum(c for _, c in rels)
    main = [(r, c) for r, c in rels if c / total > 0.01]
    other_sum = sum(c for r, c in rels if c / total <= 0.01)
    if other_sum > 0:
        main.append(("其他", other_sum))

    labels = [r for r, _ in main]
    sizes = [c for _, c in main]

    fig, ax = plt.subplots(figsize=(8, 5.5))
    colors = plt.cm.Set3(np.linspace(0, 1, len(main)))
    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, autopct=lambda p: f"{p:.1f}%\n({int(p/100*total):,})",
        startangle=90, colors=colors, textprops={"fontsize": 9},
        pctdistance=0.78, labeldistance=1.05,
    )
    for at in autotexts:
        at.set_fontsize(7.5)
    ax.set_title(f"PT6A 知识图谱关系类型分布（共 {total:,} 条边）", fontsize=12)
    plt.tight_layout()
    out = FIG / "fig11_kg_relations.pdf"
    plt.savefig(out, bbox_inches="tight")
    plt.close()
    print(f"[OK] {out}")


def main():
    print("Loading experiment records...")
    all_recs = load_all_records()
    for b, recs in all_recs.items():
        print(f"  {b}: {len(recs)} records")

    plot_fig8(all_recs)
    plot_fig9(all_recs)
    plot_fig10(all_recs)
    plot_fig11()
    print("\nAll figures done.")


if __name__ == "__main__":
    main()
