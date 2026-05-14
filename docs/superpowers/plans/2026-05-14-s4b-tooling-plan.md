# S4b 工装选型 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现 S4b 工装选型阶段——基于 S4a 工序链，通过 LLM + KG 查询生成带分类/成本层级/工艺性反馈的工装规划 JSON，激活 `POST /assembly-design/scheme/{id}/stage/4b` 端点。

**Architecture:** 完全镜像 `stage4a_process.py` 模式：单次 LLM 调用 + KG 预填充 + 四层降级保险（LLM=None / 无效 JSON / schema 校验失败 / 交叉引用完整性失败均返回 PLACEHOLDER）。新增 `_cross_validate()` 函数校验 `used_in_procedures` 和 `tooling_constraints` 中的 id 引用完整性。

**Tech Stack:** Python 3.10, jsonschema, FastAPI, pytest, neo4j-driver（可选）

---

## File Map

| 文件 | 操作 | 说明 |
|------|------|------|
| `skills/aero-engine-assembly-scheme/templates/schemas/stage4b.schema.json` | 新建 | S4b 正式 schema |
| `skills/aero-engine-assembly-scheme/prompts/s4b_tooling.prompt.md` | 新建 | LLM 提示词模板 |
| `backend/pipelines/assembly_scheme/stage4b_tooling.py` | 新建 | `run_stage4b_tooling()` 主管道 |
| `backend/routers/assembly_design.py` | 修改 L136、L217-218 | 激活 stage/4b，移除 501 |
| `tests/assembly/test_stage4b_tooling.py` | 新建 | 8 条单元测试 |
| `tests/assembly/test_assembly_design_router.py` | 修改末尾 | 补 2 条路由测试 |
| `tests/assembly/test_e2e_s1_s2_s3.py` | 修改 | 4b 从 501 改为 409 断言 |

---

### Task 1: 创建 stage4b.schema.json

**Files:**
- Create: `skills/aero-engine-assembly-scheme/templates/schemas/stage4b.schema.json`

- [ ] **Step 1: 写入 schema 文件**

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "stage4b.schema.json",
  "title": "Stage 4b — Tooling Plan",
  "type": "object",
  "required": ["stage4a_ref", "tools", "dfa_tooling_score"],
  "properties": {
    "stage4a_ref": {
      "type": "string",
      "pattern": "^scheme-[0-9]{8}-[a-f0-9]{6}$"
    },
    "tools": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": ["id", "name", "category", "cost_tier", "used_in_procedures"],
        "properties": {
          "id": {"type": "string", "pattern": "^T[0-9]{2,}$"},
          "name": {"type": "string", "minLength": 2},
          "category": {"type": "string", "enum": ["generic", "special"]},
          "cost_tier": {"type": "string", "enum": ["低", "中", "高"]},
          "used_in_procedures": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 1
          },
          "design_requirements": {"type": "string"},
          "notes": {"type": "string"}
        }
      }
    },
    "tooling_constraints": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["procedure_id", "tool_id", "issue", "suggested_action"],
        "properties": {
          "procedure_id": {"type": "string"},
          "tool_id": {"type": "string"},
          "issue": {"type": "string", "minLength": 5},
          "suggested_action": {"type": "string", "minLength": 5}
        }
      }
    },
    "dfa_tooling_score": {"type": "number", "minimum": 0, "maximum": 1},
    "uncertainty": {"type": "string", "enum": ["高", "中", "低"]}
  }
}
```

- [ ] **Step 2: 验证 schema 文件本身合法（Python 一行）**

```bash
"C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" -c "import json,jsonschema; s=json.load(open('skills/aero-engine-assembly-scheme/templates/schemas/stage4b.schema.json',encoding='utf-8')); print('OK', s['title'])"
```

Expected output: `OK Stage 4b — Tooling Plan`

- [ ] **Step 3: Commit**

```bash
git add skills/aero-engine-assembly-scheme/templates/schemas/stage4b.schema.json
git commit -m "feat(assembly): add stage4b.schema.json for tooling plan"
```

---

### Task 2: 创建 s4b_tooling.prompt.md

**Files:**
- Create: `skills/aero-engine-assembly-scheme/prompts/s4b_tooling.prompt.md`

- [ ] **Step 1: 写入 prompt 文件**

```markdown
# System

