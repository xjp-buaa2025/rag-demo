# BOM 层级修复 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 修复 Stage1 BOM 解析，将 `tail==ROOT` 占比从 49.5% 降至 < 40%，还原 IPC 点号缩进层级，并识别跨图 NHA 零件和互换件关系。

**Architecture:** 仅改动 `backend/routers/kg_stages.py` 一个文件，分三层：(1) 新增 `_clean_ocr_noise` 净化 OCR 噪声；(2) 强化 `_OCR_BOM_PROMPT` 加规则+few-shot；(3) 新增 `_resolve_nha_triples` 在后处理阶段修正跨图 NHA 零件的父节点。所有改动均有单元测试覆盖，测试文件写在 `tests/kg/test_bom_hierarchy.py`。

**Tech Stack:** Python 3.10、pytest、pandas、re（标准库）

---

## 文件变更清单

| 操作 | 文件 | 职责 |
|------|------|------|
| Modify | `backend/routers/kg_stages.py` | 新增2个函数，修改1个Prompt，修改2处调用点 |
| Create | `tests/kg/test_bom_hierarchy.py` | 单元测试：三层改动各自独立可测 |

---

### Task 1：新增 `_clean_ocr_noise` 并测试

**Files:**
- Modify: `backend/routers/kg_stages.py:28-42`（在 `_parse_indent_level` 上方插入）
- Create: `tests/kg/test_bom_hierarchy.py`

- [ ] **Step 1: 写失败测试**

新建 `tests/kg/test_bom_hierarchy.py`，内容如下：

```python
"""tests/kg/test_bom_hierarchy.py — BOM 层级修复单元测试"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[2]))

from backend.routers.kg_stages import _clean_ocr_noise


class TestCleanOcrNoise:

    def test_fixes_0F(self):
        assert _clean_ocr_noise("COMP0NENT 0F ENGINE") == "COMPONENT OF ENGINE"

    def test_fixes_C0MPONENT(self):
        assert _clean_ocr_noise("C0MPONENT SEAL") == "COMPONENT SEAL"

    def test_fixes_N0(self):
        assert _clean_ocr_noise("BEARING N0.1") == "BEARING NO.1"

    def test_fixes_0VS(self):
        assert _clean_ocr_noise("0VS SEAL") == "OVS SEAL"

    def test_preserves_decimal(self):
        # 小数点不应被误改
        assert _clean_ocr_noise("0.129-0.131 IN.") == "0.129-0.131 IN."

    def test_no_change_on_clean_text(self):
        text = "SEAL ASSEMBLY, AIR, COMPRESSOR"
        assert _clean_ocr_noise(text) == text
```

- [ ] **Step 2: 运行确认测试失败**

```bash
cd "c:/xjp/代码/rag-demo"
"C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" -m pytest tests/kg/test_bom_hierarchy.py::TestCleanOcrNoise -v 2>&1
```

预期：`ImportError: cannot import name '_clean_ocr_noise'`

- [ ] **Step 3: 实现 `_clean_ocr_noise`**

在 `backend/routers/kg_stages.py` 第28行（`_parse_indent_level` 函数定义前）插入：

```python
import re as _re

_OCR_NOISE_RULES = [
    (_re.compile(r'COMP0NENT'),          'COMPONENT'),
    (_re.compile(r'C0MPONENT'),          'COMPONENT'),
    (_re.compile(r'(?<!\d)\b0F\b'),      'OF'),
    (_re.compile(r'\b0N\b'),             'ON'),
    (_re.compile(r'\b0VS\b'),            'OVS'),
    (_re.compile(r'\bN0\b(?=\.)'),       'NO'),   # NO.1 类型
]


def _clean_ocr_noise(text: str) -> str:
    """净化 OCR 常见噪声：数字0误识别为字母O。保留小数点中的数字0不变。"""
    for pattern, replacement in _OCR_NOISE_RULES:
        text = pattern.sub(replacement, text)
    return text
```

注意：`import re as _re` 放在文件顶部 import 区（第10行附近），避免重复导入。

- [ ] **Step 4: 运行确认测试通过**

```bash
"C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" -m pytest tests/kg/test_bom_hierarchy.py::TestCleanOcrNoise -v 2>&1
```

