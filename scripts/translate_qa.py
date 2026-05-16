"""
QA 双语化（task #10）：给 Tier-1 + Tier-2 每条 QA 添加 question_en + gold_answer_en

输入：
  tests/kg/fixtures/assembly_qa_tier1.jsonl
  tests/kg/fixtures/assembly_qa_tier2.jsonl

输出（覆盖原文件，添加新字段）：
  question_en / gold_answer_en

策略：
  - 批量翻译（每次 8 题）→ 80 题约 10 次 LLM 调用
  - 用 SiliconFlow（便宜）；MiniMax 备选
  - JSON schema 严格约束，失败时 fallback 单条调用

费用估算：80 题 × ~400 tokens 输入 + 200 tokens 输出 ≈ 50K tokens 总
  SiliconFlow Qwen2.5-14B: 约 ¥0.5
  MiniMax M2.5: 约 ¥3
"""
import json
import os
import sys
import time
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# 加载 .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from openai import OpenAI

T1 = Path("tests/kg/fixtures/assembly_qa_tier1.jsonl")
T2 = Path("tests/kg/fixtures/assembly_qa_tier2.jsonl")
BATCH_SIZE = 8

API_KEY = os.getenv("LLM_API_KEY") or os.getenv("MINIMAX_API_KEY")
BASE_URL = os.getenv("LLM_BASE_URL") or os.getenv("MINIMAX_BASE_URL")
MODEL = os.getenv("LLM_MODEL") or os.getenv("MINIMAX_MODEL")

if not (API_KEY and BASE_URL and MODEL):
    print("ERROR: 缺少 LLM_API_KEY / LLM_BASE_URL / LLM_MODEL 环境变量")
    sys.exit(1)

print(f"Using LLM: {MODEL} @ {BASE_URL}", flush=True)
client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

SYSTEM = """You are a professional translator specialized in aviation engine maintenance manuals.
Translate Chinese aviation assembly QA pairs into English.
Rules:
  - Keep technical terms in their original English form (part numbers, ATA sections like '72-30-05', model codes like 'PT6A').
  - Use professional aviation terminology (e.g. "压气机" → "compressor", "燃气发生器" → "gas generator").
  - Output STRICT JSON only, no preamble or explanation.
  - Preserve the order and IDs exactly."""


def translate_batch(items: list) -> list | None:
    """
    items: [{"id": ..., "question": ..., "answer": ...}, ...]
    return: [{"id": ..., "question_en": ..., "answer_en": ...}, ...] 或 None
    """
    user_prompt = (
        "Translate the following QA pairs from Chinese to English. "
        "Output ONLY a JSON array (no markdown fence) with the same length and IDs.\n\n"
        f"INPUT:\n{json.dumps(items, ensure_ascii=False, indent=2)}\n\n"
        'EXPECTED OUTPUT FORMAT:\n[{"id":"X","question_en":"...","answer_en":"..."}]'
    )
    for attempt in range(3):
        try:
            resp = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.1,
                max_tokens=4000,
                timeout=90,
            )
            content = resp.choices[0].message.content.strip()
            # 去掉可能的 markdown fence
            if content.startswith("```"):
                content = content.strip("`")
                if content.startswith(("json\n", "json\r")):
                    content = content[5:]
            data = json.loads(content)
            if isinstance(data, list) and len(data) == len(items):
                return data
            print(f"  ⚠ batch length mismatch: got {len(data) if isinstance(data, list) else 'non-list'} expected {len(items)}", flush=True)
        except json.JSONDecodeError as e:
            print(f"  ⚠ JSON parse error (attempt {attempt+1}): {e}", flush=True)
        except Exception as e:
            print(f"  ⚠ LLM call error (attempt {attempt+1}): {e}", flush=True)
            time.sleep(2)
    return None


def translate_qa_file(path: Path):
    qs = [json.loads(l) for l in open(path, encoding="utf-8")]
    print(f"\n=== {path.name} ({len(qs)} QAs) ===")
    # 过滤已翻译过的
    todo = [(i, q) for i, q in enumerate(qs) if not q.get("question_en")]
    print(f"  Need translation: {len(todo)} (skipping {len(qs) - len(todo)} already translated)")
    if not todo:
        return

    # 分批
    batches = []
    for start in range(0, len(todo), BATCH_SIZE):
        batches.append(todo[start:start + BATCH_SIZE])

    success = 0
    fail = 0
    for bi, batch in enumerate(batches, 1):
        items = [{"id": q["qa_id_global"], "question": q["question"], "answer": q["gold_answer"]}
                 for _, q in batch]
        print(f"  Batch {bi}/{len(batches)} ({len(batch)} items)...", flush=True)
        result = translate_batch(items)
        if result is None:
            print(f"  ✗ Batch {bi} failed (all 3 retries)", flush=True)
            fail += len(batch)
            continue
        # 写回
        result_by_id = {r.get("id"): r for r in result}
        for (orig_idx, q) in batch:
            r = result_by_id.get(q["qa_id_global"])
            if r:
                qs[orig_idx]["question_en"] = r.get("question_en", "")
                qs[orig_idx]["gold_answer_en"] = r.get("answer_en", "") or r.get("gold_answer_en", "")
                success += 1
            else:
                fail += 1
        # 增量保存（防中断丢失）
        with open(path, "w", encoding="utf-8") as f:
            for q in qs:
                f.write(json.dumps(q, ensure_ascii=False) + "\n")

    print(f"  → success {success} / fail {fail}")


def main():
    t0 = time.time()
    for path in [T1, T2]:
        if path.exists():
            translate_qa_file(path)
    print(f"\n[OK] Total elapsed: {(time.time() - t0):.1f}s")


if __name__ == "__main__":
    main()
