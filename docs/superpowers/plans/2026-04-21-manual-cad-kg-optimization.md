# Manual & CAD KG Optimization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 Stage 2 手册 KG 的 BOM 对齐率从 7% 提升至 ≥35%，并为 Stage 3 CAD 装配树添加复合名称清洗和拓扑结构对齐。

**Architecture:** Stage 2 的核心是接通一个已有但未被调用的函数 `_build_prompt_with_bom`，同时增强它的内容（加名称列 + bom_id 注释指令），并在后处理中过滤乱码实体。Stage 3 在 `nodes_cad.py` 中新增 `_clean_composite_name` 辅助函数和 `_topology_align_cad_bom` 对齐函数，分别消除复合名称噪音和建立 CAD↔BOM 低置信度 hint。

**Tech Stack:** Python 3.10, FastAPI SSE, pytest；主要文件：`backend/routers/kg_stages.py`、`backend/pipelines/nodes_kg.py`、`backend/pipelines/nodes_cad.py`

---

## 文件变更总览

| 文件 | 操作 | 用途 |
|------|------|------|
| `backend/pipelines/nodes_kg.py` | 修改（第 109-129 行） | 增强 `_build_prompt_with_bom`：加名称列 + bom_id 注释指令 |
| `backend/routers/kg_stages.py` | 修改（第 955-958、977-980、747-772 行） | Stage 2 接通 BOM 注入；后处理加乱码过滤 |
| `backend/pipelines/nodes_cad.py` | 修改（第 293-308 行）+ 末尾新增函数 | 复合名称清洗；拓扑对齐函数 |
| `backend/routers/kg_stages.py` | 修改（第 1499、1586 行） | Stage 3 调用拓扑对齐；`_cad_data_to_flat_triples` 加 source_file |
| `tests/kg/test_manual_bom_align.py` | 新建 | Stage 2 相关单元测试 |
| `tests/kg/test_cad_topology.py` | 新建 | Stage 3 相关单元测试 |

---

## Task 1: 增强 `_build_prompt_with_bom`（名称列 + bom_id 指令）

**Files:**
- Modify: `backend/pipelines/nodes_kg.py:109-129`
- Test: `tests/kg/test_manual_bom_align.py`

- [ ] **Step 1: 写失败测试**

新建文件 `tests/kg/test_manual_bom_align.py`，内容如下：

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from backend.pipelines.nodes_kg import _build_prompt_with_bom


def test_bom_table_includes_name_column():
    """速查表应同时包含零件号和名称两列。"""
    bom_entities = [
        {"part_number": "3034521", "name": "CENTER FIRESEAL MOUNT RING"},
        {"part_number": "3034344", "name": "COMPRESSOR ROTOR INSTALLATION"},
    ]
    result = _build_prompt_with_bom("BASE_PROMPT", bom_entities)
    assert "CENTER FIRESEAL MOUNT RING" in result
    assert "3034521" in result
    assert "COMPRESSOR ROTOR INSTALLATION" in result
    assert "3034344" in result


def test_bom_table_includes_bom_id_annotation_instruction():
    """速查表说明中应包含 [BOM:{零件号}] 注释指令。"""
    bom_entities = [{"part_number": "3034521", "name": "MOUNT RING"}]
    result = _build_prompt_with_bom("BASE_PROMPT", bom_entities)
    assert "[BOM:" in result
    assert "bom_id" in result.lower() or "[BOM:" in result


def test_empty_bom_entities_returns_base_prompt():
    """空列表时返回原始 prompt 不变。"""
    result = _build_prompt_with_bom("MY_PROMPT", [])
    assert result == "MY_PROMPT"


def test_entities_without_part_number_still_show_name():
    """只有名称没有零件号的实体也应出现在速查表中。"""
    bom_entities = [{"part_number": "", "name": "THRUST BEARING"}]
    result = _build_prompt_with_bom("BASE_PROMPT", bom_entities)
    assert "THRUST BEARING" in result
