"""
KG 提取进度 watcher：每 60s 输出 Neo4j 节点/边数 + Qdrant chunks
用于跟踪后台 ingest_pipeline 的 KG 提取阶段进度

用法：
  python scripts/watch_kg_progress.py
  Ctrl+C 退出
"""
import sys
import time
import requests
from neo4j import GraphDatabase

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def snapshot():
    """单次快照"""
    out = {}
    # Qdrant chunks
    try:
        r = requests.get("http://localhost:8000/health", timeout=3).json()
        out["chunks"] = r.get("collection_count", -1)
    except Exception as e:
        out["chunks"] = f"err:{e}"

    # Neo4j
    try:
        drv = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
        with drv.session() as s:
            n = s.run("MATCH (n) RETURN count(n) as c").single()["c"]
            e = s.run("MATCH ()-[r]->() RETURN count(r) as c").single()["c"]
            labels = s.run(
                "MATCH (n) RETURN labels(n)[0] as lbl, count(*) as c ORDER BY c DESC"
            ).data()
        drv.close()
        out["nodes"] = n
        out["edges"] = e
        out["labels"] = {x["lbl"]: x["c"] for x in labels}
    except Exception as e:
        out["nodes"] = f"err:{e}"

    return out


def main():
    print(f"[{time.strftime('%H:%M:%S')}] KG progress watcher started. Ctrl+C to stop.")
    print(f"  Format: chunks | nodes | edges | by-label")
    last = None
    same_count = 0
    while True:
        s = snapshot()
        delta_n = s.get("nodes", 0) - (last["nodes"] if last else 0) if last else 0
        delta_e = s.get("edges", 0) - (last["edges"] if last else 0) if last else 0
        labels_str = " ".join(f"{k}={v}" for k, v in (s.get("labels") or {}).items())
        msg = (
            f"[{time.strftime('%H:%M:%S')}] "
            f"chunks={s.get('chunks')} | nodes={s.get('nodes')} (+{delta_n}) | "
            f"edges={s.get('edges')} (+{delta_e}) | {labels_str}"
        )
        print(msg, flush=True)

        # 静止判定
        if last and s.get("nodes") == last.get("nodes") and s.get("edges") == last.get("edges"):
            same_count += 1
        else:
            same_count = 0
        if same_count >= 5:
            print(f"[{time.strftime('%H:%M:%S')}] 5 轮无变化，KG 提取可能已完成或卡住。退出。", flush=True)
            break

        last = s
        time.sleep(60)


if __name__ == "__main__":
    main()