你是航空发动机装配工艺资深专家，正在执行装配方案设计 skill 的 **S4b 阶段（工装选型）**。

你的目标：基于 S4a 工序总表，对每条工序所需工装进行分类（通用/专用）、成本估级，并识别工艺性约束（哪些工序因工装体积/可达性受限）。

## 必须遵守

1. 输出严格符合 `templates/schemas/stage4b.schema.json`
2. 每个工装 `id` 必须是 T01/T02/T03… 连续编号
3. `used_in_procedures` 只能引用 S4a `procedures` 中存在的 id（P01/P02…）
4. `category: "special"` 时 `design_requirements` 必须非空，描述专用工装的设计约束
5. `dfa_tooling_score` = generic 工装数 / 总工装数（自行计算，保留两位小数）
6. **绝不杜撰** CMM 工具号或具体价格；不确定时 `notes: "见 CMM"` 或 `"待确认"`
7. `tooling_constraints` 仅列出真正影响工序顺序或可行性的约束；若无约束填空列表 `[]`
8. `uncertainty: "高"` 时工装数量不超过 5 条

## 输入变量

- `stage4a_payload`：S4a 完整产物（含工序链和每条工序的 tooling 名称列表）
- `kg_tools`：KG 查询到的已有 Tool 节点（可能为空）
- `user_guidance`：HITL 指导意见；可能为空

## 输出格式

仅输出 JSON 对象，不要 markdown 代码块包裹。

## 反模式（禁止）

- ❌ `used_in_procedures` 引用不存在的工序 id
- ❌ `tooling_constraints.tool_id` 引用不在 tools 列表中的 id
- ❌ `category: "special"` 而 `design_requirements` 为空或缺失
- ❌ `dfa_tooling_score` > 1 或 < 0
- ❌ 相同工装名称出现两次（必须去重合并 used_in_procedures）
```

- [ ] **Step 2: Commit**

```bash
git add skills/aero-engine-assembly-scheme/prompts/s4b_tooling.prompt.md
git commit -m "feat(assembly): add s4b_tooling.prompt.md"
```

---

### Task 3: 实现 stage4b_tooling.py（先写测试，再实现）

**Files:**
- Create: `tests/assembly/test_stage4b_tooling.py`
- Create: `backend/pipelines/assembly_scheme/stage4b_tooling.py`

- [ ] **Step 1: 写测试文件（8 条用例，先让它们全部 ImportError 失败）**

创建 `tests/assembly/test_stage4b_tooling.py`：

```python
"""Tests for backend.pipelines.assembly_scheme.stage4b_tooling.run_stage4b_tooling."""
from pathlib import Path
from unittest.mock import MagicMock
import json
import pytest
import jsonschema

from backend.pipelines.assembly_scheme.stage4b_tooling import (
    run_stage4b_tooling,
    PLACEHOLDER_STAGE4B,
    query_kg_tools,
)
from backend.pipelines.assembly_scheme.skill_loader import SkillRegistry

SKILL_ROOT = Path(__file__).resolve().parents[2] / "skills" / "aero-engine-assembly-scheme"


@pytest.fixture(scope="module")
def loaded_skill():
    reg = SkillRegistry(SKILL_ROOT)
    reg.load()
    return reg


@pytest.fixture
def sample_stage4a():
    return {
        "stage3_ref": "scheme-20260511-aaaaaa",
        "architecture_ref": "A1",
        "procedures": [
            {
                "id": "P01",
                "name": "后轴承座定位装夹",
                "seq_no": 1,
                "depends_on": [],
                "parts_involved": ["后轴承座"],
                "tooling": ["定位夹具 JIG-001"],
                "spec_values": [{"param": "定位精度", "value": "±0.02mm"}],
            },
            {
                "id": "P02",
                "name": "转子鼓筒套装",
                "seq_no": 2,
                "depends_on": ["P01"],
                "parts_involved": ["转子鼓筒"],
                "tooling": ["液压套装工具"],
                "spec_values": [{"param": "热套温度", "value": "见 CMM"}],
            },
            {
                "id": "P03",
                "name": "前法兰螺栓紧固",
                "seq_no": 3,
                "depends_on": ["P02"],
                "parts_involved": ["法兰螺栓 M8"],
                "tooling": ["扭矩扳手"],
                "spec_values": [{"param": "力矩", "value": "见 CMM"}],
            },
        ],
        "topology": {
            "sequence": ["P01", "P02", "P03"],
            "method": "DFA-heuristic",
            "dfa_efficiency": 0.72,
        },
        "uncertainty": "中",
    }


