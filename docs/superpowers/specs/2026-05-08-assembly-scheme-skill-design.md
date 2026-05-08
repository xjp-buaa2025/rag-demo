# 航空发动机装配方案设计 Skill —— 设计规格

> **版本**：v1.0（2026-05-08）
> **状态**：等待用户审定
> **目标读者**：实施工程师、论文 case study 作者
> **作者**：陛下 + 微臣（脑暴对话产出）

---

## 0. 摘要

本规格定义一个**学科智能体级别**的工作流——`aero-engine-assembly-scheme` skill——用于把现有 RAG/KG/CAD/BOM 工具，组装成"像航空发动机装配工艺师一样设计装配方案"的端到端能力。

**核心定位**：从单纯的工具堆叠，跃迁到"专家心智 + 工作流 + HITL + 自我生长"的领域智能体。

**首版示范标的**：PT6A 高压压气机（HPC）子系统（与现有黄金三元组集和 P&W 维修手册 72-30 章天然闭环）。

**关键设计参数**（脑暴定型）：

| 维度 | 选择 |
|------|------|
| 形态 | 底层 Skill markdown 定义方法论 + 前端 Stage 向导承载 HITL 与产物 |
| 任务定位 | 上下游贯通（概念初设 → 详细装配方案） |
| 阶段划分 | 5 阶段：S1 调研 / S2 需求 / S3 概念 / S4 详细工艺 / S5 评审 |
| HITL 粒度 | 双轨：直接编辑产物字段 + 自然语言指导意见 |
| 参考资料 | 预烘黄金模板 + 运行时 Web 搜索补充 + 用户审核反哺入库 |
| S4 拆分 | 4a 工序 / 4b 工装 / **4c 公差分配（可跳过）** / **4d 关键件控制（可跳过）** |

---

## 1. 整体架构

### 1.1 命名与定位

- **Skill 名称**：`aero-engine-assembly-scheme`
- **类型**：domain-workflow（领域工作流类 skill）
- **触发关键词**：装配方案、装配工艺规程、装配顺序设计、工装规划、QC 点设置
- **不触发场景**：单点工艺问题（用 RAG 即可）、KG 构建本身（用 KgBuilder）、整机总体设计

### 1.2 三层架构

```
┌────────────────────────────────────────────────────────────────┐
│ Layer 3: 前端 Stage 向导（用户交互层）                          │
│   AssemblySchemePage.tsx — 5 阶段卡片 + 双轨 HITL              │
│   每阶段：左侧产物编辑器 / 右侧"指导意见"对话框                │
└─────────────────────────┬──────────────────────────────────────┘
                          │ POST /assembly-design/stage{N}（SSE）
┌─────────────────────────▼──────────────────────────────────────┐
│ Layer 2: 阶段管道与工具调度（执行层）                           │
│   backend/pipelines/assembly_scheme/                           │
│     ├─ stage1_intake.py        需求采集 + Web 搜索补充          │
│     ├─ stage2_requirements.py  指标转化 + DFM/DFA + KC 识别     │
│     ├─ stage3_concept.py       架构/模块/接口推导 + 装配仿真    │
│     ├─ stage4a_procedures.py   工序总表与顺序                   │
│     ├─ stage4b_tooling.py      工装规划                         │
│     ├─ stage4c_tolerance.py    公差分配（可跳过）              │
│     ├─ stage4d_key_parts.py    关键件特殊控制（可跳过）        │
│     └─ stage5_review.py        三角色评审 + Markdown 导出       │
│   工具调度：rag_search / kg_query / cad_query / web_search     │
└─────────────────────────┬──────────────────────────────────────┘
                          │ 每阶段消费上一阶段 JSON 产物
┌─────────────────────────▼──────────────────────────────────────┐
│ Layer 1: Skill 文档（专家心智 source of truth）                 │
│   skills/aero-engine-assembly-scheme/                          │
│     ├─ SKILL.md            主入口（5 阶段 checklist + 决策图） │
│     ├─ methodology/        每阶段方法论（5 份 .md）            │
│     ├─ templates/          黄金模板（产物 JSON schema + 示范） │
│     ├─ references/         GJB/HB 标准摘要、PT6A 范例         │
│     └─ prompts/            每阶段 LLM 提示词（含 few-shot）   │
└────────────────────────────────────────────────────────────────┘
```

### 1.3 五条核心设计原则

1. **Skill 是 source of truth**：方法论、checklist、产物 schema、prompt 模板都长在 skill 文件夹里。Layer 2 的管道代码只负责"按 skill 指令调度工具"，不藏方法论。
2. **预烘 + 运行时补充**：`templates/` 里有"PT6A HPC 装配方案"完整范例 + 标准骨架；S1 联网检索补充该具体子系统的最新资料。
3. **双轨 HITL**：每个 Stage 卡片同时提供"结构化字段编辑"和"自然语言指导意见"两个入口，"指导意见"被作为 LLM 重新生成时的 system note 注入。
4. **5 阶段产物链**：每阶段产出一份 JSON 文件落到 `storage/assembly_schemes/{scheme_id}/stage{N}.json`，下阶段消费上阶段。中途退出可恢复。
5. **运行时反哺生长**：Web 搜索结果经用户审核后，可双向写入 `skill/references/`（方法论级）和 RAG 知识库（事实级），skill 随每次使用自我增强。

### 1.4 与现有系统的复用关系

