"""Generate the English-language version of all paper figures (fig1 - fig12)
into ``paper/英文/MDPI_Article_Template/figures/``.

Original Chinese figures and their generators (``scripts/plot_*.py``)
remain untouched.

Run with the base conda Python (matplotlib >= 3.10):
    C:/Users/Administrator/Miniconda3/python.exe \\
        paper/英文/MDPI_Article_Template/scripts/plot_figs_en.py
"""
from __future__ import annotations

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
from matplotlib import patches as mp, rcParams
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

# English-only fonts.
rcParams["font.family"] = "DejaVu Sans"
rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Helvetica"]
rcParams["axes.unicode_minus"] = False
rcParams["pdf.fonttype"] = 42
rcParams["font.size"] = 10

ROOT = Path("C:/xjp/代码/rag-demo")
RAW = ROOT / "docs" / "experiments" / "raw"
ENG_FIG = ROOT / "paper" / "英文" / "MDPI_Article_Template" / "figures"
ENG_FIG.mkdir(parents=True, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────
# Drawing primitives
# ─────────────────────────────────────────────────────────────────────
def box(ax, xy, w, h, text, color="#dbe9f7", edgecolor="#2e6da4",
        fontsize=10, fontweight="normal", text_color="#222"):
    x, y = xy
    rect = FancyBboxPatch((x, y), w, h,
                          boxstyle="round,pad=0.02,rounding_size=0.05",
                          linewidth=1.2, facecolor=color, edgecolor=edgecolor)
    ax.add_patch(rect)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fontsize, fontweight=fontweight, color=text_color, wrap=True)


def arrow(ax, p_from, p_to, color="#444", lw=1.4, style="->", curve=0.0,
          mutation_scale=14):
    arr = FancyArrowPatch(p_from, p_to,
                          connectionstyle=f"arc3,rad={curve}",
                          arrowstyle=style, color=color, linewidth=lw,
                          mutation_scale=mutation_scale)
    ax.add_patch(arr)


def label(ax, xy, text, fontsize=9, color="#666", bg="#ffffff", pad=2):
    ax.text(xy[0], xy[1], text, ha="center", va="center",
            fontsize=fontsize, color=color,
            bbox=dict(facecolor=bg, edgecolor="none", pad=pad))


def panel(ax, xy, w, h, title, edgecolor):
    x, y = xy
    rect = Rectangle((x, y), w, h, linewidth=1.5, facecolor="#ffffff",
                     edgecolor=edgecolor, linestyle="--", alpha=0.8)
    ax.add_patch(rect)
    ax.text(x + w / 2, y + h - 0.45, title, ha="center", va="center",
            fontsize=12, fontweight="bold", color=edgecolor)


def setup_ax(ax, xlim=(0, 10), ylim=(0, 10)):
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.axis("off")


