"""Standalone inline 版（不 import 自身），规避沙箱模块加载问题"""
import json
import sys
import warnings
from collections import defaultdict
from pathlib import Path

warnings.filterwarnings("ignore")
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import rcParams

rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "DejaVu Sans"]
rcParams["axes.unicode_minus"] = False
rcParams["font.size"] = 11
rcParams["pdf.fonttype"] = 42

ROOT = Path("C:/xjp/代码/rag-demo")
RAW = ROOT / "docs" / "experiments" / "raw"
FIG = ROOT / "paper" / "figures"
TBL = ROOT / "docs" / "experiments"
FIG.mkdir(parents=True, exist_ok=True)

BASELINES = {
    "B1_dense": "Dense-only",
    "B2_bm25": "BM25-only",
    "B3_hybrid": "Hybrid (RRF)",
    "B4_clip": "+CLIP",
    "B5_kg": "+KG",
    "B6_full": "MHRAG (full)",
    "A1_no_rerank": "B6 -Rerank",
}

CATEGORY_LABELS = {
    "A_structure": "A 零件结构",
    "B_procedure": "B 工序工具",
    "C_specification": "C 技术规范",
    "D_geometry": "D 几何配合",
}

# ─── 加载记录 ─────────────────────────────────────────
print("Loading...")
all_recs = {}
for b in BASELINES:
    all_recs[b] = []
    d = RAW / b
    if not d.exists():
        continue
    for f in d.glob("qa_*.json"):
        with open(f, encoding="utf-8") as fp:
            all_recs[b].append(json.load(fp))
    print(f"  {b}: {len(all_recs[b])}")


def aggregate(records, tier=1, category=None):
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


# ─── Fig 8 ─────────────────────────────────────────
print("Fig 8...")
fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
baselines = list(BASELINES.keys())
labels = [BASELINES[b] for b in baselines]
aggs = {b: aggregate(all_recs[b], tier=1) for b in baselines}

x = np.arange(len(baselines))
width = 0.26
metrics_l = [("recall@5", "Recall@5", "#3a7bd5"),
             ("mrr", "MRR", "#00a98f"),
             ("hit@1", "Hit@1", "#f5a623")]
for i, (m, zh, c) in enumerate(metrics_l):
    ys = [aggs[b][m] if aggs[b] else 0 for b in baselines]
    axes[0].bar(x + (i - 1) * width, ys, width, label=zh, color=c, edgecolor="white", linewidth=0.5)
axes[0].set_xticks(x)
axes[0].set_xticklabels(labels, rotation=20, ha="right", fontsize=9)
axes[0].set_ylim(0.6, 1.10)
axes[0].set_ylabel("Score", fontsize=11)
axes[0].set_title("(a) 检索阶段指标（Tier-1, 60题）", fontsize=12)
axes[0].legend(loc="upper center", bbox_to_anchor=(0.5, 1.0), ncol=3,
               fontsize=9, frameon=True, columnspacing=1.0, handletextpad=0.4)
axes[0].grid(axis="y", alpha=0.3, linestyle="--")

metrics_r = [("judge_relevance", "Relevance", "#7b68ee"),
             ("judge_completeness", "Completeness", "#d56b3a"),
             ("judge_correctness", "Correctness", "#3aa55a")]
for i, (m, zh, c) in enumerate(metrics_r):
    ys = [aggs[b][m] if aggs[b] else 0 for b in baselines]
    axes[1].bar(x + (i - 1) * width, ys, width, label=zh, color=c, edgecolor="white", linewidth=0.5)
axes[1].set_xticks(x)
axes[1].set_xticklabels(labels, rotation=20, ha="right", fontsize=9)
axes[1].set_ylim(0, 5.6)
axes[1].set_ylabel("LLM-Judge Score (0-5)", fontsize=11)
axes[1].set_title("(b) 生成阶段 LLM-Judge 三维评分", fontsize=12)
axes[1].legend(loc="upper center", bbox_to_anchor=(0.5, 1.0), ncol=3,
               fontsize=9, frameon=True, columnspacing=1.0, handletextpad=0.4)
axes[1].grid(axis="y", alpha=0.3, linestyle="--")
plt.tight_layout()
plt.savefig(FIG / "fig8_main_compare.pdf", bbox_inches="tight")
plt.close()
print(f"  -> {FIG / 'fig8_main_compare.pdf'}")

# ─── Fig 9 消融 ─────────────────────────────────────────
print("Fig 9...")
base = aggregate(all_recs["B6_full"], tier=1)
ablations = {"-BM25": "B1_dense", "-CLIP": "B5_kg", "-KG": "B4_clip", "-Rerank": "A1_no_rerank"}
metrics = [("recall@5", "Recall@5"), ("mrr", "MRR"),
           ("judge_relevance", "Judge Relevance"),
           ("judge_correctness", "Judge Correctness")]