| 现有能力 | 在此 skill 中的角色 |
|---------|-------------------|
| RAG 双路检索（bge-m3 + BM25） | S1/S4 检索 PT6A 手册具体段落 |
| KG 查询（Neo4j） | S3 查"压气机有哪些零件/接口"，S4 查"工序链" |
| CAD 查询（pythonocc） | S3 查"零件配合关系"，S4 推导"装配可达性" |
| Vision LLM（MiniMax） | S1 解析陛下上传的参考图片/手绘草图 |
| FallbackLLMClient | 各阶段生成与重生成 |
| LangGraph | Layer 2 的阶段内子流程（如 S4a 内部"工序生成→冲突检测→重排"） |
| Web 搜索（新增 Tavily 封装） | S1 资料补充、S5 评审时查"最佳实践" |

**新增唯一外部依赖**：`backend/tools/web_search.py`（封装 Tavily API；可降级 SearXNG 自建）。

### 1.5 运行时反哺机制（Web → 审核 → 入库）

#### 触发点
- **S1 资料采集**：批量触发，结果集中审核
- **任意阶段 HITL "指导意见"内**触发（如打"查一下 GJB 5060A 对叶片装配的最新条款"）：单次触发，弹窗审核

#### 审核 UI（复用 `<ItemReviewList>` 通用组件）
逐条选**目的地**（references / RAG / 两者 / 丢弃），可在线**编辑摘录**，自动记**审核日志** `storage/assembly_schemes/{scheme_id}/audit_log.json`。

#### 入库去向（双目的地）

| 目的地 | 适用 | 写入操作 |
|--------|------|----------|
| `skills/.../references/` | "通用方法论级"资料（标准条款、行业最佳实践、范例方案） | 写 markdown + SKILL.md 索引追加一行 |
| `data/web_corpus/{topic}/` → Qdrant + BM25 + KG | "具体事实级"资料（某型号参数、某 SB 内容） | 走现有 `/ingest/pipeline` 增量入库 |
| 都进 | 既是方法论又有具体事实 | 两者都执行 |

---

## 2. 5 阶段详细 Spec

每节统一格式：**目的 / 输入 / 工具与 Prompt / 产物 JSON / HITL 触发**。

### 2.1 S1 任务说明书 + 资料采集

**目的**：把陛下输入的"我要为 X 设计装配方案"翻译成结构化任务卡，并集中拉一次参考资料。

**输入**：
- 用户填写：目标对象（如 "PT6A HPC"）、设计意图（新设计 / 优化 / 复刻）、关键约束（成本/重量/可靠性优先级）、是否上传参考图/手绘
- 自动注入：本地 KG 已有的同名子系统摘要

**工具与 Prompt**：
1. `kg_query("PT6A HPC")` → 拉子系统已有零件/总成清单
2. `web_search` 三组查询（并发）：
   - `"装配工艺规程 + 子系统名 + GJB"` → 标准条款
   - `"<子系统英文名> assembly procedure"` → 国际范例
   - `"<具体型号> service bulletin assembly"` → 实物变更通告
3. `vision_describe`（可选）→ 解析陛下上传的草图
4. **新增**：适航/质量体系合规性预筛（识别 AS9100 / GJB 9001 适用条款）
5. LLM Prompt：基于以上素材生成"任务说明书"草案，含目标/范围/边界/约束/已知风险五栏

**产物 `stage1_intake.json`**：
```json
{
  "scheme_id": "scheme-20260508-001",
  "subject": {
    "system": "PT6A 高压压气机 HPC",
    "scope": ["3 级轴流 + 1 级离心", "含转子/静子/支撑环"],
    "design_intent": "工艺优化",
    "constraints": {"primary": "可靠性", "secondary": "维修性"}
  },
  "kg_snapshot": {"part_count": 35, "assembly_count": 13, "key_interfaces": [...]},
  "web_search_results": [
    {"id": "ws-1", "url": "...", "title": "GJB 5060A § 5.3", "excerpt": "...", "confidence": 0.9, "selected": null}
  ],
  "vision_notes": "用户草图显示 ...",
  "compliance_scope": ["AS9100D §8.1", "GJB 9001C §7.5"],
  "task_card_md": "## 任务说明书\n\n**对象**：PT6A HPC\n..."
}
```

**HITL 触发**：
- Web 搜索结果走"双目的地审核"
- `task_card_md` 整段可直接编辑，或对话框打指导意见

### 2.2 S2 需求与约束分析

**目的**：把模糊目标转换成可量化指标，识别关键尺寸特征（KC）和装配可制造性问题。

**输入**：`stage1_intake.json`

**工具与 Prompt**：
1. `rag_search("装配可靠性 指标")` + `references/methodology/s2_requirements.md`
2. **新增**：DFM/DFA 评分（Boothroyd-Dewhurst 法），输出可装配性评分 + 反馈给设计的整改清单
3. **新增**：关键尺寸链初步识别（哪些是 KC—Key Characteristic）
4. 可选 `kg_query` 检索同子系统历史失效模式（FMEA 资料若已入库）
5. LLM Prompt：用"客户需求 → 工程指标 → 装配可控特征"三栏映射表填表

**产物 `stage2_requirements.json`**：
```json
{
  "user_needs": [{"id": "U1", "text": "高可靠性", "weight": 5}],
  "engineering_metrics": [{"id": "M1", "name": "MTBF", "target": ">= 4000 hrs", "linked_needs": ["U1"]}],
  "assembly_features": [{"id": "F1", "name": "叶片装入扭矩一致性", "spec": "Cpk >= 1.33", "linked_metrics": ["M1"]}],
  "key_characteristics": [{"id": "KC1", "name": "叶尖间隙", "target_mm": "0.5-1.0", "criticality": "high"}],
  "dfa_score": {"overall": 0.72, "bottlenecks": [{"part_id": "P012", "issue": "定位面缺失"}]},
  "risks": [{"id": "R1", "text": "高温段间隙超差导致碰摩", "severity": 4}]
}
```

