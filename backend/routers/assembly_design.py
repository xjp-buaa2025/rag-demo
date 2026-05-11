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

    if stage_key != "1":
        raise HTTPException(501, f"stage {stage_key} not implemented in Plan 1")

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
            return {"saved": True, "scheme_id": scheme_id, "stage_key": stage_key}

        if req.action in ("generate", "regenerate"):
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
            stage_path.write_text(
                json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            if stage_key not in meta["stages_done"]:
                meta["stages_done"].append(stage_key)
                _write_meta(scheme_id, meta)
            return result

        raise HTTPException(400, f"unknown action: {req.action}")


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
    if not _scheme_dir(scheme_id).exists():
        raise HTTPException(404, f"scheme not found: {scheme_id}")
    raise HTTPException(501, "export not implemented in Plan 1")
