# Assembly Scheme Skill 前端集成 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为后端 `/assembly-design/*` 端点新增独立前端页面，支持创建方案、逐阶段 S1→S5 生成、产物展示和 MD 导出。

**Architecture:** 引入 react-router-dom v6，`/` 保持现有主页，`/assembly-design` 新增左侧方案列表 + 右侧阶段卡片的双栏页面；所有 API 调用封装在 `api/assemblyDesign.ts`；组件放在 `components/assembly/`。

**Tech Stack:** React 19 + TypeScript + Vite + Tailwind CSS v4 + react-router-dom v6 + react-markdown（已安装）

> ⚠️ 前端无测试基础设施，验证方式为 `npm run build`（TypeScript 类型检查）+ 开发服务器手动验证。每个 Task 均以 build 无报错为通过标准。

---

## 文件地图

| 动作 | 文件 |
|------|------|
| 修改 | `frontend/src/main.tsx` |
| 修改 | `frontend/src/App.tsx` |
| 新增 | `frontend/src/types/assemblyDesign.ts` |
| 新增 | `frontend/src/api/assemblyDesign.ts` |
| 新增 | `frontend/src/components/assembly/NewSchemeModal.tsx` |
| 新增 | `frontend/src/components/assembly/SchemeList.tsx` |
| 新增 | `frontend/src/components/assembly/StageCard.tsx` |
| 新增 | `frontend/src/components/assembly/SchemeDetail.tsx` |
| 新增 | `frontend/src/pages/AssemblyDesignPage.tsx` |

---

## Task 1: 安装 react-router-dom + 路由基础设施

**Files:**
- Modify: `frontend/src/main.tsx`
- Modify: `frontend/src/App.tsx`

- [ ] **Step 1: 安装 react-router-dom**

在 `frontend/` 目录执行：

```bash
cd frontend && npm install react-router-dom
```

期望：`package.json` dependencies 中出现 `"react-router-dom": "^6.x.x"`

- [ ] **Step 2: 修改 `frontend/src/main.tsx`，加 BrowserRouter 包裹**

将原内容替换为：

```tsx
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import './index.css'
import App from './App.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </StrictMode>,
)
```

- [ ] **Step 3: 修改 `frontend/src/App.tsx`，提取 HomeContent + 加路由**

将 `App.tsx` 完整替换为：