**HITL 触发**：三栏表格直接编辑、KC 列表增减、指导意见可触发"再补一条关于装配工时的约束"。

### 2.3 S3 概念 / 架构设计

**目的**：在指标约束下，给出"模块划分 + 关键接口 + 装配单元"的概念架构，并做装配仿真预检。

**输入**：`stage1` + `stage2`

**工具与 Prompt**：
1. `kg_query` 三连：① `isPartOf` 树 → 现有模块结构 ② `matesWith` / `hasInterface` → 关键配合 ③ `adjacentTo` → 空间约束
2. `cad_query`（可选，若有 STEP）→ 提取实际配合面
3. **新增**：装配仿真预检——基于 KG/CAD 的可达性分析与装配序列冲突检测
4. **新增**：基准统一性审查（工艺基准 / 装配基准 / 检测基准）
5. `rag_search("模块划分 装配单元")` → 拿方法论
6. LLM Prompt：综合上述生成"3-5 个备选概念架构"，每个含模块清单/接口表/优劣分析；推荐 1 个

**产物 `stage3_concept.json`**：
```json
{
  "candidate_architectures": [
    {
      "id": "A1",
      "name": "三段分体式（前段/转子段/后段）",
      "modules": [{"id": "M1", "name": "前段静子组件", "parts": ["P001", "P002"]}],
      "key_interfaces": [{"from": "M1", "to": "M2", "type": "法兰螺栓 + 定位销"}],
      "assembly_simulation": {"reachability_pass": true, "interference_count": 0},
      "datum_consistency": {"unified": true, "issues": []},
      "pros": ["拆装方便"],
      "cons": ["前段法兰应力集中"],
      "fit_score_to_metrics": 0.82
    }
  ],
  "recommended": "A1",
  "rationale_md": "..."
}
```

**HITL 触发**：陛下勾选最终架构（可不是推荐项）、模块合并/拆分编辑、指导意见可触发新增备选。

### 2.4 S4 详细装配工艺方案（拆 4 子模块）

前端 1 个 S4 卡片，内部 Tab 切换 4 子模块。**4c / 4d 设为可跳过阶段**——若数据不足可标记"未覆盖"，final.md 中明示。

#### 2.4.1 S4a 工序总表与顺序

**目的**：装配顺序、工序号、输入零件、输出总成。

**工具与 Prompt**：
1. `kg_query("Procedure WHERE 涉及 selected_modules")` → 现有手册工序模板
2. `kg_query("matesWith / adjacentTo")` → 推导装配可达性顺序
3. LLM Step A：生成装配工序总表

**产物 `stage4a_procedures.json`**：
```json
{
  "architecture_ref": "A1",
  "procedures": [
    {
      "seq_no": 1,
      "name": "前段静子叶片装入",
      "input_parts": ["P003", "P004"],
      "output_assembly": "M1-sub1",
      "predecessors": [],
      "duration_min": 25
    }
  ],
  "topology": {"edges": [["1","2"], ["2","3"]]}
}
```

#### 2.4.2 S4b 工装规划

**目的**：每道工序对应的工装清单（通用 + 专用）。

**产物 `stage4b_tooling.json`**：
```json
{
  "tooling": [
    {"id": "T1", "name": "叶片定位夹具", "type": "专用", "used_in_procedures": [1, 3]}
  ],
  "tooling_summary": {...}
}
```

#### 2.4.3 S4c 公差分配（可跳过）

**目的**：从最终关键尺寸（S2 KC）反推每道工序的公差分配。

**工具与 Prompt**：
1. `kg_query` + `cad_query` → 公差链上各零件 GD&T 信息
2. **新增**：Stack-up 分析（最坏情况 / RSS / 蒙特卡罗，依方法论 ASME B89.7.5）
3. LLM Prompt：生成每个 KC 对应的公差链 + 工序级公差分配

**产物 `stage4c_tolerance.json`**：
```json
{
  "skipped": false,
  "skip_reason": null,
  "stack_ups": [
    {
      "kc_id": "KC1",
      "kc_name": "叶尖间隙",
      "target_mm": "0.5-1.0",
      "method": "RSS",
      "chain": [{"part_id": "P003", "dim_id": "D1", "tol": "±0.02"}],
      "predicted_range_mm": "0.45-0.95",
      "feasible": true,
      "process_tol_allocation": [{"procedure_seq": 1, "feature": "...", "spec": "..."}]
    }
  ]
}
```

跳过时：`{"skipped": true, "skip_reason": "v1 未提供完整 GD&T 数据", "stack_ups": []}`

#### 2.4.4 S4d 关键件特殊控制（可跳过）

**目的**：转子动平衡 / 选配-配磨-配研 / 预紧力管理 / 关键件追溯 / FOD 控制。

**产物 `stage4d_key_parts.json`**：
```json
{
  "skipped": false,
  "skip_reason": null,
  "balancing": {"rotors": [{"id": "R1", "type": "刚性一阶", "spec_g_mm": 5.0, "method": "..."}]},
  "select_fitting": [{"id": "SF1", "parts": ["P011", "P020"], "method": "热套选配", "groups": 5}],
  "preload": [{"bolt_set": "B1", "torque_n_m": 50, "yield_factor": 0.6, "temp_correction": "..."}],
  "traceability_kcs": ["KC1", "KC3"],
  "fod_zones": [{"zone": "压气机进气段", "control_level": "A级"}]
}
```

