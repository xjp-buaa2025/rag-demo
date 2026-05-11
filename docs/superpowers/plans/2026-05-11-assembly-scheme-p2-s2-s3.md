# Assembly-Scheme Skill — Plan 2 (S2 + S3) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend the `aero-engine-assembly-scheme` skill from Plan 1's S1-only state to a working S1→S2→S3 backend chain. After this plan completes, the system can accept stage1 output, run requirements analysis (QFD + DFA + KC) for stage2, and produce candidate concept architectures (with KG-based reachability check + datum consistency review) for stage3.

**Architecture:** Same three-layer split as Plan 1. This plan only touches Layer 1 (skill files) and Layer 2 (backend pipelines + router). Frontend stays deferred to Plan 3. We also clean up 3 carry-over items from Plan 1: `assembly_lock` is now actually used, `subject_scope` no longer silently violates stage1 schema, and we add an explicit out-of-scope note for cleaning up garbled untracked files.

**Tech Stack:** Python 3.10 / FastAPI / Pydantic v1 (existing) / pytest / `jsonschema` (already installed) / Neo4j driver (optional, lazy) / existing `FallbackLLMClient`. No new external deps.

**Spec reference:** `docs/superpowers/specs/2026-05-08-assembly-scheme-skill-design.md` §§2.2, 2.3, 4.1-4.5, 5.5 (P3 subset: S2+S3)

**Conventions:**
- All Python commands run from repo root with conda env `rag_demo` activated. PowerShell form: `$env:PYTHONUTF8="1"; python ...`. Bash form: `PYTHONUTF8=1 python ...`. Use whichever matches your shell.
- All test runs target `tests/assembly/` per this plan; use `-v` for verbose output.
- All commits should pass tests before being made. If a test fails after an implementation step, fix the implementation in a follow-up step before committing.
- TDD discipline: every code-bearing task has the red-green-refactor cycle written out as separate steps. Pure-document tasks (methodology / prompt markdown) skip the failing-test step but still commit at the end.

---

## File Structure

### Created in this plan

```
skills/aero-engine-assembly-scheme/
├── methodology/
│   ├── s2_requirements_qfd.md        # REWRITTEN — was outline-only
│   └── s3_concept_architecture.md    # REWRITTEN — was outline-only
├── prompts/
│   ├── s2_requirements.prompt.md     # NEW
│   └── s3_concept.prompt.md          # NEW
└── templates/
    ├── schemas/
    │   ├── stage2.schema.json        # REWRITTEN — was placeholder
    │   └── stage3.schema.json        # REWRITTEN — was placeholder
    └── golden/
        ├── pt6a_hpc_stage2.json      # NEW
        └── pt6a_hpc_stage3.json      # NEW

backend/pipelines/assembly_scheme/
├── stage2_requirements.py            # NEW
└── stage3_concept.py                 # NEW

tests/assembly/
├── test_schemas.py                   # EXTENDED — adds stage2/stage3 validation tests
├── test_stage2_requirements.py       # NEW
├── test_stage3_concept.py            # NEW
├── test_assembly_design_router.py    # EXTENDED — adds stage2/stage3 route tests
└── test_e2e_s1_s2_s3.py              # NEW — full chain smoke test
```

### Modified

| File | Change |
|------|--------|
| `backend/routers/assembly_design.py` | (1) `NewSchemeRequest.subject_scope` becomes required, `min_length=1`; (2) `run_stage` uses `state.assembly_lock` around file writes; (3) `stage_key in {"2", "3"}` now dispatches to new pipelines |
| `PROJECT_GUIDE.md` | §16 gains "P2 progress: S2 + S3 active" subsection with evidence links |

### Out of scope (carry-over for chamberlain)

1. **Garbled untracked files** (e.g. `data/\357\200\252...`): not deleted here — destructive ops require explicit chamberlain approval per house rules. Run `git clean -nd data/` first, then `git clean -fd data/` if the dry-run looks right.
2. Stages S4a-S4d and S5 (deferred to Plan 3).
3. Frontend `AssemblySchemePage.tsx` and `StageCard.tsx` (deferred to Plan 3).
4. Reflux / iterate / export endpoints stay HTTP 501.

---

## Tasks Overview

| # | Task | Phase | Time |
|---|------|-------|------|
| 1 | Carry-over: enforce `subject_scope` non-empty | P0 | 15 min |
| 2 | Carry-over: actually use `assembly_lock` in router writes | P0 | 20 min |
| 3 | Stage 2 schema + golden example (TDD) | P1 | 30 min |
| 4 | Stage 2 methodology + prompt (documents) | P1 | 25 min |
| 5 | Implement `run_stage2_requirements` (TDD) | P1 | 45 min |
| 6 | Activate stage 2 route (TDD) | P1 | 25 min |
| 7 | Stage 3 schema + golden example (TDD) | P2 | 35 min |
| 8 | Stage 3 methodology + prompt (documents) | P2 | 25 min |
| 9 | Implement `run_stage3_concept` (TDD) | P2 | 50 min |
| 10 | Activate stage 3 route (TDD) | P2 | 25 min |
| 11 | E2E S1 → S2 → S3 chain test | P3 | 25 min |
| 12 | PROJECT_GUIDE.md §16 update + full suite green | P3 | 20 min |

Estimated total: ~5.5 hours of focused work.

---

# Phase 0: Carry-over Fixes

## Task 1: Enforce `subject_scope` non-empty in `NewSchemeRequest`

**Why:** Plan 1's `NewSchemeRequest.subject_scope: List[str] = Field(default_factory=list)` allowed `[]`, but `stage1.schema.json` requires `"scope": { "minItems": 1 }`. Today an empty scope passes through `POST /scheme/new` and only blows up later when stage1 runs schema validation. Fix at the boundary.

**Files:**
- Modify: `backend/routers/assembly_design.py:40-45` (NewSchemeRequest class)
- Test: `tests/assembly/test_assembly_design_router.py` (add 2 cases)

- [ ] **Step 1.1: Add failing test for empty scope rejection**

Append to `tests/assembly/test_assembly_design_router.py` (create the test if file uses class-style; otherwise add as a top-level function near the existing `test_create_scheme` style):

```python
def test_create_scheme_rejects_empty_scope(client):
    """subject_scope=[] must be rejected at the API boundary, not silently passed through."""
    resp = client.post(
        "/assembly-design/scheme/new",
        json={
            "subject_system": "PT6A HPC",
            "subject_scope": [],
            "design_intent": "工艺优化",
            "constraints": {"primary": "可靠性"},
        },
    )
    assert resp.status_code == 422, f"expected 422, got {resp.status_code}: {resp.text}"


def test_create_scheme_accepts_single_element_scope(client):
    """A 1-element scope must succeed."""
    resp = client.post(
        "/assembly-design/scheme/new",
        json={
            "subject_system": "PT6A HPC",
            "subject_scope": ["3 级轴流"],
            "design_intent": "工艺优化",
            "constraints": {"primary": "可靠性"},
        },
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["meta"]["subject"]["scope"] == ["3 级轴流"]
```

- [ ] **Step 1.2: Run tests, confirm first one fails**

PowerShell: `$env:PYTHONUTF8="1"; pytest tests/assembly/test_assembly_design_router.py::test_create_scheme_rejects_empty_scope -v`
Bash: `PYTHONUTF8=1 pytest tests/assembly/test_assembly_design_router.py::test_create_scheme_rejects_empty_scope -v`
Expected: FAIL — endpoint returns 200 with empty scope.

- [ ] **Step 1.3: Modify `NewSchemeRequest` in `backend/routers/assembly_design.py`**