def _valid_llm_resp(scheme_id: str) -> dict:
    return {
        "stage4a_ref": scheme_id,
        "tools": [
            {
                "id": "T01",
                "name": "定位夹具 JIG-001",
                "category": "special",
                "cost_tier": "高",
                "used_in_procedures": ["P01"],
                "design_requirements": "需定制，用于后轴承座精密定位",
            },
            {
                "id": "T02",
                "name": "液压套装工具",
                "category": "special",
                "cost_tier": "高",
                "used_in_procedures": ["P02"],
                "design_requirements": "液压驱动，最大压力 200MPa",
            },
            {
                "id": "T03",
                "name": "扭矩扳手",
                "category": "generic",
                "cost_tier": "低",
                "used_in_procedures": ["P03"],
                "notes": "标准扭矩扳手，量程 10-100 N·m",
            },
        ],
        "tooling_constraints": [
            {
                "procedure_id": "P02",
                "tool_id": "T02",
                "issue": "液压套装工具体积大，需工件翻转后操作",
                "suggested_action": "考虑在 P01 后增加工件翻转工序",
            }
        ],
        "dfa_tooling_score": 0.33,
        "uncertainty": "中",
    }


def test_run_stage4b_no_llm_returns_placeholder(loaded_skill, sample_stage4a):
    result = run_stage4b_tooling(
        stage4a_payload=sample_stage4a,
        skill=loaded_skill,
        llm_client=None,
        neo4j_driver=None,
    )
    jsonschema.validate(instance=result, schema=loaded_skill.schemas["stage4b"])
    assert result["stage4a_ref"] == sample_stage4a["stage3_ref"]
    assert len(result["tools"]) >= 1
    assert result["uncertainty"] == "高"
    # All used_in_procedures must reference real S4a proc ids
    proc_ids = {p["id"] for p in sample_stage4a["procedures"]}
    for tool in result["tools"]:
        for pid in tool["used_in_procedures"]:
            assert pid in proc_ids, f"placeholder tool {tool['id']} refs missing proc {pid}"


def test_query_kg_tools_no_driver_returns_empty():
    rows = query_kg_tools(None, "PT6A HPC")
    assert rows == []


def test_query_kg_tools_handles_exception():
    bad_driver = MagicMock()
    bad_driver.session.side_effect = RuntimeError("neo4j down")
    rows = query_kg_tools(bad_driver, "PT6A HPC")
    assert rows == []


def test_run_stage4b_with_valid_llm_output(loaded_skill, sample_stage4a):
    scheme_id = sample_stage4a["stage3_ref"]
    mock_llm = MagicMock()
    mock_llm.chat.completions.create.return_value.choices[0].message.content = (
        json.dumps(_valid_llm_resp(scheme_id), ensure_ascii=False)
    )
    result = run_stage4b_tooling(
        stage4a_payload=sample_stage4a,
        skill=loaded_skill,
        llm_client=mock_llm,
        neo4j_driver=None,
    )
    jsonschema.validate(instance=result, schema=loaded_skill.schemas["stage4b"])
    assert result["stage4a_ref"] == scheme_id
    assert len(result["tools"]) == 3
    assert result["dfa_tooling_score"] == pytest.approx(0.33, abs=0.01)
    assert len(result["tooling_constraints"]) == 1


def test_run_stage4b_bad_json_falls_back(loaded_skill, sample_stage4a):
    mock_llm = MagicMock()
    mock_llm.chat.completions.create.return_value.choices[0].message.content = "not json"
    result = run_stage4b_tooling(
        stage4a_payload=sample_stage4a,
        skill=loaded_skill,
        llm_client=mock_llm,
        neo4j_driver=None,
    )
    jsonschema.validate(instance=result, schema=loaded_skill.schemas["stage4b"])
    assert result["uncertainty"] == "高"