```tsx
import { useEffect, useState } from 'react'
import { Routes, Route, Link, useLocation } from 'react-router-dom'
import { getHealth } from './api/client'
import KnowledgePanel from './components/rag/KnowledgePanel'
import EvalPanel from './components/rag/EvalPanel'
import KgStagesPanel from './components/kg/KgStagesPanel'
import KgViewer from './components/kg/KgViewer'
import UnifiedChat from './components/shared/UnifiedChat'
import AssemblyDesignPage from './pages/AssemblyDesignPage'

// ============================================================
// Accordion — 可折叠面板
// ============================================================
function Accordion({
  title,
  children,
  defaultOpen = false,
}: {
  title: string
  children: React.ReactNode
  defaultOpen?: boolean
}) {
  const [open, setOpen] = useState(defaultOpen)
  return (
    <div className="border border-slate-200 rounded-lg overflow-hidden">
      <button
        onClick={() => setOpen((v) => !v)}
        className="w-full flex items-center justify-between px-4 py-3 bg-slate-50 hover:bg-slate-100 transition-colors text-sm font-medium text-slate-700"
      >
        <span>{title}</span>
        <span className="text-slate-400 text-xs">{open ? '▲' : '▼'}</span>
      </button>
      <div className={open ? 'p-4 bg-white' : 'hidden'}>{children}</div>
    </div>
  )
}

// ============================================================
// HomeContent — 原有主页内容
// ============================================================
function HomeContent() {
  return (
    <main className="max-w-6xl mx-auto px-6 py-4 space-y-4">
      <Accordion title="📂 知识库管理">
        <KnowledgePanel />
      </Accordion>
      <Accordion title="📊 性能评估">
        <EvalPanel />
      </Accordion>
      <Accordion title="🔗 图谱构建（四阶段）" defaultOpen={false}>
        <KgStagesPanel />
      </Accordion>
      <Accordion title="🕸️ 知识图谱">
        <KgViewer />
      </Accordion>
      <UnifiedChat />
    </main>
  )
}

// ============================================================
// App — 顶层路由 + Header
// ============================================================
function App() {
  const [healthInfo, setHealthInfo] = useState<{ count: number; model: string } | null>(null)
  const location = useLocation()

  useEffect(() => {
    let timer: ReturnType<typeof setInterval>
    const tryFetch = () => {
      getHealth()
        .then((h) => {
          setHealthInfo({ count: h.collection_count, model: h.model })
          clearInterval(timer)
        })
        .catch(() => {})
    }
    tryFetch()
    timer = setInterval(tryFetch, 3000)
    return () => clearInterval(timer)
  }, [])

  return (
    <div className="min-h-screen bg-slate-50">
      {/* ===== Header ===== */}
      <header className="bg-white border-b border-slate-200 px-6 py-4">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-slate-800">
              🚀 航空发动机知识库 &amp; 装配系统
            </h1>
            <p className="text-xs text-slate-400 mt-0.5">
              RAG + Neo4j BOM + 知识图谱 · FastAPI + React
            </p>
          </div>
          <div className="flex items-center gap-6">
            {/* 导航 */}
            <nav className="flex gap-1">
              <Link
                to="/"
                className={`px-3 py-1.5 text-sm rounded transition-colors ${
                  location.pathname === '/'
                    ? 'bg-blue-600 text-white'
                    : 'text-slate-600 hover:bg-slate-100'
                }`}
              >
                🏠 主页
              </Link>
              <Link
                to="/assembly-design"
                className={`px-3 py-1.5 text-sm rounded transition-colors ${
                  location.pathname === '/assembly-design'
                    ? 'bg-blue-600 text-white'
                    : 'text-slate-600 hover:bg-slate-100'
                }`}
              >
                ✈ 装配设计
              </Link>
            </nav>
            {/* 健康状态 */}
            {healthInfo ? (
              <div className="text-right text-xs text-slate-500 space-y-0.5">
                <p>📚 知识库：<span className="font-medium text-blue-600">{healthInfo.count} 块</span></p>
                <p>🤖 LLM：<span className="font-medium">{healthInfo.model}</span></p>
              </div>
            ) : (
              <span className="text-xs text-slate-400">后端连接中…</span>
            )}
          </div>
        </div>
      </header>

      {/* ===== 路由 ===== */}
      <Routes>
        <Route path="/" element={<HomeContent />} />
        <Route path="/assembly-design" element={<AssemblyDesignPage />} />
      </Routes>
    </div>
  )
}

export default App
```

- [ ] **Step 4: 创建空 `AssemblyDesignPage` 占位（避免编译报错）**

新建 `frontend/src/pages/AssemblyDesignPage.tsx`：

```tsx
export default function AssemblyDesignPage() {
  return <div className="p-8 text-slate-500">装配设计页面（建设中）</div>
}
```

- [ ] **Step 5: 验证编译通过**

```bash
cd frontend && npm run build 2>&1 | tail -10
```

期望：`✓ built in` 无 TypeScript 错误

- [ ] **Step 6: commit**

```bash
git add frontend/src/main.tsx frontend/src/App.tsx frontend/src/pages/AssemblyDesignPage.tsx frontend/package.json frontend/package-lock.json
git commit -m "feat(frontend): add react-router-dom, extract HomeContent, add /assembly-design route stub"
```

---

## Task 2: 类型定义 + API 层

**Files:**
- Create: `frontend/src/types/assemblyDesign.ts`
- Create: `frontend/src/api/assemblyDesign.ts`

- [ ] **Step 1: 创建 `frontend/src/types/assemblyDesign.ts`**

```typescript
// Types for /assembly-design/* endpoints

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

export interface CreateSchemeRequest {
  subject_system: string
  subject_system_en?: string
  subject_scope: string[]
  design_intent?: string
  constraints?: Record<string, string>
}
```