Change the field definition. Pydantic v1 syntax (this project's version):

```python
class NewSchemeRequest(BaseModel):
    subject_system: str = Field(..., min_length=1)
    subject_system_en: Optional[str] = None
    subject_scope: List[str] = Field(..., min_items=1)  # was default_factory=list
    design_intent: str = "工艺优化"
    constraints: Dict[str, str] = Field(default_factory=dict)
```

(If the project is on Pydantic v2, swap `min_items` for `min_length`. Check `requirements.txt` if uncertain.)

- [ ] **Step 1.4: Run both tests, confirm both pass**

`pytest tests/assembly/test_assembly_design_router.py::test_create_scheme_rejects_empty_scope tests/assembly/test_assembly_design_router.py::test_create_scheme_accepts_single_element_scope -v`
Expected: 2 PASS.

- [ ] **Step 1.5: Run the full assembly suite to confirm no regression**

`pytest tests/assembly/ -v`
Expected: all green (carry-over test cases that used empty scope may need fixing — find them with the next step if any fail).

- [ ] **Step 1.6: If regressions surface, fix them**

Search for any existing tests that POST `/scheme/new` without scope or with `[]`:

Use Grep: pattern `subject_scope`, path `tests/assembly`. For each hit that uses `[]` or omits the field, change to a 1-element list (e.g. `["3 级轴流"]`). These are test data updates, not behavior changes.

Re-run `pytest tests/assembly/ -v`. Expected: all green.

- [ ] **Step 1.7: Commit**

```bash
git add backend/routers/assembly_design.py tests/assembly/test_assembly_design_router.py
git commit -m "fix(assembly): enforce subject_scope non-empty at NewSchemeRequest boundary"
```

---

## Task 2: Wrap router file writes with `assembly_lock`

**Why:** Plan 1 added `state.assembly_lock: threading.Lock` but `assembly_design.py` never acquires it. Two concurrent `POST /scheme/{id}/stage/1` for the same scheme can interleave `stage1.json` writes and corrupt `meta.json["stages_done"]`. Hold the lock for the duration of "compute → write JSON → update meta".

**Files:**
- Modify: `backend/routers/assembly_design.py` — wrap the body of `run_stage` (the generate/regenerate/save_edits dispatcher) with `state.assembly_lock`
- Test: `tests/assembly/test_assembly_design_router.py` (1 case using `threading.Thread`)

- [ ] **Step 2.1: Add failing test for concurrent stage write**

Append to `tests/assembly/test_assembly_design_router.py`:

```python
def test_concurrent_stage_writes_are_serialized(client, monkeypatch):
    """Two threads hitting the same stage must not corrupt stages_done.

    We don't measure throughput — we measure that meta.json after both writes
    has each stage_key listed exactly once (no duplicate, no missing).
    """
    import threading

    # 1) Create a scheme
    resp = client.post(
        "/assembly-design/scheme/new",
        json={
            "subject_system": "PT6A HPC",
            "subject_scope": ["3 级轴流"],
            "design_intent": "工艺优化",
            "constraints": {"primary": "可靠性"},
        },
    )
    scheme_id = resp.json()["scheme_id"]

    errors: list = []

    def hit_stage_one():
        try:
            r = client.post(
                f"/assembly-design/scheme/{scheme_id}/stage/1",
                json={"action": "generate", "payload": {}},
            )
            assert r.status_code == 200, r.text
        except Exception as e:
            errors.append(e)

    t1 = threading.Thread(target=hit_stage_one)
    t2 = threading.Thread(target=hit_stage_one)
    t1.start(); t2.start()
    t1.join(); t2.join()

    assert not errors, f"thread errors: {errors}"

    # Re-fetch and check stages_done has no duplicates
    final = client.get(f"/assembly-design/scheme/{scheme_id}").json()
    assert final["meta"]["stages_done"].count("1") == 1, final["meta"]["stages_done"]
```

- [ ] **Step 2.2: Run test, confirm it fails (or is flaky)**

`pytest tests/assembly/test_assembly_design_router.py::test_concurrent_stage_writes_are_serialized -v`
Expected: FAIL or flaky — `stages_done` ends up as `["1", "1"]` because the unguarded append-then-write races.

- [ ] **Step 2.3: Add lock acquisition in `run_stage`**

In `backend/routers/assembly_design.py`, find the `run_stage` function. Wrap the function body that performs writes:

```python
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

    # Serialize all writes for this scheme across threads.
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
```

The lock is held throughout because the read-modify-write of `meta["stages_done"]` is what races.

- [ ] **Step 2.4: Run test, confirm it passes**

`pytest tests/assembly/test_assembly_design_router.py::test_concurrent_stage_writes_are_serialized -v`
Expected: PASS.

- [ ] **Step 2.5: Run full assembly suite**

`pytest tests/assembly/ -v`
Expected: all green.

- [ ] **Step 2.6: Commit**

```bash
git add backend/routers/assembly_design.py tests/assembly/test_assembly_design_router.py
git commit -m "fix(assembly): serialize stage writes with assembly_lock to prevent stages_done corruption"
```

---

# Phase 1: Stage 2 (Requirements & Constraints)

## Task 3: Stage 2 schema + golden example (TDD)

**Why:** `templates/schemas/stage2.schema.json` is a placeholder with no nested constraints. Spec §2.2 needs structured `user_needs`, `engineering_metrics`, `assembly_features`, `key_characteristics` (each with id/text/links), a `dfa_score` block, and a `risks` block. The golden file `pt6a_hpc_stage2.json` doubles as JSON-schema positive case and LLM few-shot.

**Files:**
- Modify: `skills/aero-engine-assembly-scheme/templates/schemas/stage2.schema.json` (full rewrite)
- Create: `skills/aero-engine-assembly-scheme/templates/golden/pt6a_hpc_stage2.json`
- Modify: `tests/assembly/test_schemas.py` (add 2 cases)

- [ ] **Step 3.1: Add failing tests for stage2 schema + golden validity**

Append to `tests/assembly/test_schemas.py` (this file already exists from Plan 1):

```python
def test_stage2_schema_requires_qfd_blocks():
    """stage2 schema must declare the QFD blocks + KC + DFA + risks as required."""
    import json
    from pathlib import Path
    schema_path = Path("skills/aero-engine-assembly-scheme/templates/schemas/stage2.schema.json")
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    required = set(schema["required"])
    for key in ["stage1_ref", "user_needs", "engineering_metrics",
                "assembly_features", "key_characteristics", "dfa_score", "risks"]:
        assert key in required, f"stage2 schema must require '{key}'"
    # Every list field must enforce minItems >= 1
    for arr in ["user_needs", "engineering_metrics", "assembly_features",
                "key_characteristics", "risks"]:
        assert schema["properties"][arr].get("minItems", 0) >= 1, \
            f"'{arr}' must enforce minItems >= 1"


def test_pt6a_hpc_stage2_golden_validates():
    """The golden PT6A HPC stage2 example must satisfy stage2 schema."""
    import json
    import jsonschema
    from pathlib import Path
    schema = json.loads(
        Path("skills/aero-engine-assembly-scheme/templates/schemas/stage2.schema.json")
        .read_text(encoding="utf-8")
    )
    golden = json.loads(
        Path("skills/aero-engine-assembly-scheme/templates/golden/pt6a_hpc_stage2.json")
        .read_text(encoding="utf-8")
    )
    jsonschema.validate(instance=golden, schema=schema)
```

- [ ] **Step 3.2: Run tests, confirm both fail**

`pytest tests/assembly/test_schemas.py -v -k stage2`
Expected: 2 FAIL — schema still placeholder, golden doesn't exist.

- [ ] **Step 3.3: Write full stage2 schema**

Overwrite `skills/aero-engine-assembly-scheme/templates/schemas/stage2.schema.json`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "stage2.schema.json",
  "title": "Stage 2 — Requirements & Constraints",
  "type": "object",
  "required": ["stage1_ref", "user_needs", "engineering_metrics", "assembly_features", "key_characteristics", "dfa_score", "risks"],
  "properties": {
    "stage1_ref": {
      "type": "string",
      "pattern": "^scheme-[0-9]{8}-[a-f0-9]{6}$",
      "description": "scheme_id of the stage1 this stage2 was derived from"
    },
    "user_needs": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": ["id", "text", "weight"],
        "properties": {
          "id": {"type": "string", "pattern": "^U[0-9]+$"},
          "text": {"type": "string", "minLength": 1},
          "weight": {"type": "integer", "minimum": 1, "maximum": 5}
        }
      }
    },
    "engineering_metrics": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": ["id", "name", "target", "linked_needs"],
        "properties": {
          "id": {"type": "string", "pattern": "^M[0-9]+$"},
          "name": {"type": "string", "minLength": 1},
          "target": {"type": "string", "minLength": 1},
          "linked_needs": {
            "type": "array",
            "minItems": 1,
            "items": {"type": "string", "pattern": "^U[0-9]+$"}
          }
        }
      }
    },
    "assembly_features": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": ["id", "name", "spec", "linked_metrics"],
        "properties": {
          "id": {"type": "string", "pattern": "^F[0-9]+$"},
          "name": {"type": "string", "minLength": 1},
          "spec": {"type": "string", "minLength": 1},
          "linked_metrics": {
            "type": "array",
            "minItems": 1,
            "items": {"type": "string", "pattern": "^M[0-9]+$"}
          }
        }
      }
    },
    "key_characteristics": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": ["id", "name", "target", "criticality"],
        "properties": {
          "id": {"type": "string", "pattern": "^KC[0-9]+$"},
          "name": {"type": "string", "minLength": 1},
          "target": {"type": "string", "minLength": 1},
          "criticality": {"type": "string", "enum": ["high", "medium", "low"]},
          "linked_features": {
            "type": "array",
            "items": {"type": "string", "pattern": "^F[0-9]+$"}
          }
        }
      }
    },
    "dfa_score": {
      "type": "object",
      "required": ["overall", "theoretical_min_parts", "actual_parts", "bottlenecks"],
      "properties": {
        "overall": {"type": "number", "minimum": 0, "maximum": 1},
        "theoretical_min_parts": {"type": "integer", "minimum": 1},
        "actual_parts": {"type": "integer", "minimum": 1},
        "method": {"type": "string"},
        "bottlenecks": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["part_id", "issue"],
            "properties": {
              "part_id": {"type": "string"},
              "name": {"type": "string"},
              "issue": {"type": "string"}
            }
          }
        }
      }
    },
    "risks": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": ["id", "text", "severity"],
        "properties": {
          "id": {"type": "string", "pattern": "^R[0-9]+$"},
          "text": {"type": "string", "minLength": 1},
          "severity": {"type": "integer", "minimum": 1, "maximum": 5},
          "linked_kcs": {
            "type": "array",
            "items": {"type": "string", "pattern": "^KC[0-9]+$"}
          }
        }
      }
    },
    "uncertainty": {
      "type": "string",
      "enum": ["高", "中", "低"],
      "description": "Self-reported confidence by LLM; allowed to be omitted in placeholder mode"
    }
  }
}
```

- [ ] **Step 3.4: Run schema test, confirm it passes (golden still fails)**

`pytest tests/assembly/test_schemas.py::test_stage2_schema_requires_qfd_blocks -v`
Expected: PASS.
`pytest tests/assembly/test_schemas.py::test_pt6a_hpc_stage2_golden_validates -v`
Expected: FAIL — golden file doesn't exist yet.

- [ ] **Step 3.5: Write the PT6A HPC stage2 golden example**

Create `skills/aero-engine-assembly-scheme/templates/golden/pt6a_hpc_stage2.json`:

```json
{
  "stage1_ref": "scheme-20260508-a1b2c3",
  "user_needs": [
    {"id": "U1", "text": "高可靠性，长时间运行不易失效", "weight": 5},
    {"id": "U2", "text": "便于外场维修与关键件更换", "weight": 4},
    {"id": "U3", "text": "单台装配工时可控", "weight": 3},
    {"id": "U4", "text": "合规 AS9100D / GJB 5060A", "weight": 5}
  ],
  "engineering_metrics": [
    {"id": "M1", "name": "MTBF", "target": ">= 4000 hrs", "linked_needs": ["U1"]},
    {"id": "M2", "name": "MTTR (关键件)", "target": "<= 8 hrs", "linked_needs": ["U2"]},
    {"id": "M3", "name": "单台装配工时", "target": "<= 40 工时", "linked_needs": ["U3"]},
    {"id": "M4", "name": "首次装配合格率", "target": ">= 95%", "linked_needs": ["U1", "U4"]}
  ],
  "assembly_features": [
    {"id": "F1", "name": "叶片装入扭矩一致性", "spec": "Cpk >= 1.33", "linked_metrics": ["M1", "M4"]},
    {"id": "F2", "name": "转子动平衡精度", "spec": "<= 5 g·mm @ 一阶", "linked_metrics": ["M1"]},
    {"id": "F3", "name": "前段法兰可拆性", "spec": "无需破坏性拆卸", "linked_metrics": ["M2"]},
    {"id": "F4", "name": "装配工序流转节拍", "spec": "瓶颈工序 <= 90 min", "linked_metrics": ["M3"]}
  ],
  "key_characteristics": [
    {"id": "KC1", "name": "叶尖间隙", "target": "0.5-1.0 mm", "criticality": "high", "linked_features": ["F1"]},
    {"id": "KC2", "name": "转子端面跳动", "target": "<= 0.05 mm", "criticality": "high", "linked_features": ["F2"]},
    {"id": "KC3", "name": "法兰螺栓预紧力一致性", "target": "± 5% N·m", "criticality": "medium", "linked_features": ["F3"]},
    {"id": "KC4", "name": "转子整体不平衡量", "target": "<= 5 g·mm", "criticality": "high", "linked_features": ["F2"]}
  ],
  "dfa_score": {
    "overall": 0.72,
    "theoretical_min_parts": 25,
    "actual_parts": 35,
    "method": "Boothroyd-Dewhurst (lightweight)",
    "bottlenecks": [
      {"part_id": "P012", "name": "前段静子定位环", "issue": "定位面缺失，需借助专用工装定位"},
      {"part_id": "P021", "name": "后段轴承支撑", "issue": "螺栓孔位偏置导致重复定位耗时高"}
    ]
  },
  "risks": [
    {"id": "R1", "text": "高温段间隙超差导致碰摩", "severity": 4, "linked_kcs": ["KC1"]},
    {"id": "R2", "text": "转子不平衡引起一阶振动", "severity": 4, "linked_kcs": ["KC2", "KC4"]},
    {"id": "R3", "text": "法兰螺栓预紧力离散导致密封失效", "severity": 3, "linked_kcs": ["KC3"]}
  ],
  "uncertainty": "中"
}
```

- [ ] **Step 3.6: Run both schema tests, confirm both pass**

`pytest tests/assembly/test_schemas.py -v -k stage2`
Expected: 2 PASS.

- [ ] **Step 3.7: Commit**

```bash
git add skills/aero-engine-assembly-scheme/templates/schemas/stage2.schema.json \
        skills/aero-engine-assembly-scheme/templates/golden/pt6a_hpc_stage2.json \
        tests/assembly/test_schemas.py
