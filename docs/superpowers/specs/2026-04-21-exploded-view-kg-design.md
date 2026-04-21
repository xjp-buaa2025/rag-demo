# 爆炸图与知识图谱关联设计

**日期**：2026-04-21  
**状态**：已审批  
**作者**：Claude Code

---

## 1. 背景与目标

### 问题

当前知识图谱（Neo4j）包含 BOM 零件节点（Part/Assembly）和维修工序节点（Procedure），但与 PDF 中的爆炸图（IPC 图解零件目录）和维修示意图之间没有关联。技术人员在查询装配方案时，无法同步获取直观的图形参考。

### 目标

支持以下两种查询模式，并在装配方案输出中自动附带相关爆炸图：

- **查询A**：给定零件号 → 找到该零件出现在哪张爆炸图，以及在图中的 callout 编号
- **查询C**：给定 ATA 章节 → 找到对应的维修手册示意图

---

## 2. 数据源分析

### 2.1 IPC BOM 爆炸图（`压气机BOM表.pdf`）

标准 IPC（图解零件目录）格式，页面结构：

```
[页A] FIGURE 1 标题 + 爆炸图（工程线稿，含 callout 编号）
[页B] BOM 表格：FIG. | ITEM | PART NUMBER | NOMENCLATURE | QTY
[页C] FIGURE 2 标题 + 爆炸图
...
```

- `FIG.` 列 = 图编号，`ITEM` 列 = 图中 callout 编号
- callout 编号与 Part Number 一一对应，是**结构化**映射关系
- 互换件变体格式：`-1A`, `-1B`（同一零件位的替代件）

### 2.2 维修手册示意图（`压气机维修手册.pdf`）

AMM（飞机维护手册）格式，图例特征：

- 图中 callout 编号（①~⑪）对应**工序步骤**，不对应零件号
- 页脚含 `Figure NNN`（图编号）和 ATA 章节号（如 `72-30-02`）
- 图标题描述操作内容（如 "Removal/Installation of Compressor Wash Ring"）
- 通过 ATA 章节号与 Procedure 节点关联，是**语义化**映射关系

---

## 3. 图谱扩展设计

### 3.1 新节点类型

```
ExplodedView {
  figure_id    : String   // 唯一标识，如 "BOM_FIG_1", "MANUAL_FIG_201"
  image_path   : String   // 相对路径，如 "kg_figures/bom_fig_1.png"
  title        : String   // 图标题
  source       : String   // "IPC" | "Manual"
  ata_chapter  : String   // ATA章节，Manual图专用（IPC图为 null）
  page_number  : Int      // 原始 PDF 页码，供溯源
}
```

### 3.2 新关系类型

```cypher
// IPC 爆炸图：零件位于图中特定 callout 位置
(Part|Assembly)-[:SHOWN_IN {item_callout: "3"}]->(ExplodedView)

// 维修手册示意图：工序对应某张操作示意图
(Procedure)-[:ILLUSTRATED_BY]->(ExplodedView)
```

### 3.3 设计决策

- `ExplodedView` 作为**独立节点**，支持 many:many（一图多零件、一零件多图）
- `item_callout` 存于**关系属性**，同一张图中不同零件的 callout 不同
- `ata_chapter` 仅在 `source="Manual"` 时有值，IPC 图通过 `Part -[SHOWN_IN]->` 关联

### 3.4 图谱示例

```
(3034344:Assembly {name:"COMPRESSOR ROTOR INSTALLATION"})
    -[:SHOWN_IN {item_callout:"1"}]->
(BOM_FIG_1:ExplodedView {source:"IPC", title:"COMPRESSOR ROTOR"})
    <-[:SHOWN_IN {item_callout:"2"}]-
(MS9556-06:Part {name:"BOLT,MACHINE,DBL HEX"})

(Procedure {ata_chapter:"72-30-02"})
    -[:ILLUSTRATED_BY]->
(MANUAL_FIG_201:ExplodedView {
  source:"Manual",
  title:"Removal/Installation of Compressor Wash Ring",
  ata_chapter:"72-30-02"
})
```

---

## 4. 图片存储

### 4.1 文件系统

```
storage/images/kg_figures/
    ├── bom_fig_1.png          # IPC Figure 1
    ├── bom_fig_2.png
    ├── manual_fig_201.png     # Manual Figure 201
    └── manual_fig_202.png
```

### 4.2 静态服务

复用现有 FastAPI 静态文件路由，无需新增路由：

```
Neo4j: ExplodedView.image_path = "kg_figures/bom_fig_1.png"
                ↓
disk: storage/images/kg_figures/bom_fig_1.png
                ↓
HTTP: GET /images/kg_figures/bom_fig_1.png
```