跳过时：`{"skipped": true, "skip_reason": "v1 关键件数据待完善", "balancing": {}, ...}`

**HITL 触发（4 子模块共通）**：
- 工序总表拖拽排序、单工序展开后字段可改、指导意见触发局部重生成
- 跳过子模块时陛下需在卡片上明确点击"跳过此节"按钮，并填写跳过原因（写入 JSON）

### 2.5 S5 方案评审与导出

**目的**：让"虚拟评审委员会"给方案打分挑错，最终导出可送审的 Markdown / PDF。允许"评审 → 局部回 S4 重生成"循环。

**输入**：`stage1` + `stage2` + `stage3` + 全部 `stage4*`

**工具与 Prompt**：
1. **三角色评审**（LLM 多 persona，并行）：
   - **工艺工程师**：检查工序冲突、工装重复、QC 覆盖
   - **质量工程师**：检查 QC 点是否覆盖关键件、规范是否引用正确
   - **设计工程师**：检查方案是否回应 S2 的所有指标
2. `web_search`（按陛下指示触发）："最佳实践对比"
3. **新增**：追溯性矩阵生成（KC → 工序 → QC → 检验记录）
4. **新增**：虚拟试装迭代路径——评审发现问题可标记"回 S4a/S4b/S4c/S4d 重生成"
5. LLM Prompt：合并三角色意见 → 评审报告 + 整改建议

**产物 `stage5_review.json` + `final_scheme.md`**：
```json
{
  "review_panel": [
    {"role": "工艺工程师", "issues": [{"severity": "high", "text": "...", "linked": "stage4a.procedures[3]", "iterate_to": "stage4a"}]}
  ],
  "metrics_coverage": {"M1": "covered", "M2": "partial"},
  "kc_traceability_matrix": [{"kc_id": "KC1", "procedures": [1,3], "qcs": ["QC1","QC5"], "inspection": "..."}],
  "overall_score": 4.2,
  "recommendation": "approved_with_revision",
  "iterations": [{"ts": "...", "from_stage": "5", "to_stage": "4a", "reason": "..."}],
  "export_path": "storage/assembly_schemes/{id}/final_scheme.md"
}
```

**HITL 触发**：逐条采纳/拒绝评审意见、采纳的会回写到对应子阶段触发局部重生成、最终点"导出"生成完整 Markdown。

---

## 3. 前端 Stage 向导 UI

### 3.1 整体页面结构

新页面 `AssemblySchemePage.tsx`，挂在 App.tsx Accordion 第 5 项（KgViewer 之后）：

```
🏗️ 装配方案设计师
├── [新建方案 +]  下拉选择 [继续上次方案 ▼]
├── 任务进度条：S1 ▶─── S2 ──── S3 ──── S4 ──── S5
└── 当前阶段卡片（占整页主区域）
```

状态：
- **未启动**：仅显示"新建方案"输入框 + "开始"按钮
- **进行中**：当前阶段卡片 + 已完成阶段绿色实心 / 当前蓝色脉动 / 未完成灰色
- **已完成**：跳到 S5 评审视图，含"导出"按钮

### 3.2 Stage 卡片：双轨 HITL 内部结构

```
┌─────────────────────────────────────────────────────────────────┐
│ [Sx 阶段名]               状态：● 已生成 / ⏳ 生成中 / ✏️ 编辑中  │
├──────────────────────┬──────────────────────────────────────────┤
│  📄 产物编辑区        │  💬 指导意见                              │
│  （左 60%）           │  （右 40%）                                │
│                      │                                          │
│  - 结构化字段表格     │  历史对话气泡：user → assistant            │
│    可在线编辑         │                                          │
│  - 或 Markdown 编辑器 │  输入框：                                 │
│    （S1 / S5 适用）   │  [给出指导意见，Cmd+Enter 触发再生成 ▶] │
│                      │                                          │
│  字段联动：           │                                          │
│  - 改了某行 → 该行变橙 │                                          │
│  - "重新生成此行"按钮  │                                          │
├──────────────────────┴──────────────────────────────────────────┤
│  [⟲ 全文重新生成]  [💾 保存草稿]  [✓ 确认并推进下一阶段 →]      │
└─────────────────────────────────────────────────────────────────┘
```

**两个轨道交互细节**：
- **左轨道（直接编辑）**：陛下点单元格→变可编辑→失焦保存→该字段标记 `user_edited: true`，下次重生成会跳过它
- **右轨道（指导意见）**：陛下打字→Cmd+Enter→后端拿当前 JSON + 指导意见去重新生成 → 流式覆盖左轨道未被编辑的字段
- **冲突处理**：若指导意见会动到陛下手动改过的字段，弹小提示询问是否允许覆盖

### 3.3 状态机（每阶段独立）

```
[empty] ──"开始生成"──▶ [generating]
   ▲                        │
   │                        ▼
   │                    [editing] ◀──"指导意见"──┐
   │                        │                    │
   │                        ▼                    │
   └─"返回上阶段"──── [confirmed] ───"推进"──▶ 下一阶段
                            │
                            └──"全文重生成"──▶ [generating]
```

### 3.4 阶段间数据流转

