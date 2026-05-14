# SESSION_STATE.md — 热记忆

## [Plan 4 已完成（2026-05-14）— 可开新会话推进 Plan 5]

**Plan 4（Assembly Scheme Skill S4b 工装选型）已完成**，branch `feat/assembly-scheme-p2-s2-s3`，88 tests 全绿。

### 已交付内容
- `backend/pipelines/assembly_scheme/stage4b_tooling.py`：工装去重提取 + KG 查询 + LLM 生成 + 四层降级保险 + `_cross_validate()` 交叉引用完整性校验
- `skills/aero-engine-assembly-scheme/templates/schemas/stage4b.schema.json`：正式 schema（tools/dfa_tooling_score/tooling_constraints）
- `skills/aero-engine-assembly-scheme/prompts/s4b_tooling.prompt.md`：S4b LLM 提示词
- `backend/routers/assembly_design.py`：stage/4b 路由激活（依赖 stage4a，否则 409）
- `PROJECT_GUIDE.md §16.P4`：已更新（3W1H 标准）
- 证据：`tests/assembly/`（88 tests，含 8 个 S4b 单元测试 + S4b 路由 E2E 测试）

### 下一步建议（Plan 5 选项）
1. **S4c 公差与配合分析**：基于 S4b 工装清单，分析各工序的公差链和配合精度要求
2. **S4d 工时与成本估算**：基于 S4a 工序链 + S4b 工装，估算各工序工时和装配成本
3. **前端 S2/S3/S4a/S4b 展示**：在 KG 阶段组件中接入 assembly-design 端点，展示工装清单 + DFA 得分
4. **KG 诊断计划（已有诊断报告）**：按 bubbly-chasing-pizza.md P0 实施 docx BOM 解析器

### 已知遗留（不影响 P4 交付）
- `tests/kg/test_stage3_batch_api.py::test_c52696c_no_bare_numeric_names` 与 P4 无关
- 工作树含多个未提交的非 P4 文件（KG 实验、论文等）

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

### 关键叙事点（论文用）
1. **B6 在 Tier-1 Judge Rel/Comp 全场最高**（3.63 / 3.15，+7.4% / +9.4% vs B1）
2. **B5 + KG 在 Tier-2 全维度领先**（Rel 3.75 / Comp 3.05 / Corr 2.70）
3. **B 工序工具类 KG 增益 +28.5%**（B6 3.75 vs B1 2.92）—— KG 价值最直接体现

### 已知遗留（不影响投稿）
- backend matplotlib 在 sandbox 卡 ax.bar，画图必须用 `C:/Users/Administrator/Miniconda3/python.exe`（base conda）
- KG ANN 索引启动时 lazy 构建（首次调用 ~250s），后续 ~2.5s
