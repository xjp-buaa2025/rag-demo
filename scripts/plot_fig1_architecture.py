"""绘制论文图 1：MHRAG 系统总体架构（替代 drawio 导出版）。

输出：paper/figures/fig1_architecture.pdf
依赖：base conda Python（matplotlib 3.10）。
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "DejaVu Sans"]
rcParams["axes.unicode_minus"] = False
rcParams["pdf.fonttype"] = 42

ROOT = Path("C:/xjp/代码/rag-demo")
FIG = ROOT / "paper" / "figures"


def box(ax, xy, w, h, text, color, edgecolor, fontsize=10, fontweight="normal"):
    x, y = xy
    rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.10",
                          linewidth=1.2, facecolor=color, edgecolor=edgecolor)
    ax.add_patch(rect)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fontsize, fontweight=fontweight, color="#222")


def arrow(ax, p_from, p_to, color="#666", lw=1.3, curve=0.0, mutation_scale=12):
    arr = FancyArrowPatch(p_from, p_to,
                          connectionstyle=f"arc3,rad={curve}",
                          arrowstyle="->", color=color, linewidth=lw,
                          mutation_scale=mutation_scale)
    ax.add_patch(arr)


def panel(ax, xy, w, h, title, edgecolor):
    x, y = xy
    rect = Rectangle((x, y), w, h, linewidth=1.5, facecolor="#ffffff",
                     edgecolor=edgecolor, linestyle="--", alpha=0.8)
    ax.add_patch(rect)
    ax.text(x + w / 2, y + h - 0.45, title, ha="center", va="center",
            fontsize=12, fontweight="bold", color=edgecolor)


def main():
    fig, ax = plt.subplots(figsize=(15, 8))
    ax.set_xlim(0, 30)
    ax.set_ylim(0, 16)
    ax.set_aspect("equal")
    ax.axis("off")

    # ── 三大区块边框 ──
    panel(ax, (0.5, 1.5), 4.5, 13, "数据源", "#888888")
    panel(ax, (5.5, 1.5), 9.5, 13, "离线知识构建", "#2e6da4")
    panel(ax, (15.5, 1.5), 14.0, 13, "在线问答推理", "#d48b18")

    # ── 数据源 ──
    box(ax, (1.0, 10.5), 3.5, 1.8, "装配技术手册\n(PDF / MD)",
        "#f0f0f0", "#888", fontsize=10, fontweight="bold")
    box(ax, (1.0, 7.0), 3.5, 1.8, "BOM 物料清单\n(Excel / DOCX)",
        "#f0f0f0", "#888", fontsize=10, fontweight="bold")
    box(ax, (1.0, 3.5), 3.5, 1.8, "CAD 模型\n(STEP / IPC)",
        "#f0f0f0", "#888", fontsize=10, fontweight="bold")

    # ── 离线构建：双管道 ──
    # 文档向量管道
    ax.text(10.25, 12.5, "文档向量管道", fontsize=10, color="#2e6da4",
            ha="center", style="italic")
    box(ax, (5.8, 11.0), 2.6, 1.2, "文档解析\nPyMuPDF", "#dbe9f7", "#2e6da4", fontsize=9)
    box(ax, (8.6, 11.0), 2.4, 1.2, "语义切块\n500字符", "#dbe9f7", "#2e6da4", fontsize=9)
    box(ax, (11.2, 11.0), 2.4, 1.2, "BGE-M3\n向量化", "#dbe9f7", "#2e6da4", fontsize=9)
    box(ax, (13.8, 10.4), 1.0, 2.4, "Qdrant", "#3a7bd5", "#1a4fa0", fontsize=9, fontweight="bold")

    # 知识图谱管道
    ax.text(10.25, 8.7, "知识图谱管道", fontsize=10, color="#2e7d32",
            ha="center", style="italic")
    box(ax, (5.8, 7.0), 2.6, 1.2, "BOM/CAD/手册\n三源解析", "#dff0d8", "#2e7d32", fontsize=9)
    box(ax, (8.6, 7.0), 2.4, 1.2, "多智能体\n知识抽取", "#dff0d8", "#2e7d32", fontsize=9)
    box(ax, (11.2, 7.0), 2.4, 1.2, "三级实体\n对齐", "#dff0d8", "#2e7d32", fontsize=9)
    box(ax, (13.8, 6.4), 1.0, 2.4, "Neo4j", "#3aa55a", "#1f7a3a", fontsize=9, fontweight="bold")

    # 数据源 → 离线
    # 装配技术手册同时指向：文档向量管道 + 知识图谱管道（手册抽取智能体 C）
    arrow(ax, (4.5, 11.4), (5.8, 11.6))                         # 手册 → 文档向量管道
    arrow(ax, (4.5, 10.7), (5.8, 8.0), curve=-0.20)             # 手册 → KG 管道（手册三元组抽取）
    arrow(ax, (4.5, 7.9), (5.8, 7.6))                           # BOM → KG 管道
    arrow(ax, (4.5, 4.4), (5.8, 7.0), curve=0.2)                # CAD → KG 管道

    # 离线管道箭头
    for x_from, x_to in [(8.4, 8.6), (11.0, 11.2), (13.6, 13.8)]:
        arrow(ax, (x_from, 11.6), (x_to, 11.6))
        arrow(ax, (x_from, 7.6), (x_to, 7.6))

    # ── 在线推理 ──
    # 第一层：用户查询 → 多查询扩展
    box(ax, (16.0, 12.5), 2.6, 1.2, "用户查询 q",
        "#fef5d4", "#d48b18", fontsize=10, fontweight="bold")
    box(ax, (19.5, 12.5), 3.0, 1.2, "LLM\n多查询扩展", "#fef5d4", "#d48b18", fontsize=10)
    box(ax, (23.5, 12.5), 3.4, 1.2, "查询集 Q={q,q1,q2}", "#fef5d4", "#d48b18", fontsize=9)
    arrow(ax, (18.6, 13.1), (19.5, 13.1))
    arrow(ax, (22.5, 13.1), (23.5, 13.1))

    # 第二层：四路并行检索
    paths = [
        (16.3, 10.5, "①Dense  BGE-M3 → text_vec",  "#dbe9f7", "#2e6da4"),
        (16.3,  9.0, "②BM25  稀疏倒排索引",       "#dff0d8", "#2e7d32"),
        (16.3,  7.5, "③CLIP  Chinese-CLIP → image_vec", "#fff3e0", "#e08e0b"),
        (16.3,  6.0, "④KG  ANN 锚点召回 + Neo4j 一跳邻域", "#e8d3f0", "#7b4397"),
    ]
    for x, y, t, c, ec in paths:
        box(ax, (x, y), 8.5, 1.1, t, c, ec, fontsize=10)
        # 查询集到各路径
        arrow(ax, (25.2, 12.5), (x + 8.5, y + 1.1), curve=-0.1, color="#888")

    # 数据源指向
    arrow(ax, (14.8, 11.6), (16.3, 11.0), curve=-0.05)  # Qdrant → ①
    arrow(ax, (14.8, 11.6), (16.3,  8.05), curve=-0.15)  # Qdrant → ③ (image)
    arrow(ax, (14.8,  7.6), (16.3,  6.55), curve=-0.05)  # Neo4j → ④

    # 第三层：RRF
    box(ax, (25.5, 8.0), 3.5, 1.4,
        "RRF 融合\nRRF(d)=Σ 1/(k+rank)",
        "#f8d7da", "#a94442", fontsize=9, fontweight="bold")
    for y in [11.05, 9.55, 8.05, 6.55]:
        arrow(ax, (24.8, y), (25.5, 8.7), curve=-0.05, color="#888", lw=0.9)

    # 第四层：Reranker
    box(ax, (25.5, 5.8), 3.5, 1.4, "BGE-Reranker\n交叉编码器精排",
        "#fef5d4", "#d48b18", fontsize=9)
    arrow(ax, (27.25, 8.0), (27.25, 7.2))

    # 第五层：LLM
    box(ax, (25.5, 3.6), 3.5, 1.4, "LLM 生成\n(远端 vLLM)",
        "#cfe9d8", "#2e7d32", fontsize=9, fontweight="bold")
    arrow(ax, (27.25, 5.8), (27.25, 5.0))

    # 第六层：SSE 输出
    box(ax, (25.5, 2.0), 3.5, 1.0, "SSE 流式输出\n含来源图片 URL",
        "#dbe9f7", "#2e6da4", fontsize=9)
    arrow(ax, (27.25, 3.6), (27.25, 3.0))

    plt.tight_layout()
    out = FIG / "fig1_architecture.pdf"
    plt.savefig(out, bbox_inches="tight")
    plt.close()
    print(f"[OK] {out}")


if __name__ == "__main__":
    main()
