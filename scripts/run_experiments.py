"""
PT6A 主实验脚本（task #12，论文 §4 数字生成器）

支持 6 基线 × 80 QA 的端到端评测：
  B1 Naive RAG (Dense-only) | B2 BM25-only | B3 Hybrid (Dense+BM25 RRF)
  B4 +CLIP | B5 +KG | B6 MHRAG (full)
  A1 = B6 - Rerank（消融附加）

阶段（可独立运行，resumable）：
  --stage retrieval   只跑检索，输出 retrieved chunks
  --stage generation  用检索结果 + LLM 生成答案
  --stage eval        计算所有指标
  --stage all         一气呵成

输出：
  docs/experiments/raw/{baseline}/qa_{qid}.json   每条 QA 一文件（中断可恢复）
  docs/experiments/table2_main.csv                Tier-1 主对比
  docs/experiments/table3_ablation.csv            消融
  docs/experiments/table5_tier2.csv               跨章节粗评

费用估算（80 QA × 6 基线）：
  - 检索：本地 GPU 推理，无 API 成本，~30 min
  - 生成：480 LLM 调用 × ~3000 tokens ≈ 1.5M tokens ≈ ¥3-10
  - LLM-Judge：480 调用，同上 ≈ ¥3-10
  - 总计 ¥6-20 / 1-2 h
"""
import argparse
import json
import math
import os
import re
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Optional

import requests

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from openai import OpenAI

BACKEND = "http://localhost:8000"
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
QA_FINAL = _PROJECT_ROOT / "tests" / "kg" / "fixtures" / "assembly_qa_final.jsonl"
OUT_DIR = _PROJECT_ROOT / "docs" / "experiments"
RAW_DIR = OUT_DIR / "raw"
TABLE_DIR = OUT_DIR

# ─────────────────────────────────────────────────────────────────────────────
# 6 基线 + 1 消融附加 配置
# ─────────────────────────────────────────────────────────────────────────────
BASELINES = {
    "B1_dense":    {"paths": ["dense"],                        "use_rerank": False, "label": "Naive RAG (Dense-only)"},
    "B2_bm25":     {"paths": ["bm25"],                         "use_rerank": False, "label": "BM25-only"},
    "B3_hybrid":   {"paths": ["dense", "bm25"],                "use_rerank": True,  "label": "Hybrid (Dense+BM25 RRF)"},
    "B4_clip":     {"paths": ["dense", "bm25", "clip"],        "use_rerank": True,  "label": "+CLIP"},
    "B5_kg":       {"paths": ["dense", "bm25", "kg"],          "use_rerank": True,  "label": "+KG"},
    "B6_full":     {"paths": ["dense", "bm25", "clip", "kg"],  "use_rerank": True,  "label": "MHRAG (full)"},
    "A1_no_rerank":{"paths": ["dense", "bm25", "clip", "kg"],  "use_rerank": False, "label": "B6 -Rerank"},
}

TOP_K = 5
RECALL_N = 20

# ─────────────────────────────────────────────────────────────────────────────
# LLM client（用于 generation + judge）
# ─────────────────────────────────────────────────────────────────────────────
LLM_API_KEY = os.getenv("LLM_API_KEY") or os.getenv("MINIMAX_API_KEY")
LLM_BASE_URL = os.getenv("LLM_BASE_URL") or os.getenv("MINIMAX_BASE_URL")
LLM_MODEL = os.getenv("LLM_MODEL") or os.getenv("MINIMAX_MODEL")
_llm_client = None


def get_llm():
    global _llm_client
    if _llm_client is None:
        _llm_client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)
    return _llm_client


