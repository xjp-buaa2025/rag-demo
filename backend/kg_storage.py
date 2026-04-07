"""backend/kg_storage.py — 知识图谱阶段中间产物存储辅助"""
import os, json
from datetime import datetime, timezone

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORAGE_DIR = os.path.join(_ROOT, "storage", "kg_stages")
GOLDEN_PATH = os.path.join(_ROOT, "tests", "kg", "fixtures", "golden_triples.json")

STAGE_FILES = {
    "bom":    os.path.join(STORAGE_DIR, "stage1_bom_triples.json"),
    "manual": os.path.join(STORAGE_DIR, "stage2_manual_triples.json"),
    "cad":    os.path.join(STORAGE_DIR, "stage3_cad_triples.json"),
}
STAGE_ORDER = ["bom", "manual", "cad"]

def write_stage(stage: str, data: dict) -> None:
    os.makedirs(STORAGE_DIR, exist_ok=True)
    with open(STAGE_FILES[stage], "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def read_stage(stage: str) -> dict | None:
    path = STAGE_FILES.get(stage)
    if path and os.path.exists(path):
        return json.loads(open(path, encoding="utf-8").read())
    return None

def stage_exists(stage: str) -> bool:
    path = STAGE_FILES.get(stage)
    return bool(path and os.path.exists(path))

def get_all_stages_status() -> dict:
    return {
        s: {
            "exists": stage_exists(s),
            "file": STAGE_FILES[s],
            "generated_at": (read_stage(s) or {}).get("generated_at"),
        }
        for s in STAGE_ORDER
    }

def check_prereq(stage: str) -> str | None:
    """返回缺失的前序阶段名，若全部满足返回None"""
    idx = STAGE_ORDER.index(stage) if stage in STAGE_ORDER else -1
    for prereq in STAGE_ORDER[:idx]:
        if not stage_exists(prereq):
            return prereq
    return None
