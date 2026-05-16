# Assembly Scheme Skill Plan 5 — S5 虚拟评审与方案导出

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现 Assembly Scheme Skill 的最终阶段 S5：三角色虚拟评审 + KC 追溯矩阵 + 方案导出为 `final_scheme.md`，完成 S1→S5 全链路贯通。

**Architecture:** 新增 `backend/pipelines/assembly_scheme/stage5_review.py`，实现与 stage4b_tooling.py 相同的 4 层降级 PLACEHOLDER 模式；路由层 `assembly_design.py` 激活 stage "5" 和 GET `/export` 端点；schema 从占位符 v1 升级为完整约束版。

**Tech Stack:** Python 3.10, jsonschema, FastAPI, pytest, pathlib；延续 stage4b 的 LLM call → parse → validate → cross_validate → PLACEHOLDER 四层保险模式。

---

## 文件地图

| 动作 | 文件 | 说明 |
|------|------|------|
| **修改** | `skills/aero-engine-assembly-scheme/templates/schemas/stage5.schema.json` | 从 placeholder v1 升级为完整带约束的 schema |
| **新增** | `skills/aero-engine-assembly-scheme/prompts/s5_review.prompt.md` | S5 三角色评审 LLM 提示词 |
| **新增** | `backend/pipelines/assembly_scheme/stage5_review.py` | S5 管道主文件 |
| **新增** | `tests/assembly/test_stage5_review.py` | S5 单元测试（8 条） |
| **修改** | `backend/routers/assembly_design.py` | 激活 stage "5" 分支 + 实现 GET /export |
| **修改** | `tests/assembly/test_assembly_design_router.py` | stage/5 从 501 → 409 断言 |
| **修改** | `tests/assembly/test_e2e_s1_s2_s3.py` | stage 5 从 501 → 409 断言 |

---

## Task 1: 升级 stage5.schema.json

**Files:**
- Modify: `skills/aero-engine-assembly-scheme/templates/schemas/stage5.schema.json`

- [ ] **Step 1: 覆写 stage5.schema.json 为完整约束版**

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "stage5.schema.json",
  "title": "Stage 5 — Review & Export",
  "type": "object",
  "required": ["stage4b_ref", "review_panel", "kc_traceability_matrix", "overall_score", "recommendation", "uncertainty"],
  "properties": {
    "stage4b_ref": {
      "type": "string",
      "description": "scheme_id 继承自 stage4b"
    },
    "review_panel": {
      "type": "array",
      "minItems": 3,
      "maxItems": 3,
      "items": {
        "type": "object",
        "required": ["role", "findings", "severity_issues"],
        "properties": {
          "role": {
            "type": "string",
            "enum": ["工艺工程师", "质量工程师", "设计工程师"]
          },
          "findings": {
            "type": "array",
            "items": {"type": "string", "minLength": 1}
          },
          "severity_issues": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["issue", "severity"],
              "properties": {
                "issue": {"type": "string", "minLength": 1},
                "severity": {"type": "string", "enum": ["low", "medium", "high"]},
                "iterate_to": {"type": "string"}
              }
            }
          }
        }
      }
    },
    "kc_traceability_matrix": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["kc_id", "kc_name", "procedures", "qc_checkpoints", "covered"],
        "properties": {
          "kc_id": {"type": "string"},
          "kc_name": {"type": "string"},
          "procedures": {"type": "array", "items": {"type": "string"}},
          "qc_checkpoints": {"type": "array", "items": {"type": "string"}},
          "covered": {"type": "boolean"}
        }
      }
    },
    "overall_score": {"type": "number", "minimum": 0, "maximum": 5},
    "recommendation": {
      "type": "string",
      "enum": ["approved", "approved_with_revision", "rejected"]
    },
    "iterations": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["issue", "severity", "iterate_to", "reason"],
        "properties": {
          "issue": {"type": "string"},
          "severity": {"type": "string", "enum": ["low", "medium", "high"]},
          "iterate_to": {"type": "string"},
          "reason": {"type": "string"}
        }
      }
    },
    "uncertainty": {
      "type": "string",
      "enum": ["高", "中", "低"]
    },
    "export_path": {"type": "string"}
  }
}
```

- [ ] **Step 2: 验证 schema 文件本身是合法 JSON**

```bash
python -c "import json; json.loads(open('skills/aero-engine-assembly-scheme/templates/schemas/stage5.schema.json', encoding='utf-8').read()); print('OK')"
```

期望输出：`OK`

- [ ] **Step 3: 运行现有 test_schemas.py 确保无回归**

```bash
python -m pytest tests/assembly/test_schemas.py -v
```

期望：全部 PASS

- [ ] **Step 4: commit**

```bash
git add skills/aero-engine-assembly-scheme/templates/schemas/stage5.schema.json
git commit -m "feat(assembly): upgrade stage5.schema.json to full constraints"
```

---

## Task 2: 新增 S5 提示词

**Files:**
- Create: `skills/aero-engine-assembly-scheme/prompts/s5_review.prompt.md`

- [ ] **Step 1: 创建 s5_review.prompt.md**

```markdown
# S5 三角色虚拟评审提示词