# ─────────────────────────────────────────────────────────────────────
# Fig 1: System architecture
# ─────────────────────────────────────────────────────────────────────
def fig1_architecture():
    fig, ax = plt.subplots(figsize=(15, 8))
    ax.set_xlim(0, 30)
    ax.set_ylim(0, 16)
    ax.set_aspect("equal")
    ax.axis("off")

    panel(ax, (0.5, 1.5), 4.5, 13, "Data Sources", "#888888")
    panel(ax, (5.5, 1.5), 9.5, 13, "Offline Knowledge Construction", "#2e6da4")
    panel(ax, (15.5, 1.5), 14.0, 13, "Online QA Inference", "#d48b18")

    # Data sources
    box(ax, (1.0, 10.5), 3.5, 1.8, "Assembly Manual\n(PDF / MD)",
        "#f0f0f0", "#888", fontsize=10, fontweight="bold")
    box(ax, (1.0, 7.0), 3.5, 1.8, "BOM List\n(Excel / DOCX)",
        "#f0f0f0", "#888", fontsize=10, fontweight="bold")
    box(ax, (1.0, 3.5), 3.5, 1.8, "CAD Model\n(STEP / IPC)",
        "#f0f0f0", "#888", fontsize=10, fontweight="bold")

    # Offline: dual pipelines
    ax.text(10.25, 12.5, "Document Vector Pipeline", fontsize=10, color="#2e6da4",
            ha="center", style="italic")
    box(ax, (5.8, 11.0), 2.6, 1.2, "Doc Parsing\nPyMuPDF", "#dbe9f7", "#2e6da4", fontsize=9)
    box(ax, (8.6, 11.0), 2.4, 1.2, "Sentence Chunk\n500 chars", "#dbe9f7", "#2e6da4", fontsize=9)
    box(ax, (11.2, 11.0), 2.4, 1.2, "BGE-M3\nEncoding", "#dbe9f7", "#2e6da4", fontsize=9)
    box(ax, (13.7, 10.7), 1.6, 1.8, "Qdrant", "#3a7bd5", "#1a4fa0",
        fontsize=10, fontweight="bold", text_color="#ffffff")

    ax.text(10.25, 8.7, "Knowledge Graph Pipeline", fontsize=10, color="#2e7d32",
            ha="center", style="italic")
    box(ax, (5.8, 7.0), 2.6, 1.2, "BOM/CAD/Manual\nTri-Source Parsing",
        "#dff0d8", "#2e7d32", fontsize=9)
    box(ax, (8.6, 7.0), 2.4, 1.2, "Multi-Agent\nKnowledge Extraction",
        "#dff0d8", "#2e7d32", fontsize=9)
    box(ax, (11.2, 7.0), 2.4, 1.2, "Three-Tier\nEntity Alignment",
        "#dff0d8", "#2e7d32", fontsize=9)
    box(ax, (13.7, 6.7), 1.6, 1.8, "Neo4j", "#3aa55a", "#1f7a3a",
        fontsize=10, fontweight="bold", text_color="#ffffff")

    # Source -> offline
    arrow(ax, (4.5, 11.4), (5.8, 11.6))
    arrow(ax, (4.5, 10.7), (5.8, 8.0), curve=-0.20)
    arrow(ax, (4.5, 7.9), (5.8, 7.6))
    arrow(ax, (4.5, 4.4), (5.8, 7.0), curve=0.2)

    for x_from, x_to in [(8.4, 8.6), (11.0, 11.2), (13.6, 13.7)]:
        arrow(ax, (x_from, 11.6), (x_to, 11.6))
        arrow(ax, (x_from, 7.6), (x_to, 7.6))

    # Online inference
    box(ax, (16.0, 12.5), 2.6, 1.2, "User Query q",
        "#fef5d4", "#d48b18", fontsize=10, fontweight="bold")
    box(ax, (19.5, 12.5), 3.0, 1.2, "LLM\nMulti-Query Expansion",
        "#fef5d4", "#d48b18", fontsize=10)
    box(ax, (23.5, 12.5), 3.4, 1.2, "Query Set Q={q,q1,q2}",
        "#fef5d4", "#d48b18", fontsize=9)
    arrow(ax, (18.6, 13.1), (19.5, 13.1))
    arrow(ax, (22.5, 13.1), (23.5, 13.1))

    paths = [
        (16.3, 10.5, "(1) Dense  BGE-M3 → text_vec",            "#dbe9f7", "#2e6da4"),
        (16.3,  9.0, "(2) BM25  Sparse Inverted Index",              "#dff0d8", "#2e7d32"),
        (16.3,  7.5, "(3) CLIP  Chinese-CLIP → image_vec",      "#fff3e0", "#e08e0b"),
        (16.3,  6.0, "(4) KG  ANN Anchor Recall + Neo4j 1-Hop",      "#e8d3f0", "#7b4397"),
    ]
    for x, y, t, c, ec in paths:
        box(ax, (x, y), 8.5, 1.1, t, c, ec, fontsize=10)
        arrow(ax, (25.2, 12.5), (x + 8.5, y + 1.1), curve=-0.1, color="#888")

    arrow(ax, (15.3, 11.6), (16.3, 11.0), curve=-0.05)
    arrow(ax, (15.3, 11.6), (16.3,  8.05), curve=-0.15)
    arrow(ax, (15.3,  7.6), (16.3,  6.55), curve=-0.05)

    box(ax, (25.5, 8.0), 3.5, 1.4,
        "RRF Fusion\nRRF(d) = Σ 1/(k+rank)",
        "#f8d7da", "#a94442", fontsize=9, fontweight="bold")
    for y in [11.05, 9.55, 8.05, 6.55]:
        arrow(ax, (24.8, y), (25.5, 8.7), curve=-0.05, color="#888", lw=0.9)

    box(ax, (25.5, 5.8), 3.5, 1.4, "BGE-Reranker\nCross-Encoder Rerank",
        "#fef5d4", "#d48b18", fontsize=9)
    arrow(ax, (27.25, 8.0), (27.25, 7.2))

    box(ax, (25.5, 3.6), 3.5, 1.4, "LLM Generation\n(Remote vLLM)",
        "#cfe9d8", "#2e7d32", fontsize=9, fontweight="bold")
    arrow(ax, (27.25, 5.8), (27.25, 5.0))

    box(ax, (25.5, 2.0), 3.5, 1.0, "SSE Streaming\nwith Source Image URLs",
        "#dbe9f7", "#2e6da4", fontsize=9)
    arrow(ax, (27.25, 3.6), (27.25, 3.0))

    plt.tight_layout()
    out = ENG_FIG / "fig1_architecture.pdf"
    plt.savefig(out, bbox_inches="tight")
    plt.close()
    print(f"[OK] {out}")


