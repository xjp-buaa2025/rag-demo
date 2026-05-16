from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np


OUT_DIR = Path(__file__).resolve().parent

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "axes.unicode_minus": False,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    }
)


BASELINES = ["B1\nDense", "B2\nBM25", "B3\nHybrid", "B4\nMHRAG"]

RETRIEVAL = {
    "Recall@5": [0.778, 0.719, 0.769, 0.697],
    "MRR": [0.992, 0.938, 0.983, 0.926],
    "Hit@1": [0.983, 0.900, 0.967, 0.867],
    "NDCG@5": [0.987, 0.951, 0.974, 0.951],
}

JUDGE = {
    "Relevance": [3.38, 3.43, 3.48, 3.50],
    "Completeness": [2.88, 2.78, 2.88, 3.02],
    "Correctness": [2.12, 2.00, 2.05, 2.35],
}

ENGINEERING = {
    "Retrieval": [2.17, 2.03, 3.82, 4.78],
    "Generation": [3.05, 2.94, 3.40, 2.98],
    "HR": [46.25, 35.00, 43.75, 35.00],
}

COLORS = {
    "dense": "#2E86C1",
    "bm25": "#1E8449",
    "kg": "#8E44AD",
    "gen": "#922B21",
    "neutral": "#555555",
    "b1": "#5DADE2",
    "b2": "#58D68D",
    "b3": "#F5B041",
    "b4": "#AF7AC5",
}


def save(fig, filename):
    fig.savefig(OUT_DIR / filename, bbox_inches="tight")
    plt.close(fig)


def draw_box(ax, xy, w, h, text, fc, ec, fontsize=9, weight="normal"):
    box = patches.FancyBboxPatch(
        xy,
        w,
        h,
        boxstyle="round,pad=0.02,rounding_size=0.025",
        linewidth=1.3,
        edgecolor=ec,
        facecolor=fc,
    )
    ax.add_patch(box)
    ax.text(
        xy[0] + w / 2,
        xy[1] + h / 2,
        text,
        ha="center",
        va="center",
        fontsize=fontsize,
        fontweight=weight,
        color="#222222",
    )


def arrow(ax, p1, p2, color="#555555", lw=1.4, style="-"):
    ax.annotate(
        "",
        xy=p2,
        xytext=p1,
        arrowprops=dict(arrowstyle="-|>", lw=lw, color=color, linestyle=style),
    )


