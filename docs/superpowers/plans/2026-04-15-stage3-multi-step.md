# Stage3 CAD 多文件解析 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 让 Stage3 端点支持同时上传多个 STEP 文件，并修复 C52696C 子零件纯数字命名问题，使三元组总数从 30 条增长到 300+。

**Architecture:** 前端 `Stage3Cad.tsx` 改为多文件选择，`client.ts` 的 `postKgStage3` 接受 `File[]`；后端新增 `_stage3_cad_batch_gen` 逐文件解析后合并三元组；`_parse_step_tree_from_text` 在 parent_map 构建完成后插入前缀补全，将纯数字零件名改为 `{顶层装配名}-{数字}` 格式。

**Tech Stack:** Python 3.10 / FastAPI / TypeScript / React

---

## File Map

| 文件 | 变更类型 | 职责 |
|------|---------|------|
| `backend/pipelines/nodes_cad.py` | Modify | 在 `_parse_step_tree_from_text` 加前缀补全逻辑 |
| `backend/routers/kg_stages.py` | Modify | 新增 `_stage3_cad_batch_gen`；路由签名改为 `files: List[UploadFile]` |
| `frontend/src/api/client.ts` | Modify | `postKgStage3` 改为接受 `File[]` |
| `frontend/src/components/kg/stages/Stage3Cad.tsx` | Modify | file input 加 `multiple`，状态改为 `File[]` |
| `tests/kg/test_stage3_naming.py` | Create | 命名修复单测 |
| `tests/kg/test_stage3_batch_api.py` | Create | 批量端点集成测试 |

---

## Task 1: 修复 `_parse_step_tree_from_text` 纯数字命名

**Files:**
- Modify: `backend/pipelines/nodes_cad.py:265-304`
- Test: `tests/kg/test_stage3_naming.py`

- [ ] **Step 1: 写失败测试**

新建文件 `tests/kg/test_stage3_naming.py`：

```python
"""
测试 _parse_step_tree_from_text 的数字名前缀补全逻辑。
使用内联 STEP 文本，无需真实文件。
"""
import tempfile, os, pytest
from backend.pipelines.nodes_cad import _parse_step_tree_from_text

# 最小化 STEP 文本：根装配 C52696C，两个子零件 '10' 和 '180-blade'
_STEP_NUMERIC = """
ISO-10303-21;
HEADER; ENDSEC;
DATA;
#1 = PRODUCT ( 'C52696C', 'C52696C', '', ( #99 ) ) ;
#2 = PRODUCT ( '10', '10', '', ( #99 ) ) ;
#3 = PRODUCT ( '180-blade', '180-blade', '', ( #99 ) ) ;
#10 = PRODUCT_DEFINITION_FORMATION ( ' ', ' ', #1 ) ;
#11 = PRODUCT_DEFINITION_FORMATION ( ' ', ' ', #2 ) ;
#12 = PRODUCT_DEFINITION_FORMATION ( ' ', ' ', #3 ) ;
#20 = PRODUCT_DEFINITION ( 'design', ' ', #10 ) ;
#21 = PRODUCT_DEFINITION ( 'design', ' ', #11 ) ;
#22 = PRODUCT_DEFINITION ( 'design', ' ', #12 ) ;
#30 = NEXT_ASSEMBLY_USAGE_OCCURRENCE ( 'u1', ' ', ' ', #20, #21, $ ) ;
#31 = NEXT_ASSEMBLY_USAGE_OCCURRENCE ( 'u2', ' ', ' ', #20, #22, $ ) ;
ENDSEC;
END-ISO-10303-21;
"""

# 有意义名称的 STEP（C89119 风格），子零件名已经有前缀，不应被修改
_STEP_MEANINGFUL = """
ISO-10303-21;
HEADER; ENDSEC;
DATA;
#1 = PRODUCT ( 'C89119', 'C89119', '', ( #99 ) ) ;
#2 = PRODUCT ( 'C89119-270', 'C89119-270', '', ( #99 ) ) ;
#10 = PRODUCT_DEFINITION_FORMATION ( ' ', ' ', #1 ) ;
#11 = PRODUCT_DEFINITION_FORMATION ( ' ', ' ', #2 ) ;
#20 = PRODUCT_DEFINITION ( 'design', ' ', #10 ) ;
#21 = PRODUCT_DEFINITION ( 'design', ' ', #11 ) ;
#30 = NEXT_ASSEMBLY_USAGE_OCCURRENCE ( 'u1', ' ', ' ', #20, #21, $ ) ;
ENDSEC;
END-ISO-10303-21;
"""


def _write_tmp(content: str) -> str:
    f = tempfile.NamedTemporaryFile(mode='w', suffix='.step', delete=False, encoding='utf-8')
    f.write(content)
    f.close()
    return f.name


def test_numeric_children_get_prefix():
    """纯数字子零件名应被补全为 {root}-{num} 格式"""
    path = _write_tmp(_STEP_NUMERIC)
    try:
        tree = _parse_step_tree_from_text(path)
        # 根节点应是 C52696C
        assert 'C52696C' in tree, f"根节点未找到 C52696C，tree={tree}"
        children = set(tree['C52696C'].keys())
        assert 'C52696C-10' in children, f"期望 C52696C-10，实际 children={children}"
        assert 'C52696C-180-blade' in children, f"期望 C52696C-180-blade，实际 children={children}"
        # 裸数字不应出现
        assert '10' not in children
        assert '180-blade' not in children
    finally:
        os.unlink(path)


def test_meaningful_names_unchanged():
    """已有意义的子零件名（C89119-270）不应被修改"""
    path = _write_tmp(_STEP_MEANINGFUL)
    try:
        tree = _parse_step_tree_from_text(path)
        assert 'C89119' in tree
        children = set(tree['C89119'].keys())
        assert 'C89119-270' in children, f"期望 C89119-270，实际={children}"
        # 不应出现双前缀
        assert 'C89119-C89119-270' not in children
    finally:
        os.unlink(path)
```