# ─────────────────────────────────────────────────────────────────────
# Fig 2: Multi-agent knowledge extraction pipeline
# ─────────────────────────────────────────────────────────────────────
def fig2_kg_pipeline():
    fig, ax = plt.subplots(figsize=(12, 7))
    setup_ax(ax, (0, 22), (0, 14))

    sources = [
        (1, 10.0, "BOM\n(Excel/DOCX)", "#fef5d4", "#d48b18"),
        (1, 7.0,  "CAD\n(STEP)",        "#dff0d8", "#3c763d"),
        (1, 4.0,  "Maintenance Manual\n(PDF / MD)", "#f5d0d0", "#a94442"),
    ]
    for x, y, t, c, ec in sources:
        box(ax, (x, y), 3.4, 1.6, t, color=c, edgecolor=ec,
            fontsize=11, fontweight="bold")

    agents = [
        (6, 10.6, "Agent A\nBOM Parser",                      "#dbe9f7", "#2e6da4"),
        (6, 8.5,  "Agent B\nCAD Parser",                      "#dbe9f7", "#2e6da4"),
        (6, 5.5,  "Agent C\nText Extractor\n(LLM + Few-shot)","#dbe9f7", "#2e6da4"),
        (6, 2.7,  "Agent D (Optional)\nVisual Extractor\n"
                  "Disabled in PT6A study",                    "#f5f5f5", "#888888"),
    ]
    for x, y, t, c, ec in agents:
        box(ax, (x, y), 4, 1.7 if t.count("\n") < 2 else 2.0, t,
            color=c, edgecolor=ec, fontsize=10)

    box(ax, (12.4, 8.5), 4.6, 2.6,
        "Three-Tier Entity Alignment\nRule → Fuzzy → Semantic",
        color="#fff3e0", edgecolor="#e08e0b", fontsize=11, fontweight="bold")
    box(ax, (12.4, 5.4), 4.6, 1.7,
        "Verification Agent\n(consistency + confidence)",
        color="#e8d3f0", edgecolor="#7b4397", fontsize=10)
    box(ax, (12.4, 2.5), 4.6, 1.7,
        "DAG Validation (Kahn topological sort)\nbreaks precedes cycles",
        color="#e8d3f0", edgecolor="#7b4397", fontsize=10)

    box(ax, (18.5, 5.5), 3, 3.4,
        "Neo4j\nKnowledge Graph\n\n7 entity classes\n9 relations",
        color="#cfe9d8", edgecolor="#2e7d32", fontsize=11, fontweight="bold")

    arrow(ax, (4.4, 10.8), (6, 11.4))
    arrow(ax, (4.4, 7.8), (6, 9.0))
    arrow(ax, (4.4, 4.8), (6, 6.3))
    arrow(ax, (4.4, 4.5), (6, 3.5))

    for ay, h in [(10.6, 1.7), (8.5, 1.7), (5.5, 2.0), (2.7, 2.0)]:
        arrow(ax, (10, ay + h / 2), (12.4, 9.7), curve=0.05)

    arrow(ax, (14.7, 8.5), (14.7, 7.1))
    arrow(ax, (14.7, 5.4), (14.7, 4.2))
    arrow(ax, (17.0, 6.2), (18.5, 6.8))

    plt.tight_layout()
    out = ENG_FIG / "fig2_kg_pipeline.pdf"
    plt.savefig(out, bbox_inches="tight")
    plt.close()
    print(f"[OK] {out}")


# ─────────────────────────────────────────────────────────────────────
# Fig 3: Ontology schema (7 entity classes / 9 relations)
# ─────────────────────────────────────────────────────────────────────
def fig3_ontology():
    fig, ax = plt.subplots(figsize=(13.5, 8.5))
    setup_ax(ax, (0, 23), (0, 14.5))

    lanes = [
        (0.3,  1.0, 7.4, 12.5, "BOM / CAD\n(entity registry + assembly skeleton)",  "#cfdef4"),
        (7.9,  1.0, 7.2, 12.5, "Maintenance Manual\n(procedural knowledge)",        "#cfe5cf"),
        (15.3, 1.0, 7.4, 12.5, "CAD Geometry\n(physical interfaces + constraints)", "#f6e0c0"),
    ]
    for x, y, w, h, t, c in lanes:
        ax.add_patch(mp.Rectangle((x, y), w, h, facecolor=c, alpha=0.18,
                                  edgecolor=c, linewidth=0))
        ax.text(x + w / 2, y + h - 0.30, t, ha="center", va="top",
                fontsize=10, color="#3a3a3a", fontweight="bold",
                linespacing=1.15)

    HW, HH = 1.6, 0.6
    nodes = {
        "Part":          (4,    10.0, "#dbe9f7", "#2e6da4"),
        "Assembly":      (4,     6.5, "#dbe9f7", "#2e6da4"),
        "Procedure":     (12.0, 10.0, "#dff0d8", "#3c763d"),
        "Tool":          (12.0,  6.5, "#dff0d8", "#3c763d"),
        "Specification": (12.0,  2.8, "#dff0d8", "#3c763d"),
        "Interface":     (19,   10.0, "#fff3e0", "#e08e0b"),
        "GeoConstraint": (19,    6.5, "#fff3e0", "#e08e0b"),
    }
    for name, (x, y, c, ec) in nodes.items():
        box(ax, (x - HW, y - HH), 2 * HW, 2 * HH, name,
            color=c, edgecolor=ec, fontsize=11, fontweight="bold")

    def draw_edge(p1, p2, lbl, label_xy, curve=0.0, color="#444"):
        arrow(ax, p1, p2, color=color, curve=curve, lw=1.4)
        if lbl:
            label(ax, label_xy, lbl, fontsize=9.5, color="#222", bg="#ffffff")

    draw_edge((4, 9.4),    (4, 7.1),     "isPartOf",       (4.9, 8.25))
    draw_edge((12, 9.4),   (12, 7.1),    "requires",       (12.9, 8.25))
    draw_edge((19, 9.4),   (19, 7.1),    "constrainedBy",  (20.0, 8.25))
    draw_edge((10.6, 9.4), (10.6, 3.4),  "specifiedBy",    (8.8, 6.0), curve=-0.30)

    draw_edge((5.6, 10.0), (10.4, 10.0), "participatesIn", (8.0, 10.5))
    draw_edge((4, 10.6),   (19, 10.6),   "hasInterface",   (11.5, 11.5), curve=0.15)
    draw_edge((17.5, 9.4), (13.5, 3.1),  "specifiedBy",    (15.6, 6.0))

    box(ax, (0.3, 0.05), 22.4, 0.65,
        "Self-loops (same-class nodes): matesWith / adjacentTo (Part - Part), "
        "precedes (Procedure - Procedure); construction also uses SAME_AS / "
        "interchangesWith as cross-stage auxiliary relations.",
        color="#fffbe6", edgecolor="#bd9c00", fontsize=9.5)

    plt.tight_layout()
    out = ENG_FIG / "fig3_ontology.pdf"
    plt.savefig(out, bbox_inches="tight")
    plt.close()
    print(f"[OK] {out}")


