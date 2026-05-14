# S4b 工装选型设计文档

**日期**：2026-05-14  
**分支**：feat/assembly-scheme-p2-s2-s3  
**前置依赖**：S4a 工序排序（stage4a_process.py）已完成

---

## 1. 背景与目标

S4a 为每条工序标注了 `tooling` 名称列表（如 `["扭矩扳手", "液压套装工具"]`），但仅是原始字符串，缺少：

- 通用 / 专用分类
- 成本层级（决定是否需要采购或设计）
- 工艺性反馈（哪些工序因工装约束需要调序）

S4b 填补这一缺口，输出：
1. 统一编号的工装清单（T01/T02…）
2. 每条工装的分类、成本层级、关联工序
3. 专用工装的设计需求描述
4. 工装约束列表（哪些工序受工装限制，建议调序）
5. DFA 工装效率得分（通用工装占比）

---

## 2. Schema（stage4b.schema.json）

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
          "id": { "type": "string", "pattern": "^T[0-9]{2,}$" },
          "name": { "type": "string", "minLength": 2 },
          "category": { "type": "string", "enum": ["generic", "special"] },
          "cost_tier": { "type": "string", "enum": ["低", "中", "高"] },
          "used_in_procedures": {
            "type": "array",
            "items": { "type": "string" },
            "minItems": 1
          },
          "design_requirements": { "type": "string" },
          "notes": { "type": "string" }
        }
      }
    },
    "tooling_constraints": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["procedure_id", "tool_id", "issue", "suggested_action"],
        "properties": {
          "procedure_id": { "type": "string" },
          "tool_id": { "type": "string" },
          "issue": { "type": "string", "minLength": 5 },
          "suggested_action": { "type": "string", "minLength": 5 }
        }
      }
    },
    "dfa_tooling_score": {
      "type": "number",
      "minimum": 0,
      "maximum": 1
    },
    "uncertainty": {
      "type": "string",
      "enum": ["高", "中", "低"]
    }
  }
}
```

**Pipeline 层完整性校验**（不放入 schema，代码校验）：

- `tools[*].used_in_procedures` 每个 id 必须存在于 S4a `procedures` 中
- `tooling_constraints[*].procedure_id` 必须在 S4a procedures 中
- `tooling_constraints[*].tool_id` 必须在本 `tools` 列表中
- 任一失败 → 返回 PLACEHOLDER

---

## 3. Pipeline 调用链

```
POST /assembly-design/scheme/{id}/stage/4b
  → router: check stage4a.json exists (→ 409 if missing)
  → assembly_lock.acquire()
  → run_stage4b_tooling(stage4a_payload, skill, llm_client, neo4j_driver, user_guidance)
      │
      ├─ 1. 提取去重工装名
      │      {procedure_id: tooling_list} from stage4a["procedures"]
      │
      ├─ 2. query_kg_tools(neo4j_driver, subject_name)
      │      MATCH (t:Tool) WHERE t.kg_name CONTAINS $subj
      │      OPTIONAL MATCH (:Procedure)-[:requires]->(t)
      │      → kg_tools (list[dict])  # None/异常 → []
      │
      ├─ 3. _build_prompt(skill, stage4a_payload, kg_tools, user_guidance)
      │      prompt: s4b_tooling.prompt.md
      │      + methodology: s4_detailed_process.md
      │      + stage4a 工序链（含所有 tooling 名称）
      │      + KG 预填充工装节点
      │
      ├─ 4. _call_llm(llm_client, prompt)  # None → None，异常 → None
      │
      ├─ 5. _parse_and_validate(raw, schema)
      │      → jsonschema.validate(obj, stage4b.schema)
      │      → _cross_validate(obj, stage4a_payload)  # 交叉引用完整性
      │      → 任一失败 → None
      │
      └─ 6. None → PLACEHOLDER_STAGE4B（uncertainty: "高"）
             否则 → 强制覆写 stage4a_ref → 返回
  → 写 stage4b.json，meta.json stages_done += "4b"
  → assembly_lock.release()
```

### 降级策略（四层保险）

1. LLM=None → PLACEHOLDER
2. LLM 返回无效 JSON → PLACEHOLDER
3. JSON 不过 schema → PLACEHOLDER
4. `used_in_procedures` / constraint ids 交叉引用失败 → PLACEHOLDER

---

## 4. Prompt 设计要点（s4b_tooling.prompt.md）

关键规则：
- `tools[*].id` 必须是 T01/T02… 连续编号，由 LLM 自行分配
- `used_in_procedures` 只能引用 S4a 中存在的工序 id
- `category: "special"` 时 `design_requirements` 必须非空
- `dfa_tooling_score` = generic 工装数 / 总工装数（LLM 自行计算）
- **禁止杜撰**具体 CMM 工具号；信息不足时 `notes: "见 CMM"` 或 `"待确认"`
- `uncertainty: "高"` 时 tooling_constraints 可为空列表

---

## 5. 文件清单

| 文件 | 说明 |
|------|------|
| `skills/.../schemas/stage4b.schema.json` | 正式 schema |
| `skills/.../prompts/s4b_tooling.prompt.md` | LLM 提示词 |
| `backend/pipelines/assembly_scheme/stage4b_tooling.py` | `run_stage4b_tooling()` |
| `backend/routers/assembly_design.py` | 激活 stage/4b，stage4a 前置门控 |
| `tests/assembly/test_stage4b_tooling.py` | 8 条单元测试 |
| `tests/assembly/test_assembly_design_router.py` | 补 2 条路由测试 |

---

## 6. 测试矩阵

| 测试用例 | 验证点 |
|---|---|
| `test_run_stage4b_no_llm_returns_placeholder` | LLM=None → placeholder schema 合法 |
| `test_query_kg_tools_no_driver_returns_empty` | neo4j_driver=None → [] |
| `test_query_kg_tools_handles_exception` | driver 抛异常 → [] |
| `test_run_stage4b_with_valid_llm_output` | 正常 LLM 输出 → schema 合法，字段正确 |
| `test_run_stage4b_bad_json_falls_back` | LLM 返回非 JSON → placeholder |
| `test_run_stage4b_dangling_procedure_ref_falls_back` | `used_in_procedures` 引用不存在 P99 → placeholder |
| `test_run_stage4b_dangling_constraint_tool_ref_falls_back` | constraint tool_id 引用不存在 T99 → placeholder |
| `test_placeholder_stage4b_validates` | PLACEHOLDER 常量本身通过 schema |
| `test_stage4b_requires_stage4a_first`（router） | 无 stage4a.json → 409 |
| `test_stage4b_runs_after_full_chain`（router） | S1→S2→S3→S4a→S4b happy path |

预计总测试数：**88 passed**

---

## 7. 成功标准

1. `pytest tests/assembly/ -v` 全绿（≥88 passed）
2. `POST /assembly-design/scheme/{id}/stage/4b`：无 stage4a → 409；有 stage4a → 200，返回 tools + dfa_tooling_score
3. `tools[*].used_in_procedures` 引用完整性 100%（pipeline 层保证）
4. PLACEHOLDER 的 `uncertainty: "高"` 始终触发（LLM=None 时）
