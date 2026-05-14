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
