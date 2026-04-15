# Stage3 CAD 多文件解析设计文档

**日期**：2026-04-15  
**任务编号**：Plan B — C52696C STEP 补全解析（P0）  
**状态**：待实施

---

## 背景与问题

`data/kg/` 目录下有两个 STEP 文件：

| 文件 | NAUO 条数 | 子零件命名 |
|------|-----------|-----------|
| C89119.STEP | 65 | 有意义（`C89119-270`、`C89119-190`…） |
| C52696C.STEP | 300 | 纯数字（`'10'`、`'120'`、`'180-blade'`…） |

现有 `POST /kg/stage3/cad` 端点只接受单文件上传，导致：
- 每次只处理一个 STEP，三元组仅 30 条（只有 C89119）
- C52696C 的 300 个 NAUO 关系从未提取
- C52696C 子零件的 `PRODUCT` 实体 name/description 均为纯数字，无语义

---

## 目标

1. 前端一次可选多个 STEP 文件上传
2. 后端逐一解析、合并三元组，一次性写入 `stage3_cad_triples.json`
3. C52696C 子零件命名修复：纯数字名加顶层装配名前缀（`C52696C-10`）

验收：三元组从 30 条增长到 **300+**，覆盖两个 STEP 文件。

---

## 设计详情

### 1. 后端 API 改造（`backend/routers/kg_stages.py`）

**改动范围**：`stage3_cad` 路由函数 + 新增 `_stage3_cad_batch_gen`

```
POST /kg/stage3/cad
  files: List[UploadFile]   ← 从单个 UploadFile 改为列表
```

新内部生成器 `_stage3_cad_batch_gen(files, state, neo4j_cfg)`：

```
all_triples = []
source_files = []
for file in files:
    写临时文件 tmp_path（同现有逻辑）
    result = parse_cad_step({"file_path": tmp_path})
    flat = _cad_data_to_flat_triples(assembly_tree, constraints, adjacency)
    all_triples.extend(flat)
    source_files.append(file.filename)
    清理 tmp_path

# BOM 对齐：一次性针对 all_triples
if bom_entities:
    _align_cad_to_bom(all_triples, bom_entities, state)

# 写 JSON
output = {
    "source_files": source_files,   ← 字段从 source_file(str) 改为 source_files(list)
    "triples": all_triples,
    "stats": {...}
}
write_stage("cad", output)
```

旧的 `_stage3_cad_gen`（单文件逻辑）**保留不改**，不影响向后兼容。

### 2. 零件命名修复（`backend/pipelines/nodes_cad.py`）

**改动函数**：`_parse_step_tree_from_text`

在现有 NAUO 循环解析完、`parent_map` 构建完成后，插入一步**前缀补全**：

```python
# 找根节点（无父节点的节点）作为前缀
all_names = set(parent_map.keys()) | set(parent_map.values())
roots = all_names - set(parent_map.keys())
top_prefix = next(iter(roots), "")

# 数字名正则：纯数字 或 数字+连字符+字母数字（如 '180-blade'）
_NUMERIC_NAME_RE = re.compile(r'^\d[\d\-a-zA-Z]*$')

# 重写 parent_map 中的数字名
if top_prefix and not _NUMERIC_NAME_RE.match(top_prefix):
    def _fix(name):
        return f"{top_prefix}-{name}" if _NUMERIC_NAME_RE.match(name) else name
    parent_map = {_fix(c): _fix(p) for c, p in parent_map.items()}
```

效果：
- `'10'` → `'C52696C-10'`
- `'180-blade'` → `'C52696C-180-blade'`
- `'C89119'`、`'C89119-270'` → 不变（不匹配数字正则）

### 3. 前端改造（`frontend/src/`）

#### 3a. `api/client.ts`

```typescript
// 原：uploadCadStep(file: File)
// 改：uploadCadStep(files: FileList | File[])
uploadCadStep(files) {
    const formData = new FormData()
    Array.from(files).forEach(f => formData.append('files', f))
    return this.post('/kg/stage3/cad', formData, { responseType: 'stream' })
}
```

#### 3b. `components/kg/stages/Stage4Validate.tsx`（或 Stage3 对应组件）

```tsx
<input
  type="file"
  accept=".step,.stp"
  multiple                    ← 新增
  onChange={handleFiles}
/>
// UI 提示：已选 {files.length} 个 STEP 文件
```

---

## 数据格式变更

`stage3_cad_triples.json` schema 变更：

```json
// 旧
{ "source_file": "tmpXXX.step", "triples": [...] }

// 新
{ "source_files": ["C52696C.STEP", "C89119.STEP"], "triples": [...] }
```

消费方（Stage4 读取 cad stage 数据的地方）需注意兼容 `source_file` 旧字段。

---

## 验收标准

| 指标 | 目标值 |
|------|--------|
| stage3 三元组总数 | ≥ 300 |
| C52696C 零件名 | `C52696C-10` 格式，无裸数字 |
| C89119 零件名 | `C89119-270` 格式，不受影响 |
| 前端文件选择 | 支持多选 STEP |

---

## 涉及文件

| 文件 | 改动类型 |
|------|---------|
| `backend/routers/kg_stages.py` | 新增 `_stage3_cad_batch_gen`，路由签名改 `files` |
| `backend/pipelines/nodes_cad.py` | `_parse_step_tree_from_text` 加前缀补全逻辑 |
| `frontend/src/api/client.ts` | `uploadCadStep` 改为接收 `FileList` |
| `frontend/src/components/kg/stages/Stage4Validate.tsx` | input 加 `multiple` |

---

## 不在范围内

- 空间邻接（adjacency）计算——需 pythonocc-core，不在本次任务范围
- Stage4 Neo4j 同步逻辑——不改
- BOM 对齐算法——不改，仅调整调用时机（改为批量后统一对齐）