- 后端：`POST /assembly-design/stage{N}` body `{scheme_id, action: "generate"|"regenerate"|"save_edits", payload}`，流式 SSE
- 前端 hook `useAssemblyDesign(scheme_id)` 管理整个方案的 `Map<stageNo, StageState>`
- 各阶段产物 JSON 存到 `storage/assembly_schemes/{scheme_id}/stage{N}.json` + 前端 sessionStorage（防刷新丢）

### 3.5 与 KgBuilder 的视觉一致性

| 元素 | 现有 KgBuilder | 本页复用 |
|------|---------------|---------|
| 三栏卡片配色 | 文件类别 | 改为阶段配色：S1蓝/S2绿/S3紫/S4橙/S5红 |
| `<ItemReviewList>`（新抽出） | KG 实体审核 | Web 搜索结果审核 |
| SSE 日志气泡 | 入库进度 | 阶段内 LLM 思考流（thinking → tool_call → result） |
| 数据源徽章 | Neo4j 状态 | RAG/KG/CAD/Web 四个数据源连通指示灯 |

### 3.6 Web 搜索审核浮窗

S1 阶段下方触发后，卡片下方展开 `<ItemReviewList>`（不是新页面），陛下边看产物边审核。S2-S5 通过指导意见触发的 web search 用 Toast 风格弹窗审核。

---

## 4. Skill 文档结构与专家心智内容

### 4.1 文件夹布局

```
skills/aero-engine-assembly-scheme/
├── SKILL.md                           # 主入口（frontmatter + checklist + 决策图）
├── methodology/                       # 专家心智（5 份，每阶段 1 份）
│   ├── s1_intake_and_research.md
│   ├── s2_requirements_qfd.md
│   ├── s3_concept_architecture.md
│   ├── s4_detailed_process.md         # 涵盖 4 子模块的方法论合集
│   └── s5_review_and_export.md
├── templates/                         # 产物 schema + 黄金范例
│   ├── schemas/
│   │   ├── stage1.schema.json
│   │   ├── stage2.schema.json
│   │   ├── stage3.schema.json
│   │   ├── stage4a.schema.json
│   │   ├── stage4b.schema.json
│   │   ├── stage4c.schema.json        # 含 skipped/skip_reason 字段
│   │   ├── stage4d.schema.json        # 含 skipped/skip_reason 字段
│   │   └── stage5.schema.json
│   └── golden/
│       ├── pt6a_hpc_stage1.json
│       ├── pt6a_hpc_stage4a.json      # 8-12 道工序的精譔示范
│       ├── pt6a_hpc_stage4b.json
│       └── pt6a_hpc_final.md
├── references/                        # 标准/规范/范例摘要库（运行时反哺写入）
│   ├── standards/
│   │   ├── gjb_5060a_excerpt.md
│   │   ├── as9100d_excerpt.md
│   │   ├── asme_y14_5_gd_t.md
│   │   ├── asme_b89_7_5_stack_up.md
│   │   ├── nas_fastener_specs.md
│   │   └── _index.md                  # 自动维护的索引
│   ├── case_studies/
│   │   ├── pt6a_72_30_summary.md
│   │   └── _index.md
│   └── _ingest_log.json               # 反哺写入审计日志
└── prompts/                           # 5 阶段 LLM Prompt 模板（含 few-shot）
    ├── s1_intake.prompt.md
    ├── s2_requirements.prompt.md
    ├── s3_concept.prompt.md
    ├── s4a_procedures.prompt.md
    ├── s4b_tooling.prompt.md
    ├── s4c_tolerance.prompt.md
    ├── s4d_key_parts.prompt.md
    └── s5_review.prompt.md
```

### 4.2 SKILL.md 主入口（范例）

```markdown
---
name: aero-engine-assembly-scheme
description: 用于设计航空发动机子系统装配方案的端到端工作流。触发时机：
  用户提出"为 X 设计装配方案 / 装配工艺 / 装配规程"、"做装配方案设计"、
  或在装配/工艺工程语境下提出方案级问题。包含 5 阶段方法论
  （任务调研→需求分析→概念设计→详细工艺→评审导出），双轨 HITL，
  Web 反哺。范围聚焦子系统级（如 PT6A HPC），不处理整机总体设计。
type: domain-workflow
target_subsystem_default: PT6A HPC
version: 1.0
---

## 触发与不触发

**触发**：装配方案、装配工艺规程、装配顺序设计、工装规划、QC 点设置
**不触发**：单点工艺问题（去查 RAG）、KG 构建本身（去用 KgBuilder）、整机总体设计

## 核心 Checklist（5 阶段）

每阶段都必须做：
- [ ] 读取上一阶段 JSON（S1 除外）
- [ ] 调用对应 methodology/sN_*.md 作为方法论上下文
- [ ] 按 prompts/sN_*.prompt.md 模板执行
- [ ] 产物校验通过 templates/schemas/stageN.schema.json
- [ ] HITL 暂停，等待用户编辑或指导意见
- [ ] 用户确认后写入 storage/assembly_schemes/{scheme_id}/stageN.json

## 决策图

\`\`\`dot
digraph assembly_scheme {
  "用户提需求" -> "S1 任务调研";
  "S1 任务调研" -> "Web 搜索结果审核";
  "Web 搜索结果审核" -> "skill references/" [label="是"];
  "Web 搜索结果审核" -> "RAG 知识库" [label="是"];
  "S1 任务调研" -> "S2 需求分析";
  "S2 需求分析" -> "S3 概念设计";
  "S3 概念设计" -> "用户选定架构";
  "用户选定架构" -> "S4a 工序总表";
  "S4a 工序总表" -> "S4b 工装规划";
  "S4b 工装规划" -> "S4c 公差分配?" [label="数据足"];
  "S4b 工装规划" -> "标记跳过 S4c" [label="数据不足"];
  "S4c 公差分配?" -> "S4d 关键件控制?";
  "标记跳过 S4c" -> "S4d 关键件控制?";
  "S4d 关键件控制?" -> "S5 三角色评审";
  "S5 三角色评审" -> "评审通过?" [label="否，回 S4* 局部重生成"];
  "S5 三角色评审" -> "导出 final_scheme.md" [label="是"];
}
\`\`\`

## 关键反模式

- ❌ 跳过 S2 直接出工序：会丢失需求追溯，QC 覆盖不全
- ❌ 在 S3 只给 1 个架构：违反"概念设计需多备选"原则
- ❌ S4a 一次性生成全部工序展开：token 爆炸 + 工序间冲突
- ❌ 把 Web 搜索结果直接当事实写入产物：必须先经审核
- ❌ S4c/S4d 数据不足却强行编造：必须明确标记 skipped + skip_reason
```

