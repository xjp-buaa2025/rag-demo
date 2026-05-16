# Task 01: BOM 点号层级解析

## 问题
当前 Stage 1 BOM 解析将 175 个零件全部挂在 ROOT 下，丢失了装配层级。
实际上 IPC（Illustrated Parts Catalog）用 **点号前缀** 表示层级：
- 无点 = 顶层装配体（如 `ROTOR BALANCING ASSEMBLY`）
- `.` 一个点 = 直属子件（如 `.SEAL, AIR`）
- `..` 两个点 = 孙子件（如 `..SEAL, 0.129 - 0.131 IN.`）

此外，带 dash 的 FIG. ITEM（-1A, -1B, -1C）是同一零件的互换件/变体（INTRCHG WITH P/N）。

## 目标
修改 Stage 1 的 BOM 解析逻辑，正确提取层级关系，使 `isPartOf` 的 tail 不再全是 ROOT。

## 涉及文件
- `backend/routers/kg_stages.py` — `_bom_df_to_entities_and_triples()` 函数
- `backend/pipelines/nodes_kg_unified.py` — `bom_to_triples_node`

## 改动要点

### 1. 解析点号前缀确定层级深度
```python
def _parse_indent_level(nomenclature: str) -> tuple[int, str]:
    """从 IPC 零件名中解析点号缩进层级。
    返回 (层级深度, 清理后的名称)
    """
    level = 0
    name = nomenclature.lstrip()
    while name.startswith('.'):
        level += 1
        name = name[1:]
    return level, name.strip()
```

### 2. 用栈结构推断 parent_id
```python
# 遍历 BOM DataFrame 时维护层级栈
parent_stack = []  # [(level, part_id)]

for row in bom_rows:
    level, clean_name = _parse_indent_level(row['nomenclature'])
    
    # 弹出栈中层级 >= 当前层级的项（找到父节点）
    while parent_stack and parent_stack[-1][0] >= level:
        parent_stack.pop()
    
    parent_id = parent_stack[-1][1] if parent_stack else "ROOT"
    parent_stack.append((level, row['part_id']))
    
    # 生成 triple: row['name'] --isPartOf--> parent_name
```

### 3. 识别互换件变体
- FIG. ITEM 带 dash（-1A, -1B）且名称含 "INTRCHG WITH P/N" 的，标记为 `interchangesWith` 关系
- 这些不是新的层级节点，而是同一零件位的替代件

### 4. 三元组 head 使用 part_number + name 组合
当前用 `name` 做 head 导致同名不同号的零件合并。改为：
```python
head = f"{part_number} {name}"  # 如 "3102464-01 ROTOR BALANCING ASSEMBLY, COMPRESSOR"
```

## 验证标准
- tail 不为 ROOT 的三元组占比 > 60%
- 出现至少 3 层嵌套的 isPartOf 链（ROOT → Assembly → Part → SubPart）
- 互换件生成 interchangesWith 关系

## 预计工作量
中等（约 1-2 小时）
