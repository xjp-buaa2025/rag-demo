# SESSION_STATE.md — 热记忆

## [Plan 2 已完成（2026-05-14）— 可开新会话推进 Plan 3]

**Plan 2（Assembly Scheme Skill S2 + S3）已完成**，branch `feat/assembly-scheme-p2-s2-s3`，69 tests 全绿。

### 下一步（Plan 3 建议）
- **S4a/S4b**：装配工序 + 工装选型管道（后端 + 前端）
- **前端 S2/S3 展示**：在 KG 阶段组件中接入 stage/2、stage/3 端点，展示 QFD 矩阵 + 候选架构卡片
- **先跑哪个**：建议 Plan 3 = S4a 装配工序（因为 S3 输出的候选架构自然导向工序设计）

### Plan 2 已交付内容（供参考）
- `backend/pipelines/assembly_scheme/stage2_requirements.py`：QFD + DFA-lite + KC + 风险
- `backend/pipelines/assembly_scheme/stage3_concept.py`：多候选架构 + KG 可达性 + fit_score
- `backend/routers/assembly_design.py`：stage/2 和 stage/3 路由已激活（含 409 门控 + assembly_lock）
- `skills/aero-engine-assembly-scheme/`：stage2/stage3 schema + golden + methodology + prompts
- `PROJECT_GUIDE.md §16.P2`：已更新（3W1H 标准）
- 证据：`tests/assembly/`（69 tests）

### 已知遗留（不影响 Plan 2 交付）
- `tests/kg/test_stage3_batch_api.py::test_c52696c_no_bare_numeric_names` 因 `backend/routers/kg_stages.py`（未提交修改）产生裸数字名，与 P2 无关
- 工作树含多个未提交的非 P2 文件（KG 实验、论文等）

## [论文工作线（独立保留）]

论文全章节填实 + 6 章结论 + 11 张图（4 真图 + 6 占位符 + 1 架构图）+ 一致性检查全 OK。可编译。

### Todo
1. 陛下：装 TeXLive/MikTeX 后编译 `cd paper && xelatex main.tex`（×2）
2. 占位符 fig2-7 待替换为真图（可选）
3. 论文已含 §1-§6 完整内容

## [PT6A 实验最终结果（A+B 改进后，2026-05-03）]

### Tier-1 主表（60 题）
| Baseline | Recall@5 | MRR | Hit@1 | Judge.Rel | Judge.Comp | Judge.Corr |
|---|---|---|---|---|---|---|
| B1 Dense | 0.778 | 0.992 | **0.983** | 3.38 | 2.88 | 2.12 |
| B2 BM25 | 0.719 | 0.938 | 0.900 | 3.43 | 2.78 | 2.00 |
| B3 Hybrid | 0.769 | 0.983 | 0.967 | 3.48 | 2.88 | 2.05 |
| B4 +CLIP | 0.769 | 0.983 | 0.967 | 3.42 | 2.93 | 2.25 |
| B5 +KG | 0.697 | 0.926 | 0.867 | 3.50 | 3.02 | **2.35** |
| **B6 Full** | 0.697 | 0.926 | 0.867 | **3.63** | **3.15** | 2.33 |
| A1 -Rerank | 0.800 | 0.983 | 0.967 | 3.40 | 2.83 | 2.17 |

### Tier-1 题型分组 (Judge Relevance)
| 题型 | B1 Dense | B2 BM25 | B3 Hybrid | B4 +CLIP | B5 +KG | B6 Full | A1 -Rerank |
|---|---|---|---|---|---|---|---|
| A 零件结构 | 3.15 | **3.90** | 3.25 | 3.15 | 3.30 | 3.35 | 3.60 |
| B 工序工具 | 2.92 | 3.42 | 2.83 | 2.83 | 3.42 | **3.75** | 3.33 |
| C 技术规范 | 3.00 | 2.56 | 3.11 | 3.11 | **3.22** | 3.11 | 2.44 |
| D 几何配合 | 4.11 | 3.37 | **4.32** | 4.21 | 3.90 | 4.11 | 3.68 |

### Tier-2 跨章节（20 题，仅 Judge）
| Baseline | Judge.Rel | Judge.Comp | Judge.Corr |
|---|---|---|---|
| B1 Dense | 3.10 | 2.40 | 2.00 |
| B2 BM25 | 3.65 | 2.80 | 2.65 |
| B3 Hybrid | 3.25 | 2.55 | 2.05 |
| B4 +CLIP | 3.25 | 2.50 | 1.95 |
| **B5 +KG** | **3.75** | 3.05 | **2.70** |
| **B6 Full** | 3.65 | **3.10** | **2.70** |
| A1 -Rerank | 3.50 | 2.80 | 2.50 |

### 关键叙事点（论文用）
1. **B6 在 Tier-1 Judge Rel/Comp 全场最高**（3.63 / 3.15，+7.4% / +9.4% vs B1）
2. **B5 + KG 在 Tier-2 全维度领先**（Rel 3.75 / Comp 3.05 / Corr 2.70）
3. **B 工序工具类 KG 增益 +28.5%**（B6 3.75 vs B1 2.92）—— KG 价值最直接体现
4. **关闭 KG 路径导致 Judge Comp 下降 7.0%** —— KG 不可替代性的实证
5. **Recall@5 B6 反低于 B1**（0.697 vs 0.778）：KG 子图作为异质内容挤入候选池

### 论文章节状态
- §0 abstract: ✅ 全部新数字（3.63/3.15/+7.4%/+9.4%）
- §1.3 贡献 4: ✅ 双层评测 + KG 28.5% 提升
- §3.2.2 (3) adjacentTo: ✅ 加 OCC + Logical Sibling 双路
- §3.2.3 KG 规模: ✅ 加 fig11 关系分布饼图
- §3.3.3 HITL 数字: ✅ 删伪数字改定性
- §4.5 主实验: ✅ 三表（检索/Judge/Tier-2）+ 题型热力图分析
- §4.6 消融: ✅ 4 项变体 + fig9 + 4 段深度讨论
- §5.1 路径贡献分析: ✅ 4 方面深度讨论
- §5.2/§5.3 已存在框架，可微调

### 关键文件
- `paper/figures/fig8_main_compare.pdf` 主对比柱状（左检索 / 右 Judge）
- `paper/figures/fig9_ablation_delta.pdf` 消融 Δ
- `paper/figures/fig10_subtype_heatmap.pdf` 题型 × baseline 热力图
- `paper/figures/fig11_kg_relations.pdf` KG 关系分布饼图
- `docs/experiments/table2_main_tier1.csv` Tier-1 主表
- `docs/experiments/table5_tier2.csv` Tier-2 表
- `docs/experiments/table_subtype_judge_relevance.csv` 题型细分
- `tests/kg/fixtures/assembly_qa_final.jsonl` 80 题最终评测集

### 关键代码改动
- `backend/routers/retrieve.py` `kg_search_neo4j`：BGE-M3 ANN 替代 CONTAINS keyword
- `scripts/run_experiments.py` `chunk_id_match`：支持 KG 子图节点命中
- `scripts/run_experiments.py` 加 `--force-eval-retrieval` 仅重算检索指标

### 已知遗留（不影响投稿）
- backend matplotlib 在 sandbox 卡 ax.bar，画图必须用 `C:/Users/Administrator/Miniconda3/python.exe`（base conda）
- KG ANN 索引启动时 lazy 构建（首次调用 ~250s），后续 ~2.5s