- [ ] **Step 2: 创建 `frontend/src/api/assemblyDesign.ts`**

```typescript
import type {
  SchemeMeta,
  SchemeDetail,
  StageKey,
  StageRunRequest,
  ExportResult,
  CreateSchemeRequest,
} from '../types/assemblyDesign'

const BASE = '/api/assembly-design'

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`HTTP ${res.status}: ${text}`)
  }
  return res.json() as Promise<T>
}

export function listSchemes(): Promise<{ schemes: SchemeMeta[] }> {
  return apiFetch('/scheme/list')
}

export function createScheme(
  req: CreateSchemeRequest,
): Promise<{ scheme_id: string; meta: SchemeMeta }> {
  return apiFetch('/scheme/new', {
    method: 'POST',
    body: JSON.stringify(req),
  })
}

export function getScheme(id: string): Promise<SchemeDetail> {
  return apiFetch(`/scheme/${encodeURIComponent(id)}`)
}

export function runStage(
  id: string,
  key: StageKey,
  req: StageRunRequest,
): Promise<Record<string, unknown>> {
  return apiFetch(`/scheme/${encodeURIComponent(id)}/stage/${key}`, {
    method: 'POST',
    body: JSON.stringify(req),
  })
}

export function exportScheme(id: string): Promise<ExportResult> {
  return apiFetch(`/scheme/${encodeURIComponent(id)}/export`)
}
```

- [ ] **Step 3: 验证编译**

```bash
cd frontend && npm run build 2>&1 | tail -5
```

期望：无 TypeScript 错误

- [ ] **Step 4: commit**

```bash
git add frontend/src/types/assemblyDesign.ts frontend/src/api/assemblyDesign.ts
git commit -m "feat(frontend): add assemblyDesign types and API layer"
```

---

## Task 3: NewSchemeModal 组件

**Files:**
- Create: `frontend/src/components/assembly/NewSchemeModal.tsx`

- [ ] **Step 1: 创建 `frontend/src/components/assembly/NewSchemeModal.tsx`**

```tsx
import { useState } from 'react'
import { createScheme } from '../../api/assemblyDesign'

interface Props {
  isOpen: boolean
  onClose: () => void
  onCreated: (schemeId: string) => void
}

export default function NewSchemeModal({ isOpen, onClose, onCreated }: Props) {
  const [system, setSystem] = useState('')
  const [systemEn, setSystemEn] = useState('')
  const [scope, setScope] = useState('')
  const [intent, setIntent] = useState('工艺优化')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  if (!isOpen) return null

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!system.trim()) { setError('子系统名称不能为空'); return }
    const scopeArr = scope.split(/[,，]/).map(s => s.trim()).filter(Boolean)
    if (scopeArr.length === 0) { setError('范围不能为空'); return }
    setLoading(true)
    setError(null)
    try {
      const res = await createScheme({
        subject_system: system.trim(),
        subject_system_en: systemEn.trim() || undefined,
        subject_scope: scopeArr,
        design_intent: intent.trim() || '工艺优化',
      })
      onCreated(res.scheme_id)
      // reset
      setSystem(''); setSystemEn(''); setScope(''); setIntent('工艺优化')
    } catch (err) {
      setError(err instanceof Error ? err.message : '创建失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-md">
        <h2 className="text-base font-semibold text-slate-800 mb-4">新建装配方案</h2>
        <form onSubmit={handleSubmit} className="space-y-3">
          <div>
            <label className="text-xs text-slate-600 block mb-1">子系统名称（中文）*</label>
            <input
              value={system}
              onChange={e => setSystem(e.target.value)}
              placeholder="例：PT6A 高压压气机"
              className="w-full border border-slate-300 rounded px-3 py-1.5 text-sm focus:outline-none focus:border-blue-400"
            />
          </div>
          <div>
            <label className="text-xs text-slate-600 block mb-1">子系统名称（英文，可选）</label>
            <input
              value={systemEn}
              onChange={e => setSystemEn(e.target.value)}
              placeholder="例：PT6A HPC"
              className="w-full border border-slate-300 rounded px-3 py-1.5 text-sm focus:outline-none focus:border-blue-400"
            />
          </div>
          <div>
            <label className="text-xs text-slate-600 block mb-1">范围（逗号分隔）*</label>
            <input
              value={scope}
              onChange={e => setScope(e.target.value)}
              placeholder="例：3 级轴流, 含转子/静子"
              className="w-full border border-slate-300 rounded px-3 py-1.5 text-sm focus:outline-none focus:border-blue-400"
            />
          </div>
          <div>
            <label className="text-xs text-slate-600 block mb-1">设计意图</label>
            <input
              value={intent}
              onChange={e => setIntent(e.target.value)}
              placeholder="工艺优化"
              className="w-full border border-slate-300 rounded px-3 py-1.5 text-sm focus:outline-none focus:border-blue-400"
            />
          </div>
          {error && <p className="text-xs text-red-600">{error}</p>}
          <div className="flex justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-1.5 text-sm text-slate-600 border border-slate-300 rounded hover:bg-slate-50"
            >
              取消
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-1.5 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-40"
            >
              {loading ? '创建中…' : '创建'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
```

