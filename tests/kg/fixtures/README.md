# KG Harness Fixtures 说明

## sample_bom.csv（层二用，人工准备）

从真实 BOM 中截取一个子装配件（30-50 行）。

### 必须包含的列

| 列名 | 类型 | 说明 |
|------|------|------|
| part_id | str | 零件唯一编号（如 P-001） |
| part_name | str | 零件中文名称 |

### 可选列
parent_id, quantity, unit, ata_chapter 等

### 示例格式

```csv
part_id,part_name,parent_id,quantity,unit
P-010,高压压气机转子,,,
P-001,高压压气机第3级转子叶片,P-010,36,件
P-002,高压压气机第3级叶盘,P-010,1,件
P-003,叶片锁紧片,P-001,36,件
```

---

## golden_triples.json（层三用，人工标注）

人工从真实手册中标注的黄金三元组。建议 30 条，分布如下：

| 来源 | 数量 | 关系类型 |
|------|------|----------|
| 手册工序 | 15 条 | precedes / participatesIn |
| BOM 结构 | 10 条 | isPartOf / matesWith |
| 工具/规范 | 5 条 | requires / specifiedBy |

### 字段说明

| 字段 | 必填 | 说明 |
|------|------|------|
| head | 是 | 关系头实体原始文本（与手册一致） |
| relation | 是 | 必须是下列之一：precedes / participatesIn / requires / specifiedBy / matesWith / isPartOf |
| tail | 是 | 关系尾实体原始文本 |
| source_text | 否 | 来源原文片段（便于溯源） |
| source_page | 否 | 来源页码 |
| confidence | 否 | 标注置信度（0~1，默认 1.0） |

### 示例

```json
[
  {
    "head": "检查叶片榫头表面",
    "relation": "precedes",
    "tail": "插入叶片榫头至叶盘榫槽",
    "source_text": "首先检查叶片榫头表面，确认无毛刺，然后将叶片榫头对准叶盘榫槽缓慢插入",
    "source_page": 42,
    "confidence": 1.0
  },
  {
    "head": "施加预紧扭矩",
    "relation": "requires",
    "tail": "扭力扳手",
    "source_text": "用扭力扳手施加50N·m预紧扭矩",
    "source_page": 42,
    "confidence": 1.0
  }
]
```

### 标注规则

1. `head`/`tail` 保留**原始文本**（无需自行归一化，测试代码会动态处理）
2. 缩写可保留原样（如 HPC、Stage-3），归一化时会自动展开
3. 同一对实体之间若有多条相同 relation，只保留一条
4. 确实不确定的三元组将 `confidence` 设为 0.8，以便 `test_high_confidence_recall` 区分
