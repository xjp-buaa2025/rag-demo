# Manual & CAD KG Optimization Design

## Goal

提升 Stage 2（维修手册 → KG）的 BOM 对齐率（7% → 35%+），并修复 Stage 3（CAD STEP → KG）的复合名称噪音、补充拓扑结构对齐，使两阶段 KG 数据质量达到可用于 Stage 4 跨源验证的水平。

## Architecture

两个阶段独立优化，但共享同一次实施周期。

**Stage 2** 的核心问题是"BOM 速查表注入函数存在却未被调用"——一行接线 + 增强速查表内容 + 加注释指令，即可大幅提升 LLM 打标准确率。

**Stage 3** 的解析本身正常（两个 STEP 文件均可提取完整装配树），重点在于清洗复合名称噪音、增加拓扑结构对齐，为跨源验证提供低置信度 hint。

## Tech Stack

- Python 3.10, FastAPI SSE pipeline
- `backend/routers/kg_stages.py` — Stage 2/3 主流程
- `backend/pipelines/nodes_kg.py` — KG 提取 prompt + 工具函数
- `backend/pipelines/nodes_cad.py` — STEP 解析 + CAD 树处理
- LLM: OpenAI-compatible API (Qwen via vLLM)

---

## Stage 2 设计

### 问题根因

`_stage2_manual_gen`（`kg_stages.py:977`）直接调用裸 `_KG_EXTRACTION_PROMPT.format(...)`，完全跳过了 `nodes_kg.py` 中已有的 `_build_prompt_with_bom()` 函数。

此外，`_build_prompt_with_bom` 当前只在速查表里注入零件号（`3034344`），而维修手册中出现的是零件名（`CENTER FIRESEAL MOUNT RING`），导致 LLM 无法匹配。

### 修改清单

#### 改动 ① — 接通 BOM 速查表注入（`kg_stages.py`）

**位置**：`_stage2_manual_gen` 函数内，约第 977 行

```python
# 改前
prompt = _KG_EXTRACTION_PROMPT.format(
    ata_section=ata_section,
    chunk_text=text,
)

# 改后（read_stage/stage_exists 已在模块顶部导入，无需重复）
_bom_ents = []
if stage_exists("bom"):
    _bom_data = read_stage("bom") or {}
    _bom_ents = _bom_data.get("entities", [])
base_prompt = _KG_EXTRACTION_PROMPT.format(
    ata_section=ata_section,
    chunk_text=text,
)
prompt = _build_prompt_with_bom(base_prompt, _bom_ents)
```

注意：`read_stage`/`stage_exists` 在该函数作用域内已导入，可直接使用。

#### 改动 ② — 增强 BOM 速查表格式（`nodes_kg.py`）

**位置**：`_build_prompt_with_bom` 函数，约第 109 行

```python
# 改前：只输出零件号
lines.append(f"  {pn:<16} {name}")

# 改后：零件号 + 名称，供 LLM 按名称匹配
for e in bom_entities[:80]:          # 上限从 60 提升到 80
    pn   = e.get("part_number", "")
    name = e.get("name", "")
    if pn and name:
        lines.append(f"  {pn:<16} {name}")
    elif name:
        lines.append(f"  {'':16} {name}")
```

同时把速查表标题和说明更新为同时提示名称匹配：

```python
section = (
    "\n\n【当前 BOM 零件编号速查表（按零件号或名称匹配）】\n"
    "提取实体时，若实体名称或文本中的零件编号能对应以下任一条目，\n"
    "请在该实体的 text 字段末尾加注 [BOM:{零件号}]，例如：\"Center Fireseal Mount Ring [BOM:3034521]\"。\n"
    "零件号列（左）  名称列（右）\n"
    + "\n".join(lines)
)
```

#### 改动 ③ — 乱码实体过滤（`kg_stages.py` 的 `_post_process_triples`）

维修手册是英文 PDF，但部分扫描页面会产生非 ASCII 乱码实体（如 `'����ȥ��'`）。在现有后处理函数中增加一条规则：