- [ ] **Step 2: 验证编译**

```bash
cd frontend && npm run build 2>&1 | tail -5
```

期望：无错误

- [ ] **Step 3: commit**

```bash
git add frontend/src/components/assembly/NewSchemeModal.tsx
git commit -m "feat(frontend): add NewSchemeModal component"
```

---

## Task 4: SchemeList 组件

**Files:**
- Create: `frontend/src/components/assembly/SchemeList.tsx`

- [ ] **Step 1: 创建 `frontend/src/components/assembly/SchemeList.tsx`**

```tsx
import { useState, useEffect } from 'react'
import { listSchemes } from '../../api/assemblyDesign'
import type { SchemeMeta } from '../../types/assemblyDesign'
import NewSchemeModal from './NewSchemeModal'

interface Props {
  selectedId: string | null
  onSelect: (id: string) => void
  refreshKey: number
}

export default function SchemeList({ selectedId, onSelect, refreshKey }: Props) {
  const [schemes, setSchemes] = useState<SchemeMeta[]>([])
  const [showModal, setShowModal] = useState(false)
  const [loading, setLoading] = useState(false)

  const load = () => {
    setLoading(true)
    listSchemes()
      .then(r => setSchemes(r.schemes))
      .catch(() => {})
      .finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [refreshKey])

  const handleCreated = (id: string) => {
    setShowModal(false)
    load()
    onSelect(id)
  }

  return (
    <div className="flex flex-col h-full">
      <div className="p-3 border-b border-slate-200">
        <button
          onClick={() => setShowModal(true)}
          className="w-full px-3 py-1.5 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          + 新建方案
        </button>
      </div>

      <div className="flex-1 overflow-y-auto">
        {loading && (
          <p className="text-xs text-slate-400 p-3">加载中…</p>
        )}
        {!loading && schemes.length === 0 && (
          <p className="text-xs text-slate-400 p-3">暂无方案，点击上方新建</p>
        )}
        {schemes.map(s => (
          <button
            key={s.scheme_id}
            onClick={() => onSelect(s.scheme_id)}
            className={`w-full text-left px-3 py-2.5 border-b border-slate-100 hover:bg-slate-50 transition-colors ${
              selectedId === s.scheme_id ? 'bg-blue-50 border-l-2 border-l-blue-500' : ''
            }`}
          >
            <div className="text-sm font-medium text-slate-700 truncate">
              {s.subject.system}
            </div>
            <div className="flex items-center justify-between mt-0.5">
              <span className="text-xs text-slate-400">
                {s.created_at.slice(0, 10)}
              </span>
              <span className="text-xs bg-green-100 text-green-700 px-1.5 py-0.5 rounded">
                {s.stages_done.length}/6
              </span>
            </div>
          </button>
        ))}
      </div>

      <NewSchemeModal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        onCreated={handleCreated}
      />
    </div>
  )
}
```

- [ ] **Step 2: 验证编译**