git commit -m "feat(assembly): full stage2 schema (QFD + DFA + KC + risks) and PT6A HPC golden example"
```

---

## Task 4: Stage 2 methodology + prompt (documents)

**Why:** Plan 1 left `s2_requirements_qfd.md` as a 17-line outline. The stage2 LLM needs full method text (QFD-lite procedure, DFA evaluation rules, KC identification decision tree, risk register format) to produce useful output. The prompt file is a new artifact, parallel to `s1_intake.prompt.md`.

**Files:**
- Modify: `skills/aero-engine-assembly-scheme/methodology/s2_requirements_qfd.md` (full rewrite)
- Create: `skills/aero-engine-assembly-scheme/prompts/s2_requirements.prompt.md`

Pure documents. No failing test needed; commit after writing.

- [ ] **Step 4.1: Rewrite the methodology file**

Overwrite `skills/aero-engine-assembly-scheme/methodology/s2_requirements_qfd.md`:

````markdown
# S2: 需求与约束分析 — 方法论

## 目的

把陛下在 S1 提的模糊目标（"可靠性优先 / 工艺优化"）转换成可量化的指标体系，识别关键尺寸特征（KC），并用 DFA 评分定位现有结构的装配瓶颈。S2 的产物是 S3 概念架构和 S4 详细工艺的需求追溯源头。

## 核心方法

### 1. QFD-轻量法（三栏映射）

把 QFD 经典的 House of Quality 简化为三栏映射，避免在 v1 阶段陷入完整 HoQ 矩阵：

| 栏目 | 含义 | 编号约定 | 必填字段 |
|------|------|---------|---------|
| `user_needs` | 客户声音（VOC） | U1, U2, ... | text + weight (1-5) |
| `engineering_metrics` | 工程指标 | M1, M2, ... | name + target + linked_needs |
| `assembly_features` | 装配可控特征 | F1, F2, ... | name + spec + linked_metrics |

**链路约束**：每个 user_need 至少被一个 engineering_metric 覆盖；每个 metric 至少被一个 assembly_feature 落地。LLM 自检时若发现孤儿 need，必须新增 metric 或显式标注 `uncertainty: 高` 让陛下补。

### 2. DFA 评分（Boothroyd-Dewhurst 轻量版）

完整 BD-DFA 需要每个零件的"手动装配时间"和"可调整位置数"，v1 不引入数值打分明细。改用**比值简化版**：

- 理论最小零件数 `theoretical_min_parts`：满足产品功能所必需的零件数。判定准则：移除该件后系统是否仍能完成主功能、是否仍能保持几何完整性、是否需要拆装。三个回答都为"否"即可计入理论最小集合。
- 实际零件数 `actual_parts`：从 S1 `kg_snapshot.part_count` + chamberlain 输入提取。
- 总分 `overall = theoretical_min_parts / actual_parts`，范围 [0, 1]。`>= 0.7` 视为良好，`< 0.5` 视为需重设计。
- 瓶颈件 `bottlenecks`：DFA 中"装配时间显著高于均值"或"需要专用工装才能装入"的零件，列出 `part_id + issue`。瓶颈件不影响 overall 数值，仅用于 S3/S4a 提醒。

### 3. KC 识别（决策树）

对每个 `assembly_feature`，问以下问题：

1. 该特征的离散是否会导致 `engineering_metric` 直接不达标？→ 是：候选 KC
2. 该特征是否覆盖在外场不可检测/不可调整？→ 是：升级为 high criticality
3. 该特征的公差链是否跨 ≥ 3 个零件？→ 是：标注 `criticality: high` 且必须在 S4c 做 stack-up

每个 KC 必须有 `target`（区间或单边阈值）、`criticality ∈ {high, medium, low}`、可选 `linked_features`。

### 4. 风险登记

风险来自三个源头：

| 源头 | 形式 |
|------|------|
| KG 失效模式（若已入库 FMEA） | 直接复制为 risk 条目 |
| KC 反推 | 每个 high-criticality KC 必须有至少 1 条对应 risk |
| chamberlain 输入 | 可在 HITL 指导意见里手添 |

每条 risk 字段：`id (R1, R2, ...)` / `text` / `severity (1-5)` / `linked_kcs`。

## 常见陷阱

- ❌ 把模糊形容词当 metric（如 "提高可靠性"——必须给 target 数字或区间）
- ❌ KC 列表只抄 Spec §2.2 示例不结合 S1 subject —— LLM 易犯
- ❌ DFA 评分编造（虚报 theoretical_min_parts）—— Prompt 必须强调"不确定时给区间或标 uncertainty: 高"
- ❌ 把 Web 搜索结果当 metric target 直接复制（GJB 写"高可靠"是定性词，不是数字）

## 产物质量自检 checklist

- [ ] `stage1_ref` 与 S1 scheme_id 一致
- [ ] 每个 user_need 至少链到一个 metric（无孤儿）
- [ ] 每个 metric 至少链到一个 assembly_feature
- [ ] 每个 high-criticality KC 至少链到一个 assembly_feature 与一条 risk
- [ ] `dfa_score.overall` ∈ [0, 1]，且 `theoretical_min_parts <= actual_parts`
- [ ] `risks` 数组非空，severity 字段都是 1-5 整数
- [ ] LLM 不确定时显式给 `uncertainty: 高/中/低`，不杜撰数字

## 留待 v2 完善

- 完整 BD-DFA 装配时间表格（每件 manual handling time / insertion time）
- FMEA-MEDA 数据接入（从 KG 中按 `failureMode` 关系自动建 risk 表）
- 客户需求权重的 AHP 推导（v1 直接由 chamberlain 指定 1-5）
````

- [ ] **Step 4.2: Write the stage 2 prompt template**

Create `skills/aero-engine-assembly-scheme/prompts/s2_requirements.prompt.md`:

````markdown
# System

你是航空发动机装配工艺资深专家，正在执行装配方案设计 skill 的 **S2 阶段（需求与约束分析）**。

你的目标：基于 S1 任务说明书 + KG 快照 + Web 检索摘要，按 QFD-轻量法构建三栏映射，识别 KC，给出 DFA 评分，并登记风险清单。

## 必须遵守

1. 输出严格符合 `templates/schemas/stage2.schema.json` —— 这是 JSON 契约，缺字段或字段格式错误都会被 jsonschema.validate 拒绝
2. 每个 `engineering_metric.target` 必须是可测量的（数字 / 区间 / 阈值），不允许定性形容词
3. **每个 user_need 必须至少被一个 engineering_metric 覆盖**；每个 metric 必须至少被一个 assembly_feature 落地。LLM 自检时若发现孤儿，必须新增条目，不能留空
4. KC 识别按方法论决策树执行；每个 high-criticality KC 必须至少链到 1 个 assembly_feature 与 1 条 risk
5. `dfa_score.theoretical_min_parts` 不得超过 `actual_parts`；若理论数据不足，`uncertainty` 字段标 "高"
6. **绝不杜撰** PT6A 具体参数；不确定时显式 `uncertainty: 高`，等 chamberlain 在 HITL 里补
7. 引用文献用 `[ref:standard_id]` 或 `[ref:ws-N]`（来自 S1 web_search_results 的 id）

## 输入变量

- `stage1_payload`：S1 完整产物（含 subject、kg_snapshot、web_search_results、task_card_md、compliance_scope）
- `rag_methodology`：从 RAG 检索到的额外方法论片段（可能为空）
- `kg_failure_modes`：KG 中已入库的失效模式（可能为空）
- `user_guidance`：chamberlain 在 HITL 给的指导意见（可能为空）

## 方法论上下文

{{include: methodology/s2_requirements_qfd.md}}

## 输出格式

仅输出 JSON 对象，不要 markdown 代码块包裹。结构示例（值仅示意，不要照抄）：

```
{
  "stage1_ref": "{自动注入 S1 scheme_id}",
  "user_needs": [
    {"id": "U1", "text": "高可靠性", "weight": 5}
  ],
  "engineering_metrics": [
    {"id": "M1", "name": "MTBF", "target": ">= 4000 hrs", "linked_needs": ["U1"]}
  ],
  "assembly_features": [
    {"id": "F1", "name": "叶片装入扭矩一致性", "spec": "Cpk >= 1.33", "linked_metrics": ["M1"]}
  ],
  "key_characteristics": [
    {"id": "KC1", "name": "叶尖间隙", "target": "0.5-1.0 mm", "criticality": "high", "linked_features": ["F1"]}
  ],
  "dfa_score": {
    "overall": 0.72,
    "theoretical_min_parts": 25,
    "actual_parts": 35,
    "method": "Boothroyd-Dewhurst (lightweight)",
    "bottlenecks": [
      {"part_id": "P012", "name": "...", "issue": "..."}
    ]
  },
  "risks": [
    {"id": "R1", "text": "...", "severity": 4, "linked_kcs": ["KC1"]}
  ],
  "uncertainty": "低"
}
```

## Few-shot（PT6A HPC v1 范例）

输入 stage1_payload 中 subject 为 `PT6A 高压压气机`，输出参 `templates/golden/pt6a_hpc_stage2.json`（同目录），重点观察：
- 4 条 user_need 对应 4 个 engineering_metric
- 4 个 KC 都有 criticality 字段，3 条 risk 与 KC 互相链回
- `dfa_score.overall = 25/35 ≈ 0.71`，存在 2 个瓶颈件
- `uncertainty` 给 "中"，表明部分参数来自手册而非内部数据

## 反模式（禁止）

- ❌ engineering_metric.target 写 "高可靠性"、"较好"、"优于现有"——必须是数字
- ❌ KC 不写 target——所有 KC 必须有可测量 target
- ❌ dfa_score 缺 theoretical_min_parts 或 actual_parts
- ❌ stage1_ref 改成自己生成的 id
- ❌ 把 Web 搜索结果中的概括语原文塞到 metric.target
````

- [ ] **Step 4.3: Sanity test — reload SkillRegistry and check the two files are picked up**

Quick interactive check (no new pytest needed; the existing `test_skill_loader.py` already exercises this glob pattern):

`pytest tests/assembly/test_skill_loader.py -v`
Expected: tests that count methodology files and prompt files should now find one more prompt (`s2_requirements`). If a test hard-codes `len(prompts) == 1`, update it to `>= 2`. Find it with: Grep pattern `len(.*prompts)` in `tests/assembly`.

- [ ] **Step 4.4: Commit**

```bash
git add skills/aero-engine-assembly-scheme/methodology/s2_requirements_qfd.md \
        skills/aero-engine-assembly-scheme/prompts/s2_requirements.prompt.md \
        tests/assembly/test_skill_loader.py
git commit -m "feat(assembly): full S2 methodology (QFD/DFA/KC/risks) and s2 prompt template"
```

---

## Task 5: Implement `run_stage2_requirements` (TDD)

**Why:** Stage 2 needs its own pipeline file mirroring `stage1_intake.py`'s shape. Inputs are the stage1 dict + skill + llm + optional rag/kg helpers; output is a dict satisfying stage2 schema. Same degradation philosophy: LLM=None returns a minimal placeholder that still validates against schema.

**Files:**
- Create: `backend/pipelines/assembly_scheme/stage2_requirements.py`
- Create: `tests/assembly/test_stage2_requirements.py`

- [ ] **Step 5.1: Write the failing tests**

Create `tests/assembly/test_stage2_requirements.py`:

```python
"""Tests for backend.pipelines.assembly_scheme.stage2_requirements.run_stage2_requirements."""
from pathlib import Path
from unittest.mock import MagicMock
import json
import pytest
import jsonschema

from backend.pipelines.assembly_scheme.stage2_requirements import (
    run_stage2_requirements,
    PLACEHOLDER_STAGE2,
)
from backend.pipelines.assembly_scheme.skill_loader import SkillRegistry

SKILL_ROOT = Path(__file__).resolve().parents[2] / "skills" / "aero-engine-assembly-scheme"


@pytest.fixture(scope="module")
def loaded_skill():
    reg = SkillRegistry(SKILL_ROOT)
    reg.load()
    return reg


@pytest.fixture
def sample_stage1():
    return {
        "scheme_id": "scheme-20260511-aaaaaa",
        "subject": {
            "system": "PT6A 高压压气机",
            "system_en": "PT6A HPC",
            "scope": ["3 级轴流"],
            "design_intent": "工艺优化",
            "constraints": {"primary": "可靠性", "secondary": "维修性"},
        },
        "kg_snapshot": {
            "part_count": 35,
            "assembly_count": 13,
            "key_interfaces": [],
            "relations_sample": ["isPartOf", "matesWith"],
        },
        "web_search_results": [],
        "vision_notes": "",
        "compliance_scope": ["AS9100D §8.1"],
        "task_card_md": "## 任务说明书\n**目标**：测试\n**范围**：测试\n**边界**：测试\n**约束**：测试\n**已知风险**：测试",
    }


# ── degradation: no LLM, no RAG, no KG ───────────────────────────────────────

def test_run_stage2_no_llm_returns_placeholder(loaded_skill, sample_stage1):
    """When llm_client is None, return a placeholder that still validates against schema."""
    result = run_stage2_requirements(
        stage1_payload=sample_stage1,
        skill=loaded_skill,
        llm_client=None,
        rag_searcher=None,
        neo4j_driver=None,
    )
    schema = loaded_skill.schemas["stage2"]
    jsonschema.validate(instance=result, schema=schema)
    assert result["stage1_ref"] == sample_stage1["scheme_id"]
    assert result["user_needs"]  # non-empty
    assert result.get("uncertainty") == "高"  # placeholder is high-uncertainty


# ── LLM happy path ───────────────────────────────────────────────────────────

def test_run_stage2_with_llm_uses_response(loaded_skill, sample_stage1):
    """When LLM returns valid JSON, that JSON wins."""
    mock_resp = {
        "stage1_ref": sample_stage1["scheme_id"],
        "user_needs": [{"id": "U1", "text": "可靠", "weight": 5}],
        "engineering_metrics": [{"id": "M1", "name": "MTBF", "target": ">= 4000h", "linked_needs": ["U1"]}],
        "assembly_features": [{"id": "F1", "name": "扭矩一致", "spec": "Cpk>=1.33", "linked_metrics": ["M1"]}],
        "key_characteristics": [{"id": "KC1", "name": "叶尖间隙", "target": "0.5-1.0 mm", "criticality": "high", "linked_features": ["F1"]}],
        "dfa_score": {"overall": 0.7, "theoretical_min_parts": 25, "actual_parts": 35, "bottlenecks": []},
        "risks": [{"id": "R1", "text": "碰摩", "severity": 4, "linked_kcs": ["KC1"]}],
        "uncertainty": "低",
    }
    mock_llm = MagicMock()
    mock_llm.chat.completions.create.return_value.choices[0].message.content = json.dumps(
        mock_resp, ensure_ascii=False
    )

    result = run_stage2_requirements(
        stage1_payload=sample_stage1,
        skill=loaded_skill,
        llm_client=mock_llm,
        rag_searcher=None,
        neo4j_driver=None,
    )
    jsonschema.validate(instance=result, schema=loaded_skill.schemas["stage2"])
    assert result["user_needs"][0]["text"] == "可靠"
    mock_llm.chat.completions.create.assert_called_once()


# ── LLM returns malformed JSON → fallback to placeholder ─────────────────────

def test_run_stage2_llm_returns_garbage_falls_back(loaded_skill, sample_stage1):
    """When LLM output isn't valid JSON or doesn't satisfy schema, fall back to placeholder."""
    mock_llm = MagicMock()
    mock_llm.chat.completions.create.return_value.choices[0].message.content = "not json at all"
    result = run_stage2_requirements(
        stage1_payload=sample_stage1,
        skill=loaded_skill,
        llm_client=mock_llm,
        rag_searcher=None,
        neo4j_driver=None,
    )
    jsonschema.validate(instance=result, schema=loaded_skill.schemas["stage2"])
    assert result.get("uncertainty") == "高"


# ── stage1_ref correctly carries through ─────────────────────────────────────

def test_run_stage2_overrides_stage1_ref_even_if_llm_returns_wrong_id(loaded_skill, sample_stage1):
    """The pipeline must enforce stage1_ref == stage1.scheme_id regardless of what LLM said."""
    bad_resp = {
        "stage1_ref": "scheme-20260101-deadbeef",  # WRONG on purpose
        "user_needs": [{"id": "U1", "text": "x", "weight": 1}],
        "engineering_metrics": [{"id": "M1", "name": "x", "target": ">=1", "linked_needs": ["U1"]}],
        "assembly_features": [{"id": "F1", "name": "x", "spec": "x", "linked_metrics": ["M1"]}],
        "key_characteristics": [{"id": "KC1", "name": "x", "target": "x", "criticality": "low", "linked_features": ["F1"]}],
        "dfa_score": {"overall": 0.5, "theoretical_min_parts": 1, "actual_parts": 2, "bottlenecks": []},
        "risks": [{"id": "R1", "text": "x", "severity": 1, "linked_kcs": ["KC1"]}],
    }
    mock_llm = MagicMock()
    mock_llm.chat.completions.create.return_value.choices[0].message.content = json.dumps(bad_resp, ensure_ascii=False)
    result = run_stage2_requirements(
        stage1_payload=sample_stage1,
        skill=loaded_skill,
        llm_client=mock_llm,
        rag_searcher=None,
        neo4j_driver=None,
    )
    assert result["stage1_ref"] == sample_stage1["scheme_id"]


# ── placeholder is itself a valid stage2 ─────────────────────────────────────

def test_placeholder_validates_against_schema(loaded_skill, sample_stage1):
    """The static PLACEHOLDER_STAGE2 (with stage1_ref injected) is a valid stage2 object."""
    p = dict(PLACEHOLDER_STAGE2)
    p["stage1_ref"] = sample_stage1["scheme_id"]
    jsonschema.validate(instance=p, schema=loaded_skill.schemas["stage2"])