def test_run_stage4b_dangling_procedure_ref_falls_back(loaded_skill, sample_stage4a):
    """used_in_procedures references a procedure id (P99) that doesn't exist in S4a."""
    scheme_id = sample_stage4a["stage3_ref"]
    bad_resp = _valid_llm_resp(scheme_id)
    bad_resp["tools"][0]["used_in_procedures"] = ["P99"]  # P99 doesn't exist
    mock_llm = MagicMock()
    mock_llm.chat.completions.create.return_value.choices[0].message.content = (
        json.dumps(bad_resp, ensure_ascii=False)
    )
    result = run_stage4b_tooling(
        stage4a_payload=sample_stage4a,
        skill=loaded_skill,
        llm_client=mock_llm,
        neo4j_driver=None,
    )
    jsonschema.validate(instance=result, schema=loaded_skill.schemas["stage4b"])
    assert result["uncertainty"] == "高"


def test_run_stage4b_dangling_constraint_tool_ref_falls_back(loaded_skill, sample_stage4a):
    """tooling_constraints references a tool id (T99) not in tools list."""
    scheme_id = sample_stage4a["stage3_ref"]
    bad_resp = _valid_llm_resp(scheme_id)
    bad_resp["tooling_constraints"][0]["tool_id"] = "T99"  # T99 not in tools
    mock_llm = MagicMock()
    mock_llm.chat.completions.create.return_value.choices[0].message.content = (
        json.dumps(bad_resp, ensure_ascii=False)
    )
    result = run_stage4b_tooling(
        stage4a_payload=sample_stage4a,
        skill=loaded_skill,
        llm_client=mock_llm,
        neo4j_driver=None,
    )
    jsonschema.validate(instance=result, schema=loaded_skill.schemas["stage4b"])
    assert result["uncertainty"] == "高"


def test_placeholder_stage4b_validates(loaded_skill, sample_stage4a):
    p = json.loads(json.dumps(PLACEHOLDER_STAGE4B, ensure_ascii=False))
    p["stage4a_ref"] = sample_stage4a["stage3_ref"]
    # Fix used_in_procedures to point at real proc ids
    proc_ids = [proc["id"] for proc in sample_stage4a["procedures"]]
    for tool in p["tools"]:
        tool["used_in_procedures"] = [proc_ids[0]]
    jsonschema.validate(instance=p, schema=loaded_skill.schemas["stage4b"])
```

- [ ] **Step 2: 运行测试确认全部失败（ImportError）**

```bash
cd "C:\xjp\代码\rag-demo" && "C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" -m pytest tests/assembly/test_stage4b_tooling.py -v 2>&1 | tail -15
```

Expected: 所有测试 ERROR with `ImportError: cannot import name 'run_stage4b_tooling'`

- [ ] **Step 3: 创建 stage4b_tooling.py**

创建 `backend/pipelines/assembly_scheme/stage4b_tooling.py`：

```python
"""backend/pipelines/assembly_scheme/stage4b_tooling.py — S4b Tooling planning."""

from __future__ import annotations
from typing import Any, Dict, List, Optional
import json
import logging
import jsonschema
from backend.pipelines.assembly_scheme.skill_loader import SkillRegistry

logger = logging.getLogger(__name__)

PLACEHOLDER_STAGE4B: Dict[str, Any] = {
    "stage4a_ref": "PLACEHOLDER",
    "tools": [
        {
            "id": "T01",
            "name": "（占位）通用定位夹具",
            "category": "generic",
            "cost_tier": "低",
            "used_in_procedures": ["P01"],
            "notes": "占位，待 chamberlain 补全",
        },
        {
            "id": "T02",
            "name": "（占位）专用套装工具",
            "category": "special",
            "cost_tier": "高",
            "used_in_procedures": ["P01"],
            "design_requirements": "（占位）待补充设计要求",
        },
        {
            "id": "T03",
            "name": "（占位）通用扭矩扳手",
            "category": "generic",
            "cost_tier": "低",
            "used_in_procedures": ["P01"],
            "notes": "占位",
        },
    ],
    "tooling_constraints": [],
    "dfa_tooling_score": 0.67,
    "uncertainty": "高",
}


