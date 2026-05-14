"""
backend/routers/assembly_design.py

REST endpoints for the assembly-scheme skill (Plan 1: stage 1 active only).

7 endpoints (v0):
  POST   /assembly-design/scheme/new
  GET    /assembly-design/scheme/list
  GET    /assembly-design/scheme/{scheme_id}
  POST   /assembly-design/scheme/{scheme_id}/stage/{stage_key}
  POST   /assembly-design/scheme/{scheme_id}/reflux                 (501 in v0)
  POST   /assembly-design/scheme/{scheme_id}/iterate                (501 in v0)
  GET    /assembly-design/scheme/{scheme_id}/export                 (501 in v0)
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from backend.deps import get_state
from backend.pipelines.assembly_scheme.stage1_intake import run_stage1_intake
from backend.pipelines.assembly_scheme.stage2_requirements import run_stage2_requirements
from backend.pipelines.assembly_scheme.stage3_concept import run_stage3_concept
from backend.pipelines.assembly_scheme.stage4a_process import run_stage4a_process
from backend.pipelines.assembly_scheme.stage4b_tooling import run_stage4b_tooling
from backend.pipelines.assembly_scheme.stage5_review import run_stage5_review

router = APIRouter(prefix="/assembly-design", tags=["assembly-design"])

# Default storage dir; tests can monkeypatch this module-level constant.
SCHEMES_DIR = Path("storage/assembly_schemes")
SCHEMES_DIR.mkdir(parents=True, exist_ok=True)

VALID_STAGE_KEYS = {"1", "2", "3", "4a", "4b", "4c", "4d", "5"}


class NewSchemeRequest(BaseModel):
    subject_system: str = Field(..., min_length=1)
    subject_system_en: Optional[str] = None
    subject_scope: List[str] = Field(..., min_length=1)  # was default_factory=list; empty list rejected at boundary
    design_intent: str = "工艺优化"
    constraints: Dict[str, str] = Field(default_factory=dict)


class StageRequest(BaseModel):
    action: str  # "generate" | "regenerate" | "save_edits"
    payload: Dict[str, Any] = Field(default_factory=dict)
    user_guidance: Optional[str] = None


class RefluxRequest(BaseModel):
    approved: List[Dict[str, Any]] = Field(default_factory=list)


class IterateRequest(BaseModel):
    target_stage_key: str
    reason: Optional[str] = None


def _scheme_dir(scheme_id: str) -> Path:
    return SCHEMES_DIR / scheme_id


def _read_meta(scheme_id: str) -> Dict[str, Any]:
    p = _scheme_dir(scheme_id) / "meta.json"
    if not p.exists():
        raise HTTPException(404, f"scheme not found: {scheme_id}")
    return json.loads(p.read_text(encoding="utf-8"))


def _write_meta(scheme_id: str, meta: Dict[str, Any]) -> None:
    (_scheme_dir(scheme_id) / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )


@router.post("/scheme/new")
def create_scheme(req: NewSchemeRequest):
    scheme_id = f"scheme-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6]}"
    sd = _scheme_dir(scheme_id)
    sd.mkdir(parents=True, exist_ok=True)
    meta = {
        "scheme_id": scheme_id,
        "created_at": datetime.now().isoformat(),
        "subject": {
            "system": req.subject_system,
            "system_en": req.subject_system_en,
            "scope": req.subject_scope,
            "design_intent": req.design_intent,
            "constraints": req.constraints,
        },
        "stages_done": [],
    }
    _write_meta(scheme_id, meta)
    return {"scheme_id": scheme_id, "meta": meta}


@router.get("/scheme/list")
def list_schemes():
    items = []
    if SCHEMES_DIR.exists():
        for d in sorted(SCHEMES_DIR.iterdir()):
            if d.is_dir() and (d / "meta.json").exists():
                items.append(json.loads((d / "meta.json").read_text(encoding="utf-8")))
    return {"schemes": items}


@router.get("/scheme/{scheme_id}")
def get_scheme(scheme_id: str):
    sd = _scheme_dir(scheme_id)
    if not sd.exists():
        raise HTTPException(404, f"scheme not found: {scheme_id}")
    out: Dict[str, Any] = {"meta": _read_meta(scheme_id)}
    for stage_key in sorted(VALID_STAGE_KEYS):
        f = sd / f"stage{stage_key}.json"
        if f.exists():
            out[f"stage{stage_key}"] = json.loads(f.read_text(encoding="utf-8"))
    return out


@router.post("/scheme/{scheme_id}/stage/{stage_key}")
def run_stage(scheme_id: str, stage_key: str, req: StageRequest, state=Depends(get_state)):
    if stage_key not in VALID_STAGE_KEYS:
        raise HTTPException(400, f"invalid stage_key: {stage_key}")

    sd = _scheme_dir(scheme_id)
    if not sd.exists():
        raise HTTPException(404, f"scheme not found: {scheme_id}")

    # Stages not implemented yet
    if stage_key in {"4c", "4d"}:
        raise HTTPException(501, f"stage {stage_key} not implemented yet")

    if state.skill_registry is None:
        raise HTTPException(503, "skill registry not loaded")

    with state.assembly_lock:
        meta = _read_meta(scheme_id)
        stage_path = sd / f"stage{stage_key}.json"

        if req.action == "save_edits":
            if not req.payload:
                raise HTTPException(400, "save_edits requires non-empty payload")
            stage_path.write_text(
                json.dumps(req.payload, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            if stage_key not in meta["stages_done"]:
                meta["stages_done"].append(stage_key)
                _write_meta(scheme_id, meta)
            return {"saved": True, "scheme_id": scheme_id, "stage_key": stage_key}

        if req.action not in ("generate", "regenerate"):
            raise HTTPException(400, f"unknown action: {req.action}")

        if stage_key == "1":
            user_input = {
                "scheme_id": scheme_id,
                "subject": meta["subject"],
                "vision_notes": req.payload.get("vision_notes", ""),
            }
            result = run_stage1_intake(
                user_input=user_input,
                skill=state.skill_registry,
                web_search=state.web_search_client,
                llm_client=state.llm_client,
                neo4j_driver=state.neo4j_driver,
            )

        elif stage_key == "2":
            stage1_path = sd / "stage1.json"
            if not stage1_path.exists():
                raise HTTPException(409, "stage1 must be generated before stage2")
            stage1_payload = json.loads(stage1_path.read_text(encoding="utf-8"))
            result = run_stage2_requirements(
                stage1_payload=stage1_payload,
                skill=state.skill_registry,
                llm_client=state.llm_client,
                rag_searcher=None,
                neo4j_driver=state.neo4j_driver,
                user_guidance=req.user_guidance,
            )

        elif stage_key == "3":
            stage1_path = sd / "stage1.json"
            stage2_path = sd / "stage2.json"
            if not stage2_path.exists():
                raise HTTPException(409, "stage2 must be generated before stage3")
            if not stage1_path.exists():
                raise HTTPException(409, "stage1 must be generated before stage3")
            stage1_payload = json.loads(stage1_path.read_text(encoding="utf-8"))
            stage2_payload = json.loads(stage2_path.read_text(encoding="utf-8"))
            result = run_stage3_concept(
                stage1_payload=stage1_payload,
                stage2_payload=stage2_payload,
                skill=state.skill_registry,
                llm_client=state.llm_client,
                neo4j_driver=state.neo4j_driver,
                user_guidance=req.user_guidance,
            )

        elif stage_key == "4a":
            stage3_path = sd / "stage3.json"
            if not stage3_path.exists():
                raise HTTPException(409, "stage3 must be generated before stage4a")
            stage3_payload = json.loads(stage3_path.read_text(encoding="utf-8"))
            result = run_stage4a_process(
                stage3_payload=stage3_payload,
                skill=state.skill_registry,
                llm_client=state.llm_client,
                neo4j_driver=state.neo4j_driver,
                user_guidance=req.user_guidance,
            )

        elif stage_key == "4b":
            stage4a_path = sd / "stage4a.json"
            if not stage4a_path.exists():
                raise HTTPException(409, "stage4a must be generated before stage4b")
            stage4a_payload = json.loads(stage4a_path.read_text(encoding="utf-8"))
            result = run_stage4b_tooling(
                stage4a_payload=stage4a_payload,
                skill=state.skill_registry,
                llm_client=state.llm_client,
                neo4j_driver=state.neo4j_driver,
                user_guidance=req.user_guidance,
            )

        elif stage_key == "5":
            stage4b_path = sd / "stage4b.json"
            if not stage4b_path.exists():
                raise HTTPException(409, "stage4b must be generated before stage5")
            stage4a_path = sd / "stage4a.json"
            stage2_path = sd / "stage2.json"
            stage4b_payload = json.loads(stage4b_path.read_text(encoding="utf-8"))
            stage4a_payload = json.loads(stage4a_path.read_text(encoding="utf-8")) if stage4a_path.exists() else {}
            stage2_payload = json.loads(stage2_path.read_text(encoding="utf-8")) if stage2_path.exists() else {}
            result = run_stage5_review(
                stage4b_payload=stage4b_payload,
                stage4a_payload=stage4a_payload,
                stage2_payload=stage2_payload,
                skill=state.skill_registry,
                llm_client=state.llm_client,
                neo4j_driver=state.neo4j_driver,
                user_guidance=req.user_guidance,
            )

        stage_path.write_text(
            json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        if stage_key not in meta["stages_done"]:
            meta["stages_done"].append(stage_key)
            _write_meta(scheme_id, meta)
        return result


@router.post("/scheme/{scheme_id}/reflux")
def submit_reflux(scheme_id: str, req: RefluxRequest):
    if not _scheme_dir(scheme_id).exists():
        raise HTTPException(404, f"scheme not found: {scheme_id}")
    raise HTTPException(501, "reflux not implemented in Plan 1")


@router.post("/scheme/{scheme_id}/iterate")
def iterate_stage(scheme_id: str, req: IterateRequest):
    if not _scheme_dir(scheme_id).exists():
        raise HTTPException(404, f"scheme not found: {scheme_id}")
    raise HTTPException(501, "iterate not implemented in Plan 1")


@router.get("/scheme/{scheme_id}/export")
def export_scheme(scheme_id: str):
    sd = _scheme_dir(scheme_id)
    if not sd.exists():
        raise HTTPException(404, f"scheme not found: {scheme_id}")
    stage5_path = sd / "stage5.json"
    if not stage5_path.exists():
        raise HTTPException(409, "stage5 must be generated before export")

    stages: Dict[str, Any] = {}
    for sk in ("1", "2", "3", "4a", "4b", "5"):
        p = sd / f"stage{sk}.json"
        if p.exists():
            stages[sk] = json.loads(p.read_text(encoding="utf-8"))
    meta = _read_meta(scheme_id)

    lines = [
        "# 装配方案导出报告",
        "",
        f"**方案 ID**: `{scheme_id}`",
        f"**子系统**: {meta['subject']['system']}",
        f"**设计意图**: {meta['subject'].get('design_intent', '')}",
        f"**导出时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "---",
        "",
    ]

    stage_titles = {
        "1": "S1 任务调研",
        "2": "S2 需求分析",
        "3": "S3 概念架构",
        "4a": "S4a 工序总表",
        "4b": "S4b 工装规划",
        "5": "S5 评审报告",
    }

    for sk, title in stage_titles.items():
        if sk not in stages:
            continue
        lines.append(f"## {title}")
        lines.append("")
        lines.append("```json")
        lines.append(json.dumps(stages[sk], ensure_ascii=False, indent=2))
        lines.append("```")
        lines.append("")

    s5 = stages.get("5", {})
    kc_matrix = s5.get("kc_traceability_matrix", [])
    if kc_matrix:
        lines.append("## KC 追溯矩阵")
        lines.append("")
        lines.append("| KC ID | KC 名称 | 工序 | QC 检查点 | 覆盖 |")
        lines.append("|-------|---------|------|-----------|------|")
        for row in kc_matrix:
            covered = "✓" if row.get("covered") else "✗"
            procs = ", ".join(row.get("procedures", []))
            qcs = "; ".join(row.get("qc_checkpoints", []))
            lines.append(f"| {row.get('kc_id','')} | {row.get('kc_name','')} | {procs} | {qcs} | {covered} |")
        lines.append("")

    content_md = "\n".join(lines)
    export_path = str(sd / "final_scheme.md")
    (sd / "final_scheme.md").write_text(content_md, encoding="utf-8")
    return {"export_path": export_path, "content_md": content_md}