```

- [ ] **Step 2: 运行测试，确认全部失败**

```bash
cd C:/xjp/代码/rag-demo
PYTHONUTF8=1 "C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" -m pytest tests/kg/test_manual_bom_align.py -v
```

预期：`test_bom_table_includes_name_column` 失败（速查表没有名称列），其余可能部分通过。

- [ ] **Step 3: 修改 `_build_prompt_with_bom`**

打开 `backend/pipelines/nodes_kg.py`，将第 109-129 行整段替换为：

```python
def _build_prompt_with_bom(base_prompt: str, bom_entities: list) -> str:
    """
    动态在 base_prompt 末尾追加 BOM 编号+名称速查表（≤80 条）。
    同时注入 [BOM:{零件号}] 打标指令，让 LLM 提取实体时直接标注 bom_id。
    """
    if not bom_entities:
        return base_prompt
    lines = []
    for e in bom_entities[:80]:
        pn   = e.get("part_number", "")
        name = e.get("name", "")
        if pn and name:
            lines.append(f"  {pn:<16} {name}")
        elif name:
            lines.append(f"  {'':16} {name}")
        elif pn:
            lines.append(f"  {pn:<16}")
    if not lines:
        return base_prompt
    section = (
        "\n\n【当前 BOM 零件编号速查表（按零件号或名称匹配）】\n"
        "提取实体时，若实体名称或文本中的零件编号能对应以下任一条目，\n"
        "请在该实体的 text 字段末尾加注 [BOM:{零件号}]，"
        "例如：\"Center Fireseal Mount Ring [BOM:3034521]\"。\n"
        "零件号列（左）      名称列（右）\n"
        + "\n".join(lines)
    )
    return base_prompt + section
```

- [ ] **Step 4: 运行测试，确认全部通过**

```bash
PYTHONUTF8=1 "C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" -m pytest tests/kg/test_manual_bom_align.py -v
```

预期：4 个测试全部 PASS。

- [ ] **Step 5: 提交**

```bash
git add backend/pipelines/nodes_kg.py tests/kg/test_manual_bom_align.py
git commit -m "feat(stage2): enhance _build_prompt_with_bom with name column and bom_id annotation"
```

---

## Task 2: Stage 2 接通 BOM 速查表注入

**Files:**
- Modify: `backend/routers/kg_stages.py:955-958, 977-980`
- Test: `tests/kg/test_manual_bom_align.py`（追加）

- [ ] **Step 1: 写失败测试**

在 `tests/kg/test_manual_bom_align.py` 末尾追加：

```python
from unittest.mock import patch, MagicMock


def test_stage2_prompt_includes_bom_when_bom_exists():
    """Stage 2 提取时 prompt 应包含 BOM 速查表内容。"""
    captured_prompts = []

    # 模拟 LLM 客户端
    mock_resp = MagicMock()
    mock_resp.choices[0].message.content = '{"entities":[],"relations":[]}'
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_resp

    # 模拟 BOM 数据已存在
    mock_bom = {
        "entities": [
            {"part_number": "3034521", "name": "CENTER FIRESEAL MOUNT RING"},
        ]
    }

    def fake_create(messages, temperature):
        captured_prompts.append(messages[0]["content"])
        return mock_resp

    mock_client.chat.completions.create.side_effect = fake_create

    from backend.routers.kg_stages import _stage2_manual_gen
    from backend.app_state import AppState

    state = MagicMock(spec=AppState)
    state.llm_client = mock_client

    with patch("backend.routers.kg_stages.stage_exists", return_value=True), \
         patch("backend.routers.kg_stages.read_stage", return_value=mock_bom), \
         patch("backend.routers.kg_stages._extract_pdf_chunks",
               return_value=([{"text": "Remove nuts and bolts. Apply torque.",
                               "chunk_id": "c1", "ata_section": "72-30-01"}], "pdfplumber")):
        list(_stage2_manual_gen("fake.pdf", "test.pdf", state, {}))

    assert len(captured_prompts) > 0
    assert "CENTER FIRESEAL MOUNT RING" in captured_prompts[0], \
        "BOM 名称未注入 prompt，说明 _build_prompt_with_bom 未被调用"