def llm_call(messages: list, temperature: float = 0.2, max_tokens: int = 800) -> str:
    """统一 LLM 调用，3 次重试，返回文本。"""
    for attempt in range(3):
        try:
            resp = get_llm().chat.completions.create(
                model=LLM_MODEL,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=60,
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            if attempt == 2:
                print(f"  ⚠ LLM 3 次重试失败：{e}", flush=True)
                return ""
            time.sleep(2 + attempt)
    return ""


# ─────────────────────────────────────────────────────────────────────────────
# Stage 1: 检索
# ─────────────────────────────────────────────────────────────────────────────
def retrieve_for_baseline(query: str, baseline_cfg: dict) -> list:
    body = {
        "query": query,
        "top_k": TOP_K,
        "paths": baseline_cfg["paths"],
        "use_rerank": baseline_cfg["use_rerank"],
        "recall_n": RECALL_N,
    }
    try:
        r = requests.post(f"{BACKEND}/retrieve_ablation", json=body, timeout=60)
        r.raise_for_status()
        return r.json().get("chunks", [])
    except Exception as e:
        print(f"  retrieve err: {e}", flush=True)
        return []


def stage_retrieval(qa_list: list, baseline_id: str) -> int:
    """对所有 QA 跑检索，按 baseline 输出。Resumable：跳过已存在文件。"""
    cfg = BASELINES[baseline_id]
    out_dir = RAW_DIR / baseline_id
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n=== Stage RETRIEVAL [{baseline_id}] paths={cfg['paths']} rerank={cfg['use_rerank']} ===")
    t0 = time.time()
    skipped = 0
    n = 0
    for qa in qa_list:
        qid = qa["qa_id_global"]
        out_file = out_dir / f"qa_{qid}.json"
        if out_file.exists():
            try:
                existing = json.load(open(out_file, encoding="utf-8"))
                if existing.get("retrieved_chunks") is not None:
                    skipped += 1
                    continue
            except Exception:
                pass

        # 双语 query：中 + 英
        zh = qa.get("question", "")
        en = qa.get("question_en", "")
        query = (zh + " " + en).strip()[:500]
        chunks = retrieve_for_baseline(query, cfg)

        record = {
            "qa_id": qid,
            "tier": qa.get("tier"),
            "category": qa.get("category"),
            "subtype": qa.get("subtype"),
            "question": zh,
            "question_en": en,
            "gold_answer": qa.get("gold_answer", ""),
            "gold_answer_en": qa.get("gold_answer_en", ""),
            "gold_answer_kw": qa.get("gold_answer_kw", []),
            "gold_chunk_candidates": qa.get("gold_chunk_candidates", []),
            "source_ata": qa.get("source_ata", ""),
            "baseline": baseline_id,
            "baseline_label": cfg["label"],
            "paths": cfg["paths"],
            "use_rerank": cfg["use_rerank"],
            "retrieved_chunks": chunks,
            "retrieved_at": time.time(),
        }
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(record, f, ensure_ascii=False, indent=2)
        n += 1
        if n % 10 == 0:
            print(f"  [{baseline_id}] {n} new + {skipped} skip / {len(qa_list)} | elapsed {(time.time()-t0):.0f}s", flush=True)

    print(f"=== {baseline_id} retrieval done: {n} new + {skipped} skip / total {len(qa_list)} | {(time.time()-t0)/60:.1f} min ===")
    return n


# ─────────────────────────────────────────────────────────────────────────────
# Stage 2: 生成
# ─────────────────────────────────────────────────────────────────────────────
GENERATION_PROMPT = """你是 PT6A 航空发动机装配专家。基于下方提供的参考资料回答用户问题。

要求：
1. 严格基于参考资料，不要凭空编造
2. 答案要直接、简洁、有事实依据
3. 若参考资料中无相关信息，明确说"参考资料中未找到相关信息"
4. 用中文回答（除非问题是英文）

【参考资料】
{context}

【问题】
{question}

【答案】"""


def build_context(chunks: list, max_chars: int = 4000) -> str:
    parts = []
    used = 0
    for i, c in enumerate(chunks, 1):
        text = (c.get("text") or "").strip()
        src = c.get("source", "?")
        page = c.get("page", "")
        ctype = c.get("chunk_type", "text")
        head = f"[资料{i} | {src} p{page} | {ctype}]"
        block = f"{head}\n{text}\n"
        if used + len(block) > max_chars:
            break
        parts.append(block)
        used += len(block)
    return "\n".join(parts) if parts else "（无相关资料）"


def stage_generation(qa_list: list, baseline_id: str) -> int:
    out_dir = RAW_DIR / baseline_id
    print(f"\n=== Stage GENERATION [{baseline_id}] ===")
    t0 = time.time()
    n = 0
    skipped = 0
    for qa in qa_list:
        qid = qa["qa_id_global"]
        f = out_dir / f"qa_{qid}.json"
        if not f.exists():
            print(f"  ⚠ {qid} 检索结果未生成，跳过")
            continue
        rec = json.load(open(f, encoding="utf-8"))
        if rec.get("generated_answer"):
            skipped += 1
            continue

        chunks = rec.get("retrieved_chunks") or []
        ctx = build_context(chunks, max_chars=4000)
        prompt = GENERATION_PROMPT.format(context=ctx, question=rec["question"])
        ans = llm_call([{"role": "user", "content": prompt}], temperature=0.2, max_tokens=600)
        rec["generated_answer"] = ans
        rec["generated_at"] = time.time()
        with open(f, "w", encoding="utf-8") as fp:
            json.dump(rec, fp, ensure_ascii=False, indent=2)
        n += 1
        if n % 5 == 0:
            print(f"  [{baseline_id}] {n} gen + {skipped} skip / {len(qa_list)} | elapsed {(time.time()-t0):.0f}s", flush=True)

    print(f"=== {baseline_id} generation done: {n} new + {skipped} skip | {(time.time()-t0)/60:.1f} min ===")
    return n


# ─────────────────────────────────────────────────────────────────────────────
# Stage 3: 评估
# ─────────────────────────────────────────────────────────────────────────────
JUDGE_PROMPT = """你是 RAG 答案评估专家。请对以下答案打分。

【问题】{question}

【参考标准答案】{gold_answer}

【系统答案】{generated_answer}

请从三个维度打 0-5 分（整数），并简要给出依据：
1. relevance（相关性）：答案与问题相关程度
2. completeness（完整性）：答案是否覆盖了关键信息
3. correctness（正确性）：答案与标准答案一致程度

严格按 JSON 输出，不要 markdown 包裹：
{{"relevance": <int>, "completeness": <int>, "correctness": <int>, "reason": "<一句话>"}}"""


def llm_judge(question: str, gold: str, generated: str) -> dict:
    if not generated:
        return {"relevance": 0, "completeness": 0, "correctness": 0, "reason": "no answer"}
    prompt = JUDGE_PROMPT.format(question=question, gold_answer=gold[:600], generated_answer=generated[:1000])
    raw = llm_call([{"role": "user", "content": prompt}], temperature=0.1, max_tokens=300)
    if not raw:
        return {"relevance": 0, "completeness": 0, "correctness": 0, "reason": "judge call failed"}
    # 提取 JSON
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw)
    try:
        return json.loads(raw)
    except Exception:
        # 尝试找 JSON 子串
        m = re.search(r"\{[^{}]*\}", raw)
        if m:
            try:
                return json.loads(m.group(0))
            except Exception:
                pass
        return {"relevance": 0, "completeness": 0, "correctness": 0, "reason": "parse fail"}


