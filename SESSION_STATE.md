# SESSION_STATE.md — 热记忆

## [Plan 5 已完成（2026-05-14）— Assembly Scheme Skill S1→S5 全链路贯通]

**Plan 5（Assembly Scheme Skill S5 评审与导出）已完成**，branch `feat/assembly-scheme-p2-s2-s3`，100 tests 全绿。

### 已交付内容
- `backend/pipelines/assembly_scheme/stage5_review.py`：三角色评审 + KC 追溯矩阵 + 四层降级保险 + `_cross_validate()`（high severity 不可标 approved）
- `skills/aero-engine-assembly-scheme/templates/schemas/stage5.schema.json`：完整约束 schema（从 placeholder v1 升级）
- `skills/aero-engine-assembly-scheme/prompts/s5_review.prompt.md`：S5 LLM 提示词
- `backend/routers/assembly_design.py`：stage/5 路由激活（依赖 stage4b）+ GET /export 导出实现
- `PROJECT_GUIDE.md §16.P5`：已更新（3W1H 标准）
- 证据：`tests/assembly/`（100 tests，含 8 个 S5 单元测试 + 4 个 S5 路由/export 测试）

### Assembly Scheme Skill 全阶段状态
| 阶段 | 状态 | Plan |
|------|------|------|
| S1 任务调研 | ✅ 完成 | P1 |
| S2 需求分析 | ✅ 完成 | P2 |
| S3 概念架构 | ✅ 完成 | P2 |
| S4a 工序总表 | ✅ 完成 | P3 |
| S4b 工装规划 | ✅ 完成 | P4 |
| S4c 公差分配 | ⏭ 跳过（数据不足） | — |
| S4d 关键件控制 | ⏭ 跳过（数据不足） | — |
| S5 评审与导出 | ✅ 完成 | P5 |

### 后续建议
1. **前端集成**：在 KG 阶段组件中接入 assembly-design 端点，展示 S5 评审报告 + KC 追溯矩阵
2. **KG 诊断**：按 bubbly-chasing-pizza.md P0 实施 docx BOM 解析器
3. **开新会话**：请陛下开启新对话（Reset Session）以节约 Token

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

### 已知遗留（不影响投稿）
- backend matplotlib 在 sandbox 卡 ax.bar，画图必须用 `C:/Users/Administrator/Miniconda3/python.exe`（base conda）
- KG ANN 索引启动时 lazy 构建（首次调用 ~250s），后续 ~2.5s