```python
def _post_process_triples(triples: list[dict]) -> list[dict]:
    import unicodedata
    filtered = []
    for t in triples:
        # 现有规则（置信度、长度、本体约束）...

        # 新增：乱码实体过滤
        # 若实体超过 30% 字符是替换字符或控制字符，视为乱码跳过
        def _is_garbled(text: str) -> bool:
            if not text:
                return False
            bad = sum(1 for c in text if unicodedata.category(c) in ('Cs', 'Co', 'Cn') or c == '\ufffd')
            return bad / len(text) > 0.3

        if _is_garbled(t.get("head", "")) or _is_garbled(t.get("tail", "")):
            continue

        filtered.append(t)
    return filtered
```

### 预期指标

| 指标 | 改前 | 改后 |
|------|------|------|
| BOM 对齐率 | 7% (29/405) | ≥35% |
| 乱码实体数 | ~4 条 | 0 |
| LLM 调用次数/段 | 不变 | 不变（无额外调用） |

---

## Stage 3 设计

### 问题根因

- C89119.STEP（15 个子零件）和 C52696C.STEP（30+ 子零件）的装配树提取均正常，当前 stage3 JSON 只有 30 条三元组是因为上次入库未包含 C52696C.STEP，不是解析 bug。
- C52696C.STEP 含复合名称节点（`100&110`、`190&200`、`370-2 holes`），这些是 STEP 多实例引用的产物，需要清洗。
- 两个 STEP 文件的 CAD 零件号（`C52696C-10`）与 BOM 零件号（`3034xxx`）是两套独立编号体系，无法字符串匹配；需要用装配树拓扑结构做低置信度桥接。

### 修改清单

#### 改动 ④ — 复合名称清洗（`nodes_cad.py`）

**位置**：`_parse_step_tree_from_text` 函数数字前缀补全段之后，约第 296 行

```python
def _clean_composite_name(name: str, root: str) -> list[str]:
    """
    处理形如 '100&110'、'190&200' 的多实例复合名称。
    返回拆分后的名称列表（每个子名称已完成根前缀补全）。
    '370-2 holes' 等描述性后缀名直接原样返回（单元素列表）。
    """
    import re
    # 仅拆分形如 'N&M' 或 'N&M&K' 的纯数字组合
    _MULTI_RE = re.compile(r'^(\d+)(?:&(\d+))+$')
    if _MULTI_RE.match(name):
        parts = name.split('&')
        result = []
        for p in parts:
            fixed = f"{root}-{p}" if _NUMERIC_NAME_RE.match(p) else p
            result.append(fixed)
        return result
    return [name]
```

在 `parent_map` 构建完成后，对所有包含复合名称的节点展开：

```python
# 展开复合名称
new_map = {}
_top = next(iter(_roots)) if _roots else ""
for child, parent in parent_map.items():
    expanded = _clean_composite_name(child, _top)
    for c in expanded:
        new_map[c] = parent
parent_map = new_map
```

#### 改动 ⑤ — 拓扑结构对齐（`nodes_cad.py` 新函数）

**位置**：`nodes_cad.py` 末尾新增函数，并在 `kg_stages.py` Stage 3 流程中调用

```python
def _topology_align_cad_bom(
    cad_tree: dict,
    bom_entities: list[dict],
) -> dict:
    """
    按装配树层级位置（深度 + 同层序号）匹配 CAD 节点与 BOM 实体。
    返回 {cad_part_name: {"bom_id": str, "bom_name": str, "method": "topology"}}。
    置信度固定为 0.5（仅提供 hint，不强制绑定）。
    """
    # 1. 展平 CAD 树：每个节点记录 (depth, sibling_index, name)
    def _flatten(node: dict, depth: int = 0, idx: int = 0) -> list[tuple]:
        result = []
        for i, (child, subtree) in enumerate(node.items()):
            result.append((depth, i, child))
            result.extend(_flatten(subtree, depth + 1, i))
        return result

    cad_nodes = _flatten(cad_tree)  # [(depth, sibling_idx, name), ...]

    # 2. 展平 BOM 树：按 parent_id 重建层级，记录同样的位置信息
    # bom_entities: [{"id": str, "name": str, "parent_id": str, ...}]
    bom_by_id = {e["id"]: e for e in bom_entities if e.get("id")}
    bom_children: dict = {}
    for e in bom_entities:
        pid = e.get("parent_id", "ROOT")
        bom_children.setdefault(pid, []).append(e["id"])

    def _flatten_bom(parent_id: str = "ROOT", depth: int = 0) -> list[tuple]:
        result = []
        for i, eid in enumerate(bom_children.get(parent_id, [])):
            e = bom_by_id.get(eid, {})
            result.append((depth, i, eid, e.get("name", ""), e.get("part_number", "")))
            result.extend(_flatten_bom(eid, depth + 1))
        return result

    bom_nodes = _flatten_bom()  # [(depth, sibling_idx, id, name, pn), ...]

    # 3. 按 (depth, sibling_idx) 配对
    bom_by_pos = {(d, i): (eid, name, pn) for d, i, eid, name, pn in bom_nodes}
    mapping = {}
    for depth, idx, cad_name in cad_nodes:
        if (depth, idx) in bom_by_pos:
            eid, bom_name, bom_pn = bom_by_pos[(depth, idx)]
            mapping[cad_name] = {
                "bom_id":   eid,
                "bom_name": bom_name,
                "bom_pn":   bom_pn,
                "method":   "topology",
            }

    return mapping
```

