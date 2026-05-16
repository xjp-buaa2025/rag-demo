# HITL KG Review — 人在回路知识图谱审阅系统实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 Stage 1（BOM）和 Stage 2（手册）完成后自动暂停，展示分析报告 + KG 快照，引导专家通过编辑三元组、输入领域知识或调整参数进行干预，确认后才解锁下一 Stage。

**Architecture:** 后端 Gate 机制——每个 Stage 的 SSE 生成器末尾调用 `generate_stage_report()` 写报告 JSON，并推送 `stage_report_ready` 事件；前端收到事件后展开内嵌审阅面板并锁定"下一步"按钮；专家干预后调用 `POST /kg/stage{N}/approve` 解锁。状态机（`idle → running → awaiting_review → approved`）持久化为 JSON 文件。

**Tech Stack:** FastAPI + Python dataclasses（后端）；React 18 + TypeScript + Tailwind CSS v4 + D3（前端）；现有 SSE 基础设施（`stage_gen_to_sse` / `useStageSSE`）复用。

---

## 文件结构（新建 / 修改）

### 后端
| 文件 | 类型 | 职责 |
|------|------|------|
| `backend/pipelines/kg_report.py` | 新建 | 统计分析 → 生成 StageReport；与 LLM 无关，纯计算 |
| `backend/pipelines/kg_diagnose.py` | 新建 | LLM 诊断 Prompt + SSE 流式返回建议 |
| `backend/pipelines/kg_translate.py` | 新建 | 三元组中英文翻译（LLM + JSON 缓存） |
| `backend/kg_storage.py` | 修改 | 新增 state / report / translation 的读写方法 |
| `backend/routers/kg_stages.py` | 修改 | Stage 1/2 末尾调用报告生成；新增 7 个端点 |

### 前端
| 文件 | 类型 | 职责 |
|------|------|------|
| `frontend/src/types/index.ts` | 修改 | 新增 StageReport、StageIssue、StageDiff、ExpertDiff 类型 |
| `frontend/src/api/client.ts` | 修改 | 新增 7 个 API 封装方法 |
| `frontend/src/components/kg/stages/StageReviewPanel.tsx` | 新建 | 审阅面板主容器（统计卡 + 问题清单 + KG 快照 + 干预区 + 放行按钮） |
| `frontend/src/components/kg/stages/StageIssueCard.tsx` | 新建 | 单条问题卡片（严重/警告/信息，高亮相关三元组） |
| `frontend/src/components/kg/stages/TriplesEditor.tsx` | 新建 | 三元组增删改表格（含中英对照模式切换） |
| `frontend/src/components/kg/stages/ExpertKnowledgeInput.tsx` | 新建 | 领域知识输入框 + diff 预览 + 确认 |
| `frontend/src/components/kg/stages/ParamTuner.tsx` | 新建 | 置信度阈值等参数调整 + 重跑 |
| `frontend/src/components/kg/stages/Stage1Bom.tsx` | 修改 | 集成 StageReviewPanel，处理 `stage_report_ready` 事件 |
| `frontend/src/components/kg/stages/Stage2Manual.tsx` | 修改 | 同上 |
| `frontend/src/components/kg/KgViewer.tsx` | 修改 | 新增 `stageFilter` prop，只渲染指定 Stage 的节点 |

---

## Task 1：后端数据类型 + kg_storage 扩展

**Files:**
- Modify: `backend/kg_storage.py`

### 背景
`kg_storage.py` 当前只管三元组 JSON 的读写（`write_stage` / `read_stage`）。需要扩展为支持 state、report、translation 三类辅助文件，以及对应的 dataclass 定义供后续任务使用。

- [ ] **Step 1: 写测试**

新建 `tests/kg/test_kg_storage_hitl.py`：

```python
import json, os, pytest
from backend.kg_storage import (
    write_stage_state, read_stage_state,
    write_stage_report, read_stage_report,
    write_translations, read_translations,
    STAGE_STATE_FILES, STAGE_REPORT_FILES, TRANSLATIONS_FILE,
    StageState, StageReport, StageStats, StageIssue, StageDiff,
)

def test_stage_state_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr("backend.kg_storage.STORAGE_DIR", str(tmp_path))
    # 重新计算衍生路径
    import backend.kg_storage as ks
    ks.STAGE_STATE_FILES = {s: str(tmp_path / f"stage_{s}_state.json") for s in ["bom","manual"]}
    
    state = StageState(stage="bom", status="awaiting_review")
    write_stage_state("bom", state)
    loaded = read_stage_state("bom")
    assert loaded is not None
    assert loaded.status == "awaiting_review"

def test_stage_report_roundtrip(tmp_path, monkeypatch):
    import backend.kg_storage as ks
    ks.STAGE_REPORT_FILES = {s: str(tmp_path / f"stage_{s}_report.json") for s in ["bom","manual"]}
    
    report = StageReport(
        stage="bom",
        generated_at="2026-04-20T00:00:00Z",
        stats=StageStats(
            entities_count=150, triples_count=287,
            relation_breakdown={"isPartOf": 200, "matesWith": 87},
            confidence_histogram=[0.1, 0.2, 0.4, 0.2, 0.1],
            bom_coverage_ratio=None,
            isolated_entities_count=5,
            low_confidence_count=12,
        ),
        issues=[],
        diff=None,
    )
    write_stage_report("bom", report)
    loaded = read_stage_report("bom")
    assert loaded is not None
    assert loaded.stats.entities_count == 150

def test_translations_roundtrip(tmp_path, monkeypatch):
    import backend.kg_storage as ks
    ks.TRANSLATIONS_FILE = str(tmp_path / "translations.json")
    
    write_translations({"COMPRESSOR ROTOR": "压气机转子", "isPartOf": "属于"})
    loaded = read_translations()
    assert loaded["COMPRESSOR ROTOR"] == "压气机转子"
```

- [ ] **Step 2: 运行测试，确认失败**

```bash
cd "c:/xjp/代码/rag-demo"
PYTHONUTF8=1 "C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" -m pytest tests/kg/test_kg_storage_hitl.py -v 2>&1 | head -30
```

预期：ImportError（StageState 等未定义）

- [ ] **Step 3: 在 kg_storage.py 末尾追加实现**

读取当前 `backend/kg_storage.py` 末尾，然后追加以下内容（保留已有代码）：

```python
# ── HITL 扩展 ──────────────────────────────────────────────────────────────

from dataclasses import dataclass, asdict, field
from typing import Optional, List, Dict, Tuple

@dataclass
class StageState:
    stage: str
    status: str  # "idle" | "running" | "awaiting_review" | "approved"
    approved_at: Optional[str] = None

@dataclass
class StageStats:
    entities_count: int
    triples_count: int
    relation_breakdown: Dict[str, int]
    confidence_histogram: List[float]          # 5个区间 [0-0.2, 0.2-0.4, ..., 0.8-1.0] 各占比
    bom_coverage_ratio: Optional[float]        # Stage2 专用
    isolated_entities_count: int
    low_confidence_count: int                  # confidence < 0.5

@dataclass
class StageIssue:
    severity: str                              # "critical" | "warning" | "info"
    title: str
    title_zh: str
    description: str
    suggestion: str
    affected_triple_ids: List[str] = field(default_factory=list)

@dataclass
class StageDiff:
    added_triples: List[dict] = field(default_factory=list)
    removed_triples: List[dict] = field(default_factory=list)
    modified_triples: List[List[dict]] = field(default_factory=list)  # [[before, after], ...]

@dataclass
class StageReport:
    stage: str
    generated_at: str
    stats: StageStats
    issues: List[StageIssue] = field(default_factory=list)
    diff: Optional[StageDiff] = None


STAGE_STATE_FILES = {
    s: os.path.join(STORAGE_DIR, f"stage_{s}_state.json")
    for s in ["bom", "manual"]
}
STAGE_REPORT_FILES = {
    s: os.path.join(STORAGE_DIR, f"stage_{s}_report.json")
    for s in ["bom", "manual"]
}
TRANSLATIONS_FILE = os.path.join(STORAGE_DIR, "translations.json")


def _dc_to_dict(obj) -> dict:
    """dataclass → dict，递归处理嵌套"""
    return asdict(obj)


def _dict_to_stage_stats(d: dict) -> StageStats:
    return StageStats(**d)


def _dict_to_stage_issue(d: dict) -> StageIssue:
    return StageIssue(**d)


def _dict_to_stage_diff(d: Optional[dict]) -> Optional[StageDiff]:
    if d is None:
        return None
    return StageDiff(**d)


def write_stage_state(stage: str, state: StageState) -> None:
    path = STAGE_STATE_FILES[stage]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(_dc_to_dict(state), f, ensure_ascii=False, indent=2)


def read_stage_state(stage: str) -> Optional[StageState]:
    path = STAGE_STATE_FILES[stage]
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    return StageState(**d)


def write_stage_report(stage: str, report: StageReport) -> None:
    path = STAGE_REPORT_FILES[stage]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(_dc_to_dict(report), f, ensure_ascii=False, indent=2)


def read_stage_report(stage: str) -> Optional[StageReport]:
    path = STAGE_REPORT_FILES[stage]
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    stats = _dict_to_stage_stats(d["stats"])
    issues = [_dict_to_stage_issue(i) for i in d.get("issues", [])]
    diff = _dict_to_stage_diff(d.get("diff"))
    return StageReport(
        stage=d["stage"],
        generated_at=d["generated_at"],
        stats=stats,
        issues=issues,
        diff=diff,
    )


def write_translations(cache: Dict[str, str]) -> None:
    os.makedirs(os.path.dirname(TRANSLATIONS_FILE), exist_ok=True)
    with open(TRANSLATIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def read_translations() -> Dict[str, str]:
    if not os.path.exists(TRANSLATIONS_FILE):
        return {}
    with open(TRANSLATIONS_FILE, encoding="utf-8") as f:
        return json.load(f)
```

- [ ] **Step 4: 运行测试，确认通过**

```bash
cd "c:/xjp/代码/rag-demo"
PYTHONUTF8=1 "C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" -m pytest tests/kg/test_kg_storage_hitl.py -v
```

预期：3 个 PASSED

- [ ] **Step 5: 提交**

```bash
cd "c:/xjp/代码/rag-demo"
git add backend/kg_storage.py tests/kg/test_kg_storage_hitl.py
git commit -m "feat(hitl): add StageReport dataclasses and storage helpers"
```

---

## Task 2：kg_report.py — 纯统计分析（无 LLM）

**Files:**
- Create: `backend/pipelines/kg_report.py`
- Test: `tests/kg/test_kg_report.py`

### 背景
Stage 完成后同步生成 StageReport：统计实体数、三元组数、关系分布、置信度直方图、孤立实体数、低置信度数。Stage 2 额外计算对 BOM 实体的覆盖率。此模块不调用 LLM，保证即时生成。

- [ ] **Step 1: 写测试**

新建 `tests/kg/test_kg_report.py`：