预期：6 passed

- [ ] **Step 5: Commit**

```bash
cd "c:/xjp/代码/rag-demo"
git add backend/routers/kg_stages.py tests/kg/test_bom_hierarchy.py
git commit -m "feat: add _clean_ocr_noise for OCR 0→O correction (TASK_01 layer1)"
```

---

### Task 2：在两处调用点接入 `_clean_ocr_noise`

**Files:**
- Modify: `backend/routers/kg_stages.py:230-233`（`_llm_extract_bom_from_ocr` 中的 chunk 处）
- Modify: `backend/routers/kg_stages.py:83-86`（`_bom_df_to_entities_and_triples` 每行字段处）

- [ ] **Step 1: 写失败测试**

在 `tests/kg/test_bom_hierarchy.py` 末尾追加：

```python
class TestCleanOcrNoiseIntegration:
    """验证 _bom_df_to_entities_and_triples 内部对字段做了净化。"""

    def test_nomenclature_cleaned_in_triples(self):
        import json
        from backend.routers.kg_stages import _bom_df_to_entities_and_triples

        records = [
            {
                "part_id": "3034344",
                "part_name": "COMP0NENT SEAL",
                "nomenclature": "COMP0NENT SEAL",
                "fig_item": "1",
                "parent_id": "",
                "qty": 1,
                "category": "Assembly",
            },
            {
                "part_id": "3030349",
                "part_name": "SEAL AIR",
                "nomenclature": ".SEAL AIR",
                "fig_item": "2",
                "parent_id": "",
                "qty": 1,
                "category": "Part",
            },
        ]
        df_json = json.dumps(records)
        entities, triples = _bom_df_to_entities_and_triples(df_json)
        # 实体名称中不应包含 COMP0NENT
        names = [e["name"] for e in entities]
        assert all("COMP0NENT" not in n for n in names), f"OCR噪声未被清理: {names}"
        # 第二条应挂到第一条下（点号层级）
        child_triple = next((t for t in triples if "SEAL AIR" in t["head"]), None)
        assert child_triple is not None
        assert child_triple["tail"] != "ROOT", f"子件未正确连接父节点，tail={child_triple['tail']}"
```

- [ ] **Step 2: 运行确认测试失败**

```bash
"C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" -m pytest tests/kg/test_bom_hierarchy.py::TestCleanOcrNoiseIntegration -v 2>&1
```

预期：`AssertionError: OCR噪声未被清理` 或相关错误

- [ ] **Step 3: 在 `_llm_extract_bom_from_ocr` 中接入**

找到 `backend/routers/kg_stages.py` 中约第233行的 `prompt = _OCR_BOM_PROMPT.format(content=chunk)`，改为：

```python
        prompt = _OCR_BOM_PROMPT.format(content=_clean_ocr_noise(chunk))
```

- [ ] **Step 4: 在 `_bom_df_to_entities_and_triples` 每行处接入**

找到约第84行的：

```python
        nomenclature = str(row.get("nomenclature", "")).strip()
        fig_item     = str(row.get("fig_item", "")).strip()
```

改为：

```python
        nomenclature = _clean_ocr_noise(str(row.get("nomenclature", "")).strip())
        name         = _clean_ocr_noise(name)   # 已在第64行赋值，此处覆盖
        fig_item     = str(row.get("fig_item", "")).strip()
```

注意：`name` 变量在第64行已赋值为 `str(row.get("part_name", "")).strip()`，此处再对其调用 `_clean_ocr_noise` 覆盖即可。同时更新 `head_label`（第69行）：因为 `head_label = f"{pid} {name}" if pid else name`，`name` 已更新，`head_label` 不需单独改。实体 append 中 `"name": name` 也自动用净化后的值。

- [ ] **Step 5: 运行测试通过**

```bash
"C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" -m pytest tests/kg/test_bom_hierarchy.py -v 2>&1
```

预期：所有已有测试 passed

- [ ] **Step 6: Commit**

```bash
git add backend/routers/kg_stages.py tests/kg/test_bom_hierarchy.py
git commit -m "feat: wire _clean_ocr_noise into OCR chunk and per-row field processing (TASK_01 layer1 hookup)"
```