你是航空发动机装配方案的三角色评审委员会，分别扮演：
1. **工艺工程师**：检查工序冲突、工装覆盖、工艺可行性
2. **质量工程师**：检查 KC 追溯、QC 点覆盖、规范引用正确性
3. **设计工程师**：检查方案是否完整回应 S2 所有工程指标

## 评审规则

1. 每个角色必须给出 `findings`（至少 1 条观察）和 `severity_issues`（可为空列表）
2. `severity_issues` 中 severity 取值：`"low"` | `"medium"` | `"high"`
3. high severity 问题必须在 `iterations` 列表中记录，并注明 `iterate_to`（如 "4a" 或 "4b"）
4. `kc_traceability_matrix`：为 S2 中每个 KC 找到对应的 S4a 工序和 QC 检查点；`covered` 为 true 当且仅当至少有 1 个 qc_checkpoint
5. `overall_score`：[0, 5] 小数，综合三角色评分加权均值
6. `recommendation`：
   - 无 high severity → "approved" 或 "approved_with_revision"
   - 有 high severity → 必须为 "approved_with_revision" 或 "rejected"
7. `uncertainty`：取 "高"/"中"/"低"，反映评审置信度

## 反模式

- ❌ `recommendation: "approved"` 同时存在 high severity issues
- ❌ kc_traceability_matrix 中遗漏任何一个 S2 KC
- ❌ findings 使用空字符串或泛化废话

## 输出格式

严格输出符合 stage5.schema.json 的 JSON 对象，不带 markdown 代码块包裹。
```

- [ ] **Step 2: 验证 skill_loader 能加载新 prompt（依赖 Task 3 的 SkillRegistry 不变）**

（在 Task 3 完成后验证，此处 commit 即可）

- [ ] **Step 3: commit**

```bash
git add skills/aero-engine-assembly-scheme/prompts/s5_review.prompt.md
git commit -m "feat(assembly): add s5_review.prompt.md"
```

---

## Task 3: 实现 stage5_review.py（先写测试，再写实现）

**Files:**
- Create: `tests/assembly/test_stage5_review.py`
- Create: `backend/pipelines/assembly_scheme/stage5_review.py`

- [ ] **Step 1: 先写失败测试文件 `tests/assembly/test_stage5_review.py`**

```python
"""Tests for backend.pipelines.assembly_scheme.stage5_review.run_stage5_review."""
from pathlib import Path
from unittest.mock import MagicMock
import json
import pytest
import jsonschema

from backend.pipelines.assembly_scheme.stage5_review import (
    run_stage5_review,
    PLACEHOLDER_STAGE5,
)
from backend.pipelines.assembly_scheme.skill_loader import SkillRegistry

SKILL_ROOT = Path(__file__).resolve().parents[2] / "skills" / "aero-engine-assembly-scheme"


@pytest.fixture(scope="module")
def loaded_skill():
    reg = SkillRegistry(SKILL_ROOT)
    reg.load()
    return reg


@pytest.fixture
def sample_stage4b():
    return {
        "stage4a_ref": "scheme-20260511-aaaaaa",
        "tools": [
            {"id": "T01", "name": "定位夹具 JIG-001", "category": "special",
             "cost_tier": "高", "used_in_procedures": ["P01"]},
            {"id": "T02", "name": "扭矩扳手", "category": "generic",
             "cost_tier": "低", "used_in_procedures": ["P02"]},
        ],
        "tooling_constraints": [],
        "dfa_tooling_score": 0.5,
        "uncertainty": "中",
    }


@pytest.fixture
def sample_stage4a():
    return {
        "stage3_ref": "scheme-20260511-aaaaaa",
        "procedures": [
            {"id": "P01", "name": "后轴承座定位装夹", "seq_no": 1, "depends_on": [],
             "parts_involved": ["后轴承座"], "tooling": ["定位夹具 JIG-001"],
             "spec_values": [{"param": "定位精度", "value": "±0.02mm"}]},
            {"id": "P02", "name": "螺栓紧固", "seq_no": 2, "depends_on": ["P01"],
             "parts_involved": ["法兰螺栓"], "tooling": ["扭矩扳手"],
             "spec_values": [{"param": "力矩", "value": "25 N·m"}]},
        ],
        "topology": {"sequence": ["P01", "P02"], "method": "DFA-heuristic", "dfa_efficiency": 0.72},
        "uncertainty": "中",
    }


@pytest.fixture
def sample_stage2():
    return {
        "stage1_ref": "scheme-20260511-aaaaaa",
        "user_needs": [{"id": "U1", "text": "高可靠性", "weight": 5}],
        "engineering_metrics": [{"id": "M1", "name": "叶尖间隙", "target": "0.3mm", "linked_needs": ["U1"]}],
        "assembly_features": [{"id": "F1", "name": "转子定心精度", "spec": "±0.02mm", "linked_metrics": ["M1"]}],
        "key_characteristics": [
            {"id": "KC1", "name": "叶尖间隙", "target": "0.3±0.05mm", "criticality": "high"},
            {"id": "KC2", "name": "轴向预紧力", "target": "2000±100N", "criticality": "medium"},
        ],
        "dfa_score": {"overall": 0.72, "theoretical_min_parts": 5, "actual_parts": 7, "bottlenecks": []},
        "risks": [{"id": "R1", "text": "叶尖间隙超差风险", "severity": 4}],
        "uncertainty": "中",
    }