```python
import pytest
from backend.pipelines.kg_report import generate_stage_report
from backend.kg_storage import StageReport

BOM_TRIPLES = {
    "entities": [
        {"id": "P1", "name": "ROTOR", "type": "Assembly"},
        {"id": "P2", "name": "BOLT", "type": "Part"},
        {"id": "P3", "name": "SEAL", "type": "Part"},
    ],
    "triples": [
        {"head": "BOLT", "relation": "isPartOf", "tail": "ROTOR", "confidence": 1.0, "source": "BOM", "head_type": "Part", "tail_type": "Assembly"},
        {"head": "SEAL", "relation": "isPartOf", "tail": "ROTOR", "confidence": 0.9, "source": "BOM", "head_type": "Part", "tail_type": "Assembly"},
        {"head": "BOLT_ALT", "relation": "interchangesWith", "tail": "BOLT", "confidence": 0.3, "source": "BOM", "head_type": "Part", "tail_type": "Part"},
    ],
    "stats": {"entities_count": 3, "triples_count": 3},
    "generated_at": "2026-04-20T00:00:00Z",
}

def test_generate_bom_report_stats():
    report = generate_stage_report("bom", BOM_TRIPLES, prev_data=None)
    assert isinstance(report, StageReport)
    assert report.stage == "bom"
    assert report.stats.entities_count == 3
    assert report.stats.triples_count == 3
    assert report.stats.relation_breakdown["isPartOf"] == 2
    assert report.stats.low_confidence_count == 1  # confidence 0.3 < 0.5

def test_isolated_entities_detected():
    # BOLT_ALT 没有连接到主图（只有 interchangesWith 到 BOLT，但 BOLT_ALT 不在 entities 里）
    # ROTOR 被两个 isPartOf 连接 → 不孤立
    # 孤立 = 在 entities 里但没有出现在任何 triple 的 head 或 tail 中
    report = generate_stage_report("bom", BOM_TRIPLES, prev_data=None)
    assert report.stats.isolated_entities_count == 0  # P1/P2/P3 都出现在三元组中

def test_confidence_histogram():
    report = generate_stage_report("bom", BOM_TRIPLES, prev_data=None)
    hist = report.stats.confidence_histogram
    assert len(hist) == 5  # 5个区间
    assert abs(sum(hist) - 1.0) < 1e-6  # 总和为1

def test_bom_coverage_for_manual():
    manual_data = {
        "triples": [
            {"head": "ROTOR", "relation": "matesWith", "tail": "BLADE", "confidence": 0.8, "source": "Manual",
             "head_type": "Assembly", "tail_type": "Part", "head_bom_id": "P1"},
        ],
        "stats": {},
        "generated_at": "2026-04-20T01:00:00Z",
    }
    report = generate_stage_report("manual", manual_data, prev_data=None, bom_data=BOM_TRIPLES)
    # 3个BOM实体，手册覆盖了1个(P1/ROTOR)
    assert report.stats.bom_coverage_ratio is not None
    assert 0 < report.stats.bom_coverage_ratio <= 1.0

def test_diff_when_prev_exists():
    prev = {**BOM_TRIPLES, "triples": BOM_TRIPLES["triples"][:2]}
    report = generate_stage_report("bom", BOM_TRIPLES, prev_data=prev)
    assert report.diff is not None
    assert len(report.diff.added_triples) == 1  # 第3条是新增的
```

- [ ] **Step 2: 运行测试，确认失败**

```bash
cd "c:/xjp/代码/rag-demo"
PYTHONUTF8=1 "C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" -m pytest tests/kg/test_kg_report.py -v 2>&1 | head -20
```

预期：ModuleNotFoundError

- [ ] **Step 3: 实现 kg_report.py**

新建 `backend/pipelines/kg_report.py`：

```python
"""
Stage 完成后的统计分析模块。不调用 LLM，同步执行。
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from backend.kg_storage import (
    StageReport, StageStats, StageIssue, StageDiff,
)


def generate_stage_report(
    stage: str,
    current_data: dict,
    prev_data: Optional[dict] = None,
    bom_data: Optional[dict] = None,
) -> StageReport:
    """
    Args:
        stage: "bom" | "manual"
        current_data: 当前 Stage 的 JSON 数据（含 triples/entities/stats）
        prev_data: 上次运行的 JSON 数据（用于生成 diff），首次为 None
        bom_data: Stage 2 时传入 Stage 1 的数据，用于计算覆盖率
    """
    triples = current_data.get("triples", [])
    entities = current_data.get("entities", [])

    stats = _compute_stats(stage, triples, entities, bom_data)
    issues = _detect_issues(stage, stats)
    diff = _compute_diff(triples, prev_data.get("triples", []) if prev_data else None)

    return StageReport(
        stage=stage,
        generated_at=datetime.now(timezone.utc).isoformat(),
        stats=stats,
        issues=issues,
        diff=diff,
    )


def _compute_stats(
    stage: str,
    triples: list,
    entities: list,
    bom_data: Optional[dict],
) -> StageStats:
    # 关系类型分布
    relation_breakdown: dict[str, int] = {}
    for t in triples:
        rel = t.get("relation", "unknown")
        relation_breakdown[rel] = relation_breakdown.get(rel, 0) + 1

    # 置信度直方图（5个区间）
    boundaries = [0.0, 0.2, 0.4, 0.6, 0.8, 1.001]
    counts = [0] * 5
    for t in triples:
        c = float(t.get("confidence", 0))
        for i in range(5):
            if boundaries[i] <= c < boundaries[i + 1]:
                counts[i] += 1
                break
    total = len(triples) or 1
    histogram = [round(c / total, 4) for c in counts]

    # 低置信度
    low_conf = sum(1 for t in triples if float(t.get("confidence", 0)) < 0.5)

    # 孤立实体（在 entities 里但未出现在任何三元组中）
    entity_ids = {e.get("id", e.get("name", "")) for e in entities}
    # 也从三元组的 head/tail 反推实体出现集
    appeared = set()
    for t in triples:
        appeared.add(t.get("head", ""))
        appeared.add(t.get("tail", ""))
    # 实体名/id 命中了任何出现集
    entity_names = {e.get("name", e.get("id", "")) for e in entities}
    isolated = entity_names - appeared if entity_names else set()
    isolated_count = len(isolated)

    # BOM 覆盖率（Stage 2 专用）
    bom_coverage = None
    if stage == "manual" and bom_data:
        bom_entity_ids = {
            e.get("id", e.get("name", ""))
            for e in bom_data.get("entities", [])
        }
        covered = set()
        for t in triples:
            if t.get("head_bom_id"):
                covered.add(t["head_bom_id"])
            if t.get("tail_bom_id"):
                covered.add(t["tail_bom_id"])
        bom_coverage = round(len(covered) / len(bom_entity_ids), 4) if bom_entity_ids else 0.0

    return StageStats(
        entities_count=len(entities),
        triples_count=len(triples),
        relation_breakdown=relation_breakdown,
        confidence_histogram=histogram,
        bom_coverage_ratio=bom_coverage,
        isolated_entities_count=isolated_count,
        low_confidence_count=low_conf,
    )


def _detect_issues(stage: str, stats: StageStats) -> list[StageIssue]:
    issues: list[StageIssue] = []

    # 规则1：低置信度三元组占比超过 30%
    low_ratio = stats.low_confidence_count / (stats.triples_count or 1)
    if low_ratio > 0.3:
        issues.append(StageIssue(
            severity="critical",
            title="High low-confidence triple ratio",
            title_zh="低置信度三元组占比过高",
            description=f"{stats.low_confidence_count} / {stats.triples_count} 条三元组置信度 < 0.5（占比 {low_ratio:.0%}）",
            suggestion="建议调低置信度阈值或检查 LLM Prompt 质量；也可在编辑面板手动修正",
        ))

    # 规则2：孤立实体超过 10%
    isolated_ratio = stats.isolated_entities_count / (stats.entities_count or 1)
    if isolated_ratio > 0.1:
        issues.append(StageIssue(
            severity="warning",
            title="Isolated entities detected",
            title_zh="存在孤立实体",
            description=f"{stats.isolated_entities_count} 个实体没有与任何其他实体建立关系（占比 {isolated_ratio:.0%}）",
            suggestion="在编辑面板为孤立实体手动补充关系，或确认是否为数据噪声",
        ))

    # 规则3：Stage 2 BOM 覆盖率过低
    if stage == "manual" and stats.bom_coverage_ratio is not None:
        if stats.bom_coverage_ratio < 0.4:
            issues.append(StageIssue(
                severity="critical",
                title="Low BOM coverage in manual stage",
                title_zh="手册对 BOM 覆盖率过低",
                description=f"手册三元组仅覆盖了 {stats.bom_coverage_ratio:.0%} 的 BOM 实体（预期 > 40%）",
                suggestion="建议提供更完整的手册章节，或通过「输入领域知识」补充关键零件的装配关系",
            ))

    # 规则4：三元组总数过少
    min_triples = {"bom": 10, "manual": 20}.get(stage, 10)
    if stats.triples_count < min_triples:
        issues.append(StageIssue(
            severity="critical",
            title="Too few triples extracted",
            title_zh="提取三元组数量过少",
            description=f"仅提取到 {stats.triples_count} 条三元组（{stage} 阶段预期至少 {min_triples} 条）",
            suggestion="检查输入文件质量；若为扫描件，建议提供更清晰版本或文字版 PDF",
        ))

    return issues


def _compute_diff(
    current_triples: list,
    prev_triples: Optional[list],
) -> Optional[StageDiff]:
    if prev_triples is None:
        return None

    def triple_key(t: dict) -> str:
        return f"{t.get('head','')}__{t.get('relation','')}__{t.get('tail','')}"

    prev_keys = {triple_key(t): t for t in prev_triples}
    curr_keys = {triple_key(t): t for t in current_triples}

    added = [curr_keys[k] for k in curr_keys if k not in prev_keys]
    removed = [prev_keys[k] for k in prev_keys if k not in curr_keys]

    return StageDiff(added_triples=added, removed_triples=removed, modified_triples=[])
```

- [ ] **Step 4: 运行测试**

```bash
cd "c:/xjp/代码/rag-demo"
PYTHONUTF8=1 "C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" -m pytest tests/kg/test_kg_report.py -v
```

预期：5 个 PASSED

- [ ] **Step 5: 提交**

```bash
cd "c:/xjp/代码/rag-demo"
git add backend/pipelines/kg_report.py tests/kg/test_kg_report.py
git commit -m "feat(hitl): add generate_stage_report with pure stats analysis"
```

---

## Task 3：kg_diagnose.py — LLM 诊断（SSE 流式）

**Files:**
- Create: `backend/pipelines/kg_diagnose.py`
- Test: `tests/kg/test_kg_diagnose.py`

### 背景
专家点击「生成 LLM 诊断」时，后端调用 LLM 为每个 StageIssue 生成更具体的专家行动建议，以 SSE 流式返回。LLM 调用参考项目已有的 `nodes_kg.py` 中的客户端创建方式。

- [ ] **Step 1: 写测试（mock LLM）**

新建 `tests/kg/test_kg_diagnose.py`：