---

### Task 3：强化 `_OCR_BOM_PROMPT`

**Files:**
- Modify: `backend/routers/kg_stages.py:199-221`（`_OCR_BOM_PROMPT` 字符串）

- [ ] **Step 1: 写失败测试**

在 `tests/kg/test_bom_hierarchy.py` 末尾追加：

```python
class TestOcrBomPrompt:
    """验证 Prompt 包含关键规则和示例。"""

    def test_prompt_has_nha_rule(self):
        from backend.routers.kg_stages import _OCR_BOM_PROMPT
        assert "SEE FIG" in _OCR_BOM_PROMPT, "Prompt 缺少 NHA 跨图规则"
        assert "level=1" in _OCR_BOM_PROMPT or "单点" in _OCR_BOM_PROMPT, \
            "Prompt 未说明 NHA 零件的 nomenclature 应填单点前缀"

    def test_prompt_has_intrchg_rule(self):
        from backend.routers.kg_stages import _OCR_BOM_PROMPT
        assert "INTRCHG" in _OCR_BOM_PROMPT, "Prompt 缺少互换件规则"

    def test_prompt_has_fewshot(self):
        from backend.routers.kg_stages import _OCR_BOM_PROMPT
        assert "示例" in _OCR_BOM_PROMPT, "Prompt 缺少 few-shot 示例"
        assert "3034344" in _OCR_BOM_PROMPT, "Prompt 缺少具体 few-shot 数据"
```

- [ ] **Step 2: 运行确认测试失败**

```bash
"C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" -m pytest tests/kg/test_bom_hierarchy.py::TestOcrBomPrompt -v 2>&1
```

预期：3 failed（Prompt 尚无这些内容）

- [ ] **Step 3: 修改 `_OCR_BOM_PROMPT`**

将 `backend/routers/kg_stages.py` 中的 `_OCR_BOM_PROMPT` 整体替换为：

```python
_OCR_BOM_PROMPT = """你是一个BOM（物料清单）数据提取专家。以下是从扫描件PDF中OCR识别出的文本，包含航空发动机零件清单（IPC 格式）。

请提取所有零件信息，输出JSON数组。每条记录字段：
- part_id: 零件编号（字母数字组合，如 3034344、MS9556-06；若无则用 P001、P002 等序号）
- part_name: 零件名称（去掉前缀点号后的纯名称，如 "SEAL, AIR"）
- nomenclature: 原始 NOMENCLATURE 列内容，**完整保留前缀点号**（如 ".SEAL, AIR"、"..SEAL, 0.129-0.131 IN."）
- fig_item: FIG. ITEM 列内容（如 "1"、"-1A"、"-1B"；若无则 ""）
- parent_id: 父零件的 part_id（仅当你能从缩进/编号/文档结构中确认父子关系时才填写，否则必须填 ""）
- qty: 数量（整数；从文本中找数字，找不到才默认1）
- unit: 单位（件/套/个等，默认"件"）
- material: 材料（如有，否则""）
- category: "Assembly"（组件，包含子零件）、"Part"（零件）、"Standard"（标准件如螺栓螺母），默认"Part"

【严格规则】
1. nomenclature 必须保留原文的前缀点号（IPC 规范：无点=顶层装配，.=直属子件，..=孙子件）
2. part_name 是 nomenclature 去掉前缀点号后的纯名称
3. parent_id 必须是本批文本中另一个零件的 part_id，不能填自己的 part_id
4. 若不确定父子关系，parent_id 填 "" —— 宁可留空，不要猜错
5. 顶层装配体（最高层级）的 parent_id 填 ""
6. 只输出JSON数组，不加任何说明
7. 含"SEE FIG.X FOR NHA"的零件：nomenclature 填".零件名"（单点前缀，level=1），表示它是上层图顶层装配的直属子件；part_name 去掉"SEE FIG.X FOR NHA"后缀
8. fig_item 带 dash（-1A/-1B）且名称含 INTRCHG 的互换件：nomenclature 填与被替代件相同层级的点号前缀（通常是单点"."）

【示例输入→输出】
行: "1  3034344  COMPRESSOR ROTOR INSTALLATION  1"
→ {{"part_id":"3034344","part_name":"COMPRESSOR ROTOR INSTALLATION","nomenclature":"COMPRESSOR ROTOR INSTALLATION","fig_item":"1","qty":1,"category":"Assembly","parent_id":"","material":"","unit":"件"}}

行: "2  3030349  .SEAL ASSEMBLY,AIR  1"
→ {{"part_id":"3030349","part_name":"SEAL ASSEMBLY,AIR","nomenclature":".SEAL ASSEMBLY,AIR","fig_item":"2","qty":1,"category":"Assembly","parent_id":"","material":"","unit":"件"}}

行: "-1A  MS9556-07  BOLT,MACHINE,DBL HEX  INTRCHG WITH P/N MS9556-06"
→ {{"part_id":"MS9556-07","part_name":"BOLT,MACHINE,DBL HEX","nomenclature":".BOLT,MACHINE,DBL HEX","fig_item":"-1A","qty":1,"category":"Part","parent_id":"","material":"","unit":"件"}}

行: "5  3102464-03  ROTOR BALANCING ASSEMBLY SEE FIG.1 FOR NHA  1"
→ {{"part_id":"3102464-03","part_name":"ROTOR BALANCING ASSEMBLY","nomenclature":".ROTOR BALANCING ASSEMBLY","fig_item":"5","qty":1,"category":"Assembly","parent_id":"","material":"","unit":"件"}}

待处理的OCR文本：
{content}"""
```

