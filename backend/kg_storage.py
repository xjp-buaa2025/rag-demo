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


# ── HITL 扩展 ──────────────────────────────────────────────────────────────

from dataclasses import dataclass, asdict, field
from typing import Optional, List, Dict

@dataclass
class StageState:
    stage: str
    status: str  # "idle" | "running" | "awaiting_review" | "approved"
    approved_at: Optional[str] = None

@dataclass
class StageStats:
    entities_count: int
    triples_count: int
    relation_breakdown: Dict[str, int]
    confidence_histogram: List[float]          # 5个区间 [0-0.2, 0.2-0.4, ..., 0.8-1.0] 各占比
    bom_coverage_ratio: Optional[float]        # Stage2 专用
    isolated_entities_count: int
    low_confidence_count: int                  # confidence < 0.5

@dataclass
class StageIssue:
    severity: str                              # "critical" | "warning" | "info"
    title: str
    title_zh: str
    description: str
    suggestion: str
    affected_triple_ids: List[str] = field(default_factory=list)

@dataclass
class StageDiff:
    added_triples: List[dict] = field(default_factory=list)
    removed_triples: List[dict] = field(default_factory=list)
    modified_triples: List[List[dict]] = field(default_factory=list)  # [[before, after], ...]

@dataclass
class StageReport:
    stage: str
    generated_at: str
    stats: StageStats
    issues: List[StageIssue] = field(default_factory=list)
    diff: Optional[StageDiff] = None


STAGE_STATE_FILES = {
    s: os.path.join(STORAGE_DIR, f"stage_{s}_state.json")
    for s in ["bom", "manual"]
}
STAGE_REPORT_FILES = {
    s: os.path.join(STORAGE_DIR, f"stage_{s}_report.json")
    for s in ["bom", "manual"]
}
TRANSLATIONS_FILE = os.path.join(STORAGE_DIR, "translations.json")


def _dc_to_dict(obj) -> dict:
    """dataclass → dict，递归处理嵌套"""
    return asdict(obj)


def _dict_to_stage_stats(d: dict) -> StageStats:
    return StageStats(**d)


def _dict_to_stage_issue(d: dict) -> StageIssue:
    return StageIssue(**d)


def _dict_to_stage_diff(d: Optional[dict]) -> Optional[StageDiff]:
    if d is None:
        return None
    return StageDiff(**d)


def write_stage_state(stage: str, state: StageState) -> None:
    path = STAGE_STATE_FILES[stage]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(_dc_to_dict(state), f, ensure_ascii=False, indent=2)


def read_stage_state(stage: str) -> Optional[StageState]:
    path = STAGE_STATE_FILES[stage]
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    return StageState(**d)


def write_stage_report(stage: str, report: StageReport) -> None:
    path = STAGE_REPORT_FILES[stage]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(_dc_to_dict(report), f, ensure_ascii=False, indent=2)


def read_stage_report(stage: str) -> Optional[StageReport]:
    path = STAGE_REPORT_FILES[stage]
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    stats = _dict_to_stage_stats(d["stats"])
    issues = [_dict_to_stage_issue(i) for i in d.get("issues", [])]
    diff = _dict_to_stage_diff(d.get("diff"))
    return StageReport(
        stage=d["stage"],
        generated_at=d["generated_at"],
        stats=stats,
        issues=issues,
        diff=diff,
    )


def write_translations(cache: Dict[str, str]) -> None:
    os.makedirs(os.path.dirname(TRANSLATIONS_FILE), exist_ok=True)
    with open(TRANSLATIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def read_translations() -> Dict[str, str]:
    if not os.path.exists(TRANSLATIONS_FILE):
        return {}
    with open(TRANSLATIONS_FILE, encoding="utf-8") as f:
        return json.load(f)
