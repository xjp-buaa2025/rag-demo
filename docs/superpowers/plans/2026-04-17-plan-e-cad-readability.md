# Plan E: CAD 实体可读性增强 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 让 CAD 实体名称从纯编号变为有意义的描述，`cad_entities.description` 非空率 ≥ 50%，`Part_<ref>` 格式占比 < 50%。

**Architecture:** 三层改动：① `_build_step_name_chain` 加 Step4 从 SHAPE_REPRESENTATION 回填无意义名称；② 新增模块级 `_KW_MAP`/`_GEOM_TYPE_MAP`/`_infer_description`，根据名称关键词和几何分类推断中文描述；③ `cad_to_kg_triples` 在构建 `cad_entities` 时调用 `_infer_description` 填充 `description` 字段。接口不变，调用方零改动。

**Tech Stack:** Python 3.10, pytest, re（标准库），无新增依赖

---

## 文件改动范围

| 文件 | 操作 | 职责 |
|------|------|------|
| `backend/pipelines/nodes_cad.py` | Modify | 加 Step4、新增辅助函数、填 description |
| `tests/kg/test_cad_readability.py` | Create | 单元测试：关键词推断、SHAPE_REP 回填、name ratio |

---

## Task 1: 为 `_infer_description` 写失败测试

**Files:**
- Create: `tests/kg/test_cad_readability.py`

- [ ] **Step 1: 新建测试文件，写4个关于 `_infer_description` 的失败测试**

```python
# tests/kg/test_cad_readability.py
"""
Plan E — CAD 实体可读性增强 单元测试。
覆盖：_infer_description 关键词推断、几何分类 fallback、SHAPE_REP 名称回填。
"""
import os, sys, tempfile, pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from backend.pipelines.nodes_cad import _infer_description


def test_infer_description_blade():
    """名称含 'blade' 应返回 '叶片'"""
    assert _infer_description("C52696C-180-blade") == "叶片"


def test_infer_description_disk():
    """名称含 'disk' 应返回 '叶盘'"""
    assert _infer_description("Rotor-disk-01") == "叶盘"


def test_infer_description_geom_fallback():
    """无关键词，part_type='Disk/Ring' 应返回 '盘/环类零件'"""
    assert _infer_description("C89119-270", "Disk/Ring") == "盘/环类零件"


def test_infer_description_empty():
    """无关键词，无 part_type 应返回空字符串"""
    assert _infer_description("C89119-270") == ""
```

- [ ] **Step 2: 运行确认失败（函数不存在）**

```bash
cd "c:/xjp/代码/rag-demo"
"C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" -m pytest tests/kg/test_cad_readability.py -v
```

期望：`ImportError` 或 `AttributeError: module ... has no attribute '_infer_description'`

---

## Task 2: 实现 `_KW_MAP` / `_GEOM_TYPE_MAP` / `_infer_description`

**Files:**
- Modify: `backend/pipelines/nodes_cad.py:19-23`（模块级常量区）

- [ ] **Step 1: 在 `_NUMERIC_NAME_RE` 定义之后插入常量和函数**