# 全局黄金集实体 id→names 映射（懒加载）
_GOLDEN_ID_TO_NAMES = None


def _load_golden_id_to_names() -> dict:
    """从 golden_triples.json 建立 entity_id → set of names（zh+en+部分零件号）"""
    global _GOLDEN_ID_TO_NAMES
    if _GOLDEN_ID_TO_NAMES is not None:
        return _GOLDEN_ID_TO_NAMES
    p = _PROJECT_ROOT / "storage" / "kg_stages" / "golden_triples.json"
    out = {}
    try:
        d = json.load(open(p, encoding="utf-8"))
        for items in d.get("entities", {}).values():
            for e in items:
                eid = e.get("id", "")
                if not eid:
                    continue
                names = set()
                for k in ("name_zh", "name_en", "tool_id", "step_id"):
                    v = e.get(k, "")
                    if v:
                        names.add(str(v).strip())
                # part_number 可能是 list
                pn = e.get("part_number") or []
                if isinstance(pn, list):
                    for x in pn:
                        if x:
                            names.add(str(x).strip())
                elif pn:
                    names.add(str(pn).strip())
                out[eid] = names
    except Exception as e:
        print(f"[load_golden_id_to_names] err: {e}")
    _GOLDEN_ID_TO_NAMES = out
    return out


