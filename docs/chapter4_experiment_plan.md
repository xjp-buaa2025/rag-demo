# 第四章实验数据准备清单 & 推进流程（v4 定稿）

> 创建日期：2026-04-23（v4 路线 B，加入跨章节粗评测）
> 对应论文章节：`paper/main.tex` §4 实验与结果、§5 讨论
> 核心评测基准：`storage/kg_stages/golden_triples.json`（108 实体 / 99 三元组 / 压气机 72-30 子系统）
> **语料范围**：PT6A 整机（textin MD）入库作检索池；**双层评测**：60 题精评（72-30）+ 20 题粗评（跨章节）

## 语料就位盘点（2026-04-23）

| 文件 | 大小 | 角色 |
|---|---|---|
| `data/KG/PT6A/manual1.md` | 732 KB / 25887 行 | TOC + 索引，正文从 L8xxx 开始 |
| `data/KG/PT6A/manual2.md` | 669 KB / 20757 行 | 72-xx / 73-xx 维修章节正文 |
| `data/KG/PT6A/manual3.md` | 378 KB / 11241 行 | 74/76/77/79 章节正文 |
| `data/KG/PT6A/bom.docx` | 205 KB | 581 子表 / 3138 FIG.ITEM / **3717 PART NUMBER** |
| **合计** | **1.99 MB** | 10 章 ATA（61/70/71/72/73/74/75/76/77/79）全覆盖 |

---

## 零、已冻结的决策矩阵（陛下已签，v3 更新）

| 决策项 | 选择 | 说明 |
|---|---|---|
| **Q1 硬件** | **RTX 5070 / i7-13xxx / 32 GB RAM** + 远程 LLM API | 本地 GPU 足够跑 bge-m3 / CLIP / bge-reranker |
| **Q2 范围（v3 调整）** | **PT6A 整机文本语料**入库作召回池；**精评测锁定 72-30** | 陛下提供完整 PT6A 手册+BOM |
| **Q3 QA 数量（v4 升级为路线 B）** | **60 精评（72-30 带 gold）+ 20 粗评（跨章节 LLM-Judge only）= 80 题** | ← 陛下选 B：升级为整机级评测 |
| **Q4 QA 分布** | A 结构 20 / B 工序 12 / C 规范 9 / D 几何 19 | 按黄金三元组关系比例推算 |
| **Q5 HITL 实证** | **删** | 删掉 §3.3.3 "8.3%→2.1%" 数字 |
| **Q6 基线策略** | **只消融**，不重实现 HybridRAG | |
| **Q7 端到端评估** | LLM-Judge + RAGAS + ROUGE-L(中文) | |
| **Q8 Chapter 5** | **是**，一并起草 | |
| **QA 主题** | 全部围绕**航空发动机装配**场景 | |
| **⭐ v3 新增：CLIP 策略** | **暂缓**（Week 2 结束再定） | Week 1 不处理爆炸图；论文架构描述保留，实验数据 Week 2 观察 |
| **⭐ v3 新增：PDF 处理** | **陛下 textin 自转 MD**，系统跳过本地 PDF 解析 | 规避 DeepDoc 不稳定风险 |

---

## 一、QA 评测集设计（v4 双层）

### 1.0 双层结构

| 层 | 规模 | 范围 | 有无 gold_chunk | 指标 |
|---|---|---|---|---|
| **精评（Tier-1）** | 60 题 | 72-30 压气机 | ✅ 有（来自 golden_triples） | Recall@K / MRR / Hit@K / NDCG + LLM-Judge + RAGAS + ROUGE-L |
| **粗评（Tier-2）** | 20 题 | 跨章节（72-50 / 73 / 76-77 / 79） | ❌ 无 | 仅 LLM-Judge 三维评分 |

### 1.0.1 Tier-2 跨章节 QA 分配

