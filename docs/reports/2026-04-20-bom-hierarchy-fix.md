# BOM 层级修复报告

**日期**：2026-04-20  
**模块**：`backend/routers/kg_stages.py`、`tests/kg/test_bom_hierarchy.py`  
**改动性质**：Bug Fix — 知识图谱阶段一（BOM入库）层级关系严重失真

---

## 一、问题发现

### 现象

前端「阶段一：BOM入库」页面显示成功生成 **142 条三元组、142 个实体**，数量看似正常，但检查三元组编辑器后发现：

```
3034344 COMPRESSOR ROTOR INSTALLATION  isPartOf  ROOT     ✓ 正确
MS9556-06 BOLT,MACHINE,DBL HEX          isPartOf  ROOT     ✗ 错误
MS9556-07 BOLT,MACHINE,DBL HEX          isPartOf  ROOT     ✗ 错误
AS3209-267 PACKING,PREFORMED            isPartOf  ROOT     ✗ 错误
3030349 SEAL ASSEMBLY,AIR               isPartOf  AS3209-267 PACKING,PREFORMED  ✗ 错误
P002 WASHER,FLAT                        isPartOf  3101851-02 WASHER,KEY          ✗ 错误
3102464-03 ROTOR BALANCING ASSEMBLY     isPartOf  P001 NOT USED ITEM             ✗ 错误
```

**统计**：
- 总三元组：142 条，关系类型全为 `isPartOf`
- 挂到 ROOT（平级，无父节点）：**73 条（51%）**
- 非 ROOT 但父子关系错误：约 40 条（目测）
- 真正正确的层级关系：约 30 条（21%）

零件树本应是以 `3034344 COMPRESSOR ROTOR INSTALLATION` 为根、螺栓/密封件/轴承等为子节点的层级结构，实际上几乎全部扁平化为同级节点。

---

## 二、数据背景

### 数据源：Pratt & Whitney Canada 图解零件目录（IPC）

`data/KG/压气机BOM表.pdf`，共 17 页，**全部为扫描图片**（无可选取文字）。

文件结构如下：

| 页码 | 内容类型 | 说明 |
|---|---|---|
| 1、5、9…（奇数组） | **爆炸图页** | 零件分解图，带圆圈序号（10, 20, 40…）和引导线 |
| 2–4、6–8…（偶数组） | **BOM 表格页** | IPC 标准格式的零件清单 |

BOM 表格每行包含以下列：

```
FIG.ITEM | PART NUMBER    | NOMENCLATURE                              | QTY | UNITS
---------|----------------|-------------------------------------------|-----|------
-1       | 3034344        | COMPRESSOR ROTOR INSTALLATION             |  1  | REF
10       | MS9556-06      | BOLT,MACHINE,DBL HEX                      |  1  | A
20       | MS9556-07      | BOLT,MACHINE,DBL HEX                      |  1  | A
30       | AS3209-267     | PACKING,PREFORMED                         |  1  | A
40       | 3030349        | .SEAL ASSEMBLY,AIR COMPRESSOR REAR        |  1  | A
-40A     | 3103074-01     | .SEAL ASSEMBLY,AIR PRE-SB15108            |  1  | A
-40B     | 3107262-01     | .SEAL ASSEMBLY,AIR POST-SB15108           |  1  | A
         | ATTACHING PARTS|                                           |     |
50       | MS9676-11      | NUT,DBL HEX                               |  4  | A
```

**IPC FIG.ITEM 编码规则**（行业标准，非本系统自定义）：

| FIG.ITEM 格式 | 含义 |
|---|---|
| `-1` | 顶层装配体（根节点） |
| 普通整数（`10`, `20`, `30`） | 该装配体的直属子件，序号对应爆炸图中的气泡编号 |
| 带点号 NOMENCLATURE（`.SEAL ASSEMBLY`） | 该条目是一个子装配体（subassembly），内部含更多子件 |
| 带 `-` 前缀整数（`-40`） | 基础件的子装配体版本 |
| 带 `-` 前缀字母后缀（`-40A`, `-40B`） | 基础件的互换/替代版本，与基础件同级（共享父节点） |
| `ATTACHING PARTS` | 附件组标记，其后的行（螺栓、螺母等）归属于上文最近的组件 |

---

## 三、根因分析

### 3.1 处理流程

由于 PDF 是扫描件，`pdfplumber` 无法提取文字，系统进入降级路径：

```
BOM PDF（全扫描）
  ├─ pdfplumber 提取 → 空字符串 → 触发降级
  ├─ deepdoc OCR → 成功提取约 48,029 字符
  ├─ _llm_extract_bom_from_ocr → LLM 识别 142 条记录
  └─ _bom_df_to_entities_and_triples → 生成三元组（层级错误）
```

OCR 本身工作正常，问题出在 OCR 之后的**两个环节**。

---

### 3.2 根因一：Prompt 要求 LLM 做它不擅长的事