```

- [ ] **Step 2: 运行测试，确认新增测试失败**

```bash
PYTHONUTF8=1 "C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" -m pytest tests/kg/test_manual_bom_align.py::test_stage2_prompt_includes_bom_when_bom_exists -v
```

预期：FAIL — `AssertionError: BOM 名称未注入 prompt`。

- [ ] **Step 3: 修改 `_stage2_manual_gen` 接通 BOM 注入**

打开 `backend/routers/kg_stages.py`，找到第 955-958 行（`from backend.pipelines.nodes_kg import ...`），将其改为同时导入 `_build_prompt_with_bom`：

```python
    from backend.pipelines.nodes_kg import (
        _is_procedure_text, _KG_EXTRACTION_PROMPT, _KG_GLEANING_PROMPT, _parse_kg_json,
        _build_prompt_with_bom,
    )
    import json as _json
```

然后找到第 977-980 行（`prompt = _KG_EXTRACTION_PROMPT.format(...)`），替换为：

```python
                _bom_ents: list = []
                if stage_exists("bom"):
                    _bom_data = read_stage("bom") or {}
                    _bom_ents = _bom_data.get("entities", [])
                base_prompt = _KG_EXTRACTION_PROMPT.format(
                    ata_section=ata_section,
                    chunk_text=text,
                )
                prompt = _build_prompt_with_bom(base_prompt, _bom_ents)
```

- [ ] **Step 4: 运行全部手册对齐测试**

```bash
PYTHONUTF8=1 "C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" -m pytest tests/kg/test_manual_bom_align.py -v
```

预期：5 个测试全部 PASS。

- [ ] **Step 5: 提交**

```bash
git add backend/routers/kg_stages.py tests/kg/test_manual_bom_align.py
git commit -m "feat(stage2): wire _build_prompt_with_bom into _stage2_manual_gen"
```

---

## Task 3: 后处理乱码实体过滤

**Files:**
- Modify: `backend/routers/kg_stages.py:747-772`
- Test: `tests/kg/test_manual_bom_align.py`（追加）

- [ ] **Step 1: 写失败测试**

在 `tests/kg/test_manual_bom_align.py` 末尾追加：

```python
from backend.routers.kg_stages import _post_process_triples


def test_garbled_head_entity_is_filtered():
    """head 含乱码字符（Unicode 替换字符）的三元组应被过滤。"""
    triples = [
        {"head": "\ufffd\ufffd\ufffd\ufffd", "tail": "Gas generator case",
         "relation": "matesWith", "confidence": 0.8,
         "head_type": "Assembly", "tail_type": "Assembly"},
    ]
    result = _post_process_triples(triples)
    assert result == [], f"Expected empty list, got {result}"


def test_garbled_tail_entity_is_filtered():
    """tail 含乱码字符的三元组也应被过滤。"""
    triples = [
        {"head": "Compressor Rotor", "tail": "\ufffd\ufffdȥ\ufffd\ufffd",
         "relation": "matesWith", "confidence": 0.9,
         "head_type": "Assembly", "tail_type": "Assembly"},
    ]
    result = _post_process_triples(triples)
    assert result == []


def test_normal_english_entity_passes_through():
    """正常英文实体不应被误过滤。"""
    triples = [
        {"head": "Center Fireseal Mount Ring", "tail": "Gas Generator Case",
         "relation": "matesWith", "confidence": 0.85,
         "head_type": "Assembly", "tail_type": "Assembly"},
    ]
    result = _post_process_triples(triples)
    assert len(result) == 1