---

## 5. 数据提取流水线

### 5.1 Stage 1 BOM 增强（IPC 图片提取）

在现有 `_bom_df_to_entities_and_triples()` 基础上新增子步骤：

```
parse_bom_pdf()
  ├── extract_bom_table()           # 现有：提取 DataFrame
  ├── extract_ipc_figures()         # 新增：检测 FIGURE X 标题，提取图片
  │     PyMuPDF 逻辑：
  │     - page.get_text() 匹配 r'FIGURE\s+(\d+)'
  │     - page.get_images() 找大图（>300×300）
  │     - doc.extract_image(xref) → 保存 bom_fig_{n}.png
  │     - 记录 figure_number → page_number 映射
  └── write_exploded_views_neo4j()  # 新增：写 ExplodedView + SHOWN_IN
        每个 BOM 实体携带：
        { part_number, figure_number, item_callout }
```

### 5.2 Stage 2 Manual 增强（维修示意图提取）

在现有手册解析基础上新增子步骤：

```
parse_manual_pdf()
  ├── extract_manual_triples()      # 现有：LLM 提取三元组
  ├── extract_manual_figures()      # 新增：检测图页
  │     PyMuPDF 逻辑：
  │     - page.get_images() 中存在大图（>300×300）
  │     - page.get_text() 匹配 r'Figure\s+(\d+)'
  │     - page.get_text() 匹配 r'\b(\d{2}-\d{2}-\d{2})\b'（ATA章节）
  │     - doc.extract_image(xref) → 保存 manual_fig_{n}.png
  └── write_manual_figures_neo4j()  # 新增：写 ExplodedView + ILLUSTRATED_BY
        MATCH Procedure {ata_chapter} → CREATE ILLUSTRATED_BY 关系
```

---

## 6. API 扩展

### 6.1 新增 Cypher 查询

**查询A：零件号 → 爆炸图**
```cypher
MATCH (p {part_number: $pn})-[r:SHOWN_IN]->(f:ExplodedView)
RETURN f.figure_id, f.image_path, f.title, r.item_callout
```

**查询C：ATA章节 → 维修示意图**
```cypher
MATCH (proc:Procedure {ata_chapter: $ata})-[:ILLUSTRATED_BY]->(f:ExplodedView)
RETURN f.figure_id, f.image_path, f.title
```

### 6.2 `/assembly/chat` SSE 帧扩展

新增 `figures` 类型帧，与现有 `sources_md` 帧并列输出：

```json
{
  "type": "figures",
  "data": [
    {
      "url": "/images/kg_figures/bom_fig_1.png",
      "title": "COMPRESSOR ROTOR INSTALLATION",
      "source": "IPC",
      "callout": "3",
      "ata_chapter": null
    },
    {
      "url": "/images/kg_figures/manual_fig_201.png",
      "title": "Removal/Installation of Compressor Wash Ring",
      "source": "Manual",
      "callout": null,
      "ata_chapter": "72-30-02"
    }
  ]
}
```

---

## 7. 前端展示

在装配问答结果区下方新增"相关爆炸图"折叠区：

```
┌─────────────────────────────────────────────┐
│  装配方案（文字回答）                         │
├─────────────────────────────────────────────┤
│  📐 相关爆炸图 (2张)             [展开/折叠] │
│  ┌──────────────┐  ┌──────────────┐          │
│  │ [IPC Fig.1]  │  │[Manual 201]  │          │
│  │ COMPRESSOR   │  │ Wash Ring    │          │
│  │ ROTOR        │  │ Removal      │          │
│  │ Item: 3      │  │ 72-30-02     │          │
│  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────┘
```

交互细节：
- 点击图片 → 全屏弹窗（原图尺寸）
- IPC 图显示 `Item: {callout}` 帮助定位零件
- Manual 图显示 ATA 章节号

---

## 8. 完整数据链路

```
用户问："压气机转子如何装配？"
    ↓ LLM 从问题中提取零件号（3034344）+ ATA章节（72-30-02）
    ↓ Cypher 查询A：(Part)-[:SHOWN_IN]->(ExplodedView)
    ↓ Cypher 查询C：(Procedure)-[:ILLUSTRATED_BY]->(ExplodedView)
    ↓ SSE figures 帧 → 前端渲染爆炸图卡片
    ↓ 用户点击图片 → 全屏查看高清爆炸图
```

---

## 9. 不在本次范围内

- 视觉相似搜索（用例D：上传图片搜相似爆炸图）——留作后续扩展
- 爆炸图中 callout 文字的 OCR 识别——依赖 PDF 文本层，暂不处理扫描件
- CAD STEP 文件与爆炸图的关联——已有 Stage 3 CAD 解析，可独立扩展