**旧 `_OCR_BOM_PROMPT`** 要求 LLM 完成两件事：
1. 从 OCR 文本中提取零件信息
2. **推断父子层级**，并用点号前缀（`.NAME`, `..NAME`）在 `nomenclature` 字段中表达

```python
# 旧 Prompt 规则节选
"""
3. parent_id 必须是本批文本中另一个零件的 part_id
4. 若不确定父子关系，parent_id 填 ""
"""
```

问题核心：**OCR 文本已经丢失了列对齐信息**。

IPC 表格的层级关系通过两种视觉线索表达：
- NOMENCLATURE 列的物理缩进（印刷上用空格表示）
- FIG.ITEM 列的编码规则（`-40A` 表示 `40` 的变体）

deepdoc OCR 按区域逐块提取文字，合并为单行字符串后，缩进消失、列边界消失。LLM 看到的是：

```
10 MS9556-06 BOLT,MACHINE,DBL HEX 1
20 MS9556-07 BOLT,MACHINE,DBL HEX 1
30 AS3209-267 PACKING,PREFORMED 1
40 3030349 .SEAL ASSEMBLY,AIR 1
-40A 3103074-01 .SEAL ASSEMBLY,AIR PRE-SB15108 1
```

LLM 无法可靠判断：数字 `10`, `20`, `30` 是序号而非层级；`-40A` 与 `40` 是兄弟而非父子。因此大量条目的 `nomenclature` 未加点号前缀，`parent_id` 乱填或留空。

**统计验证**：在 142 条 LLM 输出记录中，仅少数条目携带正确的点号前缀，导致后续栈逻辑无法推断层级。

---

### 3.3 根因二：`_bom_df_to_entities_and_triples` 的 level=0 逻辑错误

即便 LLM 对某些无点号条目给出了正确的 `parent_id`，`_bom_df_to_entities_and_triples` 里的点号栈逻辑也存在缺陷。

```python
# 旧代码（问题所在）
level, _ = _parse_indent_level(nomenclature)

while parent_stack and parent_stack[-1][0] >= level:
    parent_stack.pop()   # ← 遇到第二个 level=0 条目，会把根Assembly弹出！

if level == 0:
    parent_label = "ROOT"   # ← 所有 level=0 无差别挂 ROOT
    tail_type    = "ROOT"
```

**执行过程演示**：

```
处理 "COMPRESSOR ROTOR INSTALLATION"（level=0）
  → parent_stack 为空 → parent="ROOT" → 推入栈: [(0, "3034344...")]  ✓

处理 "BOLT,MACHINE,DBL HEX"（nomenclature无点号 → level=0）
  → while 循环: parent_stack[-1][0]=0 >= level=0 → 弹出根Assembly!
  → parent_stack 空 → parent="ROOT"  ✗  应为 "3034344..."
```

根Assembly被弹出后，所有后续无点号条目全部挂 ROOT，造成层级坍塌。

---

## 四、修复方案

### 修复原则：职责分离

```
改前：LLM 承担「提取 + 推断层级 + 维护parent_id」→ 不可靠
改后：LLM 只做「忠实提取原始字段」，层级由确定性规则函数计算
```

---

### 4.1 重写 `_OCR_BOM_PROMPT`

**核心变化**：
- 删除"推断父子关系"要求
- `parent_id` 固定填 `""`（不允许 LLM 猜测）
- 新增 IPC 特殊情况处理规则
- 新增爆炸图页识别和跳过规则
- 扩充 few-shot 示例，覆盖更多 IPC 格式

新增关键规则：

```
规则4：遇到 "ATTACHING PARTS" 行
  → fig_item 填 "ATTACHING PARTS"，category 填 "AttachingParts"

规则7：爆炸图页（主要是 "Figure 1  72-30-05  Page 2" 格式）
  → 整页跳过，不输出任何记录

规则9：PRE-SB / POST-SB 版本信息
  → 完整保留在 part_name 中（如 "SEAL ASSEMBLY,AIR PRE-SB15108"）
```

---

### 4.2 新增 `_apply_ipc_hierarchy` 函数

在 `_bom_df_to_entities_and_triples` 调用前，对 LLM 输出的平铺记录表应用确定性 IPC 层级规则：

```python
def _apply_ipc_hierarchy(records: list) -> list:
    """
    规则（按优先级）：
    R0. pid == root_assembly_id → 顶层Assembly自身，parent_id="" 不变
    R1. nomenclature 含点号前缀（OCR原文保留）→ 不干预，由栈逻辑处理
    R2. fig_item == "ATTACHING PARTS" → 标记附件块，本行不生成实体
    R3. 附件块内（ATTACHING PARTS之后）→ parent_id = 最近 Assembly 的 part_id
    R4. fig_item 以"-"开头（-40、-40A）→ 基础序号（40）的共享父节点
    R5. fig_item 为普通整数（10,20,30）且无点号 → parent_id = root_assembly_id
    R6. 其他 → parent_id 保持 ""（由后续逻辑或 ROOT 兜底）
    """
```