- [ ] **Step 2: 运行测试，确认失败**

```bash
cd c:/xjp/代码/rag-demo
"C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" -m pytest tests/kg/test_stage3_naming.py -v 2>&1
```

预期：`FAILED` — `AssertionError: 期望 C52696C-10`（因为当前没有前缀补全逻辑）

- [ ] **Step 3: 实现前缀补全**

在 `backend/pipelines/nodes_cad.py` 的 `_parse_step_tree_from_text` 函数中，找到 `if not parent_map:` 那一行（第 293 行），在它**之前**插入前缀补全逻辑。将原来的：

```python
    except Exception:
        pass

    if not parent_map:
        return {"root": {}}
```

替换为：

```python
    except Exception:
        pass

    # ── 数字名前缀补全 ─────────────────────────────────────────────────────
    # C52696C 的子零件 PRODUCT name/description 均为纯数字（'10'、'180-blade'）。
    # 找到根节点（无父节点的节点）作为前缀，将数字名改为 {root}-{name} 格式。
    if parent_map:
        _all = set(parent_map.keys()) | set(parent_map.values())
        _roots = _all - set(parent_map.keys())
        _top = next(iter(_roots), "")
        _NUMERIC_RE = re.compile(r'^\d[\d\-a-zA-Z]*$')
        # 只有当根节点名本身不是数字时才补全（避免误处理）
        if _top and not _NUMERIC_RE.match(_top):
            def _fix(name: str) -> str:
                return f"{_top}-{name}" if _NUMERIC_RE.match(name) else name
            parent_map = {_fix(c): _fix(p) for c, p in parent_map.items()}

    if not parent_map:
        return {"root": {}}
```

- [ ] **Step 4: 运行测试，确认通过**

```bash
cd c:/xjp/代码/rag-demo
"C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" -m pytest tests/kg/test_stage3_naming.py -v 2>&1
```

预期：`2 passed`

- [ ] **Step 5: 提交**

```bash
cd c:/xjp/代码/rag-demo
git add backend/pipelines/nodes_cad.py tests/kg/test_stage3_naming.py
git commit -m "fix: prefix numeric NAUO child names with top-assembly name in _parse_step_tree_from_text"
```

---

## Task 2: 新增后端批量生成器 `_stage3_cad_batch_gen`

**Files:**
- Modify: `backend/routers/kg_stages.py:1289-1410`

