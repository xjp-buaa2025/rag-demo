// ============================================================
// App.tsx — 顶层布局：Header + 双 Tab 页面
//
// 两个 Tab：
//   Tab 1：📖 RAG 知识库问答（KnowledgePanel + EvalPanel + RagChat）
//   Tab 2：🔩 BOM 装配系统（Neo4jStatus + BomIngest + AssemblyChat）
//
// Header 通过 GET /api/health 获取后端状态（文档块数、模型名）。
// ============================================================

import { useEffect, useState } from 'react'
import { getHealth } from './api/client'
import KnowledgePanel from './components/rag/KnowledgePanel'
import EvalPanel from './components/rag/EvalPanel'
import RagChat from './components/rag/RagChat'
import Neo4jStatus from './components/bom/Neo4jStatus'
import BomIngest from './components/bom/BomIngest'
import AssemblyChat from './components/bom/AssemblyChat'

type TabId = 'rag' | 'bom'

function App() {
  const [activeTab, setActiveTab] = useState<TabId>('rag')
  const [healthInfo, setHealthInfo] = useState<{ count: number; model: string } | null>(null)

  // 获取后端健康状态
  useEffect(() => {
    getHealth()
      .then((h) => setHealthInfo({ count: h.collection_count, model: h.model }))
      .catch(() => setHealthInfo(null))
  }, [])

  const tabs: { id: TabId; label: string }[] = [
    { id: 'rag', label: '📖 RAG 知识库问答' },
    { id: 'bom', label: '🔩 BOM 装配系统' },
  ]

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
              RAG + Neo4j BOM · FastAPI + React
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

      {/* ===== Tab 导航 ===== */}
      <div className="max-w-6xl mx-auto px-6 pt-4">
        <div className="flex gap-1 border-b border-slate-200">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-5 py-2.5 text-sm font-medium rounded-t-lg transition-colors ${
                activeTab === tab.id
                  ? 'bg-white border border-b-white border-slate-200 text-blue-600 -mb-px'
                  : 'text-slate-500 hover:text-slate-700 hover:bg-slate-100'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* ===== Tab 内容 ===== */}
      <main className="max-w-6xl mx-auto px-6 py-4">

        {/* Tab 1：RAG 知识库问答 */}
        {activeTab === 'rag' && (
          <div className="space-y-4">
            <Accordion title="📂 知识库管理">
              <KnowledgePanel />
            </Accordion>
            <Accordion title="📊 性能评估">
              <EvalPanel />
            </Accordion>
            <RagChat />
          </div>
        )}

        {/* Tab 2：BOM 装配系统 */}
        {activeTab === 'bom' && (
          <div className="space-y-4">
            <Accordion title="⚙️ Neo4j 图数据库状态" defaultOpen>
              <Neo4jStatus />
            </Accordion>
            <Accordion title="📋 BOM 入库">
              <BomIngest />
            </Accordion>
            <h2 className="text-base font-semibold text-slate-700">💬 装配方案生成</h2>
            <AssemblyChat />
          </div>
        )}
      </main>
    </div>
  )
}

// ============================================================
// Accordion — 可折叠面板（对应 Gradio 的 gr.Accordion）
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
      {open && <div className="p-4 bg-white">{children}</div>}
    </div>
  )
}

export default App