```

- [ ] **Step 5.2: Run tests, confirm import error / all fail**

`pytest tests/assembly/test_stage2_requirements.py -v`
Expected: 5 ERROR — `stage2_requirements` module doesn't exist.

- [ ] **Step 5.3: Implement `run_stage2_requirements`**

Create `backend/pipelines/assembly_scheme/stage2_requirements.py`:

```python
"""
backend/pipelines/assembly_scheme/stage2_requirements.py

S2: Requirements & constraints analysis. See spec §2.2.

Steps:
  1. Optionally call rag_searcher for extra methodology snippets
  2. Optionally query KG for historic failure modes (kg_failure_modes)
  3. Build LLM prompt = skill.prompts['s2_requirements'] + methodology + stage1 payload
  4. Call LLM, parse JSON, validate against stage2 schema
  5. If LLM is None / response unparseable / response invalid → return PLACEHOLDER_STAGE2
  6. Always enforce stage1_ref = stage1.scheme_id (so a wrong LLM id gets overwritten)
"""

from __future__ import annotations

from typing import Any, Dict, Optional
import json
import logging

import jsonschema

from backend.pipelines.assembly_scheme.skill_loader import SkillRegistry

logger = logging.getLogger(__name__)


PLACEHOLDER_STAGE2: Dict[str, Any] = {
    "stage1_ref": "PLACEHOLDER",
    "user_needs": [
        {"id": "U1", "text": "（占位：高可靠性，待 chamberlain 补全）", "weight": 5}
    ],
    "engineering_metrics": [
        {"id": "M1", "name": "MTBF", "target": "（占位：待补具体数字）", "linked_needs": ["U1"]}
    ],
    "assembly_features": [
        {"id": "F1", "name": "（占位）关键装配特征", "spec": "（占位）", "linked_metrics": ["M1"]}
    ],
    "key_characteristics": [
        {"id": "KC1", "name": "（占位）关键尺寸", "target": "（占位）", "criticality": "high", "linked_features": ["F1"]}
    ],
    "dfa_score": {
        "overall": 0.5,
        "theoretical_min_parts": 1,
        "actual_parts": 1,
        "method": "placeholder",
        "bottlenecks": []
    },
    "risks": [
        {"id": "R1", "text": "（占位）需要 chamberlain 在 HITL 补具体风险", "severity": 3, "linked_kcs": ["KC1"]}
    ],
    "uncertainty": "高"
}


def _build_prompt(skill: SkillRegistry, stage1_payload: Dict[str, Any],
                  rag_methodology: str, kg_failure_modes: list,
                  user_guidance: Optional[str]) -> str:
    prompt_template = skill.prompts.get("s2_requirements", "")
    methodology = skill.methodology.get("s2_requirements_qfd", "")
    return (
        f"{prompt_template}\n\n"
        f"## 方法论上下文\n{methodology}\n\n"
        f"## 额外 RAG 方法论片段\n{rag_methodology or '（无）'}\n\n"
        f"## KG 失效模式（历史）\n{json.dumps(kg_failure_modes, ensure_ascii=False, indent=2)}\n\n"
        f"## S1 产物\n```json\n{json.dumps(stage1_payload, ensure_ascii=False, indent=2)}\n```\n\n"
        f"## chamberlain 指导意见\n{user_guidance or '（无）'}\n\n"
        "请生成符合 stage2.schema.json 的 JSON 对象："
    )


def _query_failure_modes(neo4j_driver: Any, subject_name: str) -> list:
    """Best-effort lookup; returns [] on any failure."""
    if neo4j_driver is None:
        return []
    cypher = (
        "MATCH (p)-[:failureMode]->(f) "
        "WHERE coalesce(p.kg_name, '') CONTAINS $subj OR coalesce(p.part_name, '') CONTAINS $subj "
        "RETURN f.text AS text, f.severity AS severity LIMIT 10"
    )
    try:
        with neo4j_driver.session() as session:
            records = session.run(cypher, subj=subject_name).data()
            return records
    except Exception as e:
        logger.warning("KG failure-mode query failed: %s", e)
        return []


def _call_llm(llm_client: Any, prompt: str) -> Optional[str]:
    if llm_client is None:
        return None
    try:
        resp = llm_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        return resp.choices[0].message.content
    except Exception as e:
        logger.error("Stage2 LLM call failed: %s", e)
        return None


def _parse_and_validate(raw: str, schema: dict) -> Optional[Dict[str, Any]]:
    """Parse LLM JSON output and validate against schema. Return None on any failure."""
    try:
        # Tolerate ```json ... ``` fencing even though prompt forbids it
        s = raw.strip()
        if s.startswith("```"):
            s = s.strip("`")
            if s.lower().startswith("json\n"):
                s = s[5:]
        obj = json.loads(s)
    except json.JSONDecodeError as e:
        logger.warning("Stage2 LLM JSON parse failed: %s; raw=%s", e, raw[:200])
        return None
    try:
        jsonschema.validate(instance=obj, schema=schema)
    except jsonschema.ValidationError as e:
        logger.warning("Stage2 LLM output failed schema: %s", e.message)
        return None
    return obj


def run_stage2_requirements(
    stage1_payload: Dict[str, Any],
    skill: SkillRegistry,
    llm_client: Any,
    rag_searcher: Any = None,
    neo4j_driver: Any = None,
    user_guidance: Optional[str] = None,
) -> Dict[str, Any]:
    """Execute S2 pipeline. Returns a dict valid per stage2.schema.json."""
    schema = skill.schemas["stage2"]
    scheme_id = stage1_payload["scheme_id"]

    rag_methodology = ""
    if rag_searcher is not None:
        try:
            hits = rag_searcher.search("装配可靠性 指标 QFD", top_k=3)
            rag_methodology = "\n---\n".join(h.get("text", "") for h in hits)
        except Exception as e:
            logger.warning("Stage2 RAG search failed: %s", e)

    failure_modes = _query_failure_modes(neo4j_driver, stage1_payload["subject"]["system"])

    prompt = _build_prompt(skill, stage1_payload, rag_methodology, failure_modes, user_guidance)
    raw = _call_llm(llm_client, prompt)
    parsed = _parse_and_validate(raw, schema) if raw else None

    if parsed is None:
        result = json.loads(json.dumps(PLACEHOLDER_STAGE2, ensure_ascii=False))  # deep copy
        result["stage1_ref"] = scheme_id
        return result

    # Enforce stage1_ref linkage even if LLM lied
    parsed["stage1_ref"] = scheme_id
    return parsed
```

- [ ] **Step 5.4: Run tests, confirm all pass**

`pytest tests/assembly/test_stage2_requirements.py -v`
Expected: 5 PASS.

- [ ] **Step 5.5: Run full assembly suite to ensure no regression**

`pytest tests/assembly/ -v`
Expected: all green.

- [ ] **Step 5.6: Commit**

```bash
git add backend/pipelines/assembly_scheme/stage2_requirements.py \
        tests/assembly/test_stage2_requirements.py
git commit -m "feat(assembly): implement run_stage2_requirements (QFD+DFA+KC) with graceful degradation"
```

---

## Task 6: Activate stage 2 route (TDD)

**Why:** Currently `POST /scheme/{id}/stage/2` returns HTTP 501. Wire it to `run_stage2_requirements`. Stage 2 requires that stage 1 was already run (its output lives in `stage1.json` on disk).

**Files:**
- Modify: `backend/routers/assembly_design.py` (run_stage dispatch)
- Modify: `tests/assembly/test_assembly_design_router.py` (3 new cases)

- [ ] **Step 6.1: Add failing router tests**

Append to `tests/assembly/test_assembly_design_router.py`:

```python
def test_stage2_requires_stage1_first(client):
    """POST /stage/2 must 409 if stage1 has not been run yet."""
    create_resp = client.post(
        "/assembly-design/scheme/new",
        json={
            "subject_system": "PT6A HPC",
            "subject_scope": ["3 级轴流"],
            "design_intent": "工艺优化",
            "constraints": {"primary": "可靠性"},
        },
    )
    scheme_id = create_resp.json()["scheme_id"]

    resp = client.post(
        f"/assembly-design/scheme/{scheme_id}/stage/2",
        json={"action": "generate", "payload": {}},
    )
    assert resp.status_code == 409, resp.text
    assert "stage1" in resp.text.lower()


def test_stage2_runs_after_stage1(client):
    """Happy path: create scheme → run stage1 → run stage2 → fetch and see both."""
    create_resp = client.post(
        "/assembly-design/scheme/new",
        json={
            "subject_system": "PT6A HPC",
            "subject_scope": ["3 级轴流"],
            "design_intent": "工艺优化",
            "constraints": {"primary": "可靠性"},
        },
    )
    scheme_id = create_resp.json()["scheme_id"]

    r1 = client.post(
        f"/assembly-design/scheme/{scheme_id}/stage/1",
        json={"action": "generate", "payload": {}},
    )
    assert r1.status_code == 200, r1.text

    r2 = client.post(
        f"/assembly-design/scheme/{scheme_id}/stage/2",
        json={"action": "generate", "payload": {}},
    )
    assert r2.status_code == 200, r2.text
    body = r2.json()
    assert "user_needs" in body
    assert "dfa_score" in body
    assert body["stage1_ref"] == scheme_id

    final = client.get(f"/assembly-design/scheme/{scheme_id}").json()
    assert "stage1" in final
    assert "stage2" in final
    assert "2" in final["meta"]["stages_done"]


def test_stage2_save_edits(client):
    """save_edits action writes payload verbatim, no LLM call."""
    create_resp = client.post(
        "/assembly-design/scheme/new",
        json={
            "subject_system": "PT6A HPC",
            "subject_scope": ["3 级轴流"],
            "design_intent": "工艺优化",
            "constraints": {"primary": "可靠性"},
        },
    )
    scheme_id = create_resp.json()["scheme_id"]
    client.post(
        f"/assembly-design/scheme/{scheme_id}/stage/1",
        json={"action": "generate", "payload": {}},
    )
    edited = {
        "stage1_ref": scheme_id,
        "user_needs": [{"id": "U99", "text": "陛下手改", "weight": 5}],
        "engineering_metrics": [{"id": "M99", "name": "X", "target": ">=1", "linked_needs": ["U99"]}],
        "assembly_features": [{"id": "F99", "name": "X", "spec": "X", "linked_metrics": ["M99"]}],
        "key_characteristics": [{"id": "KC99", "name": "X", "target": "X", "criticality": "low", "linked_features": ["F99"]}],
        "dfa_score": {"overall": 0.5, "theoretical_min_parts": 1, "actual_parts": 1, "bottlenecks": []},
        "risks": [{"id": "R99", "text": "X", "severity": 1, "linked_kcs": ["KC99"]}],
    }
    r = client.post(
        f"/assembly-design/scheme/{scheme_id}/stage/2",
        json={"action": "save_edits", "payload": edited},
    )
    assert r.status_code == 200, r.text
    final = client.get(f"/assembly-design/scheme/{scheme_id}").json()
    assert final["stage2"]["user_needs"][0]["id"] == "U99"