def _valid_llm_resp(scheme_id: str) -> dict:
    return {
        "stage4b_ref": scheme_id,
        "review_panel": [
            {"role": "工艺工程师", "findings": ["工序 P01 定位精度满足要求"], "severity_issues": []},
            {"role": "质量工程师", "findings": ["KC1 叶尖间隙有 QC 检查点覆盖"], "severity_issues": []},
            {"role": "设计工程师", "findings": ["S2 需求 M1 已在工序中体现"], "severity_issues": []},
        ],
        "kc_traceability_matrix": [
            {"kc_id": "KC1", "kc_name": "叶尖间隙", "procedures": ["P01"],
             "qc_checkpoints": ["叶尖间隙测量（游标卡尺）"], "covered": True},
            {"kc_id": "KC2", "kc_name": "轴向预紧力", "procedures": ["P02"],
             "qc_checkpoints": ["轴向力矩核验"], "covered": True},
        ],
        "overall_score": 4.0,
        "recommendation": "approved_with_revision",
        "iterations": [],
        "uncertainty": "中",
    }


def test_run_stage5_no_llm_returns_placeholder(loaded_skill, sample_stage4b, sample_stage4a, sample_stage2):
    result = run_stage5_review(
        stage4b_payload=sample_stage4b,
        stage4a_payload=sample_stage4a,
        stage2_payload=sample_stage2,
        skill=loaded_skill,
        llm_client=None,
    )
    jsonschema.validate(instance=result, schema=loaded_skill.schemas["stage5"])
    assert result["stage4b_ref"] == sample_stage4b["stage4a_ref"]
    assert result["uncertainty"] == "高"
    assert result["recommendation"] in ("approved_with_revision", "rejected")
    assert len(result["review_panel"]) == 3


def test_run_stage5_with_valid_llm_output(loaded_skill, sample_stage4b, sample_stage4a, sample_stage2):
    scheme_id = sample_stage4b["stage4a_ref"]
    mock_llm = MagicMock()
    mock_llm.chat.completions.create.return_value.choices[0].message.content = (
        json.dumps(_valid_llm_resp(scheme_id), ensure_ascii=False)
    )
    result = run_stage5_review(
        stage4b_payload=sample_stage4b,
        stage4a_payload=sample_stage4a,
        stage2_payload=sample_stage2,
        skill=loaded_skill,
        llm_client=mock_llm,
    )
    jsonschema.validate(instance=result, schema=loaded_skill.schemas["stage5"])
    assert result["stage4b_ref"] == scheme_id
    assert result["overall_score"] == pytest.approx(4.0, abs=0.01)
    assert len(result["kc_traceability_matrix"]) == 2


def test_run_stage5_bad_json_falls_back(loaded_skill, sample_stage4b, sample_stage4a, sample_stage2):
    mock_llm = MagicMock()
    mock_llm.chat.completions.create.return_value.choices[0].message.content = "not valid json"
    result = run_stage5_review(
        stage4b_payload=sample_stage4b,
        stage4a_payload=sample_stage4a,
        stage2_payload=sample_stage2,
        skill=loaded_skill,
        llm_client=mock_llm,
    )
    jsonschema.validate(instance=result, schema=loaded_skill.schemas["stage5"])
    assert result["uncertainty"] == "高"


def test_run_stage5_high_severity_with_approved_fails_crossvalidate(loaded_skill, sample_stage4b, sample_stage4a, sample_stage2):
    """If LLM outputs approved + high severity issue, cross_validate rejects → PLACEHOLDER."""
    scheme_id = sample_stage4b["stage4a_ref"]
    bad_resp = _valid_llm_resp(scheme_id)
    bad_resp["recommendation"] = "approved"
    bad_resp["review_panel"][0]["severity_issues"] = [
        {"issue": "工序 P02 力矩超差风险极高", "severity": "high", "iterate_to": "4a"}
    ]
    mock_llm = MagicMock()
    mock_llm.chat.completions.create.return_value.choices[0].message.content = (
        json.dumps(bad_resp, ensure_ascii=False)
    )
    result = run_stage5_review(
        stage4b_payload=sample_stage4b,
        stage4a_payload=sample_stage4a,
        stage2_payload=sample_stage2,
        skill=loaded_skill,
        llm_client=mock_llm,
    )
    jsonschema.validate(instance=result, schema=loaded_skill.schemas["stage5"])
    assert result["uncertainty"] == "高"


