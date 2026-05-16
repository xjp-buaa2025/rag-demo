"""
解析陛下勾选过的 assembly_qa_review.md，生成最终评测集：
  - tests/kg/fixtures/assembly_qa_final.jsonl  （只含 ✅ 通过 + ✏️ 修改后版本）
  - 删除条目记录到 tests/kg/fixtures/assembly_qa_dropped.jsonl

支持的勾选格式：
  - [x] ✅ 通过
  - [x] ❌ 删除
  - [x] ✏️ 修改   （随后 "**备注**" 段落里的内容会替换问题/答案）

备注约定（修改类）：
  > 问题: <新问题>
  > 答案: <新答案>
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

REVIEW_MD = Path("tests/kg/fixtures/assembly_qa_review.md")
T1 = Path("tests/kg/fixtures/assembly_qa_tier1.jsonl")
T2 = Path("tests/kg/fixtures/assembly_qa_tier2.jsonl")
FINAL = Path("tests/kg/fixtures/assembly_qa_final.jsonl")
DROPPED = Path("tests/kg/fixtures/assembly_qa_dropped.jsonl")

# 区块分隔规则：## Q001 ... ---
BLOCK_PAT = re.compile(r"^## (Q\d+|T2_\d+)\s+`\[", re.MULTILINE)
CHECK_PAT = re.compile(r"^- \[(x|X| )\]\s+(✅|❌|✏️)", re.MULTILINE)
NOTE_QUESTION = re.compile(r"^>\s*问题[:：]\s*(.+)$", re.MULTILINE)
NOTE_ANSWER = re.compile(r"^>\s*答案[:：]\s*(.+)$", re.MULTILINE)


def load_originals():
    qs = {}
    for f in [T1, T2]:
        if not f.exists():
            continue
        for line in open(f, encoding="utf-8"):
            q = json.loads(line)
            qs[q["qa_id_global"]] = q
    return qs


def extract_blocks(md: str):
    """从 markdown 切分出每题块，返回 [(qid, block_text), ...]"""
    blocks = []
    matches = list(BLOCK_PAT.finditer(md))
    for i, m in enumerate(matches):
        qid = m.group(1)
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(md)
        blocks.append((qid, md[start:end]))
    return blocks


def parse_block(block: str) -> dict:
    """从单题 block 解析勾选 + 备注"""
    decision = "未评"  # 默认未评
    for m in CHECK_PAT.finditer(block):
        marked = m.group(1).strip().lower() == "x"
        symbol = m.group(2)
        if marked:
            decision = {"✅": "approve", "❌": "drop", "✏️": "edit"}.get(symbol, "未评")
            break

    note_q = NOTE_QUESTION.search(block)
    note_a = NOTE_ANSWER.search(block)
    return {
        "decision": decision,
        "edited_question": note_q.group(1).strip() if note_q else None,
        "edited_answer": note_a.group(1).strip() if note_a else None,
    }


def main():
    if not REVIEW_MD.exists():
        print(f"ERROR: 评审文件不存在：{REVIEW_MD}")
        print("请先运行：python scripts/build_qa_review_md.py")
        sys.exit(1)

    md = REVIEW_MD.read_text(encoding="utf-8")
    originals = load_originals()
    blocks = extract_blocks(md)

    if not blocks:
        print("ERROR: 未找到题目块（## Q001 ...），请检查 markdown 格式")
        sys.exit(1)

    print(f"Loaded {len(originals)} original QAs")
    print(f"Found {len(blocks)} blocks in review markdown")

    final = []
    dropped = []
    decisions = Counter()

    for qid, block in blocks:
        orig = originals.get(qid)
        if not orig:
            print(f"  ⚠ {qid} 在原始 jsonl 中未找到，跳过")
            continue
        review = parse_block(block)
        decisions[review["decision"]] += 1

        if review["decision"] == "drop":
            dropped.append({**orig, "drop_reason": "human review"})
        elif review["decision"] == "edit":
            new_q = {
                **orig,
                "question": review["edited_question"] or orig["question"],
                "gold_answer": review["edited_answer"] or orig["gold_answer"],
                "human_edited": True,
            }
            final.append(new_q)
        elif review["decision"] == "approve":
            final.append({**orig, "human_approved": True})
        else:  # 未评
            final.append({**orig, "human_unreviewed": True})

    print(f"\nDecisions:")
    for k, v in decisions.most_common():
        print(f"  {k}: {v}")

    FINAL.parent.mkdir(parents=True, exist_ok=True)
    with open(FINAL, "w", encoding="utf-8") as f:
        for q in final:
            f.write(json.dumps(q, ensure_ascii=False) + "\n")
    with open(DROPPED, "w", encoding="utf-8") as f:
        for q in dropped:
            f.write(json.dumps(q, ensure_ascii=False) + "\n")

    print(f"\n[OK] Final: {FINAL} ({len(final)} 题)")
    print(f"[OK] Dropped: {DROPPED} ({len(dropped)} 题)")


if __name__ == "__main__":
    main()