```

- [ ] **Step 2: 运行测试，确认乱码测试失败**

```bash
PYTHONUTF8=1 "C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" -m pytest tests/kg/test_manual_bom_align.py::test_garbled_head_entity_is_filtered tests/kg/test_manual_bom_align.py::test_garbled_tail_entity_is_filtered -v
```

预期：FAIL — 乱码三元组未被过滤。

- [ ] **Step 3: 在 `_post_process_triples` 中添加乱码过滤规则**

打开 `backend/routers/kg_stages.py`，找到第 747 行的 `def _post_process_triples`。在函数开头的 `import re as _re` 之后，紧跟 `_noise_pattern` 定义之后，在 `for t in triples:` 循环里、`filtered.append(t)` 之前，添加以下乱码检测逻辑：

将第 753-772 行的循环体替换为：

```python
    import unicodedata as _ud

    def _is_garbled(text: str) -> bool:
        if not text:
            return False
        bad = sum(
            1 for c in text
            if c == "\ufffd" or _ud.category(c) in ("Cs", "Co", "Cn")
        )
        return bad / len(text) > 0.3

    filtered = []
    for t in triples:
        if t.get("confidence", 0) < 0.3:
            continue
        head, tail = t.get("head", ""), t.get("tail", "")
        if len(head) < 4 or len(tail) < 4:
            continue
        if _noise_pattern.match(head.strip()) or _noise_pattern.match(tail.strip()):
            continue
        if _is_garbled(head) or _is_garbled(tail):
            continue
        rel = t.get("relation", "")
        head_type = t.get("head_type", "")
        tail_type = t.get("tail_type", "")
        if rel == "specifiedBy":
            if head_type not in ("Procedure", "Interface", "Part", "Assembly"):
                continue
        if rel == "precedes":
            if head_type != "Procedure" or tail_type != "Procedure":
                continue
        filtered.append(t)
    return filtered
```

注意：`import re as _re` 和 `_noise_pattern` 定义（第 749-752 行）保持不变，只替换 `filtered = []` 及之后的部分。

- [ ] **Step 4: 运行全部测试**

```bash
PYTHONUTF8=1 "C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" -m pytest tests/kg/test_manual_bom_align.py -v
```

预期：所有 8 个测试全部 PASS。

- [ ] **Step 5: 提交**

```bash
git add backend/routers/kg_stages.py tests/kg/test_manual_bom_align.py
git commit -m "feat(stage2): filter garbled entities in _post_process_triples"
```

---

## Task 4: 复合名称清洗（`_clean_composite_name`）

**Files:**
- Modify: `backend/pipelines/nodes_cad.py:293-308`（在数字前缀补全段之后插入）
- Test: `tests/kg/test_cad_topology.py`

- [ ] **Step 1: 写失败测试**

新建文件 `tests/kg/test_cad_topology.py`，内容如下：

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from backend.pipelines.nodes_cad import _clean_composite_name


def test_ampersand_pair_splits_into_two():
    """'100&110' 应拆分为 ['C52696C-100', 'C52696C-110']。"""
    result = _clean_composite_name("100&110", "C52696C")
    assert result == ["C52696C-100", "C52696C-110"]


def test_ampersand_triple_splits_into_three():
    """'100&110&120' 应拆分为三个带前缀的名称。"""
    result = _clean_composite_name("100&110&120", "C52696C")
    assert result == ["C52696C-100", "C52696C-110", "C52696C-120"]


def test_non_numeric_ampersand_not_split():
    """'190&200' 两边均为纯数字，应拆分。"""
    result = _clean_composite_name("190&200", "C52696C")
    assert result == ["C52696C-190", "C52696C-200"]


def test_descriptive_name_with_spaces_not_split():
    """'370-2 holes' 有空格，不是纯数字组合，不应拆分。"""
    result = _clean_composite_name("370-2 holes", "C52696C")
    assert result == ["370-2 holes"]


def test_already_prefixed_name_not_split():
    """'C52696C-10' 已带前缀，不含 '&'，直接原样返回。"""
    result = _clean_composite_name("C52696C-10", "C52696C")
    assert result == ["C52696C-10"]


def test_single_numeric_not_split():
    """'100' 单个纯数字，不含 '&'，直接原样返回（单元素列表）。"""
    result = _clean_composite_name("100", "C52696C")
    assert result == ["100"]
```