def query_kg_tools(neo4j_driver: Any, subject_name: str) -> List[Dict]:
    """Query existing Tool nodes and requires relationships from KG."""
    if neo4j_driver is None:
        return []
    try:
        with neo4j_driver.session() as session:
            rows = session.run(
                "MATCH (t:Tool) "
                "WHERE coalesce(t.kg_name, '') CONTAINS $subj "
                "OPTIONAL MATCH (p:Procedure)-[:requires]->(t) "
                "RETURN t.kg_name AS name, t.tool_type AS tool_type, "
                "       p.kg_name AS used_in_procedure LIMIT 30",
                subj=subject_name,
            ).data()
            return rows
    except Exception as e:
        logger.warning("Stage4b KG tool query failed: %s", e)
        return []


def _cross_validate(obj: dict, stage4a_payload: dict) -> bool:
    """Return True if all id cross-references are valid, False otherwise."""
    proc_ids = {p["id"] for p in stage4a_payload.get("procedures", [])}
    tool_ids = {t["id"] for t in obj.get("tools", [])}

    for tool in obj.get("tools", []):
        for pid in tool.get("used_in_procedures", []):
            if pid not in proc_ids:
                logger.warning(
                    "Stage4b cross-validate: tool %s refs unknown proc %s", tool["id"], pid
                )
                return False

    for constraint in obj.get("tooling_constraints", []):
        pid = constraint.get("procedure_id", "")
        tid = constraint.get("tool_id", "")
        if pid not in proc_ids:
            logger.warning("Stage4b cross-validate: constraint refs unknown proc %s", pid)
            return False
        if tid not in tool_ids:
            logger.warning("Stage4b cross-validate: constraint refs unknown tool %s", tid)
            return False

    return True


def _build_prompt(skill, stage4a_payload, kg_tools, user_guidance):
    prompt_template = skill.prompts.get("s4b_tooling", "")
    methodology = skill.methodology.get("s4_detailed_process", "")
    return (
        f"{prompt_template}\n\n"
        f"## 方法论上下文\n{methodology}\n\n"
        f"## S4a 产物\n```json\n{json.dumps(stage4a_payload, ensure_ascii=False, indent=2)}\n```\n\n"
        f"## KG 已有工装节点\n```json\n{json.dumps(kg_tools, ensure_ascii=False, indent=2)}\n```\n\n"
        f"## chamberlain 指导意见\n{user_guidance or '（无）'}\n\n"
        "请生成符合 stage4b.schema.json 的 JSON 对象："
    )


def _call_llm(llm_client, prompt):
    if llm_client is None:
        return None
    try:
        resp = llm_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}], temperature=0.2,
        )
        return resp.choices[0].message.content
    except Exception as e:
        logger.error("Stage4b LLM call failed: %s", e)
        return None


def _parse_and_validate(raw: str, schema: dict, stage4a_payload: dict) -> Optional[Dict]:
    try:
        s = raw.strip()
        if s.startswith("```"):
            s = s.strip("`")
            if s.lower().startswith("json\n"):
                s = s[5:]
        obj = json.loads(s)
    except json.JSONDecodeError as e:
        logger.warning("Stage4b LLM JSON parse failed: %s; raw=%s", e, raw[:200])
        return None
    try:
        jsonschema.validate(instance=obj, schema=schema)
    except jsonschema.ValidationError as e:
        logger.warning("Stage4b LLM output failed schema: %s", e.message)
        return None
    if not _cross_validate(obj, stage4a_payload):
        return None
    return obj


