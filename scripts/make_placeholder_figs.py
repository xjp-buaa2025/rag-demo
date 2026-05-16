"""为论文生成图片占位符（Placeholder PDFs），含图标题与说明文字。
当真实图未绘制时，编译时使用占位符以保证论文可编译。

依赖：base conda Python（C:/Users/Administrator/Miniconda3/python.exe），
matplotlib 3.10+。
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import rcParams

rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "DejaVu Sans"]
rcParams["axes.unicode_minus"] = False
rcParams["pdf.fonttype"] = 42

ROOT = Path("C:/xjp/代码/rag-demo")
FIG = ROOT / "paper" / "figures"
FIG.mkdir(parents=True, exist_ok=True)

PLACEHOLDERS = [
    {
        "name": "fig2_kg_pipeline.pdf",
        "title": "图 3-2  多智能体协同知识抽取流水线",
        "caption": "占位符：四类智能体（BOM Parser / CAD Parser / Text Extractor /\n"
                   "Visual Extractor）并行处理，经三级实体对齐与 DAG 校验后\n"
                   "汇入 Neo4j。详细描述见 §3.2.2。",
        "figsize": (10, 5.5),
    },
    {
        "name": "fig3_ontology.pdf",
        "title": "图 3-3  知识图谱本体模式（7 类实体 / 9 类关系）",
        "caption": "占位符：节点 = Part / Assembly / Procedure / Tool /\n"
                   "Specification / Interface / GeoConstraint；\n"
                   "边 = isPartOf / precedes / participatesIn / requires /\n"
                   "specifiedBy / matesWith / adjacentTo / hasInterface /\n"
                   "constrainedBy。详细规范见表 3-1。",
        "figsize": (10, 6),
    },
    {
        "name": "fig4_entity_align.pdf",
        "title": "图 3-4  三级级联实体对齐与验证流程",
        "caption": "占位符：规则级（航空领域缩写词典）→ 模糊级（编辑距离）\n"
                   "→ 语义级（BGE-M3 余弦相似度）三级级联，\n"
                   "命中后由 Verification Agent 做一致性校验。",
        "figsize": (10, 5),
    },
    {
        "name": "fig5_retrieval_rrf.pdf",
        "title": "图 3-5  四路并行混合检索与 RRF 融合流程",
        "caption": "占位符：用户问题 → 多查询扩展 → 四路并行（Dense BGE-M3 /\n"
                   "BM25 / Chinese-CLIP / KG ANN）→ RRF 融合 → BGE-Reranker\n"
                   "精排 → 上下文 → LLM。详细公式见式 (3-7) 与 §3.4.6。",
        "figsize": (11, 5.5),
    },
    {
        "name": "fig6_indexing.pdf",
        "title": "图 3-6  文档解析与多模态双通道向量化索引构建流程",
        "caption": "占位符：PDF/MD → 双路解析（PyMuPDF + DeepDoc OCR）→\n"
                   "句子切块 + 图片提取 → BGE-M3 (text_vec 1024D) +\n"
                   "Chinese-CLIP (image_vec 768D) 双路编码 → Qdrant 双向量。",
        "figsize": (11, 5),
    },
    {
        "name": "fig7_rag_evolution.pdf",
        "title": "图 2-1  RAG 技术三阶段演进对比",
        "caption": "占位符：Naive RAG（稠密向量单路）→ Advanced RAG\n"
                   "（多查询扩展 + 稀疏-稠密混合 + 交叉编码器精排）→\n"
                   "GraphRAG（结构化推理 + 多跳遍历）。详细对比见 §2.1.1。",
        "figsize": (11, 4.5),
    },
]


def draw(spec: dict):
    fig, ax = plt.subplots(figsize=spec["figsize"])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    # 边框
    rect = plt.Rectangle((0.02, 0.02), 0.96, 0.96, fill=False,
                         edgecolor="#888", linewidth=1.5, linestyle="--")
    ax.add_patch(rect)
    # 标题
    ax.text(0.5, 0.78, spec["title"], ha="center", va="center",
            fontsize=18, fontweight="bold", color="#222")
    # PLACEHOLDER 大字
    ax.text(0.5, 0.55, "[ 图片占位符 / Placeholder ]", ha="center", va="center",
            fontsize=22, color="#c0392b", fontweight="bold")
    # 描述
    ax.text(0.5, 0.32, spec["caption"], ha="center", va="center",
            fontsize=12, color="#555", linespacing=1.6)
    # 底部说明
    ax.text(0.5, 0.10, "（待替换为真实示意图）", ha="center", va="center",
            fontsize=10, color="#888", style="italic")
    plt.tight_layout()
    out = FIG / spec["name"]
    plt.savefig(out, bbox_inches="tight")
    plt.close()
    print(f"[OK] {out}")


# fig1_architecture.pdf -> 直接用现有 mhrag_architecture.pdf
import shutil
src_arch = FIG / "mhrag_architecture.pdf"
dst_arch = FIG / "fig1_architecture.pdf"
if src_arch.exists() and not dst_arch.exists():
    shutil.copy(src_arch, dst_arch)
    print(f"[OK] {dst_arch} (copied from mhrag_architecture.pdf)")

for spec in PLACEHOLDERS:
    draw(spec)

print("\nAll placeholders generated.")