- [ ] **Step 2: 运行测试，确认失败（函数不存在）**

```bash
PYTHONUTF8=1 "C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" -m pytest tests/kg/test_cad_topology.py -v
```

预期：全部 FAIL — `ImportError: cannot import name '_clean_composite_name'`。

- [ ] **Step 3: 实现 `_clean_composite_name` 并接入装配树解析**

打开 `backend/pipelines/nodes_cad.py`。

**第一步**：在文件顶部 `_NUMERIC_NAME_RE` 定义处（第 23 行）之后添加辅助函数：

```python
def _clean_composite_name(name: str, root: str) -> list:
    """
    处理形如 '100&110'、'190&200' 的多实例复合名称（纯数字用 & 连接）。
    返回拆分并补全前缀后的名称列表。
    非纯数字组合（如 '370-2 holes'）原样返回单元素列表。
    """
    _MULTI_RE = re.compile(r'^(\d+)(&\d+)+$')
    if _MULTI_RE.match(name):
        parts = name.split('&')
        return [
            f"{root}-{p}" if _NUMERIC_NAME_RE.match(p) else p
            for p in parts
        ]
    return [name]
```

**第二步**：在 `_parse_step_tree_from_text` 函数的数字前缀补全段末尾（第 308 行，`parent_map = {_fix(c): _fix(p) for c, p in parent_map.items()}` 之后），添加复合名展开：

```python
                parent_map = {_fix(c): _fix(p) for c, p in parent_map.items()}

    # ── 复合名称展开（'100&110' → 'C52696C-100', 'C52696C-110'）────────────
    if parent_map:
        _all2 = set(parent_map.keys()) | set(parent_map.values())
        _roots2 = _all2 - set(parent_map.keys())
        _top2 = next(iter(_roots2)) if len(_roots2) == 1 else ""
        new_map: dict = {}
        for child, parent in parent_map.items():
            for expanded in _clean_composite_name(child, _top2):
                new_map[expanded] = parent
        parent_map = new_map
```

- [ ] **Step 4: 运行测试**

```bash
PYTHONUTF8=1 "C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" -m pytest tests/kg/test_cad_topology.py -v
```

预期：6 个测试全部 PASS。

- [ ] **Step 5: 验证 C52696C 装配树不再含 `&` 节点**

```bash
PYTHONUTF8=1 "C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" -c "
import sys; sys.path.insert(0,'.')
from backend.pipelines.nodes_cad import _parse_step_tree_from_text
import json
tree = _parse_step_tree_from_text('data/KG/C52696C.STEP')
flat = []
def collect(node):
    for k, v in node.items():
        flat.append(k)
        collect(v)
collect(tree)
bad = [n for n in flat if '&' in n]
print(f'Total nodes: {len(flat)}, Ampersand nodes: {bad}')
"
```

预期输出：`Ampersand nodes: []`。

- [ ] **Step 6: 提交**

```bash
git add backend/pipelines/nodes_cad.py tests/kg/test_cad_topology.py
git commit -m "feat(stage3): add _clean_composite_name to expand multi-instance STEP nodes"
```

---

## Task 5: 拓扑结构对齐（`_topology_align_cad_bom`）

**Files:**
- Modify: `backend/pipelines/nodes_cad.py`（末尾追加函数）
- Modify: `backend/routers/kg_stages.py:1499, 1586`（Stage 3 调用处）
- Test: `tests/kg/test_cad_topology.py`（追加）

- [ ] **Step 1: 写失败测试**