def test_run_stage5_schema_fail_falls_back(loaded_skill, sample_stage4b, sample_stage4a, sample_stage2):
    """LLM returns JSON that fails schema (wrong recommendation value)."""
    scheme_id = sample_stage4b["stage4a_ref"]
    bad_resp = _valid_llm_resp(scheme_id)
    bad_resp["recommendation"] = "maybe"  # not in enum
    mock_llm = MagicMock()
    mock_llm.chat.completions.create.return_value.choices[0].message.content = (
        json.dumps(bad_resp, ensure_ascii=False)
    )
    result = run_stage5_review(
        stage4b_payload=sample_stage4b,
        stage4a_payload=sample_stage4a,
        stage2_payload=sample_stage2,
        skill=loaded_skill,
        llm_client=mock_llm,
    )
    jsonschema.validate(instance=result, schema=loaded_skill.schemas["stage5"])
    assert result["uncertainty"] == "高"


def test_placeholder_stage5_validates(loaded_skill, sample_stage4b):
    p = json.loads(json.dumps(PLACEHOLDER_STAGE5, ensure_ascii=False))
    p["stage4b_ref"] = sample_stage4b["stage4a_ref"]
    jsonschema.validate(instance=p, schema=loaded_skill.schemas["stage5"])


def test_run_stage5_fence_stripped_json(loaded_skill, sample_stage4b, sample_stage4a, sample_stage2):
    """LLM wraps output in ```json...``` — should be stripped and parsed correctly."""
    scheme_id = sample_stage4b["stage4a_ref"]
    raw = "```json\n" + json.dumps(_valid_llm_resp(scheme_id), ensure_ascii=False) + "\n```"
    mock_llm = MagicMock()
    mock_llm.chat.completions.create.return_value.choices[0].message.content = raw
    result = run_stage5_review(
        stage4b_payload=sample_stage4b,
        stage4a_payload=sample_stage4a,
        stage2_payload=sample_stage2,
        skill=loaded_skill,
        llm_client=mock_llm,
    )
    jsonschema.validate(instance=result, schema=loaded_skill.schemas["stage5"])
    assert result["stage4b_ref"] == scheme_id


def test_run_stage5_llm_exception_falls_back(loaded_skill, sample_stage4b, sample_stage4a, sample_stage2):
    """LLM raises exception → PLACEHOLDER."""
    mock_llm = MagicMock()
    mock_llm.chat.completions.create.side_effect = RuntimeError("API timeout")
    result = run_stage5_review(
        stage4b_payload=sample_stage4b,
        stage4a_payload=sample_stage4a,
        stage2_payload=sample_stage2,
        skill=loaded_skill,
        llm_client=mock_llm,
    )
    jsonschema.validate(instance=result, schema=loaded_skill.schemas["stage5"])
    assert result["uncertainty"] == "高"
```

- [ ] **Step 2: 运行测试确认全部 FAIL（模块未存在）**

```bash
python -m pytest tests/assembly/test_stage5_review.py -v 2>&1 | head -30
```

期望：`ImportError: cannot import name 'run_stage5_review'`

- [ ] **Step 3: 创建 `backend/pipelines/assembly_scheme/stage5_review.py`**

```python
"""backend/pipelines/assembly_scheme/stage5_review.py — S5 三角色虚拟评审."""

from __future__ import annotations
from typing import Any, Dict, List, Optional
import json
import logging
import jsonschema
from backend.pipelines.assembly_scheme.skill_loader import SkillRegistry

logger = logging.getLogger(__name__)

PLACEHOLDER_STAGE5: Dict[str, Any] = {
    "stage4b_ref": "PLACEHOLDER",
    "review_panel": [
        {
            "role": "工艺工程师",
            "findings": ["（占位）工序链未经验证，需 LLM 生成完整评审"],
            "severity_issues": [],
        },
        {
            "role": "质量工程师",
            "findings": ["（占位）KC 追溯矩阵待生成"],
            "severity_issues": [],
        },
        {
            "role": "设计工程师",
            "findings": ["（占位）需求覆盖度待核实"],
            "severity_issues": [],
        },
    ],
    "kc_traceability_matrix": [],
    "overall_score": 0.0,
    "recommendation": "approved_with_revision",
    "iterations": [],
    "uncertainty": "高",
}


def _cross_validate(obj: dict) -> bool:
    """Return False if high severity issues exist but recommendation is 'approved'."""
    has_high = any(
        si.get("severity") == "high"
        for reviewer in obj.get("review_panel", [])
        for si in reviewer.get("severity_issues", [])
    )
    if has_high and obj.get("recommendation") == "approved":
        logger.warning(
            "Stage5 cross-validate: recommendation='approved' but high severity issues present"
        )
        return False
    return True


def _build_prompt(
    skill: SkillRegistry,
    stage4b_payload: dict,
    stage4a_payload: dict,
    stage2_payload: dict,
    user_guidance: Optional[str],
) -> str:
    prompt_template = skill.prompts.get("s5_review", "")
    methodology = skill.methodology.get("s5_review_and_export", "")
    return (
        f"{prompt_template}\n\n"
        f"## 方法论上下文\n{methodology}\n\n"
        f"## S2 需求分析产物\n```json\n{json.dumps(stage2_payload, ensure_ascii=False, indent=2)}\n```\n\n"
        f"## S4a 工序链\n```json\n{json.dumps(stage4a_payload, ensure_ascii=False, indent=2)}\n```\n\n"
        f"## S4b 工装清单\n```json\n{json.dumps(stage4b_payload, ensure_ascii=False, indent=2)}\n```\n\n"
        f"## 评审指导意见\n{user_guidance or '（无）'}\n\n"
        "请生成符合 stage5.schema.json 的 JSON 对象："
    )