在 [backend/pipelines/nodes_cad.py:23](backend/pipelines/nodes_cad.py#L23) 的 `_NUMERIC_NAME_RE = ...` 行**之后**，插入以下代码（紧接着空行）：

```python
# 关键词 → 中文描述（用于 _infer_description）
_KW_MAP: dict[str, str] = {
    "blade":   "叶片",   "vane":    "导叶",   "disk":    "叶盘",
    "shaft":   "轴",     "nut":     "螺母",   "bolt":    "螺栓",
    "ring":    "篦齿环", "seal":    "封严",   "stator":  "静子",
    "rotor":   "转子",   "case":    "机匣",   "bearing": "轴承",
    "spacer":  "隔圈",   "flange":  "法兰",
}

# 几何分类英文 → 中文描述 fallback
_GEOM_TYPE_MAP: dict[str, str] = {
    "Disk/Ring":      "盘/环类零件",
    "Bolt/Shaft":     "轴类/紧固件",
    "Fastener":       "紧固件",
    "Housing/Casing": "机匣/壳体",
}


def _infer_description(name: str, part_type: str = "") -> str:
    """
    从实体名称关键词或几何分类推断中文描述。
    优先关键词匹配，fallback 到几何分类映射，均无则返回空字符串。
    """
    name_lower = name.lower()
    for kw, zh in _KW_MAP.items():
        if kw in name_lower:
            return zh
    return _GEOM_TYPE_MAP.get(part_type, "")
```

- [ ] **Step 2: 运行 Task 1 的4个测试，确认全部通过**

```bash
cd "c:/xjp/代码/rag-demo"
"C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" -m pytest tests/kg/test_cad_readability.py::test_infer_description_blade tests/kg/test_cad_readability.py::test_infer_description_disk tests/kg/test_cad_readability.py::test_infer_description_geom_fallback tests/kg/test_cad_readability.py::test_infer_description_empty -v
```

期望：4 passed

- [ ] **Step 3: 提交**

```bash
cd "c:/xjp/代码/rag-demo"
git add backend/pipelines/nodes_cad.py tests/kg/test_cad_readability.py
git commit -m "feat: add _infer_description with _KW_MAP and _GEOM_TYPE_MAP"
```

---

## Task 3: 为 SHAPE_REPRESENTATION 回填写失败测试

**Files:**
- Modify: `tests/kg/test_cad_readability.py`（追加）

- [ ] **Step 1: 追加 `test_name_chain_shape_rep_fallback` 测试**

在 `tests/kg/test_cad_readability.py` **末尾**追加：

```python
from backend.pipelines.nodes_cad import _build_step_name_chain


# STEP 内容：PRODUCT description 为空，但有 SHAPE_REPRESENTATION 名称
_STEP_WITH_SHAPE_REP = """
ISO-10303-21;
HEADER; ENDSEC;
DATA;
#1  = PRODUCT ( 'P001', '', '', ( #99 ) ) ;
#10 = PRODUCT_DEFINITION_FORMATION ( ' ', ' ', #1 ) ;
#20 = PRODUCT_DEFINITION ( 'design', ' ', #10 ) ;
#30 = SHAPE_DEFINITION ( 'sd', ' ', #20 ) ;
#40 = SHAPE_REPRESENTATION ( 'CompressorBlade', ( ), #50 ) ;
#41 = SHAPE_DEFINITION_REPRESENTATION ( #30, #40 ) ;
ENDSEC;
END-ISO-10303-21;
"""


def test_name_chain_shape_rep_fallback():
    """
    PRODUCT description 为空时，应从 SHAPE_REPRESENTATION 回填名称，
    pd_name_map 中不应出现 'Part_20' 格式。
    """
    result = _build_step_name_chain(_STEP_WITH_SHAPE_REP)
    # pd_ref=20 对应的名称应为 'CompressorBlade'，而非 'Part_20'
    assert result.get("20") == "CompressorBlade", (
        f"期望 'CompressorBlade'，实际={result.get('20')!r}，full={result}"
    )
```

- [ ] **Step 2: 运行确认失败**

```bash
cd "c:/xjp/代码/rag-demo"
"C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" -m pytest tests/kg/test_cad_readability.py::test_name_chain_shape_rep_fallback -v
```

期望：FAILED — `assert result.get("20") == "CompressorBlade"` （实际返回 `'P001'` 或 `'Part_20'`）

---

## Task 4: 实现 `_build_step_name_chain` Step4（SHAPE_REPRESENTATION 回填）

**Files:**
- Modify: `backend/pipelines/nodes_cad.py:218-265`（`_build_step_name_chain` 函数）

- [ ] **Step 1: 在函数末尾（`return pd_name_map` 之前）插入 Step4**

找到 [backend/pipelines/nodes_cad.py:261](backend/pipelines/nodes_cad.py#L261)，当前末尾：

```python
        else:
            pd_name_map[pd_ref] = f"Part_{pd_ref}"

    return pd_name_map
```

替换为：

```python
        else:
            pd_name_map[pd_ref] = f"Part_{pd_ref}"

    # Step4: 对仍是 Part_<ref> 的条目，尝试从 SHAPE_REPRESENTATION 回填
    # 引用链：PRODUCT_DEFINITION(#pd) → SHAPE_DEFINITION → SHAPE_DEFINITION_REPRESENTATION → SHAPE_REPRESENTATION('name')
    _shape_def_re = re.compile(
        r"#(\d+)\s*=\s*SHAPE_DEFINITION\s*\(\s*'[^']*'\s*,\s*'[^']*'\s*,\s*#(\d+)",
        re.IGNORECASE,
    )
    _shape_def_rep_re = re.compile(
        r"#(\d+)\s*=\s*SHAPE_DEFINITION_REPRESENTATION\s*\(\s*#(\d+)\s*,\s*#(\d+)",
        re.IGNORECASE,
    )
    _shape_rep_re = re.compile(
        r"#(\d+)\s*=\s*(?:ADVANCED_)?SHAPE_REPRESENTATION\s*\(\s*'([^']*)'",
        re.IGNORECASE,
    )

    # 构建辅助映射
    # pd_ref → shape_def_ref
    _pd_to_shapedef: dict[str, str] = {}
    for _m in _shape_def_re.finditer(content):
        _pd_to_shapedef[_m.group(2)] = _m.group(1)   # SHAPE_DEFINITION(#sd) 引用 PRODUCT_DEFINITION(#pd)

    # shape_def_ref → shape_rep_ref
    _shapedef_to_shaperep: dict[str, str] = {}
    for _m in _shape_def_rep_re.finditer(content):
        _shapedef_to_shaperep[_m.group(2)] = _m.group(3)

    # shape_rep_ref → name
    _shaperep_names: dict[str, str] = {}
    for _m in _shape_rep_re.finditer(content):
        if _m.group(2).strip():
            _shaperep_names[_m.group(1)] = _m.group(2).strip()

    for pd_ref, name in list(pd_name_map.items()):
        if name.startswith("Part_"):
            sd_ref = _pd_to_shapedef.get(pd_ref)
            if sd_ref:
                sr_ref = _shapedef_to_shaperep.get(sd_ref)
                if sr_ref and sr_ref in _shaperep_names:
                    pd_name_map[pd_ref] = _shaperep_names[sr_ref]

    return pd_name_map
```

- [ ] **Step 2: 运行 Task 3 的测试，确认通过**

```bash
cd "c:/xjp/代码/rag-demo"
"C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" -m pytest tests/kg/test_cad_readability.py::test_name_chain_shape_rep_fallback -v
```

期望：PASSED

- [ ] **Step 3: 运行全部已有 CAD 命名测试，确认无回归**

```bash
cd "c:/xjp/代码/rag-demo"
"C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" -m pytest tests/kg/test_stage3_naming.py tests/kg/test_cad_readability.py -v
```

期望：全部 PASSED

- [ ] **Step 4: 提交**

```bash
cd "c:/xjp/代码/rag-demo"
git add backend/pipelines/nodes_cad.py tests/kg/test_cad_readability.py
git commit -m "feat: add Step4 SHAPE_REPRESENTATION fallback to _build_step_name_chain"
```

---

## Task 5: `cad_to_kg_triples` 填充 `cad_entities.description`

**Files:**
- Modify: `backend/pipelines/nodes_cad.py:140-208`（`cad_to_kg_triples` 闭包）

当前 `cad_to_kg_triples` 中 `cad_entities` 由 `nodes_kg_unified` 返回，微臣需确认其结构后补充 `description`。

- [ ] **Step 1: 查看 nodes_kg_unified 中 cad_entities 的填充位置**

```bash
cd "c:/xjp/代码/rag-demo"
grep -n "cad_entities" backend/pipelines/nodes_kg_unified.py | head -30
```

- [ ] **Step 2: 在 `cad_to_kg_triples` 返回前，对 `cad_entities` 中每个实体补充 `description`**

找到 [backend/pipelines/nodes_cad.py](backend/pipelines/nodes_cad.py) 中 `cad_to_kg_triples` 函数的返回语句（约 L203-L208）：

```python
        return {
            "cad_kg_triples": cad_kg_triples,
            "cad_entities":   cad_entities,
            "log_messages":   [log_msg],
            "current_node":   "cad_to_kg_triples",
        }
```

**在此返回语句之前**插入：

```python
        # Plan E: 为每个实体补充 description（关键词推断 + 几何分类 fallback）
        cad_geometry = state.get("cad_geometry") or {}
        for ent_name, ent_data in cad_entities.items():
            if not ent_data.get("description"):
                part_type = ""
                if ent_name in cad_geometry:
                    part_type = cad_geometry[ent_name].get("part_type", "")
                ent_data["description"] = _infer_description(ent_name, part_type)
```

- [ ] **Step 3: 运行全量 CAD + 可读性测试**

```bash
cd "c:/xjp/代码/rag-demo"
"C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" -m pytest tests/kg/test_stage3_naming.py tests/kg/test_cad_readability.py -v
```

期望：全部 PASSED

- [ ] **Step 4: 提交**

```bash
cd "c:/xjp/代码/rag-demo"
git add backend/pipelines/nodes_cad.py
git commit -m "feat: populate cad_entities.description via _infer_description in cad_to_kg_triples"
```

---

## Task 6: 验收测试 — `Part_<ref>` 占比 < 50%

**Files:**
- Modify: `tests/kg/test_cad_readability.py`（追加）

- [ ] **Step 1: 追加 `test_numeric_name_ratio` 测试**

在 `tests/kg/test_cad_readability.py` **末尾**追加：

```python
import json, re as _re

_PART_REF_RE = _re.compile(r'^Part_\d+$')


def test_numeric_name_ratio():
    """
    stage3_cad_triples.json 中，实体名称含 'Part_<数字>' 格式的占比须 < 50%。
    若文件不存在则跳过（CI 环境无真实 STEP 文件时不强制）。
    """
    fixture = os.path.join(
        os.path.dirname(__file__), "..", "..", "storage", "kg_stages", "stage3_cad_triples.json"
    )
    if not os.path.exists(fixture):
        pytest.skip("stage3_cad_triples.json 不存在，跳过")

    with open(fixture, encoding="utf-8") as f:
        data = json.load(f)

    triples = data.get("triples", [])
    all_names = set(t["head"] for t in triples) | set(t["tail"] for t in triples)
    if not all_names:
        pytest.skip("triples 为空，跳过")

    part_ref_count = sum(1 for n in all_names if _PART_REF_RE.match(n))
    ratio = part_ref_count / len(all_names)
    assert ratio < 0.5, (
        f"Part_<ref> 占比 {ratio:.1%}（{part_ref_count}/{len(all_names)}）>= 50%，未达标"
    )
```

- [ ] **Step 2: 运行验收测试**

```bash
cd "c:/xjp/代码/rag-demo"
"C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" -m pytest tests/kg/test_cad_readability.py::test_numeric_name_ratio -v
```

期望：PASSED（stage3_cad_triples.json 中实体名均为 `C89119-xxx` 格式，无 `Part_<ref>`，占比 0%）

- [ ] **Step 3: 运行全量测试套件**

```bash
cd "c:/xjp/代码/rag-demo"
"C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" -m pytest tests/kg/test_stage3_naming.py tests/kg/test_cad_readability.py -v
```

期望：全部 PASSED

- [ ] **Step 4: 提交**

```bash
cd "c:/xjp/代码/rag-demo"
git add tests/kg/test_cad_readability.py
git commit -m "test: add acceptance test for Part_<ref> name ratio < 50%"
```

---

## 自检清单（已通过）

| 检查项 | 结论 |
|--------|------|
| Spec 所有要求有对应 Task | ✓ Step4 回填→Task4；关键词推断→Task2；description 填充→Task5；验收→Task6 |
| 无 TBD / TODO / 相似于 TaskN | ✓ |
| 函数签名一致 | ✓ `_infer_description(name, part_type="")` 在 Task2 定义，Task5 调用签名一致 |
| 测试先于实现（TDD） | ✓ Task1→Task2；Task3→Task4；Task6 在 Task5 后验收 |
| 无新增第三方依赖 | ✓ 仅用 `re`（已导入） |
