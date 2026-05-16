# Task 02: Stage 2 Manual Prompt 优化 + 后处理

## 问题
Stage 2 提取了 459 条三元组，质量在三阶段中最好，但存在：
1. 实体粒度太粗 — "Bolt"、"Nut"、"Washer" 等泛化名词，无法对应具体 BOM 零件
2. Prompt 中英文不匹配 — few-shot 示例全是中文，但维修手册是英文
3. 低质量三元组未过滤 — confidence=0.1 的噪音大量存在（"Figure 201"、"SB1445"）
4. 本体约束未校验 — specifiedBy 的 head 应是 Procedure/Interface，但出现了 Specification→Specification

## 目标
提升 Manual 三元组的精度和 BOM 对齐率。

## 涉及文件
- `backend/pipelines/nodes_kg.py` — `_KG_EXTRACTION_PROMPT`、`_KG_GLEANING_PROMPT`
- `backend/routers/kg_stages.py` — Stage 2 提取和对齐逻辑

## 改动要点

### 1. Prompt 增加英文 few-shot 示例
当前 prompt 只有中文示例（"检查叶片榫头表面..."），需要新增：
```
Input: "Remove nuts (MS9767-09), washers and bolts (MS9556-07) securing ring halves 
to brackets. Apply torque 32 to 36 lb.in to mounting nuts."

Output:
entities:
- {id: e1, type: Procedure, text: "Remove nuts, washers and bolts securing ring halves to brackets"}
- {id: e2, type: Procedure, text: "Apply torque to mounting nuts"}
- {id: e3, type: Part, text: "Nut MS9767-09"}          ← 保留完整编号
- {id: e4, type: Part, text: "Bolt MS9556-07"}          ← 保留完整编号
- {id: e5, type: Tool, text: "Torque wrench"}
- {id: e6, type: Specification, text: "32-36 lb.in"}

relations:
- {head: e1, tail: e2, type: precedes, weight: 9}
- {head: e3, tail: e1, type: participatesIn, weight: 8}
- {head: e4, tail: e1, type: participatesIn, weight: 8}
- {head: e2, tail: e5, type: requires, weight: 9}
- {head: e2, tail: e6, type: specifiedBy, weight: 10}
```

### 2. Prompt 增加实体命名规则
在 prompt 的"字段要求"部分追加：
```
【实体命名规则】
1. Part/Assembly 名称必须保留完整描述，禁止简化为 "Bolt"、"Nut" 等泛称
2. 若文本中出现零件编号（如 MS9556-07），必须附加到名称中
3. 名称格式示例：
   ✓ "Mounting bolt MS9556-07"
   ✗ "Bolt"
   ✓ "Center Fireseal Mount Ring"
   ✗ "Ring"
```

### 3. 后处理过滤规则
在三元组生成后，增加过滤/修正步骤：
```python
def _post_process_triples(triples: list[dict]) -> list[dict]:
    filtered = []
    for t in triples:
        # 1. 过滤低置信度
        if t.get('confidence', 0) < 0.3:
            continue
        # 2. 过滤过短实体名（图表编号等噪音）
        if len(t['head']) < 4 or len(t['tail']) < 4:
            continue
        # 3. 本体约束校验
        if t['relation'] == 'specifiedBy':
            if t.get('head_type') not in ('Procedure', 'Interface', 'Part', 'Assembly'):
                continue  # Specification→Specification 不合法
        if t['relation'] == 'precedes':
            if t.get('head_type') != 'Procedure' or t.get('tail_type') != 'Procedure':
                continue
        filtered.append(t)
    return filtered
```

### 4. Gleaning 轮次增加置信度衰减
第二轮 gleaning 补全的三元组，置信度应自动 ×0.8 衰减：
```python
for triple in gleaning_triples:
    triple['confidence'] = triple.get('confidence', 0.5) * 0.8
```

## 验证标准
- "Bolt"、"Nut"、"Washer" 等单词作为实体出现的次数 < 5（当前约 20+）
- confidence < 0.3 的三元组数量为 0
- 所有 specifiedBy 关系的 head_type 均为 Procedure/Interface/Part/Assembly
- 有 `bom_id` 的三元组占比从 30% 提升到 45%+

## 预计工作量
小（约 30-60 分钟）