def fig1_architecture():
    fig, ax = plt.subplots(figsize=(13.5, 6.2))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    zones = [
        (0.02, 0.08, 0.18, 0.84, "Sources"),
        (0.24, 0.08, 0.30, 0.84, "Offline knowledge build"),
        (0.58, 0.08, 0.40, 0.84, "Online question answering"),
    ]
    for x, y, w, h, title in zones:
        rect = patches.FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.015,rounding_size=0.02",
            linewidth=1.2,
            edgecolor="#B0B0B0",
            facecolor="#F8F9F9",
            linestyle="--",
        )
        ax.add_patch(rect)
        ax.text(x + 0.02, y + h - 0.055, title, fontsize=12, fontweight="bold", color="#333333")

    draw_box(ax, (0.05, 0.68), 0.12, 0.10, "Manual\nPDF/Markdown", "#FFFFFF", "#999999")
    draw_box(ax, (0.05, 0.45), 0.12, 0.10, "BOM\nparts list", "#FFFFFF", "#999999")
    draw_box(ax, (0.05, 0.22), 0.12, 0.10, "CAD/IPC\nSTEP data", "#FFFFFF", "#999999")

    draw_box(ax, (0.27, 0.67), 0.09, 0.10, "Parse\n& chunk", "#D6EAF8", COLORS["dense"])
    draw_box(ax, (0.385, 0.67), 0.09, 0.10, "BGE-M3\ntext embed", "#D6EAF8", COLORS["dense"])
    draw_box(ax, (0.475, 0.67), 0.055, 0.10, "Qdrant\ntext", "#AED6F1", COLORS["dense"], fontsize=8)

    draw_box(ax, (0.27, 0.34), 0.09, 0.11, "BOM/CAD/\nmanual agents", "#D5F5E3", COLORS["bm25"], fontsize=8)
    draw_box(ax, (0.385, 0.34), 0.09, 0.11, "Entity\nalignment", "#D5F5E3", COLORS["bm25"])
    draw_box(ax, (0.475, 0.34), 0.055, 0.11, "Neo4j\nKG", "#ABEBC6", COLORS["bm25"], fontsize=8)

    draw_box(ax, (0.61, 0.74), 0.13, 0.08, "User query", "#FCF3CF", "#D4AC0D")
    draw_box(ax, (0.78, 0.74), 0.13, 0.08, "Multi-query\nexpansion", "#FCF3CF", "#D4AC0D")

    draw_box(ax, (0.61, 0.58), 0.22, 0.075, "Path 1: Dense retrieval", "#D6EAF8", COLORS["dense"])
    draw_box(ax, (0.61, 0.47), 0.22, 0.075, "Path 2: BM25 retrieval", "#D5F5E3", COLORS["bm25"])
    draw_box(ax, (0.61, 0.36), 0.22, 0.075, "Path 3: KG subgraph retrieval", "#E8DAEF", COLORS["kg"])

    draw_box(ax, (0.86, 0.53), 0.10, 0.08, "RRF\nfusion", "#F9EBEA", COLORS["gen"], fontsize=8, weight="bold")
    draw_box(ax, (0.86, 0.40), 0.10, 0.08, "BGE\nrerank", "#F9EBEA", COLORS["gen"], fontsize=8, weight="bold")
    draw_box(ax, (0.86, 0.27), 0.10, 0.08, "LLM answer\n+ sources", "#F9EBEA", COLORS["gen"], fontsize=8, weight="bold")

    arrow(ax, (0.17, 0.73), (0.27, 0.72))
    arrow(ax, (0.17, 0.50), (0.27, 0.40))
    arrow(ax, (0.17, 0.27), (0.27, 0.38))
    arrow(ax, (0.36, 0.72), (0.385, 0.72), COLORS["dense"])
    arrow(ax, (0.475, 0.72), (0.475, 0.72), COLORS["dense"])
    arrow(ax, (0.36, 0.40), (0.385, 0.40), COLORS["bm25"])
    arrow(ax, (0.475, 0.40), (0.475, 0.40), COLORS["bm25"])
    arrow(ax, (0.53, 0.72), (0.61, 0.62), COLORS["dense"], style="--")
    arrow(ax, (0.53, 0.40), (0.61, 0.40), COLORS["kg"], style="--")
    arrow(ax, (0.74, 0.78), (0.78, 0.78), "#D4AC0D")
    arrow(ax, (0.845, 0.62), (0.86, 0.57))
    arrow(ax, (0.845, 0.51), (0.86, 0.57))
    arrow(ax, (0.845, 0.40), (0.86, 0.57))
    arrow(ax, (0.91, 0.53), (0.91, 0.48), COLORS["gen"])
    arrow(ax, (0.91, 0.40), (0.91, 0.35), COLORS["gen"])

    ax.text(
        0.50,
        0.03,
        "MHRAG uses text retrieval for coverage and KG subgraphs for factual constraints.",
        ha="center",
        fontsize=9,
        color="#555555",
    )
    save(fig, "fig1_architecture.pdf")


def fig8_main_compare():
    x = np.arange(len(BASELINES))
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.6))

    width = 0.18
    for i, (name, vals) in enumerate(RETRIEVAL.items()):
        axes[0].bar(x + (i - 1.5) * width, vals, width, label=name)
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(BASELINES)
    axes[0].set_ylim(0.62, 1.03)
    axes[0].set_ylabel("Score")
    axes[0].set_title("Tier-1 retrieval metrics")
    axes[0].grid(axis="y", linestyle="--", alpha=0.35)
    axes[0].legend(ncol=2, fontsize=8, frameon=False)

    width = 0.22
    for i, (name, vals) in enumerate(JUDGE.items()):
        axes[1].bar(x + (i - 1) * width, vals, width, label=name)
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(BASELINES)
    axes[1].set_ylim(1.8, 3.75)
    axes[1].set_ylabel("Judge score (0-5)")
    axes[1].set_title("Tier-1 answer quality")
    axes[1].grid(axis="y", linestyle="--", alpha=0.35)
    axes[1].legend(fontsize=8, frameon=False)

    fig.suptitle("Main comparison: retrieval ranking vs. generation quality", fontsize=12, fontweight="bold")
    fig.tight_layout()
    save(fig, "fig8_main_compare.pdf")