| ATA 章节 | 主题 | 题数 | 典型问题 |
|---|---|---|---|
| 72-50 | 涡轮装配 | 6 | "第2级涡轮盘与轴的连接方式是什么？" |
| 73-10/20 | 燃油系统装配 | 5 | "燃油计量装置的安装扭矩是多少？" |
| 76-77 | 控制与指示装配 | 4 | "N2 转速传感器装在哪个位置？" |
| 79 | 滑油系统装配 | 5 | "主滑油泵与减速箱的装配顺序？" |
| **合计** | | **20** | 均聚焦装配场景 |



### 1.1 分布推算依据

基于 `golden_triples.json` 的 99 条关系实例：

| 类别 | 含三元组关系 | 数量 | 占比 | 60 题配额 |
|---|---|---:|---:|---:|
| **A 零件结构查询** | isPartOf | 34 | 34% | **20 题** |
| **B 工序工具查询** | precedes / participatesIn / requires | 5+8+7 = 20 | 20% | **12 题** |
| **C 技术规范查询** | specifiedBy | 14 | 14% | **9 题** |
| **D 几何配合查询** | matesWith / adjacentTo / hasInterface / constrainedBy | 9+7+9+6 = 31 | 31% | **19 题** |
| **合计** | | 99 | 100% | **60 题** |

### 1.2 四类 QA 的场景定位（均围绕装配）

| 类别 | 示例问题（装配场景） | 需要系统回答的关键信息 |
|---|---|---|
| A 结构 | "压气机主轴承包含哪些子零件？"、"PN 1002-AX 属于哪个装配体？" | Part/Assembly 层级、零件编号 |
| B 工序 | "安装涡轮盘前必须完成哪些步骤？"、"拧紧主轴螺栓需要什么工具？" | 工序先后、工具清单 |
| C 规范 | "主轴螺栓的扭矩规范是多少？"、"第3级叶片与机匣的间隙要求？" | 数值 + 单位 |
| D 几何 | "叶片与导流片的配合方式是什么？"、"主轴承与涡轮盘是同轴配合吗？" | 配合类型、几何约束 |

### 1.3 条目格式（`tests/kg/fixtures/assembly_qa.jsonl`）

```json
{
  "qa_id": "Q001",
  "category": "A_structure",
  "question": "压气机转子组件（Compressor Rotor Assembly）由哪几个主要零件构成？",
  "gold_chunk_ids": ["3013242_72-30-00_p01_c03"],
  "gold_subgraph": {
    "nodes": ["A002", "P003", "P004", "P005"],
    "triples": [["P003", "isPartOf", "A002"], ["P004", "isPartOf", "A002"]]
  },
  "gold_answer_kw": ["转子盘", "叶片", "主轴"],
  "gold_answer": "压气机转子组件主要由转子盘、压气机叶片和主轴组成。",
  "source_golden_id": "A002",
  "generated_by": "auto-from-golden",
  "need_human_check": true
}
```

### 1.4 生成流程（臣自动做）

```
Tier-1（60 题精评）:
  golden_triples.json
    ↓ 按 A/B/C/D 四类分桶
    ↓ 每桶按三元组数量抽样
    ↓ LLM 反向生成问题（提示词含"必须围绕装配场景"约束）
    ↓ 人工 reachback：gold_chunk_ids 通过 BGE-M3 在 Qdrant 反查
    ↓ 输出 assembly_qa_tier1.jsonl（60 条）

Tier-2（20 题粗评）:
  PT6A 整机 BOM + manual 按章节筛选
    ↓ 每章节取 5-6 条高 UNITS_PER_ASSY 的关键零件作锚
    ↓ LLM 根据锚零件生成"装配场景"问题
    ↓ 输出 assembly_qa_tier2.jsonl（20 条，无 gold_chunk）

  陛下 30 min 批量勾选 ✓/✗（80 题一起）
```

---

## 二、任务分工（更新版）

### 🟢 臣可独立完成（v4 任务清单）

