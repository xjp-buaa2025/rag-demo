# Task 04: 跨阶段实体对齐算法改进

## 问题
当前三个阶段的产出是三张孤立的图，融合率极低：
- BOM↔Manual 对齐率约 30%（139/459 条有 bom_id）
- BOM↔CAD 对齐率 0%
- 对齐方法：精确子串 + SequenceMatcher(0.75) 效果差

失败原因：
- BOM 名称 "BOLT, MACHINE, DBL HEX" vs Manual 提取 "Bolt" → 相似度远低于 0.75
- CAD 名称 "Part_283904" vs 任何东西 → 无法文本匹配

## 目标
将跨阶段融合率从 ~20% 提升到 ~60%。

## 涉及文件
- `backend/routers/kg_stages.py` — BOM 对齐逻辑
- `backend/pipelines/nodes_kg_unified.py` — `align_entities_multi_source`（4级级联对齐）

## 改动要点

### 1. 关键词集合匹配（替代整串相似度）
```python
import re

def _keyword_set(name: str) -> set[str]:
    """将零件名拆为关键词集合，忽略通用词"""
    stopwords = {'the', 'a', 'an', 'of', 'for', 'and', 'or', 'with', 'to', 'in', 'at', 'on'}
    tokens = set(re.findall(r'[a-zA-Z]{3,}', name.upper()))
    return tokens - {w.upper() for w in stopwords}

def _keyword_similarity(name_a: str, name_b: str) -> float:
    set_a = _keyword_set(name_a)
    set_b = _keyword_set(name_b)
    if not set_a or not set_b:
        return 0.0
    intersection = set_a & set_b
    # Jaccard 相似度
    return len(intersection) / len(set_a | set_b)
```

示例：
- "BOLT, MACHINE, DBL HEX" → {"BOLT", "MACHINE", "DBL", "HEX"}
- "Mounting bolt MS9556-07" → {"MOUNTING", "BOLT", "MS9556"}
- Jaccard = 1/6 = 0.17 → 低，但 "BOLT" 命中了关键词

改进：对核心名词（非修饰词）加权，BOLT 匹配比 MACHINE 匹配更重要。

### 2. 上下文感知对齐
同一个 PDF chunk 中出现的 BOM 零件编号，优先匹配该 chunk 提取的实体：
```python
def _context_aware_align(triple, chunk_text, bom_entities):
    """如果 chunk 原文中出现 BOM part_number，直接关联"""
    for bom in bom_entities:
        if bom['part_number'] in chunk_text:
            # 该 chunk 明确提到了这个 BOM 编号
            # 将 chunk 中类型相同的实体优先对齐到此 BOM
            ...
```

### 3. 航空术语同义词表扩展
当前 `AVIATION_ABBREV` 只有缩写展开，缺少同义词映射：
```python
AVIATION_SYNONYMS = {
    "bolt": ["screw", "fastener", "stud"],
    "seal": ["packing", "gasket", "o-ring"],
    "ring": ["retaining ring", "snap ring", "lock ring"],
    "housing": ["case", "casing", "enclosure"],
    "vane": ["stator blade", "guide vane", "nozzle"],
    "disk": ["disc", "wheel", "rotor disk"],
    ...
}
```
对齐时先做同义词归一化，再做关键词匹配。

### 4. Manual→BOM 反向丰富
Stage 2 提取的 `isPartOf`/`participatesIn` 关系可以补充 BOM 层级：
```python
def _enrich_bom_from_manual(bom_triples, manual_triples):
    """将 Manual 中发现的装配关系回写到 BOM 图谱"""
    for mt in manual_triples:
        if mt['relation'] in ('participatesIn', 'matesWith'):
            # 如果 head 和 tail 都能对齐到 BOM 实体
            # 且 BOM 中这两个实体之间没有关系
            # → 新增一条 isPartOf/matesWith 关系，source="Manual"
            ...
```

## 依赖
- Task 01（BOM 有层级后对齐锚点更多）
- Task 02（Manual 实体粒度改善后对齐更准确）

## 验证标准
- BOM↔Manual 对齐率 > 50%
- Stage 4 Validate 的 F1 分数有明显提升
- KgViewer 中三个来源的节点有明显的连接（而非三个孤岛）

## 预计工作量
中等（约 1.5-2 小时）