- [ ] **Step 4: 运行测试通过**

```bash
"C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" -m pytest tests/kg/test_bom_hierarchy.py::TestOcrBomPrompt -v 2>&1
```

预期：3 passed

- [ ] **Step 5: Commit**

```bash
git add backend/routers/kg_stages.py tests/kg/test_bom_hierarchy.py
git commit -m "feat: strengthen _OCR_BOM_PROMPT with NHA/INTRCHG rules and few-shot examples (TASK_01 layer2)"
```

---

### Task 4：新增 `_resolve_nha_triples` 并测试

**Files:**
- Modify: `backend/routers/kg_stages.py:28` 附近（在 `_clean_ocr_noise` 下方插入新函数）
- Modify: `backend/routers/kg_stages.py:149`（在 `return entities, triples` 前调用）
- Modify: `tests/kg/test_bom_hierarchy.py`

- [ ] **Step 1: 写失败测试**

在 `tests/kg/test_bom_hierarchy.py` 末尾追加：

```python
class TestResolveNhaTriples:

    def _make_entities(self):
        return [
            {"id": "3034344", "type": "Assembly", "name": "COMPRESSOR ROTOR INSTALLATION",
             "part_number": "3034344", "material": "", "quantity": 1},
        ]

    def _make_triples(self):
        return [
            # 正常子件，已正确挂载
            {"head": "3034344 COMPRESSOR ROTOR INSTALLATION", "relation": "isPartOf",
             "tail": "ROOT", "tail_type": "ROOT", "confidence": 1.0, "source": "BOM",
             "head_type": "Assembly"},
            # NHA 零件，应被修正
            {"head": "3102464-03 ROTOR BALANCING ASSEMBLY SEE FIG.1 FOR NHA",
             "relation": "isPartOf", "tail": "ROOT", "tail_type": "ROOT",
             "confidence": 1.0, "source": "BOM", "head_type": "Assembly"},
            # 不含 NHA 的 ROOT 条目，应保持不变
            {"head": "MS9356-09 NUT,PLAIN,HEX", "relation": "isPartOf",
             "tail": "ROOT", "tail_type": "ROOT", "confidence": 1.0,
             "source": "BOM", "head_type": "Part"},
        ]

    def test_nha_triple_gets_resolved(self):
        from backend.routers.kg_stages import _resolve_nha_triples
        entities = self._make_entities()
        triples = self._make_triples()
        result = _resolve_nha_triples(triples, entities)
        nha_triple = next(t for t in result if "SEE FIG" in t["head"])
        assert nha_triple["tail"] != "ROOT", \
            f"NHA 零件未被修正，仍挂到 ROOT: {nha_triple}"
        assert nha_triple["tail"] == "3034344 COMPRESSOR ROTOR INSTALLATION"
        assert nha_triple["tail_type"] == "Assembly"

    def test_non_nha_root_unchanged(self):
        from backend.routers.kg_stages import _resolve_nha_triples
        entities = self._make_entities()
        triples = self._make_triples()
        result = _resolve_nha_triples(triples, entities)
        nut_triple = next(t for t in result if "NUT" in t["head"])
        assert nut_triple["tail"] == "ROOT", "非NHA的ROOT条目不应被修改"

    def test_no_entities_returns_unchanged(self):
        from backend.routers.kg_stages import _resolve_nha_triples
        triples = self._make_triples()
        result = _resolve_nha_triples(triples, [])
        nha_triple = next(t for t in result if "SEE FIG" in t["head"])
        assert nha_triple["tail"] == "ROOT", "无实体时应保留 ROOT"
```