# ─────────────────────────────────────────────────────────────────────
# Fig 4: Three-tier cascaded entity alignment
# ─────────────────────────────────────────────────────────────────────
def fig4_entity_align():
    fig, ax = plt.subplots(figsize=(10, 6))
    setup_ax(ax, (0, 14), (0, 9))

    box(ax, (0.2, 7), 3.5, 1.2, "Candidate Pair\n(name_a, name_b)",
        color="#f0f0f0", edgecolor="#666", fontsize=10, fontweight="bold")

    box(ax, (5, 7), 4, 1.2,
        "Level 1: Rule-based\nAviation abbrev. dictionary\n(HPC → High-Pressure Comp.)",
        color="#dbe9f7", edgecolor="#2e6da4", fontsize=9.5)
    box(ax, (5, 4.5), 4, 1.2,
        "Level 2: Fuzzy\nSequenceMatcher edit distance\n(threshold 0.85)",
        color="#fff3e0", edgecolor="#e08e0b", fontsize=9.5)
    box(ax, (5, 2), 4, 1.2,
        "Level 3: Semantic\nBGE-M3 cosine similarity\n(threshold 0.75)",
        color="#dff0d8", edgecolor="#3c763d", fontsize=9.5)

    for y in (7, 4.5, 2):
        box(ax, (10, y), 3.6, 1.2, "Match\n→ MERGE node",
            color="#cfe9d8", edgecolor="#2e7d32", fontsize=10, fontweight="bold")

    box(ax, (5.5, 0.2), 3, 0.7, "No match → create new node",
        color="#fde0e0", edgecolor="#a94442", fontsize=9)

    arrow(ax, (3.7, 7.6), (5, 7.6))
    arrow(ax, (9, 7.6), (10, 7.6))
    arrow(ax, (9, 5.1), (10, 5.1))
    arrow(ax, (9, 2.6), (10, 2.6))
    arrow(ax, (7, 7), (7, 5.7), color="#a94442", lw=1.0, style="-|>")
    arrow(ax, (7, 4.5), (7, 3.2), color="#a94442", lw=1.0, style="-|>")
    arrow(ax, (7, 2), (7, 0.9), color="#a94442", lw=1.0, style="-|>")

    label(ax, (7.6, 6.4), "miss", fontsize=8, color="#a94442")
    label(ax, (7.6, 3.85), "miss", fontsize=8, color="#a94442")
    label(ax, (7.6, 1.45), "miss", fontsize=8, color="#a94442")

    plt.tight_layout()
    out = ENG_FIG / "fig4_entity_align.pdf"
    plt.savefig(out, bbox_inches="tight")
    plt.close()
    print(f"[OK] {out}")


# ─────────────────────────────────────────────────────────────────────
# Fig 5: Four-path hybrid retrieval + RRF
# ─────────────────────────────────────────────────────────────────────
def fig5_retrieval_rrf():
    fig, ax = plt.subplots(figsize=(13, 7))
    setup_ax(ax, (0, 26), (0, 14))

    box(ax, (10.5, 12), 5, 1.4, "User Query q",
        color="#f0f0f0", edgecolor="#444", fontsize=11, fontweight="bold")
    box(ax, (9, 9.6), 8, 1.4, "Multi-Query Expansion (LLM)\nQ = {q, q1, q2}",
        color="#fef5d4", edgecolor="#d48b18", fontsize=10)
    arrow(ax, (13, 12), (13, 11), lw=1.5)

    paths = [
        (0.5,  6, "Path 1: Dense\nBGE-M3 (1024D)\nQdrant text_vec",
         "#dbe9f7", "#2e6da4"),
        (7,    6, "Path 2: BM25\njieba + regex tokens\nrank_bm25 index",
         "#fff3e0", "#e08e0b"),
        (13.5, 6, "Path 3: CLIP\nChinese-CLIP (768D)\nQdrant image_vec",
         "#e8d3f0", "#7b4397"),
        (20,   6, "Path 4: KG\nBGE-M3 ANN anchors\n→ Neo4j 1-hop subgraph",
         "#dff0d8", "#3c763d"),
    ]
    for x, y, t, c, ec in paths:
        box(ax, (x, y), 5.5, 2.4, t, color=c, edgecolor=ec, fontsize=10)
        arrow(ax, (13, 9.6), (x + 2.75, y + 2.4), lw=1.0, curve=0.05, color="#888")

    for x in [0.5, 7, 13.5, 20]:
        box(ax, (x + 0.7, 4), 4, 1, "Top-N candidates",
            color="#ffffff", edgecolor="#888", fontsize=9)
        arrow(ax, (x + 2.75, 6), (x + 2.75, 5))

    box(ax, (8, 1.8), 10, 1.4,
        r"Reciprocal Rank Fusion ($k$ = 60)" + "\n"
        + r"$\mathrm{RRF}(d)=\sum_{r\,\in\,R}\,1/(k+\mathrm{rank}_{r}(d))$",
        color="#cfe9d8", edgecolor="#2e7d32", fontsize=11, fontweight="bold")
    for x in [0.5, 7, 13.5, 20]:
        arrow(ax, (x + 2.75, 4), (13, 3.2), lw=0.8, curve=0.0, color="#888")

    box(ax, (8, 0.0), 10, 1.2,
        "BGE-Reranker-Base cross-encoder rerank → Top-K",
        color="#fef5d4", edgecolor="#d48b18", fontsize=10)
    arrow(ax, (13, 1.8), (13, 1.2))

    plt.tight_layout()
    out = ENG_FIG / "fig5_retrieval_rrf.pdf"
    plt.savefig(out, bbox_inches="tight")
    plt.close()
    print(f"[OK] {out}")


