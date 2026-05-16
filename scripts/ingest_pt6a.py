"""
PT6A 整机受控入库脚本（Day 1 AM 任务）

对应计划：docs/chapter4_experiment_plan.md v4

执行流程：
  Step 0. 健康检查 + 确认知识库为 0
  Step 1. BOM 结构化入库（快，10-20 min）
          POST /kg/stage1/bom  bom.docx
          产出：storage/kg_stages/stage1_bom_triples.json + Neo4j Part/Assembly
  Step 2. 手册 RAG 入库 + KG 自动提取（慢，2-3 h）
          POST /ingest/pipeline × 3（manual1_body.md, manual2.md, manual3.md）
          产出：Qdrant 向量 + BM25 索引 + Neo4j KG 三元组
  Step 3. 最终健康检查 + 报告

前置条件：
  - 后端已启动（PYTHONUTF8=1 DISABLE_AUTO_INGEST=1）
  - Qdrant / BM25 / Neo4j 已清空
  - data/KG/PT6A/ 下文件已就位

用法：
  python scripts/ingest_pt6a.py            # 完整入库
  python scripts/ingest_pt6a.py --smoke    # 烟雾测试（只跑 BOM，快速验证）
  python scripts/ingest_pt6a.py --skip-bom # 跳过 BOM（若已入库过）
"""

import argparse
import json
import sys
import time
from pathlib import Path

import requests

# 强制 stdout/stderr 用 UTF-8（Windows GBK 默认编码无法输出 ⚠/✓ 等字符）
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

BACKEND = "http://localhost:8000"
PT6A_DIR = Path("data/KG/PT6A")


def log(msg: str, level: str = "INFO"):
    ts = time.strftime("%H:%M:%S")
    print(f"[{ts}] [{level}] {msg}", flush=True)


def health_check() -> dict:
    r = requests.get(f"{BACKEND}/health", timeout=5)
    r.raise_for_status()
    return r.json()


def consume_sse(url: str, files: dict, data: dict | None = None, label: str = "") -> int:
    """
    消费 SSE 流，返回收到的 log 帧数。
    遇到 [DONE] 或流结束即返回。
    """
    t0 = time.time()
    last_log_line = ""
    frame_count = 0
    try:
        with requests.post(url, files=files, data=data, stream=True, timeout=(30, 7200)) as r:
            r.raise_for_status()
            for raw in r.iter_lines(decode_unicode=True):
                if not raw:
                    continue
                if raw.startswith("data: "):
                    payload = raw[6:].strip()
                    if payload == "[DONE]":
                        break
                    try:
                        obj = json.loads(payload)
                    except Exception:
                        continue
                    frame_count += 1
                    # log 帧：只打印与上次不同的最后一行
                    if "log" in obj:
                        lines = obj["log"].rstrip().split("\n")
                        newest = lines[-1] if lines else ""
                        if newest and newest != last_log_line:
                            elapsed = time.time() - t0
                            print(f"    [{label} +{elapsed:5.0f}s] {newest[:160]}", flush=True)
                            last_log_line = newest
                    elif "stage" in obj:
                        print(f"    [{label}] >>> stage: {obj['stage']}", flush=True)
                    elif obj.get("done"):
                        print(f"    [{label}] === done ===", flush=True)
    except requests.exceptions.ReadTimeout:
        log(f"{label} 超时（7200s），继续下一步", "WARN")
    except Exception as e:
        log(f"{label} SSE 异常：{e}", "ERROR")
    elapsed = (time.time() - t0) / 60
    log(f"{label} 结束，耗时 {elapsed:.1f} min，收到 {frame_count} 帧")
    return frame_count


def step_bom():
    # 优先使用 bom.csv（由 convert_bom_docx_to_csv.py 生成，结构化快速路径）
    # 若不存在才回退 bom.docx（走 LLM 慢路径）
    path_csv = PT6A_DIR / "bom.csv"
    path_docx = PT6A_DIR / "bom.docx"
    if path_csv.exists():
        path = path_csv
        mime = "text/csv"
    elif path_docx.exists():
        log("bom.csv 不存在，回退 bom.docx（将走 LLM 慢路径）", "WARN")
        path = path_docx
        mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    else:
        log(f"BOM 文件不存在：{PT6A_DIR}", "ERROR")
        return False
    size_kb = path.stat().st_size / 1024
    log(f"Step 1 | BOM 入库 ({path.name}, {size_kb:.0f} KB)")
    with open(path, "rb") as f:
        files = {"file": (path.name, f, mime)}
        data = {"clear_first": "true"}
        consume_sse(f"{BACKEND}/kg/stage1/bom", files=files, data=data, label="BOM")
    return True


def step_manual(filename: str):
    path = PT6A_DIR / filename
    if not path.exists():
        log(f"手册文件不存在：{path}", "ERROR")
        return False
    size_kb = path.stat().st_size / 1024
    log(f"Step 2 | 手册入库 ({path.name}, {size_kb:.0f} KB)")
    with open(path, "rb") as f:
        files = {"file": (path.name, f, "text/markdown")}
        consume_sse(f"{BACKEND}/ingest/pipeline", files=files, label=path.stem)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true", help="只跑 BOM（烟雾测试）")
    ap.add_argument("--skip-bom", action="store_true", help="跳过 BOM")
    ap.add_argument("--only-manual", default=None, help="只入指定 manual 文件名")
    args = ap.parse_args()

    log("=" * 60)
    log("PT6A 整机受控入库（Day 1 AM）")
    log("=" * 60)

    # 健康检查
    try:
        h = health_check()
    except Exception as e:
        log(f"后端不可达：{e}", "ERROR")
        sys.exit(1)

    count = h.get("collection_count", 0)
    log(f"Backend OK | LLM: {h.get('model', '?')}")
    log(f"Current Qdrant chunks: {count}")
    if count != 0:
        log(f"⚠️  知识库不为 0（{count} 条），请先清库！", "ERROR")
        sys.exit(1)

    total_t0 = time.time()

    # Step 1: BOM
    if not args.skip_bom:
        step_bom()
        h = health_check()
        log(f"After BOM: Qdrant={h.get('collection_count', 0)} chunks")

    if args.smoke:
        log("--smoke 模式，跳过手册入库")
        return

    # Step 2: Manuals
    manuals = ["manual1_body.md", "manual2.md", "manual3.md"]
    if args.only_manual:
        manuals = [args.only_manual]

    for fn in manuals:
        step_manual(fn)
        h = health_check()
        log(f"After {fn}: Qdrant={h.get('collection_count', 0)} chunks")

    total_min = (time.time() - total_t0) / 60
    log("=" * 60)
    log(f"ALL DONE | Total elapsed: {total_min:.1f} min")
    log("=" * 60)
    h = health_check()
    log(f"Final: Qdrant={h.get('collection_count', 0)} chunks")


if __name__ == "__main__":
    main()
