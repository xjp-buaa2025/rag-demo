# Task 05: 三元组后处理（去噪 + 去重 + 本体校验）

## 问题
当前三个阶段合计约 690 条三元组中存在大量噪音：
- 低置信度三元组（confidence=0.1）约占 15%
- 同名不同号的实体导致隐性重复
- 部分关系方向违反本体定义
- 大小写不统一导致同一实体被视为不同节点

## 目标
增加统一的后处理管道，在写入 Neo4j 前清洗三元组。

## 涉及文件
- `backend/routers/kg_stages.py` — 在 Stage 4 sync 之前插入后处理
- 可新建 `backend/pipelines/kg_postprocess.py`

## 改动要点

### 1. 置信度过滤
```python
MIN_CONFIDENCE = 0.3
triples = [t for t in triples if t.get('confidence', 0) >= MIN_CONFIDENCE]
```

### 2. 实体名称归一化
```python
def _normalize_entity(name: str) -> str:
    # 1. 统一大小写（标题形式）
    name = name.strip()
    # 2. 去除多余空格
    name = re.sub(r'\s+', ' ', name)
    # 3. 统一标点（中英文逗号等）
    name = name.replace('，', ',')
    return name
```

### 3. 实体去重（同义实体合并）
```python
# 构建实体等价类
# "CENTER FIRESEAL MOUNT RING" == "Center Fireseal Mount Ring" == "center fireseal mount ring"
# 选择 BOM 中出现的形式作为规范名称（canonical name）
```

### 4. 本体约束校验
```python
ONTOLOGY_RULES = {
    'precedes':      {'head': ['Procedure'], 'tail': ['Procedure']},
    'participatesIn':{'head': ['Part', 'Assembly'], 'tail': ['Procedure']},
    'requires':      {'head': ['Procedure'], 'tail': ['Tool']},
    'specifiedBy':   {'head': ['Procedure', 'Interface', 'Part', 'Assembly'], 'tail': ['Specification']},
    'matesWith':     {'head': ['Part', 'Assembly', 'Interface'], 'tail': ['Part', 'Assembly', 'Interface']},
    'isPartOf':      {'head': ['Part', 'Assembly'], 'tail': ['Part', 'Assembly', 'ROOT']},
}

def _validate_ontology(triple):
    rule = ONTOLOGY_RULES.get(triple['relation'])
    if not rule:
        return True  # 未知关系类型暂时保留
    head_ok = triple.get('head_type', 'Unknown') in rule['head']
    tail_ok = triple.get('tail_type', 'Unknown') in rule['tail']
    return head_ok and tail_ok
```

### 5. 重复三元组去重
```python
def _dedup_triples(triples):
    seen = set()
    result = []
    for t in triples:
        key = (
            _normalize_entity(t['head']).lower(),
            t['relation'],
            _normalize_entity(t['tail']).lower()
        )
        if key not in seen:
            seen.add(key)
            result.append(t)
        else:
            # 保留置信度更高的那条
            ...
    return result
```

## 依赖
- 无硬依赖，可独立实施
- 但在 Task 01-04 完成后效果更好

## 验证标准
- 过滤后无 confidence < 0.3 的三元组
- 无大小写导致的重复实体
- 所有三元组通过本体约束校验
- 三元组总数减少约 15-25%（噪音被清除）

## 预计工作量
小（约 30-60 分钟）