def _call_llm(llm_client: Any, prompt: str) -> Optional[str]:
    if llm_client is None:
        return None
    try:
        resp = llm_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}], temperature=0.2,
        )
        return resp.choices[0].message.content
    except Exception as e:
        logger.error("Stage5 LLM call failed: %s", e)
        return None


def _parse_and_validate(raw: str, schema: dict) -> Optional[Dict]:
    try:
        s = raw.strip()
        if s.startswith("```"):
            lines = s.splitlines()
            end = -1 if lines and lines[-1].strip() == "```" else len(lines)
            s = "\n".join(lines[1:end])
        obj = json.loads(s)
    except json.JSONDecodeError as e:
        logger.warning("Stage5 LLM JSON parse failed: %s; raw=%s", e, raw[:200])
        return None
    try:
        jsonschema.validate(instance=obj, schema=schema)
    except jsonschema.ValidationError as e:
        logger.warning("Stage5 LLM output failed schema: %s", e.message)
        return None
    if not _cross_validate(obj):
        return None
    return obj


def run_stage5_review(
    stage4b_payload: Dict[str, Any],
    stage4a_payload: Dict[str, Any],
    stage2_payload: Dict[str, Any],
    skill: SkillRegistry,
    llm_client: Any,
    neo4j_driver: Any = None,
    user_guidance: Optional[str] = None,
) -> Dict[str, Any]:
    """Execute S5 pipeline. Returns a dict valid per stage5.schema.json."""
    schema = skill.schemas["stage5"]
    scheme_id = stage4b_payload.get("stage4a_ref", "PLACEHOLDER")

    prompt = _build_prompt(skill, stage4b_payload, stage4a_payload, stage2_payload, user_guidance)
    raw = _call_llm(llm_client, prompt)
    parsed = _parse_and_validate(raw, schema) if raw else None

    if parsed is None:
        result = json.loads(json.dumps(PLACEHOLDER_STAGE5, ensure_ascii=False))
        result["stage4b_ref"] = scheme_id
        return result

    parsed["stage4b_ref"] = scheme_id
    return parsed
```

- [ ] **Step 4: 运行 8 条单元测试确认全部 PASS**

```bash
python -m pytest tests/assembly/test_stage5_review.py -v
```

期望：**8 passed**

- [ ] **Step 5: 运行全套 assembly 测试确认无回归**

```bash
python -m pytest tests/assembly/ -v --tb=short 2>&1 | tail -10
```

期望：之前 88 条 + 新增 8 条 = **96 passed**

- [ ] **Step 6: commit**

```bash
git add backend/pipelines/assembly_scheme/stage5_review.py tests/assembly/test_stage5_review.py
git commit -m "feat(assembly): implement stage5_review pipeline with 8 unit tests"
```

---

## Task 4: 路由激活 stage/5 + 实现 GET /export

**Files:**
- Modify: `backend/routers/assembly_design.py`

- [ ] **Step 1: 先在 `test_assembly_design_router.py` 中添加 stage/5 和 export 的测试**

在 `tests/assembly/test_assembly_design_router.py` 末尾追加：

```python
def test_stage5_requires_stage4b_first(client):
    """POST /stage/5 must 409 if stage4b has not been run."""
    create_resp = client.post(
        "/assembly-design/scheme/new",
        json={
            "subject_system": "PT6A HPC",
            "subject_scope": ["3 级轴流"],
            "design_intent": "工艺优化",
        },
    )
    scheme_id = create_resp.json()["scheme_id"]
    r = client.post(
        f"/assembly-design/scheme/{scheme_id}/stage/5",
        json={"action": "generate", "payload": {}},
    )
    assert r.status_code == 409, r.text
    assert "stage4b" in r.text.lower()


def test_stage5_runs_after_full_chain(client):
    """Happy path: S1 → S2 → S3 → S4a → S4b → S5."""
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
    for stage_key in ("1", "2", "3", "4a", "4b"):
        r = client.post(
            f"/assembly-design/scheme/{scheme_id}/stage/{stage_key}",
            json={"action": "generate", "payload": {}},
        )
        assert r.status_code == 200, f"stage {stage_key} failed: {r.text}"

    r5 = client.post(
        f"/assembly-design/scheme/{scheme_id}/stage/5",
        json={"action": "generate", "payload": {}},
    )
    assert r5.status_code == 200, r5.text
    body = r5.json()
    assert "review_panel" in body
    assert len(body["review_panel"]) == 3
    assert body["recommendation"] in ("approved", "approved_with_revision", "rejected")

    final = client.get(f"/assembly-design/scheme/{scheme_id}").json()
    assert "stage5" in final
    assert "5" in final["meta"]["stages_done"]