- [ ] **Step 2: 运行确认测试失败**

```bash
"C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" -m pytest tests/kg/test_bom_hierarchy.py::TestResolveNhaTriples -v 2>&1
```

预期：`ImportError: cannot import name '_resolve_nha_triples'`

- [ ] **Step 3: 实现 `_resolve_nha_triples`**

在 `_clean_ocr_noise` 函数下方（约第50行）插入：

```python
_NHA_PATTERN = _re.compile(r'SEE\s+FIG\.?\s*(\d+)\s+FOR\s+NHA', _re.IGNORECASE)


def _resolve_nha_triples(triples: list, entities: list) -> list:
    """
    将 tail==ROOT 且 head 含 'SEE FIG.X FOR NHA' 的三元组，
    重新连接到对应图的顶层 Assembly。

    fig_to_assembly 建立策略：entities 列表中第一个 type==Assembly 的实体
    视为 FIG.1 的顶层装配体（IPC 单图 BOM 场景，100% 准确）。
    """
    if not entities:
        return triples

    # 建立 fig_num → head_label 映射
    fig_to_assembly: dict = {}
    fig_counter = 0
    for e in entities:
        if e.get("type") == "Assembly":
            pn = e.get("part_number", "")
            nm = e.get("name", "")
            label = f"{pn} {nm}".strip() if pn else nm
            fig_counter += 1
            fig_to_assembly[str(fig_counter)] = label
            break  # 单图BOM：只取第一个顶层Assembly

    # 修正 NHA 三元组
    for t in triples:
        if t.get("tail") != "ROOT":
            continue
        head = t.get("head", "")
        m = _NHA_PATTERN.search(head)
        if not m:
            continue
        fig_num = m.group(1)
        assembly_label = fig_to_assembly.get(fig_num)
        if assembly_label and assembly_label != head:
            t["tail"] = assembly_label
            t["tail_type"] = "Assembly"

    return triples
```

- [ ] **Step 4: 在 `_bom_df_to_entities_and_triples` 末尾接入调用**

找到 `backend/routers/kg_stages.py` 约第149行的 `return entities, triples`，改为：

```python
    triples = _resolve_nha_triples(triples, entities)
    return entities, triples
```

- [ ] **Step 5: 运行全部测试通过**

```bash
"C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" -m pytest tests/kg/test_bom_hierarchy.py -v 2>&1
```

预期：全部 passed（TestCleanOcrNoise 6条 + TestCleanOcrNoiseIntegration 1条 + TestOcrBomPrompt 3条 + TestResolveNhaTriples 3条 = 13条）

- [ ] **Step 6: Commit**

```bash
git add backend/routers/kg_stages.py tests/kg/test_bom_hierarchy.py
git commit -m "feat: add _resolve_nha_triples to fix cross-figure NHA parent assignment (TASK_01 layer3)"
```

---

### Task 5：验收指标验证

**Files:**
- Read: `storage/kg_stages/stage1_bom_triples.json`（历史数据静态验证）
- Create: `tests/kg/test_bom_stage1_acceptance.py`

- [ ] **Step 1: 写验收测试（基于历史 JSON 静态验证，不需要跑 LLM）**

新建 `tests/kg/test_bom_stage1_acceptance.py`：