def _kg_chunk_match_gold_subgraph(chunk_text: str, gold_subgraph: dict) -> bool:
    """
    KG 子图块的命中判定：
      1. 从 chunk_text 提取 [KG entity: NAME (LABEL)] 的 NAME
      2. 把 gold_subgraph.nodes（如 ['P001', 'A002']）翻译成 names
      3. 任一交集即算命中
    """
    if not chunk_text or not gold_subgraph:
        return False
    nodes = gold_subgraph.get("nodes") or []
    if not nodes:
        return False

    # 提取 chunk 中的 KG 实体名（包含 head 与所有 tail）
    chunk_names = set()
    # head: [KG entity: NAME (LABEL)]
    m = re.search(r"\[KG entity:\s*(.+?)\s*\(", chunk_text)
    if m:
        chunk_names.add(m.group(1).strip())
    # tails: -[REL]→ NAME
    for m in re.finditer(r"-\[[^\]]+\][→\->]+\s*(.+?)(?:\n|$)", chunk_text):
        chunk_names.add(m.group(1).strip())
    if not chunk_names:
        return False

    # gold_subgraph nodes → 候选名字（中英文 + 部分零件号）
    id_map = _load_golden_id_to_names()
    gold_names = set()
    for nid in nodes:
        gold_names.update(id_map.get(nid, set()))
        # 也允许直接 ID 匹配（如已是名字）
        gold_names.add(nid)
    if not gold_names:
        return False

    # 任一 chunk 实体名与任一 gold 名字"包含"匹配（双向）
    for cn in chunk_names:
        cn_low = cn.lower()
        for gn in gold_names:
            if not gn:
                continue
            gn_low = str(gn).lower()
            if not gn_low or len(gn_low) < 2:
                continue
            # 双向部分匹配
            if cn_low == gn_low or gn_low in cn_low or cn_low in gn_low:
                return True
    return False


def chunk_id_match(retrieved: list, gold_candidates: list, gold_subgraph: dict | None = None) -> list:
    """
    每条 retrieved chunk 是否命中黄金集。
    - 文本/图像块：source + page 与 gold_chunk_candidates 比对
    - KG 子图块：实体名与 gold_subgraph.nodes 翻译成的名字比对
    """
    flags = []
    gold_keys = set()
    for g in (gold_candidates or []):
        if g.get("_error"):
            continue
        key = (g.get("source", ""), g.get("page", 0))
        gold_keys.add(key)

    for r in retrieved:
        ctype = r.get("chunk_type", "text")
        match = False
        if ctype == "kg_subgraph":
            # KG 子图：与 gold_subgraph 节点匹配
            match = _kg_chunk_match_gold_subgraph(r.get("text") or "", gold_subgraph or {})
        else:
            # 文本/图像：source+page 匹配
            rkey = (r.get("source", ""), r.get("page", 0))
            match = rkey in gold_keys
        flags.append(match)
    return flags


def compute_retrieval_metrics(retrieved: list, gold_candidates: list,
                              gold_subgraph: dict | None = None,
                              top_k: int = 5) -> dict:
    """Recall@K, MRR, Hit@1, Hit@K, NDCG@K（含 KG 子图 + 文本块的混合命中）"""
    if not retrieved:
        return {"recall@5": 0.0, "mrr": 0.0, "hit@1": 0, "hit@5": 0, "ndcg@5": 0.0}
    flags = chunk_id_match(retrieved[:top_k], gold_candidates, gold_subgraph)
    any_hit = any(flags)
    hit_1 = 1 if (flags and flags[0]) else 0
    hit_k = 1 if any_hit else 0
    mrr = 0.0
    for i, f in enumerate(flags):
        if f:
            mrr = 1.0 / (i + 1)
            break
    # Recall@K：分母 = gold_chunk + gold_subgraph_nodes 各算 1
    n_gold_text = len([g for g in (gold_candidates or []) if not g.get("_error")])
    n_gold_kg = 1 if (gold_subgraph and gold_subgraph.get("nodes")) else 0
    n_gold_total = max(n_gold_text + n_gold_kg, 1)
    n_relevant_in_top = sum(1 for f in flags if f)
    recall_k = min(n_relevant_in_top, n_gold_total) / n_gold_total
    dcg = sum(1.0 / math.log2(i + 2) for i, f in enumerate(flags) if f)
    idcg = sum(1.0 / math.log2(i + 2) for i in range(min(n_gold_total, top_k)))
    ndcg = dcg / idcg if idcg > 0 else 0.0
    return {
        "recall@5": round(recall_k, 4),
        "mrr": round(mrr, 4),
        "hit@1": hit_1,
        "hit@5": hit_k,
        "ndcg@5": round(ndcg, 4),
    }


