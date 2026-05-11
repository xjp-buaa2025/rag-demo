# S2: 需求与约束分析 — 方法论

## 目的

把陛下在 S1 提的模糊目标（"可靠性优先 / 工艺优化"）转换成可量化的指标体系，识别关键尺寸特征（KC），并用 DFA 评分定位现有结构的装配瓶颈。S2 的产物是 S3 概念架构和 S4 详细工艺的需求追溯源头。

## 核心方法

### 1. QFD-轻量法（三栏映射）

把 QFD 经典的 House of Quality 简化为三栏映射，避免在 v1 阶段陷入完整 HoQ 矩阵：

| 栏目 | 含义 | 编号约定 | 必填字段 |
|------|------|---------|---------|
| `user_needs` | 客户声音（VOC） | U1, U2, ... | text + weight (1-5) |
| `engineering_metrics` | 工程指标 | M1, M2, ... | name + target + linked_needs |
| `assembly_features` | 装配可控特征 | F1, F2, ... | name + spec + linked_metrics |

**链路约束**：每个 user_need 至少被一个 engineering_metric 覆盖；每个 metric 至少被一个 assembly_feature 落地。LLM 自检时若发现孤儿 need，必须新增 metric 或显式标注 `uncertainty: 高` 让陛下补。

### 2. DFA 评分（Boothroyd-Dewhurst 轻量版）

完整 BD-DFA 需要每个零件的"手动装配时间"和"可调整位置数"，v1 不引入数值打分明细。改用**比值简化版**：

- 理论最小零件数 `theoretical_min_parts`：满足产品功能所必需的零件数。判定准则：移除该件后系统是否仍能完成主功能、是否仍能保持几何完整性、是否需要拆装。三个回答都为"否"即可计入理论最小集合。
- 实际零件数 `actual_parts`：从 S1 `kg_snapshot.part_count` + chamberlain 输入提取。
- 总分 `overall = theoretical_min_parts / actual_parts`，范围 [0, 1]。`>= 0.7` 视为良好，`< 0.5` 视为需重设计。
- 瓶颈件 `bottlenecks`：DFA 中"装配时间显著高于均值"或"需要专用工装才能装入"的零件，列出 `part_id + issue`。瓶颈件不影响 overall 数值，仅用于 S3/S4a 提醒。

### 3. KC 识别（决策树）

对每个 `assembly_feature`，问以下问题：

1. 该特征的离散是否会导致 `engineering_metric` 直接不达标？→ 是：候选 KC
2. 该特征是否覆盖在外场不可检测/不可调整？→ 是：升级为 high criticality
3. 该特征的公差链是否跨 ≥ 3 个零件？→ 是：标注 `criticality: high` 且必须在 S4c 做 stack-up

每个 KC 必须有 `target`（区间或单边阈值）、`criticality ∈ {high, medium, low}`、可选 `linked_features`。

### 4. 风险登记

风险来自三个源头：

| 源头 | 形式 |
|------|------|
| KG 失效模式（若已入库 FMEA） | 直接复制为 risk 条目 |
| KC 反推 | 每个 high-criticality KC 必须有至少 1 条对应 risk |
| chamberlain 输入 | 可在 HITL 指导意见里手添 |

每条 risk 字段：`id (R1, R2, ...)` / `text` / `severity (1-5)` / `linked_kcs`。

## 常见陷阱

- ❌ 把模糊形容词当 metric（如 "提高可靠性"——必须给 target 数字或区间）
- ❌ KC 列表只抄 Spec §2.2 示例不结合 S1 subject —— LLM 易犯
- ❌ DFA 评分编造（虚报 theoretical_min_parts）—— Prompt 必须强调"不确定时给区间或标 uncertainty: 高"
- ❌ 把 Web 搜索结果当 metric target 直接复制（GJB 写"高可靠"是定性词，不是数字）

## 产物质量自检 checklist

- [ ] `stage1_ref` 与 S1 scheme_id 一致
- [ ] 每个 user_need 至少链到一个 metric（无孤儿）
- [ ] 每个 metric 至少链到一个 assembly_feature
- [ ] 每个 high-criticality KC 至少链到一个 assembly_feature 与一条 risk
- [ ] `dfa_score.overall` ∈ [0, 1]，且 `theoretical_min_parts <= actual_parts`
- [ ] `risks` 数组非空，severity 字段都是 1-5 整数
- [ ] LLM 不确定时显式给 `uncertainty: 高/中/低`，不杜撰数字

## 留待 v2 完善

- 完整 BD-DFA 装配时间表格（每件 manual handling time / insertion time）
- FMEA-MEDA 数据接入（从 KG 中按 `failureMode` 关系自动建 risk 表）
- 客户需求权重的 AHP 推导（v1 直接由 chamberlain 指定 1-5）