```python
import asyncio, pytest
from unittest.mock import AsyncMock, patch, MagicMock
from backend.pipelines.kg_diagnose import diagnose_issues_stream
from backend.kg_storage import StageIssue, StageReport, StageStats

SAMPLE_REPORT = StageReport(
    stage="bom",
    generated_at="2026-04-20T00:00:00Z",
    stats=StageStats(
        entities_count=10, triples_count=5,
        relation_breakdown={}, confidence_histogram=[0,0,0.2,0.6,0.2],
        bom_coverage_ratio=None, isolated_entities_count=0, low_confidence_count=2,
    ),
    issues=[
        StageIssue(
            severity="warning",
            title="Low confidence triples",
            title_zh="低置信度三元组",
            description="2 triples < 0.5",
            suggestion="",
        )
    ],
)

@pytest.mark.asyncio
async def test_diagnose_yields_chunks():
    async def fake_stream(*args, **kwargs):
        for chunk in ["建议", "检查", "Prompt"]:
            mock = MagicMock()
            mock.choices[0].delta.content = chunk
            yield mock

    with patch("backend.pipelines.kg_diagnose._create_llm_client") as mock_client:
        instance = MagicMock()
        instance.chat.completions.create = MagicMock(return_value=fake_stream())
        mock_client.return_value = instance

        frames = []
        async for frame in diagnose_issues_stream(SAMPLE_REPORT):
            frames.append(frame)

    types = [f["type"] for f in frames]
    assert "diagnosis_chunk" in types
    assert frames[-1]["type"] == "diagnosis_done"
```

- [ ] **Step 2: 运行测试，确认失败**

```bash
cd "c:/xjp/代码/rag-demo"
PYTHONUTF8=1 "C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" -m pytest tests/kg/test_kg_diagnose.py -v 2>&1 | head -20
```

- [ ] **Step 3: 实现 kg_diagnose.py**

先查看 `backend/pipelines/nodes_kg.py` 前 30 行，了解 LLM 客户端创建方式，然后新建：

```python
"""
LLM 诊断模块：为每个 StageIssue 生成专家行动建议，SSE 流式 yield。
"""
from __future__ import annotations

import os
from typing import AsyncGenerator

from backend.kg_storage import StageReport, StageIssue


def _create_llm_client():
    """复用项目 LLM 配置（OpenAI 兼容 API）"""
    from openai import OpenAI
    return OpenAI(
        api_key=os.environ.get("LLM_API_KEY", ""),
        base_url=os.environ.get("LLM_BASE_URL", ""),
    )


_DIAGNOSIS_PROMPT = """你是一位知识图谱质量专家，正在帮助领域专家理解知识图谱构建过程中出现的问题。

以下是某个阶段（{stage}）的分析报告摘要：
- 实体总数：{entities_count}
- 三元组总数：{triples_count}  
- 低置信度三元组（<0.5）：{low_conf_count}
- 孤立实体：{isolated_count}
{coverage_line}

其中检测到的问题是：
【{severity}】{title_zh}
详情：{description}

请用2-3句简洁的中文，向领域专家解释：
1. 这个问题最可能的根本原因是什么（数据质量？Prompt 设计？还是领域知识缺失？）
2. 专家最应该优先做什么（提供更好的数据？直接编辑三元组？还是补充领域知识？）

回答要直接、具体，不要泛泛而谈。"""


async def diagnose_issues_stream(
    report: StageReport,
) -> AsyncGenerator[dict, None]:
    """
    为 report 中的每个 issue 调用 LLM 生成详细建议。
    yield dict：
      {"type": "diagnosis_chunk", "issue_index": int, "content": str}
      {"type": "diagnosis_done"}
    """
    client = _create_llm_client()
    stats = report.stats
    coverage_line = (
        f"- BOM 覆盖率：{stats.bom_coverage_ratio:.0%}"
        if stats.bom_coverage_ratio is not None
        else ""
    )

    for i, issue in enumerate(report.issues):
        prompt = _DIAGNOSIS_PROMPT.format(
            stage=report.stage,
            entities_count=stats.entities_count,
            triples_count=stats.triples_count,
            low_conf_count=stats.low_confidence_count,
            isolated_count=stats.isolated_entities_count,
            coverage_line=coverage_line,
            severity=issue.severity,
            title_zh=issue.title_zh,
            description=issue.description,
        )

        stream = client.chat.completions.create(
            model=os.environ.get("LLM_MODEL", ""),
            messages=[{"role": "user", "content": prompt}],
            stream=True,
            max_tokens=200,
            temperature=0.3,
        )

        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                yield {"type": "diagnosis_chunk", "issue_index": i, "content": content}

    yield {"type": "diagnosis_done"}
```

- [ ] **Step 4: 运行测试**

```bash
cd "c:/xjp/代码/rag-demo"
PYTHONUTF8=1 "C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" -m pytest tests/kg/test_kg_diagnose.py -v
```

预期：1 个 PASSED

- [ ] **Step 5: 提交**

```bash
cd "c:/xjp/代码/rag-demo"
git add backend/pipelines/kg_diagnose.py tests/kg/test_kg_diagnose.py
git commit -m "feat(hitl): add LLM diagnosis streaming module"
```

---

## Task 4：kg_translate.py — 中英文翻译缓存

**Files:**
- Create: `backend/pipelines/kg_translate.py`
- Test: `tests/kg/test_kg_translate.py`

### 背景
三元组的 head/tail/relation 都是英文，需要翻译为中文供专家阅读。翻译结果缓存在 `storage/kg_stages/translations.json`，相同词汇不重复调用 LLM。

- [ ] **Step 1: 写测试**

新建 `tests/kg/test_kg_translate.py`：

```python
import pytest
from unittest.mock import patch, MagicMock
from backend.pipelines.kg_translate import translate_terms, translate_triples_batch

def make_mock_client(response_text: str):
    client = MagicMock()
    choice = MagicMock()
    choice.message.content = response_text
    client.chat.completions.create.return_value = MagicMock(choices=[choice])
    return client

def test_translate_uses_cache(tmp_path, monkeypatch):
    import backend.kg_storage as ks
    ks.TRANSLATIONS_FILE = str(tmp_path / "translations.json")
    ks.write_translations({"ROTOR": "转子", "isPartOf": "属于"})

    with patch("backend.pipelines.kg_translate._create_llm_client") as mock_c:
        result = translate_terms(["ROTOR", "isPartOf"])
        mock_c.assert_not_called()  # 全部命中缓存，不调用 LLM

    assert result["ROTOR"] == "转子"
    assert result["isPartOf"] == "属于"

def test_translate_calls_llm_for_new_terms(tmp_path, monkeypatch):
    import backend.kg_storage as ks
    ks.TRANSLATIONS_FILE = str(tmp_path / "translations.json")

    llm_response = '{"COMPRESSOR": "压气机", "matesWith": "配合"}'
    with patch("backend.pipelines.kg_translate._create_llm_client") as mock_c:
        mock_c.return_value = make_mock_client(llm_response)
        result = translate_terms(["COMPRESSOR", "matesWith"])

    assert result["COMPRESSOR"] == "压气机"

def test_translate_triples_batch(tmp_path, monkeypatch):
    import backend.kg_storage as ks
    ks.TRANSLATIONS_FILE = str(tmp_path / "translations.json")
    ks.write_translations({"ROTOR": "转子", "isPartOf": "属于", "BOLT": "螺栓"})

    triples = [
        {"head": "BOLT", "relation": "isPartOf", "tail": "ROTOR", "confidence": 1.0}
    ]
    result = translate_triples_batch(triples)
    assert result[0]["head_zh"] == "螺栓"
    assert result[0]["relation_zh"] == "属于"
    assert result[0]["tail_zh"] == "转子"
```

- [ ] **Step 2: 运行测试，确认失败**

```bash
cd "c:/xjp/代码/rag-demo"
PYTHONUTF8=1 "C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" -m pytest tests/kg/test_kg_translate.py -v 2>&1 | head -20
```

- [ ] **Step 3: 实现 kg_translate.py**

新建 `backend/pipelines/kg_translate.py`：

```python
"""
三元组中英文翻译模块。翻译结果缓存到 translations.json，避免重复调用 LLM。
"""
from __future__ import annotations

import json
import os
from typing import Dict, List

from backend.kg_storage import read_translations, write_translations

# 关系类型固定译名（无需 LLM）
_RELATION_MAP: Dict[str, str] = {
    "isPartOf": "属于",
    "matesWith": "配合",
    "precedes": "先于",
    "participatesIn": "参与",
    "requires": "需要",
    "specifiedBy": "规定于",
    "hasInterface": "具有接口",
    "interchangesWith": "可互换",
    "hasComponent": "包含",
    "hasConstraint": "有约束",
    "isAdjacentTo": "相邻",
}


def _create_llm_client():
    from openai import OpenAI
    return OpenAI(
        api_key=os.environ.get("LLM_API_KEY", ""),
        base_url=os.environ.get("LLM_BASE_URL", ""),
    )


_TRANSLATE_PROMPT = """请将以下航空发动机领域的英文术语翻译为中文。
返回严格的 JSON 对象，key 为英文原文，value 为中文译名。
不要添加任何解释。

术语列表：
{terms}"""


def translate_terms(terms: List[str]) -> Dict[str, str]:
    """
    翻译一批术语。优先从缓存读取，未命中的批量调用 LLM。
    """
    cache = read_translations()

    # 先用固定映射填充
    for t in terms:
        if t in _RELATION_MAP and t not in cache:
            cache[t] = _RELATION_MAP[t]

    missing = [t for t in terms if t not in cache]
    if not missing:
        return {t: cache[t] for t in terms}

    # 调用 LLM 翻译缺失部分
    client = _create_llm_client()
    prompt = _TRANSLATE_PROMPT.format(terms="\n".join(f"- {t}" for t in missing))
    resp = client.chat.completions.create(
        model=os.environ.get("LLM_MODEL", ""),
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0,
    )
    raw = resp.choices[0].message.content.strip()

    # 解析 JSON（容错：去掉 markdown 代码块）
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    try:
        new_translations = json.loads(raw)
        cache.update(new_translations)
        write_translations(cache)
    except json.JSONDecodeError:
        pass  # 解析失败时保持原英文，不中断流程

    return {t: cache.get(t, t) for t in terms}


def translate_triples_batch(triples: List[dict]) -> List[dict]:
    """
    为三元组列表增加 head_zh / relation_zh / tail_zh 字段。
    修改原始 dict（返回同一列表，方便链式调用）。
    """
    all_terms: List[str] = []
    for t in triples:
        all_terms.extend([t.get("head", ""), t.get("relation", ""), t.get("tail", "")])
    unique_terms = list(set(filter(None, all_terms)))
    translations = translate_terms(unique_terms)

    for t in triples:
        t["head_zh"] = translations.get(t.get("head", ""), t.get("head", ""))
        t["relation_zh"] = translations.get(t.get("relation", ""), t.get("relation", ""))
        t["tail_zh"] = translations.get(t.get("tail", ""), t.get("tail", ""))

    return triples
```

- [ ] **Step 4: 运行测试**

```bash
cd "c:/xjp/代码/rag-demo"
PYTHONUTF8=1 "C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" -m pytest tests/kg/test_kg_translate.py -v
```

预期：3 个 PASSED

- [ ] **Step 5: 提交**

```bash
cd "c:/xjp/代码/rag-demo"
git add backend/pipelines/kg_translate.py tests/kg/test_kg_translate.py
git commit -m "feat(hitl): add bilingual translation module with JSON cache"
```

