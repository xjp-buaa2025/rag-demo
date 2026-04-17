# Plan E: CAD 实体可读性增强 — 设计规范

**日期**：2026-04-17  
**状态**：已批准  
**目标**：让 CAD 实体名称从纯编号变为有意义的描述，纯编号占比从 100% 降到 < 50%

---

## 背景

当前 `stage3_cad_triples.json` 中，子节点名称形如 `C89119-270`、`C89119-190`，
虽经过父装配名前缀补全，但仍无任何语义信息（不知是叶片、轴承还是轮盘）。
`cad_entities` 的 `description` 字段目前全为空。

---

## 方案选择

采用**方案C（A+B 组合）**：
1. SHAPE_REPRESENTATION 名称回填（改善实体名称）
2. 几何分类结果写入 `entity.description`（补语义）
3. 含关键词名称做中文类型推断写入 `entity.description`

---

## 数据流

```
STEP 文件
    │
    ▼
_build_step_name_chain()           ← 改动①：加 Step4 SHAPE_REPRESENTATION 回填
    │  现有 Step1-3：PRODUCT → FORMATION → PRODUCT_DEFINITION
    │  新增 Step4：对仍是 Part_<ref> 的条目，
    │             查 SHAPE_DEFINITION → SHAPE_DEFINITION_REPRESENTATION
    │             → SHAPE_REPRESENTATION('name') 回填
    ▼
pd_name_map: {pd_ref → str}         ← 接口不变，调用方零改动
    │
    ▼
_parse_step_tree_from_text()        ← 不改，前缀补全逻辑现有已正确
_parse_step_constraints()           ← 不改
    │
    ▼
cad_to_kg_triples()                 ← 改动②：调用 _infer_description 填 description
    │
    ▼
cad_entities: {name → {description, part_type, source}}
```

---

## 改动点详解

### 改动① `_build_step_name_chain` — Step4 SHAPE_REPRESENTATION 回填

在现有三步（PRODUCT → FORMATION → PRODUCT_DEFINITION）之后加 Step4：

```
STEP 引用链：
  PRODUCT_DEFINITION(#pd) → SHAPE_DEFINITION(引用 #pd)
  → SHAPE_DEFINITION_REPRESENTATION(#shape_def, #shape_rep)
  → SHAPE_REPRESENTATION('actual_name', ...)
```

正则模式（新增）：
- `SHAPE_DEFINITION`：`#(\d+)\s*=\s*SHAPE_DEFINITION\s*\(\s*'[^']*'\s*,\s*'[^']*'\s*,\s*#(\d+)`
- `SHAPE_DEFINITION_REPRESENTATION`：`#(\d+)\s*=\s*SHAPE_DEFINITION_REPRESENTATION\s*\(\s*#(\d+)\s*,\s*#(\d+)`
- `SHAPE_REPRESENTATION`：`#(\d+)\s*=\s*(?:ADVANCED_)?SHAPE_REPRESENTATION\s*\(\s*'([^']*)'`

**接口约定**：返回值仍为 `{pd_ref: str}`，调用方不变。Step4 仅在 `Part_<ref>` 条目上静默覆盖。

### 改动② 新增 `_infer_description` + `_KW_MAP`

```python
_KW_MAP = {
    "blade":   "叶片",   "vane":    "导叶",   "disk":    "叶盘",
    "shaft":   "轴",     "nut":     "螺母",   "bolt":    "螺栓",
    "ring":    "篦齿环", "seal":    "封严",   "stator":  "静子",
    "rotor":   "转子",   "case":    "机匣",   "bearing": "轴承",
    "spacer":  "隔圈",   "flange":  "法兰",
}

_GEOM_TYPE_MAP = {
    "Disk/Ring":      "盘/环类零件",
    "Bolt/Shaft":     "轴类/紧固件",
    "Fastener":       "紧固件",
    "Housing/Casing": "机匣/壳体",
}

def _infer_description(name: str, part_type: str = "") -> str:
    name_lower = name.lower()
    for kw, zh in _KW_MAP.items():
        if kw in name_lower:
            return zh
    return _GEOM_TYPE_MAP.get(part_type, "")
```

### 改动③ `cad_to_kg_triples` 填充 `cad_entities`

在现有 `cad_entities` 构建处，对每个实体名称调用 `_infer_description`，
并将 `cad_geometry` 中的 `part_type` 传入：

```python
cad_entities[name] = {
    "name":        name,
    "description": _infer_description(name, part_type),
    "part_type":   part_type,   # 几何分类英文原文
    "source":      "CAD",
}
```

---

## 文件改动范围

| 文件 | 改动内容 |
|------|---------|
| `backend/pipelines/nodes_cad.py` | `_build_step_name_chain` 加 Step4；新增 `_KW_MAP`、`_GEOM_TYPE_MAP`、`_infer_description`；`cad_to_kg_triples` 填充 `description` 字段 |
| `tests/kg/test_cad_readability.py`（新建） | 单元测试（见下节） |

---

## 测试规范

新建 `tests/kg/test_cad_readability.py`，覆盖以下用例：

| 测试 ID | 描述 | 通过条件 |
|---------|------|---------|
| `test_infer_description_blade` | 名称含 "blade" | 返回 "叶片" |
| `test_infer_description_disk` | 名称含 "disk" | 返回 "叶盘" |
| `test_infer_description_geom_fallback` | 无关键词，part_type="Disk/Ring" | 返回 "盘/环类零件" |
| `test_infer_description_empty` | 无关键词，无 part_type | 返回 "" |
| `test_name_chain_shape_rep_fallback` | mock STEP 内容含 SHAPE_REPRESENTATION，PRODUCT desc 为空 | pd_name_map 不含 `Part_` 前缀 |
| `test_numeric_name_ratio` | 对 stage3_cad_triples.json 中实体名称统计 | 纯 `Part_<ref>` 占比 < 50% |

---

## 验收标准

| 指标 | 目标 |
|------|------|
| `cad_entities[*].description` 非空比例（有几何数据时） | ≥ 50% |
| 实体名称中 `Part_<ref>` 格式占比 | < 50% |
| 所有现有 CAD 相关测试通过 | 必须 |
| 无新增第三方依赖 | 必须 |

---

## 不在范围内

- 不修改 `_parse_step_adjacency`（邻接检测与命名无关）
- 不修改 `_classify_part_by_geometry`（几何分类逻辑已足够）
- 不引入 LLM 调用
- 不修改 Neo4j 写入 schema（`description` 字段已在现有 Cypher 中支持 `ON CREATE SET`）