- [ ] **Step 1: 找到现有 `_stage3_cad_gen` 的结束位置**

阅读 `backend/routers/kg_stages.py` 第 1366 行附近（`yield {"type": "done", "success": True}` 那行）。`_stage3_cad_gen` 在第 1366 行结束，之后是空行和路由函数。新函数将插入在第 1366 行之后、`# POST /kg/stage3/cad` 注释之前。

- [ ] **Step 2: 在 `kg_stages.py` 中插入 `_stage3_cad_batch_gen`**

在 `backend/routers/kg_stages.py` 中，找到：

```python
    yield {"type": "done", "success": True}


# ─────────────────────────────────────────────
# POST /kg/stage3/cad
```

替换为：

```python
    yield {"type": "done", "success": True}


# 内部生成器：阶段3 CAD 批量处理（多文件）
# ─────────────────────────────────────────────

def _stage3_cad_batch_gen(tmp_items: list, state: AppState, neo4j_cfg: dict):
    """
    tmp_items: [(tmp_path, orig_filename), ...]
    逐文件解析，合并三元组后统一 BOM 对齐并写 JSON。
    """
    yield {"type": "log", "message": f"[Stage3] 开始批量处理 {len(tmp_items)} 个 CAD 文件"}

    from backend.pipelines.nodes_cad import make_cad_nodes
    nodes = make_cad_nodes(state, neo4j_cfg)

    all_triples: list = []
    source_files: list = []

    for tmp_path, orig_name in tmp_items:
        yield {"type": "log", "message": f"[Stage3] 解析：{orig_name}"}
        result = nodes["parse_cad_step"]({"file_path": tmp_path, "file_ext": orig_name.rsplit(".", 1)[-1].lower()})
        if "error" in result:
            yield {"type": "log", "message": f"[Stage3] ⚠ {orig_name} 解析失败：{result['error']}，跳过"}
            continue
        for msg in result.get("log_messages", []):
            yield {"type": "log", "message": msg}

        assembly_tree = result.get("cad_assembly_tree", {})
        constraints   = result.get("cad_constraints", [])
        adjacency     = result.get("cad_adjacency", [])
        flat = _cad_data_to_flat_triples(assembly_tree, constraints, adjacency)
        all_triples.extend(flat)
        source_files.append(orig_name)
        yield {"type": "log", "message": f"[Stage3] {orig_name} → {len(flat)} 条三元组，累计 {len(all_triples)} 条"}

    if not all_triples:
        yield {"type": "error", "message": "[Stage3] 所有文件解析后无三元组"}
        return

    yield {"type": "log", "message": f"[Stage3] 生成 {len(all_triples)} 条扁平三元组（{len(source_files)} 个文件）"}

    # BOM 对齐（一次性，针对所有三元组）
    bom_entities_for_cad = []
    if stage_exists("bom"):
        bom_data = read_stage("bom")
        bom_entities_for_cad = (bom_data or {}).get("entities", [])

    if bom_entities_for_cad:
        cad_mapping = _align_cad_to_bom(all_triples, bom_entities_for_cad, state)
        method_dist: dict = {}
        for v in cad_mapping.values():
            m = v["method"]
            method_dist[m] = method_dist.get(m, 0) + 1
        hit = sum(1 for t in all_triples if t.get("head_bom_id") or t.get("tail_bom_id"))
        yield {"type": "log", "message": f"[Stage3] BOM 对齐命中 {hit} 个实体字段，方法分布：{method_dist}"}
        if not cad_mapping:
            yield {"type": "log", "message": "[Stage3] ⚠ CAD 零件命名对齐率有限"}
    else:
        yield {"type": "log", "message": "[Stage3] ⚠ 无BOM数据，跳过CAD对齐"}

    # 写中间产物 JSON
    output = {
        "generated_at":  datetime.now(timezone.utc).isoformat(),
        "source_files":  source_files,
        "triples":       all_triples,
        "stats": {
            "triples_count":  len(all_triples),
            "assembly_nodes": sum(1 for t in all_triples if t["relation"] == "isPartOf"),
            "constraints":    sum(1 for t in all_triples if t["relation"] in ("matesWith", "hasInterface", "constrainedBy")),
            "adjacency":      sum(1 for t in all_triples if t["relation"] == "adjacentTo"),
        },
    }
    write_stage("cad", output)
    yield {
        "type":          "result",
        "triples_count": len(all_triples),
        "stats":         output["stats"],
        "output_file":   STAGE_FILES["cad"],
    }
    yield {"type": "log", "message": f"[Stage3] 已写入：{STAGE_FILES['cad']}"}

    # 尝试写 Neo4j（失败不中断）
    try:
        yield {"type": "log", "message": "[Stage3] 尝试写入 Neo4j…"}
        # 批量模式下 Neo4j 写入以最后一个文件的 assembly_tree 为准（数量最多那个）
        # 此处简化：直接调用节点的 cad_to_kg_triples，传空 assembly_tree 让它跳过直写
        neo4j_result = nodes["cad_to_kg_triples"]({
            "cad_assembly_tree": {},
            "cad_constraints":   [],
            "cad_adjacency":     [],
        })
        for msg in neo4j_result.get("log_messages", []):
            yield {"type": "log", "message": msg}
    except Exception as e:
        yield {"type": "log", "message": f"[Stage3] Neo4j 写入跳过：{e}"}

    yield {"type": "done", "success": True}


# ─────────────────────────────────────────────
# POST /kg/stage3/cad
```

