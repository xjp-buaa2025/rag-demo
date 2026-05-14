# Assembly Scheme Skill 前端集成设计文档

**日期：** 2026-05-14
**范围：** Plan 6 — 为后端 `/assembly-design/*` 端点新增独立前端页面

---

## 1. 目标

在现有 React 前端中新增 `/assembly-design` 路由页面，支持：
- 创建/列出装配方案
- 逐阶段手动触发 S1→S5 生成
- 展开查看各阶段产物（Markdown 渲染 + 原始 JSON 折叠）
- S5 完成后导出 `final_scheme.md`

## 2. 技术选型

- **路由**：引入 `react-router-dom` v6，`/` 保持现有主页，`/assembly-design` 新页面
- **样式**：沿用 Tailwind CSS v4，不引入新 UI 库
- **状态**：组件本地 state（无需全局状态管理），`AssemblyDesignPage` 持有 `selectedSchemeId`
- **API**：新增 `frontend/src/api/assemblyDesign.ts`，所有调用通过 `/api` Vite 代理转发

## 3. 文件结构

```
frontend/src/
├── main.tsx                         # 修改：加 BrowserRouter
├── App.tsx                          # 修改：加导航栏 + <Routes>，/ 和 /assembly-design 两条路由
├── pages/
│   └── AssemblyDesignPage.tsx       # 新增：左右分栏布局页面
├── api/
│   └── assemblyDesign.ts            # 新增：listSchemes / createScheme / getScheme / runStage / exportScheme
├── types/
│   └── assemblyDesign.ts            # 新增：SchemeMeta / SchemeDetail / StageKey 等类型
└── components/assembly/
    ├── SchemeList.tsx               # 新增：左侧方案列表 + [+ 新建方案] 按钮
    ├── NewSchemeModal.tsx           # 新增：新建方案弹窗表单
    ├── SchemeDetail.tsx             # 新增：右侧阶段卡片列表 + 导出按钮
    └── StageCard.tsx               # 新增：单个阶段卡（生成按钮 + 产物展开）
```

## 4. UI 布局

```
/assembly-design
┌────────────────────────────────────────────────────────────────┐
│ Header: [← 主页] | ✈ 装配方案设计                               │
├──────────────────────┬─────────────────────────────────────────┤
│ 左侧边栏 (w-64)       │ 右侧详情区                               │
│                      │                                         │
│ [+ 新建方案]          │ （未选中时显示提示文字）                  │
│ ──────────────       │                                         │
│ ■ PT6A HPC           │ 子系统：PT6A 高压压气机                  │
│   2026-05-14         │ 设计意图：工艺优化                       │
│ □ PT6A 涡轮           │                                         │
│   2026-05-13         │ ┌─ S1 任务调研 ──────────────────────┐  │
│                      │ │ [生成] ✓ 已完成 ▶ 展开产物          │  │
│                      │ └────────────────────────────────────┘  │
│                      │ ┌─ S2 需求分析 ──────────────────────┐  │
│                      │ │ [生成]  前置：需先完成 S1           │  │
│                      │ └────────────────────────────────────┘  │
│                      │ ... S3 / S4a / S4b / S5 同结构 ...     │
│                      │                                         │
│                      │ [📄 导出方案 MD]（S5 完成后可点击）      │
└──────────────────────┴─────────────────────────────────────────┘
```

## 5. 类型定义（assemblyDesign.ts）

```typescript
export interface SchemeMeta {
  scheme_id: string
  created_at: string
  subject: {
    system: string
    system_en?: string
    scope: string[]
    design_intent: string
    constraints: Record<string, string>
  }
  stages_done: string[]
}

export interface SchemeDetail extends SchemeMeta {
  stage1?: Record<string, unknown>
  stage2?: Record<string, unknown>
  stage3?: Record<string, unknown>
  stage4a?: Record<string, unknown>
  stage4b?: Record<string, unknown>
  stage5?: Record<string, unknown>
}

export type StageKey = '1' | '2' | '3' | '4a' | '4b' | '5'

export interface StageRunRequest {
  action: 'generate' | 'regenerate' | 'save_edits'
  payload?: Record<string, unknown>
  user_guidance?: string
}

export interface ExportResult {
  export_path: string
  content_md: string
}
```

## 6. API 函数（assemblyDesign.ts）