在 `tests/kg/test_cad_topology.py` 末尾追加：

```python
from backend.pipelines.nodes_cad import _topology_align_cad_bom


def test_topology_align_matches_by_depth_and_sibling_index():
    """
    CAD 树和 BOM 树结构相同时，应按 (depth, sibling_index) 位置对齐。
    CAD 根 → [child_a, child_b]
    BOM 根 → [bom_part_1, bom_part_2]
    期望：child_a → bom_part_1，child_b → bom_part_2
    """
    cad_tree = {
        "C52696C": {
            "C52696C-10": {},
            "C52696C-20": {},
        }
    }
    bom_entities = [
        {"id": "ROOT", "name": "COMPRESSOR ASSY",    "part_number": "3034344", "parent_id": "ROOT"},
        {"id": "P001", "name": "COMPRESSOR ROTOR",   "part_number": "3034100", "parent_id": "ROOT"},
        {"id": "P002", "name": "COMPRESSOR STATOR",  "part_number": "3034200", "parent_id": "ROOT"},
    ]
    result = _topology_align_cad_bom(cad_tree, bom_entities)
    assert "C52696C-10" in result
    assert result["C52696C-10"]["method"] == "topology"
    assert result["C52696C-10"]["bom_id"] == "P001"
    assert "C52696C-20" in result
    assert result["C52696C-20"]["bom_id"] == "P002"


def test_topology_align_returns_empty_when_no_bom():
    """BOM 实体为空时返回空字典。"""
    cad_tree = {"C89119": {"C89119-10": {}}}
    result = _topology_align_cad_bom(cad_tree, [])
    assert result == {}


def test_topology_align_unmatched_cad_node_not_in_result():
    """CAD 树节点多于 BOM 节点时，多余的 CAD 节点不出现在结果中。"""
    cad_tree = {
        "C52696C": {
            "C52696C-10": {},
            "C52696C-20": {},
            "C52696C-30": {},   # BOM 只有 2 个子节点
        }
    }
    bom_entities = [
        {"id": "ROOT", "name": "ASSY",   "part_number": "0001", "parent_id": "ROOT"},
        {"id": "P001", "name": "PART A", "part_number": "0002", "parent_id": "ROOT"},
        {"id": "P002", "name": "PART B", "part_number": "0003", "parent_id": "ROOT"},
    ]
    result = _topology_align_cad_bom(cad_tree, bom_entities)
    assert "C52696C-30" not in result
```

- [ ] **Step 2: 运行测试，确认失败（函数不存在）**

```bash
PYTHONUTF8=1 "C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" -m pytest tests/kg/test_cad_topology.py::test_topology_align_matches_by_depth_and_sibling_index tests/kg/test_cad_topology.py::test_topology_align_returns_empty_when_no_bom -v
```

预期：FAIL — `ImportError: cannot import name '_topology_align_cad_bom'`。

- [ ] **Step 3: 在 `nodes_cad.py` 末尾实现 `_topology_align_cad_bom`**

在 `backend/pipelines/nodes_cad.py` 文件末尾（第 593 行之后）追加：