def stage_eval(qa_list: list, baseline_id: str, force_retrieval: bool = False) -> int:
    """
    force_retrieval=True 时只重算检索指标（recall/mrr/hit/ndcg），保留已有 LLM-Judge 三维分。
    """
    out_dir = RAW_DIR / baseline_id
    print(f"\n=== Stage EVAL [{baseline_id}] {'(force_retrieval)' if force_retrieval else ''} ===")
    t0 = time.time()
    n = 0
    skipped = 0
    for qa in qa_list:
        qid = qa["qa_id_global"]
        f = out_dir / f"qa_{qid}.json"
        if not f.exists():
            continue
        rec = json.load(open(f, encoding="utf-8"))

        # qa_list 来自 final.jsonl，包含 gold_subgraph
        gold_subgraph = qa.get("gold_subgraph") or {}

        if rec.get("metrics") and not force_retrieval:
            skipped += 1
            continue

        chunks = rec.get("retrieved_chunks") or []
        gold_cands = rec.get("gold_chunk_candidates") or []
        retrieval_m = compute_retrieval_metrics(chunks, gold_cands,
                                                gold_subgraph=gold_subgraph, top_k=TOP_K)

        if force_retrieval and rec.get("metrics"):
            # 仅更新检索指标，复用 judge 字段
            old_m = rec["metrics"]
            rec["metrics"] = {
                **retrieval_m,
                "judge_relevance": old_m.get("judge_relevance", 0),
                "judge_completeness": old_m.get("judge_completeness", 0),
                "judge_correctness": old_m.get("judge_correctness", 0),
                "judge_reason": old_m.get("judge_reason", ""),
            }
        else:
            gen = rec.get("generated_answer", "")
            gold = rec.get("gold_answer", "")
            judge = llm_judge(rec["question"], gold, gen) if gen else {}
            rec["metrics"] = {
                **retrieval_m,
                "judge_relevance": judge.get("relevance", 0),
                "judge_completeness": judge.get("completeness", 0),
                "judge_correctness": judge.get("correctness", 0),
                "judge_reason": judge.get("reason", ""),
            }

        rec["evaluated_at"] = time.time()
        with open(f, "w", encoding="utf-8") as fp:
            json.dump(rec, fp, ensure_ascii=False, indent=2)
        n += 1
        if n % 20 == 0:
            print(f"  [{baseline_id}] {n} eval + {skipped} skip | elapsed {(time.time()-t0):.0f}s", flush=True)

    print(f"=== {baseline_id} eval done: {n} new + {skipped} skip | {(time.time()-t0)/60:.1f} min ===")
    return n


# ─────────────────────────────────────────────────────────────────────────────
# Stage 4: 汇总表格
# ─────────────────────────────────────────────────────────────────────────────
def aggregate_baseline(baseline_id: str, tier: int = None) -> dict:
    out_dir = RAW_DIR / baseline_id
    if not out_dir.exists():
        return {}
    keys = ["recall@5", "mrr", "hit@1", "hit@5", "ndcg@5",
            "judge_relevance", "judge_completeness", "judge_correctness"]
    sums = defaultdict(float)
    n = 0
    for f in out_dir.glob("qa_*.json"):
        rec = json.load(open(f, encoding="utf-8"))
        if tier is not None and rec.get("tier") != tier:
            continue
        m = rec.get("metrics") or {}
        if not m:
            continue
        for k in keys:
            v = m.get(k, 0)
            sums[k] += float(v) if isinstance(v, (int, float)) else 0
        n += 1
    if n == 0:
        return {}
    return {"baseline": baseline_id, "n_qa": n, **{k: round(sums[k] / n, 4) for k in keys}}