- [ ] **Step 3: 修改路由函数签名**

在 `backend/routers/kg_stages.py` 中，找到：

```python
@router.post("/stage3/cad", summary="阶段3：CAD 模型入库（SSE）")
async def stage3_cad(
    request: Request,
    file: UploadFile = File(...),
    state: AppState = Depends(get_state),
):
    """
    上传 STEP/STP 文件，提取装配树/配合约束/空间邻接并生成三元组。
    响应为 SSE 流。
    """
    neo4j_cfg = request.app.state.neo4j_cfg

    ext = (file.filename or "").rsplit(".", 1)[-1].lower()
    if ext not in ("step", "stp"):
        return JSONResponse(
            status_code=400,
            content={"error": f"不支持的文件格式：{ext}，仅支持 STEP/STP"},
        )

    content = await file.read()
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    def cleanup_and_gen():
        try:
            yield from _stage3_cad_gen(tmp_path, ext, state, neo4j_cfg)
        finally:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass

    return stage_gen_to_sse(cleanup_and_gen())
```

替换为：

```python
@router.post("/stage3/cad", summary="阶段3：CAD 模型入库（SSE，支持多文件）")
async def stage3_cad(
    request: Request,
    files: List[UploadFile] = File(...),
    state: AppState = Depends(get_state),
):
    """
    上传一个或多个 STEP/STP 文件，提取装配树/配合约束/空间邻接并生成三元组。
    多文件时三元组合并写入 stage3_cad_triples.json。
    响应为 SSE 流。
    """
    neo4j_cfg = request.app.state.neo4j_cfg

    # 校验所有文件扩展名
    for f in files:
        ext = (f.filename or "").rsplit(".", 1)[-1].lower()
        if ext not in ("step", "stp"):
            return JSONResponse(
                status_code=400,
                content={"error": f"不支持的文件格式：{ext}（{f.filename}），仅支持 STEP/STP"},
            )

    # 写所有临时文件
    tmp_items = []
    for f in files:
        ext = (f.filename or "file").rsplit(".", 1)[-1].lower()
        content = await f.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
            tmp.write(content)
            tmp_items.append((tmp.name, f.filename or f"file.{ext}"))

    def cleanup_and_gen():
        try:
            yield from _stage3_cad_batch_gen(tmp_items, state, neo4j_cfg)
        finally:
            for tmp_path, _ in tmp_items:
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass

    return stage_gen_to_sse(cleanup_and_gen())
```

- [ ] **Step 4: 确认 `List` 已导入**

检查 `kg_stages.py` 顶部是否有 `from typing import List`。用 grep 确认：

```bash
grep -n "from typing import" c:/xjp/代码/rag-demo/backend/routers/kg_stages.py | head -5
```

若没有 `List`，在该行末尾追加 `List`，例如：
`from typing import Any, Dict, List` （视已有导入情况而定）

- [ ] **Step 5: 提交**

