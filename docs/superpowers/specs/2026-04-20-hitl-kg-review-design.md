# HITL KG Review — 人在回路知识图谱审阅系统设计

**日期**：2026-04-20  
**范围**：Stage 1（BOM）+ Stage 2（手册）MVP  
**方案**：后端 Gate 机制（方案一）

---

## 背景与动机

当前 KG 构建流程是顺序执行四个 Stage，最后统一检查结果。问题在于：

- 专家无法在流程中途介入纠正错误，错误会向后传播
- 无法区分「数据质量问题」还是「代码/Prompt 问题」
- 缺乏对专家的行动引导（不知道该补充什么）

目标：每个 Stage 完成后自动暂停，生成分析报告 + KG 可视化，引导专家审阅并干预，确认后才解锁下一 Stage。

---

## 核心设计

### 1. 整体流程（暂停-审阅-放行）

```
用户上传文件
  → POST /kg/stage{N}/bom|manual
  → SSE 实时日志（已有）
  → Stage 完成，后端自动：
      1. 生成 StageReport（统计分析）
      2. 写 storage/kg_stages/stage{N}_report.json
      3. SSE 推送 {"type": "stage_report_ready"}
  → 前端收到事件，展开审阅面板（锁定下一步按钮）
  → 专家查看报告 → 干预（可选）→ 点击「确认放行」
  → POST /kg/stage{N}/approve
  → 解锁下一 Stage
```

### 2. Stage 状态机

```
idle → running → awaiting_review → approved
                      ↑ (重跑后回到此状态)
```

状态持久化在 `storage/kg_stages/stage{N}_state.json`。

---

## 后端设计

### 2.1 新增接口（最小集）

| 方法 | 路径 | 功能 |
|------|------|------|
| `GET` | `/kg/stage{N}/report` | 返回 StageReport JSON |
| `POST` | `/kg/stage{N}/diagnose` | 触发 LLM 诊断，SSE 返回结论 |
| `POST` | `/kg/stage{N}/approve` | 设置状态为 approved |
| `PATCH` | `/kg/stage{N}/triples/{id}` | 编辑/删除单条三元组 |
| `POST` | `/kg/stage{N}/triples` | 手动新增三元组 |
| `POST` | `/kg/stage{N}/expert-knowledge` | 提交领域知识文本，LLM 修改实体/关系，返回 diff |
| `POST` | `/kg/stage{N}/expert-knowledge/confirm` | 确认应用 diff |

### 2.2 StageReport 数据结构

```python
@dataclass
class StageReport:
    stage: str                    # "bom" | "manual"
    generated_at: str
    
    # 基础统计
    stats: StageStats
    
    # 质量问题列表（结构化卡片）
    issues: List[StageIssue]
    
    # 与上次运行对比（可选，首次为 None）
    diff: Optional[StageDiff]

@dataclass
class StageStats:
    entities_count: int
    triples_count: int
    relation_breakdown: Dict[str, int]   # {"isPartOf": 120, "matesWith": 80, ...}
    confidence_histogram: List[float]     # [0.1, 0.3, 0.5, 0.7, 0.9] 各区间占比
    bom_coverage_ratio: float            # Stage2 专用：手册覆盖了多少 BOM 实体
    isolated_entities_count: int
    low_confidence_count: int            # confidence < 0.5

@dataclass
class StageIssue:
    severity: Literal["critical", "warning", "info"]
    title: str                           # 英文简标题
    title_zh: str                        # 中文标题
    description: str
    suggestion: str                      # 专家行动建议（LLM 生成）
    affected_triple_ids: List[str]       # 相关三元组 ID，供前端高亮

@dataclass
class StageDiff:
    added_triples: List[Triple]
    removed_triples: List[Triple]
    modified_triples: List[Tuple[Triple, Triple]]  # (before, after)
```

### 2.3 StageReport 生成逻辑

在 `backend/pipelines/kg_report.py`（新建）中实现：

```python
def generate_stage_report(stage: str, triples_path: str, prev_report_path: Optional[str]) -> StageReport:
    """Stage 完成后同步调用，生成统计报告（不含 LLM 诊断）"""
    ...

async def diagnose_stage_report(report: StageReport, llm_client) -> List[StageIssue]:
    """异步调用 LLM，为每个问题生成专家行动建议（SSE 流式返回）"""
    ...
```

**生成时机**：在 `kg_stages.py` 各 Stage 的最后，写完 JSON 后立即调用 `generate_stage_report()`，结果写入 `stage{N}_report.json`，然后 SSE 推送 `stage_report_ready`。

### 2.4 领域知识干预（方式 C）

```
POST /kg/stage{N}/expert-knowledge
  body: { "text": "压气机第一级叶片和盘是榫槽配合，不是螺栓连接" }
  
  → LLM Prompt：
    "以下是专家提供的领域知识：{text}
     请根据此知识，对以下三元组列表进行修改（增/删/改），
     返回 JSON diff 格式：{added: [...], removed: [...], modified: [...]}"
  
  → 返回 diff，前端展示变更预览

POST /kg/stage{N}/expert-knowledge/confirm
  body: { "diff": {...} }
  → 将 diff 应用到 stage{N}_bom_triples.json
```

---

## 前端设计