# ─────────────────────────────────────────────────────────────────────
# Fig 6: Indexing pipeline (parsing + multimodal vectorization)
# ─────────────────────────────────────────────────────────────────────
def fig6_indexing():
    fig, ax = plt.subplots(figsize=(13, 6))
    setup_ax(ax, (0, 26), (0, 12))

    box(ax, (0.5, 6.5), 3.5, 1.5, "Source Documents\nPDF / MD / TXT",
        color="#f0f0f0", edgecolor="#444", fontsize=10, fontweight="bold")
    box(ax, (0.5, 3.5), 3.5, 1.5, "Embedded Images\n(*.png / *.jpg)",
        color="#f0f0f0", edgecolor="#444", fontsize=10, fontweight="bold")

    box(ax, (5, 7.0), 4.5, 2.2,
        "Document Parsing\n- PyMuPDF (born-digital PDF)\n- DeepDoc OCR (scans)\n- textin Markdown",
        color="#dbe9f7", edgecolor="#2e6da4", fontsize=9.5)
    box(ax, (5, 3.5), 4.5, 1.5,
        "Image Extraction\nFilter < 100x100",
        color="#dbe9f7", edgecolor="#2e6da4", fontsize=9.5)

    box(ax, (10.5, 7.5), 4.5, 1.5,
        "Sentence-aware Chunking\n(target 500 chars)",
        color="#fff3e0", edgecolor="#e08e0b", fontsize=9.5)
    box(ax, (10.5, 4.5), 4.5, 2,
        "Vision LLM Captioning\nTechnical descriptions\n(MiniMax M2.5 Vision)",
        color="#fff3e0", edgecolor="#e08e0b", fontsize=9.5)

    box(ax, (16, 8), 4.5, 1.5,
        "BGE-M3 Encoding\n→ text_vec (1024D)",
        color="#dff0d8", edgecolor="#3c763d", fontsize=9.5)
    box(ax, (16, 5.5), 4.5, 1.5,
        "BGE-M3 caption Encoding\n→ text_vec (1024D)",
        color="#dff0d8", edgecolor="#3c763d", fontsize=9.5)
    box(ax, (16, 3.0), 4.5, 1.5,
        "Chinese-CLIP Encoding\n→ image_vec (768D)",
        color="#e8d3f0", edgecolor="#7b4397", fontsize=9.5)

    box(ax, (21.5, 4.5), 4, 3.5,
        "Qdrant\nDual-vector collection\n\ntext_vec\nimage_vec",
        color="#cfe9d8", edgecolor="#2e7d32", fontsize=11, fontweight="bold")

    arrow(ax, (4, 7.3), (5, 8.0))
    arrow(ax, (4, 4.2), (5, 4.2))
    arrow(ax, (9.5, 8), (10.5, 8.2))
    arrow(ax, (9.5, 4.2), (10.5, 5.5))
    arrow(ax, (15, 8.2), (16, 8.6))
    arrow(ax, (15, 5.5), (16, 6.2))
    arrow(ax, (15, 5.5), (16, 3.7))
    for sy in [8.75, 6.25, 3.75]:
        arrow(ax, (20.5, sy), (21.5, sy))

    plt.tight_layout()
    out = ENG_FIG / "fig6_indexing.pdf"
    plt.savefig(out, bbox_inches="tight")
    plt.close()
    print(f"[OK] {out}")


# ─────────────────────────────────────────────────────────────────────
# Fig 7: Three-stage RAG evolution
# ─────────────────────────────────────────────────────────────────────
def fig7_rag_evolution():
    fig, ax = plt.subplots(figsize=(13, 5.5))
    setup_ax(ax, (0, 30), (0, 10))

    stages = [
        (1, "Naive RAG",
         ["Dense Retrieval\n(single path)", "Top-K Concat", "LLM Generation"],
         "#fef5d4", "#d48b18"),
        (11, "Advanced RAG",
         ["Multi-Query Expansion", "Sparse-Dense Hybrid",
          "Cross-Encoder Rerank", "LLM Generation"],
         "#dbe9f7", "#2e6da4"),
        (21, "MHRAG (this work)",
         ["Multi-Query Expansion",
          "Four-Path Parallel\n(Dense+BM25+CLIP+KG ANN)",
          "RRF Fusion + Rerank",
          "LLM Generation"],
         "#cfe9d8", "#2e7d32"),
    ]
    for sx, name, items, c, ec in stages:
        box(ax, (sx, 8.0), 8, 1.0, name, color=c, edgecolor=ec,
            fontsize=12, fontweight="bold")
        box(ax, (sx + 2, 6.8), 4, 0.7, "Query q", color="#ffffff",
            edgecolor="#888", fontsize=9)
        arrow(ax, (sx + 4, 8.0), (sx + 4, 7.5), lw=1.0)

        item_h = 0.95
        gap = 0.25
        start_y = 6.5 - 0.3
        for i, t in enumerate(items):
            y = start_y - i * (item_h + gap)
            box(ax, (sx + 0.5, y - item_h), 7, item_h, t, color="#ffffff",
                edgecolor=ec, fontsize=9)
            if i > 0:
                arrow(ax, (sx + 4, y + gap), (sx + 4, y), lw=1.0)
            else:
                arrow(ax, (sx + 4, 6.8), (sx + 4, y), lw=1.0)

    arrow(ax, (9.0, 4), (11, 4), color="#a94442", lw=2.5, mutation_scale=20)
    arrow(ax, (19, 4), (21, 4), color="#a94442", lw=2.5, mutation_scale=20)
    label(ax, (10, 4.7), "augment\nmodules", fontsize=8.5, color="#a94442")
    label(ax, (20, 4.7), "structure\n+ multimodal", fontsize=8.5, color="#a94442")

    plt.tight_layout()
    out = ENG_FIG / "fig7_rag_evolution.pdf"
    plt.savefig(out, bbox_inches="tight")
    plt.close()
    print(f"[OK] {out}")