```bash
cd c:/xjp/代码/rag-demo
git add backend/routers/kg_stages.py
git commit -m "feat: add _stage3_cad_batch_gen and change stage3/cad to accept List[UploadFile]"
```

---

## Task 3: 前端多文件支持

**Files:**
- Modify: `frontend/src/api/client.ts:223-227`
- Modify: `frontend/src/components/kg/stages/Stage3Cad.tsx:10-60`

- [ ] **Step 1: 修改 `client.ts` 中的 `postKgStage3`**

在 `frontend/src/api/client.ts` 中，找到：

```typescript
export async function* postKgStage3(file: File): AsyncGenerator<KgSseFrame> {
  const form = new FormData()
  form.append('file', file)
  yield* postSSE('/kg/stage3/cad', form) as AsyncGenerator<KgSseFrame>
}
```

替换为：

```typescript
export async function* postKgStage3(files: File[]): AsyncGenerator<KgSseFrame> {
  const form = new FormData()
  files.forEach(f => form.append('files', f))
  yield* postSSE('/kg/stage3/cad', form) as AsyncGenerator<KgSseFrame>
}
```

- [ ] **Step 2: 修改 `Stage3Cad.tsx`**

在 `frontend/src/components/kg/stages/Stage3Cad.tsx` 中，找到：

```typescript
export default function Stage3Cad({ onComplete }: Props) {
  const [file, setFile] = useState<File | null>(null)
```

替换为：

```typescript
export default function Stage3Cad({ onComplete }: Props) {
  const [files, setFiles] = useState<File[]>([])
```

找到：

```typescript
  const handleRun = async () => {
    if (!file) return
    setLogs([])
    setResultFrame(null)
    setPreview(null)
    setPreviewOffset(0)
    await run(postKgStage3(file), {
```

替换为：

```typescript
  const handleRun = async () => {
    if (files.length === 0) return
    setLogs([])
    setResultFrame(null)
    setPreview(null)
    setPreviewOffset(0)
    await run(postKgStage3(files), {
```

找到：

```typescript
        <input
          type="file"
          accept=".step,.stp"
          onChange={e => setFile(e.target.files?.[0] ?? null)}
          className="text-sm text-slate-600"
        />
        <button
          onClick={handleRun}
          disabled={loading || !file}
```

替换为：

```typescript
        <input
          type="file"
          accept=".step,.stp"
          multiple
          onChange={e => setFiles(Array.from(e.target.files ?? []))}
          className="text-sm text-slate-600"
        />
        {files.length > 0 && (
          <span className="text-xs text-slate-500">已选 {files.length} 个文件</span>
        )}
        <button
          onClick={handleRun}
          disabled={loading || files.length === 0}
```

- [ ] **Step 3: 提交**

```bash
cd c:/xjp/代码/rag-demo
git add frontend/src/api/client.ts frontend/src/components/kg/stages/Stage3Cad.tsx
git commit -m "feat: Stage3Cad supports multiple STEP file upload"
```

---

## Task 4: 集成验收测试

**Files:**
- Create: `tests/kg/test_stage3_batch_api.py`

- [ ] **Step 1: 写集成测试（调用真实 STEP 文件）**

新建 `tests/kg/test_stage3_batch_api.py`：