```python


def _topology_align_cad_bom(
    cad_tree: dict,
    bom_entities: list,
) -> dict:
    """
    按装配树层级位置（depth, sibling_index）匹配 CAD 节点与 BOM 实体。
    返回 {cad_name: {"bom_id", "bom_name", "bom_pn", "method": "topology"}}。
    仅提供 hint（置信度语义为 0.5），不强制绑定。
    """
    if not bom_entities:
        return {}

    # 1. 展平 CAD 树：记录每个节点的 (depth, sibling_index)
    cad_positions: dict = {}  # cad_name → (depth, sibling_index)

    def _flatten_cad(node: dict, depth: int = 0) -> None:
        for idx, (child, subtree) in enumerate(node.items()):
            cad_positions[child] = (depth, idx)
            if isinstance(subtree, dict):
                _flatten_cad(subtree, depth + 1)

    _flatten_cad(cad_tree)

    # 2. 展平 BOM 树：按 parent_id 重建层级，记录 (depth, sibling_index)
    bom_by_id = {e["id"]: e for e in bom_entities if e.get("id")}
    bom_children: dict = {}
    for e in bom_entities:
        pid = e.get("parent_id", "ROOT")
        bom_children.setdefault(pid, []).append(e["id"])

    bom_pos_map: dict = {}  # (depth, sibling_index) → (id, name, pn)

    def _flatten_bom(parent_id: str = "ROOT", depth: int = 0) -> None:
        for idx, eid in enumerate(bom_children.get(parent_id, [])):
            e = bom_by_id.get(eid, {})
            bom_pos_map[(depth, idx)] = (
                eid,
                e.get("name", ""),
                e.get("part_number", ""),
            )
            _flatten_bom(eid, depth + 1)

    _flatten_bom()

    # 3. 按位置配对
    mapping: dict = {}
    for cad_name, pos in cad_positions.items():
        if pos in bom_pos_map:
            eid, bom_name, bom_pn = bom_pos_map[pos]
            mapping[cad_name] = {
                "bom_id":   eid,
                "bom_name": bom_name,
                "bom_pn":   bom_pn,
                "method":   "topology",
            }

    return mapping
```

- [ ] **Step 4: 运行测试**

```bash
PYTHONUTF8=1 "C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" -m pytest tests/kg/test_cad_topology.py -v
```

预期：所有 9 个测试全部 PASS。

- [ ] **Step 5: 在 Stage 3 单文件流程中调用拓扑对齐 + 添加 source_file 字段**

打开 `backend/routers/kg_stages.py`，找到 `_stage3_cad_gen` 函数。

**5a. `_cad_data_to_flat_triples` 加 source_file 参数**（约第 1173 行函数定义处）：

将函数签名改为：
```python
def _cad_data_to_flat_triples(assembly_tree, constraints, adjacency, source_file: str = "") -> list:
```

在函数末尾 `return triples` 之前插入：
```python
    if source_file:
        for t in triples:
            t["cad_source_file"] = source_file
```

**5b. 在单文件流程中传入 source_file**（约第 1499 行）：

将 `flat_triples = _cad_data_to_flat_triples(assembly_tree, constraints, adjacency)` 改为：
```python
    flat_triples = _cad_data_to_flat_triples(
        assembly_tree, constraints, adjacency,
        source_file=os.path.basename(tmp_path),
    )
```

**5c. 插入拓扑对齐调用**（位置：`if bom_entities_for_cad:` 块内，`cad_mapping = _align_cad_to_bom(...)` 调用之后，约第 1509-1515 行）：

```python
    if bom_entities_for_cad:
        cad_mapping = _align_cad_to_bom(flat_triples, bom_entities_for_cad, state)
        # ... 现有代码（method_dist、hit、yield log）保持不变 ...

        # ── 新增：拓扑结构对齐 hint ──────────────────────────────────────
        from backend.pipelines.nodes_cad import _topology_align_cad_bom
        topo_map = _topology_align_cad_bom(assembly_tree, bom_entities_for_cad)
        for t in flat_triples:
            for field in ("head", "tail"):
                name = t.get(field, "")
                if name in topo_map and not t.get(f"{field}_bom_id"):
                    info = topo_map[name]
                    t[f"{field}_bom_id"]     = info["bom_id"]
                    t[f"{field}_bom_name"]   = info["bom_name"]
                    t[f"{field}_bom_method"] = "topology"
        topo_hits = sum(
            1 for t in flat_triples
            if t.get("head_bom_method") == "topology"
            or t.get("tail_bom_method") == "topology"
        )
        yield {"type": "log", "message": f"[Stage3] 拓扑对齐 hint：{topo_hits} 条三元组"}
```

