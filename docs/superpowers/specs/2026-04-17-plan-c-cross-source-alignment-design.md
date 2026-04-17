# Plan C：跨源对齐增强设计规格

**日期：** 2026-04-17  
**目标：** 将手册三元组 BOM 关联率从 0% 提升至 >40%，CAD 三元组 >20%  
**状态：** 已批准，待实施

---

## 1. 背景

当前三个阶段三元组的跨源关联现状：

| 来源 | 三元组数 | bom_id 关联率 |
|------|----------|---------------|
| Stage1 BOM | 188 条 | 100%（自身） |
| Stage2 Manual | 405 条 | **0%** |
| Stage3 CAD | 待统计 | **0%** |

失败原因：
- 手册文本使用自然语言（`"COMPRESSOR ROTOR"`），BOM 使用编号+规范名（`MS9556-06 / BOLT,MACHINE,DBL HEX`），直接字符串匹配率极低
- 现有 `align_entities_multi_source` 四级对齐未针对"编号提取"做专项处理
- CAD 实体名（`C89119-001`）与 BOM 无直接字符串关联

---

## 2. 方案选型

采用**方案 Y：独立后处理模块**，理由：
- 与已规划的 `kg_postprocess.py`（TASK_05）完全对齐
- 零侵入现有 4 级对齐节点
- 函数职责单一，可独立 pytest 验证

放弃的方案：
- 方案 X（堆叠在 align 函数中）：函数将膨胀超 400 行，难以维护
- 方案 Z（新 LangGraph 节点）：补跑已有数据场景过重，架构收益不足

---

## 3. 架构总览

```
┌─────────────────────────────────────────────────────────┐
│  子模块 A：Prompt 注入（nodes_kg.py）                    │
│  _build_prompt_with_bom(base_prompt, bom_entities)      │
│  在 Stage2 抽取时动态拼接 BOM 编号速查表（≤60条）        │
└─────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────┐
│  子模块 B：后处理补全（kg_postprocess.py）               │
│  enrich_bom_links(triples, bom_entities) → result       │
│  ├─ Level 1.5: 正则零件编号提取                         │
│  ├─ Level 1.6: CAD 启发式编号映射                       │
│  └─ Level 1.7: 关键词集合匹配（Jaccard ≥ 0.35 兜底）   │
└─────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────┐
│  子模块 C：调用入口（kg_stages.py router）               │
│  Stage4 sync 前自动调用 enrich_bom_links                 │
└─────────────────────────────────────────────────────────┘
```

数据流：
```
Stage2 已有三元组（405条，bom_id=None）
    ↓  enrich_bom_links()
三元组（bom_id 已填充，rate >40%）
    ↓  write_to_neo4j()
Neo4j（Manual↔BOM 有连接）
```

---

## 4. 子模块 B 算法设计

### Level 1.5 — 正则零件编号提取

从三元组 `head`/`tail` 文本中用正则抽出编号，直接查 BOM `part_number` 索引：

```python
_PN_PATTERNS = [
    r'\b\d{7}(-\d+)?\b',        # 7位数字，如 3034344、3103074-01
    r'\bMS\d+(-\d+)?\b',         # MS规格，如 MS9556-07
    r'\b[A-Z]{2}\d+(-\d+)?\b',   # AS/AN类，如 AS3209-267、AN150568
]
```

命中即停，写入 `bom_id`。精度最高，优先运行。

### Level 1.6 — CAD 启发式编号映射

CAD 实体名形如 `C89119-001`，去掉前缀字母取数字主体，在 BOM `part_number` 中做子串匹配：

```
C89119-001 → strip leading letters → "89119-001"
           → 在 BOM part_number 中找子串 "89119"
           → 若唯一命中 → bom_id = 该 BOM id
           → 若多义（≥2条命中）→ 跳过，不猜
```

映射结果缓存为 `_cad_bom_cache: dict[str, str|None]`，避免重复计算。

### Level 1.7 — 关键词集合匹配（Jaccard 兜底）

```python
_STOPWORDS = {'THE','A','AN','OF','FOR','AND','OR','WITH','TO','IN','AT','ON'}

def _keyword_set(name: str) -> set[str]:
    tokens = set(re.findall(r'[A-Z]{2,}', name.upper()))
    return tokens - _STOPWORDS

def _jaccard(a: str, b: str) -> float:
    sa, sb = _keyword_set(a), _keyword_set(b)
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)
```

对每条三元组文本，遍历所有 BOM 名称取最高 Jaccard 分，≥ 0.35 则命中。

阈值 0.35 依据：BOM 名称含修饰词多，过高（>0.5）会漏掉"COMPRESSOR ROTOR"类命中，过低（<0.25）会产生大量误匹配。

### 返回结构

```python
{
    "triples": List[dict],   # 原三元组列表，bom_id 字段已填充
    "stats": {
        "regex_hits":    int,
        "cad_hits":      int,
        "keyword_hits":  int,
        "unmatched":     int,
        "total":         int,
    }
}
```

---

## 5. 子模块 A 设计

不修改 `_KG_EXTRACTION_PROMPT` 常量，在调用处动态拼接：

```python
def _build_prompt_with_bom(base_prompt: str, bom_entities: dict) -> str:
    """动态注入 BOM 编号速查表（≤60条）"""
    if not bom_entities:
        return base_prompt
    lines = [
        f"  {e['part_number']:<14} {e['name']}"
        for e in list(bom_entities.values())[:60]
        if e.get('part_number')
    ]
    if not lines:
        return base_prompt
    section = "\n【当前 BOM 零件编号速查表】\n以下编号出现在文本中时，请在实体 text 字段保留完整编号（格式：'名称 编号'）。\n"
    section += "\n".join(lines)
    return base_prompt + section
```

注入上限 60 条，防止 token 超限（约增加 ~800 tokens）。

---

## 6. 子模块 C 调用入口

在 `kg_stages.py` Stage4 sync 处插入：

```python
from backend.pipelines.kg_postprocess import enrich_bom_links

# 补全 bom_id
result = enrich_bom_links(stage2_triples, bom_entities)
logger.info(f"[EnrichBOM] stats={result['stats']}")
triples_to_write = result["triples"]
```

---

## 7. 涉及文件

| 文件 | 改动类型 | 说明 |
|------|----------|------|
| `backend/pipelines/kg_postprocess.py` | **新建** | 核心后处理逻辑（Level 1.5/1.6/1.7） |
| `backend/pipelines/nodes_kg.py` | **修改** | 新增 `_build_prompt_with_bom`，在 extract 节点调用 |
| `backend/routers/kg_stages.py` | **修改** | Stage4 sync 前调用 `enrich_bom_links` |
| `tests/kg/test_enrich_bom.py` | **新建** | pytest 覆盖三级逻辑 |

---

## 8. 验收标准

| 指标 | 当前 | 目标 |
|------|------|------|
| 手册三元组 `bom_id` 关联率 | 0% | **> 40%** |
| CAD 三元组 `bom_id` 关联率 | 0% | **> 20%** |
| `test_enrich_bom.py` 全部通过 | 无 | pytest green |
| Stage4 日志输出 EnrichBOM stats | 无 | 有 |

---

## 9. 不在本 Plan C 范围内

- BOM↔Manual 语义向量对齐（已有 Level 3，不重复）
- 三元组去重、本体校验（属于 TASK_05 其他子任务）
- CAD 人工映射表维护（采用启发式，无需人工）