### 4.3 methodology/ 每节大纲

每份 markdown 含 4 部分：
1. **该阶段的目的与关键产物**
2. **核心方法（带学科出处）**：
   - S2：QFD-轻量、Boothroyd-Dewhurst DFA、KC 识别
   - S3：功能-结构映射 + 装配树推导、装配仿真预检
   - S4a：Mickey Mouse 装配序列法 + DFA 启发式
   - S4b：通用工装库 + 专用工装设计原则
   - S4c：ASME B89.7.5 stack-up（最坏情况 / RSS / 蒙特卡罗）
   - S4d：动平衡（一阶/二阶刚性 vs 柔性）、选配/配磨/配研、预紧力（屈服扭矩 + 椭圆系数 + 温度修正）、AS9100 追溯性、FOD 控制
   - S5：FMEA 简版 + 三角色评审范式
3. **常见陷阱与判别方法**
4. **产物质量自检 checklist**

### 4.4 templates/golden/pt6a_hpc_*.json

人工精譔 + 系统验证过的 PT6A HPC 装配范例，含完整 8-12 道工序示范。同时是：
- LLM few-shot 学习样本
- JSON Schema 的"正例"
- 论文里"系统能力上限"的展示物

由微臣依据陛下手上的 P&W 3013242 手册 72-30 章 + 黄金三元组集（108 实体 / 99 三元组）合成首版，然后陛下校核。**v1 提供两份**：
- `pt6a_hpc_stage4_full.json`：完整含 4c/4d
- `pt6a_hpc_stage4_skipped.json`：4c/4d 标记跳过的版本（演示"数据不足时的优雅降级"）

### 4.5 prompts/sN_*.prompt.md 模板

统一结构：
```markdown
# System
你是航发装配工艺专家，正在执行装配方案设计 skill 的第 X 阶段。

## 方法论上下文
{{include: methodology/sX_*.md}}

## 必须遵守
1. 输出严格符合 templates/schemas/stageX.schema.json
2. 每个事实性陈述必须可追溯到 references/ 或 KG/RAG 检索结果
3. 不确定时输出 "uncertainty": 高/中/低 字段，不杜撰
4. 引用文献用 [ref:standard_id 或 chunk_id] 格式

## Few-shot
### 输入示例
{{include: templates/golden/pt6a_hpc_stageX 的输入对应部分}}
### 期望输出
{{include: templates/golden/pt6a_hpc_stageX.json}}

## 当前任务
- 上阶段产物：{prev_stage_json}
- 用户指导意见（若有）：{user_guidance}
- 检索到的资料：{retrieved_chunks}

请生成本阶段产物。
```

### 4.6 Skill 加载机制（双入口）

**入口 A — Claude Code / Agent 端自动触发**：通过 SKILL.md frontmatter 的 `description` 被 Claude 系统判断"是否相关"，命中后自动加载。

**入口 B — 前端 Stage 页面手动**：陛下打开 AssemblySchemePage 即视为显式调用。后端 `assembly_scheme/` 管道始终把 SKILL.md + 当前阶段对应的 methodology / prompts 文件加载到 LLM 调用的 system message。

两个入口共享同一份 skill 文件——确保"用 chat 问"和"用前端走"得到一致的方法论。

### 4.7 反哺机制对 skill 的具体写入

`references/_ingest_log.json` 记录每条反哺写入：
```json
{
  "ts": "2026-05-08T14:32:00",
  "scheme_id": "scheme-20260508-001",
  "stage": 1,
  "source_url": "...",
  "target": "references/standards/gjb_5060a_chap5.md",
  "user_edit_diff": "...",
  "approved_by": "用户"
}
```

`references/standards/_index.md` 自动重排，按"被引用次数 / 最近写入时间"排序，下次跑 skill 时优先注入热门条目（避免 token 爆炸）。

### 4.8 参考资料清单（v1 预烘）

#### 国内核心
- GJB 5060A-2014《航空发动机装配通用要求》
- GJB 9001C-2017《质量管理体系要求》
- HB/Z 9-2009《航空发动机制造工艺与材料学》
- HB 5354《航空发动机用螺栓》、HB 6586《装配通用规范》等
- 《航空发动机设计手册》第 19 册（装配工艺）
- 《航空发动机设计手册》第 7 册（疲劳寿命）
- 《航空发动机制造技术》（刘大响主编）
- 《航空燃气涡轮发动机结构与设计》（陈光，北航）
- **陛下手上**：《航空发动机故障诊断》（邓明、金业壮）—— 反推装配缺陷模式

