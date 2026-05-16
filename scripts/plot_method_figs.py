"""绘制论文 §2/§3 方法章节的 6 张示意图：
  fig2_kg_pipeline.pdf      多智能体协同知识抽取流水线
  fig3_ontology.pdf         本体模式（7 类实体 / 9 类关系）
  fig4_entity_align.pdf     三级级联实体对齐
  fig5_retrieval_rrf.pdf    四路并行混合检索 + RRF
  fig6_indexing.pdf         文档解析与多模态向量化
  fig7_rag_evolution.pdf    RAG 三阶段演进

依赖：base conda Python（matplotlib 3.10），已注册 SimHei 字体。
用法：C:/Users/Administrator/Miniconda3/python.exe scripts/plot_method_figs.py
"""
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import patches as mp, rcParams
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "DejaVu Sans"]
rcParams["axes.unicode_minus"] = False
rcParams["pdf.fonttype"] = 42
rcParams["font.size"] = 10

ROOT = Path("C:/xjp/代码/rag-demo")
FIG = ROOT / "paper" / "figures"
FIG.mkdir(parents=True, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────
# 通用绘图原语
# ─────────────────────────────────────────────────────────────────────
def box(ax, xy, w, h, text, color="#dbe9f7", edgecolor="#2e6da4",
        fontsize=10, fontweight="normal", text_color="#222"):
    x, y = xy
    rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.05",
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


def setup_ax(ax, xlim=(0, 10), ylim=(0, 10)):
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.axis("off")


# ─────────────────────────────────────────────────────────────────────
# Fig 2: 多智能体协同知识抽取流水线
# ─────────────────────────────────────────────────────────────────────
def fig2_kg_pipeline():
    fig, ax = plt.subplots(figsize=(12, 7))
    setup_ax(ax, (0, 22), (0, 14))

    # 第一列：数据源
    sources = [
        (1, 10.0, "BOM\n(Excel/DOCX)", "#fef5d4", "#d48b18"),
        (1, 7.0, "CAD\n(STEP)", "#dff0d8", "#3c763d"),
        (1, 4.0, "维修手册\n(PDF / MD)", "#f5d0d0", "#a94442"),
    ]
    for x, y, t, c, ec in sources:
        box(ax, (x, y), 3.4, 1.6, t, color=c, edgecolor=ec, fontsize=11, fontweight="bold")

    # 第二列：智能体（避开标题 13.0 处）
    agents = [
        (6, 10.6, "智能体 A\nBOM Parser", "#dbe9f7", "#2e6da4"),
        (6, 8.5, "智能体 B\nCAD Parser", "#dbe9f7", "#2e6da4"),
        (6, 5.5, "智能体 C\nText Extractor\n(LLM + Few-shot)", "#dbe9f7", "#2e6da4"),
        (6, 2.7, "智能体 D（可选）\nVisual Extractor\n本文 PT6A 实验未启用", "#f5f5f5", "#888888"),
    ]
    for x, y, t, c, ec in agents:
        box(ax, (x, y), 4, 1.7 if t.count("\n") < 2 else 2.0, t,
            color=c, edgecolor=ec, fontsize=10)

    # 第三列：融合阶段
    box(ax, (12.4, 8.5), 4.6, 2.6,
        "三级级联实体对齐\n规则 → 模糊 → 语义",
        color="#fff3e0", edgecolor="#e08e0b", fontsize=11, fontweight="bold")
    box(ax, (12.4, 5.4), 4.6, 1.7,
        "Verification Agent\n（一致性校验 + 置信度）",
        color="#e8d3f0", edgecolor="#7b4397", fontsize=10)
    box(ax, (12.4, 2.5), 4.6, 1.7,
        "DAG 校验（Kahn 拓扑排序）\n断 precedes 环路",
        color="#e8d3f0", edgecolor="#7b4397", fontsize=10)

    # 第四列：输出
    box(ax, (18.5, 5.5), 3, 3.4,
        "Neo4j\n知识图谱\n\n7 类实体\n9 类关系",
        color="#cfe9d8", edgecolor="#2e7d32", fontsize=11, fontweight="bold")

    # 箭头：数据源 → 智能体
    arrow(ax, (4.4, 10.8), (6, 11.4))     # BOM -> A
    arrow(ax, (4.4, 7.8), (6, 9.0))       # CAD -> B
    arrow(ax, (4.4, 4.8), (6, 6.3))       # Manual -> C
    arrow(ax, (4.4, 4.5), (6, 3.5))       # Manual -> D

    # 箭头：智能体 → 三级对齐（每个智能体右侧到对齐框左侧）
    for ay, h in [(10.6, 1.7), (8.5, 1.7), (5.5, 2.0), (2.7, 2.0)]:
        arrow(ax, (10, ay + h / 2), (12.4, 9.7), curve=0.05)

    # 箭头：对齐 → Verify → DAG → Neo4j
    arrow(ax, (14.7, 8.5), (14.7, 7.1))
    arrow(ax, (14.7, 5.4), (14.7, 4.2))
    arrow(ax, (17.0, 6.2), (18.5, 6.8))

    plt.tight_layout()
    out = FIG / "fig2_kg_pipeline.pdf"
    plt.savefig(out, bbox_inches="tight")
    plt.close()
    print(f"[OK] {out}")


# ─────────────────────────────────────────────────────────────────────
# Fig 3: 本体模式（7 类实体 / 9 类关系）
# ─────────────────────────────────────────────────────────────────────
def fig3_ontology():
    """三列泳道布局：BOM/CAD（左）、维修手册（中）、CAD几何（右）；
    7 个节点 + 7 条跨节点边，3 个自环关系单独在底部说明栏列出，避免视觉杂乱。"""
    fig, ax = plt.subplots(figsize=(13.5, 8.5))
    setup_ax(ax, (0, 23), (0, 14.5))

    # 三列泳道（背景色块）
    lanes = [
        (0.3,  1.0, 7.4, 12.5, "BOM / CAD：实体注册 + 装配骨架",     "#cfdef4"),
        (7.9,  1.0, 7.2, 12.5, "维修手册：过程性知识",                "#cfe5cf"),
        (15.3, 1.0, 7.4, 12.5, "CAD 几何：物理接口 + 数学约束",       "#f6e0c0"),
    ]
    for x, y, w, h, t, c in lanes:
        ax.add_patch(mp.Rectangle((x, y), w, h, facecolor=c, alpha=0.18,
                                  edgecolor=c, linewidth=0))
        ax.text(x + w / 2, y + h - 0.45, t, ha="center", va="top",
                fontsize=10.5, color="#3a3a3a", fontweight="bold")

    # 7 个实体节点（按列规整）
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

    # 跨节点边（每条边：起点、终点、标签文字、标签位置、curve）
    def draw_edge(p1, p2, lbl, label_xy, curve=0.0, color="#444"):
        arrow(ax, p1, p2, color=color, curve=curve, lw=1.4)
        if lbl:
            label(ax, label_xy, lbl, fontsize=9.5, color="#222", bg="#ffffff")

    # ── 同列垂直边
    draw_edge((4, 9.4),    (4, 7.1),     "isPartOf",       (4.9, 8.25))
    draw_edge((12, 9.4),   (12, 7.1),    "requires",       (12.9, 8.25))
    draw_edge((19, 9.4),   (19, 7.1),    "constrainedBy",  (20.0, 8.25))
    # Procedure → Specification（绕 Tool 左侧，rad=-0.30 向西外凸）
    draw_edge((10.6, 9.4), (10.6, 3.4),  "specifiedBy",    (8.8, 6.0), curve=-0.30)

    # ── 跨列水平 / 拱形 / 对角线
    draw_edge((5.6, 10.0), (10.4, 10.0), "participatesIn", (8.0, 10.5))
    # Part → Interface：自顶部拱形跨越 Procedure
    draw_edge((4, 10.6),   (19, 10.6),   "hasInterface",   (11.5, 12.5), curve=0.20)
    # Interface → Specification：右上 → 中下，直接对角
    draw_edge((17.5, 9.4), (13.5, 3.1),  "specifiedBy",    (15.6, 6.0))

    # ── 自连关系（底部说明栏）
    box(ax, (0.3, 0.05), 22.4, 0.65,
        "自连关系（同类节点）：matesWith / adjacentTo（Part — Part），"
        "precedes（Procedure — Procedure）；构建图谱时另含 SAME_AS / interchangesWith 跨阶段辅助关系",
        color="#fffbe6", edgecolor="#bd9c00", fontsize=9.5)

    plt.tight_layout()
    out = FIG / "fig3_ontology.pdf"
    plt.savefig(out, bbox_inches="tight")
    plt.close()
    print(f"[OK] {out}")


# ─────────────────────────────────────────────────────────────────────
# Fig 4: 三级级联实体对齐
# ─────────────────────────────────────────────────────────────────────
def fig4_entity_align():
    fig, ax = plt.subplots(figsize=(10, 6))
    setup_ax(ax, (0, 14), (0, 9))

    # 输入
    box(ax, (0.2, 7), 3.5, 1.2, "候选实体对\n(name_a, name_b)",
        color="#f0f0f0", edgecolor="#666", fontsize=10, fontweight="bold")

    # 三级级联（垂直）
    box(ax, (5, 7), 4, 1.2, "Level 1: 规则级\n航空领域缩写词典\n(HPC→高压压气机)",
        color="#dbe9f7", edgecolor="#2e6da4", fontsize=9.5)
    box(ax, (5, 4.5), 4, 1.2, "Level 2: 模糊级\nSequenceMatcher 编辑距离\n(阈值 0.85)",
        color="#fff3e0", edgecolor="#e08e0b", fontsize=9.5)
    box(ax, (5, 2), 4, 1.2, "Level 3: 语义级\nBGE-M3 向量余弦相似度\n(阈值 0.75)",
        color="#dff0d8", edgecolor="#3c763d", fontsize=9.5)

    # 输出
    box(ax, (10, 7), 3.6, 1.2, "对齐成功\n→ MERGE 同节点",
        color="#cfe9d8", edgecolor="#2e7d32", fontsize=10, fontweight="bold")
    box(ax, (10, 4.5), 3.6, 1.2, "对齐成功\n→ MERGE 同节点",
        color="#cfe9d8", edgecolor="#2e7d32", fontsize=10, fontweight="bold")
    box(ax, (10, 2), 3.6, 1.2, "对齐成功\n→ MERGE 同节点",
        color="#cfe9d8", edgecolor="#2e7d32", fontsize=10, fontweight="bold")

    # 失败 → 下一级
    box(ax, (5.5, 0.2), 3, 0.7, "未命中 → 创建新节点",
        color="#fde0e0", edgecolor="#a94442", fontsize=9)

    # 箭头
    arrow(ax, (3.7, 7.6), (5, 7.6))
    arrow(ax, (9, 7.6), (10, 7.6))
    arrow(ax, (9, 5.1), (10, 5.1))
    arrow(ax, (9, 2.6), (10, 2.6))
    # 失败下一级
    arrow(ax, (7, 7), (7, 5.7), color="#a94442", lw=1.0, style="-|>")
    arrow(ax, (7, 4.5), (7, 3.2), color="#a94442", lw=1.0, style="-|>")
    arrow(ax, (7, 2), (7, 0.9), color="#a94442", lw=1.0, style="-|>")

    # 失败标签
    label(ax, (7.6, 6.4), "未命中", fontsize=8, color="#a94442")
    label(ax, (7.6, 3.85), "未命中", fontsize=8, color="#a94442")
    label(ax, (7.6, 1.45), "未命中", fontsize=8, color="#a94442")

    plt.tight_layout()
    out = FIG / "fig4_entity_align.pdf"
    plt.savefig(out, bbox_inches="tight")
    plt.close()
    print(f"[OK] {out}")


# ─────────────────────────────────────────────────────────────────────
# Fig 5: 四路并行混合检索 + RRF
# ─────────────────────────────────────────────────────────────────────
def fig5_retrieval_rrf():
    fig, ax = plt.subplots(figsize=(13, 7))
    setup_ax(ax, (0, 26), (0, 14))

    # 顶部：用户查询 + 多查询扩展
    box(ax, (10.5, 12), 5, 1.4, "用户问题 q",
        color="#f0f0f0", edgecolor="#444", fontsize=11, fontweight="bold")
    box(ax, (9, 9.6), 8, 1.4, "多查询扩展（LLM）\nQ = {q, q1, q2}",
        color="#fef5d4", edgecolor="#d48b18", fontsize=10)
    arrow(ax, (13, 12), (13, 11), lw=1.5)

    # 四路并行
    paths = [
        (0.5, 6, "路径一：Dense\nBGE-M3 (1024D)\nQdrant text_vec", "#dbe9f7", "#2e6da4"),
        (7, 6, "路径二：BM25\njieba+regex 双轨分词\nrank_bm25 索引", "#fff3e0", "#e08e0b"),
        (13.5, 6, "路径三：CLIP\nChinese-CLIP (768D)\nQdrant image_vec", "#e8d3f0", "#7b4397"),
        (20, 6, "路径四：KG\nBGE-M3 ANN 锚点召回\n→ Neo4j 一跳子图扩展", "#dff0d8", "#3c763d"),
    ]
    for x, y, t, c, ec in paths:
        box(ax, (x, y), 5.5, 2.4, t, color=c, edgecolor=ec, fontsize=10)
        # 从多查询到每路
        arrow(ax, (13, 9.6), (x + 2.75, y + 2.4), lw=1.0, curve=0.05, color="#888")

    # 各路输出
    for x in [0.5, 7, 13.5, 20]:
        box(ax, (x + 0.7, 4), 4, 1, "Top-N 候选",
            color="#ffffff", edgecolor="#888", fontsize=9)
        arrow(ax, (x + 2.75, 6), (x + 2.75, 5))

    # RRF 融合
    box(ax, (8, 1.8), 10, 1.4,
        "互惠排名融合 RRF（k=60）\nRRF(d) = Σ 1 / (k + rank_r(d))",
        color="#cfe9d8", edgecolor="#2e7d32", fontsize=11, fontweight="bold")
    for x in [0.5, 7, 13.5, 20]:
        arrow(ax, (x + 2.75, 4), (13, 3.2), lw=0.8, curve=0.0, color="#888")

    # Reranker
    box(ax, (8, 0.0), 10, 1.2, "BGE-Reranker-Base 交叉编码器精排 → Top-K",
        color="#fef5d4", edgecolor="#d48b18", fontsize=10)
    arrow(ax, (13, 1.8), (13, 1.2))

    plt.tight_layout()
    out = FIG / "fig5_retrieval_rrf.pdf"
    plt.savefig(out, bbox_inches="tight")
    plt.close()
    print(f"[OK] {out}")


# ─────────────────────────────────────────────────────────────────────
# Fig 6: 文档解析与多模态向量化
# ─────────────────────────────────────────────────────────────────────
def fig6_indexing():
    fig, ax = plt.subplots(figsize=(13, 6))
    setup_ax(ax, (0, 26), (0, 12))

    # 输入
    box(ax, (0.5, 6.5), 3.5, 1.5, "原始文档\nPDF / MD / TXT",
        color="#f0f0f0", edgecolor="#444", fontsize=10, fontweight="bold")
    box(ax, (0.5, 3.5), 3.5, 1.5, "嵌入图片\n(*.png / *.jpg)",
        color="#f0f0f0", edgecolor="#444", fontsize=10, fontweight="bold")

    # 解析
    box(ax, (5, 7.0), 4.5, 2.2,
        "文档解析\n· PyMuPDF（可复制 PDF）\n· DeepDoc OCR（扫描件）\n· textin Markdown",
        color="#dbe9f7", edgecolor="#2e6da4", fontsize=9.5)
    box(ax, (5, 3.5), 4.5, 1.5,
        "图片提取\n过滤 < 100×100",
        color="#dbe9f7", edgecolor="#2e6da4", fontsize=9.5)

    # 切块 + caption
    box(ax, (10.5, 7.5), 4.5, 1.5,
        "句子边界切块\n（目标 500 字符）",
        color="#fff3e0", edgecolor="#e08e0b", fontsize=9.5)
    box(ax, (10.5, 4.5), 4.5, 2,
        "Vision LLM 生成\n中文技术描述\n(MiniMax M2.5 Vision)",
        color="#fff3e0", edgecolor="#e08e0b", fontsize=9.5)

    # 编码
    box(ax, (16, 8), 4.5, 1.5,
        "BGE-M3 编码\n→ text_vec (1024D)",
        color="#dff0d8", edgecolor="#3c763d", fontsize=9.5)
    box(ax, (16, 5.5), 4.5, 1.5,
        "BGE-M3 编码 caption\n→ text_vec (1024D)",
        color="#dff0d8", edgecolor="#3c763d", fontsize=9.5)
    box(ax, (16, 3.0), 4.5, 1.5,
        "Chinese-CLIP 编码\n→ image_vec (768D)",
        color="#e8d3f0", edgecolor="#7b4397", fontsize=9.5)

    # Qdrant
    box(ax, (21.5, 4.5), 4, 3.5,
        "Qdrant\n双向量集合\n\ntext_vec\nimage_vec",
        color="#cfe9d8", edgecolor="#2e7d32", fontsize=11, fontweight="bold")

    # 箭头
    arrow(ax, (4, 7.3), (5, 8.0))
    arrow(ax, (4, 4.2), (5, 4.2))
    arrow(ax, (9.5, 8), (10.5, 8.2))
    arrow(ax, (9.5, 4.2), (10.5, 5.5))
    arrow(ax, (15, 8.2), (16, 8.6))
    arrow(ax, (15, 5.5), (16, 6.2))
    arrow(ax, (15, 5.5), (16, 3.7))
    # 编码 → Qdrant：终点停在框左边界（不进入 box 内部，避免穿过文字）
    for sy in [8.75, 6.25, 3.75]:
        arrow(ax, (20.5, sy), (21.5, sy))

    plt.tight_layout()
    out = FIG / "fig6_indexing.pdf"
    plt.savefig(out, bbox_inches="tight")
    plt.close()
    print(f"[OK] {out}")


# ─────────────────────────────────────────────────────────────────────
# Fig 7: RAG 三阶段演进
# ─────────────────────────────────────────────────────────────────────
def fig7_rag_evolution():
    fig, ax = plt.subplots(figsize=(13, 5.5))
    setup_ax(ax, (0, 30), (0, 10))

    # 三个阶段
    stages = [
        (1, "Naive RAG", ["稠密向量检索\n(单路)", "Top-K 拼接", "LLM 生成"],
         "#fef5d4", "#d48b18"),
        (11, "Advanced RAG", ["多查询扩展", "稀疏-稠密混合", "Cross-Encoder 精排", "LLM 生成"],
         "#dbe9f7", "#2e6da4"),
        (21, "MHRAG（本文）", ["多查询扩展",
                                "四路并行检索\n(Dense+BM25+CLIP+KG ANN)",
                                "RRF 融合 + 精排",
                                "LLM 生成"],
         "#cfe9d8", "#2e7d32"),
    ]
    for sx, name, items, c, ec in stages:
        # 头部标题框
        box(ax, (sx, 8.0), 8, 1.0, name, color=c, edgecolor=ec,
            fontsize=12, fontweight="bold")
        # query 入口
        box(ax, (sx + 2, 6.8), 4, 0.7, "查询 q", color="#ffffff",
            edgecolor="#888", fontsize=9)
        arrow(ax, (sx + 4, 8.0), (sx + 4, 7.5), lw=1.0)

        # 流程项（垂直）
        item_h = 0.95
        gap = 0.25
        # 总高度
        total_h = len(items) * item_h + (len(items) - 1) * gap
        start_y = 6.5 - 0.3
        for i, t in enumerate(items):
            y = start_y - i * (item_h + gap)
            box(ax, (sx + 0.5, y - item_h), 7, item_h, t, color="#ffffff",
                edgecolor=ec, fontsize=9)
            if i > 0:
                arrow(ax, (sx + 4, y + gap), (sx + 4, y), lw=1.0)
            else:
                arrow(ax, (sx + 4, 6.8), (sx + 4, y), lw=1.0)

    # 演进箭头（横向）
    arrow(ax, (9.0, 4), (11, 4), color="#a94442", lw=2.5, mutation_scale=20)
    arrow(ax, (19, 4), (21, 4), color="#a94442", lw=2.5, mutation_scale=20)
    label(ax, (10, 4.7), "增强\n模块", fontsize=8.5, color="#a94442")
    label(ax, (20, 4.7), "结构化\n+ 多模态", fontsize=8.5, color="#a94442")

    plt.tight_layout()
    out = FIG / "fig7_rag_evolution.pdf"
    plt.savefig(out, bbox_inches="tight")
    plt.close()
    print(f"[OK] {out}")


def main():
    fig2_kg_pipeline()
    fig3_ontology()
    fig4_entity_align()
    fig5_retrieval_rrf()
    fig6_indexing()
    fig7_rag_evolution()
    print("\nAll method figures done.")


if __name__ == "__main__":
    main()