### 3.1 布局：嵌入式展开（Inline Expand）

在现有 `KgStagesPanel.tsx` 的每个 Stage Tab 下方，Stage 完成后自动展开审阅报告区：

```
┌─────────────────────────────────────────────┐
│  Stage 1 BOM  ✓ 完成                ▼ 审阅  │
├─────────────────────────────────────────────┤
│  [统计卡片行]  实体150  三元组287  覆盖31%↓  │
│                                             │
│  [问题清单]                                 │
│  🔴 严重 · 覆盖率过低                       │
│     → 建议提供第3章高清PDF                  │
│  🟡 警告 · 孤立实体 12 个                   │
│     → 在编辑面板中手动补充关系              │
│                                             │
│  [KG 快照]  本阶段新增图谱（D3，可点击）    │
│                                             │
│  [专家干预区]                               │
│  [编辑三元组] [输入领域知识] [调整参数]     │
│                                             │
│  [LLM 诊断] ▸ 点击生成诊断建议（SSE）      │
│                                             │
│        [✅ 确认放行 → Stage 2]              │
└─────────────────────────────────────────────┘
│  Stage 2 手册  🔒 等待放行                  │
└─────────────────────────────────────────────┘
```

### 3.2 三元组表格：中英文对照

现有分页预览表新增「中文译名」列，通过 LLM 批量翻译（按需、懒加载）：

| 实体（英文） | 中文译名 | 关系 | 中文关系 | 实体（英文） | 中文译名 | 置信度 |
|---|---|---|---|---|---|---|
| COMPRESSOR ROTOR | 压气机转子 | isPartOf | 属于 | GAS GENERATOR | 燃气发生器 | 1.0 |
| First-stage Blade | 第一级叶片 | matesWith | 配合 | Rotor Disk | 转子盘 | 0.85 |

- 翻译结果缓存在 `storage/kg_stages/translations.json`，避免重复调用
- 表格支持「显示英文」/「显示中文」/「中英对照」三种模式切换

### 3.3 新增/修改的前端文件

| 文件 | 类型 | 说明 |
|------|------|------|
| `components/kg/stages/StageReviewPanel.tsx` | 新建 | 审阅报告面板主组件 |
| `components/kg/stages/StageIssueCard.tsx` | 新建 | 单条问题卡片（严重/警告/信息） |
| `components/kg/stages/TriplesEditor.tsx` | 新建 | 三元组编辑器（增删改 + 中英对照） |
| `components/kg/stages/ExpertKnowledgeInput.tsx` | 新建 | 领域知识输入 + diff 预览 |
| `components/kg/stages/ParamTuner.tsx` | 新建 | 参数调整面板（置信度阈值等） |
| `components/kg/stages/Stage1Bom.tsx` | 修改 | 集成 StageReviewPanel，处理 stage_report_ready 事件 |
| `components/kg/stages/Stage2Manual.tsx` | 修改 | 同上 |
| `components/kg/KgViewer.tsx` | 修改 | 支持只显示指定 Stage 的三元组（KG 快照模式） |
| `api/client.ts` | 修改 | 新增5个接口的封装方法 |
| `types/index.ts` | 修改 | 新增 StageReport, StageIssue, StageDiff 类型 |

### 3.4 SSE 事件扩展

在现有 SSE 协议中新增两个事件类型：

```jsonc
// Stage 完成后推送（已有 done 之后）
{"type": "stage_report_ready", "report_path": "storage/kg_stages/stage1_report.json"}

// LLM 诊断流式输出
{"type": "diagnosis_chunk", "issue_index": 0, "suggestion": "建议..."}
{"type": "diagnosis_done"}
```

---

## 后端新建文件

| 文件 | 说明 |
|------|------|
| `backend/pipelines/kg_report.py` | StageReport 生成逻辑（统计分析） |
| `backend/pipelines/kg_diagnose.py` | LLM 诊断 Prompt + 解析 |
| `backend/pipelines/kg_translate.py` | 三元组中文翻译（LLM + 缓存） |

**修改文件**：

| 文件 | 改动 |
|------|------|
| `backend/routers/kg_stages.py` | 各 Stage 末尾调用 `generate_stage_report()`，新增5个端点 |
| `backend/kg_storage.py` | 新增 stage state / report 的读写方法 |

---

## 验证方式

1. 上传 BOM 文件 → Stage 1 完成 → 审阅面板自动展开，「确认放行」按钮可见
2. 「确认放行」前点击 Stage 2 Tab → 按钮禁用/提示"请先完成 Stage 1 审阅"
3. 点击「生成 LLM 诊断」→ SSE 流式出现问题建议文字
4. 编辑一条三元组 → 刷新页面 → 修改持久化
5. 输入领域知识 → 出现 diff 预览 → 确认 → 三元组表更新
6. 三元组表切换「中英对照」模式 → 中文译名列显示
7. 确认放行 → Stage 2 Tab 解锁，可上传手册文件

---

## 不在本次范围内

- Stage 3（CAD）、Stage 4（验证）的审阅面板
- 多专家协作 / 干预历史审计
- 溯源追踪（点击三元组跳转原文页码）— 后期迭代
- 与上次运行对比（Diff）的详细 UI — 后期迭代