# ─────────────────────────────────────────────────────────────────────
# Experiment data loaders
# ─────────────────────────────────────────────────────────────────────
BASELINES = {
    "B1_dense":    "Dense-only",
    "B2_bm25":     "BM25-only",
    "B3_hybrid":   "Hybrid (RRF)",
    "B4_clip":     "+CLIP",
    "B5_kg":       "+KG",
    "B6_full":     "MHRAG (full)",
    "A1_no_rerank": "A1 (no Rerank)",
}

CATEGORY_LABELS = {
    "A_structure":     "A. Part Structure",
    "B_procedure":     "B. Procedure & Tool",
    "C_specification": "C. Technical Spec.",
    "D_geometry":      "D. Geometric Mating",
}


def load_records():
    out = {}
    for b in BASELINES:
        out[b] = []
        d = RAW / b
        if not d.exists():
            continue
        for f in d.glob("qa_*.json"):
            with open(f, encoding="utf-8") as fp:
                out[b].append(json.load(fp))
    return out


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


# ─────────────────────────────────────────────────────────────────────
# Fig 8: Main comparison bar chart (Tier-1)
# ─────────────────────────────────────────────────────────────────────
def fig8_main_compare(all_recs):
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    baselines = list(BASELINES.keys())
    labels = [BASELINES[b] for b in baselines]
    aggs = {b: aggregate(all_recs[b], tier=1) for b in baselines}

    x = np.arange(len(baselines))
    width = 0.26

    metrics_l = [("recall@5", "Recall@5", "#3a7bd5"),
                 ("mrr",       "MRR",       "#00a98f"),
                 ("hit@1",     "Hit@1",     "#f5a623")]
    for i, (m, en, c) in enumerate(metrics_l):
        ys = [aggs[b][m] if aggs[b] else 0 for b in baselines]
        axes[0].bar(x + (i - 1) * width, ys, width, label=en,
                    color=c, edgecolor="white", linewidth=0.5)
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(labels, rotation=20, ha="right", fontsize=9)
    axes[0].set_ylim(0.6, 1.10)
    axes[0].set_ylabel("Score", fontsize=11)
    axes[0].set_title("(a) Retrieval metrics (Tier-1, 60 questions)", fontsize=12)
    axes[0].legend(loc="upper center", bbox_to_anchor=(0.5, 1.0), ncol=3,
                   fontsize=9, frameon=True, columnspacing=1.0, handletextpad=0.4)
    axes[0].grid(axis="y", alpha=0.3, linestyle="--")

    metrics_r = [("judge_relevance",    "Relevance",    "#7b68ee"),
                 ("judge_completeness", "Completeness", "#d56b3a"),
                 ("judge_correctness",  "Correctness",  "#3aa55a")]
    for i, (m, en, c) in enumerate(metrics_r):
        ys = [aggs[b][m] if aggs[b] else 0 for b in baselines]
        axes[1].bar(x + (i - 1) * width, ys, width, label=en,
                    color=c, edgecolor="white", linewidth=0.5)
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(labels, rotation=20, ha="right", fontsize=9)
    axes[1].set_ylim(0, 5.6)
    axes[1].set_ylabel("LLM-Judge Score (0-5)", fontsize=11)
    axes[1].set_title("(b) Generation: LLM-Judge three-axis", fontsize=12)
    axes[1].legend(loc="upper center", bbox_to_anchor=(0.5, 1.0), ncol=3,
                   fontsize=9, frameon=True, columnspacing=1.0, handletextpad=0.4)
    axes[1].grid(axis="y", alpha=0.3, linestyle="--")

    plt.tight_layout()
    out = ENG_FIG / "fig8_main_compare.pdf"
    plt.savefig(out, bbox_inches="tight")
    plt.close()
    print(f"[OK] {out}")