def test_export_requires_stage5_first(client):
    """GET /export must 409 if stage5 has not been run."""
    create_resp = client.post(
        "/assembly-design/scheme/new",
        json={
            "subject_system": "PT6A HPC",
            "subject_scope": ["3 级轴流"],
            "design_intent": "工艺优化",
        },
    )
    scheme_id = create_resp.json()["scheme_id"]
    r = client.get(f"/assembly-design/scheme/{scheme_id}/export")
    assert r.status_code == 409, r.text
    assert "stage5" in r.text.lower()


def test_export_generates_final_scheme_md(client):
    """GET /export after full chain returns export_path and content_md."""
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
    for stage_key in ("1", "2", "3", "4a", "4b", "5"):
        r = client.post(
            f"/assembly-design/scheme/{scheme_id}/stage/{stage_key}",
            json={"action": "generate", "payload": {}},
        )
        assert r.status_code == 200, f"stage {stage_key} failed: {r.text}"

    exp = client.get(f"/assembly-design/scheme/{scheme_id}/export")
    assert exp.status_code == 200, exp.text
    data = exp.json()
    assert "export_path" in data
    assert "content_md" in data
    assert "# 装配方案" in data["content_md"]
    assert scheme_id in data["content_md"]
```

- [ ] **Step 2: 运行新测试确认 FAIL**

```bash
python -m pytest tests/assembly/test_assembly_design_router.py::test_stage5_requires_stage4b_first tests/assembly/test_assembly_design_router.py::test_stage5_runs_after_full_chain tests/assembly/test_assembly_design_router.py::test_export_requires_stage5_first tests/assembly/test_assembly_design_router.py::test_export_generates_final_scheme_md -v 2>&1 | tail -20
```

期望：4 FAIL（501 vs 409 / 200）

- [ ] **Step 3: 修改 `backend/routers/assembly_design.py`**

**3a.** 在文件顶部 import 新增：

```python
from backend.pipelines.assembly_scheme.stage5_review import run_stage5_review
```

**3b.** 将 `run_stage` 函数中的 501 行：

```python
    # Stages not implemented yet
    if stage_key in {"4c", "4d", "5"}:
        raise HTTPException(501, f"stage {stage_key} not implemented yet")
```

改为：

```python
    # Stages not implemented yet
    if stage_key in {"4c", "4d"}:
        raise HTTPException(501, f"stage {stage_key} not implemented yet")