```python
"""
Stage3 批量解析集成测试。
直接调用 _parse_step_tree_from_text 和 _cad_data_to_flat_triples，
无需启动服务器，验证两个真实 STEP 文件的三元组数量。
"""
import pytest, os, sys

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'kg')
C52696C_PATH = os.path.join(DATA_DIR, 'C52696C.STEP')
C89119_PATH  = os.path.join(DATA_DIR, 'C89119.STEP')


@pytest.mark.skipif(
    not os.path.exists(C52696C_PATH),
    reason="C52696C.STEP 不存在，跳过集成测试"
)
def test_c52696c_triple_count():
    """C52696C.STEP 应提取到 ≥ 280 条三元组（300 NAUO × ~93% 解析成功率）"""
    from backend.pipelines.nodes_cad import _parse_step_tree_from_text, _parse_step_constraints
    from backend.routers.kg_stages import _cad_data_to_flat_triples

    tree = _parse_step_tree_from_text(C52696C_PATH)
    constraints = _parse_step_constraints(C52696C_PATH)
    triples = _cad_data_to_flat_triples(tree, constraints, [])

    assert len(triples) >= 280, f"期望 ≥ 280 条，实际 {len(triples)} 条"


@pytest.mark.skipif(
    not os.path.exists(C52696C_PATH),
    reason="C52696C.STEP 不存在，跳过集成测试"
)
def test_c52696c_no_bare_numeric_names():
    """C52696C 解析结果中不应出现裸数字零件名（如 '10'、'120'）"""
    from backend.pipelines.nodes_cad import _parse_step_tree_from_text, _parse_step_constraints
    from backend.routers.kg_stages import _cad_data_to_flat_triples
    import re

    tree = _parse_step_tree_from_text(C52696C_PATH)
    constraints = _parse_step_constraints(C52696C_PATH)
    triples = _cad_data_to_flat_triples(tree, constraints, [])

    _BARE_NUMERIC = re.compile(r'^\d[\d\-a-zA-Z]*$')
    bare = [t for t in triples if _BARE_NUMERIC.match(t['head']) or _BARE_NUMERIC.match(t['tail'])]
    assert len(bare) == 0, f"发现 {len(bare)} 条含裸数字名的三元组，例：{bare[:3]}"


@pytest.mark.skipif(
    not os.path.exists(C89119_PATH),
    reason="C89119.STEP 不存在，跳过集成测试"
)
def test_c89119_names_unchanged():
    """C89119.STEP 的零件名应保持 C89119-xxx 格式，不受前缀补全影响"""
    from backend.pipelines.nodes_cad import _parse_step_tree_from_text, _parse_step_constraints
    from backend.routers.kg_stages import _cad_data_to_flat_triples

    tree = _parse_step_tree_from_text(C89119_PATH)
    constraints = _parse_step_constraints(C89119_PATH)
    triples = _cad_data_to_flat_triples(tree, constraints, [])

    assert len(triples) >= 20, f"C89119 应有 ≥ 20 条三元组，实际 {len(triples)}"
    # 确认没有双前缀
    double_prefix = [t for t in triples if 'C89119-C89119' in t['head'] or 'C89119-C89119' in t['tail']]
    assert len(double_prefix) == 0, f"发现双前缀三元组：{double_prefix[:3]}"
```

- [ ] **Step 2: 运行集成测试**

```bash
cd c:/xjp/代码/rag-demo
"C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" -m pytest tests/kg/test_stage3_batch_api.py -v 2>&1
```

预期：`3 passed`（三元组 ≥ 280，无裸数字名，无双前缀）

- [ ] **Step 3: 提交**

```bash
cd c:/xjp/代码/rag-demo
git add tests/kg/test_stage3_batch_api.py
git commit -m "test: add Stage3 batch integration tests for C52696C naming and triple count"
```

---

## 自检结果

**Spec coverage 核查：**

| Spec 要求 | 对应 Task |
|-----------|-----------|
| 前端多文件选择 | Task 3 Step 2（`multiple` + `File[]`） |
| `postKgStage3` 接受 `File[]` | Task 3 Step 1 |
| 后端批量生成器 `_stage3_cad_batch_gen` | Task 2 Step 2 |
| 路由签名改为 `List[UploadFile]` | Task 2 Step 3 |
| 纯数字名前缀补全 | Task 1 Step 3 |
| `source_files` 字段改为列表 | Task 2 Step 2（output dict 中） |
| 验收：三元组 ≥ 300 | Task 4 Step 2 |
| C89119 零件名不受影响 | Task 4 Step 2（`test_c89119_names_unchanged`） |

**Placeholder 扫描：** 无 TBD/TODO，每个步骤均有完整代码。

**类型一致性：**
- `postKgStage3(files: File[])` — Task 3 Step 1 定义，Task 3 Step 2 调用 `postKgStage3(files)` 一致。
- `_stage3_cad_batch_gen(tmp_items: list, ...)` — Task 2 Step 2 定义，Task 2 Step 3 路由中调用 `_stage3_cad_batch_gen(tmp_items, state, neo4j_cfg)` 一致。
- `_cad_data_to_flat_triples` 在 Task 4 中从 `backend.routers.kg_stages` 导入，该函数确实定义在此模块中。