def run_stage4b_tooling(
    stage4a_payload: Dict[str, Any],
    skill: SkillRegistry,
    llm_client: Any,
    neo4j_driver: Any = None,
    user_guidance: Optional[str] = None,
) -> Dict[str, Any]:
    """Execute S4b pipeline. Returns a dict valid per stage4b.schema.json."""
    schema = skill.schemas["stage4b"]
    scheme_id = stage4a_payload.get("stage3_ref", "PLACEHOLDER")

    subject_name = stage4a_payload.get("subject", {}).get("system", "")

    kg_tools = query_kg_tools(neo4j_driver, subject_name)
    prompt = _build_prompt(skill, stage4a_payload, kg_tools, user_guidance)
    raw = _call_llm(llm_client, prompt)
    parsed = _parse_and_validate(raw, schema, stage4a_payload) if raw else None

    if parsed is None:
        result = json.loads(json.dumps(PLACEHOLDER_STAGE4B, ensure_ascii=False))
        result["stage4a_ref"] = scheme_id
        # Fix used_in_procedures to reference real S4a procedure ids
        proc_ids = [p["id"] for p in stage4a_payload.get("procedures", [])]
        if proc_ids:
            for tool in result["tools"]:
                tool["used_in_procedures"] = [proc_ids[0]]
        return result

    parsed["stage4a_ref"] = scheme_id
    return parsed
```

- [ ] **Step 4: 运行测试确认全部通过**

```bash
cd "C:\xjp\代码\rag-demo" && "C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" -m pytest tests/assembly/test_stage4b_tooling.py -v 2>&1 | tail -20
```

Expected: `8 passed`

- [ ] **Step 5: Commit**

```bash
git add backend/pipelines/assembly_scheme/stage4b_tooling.py tests/assembly/test_stage4b_tooling.py
git commit -m "feat(assembly): implement stage4b_tooling pipeline with 8 unit tests"
```

---

### Task 4: 激活路由 stage/4b

**Files:**
- Modify: `backend/routers/assembly_design.py`

- [ ] **Step 1: 先写路由失败测试（追加到 test_assembly_design_router.py 末尾）**

在 `tests/assembly/test_assembly_design_router.py` 末尾追加：

```python
def test_stage4b_requires_stage4a_first(client):
    """POST /stage/4b must 409 if stage4a has not been run."""
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
        f"/assembly-design/scheme/{scheme_id}/stage/4b",
        json={"action": "generate", "payload": {}},
    )
    assert r.status_code == 409, r.text
    assert "stage4a" in r.text.lower()


def test_stage4b_runs_after_full_chain(client):
    """Happy path: S1 → S2 → S3 → S4a → S4b."""
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
    for stage in ("1", "2", "3", "4a"):
        r = client.post(
            f"/assembly-design/scheme/{scheme_id}/stage/{stage}",
            json={"action": "generate", "payload": {}},
        )
        assert r.status_code == 200, f"stage {stage} failed: {r.text}"

    r4b = client.post(
        f"/assembly-design/scheme/{scheme_id}/stage/4b",
        json={"action": "generate", "payload": {}},
    )
    assert r4b.status_code == 200, r4b.text
    body = r4b.json()
    assert "tools" in body
    assert len(body["tools"]) >= 1
    assert "dfa_tooling_score" in body
    # Verify stored in scheme
    final = client.get(f"/assembly-design/scheme/{scheme_id}").json()
    assert "stage4b" in final
    assert "4b" in final["meta"]["stages_done"]
```

- [ ] **Step 2: 运行路由测试确认两条新测试失败（501）**

```bash
cd "C:\xjp\代码\rag-demo" && "C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" -m pytest tests/assembly/test_assembly_design_router.py::test_stage4b_requires_stage4a_first tests/assembly/test_assembly_design_router.py::test_stage4b_runs_after_full_chain -v 2>&1 | tail -15
```

Expected: 2 FAILED（`stage4b` 仍返回 501）

- [ ] **Step 3: 修改 assembly_design.py**

**修改1**：在 `backend/routers/assembly_design.py` 第 29 行附近，在现有 import 后添加：

```python
from backend.pipelines.assembly_scheme.stage4b_tooling import run_stage4b_tooling
```

**修改2**：将第 136 行：
```python
    if stage_key in {"4b", "4c", "4d", "5"}:
        raise HTTPException(501, f"stage {stage_key} not implemented yet")
```
改为：
```python
    if stage_key in {"4c", "4d", "5"}:
        raise HTTPException(501, f"stage {stage_key} not implemented yet")