```bash
cd frontend && npm run build 2>&1 | tail -5
```

期望：无错误

- [ ] **Step 3: commit**

```bash
git add frontend/src/components/assembly/SchemeList.tsx
git commit -m "feat(frontend): add SchemeList component"
```

---

## Task 5: StageCard 组件

**Files:**
- Create: `frontend/src/components/assembly/StageCard.tsx`

- [ ] **Step 1: 创建 `frontend/src/components/assembly/StageCard.tsx`**

```tsx
import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import type { StageKey } from '../../types/assemblyDesign'

interface Props {
  stageKey: StageKey
  title: string
  isDone: boolean
  stageData?: Record<string, unknown>
  prerequisiteDone: boolean
  prerequisiteLabel: string | null  // e.g. "S1" or null
  loading: boolean
  onGenerate: () => void
}

export default function StageCard({
  stageKey,
  title,
  isDone,
  stageData,
  prerequisiteDone,
  prerequisiteLabel,
  loading,
  onGenerate,
}: Props) {
  const [expanded, setExpanded] = useState(false)
  const [showRaw, setShowRaw] = useState(false)

  const canGenerate = prerequisiteDone && !loading

  return (
    <div className={`border rounded-lg overflow-hidden ${isDone ? 'border-green-200' : 'border-slate-200'}`}>
      {/* Header row */}
      <div className={`flex items-center justify-between px-4 py-3 ${isDone ? 'bg-green-50' : 'bg-slate-50'}`}>
        <div className="flex items-center gap-2">
          <span className={`text-xs font-mono px-1.5 py-0.5 rounded ${isDone ? 'bg-green-200 text-green-800' : 'bg-slate-200 text-slate-600'}`}>
            {isDone ? '✓' : '○'}
          </span>
          <span className="text-sm font-medium text-slate-700">{title}</span>
        </div>
        <div className="flex items-center gap-2">
          {isDone && (
            <button
              onClick={() => setExpanded(v => !v)}
              className="text-xs text-blue-600 hover:underline"
            >
              {expanded ? '▲ 收起' : '▶ 展开产物'}
            </button>
          )}
          <button
            onClick={onGenerate}
            disabled={!canGenerate}
            title={!prerequisiteDone && prerequisiteLabel ? `请先完成 ${prerequisiteLabel}` : undefined}
            className="px-3 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed"
          >
            {loading ? '生成中…' : isDone ? '重新生成' : '生成'}
          </button>
        </div>
      </div>

      {/* Expanded content */}
      {expanded && isDone && stageData && (
        <div className="px-4 py-3 bg-white border-t border-slate-100 space-y-2">
          {/* S1: show task_card_md as Markdown */}
          {stageKey === '1' && typeof stageData.task_card_md === 'string' && (
            <div className="prose prose-sm max-w-none text-slate-700">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {stageData.task_card_md}
              </ReactMarkdown>
            </div>
          )}

          {/* S5: show recommendation + overall_score */}
          {stageKey === '5' && (
            <div className="flex gap-4 text-sm">
              <span className="text-slate-600">评审结论：
                <span className={`ml-1 font-semibold ${
                  stageData.recommendation === 'approved' ? 'text-green-600' :
                  stageData.recommendation === 'rejected' ? 'text-red-600' : 'text-amber-600'
                }`}>
                  {String(stageData.recommendation)}
                </span>
              </span>
              {typeof stageData.overall_score === 'number' && (
                <span className="text-slate-600">综合评分：
                  <span className="ml-1 font-semibold text-blue-600">
                    {stageData.overall_score.toFixed(1)} / 5
                  </span>
                </span>
              )}
            </div>
          )}

          {/* Raw JSON toggle */}
          <div>
            <button
              onClick={() => setShowRaw(v => !v)}
              className="text-xs text-slate-400 hover:text-slate-600"
            >
              {showRaw ? '▲ 隐藏 JSON' : '▶ 原始 JSON'}
            </button>
            {showRaw && (
              <pre className="mt-2 text-xs bg-slate-900 text-green-300 p-3 rounded overflow-x-auto max-h-64 overflow-y-auto">
                {JSON.stringify(stageData, null, 2)}
              </pre>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
```

