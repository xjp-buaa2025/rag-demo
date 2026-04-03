// ============================================================
// App.tsx — 顶层布局
//
// 统一布局（无 Tab 切换）：
//   - Accordion: 📂 知识库管理（KnowledgePanel）
//   - Accordion: 📊 性能评估（EvalPanel）
//   - Accordion: 📋 BOM 入库（BomIngest）
//   - Accordion: 🔗 图谱构建（KgBuilder）
//   - Accordion: 🕸️ 知识图谱（KgViewer）
//   - 统一聊天（UnifiedChat，内含 RAG/装配 模式切换）
//
// Header 通过 GET /api/health 获取后端状态（文档块数、模型名）。
// ============================================================

import { useEffect, useState } from 'react'
import { getHealth } from './api/client'
import KnowledgePanel from './components/rag/KnowledgePanel'
import EvalPanel from './components/rag/EvalPanel'
import BomIngest from './components/bom/BomIngest'
import KgBuilder from './components/kg/KgBuilder'
import KgViewer from './components/kg/KgViewer'
import UnifiedChat from './components/shared/UnifiedChat'

function App() {
  const [healthInfo, setHealthInfo] = useState<{ count: number; model: string } | null>(null)

  // 获取后端健康状态（轮询，每 3 秒重试，后端就绪后停止）
  useEffect(() => {
    let timer: ReturnType<typeof setInterval>
    const tryFetch = () => {
      getHealth()
        .then((h) => {
          setHealthInfo({ count: h.collection_count, model: h.model })
          clearInterval(timer)
        })
        .catch(() => {}) // 保持 null，继续轮询
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
          {healthInfo ? (
            <div className="text-right text-xs text-slate-500 space-y-0.5">
              <p>📚 知识库：<span className="font-medium text-blue-600">{healthInfo.count} 块</span></p>
              <p>🤖 LLM：<span className="font-medium">{healthInfo.model}</span></p>
            </div>
          ) : (
            <span className="text-xs text-slate-400">后端连接中…</span>
          )}
        </div>
      </header>

      {/* ===== 主内容 ===== */}
      <main className="max-w-6xl mx-auto px-6 py-4 space-y-4">

        <Accordion title="📂 知识库管理">
          <KnowledgePanel />
        </Accordion>

        <Accordion title="📊 性能评估">
          <EvalPanel />
        </Accordion>

        <Accordion title="📋 BOM 入库">
          <BomIngest />
        </Accordion>

        <Accordion title="🔗 图谱构建">
          <KgBuilder />
        </Accordion>

        <Accordion title="🕸️ 知识图谱">
          <KgViewer />
        </Accordion>

        <UnifiedChat />
      </main>
    </div>
  )
}

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

export default App
