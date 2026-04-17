# Plan D — 后处理管道（P2）设计文档

**日期**：2026-04-17  
**方案**：方案 B（前端展示 + 后处理单元测试）  
**状态**：已审批，待实施

---

## 背景与目标

后处理管道（`backend/pipelines/kg_postprocess.py`）已实现四步清洗逻辑：

1. 置信度过滤（`confidence < 0.3` 丢弃）
2. 实体名称归一化（去空白、合并多余空格、中文标点→英文）
3. 本体约束校验（`precedes` 的 head/tail 必须是 Procedure）
4. 去重（同 head+relation+tail 保留最高置信度）

`kg_stages.py` 的 Stage4 和 sync-neo4j 已调用此管道，后端返回 `postprocess` 统计字段。  
**当前缺口**：前端未展示统计，无测试保护验收标准。

**Plan D 验收标准**：
- 总三元组减少 ≥ 15%（`retention_rate ≤ 0.85`）
- 无 `precedes` 本体违规关系残留

---

## 架构

```
Plan D 验收目标
├── 前端展示后处理统计（可见性）
│   ├── frontend/src/types/index.ts        ← 新增接口，扩展 ValidationReport
│   └── frontend/src/components/kg/stages/Stage4Validate.tsx  ← 新增统计卡片
└── 测试保护验收标准（可测性）
    └── tests/kg/test_postprocess.py       ← 新建，4步单测 + 验收断言
```

**后端 0 改动**。`kg_postprocess.py` 和 `kg_stages.py` 均不变。

---

## 变更详情

### 1. `frontend/src/types/index.ts`

新增两个接口：

```ts
export interface PostprocessStageStats {
  original: number
  removed_low_confidence: number
  removed_ontology_violation: number
  removed_duplicates: number
  final: number
  total_removed: number
  retention_rate: number   // 0.0~1.0
}
```

扩展 `ValidationReport`，新增可选字段：

```ts
postprocess?: Record<string, PostprocessStageStats>  // key: "bom"|"manual"|"cad"
```

### 2. `frontend/src/components/kg/stages/Stage4Validate.tsx`

在现有 F1/精确率/召回率指标下方，新增"后处理清洗统计"区块：

- 仅当 `report.postprocess` 存在时渲染（graceful degradation）
- 每阶段（bom/manual/cad）一行，展示：原始数 → 最终数、减少百分比
- 减少率 ≥ 15% 时显示绿色，否则显示黄色（提示未达标）
- 子项展示：低置信度剔除数、本体违规剔除数、去重剔除数

### 3. `tests/kg/test_postprocess.py`（新建）

**单元测试**（无 I/O，快速）：

| 测试 | 验证内容 |
|------|---------|
| `test_confidence_filter` | `confidence < 0.3` 被过滤，边界值 `0.3` 保留 |
| `test_normalize_entity` | 多余空格合并、中文标点转英文、首尾去空白 |
| `test_ontology_precedes_violation` | `precedes` head/tail 非 Procedure 时被删除 |
| `test_ontology_valid_passes` | 合规 `precedes` 三元组保留 |
| `test_dedup_keeps_highest_confidence` | 同 key 保留置信度最高的一条 |
| `test_pipeline_stats_fields` | 返回 stats 含所有必要字段 |

**验收断言**（读真实 JSON）：

| 测试 | 断言 |
|------|------|
| `test_manual_stage_retention_rate` | `retention_rate <= 0.85`（减少 ≥ 15%） |
| `test_no_precedes_ontology_violation` | 清洗后所有 `precedes` 的 head/tail 均为 Procedure |

---

## 数据流

```
Stage4 /validate 响应
  └── report.postprocess
        ├── "bom":    PostprocessStageStats
        ├── "manual": PostprocessStageStats
        └── "cad":    PostprocessStageStats
              └── Stage4Validate.tsx 渲染统计卡片
```

---

## 不在本次范围内

- OCR 修复规则迁移到后处理管道（方案 C，风险较高，留后续迭代）
- 调整置信度阈值或本体规则
- 其他阶段（Stage1/2/3）的展示改动