---

## Task 5：kg_stages.py — 集成报告生成 + 新增 7 个端点

**Files:**
- Modify: `backend/routers/kg_stages.py`
- Test: `tests/kg/test_hitl_endpoints.py`

### 背景
在 Stage 1/2 的 SSE 生成器末尾（`yield done` 之前）插入报告生成逻辑并推送 `stage_report_ready` 事件；新增 7 个 HITL 端点：`/report`、`/diagnose`、`/approve`、`/triples`（GET/POST/PATCH/DELETE）、`/expert-knowledge`、`/expert-knowledge/confirm`。

- [ ] **Step 1: 写端点测试**

新建 `tests/kg/test_hitl_endpoints.py`：

```python
import json, pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# 假设 main.py 导出 app
from backend.main import app

client = TestClient(app)

def _write_bom_fixture(tmp_path):
    """写一个最小 BOM triples JSON 供测试用"""
    import backend.kg_storage as ks
    data = {
        "entities": [{"id": "P1", "name": "ROTOR", "type": "Assembly"}],
        "triples": [{"head": "BOLT", "relation": "isPartOf", "tail": "ROTOR",
                     "confidence": 1.0, "source": "BOM", "head_type": "Part", "tail_type": "Assembly"}],
        "stats": {"entities_count": 1, "triples_count": 1},
        "generated_at": "2026-04-20T00:00:00Z",
    }
    ks.write_stage("bom", data)
    return data

def test_get_report_returns_200(tmp_path, monkeypatch):
    import backend.kg_storage as ks
    monkeypatch.setattr(ks, "STORAGE_DIR", str(tmp_path))
    ks.STAGE_FILES = {s: str(tmp_path / f"stage_{s}_triples.json") for s in ["bom","manual","cad"]}
    ks.STAGE_REPORT_FILES = {s: str(tmp_path / f"stage_{s}_report.json") for s in ["bom","manual"]}
    _write_bom_fixture(tmp_path)

    resp = client.get("/kg/stage1/report")
    assert resp.status_code == 200
    body = resp.json()
    assert "stats" in body
    assert "issues" in body

def test_approve_sets_state(tmp_path, monkeypatch):
    import backend.kg_storage as ks
    monkeypatch.setattr(ks, "STORAGE_DIR", str(tmp_path))
    ks.STAGE_STATE_FILES = {s: str(tmp_path / f"stage_{s}_state.json") for s in ["bom","manual"]}
    ks.STAGE_FILES = {s: str(tmp_path / f"stage_{s}_triples.json") for s in ["bom","manual","cad"]}
    _write_bom_fixture(tmp_path)

    resp = client.post("/kg/stage1/approve")
    assert resp.status_code == 200
    state = ks.read_stage_state("bom")
    assert state is not None
    assert state.status == "approved"

def test_patch_triple_modifies_json(tmp_path, monkeypatch):
    import backend.kg_storage as ks
    monkeypatch.setattr(ks, "STORAGE_DIR", str(tmp_path))
    ks.STAGE_FILES = {s: str(tmp_path / f"stage_{s}_triples.json") for s in ["bom","manual","cad"]}
    _write_bom_fixture(tmp_path)

    resp = client.patch("/kg/stage1/triples/0", json={
        "head": "BOLT_UPDATED", "relation": "isPartOf", "tail": "ROTOR", "confidence": 1.0
    })
    assert resp.status_code == 200
    updated = ks.read_stage("bom")
    assert updated["triples"][0]["head"] == "BOLT_UPDATED"

def test_post_triple_appends(tmp_path, monkeypatch):
    import backend.kg_storage as ks
    monkeypatch.setattr(ks, "STORAGE_DIR", str(tmp_path))
    ks.STAGE_FILES = {s: str(tmp_path / f"stage_{s}_triples.json") for s in ["bom","manual","cad"]}
    _write_bom_fixture(tmp_path)

    resp = client.post("/kg/stage1/triples", json={
        "head": "SEAL", "relation": "isPartOf", "tail": "ROTOR",
        "confidence": 1.0, "source": "expert", "head_type": "Part", "tail_type": "Assembly"
    })
    assert resp.status_code == 200
    updated = ks.read_stage("bom")
    assert len(updated["triples"]) == 2
```

- [ ] **Step 2: 运行测试，确认失败**

```bash
cd "c:/xjp/代码/rag-demo"
PYTHONUTF8=1 "C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" -m pytest tests/kg/test_hitl_endpoints.py -v 2>&1 | head -30
```

- [ ] **Step 3: 在 kg_stages.py 的 Stage 1 末尾插入报告生成**

在 `_stage1_bom_gen()` 生成器中，找到 `yield {"type": "result", ...}` 之前，插入：

```python
        # ── HITL: 生成 StageReport ───────────────────────────────────────
        try:
            from backend.pipelines.kg_report import generate_stage_report
            from backend.kg_storage import (
                write_stage_report, write_stage_state, StageState,
                read_stage, STAGE_REPORT_FILES,
            )
            current_data = read_stage("bom") or {}
            prev_data = None  # 首次运行无历史
            if os.path.exists(STAGE_REPORT_FILES.get("bom", "")):
                prev_stage = read_stage("bom")  # 已被覆盖，简化处理
            report = generate_stage_report("bom", current_data, prev_data=None)
            write_stage_report("bom", report)
            write_stage_state("bom", StageState(stage="bom", status="awaiting_review"))
            yield {"type": "stage_report_ready", "stage": "bom", "issues_count": len(report.issues)}
        except Exception as e:
            yield {"type": "log", "message": f"[Report] 报告生成失败（不影响主流程）: {e}"}
        # ────────────────────────────────────────────────────────────────
```

对 `_stage2_manual_gen()` 做相同处理（stage 参数改为 `"manual"`，并传入 `bom_data=read_stage("bom")`）。

- [ ] **Step 4: 在 kg_stages.py 末尾新增 7 个端点**

```python
# ══════════════════════════════════════════════════════
# HITL 端点
# ══════════════════════════════════════════════════════

from fastapi import Body
from backend.pipelines.kg_report import generate_stage_report
from backend.kg_storage import (
    read_stage_report, write_stage_report,
    read_stage_state, write_stage_state, StageState,
    read_stage, write_stage,
)

_STAGE_SLUG = {"1": "bom", "2": "manual"}


def _resolve_stage(n: str) -> str:
    """'1' → 'bom', '2' → 'manual'"""
    s = _STAGE_SLUG.get(n)
    if not s:
        from fastapi import HTTPException
        raise HTTPException(404, f"Stage {n} not supported for HITL")
    return s


@router.get("/stage{n}/report")
async def get_stage_report(n: str):
    """返回最新 StageReport，若无则实时生成"""
    stage = _resolve_stage(n)
    report = read_stage_report(stage)
    if report is None:
        data = read_stage(stage)
        if data is None:
            from fastapi import HTTPException
            raise HTTPException(404, "Stage data not found. Run the stage first.")
        bom_data = read_stage("bom") if stage == "manual" else None
        report = generate_stage_report(stage, data, prev_data=None, bom_data=bom_data)
        write_stage_report(stage, report)
    from dataclasses import asdict
    return asdict(report)


@router.post("/stage{n}/approve")
async def approve_stage(n: str):
    """专家确认放行，设置状态为 approved"""
    stage = _resolve_stage(n)
    from datetime import datetime, timezone
    state = StageState(
        stage=stage,
        status="approved",
        approved_at=datetime.now(timezone.utc).isoformat(),
    )
    write_stage_state(stage, state)
    return {"ok": True, "stage": stage, "status": "approved"}


@router.get("/stage{n}/state")
async def get_stage_state(n: str):
    """返回 Stage 状态（idle/running/awaiting_review/approved）"""
    stage = _resolve_stage(n)
    state = read_stage_state(stage)
    if state is None:
        return {"stage": stage, "status": "idle"}
    from dataclasses import asdict
    return asdict(state)


@router.get("/stage{n}/triples")
async def list_triples(n: str, offset: int = 0, limit: int = 50):
    """分页返回三元组（含 head_zh/relation_zh/tail_zh）"""
    stage = _resolve_stage(n)
    data = read_stage(stage)
    if data is None:
        from fastapi import HTTPException
        raise HTTPException(404, "Stage data not found")
    triples = data.get("triples", [])
    page = triples[offset: offset + limit]
    # 懒翻译：仅翻译当前页
    try:
        from backend.pipelines.kg_translate import translate_triples_batch
        page = translate_triples_batch([dict(t) for t in page])
    except Exception:
        pass
    return {"total": len(triples), "offset": offset, "limit": limit, "triples": page}


@router.patch("/stage{n}/triples/{idx}")
async def update_triple(n: str, idx: int, triple: dict = Body(...)):
    """编辑指定索引的三元组"""
    stage = _resolve_stage(n)
    data = read_stage(stage)
    if data is None or idx >= len(data.get("triples", [])):
        from fastapi import HTTPException
        raise HTTPException(404, "Triple not found")
    data["triples"][idx] = triple
    write_stage(stage, data)
    return {"ok": True, "updated": triple}


@router.delete("/stage{n}/triples/{idx}")
async def delete_triple(n: str, idx: int):
    """删除指定索引的三元组"""
    stage = _resolve_stage(n)
    data = read_stage(stage)
    if data is None or idx >= len(data.get("triples", [])):
        from fastapi import HTTPException
        raise HTTPException(404, "Triple not found")
    removed = data["triples"].pop(idx)
    write_stage(stage, data)
    return {"ok": True, "removed": removed}


@router.post("/stage{n}/triples")
async def add_triple(n: str, triple: dict = Body(...)):
    """手动新增一条三元组"""
    stage = _resolve_stage(n)
    data = read_stage(stage)
    if data is None:
        from fastapi import HTTPException
        raise HTTPException(404, "Stage data not found")
    triple.setdefault("source", "expert")
    triple.setdefault("confidence", 1.0)
    data.setdefault("triples", []).append(triple)
    write_stage(stage, data)
    return {"ok": True, "added": triple, "total": len(data["triples"])}


@router.post("/stage{n}/expert-knowledge")
async def submit_expert_knowledge(n: str, payload: dict = Body(...)):
    """
    提交领域知识文本，LLM 解析并返回 diff 预览。
    body: {"text": "..."}
    """
    stage = _resolve_stage(n)
    text = payload.get("text", "").strip()
    if not text:
        from fastapi import HTTPException
        raise HTTPException(400, "text is required")

    data = read_stage(stage)
    if data is None:
        from fastapi import HTTPException
        raise HTTPException(404, "Stage data not found")

    triples_snapshot = data.get("triples", [])

    # 调用 LLM 生成 diff
    import os
    from openai import OpenAI
    client = OpenAI(
        api_key=os.environ.get("LLM_API_KEY", ""),
        base_url=os.environ.get("LLM_BASE_URL", ""),
    )
    prompt = f"""你是知识图谱构建专家。以下是专家提供的领域知识：

"{text}"

以下是当前的三元组列表（JSON）：
{__import__('json').dumps(triples_snapshot[:30], ensure_ascii=False, indent=2)}

请根据专家知识，对三元组进行必要的修改（增/删/改）。
返回严格 JSON，格式如下（无需解释，仅 JSON）：
{{
  "added": [  // 新增的三元组，每个含 head/relation/tail/confidence/source/head_type/tail_type
  ],
  "removed_indices": [],  // 需要删除的三元组索引（基于上面列表）
  "modified": [  // {{index: int, triple: {{...}}}} 格式
  ]
}}"""

    resp = client.chat.completions.create(
        model=os.environ.get("LLM_MODEL", ""),
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000,
        temperature=0.1,
    )
    raw = resp.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    import json as _json
    try:
        diff = _json.loads(raw)
    except _json.JSONDecodeError:
        from fastapi import HTTPException
        raise HTTPException(500, f"LLM returned invalid JSON: {raw[:200]}")

    diff.setdefault("added", [])
    diff.setdefault("removed_indices", [])
    diff.setdefault("modified", [])
    for item in diff["added"]:
        item.setdefault("source", "expert")
        item.setdefault("confidence", 1.0)

    return {"ok": True, "diff": diff}


@router.post("/stage{n}/expert-knowledge/confirm")
async def confirm_expert_knowledge(n: str, payload: dict = Body(...)):
    """
    将 /expert-knowledge 返回的 diff 应用到 JSON。
    body: {"diff": {"added": [...], "removed_indices": [...], "modified": [...]}}
    """
    stage = _resolve_stage(n)
    diff = payload.get("diff", {})
    data = read_stage(stage)
    if data is None:
        from fastapi import HTTPException
        raise HTTPException(404, "Stage data not found")

    triples = data.get("triples", [])

    # 先处理 modified（改索引不变）
    for m in diff.get("modified", []):
        idx = m.get("index")
        if idx is not None and 0 <= idx < len(triples):
            triples[idx] = m["triple"]

    # 再处理 removed（从大到小删，避免索引偏移）
    for idx in sorted(diff.get("removed_indices", []), reverse=True):
        if 0 <= idx < len(triples):
            triples.pop(idx)

    # 最后追加 added
    for t in diff.get("added", []):
        triples.append(t)

    data["triples"] = triples
    write_stage(stage, data)
    return {"ok": True, "total": len(triples)}


@router.post("/stage{n}/diagnose")
async def diagnose_stage(n: str, request: Request):
    """触发 LLM 诊断，SSE 流式返回"""
    stage = _resolve_stage(n)
    report = read_stage_report(stage)
    if report is None:
        from fastapi import HTTPException
        raise HTTPException(404, "No report found. Call /report first.")

    from backend.pipelines.kg_diagnose import diagnose_issues_stream
    import json as _json

    async def _gen():
        async for frame in diagnose_issues_stream(report):
            yield f"data: {_json.dumps(frame, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"

    from fastapi.responses import StreamingResponse
    return StreamingResponse(_gen(), media_type="text/event-stream")
```