- [ ] **Step 2: 验证编译**

```bash
cd frontend && npm run build 2>&1 | tail -5
```

期望：无错误

- [ ] **Step 3: commit**

```bash
git add frontend/src/components/assembly/StageCard.tsx
git commit -m "feat(frontend): add StageCard component with Markdown and JSON preview"
```

---

## Task 6: SchemeDetail 组件

**Files:**
- Create: `frontend/src/components/assembly/SchemeDetail.tsx`

- [ ] **Step 1: 创建 `frontend/src/components/assembly/SchemeDetail.tsx`**

```tsx
import { useState, useEffect, useCallback } from 'react'
import { getScheme, runStage, exportScheme } from '../../api/assemblyDesign'
import type { SchemeDetail as SchemeDetailType, StageKey } from '../../types/assemblyDesign'
import StageCard from './StageCard'

interface StageConfig {
  key: StageKey
  title: string
  prerequisite: StageKey | null
  prerequisiteLabel: string | null
}

const STAGES: StageConfig[] = [
  { key: '1',  title: 'S1 任务调研',  prerequisite: null,  prerequisiteLabel: null },
  { key: '2',  title: 'S2 需求分析',  prerequisite: '1',   prerequisiteLabel: 'S1' },
  { key: '3',  title: 'S3 概念架构',  prerequisite: '2',   prerequisiteLabel: 'S2' },
  { key: '4a', title: 'S4a 工序总表', prerequisite: '3',   prerequisiteLabel: 'S3' },
  { key: '4b', title: 'S4b 工装规划', prerequisite: '4a',  prerequisiteLabel: 'S4a' },
  { key: '5',  title: 'S5 评审导出',  prerequisite: '4b',  prerequisiteLabel: 'S4b' },
]

const STAGE_DATA_KEY: Record<StageKey, keyof SchemeDetailType> = {
  '1': 'stage1', '2': 'stage2', '3': 'stage3',
  '4a': 'stage4a', '4b': 'stage4b', '5': 'stage5',
}

interface Props {
  schemeId: string
}

export default function SchemeDetail({ schemeId }: Props) {
  const [scheme, setScheme] = useState<SchemeDetailType | null>(null)
  const [loadingStage, setLoadingStage] = useState<StageKey | null>(null)
  const [stageError, setStageError] = useState<Partial<Record<StageKey, string>>>({})
  const [exportContent, setExportContent] = useState<string | null>(null)
  const [exporting, setExporting] = useState(false)

  const refresh = useCallback(() => {
    getScheme(schemeId).then(setScheme).catch(() => {})
  }, [schemeId])

  useEffect(() => { refresh() }, [refresh])

  const handleGenerate = async (key: StageKey) => {
    setLoadingStage(key)
    setStageError(prev => ({ ...prev, [key]: undefined }))
    try {
      await runStage(schemeId, key, { action: 'generate' })
      refresh()
    } catch (err) {
      setStageError(prev => ({
        ...prev,
        [key]: err instanceof Error ? err.message : '生成失败',
      }))
    } finally {
      setLoadingStage(null)
    }
  }

  const handleExport = async () => {
    setExporting(true)
    try {
      const result = await exportScheme(schemeId)
      setExportContent(result.content_md)
    } catch (err) {
      alert(err instanceof Error ? err.message : '导出失败')
    } finally {
      setExporting(false)
    }
  }

  if (!scheme) {
    return <div className="p-8 text-slate-400 text-sm">加载中…</div>
  }

  const doneSet = new Set(scheme.stages_done)
  const s5Done = doneSet.has('5')

  return (
    <div className="p-4 space-y-3">
      {/* Scheme header */}
      <div className="border border-slate-200 rounded-lg p-4 bg-white">
        <div className="text-base font-semibold text-slate-800">{scheme.subject.system}</div>
        {scheme.subject.system_en && (
          <div className="text-xs text-slate-500">{scheme.subject.system_en}</div>
        )}
        <div className="mt-1 flex flex-wrap gap-3 text-xs text-slate-500">
          <span>设计意图：{scheme.subject.design_intent}</span>
          <span>范围：{scheme.subject.scope.join('、')}</span>
          <span>创建：{scheme.created_at.slice(0, 10)}</span>
          <span className="text-green-600 font-medium">
            已完成 {scheme.stages_done.length}/6 阶段
          </span>
        </div>
      </div>

      {/* Stage cards */}
      {STAGES.map(cfg => {
        const prereqDone = cfg.prerequisite === null || doneSet.has(cfg.prerequisite)
        const isDone = doneSet.has(cfg.key)
        const dataKey = STAGE_DATA_KEY[cfg.key]
        const stageData = scheme[dataKey] as Record<string, unknown> | undefined
        return (
          <div key={cfg.key}>
            <StageCard
              stageKey={cfg.key}
              title={cfg.title}
              isDone={isDone}
              stageData={stageData}
              prerequisiteDone={prereqDone}
              prerequisiteLabel={cfg.prerequisiteLabel}
              loading={loadingStage === cfg.key}
              onGenerate={() => handleGenerate(cfg.key)}
            />
            {stageError[cfg.key] && (
              <p className="text-xs text-red-600 mt-1 px-1">{stageError[cfg.key]}</p>
            )}
          </div>
        )
      })}

      {/* Export button */}
      <div className="pt-2 border-t border-slate-200">
        <button
          onClick={handleExport}
          disabled={!s5Done || exporting}
          title={!s5Done ? '请先完成 S5 评审' : undefined}
          className="px-4 py-2 text-sm bg-emerald-600 text-white rounded hover:bg-emerald-700 disabled:opacity-40 disabled:cursor-not-allowed"
        >
          {exporting ? '导出中…' : '📄 导出方案 MD'}
        </button>
        {exportContent && (
          <div className="mt-3">
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs text-slate-600 font-medium">final_scheme.md 内容：</span>
              <button
                onClick={() => {
                  const blob = new Blob([exportContent], { type: 'text/markdown' })
                  const url = URL.createObjectURL(blob)
                  const a = document.createElement('a')
                  a.href = url
                  a.download = `${schemeId}_final_scheme.md`
                  a.click()
                  URL.revokeObjectURL(url)
                }}
                className="text-xs text-blue-600 hover:underline"
              >
                ⬇ 下载
              </button>
            </div>
            <pre className="text-xs bg-slate-900 text-green-300 p-3 rounded overflow-x-auto max-h-64 overflow-y-auto">
              {exportContent.slice(0, 2000)}{exportContent.length > 2000 ? '\n…（截断）' : ''}
            </pre>
          </div>
        )}
      </div>
    </div>
  )
}
```