#### 国际核心
- AS9100D / AS9145
- NAS（National Aerospace Standards）系列
- **ASME Y14.5-2018**《Dimensioning and Tolerancing》
- **ASME B89.7.5**《Tolerance Stack-up Analysis》
- MIL-HDBK-727《Design Guidance for Producibility》
- ARP4754A
- Boothroyd-Dewhurst DFA Methodology

#### 经典教材/手册
- 《Aircraft Engine Design》（Mattingly, Heiser, Pratt）
- 《Gas Turbine Engineering Handbook》（Boyce）
- 《Aircraft Engine Component Maintenance Manual》（Treager）

#### 公开数据库（联网搜索定向）
- NTRS（NASA Technical Reports Server）
- DTIC
- EASA Type Certificate Data Sheets
- CNKI 知网

---

## 5. 落地步骤与文件清单

### 5.1 文件清单（新增）

```
rag-demo/
├── skills/                                          # 全新顶层目录
│   └── aero-engine-assembly-scheme/                 # （详见 §4.1 完整布局）
│
├── backend/
│   ├── pipelines/
│   │   └── assembly_scheme/                         # 新增管道目录
│   │       ├── __init__.py
│   │       ├── skill_loader.py
│   │       ├── stage1_intake.py
│   │       ├── stage2_requirements.py
│   │       ├── stage3_concept.py
│   │       ├── stage4a_procedures.py
│   │       ├── stage4b_tooling.py
│   │       ├── stage4c_tolerance.py
│   │       ├── stage4d_key_parts.py
│   │       ├── stage5_review.py
│   │       └── reflux.py
│   ├── routers/
│   │   └── assembly_design.py                       # 新增端点（详见 §5.3）
│   └── tools/
│       └── web_search.py                            # 新增（封装 Tavily）
│
├── frontend/src/components/
│   └── assembly_scheme/                             # 新增组件目录
│       ├── AssemblySchemePage.tsx
│       ├── StageCard.tsx
│       ├── StageProgressBar.tsx
│       ├── DualTrackHITL.tsx
│       ├── ItemReviewList.tsx
│       ├── stages/
│       │   ├── Stage1Intake.tsx
│       │   ├── Stage2Requirements.tsx
│       │   ├── Stage3Concept.tsx
│       │   ├── Stage4Process.tsx                    # 含 4 个子 Tab
│       │   └── Stage5Review.tsx
│       └── exporters/
│           └── MarkdownExporter.tsx
│
└── storage/
    └── assembly_schemes/                            # 各方案产物落地
        └── {scheme_id}/
            ├── stage1.json ... stage5.json
            ├── audit_log.json
            └── final_scheme.md
```

### 5.2 现有文件修改清单

| 文件 | 改动 |
|------|------|
| `backend/main.py` | lifespan 加载 skill 目录到 `state.skill_registry`；注册 `assembly_design` 路由 |
| `backend/state.py` | `AppState` 加 `web_search_client` / `skill_registry` / `assembly_lock` 字段 |
| `backend/langchain_components/tools.py` | 新增 `@tool web_search`（第 7 个工具）|
| `frontend/src/App.tsx` | Accordion 加第 5 项"🏗️ 装配方案设计师" |
| `frontend/src/api/client.ts` | 加 `postAssemblyStage` / `getSchemeList` / `resumeScheme` 等方法 |
| `frontend/src/types/index.ts` | 加 `AssemblyScheme` / `StageState` / `ReviewItem` 等类型 |
| `frontend/src/components/kg/stages/StageReviewPanel.tsx` | 抽出通用 `<ItemReviewList>` 共用 |
| `requirements.txt` | 加 `jsonschema`、`tavily-python` |
| `frontend/package.json` | 加 `ajv`（前端 schema 校验，可选）|
| `.env.example` | 加 `TAVILY_API_KEY` 配置项 |
| `PROJECT_GUIDE.md` | 新增第 16 节"Assembly Scheme Skill" |

### 5.3 后端新增端点（7 个）

| 端点 | 方法 | 功能 |
|------|------|------|
| `POST /assembly-design/scheme/new` | POST | 创建方案，分配 scheme_id |
| `GET /assembly-design/scheme/list` | GET | 列出已有方案 |
| `GET /assembly-design/scheme/{id}` | GET | 获取某方案全部阶段产物 |
| `POST /assembly-design/scheme/{id}/stage/{stage_key}` | POST + SSE | 生成/重生成/保存某阶段。`stage_key ∈ {"1", "2", "3", "4a", "4b", "4c", "4d", "5"}`，共 8 个子阶段 |
| `POST /assembly-design/scheme/{id}/reflux` | POST | 提交 web 搜索审核结果，触发反哺入库 |
| `POST /assembly-design/scheme/{id}/iterate` | POST | S5 评审采纳 → 触发 S4a/4b/4c/4d 局部重生成（body 含 `target_stage_key`） |
| `GET /assembly-design/scheme/{id}/export` | GET | 下载 final_scheme.md（或后续 PDF） |

**stage_key 取值约定**（贯穿整个文档）：
- `"1"` / `"2"` / `"3"` / `"5"`：对应 §2.1-2.3 / §2.5
- `"4a"` / `"4b"` / `"4c"` / `"4d"`：对应 §2.4.1-2.4.4
- 文件落地：`storage/assembly_schemes/{id}/stage{stage_key}.json`（如 `stage4a.json`）
- Schema 文件：`templates/schemas/stage{stage_key}.schema.json`
- Prompt 文件：`prompts/s{stage_key}_*.prompt.md`

