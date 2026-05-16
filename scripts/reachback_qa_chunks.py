"""
QA gold_chunk_ids reachback（简化版）

为 assembly_qa_tier1.jsonl 每条 QA 自动召回 top-5 相关 chunks 作为候选 gold_chunk_ids。
召回路径：POST /retrieve（混合 Dense+BM25+RRF 已在后端封装）

用途：陛下 Day 3 勾选 QA 时可一并审"系统当前能否召回正确文档"。
最终评测时再人工选定 gold_chunk_ids。

字段写入格式：
  qa["gold_chunk_candidates"] = [
    {"source": "manual2.md", "page": 12, "score": 0.83, "preview": "首 80 字..."},
    ...
  ]
"""
import json
import sys
import time
from pathlib import Path

import requests

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

QA_FILE = Path("tests/kg/fixtures/assembly_qa_tier1.jsonl")
TOP_K = 5
BACKEND = "http://localhost:8000"


def retrieve(query: str, top_k: int = TOP_K) -> list:
    try:
        r = requests.post(
            f"{BACKEND}/retrieve",
            json={"query": query, "top_k": top_k, "use_rerank": True},
            timeout=30,
        )
        r.raise_for_status()
        return r.json().get("chunks", [])
    except Exception as e:
        return [{"_error": str(e)}]


def main():
    # 健康检查
    h = requests.get(f"{BACKEND}/health", timeout=5).json()
    n = h.get("collection_count", 0)
    if n == 0:
        print("ERROR: Qdrant 为空，请先入库。")
        sys.exit(1)
    print(f"Backend OK | {n} chunks in Qdrant\n")

    qs = [json.loads(l) for l in open(QA_FILE, encoding="utf-8")]
    print(f"Loaded {len(qs)} QA items from {QA_FILE}")

    t0 = time.time()
    for i, q in enumerate(qs, 1):
        # 用 question + 关键词联合检索
        kws = q.get("gold_answer_kw", [])
        if isinstance(kws, list) and kws:
            kw_str = " ".join([str(k) for k in kws if k])[:200]
            query = f"{q['question']} {kw_str}"
        else:
            query = q["question"]

        chunks = retrieve(query, top_k=TOP_K)
        cands = []
        for c in chunks:
            if "_error" in c:
                cands.append({"_error": c["_error"]})
                continue
            cands.append({
                "source": c.get("source", ""),
                "page": c.get("page", 0),
                "chunk_type": c.get("chunk_type", "text"),
                "score": round(c.get("rerank_score") or c.get("distance", 0), 4),
                "preview": (c.get("text") or "")[:120].replace("\n", " "),
            })
        q["gold_chunk_candidates"] = cands

        if i % 10 == 0:
            elapsed = time.time() - t0
            print(f"  [{i}/{len(qs)}] elapsed {elapsed:.1f}s")

    # 写回
    with open(QA_FILE, "w", encoding="utf-8") as f:
        for q in qs:
            f.write(json.dumps(q, ensure_ascii=False) + "\n")
    print(f"\n[OK] Updated {QA_FILE} with gold_chunk_candidates ({time.time()-t0:.1f}s)")
    # 简单统计：召回到 chunks 的 QA 占比
    has_cands = sum(1 for q in qs if q.get("gold_chunk_candidates") and not q["gold_chunk_candidates"][0].get("_error"))
    print(f"QA with non-empty candidates: {has_cands}/{len(qs)}")


if __name__ == "__main__":
    main()