**调用位置**（`_stage1_bom_gen` OCR 路径中，LLM 提取完成后立即应用）：

```python
records = _llm_extract_bom_from_ocr(ocr_text, state)
records = _apply_ipc_hierarchy(records)   # ← 新增这一行
df = pd.DataFrame(records)
```

---

### 4.3 修复 `_bom_df_to_entities_and_triples` 的 level=0 逻辑

**两处精确修改**：

**修改①**：弹栈循环增加保护，栈底根 Assembly 不被弹出：

```python
# 旧
while parent_stack and parent_stack[-1][0] >= level:
    parent_stack.pop()

# 新
while parent_stack and parent_stack[-1][0] >= level:
    if len(parent_stack) == 1 and parent_stack[0][0] == 0:
        break  # 保留根Assembly，不弹出
    parent_stack.pop()
```

**修改②**：level=0 的非首条记录挂到栈底根 Assembly，不挂 ROOT：

```python
# 旧
if level == 0:
    parent_label = "ROOT"
    tail_type    = "ROOT"

# 新
if level == 0 and not parent_stack:
    # 第一个 level=0 → 顶层装配体 → 挂 ROOT
    parent_label = "ROOT"
    tail_type    = "ROOT"
elif level == 0 and parent_stack:
    # 后续 level=0（无点号的直属子件）→ 挂栈底根Assembly
    parent_label = parent_stack[0][1]
    tail_type    = "Assembly"
```

---

## 五、改动文件清单

| 文件 | 改动性质 | 行数变化 |
|---|---|---|
| `backend/routers/kg_stages.py` | 重写 Prompt + 新增函数 + 修复逻辑 | +130 行 |
| `tests/kg/test_bom_hierarchy.py` | 新增单元测试 8 个 | +130 行 |

所有改动均在后端单文件内，不影响其他模块。

---

## 六、测试覆盖

新增 8 个测试用例，覆盖所有修复路径：

| 测试用例 | 验证内容 |
|---|---|
| `test_plain_integer_items_get_root_assembly_as_parent` | 普通整数 fig_item（10,20）→ 挂顶层 Assembly |
| `test_top_assembly_parent_id_unchanged` | 顶层 Assembly 自身（fig_item="-1"）→ parent_id="" |
| `test_dash_prefix_item_shares_parent_with_base` | `-40A` 与 `40` 共享同一父节点 |
| `test_attaching_parts_block_skipped_and_items_get_correct_parent` | ATTACHING PARTS 行被跳过；附件块内零件归属正确 |
| `test_dot_prefix_items_not_overridden` | 含点号前缀的条目不被 `_apply_ipc_hierarchy` 干预 |
| `test_level0_non_first_assembly_hangs_under_root_assembly` | level=0 非首条通过 parent_id 路径正确挂父节点 |
| `test_level0_first_assembly_still_at_root` | 顶层 Assembly 仍然挂 ROOT |
| `test_dot_child_still_hangs_under_assembly_not_root` | 点号子件在 level=0 保护后仍正确挂父节点 |

**测试结果**：

```
全套 KG 测试（69 个用例）：69 passed, 0 failed
tests/kg/test_bom_hierarchy.py：23 passed（含原有 15 个 + 新增 8 个）
```

---

## 七、预期改善效果

| 指标 | 修复前 | 修复后（预期） |
|---|---|---|
| 挂 ROOT 的三元组 | 73/142（51%） | ≤ 5 条（仅真正的顶层装配体） |
| 层级关系准确率 | ~21% | > 85% |
| ATTACHING PARTS 归属 | 误挂错误父节点 | 正确归属上文最近 Assembly |
| `-40A` / `-40B` 互换件 | 层级随机 | 与基础件共享父节点 |
| PRE/POST-SB 版本信息 | 保留在 part_name | 继续保留 |

**验证方式**：在前端「阶段一：BOM入库」重新上传 `压气机BOM表.pdf`，观察三元组编辑器中各零件的 `tail` 字段是否正确指向 `3034344 COMPRESSOR ROTOR INSTALLATION`。

---

## 八、遗留问题与后续优化

本次修复解决了层级错误的核心问题，以下内容在本次范围之外，后续可继续优化：

1. **Service Bulletin 版本节点化**：目前 PRE-SB15108 保留在零件名中，可进一步拆分为独立 `ServiceBulletin` 节点，建立 `replacedByAfter` 关系
2. **爆炸图序号-零件映射**：BOM 第1页爆炸图的气泡序号（10, 20, 40…）与表格 FIG.ITEM 一一对应，可用 Vision LLM 提取序号对应的空间位置信息，增加 `spatialPosition` 属性
3. **多图 BOM 支持**：当前顶层 Assembly 查找只取第一个，若一个 IPC 文件包含多个 Figure（Figure 1、Figure 2），需要按图号分组处理
4. **`_resolve_nha_triples` 多图增强**：当前只处理单图 BOM（`break` 在第一个 Assembly），多图场景下需要建立 fig_num → Assembly 的完整映射