fig, ax = plt.subplots(figsize=(9, 4.5))
x = np.arange(len(metrics))
width = 0.2
colors = ["#e74c3c", "#9b59b6", "#3498db", "#1abc9c"]
for i, (lbl, bid) in enumerate(ablations.items()):
    agg = aggregate(all_recs[bid], tier=1)
    deltas = []
    for mk, _ in metrics:
        if "judge" in mk:
            d = (agg[mk] - base[mk]) / 5.0 * 100
        else:
            d = (agg[mk] - base[mk]) * 100
        deltas.append(d)
    ax.bar(x + (i - 1.5) * width, deltas, width, label=lbl, color=colors[i], edgecolor="white", linewidth=0.5)

ax.axhline(0, color="black", linewidth=0.8)
ax.set_xticks(x)
ax.set_xticklabels([m[1] for m in metrics], fontsize=10)
ax.set_ylabel("相对 B6 (full) 的变化（百分点）", fontsize=11)
ax.set_title("消融实验：各路径关闭后相对 B6 的指标变化", fontsize=12)
ax.legend(loc="best", fontsize=9, frameon=True)
ax.grid(axis="y", alpha=0.3, linestyle="--")
plt.tight_layout()
plt.savefig(FIG / "fig9_ablation_delta.pdf", bbox_inches="tight")
plt.close()
print(f"  -> {FIG / 'fig9_ablation_delta.pdf'}")

# ─── Fig 10 热力图 ─────────────────────────────────────────
print("Fig 10...")
cats = list(CATEGORY_LABELS.keys())
cat_zh = [CATEGORY_LABELS[c] for c in cats]
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
for i in range(len(cats)):
    for j in range(len(baselines)):
        val = matrix[i, j]
        if val > 0:
            color = "white" if val < 2.8 else "black"
            ax.text(j, i, f"{val:.2f}", ha="center", va="center", color=color, fontsize=9)
cbar = plt.colorbar(im, ax=ax, shrink=0.8)
cbar.set_label("Judge Relevance (0-5)", fontsize=10)
plt.tight_layout()
plt.savefig(FIG / "fig10_subtype_heatmap.pdf", bbox_inches="tight")
plt.close()
print(f"  -> {FIG / 'fig10_subtype_heatmap.pdf'}")

# CSV
csv_lines = ["category," + ",".join(BASELINES[b] for b in baselines)]
for i, c in enumerate(cats):
    csv_lines.append(CATEGORY_LABELS[c] + "," + ",".join(f"{matrix[i, j]:.3f}" for j in range(len(baselines))))
(TBL / "table_subtype_judge_relevance.csv").write_text("\n".join(csv_lines), encoding="utf-8-sig")
print(f"  -> {TBL / 'table_subtype_judge_relevance.csv'}")

# ─── Fig 11 KG 关系水平柱状图 ─────────────────────────────────────────
print("Fig 11...")
try:
    from neo4j import GraphDatabase
    drv = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
    rels = []
    with drv.session() as s:
        for row in s.run("MATCH ()-[r]->() RETURN type(r) as rel, count(*) as c ORDER BY c DESC").data():
            rels.append((row["rel"], row["c"]))
    drv.close()
    total = sum(c for _, c in rels)
    # 按数量从小到大排序（horizontal bar 上→下数量递增）
    rels_sorted = sorted(rels, key=lambda x: x[1])
    names = [r for r, _ in rels_sorted]
    counts = [c for _, c in rels_sorted]
    pcts = [c / total * 100 for c in counts]

    fig, ax = plt.subplots(figsize=(9, max(4.5, 0.45 * len(names) + 1.0)))
    cmap = plt.cm.viridis(np.linspace(0.15, 0.85, len(names)))
    bars = ax.barh(np.arange(len(names)), counts, color=cmap, edgecolor="white", linewidth=0.6)
    ax.set_yticks(np.arange(len(names)))
    ax.set_yticklabels(names, fontsize=10)
    ax.set_xlabel("边数量", fontsize=11)
    ax.set_title(f"PT6A 知识图谱关系分布（9 类核心语义关系 + 2 类辅助关系，共 {total:,} 条边）",
                 fontsize=12)
    ax.grid(axis="x", alpha=0.3, linestyle="--")
    ax.set_xlim(0, max(counts) * 1.18)
    for i, (c, p) in enumerate(zip(counts, pcts)):
        ax.text(c + max(counts) * 0.012, i, f"{c:,}  ({p:.1f}%)",
                va="center", fontsize=9, color="#222")
    plt.tight_layout()
    plt.savefig(FIG / "fig11_kg_relations.pdf", bbox_inches="tight")
    plt.close()
    print(f"  -> {FIG / 'fig11_kg_relations.pdf'}")
except Exception as e:
    print(f"  Neo4j err: {e}, fig11 skipped")

print("\nDONE")
