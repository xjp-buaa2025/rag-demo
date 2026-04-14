# BOM 层级修复设计文档

**日期**：2026-04-14  
**任务**：TASK_01_BOM_HIERARCHY — Stage1 BOM 点号层级解析修复  
**状态**：已批准，待实施

---

## 问题背景

当前 `stage1_bom_triples.json` 中 188 条三元组里有 93 条（49.5%）的 `tail == "ROOT"`，
远超验收要求的 < 40%。根因分析：

| 类别 | 数量 | 根因 |
|------|------|------|
| LLM 漏填 nomenclature 点号 | ~60 条 | Prompt 规则不够清晰，缺少 few-shot 示例 |
| 跨图 NHA 零件无法定位父节点 | ~7 条 | 后处理未识别 `SEE FIG.X FOR NHA` 标记 |
| OCR 噪声导致字段污染 | ~10 条 | `0F→OF`、`COMP0NENT` 等噪声影响 LLM 理解 |
| 互换件检测漏网 | ~16 条 | `INTRCHG` 在 nomenclature 正文中，fig_item 无 dash |

---

## 设计方案（方案二：全量修复）

### 改动范围

**唯一修改文件**：`backend/routers/kg_stages.py`

**不改动文件**：`nodes_kg.py`、`nodes_kg_unified.py`、`factory.py`、前端

---

## 数据流

```
扫描PDF → deepdoc OCR文本
           ↓
    [层1] _clean_ocr_noise(text)        ← 新函数，正则净化原始OCR文本
           ↓
    _OCR_BOM_PROMPT（强化版）           ← 修改现有Prompt，加规则+few-shot
           ↓
    LLM → JSON records
           ↓
    _bom_df_to_entities_and_triples(df_json)
      ├── [层1复用] _clean_ocr_noise(nomenclature/part_name)  ← 每行再净化一遍
      ├── 互换件检测（现有逻辑，小修：放宽 fig_item dash 条件）
      ├── 点号栈推断父节点（现有逻辑，不动）
      ├── parent_id fallback（现有逻辑，不动）
      └── [层3] _resolve_nha_triples(triples, entities)  ← 新函数，末尾修正
           ↓
    return (entities, triples)
```

---

## 三层改动细节

### 层1：`_clean_ocr_noise(text: str) -> str`

**位置**：`_parse_indent_level` 函数上方（约第28行）

**替换规则**（按顺序执行）：

```python
import re

_OCR_NOISE_RULES = [
    # 数字0误识别为字母O（仅单词边界，避免误伤小数点）
    (re.compile(r'\b0F\b'),        'OF'),
    (re.compile(r'\b0N\b'),        'ON'),
    (re.compile(r'\b0VS\b'),       'OVS'),
    (re.compile(r'\bN0\b'),        'NO'),
    (re.compile(r'COMP0NENT'),     'COMPONENT'),
    (re.compile(r'C0MPONENT'),     'COMPONENT'),
    (re.compile(r'\b0F\b'),        'OF'),   # 二次保险
]

def _clean_ocr_noise(text: str) -> str:
    for pattern, replacement in _OCR_NOISE_RULES:
        text = pattern.sub(replacement, text)
    return text
```

**调用时机**：
1. `_llm_extract_bom_from_ocr` 中，`prompt` 生成前对 `chunk` 调用
2. `_bom_df_to_entities_and_triples` 每行处理时，对 `nomenclature` 和 `part_name` 各调用一次

---

### 层2：`_OCR_BOM_PROMPT` 强化

**在【严格规则】末尾追加两条**：

```
7. 含"SEE FIG.X FOR NHA"的零件：nomenclature 填".零件名"（单点prefix，level=1），
   表示它是上层图顶层装配的直属子件；part_name 去掉"SEE FIG.X FOR NHA"后缀
8. fig_item 带 dash（-1A/-1B）且名称含 INTRCHG 的互换件：nomenclature 填与
   被替代件相同层级的点号前缀（通常是单点"."）
```