| 任务 | 输入 | 输出 | 预计耗时 |
|---|---|---|---|
| **PT6A 整机入库脚本** | 3 MD + 1 docx | `scripts/ingest_pt6a.py`（含 TOC 过滤 + EFFECT=A 过滤 + BOM 噪声清洗） | 0.5 天 |
| **整机入库执行**（后台跑）| 上脚本 | Qdrant 文本向量 + BM25 索引 + Neo4j BOM + KG 三元组 | 0.5~1 天 |
| **Tier-1 QA 生成** | `golden_triples.json`+手册 | `tests/kg/fixtures/assembly_qa_tier1.jsonl`（60 条） | 0.5 天 |
| **Tier-2 QA 生成** | PT6A 整机数据 | `tests/kg/fixtures/assembly_qa_tier2.jsonl`（20 条） | 0.5 天 |
| **CAD 轨补三类关系** | 两个 STEP 文件 | stage3 补齐 adjacentTo / hasInterface / GeoConstraint | 1 天 |
| **Manual 四级对齐** | stage2 产物（已升级） | 整机 BOM 入库后 coverage 预计破 60% | 0.5 天 |
| **BOM 层级噪声扩正则** | `_apply_ipc_hierarchy` | 处理 `- 11b` / `- 220c` / OCR 噪声 283 条 | 0.5 天 |
| **path_mask 消融开关** | `backend/routers/chat.py` | 支持 `path_mask={dense,bm25,clip,kg}` | 0.5 天 |
| **6 种基线封装** | path_mask 组合 | Naive / BM25 / Dense / Dense+BM25 / +CLIP / MHRAG | 0.5 天 |
| **自动评测脚本** | `/eval/ranked` + RAGAS + LLM-Judge + ROUGE-L | `scripts/run_experiments.py` | 1 天 |
| **Tier-2 跨章节粗评** | tier2.jsonl × 6 基线 | LLM-Judge 三维分数 | 0.5 天 |
| **四张表出 CSV + LaTeX** | 评测产出 | `docs/experiments/table{2,3,4,5}.{csv,tex}` | 0.5 天 |
| **柱状图 PDF 生成** | CSV | `paper/figures/fig8-11_*.pdf`（主表/消融/KG 质量/跨章节） | 0.5 天 |
| **Chapter 4 + 5 起草** | 全部结果 | `paper/chapters/chapter4.tex` / `chapter5.tex` | 3 天 |
| **Chapter 3 HITL 段回改** | `paper/chapters/chapter3.tex` | 删伪数字，改定性 | 0.5 天 |

### 🟡 陛下需做的事

| 时点 | 事项 | 时长 |
|---|---|---|
| 启动前 | 一句话给硬件规格（CPU/GPU/RAM/存储） | 1 min |
| 启动前 | 原始手册 PDF 能否提供？（详见 §五）| 1 min |
| Week 1 Day 3 | 勾选 60 条 QA 的 ✓/✗（问题/答案合理性） | 30 min |
| Week 2 Day 14 | 过一眼数字表，决定是否 re-run | 10 min |
| Week 3 Day 20 | 审 chapter4/5 初稿 | 1 h |
| **合计** | | **< 2 h** |

### 🔴 已删除的任务（Q5 决策）

- ~~组织 N 位专家 × M 份报告的受控实验~~
- ~~计算 8.3%→2.1% 的前后对比~~
- ~~§3.3.3 凭空数字段落~~（改为：机制描述 + 图示说明 stage gate 状态机）

---

## 三、基线方法（只消融不重实现）

| # | 名称 | path_mask 配置 | 备注 |
|---|---|---|---|
| B1 | **Naive RAG** | `dense` only | 最弱基线 |
| B2 | **BM25-only** | `bm25` only | 稀疏基线 |
| B3 | **Dense-only** | `dense` only（同 B1，区别在是否多查询） | 若 B1 含多查询，B3 为纯单查询 Dense |
| B4 | **Hybrid (Dense+BM25 RRF)** | `dense+bm25` | 文本双路 |
| B5 | **+ CLIP 图像** | `dense+bm25+clip` | 三模态 |
| **B6** | **MHRAG（本文全量）** | `dense+bm25+clip+kg` | 四路完整 |

