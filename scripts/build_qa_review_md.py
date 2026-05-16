"""
将 assembly_qa_tier1.jsonl + assembly_qa_tier2.jsonl 转换为 Markdown 评审文档。
陛下在 VSCode 直接打勾：✅ 通过 / ❌ 删除 / ✏️ 修改。

输出：tests/kg/fixtures/assembly_qa_review.md

使用流程：
  1. python scripts/build_qa_review_md.py   # 生成此 MD
  2. 陛下用 VSCode 打开 assembly_qa_review.md，逐题打勾 / 修改
  3. python scripts/parse_qa_review_md.py   # 解析回 jsonl 生成 final 版本
"""
import json
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

T1 = Path("tests/kg/fixtures/assembly_qa_tier1.jsonl")
T2 = Path("tests/kg/fixtures/assembly_qa_tier2.jsonl")
OUT = Path("tests/kg/fixtures/assembly_qa_review.md")


def fmt_qa_block(q: dict, idx: int, tier: int) -> str:
    """单题 markdown 块"""
    qid = q.get("qa_id_global", f"Q{idx:03d}")
    cat = q.get("category", "")
    sub = q.get("subtype", "")
    ata = q.get("source_ata", "")
    question = q.get("question", "").strip()
    answer = q.get("gold_answer", "").strip()
    kws = q.get("gold_answer_kw", [])
    kws_str = ", ".join([str(k)[:30] for k in kws if k])[:200]

    lines = [
        f"## {qid} `[{cat} / {sub}]`{f' ATA `{ata}`' if ata else ''}",
        "",
        f"**Q**: {question}",
        "",
        f"**A**: {answer}",
        "",
    ]
    if kws_str:
        lines += [f"**关键词**: {kws_str}", ""]

    # Tier-1 含 gold_chunk_candidates，展示前 3 个
    cands = q.get("gold_chunk_candidates", [])
    if cands and not cands[0].get("_error"):
        lines += ["<details><summary>📍 召回 Top-3 候选 chunks（参考用）</summary>", ""]
        for i, c in enumerate(cands[:3], 1):
            score = c.get("score", "?")
            src = (c.get("source", "?") or "")[:30]
            page = c.get("page", "?")
            preview = (c.get("preview", "") or "")[:120].replace("\n", " ")
            lines.append(f"  {i}. `score={score}` `src={src} p={page}`")
            lines.append(f"     > {preview}")
        lines += ["", "</details>", ""]

    # Tier-2 含 anchor_entity
    if tier == 2:
        anchor = q.get("anchor_entity", "")
        atype = q.get("anchor_type", "")
        lines += [f"**锚点实体**: `{anchor}`（{atype}）", ""]

    # 勾选区
    lines += [
        "**评审**（在方括号里打 x，三选一）：",
        "",
        "- [ ] ✅ **通过** — 问题表述清楚、答案与黄金集一致",
        "- [ ] ❌ **删除** — 问题不合理或答案错误（说明原因可加备注）",
        "- [ ] ✏️ **修改** — 在下方备注里写改后的版本",
        "",
        "**备注**（可选）：",
        "> ",
        "",
        "---",
        "",
    ]
    return "\n".join(lines)


def main():
    if not T1.exists() or not T2.exists():
        print(f"ERROR: 缺少输入文件 {T1} 或 {T2}")
        sys.exit(1)

    t1_qs = [json.loads(l) for l in open(T1, encoding="utf-8")]
    t2_qs = [json.loads(l) for l in open(T2, encoding="utf-8")]

    parts = [
        "# PT6A 装配 QA 评审清单",
        "",
        f"> 生成时间：自动生成 / 共 {len(t1_qs) + len(t2_qs)} 题（Tier-1 {len(t1_qs)} 精评 + Tier-2 {len(t2_qs)} 粗评）",
        "",
        "## 评审方法",
        "",
        "1. 每题三选一：`✅ 通过` / `❌ 删除` / `✏️ 修改`，在 `- [ ]` 方括号里填 `x`（如 `- [x] ✅`）",
        "2. 修改类需在「备注」里写新版问题/答案",
        "3. 召回候选 chunks 仅供参考——评审重点在「问题表达」与「答案是否与黄金集一致」",
        "",
        "## 进度",
        "",
        f"- Tier-1 精评（72-30 压气机）：0/{len(t1_qs)}",
        f"- Tier-2 粗评（跨章节）：0/{len(t2_qs)}",
        "",
        "---",
        "",
        f"# Tier-1（72-30 精评 / 60 题）",
        "",
    ]
    for i, q in enumerate(t1_qs, 1):
        parts.append(fmt_qa_block(q, i, tier=1))

    parts += [
        f"# Tier-2（跨章节粗评 / {len(t2_qs)} 题）",
        "",
    ]
    for i, q in enumerate(t2_qs, 1):
        parts.append(fmt_qa_block(q, i, tier=2))

    OUT.write_text("\n".join(parts), encoding="utf-8")
    print(f"[OK] {OUT} ({OUT.stat().st_size / 1024:.1f} KB, {len(t1_qs)+len(t2_qs)} QA blocks)")


if __name__ == "__main__":
    main()