**5d. 批量流程同样处理**（`_stage3_cad_batch_gen`，约第 1586 行）：

将 `flat = _cad_data_to_flat_triples(assembly_tree, constraints, adjacency)` 改为：
```python
        flat = _cad_data_to_flat_triples(
            assembly_tree, constraints, adjacency,
            source_file=orig_name,
        )
```

在批量流程的 `if bom_entities_for_cad:` 块内（约第 1603 行，`cad_mapping = _align_cad_to_bom(...)` 之后），追加拓扑对齐（注意此处是对 `all_triples` 操作，assembly_tree 不可用，跳过拓扑对齐；拓扑对齐仅在单文件流程有意义）：

```python
    # 批量模式：各文件 source_file 已在 _cad_data_to_flat_triples 中打标
    # 拓扑对齐依赖单文件 assembly_tree，批量模式不运行
```

即批量模式不运行拓扑对齐（assembly_tree 在 all_triples 汇总后已不可用），只保留 source_file 字段即可。

- [ ] **Step 6: 运行全部 CAD 测试**

```bash
PYTHONUTF8=1 "C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" -m pytest tests/kg/test_cad_topology.py tests/kg/test_stage3_naming.py -v
```

预期：全部 PASS（不破坏已有 Stage 3 命名测试）。

- [ ] **Step 7: 提交**

```bash
git add backend/pipelines/nodes_cad.py backend/routers/kg_stages.py tests/kg/test_cad_topology.py
git commit -m "feat(stage3): add topology CAD-BOM alignment and integrate into stage3 pipeline"
```

---

## Task 6: 端到端验证

**Files:**
- 无新文件，运行全量测试套件

- [ ] **Step 1: 运行全量 KG 测试套件**

```bash
PYTHONUTF8=1 "C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" -m pytest tests/kg/ -v --tb=short 2>&1 | tail -30
```

预期：所有测试通过，无新增失败。

- [ ] **Step 2: 验证 Stage 2 BOM 对齐率**

```bash
PYTHONUTF8=1 "C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" -c "
import json
with open('storage/kg_stages/stage2_manual_triples.json', encoding='utf-8') as f:
    d = json.load(f)
triples = d.get('triples', [])
linked = [t for t in triples if t.get('head_bom_id') or t.get('tail_bom_id')]
print(f'Total triples: {len(triples)}')
print(f'BOM-linked: {len(linked)} ({100*len(linked)/max(len(triples),1):.1f}%)')
garbled = [t for t in triples if '\ufffd' in t.get('head','') or '\ufffd' in t.get('tail','')]
print(f'Garbled entities: {len(garbled)}')
"
```

注意：此步骤需要先通过前端重新上传 `压气机维修手册.pdf` 入库（Stage 2），让新代码生效，否则 JSON 是旧数据。

- [ ] **Step 3: 验证 C52696C 装配树三元组**

上传 `data/KG/C52696C.STEP` 通过前端入库后运行：

```bash
PYTHONUTF8=1 "C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" -c "
import json
with open('storage/kg_stages/stage3_cad_triples.json', encoding='utf-8') as f:
    d = json.load(f)
triples = d.get('triples', [])
isPartOf = [t for t in triples if t['relation'] == 'isPartOf']
bad_names = [t for t in triples if '&' in t.get('head','') or '&' in t.get('tail','')]
topo = [t for t in triples if t.get('head_bom_method') == 'topology' or t.get('tail_bom_method') == 'topology']
print(f'isPartOf triples: {len(isPartOf)} (目标 ≥ 40)')
print(f'Ampersand noise nodes: {len(bad_names)} (目标 0)')
print(f'Topology-aligned triples: {len(topo)}')
"
```

预期：`isPartOf ≥ 40`，`Ampersand noise = 0`。

- [ ] **Step 4: 最终提交**

```bash
git add .
git commit -m "test(kg): end-to-end validation for Stage2 BOM alignment and Stage3 CAD topology"
```