def stage_aggregate(qa_list: list, baselines: list):
    print("\n=== Stage AGGREGATE → CSV ===")
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Tier-1 主表（所有 baselines）
    rows_t1 = [aggregate_baseline(b, tier=1) for b in baselines]
    rows_t1 = [r for r in rows_t1 if r]
    csv_t1 = TABLE_DIR / "table2_main_tier1.csv"
    write_csv(csv_t1, rows_t1)
    print(f"[OK] {csv_t1}")

    # Tier-2 跨章节
    rows_t2 = [aggregate_baseline(b, tier=2) for b in baselines]
    rows_t2 = [r for r in rows_t2 if r]
    csv_t2 = TABLE_DIR / "table5_tier2.csv"
    write_csv(csv_t2, rows_t2)
    print(f"[OK] {csv_t2}")

    # 控制台美化打印
    print("\n=== Tier-1 主表（80→Tier-1 60题）===")
    print_table(rows_t1)
    print("\n=== Tier-2 跨章节（20题）===")
    print_table(rows_t2)


def write_csv(path: Path, rows: list):
    if not rows:
        path.write_text("(no data)", encoding="utf-8")
        return
    keys = list(rows[0].keys())
    lines = [",".join(keys)]
    for r in rows:
        lines.append(",".join(str(r.get(k, "")) for k in keys))
    path.write_text("\n".join(lines), encoding="utf-8-sig")


def print_table(rows: list):
    if not rows:
        print("(empty)")
        return
    keys = ["baseline", "n_qa", "recall@5", "mrr", "hit@1", "hit@5",
            "judge_relevance", "judge_completeness", "judge_correctness"]
    print(" | ".join(f"{k:<22}" for k in keys))
    for r in rows:
        print(" | ".join(f"{str(r.get(k, '-')):<22}" for k in keys))


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["retrieval", "generation", "eval", "aggregate", "all"], default="all")
    ap.add_argument("--baseline", default=None, help="跑单个 baseline（默认全跑）")
    ap.add_argument("--limit", type=int, default=None, help="限制 QA 数量（smoke test）")
    ap.add_argument("--force-eval-retrieval", action="store_true",
                    help="只重算检索指标（recall/mrr/hit/ndcg），保留已有 LLM-Judge")
    args = ap.parse_args()

    if not QA_FINAL.exists():
        print(f"ERROR: {QA_FINAL} 不存在")
        sys.exit(1)
    qa_list = [json.loads(l) for l in open(QA_FINAL, encoding="utf-8")]
    if args.limit:
        qa_list = qa_list[:args.limit]
    print(f"Loaded {len(qa_list)} QAs (Tier-1: {sum(1 for q in qa_list if q.get('tier')==1)}, Tier-2: {sum(1 for q in qa_list if q.get('tier')==2)})")

    baselines = [args.baseline] if args.baseline else list(BASELINES.keys())
    print(f"Baselines: {baselines}")

    # 健康检查
    try:
        h = requests.get(f"{BACKEND}/health", timeout=5).json()
        print(f"Backend: {h.get('collection_count')} chunks | {h.get('model')}")
    except Exception as e:
        print(f"⚠ Backend 不可达：{e}")
        sys.exit(1)

    grand_t0 = time.time()
    for b in baselines:
        if args.stage in ("retrieval", "all"):
            stage_retrieval(qa_list, b)
        if args.stage in ("generation", "all"):
            stage_generation(qa_list, b)
        if args.stage in ("eval", "all"):
            stage_eval(qa_list, b, force_retrieval=args.force_eval_retrieval)

    if args.stage in ("aggregate", "all"):
        stage_aggregate(qa_list, baselines)

    print(f"\n[ALL DONE] total elapsed: {(time.time()-grand_t0)/60:.1f} min")


if __name__ == "__main__":
    main()