> 论文§2 提到的 HybridRAG[shen2025hybridrag] **不重实现**。改为在§4.4 明确说明："我们采用**内部消融**而非外部复现，因 HybridRAG 未开源且本文贡献聚焦于三源 KG 构建而非融合算法替换"。

### 消融实验（在 B6 基础上逐路径减）

| # | 配置 | 移除对象 |
|---|---|---|
| Ablation-1 | B6 − BM25 | 稀疏路径 |
| Ablation-2 | B6 − CLIP | 图像路径 |
| Ablation-3 | B6 − KG | 图谱路径 |
| Ablation-4 | B6 − 多查询扩展 | 查询扩展模块 |
| Ablation-5 | B6 − Reranker | CrossEncoder 精排 |

---

## 四、端到端评估（组合三指标）

| 指标族 | 具体指标 | 评估工具 | 说明 |
|---|---|---|---|
| **检索质量** | Recall@5 / MRR / Hit@1 / Hit@5 / NDCG@5 | `/eval/ranked` | 需要 `gold_chunk_ids` |
| **生成质量（LLM-Judge）** | Relevance / Completeness / Answerability (0-5) | `/eval/judge` | 主观维度 |
| **生成质量（RAGAS）** | Faithfulness / Answer Relevance / Context Precision | `/eval/ragas` | 半客观维度 |
| **生成质量（字面）** | ROUGE-L (中文, jieba 分词) | 自建 script | 补充性指标；陛下口谕要"组合" |
| **KG 质量** | Entity-P/R/F1, Relation-P/R/F1, Coverage | 对比 golden_triples | §5.2 用 |

> ROUGE-L 在中文下有偏差，主要看前两者；若数字与 LLM-Judge 矛盾，以 LLM-Judge 为准。

---

## 五、语料处理方案（v3 核心变更）

### 5.1 陛下的 textin 转 MD 操作指引

```
步骤 1：访问 https://www.textin.com/
步骤 2：注册/登录后使用「PDF 转 Markdown」功能
步骤 3：上传：
  - PT6A 维修手册 PDF
  - PT6A BOM 表 PDF
步骤 4：等待转换完成后下载 MD 文件
步骤 5：保存到本地：
  data/KG/PT6A/manual.md    ← 整机维修手册
  data/KG/PT6A/bom.md       ← 整机 BOM 表
  （可选，若分章节下载）
  data/KG/PT6A/manual_72-30.md  ← 压气机子系统（若 textin 拆分输出）
```

> **textin 为何合适**：
> - 保留表格（`<table>` HTML 标签）、ATA 章节编号（如 72-30-00）
> - 保留图片引用（即使是 CDN URL，caption 仍可检索）
> - 文本质量显著优于本地 DeepDoc 的 OCR 产出
> - 陛下操作 1 次即可，不占本地算力

### 5.2 爆炸图暂缓处理（Q: CLIP 策略）

| 阶段 | 处理 |
|---|---|
| Week 1 | **完全搁置**，不处理图片 |
| Week 2 Day 10 | 跑完主实验后，观察 CLIP 路径对总指标的影响 |
| Week 2 Day 14 | 陛下决定：保留 case study / 彻底删除 / 补方案 B 抢救 |

**论文暂时保留**：§1.3 贡献 2、§2.3、§3.4.4 暂不改动，Week 2 末再定。

### 5.3 臣收到 MD 后的自动流程