| 函数签名 | 后端端点 | 说明 |
|---------|---------|------|
| `listSchemes(): Promise<SchemeMeta[]>` | `GET /assembly-design/scheme/list` | 获取所有方案 |
| `createScheme(req): Promise<{scheme_id, meta}>` | `POST /assembly-design/scheme/new` | 新建方案 |
| `getScheme(id): Promise<SchemeDetail>` | `GET /assembly-design/scheme/{id}` | 获取方案+各阶段产物 |
| `runStage(id, key, req): Promise<Record<string, unknown>>` | `POST /assembly-design/scheme/{id}/stage/{key}` | 触发阶段生成 |
| `exportScheme(id): Promise<ExportResult>` | `GET /assembly-design/scheme/{id}/export` | 导出 final_scheme.md |

## 7. 组件职责

### AssemblyDesignPage
- 持有 `selectedSchemeId: string | null` state
- 渲染左右分栏：左 `SchemeList`，右 `SchemeDetail`（或空态提示）
- 向 `SchemeList` 传 `onSelect` 和 `onCreated` 回调

### SchemeList
- 调用 `listSchemes()` 初始化列表
- 渲染方案列表（每项：系统名 + 创建日期 + stages_done 数量徽标）
- 点击「+ 新建方案」打开 `NewSchemeModal`
- 方案创建成功后刷新列表并自动选中新方案

### NewSchemeModal
- 受控弹窗（`isOpen` prop）
- 表单字段：`subject_system`（必填）、`subject_system_en`、`scope`（逗号分隔转数组）、`design_intent`（默认"工艺优化"）
- 提交调用 `createScheme()`，成功后关闭并回调 `onCreated(scheme_id)`

### SchemeDetail
- 接收 `schemeId` prop，调用 `getScheme()` 获取完整数据
- 渲染 6 张 `StageCard`（S1/S2/S3/S4a/S4b/S5），按固定顺序
- 每张 card 生成完成后重新调用 `getScheme()` 刷新状态
- S5 完成后显示「导出方案 MD」按钮，点击调用 `exportScheme()`，下载或弹出内容

### StageCard
- Props：`stageKey`、`title`、`isDone`、`stageData`（产物 JSON）、`prerequisite`（前置阶段key）、`onGenerate`、`loading`
- 「生成」按钮：前置未完成时 disabled + tooltip 提示
- 产物展开区：`isDone` 时显示折叠面板，内含 Markdown 渲染（stage1 的 `task_card_md`）或 JSON 预览

## 8. 阶段前置依赖

| 阶段 | 前置条件 |
|------|---------|
| S1 | 无 |
| S2 | S1 完成 |
| S3 | S2 完成 |
| S4a | S3 完成 |
| S4b | S4a 完成 |
| S5 | S4b 完成 |

按钮 disabled 逻辑：`stages_done` 数组不含前置 key 时禁用，tooltip 说明"需先完成 SX"。

## 9. 错误处理

- API 失败：在对应 StageCard 下方显示红色错误提示（`error: string | null` state），不阻断其他卡片
- 409 前置未满足：显示"请先完成前置阶段"（理论上按钮已 disabled，此为兜底）
- 导出失败：Toast 提示（复用已有 UI 风格，无单独 Toast 库，用临时 div 显示 2 秒后消失）

## 10. 导航变更

`main.tsx`：
```tsx
<BrowserRouter>
  <App />
</BrowserRouter>
```

`App.tsx` Header 新增导航按钮：
```
[🏠 主页]  [✈ 装配设计]
```

`App.tsx` 主体用 `<Routes>` 包裹：
- `<Route path="/" element={<HomePage />}>`（现有内容提取为 `HomePage`）
- `<Route path="/assembly-design" element={<AssemblyDesignPage />}>`

## 11. 测试策略

- 每个新组件对应一个渲染测试（Vitest + React Testing Library）：验证正常渲染、空态、loading 态
- API 函数：mock fetch 验证调用路径和参数格式
- 端到端：手动验证 S1→S5 完整流程（后端已有 100 条单元测试覆盖逻辑层）

## 12. 不在范围内

- S4c / S4d（后端 501）：前端不显示这两个阶段卡片
- HITL 编辑产物（save_edits action）：Plan 6 只做生成+展示，编辑留 Plan 7
- 实时流式输出（SSE）：后端 runStage 是同步 JSON 响应，直接 await 即可