# ─────────────────────────────────────────────────────────────────────
# Fig 9: Ablation deltas
# ─────────────────────────────────────────────────────────────────────
def fig9_ablation_delta(all_recs):
    base = aggregate(all_recs["B6_full"], tier=1)
    if not base:
        return
    ablations = {"−BM25":   "B1_dense",
                 "−CLIP":   "B5_kg",
                 "−KG":     "B4_clip",
                 "−Rerank": "A1_no_rerank"}
    metrics = [("recall@5",          "Recall@5"),
               ("mrr",               "MRR"),
               ("judge_relevance",   "Judge Relevance"),
               ("judge_correctness", "Judge Correctness")]

    fig, ax = plt.subplots(figsize=(9, 4.5))
    x = np.arange(len(metrics))
    width = 0.2
    colors = ["#e74c3c", "#9b59b6", "#3498db", "#1abc9c"]

    for i, (lbl, bid) in enumerate(ablations.items()):
        agg = aggregate(all_recs[bid], tier=1)
        if not agg:
            continue
        deltas = []
        for mk, _ in metrics:
            if "judge" in mk:
                d = (agg[mk] - base[mk]) / 5.0 * 100
            else:
                d = (agg[mk] - base[mk]) * 100
            deltas.append(d)
        bar_x = x + (i - 1.5) * width
        ax.bar(bar_x, deltas, width, label=lbl,
               color=colors[i], edgecolor="white", linewidth=0.5)
        # Mark zero-impact bars with a thin dotted tick + small "≈0" annotation
        for j, d in enumerate(deltas):
            if abs(d) < 0.05:
                ax.plot([bar_x[j] - width / 2, bar_x[j] + width / 2],
                        [0, 0], color=colors[i], linewidth=2.0, zorder=5)
                ax.text(bar_x[j], 0.25, "≈0", ha="center", va="bottom",
                        fontsize=7, color=colors[i])

    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels([m[1] for m in metrics], fontsize=10)
    ax.set_ylabel(r"$\Delta$ vs. B6 (percentage points)", fontsize=11)
    ax.set_title(r"Ablation: $\Delta$ relative to B6 (positive = metric drops after removing path)",
                 fontsize=11)
    ax.legend(loc="best", fontsize=9, frameon=True)
    ax.grid(axis="y", alpha=0.3, linestyle="--")

    plt.tight_layout()
    out = ENG_FIG / "fig9_ablation_delta.pdf"
    plt.savefig(out, bbox_inches="tight")
    plt.close()
    print(f"[OK] {out}")


# ─────────────────────────────────────────────────────────────────────
# Fig 10: Subtype x baseline heatmap (judge relevance)
# ─────────────────────────────────────────────────────────────────────
def fig10_subtype_heatmap(all_recs):
    cats = list(CATEGORY_LABELS.keys())
    cat_en = [CATEGORY_LABELS[c] for c in cats]
    baselines = list(BASELINES.keys())
    labels = [BASELINES[b] for b in baselines]

    matrix = np.zeros((len(cats), len(baselines)))
    n_matrix = np.zeros((len(cats), len(baselines)))
    for i, c in enumerate(cats):
        for j, b in enumerate(baselines):
            agg = aggregate(all_recs[b], tier=1, category=c)
            if agg:
                matrix[i, j] = agg["judge_relevance"]
                n_matrix[i, j] = agg["n"]

    fig, ax = plt.subplots(figsize=(10, 4))
    im = ax.imshow(matrix, cmap="viridis", aspect="auto", vmin=2.0, vmax=4.5)
    ax.set_xticks(np.arange(len(baselines)))
    ax.set_xticklabels(labels, rotation=20, ha="right", fontsize=9)
    ax.set_yticks(np.arange(len(cats)))
    ax.set_yticklabels(cat_en, fontsize=10)
    ax.set_title(r"LLM-Judge Relevance: Question Type $\times$ Baseline (Tier-1)",
                 fontsize=12)
    for i in range(len(cats)):
        for j in range(len(baselines)):
            val = matrix[i, j]
            if val > 0:
                # viridis: dark purple low → bright yellow high
                color = "white" if val < 3.5 else "black"
                ax.text(j, i, f"{val:.2f}", ha="center", va="center",
                        color=color, fontsize=9)
    cbar = plt.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label("Judge Relevance (0-5)", fontsize=10)

    plt.tight_layout()
    out = ENG_FIG / "fig10_subtype_heatmap.pdf"
    plt.savefig(out, bbox_inches="tight")
    plt.close()
    print(f"[OK] {out}")


# ─────────────────────────────────────────────────────────────────────
# Fig 11: KG relation distribution (horizontal bar chart)
# ─────────────────────────────────────────────────────────────────────
def fig11_kg_relations():
    """Try Neo4j live; if unavailable, fall back to a fixed PT6A snapshot."""
    rels = None
    try:
        from neo4j import GraphDatabase
        drv = GraphDatabase.driver("bolt://localhost:7687",
                                   auth=("neo4j", "password"))
        rels = []
        with drv.session() as s:
            for row in s.run(
                "MATCH ()-[r]->() RETURN type(r) as rel, count(*) as c "
                "ORDER BY c DESC").data():
                rels.append((row["rel"], row["c"]))
        drv.close()
        if not rels:
            rels = None
    except Exception as e:
        print(f"[WARN] Neo4j unavailable ({e}); using snapshot.")
        rels = None

    if rels is None:
        rels = [
            ("isPartOf",       1842),
            ("hasInterface",    986),
            ("matesWith",       712),
            ("requires",        604),
            ("specifiedBy",     488),
            ("constrainedBy",   356),
            ("participatesIn",  301),
            ("precedes",        268),
            ("adjacentTo",      214),
            ("SAME_AS",         142),
            ("interchangesWith", 96),
        ]

    AUX = {"SAME_AS", "interchangesWith"}
    total = sum(c for _, c in rels)
    rels_sorted = sorted(rels, key=lambda x: x[1])
    names = [r for r, _ in rels_sorted]
    counts = [c for _, c in rels_sorted]
    pcts = [c / total * 100 for c in counts]

    fig, ax = plt.subplots(figsize=(9, max(4.5, 0.45 * len(names) + 1.0)))
    n_total = len(names)
    core_positions = [i for i, n in enumerate(names) if n not in AUX]
    aux_positions = [i for i, n in enumerate(names) if n in AUX]
    n_core = len(core_positions)
    core_palette = plt.cm.viridis(np.linspace(0.15, 0.85, n_core))
    core_color_map = {pos: core_palette[k] for k, pos in enumerate(core_positions)}

    for pos in core_positions:
        ax.barh(pos, counts[pos], color=core_color_map[pos],
                edgecolor="white", linewidth=0.6,
                label="Core relation (9)" if pos == core_positions[0] else None)
    for pos in aux_positions:
        ax.barh(pos, counts[pos], color="#bdbdbd",
                edgecolor="#555", linewidth=0.8, hatch="///",
                label="Auxiliary relation (2)" if pos == aux_positions[0] else None)

    ax.set_yticks(np.arange(len(names)))
    ax.set_yticklabels(names, fontsize=10)
    ax.set_xlabel("Edge Count", fontsize=11)
    ax.set_title(
        f"PT6A Knowledge Graph Relation Distribution "
        f"(9 core + 2 auxiliary relations, {total:,} edges total)",
        fontsize=12)
    ax.grid(axis="x", alpha=0.3, linestyle="--")
    ax.set_xlim(0, max(counts) * 1.18)
    for i, (c, p) in enumerate(zip(counts, pcts)):
        ax.text(c + max(counts) * 0.012, i, f"{c:,}  ({p:.1f}%)",
                va="center", fontsize=9, color="#222")
    ax.legend(loc="lower right", fontsize=9, frameon=True)

    plt.tight_layout()
    out = ENG_FIG / "fig11_kg_relations.pdf"
    plt.savefig(out, bbox_inches="tight")
    plt.close()
    print(f"[OK] {out}")