- [ ] **Step 5: 运行端点测试**

```bash
cd "c:/xjp/代码/rag-demo"
PYTHONUTF8=1 "C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" -m pytest tests/kg/test_hitl_endpoints.py -v
```

预期：4 个 PASSED

- [ ] **Step 6: 提交**

```bash
cd "c:/xjp/代码/rag-demo"
git add backend/routers/kg_stages.py tests/kg/test_hitl_endpoints.py
git commit -m "feat(hitl): integrate report generation into Stage 1/2 and add 7 HITL endpoints"
```

---

## Task 6：前端 TypeScript 类型 + API 客户端

**Files:**
- Modify: `frontend/src/types/index.ts`
- Modify: `frontend/src/api/client.ts`

### 背景
新增前端类型定义和 API 方法，供后续组件使用。

- [ ] **Step 1: 在 types/index.ts 末尾追加新类型**

读取 `frontend/src/types/index.ts` 末尾，追加：

```typescript
// ── HITL 扩展类型 ──────────────────────────────────────

export interface StageStats {
  entities_count: number
  triples_count: number
  relation_breakdown: Record<string, number>
  confidence_histogram: number[]          // 5个区间的占比
  bom_coverage_ratio: number | null       // Stage 2 专用
  isolated_entities_count: number
  low_confidence_count: number
}

export interface StageIssue {
  severity: 'critical' | 'warning' | 'info'
  title: string
  title_zh: string
  description: string
  suggestion: string
  affected_triple_ids: string[]
}

export interface StageDiff {
  added_triples: FlatTriple[]
  removed_triples: FlatTriple[]
  modified_triples: [FlatTriple, FlatTriple][]
}

export interface StageReport {
  stage: string
  generated_at: string
  stats: StageStats
  issues: StageIssue[]
  diff: StageDiff | null
}

export interface StageStateInfo {
  stage: string
  status: 'idle' | 'running' | 'awaiting_review' | 'approved'
  approved_at?: string
}

export interface BilingualTriple extends FlatTriple {
  head_zh: string
  relation_zh: string
  tail_zh: string
}

export interface ExpertDiff {
  added: FlatTriple[]
  removed_indices: number[]
  modified: { index: number; triple: FlatTriple }[]
}
```

扩展已有 `KgSseFrame` 接口，新增 `stage_report_ready` 类型：

```typescript
// 在现有 KgSseFrame 的 type 联合类型中新增
// 找到 type: 'log' | 'result' | 'done' | 'error'，改为：
// type: 'log' | 'result' | 'done' | 'error' | 'stage_report_ready'
// 并新增字段：
//   issues_count?: number   // stage_report_ready 时的问题数
```

- [ ] **Step 2: 在 api/client.ts 末尾追加新方法**

读取 `frontend/src/api/client.ts`，在末尾追加：

```typescript
// ── HITL API ──────────────────────────────────────────

const BASE = '/api'  // 复用文件中已有的 BASE 常量名

export async function getStageReport(stageN: 1 | 2): Promise<StageReport> {
  const res = await fetch(`${BASE}/kg/stage${stageN}/report`)
  if (!res.ok) throw new Error(`getStageReport failed: ${res.status}`)
  return res.json()
}

export async function getStageState(stageN: 1 | 2): Promise<StageStateInfo> {
  const res = await fetch(`${BASE}/kg/stage${stageN}/state`)
  if (!res.ok) throw new Error(`getStageState failed: ${res.status}`)
  return res.json()
}

export async function approveStage(stageN: 1 | 2): Promise<void> {
  const res = await fetch(`${BASE}/kg/stage${stageN}/approve`, { method: 'POST' })
  if (!res.ok) throw new Error(`approveStage failed: ${res.status}`)
}

export async function listTriplesBilingual(
  stageN: 1 | 2,
  offset = 0,
  limit = 50
): Promise<{ total: number; offset: number; limit: number; triples: BilingualTriple[] }> {
  const res = await fetch(`${BASE}/kg/stage${stageN}/triples?offset=${offset}&limit=${limit}`)
  if (!res.ok) throw new Error(`listTriplesBilingual failed: ${res.status}`)
  return res.json()
}

export async function updateTriple(stageN: 1 | 2, idx: number, triple: Partial<FlatTriple>): Promise<void> {
  const res = await fetch(`${BASE}/kg/stage${stageN}/triples/${idx}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(triple),
  })
  if (!res.ok) throw new Error(`updateTriple failed: ${res.status}`)
}

export async function deleteTriple(stageN: 1 | 2, idx: number): Promise<void> {
  const res = await fetch(`${BASE}/kg/stage${stageN}/triples/${idx}`, { method: 'DELETE' })
  if (!res.ok) throw new Error(`deleteTriple failed: ${res.status}`)
}

export async function addTriple(stageN: 1 | 2, triple: Partial<FlatTriple>): Promise<void> {
  const res = await fetch(`${BASE}/kg/stage${stageN}/triples`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(triple),
  })
  if (!res.ok) throw new Error(`addTriple failed: ${res.status}`)
}

export async function submitExpertKnowledge(stageN: 1 | 2, text: string): Promise<{ diff: ExpertDiff }> {
  const res = await fetch(`${BASE}/kg/stage${stageN}/expert-knowledge`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text }),
  })
  if (!res.ok) throw new Error(`submitExpertKnowledge failed: ${res.status}`)
  return res.json()
}

export async function confirmExpertKnowledge(stageN: 1 | 2, diff: ExpertDiff): Promise<void> {
  const res = await fetch(`${BASE}/kg/stage${stageN}/expert-knowledge/confirm`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ diff }),
  })
  if (!res.ok) throw new Error(`confirmExpertKnowledge failed: ${res.status}`)
}

export async function* diagnoseStage(stageN: 1 | 2): AsyncGenerator<Record<string, unknown>> {
  yield* postSSE(`/kg/stage${stageN}/diagnose`, undefined) as AsyncGenerator<Record<string, unknown>>
}
```

- [ ] **Step 3: 构建检查（TypeScript 类型无误）**

```bash
cd "c:/xjp/代码/rag-demo/frontend"
npx tsc --noEmit 2>&1 | head -30
```

预期：无错误输出（或仅有已有的无关 warning）

- [ ] **Step 4: 提交**

```bash
cd "c:/xjp/代码/rag-demo"
git add frontend/src/types/index.ts frontend/src/api/client.ts
git commit -m "feat(hitl): add frontend types and API client methods"
```

---

## Task 7：StageIssueCard.tsx — 问题卡片组件

**Files:**
- Create: `frontend/src/components/kg/stages/StageIssueCard.tsx`

- [ ] **Step 1: 实现组件**

```tsx
import React from 'react'
import { StageIssue } from '../../../types'

interface Props {
  issue: StageIssue
  extraSuggestion?: string   // LLM 诊断追加的建议
  onHighlight?: (ids: string[]) => void
}

const SEVERITY_STYLE: Record<string, { bg: string; border: string; badge: string; text: string }> = {
  critical: { bg: 'bg-red-950/30', border: 'border-red-600', badge: 'bg-red-600 text-white', text: 'text-red-400' },
  warning:  { bg: 'bg-amber-950/30', border: 'border-amber-500', badge: 'bg-amber-500 text-black', text: 'text-amber-400' },
  info:     { bg: 'bg-blue-950/30', border: 'border-blue-500', badge: 'bg-blue-500 text-white', text: 'text-blue-400' },
}

const SEVERITY_LABEL: Record<string, string> = {
  critical: '严重', warning: '警告', info: '提示',
}