### 5.4 关键依赖与外部服务

- **Web 搜索**：默认 **Tavily**（免费 1000 次/月，AI 友好 API）；失败降级 SearXNG 自建（可选）
- **JSON Schema 校验**：`jsonschema` (Python)
- **PDF 导出**（可选 v2）：pandoc CLI

### 5.5 分 6 个 Phase 实施

| Phase | 内容 | 交付物 | 预计时长 |
|-------|------|--------|---------|
| **P1 Skill 骨架** | SKILL.md + 8 schemas + 5 methodology 大纲 + Web 搜索工具封装 | skill/ 目录可被加载、`web_search` 工具可调用 | ~1 天 |
| **P2 后端管道 v0** | skill_loader + stage1_intake + assembly_design 路由 + 一份 PT6A HPC 半成品 golden 范例 | S1 端到端可跑通：上传任务→Web 搜索→生成 task_card | ~1.5 天 |
| **P3 后端 S2-S5** | 实现剩余 stage2/3/4(4a-4d)/5 + reflux 反哺逻辑 + 全部 prompts | 后端能从 S1 一路串到 S5 出 final.md | ~3 天 |
| **P4 前端向导** | AssemblySchemePage + StageCard + DualTrackHITL + 5 个 stages 视图 | 前端能完整跑完一个方案 | ~3 天 |
| **P5 PT6A HPC 黄金范例完整化** | 微臣依据手册 + 黄金三元组合成 v1 完整范例（full + skipped 两版）；陛下校核 | `templates/golden/pt6a_hpc_*` 完整 | ~1.5 天（含校核） |
| **P6 反哺审核 UI + 论文 case study** | ItemReviewList 抽出 + 反哺审核浮窗 + final.md → PDF 导出（可选）+ 写一段论文 case study 草稿 | 论文里能放进 case study 章节 | ~2 天 |

总工期：**~12 天**。

### 5.6 与现有系统的安全衔接

- **Lifespan 加载**：skill 目录在 backend 启动时一次性读入 `state.skill_registry`（dict），失败则降级——assembly 端点返回 503，**不影响其他模块**
- **数据隔离**：所有方案产物落 `storage/assembly_schemes/`，与现有 Qdrant / Neo4j / KG 无写交叉，仅有"反哺审核通过后"才往 RAG/skill 写入
- **配置可选**：未配置 Tavily key 时，`web_search` 工具返回提示性错误，S1 仍可用本地数据跑通（仅缺 web 资料补充）
- **数据库无新增表**：所有新数据走文件系统 + Neo4j MERGE（反哺时与现有 KG 合并）
- **回滚成本**：删除 `skills/`、`backend/pipelines/assembly_scheme/`、`backend/routers/assembly_design.py`、`frontend/src/components/assembly_scheme/` + 还原 6 处现有文件改动 = 完全回滚

---

## 6. 风险与未决事项

### 6.1 已识别风险

| 风险 | 缓解 |
|------|------|
| Tavily 配额 1000 次/月对论文实验可能不够 | 加 `web_search` 缓存层（按 query hash 缓存到 `storage/web_cache/`） |
| 黄金范例（PT6A HPC v1 完整）合成需要大量手册细读 | P5 阶段陛下与微臣分工：微臣从手册 + 黄金三元组生成草稿，陛下校核 |
| 前端 Stage 卡片 4c/4d 子 Tab 可跳过的 UX 设计 | 用清晰的"跳过"按钮 + 必填的"跳过原因"表单，避免误跳 |
| LLM 在 S4c/S4d 编造数据 | Prompt 严控 + JSON Schema 校验 `skipped` 字段 + 拒绝包含 `[FABRICATED]` 标签的输出 |
| 反哺写入 RAG 时与现有数据冲突 | 走现有 `/ingest/pipeline` 路径，由 `doc_id` 唯一性保证幂等 |

### 6.2 v1 不做（推迟到 v2+）

- PDF 导出（v1 仅 Markdown）
- 装配仿真的高保真版本（v1 只做 KG/CAD 静态可达性分析）
- 多语言支持（v1 仅中文）
- 多用户协作（v1 单用户）
- 反哺写入的回滚机制（v1 仅 append-only）

### 6.3 等待陛下决策的细节

P5 黄金范例校核时，是否需要陛下：
- 提供另一份内部资料补充手册细节？
- 接受微臣"基于公开手册 + 领域知识"合成版本（明确标记数据来源）？

此点不阻塞 P1-P4 启动，留待 P5 前再确认。

---

## 7. 附：与论文章节的映射

本 skill 实现后，可作为论文以下章节的支撑：

| 论文章节 | 对应 skill 部分 |
|---------|----------------|
| §3 系统架构 — 增加"学科智能体层" | Layer 1（Skill 文档）+ Layer 2（管道调度）|
| §3.x 知识图谱应用 | S3/S4a 中 KG 查询的具体调用 |
| §4 实验与 case study | P5 PT6A HPC 黄金范例 + 实际跑一遍方案 |
| §4.x 人机协作分析 | audit_log.json 提供的反哺审核量化数据 |
| §5 讨论 — 学科智能体的可演进性 | 反哺机制 + version log |

---

**文档结束。等待陛下审定后转 writing-plans 制定实施 plan。**