**在 `待处理的OCR文本：{content}` 之前追加 few-shot 示例**：

```
【示例输入→输出】
行: "1  3034344  COMPRESSOR ROTOR INSTALLATION  1"
→ {"part_id":"3034344","part_name":"COMPRESSOR ROTOR INSTALLATION",
    "nomenclature":"COMPRESSOR ROTOR INSTALLATION","fig_item":"1","qty":1,
    "category":"Assembly","parent_id":"","material":"","unit":"件"}

行: "2  3030349  .SEAL ASSEMBLY,AIR  1"
→ {"part_id":"3030349","part_name":"SEAL ASSEMBLY,AIR",
    "nomenclature":".SEAL ASSEMBLY,AIR","fig_item":"2","qty":1,
    "category":"Assembly","parent_id":"","material":"","unit":"件"}

行: "-1A  MS9556-07  BOLT,MACHINE,DBL HEX  INTRCHG WITH P/N MS9556-06"
→ {"part_id":"MS9556-07","part_name":"BOLT,MACHINE,DBL HEX",
    "nomenclature":".BOLT,MACHINE,DBL HEX","fig_item":"-1A","qty":1,
    "category":"Part","parent_id":"","material":"","unit":"件"}

行: "5  3102464-03  ROTOR BALANCING ASSEMBLY SEE FIG.1 FOR NHA  1"
→ {"part_id":"3102464-03","part_name":"ROTOR BALANCING ASSEMBLY",
    "nomenclature":".ROTOR BALANCING ASSEMBLY","fig_item":"5","qty":1,
    "category":"Assembly","parent_id":"","material":"","unit":"件"}
```

---

### 层3：`_resolve_nha_triples(triples, entities) -> list`

**位置**：`_bom_df_to_entities_and_triples` 的 `return` 语句之前调用

**逻辑**：

```python
_NHA_PATTERN = re.compile(r'SEE\s+FIG\.?\s*(\d+)\s+FOR\s+NHA', re.IGNORECASE)

def _resolve_nha_triples(triples: list, entities: list) -> list:
    """
    将 tail==ROOT 且 head 含 NHA 标记的三元组，重新连接到对应图的顶层 Assembly。
    fig_to_assembly 用实体列表中 level=0、category=Assembly 的第一个实体近似。
    """
    # 1. 从实体表构建 fig_num → 顶层Assembly head_label 的映射
    #    策略：entities 按 BOM 出现顺序，每遇 category=Assembly 且无点号前缀的实体
    #    即视为当前 fig 的顶层 Assembly（IPC 每图一个顶层装配体）
    fig_to_assembly: dict = {}
    fig_counter = 0
    for e in entities:
        if e.get("type") == "Assembly":
            label = f"{e['part_number']} {e['name']}" if e.get("part_number") else e["name"]
            fig_counter += 1
            fig_to_assembly[str(fig_counter)] = label
            break  # 单图BOM只有一个顶层，多图BOM此处需扩展

    # 2. 修正 NHA 三元组
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

---

## 验收标准

| 指标 | 当前值 | 目标值 |
|------|--------|--------|
| tail == ROOT 占比 | 49.5% (93/188) | < 40% |
| 层级深度 ≥ 3 的 isPartOf 链 | 0 条 | ≥ 1 条 |
| interchangesWith 关系 | 2 条 | ≥ 3 条（互换件改善） |
| OCR 噪声字段（COMP0NENT等） | 存在 | 0 条 |

---

## 风险与边界

- **多图 BOM**：`_resolve_nha_triples` 当前仅对单图 BOM 完全准确；多图场景下 fig_to_assembly 映射需扩展，留作后续 TASK
- **chunk 边界问题**：LLM 按 12000 字符切片，跨 chunk 的层级关系仍依赖 NHA 后处理，Prompt 改动不能完全消除
- **正则顺序**：OCR 噪声规则必须按定义顺序执行，防止二次误替换