- [ ] **Step 2: 验证编译**

```bash
cd frontend && npm run build 2>&1 | tail -5
```

期望：无错误

- [ ] **Step 3: commit**

```bash
git add frontend/src/components/assembly/SchemeDetail.tsx
git commit -m "feat(frontend): add SchemeDetail component with stage cards and export"
```

---

## Task 7: AssemblyDesignPage + 最终接线 + 验证

**Files:**
- Modify: `frontend/src/pages/AssemblyDesignPage.tsx`

- [ ] **Step 1: 替换 AssemblyDesignPage.tsx 为完整实现**

```tsx
import { useState } from 'react'
import SchemeList from '../components/assembly/SchemeList'
import SchemeDetail from '../components/assembly/SchemeDetail'

export default function AssemblyDesignPage() {
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [refreshKey, setRefreshKey] = useState(0)

  const handleCreated = (id: string) => {
    setRefreshKey(k => k + 1)
    setSelectedId(id)
  }

  return (
    <div className="flex h-[calc(100vh-73px)]">
      {/* 左侧边栏 */}
      <aside className="w-64 flex-shrink-0 border-r border-slate-200 bg-white overflow-hidden flex flex-col">
        <div className="px-3 py-3 border-b border-slate-200">
          <h2 className="text-sm font-semibold text-slate-700">✈ 装配方案</h2>
        </div>
        <SchemeList
          selectedId={selectedId}
          onSelect={setSelectedId}
          refreshKey={refreshKey}
        />
      </aside>

      {/* 右侧详情 */}
      <main className="flex-1 overflow-y-auto bg-slate-50">
        {selectedId ? (
          <SchemeDetail schemeId={selectedId} />
        ) : (
          <div className="flex flex-col items-center justify-center h-full text-slate-400 space-y-2">
            <span className="text-4xl">✈</span>
            <p className="text-sm">从左侧选择方案，或新建一个</p>
          </div>
        )}
      </main>
    </div>
  )
}
```