```python
"""
tests/kg/test_bom_stage1_acceptance.py

静态验收测试：读取已有的 stage1_bom_triples.json，验证指标。
不触发 LLM，纯离线验证。

注意：此测试验证的是最新一次 Stage1 运行的产物。
每次重新跑 Stage1 后再运行此测试。
"""
import json
from pathlib import Path
import pytest

STAGE1_PATH = Path(__file__).parents[2] / "storage/kg_stages/stage1_bom_triples.json"


@pytest.fixture(scope="module")
def stage1_data():
    if not STAGE1_PATH.exists():
        pytest.skip(f"stage1 产物不存在: {STAGE1_PATH}")
    with open(STAGE1_PATH, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def triples(stage1_data):
    return stage1_data.get("triples", [])


@pytest.fixture(scope="module")
def ispartof_triples(triples):
    return [t for t in triples if t.get("relation") == "isPartOf"]


class TestStage1Acceptance:

    def test_root_ratio_below_threshold(self, ispartof_triples):
        """tail==ROOT 占比应 < 40%。"""
        total = len(ispartof_triples)
        assert total > 0, "无 isPartOf 三元组，Stage1 未运行或产物为空"
        root_count = sum(1 for t in ispartof_triples if t.get("tail") == "ROOT")
        ratio = root_count / total
        assert ratio < 0.40, (
            f"ROOT 占比 {ratio:.1%}（{root_count}/{total}）仍超过 40% 门槛。\n"
            f"可能原因：LLM 仍漏填 nomenclature 点号，或 _resolve_nha_triples 未生效。"
        )

    def test_has_deep_hierarchy(self, ispartof_triples):
        """应存在至少一条非 ROOT 且 tail 也不是直接顶层的三元组（间接验证深度 ≥ 2）。"""
        non_root = [t for t in ispartof_triples if t.get("tail") != "ROOT"]
        assert len(non_root) > 0, "所有 isPartOf 均挂到 ROOT，层级完全扁平"
        # tail 的种类多于1说明有多层
        tail_values = {t["tail"] for t in ispartof_triples if t.get("tail") != "ROOT"}
        assert len(tail_values) >= 2, (
            f"只有 {len(tail_values)} 种非ROOT父节点，层级可能仍然过于扁平"
        )

    def test_has_interchanges_relation(self, triples):
        """应存在至少 2 条 interchangesWith 关系。"""
        interchanges = [t for t in triples if t.get("relation") == "interchangesWith"]
        assert len(interchanges) >= 2, (
            f"interchangesWith 关系仅 {len(interchanges)} 条，互换件识别可能失效"
        )

    def test_no_ocr_noise_in_entities(self, stage1_data):
        """实体名称中不应含 OCR 噪声（COMP0NENT 等）。"""
        entities = stage1_data.get("entities", [])
        noisy = [
            e["name"] for e in entities
            if "COMP0NENT" in e.get("name", "") or "C0MPONENT" in e.get("name", "")
        ]
        assert len(noisy) == 0, f"发现 {len(noisy)} 条含OCR噪声的实体名: {noisy[:5]}"
```

- [ ] **Step 2: 运行验收测试（基于现有历史数据）**

```bash
"C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" -m pytest tests/kg/test_bom_stage1_acceptance.py -v 2>&1
```

预期：`test_root_ratio_below_threshold` 会 FAIL（历史数据仍是 49.5%），其他3条应 PASS。这是正常的——此测试用于验证重新跑 Stage1 后的产物。

- [ ] **Step 3: 运行全部单元测试确认无回归**

```bash
"C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" -m pytest tests/kg/test_bom_hierarchy.py -v 2>&1
```

预期：13 passed

- [ ] **Step 4: Commit**

```bash
git add tests/kg/test_bom_stage1_acceptance.py
git commit -m "test: add Stage1 acceptance tests for BOM hierarchy metrics (TASK_01 验收)"
```

---

## 执行完成后的验证步骤

实施完毕后，需重新触发 Stage1（通过前端上传同一 PDF 文件），再运行：

```bash
"C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" -m pytest tests/kg/test_bom_stage1_acceptance.py -v 2>&1
```

全部 4 条 PASS 即表示 TASK_01 验收通过。