def fig9_ablation_delta():
    metrics = ["Recall@5", "MRR", "Relevance", "Completeness", "Correctness"]
    b4 = np.array([0.697, 0.926, 3.50, 3.02, 2.35])
    variants = {
        "B1 Dense-only": np.array([0.778, 0.992, 3.38, 2.88, 2.12]) - b4,
        "B2 BM25-only": np.array([0.719, 0.938, 3.43, 2.78, 2.00]) - b4,
        "B3 Dense+BM25": np.array([0.769, 0.983, 3.48, 2.88, 2.05]) - b4,
    }
    colors = ["#5DADE2", "#58D68D", "#F5B041"]

    fig, ax = plt.subplots(figsize=(11.5, 4.8))
    x = np.arange(len(metrics))
    width = 0.22
    for i, (label, vals) in enumerate(variants.items()):
        ax.bar(x + (i - 1) * width, vals, width, label=label, color=colors[i], edgecolor="white")

    ax.axhline(0, color="#333333", linewidth=1)
    ax.axvline(1.5, color="#777777", linestyle=":", linewidth=1)
    ax.text(0.5, 0.095, "retrieval metrics", ha="center", color="#666666", fontsize=9)
    ax.text(3.0, 0.095, "judge metrics", ha="center", color="#666666", fontsize=9)
    ax.set_xticks(x)
    ax.set_xticklabels(metrics)
    ax.set_ylabel("Difference from B4 MHRAG")
    ax.set_title("Ablation view: what changes when KG is removed or paths are isolated")
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    ax.legend(frameon=False, fontsize=9, loc="lower left")
    ax.set_ylim(-0.42, 0.14)
    fig.tight_layout()
    save(fig, "fig9_ablation_delta.pdf")


def fig12_engineering():
    x = np.arange(len(BASELINES))
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.4))

    retrieval = np.array(ENGINEERING["Retrieval"])
    generation = np.array(ENGINEERING["Generation"])
    axes[0].bar(x, retrieval, label="Retrieval", color="#85C1E9")
    axes[0].bar(x, generation, bottom=retrieval, label="Generation", color="#F1948A")
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(BASELINES)
    axes[0].set_ylabel("Latency (s)")
    axes[0].set_title("End-to-end latency")
    axes[0].grid(axis="y", linestyle="--", alpha=0.35)
    axes[0].legend(frameon=False)

    bars = axes[1].bar(x, ENGINEERING["HR"], color=["#5DADE2", "#58D68D", "#F5B041", "#AF7AC5"])
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(BASELINES)
    axes[1].set_ylim(0, 52)
    axes[1].set_ylabel("Hallucination rate (%)")
    axes[1].set_title("Answer-mismatch risk")
    axes[1].grid(axis="y", linestyle="--", alpha=0.35)
    for bar, val in zip(bars, ENGINEERING["HR"]):
        axes[1].text(bar.get_x() + bar.get_width() / 2, val + 1.0, f"{val:.1f}", ha="center", fontsize=8)

    fig.suptitle("Engineering trade-off: KG adds retrieval cost but improves factual constraints", fontsize=12, fontweight="bold")
    fig.tight_layout()
    save(fig, "fig12_engineering.pdf")


def main():
    fig1_architecture()
    fig8_main_compare()
    fig9_ablation_delta()
    fig12_engineering()
    print("Generated current MHRAG figures in", OUT_DIR)


if __name__ == "__main__":
    main()