```

- [ ] **Step 6.2: Run, confirm 3 fail**

`pytest tests/assembly/test_assembly_design_router.py -v -k stage2`
Expected: 3 FAIL (all return 501).

- [ ] **Step 6.3: Update the router dispatch**

In `backend/routers/assembly_design.py`, modify the `run_stage` function. Two changes: (1) import `run_stage2_requirements`; (2) add stage_key=="2" branch.

Add import near the top, next to the existing `run_stage1_intake` import:

```python
from backend.pipelines.assembly_scheme.stage1_intake import run_stage1_intake
from backend.pipelines.assembly_scheme.stage2_requirements import run_stage2_requirements
```

Replace the existing `if stage_key != "1": raise HTTPException(501, ...)` gate with proper dispatch. The full updated `run_stage` body (inside the existing `with state.assembly_lock:` from Task 2):

```python
@router.post("/scheme/{scheme_id}/stage/{stage_key}")
def run_stage(scheme_id: str, stage_key: str, req: StageRequest, state=Depends(get_state)):
    if stage_key not in VALID_STAGE_KEYS:
        raise HTTPException(400, f"invalid stage_key: {stage_key}")

    sd = _scheme_dir(scheme_id)
    if not sd.exists():
        raise HTTPException(404, f"scheme not found: {scheme_id}")

    # Stages not implemented yet
    if stage_key in {"3", "4a", "4b", "4c", "4d", "5"}:
        raise HTTPException(501, f"stage {stage_key} not implemented in Plan 2")

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
                rag_searcher=None,         # Plan 3 will wire QdrantDualPathRetriever here
                neo4j_driver=state.neo4j_driver,
                user_guidance=req.user_guidance,
            )

        # stage_key "3" and beyond handled by the early HTTP 501 above

        stage_path.write_text(
            json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        if stage_key not in meta["stages_done"]:
            meta["stages_done"].append(stage_key)
            _write_meta(scheme_id, meta)
        return result
```

Note: also note we added `meta["stages_done"]` update inside the `save_edits` branch — that's a small behavior change (save_edits used not to update stages_done). It's the right behavior: if chamberlain edits stage 2 manually without ever calling generate, the meta should still reflect that stage 2 exists. The Task 6 test_stage2_save_edits relies on this.

- [ ] **Step 6.4: Run tests, confirm all 3 pass**

`pytest tests/assembly/test_assembly_design_router.py -v -k stage2`
Expected: 3 PASS.

- [ ] **Step 6.5: Run full suite**

`pytest tests/assembly/ -v`
Expected: all green.

- [ ] **Step 6.6: Commit**

```bash
git add backend/routers/assembly_design.py tests/assembly/test_assembly_design_router.py
git commit -m "feat(assembly): activate /scheme/{id}/stage/2 endpoint (requires stage1 first)"
```

---

# Phase 2: Stage 3 (Concept Architecture)

## Task 7: Stage 3 schema + golden example (TDD)

**Why:** Spec §2.3 needs `candidate_architectures` with each entry holding `modules` / `key_interfaces` / `assembly_simulation` / `datum_consistency` / `pros` / `cons` / `fit_score_to_metrics`. The current placeholder declares only the top-level `candidate_architectures`, `recommended`, `rationale_md` shells. Same as Task 3: full schema + PT6A HPC golden.

**Files:**
- Modify: `skills/aero-engine-assembly-scheme/templates/schemas/stage3.schema.json`
- Create: `skills/aero-engine-assembly-scheme/templates/golden/pt6a_hpc_stage3.json`
- Modify: `tests/assembly/test_schemas.py`

- [ ] **Step 7.1: Add failing schema + golden tests**

Append to `tests/assembly/test_schemas.py`:

```python
def test_stage3_schema_requires_arch_internals():
    """stage3 schema must require deep architecture fields, not just the array."""
    import json
    from pathlib import Path
    schema = json.loads(
        Path("skills/aero-engine-assembly-scheme/templates/schemas/stage3.schema.json")
        .read_text(encoding="utf-8")
    )
    required = set(schema["required"])
    for key in ["stage1_ref", "stage2_ref", "candidate_architectures", "recommended", "rationale_md"]:
        assert key in required, f"stage3 must require '{key}'"

    arch_schema = schema["properties"]["candidate_architectures"]["items"]
    arch_required = set(arch_schema["required"])
    for key in ["id", "name", "modules", "key_interfaces", "assembly_simulation",
                "datum_consistency", "pros", "cons", "fit_score_to_metrics"]:
        assert key in arch_required, f"each architecture must require '{key}'"

    # candidate_architectures must have minItems >= 2 (spec: "concept design needs alternatives")
    assert schema["properties"]["candidate_architectures"].get("minItems", 0) >= 2


def test_pt6a_hpc_stage3_golden_validates():
    """The golden PT6A HPC stage3 example must satisfy stage3 schema."""
    import json
    import jsonschema
    from pathlib import Path
    schema = json.loads(
        Path("skills/aero-engine-assembly-scheme/templates/schemas/stage3.schema.json")
        .read_text(encoding="utf-8")
    )
    golden = json.loads(
        Path("skills/aero-engine-assembly-scheme/templates/golden/pt6a_hpc_stage3.json")
        .read_text(encoding="utf-8")
    )
    jsonschema.validate(instance=golden, schema=schema)
```

- [ ] **Step 7.2: Run, confirm both fail**

`pytest tests/assembly/test_schemas.py -v -k stage3`
Expected: 2 FAIL.

- [ ] **Step 7.3: Write full stage3 schema**

Overwrite `skills/aero-engine-assembly-scheme/templates/schemas/stage3.schema.json`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "stage3.schema.json",
  "title": "Stage 3 — Concept Architecture",
  "type": "object",
  "required": ["stage1_ref", "stage2_ref", "candidate_architectures", "recommended", "rationale_md"],
  "properties": {
    "stage1_ref": {"type": "string", "pattern": "^scheme-[0-9]{8}-[a-f0-9]{6}$"},
    "stage2_ref": {"type": "string", "pattern": "^scheme-[0-9]{8}-[a-f0-9]{6}$"},
    "candidate_architectures": {
      "type": "array",
      "minItems": 2,
      "items": {
        "type": "object",
        "required": ["id", "name", "modules", "key_interfaces", "assembly_simulation",
                     "datum_consistency", "pros", "cons", "fit_score_to_metrics"],
        "properties": {
          "id": {"type": "string", "pattern": "^A[0-9]+$"},
          "name": {"type": "string", "minLength": 1},
          "modules": {
            "type": "array",
            "minItems": 1,
            "items": {
              "type": "object",
              "required": ["id", "name", "parts"],
              "properties": {
                "id": {"type": "string", "pattern": "^M[0-9]+$"},
                "name": {"type": "string", "minLength": 1},
                "parts": {
                  "type": "array",
                  "items": {"type": "string"},
                  "minItems": 1
                }
              }
            }
          },
          "key_interfaces": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["from", "to", "type"],
              "properties": {
                "from": {"type": "string"},
                "to": {"type": "string"},
                "type": {"type": "string", "minLength": 1}
              }
            }
          },
          "assembly_simulation": {
            "type": "object",
            "required": ["reachability_pass", "interference_count", "method"],
            "properties": {
              "reachability_pass": {"type": "boolean"},
              "interference_count": {"type": "integer", "minimum": 0},
              "method": {"type": "string", "enum": ["KG-static", "CAD-occ", "hybrid", "placeholder"]},
              "notes": {"type": "string"}
            }
          },
          "datum_consistency": {
            "type": "object",
            "required": ["unified", "issues"],
            "properties": {
              "unified": {"type": "boolean"},
              "issues": {
                "type": "array",
                "items": {"type": "string"}
              }
            }
          },
          "pros": {
            "type": "array",
            "minItems": 1,
            "items": {"type": "string", "minLength": 1}
          },
          "cons": {
            "type": "array",
            "items": {"type": "string"}
          },
          "fit_score_to_metrics": {"type": "number", "minimum": 0, "maximum": 1}
        }
      }
    },
    "recommended": {"type": "string", "pattern": "^A[0-9]+$"},
    "rationale_md": {"type": "string", "minLength": 1},
    "uncertainty": {"type": "string", "enum": ["高", "中", "低"]}
  }
}
```

- [ ] **Step 7.4: Run schema-only test, confirm PASS; golden test still FAIL**

`pytest tests/assembly/test_schemas.py::test_stage3_schema_requires_arch_internals -v`
Expected: PASS.

- [ ] **Step 7.5: Write the PT6A HPC stage3 golden**

Create `skills/aero-engine-assembly-scheme/templates/golden/pt6a_hpc_stage3.json`:

```json
{
  "stage1_ref": "scheme-20260508-a1b2c3",
  "stage2_ref": "scheme-20260508-a1b2c3",
  "candidate_architectures": [
    {
      "id": "A1",
      "name": "三段分体式（前段静子 / 转子段 / 后段静子）",
      "modules": [
        {"id": "M1", "name": "前段静子组件", "parts": ["P001", "P002", "P003", "P004"]},
        {"id": "M2", "name": "转子组件 (含 3 级轴流盘 + 1 级离心叶轮)", "parts": ["P010", "P011", "P012", "P013"]},
        {"id": "M3", "name": "后段静子与轴承支撑", "parts": ["P020", "P021", "P022"]},
        {"id": "M4", "name": "外机匣组件", "parts": ["P030", "P031"]}
      ],
      "key_interfaces": [
        {"from": "M1", "to": "M2", "type": "径向间隙配合 + 轴向定位面"},
        {"from": "M2", "to": "M3", "type": "法兰螺栓 + 定位销"},
        {"from": "M4", "to": "M1", "type": "外机匣前端法兰"},
        {"from": "M4", "to": "M3", "type": "外机匣后端法兰"}
      ],
      "assembly_simulation": {
        "reachability_pass": true,
        "interference_count": 0,
        "method": "KG-static",
        "notes": "基于 KG isPartOf + matesWith 的静态可达性分析；CAD 干涉检查留待 v2"
      },
      "datum_consistency": {
        "unified": true,
        "issues": []
      },
      "pros": [
        "拆装方便，外场可单段更换",
        "三段独立可分别送修",
        "工序流转明晰"
      ],
      "cons": [
        "前段法兰应力集中风险",
        "三段需 4 处法兰螺栓，紧固件件数偏多"
      ],
      "fit_score_to_metrics": 0.82
    },
    {
      "id": "A2",
      "name": "整体压力外壳 + 内部分级模块",
      "modules": [
        {"id": "M1", "name": "整体外机匣（含前后法兰一体）", "parts": ["P030", "P031", "P032"]},
        {"id": "M2", "name": "转子组件", "parts": ["P010", "P011", "P012", "P013"]},
        {"id": "M3", "name": "静子叶片组（轴向 + 离心）", "parts": ["P001", "P002", "P003", "P020", "P021"]}
      ],
      "key_interfaces": [
        {"from": "M1", "to": "M3", "type": "内壁榫槽 + 锁紧环"},
        {"from": "M3", "to": "M2", "type": "径向间隙配合"}
      ],
      "assembly_simulation": {
        "reachability_pass": true,
        "interference_count": 1,
        "method": "KG-static",
        "notes": "整体外机匣下，静子叶片组装入需要从前端逐排穿入，KG matesWith 显示存在 1 处轴向干涉风险（待 CAD 复核）"
      },
      "datum_consistency": {
        "unified": false,
        "issues": ["静子叶片组的工艺基准（M3 端面）与装配基准（M1 内壁）不一致"]
      },
      "pros": [
        "零件总数下降",
        "压力密封性优于分体式"
      ],
      "cons": [
        "外场维修困难，需整体返厂",
        "基准不统一带来公差链放大",
        "存在装入干涉风险"
      ],
      "fit_score_to_metrics": 0.58
    },
    {
      "id": "A3",
      "name": "两段式（前后段，转子作为独立装配单元）",
      "modules": [
        {"id": "M1", "name": "前段（含前静子 + 外机匣前半）", "parts": ["P001", "P002", "P003", "P030"]},
        {"id": "M2", "name": "转子组件（独立动平衡）", "parts": ["P010", "P011", "P012", "P013"]},
        {"id": "M3", "name": "后段（含后静子 + 外机匣后半 + 支撑）", "parts": ["P020", "P021", "P022", "P031"]}
      ],
      "key_interfaces": [
        {"from": "M1", "to": "M2", "type": "径向间隙 + 轴承内圈定位"},
        {"from": "M2", "to": "M3", "type": "径向间隙 + 轴承外圈定位"},
        {"from": "M1", "to": "M3", "type": "中分面法兰螺栓"}
      ],
      "assembly_simulation": {
        "reachability_pass": true,
        "interference_count": 0,
        "method": "KG-static",
        "notes": "前后段 + 独立转子三件装配，转子先动平衡再装入，KG 可达性满分"
      },
      "datum_consistency": {
        "unified": true,
        "issues": []
      },
      "pros": [
        "转子动平衡独立，与机匣解耦",
        "中分面少（仅 1 处法兰）",
        "维修拆装路径短"
      ],
      "cons": [
        "中分面法兰承载所有轴向力，紧固件设计要求高",
        "前段集成度高，单件成本上升"
      ],
      "fit_score_to_metrics": 0.78
    }
  ],
  "recommended": "A1",
  "rationale_md": "推荐 **A1 三段分体式**：\n\n- **可靠性（M1=MTBF）**：三段独立动平衡 + 法兰带定位销，工艺成熟，与 PT6A 系列既有装配经验一致 [ref:ws-pwc-cmm]\n- **维修性（M2=MTTR）**：A1 与 A3 都满足 8 hrs 外场更换，但 A1 三段路径短，平均节省 1 hr\n- **基准统一性**：A1、A3 都 unified；A2 不 unified，直接 PASS\n- **装配可达性**：A1、A3 均 0 干涉；A2 存在 1 处需 CAD 复核\n- **fit_score 排序**：A1 (0.82) > A3 (0.78) > A2 (0.58)\n\nA3 作为强备选保留：若 chamberlain 在 HITL 强调\"中分面少 = 密封风险低\"，可切换。\n\n**不推荐 A2**：基准不统一 + 干涉风险 + 维修性差，三票否决。",
  "uncertainty": "中"
}
```

- [ ] **Step 7.6: Run both schema tests, confirm both PASS**

`pytest tests/assembly/test_schemas.py -v -k stage3`
Expected: 2 PASS.

- [ ] **Step 7.7: Commit**

```bash
git add skills/aero-engine-assembly-scheme/templates/schemas/stage3.schema.json \
        skills/aero-engine-assembly-scheme/templates/golden/pt6a_hpc_stage3.json \
        tests/assembly/test_schemas.py
git commit -m "feat(assembly): full stage3 schema (multi-architecture + reachability + datum) and PT6A HPC golden"
```

---

## Task 8: Stage 3 methodology + prompt (documents)

**Why:** Same shape as Task 4 but for S3. Function-to-structure mapping, assembly tree derivation, reachability heuristics, datum unification checklist.

**Files:**
- Modify: `skills/aero-engine-assembly-scheme/methodology/s3_concept_architecture.md`
- Create: `skills/aero-engine-assembly-scheme/prompts/s3_concept.prompt.md`

- [ ] **Step 8.1: Rewrite the methodology**

Overwrite `skills/aero-engine-assembly-scheme/methodology/s3_concept_architecture.md`:

````markdown
# S3: 概念 / 架构设计 — 方法论

## 目的

在 S2 指标与 KC 约束下，给出 **2-5 个备选概念架构**，每个含模块划分 + 关键接口 + 装配仿真预检 + 基准统一性审查 + 利弊。给出推荐项及理由。

S3 是从"我想要什么"到"系统长什么样"的关键跃迁。多备选是硬性要求——单一架构等于没做概念设计。

## 核心方法

### 1. 功能-结构映射

把 S2 的 `engineering_metrics` 当作功能需求列表，映射到物理结构：

| S2 source | 映射到 S3 字段 |
|-----------|--------------|
| `engineering_metrics.target` | 倒推该指标依赖的物理特征（如 MTBF→可单独更换的模块） |
| `assembly_features.spec` | 决定模块边界（同一 spec 内的零件归同一模块） |
| `key_characteristics.criticality:high` | 必须有独立装配检验工序 → 影响模块划分 |
| `risks.linked_kcs` | 决定关键接口的设计权重 |

### 2. 装配树推导（KG 驱动）

利用本地 KG 的 `isPartOf` / `matesWith` / `adjacentTo` 三种关系：

- **`isPartOf` 树**：直接给出现有模块拓扑——这是 baseline
- **`matesWith` 簇**：用图聚类（弱连接率 < 30%）切割得到候选模块边界
- **`adjacentTo` 链**：辅助识别装配顺序约束（不影响划分本身）

LLM 应基于 KG 输出 **多个**（≥ 2）切割方案。若 KG 中实体数 < 5，可标 `uncertainty: 高` 并给一个 baseline + 一个变体。

### 3. 装配仿真预检（v1 简化版）

V1 不接 DELMIA / Process Simulate，用**静态可达性 + 接口冲突计数**两个指标：

#### 可达性 `reachability_pass`（boolean）

判定规则：对每个模块 M，存在至少一条装配路径，使得 M 在被装入时其所有 `matesWith` 已就位的模块都不阻挡装入方向（轴向 / 径向之一）。判定时取 KG 中的 `matesWith` 关系当作硬约束。Pass = 所有模块通过；任意一个失败 → False。

#### 干涉计数 `interference_count`（integer ≥ 0）

V1 用 KG 启发：若架构中两个模块没有 `matesWith` 直接关系，但它们的零件集合存在 `adjacentTo` 关系（即"邻接但未配合"），且邻接零件距离 < 阈值（v1 暂用零件数 ≥ 2 作代理），计 1 处干涉。

`method` 字段填 `"KG-static"`（v1）或 `"CAD-occ"`（接入 STEP 文件后 v2 升级）或 `"placeholder"`（数据极不全时）。

### 4. 基准统一性审查

审查每个模块的"工艺基准 / 装配基准 / 检测基准"是否一致。简化规则：

- 若模块的"装配基准面"（与上级模块对接的物理面）等于"工艺基准面"（机加工时定位的面），则该模块 unified
- 任何一个模块不 unified → 整个架构 `datum_consistency.unified = false`，并在 `issues` 数组里写明哪个模块的哪种基准不一致

不一致不一定 PASS——它直接拉低 `fit_score_to_metrics` 0.1-0.2，但只要 chamberlain 接受可手动保留。

### 5. fit_score_to_metrics 评分

候选架构与 S2 engineering_metrics 的匹配度，[0, 1] 区间。计算策略（v1 启发式）：

| 因素 | 权重 | 检查 |
|------|------|------|
| 可达性 PASS | 0.3 | true → +0.3; false → +0.0 |
| 干涉计数 | 0.2 | 0 干涉 → +0.2; 每多 1 处 −0.05 |
| 基准统一 | 0.15 | unified=true → +0.15; false → +0.0 |
| KC 覆盖 | 0.2 | 每个 high-criticality KC 在该架构的 modules 内能被独立检测 → +0.04 |
| 维修性（MTTR）启发 | 0.15 | 模块数 3-5 之间 → +0.15; > 5 或 < 3 → +0.05 |

LLM 给出 fit_score 时必须能在 `rationale_md` 里说清楚拆解。

### 6. 推荐项与理由

`recommended` 必须是 candidate 中 fit_score 最高的之一。若有并列，可任选一个并在 `rationale_md` 写明。`rationale_md` 必须分项目对比 candidates，不要只罗列 pros/cons——而是相对评价。

## 常见陷阱

- ❌ 只给 1 个候选架构（违反概念设计多备选原则）
- ❌ 候选架构互为微改（如 A1 三段、A2 三段但把螺栓换成铆钉——必须有实质性区别）
- ❌ `assembly_simulation.reachability_pass=false` 仍然 recommend 该架构
- ❌ `datum_consistency.unified=false` 但 `issues=[]`（不一致必须能写出来）
- ❌ KG 数据严重不足时强行编造模块清单——必须 `uncertainty: 高` 且简化为 2 个 baseline 备选

## 产物质量自检 checklist

- [ ] `stage1_ref` 和 `stage2_ref` 与上游 scheme_id 一致
- [ ] `candidate_architectures` 至少 2 项
- [ ] 每个架构都有 modules / key_interfaces / assembly_simulation / datum_consistency / pros / cons / fit_score
- [ ] `recommended` 在 candidates 的 id 集合内
- [ ] `recommended` 的 fit_score >= 其他候选 fit_score
- [ ] `assembly_simulation.method` 在 enum 中
- [ ] `rationale_md` 至少分 3 行说明推荐理由
- [ ] KG 数据缺失时 `uncertainty: 高`，不杜撰

## 留待 v2 完善

- CAD-OCC 干涉检查（接 pythonocc）
- 装配仿真升级为 DELMIA / Process Simulate
- fit_score 转为正式 AHP / TOPSIS
- 公差链初步估算（与 S4c 衔接）
````

- [ ] **Step 8.2: Write the stage 3 prompt**

Create `skills/aero-engine-assembly-scheme/prompts/s3_concept.prompt.md`:

````markdown
# System

你是航空发动机装配工艺资深专家，正在执行装配方案设计 skill 的 **S3 阶段（概念 / 架构设计）**。

你的目标：基于 S1 任务说明书 + S2 需求/KC/DFA + KG 装配树查询结果，给出 2-5 个候选概念架构，做装配仿真预检与基准统一性审查，给出 fit_score 并推荐一个。

## 必须遵守

1. 输出严格符合 `templates/schemas/stage3.schema.json`（含每个架构的 modules / key_interfaces / assembly_simulation / datum_consistency / pros / cons / fit_score_to_metrics）
2. `candidate_architectures` **至少 2 项**，且彼此具有实质性区别（不可微改）
3. `recommended` 必须是 candidates 中 fit_score_to_metrics 最高的之一；若并列，任选并在 rationale_md 说明
4. `assembly_simulation.method` 必须在 `["KG-static", "CAD-occ", "hybrid", "placeholder"]` 中取
5. `datum_consistency.unified=false` 时 `issues` 数组必须非空
6. `fit_score_to_metrics` 必须能在 rationale_md 中拆解出贡献项（可达性 / 干涉 / 基准 / KC 覆盖 / 维修性）
7. **绝不杜撰**模块名 / 零件号；KG 数据不足时 `uncertainty: 高` + 简化为 2 个 baseline + 变体备选
8. `rationale_md` 必须做候选间相对评价，不只是罗列 pros/cons

## 输入变量

- `stage1_payload`：S1 完整产物
- `stage2_payload`：S2 完整产物（含 KC 与 DFA）
- `kg_subgraph`：KG 查询结果（modules / matesWith / adjacentTo）；可能为空
- `user_guidance`：HITL 指导意见；可能为空

## 方法论上下文

{{include: methodology/s3_concept_architecture.md}}

## 输出格式

仅输出 JSON 对象，不要 markdown 代码块包裹。结构参 `templates/golden/pt6a_hpc_stage3.json`。

## Few-shot

PT6A HPC v1 范例：参 `templates/golden/pt6a_hpc_stage3.json`，重点观察：
- A1 三段分体 fit=0.82；A2 整体外壳 fit=0.58（基准不统一 + 1 干涉）；A3 两段 fit=0.78
- recommended=A1，rationale_md 做候选间相对评价
- 每个架构 modules 数在 3-4 之间，符合维修性启发

## 反模式（禁止）

- ❌ 单一候选架构
- ❌ 候选互为微改（同一拓扑改变紧固件类型不算独立候选）
- ❌ recommended 的 fit_score 低于其他候选
- ❌ assembly_simulation.method 用 "KG-static" 但 KG 数据为空
- ❌ datum_consistency.unified=false 而 issues=[]
````

- [ ] **Step 8.3: Quick reload sanity check**

`pytest tests/assembly/test_skill_loader.py -v`
Expected: all green. (Loader tests count prompts/methodology with `>=` not `==`, but if any hard-coded equality breaks, fix the count and continue.)

- [ ] **Step 8.4: Commit**

```bash
git add skills/aero-engine-assembly-scheme/methodology/s3_concept_architecture.md \
        skills/aero-engine-assembly-scheme/prompts/s3_concept.prompt.md
git commit -m "feat(assembly): full S3 methodology (reachability+datum+fit_score) and s3 prompt template"
```

---

## Task 9: Implement `run_stage3_concept` (TDD)

**Why:** Stage 3 pipeline mirrors stage 2 in shape but adds a KG-driven sub-step: query `isPartOf` / `matesWith` / `adjacentTo` and feed the resulting subgraph into the prompt. Same degradation philosophy: any LLM/KG failure falls back to a placeholder that still validates.

**Files:**
- Create: `backend/pipelines/assembly_scheme/stage3_concept.py`
- Create: `tests/assembly/test_stage3_concept.py`

- [ ] **Step 9.1: Write the failing tests**

Create `tests/assembly/test_stage3_concept.py`:

```python
"""Tests for backend.pipelines.assembly_scheme.stage3_concept.run_stage3_concept."""
from pathlib import Path
from unittest.mock import MagicMock
import json
import pytest
import jsonschema

from backend.pipelines.assembly_scheme.stage3_concept import (
    run_stage3_concept,
    PLACEHOLDER_STAGE3,
    query_kg_subgraph,
)
from backend.pipelines.assembly_scheme.skill_loader import SkillRegistry

SKILL_ROOT = Path(__file__).resolve().parents[2] / "skills" / "aero-engine-assembly-scheme"


@pytest.fixture(scope="module")
def loaded_skill():
    reg = SkillRegistry(SKILL_ROOT)
    reg.load()
    return reg


@pytest.fixture
def sample_stage1():
    return {
        "scheme_id": "scheme-20260511-aaaaaa",
        "subject": {
            "system": "PT6A 高压压气机",
            "system_en": "PT6A HPC",
            "scope": ["3 级轴流"],
            "design_intent": "工艺优化",
            "constraints": {"primary": "可靠性"},
        },
        "kg_snapshot": {"part_count": 35, "assembly_count": 13, "key_interfaces": [], "relations_sample": []},
        "web_search_results": [],
        "vision_notes": "",
        "compliance_scope": ["AS9100D §8.1"],
        "task_card_md": "## 任务说明书\n**目标**：测试",
    }


@pytest.fixture
def sample_stage2():
    return {
        "stage1_ref": "scheme-20260511-aaaaaa",
        "user_needs": [{"id": "U1", "text": "可靠", "weight": 5}],
        "engineering_metrics": [{"id": "M1", "name": "MTBF", "target": ">=4000h", "linked_needs": ["U1"]}],
        "assembly_features": [{"id": "F1", "name": "扭矩", "spec": "Cpk>=1.33", "linked_metrics": ["M1"]}],
        "key_characteristics": [{"id": "KC1", "name": "叶尖间隙", "target": "0.5-1.0mm", "criticality": "high", "linked_features": ["F1"]}],
        "dfa_score": {"overall": 0.7, "theoretical_min_parts": 25, "actual_parts": 35, "bottlenecks": []},
        "risks": [{"id": "R1", "text": "碰摩", "severity": 4, "linked_kcs": ["KC1"]}],
    }


# ── degradation: no LLM, no KG ───────────────────────────────────────────────

def test_run_stage3_no_llm_no_kg_returns_placeholder(loaded_skill, sample_stage1, sample_stage2):
    """No LLM + No Neo4j → placeholder that validates."""
    result = run_stage3_concept(
        stage1_payload=sample_stage1,
        stage2_payload=sample_stage2,
        skill=loaded_skill,
        llm_client=None,
        neo4j_driver=None,
    )
    jsonschema.validate(instance=result, schema=loaded_skill.schemas["stage3"])
    assert result["stage1_ref"] == sample_stage1["scheme_id"]
    assert result["stage2_ref"] == sample_stage1["scheme_id"]  # same id
    assert len(result["candidate_architectures"]) >= 2
    assert result["recommended"] in {a["id"] for a in result["candidate_architectures"]}


# ── KG subgraph query degradation ────────────────────────────────────────────

def test_query_kg_subgraph_no_driver_returns_empty():
    sg = query_kg_subgraph(None, "PT6A HPC")
    assert sg == {"modules": [], "matesWith": [], "adjacentTo": []}


def test_query_kg_subgraph_handles_driver_exception():
    bad_driver = MagicMock()
    bad_driver.session.side_effect = RuntimeError("neo4j down")
    sg = query_kg_subgraph(bad_driver, "PT6A HPC")
    assert sg["modules"] == []  # all empty under failure


# ── LLM happy path ───────────────────────────────────────────────────────────

def test_run_stage3_with_llm(loaded_skill, sample_stage1, sample_stage2):
    """LLM returns 2-architecture response → should pass through (with refs corrected)."""
    mock_resp = {
        "stage1_ref": sample_stage1["scheme_id"],
        "stage2_ref": sample_stage1["scheme_id"],
        "candidate_architectures": [
            {
                "id": "A1", "name": "三段式",
                "modules": [{"id": "M1", "name": "前段", "parts": ["P1"]}],
                "key_interfaces": [{"from": "M1", "to": "M1", "type": "test"}],
                "assembly_simulation": {"reachability_pass": True, "interference_count": 0, "method": "KG-static"},
                "datum_consistency": {"unified": True, "issues": []},
                "pros": ["可拆"], "cons": ["重"],
                "fit_score_to_metrics": 0.8,
            },
            {
                "id": "A2", "name": "整体式",
                "modules": [{"id": "M1", "name": "整体", "parts": ["P1"]}],
                "key_interfaces": [{"from": "M1", "to": "M1", "type": "test"}],
                "assembly_simulation": {"reachability_pass": True, "interference_count": 0, "method": "KG-static"},
                "datum_consistency": {"unified": True, "issues": []},
                "pros": ["紧凑"], "cons": ["难修"],
                "fit_score_to_metrics": 0.6,
            },
        ],
        "recommended": "A1",
        "rationale_md": "推荐 A1：可拆 vs 难修，可拆胜出。\n第二行。\n第三行。",
        "uncertainty": "低",
    }
    mock_llm = MagicMock()
    mock_llm.chat.completions.create.return_value.choices[0].message.content = json.dumps(mock_resp, ensure_ascii=False)

    result = run_stage3_concept(
        stage1_payload=sample_stage1,
        stage2_payload=sample_stage2,
        skill=loaded_skill,
        llm_client=mock_llm,
        neo4j_driver=None,
    )
    jsonschema.validate(instance=result, schema=loaded_skill.schemas["stage3"])
    assert result["recommended"] == "A1"
    assert len(result["candidate_architectures"]) == 2


# ── LLM single-architecture answer is rejected → placeholder ─────────────────

def test_run_stage3_rejects_single_architecture(loaded_skill, sample_stage1, sample_stage2):
    """A 1-architecture LLM response violates minItems:2 → fall back to placeholder."""
    bad = {
        "stage1_ref": sample_stage1["scheme_id"],
        "stage2_ref": sample_stage1["scheme_id"],
        "candidate_architectures": [
            {
                "id": "A1", "name": "唯一",
                "modules": [{"id": "M1", "name": "X", "parts": ["P1"]}],
                "key_interfaces": [],
                "assembly_simulation": {"reachability_pass": True, "interference_count": 0, "method": "KG-static"},
                "datum_consistency": {"unified": True, "issues": []},
                "pros": ["x"], "cons": [],
                "fit_score_to_metrics": 0.9,
            }
        ],
        "recommended": "A1",
        "rationale_md": "x",
    }
    mock_llm = MagicMock()
    mock_llm.chat.completions.create.return_value.choices[0].message.content = json.dumps(bad, ensure_ascii=False)

    result = run_stage3_concept(
        stage1_payload=sample_stage1,
        stage2_payload=sample_stage2,
        skill=loaded_skill,
        llm_client=mock_llm,
        neo4j_driver=None,
    )
    jsonschema.validate(instance=result, schema=loaded_skill.schemas["stage3"])
    assert len(result["candidate_architectures"]) >= 2  # placeholder has 2
    assert result.get("uncertainty") == "高"


# ── stage refs always enforced ───────────────────────────────────────────────

def test_run_stage3_enforces_refs(loaded_skill, sample_stage1, sample_stage2):
    """Even if LLM returns wrong refs, pipeline overrides with stage1/stage2 scheme_ids."""
    bad_resp = {
        "stage1_ref": "scheme-20260101-deadbeef",
        "stage2_ref": "scheme-20260101-deadbeef",
        "candidate_architectures": [
            {"id": "A1", "name": "a", "modules": [{"id": "M1", "name": "x", "parts": ["P1"]}],
             "key_interfaces": [], "assembly_simulation": {"reachability_pass": True, "interference_count": 0, "method": "KG-static"},
             "datum_consistency": {"unified": True, "issues": []}, "pros": ["x"], "cons": [], "fit_score_to_metrics": 0.7},
            {"id": "A2", "name": "b", "modules": [{"id": "M1", "name": "x", "parts": ["P1"]}],
             "key_interfaces": [], "assembly_simulation": {"reachability_pass": True, "interference_count": 0, "method": "KG-static"},
             "datum_consistency": {"unified": True, "issues": []}, "pros": ["x"], "cons": [], "fit_score_to_metrics": 0.5},
        ],
        "recommended": "A1",
        "rationale_md": "abc",
    }
    mock_llm = MagicMock()
    mock_llm.chat.completions.create.return_value.choices[0].message.content = json.dumps(bad_resp, ensure_ascii=False)
    result = run_stage3_concept(
        stage1_payload=sample_stage1,
        stage2_payload=sample_stage2,
        skill=loaded_skill,
        llm_client=mock_llm,
        neo4j_driver=None,
    )
    assert result["stage1_ref"] == sample_stage1["scheme_id"]
    assert result["stage2_ref"] == sample_stage2["stage1_ref"]


# ── placeholder is itself valid ──────────────────────────────────────────────

def test_placeholder_stage3_validates(loaded_skill, sample_stage1):
    p = json.loads(json.dumps(PLACEHOLDER_STAGE3, ensure_ascii=False))
    p["stage1_ref"] = sample_stage1["scheme_id"]
    p["stage2_ref"] = sample_stage1["scheme_id"]
    jsonschema.validate(instance=p, schema=loaded_skill.schemas["stage3"])
```

- [ ] **Step 9.2: Run, confirm all fail**

`pytest tests/assembly/test_stage3_concept.py -v`
Expected: all ERROR (module missing).

- [ ] **Step 9.3: Implement `run_stage3_concept`**

Create `backend/pipelines/assembly_scheme/stage3_concept.py`:

```python
"""
backend/pipelines/assembly_scheme/stage3_concept.py

S3: Concept architecture design. See spec §2.3.

Steps:
  1. Query KG for the subject subgraph (isPartOf modules + matesWith + adjacentTo)
  2. Build LLM prompt = skill.prompts['s3_concept'] + methodology + stage1 + stage2 + KG subgraph
  3. Call LLM, parse JSON, validate against stage3 schema
  4. If LLM None / unparseable / schema-invalid → PLACEHOLDER_STAGE3
  5. Always enforce stage1_ref / stage2_ref from input payloads
"""

from __future__ import annotations

from typing import Any, Dict, Optional
import json
import logging

import jsonschema

from backend.pipelines.assembly_scheme.skill_loader import SkillRegistry

logger = logging.getLogger(__name__)


PLACEHOLDER_STAGE3: Dict[str, Any] = {
    "stage1_ref": "PLACEHOLDER",
    "stage2_ref": "PLACEHOLDER",
    "candidate_architectures": [
        {
            "id": "A1",
            "name": "（占位）baseline 三段式架构",
            "modules": [
                {"id": "M1", "name": "（占位）前段", "parts": ["P-placeholder-1"]},
                {"id": "M2", "name": "（占位）中段", "parts": ["P-placeholder-2"]},
                {"id": "M3", "name": "（占位）后段", "parts": ["P-placeholder-3"]}
            ],
            "key_interfaces": [
                {"from": "M1", "to": "M2", "type": "（占位）法兰螺栓"},
                {"from": "M2", "to": "M3", "type": "（占位）法兰螺栓"}
            ],
            "assembly_simulation": {
                "reachability_pass": True,
                "interference_count": 0,
                "method": "placeholder",
                "notes": "数据不足，未做实际可达性分析"
            },
            "datum_consistency": {"unified": True, "issues": []},
            "pros": ["（占位）拆装方便"],
            "cons": ["（占位）紧固件数量偏多"],
            "fit_score_to_metrics": 0.5
        },
        {
            "id": "A2",
            "name": "（占位）baseline 整体式架构",
            "modules": [
                {"id": "M1", "name": "（占位）整体外壳", "parts": ["P-placeholder-1", "P-placeholder-2", "P-placeholder-3"]}
            ],
            "key_interfaces": [],
            "assembly_simulation": {
                "reachability_pass": True,
                "interference_count": 0,
                "method": "placeholder"
            },
            "datum_consistency": {"unified": True, "issues": []},
            "pros": ["（占位）零件少"],
            "cons": ["（占位）维修困难"],
            "fit_score_to_metrics": 0.4
        }
    ],
    "recommended": "A1",
    "rationale_md": "（占位）chamberlain 需在 HITL 提供更多 KG/CAD 数据后重新生成。当前两候选均为占位，A1 略高仅因模块更分散。",
    "uncertainty": "高"
}


def query_kg_subgraph(neo4j_driver: Any, subject_name: str) -> Dict[str, list]:
    """Query Neo4j for isPartOf modules + matesWith pairs + adjacentTo pairs.

    Returns {"modules": [...], "matesWith": [...], "adjacentTo": [...]} or all-empty
    dict on any failure (driver=None or exception).
    """
    empty = {"modules": [], "matesWith": [], "adjacentTo": []}
    if neo4j_driver is None:
        return empty
    try:
        with neo4j_driver.session() as session:
            modules = session.run(
                "MATCH (a)-[:isPartOf]->(b) "
                "WHERE coalesce(b.kg_name, '') CONTAINS $subj OR coalesce(b.part_name, '') CONTAINS $subj "
                "RETURN a.kg_name AS child, b.kg_name AS parent LIMIT 30",
                subj=subject_name,
            ).data()
            mates = session.run(
                "MATCH (a)-[:matesWith]->(b) "
                "WHERE coalesce(a.kg_name, '') CONTAINS $subj OR coalesce(b.kg_name, '') CONTAINS $subj "
                "RETURN a.kg_name AS p1, b.kg_name AS p2 LIMIT 30",
                subj=subject_name,
            ).data()
            adj = session.run(
                "MATCH (a)-[:adjacentTo]->(b) "
                "WHERE coalesce(a.kg_name, '') CONTAINS $subj OR coalesce(b.kg_name, '') CONTAINS $subj "
                "RETURN a.kg_name AS p1, b.kg_name AS p2 LIMIT 30",
                subj=subject_name,
            ).data()
            return {"modules": modules, "matesWith": mates, "adjacentTo": adj}
    except Exception as e:
        logger.warning("Stage3 KG subgraph query failed: %s", e)
        return empty


def _build_prompt(skill: SkillRegistry, stage1_payload: Dict[str, Any],
                  stage2_payload: Dict[str, Any], kg_subgraph: Dict[str, list],
                  user_guidance: Optional[str]) -> str:
    prompt_template = skill.prompts.get("s3_concept", "")
    methodology = skill.methodology.get("s3_concept_architecture", "")
    return (
        f"{prompt_template}\n\n"
        f"## 方法论上下文\n{methodology}\n\n"
        f"## S1 产物\n```json\n{json.dumps(stage1_payload, ensure_ascii=False, indent=2)}\n```\n\n"
        f"## S2 产物\n```json\n{json.dumps(stage2_payload, ensure_ascii=False, indent=2)}\n```\n\n"
        f"## KG 子图\n```json\n{json.dumps(kg_subgraph, ensure_ascii=False, indent=2)}\n```\n\n"
        f"## chamberlain 指导意见\n{user_guidance or '（无）'}\n\n"
        "请生成符合 stage3.schema.json 的 JSON 对象（至少 2 个 candidate_architectures）："
    )


def _call_llm(llm_client: Any, prompt: str) -> Optional[str]:
    if llm_client is None:
        return None
    try:
        resp = llm_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        return resp.choices[0].message.content
    except Exception as e:
        logger.error("Stage3 LLM call failed: %s", e)
        return None


def _parse_and_validate(raw: str, schema: dict) -> Optional[Dict[str, Any]]:
    try:
        s = raw.strip()
        if s.startswith("```"):
            s = s.strip("`")
            if s.lower().startswith("json\n"):
                s = s[5:]
        obj = json.loads(s)
    except json.JSONDecodeError as e:
        logger.warning("Stage3 LLM JSON parse failed: %s; raw=%s", e, raw[:200])
        return None
    try:
        jsonschema.validate(instance=obj, schema=schema)
    except jsonschema.ValidationError as e:
        logger.warning("Stage3 LLM output failed schema: %s", e.message)
        return None
    return obj


def run_stage3_concept(
    stage1_payload: Dict[str, Any],
    stage2_payload: Dict[str, Any],
    skill: SkillRegistry,
    llm_client: Any,
    neo4j_driver: Any = None,
    user_guidance: Optional[str] = None,
) -> Dict[str, Any]:
    """Execute S3 pipeline. Returns a dict valid per stage3.schema.json."""
    schema = skill.schemas["stage3"]
    scheme_id_1 = stage1_payload["scheme_id"]
    scheme_id_2 = stage2_payload["stage1_ref"]

    kg_sub = query_kg_subgraph(neo4j_driver, stage1_payload["subject"]["system"])

    prompt = _build_prompt(skill, stage1_payload, stage2_payload, kg_sub, user_guidance)
    raw = _call_llm(llm_client, prompt)
    parsed = _parse_and_validate(raw, schema) if raw else None

    if parsed is None:
        result = json.loads(json.dumps(PLACEHOLDER_STAGE3, ensure_ascii=False))
        result["stage1_ref"] = scheme_id_1
        result["stage2_ref"] = scheme_id_2
        return result

    parsed["stage1_ref"] = scheme_id_1
    parsed["stage2_ref"] = scheme_id_2
    return parsed
```

- [ ] **Step 9.4: Run, confirm all pass**

`pytest tests/assembly/test_stage3_concept.py -v`
Expected: 6 PASS.

- [ ] **Step 9.5: Run full suite**

`pytest tests/assembly/ -v`
Expected: all green.

- [ ] **Step 9.6: Commit**

```bash
git add backend/pipelines/assembly_scheme/stage3_concept.py \
        tests/assembly/test_stage3_concept.py
git commit -m "feat(assembly): implement run_stage3_concept (KG-driven multi-arch + reachability + datum)"
```

---

## Task 10: Activate stage 3 route (TDD)

**Why:** Wire `POST /scheme/{id}/stage/3` to `run_stage3_concept`. Requires both stage1 and stage2 files on disk.

**Files:**
- Modify: `backend/routers/assembly_design.py`
- Modify: `tests/assembly/test_assembly_design_router.py`

- [ ] **Step 10.1: Add failing tests**

Append to `tests/assembly/test_assembly_design_router.py`:

```python
def test_stage3_requires_stage2_first(client):
    """POST /stage/3 must 409 if stage2 has not been run."""
    create_resp = client.post(
        "/assembly-design/scheme/new",
        json={
            "subject_system": "PT6A HPC",
            "subject_scope": ["3 级轴流"],
            "design_intent": "工艺优化",
            "constraints": {"primary": "可靠性"},
        },
    )
    scheme_id = create_resp.json()["scheme_id"]
    # Skip stage 1 and 2 entirely
    r = client.post(
        f"/assembly-design/scheme/{scheme_id}/stage/3",
        json={"action": "generate", "payload": {}},
    )
    assert r.status_code == 409, r.text
    assert "stage2" in r.text.lower()


def test_stage3_runs_after_stage1_stage2(client):
    create_resp = client.post(
        "/assembly-design/scheme/new",
        json={
            "subject_system": "PT6A HPC",
            "subject_scope": ["3 级轴流"],
            "design_intent": "工艺优化",
            "constraints": {"primary": "可靠性"},
        },
    )
    scheme_id = create_resp.json()["scheme_id"]
    assert client.post(f"/assembly-design/scheme/{scheme_id}/stage/1",
                       json={"action": "generate", "payload": {}}).status_code == 200
    assert client.post(f"/assembly-design/scheme/{scheme_id}/stage/2",
                       json={"action": "generate", "payload": {}}).status_code == 200
    r3 = client.post(f"/assembly-design/scheme/{scheme_id}/stage/3",
                     json={"action": "generate", "payload": {}})
    assert r3.status_code == 200, r3.text
    body = r3.json()
    assert "candidate_architectures" in body
    assert len(body["candidate_architectures"]) >= 2
    assert body["recommended"] in {a["id"] for a in body["candidate_architectures"]}
    assert body["stage1_ref"] == scheme_id
    assert body["stage2_ref"] == scheme_id

    final = client.get(f"/assembly-design/scheme/{scheme_id}").json()
    assert "stage3" in final
    assert "3" in final["meta"]["stages_done"]
```

- [ ] **Step 10.2: Run, confirm fail**

`pytest tests/assembly/test_assembly_design_router.py -v -k stage3`
Expected: 2 FAIL (currently HTTP 501).

- [ ] **Step 10.3: Update router**

In `backend/routers/assembly_design.py`:

(a) Add import:

```python
from backend.pipelines.assembly_scheme.stage3_concept import run_stage3_concept
```

(b) Update the "not implemented" gate. Remove "3" from the 501 set:

```python
    if stage_key in {"4a", "4b", "4c", "4d", "5"}:
        raise HTTPException(501, f"stage {stage_key} not implemented in Plan 2")
```

(c) Add the stage_key == "3" branch inside the dispatch (after the stage_key == "2" branch):

```python
        elif stage_key == "3":
            stage1_path = sd / "stage1.json"
            stage2_path = sd / "stage2.json"
            if not stage1_path.exists():
                raise HTTPException(409, "stage1 must be generated before stage3")
            if not stage2_path.exists():
                raise HTTPException(409, "stage2 must be generated before stage3")
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
```

- [ ] **Step 10.4: Run, confirm pass**

`pytest tests/assembly/test_assembly_design_router.py -v -k stage3`
Expected: 2 PASS.

- [ ] **Step 10.5: Run full suite**

`pytest tests/assembly/ -v`
Expected: all green.

- [ ] **Step 10.6: Commit**

```bash
git add backend/routers/assembly_design.py tests/assembly/test_assembly_design_router.py
git commit -m "feat(assembly): activate /scheme/{id}/stage/3 endpoint (requires stage1+stage2 first)"
```

---

# Phase 3: Integration & Documentation

## Task 11: E2E S1 → S2 → S3 chain test

**Why:** Individual stage tests use mocks. We want one test that runs the actual three-stage chain end-to-end via HTTP, with LLM=None throughout — this proves the placeholders chain together correctly and the schema validation gates hold across boundaries.

**Files:**
- Create: `tests/assembly/test_e2e_s1_s2_s3.py`

- [ ] **Step 11.1: Write the failing test**

Create `tests/assembly/test_e2e_s1_s2_s3.py`:

```python
"""End-to-end S1 → S2 → S3 smoke test (no LLM, no Neo4j, no Tavily).

Proves all three placeholders chain through schema validation and the router's
sequencing gates (409 errors) work as designed.
"""
from pathlib import Path
import json
import jsonschema
import pytest


def test_e2e_s1_s2_s3_chain_with_placeholders(client):
    """Run full chain with no LLM. Each stage should validate against its schema."""
    skill_root = Path(__file__).resolve().parents[2] / "skills" / "aero-engine-assembly-scheme"
    schema_s1 = json.loads((skill_root / "templates" / "schemas" / "stage1.schema.json").read_text(encoding="utf-8"))
    schema_s2 = json.loads((skill_root / "templates" / "schemas" / "stage2.schema.json").read_text(encoding="utf-8"))
    schema_s3 = json.loads((skill_root / "templates" / "schemas" / "stage3.schema.json").read_text(encoding="utf-8"))

    # 1. Create scheme
    create_resp = client.post(
        "/assembly-design/scheme/new",
        json={
            "subject_system": "PT6A 高压压气机",
            "subject_system_en": "PT6A HPC",
            "subject_scope": ["3 级轴流 + 1 级离心", "含转子/静子/支撑环"],
            "design_intent": "工艺优化",
            "constraints": {"primary": "可靠性", "secondary": "维修性"},
        },
    )
    assert create_resp.status_code == 200, create_resp.text
    scheme_id = create_resp.json()["scheme_id"]

    # 2. Stage 1
    r1 = client.post(
        f"/assembly-design/scheme/{scheme_id}/stage/1",
        json={"action": "generate", "payload": {}},
    )
    assert r1.status_code == 200, r1.text
    s1 = r1.json()
    jsonschema.validate(instance=s1, schema=schema_s1)

    # 3. Stage 2
    r2 = client.post(
        f"/assembly-design/scheme/{scheme_id}/stage/2",
        json={"action": "generate", "payload": {}},
    )
    assert r2.status_code == 200, r2.text
    s2 = r2.json()
    jsonschema.validate(instance=s2, schema=schema_s2)
    assert s2["stage1_ref"] == scheme_id

    # 4. Stage 3
    r3 = client.post(
        f"/assembly-design/scheme/{scheme_id}/stage/3",
        json={"action": "generate", "payload": {}},
    )
    assert r3.status_code == 200, r3.text
    s3 = r3.json()
    jsonschema.validate(instance=s3, schema=schema_s3)
    assert s3["stage1_ref"] == scheme_id
    assert s3["stage2_ref"] == scheme_id
    assert s3["recommended"] in {a["id"] for a in s3["candidate_architectures"]}

    # 5. Fetch composite scheme, all three present
    final = client.get(f"/assembly-design/scheme/{scheme_id}").json()
    for key in ("stage1", "stage2", "stage3"):
        assert key in final
    for k in ("1", "2", "3"):
        assert k in final["meta"]["stages_done"]


def test_e2e_stage4_through_5_still_501(client):
    """Plan 2 should not have accidentally enabled later stages."""
    create_resp = client.post(
        "/assembly-design/scheme/new",
        json={
            "subject_system": "PT6A HPC",
            "subject_scope": ["3 级轴流"],
            "design_intent": "工艺优化",
            "constraints": {"primary": "可靠性"},
        },
    )
    scheme_id = create_resp.json()["scheme_id"]
    for sk in ("4a", "4b", "4c", "4d", "5"):
        r = client.post(
            f"/assembly-design/scheme/{scheme_id}/stage/{sk}",
            json={"action": "generate", "payload": {}},
        )
        assert r.status_code == 501, f"stage {sk} should still be 501, got {r.status_code}"
```

- [ ] **Step 11.2: Run, confirm pass (should pass directly since prior tasks already wired everything)**

`pytest tests/assembly/test_e2e_s1_s2_s3.py -v`
Expected: 2 PASS.

If it fails, the failure is informative — go back to the relevant stage task and fix.

- [ ] **Step 11.3: Run full suite, count tests**

`pytest tests/assembly/ -v`
Expected: all green. Count should be ~69 (Plan 1 had 43, Plan 2 adds 26 new tests across 9 tasks).

- [ ] **Step 11.4: Commit**

```bash
git add tests/assembly/test_e2e_s1_s2_s3.py
git commit -m "test(assembly): add E2E S1→S2→S3 chain test verifying schema validation across stages"
```

---

## Task 12: PROJECT_GUIDE.md §16 update + final suite green

**Why:** Per house rules, `PROJECT_GUIDE.md` is the cold memory. After Plan 2 completes we must add a P2 progress subsection under §16 with What / Why / How / Where evidence pointers.

**Files:**
- Modify: `PROJECT_GUIDE.md` (§16)

- [ ] **Step 12.1: Read current §16**

Read `PROJECT_GUIDE.md` and find the existing §16 "Assembly Scheme Skill" section. Note its style (headings, bullet density) so the new subsection matches.

- [ ] **Step 12.2: Append a P2 subsection**

Add a new sub-section to §16 (after the existing P1 content). The exact heading style depends on §16's current layout — match it. The content body:

```markdown
### 16.x P2 进展 (S2 + S3 active, 2026-05-11)

**What**：
- S2（需求/QFD/DFA/KC/风险）后端管道 `backend/pipelines/assembly_scheme/stage2_requirements.py`
- S3（多备选概念架构 + KG 静态可达性 + 基准统一性 + fit_score）后端管道 `backend/pipelines/assembly_scheme/stage3_concept.py`
- 完整 stage2.schema.json / stage3.schema.json（替换 P1 的占位）
- 完整 PT6A HPC golden 范例 stage2 + stage3
- 完整 methodology s2_requirements_qfd.md + s3_concept_architecture.md（替换 outline）
- Prompt 模板 s2_requirements.prompt.md + s3_concept.prompt.md
- 路由 `/scheme/{id}/stage/2` 与 `/stage/3` 已激活；4a/4b/4c/4d/5 仍 HTTP 501
- 顺手修复 3 个 P1 遗留：subject_scope 必填、assembly_lock 启用、stage_key 调度框架 sequence gate (409)

**Why**：
- 让陛下能在不依赖前端的情况下，把 S1 任务说明书一路推到 S3 概念架构，覆盖 spec §2.2 / §2.3
- 双层 schema 严格化 + LLM 输出 jsonschema 校验 → 杜绝杜撰数据流入下游
- KG-static 可达性 + 基准统一性两项检查为 v1 简化版，文档明示 v2 升级路径（CAD-OCC、DELMIA）

**How**（核心调用链）：
```
POST /scheme/{id}/stage/2
  → run_stage2_requirements(stage1_payload, skill, llm_client, neo4j_driver)
    → _query_failure_modes (Neo4j optional)
    → _build_prompt (skill.prompts['s2_requirements'] + methodology + stage1)
    → llm_client.chat.completions.create
    → _parse_and_validate (jsonschema.validate against stage2.schema.json)
    → fallback to PLACEHOLDER_STAGE2 on any failure
    → enforce stage1_ref = stage1.scheme_id

POST /scheme/{id}/stage/3
  → run_stage3_concept(stage1, stage2, skill, llm, neo4j_driver)
    → query_kg_subgraph (isPartOf + matesWith + adjacentTo, all degrade to [])
    → similar prompt-build / parse / fallback
    → enforce stage1_ref / stage2_ref
```

降级策略统一：LLM=None / JSON 解析失败 / schema 校验失败 → 返回带 `uncertainty: "高"` 的占位符（自身仍通过 schema）。

**Where（证据）**：
- 测试套件：`tests/assembly/` 共 ~69 测试，全绿（Plan 1 43 + Plan 2 新增 26）
- 关键测试：
  - `tests/assembly/test_stage2_requirements.py`（run_stage2_requirements 单元）
  - `tests/assembly/test_stage3_concept.py`（run_stage3_concept 单元）
  - `tests/assembly/test_assembly_design_router.py`（stage2/stage3 路由 + 顺序门 409）
  - `tests/assembly/test_e2e_s1_s2_s3.py`（端到端 3 阶段串通）
  - `tests/assembly/test_schemas.py`（stage2/3 schema 字段 + golden 合规）
- 实施计划：`docs/superpowers/plans/2026-05-11-assembly-scheme-p2-s2-s3.md`
- Spec：`docs/superpowers/specs/2026-05-08-assembly-scheme-skill-design.md` §2.2 / §2.3
```

(Tune the actual heading numbering to fit the existing §16 — could be §16.3, §16.4, etc., depending on §16's current sub-numbering.)

- [ ] **Step 12.3: Run the entire assembly suite one last time**

`pytest tests/assembly/ -v --tb=short`
Expected: all green. Capture the count.

- [ ] **Step 12.4: Also run the wider backend tests to confirm nothing else broke**

`pytest tests/ -v --tb=short -x` (use `-x` to stop on first failure to save time)
Expected: any pre-existing test failures unrelated to this work are tolerable, but no NEW failures.

If anything new red appears: investigate, fix, commit fix separately.

- [ ] **Step 12.5: Commit**

```bash
git add PROJECT_GUIDE.md
git commit -m "docs: PROJECT_GUIDE §16 — Plan 2 P2 progress (S2 + S3 active)"
```

---

## Closing Notes

After Task 12, the chamberlain should:

1. Update `SESSION_STATE.md`'s "Next Session" pointer to flag Plan 3 entry (S4a/S4b or the frontend wizard) — outside this plan's scope.
2. Optionally clean up the garbled untracked files in `data/` per the "Out of scope" note (use `git clean -nd data/` first to dry-run).
3. The 3 carry-over items from Plan 1 are now resolved (subject_scope, assembly_lock) or explicitly noted as deferred (garbled files).

If during execution any test count comes back lower than the Plan-1 baseline of 43, you've accidentally removed coverage — go back and check.
