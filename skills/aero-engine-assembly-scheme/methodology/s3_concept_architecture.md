# S3: 概念 / 架构设计 — 方法论

## 目的

在 S2 指标与 KC 约束下，给出 **2-5 个备选概念架构**，每个含模块划分 + 关键接口 + 装配仿真预检 + 基准统一性审查 + 利弊。给出推荐项及理由。

S3 是从"我想要什么"到"系统长什么样"的关键跃迁。多备选是硬性要求——单一架构等于没做概念设计。

## 核心方法

### 1. 功能-结构映射

把 S2 的 `engineering_metrics` 当作功能需求列表，映射到物理结构：

| S2 source | 映射到 S3 字段 |
|-----------|--------------|
| `engineering_metrics.target` | 倒推该指标依赖的物理特征（如 MTBF→可单独更换的模块） |
| `assembly_features.spec` | 决定模块边界（同一 spec 内的零件归同一模块） |
| `key_characteristics.criticality:high` | 必须有独立装配检验工序 → 影响模块划分 |
| `risks.linked_kcs` | 决定关键接口的设计权重 |

### 2. 装配树推导（KG 驱动）

利用本地 KG 的 `isPartOf` / `matesWith` / `adjacentTo` 三种关系：

- **`isPartOf` 树**：直接给出现有模块拓扑——这是 baseline
- **`matesWith` 簇**：用图聚类（弱连接率 < 30%）切割得到候选模块边界
- **`adjacentTo` 链**：辅助识别装配顺序约束（不影响划分本身）

LLM 应基于 KG 输出 **多个**（≥ 2）切割方案。若 KG 中实体数 < 5，可标 `uncertainty: 高` 并给一个 baseline + 一个变体。

### 3. 装配仿真预检（v1 简化版）

V1 不接 DELMIA / Process Simulate，用**静态可达性 + 接口冲突计数**两个指标：

#### 可达性 `reachability_pass`（boolean）

判定规则：对每个模块 M，存在至少一条装配路径，使得 M 在被装入时其所有 `matesWith` 已就位的模块都不阻挡装入方向（轴向 / 径向之一）。判定时取 KG 中的 `matesWith` 关系当作硬约束。Pass = 所有模块通过；任意一个失败 → False。

#### 干涉计数 `interference_count`（integer ≥ 0）

V1 用 KG 启发：若架构中两个模块没有 `matesWith` 直接关系，但它们的零件集合存在 `adjacentTo` 关系（即"邻接但未配合"），且邻接零件距离 < 阈值（v1 暂用零件数 ≥ 2 作代理），计 1 处干涉。

`method` 字段填 `"KG-static"`（v1）或 `"CAD-occ"`（接入 STEP 文件后 v2 升级）或 `"placeholder"`（数据极不全时）。

### 4. 基准统一性审查

审查每个模块的"工艺基准 / 装配基准 / 检测基准"是否一致。简化规则：

- 若模块的"装配基准面"（与上级模块对接的物理面）等于"工艺基准面"（机加工时定位的面），则该模块 unified
- 任何一个模块不 unified → 整个架构 `datum_consistency.unified = false`，并在 `issues` 数组里写明哪个模块的哪种基准不一致

不一致不一定 PASS——它直接拉低 `fit_score_to_metrics` 0.1-0.2，但只要 chamberlain 接受可手动保留。

### 5. fit_score_to_metrics 评分

候选架构与 S2 engineering_metrics 的匹配度，[0, 1] 区间。计算策略（v1 启发式）：

| 因素 | 权重 | 检查 |
|------|------|------|
| 可达性 PASS | 0.3 | true → +0.3; false → +0.0 |
| 干涉计数 | 0.2 | 0 干涉 → +0.2; 每多 1 处 −0.05 |
| 基准统一 | 0.15 | unified=true → +0.15; false → +0.0 |
| KC 覆盖 | 0.2 | 每个 high-criticality KC 在该架构的 modules 内能被独立检测 → +0.04 |
| 维修性（MTTR）启发 | 0.15 | 模块数 3-5 之间 → +0.15; > 5 或 < 3 → +0.05 |

LLM 给出 fit_score 时必须能在 `rationale_md` 里说清楚拆解。

### 6. 推荐项与理由

`recommended` 必须是 candidate 中 fit_score 最高的之一。若有并列，可任选一个并在 `rationale_md` 写明。`rationale_md` 必须分项目对比 candidates，不要只罗列 pros/cons——而是相对评价。

## 常见陷阱

- ❌ 只给 1 个候选架构（违反概念设计多备选原则）
- ❌ 候选架构互为微改（如 A1 三段、A2 三段但把螺栓换成铆钉——必须有实质性区别）
- ❌ `assembly_simulation.reachability_pass=false` 仍然 recommend 该架构
- ❌ `datum_consistency.unified=false` 但 `issues=[]`（不一致必须能写出来）
- ❌ KG 数据严重不足时强行编造模块清单——必须 `uncertainty: 高` 且简化为 2 个 baseline 备选

## 产物质量自检 checklist

- [ ] `stage1_ref` 和 `stage2_ref` 与上游 scheme_id 一致
- [ ] `candidate_architectures` 至少 2 项
- [ ] 每个架构都有 modules / key_interfaces / assembly_simulation / datum_consistency / pros / cons / fit_score
- [ ] `recommended` 在 candidates 的 id 集合内
- [ ] `recommended` 的 fit_score >= 其他候选 fit_score
- [ ] `assembly_simulation.method` 在 enum 中
- [ ] `rationale_md` 至少分 3 行说明推荐理由
- [ ] KG 数据缺失时 `uncertainty: 高`，不杜撰

## 留待 v2 完善

- CAD-OCC 干涉检查（接 pythonocc）
- 装配仿真升级为 DELMIA / Process Simulate
- fit_score 转为正式 AHP / TOPSIS
- 公差链初步估算（与 S4c 衔接）