```
data/KG/PT6A/*.md
    ↓ 走文本入库路径（跳过 PDF 解析）
    ↓ 按 ATA 章节切块（正则识别 72-XX-XX）
    ↓ BGE-M3 编码 → Qdrant text_vec
    ↓ BM25 索引更新（jieba + regex 双轨）
    ↓ LLM 三元组抽取（nodes_kg）
    ↓ 三级级联对齐（已升级为四级，见 SESSION_STATE）
    ↓ 写入 Neo4j
    
BOM MD：
    ↓ /bom/ingest/pipeline 的 LLM-to-CSV 路径
    ↓ 解析为 {part_id, part_name, material, qty, parent}
    ↓ 写 Neo4j Part/Assembly 节点 + CHILD_OF 边
    ↓ 作为 KG 实体注册表供 manual 对齐
```

---

## 六、推进流程（v4 路线 B）

```
┌──────────────────────── Week 1 (补数据) ────────────────────────┐
│ Day 0  ✅  陛下 textin 转 MD 已就位                               │
│ Day 1 AM   臣：入库脚本（TOC 过滤/EFFECT=A/BOM 噪声清洗）         │
│ Day 1 PM   臣：整机入库后台跑 + 同步生成 Tier-1 60 题 QA 草稿     │
│ Day 2 AM   臣：入库完成检查 + 出 KG/BOM 规模报告                  │
│ Day 2 PM   臣：CAD 轨补 3 类关系 + Tier-2 20 题 QA 草稿           │
│ Day 3      陛下：30 min 勾选 80 题 ✓/✗                            │
│ Day 3      臣：根据勾选结果补题/替换                              │
│ Day 4      臣：Manual 四级对齐重跑；目标 coverage 60%+             │
│ Day 5      臣：三阶段 KG 重跑，出 KG 质量对比报告                 │
│ Day 6-7    臣：path_mask + 6 基线封装 + smoke test                │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────── Week 2 (跑实验) ────────────────────────┐
│ Day 8      Tier-1 主实验：6 档 × 60 QA → Table 2                  │
│ Day 9      Tier-1 端到端：Judge+RAGAS+ROUGE-L                     │
│ Day 10     Tier-1 消融 5 项 + Tier-2 跨章节粗评 → Table 3+5      │
│ Day 11     KG 质量：对比 golden_triples → Table 4                 │
│ Day 12-13  出 4 张 PDF 柱状图                                     │
│ Day 14     陛下：数字验收                                         │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────── Week 2 (跑实验) ────────────────────────┐
│ Day 8        主实验：6 档 × 60 QA → Table 2 检索半               │
│ Day 9        端到端：LLM-Judge + RAGAS + ROUGE-L → Table 2 生成半 │
│ Day 10       消融 5 项 → Table 3                                  │
│ Day 11       KG 质量：对比 golden_triples → Table 4               │
│ Day 12-13    出 4 张 PDF 柱状图；生成 LaTeX booktabs 表格         │
│ Day 14       陛下：过一眼数字，决定是否 re-run                    │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────── Week 3 (写论文) ────────────────────────┐
│ Day 15-17    臣：chapter4.tex 起草（§4.1–4.6）                   │
│ Day 18-19    臣：chapter5.tex 起草（§5.1–5.3）+ §3.3.3 回改       │
│ Day 20       陛下：审稿                                           │
│ Day 21       全文编译 + latex-thesis-zh 终审                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## 七、目标产出一览（Table 示意，数字待跑）

### 7.1 Table 2 — 主实验

| 方法 | Recall@5 | MRR | Hit@5 | NDCG@5 | Faith. | Ans.Rel. | ROUGE-L |
|---|---|---|---|---|---|---|---|
| B1 Naive RAG | - | - | - | - | - | - | - |
| B2 BM25-only | - | - | - | - | - | - | - |
| B3 Dense-only | - | - | - | - | - | - | - |
| B4 Dense+BM25 | - | - | - | - | - | - | - |
| B5 + CLIP | - | - | - | - | - | - | - |
| **B6 MHRAG** | - | - | - | - | - | - | - |

### 7.2 Table 3 — 消融

| 配置 | Recall@5 | MRR | ΔMRR | A类↓ | B类↓ | C类↓ | D类↓ |
|---|---|---|---|---|---|---|---|
| MHRAG (全) | - | - | — | — | — | — | — |
| − BM25 | - | - | - | - | - | - | - |
| − CLIP | - | - | - | - | - | - | - |
| − KG | - | - | - | - | - | - | - |
| − 多查询 | - | - | - | - | - | - | - |
| − Reranker | - | - | - | - | - | - | - |

> 分类贡献列（A/B/C/D 类 QA 的 MRR 跌幅）可以支撑§5.1 "各路径贡献"的细粒度分析。

### 7.3 Table 4 — KG 质量 vs 生成效果

| KG 版本 | Entity-F1 | Rel-F1 | Coverage | 对应 B6 MRR |
|---|---|---|---|---|
| 自动抽取（当前） | - | - | 15% | - |
| + Manual 对齐优化 | - | - | 40%+ | - |

---

## 八、关键文件索引

| 文件 | 路径 | 状态 |
|---|---|---|
| QA 评测集 | `tests/kg/fixtures/assembly_qa.jsonl` | Week 1 Day 1 生成 |
| 原始手册 PDF（方案 A 需要） | `data/KG/3013242.pdf` | **陛下待定** |
| 下载的图片（方案 B 产物） | `storage/images/textin_*.jpg` | Week 1 Day 2 |
| CAD 补全后三元组 | `storage/kg_stages/stage3_cad_triples.json` | Week 1 Day 4 覆盖 |
| 对齐后 manual 三元组 | `storage/kg_stages/stage2_manual_triples.json` | Week 1 Day 5 覆盖 |
| 主实验 CSV | `docs/experiments/table2_main.csv` | Week 2 Day 8-9 |
| 消融 CSV | `docs/experiments/table3_ablation.csv` | Week 2 Day 10 |
| KG 质量 CSV | `docs/experiments/table4_kg_quality.csv` | Week 2 Day 11 |
| 柱状图 PDF | `paper/figures/fig8_*.pdf` | Week 2 Day 12-13 |
| Chapter 4 初稿 | `paper/chapters/chapter4.tex` | Week 3 Day 15-17 |
| Chapter 5 初稿 | `paper/chapters/chapter5.tex` | Week 3 Day 18-19 |
| Chapter 3 §3.3.3 回改 | `paper/chapters/chapter3.tex`（删数字） | Week 3 Day 19 |

---

## 九、下一步行动（v3 已对齐陛下口谕）

**硬件**：✅ RTX 5070 / i7-13xxx / 32 GB RAM  
**CLIP 策略**：✅ 暂缓，Week 2 再定  
**PDF 处理**：✅ 陛下 textin 自转 MD

**唯一等待动作**：陛下把 textin 转出的 MD 放到 `data/KG/PT6A/`，回一句"MD 已放"，臣即刻开 Day 1。

若 MD 很大（整机手册可能几 MB），建议分两次放：
  1. 先放 `manual_72-30.md` 即可启动精评测相关任务（QA/KG 质量）
  2. 整机 `manual.md` 放到后再跑全机召回池入库

---

## 十、Plan B 兜底

| 风险 | 缓解 |
|---|---|
| KG-path 增益 < 3% | §1.3 贡献点从"KG 增益"转向"多模态召回+结构化可解释性"；Table 3 的 −KG 列降幅作为定性证据 |
| CLIP 图片全部丢失 | 走方案 C，§4.6 中 +CLIP 路径的增益改为定性"图纸引用能力演示"，跑 5 条图纸专项 case study |
| 跑完 Manual 对齐 coverage 仍 < 40% | 加一轮 HITL 审阅（机制已实现），手动补 10 条关键 alignment；不再追求 40% 指标而改为"+N 条关键对齐"描述 |
| 60 题 QA 过多耗时 | 用 B6 先跑出数字；如陛下觉得可接受，其余基线跑样本量 30 的分层子集 |

---

**注**：v1 已废弃（`docs/chapter4_experiment_plan.md` 首版）。本 v2 为当前有效版本。
