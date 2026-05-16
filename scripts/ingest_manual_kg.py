"""
Manual KG 提取（stage2/manual 路径），方案 A 替代 ingest_pipeline 失败的 KG 部分

背景：
  ingest_pt6a.py 的 /ingest/pipeline 路径在 manual1 KG 阶段因 MiniMax 余额耗尽而失败，
  Neo4j 仅保留 BOM 节点（2985）+ 0 边。改走受控的 stage2/manual 端点重新提取。

策略：
  串行跑 3 个 manual 文件 → 每跑一次，读 stage2_manual_triples.json 暂存 triples → 备份
  最后合并三份 triples 一次性写回 stage2_manual_triples.json + 写 Neo4j

费用：单文件 ~1000 chunks × 单 LLM 调用，三个总 ~3000 调用
预计：MiniMax 主线 60-90 min；fallback 慢 2-3x

用法：
  python scripts/ingest_manual_kg.py            # 全跑
  python scripts/ingest_manual_kg.py --only manual2.md  # 单文件
  python scripts/ingest_manual_kg.py --skip manual1_body.md  # 跳过指定文件
"""
import argparse
import json
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

BACKEND = "http://localhost:8000"
PT6A_DIR = Path("data/KG/PT6A")
STAGE_FILE = Path("storage/kg_stages/stage2_manual_triples.json")
BACKUP_DIR = Path("storage/kg_stages")
MANUALS = ["manual1_body.md", "manual2.md", "manual3.md"]


def log(msg: str, level: str = "INFO"):
    print(f"[{time.strftime('%H:%M:%S')}] [{level}] {msg}", flush=True)


def consume_sse(url: str, files: dict, label: str, max_seconds: int = 10800) -> tuple:
    """消费 SSE，返回 (elapsed_sec, done_seen, last_result_dict)"""
    t0 = time.time()
    last_log = ""
    done_seen = False
    last_result = None
    try:
        with requests.post(url, files=files, stream=True, timeout=(30, max_seconds)) as r:
            r.raise_for_status()
            for raw in r.iter_lines(decode_unicode=True):
                if not raw or not raw.startswith("data: "):
                    continue
                payload = raw[6:].strip()
                if payload == "[DONE]":
                    done_seen = True
                    break
                try:
                    obj = json.loads(payload)
                except Exception:
                    continue
                if "message" in obj and obj.get("type") == "log":
                    line = obj["message"]
                    if line and line != last_log:
                        elapsed = int(time.time() - t0)
                        print(f"    [{label} +{elapsed:5d}s] {line[:180]}", flush=True)
                        last_log = line
                elif obj.get("type") == "result":
                    last_result = obj
                    elapsed = int(time.time() - t0)
                    print(f"    [{label} +{elapsed:5d}s] >> result: {obj.get('triples_count', '?')} triples / {obj.get('entities_count', '?')} entities", flush=True)
                elif obj.get("type") == "done":
                    done_seen = True
                elif obj.get("type") == "error":
                    print(f"    [{label}] ERROR: {obj.get('message', '?')}", flush=True)
    except requests.exceptions.ChunkedEncodingError as e:
        log(f"{label} ChunkedEncodingError（后端可能已结束）：{e}", "WARN")
    except Exception as e:
        log(f"{label} SSE 异常：{e}", "ERROR")
    return time.time() - t0, done_seen, last_result


def health_check() -> dict:
    return requests.get(f"{BACKEND}/health", timeout=5).json()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=None, help="只跑指定文件名")
    ap.add_argument("--skip", action="append", default=[], help="跳过指定文件")
    args = ap.parse_args()

    log("=" * 70)
    log("PT6A Manual KG 提取（stage2/manual 路径）")
    log("=" * 70)

    h = health_check()
    log(f"Backend: {h.get('collection_count', 0)} chunks | {h.get('model', '?')}")

    targets = MANUALS if not args.only else [args.only]
    targets = [m for m in targets if m not in args.skip]
    log(f"Targets: {targets}")

    all_triples = []
    sources = []
    summaries = []
    total_t0 = time.time()

    for fn in targets:
        path = PT6A_DIR / fn
        if not path.exists():
            log(f"{path} not found, skip", "ERROR")
            continue
        size_kb = path.stat().st_size / 1024
        log(f"\n>>> {fn} ({size_kb:.0f} KB) → /kg/stage2/manual")
        with open(path, "rb") as f:
            files = {"file": (path.name, f, "text/markdown")}
            elapsed, done, result = consume_sse(f"{BACKEND}/kg/stage2/manual", files=files, label=path.stem)

        log(f"<<< {fn} elapsed {elapsed/60:.1f} min | done_seen={done}")

        if STAGE_FILE.exists():
            try:
                data = json.load(open(STAGE_FILE, encoding="utf-8"))
                triples = data.get("triples", [])
                log(f"  Read {len(triples)} triples from {STAGE_FILE.name}")
                all_triples.extend(triples)
                sources.append(fn)
                summaries.append({
                    "file": fn,
                    "triples": len(triples),
                    "elapsed_min": round(elapsed / 60, 1),
                    "stats": data.get("stats", {}),
                })
                # 备份本轮产物
                backup = BACKUP_DIR / f"stage2_{path.stem}_triples.json"
                shutil.copy(STAGE_FILE, backup)
                log(f"  Backup → {backup.name}")
            except Exception as e:
                log(f"  Read/backup failed: {e}", "ERROR")
        else:
            log(f"  {STAGE_FILE.name} not found after upload!", "ERROR")

    # 合并写回
    log(f"\n=== Merging {len(all_triples)} triples from {len(sources)} files ===")
    from collections import Counter
    rels = Counter(t.get("relation") for t in all_triples)
    total_entities = len({t.get("head") for t in all_triples} | {t.get("tail") for t in all_triples})
    merged = {
        "stage": "manual",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_files": sources,
        "triples": all_triples,
        "stats": {
            "total_triples": len(all_triples),
            "entities_count": total_entities,
            "relations_breakdown": dict(rels),
        },
        "per_file_summary": summaries,
    }
    with open(STAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    log(f"[OK] Merged JSON → {STAGE_FILE}")
    log(f"Total: {len(all_triples)} triples | {total_entities} entities | relations: {dict(rels)}")
    log(f"Total elapsed: {(time.time() - total_t0) / 60:.1f} min")


if __name__ == "__main__":
    main()