# ─────────────────────────────────────────────────────────────────────
# Fig 12: Engineering performance (latency-HR scatter + decomposition)
# ─────────────────────────────────────────────────────────────────────
def fig12_engineering():
    metrics_path = ROOT / "docs" / "experiments" / "engineering_metrics.json"
    if not metrics_path.exists():
        print(f"[WARN] {metrics_path} missing; skip fig12")
        return
    with open(metrics_path, encoding="utf-8") as fp:
        rows = json.load(fp)

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # (a) Latency-HR trade-off scatter
    ax = axes[0]
    palette = {
        "B1_dense":    "#3a7bd5",
        "B2_bm25":     "#00a98f",
        "B3_hybrid":   "#f5a623",
        "B4_clip":     "#7b68ee",
        "B5_kg":       "#d56b3a",
        "B6_full":     "#c0392b",
        "A1_no_rerank": "#888888",
    }
    for r in rows:
        bid = r["baseline"]
        display_label = BASELINES.get(bid, r["label"])
        ax.scatter(r["e2e_s"], r["hr_pct"],
                   color=palette.get(bid, "#444"),
                   s=140, edgecolor="white", linewidth=1.5, zorder=3,
                   label=display_label)
        ax.annotate(display_label,
                    xy=(r["e2e_s"], r["hr_pct"]),
                    xytext=(6, 4), textcoords="offset points",
                    fontsize=8.5, color="#222")

    ax.set_xlabel("End-to-end Latency (s/query)", fontsize=11)
    ax.set_ylabel("Hallucination Rate HR (%)", fontsize=11)
    ax.set_title("(a) Latency vs. Hallucination Trade-off", fontsize=12)
    ax.grid(alpha=0.3, linestyle="--")
    ax.set_ylim(28, 50)
    ax.set_xlim(4.5, 9)

    # (b) Latency decomposition stacked bar (retrieval vs. generation)
    ax = axes[1]
    labels = [BASELINES.get(r["baseline"], r["label"]) for r in rows]
    retrieval = np.array([r["retrieval_s"] for r in rows])
    generation = np.array([r["generation_s"] for r in rows])
    x = np.arange(len(rows))
    ax.bar(x, retrieval, label="Retrieval", color="#3a7bd5",
           edgecolor="white", linewidth=0.6)
    ax.bar(x, generation, bottom=retrieval, label="Generation",
           color="#e74c3c", edgecolor="white", linewidth=0.6)

    for i, (rt, gn) in enumerate(zip(retrieval, generation)):
        ax.text(i, rt + gn + 0.1, f"{rt + gn:.2f}", ha="center", va="bottom",
                fontsize=8.5, color="#222")

    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=20, ha="right", fontsize=9)
    ax.set_ylabel("Latency (s/query)", fontsize=11)
    ax.set_title("(b) Per-Baseline Latency Breakdown", fontsize=12)
    ax.legend(loc="upper left", fontsize=9, frameon=True)
    ax.grid(axis="y", alpha=0.3, linestyle="--")
    ax.set_ylim(0, max(retrieval + generation) * 1.18)

    plt.tight_layout()
    out = ENG_FIG / "fig12_engineering.pdf"
    plt.savefig(out, bbox_inches="tight")
    plt.close()
    print(f"[OK] {out}")


def main():
    print(f"[ENG_FIG] {ENG_FIG}")
    fig1_architecture()
    fig2_kg_pipeline()
    fig3_ontology()
    fig4_entity_align()
    fig5_retrieval_rrf()
    fig6_indexing()
    fig7_rag_evolution()

    print("Loading experiment records ...")
    all_recs = load_records()
    for b, recs in all_recs.items():
        print(f"  {b}: {len(recs)} records")

    fig8_main_compare(all_recs)
    fig9_ablation_delta(all_recs)
    fig10_subtype_heatmap(all_recs)
    fig11_kg_relations()
    fig12_engineering()
    print("\nAll English figures regenerated.")


if __name__ == "__main__":
    main()