在 `kg_stages.py` 的 Stage 3 流程里，在生成 `flat_triples` 后调用：

```python
# 拓扑结构对齐（置信度 0.5 hint）
if bom_entities_for_cad:
    topo_map = _topology_align_cad_bom(assembly_tree, bom_entities_for_cad)
    for t in flat_triples:
        for field in ("head", "tail"):
            name = t.get(field, "")
            if name in topo_map and not t.get(f"{field}_bom_id"):
                info = topo_map[name]
                t[f"{field}_bom_id"]   = info["bom_id"]
                t[f"{field}_bom_name"] = info["bom_name"]
                t[f"{field}_bom_method"] = "topology"
    topo_hits = sum(1 for t in flat_triples if t.get("head_bom_method") == "topology" or t.get("tail_bom_method") == "topology")
    yield {"type": "log", "message": f"[Stage3] 拓扑对齐 hint：{topo_hits} 条三元组"}
```

#### 改动 ⑥ — 每条三元组加来源文件字段（`kg_stages.py`）

**位置**：`_cad_data_to_flat_triples` 调用处，或在 `_cad_data_to_flat_triples` 内部加参数

```python
# _cad_data_to_flat_triples 增加可选参数
def _cad_data_to_flat_triples(
    assembly_tree, constraints, adjacency, source_file: str = ""
) -> list[dict]:
    # ... 现有逻辑 ...
    # 在每条 triple 里追加 source_file 字段
    for t in triples:
        if source_file:
            t["cad_source_file"] = source_file
    return triples
```

### 预期指标

| 指标 | 改前 | 改后 |
|------|------|------|
| C89119 isPartOf 三元组数 | 15 | 15（不变，已正常） |
| C52696C isPartOf 三元组数 | 0（未入库） | ~50（完整装配树） |
| 复合名称噪音节点 | ~5 个 | 0 |
| CAD→BOM 拓扑 hint 覆盖率 | 0% | ~60%（topology 方法） |

---

## 文件变更总览

| 文件 | 改动类型 | 改动编号 |
|------|----------|----------|
| `backend/routers/kg_stages.py` | 修改 | ①③⑤调用处⑥ |
| `backend/pipelines/nodes_kg.py` | 修改 | ②速查表增强 |
| `backend/pipelines/nodes_cad.py` | 修改 + 新增函数 | ④⑤⑥签名 |
| `tests/kg/` | 新增测试 | ①②④⑤各一组 |

---

## 测试策略

### Stage 2 测试

- **对齐率回归**：入库 `压气机维修手册.pdf`，检查 `stage2_manual_triples.json` 中 `head_bom_id` 或 `tail_bom_id` 非空的三元组占比 ≥ 35%
- **乱码实体**：`head` 或 `tail` 包含 `\ufffd` 或 Unicode 替换字符的三元组数量 = 0
- **单元测试 `_build_prompt_with_bom`**：传入含名称和零件号的 bom_entities，断言返回字符串包含名称列和 `[BOM:{pn}]` 注释指令

### Stage 3 测试

- **复合名清洗**：`_clean_composite_name('100&110', 'C52696C')` 返回 `['C52696C-100', 'C52696C-110']`
- **拓扑对齐**：构造一个 3 节点 CAD 树和对应 BOM，断言 `_topology_align_cad_bom` 返回正确的位置匹配
- **C52696C 端到端**：上传 C52696C.STEP，断言 `assembly_nodes ≥ 40`、无 `'&'` 出现在三元组 head/tail 中