```

**3c.** 在 `elif stage_key == "4b":` 块之后、`stage_path.write_text(...)` 之前添加：

```python
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
```

**3d.** 将 `export_scheme` 函数替换为（实现真正的导出逻辑）：

```python
@router.get("/scheme/{scheme_id}/export")
def export_scheme(scheme_id: str):
    sd = _scheme_dir(scheme_id)
    if not sd.exists():
        raise HTTPException(404, f"scheme not found: {scheme_id}")
    stage5_path = sd / "stage5.json"
    if not stage5_path.exists():
        raise HTTPException(409, "stage5 must be generated before export")

    # Read all available stages
    stages: Dict[str, Any] = {}
    for sk in ("1", "2", "3", "4a", "4b", "5"):
        p = sd / f"stage{sk}.json"
        if p.exists():
            stages[sk] = json.loads(p.read_text(encoding="utf-8"))
    meta = _read_meta(scheme_id)

    lines = [
        f"# 装配方案导出报告",
        f"",
        f"**方案 ID**: `{scheme_id}`",
        f"**子系统**: {meta['subject']['system']}",
        f"**设计意图**: {meta['subject'].get('design_intent', '')}",
        f"**导出时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"",
        f"---",
        f"",
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
        lines.append(f"```json")
        lines.append(json.dumps(stages[sk], ensure_ascii=False, indent=2))
        lines.append(f"```")
        lines.append("")

    # Append KC traceability matrix as table
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
```

- [ ] **Step 4: 运行 4 条新路由测试确认 PASS**

```bash
python -m pytest tests/assembly/test_assembly_design_router.py::test_stage5_requires_stage4b_first tests/assembly/test_assembly_design_router.py::test_stage5_runs_after_full_chain tests/assembly/test_assembly_design_router.py::test_export_requires_stage5_first tests/assembly/test_assembly_design_router.py::test_export_generates_final_scheme_md -v
```

期望：**4 passed**

- [ ] **Step 5: commit**

```bash
git add backend/routers/assembly_design.py tests/assembly/test_assembly_design_router.py
git commit -m "feat(assembly): activate /scheme/{id}/stage/5 endpoint and implement GET /export"
```

---

## Task 5: 更新 E2E 测试中 stage 5 的断言

**Files:**
- Modify: `tests/assembly/test_e2e_s1_s2_s3.py`

- [ ] **Step 1: 找到并修改 stage 5 的断言**

在 `test_e2e_stage4_through_5_still_501` 函数中，将：

```python
    for sk in ("4c", "4d", "5"):
        r = client.post(
            f"/assembly-design/scheme/{scheme_id}/stage/{sk}",
            json={"action": "generate", "payload": {}},
        )
        assert r.status_code == 501, f"stage {sk} should still be 501, got {r.status_code}"
```

改为：

```python
    for sk in ("4c", "4d"):
        r = client.post(
            f"/assembly-design/scheme/{scheme_id}/stage/{sk}",
            json={"action": "generate", "payload": {}},
        )
        assert r.status_code == 501, f"stage {sk} should still be 501, got {r.status_code}"
    # stage 5 is now active: requires stage4b first, so returns 409 (not 501)
    r5 = client.post(
        f"/assembly-design/scheme/{scheme_id}/stage/5",
        json={"action": "generate", "payload": {}},
    )
    assert r5.status_code == 409, f"stage 5 should 409 (needs stage4b), got {r5.status_code}"
```

- [ ] **Step 2: 运行全套 assembly 测试确认全绿**

```bash
python -m pytest tests/assembly/ -v --tb=short 2>&1 | tail -15
```

期望：**所有测试 PASS**（88 旧 + 8 S5单元 + 4 路由新 = 100 passed）

- [ ] **Step 3: commit**

```bash
git add tests/assembly/test_e2e_s1_s2_s3.py
git commit -m "test(assembly): update E2E stage 5 assertion from 501 to 409"
```

---

## Task 6: 更新 PROJECT_GUIDE.md 和 SESSION_STATE.md

**Files:**
- Modify: `PROJECT_GUIDE.md`
- Modify: `SESSION_STATE.md`

- [ ] **Step 1: 在 PROJECT_GUIDE.md §16 末尾追加 P5 小节**

在 `PROJECT_GUIDE.md` 文件末尾（§16.P4 之后）追加：

```markdown
---

### 16.P5 Plan 5 进展 — S5 三角色虚拟评审与方案导出 (2026-05-14)

> 状态：Plan 5 完成 — S5 端到端可跑通，XXX 条 assembly 测试全绿。S1→S5 全链路贯通。

#### What
在 P4（S4b 工装规划）基础上，新增 S5（三角色虚拟评审 + KC 追溯矩阵 + final_scheme.md 导出）阶段，完成 Assembly Scheme Skill 主链路的最后一环。

**新增管道**
- `backend/pipelines/assembly_scheme/stage5_review.py`：`run_stage5_review()` — 三角色评审生成 + KC 追溯矩阵 + cross_validate（高危问题不可标记 approved）+ 四层降级 PLACEHOLDER

**升级 Skill 资产**
- `skills/aero-engine-assembly-scheme/templates/schemas/stage5.schema.json`：从 placeholder v1 升级为完整约束 schema（review_panel minItems=3，角色 enum，severity enum，uncertainty 必填）
- `skills/aero-engine-assembly-scheme/prompts/s5_review.prompt.md`：S5 LLM 提示词（三角色角色定义、KC 追溯规则、7条评审规则）

**路由激活**
- `backend/routers/assembly_design.py`：移除 `"5"` 的 501，新增 `elif stage_key == "5"` 分支（依赖 stage4b.json，否则 409）；实现 GET `/export` 端点（读全部 stage JSON → 生成 `final_scheme.md` + KC 追溯矩阵 Markdown 表格）

#### Why
S4b 输出的工装清单缺少质量可信度背书：没有 KC 追溯、没有 QC 点验证、没有三角色审查。S5 填补这一缺口，提供：① 三角色视角全面审查；② KC→工序→QC 四列追溯矩阵；③ 最终装配方案 Markdown 导出。`_cross_validate` 强制保证"approved 不可并存 high severity"，避免 LLM 自相矛盾。

#### How（核心调用链）

```
POST /assembly-design/scheme/{id}/stage/5
  → router: check stage4b.json exists (→ 409 if missing)
  → assembly_lock.acquire()
  → run_stage5_review(stage4b_payload, stage4a_payload, stage2_payload, skill, llm_client, ...)
      → _build_prompt(s5_review prompt + s5_review_and_export methodology + S2/S4a/S4b payloads)
      → LLM call（None/exception → PLACEHOLDER）
      → fence strip → json.loads（失败 → PLACEHOLDER）
      → jsonschema.validate(result, stage5.schema.json)（失败 → PLACEHOLDER）
      → _cross_validate(result)：high severity + "approved" → PLACEHOLDER
      → 强制覆写 stage4b_ref（继承 scheme_id from stage4b["stage4a_ref"]）
      → 返回 stage5 dict
  → 写 stage5.json，更新 meta.json stages_done += "5"
  → assembly_lock.release()

GET /assembly-design/scheme/{id}/export
  → check stage5.json exists (→ 409 if missing)
  → 读取所有 stageN.json → 生成 Markdown（含 KC 追溯表格）
  → 写 final_scheme.md → 返回 {export_path, content_md}
```

**降级策略（四层保险）**
1. LLM=None → 直接返回 PLACEHOLDER（3 角色占位，`uncertainty:"高"`）
2. LLM 调用异常 → PLACEHOLDER
3. LLM JSON 无效 → PLACEHOLDER
4. schema 校验失败 或 cross_validate 失败（high+approved 矛盾）→ PLACEHOLDER

#### Where（证据）
- 单元测试：`tests/assembly/test_stage5_review.py`（8 tests：no_llm/valid_llm/bad_json/high_severity_approved/schema_fail/fence_strip/llm_exception/placeholder_validates）
- 路由测试：`tests/assembly/test_assembly_design_router.py`（含 stage5 409 门控 + S1→S5 happy path + export 409/200）
- 更新 E2E：`tests/assembly/test_e2e_s1_s2_s3.py`（5 从 501 改为 409 断言）
- 全套结果：**100 passed**（branch `feat/assembly-scheme-p2-s2-s3`）
```

- [ ] **Step 2: 清理 SESSION_STATE.md（Plan 5 完成）**

将 SESSION_STATE.md 更新为：

```markdown
# SESSION_STATE.md — 热记忆

## [Plan 5 已完成（2026-05-14）— Assembly Scheme Skill S1→S5 全链路贯通]

**Plan 5（Assembly Scheme Skill S5 评审与导出）已完成**，branch `feat/assembly-scheme-p2-s2-s3`，100 tests 全绿。

### 已交付内容
- `backend/pipelines/assembly_scheme/stage5_review.py`：三角色评审 + KC 追溯矩阵 + 四层降级保险 + `_cross_validate()`（high severity 不可标 approved）
- `skills/aero-engine-assembly-scheme/templates/schemas/stage5.schema.json`：完整约束 schema
- `skills/aero-engine-assembly-scheme/prompts/s5_review.prompt.md`：S5 LLM 提示词
- `backend/routers/assembly_design.py`：stage/5 路由激活（依赖 stage4b） + GET /export 导出实现
- `PROJECT_GUIDE.md §16.P5`：已更新（3W1H 标准）
- 证据：`tests/assembly/`（100 tests，含 8 个 S5 单元测试 + S5 路由 E2E 测试）

### Assembly Scheme Skill 全阶段状态
| 阶段 | 状态 | Plan |
|------|------|------|
| S1 任务调研 | ✅ 完成 | P1 |
| S2 需求分析 | ✅ 完成 | P2 |
| S3 概念架构 | ✅ 完成 | P2 |
| S4a 工序总表 | ✅ 完成 | P3 |
| S4b 工装规划 | ✅ 完成 | P4 |
| S4c 公差分配 | ⏭ 跳过（数据不足） | — |
| S4d 关键件控制 | ⏭ 跳过（数据不足） | — |
| S5 评审与导出 | ✅ 完成 | P5 |

### 后续建议
1. **前端集成**：在 KG 阶段组件中接入 assembly-design 端点，展示 S5 评审报告 + KC 追溯矩阵
2. **KG 诊断**：按 bubbly-chasing-pizza.md P0 实施 docx BOM 解析器
3. **开新会话**：请陛下开启新对话（Reset Session）以节约 Token

## [PT6A 实验最终结果（A+B 改进后，2026-05-03）]

### Tier-1 主表（60 题）
| Baseline | Recall@5 | MRR | Hit@1 | Judge.Rel | Judge.Comp | Judge.Corr |
|---|---|---|---|---|---|---|
| B1 Dense | 0.778 | 0.992 | **0.983** | 3.38 | 2.88 | 2.12 |
| B2 BM25 | 0.719 | 0.938 | 0.900 | 3.43 | 2.78 | 2.00 |
| B3 Hybrid | 0.769 | 0.983 | 0.967 | 3.48 | 2.88 | 2.05 |
| B4 +CLIP | 0.769 | 0.983 | 0.967 | 3.42 | 2.93 | 2.25 |
| B5 +KG | 0.697 | 0.926 | 0.867 | 3.50 | 3.02 | **2.35** |
| **B6 Full** | 0.697 | 0.926 | 0.867 | **3.63** | **3.15** | 2.33 |
```

- [ ] **Step 3: commit 文档更新**

```bash
git add PROJECT_GUIDE.md SESSION_STATE.md
git commit -m "docs: PROJECT_GUIDE 16.P5 -- Plan 5 complete (S5 review & export, 100 tests green)"
```

---

## 自查清单

**Spec coverage:**
- [x] 三角色虚拟评审（工艺/质量/设计）→ `review_panel` in stage5_review.py
- [x] KC → 工序 → QC 追溯矩阵 → `kc_traceability_matrix` in schema + prompt
- [x] 虚拟试装迭代（high severity → iterate_to）→ `_cross_validate()` + `iterations`
- [x] 导出 final_scheme.md → `GET /export` 端点
- [x] 四层降级 PLACEHOLDER → LLM=None/exception/bad json/schema/cross_validate
- [x] stage 5 门控（需要 stage4b.json）→ 409
- [x] export 门控（需要 stage5.json）→ 409

**No placeholders:** 所有 step 都有实际代码。

**Type consistency:** `stage4b_ref` 贯穿 PLACEHOLDER_STAGE5、schema、pipeline 函数返回值；路由读取 `stage4b_payload["stage4a_ref"]` 作为 scheme_id（与 stage4b_tooling.py 一致）。