export default function StageIssueCard({ issue, extraSuggestion, onHighlight }: Props) {
  const s = SEVERITY_STYLE[issue.severity] ?? SEVERITY_STYLE.info

  return (
    <div className={`rounded-lg border ${s.border} ${s.bg} p-3 mb-2`}>
      <div className="flex items-start gap-2">
        <span className={`text-xs px-2 py-0.5 rounded font-semibold shrink-0 ${s.badge}`}>
          {SEVERITY_LABEL[issue.severity]}
        </span>
        <div className="flex-1 min-w-0">
          <p className={`font-semibold text-sm ${s.text}`}>{issue.title_zh}</p>
          <p className="text-xs text-gray-400 mt-0.5">{issue.description}</p>
          <p className="text-xs text-blue-400 mt-1">
            👉 {issue.suggestion}
          </p>
          {extraSuggestion && (
            <p className="text-xs text-purple-400 mt-1 border-t border-purple-900/50 pt-1">
              🤖 {extraSuggestion}
            </p>
          )}
          {issue.affected_triple_ids.length > 0 && onHighlight && (
            <button
              onClick={() => onHighlight(issue.affected_triple_ids)}
              className="mt-1 text-xs text-gray-500 hover:text-blue-400 underline"
            >
              高亮 {issue.affected_triple_ids.length} 条相关三元组
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
```

- [ ] **Step 2: 构建检查**

```bash
cd "c:/xjp/代码/rag-demo/frontend"
npx tsc --noEmit 2>&1 | head -20
```

- [ ] **Step 3: 提交**

```bash
cd "c:/xjp/代码/rag-demo"
git add frontend/src/components/kg/stages/StageIssueCard.tsx
git commit -m "feat(hitl): add StageIssueCard component"
```

---

## Task 8：TriplesEditor.tsx — 三元组编辑器（含中英对照）

**Files:**
- Create: `frontend/src/components/kg/stages/TriplesEditor.tsx`

- [ ] **Step 1: 实现组件**

```tsx
import React, { useState, useEffect, useCallback } from 'react'
import { BilingualTriple } from '../../../types'
import {
  listTriplesBilingual, updateTriple, deleteTriple, addTriple,
} from '../../../api/client'

interface Props {
  stageN: 1 | 2
  highlightIds?: string[]
}

type DisplayMode = 'en' | 'zh' | 'both'

const EMPTY_TRIPLE = { head: '', relation: '', tail: '', confidence: 1.0, source: 'expert', head_type: '', tail_type: '' }

export default function TriplesEditor({ stageN, highlightIds = [] }: Props) {
  const [triples, setTriples] = useState<BilingualTriple[]>([])
  const [total, setTotal] = useState(0)
  const [offset, setOffset] = useState(0)
  const [mode, setMode] = useState<DisplayMode>('both')
  const [editIdx, setEditIdx] = useState<number | null>(null)
  const [editBuf, setEditBuf] = useState<Partial<BilingualTriple>>({})
  const [adding, setAdding] = useState(false)
  const [newTriple, setNewTriple] = useState({ ...EMPTY_TRIPLE })
  const [loading, setLoading] = useState(false)
  const LIMIT = 50

  const load = useCallback(async (off: number) => {
    setLoading(true)
    try {
      const res = await listTriplesBilingual(stageN, off, LIMIT)
      setTriples(res.triples)
      setTotal(res.total)
      setOffset(off)
    } finally {
      setLoading(false)
    }
  }, [stageN])

  useEffect(() => { load(0) }, [load])

  const handleSave = async (idx: number) => {
    await updateTriple(stageN, offset + idx, editBuf)
    setEditIdx(null)
    load(offset)
  }

  const handleDelete = async (idx: number) => {
    if (!confirm('确认删除这条三元组？')) return
    await deleteTriple(stageN, offset + idx)
    load(offset)
  }

  const handleAdd = async () => {
    await addTriple(stageN, newTriple)
    setAdding(false)
    setNewTriple({ ...EMPTY_TRIPLE })
    load(offset)
  }

  const isHighlighted = (t: BilingualTriple) =>
    highlightIds.includes(t.head) || highlightIds.includes(t.tail)

  const showEn = mode === 'en' || mode === 'both'
  const showZh = mode === 'zh' || mode === 'both'

  return (
    <div className="text-xs">
      {/* 工具栏 */}
      <div className="flex items-center gap-2 mb-2">
        <span className="text-gray-400">显示模式：</span>
        {(['en', 'zh', 'both'] as DisplayMode[]).map(m => (
          <button
            key={m}
            onClick={() => setMode(m)}
            className={`px-2 py-0.5 rounded text-xs border ${mode === m ? 'border-blue-500 text-blue-400' : 'border-gray-600 text-gray-500'}`}
          >
            {{ en: '仅英文', zh: '仅中文', both: '中英对照' }[m]}
          </button>
        ))}
        <button
          onClick={() => setAdding(true)}
          className="ml-auto px-2 py-0.5 rounded border border-green-600 text-green-400"
        >
          + 新增三元组
        </button>
      </div>

      {/* 新增行 */}
      {adding && (
        <div className="mb-2 p-2 bg-green-950/30 border border-green-700 rounded flex gap-1 flex-wrap">
          {(['head', 'relation', 'tail'] as const).map(f => (
            <input
              key={f}
              placeholder={f}
              value={newTriple[f]}
              onChange={e => setNewTriple(p => ({ ...p, [f]: e.target.value }))}
              className="flex-1 min-w-20 bg-gray-900 border border-gray-600 rounded px-1 py-0.5 text-white"
            />
          ))}
          <input
            type="number" min={0} max={1} step={0.1}
            value={newTriple.confidence}
            onChange={e => setNewTriple(p => ({ ...p, confidence: parseFloat(e.target.value) }))}
            className="w-16 bg-gray-900 border border-gray-600 rounded px-1 py-0.5 text-white"
          />
          <button onClick={handleAdd} className="px-2 py-0.5 bg-green-700 text-white rounded">确认</button>
          <button onClick={() => setAdding(false)} className="px-2 py-0.5 bg-gray-700 text-white rounded">取消</button>
        </div>
      )}

      {/* 表格 */}
      <div className="overflow-x-auto">
        <table className="w-full border-collapse">
          <thead>
            <tr className="text-gray-500 border-b border-gray-700">
              {showEn && <th className="text-left p-1">Head</th>}
              {showZh && <th className="text-left p-1 text-blue-400/70">主体</th>}
              {showEn && <th className="text-left p-1">Relation</th>}
              {showZh && <th className="text-left p-1 text-blue-400/70">关系</th>}
              {showEn && <th className="text-left p-1">Tail</th>}
              {showZh && <th className="text-left p-1 text-blue-400/70">客体</th>}
              <th className="text-left p-1">置信度</th>
              <th className="p-1"></th>
            </tr>
          </thead>
          <tbody>
            {loading && (
              <tr><td colSpan={8} className="text-center py-4 text-gray-500">加载中...</td></tr>
            )}
            {triples.map((t, i) => {
              const hi = isHighlighted(t)
              if (editIdx === i) {
                return (
                  <tr key={i} className="bg-blue-950/40 border-b border-gray-800">
                    <td colSpan={showZh ? 6 : 3} className="p-1">
                      <div className="flex gap-1">
                        {(['head', 'relation', 'tail'] as const).map(f => (
                          <input
                            key={f}
                            value={String(editBuf[f] ?? t[f] ?? '')}
                            onChange={e => setEditBuf(p => ({ ...p, [f]: e.target.value }))}
                            className="flex-1 bg-gray-900 border border-blue-600 rounded px-1 py-0.5 text-white text-xs"
                          />
                        ))}
                      </div>
                    </td>
                    <td className="p-1">
                      <input
                        type="number" min={0} max={1} step={0.1}
                        value={Number(editBuf.confidence ?? t.confidence)}
                        onChange={e => setEditBuf(p => ({ ...p, confidence: parseFloat(e.target.value) }))}
                        className="w-14 bg-gray-900 border border-blue-600 rounded px-1 py-0.5 text-white text-xs"
                      />
                    </td>
                    <td className="p-1 flex gap-1">
                      <button onClick={() => handleSave(i)} className="px-1 py-0.5 bg-blue-700 text-white rounded">保存</button>
                      <button onClick={() => setEditIdx(null)} className="px-1 py-0.5 bg-gray-700 text-white rounded">取消</button>
                    </td>
                  </tr>
                )
              }
              return (
                <tr
                  key={i}
                  className={`border-b border-gray-800 ${hi ? 'bg-amber-950/20' : 'hover:bg-gray-800/30'}`}
                >
                  {showEn && <td className="p-1 text-gray-300 truncate max-w-32">{t.head}</td>}
                  {showZh && <td className="p-1 text-blue-300 truncate max-w-24">{t.head_zh}</td>}
                  {showEn && <td className="p-1 text-purple-400 truncate max-w-24">{t.relation}</td>}
                  {showZh && <td className="p-1 text-purple-300 truncate max-w-20">{t.relation_zh}</td>}
                  {showEn && <td className="p-1 text-gray-300 truncate max-w-32">{t.tail}</td>}
                  {showZh && <td className="p-1 text-blue-300 truncate max-w-24">{t.tail_zh}</td>}
                  <td className="p-1 text-gray-400">{t.confidence.toFixed(2)}</td>
                  <td className="p-1 flex gap-1 shrink-0">
                    <button onClick={() => { setEditIdx(i); setEditBuf({}) }} className="text-blue-500 hover:text-blue-300">编辑</button>
                    <button onClick={() => handleDelete(i)} className="text-red-500 hover:text-red-300">删除</button>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      {/* 分页 */}
      <div className="flex items-center gap-2 mt-2 text-gray-500">
        <span>共 {total} 条</span>
        <button
          disabled={offset === 0}
          onClick={() => load(Math.max(0, offset - LIMIT))}
          className="px-2 py-0.5 border border-gray-700 rounded disabled:opacity-30"
        >上页</button>
        <span>{Math.floor(offset / LIMIT) + 1} / {Math.ceil(total / LIMIT)}</span>
        <button
          disabled={offset + LIMIT >= total}
          onClick={() => load(offset + LIMIT)}
          className="px-2 py-0.5 border border-gray-700 rounded disabled:opacity-30"
        >下页</button>
      </div>
    </div>
  )
}
```

- [ ] **Step 2: 构建检查**

```bash
cd "c:/xjp/代码/rag-demo/frontend"
npx tsc --noEmit 2>&1 | head -20
```

- [ ] **Step 3: 提交**

```bash
cd "c:/xjp/代码/rag-demo"
git add frontend/src/components/kg/stages/TriplesEditor.tsx
git commit -m "feat(hitl): add TriplesEditor with bilingual display and CRUD"
```

---

## Task 9：ExpertKnowledgeInput.tsx + ParamTuner.tsx

**Files:**
- Create: `frontend/src/components/kg/stages/ExpertKnowledgeInput.tsx`
- Create: `frontend/src/components/kg/stages/ParamTuner.tsx`

- [ ] **Step 1: 实现 ExpertKnowledgeInput.tsx**

```tsx
import React, { useState } from 'react'
import { ExpertDiff } from '../../../types'
import { submitExpertKnowledge, confirmExpertKnowledge } from '../../../api/client'

interface Props {
  stageN: 1 | 2
  onConfirmed: () => void
}

export default function ExpertKnowledgeInput({ stageN, onConfirmed }: Props) {
  const [text, setText] = useState('')
  const [diff, setDiff] = useState<ExpertDiff | null>(null)
  const [loading, setLoading] = useState(false)
  const [confirming, setConfirming] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async () => {
    if (!text.trim()) return
    setLoading(true)
    setError('')
    setDiff(null)
    try {
      const res = await submitExpertKnowledge(stageN, text)
      setDiff(res.diff)
    } catch (e) {
      setError(String(e))
    } finally {
      setLoading(false)
    }
  }

  const handleConfirm = async () => {
    if (!diff) return
    setConfirming(true)
    try {
      await confirmExpertKnowledge(stageN, diff)
      setDiff(null)
      setText('')
      onConfirmed()
    } finally {
      setConfirming(false)
    }
  }

  return (
    <div className="text-xs">
      <p className="text-gray-400 mb-1">输入您的领域知识，系统将自动分析并修改对应的三元组：</p>
      <textarea
        rows={3}
        value={text}
        onChange={e => setText(e.target.value)}
        placeholder="例如：压气机第一级叶片和盘是榫槽配合，不是螺栓连接..."
        className="w-full bg-gray-900 border border-gray-600 rounded px-2 py-1 text-white text-xs resize-none focus:border-purple-500 outline-none"
      />
      <button
        onClick={handleSubmit}
        disabled={loading || !text.trim()}
        className="mt-1 px-3 py-1 bg-purple-800 text-white rounded disabled:opacity-40 hover:bg-purple-700"
      >
        {loading ? '分析中...' : '提交领域知识'}
      </button>

      {error && <p className="mt-1 text-red-400">{error}</p>}

      {/* Diff 预览 */}
      {diff && (
        <div className="mt-3 border border-purple-700 rounded p-2 bg-purple-950/20">
          <p className="text-purple-400 font-semibold mb-2">变更预览</p>

          {diff.added.length > 0 && (
            <div className="mb-2">
              <p className="text-green-400 mb-1">+ 新增 {diff.added.length} 条</p>
              {diff.added.map((t, i) => (
                <div key={i} className="text-green-300 bg-green-950/30 rounded px-1 py-0.5 mb-0.5">
                  {t.head} → <span className="text-purple-300">{t.relation}</span> → {t.tail}
                </div>
              ))}
            </div>
          )}

          {diff.removed_indices.length > 0 && (
            <div className="mb-2">
              <p className="text-red-400 mb-1">- 删除 {diff.removed_indices.length} 条（索引：{diff.removed_indices.join(', ')}）</p>
            </div>
          )}

          {diff.modified.length > 0 && (
            <div className="mb-2">
              <p className="text-amber-400 mb-1">~ 修改 {diff.modified.length} 条</p>
              {diff.modified.map((m, i) => (
                <div key={i} className="text-amber-300 bg-amber-950/30 rounded px-1 py-0.5 mb-0.5">
                  #{m.index}: {m.triple.head} → <span className="text-purple-300">{m.triple.relation}</span> → {m.triple.tail}
                </div>
              ))}
            </div>
          )}

          <div className="flex gap-2 mt-2">
            <button
              onClick={handleConfirm}
              disabled={confirming}
              className="px-3 py-1 bg-green-800 text-white rounded hover:bg-green-700 disabled:opacity-40"
            >
              {confirming ? '应用中...' : '确认应用'}
            </button>
            <button
              onClick={() => setDiff(null)}
              className="px-3 py-1 bg-gray-700 text-white rounded hover:bg-gray-600"
            >
              取消
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
```

- [ ] **Step 2: 实现 ParamTuner.tsx**

```tsx
import React, { useState } from 'react'

interface Props {
  stageN: 1 | 2
  onRerun: (params: RerunParams) => void
  running: boolean
}

export interface RerunParams {
  confidence_threshold: number
  gleaning_rounds: number
}

export default function ParamTuner({ stageN, onRerun, running }: Props) {
  const [threshold, setThreshold] = useState(0.3)
  const [gleaning, setGleaning] = useState(1)

  return (
    <div className="text-xs">
      <p className="text-gray-400 mb-2">调整参数后点击重跑，结果将替换本阶段当前数据：</p>

      <div className="flex flex-col gap-2">
        <label className="flex items-center gap-3">
          <span className="text-gray-300 w-28 shrink-0">置信度阈值</span>
          <input
            type="range" min={0} max={0.9} step={0.05}
            value={threshold}
            onChange={e => setThreshold(parseFloat(e.target.value))}
            className="flex-1"
          />
          <span className="text-blue-400 w-10 text-right">{threshold.toFixed(2)}</span>
        </label>
        <p className="text-gray-600 pl-31 -mt-1">低于此置信度的三元组将被过滤</p>

        {stageN === 2 && (
          <label className="flex items-center gap-3">
            <span className="text-gray-300 w-28 shrink-0">Gleaning 轮次</span>
            <input
              type="range" min={0} max={3} step={1}
              value={gleaning}
              onChange={e => setGleaning(parseInt(e.target.value))}
              className="flex-1"
            />
            <span className="text-blue-400 w-10 text-right">{gleaning}</span>
          </label>
        )}
      </div>

      <button
        onClick={() => onRerun({ confidence_threshold: threshold, gleaning_rounds: gleaning })}
        disabled={running}
        className="mt-3 px-3 py-1 bg-amber-800 text-white rounded hover:bg-amber-700 disabled:opacity-40"
      >
        {running ? '重跑中...' : `重新运行 Stage ${stageN}`}
      </button>
      <p className="text-gray-600 mt-1">注：重跑后需重新审阅</p>
    </div>
  )
}
```

- [ ] **Step 3: 构建检查**

```bash
cd "c:/xjp/代码/rag-demo/frontend"
npx tsc --noEmit 2>&1 | head -20
```

- [ ] **Step 4: 提交**

```bash
cd "c:/xjp/代码/rag-demo"
git add frontend/src/components/kg/stages/ExpertKnowledgeInput.tsx frontend/src/components/kg/stages/ParamTuner.tsx
git commit -m "feat(hitl): add ExpertKnowledgeInput and ParamTuner components"
```

---

## Task 10：StageReviewPanel.tsx — 审阅面板主容器

**Files:**
- Create: `frontend/src/components/kg/stages/StageReviewPanel.tsx`

- [ ] **Step 1: 实现组件**

```tsx
import React, { useState, useEffect, useCallback } from 'react'
import { StageReport, StageIssue } from '../../../types'
import {
  getStageReport, approveStage, diagnoseStage,
} from '../../../api/client'
import StageIssueCard from './StageIssueCard'
import TriplesEditor from './TriplesEditor'
import ExpertKnowledgeInput from './ExpertKnowledgeInput'
import ParamTuner, { RerunParams } from './ParamTuner'
import KgViewer from '../KgViewer'

interface Props {
  stageN: 1 | 2
  onApproved: () => void
  onRerun: (params: RerunParams) => void
  rerunning: boolean
}

type ActiveTab = 'issues' | 'graph' | 'triples' | 'knowledge' | 'params'

export default function StageReviewPanel({ stageN, onApproved, onRerun, rerunning }: Props) {
  const [report, setReport] = useState<StageReport | null>(null)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<ActiveTab>('issues')
  const [diagnosing, setDiagnosing] = useState(false)
  const [diagnosisByIndex, setDiagnosisByIndex] = useState<Record<number, string>>({})
  const [approving, setApproving] = useState(false)
  const [highlightIds, setHighlightIds] = useState<string[]>([])

  const loadReport = useCallback(async () => {
    setLoading(true)
    try {
      const r = await getStageReport(stageN)
      setReport(r)
    } finally {
      setLoading(false)
    }
  }, [stageN])

  useEffect(() => { loadReport() }, [loadReport])

  const handleDiagnose = async () => {
    if (!report) return
    setDiagnosing(true)
    setDiagnosisByIndex({})
    try {
      for await (const frame of diagnoseStage(stageN)) {
        if (frame.type === 'diagnosis_chunk') {
          const idx = frame.issue_index as number
          setDiagnosisByIndex(prev => ({
            ...prev,
            [idx]: (prev[idx] ?? '') + (frame.content as string),
          }))
        }
      }
    } finally {
      setDiagnosing(false)
    }
  }

  const handleApprove = async () => {
    setApproving(true)
    try {
      await approveStage(stageN)
      onApproved()
    } finally {
      setApproving(false)
    }
  }

  if (loading) {
    return <div className="py-4 text-center text-gray-500 text-sm">加载审阅报告...</div>
  }
  if (!report) {
    return <div className="py-4 text-center text-red-500 text-sm">报告加载失败</div>
  }

  const { stats, issues, diff } = report
  const criticalCount = issues.filter(i => i.severity === 'critical').length
  const warningCount = issues.filter(i => i.severity === 'warning').length

  const TABS: { key: ActiveTab; label: string }[] = [
    { key: 'issues', label: `问题清单 (${issues.length})` },
    { key: 'graph', label: 'KG 快照' },
    { key: 'triples', label: '三元组编辑' },
    { key: 'knowledge', label: '领域知识' },
    { key: 'params', label: '参数调整' },
  ]

  return (
    <div className="border border-purple-700/50 rounded-lg bg-gray-900/50 p-4 mt-2">
      {/* 统计卡片行 */}
      <div className="flex flex-wrap gap-2 mb-4">
        <div className="bg-blue-950/40 border border-blue-700/50 rounded px-3 py-1.5 text-xs">
          <span className="text-gray-400">实体</span>
          <span className="ml-2 text-blue-400 font-semibold">{stats.entities_count}</span>
        </div>
        <div className="bg-blue-950/40 border border-blue-700/50 rounded px-3 py-1.5 text-xs">
          <span className="text-gray-400">三元组</span>
          <span className="ml-2 text-blue-400 font-semibold">{stats.triples_count}</span>
        </div>
        {stats.bom_coverage_ratio !== null && (
          <div className={`border rounded px-3 py-1.5 text-xs ${stats.bom_coverage_ratio < 0.4 ? 'bg-red-950/40 border-red-700/50' : 'bg-green-950/40 border-green-700/50'}`}>
            <span className="text-gray-400">BOM覆盖率</span>
            <span className={`ml-2 font-semibold ${stats.bom_coverage_ratio < 0.4 ? 'text-red-400' : 'text-green-400'}`}>
              {(stats.bom_coverage_ratio * 100).toFixed(0)}%
            </span>
          </div>
        )}
        <div className={`border rounded px-3 py-1.5 text-xs ${criticalCount > 0 ? 'bg-red-950/40 border-red-700/50' : 'bg-gray-800 border-gray-700'}`}>
          <span className="text-gray-400">严重</span>
          <span className={`ml-2 font-semibold ${criticalCount > 0 ? 'text-red-400' : 'text-gray-500'}`}>{criticalCount}</span>
        </div>
        <div className={`border rounded px-3 py-1.5 text-xs ${warningCount > 0 ? 'bg-amber-950/40 border-amber-700/50' : 'bg-gray-800 border-gray-700'}`}>
          <span className="text-gray-400">警告</span>
          <span className={`ml-2 font-semibold ${warningCount > 0 ? 'text-amber-400' : 'text-gray-500'}`}>{warningCount}</span>
        </div>
        {diff && (
          <div className="bg-gray-800 border border-gray-700 rounded px-3 py-1.5 text-xs">
            <span className="text-green-400">+{diff.added_triples.length}</span>
            <span className="text-gray-600 mx-1">/</span>
            <span className="text-red-400">-{diff.removed_triples.length}</span>
            <span className="text-gray-500 ml-1">（与上次对比）</span>
          </div>
        )}
      </div>

      {/* Tab 导航 */}
      <div className="flex gap-1 border-b border-gray-700 mb-3">
        {TABS.map(t => (
          <button
            key={t.key}
            onClick={() => setActiveTab(t.key)}
            className={`px-3 py-1 text-xs rounded-t border-b-2 transition-colors ${
              activeTab === t.key
                ? 'border-purple-500 text-purple-300'
                : 'border-transparent text-gray-500 hover:text-gray-300'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Tab 内容 */}
      <div className="min-h-40">
        {activeTab === 'issues' && (
          <div>
            {issues.length === 0 && (
              <p className="text-green-400 text-sm">✓ 未检测到明显问题，质量良好</p>
            )}
            {issues.map((issue, i) => (
              <StageIssueCard
                key={i}
                issue={issue}
                extraSuggestion={diagnosisByIndex[i]}
                onHighlight={ids => { setHighlightIds(ids); setActiveTab('triples') }}
              />
            ))}
            {issues.length > 0 && (
              <button
                onClick={handleDiagnose}
                disabled={diagnosing}
                className="mt-2 px-3 py-1 text-xs border border-purple-600 text-purple-400 rounded hover:bg-purple-950/30 disabled:opacity-40"
              >
                {diagnosing ? '🤖 LLM 诊断中...' : '🤖 生成 LLM 深度诊断'}
              </button>
            )}
          </div>
        )}

        {activeTab === 'graph' && (
          <div className="h-64 rounded border border-gray-700 overflow-hidden">
            <KgViewer stageFilter={stageN === 1 ? 'BOM' : 'Manual'} />
          </div>
        )}

        {activeTab === 'triples' && (
          <TriplesEditor
            stageN={stageN}
            highlightIds={highlightIds}
          />
        )}

        {activeTab === 'knowledge' && (
          <ExpertKnowledgeInput
            stageN={stageN}
            onConfirmed={() => { loadReport() }}
          />
        )}

        {activeTab === 'params' && (
          <ParamTuner
            stageN={stageN}
            onRerun={onRerun}
            running={rerunning}
          />
        )}
      </div>

      {/* 确认放行按钮 */}
      <div className="mt-4 pt-3 border-t border-gray-700 flex items-center gap-3">
        <button
          onClick={handleApprove}
          disabled={approving}
          className="px-4 py-1.5 bg-green-800 text-white rounded font-semibold hover:bg-green-700 disabled:opacity-40 text-sm"
        >
          {approving ? '处理中...' : `✅ 确认放行 → Stage ${stageN === 1 ? '2' : '完成'}`}
        </button>
        <p className="text-gray-500 text-xs">确认后将解锁下一阶段</p>
      </div>
    </div>
  )
}
```

- [ ] **Step 2: 构建检查**

```bash
cd "c:/xjp/代码/rag-demo/frontend"
npx tsc --noEmit 2>&1 | head -20
```

- [ ] **Step 3: 提交**

```bash
cd "c:/xjp/代码/rag-demo"
git add frontend/src/components/kg/stages/StageReviewPanel.tsx
git commit -m "feat(hitl): add StageReviewPanel main container"
```

---

## Task 11：KgViewer.tsx — 新增 stageFilter prop

**Files:**
- Modify: `frontend/src/components/kg/KgViewer.tsx`

- [ ] **Step 1: 读取当前 KgViewer.tsx 的 props 接口和数据加载部分**

读取 `frontend/src/components/kg/KgViewer.tsx` 前 60 行，确认：
- 当前组件是否有 Props 接口
- `getKgGraph` 的调用方式

- [ ] **Step 2: 修改 KgViewer.tsx**

在现有组件基础上：

1. 新增 `Props` 接口：
```tsx
interface Props {
  stageFilter?: string   // 'BOM' | 'Manual' | 'CAD'，不传则显示全部
}

export default function KgViewer({ stageFilter }: Props = {}) {
```

2. 在 `loadAndRender` 中，拿到 `data` 后过滤节点：
```tsx
// 在 const data = await getKgGraph(...) 之后插入：
if (stageFilter) {
  data.nodes = data.nodes.filter((n: KgNode) =>
    !n.source || n.source === stageFilter
  )
  const nodeIds = new Set(data.nodes.map((n: KgNode) => n.id))
  data.links = data.links.filter((l: { source: string; target: string }) =>
    nodeIds.has(l.source) && nodeIds.has(l.target)
  )
}
```

- [ ] **Step 3: 构建检查**

```bash
cd "c:/xjp/代码/rag-demo/frontend"
npx tsc --noEmit 2>&1 | head -20
```

- [ ] **Step 4: 提交**

```bash
cd "c:/xjp/代码/rag-demo"
git add frontend/src/components/kg/KgViewer.tsx
git commit -m "feat(hitl): add stageFilter prop to KgViewer for per-stage snapshot"
```

---

## Task 12：集成到 Stage1Bom.tsx 和 Stage2Manual.tsx

**Files:**
- Modify: `frontend/src/components/kg/stages/Stage1Bom.tsx`
- Modify: `frontend/src/components/kg/stages/Stage2Manual.tsx`

### 背景
在两个 Stage 组件中：1）处理新增的 `stage_report_ready` SSE 事件，展开审阅面板；2）锁定「下一步」逻辑（通过 `onComplete` 的触发时机控制）；3）传入重跑回调给 `StageReviewPanel`。

- [ ] **Step 1: 修改 Stage1Bom.tsx**

读取 `frontend/src/components/kg/stages/Stage1Bom.tsx` 完整内容，然后做以下改动：

**新增 state：**
```tsx
const [showReview, setShowReview] = useState(false)
const [approved, setApproved] = useState(false)
const [rerunning, setRerunning] = useState(false)
```

**在 `useStageSSE` 的 callbacks 中新增处理：**
```tsx
// 在 onDone 回调中，将原来调用 onComplete?.() 改为：
onDone: async (success) => {
  if (success) {
    const p = await getKgStagePreview('bom', 0)
    setPreview(p)
    setShowReview(true)   // 展开审阅面板，不立即 onComplete
  }
},
// 新增 onFrame 回调（如果 useStageSSE 支持），或在 for-await 中额外处理：
// 如果 KgSseFrame.type === 'stage_report_ready'，也触发 setShowReview(true)
```

**重跑回调：**
```tsx
const handleRerun = async (params: RerunParams) => {
  if (!file) return
  setRerunning(true)
  setShowReview(false)
  setApproved(false)
  await run(postKgStage1(file, false), {
    onLog: (msg) => setLogs(prev => [...prev, msg]),
    onResult: (data) => setResultFrame(data),
    onDone: async (success) => {
      if (success) {
        const p = await getKgStagePreview('bom', 0)
        setPreview(p)
        setShowReview(true)
      }
    },
  })
  setRerunning(false)
}
```

**在 UI 中，在结果摘要卡片下方条件渲染 StageReviewPanel：**
```tsx
{showReview && !approved && (
  <StageReviewPanel
    stageN={1}
    onApproved={() => { setApproved(true); onComplete?.() }}
    onRerun={handleRerun}
    rerunning={rerunning}
  />
)}
{approved && (
  <div className="mt-2 p-2 bg-green-950/30 border border-green-700 rounded text-green-400 text-sm">
    ✅ Stage 1 已放行
  </div>
)}
```

**在文件顶部新增 import：**
```tsx
import StageReviewPanel from './StageReviewPanel'
import { RerunParams } from './ParamTuner'
```

- [ ] **Step 2: 同样修改 Stage2Manual.tsx**

逻辑完全相同，只是：
- `stageN={2}`
- 调用 `postKgStage2(file)` 而非 `postKgStage1`
- `getKgStagePreview('manual', 0)`
- `onApproved` 中只调用 `onComplete?.()`（Stage 2 是最后一步）

- [ ] **Step 3: 构建检查**

```bash
cd "c:/xjp/代码/rag-demo/frontend"
npx tsc --noEmit 2>&1 | head -30
```

- [ ] **Step 4: 提交**

```bash
cd "c:/xjp/代码/rag-demo"
git add frontend/src/components/kg/stages/Stage1Bom.tsx frontend/src/components/kg/stages/Stage2Manual.tsx
git commit -m "feat(hitl): integrate StageReviewPanel into Stage1Bom and Stage2Manual"
```

---

## Task 13：端到端验证

**目标：** 按设计文档中的 7 个验证场景逐一验证。

- [ ] **Step 1: 启动后端**

```bash
cd "c:/xjp/代码/rag-demo"
PYTHONUTF8=1 "C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" -m uvicorn backend.main:app --reload --port 8000
```

- [ ] **Step 2: 启动前端**

```bash
cd "c:/xjp/代码/rag-demo/frontend"
npm run dev
```

打开 http://localhost:5173

- [ ] **Step 3: 验证场景 1 — 审阅面板自动展开**

1. 进入 KG 构建 → Stage 1 BOM
2. 上传 BOM 文件，点击运行
3. ✅ SSE 日志结束后，审阅面板自动展开
4. ✅ 「确认放行」按钮可见
5. ✅ 统计卡片显示实体数/三元组数

- [ ] **Step 4: 验证场景 2 — Stage 2 锁定**

1. Stage 1 未放行时，切换到 Stage 2 Tab
2. ✅ 上传按钮应禁用或有提示（根据实现）

> 注：若 KgStagesPanel 没有显式锁定逻辑，此步可跳过，以 `approved` state 控制 `onComplete` 为准。

- [ ] **Step 5: 验证场景 3 — LLM 诊断**

1. 在「问题清单」Tab 点击「生成 LLM 深度诊断」
2. ✅ 问题卡片下方出现紫色流式文字

- [ ] **Step 6: 验证场景 4 — 编辑三元组持久化**

1. 切换到「三元组编辑」Tab
2. 点击第一条三元组「编辑」，修改 head 字段，点保存
3. ✅ 修改立即显示
4. 刷新页面，重新进入同一 Tab
5. ✅ 修改已持久化（从 JSON 文件读取）

- [ ] **Step 7: 验证场景 5 — 领域知识干预**

1. 切换到「领域知识」Tab
2. 输入："第一级叶片和压气机盘通过燕尾槽连接"，点击提交
3. ✅ 出现 diff 预览（新增/修改/删除条目）
4. 点击「确认应用」
5. ✅ 「三元组编辑」Tab 中能看到新增的三元组

- [ ] **Step 8: 验证场景 6 — 中英对照切换**

1. 在「三元组编辑」Tab 切换显示模式按钮
2. ✅「仅英文」：只显示英文列
3. ✅「仅中文」：只显示中文译名列
4. ✅「中英对照」：双列显示

- [ ] **Step 9: 验证场景 7 — 确认放行**

1. 点击「✅ 确认放行 → Stage 2」
2. ✅ 面板消失，显示「Stage 1 已放行」绿色条
3. ✅ Stage 2 Tab 可以上传文件并运行

- [ ] **Step 10: 运行全套测试**

```bash
cd "c:/xjp/代码/rag-demo"
PYTHONUTF8=1 "C:/Users/Administrator/Miniconda3/envs/rag_demo/python.exe" -m pytest tests/kg/test_kg_storage_hitl.py tests/kg/test_kg_report.py tests/kg/test_kg_diagnose.py tests/kg/test_kg_translate.py tests/kg/test_hitl_endpoints.py -v
```

预期：全部 PASSED

- [ ] **Step 11: 最终提交**

```bash
cd "c:/xjp/代码/rag-demo"
git add -A
git commit -m "feat(hitl): complete HITL KG review system for Stage 1+2"
```