```

**修改3**：在 `elif stage_key == "4a":` 块（约第 206-217 行）之后，`stage_path.write_text(` 之前，插入：

```python
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
```

- [ ] **Step 4: 运行路由测试确认两条新测试通过**

```bash
cd "C:\xjp\代码\rag-demo" && "C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" -m pytest tests/assembly/test_assembly_design_router.py::test_stage4b_requires_stage4a_first tests/assembly/test_assembly_design_router.py::test_stage4b_runs_after_full_chain -v 2>&1 | tail -15
```

Expected: `2 passed`

- [ ] **Step 5: Commit**

```bash
git add backend/routers/assembly_design.py tests/assembly/test_assembly_design_router.py
git commit -m "feat(assembly): activate stage/4b endpoint with 409 gate and happy path"
```

---

### Task 5: 修复 e2e 测试断言 + 全量验证

**Files:**
- Modify: `tests/assembly/test_e2e_s1_s2_s3.py`

- [ ] **Step 1: 更新 e2e 测试中 4b 的断言**

在 `tests/assembly/test_e2e_s1_s2_s3.py` 中找到：

```python
    r4a = client.post(
        f"/assembly-design/scheme/{scheme_id}/stage/4a",
        json={"action": "generate", "payload": {}},
    )
    assert r4a.status_code == 409, f"stage 4a should 409 (needs stage3), got {r4a.status_code}"
    for sk in ("4b", "4c", "4d", "5"):
        r = client.post(
            f"/assembly-design/scheme/{scheme_id}/stage/{sk}",
            json={"action": "generate", "payload": {}},
        )
        assert r.status_code == 501, f"stage {sk} should still be 501, got {r.status_code}"
```

替换为：

```python
    r4a = client.post(
        f"/assembly-design/scheme/{scheme_id}/stage/4a",
        json={"action": "generate", "payload": {}},
    )
    assert r4a.status_code == 409, f"stage 4a should 409 (needs stage3), got {r4a.status_code}"
    # 4b is now active (409 without prior stage4a); 4c-5 remain 501
    r4b = client.post(
        f"/assembly-design/scheme/{scheme_id}/stage/4b",
        json={"action": "generate", "payload": {}},
    )
    assert r4b.status_code == 409, f"stage 4b should 409 (needs stage4a), got {r4b.status_code}"
    for sk in ("4c", "4d", "5"):
        r = client.post(
            f"/assembly-design/scheme/{scheme_id}/stage/{sk}",
            json={"action": "generate", "payload": {}},
        )
        assert r.status_code == 501, f"stage {sk} should still be 501, got {r.status_code}"
```

- [ ] **Step 2: 运行全量测试**

```bash
cd "C:\xjp\代码\rag-demo" && "C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" -m pytest tests/assembly/ -v 2>&1 | tail -25
```

Expected: `88 passed` (78 existing + 8 unit + 2 router)

- [ ] **Step 3: Commit**

```bash
git add tests/assembly/test_e2e_s1_s2_s3.py
git commit -m "test(assembly): update e2e assertion — stage4b now 409 (not 501)"
```

---

### Task 6: 更新文档

**Files:**
- Modify: `PROJECT_GUIDE.md`
- Modify: `SESSION_STATE.md`

- [ ] **Step 1: 在 PROJECT_GUIDE.md §15 变更日志追加一行**

在 `| 2026-05-14 | Assembly Scheme Skill Plan 3 (S4a)…` 行之后插入：

```
| 2026-05-14 | Assembly Scheme Skill Plan 4 (S4b)：新增 stage4b_tooling.py（KG 工装查询 + LLM 分类 + 交叉引用校验）+ stage4b.schema.json + s4b_tooling.prompt.md；路由激活 stage/4b（需 stage4a 前置）；88 tests 全绿 |
```

- [ ] **Step 2: 在 PROJECT_GUIDE.md 末尾追加 §16.P4 章节**

```markdown
---

### 16.P4 Plan 4 进展 — S4b 工装选型 (2026-05-14)

> 状态：Plan 4 完成 — S4b 端到端可跑通，88 条 assembly 测试全绿。

#### What
在 P3（S4a 工序排序）基础上，新增 S4b（工装选型）阶段，将工序链中的工装名称升级为带分类/成本/工艺性约束的结构化工装规划。

**新增管道**
- `backend/pipelines/assembly_scheme/stage4b_tooling.py`：`run_stage4b_tooling()` — KG 工装预查询 + LLM 分类（generic/special）+ 成本层级 + 四层降级保险 + `_cross_validate()` 交叉引用完整性校验

**新增 Skill 资产**
- `prompts/s4b_tooling.prompt.md`：S4b LLM 提示词（含 8 条必须遵守 + 5 条禁止反模式）
- `templates/schemas/stage4b.schema.json`：正式 schema（tools minItems≥1，tooling_constraints 可选）

**路由激活**
- `backend/routers/assembly_design.py`：移除 `"4b"` 的 501，新增 `elif stage_key == "4b"` 分支（依赖 stage4a.json 存在，否则 409）

#### Why
S4a 的 `tooling` 字段仅是原始字符串列表，缺少分类和成本信息；S4b 通过 LLM 分类（generic/special）+ 成本层级（低/中/高）使后续采购/设计决策有数据支撑。`_cross_validate()` 确保 `used_in_procedures` 和 `tooling_constraints` 的 id 引用完整性，防止"孤岛工装"写入 Neo4j。

#### How（核心调用链）

```
POST /assembly-design/scheme/{id}/stage/4b
  → router: check stage4a.json exists (→ 409 if missing)
  → assembly_lock.acquire()
  → run_stage4b_tooling(stage4a_payload, skill, llm_client, neo4j_driver=None, ...)
      → query_kg_tools(neo4j_driver, subject_name)   # Tool 节点 + requires 关系
      → _build_prompt(skill, stage4a_payload, kg_tools, user_guidance)
      → _call_llm(llm_client, prompt)
      → _parse_and_validate(raw, schema, stage4a_payload)
          → jsonschema.validate
          → _cross_validate: used_in_procedures ∈ S4a proc_ids
                             constraint.procedure_id ∈ S4a proc_ids
                             constraint.tool_id ∈ tools
      → None → PLACEHOLDER（动态修正 used_in_procedures 为 S4a 第一个 proc id）
      → 强制覆写 stage4a_ref
  → 写 stage4b.json，meta.json stages_done += "4b"
  → assembly_lock.release()
```

#### Where（证据）
- 单元测试：`tests/assembly/test_stage4b_tooling.py`（8 tests）
- 路由测试：`tests/assembly/test_assembly_design_router.py`（含 4b 409 门控 + S1→…→S4b happy path）
- 全套结果：**88 passed**（branch `feat/assembly-scheme-p2-s2-s3`）
```

- [ ] **Step 3: 更新 SESSION_STATE.md**

将 SESSION_STATE.md 中 `## [Plan 3 已完成` 那一节的标题改为：

```markdown
## [Plan 4 已完成（2026-05-14）— 可开新会话推进 Plan 5]

**Plan 4（Assembly Scheme Skill S4b）已完成**，branch `feat/assembly-scheme-p2-s2-s3`，88 tests 全绿。

### 已交付内容
- `backend/pipelines/assembly_scheme/stage4b_tooling.py`：KG 工装查询 + LLM 分类 + `_cross_validate()` 四层保险
- `skills/aero-engine-assembly-scheme/templates/schemas/stage4b.schema.json`：正式 schema
- `skills/aero-engine-assembly-scheme/prompts/s4b_tooling.prompt.md`：S4b LLM 提示词
- `backend/routers/assembly_design.py`：stage/4b 路由激活（依赖 stage4a，否则 409）
- `PROJECT_GUIDE.md §16.P4`：已更新（3W1H 标准）
- 证据：`tests/assembly/`（88 tests）

### 下一步建议（Plan 5 选项）
1. **前端 S1-S4b 展示**：在 React 中接入 assembly-design 端点，展示各阶段产物
2. **S4c 公差分配（可跳过）**：ASME B89.7.5 stack-up，需有完整 GD&T 数据
3. **S5 评审导出**：生成完整工艺方案 PDF/Markdown 报告
```

- [ ] **Step 4: Commit**

```bash
git add PROJECT_GUIDE.md SESSION_STATE.md
git commit -m "docs: PROJECT_GUIDE 16.P4 -- Plan 4 complete (S4b tooling, 88 tests green)"
```