注意：`handleCreated` 传给 `SchemeList` 时通过 `onSelect` + `refreshKey` 实现，`SchemeList` 内部的 `onCreated` 已调用父组件的 `onSelect`。`AssemblyDesignPage` 不直接传 `onCreated`，由 `SchemeList` 内部持有 `NewSchemeModal` 并在创建后调用 `load()` + `onSelect(id)`，因此 `AssemblyDesignPage` 只需传 `refreshKey` 触发列表刷新。

- [ ] **Step 2: 验证 TypeScript 编译**

```bash
cd frontend && npm run build 2>&1 | tail -10
```

期望：`✓ built in` 无错误

- [ ] **Step 3: 启动开发服务器手动验证**

```bash
cd frontend && npm run dev
```

打开浏览器 http://localhost:5173，验证：
- Header 显示「🏠 主页」和「✈ 装配设计」两个导航按钮
- 点击「✈ 装配设计」跳转到新页面，显示左侧边栏 + 右侧空态
- 点击「+ 新建方案」弹出 Modal，填写后可创建
- 创建成功后方案出现在左侧列表，右侧显示 6 张阶段卡片
- 点击「S1 生成」按钮（无前置要求）调用后端，成功后卡片变绿并可展开产物
- S5 完成后「导出方案 MD」按钮变为可点击，导出后可预览 + 下载

- [ ] **Step 4: 更新 SESSION_STATE.md**

将 SESSION_STATE.md 中「后续建议」的「前端集成」改为「✅ 已完成（Plan 6）」

- [ ] **Step 5: commit**

```bash
git add frontend/src/pages/AssemblyDesignPage.tsx SESSION_STATE.md
git commit -m "feat(frontend): complete AssemblyDesignPage, wire up left/right layout"
```

---

## 自查清单

**Spec coverage:**
- [x] React Router v6 引入 → T1
- [x] `/assembly-design` 独立路由 → T1
- [x] 左侧方案列表 + 新建按钮 → T4 SchemeList
- [x] 新建方案 Modal（中英文名/范围/意图）→ T3 NewSchemeModal
- [x] 右侧 6 张阶段卡片（S1-S5）→ T5 StageCard + T6 SchemeDetail
- [x] 前置依赖门控（disabled + tooltip）→ T5 StageCard
- [x] S1 产物：Markdown 渲染 → T5 StageCard (stageKey==='1')
- [x] S5 产物：recommendation + overall_score → T5 StageCard (stageKey==='5')
- [x] 原始 JSON 折叠展示 → T5 StageCard showRaw
- [x] S5 完成后导出按钮 → T6 SchemeDetail
- [x] 导出内容预览 + 下载 → T6 SchemeDetail
- [x] 错误处理（API 失败显示错误） → T6 SchemeDetail stageError
- [x] Header 导航栏 → T1 App.tsx

**No placeholders:** 所有组件代码完整。

**Type consistency:**
- `StageKey` 定义于 `types/assemblyDesign.ts`，在 `StageCard.tsx`、`SchemeDetail.tsx`、`api/assemblyDesign.ts` 中一致使用
- `SchemeDetail` 类型的 `stage4a`/`stage4b` 字段名与后端 `GET /scheme/{id}` 响应一致（后端路由 `get_scheme` 使用 `f"stage{stage_key}"` 作为 key，`4a` → `"stage4a"`）
- `STAGE_DATA_KEY` 映射在 `SchemeDetail.tsx` 中集中管理，避免散落的字符串
